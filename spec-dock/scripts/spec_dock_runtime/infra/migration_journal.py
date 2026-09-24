"""Durable, fixed-byte migration journal in the Git common directory."""

from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
from uuid import uuid4

_ID = re.compile(r"[0-9a-f]{32}\Z")
_DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")
_ENGINE = re.compile(r"[0-9a-f]{64}\Z")
_PHASES = {"prepared", "applying", "recovery-required", "committed", "rolled-back"}
_MAX_FILE = 50 * 1024 * 1024


@dataclass(frozen=True)
class MigrationFile:
    path: str
    before_bytes: bytes | None
    after_bytes: bytes
    before_digest: str | None
    after_digest: str


@dataclass(frozen=True)
class MigrationRecord:
    operation_id: str
    common_dir: str
    repository_uid: str
    source_inventory_digest: str
    engine_digest: str
    control_epoch: int
    worktrees: tuple[tuple[str, str], ...]
    files: tuple[MigrationFile, ...]
    completed_paths: tuple[str, ...]
    phase: str
    error: str | None = None


def _digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _directory(common_dir: Path, operation_id: str) -> Path:
    if not common_dir.is_absolute() or _ID.fullmatch(operation_id) is None:
        raise ValueError("invalid migration journal location")
    directory = common_dir / "spec-dock" / "control" / "migrations" / operation_id
    if any(path.is_symlink() for path in (directory, *directory.parents)):
        raise ValueError("migration journal location is redirected")
    return directory


def _managed_file(path: Path, roots: set[str]) -> bool:
    if not path.is_absolute() or ".." in path.parts:
        return False
    for root in roots:
        if not path.is_relative_to(root):
            continue
        relative = path.relative_to(root)
        if relative in (Path("spec-dock/workspace.json"), Path("spec-dock/.agent/active.json")):
            return True
        if relative.parts[:2] == ("spec-dock", "initiatives") and relative.name == ".meta.json":
            return True
    return False


def _validate(record: MigrationRecord) -> None:
    if (
        not isinstance(record.operation_id, str)
        or _ID.fullmatch(record.operation_id) is None
        or not isinstance(record.common_dir, str)
        or not Path(record.common_dir).is_absolute()
        or not isinstance(record.repository_uid, str)
        or _DIGEST.fullmatch(record.repository_uid) is None
        or not isinstance(record.source_inventory_digest, str)
        or _DIGEST.fullmatch(record.source_inventory_digest) is None
        or not isinstance(record.engine_digest, str)
        or _ENGINE.fullmatch(record.engine_digest) is None
        or type(record.control_epoch) is not int
        or record.control_epoch < 0
        or record.phase not in _PHASES
        or not isinstance(record.worktrees, tuple)
        or not record.worktrees
        or not isinstance(record.files, tuple)
        or not isinstance(record.completed_paths, tuple)
        or (record.error is not None and not isinstance(record.error, str))
    ):
        raise ValueError("invalid migration journal record")
    worktree_ids: set[str] = set()
    roots: set[str] = set()
    for worktree_id, root in record.worktrees:
        if (
            not isinstance(worktree_id, str)
            or re.fullmatch(r"[a-z0-9][a-z0-9._-]*", worktree_id) is None
            or not isinstance(root, str)
            or not Path(root).is_absolute()
            or ".." in Path(root).parts
            or worktree_id in worktree_ids
            or root in roots
        ):
            raise ValueError("invalid migration worktree identity")
        worktree_ids.add(worktree_id)
        roots.add(root)
    paths: set[str] = set()
    for item in record.files:
        if (
            not isinstance(item, MigrationFile)
            or not isinstance(item.path, str)
            or not _managed_file(Path(item.path), roots)
            or item.path in paths
            or not isinstance(item.after_bytes, bytes)
            or len(item.after_bytes) > _MAX_FILE
            or not isinstance(item.after_digest, str)
            or _digest(item.after_bytes) != item.after_digest
            or (item.before_bytes is None) != (item.before_digest is None)
            or (
                item.before_bytes is not None
                and (
                    not isinstance(item.before_bytes, bytes)
                    or len(item.before_bytes) > _MAX_FILE
                    or _digest(item.before_bytes) != item.before_digest
                )
            )
        ):
            raise ValueError("invalid migration file snapshot")
        paths.add(item.path)
    if len(set(record.completed_paths)) != len(record.completed_paths) or set(record.completed_paths) - paths:
        raise ValueError("migration completion record has an unknown path")
    if record.phase == "committed" and set(record.completed_paths) != paths:
        raise ValueError("committed migration has incomplete files")


