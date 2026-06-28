from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.domain import assurance
        from spec_dock_runtime.infra.assurance_store import AssuranceStore, AssuranceStoreError
    finally:
        sys.path.pop(0)
    return assurance, AssuranceStore, AssuranceStoreError


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")


def _make_issue(
    repo_root: Path,
    *,
    issue_id: str = "iss-00227",
    github_issue_number: int | None = 227,
    body: str = "# Requirement\n",
) -> Path:
    issue_dir = (
        repo_root
        / "spec-dock"
        / "initiatives"
        / "init-local-00003-platform"
        / "epics"
        / "epic-00224-assurance"
        / "issues"
        / f"{issue_id}-target"
    )
    issue_dir.mkdir(parents=True)
    (issue_dir / "requirement.md").write_text(body, encoding="utf-8")
    (issue_dir / "design.md").write_text("# Design\n", encoding="utf-8")
    (issue_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (issue_dir / "report.md").write_text("# Report\n", encoding="utf-8")
    meta: dict[str, object] = {
        "schema_version": 1,
        "type": "issue",
        "id": issue_id,
        "title": "Target",
        "slug": "target",
    }
    if github_issue_number is not None:
        meta["github"] = {"issue_number": github_issue_number}
    _write_json(issue_dir / ".meta.json", meta)
    return issue_dir


def _write_active(repo_root: Path, issue_dir: Path, issue_id: str = "iss-00227") -> None:
    rel_issue_dir = issue_dir.relative_to(repo_root).as_posix()
    _write_json(
        repo_root / "spec-dock" / ".agent" / "active.json",
        {
            "schema_version": 2,
            "issue": {"id": issue_id, "path": rel_issue_dir},
            "epic": None,
            "initiative": None,
        },
    )
    active_issue = repo_root / "spec-dock" / "active" / "issue"
    active_issue.parent.mkdir(parents=True, exist_ok=True)
    active_issue.symlink_to(Path("..") / Path(rel_issue_dir).relative_to("spec-dock"), target_is_directory=True)


def test_source_binding_persists_resolved_issue_local_path_and_active_display_path(tmp_path: Path) -> None:
    assurance, AssuranceStore, _ = _runtime_modules()
    issue_dir = _make_issue(tmp_path, body="# Requirement\n\nStable source.\n")
    _write_active(tmp_path, issue_dir)
    store = AssuranceStore(tmp_path)

    target = store.resolve_issue_target(None)
    binding = store.build_requirement_source_binding(target)
    artifacts = {artifact.role: artifact for artifact in binding.artifacts}
    artifact = artifacts["requirement"]

    assert tuple(artifacts) == ("requirement", "design", "plan")
    assert artifact.path == (issue_dir / "requirement.md").relative_to(tmp_path).as_posix()
    assert artifact.display_path == "spec-dock/active/issue/requirement.md"
    assert artifact.role == "requirement"
    assert len(artifact.sha256) == 64
    assert artifact.sha256 == artifact.sha256.lower()
    int(artifact.sha256, 16)
    assert artifacts["design"].display_path == "spec-dock/active/issue/design.md"
    assert artifacts["plan"].display_path == "spec-dock/active/issue/plan.md"

    contract = assurance.build_assurance_contract(
        issue_id=target.issue_id,
        stage=assurance.ClassificationStage.REQUIREMENT,
        source_binding=binding,
    )
    store.write_contract(target, contract)
    result = store.read_contract(target)
    assert result.status == "valid"
    assert result.contract is not None
    assert result.contract.to_dict() == contract.to_dict()

    verified = store.verify_contract(target)
    assert verified.status == "valid"
    assert verified.contract is not None
    assert verified.contract.to_dict() == contract.to_dict()


def test_contract_with_unknown_root_field_is_invalid(tmp_path: Path) -> None:
    assurance, AssuranceStore, _ = _runtime_modules()
    issue_dir = _make_issue(tmp_path, body="# Requirement\n\nStable source.\n")
    _write_active(tmp_path, issue_dir)
    store = AssuranceStore(tmp_path)
    target = store.resolve_issue_target(None)
    binding = store.build_requirement_source_binding(target)
    contract = assurance.build_assurance_contract(
        issue_id=target.issue_id,
        stage=assurance.ClassificationStage.REQUIREMENT,
        source_binding=binding,
    )
    store.write_contract(target, contract)
    payload = json.loads((issue_dir / ".assurance.json").read_text(encoding="utf-8"))
    payload["extra_metadata"] = {"note": "must not be silently dropped"}
    _write_json(issue_dir / ".assurance.json", payload)

    result = store.read_contract(target)

    assert result.status == "invalid"
    assert result.reason == "invalid_schema"
    assert "unknown_root_field:extra_metadata" in result.details


def test_source_binding_rejects_symlinked_planning_artifacts(tmp_path: Path) -> None:
    _, AssuranceStore, AssuranceStoreError = _runtime_modules()
    issue_dir = _make_issue(tmp_path)
    external_requirement = tmp_path / "external-requirement.md"
    external_requirement.write_text("# Requirement\n\noutside\n", encoding="utf-8")
    (issue_dir / "requirement.md").unlink()
    (issue_dir / "requirement.md").symlink_to(external_requirement)
    store = AssuranceStore(tmp_path)
    target = store.resolve_issue_target("iss-00227")

    with pytest.raises(AssuranceStoreError) as exc_info:
        store.build_requirement_source_binding(target)

    assert exc_info.value.reason == "requirement_symlink"


def test_missing_contract_is_strict_legacy_not_invalid(tmp_path: Path) -> None:
    _, AssuranceStore, _ = _runtime_modules()
    issue_dir = _make_issue(tmp_path)
    _write_active(tmp_path, issue_dir)
    store = AssuranceStore(tmp_path)
    target = store.resolve_issue_target("iss-00227")

    result = store.verify_contract(target)

    assert result.status == "missing"
    assert result.mode == "strict-legacy"
    assert result.reason == "missing_assurance_contract"
    assert result.contract is None


def test_legacy_visible_contract_requires_migration(tmp_path: Path) -> None:
    _, AssuranceStore, _ = _runtime_modules()
    issue_dir = _make_issue(tmp_path)
    _write_json(issue_dir / "assurance.json", {"legacy": True})
    store = AssuranceStore(tmp_path)
    target = store.resolve_issue_target("iss-00227")

    result = store.verify_contract(target)

    assert result.status == "invalid"
    assert result.mode == "invalid"
    assert result.reason == "legacy_assurance_contract_path"
    assert result.contract is None
    assert any("legacy_path=" in detail and "assurance.json" in detail for detail in result.details)
    assert any("canonical_path=" in detail and ".assurance.json" in detail for detail in result.details)


def test_legacy_visible_contract_rejects_dual_path_state(tmp_path: Path) -> None:
    assurance, AssuranceStore, AssuranceStoreError = _runtime_modules()
    issue_dir = _make_issue(tmp_path)
    store = AssuranceStore(tmp_path)
    target = store.resolve_issue_target("iss-00227")
    contract = assurance.build_assurance_contract(
        issue_id=target.issue_id,
        stage=assurance.ClassificationStage.REQUIREMENT,
        source_binding=store.build_requirement_source_binding(target),
    )
    _write_json(issue_dir / ".assurance.json", contract.to_dict())
    _write_json(issue_dir / "assurance.json", {"legacy": True})

    result = store.verify_contract(target)

    assert result.status == "invalid"
    assert result.mode == "invalid"
    assert result.reason == "legacy_assurance_contract_path"
    assert result.contract is None

    with pytest.raises(AssuranceStoreError) as excinfo:
        store.write_contract(target, contract)
    assert excinfo.value.reason == "legacy_assurance_contract_path"


def test_read_contract_rejects_symlinked_hidden_assurance_contract(tmp_path: Path) -> None:
    _, AssuranceStore, _ = _runtime_modules()
    issue_dir = _make_issue(tmp_path)
    external = tmp_path / "external-assurance.json"
    external.write_text('{"keep": true}\n', encoding="utf-8")
    (issue_dir / ".assurance.json").symlink_to(external)
    store = AssuranceStore(tmp_path)
    target = store.resolve_issue_target("iss-00227")

    result = store.verify_contract(target)

    assert result.status == "invalid"
    assert result.mode == "invalid"
    assert result.reason == "contract_path_symlink"
    assert result.contract is None


def test_read_contract_rejects_non_file_hidden_assurance_contract(tmp_path: Path) -> None:
    _, AssuranceStore, _ = _runtime_modules()
    issue_dir = _make_issue(tmp_path)
    (issue_dir / ".assurance.json").mkdir()
    store = AssuranceStore(tmp_path)
    target = store.resolve_issue_target("iss-00227")

    result = store.verify_contract(target)

    assert result.status == "invalid"
    assert result.mode == "invalid"
    assert result.reason == "contract_path_not_file"
    assert result.contract is None


def test_write_contract_rejects_symlinked_assurance_contract_without_touching_target(tmp_path: Path) -> None:
    assurance, AssuranceStore, AssuranceStoreError = _runtime_modules()
    issue_dir = _make_issue(tmp_path)
    store = AssuranceStore(tmp_path)
    target = store.resolve_issue_target("iss-00227")
    external = tmp_path / "external-assurance.json"
    external.write_text('{"keep": true}\n', encoding="utf-8")
    (issue_dir / ".assurance.json").symlink_to(external)
    contract = assurance.build_assurance_contract(
        issue_id=target.issue_id,
        stage=assurance.ClassificationStage.REQUIREMENT,
        source_binding=store.build_requirement_source_binding(target),
    )

    with pytest.raises(AssuranceStoreError) as excinfo:
        store.write_contract(target, contract)

    assert excinfo.value.reason == "contract_path_symlink"
    assert external.read_text(encoding="utf-8") == '{"keep": true}\n'


@pytest.mark.parametrize(
    ("role", "filename"), [("requirement", "requirement.md"), ("design", "design.md"), ("plan", "plan.md")]
)
def test_verify_contract_rejects_stale_planning_source_binding(
    tmp_path: Path,
    role: str,
    filename: str,
) -> None:
    assurance, AssuranceStore, _ = _runtime_modules()
    issue_dir = _make_issue(tmp_path)
    store = AssuranceStore(tmp_path)
    target = store.resolve_issue_target("iss-00227")
    contract = assurance.build_assurance_contract(
        issue_id=target.issue_id,
        stage=assurance.ClassificationStage.REQUIREMENT,
        source_binding=store.build_requirement_source_binding(target),
    )
    store.write_contract(target, contract)

    (issue_dir / filename).write_text(f"# Changed {role}\n", encoding="utf-8")

    result = store.verify_contract(target)

    assert result.status == "invalid"
    assert result.reason == "stale_source_binding"
    assert result.contract is not None
    assert result.contract.to_dict() == contract.to_dict()
    assert any(f"role={role}" in detail for detail in result.details)
    assert any("expected_sha256=" in detail and "actual_sha256=" in detail for detail in result.details)


def test_verify_contract_rejects_partial_legacy_source_binding(tmp_path: Path) -> None:
    assurance, AssuranceStore, _ = _runtime_modules()
    issue_dir = _make_issue(tmp_path)
    store = AssuranceStore(tmp_path)
    target = store.resolve_issue_target("iss-00227")
    payload = assurance.build_assurance_contract(
        issue_id=target.issue_id,
        stage=assurance.ClassificationStage.REQUIREMENT,
        source_binding=store.build_requirement_source_binding(target),
    ).to_dict()
    payload["source_binding"]["artifacts"] = [
        artifact for artifact in payload["source_binding"]["artifacts"] if artifact["role"] == "requirement"
    ]
    _write_json(issue_dir / ".assurance.json", payload)

    result = store.verify_contract(target)

    assert result.status == "invalid"
    assert result.reason == "invalid_schema"
    assert "missing_source_binding_role:design" in result.details
    assert "missing_source_binding_role:plan" in result.details


def test_verify_contract_rejects_source_role_bound_to_wrong_artifact(tmp_path: Path) -> None:
    assurance, AssuranceStore, _ = _runtime_modules()
    issue_dir = _make_issue(tmp_path)
    store = AssuranceStore(tmp_path)
    target = store.resolve_issue_target("iss-00227")
    payload = assurance.build_assurance_contract(
        issue_id=target.issue_id,
        stage=assurance.ClassificationStage.REQUIREMENT,
        source_binding=store.build_requirement_source_binding(target),
    ).to_dict()
    requirement_artifact = next(
        artifact for artifact in payload["source_binding"]["artifacts"] if artifact["role"] == "requirement"
    )
    for artifact in payload["source_binding"]["artifacts"]:
        if artifact["role"] == "design":
            artifact["path"] = requirement_artifact["path"]
            artifact["sha256"] = requirement_artifact["sha256"]
    _write_json(issue_dir / ".assurance.json", payload)

    result = store.verify_contract(target)

    assert result.status == "invalid"
    assert result.reason == "invalid_schema"
    assert "source_binding_role_path_mismatch:design" in result.details


def test_verify_contract_rejects_source_role_bound_to_nested_same_named_artifact(tmp_path: Path) -> None:
    assurance, AssuranceStore, _ = _runtime_modules()
    issue_dir = _make_issue(tmp_path)
    nested_dir = issue_dir / "nested"
    nested_dir.mkdir()
    nested_design = nested_dir / "design.md"
    nested_design.write_text("# Nested Design\n", encoding="utf-8")
    store = AssuranceStore(tmp_path)
    target = store.resolve_issue_target("iss-00227")
    payload = assurance.build_assurance_contract(
        issue_id=target.issue_id,
        stage=assurance.ClassificationStage.REQUIREMENT,
        source_binding=store.build_requirement_source_binding(target),
    ).to_dict()
    for artifact in payload["source_binding"]["artifacts"]:
        if artifact["role"] == "design":
            artifact["path"] = nested_design.relative_to(tmp_path).as_posix()
            artifact["sha256"] = "1" * 64
    _write_json(issue_dir / ".assurance.json", payload)

    result = store.verify_contract(target)

    assert result.status == "invalid"
    assert result.reason == "invalid_schema"
    assert "source_binding_path_not_canonical:design" in result.details


def test_invalid_json_and_invalid_schema_have_distinct_machine_reasons(tmp_path: Path) -> None:
    assurance, AssuranceStore, _ = _runtime_modules()
    malformed_dir = _make_issue(tmp_path, issue_id="iss-00227", github_issue_number=227)
    schema_dir = _make_issue(tmp_path, issue_id="iss-00228", github_issue_number=228)
    semantic_dir = _make_issue(tmp_path, issue_id="iss-00229", github_issue_number=229)
    obligations_dir = _make_issue(tmp_path, issue_id="iss-00230", github_issue_number=230)
    malformed_fact_source_dir = _make_issue(tmp_path, issue_id="iss-00231", github_issue_number=231)
    malformed_fact_reason_dir = _make_issue(tmp_path, issue_id="iss-00232", github_issue_number=232)
    store = AssuranceStore(tmp_path)

    (malformed_dir / ".assurance.json").write_text("{not json\n", encoding="utf-8")
    _write_json(schema_dir / ".assurance.json", {"schema_version": 1, "issue_id": "iss-00228"})
    source_binding = store.build_requirement_source_binding(store.resolve_issue_target("iss-00229"))
    semantic_payload = assurance.build_assurance_contract(
        issue_id="iss-00229",
        stage=assurance.ClassificationStage.REQUIREMENT,
        source_binding=source_binding,
    ).to_dict()
    semantic_payload["risk_facts"] = semantic_payload["risk_facts"][:-1]
    _write_json(semantic_dir / ".assurance.json", semantic_payload)
    obligations_payload = assurance.build_assurance_contract(
        issue_id="iss-00230",
        stage=assurance.ClassificationStage.REQUIREMENT,
        source_binding=store.build_requirement_source_binding(store.resolve_issue_target("iss-00230")),
    ).to_dict()
    obligations_payload["obligations"] = {"profile_preset": "lite", "notes": []}
    _write_json(obligations_dir / ".assurance.json", obligations_payload)
    malformed_fact_source_payload = assurance.build_assurance_contract(
        issue_id="iss-00231",
        stage=assurance.ClassificationStage.REQUIREMENT,
        source_binding=store.build_requirement_source_binding(store.resolve_issue_target("iss-00231")),
    ).to_dict()
    malformed_fact_source_payload["risk_facts"][0]["source"] = "design"
    _write_json(malformed_fact_source_dir / ".assurance.json", malformed_fact_source_payload)
    malformed_fact_reason_payload = assurance.build_assurance_contract(
        issue_id="iss-00232",
        stage=assurance.ClassificationStage.REQUIREMENT,
        source_binding=store.build_requirement_source_binding(store.resolve_issue_target("iss-00232")),
    ).to_dict()
    malformed_fact_reason_payload["risk_facts"][0]["reason_code"] = ""
    _write_json(malformed_fact_reason_dir / ".assurance.json", malformed_fact_reason_payload)

    malformed = store.verify_contract(store.resolve_issue_target("#227"))
    schema_invalid = store.verify_contract(store.resolve_issue_target("228"))
    semantic_invalid = store.verify_contract(store.resolve_issue_target("229"))
    obligations_invalid = store.verify_contract(store.resolve_issue_target("230"))
    malformed_fact_source_invalid = store.verify_contract(store.resolve_issue_target("231"))
    malformed_fact_reason_invalid = store.verify_contract(store.resolve_issue_target("232"))

    assert malformed.status == "invalid"
    assert malformed.reason == "invalid_json"
    assert malformed.contract is None
    assert schema_invalid.status == "invalid"
    assert schema_invalid.reason == "invalid_schema"
    assert "missing_policy_version" in schema_invalid.details
    assert semantic_invalid.status == "invalid"
    assert semantic_invalid.reason == "invalid_schema"
    assert "missing supported assurance facts: security_or_privacy_sensitive" in semantic_invalid.details
    assert obligations_invalid.status == "invalid"
    assert obligations_invalid.reason == "invalid_schema"
    assert "obligations_profile_mismatch" in obligations_invalid.details
    assert malformed_fact_source_invalid.status == "invalid"
    assert malformed_fact_source_invalid.reason == "invalid_schema"
    assert "invalid_risk_facts" in malformed_fact_source_invalid.details
    assert malformed_fact_reason_invalid.status == "invalid"
    assert malformed_fact_reason_invalid.reason == "invalid_schema"
    assert "invalid_risk_facts" in malformed_fact_reason_invalid.details


def test_schema_validation_rejects_invalid_issue_id_and_non_issue_local_source_paths(tmp_path: Path) -> None:
    assurance, AssuranceStore, _ = _runtime_modules()
    issue_id_dir = _make_issue(tmp_path, issue_id="iss-00231", github_issue_number=231)
    source_path_dir = _make_issue(tmp_path, issue_id="iss-00232", github_issue_number=232)
    store = AssuranceStore(tmp_path)

    issue_id_payload = assurance.build_assurance_contract(
        issue_id="iss-00231",
        stage=assurance.ClassificationStage.REQUIREMENT,
        source_binding=store.build_requirement_source_binding(store.resolve_issue_target("iss-00231")),
    ).to_dict()
    issue_id_payload["issue_id"] = "not-an-issue"
    _write_json(issue_id_dir / ".assurance.json", issue_id_payload)

    source_path_payload = assurance.build_assurance_contract(
        issue_id="iss-00232",
        stage=assurance.ClassificationStage.REQUIREMENT,
        source_binding=store.build_requirement_source_binding(store.resolve_issue_target("iss-00232")),
    ).to_dict()
    requirement_source = next(
        artifact for artifact in source_path_payload["source_binding"]["artifacts"] if artifact["role"] == "requirement"
    )
    requirement_source["path"] = "not-an-issue/requirement.md"
    _write_json(source_path_dir / ".assurance.json", source_path_payload)

    invalid_issue_id = store.verify_contract(store.resolve_issue_target("231"))
    invalid_source_path = store.verify_contract(store.resolve_issue_target("232"))

    assert invalid_issue_id.status == "invalid"
    assert invalid_issue_id.reason == "invalid_schema"
    assert "invalid_issue_id" in invalid_issue_id.details
    assert invalid_source_path.status == "invalid"
    assert invalid_source_path.reason == "invalid_schema"
    assert "source_binding_path_not_issue_local" in invalid_source_path.details


def test_hidden_contract_rejects_source_binding_from_another_issue(tmp_path: Path) -> None:
    assurance, AssuranceStore, _ = _runtime_modules()
    target_dir = _make_issue(tmp_path, issue_id="iss-00232", github_issue_number=232)
    source_dir = _make_issue(tmp_path, issue_id="iss-00233", github_issue_number=233)
    store = AssuranceStore(tmp_path)
    source_target = store.resolve_issue_target("iss-00233")
    target = store.resolve_issue_target("iss-00232")
    payload = assurance.build_assurance_contract(
        issue_id="iss-00232",
        stage=assurance.ClassificationStage.REQUIREMENT,
        source_binding=store.build_requirement_source_binding(source_target),
    ).to_dict()
    _write_json(target_dir / ".assurance.json", payload)

    result = store.verify_contract(target)

    assert source_dir != target_dir
    assert result.status == "invalid"
    assert result.reason == "invalid_schema"
    assert "source_binding_path_not_issue_local" in result.details


def test_explicit_path_targets_are_contained_issue_paths_and_do_not_fallback_to_active(tmp_path: Path) -> None:
    _, AssuranceStore, AssuranceStoreError = _runtime_modules()
    active_dir = _make_issue(tmp_path, issue_id="iss-00227", github_issue_number=227)
    explicit_dir = _make_issue(tmp_path, issue_id="iss-00228", github_issue_number=228)
    _write_active(tmp_path, active_dir)
    non_issue_dir = tmp_path / "spec-dock" / "notes"
    non_issue_dir.mkdir(parents=True)
    escaped = tmp_path.parent / f"{tmp_path.name}-outside.md"
    escaped.write_text("outside\n", encoding="utf-8")
    escape_link = tmp_path / "spec-dock" / "escape.md"
    escape_link.symlink_to(escaped)
    store = AssuranceStore(tmp_path)

    by_abs_artifact = store.resolve_issue_target(explicit_dir / "requirement.md")
    by_rel_dir = store.resolve_issue_target(explicit_dir.relative_to(tmp_path).as_posix())
    by_id = store.resolve_issue_target("iss-00228")
    by_github = store.resolve_issue_target("228")

    assert by_abs_artifact.issue_id == "iss-00228"
    assert by_rel_dir.issue_id == "iss-00228"
    assert by_id.issue_id == "iss-00228"
    assert by_github.issue_id == "iss-00228"

    for bad_target, reason in (
        (non_issue_dir, "target_not_issue_dir"),
        ("spec-dock/missing/requirement.md", "target_path_missing"),
        (escaped, "target_path_outside_repo"),
        (escape_link, "target_path_outside_repo"),
    ):
        with pytest.raises(AssuranceStoreError) as excinfo:
            store.resolve_issue_target(bad_target)
        assert excinfo.value.reason == reason

    assert store.resolve_issue_target(None).issue_id == "iss-00227"
