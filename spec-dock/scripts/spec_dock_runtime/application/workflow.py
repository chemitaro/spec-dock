from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

from spec_dock_runtime.application.contracts import (
    RunbookProjectionResult,
    WorkflowNextRequest,
    WorkflowResult,
    WorkflowStatusRequest,
)
from spec_dock_runtime.domain.runbook import compile_runbook
from spec_dock_runtime.domain.workflow_state import (
    STRICT_LEGACY_AUTHORITY,
    UNAVAILABLE_AUTHORITY,
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
    runbook = compile_runbook(request.workflow_target, state)
    return _workflow_result_with_projection(state, runbook, runbook_store)


def _workflow_result_with_projection(
    state: WorkflowState,
    runbook: Runbook,
    runbook_store: RunbookStoreLike,
) -> WorkflowResult:
    return WorkflowResult(
        operation="next",
        state=state,
        runbook=runbook,
        projection=runbook_store.write_current(runbook),
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
    assurance = store.verify_contract(target)
    authority = STRICT_LEGACY_AUTHORITY
    if assurance.status == "valid" and assurance.contract is not None:
        classification = assurance.contract.classification
        authority = RunbookAuthority(
            authorized_profile=classification.authorized_profile.value,
            lite_candidate=classification.lite_candidate,
            obligation_source="authorized_profile",
        )

    readiness = classify_requirement_text(requirement_text)
    if readiness != "substantive":
        return WorkflowState(
            kind="requirement-capture",
            active_issue_id=target.issue_id,
            reason_code="requirement-scaffold",
            artifact_readiness=readiness,
            authority=authority,
        )

    if assurance.status == "valid" and assurance.contract is not None:
        plan_readiness = _classify_plan_text(_read_optional_text(Path(target.issue_dir) / "plan.md"))
        if plan_readiness != "executable":
            return WorkflowState(
                kind="blocked",
                active_issue_id=target.issue_id,
                reason_code="plan-missing" if plan_readiness == "missing" else "plan-not-executable",
                artifact_readiness="substantive",
                authority=authority,
                details=(
                    "plan.md must be an executable workflow contract before issue execution.",
                    "Add implementation steps, verification obligations, reviewer/no-review rationale, and report evidence destinations.",
                ),
            )
        return WorkflowState(
            kind="ready",
            active_issue_id=target.issue_id,
            reason_code="assurance-valid",
            artifact_readiness="substantive",
            authority=authority,
        )
    if assurance.status == "invalid":
        return WorkflowState(
            kind="classification-required",
            active_issue_id=target.issue_id,
            reason_code="authority-invalid",
            artifact_readiness="substantive",
            authority=UNAVAILABLE_AUTHORITY,
            details=tuple(assurance.details),
        )
    return WorkflowState(
        kind="ready",
        active_issue_id=target.issue_id,
        reason_code="strict-legacy-missing-assurance",
        artifact_readiness="substantive",
        authority=STRICT_LEGACY_AUTHORITY,
    )


def _read_optional_text(path: Path) -> str | None:
    try:
        if not path.exists() or not path.is_file():
            return None
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _classify_plan_text(plan_text: str | None) -> str:
    if plan_text is None:
        return "missing"
    stripped = plan_text.strip()
    if not stripped:
        return "scaffold"
    lower = stripped.lower()
    scaffold_markers = (
        '状態: "draft',
        "状態: draft",
        "draft | proposed",
        "no structured implementation steps",
        "record red, green, and refactor evidence",
        "link each closure id to its observed verification result",
        "todo",
        "tbd",
        "template",
        "placeholder",
        "未記入",
        "記載してください",
    )
    if any(marker in lower for marker in scaffold_markers):
        return "scaffold"
    markers = (
        "実装ステップ",
        "implementation step",
        "planned contract",
        "具体テストケース",
        "step closure contract",
        "approved-no-op",
        "decision-only closure",
    )
    if any(marker in lower for marker in markers):
        return "executable"
    return "scaffold"
