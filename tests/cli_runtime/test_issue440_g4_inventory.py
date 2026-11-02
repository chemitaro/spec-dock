"""Incomplete Git inventory rows stay visible in sync and cannot authorize `work start` (iss-00440, G4).

Replaces tests/integration/test_issue413_inventory_diagnostics.py, which ran on a schema-3 workspace. The Git
inventory shim is unchanged; the clone is a linked canonical checkout (its catalog worktree is not a row).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

from tests.support.canonical_scopes import CanonicalWorld
from tests.support.canonical_writes import WriteWorld

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.skipif(os.name == "nt", reason="POSIX executable fixture")


def inventory_fixture(root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, field: bytes) -> Path:
    """A linked worktree whose `git worktree list --porcelain -z` record carries one injected attribute."""
    linked = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "--detach", str(linked), "HEAD"],
        check=True,
        capture_output=True,
    )
    linked = linked.resolve()
    real_git = shutil.which("git")
    assert real_git
    output = subprocess.check_output([real_git, "-C", str(root), "worktree", "list", "--porcelain", "-z"])
    marker = b"worktree " + os.fsencode(linked) + b"\0"
    assert output.count(marker) == 1
    output = output.replace(marker, marker + field + b"\0")
    binary = tmp_path / "bin"
    binary.mkdir()
    executable = binary / "git"
    executable.write_text(
        f"#!{sys.executable}\nimport os, sys\n"
        "if sys.argv[-4:] == ['worktree', 'list', '--porcelain', '-z']:\n"
        f" sys.stdout.buffer.write({output!r}); sys.exit(0)\n"
        f"os.execv({real_git!r}, [{real_git!r}, *sys.argv[1:]])\n"
    )
    executable.chmod(0o700)
    monkeypatch.setenv("PATH", str(binary) + os.pathsep + os.environ.get("PATH", ""))
    return linked


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> CanonicalWorld:
    world = CanonicalWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "Plan")
    world.scope("epic", 2, "Core", parent=1)
    world.scope("issue", 3, "Leaf", parent=2)
    return world


def test_sync_retains_unknown_inventory_row_and_healthy_selection(
    world: CanonicalWorld, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    world.select("iss-00003", 3)
    (record,) = (world.main / "spec-dock/.agent/work-target").glob("target-*.json")
    before = record.read_bytes()
    linked = inventory_fixture(world.main, tmp_path, monkeypatch, b"future-attribute enabled")
    code, result = world.run("workspace", "sync")
    assert code == 7
    assert result["status"] == "partial" and result["effects"] == []
    data = result["data"]
    assert data["complete"] is False
    rows = {row["path"]: row for row in data["worktrees"]}
    assert rows[str(world.main)]["selection"]["status"] == "selected"
    assert rows[str(linked)]["selection"]["status"] == "unavailable"
    assert "future-attribute" in rows[str(linked)]["findings"][0]["message"]
    assert {row["scope_id"]: row for row in data["counts"]}["iss-00003"] == {
        "scope_id": "iss-00003",
        "direct_selected_count": 1,
        "descendant_selected_count": 0,
        "complete": False,
    }
    assert record.read_bytes() == before
    assert not (linked / "spec-dock/.agent").exists()


def test_sync_retains_duplicate_inventory_attribute_as_one_unavailable_row(
    world: CanonicalWorld, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    linked = inventory_fixture(world.main, tmp_path, monkeypatch, b"HEAD " + b"0" * 40)
    code, result = world.run("workspace", "sync")
    assert code == 7
    assert result["effects"] == []
    assert result["data"]["complete"] is False
    rows = {row["path"]: row for row in result["data"]["worktrees"]}
    assert len(rows) == 2
    assert rows[str(world.main)]["selection"]["status"] == "empty"
    assert rows[str(linked)]["selection"]["status"] == "unavailable"
    assert "duplicate" in rows[str(linked)]["findings"][0]["message"]
    assert not (world.main / "spec-dock/.agent").exists()


@pytest.mark.parametrize("field", [b"future-attribute enabled", b"HEAD " + b"0" * 40])
def test_start_stops_before_git_effects_for_an_incomplete_inventory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], field: bytes
) -> None:
    world = WriteWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "Plan")
    world.scope("epic", 2, "Core", parent=1)
    world.scope("issue", 3, "Leaf", parent=2)
    linked = inventory_fixture(world.main, tmp_path, monkeypatch, field)
    before = subprocess.check_output(["git", "-C", str(world.main), "show-ref"])
    code, result = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert code == 3, result
    assert result["effects"] == []
    assert result["data"]["started"] is False
    assert subprocess.check_output(["git", "-C", str(world.main), "show-ref"]) == before
    assert not (world.main / "spec-dock/.agent").exists()
    assert not (linked / "spec-dock/.agent").exists()
    assert world.writes() == []


def test_sync_rejects_an_inventory_flag_with_an_unexpected_value(
    world: CanonicalWorld, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    linked = inventory_fixture(world.main, tmp_path, monkeypatch, b"bare false")
    code, result = world.run("workspace", "sync")
    assert code == 7
    row = next(row for row in result["data"]["worktrees"] if row["path"] == str(linked))
    assert row["selection"]["status"] == "unavailable"
    assert "bare" in row["findings"][0]["message"]
    assert "attribute" in row["findings"][0]["message"]


def test_sync_keeps_a_known_path_when_its_branch_attribute_is_invalid(
    world: CanonicalWorld, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    linked = inventory_fixture(world.main, tmp_path, monkeypatch, b"branch refs/tags/v1")
    code, result = world.run("workspace", "sync")
    assert code == 7
    assert len(result["data"]["worktrees"]) == 2
    row = next(row for row in result["data"]["worktrees"] if row["path"] == str(linked))
    assert row["selection"]["status"] == "unavailable"
    assert "branch" in row["findings"][0]["message"]
