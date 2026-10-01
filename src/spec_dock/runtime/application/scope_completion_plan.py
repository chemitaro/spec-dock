"""Pure close/reopen decisions without writer admission or persistent operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from spec_dock.runtime.application.scope_query import show_scope

if TYPE_CHECKING:
    from collections.abc import Mapping

    from spec_dock.runtime.application.scope_query import ScopeView
    from spec_dock.runtime.domain.lifecycle import ObservedState

CompletionReason = Literal["completed", "not-planned"]


@dataclass(frozen=True)
class CompletionDecision:
    target_id: str
    before: ObservedState
    after: Literal["open", "completed", "not-planned"]
    changed: bool
    descendants: tuple[str, ...]


def _state(statuses: Mapping[str, ObservedState], scope_id: str) -> ObservedState:
    try:
        return statuses[scope_id]
    except KeyError as error:
        raise ValueError("SCOPE_STATUS_UNOBSERVED") from error


def _ancestors(views: tuple[ScopeView, ...], target: ScopeView) -> tuple[ScopeView, ...]:
    by_id = {view.id: view for view in views}
    ancestors: list[ScopeView] = []
    seen = {target.id}
    parent_id = target.parent_id
    while parent_id is not None:
        if parent_id in seen or parent_id not in by_id:
            raise ValueError("SCOPE_ANCESTRY_INVALID")
        seen.add(parent_id)
        parent = by_id[parent_id]
        ancestors.append(parent)
        parent_id = parent.parent_id
    return tuple(ancestors)


def _descendants(views: tuple[ScopeView, ...], target: ScopeView) -> tuple[ScopeView, ...]:
    by_id = {view.id: view for view in views}
    children: list[ScopeView] = []
    for view in views:
        if view.id == target.id:
            continue
        seen = {view.id}
        parent_id = view.parent_id
        while parent_id is not None:
            if parent_id in seen or parent_id not in by_id:
                raise ValueError("SCOPE_ANCESTRY_INVALID")
            if parent_id == target.id:
                children.append(view)
                break
            seen.add(parent_id)
            parent_id = by_id[parent_id].parent_id
    return tuple(children)


def plan_close(
    views: tuple[ScopeView, ...],
    target_id: str,
    statuses: Mapping[str, ObservedState],
    *,
    reason: CompletionReason = "completed",
) -> CompletionDecision:
    if reason not in ("completed", "not-planned"):
        raise ValueError("INVALID_COMPLETION_REASON")
    target = show_scope(views, target_id)
    before = _state(statuses, target.id)
    descendants = _descendants(views, target)
    if reason == "completed" and any(_state(statuses, child.id) != "completed" for child in descendants):
        raise ValueError("DESCENDANT_NOT_COMPLETED")
    if before == "unknown":
        raise ValueError("SCOPE_STATUS_UNKNOWN")
    if before != "open" and before != reason:
        raise ValueError("TERMINAL_REASON_CONFLICT")
    return CompletionDecision(target.id, before, reason, before != reason, tuple(child.id for child in descendants))


def plan_reopen(
    views: tuple[ScopeView, ...], target_id: str, statuses: Mapping[str, ObservedState]
) -> CompletionDecision:
    target = show_scope(views, target_id)
    before = _state(statuses, target.id)
    if any(_state(statuses, ancestor.id) != "open" for ancestor in _ancestors(views, target)):
        raise ValueError("ANCESTOR_TERMINAL")
    if before == "unknown":
        raise ValueError("SCOPE_STATUS_UNKNOWN")
    return CompletionDecision(target.id, before, "open", before != "open", ())
