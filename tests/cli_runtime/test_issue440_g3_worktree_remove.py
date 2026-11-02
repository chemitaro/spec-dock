"""Native worktree removal in canonical mode preserves branches and outside files (iss-00440).

Replaces tests/cli_runtime/test_issue413_worktree_remove.py, which ran on the retired schema-3 committed
workspace. The linked worktree carries its own catalog link; canonical removal treats that link as SpecDock's own
ignored entry, so the legacy expectations about other ignored content still hold.
"""

from __future__ import annotations

import errno
import json
import os
import shutil
import subprocess
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from tests.support.legacy_contracts_g3 import cli, linked_worktree, make_world, select

if TYPE_CHECKING:
    from pathlib import Path


def linked_workspace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> tuple[Path, Path]:
    world = make_world(tmp_path, monkeypatch, capsys)
    return world.main, linked_worktree(world, tmp_path / "linked", "parallel")


def _remove(capsys: pytest.CaptureFixture[str], project: Path, target: Path, *options: str) -> tuple[int, dict]:
    return cli(capsys, "--project", str(project), "worktree", "remove", str(target), *options, "--json")


def test_remove_operates_on_native_inventory_and_retains_the_branch_and_outside_content(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other = linked_workspace(tmp_path, monkeypatch, capsys)
    outside = tmp_path / "outside.txt"
    outside.write_bytes(b"outside remains")
    branch = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "refs/heads/parallel"], check=True, capture_output=True
    ).stdout
    code, result = _remove(capsys, root, other, "--yes")
    assert code == 0, result
    assert result["data"]["result"]["path"] == str(other) and result["data"]["result"]["changed"] is True
    assert result["effects"] == [{"kind": "git.worktree.remove", "status": "succeeded", "target": str(other)}]
    assert not other.exists() and outside.read_bytes() == b"outside remains"
    assert (
        subprocess.run(
            ["git", "-C", str(root), "rev-parse", "refs/heads/parallel"], check=True, capture_output=True
        ).stdout
        == branch
    )
    assert not (root / ".git/spec-dock").exists() and not (root / "spec-dock/.agent").exists()


def test_remove_requires_explicit_confirmation_and_preserves_an_unconfirmed_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other = linked_workspace(tmp_path, monkeypatch, capsys)
    code, result = _remove(capsys, root, other)
    assert code == 3, result
    assert result["effects"] == [] and other.is_dir()


def test_remove_preview_checks_the_target_without_git_or_filesystem_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other = linked_workspace(tmp_path, monkeypatch, capsys)
    inventory = subprocess.run(
        ["git", "-C", str(root), "worktree", "list", "--porcelain", "-z"], check=True, capture_output=True
    ).stdout
    code, result = _remove(capsys, root, other, "--dry-run")
    assert code == 0, result
    assert result["status"] == "planned" and result["data"]["result"]["can_apply"] is True
    assert result["data"]["result"]["changed"] is False and other.is_dir()
    assert result["effects"] == [{"kind": "git.worktree.remove", "status": "planned", "target": str(other)}]
    assert (
        subprocess.run(
            ["git", "-C", str(root), "worktree", "list", "--porcelain", "-z"], check=True, capture_output=True
        ).stdout
        == inventory
    )


@pytest.mark.parametrize("protected", ["main", "current"])
@pytest.mark.parametrize("dry_run", [False, True])
def test_remove_rejects_the_main_or_current_worktree_before_any_git_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], protected: str, dry_run: bool
) -> None:
    root, other = linked_workspace(tmp_path, monkeypatch, capsys)
    project, target = (other, root) if protected == "main" else (other, other)
    flags = ["--dry-run"] if dry_run else []
    code, result = _remove(capsys, project, target, "--yes", *flags)
    assert code == 3, result
    assert result["effects"] == [] and root.is_dir() and other.is_dir()


@pytest.mark.parametrize("dirty", ["tracked", "untracked"])
@pytest.mark.parametrize("dry_run", [False, True])
def test_remove_never_discards_tracked_or_untracked_changes_even_with_discard_ignored(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], dirty: str, dry_run: bool
) -> None:
    root, other = linked_workspace(tmp_path, monkeypatch, capsys)
    path = other / "spec-dock/workspace.json" if dirty == "tracked" else other / "untracked.txt"
    path.write_bytes(b"preserve unfinished work")
    flags = ["--dry-run"] if dry_run else []
    code, result = _remove(capsys, root, other, "--discard-ignored", "--yes", *flags)
    assert code == 3, result
    assert result["effects"] == [] and path.read_bytes() == b"preserve unfinished work"


