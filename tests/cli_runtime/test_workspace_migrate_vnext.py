"""Workspace migration begins with a complete read-only inventory."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import cast

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.cli.vnext_runtime import run_vnext  # noqa: E402
from spec_dock_runtime.infra.migration_store import inspect_migration_inventory  # noqa: E402
from tests.cli_runtime.test_worktree_create_vnext import _committed_repo  # noqa: E402


def test_workspace_migrate_dry_run_inventories_all_worktrees(tmp_path: Path) -> None:
    common = _committed_repo(tmp_path)
    root = cast("Path", common["repo_root"])
    result = run_vnext(
        ["workspace", "migrate", "--to-schema", "3", "--dry-run", "--json"],
        invocation_cwd=root,
        engine_digest=cast("str", common["engine_digest"]),
        engine_version="0.2.4",
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "planned"
    assert payload["data"]["repository_uid"].startswith("sha256:")
    assert len(payload["data"]["worktrees"]) == 1
    assert payload["data"]["worktrees"][0]["root"] == str(root)


def test_workspace_migrate_dry_run_requires_exact_mapping_inventory(tmp_path: Path) -> None:
    common = _committed_repo(tmp_path)
    root = cast("Path", common["repo_root"])
    inventory = inspect_migration_inventory(root)
    mapping = tmp_path / "migration-map.json"
    payload = {
        "schema_version": "specdock.migration-map/v1",
        "repository_uid": inventory.repository_uid,
        "source_inventory_digest": inventory.digest,
        "scope_backend_overrides": [],
        "branch_bindings": [],
        "active_repairs": [],
        "worktrees": [],
    }
    mapping.write_text(json.dumps(payload), encoding="utf-8")
    result = run_vnext(
        ["workspace", "migrate", "--to-schema", "3", "--mapping-file", str(mapping), "--dry-run", "--json"],
        invocation_cwd=root,
        engine_digest=cast("str", common["engine_digest"]),
        engine_version="0.2.4",
    )
    assert result.exit_code == 0
    payload["source_inventory_digest"] = "sha256:" + "0" * 64
    mapping.write_text(json.dumps(payload), encoding="utf-8")
    rejected = run_vnext(
        ["workspace", "migrate", "--to-schema", "3", "--mapping-file", str(mapping), "--dry-run", "--json"],
        invocation_cwd=root,
        engine_digest=cast("str", common["engine_digest"]),
        engine_version="0.2.4",
    )
    assert rejected.exit_code == 3
