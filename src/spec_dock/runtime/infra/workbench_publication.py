"""Publish a complete opaque link without dereferencing its target."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from spec_dock.runtime.infra.file_publication import FilePublicationIncomplete
from spec_dock.runtime.infra.json_store import open_guarded_directory
from spec_dock.runtime.infra.workbench_snapshot import read_entry

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from spec_dock.runtime.infra.workbench_snapshot import WorkbenchEntry


def publish_link(
    path: Path, link: str, *, stage_name: str, verify: Callable[[], object], expected: WorkbenchEntry | None = None
) -> None:
    if stage_name in ("", ".", "..") or "/" in stage_name or "\\" in stage_name:
        raise ValueError("stage name must be a single component")
    parent = open_guarded_directory(path.parent)
    candidate = None
    attempted = confirmed = False
    try:
        verify()
        if expected is not None and read_entry(path) != expected:
            raise ValueError("link destination changed before replacement")
        if expected is None and os.path.lexists(path):
            raise ValueError("link destination already exists")
        os.symlink(link, stage_name, dir_fd=parent)
        candidate = read_entry(path.parent / stage_name)
        verify()
        fresh = open_guarded_directory(path.parent)
        try:
            left, right = os.fstat(parent), os.fstat(fresh)
            if (left.st_dev, left.st_ino) != (right.st_dev, right.st_ino):
                raise ValueError("link publication parent changed")
        finally:
            os.close(fresh)
        if read_entry(path.parent / stage_name) != candidate or candidate.link != link:
            raise ValueError("link publication candidate changed")
        if expected is not None and read_entry(path) != expected:
            raise ValueError("link destination changed before replacement")
        attempted = True
        if expected is not None:
            os.replace(stage_name, path.name, src_dir_fd=parent, dst_dir_fd=parent)
        else:
            try:
                os.link(stage_name, path.name, src_dir_fd=parent, dst_dir_fd=parent, follow_symlinks=False)
            except FileExistsError as error:
                attempted = False
                raise ValueError("link destination publication conflict") from error
            os.unlink(stage_name, dir_fd=parent)
        os.fsync(parent)
        published = read_entry(path)
        if published.identity != candidate.identity or published.link != link:
            raise ValueError("link publication readback changed")
        confirmed = True
    except (OSError, ValueError, RuntimeError) as error:
        if attempted:
            raise FilePublicationIncomplete(str(error), confirmed=confirmed) from error
        raise
    finally:
        try:
            if candidate is not None and not attempted:
                try:
                    observed = os.stat(stage_name, dir_fd=parent, follow_symlinks=False)
                    if (observed.st_dev, observed.st_ino) == candidate.identity:
                        os.unlink(stage_name, dir_fd=parent)
                except FileNotFoundError:
                    pass
        finally:
            try:
                os.close(parent)
            except OSError as error:
                if attempted:
                    raise FilePublicationIncomplete(str(error), confirmed=confirmed) from error
                raise
