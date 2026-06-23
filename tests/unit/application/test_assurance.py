from __future__ import annotations

from pathlib import Path
import sys


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application import assurance as app_assurance, contracts as app_contracts
        from spec_dock_runtime.domain import assurance as domain_assurance
        from spec_dock_runtime.infra.assurance_store import AssuranceStoreResult, ResolvedIssueTarget
    finally:
        sys.path.pop(0)
    return app_assurance, app_contracts, domain_assurance, AssuranceStoreResult, ResolvedIssueTarget


class _StoreFake:
    def __init__(self, read_result=None) -> None:
        self.target = None
        self.binding = None
        self.read_result = read_result
        self.writes: list[tuple[object, object]] = []

    def resolve_issue_target(self, issue):
        self.resolved_issue_arg = issue
        return self.target

    def build_requirement_source_binding(self, target):
        self.binding_target = target
        return self.binding

    def write_contract(self, target, contract):
        self.writes.append((target, contract))
        return target.issue_dir / "assurance.json"

    def read_contract(self, target):
        self.read_target = target
        return self.read_result

    def verify_contract(self, target):
        self.verify_target = target
        return self.read_result


def _contract(domain_assurance, *, issue_id: str = "iss-00227"):
    binding = domain_assurance.SourceBinding(
        artifacts=(
            domain_assurance.SourceArtifact(
                path=f"spec-dock/initiatives/init/epics/epic/issues/{issue_id}/requirement.md",
                display_path="spec-dock/active/issue/requirement.md",
                role="requirement",
                sha256="0" * 64,
            ),
        ),
    )
    return domain_assurance.build_assurance_contract(
        issue_id=issue_id,
        stage=domain_assurance.ClassificationStage.REQUIREMENT,
        source_binding=binding,
    )


def _store_with_target(domain_assurance, ResolvedIssueTarget, *, issue_id: str = "iss-00227"):
    store = _StoreFake()
    store.target = ResolvedIssueTarget(
        issue_id=issue_id,
        issue_dir=Path("/repo/spec-dock/initiatives/init/epics/epic/issues") / f"{issue_id}-target",
        repo_relative_path=f"spec-dock/initiatives/init/epics/epic/issues/{issue_id}-target",
    )
    store.binding = _contract(domain_assurance, issue_id=issue_id).source_binding
    return store


def test_classify_writes_contract_and_dry_run_returns_same_contract_without_write() -> None:
    app_assurance, app_contracts, domain_assurance, _AssuranceStoreResult, ResolvedIssueTarget = _runtime_modules()
    store = _store_with_target(domain_assurance, ResolvedIssueTarget)

    write_result = app_assurance.classify_assurance(
        app_contracts.ClassifyAssuranceRequest(stage="requirement", dry_run=False),
        store=store,
    )
    dry_run_result = app_assurance.classify_assurance(
        app_contracts.ClassifyAssuranceRequest(stage="requirement", dry_run=True),
        store=store,
    )

    assert write_result.ok
    assert write_result.operation == "classify"
    assert write_result.status == "valid"
    assert write_result.written_path == store.target.issue_dir / "assurance.json"
    assert len(store.writes) == 1
    assert store.writes[0] == (store.target, write_result.contract)
    assert dry_run_result.ok
    assert dry_run_result.dry_run
    assert dry_run_result.written_path is None
    assert len(store.writes) == 1
    assert domain_assurance.canonical_json_bytes(dry_run_result.contract) == domain_assurance.canonical_json_bytes(
        write_result.contract
    )


def test_show_and_verify_map_valid_missing_and_invalid_store_outcomes() -> None:
    app_assurance, app_contracts, domain_assurance, AssuranceStoreResult, ResolvedIssueTarget = _runtime_modules()
    store = _store_with_target(domain_assurance, ResolvedIssueTarget)
    valid_contract = _contract(domain_assurance)

    cases = [
        (
            AssuranceStoreResult(
                status="valid",
                target=store.target,
                contract=valid_contract,
                mode="adaptive",
                reason="ok",
            ),
            True,
            "valid",
            "adaptive",
            "ok",
        ),
        (
            AssuranceStoreResult(
                status="missing",
                target=store.target,
                contract=None,
                mode="strict-legacy",
                reason="missing_assurance_contract",
            ),
            True,
            "missing",
            "strict-legacy",
            "missing_assurance_contract",
        ),
        (
            AssuranceStoreResult(
                status="invalid",
                target=store.target,
                contract=None,
                mode="invalid",
                reason="invalid_json",
                details=("line=1", "column=2"),
            ),
            False,
            "invalid",
            "invalid",
            "invalid_json",
        ),
        (
            AssuranceStoreResult(
                status="invalid",
                target=store.target,
                contract=None,
                mode="invalid",
                reason="invalid_schema",
                details=("missing_policy_version",),
            ),
            False,
            "invalid",
            "invalid",
            "invalid_schema",
        ),
    ]

    for store_result, ok, status, mode, reason in cases:
        store.read_result = store_result
        show = app_assurance.show_assurance(app_contracts.ShowAssuranceRequest(), store=store)
        verify = app_assurance.verify_assurance(app_contracts.VerifyAssuranceRequest(), store=store)

        assert show.operation == "show"
        assert show.ok is ok
        assert show.status == status
        assert show.mode == mode
        assert show.reason == reason
        assert verify.operation == "verify"
        assert verify.ok is ok
        assert verify.status == status
        assert verify.mode == mode
        assert verify.reason == reason
