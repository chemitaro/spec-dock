"""Build an immutable schema-three write set from a fixed legacy inventory."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

from spec_dock_runtime.cli.admission import admit_writer
from spec_dock_runtime.domain.lifecycle import decode_scope_metadata
from spec_dock_runtime.infra.control_store import WRITER_PROTOCOL, load_control, store_control
from spec_dock_runtime.infra.git_cli import worktree_list
from spec_dock_runtime.infra.migration_executor import (
    apply_migration_file,
    preflight_rollback_file,
    rollback_migration_file,
    snapshot_migration_file,
)
from spec_dock_runtime.infra.migration_journal import (
    MigrationFile,
    MigrationRecord,
    read_migration_record,
    write_migration_record,
)
from spec_dock_runtime.infra.migration_store import inspect_migration_inventory
from spec_dock_runtime.infra.writer_lock import writer_transaction

if TYPE_CHECKING:
    from spec_dock_runtime.infra.migration_store import MigrationInventory, MigrationMap


@dataclass(frozen=True)
class MigrationChange:
    path: str
    before_digest: str | None
    after_bytes: bytes


def _encode(payload: dict[str, object]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _snapshot(path: Path, expected_digest: str | None) -> tuple[dict[str, object] | None, str | None]:
    if path.is_symlink():
        raise ValueError("migration input path is redirected")
    if not path.exists():
        if expected_digest is not None:
            raise ValueError("migration input disappeared after inventory")
        return None, None
    data = path.read_bytes()
    digest = "sha256:" + hashlib.sha256(data).hexdigest()
    if digest != expected_digest:
        raise ValueError("migration input changed after inventory")
    try:
        payload = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("migration input is invalid JSON") from error
    if not isinstance(payload, dict):
        raise ValueError("migration input must be a JSON object")
    return payload, digest


def plan_migration_changes(
    inventory: MigrationInventory, mapping: MigrationMap, *, updated_at: str
) -> tuple[MigrationChange, ...]:
    """Prepare new bytes without changing any consumer file or Git history."""
    if (
        mapping.repository_uid != inventory.repository_uid
        or mapping.source_inventory_digest != inventory.digest
        or not updated_at
    ):
        raise ValueError("migration plan source identity is invalid")
    allowed_blockers = {"BACKEND_MAPPING_REQUIRED", "ACTIVE_REPAIR_REQUIRED", "WORKTREE_UNREGISTERED"}
    if set(inventory.blockers) - allowed_blockers:
        raise ValueError("migration inventory contains unresolved blockers")
    registered = {row["root"]: row["registration_id"] for row in mapping.worktrees}
    backend_overrides = {(row["worktree_id"], row["scope_id"]): row for row in mapping.scope_backend_overrides}
    repairs = {row["worktree_id"] for row in mapping.active_repairs}
    changes: list[MigrationChange] = []
    for worktree in inventory.worktrees:
        worktree_id = worktree.registration_id or registered.get(worktree.root)
        if not isinstance(worktree_id, str) or not worktree_id:
            raise ValueError("migration worktree requires an explicit registration")
        root = Path(worktree.root)
        for scope in worktree.scopes:
            if scope.id is None or scope.kind is None or scope.schema_version not in (1, 3):
                raise ValueError("migration Scope identity or schema is invalid")
            if set(scope.blockers) - {"BACKEND_MAPPING_REQUIRED"}:
                raise ValueError("migration Scope has an unresolved blocker")
            path = root / scope.path / ".meta.json"
            payload, digest = _snapshot(path, scope.digest)
            assert payload is not None
            if scope.schema_version == 3:
                decode_scope_metadata(payload)
                continue
            override = backend_overrides.get((worktree_id, scope.id))
            backend = override["backend"] if override is not None else scope.backend_candidate
            if backend not in ("github", "local"):
                raise ValueError("migration Scope backend needs explicit mapping")
            converted = dict(payload)
            converted.update(schema_version=3, revision=0, backend=backend)
            if backend == "local":
                converted["github"] = None
                converted["lifecycle"] = {"state": "open", "revision": 0, "updated_at": updated_at}
            else:
                if override is not None:
                    converted["github"] = override["github"]
                converted["lifecycle"] = None
            decode_scope_metadata(converted)
            changes.append(MigrationChange(str(path), digest, _encode(converted)))
        active_path = root / "spec-dock/.agent/active.json"
        if worktree.active_digest is not None:
            active, active_digest = _snapshot(active_path, worktree.active_digest)
            assert active is not None
            if "ACTIVE_REPAIR_REQUIRED" in worktree.blockers:
                if worktree_id not in repairs:
                    raise ValueError("migration active repair requires explicit mapping")
                selected: dict[str, object] = dict.fromkeys(("initiative", "epic", "issue"))
                focus = None
            else:
                selected = {role: active.get(role) for role in ("initiative", "epic", "issue")}
                focus = worktree.active_focus
            if active.get("schema_version") != 3 or "ACTIVE_REPAIR_REQUIRED" in worktree.blockers:
                converted_active: dict[str, object] = {
                    "schema_version": 3,
                    "worktree_id": worktree_id,
                    "revision": 0,
                    "focus_id": focus,
                    **selected,
                }
                changes.append(MigrationChange(str(active_path), active_digest, _encode(converted_active)))
        workspace_path = root / "spec-dock/workspace.json"
        workspace, workspace_digest = _snapshot(workspace_path, worktree.workspace_digest)
        if workspace is None:
            workspace = {}
        if worktree.workspace_schema not in (None, 1, 3):
            raise ValueError("migration workspace schema is unsupported")
        converted_workspace = dict(workspace)
        converted_workspace.update(schema_version=3, writer_protocol="specdock.writer/v1")
        if converted_workspace != workspace:
            changes.append(MigrationChange(str(workspace_path), workspace_digest, _encode(converted_workspace)))
    return tuple(changes)


def _finish_migration(common_dir: Path, record: MigrationRecord) -> MigrationRecord:
    control = load_control(common_dir)
    before = record.control_before
    if (
        control is None
        or before is None
        or control.mode != "maintenance"
        or control.engine_digest != record.engine_digest
    ):
        raise ValueError("migration lost maintenance control")
    desired_worktrees = tuple(
        replace(item, schema_version=3, writer_protocol=WRITER_PROTOCOL, engine_digest=record.engine_digest)
        if item.active
        else item
        for item in before.worktrees
    )
    desired = replace(before, epoch=record.control_epoch + 1, worktrees=desired_worktrees)
    if control == before:
        store_control(
            common_dir,
            desired,
            expected_epoch=control.epoch,
        )
    elif control != desired:
        raise ValueError("migration control changed during finalization")
    completed = replace(record, phase="committed", error=None)
    write_migration_record(common_dir, completed)
    return completed


def _continue_migration(common_dir: Path, record: MigrationRecord) -> MigrationRecord:
    for item in record.files:
        if item.path in record.completed_paths:
            _current, digest = snapshot_migration_file(record, item)
            if digest != item.after_digest:
                raise ValueError("completed migration file changed")
            continue
        apply_migration_file(record, item)
        record = replace(record, phase="applying", completed_paths=(*record.completed_paths, item.path), error=None)
        write_migration_record(common_dir, record)
    return _finish_migration(common_dir, record)


def apply_workspace_migration(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    inventory: MigrationInventory,
    mapping: MigrationMap,
    updated_at: str,
    lock_timeout: float = 0.0,
) -> MigrationRecord:
    """Apply one fixed migration under the common writer lock and maintenance mode."""
    changes = plan_migration_changes(inventory, mapping, updated_at=updated_at)
    roots = tuple((item.registration_id, item.root) for item in inventory.worktrees if item.registration_id is not None)
    if len(roots) != len(inventory.worktrees):
        raise ValueError("migration requires all worktrees to be registered before apply")
    with writer_transaction(common_dir, worktree_ids=tuple(item[0] for item in roots), timeout=lock_timeout):
        if inspect_migration_inventory(repo_root) != inventory:
            raise ValueError("migration inventory changed before the writer lock")
        control = load_control(common_dir)
        if control is None or control.mode != "maintenance":
            raise ValueError("migration requires maintenance control")
        admit_writer(
            control,
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
            maintenance_command="workspace.migrate",
        )
        record = MigrationRecord(
            uuid4().hex,
            str(common_dir),
            inventory.repository_uid,
            inventory.digest,
            engine_digest,
            control.epoch,
            roots,
            (),
            (),
            "prepared",
            control_before=control,
        )
        files: list[MigrationFile] = []
        for change in changes:
            placeholder = MigrationFile(change.path, None, change.after_bytes, None, _file_digest(change.after_bytes))
            before, before_digest = snapshot_migration_file(record, placeholder)
            if before_digest != change.before_digest:
                raise ValueError("migration file changed after planning")
            files.append(
                MigrationFile(change.path, before, change.after_bytes, before_digest, placeholder.after_digest)
            )
        record = replace(record, files=tuple(files))
        write_migration_record(common_dir, record, create=True)
        try:
            return _continue_migration(common_dir, record)
        except Exception as error:
            record = replace(
                read_migration_record(common_dir, record.operation_id), phase="recovery-required", error=str(error)
            )
            write_migration_record(common_dir, record)
            raise


def _file_digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def resume_workspace_migration(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    operation_id: str,
    lock_timeout: float = 0.0,
) -> MigrationRecord:
    """Continue only the fixed bytes and worktrees from an existing migration journal."""
    record = read_migration_record(common_dir, operation_id)
    if record.engine_digest != engine_digest or record.phase in {"rolled-back", "rollback-required"}:
        raise ValueError("migration operation is not resumable by this engine")
    if record.phase == "committed":
        return record
    with writer_transaction(common_dir, worktree_ids=tuple(item[0] for item in record.worktrees), timeout=lock_timeout):
        record = read_migration_record(common_dir, operation_id)
        if record.engine_digest != engine_digest or record.phase in {"rolled-back", "rollback-required"}:
            raise ValueError("migration operation is not resumable by this engine")
        if record.phase == "committed":
            return record
        observed = worktree_list(repo_root)
        if any(item.bare or item.path.is_symlink() or not item.path.is_dir() for item in observed) or {
            str(item.path.resolve(strict=True)) for item in observed
        } != {root for _id, root in record.worktrees}:
            raise ValueError("migration recovery worktree inventory changed")
        control = load_control(common_dir)
        if control is None or control.mode != "maintenance":
            raise ValueError("migration recovery requires maintenance control")
        admit_writer(
            control,
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=control.epoch,
            recovery_operation_id=operation_id,
        )
        try:
            return _continue_migration(common_dir, record)
        except Exception as error:
            failed = replace(
                read_migration_record(common_dir, operation_id), phase="recovery-required", error=str(error)
            )
            write_migration_record(common_dir, failed)
            raise


def rollback_workspace_migration(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    operation_id: str,
    lock_timeout: float = 0.0,
) -> MigrationRecord:
    """Restore fixed pre-migration bytes without overwriting later user changes."""
    record = read_migration_record(common_dir, operation_id)
    if record.engine_digest != engine_digest:
        raise ValueError("migration rollback engine differs")
    if record.phase == "rolled-back":
        return record
    with writer_transaction(common_dir, worktree_ids=tuple(item[0] for item in record.worktrees), timeout=lock_timeout):
        record = read_migration_record(common_dir, operation_id)
        if record.engine_digest != engine_digest:
            raise ValueError("migration rollback engine differs")
        if record.phase == "rolled-back":
            return record
        observed = worktree_list(repo_root)
        if any(item.bare or item.path.is_symlink() or not item.path.is_dir() for item in observed) or {
            str(item.path.resolve(strict=True)) for item in observed
        } != {root for _id, root in record.worktrees}:
            raise ValueError("migration rollback worktree inventory changed")
        control = load_control(common_dir)
        before = record.control_before
        if control is None or before is None or control.mode != "maintenance":
            raise ValueError("migration rollback requires maintenance control")
        committed = record.phase == "committed"
        if committed and control.epoch != record.control_epoch + 1:
            raise ValueError("migration rollback refuses a later control epoch")
        if not committed and control.epoch not in {
            record.control_epoch,
            record.control_epoch + 1,
            record.control_epoch + 2,
        }:
            raise ValueError("migration rollback refuses a later control epoch")
        admit_writer(
            control,
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=control.epoch,
            **({"maintenance_command": "workspace.migrate"} if committed else {"recovery_operation_id": operation_id}),
        )
        desired_worktrees = tuple(
            replace(item, schema_version=3, writer_protocol=WRITER_PROTOCOL, engine_digest=record.engine_digest)
            if item.active
            else item
            for item in before.worktrees
        )
        if control.worktrees not in (before.worktrees, desired_worktrees):
            raise ValueError("migration rollback control registration changed")
        for item in record.files:
            preflight_rollback_file(record, item)
        try:
            record = replace(record, phase="rollback-required", error=None)
            write_migration_record(common_dir, record)
            for item in reversed(record.files):
                rollback_migration_file(record, item)
            if control.worktrees != before.worktrees:
                restored = replace(control, epoch=control.epoch + 1, worktrees=before.worktrees)
                store_control(common_dir, restored, expected_epoch=control.epoch)
            completed = replace(record, phase="rolled-back", error=None)
            write_migration_record(common_dir, completed)
            return completed
        except Exception as error:
            failed = replace(
                read_migration_record(common_dir, operation_id), phase="rollback-required", error=str(error)
            )
            write_migration_record(common_dir, failed)
            raise
