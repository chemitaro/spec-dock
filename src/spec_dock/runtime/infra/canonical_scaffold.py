"""Catalog file operations for canonical Scope writes: template copies and the number buckets.

Paths are real catalog paths (never through a checkout's spec-dock/initiatives link); every component is opened
without following links, as the legacy publication adapters do.
"""

from __future__ import annotations

import errno
import os
import stat
from typing import TYPE_CHECKING

from spec_dock.runtime.domain.canonical_scaffold import rebase_spec_dock_links, strip_structure_front_matter
from spec_dock.runtime.infra.json_store import open_guarded_directory
from spec_dock.runtime.infra.template_scaffolder import (
    _open_parent_at,
    _preflight_no_collision_at,
    _template_files,
    _write_all,
    render_text,
)

if TYPE_CHECKING:
    from pathlib import Path


class BucketOccupied(ValueError):
    """The bucket's place holds a symlink or a file, which the catalog never treats as a bucket."""

    def __init__(self, path: Path) -> None:
        super().__init__(f"{path} is not a real directory; a number bucket must be one")
        self.path = path


def copy_scope_template_at(src_dir: Path, dest_dir: Path, dest_fd: int, replacements: dict[str, str]) -> list[Path]:
    """Copy a Scope template through a held directory descriptor, rendered, without title/parent lines and
    with its spec-dock/docs links at the flat Scope depth."""
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
            rendered = rebase_spec_dock_links(strip_structure_front_matter(render_text(text, replacements)))
            payload = rendered.encode("utf-8")
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


def prepare_bucket(catalog: Path, bucket: str) -> bool:
    """Make sure `<catalog>/<bucket>` is a real directory; True when it was created now."""
    catalog_fd = open_guarded_directory(catalog)
    try:
        try:
            os.mkdir(bucket, dir_fd=catalog_fd)
        except FileExistsError:
            observed = os.stat(bucket, dir_fd=catalog_fd, follow_symlinks=False)
            if not stat.S_ISDIR(observed.st_mode):
                raise BucketOccupied(catalog / bucket) from None
            return False
        os.fsync(catalog_fd)
        return True
    finally:
        os.close(catalog_fd)


def remove_empty_bucket(catalog: Path, bucket: str) -> bool:
    """Remove `<catalog>/<bucket>` when it is an empty real directory; True when it was removed now."""
    catalog_fd = open_guarded_directory(catalog)
    try:
        try:
            observed = os.stat(bucket, dir_fd=catalog_fd, follow_symlinks=False)
        except FileNotFoundError:
            return False
        if not stat.S_ISDIR(observed.st_mode):
            return False
        try:
            os.rmdir(bucket, dir_fd=catalog_fd)
        except OSError as error:
            if error.errno in (errno.ENOTEMPTY, errno.EEXIST):
                return False
            raise
        os.fsync(catalog_fd)
        return True
    finally:
        os.close(catalog_fd)
