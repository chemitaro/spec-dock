"""Fail-closed admission for mutations sharing one Git common directory."""

from __future__ import annotations

from typing import TYPE_CHECKING

from spec_dock_runtime.infra.control_store import WORKSPACE_SCHEMA, WRITER_PROTOCOL, ControlState
from spec_dock_runtime.infra.installation_group_store import pending_installation_groups
from spec_dock_runtime.infra.operation_journal import JournalStore

if TYPE_CHECKING:
    from pathlib import Path

_MAINTENANCE_COMMANDS = frozenset({
    "workspace.migrate",
    "installation.init",
    "installation.update",
    "installation.uninstall",
})


class AdmissionError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def admit_writer(
    control: ControlState | None,
    *,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    maintenance_command: str | None = None,
    recovery_operation_id: str | None = None,
) -> None:
    """Run under the common writer lock immediately before any mutation."""
    if control is None or control.mode == "uninitialized":
        raise AdmissionError("CONTROL_UNINITIALIZED", "repository control is uninitialized")
    if control.schema_version != WORKSPACE_SCHEMA or control.writer_protocol != WRITER_PROTOCOL:
        raise AdmissionError("WRITER_PROTOCOL_MISMATCH", "repository writer protocol or schema is incompatible")
    if control.epoch != expected_epoch:
        raise AdmissionError("CONTROL_EPOCH_CHANGED", "repository control epoch changed")
    if control.engine_digest != engine_digest:
        raise AdmissionError("ENGINE_MISMATCH", "writer engine digest does not match repository control")
    registered = {item.id: item for item in control.worktrees}
    if worktree_id not in registered or not registered[worktree_id].active:
        raise AdmissionError("WORKTREE_UNREGISTERED", "current worktree is not active in the control inventory")
    operations = JournalStore(common_dir).pending()
    blocking = tuple(item for item in operations if item.terminal_status in {"pending", "unknown"})
    pending_groups = pending_installation_groups(common_dir)
    pending_ids = {item.operation_id for item in blocking} | set(pending_groups)
    if recovery_operation_id is not None:
        if len(blocking) + len(pending_groups) != 1 or pending_ids != {recovery_operation_id}:
            raise AdmissionError(
                "RECOVERY_TARGET_MISMATCH", "recovery operation does not match a pending blocking journal"
            )
        return
    if pending_ids or control.mode == "recovery-required":
        raise AdmissionError("RECOVERY_REQUIRED", "pending blocking journal requires explicit recovery")
    if control.mode == "maintenance" and maintenance_command not in _MAINTENANCE_COMMANDS:
        raise AdmissionError("MAINTENANCE_REQUIRED", "repository is in maintenance mode")
    if maintenance_command is not None and maintenance_command not in _MAINTENANCE_COMMANDS:
        raise AdmissionError("INVALID_MAINTENANCE_COMMAND", "command cannot write during maintenance")
    if control.mode == "maintenance" and maintenance_command is not None:
        return
    if any(
        item.active
        and (
            item.schema_version != WORKSPACE_SCHEMA
            or item.writer_protocol != WRITER_PROTOCOL
            or item.engine_digest != engine_digest
        )
        for item in control.worktrees
    ):
        raise AdmissionError("WRITER_PROTOCOL_MISMATCH", "an active worktree uses an incompatible writer protocol")
