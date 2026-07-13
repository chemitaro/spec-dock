from __future__ import annotations

import ctypes
import errno
import hashlib
import os
from pathlib import Path
import stat
import sys
import tempfile
from typing import TYPE_CHECKING

from spec_dock_runtime.application.contracts import (
    BinaryArtifactCleanupState,
    BinaryArtifactPublishError,
    BinaryArtifactPublishRequest,
    BinaryArtifactPublishResult,
    BinaryArtifactPublishWarning,
    GuardedWorkbenchSource,
    WorkbenchSourceGuardRequest,
)

if TYPE_CHECKING:
    from collections.abc import Callable


_UNSUPPORTED_PUBLICATION_ERRNOS = {
    errno.EACCES,
    errno.ENOENT,
    errno.ENOSYS,
    errno.EPERM,
    errno.EXDEV,
}
if hasattr(errno, "EOPNOTSUPP"):
    _UNSUPPORTED_PUBLICATION_ERRNOS.add(errno.EOPNOTSUPP)


class _PublishFailure(RuntimeError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class FilesystemBinaryArtifactPublisher:
    """Guard, stage, verify, and exclusively publish opaque Workbench bytes."""

    def __init__(
        self,
        *,
        chunk_size: int = 1024 * 1024,
        stage_barrier: Callable[[], None] | None = None,
        fault_injector: Callable[[str], None] | None = None,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        self._chunk_size = chunk_size
        self._stage_barrier = stage_barrier
        self._fault_injector = fault_injector

    def guard_source(self, request: WorkbenchSourceGuardRequest) -> GuardedWorkbenchSource:
        try:
            repo_root = _absolute_lexical(request.repo_root)
            specdock_dir = _absolute_lexical(request.specdock_dir)
            source_path = _absolute_lexical(request.source_path, relative_to=repo_root)
            scope_directories = tuple(_absolute_lexical(path) for path in request.scope_directories)
            if request.source_path.suffix != ".md":
                raise _PublishFailure("source_ineligible")
            _require_contained(repo_root, specdock_dir)
            approved_roots = (
                specdock_dir / ".workbench",
                *(scope / ".workbench" for scope in scope_directories),
            )
            matching_roots = [root for root in approved_roots if _is_lexically_contained(root, source_path)]
            if len(matching_roots) != 1:
                raise _PublishFailure("source_ineligible")
            workbench_root = matching_roots[0]
            _require_contained(repo_root, workbench_root)
            _guard_directory_ancestry(repo_root, source_path.parent)
            status = source_path.lstat()
            if not stat.S_ISREG(status.st_mode) or stat.S_ISLNK(status.st_mode):
                raise _PublishFailure("source_ineligible")
            return GuardedWorkbenchSource(
                source_path=source_path,
                workbench_root=workbench_root,
                device=status.st_dev,
                inode=status.st_ino,
                mode=status.st_mode,
            )
        except BinaryArtifactPublishError:
            raise
        except (_PublishFailure, FileNotFoundError, OSError, ValueError):
            raise BinaryArtifactPublishError(
                code="source_ineligible",
                cleanup_state="not_created",
            ) from None

    def publish(self, request: BinaryArtifactPublishRequest) -> BinaryArtifactPublishResult:
        guarded = self.guard_source(request.source)
        destination = _absolute_lexical(request.destination_path)
        repo_root = _absolute_lexical(request.source.repo_root)
        try:
            _require_contained(repo_root, destination)
            _guard_directory_ancestry(repo_root, destination.parent)
        except (_PublishFailure, FileNotFoundError, OSError, ValueError):
            raise BinaryArtifactPublishError(
                code="destination_ineligible",
                cleanup_state="not_created",
            ) from None

        source_fd: int | None = None
        temp_fd: int | None = None
        temp_path: Path | None = None
        try:
            source_fd, initial_status = self._open_guarded_source(guarded)
            try:
                self._inject("temp_create")
                temp_fd, raw_temp_path = tempfile.mkstemp(
                    prefix=".spec-dock-import-",
                    suffix=".tmp",
                    dir=destination.parent,
                )
                temp_path = Path(raw_temp_path)
            except OSError:
                raise _PublishFailure("temp_create_failed") from None

            stream_sha256, stream_count = self._copy_source_to_temp(source_fd, temp_fd)
            try:
                self._inject("file_fsync")
                os.fsync(temp_fd)
            except OSError:
                raise _PublishFailure("file_fsync_failed") from None

            try:
                self._inject("hash")
                staged_sha256, staged_count = self._hash_descriptor(temp_fd)
            except OSError:
                raise _PublishFailure("hash_failed") from None
            if (staged_sha256, staged_count) != (stream_sha256, stream_count):
                raise _PublishFailure("hash_mismatch")

            staged_status = os.fstat(temp_fd)
            if not stat.S_ISREG(staged_status.st_mode):
                raise _PublishFailure("hash_mismatch")
            if (staged_status.st_dev, staged_status.st_ino) == (
                initial_status.st_dev,
                initial_status.st_ino,
            ):
                raise _PublishFailure("source_alias")

            if self._stage_barrier is not None:
                self._stage_barrier()
            source_sha256, source_count = self._verify_source_stability(
                source_fd,
                guarded.source_path,
                initial_status,
            )
            if (source_sha256, source_count) != (stream_sha256, stream_count):
                raise _PublishFailure("source_changed")

            self._publish_no_replace(temp_fd, destination)
            warning_codes: list[BinaryArtifactPublishWarning] = []
            if not self._fsync_directory(destination.parent):
                warning_codes.append("directory_fsync_failed")
            try:
                destination_sha256, destination_count = self._hash_published_destination(destination)
            except _PublishFailure as exc:
                if exc.code != "destination_read_failed":
                    raise
                destination_sha256, destination_count = staged_sha256, staged_count
                warning_codes.append("destination_read_failed")
            else:
                if (destination_sha256, destination_count) != (
                    staged_sha256,
                    staged_count,
                ):
                    warning_codes.append("destination_mismatch")
            cleanup_state = self._cleanup_temp(temp_path, temp_fd)
            if cleanup_state == "removed":
                temp_path = None
            else:
                warning_codes.append("temp_cleanup_retained")
            return BinaryArtifactPublishResult(
                source_path=guarded.source_path,
                destination_path=destination,
                source_sha256=source_sha256,
                stream_sha256=stream_sha256,
                staged_sha256=staged_sha256,
                destination_sha256=destination_sha256,
                source_byte_count=source_count,
                stream_byte_count=stream_count,
                staged_byte_count=staged_count,
                destination_byte_count=destination_count,
                source_inode=initial_status.st_ino,
                staged_inode=staged_status.st_ino,
                cleanup_state=cleanup_state,
                warning_codes=tuple(warning_codes),
            )
        except BinaryArtifactPublishError:
            raise
        except _PublishFailure as exc:
            cleanup_state = self._cleanup_after_failure(temp_path, temp_fd)
            raise BinaryArtifactPublishError(
                code=exc.code,
                cleanup_state=cleanup_state,
            ) from None
        except OSError:
            cleanup_state = self._cleanup_after_failure(temp_path, temp_fd)
            raise BinaryArtifactPublishError(
                code="filesystem_failed",
                cleanup_state=cleanup_state,
            ) from None
        finally:
            if temp_fd is not None:
                os.close(temp_fd)
            if source_fd is not None:
                os.close(source_fd)

    def _open_guarded_source(self, guarded: GuardedWorkbenchSource) -> tuple[int, os.stat_result]:
        flags = os.O_RDONLY
        if hasattr(os, "O_CLOEXEC"):
            flags |= os.O_CLOEXEC
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        source_fd: int | None = None
        try:
            source_fd = os.open(guarded.source_path, flags)
            status = os.fstat(source_fd)
            path_status = guarded.source_path.lstat()
        except OSError:
            if source_fd is not None:
                os.close(source_fd)
            raise _PublishFailure("source_changed") from None
        expected = (guarded.device, guarded.inode, guarded.mode)
        if (
            not stat.S_ISREG(status.st_mode)
            or (
                status.st_dev,
                status.st_ino,
                status.st_mode,
            )
            != expected
            or (
                path_status.st_dev,
                path_status.st_ino,
                path_status.st_mode,
            )
            != expected
        ):
            os.close(source_fd)
            raise _PublishFailure("source_changed")
        return source_fd, status

    def _copy_source_to_temp(self, source_fd: int, temp_fd: int) -> tuple[str, int]:
        digest = hashlib.sha256()
        byte_count = 0
        try:
            self._inject("write")
            while True:
                chunk = os.read(source_fd, self._chunk_size)
                if not chunk:
                    break
                digest.update(chunk)
                byte_count += len(chunk)
                _write_all(temp_fd, chunk)
        except OSError:
            raise _PublishFailure("copy_failed") from None
        return digest.hexdigest(), byte_count

    def _hash_descriptor(self, descriptor: int) -> tuple[str, int]:
        os.lseek(descriptor, 0, os.SEEK_SET)
        digest = hashlib.sha256()
        byte_count = 0
        while True:
            chunk = os.read(descriptor, self._chunk_size)
            if not chunk:
                return digest.hexdigest(), byte_count
            digest.update(chunk)
            byte_count += len(chunk)

    def _verify_source_stability(
        self,
        source_fd: int,
        source_path: Path,
        initial_status: os.stat_result,
    ) -> tuple[str, int]:
        try:
            source_sha256, source_count = self._hash_descriptor(source_fd)
            descriptor_status = os.fstat(source_fd)
            path_status = source_path.lstat()
        except OSError:
            raise _PublishFailure("source_changed") from None
        initial_identity = (initial_status.st_dev, initial_status.st_ino, initial_status.st_mode)
        descriptor_identity = (
            descriptor_status.st_dev,
            descriptor_status.st_ino,
            descriptor_status.st_mode,
        )
        path_identity = (path_status.st_dev, path_status.st_ino, path_status.st_mode)
        initial_metadata = (
            initial_status.st_size,
            initial_status.st_mtime_ns,
            initial_status.st_ctime_ns,
        )
        descriptor_metadata = (
            descriptor_status.st_size,
            descriptor_status.st_mtime_ns,
            descriptor_status.st_ctime_ns,
        )
        if (
            descriptor_identity != initial_identity
            or path_identity != initial_identity
            or descriptor_metadata != initial_metadata
            or not stat.S_ISREG(path_status.st_mode)
        ):
            raise _PublishFailure("source_changed")
        return source_sha256, source_count

    def _publish_no_replace(self, temp_fd: int, destination: Path) -> None:
        self._inject("before_publication")
        try:
            self._inject("publication_unsupported")
        except OSError:
            raise _PublishFailure("publication_unsupported") from None
        try:
            if sys.platform == "darwin":
                _clone_macos_descriptor(temp_fd, destination)
            elif sys.platform.startswith("linux"):
                os.link(
                    f"/proc/self/fd/{temp_fd}",
                    destination,
                    follow_symlinks=True,
                )
            else:
                raise _PublishFailure("publication_unsupported")
        except FileExistsError:
            raise _PublishFailure("destination_exists") from None
        except (NotImplementedError, TypeError):
            raise _PublishFailure("publication_unsupported") from None
        except OSError as exc:
            if exc.errno in _UNSUPPORTED_PUBLICATION_ERRNOS:
                raise _PublishFailure("publication_unsupported") from None
            raise _PublishFailure("publication_failed") from None

    def _hash_published_destination(self, destination: Path) -> tuple[str, int]:
        flags = os.O_RDONLY
        if hasattr(os, "O_CLOEXEC"):
            flags |= os.O_CLOEXEC
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor: int | None = None
        try:
            self._inject("post_confirmation")
            descriptor = os.open(destination, flags)
            return self._hash_descriptor(descriptor)
        except OSError:
            raise _PublishFailure("destination_read_failed") from None
        finally:
            if descriptor is not None:
                os.close(descriptor)

    def _fsync_directory(self, directory: Path) -> bool:
        flags = os.O_RDONLY
        if hasattr(os, "O_CLOEXEC"):
            flags |= os.O_CLOEXEC
        if hasattr(os, "O_DIRECTORY"):
            flags |= os.O_DIRECTORY
        descriptor: int | None = None
        try:
            self._inject("directory_fsync")
            descriptor = os.open(directory, flags)
            os.fsync(descriptor)
        except OSError:
            return False
        finally:
            if descriptor is not None:
                os.close(descriptor)
        return True

    def _cleanup_after_failure(
        self,
        temp_path: Path | None,
        temp_fd: int | None,
    ) -> BinaryArtifactCleanupState:
        if temp_path is None:
            return "not_created"
        return self._cleanup_temp(temp_path, temp_fd)

    def _cleanup_temp(
        self,
        temp_path: Path,
        temp_fd: int | None,
    ) -> BinaryArtifactCleanupState:
        if temp_fd is None:
            return "retained"
        try:
            path_status = temp_path.lstat()
            descriptor_status = os.fstat(temp_fd)
        except FileNotFoundError:
            return "removed"
        except OSError:
            return "retained"
        if (path_status.st_dev, path_status.st_ino) != (
            descriptor_status.st_dev,
            descriptor_status.st_ino,
        ):
            return "retained"
        try:
            self._inject("cleanup")
            temp_path.unlink()
        except OSError:
            return "retained"
        return "removed"

    def _inject(self, point: str) -> None:
        if self._fault_injector is not None:
            self._fault_injector(point)


def _absolute_lexical(path: Path, *, relative_to: Path | None = None) -> Path:
    candidate = path
    if not candidate.is_absolute():
        if relative_to is None:
            raise ValueError("relative path has no base")
        candidate = relative_to / candidate
    return Path(os.path.normpath(candidate))


def _is_lexically_contained(root: Path, path: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _require_contained(root: Path, path: Path) -> None:
    if not root.is_absolute() or not path.is_absolute() or not _is_lexically_contained(root, path):
        raise _PublishFailure("source_ineligible")


def _guard_directory_ancestry(root: Path, endpoint: Path) -> None:
    _require_contained(root, endpoint)
    relative = endpoint.relative_to(root)
    components = (
        root,
        *(root.joinpath(*relative.parts[:index]) for index in range(1, len(relative.parts) + 1)),
    )
    for component in components:
        status = component.lstat()
        if stat.S_ISLNK(status.st_mode) or not stat.S_ISDIR(status.st_mode):
            raise _PublishFailure("source_ineligible")


def _write_all(descriptor: int, body: bytes) -> None:
    view = memoryview(body)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            raise OSError("short binary write")
        view = view[written:]


def _clone_macos_descriptor(source_fd: int, destination: Path) -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    try:
        fclonefileat = libc.fclonefileat
    except AttributeError:
        raise OSError(errno.ENOSYS, "fclonefileat unavailable") from None
    fclonefileat.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32]
    fclonefileat.restype = ctypes.c_int
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    directory_fd = os.open(destination.parent, flags)
    try:
        if fclonefileat(source_fd, directory_fd, os.fsencode(destination.name), 0) != 0:
            error_number = ctypes.get_errno()
            raise OSError(error_number, os.strerror(error_number))
    finally:
        os.close(directory_fd)
