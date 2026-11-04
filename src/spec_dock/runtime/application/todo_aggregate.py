"""Human tasks of every catalog in this PC's registry (epic-00547 D-13〜D-15; iss-00550 D-01〜D-06).

`todo list --all-repositories`/`--repository`, `todo show <REF>`, and the `todos` counts of `dashboard summary`
and of the server's summary read the catalogs' `todos/` in place. They take no lock, write nothing and contact
neither GitHub nor a server. One repository's failure stays in its own row.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import os
from pathlib import Path
from typing import TYPE_CHECKING, Final

from spec_dock.runtime.application import todo_common
from spec_dock.runtime.application.todo_common import command_error, settings_warnings
from spec_dock.runtime.application.todo_list import classify, counts_of, normalize_scope, show_from_store
from spec_dock.runtime.domain.todo_model import Filters, matches, order, tally
from spec_dock.runtime.domain.todo_record import TodoError, normalize_id
from spec_dock.runtime.domain.todo_settings import resolve
from spec_dock.runtime.infra.canonical_registry import RegistryUnreadable, read_registry
from spec_dock.runtime.infra.dashboard_files import read_hidden
from spec_dock.runtime.infra.github_structure import GithubRepository
from spec_dock.runtime.infra.state_root import resolve_state_root
from spec_dock.runtime.infra.todo_store import TodoStore
from spec_dock.runtime.infra.user_config import read_user_todo_settings
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, OperationResult
from spec_dock.runtime.presentation.todo_document import list_item, repository_row, todo_list_document

if TYPE_CHECKING:
    import argparse
    from datetime import datetime

    from spec_dock.runtime.application.todo_list import Classified
    from spec_dock.runtime.domain.canonical_sync_state import RegistryEntry, SyncRegistry
    from spec_dock.runtime.domain.todo_settings import Effective, Layer

UNREADABLE: Final = "TODO_REPOSITORY_UNREADABLE"
UNKNOWN: Final = "TODO_REPOSITORY_UNKNOWN"
DUPLICATE: Final = "TODO_REPOSITORY_DUPLICATE"
REGISTRY_UNREADABLE: Final = "TODO_REGISTRY_UNREADABLE"
LIST_STEP: Final = "spec-dock dashboard list"


# --- Choosing catalogs from the registry (D-01) ----------------------------------------------------------------


@dataclass(frozen=True)
class Selected:
    """One registry row; `chosen` is the catalog read instead when this row is a second clone."""

    entry: RegistryEntry
    repository: GithubRepository | None
    chosen: str | None = None

    @property
    def catalog(self) -> Path:
        return Path(self.entry.catalog)


def _parse(value: str | None) -> GithubRepository | None:
    if value is None:
        return None
    try:
        return GithubRepository.parse(value)
    except ValueError:
        return None


def select_catalogs(registry: SyncRegistry) -> tuple[Selected, ...]:
    """Every row by repository, main checkout and catalog; of two clones only the first is read (Epic D-14)."""
    rows = [(entry, _parse(entry.repository)) for entry in registry.catalogs]
    rows.sort(key=lambda row: (row[1] is None, row[1].key if row[1] else "", row[0].main_checkout, row[0].catalog))
    chosen: dict[str, str] = {}
    selected: list[Selected] = []
    for entry, repository in rows:
        if repository is not None and repository.key in chosen:
            selected.append(Selected(entry, repository, chosen[repository.key]))
            continue
        if repository is not None:
            chosen[repository.key] = entry.catalog
        selected.append(Selected(entry, repository))
    return tuple(selected)


def catalog_for(registry: SyncRegistry, repository: GithubRepository) -> Selected | None:
    return next(
        (
            row
            for row in select_catalogs(registry)
            if row.chosen is None and row.repository is not None and row.repository.key == repository.key
        ),
        None,
    )


def registry_or_stop(state_root: Path) -> SyncRegistry:
    try:
        return read_registry(state_root)
    except RegistryUnreadable as error:
        raise TodoError(
            REGISTRY_UNREADABLE,
            f"the catalog registry {error.path} cannot be read: {error.reason}",
            details={"path": str(error.path), "reason": error.reason},
            next_step="spec-dock canonical status",
        ) from error


# --- Reading one catalog (D-02) --------------------------------------------------------------------------------


@dataclass(frozen=True)
class CatalogRead:
    store: TodoStore
    problem: dict[str, object] | None
    classified: Classified | None
    settings: Effective | None

    @property
    def readable(self) -> bool:
        return self.problem is None


def unreadable_problem(catalog: Path, main_checkout: str, reason: str) -> dict[str, object]:
    return {
        "code": UNREADABLE,
        "message": f"the catalog {catalog} cannot be read: {reason}",
        "next_step": f"spec-dock --project {main_checkout} canonical link",
    }


def read_catalog(catalog: Path, main_checkout: str, *, user_layer: Layer | None) -> CatalogRead:
    """The catalog's records, or why it cannot be read; a missing `todos/` is simply empty."""
    store = TodoStore(catalog)
    try:
        if not catalog.is_dir():
            return CatalogRead(store, unreadable_problem(catalog, main_checkout, "it is not a directory"), None, None)
        with os.scandir(catalog):
            pass
        if store.root.exists() and not store.root.is_dir():
            return CatalogRead(
                store, unreadable_problem(catalog, main_checkout, "todos is not a directory"), None, None
            )
        read = store.read_all()
    except OSError as error:
        return CatalogRead(store, unreadable_problem(catalog, main_checkout, error.strerror or str(error)), None, None)
    settings = resolve((user_layer, store.read_settings())) if user_layer is not None else None
    return CatalogRead(store, None, classify(store, read), settings)


