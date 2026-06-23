from __future__ import annotations

import hashlib
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

from spec_dock_runtime.application.context_packets import (
    SourceRef,
    compile_context_packet_projection,
    compile_step_assurance_projection,
)
from spec_dock_runtime.application.contracts import (
    RunbookProjectionResult,
    WorkflowNextRequest,
    WorkflowResult,
    WorkflowStatusRequest,
)
from spec_dock_runtime.domain.runbook import compile_runbook
from spec_dock_runtime.domain.workflow_state import (
    STRICT_LEGACY_AUTHORITY,
    RunbookAuthority,
    WorkflowState,
    classify_requirement_text,
)
from spec_dock_runtime.infra.context_packet_store import ContextPacketStore
from spec_dock_runtime.infra.context_policy_store import ContextPolicyStore

if TYPE_CHECKING:
    from spec_dock_runtime.domain.runbook import Runbook


class WorkflowAssuranceStoreLike(Protocol):
    def resolve_issue_target(self, target: None) -> Any: ...

    def read_contract(self, target: Any) -> Any: ...

    def verify_contract(self, target: Any) -> Any: ...

    def read_requirement_text(self, target: Any) -> str | None: ...


class RunbookStoreLike(Protocol):
    def write_current(self, runbook: Runbook) -> RunbookProjectionResult: ...


def workflow_status(_request: WorkflowStatusRequest, *, store: WorkflowAssuranceStoreLike) -> WorkflowResult:
    state = _resolve_state(store)
    return WorkflowResult(operation="status", state=state, runbook=None)


def workflow_next(
    request: WorkflowNextRequest,
    *,
    store: WorkflowAssuranceStoreLike,
    runbook_store: RunbookStoreLike,
) -> WorkflowResult:
    state = _resolve_state(store)
    step_assurance: dict[str, Any] | None = None
    context_packets: dict[str, Any] | None = None
    if request.workflow_target == "issue-execution" and state.kind == "ready":
        step_assurance, context_packets = _compile_execution_context(store, state)
    runbook = compile_runbook(
        request.workflow_target,
        state,
        step_assurance=step_assurance,
        context_packets=context_packets,
    )
    projection = runbook_store.write_current(runbook)
    if projection.written:
        return WorkflowResult(operation="next", state=state, runbook=runbook, projection=projection)
    blocked_state = WorkflowState(
        kind="blocked",
        active_issue_id=state.active_issue_id,
        reason_code="runbook-write-failure",
        artifact_readiness=state.artifact_readiness,
        authority=STRICT_LEGACY_AUTHORITY,
        details=(
            *projection.errors,
            "Run ./spec-dock/scripts/spec-dock doctor.",
            "Remove stale spec-dock/.agent/runbooks/*.tmp files if present.",
        ),
    )
    return WorkflowResult(
        operation="next",
        state=blocked_state,
        runbook=compile_runbook(request.workflow_target, blocked_state),
        projection=projection,
    )


