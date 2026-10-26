"""Pure rules of the periodic canonical sync (Epic ch. 5): names, path selection, holds and conflict plans.

Time, the PC name and file facts are arguments; nothing here touches Git, files or the clock.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import re
from typing import TYPE_CHECKING, Final, Literal

from spec_dock.runtime.domain.canonical_structure import format_timestamp, parse_timestamp

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Set

QUIET: Final = timedelta(seconds=30)
MAX_WAIT: Final = timedelta(minutes=5)
ChangeKind = Literal["modified", "added", "deleted"]
HoldKind = Literal["mass_delete", "secret", "too_large"]
MASS_DELETE_COUNT: Final = 20
MASS_DELETE_MIN: Final = 5
MASS_DELETE_RATIO: Final = 0.10
MAX_FILE_BYTES: Final = 10 * 1024 * 1024
# Whole token shapes only: a document that merely names a prefix is never held.
SECRET_PATTERNS: Final = tuple(
    re.compile(pattern)
    for pattern in (
        rb"ghp_[A-Za-z0-9]{36}",
        rb"gho_[A-Za-z0-9]{36}",
        rb"github_pat_[A-Za-z0-9_]{82}",
        rb"AKIA[0-9A-Z]{16}",
        rb"-----BEGIN [A-Z ]*PRIVATE KEY-----\r?\n[A-Za-z0-9+/=]",
    )
)

_PC_INVALID = re.compile(r"[^a-z0-9-]+")
_PC_DASHES = re.compile(r"-{2,}")
PC_NAME_MAX: Final = 32


def pc_name(hostname: str) -> str:
    """The hostname before its first dot, lowercased, with runs of other characters as one dash, at most 32."""
    name = _PC_INVALID.sub("-", hostname.split(".", 1)[0].lower())
    name = _PC_DASHES.sub("-", name).strip("-")[:PC_NAME_MAX].strip("-")
    return name or "pc"


def _stamp(now: datetime) -> str:
    if now.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware")
    return now.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def conflict_copy_name(path: str, *, pc: str, now: datetime, taken: Set[str]) -> str:
    """`<stem>.conflict-<pc>-<UTC>[.<ext>]` beside `path`; a dot only at the start or no dot means no extension."""
    directory, slash, name = path.rpartition("/")
    dot = name.rfind(".")
    stem, extension = (name[:dot], name[dot:]) if dot > 0 else (name, "")
    base = f"{stem}.conflict-{pc}-{_stamp(now)}"
    prefix = directory + slash
    candidate = f"{prefix}{base}{extension}"
    counter = 2
    while candidate in taken:
        candidate = f"{prefix}{base}-{counter}{extension}"
        counter += 1
    return candidate


@dataclass(frozen=True)
class CatalogChange:
    """One unsaved path in the catalog work tree; a deletion has no modification time."""

    path: str
    kind: ChangeKind
    mtime: datetime | None


@dataclass(frozen=True)
class Selection:
    selected: tuple[str, ...]
    pending_since: dict[str, str]


def select_paths(changes: Iterable[CatalogChange], *, pending_since: Mapping[str, str], now: datetime) -> Selection:
    """Pick paths quiet for 30 seconds, deletions 30 seconds after first seen, and anything first seen 5 minutes ago.

    `pending_since` keeps the first time each still-changed path was seen; saved or reverted paths leave it.
    """
    stamp = format_timestamp(now)
    seen: dict[str, str] = {}
    selected: list[str] = []
    for change in changes:
        first = pending_since.get(change.path, stamp)
        seen[change.path] = first
        waited = now - parse_timestamp(first)
        if change.kind == "deleted":
            quiet = waited >= QUIET
        else:
            assert change.mtime is not None
            quiet = now - min(change.mtime, now) >= QUIET
        if quiet or waited >= MAX_WAIT:
            selected.append(change.path)
    return Selection(tuple(sorted(selected)), seen)


@dataclass(frozen=True)
class HoldCandidate:
    """A file about to be saved: its size, current blob and content (None when too large or a symbolic link)."""

    path: str
    size: int
    blob: str
    content: bytes | None


def is_secret(content: bytes) -> bool:
    return any(pattern.search(content) for pattern in SECRET_PATTERNS)


def classify_holds(
    candidates: Iterable[HoldCandidate],
    *,
    deletions: Iterable[str],
    tracked_count: int,
    accepted_paths: Mapping[str, str],
    accepted_deletions: Iterable[str],
) -> dict[str, HoldKind]:
    """The paths the sync must not save automatically, by hold kind (Epic ch. 5, R-C4).

    `deletions` are every current work-tree deletion that no `origin: command` changeset covers, not only
    the ones selected this cycle, so a mass delete cannot trickle through the 30-second rule.
    """
    held: dict[str, HoldKind] = {}
    for candidate in candidates:
        if accepted_paths.get(candidate.path) == candidate.blob:
            continue
        if candidate.size > MAX_FILE_BYTES:
            held[candidate.path] = "too_large"
        elif candidate.content is not None and is_secret(candidate.content):
            held[candidate.path] = "secret"
    allowed = set(accepted_deletions)
    counted = sorted({path for path in deletions if path not in allowed})
    count = len(counted)
    if count >= MASS_DELETE_COUNT or (count >= MASS_DELETE_MIN and count >= MASS_DELETE_RATIO * tracked_count):
        held.update(dict.fromkeys(counted, "mass_delete"))
    return held


@dataclass(frozen=True)
class ConflictEntry:
    """One `git merge-tree -z` conflicted-file record: stage 1 is the base, 2 the first (local), 3 the second (remote)."""

    mode: str
    oid: str
    stage: int
    path: str


@dataclass(frozen=True)
class IndexEntry:
    mode: str
    oid: str
    path: str


@dataclass(frozen=True)
class Resolution:
    updates: tuple[IndexEntry, ...]
    removals: tuple[str, ...]
    copies: tuple[tuple[str, str], ...]


def resolve_conflicts(entries: Iterable[ConflictEntry], *, pc: str, now: datetime, taken: Set[str]) -> Resolution:
    """Resolve by stage only: the remote version keeps the name, the local one becomes a conflict copy (R-C3).

    A side that changed beats a side that deleted, so nothing that was edited is lost.
    """
    stages: dict[str, dict[int, ConflictEntry]] = {}
    for entry in entries:
        if entry.stage not in (1, 2, 3):
            raise ValueError(f"unknown merge stage {entry.stage} for {entry.path!r}")
        stages.setdefault(entry.path, {})[entry.stage] = entry
    names = set(taken)
    updates: list[IndexEntry] = []
    removals: list[str] = []
    copies: list[tuple[str, str]] = []
    for path in sorted(stages):
        local, remote = stages[path].get(2), stages[path].get(3)
        if local is not None and remote is not None:
            copy = conflict_copy_name(path, pc=pc, now=now, taken=names)
            names.add(copy)
            updates.append(IndexEntry(remote.mode, remote.oid, path))
            updates.append(IndexEntry(local.mode, local.oid, copy))
            copies.append((path, copy))
        elif local is not None or remote is not None:
            kept = local or remote
            assert kept is not None
            updates.append(IndexEntry(kept.mode, kept.oid, path))
        else:
            removals.append(path)
    return Resolution(tuple(updates), tuple(removals), tuple(copies))
