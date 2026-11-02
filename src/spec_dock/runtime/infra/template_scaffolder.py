from __future__ import annotations

import contextlib
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def render_text(text: str, replacements: dict[str, str]) -> str:
    rendered = text
    for key, value in replacements.items():
        rendered = rendered.replace(key, value)
    return rendered


def _template_files(src_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(src_dir.rglob("*"), key=lambda p: p.as_posix()):
        if path.is_file():
            files.append(path)
    return files


def _open_directory_at(parent_fd: int, name: str, *, create: bool) -> int:
    if create:
        with contextlib.suppress(FileExistsError):
            os.mkdir(name, dir_fd=parent_fd)
    return os.open(
        name,
        os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0),
        dir_fd=parent_fd,
    )


def _open_parent_at(root_fd: int, parts: tuple[str, ...], *, create: bool) -> int | None:
    current_fd = os.dup(root_fd)
    try:
        for part in parts:
            try:
                next_fd = _open_directory_at(current_fd, part, create=create)
            except FileNotFoundError:
                if create:
                    raise
                os.close(current_fd)
                return None
            os.close(current_fd)
            current_fd = next_fd
        return current_fd
    except Exception:
        with contextlib.suppress(OSError):
            os.close(current_fd)
        raise


def _write_all(descriptor: int, payload: bytes) -> None:
    offset = 0
    while offset < len(payload):
        written = os.write(descriptor, payload[offset:])
        if written == 0:
            raise OSError("short scaffold write")
        offset += written


def _preflight_no_collision_at(dest_dir_fd: int, rel_files: list[Path], dest_dir: Path) -> None:
    for rel_path in rel_files:
        parent_fd = _open_parent_at(dest_dir_fd, rel_path.parts[:-1], create=False)
        if parent_fd is None:
            continue
        try:
            try:
                os.stat(rel_path.name, dir_fd=parent_fd, follow_symlinks=False)
            except FileNotFoundError:
                continue
            raise RuntimeError(f"Destination already exists: {dest_dir / rel_path}")
        finally:
            os.close(parent_fd)
