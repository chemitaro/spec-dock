"""The dashboard server's reading of human tasks (iss-00554 D-02, D-03; epic-00547 D-16).

The server only reads the catalogs' `todos/`, with the functions of `todo list --all-repositories` (iss-00550), and
writes nothing. Each catalog's reading is remembered with the times of `todos/`, its month directories,
`settings.json` and the user's settings file, and read again only when one of them changes. One repository's
failure stays in its own row or response.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import threading
from typing import TYPE_CHECKING, Final

from spec_dock.runtime.application.todo_aggregate import (
    UNKNOWN,
    CatalogRead,
    Selected,
    collect,
    read_catalog,
    select_catalogs,
)
from spec_dock.runtime.application.todo_list import show_from_store
from spec_dock.runtime.domain.canonical_sync_state import SyncRegistry
from spec_dock.runtime.domain.todo_model import Filters, derived, order, scope_marks, tally
from spec_dock.runtime.domain.todo_record import CLOSED, STATUSES, normalize_id
from spec_dock.runtime.infra.todo_store import TodoStore
from spec_dock.runtime.infra.user_config import read_user_todo_settings, user_config_path
from spec_dock.runtime.presentation.todo_document import repository_row, todo_list_document, todo_ref

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence
    from datetime import datetime
    from pathlib import Path

    from spec_dock.runtime.application.dashboard_site import SiteRepository
    from spec_dock.runtime.domain.canonical_sync_state import RegistryEntry
    from spec_dock.runtime.domain.dashboard_model import DashboardModel

STATUS_VALUES: Final = frozenset({*STATUSES, "all"})
_Signature = tuple[int, int] | None
ZERO: Final = {"blocking": 0, "blocking_with_descendants": 0, "related": 0}


class TodoFilterInvalid(ValueError):
    """An unknown `status` value of the task API (400 DASHBOARD_TODO_FILTER_INVALID)."""


def _signature(path: Path) -> _Signature:
    try:
        info = path.stat()
    except OSError:
        return None
    return (info.st_mtime_ns, info.st_size)


def files_signature(catalog: Path) -> tuple[object, ...]:
    """`todos/`, each month directory and `settings.json`: a record is written by a rename inside its month."""
    root = TodoStore(catalog).root
    months: list[tuple[str, _Signature]] = []
    try:
        if root.is_dir():
            months = [(entry.name, _signature(entry)) for entry in sorted(root.iterdir()) if entry.is_dir()]
    except OSError:
        months = [("?", None)]
    return (_signature(root), tuple(months), _signature(root / "settings.json"))


def parse_status(value: str | None) -> str:
    status = value or "open"
    if status not in STATUS_VALUES:
        raise TodoFilterInvalid(status)
    return status


def _unreadable_row(entry: RegistryEntry | None, key: str, problem: dict[str, object]) -> dict[str, object]:
    return repository_row(
        repository=key,
        catalog=entry.catalog if entry is not None else "",
        main_checkout=entry.main_checkout if entry is not None else "",
        hidden=False,
        status="unreadable",
        problem=problem,
    )


@dataclass(frozen=True)
class Annotations:
    """What the structure and scope responses add: the summary, each Scope's marks and the task records."""

    summary: dict[str, object]
    marks: dict[str, dict[str, int]]
    records: tuple[dict[str, object], ...]
    repository: str
    ref_of: Callable[[str], str | None]

    @property
    def readable(self) -> bool:
        return self.summary.get("status") == "ok"

    def scope_lists(self, model: DashboardModel, scope_id: str, now: datetime) -> dict[str, object]:
        """Open tasks blocking the Scope, blocking only its descendants, and related to it (iss-00554 D-03)."""
        if not self.readable:
            return {
                "status": "unavailable",
                "problem": self.summary.get("problem"),
                "blocking": [],
                "related": [],
                "descendants": [],
            }
        below = _descendants(model, scope_id)
        blocking: list[dict[str, object]] = []
        related: list[dict[str, object]] = []
        descendants: list[dict[str, object]] = []
        for record in self.records:
            if record.get("status") in CLOSED:
                continue
            blocks, links = _scopes(record, "blocks"), _scopes(record, "related")
            if scope_id in blocks:
                blocking.append(record)
            elif below.intersection(blocks):
                descendants.append(record)
            if scope_id in links:
                related.append(record)
        view = lambda records: [self._item(record, now) for record in order(records, now)]  # noqa: E731
        return {
            "status": "ok",
            "problem": None,
            "blocking": view(blocking),
            "related": view(related),
            "descendants": view(descendants),
        }

    def _item(self, record: Mapping[str, object], now: datetime) -> dict[str, object]:
        state = derived(record, now)
        todo_id = str(record.get("id"))
        return {
            "ref": self.ref_of(todo_id),
            "repository": self.repository,
            "id": todo_id,
            "title": record.get("title"),
            "kind": record.get("kind"),
            "due": record.get("due"),
            "overdue": state["overdue"],
            "due_soon": state["due_soon"],
            "effective_status": state["effective_status"],
            "blocks": _scopes(record, "blocks"),
            "related": _scopes(record, "related"),
        }