@pytest.mark.parametrize("dry_run", [False, True])
def test_remove_requires_discard_ignored_before_any_effect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], dry_run: bool
) -> None:
    root, other = linked_workspace(tmp_path, monkeypatch, capsys)
    evidence = other / "spec-dock/.workbench/important.bin"
    evidence.parent.mkdir()
    evidence.write_bytes(b"preserve ignored evidence")
    flags = ["--dry-run"] if dry_run else []
    code, result = _remove(capsys, root, other, "--yes", *flags)
    assert code == 3, result
    assert result["effects"] == []
    assert evidence.read_bytes() == b"preserve ignored evidence"


@pytest.mark.parametrize("dry_run", [False, True])
def test_remove_requires_unlock_for_a_native_locked_worktree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], dry_run: bool
) -> None:
    root, other = linked_workspace(tmp_path, monkeypatch, capsys)
    subprocess.run(
        ["git", "-C", str(root), "worktree", "lock", "--reason", "fixture", str(other)], check=True, capture_output=True
    )
    flags = ["--dry-run"] if dry_run else []
    code, result = _remove(capsys, root, other, "--yes", *flags)
    assert code == 3, result
    assert result["effects"] == [] and other.is_dir()
    inventory = subprocess.run(
        ["git", "-C", str(root), "worktree", "list", "--porcelain", "-z"], check=True, capture_output=True
    ).stdout
    assert b"locked fixture\0" in inventory


@pytest.mark.parametrize("dry_run", [False, True])
def test_remove_unlocks_only_the_explicit_target_or_plans_both_effects_without_writing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], dry_run: bool
) -> None:
    root, other = linked_workspace(tmp_path, monkeypatch, capsys)
    subprocess.run(
        ["git", "-C", str(root), "worktree", "lock", "--reason", "fixture", str(other)], check=True, capture_output=True
    )
    flags = ["--dry-run"] if dry_run else []
    code, result = _remove(capsys, root, other, "--unlock", "--yes", *flags)
    assert code == 0, result
    status = "planned" if dry_run else "succeeded"
    assert result["effects"] == [
        {"kind": "git.worktree.unlock", "status": status, "target": str(other)},
        {"kind": "git.worktree.remove", "status": status, "target": str(other)},
    ]
    assert other.exists() is dry_run and result["data"]["result"]["changed"] is not dry_run
    inventory = subprocess.run(
        ["git", "-C", str(root), "worktree", "list", "--porcelain", "-z"], check=True, capture_output=True
    ).stdout
    assert (b"locked fixture\0" in inventory) is dry_run


def test_remove_keeps_successful_unlock_and_native_error_when_removal_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other = linked_workspace(tmp_path, monkeypatch, capsys)
    subprocess.run(["git", "-C", str(root), "worktree", "lock", str(other)], check=True, capture_output=True)
    native_run = subprocess.run
    stderr = b"fatal: fixture remove failure\nkeep this native second line\n"

    def run(argv, *args, **kwargs):
        if tuple(argv[:5]) == ("git", "-C", str(root), "worktree", "remove"):
            return subprocess.CompletedProcess(argv, 128, b"", stderr)
        return native_run(argv, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", run)
    assert main(["--project", str(root), "worktree", "remove", str(other), "--unlock", "--yes", "--json"]) == 6
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == "" and result["status"] == "partial" and result["data"]["result"]["changed"] is True
    assert result["effects"] == [
        {"kind": "git.worktree.unlock", "status": "succeeded", "target": str(other)},
        {"kind": "git.worktree.remove", "status": "unknown", "target": str(other)},
    ]
    assert result["error"]["details"]["git"]["stderr"] == stderr.decode()
    assert result["error"]["details"]["git"]["returncode"] == 128 and other.is_dir()
    inventory = native_run(
        ["git", "-C", str(root), "worktree", "list", "--porcelain", "-z"], check=True, capture_output=True
    ).stdout
    # the clone's catalog worktree stays locked; only the target's own entry must be unlocked
    (entry,) = [item for item in inventory.split(b"\0\0") if item.startswith(b"worktree " + os.fsencode(other))]
    assert b"locked" not in entry
    assert result["recovery"]["can_resume"] is False and result["recovery"]["can_rollback"] is False


@pytest.mark.parametrize("guard", ["current", "backend"])
@pytest.mark.parametrize("dry_run", [False, True])
def test_remove_checks_self_selection_and_rejects_backend_expectations_without_a_scope_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], guard: str, dry_run: bool
) -> None:
    world = make_world(tmp_path, monkeypatch, capsys)
    root, other = world.main, linked_worktree(world, tmp_path / "linked", "parallel")
    world.scope("epic", 2, "Second", parent=1)
    record = select(world)
    before = record.read_bytes()
    option = ["--expect-current", "gh:example/repo#2"] if guard == "current" else ["--expect-backend", "github"]
    flags = ["--dry-run"] if dry_run else []
    code, result = _remove(capsys, root, other, "--yes", *option, *flags)
    assert code == 3, result
    assert result["effects"] == [] and record.read_bytes() == before and other.is_dir()
    code, result = _remove(capsys, root, other, "--yes", "--expect-current", "gh:example/repo#1", *flags)
    assert code == 0, result
    assert result["data"]["result"]["changed"] is not dry_run
    assert record.read_bytes() == before and other.exists() is dry_run


