"""Start readiness of a Scope from the structure snapshot (iss-00431; work start and the dashboard use it).

The rules are today's: the Scope and its ancestors must be open and every prerequisite Scope declared by them
must be closed as completed. A non-Scope Issue of the same repository blocks only while open. Anything the
snapshot cannot decide (anomalies on the chain, foreign relations, dependencies it does not hold) is UNKNOWN,
never ready. Aggregating states from descendants belongs to epic-00427.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, Literal

from spec_dock.runtime.domain.canonical_structure import PARENT_INVALID, PARENT_KINDS, parse_scope_id
from spec_dock.runtime.domain.lifecycle import observe_github_state

if TYPE_CHECKING:
    from collections.abc import Mapping

    from spec_dock.runtime.domain.canonical_structure import ScopeNode, StructureSnapshot

ReadinessState = Literal["READY", "BLOCKED", "DOING", "DONE", "UNKNOWN"]
BlockerRole = Literal["self", "ancestor", "prerequisite", "external"]

DEPENDENCY_NOT_IN_SNAPSHOT: Final = "DEPENDENCY_NOT_IN_SNAPSHOT"


@dataclass(frozen=True)
class CanonicalBlocker:
    """An Issue that stops the start; scope_id is None for a non-Scope Issue (role "external")."""

    number: int
    scope_id: str | None
    role: BlockerRole
    required_state: str
    observed_state: str
    declared_by: str | None = None


@dataclass(frozen=True)
class UnknownReason:
    """Why readiness cannot be decided: a snapshot anomaly code or DEPENDENCY_NOT_IN_SNAPSHOT."""

    number: int
    scope_id: str | None
    code: str
    message: str


@dataclass(frozen=True)
class ScopeReadiness:
    scope_id: str
    number: int
    state: ReadinessState
    ready: bool
    in_progress: bool
    blockers: tuple[CanonicalBlocker, ...]
    unknown: tuple[UnknownReason, ...]


def evaluate_readiness(snapshot: StructureSnapshot, scope_id: str) -> ScopeReadiness:
    try:
        parse_scope_id(scope_id)
    except ValueError as error:
        raise LookupError(f"{scope_id} is not a Scope ID") from error
    target = snapshot.find(scope_id)
    if target is None or target.id is None:
        raise LookupError(f"{scope_id} is not a Scope in the structure snapshot")
    unknown: list[UnknownReason] = []
    blockers: list[CanonicalBlocker] = []
    chain = _chain(snapshot, target, unknown)
    for member in chain:
        unknown.extend(
            UnknownReason(item.number, member.id, item.code, item.message)
            for item in snapshot.anomalies_for(member.number)
        )
        if member.state != "open":
            blockers.append(
                CanonicalBlocker(
                    member.number,
                    member.id,
                    "self" if member is target else "ancestor",
                    "open",
                    observe_github_state(member.state, member.state_reason),
                )
            )
    seen: set[int] = set()
    for member in chain:
        for number in member.blocked_by:
            if number in seen:
                continue
            seen.add(number)
            _prerequisite(snapshot, number, member, blockers, unknown)
    if target.state != "open":
        state: ReadinessState = "DONE"
    elif unknown:
        state = "UNKNOWN"
    elif target.in_progress:
        state = "DOING"
    elif blockers:
        state = "BLOCKED"
    else:
        state = "READY"
    return ScopeReadiness(
        target.id,
        target.number,
        state,
        not blockers and not unknown,
        target.in_progress,
        tuple(blockers),
        tuple(unknown),
    )


def evaluate_all(snapshot: StructureSnapshot) -> Mapping[str, ScopeReadiness]:
    return {node.id: evaluate_readiness(snapshot, node.id) for node in snapshot.scopes if node.id is not None}


def _chain(snapshot: StructureSnapshot, target: ScopeNode, unknown: list[UnknownReason]) -> tuple[ScopeNode, ...]:
    """The Scope and its ancestors; a broken link stops the walk and records why (the anomaly or PARENT_INVALID)."""
    chain = [target]
    current = target
    while current.parent is not None:
        parent = snapshot.issues.get(current.parent)
        expected = PARENT_KINDS.get(current.kind) if current.kind is not None else None
        if (
            parent is None
            or parent.id is None
            or parent.kind != expected
            or any(member.number == parent.number for member in chain)
        ):
            if not snapshot.anomalies_for(current.number):
                unknown.append(
                    UnknownReason(
                        current.number, current.id, PARENT_INVALID, f"the parent #{current.parent} cannot be resolved"
                    )
                )
            break
        chain.append(parent)
        current = parent
    return tuple(chain)


def _prerequisite(
    snapshot: StructureSnapshot,
    number: int,
    declared_by: ScopeNode,
    blockers: list[CanonicalBlocker],
    unknown: list[UnknownReason],
) -> None:
    node = snapshot.issues.get(number)
    if node is not None and node.id is not None:
        observed = observe_github_state(node.state, node.state_reason)
        if observed != "completed":
            blockers.append(CanonicalBlocker(number, node.id, "prerequisite", "completed", observed, declared_by.id))
        return
    if node is not None:
        anomalies = snapshot.anomalies_for(number)
        if anomalies:
            unknown.extend(UnknownReason(number, None, item.code, item.message) for item in anomalies)
            return
    else:
        external = snapshot.external.get(number)
        if external is not None:
            if external.state == "open":
                blockers.append(CanonicalBlocker(number, None, "external", "closed", "open", declared_by.id))
            return
    unknown.append(
        UnknownReason(
            number,
            None,
            DEPENDENCY_NOT_IN_SNAPSHOT,
            f"#{number}, a dependency of {declared_by.id}, is not in the structure snapshot",
        )
    )
