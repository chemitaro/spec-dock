"""Fail-closed admission for mutations sharing one Git common directory."""

from __future__ import annotations

from dataclasses import dataclass

from spec_dock_runtime.infra.control_store import WORKSPACE_SCHEMA, WRITER_PROTOCOL, ControlState

_BLOCKING_COMMANDS = frozenset({
    "scope.create",
    "scope.import",
    "scope.close",
    "scope.reopen",
    "scope.delete",
    "work.start",
    "work.finish",
    "branch.create",
    "workspace.migrate",
    "installation.init",
    "installation.update",
    "installation.uninstall",
})
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


@dataclass(frozen=True)
class PendingOperation:
    operation_id: str
    command: str
    terminal_status: str
    blocking: bool


def admit_writer(
    control: ControlState | None,
    *,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    operations: tuple[PendingOperation, ...] = (),
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
    blocking = tuple(
        item
        for item in operations
        if item.blocking and item.command in _BLOCKING_COMMANDS and item.terminal_status in {"pending", "unknown"}
    )
    if recovery_operation_id is not None:
        if len(blocking) != 1 or blocking[0].operation_id != recovery_operation_id:
            raise AdmissionError(
                "RECOVERY_TARGET_MISMATCH", "recovery operation does not match a pending blocking journal"
            )
        return
    if blocking or control.mode == "recovery-required":
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
