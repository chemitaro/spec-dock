"""The vNext delete leaf previews its fixed subtree before quarantine."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

from spec_dock.runtime.application.create_local_scope import create_local_scope
from spec_dock.runtime.cli.vnext_runtime import run_vnext
from tests.cli_runtime.test_scope_github_vnext import _ready_repo

if TYPE_CHECKING:
    from pathlib import Path


def test_scope_delete_cli_requires_confirmation_and_previews_without_writes(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    created = create_local_scope(kind="initiative", title="Plan", parent=None, ancestors=(), **common)
    command = ["scope", "delete", created.id, "--json"]
    rejected = run_vnext(command, invocation_cwd=repo, engine_digest="engine-a", engine_version="0.2.4")
    assert rejected.exit_code == 3
    assert created.path.exists()
    preview = run_vnext([*command, "--dry-run"], invocation_cwd=repo, engine_digest="engine-a", engine_version="0.2.4")
    assert preview.exit_code == 0
    assert json.loads(preview.stdout)["data"]["deleted_ids"] == [created.id]
    assert created.path.exists()
    deleted = run_vnext([*command, "--yes"], invocation_cwd=repo, engine_digest="engine-a", engine_version="0.2.4")
    assert deleted.exit_code == 0
    assert not created.path.exists()
    operation_id = json.loads(deleted.stdout)["operation_id"]
    wrong_target = run_vnext(
        ["scope", "delete", "init-local-99999", "--resume", operation_id, "--yes", "--json"],
        invocation_cwd=repo,
        engine_digest="engine-a",
        engine_version="0.2.4",
    )
    assert wrong_target.exit_code == 3
    resumed = run_vnext(
        [*command, "--resume", operation_id, "--yes"],
        invocation_cwd=repo,
        engine_digest="engine-a",
        engine_version="0.2.4",
    )
    assert resumed.exit_code == 0
