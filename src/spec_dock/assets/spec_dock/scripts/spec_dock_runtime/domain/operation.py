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
EffectStatus = Literal["intent", "succeeded", "failed", "unknown", "not-applied"]
TerminalStatus = Literal["pending", "succeeded", "failed", "unknown", "rolled-back"]


@dataclass(frozen=True)
class OperationEffect:
    id: str
    kind: Literal["local", "git", "remote"]
    target: str
    status: EffectStatus
    retry_of: str | None = None
    after_revisions: tuple[tuple[str, int], ...] = ()

    def __post_init__(self) -> None:
        if not self.id or not self.target:
            raise ValueError("effect ID and target are required")
        if self.after_revisions and self.status != "succeeded":
            raise ValueError("only succeeded effects may hold after revisions")
        if self.after_revisions != tuple(sorted(self.after_revisions)):
            raise ValueError("effect after revisions must be sorted")


@dataclass(frozen=True)
class OperationRecord:
    operation_id: str
    command: str
    fixed_targets: tuple[tuple[str, str], ...]
    effect_plan: tuple[str, ...]
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
        if (
            not self.effect_plan
            or len(set(self.effect_plan)) != len(self.effect_plan)
            or any(not item or "#" in item for item in self.effect_plan)
        ):
            raise ValueError("operation effect plan must be nonempty and unique")
        if len({effect.id for effect in self.effects}) != len(self.effects):
            raise ValueError("operation effect IDs must be unique")
        completed: set[str] = set()
        for effect in self.effects:
            logical_id = effect.retry_of or effect.id
            if logical_id not in self.effect_plan:
                raise ValueError("effect is absent from the fixed effect plan")
            expected_index = len(completed)
            if expected_index >= len(self.effect_plan) or self.effect_plan[expected_index] != logical_id:
                raise ValueError("effect does not follow the fixed effect plan")
            if effect.status == "succeeded":
                completed.add(logical_id)
        if self.terminal_status == "succeeded" and completed != set(self.effect_plan):
            raise ValueError("terminal success requires the complete effect plan")
        if self.terminal_status in ("failed", "rolled-back") and any(
            effect.status in ("intent", "unknown") for effect in self.effects
        ):
            raise ValueError("terminal state cannot contain unresolved effects")
        if self.terminal_status == "failed" and any(effect.status == "succeeded" for effect in self.effects):
            raise ValueError("terminal failure cannot hide applied effects")