def test_remove_reports_confirmed_removal_when_git_finishes_the_mutation_then_returns_an_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other = linked_workspace(tmp_path, monkeypatch, capsys)
    native_run = subprocess.run

    def run(argv, *args, **kwargs):
        result = native_run(argv, *args, **kwargs)
        if tuple(argv[:5]) == ("git", "-C", str(root), "worktree", "remove"):
            assert result.returncode == 0
            return subprocess.CompletedProcess(argv, 128, result.stdout, b"native error after removal\n")
        return result

    monkeypatch.setattr(subprocess, "run", run)
    code, result = _remove(capsys, root, other, "--yes")
    assert code == 6, result
    assert result["effects"] == [{"kind": "git.worktree.remove", "status": "succeeded", "target": str(other)}]
    assert result["data"]["result"]["changed"] is True and result["data"]["result"]["observed"]["removed"] is True
    assert result["error"]["details"]["git"]["stderr"] == "native error after removal\n" and not other.exists()


def test_remove_does_not_claim_success_from_a_git_exit_zero_with_the_target_still_present(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other = linked_workspace(tmp_path, monkeypatch, capsys)
    native_run = subprocess.run

    def run(argv, *args, **kwargs):
        if tuple(argv[:5]) == ("git", "-C", str(root), "worktree", "remove"):
            return subprocess.CompletedProcess(argv, 0, b"", b"")
        return native_run(argv, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", run)
    code, result = _remove(capsys, root, other, "--yes")
    assert code == 6, result
    assert result["effects"] == [{"kind": "git.worktree.remove", "status": "unknown", "target": str(other)}]
    assert result["data"]["result"]["changed"] is False and result["data"]["result"]["observed"]["removed"] is False
    assert other.is_dir() and result["status"] == "partial"


def test_remove_confirms_unlock_before_attempting_removal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other = linked_workspace(tmp_path, monkeypatch, capsys)
    subprocess.run(["git", "-C", str(root), "worktree", "lock", str(other)], check=True, capture_output=True)
    native_run = subprocess.run
    removals: list[str] = []

    def run(argv, *args, **kwargs):
        if tuple(argv[:5]) == ("git", "-C", str(root), "worktree", "unlock"):
            return subprocess.CompletedProcess(argv, 0, b"", b"")
        if tuple(argv[:5]) == ("git", "-C", str(root), "worktree", "remove"):
            removals.append(str(argv[-1]))
        return native_run(argv, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", run)
    code, result = _remove(capsys, root, other, "--unlock", "--yes")
    assert code == 6, result
    assert removals == [] and other.is_dir()
    assert result["effects"] == [
        {"kind": "git.worktree.unlock", "status": "unknown", "target": str(other)},
        {"kind": "git.worktree.remove", "status": "not_attempted", "target": str(other)},
    ]
    assert result["data"]["result"]["changed"] is False


@pytest.mark.parametrize("dry_run", [False, True])
def test_explicit_discard_removes_only_ignored_content_inside_the_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], dry_run: bool
) -> None:
    world = make_world(tmp_path, monkeypatch, capsys)
    root, other = world.main, linked_worktree(world, tmp_path / "linked", "parallel")
    outside = tmp_path / "outside.bin"
    outside.write_bytes(b"outside evidence")
    evidence = other / "spec-dock/.workbench/ignored.bin"
    evidence.parent.mkdir()
    evidence.write_bytes(b"explicitly discard this")
    if os.name == "posix":
        (evidence.parent / "outside-link").symlink_to(outside)
    scope_file = world.catalog / "00000-00999/init-00001/requirement.md"
    catalog_bytes = scope_file.read_bytes()
    flags = ["--dry-run"] if dry_run else []
    code, result = _remove(capsys, root, other, "--discard-ignored", "--yes", *flags)
    assert code == 0, result
    assert result["data"]["result"]["changed"] is not dry_run and other.exists() is dry_run
    assert outside.read_bytes() == b"outside evidence"
    # the target's catalog link is ignored content too; discarding it never touches the catalog
    assert scope_file.read_bytes() == catalog_bytes
    assert subprocess.run(
        ["git", "-C", str(root), "show-ref", "--verify", "refs/heads/parallel"], check=True, capture_output=True
    ).stdout


def test_remove_rejects_the_bare_main_of_a_clone_from_a_valid_linked_project(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    initial = make_world(tmp_path, monkeypatch, capsys).main
    bare, source = tmp_path / "bare.git", tmp_path / "source"
    subprocess.run(["git", "clone", "--bare", str(initial), str(bare)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(bare), "worktree", "add", "-b", "source", str(source)], check=True, capture_output=True
    )
    code, result = _remove(capsys, source, bare, "--yes")
    # canonical mode lists the target's ignored files before the legacy bare/main refusal, so the refusal comes
    # from Git (GIT_FAILED, exit 5) instead of the legacy precondition (exit 3); it still stops before any effect
    assert code == 5 and result["status"] == "failed", result
    assert result["effects"] == [] and bare.is_dir() and source.is_dir()


@pytest.mark.parametrize("phase", ["unlock", "remove"])
def test_remove_detects_a_source_selection_change_without_restoring_the_actor_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], phase: str
) -> None:
    world = make_world(tmp_path, monkeypatch, capsys)
    root, other = world.main, linked_worktree(world, tmp_path / "linked", "parallel")
    record = select(world)
    if phase == "unlock":
        subprocess.run(["git", "-C", str(root), "worktree", "lock", str(other)], check=True, capture_output=True)
    native_run = subprocess.run
    removals: list[str] = []

    def run(argv, *args, **kwargs):
        result = native_run(argv, *args, **kwargs)
        if tuple(argv[:5]) == ("git", "-C", str(root), "worktree", "remove"):
            removals.append(str(argv[-1]))
        if tuple(argv[:5]) == ("git", "-C", str(root), "worktree", phase):
            assert result.returncode == 0
            record.unlink()
        return result

    monkeypatch.setattr(subprocess, "run", run)
    flags = ["--unlock"] if phase == "unlock" else []
    code, result = _remove(capsys, root, other, "--yes", *flags)
    assert code == 6, result
    assert not record.exists() and result["data"]["result"]["changed"] is True
    if phase == "unlock":
        assert removals == [] and other.is_dir()
        assert result["effects"] == [
            {"kind": "git.worktree.unlock", "status": "succeeded", "target": str(other)},
            {"kind": "git.worktree.remove", "status": "not_attempted", "target": str(other)},
        ]
    else:
        assert len(removals) == 1 and not other.exists()
        assert result["effects"] == [{"kind": "git.worktree.remove", "status": "succeeded", "target": str(other)}]


