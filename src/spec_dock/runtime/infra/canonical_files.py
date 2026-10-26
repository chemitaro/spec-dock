"""Observe and place the spec-dock/initiatives link and append the exclude lines, never replacing real content.

Link writes are anchored to the inspected spec-dock directory descriptor, so a directory swapped after
inspection cannot redirect the write.
"""

from __future__ import annotations

from contextlib import suppress
import os
from pathlib import Path
import secrets
import stat
from typing import TYPE_CHECKING, Literal

from spec_dock.runtime.domain.canonical_layout import LinkObservation, append_lines, missing_lines

if TYPE_CHECKING:
    from collections.abc import Sequence

_DIRECTORY_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)


class LinkOccupied(FileExistsError):
    """The link name holds a real file or directory; SpecDock never replaces it."""


def observe_link(path: Path) -> LinkObservation:
    try:
        observed = os.lstat(path)
    except (FileNotFoundError, NotADirectoryError):
        return LinkObservation(path, "absent")
    if stat.S_ISLNK(observed.st_mode):
        resolved = Path(os.path.realpath(path)) if Path(path).exists() else None
        return LinkObservation(path, "symlink", str(path.readlink()), resolved)
    if stat.S_ISDIR(observed.st_mode):
        return LinkObservation(path, "directory", entries=count_entries(path))
    return LinkObservation(path, "file" if stat.S_ISREG(observed.st_mode) else "other")


def count_entries(directory: Path) -> int:
    """Files and directories below `directory`, without following links."""
    total = 0
    for _root, directories, files in os.walk(directory, followlinks=False):
        total += len(directories) + len(files)
    return total


def place_link(spec_dock_dir: Path, name: str, text: str) -> Literal["created", "replaced", "unchanged"]:
    """Create `name -> text`, or atomically replace a symlink with another value; real content raises LinkOccupied."""
    directory_fd = os.open(spec_dock_dir, _DIRECTORY_FLAGS)
    try:
        try:
            observed = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
        except FileNotFoundError:
            observed = None
        if observed is None:
            try:
                # symlink() never replaces an entry, so anything that appeared meanwhile is kept.
                os.symlink(text, name, dir_fd=directory_fd)
            except FileExistsError as error:
                raise LinkOccupied(f"{spec_dock_dir / name} appeared while linking") from error
            os.fsync(directory_fd)
            return "created"
        if not stat.S_ISLNK(observed.st_mode):
            raise LinkOccupied(f"{spec_dock_dir / name} is not a symbolic link")
        if os.readlink(name, dir_fd=directory_fd) == text:
            return "unchanged"
        temporary = f".{name}.{secrets.token_hex(8)}.tmp"
        os.symlink(text, temporary, dir_fd=directory_fd)
        try:
            # Re-check right before the rename. A directory that appears after this check makes rename fail
            # (EISDIR), so it stays; a regular file created in the remaining instant would be replaced. Nothing
            # SpecDock or Git writes creates a file named spec-dock/initiatives, so that window is accepted.
            if not _is_symlink_at(directory_fd, name):
                raise LinkOccupied(f"{spec_dock_dir / name} is not a symbolic link")
            os.rename(temporary, name, src_dir_fd=directory_fd, dst_dir_fd=directory_fd)
        except BaseException:
            with suppress(OSError):
                os.unlink(temporary, dir_fd=directory_fd)
            raise
        os.fsync(directory_fd)
        return "replaced"
    finally:
        os.close(directory_fd)


def _is_symlink_at(directory_fd: int, name: str) -> bool:
    try:
        return stat.S_ISLNK(os.stat(name, dir_fd=directory_fd, follow_symlinks=False).st_mode)
    except FileNotFoundError:
        return False


class FileOccupied(FileExistsError):
    """A directory or symbolic link is where SpecDock writes a generated file; it is never replaced."""


def is_regular_file(path: Path) -> bool:
    """A regular file at `path` itself; a symbolic link to one does not count."""
    try:
        return stat.S_ISREG(os.lstat(path).st_mode)
    except OSError:
        return False


def replace_text_file(directory: Path, name: str, text: str) -> None:
    """Atomically replace `directory/name` with `text`, anchored to the inspected directory descriptor.

    The temporary file is created exclusively without following links, synced and renamed; a directory or
    symbolic link at `name` raises FileOccupied and stays as it is.
    """
    directory_fd = os.open(directory, _DIRECTORY_FLAGS)
    try:
        if _occupied_at(directory_fd, name):
            raise FileOccupied(f"{directory / name} is a directory or symbolic link")
        temporary = f".{name}.{secrets.token_hex(8)}.tmp"
        descriptor = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0),
            0o644,
            dir_fd=directory_fd,
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                stream.write(text)
                stream.flush()
                os.fsync(stream.fileno())
            # A directory that appears after this check makes the rename fail; it stays.
            if _occupied_at(directory_fd, name):
                raise FileOccupied(f"{directory / name} is a directory or symbolic link")
            os.rename(temporary, name, src_dir_fd=directory_fd, dst_dir_fd=directory_fd)
        except BaseException:
            with suppress(OSError):
                os.unlink(temporary, dir_fd=directory_fd)
            raise
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def _occupied_at(directory_fd: int, name: str) -> bool:
    try:
        mode = os.stat(name, dir_fd=directory_fd, follow_symlinks=False).st_mode
    except FileNotFoundError:
        return False
    return stat.S_ISDIR(mode) or stat.S_ISLNK(mode)


def read_text_file(path: Path) -> str | None:
    """Text for rule matching; bytes that are not UTF-8 stay distinguishable (surrogateescape)."""
    try:
        return path.read_bytes().decode("utf-8", errors="surrogateescape")
    except (FileNotFoundError, NotADirectoryError):
        return None


def append_exclude(common_dir: Path, lines: Sequence[str]) -> tuple[str, ...]:
    """Append the rule block to <common>/info/exclude when it is not in effect, keeping existing bytes and mode."""
    info = common_dir / "info"
    with suppress(FileExistsError):
        Path(info).mkdir(mode=0o755)
    exclude = info / "exclude"
    try:
        current = exclude.read_bytes()
    except FileNotFoundError:
        current = None
    text = current.decode("utf-8", errors="surrogateescape") if current is not None else None
    missing = missing_lines(text, lines)
    if not missing:
        return ()
    updated = append_lines(text, lines).encode("utf-8", errors="surrogateescape")
    try:
        mode = stat.S_IMODE(exclude.stat().st_mode)
    except FileNotFoundError:
        mode = 0o644
    temporary = info / f".exclude.{secrets.token_hex(8)}.tmp"
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0), 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(updated)
            stream.flush()
            os.fsync(stream.fileno())
        Path(temporary).chmod(mode)
        Path(temporary).replace(exclude)
    except BaseException:
        with suppress(OSError):
            Path(temporary).unlink()
        raise
    directory_fd = os.open(info, _DIRECTORY_FLAGS)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    return missing
