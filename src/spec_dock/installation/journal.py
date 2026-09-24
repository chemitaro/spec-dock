"""Durable installation operation records outside replaced tooling directories."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import re
import uuid

_ID = re.compile(r"[0-9a-f]{32}\Z")
_PHASES = frozenset({
    "planned",
    "staged",
    "backed_up",
    "replacing",
    "verified",
    "committed",
    "recovery-required",
    "rolled-back",
})


@dataclass(frozen=True)
class InstallationRecord:
    operation_id: str
    action: str
    target: str
    source_commit: str | None
    source_digest: str | None
    phase: str
    completed_roots: tuple[str, ...]
    before_hashes: dict[str, str | None]
    after_hashes: dict[str, str | None]
    error: str | None = None


def operation_directory(journal_root: Path, operation_id: str) -> Path:
    if _ID.fullmatch(operation_id) is None or not journal_root.is_absolute():
        raise ValueError("invalid installation journal location")
    return journal_root / "installations" / operation_id


def read_record(journal_root: Path, operation_id: str) -> InstallationRecord:
    path = operation_directory(journal_root, operation_id) / "record.json"
    if path.is_symlink():
        raise ValueError("installation journal is a symlink")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("installation journal is missing or invalid") from error
    if not isinstance(payload, dict):
        raise ValueError("installation journal must be an object")
    try:
        record = InstallationRecord(**payload)
    except TypeError as error:
        raise ValueError("installation journal shape is invalid") from error
    if (
        record.operation_id != operation_id
        or record.action not in ("init", "update", "uninstall")
        or record.phase not in _PHASES
        or not isinstance(record.target, str)
        or not Path(record.target).is_absolute()
        or not isinstance(record.completed_roots, (list, tuple))
        or not all(isinstance(root, str) for root in record.completed_roots)
        or not isinstance(record.before_hashes, dict)
        or not isinstance(record.after_hashes, dict)
    ):
        raise ValueError("installation journal content is invalid")
    return InstallationRecord(
        operation_id,
        record.action,
        record.target,
        record.source_commit,
        record.source_digest,
        record.phase,
        tuple(record.completed_roots),
        record.before_hashes,
        record.after_hashes,
        record.error,
    )


def write_record(journal_root: Path, record: InstallationRecord, *, create: bool = False) -> None:
    directory = operation_directory(journal_root, record.operation_id)
    if create:
        directory.mkdir(mode=0o700, parents=True, exist_ok=False)
    elif not directory.is_dir() or directory.is_symlink():
        raise ValueError("installation journal directory is missing or unsafe")
    path = directory / "record.json"
    if path.is_symlink():
        raise ValueError("installation journal is a symlink")
    temporary = directory / f".record-{uuid.uuid4().hex}.tmp"
    payload = (json.dumps(asdict(record), sort_keys=True, separators=(",", ":")) + "\n").encode()
    fd = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
        directory_fd = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)
