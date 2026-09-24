"""Atomic writes for the fixed files in one schema migration record."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import stat
from typing import TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from spec_dock_runtime.infra.migration_journal import MigrationFile, MigrationRecord


def _digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _guard_path(record: MigrationRecord, path: Path) -> None:
    roots = [Path(root) for _id, root in record.worktrees if path.is_relative_to(root)]
    if len(roots) != 1 or ".." in path.parts:
        raise ValueError("migration path is outside its fixed worktree")
    root = roots[0]
    if root.is_symlink() or not root.is_dir():
        raise ValueError("migration worktree root is unavailable")
    candidate = root
    for part in path.relative_to(root).parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise ValueError("migration path is redirected")
    if not path.parent.is_dir():
        raise ValueError("migration file parent is unavailable")


def snapshot_migration_file(record: MigrationRecord, item: MigrationFile) -> tuple[bytes | None, str | None]:
    path = Path(item.path)
    _guard_path(record, path)
    if not path.exists():
        return None, None
    if not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
        raise ValueError("migration target is not a regular file")
    data = path.read_bytes()
    return data, _digest(data)


def _publish(path: Path, data: bytes, *, mode: int) -> None:
    staged = path.parent / f".migration-{uuid4().hex}.tmp"
    descriptor = os.open(staged, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), mode)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fchmod(stream.fileno(), mode)
            os.fsync(stream.fileno())
        staged.replace(path)
        parent_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(parent_fd)
        finally:
            os.close(parent_fd)
    finally:
        staged.unlink(missing_ok=True)


def apply_migration_file(record: MigrationRecord, item: MigrationFile) -> None:
    path = Path(item.path)
    before, current_digest = snapshot_migration_file(record, item)
    if current_digest == item.after_digest:
        return
    if current_digest != item.before_digest:
        raise ValueError("migration target changed after preparation")
    mode = stat.S_IMODE(path.stat().st_mode) if before is not None else 0o644
    _publish(path, item.after_bytes, mode=mode)
    _after, verified_digest = snapshot_migration_file(record, item)
    if verified_digest != item.after_digest:
        raise ValueError("migration target did not reach planned content")


def preflight_rollback_file(record: MigrationRecord, item: MigrationFile) -> None:
    _current, digest = snapshot_migration_file(record, item)
    if digest not in (item.before_digest, item.after_digest):
        raise ValueError("migration rollback refuses later changes")


def rollback_migration_file(record: MigrationRecord, item: MigrationFile) -> None:
    path = Path(item.path)
    _current, digest = snapshot_migration_file(record, item)
    if digest == item.before_digest:
        return
    if digest != item.after_digest:
        raise ValueError("migration rollback refuses later changes")
    if item.before_bytes is None:
        path.unlink()
        parent_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(parent_fd)
        finally:
            os.close(parent_fd)
    else:
        _publish(path, item.before_bytes, mode=stat.S_IMODE(path.stat().st_mode))
