"""Pure, monotone local Scope ID reservations."""

from __future__ import annotations

from dataclasses import dataclass, replace
import re
from typing import TYPE_CHECKING

from spec_dock_runtime.domain.ids import format_id
from spec_dock_runtime.domain.selectors import ScopeIdSelector, parse_scope_selector

if TYPE_CHECKING:
    from collections.abc import Iterable

    from spec_dock_runtime.domain.branch_binding import BranchBinding
    from spec_dock_runtime.domain.selectors import ScopeKind

_KIND_INDEX = {"initiative": 0, "epic": 1, "issue": 2}
_KIND_PREFIX = {"initiative": "init", "epic": "epic", "issue": "iss"}
_PREFIX_INDEX = {"init": 0, "epic": 1, "iss": 2}
_OBSERVED_ID = re.compile(r"^(?P<prefix>init|epic|iss)(?P<local>-local)?-(?P<number>[0-9]+)$")


@dataclass(frozen=True)
class LocalIdRegistry:
    revision: int
    high_water: tuple[int, int, int]
    reserved: frozenset[str]
    branches: tuple[BranchBinding, ...] = ()
    deleted_ids: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if type(self.revision) is not int or self.revision < 0:
            raise ValueError("registry revision is invalid")
        if len(self.high_water) != 3 or any(type(value) is not int or value < 0 for value in self.high_water):
            raise ValueError("registry high-water marks are invalid")
        for scope_id in self.reserved:
            match = _OBSERVED_ID.fullmatch(scope_id)
            if match is None or match.group("local") is None or int(match.group("number")) <= 0:
                raise ValueError("registry reservation is invalid")
            prefix = match.group("prefix")
            number = int(match.group("number"))
            if scope_id != format_id(prefix, number, local=True):
                raise ValueError("registry reservation is not canonical")
            if number > self.high_water[_PREFIX_INDEX[prefix]]:
                raise ValueError("registry reservation exceeds its high-water mark")
        if len({binding.scope_id for binding in self.branches}) != len(self.branches) or len({
            binding.name for binding in self.branches
        }) != len(self.branches):
            raise ValueError("canonical branch registry has duplicate bindings")
        for scope_id in self.deleted_ids:
            selector = parse_scope_selector(scope_id)
            if not isinstance(selector, ScopeIdSelector) or selector.id != scope_id:
                raise ValueError("deleted Scope ID reservation is invalid")

    @classmethod
    def empty(cls) -> LocalIdRegistry:
        return cls(0, (0, 0, 0), frozenset())


def reserve_local_id(
    state: LocalIdRegistry,
    *,
    kind: ScopeKind,
    observed_ids: Iterable[str],
) -> tuple[LocalIdRegistry, str]:
    """Burn a fresh ID under the shared writer lock, even if later create fails."""
    index = _KIND_INDEX[kind]
    prefix = _KIND_PREFIX[kind]
    highest = state.high_water[index]
    for node_id in (*state.reserved, *observed_ids):
        match = _OBSERVED_ID.fullmatch(node_id)
        if match is None or int(match.group("number")) <= 0:
            raise ValueError("invalid observed Scope ID in local allocator")
        if node_id != format_id(
            match.group("prefix"), int(match.group("number")), local=match.group("local") is not None
        ):
            raise ValueError("noncanonical observed Scope ID in local allocator")
        if match.group("prefix") == prefix and match.group("local") is not None:
            highest = max(highest, int(match.group("number")))
    number = highest + 1
    allocated = format_id(prefix, number, local=True)
    if allocated in state.reserved:
        raise ValueError("local Scope ID reservation collision")
    updated = list(state.high_water)
    updated[index] = number
    next_high_water = (updated[0], updated[1], updated[2])
    return replace(
        state, revision=state.revision + 1, high_water=next_high_water, reserved=state.reserved | {allocated}
    ), allocated


def include_observed_local_ids(state: LocalIdRegistry, observed_ids: Iterable[str]) -> LocalIdRegistry:
    """Reserve current and historical local IDs without consuming the next ID."""
    observed = set(state.reserved)
    high_water = list(state.high_water)
    for scope_id in observed_ids:
        match = _OBSERVED_ID.fullmatch(scope_id)
        if match is None or int(match.group("number")) <= 0:
            raise ValueError("migration observed Scope ID is invalid")
        prefix = match.group("prefix")
        number = int(match.group("number"))
        if scope_id != format_id(prefix, number, local=match.group("local") is not None):
            raise ValueError("migration observed Scope ID is not canonical")
        if match.group("local") is not None:
            observed.add(scope_id)
            high_water[_PREFIX_INDEX[prefix]] = max(high_water[_PREFIX_INDEX[prefix]], number)
    next_high_water = (high_water[0], high_water[1], high_water[2])
    if frozenset(observed) == state.reserved and next_high_water == state.high_water:
        return state
    return replace(state, revision=state.revision + 1, high_water=next_high_water, reserved=frozenset(observed))
