"""Write the derived spec-dock/active role links one atomic rename at a time."""

from __future__ import annotations

from dataclasses import dataclass
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


def sync_active_links(
    specdock_dir: Path, plans: tuple[LinkPlan, ...], *, dry_run: bool
) -> tuple[tuple[LinkOutcome, ...], tuple[LegacyOutcome, ...]]:
    active = specdock_dir / "active"
    try:
        try:
            root = active.lstat()
        except FileNotFoundError:
            if not dry_run:
                active.mkdir()
        else:
            if not stat.S_ISDIR(root.st_mode):
                return tuple(LinkOutcome(plan.role, "skipped", "active_not_directory") for plan in plans), ()
    except OSError as error:
        return tuple(LinkOutcome(plan.role, "skipped", _reason(error)) for plan in plans), ()
    outcomes: list[LinkOutcome] = []
    for plan in plans:
        link = active / plan.role
        text = os.path.relpath(specdock_dir / plan.target, active)
        if not (specdock_dir / plan.target).is_dir():
            outcomes.append(LinkOutcome(plan.role, "skipped", "target_missing"))
            continue
        try:
            outcomes.append(_sync_role(plan.role, link, text, dry_run=dry_run))
        except OSError as error:
            outcomes.append(LinkOutcome(plan.role, "skipped", _reason(error)))
    return tuple(outcomes), _remove_legacy(active, dry_run=dry_run)


def _remove_legacy(active: Path, *, dry_run: bool) -> tuple[LegacyOutcome, ...]:
    """Old writers' generated files are never updated now; unlink them without reading or following."""
    outcomes: list[LegacyOutcome] = []
    for name in LEGACY_GENERATED:
        path = active / name
        try:
            observed = path.lstat()
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
            path.unlink()
        except OSError as error:
            outcomes.append(LegacyOutcome(name, "skipped", _reason(error)))
            continue
        outcomes.append(LegacyOutcome(name, "succeeded"))
    return tuple(outcomes)


def _sync_role(role: Role, link: Path, text: str, *, dry_run: bool) -> LinkOutcome:
    try:
        observed = link.lstat()
    except FileNotFoundError:
        observed = None
    if observed is not None and not stat.S_ISLNK(observed.st_mode):
        return LinkOutcome(role, "skipped", "occupied")
    if observed is not None and str(link.readlink()) == text:
        return LinkOutcome(role, "unchanged")
    if dry_run:
        return LinkOutcome(role, "planned")
    _replace_link(link, text)
    return LinkOutcome(role, "succeeded")


def _replace_link(link: Path, text: str) -> None:
    staged = link.with_name(f".{link.name}.{secrets.token_hex(8)}.tmp")
    staged.symlink_to(text)
    try:
        staged.replace(link)
    except BaseException:
        staged.unlink(missing_ok=True)
        raise


def _reason(error: OSError) -> str:
    # strerror omits the absolute path that str(error) would expose.
    return f"{type(error).__name__}: {error.strerror or error}"
