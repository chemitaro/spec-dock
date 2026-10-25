"""The catalog lock shared by catalog-writing commands and sync: a flock on the catalog directory (contract C4).

It creates no file, so a sandboxed process can take it, and it is separate from the clone Start lock so
catalog writes never make work start wait. Never use the network while holding it.
"""

from __future__ import annotations

import math
import os
import time
from typing import TYPE_CHECKING

from spec_dock.runtime.infra.identity import DirectoryIdentity

if TYPE_CHECKING:
    from pathlib import Path
    from types import TracebackType


class CatalogLockBusy(TimeoutError):
    pass


class CatalogLock:
    def __init__(self, catalog: Path, *, timeout: float = 10.0) -> None:
        self.catalog = catalog
        self.timeout = timeout
        self._fd: int | None = None
        self._directory: DirectoryIdentity | None = None

    def __enter__(self) -> CatalogLock:
        if not math.isfinite(self.timeout) or not 0 <= self.timeout <= 300:
            raise ValueError("catalog lock timeout must be finite and between 0 and 300 seconds")
        if self._directory is not None:
            raise RuntimeError("catalog lock is already held")
        if os.name != "posix":
            raise NotImplementedError("catalog lock is not supported on this platform")
        import fcntl

        directory = DirectoryIdentity(self.catalog).__enter__()
        fd = directory.descriptor
        assert fd is not None
        deadline = time.monotonic() + self.timeout
        try:
            while True:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError as error:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise CatalogLockBusy("another SpecDock command or sync holds the catalog lock") from error
                    time.sleep(min(0.05, remaining))
        except BaseException:
            directory.__exit__(None, None, None)
            raise
        self._fd = fd
        self._directory = directory
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
                directory, self._directory = self._directory, None
                assert directory is not None
                directory.__exit__(None, None, None)
