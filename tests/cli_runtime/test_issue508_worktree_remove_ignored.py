"""`worktree remove` keeps ignored files that appear after the link-only judgment (iss-00508).

Canonical removal lets a worktree whose only ignored entry is its correct catalog link go without
--discard-ignored. That judgment must hold right before `git worktree remove` (after any unlock), not only once
at the start: Git treats ignored files as clean and deletes them.
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

import pytest

from tests.support.legacy_contracts_g3 import cli, linked_worktree, make_world

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

IGNORED_LISTING = ("ls-files", "--others", "--ignored")


def _workspace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> tuple[Path, Path, Path]:
    world = make_world(tmp_path, monkeypatch, capsys)
    return world.main, linked_worktree(world, tmp_path / "linked", "parallel"), world.catalog


def _remove(capsys: pytest.CaptureFixture[str], root: Path, other: Path, *options: str) -> tuple[int, dict]:
    return cli(capsys, "--project", str(root), "worktree", "remove", str(other), *options, "--json")


def _intercept(
    monkeypatch: pytest.MonkeyPatch, root: Path, other: Path, *, after: Callable[[list[str]], bool], change
) -> list[str]:
    """Run `change()` once, right after the first native call for which `after(argv)` holds."""
    native_run = subprocess.run
    removals: list[str] = []
    done = False

    def run(argv, *args, **kwargs):
        nonlocal done
        if tuple(argv[:5]) == ("git", "-C", str(root), "worktree", "remove"):
            removals.append(str(argv[-1]))
        result = native_run(argv, *args, **kwargs)
        if not done and after(list(argv)):
            assert result.returncode == 0
            done = True
            change()
        return result

    monkeypatch.setattr(subprocess, "run", run)
    return removals


def _write_ignored(path: Path) -> Callable[[], None]:
    def change() -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"new ignored evidence")

    return change


def test_remove_preserves_ignored_content_created_after_unlock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other, _ = _workspace(tmp_path, monkeypatch, capsys)
    subprocess.run(["git", "-C", str(root), "worktree", "lock", str(other)], check=True, capture_output=True)
    actor_file = other / "spec-dock/.agent/new-evidence.bin"
    removals = _intercept(
        monkeypatch,
        root,
        other,
        after=lambda argv: tuple(argv[:5]) == ("git", "-C", str(root), "worktree", "unlock"),
        change=_write_ignored(actor_file),
    )
    code, result = _remove(capsys, root, other, "--unlock", "--yes")
    assert code == 6, result
    assert result["status"] == "partial" and result["error"]["code"] == "WORKTREE_REMOVE_FAILED"
    assert removals == [] and actor_file.read_bytes() == b"new ignored evidence"
    assert result["effects"] == [
        {"kind": "git.worktree.unlock", "status": "succeeded", "target": str(other)},
        {"kind": "git.worktree.remove", "status": "not_attempted", "target": str(other)},
    ]


def test_remove_preserves_ignored_content_created_after_the_first_judgment_without_a_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other, _ = _workspace(tmp_path, monkeypatch, capsys)
    actor_file = other / "spec-dock/.workbench/new-evidence.bin"
    removals = _intercept(
        monkeypatch,
        root,
        other,
        after=lambda argv: argv[:3] == ["git", "-C", str(other)] and tuple(argv[3:6]) == IGNORED_LISTING,
        change=_write_ignored(actor_file),
    )
    code, result = _remove(capsys, root, other, "--yes")
    assert code == 3, result
    assert result["status"] == "failed" and result["error"]["code"] == "PRECONDITION_FAILED"
    assert removals == [] and actor_file.read_bytes() == b"new ignored evidence"
    assert result["effects"] == []


@pytest.mark.parametrize("locked", [False, True])
def test_remove_still_discards_only_the_correct_catalog_link_without_discard_ignored(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], locked: bool
) -> None:
    root, other, catalog = _workspace(tmp_path, monkeypatch, capsys)
    assert (other / "spec-dock/initiatives").is_symlink()
    scope_file = catalog / "00000-00999/init-00001/requirement.md"
    catalog_bytes = scope_file.read_bytes()
    flags = ["--unlock"] if locked else []
    if locked:
        subprocess.run(["git", "-C", str(root), "worktree", "lock", str(other)], check=True, capture_output=True)
    code, result = _remove(capsys, root, other, "--yes", *flags)
    assert code == 0, result
    expected = [{"kind": "git.worktree.remove", "status": "succeeded", "target": str(other)}]
    if locked:
        expected.insert(0, {"kind": "git.worktree.unlock", "status": "succeeded", "target": str(other)})
    assert result["effects"] == expected
    assert not other.exists() and scope_file.read_bytes() == catalog_bytes
