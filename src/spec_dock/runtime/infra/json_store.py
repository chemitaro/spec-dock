from __future__ import annotations

import ctypes
import errno
import json
import os
import stat
import sys
from typing import TYPE_CHECKING, Any

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
    """Read a single-link regular JSON file through a verified parent handle."""
    loaded = read_guarded_json_bytes(path)
    return (loaded[0], loaded[2]) if loaded is not None else None


def read_guarded_json_bytes(path: Path) -> tuple[Any, bytes, tuple[int, int]] | None:
    """Capture exact input bytes and identity without JSON reserialization."""
    if not path.is_absolute():
        raise ValueError("JSON source must be absolute")
    if os.name == "nt":
        from spec_dock.runtime.infra.windows_handles import WindowsDirectory

        try:
            with WindowsDirectory(path.parent) as directory:
                captured = directory.read_file_bytes(path.name)
        except FileNotFoundError:
            return None
        if captured is None:
            return None
        payload, identity = captured
        return json.loads(payload), payload, identity
    if not path.parent.exists():
        return None
    directory_fd = _open_directory_without_links(path.parent)
    try:
        return read_guarded_json_bytes_at(directory_fd, path.name)
    finally:
        os.close(directory_fd)


def read_guarded_json_at(directory_fd: int, name: str) -> tuple[Any, tuple[int, int]] | None:
    loaded = read_guarded_json_bytes_at(directory_fd, name)
    return (loaded[0], loaded[2]) if loaded is not None else None


def read_guarded_json_bytes_at(directory_fd: int, name: str) -> tuple[Any, bytes, tuple[int, int]] | None:
    if not name or name in (".", "..") or "/" in name or "\\" in name:
        raise ValueError("JSON name must be a single path component")
    try:
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory_fd)
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
        payload = stream.read()
        return json.loads(payload), payload, (metadata.st_dev, metadata.st_ino)


def open_guarded_directory(path: Path) -> int:
    if not path.is_absolute():
        raise ValueError("guarded directory must be absolute")
    return _open_directory_without_links(path)


def _rename_no_replace_at(source_fd: int, source: str, target_fd: int, target: str) -> None:
    library = ctypes.CDLL(None, use_errno=True)
    if sys.platform.startswith("linux"):
        function = getattr(library, "renameat2", None)
        flag = 0x1
    elif sys.platform == "darwin":
        function = getattr(library, "renameatx_np", None)
        flag = 0x4
    else:
        raise NotImplementedError("safe JSON rename is unavailable")
    if function is None:
        raise NotImplementedError("safe JSON rename is unavailable")
    function.argtypes = (ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint)
    function.restype = ctypes.c_int
    if function(source_fd, os.fsencode(source), target_fd, os.fsencode(target), flag) == 0:
        return
    error = ctypes.get_errno()
    if error in (errno.EEXIST, errno.ENOTEMPTY):
        raise FileExistsError(error, os.strerror(error), target)
    raise OSError(error, os.strerror(error), target)


def _open_directory_without_links(directory: Path) -> int:
    if os.name != "posix":
        raise NotImplementedError("guarded directory adapter is not connected for this platform")
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