def _resolve_state(store: WorkflowAssuranceStoreLike) -> WorkflowState:
    try:
        target = store.resolve_issue_target(None)
    except Exception as exc:
        reason = getattr(exc, "reason", "")
        if reason == "active_issue_missing":
            return WorkflowState(
                kind="no-active",
                active_issue_id=None,
                reason_code="active-issue-missing",
                artifact_readiness="missing",
                authority=STRICT_LEGACY_AUTHORITY,
            )
        return WorkflowState(
            kind="no-active",
            active_issue_id=None,
            reason_code=reason or "active-issue-unavailable",
            artifact_readiness="missing",
            authority=STRICT_LEGACY_AUTHORITY,
            details=(str(exc),),
        )

    try:
        requirement_text = store.read_requirement_text(target)
    except OSError as exc:
        return WorkflowState(
            kind="requirement-capture",
            active_issue_id=target.issue_id,
            reason_code="requirement-unreadable",
            artifact_readiness="missing",
            authority=STRICT_LEGACY_AUTHORITY,
            details=(str(exc),),
        )
    if requirement_text is None:
        return WorkflowState(
            kind="requirement-capture",
            active_issue_id=target.issue_id,
            reason_code="requirement-missing",
            artifact_readiness="missing",
            authority=STRICT_LEGACY_AUTHORITY,
        )
    readiness = classify_requirement_text(requirement_text)
    if readiness != "substantive":
        return WorkflowState(
            kind="requirement-capture",
            active_issue_id=target.issue_id,
            reason_code="requirement-scaffold",
            artifact_readiness=readiness,
            authority=STRICT_LEGACY_AUTHORITY,
        )

    assurance = store.verify_contract(target)
    if assurance.status == "valid" and assurance.contract is not None:
        classification = assurance.contract.classification
        return WorkflowState(
            kind="ready",
            active_issue_id=target.issue_id,
            reason_code="assurance-valid",
            artifact_readiness="substantive",
            authority=RunbookAuthority(
                authorized_profile=classification.authorized_profile.value,
                lite_candidate=classification.lite_candidate,
                obligation_source="authorized_profile",
            ),
        )
    if assurance.status == "invalid":
        return WorkflowState(
            kind="classification-required",
            active_issue_id=target.issue_id,
            reason_code="authority-invalid",
            artifact_readiness="substantive",
            authority=STRICT_LEGACY_AUTHORITY,
            details=tuple(assurance.details),
        )
    return WorkflowState(
        kind="classification-required",
        active_issue_id=target.issue_id,
        reason_code="assurance-missing",
        artifact_readiness="substantive",
        authority=STRICT_LEGACY_AUTHORITY,
    )


def _compile_execution_context(
    store: WorkflowAssuranceStoreLike,
    state: WorkflowState,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    repo_root = getattr(store, "repo_root", None)
    if repo_root is None or state.active_issue_id is None:
        return None, None
    try:
        target = store.resolve_issue_target(None)
    except Exception:
        return None, None
    repo_root_path = Path(repo_root)
    issue_dir = Path(target.issue_dir)
    source_refs = _source_refs(repo_root_path, issue_dir)
    policy_result = ContextPolicyStore(repo_root_path).load()
    step_projection = compile_step_assurance_projection(
        issue_id=state.active_issue_id,
        authorized_profile=state.authority.authorized_profile,
        lite_candidate=state.authority.lite_candidate,
        plan_text=_read_optional_text(issue_dir / "plan.md"),
        report_text=_read_optional_text(issue_dir / "report.md"),
        source_refs=source_refs,
        policy_result=policy_result,
    )
    packet_projection = compile_context_packet_projection(
        step_projection=step_projection,
        packet_store=ContextPacketStore(repo_root_path),
    )
    return step_projection.to_payload(), packet_projection.to_payload()


def _source_refs(repo_root: Path, issue_dir: Path) -> tuple[SourceRef, ...]:
    refs: list[SourceRef] = []
    for filename in ("requirement.md", "design.md", "plan.md", "report.md", "assurance.json"):
        path = issue_dir / filename
        rel_path = _repo_relative(repo_root, path)
        if not path.exists() or not path.is_file():
            refs.append(SourceRef(path=rel_path, sha256=None, missing_reason="missing"))
            continue
        try:
            refs.append(SourceRef(path=rel_path, sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        except OSError:
            refs.append(SourceRef(path=rel_path, sha256=None, missing_reason="unreadable"))
    policy_path = repo_root / "spec-dock/system/assurance/context-routing-policy.json"
    if policy_path.exists() and policy_path.is_file():
        try:
            refs.append(
                SourceRef(
                    path=_repo_relative(repo_root, policy_path),
                    sha256=hashlib.sha256(policy_path.read_bytes()).hexdigest(),
                )
            )
        except OSError:
            refs.append(
                SourceRef(path=_repo_relative(repo_root, policy_path), sha256=None, missing_reason="unreadable")
            )
    else:
        refs.append(
            SourceRef(
                path="spec-dock/system/assurance/context-routing-policy.json",
                sha256=None,
                missing_reason="missing",
            )
        )
    return tuple(refs)


def _read_optional_text(path: Path) -> str | None:
    try:
        if not path.exists() or not path.is_file():
            return None
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()
