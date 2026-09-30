"""Physical directory handles shared by project admission and Start."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from spec_dock.runtime.domain.work_target import PhysicalIdentity
from spec_dock.runtime.infra.json_store import open_guarded_directory

if TYPE_CHECKING:
    from pathlib import Path
    from types import TracebackType

    from spec_dock.runtime.infra.windows_handles import WindowsDirectory


class DirectoryIdentity:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.descriptor: int | None = None
        self._windows: WindowsDirectory | None = None

    def __enter__(self) -> DirectoryIdentity:
        if self.descriptor is not None or self._windows is not None:
            raise RuntimeError("physical directory handle is already open")
        if os.name == "nt":
            from spec_dock.runtime.infra.windows_handles import WindowsDirectory

            self._windows = WindowsDirectory(self.path).__enter__()
        elif os.name == "posix":
            self.descriptor = open_guarded_directory(self.path)
        else:
            raise NotImplementedError("physical directory adapter is not connected for this platform")
        return self

    @property
    def identity(self) -> PhysicalIdentity:
        if self._windows is not None:
            return self._windows.identity
        if self.descriptor is None:
            raise RuntimeError("physical directory handle is not open")
        observed = os.fstat(self.descriptor)
        return PhysicalIdentity("posix", str(observed.st_dev), str(observed.st_ino))

    def verify(self) -> None:
        with DirectoryIdentity(self.path) as current:
            if current.identity != self.identity:
                raise ValueError("directory physical identity changed")

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None
    ) -> None:
        if self._windows is not None:
            windows, self._windows = self._windows, None
            windows.__exit__(exc_type, exc, tb)
        if self.descriptor is not None:
            descriptor, self.descriptor = self.descriptor, None
            os.close(descriptor)