def _after_unlock(monkeypatch: pytest.MonkeyPatch, root: Path, change) -> list[str]:
    """Run `change()` right after a successful native unlock; record attempted removals."""
    native_run = subprocess.run
    removals: list[str] = []

    def run(argv, *args, **kwargs):
        if tuple(argv[:5]) == ("git", "-C", str(root), "worktree", "remove"):
            removals.append(str(argv[-1]))
        result = native_run(argv, *args, **kwargs)
        if tuple(argv[:5]) == ("git", "-C", str(root), "worktree", "unlock"):
            assert result.returncode == 0
            change()
        return result

    monkeypatch.setattr(subprocess, "run", run)
    return removals


def _unlocked_then_not_removed(other: Path) -> list[dict[str, str]]:
    return [
        {"kind": "git.worktree.unlock", "status": "succeeded", "target": str(other)},
        {"kind": "git.worktree.remove", "status": "not_attempted", "target": str(other)},
    ]


def test_remove_rechecks_target_changes_after_unlock_before_attempting_removal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other = linked_workspace(tmp_path, monkeypatch, capsys)
    subprocess.run(["git", "-C", str(root), "worktree", "lock", str(other)], check=True, capture_output=True)
    actor_file = other / "actor-work.txt"
    removals = _after_unlock(monkeypatch, root, lambda: actor_file.write_bytes(b"new work after unlock"))
    code, result = _remove(capsys, root, other, "--unlock", "--yes")
    assert code == 6, result
    assert removals == [] and actor_file.read_bytes() == b"new work after unlock"
    assert result["effects"] == _unlocked_then_not_removed(other)


