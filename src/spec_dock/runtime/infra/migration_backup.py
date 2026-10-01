"""Real cutover backups, including an independent restore-and-compare check."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import tempfile
from typing import TYPE_CHECKING

from spec_dock.runtime.infra.json_store import open_guarded_directory
from spec_dock.runtime.infra.tree_backup import copy_tree_at, tree_digest, verify_backup_root

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True)
class BackupTree:
    source: Path
    relative: Path
    digest: str


@dataclass(frozen=True)
class VerifiedBackup:
    path: Path
    identity: tuple[int, int]
    sources: tuple[BackupTree, ...]

    def verify(self) -> None:
        descriptor = open_guarded_directory(self.path)
        try:
            visible = os.fstat(descriptor)
            if (visible.st_dev, visible.st_ino) != self.identity:
                raise ValueError("verified backup physical identity changed")
            for source in self.sources:
                if tree_digest(self.path / source.relative) != source.digest:
                    raise ValueError("verified backup content changed")
            verify_backup_root(self.path, descriptor)
        finally:
            os.close(descriptor)


class MigrationBackupIncomplete(RuntimeError):
    def __init__(self, *, backup_verified: bool, restore_verified: bool) -> None:
        self.backup_verified = backup_verified
        self.restore_verified = restore_verified
        super().__init__("migration backup did not complete; retain it for inspection")


def create_verified_backup(
    backup: Path, sources: tuple[BackupTree, ...], *, verify: Callable[[], None]
) -> VerifiedBackup:
    """Create a new external directory; never overwrite or restore into live data."""
    parent = open_guarded_directory(backup.parent)
    descriptor: int | None = None
    claimed = False
    backup_verified = False
    restore_verified = False
    try:
        verify()
        try:
            os.mkdir(backup.name, mode=0o700, dir_fd=parent)
        except FileExistsError as error:
            raise ValueError("backup destination appeared before creation") from error
        claimed = True
        descriptor = os.open(backup.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
        verify_backup_root(backup, descriptor)
        for source in sources:
            copy_tree_at(descriptor, source.relative, source.source)
            verify_backup_root(backup, descriptor)
            if tree_digest(backup / source.relative) != source.digest:
                raise ValueError("backup content differs from the captured source")
        os.fsync(descriptor)
        os.fsync(parent)
        with tempfile.TemporaryDirectory(prefix=".specdock-restore-", dir=backup.parent) as temporary:
            restored = Path(temporary)
            restored_fd = open_guarded_directory(restored)
            try:
                for source in sources:
                    verify_backup_root(backup, descriptor)
                    copy_tree_at(restored_fd, source.relative, backup / source.relative)
                    if tree_digest(restored / source.relative) != source.digest:
                        raise ValueError("restored content differs from the captured source")
                    if tree_digest(backup / source.relative) != source.digest:
                        raise ValueError("backup changed during restoration verification")
                restore_verified = True
                backup_verified = True
            finally:
                os.close(restored_fd)
        verify_backup_root(backup, descriptor)
        verify()
        current = os.fstat(descriptor)
        return VerifiedBackup(backup, (current.st_dev, current.st_ino), sources)
    except (OSError, ValueError, RuntimeError) as error:
        if claimed:
            raise MigrationBackupIncomplete(
                backup_verified=backup_verified, restore_verified=restore_verified
            ) from error
        raise
    finally:
        cleanup_error: OSError | None = None
        for opened in (descriptor, parent):
            if opened is not None:
                try:
                    os.close(opened)
                except OSError as error:
                    cleanup_error = error
        if cleanup_error is not None:
            if claimed:
                raise MigrationBackupIncomplete(
                    backup_verified=backup_verified, restore_verified=restore_verified
                ) from cleanup_error
            raise cleanup_error
