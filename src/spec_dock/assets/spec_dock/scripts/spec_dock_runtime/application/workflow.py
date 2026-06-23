from __future__ import annotations

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
