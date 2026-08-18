from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
from typing import TYPE_CHECKING

import pytest

import spec_dock.managed_distribution as managed_distribution
from spec_dock.managed_distribution import (
    DistributionAction,
    DistributionAdmissionError,
    DistributionApplyError,
    DistributionAsset,
    DistributionIdentity,
    DistributionManifestError,
    DistributionPlan,
    DistributionPlanError,
    DistributionResult,
    DistributionRetryMarker,
    DistributionRootIdentity,
    DistributionStageOwnership,
    DistributionTargetSnapshot,
    OperationJournalStore,
    PathIdentitySnapshot,
    admit_distribution_operation,
    apply_distribution_plan,
    build_distribution_plan,
    build_executable_mutation_plan,
    build_workspace_assessment,
    execute_recognized_distribution,
)

if TYPE_CHECKING:
    from collections.abc import Callable

REPO_ROOT = Path(__file__).resolve().parents[3]
INSTALL_ROOT = REPO_ROOT / "src" / "spec_dock" / "assets" / "install_root"
MANIFEST_PATH = REPO_ROOT / "src" / "spec_dock" / "assets" / "managed_distribution.json"
HISTORICAL_COMMIT = "948d0cf0dedb84ca34e51a4adc0995820aa011f6"

EXPECTED_CURRENT_PATHS = frozenset({
    ".agents/skills/spec-dock/SKILL.md",
    ".agents/skills/spec-dock-grill-with-docs/SKILL.md",
    ".agents/skills/spec-dock-grill-with-docs/agents/openai.yaml",
    ".agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py",
    ".github/workflows/ci.yml",
})
EXPECTED_OBSOLETE_SKILL_PATHS = frozenset(
    f".agents/skills/{name}/SKILL.md"
    for name in (
        "spec-dock-hub",
        "spec-dock-initiative-planning",
        "spec-dock-epic-planning",
        "spec-dock-epic-execution",
        "spec-dock-issue-planning",
        "spec-dock-issue-execution",
        "spec-dock-chatgpt-authoring",
        "spec-dock-initiative-planning-manual",
        "spec-dock-epic-planning-manual",
        "spec-dock-issue-planning-manual",
        "spec-dock-clarification",
        "spec-dock-adr-facilitation",
        "spec-dock-codex-adapter",
        "spec-dock-copilot-adapter",
        "git-commit-conventional-ja",
        "github-pr-observation",
        "github-pr-creator",
        "github-pr-merge-preparer",
        "spec-driven-tdd-workflow",
        "spec-dock-system-architect",
        "spec-dock-implementation-planner",
    )
)
EXPECTED_UNPROVEN_LEGACY_ENTRYPOINT_PATHS = frozenset(
    f"spec-dock/current-{scope}{suffix}" for scope in ("initiative", "epic", "issue") for suffix in ("", ".path")
)
MANIFEST_FIELDS = {
    "schema_version",
    "recognized_workspace_versions",
    "historical_current_identities",
    "trusted_consumer_manifests",
    "obsolete_exact_files",
    "historical_shortcuts",
}
EXPECTED_HISTORICAL_CURRENT_IDENTITY = {
    "path": ".agents/skills/spec-dock-grill-with-docs/SKILL.md",
    "kind": "regular",
    "sha256": "7182c1156bcf3635ffd3113cdcfb1d507c819b6aba6982673c0b10166f5da40c",
    "mode": 0o644,
    "source": {"kind": "git-provider-source", "ref": HISTORICAL_COMMIT},
}


def _manifest_with(**overrides: object) -> dict[str, object]:
    manifest: dict[str, object] = {
        "schema_version": 1,
        "recognized_workspace_versions": [],
        "historical_current_identities": [],
        "trusted_consumer_manifests": [],
        "obsolete_exact_files": [],
        "historical_shortcuts": [],
    }
    manifest.update(overrides)
    return manifest


def _write_manifest(tmp_path: Path, manifest: dict[str, object]) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / "managed_distribution.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


def _regular_record(
    path: str,
    content: bytes,
    *,
    source_kind: str = "test-fixture",
    mode: int | None = None,
) -> dict[str, object]:
    record: dict[str, object] = {
        "path": path,
        "kind": "regular",
        "sha256": hashlib.sha256(content).hexdigest(),
        "source": {"kind": source_kind, "ref": "issue-360-test"},
    }
    if mode is not None:
        record["mode"] = mode
    return record


def _minimal_install_root(tmp_path: Path, content: bytes = b"current\n") -> Path:
    install_root = tmp_path / "install-root"
    source = install_root / ".github" / "workflows" / "ci.yml"
    source.parent.mkdir(parents=True)
    source.write_bytes(content)
    return install_root


def _minimal_scaffold_root(tmp_path: Path) -> Path:
    scaffold_root = tmp_path / "scaffold"
    for root in ("docs", "templates", "scripts", "system"):
        (scaffold_root / root).mkdir(parents=True)
    (scaffold_root / ".gitignore").write_text(".agent/\n", encoding="utf-8")
    runtime = scaffold_root / "scripts" / "spec-dock"
    runtime.write_text("#!/bin/sh\n", encoding="utf-8")
    runtime.chmod(0o755)
    seed = scaffold_root / "templates" / "root" / ".workbench" / "README.md"
    seed.parent.mkdir(parents=True)
    seed.write_text("workbench\n", encoding="utf-8")
    return scaffold_root


def test_s20_public_catalog_is_derived_from_physical_install_root() -> None:
    plan = build_distribution_plan(INSTALL_ROOT, manifest_path=MANIFEST_PATH)

    assert {asset.path for asset in plan.current_assets} == EXPECTED_CURRENT_PATHS
    assert plan.actions == ()
    assert plan.manifest.schema_version == 1
    assert plan.manifest.historical_current_identities == (EXPECTED_HISTORICAL_CURRENT_IDENTITY,)
    obsolete_paths = {item["path"] for item in plan.manifest.obsolete_exact_files}
    assert len(obsolete_paths) == 81
    assert obsolete_paths >= EXPECTED_OBSOLETE_SKILL_PATHS
    assert obsolete_paths >= EXPECTED_UNPROVEN_LEGACY_ENTRYPOINT_PATHS
    assert ".agents/host-adapters/meta.json" in obsolete_paths
    assert any(path.startswith(".codex/") for path in obsolete_paths)
    assert any(path.startswith(".github/agents/") for path in obsolete_paths)
    for asset in plan.current_assets:
        source = INSTALL_ROOT / asset.path
        assert asset.identity.kind == "regular"
        assert asset.identity.sha256 == hashlib.sha256(source.read_bytes()).hexdigest()
        assert asset.identity.mode == stat.S_IMODE(source.stat().st_mode)


def test_s20_current_catalog_bytes_are_not_duplicated_in_historical_manifest() -> None:
    raw = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert set(raw) == MANIFEST_FIELDS
    assert not any(key in raw for key in {"current", "current_assets", "current_catalog"})
    assert raw["historical_current_identities"] == [EXPECTED_HISTORICAL_CURRENT_IDENTITY]
    current_identities = {
        path.relative_to(INSTALL_ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in INSTALL_ROOT.rglob("*")
        if path.is_file()
    }
    assert all(
        identity["sha256"] != current_identities[identity["path"]] for identity in raw["historical_current_identities"]
    )
    obsolete_paths = {item["path"] for item in raw["obsolete_exact_files"]}
    assert len(obsolete_paths) == 81
    assert obsolete_paths >= EXPECTED_OBSOLETE_SKILL_PATHS
    assert obsolete_paths >= EXPECTED_UNPROVEN_LEGACY_ENTRYPOINT_PATHS
    assert not any(item["path"] in EXPECTED_CURRENT_PATHS for item in raw["obsolete_exact_files"])
    unproven_entrypoints = {
        item["path"]: item
        for item in raw["obsolete_exact_files"]
        if item["path"] in EXPECTED_UNPROVEN_LEGACY_ENTRYPOINT_PATHS
    }
    assert set(unproven_entrypoints) == EXPECTED_UNPROVEN_LEGACY_ENTRYPOINT_PATHS
    assert all(item["identities"] == [] for item in unproven_entrypoints.values())
    assert all(item["on_unknown"] == "preserve-and-block" for item in unproven_entrypoints.values())


def test_s55_historical_catalog_is_bound_to_reproducible_git_source() -> None:
    raw = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    records = list(raw["historical_current_identities"])
    records.extend(identity for item in raw["obsolete_exact_files"] for identity in item["identities"])

    assert records
    assert {identity["source"]["ref"] for identity in records} == {HISTORICAL_COMMIT}
    source_available = subprocess.run(
        ["git", "cat-file", "-e", f"{HISTORICAL_COMMIT}^{{commit}}"],
        check=False,
        capture_output=True,
    )
    assert source_available.returncode == 0, "historical source commit is unavailable in this checkout"
    for identity in records:
        path = identity["path"]
        provider_path = f"src/spec_dock/assets/install_root/{path}"
        content = subprocess.check_output(["git", "show", f"{HISTORICAL_COMMIT}:{provider_path}"])
        tree = subprocess.check_output(
            ["git", "ls-tree", HISTORICAL_COMMIT, "--", provider_path],
            text=True,
        )
        mode = tree.split(maxsplit=1)[0]
        assert mode in {"100644", "100755"}
        assert identity["sha256"] == hashlib.sha256(content).hexdigest()
        assert identity["mode"] == int(mode, 8) & 0o777


def test_s20_build_is_read_only(tmp_path: Path) -> None:
    install_root = tmp_path / "install_root"
    source = install_root / ".github" / "workflows" / "ci.yml"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"ci\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    before = {
        path.relative_to(tmp_path): (path.read_bytes() if path.is_file() else None)
        for path in tmp_path.rglob("*")
        if path.is_file()
    }

    build_distribution_plan(install_root, manifest_path=manifest_path)

    after = {
        path.relative_to(tmp_path): (path.read_bytes() if path.is_file() else None)
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    assert after == before


def test_i368_workspace_assessment_is_read_only_and_binds_contract(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    before = {path.relative_to(tmp_path): path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}

    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        intent="update",
    )

    after = {path.relative_to(tmp_path): path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}
    assert after == before
    assert assessment.intent == "update"
    assert assessment.blockers == ()
    assert len(assessment.contract_identity) == 64
    assert {action.action for action in assessment.actions} == {"create"}


def test_i368_blocked_assessment_cannot_issue_executable_authority(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    collision = target_root / ".github" / "workflows" / "ci.yml"
    collision.parent.mkdir(parents=True)
    collision.write_bytes(b"user-owned\n")

    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        intent="init-force",
    )

    assert assessment.blockers
    with pytest.raises(DistributionPlanError, match="blocker"):
        build_executable_mutation_plan(assessment)


def test_i368_executable_plan_digest_is_stable_for_equivalent_assessment(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()

    first = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="update",
        )
    )
    second = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="update",
        )
    )

    assert first.plan_digest == second.plan_digest
    assert len(first.plan_digest) == 64
    assert first.root_identity == second.root_identity


