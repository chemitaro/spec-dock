"""Guarded regular-file snapshots and one-file publication without a journal."""

from __future__ import annotations

from dataclasses import dataclass
import errno
import os
import stat
from typing import TYPE_CHECKING

from spec_dock.runtime.infra.json_store import open_guarded_directory

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from spec_dock.runtime.infra.workbench_snapshot import WorkbenchEntry


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


class FileRetirementIncomplete(RuntimeError):
    def __init__(self, message: str, *, confirmed: bool = False) -> None:
        self.confirmed = confirmed
        super().__init__(message)


def retire_file(path: Path, *, expected: FileSnapshot, verify: Callable[[], object]) -> None:
    """Unlink one captured regular file, without recursive deletion or rollback."""
    parent = open_guarded_directory(path.parent)
    attempted = confirmed = False
    try:
        verify()
        if read_regular_file(path) != expected:
            raise ValueError("static retirement input changed")
        _verify_file_parent(path, parent)
        attempted = True
        os.unlink(path.name, dir_fd=parent)
        os.fsync(parent)
        _verify_file_parent(path, parent)
        if os.path.lexists(path):
            raise ValueError("retired static path is occupied again")
        confirmed = True
    except (OSError, ValueError, RuntimeError) as error:
        if attempted:
            raise FileRetirementIncomplete(str(error), confirmed=confirmed) from error
        raise
    finally:
        try:
            os.close(parent)
        except OSError as error:
            if attempted:
                raise FileRetirementIncomplete(str(error), confirmed=confirmed) from error
            raise


def _verify_file_parent(path: Path, held: int) -> None:
    fresh = open_guarded_directory(path.parent)
    try:
        current, previous = os.fstat(fresh), os.fstat(held)
        if (current.st_dev, current.st_ino) != (previous.st_dev, previous.st_ino):
            raise ValueError("static file parent physical identity changed")
    finally:
        os.close(fresh)


def verify_existing_parent(path: Path) -> None:
    """Inspect the nearest existing ancestor without creating or following links."""
    parent = path.parent
    while not os.path.lexists(parent):
        parent = parent.parent
    if any(item.is_symlink() for item in (parent, *parent.parents)):
        raise ValueError("file publication parent must not be a symbolic link")
    try:
        descriptor = open_guarded_directory(parent)
    except OSError as error:
        if error.errno in (errno.ELOOP, errno.ENOTDIR):
            raise ValueError("file publication parent must be a regular directory") from error
        raise
    os.close(descriptor)


def create_missing_parents(root: Path, path: Path, *, on_created: Callable[[Path], None]) -> None:
    """Create contained directories, reporting each before subsequent IO can fail."""
    directory = root
    for part in path.parent.relative_to(root).parts:
        parent = open_guarded_directory(directory)
        directory /= part
        try:
            try:
                os.mkdir(part, mode=0o755, dir_fd=parent)
            except FileExistsError:
                pass
            else:
                on_created(directory)
                os.fsync(parent)
            opened = open_guarded_directory(directory)
            os.close(opened)
        finally:
            os.close(parent)


def publish_file(
    path: Path,
    payload: bytes,
    *,
    stage_name: str,
    verify: Callable[[], object],
    mode: int = 0o666,
    expected: FileSnapshot | WorkbenchEntry | None = None,
    preserve_mode: bool = False,
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

    def verify_expected() -> None:
        if expected is None:
            return
        if isinstance(expected, FileSnapshot):
            observed: FileSnapshot | WorkbenchEntry = read_regular_file(path)
        else:
            from spec_dock.runtime.infra.workbench_snapshot import read_entry

            if expected.kind != "symlink":
                raise ValueError("replacement expected entry must be a regular file or a symbolic link")
            observed = read_entry(path)
        if observed != expected:
            raise ValueError("destination changed before replacement")

    try:
        verify()
        verify_expected()
        if expected is None and os.path.lexists(path):
            raise ValueError("destination already exists")
        try:
            descriptor = os.open(stage_name, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode, dir_fd=parent)
        except FileExistsError as error:
            raise ValueError("publication candidate is already claimed; inspect before a new operation") from error
        with os.fdopen(os.dup(descriptor), "wb") as stream:
            stream.write(payload)
            stream.flush()
            if preserve_mode:
                os.fchmod(descriptor, mode)
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
        if (
            candidate.identity != (staged.st_dev, staged.st_ino)
            or candidate.payload != payload
            or (preserve_mode and candidate.mode != mode)
        ):
            raise ValueError("publication stage identity or bytes changed")
        verify_expected()
        attempted = True
        if expected is not None:
            os.replace(stage_name, path.name, src_dir_fd=parent, dst_dir_fd=parent)
        else:
            try:
                os.link(stage_name, path.name, src_dir_fd=parent, dst_dir_fd=parent, follow_symlinks=False)
            except FileExistsError as error:
                attempted = False
                raise ValueError("destination publication conflict") from error
            os.unlink(stage_name, dir_fd=parent)
        os.fsync(parent)
        observed = read_regular_file(path)
        staged = os.fstat(descriptor)
        if (
            observed.payload != payload
            or observed.identity != (staged.st_dev, staged.st_ino)
            or (preserve_mode and observed.mode != mode)
        ):
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
