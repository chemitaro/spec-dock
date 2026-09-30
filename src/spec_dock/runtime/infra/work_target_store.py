"""The worktree-local direct-selection persistence boundary."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import os
import re
import secrets
import stat
from typing import TYPE_CHECKING, Literal

from spec_dock.runtime.domain.work_target import WorkTarget
from spec_dock.runtime.infra.json_store import _rename_no_replace_at, open_guarded_directory

if TYPE_CHECKING:
    from pathlib import Path
    from types import TracebackType

    from spec_dock.runtime.infra.identity import DirectoryIdentity

_NAME = re.compile(r"target-([0-9a-f]{32})\.json\Z")
_MAX_BYTES = 65536


class SelectionPublicationUnknown(RuntimeError):
    """Rename succeeded, but durable publication or readback could not be confirmed."""

    def __init__(self, token: str, cause: Exception) -> None:
        self.token = token
        super().__init__(str(cause))


class SelectionRemovalUnknown(RuntimeError):
    """Unlink succeeded, but durable removal could not be confirmed."""


@dataclass(frozen=True)
class SelectionHandle:
    basename: str
    directory_identity: tuple[int, int]
    file_identity: tuple[int, int]
    content_hash: str

    @property
    def token(self) -> str:
        return self.basename[7:-5]


@dataclass(frozen=True)
class StoredSelection:
    status: Literal["empty", "selected", "invalid", "unavailable"]
    record: WorkTarget | None = None
    handle: SelectionHandle | None = None
    reason: str | None = None
    observed_handles: tuple[SelectionHandle, ...] = ()


class WorkTargetStore:
    def __init__(self, root: Path, *, root_handle: DirectoryIdentity | None = None) -> None:
        self.root = root
        self._root_handle = root_handle
        self.path = root / "spec-dock/.agent/work-target"
        self._directory_fd: int | None = None

    def __enter__(self) -> WorkTargetStore:
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None
    ) -> None:
        if self._directory_fd is not None:
            os.close(self._directory_fd)
            self._directory_fd = None

    def _open(self, *, create: bool = False) -> int:
        if os.name == "nt":
            raise NotImplementedError("Windows selection adapter is not connected yet")
        if self._directory_fd is None:
            if self._root_handle is not None:
                self._root_handle.verify()
                if self._root_handle.descriptor is None:
                    raise ValueError("held root descriptor is not available")
                parent = os.open(
                    "spec-dock",
                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                    dir_fd=self._root_handle.descriptor,
                )
            else:
                parent = open_guarded_directory(self.root / "spec-dock")
            try:
                for name in (".agent", "work-target"):
                    if create:
                        try:
                            os.mkdir(name, mode=0o700, dir_fd=parent)
                        except FileExistsError:
                            pass
                        else:
                            os.fsync(parent)
                    child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
                    os.close(parent)
                    parent = child
                self._directory_fd = parent
                parent = -1
            finally:
                if parent != -1:
                    os.close(parent)
        return self._directory_fd

    def _verify_directory(self, directory_fd: int) -> None:
        if self._root_handle is not None:
            self._root_handle.verify()
        fresh = open_guarded_directory(self.path)
        try:
            if _identity(os.fstat(fresh)) != _identity(os.fstat(directory_fd)):
                raise ValueError("work target directory identity changed")
        finally:
            os.close(fresh)

    def _read_file(self, directory_fd: int, name: str) -> tuple[bytes, SelectionHandle]:
        descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory_fd)
        with os.fdopen(descriptor, "rb") as stream:
            observed = os.fstat(stream.fileno())
            if not stat.S_ISREG(observed.st_mode) or observed.st_nlink != 1:
                raise ValueError("work target must be a single-link regular file")
            payload = stream.read(_MAX_BYTES + 1)
            if len(payload) > _MAX_BYTES:
                raise ValueError("work target is too large")
        return payload, SelectionHandle(
            name, _identity(os.fstat(directory_fd)), _identity(observed), hashlib.sha256(payload).hexdigest()
        )

    def read(self) -> StoredSelection:
        try:
            directory_fd = self._open()
        except FileNotFoundError:
            return StoredSelection("empty")
        except (OSError, ValueError, NotImplementedError) as error:
            return StoredSelection("unavailable", reason=str(error))
        handles: list[SelectionHandle] = []
        records: list[WorkTarget] = []
        problems: list[str] = []
        try:
            self._verify_directory(directory_fd)
            entries = os.listdir(directory_fd)  # noqa: PTH208 - owned descriptor, not a redirected path
            for name in entries:
                if not _NAME.fullmatch(name):
                    problems.append(f"unrecognized work target entry: {name}")
                    continue
                try:
                    payload, handle = self._read_file(directory_fd, name)
                    handles.append(handle)
                    records.append(WorkTarget.from_payload(json.loads(payload)))
                except (ValueError, OSError) as error:
                    problems.append(str(error))
            if problems or len(records) > 1:
                return StoredSelection(
                    "invalid", reason="; ".join(problems) or "multiple work targets", observed_handles=tuple(handles)
                )
            if not records:
                return StoredSelection("empty")
            return StoredSelection("selected", records[0], handles[0], observed_handles=tuple(handles))
        except (OSError, ValueError) as error:
            return StoredSelection("unavailable", reason=str(error))

    def publish(self, record: WorkTarget, *, token: str | None = None) -> SelectionHandle:
        token = secrets.token_hex(16) if token is None else token
        if not _NAME.fullmatch(f"target-{token}.json"):
            raise ValueError("invalid publication token")
        if self._root_handle is not None and self._root_handle.identity != record.worktree_identity:
            raise ValueError("work target root physical identity mismatch")
        directory_fd = self._open(create=True)
        self._verify_directory(directory_fd)
        if self.read().status != "empty":
            raise FileExistsError("work target directory is not empty")
        stage = f".stage-{token}"
        name = f"target-{token}.json"
        payload = (json.dumps(asdict(record), ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
        descriptor = os.open(stage, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=directory_fd)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        self._verify_directory(directory_fd)
        _rename_no_replace_at(directory_fd, stage, directory_fd, name)
        try:
            os.fsync(directory_fd)
            self._verify_directory(directory_fd)
            observed_payload, handle = self._read_file(directory_fd, name)
            if observed_payload != payload:
                raise ValueError("published work target bytes changed")
            selection = self.read()
            if selection.status != "selected" or selection.handle != handle or selection.record != record:
                raise ValueError("published work target is not the sole valid selection")
            self._verify_directory(directory_fd)
        except (OSError, ValueError) as error:
            raise SelectionPublicationUnknown(token, error) from error
        return handle

    def remove_observed(self, handle: SelectionHandle) -> Literal["removed", "already_absent", "conflict"]:
        if not _NAME.fullmatch(handle.basename):
            raise ValueError("invalid observed basename")
        try:
            directory_fd = self._open()
        except FileNotFoundError:
            return "already_absent"
        self._verify_directory(directory_fd)
        if _identity(os.fstat(directory_fd)) != handle.directory_identity:
            return "conflict"
        try:
            _, current = self._read_file(directory_fd, handle.basename)
        except FileNotFoundError:
            return "already_absent"
        if current != handle:
            return "conflict"
        try:
            os.unlink(handle.basename, dir_fd=directory_fd)
        except FileNotFoundError:
            return "already_absent"
        try:
            os.fsync(directory_fd)
        except OSError as error:
            raise SelectionRemovalUnknown(str(error)) from error
        return "removed"


def _identity(value: os.stat_result) -> tuple[int, int]:
    return value.st_dev, value.st_ino