def test_remove_preserves_a_target_that_changes_branch_after_unlock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other = linked_workspace(tmp_path, monkeypatch, capsys)
    subprocess.run(["git", "-C", str(root), "worktree", "lock", str(other)], check=True, capture_output=True)
    native_run = subprocess.run
    removals = _after_unlock(
        monkeypatch,
        root,
        lambda: native_run(
            ["git", "-C", str(other), "checkout", "-qb", "actor-branch"], check=True, capture_output=True
        ),
    )
    code, result = _remove(capsys, root, other, "--unlock", "--yes")
    assert code == 6, result
    assert removals == [] and other.is_dir()
    assert result["effects"] == _unlocked_then_not_removed(other)
    assert (
        native_run(["git", "-C", str(other), "symbolic-ref", "--short", "HEAD"], check=True, capture_output=True).stdout
        == b"actor-branch\n"
    )


def test_remove_preserves_a_same_path_replacement_after_unlock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other = linked_workspace(tmp_path, monkeypatch, capsys)
    subprocess.run(["git", "-C", str(root), "worktree", "lock", str(other)], check=True, capture_output=True)
    parked = tmp_path / "parked"
    original_identity = other.stat().st_ino

    def change() -> None:
        other.rename(parked)
        shutil.copytree(parked, other, symlinks=True)
        assert other.stat().st_ino != original_identity

    removals = _after_unlock(monkeypatch, root, change)
    code, result = _remove(capsys, root, other, "--unlock", "--yes")
    assert code == 6, result
    assert removals == [] and other.is_dir() and parked.is_dir()
    assert parked.stat().st_ino == original_identity
    assert result["effects"] == _unlocked_then_not_removed(other)


@pytest.mark.parametrize("dry_run", [False, True])
def test_remove_rechecks_the_target_before_unlock_or_preview(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], dry_run: bool
) -> None:
    root, other = linked_workspace(tmp_path, monkeypatch, capsys)
    subprocess.run(["git", "-C", str(root), "worktree", "lock", str(other)], check=True, capture_output=True)
    native_run = subprocess.run
    mutations: list[str] = []
    changed = False

    def run(argv, *args, **kwargs):
        nonlocal changed
        if tuple(argv[:4]) == ("git", "-C", str(root), "worktree") and argv[4] in ("unlock", "remove"):
            mutations.append(argv[4])
        result = native_run(argv, *args, **kwargs)
        # the first target listing happens after the target was resolved and before any mutation
        if not changed and tuple(argv[:4]) == ("git", "-C", str(other), "ls-files"):
            changed = True
            native_run(["git", "-C", str(other), "checkout", "-qb", "actor-branch"], check=True, capture_output=True)
        return result

    monkeypatch.setattr(subprocess, "run", run)
    flags = ["--dry-run"] if dry_run else []
    code, result = _remove(capsys, root, other, "--unlock", "--yes", *flags)
    assert code == 3, result
    assert changed and mutations == [] and result["effects"] == [] and other.is_dir()
    assert (
        native_run(["git", "-C", str(other), "symbolic-ref", "--short", "HEAD"], check=True, capture_output=True).stdout
        == b"actor-branch\n"
    )
    assert (
        b"locked"
        in native_run(
            ["git", "-C", str(root), "worktree", "list", "--porcelain", "-z"], check=True, capture_output=True
        ).stdout
    )


def test_remove_confirms_an_unlock_that_finishes_before_a_native_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other = linked_workspace(tmp_path, monkeypatch, capsys)
    subprocess.run(["git", "-C", str(root), "worktree", "lock", str(other)], check=True, capture_output=True)
    native_run = subprocess.run
    removals: list[str] = []
    stderr = b"fatal: error after unlock\noriginal second line\n"

    def run(argv, *args, **kwargs):
        if tuple(argv[:5]) == ("git", "-C", str(root), "worktree", "remove"):
            removals.append(str(argv[-1]))
        result = native_run(argv, *args, **kwargs)
        if tuple(argv[:5]) == ("git", "-C", str(root), "worktree", "unlock"):
            assert result.returncode == 0
            return subprocess.CompletedProcess(argv, 128, result.stdout, stderr)
        return result

    monkeypatch.setattr(subprocess, "run", run)
    code, result = _remove(capsys, root, other, "--unlock", "--yes")
    assert code == 6, result
    assert removals == [] and other.is_dir() and result["data"]["result"]["changed"] is True
    assert result["data"]["result"]["observed"]["locked"] is False
    assert result["effects"] == _unlocked_then_not_removed(other)
    assert result["error"]["details"]["git"]["stderr"] == stderr.decode()
    assert result["error"]["details"]["git"]["returncode"] == 128


