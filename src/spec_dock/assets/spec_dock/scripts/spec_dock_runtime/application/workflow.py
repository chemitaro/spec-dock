from __future__ import annotations

from typing import Any, Protocol

from spec_dock_runtime.application.contracts import WorkflowNextRequest, WorkflowResult, WorkflowStatusRequest
from spec_dock_runtime.domain.runbook import compile_runbook
from spec_dock_runtime.domain.workflow_state import (
    STRICT_LEGACY_AUTHORITY,
    RunbookAuthority,
    WorkflowState,
    classify_requirement_text,
)


class WorkflowAssuranceStoreLike(Protocol):
    def resolve_issue_target(self, target: None) -> Any: ...

    def read_contract(self, target: Any) -> Any: ...

    def read_requirement_text(self, target: Any) -> str | None: ...


def workflow_status(_request: WorkflowStatusRequest, *, store: WorkflowAssuranceStoreLike) -> WorkflowResult:
    state = _resolve_state(store)
    return WorkflowResult(operation="status", state=state, runbook=None)


def workflow_next(request: WorkflowNextRequest, *, store: WorkflowAssuranceStoreLike) -> WorkflowResult:
    state = _resolve_state(store)
    return WorkflowResult(operation="next", state=state, runbook=compile_runbook(request.workflow_target, state))


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

    assurance = store.read_contract(target)
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
