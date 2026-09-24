"""Durable, fixed-target journals for D-16 recoverable operations."""

from __future__ import annotations

from dataclasses import asdict
import json
import re
from typing import TYPE_CHECKING, cast

from spec_dock_runtime.domain.operation import OperationEffect, OperationRecord, TerminalStatus
from spec_dock_runtime.infra.control_store import control_directory
from spec_dock_runtime.infra.json_store import atomic_write_json

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
        if (
            not isinstance(effect_id, str)
            or kind not in ("local", "git", "remote")
            or not isinstance(target, str)
            or status not in ("intent", "succeeded", "failed", "unknown")
        ):
            raise ValueError("invalid journal effect")
        effects.append(OperationEffect(effect_id, kind, target, status))
    fixed_targets = _pairs(payload.get("fixed_targets"), values=str)
    before_revisions = _pairs(payload.get("before_revisions"), values=int)
    return OperationRecord(
        operation_id=operation_id,
        command=command,
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
        self.root.mkdir(parents=True, exist_ok=True)
        if self.root.is_symlink():
            raise ValueError("operations directory must not be a symlink")
        path.parent.mkdir(mode=0o700, exist_ok=False)
        try:
            atomic_write_json(path, asdict(record))
        except BaseException:
            path.parent.rmdir()
            raise

    def load(self, operation_id: str) -> OperationRecord:
        path = self._path(operation_id)
        if path.parent.is_symlink() or path.is_symlink():
            raise ValueError("journal path must not be a symlink")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError("invalid journal JSON") from exc
        record = _decode(payload)
        if record.operation_id != operation_id:
            raise ValueError("journal ID and directory disagree")
        return record

    def update(self, record: OperationRecord, *, expected_sequence: int) -> None:
        path = self._path(record.operation_id)
        current = self.load(record.operation_id)
        if current.sequence != expected_sequence or record.sequence != expected_sequence + 1:
            raise ValueError("journal sequence changed")
        if any(
            getattr(current, field) != getattr(record, field)
            for field in (
                "operation_id",
                "command",
                "fixed_targets",
                "request_fingerprint",
                "before_revisions",
                "engine_digest",
                "writer_epoch",
            )
        ):
            raise ValueError("journal fixed operation identity changed")
        metadata = path.lstat()
        atomic_write_json(path, asdict(record), expected_identity=(metadata.st_dev, metadata.st_ino))

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
