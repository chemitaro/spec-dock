"""Branch switch joins the Start lock so checkouts and link writes never overlap, in canonical mode.

Replaces the schema-3 lock tests of tests/cli_runtime/test_issue416_branch_lock.py (iss-00440).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.infra.start_lock import StartLock
from tests.support.canonical_repo import git
from tests.support.legacy_contracts_g1 import chain_world, select_record

if TYPE_CHECKING:
    from pathlib import Path

    from tests.support.canonical_scopes import CanonicalWorld


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> CanonicalWorld:
    world = chain_world(tmp_path, monkeypatch, capsys)
    git(world.main, "branch", "candidate")
    select_record(world, "init-00001", 1)
    return world


def _git_tree(root: Path) -> set[str]:
    return {str(path.relative_to(root / ".git")) for path in (root / ".git").rglob("*")}


def test_branch_switch_waits_for_the_start_lock_and_stops_without_checkout(world: CanonicalWorld) -> None:
    before_git = _git_tree(world.main)
    with StartLock(world.main / ".git", timeout=0):
        code, result = world.run(
            "branch", "switch", "init-00001", "--name", "candidate", "--lock-timeout", "0", "--yes"
        )
    assert code == 3, result
    assert result["status"] == "failed"
    assert result["error"]["code"] == "START_LOCK_BUSY"
    assert result["effects"] == []
    assert git(world.main, "branch", "--show-current") == "main"
    assert not git(world.main, "status", "--porcelain")
    assert _git_tree(world.main) == before_git


def test_branch_switch_dry_run_does_not_take_the_start_lock(world: CanonicalWorld) -> None:
    with StartLock(world.main / ".git", timeout=0):
        code, result = world.run("branch", "switch", "init-00001", "--name", "candidate", "--dry-run")
    assert code == 0, result
    assert result["effects"] == [{"kind": "git.checkout", "status": "planned", "target": "candidate"}]
    assert git(world.main, "branch", "--show-current") == "main"
