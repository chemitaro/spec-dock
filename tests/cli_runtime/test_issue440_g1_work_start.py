"""Public `work start` keeps Git checkout and publishes only a local direct target, in canonical mode.

Replaces the common-contract tests of tests/cli_runtime/test_issue413_work_start.py (iss-00440). Canonical start
reuses the legacy StartLock, record store and inventory checks; it reads the Scope from the GitHub structure, names
a new branch after the ID, and after the selection adds `active.link` and in-progress follow-ups that never change
the result. Assertions on the effect order therefore look only at the Git and selection effects.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.infra.start_lock import StartLock
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.canonical_repo import add_worktree, git
from tests.support.legacy_contracts_g1 import (
    chain_world,
    commit,
    raw,
    records,
    run_err,
    run_process,
    select_record,
    start_effects,
    token,
)

if TYPE_CHECKING:
    from pathlib import Path

    from tests.support.canonical_writes import WriteWorld


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> WriteWorld:
    return chain_world(tmp_path, monkeypatch, capsys, write=True, sibling=True)  # type: ignore[return-value]


def _targets(world: WriteWorld) -> Path:
    return world.main / "spec-dock/.agent/work-target"


def _hook(world: WriteWorld, body: str) -> None:
    hook = world.main / ".git/hooks/post-checkout"
    hook.write_text("#!/bin/sh\n" + body)
    hook.chmod(0o755)


@pytest.mark.skipif(os.name != "posix", reason="native POSIX unlink and Start lock boundary")
def test_start_accepts_a_parallel_clear_of_the_same_captured_token_before_replacement(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    code, first = world.run("work", "start", "iss-00003", "--branch", "first", "--base", "HEAD")
    assert code == 0, first
    old_token = first["data"]["selection_token"]
    original_unlink = os.unlink
    cleared: list[dict[str, object]] = []

    def unlink(path: str, *, dir_fd: int | None = None) -> None:
        if path == f"target-{old_token}.json" and not cleared:
            completed = run_process(world, "active", "clear", "--from", "iss-00003", timeout=30)
            assert completed.returncode == 0, completed.stdout + completed.stderr
            cleared.append(json.loads(completed.stdout))
        original_unlink(path, dir_fd=dir_fd)

    monkeypatch.setattr(os, "unlink", unlink)
    code, result = world.run("work", "start", "iss-00003", "--branch", "second", "--base", "HEAD", "--switch-active")
    assert code == 0, result
    assert len(cleared) == 1 and cleared[0]["status"] == "succeeded"
    assert result["status"] == "succeeded" and result["data"]["started"] is True
    assert start_effects(result["effects"])[-2] == {
        "kind": "selection.clear",
        "status": "unchanged",
        "target": "iss-00003",
    }
    found = records(world.main)
    assert [path.name for path in found] == [f"target-{result['data']['selection_token']}.json"]
    assert result["data"]["selection_token"] != old_token
    assert json.loads(found[0].read_bytes())["selected_branch"] == "second"


@pytest.mark.parametrize("dry_run", [False, True])
@pytest.mark.parametrize("missing", ["platform", "native-symbol"])
def test_start_missing_publication_primitive_stops_before_git_effects(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch, dry_run: bool, missing: str
) -> None:
    from types import SimpleNamespace

    from spec_dock.runtime.infra import json_store

    before = tree_digest(world.main)
    if missing == "platform":
        monkeypatch.setattr(json_store, "sys", SimpleNamespace(platform="unavailable"))
    else:
        monkeypatch.setattr(json_store, "ctypes", SimpleNamespace(CDLL=lambda *args, **kwargs: SimpleNamespace()))
    code, result, err = run_err(
        world,
        "work",
        "start",
        "iss-00003",
        "--branch",
        "unsupported-publication",
        "--base",
        "HEAD",
        *(["--dry-run"] if dry_run else []),
    )
    assert code == 5, result
    assert result["status"] == "failed" and result["data"]["started"] is False
    assert result["data"]["branch_before"] == result["data"]["branch_after"] == "main"
    assert result["data"]["selection_token"] is None and result["effects"] == []
    assert "safe JSON rename is unavailable" in result["error"]["message"]
    assert err == "" and tree_digest(world.main) == before
    assert not (world.main / "spec-dock/.agent").exists() and not (world.main / ".git/spec-dock").exists()
    assert world.writes() == []


@pytest.mark.parametrize("dry_run", [False, True])
def test_start_known_unsupported_publication_preserves_captured_selection(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch, dry_run: bool
) -> None:
    from types import SimpleNamespace

    from spec_dock.runtime.infra import json_store

    record = select_record(world, "iss-00003", 3)
    before = tree_digest(world.main)
    monkeypatch.setattr(json_store, "ctypes", SimpleNamespace(CDLL=lambda *args, **kwargs: SimpleNamespace()))
    code, result = world.run(
        "work",
        "start",
        "iss-00003",
        "--branch",
        "replacement",
        "--base",
        "HEAD",
        *(["--dry-run"] if dry_run else []),
    )
    assert code == 5, result
    assert result["status"] == "failed" and result["effects"] == []
    assert result["data"]["started"] is False and result["data"]["branch_after"] == "main"
    assert record.is_file() and tree_digest(world.main) == before


@pytest.mark.parametrize("dry_run", [False, True])
def test_unchanged_start_does_not_require_a_publication_primitive(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch, dry_run: bool
) -> None:
    from types import SimpleNamespace

    from spec_dock.runtime.infra import json_store

    record = select_record(world, "iss-00003", 3)
    before = record.read_bytes()
    # A first unchanged start puts the canonical follow-ups in place (links, registry, in-progress mark), so the
    # second one changes nothing at all, as the legacy unchanged start did.
    code, result = world.run("work", "start", "iss-00003", "--branch", "main")
    assert (code, result["data"]["selection_token"]) == (0, token(record)), result
    digest = tree_digest(world.main)
    monkeypatch.setattr(json_store, "ctypes", SimpleNamespace(CDLL=lambda *args, **kwargs: SimpleNamespace()))
    code, result = world.run("work", "start", "iss-00003", "--branch", "main", *(["--dry-run"] if dry_run else []))
    assert code == 0, result
    assert result["status"] == ("planned" if dry_run else "unchanged"), result
    if not dry_run:
        assert result["data"]["selection_token"] == token(record) and start_effects(result["effects"]) == []
        assert {effect["status"] for effect in result["effects"]} <= {"unchanged"}
    assert tree_digest(world.main) == digest
    assert record.read_bytes() == before and records(world.main) == [record]


def test_start_current_branch_skips_checkout_and_its_hook(world: WriteWorld, tmp_path: Path) -> None:
    marker = tmp_path / "hook-was-run"
    _hook(world, f"touch {shlex.quote(str(marker))}\n")
    code, result = world.run("work", "start", "iss-00003", "--branch", "main")
    assert code == 0, result
    assert not marker.exists()
    assert result["data"]["started"] is True
    assert next(effect for effect in result["effects"] if effect["kind"] == "git.checkout")["status"] == "unchanged"


def test_noop_checkout_does_not_make_prepublication_failure_partial(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    real_open = os.open

    def opening(path, *args, **kwargs):
        if isinstance(path, str) and path.startswith(".stage-"):
            raise OSError("fixture stage creation refused")
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(os, "open", opening)
    code, result = world.run("work", "start", "iss-00003", "--branch", "main")
    assert code == 5, result
    assert result["status"] == "failed"
    assert result["data"]["started"] is False
    assert {effect["status"] for effect in result["effects"]} <= {"unchanged", "failed", "not_attempted"}
    assert result["data"]["selection_token"] is None


@pytest.mark.parametrize("tracked", [True, False])
def test_start_stops_before_selection_replacement_when_checkout_hook_dirties_worktree(
    world: WriteWorld, tracked: bool
) -> None:
    note = world.main / "notes.txt"
    if tracked:
        note.write_text("before\n")
        commit(world.main, "note", "notes.txt")
    code, first = world.run("work", "start", "iss-00003", "--branch", "main")
    assert code == 0, first
    old_record = _targets(world) / f"target-{first['data']['selection_token']}.json"
    before = old_record.read_bytes()
    _hook(world, f"printf 'after\\n' > {shlex.quote(str(note))}\n")
    code, result = world.run("work", "start", "iss-00003", "--base", "HEAD", "--branch", "next")
    assert code == 6, result
    assert result["data"]["started"] is False
    assert result["error"]["code"] == "WORKTREE_CHANGED"
    assert next(effect for effect in result["effects"] if effect["kind"] == "git.checkout")["status"] == "succeeded"
    assert (
        next(effect for effect in result["effects"] if effect["kind"] == "selection.clear")["status"] == "not_attempted"
    )
    assert old_record.read_bytes() == before
    assert records(world.main) == [old_record]
    assert git(world.main, "branch", "--show-current") == "next"


def test_start_publication_unknown_has_no_confirmed_selection_token(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    directory = _targets(world)
    real_fsync = os.fsync

    def syncing(fd):
        if (
            directory.exists()
            and os.fstat(fd).st_ino == directory.stat().st_ino
            and list(directory.glob("target-*.json"))
        ):
            raise OSError("fixture publication sync failure")
        real_fsync(fd)

    monkeypatch.setattr(os, "fsync", syncing)
    code, result = world.run("work", "start", "iss-00003", "--branch", "main")
    assert code == 6, result
    assert result["data"]["started"] is False
    assert result["error"]["code"] == "SELECTION_PUBLICATION_UNKNOWN"
    assert result["data"]["selection_token"] is None
    assert next(effect for effect in result["effects"] if effect["kind"] == "selection.publish")["status"] == "unknown"
    assert len(list(directory.glob("target-*.json"))) == 1


def test_start_retained_stage_is_a_partial_publication_even_when_git_is_unchanged(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    directory = _targets(world)
    real_fsync = os.fsync

    def syncing(descriptor):
        if directory.exists() and any(
            path.stat().st_ino == os.fstat(descriptor).st_ino for path in directory.glob(".stage-*")
        ):
            raise OSError("fixture staged record sync failed")
        return real_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", syncing)
    code, result = world.run("work", "start", "iss-00003", "--branch", "main")
    assert code == 6, result
    assert result["status"] == "partial"
    assert result["data"]["started"] is False
    assert result["data"]["selection_token"] is None
    assert result["error"]["code"] == "SELECTION_PUBLICATION_UNKNOWN"
    assert {effect["kind"]: effect["status"] for effect in result["effects"]} == {
        "git.branch.create": "unchanged",
        "git.checkout": "unchanged",
        "selection.publish": "unknown",
    }
    assert result["recovery"]["instructions"]
    assert len(list(directory.glob(".stage-*"))) == 1
    assert not list(directory.glob("target-*.json"))
    assert git(world.main, "branch", "--show-current") == "main"


@pytest.mark.skipif(os.name != "posix", reason="native POSIX permission boundary")
def test_start_retains_stage_and_reports_unknown_when_native_rename_is_refused(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    directory = _targets(world)
    real_fsync = os.fsync
    restricted = False

    def syncing(descriptor):
        nonlocal restricted
        real_fsync(descriptor)
        if directory.exists() and any(
            path.stat().st_ino == os.fstat(descriptor).st_ino for path in directory.glob(".stage-*")
        ):
            directory.chmod(0o500)
            restricted = True

    monkeypatch.setattr(os, "fsync", syncing)
    try:
        code, result = world.run("work", "start", "iss-00003", "--branch", "main")
    finally:
        if directory.exists():
            directory.chmod(0o700)
    assert restricted
    assert code == 6, result
    assert result["status"] == "partial"
    assert result["error"]["code"] == "SELECTION_PUBLICATION_UNKNOWN"
    assert next(effect for effect in result["effects"] if effect["kind"] == "selection.publish")["status"] == "unknown"
    assert len(list(directory.glob(".stage-*"))) == 1
    assert not list(directory.glob("target-*.json"))


@pytest.mark.parametrize("additional", ["record", "unknown"])
def test_start_does_not_confirm_publication_with_an_additional_entry(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch, additional: str
) -> None:
    directory = _targets(world)
    real_fsync = os.fsync
    inserted = False

    def syncing(fd):
        nonlocal inserted
        real_fsync(fd)
        if not inserted and directory.exists() and os.fstat(fd).st_ino == directory.stat().st_ino:
            final = list(directory.glob("target-*.json"))
            if final:
                inserted = True
                if additional == "record":
                    (directory / ("target-" + "b" * 32 + ".json")).write_bytes(final[0].read_bytes())
                else:
                    (directory / "unexpected").write_bytes(b"preserve")

    monkeypatch.setattr(os, "fsync", syncing)
    code, result = world.run("work", "start", "iss-00003", "--branch", "main")
    assert code == 6, result
    assert inserted
    assert result["data"]["started"] is False
    assert result["data"]["selection_token"] is None
    assert result["error"]["code"] == "SELECTION_PUBLICATION_UNKNOWN"
    assert next(effect for effect in result["effects"] if effect["kind"] == "selection.publish")["status"] == "unknown"
    assert len(list(directory.iterdir())) == 2


@pytest.mark.parametrize("guard", [["--expect-backend", "local"], ["--expect-current", "iss-00003"]])
def test_start_expectation_mismatch_stops_before_git_effects(world: WriteWorld, guard: list[str]) -> None:
    before = git(world.main, "symbolic-ref", "--short", "HEAD")
    code, result = world.run("work", "start", "iss-00003", "--base", "HEAD", *guard)
    assert code == 3, result
    assert result["error"]["code"] == "EXPECTATION_FAILED"
    assert result["effects"] == []
    assert not _targets(world).exists()
    assert git(world.main, "symbolic-ref", "--short", "HEAD") == before
    assert world.writes() == []


def test_start_requires_ascii_branch_name_before_effects(world: WriteWorld) -> None:
    code, result = world.run("work", "start", "iss-00003", "--base", "HEAD", "--branch", "feature/日本語")
    assert code == 3, result
    assert result["effects"] == []
    assert not _targets(world).exists()


def test_start_does_not_expand_previous_checkout_syntax_as_branch_name(world: WriteWorld) -> None:
    git(world.main, "checkout", "-qb", "previous")
    git(world.main, "checkout", "-q", "main")
    code, result = world.run("work", "start", "iss-00003", "--branch", "@{-1}", "--base", "HEAD")
    assert code == 3, result
    assert result["error"]["code"] == "INVALID_BRANCH"
    assert result["effects"] == []
    assert git(world.main, "branch", "--show-current") == "main"
    assert not _targets(world).exists()


def test_store_cleanup_failure_preserves_confirmed_publication_effect(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    native_open, native_close = os.open, os.close
    held_directory = None
    failed = False

    def observe_open(path, *args, **kwargs):
        nonlocal held_directory
        fd = native_open(path, *args, **kwargs)
        if path == "work-target" and held_directory is None:
            held_directory = fd
        return fd

    def fail_confirmed_store_close(fd):
        nonlocal failed
        native_close(fd)
        if fd == held_directory and not failed and list(_targets(world).glob("target-*.json")):
            failed = True
            raise OSError("fixture cleanup after confirmed publication")

    monkeypatch.setattr(os, "open", observe_open)
    monkeypatch.setattr(os, "close", fail_confirmed_store_close)
    code, result, err = run_err(world, "work", "start", "iss-00003", "--base", "HEAD")
    assert code == 6, result
    assert failed
    assert err == ""
    assert result["status"] == "partial"
    assert (
        next(effect for effect in result["effects"] if effect["kind"] == "selection.publish")["status"] == "succeeded"
    )
    found = records(world.main)
    assert len(found) == 1
    assert json.loads(found[0].read_bytes())["scope_id"] == "iss-00003"


def test_same_scope_on_different_branch_replaces_only_captured_token(world: WriteWorld) -> None:
    code, first = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert code == 0, first
    old_token = first["data"]["selection_token"]
    code, second = world.run("work", "start", "iss-00003", "--branch", "alternate", "--base", "HEAD")
    assert code == 0, second
    new_token = second["data"]["selection_token"]
    assert old_token != new_token
    assert second["data"]["branch_after"] == "alternate"
    assert start_effects(second["effects"])[-2:] == [
        {"kind": "selection.clear", "status": "succeeded", "target": "iss-00003"},
        {"kind": "selection.publish", "status": "succeeded", "target": "iss-00003"},
    ]
    assert [path.name for path in _targets(world).iterdir()] == [f"target-{new_token}.json"]


@pytest.mark.parametrize("selected,number,target", [("iss-00003", 3, "epic-00002"), ("epic-00002", 2, "iss-00003")])
def test_start_requires_explicit_switch_even_for_direct_ancestor_or_descendant(
    world: WriteWorld, selected: str, number: int, target: str
) -> None:
    record = select_record(world, selected, number)
    before = tree_digest(world.main)
    exact_record = record.read_bytes()
    code, result, err = run_err(world, "work", "start", target, "--base", "HEAD")
    assert code == 3, result
    assert "--switch-active" in result["error"]["message"] and result["effects"] == [] and not err
    assert record.read_bytes() == exact_record and tree_digest(world.main) == before
    assert world.writes() == []


@pytest.mark.parametrize("switch", [False, True])
def test_different_scope_requires_explicit_switch_and_replaces_only_old_target(world: WriteWorld, switch: bool) -> None:
    code, first = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert code == 0, first
    old_token = first["data"]["selection_token"]
    flags = ["--switch-active"] if switch else []
    code, result = world.run("work", "start", "iss-00004", "--base", "HEAD", *flags)
    assert code == (0 if switch else 3), result
    directory = _targets(world)
    if switch:
        assert start_effects(result["effects"])[-2] == {
            "kind": "selection.clear",
            "status": "succeeded",
            "target": "iss-00003",
        }
        assert [path.name for path in directory.iterdir()] == [f"target-{result['data']['selection_token']}.json"]
        assert not (directory / f"target-{old_token}.json").exists()
    else:
        assert result["error"]["code"] == "SWITCH_ACTIVE_REQUIRED"
        assert result["effects"] == []
        assert [path.name for path in directory.iterdir()] == [f"target-{old_token}.json"]


def test_existing_branch_tip_changed_during_live_get_stops_before_git_effects(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    git(world.main, "branch", "requested", "HEAD")
    (world.main / "note.txt").write_text("new tip")
    commit(world.main, "next", "note.txt")
    original = git(world.main, "symbolic-ref", "--short", "HEAD")
    original_enter = StartLock.__enter__

    # Canonical start fixes the branch tip after the GitHub reread; the tip moves once the plan is made instead.
    def enter_and_move(lock: StartLock) -> StartLock:
        result = original_enter(lock)
        git(world.main, "update-ref", "refs/heads/requested", "HEAD")
        return result

    monkeypatch.setattr(StartLock, "__enter__", enter_and_move)
    code, result = world.run("work", "start", "iss-00003", "--branch", "requested")
    assert code == 3, result
    assert result["error"]["code"] == "BRANCH_CHANGED"
    assert result["effects"] == []
    assert git(world.main, "symbolic-ref", "--short", "HEAD") == original


def test_start_creates_checks_out_and_selects_without_git_control(world: WriteWorld) -> None:
    code, result, err = run_err(world, "work", "start", "iss-00003", "--base", "HEAD")
    assert code == 0, result
    assert err == ""
    assert result["data"]["kind"] == "work-start"
    assert result["data"]["started"] is True
    assert result["data"]["branch_after"] == "iss-00003"
    assert result["data"]["selection_token"]
    assert [item["kind"] for item in start_effects(result["effects"])] == [
        "git.branch.create",
        "git.checkout",
        "selection.publish",
    ]
    assert git(world.main, "branch", "--show-current") == "iss-00003"
    found = records(world.main)
    assert len(found) == 1
    assert json.loads(found[0].read_bytes())["scope_id"] == "iss-00003"
    assert not (world.main / ".git/spec-dock").exists()
    assert git(world.main, "status", "--porcelain") == ""


def test_start_does_not_publish_after_checkout_changes_worktree_inventory(world: WriteWorld, tmp_path: Path) -> None:
    linked = tmp_path / "created-during-checkout"
    _hook(
        world,
        "unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE\n"
        f"if [ ! -d {shlex.quote(str(linked))} ]; then\n"
        f"  git -C {shlex.quote(str(world.main))} worktree add --detach {shlex.quote(str(linked))} HEAD >&2\n"
        "fi\n",
    )
    code, result = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert code == 6, result
    assert result["data"]["started"] is False
    assert result["error"]["code"] == "WORKTREE_INVENTORY_CHANGED"
    assert result["effects"][-1] == {"kind": "selection.publish", "status": "not_attempted", "target": "iss-00003"}
    assert linked.is_dir()
    assert not _targets(world).exists()
    assert git(world.main, "branch", "--show-current") == "iss-00003"


def test_start_rejects_branch_checked_out_by_another_worktree_before_effects(world: WriteWorld, tmp_path: Path) -> None:
    add_worktree(world.main, tmp_path / "linked", "occupied")
    before = git(world.main, "branch", "--show-current")
    code, result = world.run("work", "start", "iss-00003", "--branch", "occupied")
    assert code == 3, result
    assert result["error"]["code"] == "BRANCH_IN_USE"
    assert result["effects"] == []
    assert git(world.main, "branch", "--show-current") == before
    assert not _targets(world).exists()


def test_start_reports_publication_unknown_when_sync_fails_after_record_rename(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_fsync = os.fsync
    directory = _targets(world)

    def fail_after_publication(descriptor: int) -> None:
        if list(directory.glob("target-*.json")):
            raise OSError("fixture: directory synchronization failed after rename")
        original_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", fail_after_publication)
    code, result = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert code == 6, result
    assert result["data"]["started"] is False
    assert result["effects"][-1] == {"kind": "selection.publish", "status": "unknown", "target": "iss-00003"}
    assert len(list(directory.glob("target-*.json"))) == 1
    assert git(world.main, "branch", "--show-current") == "iss-00003"


def test_start_reports_unknown_publication_when_a_stage_remains_before_rename(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_fsync = os.fsync
    directory = _targets(world)

    def fail_stage_sync(descriptor: int) -> None:
        if list(directory.glob(".stage-*")):
            raise OSError("fixture: stage synchronization failed")
        original_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", fail_stage_sync)
    code, result = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert code == 6, result
    assert result["effects"][-1] == {"kind": "selection.publish", "status": "unknown", "target": "iss-00003"}
    assert not list(directory.glob("target-*.json"))
    assert len(list(directory.glob(".stage-*"))) == 1


def test_switch_reports_clear_unknown_when_sync_fails_after_unlink(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    code, first = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert code == 0, first
    directory = _targets(world)
    old = directory / f"target-{first['data']['selection_token']}.json"
    original_fsync = os.fsync

    def failed_clear_sync(descriptor: int) -> None:
        if not old.exists():
            raise OSError("fixture: synchronization failed after unlink")
        original_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", failed_clear_sync)
    code, result = world.run("work", "start", "iss-00003", "--branch", "alternate", "--base", "HEAD")
    assert code == 6, result
    assert start_effects(result["effects"])[-2:] == [
        {"kind": "selection.clear", "status": "unknown", "target": "iss-00003"},
        {"kind": "selection.publish", "status": "not_attempted", "target": "iss-00003"},
    ]
    assert not old.exists()
    assert not list(directory.iterdir())


def test_switch_rechecks_inventory_after_old_target_removal_before_publication(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    code, first = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert code == 0, first
    original_unlink = os.unlink
    linked = tmp_path / "created-after-clear"

    def unlink_and_add_worktree(path, *, dir_fd=None):
        original_unlink(path, dir_fd=dir_fd)
        if isinstance(path, str) and path.startswith("target-"):
            git(world.main, "worktree", "add", "--detach", str(linked), "HEAD")

    monkeypatch.setattr(os, "unlink", unlink_and_add_worktree)
    code, result = world.run("work", "start", "iss-00003", "--branch", "alternate", "--base", "HEAD")
    assert code == 6, result
    assert result["error"]["code"] == "WORKTREE_INVENTORY_CHANGED"
    assert start_effects(result["effects"])[-2:] == [
        {"kind": "selection.clear", "status": "succeeded", "target": "iss-00003"},
        {"kind": "selection.publish", "status": "not_attempted", "target": "iss-00003"},
    ]
    assert not list(_targets(world).iterdir())


def test_start_dry_run_does_not_take_lock_or_create_branch_or_selection(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden_lock(self: object) -> None:
        raise AssertionError("dry-run must not acquire Start lock")

    monkeypatch.setattr("spec_dock.runtime.application.canonical_work.StartLock.__enter__", forbidden_lock)
    before = git(world.main, "show-ref")
    code, result = world.run("work", "start", "iss-00003", "--base", "HEAD", "--dry-run")
    assert code == 0, result
    assert result["status"] == "planned"
    assert result["data"]["started"] is False
    assert {item["status"] for item in result["effects"]} == {"planned"}
    assert git(world.main, "show-ref") == before
    assert not (world.main / "spec-dock/.agent").exists()
    assert world.writes() == []


def test_checkout_failure_preserves_created_branch_and_native_stderr(world: WriteWorld) -> None:
    # Git's own index lock rejects checkout, while branch creation remains possible.
    (world.main / ".git/index.lock").write_bytes(b"")
    before = git(world.main, "branch", "--show-current")
    code, result, err = run_err(world, "work", "start", "iss-00003", "--base", "HEAD")
    assert code == 6, result
    assert result["status"] == "partial"
    assert result["data"]["started"] is False
    assert [(item["kind"], item["status"]) for item in result["effects"]] == [
        ("git.branch.create", "succeeded"),
        ("git.checkout", "failed"),
        ("selection.publish", "not_attempted"),
    ]
    assert git(world.main, "branch", "--show-current") == before
    native = subprocess.run(["git", "-C", str(world.main), "checkout", "iss-00003"], capture_output=True, check=False)
    assert result["error"]["details"]["git"]["stderr"] == native.stderr.decode()
    assert result["error"]["details"]["git"]["returncode"] == native.returncode
    assert result["recovery"] == {
        "can_resume": False,
        "can_rollback": False,
        "instructions": [
            "現在のbranch/HEAD、branch show、active showで現物を確認してください。",
            "原因を修正後、branchが存在すれば--branchを明示して新しいwork startを実行してください。--baseは付けません。",
            "選択がinvalid/unknownならworkspace doctorで確認してください。記録やGit効果は自動で巻き戻しません。",
        ],
    }
    assert not err
    assert not (world.main / "spec-dock/.agent").exists()


def test_failed_post_checkout_hook_reports_observed_head_without_rollback(world: WriteWorld) -> None:
    _hook(world, "printf 'fixture: post-checkout failed\\n' >&2\nexit 1\n")
    code, result = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert code == 6, result
    assert result["data"]["started"] is False
    assert result["data"]["branch_after"] == "iss-00003"
    assert result["effects"][1] == {"kind": "git.checkout", "status": "succeeded", "target": "iss-00003"}
    assert result["error"]["details"]["git"]["returncode"] == 1
    assert "fixture: post-checkout failed\n" in result["error"]["details"]["git"]["stderr"]
    assert not _targets(world).exists()


def test_readonly_git_probe_failure_after_checkout_does_not_relabel_checkout_as_failed(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    real_run = subprocess.run
    head = world.main / ".git/HEAD"

    def fail_post_checkout_probe(argv, **kwargs):
        if "check-ignore" in argv and head.read_text() == "ref: refs/heads/iss-00003\n":
            return subprocess.CompletedProcess(argv, 19, stdout=b"", stderr=b"fixture: readonly ignore probe failed\n")
        return real_run(argv, **kwargs)

    monkeypatch.setattr(subprocess, "run", fail_post_checkout_probe)
    code, result = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert code == 6, result
    assert [(effect["kind"], effect["status"]) for effect in result["effects"]] == [
        ("git.branch.create", "succeeded"),
        ("git.checkout", "succeeded"),
        ("selection.publish", "not_attempted"),
    ]
    assert result["error"]["details"]["git"]["returncode"] == 19


def test_existing_branch_requires_explicit_reuse_and_no_base(world: WriteWorld) -> None:
    git(world.main, "branch", "iss-00003")
    code, result = world.run("work", "start", "iss-00003")
    assert code == 3, result
    assert result["effects"] == []
    code, result = world.run("work", "start", "iss-00003", "--branch", "iss-00003", "--base", "HEAD")
    assert code == 3, result
    assert result["effects"] == []
    code, result = world.run("work", "start", "iss-00003", "--branch", "iss-00003")
    assert code == 0, result
    assert result["data"]["started"] is True
    assert result["effects"][0] == {"kind": "git.branch.create", "status": "unchanged", "target": "iss-00003"}


def test_text_checkout_failure_preserves_native_stderr_newlines(world: WriteWorld) -> None:
    (world.main / ".git/index.lock").write_bytes(b"")
    code, out, err = raw(world, "work", "start", "iss-00003", "--base", "HEAD")
    assert code == 6, out + err
    native = subprocess.run(["git", "-C", str(world.main), "checkout", "iss-00003"], capture_output=True, check=False)
    assert err.endswith(native.stderr.decode())
    assert "spec-dock: partial" in out


def test_start_refuses_unignored_state_before_creating_branch(world: WriteWorld) -> None:
    (world.main / "spec-dock/.gitignore").write_bytes(b"")
    commit(world.main, "unignored", "spec-dock/.gitignore")
    before = git(world.main, "show-ref")
    code, result = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert code == 3, result
    assert result["effects"] == []
    assert "ignored" in result["error"]["message"]
    assert git(world.main, "show-ref") == before
    assert not (world.main / "spec-dock/.agent").exists()


def test_start_rechecks_clean_state_after_acquiring_lock(world: WriteWorld, monkeypatch: pytest.MonkeyPatch) -> None:
    original_enter = StartLock.__enter__

    def enter_and_edit(lock: StartLock) -> StartLock:
        result = original_enter(lock)
        (world.main / "untracked.txt").write_text("changed after preflight")
        return result

    monkeypatch.setattr(StartLock, "__enter__", enter_and_edit)
    before = git(world.main, "show-ref")
    code, result = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert code == 3, result
    assert result["effects"] == []
    assert git(world.main, "show-ref") == before
    assert (world.main / "untracked.txt").read_text() == "changed after preflight"


@pytest.mark.parametrize("stale", [False, True])
def test_other_worktree_stale_selection_reserves_scope_id(world: WriteWorld, tmp_path: Path, stale: bool) -> None:
    linked = world.worktree("linked")
    record = select_record(world, "iss-00003", 99 if stale else 3, checkout=linked, branch="old")
    before_record = record.read_bytes()
    before_refs = git(world.main, "show-ref")
    code, result = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert code == 3, result
    assert result["error"]["code"] == "SCOPE_ALREADY_SELECTED"
    assert result["effects"] == []
    assert record.read_bytes() == before_record
    assert git(world.main, "show-ref") == before_refs


def test_same_valid_target_on_same_branch_is_unchanged(world: WriteWorld) -> None:
    code, first = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert code == 0, first
    saved = {path.name: path.read_bytes() for path in _targets(world).iterdir()}
    code, result = world.run("work", "start", "iss-00003", "--branch", "iss-00003")
    assert code == 0, result
    assert result["status"] == "unchanged"
    assert result["data"]["started"] is True
    assert result["data"]["selection_token"] == first["data"]["selection_token"]
    assert {path.name: path.read_bytes() for path in _targets(world).iterdir()} == saved
    assert {item["status"] for item in result["effects"]} <= {"unchanged"}


@pytest.mark.parametrize(
    "bad_payload",
    [
        {"required_features": None},
        {"required_features": False},
        {"required_features": 0},
        {"required_features": ""},
        {"required_features": {}},
        {"required_features": [1]},
        {"type": "workspace"},
        {"control_epoch": 1},
    ],
)
def test_start_rejects_invalid_writer_workspace_before_git_effects(
    world: WriteWorld, bad_payload: dict[str, object]
) -> None:
    # Only the current workspace is checked: canonical start never reads workspace.json at the base commit.
    workspace = world.main / "spec-dock/workspace.json"
    workspace.write_text(json.dumps(dict(json.loads(workspace.read_bytes()), **bad_payload)))
    commit(world.main, "invalid workspace", "spec-dock/workspace.json")
    code, result = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert code == 3, result
    assert result["effects"] == []
    assert not _targets(world).exists()


def test_start_rejects_probe_only_ignore_rule_before_git_effects(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Only the current checkout is checked: canonical start never reads ignore rules at the base commit.
    (world.main / "spec-dock/.gitignore").write_text(
        ".agent/work-target/target-0*.json\n.agent/work-target/.stage-0*\n"
    )
    commit(world.main, "probe only ignore", "spec-dock/.gitignore")
    monkeypatch.setattr("secrets.token_hex", lambda size: "f" * 32)
    refs_before = git(world.main, "show-ref")
    status_before = git(world.main, "status", "--porcelain")
    code, result = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert code == 3, result
    assert result["error"]["code"] == "WORK_TARGET_PATH_NOT_IGNORED"
    assert result["effects"] == []
    assert git(world.main, "show-ref") == refs_before
    assert git(world.main, "status", "--porcelain") == status_before


@pytest.mark.parametrize("target,number", [("init-00001", 1), ("epic-00002", 2), ("iss-00003", 3)])
@pytest.mark.parametrize("detached", [False, True])
def test_new_start_requires_explicit_base_from_attached_or_detached_head(
    world: WriteWorld, target: str, number: int, detached: bool
) -> None:
    if detached:
        git(world.main, "checkout", "--detach", "HEAD")
    before = tree_digest(world.main)
    code, result, err = run_err(world, "work", "start", target)
    assert code == 3, result
    assert "new branch requires --base" in result["error"]["message"]
    assert result["effects"] == [] and not err and tree_digest(world.main) == before
    assert world.writes() == [] and not _targets(world).exists()
    if detached:
        code, result, err = run_err(world, "work", "start", target, "--base", "HEAD")
        assert code == 0, result
        assert result["data"]["started"] is True and result["data"]["scope_id"] == target
        assert result["data"]["branch_after"] == target and not err
        record = _targets(world) / f"target-{result['data']['selection_token']}.json"
        assert json.loads(record.read_bytes())["github_ref"] == f"gh:example/repo#{number}"
        assert not (world.main / ".git/spec-dock").exists()
