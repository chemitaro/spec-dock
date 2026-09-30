"""OS-owned advisory locks for common writers and worktree lifetime leases."""

from __future__ import annotations

from contextlib import ExitStack, contextmanager
import errno
import importlib
import os
import re
import stat
import time
from typing import TYPE_CHECKING

if os.name == "nt":
    _msvcrt = importlib.import_module("msvcrt")
else:
    import fcntl

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path
    from types import TracebackType

_WORKTREE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


class WriterLockBusy(TimeoutError):
    pass


def _lock_file(common_dir: Path, name: str) -> Path:
    if not common_dir.is_absolute():
        raise ValueError("Git common directory must be absolute")
    control = common_dir / "spec-dock" / "control"
    lock_dir = control / "locks"
    for directory in (common_dir / "spec-dock", control, lock_dir):
        directory.mkdir(mode=0o700, exist_ok=True)
        if directory.is_symlink():
            raise ValueError("control lock directory must not be a symlink")
    return lock_dir / name


def _try_lock(fd: int, *, exclusive: bool) -> bool:
    try:
        if os.name == "nt":
            os.lseek(fd, 0, os.SEEK_SET)
            _msvcrt.locking(fd, getattr(_msvcrt, "LK_NBLCK" if exclusive else "LK_NBRLCK"), 1)
        else:
            fcntl.flock(fd, (fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH) | fcntl.LOCK_NB)
        return True
    except (BlockingIOError, OSError) as exc:
        if isinstance(exc, BlockingIOError) or getattr(exc, "errno", None) in {
            errno.EAGAIN,
            errno.EACCES,
            errno.EWOULDBLOCK,
        }:
            return False
        raise


def _unlock(fd: int) -> None:
    if os.name == "nt":
        os.lseek(fd, 0, os.SEEK_SET)
        _msvcrt.locking(fd, _msvcrt.LK_UNLCK, 1)
    else:
        fcntl.flock(fd, fcntl.LOCK_UN)


class _AdvisoryLock:
    def __init__(self, path: Path, *, exclusive: bool, timeout: float) -> None:
        if timeout < 0:
            raise ValueError("lock timeout must be nonnegative")
        self.path = path
        self.exclusive = exclusive
        self.timeout = timeout
        self._fd: int | None = None

    def __enter__(self) -> _AdvisoryLock:
        flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(self.path, flags, 0o600)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise ValueError("lock path must be a regular file")
            if os.name == "nt" and os.fstat(fd).st_size == 0:
                os.write(fd, b"\0")
            deadline = time.monotonic() + self.timeout
            while not _try_lock(fd, exclusive=self.exclusive):
                if time.monotonic() >= deadline:
                    raise WriterLockBusy(f"writer lock is busy: {self.path.name}")
                time.sleep(min(0.05, max(0.0, deadline - time.monotonic())))
            self._fd = fd
            return self
        except BaseException:
            os.close(fd)
            raise

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._fd is not None:
            try:
                _unlock(self._fd)
            finally:
                os.close(self._fd)
                self._fd = None


class WriterLock(_AdvisoryLock):
    def __init__(self, common_dir: Path, *, timeout: float = 0) -> None:
        super().__init__(_lock_file(common_dir, "writer.lock"), exclusive=True, timeout=timeout)


class WorktreeLease(_AdvisoryLock):
    def __init__(self, common_dir: Path, worktree_id: str, *, exclusive: bool, timeout: float = 0) -> None:
        if not _WORKTREE_ID.fullmatch(worktree_id):
            raise ValueError("invalid worktree ID for lease")
        super().__init__(_lock_file(common_dir, f"worktree-{worktree_id}.lock"), exclusive=exclusive, timeout=timeout)


@contextmanager
def writer_transaction(common_dir: Path, *, worktree_ids: tuple[str, ...] = (), timeout: float = 0) -> Iterator[None]:
    """Take the common writer lock before exclusive leases in stable ID order."""
    with ExitStack() as stack:
        stack.enter_context(WriterLock(common_dir, timeout=timeout))
        for worktree_id in sorted(set(worktree_ids)):
            stack.enter_context(WorktreeLease(common_dir, worktree_id, exclusive=True, timeout=timeout))
        yield
