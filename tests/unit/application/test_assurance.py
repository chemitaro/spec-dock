from __future__ import annotations

from dataclasses import dataclass
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
        return target.issue_dir / ".assurance.json"

    def read_contract(self, target):
        self.read_target = target
        return self.read_result

    def verify_contract(self, target):
        self.verify_target = target
        return self.read_result

    def ensure_contract_writable(self, target):
        self.ensure_contract_writable_target = target


@dataclass(frozen=True)
class _ArtifactFake:
    artifact: str
    path: Path
    repo_relative_path: str
    text: str


class _ArtifactStoreFake:
    def __init__(self, manifest, artifacts) -> None:
        self.manifest = manifest
        self.artifacts = tuple(artifacts)
        self.unwritable: set[str] = set()
        self.missing_templates: set[str] = set()
        self.invalid_marker_templates: set[str] = set()
        self.preflighted: list[str] = []
        self.writes: list[tuple[str, str]] = []

    def artifact_kinds(self, selection):
        if selection == "all":
            return tuple(artifact.artifact for artifact in self.artifacts)
        return (selection,)

    def read_artifact(self, target, artifact):
        del target
        for item in self.artifacts:
            if item.artifact == artifact:
                return item
        raise AssertionError(f"unknown artifact: {artifact}")

    def ensure_artifact_writable(self, artifact):
        self.preflighted.append(artifact.artifact)
        if artifact.artifact in self.unwritable:
            raise RuntimeError(f"unwritable artifact: {artifact.artifact}")

    def write_artifact(self, artifact, text):
        self.writes.append((artifact.artifact, text))

    def load_profile_section_manifest(self):
        return self.manifest

    def load_profile_artifact_template(self, artifact, profile):
        from spec_dock_runtime.domain.artifact_composer import ProfileArtifactTemplate

        if artifact in self.missing_templates:
            raise FileNotFoundError(
                f"Profile template not found: spec-dock/templates/issue-profiles/{profile}/{artifact}.md"
            )
        body = f"# {profile} {artifact} template\n\n{profile.upper()}_{artifact.upper()}_TEMPLATE_BODY\n"
        if artifact in self.invalid_marker_templates:
            body += '<!-- spec-dock:managed-section begin id="template.invalid" -->\n'
        return ProfileArtifactTemplate(
            profile=profile,
            artifact=artifact,
            repo_relative_path=f"spec-dock/templates/issue-profiles/{profile}/{artifact}.md",
            body=body,
        )


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


def _artifact_placeholder(artifact: str) -> str:
    title = "設計" if artifact == "design" else "実装計画"
    noun = "設計書" if artifact == "design" else "実装計画"
    return (
        "---\n"
        "artifact_state: awaiting-assurance-compose\n"
        "---\n"
        f"# iss-00227 — {title} placeholder\n"
        "\n"
        "このファイルはまだ合成されていません。\n"
        "\n"
        "先に `requirement.md` を具体化し、`assurance classify --stage requirement` を実行してください。\n"
        f"その後、`assurance compose --artifact all` を実行して、この Issue の分類に応じた{noun}テンプレートを合成してください。\n"
        "\n"
        f"この状態のまま{title}本文を書き始めないでください。\n"
    )


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
    assert write_result.written_path == store.target.issue_dir / ".assurance.json"
    assert len(store.writes) == 1
    assert store.writes[0] == (store.target, write_result.contract)
    assert dry_run_result.ok
    assert dry_run_result.dry_run
    assert dry_run_result.written_path is None
    assert len(store.writes) == 1
    assert domain_assurance.canonical_json_bytes(dry_run_result.contract) == domain_assurance.canonical_json_bytes(
        write_result.contract
    )


