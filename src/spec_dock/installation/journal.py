"""Durable installation operation records outside replaced tooling directories."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import re
import uuid

_ID = re.compile(r"[0-9a-f]{32}\Z")
_SHA = re.compile(r"[0-9a-f]{40}\Z")
_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
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
    marker_tracked: bool = False
    marker_before: dict[str, int] | None = None
    marker_publish: dict[str, int] | None = None
    before_identities: dict[str, str | None] | None = None
    requested_version: str | None = None
    after_identities: dict[str, str | None] | None = None
    identity_schema: int | None = None


def durable_mkdir(directory: Path) -> None:
    """Publish every newly created directory entry before a journaled effect."""
    absent: list[Path] = []
    current = directory
    while not current.exists():
        absent.append(current)
        current = current.parent
    directory.mkdir(mode=0o700, parents=True, exist_ok=False)
    for created in absent:
        for path in (created, created.parent):
            descriptor = os.open(path, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)


def operation_directory(journal_root: Path, operation_id: str) -> Path:
    if _ID.fullmatch(operation_id) is None or not journal_root.is_absolute():
        raise ValueError("invalid installation journal location")
    directory = journal_root / "installations" / operation_id
    if any(path.is_symlink() for path in (directory, *directory.parents)):
        raise ValueError("installation journal location contains a symlink")
    return directory


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
        or (
            record.source_commit is not None
            and (not isinstance(record.source_commit, str) or _SHA.fullmatch(record.source_commit) is None)
        )
        or (
            record.source_digest is not None
            and (not isinstance(record.source_digest, str) or _DIGEST.fullmatch(record.source_digest) is None)
        )
        or (record.error is not None and not isinstance(record.error, str))
        or (record.requested_version is not None and not isinstance(record.requested_version, str))
        or record.identity_schema not in (None, 2)
        or not isinstance(record.marker_tracked, bool)
        or any(
            identity is not None
            and (
                not isinstance(identity, dict)
                or set(identity) != {"device", "inode"}
                or any(
                    not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in identity.values()
                )
            )
            for identity in (record.marker_before, record.marker_publish)
        )
        or (
            record.before_identities is not None
            and (
                not isinstance(record.before_identities, dict)
                or any(
                    not isinstance(key, str)
                    or (identity is not None and (not isinstance(identity, str) or _DIGEST.fullmatch(identity) is None))
                    for key, identity in record.before_identities.items()
                )
            )
        )
        or (
            record.after_identities is not None
            and (
                not isinstance(record.after_identities, dict)
                or any(
                    not isinstance(key, str)
                    or (identity is not None and (not isinstance(identity, str) or _DIGEST.fullmatch(identity) is None))
                    for key, identity in record.after_identities.items()
                )
            )
        )
    ):
        raise ValueError("installation journal content is invalid")
    for hashes in (record.before_hashes, record.after_hashes):
        if any(
            not isinstance(key, str)
            or (value is not None and (not isinstance(value, str) or _DIGEST.fullmatch(value) is None))
            for key, value in hashes.items()
        ):
            raise ValueError("installation journal hash inventory is invalid")
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
        record.marker_tracked,
        record.marker_before,
        record.marker_publish,
        record.before_identities,
        record.requested_version,
        record.after_identities,
        record.identity_schema,
    )


def write_record(journal_root: Path, record: InstallationRecord, *, create: bool = False) -> None:
    directory = operation_directory(journal_root, record.operation_id)
    if create:
        durable_mkdir(directory)
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
