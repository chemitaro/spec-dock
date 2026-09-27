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
from tests.cli_runtime.test_worktree_create_vnext import _committed_repo  # noqa: E402


def _run(repo: Path, *args: str):
    return run_vnext([*args, "--json"], invocation_cwd=repo, engine_digest="engine-a", engine_version="0.2.4")


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


def test_worktree_create_remove_cli_previews_and_keeps_branch(tmp_path: Path) -> None:
    common = _committed_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    root = tmp_path / "worktrees"
    prefix = ("worktree", "create", "planning", "--base", "HEAD", "--root", str(root))
    preview = _run(repo, *prefix, "--dry-run")
    assert preview.exit_code == 0
    assert json.loads(preview.stdout)["data"]["id"] == "wt1"
    assert not root.exists()
    created = _run(repo, *prefix)
    assert created.exit_code == 0
    payload = json.loads(created.stdout)["data"]
    assert payload["id"] == "wt1"
    target = Path(payload["path"])
    assert target.is_dir()
    remove_prefix = ("worktree", "remove", "wt:wt1")
    denied = _run(repo, *remove_prefix)
    assert denied.exit_code == 3
    removal_plan = _run(repo, *remove_prefix, "--dry-run")
    assert removal_plan.exit_code == 0
    removed = _run(repo, *remove_prefix, "--yes")
    assert removed.exit_code == 0
    assert not target.exists()
    assert json.loads(removed.stdout)["data"]["branch_deleted"] is False


def test_worktree_bootstrap_cli_dry_run_and_actual_result(tmp_path: Path) -> None:
    common = _committed_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    created = _run(repo, "worktree", "create", "planning", "--base", "HEAD", "--root", str(tmp_path / "trees"))
    assert created.exit_code == 0
    target = Path(json.loads(created.stdout)["data"]["path"])
    prefix = ("worktree", "bootstrap", "wt:wt1")
    preview = _run(repo, *prefix, "--dry-run")
    assert preview.exit_code == 0
    assert not (target / "bootstrap-ran").exists()
    offline = _run(repo, *prefix, "--offline", "--yes")
    assert offline.exit_code == 3
    completed = _run(repo, *prefix, "--yes")
    assert completed.exit_code == 0
    assert json.loads(completed.stdout)["data"]["status"] == "succeeded"
    assert (target / "bootstrap-ran").exists()
