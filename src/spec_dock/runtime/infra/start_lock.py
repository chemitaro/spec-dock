"""Start's only shared lock; the existing Git directory is never changed."""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import time
from typing import TYPE_CHECKING

from spec_dock.runtime.infra.identity import DirectoryIdentity

if TYPE_CHECKING:
    from pathlib import Path
    from types import TracebackType

    from spec_dock.runtime.domain.work_target import PhysicalIdentity
    from spec_dock.runtime.infra.windows_handles import WindowsMutex


class StartLockBusy(TimeoutError):
    pass


def windows_mutex_name(identity: PhysicalIdentity) -> str:
    if identity.platform != "windows":
        raise ValueError("Windows mutex requires Windows physical identity")
    canonical = json.dumps(
        ["specdock.start/v1", identity.platform, identity.device, identity.file_id], separators=(",", ":")
    ).encode("utf-8")
    return "Global\\SpecDock.Start.v1." + hashlib.sha256(canonical).hexdigest()


class StartLock:
    def __init__(self, common_dir: Path, *, timeout: float = 5.0) -> None:
        self.common_dir = common_dir
        self.timeout = timeout
        self._fd: int | None = None
        self._directory: DirectoryIdentity | None = None
        self._mutex: WindowsMutex | None = None

    def __enter__(self) -> StartLock:
        if not math.isfinite(self.timeout) or not 0 <= self.timeout <= 300:
            raise ValueError("Start lock timeout must be finite and between 0 and 300 seconds")
        if self._directory is not None:
            raise RuntimeError("Start lock is already held")
        if sys.platform == "win32":
            from spec_dock.runtime.infra.windows_handles import WindowsMutex

            directory = DirectoryIdentity(self.common_dir).__enter__()
            try:
                mutex = WindowsMutex(windows_mutex_name(directory.identity), timeout=self.timeout).__enter__()
            except BaseException as error:
                directory.__exit__(None, None, None)
                if isinstance(error, TimeoutError):
                    raise StartLockBusy(str(error)) from error
                raise
            self._directory, self._mutex = directory, mutex
            return self
        if os.name != "posix":
            raise NotImplementedError("Start lock is not supported on this platform")
        import fcntl

        directory = DirectoryIdentity(self.common_dir).__enter__()
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
                        raise StartLockBusy("another work start holds the clone lock") from error
                    time.sleep(min(0.05, remaining))
        except BaseException:
            directory.__exit__(None, None, None)
            raise
        self._fd = fd
        self._directory = directory
        return self

    @property
    def identity(self) -> PhysicalIdentity:
        if self._directory is None:
            raise RuntimeError("Start lock is not held")
        return self._directory.identity

    def verify(self) -> None:
        if self._directory is None:
            raise RuntimeError("Start lock is not held")
        self._directory.verify()

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None
    ) -> None:
        if self._mutex is not None:
            mutex, self._mutex = self._mutex, None
            try:
                mutex.__exit__(exc_type, exc, tb)
            finally:
                directory, self._directory = self._directory, None
                assert directory is not None
                directory.__exit__(exc_type, exc, tb)
        if sys.platform != "win32" and self._fd is not None:
            import fcntl

            fd, self._fd = self._fd, None
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                directory, self._directory = self._directory, None
                assert directory is not None
                directory.__exit__(None, None, None)