def _scopes(record: Mapping[str, object], key: str) -> list[str]:
    scopes = record.get("scopes")
    values = scopes.get(key) if isinstance(scopes, dict) else None
    return [value for value in values if isinstance(value, str)] if isinstance(values, list) else []


def _descendants(model: DashboardModel, scope_id: str) -> set[str]:
    found: set[str] = set()
    stack = list(model.scopes[scope_id].children) if scope_id in model.scopes else []
    while stack:
        current = stack.pop()
        if current in found or current not in model.scopes:
            continue
        found.add(current)
        stack.extend(model.scopes[current].children)
    return found


def unavailable(problem: Mapping[str, object] | None) -> dict[str, object]:
    return {"status": "unavailable", "open": None, "blocking": None, "overdue": None, "problem": dict(problem or {})}


class DashboardTodos:
    def __init__(self, entries: Callable[[], Sequence[RegistryEntry]], *, now: Callable[[], datetime]) -> None:
        self._entries = entries
        self.now = now
        self._lock = threading.Lock()
        self._cache: dict[str, tuple[tuple[object, ...], CatalogRead]] = {}

    # --- Choosing and reading a catalog ---------------------------------------------------------------------

    def _selected(self, site: SiteRepository) -> Selected | None:
        """The registry row read for the repository; of two clones the first (as `todo list` chooses)."""
        rows = select_catalogs(SyncRegistry(None, tuple(self._entries())))
        return next(
            (
                row
                for row in rows
                if row.chosen is None and row.repository is not None and row.repository.key == site.key
            ),
            None,
        )

    def read(self, catalog: Path, main_checkout: str) -> CatalogRead:
        key = (files_signature(catalog), _signature(user_config_path()))
        with self._lock:
            cached = self._cache.get(str(catalog))
            if cached is not None and cached[0] == key:
                return cached[1]
        read = read_catalog(catalog, main_checkout, user_layer=read_user_todo_settings())
        with self._lock:
            self._cache[str(catalog)] = (key, read)
        return read

    def _site_read(self, site: SiteRepository) -> tuple[Selected | None, CatalogRead | None, dict[str, object] | None]:
        selected = self._selected(site)
        if selected is None:
            problem: dict[str, object] = {
                "code": UNKNOWN,
                "message": f"{site.key} is not in this PC's catalog registry",
                "next_step": "spec-dock canonical link",
            }
            return None, None, problem
        read = self.read(selected.catalog, selected.entry.main_checkout)
        return selected, read, read.problem

    # --- Lists (D-01, D-02) ---------------------------------------------------------------------------------

    def _document(self, sites: Sequence[SiteRepository], status: str, mode: str) -> dict[str, object]:
        now = self.now()
        filters = Filters(status=status)
        chosen: list[Selected] = []
        missing: list[dict[str, object]] = []
        for site in sites:
            selected = self._selected(site)
            if selected is None:
                missing.append(
                    _unreadable_row(
                        None,
                        site.key,
                        {
                            "code": UNKNOWN,
                            "message": f"{site.key} is not in this PC's catalog registry",
                            "next_step": "spec-dock canonical link",
                        },
                    )
                )
            else:
                chosen.append(selected)
        collected = collect(
            chosen, filters=filters, now=now, user_layer=None, hidden=lambda _repository: False, read=self.read
        )
        rows = sorted([*collected.rows, *missing], key=lambda row: str(row["repository"]))
        return todo_list_document(
            now=now, filters=filters.to_json(), repositories=rows, items=collected.items, mode=mode
        )

    def list_document(self, sites: Sequence[SiteRepository], status: str) -> dict[str, object]:
        return self._document(sites, status, "all_repositories")

    def repository_document(self, site: SiteRepository, status: str) -> dict[str, object]:
        return self._document([site], status, "repository")

    def one(self, site: SiteRepository, raw_id: str) -> dict[str, object]:
        """One task's result like `todo show`; TodoError (or LookupError for the catalog) for the caller to map."""
        todo_id = normalize_id(raw_id)
        selected, read, problem = self._site_read(site)
        if selected is None or read is None or problem is not None:
            raise CatalogUnreadable(problem or {})
        view, _warnings = show_from_store(read.store, selected.repository, todo_id, now=self.now())
        return view

    # --- Marks and revision (D-03, D-04) --------------------------------------------------------------------

    def annotations(self, site: SiteRepository, model: DashboardModel | None) -> Annotations:
        repository = site.repository
        ref_of = lambda todo_id: todo_ref(repository, todo_id)  # noqa: E731
        try:
            _selected, read, problem = self._site_read(site)
        except Exception as error:  # the structure is still drawn (F-01)
            problem, read = (
                {
                    "code": "TODO_READ_FAILED",
                    "message": f"{type(error).__name__}: {error}",
                    "next_step": "spec-dock todo check",
                },
                None,
            )
        if problem is not None or read is None or read.classified is None:
            return Annotations(unavailable(problem), {}, (), site.key, ref_of)
        records = tuple(item.record for item in read.classified.valid)
        counts = tally(records, self.now())
        summary: dict[str, object] = {
            "status": "ok",
            "open": counts["open"],
            "blocking": counts["blocking"],
            "overdue": counts["overdue"],
            "problem": None,
        }
        parents = {scope.id: scope.parent_id for scope in model.scopes.values()} if model is not None else {}
        return Annotations(summary, scope_marks(records, parents), records, site.key, ref_of)

    def signature(self, site: SiteRepository) -> str:
        """The files' times and, from the remembered records, what the clock decides (overdue, due soon, the end of
        a snooze), so a passing due changes the revision without any write."""
        try:
            selected, read, problem = self._site_read(site)
            if selected is None or read is None:
                return repr(("none", problem))
            now = self.now()
            states = tuple(
                (
                    item.record.get("id"),
                    *(derived(item.record, now)[key] for key in ("effective_status", "overdue", "due_soon")),
                )
                for item in (read.classified.valid if read.classified is not None else ())
            )
            parts: tuple[object, ...] = (
                str(selected.catalog),
                files_signature(selected.catalog),
                _signature(user_config_path()),
                problem,
                states,
            )
        except Exception as error:
            parts = ("error", type(error).__name__)
        return hashlib.sha256(repr(parts).encode()).hexdigest()[:16]

    def revision(self, sites: Sequence[SiteRepository], listing: object) -> str:
        parts = (listing, tuple((site.key, self.signature(site)) for site in sites))
        return hashlib.sha256(repr(parts).encode()).hexdigest()[:16]


class CatalogUnreadable(LookupError):
    def __init__(self, problem: Mapping[str, object]) -> None:
        super().__init__(str(problem.get("message", "the catalog cannot be read")))
        self.problem = dict(problem)
