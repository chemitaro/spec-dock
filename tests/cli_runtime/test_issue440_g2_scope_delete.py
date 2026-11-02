"""Canonical `scope delete` fail-closed, backup, removal and selection contracts kept from legacy tests (iss-00440).

Replaces the common-contract tests of tests/cli_runtime/test_issue413_scope_delete.py and
tests/cli_runtime/test_scope_delete_commands_vnext.py, which deleted nested `.meta.json` subtrees. Canonical
`scope delete` shares the backup (`tree_backup`), removal (`tree_removal`) and selection (`WorkTargetStore`)
adapters with them, so their fail-closed paths are checked here on the flat catalog.
"""

from __future__ import annotations

import io
import json
import os
import stat
import sys
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.cli import main
from tests.support.canonical_writes import WriteWorld

if TYPE_CHECKING:
    from pathlib import Path

LEAF = "00000-00999/iss-00003"
EPIC = "00000-00999/epic-00002"


class TerminalAnswer(io.StringIO):
    def isatty(self) -> bool:
        return True


def _world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> WriteWorld:
    world = WriteWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "plan")
    world.scope("epic", 2, "core", parent=1)
    world.scope("issue", 3, "leaf", parent=2)
    world.scope("epic", 4, "spare", parent=1)
    return world


def _selected(world: WriteWorld, scope_id: str = "iss-00003", number: int = 3, checkout: Path | None = None) -> Path:
    world.select(scope_id, number, checkout=checkout)
    return next(((checkout or world.main) / "spec-dock/.agent/work-target").iterdir())


def _token(record: Path) -> str:
    return record.name[len("target-") : -len(".json")]


def _files(directory: Path) -> dict[str, bytes]:
    return {
        path.relative_to(directory).as_posix(): path.read_bytes() for path in directory.rglob("*") if path.is_file()
    }


def _delete(world: WriteWorld, target: str, backup: Path, *extra: str) -> tuple[int, dict[str, Any]]:
    return world.run("scope", "delete", target, "--backup-dir", str(backup), *extra)


def _effects(payload: dict[str, Any]) -> list[tuple[str, str]]:
    return [(effect["kind"], effect["status"]) for effect in payload["effects"]]


# Confirmation, dry run and plan


def test_scope_delete_cli_requires_confirmation_and_previews_without_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    leaf = world.find("iss-00003")
    before = _files(leaf)
    backup = tmp_path / "delete-backup"
    code, payload = _delete(world, "iss-00003", backup)
    assert (code, payload["error"]["code"], payload["effects"]) == (3, "CONFIRMATION_REQUIRED", []), payload
    code, payload = _delete(world, "iss-00003", backup, "--dry-run")
    assert (code, payload["status"]) == (0, "planned"), payload
    assert _files(leaf) == before and not backup.exists() and world.writes() == []
    code, payload = _delete(world, "iss-00003", backup, "--yes")
    assert (code, payload["status"]) == (0, "succeeded"), payload
    assert not leaf.exists() and _files(backup / LEAF) == before
    code, payload = _delete(world, "epic-00004", backup, "--yes")
    assert (code, payload["error"]["code"], payload["effects"]) == (3, "PRECONDITION_FAILED", []), payload
    assert "backup destination already exists" in payload["error"]["message"]
    assert world.find("epic-00004").is_dir()


@pytest.mark.parametrize("answer", ["yes\n", "no\n"])
def test_scope_delete_accepts_or_declines_terminal_confirmation_after_showing_its_plan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], answer: str
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    leaf = world.find("iss-00003")
    before = _files(leaf)
    backup = tmp_path / "delete-backup"
    monkeypatch.setattr(sys, "stdin", TerminalAnswer(answer))
    code = main(["--project", str(world.main), "scope", "delete", "iss-00003", "--backup-dir", str(backup)])
    output = capsys.readouterr()
    assert "Confirm [yes/no]" in output.err and "iss-00003" in output.err and str(backup) in output.err
    if answer == "yes\n":
        assert code == 0, output
        assert not leaf.exists() and _files(backup / LEAF) == before
    else:
        assert code == 3, output
        assert "CONFIRMATION_DECLINED" in output.err
        assert _files(leaf) == before and not backup.exists() and world.writes() == []


