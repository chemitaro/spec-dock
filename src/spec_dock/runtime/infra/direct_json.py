"""One-file cooperative metadata replacement without a persistent transaction journal."""

from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
import json
import os
import secrets
import stat
from typing import TYPE_CHECKING

from spec_dock.runtime.infra.json_store import open_guarded_directory, read_guarded_json_bytes_at

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


@dataclass(frozen=True)
class PublishedJson:
    payload: bytes
    identity: tuple[int, int]


class MetadataPublicationIncomplete(RuntimeError):
    """An attempted replacement or its later cleanup did not complete normally."""

    def __init__(self, message: str, *, published: PublishedJson | None = None) -> None:
        self.published = published
        super().__init__(message)


def replace_existing_json(
    path: Path,
    data: dict[str, object],
    *,
    expected_bytes: bytes,
    expected_identity: tuple[int, int],
    staging_dir: Path,
    before_replace: Callable[[], object],
    before_stage: Callable[[Path], None],
) -> PublishedJson:
    """Compare exact bytes/identity, then atomically replace one existing regular file.

    This is an optimistic cooperative check, not an atomic CAS against arbitrary
    external writers. A failed or unknown replacement is never rolled back.
    """
    parent_fd = open_guarded_directory(path.parent)
    stage_fd: int | None = None
    name = f".stage-{secrets.token_hex(16)}"
    descriptor: int | None = None
    attempted = False
    confirmed: PublishedJson | None = None
    try:
        before_stage(staging_dir / name)
        stage_fd = _create_guarded_directory(staging_dir)
        if os.fstat(stage_fd).st_dev != os.fstat(parent_fd).st_dev:
            raise ValueError("metadata staging must be on the destination filesystem")
        loaded = read_guarded_json_bytes_at(parent_fd, path.name)
        if loaded is None or loaded[1:] != (expected_bytes, expected_identity):
            raise ValueError("metadata input changed")
        current = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        payload = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode()
        descriptor = os.open(
            name, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, stat.S_IMODE(current.st_mode), dir_fd=stage_fd
        )
        os.fchmod(descriptor, stat.S_IMODE(current.st_mode))
        with os.fdopen(os.dup(descriptor), "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        before_replace()
        loaded = read_guarded_json_bytes_at(parent_fd, path.name)
        if loaded is None or loaded[1:] != (expected_bytes, expected_identity):
            raise ValueError("metadata input changed before replacement")
        fresh_fd = open_guarded_directory(path.parent)
        try:
            if (os.fstat(fresh_fd).st_dev, os.fstat(fresh_fd).st_ino) != (
                os.fstat(parent_fd).st_dev,
                os.fstat(parent_fd).st_ino,
            ):
                raise ValueError("metadata parent identity changed")
        finally:
            os.close(fresh_fd)
        attempted = True
        os.replace(name, path.name, src_dir_fd=stage_fd, dst_dir_fd=parent_fd)
        os.fsync(parent_fd)
        os.fsync(stage_fd)
        published = read_guarded_json_bytes_at(parent_fd, path.name)
        new_stat = os.fstat(descriptor)
        identity = (new_stat.st_dev, new_stat.st_ino)
        if published is None or published[1:] != (payload, identity):
            raise ValueError("metadata replacement readback changed")
        fresh_fd = open_guarded_directory(path.parent)
        try:
            if (os.fstat(fresh_fd).st_dev, os.fstat(fresh_fd).st_ino) != (
                os.fstat(parent_fd).st_dev,
                os.fstat(parent_fd).st_ino,
            ):
                raise ValueError("metadata parent identity changed after replacement")
        finally:
            os.close(fresh_fd)
        confirmed = PublishedJson(payload, identity)
        return confirmed
    except (OSError, ValueError, RuntimeError) as error:
        if attempted:
            raise MetadataPublicationIncomplete(str(error), published=confirmed) from error
        raise
    finally:
        cleanup_error: OSError | None = None
        if stage_fd is not None and not attempted and descriptor is not None:
            try:
                observed = os.stat(name, dir_fd=stage_fd, follow_symlinks=False)
                expected = os.fstat(descriptor)
                if (observed.st_dev, observed.st_ino) == (expected.st_dev, expected.st_ino):
                    os.unlink(name, dir_fd=stage_fd)
            except FileNotFoundError:
                pass
            except OSError as error:
                cleanup_error = error
        for opened in (descriptor, stage_fd, parent_fd):
            if opened is not None:
                try:
                    os.close(opened)
                except OSError as error:
                    cleanup_error = error
        if cleanup_error is not None:
            if attempted:
                raise MetadataPublicationIncomplete(str(cleanup_error), published=confirmed) from cleanup_error
            raise cleanup_error


def _create_guarded_directory(path: Path) -> int:
    if not path.is_absolute():
        raise ValueError("metadata staging must be absolute")
    ancestor = path
    missing: list[str] = []
    while not ancestor.exists():
        missing.append(ancestor.name)
        ancestor = ancestor.parent
    descriptor = open_guarded_directory(ancestor)
    try:
        for name in reversed(missing):
            with suppress(FileExistsError):
                os.mkdir(name, mode=0o700, dir_fd=descriptor)
            child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise
