from __future__ import annotations

import shutil
import stat
from typing import TYPE_CHECKING

from spec_dock_runtime.application.contracts import WorkbenchFilesystemError

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


def guard_workbench_ancestry(root: Path, endpoint: Path, *, allow_missing_leaf: bool = False) -> None:
    """Reject lexical escapes and symlinks without resolving their targets."""
    try:
        if not root.is_absolute() or not endpoint.is_absolute():
            raise WorkbenchFilesystemError(mutation_started=False)
        if ".." in root.parts or ".." in endpoint.parts:
            raise WorkbenchFilesystemError(mutation_started=False)
        try:
            relative = endpoint.relative_to(root)
        except ValueError as exc:
            raise WorkbenchFilesystemError(mutation_started=False) from exc

        components = (
            root,
            *(root.joinpath(*relative.parts[:index]) for index in range(1, len(relative.parts) + 1)),
        )
        for index, component in enumerate(components):
            is_endpoint = index == len(components) - 1
            try:
                mode = component.lstat().st_mode
            except FileNotFoundError:
                if allow_missing_leaf and is_endpoint:
                    return
                raise WorkbenchFilesystemError(mutation_started=False) from None
            if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
                raise WorkbenchFilesystemError(mutation_started=False)
    except WorkbenchFilesystemError:
        raise
    except OSError as exc:
        raise WorkbenchFilesystemError(mutation_started=False) from exc


def guard_workbench_inventory(specdock_dir: Path) -> None:
    """Guard the complete recursive metadata discovery surface before loading."""
    try:
        initiatives_root = specdock_dir / "initiatives"
        if not _optional_directory(initiatives_root):
            return
        pending = [initiatives_root]
        while pending:
            current = pending.pop()
            children: list[Path] = []
            for child in current.iterdir():
                if child.name == ".workbench":
                    continue
                mode = child.lstat().st_mode
                if child.name == ".meta.json":
                    if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
                        raise WorkbenchFilesystemError(mutation_started=False)
                    continue
                if stat.S_ISLNK(mode):
                    if child.is_dir():
                        raise WorkbenchFilesystemError(mutation_started=False)
                    continue
                if stat.S_ISDIR(mode):
                    children.append(child)
            pending.extend(sorted(children, key=lambda path: path.name, reverse=True))
    except WorkbenchFilesystemError:
        raise
    except OSError as exc:
        raise WorkbenchFilesystemError(mutation_started=False) from exc


def _optional_directory(path: Path) -> bool:
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return False
    if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
        raise WorkbenchFilesystemError(mutation_started=False)
    return True


def copy_workbench(source: Path, destination: Path) -> None:
    """Merge an opaque Workbench tree without following symlinks."""
    mutation_started = [False]
    try:
        if not stat.S_ISDIR(source.lstat().st_mode):
            raise RuntimeError("workbench copy source is not a directory")
        destination_kind = path_kind(destination)
        if destination_kind == "missing":
            destination.mkdir(parents=False)
            mutation_started[0] = True
        elif destination_kind != "directory":
            raise RuntimeError("workbench copy destination is not a directory")
        for source_entry in sorted(source.iterdir(), key=lambda entry: entry.name):
            _merge_workbench_entry(source_entry, destination / source_entry.name, mutation_started)
    except WorkbenchFilesystemError:
        raise
    except (OSError, RuntimeError) as exc:
        raise WorkbenchFilesystemError(mutation_started=mutation_started[0]) from exc


def _merge_workbench_entry(source: Path, destination: Path, mutation_started: list[bool]) -> None:
    source_kind = path_kind(source)
    destination_kind = path_kind(destination)

    if source_kind == "directory":
        if destination_kind == "missing":
            destination.mkdir()
            mutation_started[0] = True
        elif destination_kind != "directory":
            raise RuntimeError("workbench copy entry type collision")
        for child in sorted(source.iterdir(), key=lambda entry: entry.name):
            _merge_workbench_entry(child, destination / child.name, mutation_started)
        return

    if source_kind not in {"file", "symlink"}:
        raise RuntimeError("workbench copy source entry type is unsupported")
    if destination_kind == "directory" or destination_kind == "other":
        raise RuntimeError("workbench copy entry type collision")
    if destination_kind in {"file", "symlink"}:
        destination.unlink()
        mutation_started[0] = True

    if source_kind == "file":
        # copy2 may have created or truncated the destination before raising.
        mutation_started[0] = True
        shutil.copy2(source, destination, follow_symlinks=False)
    else:
        destination.symlink_to(source.readlink())
        mutation_started[0] = True
