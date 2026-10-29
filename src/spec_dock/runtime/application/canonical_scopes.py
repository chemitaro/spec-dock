"""Shared reading side of canonical-mode commands: the structure snapshot as legacy-shaped Scope views.

Structure (titles, kinds, states, parents, dependencies) comes from the structure snapshot at display freshness
(C10); a Scope's directory is always `<catalog>/<bucket>/<ID>` (C3). Views carry `.meta.json`-free values in the legacy
`ScopeView` shape so the unchanged legacy helpers (selection, expectations, listing, navigation links, Artifact
listing) work on them. A view's path goes through this checkout's `spec-dock/initiatives` link and is never
resolved, so paths relative to `spec-dock/` stay `initiatives/<bucket>/<ID>`.

A GitHub kind-label change moves a number to another ID while its catalog directory keeps the old name; such a
Scope is SCOPE_KIND_CHANGED (Epic design ch. 2): reads warn, branch and selection writes stop, and an old ID
never resolves (it names the current ID instead of SCOPE_NOT_FOUND).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from spec_dock.runtime.application.canonical_catalog import require_linked
from spec_dock.runtime.application.canonical_errors import SCOPE_KIND_CHANGED_RECOVERY, CanonicalCommandError
from spec_dock.runtime.application.scope_expectations import check_scope_expectations
from spec_dock.runtime.application.scope_query import ScopeView, _sort_key
from spec_dock.runtime.application.worktree_observation import read_selection, resolve_scope
from spec_dock.runtime.domain.canonical_layout import LINK_RELATIVE, scope_relative
from spec_dock.runtime.domain.canonical_structure import (
    SCOPE_KIND_CHANGED,
    KindChange,
    kind_changes,
    parse_scope_id,
    renamed_scope,
)
from spec_dock.runtime.domain.lifecycle import GithubBackend, StatusObservation, observe_github_state
from spec_dock.runtime.domain.selectors import ScopeIdSelector, parse_scope_selector
from spec_dock.runtime.infra.git_process import GitProcessError
from spec_dock.runtime.infra.github_snapshot import (
    GITHUB_SNAPSHOT_STALE,
    FreshSnapshot,
    SnapshotStore,
    SnapshotWarning,
    StructureSnapshotService,
)
from spec_dock.runtime.infra.github_structure import GithubApi, GithubStructureClient, repository_for_checkout
from spec_dock.runtime.infra.state_root import resolve_state_root
from spec_dock.runtime.infra.work_target_store import WorkTargetStore
from spec_dock.runtime.presentation.envelope import Diagnostic

if TYPE_CHECKING:
    import argparse
    from collections.abc import Callable, Mapping
    from pathlib import Path

    from spec_dock.runtime.application.canonical_catalog import LinkedCatalog
    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.worktree_observation import SelectionObservation
    from spec_dock.runtime.domain.canonical_structure import ScopeNode, StructureSnapshot
    from spec_dock.runtime.infra.catalog_tree import ScopeDirectory
    from spec_dock.runtime.infra.github_structure import GithubRepository
    from spec_dock.runtime.infra.work_target_store import StoredSelection

    ServiceFactory = Callable[[GithubRepository, Path, float], StructureSnapshotService]

OFFLINE_MESSAGE: Final = "offline mode cannot fetch required GitHub state"


def default_service(repository: GithubRepository, root: Path, timeout: float) -> StructureSnapshotService:
    api = GithubApi(timeout=timeout, cwd=root)
    return StructureSnapshotService(
        repository,
        store=SnapshotStore(resolve_state_root(), repository),
        client=GithubStructureClient(repository, api),
        clock=api.clock,
    )


@dataclass(frozen=True)
class CanonicalScopes:
    context: ProjectContext
    repository: GithubRepository
    fresh: FreshSnapshot
    snapshot: StructureSnapshot
    views: tuple[ScopeView, ...]
    catalog: LinkedCatalog | None
    directories: Mapping[str, ScopeDirectory]
    kind_changes: Mapping[int, KindChange]

    def node(self, scope_id: str) -> ScopeNode:
        found = self.snapshot.find(scope_id)
        if found is None:
            raise LookupError(f"{scope_id} is not in the structure snapshot")
        return found

    def view(self, scope_id: str) -> ScopeView:
        for view in self.views:
            if view.id == scope_id:
                return view
        raise LookupError(f"{scope_id} is not in the structure snapshot")

    def directory(self, scope_id: str) -> ScopeDirectory | None:
        return self.directories.get(scope_id)

    def require_directory(self, scope_id: str) -> Path:
        """The Scope's directory through this checkout's link; a missing one is LOCAL_TARGET_NOT_FOUND."""
        if self.directory(scope_id) is None:
            raise FileNotFoundError(f"{scope_id} has no directory in the catalog")
        return self.view(scope_id).path

    def payload(self, view: ScopeView) -> dict[str, object]:
        """The legacy `scope_payload` keys plus GitHub facts; path is null when the catalog has no directory."""
        node = self.node(view.id)
        found = view.id in self.directories
        return {
            "id": view.id,
            "kind": view.kind,
            "title": view.title,
            "parent_id": view.parent_id,
            "backend": view.backend.kind,
            "github_ref": view.github_ref,
            "path": view.path.relative_to(self.context.root).as_posix() if found else None,
            "revision": None,
            "status": {
                "state": view.status.state,
                "authority": view.status.authority,
                "source": view.status.source,
                "observed_at": view.status.observed_at,
            },
            "number": node.number,
            "url": node.url,
            "state_reason": node.state_reason,
            "in_progress": node.in_progress,
            "directory_found": found,
        }

    def snapshot_payload(self) -> dict[str, object]:
        return {**self.fresh.payload(), "repository": self.repository.key}

    def lineage(self, scope_id: str) -> tuple[str, ...]:
        """The Scope and its GitHub ancestors' IDs, nearest first; it stops at a missing, undecided or looping parent.

        Unlike the validated ancestor chain it never fails, so a kind change of an ancestor is still found.
        """
        found: list[str] = []
        node = self.snapshot.find(scope_id)
        while node is not None and node.id is not None and node.id not in found:
            found.append(node.id)
            node = self.snapshot.issues.get(node.parent) if node.parent is not None else None
        return tuple(found)

    def require_kind_unchanged(self, *scope_ids: str) -> None:
        """Stop (exit 3) before a write when GitHub moved one of these Scopes to another kind."""
        for scope_id in scope_ids:
            change = self.kind_changes.get(parse_scope_id(scope_id)[1])
            if change is not None:
                raise kind_change_error(change)

    def snapshot_warnings(self) -> tuple[Diagnostic, ...]:
        warning = self.fresh.warning
        return () if warning is None else (Diagnostic(warning.code, warning.message, dict(warning.details)),)

    def kind_change_warnings(self) -> tuple[Diagnostic, ...]:
        return tuple(
            Diagnostic(SCOPE_KIND_CHANGED, _kind_change_message(change), _kind_change_details(change))
            for change in self.kind_changes.values()
        )

    def warnings(self) -> tuple[Diagnostic, ...]:
        """What a reading command shows: a stale snapshot and every kind change, without changing the result."""
        return (*self.snapshot_warnings(), *self.kind_change_warnings())


def _kind_change_message(change: KindChange) -> str:
    return (
        f"GitHub now gives #{change.number} the ID {change.current_id}, but the catalog keeps "
        f"{', '.join(change.directories) or 'its old ID'}; SpecDock never renames it"
    )


def _kind_change_details(change: KindChange, requested: str | None = None) -> dict[str, object]:
    details: dict[str, object] = {
        "scope_id": change.current_id,
        "number": change.number,
        "current_id": change.current_id,
        "directories": list(change.directories),
    }
    if requested is not None:
        details["requested"] = requested
    return {**details, "next_step": SCOPE_KIND_CHANGED_RECOVERY}


def kind_change_error(change: KindChange, *, requested: str | None = None) -> CanonicalCommandError:
    return CanonicalCommandError(
        SCOPE_KIND_CHANGED,
        _kind_change_message(change)
        if requested is None
        else f"{requested} is no longer an ID: GitHub now gives #{change.number} the ID {change.current_id}",
        recovery=(SCOPE_KIND_CHANGED_RECOVERY,),
        details=_kind_change_details(change, requested),
    )


def resolve_canonical_scope(
    context: ProjectContext, scopes: CanonicalScopes, target: str, *, selection: SelectionObservation | None = None
) -> ScopeView:
    """Today's selector resolution, except that an old ID of a re-kinded number is SCOPE_KIND_CHANGED."""
    refuse_old_ids(scopes, target)
    return resolve_scope(context, scopes.views, target, selection=selection)


