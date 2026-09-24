"""Fixed, resumable operation records for the D-16 command allowlist."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

BLOCKING_COMMANDS = frozenset({
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
ROLLBACK_COMMANDS = frozenset({
    "scope.delete",
    "workspace.migrate",
    "installation.init",
    "installation.update",
    "installation.uninstall",
})
EffectStatus = Literal["intent", "succeeded", "failed", "unknown"]
TerminalStatus = Literal["pending", "succeeded", "failed", "unknown", "rolled-back"]


@dataclass(frozen=True)
class OperationEffect:
    id: str
    kind: Literal["local", "git", "remote"]
    target: str
    status: EffectStatus


@dataclass(frozen=True)
class OperationRecord:
    operation_id: str
    command: str
    fixed_targets: tuple[tuple[str, str], ...]
    request_fingerprint: str
    before_revisions: tuple[tuple[str, int], ...]
    phase: str
    effects: tuple[OperationEffect, ...]
    backup_refs: tuple[str, ...]
    engine_digest: str
    writer_epoch: int
    terminal_status: TerminalStatus
    sequence: int

    def __post_init__(self) -> None:
        if self.command not in BLOCKING_COMMANDS:
            raise ValueError("blocking journal is unavailable for this command")
        if self.writer_epoch < 0 or self.sequence < 0:
            raise ValueError("operation version must be nonnegative")
        if not self.operation_id or not self.request_fingerprint or not self.engine_digest:
            raise ValueError("operation identity, fingerprint, and engine digest are required")
