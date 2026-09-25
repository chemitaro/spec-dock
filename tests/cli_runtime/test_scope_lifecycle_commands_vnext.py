"""Scope close and reopen are independent from active selection."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import cast

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.create_local_scope import create_local_scope  # noqa: E402
from spec_dock_runtime.cli.vnext_runtime import run_vnext  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import _ready_repo  # noqa: E402


def _run(repo: Path, *args: str):
    return run_vnext([*args, "--json"], invocation_cwd=repo, engine_digest="engine-a", engine_version="0.2.4")


def test_scope_close_reopen_cli_previews_and_updates_local_lifecycle(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    created = create_local_scope(kind="initiative", title="Plan", parent=None, ancestors=(), **common)
    metadata = created.path / ".meta.json"
    before = metadata.read_bytes()
    planned = _run(repo, "scope", "close", created.id, "--dry-run")
    assert planned.exit_code == 0
    assert json.loads(planned.stdout)["status"] == "planned"
    assert metadata.read_bytes() == before
    unconfirmed = _run(repo, "scope", "close", created.id)
    assert unconfirmed.exit_code == 3
    assert metadata.read_bytes() == before
    closed = _run(repo, "scope", "close", created.id, "--yes")
    assert closed.exit_code == 0
    assert json.loads(metadata.read_text())["lifecycle"]["state"] == "completed"
    operation_id = json.loads(closed.stdout)["operation_id"]
    wrong_action = _run(repo, "scope", "reopen", created.id, "--resume", operation_id, "--yes")
    assert wrong_action.exit_code == 3
    resumed = _run(repo, "scope", "close", created.id, "--resume", operation_id, "--yes")
    assert resumed.exit_code == 0
    unconfirmed_reopen = _run(repo, "scope", "reopen", created.id)
    assert unconfirmed_reopen.exit_code == 3
    assert json.loads(metadata.read_text())["lifecycle"]["state"] == "completed"
    reopened = _run(repo, "scope", "reopen", created.id, "--yes")
    assert reopened.exit_code == 0
    assert json.loads(metadata.read_text())["lifecycle"]["state"] == "open"
    abandoned = _run(repo, "scope", "close", created.id, "--reason", "not-planned", "--yes")
    assert abandoned.exit_code == 0
    abandoned_id = json.loads(abandoned.stdout)["operation_id"]
    implicit_completed = _run(repo, "scope", "close", created.id, "--resume", abandoned_id, "--yes")
    assert implicit_completed.exit_code == 3
    resumed_abandoned = _run(
        repo, "scope", "close", created.id, "--reason", "not-planned", "--resume", abandoned_id, "--yes"
    )
    assert resumed_abandoned.exit_code == 0


def test_scope_mutation_checks_expected_current_and_backend_before_edit(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    created = create_local_scope(kind="initiative", title="Plan", parent=None, ancestors=(), **common)
    metadata = created.path / ".meta.json"
    selected = _run(repo, "active", "set", created.id)
    assert selected.exit_code == 0
    before = metadata.read_bytes()

    missing = _run(repo, "scope", "edit", "@current", "--title", "New")
    assert missing.exit_code == 3
    assert metadata.read_bytes() == before
    mismatched = _run(repo, "scope", "edit", "@current", "--title", "New", "--expect-current", "init-local-99999")
    assert mismatched.exit_code == 3
    assert json.loads(mismatched.stdout)["error"]["code"] == "STATE_CONFLICT"
    assert metadata.read_bytes() == before
    wrong_backend = _run(repo, "scope", "edit", created.id, "--title", "New", "--expect-backend", "github")
    assert wrong_backend.exit_code == 3
    assert json.loads(wrong_backend.stdout)["error"]["code"] == "STATE_CONFLICT"
    assert metadata.read_bytes() == before

    changed = _run(
        repo,
        "scope",
        "edit",
        "@current",
        "--title",
        "New",
        "--expect-current",
        created.id,
        "--expect-backend",
        "local",
    )
    assert changed.exit_code == 0
    assert json.loads(metadata.read_text())["title"] == "New"
