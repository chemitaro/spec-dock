"""The vNext Scope create leaf resolves explicit ancestry before writing."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import cast

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.cli.vnext_runtime import run_vnext  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import _ready_repo  # noqa: E402


def _run(repo: Path, *args: str):
    return run_vnext([*args, "--json"], invocation_cwd=repo, engine_digest="engine-a", engine_version="0.2.4")


def test_local_scope_create_cli_uses_explicit_parent_and_dry_run(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    preview = _run(repo, "scope", "create", "initiative", "--backend", "local", "--title", "Program", "--dry-run")
    assert preview.exit_code == 0
    assert json.loads(preview.stdout)["status"] == "planned"
    assert not tuple((repo / "spec-dock" / "initiatives").glob("init-local-*"))

    initiative = _run(repo, "scope", "create", "initiative", "--backend", "local", "--title", "Program")
    assert initiative.exit_code == 0
    initiative_id = json.loads(initiative.stdout)["data"]["scope_id"]
    assert initiative_id == "init-local-00001"
    epic = _run(repo, "scope", "create", "epic", "--backend", "local", "--parent", initiative_id, "--title", "Plan")
    assert epic.exit_code == 0
    epic_id = json.loads(epic.stdout)["data"]["scope_id"]
    issue = _run(repo, "scope", "create", "issue", "--backend", "local", "--parent", epic_id, "--title", "Build")
    assert issue.exit_code == 0
    issue_id = json.loads(issue.stdout)["data"]["scope_id"]
    shown = _run(repo, "scope", "show", issue_id)
    assert json.loads(shown.stdout)["data"]["item"]["parent_id"] == epic_id


def test_local_scope_create_cli_rejects_missing_parent(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    result = _run(
        repo, "scope", "create", "epic", "--backend", "local", "--parent", "init-local-00999", "--title", "Plan"
    )
    assert result.exit_code == 4
    assert not tuple((repo / "spec-dock" / "initiatives").glob("init-local-*"))


def test_local_scope_create_cli_does_not_retry_a_recovery_request_as_new(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    result = _run(
        repo,
        "scope",
        "create",
        "initiative",
        "--backend",
        "local",
        "--title",
        "Program",
        "--resume",
        "a" * 32,
    )
    assert result.exit_code == 3
    assert not tuple((repo / "spec-dock" / "initiatives").glob("init-local-*"))
