"""The new work leaves compose the same lifecycle for every Scope kind."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.cli.options import parse_vnext  # noqa: E402
from spec_dock_runtime.commands.work_vnext import WorkContext, run_work_finish, run_work_start  # noqa: E402
from spec_dock_runtime.infra.active_store import load_selection_v3  # noqa: E402
from spec_dock_runtime.infra.github_lifecycle import GithubIssueGateway  # noqa: E402
from tests.cli_runtime.test_active_vnext import _three_scopes  # noqa: E402


def test_work_commands_start_and_finish_all_three_kinds(tmp_path: Path) -> None:
    specdock_dir, _views, initiative, epic, issue = _three_scopes(tmp_path)
    repo_root = specdock_dir.parent
    subprocess.run(["git", "add", "-A"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    context = WorkContext(repo_root, repo_root / ".git", "main", "engine-a", 1)
    gateway = GithubIssueGateway()
    for scope in (initiative, epic, issue):
        outcome = run_work_start(parse_vnext(["work", "start", scope.id]), context, gateway=gateway)
        assert outcome.status == "succeeded"
        assert outcome.data.scope_id == scope.id
        assert load_selection_v3(specdock_dir, worktree_id="main")[0].focus_id == scope.id
    for scope in (issue, epic, initiative):
        outcome = run_work_finish(parse_vnext(["work", "finish", scope.id, "--yes"]), context, gateway=gateway)
        assert outcome.status == "succeeded"
        assert outcome.data.scope_id == scope.id
    assert load_selection_v3(specdock_dir, worktree_id="main")[0].focus_id is None


def test_work_adapter_rejects_unimplemented_dry_run_and_unconfirmed_finish(tmp_path: Path) -> None:
    specdock_dir, _views, _initiative, _epic, issue = _three_scopes(tmp_path)
    repo_root = specdock_dir.parent
    context = WorkContext(repo_root, repo_root / ".git", "main", "engine-a", 1)
    gateway = GithubIssueGateway()
    before = (issue.path / ".meta.json").read_bytes()
    with pytest.raises(ValueError, match="dry-run"):
        run_work_start(parse_vnext(["work", "start", issue.id, "--dry-run"]), context, gateway=gateway)
    with pytest.raises(ValueError, match="requires --yes"):
        run_work_finish(parse_vnext(["work", "finish", issue.id]), context, gateway=gateway)
    assert (issue.path / ".meta.json").read_bytes() == before
    assert load_selection_v3(specdock_dir, worktree_id="main")[0].focus_id is None
