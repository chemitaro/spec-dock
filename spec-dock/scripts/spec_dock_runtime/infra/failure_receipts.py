"""Read-only failure receipts from the existing D-16 journal owners."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from spec_dock.installation.group_journal import read_group_record
from spec_dock_runtime.domain.operation import ROLLBACK_COMMANDS
from spec_dock_runtime.infra.control_store import load_control
from spec_dock_runtime.infra.engine_handover_store import pending_engine_handovers, read_engine_handover
from spec_dock_runtime.infra.finalization_store import pending_finalizations, read_finalization
from spec_dock_runtime.infra.installation_group_store import pending_installation_groups
from spec_dock_runtime.infra.migration_journal import pending_migrations, read_migration_record
from spec_dock_runtime.infra.operation_journal import JournalStore

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class ReceiptEffect:
    kind: str
    status: str
    target: str | None


@dataclass(frozen=True)
class FailureReceipt:
    operation_id: str
    command: str
    phase: str
    fixed_target: str | None
    fixed_kind: str | None
    fixed_backend: str | None
    effects: tuple[ReceiptEffect, ...]
    can_rollback: bool

    @property
    def effect_started(self) -> bool:
        return any(effect.status in {"succeeded", "unknown"} for effect in self.effects)


def pending_receipt_ids(common_dir: Path) -> set[str]:
    """Inventory the typed existing stores; never infer a journal from arbitrary files."""
    return {
        *(record.operation_id for record in JournalStore(common_dir).pending()),
        *pending_migrations(common_dir),
        *pending_installation_groups(common_dir),
        *pending_finalizations(common_dir),
        *pending_engine_handovers(common_dir),
    }


def pending_failure_receipts(common_dir: Path) -> tuple[FailureReceipt, ...]:
    receipts: list[FailureReceipt] = []
    for record in JournalStore(common_dir).pending():
        fixed = dict(record.fixed_targets)
        states = {
            "intent": "unknown",
            "succeeded": "succeeded",
            "unknown": "unknown",
            "failed": "failed",
            "not-applied": "not_attempted",
        }
        receipts.append(
            FailureReceipt(
                record.operation_id,
                record.command,
                record.phase,
                fixed.get("scope") or fixed.get("target"),
                fixed.get("kind"),
                fixed.get("backend"),
                tuple(ReceiptEffect(effect.id, states[effect.status], effect.target) for effect in record.effects),
                record.command in ROLLBACK_COMMANDS,
            )
        )
    for operation_id in pending_migrations(common_dir):
        record = read_migration_record(common_dir, operation_id)
        completed = set(record.completed_paths)
        effects = tuple(ReceiptEffect("migration-file", "succeeded", path) for path in record.completed_paths)
        if record.phase in {"applying", "recovery-required", "rollback-required"}:
            pending = next((item.path for item in record.files if item.path not in completed), None)
            if pending is not None:
                effects += (ReceiptEffect("migration-file", "unknown", pending),)
        receipts.append(
            FailureReceipt(operation_id, "workspace.migrate", record.phase, None, None, None, effects, True)
        )
    for operation_id in pending_installation_groups(common_dir):
        record = read_group_record(common_dir, operation_id)
        effects = tuple(
            ReceiptEffect("installation-target", "succeeded", item.worktree_id)
            for item in record.targets
            if item.completed
        )
        if record.phase in {"applying", "recovery-required"}:
            pending = next((item.worktree_id for item in record.targets if not item.completed), None)
            if pending is not None:
                effects += (ReceiptEffect("installation-target", "unknown", pending),)
        receipts.append(
            FailureReceipt(
                operation_id,
                "installation." + record.action,
                record.phase,
                None,
                None,
                None,
                effects,
                True,
            )
        )
    for operation_id in pending_finalizations(common_dir):
        record = read_finalization(common_dir, operation_id)
        control = load_control(common_dir)
        if control is not None and control.mode == "maintenance" and control.epoch == record.control_epoch:
            effects = ()
        elif (
            control is not None
            and control.mode == "ready"
            and control.epoch == record.control_epoch + 1
            and control.engine_digest == record.engine_digest
        ):
            effects = (ReceiptEffect("installation-finalize", "succeeded", str(common_dir)),)
        else:
            effects = (ReceiptEffect("installation-finalize", "unknown", str(common_dir)),)
        receipts.append(
            FailureReceipt(operation_id, "installation.update", record.phase, None, None, None, effects, False)
        )
    for operation_id in pending_engine_handovers(common_dir):
        record = read_engine_handover(common_dir, operation_id)
        # A prepared record precedes both pin replacement and control publication.
        # Its phase alone cannot prove that neither effect ran before the stop.
        effects = (ReceiptEffect("engine-handover", "unknown", str(common_dir)),)
        receipts.append(
            FailureReceipt(operation_id, "installation.update", record.phase, None, None, None, effects, True)
        )
    return tuple(receipts)
