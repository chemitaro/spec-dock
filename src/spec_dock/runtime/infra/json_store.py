from __future__ import annotations

import ctypes
import errno
import json
import os
import stat
import sys
from typing import TYPE_CHECKING, Any
import uuid

if TYPE_CHECKING:
    from pathlib import Path


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON: {path}: {e}") from e
    except UnicodeDecodeError as e:
        raise RuntimeError(f"Failed to read: {path}: {e}") from e
    except OSError as e:
        raise RuntimeError(f"Failed to read: {path}: {e}") from e


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_guarded_json(path: Path) -> tuple[Any, tuple[int, int]] | None:
    """Read a single-link regular JSON file through a verified parent descriptor."""
    if not path.is_absolute():
        raise ValueError("JSON source must be absolute")
    if not path.parent.exists():
        return None
    directory_fd = _open_directory_without_links(path.parent)
    try:
        return read_guarded_json_at(directory_fd, path.name)
    finally:
        os.close(directory_fd)


def read_guarded_json_at(directory_fd: int, name: str) -> tuple[Any, tuple[int, int]] | None:
    if not name or name in (".", "..") or "/" in name or "\\" in name:
        raise ValueError("JSON name must be a single path component")
    try:
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory_fd)
    except FileNotFoundError:
        return None
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise ValueError("JSON source must not be a symlink") from exc
        raise
    with os.fdopen(fd, "rb") as stream:
        metadata = os.fstat(stream.fileno())
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise ValueError("JSON source must be a single-link regular file")
        payload = json.load(stream)
        return payload, (metadata.st_dev, metadata.st_ino)


def open_guarded_directory(path: Path) -> int:
    if not path.is_absolute():
        raise ValueError("guarded directory must be absolute")
    return _open_directory_without_links(path)


