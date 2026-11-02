"""Scope lifecycle, backend and status observation values shared by the canonical views."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

LifecycleState = Literal["open", "completed", "not-planned"]
ObservedState = Literal["open", "completed", "not-planned", "unknown"]


@dataclass(frozen=True)
class LocalLifecycle:
    state: LifecycleState
    revision: int
    updated_at: str


@dataclass(frozen=True)
class LocalBackend:
    lifecycle: LocalLifecycle
    kind: Literal["local"] = "local"


@dataclass(frozen=True)
class GithubBackend:
    issue_number: int
    repo_owner: str
    repo_name: str
    kind: Literal["github"] = "github"


ScopeBackend = LocalBackend | GithubBackend


@dataclass(frozen=True)
class StatusObservation:
    state: ObservedState
    authority: Literal["local", "github"]
    source: Literal["local", "github", "cache", "unknown"]
    observed_at: str | None
    remote_updated_at: str | None
    stale: bool


@dataclass(frozen=True)
class SelectionState:
    worktree_id: str
    revision: int
    initiative_id: str | None
    epic_id: str | None
    issue_id: str | None
    focus_id: str | None

    def __post_init__(self) -> None:
        if not self.worktree_id:
            raise ValueError("selection requires worktree_id")
        if self.revision < 0:
            raise ValueError("selection revision must be nonnegative")
        if self.epic_id is not None and self.initiative_id is None:
            raise ValueError("epic selection requires initiative")
        if self.issue_id is not None and self.epic_id is None:
            raise ValueError("issue selection requires epic")
        expected_focus = self.issue_id or self.epic_id or self.initiative_id
        if self.focus_id != expected_focus:
            raise ValueError("selection focus does not match chain")


def observe_github_state(state: str, state_reason: str | None) -> ObservedState:
    normalized_state = state.strip().upper()
    if normalized_state == "OPEN":
        return "open"
    if normalized_state != "CLOSED":
        return "unknown"
    if state_reason == "completed":
        return "completed"
    if state_reason == "not_planned":
        return "not-planned"
    return "unknown"
