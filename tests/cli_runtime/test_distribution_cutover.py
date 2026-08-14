from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import pytest

from spec_dock import cli
from tests.cli_runtime.harness import main

REPO_ROOT = Path(__file__).resolve().parents[2]
PROVIDER_ROOT = REPO_ROOT / "src" / "spec_dock" / "assets"
INSTALL_ROOT = PROVIDER_ROOT / "install_root"
SCAFFOLD_ROOT = PROVIDER_ROOT / "spec_dock"

CURRENT_INSTALL_ROOT_FILES = frozenset({
    ".agents/skills/spec-dock/SKILL.md",
    ".agents/skills/spec-dock-grill-with-docs/SKILL.md",
    ".agents/skills/spec-dock-grill-with-docs/agents/openai.yaml",
    ".agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py",
    ".github/workflows/ci.yml",
})
CURRENT_SKILL_SHA256 = {
    ".agents/skills/spec-dock/SKILL.md": "7d722020bc4666dd523ddb48d454d5af40367b1d712299e3d5c7dbc88319ae71",
    ".agents/skills/spec-dock-grill-with-docs/SKILL.md": "7182c1156bcf3635ffd3113cdcfb1d507c819b6aba6982673c0b10166f5da40c",
}

REMOVED_INSTALL_ROOT_PREFIXES = (
    ".agents/host-adapters/",
    ".codex/",
    ".github/agents/",
)
REMOVED_SKILL_NAMES = frozenset({
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
})
REMOVED_DOC_PATHS = frozenset({
    "docs/authoring/chatgpt-pack.md",
    "docs/authoring/decision-routing.md",
    "docs/reference_authoring_pack_backend.md",
    "docs/reference_hard_cutover.md",
    "docs/github.md",
    "docs/phase_design.md",
    "docs/phase_plan.md",
    "docs/phase_plan_epic.md",
    "docs/phase_plan_initiative.md",
    "docs/phase_plan_issue.md",
    "docs/phase_requirement.md",
    "docs/workflow-tree.md",
    "docs/workflow_adr.md",
    "docs/workflow_chatgpt_authoring_pack.md",
    "docs/workflow_clarification.md",
    "docs/workflow_epic.md",
    "docs/workflow_initiative.md",
    "docs/workflow_issue.md",
    "docs/workflow_spec_authoring.md",
})
REMOVED_TEMPLATE_PREFIXES = (
    "templates/discussions/",
    "templates/assurance/",
    "templates/issue-profiles/",
)


def _relative_files(root: Path) -> frozenset[str]:
    return frozenset(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix not in {".pyc", ".pyo"}
    )


def _filesystem_snapshot(root: Path) -> dict[str, tuple[object, ...]]:
    snapshot: dict[str, tuple[object, ...]] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        info = path.lstat()
        if path.is_symlink():
            snapshot[relative] = ("symlink", path.readlink())
        elif path.is_file():
            snapshot[relative] = ("file", info.st_mode & 0o777, path.read_bytes())
        elif path.is_dir():
            snapshot[relative] = ("directory", info.st_mode & 0o777)
    return snapshot


def test_s40b_provider_install_root_is_current_catalog_only() -> None:
    actual = _relative_files(INSTALL_ROOT)

    assert actual == CURRENT_INSTALL_ROOT_FILES
    assert all(not path.startswith(prefix) for path in actual for prefix in REMOVED_INSTALL_ROOT_PREFIXES)
    assert all(
        not (path.startswith(".agents/skills/") and Path(path).parts[2] in REMOVED_SKILL_NAMES) for path in actual
    )


def test_s40b_retained_skill_identity_matches_issue359_final_source() -> None:
    for relative_path, expected_sha256 in CURRENT_SKILL_SHA256.items():
        actual_sha256 = hashlib.sha256((INSTALL_ROOT / relative_path).read_bytes()).hexdigest()
        assert actual_sha256 == expected_sha256


def test_s35_cli_blocks_unknown_version_before_any_update_write(tmp_path: Path, capsys) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    assert main(["init", str(target)]) == 0
    version = target / "spec-dock" / "spec-dock.version"
    version.write_bytes(b"9.9.9\n")
    before = {
        path.relative_to(target): path.read_bytes()
        for path in target.rglob("*")
        if path.is_file() and not path.is_symlink()
    }

    assert main(["update", str(target)]) == 1
    assert "unknown-version" in capsys.readouterr().err
    after = {
        path.relative_to(target): path.read_bytes()
        for path in target.rglob("*")
        if path.is_file() and not path.is_symlink()
    }
    assert after == before


def test_s35_cli_rejects_dual_retry_markers_without_writes(tmp_path: Path, capsys) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    assert main(["init", str(target)]) == 0
    marker = target / "spec-dock" / ".distribution-retry.json"
    root_stat = target.stat()
    marker.write_text(
        json.dumps({
            "schema_version": 1,
            "operation": "update",
            "package_version": "0.2.3",
            "target_root": {"device": root_stat.st_dev, "inode": root_stat.st_ino},
            "last_completed_phase": "preflight-complete",
            "purpose": "distribution-rerun",
        }),
        encoding="utf-8",
    )
    uninstall_marker = target / "spec-dock" / ".uninstall-retry.json"
    uninstall_marker.write_text(
        json.dumps({"schema_version": 1, "managed_by": "spec-dock", "purpose": "uninstall-rerun"}),
        encoding="utf-8",
    )
    before = marker.read_bytes(), uninstall_marker.read_bytes()

    assert main(["update", str(target)]) == 1
    assert "dual-marker" in capsys.readouterr().err
    assert (marker.read_bytes(), uninstall_marker.read_bytes()) == before


