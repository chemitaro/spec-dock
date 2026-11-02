"""Native worktree list/show/create in canonical mode (iss-00440).

Replaces tests/cli_runtime/test_issue413_worktree.py and the list/show and create/remove round trips of
tests/cli_runtime/test_worktree_commands_vnext.py, which ran on the retired schema-3 committed workspace.
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.legacy_contracts_g3 import (
    cli,
    git_out,
    has_branch,
    linked_worktree,
    make_world,
    other_clone,
    select,
)

if TYPE_CHECKING:
    from pathlib import Path

    from tests.support.canonical_scopes import CanonicalWorld


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> CanonicalWorld:
    return make_world(tmp_path, monkeypatch, capsys)


def _create(capsys: pytest.CaptureFixture[str], root: Path, name: str, *options: str) -> tuple[int, dict]:
    return cli(capsys, "--project", str(root), "worktree", "create", name, "--base", "HEAD", *options, "--json")


def test_list_uses_native_inventory_without_scope_metadata_or_control(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    head = git_out(root, "rev-parse", "HEAD")
    other = tmp_path / "linked with space"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "-b", "parallel", str(other)], check=True, capture_output=True
    )
    assert main(["--project", str(root), "worktree", "list", "--json"]) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == "" and result["effects"] == []
    assert result["data"]["kind"] == "worktree-list"
    rows = {item["path"]: item for item in result["data"]["result"]["items"]}
    native = {"bare": False, "locked": False, "prunable": False, "catalog": False}
    assert rows[str(root)] == {"path": str(root), "branch": "main", "head": head, **native}
    assert rows[str(other)] == {"path": str(other), "branch": "parallel", "head": head, **native}
    # canonical mode also lists the clone's catalog worktree, marked as such
    catalog = str(world.catalog.resolve())
    assert set(rows) == {str(root), str(other), catalog} and rows[catalog]["catalog"] is True
    assert not (root / ".git/spec-dock").exists()
    assert not (other / "spec-dock/.agent").exists()


@pytest.mark.parametrize("reference", ["planning", "wt:wt1", "relative/path"])
def test_show_rejects_retired_aliases_and_relative_paths_before_project_access(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], reference: str
) -> None:
    code, result = cli(capsys, "--project", str(tmp_path / "missing"), "worktree", "show", reference, "--json")
    assert code == 2
    assert result["effects"] == [] and list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("leaf", ["create", "bootstrap"])
def test_worktree_rejects_retired_recovery_before_project_access(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], leaf: str
) -> None:
    options = (
        ["planning", "--base", "HEAD", "--root", str(tmp_path / "worktrees"), "--recover", "wt1"]
        if leaf == "create"
        else [str(tmp_path / "linked"), "--recover"]
    )
    code, result = cli(capsys, "--project", str(tmp_path / "missing"), "worktree", leaf, *options, "--json")
    assert code == 2
    assert result["error"]["code"] == "ARGUMENT_RETIRED" and result["effects"] == []
    assert list(tmp_path.iterdir()) == []


def test_show_resolves_an_explicit_native_path_without_reading_the_target_workspace(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    other = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "-b", "parallel", str(other)], check=True, capture_output=True
    )
    (other / "spec-dock/workspace.json").unlink()
    code, result = cli(capsys, "--project", str(root), "worktree", "show", str(other), "--json")
    assert code == 0
    assert result["data"]["kind"] == "worktree" and result["effects"] == []
    observed = result["data"]["result"]
    assert observed["path"] == str(other) and observed["branch"] == "parallel"
    assert observed["head"] == git_out(other, "rev-parse", "HEAD")
    assert observed["changed"] is False and observed["catalog"] is False
    assert observed["observed"]["bare"] is False and observed["observed"]["locked"] is False
    assert not (root / ".git/spec-dock").exists()


def test_create_uses_the_explicit_name_and_fixed_base_without_registration_or_bootstrap(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    selected = select(world)
    exact_selection = selected.read_bytes()
    head = git_out(root, "rev-parse", "HEAD")
    container = tmp_path / "worktrees"
    created = container / "planning"
    code, result = _create(capsys, root, "planning", "--root", str(container))
    assert code == 0, result
    assert result["status"] == "succeeded" and result["data"]["kind"] == "worktree"
    data = result["data"]["result"]
    assert data["path"] == str(created) and data["branch"] == "worktree/planning"
    assert data["head"] == head and data["changed"] is True
    assert git_out(created, "branch", "--show-current") == "worktree/planning"
    assert (created / "spec-dock/workspace.json").read_bytes() == (root / "spec-dock/workspace.json").read_bytes()
    # canonical mode links the new worktree to the clone's catalog
    assert (created / "spec-dock/initiatives").is_symlink()
    assert not (created / "spec-dock/.agent").exists() and not (root / ".git/spec-dock").exists()
    assert selected.read_bytes() == exact_selection
    assert not (created / "bootstrap-ran").exists()
    assert git_out(root, "branch", "--show-current") == "main"


def test_create_dry_run_plans_the_fixed_target_without_creating_a_directory_or_branch(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    container = tmp_path / "worktrees"
    code, result = _create(capsys, root, "planning", "--root", str(container), "--dry-run")
    assert code == 0, result
    assert result["status"] == "planned" and result["data"]["result"]["changed"] is False
    assert result["data"]["result"]["can_apply"] is True and result["data"]["result"]["blockers"] == []
    assert result["data"]["result"]["path"] == str(container / "planning")
    assert not container.exists()
    assert not has_branch(root, "worktree/planning")
    # the follow-up link effects are planned too
    assert all(effect["status"] == "planned" for effect in result["effects"])


@pytest.mark.parametrize("dry_run", [False, True])
def test_create_handles_explicit_nested_placement_and_dry_run_keeps_all_missing_directories_absent(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str], dry_run: bool
) -> None:
    root = world.main
    parent = tmp_path / "new-parent"
    container = parent / "worktrees"
    options = ["--dry-run"] if dry_run else []
    code, result = _create(capsys, root, "planning", "--root", str(container), *options)
    assert code == 0, result
    assert result["data"]["result"]["path"] == str(container / "planning")
    assert (container / "planning").exists() is not dry_run
    assert parent.exists() is not dry_run
    assert [effect["target"] for effect in result["effects"] if effect["kind"] == "worktree-directory"] == [
        str(parent),
        str(container),
    ]
    native = [effect for effect in result["effects"] if not effect["kind"].startswith(("canonical.", "git.info"))]
    # the follow-up link step adds canonical.* effects, some of them unchanged
    assert all(effect["status"] == ("planned" if dry_run else "succeeded") for effect in native)


def test_create_requires_an_explicit_name_before_reading_the_project(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, result = cli(
        capsys,
        "--project",
        str(tmp_path / "missing"),
        "worktree",
        "create",
        "--base",
        "HEAD",
        "--root",
        str(tmp_path / "worktrees"),
        "--json",
    )
    assert code == 2
    assert result["effects"] == [] and list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("override", [False, True])
def test_create_uses_configured_root_with_explicit_root_taking_precedence(
    world: CanonicalWorld,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    override: bool,
) -> None:
    root = world.main
    configured = tmp_path / "configured-worktrees"
    explicit = tmp_path / "explicit-worktrees"
    monkeypatch.setenv("SPEC_DOCK_WORKTREE_ROOT", str(configured))
    options = ["--root", str(explicit)] if override else []
    code, result = _create(capsys, root, "planning", *options)
    assert code == 0, result
    container = explicit if override else configured
    assert result["data"]["result"]["path"] == str(container / "planning")
    assert (container / "planning").is_dir()
    assert not (configured if override else explicit).exists()


def test_create_refuses_dirty_source_without_stashing_or_creating_a_branch(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    note = root / "untracked.txt"
    note.write_bytes(b"must remain")
    container = tmp_path / "worktrees"
    code, result = _create(capsys, root, "planning", "--root", str(container))
    assert code == 3, result
    assert result["effects"] == [] and not container.exists()
    assert note.read_bytes() == b"must remain"
    assert not has_branch(root, "worktree/planning")


@pytest.mark.skipif(os.name != "posix", reason="native reference-transaction hook")
def test_create_stops_after_a_branch_hook_changes_source_selection_and_preserves_the_git_effect(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    record = select(world)
    hook = root / ".git/hooks/reference-transaction"
    hook.write_text(f'#!/bin/sh\nif [ "$1" = committed ]; then rm -f {shlex.quote(str(record))}; fi\nexit 0\n')
    hook.chmod(0o700)
    container = tmp_path / "worktrees"
    code, result = _create(capsys, root, "planning", "--root", str(container))
    assert code == 6, result
    assert result["status"] == "partial" and result["data"]["result"]["changed"] is True
    assert "direct selection changed" in result["error"]["message"]
    assert any(
        effect["kind"] == "git.branch.create" and effect["status"] == "succeeded" for effect in result["effects"]
    )
    assert any(
        effect["kind"] == "git.worktree.add" and effect["status"] == "not_attempted" for effect in result["effects"]
    )
    assert not record.exists() and not (container / "planning").exists()
    assert has_branch(root, "worktree/planning")


def test_create_refuses_a_missing_path_still_present_in_native_inventory_without_creating_a_ref(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    container = tmp_path / "worktrees"
    path = container / "planning"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "-b", "older", str(path)], check=True, capture_output=True
    )
    shutil.rmtree(path)
    code, result = _create(capsys, root, "planning", "--root", str(container))
    assert code == 3, result
    assert result["effects"] == [] and not path.exists()
    assert not has_branch(root, "worktree/planning")


@pytest.mark.skipif(os.name != "posix", reason="native post-checkout hook")
def test_create_reports_a_confirmed_worktree_even_when_native_git_returns_a_hook_failure(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    hook = root / ".git/hooks/post-checkout"
    hook.write_text("#!/bin/sh\nprintf 'fixture worktree checkout hook failed\\nsecond hook line\\n' >&2\nexit 17\n")
    hook.chmod(0o700)
    container = tmp_path / "worktrees"
    container.mkdir()
    path = container / "planning"
    assert (
        main([
            "--project",
            str(root),
            "worktree",
            "create",
            "planning",
            "--base",
            "HEAD",
            "--root",
            str(container),
            "--json",
        ])
        == 6
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == "" and result["error"]["code"] == "GIT_FAILED"
    assert "fixture worktree checkout hook failed\nsecond hook line\n" in result["error"]["details"]["git"]["stderr"]
    assert result["error"]["details"]["git"]["returncode"] != 0
    # canonical mode returns an incomplete native result unchanged: no link step follows
    assert result["effects"] == [
        {"kind": "git.branch.create", "status": "succeeded", "target": "worktree/planning"},
        {"kind": "git.worktree.add", "status": "succeeded", "target": str(path)},
    ]
    assert path.is_dir() and (path / "spec-dock/workspace.json").exists()
    assert result["data"]["result"]["observed"]["branch"] == "worktree/planning"
    assert result["data"]["result"]["changed"] is True
    assert result["recovery"]["can_rollback"] is False


def test_unknown_placement_directory_creation_is_partial_without_attempting_git_mutations(
    world: CanonicalWorld, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    container = tmp_path / "worktrees"
    real_mkdir = os.mkdir

    def mkdir(path, mode=0o777, *, dir_fd=None):
        real_mkdir(path, mode, dir_fd=dir_fd)
        if path == "worktrees" and dir_fd is not None:
            raise OSError("placement directory reply was lost")

    monkeypatch.setattr(os, "mkdir", mkdir)
    code, result = _create(capsys, root, "planning", "--root", str(container))
    assert code == 6, result
    assert result["effects"] == [
        {"kind": "worktree-directory", "status": "unknown", "target": str(container)},
        {"kind": "git.branch.create", "status": "not_attempted", "target": "worktree/planning"},
        {"kind": "git.worktree.add", "status": "not_attempted", "target": str(container / "planning")},
    ]
    assert container.is_dir() and list(container.iterdir()) == []
    assert not has_branch(root, "worktree/planning")


def test_create_refuses_a_scope_backend_guard_without_a_scope_target_before_any_effect(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    container = tmp_path / "worktrees"
    code, result = _create(capsys, root, "planning", "--root", str(container), "--expect-backend", "github")
    assert code == 3, result
    assert "one existing Scope target" in result["error"]["message"]
    assert result["effects"] == [] and not container.exists()
    assert not has_branch(root, "worktree/planning")


def test_create_checks_the_captured_direct_scope_for_expect_current_without_changing_it(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    world.scope("epic", 2, "Second", parent=1)
    record = select(world)
    before = record.read_bytes()
    container = tmp_path / "worktrees"
    code, result = _create(capsys, root, "planning", "--root", str(container), "--expect-current", "epic-00002")
    assert code == 3, result
    assert "direct target does not match" in result["error"]["message"]
    assert result["effects"] == [] and not container.exists() and record.read_bytes() == before


@pytest.mark.parametrize("leaf", ["list", "show"])
def test_native_queries_do_not_silently_ignore_an_inapplicable_backend_guard(
    world: CanonicalWorld, capsys: pytest.CaptureFixture[str], leaf: str
) -> None:
    root = world.main
    target = [str(root)] if leaf == "show" else []
    code, result = cli(
        capsys, "--project", str(root), "worktree", leaf, *target, "--expect-backend", "github", "--json"
    )
    assert code == 3, result
    assert "one existing Scope target" in result["error"]["message"] and result["effects"] == []


@pytest.mark.parametrize("leaf", ["list", "show"])
def test_native_queries_compare_expect_current_with_the_own_worktree_selection(
    world: CanonicalWorld, capsys: pytest.CaptureFixture[str], leaf: str
) -> None:
    root = world.main
    target = [str(root)] if leaf == "show" else []
    code, result = cli(
        capsys, "--project", str(root), "worktree", leaf, *target, "--expect-current", "init-00001", "--json"
    )
    assert code == 3, result
    assert "direct target does not match" in result["error"]["message"] and result["effects"] == []
    record = select(world)
    before = record.read_bytes()
    code, result = cli(
        capsys, "--project", str(root), "worktree", leaf, *target, "--expect-current", "gh:example/repo#1", "--json"
    )
    assert code == 0, result
    assert result["effects"] == [] and record.read_bytes() == before


def test_create_does_not_replace_an_explicit_empty_root_with_an_environment_default(
    world: CanonicalWorld, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    configured = tmp_path / "configured-worktrees"
    monkeypatch.setenv("SPEC_DOCK_WORKTREE_ROOT", str(configured))
    code, result = _create(capsys, root, "planning", "--root", "")
    assert code == 3, result
    assert result["effects"] == [] and not configured.exists()


@pytest.mark.skipif(os.name != "posix", reason="native reference-transaction hook")
def test_create_rechecks_the_new_branch_tip_before_attaching_a_worktree(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    previous = git_out(root, "rev-parse", "HEAD")
    git_out(root, "commit", "--allow-empty", "-qm", "second commit")
    marker = root / ".git/fixture-hook-ran"
    hook = root / ".git/hooks/reference-transaction"
    hook.write_text(
        f'#!/bin/sh\nif [ "$1" = committed ] && [ ! -e {shlex.quote(str(marker))} ]; then\n'
        f"touch {shlex.quote(str(marker))}\n"
        f"git -C {shlex.quote(str(root))} update-ref refs/heads/worktree/planning {previous}\nfi\nexit 0\n"
    )
    hook.chmod(0o700)
    container = tmp_path / "worktrees"
    code, result = _create(capsys, root, "planning", "--root", str(container))
    assert code == 6, result
    assert result["status"] == "partial"
    assert "branch no longer matches" in result["error"]["message"]
    assert any(
        effect["kind"] == "git.branch.create" and effect["status"] == "succeeded" for effect in result["effects"]
    )
    assert any(
        effect["kind"] == "git.worktree.add" and effect["status"] == "not_attempted" for effect in result["effects"]
    )
    assert not (container / "planning").exists()
    assert git_out(root, "rev-parse", "refs/heads/worktree/planning") == previous


@pytest.mark.skipif(os.name != "posix", reason="native post-checkout hook")
def test_create_preserves_a_hook_modified_worktree_and_reports_partial_instead_of_success(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    hook = root / ".git/hooks/post-checkout"
    hook.write_text('#!/bin/sh\nprintf "hook output must remain\\n" > hook-note.txt\nexit 0\n')
    hook.chmod(0o700)
    container = tmp_path / "worktrees"
    code, result = _create(capsys, root, "planning", "--root", str(container))
    assert code == 6, result
    assert "created worktree is not clean" in result["error"]["message"]
    assert result["data"]["result"]["changed"] is True
    assert any(effect["kind"] == "git.worktree.add" and effect["status"] == "succeeded" for effect in result["effects"])
    assert (container / "planning/hook-note.txt").read_text() == "hook output must remain\n"
    assert result["recovery"]["can_rollback"] is False


@pytest.mark.skipif(os.name != "posix", reason="native reference-transaction hook")
def test_create_does_not_adopt_a_target_directory_created_by_an_actor_after_branch_creation(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    container = tmp_path / "worktrees"
    container.mkdir()
    target = container / "planning"
    hook = root / ".git/hooks/reference-transaction"
    hook.write_text(
        f'#!/bin/sh\nif [ "$1" = committed ] && [ ! -e {shlex.quote(str(target))} ]; then '
        f"mkdir {shlex.quote(str(target))}; fi\nexit 0\n"
    )
    hook.chmod(0o700)
    code, result = _create(capsys, root, "planning", "--root", str(container))
    assert code == 6, result
    assert result["effects"] == [
        {"kind": "git.branch.create", "status": "succeeded", "target": "worktree/planning"},
        {"kind": "git.worktree.add", "status": "not_attempted", "target": str(target)},
    ]
    assert target.is_dir() and list(target.iterdir()) == []
    assert str(target) not in git_out(root, "worktree", "list", "--porcelain")


def test_native_worktree_help_describes_name_path_and_git_inventory_without_retired_control(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["help", "worktree", "create"]) == 0
    create = capsys.readouterr().out
    assert "worktree/NAME" in create and "SPEC_DOCK_WORKTREE_ROOT" in create
    assert "--recover" not in create and "operation record" not in create
    assert main(["help", "worktree", "list"]) == 0
    listed = capsys.readouterr().out
    assert "native Git" in listed and "installation control" not in listed
    assert "Worktree ID" not in listed and "control state" not in listed
    assert main(["help", "worktree", "show"]) == 0
    shown = capsys.readouterr().out
    assert "/absolute/worktree" in shown and "installation control" not in shown
    assert "worktree ID" not in shown and "Worktree ID" not in shown


def test_create_refuses_a_direct_record_copied_from_another_physical_clone_without_effects(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    foreign = other_clone(world, tmp_path / "other-clone")
    record = select(world)
    record.write_bytes(select(world, checkout=foreign).read_bytes())
    before = record.read_bytes()
    container = tmp_path / "worktrees"
    code, result = _create(capsys, root, "planning", "--root", str(container))
    assert code == 3, result
    assert "physical identity" in result["error"]["message"]
    assert result["effects"] == [] and not container.exists() and record.read_bytes() == before


@pytest.mark.skipif(os.name != "posix", reason="native directory replacement during fsync")
def test_create_stops_if_a_new_placement_parent_is_replaced_before_the_next_directory(
    world: CanonicalWorld, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    parent = tmp_path / "new-parent"
    container = parent / "worktrees"
    retained = tmp_path / "retained-parent"
    native_fsync = os.fsync
    boundary_identity = tmp_path.stat().st_ino

    def fsync(descriptor: int) -> None:
        if os.fstat(descriptor).st_ino == boundary_identity and parent.is_dir() and not retained.exists():
            parent.rename(retained)
            parent.mkdir()
        native_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", fsync)
    code, result = _create(capsys, root, "planning", "--root", str(container))
    assert code == 6, result
    assert result["effects"] == [
        {"kind": "worktree-directory", "status": "succeeded", "target": str(parent)},
        {"kind": "worktree-directory", "status": "not_attempted", "target": str(container)},
        {"kind": "git.branch.create", "status": "not_attempted", "target": "worktree/planning"},
        {"kind": "git.worktree.add", "status": "not_attempted", "target": str(container / "planning")},
    ]
    assert parent.is_dir() and list(parent.iterdir()) == []
    assert retained.is_dir() and list(retained.iterdir()) == []


@pytest.mark.parametrize("from_linked", [False, True])
def test_list_reports_native_locked_detached_and_missing_worktrees_from_either_root(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str], from_linked: bool
) -> None:
    root = world.main
    locked, detached, missing = (tmp_path / name for name in ("locked", "detached", "missing"))
    linked_worktree(world, locked, "parallel")
    subprocess.run(["git", "-C", str(root), "worktree", "lock", str(locked)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "--detach", str(detached), "HEAD"], check=True, capture_output=True
    )
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "-b", "old", str(missing)], check=True, capture_output=True
    )
    shutil.rmtree(missing)
    code, result = cli(capsys, "--project", str(locked if from_linked else root), "worktree", "list", "--json")
    assert code == 0, result
    rows = {item["path"]: item for item in result["data"]["result"]["items"]}
    assert rows[str(locked)]["locked"] is True and rows[str(locked)]["branch"] == "parallel"
    assert rows[str(detached)]["branch"] is None and rows[str(detached)]["bare"] is False
    assert rows[str(missing)]["prunable"] is True and rows[str(missing)]["branch"] == "old"
    assert result["effects"] == [] and not (root / ".git/spec-dock").exists()
    assert not missing.exists()


@pytest.mark.parametrize("mode", ["other-clone", "subdirectory", "symlink"])
def test_show_refuses_paths_that_are_not_an_exact_native_worktree_of_this_clone(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str], mode: str
) -> None:
    root = world.main
    if mode == "other-clone":
        target = other_clone(world, tmp_path / "other-clone")
    elif mode == "subdirectory":
        target = root / "spec-dock"
    else:
        target = tmp_path / "alias"
        target.symlink_to(root, target_is_directory=True)
    code, result = cli(capsys, "--project", str(root), "worktree", "show", str(target), "--json")
    assert code == (5 if mode == "symlink" else 4), result
    assert result["status"] == "failed" and result["effects"] == []
    assert (root / "spec-dock/workspace.json").is_file() and not (root / ".git/spec-dock").exists()


def test_known_directory_collision_preserves_the_actor_path_without_claiming_an_uncertain_write(
    world: CanonicalWorld, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    container = tmp_path / "worktrees"
    native_mkdir = os.mkdir

    def mkdir(path, mode=0o777, *, dir_fd=None):
        native_mkdir(path, mode, dir_fd=dir_fd)
        if path == "worktrees" and dir_fd is not None:
            raise FileExistsError("another actor created the placement")

    monkeypatch.setattr(os, "mkdir", mkdir)
    code, result = _create(capsys, root, "planning", "--root", str(container))
    assert code == 3, result
    assert all(effect["status"] == "not_attempted" for effect in result["effects"])
    assert container.is_dir() and list(container.iterdir()) == []
    assert not has_branch(root, "worktree/planning")


def test_create_from_a_detached_source_keeps_its_head_and_pins_the_explicit_base(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    subprocess.run(["git", "-C", str(root), "switch", "--detach", "HEAD"], check=True, capture_output=True)
    head = git_out(root, "rev-parse", "HEAD")
    container = tmp_path / "worktrees"
    assert (
        main([
            "--project",
            str(root),
            "worktree",
            "create",
            "detached-plan",
            "--base",
            "HEAD",
            "--root",
            str(container),
            "--json",
        ])
        == 0
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    created = container / "detached-plan"
    assert not output.err and result["status"] == "succeeded"
    assert result["data"]["result"]["head"] == head
    assert result["data"]["result"]["branch"] == "worktree/detached-plan"
    assert git_out(created, "rev-parse", "HEAD") == head
    assert subprocess.run(["git", "-C", str(root), "symbolic-ref", "-q", "HEAD"], capture_output=True).returncode == 1
    assert git_out(root, "rev-parse", "HEAD") == head
    assert not (created / "spec-dock/.agent").exists() and not (created / "bootstrap-ran").exists()
    assert not (root / ".git/spec-dock").exists()


@pytest.mark.parametrize(("blocked", "exit_code"), [("missing-base", 5), ("path", 3), ("branch", 3)])
def test_create_rejects_an_unknown_base_or_existing_name_before_any_effect(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str], blocked: str, exit_code: int
) -> None:
    root = world.main
    container = tmp_path / "worktrees"
    if blocked == "path":
        (container / "planning").mkdir(parents=True)
        (container / "planning/evidence.bin").write_bytes(b"actor content")
    elif blocked == "branch":
        subprocess.run(["git", "-C", str(root), "branch", "worktree/planning", "HEAD"], check=True, capture_output=True)
    before = tree_digest(root), tree_digest(container) if container.exists() else None
    assert (
        main([
            "--project",
            str(root),
            "worktree",
            "create",
            "planning",
            "--base",
            "missing-ref" if blocked == "missing-base" else "HEAD",
            "--root",
            str(container),
            "--json",
        ])
        == exit_code
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["status"] == "failed" and result["effects"] == [] and not output.err
    assert (tree_digest(root), tree_digest(container) if container.exists() else None) == before
    assert not (root / ".git/spec-dock").exists()


# --- from tests/cli_runtime/test_worktree_commands_vnext.py ---


def test_worktree_list_and_show_use_native_identity_without_scope_or_control_read(
    world: CanonicalWorld, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    before = tree_digest(root)
    prefix = ["--project", str(root), "worktree"]
    code, listed = cli(capsys, *prefix, "list", "--json")
    assert code == 0, listed
    items = [item for item in listed["data"]["result"]["items"] if not item["catalog"]]
    assert len(items) == 1 and items[0]["path"] == str(root) and items[0]["branch"] == "main"
    assert listed["effects"] == []
    code, shown = cli(capsys, *prefix, "show", str(root), "--json")
    assert code == 0, shown
    assert shown["data"]["result"]["path"] == str(root)
    assert shown["data"]["result"]["head"] == items[0]["head"] and shown["data"]["result"]["branch"] == "main"
    assert shown["effects"] == [] and tree_digest(root) == before
    assert not (root / ".git/spec-dock").exists() and not (root / "spec-dock/.agent").exists()


def test_worktree_create_and_remove_preview_without_writes_and_retain_the_branch(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    container = tmp_path / "worktrees"
    target = container / "planning"
    command = ["--project", str(root), "worktree", "create", "planning", "--base", "HEAD", "--root", str(container)]
    before = tree_digest(root)
    code, preview = cli(capsys, *command, "--json", "--dry-run")
    assert code == 0, preview
    assert preview["status"] == "planned" and preview["data"]["result"]["path"] == str(target)
    assert preview["data"]["result"]["changed"] is False and preview["data"]["result"]["can_apply"] is True
    assert not container.exists() and tree_digest(root) == before
    code, created = cli(capsys, *command, "--json")
    assert code == 0, created
    assert (
        created["data"]["result"]["path"] == str(target) and created["data"]["result"]["branch"] == "worktree/planning"
    )
    assert target.is_dir() and created["data"]["result"]["changed"] is True
    branch_tip = git_out(root, "rev-parse", "refs/heads/worktree/planning")
    remove = ["--project", str(root), "worktree", "remove", str(target), "--json"]
    current = tree_digest(root)
    target_before = tree_digest(target)
    code, refused = cli(capsys, *remove)
    assert code == 3 and refused["effects"] == []
    assert tree_digest(root) == current and tree_digest(target) == target_before
    code, plan = cli(capsys, *remove, "--dry-run")
    assert code == 0, plan
    assert plan["status"] == "planned" and plan["data"]["result"]["can_apply"] is True
    assert tree_digest(root) == current and tree_digest(target) == target_before
    code, removed = cli(capsys, *remove, "--yes")
    assert code == 0, removed
    assert removed["data"]["result"]["path"] == str(target) and removed["data"]["result"]["changed"] is True
    assert not target.exists()
    assert git_out(root, "rev-parse", "refs/heads/worktree/planning") == branch_tip
    assert not (root / ".git/spec-dock").exists()
