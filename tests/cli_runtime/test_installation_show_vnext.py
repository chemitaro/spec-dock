"""Installation show reads the registered worktree inventory without mutation."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import cast

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.cli.vnext_runtime import run_vnext  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import _ready_repo  # noqa: E402


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
