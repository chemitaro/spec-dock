"""The vNext parser reaches the real work use case in a registered worktree."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.cli.vnext_runtime import run_vnext  # noqa: E402
from spec_dock_runtime.infra.active_store import load_selection_v3  # noqa: E402
from tests.cli_runtime.test_active_vnext import _three_scopes  # noqa: E402


def test_vnext_cli_executes_three_kind_work_lifecycle_with_json(tmp_path: Path) -> None:
    specdock_dir, _views, initiative, epic, issue = _three_scopes(tmp_path)
    root = specdock_dir.parent
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    arguments = {"invocation_cwd": root, "engine_digest": "engine-a", "engine_version": "test"}
    for scope in (initiative, epic, issue):
        result = run_vnext(["work", "start", scope.id, "--json"], **arguments)
        assert result.exit_code == 0 and not result.stderr
        payload = json.loads(result.stdout)
        assert payload["command"] == "work start" and payload["data"]["scope_id"] == scope.id
    for scope in (issue, epic, initiative):
        result = run_vnext(["work", "finish", scope.id, "--json", "--yes"], **arguments)
        assert result.exit_code == 0 and not result.stderr
        payload = json.loads(result.stdout)
        assert payload["command"] == "work finish" and payload["data"]["scope_id"] == scope.id
    assert load_selection_v3(specdock_dir, worktree_id="main")[0].focus_id is None


def test_vnext_cli_rejects_engine_mismatch_before_work_mutation(tmp_path: Path) -> None:
    specdock_dir, _views, _initiative, _epic, issue = _three_scopes(tmp_path)
    root = specdock_dir.parent
    before = (issue.path / ".meta.json").read_bytes()
    result = run_vnext(
        ["work", "finish", issue.id, "--json", "--yes"],
        invocation_cwd=root,
        engine_digest="wrong",
        engine_version="test",
    )
    assert result.exit_code == 3
    assert json.loads(result.stdout)["error"]["code"] == "PRECONDITION_FAILED"
    assert (issue.path / ".meta.json").read_bytes() == before
