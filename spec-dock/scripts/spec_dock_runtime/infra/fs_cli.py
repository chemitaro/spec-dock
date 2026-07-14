from __future__ import annotations

import os
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


def _descriptor_identity(status: os.stat_result) -> PathIdentity:
    return status.st_dev, status.st_ino, status.st_mode


def _open_verified_regular_source(path: Path, expected: PathIdentity) -> int:
    no_follow = getattr(os, "O_NOFOLLOW", None)
    if no_follow is None:
        raise OSError("required no-follow open is unavailable")
    flags = os.O_RDONLY | no_follow | getattr(os, "O_CLOEXEC", 0)
    descriptor = os.open(path, flags)
    try:
        status = os.fstat(descriptor)
        if not stat.S_ISREG(status.st_mode) or _descriptor_identity(status) != expected:
            raise RuntimeError("workbench copy source identity changed")
    except BaseException:
        os.close(descriptor)
        raise
    return descriptor


def _open_verified_directory(path: Path, expected: DirectoryIdentity) -> int:
    no_follow = getattr(os, "O_NOFOLLOW", None)
    directory = getattr(os, "O_DIRECTORY", None)
    if no_follow is None or directory is None:
        raise OSError("required directory open flags are unavailable")
    flags = os.O_RDONLY | directory | no_follow | getattr(os, "O_CLOEXEC", 0)
    descriptor = os.open(path, flags)
    try:
        if _descriptor_identity(os.fstat(descriptor)) != expected:
            raise RuntimeError("workbench copy directory identity changed")
    except BaseException:
        os.close(descriptor)
        raise
    return descriptor


def _assert_fd_path_missing(parent_fd: int, name: str) -> None:
    try:
        os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    raise RuntimeError("workbench copy destination path appeared")


def _open_exclusive_regular_file(parent_fd: int, name: str) -> int:
    no_follow = getattr(os, "O_NOFOLLOW", None)
    if no_follow is None:
        raise OSError("required no-follow open is unavailable")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | no_follow | getattr(os, "O_CLOEXEC", 0)
    return os.open(name, flags, 0o600, dir_fd=parent_fd)


def _copy_descriptor_bytes(source_fd: int, destination_fd: int) -> None:
    while chunk := os.read(source_fd, 1024 * 1024):
        pending = memoryview(chunk)
        while pending:
            written = os.write(destination_fd, pending)
            if written == 0:
                raise OSError("workbench copy descriptor write made no progress")
            pending = pending[written:]


def _copy_regular_file(
    source: Path,
    destination: Path,
    source_identity: PathIdentity,
    destination_identity: PathIdentity | None,
    destination_parent: Path,
    destination_parent_identity: DirectoryIdentity,
    mutation_started: list[bool],
) -> None:
    source_fd = _open_verified_regular_source(source, source_identity)
    try:
        source_status = os.fstat(source_fd)
        destination_parent_fd = _open_verified_directory(destination_parent, destination_parent_identity)
        try:
            if destination_identity is not None:
                actual = os.stat(destination.name, dir_fd=destination_parent_fd, follow_symlinks=False)
                if _descriptor_identity(actual) != destination_identity:
                    raise RuntimeError("workbench copy path identity changed")
                os.unlink(destination.name, dir_fd=destination_parent_fd)
                mutation_started[0] = True
            _assert_fd_path_missing(destination_parent_fd, destination.name)
            destination_fd = _open_exclusive_regular_file(destination_parent_fd, destination.name)
            mutation_started[0] = True
            try:
                _copy_descriptor_bytes(source_fd, destination_fd)
                os.fchmod(destination_fd, stat.S_IMODE(source_status.st_mode))
                os.utime(
                    destination_fd,
                    ns=(source_status.st_atime_ns, source_status.st_mtime_ns),
                )
            finally:
                os.close(destination_fd)
        finally:
            os.close(destination_parent_fd)
    finally:
        os.close(source_fd)


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
    if source_kind == "file":
        _copy_regular_file(
            source,
            destination,
            source_identity,
            destination_identity,
            destination_parent,
            destination_parent_identity,
            mutation_started,
        )
        return
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
    link_target = source.readlink()
    _assert_directory_identity(source_parent, source_parent_identity)
    _assert_path_identity(source, source_identity)
    _assert_directory_identity(destination_parent, destination_parent_identity)
    _assert_path_missing(destination)
    destination.symlink_to(link_target)
    mutation_started[0] = True
