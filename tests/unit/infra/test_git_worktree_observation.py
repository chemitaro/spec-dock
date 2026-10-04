"""Git inventory paths survive spaces and literal newlines (Issue #413 D-04)."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.infra.git_cli import worktree_list

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize("spelling", ["linked\ntree", " linked\r\ntree "])
def test_git_inventory_keeps_literal_newline_path(tmp_path: Path, spelling: str) -> None:
    root = tmp_path / "main tree"
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "--allow-empty",
            "-qm",
            "fixture",
        ],
        check=True,
        capture_output=True,
    )
    linked = tmp_path / spelling
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "--detach", str(linked), "HEAD"], check=True, capture_output=True
    )
    inventory = worktree_list(root)
    assert {item.path for item in inventory} == {root, linked}
    target = next(item for item in inventory if item.path == linked)
    assert target.branch is None
    assert not target.bare
