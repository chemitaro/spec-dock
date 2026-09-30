"""Pure direct-selection policy: only explicit Start can obtain a new token."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from spec_dock.runtime.application.worktree_observation import SelectionObservation


class StartSelectionError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


@dataclass(frozen=True)
class SelectionPlan:
    action: Literal["unchanged", "publish", "replace_same_scope", "switch_scope"]
    observed: SelectionObservation


def plan_selection(
    observation: SelectionObservation,
    *,
    scope_id: str,
    branch: str,
    tip: str,
    current_branch: str | None,
    current_head: str | None,
    switch_active: bool,
) -> SelectionPlan:
    if observation.status == "empty" and observation.record is None and observation.handle is None:
        return SelectionPlan("publish", observation)
    record = observation.record
    if observation.status != "selected" or record is None or observation.handle is None:
        raise StartSelectionError("SELECTION_INVALID", "current direct target must be valid before Start")
    if record.scope_id != scope_id:
        if not switch_active:
            raise StartSelectionError("SWITCH_ACTIVE_REQUIRED", "a different direct target requires --switch-active")
        return SelectionPlan("switch_scope", observation)
    if record.selected_branch == branch and current_branch == branch and current_head == tip:
        return SelectionPlan("unchanged", observation)
    return SelectionPlan("replace_same_scope", observation)