def test_recursive_delete_dry_run_lists_the_plan_without_backup_or_workspace_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    before = _files(world.catalog)
    backup = tmp_path / "delete-backup"
    code, payload = _delete(world, "epic-00002", backup, "--recursive", "--dry-run")
    assert (code, payload["status"]) == (0, "planned"), payload
    data = payload["data"]["result"]
    assert data["can_apply"] is True and data["blockers"] == []
    assert data["removed_ids"] == [] and data["changed_paths"] == [] and data["remaining_paths"] == [EPIC, LEAF]
    assert data["backup_path"] == str(backup)
    # Canonical delete also plans the GitHub detachment steps after the directory removals.
    assert [(effect["kind"], effect["target"]) for effect in payload["effects"]][:3] == [
        ("backup", str(backup)),
        ("scope.delete", EPIC),
        ("scope.delete", LEAF),
    ]
    assert all(effect["status"] == "planned" for effect in payload["effects"])
    assert _files(world.catalog) == before and not backup.exists()
    assert world.writes() == [] and world.changesets() == []


def test_delete_dry_run_lists_dependency_edit_and_captured_clear_without_writing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.edit(lambda fake: fake.block(4, by=3))
    record = _selected(world)
    selected, before = record.read_bytes(), _files(world.catalog)
    backup = tmp_path / "delete-backup"
    code, payload = _delete(
        world, "@epic", backup, "--recursive", "--clear-active", "--detach-dependencies", "--dry-run"
    )
    assert (code, payload["status"]) == (0, "planned"), payload
    assert [(effect["kind"], effect["target"]) for effect in payload["effects"]][:5] == [
        ("backup", str(backup)),
        ("selection.clear", _token(record)),
        ("scope.delete", EPIC),
        ("scope.delete", LEAF),
        ("dependency-edge", "epic-00004->iss-00003"),
    ]
    assert all(effect["status"] == "planned" for effect in payload["effects"])
    data = payload["data"]["result"]
    assert data["can_apply"] is True and data["removed_ids"] == [] and data["changed_paths"] == []
    assert record.read_bytes() == selected and _files(world.catalog) == before and not backup.exists()
    assert world.writes() == [] and world.changesets() == []


# Fail-closed refusals before the backup


