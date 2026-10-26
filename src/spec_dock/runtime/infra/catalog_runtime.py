"""The catalog's ignored .runtime area: changesets for the next sync and the creation staging area (contract C4)."""

from __future__ import annotations

from contextlib import suppress
import json
import os
from pathlib import Path, PurePosixPath
import secrets
from typing import TYPE_CHECKING, Final

from spec_dock.runtime.domain.canonical_changeset import changeset_filename
from spec_dock.runtime.domain.canonical_structure import parse_timestamp

if TYPE_CHECKING:
    from spec_dock.runtime.domain.canonical_changeset import Changeset

CHANGESETS_RELATIVE: Final = PurePosixPath(".runtime/changesets")
STAGING_RELATIVE: Final = PurePosixPath(".runtime/staging")
_DIRECTORY_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)


def runtime_directory(catalog: Path, relative: PurePosixPath) -> Path:
    """Create `catalog/relative` component by component, refusing any symbolic link on the way."""
    os.close(_open_runtime_directory(catalog, relative))
    return catalog / relative


def _open_runtime_directory(catalog: Path, relative: PurePosixPath) -> int:
    current = os.open(catalog, _DIRECTORY_FLAGS)
    try:
        for part in relative.parts:
            with suppress(FileExistsError):
                os.mkdir(part, 0o755, dir_fd=current)
            following = os.open(part, _DIRECTORY_FLAGS, dir_fd=current)
            os.close(current)
            current = following
    except BaseException:
        os.close(current)
        raise
    return current


def write_changeset(catalog: Path, changeset: Changeset, *, token: str | None = None) -> Path:
    """Place one changeset with a temporary file and rename; call it while holding the catalog lock.

    Every write goes through the descriptor of the verified `.runtime/changesets` directory.
    """
    payload = (json.dumps(changeset.to_json(), ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    created = parse_timestamp(changeset.created_at)
    directory_fd = _open_runtime_directory(catalog, CHANGESETS_RELATIVE)
    try:
        name = changeset_filename(created, token or secrets.token_hex(8))
        while _exists(directory_fd, name):
            name = changeset_filename(created, secrets.token_hex(8))
        temporary = f".{name}.{secrets.token_hex(8)}.tmp"
        descriptor = os.open(
            temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0), 0o644, dir_fd=directory_fd
        )
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.rename(temporary, name, src_dir_fd=directory_fd, dst_dir_fd=directory_fd)
        except BaseException:
            with suppress(OSError):
                os.unlink(temporary, dir_fd=directory_fd)
            raise
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    return catalog / CHANGESETS_RELATIVE / name


def _exists(directory_fd: int, name: str) -> bool:
    try:
        os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
    except FileNotFoundError:
        return False
    return True


def staging_directory(catalog: Path) -> Path:
    return runtime_directory(catalog, STAGING_RELATIVE)
