"""Memory-only Workbench inputs captured without following links."""

from __future__ import annotations

from dataclasses import dataclass
import os
import stat
from typing import TYPE_CHECKING, Literal

from spec_dock.runtime.infra.file_publication import FileSnapshot, read_regular_file
from spec_dock.runtime.infra.json_store import open_guarded_directory

if TYPE_CHECKING:
    from collections.abc import Set
    from pathlib import Path


@dataclass(frozen=True)
class WorkbenchEntry:
    kind: Literal["directory", "file", "symlink"]
    identity: tuple[int, int]
    mode: int
    file: FileSnapshot | None = None
    link: str | None = None
    link_signature: tuple[int, int, int] | None = None


def read_entry(path: Path) -> WorkbenchEntry:
    parent = open_guarded_directory(path.parent)
    try:
        observed = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
        if stat.S_ISLNK(observed.st_mode):
            link = os.readlink(path.name, dir_fd=parent)
            after = os.stat(path.name, dir_fd=parent, follow_symlinks=False)

            def signature(value: os.stat_result) -> tuple[int, int, int, int, int, int]:
                return (value.st_dev, value.st_ino, value.st_mode, value.st_size, value.st_mtime_ns, value.st_ctime_ns)

            if signature(observed) != signature(after):
                raise ValueError("Workbench symbolic link changed while reading")
            return WorkbenchEntry(
                "symlink",
                (after.st_dev, after.st_ino),
                stat.S_IMODE(after.st_mode),
                link=link,
                link_signature=(after.st_size, after.st_mtime_ns, after.st_ctime_ns),
            )
        if stat.S_ISREG(observed.st_mode):
            snapshot = read_regular_file(path)
            if snapshot.identity != (observed.st_dev, observed.st_ino):
                raise ValueError("Workbench file changed while reading")
            return WorkbenchEntry("file", snapshot.identity, snapshot.mode, snapshot)
        if not stat.S_ISDIR(observed.st_mode):
            raise ValueError("Workbench entry type is unsupported")
        descriptor = open_guarded_directory(path)
        try:
            opened = os.fstat(descriptor)
            if (opened.st_dev, opened.st_ino, opened.st_mode) != (observed.st_dev, observed.st_ino, observed.st_mode):
                raise ValueError("Workbench directory changed while reading")
            return WorkbenchEntry("directory", (opened.st_dev, opened.st_ino), stat.S_IMODE(opened.st_mode))
        finally:
            os.close(descriptor)
    finally:
        os.close(parent)


def snapshot_workbench(
    root: Path, *, missing_ok: bool = False, paths: Set[str] | None = None, ignore_path: str | None = None
) -> dict[str, WorkbenchEntry]:
    try:
        descriptor = open_guarded_directory(root)
    except FileNotFoundError:
        parent = open_guarded_directory(root.parent)
        try:
            if os.path.lexists(root) or not missing_ok:
                raise
        finally:
            os.close(parent)
        return {}
    entries: dict[str, WorkbenchEntry] = {}
    try:
        opened = os.fstat(descriptor)
        entries["."] = WorkbenchEntry("directory", (opened.st_dev, opened.st_ino), stat.S_IMODE(opened.st_mode))

        def walk(path: Path, held: int) -> None:
            names = sorted(os.listdir(held))
            for name in names:
                child = path / name
                relative = child.relative_to(root).as_posix()
                if relative == ignore_path or (paths is not None and relative not in paths):
                    continue
                observed = os.stat(name, dir_fd=held, follow_symlinks=False)
                entry = read_entry(child)
                if entry.identity != (observed.st_dev, observed.st_ino):
                    raise ValueError("Workbench entry binding changed")
                entries[relative] = entry
                if entry.kind == "directory":
                    nested = open_guarded_directory(child)
                    try:
                        opened = os.fstat(nested)
                        if entry.identity != (opened.st_dev, opened.st_ino):
                            raise ValueError("Workbench directory identity changed")
                        walk(child, nested)
                    finally:
                        os.close(nested)
            if paths is None and names != sorted(os.listdir(held)):
                raise ValueError("Workbench entries changed while reading")
            fresh = open_guarded_directory(path)
            try:
                left, right = os.fstat(held), os.fstat(fresh)
                if (left.st_dev, left.st_ino) != (right.st_dev, right.st_ino):
                    raise ValueError("Workbench directory identity changed")
            finally:
                os.close(fresh)

        walk(root, descriptor)
        return entries
    finally:
        os.close(descriptor)
