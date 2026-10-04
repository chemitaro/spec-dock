"""Remove one observed local tree through held directory descriptors."""

from __future__ import annotations

import os
import stat
from typing import TYPE_CHECKING

from spec_dock.runtime.infra.json_store import open_guarded_directory

if TYPE_CHECKING:
    from pathlib import Path


class TreeRemovalIncomplete(RuntimeError):
    def __init__(
        self,
        cause: ValueError | OSError | RuntimeError,
        *,
        applied: tuple[str, ...],
        remaining: tuple[str, ...],
        failed_path: str | None,
        attempted: bool,
    ) -> None:
        self.cause = cause
        self.applied = applied
        self.remaining = remaining
        self.failed_path = failed_path
        self.attempted = attempted
        super().__init__(str(cause))


def remove_tree(root: Path, *, expected_entries: dict[str, os.stat_result]) -> None:
    planned = tuple(sorted(expected_entries, key=lambda name: (-(0 if name == "." else name.count("/") + 1), name)))
    applied: list[str] = []
    current: str | None = None
    attempted = False
    parent_fd: int | None = None
    root_fd: int | None = None
    failure: ValueError | OSError | RuntimeError | None = None

    def walk(path: Path, descriptor: int) -> None:
        nonlocal current, attempted
        for name in sorted(os.listdir(descriptor)):
            current = (path / name).relative_to(root).as_posix()
            attempted = False
            if current not in planned:
                raise ValueError("delete tree contains an entry outside the verified backup plan")
            _verify_bound(path, descriptor)
            observed = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
            expected = expected_entries[current]
            if (observed.st_dev, observed.st_ino, observed.st_mode) != (
                expected.st_dev,
                expected.st_ino,
                expected.st_mode,
            ):
                raise ValueError("delete tree entry identity or mode changed")
            if not stat.S_ISDIR(observed.st_mode) and (
                observed.st_size,
                observed.st_mtime_ns,
                observed.st_ctime_ns,
            ) != (expected.st_size, expected.st_mtime_ns, expected.st_ctime_ns):
                raise ValueError("delete tree entry content changed")
            if stat.S_ISDIR(observed.st_mode):
                child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
                try:
                    if (os.fstat(child).st_dev, os.fstat(child).st_ino) != (observed.st_dev, observed.st_ino):
                        raise ValueError("delete directory identity changed")
                    walk(path / name, child)
                    _verify_bound(path / name, child)
                finally:
                    os.close(child)
                current = (path / name).relative_to(root).as_posix()
                attempted = True
                os.rmdir(name, dir_fd=descriptor)
            elif stat.S_ISREG(observed.st_mode) or stat.S_ISLNK(observed.st_mode):
                attempted = True
                os.unlink(name, dir_fd=descriptor)
            else:
                raise ValueError("delete tree contains an unsupported entry")
            applied.append(current)
            os.fsync(descriptor)

    try:
        current = "."
        parent_fd = open_guarded_directory(root.parent)
        root_fd = open_guarded_directory(root)
        walk(root, root_fd)
        current = "."
        attempted = False
        _verify_bound(root.parent, parent_fd)
        _verify_bound(root, root_fd)
        attempted = True
        os.rmdir(root.name, dir_fd=parent_fd)
        applied.append(".")
        os.fsync(parent_fd)
    except (ValueError, OSError, RuntimeError) as error:
        failure = error
    finally:
        for opened in (root_fd, parent_fd):
            if opened is not None:
                try:
                    os.close(opened)
                except OSError as error:
                    if failure is None:
                        failure = error
    if failure is not None:
        remaining = tuple(path for path in planned if path not in applied)
        if current is not None and current not in planned and current not in applied:
            remaining = (current, *remaining)
        raise TreeRemovalIncomplete(
            failure,
            applied=tuple(applied),
            remaining=remaining,
            failed_path=current if current not in applied else None,
            attempted=attempted,
        ) from failure


def _verify_bound(path: Path, descriptor: int) -> None:
    fresh = open_guarded_directory(path)
    try:
        current, held = os.fstat(fresh), os.fstat(descriptor)
        if (current.st_dev, current.st_ino) != (held.st_dev, held.st_ino):
            raise ValueError("delete directory path changed")
    finally:
        os.close(fresh)
