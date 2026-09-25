"""CLI adapter for inventory-bound schema migration and fixed-journal recovery."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path
from typing import TYPE_CHECKING

from spec_dock_runtime.application.migrate_workspace_vnext import (
    apply_workspace_migration,
    inspect_workspace_migration,
    prepare_workspace_migration,
    resume_workspace_migration,
    rollback_workspace_migration,
)
from spec_dock_runtime.presentation.envelope import Effect, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock_runtime.commands.work_vnext import WorkContext


@dataclass(frozen=True)
class MigrationOutcome:
    operation_id: str
    source_inventory_digest: str
    phase: str
    changed_files: int
    worktrees: tuple[str, ...]


@dataclass(frozen=True)
class MigrationPreviewFile:
    path: str
    before_digest: str | None
    action: str
    after_digest: str


@dataclass(frozen=True)
class MigrationPreview:
    common_dir: str
    repository_uid: str
    control_digest: str | None
    digest: str
    worktrees: tuple[object, ...]
    blockers: tuple[str, ...]
    changes: tuple[MigrationPreviewFile, ...]


def run_workspace_migrate(
    ns: argparse.Namespace, context: WorkContext, *, invocation_cwd: Path
) -> OperationResult[MigrationPreview | MigrationOutcome]:
    if ns.to_schema != "3":
        raise ValueError("workspace migrate supports only --to-schema 3")
    if (ns.resume or ns.rollback) and (ns.dry_run or ns.mapping_file):
        raise ValueError("workspace migration recovery accepts only its operation ID")
    if not ns.dry_run and not ns.yes:
        raise ValueError("workspace migration apply and recovery require --yes")
    common = {
        "repo_root": context.repo_root,
        "common_dir": context.common_dir,
        "worktree_id": context.worktree_id,
        "engine_digest": context.engine_digest,
        "lock_timeout": ns.lock_timeout,
    }
    if ns.resume or ns.rollback:
        record = (
            resume_workspace_migration(operation_id=ns.resume, **common)
            if ns.resume
            else rollback_workspace_migration(operation_id=ns.rollback, **common)
        )
        outcome = MigrationOutcome(
            record.operation_id,
            record.source_inventory_digest,
            record.phase,
            len(record.files),
            tuple(root for _id, root in record.worktrees),
        )
        return OperationResult(
            ns.command_path,
            "succeeded",
            outcome,
            0,
            operation_id=record.operation_id,
            effects=(Effect("workspace-migration", "succeeded", record.operation_id),),
        )
    inventory = inspect_workspace_migration(context.repo_root)
    prepared = getattr(ns, "_prepared_migration_plan", None)
    mapping = None
    if ns.mapping_file:
        mapping_path = Path(ns.mapping_file).expanduser()
        if not mapping_path.is_absolute():
            mapping_path = invocation_cwd / mapping_path
        if prepared is None:
            prepared = prepare_workspace_migration(
                inventory, mapping_path, updated_at=datetime.now(timezone.utc).isoformat()
            )
        elif prepared.mapping_path != mapping_path or prepared.inventory != inventory:
            raise ValueError("migration prepared plan no longer matches the target inventory")
        mapping = prepared.mapping
    if ns.dry_run:
        changes = prepared.changes if prepared is not None else ()
        ns._prepared_migration_plan = prepared
        preview = MigrationPreview(
            inventory.common_dir,
            inventory.repository_uid,
            inventory.control_digest,
            inventory.digest,
            inventory.worktrees,
            inventory.blockers,
            tuple(
                MigrationPreviewFile(
                    item.path,
                    item.before_digest,
                    "create" if item.before_digest is None else "replace",
                    "sha256:" + hashlib.sha256(item.after_bytes).hexdigest(),
                )
                for item in changes
            ),
        )
        return OperationResult(
            ns.command_path,
            "planned",
            preview,
            0,
            effects=tuple(Effect("write-file", "planned", item.path) for item in changes),
        )
    if mapping is None:
        raise ValueError("workspace migration apply requires an inventory-bound --mapping-file")
    assert prepared is not None
    record = apply_workspace_migration(
        expected_epoch=context.expected_epoch,
        inventory=inventory,
        mapping=mapping,
        updated_at=prepared.updated_at,
        prepared=prepared,
        **common,
    )
    outcome = MigrationOutcome(
        record.operation_id,
        record.source_inventory_digest,
        record.phase,
        len(record.files),
        tuple(root for _id, root in record.worktrees),
    )
    return OperationResult(
        ns.command_path,
        "succeeded",
        outcome,
        0,
        operation_id=record.operation_id,
        effects=(Effect("workspace-migration", "succeeded", record.operation_id),),
    )
