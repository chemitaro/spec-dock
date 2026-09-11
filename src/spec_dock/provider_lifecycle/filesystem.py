"""Descriptor-relative filesystem operations with closed native atomics."""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
import errno
import hashlib
import os
from pathlib import Path
import posixpath
import secrets
import stat
from typing import TYPE_CHECKING, Protocol

from spec_dock.provider_lifecycle.contracts import InodeWitness

if TYPE_CHECKING:
    from collections.abc import Collection, Iterable


class FilesystemSafetyError(RuntimeError):
    """A bound object changed or has an unsafe filesystem identity."""


class AtomicRenameUnavailable(RuntimeError):
    """The host does not provide the required native atomic operation."""


@dataclass(frozen=True, slots=True)
class TreeEntry:
    kind: str
    path: str
    mode: int | None = None
    sha256: str | None = None
    target: str | None = None


@dataclass(frozen=True, slots=True)
class DomainTreeIdentity:
    tree_digest: str
    entry_count: int
    entries: tuple[TreeEntry, ...]


class _NativeAdapter(Protocol):
    def rename_no_replace(self, src_parent_fd: int, src_name: str, dst_parent_fd: int, dst_name: str) -> None: ...

    def exchange(self, src_parent_fd: int, src_name: str, dst_parent_fd: int, dst_name: str) -> None: ...


def _fd_flags() -> int:
    return os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0)


def _object_kind(mode: int) -> str:
    if stat.S_ISREG(mode):
        return "regular"
    if stat.S_ISDIR(mode):
        return "directory"
    if stat.S_ISLNK(mode):
        return "symlink"
    return "special"


def _native_error(name: str, error_number: int) -> AtomicRenameUnavailable:
    return AtomicRenameUnavailable(f"{name} unavailable: errno {error_number}")


class _LibCAtomicAdapter:
    """Common ctypes binding helpers for the platform-specific adapters."""

    def __init__(self, symbol: str, flags: dict[str, int]) -> None:
        self._symbol_name = symbol
        self._flags = flags
        try:
            library = ctypes.CDLL(None, use_errno=True)
            function = getattr(library, symbol)
        except AttributeError as exc:
            raise AtomicRenameUnavailable(f"libc {symbol} is unavailable") from exc
        function.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        function.restype = ctypes.c_int
        self._function = function

    def _call(self, flag: int, src_parent_fd: int, src_name: str, dst_parent_fd: int, dst_name: str) -> None:
        if "\x00" in src_name or "\x00" in dst_name:
            raise FilesystemSafetyError("native atomic names cannot contain NUL")
        result = self._function(
            src_parent_fd,
            os.fsencode(src_name),
            dst_parent_fd,
            os.fsencode(dst_name),
            flag,
        )
        if result == 0:
            return
        error_number = ctypes.get_errno()
        if error_number in {errno.ENOSYS, errno.EINVAL, errno.ENOTSUP, getattr(errno, "EOPNOTSUPP", errno.ENOTSUP)}:
            raise _native_error(self._symbol_name, error_number)
        raise OSError(error_number, os.strerror(error_number), src_name)


class LinuxRenameAt2Adapter(_LibCAtomicAdapter):
    """Linux ``renameat2`` adapter; no path-only downgrade exists."""

    RENAME_NOREPLACE = 1
    RENAME_EXCHANGE = 2

    def __init__(self) -> None:
        if sys_platform() != "linux":
            raise AtomicRenameUnavailable("renameat2 is a Linux-only primitive")
        super().__init__("renameat2", {"no_replace": self.RENAME_NOREPLACE, "exchange": self.RENAME_EXCHANGE})

    def rename_no_replace(self, src_parent_fd: int, src_name: str, dst_parent_fd: int, dst_name: str) -> None:
        self._call(self._flags["no_replace"], src_parent_fd, src_name, dst_parent_fd, dst_name)

    def exchange(self, src_parent_fd: int, src_name: str, dst_parent_fd: int, dst_name: str) -> None:
        self._call(self._flags["exchange"], src_parent_fd, src_name, dst_parent_fd, dst_name)


