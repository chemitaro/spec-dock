"""Read-only failure receipts from the existing D-16 journal owners."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from spec_dock.installation.group_journal import read_group_record
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
    can_resume: bool
    can_rollback: bool
    commands: tuple[tuple[str, ...], ...]
    blocked_reason: str | None = None

    @property
    def effect_started(self) -> bool:
        return any(effect.status in {"succeeded", "unknown"} for effect in self.effects)


def _operation_commands(record: object) -> tuple[tuple[str, ...], ...]:
    """Construct recovery argv from the fixed request owned by the operation journal."""
    from spec_dock_runtime.domain.operation import OperationRecord

    assert isinstance(record, OperationRecord)
    fixed = dict(record.fixed_targets)
    command = record.command
    target = fixed.get("scope") or fixed.get("target")
    prefix: tuple[str, ...]
    if command == "scope.create":
        kind = fixed.get("kind")
        if kind not in {"initiative", "epic", "issue"} or not {"title", "slug", "parent"} <= fixed.keys():
            return ()
        backend = "github" if "github-create" in record.effect_plan else "local"
        prefix = ("spec-dock", "scope", "create", kind, "--backend", backend, "--title", fixed["title"])
        if fixed.get("parent"):
            prefix += ("--parent", fixed["parent"])
        prefix += ("--slug", fixed["slug"])
    elif command == "scope.import":
        kind = fixed.get("kind")
        if kind not in {"initiative", "epic", "issue"} or not {"github_ref", "title", "slug", "parent"} <= fixed.keys():
            return ()
        prefix = ("spec-dock", "scope", "import", "github", kind, fixed["github_ref"], "--title", fixed["title"])
        if fixed.get("parent"):
            prefix += ("--parent", fixed["parent"])
        prefix += ("--slug", fixed["slug"])
    elif command in {"scope.close", "scope.reopen"} and target and (command != "scope.close" or "reason" in fixed):
        prefix = ("spec-dock", "scope", command.split(".")[1], target)
        if command == "scope.close":
            prefix += ("--reason", fixed["reason"])
    elif command == "scope.delete" and target:
        prefix = ("spec-dock", "scope", "delete", target)
    elif (
        command == "work.start"
        and target
        and {"readiness_source", "allow_stale", "offline", "switch_active"} <= fixed.keys()
    ):
        prefix = ("spec-dock", "work", "start", target, "--source", fixed["readiness_source"])
        for key, flag in (
            ("allow_stale", "--allow-stale"),
            ("offline", "--offline"),
            ("switch_active", "--switch-active"),
        ):
            if fixed[key] == "true":
                prefix += (flag,)
    elif command == "work.finish" and target:
        prefix = ("spec-dock", "work", "finish", target)
    elif command == "branch.create" and target:
        prefix = ("spec-dock", "branch", "create", target)
    else:
        return ()
    resume = (*prefix, "--resume", record.operation_id, "--yes")
    rollback = (*prefix, "--rollback", record.operation_id, "--yes") if command == "scope.delete" else None
    return (resume, rollback) if rollback is not None else (resume,)


def _installation_commands(record: object) -> tuple[tuple[str, ...], ...]:
    from spec_dock.installation.group_journal import InstallationGroupRecord

    assert isinstance(record, InstallationGroupRecord)
    prefix: tuple[str, ...] = ("spec-dock", "installation", record.action)
    if record.action == "init":
        if not record.targets:
            return ()
        prefix += (record.targets[0].root,)
    elif record.action == "update":
        if not record.source_commit:
            return ()
        prefix += ("--commit", record.source_commit)
        if record.keep_maintenance:
            prefix += ("--maintenance",)
    elif record.action != "uninstall":
        return ()
    return (
        (*prefix, "--resume", record.operation_id, "--yes"),
        ("spec-dock", "installation", record.action, "--rollback", record.operation_id, "--yes"),
    )


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
        commands = _operation_commands(record)
        receipts.append(
            FailureReceipt(
                record.operation_id,
                record.command,
                record.phase,
                fixed.get("scope") or fixed.get("target"),
                fixed.get("kind"),
                fixed.get("backend")
                or (
                    "github"
                    if "github-create" in record.effect_plan
                    else "local"
                    if record.command == "scope.create"
                    else None
                ),
                tuple(ReceiptEffect(effect.id, states[effect.status], effect.target) for effect in record.effects),
                bool(commands),
                len(commands) > 1,
                commands,
                None if commands else "Recorded request cannot be reconstructed; inspect the operation journal.",
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
        prefix = ("spec-dock", "workspace", "migrate", "--to-schema", "3")
        resume = record.phase not in {"rollback-required"}
        commands = (((*prefix, "--resume", operation_id, "--yes"),) if resume else ()) + (
            (*prefix, "--rollback", operation_id, "--yes"),
        )
        receipts.append(
            FailureReceipt(
                operation_id, "workspace.migrate", record.phase, None, None, None, effects, resume, True, commands
            )
        )
    for operation_id in pending_installation_groups(common_dir):
        record = read_group_record(common_dir, operation_id)
        commands = _installation_commands(record)
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
                bool(commands),
                len(commands) > 1,
                commands,
                None if commands else "Recorded installation source or targets are unavailable.",
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
            FailureReceipt(
                operation_id,
                "installation.update",
                record.phase,
                None,
                None,
                None,
                effects,
                True,
                False,
                (("spec-dock", "installation", "update", "--finalize", "--resume", operation_id, "--yes"),),
            )
        )
    for operation_id in pending_engine_handovers(common_dir):
        record = read_engine_handover(common_dir, operation_id)
        # A prepared record precedes both pin replacement and control publication.
        # Its phase alone cannot prove that neither effect ran before the stop.
        effects = (ReceiptEffect("engine-handover", "unknown", str(common_dir)),)
        receipts.append(
            FailureReceipt(
                operation_id,
                "installation.update",
                record.phase,
                None,
                None,
                None,
                effects,
                True,
                True,
                (
                    ("spec-dock", "installation", "update", "--activate-engine", "--resume", operation_id, "--yes"),
                    ("spec-dock", "installation", "update", "--activate-engine", "--rollback", operation_id, "--yes"),
                ),
            )
        )
    return tuple(receipts)
