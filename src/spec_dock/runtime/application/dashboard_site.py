"""What the dashboard server serves: the repository list and each repository's reading (iss-00529 D-03).

The registry and the hidden marks are re-read when their files change, so a new `canonical link` appears
without a restart (Epic R-01). Each repository keeps its last readable snapshot: an unreadable file (broken, or
caught mid-write) keeps showing it, marked unreadable (Epic D-12, F-04); a missing or unknown-version file does
not. Models are rebuilt per request because staleness and pull request certainty change with time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import threading
from typing import TYPE_CHECKING, Literal

from spec_dock.runtime.application.dashboard_todos import DashboardTodos
from spec_dock.runtime.domain.canonical_structure import parse_timestamp
from spec_dock.runtime.domain.dashboard_model import STALE_AFTER, build_model
from spec_dock.runtime.infra.canonical_registry import RegistryUnreadable, read_registry, registry_path
from spec_dock.runtime.infra.canonical_state import STATE_FILE, catalog_state_dir
from spec_dock.runtime.infra.dashboard_files import (
    DASHBOARD_DIRECTORY,
    REPOSITORIES_FILE,
    read_snapshot_file,
    snapshot_path,
)
from spec_dock.runtime.infra.dashboard_store import hidden_repositories
from spec_dock.runtime.infra.github_structure import GithubRepository

if TYPE_CHECKING:
    from collections.abc import Callable

    from spec_dock.runtime.domain.canonical_sync_state import RegistryEntry
    from spec_dock.runtime.domain.dashboard_model import DashboardModel
    from spec_dock.runtime.domain.dashboard_snapshot import ParsedSnapshot

ReadStatus = Literal["ok", "unreadable", "missing", "unsupported"]
Lookup = Literal["visible", "hidden", "unknown"]
Problem = Literal["ambiguous"]
_Signature = tuple[int, int] | None


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _signature(path: Path) -> _Signature:
    try:
        info = path.stat()
    except OSError:
        return None
    return (info.st_mtime_ns, info.st_size)


@dataclass(frozen=True)
class SiteRepository:
    """A served repository; `catalog` is None when two clones are registered (`problem` ambiguous)."""

    repository: GithubRepository
    catalog: Path | None
    catalogs: tuple[str, ...]
    problem: Problem | None = None

    @property
    def key(self) -> str:
        return self.repository.key


@dataclass(frozen=True)
class RegistryRow:
    repository: str | None
    catalog: str
    main_checkout: str
    hidden: bool
    served: bool
    problem: str | None


@dataclass(frozen=True)
class RepositoryView:
    """One repository's reading: `parsed` is the current or the last readable snapshot (status unreadable)."""

    repository: SiteRepository
    status: ReadStatus
    parsed: ParsedSnapshot | None
    detail: str | None
    model: DashboardModel | None
    revision: str


@dataclass
class _Cache:
    signature: _Signature = None
    status: ReadStatus = "missing"
    detail: str | None = None
    current: ParsedSnapshot | None = None
    last_good: ParsedSnapshot | None = None
    read: bool = False


@dataclass
class _Listing:
    signature: tuple[_Signature, _Signature] | None = None
    entries: tuple[RegistryEntry, ...] = ()
    hidden: frozenset[str] = frozenset()
    registry_error: str | None = None
    marks_unreadable: bool = False
    marks_read: bool = False
    served: dict[str, SiteRepository] = field(default_factory=dict)


