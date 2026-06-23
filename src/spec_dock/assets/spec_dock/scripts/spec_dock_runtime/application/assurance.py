from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from spec_dock_runtime.application.contracts import (
    AssuranceOperation,
    AssuranceResult,
    AssuranceTargetView,
    ClassifyAssuranceRequest,
    ShowAssuranceRequest,
    VerifyAssuranceRequest,
)
from spec_dock_runtime.domain.assurance import (
    AssuranceContract,
    ClassificationStage,
    SourceBinding,
    build_assurance_contract,
)

if TYPE_CHECKING:
    from pathlib import Path


class AssuranceStoreLike(Protocol):
    def resolve_issue_target(self, target: str | Path | None) -> Any: ...

    def build_requirement_source_binding(self, target: Any) -> SourceBinding: ...

    def write_contract(self, target: Any, contract: AssuranceContract) -> Path: ...

    def read_contract(self, target: Any) -> Any: ...

    def verify_contract(self, target: Any) -> Any: ...


def show_assurance(request: ShowAssuranceRequest, *, store: AssuranceStoreLike) -> AssuranceResult:
    target = store.resolve_issue_target(request.issue)
    return _result_from_store_result(operation="show", store_result=store.read_contract(target))


def classify_assurance(request: ClassifyAssuranceRequest, *, store: AssuranceStoreLike) -> AssuranceResult:
    target = store.resolve_issue_target(request.issue)
    source_binding = store.build_requirement_source_binding(target)
    contract = build_assurance_contract(
        issue_id=target.issue_id,
        stage=ClassificationStage(request.stage),
        source_binding=source_binding,
    )
    written_path = None
    if not request.dry_run:
        written_path = store.write_contract(target, contract)
    return AssuranceResult(
        operation="classify",
        ok=True,
        status="valid",
        target=_target_view(target),
        mode=contract.mode.value,
        reason="ok",
        details=(),
        contract=contract,
        dry_run=request.dry_run,
        written_path=written_path,
    )


def verify_assurance(request: VerifyAssuranceRequest, *, store: AssuranceStoreLike) -> AssuranceResult:
    target = store.resolve_issue_target(request.issue)
    return _result_from_store_result(operation="verify", store_result=store.verify_contract(target))


def _result_from_store_result(*, operation: AssuranceOperation, store_result: Any) -> AssuranceResult:
    return AssuranceResult(
        operation=operation,
        ok=store_result.status in ("valid", "missing"),
        status=store_result.status,
        target=_target_view(store_result.target),
        mode=store_result.mode,
        reason=store_result.reason,
        details=store_result.details,
        contract=store_result.contract,
    )


def _target_view(target: Any) -> AssuranceTargetView:
    return AssuranceTargetView(issue_id=target.issue_id, repo_relative_path=target.repo_relative_path)
