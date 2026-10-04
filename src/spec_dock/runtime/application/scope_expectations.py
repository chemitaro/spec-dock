"""Compare optional expectations with already resolved local observations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from spec_dock.runtime.application.worktree_observation import resolve_scope

if TYPE_CHECKING:
    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.scope_query import ScopeView
    from spec_dock.runtime.application.worktree_observation import SelectionObservation


def check_scope_expectations(
    context: ProjectContext,
    views: tuple[ScopeView, ...],
    selection: SelectionObservation | None,
    *,
    target: ScopeView | None,
    expected_current: str | None,
    expected_backend: str | None,
) -> None:
    if expected_backend is not None:
        if target is None:
            raise ValueError("--expect-backend requires one existing Scope target")
        if target.backend.kind != expected_backend:
            raise ValueError("target backend does not match --expect-backend")
    if expected_current is not None:
        expected = resolve_scope(context, views, expected_current, selection=selection).id
        if (
            selection is None
            or selection.status != "selected"
            or selection.record is None
            or selection.record.scope_id != expected
        ):
            raise ValueError("direct target does not match --expect-current")
