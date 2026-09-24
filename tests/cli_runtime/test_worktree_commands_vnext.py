"""Worktree inventory leaves use stable registration identifiers."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import cast

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.cli.vnext_runtime import run_vnext  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import _ready_repo  # noqa: E402


def test_worktree_list_show_cli_uses_registered_identity(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    listed = run_vnext(
        ["worktree", "list", "--json"], invocation_cwd=repo, engine_digest="engine-a", engine_version="0.2.4"
    )
    assert listed.exit_code == 0
    items = json.loads(listed.stdout)["data"]["items"]
    assert len(items) == 1
    assert items[0]["id"] == common["worktree_id"]
    assert items[0]["path"] == str(repo)
    shown = run_vnext(
        ["worktree", "show", f"wt:{common['worktree_id']}", "--json"],
        invocation_cwd=repo,
        engine_digest="engine-a",
        engine_version="0.2.4",
    )
    assert shown.exit_code == 0
    assert json.loads(shown.stdout)["data"]["id"] == common["worktree_id"]