@pytest.mark.skipif(os.name != "posix", reason="native POSIX FIFO boundary")
def test_scope_delete_refuses_a_fifo_before_creating_backup_without_blocking(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    leaf = world.find("iss-00003")
    fifo = leaf / "unsupported-fifo"
    os.mkfifo(fifo)
    before = _files(leaf)
    backup = tmp_path / "delete-backup"
    # In process: a blocking open of the FIFO would hang the test run, which then fails on its timeout.
    code, payload = _delete(world, "iss-00003", backup, "--yes")
    assert (code, payload["error"]["code"], payload["effects"]) == (3, "PRECONDITION_FAILED", []), payload
    assert not backup.exists()
    assert stat.S_ISFIFO(fifo.lstat().st_mode) and _files(leaf) == before
    assert world.writes() == [] and world.changesets() == []


@pytest.mark.parametrize("mode", [("--yes",), ("--dry-run",)])
def test_delete_refuses_a_backup_path_that_traverses_into_git_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], mode: tuple[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    before = _files(world.find("iss-00003"))
    (world.main / "scratch").mkdir()
    backup = world.main / "scratch/../.git/new-backup"
    code, payload = _delete(world, "iss-00003", backup, *mode)
    assert (code, payload["error"]["code"], payload["effects"]) == (3, "PRECONDITION_FAILED", []), payload
    assert _files(world.find("iss-00003")) == before and not (world.main / ".git/new-backup").exists()
    assert world.writes() == []


def test_delete_dry_run_refuses_a_redirected_backup_parent_without_writing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    before = _files(world.find("iss-00003"))
    external = tmp_path / "external"
    external.mkdir()
    alias = tmp_path / "backup-alias"
    alias.symlink_to(external, target_is_directory=True)
    code, payload = _delete(world, "iss-00003", alias / "new-backup", "--dry-run")
    assert (code, payload["error"]["code"], payload["effects"]) == (3, "PRECONDITION_FAILED", []), payload
    assert list(external.iterdir()) == [] and alias.is_symlink()
    assert _files(world.find("iss-00003")) == before


def test_recursive_delete_requires_clear_active_for_the_captured_direct_descendant(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    record = _selected(world)
    selected, before = record.read_bytes(), _files(world.catalog)
    backup = tmp_path / "delete-backup"
    code, payload = _delete(world, "@epic", backup, "--recursive", "--yes")
    assert (code, payload["effects"]) == (3, []), payload
    assert "CLEAR_ACTIVE_REQUIRED" in payload["error"]["message"]
    assert record.read_bytes() == selected and _files(world.catalog) == before and not backup.exists()
    assert world.writes() == []


def test_delete_refuses_an_unreadable_direct_selection_without_assuming_it_is_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    record = _selected(world)
    record.write_bytes(b"broken direct selection")
    before = _files(world.catalog)
    backup = tmp_path / "delete-backup"
    code, payload = _delete(world, "iss-00003", backup, "--yes")
    assert (code, payload["effects"]) == (3, []), payload
    assert record.read_bytes() == b"broken direct selection" and _files(world.catalog) == before
    assert not backup.exists() and world.writes() == []


@pytest.mark.parametrize("guard", [("--expect-backend", "local"), ("--expect-current", "@epic")])
def test_delete_guard_mismatch_stops_before_backup_or_clear(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], guard: tuple[str, str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    record = _selected(world)
    selected, before = record.read_bytes(), _files(world.catalog)
    backup = tmp_path / "delete-backup"
    code, payload = _delete(world, "@epic", backup, "--recursive", "--clear-active", *guard, "--yes")
    assert (code, payload["error"]["code"], payload["effects"]) == (3, "PRECONDITION_FAILED", []), payload
    assert record.read_bytes() == selected and _files(world.catalog) == before and not backup.exists()
    assert world.writes() == []


# Backup content and successful removal


@pytest.mark.skipif(os.name != "posix", reason="native POSIX mode and symlink boundary")
def test_scope_delete_backup_preserves_modes_and_link_bytes_without_following_the_link(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    leaf = world.find("iss-00003")
    external = tmp_path / "external.txt"
    external.write_bytes(b"external bytes stay unchanged")
    document = leaf / "design.md"
    document.write_bytes(b"scope-owned document")
    document.chmod(0o640)
    (leaf / "external-link").symlink_to(external)
    leaf.chmod(0o750)
    backup = tmp_path / "delete-backup"
    code, payload = _delete(world, "iss-00003", backup, "--yes")
    assert code == 0, payload
    copied = backup / LEAF
    assert stat.S_IMODE(copied.stat().st_mode) == 0o750
    assert stat.S_IMODE((copied / "design.md").stat().st_mode) == 0o640
    assert (copied / "design.md").read_bytes() == b"scope-owned document"
    assert (copied / "external-link").is_symlink() and (copied / "external-link").readlink() == external
    assert external.read_bytes() == b"external bytes stay unchanged" and not leaf.exists()


@pytest.mark.skipif(os.name != "posix", reason="native POSIX directory flock boundary")
def test_scope_delete_proceeds_while_start_exclusion_is_held(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from spec_dock.runtime.infra.start_lock import StartLock

    world = _world(tmp_path, monkeypatch, capsys)
    before = _files(world.find("iss-00003"))
    backup = tmp_path / "delete-backup"
    with StartLock(world.main / ".git", timeout=0):
        code, payload = _delete(world, "iss-00003", backup, "--yes")
    assert code == 0, payload
    assert payload["data"]["result"]["removed_ids"] == ["iss-00003"]
    assert not (world.catalog / LEAF).exists() and _files(backup / LEAF) == before


def test_delete_backs_up_and_clears_only_the_captured_direct_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.edit(lambda fake: fake.block(4, by=3))
    record = _selected(world)
    selected = record.read_bytes()
    backup = tmp_path / "delete-backup"
    code, payload = _delete(world, "@epic", backup, "--recursive", "--clear-active", "--detach-dependencies", "--yes")
    assert code == 0, payload
    data = payload["data"]["result"]
    assert data["removed_ids"] == ["epic-00002", "iss-00003"] and data["remaining_paths"] == []
    assert [(effect["kind"], effect["status"], effect["target"]) for effect in payload["effects"]][:4] == [
        ("backup", "succeeded", str(backup)),
        ("selection.clear", "succeeded", _token(record)),
        ("scope.delete", "succeeded", EPIC),
        ("scope.delete", "succeeded", LEAF),
    ]
    assert (backup / record.relative_to(world.main)).read_bytes() == selected
    assert not record.exists() and not (world.catalog / EPIC).exists()
    assert world.fake().issue(4).blocked_by == []


def test_delete_preserves_another_worktree_record_which_then_reads_as_stale(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    linked = world.worktree("linked")
    own = _selected(world)
    other = _selected(world, checkout=linked)
    before = other.read_bytes()
    code, payload = _delete(world, "iss-00003", tmp_path / "delete-backup", "--clear-active", "--yes")
    assert code == 0, payload
    assert not own.exists() and other.read_bytes() == before and not (world.catalog / LEAF).exists()
    code, payload = world.run("workspace", "sync")
    row = next(item for item in payload["data"]["worktrees"] if item["path"] == str(linked))
    assert row["selection"]["status"] == "stale" and row["selection"]["scope_id"] == "iss-00003", row
    assert other.read_bytes() == before


def test_delete_does_not_clear_a_new_token_after_the_captured_token_was_removed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    record = _selected(world)
    original = record.read_bytes()
    replacement = record.with_name("target-" + "b" * 32 + ".json")
    payload = json.loads(original)
    payload.update(scope_id="epic-00002", github_ref="gh:example/repo#2")
    new_bytes = json.dumps(payload).encode()
    real_unlink = os.unlink
    raced: list[bool] = []

    def unlink(path: Any, **kwargs: Any) -> None:
        if path == record.name and not raced:
            raced.append(True)
            real_unlink(path, **kwargs)
            replacement.write_bytes(new_bytes)
        real_unlink(path, **kwargs)

    monkeypatch.setattr(os, "unlink", unlink)
    backup = tmp_path / "delete-backup"
    code, result = _delete(world, "iss-00003", backup, "--clear-active", "--yes")
    assert raced and code == 0, result
    assert replacement.read_bytes() == new_bytes and not (world.catalog / LEAF).exists()
    assert result["effects"][1] == {"kind": "selection.clear", "status": "unchanged", "target": _token(record)}
    assert (backup / record.relative_to(world.main)).read_bytes() == original


# Failures during the backup


def _same(descriptor: int, path: Path) -> bool:
    if not path.exists():
        return False
    left, right = os.fstat(descriptor), path.lstat()
    return (left.st_dev, left.st_ino) == (right.st_dev, right.st_ino)


def test_incomplete_backup_is_retained_and_never_allows_subtree_deletion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    leaf = world.find("iss-00003")
    before = _files(leaf)
    backup = tmp_path / "delete-backup"
    real_open = os.open
    failed: list[bool] = []

    def open_file(path: Any, flags: int, mode: int = 0o777, **kwargs: Any) -> int:
        parent = kwargs.get("dir_fd")
        if path == "plan.md" and flags & os.O_CREAT and parent is not None and _same(parent, backup / LEAF):
            failed.append(True)
            raise OSError("fixture: backup destination write failed")
        return real_open(path, flags, mode, **kwargs)

    monkeypatch.setattr(os, "open", open_file)
    code, payload = _delete(world, "iss-00003", backup, "--yes")
    assert failed and (code, payload["status"]) == (6, "partial"), payload
    assert backup.is_dir() and _files(leaf) == before
    assert payload["data"]["result"]["removed_ids"] == []
    assert _effects(payload)[:2] == [("backup", "unknown"), ("scope.delete", "not_attempted")]
    assert world.changesets() == [] and world.writes() == []


def test_redirected_backup_root_never_writes_through_the_external_alias(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    leaf = world.find("iss-00003")
    before = _files(leaf)
    backup = tmp_path / "delete-backup"
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "preserve.bin").write_bytes(b"external bytes")
    real_mkdir = os.mkdir
    redirected: list[bool] = []

    def mkdir(path: Any, mode: int = 0o777, **kwargs: Any) -> None:
        real_mkdir(path, mode, **kwargs)
        if path == backup.name and not redirected:
            redirected.append(True)
            backup.rename(tmp_path / "moved-backup")
            backup.symlink_to(outside, target_is_directory=True)

    monkeypatch.setattr(os, "mkdir", mkdir)
    code, payload = _delete(world, "iss-00003", backup, "--yes")
    assert redirected and (code, payload["status"]) == (6, "partial"), payload
    assert _files(leaf) == before and backup.is_symlink()
    assert sorted(path.name for path in outside.iterdir()) == ["preserve.bin"]
    assert _effects(payload)[:2] == [("backup", "unknown"), ("scope.delete", "not_attempted")]


def test_uncertain_backup_directory_creation_keeps_the_directory_and_does_not_delete_scope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    leaf = world.find("iss-00003")
    before = _files(leaf)
    backup = tmp_path / "delete-backup"
    real_mkdir = os.mkdir
    injected: list[bool] = []

    def mkdir(path: Any, mode: int = 0o777, **kwargs: Any) -> None:
        real_mkdir(path, mode, **kwargs)
        if path == backup.name and not injected:
            injected.append(True)
            raise OSError("fixture: mkdir outcome unavailable")

    monkeypatch.setattr(os, "mkdir", mkdir)
    code, payload = _delete(world, "iss-00003", backup, "--yes")
    assert injected and (code, payload["status"]) == (6, "partial"), payload
    assert backup.is_dir() and _files(leaf) == before
    assert _effects(payload)[:2] == [("backup", "unknown"), ("scope.delete", "not_attempted")]
    assert payload["data"]["result"]["changed_paths"] == [] and payload["data"]["result"]["removed_ids"] == []


def test_backup_root_redirected_after_open_never_writes_to_the_external_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    leaf = world.find("iss-00003")
    before = _files(leaf)
    backup = tmp_path / "delete-backup"
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "preserve.bin").write_bytes(b"external bytes")
    real_close = os.close
    redirected: list[bool] = []

    def close(descriptor: int) -> None:
        should_redirect = not redirected and _same(descriptor, backup)
        real_close(descriptor)
        if should_redirect:
            redirected.append(True)
            backup.rename(tmp_path / "moved-backup")
            backup.symlink_to(outside, target_is_directory=True)

    monkeypatch.setattr(os, "close", close)
    code, payload = _delete(world, "iss-00003", backup, "--yes")
    assert redirected and (code, payload["status"]) == (6, "partial"), payload
    assert _files(leaf) == before and backup.is_symlink()
    assert sorted(path.name for path in outside.iterdir()) == ["preserve.bin"]
    assert payload["effects"][0] == {"kind": "backup", "status": "unknown", "target": str(backup)}


# Failures after the verified backup


def test_subtree_unlink_with_unknown_outcome_retains_backup_and_reports_the_scope_unknown(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    leaf = world.find("iss-00003")
    before = _files(leaf)
    backup = tmp_path / "delete-backup"
    real_unlink = os.unlink
    calls: list[str] = []

    def unlink(path: Any, **kwargs: Any) -> None:
        real_unlink(path, **kwargs)
        if kwargs.get("dir_fd") is not None and _same(kwargs["dir_fd"], leaf):
            calls.append(path)
            if len(calls) == 2:  # one entry is confirmed removed, the next unlink's outcome is unknown
                raise OSError("fixture: unlink outcome unavailable")

    monkeypatch.setattr(os, "unlink", unlink)
    code, payload = _delete(world, "iss-00003", backup, "--yes")
    assert len(calls) == 2 and (code, payload["status"]) == (6, "partial"), payload
    assert leaf.is_dir() and _files(backup / LEAF) == before
    assert _effects(payload)[:2] == [("backup", "succeeded"), ("scope.delete", "unknown")]
    assert payload["data"]["result"]["removed_ids"] == []
    assert payload["data"]["result"]["remaining_paths"] == [LEAF]
    for name, content in _files(leaf).items():
        assert before[name] == content


def test_subtree_removal_preserves_a_new_file_that_was_not_in_the_verified_backup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    leaf = world.find("iss-00003")
    before = _files(leaf)
    backup = tmp_path / "delete-backup"
    late = leaf / "late.txt"
    real_listdir = os.listdir
    injected: list[bool] = []

    def listdir(path: Any = ".") -> list[str]:
        if isinstance(path, int) and not injected and _same(path, leaf) and (backup / LEAF / "plan.md").exists():
            injected.append(True)
            late.write_bytes(b"actor content without a backup")
        return real_listdir(path)

    monkeypatch.setattr(os, "listdir", listdir)
    code, payload = _delete(world, "iss-00003", backup, "--yes")
    assert injected and (code, payload["status"]) == (6, "partial"), payload
    assert late.read_bytes() == b"actor content without a backup" and not (backup / LEAF / "late.txt").exists()
    assert _files(backup / LEAF) == before
    assert payload["data"]["result"]["removed_ids"] == [] and payload["data"]["result"]["remaining_paths"] == [LEAF]


def test_subtree_removal_preserves_a_file_changed_after_backup_and_before_its_unlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    leaf = world.find("iss-00003")
    document = leaf / "zz-later.txt"  # removed last: entries are removed in name order
    document.write_bytes(b"original document")
    backup = tmp_path / "delete-backup"
    real_unlink = os.unlink
    injected: list[bool] = []

    def unlink(path: Any, **kwargs: Any) -> None:
        real_unlink(path, **kwargs)
        if not injected and kwargs.get("dir_fd") is not None and _same(kwargs["dir_fd"], leaf):
            injected.append(True)
            document.write_bytes(b"actor replacement that must be preserved")

    monkeypatch.setattr(os, "unlink", unlink)
    code, payload = _delete(world, "iss-00003", backup, "--yes")
    assert injected and (code, payload["status"]) == (6, "partial"), payload
    assert document.read_bytes() == b"actor replacement that must be preserved"
    assert (backup / LEAF / "zz-later.txt").read_bytes() == b"original document"
    assert _effects(payload)[:2] == [("backup", "succeeded"), ("scope.delete", "unknown")]
    assert payload["data"]["result"]["removed_ids"] == [] and payload["data"]["result"]["remaining_paths"] == [LEAF]


def test_delete_preserves_a_changed_direct_record_and_the_subtree_after_backup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    record = _selected(world)
    before = record.read_bytes()
    actor = {**json.loads(before), "selected_branch": "actor-branch"}
    backup = tmp_path / "delete-backup"
    real_mkdir = os.mkdir
    changed: list[bool] = []

    def mkdir(path: Any, mode: int = 0o777, **kwargs: Any) -> None:
        real_mkdir(path, mode, **kwargs)
        if path == backup.name and not changed:
            changed.append(True)
            record.write_text(json.dumps(actor))

    monkeypatch.setattr(os, "mkdir", mkdir)
    code, payload = _delete(world, "iss-00003", backup, "--clear-active", "--yes")
    assert changed and (code, payload["status"]) == (6, "partial"), payload
    assert json.loads(record.read_bytes()) == actor and (world.catalog / LEAF).is_dir()
    assert (backup / record.relative_to(world.main)).read_bytes() == before
    assert payload["data"]["result"]["removed_ids"] == [] and payload["data"]["result"]["changed_paths"] == []
    assert payload["effects"][:3] == [
        {"kind": "backup", "status": "succeeded", "target": str(backup)},
        {"kind": "selection.clear", "status": "failed", "target": _token(record)},
        {"kind": "scope.delete", "status": "not_attempted", "target": LEAF},
    ]
    assert world.writes() == []
