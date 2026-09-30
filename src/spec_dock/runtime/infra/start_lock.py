"""Start's only shared lock; the existing Git directory is never changed."""

from __future__ import annotations

import math
import os
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from types import TracebackType


class StartLockBusy(TimeoutError):
    pass


class StartLock:
    def __init__(self, common_dir: Path, *, timeout: float = 5.0) -> None:
        self.common_dir = common_dir
        self.timeout = timeout
        self._fd: int | None = None

    def __enter__(self) -> StartLock:
        if not math.isfinite(self.timeout) or not 0 <= self.timeout <= 300:
            raise ValueError("Start lock timeout must be finite and between 0 and 300 seconds")
        if self._fd is not None:
            raise RuntimeError("Start lock is already held")
        if os.name != "posix":
            raise NotImplementedError("Start lock is not supported on this platform")
        import fcntl

        fd = os.open(self.common_dir, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        os.set_inheritable(fd, False)
        deadline = time.monotonic() + self.timeout
        try:
            while True:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError as error:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise StartLockBusy("another work start holds the clone lock") from error
                    time.sleep(min(0.05, remaining))
        except BaseException:
            os.close(fd)
            raise
        self._fd = fd
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None
    ) -> None:
        if self._fd is not None:
            import fcntl

            fd, self._fd = self._fd, None
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)
