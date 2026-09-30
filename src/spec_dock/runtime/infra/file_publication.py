"""Guarded regular-file snapshots and one-file publication without a journal."""

from __future__ import annotations

from dataclasses import dataclass
import os
import stat
from typing import TYPE_CHECKING

from spec_dock.runtime.infra.json_store import open_guarded_directory

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


@dataclass(frozen=True)
class FileSnapshot:
    payload: bytes
    identity: tuple[int, int]
    mode: int
    size: int
    mtime_ns: int
    ctime_ns: int


def read_regular_file(path: Path) -> FileSnapshot:
    parent = open_guarded_directory(path.parent)
    descriptor: int | None = None
    try:
        descriptor = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise ValueError("file must be a single-link regular file")
        with os.fdopen(os.dup(descriptor), "rb") as stream:
            payload = stream.read()
        after = os.fstat(descriptor)
        visible = os.stat(path.name, dir_fd=parent, follow_symlinks=False)

        def key(item: os.stat_result) -> tuple[int, int, int, int, int, int]:
            return item.st_dev, item.st_ino, item.st_mode, item.st_size, item.st_mtime_ns, item.st_ctime_ns

        if key(before) != key(after) or key(after) != key(visible):
            raise ValueError("file changed while reading")
        fresh = open_guarded_directory(path.parent)
        try:
            if (os.fstat(fresh).st_dev, os.fstat(fresh).st_ino) != (os.fstat(parent).st_dev, os.fstat(parent).st_ino):
                raise ValueError("file parent identity changed")
        finally:
            os.close(fresh)
        return FileSnapshot(
            payload,
            (after.st_dev, after.st_ino),
            stat.S_IMODE(after.st_mode),
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        )
    finally:
        try:
            if descriptor is not None:
                os.close(descriptor)
        finally:
            os.close(parent)


class FilePublicationIncomplete(RuntimeError):
    def __init__(self, message: str, *, confirmed: bool = False) -> None:
        self.confirmed = confirmed
        super().__init__(message)


def publish_file(
    path: Path,
    payload: bytes,
    *,
    stage_name: str,
    verify: Callable[[], object],
    mode: int = 0o666,
) -> None:
    """Publish from a held same-directory stage, preserving an uncertain outcome.

    The stage contains the actual candidate bytes. A deterministic candidate name
    can reject concurrent publication of the same Artifact slot without a counter
    or a shared writer lock. An existing stage is never reused or automatically recovered.
    """
    if stage_name in ("", ".", "..") or "/" in stage_name or "\\" in stage_name:
        raise ValueError("stage name must be a single component")
    parent = open_guarded_directory(path.parent)
    descriptor: int | None = None
    attempted = confirmed = False
    try:
        verify()
        if os.path.lexists(path):
            raise ValueError("destination already exists")
        try:
            descriptor = os.open(stage_name, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode, dir_fd=parent)
        except FileExistsError as error:
            raise ValueError("publication candidate is already claimed; inspect before a new operation") from error
        with os.fdopen(os.dup(descriptor), "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        verify()
        fresh = open_guarded_directory(path.parent)
        try:
            if (os.fstat(fresh).st_dev, os.fstat(fresh).st_ino) != (os.fstat(parent).st_dev, os.fstat(parent).st_ino):
                raise ValueError("publication parent identity changed")
        finally:
            os.close(fresh)
        candidate = read_regular_file(path.parent / stage_name)
        staged = os.fstat(descriptor)
        if candidate.identity != (staged.st_dev, staged.st_ino) or candidate.payload != payload:
            raise ValueError("publication stage identity or bytes changed")
        attempted = True
        try:
            os.link(stage_name, path.name, src_dir_fd=parent, dst_dir_fd=parent, follow_symlinks=False)
        except FileExistsError as error:
            attempted = False
            raise ValueError("destination publication conflict") from error
        os.unlink(stage_name, dir_fd=parent)
        os.fsync(parent)
        observed = read_regular_file(path)
        staged = os.fstat(descriptor)
        if observed.payload != payload or observed.identity != (staged.st_dev, staged.st_ino):
            raise ValueError("published file readback changed")
        confirmed = True
    except (OSError, ValueError, RuntimeError) as error:
        if attempted:
            raise FilePublicationIncomplete(str(error), confirmed=confirmed) from error
        raise
    finally:
        cleanup_error: OSError | None = None
        if descriptor is not None and not attempted:
            try:
                stage_visible = os.stat(stage_name, dir_fd=parent, follow_symlinks=False)
                staged = os.fstat(descriptor)
                if (stage_visible.st_dev, stage_visible.st_ino) == (staged.st_dev, staged.st_ino):
                    os.unlink(stage_name, dir_fd=parent)
            except FileNotFoundError:
                pass
            except OSError as error:
                cleanup_error = error
        for opened in (descriptor, parent):
            if opened is not None:
                try:
                    os.close(opened)
                except OSError as error:
                    cleanup_error = error
        if cleanup_error is not None:
            if attempted:
                raise FilePublicationIncomplete(str(cleanup_error), confirmed=confirmed) from cleanup_error
            raise cleanup_error
