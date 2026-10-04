"""Physical directory handles shared by project admission and Start."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from spec_dock.runtime.domain.work_target import PhysicalIdentity
from spec_dock.runtime.infra.json_store import open_guarded_directory

if TYPE_CHECKING:
    from pathlib import Path
    from types import TracebackType


class DirectoryIdentity:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.descriptor: int | None = None

    def __enter__(self) -> DirectoryIdentity:
        if self.descriptor is not None:
            raise RuntimeError("physical directory handle is already open")
        self.descriptor = open_guarded_directory(self.path)
        return self

    @property
    def identity(self) -> PhysicalIdentity:
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
        if self.descriptor is not None:
            descriptor, self.descriptor = self.descriptor, None
            os.close(descriptor)