def test_i368_generated_asset_path_must_be_canonical_and_repository_relative(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    content = b"outside\n"
    generated = DistributionAsset(
        path="../outside.txt",
        identity=DistributionIdentity(
            kind="regular",
            sha256=hashlib.sha256(content).hexdigest(),
            mode=0o644,
        ),
        generated_content=content,
    )

    with pytest.raises(DistributionPlanError, match="repository-relative"):
        build_distribution_plan(
            install_root,
            manifest_path=manifest_path,
            generated_assets=(generated,),
        )


def test_i368_journal_prepare_records_bound_actions_before_target_mutation(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    executable = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="update",
        )
    )

    journal = OperationJournalStore(target_root).prepare(executable, package_version="1.2.3")

    assert journal.status == "prepared"
    assert journal.plan_digest == executable.plan_digest
    assert journal.actions
    assert {action.checkpoint for action in journal.actions} == {"pending"}
    assert not (target_root / ".github" / "workflows" / "ci.yml").exists()


def test_i368_journal_resume_rejects_intent_mismatch_without_rewrite(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    update = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="update",
        )
    )
    init_force = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="init-force",
        )
    )
    store = OperationJournalStore(target_root)
    store.prepare(update, package_version="1.2.3")
    before = store.path.read_bytes()

    with pytest.raises(DistributionApplyError, match="journal-intent-mismatch"):
        store.resume(init_force, package_version="1.2.3")

    assert store.path.read_bytes() == before


def test_i368_journal_resume_rejects_cross_root_replay_without_rewrite(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    (first_root / "spec-dock").mkdir(parents=True)
    (second_root / "spec-dock").mkdir(parents=True)
    first = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=first_root,
            intent="update",
        )
    )
    first_store = OperationJournalStore(first_root)
    first_store.prepare(first, package_version="1.2.3")
    replay = second_root / "spec-dock" / ".distribution-journal.json"
    replay.write_bytes(first_store.path.read_bytes())
    second = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=second_root,
            intent="update",
        )
    )
    before = replay.read_bytes()

    with pytest.raises(DistributionApplyError, match="journal-root-mismatch"):
        OperationJournalStore(second_root).resume(second, package_version="1.2.3")

    assert replay.read_bytes() == before


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("authority", "different-authority", "journal-authority-mismatch"),
        ("protocol_version", 999, "journal-protocol-incompatible"),
        ("plan_digest", "0" * 64, "journal-plan-mismatch"),
    ],
)
def test_i368_journal_resume_rejects_binding_mismatch_without_rewrite(
    tmp_path: Path,
    field: str,
    value: object,
    reason: str,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    executable = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="update",
        )
    )
    store = OperationJournalStore(target_root)
    store.prepare(executable, package_version="1.2.3")
    payload = json.loads(store.path.read_text(encoding="utf-8"))
    payload[field] = value
    store.path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    before = store.path.read_bytes()

    with pytest.raises(DistributionApplyError, match=reason):
        store.resume(executable, package_version="1.2.3")

    assert store.path.read_bytes() == before


def test_i368_journal_resume_rejects_recomputed_digest_for_changed_action(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        generated_assets=(
            managed_distribution._generated_regular_asset(
                "spec-dock/spec-dock.version",
                b"1.2.3\n",
                mode=0o644,
            ),
        ),
    )
    store = OperationJournalStore(target_root)
    journal = store.prepare(build_executable_mutation_plan(assessment), package_version="1.2.3")
    changed = list(journal.actions)
    changed[0] = managed_distribution.replace(changed[0], action="prune")
    tampered = managed_distribution.replace(journal, actions=tuple(changed))
    tampered = managed_distribution.replace(
        tampered,
        plan_digest=managed_distribution._journal_digest(tampered),
    )
    store.write(tampered)

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert result.status == "recovery_required"
    assert result.reason == "journal-plan-mismatch"


def test_i368_journal_resume_rejects_existing_parent_rebind(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    parent = target_root / ".github" / "workflows"
    parent.mkdir(parents=True)
    (target_root / "spec-dock").mkdir()
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        generated_assets=(
            managed_distribution._generated_regular_asset(
                "spec-dock/spec-dock.version",
                b"1.2.3\n",
                mode=0o644,
            ),
        ),
    )
    OperationJournalStore(target_root).prepare(
        build_executable_mutation_plan(assessment),
        package_version="1.2.3",
    )
    parent.rename(target_root / ".github" / "workflows-old")
    parent.mkdir()
    sentinel = parent / "sentinel.txt"
    sentinel.write_text("replacement\n", encoding="utf-8")

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert result.status == "recovery_required"
    assert result.reason == "journal-precondition-mismatch"
    assert sentinel.read_text(encoding="utf-8") == "replacement\n"
    assert not (parent / "ci.yml").exists()


def test_i368_recognized_service_executes_and_finalizes_journal(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert result.status == "completed", result.reason
    assert (target_root / ".github" / "workflows" / "ci.yml").read_bytes() == b"desired\n"
    assert (target_root / "spec-dock" / ".gitignore").read_text(encoding="utf-8") == ".agent/\n"
    assert (target_root / "spec-dock" / "spec-dock.version").read_text(encoding="utf-8") == "1.2.3\n"
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i368_recognized_noop_does_not_prepare_a_journal(tmp_path: Path, monkeypatch) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )
    assert first.status == "completed", first.reason
    prepared = False
    original_prepare = OperationJournalStore.prepare

    def record_prepare(*args, **kwargs):
        nonlocal prepared
        prepared = True
        return original_prepare(*args, **kwargs)

    monkeypatch.setattr(OperationJournalStore, "prepare", record_prepare)

    second = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert second.status == "completed", second.reason
    assert not prepared
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i368_recognized_service_upgrades_a_recognized_workspace_version(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            recognized_workspace_versions=[
                {"version": "1.1.0", "anchors": [_regular_record("legacy-anchor", b"legacy\n")]}
            ]
        ),
    )
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    specdock_dir = target_root / "spec-dock"
    specdock_dir.mkdir(parents=True)
    (specdock_dir / "spec-dock.version").write_text("1.1.0\n", encoding="utf-8")

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert result.status == "completed", result.reason
    assert (specdock_dir / "spec-dock.version").read_text(encoding="utf-8") == "1.2.3\n"


def test_i368_generated_state_asset_failure_retains_journal_and_resumes(
    tmp_path: Path,
    monkeypatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)

    content = b"generated context\n"
    generated_asset = DistributionAsset(
        path="spec-dock/active/context-pack.md",
        identity=DistributionIdentity(
            kind="regular",
            sha256=hashlib.sha256(content).hexdigest(),
            mode=0o644,
        ),
        generated_content=content,
    )
    original_apply = managed_distribution._apply_distribution_action

    def fail_generated_action(*args, **kwargs):
        action = kwargs["action"]
        if action.path == generated_asset.path:
            raise DistributionApplyError("injected generated-state failure")
        return original_apply(*args, **kwargs)

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", fail_generated_action)

    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
        generated_assets=(generated_asset,),
    )
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    assert first.status == "recovery_required"
    assert journal_path.is_file()
    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    assert generated_asset.path in {action["path"] for action in journal["actions"]}

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", original_apply)

    second = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
        generated_assets=(generated_asset,),
    )

    assert second.status == "completed", second.reason
    assert not journal_path.exists()
    assert (target_root / generated_asset.path).read_bytes() == content


@pytest.mark.parametrize(
    ("phase", "expected_status"),
    [("preflight-complete", "completed"), ("managed-scaffold-refreshed", "recovery_required")],
)
def test_i368_legacy_marker_conversion_is_limited_to_prewrite_state(
    tmp_path: Path,
    phase: str,
    expected_status: str,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    root_info = target_root.stat()
    marker = DistributionRetryMarker(
        operation="update",
        package_version="1.2.3",
        target_root=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
        last_completed_phase=phase,
        purpose="distribution-rerun",
    )
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    marker_path.write_text(
        json.dumps({
            "schema_version": 1,
            "operation": marker.operation,
            "package_version": marker.package_version,
            "target_root": {"device": root_info.st_dev, "inode": root_info.st_ino},
            "last_completed_phase": marker.last_completed_phase,
            "purpose": marker.purpose,
            "stage_ownership": [],
        }),
        encoding="utf-8",
    )
    before = marker_path.read_bytes()

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
        legacy_marker=marker,
    )

    assert result.status == expected_status
    if expected_status == "completed":
        assert not marker_path.exists()
    else:
        assert marker_path.read_bytes() == before
        assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i368_same_plan_partial_failure_resumes_from_journal_checkpoint(tmp_path: Path, monkeypatch) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    second_source = install_root / ".agents" / "skills" / "example" / "SKILL.md"
    second_source.parent.mkdir(parents=True)
    second_source.write_bytes(b"second\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    original_apply = managed_distribution._apply_distribution_action
    calls = 0

    def fail_second_action(
        plan: DistributionPlan,
        action_target_root: Path,
        action: DistributionAction,
        snapshot: DistributionTargetSnapshot,
        created_parent_bindings: dict[str, PathIdentitySnapshot],
        stage_ownership_recorder: Callable[[DistributionStageOwnership], None] | None = None,
    ) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise DistributionApplyError("injected partial failure")
        original_apply(
            plan,
            action_target_root,
            action,
            snapshot,
            created_parent_bindings,
            stage_ownership_recorder,
        )

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", fail_second_action)
    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )
    assert first.status == "recovery_required"
    assert (target_root / "spec-dock" / ".distribution-journal.json").is_file()

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", original_apply)
    second = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert second.status == "completed", second.reason
    assert second_source.relative_to(install_root).as_posix() in {
        path.relative_to(target_root).as_posix() for path in target_root.rglob("*") if path.is_file()
    }
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i368_checkpoint_write_failure_recovers_from_exact_postcondition(tmp_path: Path, monkeypatch) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    original_checkpoint = OperationJournalStore.checkpoint_published
    failed = False

    def fail_first_checkpoint(
        self: OperationJournalStore,
        journal: managed_distribution.OperationJournal,
        completed_paths: tuple[str, ...],
    ) -> managed_distribution.OperationJournal:
        nonlocal failed
        if not failed and completed_paths:
            failed = True
            raise DistributionApplyError("injected checkpoint failure")
        return original_checkpoint(self, journal, completed_paths)

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", fail_first_checkpoint)
    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    assert first.status == "recovery_required"
    assert journal_path.is_file()

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", original_checkpoint)
    second = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert second.status == "completed", second.reason
    assert not journal_path.exists()


