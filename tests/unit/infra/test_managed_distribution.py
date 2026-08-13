from __future__ import annotations

import hashlib
import json
import stat
from pathlib import Path

import pytest

from spec_dock.managed_distribution import (
    DistributionManifestError,
    build_distribution_plan,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
INSTALL_ROOT = REPO_ROOT / "src" / "spec_dock" / "assets" / "install_root"
MANIFEST_PATH = REPO_ROOT / "src" / "spec_dock" / "assets" / "managed_distribution.json"

EXPECTED_CURRENT_PATHS = frozenset(
    {
        ".agents/skills/spec-dock/SKILL.md",
        ".agents/skills/spec-dock-grill-with-docs/SKILL.md",
        ".agents/skills/spec-dock-grill-with-docs/agents/openai.yaml",
        ".agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py",
        ".github/workflows/ci.yml",
    }
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


def _regular_record(path: str, content: bytes, *, source_kind: str = "test-fixture") -> dict[str, object]:
    return {
        "path": path,
        "kind": "regular",
        "sha256": hashlib.sha256(content).hexdigest(),
        "source": {"kind": source_kind, "ref": "issue-360-test"},
    }


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
    assert plan.manifest.obsolete_exact_files == ()
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
    assert raw["obsolete_exact_files"] == []


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
            historical_current_identities=[
                {"path": ".agents/legacy.md", "kind": "regular", "sha256": "a" * 64}
            ],
            obsolete_exact_files=[
                {"path": ".agents/legacy.md/child", "kind": "regular", "sha256": "b" * 64}
            ],
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
