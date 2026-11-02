"""Canonical-mode stand-ins for the retired schema-3 fixtures of the G3 worktree, branch and Artifact tests (iss-00440).

    world = make_world(tmp_path, monkeypatch, capsys)        # linked clone under tmp_path/world, init-00001 "Fixture"
    other = linked_worktree(world, tmp_path / "linked", "parallel")
    code, result = cli(capsys, "--project", str(world.main), "worktree", "list", "--json")

The world lives in its own directory, so paths a test makes directly under `tmp_path` stay the test's own.
"""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING, Any

from spec_dock.cli import main
from tests.support.canonical_repo import add_worktree, clone
from tests.support.canonical_scopes import CanonicalWorld
from tests.support.canonical_writes import WriteWorld

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

WORK_TARGET = "spec-dock/.agent/work-target"


def make_world(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    *,
    write: bool = False,
) -> CanonicalWorld:
    """A canonical clone with GitHub Issue #1 `init-00001` ("Fixture") and its catalog directory."""
    base = tmp_path / "world"
    base.mkdir()
    world = (WriteWorld if write else CanonicalWorld).create(base, monkeypatch, capsys)
    world.scope("initiative", 1, "Fixture")
    return world


def cli(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, dict[str, Any]]:
    code = main(list(argv))
    return code, json.loads(capsys.readouterr().out)


def git_out(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout.strip()


def has_branch(root: Path, name: str) -> bool:
    checked = subprocess.run(
        ["git", "-C", str(root), "show-ref", "--verify", "--quiet", f"refs/heads/{name}"], capture_output=True
    )
    return checked.returncode == 0


def select(
    world: CanonicalWorld, scope_id: str = "init-00001", number: int = 1, *, checkout: Path | None = None
) -> Path:
    """Write a direct selection record and return its file."""
    root = checkout or world.main
    world.select(scope_id, number, checkout=root)
    (record,) = (root / WORK_TARGET).glob("target-*.json")
    return record


def linked_worktree(world: CanonicalWorld, path: Path, branch: str) -> Path:
    """A linked worktree on a new branch with its own correct catalog link."""
    linked = add_worktree(world.main, path, branch)
    code, payload = world.run("canonical", "link", checkout=linked)
    assert code == 0, payload
    return linked


def other_clone(world: CanonicalWorld, path: Path) -> Path:
    """Another physical clone of the same origin (schema 4, without a catalog link)."""
    return clone(world.tmp_path / "remote.git", path)
