"""Pure one-Scope/one-branch registry invariants."""

from __future__ import annotations

from dataclasses import dataclass, replace
import re
from typing import TYPE_CHECKING

from spec_dock_runtime.domain.selectors import ScopeIdSelector, parse_scope_selector

if TYPE_CHECKING:
    from spec_dock_runtime.domain.registry import LocalIdRegistry

_SHA = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")


@dataclass(frozen=True)
class BranchBinding:
    scope_id: str
    name: str
    initial_sha: str

    def __post_init__(self) -> None:
        selector = parse_scope_selector(self.scope_id)
        if not isinstance(selector, ScopeIdSelector) or selector.id != self.scope_id:
            raise ValueError("branch binding requires a canonical Scope ID")
        if not self.name or not self.name.isascii() or any(character.isspace() for character in self.name):
            raise ValueError("canonical branch name is invalid")
        if _SHA.fullmatch(self.initial_sha) is None:
            raise ValueError("canonical branch initial SHA is invalid")


def bind_branch(state: LocalIdRegistry, binding: BranchBinding) -> LocalIdRegistry:
    for prior in state.branches:
        if prior.scope_id == binding.scope_id or prior.name == binding.name:
            if prior == binding:
                return state
            raise ValueError("Scope or branch is already bound")
    return replace(state, revision=state.revision + 1, branches=(*state.branches, binding))
