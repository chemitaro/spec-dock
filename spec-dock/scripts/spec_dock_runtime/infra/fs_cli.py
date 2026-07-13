from __future__ import annotations

import shutil
import stat
from typing import TYPE_CHECKING

from spec_dock_runtime.application.contracts import WorkbenchFilesystemError

if TYPE_CHECKING:
    from pathlib import Path


DirectoryIdentity = tuple[int, int, int]
PathIdentity = tuple[int, int, int]


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


def _capture_directory_identity(path: Path) -> DirectoryIdentity:
    status = path.lstat()
    if not stat.S_ISDIR(status.st_mode):
        raise RuntimeError("workbench copy path is not a directory")
    return status.st_dev, status.st_ino, status.st_mode


def _assert_directory_identity(path: Path, expected: DirectoryIdentity) -> None:
    if _capture_directory_identity(path) != expected:
        raise RuntimeError("workbench copy directory identity changed")


def _inspect_path(path: Path) -> tuple[str, PathIdentity | None]:
    try:
        status = path.lstat()
    except FileNotFoundError:
        return "missing", None
    identity = status.st_dev, status.st_ino, status.st_mode
    if stat.S_ISDIR(status.st_mode):
        return "directory", identity
    if stat.S_ISREG(status.st_mode):
        return "file", identity
    if stat.S_ISLNK(status.st_mode):
        return "symlink", identity
    return "other", identity


def _assert_path_identity(path: Path, expected: PathIdentity) -> None:
    _, actual = _inspect_path(path)
    if actual != expected:
        raise RuntimeError("workbench copy path identity changed")


def _assert_path_missing(path: Path) -> None:
    kind, _ = _inspect_path(path)
    if kind != "missing":
        raise RuntimeError("workbench copy destination path appeared")


def copy_workbench(source: Path, destination: Path) -> None:
    """Merge an opaque Workbench tree without following symlinks."""
    mutation_started = [False]
    try:
        source_identity = _capture_directory_identity(source)
        destination_kind, destination_identity = _inspect_path(destination)
        if destination_kind == "missing":
            destination_parent_identity = _capture_directory_identity(destination.parent)
            _assert_directory_identity(source, source_identity)
            _assert_directory_identity(destination.parent, destination_parent_identity)
            destination.mkdir(parents=False)
            mutation_started[0] = True
            _assert_directory_identity(destination.parent, destination_parent_identity)
            destination_identity = _capture_directory_identity(destination)
        elif destination_kind != "directory":
            raise RuntimeError("workbench copy destination is not a directory")
        if destination_identity is None:
            raise RuntimeError("workbench copy destination identity is missing")
        _merge_workbench_directory(
            source,
            destination,
            source_identity,
            destination_identity,
            mutation_started,
        )
    except WorkbenchFilesystemError:
        raise
    except (OSError, RuntimeError) as exc:
        raise WorkbenchFilesystemError(mutation_started=mutation_started[0]) from exc


def _merge_workbench_directory(
    source: Path,
    destination: Path,
    source_identity: DirectoryIdentity,
    destination_identity: DirectoryIdentity,
    mutation_started: list[bool],
) -> None:
    _assert_directory_identity(source, source_identity)
    _assert_directory_identity(destination, destination_identity)
    source_entries = sorted(source.iterdir(), key=lambda entry: entry.name)
    _assert_directory_identity(source, source_identity)
    _assert_directory_identity(destination, destination_identity)
    for source_entry in source_entries:
        _assert_directory_identity(source, source_identity)
        _assert_directory_identity(destination, destination_identity)
        _merge_workbench_entry(
            source_entry,
            destination / source_entry.name,
            source,
            destination,
            source_identity,
            destination_identity,
            mutation_started,
        )


def _merge_workbench_entry(
    source: Path,
    destination: Path,
    source_parent: Path,
    destination_parent: Path,
    source_parent_identity: DirectoryIdentity,
    destination_parent_identity: DirectoryIdentity,
    mutation_started: list[bool],
) -> None:
    _assert_directory_identity(source_parent, source_parent_identity)
    _assert_directory_identity(destination_parent, destination_parent_identity)
    source_kind, source_identity = _inspect_path(source)
    destination_kind, destination_identity = _inspect_path(destination)

    if source_kind == "directory":
        _assert_directory_identity(source_parent, source_parent_identity)
        if source_identity is None:
            raise RuntimeError("workbench copy source identity is missing")
        _assert_path_identity(source, source_identity)
        if destination_kind == "missing":
            _assert_directory_identity(destination_parent, destination_parent_identity)
            destination.mkdir()
            mutation_started[0] = True
            _assert_directory_identity(destination_parent, destination_parent_identity)
            destination_identity = _capture_directory_identity(destination)
        elif destination_kind != "directory":
            raise RuntimeError("workbench copy entry type collision")
        elif destination_identity is None:
            raise RuntimeError("workbench copy destination identity is missing")
        _assert_path_identity(destination, destination_identity)
        _merge_workbench_directory(
            source,
            destination,
            source_identity,
            destination_identity,
            mutation_started,
        )
        return

    if source_kind not in {"file", "symlink"}:
        raise RuntimeError("workbench copy source entry type is unsupported")
    if source_identity is None:
        raise RuntimeError("workbench copy source identity is missing")
    if destination_kind == "directory" or destination_kind == "other":
        raise RuntimeError("workbench copy entry type collision")
    if destination_kind in {"file", "symlink"}:
        if destination_identity is None:
            raise RuntimeError("workbench copy destination identity is missing")
        _assert_directory_identity(destination_parent, destination_parent_identity)
        _assert_path_identity(destination, destination_identity)
        destination.unlink()
        mutation_started[0] = True

    _assert_directory_identity(source_parent, source_parent_identity)
    _assert_path_identity(source, source_identity)
    _assert_directory_identity(destination_parent, destination_parent_identity)
    if source_kind == "file":
        _assert_path_missing(destination)
        # copy2 may have created or truncated the destination before raising.
        mutation_started[0] = True
        shutil.copy2(source, destination, follow_symlinks=False)
    else:
        link_target = source.readlink()
        _assert_directory_identity(source_parent, source_parent_identity)
        _assert_path_identity(source, source_identity)
        _assert_directory_identity(destination_parent, destination_parent_identity)
        _assert_path_missing(destination)
        destination.symlink_to(link_target)
        mutation_started[0] = True
