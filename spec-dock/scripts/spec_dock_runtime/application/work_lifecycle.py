"""Compose work transitions from fixed Scope and selection snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from spec_dock_runtime.application.active_selection import clear_selection
from spec_dock_runtime.application.scope_completion import plan_close
from spec_dock_runtime.application.scope_query import show_scope

if TYPE_CHECKING:
    from collections.abc import Mapping

    from spec_dock_runtime.application.scope_completion import CompletionDecision
    from spec_dock_runtime.application.scope_query import ScopeView
    from spec_dock_runtime.domain.lifecycle import ObservedState, SelectionState


@dataclass(frozen=True)
class WorkFinishPlan:
    target_id: str
    completion: CompletionDecision
    selection_after: SelectionState


def plan_finish_work(
    views: tuple[ScopeView, ...],
    *,
    target: str,
    statuses: Mapping[str, ObservedState],
    selection: SelectionState,
) -> WorkFinishPlan:
    """Fix the requested Scope before any lifecycle or active mutation occurs."""
    scope = show_scope(views, target, selection=selection)
    completion = plan_close(views, scope.id, statuses)
    selection_after = clear_selection(views, current=selection, from_target=scope.id)
    return WorkFinishPlan(scope.id, completion, selection_after)