def test_s40b_retained_ci_and_gitignore_are_deterministic_assets() -> None:
    ci = (INSTALL_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "python3 ./spec-dock/scripts/spec-dock sync" in ci
    assert "python3 ./spec-dock/scripts/spec-dock validate" in ci
    assert "spec-dock-chatgpt" not in ci
    assert (SCAFFOLD_ROOT / ".gitignore").is_file()
    assert "_DEFAULT_SPEC_DOCK_GITIGNORE" not in Path(cli.__file__).read_text(encoding="utf-8")


def test_s40b_provider_scaffold_excludes_removed_docs_and_templates() -> None:
    actual = _relative_files(SCAFFOLD_ROOT)
    assert REMOVED_DOC_PATHS.isdisjoint(actual)
    assert all(not path.startswith(prefix) for path in actual for prefix in REMOVED_TEMPLATE_PREFIXES)
    assert "templates/artifacts/pr-repair-batch.md" not in actual


def test_s40b_fresh_init_materializes_only_current_external_catalog(tmp_path: Path) -> None:
    assert main(["init", str(tmp_path)]) == 0

    installed = _relative_files(tmp_path)
    installed_external = frozenset(
        path for path in installed if path.startswith(".agents/") or path.startswith(".github/")
    )
    assert installed_external == CURRENT_INSTALL_ROOT_FILES
    assert (tmp_path / "spec-dock/.gitignore").read_bytes() == (SCAFFOLD_ROOT / ".gitignore").read_bytes()
    assert not (tmp_path / "spec-dock/scripts/spec-dock-chatgpt").exists()


def test_s45_fresh_preserves_unrelated_and_obsolete_looking_external_paths(tmp_path: Path) -> None:
    unrelated = tmp_path / "README.user.md"
    unrelated.write_bytes(b"user content\n")
    obsolete_skill = tmp_path / ".agents/skills/spec-dock-issue-planning/SKILL.md"
    obsolete_skill.parent.mkdir(parents=True)
    obsolete_skill.write_bytes(b"user-owned obsolete-looking skill\n")
    native_shim = tmp_path / ".codex/agents/legacy.md"
    native_shim.parent.mkdir(parents=True)
    native_shim.write_bytes(b"user-owned native shim\n")
    unknown_workflow = tmp_path / ".github/workflows/user.yml"
    unknown_workflow.parent.mkdir(parents=True)
    unknown_workflow.write_bytes(b"user-owned workflow\n")
    before = _filesystem_snapshot(tmp_path)

    assert main(["init", str(tmp_path)]) == 0

    after = _filesystem_snapshot(tmp_path)
    for path in (
        unrelated,
        obsolete_skill,
        native_shim,
        unknown_workflow,
    ):
        relative = path.relative_to(tmp_path).as_posix()
        assert after[relative] == before[relative]
    assert (tmp_path / "spec-dock/.workbench/README.md").is_file()
    assert (tmp_path / "spec-dock/.gitignore").read_bytes() == (SCAFFOLD_ROOT / ".gitignore").read_bytes()


@pytest.mark.parametrize("collision_kind", ("file", "symlink"))
def test_s45_fresh_preserves_legacy_named_workflow_without_ownership_proof(
    tmp_path: Path,
    collision_kind: str,
) -> None:
    workflow = tmp_path / ".github/workflows/spec-dock-close.yml"
    workflow.parent.mkdir(parents=True)
    if collision_kind == "file":
        workflow.write_bytes(b"user-owned legacy workflow\n")
    else:
        target = tmp_path / "user-owned-close-target.yml"
        target.write_bytes(b"user-owned workflow target\n")
        workflow.symlink_to(target)
    before = _filesystem_snapshot(tmp_path)

    assert main(["init", str(tmp_path)]) == 0

    after = _filesystem_snapshot(tmp_path)
    assert after[".github/workflows/spec-dock-close.yml"] == before[".github/workflows/spec-dock-close.yml"]


def test_s45_fresh_current_collision_blocks_before_any_write(tmp_path: Path, capsys) -> None:
    collision = tmp_path / ".github/workflows/ci.yml"
    collision.parent.mkdir(parents=True)
    collision.write_bytes(b"user-owned workflow\n")
    unrelated = tmp_path / "user.txt"
    unrelated.write_bytes(b"keep\n")
    before = _filesystem_snapshot(tmp_path)

    assert main(["init", str(tmp_path)]) == 1

    captured = capsys.readouterr()
    assert "unknown-current-collision" in captured.err
    assert _filesystem_snapshot(tmp_path) == before
    assert not (tmp_path / "spec-dock").exists()
    assert not (tmp_path / ".agents/skills/spec-dock/SKILL.md").exists()


def test_s45_fresh_rejects_existing_spec_dock_non_directory_without_writes(tmp_path: Path, capsys) -> None:
    workspace = tmp_path / "spec-dock"
    workspace.write_bytes(b"user-owned path\n")
    before = _filesystem_snapshot(tmp_path)

    assert main(["init", str(tmp_path)]) == 1

    captured = capsys.readouterr()
    assert "workspace-invalid" in captured.err
    assert _filesystem_snapshot(tmp_path) == before


def test_s45_fresh_adopts_identical_current_assets_without_rewriting_them(tmp_path: Path) -> None:
    for relative_path in CURRENT_INSTALL_ROOT_FILES:
        source = INSTALL_ROOT / relative_path
        destination = tmp_path / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())
        destination.chmod(source.stat().st_mode & 0o777)
    shortcut = tmp_path / "spec"
    shortcut.symlink_to("spec-dock/scripts/spec-dock")
    before = _filesystem_snapshot(tmp_path)

    assert main(["init", str(tmp_path)]) == 0

    after = _filesystem_snapshot(tmp_path)
    for relative_path in (*CURRENT_INSTALL_ROOT_FILES, "spec"):
        assert after[relative_path] == before[relative_path]


def test_s45_fresh_current_symlink_or_directory_collision_is_zero_write(tmp_path: Path) -> None:
    for collision_kind in ("symlink", "directory"):
        target = tmp_path / collision_kind
        target.mkdir()
        collision = target / ".github/workflows/ci.yml"
        collision.parent.mkdir(parents=True)
        if collision_kind == "symlink":
            collision.symlink_to(target / "user-owned.yml")
        else:
            collision.mkdir()
        before = _filesystem_snapshot(target)

        assert main(["init", str(target)]) == 1
        assert _filesystem_snapshot(target) == before