def test_compose_preflights_all_changed_artifacts_before_writing() -> None:
    app_assurance, app_contracts, domain_assurance, AssuranceStoreResult, ResolvedIssueTarget = _runtime_modules()
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.domain.artifact_composer import load_profile_section_manifest
    finally:
        sys.path.pop(0)
    manifest_text = (
        Path(__file__).resolve().parents[3]
        / "src"
        / "spec_dock"
        / "assets"
        / "spec_dock"
        / "templates"
        / "assurance"
        / "profile-sections.json"
    ).read_text(encoding="utf-8")
    manifest = load_profile_section_manifest(manifest_text)
    store = _store_with_target(domain_assurance, ResolvedIssueTarget)
    valid_contract = _contract(domain_assurance)
    store.read_result = AssuranceStoreResult(
        status="valid",
        target=store.target,
        contract=valid_contract,
        mode="adaptive",
        reason="ok",
    )
    artifact_store = _ArtifactStoreFake(
        manifest,
        (
            _ArtifactFake(
                "design",
                store.target.issue_dir / "design.md",
                "design.md",
                _artifact_placeholder("design"),
            ),
            _ArtifactFake(
                "plan",
                store.target.issue_dir / "plan.md",
                "plan.md",
                _artifact_placeholder("plan"),
            ),
        ),
    )
    artifact_store.unwritable.add("plan")

    try:
        app_assurance.compose_assurance(
            app_contracts.ComposeAssuranceRequest(artifact="all", dry_run=False),
            store=store,
            artifact_store=artifact_store,
        )
    except RuntimeError as exc:
        assert "unwritable artifact: plan" in str(exc)
    else:
        raise AssertionError("compose should fail during writable preflight")

    assert artifact_store.preflighted == ["design", "plan"]
    assert artifact_store.writes == []
    assert len(store.writes) == 0


def test_compose_missing_profile_template_fails_before_writes() -> None:
    app_assurance, app_contracts, domain_assurance, AssuranceStoreResult, ResolvedIssueTarget = _runtime_modules()
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.domain.artifact_composer import load_profile_section_manifest
    finally:
        sys.path.pop(0)
    manifest_text = (
        Path(__file__).resolve().parents[3]
        / "src"
        / "spec_dock"
        / "assets"
        / "spec_dock"
        / "templates"
        / "assurance"
        / "profile-sections.json"
    ).read_text(encoding="utf-8")
    manifest = load_profile_section_manifest(manifest_text)
    store = _store_with_target(domain_assurance, ResolvedIssueTarget)
    store.read_result = AssuranceStoreResult(
        status="valid",
        target=store.target,
        contract=_contract(domain_assurance),
        mode="adaptive",
        reason="ok",
    )
    artifact_store = _ArtifactStoreFake(
        manifest,
        (
            _ArtifactFake("design", store.target.issue_dir / "design.md", "design.md", _artifact_placeholder("design")),
            _ArtifactFake("plan", store.target.issue_dir / "plan.md", "plan.md", _artifact_placeholder("plan")),
            _ArtifactFake("report", store.target.issue_dir / "report.md", "report.md", "# Report\n"),
        ),
    )
    artifact_store.missing_templates.add("plan")

    result = app_assurance.compose_assurance(
        app_contracts.ComposeAssuranceRequest(artifact="all", dry_run=False),
        store=store,
        artifact_store=artifact_store,
    )

    assert result.ok is False
    assert result.status == "invalid"
    assert result.reason == "template_validation_failed"
    assert "Profile template not found" in " ".join(result.details)
    assert artifact_store.writes == []
    assert store.writes == []


def test_compose_all_invalid_profile_template_marker_does_not_write_artifacts_or_contract() -> None:
    app_assurance, app_contracts, domain_assurance, AssuranceStoreResult, ResolvedIssueTarget = _runtime_modules()
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.domain.artifact_composer import load_profile_section_manifest
    finally:
        sys.path.pop(0)
    manifest_text = (
        Path(__file__).resolve().parents[3]
        / "src"
        / "spec_dock"
        / "assets"
        / "spec_dock"
        / "templates"
        / "assurance"
        / "profile-sections.json"
    ).read_text(encoding="utf-8")
    manifest = load_profile_section_manifest(manifest_text)
    store = _store_with_target(domain_assurance, ResolvedIssueTarget)
    store.read_result = AssuranceStoreResult(
        status="valid",
        target=store.target,
        contract=_contract(domain_assurance),
        mode="adaptive",
        reason="ok",
    )
    artifact_store = _ArtifactStoreFake(
        manifest,
        (
            _ArtifactFake("design", store.target.issue_dir / "design.md", "design.md", _artifact_placeholder("design")),
            _ArtifactFake("plan", store.target.issue_dir / "plan.md", "plan.md", _artifact_placeholder("plan")),
            _ArtifactFake("report", store.target.issue_dir / "report.md", "report.md", "# Report\n"),
        ),
    )
    artifact_store.invalid_marker_templates.add("plan")

    result = app_assurance.compose_assurance(
        app_contracts.ComposeAssuranceRequest(artifact="all", dry_run=False),
        store=store,
        artifact_store=artifact_store,
    )

    assert result.ok is False
    assert result.status == "invalid"
    assert result.reason == "marker_conflict"
    assert "Managed section template.invalid has no end marker." in result.errors
    assert artifact_store.writes == []
    assert store.writes == []


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