def atomic_write_json(path: Path, data: Any, *, expected_identity: tuple[int, int] | None = None) -> None:
    """Publish JSON with no-replace or a recoverable exchange under the caller's writer lock.

    Identity CAS is a cooperative-writer contract. An external directory writer can
    race between observations; an ambiguous exchange retains both files for recovery.
    """
    directory = path.parent
    if not directory.is_absolute():
        raise ValueError("JSON destination must be absolute")
    if any(parent.is_symlink() for parent in (directory, *directory.parents)):
        raise ValueError("JSON destination ancestor must not be a symlink")
    directory.mkdir(parents=True, exist_ok=True)
    directory_fd = _open_directory_without_links(directory)
    transaction_name = ".specdock-json-transactions"
    try:
        try:
            os.mkdir(transaction_name, mode=0o700, dir_fd=directory_fd)
        except FileExistsError:
            pass
        else:
            os.fsync(directory_fd)
        transaction_fd = os.open(transaction_name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory_fd)
    except BaseException:
        os.close(directory_fd)
        raise
    nonce = uuid.uuid4().hex
    staged_name = f"{path.name}.{nonce}.stage"
    intent_name = f"{path.name}.{nonce}.intent"
    done_name = f"{path.name}.{nonce}.done"
    payload = (json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
    stage_fd: int | None = None
    expected_fd: int | None = None
    try:
        entries = set(os.listdir(transaction_fd))  # noqa: PTH208 - inspect the verified directory descriptor
        for name in entries:
            if name.startswith(f"{path.name}.") and name.endswith(".intent"):
                done = name[:-7] + ".done"
                if done not in entries:
                    raise RuntimeError("JSON publish recovery is required")
                marker = read_guarded_json_at(transaction_fd, done)
                if marker is None or marker[0] not in (
                    {"status": "published"},
                    {"status": "aborted"},
                    {"status": "conflict"},
                ):
                    raise RuntimeError("JSON publish recovery is required")
        before = _target_identity(directory_fd, path.name)
        if expected_identity is None and before is not None:
            raise FileExistsError(path)
        if expected_identity is not None and before != expected_identity:
            raise ValueError("JSON destination identity changed")
        stage_fd = os.open(
            staged_name,
            os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
            dir_fd=transaction_fd,
        )
        stage_stat = os.fstat(stage_fd)
        stage_identity = (stage_stat.st_dev, stage_stat.st_ino)
        with os.fdopen(os.dup(stage_fd), "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if expected_identity is None:
            _rename_no_replace_at(transaction_fd, staged_name, directory_fd, path.name)
            os.fsync(directory_fd)
            os.fsync(transaction_fd)
        else:
            expected_fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory_fd)
            expected_stat = os.fstat(expected_fd)
            if not stat.S_ISREG(expected_stat.st_mode) or expected_stat.st_nlink != 1:
                raise ValueError("JSON destination must be a single-link regular file")
            if (expected_stat.st_dev, expected_stat.st_ino) != expected_identity:
                raise ValueError("JSON destination identity changed")
            if _target_identity(directory_fd, path.name) != expected_identity:
                raise ValueError("JSON destination identity changed")
            os.fchmod(stage_fd, stat.S_IMODE(expected_stat.st_mode))
            os.fsync(stage_fd)
            _write_transaction_record(
                transaction_fd,
                intent_name,
                {
                    "version": 1,
                    "target": path.name,
                    "stage": staged_name,
                    "expected": list(expected_identity),
                    "new": list(stage_identity),
                },
            )
            try:
                _rename_exchange_at(transaction_fd, staged_name, directory_fd, path.name)
            except OSError:
                if _exchange_topology(transaction_fd, staged_name, directory_fd, path.name) == (
                    expected_identity,
                    stage_identity,
                ):
                    _write_transaction_record(transaction_fd, done_name, {"status": "aborted"})
                raise
            os.fsync(directory_fd)
            os.fsync(transaction_fd)
            topology = _exchange_topology(transaction_fd, staged_name, directory_fd, path.name)
            if topology == (stage_identity, expected_identity):
                _write_transaction_record(transaction_fd, done_name, {"status": "published"})
            elif topology[0] == stage_identity and topology[1] is not None:
                competing_identity = topology[1]
                _rename_exchange_at(transaction_fd, staged_name, directory_fd, path.name)
                os.fsync(directory_fd)
                os.fsync(transaction_fd)
                if _exchange_topology(transaction_fd, staged_name, directory_fd, path.name) != (
                    competing_identity,
                    stage_identity,
                ):
                    raise RuntimeError("JSON publish recovery is required")
                _write_transaction_record(transaction_fd, done_name, {"status": "conflict"})
                raise ValueError("JSON destination identity changed")
            else:
                raise RuntimeError("JSON publish recovery is required")
    finally:
        if stage_fd is not None:
            os.close(stage_fd)
        if expected_fd is not None:
            os.close(expected_fd)
        os.close(transaction_fd)
        os.close(directory_fd)


def _rename_with_flag(source_fd: int, source: str, target_fd: int, target: str, *, exchange: bool) -> None:
    library = ctypes.CDLL(None, use_errno=True)
    if sys.platform.startswith("linux"):
        function = getattr(library, "renameat2", None)
        flag = 0x2 if exchange else 0x1
    elif sys.platform == "darwin":
        function = getattr(library, "renameatx_np", None)
        flag = 0x2 if exchange else 0x4
    else:
        raise NotImplementedError("safe JSON rename is unavailable")
    if function is None:
        raise NotImplementedError("safe JSON rename is unavailable")
    function.argtypes = (ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint)
    function.restype = ctypes.c_int
    if function(source_fd, os.fsencode(source), target_fd, os.fsencode(target), flag) == 0:
        return
    error = ctypes.get_errno()
    if not exchange and error in (errno.EEXIST, errno.ENOTEMPTY):
        raise FileExistsError(error, os.strerror(error), target)
    raise OSError(error, os.strerror(error), target)


def _rename_exchange_at(source_fd: int, source: str, target_fd: int, target: str) -> None:
    _rename_with_flag(source_fd, source, target_fd, target, exchange=True)


def _rename_no_replace_at(source_fd: int, source: str, target_fd: int, target: str) -> None:
    _rename_with_flag(source_fd, source, target_fd, target, exchange=False)


def _exchange_topology(
    source_fd: int, source: str, target_fd: int, target: str
) -> tuple[tuple[int, int] | None, tuple[int, int] | None]:
    return _target_identity(target_fd, target), _target_identity(source_fd, source)


def _write_transaction_record(directory_fd: int, name: str, payload: dict[str, object]) -> None:
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=directory_fd)
    with os.fdopen(fd, "wb") as stream:
        stream.write((json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode())
        stream.flush()
        os.fsync(stream.fileno())
    os.fsync(directory_fd)


def reconcile_atomic_json(path: Path) -> tuple[str, ...]:
    """Classify interrupted publishes after the owning operation has rechecked its lock.

    This never repeats an exchange or deletes a displaced inode. Ambiguous topology
    remains pending for an operator to inspect.
    """
    if not path.is_absolute() or any(parent.is_symlink() for parent in (path.parent, *path.parent.parents)):
        raise ValueError("JSON recovery path must be absolute and free of symlink ancestors")
    directory_fd = _open_directory_without_links(path.parent)
    try:
        transaction_fd = os.open(
            ".specdock-json-transactions", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory_fd
        )
        try:
            entries = set(os.listdir(transaction_fd))  # noqa: PTH208 - inspect the verified directory descriptor
            outcomes: list[str] = []
            for name in sorted(entries):
                if not (name.startswith(f"{path.name}.") and name.endswith(".intent")):
                    continue
                done_name = name[:-7] + ".done"
                if done_name in entries:
                    continue
                loaded = read_guarded_json_at(transaction_fd, name)
                if loaded is None or not isinstance(loaded[0], dict):
                    raise RuntimeError("JSON publish record is invalid")
                record = loaded[0]
                stage_name = record.get("stage")
                expected = record.get("expected")
                new = record.get("new")
                if (
                    record.get("version") != 1
                    or record.get("target") != path.name
                    or stage_name != name[:-7] + ".stage"
                    or not isinstance(expected, list)
                    or not isinstance(new, list)
                    or len(expected) != 2
                    or len(new) != 2
                    or any(not isinstance(item, int) or isinstance(item, bool) for item in (*expected, *new))
                ):
                    raise RuntimeError("JSON publish record is invalid")
                expected_identity = (expected[0], expected[1])
                new_identity = (new[0], new[1])
                assert isinstance(stage_name, str)
                topology = _exchange_topology(transaction_fd, stage_name, directory_fd, path.name)
                if topology == (expected_identity, new_identity):
                    status = "aborted"
                elif topology == (new_identity, expected_identity):
                    status = "published"
                elif topology[1] == new_identity and topology[0] is not None:
                    status = "conflict"
                else:
                    raise RuntimeError("JSON publish recovery is required")
                os.fsync(directory_fd)
                os.fsync(transaction_fd)
                _write_transaction_record(transaction_fd, done_name, {"status": status})
                outcomes.append(status)
            return tuple(outcomes)
        finally:
            os.close(transaction_fd)
    finally:
        os.close(directory_fd)


def _open_directory_without_links(directory: Path) -> int:
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in directory.parts[1:]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def _target_identity(directory_fd: int, name: str) -> tuple[int, int] | None:
    try:
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory_fd)
    except FileNotFoundError:
        return None
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise ValueError("JSON destination must not be a symlink") from exc
        raise
    try:
        metadata = os.fstat(fd)
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError("JSON destination must be a regular file")
        if metadata.st_nlink != 1:
            raise ValueError("JSON destination has multiple hardlinks")
        return metadata.st_dev, metadata.st_ino
    finally:
        os.close(fd)
