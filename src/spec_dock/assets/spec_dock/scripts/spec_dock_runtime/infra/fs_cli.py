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
    """Copy the S02 single-file Workbench slice; broader merge semantics follow in S04."""
    try:
        if not stat.S_ISDIR(source.lstat().st_mode):
            raise RuntimeError("workbench copy source is not a directory")
        entries = list(source.iterdir())
    except OSError as exc:
        raise RuntimeError("workbench copy source is unavailable") from exc
    if not entries:
        try:
            destination.mkdir(parents=False, exist_ok=True)
        except OSError as exc:
            raise RuntimeError("workbench copy failed") from exc
        return
    if len(entries) != 1 or not stat.S_ISREG(entries[0].lstat().st_mode):
        raise RuntimeError("workbench copy source is outside the current single-file slice")

    source_file = entries[0]
    try:
        try:
            destination_mode = destination.lstat().st_mode
        except FileNotFoundError:
            destination.mkdir(parents=False)
        else:
            if not stat.S_ISDIR(destination_mode):
                raise RuntimeError("workbench copy destination is not a directory")
        destination_file = destination / source_file.name
        try:
            destination_file_mode = destination_file.lstat().st_mode
        except FileNotFoundError:
            pass
        else:
            if not stat.S_ISREG(destination_file_mode):
                raise RuntimeError("workbench copy destination entry has an unsupported type")
        shutil.copy2(source_file, destination_file)
    except OSError as exc:
        raise RuntimeError("workbench copy failed") from exc