@pytest.mark.parametrize(
    "record",
    [
        {"path": "/.agents/old", "kind": "regular", "sha256": "a" * 64},
        {"path": "../.agents/old", "kind": "regular", "sha256": "a" * 64},
        {"path": r".agents\\old", "kind": "regular", "sha256": "a" * 64},
        {"path": ".agents/*", "kind": "regular", "sha256": "a" * 64},
        {"path": ".agents/old/", "kind": "regular", "sha256": "a" * 64},
        {"path": ".agents/old", "kind": "directory", "sha256": "a" * 64},
        {"path": ".agents/old", "kind": "regular", "sha256": "A" * 64},
        {"path": ".agents/old", "kind": "regular", "sha256": "not-a-digest"},
        {"path": ".agents/old", "kind": "regular", "sha256": "a" * 63},
        {"path": ".agents/old", "kind": "regular", "sha256": "a" * 64, "mode": "0644"},
        {"path": ".agents/old", "kind": "regular", "sha256": "a" * 64, "mode": -1},
        {"path": ".agents/old", "kind": "regular", "sha256": "a" * 64, "mode": 0o100644},
    ],
)
def test_s20_invalid_historical_record_is_rejected(tmp_path: Path, record: dict[str, object]) -> None:
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[record]),
    )

    with pytest.raises(DistributionManifestError):
        build_distribution_plan(INSTALL_ROOT, manifest_path=manifest_path)


def test_s20_duplicate_and_current_obsolete_overlap_are_rejected(tmp_path: Path) -> None:
    duplicate = {
        "path": ".agents/legacy.md",
        "surface": "legacy-test",
        "identities": [_regular_record(".agents/legacy.md", b"legacy\n")],
        "on_unknown": "preserve-and-block",
    }
    duplicate_manifest = _write_manifest(
        tmp_path / "duplicate",
        _manifest_with(obsolete_exact_files=[duplicate, duplicate.copy()]),
    )

    with pytest.raises(DistributionManifestError):
        build_distribution_plan(INSTALL_ROOT, manifest_path=duplicate_manifest)

    overlap_manifest = _write_manifest(
        tmp_path / "overlap",
        _manifest_with(
            obsolete_exact_files=[
                {
                    "path": ".agents/skills/spec-dock/SKILL.md",
                    "surface": "legacy-test",
                    "identities": [],
                    "on_unknown": "preserve-and-block",
                }
            ]
        ),
    )

    with pytest.raises(DistributionManifestError):
        build_distribution_plan(INSTALL_ROOT, manifest_path=overlap_manifest)

    shortcut_overlap_manifest = _write_manifest(
        tmp_path / "shortcut-overlap",
        _manifest_with(
            obsolete_exact_files=[
                {
                    "path": "spec",
                    "surface": "legacy-test",
                    "identities": [],
                    "on_unknown": "preserve-and-block",
                }
            ]
        ),
    )

    with pytest.raises(DistributionManifestError):
        build_distribution_plan(INSTALL_ROOT, manifest_path=shortcut_overlap_manifest)


@pytest.mark.parametrize(
    "protected_path",
    (
        "spec-dock/docs/README.md",
        "spec-dock/initiatives/user-owned/requirement.md",
        "spec-dock/active/issue/requirement.md",
        "spec-dock/.workbench/README.md",
    ),
)
def test_s20_protected_workspace_overlap_is_rejected(tmp_path: Path, protected_path: str) -> None:
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            obsolete_exact_files=[
                {
                    "path": protected_path,
                    "surface": "legacy-test",
                    "identities": [],
                    "on_unknown": "preserve-and-block",
                }
            ]
        ),
    )

    with pytest.raises(DistributionManifestError, match="protected workspace surface"):
        build_distribution_plan(INSTALL_ROOT, manifest_path=manifest_path)


def test_s20_physical_current_catalog_cannot_overlap_protected_workspace(tmp_path: Path) -> None:
    install_root = tmp_path / "install_root"
    protected = install_root / "spec-dock/initiatives/user-owned/requirement.md"
    protected.parent.mkdir(parents=True)
    protected.write_text("must remain user-owned\n", encoding="utf-8")
    manifest_path = _write_manifest(tmp_path, _manifest_with())

    with pytest.raises(DistributionManifestError, match="protected workspace surface"):
        build_distribution_plan(install_root, manifest_path=manifest_path)


def test_s20_ancestor_overlap_between_historical_records_is_rejected(tmp_path: Path) -> None:
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            historical_current_identities=[{"path": ".agents/legacy.md", "kind": "regular", "sha256": "a" * 64}],
            obsolete_exact_files=[{"path": ".agents/legacy.md/child", "kind": "regular", "sha256": "b" * 64}],
        ),
    )

    with pytest.raises(DistributionManifestError):
        build_distribution_plan(INSTALL_ROOT, manifest_path=manifest_path)


def test_s20_nested_historical_records_cannot_overlap_current_or_each_other(tmp_path: Path) -> None:
    current_overlap = _write_manifest(
        tmp_path / "current-overlap",
        _manifest_with(
            recognized_workspace_versions=[
                {
                    "version": "0.1.0",
                    "anchors": [
                        {
                            "path": ".agents/skills/spec-dock",
                            "kind": "regular",
                            "sha256": "a" * 64,
                            "source": {"kind": "git-blob", "ref": "old"},
                        }
                    ],
                }
            ]
        ),
    )
    with pytest.raises(DistributionManifestError):
        build_distribution_plan(INSTALL_ROOT, manifest_path=current_overlap)

    nested_overlap = _write_manifest(
        tmp_path / "nested-overlap",
        _manifest_with(
            trusted_consumer_manifests=[
                {
                    "path": ".agents/legacy-manifest.json",
                    "kind": "regular",
                    "sha256": "a" * 64,
                    "source": {"kind": "git-blob", "ref": "old"},
                    "claims": [
                        {
                            "path": ".agents/legacy-manifest.json/child",
                            "kind": "regular",
                            "sha256": "b" * 64,
                            "source": {"kind": "git-blob", "ref": "old"},
                        }
                    ],
                }
            ]
        ),
    )
    with pytest.raises(DistributionManifestError):
        build_distribution_plan(INSTALL_ROOT, manifest_path=nested_overlap)


def test_s20_historical_schema_requires_all_named_sections(tmp_path: Path) -> None:
    manifest = _manifest_with()
    del manifest["historical_shortcuts"]
    manifest_path = _write_manifest(tmp_path, manifest)

    with pytest.raises(DistributionManifestError):
        build_distribution_plan(INSTALL_ROOT, manifest_path=manifest_path)


def test_s20_scaffold_is_a_source_root_not_a_second_current_catalog(tmp_path: Path) -> None:
    scaffold_root = _minimal_scaffold_root(tmp_path)
    (scaffold_root / "docs" / "README.md").write_text("docs\n", encoding="utf-8")

    plan = build_distribution_plan(
        INSTALL_ROOT,
        manifest_path=MANIFEST_PATH,
        scaffold_root=scaffold_root,
    )

    assert {asset.path for asset in plan.current_assets} == EXPECTED_CURRENT_PATHS
    assert plan.scaffold_root == scaffold_root


def test_s25_fresh_classifies_missing_and_current_identical_without_mutation(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"current\n")

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    by_path = {action.path: action for action in plan.actions}
    assert by_path[".github/workflows/ci.yml"].action == "adopt"
    assert by_path[".github/workflows/ci.yml"].provenance == "current"
    assert by_path[".github/workflows/ci.yml"].blocked is False
    assert by_path[".github/workflows/ci.yml"].reason == "current-identity-match"
    assert by_path["spec"].action == "create"
    assert set(by_path) == {".github/workflows/ci.yml", "spec"}
    assert target.read_bytes() == b"current\n"