class MacOSRenameAtXAdapter(_LibCAtomicAdapter):
    """macOS ``renameatx_np`` adapter; no path-only downgrade exists."""

    RENAME_EXCL = 0x00000004
    RENAME_SWAP = 0x00000002

    def __init__(self) -> None:
        if sys_platform() != "darwin":
            raise AtomicRenameUnavailable("renameatx_np is a macOS-only primitive")
        super().__init__("renameatx_np", {"no_replace": self.RENAME_EXCL, "exchange": self.RENAME_SWAP})

    def rename_no_replace(self, src_parent_fd: int, src_name: str, dst_parent_fd: int, dst_name: str) -> None:
        self._call(self._flags["no_replace"], src_parent_fd, src_name, dst_parent_fd, dst_name)

    def exchange(self, src_parent_fd: int, src_name: str, dst_parent_fd: int, dst_name: str) -> None:
        self._call(self._flags["exchange"], src_parent_fd, src_name, dst_parent_fd, dst_name)


def sys_platform() -> str:
    """A tiny seam that keeps platform selection easy to test."""

    import sys

    return sys.platform


class BoundDirectory:
    """An owned descriptor for one no-follow directory chain."""

    def __init__(self, fd: int) -> None:
        self.fd = fd
        self._closed = False

    @property
    def closed(self) -> bool:
        return self._closed

    def close(self) -> None:
        if not self._closed:
            os.close(self.fd)
            self._closed = True

    def __enter__(self) -> BoundDirectory:
        if self._closed:
            raise ValueError("directory descriptor is closed")
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class NativeAtomicFilesystem:
    """Closed descriptor-relative filesystem facade."""

    def __init__(self, adapter: _NativeAdapter | None = None) -> None:
        self.adapter = adapter if adapter is not None else self._current_adapter()

    @staticmethod
    def _current_adapter() -> _NativeAdapter:
        if sys_platform() == "linux":
            return LinuxRenameAt2Adapter()
        if sys_platform() == "darwin":
            return MacOSRenameAtXAdapter()
        raise AtomicRenameUnavailable("no supported native atomic adapter for this host")

    def open_directory_chain_no_follow(self, absolute_path: str | os.PathLike[str]) -> BoundDirectory:
        path = os.fspath(absolute_path)
        if not Path(path).is_absolute() or "\x00" in path:
            raise FilesystemSafetyError("directory chain must be an absolute NUL-free path")
        components = list(Path(path).parts[1:])
        current_fd = os.open(os.sep, _fd_flags() | getattr(os, "O_NOFOLLOW", 0))
        try:
            for component in components:
                if component in {".", ".."}:
                    raise FilesystemSafetyError("directory chain cannot contain dot components")
                next_fd = os.open(
                    component,
                    _fd_flags() | getattr(os, "O_NOFOLLOW", 0),
                    dir_fd=current_fd,
                )
                os.close(current_fd)
                current_fd = next_fd
            return BoundDirectory(current_fd)
        except BaseException:
            os.close(current_fd)
            raise

    def capture_inode(self, parent_fd: int, name: str, expected_kind: str) -> InodeWitness | None:
        if expected_kind not in {"regular", "directory"}:
            raise ValueError("expected_kind must be regular or directory")
        try:
            before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            return None
        kind = _object_kind(before.st_mode)
        if kind != expected_kind:
            raise FilesystemSafetyError(f"{name!r} is {kind}, expected {expected_kind}")
        if kind == "regular" and before.st_nlink != 1:
            raise FilesystemSafetyError(f"{name!r} is hard-linked")
        fd = os.open(
            name,
            (_fd_flags() | getattr(os, "O_NOFOLLOW", 0))
            if kind == "directory"
            else os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        try:
            after_open = os.fstat(fd)
            if not self._same_inode(before, after_open):
                raise FilesystemSafetyError(f"{name!r} changed while opening")
            digest = None
            if kind == "regular":
                digest = self._sha256_fd(fd)
            after_read = os.fstat(fd)
            if not self._same_inode(after_open, after_read):
                raise FilesystemSafetyError(f"{name!r} changed while reading")
            visible = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            if not self._same_inode(after_read, visible):
                raise FilesystemSafetyError(f"{name!r} changed after reading")
        finally:
            os.close(fd)
        return self._witness(after_read, kind, digest)

    def capture_domain_tree(self, parent_fd: int, name: str) -> DomainTreeIdentity:
        _witness, tree = self.capture_bound_domain_tree(parent_fd, name)
        return tree

    def capture_bound_domain_tree(self, parent_fd: int, name: str) -> tuple[InodeWitness, DomainTreeIdentity]:
        """Capture a directory tree and its root witness from one bound observation."""

        root_stat = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        if not stat.S_ISDIR(root_stat.st_mode):
            raise FilesystemSafetyError(f"{name!r} is not a directory")
        root_fd = os.open(name, _fd_flags() | getattr(os, "O_NOFOLLOW", 0), dir_fd=parent_fd)
        try:
            opened = os.fstat(root_fd)
            if not self._same_inode(root_stat, opened):
                raise FilesystemSafetyError(f"{name!r} changed while opening")
            entries = tuple(
                sorted(self._capture_entries_from_fd(root_fd, ""), key=lambda entry: entry.path.encode("utf-8"))
            )
            after_scan = os.fstat(root_fd)
            if not self._same_inode(opened, after_scan):
                raise FilesystemSafetyError(f"{name!r} changed while reading")
            visible = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            if not self._same_inode(after_scan, visible):
                raise FilesystemSafetyError(f"{name!r} changed after reading")
        finally:
            os.close(root_fd)
        return self._witness(after_scan, "directory", None), _tree_identity(entries)

    def rename_no_replace(
        self,
        src_parent_fd: int,
        src_name: str,
        dst_parent_fd: int,
        dst_name: str,
        *,
        expected_source: InodeWitness | None = None,
    ) -> None:
        source = self._capture_any(src_parent_fd, src_name)
        self._ensure_directory_fd(src_parent_fd)
        self._ensure_directory_fd(dst_parent_fd)
        if expected_source is not None and (
            source is None or not self._same_content_identity(source[1], expected_source)
        ):
            raise FilesystemSafetyError("native no-replace source identity changed before mutation")
        self.adapter.rename_no_replace(src_parent_fd, src_name, dst_parent_fd, dst_name)
        destination = self._capture_any(dst_parent_fd, dst_name)
        if (
            source is None
            or destination is None
            or source[0] != destination[0]
            or not self._same_content_identity(source[1], destination[1])
        ):
            raise FilesystemSafetyError("native no-replace postcondition changed the source identity")

    def exchange(
        self,
        src_parent_fd: int,
        src_name: str,
        dst_parent_fd: int,
        dst_name: str,
        *,
        expected_source: InodeWitness | None = None,
        expected_destination: InodeWitness | None = None,
    ) -> None:
        source = self._capture_any(src_parent_fd, src_name)
        destination = self._capture_any(dst_parent_fd, dst_name)
        if source is None or destination is None:
            raise FilesystemSafetyError("native exchange requires two existing entries")
        if expected_source is not None and not self._same_content_identity(source[1], expected_source):
            raise FilesystemSafetyError("native exchange source identity changed before mutation")
        if expected_destination is not None and not self._same_content_identity(destination[1], expected_destination):
            raise FilesystemSafetyError("native exchange destination identity changed before mutation")
        self._ensure_directory_fd(src_parent_fd)
        self._ensure_directory_fd(dst_parent_fd)
        self.adapter.exchange(src_parent_fd, src_name, dst_parent_fd, dst_name)
        source_after = self._capture_any(src_parent_fd, src_name)
        destination_after = self._capture_any(dst_parent_fd, dst_name)
        if (
            source_after is None
            or destination_after is None
            or source_after[0] != destination[0]
            or destination_after[0] != source[0]
        ):
            raise FilesystemSafetyError("native exchange postcondition changed identities")

    def unlink_bound(self, parent_fd: int, name: str, expected_witness: InodeWitness) -> None:
        current = self.capture_inode(parent_fd, name, expected_witness.kind)
        if current is None or current != expected_witness:
            raise FilesystemSafetyError(f"bound unlink witness mismatch for {name!r}")
        os.unlink(name, dir_fd=parent_fd)

    def remove_tree_bound(self, parent_fd: int, name: str, expected_tree: DomainTreeIdentity) -> None:
        root_witness, current = self.capture_bound_domain_tree(parent_fd, name)
        if root_witness is None or current != expected_tree:
            raise FilesystemSafetyError(f"bound tree witness mismatch for {name!r}")
        self._remove_tree(parent_fd, name, root_witness, expected_tree.entries)

    def fsync_directory(self, fd: int) -> None:
        self._ensure_directory_fd(fd)
        os.fsync(fd)

    def probe_native_capability(self, parent_fd: int) -> None:
        """Verify both native atomic primitives without creating any entries."""

        self._ensure_directory_fd(parent_fd)
        token = secrets.token_hex(16)
        for operation in ("rename_no_replace", "exchange"):
            source = f".spec-dock-native-probe-{token}-{operation}-source"
            destination = f".spec-dock-native-probe-{token}-{operation}-destination"
            try:
                if operation == "rename_no_replace":
                    self.adapter.rename_no_replace(parent_fd, source, parent_fd, destination)
                else:
                    self.adapter.exchange(parent_fd, source, parent_fd, destination)
            except AtomicRenameUnavailable:
                raise
            except OSError as error:
                if error.errno == errno.ENOENT:
                    continue
                raise FilesystemSafetyError("native atomic capability probe failed") from error

    @staticmethod
    def _same_inode(left: os.stat_result, right: os.stat_result) -> bool:
        return (
            left.st_dev == right.st_dev
            and left.st_ino == right.st_ino
            and left.st_ctime_ns == right.st_ctime_ns
            and stat.S_IMODE(left.st_mode) == stat.S_IMODE(right.st_mode)
            and left.st_nlink == right.st_nlink
            and left.st_size == right.st_size
        )

    @staticmethod
    def _same_content_identity(left: InodeWitness, right: InodeWitness) -> bool:
        return (
            left.kind == right.kind
            and left.device == right.device
            and left.inode == right.inode
            and left.mode == right.mode
            and left.link_count == right.link_count
            and left.size == right.size
            and left.sha256 == right.sha256
        )

    @staticmethod
    def _witness(value: os.stat_result, kind: str, digest: str | None) -> InodeWitness:
        return InodeWitness(
            kind=kind,  # type: ignore[arg-type]
            device=value.st_dev,
            inode=value.st_ino,
            ctime_ns=value.st_ctime_ns,
            mode=stat.S_IMODE(value.st_mode),
            link_count=value.st_nlink,
            size=value.st_size if kind == "regular" else None,
            sha256=digest if kind == "regular" else None,
        )

    @staticmethod
    def _sha256_fd(fd: int) -> str:
        digest = hashlib.sha256()
        os.lseek(fd, 0, os.SEEK_SET)
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                return digest.hexdigest()
            digest.update(chunk)

    @staticmethod
    def _ensure_directory_fd(fd: int) -> os.stat_result:
        value = os.fstat(fd)
        if not stat.S_ISDIR(value.st_mode):
            raise FilesystemSafetyError("descriptor is not a directory")
        return value

    def _capture_any(self, parent_fd: int, name: str) -> tuple[tuple[int, int], InodeWitness] | None:
        try:
            value = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            return None
        kind = _object_kind(value.st_mode)
        if kind not in {"regular", "directory"}:
            raise FilesystemSafetyError(f"unsupported native atomic object {name!r}")
        witness = self.capture_inode(parent_fd, name, kind)
        if witness is None:
            return None
        return ((witness.device, witness.inode), witness)

    def _capture_entries(self, parent_fd: int, directory_name: str, relative_prefix: str) -> Iterable[TreeEntry]:
        directory_fd = os.open(
            directory_name,
            _fd_flags() | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        try:
            yield from self._capture_entries_from_fd(directory_fd, relative_prefix)
        finally:
            os.close(directory_fd)

    def _capture_entries_from_fd(self, directory_fd: int, relative_prefix: str) -> Iterable[TreeEntry]:
        names = sorted(os.listdir(directory_fd), key=lambda item: os.fsencode(item))
        for child_name in names:
            child_relative = posixpath.join(relative_prefix, child_name) if relative_prefix else child_name
            child_stat = os.stat(child_name, dir_fd=directory_fd, follow_symlinks=False)
            kind = _object_kind(child_stat.st_mode)
            if kind == "directory":
                yield TreeEntry("directory", child_relative)
                child_fd = os.open(
                    child_name,
                    _fd_flags() | getattr(os, "O_NOFOLLOW", 0),
                    dir_fd=directory_fd,
                )
                try:
                    opened = os.fstat(child_fd)
                    if not self._same_inode(child_stat, opened):
                        raise FilesystemSafetyError(f"{child_relative!r} changed while opening")
                    yield from self._capture_entries_from_fd(child_fd, child_relative)
                    after_scan = os.fstat(child_fd)
                    if not self._same_inode(opened, after_scan):
                        raise FilesystemSafetyError(f"{child_relative!r} changed while reading")
                    visible = os.stat(child_name, dir_fd=directory_fd, follow_symlinks=False)
                    if not self._same_inode(after_scan, visible):
                        raise FilesystemSafetyError(f"{child_relative!r} changed after reading")
                finally:
                    os.close(child_fd)
            elif kind == "regular":
                if child_stat.st_nlink != 1:
                    raise FilesystemSafetyError(f"{child_relative!r} is hard-linked")
                child_fd = os.open(
                    child_name,
                    os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
                    dir_fd=directory_fd,
                )
                try:
                    opened = os.fstat(child_fd)
                    if not self._same_inode(child_stat, opened):
                        raise FilesystemSafetyError(f"{child_relative!r} changed while opening")
                    content = self._sha256_fd(child_fd)
                    after_read = os.fstat(child_fd)
                    if not self._same_inode(opened, after_read):
                        raise FilesystemSafetyError(f"{child_relative!r} changed while reading")
                    visible = os.stat(child_name, dir_fd=directory_fd, follow_symlinks=False)
                    if not self._same_inode(after_read, visible):
                        raise FilesystemSafetyError(f"{child_relative!r} changed after reading")
                finally:
                    os.close(child_fd)
                yield TreeEntry("regular", child_relative, stat.S_IMODE(after_read.st_mode), content)
            elif kind == "symlink":
                target = os.readlink(child_name, dir_fd=directory_fd)
                after_link = os.stat(child_name, dir_fd=directory_fd, follow_symlinks=False)
                if not self._same_inode(child_stat, after_link):
                    raise FilesystemSafetyError(f"{child_relative!r} changed while reading")
                yield TreeEntry("symlink", child_relative, target=target)
            else:
                raise FilesystemSafetyError(f"unsupported tree entry at {child_relative!r}")
        if sorted(os.listdir(directory_fd), key=lambda item: os.fsencode(item)) != names:
            raise FilesystemSafetyError(f"{relative_prefix or 'tree'!r} changed while reading")

    def _remove_tree(
        self,
        parent_fd: int,
        name: str,
        expected_root: InodeWitness,
        entries: tuple[TreeEntry, ...],
    ) -> None:
        directory_fd = os.open(name, _fd_flags() | getattr(os, "O_NOFOLLOW", 0), dir_fd=parent_fd)
        try:
            opened = os.fstat(directory_fd)
            if self._witness(opened, "directory", None) != expected_root:
                raise FilesystemSafetyError("tree root changed before removal")
            self._remove_directory_contents(directory_fd, "", entries)
            current = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            if not stat.S_ISDIR(current.st_mode) or (current.st_dev, current.st_ino) != (
                expected_root.device,
                expected_root.inode,
            ):
                raise FilesystemSafetyError("tree root changed before final removal")
            os.rmdir(name, dir_fd=parent_fd)
        finally:
            os.close(directory_fd)

    def _remove_directory_contents(self, directory_fd: int, prefix: str, entries: tuple[TreeEntry, ...]) -> None:
        expected = {
            entry.path: entry
            for entry in entries
            if entry.path.startswith(prefix)
            and "/" not in entry.path[len(prefix) :].lstrip("/")
            and entry.path != prefix
        }
        names = sorted(os.listdir(directory_fd), key=lambda item: os.fsencode(item))
        if set(names) != {path[len(prefix) + 1 :] if prefix else path for path in expected}:
            raise FilesystemSafetyError("tree changed before bound removal")
        for name in names:
            relative = posixpath.join(prefix, name) if prefix else name
            entry = expected[relative]
            if entry.kind == "directory":
                witness = self.capture_inode(directory_fd, name, "directory")
                if witness is None:
                    raise FilesystemSafetyError("directory disappeared during bound removal")
                child_fd = os.open(name, _fd_flags() | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory_fd)
                try:
                    opened = os.fstat(child_fd)
                    if (opened.st_dev, opened.st_ino) != (witness.device, witness.inode):
                        raise FilesystemSafetyError("directory changed before bound removal")
                    self._remove_directory_contents(child_fd, relative, entries)
                finally:
                    os.close(child_fd)
                current = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
                if not stat.S_ISDIR(current.st_mode) or (current.st_dev, current.st_ino) != (
                    witness.device,
                    witness.inode,
                ):
                    raise FilesystemSafetyError("directory changed before final removal")
                os.rmdir(name, dir_fd=directory_fd)
            elif entry.kind == "regular":
                witness = self.capture_inode(directory_fd, name, "regular")
                if witness is None or witness.mode != entry.mode or witness.sha256 != entry.sha256:
                    raise FilesystemSafetyError("regular entry changed during bound removal")
                os.unlink(name, dir_fd=directory_fd)
            elif entry.kind == "symlink":
                value = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
                target = os.readlink(name, dir_fd=directory_fd)
                after_read = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
                if not stat.S_ISLNK(value.st_mode) or target != entry.target or not self._same_inode(value, after_read):
                    raise FilesystemSafetyError("symlink entry changed during bound removal")
                os.unlink(name, dir_fd=directory_fd)
            else:
                raise FilesystemSafetyError("unsupported entry during bound removal")


def _tree_identity(entries: tuple[TreeEntry, ...]) -> DomainTreeIdentity:
    stream = bytearray()
    for entry in entries:
        relative = entry.path.encode("utf-8")
        if entry.kind == "directory":
            stream.extend(b"D\0" + relative + b"\0")
        elif entry.kind == "regular":
            assert entry.mode is not None and entry.sha256 is not None
            stream.extend(
                b"F\0" + relative + b"\0" + f"{entry.mode:04o}".encode() + b"\0" + entry.sha256.encode() + b"\0"
            )
        elif entry.kind == "symlink":
            assert entry.target is not None
            stream.extend(b"L\0" + relative + b"\0" + entry.target.encode("utf-8") + b"\0")
        else:
            raise FilesystemSafetyError("unsupported tree entry")
    return DomainTreeIdentity(hashlib.sha256(stream).hexdigest(), len(entries), entries)


def project_domain_tree(tree: DomainTreeIdentity, *, exclude_root_names: Collection[str] = ()) -> DomainTreeIdentity:
    """Return the canonical identity after excluding selected root entries."""

    excluded = frozenset(exclude_root_names)
    entries = tuple(entry for entry in tree.entries if entry.path not in excluded)
    return _tree_identity(entries)


__all__ = [
    "AtomicRenameUnavailable",
    "BoundDirectory",
    "DomainTreeIdentity",
    "FilesystemSafetyError",
    "LinuxRenameAt2Adapter",
    "MacOSRenameAtXAdapter",
    "NativeAtomicFilesystem",
    "TreeEntry",
    "project_domain_tree",
]