def refuse_old_ids(scopes: CanonicalScopes, *targets: str | None) -> None:
    """Stop with SCOPE_KIND_CHANGED on an ID selector whose number GitHub now gives another kind.

    The selector is normalized as today (`iss-454` is `iss-00454`), so every spelling of an old ID is caught.
    """
    for target in targets:
        if target is None:
            continue
        try:
            selector = parse_scope_selector(target)
        except ValueError:
            continue  # resolution reports the invalid selector as today
        if not isinstance(selector, ScopeIdSelector):
            continue
        node = renamed_scope(scopes.snapshot, selector.id)
        if node is not None and node.id is not None:
            known = scopes.kind_changes.get(node.number)
            directories = known.directories if known is not None else ()
            raise kind_change_error(KindChange(node.number, node.id, directories), requested=selector.id)


def check_canonical_scope_expectations(
    context: ProjectContext,
    scopes: CanonicalScopes,
    selection: SelectionObservation | None,
    *,
    target: ScopeView | None,
    expected_current: str | None,
    expected_backend: str | None,
) -> None:
    """Today's --expect-current/--expect-backend check, after refusing an old ID in --expect-current."""
    refuse_old_ids(scopes, expected_current)
    check_scope_expectations(
        context,
        scopes.views,
        selection,
        target=target,
        expected_current=expected_current,
        expected_backend=expected_backend,
    )


