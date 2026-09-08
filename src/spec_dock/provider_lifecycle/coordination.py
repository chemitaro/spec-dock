"""Repository-root coordination lease primitive."""

from __future__ import annotations

import errno
import fcntl
import os
from pathlib import Path
import stat

from spec_dock.provider_lifecycle.contracts import RepositoryBinding


class RepositoryCoordinationError(RuntimeError):
    """The repository cannot be safely admitted for coordination."""


class RepositoryBusy(RepositoryCoordinationError):
    """Another process currently owns the requested repository lease."""


class RepositoryCoordinationUnavailable(RepositoryCoordinationError):
    """The host failed to provide the required coordination primitive."""


class RepositoryLease:
    """A root-fd-bound shared or exclusive non-blocking lease."""

    def __init__(self, fd: int, binding: RepositoryBinding, mode: str) -> None:
        if mode not in {"shared", "exclusive"}:
            raise ValueError("lease mode must be shared or exclusive")
        self.fd = fd
        self.binding = binding
        self.mode = mode
        self._closed = False

    @property
    def closed(self) -> bool:
        return self._closed

    def revalidate(self) -> RepositoryBinding:
        if self._closed:
            raise RepositoryCoordinationError("repository lease is closed")
        current = _binding_from_fd(self.fd)
        if current != self.binding:
            raise RepositoryCoordinationError("repository root binding changed")
        return current

    def close(self) -> None:
        if not self._closed:
            os.close(self.fd)
            self._closed = True

    def __enter__(self) -> RepositoryLease:
        self.revalidate()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def _euid() -> int:
    return os.geteuid() if hasattr(os, "geteuid") else os.getuid()


def _binding_from_fd(fd: int) -> RepositoryBinding:
    try:
        value = os.fstat(fd)
    except OSError as exc:
        raise RepositoryCoordinationUnavailable("repository lease descriptor is unavailable") from exc
    if not stat.S_ISDIR(value.st_mode):
        raise RepositoryCoordinationError("repository lease descriptor is not a directory")
    return RepositoryBinding(value.st_dev, value.st_ino, _euid())


def _directory_open_flags() -> int:
    return os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)


def _open_absolute_directory_no_follow(path: str | os.PathLike[str]) -> int:
    raw_path = os.fspath(path)
    if not Path(raw_path).is_absolute() or "\x00" in raw_path:
        raise RepositoryCoordinationError("repository root must be absolute and NUL-free")
    current_fd = os.open(os.sep, _directory_open_flags())
    try:
        for component in Path(raw_path).parts[1:]:
            if component in {"", ".", ".."}:
                raise RepositoryCoordinationError("repository root contains an unsafe component")
            next_fd = os.open(component, _directory_open_flags(), dir_fd=current_fd)
            os.close(current_fd)
            current_fd = next_fd
        return current_fd
    except BaseException:
        os.close(current_fd)
        raise


def _open_root(repository_root: str | os.PathLike[str]) -> tuple[int, RepositoryBinding, os.stat_result]:
    path = Path(repository_root)
    if not path.is_absolute() or "\x00" in os.fspath(path):
        raise RepositoryCoordinationError("repository root must be absolute")
    try:
        fd = _open_absolute_directory_no_follow(path)
    except OSError as exc:
        raise RepositoryCoordinationUnavailable("repository root cannot be opened") from exc
    before = os.fstat(fd)
    if not stat.S_ISDIR(before.st_mode):
        os.close(fd)
        raise RepositoryCoordinationError("repository root is not a directory")
    binding = _binding_from_fd(fd)
    if binding.device != before.st_dev or binding.inode != before.st_ino:
        os.close(fd)
        raise RepositoryCoordinationError("repository root changed while opening")
    return fd, binding, before


def _acquire(repository_root: str | os.PathLike[str], mode: str) -> RepositoryLease:
    fd, binding, before = _open_root(repository_root)
    operation = fcntl.LOCK_SH if mode == "shared" else fcntl.LOCK_EX
    try:
        fcntl.flock(fd, operation | fcntl.LOCK_NB)
    except OSError as exc:
        os.close(fd)
        if exc.errno in {errno.EAGAIN, errno.EWOULDBLOCK}:
            raise RepositoryBusy("repository coordination is busy") from exc
        raise RepositoryCoordinationUnavailable("repository coordination is unavailable") from exc
    try:
        after = os.fstat(fd)
    except OSError as exc:
        os.close(fd)
        raise RepositoryCoordinationUnavailable(
            "repository root descriptor disappeared after lease acquisition"
        ) from exc
    if after.st_dev != before.st_dev or after.st_ino != before.st_ino or _binding_from_fd(fd) != binding:
        os.close(fd)
        raise RepositoryCoordinationError("repository root binding changed during lease acquisition")
    return RepositoryLease(fd, binding, mode)


def acquire_shared_repository_lease(repository_root: str | os.PathLike[str]) -> RepositoryLease:
    """Acquire a non-blocking shared runtime lease on the root directory inode."""

    return _acquire(repository_root, "shared")


def acquire_exclusive_repository_lease(repository_root: str | os.PathLike[str]) -> RepositoryLease:
    """Acquire a non-blocking exclusive installer lease on the root directory inode."""

    return _acquire(repository_root, "exclusive")


def validate_inherited_repository_lease(
    fd: int,
    binding: RepositoryBinding,
    lease_mode: str = "shared",
) -> RepositoryBinding:
    """Revalidate an inherited root descriptor before it is used by a child."""

    if lease_mode not in {"shared", "exclusive"}:
        raise ValueError("lease mode must be shared or exclusive")
    current = _binding_from_fd(fd)
    if current != binding:
        raise RepositoryCoordinationError("inherited repository lease binding changed")
    return current


__all__ = [
    "RepositoryBusy",
    "RepositoryCoordinationError",
    "RepositoryCoordinationUnavailable",
    "RepositoryLease",
    "acquire_exclusive_repository_lease",
    "acquire_shared_repository_lease",
    "validate_inherited_repository_lease",
]
