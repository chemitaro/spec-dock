"""Write the derived spec-dock/active role links without ever replacing an entry that is not a link.

Every write and delete is anchored to the directory descriptors that were inspected, so a
root swapped after inspection can never redirect a link write or a legacy unlink elsewhere.
"""

from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
import errno
import os
import secrets
import stat
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from pathlib import Path

    from spec_dock.runtime.domain.active_links import LinkPlan, Role

LEGACY_GENERATED = (
    "context-pack.md",
    "current-runbook.json",
    "current-runbook.md",
    "initiative.path",
    "epic.path",
    "issue.path",
)
_DIRECTORY_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)


@dataclass(frozen=True)
class LinkOutcome:
    role: Role
    status: Literal["planned", "succeeded", "unchanged", "skipped"]
    reason: str | None = None


@dataclass(frozen=True)
class LegacyOutcome:
    name: str
    status: Literal["planned", "succeeded", "skipped"]
    reason: str | None = None


class _ActiveUnavailable(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def sync_active_links(
    specdock_dir: Path, plans: tuple[LinkPlan, ...], *, dry_run: bool
) -> tuple[tuple[LinkOutcome, ...], tuple[LegacyOutcome, ...]]:
    try:
        workspace_fd = os.open(specdock_dir, _DIRECTORY_FLAGS)
    except OSError as error:
        return tuple(LinkOutcome(plan.role, "skipped", _reason(error)) for plan in plans), ()
    try:
        try:
            active_fd = _open_active(workspace_fd, dry_run=dry_run)
        except _ActiveUnavailable as unavailable:
            return tuple(LinkOutcome(plan.role, "skipped", unavailable.reason) for plan in plans), ()
        try:
            outcomes = tuple(_sync_plan(specdock_dir, active_fd, plan, dry_run=dry_run) for plan in plans)
            legacy = _remove_legacy(active_fd, dry_run=dry_run) if active_fd is not None else ()
            return outcomes, legacy
        finally:
            if active_fd is not None:
                os.close(active_fd)
    finally:
        os.close(workspace_fd)


def _open_active(workspace_fd: int, *, dry_run: bool) -> int | None:
    """Open spec-dock/active without following a redirect; None means a dry-run of a missing root."""
    try:
        return os.open("active", _DIRECTORY_FLAGS, dir_fd=workspace_fd)
    except FileNotFoundError:
        pass
    except OSError as error:
        raise _unavailable(error) from error
    if dry_run:
        return None
    try:
        os.mkdir("active", 0o755, dir_fd=workspace_fd)
        return os.open("active", _DIRECTORY_FLAGS, dir_fd=workspace_fd)
    except OSError as error:
        raise _unavailable(error) from error


def _unavailable(error: OSError) -> _ActiveUnavailable:
    if error.errno in (errno.ELOOP, errno.ENOTDIR, errno.EEXIST):
        return _ActiveUnavailable("active_not_directory")
    return _ActiveUnavailable(_reason(error))


def _sync_plan(specdock_dir: Path, active_fd: int | None, plan: LinkPlan, *, dry_run: bool) -> LinkOutcome:
    text = f"../{plan.target}"
    try:
        if not stat.S_ISDIR((specdock_dir / plan.target).stat().st_mode):
            return LinkOutcome(plan.role, "skipped", "target_missing")
        if active_fd is None:
            return LinkOutcome(plan.role, "planned")
        return _sync_role(active_fd, plan.role, text, dry_run=dry_run)
    except (FileNotFoundError, NotADirectoryError):
        return LinkOutcome(plan.role, "skipped", "target_missing")
    except OSError as error:
        return LinkOutcome(plan.role, "skipped", _reason(error))


def _sync_role(active_fd: int, role: Role, text: str, *, dry_run: bool) -> LinkOutcome:
    try:
        observed = os.stat(role, dir_fd=active_fd, follow_symlinks=False)
    except FileNotFoundError:
        observed = None
    if observed is not None and not stat.S_ISLNK(observed.st_mode):
        return LinkOutcome(role, "skipped", "occupied")
    if observed is not None and os.readlink(role, dir_fd=active_fd) == text:
        return LinkOutcome(role, "unchanged")
    if dry_run:
        return LinkOutcome(role, "planned")
    if observed is not None and not _set_aside_stale_link(active_fd, role):
        return LinkOutcome(role, "skipped", "occupied")
    try:
        # symlink() never replaces an entry, so anything that appeared meanwhile is kept.
        os.symlink(text, role, dir_fd=active_fd)
    except FileExistsError:
        return LinkOutcome(role, "skipped", "occupied")
    return LinkOutcome(role, "succeeded")


def _set_aside_stale_link(active_fd: int, role: Role) -> bool:
    """Move the entry away and discard it only if it is still a symlink; otherwise put it back.

    Another writer may replace the inspected symlink at any moment, so the entry is moved
    atomically first and verified afterwards. A non-link is restored without ever replacing
    whatever now occupies the role name; if it cannot be restored it stays under its aside name.
    """
    aside = f".{role}.{secrets.token_hex(8)}.aside"
    os.rename(role, aside, src_dir_fd=active_fd, dst_dir_fd=active_fd)
    if stat.S_ISLNK(os.stat(aside, dir_fd=active_fd, follow_symlinks=False).st_mode):
        os.unlink(aside, dir_fd=active_fd)
        return True
    with suppress(OSError):
        os.link(aside, role, src_dir_fd=active_fd, dst_dir_fd=active_fd, follow_symlinks=False)
        os.unlink(aside, dir_fd=active_fd)
        return False
    with suppress(OSError):
        if not _exists(active_fd, role):
            os.rename(aside, role, src_dir_fd=active_fd, dst_dir_fd=active_fd)
    return False


def _exists(active_fd: int, name: str) -> bool:
    try:
        os.stat(name, dir_fd=active_fd, follow_symlinks=False)
    except FileNotFoundError:
        return False
    return True


def _remove_legacy(active_fd: int, *, dry_run: bool) -> tuple[LegacyOutcome, ...]:
    """Old writers' generated files are never updated now; unlink them without reading or following."""
    outcomes: list[LegacyOutcome] = []
    for name in LEGACY_GENERATED:
        try:
            observed = os.stat(name, dir_fd=active_fd, follow_symlinks=False)
        except FileNotFoundError:
            continue
        except OSError as error:
            outcomes.append(LegacyOutcome(name, "skipped", _reason(error)))
            continue
        if not (stat.S_ISREG(observed.st_mode) or stat.S_ISLNK(observed.st_mode)):
            outcomes.append(LegacyOutcome(name, "skipped", "not_a_file"))
            continue
        if dry_run:
            outcomes.append(LegacyOutcome(name, "planned"))
            continue
        try:
            os.unlink(name, dir_fd=active_fd)
        except OSError as error:
            outcomes.append(LegacyOutcome(name, "skipped", _reason(error)))
            continue
        outcomes.append(LegacyOutcome(name, "succeeded"))
    return tuple(outcomes)


def _reason(error: OSError) -> str:
    # strerror omits the absolute path that str(error) would expose.
    return f"{type(error).__name__}: {error.strerror or error}"