def load_canonical_scopes(
    context: ProjectContext,
    *,
    timeout: float,
    link: bool,
    refresh: bool = False,
    offline: bool = False,
    service_factory: ServiceFactory = default_service,
) -> CanonicalScopes:
    """Check the link first (local, before any network), then read the snapshot at display freshness.

    Without `link`, a correct link is still used for directories but its absence does not stop the read.
    `offline` sends nothing to GitHub and shows the stored snapshot as stale.
    """
    if offline and refresh:
        raise ValueError(OFFLINE_MESSAGE)
    if link:
        catalog: LinkedCatalog | None = require_linked(context, timeout=timeout)
    else:
        try:
            catalog = require_linked(context, timeout=timeout)
        except (CanonicalCommandError, GitProcessError, OSError):
            catalog = None
    repository = repository_for_checkout(context.root, timeout=timeout)
    service = service_factory(repository, context.root, timeout)
    if offline:
        stored, _probe = service.store.load()
        if stored is None:
            raise ValueError(OFFLINE_MESSAGE)
        fresh = FreshSnapshot(
            stored,
            True,
            "skipped",
            False,
            SnapshotWarning(
                GITHUB_SNAPSHOT_STALE,
                f"showing the structure snapshot fetched at {stored.fetched_at}; --offline sends nothing to GitHub",
                {"fetched_at": stored.fetched_at, "cause": "offline"},
            ),
        )
    else:
        fresh = service.refresh() if refresh else service.ensure_fresh("display")
    return build_canonical_scopes(context, repository, fresh, catalog)


def build_canonical_scopes(
    context: ProjectContext, repository: GithubRepository, fresh: FreshSnapshot, catalog: LinkedCatalog | None
) -> CanonicalScopes:
    """The one place that pairs a checked snapshot with the catalog: views, directories and kind changes.

    Without a catalog there are no directories and no kind changes (an old ID is still decided by the snapshot).
    """
    snapshot = fresh.require()
    directories: dict[str, ScopeDirectory] = {}
    changes: Mapping[int, KindChange] = {}
    if catalog is not None:
        known = {node.id for node in snapshot.scopes}
        found = catalog.tree.directories()
        directories = {item.scope_id: item for item in found if item.scope_id in known}
        changes = kind_changes(snapshot, (item.scope_id for item in found))
    views = build_views(context.root, repository, fresh, snapshot)
    return CanonicalScopes(context, repository, fresh, snapshot, views, catalog, directories, changes)


def build_views(
    root: Path, repository: GithubRepository, fresh: FreshSnapshot, snapshot: StructureSnapshot
) -> tuple[ScopeView, ...]:
    """Every Scope's path is `<root>/spec-dock/initiatives/<bucket>/<ID>`, whether or not its directory exists yet."""
    link = root / LINK_RELATIVE
    views: list[ScopeView] = []
    for node in snapshot.scopes:
        if node.id is None or node.kind is None:
            continue  # `scopes` holds only decided Scopes; anomalies are reported elsewhere
        parent = snapshot.issues.get(node.parent) if node.parent is not None else None
        views.append(
            ScopeView(
                id=node.id,
                kind=node.kind,
                title=node.title,
                parent_id=parent.id if parent is not None else None,
                backend=GithubBackend(node.number, repository.owner, repository.name),
                path=link / scope_relative(node.id),
                revision=0,
                status=StatusObservation(
                    observe_github_state(node.state, node.state_reason),
                    "github",
                    "cache",
                    snapshot.fetched_at,
                    node.updated_at,
                    fresh.stale,
                ),
                github_ref=f"gh:{repository.owner}/{repository.name}#{node.number}",
            )
        )
    return tuple(sorted(views, key=_sort_key))


def check_canonical_expectation(
    context: ProjectContext,
    namespace: argparse.Namespace,
    *,
    stored: StoredSelection | None = None,
    refuse_kind_changed: bool = False,
) -> tuple[Diagnostic, ...]:
    """--expect-current against the structure snapshot; no catalog or link is needed.

    Returns the kind-change warnings a reading command shows; `refuse_kind_changed` stops on the expected Scope.
    """
    if namespace.expect_current is None:
        return ()
    scopes = load_canonical_scopes(
        context, timeout=namespace.timeout, link=False, offline=bool(getattr(namespace, "offline", False))
    )
    if stored is None:
        with WorkTargetStore(context.root) as store:
            stored = store.read()
    selected = read_selection(context, scopes.views, stored=stored)
    expected = resolve_canonical_scope(context, scopes, namespace.expect_current, selection=selected).id
    if refuse_kind_changed:
        scopes.require_kind_unchanged(expected)
    if selected.status != "selected" or selected.record is None or selected.record.scope_id != expected:
        raise ValueError("direct target does not match --expect-current")
    return scopes.kind_change_warnings()
