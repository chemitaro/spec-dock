from __future__ import annotations

import hashlib
import json
from pathlib import Path

from spec_dock import cli
from tests.cli_runtime.harness import main

REPO_ROOT = Path(__file__).resolve().parents[2]
PROVIDER_ROOT = REPO_ROOT / "src" / "spec_dock" / "assets"
INSTALL_ROOT = PROVIDER_ROOT / "install_root"
SCAFFOLD_ROOT = PROVIDER_ROOT / "spec_dock"

CURRENT_INSTALL_ROOT_FILES = frozenset(
    {
        ".agents/skills/spec-dock/SKILL.md",
        ".agents/skills/spec-dock-grill-with-docs/SKILL.md",
        ".agents/skills/spec-dock-grill-with-docs/agents/openai.yaml",
        ".agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py",
        ".github/workflows/ci.yml",
    }
)
CURRENT_SKILL_SHA256 = {
    ".agents/skills/spec-dock/SKILL.md": "7d722020bc4666dd523ddb48d454d5af40367b1d712299e3d5c7dbc88319ae71",
    ".agents/skills/spec-dock-grill-with-docs/SKILL.md": "7182c1156bcf3635ffd3113cdcfb1d507c819b6aba6982673c0b10166f5da40c",
}

REMOVED_INSTALL_ROOT_PREFIXES = (
    ".agents/host-adapters/",
    ".codex/",
    ".github/agents/",
)
REMOVED_SKILL_NAMES = frozenset(
    {
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
    }
)
REMOVED_DOC_PATHS = frozenset(
    {
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
    }
)
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
        not (path.startswith(".agents/skills/") and Path(path).parts[2] in REMOVED_SKILL_NAMES)
        for path in actual
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
        json.dumps(
            {
                "schema_version": 1,
                "operation": "update",
                "package_version": "0.2.3",
                "target_root": {"device": root_stat.st_dev, "inode": root_stat.st_ino},
                "last_completed_phase": "preflight-complete",
                "purpose": "distribution-rerun",
            }
        ),
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
        path
        for path in installed
        if path.startswith(".agents/") or path.startswith(".github/")
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
