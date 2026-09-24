"""Durable, fixed-target journals for D-16 recoverable operations."""

from __future__ import annotations

from dataclasses import asdict
import os
import re
from typing import TYPE_CHECKING, cast

from spec_dock_runtime.domain.operation import ROLLBACK_COMMANDS, OperationEffect, OperationRecord, TerminalStatus
from spec_dock_runtime.infra.control_store import control_directory
from spec_dock_runtime.infra.json_store import atomic_write_json, read_guarded_json

if TYPE_CHECKING:
    from pathlib import Path

_OPERATION_ID = re.compile(r"^[0-9a-f]{32}$")


def _pairs(
    payload: object, *, values: type[str] | type[int]
) -> tuple[tuple[str, str], ...] | tuple[tuple[str, int], ...]:
    if not isinstance(payload, list):
        raise ValueError("journal pairs must be a list")
    result: list[tuple[str, str | int]] = []
    for pair in payload:
        if not isinstance(pair, list) or len(pair) != 2 or not isinstance(pair[0], str) or type(pair[1]) is not values:
            raise ValueError("invalid journal pair")
        result.append((pair[0], pair[1]))
    if result != sorted(result) or len({key for key, _ in result}) != len(result):
        raise ValueError("journal pairs must have unique sorted keys")
    return cast("tuple[tuple[str, str], ...] | tuple[tuple[str, int], ...]", tuple(result))


def _decode(payload: object) -> OperationRecord:
    if not isinstance(payload, dict):
        raise ValueError("journal must be a JSON object")
    operation_id = payload.get("operation_id")
    command = payload.get("command")
    effect_plan = payload.get("effect_plan")
    fingerprint = payload.get("request_fingerprint")
    phase = payload.get("phase")
    digest = payload.get("engine_digest")
    epoch = payload.get("writer_epoch")
    terminal = payload.get("terminal_status")
    sequence = payload.get("sequence")
    backups = payload.get("backup_refs")
    effects_raw = payload.get("effects")
    if (
        not isinstance(operation_id, str)
        or not _OPERATION_ID.fullmatch(operation_id)
        or not isinstance(command, str)
        or not isinstance(effect_plan, list)
        or not all(isinstance(item, str) for item in effect_plan)
        or not isinstance(fingerprint, str)
        or not isinstance(phase, str)
        or not isinstance(digest, str)
        or type(epoch) is not int
        or type(sequence) is not int
        or terminal not in ("pending", "succeeded", "failed", "unknown", "rolled-back")
        or not isinstance(backups, list)
        or not all(isinstance(item, str) for item in backups)
        or not isinstance(effects_raw, list)
    ):
        raise ValueError("invalid journal header")
    effects: list[OperationEffect] = []
    for item in effects_raw:
        if not isinstance(item, dict):
            raise ValueError("invalid journal effect")
        effect_id, kind, target, status = (item.get(key) for key in ("id", "kind", "target", "status"))
        retry_of = item.get("retry_of")
        remote_ref = item.get("remote_ref")
        if (
            not isinstance(effect_id, str)
            or kind not in ("local", "git", "remote")
            or not isinstance(target, str)
            or status not in ("intent", "succeeded", "failed", "unknown", "not-applied")
            or (retry_of is not None and not isinstance(retry_of, str))
            or (remote_ref is not None and not isinstance(remote_ref, str))
        ):
            raise ValueError("invalid journal effect")
        after_revisions = _pairs(item.get("after_revisions", []), values=int)
        effects.append(OperationEffect(effect_id, kind, target, status, retry_of, after_revisions, remote_ref))
    fixed_targets = _pairs(payload.get("fixed_targets"), values=str)
    before_revisions = _pairs(payload.get("before_revisions"), values=int)
    return OperationRecord(
        operation_id=operation_id,
        command=command,
        effect_plan=tuple(effect_plan),
        fixed_targets=cast("tuple[tuple[str, str], ...]", fixed_targets),
        request_fingerprint=fingerprint,
        before_revisions=cast("tuple[tuple[str, int], ...]", before_revisions),
        phase=phase,
        effects=tuple(effects),
        backup_refs=tuple(backups),
        engine_digest=digest,
        writer_epoch=epoch,
        terminal_status=cast("TerminalStatus", terminal),
        sequence=sequence,
    )


