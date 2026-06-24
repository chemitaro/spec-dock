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
from spec_dock_runtime.domain.context_routing import ContinuationFacts
from spec_dock_runtime.domain.runbook import compile_runbook
from spec_dock_runtime.domain.workflow_state import (
    STRICT_LEGACY_AUTHORITY,
    RunbookAuthority,
    WorkflowState,
    classify_requirement_text,
)

if TYPE_CHECKING:
    from spec_dock_runtime.domain.runbook import Runbook


class WorkflowAssuranceStoreLike(Protocol):
    def resolve_issue_target(self, target: None) -> Any: ...

    def read_contract(self, target: Any) -> Any: ...

    def verify_contract(self, target: Any) -> Any: ...

    def read_requirement_text(self, target: Any) -> str | None: ...


class RunbookStoreLike(Protocol):
    def write_current(self, runbook: Runbook) -> RunbookProjectionResult: ...


class ContextPolicyStoreLike(Protocol):
    def load(self) -> Any: ...


class ContextPacketStoreLike(Protocol):
    def write_current(self, payload: dict[str, Any]) -> Any: ...


class ContinuationProbeLike(Protocol):
    def current_head(self, repo_root: Path) -> str | None: ...

    def status_short(self, repo_root: Path) -> str | None: ...


def workflow_status(_request: WorkflowStatusRequest, *, store: WorkflowAssuranceStoreLike) -> WorkflowResult:
    state = _resolve_state(store)
    return WorkflowResult(operation="status", state=state, runbook=None)


def workflow_next(
    request: WorkflowNextRequest,
    *,
    store: WorkflowAssuranceStoreLike,
    runbook_store: RunbookStoreLike,
    context_policy_store: ContextPolicyStoreLike | None = None,
    context_packet_store: ContextPacketStoreLike | None = None,
    continuation_probe: ContinuationProbeLike | None = None,
) -> WorkflowResult:
    state = _resolve_state(store)
    step_assurance: dict[str, Any] | None = None
    context_packets: dict[str, Any] | None = None
    if request.workflow_target == "issue-execution" and state.kind == "ready":
        step_assurance, context_packets = _compile_execution_context(
            store,
            state,
            context_policy_store=context_policy_store,
            context_packet_store=context_packet_store,
            continuation_probe=continuation_probe,
        )
        if _is_unselectable_step(step_assurance):
            blocked_state = WorkflowState(
                kind="blocked",
                active_issue_id=state.active_issue_id,
                reason_code="workflow-plan-unselectable",
                artifact_readiness=state.artifact_readiness,
                authority=STRICT_LEGACY_AUTHORITY,
                details=(
                    "No structured implementation step could be selected from the active issue plan.",
                    "Add implementation step headings such as `### 実装ステップ S01 ...` before execution.",
                ),
            )
            blocked_runbook = compile_runbook(
                request.workflow_target,
                blocked_state,
                step_assurance=step_assurance,
                context_packets=context_packets,
            )
            return WorkflowResult(
                operation="next",
                state=blocked_state,
                runbook=blocked_runbook,
                projection=runbook_store.write_current(blocked_runbook),
            )
        if context_packets is not None and context_packets.get("written") is False:
            errors = tuple(str(item) for item in context_packets.get("errors", ()) if item)
            blocked_state = WorkflowState(
                kind="blocked",
                active_issue_id=state.active_issue_id,
                reason_code="context-packet-write-failure",
                artifact_readiness=state.artifact_readiness,
                authority=STRICT_LEGACY_AUTHORITY,
                details=(
                    *errors,
                    "Run ./spec-dock/scripts/spec-dock doctor.",
                    "Repair spec-dock/.agent/context-packets before continuing issue execution.",
                ),
            )
            blocked_runbook = compile_runbook(
                request.workflow_target,
                blocked_state,
                step_assurance=step_assurance,
                context_packets=context_packets,
            )
            return WorkflowResult(
                operation="next",
                state=blocked_state,
                runbook=blocked_runbook,
                projection=runbook_store.write_current(blocked_runbook),
            )
    runbook = compile_runbook(
        request.workflow_target,
        state,
        step_assurance=step_assurance,
        context_packets=context_packets,
    )
    projection = runbook_store.write_current(runbook)
    if projection.written:
        return WorkflowResult(
            operation="next",
            state=state,
            runbook=runbook,
            projection=projection,
        )
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
        kind="ready",
        active_issue_id=target.issue_id,
        reason_code="strict-legacy-missing-assurance",
        artifact_readiness="substantive",
        authority=STRICT_LEGACY_AUTHORITY,
    )


