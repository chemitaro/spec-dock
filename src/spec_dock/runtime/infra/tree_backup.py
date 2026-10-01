"""Capture and verify real local tree contents without following symbolic links."""

from __future__ import annotations

import hashlib
import os
import stat
from typing import TYPE_CHECKING

from spec_dock.runtime.infra.json_store import open_guarded_directory

if TYPE_CHECKING:
    from pathlib import Path


def copy_tree_at(backup_fd: int, relative: Path, source: Path) -> None:
    parent = _backup_parent(backup_fd, relative)
    source_fd: int | None = None
    destination_fd: int | None = None
    try:
        source_fd = open_guarded_directory(source)
        os.mkdir(relative.name, mode=0o700, dir_fd=parent)
        destination_fd = os.open(relative.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
        _copy_directory(source_fd, destination_fd)
        os.fsync(parent)
    finally:
        for opened in (destination_fd, source_fd, parent):
            if opened is not None:
                os.close(opened)


def copy_bytes_at(backup_fd: int, relative: Path, payload: bytes, mode: int) -> None:
    parent = _backup_parent(backup_fd, relative)
    descriptor: int | None = None
    try:
        descriptor = os.open(relative.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode, dir_fd=parent)
        _write_all(descriptor, payload)
        os.fchmod(descriptor, mode)
        os.fsync(descriptor)
        os.fsync(parent)
    finally:
        for opened in (descriptor, parent):
            if opened is not None:
                os.close(opened)


def verify_backup_root(path: Path, held: int) -> None:
    fresh = open_guarded_directory(path)
    try:
        left, right = os.fstat(fresh), os.fstat(held)
        if (left.st_dev, left.st_ino) != (right.st_dev, right.st_ino):
            raise ValueError("backup root physical identity changed")
    finally:
        os.close(fresh)


def _backup_parent(root_fd: int, relative: Path) -> int:
    if relative.is_absolute() or not relative.parts or any(part in (".", "..") for part in relative.parts):
        raise ValueError("backup entry must be a contained relative path")
    parent = os.dup(root_fd)
    try:
        for name in relative.parts[:-1]:
            try:
                os.mkdir(name, mode=0o700, dir_fd=parent)
            except FileExistsError:
                pass
            else:
                os.fsync(parent)
            child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            os.close(parent)
            parent = child
        return parent
    except BaseException:
        os.close(parent)
        raise


def _copy_directory(source_fd: int, destination_fd: int) -> None:
    for name in sorted(os.listdir(source_fd)):
        observed = os.stat(name, dir_fd=source_fd, follow_symlinks=False)
        if stat.S_ISLNK(observed.st_mode):
            os.symlink(os.readlink(name, dir_fd=source_fd), name, dir_fd=destination_fd)
            continue
        if not stat.S_ISREG(observed.st_mode) and not stat.S_ISDIR(observed.st_mode):
            raise ValueError("backup source contains an unsupported entry")
        child = os.open(
            name,
            os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | (os.O_DIRECTORY if stat.S_ISDIR(observed.st_mode) else 0),
            dir_fd=source_fd,
        )
        copied: int | None = None
        try:
            opened = os.fstat(child)
            if (opened.st_dev, opened.st_ino, opened.st_mode) != (observed.st_dev, observed.st_ino, observed.st_mode):
                raise ValueError("backup source entry changed")
            if stat.S_ISDIR(observed.st_mode):
                os.mkdir(name, mode=0o700, dir_fd=destination_fd)
                copied = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=destination_fd)
                _copy_directory(child, copied)
            else:
                copied = os.open(
                    name,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                    stat.S_IMODE(observed.st_mode),
                    dir_fd=destination_fd,
                )
                while payload := os.read(child, 1024 * 1024):
                    _write_all(copied, payload)
                after = os.fstat(child)
                if (opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns) != (
                    after.st_size,
                    after.st_mtime_ns,
                    after.st_ctime_ns,
                ):
                    raise ValueError("backup source file changed")
                os.fchmod(copied, stat.S_IMODE(opened.st_mode))
                os.fsync(copied)
        finally:
            for descriptor in (copied, child):
                if descriptor is not None:
                    os.close(descriptor)
    os.fchmod(destination_fd, stat.S_IMODE(os.fstat(source_fd).st_mode))
    os.fsync(destination_fd)


def _write_all(descriptor: int, payload: bytes) -> None:
    remaining = memoryview(payload)
    while remaining:
        written = os.write(descriptor, remaining)
        if written <= 0:
            raise OSError("backup write made no progress")
        remaining = remaining[written:]


def tree_digest(root: Path, *, excluded_entries: frozenset[str] = frozenset()) -> str:
    if any(path.is_symlink() for path in (root, *root.parents)) or not root.is_dir():
        raise ValueError("tree root must be a real directory without redirected parents")
    digest = hashlib.sha256()
    for path in (root, *sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix())):
        observed = path.lstat()
        relative = "." if path == root else path.relative_to(root).as_posix()
        if relative in excluded_entries:
            continue
        digest.update(relative.encode("utf-8", "surrogateescape"))
        digest.update(b"\0")
        digest.update(str(stat.S_IMODE(observed.st_mode)).encode("ascii"))
        if stat.S_ISDIR(observed.st_mode):
            digest.update(b"D")
        elif stat.S_ISLNK(observed.st_mode):
            digest.update(b"L")
            digest.update(os.fsencode(path.readlink()))
        elif stat.S_ISREG(observed.st_mode):
            digest.update(b"F")
            descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            with os.fdopen(descriptor, "rb") as stream:
                opened = os.fstat(stream.fileno())
                if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino, opened.st_size) != (
                    observed.st_dev,
                    observed.st_ino,
                    observed.st_size,
                ):
                    raise ValueError("tree entry changed while reading")
                while chunk := stream.read(1024 * 1024):
                    digest.update(chunk)
                after = os.fstat(stream.fileno())
                if (after.st_size, after.st_mtime_ns, after.st_ctime_ns) != (
                    opened.st_size,
                    opened.st_mtime_ns,
                    opened.st_ctime_ns,
                ):
                    raise ValueError("tree file changed while reading")
        else:
            raise ValueError("tree contains an unsupported entry")
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()
