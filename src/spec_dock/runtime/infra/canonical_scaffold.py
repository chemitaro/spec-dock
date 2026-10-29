"""Catalog file operations for canonical Scope writes: template copies and directory moves without replacement.

Paths are real catalog paths (never through a checkout's spec-dock/initiatives link); every component is opened
without following links, as the legacy publication adapters do.
"""

from __future__ import annotations

import os
import stat
from typing import TYPE_CHECKING

from spec_dock.runtime.domain.canonical_scaffold import strip_structure_front_matter
from spec_dock.runtime.infra.direct_json import _create_guarded_directory
from spec_dock.runtime.infra.json_store import _rename_no_replace_at, open_guarded_directory
from spec_dock.runtime.infra.template_scaffolder import (
    _open_parent_at,
    _preflight_no_collision_at,
    _template_files,
    _write_all,
    render_text,
)

if TYPE_CHECKING:
    from pathlib import Path


def copy_scope_template_at(src_dir: Path, dest_dir: Path, dest_fd: int, replacements: dict[str, str]) -> list[Path]:
    """Copy a Scope template through a held directory descriptor, rendered and without title/parent lines."""
    if not src_dir.is_dir():
        raise RuntimeError(f"Missing template directory: {src_dir}")
    template_files = _template_files(src_dir)
    rel_files = [path.relative_to(src_dir) for path in template_files]
    _preflight_no_collision_at(dest_fd, rel_files, dest_dir)
    created: list[Path] = []
    for source, relative in zip(template_files, rel_files, strict=True):
        source_bytes = source.read_bytes()
        source_mode = stat.S_IMODE(source.stat().st_mode)
        try:
            text = source_bytes.decode("utf-8")
        except UnicodeDecodeError:
            payload, mode = source_bytes, source_mode
        else:
            payload = strip_structure_front_matter(render_text(text, replacements)).encode("utf-8")
            mode = source_mode if payload == source_bytes else 0o666
        parent_fd = _open_parent_at(dest_fd, relative.parts[:-1], create=True)
        assert parent_fd is not None
        try:
            target_fd = os.open(relative.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode, dir_fd=parent_fd)
            try:
                _write_all(target_fd, payload)
            finally:
                os.close(target_fd)
        finally:
            os.close(parent_fd)
        created.append(dest_dir / relative)
    return created


def move_directory(source: Path, target: Path) -> None:
    """Rename `source` to `target` without replacing anything; missing parents of `target` are created."""
    source_fd = open_guarded_directory(source.parent)
    try:
        observed = os.stat(source.name, dir_fd=source_fd, follow_symlinks=False)
        if not stat.S_ISDIR(observed.st_mode):
            raise ValueError(f"{source} is not a directory")
        target_fd = _create_guarded_directory(target.parent)
        try:
            _rename_no_replace_at(source_fd, source.name, target_fd, target.name)
            os.fsync(target_fd)
        finally:
            os.close(target_fd)
        os.fsync(source_fd)
    finally:
        os.close(source_fd)