def _compile_execution_context(
    store: WorkflowAssuranceStoreLike,
    state: WorkflowState,
    *,
    context_policy_store: ContextPolicyStoreLike | None,
    context_packet_store: ContextPacketStoreLike | None,
    continuation_probe: ContinuationProbeLike | None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    repo_root = getattr(store, "repo_root", None)
    if (
        repo_root is None
        or state.active_issue_id is None
        or context_policy_store is None
        or context_packet_store is None
        or continuation_probe is None
    ):
        return None, None
    try:
        target = store.resolve_issue_target(None)
    except Exception:
        return None, None
    repo_root_path = Path(repo_root)
    issue_dir = Path(target.issue_dir)
    source_refs = _source_refs(repo_root_path, issue_dir)
    policy_result = context_policy_store.load()
    continuation_facts, continuation_state = _continuation_facts(
        repo_root_path,
        state.active_issue_id,
        source_refs,
        continuation_probe=continuation_probe,
    )
    step_projection = compile_step_assurance_projection(
        issue_id=state.active_issue_id,
        authorized_profile=state.authority.authorized_profile,
        lite_candidate=state.authority.lite_candidate,
        plan_text=_read_optional_text(issue_dir / "plan.md"),
        report_text=_read_optional_text(issue_dir / "report.md"),
        source_refs=source_refs,
        policy_result=policy_result,
        continuation_facts=continuation_facts,
        continuation_state=continuation_state,
    )
    if step_projection.selected_step.get("selection_method") == "issue_wide_default":
        return step_projection.to_payload(), None
    packet_projection = compile_context_packet_projection(
        step_projection=step_projection,
        packet_store=context_packet_store,
    )
    return step_projection.to_payload(), packet_projection.to_payload()


def _is_unselectable_step(step_assurance: dict[str, Any] | None) -> bool:
    if not isinstance(step_assurance, dict):
        return False
    selected = step_assurance.get("selected_step")
    return isinstance(selected, dict) and selected.get("selection_method") == "issue_wide_default"


def _continuation_facts(
    repo_root: Path,
    issue_id: str,
    source_refs: tuple[SourceRef, ...],
    *,
    continuation_probe: ContinuationProbeLike,
) -> tuple[ContinuationFacts, dict[str, str]]:
    current_source_binding_hash = _combined_source_hash(source_refs)
    current_source_revision = continuation_probe.current_head(repo_root)
    current_head_revalidated = current_source_revision is not None
    current_source_revision = current_source_revision or ""
    worktree_clean = continuation_probe.status_short(repo_root) == ""
    files_revalidated = all(ref.sha256 is not None for ref in source_refs)
    goal_hash = hashlib.sha256(issue_id.encode("utf-8")).hexdigest()
    allowed_paths_hash = hashlib.sha256("|".join(ref.path for ref in source_refs).encode("utf-8")).hexdigest()
    risk_fingerprint = hashlib.sha256(b"workflow-next:issue-execution").hexdigest()
    previous = _previous_continuation_state(repo_root)
    continuation_state = {
        "source_binding_hash": current_source_binding_hash,
        "source_revision": current_source_revision,
        "goal_hash": goal_hash,
        "scope_hash": goal_hash,
        "allowed_paths_hash": allowed_paths_hash,
        "risk_fingerprint": risk_fingerprint,
    }
    return ContinuationFacts(
        previous_source_binding_hash=previous.get("source_binding_hash", current_source_binding_hash),
        current_source_binding_hash=current_source_binding_hash,
        previous_source_revision=previous.get("source_revision", current_source_revision),
        current_source_revision=current_source_revision,
        previous_goal_hash=previous.get("goal_hash", goal_hash),
        current_goal_hash=goal_hash,
        previous_scope_hash=previous.get("scope_hash", goal_hash),
        current_scope_hash=goal_hash,
        previous_allowed_paths_hash=previous.get("allowed_paths_hash", allowed_paths_hash),
        current_allowed_paths_hash=allowed_paths_hash,
        previous_risk_fingerprint=previous.get("risk_fingerprint", risk_fingerprint),
        current_risk_fingerprint=risk_fingerprint,
        current_head_revalidated=current_head_revalidated,
        worktree_clean=worktree_clean,
        files_revalidated=files_revalidated,
    ), continuation_state


def _previous_continuation_state(repo_root: Path) -> dict[str, str]:
    path = repo_root / "spec-dock/.agent/context-packets/current-context-packets.json"
    try:
        import json

        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    state = payload.get("continuation_state")
    if not isinstance(state, dict):
        return {}
    return {key: value for key, value in state.items() if isinstance(key, str) and isinstance(value, str)}


def _combined_source_hash(refs: tuple[SourceRef, ...]) -> str:
    material = "|".join(f"{ref.path}:{ref.sha256 or ref.missing_reason or ''}" for ref in refs)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


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
