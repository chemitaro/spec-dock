"""Inspect required planning document names and types, never their contents."""

from __future__ import annotations

import os
import stat
from typing import TYPE_CHECKING

from spec_dock.runtime.infra.json_store import open_guarded_directory

if TYPE_CHECKING:
    from pathlib import Path

REQUIRED_SCOPE_DOCUMENTS = ("requirement.md", "design.md", "plan.md", "report.md")


def invalid_required_documents(owner: Path) -> tuple[str, ...]:
    descriptor = open_guarded_directory(owner)
    try:
        invalid: list[str] = []
        for filename in REQUIRED_SCOPE_DOCUMENTS:
            try:
                info = os.stat(filename, dir_fd=descriptor, follow_symlinks=False)
            except FileNotFoundError:
                invalid.append(filename)
            else:
                if not stat.S_ISREG(info.st_mode):
                    invalid.append(filename)
        fresh = open_guarded_directory(owner)
        try:
            before, after = os.fstat(descriptor), os.fstat(fresh)
            if (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino):
                raise ValueError("Scope document directory changed during inspection")
        finally:
            os.close(fresh)
        return tuple(invalid)
    finally:
        os.close(descriptor)
