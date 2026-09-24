"""Scope dependency graph rules for declared and inherited prerequisites."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from spec_dock_runtime.application.scope_query import ScopeView


@dataclass(frozen=True)
class DependencyEdge:
    target_id: str
    declared_by: str


@dataclass(frozen=True)
class DependencyListing:
    scope_id: str
    declared: tuple[DependencyEdge, ...]
    effective: tuple[DependencyEdge, ...]


def _ancestors(by_id: dict[str, ScopeView], scope_id: str) -> tuple[str, ...]:
    result: list[str] = []
    current = by_id[scope_id]
    while current.parent_id is not None:
        if current.parent_id not in by_id or current.parent_id in result:
            raise ValueError("Scope ancestry is missing or cyclic")
        result.append(current.parent_id)
        current = by_id[current.parent_id]
    return tuple(result)


def dependency_listing(
    views: tuple[ScopeView, ...], raw: dict[str, tuple[str, ...]], scope_id: str
) -> DependencyListing:
    by_id = {view.id: view for view in views}
    if scope_id not in by_id:
        raise LookupError("Scope was not found")
    order = {view.id: index for index, view in enumerate(views)}
    declared = tuple(
        DependencyEdge(target, scope_id) for target in sorted(raw.get(scope_id, ()), key=order.__getitem__)
    )
    effective: list[DependencyEdge] = []
    seen: set[str] = set()
    for owner in (scope_id, *_ancestors(by_id, scope_id)):
        for target in sorted(raw.get(owner, ()), key=order.__getitem__):
            if target not in seen:
                effective.append(DependencyEdge(target, owner))
                seen.add(target)
    return DependencyListing(scope_id, declared, tuple(effective))


def validate_dependency_graph(views: tuple[ScopeView, ...], raw: dict[str, tuple[str, ...]]) -> None:
    """Reject impossible ancestry edges and cycles in the inherited graph."""
    by_id = {view.id: view for view in views}
    if set(raw) != set(by_id):
        raise ValueError("dependency graph does not match the Scope snapshot")
    ancestors = {scope_id: set(_ancestors(by_id, scope_id)) for scope_id in by_id}
    for source, targets in raw.items():
        if len(set(targets)) != len(targets):
            raise ValueError("duplicate declared dependency")
        for target in targets:
            if target not in by_id:
                raise ValueError("dependency target is absent from this snapshot")
            if source == target:
                raise ValueError("self dependency is invalid")
            if target in ancestors[source] or source in ancestors[target]:
                raise ValueError("ancestor or descendant dependency is invalid")
    visited: set[str] = set()
    visiting: set[str] = set()

    def visit(scope_id: str) -> None:
        if scope_id in visiting:
            raise ValueError("effective dependency cycle is invalid")
        if scope_id in visited:
            return
        visiting.add(scope_id)
        for edge in dependency_listing(views, raw, scope_id).effective:
            visit(edge.target_id)
        visiting.remove(scope_id)
        visited.add(scope_id)

    for scope_id in by_id:
        visit(scope_id)
