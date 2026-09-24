from __future__ import annotations

import errno
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
    """Create or CAS-replace JSON in a descriptor-verified directory."""
    directory = path.parent
    if not directory.is_absolute():
        raise ValueError("JSON destination must be absolute")
    if any(parent.is_symlink() for parent in (directory, *directory.parents)):
        raise ValueError("JSON destination ancestor must not be a symlink")
    directory.mkdir(parents=True, exist_ok=True)
    directory_fd = _open_directory_without_links(directory)
    staged_name = f".{path.name}-{uuid.uuid4().hex}.tmp"
    payload = (json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
    stage_identity: tuple[int, int] | None = None
    try:
        before = _target_identity(directory_fd, path.name)
        if expected_identity is None and before is not None:
            raise FileExistsError(path)
        if expected_identity is not None and before != expected_identity:
            raise ValueError("JSON destination identity changed")
        fd = os.open(
            staged_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
            dir_fd=directory_fd,
        )
        with os.fdopen(fd, "wb") as stream:
            stage_stat = os.fstat(stream.fileno())
            stage_identity = (stage_stat.st_dev, stage_stat.st_ino)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if expected_identity is None:
            os.link(staged_name, path.name, src_dir_fd=directory_fd, dst_dir_fd=directory_fd, follow_symlinks=False)
        else:
            if _target_identity(directory_fd, path.name) != expected_identity:
                raise ValueError("JSON destination identity changed")
            os.replace(staged_name, path.name, src_dir_fd=directory_fd, dst_dir_fd=directory_fd)
        os.fsync(directory_fd)
    finally:
        if stage_identity is not None:
            try:
                candidate = os.stat(staged_name, dir_fd=directory_fd, follow_symlinks=False)
            except FileNotFoundError:
                pass
            else:
                if (candidate.st_dev, candidate.st_ino) == stage_identity:
                    os.unlink(staged_name, dir_fd=directory_fd)
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