# --- todo list --all-repositories / --repository (D-04) ---------------------------------------------------------


def parse_repository(value: str) -> GithubRepository:
    try:
        return GithubRepository.parse(value)
    except ValueError as error:
        raise TodoError(
            "TODO_REPOSITORY_INVALID",
            f"{value!r} is not owner/name or github.com/owner/name",
            exit_code=2,
            details={"repository": value},
        ) from error


def _with_repository(warning: Diagnostic, repository: GithubRepository | None) -> Diagnostic:
    return replace(warning, details={**warning.details, "repository": repository.key if repository else None})


def list_all(namespace: argparse.Namespace, cwd: Path) -> OperationResult[object] | None:
    """Only with --all-repositories or --repository; otherwise the checkout's `todo list` answers."""
    del cwd
    if not namespace.all_repositories and not namespace.repository:
        return None
    try:
        return _list_all(namespace)
    except TodoError as error:
        raise command_error(error) from error


def _list_all(namespace: argparse.Namespace) -> OperationResult[object]:
    wanted = tuple(dict.fromkeys(parse_repository(value).key for value in namespace.repository or ()))
    filters = Filters(
        status=namespace.status,
        scope=normalize_scope(namespace.scope) if namespace.scope else None,
        kind=namespace.kind,
        tag=namespace.tag,
        blocking=namespace.blocking,
        overdue=namespace.overdue,
        repositories=wanted,
    )
    state_root = resolve_state_root()
    registry = registry_or_stop(state_root)
    now = todo_common.utc_now()
    user_layer = read_user_todo_settings()
    rows: list[dict[str, object]] = []
    pool: list[tuple[dict[str, object], dict[str, object]]] = []  # (record, list item)
    warnings: list[Diagnostic] = list(settings_warnings((user_layer,)))
    seen: set[str] = set()
    for row in select_catalogs(registry):
        repository = row.repository
        if wanted and (repository is None or repository.key not in wanted):
            continue
        if repository is not None:
            seen.add(repository.key)
        key = repository.key if repository is not None else None
        hidden = read_hidden(state_root, repository) if repository is not None else False
        place: dict[str, object] = {"catalog": row.entry.catalog, "main_checkout": row.entry.main_checkout}
        catalog, checkout = row.entry.catalog, row.entry.main_checkout
        if row.chosen is not None:
            problem: dict[str, object] = {
                "code": DUPLICATE,
                "message": f"{row.entry.catalog} is a second clone of {key}; {row.chosen} is read",
                "next_step": LIST_STEP,
            }
            rows.append(
                repository_row(
                    repository=key,
                    catalog=catalog,
                    main_checkout=checkout,
                    hidden=hidden,
                    status="duplicate",
                    problem=problem,
                )
            )
            warnings.append(
                Diagnostic(DUPLICATE, str(problem["message"]), {"catalog": row.entry.catalog, "chosen": row.chosen})
            )
            continue
        read = read_catalog(row.catalog, row.entry.main_checkout, user_layer=user_layer)
        if read.problem is not None or read.classified is None or read.settings is None:
            problem = read.problem or {}
            rows.append(
                repository_row(
                    repository=key,
                    catalog=catalog,
                    main_checkout=checkout,
                    hidden=hidden,
                    status="unreadable",
                    problem=problem,
                )
            )
            warnings.append(
                Diagnostic(UNREADABLE, str(problem.get("message")), {**problem, "repository": key, **place})
            )
            continue
        classified = read.classified
        records = [item.record for item in classified.valid]
        rows.append(
            repository_row(
                repository=key,
                catalog=catalog,
                main_checkout=checkout,
                hidden=hidden,
                status="ok",
                problem=None,
                counts=counts_of(records, read.settings, now),
                invalid_files=list(classified.invalid_files),
                conflict_copies=list(classified.conflict_copies),
            )
        )
        warnings.extend(_with_repository(item, repository) for item in classified.warnings)
        warnings.extend(item for item in settings_warnings(read.settings.layers) if item.details["layer"] != "user")
        for stored in classified.valid:
            if matches(stored.record, filters, now):
                item = list_item(stored.record, now=now, repository=repository, path=read.store.relative(stored.path))
                pool.append((stored.record, item))
    for key in wanted:
        if key not in seen:
            warnings.append(
                Diagnostic(
                    UNKNOWN,
                    f"{key} is not in this PC's catalog registry",
                    {"repository": key, "next_step": LIST_STEP},
                )
            )
    by_record = {id(record): item for record, item in pool}
    items = [by_record[id(record)] for record in order([record for record, _item in pool], now)]
    document = todo_list_document(
        now=now, filters=filters.to_json(), repositories=rows, items=items, mode="all_repositories"
    )
    return OperationResult(
        namespace.command_path, "succeeded", FamilyData("todo", document), 0, warnings=tuple(warnings)
    )