def _encode(record: MigrationRecord) -> bytes:
    payload = {
        "operation_id": record.operation_id,
        "common_dir": record.common_dir,
        "repository_uid": record.repository_uid,
        "source_inventory_digest": record.source_inventory_digest,
        "engine_digest": record.engine_digest,
        "control_epoch": record.control_epoch,
        "worktrees": record.worktrees,
        "files": [
            {
                "path": item.path,
                "before_bytes": None if item.before_bytes is None else base64.b64encode(item.before_bytes).decode(),
                "after_bytes": base64.b64encode(item.after_bytes).decode(),
                "before_digest": item.before_digest,
                "after_digest": item.after_digest,
            }
            for item in record.files
        ],
        "completed_paths": record.completed_paths,
        "phase": record.phase,
        "error": record.error,
    }
    return (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _decode(payload: object) -> MigrationRecord:
    if not isinstance(payload, dict) or not isinstance(payload.get("files"), list):
        raise ValueError("migration journal shape is invalid")
    try:
        files = tuple(
            MigrationFile(
                item["path"],
                None if item["before_bytes"] is None else base64.b64decode(item["before_bytes"], validate=True),
                base64.b64decode(item["after_bytes"], validate=True),
                item["before_digest"],
                item["after_digest"],
            )
            for item in payload["files"]
        )
        record = MigrationRecord(
            payload["operation_id"],
            payload["common_dir"],
            payload["repository_uid"],
            payload["source_inventory_digest"],
            payload["engine_digest"],
            payload["control_epoch"],
            tuple(tuple(item) for item in payload["worktrees"]),
            files,
            tuple(payload["completed_paths"]),
            payload["phase"],
            payload.get("error"),
        )
    except (TypeError, KeyError, ValueError, binascii.Error) as error:
        raise ValueError("migration journal shape is invalid") from error
    _validate(record)
    return record


def read_migration_record(common_dir: Path, operation_id: str) -> MigrationRecord:
    path = _directory(common_dir, operation_id) / "record.json"
    if path.is_symlink():
        raise ValueError("migration journal is redirected")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("migration journal is missing or invalid") from error
    record = _decode(payload)
    if record.operation_id != operation_id or record.common_dir != str(common_dir):
        raise ValueError("migration journal identity differs")
    return record


def write_migration_record(common_dir: Path, record: MigrationRecord, *, create: bool = False) -> None:
    _validate(record)
    if record.common_dir != str(common_dir):
        raise ValueError("migration common directory differs")
    directory = _directory(common_dir, record.operation_id)
    if create:
        root = directory.parent
        root.mkdir(mode=0o700, parents=True, exist_ok=True)
        if root.is_symlink() or os.path.lexists(directory):
            raise ValueError("migration journal already exists or is redirected")
        staging_root = root.parent / ".migration-staging"
        staging_root.mkdir(mode=0o700, exist_ok=True)
        if staging_root.is_symlink():
            raise ValueError("migration staging directory is redirected")
        staged_directory = staging_root / uuid4().hex
        staged_directory.mkdir(mode=0o700, exist_ok=False)
        _write_record_file(staged_directory, record)
        staged_directory.replace(directory)
        root_fd = os.open(root, os.O_RDONLY)
        try:
            os.fsync(root_fd)
        finally:
            os.close(root_fd)
        return
    elif not directory.is_dir():
        raise ValueError("migration journal directory is missing")
    _write_record_file(directory, record)


def _write_record_file(directory: Path, record: MigrationRecord) -> None:
    path = directory / "record.json"
    if path.is_symlink():
        raise ValueError("migration journal is redirected")
    staged = directory / f".record-{uuid4().hex}.tmp"
    descriptor = os.open(staged, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(_encode(record))
            stream.flush()
            os.fsync(stream.fileno())
        staged.replace(path)
        directory_fd = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        staged.unlink(missing_ok=True)


def pending_migrations(common_dir: Path) -> tuple[str, ...]:
    root = common_dir / "spec-dock" / "control" / "migrations"
    if not root.exists():
        return ()
    if root.is_symlink() or not root.is_dir():
        raise ValueError("migration journal directory is invalid")
    pending: list[str] = []
    for directory in sorted(root.iterdir()):
        if directory.is_symlink() or not directory.is_dir() or _ID.fullmatch(directory.name) is None:
            raise ValueError("migration journal entry is invalid")
        record = read_migration_record(common_dir, directory.name)
        if record.phase not in {"committed", "rolled-back"}:
            pending.append(record.operation_id)
    return tuple(pending)
