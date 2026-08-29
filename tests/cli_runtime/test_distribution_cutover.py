from __future__ import annotations

import ast
from contextlib import contextmanager
import hashlib
import inspect
import json
import os
from pathlib import Path
import shlex
import shutil
import threading
import time

import pytest

from spec_dock import cli
import spec_dock.managed_distribution as managed_distribution
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
CURRENT_RETAINED_SKILL_FILES = (
    ".agents/skills/spec-dock/SKILL.md",
    ".agents/skills/spec-dock-grill-with-docs/SKILL.md",
)

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


def _executable_relative_files(root: Path) -> frozenset[str]:
    return frozenset(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and not path.is_symlink() and path.stat().st_mode & 0o111
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


def test_s40b_retained_skill_identity_matches_current_provider_and_dogfood() -> None:
    for relative_path in CURRENT_RETAINED_SKILL_FILES:
        provider = INSTALL_ROOT / relative_path
        dogfood = REPO_ROOT / relative_path
        assert provider.is_file() and not provider.is_symlink()
        assert dogfood.is_file() and not dogfood.is_symlink()
        assert provider.read_bytes() == dogfood.read_bytes()
        assert provider.stat().st_mode & 0o777 == dogfood.stat().st_mode & 0o777


def test_s40b_legacy_bootstrap_and_skill_apply_paths_are_retired() -> None:
    source = inspect.getsource(cli)

    assert "_migrate_bootstrap_only_config_if_stale" not in source
    assert "def _install_skill(" not in source
    assert "def _apply_managed_skill_install_plan(" not in source


def test_s60_distribution_operations_share_an_exclusive_root_lock(tmp_path: Path) -> None:
    first_entered = threading.Event()
    release_first = threading.Event()
    second_entered = threading.Event()
    errors: list[BaseException] = []

    def hold_first_operation() -> None:
        try:
            with cli._exclusive_distribution_operation(tmp_path):
                first_entered.set()
                assert release_first.wait(timeout=2)
        except BaseException as exc:  # pragma: no cover - surfaced below
            errors.append(exc)

    def enter_second_operation() -> None:
        try:
            assert first_entered.wait(timeout=2)
            with cli._exclusive_distribution_operation(tmp_path):
                second_entered.set()
        except BaseException as exc:  # pragma: no cover - surfaced below
            errors.append(exc)

    first = threading.Thread(target=hold_first_operation)
    second = threading.Thread(target=enter_second_operation)
    first.start()
    assert first_entered.wait(timeout=2)
    second.start()
    time.sleep(0.1)
    assert not second_entered.is_set()
    release_first.set()
    first.join(timeout=2)
    second.join(timeout=2)

    assert not errors
    assert second_entered.is_set()


def test_s60_locked_root_identity_blocks_rebind_before_fresh_admission(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys,
) -> None:
    displaced = tmp_path.with_name(f"{tmp_path.name}-locked-root")
    original_admit = cli._admit_distribution_cli
    rebound = False
    admission_calls = 0

    def rebind_before_admission(target_root: Path, *, operation):
        nonlocal admission_calls, rebound
        admission_calls += 1
        if admission_calls == 2:
            rebound = True
            target_root.rename(displaced)
            target_root.mkdir()
        return original_admit(target_root, operation=operation)

    monkeypatch.setattr(cli, "_admit_distribution_cli", rebind_before_admission)

    assert main(["init", str(tmp_path)]) == 1
    captured = capsys.readouterr().err

    assert rebound
    assert "distribution target root identity changed" in captured
    assert list(tmp_path.iterdir()) == []
    assert list(displaced.iterdir()) == []


def test_s60_root_bound_operations_serialize_process_cwd_across_roots(tmp_path: Path) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first_root.mkdir()
    second_root.mkdir()
    first_entered = threading.Event()
    release_first = threading.Event()
    second_entered = threading.Event()
    errors: list[BaseException] = []

    def hold_first_root() -> None:
        try:
            with cli._bound_distribution_root(first_root):
                first_entered.set()
                assert release_first.wait(timeout=2)
                assert Path.cwd() == first_root
        except BaseException as exc:  # pragma: no cover - surfaced below
            errors.append(exc)

    def enter_second_root() -> None:
        try:
            assert first_entered.wait(timeout=2)
            with cli._bound_distribution_root(second_root):
                second_entered.set()
                assert Path.cwd() == second_root
        except BaseException as exc:  # pragma: no cover - surfaced below
            errors.append(exc)

    first = threading.Thread(target=hold_first_root)
    second = threading.Thread(target=enter_second_root)
    first.start()
    assert first_entered.wait(timeout=2)
    second.start()
    time.sleep(0.1)
    assert not second_entered.is_set()
    release_first.set()
    first.join(timeout=2)
    second.join(timeout=2)

    assert not errors
    assert second_entered.is_set()


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


def test_i369_legacy_fresh_marker_retry_uses_canonical_init_guidance(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    specdock = target / "spec-dock"
    specdock.mkdir()
    root_stat = target.stat()
    marker = specdock / ".distribution-retry.json"
    marker.write_text(
        json.dumps({
            "schema_version": 1,
            "operation": "fresh",
            "package_version": "0.2.3",
            "target_root": {"device": root_stat.st_dev, "inode": root_stat.st_ino},
            "last_completed_phase": "preflight-complete",
            "purpose": "distribution-rerun",
        }),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        cli,
        "execute_fresh_distribution",
        lambda *_args, **_kwargs: managed_distribution.DistributionProcessResult(
            status="recovery_required",
            intent="fresh",
            actions=(),
            reason="injected",
        ),
    )

    assert main(["update", str(target)]) == 1
    captured = capsys.readouterr().err
    assert "retry=spec-dock init ." in captured
    assert "retry=spec-dock update ." not in captured
    assert marker.exists()


@pytest.mark.parametrize("workspace_state", ("absent", "empty", "preserved"))
@pytest.mark.parametrize("operation", (("init",), ("init", "--force"), ("update",)))
def test_i369_fresh_entrypoint_matrix_provisions_all_workspace_states(
    tmp_path: Path,
    workspace_state: str,
    operation: tuple[str, ...],
    capsys,
) -> None:
    history = tmp_path / "spec-dock/initiatives/preserved/requirement.md"
    if workspace_state != "absent":
        (tmp_path / "spec-dock").mkdir()
    if workspace_state == "preserved":
        history.parent.mkdir(parents=True)
        history.write_text("preserved history\n", encoding="utf-8")

    assert main([*operation, str(tmp_path)]) == 0
    capsys.readouterr()
    assert (tmp_path / "spec-dock/spec-dock.version").is_file()
    if workspace_state == "preserved":
        assert history.read_text(encoding="utf-8") == "preserved history\n"


def test_s40b_retained_ci_and_gitignore_are_deterministic_assets() -> None:
    ci = (INSTALL_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "python3 ./spec-dock/scripts/spec-dock sync" in ci
    assert "python3 ./spec-dock/scripts/spec-dock validate" in ci
    assert "spec-dock-chatgpt" not in ci
    assert (SCAFFOLD_ROOT / ".gitignore").is_file()
    assert "_DEFAULT_SPEC_DOCK_GITIGNORE" not in Path(cli.__file__).read_text(encoding="utf-8")


def test_s40b_only_runtime_wrapper_is_executable_across_current_surfaces(tmp_path: Path) -> None:
    assert _executable_relative_files(PROVIDER_ROOT) == frozenset({"spec_dock/scripts/spec-dock"})
    dogfood_paths = {
        *(REPO_ROOT / path for path in CURRENT_INSTALL_ROOT_FILES),
        *(
            path
            for root in ("docs", "templates", "scripts", "system")
            for path in (REPO_ROOT / "spec-dock" / root).rglob("*")
            if path.is_file()
        ),
    }
    dogfood_executables = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in dogfood_paths
        if not path.is_symlink() and path.stat().st_mode & 0o111
    }
    assert dogfood_executables == {"spec-dock/scripts/spec-dock"}

    assert main(["init", str(tmp_path)]) == 0
    assert _executable_relative_files(tmp_path) == frozenset({"spec-dock/scripts/spec-dock"})


def test_s40b_provider_scaffold_excludes_removed_docs_and_templates() -> None:
    actual = _relative_files(SCAFFOLD_ROOT)
    assert REMOVED_DOC_PATHS.isdisjoint(actual)
    assert all(not path.startswith(prefix) for path in actual for prefix in REMOVED_TEMPLATE_PREFIXES)
    assert "templates/artifacts/pr-repair-batch.md" not in actual
    current_docs = tuple((SCAFFOLD_ROOT / "docs").rglob("*.md"))
    for removed_path in REMOVED_DOC_PATHS:
        removed_name = Path(removed_path).name
        retired_routes = (f"`{removed_name}`", f"]({removed_name})", f"spec-dock/{removed_path}")
        assert all(
            all(route not in path.read_text(encoding="utf-8") for route in retired_routes) for path in current_docs
        ), f"Current documentation still routes to retired path: {removed_path}"


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


def test_s45_fresh_preserves_same_bytes_wrong_mode_current_asset(tmp_path: Path, capsys) -> None:
    relative_path = ".agents/skills/spec-dock/SKILL.md"
    source = INSTALL_ROOT / relative_path
    destination = tmp_path / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(source.read_bytes())
    source_mode = source.stat().st_mode & 0o777
    destination.chmod(0o600 if source_mode != 0o600 else 0o644)
    before = _filesystem_snapshot(tmp_path)

    assert main(["init", str(tmp_path)]) == 1

    captured = capsys.readouterr()
    assert "current-mode-mismatch" in captured.err
    assert _filesystem_snapshot(tmp_path) == before


def test_s45_fresh_preserves_same_bytes_wrong_mode_hard_link_current_asset(tmp_path: Path, capsys) -> None:
    relative_path = ".github/workflows/ci.yml"
    source = INSTALL_ROOT / relative_path
    destination = tmp_path / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(source.read_bytes())
    source_mode = source.stat().st_mode & 0o777
    destination.chmod(0o600 if source_mode != 0o600 else 0o644)
    alias = tmp_path / "user-owned-ci-alias.yml"
    os.link(destination, alias)
    before = _filesystem_snapshot(tmp_path)

    assert main(["init", str(tmp_path)]) == 1

    captured = capsys.readouterr()
    assert "current-mode-mismatch" in captured.err
    assert _filesystem_snapshot(tmp_path) == before


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


def test_s45_scaffold_copy_rejects_file_symlink_race_without_external_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    external = tmp_path / "external.txt"
    external.write_text("external sentinel\n", encoding="utf-8")
    original = managed_distribution._apply_distribution_action
    attacked = False

    def inject_symlink(plan, target_root, action, *args, **kwargs):
        nonlocal attacked
        if not attacked and action.action == "create":
            collision = target_root / action.path
            collision.parent.mkdir(parents=True, exist_ok=True)
            collision.symlink_to(external)
            attacked = True
        return original(plan, target_root, action, *args, **kwargs)

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", inject_symlink)
    consumer = tmp_path / "consumer"
    consumer.mkdir()

    assert main(["init", str(consumer)]) == 1
    assert attacked is True
    assert external.read_text(encoding="utf-8") == "external sentinel\n"


def test_s45_fresh_rerun_through_force_converges(tmp_path: Path) -> None:
    assert main(["init", str(tmp_path)]) == 0
    before = _filesystem_snapshot(tmp_path)

    assert main(["init", str(tmp_path), "--force"]) == 0

    assert _filesystem_snapshot(tmp_path) == before


def test_s50_update_and_force_restore_missing_non_anchor_scaffold_directories(tmp_path: Path) -> None:
    sentinels = {
        "docs": Path("README.md"),
        "templates": Path("initiative/requirement.md"),
        "system": Path("active-none/issue/report.md"),
    }
    for operation in ("update", "init-force"):
        target = tmp_path / operation
        target.mkdir()
        assert main(["init", str(target)]) == 0
        for managed_name in sentinels:
            shutil.rmtree(target / "spec-dock" / managed_name)

        command = ["update", str(target)] if operation == "update" else ["init", str(target), "--force"]
        assert main(command) == 0

        for managed_name, sentinel in sentinels.items():
            restored = target / "spec-dock" / managed_name / sentinel
            source = SCAFFOLD_ROOT / managed_name / sentinel
            assert restored.read_bytes() == source.read_bytes()


def test_s35_update_and_force_block_missing_runtime_anchor_without_writes(tmp_path: Path, capsys) -> None:
    for operation in ("update", "init-force"):
        target = tmp_path / operation
        target.mkdir()
        assert main(["init", str(target)]) == 0
        shutil.rmtree(target / "spec-dock" / "scripts")
        before = _filesystem_snapshot(target)

        command = ["update", str(target)] if operation == "update" else ["init", str(target), "--force"]
        assert main(command) == 1

        assert "anchor-mismatch" in capsys.readouterr().err
        assert _filesystem_snapshot(target) == before


def test_s45_force_init_on_empty_target_uses_fresh_distribution(tmp_path: Path) -> None:
    assert main(["init", str(tmp_path), "--force"]) == 0

    assert (tmp_path / "spec-dock/.gitignore").is_file()
    assert (tmp_path / "spec-dock/spec-dock.version").is_file()


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


def test_s50_update_preflights_all_scaffold_sources_before_distribution_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()

    assets_copy = tmp_path / "provider-assets"
    shutil.copytree(PROVIDER_ROOT, assets_copy)
    shutil.rmtree(assets_copy / "spec_dock" / "docs")

    @contextmanager
    def patched_assets_dir():
        yield assets_copy

    monkeypatch.setattr(cli, "_assets_dir", patched_assets_dir)
    before = _filesystem_snapshot(tmp_path)

    assert main(["update", str(tmp_path)]) == 1

    captured = capsys.readouterr().err
    assert "Invalid asset directory: spec_dock/docs" in captured
    assert _filesystem_snapshot(tmp_path) == before
    assert not (tmp_path / "spec-dock/.distribution-retry.json").exists()


def test_s50_update_blocks_unreadable_managed_scaffold_source_before_distribution_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    before = _filesystem_snapshot(tmp_path)
    original_read = managed_distribution._source_asset_bytes

    def fail_managed_docs_read(path: Path):
        if path == SCAFFOLD_ROOT / "docs" / "README.md":
            raise PermissionError("simulated unreadable managed scaffold source")
        return original_read(path)

    monkeypatch.setattr(managed_distribution, "_source_asset_bytes", fail_managed_docs_read)

    assert main(["update", str(tmp_path)]) == 1
    captured = capsys.readouterr().err
    monkeypatch.setattr(managed_distribution, "_source_asset_bytes", original_read)

    assert "unable to read scaffold asset: docs/README.md" in captured
    assert _filesystem_snapshot(tmp_path) == before
    assert not (tmp_path / "spec-dock/.distribution-retry.json").exists()


def test_s50_update_preflights_required_nested_runtime_before_distribution_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()

    assets_copy = tmp_path / "provider-assets"
    shutil.copytree(PROVIDER_ROOT, assets_copy)
    (assets_copy / "spec_dock" / "scripts" / "spec-dock").unlink()

    @contextmanager
    def patched_assets_dir():
        yield assets_copy

    monkeypatch.setattr(cli, "_assets_dir", patched_assets_dir)
    before = _filesystem_snapshot(tmp_path)

    assert main(["update", str(tmp_path)]) == 1

    captured = capsys.readouterr().err
    assert "Missing asset file: spec_dock/scripts/spec-dock" in captured
    assert _filesystem_snapshot(tmp_path) == before
    assert not (tmp_path / "spec-dock/.distribution-retry.json").exists()


def test_s50_update_preflights_required_nested_runtime_mode_before_distribution_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()

    assets_copy = tmp_path / "provider-assets"
    shutil.copytree(PROVIDER_ROOT, assets_copy)
    runtime_script = assets_copy / "spec_dock" / "scripts" / "spec-dock"
    runtime_script.chmod(0o644)

    @contextmanager
    def patched_assets_dir():
        yield assets_copy

    monkeypatch.setattr(cli, "_assets_dir", patched_assets_dir)
    before = _filesystem_snapshot(tmp_path)

    assert main(["update", str(tmp_path)]) == 1

    captured = capsys.readouterr().err
    assert "Invalid asset file: spec_dock/scripts/spec-dock" in captured
    assert _filesystem_snapshot(tmp_path) == before
    assert not (tmp_path / "spec-dock/.distribution-retry.json").exists()


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
    (tmp_path / "spec-dock/.gitignore").chmod(0o600)
    original_apply = managed_distribution._apply_distribution_action
    changed = False

    def mutate_gitignore_before_publish(plan, target_root, action, *args, **kwargs):
        nonlocal changed
        if not changed and action.path == "spec-dock/.gitignore":
            changed = True
            (target_root / action.path).write_bytes(b"user-owned retry content\n")
        return original_apply(plan, target_root, action, *args, **kwargs)

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", mutate_gitignore_before_publish)

    assert main(["update", str(tmp_path)]) == 1
    captured = capsys.readouterr().err
    assert "distribution partial failure" in captured
    assert "managed target identity changed for 'spec-dock/.gitignore'" in captured
    assert (tmp_path / "spec-dock/.gitignore").read_bytes() == b"user-owned retry content\n"
    journal = tmp_path / "spec-dock/.distribution-journal.json"
    assert journal.is_file()

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", original_apply)
    assert main(["update", str(tmp_path)]) == 1
    assert "journal-precondition-mismatch" in capsys.readouterr().err
    assert journal.exists()


def test_s60_marker_published_before_temporary_cleanup_failure_is_partial(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    original_rename = managed_distribution._rename_distribution_no_replace
    failed = False

    def fail_marker_publish_once(source_parent_fd, source_name, destination_parent_fd, destination_name):
        nonlocal failed
        if not failed:
            failed = True
            raise OSError("simulated marker publish failure")
        return original_rename(source_parent_fd, source_name, destination_parent_fd, destination_name)

    monkeypatch.setattr(managed_distribution, "_rename_distribution_no_replace", fail_marker_publish_once)

    assert main(["init", str(tmp_path)]) == 1
    captured = capsys.readouterr().err
    assert "distribution partial failure during fresh provisioning" in captured
    assert "target=spec-dock/.distribution-journal.json" in captured
    marker = tmp_path / "spec-dock/.distribution-retry.json"
    journal = tmp_path / "spec-dock/.distribution-journal.json"
    assert not marker.exists()
    assert not journal.exists()
    assert not list((tmp_path / "spec-dock").glob(".distribution-retry-*.stage"))
    assert not (tmp_path / "spec-dock/spec-dock.version").exists()

    monkeypatch.setattr(managed_distribution, "_rename_distribution_no_replace", original_rename)
    assert main(["init", str(tmp_path)]) == 0
    assert not marker.exists()
    assert not journal.exists()


def test_s60_fresh_marker_publication_recovers_after_write_and_cleanup_faults(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys,
) -> None:
    original_write = cli.os.write
    write_failed = False

    def fail_marker_write(fd, view):
        nonlocal write_failed
        if not write_failed:
            write_failed = True
            raise OSError("simulated marker write failure")
        return original_write(fd, view)

    monkeypatch.setattr(cli.os, "write", fail_marker_write)

    assert main(["init", str(tmp_path)]) == 1
    captured = capsys.readouterr().err
    assert "distribution partial failure during fresh provisioning" in captured
    assert "target=spec-dock/.distribution-journal.json" in captured
    marker = tmp_path / "spec-dock/.distribution-retry.json"
    journal = tmp_path / "spec-dock/.distribution-journal.json"
    assert not marker.exists()
    assert not journal.exists()
    assert not (tmp_path / "spec-dock/spec-dock.version").exists()
    assert not list((tmp_path / "spec-dock").glob(".distribution-retry-*.stage"))

    assert main(["init", str(tmp_path)]) == 0
    assert not marker.exists()
    assert not journal.exists()
    assert not list((tmp_path / "spec-dock").glob(".distribution-retry-*.stage"))


def test_s60_fresh_pre_marker_rollback_preserves_replacement_workspace(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys,
) -> None:
    displaced = tmp_path.with_name(f"{tmp_path.name}-created-workspace")
    swapped = False

    def fail_fresh_distribution(*args, **kwargs):
        nonlocal swapped
        if not swapped:
            swapped = True
            (tmp_path / "spec-dock").rename(displaced)
            (tmp_path / "spec-dock").mkdir()
        raise RuntimeError("simulated pre-journal failure")

    monkeypatch.setattr(cli, "execute_fresh_distribution", fail_fresh_distribution)

    assert main(["init", str(tmp_path)]) == 1
    assert "simulated pre-journal failure" in capsys.readouterr().err

    assert swapped
    assert (tmp_path / "spec-dock").is_dir()
    assert list((tmp_path / "spec-dock").iterdir()) == []
    assert displaced.is_dir()


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


def test_s50_update_scaffold_exact_file_directory_collision_is_zero_write(
    tmp_path: Path,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    collision = tmp_path / "spec-dock/docs/README.md"
    collision.unlink()
    collision.mkdir()
    sentinel = collision / "user-sentinel.txt"
    sentinel.write_bytes(b"preserve this directory\n")
    before = _filesystem_snapshot(tmp_path)

    assert main(["update", str(tmp_path)]) == 1

    capsys.readouterr()
    assert sentinel.read_bytes() == b"preserve this directory\n"
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


@pytest.mark.parametrize("operation", ("update", "init-force"))
@pytest.mark.parametrize(
    ("relative_path", "target_kind"),
    [
        *[(f"spec-dock/current-{scope}", "symlink") for scope in ("initiative", "epic", "issue")],
        *[(f"spec-dock/current-{scope}.path", "regular") for scope in ("initiative", "epic", "issue")],
    ],
)
def test_s55_unproven_legacy_root_entrypoint_is_preserved_and_blocks_zero_write(
    tmp_path: Path,
    capsys,
    operation: str,
    relative_path: str,
    target_kind: str,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    target = tmp_path / relative_path
    if target_kind == "symlink":
        target.symlink_to("user-owned-target")
    else:
        target.write_bytes(b"user-owned entrypoint\n")
    before = _filesystem_snapshot(tmp_path)

    command = ["update", str(tmp_path)] if operation == "update" else ["init", str(tmp_path), "--force"]
    assert main(command) == 1

    assert "obsolete-identity-unknown" in capsys.readouterr().err
    assert _filesystem_snapshot(tmp_path) == before
    assert not (tmp_path / "spec-dock/.distribution-retry.json").exists()


@pytest.mark.parametrize(
    "relative_path",
    [
        *[f"spec-dock/current-{scope}" for scope in ("initiative", "epic", "issue")],
        *[f"spec-dock/current-{scope}.path" for scope in ("initiative", "epic", "issue")],
    ],
)
def test_s55_legacy_root_entrypoint_directory_collision_blocks_zero_write(
    tmp_path: Path,
    capsys,
    relative_path: str,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    target = tmp_path / relative_path
    target.mkdir()
    (target / "user-owned.txt").write_text("keep\n", encoding="utf-8")
    before = _filesystem_snapshot(tmp_path)

    assert main(["update", str(tmp_path)]) == 1

    assert "exact-path-directory" in capsys.readouterr().err
    assert _filesystem_snapshot(tmp_path) == before
    assert not (tmp_path / "spec-dock/.distribution-retry.json").exists()


def test_s55_uninstall_preserves_unproven_legacy_root_entrypoint_and_blocks(
    tmp_path: Path,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    target = tmp_path / "spec-dock/current-initiative"
    target.symlink_to("user-owned-target")
    before = _filesystem_snapshot(tmp_path)

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 1

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "blocked"
    assert any(
        action["path"] == "spec-dock/current-initiative" and "obsolete-identity-unknown" in action["reason"]
        for action in payload["actions"]
    )
    assert _filesystem_snapshot(tmp_path) == before
    assert not (tmp_path / "spec-dock/.uninstall-retry.json").exists()


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


def test_s55_update_rejects_manifest_overlap_with_preserved_specs_before_write(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    initiative = tmp_path / "spec-dock/initiatives/user-owned.md"
    initiative.write_bytes(b"keep initiative\n")

    assets_copy = tmp_path / "provider-assets"
    shutil.copytree(PROVIDER_ROOT, assets_copy)
    manifest_path = assets_copy / "managed_distribution.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["obsolete_exact_files"].append({
        "path": "spec-dock/initiatives/user-owned.md",
        "surface": "protected-path-test",
        "identities": [
            {
                "path": "spec-dock/initiatives/user-owned.md",
                "kind": "regular",
                "sha256": hashlib.sha256(initiative.read_bytes()).hexdigest(),
                "mode": 0o644,
                "source": {"kind": "test-fixture", "ref": "issue-360"},
            }
        ],
        "on_unknown": "preserve-and-block",
    })
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    @contextmanager
    def patched_assets_dir():
        yield assets_copy

    monkeypatch.setattr(cli, "_assets_dir", patched_assets_dir)
    before = _filesystem_snapshot(tmp_path)

    assert main(["update", str(tmp_path)]) == 1
    assert "protected workspace surface" in capsys.readouterr().err
    assert _filesystem_snapshot(tmp_path) == before
    assert not (tmp_path / "spec-dock/.distribution-retry.json").exists()


def test_s60_update_forward_retry_marker_is_removed_after_success(tmp_path: Path) -> None:
    assert main(["init", str(tmp_path)]) == 0

    assert main(["update", str(tmp_path)]) == 0

    assert not (tmp_path / "spec-dock/.distribution-retry.json").exists()
    assert (tmp_path / "spec-dock/spec-dock.version").read_text(encoding="utf-8") == "0.2.3\n"


@pytest.mark.parametrize("operation", ("fresh",))
def test_s60_marker_removal_failure_reports_marker_finalization_target(
    tmp_path: Path,
    monkeypatch,
    capsys,
    operation: str,
) -> None:
    if operation != "fresh":
        assert main(["init", str(tmp_path)]) == 0

    original_remove = managed_distribution.OperationJournalStore.remove_legacy_marker

    def fail_marker_removal(self, marker):
        raise OSError("simulated marker removal failure")

    monkeypatch.setattr(managed_distribution.OperationJournalStore, "remove_legacy_marker", fail_marker_removal)
    command = {
        "fresh": ["init", str(tmp_path)],
        "update": ["update", str(tmp_path)],
        "init-force": ["init", str(tmp_path), "--force"],
    }[operation]

    assert main(command) == 1

    captured = capsys.readouterr().err
    assert "distribution partial failure during fresh provisioning" in captured
    assert "target=spec-dock/.distribution-journal.json" in captured
    marker = tmp_path / "spec-dock/.distribution-retry.json"
    journal = tmp_path / "spec-dock/.distribution-journal.json"
    assert marker.exists()
    assert journal.exists()

    monkeypatch.setattr(managed_distribution.OperationJournalStore, "remove_legacy_marker", original_remove)
    assert main(command) == 0
    assert not marker.exists()
    assert not journal.exists()


@pytest.mark.parametrize("operation", ("update", "init-force"))
def test_i368_journal_removal_failure_is_forward_recoverable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys,
    operation: str,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    (tmp_path / "spec-dock/docs/README.md").unlink()
    original_remove = managed_distribution.OperationJournalStore.remove_completed

    def fail_journal_removal(*_args, **_kwargs):
        raise managed_distribution.DistributionApplyError("journal finalization failed")

    monkeypatch.setattr(managed_distribution.OperationJournalStore, "remove_completed", fail_journal_removal)
    command = ["update", str(tmp_path)] if operation == "update" else ["init", str(tmp_path), "--force"]

    assert main(command) == 1
    assert "journal finalization failed" in capsys.readouterr().err
    journal = tmp_path / "spec-dock/.distribution-journal.json"
    assert json.loads(journal.read_text(encoding="utf-8"))["status"] == "completed"

    monkeypatch.setattr(managed_distribution.OperationJournalStore, "remove_completed", original_remove)
    assert main(command) == 0
    assert not journal.exists()


def test_s60_distribution_retry_command_runs_for_special_explicit_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys,
) -> None:
    parent = tmp_path.parent
    target = parent / "-distribution target"
    target.mkdir()
    monkeypatch.chdir(parent)
    assert main(["init", str(target)]) == 0
    capsys.readouterr()
    (target / "spec-dock/docs/README.md").unlink()

    original_apply = managed_distribution.apply_distribution_plan

    def fail_once(_plan, **_kwargs):
        monkeypatch.setattr(managed_distribution, "apply_distribution_plan", original_apply)
        raise managed_distribution.DistributionApplyError("simulated distribution failure")

    monkeypatch.setattr(managed_distribution, "apply_distribution_plan", fail_once)
    assert main(["update", str(target)]) == 1
    captured = capsys.readouterr().err
    retry = "retry=spec-dock update -- '-distribution target'"
    assert retry in captured

    assert main(shlex.split(retry.removeprefix("retry="))[1:]) == 0
    assert not (target / "spec-dock/.distribution-journal.json").exists()


def test_s60_root_rebind_during_marker_publication(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    (tmp_path / "spec-dock/docs/README.md").unlink()
    displaced = tmp_path.with_name(f"{tmp_path.name}-marker-displaced")
    original_rename = managed_distribution._rename_distribution_no_replace
    switched = False

    def rebind_before_publish(source_parent_fd, source_name, destination_parent_fd, destination_name):
        nonlocal switched
        if not switched:
            switched = True
            tmp_path.rename(displaced)
            tmp_path.mkdir()
            (tmp_path / "replacement-sentinel.txt").write_text("keep\n", encoding="utf-8")
        return original_rename(source_parent_fd, source_name, destination_parent_fd, destination_name)

    monkeypatch.setattr(managed_distribution, "_rename_distribution_no_replace", rebind_before_publish)

    assert main(["update", str(tmp_path)]) == 1
    captured = capsys.readouterr().err
    assert "journal-root-mismatch" in captured
    assert (tmp_path / "replacement-sentinel.txt").read_text(encoding="utf-8") == "keep\n"
    assert not (tmp_path / "spec-dock").exists()
    assert not (displaced / "spec-dock/.distribution-journal.json").exists()
    assert (displaced / "spec-dock/.distribution-retry.json").exists()


def test_s60_root_rebind_during_scaffold_mutation(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    (tmp_path / "spec-dock/docs/README.md").unlink()
    displaced = tmp_path.with_name(f"{tmp_path.name}-scaffold-displaced")
    original_apply = managed_distribution._apply_distribution_action
    switched = False

    def rebind_before_scaffold_action(plan, target_root, action, *args, **kwargs):
        nonlocal switched
        if not switched and action.path.startswith("spec-dock/docs/"):
            switched = True
            tmp_path.rename(displaced)
            tmp_path.mkdir()
            (tmp_path / "replacement-sentinel.txt").write_text("keep\n", encoding="utf-8")
        return original_apply(plan, target_root, action, *args, **kwargs)

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", rebind_before_scaffold_action)

    assert main(["update", str(tmp_path)]) == 1
    captured = capsys.readouterr().err
    assert "distribution partial failure during reconciliation" in captured
    assert (tmp_path / "replacement-sentinel.txt").read_text(encoding="utf-8") == "keep\n"
    assert not (tmp_path / "spec-dock").exists()
    journal = displaced / "spec-dock/.distribution-journal.json"
    assert json.loads(journal.read_text(encoding="utf-8"))["status"] == "executing"


def test_i368_noop_update_does_not_publish_version_outside_the_plan(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    original_apply = managed_distribution._apply_distribution_action
    applied: list[str] = []

    def record_apply(plan, target_root, action, *args, **kwargs):
        applied.append(action.path)
        return original_apply(plan, target_root, action, *args, **kwargs)

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", record_apply)

    assert main(["update", str(tmp_path)]) == 0
    capsys.readouterr()
    assert "spec-dock/spec-dock.version" not in applied
    assert not (tmp_path / "spec-dock/.distribution-journal.json").exists()


def test_s60_distribution_apply_fault_keeps_marker_and_old_version(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    (tmp_path / "spec-dock/docs/README.md").unlink()
    version = tmp_path / "spec-dock/spec-dock.version"
    before_version = version.read_bytes()
    journal = tmp_path / "spec-dock/.distribution-journal.json"
    original_apply = managed_distribution.apply_distribution_plan

    def fail_distribution_apply(_plan, **_kwargs):
        raise managed_distribution.DistributionApplyError("credential=secret /private/outside/source.txt")

    monkeypatch.setattr(managed_distribution, "apply_distribution_plan", fail_distribution_apply)

    assert main(["update", str(tmp_path)]) == 1
    captured = capsys.readouterr().err
    assert "credential=secret" not in captured
    assert "/private/outside/source.txt" not in captured
    assert "distribution partial failure during reconciliation" in captured
    assert "target=spec-dock/.distribution-journal.json" in captured
    assert "retry=spec-dock update ." in captured
    payload = json.loads(journal.read_text(encoding="utf-8"))
    assert payload["status"] == "executing"
    assert version.read_bytes() == before_version

    monkeypatch.setattr(managed_distribution, "apply_distribution_plan", original_apply)
    assert main(["update", str(tmp_path)]) == 0
    assert not journal.exists()


def test_s60_current_materialize_fault_reports_applied_and_pending_paths(tmp_path: Path, monkeypatch, capsys) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    missing = tmp_path / ".github/workflows/ci.yml"
    missing.unlink()
    journal = tmp_path / "spec-dock/.distribution-journal.json"
    original_apply_action = managed_distribution._apply_distribution_action

    def fail_current(plan, target_root, action, *args, **kwargs):
        if action.path == ".github/workflows/ci.yml":
            raise OSError("injected Current copy fault")
        return original_apply_action(plan, target_root, action, *args, **kwargs)

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", fail_current)

    assert main(["update", str(tmp_path)]) == 1
    captured = capsys.readouterr().err
    assert "during reconciliation" in captured
    assert "pending_paths=[" in captured
    assert '".github/workflows/ci.yml"' in captured
    assert json.loads(journal.read_text(encoding="utf-8"))["status"] == "executing"

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", original_apply_action)
    assert main(["update", str(tmp_path)]) == 0
    assert missing.is_file()
    assert not journal.exists()


def test_s60_obsolete_prune_fault_reports_applied_and_pending_paths(tmp_path: Path, monkeypatch, capsys) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    legacy = tmp_path / ".codex/config.toml"
    legacy.parent.mkdir(parents=True)
    legacy.write_bytes(b'project_doc_fallback_filenames = [".codex/AGENTS.md"]\n')
    legacy.chmod(0o644)
    preserved = tmp_path / "spec-dock/initiatives/user-owned.md"
    preserved.parent.mkdir(parents=True, exist_ok=True)
    preserved.write_bytes(b"preserve\n")
    journal = tmp_path / "spec-dock/.distribution-journal.json"
    original_apply_action = managed_distribution._apply_distribution_action

    def fail_prune(plan, target_root, action, *args, **kwargs):
        if action.path == ".codex/config.toml":
            raise OSError("injected obsolete prune fault")
        return original_apply_action(plan, target_root, action, *args, **kwargs)

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", fail_prune)

    assert main(["update", str(tmp_path)]) == 1
    captured = capsys.readouterr().err
    assert "during reconciliation" in captured
    assert "applied_paths=[" in captured
    assert "pending_paths=[" in captured
    assert '".codex/config.toml"' in captured
    assert preserved.read_bytes() == b"preserve\n"
    assert json.loads(journal.read_text(encoding="utf-8"))["status"] == "executing"

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", original_apply_action)
    assert main(["update", str(tmp_path)]) == 0
    assert not legacy.exists()
    assert preserved.read_bytes() == b"preserve\n"
    assert not journal.exists()


def test_s60_fresh_init_forward_retry_reuses_marker_and_converges(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    original_apply = managed_distribution.apply_distribution_plan
    failed = False

    def fail_once(plan, **kwargs):
        nonlocal failed
        if not failed:
            failed = True
            raise RuntimeError("credential=secret /private/outside/source.txt")
        return original_apply(plan, **kwargs)

    monkeypatch.setattr(managed_distribution, "apply_distribution_plan", fail_once)

    assert main(["init", str(tmp_path)]) == 1
    captured = capsys.readouterr().err
    assert "credential=secret" not in captured
    assert "/private/outside/source.txt" not in captured
    assert "distribution partial failure during fresh provisioning" in captured
    assert "target=spec-dock/.distribution-journal.json" in captured
    assert "retry=spec-dock init ." in captured
    marker = tmp_path / "spec-dock/.distribution-retry.json"
    journal = tmp_path / "spec-dock/.distribution-journal.json"
    assert marker.exists()
    assert journal.exists()
    assert not (tmp_path / "spec-dock/spec-dock.version").exists()

    assert main(["init", str(tmp_path)]) == 0
    assert not marker.exists()
    assert not journal.exists()
    assert (tmp_path / "spec-dock/spec-dock.version").read_text(encoding="utf-8") == "0.2.3\n"


def test_s60_fresh_retry_blocks_workbench_symlink_seed(tmp_path: Path, monkeypatch, capsys) -> None:
    original_apply = managed_distribution.apply_distribution_plan
    failed = False

    def fail_once(plan, **kwargs):
        nonlocal failed
        if not failed:
            failed = True
            raise RuntimeError("simulated distribution failure")
        return original_apply(plan, **kwargs)

    monkeypatch.setattr(managed_distribution, "apply_distribution_plan", fail_once)
    assert main(["init", str(tmp_path)]) == 1

    external = tmp_path / "external-workbench"
    external.mkdir()
    external_readme = external / "README.md"
    external_readme.write_bytes(b"external-owned\n")
    workbench = tmp_path / "spec-dock/.workbench"
    workbench.symlink_to(external, target_is_directory=True)

    assert main(["init", str(tmp_path)]) == 1
    captured = capsys.readouterr().err
    assert "distribution preflight blocked" in captured
    assert "symlink-container" in captured
    assert "target=spec-dock/.distribution-journal.json" in captured
    assert external_readme.read_bytes() == b"external-owned\n"
    assert (tmp_path / "spec-dock/.distribution-retry.json").exists()

    workbench.unlink()
    assert main(["init", str(tmp_path)]) == 0
    assert not (tmp_path / "spec-dock/.distribution-retry.json").exists()


def test_s60_fresh_retry_adopts_provider_identical_workbench_seed(tmp_path: Path, monkeypatch, capsys) -> None:
    original_apply = managed_distribution.apply_distribution_plan
    failed = False

    def fail_once(plan, **kwargs):
        nonlocal failed
        if not failed:
            failed = True
            raise RuntimeError("simulated distribution failure")
        return original_apply(plan, **kwargs)

    monkeypatch.setattr(managed_distribution, "apply_distribution_plan", fail_once)
    assert main(["init", str(tmp_path)]) == 1
    capsys.readouterr()

    source = SCAFFOLD_ROOT / "templates/root/.workbench/README.md"
    target = tmp_path / "spec-dock/.workbench/README.md"
    target.parent.mkdir(parents=True)
    shutil.copy2(source, target)

    assert main(["init", str(tmp_path)]) == 0
    assert not (tmp_path / "spec-dock/.distribution-retry.json").exists()
    assert target.read_bytes() == source.read_bytes()


def test_s60_fresh_retry_adopts_provider_identical_hard_link_workbench_seed(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    original_apply = managed_distribution.apply_distribution_plan
    failed = False

    def fail_once(plan, **kwargs):
        nonlocal failed
        if not failed:
            failed = True
            raise RuntimeError("simulated distribution failure")
        return original_apply(plan, **kwargs)

    monkeypatch.setattr(managed_distribution, "apply_distribution_plan", fail_once)
    assert main(["init", str(tmp_path)]) == 1
    capsys.readouterr()

    source = SCAFFOLD_ROOT / "templates/root/.workbench/README.md"
    source_copy = tmp_path / "provider-workbench-seed"
    shutil.copy2(source, source_copy)
    target = tmp_path / "spec-dock/.workbench/README.md"
    target.parent.mkdir(parents=True)
    os.link(source_copy, target)
    before_inode = target.stat().st_ino
    assert target.stat().st_nlink == 2

    assert main(["init", str(tmp_path)]) == 0
    assert not (tmp_path / "spec-dock/.distribution-retry.json").exists()
    assert target.stat().st_ino == before_inode
    assert target.stat().st_nlink == 2
    assert target.read_bytes() == source.read_bytes()


def test_s60_fresh_retry_blocks_modified_scaffold_collision_before_refresh(tmp_path: Path, monkeypatch, capsys) -> None:
    original_apply = managed_distribution.apply_distribution_plan
    failed = False

    def fail_once(plan, **kwargs):
        nonlocal failed
        if not failed:
            failed = True
            raise RuntimeError("simulated distribution failure")
        return original_apply(plan, **kwargs)

    monkeypatch.setattr(managed_distribution, "apply_distribution_plan", fail_once)
    assert main(["init", str(tmp_path)]) == 1
    capsys.readouterr()

    modified = tmp_path / "spec-dock/docs/README.md"
    modified.parent.mkdir(parents=True)
    modified.write_bytes(b"user-owned scaffold collision\n")

    assert main(["init", str(tmp_path)]) == 1
    captured = capsys.readouterr().err
    assert "distribution preflight blocked" in captured
    assert "unknown-current-collision" in captured
    assert modified.read_bytes() == b"user-owned scaffold collision\n"
    assert (tmp_path / "spec-dock/.distribution-retry.json").exists()


def test_s50_update_preserves_symlinked_root_workbench(tmp_path: Path) -> None:
    assert main(["init", str(tmp_path)]) == 0
    external = tmp_path / "external-workbench"
    external.mkdir()
    external_readme = external / "README.md"
    external_readme.write_bytes(b"external-owned\n")
    workbench = tmp_path / "spec-dock/.workbench"
    shutil.rmtree(workbench)
    workbench.symlink_to(external, target_is_directory=True)

    assert main(["update", str(tmp_path)]) == 0
    assert workbench.is_symlink()
    assert external_readme.read_bytes() == b"external-owned\n"


def test_s60_fresh_root_workspace_creation_stays_on_held_root(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    original_bound_root = cli._bound_distribution_root
    displaced = tmp_path.with_name(f"{tmp_path.name}-fresh-displaced")
    switched = False

    @contextmanager
    def rebind_after_open(target_root: Path, expected=None):
        nonlocal switched
        with original_bound_root(target_root, expected) as bound:
            if not switched:
                switched = True
                tmp_path.rename(displaced)
                tmp_path.mkdir()
                (tmp_path / "replacement-sentinel.txt").write_text("keep\n", encoding="utf-8")
            yield bound

    monkeypatch.setattr(cli, "_bound_distribution_root", rebind_after_open)

    assert main(["init", str(tmp_path)]) == 1
    captured = capsys.readouterr().err
    assert "distribution target root identity changed" in captured
    assert (tmp_path / "replacement-sentinel.txt").read_text(encoding="utf-8") == "keep\n"
    assert not (tmp_path / "spec-dock").exists()
    assert (displaced / "spec-dock").is_dir()


def test_i368_recognized_update_stays_on_held_root_after_visible_rebind(
    tmp_path: Path,
    monkeypatch,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    (tmp_path / "spec-dock/active/context-pack.md").unlink()
    expected_root = cli._distribution_root_identity(tmp_path)
    original_bound_root = cli._bound_distribution_root
    displaced = tmp_path.with_name(f"{tmp_path.name}-recognized-displaced")
    switched = False

    @contextmanager
    def rebind_after_open(target_root: Path, expected=None):
        nonlocal switched
        with original_bound_root(target_root, expected) as bound:
            if not switched:
                switched = True
                tmp_path.rename(displaced)
                tmp_path.mkdir()
                (tmp_path / "replacement-sentinel.txt").write_text("keep\n", encoding="utf-8")
            yield bound

    monkeypatch.setattr(cli, "_bound_distribution_root", rebind_after_open)

    with pytest.raises(RuntimeError, match="journal-root-mismatch"):
        cli._install_recognized_distribution_unlocked(
            tmp_path,
            operation="update",
            expected_root_identity=expected_root,
        )

    assert (tmp_path / "replacement-sentinel.txt").read_text(encoding="utf-8") == "keep\n"
    assert not (tmp_path / "spec-dock").exists()
    assert not (displaced / "spec-dock/active/context-pack.md").exists()


def test_s60_scaffold_failure_keeps_marker_and_old_version_and_sanitizes_diagnostic(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    version = tmp_path / "spec-dock/spec-dock.version"
    before_version = version.read_bytes()
    (tmp_path / "spec-dock/active/context-pack.md").unlink()
    original = managed_distribution._apply_distribution_action

    def fail_after_generated_state(plan, target_root, action, *args, **kwargs):
        if action.path == "spec-dock/active/context-pack.md":
            raise RuntimeError("credential=secret /private/outside/source.txt")
        return original(plan, target_root, action, *args, **kwargs)

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", fail_after_generated_state)

    assert main(["update", str(tmp_path)]) == 1

    captured = capsys.readouterr().err
    assert "credential=secret" not in captured
    assert "/private/outside/source.txt" not in captured
    assert "distribution partial failure during reconciliation" in captured
    journal = tmp_path / "spec-dock/.distribution-journal.json"
    payload = json.loads(journal.read_text(encoding="utf-8"))
    assert payload["intent"] == "update"
    assert payload["status"] == "executing"
    assert version.read_bytes() == before_version

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", original)
    assert main(["update", str(tmp_path)]) == 0
    assert not journal.exists()


def test_s60_root_rebind_preserves_replacement_and_original_retry_marker(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    (tmp_path / ".github/workflows/ci.yml").unlink()
    original = managed_distribution._apply_distribution_action
    displaced = tmp_path.with_name(f"{tmp_path.name}-displaced")
    switched = False

    def rebind_before_action(plan, target_root, action, *args, **kwargs):
        nonlocal switched
        if not switched:
            switched = True
            tmp_path.rename(displaced)
            tmp_path.mkdir()
            (tmp_path / "replacement-sentinel.txt").write_text("keep\n", encoding="utf-8")
        return original(plan, target_root, action, *args, **kwargs)

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", rebind_before_action)

    assert main(["update", str(tmp_path)]) == 1
    captured = capsys.readouterr().err
    assert "distribution partial failure during reconciliation" in captured
    assert "replacement-sentinel.txt" not in captured

    journal = displaced / "spec-dock/.distribution-journal.json"
    payload = json.loads(journal.read_text(encoding="utf-8"))
    displaced_stat = displaced.stat()
    assert payload["root_binding"] == {
        "device": displaced_stat.st_dev,
        "inode": displaced_stat.st_ino,
    }
    assert (tmp_path / "replacement-sentinel.txt").read_text(encoding="utf-8") == "keep\n"
    assert not (tmp_path / "spec-dock").exists()

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", original)
    replacement_before_retry = _filesystem_snapshot(tmp_path)
    assert main(["update", str(tmp_path)]) == 0
    assert (tmp_path / "spec-dock/spec-dock.version").is_file()
    assert (tmp_path / "replacement-sentinel.txt").read_text(encoding="utf-8") == "keep\n"
    assert journal.exists()
    assert (displaced / "spec-dock/.distribution-retry.json").exists()
    assert _filesystem_snapshot(tmp_path) != replacement_before_retry


def test_s65_uninstall_root_rebind_before_marker_write_is_zero_write(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    """I370-T-RACE-001: root rebind before the schema-2 guard writes nowhere."""

    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    displaced = tmp_path.with_name(f"{tmp_path.name}-uninstall-displaced")
    original_prepare_guard = managed_distribution.OperationJournalStore.prepare_legacy_guard
    switched = False

    def rebind_before_guard(store, *args, **kwargs):
        nonlocal switched
        if not switched:
            switched = True
            tmp_path.rename(displaced)
            tmp_path.mkdir()
            (tmp_path / "replacement-sentinel.txt").write_text("keep\n", encoding="utf-8")
        return original_prepare_guard(store, *args, **kwargs)

    monkeypatch.setattr(
        managed_distribution.OperationJournalStore,
        "prepare_legacy_guard",
        rebind_before_guard,
    )

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "error"
    assert (tmp_path / "replacement-sentinel.txt").read_text(encoding="utf-8") == "keep\n"
    assert not (tmp_path / "spec-dock/.uninstall-retry.json").exists()
    assert not (displaced / "spec-dock/.uninstall-retry.json").exists()
    assert not (tmp_path / "spec-dock/.distribution-retry.json").exists()
    assert not (displaced / "spec-dock/.distribution-retry.json").exists()
    assert not (tmp_path / "spec-dock/.distribution-journal.json").exists()
    assert not (displaced / "spec-dock/.distribution-journal.json").exists()


@pytest.mark.parametrize("relative_root", ("spec-dock/active", "spec-dock/.agent"))
def test_s65_uninstall_generated_root_type_collision_is_zero_write(
    tmp_path: Path,
    capsys,
    relative_root: str,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    generated_root = tmp_path / relative_root
    if generated_root.is_symlink() or generated_root.is_file():
        generated_root.unlink()
    else:
        shutil.rmtree(generated_root)
    generated_root.write_text("operator-owned replacement\n", encoding="utf-8")
    before = _filesystem_snapshot(tmp_path)

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "blocked"
    assert payload["phase"] == "preflight"
    assert relative_root in payload["failed_paths"]
    assert _filesystem_snapshot(tmp_path) == before


def test_s60_post_verify_failure_keeps_marker_until_forward_retry(tmp_path: Path, monkeypatch, capsys) -> None:
    assert main(["init", str(tmp_path)]) == 0
    (tmp_path / "spec-dock/docs/README.md").unlink()
    version = tmp_path / "spec-dock/spec-dock.version"
    before_version = version.read_bytes()
    original = managed_distribution.OperationJournalStore.mark_verified

    def fail_post_verify(*args, **kwargs):
        raise managed_distribution.DistributionApplyError("source bytes secret /private/outside/source.txt")

    monkeypatch.setattr(managed_distribution.OperationJournalStore, "mark_verified", fail_post_verify)

    assert main(["update", str(tmp_path)]) == 1

    captured = capsys.readouterr().err
    assert "source bytes secret" not in captured
    assert "/private/outside/source.txt" not in captured
    assert "distribution partial failure during reconciliation" in captured
    journal = tmp_path / "spec-dock/.distribution-journal.json"
    payload = json.loads(journal.read_text(encoding="utf-8"))
    assert payload["status"] == "executing"
    assert version.read_bytes() == before_version

    monkeypatch.setattr(managed_distribution.OperationJournalStore, "mark_verified", original)
    assert main(["update", str(tmp_path)]) == 0
    assert not journal.exists()


def test_s65_uninstall_invalid_version_is_zero_write(tmp_path: Path, capsys) -> None:
    assert main(["init", str(tmp_path)]) == 0
    version = tmp_path / "spec-dock/spec-dock.version"
    version.write_text("not-a-version\n", encoding="ascii")
    before = _filesystem_snapshot(tmp_path)

    assert main(["uninstall", str(tmp_path)]) == 2

    captured = capsys.readouterr().err
    assert captured == "error: Managed distribution deprovision preflight failed.\n"
    assert _filesystem_snapshot(tmp_path) == before


def test_s65_uninstall_distribution_or_dual_marker_is_zero_write(tmp_path: Path, capsys) -> None:
    """I370-T-LEG-001: foreign guard and dual evidence are typed, read-only recovery states."""

    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    root_stat = tmp_path.stat()
    distribution_marker = tmp_path / "spec-dock/.distribution-retry.json"
    distribution_marker.write_text(
        json.dumps(
            {
                "last_completed_phase": "current-external-materialized",
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

    assert main(["uninstall", str(tmp_path), "--json"]) == 1
    distribution_payload = json.loads(capsys.readouterr().out)
    assert distribution_payload["status"] == "partial_failure"
    assert distribution_payload["failed_paths"] == ["spec-dock/.distribution-retry.json"]
    assert distribution_payload["errors"] == ["Managed distribution deprovision recovery evidence does not match."]
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

    assert main(["uninstall", str(tmp_path), "--json"]) == 1
    dual_payload = json.loads(capsys.readouterr().out)
    assert dual_payload["status"] == "partial_failure"
    assert dual_payload["failed_paths"] == [
        "spec-dock/.distribution-retry.json",
        "spec-dock/.uninstall-retry.json",
    ]
    assert dual_payload["errors"] == ["Conflicting uninstall recovery evidence requires manual review."]
    assert _filesystem_snapshot(tmp_path) == before_dual


def test_s65_uninstall_legacy_retry_marker_without_version_requires_manual_recovery_and_is_read_only(
    tmp_path: Path,
    capsys,
) -> None:
    """I370-T-LEG-001: information-poor legacy state is never admitted or converted."""

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

    assert main(["uninstall", str(tmp_path), "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "partial_failure"
    assert payload["failed_paths"] == ["spec-dock/.uninstall-retry.json"]
    assert payload["retry_command"] is None
    assert payload["errors"] == ["Legacy uninstall recovery requires manual review."]
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
    assert action["reason"] == "direct-obsolete-identity-match"
    assert obsolete.exists()


def test_s70_uninstall_apply_preserves_unproven_legacy_scaffold_entry_and_blocks(
    tmp_path: Path,
    capsys,
) -> None:
    """I370-T-PRES-002: a legacy name has no recursive-root deletion authority."""

    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    legacy = tmp_path / "spec-dock/scripts/spec-dock-chatgpt"
    legacy.write_text("legacy managed scaffold\n", encoding="utf-8")
    before = _filesystem_snapshot(tmp_path)

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "blocked"
    actions = {action["path"]: action for action in payload["actions"]}
    assert "spec-dock/scripts" not in actions
    assert actions["spec-dock/scripts/spec-dock-chatgpt"]["category"] == "scaffold_managed"
    assert actions["spec-dock/scripts/spec-dock-chatgpt"]["status"] == "preserved"
    assert actions["spec-dock/scripts/spec-dock-chatgpt"]["reason"] == "unknown-managed-entry"
    assert _filesystem_snapshot(tmp_path) == before
    assert not (tmp_path / "spec-dock/.uninstall-retry.json").exists()


def test_s70_uninstall_apply_preserves_modified_managed_scaffold_and_blocks(
    tmp_path: Path,
    capsys,
) -> None:
    """I370-T-PRES-002: modified exact leaves block the whole operation."""

    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    managed = tmp_path / "spec-dock/docs/README.md"
    managed.write_text("locally modified managed scaffold\n", encoding="utf-8")
    before = _filesystem_snapshot(tmp_path)
    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "blocked"
    action = next(item for item in payload["actions"] if item["path"] == "spec-dock/docs/README.md")
    assert action["category"] == "scaffold_managed"
    assert action["status"] == "preserved"
    assert action["reason"] == "unknown-current-collision"
    assert _filesystem_snapshot(tmp_path) == before


def test_s70_keep_specs_uninstall_allows_reinit_without_losing_history(
    tmp_path: Path,
    capsys,
) -> None:
    """I370-T-PRES-001: keep deprovision and re-init preserve both witness trees exactly."""

    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    history = tmp_path / "spec-dock/initiatives/init-preserved/requirement.md"
    history.parent.mkdir(parents=True)
    history.write_text("preserved history\n", encoding="utf-8")
    empty_history_dir = history.parent / "empty"
    empty_history_dir.mkdir()
    history_link = history.parent / "requirement-link.md"
    history_link.symlink_to("requirement.md")
    workbench_note = tmp_path / "spec-dock/.workbench/product-note.md"
    workbench_note.write_text("preserved workbench\n", encoding="utf-8")
    history_before = _filesystem_snapshot(tmp_path / "spec-dock/initiatives")
    workbench_before = _filesystem_snapshot(tmp_path / "spec-dock/.workbench")

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "completed"
    assert (tmp_path / "spec-dock").is_dir()
    assert (tmp_path / "spec-dock/initiatives").is_dir()
    assert not (tmp_path / "spec-dock/spec-dock.version").exists()

    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    assert history.read_text(encoding="utf-8") == "preserved history\n"
    assert _filesystem_snapshot(tmp_path / "spec-dock/initiatives") == history_before
    assert _filesystem_snapshot(tmp_path / "spec-dock/.workbench") == workbench_before
    assert (tmp_path / "spec-dock/spec-dock.version").is_file()
    assert not (tmp_path / "spec-dock/.distribution-retry.json").exists()


@pytest.mark.parametrize(
    ("operation", "expected_status"),
    (("update", 0), ("uninstall", 0)),
)
def test_s70_empty_workspace_blocks_non_init_operations_without_writes(
    tmp_path: Path,
    operation: str,
    expected_status: int,
    capsys,
) -> None:
    specdock = tmp_path / "spec-dock"
    specdock.mkdir()
    external = tmp_path / ".agents/skills/spec-dock/SKILL.md"
    external.parent.mkdir(parents=True)
    external.write_bytes((INSTALL_ROOT / ".agents/skills/spec-dock/SKILL.md").read_bytes())
    before = _filesystem_snapshot(tmp_path)

    args = [operation, str(tmp_path)]
    assert main(args) == expected_status
    if operation == "update":
        assert _filesystem_snapshot(tmp_path) != before
        assert (tmp_path / "spec-dock/spec-dock.version").is_file()
        assert external.read_bytes() == (INSTALL_ROOT / ".agents/skills/spec-dock/SKILL.md").read_bytes()
        capsys.readouterr()
        return
    assert _filesystem_snapshot(tmp_path) == before
    captured = capsys.readouterr()
    assert captured.err == ""
    assert "status: planned" in captured.out


def test_s70_preserved_specs_workspace_blocks_update_without_writes(
    tmp_path: Path,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    history = tmp_path / "spec-dock/initiatives/init-preserved/requirement.md"
    history.parent.mkdir(parents=True)
    history.write_text("preserved history\n", encoding="utf-8")
    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 0
    capsys.readouterr()
    assert main(["update", str(tmp_path)]) == 0
    capsys.readouterr()
    assert history.read_text(encoding="utf-8") == "preserved history\n"
    assert (tmp_path / "spec-dock/spec-dock.version").is_file()


def test_s70_uninstall_apply_blocks_symlink_inside_managed_scaffold_before_marker(
    tmp_path: Path,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    external = tmp_path / "external.md"
    external.write_text("user-owned\n", encoding="utf-8")
    unsafe = tmp_path / "spec-dock/docs/external.md"
    unsafe.symlink_to(external)

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "blocked"
    assert not (tmp_path / "spec-dock/.uninstall-retry.json").exists()
    assert unsafe.is_symlink()
    assert external.read_text(encoding="utf-8") == "user-owned\n"


def test_s70_uninstall_apply_preserves_unknown_scaffold_entry_and_blocks(
    tmp_path: Path,
    capsys,
) -> None:
    """I370-T-PRES-002: an unknown managed-root child blocks without safe-subset deletion."""

    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    sentinel = tmp_path / "spec-dock/docs/rebind-sentinel.md"
    sentinel.write_text("managed root payload\n", encoding="utf-8")
    before = _filesystem_snapshot(tmp_path)

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "blocked"
    action = next(item for item in payload["actions"] if item["path"] == "spec-dock/docs/rebind-sentinel.md")
    assert action["status"] == "preserved"
    assert action["reason"] == "unknown-managed-entry"
    assert _filesystem_snapshot(tmp_path) == before
    assert not (tmp_path / "spec-dock/.uninstall-retry.json").exists()


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
    """I370-T-RACE-001: target replacement after guard publication remains pending."""

    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    managed = tmp_path / ".agents/skills/spec-dock/SKILL.md"
    original_prepare_guard = managed_distribution.OperationJournalStore.prepare_legacy_guard

    def rewrite_after_guard(store, *args, **kwargs):
        guard = original_prepare_guard(store, *args, **kwargs)
        managed.write_text("replacement after uninstall plan\n", encoding="utf-8")
        return guard

    monkeypatch.setattr(
        managed_distribution.OperationJournalStore,
        "prepare_legacy_guard",
        rewrite_after_guard,
    )

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "partial_failure"
    assert ".agents/skills/spec-dock/SKILL.md" in payload["failed_paths"]
    assert ".agents/skills/spec-dock/SKILL.md" in payload["pending_paths"]
    assert managed.read_text(encoding="utf-8") == "replacement after uninstall plan\n"
    assert (tmp_path / "spec-dock/.distribution-retry.json").is_file()
    assert (tmp_path / "spec-dock/.distribution-journal.json").is_file()
    assert not (tmp_path / "spec-dock/.uninstall-retry.json").exists()


def test_s70_uninstall_apply_rejects_same_target_symlink_replacement_after_plan(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    """I370-T-RACE-001: same-text symlink replacement fails descriptor binding."""

    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    active_issue = tmp_path / "spec-dock/active/issue"
    original_target = active_issue.readlink()
    original_prepare_guard = managed_distribution.OperationJournalStore.prepare_legacy_guard

    def replace_after_guard(store, *args, **kwargs):
        guard = original_prepare_guard(store, *args, **kwargs)
        active_issue.unlink()
        active_issue.symlink_to(original_target)
        return guard

    monkeypatch.setattr(
        managed_distribution.OperationJournalStore,
        "prepare_legacy_guard",
        replace_after_guard,
    )

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "partial_failure"
    action = next(item for item in payload["actions"] if item["path"] == "spec-dock/active/issue")
    assert action["status"] == "pending"
    assert action["error"] is None
    assert "spec-dock/active/issue" in payload["failed_paths"]
    assert "spec-dock/active/issue" in payload["pending_paths"]
    assert active_issue.is_symlink()
    assert active_issue.readlink() == original_target
    assert (tmp_path / "spec-dock/.distribution-retry.json").is_file()
    assert (tmp_path / "spec-dock/.distribution-journal.json").is_file()
    assert not (tmp_path / "spec-dock/.uninstall-retry.json").exists()


def test_s70_uninstall_apply_blocks_generated_hard_link_before_marker_write(tmp_path: Path, capsys) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    generated = tmp_path / "spec-dock/active/context-pack.md"
    external = tmp_path / "outside-context-pack.md"
    external.write_bytes(generated.read_bytes())
    generated.unlink()
    try:
        generated.hardlink_to(external)
    except OSError:
        pytest.skip("hard links are unavailable")

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "blocked"
    action = next(item for item in payload["actions"] if item["path"] == "spec-dock/active/context-pack.md")
    assert action["status"] == "preserved"
    assert action["reason"] == "generated-state-invalid"
    assert not (tmp_path / "spec-dock/.uninstall-retry.json").exists()
    assert generated.is_file()
    assert external.read_bytes() == generated.read_bytes()


def test_s70_uninstall_apply_blocks_hard_linked_generated_symlink_before_marker_write(
    tmp_path: Path,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    generated = tmp_path / "spec-dock/active/issue"
    alias = tmp_path / "active-issue-alias"
    try:
        os.link(generated, alias, follow_symlinks=False)
    except (OSError, NotImplementedError):
        pytest.skip("hard-linked symlinks are unavailable")

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "blocked"
    action = next(item for item in payload["actions"] if item["path"] == "spec-dock/active/issue")
    assert action["status"] == "preserved"
    assert action["reason"] == "generated-state-invalid"
    assert not (tmp_path / "spec-dock/.uninstall-retry.json").exists()
    assert generated.is_symlink()
    assert alias.is_symlink()


def test_s70_uninstall_apply_blocks_agent_symlink_before_marker_write(tmp_path: Path, capsys) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    external = tmp_path / "external-agent-state.txt"
    external.write_text("keep\n", encoding="utf-8")
    unsafe = tmp_path / "spec-dock/.agent/unsafe-link"
    unsafe.symlink_to(external)

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "blocked"
    action = next(item for item in payload["actions"] if item["path"] == "spec-dock/.agent/unsafe-link")
    assert action["status"] == "preserved"
    assert action["reason"] == "unknown-generated-state-entry"
    assert not (tmp_path / "spec-dock/.uninstall-retry.json").exists()
    assert unsafe.is_symlink()
    assert external.read_text(encoding="utf-8") == "keep\n"


def test_s70_uninstall_remove_specs_blocks_unsafe_descendant_before_marker_write(
    tmp_path: Path,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    external = tmp_path / "external-history.txt"
    external.write_text("keep\n", encoding="utf-8")
    unsafe = tmp_path / "spec-dock/initiatives/unsafe-link"
    unsafe.symlink_to(external)

    assert main(["uninstall", str(tmp_path), "--apply", "--remove-specs", "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "blocked"
    action = next(item for item in payload["actions"] if item["path"] == "spec-dock/initiatives")
    assert action["status"] == "preserved"
    assert "symlink" in action["reason"]
    assert not (tmp_path / "spec-dock/.uninstall-retry.json").exists()
    assert unsafe.is_symlink()
    assert external.read_text(encoding="utf-8") == "keep\n"


def test_s70_uninstall_apply_does_not_recreate_vanished_specdock_parent(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    """I370-T-RACE-001: vanished protocol parent is never recreated by guard publication."""

    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    original_prepare_guard = managed_distribution.OperationJournalStore.prepare_legacy_guard

    def remove_parent_before_guard(store, *args, **kwargs):
        shutil.rmtree(tmp_path / "spec-dock")
        return original_prepare_guard(store, *args, **kwargs)

    monkeypatch.setattr(
        managed_distribution.OperationJournalStore,
        "prepare_legacy_guard",
        remove_parent_before_guard,
    )

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "error"
    assert not (tmp_path / "spec-dock").exists()


def test_s50_update_rejects_managed_directory_replacement_after_preflight(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    (tmp_path / "spec-dock/docs/README.md").unlink()
    original_apply = managed_distribution._apply_distribution_action
    switched = False

    def replace_before_apply(plan, target_root, action, *args, **kwargs):
        nonlocal switched
        if not switched and action.path == "spec-dock/docs/README.md":
            switched = True
            managed = tmp_path / "spec-dock/docs"
            shutil.rmtree(managed)
            managed.mkdir(parents=True)
            (managed / "replacement-sentinel.md").write_text("keep\n", encoding="utf-8")
        return original_apply(plan, target_root, action, *args, **kwargs)

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", replace_before_apply)

    assert main(["update", str(tmp_path)]) == 1
    capsys.readouterr()
    assert (tmp_path / "spec-dock/docs/replacement-sentinel.md").read_text(encoding="utf-8") == "keep\n"


def test_s50_update_rejects_managed_directory_replacement_after_descriptor_open(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    (tmp_path / "spec-dock/docs/README.md").unlink()
    original_open = managed_distribution._open_distribution_parent_chain
    switched = False

    def replace_after_descriptor_open(target_root: Path, target_rel: str, **kwargs):
        nonlocal switched
        opened = original_open(target_root, target_rel, **kwargs)
        if not switched and target_rel == "spec-dock/docs/README.md":
            switched = True
            managed = tmp_path / "spec-dock/docs"
            managed.rename(tmp_path / "displaced-docs")
            managed.mkdir(parents=True)
            (managed / "replacement-sentinel.md").write_text("keep\n", encoding="utf-8")
        return opened

    monkeypatch.setattr(managed_distribution, "_open_distribution_parent_chain", replace_after_descriptor_open)

    assert main(["update", str(tmp_path)]) == 1
    capsys.readouterr()
    assert (tmp_path / "spec-dock/docs/replacement-sentinel.md").read_text(encoding="utf-8") == "keep\n"
    assert (tmp_path / "displaced-docs").is_dir()


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
    assert payload["phase"] == "complete"
    assert payload["last_completed_phase"] == "marker-finalized"
    assert shlex.split(payload["retry_command"]) == [
        "spec-dock",
        "uninstall",
        "--apply",
        "--keep-specs",
        os.path.relpath(tmp_path.resolve(), Path.cwd()),
    ]
    assert payload["pending_paths"] == []
    assert all(action["path"] != "spec-dock/.uninstall-retry.json" for action in payload["actions"])
    assert not (tmp_path / "spec-dock/.uninstall-retry.json").exists()
    assert not (tmp_path / "spec-dock/.distribution-retry.json").exists()
    assert not (tmp_path / "spec-dock/.distribution-journal.json").exists()


def test_s70_uninstall_does_not_run_fallible_workspace_cleanup_after_marker_finalization(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    original_rmdir = cli.os.rmdir
    target_identity = (tmp_path.stat().st_dev, tmp_path.stat().st_ino)
    attempted = False

    def fail_terminal_workspace_cleanup(name, *, dir_fd=None):
        nonlocal attempted
        is_target_root_parent = (
            dir_fd is not None and (os.fstat(dir_fd).st_dev, os.fstat(dir_fd).st_ino) == target_identity
        )
        if name == "spec-dock" and is_target_root_parent:
            attempted = True
            raise OSError("injected terminal workspace cleanup failure")
        return original_rmdir(name, dir_fd=dir_fd)

    monkeypatch.setattr(cli.os, "rmdir", fail_terminal_workspace_cleanup)
    assert main(["uninstall", str(tmp_path), "--apply", "--remove-specs", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    marker = tmp_path / "spec-dock/.uninstall-retry.json"
    assert payload["status"] == "completed"
    assert payload["phase"] == "complete"
    assert payload["last_completed_phase"] == "marker-finalized"
    assert not attempted
    assert not marker.exists()
    assert (tmp_path / "spec-dock").is_dir()
    assert list((tmp_path / "spec-dock").iterdir()) == [tmp_path / "spec-dock/.workbench"]


def test_s70_uninstall_marker_survives_partial_failure_and_is_removed_on_retry(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    """I370-T-REC-001: protocol-2 guard/journal survive failure and forward retry."""

    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    original_apply = managed_distribution._apply_distribution_action
    failed = False

    def fail_first_deprovision_action(plan, target_root, action, *args, **kwargs):
        nonlocal failed
        if not failed and action.operation == "uninstall":
            failed = True
            raise managed_distribution.DistributionApplyError("injected deprovision unlink failure")
        return original_apply(plan, target_root, action, *args, **kwargs)

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", fail_first_deprovision_action)
    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 1
    first_payload = json.loads(capsys.readouterr().out)
    guard = tmp_path / "spec-dock/.distribution-retry.json"
    journal = tmp_path / "spec-dock/.distribution-journal.json"
    assert first_payload["status"] == "partial_failure"
    assert first_payload["phase"] == "uninstall-apply"
    assert first_payload["last_completed_phase"] == "marker-written"
    expected_target = Path(os.path.relpath(tmp_path, Path.cwd())).as_posix()
    assert first_payload["retry_command"] == f"spec-dock uninstall --apply --keep-specs {expected_target}"
    assert first_payload["pending_paths"]
    assert first_payload["summary"]["pending"] == len(first_payload["pending_paths"])
    assert guard.is_file()
    assert journal.is_file()
    assert not (tmp_path / "spec-dock/.uninstall-retry.json").exists()

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", original_apply)
    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 0
    second_payload = json.loads(capsys.readouterr().out)
    assert second_payload["status"] == "completed"
    assert not guard.exists()
    assert not journal.exists()


def test_s70_uninstall_partial_failure_json_maps_typed_safe_result(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    """I370-T-JSON-001: JSON is a pure projection of an allowlisted typed failure."""

    failure_path = ".agents/skills/spec-dock/SKILL.md"
    result = managed_distribution.DistributionProcessResult(
        status="recovery_required",
        intent="deprovision",
        actions=(),
        action_outcomes=(
            managed_distribution.DistributionActionOutcome(
                path=failure_path,
                category="agent_skill",
                status="pending",
                reason="current-identity-match",
                error="Managed distribution deprovision action failed.",
            ),
        ),
        phase="uninstall-apply",
        last_completed_phase="marker-written",
        failed_paths=(failure_path,),
        pending_paths=(failure_path,),
        errors=(
            managed_distribution.DistributionProcessError(
                code="deprovision-recovery-required",
                message="Managed distribution deprovision recovery is required.",
            ),
        ),
        retry_policy="same-keep-command",
    )
    monkeypatch.setattr(cli, "execute_deprovision_distribution", lambda *_args, **_kwargs: result)

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    serialized = json.dumps(payload, sort_keys=True)
    expected_target = Path(os.path.relpath(tmp_path, Path.cwd())).as_posix()

    assert payload["status"] == "partial_failure"
    assert payload["target"] == expected_target
    assert payload["retry_command"] == f"spec-dock uninstall --apply --keep-specs {expected_target}"
    assert payload["failed_paths"] == [failure_path]
    assert payload["pending_paths"] == [failure_path]
    assert payload["errors"] == ["Managed distribution deprovision recovery is required."]
    assert not payload["target"].startswith("/")
    assert "secret" not in serialized
    assert "/outside/source" not in serialized


def test_s70_uninstall_partial_failure_text_shows_recovery_contract(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    """I370-T-TEXT-001: text consumes the same typed recovery result as JSON."""

    failure_path = ".agents/skills/spec-dock/SKILL.md"
    result = managed_distribution.DistributionProcessResult(
        status="recovery_required",
        intent="deprovision",
        actions=(),
        action_outcomes=(
            managed_distribution.DistributionActionOutcome(
                path=failure_path,
                category="agent_skill",
                status="pending",
                reason="current-identity-match",
                error="Managed distribution deprovision action failed.",
            ),
        ),
        phase="uninstall-apply",
        last_completed_phase="marker-written",
        failed_paths=(failure_path,),
        pending_paths=(failure_path,),
        errors=(
            managed_distribution.DistributionProcessError(
                code="deprovision-recovery-required",
                message="Managed distribution deprovision recovery is required.",
            ),
        ),
        retry_policy="same-keep-command",
    )
    monkeypatch.setattr(cli, "execute_deprovision_distribution", lambda *_args, **_kwargs: result)

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs"]) == 1
    output = capsys.readouterr().out

    assert "status: partial_failure" in output
    assert "phase: uninstall-apply" in output
    assert "last_completed_phase: marker-written" in output
    expected_target = Path(os.path.relpath(tmp_path, Path.cwd())).as_posix()
    assert f"retry_command: spec-dock uninstall --apply --keep-specs {expected_target}" in output
    assert f"failed_paths: {failure_path}" in output
    assert "Managed distribution deprovision action failed." in output
    assert "credential=should-not-leak" not in output
    assert f"-> {tmp_path}" not in output


def test_s70_uninstall_retry_command_runs_for_special_explicit_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys,
) -> None:
    """I370-T-JSON-001: a shell-safe retry re-enters the same typed keep route."""

    parent = tmp_path.parent
    target = parent / "-uninstall target"
    target.mkdir()
    monkeypatch.chdir(parent)
    failure_path = ".agents/skills/spec-dock/SKILL.md"
    results = iter((
        managed_distribution.DistributionProcessResult(
            status="recovery_required",
            intent="deprovision",
            actions=(),
            phase="uninstall-apply",
            last_completed_phase="marker-written",
            failed_paths=(failure_path,),
            pending_paths=(failure_path,),
            errors=(
                managed_distribution.DistributionProcessError(
                    code="deprovision-recovery-required",
                    message="Managed distribution deprovision recovery is required.",
                ),
            ),
            retry_policy="same-keep-command",
        ),
        managed_distribution.DistributionProcessResult(
            status="completed",
            intent="deprovision",
            actions=(),
            phase="complete",
            last_completed_phase="marker-finalized",
            retry_policy="same-keep-command",
        ),
    ))
    service_calls: list[Path] = []

    def fake_service(_install_root: Path, **kwargs: object) -> managed_distribution.DistributionProcessResult:
        target_root = kwargs["target_root"]
        assert isinstance(target_root, Path)
        service_calls.append(target_root)
        return next(results)

    monkeypatch.setattr(cli, "execute_deprovision_distribution", fake_service)
    assert main(["uninstall", str(target), "--apply", "--keep-specs", "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    retry = "spec-dock uninstall --apply --keep-specs -- '-uninstall target'"
    assert payload["retry_command"] == retry

    assert main(shlex.split(retry)[1:]) == 0
    capsys.readouterr()
    assert service_calls == [target.resolve(), target.resolve()]
    assert not (target / "spec-dock/.uninstall-retry.json").exists()


def test_s70_uninstall_marker_write_failure_is_retryable(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    """I370-T-REC-001: journal publication failure leaves a resumable guard-only state."""

    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    original_prepare = managed_distribution.OperationJournalStore.prepare
    failed = False

    def fail_journal_prepare(store, *args, **kwargs):
        nonlocal failed
        if not failed:
            failed = True
            raise managed_distribution.DistributionApplyError("injected deprovision journal write failure")
        return original_prepare(store, *args, **kwargs)

    monkeypatch.setattr(managed_distribution.OperationJournalStore, "prepare", fail_journal_prepare)
    guard = tmp_path / "spec-dock/.distribution-retry.json"
    journal = tmp_path / "spec-dock/.distribution-journal.json"

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 1
    first_payload = json.loads(capsys.readouterr().out)
    assert first_payload["status"] == "partial_failure"
    assert first_payload["phase"] == "marker-write"
    assert first_payload["last_completed_phase"] == "marker-written"
    assert guard.is_file()
    assert not journal.exists()
    assert not (tmp_path / "spec-dock/.uninstall-retry.json").exists()

    monkeypatch.setattr(managed_distribution.OperationJournalStore, "prepare", original_prepare)
    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 0
    second_payload = json.loads(capsys.readouterr().out)
    assert second_payload["status"] == "completed"
    assert not guard.exists()
    assert not journal.exists()


def test_i371_legacy_marker_reader_remains_service_owned(
    tmp_path: Path,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    marker = tmp_path / "spec-dock/.uninstall-retry.json"
    marker.write_bytes(b'{"managed_by":"spec-dock"')
    before = marker.read_bytes()

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "error"
    assert payload["retry_command"] is None
    assert marker.read_bytes() == before


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


def test_s70_uninstall_preserves_workbench_and_allows_idempotent_rerun(tmp_path: Path, capsys) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()

    assert main(["uninstall", str(tmp_path), "--apply", "--remove-specs", "--json"]) == 0
    capsys.readouterr()
    assert (tmp_path / "spec-dock").is_dir()
    assert list((tmp_path / "spec-dock").iterdir()) == [tmp_path / "spec-dock/.workbench"]

    assert main(["uninstall", str(tmp_path), "--apply", "--remove-specs", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "completed"
    assert payload["summary"]["already_removed"] > 0
    assert (tmp_path / "spec-dock").is_dir()
    assert list((tmp_path / "spec-dock").iterdir()) == [tmp_path / "spec-dock/.workbench"]


def test_s70_uninstall_remove_specs_blocks_unknown_nested_generated_directories(
    tmp_path: Path,
    capsys,
) -> None:
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    nested_active = tmp_path / "spec-dock/active/nested/empty/deeper"
    nested_agent = tmp_path / "spec-dock/.agent/nested/empty"
    nested_active.mkdir(parents=True)
    nested_agent.mkdir(parents=True)

    before = _filesystem_snapshot(tmp_path)
    assert main(["uninstall", str(tmp_path), "--apply", "--remove-specs", "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "blocked"
    assert "spec-dock/active/nested" in payload["failed_paths"]
    assert "spec-dock/.agent/nested" in payload["failed_paths"]
    assert _filesystem_snapshot(tmp_path) == before
    assert nested_active.is_dir()
    assert nested_agent.is_dir()


def test_s70_uninstall_does_not_cleanup_empty_preserved_or_unknown_directories(
    tmp_path: Path,
    capsys,
) -> None:
    """I370-T-PRES-002/I370-T-BLK-001: an unknown empty child blocks all cleanup, including safe subsets."""

    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    empty_initiative = tmp_path / "spec-dock/initiatives/empty-preserved"
    empty_initiative.mkdir(parents=True)
    empty_workbench = tmp_path / "spec-dock/.workbench/empty-payload"
    empty_workbench.mkdir(parents=True)
    empty_unknown = tmp_path / ".codex/user-owned-empty"
    empty_unknown.mkdir(parents=True)
    before = _filesystem_snapshot(tmp_path)

    assert main(["uninstall", str(tmp_path), "--apply", "--keep-specs", "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    removed_empty_paths = {action["path"] for action in payload["actions"] if action["status"] == "empty_dir_removed"}
    unknown_action = next(action for action in payload["actions"] if action["path"] == ".codex/user-owned-empty")

    assert payload["status"] == "blocked"
    assert unknown_action["status"] == "preserved"
    assert unknown_action["reason"] == "unknown-managed-entry"
    assert empty_initiative.is_dir()
    assert empty_workbench.is_dir()
    assert empty_unknown.is_dir()
    assert "spec-dock/initiatives/empty-preserved" not in removed_empty_paths
    assert "spec-dock/.workbench/empty-payload" not in removed_empty_paths
    assert ".codex/user-owned-empty" not in removed_empty_paths
    assert removed_empty_paths == set()
    assert _filesystem_snapshot(tmp_path) == before


def test_i371_uninstall_routes_deprovision_and_purge_to_typed_services(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    """Issue 371 routes every uninstall authority through one typed service."""

    service_calls: list[tuple[str, bool, object]] = []

    def fake_deprovision_service(
        install_root: Path,
        **kwargs: object,
    ) -> managed_distribution.DistributionProcessResult:
        service_calls.append(("deprovision", bool(kwargs["apply"]), kwargs.get("expected_root_identity")))
        apply = bool(kwargs["apply"])
        return managed_distribution.DistributionProcessResult(
            status="completed" if apply else "planned",
            intent="deprovision",
            actions=(),
            phase="complete" if apply else "preflight",
            last_completed_phase="marker-finalized" if apply else "preflight-complete",
            retry_policy="none" if apply else "same-keep-command",
        )

    def fake_purge_service(
        install_root: Path,
        **kwargs: object,
    ) -> managed_distribution.DistributionProcessResult:
        service_calls.append(("purge", bool(kwargs["apply"]), kwargs.get("expected_root_identity")))
        apply = bool(kwargs["apply"])
        return managed_distribution.DistributionProcessResult(
            status="completed" if apply else "planned",
            intent="purge",
            actions=(),
            phase="complete" if apply else "preflight",
            last_completed_phase="marker-finalized" if apply else "preflight-complete",
            retry_policy="none" if apply else "same-remove-command",
        )

    monkeypatch.setattr(cli, "execute_deprovision_distribution", fake_deprovision_service)
    monkeypatch.setattr(cli, "execute_explicit_spec_history_purge_distribution", fake_purge_service)

    target = tmp_path / "consumer"
    target.mkdir()
    requests = (
        ["uninstall", str(target), "--json"],
        ["uninstall", str(target), "--keep-specs", "--json"],
        ["uninstall", str(target), "--apply", "--keep-specs", "--json"],
        ["uninstall", str(target), "--remove-specs", "--json"],
        ["uninstall", str(target), "--apply", "--remove-specs", "--json"],
    )
    for request in requests:
        assert main(request) == 0
        captured = capsys.readouterr()
        assert captured.err == ""
        assert captured.out.count("\n") == 1

    assert [(kind, apply) for kind, apply, _identity in service_calls] == [
        ("deprovision", False),
        ("deprovision", False),
        ("deprovision", True),
        ("purge", False),
        ("purge", True),
    ]
    assert service_calls[2][2] is not None
    assert service_calls[4][2] is not None


def test_i371_distribution_cutover_has_single_purge_writer() -> None:
    """The old remove-specs writer is absent and the typed purge owner is unique."""

    source = inspect.getsource(cli)
    tree = ast.parse(source)
    definitions = {node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert not any(name.endswith("remove_specs_compatibility") for name in definitions)
    assert not any(name.startswith("_Uninstall") for name in definitions)
    assert not any(name.endswith("_uninstall_plan") for name in definitions)
    assert not any(name.endswith("_uninstall_tree_fd") for name in definitions)
    assert not any(name.endswith("uninstall_retry_marker") for name in definitions)

    call_edges: dict[str, set[str]] = {}
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        call_edges[node.name] = {
            child.func.id
            for child in ast.walk(node)
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name)
        }

    assert "_run_uninstall_deprovision" in call_edges["_run_uninstall"]
    assert "_run_uninstall_explicit_spec_history_purge" in call_edges["_run_uninstall"]
    assert "execute_deprovision_distribution" in call_edges["_run_uninstall_deprovision"]
    assert (
        "execute_explicit_spec_history_purge_distribution" in call_edges["_run_uninstall_explicit_spec_history_purge"]
    )
    assert source.count("execute_explicit_spec_history_purge_distribution(") == 1
    assert "OperationJournalStore" not in inspect.getsource(cli._run_uninstall_explicit_spec_history_purge)


def test_i370_typed_uninstall_mapper_preserves_schema_status_and_retry_contract(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """I370-T-RESULT-001/I370-T-JSON-001: one typed result owns every public field."""

    monkeypatch.chdir(tmp_path)
    target = (tmp_path / "-consumer target").resolve()
    normal_error = managed_distribution.DistributionProcessError(
        code="deprovision-preflight-failed",
        message="Managed distribution deprovision preflight failed.",
    )
    recovery_error = managed_distribution.DistributionProcessError(
        code="deprovision-recovery-required",
        message="Managed distribution deprovision recovery is required.",
    )
    cases = (
        (
            "default-planned",
            None,
            False,
            managed_distribution.DistributionProcessResult(
                status="planned",
                intent="deprovision",
                actions=(),
                action_outcomes=(
                    managed_distribution.DistributionActionOutcome(
                        path="spec-dock/docs/README.md",
                        category="scaffold_managed",
                        status="would_remove",
                        reason="exact managed asset",
                    ),
                ),
                phase="preflight",
                last_completed_phase="preflight-complete",
                retry_policy="same-keep-command",
            ),
            "planned",
            str(target),
            None,
            0,
        ),
        (
            "keep-planned",
            "keep",
            False,
            managed_distribution.DistributionProcessResult(
                status="planned",
                intent="deprovision",
                actions=(),
                phase="preflight",
                last_completed_phase="preflight-complete",
                retry_policy="same-keep-command",
            ),
            "planned",
            str(target),
            "spec-dock uninstall --apply --keep-specs -- '-consumer target'",
            0,
        ),
        (
            "keep-completed",
            "keep",
            True,
            managed_distribution.DistributionProcessResult(
                status="completed",
                intent="deprovision",
                actions=(),
                action_outcomes=(
                    managed_distribution.DistributionActionOutcome(
                        path="spec-dock/docs/README.md",
                        category="scaffold_managed",
                        status="removed",
                        reason="exact managed asset removed",
                    ),
                ),
                phase="complete",
                last_completed_phase="marker-finalized",
                retry_policy="same-keep-command",
            ),
            "completed",
            str(target),
            "spec-dock uninstall --apply --keep-specs -- '-consumer target'",
            0,
        ),
        (
            "keep-blocked",
            "keep",
            True,
            managed_distribution.DistributionProcessResult(
                status="blocked",
                intent="deprovision",
                actions=(),
                action_outcomes=(
                    managed_distribution.DistributionActionOutcome(
                        path="spec-dock/docs/unknown.txt",
                        category="unmanaged",
                        status="preserved",
                        reason="unproven ownership",
                    ),
                ),
                phase="preflight",
                last_completed_phase="preflight-complete",
                failed_paths=("spec-dock/docs/unknown.txt",),
                errors=(normal_error,),
                retry_policy="same-keep-command",
            ),
            "blocked",
            "-consumer target",
            "spec-dock uninstall --apply --keep-specs -- '-consumer target'",
            1,
        ),
        (
            "keep-recovery",
            "keep",
            True,
            managed_distribution.DistributionProcessResult(
                status="recovery_required",
                intent="deprovision",
                actions=(),
                action_outcomes=(
                    managed_distribution.DistributionActionOutcome(
                        path="spec-dock/docs/README.md",
                        category="scaffold_managed",
                        status="pending",
                        reason="exact managed asset",
                        error="Managed distribution deprovision action failed.",
                    ),
                ),
                phase="uninstall-apply",
                last_completed_phase="marker-written",
                failed_paths=("spec-dock/docs/README.md",),
                pending_paths=("spec-dock/docs/README.md",),
                errors=(recovery_error,),
                retry_policy="same-keep-command",
            ),
            "partial_failure",
            "-consumer target",
            "spec-dock uninstall --apply --keep-specs -- '-consumer target'",
            1,
        ),
        (
            "keep-error",
            "keep",
            True,
            managed_distribution.DistributionProcessResult(
                status="error",
                intent="deprovision",
                actions=(),
                phase="preflight",
                last_completed_phase="not-started",
                errors=(normal_error,),
                retry_policy="same-keep-command",
            ),
            "error",
            str(target),
            "spec-dock uninstall --apply --keep-specs -- '-consumer target'",
            2,
        ),
        (
            "legacy-marker",
            "keep",
            True,
            managed_distribution.DistributionProcessResult(
                status="recovery_required",
                intent="deprovision",
                actions=(),
                reason="legacy-marker-unconvertible",
                phase="preflight",
                last_completed_phase="not-started",
                failed_paths=("spec-dock/.uninstall-retry.json",),
                errors=(
                    managed_distribution.DistributionProcessError(
                        code="legacy-marker-unconvertible",
                        message="Legacy uninstall recovery requires manual review.",
                    ),
                ),
                retry_policy="manual-recovery",
            ),
            "partial_failure",
            "-consumer target",
            None,
            1,
        ),
    )

    for case_name, specs_mode, apply, result, status, expected_target, retry, exit_code in cases:
        payload = cli._uninstall_payload_from_result(
            result,
            target_root=target,
            apply=apply,
            specs_mode=specs_mode,
        )

        assert set(payload) == {
            "schema_version",
            "target",
            "mode",
            "apply",
            "specs_mode",
            "status",
            "phase",
            "last_completed_phase",
            "retry_command",
            "failed_paths",
            "pending_paths",
            "summary",
            "actions",
            "guidance",
            "errors",
        }, case_name
        assert payload["schema_version"] == 1
        assert payload["status"] == status
        assert payload["target"] == expected_target
        assert payload["retry_command"] == retry
        assert payload["phase"] == result.phase
        assert payload["last_completed_phase"] == result.last_completed_phase
        assert payload["failed_paths"] == list(result.failed_paths)
        assert payload["pending_paths"] == list(result.pending_paths)
        assert set(result.pending_paths).issubset(result.failed_paths)
        assert payload["errors"] == [error.message for error in result.errors]
        assert cli._uninstall_exit_code_from_result(result) == exit_code
        assert all("--remove-specs" not in guidance for guidance in payload["guidance"])

    planned_payload = cli._uninstall_payload_from_result(
        cases[0][3],
        target_root=target,
        apply=False,
        specs_mode=None,
    )
    assert planned_payload["summary"] == {
        "would_remove": 1,
        "removed": 0,
        "already_removed": 0,
        "preserved": 0,
        "failed": 0,
        "pending": 0,
        "empty_dir_removed": 0,
    }
    assert planned_payload["actions"] == [
        {
            "path": "spec-dock/docs/README.md",
            "category": "scaffold_managed",
            "status": "would_remove",
            "reason": "exact managed asset",
            "error": None,
        }
    ]
    recovery_payload = cli._uninstall_payload_from_result(
        cases[4][3],
        target_root=target,
        apply=True,
        specs_mode="keep",
    )
    assert recovery_payload["actions"][0]["error"] == "Managed distribution deprovision action failed."

    mapper_source = inspect.getsource(cli._uninstall_payload_from_result)
    assert "OperationJournalStore" not in mapper_source
    assert ".distribution-journal" not in mapper_source
    assert ".distribution-retry" not in mapper_source


def test_i370_typed_uninstall_mapper_allowlists_operation_and_action_errors(
    tmp_path: Path,
) -> None:
    """I370-T-RESULT-001/I370-T-JSON-001: raw typed error text is never public."""

    failure_path = "spec-dock/docs/README.md"
    injected = "credential=should-not-leak at /private/provider/source"
    result = managed_distribution.DistributionProcessResult(
        status="recovery_required",
        intent="deprovision",
        actions=(),
        action_outcomes=(
            managed_distribution.DistributionActionOutcome(
                path=failure_path,
                category="scaffold_managed",
                status="failed",
                reason="internal-unrecognized-reason",
                error=injected,
            ),
        ),
        phase="uninstall-apply",
        last_completed_phase="marker-written",
        failed_paths=(failure_path,),
        errors=(
            managed_distribution.DistributionProcessError(
                code="internal-unrecognized-error",
                message=injected,
            ),
        ),
        retry_policy="same-keep-command",
    )

    payload = cli._uninstall_payload_from_result(
        result,
        target_root=(tmp_path / "consumer").resolve(),
        apply=True,
        specs_mode="keep",
    )

    assert payload["errors"] == ["Managed distribution deprovision failed."]
    assert payload["actions"][0]["error"] == "Managed distribution deprovision action failed."
    assert injected not in json.dumps(payload, sort_keys=True)


@pytest.mark.parametrize(
    ("case_name", "target_token", "create_file"),
    (
        ("missing", "missing-target", False),
        ("file", "file-target.txt", True),
        ("leading-hyphen", "-leading-target", False),
        ("space", "space target", False),
    ),
)
@pytest.mark.parametrize("json_requested", (True, False), ids=("json", "text"))
def test_i370_uninstall_non_directory_target_error_is_stable_and_path_free(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    case_name: str,
    target_token: str,
    create_file: bool,
    json_requested: bool,
) -> None:
    """I370-T-JSON-001/I370-T-TEXT-001: target stays a field, never error text."""

    monkeypatch.chdir(tmp_path)
    target = tmp_path / target_token
    if create_file:
        target.write_bytes(b"user-owned\n")
    args = ["uninstall"]
    if json_requested:
        args.append("--json")
    else:
        args.append("--keep-specs")
    args.extend(("--", target_token))

    assert main(args) == 2, case_name
    captured = capsys.readouterr()
    expected_error = "target path is not a directory"
    if json_requested:
        assert captured.err == ""
        assert captured.out.count("\n") == 1
        assert json.loads(captured.out) == {
            "schema_version": 1,
            "target": str(target.resolve()),
            "mode": "dry-run",
            "apply": False,
            "specs_mode": None,
            "status": "error",
            "phase": "preflight",
            "last_completed_phase": "not-started",
            "retry_command": None,
            "failed_paths": [],
            "pending_paths": [],
            "summary": {
                "would_remove": 0,
                "removed": 0,
                "already_removed": 0,
                "preserved": 0,
                "failed": 0,
                "pending": 0,
                "empty_dir_removed": 0,
            },
            "actions": [],
            "guidance": [
                "dry-run only; pass --apply --keep-specs to mutate managed distribution artifacts",
                "reinstall or refresh with installer CLI: spec-dock init <target> or spec-dock update <target>",
            ],
            "errors": [expected_error],
        }
    else:
        assert captured.out == ""
        assert captured.err == f"error: {expected_error}\n"
    if create_file:
        assert target.read_bytes() == b"user-owned\n"


def test_i370_uninstall_text_uses_typed_payload_section_order(tmp_path: Path) -> None:
    """I370-T-TEXT-001: text renders the one typed payload in the public order."""

    result = managed_distribution.DistributionProcessResult(
        status="recovery_required",
        intent="deprovision",
        actions=(),
        action_outcomes=(
            managed_distribution.DistributionActionOutcome(
                path="spec-dock/docs/README.md",
                category="scaffold_managed",
                status="pending",
                reason="exact managed asset",
            ),
        ),
        phase="uninstall-apply",
        last_completed_phase="marker-written",
        failed_paths=("spec-dock/docs/README.md",),
        pending_paths=("spec-dock/docs/README.md",),
        errors=(
            managed_distribution.DistributionProcessError(
                code="deprovision-recovery-required",
                message="Managed distribution deprovision recovery is required.",
            ),
        ),
        retry_policy="same-keep-command",
    )
    payload = cli._uninstall_payload_from_result(
        result,
        target_root=(tmp_path / "consumer").resolve(),
        apply=True,
        specs_mode="keep",
    )
    rendered = cli._render_uninstall_text(payload)

    ordered_labels = (
        "spec-dock: uninstall result (apply)",
        "specs_mode:",
        "status:",
        "phase:",
        "last_completed_phase:",
        "retry_command:",
        "failed_paths:",
        "summary:",
        "actions:",
        "errors:",
        "guidance:",
    )
    positions = tuple(rendered.index(label) for label in ordered_labels)
    assert positions == tuple(sorted(positions))
    assert "status: partial_failure" in rendered
    assert "phase: uninstall-apply" in rendered
    assert "last_completed_phase: marker-written" in rendered
