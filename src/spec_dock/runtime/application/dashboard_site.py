"""What the dashboard server serves: the repository list and each repository's reading (iss-00529 D-03).

The registry, the hidden marks and the dashboard settings (the user's `config.json` and each catalog's
`dashboard.json`, iss-00552 D-03) are re-read when their files change, so a new `canonical link` or a settings
edit applies without a restart (Epic R-01). Each repository keeps its last readable snapshot: an unreadable file (broken, or
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

from spec_dock.runtime.domain.canonical_structure import parse_timestamp
from spec_dock.runtime.domain.dashboard_model import STALE_AFTER, build_model
from spec_dock.runtime.domain.dashboard_visibility import REPOSITORY_FILE, Visibility, resolve_config
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
from spec_dock.runtime.infra.user_config import read_repository_dashboard, read_user_dashboard, user_config_path

if TYPE_CHECKING:
    from collections.abc import Callable

    from spec_dock.runtime.domain.canonical_sync_state import RegistryEntry
    from spec_dock.runtime.domain.dashboard_model import DashboardModel
    from spec_dock.runtime.domain.dashboard_snapshot import ParsedSnapshot
    from spec_dock.runtime.domain.dashboard_visibility import ConfigProblem, UserDashboard

ReadStatus = Literal["ok", "unreadable", "missing", "unsupported"]
Lookup = Literal["visible", "hidden", "unknown"]
Problem = Literal["ambiguous"]
_Signature = tuple[int, int] | None
_ListingSignature = tuple[_Signature, _Signature, _Signature, tuple[_Signature, ...]]


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
    visibility: Visibility | None = None  # None for a row whose repository is unknown


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
    signature: _ListingSignature | None = None
    entries: tuple[RegistryEntry, ...] = ()
    hidden: frozenset[str] = frozenset()  # the marks as read (every served key while never readable)
    registry_error: str | None = None
    marks_unreadable: bool = False
    marks_read: bool = False
    served: dict[str, SiteRepository] = field(default_factory=dict)
    user: UserDashboard | None = None
    visibility: dict[str, Visibility] = field(default_factory=dict)
    problems: tuple[ConfigProblem, ...] = ()


class DashboardSite:
    def __init__(
        self, state_root: Path, *, now: Callable[[], datetime] = _utc_now, user_config: Path | None = None
    ) -> None:
        self.state_root = state_root
        self.now = now
        self.user_config = user_config if user_config is not None else user_config_path()
        self._lock = threading.Lock()
        self._listing = _Listing()
        self._caches: dict[str, _Cache] = {}

    # --- Listing ----------------------------------------------------------------------------------------------

    def _file_signatures(self) -> tuple[_Signature, _Signature, _Signature]:
        marks = self.state_root / DASHBOARD_DIRECTORY / REPOSITORIES_FILE
        return (_signature(registry_path(self.state_root)), _signature(marks), _signature(self.user_config))

    @staticmethod
    def _settings_signatures(entries: tuple[RegistryEntry, ...]) -> tuple[_Signature, ...]:
        return tuple(_signature(Path(entry.catalog) / REPOSITORY_FILE) for entry in entries)

    def _refresh_listing(self) -> _Listing:
        # Every signature is taken before its file is read: a write during the read then leaves a signature
        # that differs from the file and the next request reads again (a later one would keep stale contents).
        listing = self._listing
        files = self._file_signatures()
        if listing.signature is not None and listing.signature == (*files, self._settings_signatures(listing.entries)):
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
        settings = self._settings_signatures(entries)
        user = read_user_dashboard(self.user_config)
        visibility: dict[str, Visibility] = {}
        problems: list[ConfigProblem] = []
        for key, items in groups.items():
            layers = [read_repository_dashboard(Path(item.catalog)) for item in items]
            config = resolve_config(user, layers, key)
            visibility[key] = Visibility(key in hidden, config)
            problems.extend(problem for problem in config.problems if problem not in problems)
        if user.state == "invalid" and not groups:
            problems.extend(resolve_config(user, (), "").problems)
        problems.sort(key=lambda problem: (problem.layer != "user", problem.path))
        self._listing = _Listing(
            (*files, settings),
            entries,
            hidden,
            error,
            read is None,
            marks_read,
            served,
            user,
            visibility,
            tuple(problems),
        )
        return self._listing

    def repositories(self) -> tuple[SiteRepository, ...]:
        """The visible (registered, known, not hidden) repositories, by key."""
        with self._lock:
            listing = self._refresh_listing()
            return tuple(listing.served[key] for key in sorted(listing.served) if not listing.visibility[key].hidden)

    def unknown_count(self) -> int:
        with self._lock:
            return sum(1 for entry in self._refresh_listing().entries if _parse(entry.repository) is None)

    def marks_unreadable(self) -> bool:
        with self._lock:
            return self._refresh_listing().marks_unreadable

    def config_problems(self) -> tuple[ConfigProblem, ...]:
        """The unreadable settings layers and disagreeing clones, the user's file first."""
        with self._lock:
            return self._refresh_listing().problems

    def visibility(self, key: str, fallback_catalog: Path | None = None) -> Visibility:
        """One repository's answer; an unregistered one reads `fallback_catalog` as its repository layer."""
        with self._lock:
            listing = self._refresh_listing()
        found = listing.visibility.get(key)
        if found is not None:
            return found
        mark = key in listing.hidden or not listing.marks_read  # marks never readable hide (fail closed)
        layers = [read_repository_dashboard(fallback_catalog)] if fallback_catalog is not None else []
        user = listing.user if listing.user is not None else read_user_dashboard(self.user_config)
        return Visibility(mark, resolve_config(user, layers, key))

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
            visibility = listing.visibility[repository.key]
            hidden = visibility.hidden
            rows.append(
                RegistryRow(
                    repository.key, entry.catalog, entry.main_checkout, hidden, not hidden, site.problem, visibility
                )
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
            return ("hidden" if listing.visibility[key].hidden else "visible"), site

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
        )
        return hashlib.sha256(repr(parts).encode()).hexdigest()[:16]


def _parse(value: str | None) -> GithubRepository | None:
    if value is None:
        return None
    try:
        return GithubRepository.parse(value)
    except ValueError:
        return None


def read_visibility(state_root: Path, repository: GithubRepository, fallback_catalog: Path | None = None) -> Visibility:
    """What a server started now would decide for `repository` (iss-00552 D-02): the summary and `todo list` use it."""
    return DashboardSite(state_root).visibility(repository.key, fallback_catalog)