def test_s45_fresh_rerun_through_force_converges(tmp_path: Path) -> None:
    assert main(["init", str(tmp_path)]) == 0
    before = _filesystem_snapshot(tmp_path)

    assert main(["init", str(tmp_path), "--force"]) == 0

    assert _filesystem_snapshot(tmp_path) == before


def test_s50_update_restores_missing_current_asset_and_preserves_user_data(tmp_path: Path) -> None:
    assert main(["init", str(tmp_path)]) == 0
    stale_asset = tmp_path / ".agents/skills/spec-dock/SKILL.md"
    stale_asset.unlink()
    initiative = tmp_path / "spec-dock/initiatives/user-owned.md"
    initiative.parent.mkdir(parents=True, exist_ok=True)
    initiative.write_bytes(b"keep initiative\n")
    workbench_sentinel = tmp_path / "spec-dock/.workbench/sentinel.txt"
    workbench_sentinel.write_bytes(b"keep workbench\n")

    assert main(["update", str(tmp_path)]) == 0

    assert stale_asset.read_bytes() == (INSTALL_ROOT / ".agents/skills/spec-dock/SKILL.md").read_bytes()
    assert initiative.read_bytes() == b"keep initiative\n"
    assert workbench_sentinel.read_bytes() == b"keep workbench\n"


def test_s50_force_init_restores_missing_current_asset_and_preserves_user_data(tmp_path: Path) -> None:
    assert main(["init", str(tmp_path)]) == 0
    stale_asset = tmp_path / ".agents/skills/spec-dock/SKILL.md"
    stale_asset.unlink()
    initiative = tmp_path / "spec-dock/initiatives/user-owned.md"
    initiative.parent.mkdir(parents=True, exist_ok=True)
    initiative.write_bytes(b"keep initiative\n")
    workbench_sentinel = tmp_path / "spec-dock/.workbench/sentinel.txt"
    workbench_sentinel.write_bytes(b"keep workbench\n")

    assert main(["init", str(tmp_path), "--force"]) == 0

    assert stale_asset.read_bytes() == (INSTALL_ROOT / ".agents/skills/spec-dock/SKILL.md").read_bytes()
    assert initiative.read_bytes() == b"keep initiative\n"
    assert workbench_sentinel.read_bytes() == b"keep workbench\n"


def test_s50_update_unknown_scaffold_gitignore_is_preserve_and_blocked(tmp_path: Path, capsys) -> None:
    assert main(["init", str(tmp_path)]) == 0
    gitignore = tmp_path / "spec-dock/.gitignore"
    gitignore.write_bytes(b"user-owned ignore rules\n")
    before = _filesystem_snapshot(tmp_path)

    assert main(["update", str(tmp_path)]) == 1

    captured = capsys.readouterr().err
    assert "anchor-mismatch" in captured
    assert _filesystem_snapshot(tmp_path) == before
    assert not (tmp_path / "spec-dock/.distribution-retry.json").exists()