def test_s25_missing_current_target_is_create(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "missing-consumer"

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "create"
    assert action.provenance == "missing"
    assert action.blocked is False
    assert not target_root.exists()


def test_s25_uninstall_missing_current_target_is_already_absent(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "missing-consumer"

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="uninstall",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "prune"
    assert action.provenance == "missing"
    assert action.reason == "already-absent"
    assert action.blocked is False
    assert not target_root.exists()


def test_s25_unknown_current_collision_is_preserved_and_diagnostic_is_sanitized(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    secret = "token=super-secret"
    external_path = "/private/host/private-repository/source.py"
    target.write_text(f"{secret}\n{external_path}\n", encoding="utf-8")

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "preserve"
    assert action.provenance == "unknown"
    assert action.blocked is True
    assert action.reason == "unknown-current-collision"
    assert secret not in action.reason
    assert external_path not in action.reason
    diagnostic = action.diagnostic()
    assert diagnostic["path"] == ".github/workflows/ci.yml"
    assert secret not in repr(diagnostic)
    assert external_path not in repr(diagnostic)
    assert "inspect ownership" in str(diagnostic["operator_action"])
    assert target.read_text(encoding="utf-8") == f"{secret}\n{external_path}\n"


def test_s25_preflight_does_not_follow_final_component_swapped_to_symlink(tmp_path: Path, monkeypatch) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target = target_root / ".github/workflows/ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"user-owned\n")
    external = tmp_path / "external.yml"
    external.write_bytes(b"current\n")
    real_open = managed_distribution.os.open
    swapped = False

    def swap_before_open(path, flags, mode=0o777, *, dir_fd=None):
        nonlocal swapped
        if path == "ci.yml" and dir_fd is not None and not swapped:
            swapped = True
            target.unlink()
            target.symlink_to(external)
        return real_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(managed_distribution.os, "open", swap_before_open)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.blocked
    assert action.reason == "unsafe-target-path"
    assert target.is_symlink()


def test_s25_preflight_does_not_follow_parent_swapped_to_symlink(tmp_path: Path, monkeypatch) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    workflows = target_root / ".github/workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").write_bytes(b"user-owned\n")
    external = tmp_path / "external-workflows"
    external.mkdir()
    (external / "ci.yml").write_bytes(b"current\n")
    displaced = tmp_path / "displaced-workflows"
    real_open = managed_distribution.os.open
    swapped = False

    def swap_before_open(path, flags, mode=0o777, *, dir_fd=None):
        nonlocal swapped
        if path == "workflows" and dir_fd is not None and not swapped:
            swapped = True
            workflows.rename(displaced)
            workflows.symlink_to(external, target_is_directory=True)
        return real_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(managed_distribution.os, "open", swap_before_open)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.blocked
    assert action.reason == "unsafe-target-path"
    assert workflows.is_symlink()


def test_s25_update_upgrades_direct_historical_identity(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "upgrade"
    assert action.provenance == "historical"
    assert action.blocked is False
    assert action.reason == "direct-historical-identity-match"
    assert target.read_bytes() == old


def test_s25_fresh_historical_identity_is_preserved_and_blocked(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "preserve"
    assert action.provenance == "historical"
    assert action.reason == "historical-identity-fresh-preserve"
    assert action.blocked is True
    assert target.read_bytes() == old


def test_s25_trusted_manifest_requires_manifest_and_claim_identity(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_bytes = b'{"managed":true}\n'
    old_target = b"legacy\n"
    trusted_manifest = _regular_record(".agents/host-adapters/meta.json", manifest_bytes)
    trusted_manifest["claims"] = [_regular_record(".codex/config.toml", old_target)]
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            trusted_consumer_manifests=[trusted_manifest],
            obsolete_exact_files=[
                {
                    "path": ".codex/config.toml",
                    "surface": "legacy-test",
                    "identities": [],
                    "on_unknown": "preserve-and-block",
                }
            ],
        ),
    )
    target_root = tmp_path / "consumer"
    manifest_target = target_root / ".agents" / "host-adapters" / "meta.json"
    manifest_target.parent.mkdir(parents=True)
    manifest_target.write_bytes(manifest_bytes)
    claim_target = target_root / ".codex" / "config.toml"
    claim_target.parent.mkdir(parents=True)
    claim_target.write_bytes(old_target)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    action = next(item for item in plan.actions if item.path == ".codex/config.toml")
    assert action.action == "prune"
    assert action.provenance == "historical"
    assert action.reason == "trusted-manifest-identity-match"
    assert action.blocked is False


def test_s25_trusted_manifest_can_prove_historical_current_path(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    manifest_bytes = b'{"managed":true}\n'
    old_target = b"legacy\n"
    trusted_manifest = _regular_record(".agents/host-adapters/meta.json", manifest_bytes)
    trusted_manifest["claims"] = [_regular_record(".github/workflows/ci.yml", old_target)]
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(trusted_consumer_manifests=[trusted_manifest]),
    )
    target_root = tmp_path / "consumer"
    manifest_target = target_root / ".agents" / "host-adapters" / "meta.json"
    manifest_target.parent.mkdir(parents=True)
    manifest_target.write_bytes(manifest_bytes)
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old_target)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "upgrade"
    assert action.provenance == "historical"
    assert action.reason == "trusted-manifest-identity-match"


@pytest.mark.parametrize(
    ("setup", "expected_reason"),
    [
        ("exact-directory", "exact-path-directory"),
        ("exact-symlink", "exact-path-symlink"),
        ("parent-symlink", "symlink-container"),
    ],
)
def test_s25_path_type_collisions_block_before_any_mutation(
    tmp_path: Path,
    setup: str,
    expected_reason: str,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    if setup == "exact-directory":
        target.mkdir(parents=True)
    elif setup == "exact-symlink":
        target.parent.mkdir(parents=True)
        target.symlink_to("somewhere")
    else:
        (target_root / ".github").mkdir(parents=True)
        (target_root / "outside").mkdir()
        (target_root / ".github" / "workflows").symlink_to(target_root / "outside")

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "block"
    assert action.blocked is True
    assert action.reason == expected_reason


def test_s25_historical_hard_link_is_blocked_for_mutation(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    alias = target_root / "alias"
    alias.hardlink_to(target)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "block"
    assert action.provenance == "historical"
    assert action.reason == "hard-link-mutation-unsafe"
    assert action.blocked is True


def test_s25_current_hard_link_is_blocked_for_uninstall(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"current\n")
    alias = target_root / "alias"
    alias.hardlink_to(target)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="uninstall",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "block"
    assert action.provenance == "current"
    assert action.reason == "hard-link-mutation-unsafe"
    assert action.blocked is True


def test_s25_current_mode_mismatch_is_preserved_and_blocked_for_uninstall(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    source = install_root / ".github" / "workflows" / "ci.yml"
    source.chmod(0o755)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"current\n")
    target.chmod(0o600)
    before = target.read_bytes(), stat.S_IMODE(target.stat().st_mode)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="uninstall",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "preserve"
    assert action.provenance == "current"
    assert action.reason == "current-mode-mismatch"
    assert action.blocked is True
    with pytest.raises(DistributionApplyError, match="blocked"):
        apply_distribution_plan(plan)
    assert (target.read_bytes(), stat.S_IMODE(target.stat().st_mode)) == before


def test_s25_current_hard_linked_shortcut_is_blocked_for_uninstall(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    shortcut = target_root / "spec"
    shortcut.symlink_to("spec-dock/scripts/spec-dock")
    alias = target_root / "shortcut-alias"
    os.link(shortcut, alias, follow_symlinks=False)
    assert shortcut.lstat().st_nlink == 2

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="uninstall",
    )

    action = next(item for item in plan.actions if item.path == "spec")
    assert action.action == "block"
    assert action.provenance == "current"
    assert action.reason == "hard-link-mutation-unsafe"
    assert action.blocked is True


def test_s25_historical_hard_linked_shortcut_is_blocked_for_update(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    old_target = "legacy/spec-dock"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            historical_current_identities=[
                {
                    "path": "spec",
                    "kind": "symlink",
                    "target": old_target,
                    "source": {"kind": "test-fixture", "ref": "issue-360-test"},
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    shortcut = target_root / "spec"
    shortcut.symlink_to(old_target)
    alias = target_root / "shortcut-alias"
    os.link(shortcut, alias, follow_symlinks=False)
    assert shortcut.lstat().st_nlink == 2

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    action = next(item for item in plan.actions if item.path == "spec")
    assert action.action == "block"
    assert action.provenance == "historical"
    assert action.reason == "hard-link-mutation-unsafe"
    assert action.blocked is True


def test_s25_shortcut_uses_link_identity_without_following_target(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    shortcut = {
        "path": "spec",
        "kind": "symlink",
        "target": "spec-dock/scripts/spec-dock",
        "source": {"kind": "test-fixture", "ref": "issue-360-test"},
    }
    manifest_path = _write_manifest(tmp_path, _manifest_with(historical_shortcuts=[shortcut]))
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    (target_root / "spec").symlink_to("spec-dock/scripts/spec-dock")

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    action = next(item for item in plan.actions if item.path == "spec")
    assert action.action == "adopt"
    assert action.provenance == "current"
    assert action.blocked is False


def test_s25_update_can_classify_a_proven_historical_shortcut(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    old_target = "legacy/spec-dock"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            historical_current_identities=[
                {
                    "path": "spec",
                    "kind": "symlink",
                    "target": old_target,
                    "source": {"kind": "test-fixture", "ref": "issue-360-test"},
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    (target_root / "spec").symlink_to(old_target)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    action = next(item for item in plan.actions if item.path == "spec")
    assert action.action == "upgrade"
    assert action.provenance == "historical"
    assert action.blocked is False
    assert (target_root / "spec").is_symlink()


def test_s25_historical_shortcut_record_proves_canonical_shortcut(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    old_target = "legacy/spec-dock"
    shortcut = {
        "path": "spec",
        "kind": "symlink",
        "target": old_target,
        "source": {"kind": "test-fixture", "ref": "issue-360-test"},
    }
    manifest_path = _write_manifest(tmp_path, _manifest_with(historical_shortcuts=[shortcut]))
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    (target_root / "spec").symlink_to(old_target)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    action = next(item for item in plan.actions if item.path == "spec")
    assert action.action == "upgrade"
    assert action.provenance == "historical"
    assert action.blocked is False


def test_s25_noncanonical_historical_shortcut_is_evidence_only(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    shortcut = {
        "path": "legacy-spec",
        "kind": "symlink",
        "target": "legacy/spec-dock",
        "source": {"kind": "test-fixture", "ref": "issue-360-test"},
    }
    manifest_path = _write_manifest(tmp_path, _manifest_with(historical_shortcuts=[shortcut]))
    target_root = tmp_path / "consumer"

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    assert "legacy-spec" not in {action.path for action in plan.actions}


def test_s30_apply_materializes_missing_regular_target_without_replacing_existing_path(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / ".github" / "workflows").mkdir(parents=True)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    result = apply_distribution_plan(plan)

    assert isinstance(result, DistributionResult)
    assert result.status == "complete"
    target = target_root / ".github" / "workflows" / "ci.yml"
    assert target.read_bytes() == b"current\n"
    assert target.stat().st_nlink == 1


def test_s30_apply_upgrades_historical_regular_target_atomically(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    before_inode = target.stat().st_ino

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    result = apply_distribution_plan(plan)

    assert result.status == "complete"
    assert target.read_bytes() == b"new\n"
    assert target.stat().st_ino != before_inode


def test_s25_update_repairs_mode_when_content_is_current(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    source = install_root / ".github" / "workflows" / "ci.yml"
    source.chmod(0o755)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"current\n")
    target.chmod(0o600)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "upgrade"
    assert action.reason == "current-mode-mismatch"

    apply_distribution_plan(plan)

    assert target.read_bytes() == b"current\n"
    assert stat.S_IMODE(target.stat().st_mode) == 0o755


def test_s55_obsolete_identity_ownership_ignores_mode_drift(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    obsolete = tmp_path / "legacy-managed.md"
    obsolete.write_bytes(b"legacy\n")
    obsolete.chmod(0o755)
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            obsolete_exact_files=[
                {
                    "path": "legacy-managed.md",
                    "surface": "legacy-test-surface",
                    "identities": [_regular_record("legacy-managed.md", b"legacy\n", mode=0o644)],
                    "on_unknown": "preserve-and-block",
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    target = target_root / "legacy-managed.md"
    target_root.mkdir()
    target.write_bytes(obsolete.read_bytes())
    target.chmod(0o755)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    action = next(item for item in plan.actions if item.path == "legacy-managed.md")
    assert action.action == "prune"
    assert action.reason == "direct-obsolete-identity-match"
    assert apply_distribution_plan(plan).status == "complete"
    assert not target.exists()


def test_s30_apply_rejects_provider_mode_change_after_plan(
    tmp_path: Path,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    source = install_root / ".github/workflows/ci.yml"
    source.chmod(0o755)

    with pytest.raises(DistributionApplyError, match="provider Current asset identity changed"):
        apply_distribution_plan(plan)

    assert target.read_bytes() == old


def test_s30_apply_rejects_provider_content_change_with_same_planned_snapshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    original_source = managed_distribution._source_asset_bytes

    def changed_source(path: Path) -> tuple[bytes, managed_distribution.DistributionSourceSnapshot]:
        _content, snapshot = original_source(path)
        return b"unplanned\n", snapshot

    monkeypatch.setattr(managed_distribution, "_source_asset_bytes", changed_source)

    with pytest.raises(DistributionApplyError, match="provider Current asset content changed"):
        apply_distribution_plan(plan)

    assert target.read_bytes() == old


def test_s30_apply_retries_cleanup_of_known_stale_stage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    original_unlink = managed_distribution.os.unlink

    def fail_stage_cleanup(name, *args, **kwargs):
        if isinstance(name, str) and name.startswith(".spec-dock-file-"):
            raise OSError("simulated stage cleanup failure")
        return original_unlink(name, *args, **kwargs)

    monkeypatch.setattr(managed_distribution.os, "unlink", fail_stage_cleanup)
    with pytest.raises(DistributionApplyError, match="staging cleanup"):
        apply_distribution_plan(plan)
    stage_files = list(target.parent.glob(".spec-dock-file-*"))
    assert len(stage_files) == 1
    assert target.read_bytes() == b"new\n"

    monkeypatch.setattr(managed_distribution.os, "unlink", original_unlink)
    retry_plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    stage_ownership = managed_distribution._distribution_stage_ownership(
        ".github/workflows/ci.yml",
        stage_files[0].name,
        stage_files[0].lstat(),
    )
    assert (
        apply_distribution_plan(
            retry_plan,
            allow_stale_stage_cleanup=True,
            stage_ownership=(stage_ownership,),
        ).status
        == "complete"
    )
    assert not list(target.parent.glob(".spec-dock-file-*"))


def test_s30_apply_rebinds_stage_ownership_after_swap_for_retry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    recorded: list[managed_distribution.DistributionStageOwnership] = []
    original_unlink = managed_distribution.os.unlink
    failed = False

    def fail_once_after_swap(name, *args, **kwargs):
        nonlocal failed
        if not failed and isinstance(name, str) and name.startswith(".spec-dock-file-"):
            failed = True
            raise OSError("simulated stage cleanup failure")
        return original_unlink(name, *args, **kwargs)

    monkeypatch.setattr(managed_distribution.os, "unlink", fail_once_after_swap)
    with pytest.raises(DistributionApplyError, match="staging cleanup"):
        apply_distribution_plan(plan, stage_ownership_recorder=recorded.append)

    stage_files = list(target.parent.glob(".spec-dock-file-*"))
    assert len(stage_files) == 1
    assert target.read_bytes() == b"new\n"
    assert len(recorded) == 2
    rebound = recorded[-1]
    stage_stat = stage_files[0].lstat()
    assert (rebound.device, rebound.inode, rebound.ctime_ns) == (
        stage_stat.st_dev,
        stage_stat.st_ino,
        stage_stat.st_ctime_ns,
    )

    retry_plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    assert (
        apply_distribution_plan(
            retry_plan,
            allow_stale_stage_cleanup=True,
            stage_ownership=tuple(recorded),
        ).status
        == "complete"
    )
    assert not list(target.parent.glob(".spec-dock-file-*"))


def test_s30_apply_recovers_when_rebind_record_and_cleanup_both_fail(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    recorded: list[managed_distribution.DistributionStageOwnership] = []
    record_calls = 0
    original_unlink = managed_distribution.os.unlink
    cleanup_failures = 0

    def fail_post_swap_record(record: managed_distribution.DistributionStageOwnership) -> None:
        nonlocal record_calls
        record_calls += 1
        if record_calls == 2:
            raise RuntimeError("simulated post-swap marker write failure")
        recorded.append(record)

    def fail_stage_cleanup_twice(name, *args, **kwargs):
        nonlocal cleanup_failures
        if isinstance(name, str) and name.startswith(".spec-dock-file-") and cleanup_failures < 2:
            cleanup_failures += 1
            raise OSError("simulated repeated stage cleanup failure")
        return original_unlink(name, *args, **kwargs)

    monkeypatch.setattr(managed_distribution.os, "unlink", fail_stage_cleanup_twice)
    with pytest.raises(DistributionApplyError, match="staging cleanup"):
        apply_distribution_plan(plan, stage_ownership_recorder=fail_post_swap_record)

    stage_files = list(target.parent.glob(".spec-dock-file-*"))
    assert len(stage_files) == 1
    assert len(recorded) == 2
    rebound = recorded[-1]
    stage_stat = stage_files[0].lstat()
    assert (rebound.device, rebound.inode, rebound.ctime_ns) == (
        stage_stat.st_dev,
        stage_stat.st_ino,
        stage_stat.st_ctime_ns,
    )
    assert target.read_bytes() == b"new\n"

    monkeypatch.setattr(managed_distribution.os, "unlink", original_unlink)
    retry_plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    assert (
        apply_distribution_plan(
            retry_plan,
            allow_stale_stage_cleanup=True,
            stage_ownership=tuple(recorded),
        ).status
        == "complete"
    )
    assert not list(target.parent.glob(".spec-dock-file-*"))


def test_s30_apply_cleans_rebound_stage_when_marker_update_fails(
    tmp_path: Path,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    recorded: list[managed_distribution.DistributionStageOwnership] = []

    def fail_marker_update(record: managed_distribution.DistributionStageOwnership) -> None:
        if recorded:
            raise RuntimeError("simulated retry marker write failure")
        recorded.append(record)

    with pytest.raises(RuntimeError, match="retry marker write failure"):
        apply_distribution_plan(plan, stage_ownership_recorder=fail_marker_update)

    assert target.read_bytes() == b"new\n"
    assert not list(target.parent.glob(".spec-dock-file-*"))

    retry_plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    assert (
        apply_distribution_plan(
            retry_plan,
            allow_stale_stage_cleanup=True,
            stage_ownership=tuple(recorded),
        ).status
        == "complete"
    )


def test_s30_apply_retries_stage_cleanup_for_trusted_manifest_provenance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    trusted_bytes = b'{"managed":true}\n'
    trusted_manifest = _regular_record(".agents/host-adapters/meta.json", trusted_bytes)
    trusted_manifest["claims"] = [_regular_record(".github/workflows/ci.yml", old)]
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(trusted_consumer_manifests=[trusted_manifest]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    trusted_target = target_root / ".agents" / "host-adapters" / "meta.json"
    trusted_target.parent.mkdir(parents=True)
    trusted_target.write_bytes(trusted_bytes)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    assert next(item for item in plan.actions if item.path == ".github/workflows/ci.yml").action == "upgrade"
    recorded: list[managed_distribution.DistributionStageOwnership] = []
    original_unlink = managed_distribution.os.unlink
    failed = False

    def fail_stage_cleanup(name, *args, **kwargs):
        nonlocal failed
        if not failed and isinstance(name, str) and name.startswith(".spec-dock-file-"):
            failed = True
            raise OSError("simulated stage cleanup failure")
        return original_unlink(name, *args, **kwargs)

    monkeypatch.setattr(managed_distribution.os, "unlink", fail_stage_cleanup)
    with pytest.raises(DistributionApplyError, match="staging cleanup"):
        apply_distribution_plan(plan, stage_ownership_recorder=recorded.append)
    assert list(target.parent.glob(".spec-dock-file-*"))

    retry_plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    assert (
        apply_distribution_plan(
            retry_plan,
            allow_stale_stage_cleanup=True,
            stage_ownership=tuple(recorded),
        ).status
        == "complete"
    )
    assert not list(target.parent.glob(".spec-dock-file-*"))


def test_s30_historical_stage_identities_include_recognized_anchor(
    tmp_path: Path,
) -> None:
    old = b"old\n"
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            recognized_workspace_versions=[
                {
                    "version": "0.1.0",
                    "anchors": [_regular_record("legacy.txt", old)],
                }
            ]
        ),
    )
    plan = build_distribution_plan(install_root, manifest_path=manifest_path)

    historical = managed_distribution._historical_stage_identities(plan, "legacy.txt")

    assert historical == (
        managed_distribution.DistributionIdentity(
            kind="regular",
            sha256=hashlib.sha256(old).hexdigest(),
            mode=None,
        ),
    )


def test_s30_apply_refreshes_snapshots_after_stale_stage_cleanup_for_later_action(
    tmp_path: Path,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    second_source = install_root / ".github" / "workflows" / "second.yml"
    second_source.write_bytes(b"second\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    first_target = target_root / ".github" / "workflows" / "ci.yml"
    first_target.parent.mkdir(parents=True)
    first_target.write_bytes(b"current\n")
    source = install_root / ".github" / "workflows" / "ci.yml"
    stale_identity = managed_distribution.DistributionIdentity(
        kind="regular",
        sha256=hashlib.sha256(b"current\n").hexdigest(),
        mode=stat.S_IMODE(source.stat().st_mode),
    )
    stale_stage = first_target.parent / managed_distribution._distribution_stage_name(
        ".github/workflows/ci.yml",
        stale_identity,
    )
    stale_stage.write_bytes(b"current\n")

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    stage_ownership = managed_distribution._distribution_stage_ownership(
        ".github/workflows/ci.yml",
        stale_stage.name,
        stale_stage.lstat(),
    )
    assert (
        apply_distribution_plan(
            plan,
            allow_stale_stage_cleanup=True,
            stage_ownership=(stage_ownership,),
        ).status
        == "complete"
    )
    assert first_target.read_bytes() == b"current\n"
    assert (target_root / ".github/workflows/second.yml").read_bytes() == b"second\n"
    assert not list(first_target.parent.glob(".spec-dock-file-*"))


def test_s30_apply_rejects_external_parent_created_after_preflight(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"first\n")
    second_source = install_root / "zz" / "second.yml"
    second_source.parent.mkdir(parents=True)
    second_source.write_bytes(b"second\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    original_apply = managed_distribution._apply_distribution_action
    injected = False

    def apply_then_create_external_parent(
        current_plan: object,
        root: Path,
        action: object,
        snapshot: object,
        bindings: dict[str, object],
    ) -> None:
        nonlocal injected
        original_apply(current_plan, root, action, snapshot, bindings)  # type: ignore[arg-type]
        if not injected:
            injected = True
            (root / "zz").mkdir()

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", apply_then_create_external_parent)

    with pytest.raises(DistributionApplyError, match="identity"):
        apply_distribution_plan(plan)

    assert (target_root / ".github" / "workflows" / "ci.yml").read_bytes() == b"first\n"
    assert not (target_root / "zz" / "second.yml").exists()


def test_s30_apply_rejects_external_nested_parent_after_operation_parent_creation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"first\n")
    first_source = install_root / "zz" / "first.yml"
    first_source.parent.mkdir(parents=True)
    first_source.write_bytes(b"first nested\n")
    second_source = install_root / "zz" / "yy" / "second.yml"
    second_source.parent.mkdir(parents=True)
    second_source.write_bytes(b"second nested\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    original_apply = managed_distribution._apply_distribution_action
    injected = False

    def apply_then_create_external_nested_parent(
        current_plan: object,
        root: Path,
        action: object,
        snapshot: object,
        bindings: dict[str, object],
    ) -> None:
        nonlocal injected
        original_apply(current_plan, root, action, snapshot, bindings)  # type: ignore[arg-type]
        if not injected and getattr(action, "path", "") == "zz/first.yml":
            injected = True
            (root / "zz" / "yy").mkdir()

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", apply_then_create_external_nested_parent)

    with pytest.raises(DistributionApplyError, match="identity"):
        apply_distribution_plan(plan)

    assert (target_root / "zz" / "first.yml").read_bytes() == b"first nested\n"
    assert (target_root / "zz" / "yy").is_dir()
    assert not (target_root / "zz" / "yy" / "second.yml").exists()


def test_s30_apply_upgrade_keeps_target_unchanged_when_staging_write_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    def fail_staging_write(fd: int, *_args: object, **_kwargs: object) -> None:
        os.write(fd, b"partial\n")
        raise OSError("no space left on device")

    monkeypatch.setattr(managed_distribution, "_write_fd_bytes", fail_staging_write)

    with pytest.raises(DistributionApplyError, match=r"apply failed|staging"):
        apply_distribution_plan(plan)

    assert target.read_bytes() == old
    assert not list(target.parent.glob(".spec-dock-file-*"))


def test_s30_apply_records_partial_stage_identity_when_cleanup_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    recorded: list[managed_distribution.DistributionStageOwnership] = []
    original_write = managed_distribution._write_fd_bytes
    original_unlink = managed_distribution.os.unlink
    cleanup_failed = False

    def fail_stage_cleanup_once(name, *args, **kwargs):
        nonlocal cleanup_failed
        if not cleanup_failed and isinstance(name, str) and name.startswith(".spec-dock-file-"):
            cleanup_failed = True
            raise OSError("simulated stage cleanup failure")
        return original_unlink(name, *args, **kwargs)

    def fail_staging_write(fd: int, *_args: object, **_kwargs: object) -> None:
        os.write(fd, b"partial\n")
        raise OSError("no space left on device")

    monkeypatch.setattr(managed_distribution, "_write_fd_bytes", fail_staging_write)
    monkeypatch.setattr(managed_distribution.os, "unlink", fail_stage_cleanup_once)

    with pytest.raises(DistributionApplyError, match="staging cleanup"):
        apply_distribution_plan(plan, stage_ownership_recorder=recorded.append)

    assert target.read_bytes() == old
    stage_files = list(target.parent.glob(".spec-dock-file-*"))
    assert len(stage_files) == 1
    assert len(recorded) == 2
    refreshed = recorded[-1]
    stage_stat = stage_files[0].lstat()
    assert (refreshed.device, refreshed.inode, refreshed.ctime_ns) == (
        stage_stat.st_dev,
        stage_stat.st_ino,
        stage_stat.st_ctime_ns,
    )

    monkeypatch.setattr(managed_distribution, "_write_fd_bytes", original_write)
    monkeypatch.setattr(managed_distribution.os, "unlink", original_unlink)
    retry_plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    assert (
        apply_distribution_plan(
            retry_plan,
            allow_stale_stage_cleanup=True,
            stage_ownership=(refreshed,),
        ).status
        == "complete"
    )
    assert target.read_bytes() == b"new\n"
    assert not list(target.parent.glob(".spec-dock-file-*"))


def test_s30_apply_create_cleans_stage_when_staging_write_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    def fail_staging_write(*_args: object, **_kwargs: object) -> None:
        raise OSError("no space left on device")

    monkeypatch.setattr(managed_distribution, "_write_fd_bytes", fail_staging_write)

    with pytest.raises(DistributionApplyError, match=r"apply failed|staging"):
        apply_distribution_plan(plan)

    assert not list(target_root.rglob(".spec-dock-file-*"))


def test_s30_apply_create_records_partial_stage_identity_when_cleanup_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    recorded: list[managed_distribution.DistributionStageOwnership] = []
    original_write = managed_distribution._write_fd_bytes
    original_unlink = managed_distribution.os.unlink
    cleanup_failed = False

    def fail_stage_cleanup_once(name, *args, **kwargs):
        nonlocal cleanup_failed
        if not cleanup_failed and isinstance(name, str) and name.startswith(".spec-dock-file-"):
            cleanup_failed = True
            raise OSError("simulated stage cleanup failure")
        return original_unlink(name, *args, **kwargs)

    def fail_staging_write(fd: int, *_args: object, **_kwargs: object) -> None:
        os.write(fd, b"partial\n")
        raise OSError("no space left on device")

    monkeypatch.setattr(managed_distribution, "_write_fd_bytes", fail_staging_write)
    monkeypatch.setattr(managed_distribution.os, "unlink", fail_stage_cleanup_once)

    with pytest.raises(DistributionApplyError, match="staging cleanup"):
        apply_distribution_plan(plan, stage_ownership_recorder=recorded.append)

    stage_files = list(target_root.rglob(".spec-dock-file-*"))
    assert len(stage_files) == 1
    assert len(recorded) == 2
    refreshed = recorded[-1]
    stage_stat = stage_files[0].lstat()
    assert (refreshed.device, refreshed.inode, refreshed.ctime_ns) == (
        stage_stat.st_dev,
        stage_stat.st_ino,
        stage_stat.st_ctime_ns,
    )

    monkeypatch.setattr(managed_distribution, "_write_fd_bytes", original_write)
    monkeypatch.setattr(managed_distribution.os, "unlink", original_unlink)
    retry_plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    assert (
        apply_distribution_plan(
            retry_plan,
            allow_stale_stage_cleanup=True,
            stage_ownership=(refreshed,),
        ).status
        == "complete"
    )
    assert (target_root / ".github" / "workflows" / "ci.yml").read_bytes() == b"new\n"
    assert not list(target_root.rglob(".spec-dock-file-*"))


def test_s30_apply_prunes_historical_target_without_following_symlink(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            obsolete_exact_files=[
                {
                    "path": ".agents/skills/legacy/SKILL.md",
                    "surface": "legacy-test",
                    "identities": [_regular_record(".agents/skills/legacy/SKILL.md", old)],
                    "on_unknown": "preserve-and-block",
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".agents" / "skills" / "legacy" / "SKILL.md"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="uninstall",
    )

    result = apply_distribution_plan(plan)

    assert result.status == "complete"
    assert not target.exists()


def test_s55_apply_prunes_proven_obsolete_target_during_update(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    old = b"legacy-managed\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            obsolete_exact_files=[
                {
                    "path": ".codex/config.toml",
                    "surface": "legacy-codex-surface",
                    "identities": [_regular_record(".codex/config.toml", old)],
                    "on_unknown": "preserve-and-block",
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".codex" / "config.toml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    action = next(item for item in plan.actions if item.path == ".codex/config.toml")
    assert action.action == "prune"
    assert action.provenance == "historical"
    assert action.blocked is False

    result = apply_distribution_plan(plan)

    assert result.status == "complete"
    assert not target.exists()


def test_s55_mode_mismatch_still_prunes_obsolete_target(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    old = b"legacy-managed\n"
    record = _regular_record(".codex/config.toml", old)
    record["mode"] = 0o644
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            obsolete_exact_files=[
                {
                    "path": ".codex/config.toml",
                    "surface": "legacy-codex-surface",
                    "identities": [record],
                    "on_unknown": "preserve-and-block",
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".codex" / "config.toml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    target.chmod(0o755)
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    action = next(item for item in plan.actions if item.path == ".codex/config.toml")
    assert action.action == "prune"
    assert action.reason == "direct-obsolete-identity-match"
    assert action.blocked is False
    assert apply_distribution_plan(plan).status == "complete"
    assert not target.exists()


@pytest.mark.parametrize(
    ("target_kind", "expected_reason"),
    [
        ("modified", "obsolete-identity-unknown"),
        ("symlink", "obsolete-identity-unknown"),
        ("directory", "exact-path-directory"),
    ],
)
def test_s55_unknown_or_unsafe_obsolete_target_blocks_before_mutation(
    tmp_path: Path,
    target_kind: str,
    expected_reason: str,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    old = b"legacy-managed\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            obsolete_exact_files=[
                {
                    "path": ".codex/config.toml",
                    "surface": "legacy-codex-surface",
                    "identities": [_regular_record(".codex/config.toml", old)],
                    "on_unknown": "preserve-and-block",
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".codex" / "config.toml"
    target.parent.mkdir(parents=True)
    if target_kind == "modified":
        target.write_bytes(b"user-owned\n")
    elif target_kind == "symlink":
        outside = tmp_path / "outside.txt"
        outside.write_bytes(b"outside\n")
        target.symlink_to(outside)
    else:
        target.mkdir()
    before = target_root / ".codex"
    before_snapshot = (
        target.lstat(),
        tuple(sorted(path.relative_to(before).as_posix() for path in before.rglob("*"))),
    )

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    action = next(item for item in plan.actions if item.path == ".codex/config.toml")
    assert action.action == ("block" if target_kind == "directory" else "preserve")
    assert action.reason == expected_reason
    assert action.blocked is True
    with pytest.raises(DistributionApplyError, match="blocked"):
        apply_distribution_plan(plan)

    assert target.exists() or target.is_symlink()
    assert (
        target.lstat(),
        tuple(sorted(path.relative_to(before).as_posix() for path in before.rglob("*"))),
    ) == before_snapshot


def test_s30_apply_blocks_root_rebind_before_any_write(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / ".github" / "workflows").mkdir(parents=True)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    displaced = tmp_path / "displaced-consumer"
    target_root.rename(displaced)
    target_root.mkdir()
    sentinel = target_root / "sentinel.txt"
    sentinel.write_text("replacement\n", encoding="utf-8")

    with pytest.raises(DistributionApplyError, match="identity"):
        apply_distribution_plan(plan)

    assert sentinel.read_text(encoding="utf-8") == "replacement\n"
    assert not (target_root / ".github" / "workflows" / "ci.yml").exists()
    assert not (displaced / ".github" / "workflows" / "ci.yml").exists()


def test_s30_apply_blocks_root_rebind_after_preflight_before_parent_creation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    displaced = tmp_path / "displaced-consumer"
    original_open = managed_distribution._open_distribution_parent_chain
    switched = False

    def switch_root_before_open(
        root: Path,
        relative_path: str,
        *,
        create_missing: bool = False,
        expected_snapshot: DistributionTargetSnapshot | None = None,
    ) -> tuple[int, ...]:
        nonlocal switched
        if not switched:
            switched = True
            root.rename(displaced)
            root.mkdir()
            (root / "sentinel.txt").write_text("replacement\n", encoding="utf-8")
        return original_open(
            root,
            relative_path,
            create_missing=create_missing,
            expected_snapshot=expected_snapshot,
        )

    monkeypatch.setattr(managed_distribution, "_open_distribution_parent_chain", switch_root_before_open)

    with pytest.raises(DistributionApplyError, match="identity"):
        apply_distribution_plan(plan)

    assert (target_root / "sentinel.txt").read_text(encoding="utf-8") == "replacement\n"
    assert not (target_root / ".github").exists()
    assert not (displaced / ".github" / "workflows" / "ci.yml").exists()


def test_s30_apply_blocks_root_rebind_during_data_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    displaced = tmp_path / "displaced-consumer"
    original_write = managed_distribution._write_fd_bytes
    switched = False

    def switch_root_before_write(fd: int, content: bytes, *, before_mutation: object = None) -> None:
        nonlocal switched
        if not switched:
            switched = True
            target_root.rename(displaced)
            target_root.mkdir()
            (target_root / "sentinel.txt").write_text("replacement\n", encoding="utf-8")
        original_write(fd, content, before_mutation=before_mutation)  # type: ignore[arg-type]

    monkeypatch.setattr(managed_distribution, "_write_fd_bytes", switch_root_before_write)

    with pytest.raises(DistributionApplyError, match="identity"):
        apply_distribution_plan(plan)

    assert (target_root / "sentinel.txt").read_text(encoding="utf-8") == "replacement\n"
    assert not (target_root / ".github").exists()
    assert not (displaced / ".github" / "workflows" / "ci.yml").exists()


def test_s30_apply_blocks_replaced_ancestor_created_by_prior_action(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    extra_source = install_root / ".agents" / "skills" / "legacy" / "SKILL.md"
    extra_source.parent.mkdir(parents=True)
    extra_source.write_bytes(b"legacy\n")
    (extra_source.parent / "README.md").write_bytes(b"legacy-readme\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    original_apply = managed_distribution._apply_distribution_action
    replaced = False

    def replace_created_ancestor(
        current_plan: object,
        root: Path,
        action: object,
        snapshot: object,
        bindings: dict[str, object],
    ) -> None:
        nonlocal replaced
        original_apply(current_plan, root, action, snapshot, bindings)  # type: ignore[arg-type]
        if not replaced and getattr(action, "path", "").startswith(".agents/"):
            ancestor = root / ".agents"
            displaced = root / ".agents-old"
            ancestor.rename(displaced)
            ancestor.mkdir()
            (ancestor / "sentinel.txt").write_text("replacement\n", encoding="utf-8")
            replaced = True

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", replace_created_ancestor)

    with pytest.raises(DistributionApplyError, match="identity"):
        apply_distribution_plan(plan)

    assert (target_root / ".agents" / "sentinel.txt").read_text(encoding="utf-8") == "replacement\n"
    assert not (target_root / ".agents" / "skills").exists()


def test_s30_apply_blocks_parent_rebind_before_any_write(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    parent = target_root / ".github" / "workflows"
    parent.mkdir(parents=True)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    displaced = target_root / ".github" / "workflows-old"
    parent.rename(displaced)
    parent.mkdir()
    sentinel = parent / "sentinel.txt"
    sentinel.write_text("replacement\n", encoding="utf-8")

    with pytest.raises(DistributionApplyError, match="identity"):
        apply_distribution_plan(plan)

    assert sentinel.read_text(encoding="utf-8") == "replacement\n"
    assert not (parent / "ci.yml").exists()
    assert not (displaced / "ci.yml").exists()


def test_s30_apply_blocks_destination_appearance_without_overwrite(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    parent = target_root / ".github" / "workflows"
    parent.mkdir(parents=True)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    target = parent / "ci.yml"
    target.write_bytes(b"user-owned\n")

    with pytest.raises(DistributionApplyError, match="identity"):
        apply_distribution_plan(plan)

    assert target.read_bytes() == b"user-owned\n"


def test_s30_apply_blocks_hard_link_prune_without_mutation(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"current\n")
    alias = target_root / "alias"
    alias.hardlink_to(target)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="uninstall",
    )

    with pytest.raises(DistributionApplyError, match="blocked"):
        apply_distribution_plan(plan)

    assert target.read_bytes() == b"current\n"
    assert alias.read_bytes() == b"current\n"


def test_s30_apply_materializes_canonical_shortcut_without_following_target(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    result = apply_distribution_plan(plan)

    assert result.status == "complete"
    shortcut = target_root / "spec"
    assert shortcut.is_symlink()
    assert shortcut.readlink().as_posix() == "spec-dock/scripts/spec-dock"


def test_s30_apply_retries_symlink_create_stage_record_and_cleanup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    recorded: list[managed_distribution.DistributionStageOwnership] = []
    original_unlink = managed_distribution.os.unlink
    recorder_failed = False
    cleanup_failed = False

    def record_stage(record: managed_distribution.DistributionStageOwnership) -> None:
        nonlocal recorder_failed
        if record.file_type == "symlink" and not recorder_failed:
            recorder_failed = True
            raise OSError("simulated symlink stage recorder failure")
        recorded.append(record)

    def fail_symlink_cleanup_once(name, *args, **kwargs):
        nonlocal cleanup_failed
        if not cleanup_failed and isinstance(name, str) and name.startswith(".spec-dock-symlink-"):
            cleanup_failed = True
            raise OSError("simulated symlink stage cleanup failure")
        return original_unlink(name, *args, **kwargs)

    monkeypatch.setattr(managed_distribution.os, "unlink", fail_symlink_cleanup_once)

    with pytest.raises(DistributionApplyError, match="staging cleanup"):
        apply_distribution_plan(plan, stage_ownership_recorder=record_stage)

    stage_files = list(target_root.rglob(".spec-dock-symlink-*"))
    assert len(stage_files) == 1
    symlink_record = next(item for item in recorded if item.file_type == "symlink")
    stage_stat = stage_files[0].lstat()
    assert (symlink_record.device, symlink_record.inode, symlink_record.ctime_ns) == (
        stage_stat.st_dev,
        stage_stat.st_ino,
        stage_stat.st_ctime_ns,
    )

    monkeypatch.setattr(managed_distribution.os, "unlink", original_unlink)
    retry_plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    assert (
        apply_distribution_plan(
            retry_plan,
            allow_stale_stage_cleanup=True,
            stage_ownership=(symlink_record,),
        ).status
        == "complete"
    )
    shortcut = target_root / "spec"
    assert shortcut.is_symlink()
    assert shortcut.readlink().as_posix() == "spec-dock/scripts/spec-dock"
    assert not list(target_root.rglob(".spec-dock-symlink-*"))


def test_s30_apply_upgrades_canonical_shortcut_with_no_replace_publish(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            historical_shortcuts=[
                {
                    "path": "spec",
                    "kind": "symlink",
                    "target": "legacy/spec-dock",
                    "source": {"kind": "test-fixture", "ref": "issue-360-test"},
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    shortcut = target_root / "spec"
    shortcut.symlink_to("legacy/spec-dock")

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    result = apply_distribution_plan(plan)

    assert result.status == "complete"
    assert shortcut.is_symlink()
    assert shortcut.readlink().as_posix() == "spec-dock/scripts/spec-dock"
    assert not list(target_root.glob(".spec-dock-symlink-*"))


def test_s30_apply_retries_cleanup_of_known_stale_symlink_stage(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            historical_shortcuts=[
                {
                    "path": "spec",
                    "kind": "symlink",
                    "target": "legacy/spec-dock",
                    "source": {"kind": "test-fixture", "ref": "issue-360-test"},
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    shortcut = target_root / "spec"
    shortcut.symlink_to("legacy/spec-dock")
    stale_stage = target_root / managed_distribution._distribution_stage_name(
        "spec",
        managed_distribution.DistributionIdentity(kind="symlink", target="spec-dock/scripts/spec-dock"),
    )
    stale_stage.symlink_to("spec-dock/scripts/spec-dock")

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    stage_ownership = managed_distribution._distribution_stage_ownership("spec", stale_stage.name, stale_stage.lstat())
    assert (
        apply_distribution_plan(
            plan,
            allow_stale_stage_cleanup=True,
            stage_ownership=(stage_ownership,),
        ).status
        == "complete"
    )
    assert shortcut.readlink().as_posix() == "spec-dock/scripts/spec-dock"
    assert not list(target_root.glob(".spec-dock-symlink-*"))


def test_s30_apply_preserves_unknown_stage_like_sibling(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    unknown = target_root / ".github" / "workflows" / ".spec-dock-file-user"
    unknown.parent.mkdir(parents=True)
    unknown.write_bytes(b"current\n")

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    assert apply_distribution_plan(plan).status == "complete"
    assert unknown.read_bytes() == b"current\n"


def test_s30_apply_preserves_unrecorded_exact_stage_collision(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    initial_plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    action = next(item for item in initial_plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "create"
    expected = next(item.identity for item in initial_plan.current_assets if item.path == action.path)
    stage = target_root / ".github" / "workflows" / managed_distribution._distribution_stage_name(action.path, expected)
    stage.parent.mkdir(parents=True, exist_ok=True)
    stage.write_bytes(b"current\n")
    before = stage.lstat()
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    assert next(item for item in plan.actions if item.path == ".github/workflows/ci.yml").action == "create"
    assert stage.name == managed_distribution._distribution_stage_name(
        action.path,
        next(item.identity for item in plan.current_assets if item.path == action.path),
    )
    with pytest.raises(DistributionApplyError, match="managed target apply failed"):
        apply_distribution_plan(plan, allow_stale_stage_cleanup=True)
    with pytest.raises(DistributionApplyError, match="managed target apply failed"):
        apply_distribution_plan(plan, allow_stale_stage_cleanup=True)

    after = stage.lstat()
    assert (after.st_dev, after.st_ino, after.st_ctime_ns) == (before.st_dev, before.st_ino, before.st_ctime_ns)
    assert stage.read_bytes() == b"current\n"


def test_s30_symlink_upgrade_blocks_before_unlink_without_no_replace_support(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            historical_shortcuts=[
                {
                    "path": "spec",
                    "kind": "symlink",
                    "target": "legacy/spec-dock",
                    "source": {"kind": "test-fixture", "ref": "issue-360-test"},
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    shortcut = target_root / "spec"
    shortcut.symlink_to("legacy/spec-dock")

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    def unsupported_no_replace() -> tuple[object, int]:
        raise DistributionApplyError("platform lacks required atomic replace support")

    monkeypatch.setattr(
        managed_distribution,
        "_resolve_distribution_swap_rename",
        unsupported_no_replace,
    )

    with pytest.raises(DistributionApplyError, match="atomic replace"):
        apply_distribution_plan(plan)

    assert shortcut.is_symlink()
    assert shortcut.readlink().as_posix() == "legacy/spec-dock"
    assert not list(target_root.glob(".spec-dock-symlink-*"))


def _s35_version_manifest(tmp_path: Path, *, version: str = "1.2.3") -> Path:
    target_root = tmp_path / "consumer"
    scripts = target_root / "spec-dock" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "spec-dock").write_bytes(b"runtime\n")
    (target_root / "spec-dock" / ".gitignore").write_bytes(b"ignore\n")
    (target_root / "spec-dock" / "spec-dock.version").write_text(f"{version}\n", encoding="ascii")
    manifest = _manifest_with(
        recognized_workspace_versions=[
            {
                "version": version,
                "anchors": [
                    _regular_record("spec-dock/scripts/spec-dock", b"runtime\n"),
                    _regular_record("spec-dock/.gitignore", b"ignore\n"),
                ],
            }
        ]
    )
    return _write_manifest(tmp_path / "manifest", manifest)


def test_s35_admission_accepts_fresh_and_recognized_workspace_without_writes(tmp_path: Path) -> None:
    manifest_path = _s35_version_manifest(tmp_path)
    target_root = tmp_path / "consumer"
    before = {path.relative_to(tmp_path): path.read_bytes() for path in target_root.rglob("*") if path.is_file()}

    admission = admit_distribution_operation(
        target_root,
        operation="update",
        package_version="1.2.4",
        manifest_path=manifest_path,
    )

    assert admission.status == "recognized"
    assert admission.target_version == "1.2.3"
    after = {path.relative_to(tmp_path): path.read_bytes() for path in target_root.rglob("*") if path.is_file()}
    assert after == before


@pytest.mark.parametrize(
    ("version_bytes", "reason"),
    [
        (b"1.2.3", "invalid-version"),
        (b"1.2.3\r\n", "invalid-version"),
        (b"\xef\xbb\xbf1.2.3\n", "invalid-version"),
        (b"1.2.3\nextra\n", "invalid-version"),
    ],
)
def test_s35_admission_rejects_noncanonical_version_before_mutation(
    tmp_path: Path,
    version_bytes: bytes,
    reason: str,
) -> None:
    manifest_path = _s35_version_manifest(tmp_path)
    version_path = tmp_path / "consumer" / "spec-dock" / "spec-dock.version"
    version_path.write_bytes(version_bytes)
    before = {
        path.relative_to(tmp_path): path.read_bytes() for path in (tmp_path / "consumer").rglob("*") if path.is_file()
    }

    with pytest.raises(DistributionAdmissionError) as exc_info:
        admit_distribution_operation(
            tmp_path / "consumer",
            operation="update",
            package_version="1.2.4",
            manifest_path=manifest_path,
        )

    assert exc_info.value.reason == reason
    after = {
        path.relative_to(tmp_path): path.read_bytes() for path in (tmp_path / "consumer").rglob("*") if path.is_file()
    }
    assert after == before


def test_s35_admission_rejects_hard_link_and_newer_workspace(tmp_path: Path) -> None:
    manifest_path = _s35_version_manifest(tmp_path, version="1.2.4")
    target_root = tmp_path / "consumer"
    version_path = target_root / "spec-dock" / "spec-dock.version"
    external = tmp_path / "external-version"
    external.write_bytes(b"1.2.4\n")
    version_path.unlink()
    version_path.hardlink_to(external)
    with pytest.raises(DistributionAdmissionError, match="hard-link"):
        admit_distribution_operation(
            target_root,
            operation="update",
            package_version="1.2.5",
            manifest_path=manifest_path,
        )

    version_path.unlink()
    version_path.write_text("1.2.4\n", encoding="ascii")
    with pytest.raises(DistributionAdmissionError, match="downgrade-blocked"):
        admit_distribution_operation(
            target_root,
            operation="update",
            package_version="1.2.3",
            manifest_path=manifest_path,
        )


def test_s35_admission_rejects_anchor_mismatch_and_symlink_version(tmp_path: Path) -> None:
    manifest_path = _s35_version_manifest(tmp_path)
    target_root = tmp_path / "consumer"
    runtime = target_root / "spec-dock" / "scripts" / "spec-dock"
    runtime.write_bytes(b"edited\n")

    with pytest.raises(DistributionAdmissionError, match="anchor-mismatch"):
        admit_distribution_operation(
            target_root,
            operation="update",
            package_version="1.2.4",
            manifest_path=manifest_path,
        )

    version_path = target_root / "spec-dock" / "spec-dock.version"
    version_path.unlink()
    external = tmp_path / "external-version"
    external.write_bytes(b"1.2.3\n")
    version_path.symlink_to(external)
    with pytest.raises(DistributionAdmissionError, match="symlink"):
        admit_distribution_operation(
            target_root,
            operation="update",
            package_version="1.2.4",
            manifest_path=manifest_path,
        )


def test_s35_cross_root_retry_replay_and_dual_marker_are_blocked(tmp_path: Path) -> None:
    manifest_path = _s35_version_manifest(tmp_path)
    source_root = tmp_path / "consumer"
    marker = source_root / "spec-dock" / ".distribution-retry.json"
    source_stat = source_root.stat()
    marker.write_text(
        json.dumps({
            "schema_version": 1,
            "operation": "update",
            "package_version": "1.2.4",
            "target_root": {"device": source_stat.st_dev, "inode": source_stat.st_ino},
            "last_completed_phase": "preflight-complete",
            "purpose": "distribution-rerun",
        }),
        encoding="utf-8",
    )
    admission = admit_distribution_operation(
        source_root,
        operation="update",
        package_version="1.2.4",
        manifest_path=manifest_path,
    )
    assert admission.status == "retry"
    replay_root = tmp_path / "replay"
    replay_root.mkdir()
    (replay_root / "spec-dock").mkdir()
    (replay_root / "spec-dock" / ".distribution-retry.json").write_bytes(marker.read_bytes())

    with pytest.raises(DistributionAdmissionError, match="cross-root-replay"):
        admit_distribution_operation(
            replay_root,
            operation="update",
            package_version="1.2.4",
            manifest_path=manifest_path,
        )

    (replay_root / "spec-dock" / ".uninstall-retry.json").write_text(
        json.dumps({"schema_version": 1, "managed_by": "spec-dock", "purpose": "uninstall-rerun"}),
        encoding="utf-8",
    )
    with pytest.raises(DistributionAdmissionError, match="dual-marker"):
        admit_distribution_operation(
            replay_root,
            operation="update",
            package_version="1.2.4",
            manifest_path=manifest_path,
        )


def test_s35_legacy_uninstall_marker_remains_admissible_without_version(tmp_path: Path) -> None:
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    (target_root / "spec-dock" / ".uninstall-retry.json").write_text(
        json.dumps({"schema_version": 1, "managed_by": "spec-dock", "purpose": "uninstall-rerun"}),
        encoding="utf-8",
    )
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())

    admission = admit_distribution_operation(
        target_root,
        operation="uninstall",
        package_version="1.2.3",
        manifest_path=manifest_path,
    )

    assert admission.status == "uninstall-retry"


def test_s35_retry_marker_authority_precedes_empty_workspace_fast_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    monkeypatch.setattr(
        managed_distribution,
        "_read_uninstall_retry_marker_for_admission",
        lambda _target_root: True,
    )

    with pytest.raises(DistributionAdmissionError, match="uninstall-retry-present"):
        admit_distribution_operation(
            target_root,
            operation="fresh",
            package_version="1.2.3",
            manifest_path=manifest_path,
        )
