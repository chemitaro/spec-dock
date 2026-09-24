"""Read-only migration planning before any schema conversion is admitted."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from spec_dock_runtime.infra.migration_store import MigrationInventory, inspect_migration_inventory, read_migration_map
from spec_dock_runtime.presentation.envelope import Effect, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock_runtime.commands.work_vnext import WorkContext


def run_workspace_migrate(
    ns: argparse.Namespace, context: WorkContext, *, invocation_cwd: Path
) -> OperationResult[MigrationInventory]:
    if ns.to_schema != "3":
        raise ValueError("workspace migrate supports only --to-schema 3")
    if ns.resume or ns.rollback:
        raise ValueError("workspace migration recovery is not connected")
    if not ns.dry_run:
        raise ValueError("workspace migration requires a dry run before apply is connected")
    inventory = inspect_migration_inventory(context.repo_root)
    if ns.mapping_file:
        mapping_path = Path(ns.mapping_file).expanduser()
        if not mapping_path.is_absolute():
            mapping_path = invocation_cwd / mapping_path
        read_migration_map(mapping_path, inventory)
    return OperationResult(
        ns.command_path,
        "planned",
        inventory,
        0,
        effects=(Effect("workspace-migration", "planned", inventory.repository_uid),),
    )