def test_remove_keeps_confirmed_effects_if_the_target_handle_close_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other = linked_workspace(tmp_path, monkeypatch, capsys)
    before = other.stat()
    target_identity = (before.st_dev, before.st_ino)
    native_close = os.close
    injected = False

    def close(descriptor: int) -> None:
        nonlocal injected
        observed = os.fstat(descriptor)
        native_close(descriptor)
        if not injected and not other.exists() and (observed.st_dev, observed.st_ino) == target_identity:
            injected = True
            raise OSError(errno.EIO, "fixture target handle close failure")

    monkeypatch.setattr(os, "close", close)
    code, result = _remove(capsys, root, other, "--yes")
    assert code == 6, result
    assert injected and not other.exists() and result["data"]["result"]["changed"] is True
    assert result["data"]["result"]["observed"]["removed"] is True
    assert result["effects"] == [{"kind": "git.worktree.remove", "status": "succeeded", "target": str(other)}]
    assert "fixture target handle close failure" in result["error"]["message"]


@pytest.mark.parametrize("phase", ["unlock", "remove"])
@pytest.mark.parametrize("fault", ["start", "timeout", "signal"])
def test_remove_reports_git_process_failure_without_retry_or_rollback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], phase: str, fault: str
) -> None:
    root, other = linked_workspace(tmp_path, monkeypatch, capsys)
    if phase == "unlock":
        subprocess.run(["git", "-C", str(root), "worktree", "lock", str(other)], check=True, capture_output=True)
    native_run = subprocess.run
    calls: list[str] = []
    stderr = b"native interrupted operation\nsecond line retained\n"
    stdout = b"native output retained\n"

    def run(argv, *args, **kwargs):
        if tuple(argv[:4]) == ("git", "-C", str(root), "worktree") and argv[4] in ("unlock", "remove"):
            calls.append(argv[4])
            assert argv[4] == phase
            if fault == "start":
                raise FileNotFoundError(errno.ENOENT, "fixture Git process could not start")
            if fault == "timeout":
                raise subprocess.TimeoutExpired(argv, kwargs["timeout"], output=stdout, stderr=stderr)
            return subprocess.CompletedProcess(argv, -15, stdout, stderr)
        return native_run(argv, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", run)
    flags = ["--unlock"] if phase == "unlock" else []
    code, result = _remove(capsys, root, other, "--yes", *flags)
    assert code == (5 if fault == "start" else 6), result
    expected = [
        {"kind": f"git.worktree.{phase}", "status": "failed" if fault == "start" else "unknown", "target": str(other)}
    ]
    if phase == "unlock":
        expected.append({"kind": "git.worktree.remove", "status": "not_attempted", "target": str(other)})
    assert calls == [phase] and other.is_dir() and result["effects"] == expected
    assert result["data"]["result"]["changed"] is False
    details = result["error"]["details"]["git"]
    assert details["timed_out"] is (fault == "timeout")
    assert details["returncode"] == (-15 if fault == "signal" else None)
    if fault != "start":
        assert details["stderr"] == stderr.decode() and details["stdout"] == stdout.decode()
        assert result["recovery"]["can_resume"] is False and result["recovery"]["can_rollback"] is False


def test_remove_text_preserves_the_native_git_error_verbatim(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other = linked_workspace(tmp_path, monkeypatch, capsys)
    native_run = subprocess.run
    stderr = b"fatal: could not remove native target\nnative detail second line\n"

    def run(argv, *args, **kwargs):
        if tuple(argv[:5]) == ("git", "-C", str(root), "worktree", "remove"):
            return subprocess.CompletedProcess(argv, 128, b"", stderr)
        return native_run(argv, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", run)
    assert main(["--project", str(root), "worktree", "remove", str(other), "--yes", "--color", "never"]) == 6
    output = capsys.readouterr()
    assert stderr.decode() in output.err and other.is_dir()
