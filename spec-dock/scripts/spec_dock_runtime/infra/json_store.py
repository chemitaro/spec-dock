from __future__ import annotations

import json
import os
import stat
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


def atomic_write_json(path: Path, data: Any, *, expected_identity: tuple[int, int] | None = None) -> None:
    """Stage beside the destination, then publish and sync its directory."""
    directory = path.parent
    if any(parent.is_symlink() for parent in (directory, *directory.parents)):
        raise ValueError("JSON destination ancestor must not be a symlink")
    directory.mkdir(parents=True, exist_ok=True)
    if directory.is_symlink() or path.is_symlink():
        raise ValueError("JSON destination must not be a symlink")
    if expected_identity is not None:
        before = path.lstat()
        if not stat.S_ISREG(before.st_mode) or (before.st_dev, before.st_ino) != expected_identity:
            raise ValueError("JSON destination identity changed")
    staged = directory / f".{path.name}-{uuid.uuid4().hex}.tmp"
    payload = (json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
    fd = os.open(staged, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if expected_identity is not None:
            current = path.lstat()
            if (current.st_dev, current.st_ino) != expected_identity:
                raise ValueError("JSON destination identity changed")
        staged.replace(path)
        directory_fd = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        staged.unlink(missing_ok=True)