# --- todo show <REF> (D-05) ------------------------------------------------------------------------------------


def show_ref(namespace: argparse.Namespace, cwd: Path) -> OperationResult[object] | None:
    """Only for `owner/name/t-xxxx` (or `github.com/owner/name/t-xxxx`); a bare ID needs the checkout."""
    del cwd
    if "/" not in namespace.id:
        return None
    try:
        return _show_ref(namespace)
    except TodoError as error:
        raise command_error(error) from error


def _show_ref(namespace: argparse.Namespace) -> OperationResult[object]:
    named, _, raw_id = namespace.id.strip().rpartition("/")
    repository = parse_repository(named)
    todo_id = normalize_id(raw_id)
    state_root = resolve_state_root()
    selected = catalog_for(registry_or_stop(state_root), repository)
    if selected is None:
        raise TodoError(
            UNKNOWN,
            f"{repository.key} is not in this PC's catalog registry",
            details={"repository": repository.key},
            next_step=LIST_STEP,
        )
    read = read_catalog(selected.catalog, selected.entry.main_checkout, user_layer=None)
    if read.problem is not None:
        raise TodoError(
            UNREADABLE,
            str(read.problem["message"]),
            details={"repository": repository.key, "catalog": selected.entry.catalog},
            next_step=str(read.problem["next_step"]),
        )
    view, warnings = show_from_store(read.store, repository, todo_id, now=todo_common.utc_now())
    return OperationResult(namespace.command_path, "succeeded", FamilyData("todo", view), 0, warnings=warnings)


# --- dashboard summary's `todos` (D-06) ------------------------------------------------------------------------


def _unavailable(problem: dict[str, object]) -> dict[str, object]:
    return {"status": "unavailable", "open": None, "blocking": None, "overdue": None, "problem": problem}


def summary_todos(catalog: Path, main_checkout: str, *, now: datetime) -> dict[str, object]:
    """Open (snoozed included), blocking and overdue parent tasks of one catalog (Epic D-15)."""
    read = read_catalog(catalog, main_checkout, user_layer=None)
    if read.problem is not None or read.classified is None:
        return _unavailable(read.problem or {})
    counts = tally([item.record for item in read.classified.valid], now)
    return {
        "status": "ok",
        "open": counts["open"],
        "blocking": counts["blocking"],
        "overdue": counts["overdue"],
        "problem": None,
    }


def registry_summary_todos(state_root: Path, repository: GithubRepository, *, now: datetime) -> dict[str, object]:
    """The counts of the repository's catalog chosen from the registry the way `todo list` chooses it."""
    try:
        registry = read_registry(state_root)
    except RegistryUnreadable as error:
        return _unavailable({
            "code": REGISTRY_UNREADABLE,
            "message": f"the catalog registry {error.path} cannot be read: {error.reason}",
            "next_step": "spec-dock canonical status",
        })
    selected = catalog_for(registry, repository)
    if selected is None:
        return _unavailable({
            "code": UNKNOWN,
            "message": f"{repository.key} is not in this PC's catalog registry",
            "next_step": "spec-dock canonical link",
        })
    return summary_todos(selected.catalog, selected.entry.main_checkout, now=now)