class DashboardSite:
    def __init__(self, state_root: Path, *, now: Callable[[], datetime] = _utc_now) -> None:
        self.state_root = state_root
        self.now = now
        self._lock = threading.Lock()
        self._listing = _Listing()
        self._caches: dict[str, _Cache] = {}
        self.todos = DashboardTodos(self.registry_entries, now=lambda: self.now())  # iss-00554 D-02

    # --- Listing ----------------------------------------------------------------------------------------------

    def _refresh_listing(self) -> _Listing:
        marks = self.state_root / DASHBOARD_DIRECTORY / REPOSITORIES_FILE
        signature = (_signature(registry_path(self.state_root)), _signature(marks))
        listing = self._listing
        if listing.signature == signature:
            return listing
        entries = listing.entries
        error: str | None = None
        try:
            entries = read_registry(self.state_root).catalogs
        except RegistryUnreadable as failure:
            error = failure.reason  # keep the last readable registry (F-07)
        read = hidden_repositories(self.state_root)
        groups: dict[str, list[RegistryEntry]] = {}
        for entry in entries:
            repository = _parse(entry.repository)
            if repository is not None:
                groups.setdefault(repository.key, []).append(entry)
        served: dict[str, SiteRepository] = {}
        for key, items in groups.items():
            repository = GithubRepository.parse(key)
            if len(items) == 1:
                served[key] = SiteRepository(repository, Path(items[0].catalog), (items[0].catalog,))
            else:
                served[key] = SiteRepository(repository, None, tuple(item.catalog for item in items), "ambiguous")
        # Unreadable marks never unhide (fail closed): keep the last readable marks, and before any readable
        # read hide every repository until `dashboard hide`/`show` can be used again.
        if read is not None:
            hidden, marks_read = read, True
        elif listing.marks_read:
            hidden, marks_read = listing.hidden, True
        else:
            hidden, marks_read = frozenset(served), False
        self._listing = _Listing(signature, entries, hidden, error, read is None, marks_read, served)
        return self._listing

    def repositories(self) -> tuple[SiteRepository, ...]:
        """The visible (registered, known, not hidden) repositories, by key."""
        with self._lock:
            listing = self._refresh_listing()
            return tuple(listing.served[key] for key in sorted(listing.served) if key not in listing.hidden)

    def unknown_count(self) -> int:
        with self._lock:
            return sum(1 for entry in self._refresh_listing().entries if _parse(entry.repository) is None)

    def marks_unreadable(self) -> bool:
        with self._lock:
            return self._refresh_listing().marks_unreadable

    def registry_entries(self) -> tuple[RegistryEntry, ...]:
        """The last readable registry rows (the human tasks choose their catalogs from these, iss-00554 D-02)."""
        with self._lock:
            return self._refresh_listing().entries

    def listing_signature(self) -> object:
        with self._lock:
            listing = self._refresh_listing()
            return (listing.signature, tuple(sorted(listing.hidden)))

    def registry_error(self) -> str | None:
        with self._lock:
            return self._refresh_listing().registry_error

    def rows(self) -> tuple[RegistryRow, ...]:
        """Every registry row with its visibility, for `dashboard list`."""
        with self._lock:
            listing = self._refresh_listing()
        rows: list[RegistryRow] = []
        for entry in listing.entries:
            repository = _parse(entry.repository)
            if repository is None:
                rows.append(RegistryRow(None, entry.catalog, entry.main_checkout, False, False, "repository_unknown"))
                continue
            site = listing.served[repository.key]
            hidden = repository.key in listing.hidden
            rows.append(
                RegistryRow(repository.key, entry.catalog, entry.main_checkout, hidden, not hidden, site.problem)
            )
        return tuple(rows)

    def lookup(self, host: str, owner: str, name: str) -> tuple[Lookup, SiteRepository | None]:
        try:
            key = GithubRepository(owner, name, host).key
        except ValueError:
            return "unknown", None
        with self._lock:
            listing = self._refresh_listing()
            site = listing.served.get(key)
            if site is None:
                return "unknown", None
            return ("hidden" if key in listing.hidden else "visible"), site

    # --- One repository --------------------------------------------------------------------------------------

    def view(self, site: SiteRepository) -> RepositoryView:
        """Read (or reuse) the snapshot and build the model; exceptions stay in the caller's response."""
        path = snapshot_path(self.state_root, site.repository)
        with self._lock:
            cache = self._caches.setdefault(site.key, _Cache())
            signature = _signature(path)
            if not cache.read or signature != cache.signature:
                read = read_snapshot_file(self.state_root, site.repository)
                cache.signature, cache.status, cache.detail, cache.read = signature, read.status, read.detail, True
                cache.current = read.parsed
                if read.status == "ok":
                    cache.last_good = read.parsed
            status, detail = cache.status, cache.detail
            parsed = cache.current if status == "ok" else cache.last_good if status == "unreadable" else None
        now = self.now()
        model = build_model(parsed.snapshot, now=now) if parsed is not None else None
        return RepositoryView(site, status, parsed, detail, model, self._revision(site, signature, status, model, now))

    def _revision(
        self,
        site: SiteRepository,
        signature: _Signature,
        status: ReadStatus,
        model: DashboardModel | None,
        now: datetime,
    ) -> str:
        catalog_state = (
            _signature(catalog_state_dir(self.state_root, str(site.catalog)) / STATE_FILE) if site.catalog else None
        )
        age = now - parse_timestamp(model.fetched_at) if model is not None else None
        stale = age is not None and age > STALE_AFTER
        # While stale, a 10-minute step makes the screens reload the notice text ("N時間前から…").
        step = int(age.total_seconds() // 600) if stale and age is not None else None
        parts = (
            signature,
            catalog_state,
            status,
            stale,
            step,
            model.pull_request_status if model is not None else None,
            site.problem,
            self.todos.signature(site),  # CLI-written tasks reach the 5-second refresh (iss-00554 R-07)
        )
        return hashlib.sha256(repr(parts).encode()).hexdigest()[:16]


def _parse(value: str | None) -> GithubRepository | None:
    if value is None:
        return None
    try:
        return GithubRepository.parse(value)
    except ValueError:
        return None