class JournalStore:
    def __init__(self, common_dir: Path) -> None:
        self.root = control_directory(common_dir) / "operations"

    def _path(self, operation_id: str) -> Path:
        if not _OPERATION_ID.fullmatch(operation_id):
            raise ValueError("invalid operation ID")
        return self.root / operation_id / "journal.json"

    def create(self, record: OperationRecord) -> None:
        if record.sequence != 0 or record.terminal_status != "pending":
            raise ValueError("new journal must start pending at sequence zero")
        path = self._path(record.operation_id)
        _ensure_durable_directory(self.root)
        path.parent.mkdir(mode=0o700, exist_ok=False)
        _fsync_directory(self.root)
        atomic_write_json(path, asdict(record))

    def load(self, operation_id: str) -> OperationRecord:
        return self.load_with_identity(operation_id)[0]

    def load_with_identity(self, operation_id: str) -> tuple[OperationRecord, tuple[int, int]]:
        path = self._path(operation_id)
        if path.parent.is_symlink() or path.is_symlink():
            raise ValueError("journal path must not be a symlink")
        try:
            loaded = read_guarded_json(path)
        except (ValueError, UnicodeDecodeError) as exc:
            raise ValueError("invalid journal JSON") from exc
        if loaded is None:
            raise FileNotFoundError(path)
        payload, identity = loaded
        record = _decode(payload)
        if record.operation_id != operation_id:
            raise ValueError("journal ID and directory disagree")
        return record, identity

    def update(self, record: OperationRecord, *, expected_sequence: int) -> None:
        path = self._path(record.operation_id)
        current, identity = self.load_with_identity(record.operation_id)
        if current.sequence != expected_sequence or record.sequence != expected_sequence + 1:
            raise ValueError("journal sequence changed")
        if any(
            getattr(current, field) != getattr(record, field)
            for field in (
                "operation_id",
                "command",
                "effect_plan",
                "fixed_targets",
                "request_fingerprint",
                "before_revisions",
                "engine_digest",
                "writer_epoch",
            )
        ):
            raise ValueError("journal fixed operation identity changed")
        _assert_journal_transition(current, record)
        atomic_write_json(path, asdict(record), expected_identity=identity)

    def pending(self) -> tuple[OperationRecord, ...]:
        if not self.root.exists():
            return ()
        if self.root.is_symlink():
            raise ValueError("operations directory must not be a symlink")
        pending: list[OperationRecord] = []
        for directory in sorted(self.root.iterdir()):
            if directory.is_symlink() or not directory.is_dir():
                raise ValueError("invalid operation directory")
            record = self.load(directory.name)
            if record.terminal_status in ("pending", "unknown"):
                pending.append(record)
        return tuple(pending)


def _fsync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _ensure_durable_directory(path: Path) -> None:
    missing: list[Path] = []
    cursor = path
    while not cursor.exists():
        missing.append(cursor)
        cursor = cursor.parent
    if any(parent.is_symlink() for parent in (cursor, *cursor.parents)) or not cursor.is_dir():
        raise ValueError("journal directory must not be redirected")
    for directory in reversed(missing):
        directory.mkdir(mode=0o700)
        _fsync_directory(directory.parent)


def _assert_journal_transition(before: OperationRecord, after: OperationRecord) -> None:
    if before.terminal_status not in ("pending", "unknown"):
        raise ValueError("terminal journal cannot change")
    if after.terminal_status == "rolled-back" and (
        after.command not in ROLLBACK_COMMANDS or after.phase != "rollback-verified"
    ):
        raise ValueError("rollback requires a verified recovery executor")
    if len(after.effects) < len(before.effects) or len(after.effects) > len(before.effects) + 1:
        raise ValueError("journal effect history cannot be removed or skipped")
    if len(after.effects) == len(before.effects) + 1:
        if after.effects[:-1] != before.effects or after.effects[-1].status != "intent":
            raise ValueError("journal effect addition must preserve history and start with intent")
        appended = after.effects[-1]
        if appended.retry_of is not None:
            prior = [
                effect
                for effect in before.effects
                if effect.id == appended.retry_of or effect.retry_of == appended.retry_of
            ]
            if (
                not prior
                or prior[-1].status != "not-applied"
                or (prior[-1].kind, prior[-1].target) != (appended.kind, appended.target)
            ):
                raise ValueError("journal effect retry requires observed non-application")
        elif any(effect.id == appended.id for effect in before.effects):
            raise ValueError("journal effect ID is duplicated")
        if before.effects and before.effects[-1].status not in ("succeeded", "not-applied"):
            raise ValueError("journal has an unresolved effect")
    else:
        changed = [
            index for index, (old, new) in enumerate(zip(before.effects, after.effects, strict=True)) if old != new
        ]
        if len(changed) > 1 or (changed and changed[0] != len(before.effects) - 1):
            raise ValueError("journal effect history cannot be reordered or rewritten")
        if changed:
            old, new = before.effects[-1], after.effects[-1]
            if (old.id, old.kind, old.target, old.retry_of) != (new.id, new.kind, new.target, new.retry_of):
                raise ValueError("journal effect identity cannot change")
            allowed = {
                "intent": {"succeeded", "failed", "unknown"},
                "unknown": {"succeeded", "not-applied", "unknown"},
            }
            if new.status not in allowed.get(old.status, set()):
                raise ValueError("journal effect status transition is invalid")
    if after.backup_refs[: len(before.backup_refs)] != before.backup_refs:
        raise ValueError("journal backup references are append-only")
    if after.terminal_status == "succeeded" and any(effect.status != "succeeded" for effect in after.effects):
        raise ValueError("journal terminal success has incomplete effects")
    if after.terminal_status in ("failed", "rolled-back") and any(
        effect.status in ("intent", "unknown") for effect in after.effects
    ):
        raise ValueError("journal terminal state has unresolved effects")
