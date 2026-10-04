"""Publish one complete directory from private staging without replacement or a journal."""

from __future__ import annotations

import os
import re
import secrets
import stat
from typing import TYPE_CHECKING

from spec_dock.runtime.infra.direct_json import _create_guarded_directory
from spec_dock.runtime.infra.json_store import _rename_no_replace_at, open_guarded_directory

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


class DirectoryPublicationIncomplete(RuntimeError):
    def __init__(self, message: str, *, confirmed: bool = False) -> None:
        self.confirmed = confirmed
        super().__init__(message)


def publish_directory(
    destination: Path,
    *,
    staging_dir: Path,
    populate: Callable[[int], None],
    before_stage: Callable[[Path], None],
    before_publish: Callable[[], object],
    stage_name: str | None = None,
) -> None:
    name = stage_name or f".stage-{secrets.token_hex(16)}"
    if not re.fullmatch(r"\.stage-[0-9a-f]{32}", name):
        raise ValueError("invalid directory staging basename")
    before_stage(staging_dir / name)
    parent_fd = _create_guarded_directory(destination.parent)
    stage_root_fd: int | None = None
    stage_fd: int | None = None
    claimed = False
    attempted = False
    confirmed = False
    try:
        stage_root_fd = _create_guarded_directory(staging_dir)
        if os.fstat(stage_root_fd).st_dev != os.fstat(parent_fd).st_dev:
            raise ValueError("directory staging must be on the destination filesystem")
        os.mkdir(name, dir_fd=stage_root_fd)
        claimed = True
        stage_fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=stage_root_fd)
        identity = _identity(stage_fd)
        if _entry_identity(stage_root_fd, name) != identity:
            raise ValueError("directory staging identity changed")
        populate(stage_fd)
        _sync_tree(stage_fd)
        before_publish()
        _verify_parent(destination.parent, parent_fd)
        _verify_parent(staging_dir, stage_root_fd)
        if _entry_identity(stage_root_fd, name) != identity:
            raise ValueError("directory staging changed before publication")
        attempted = True
        try:
            _rename_no_replace_at(stage_root_fd, name, parent_fd, destination.name)
        except FileExistsError:
            attempted = False
            raise
        os.fsync(parent_fd)
        os.fsync(stage_root_fd)
        if _entry_identity(parent_fd, destination.name) != identity:
            raise ValueError("published directory identity changed")
        _verify_parent(destination.parent, parent_fd)
        confirmed = True
    except (OSError, ValueError, RuntimeError) as error:
        if attempted:
            raise DirectoryPublicationIncomplete(str(error), confirmed=confirmed) from error
        raise
    finally:
        cleanup_error: OSError | ValueError | RuntimeError | None = None
        if claimed and not attempted and stage_root_fd is not None and stage_fd is not None:
            try:
                if _entry_identity(stage_root_fd, name) == _identity(stage_fd):
                    _remove_contents(stage_fd)
                    if _entry_identity(stage_root_fd, name) != _identity(stage_fd):
                        raise ValueError("directory staging changed during cleanup")
                    os.rmdir(name, dir_fd=stage_root_fd)
            except (OSError, ValueError, RuntimeError) as error:
                cleanup_error = error
        for opened in (stage_fd, stage_root_fd, parent_fd):
            if opened is not None:
                try:
                    os.close(opened)
                except OSError as error:
                    cleanup_error = error
        if cleanup_error is not None:
            raise DirectoryPublicationIncomplete(str(cleanup_error), confirmed=confirmed) from cleanup_error


def _identity(descriptor: int) -> tuple[int, int]:
    observed = os.fstat(descriptor)
    return observed.st_dev, observed.st_ino


def _entry_identity(parent_fd: int, name: str) -> tuple[int, int]:
    observed = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    if not stat.S_ISDIR(observed.st_mode):
        raise ValueError("directory entry is not a regular directory")
    return observed.st_dev, observed.st_ino


def _verify_parent(path: Path, held_fd: int) -> None:
    fresh_fd = open_guarded_directory(path)
    try:
        if _identity(fresh_fd) != _identity(held_fd):
            raise ValueError("directory parent identity changed")
    finally:
        os.close(fresh_fd)


def _sync_tree(descriptor: int) -> None:
    for name in os.listdir(descriptor):
        observed = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
        if stat.S_ISLNK(observed.st_mode):
            continue
        if not stat.S_ISDIR(observed.st_mode) and not stat.S_ISREG(observed.st_mode):
            raise ValueError("directory staging contains an unsupported entry")
        child = os.open(
            name,
            os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | (os.O_DIRECTORY if stat.S_ISDIR(observed.st_mode) else 0),
            dir_fd=descriptor,
        )
        try:
            if _identity(child) != (observed.st_dev, observed.st_ino):
                raise ValueError("directory staging entry changed")
            if stat.S_ISDIR(observed.st_mode):
                _sync_tree(child)
            elif stat.S_ISREG(observed.st_mode):
                os.fsync(child)
            else:
                raise ValueError("directory staging contains an unsupported entry")
        finally:
            os.close(child)
    os.fsync(descriptor)


def _remove_contents(descriptor: int) -> None:
    for name in os.listdir(descriptor):
        observed = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
        if stat.S_ISDIR(observed.st_mode):
            child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            try:
                if _identity(child) != (observed.st_dev, observed.st_ino):
                    raise ValueError("directory staging entry changed during cleanup")
                _remove_contents(child)
                if _entry_identity(descriptor, name) != _identity(child):
                    raise ValueError("directory staging entry changed before cleanup")
                os.rmdir(name, dir_fd=descriptor)
            finally:
                os.close(child)
        else:
            os.unlink(name, dir_fd=descriptor)
