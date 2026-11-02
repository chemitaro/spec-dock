"""One-file cooperative metadata replacement without a persistent transaction journal."""

from __future__ import annotations

from contextlib import suppress
import os
from typing import TYPE_CHECKING

from spec_dock.runtime.infra.json_store import open_guarded_directory

if TYPE_CHECKING:
    from pathlib import Path


def _create_guarded_directory(path: Path) -> int:
    if not path.is_absolute():
        raise ValueError("metadata staging must be absolute")
    ancestor = path
    missing: list[str] = []
    while not ancestor.exists():
        missing.append(ancestor.name)
        ancestor = ancestor.parent
    descriptor = open_guarded_directory(ancestor)
    try:
        for name in reversed(missing):
            with suppress(FileExistsError):
                os.mkdir(name, mode=0o700, dir_fd=descriptor)
            child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise
