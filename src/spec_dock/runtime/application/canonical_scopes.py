"""Shared reading side of canonical-mode commands: the structure snapshot as legacy-shaped Scope views.

Structure (titles, kinds, states, parents, dependencies) comes from the structure snapshot at display freshness
(C10); Scope directories come from the catalog by name (C3). Views carry `.meta.json`-free values in the legacy
`ScopeView` shape so the unchanged legacy helpers (selection, expectations, listing, navigation links, Artifact
listing) work on them. A view's path goes through this checkout's `spec-dock/initiatives` link and is never
resolved, so paths relative to `spec-dock/` stay `initiatives/<catalog relative path>`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Final

from spec_dock.runtime.application.canonical_catalog import require_linked
from spec_dock.runtime.application.canonical_errors import CanonicalCommandError
from spec_dock.runtime.application.scope_query import ScopeView, _sort_key
from spec_dock.runtime.application.worktree_observation import read_selection, resolve_scope
from spec_dock.runtime.domain.canonical_layout import LINK_RELATIVE
from spec_dock.runtime.domain.lifecycle import GithubBackend, StatusObservation, observe_github_state
from spec_dock.runtime.infra.catalog_tree import ScopeDirectoryAmbiguous
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

    from spec_dock.runtime.application.canonical_catalog import LinkedCatalog
    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.domain.canonical_structure import ScopeNode, StructureSnapshot
    from spec_dock.runtime.infra.catalog_tree import ScopeDirectory
    from spec_dock.runtime.infra.github_structure import GithubRepository
    from spec_dock.runtime.infra.work_target_store import StoredSelection

    ServiceFactory = Callable[[GithubRepository, Path, float], StructureSnapshotService]

OFFLINE_MESSAGE: Final = "offline mode cannot fetch required GitHub state"
# The catalog directory that holds a Scope kind under its parent's directory (Epic design ch. 2).
SCOPE_NESTING: Final[Mapping[str, str]] = {"epic": "epics", "issue": "issues"}


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
    ambiguous: Mapping[str, tuple[ScopeDirectory, ...]]

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
        if scope_id in self.ambiguous:
            raise ScopeDirectoryAmbiguous(scope_id, self.ambiguous[scope_id])
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

    def warnings(self) -> tuple[Diagnostic, ...]:
        warning = self.fresh.warning
        return () if warning is None else (Diagnostic(warning.code, warning.message, dict(warning.details)),)


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
    return assemble_canonical_scopes(context, repository, fresh, catalog)


def assemble_canonical_scopes(
    context: ProjectContext, repository: GithubRepository, fresh: FreshSnapshot, catalog: LinkedCatalog | None
) -> CanonicalScopes:
    """Scope views and catalog directories for an already checked snapshot (reading and writing sides alike)."""
    snapshot = fresh.require()
    directories: dict[str, ScopeDirectory] = {}
    ambiguous: dict[str, tuple[ScopeDirectory, ...]] = {}
    if catalog is not None:
        known = {node.id for node in snapshot.scopes}
        ambiguous = {key: value for key, value in catalog.tree.duplicates().items() if key in known}
        directories = {
            item.scope_id: item
            for item in catalog.tree.directories()
            if item.scope_id in known and item.scope_id not in ambiguous
        }
    views = build_views(context.root, repository, fresh, snapshot, directories)
    return CanonicalScopes(context, repository, fresh, snapshot, views, catalog, directories, ambiguous)


def build_views(
    root: Path,
    repository: GithubRepository,
    fresh: FreshSnapshot,
    snapshot: StructureSnapshot,
    directories: Mapping[str, ScopeDirectory],
) -> tuple[ScopeView, ...]:
    link = root / LINK_RELATIVE
    relatives: dict[str, PurePosixPath] = {}

    def relative(node: ScopeNode, scope_id: str) -> PurePosixPath:
        if scope_id in relatives:
            return relatives[scope_id]
        found = directories.get(scope_id)
        if found is not None:
            result = found.relative
        else:
            name = PurePosixPath(f"{scope_id}-{node.slug}")
            parent = snapshot.issues.get(node.parent) if node.parent is not None else None
            nested = SCOPE_NESTING.get(node.kind or "")
            if parent is not None and parent.id is not None and nested is not None:
                relatives[scope_id] = name  # a parent cycle ends here
                result = relative(parent, parent.id) / nested / name
            else:
                result = name
        relatives[scope_id] = result
        return result

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
                path=link / relative(node, node.id),
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
) -> None:
    """--expect-current against the structure snapshot; no catalog or link is needed."""
    if namespace.expect_current is None:
        return
    scopes = load_canonical_scopes(
        context, timeout=namespace.timeout, link=False, offline=bool(getattr(namespace, "offline", False))
    )
    if stored is None:
        with WorkTargetStore(context.root) as store:
            stored = store.read()
    selected = read_selection(context, scopes.views, stored=stored)
    expected = resolve_scope(context, scopes.views, namespace.expect_current, selection=selected).id
    if selected.status != "selected" or selected.record is None or selected.record.scope_id != expected:
        raise ValueError("direct target does not match --expect-current")
