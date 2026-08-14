from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

import pytest

import spec_dock.managed_distribution as managed_distribution
from spec_dock.managed_distribution import (
    DistributionAdmissionError,
    DistributionApplyError,
    DistributionManifestError,
    DistributionResult,
    DistributionTargetSnapshot,
    admit_distribution_operation,
    apply_distribution_plan,
    build_distribution_plan,
)

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
MANIFEST_FIELDS = {
    "schema_version",
    "recognized_workspace_versions",
    "historical_current_identities",
    "trusted_consumer_manifests",
    "obsolete_exact_files",
    "historical_shortcuts",
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


def test_s20_public_catalog_is_derived_from_physical_install_root() -> None:
    plan = build_distribution_plan(INSTALL_ROOT, manifest_path=MANIFEST_PATH)

    assert {asset.path for asset in plan.current_assets} == EXPECTED_CURRENT_PATHS
    assert plan.actions == ()
    assert plan.manifest.schema_version == 1
    assert plan.manifest.historical_current_identities == ()
    obsolete_paths = {item["path"] for item in plan.manifest.obsolete_exact_files}
    assert len(obsolete_paths) == 75
    assert obsolete_paths >= EXPECTED_OBSOLETE_SKILL_PATHS
    assert ".agents/host-adapters/meta.json" in obsolete_paths
    assert any(path.startswith(".codex/") for path in obsolete_paths)
    assert any(path.startswith(".github/agents/") for path in obsolete_paths)
    for asset in plan.current_assets:
        source = INSTALL_ROOT / asset.path
        assert asset.identity.kind == "regular"
        assert asset.identity.sha256 == hashlib.sha256(source.read_bytes()).hexdigest()
        assert asset.identity.mode == stat.S_IMODE(source.stat().st_mode)


def test_s20_current_catalog_is_not_duplicated_in_historical_manifest() -> None:
    raw = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert set(raw) == MANIFEST_FIELDS
    assert not any(key in raw for key in {"current", "current_assets", "current_catalog"})
    assert raw["historical_current_identities"] == []
    obsolete_paths = {item["path"] for item in raw["obsolete_exact_files"]}
    assert len(obsolete_paths) == 75
    assert obsolete_paths >= EXPECTED_OBSOLETE_SKILL_PATHS
    assert not any(item["path"] in EXPECTED_CURRENT_PATHS for item in raw["obsolete_exact_files"])


def test_s55_obsolete_catalog_is_bound_to_reproducible_git_source() -> None:
    raw = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    records = [identity for item in raw["obsolete_exact_files"] for identity in item["identities"]]

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
    scaffold_root = tmp_path / "spec_dock"
    (scaffold_root / "docs").mkdir(parents=True)
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

    def changed_source(path: Path) -> tuple[bytes, int]:
        content, mode = original_source(path)
        return content, 0o755 if mode != 0o755 else 0o644

    monkeypatch.setattr(managed_distribution, "_source_asset_bytes", changed_source)

    with pytest.raises(DistributionApplyError, match="provider Current asset mode changed"):
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
