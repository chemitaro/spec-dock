"""Plan local Scope deletion without contacting or changing GitHub."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from spec_dock_runtime.application.active_selection import clear_selection
from spec_dock_runtime.application.scope_completion import _descendants
from spec_dock_runtime.application.scope_query import show_scope

if TYPE_CHECKING:
    from collections.abc import Mapping

    from spec_dock_runtime.application.scope_query import ScopeView
    from spec_dock_runtime.domain.lifecycle import SelectionState


@dataclass(frozen=True)
class ScopeDeletePlan:
    target_id: str
    deleted_ids: tuple[str, ...]
    selection_after: SelectionState
    boundary_edges: tuple[tuple[str, str], ...]
    survivor_dependencies: dict[str, tuple[str, ...]]


def plan_scope_delete(
    views: tuple[ScopeView, ...],
    *, target: str, selection: SelectionState,
    dependencies: Mapping[str, tuple[str, ...]], recursive: bool = False,
    clear_active: bool = False, detach_dependencies: bool = False,
) -> ScopeDeletePlan:
    """Fix the local subtree and every cross-boundary dependency before mutation."""
    scope = show_scope(views, target, selection=selection)
    descendants = _descendants(views, scope)
    if descendants and not recursive:
        raise ValueError("RECURSIVE_REQUIRED")
    deleted_ids = (scope.id, *(view.id for view in descendants))
    deleted = set(deleted_ids)
    ids = {view.id for view in views}
    if set(dependencies) != ids or any(destination not in ids for edges in dependencies.values() for destination in edges):
        raise ValueError("dependency snapshot does not match Scope graph")
    selection_intersects = bool(deleted.intersection(
        (selection.initiative_id, selection.epic_id, selection.issue_id)
    ))
    if selection_intersects and not clear_active:
        raise ValueError("CLEAR_ACTIVE_REQUIRED")
    selection_after = (
        clear_selection(views, current=selection, from_target=scope.id)
        if selection_intersects else selection
    )
    boundary_edges = tuple(sorted(
        (source, destination)
        for source, destinations in dependencies.items()
        for destination in destinations
        if (source in deleted) != (destination in deleted)
    ))
    if boundary_edges and not detach_dependencies:
        raise ValueError("DETACH_DEPENDENCIES_REQUIRED")
    survivor_dependencies = {
        source: tuple(destination for destination in destinations if destination not in deleted)
        for source, destinations in dependencies.items()
        if source not in deleted and any(destination in deleted for destination in destinations)
    }
    return ScopeDeletePlan(scope.id, deleted_ids, selection_after, boundary_edges, survivor_dependencies)