def test_s60_retry_rechecks_scaffold_gitignore_identity_before_write(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    original_write = cli._write_atomic_regular_file
    changed = False

    def mutate_gitignore_before_publish(path, payload, *, mode, **kwargs):
        nonlocal changed
        if not changed and Path(path).name == ".gitignore":
            changed = True
            Path(path).write_bytes(b"user-owned retry content\n")
        return original_write(path, payload, mode=mode, **kwargs)

    monkeypatch.setattr(cli, "_write_atomic_regular_file", mutate_gitignore_before_publish)

    assert main(["update", str(tmp_path)]) == 1
    captured = capsys.readouterr().err
    assert "distribution partial failure during scaffold-refresh" in captured
    assert "target=spec-dock" in captured
    assert (tmp_path / "spec-dock/.gitignore").read_bytes() == b"user-owned retry content\n"
    marker = tmp_path / "spec-dock/.distribution-retry.json"
    assert json.loads(marker.read_text(encoding="utf-8"))["last_completed_phase"] == "distribution-applied"

    monkeypatch.setattr(cli, "_write_atomic_regular_file", original_write)
    assert main(["update", str(tmp_path)]) == 1
    assert "distribution partial failure during preflight" in capsys.readouterr().err
    assert marker.exists()


def test_s60_marker_published_before_temporary_cleanup_failure_is_partial(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    original_unlink = Path.unlink
    failed = False

    def fail_marker_stage_cleanup(path, *args, **kwargs):
        nonlocal failed
        if not failed and path.name.startswith("..distribution-retry.json."):
            failed = True
            raise OSError("simulated temporary cleanup failure")
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", fail_marker_stage_cleanup)

    assert main(["init", str(tmp_path)]) == 1
    captured = capsys.readouterr().err
    assert "distribution partial failure during preflight" in captured
    assert "target=distribution" in captured
    marker = tmp_path / "spec-dock/.distribution-retry.json"
    assert marker.exists()
    assert not (tmp_path / "spec-dock/spec-dock.version").exists()

    monkeypatch.setattr(Path, "unlink", original_unlink)
    assert main(["init", str(tmp_path)]) == 0
    assert not marker.exists()


def test_s50_update_unknown_current_collision_is_zero_write(tmp_path: Path, capsys) -> None:
    assert main(["init", str(tmp_path)]) == 0
    collision = tmp_path / ".agents/skills/spec-dock/SKILL.md"
    collision.write_bytes(b"unknown current collision\n")
    before = _filesystem_snapshot(tmp_path)

    assert main(["update", str(tmp_path)]) == 1

    assert "unknown-current-collision" in capsys.readouterr().err
    assert _filesystem_snapshot(tmp_path) == before


def test_s50_force_init_unknown_current_collision_is_zero_write(tmp_path: Path, capsys) -> None:
    assert main(["init", str(tmp_path)]) == 0
    collision = tmp_path / ".agents/skills/spec-dock/SKILL.md"
    collision.write_bytes(b"unknown current collision\n")
    before = _filesystem_snapshot(tmp_path)

    assert main(["init", str(tmp_path), "--force"]) == 1

    assert "unknown-current-collision" in capsys.readouterr().err
    assert _filesystem_snapshot(tmp_path) == before


def test_s50_force_init_directory_only_current_collision_is_zero_write(tmp_path: Path) -> None:
    collision = tmp_path / ".github/workflows/ci.yml"
    collision.mkdir(parents=True)
    before = _filesystem_snapshot(tmp_path)

    assert main(["init", str(tmp_path), "--force"]) == 1

    assert _filesystem_snapshot(tmp_path) == before


@pytest.mark.parametrize("managed_name", ("docs", "templates", "scripts", "system"))
@pytest.mark.parametrize("collision_kind", ("symlink", "non_directory"))
def test_s50_update_scaffold_boundary_collision_is_zero_write(
    tmp_path: Path,
    managed_name: str,
    collision_kind: str,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    managed_dir = tmp_path / "spec-dock" / managed_name
    preserved = tmp_path / "preserved" / managed_name
    preserved.parent.mkdir(parents=True, exist_ok=True)
    managed_dir.rename(preserved)
    if collision_kind == "symlink":
        managed_dir.symlink_to(preserved, target_is_directory=True)
    else:
        managed_dir.write_text("user-owned replacement\n", encoding="utf-8")
    before = _filesystem_snapshot(tmp_path)

    assert main(["update", str(tmp_path)]) == 1
    capsys.readouterr()
    assert _filesystem_snapshot(tmp_path) == before
    assert not (tmp_path / "spec-dock/.distribution-retry.json").exists()


def test_s55_update_prunes_proven_historical_managed_file(tmp_path: Path) -> None:
    assert main(["init", str(tmp_path)]) == 0
    legacy = tmp_path / ".codex/config.toml"
    legacy.parent.mkdir(parents=True)
    legacy.write_bytes(b'project_doc_fallback_filenames = [".codex/AGENTS.md"]\n')
    legacy.chmod(0o644)

    assert main(["update", str(tmp_path)]) == 0

    assert not legacy.exists()


def test_s55_force_init_prunes_proven_historical_managed_file(tmp_path: Path) -> None:
    assert main(["init", str(tmp_path)]) == 0
    legacy = tmp_path / ".codex/config.toml"
    legacy.parent.mkdir(parents=True)
    legacy.write_bytes(b'project_doc_fallback_filenames = [".codex/AGENTS.md"]\n')
    legacy.chmod(0o644)

    assert main(["init", str(tmp_path), "--force"]) == 0

    assert not legacy.exists()


def test_s55_update_preserves_modified_historical_managed_file_and_blocks(
    tmp_path: Path,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    legacy = tmp_path / ".codex/config.toml"
    legacy.parent.mkdir(parents=True)
    legacy.write_bytes(b"user-owned configuration\n")
    before = _filesystem_snapshot(tmp_path)

    assert main(["update", str(tmp_path)]) == 1

    captured = capsys.readouterr()
    assert "obsolete-identity-unknown" in captured.err
    assert _filesystem_snapshot(tmp_path) == before


def test_s55_update_prunes_known_legacy_and_preserves_node_local_data(tmp_path: Path) -> None:
    assert main(["init", str(tmp_path)]) == 0
    legacy = tmp_path / ".codex/config.toml"
    legacy.parent.mkdir(parents=True)
    legacy.write_bytes(b'project_doc_fallback_filenames = [".codex/AGENTS.md"]\n')
    legacy.chmod(0o644)
    unknown = tmp_path / ".codex/user-owned.toml"
    unknown.write_bytes(b"user-owned\n")
    initiative = tmp_path / "spec-dock/initiatives/user-owned.md"
    initiative.parent.mkdir(parents=True, exist_ok=True)
    initiative.write_bytes(b"keep initiative\n")
    issue_workbench = tmp_path / "spec-dock/initiatives/user-owned/.workbench/README.md"
    issue_workbench.parent.mkdir(parents=True)
    issue_workbench.write_bytes(b"keep workbench\n")

    assert main(["update", str(tmp_path)]) == 0

    assert not legacy.exists()
    assert unknown.read_bytes() == b"user-owned\n"
    assert initiative.read_bytes() == b"keep initiative\n"
    assert issue_workbench.read_bytes() == b"keep workbench\n"


def test_s60_update_forward_retry_marker_is_removed_after_success(tmp_path: Path) -> None:
    assert main(["init", str(tmp_path)]) == 0

    assert main(["update", str(tmp_path)]) == 0

    assert not (tmp_path / "spec-dock/.distribution-retry.json").exists()
    assert (tmp_path / "spec-dock/spec-dock.version").read_text(encoding="utf-8") == "0.2.3\n"


def test_s60_atomic_regular_file_does_not_replace_racing_destination(
    tmp_path: Path,
    monkeypatch,
) -> None:
    destination = tmp_path / ".distribution-retry.json"
    original_link = cli.os.link

    def race_publish(source, target, *, follow_symlinks=False):
        Path(target).write_bytes(b"user replacement\n")
        return original_link(source, target, follow_symlinks=follow_symlinks)

    monkeypatch.setattr(cli.os, "link", race_publish)

    with pytest.raises(RuntimeError, match="managed file write failed"):
        cli._write_atomic_regular_file(destination, b"managed\n", mode=0o600)

    assert destination.read_bytes() == b"user replacement\n"


def test_s60_root_rebind_during_marker_publication(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    displaced = tmp_path.with_name(f"{tmp_path.name}-marker-displaced")
    original_link = cli.os.link
    switched = False

    def rebind_before_publish(source, target, *, follow_symlinks=False):
        nonlocal switched
        if not switched:
            switched = True
            tmp_path.rename(displaced)
            tmp_path.mkdir()
            (tmp_path / "replacement-sentinel.txt").write_text("keep\n", encoding="utf-8")
        return original_link(source, target, follow_symlinks=follow_symlinks)

    monkeypatch.setattr(cli.os, "link", rebind_before_publish)

    assert main(["update", str(tmp_path)]) == 1
    captured = capsys.readouterr().err
    assert "distribution target root identity changed" in captured
    assert (tmp_path / "replacement-sentinel.txt").read_text(encoding="utf-8") == "keep\n"
    assert not (tmp_path / "spec-dock").exists()
    assert (displaced / "spec-dock/.distribution-retry.json").exists()


def test_s60_root_rebind_during_scaffold_mutation(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    displaced = tmp_path.with_name(f"{tmp_path.name}-scaffold-displaced")
    original_sync = cli._sync_tree
    switched = False

    def rebind_before_sync(*args, **kwargs):
        nonlocal switched
        if not switched:
            switched = True
            tmp_path.rename(displaced)
            tmp_path.mkdir()
            (tmp_path / "replacement-sentinel.txt").write_text("keep\n", encoding="utf-8")
        return original_sync(*args, **kwargs)

    monkeypatch.setattr(cli, "_sync_tree", rebind_before_sync)

    assert main(["update", str(tmp_path)]) == 1
    captured = capsys.readouterr().err
    assert "distribution partial failure during scaffold-refresh" in captured
    assert (tmp_path / "replacement-sentinel.txt").read_text(encoding="utf-8") == "keep\n"
    assert not (tmp_path / "spec-dock").exists()
    marker = displaced / "spec-dock/.distribution-retry.json"
    assert json.loads(marker.read_text(encoding="utf-8"))["last_completed_phase"] == "distribution-applied"


def test_s60_root_rebind_during_version_publication(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    displaced = tmp_path.with_name(f"{tmp_path.name}-version-displaced")
    original_write = cli._write_atomic_regular_file
    switched = False

    def rebind_before_version_write(path, payload, *, mode, **kwargs):
        nonlocal switched
        if not switched and Path(path).name == "spec-dock.version":
            switched = True
            tmp_path.rename(displaced)
            tmp_path.mkdir()
            (tmp_path / "replacement-sentinel.txt").write_text("keep\n", encoding="utf-8")
        return original_write(path, payload, mode=mode, **kwargs)

    monkeypatch.setattr(cli, "_write_atomic_regular_file", rebind_before_version_write)

    assert main(["update", str(tmp_path)]) == 1
    captured = capsys.readouterr().err
    assert "distribution partial failure during version-write" in captured
    assert (tmp_path / "replacement-sentinel.txt").read_text(encoding="utf-8") == "keep\n"
    assert not (tmp_path / "spec-dock").exists()
    marker = displaced / "spec-dock/.distribution-retry.json"
    assert json.loads(marker.read_text(encoding="utf-8"))["last_completed_phase"] == "post-verified"

    monkeypatch.setattr(cli, "_write_atomic_regular_file", original_write)
    assert main(["update", str(displaced)]) == 0
    assert not marker.exists()


def test_s60_distribution_apply_fault_keeps_marker_and_old_version(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    version = tmp_path / "spec-dock/spec-dock.version"
    before_version = version.read_bytes()
    marker = tmp_path / "spec-dock/.distribution-retry.json"
    original_apply = cli.apply_distribution_plan

    def fail_distribution_apply(_plan):
        raise RuntimeError("credential=secret /private/outside/source.txt")

    monkeypatch.setattr(cli, "apply_distribution_plan", fail_distribution_apply)

    assert main(["update", str(tmp_path)]) == 1
    captured = capsys.readouterr().err
    assert "credential=secret" not in captured
    assert "/private/outside/source.txt" not in captured
    assert "distribution partial failure during distribution-apply" in captured
    assert "target=distribution" in captured
    assert "last_completed_phase=preflight-complete" in captured
    assert "retry=spec-dock update ." in captured
    payload = json.loads(marker.read_text(encoding="utf-8"))
    assert payload["last_completed_phase"] == "preflight-complete"
    assert version.read_bytes() == before_version

    monkeypatch.setattr(cli, "apply_distribution_plan", original_apply)
    assert main(["update", str(tmp_path)]) == 0
    assert not marker.exists()


def test_s60_fresh_init_forward_retry_reuses_marker_and_converges(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    original_apply = cli.apply_distribution_plan
    failed = False

    def fail_once(plan):
        nonlocal failed
        if not failed:
            failed = True
            raise RuntimeError("credential=secret /private/outside/source.txt")
        return original_apply(plan)

    monkeypatch.setattr(cli, "apply_distribution_plan", fail_once)

    assert main(["init", str(tmp_path)]) == 1
    captured = capsys.readouterr().err
    assert "credential=secret" not in captured
    assert "/private/outside/source.txt" not in captured
    assert "distribution partial failure during distribution-apply" in captured
    assert "target=distribution" in captured
    assert "last_completed_phase=preflight-complete" in captured
    assert "retry=spec-dock init ." in captured
    marker = tmp_path / "spec-dock/.distribution-retry.json"
    assert marker.exists()
    assert not (tmp_path / "spec-dock/spec-dock.version").exists()

    assert main(["init", str(tmp_path)]) == 0
    assert not marker.exists()
    assert (tmp_path / "spec-dock/spec-dock.version").read_text(encoding="utf-8") == "0.2.3\n"


def test_s60_scaffold_failure_keeps_marker_and_old_version_and_sanitizes_diagnostic(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    version = tmp_path / "spec-dock/spec-dock.version"
    before_version = version.read_bytes()
    original = cli._install_spec_dock

    def fail_after_scaffold(*args, **kwargs):
        original(*args, **kwargs)
        raise RuntimeError("credential=secret /private/outside/source.txt")

    monkeypatch.setattr(cli, "_install_spec_dock", fail_after_scaffold)

    assert main(["update", str(tmp_path)]) == 1

    captured = capsys.readouterr().err
    assert "credential=secret" not in captured
    assert "/private/outside/source.txt" not in captured
    assert "distribution partial failure during scaffold-refresh" in captured
    marker = tmp_path / "spec-dock/.distribution-retry.json"
    payload = json.loads(marker.read_text(encoding="utf-8"))
    assert payload["operation"] == "update"
    assert payload["last_completed_phase"] == "distribution-applied"
    assert version.read_bytes() == before_version

    monkeypatch.setattr(cli, "_install_spec_dock", original)
    assert main(["update", str(tmp_path)]) == 0
    assert not marker.exists()


def test_s60_root_rebind_preserves_replacement_and_original_retry_marker(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    original = cli._install_spec_dock
    displaced = tmp_path.with_name(f"{tmp_path.name}-displaced")

    def rebind_before_scaffold(*args, **kwargs):
        tmp_path.rename(displaced)
        tmp_path.mkdir()
        (tmp_path / "replacement-sentinel.txt").write_text("keep\n", encoding="utf-8")
        return original(*args, **kwargs)

    monkeypatch.setattr(cli, "_install_spec_dock", rebind_before_scaffold)

    assert main(["update", str(tmp_path)]) == 1
    captured = capsys.readouterr().err
    assert "distribution partial failure during scaffold-refresh" in captured
    assert "replacement-sentinel.txt" not in captured

    marker = displaced / "spec-dock/.distribution-retry.json"
    payload = json.loads(marker.read_text(encoding="utf-8"))
    displaced_stat = displaced.stat()
    assert payload["target_root"] == {
        "device": displaced_stat.st_dev,
        "inode": displaced_stat.st_ino,
    }
    assert (tmp_path / "replacement-sentinel.txt").read_text(encoding="utf-8") == "keep\n"
    assert not (tmp_path / "spec-dock").exists()

    monkeypatch.setattr(cli, "_install_spec_dock", original)
    replacement_before_retry = _filesystem_snapshot(tmp_path)
    assert main(["update", str(tmp_path)]) == 1
    assert _filesystem_snapshot(tmp_path) == replacement_before_retry
    assert marker.exists()


def test_s65_uninstall_root_rebind_before_marker_write_is_zero_write(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    displaced = tmp_path.with_name(f"{tmp_path.name}-uninstall-displaced")
    original_create = cli._create_uninstall_retry_marker
    switched = False

    def rebind_before_marker(*args, **kwargs):
        nonlocal switched
        if not switched:
            switched = True
            tmp_path.rename(displaced)
            tmp_path.mkdir()
            (tmp_path / "replacement-sentinel.txt").write_text("keep\n", encoding="utf-8")
        return original_create(*args, **kwargs)

    monkeypatch.setattr(cli, "_create_uninstall_retry_marker", rebind_before_marker)

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "partial_failure"
    assert (tmp_path / "replacement-sentinel.txt").read_text(encoding="utf-8") == "keep\n"
    assert not (tmp_path / "spec-dock/.uninstall-retry.json").exists()
    assert not (displaced / "spec-dock/.uninstall-retry.json").exists()


def test_s70_uninstall_cleanup_rebind_keeps_replacement_untouched(tmp_path: Path, monkeypatch) -> None:
    managed_file = tmp_path / ".agents/skills/spec-dock/SKILL.md"
    managed_file.parent.mkdir(parents=True)
    managed_file.write_text("managed\n", encoding="utf-8")
    managed_file.unlink()
    actions = (
        cli._UninstallAction(
            rel_path=".agents/skills/spec-dock/SKILL.md",
            category="agent_skill",
            status="removed",
            reason="test cleanup race",
        ),
    )
    displaced = tmp_path.with_name(f"{tmp_path.name}-agents-displaced")
    replacement_sentinel = "preserve replacement\n"
    original_rmdir = cli.os.rmdir
    switched = False

    def rebind_before_rmdir(name, *, dir_fd=None):
        nonlocal switched
        if not switched:
            switched = True
            (tmp_path / ".agents").rename(displaced / ".agents")
            replacement = tmp_path / ".agents"
            replacement.mkdir(parents=True)
            (replacement / "replacement-sentinel.txt").write_text(replacement_sentinel, encoding="utf-8")
        return original_rmdir(name, dir_fd=dir_fd)

    displaced.mkdir()
    monkeypatch.setattr(cli.os, "rmdir", rebind_before_rmdir)

    result = cli._cleanup_empty_uninstall_dirs(
        tmp_path,
        actions,
        expected_root_identity=cli._distribution_root_identity(tmp_path),
    )

    assert result == ()
    assert (tmp_path / ".agents/replacement-sentinel.txt").read_text(encoding="utf-8") == replacement_sentinel
    assert not (tmp_path / ".agents/skills/spec-dock").exists()


def test_s60_post_verify_failure_keeps_marker_until_forward_retry(tmp_path: Path, monkeypatch, capsys) -> None:
    assert main(["init", str(tmp_path)]) == 0
    version = tmp_path / "spec-dock/spec-dock.version"
    before_version = version.read_bytes()
    original = cli._write_spec_dock_version

    def fail_version_write(*args, **kwargs):
        raise RuntimeError("source bytes secret /private/outside/source.txt")

    monkeypatch.setattr(cli, "_write_spec_dock_version", fail_version_write)

    assert main(["update", str(tmp_path)]) == 1

    captured = capsys.readouterr().err
    assert "source bytes secret" not in captured
    assert "/private/outside/source.txt" not in captured
    assert "distribution partial failure during version-write" in captured
    marker = tmp_path / "spec-dock/.distribution-retry.json"
    payload = json.loads(marker.read_text(encoding="utf-8"))
    assert payload["last_completed_phase"] == "post-verified"
    assert version.read_bytes() == before_version

    monkeypatch.setattr(cli, "_write_spec_dock_version", original)
    assert main(["update", str(tmp_path)]) == 0
    assert not marker.exists()


def test_s65_uninstall_invalid_version_is_zero_write(tmp_path: Path, capsys) -> None:
    assert main(["init", str(tmp_path)]) == 0
    version = tmp_path / "spec-dock/spec-dock.version"
    version.write_text("not-a-version\n", encoding="ascii")
    before = _filesystem_snapshot(tmp_path)

    assert main(["uninstall", str(tmp_path)]) == 2

    captured = capsys.readouterr().err
    assert "spec-dock.version" in captured
    assert _filesystem_snapshot(tmp_path) == before


def test_s65_uninstall_distribution_or_dual_marker_is_zero_write(tmp_path: Path, capsys) -> None:
    assert main(["init", str(tmp_path)]) == 0
    root_stat = tmp_path.stat()
    distribution_marker = tmp_path / "spec-dock/.distribution-retry.json"
    distribution_marker.write_text(
        json.dumps(
            {
                "last_completed_phase": "distribution-applied",
                "operation": "update",
                "package_version": "0.2.3",
                "purpose": "distribution-rerun",
                "schema_version": 1,
                "target_root": {"device": root_stat.st_dev, "inode": root_stat.st_ino},
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    before_distribution = _filesystem_snapshot(tmp_path)

    assert main(["uninstall", str(tmp_path)]) == 2
    assert "recover distribution" in capsys.readouterr().err
    assert _filesystem_snapshot(tmp_path) == before_distribution

    uninstall_marker = tmp_path / "spec-dock/.uninstall-retry.json"
    uninstall_marker.write_text(
        json.dumps(
            {"managed_by": "spec-dock", "purpose": "uninstall-rerun", "schema_version": 1},
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    before_dual = _filesystem_snapshot(tmp_path)

    assert main(["uninstall", str(tmp_path)]) == 2
    assert "dual-marker" in capsys.readouterr().err
    assert _filesystem_snapshot(tmp_path) == before_dual


def test_s65_uninstall_legacy_retry_marker_without_version_is_admissible_and_read_only(tmp_path: Path) -> None:
    specdock = tmp_path / "spec-dock"
    specdock.mkdir()
    marker = specdock / ".uninstall-retry.json"
    marker.write_text(
        json.dumps(
            {"managed_by": "spec-dock", "purpose": "uninstall-rerun", "schema_version": 1},
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    before = _filesystem_snapshot(tmp_path)

    assert main(["uninstall", str(tmp_path)]) == 0
    assert _filesystem_snapshot(tmp_path) == before


def test_s65_uninstall_dry_run_preserves_modified_current_skill(tmp_path: Path, capsys) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    skill = tmp_path / ".agents/skills/spec-dock/SKILL.md"
    skill.write_text("user-modified\n", encoding="utf-8")

    assert main(["uninstall", str(tmp_path), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    action = next(item for item in payload["actions"] if item["path"] == ".agents/skills/spec-dock/SKILL.md")
    assert action["status"] == "preserved"
    assert "unknown-current-collision" in action["reason"]
    assert skill.read_text(encoding="utf-8") == "user-modified\n"


def test_s65_uninstall_dry_run_surfaces_known_obsolete_identity(tmp_path: Path, capsys) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    obsolete = tmp_path / ".codex/config.toml"
    obsolete.parent.mkdir(parents=True, exist_ok=True)
    obsolete.write_bytes(b'project_doc_fallback_filenames = [".codex/AGENTS.md"]\n')
    obsolete.chmod(0o644)

    assert main(["uninstall", str(tmp_path), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    action = next(item for item in payload["actions"] if item["path"] == ".codex/config.toml")
    assert action["status"] == "would_remove"
    assert action["category"] == "obsolete_managed"
    assert "known obsolete" in action["reason"]
    assert obsolete.exists()


def test_s60_retry_marker_phase_allowlist_rejects_unknown_phase_without_writes(tmp_path: Path, capsys) -> None:
    assert main(["init", str(tmp_path)]) == 0
    root_stat = tmp_path.stat()
    marker = tmp_path / "spec-dock/.distribution-retry.json"
    marker.write_text(
        json.dumps(
            {
                "last_completed_phase": "unknown-phase",
                "operation": "update",
                "package_version": "0.2.3",
                "purpose": "distribution-rerun",
                "schema_version": 1,
                "target_root": {"device": root_stat.st_dev, "inode": root_stat.st_ino},
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    before = _filesystem_snapshot(tmp_path)

    assert main(["update", str(tmp_path)]) == 1
    assert "marker-invalid" in capsys.readouterr().err
    assert _filesystem_snapshot(tmp_path) == before


def test_s70_uninstall_apply_blocks_modified_current_before_marker_or_removal(
    tmp_path: Path,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    skill = tmp_path / ".agents/skills/spec-dock/SKILL.md"
    skill.write_text("user-modified\n", encoding="utf-8")
    before = _filesystem_snapshot(tmp_path)

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "blocked"
    assert any(
        action["path"] == ".agents/skills/spec-dock/SKILL.md" and action["status"] == "preserved"
        for action in payload["actions"]
    )
    assert not (tmp_path / "spec-dock/.uninstall-retry.json").exists()
    assert _filesystem_snapshot(tmp_path) == before


def test_s70_uninstall_apply_rejects_rewritten_target_after_plan(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    managed = tmp_path / ".agents/skills/spec-dock/SKILL.md"
    original_write_marker = cli._write_uninstall_retry_marker

    def rewrite_after_marker(*args, **kwargs):
        original_write_marker(*args, **kwargs)
        managed.write_text("replacement after uninstall plan\n", encoding="utf-8")

    monkeypatch.setattr(cli, "_write_uninstall_retry_marker", rewrite_after_marker)

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "partial_failure"
    assert managed.read_text(encoding="utf-8") == "replacement after uninstall plan\n"
    assert (tmp_path / "spec-dock/.uninstall-retry.json").is_file()


def test_s70_uninstall_apply_does_not_recreate_vanished_specdock_parent(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    original_write_marker = cli._write_uninstall_retry_marker

    def remove_parent_before_marker(*args, **kwargs):
        shutil.rmtree(tmp_path / "spec-dock")
        return original_write_marker(*args, **kwargs)

    monkeypatch.setattr(cli, "_write_uninstall_retry_marker", remove_parent_before_marker)

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "partial_failure"
    assert not (tmp_path / "spec-dock").exists()


def test_s50_update_rejects_managed_directory_replacement_after_preflight(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    original_sync_tree = cli._sync_tree
    switched = False

    def replace_before_sync(src: Path, dest: Path, **kwargs):
        nonlocal switched
        if not switched:
            switched = True
            managed = tmp_path / "spec-dock/docs"
            shutil.rmtree(managed)
            managed.mkdir(parents=True)
            (managed / "replacement-sentinel.md").write_text("keep\n", encoding="utf-8")
        return original_sync_tree(src, dest, **kwargs)

    monkeypatch.setattr(cli, "_sync_tree", replace_before_sync)

    assert main(["update", str(tmp_path)]) == 1
    capsys.readouterr()
    assert (tmp_path / "spec-dock/docs/replacement-sentinel.md").read_text(encoding="utf-8") == "keep\n"


def test_s70_uninstall_apply_blocks_mixed_known_obsolete_and_unknown_before_mutation(
    tmp_path: Path,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    obsolete = tmp_path / ".codex/config.toml"
    obsolete.parent.mkdir(parents=True, exist_ok=True)
    obsolete.write_bytes(b'project_doc_fallback_filenames = [".codex/AGENTS.md"]\n')
    obsolete.chmod(0o644)
    unknown = tmp_path / ".codex/user-owned.toml"
    unknown.write_text("user-owned\n", encoding="utf-8")
    before = _filesystem_snapshot(tmp_path)

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "blocked"
    assert any(
        action["path"] == ".codex/config.toml" and action["status"] == "would_remove" for action in payload["actions"]
    )
    assert any(
        action["path"] == ".codex/user-owned.toml" and action["status"] == "preserved" for action in payload["actions"]
    )
    assert not (tmp_path / "spec-dock/.uninstall-retry.json").exists()
    assert _filesystem_snapshot(tmp_path) == before


def test_s70_uninstall_marker_is_removed_last_after_success(tmp_path: Path, capsys) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "completed"
    marker_action = next(action for action in payload["actions"] if action["path"] == "spec-dock/.uninstall-retry.json")
    assert marker_action["status"] == "removed"
    assert not (tmp_path / "spec-dock/.uninstall-retry.json").exists()


def test_s70_uninstall_marker_survives_partial_failure_and_is_removed_on_retry(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    original_remove = cli._remove_uninstall_path

    def fail_one(
        target_root: Path,
        action,
        *,
        expected_root_identity: cli.DistributionRootIdentity | None = None,
    ):
        if action.rel_path == ".agents/skills/spec-dock/SKILL.md":
            raise OSError("injected uninstall unlink failure")
        return original_remove(target_root, action, expected_root_identity=expected_root_identity)

    monkeypatch.setattr(cli, "_remove_uninstall_path", fail_one)
    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 1
    first_payload = json.loads(capsys.readouterr().out)
    marker = tmp_path / "spec-dock/.uninstall-retry.json"
    assert first_payload["status"] == "partial_failure"
    assert marker.is_file()

    monkeypatch.setattr(cli, "_remove_uninstall_path", original_remove)
    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 0
    second_payload = json.loads(capsys.readouterr().out)
    assert second_payload["status"] == "completed"
    assert (
        next(action for action in second_payload["actions"] if action["path"] == "spec-dock/.uninstall-retry.json")[
            "status"
        ]
        == "removed"
    )
    assert not marker.exists()


def test_s70_uninstall_keep_and_remove_specs_preserve_boundary(tmp_path: Path, capsys) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    initiative = tmp_path / "spec-dock/initiatives/user-owned.md"
    initiative.write_text("keep me\n", encoding="utf-8")

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs"]) == 0
    capsys.readouterr()
    assert initiative.read_text(encoding="utf-8") == "keep me\n"
    assert not (tmp_path / "spec-dock/.uninstall-retry.json").exists()

    # A fresh consumer verifies that only explicit remove-specs permits
    # recursive history removal.
    remove_target = tmp_path / "remove-specs"
    remove_target.mkdir()
    assert main(["init", str(remove_target)]) == 0
    remove_initiative = remove_target / "spec-dock/initiatives/user-owned.md"
    remove_initiative.write_text("remove me\n", encoding="utf-8")
    assert main(["uninstall", str(remove_target), "--apply", "--remove-specs"]) == 0
    capsys.readouterr()
    assert not remove_initiative.exists()
    assert not (remove_target / "spec-dock/.uninstall-retry.json").exists()


def test_s70_uninstall_does_not_cleanup_empty_preserved_or_unknown_directories(
    tmp_path: Path,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    empty_initiative = tmp_path / "spec-dock/initiatives/empty-preserved"
    empty_initiative.mkdir(parents=True)
    empty_workbench = tmp_path / "spec-dock/.workbench/empty-payload"
    empty_workbench.mkdir(parents=True)
    empty_unknown = tmp_path / ".codex/user-owned-empty"
    empty_unknown.mkdir(parents=True)

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    removed_empty_paths = {action["path"] for action in payload["actions"] if action["status"] == "empty_dir_removed"}

    assert empty_initiative.is_dir()
    assert empty_workbench.is_dir()
    assert empty_unknown.is_dir()
    assert "spec-dock/initiatives/empty-preserved" not in removed_empty_paths
    assert "spec-dock/.workbench/empty-payload" not in removed_empty_paths
    assert ".codex/user-owned-empty" not in removed_empty_paths
