from __future__ import annotations

import shutil
import stat
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def path_exists(path: Path) -> bool:
    try:
        path.lstat()
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise RuntimeError(f"failed to inspect target path: path={path}\n{exc}") from exc
    return True


def remove_tree(path: Path) -> None:
    try:
        shutil.rmtree(path)
    except OSError as exc:
        raise RuntimeError(f"failed to remove directory tree: path={path}\n{exc}") from exc


def remove_target(path: Path) -> None:
    try:
        mode = path.lstat().st_mode
    except OSError as exc:
        raise RuntimeError(f"failed to inspect target path: path={path}\n{exc}") from exc

    if stat.S_ISLNK(mode) or stat.S_ISREG(mode):
        try:
            path.unlink()
        except OSError as exc:
            raise RuntimeError(f"failed to remove target path: path={path}\n{exc}") from exc
        return

    if stat.S_ISDIR(mode):
        remove_tree(path)
        return

    raise RuntimeError(f"unsupported target path type: path={path}")


def path_kind(path: Path) -> str:
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return "missing"
    except OSError as exc:
        raise RuntimeError("failed to inspect workbench path") from exc
    if stat.S_ISLNK(mode):
        return "symlink"
    if stat.S_ISDIR(mode):
        return "directory"
    if stat.S_ISREG(mode):
        return "file"
    return "other"


def copy_workbench(source: Path, destination: Path) -> None:
    """Merge an opaque Workbench tree without following symlinks."""
    try:
        if not stat.S_ISDIR(source.lstat().st_mode):
            raise RuntimeError("workbench copy source is not a directory")
        destination_kind = path_kind(destination)
        if destination_kind == "missing":
            destination.mkdir(parents=False)
        elif destination_kind != "directory":
            raise RuntimeError("workbench copy destination is not a directory")
        for source_entry in sorted(source.iterdir(), key=lambda entry: entry.name):
            _merge_workbench_entry(source_entry, destination / source_entry.name)
    except OSError as exc:
        raise RuntimeError("workbench copy failed") from exc


def _merge_workbench_entry(source: Path, destination: Path) -> None:
    source_kind = path_kind(source)
    destination_kind = path_kind(destination)

    if source_kind == "directory":
        if destination_kind == "missing":
            destination.mkdir()
        elif destination_kind != "directory":
            raise RuntimeError("workbench copy entry type collision")
        for child in sorted(source.iterdir(), key=lambda entry: entry.name):
            _merge_workbench_entry(child, destination / child.name)
        return

    if source_kind not in {"file", "symlink"}:
        raise RuntimeError("workbench copy source entry type is unsupported")
    if destination_kind == "directory" or destination_kind == "other":
        raise RuntimeError("workbench copy entry type collision")
    if destination_kind in {"file", "symlink"}:
        destination.unlink()

    if source_kind == "file":
        shutil.copy2(source, destination, follow_symlinks=False)
    else:
        destination.symlink_to(source.readlink())
