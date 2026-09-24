"""Installation show reads the registered worktree inventory without mutation."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import cast

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.installation_vnext import inspect_installation_group  # noqa: E402
from spec_dock_runtime.application.worktree_vnext import create_worktree  # noqa: E402
from spec_dock_runtime.cli.vnext_runtime import run_vnext  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import _ready_repo  # noqa: E402
from tests.cli_runtime.test_worktree_create_vnext import _committed_repo  # noqa: E402


def test_installation_show_reports_bound_engine_and_installed_worktrees(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    output = run_vnext(
        ["installation", "show", "--json"],
        invocation_cwd=repo,
        engine_digest="engine-a",
        engine_version="0.2.4",
    )
    assert output.exit_code == 0
    data = json.loads(output.stdout)["data"]
    assert data["target"] == str(repo)
    assert data["engine_version"] == "0.2.4"
    assert data["source_repository"] == "chemitaro/spec-dock"
    assert data["control_mode"] == "ready"
    assert data["worktrees"][0]["id"] == "main"


def test_installation_show_rejects_unregistered_target(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    other = tmp_path / "other"
    other.mkdir()
    output = run_vnext(
        ["installation", "show", "--target", str(other), "--json"],
        invocation_cwd=repo,
        engine_digest="engine-a",
        engine_version="0.2.4",
    )
    assert output.exit_code == 3
    assert json.loads(output.stdout)["error"]["code"] == "PRECONDITION_FAILED"


def test_installation_group_fixes_every_registered_git_worktree(tmp_path: Path) -> None:
    common = _committed_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    created = create_worktree(base="HEAD", name="planning", root=tmp_path / "worktrees", **common)
    group = inspect_installation_group(repo_root=repo, common_dir=repo / ".git")
    assert {item.id for item in group.worktrees} == {"main", created.id}
    assert all(item.version is not None for item in group.worktrees)


def test_installation_group_rejects_foreign_git_worktree(tmp_path: Path) -> None:
    common = _committed_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    foreign = tmp_path / "foreign"
    subprocess.run(["git", "-C", str(repo), "worktree", "add", "-q", "-b", "foreign", str(foreign)], check=True)
    with pytest.raises(ValueError, match="differs"):
        inspect_installation_group(repo_root=repo, common_dir=repo / ".git")
