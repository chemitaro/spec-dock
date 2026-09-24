"""Version-three Scope lifecycle and authority contracts."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import re
from typing import Literal, cast

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
class ScopeMetadata:
    raw: dict[str, object]
    backend: ScopeBackend
    revision: int


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


def decode_scope_metadata(payload: dict[str, object]) -> ScopeMetadata:
    if payload.get("schema_version") != 3:
        raise ValueError("Scope metadata requires schema_version 3")
    kind = payload.get("type")
    scope_id = payload.get("id")
    if not isinstance(kind, str):
        raise ValueError("invalid Scope kind or ID")
    prefix = {"initiative": "init", "epic": "epic", "issue": "iss"}.get(kind)
    if prefix is None or not isinstance(scope_id, str):
        raise ValueError("invalid Scope kind or ID")
    match = re.fullmatch(rf"{prefix}(?:-local)?-([0-9]+)", scope_id)
    if match is None or int(match.group(1)) <= 0:
        raise ValueError("Scope ID does not match kind")
    revision = payload.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 0:
        raise ValueError("Scope metadata requires a nonnegative revision")
    if payload.get("backend") == "github":
        if payload.get("lifecycle") is not None:
            raise ValueError("GitHub Scope cannot have local lifecycle")
        github = payload.get("github")
        if not isinstance(github, dict):
            raise ValueError("GitHub Scope requires github link")
        issue_number = github.get("issue_number")
        owner = github.get("repo_owner")
        repo = github.get("repo_name")
        if not isinstance(issue_number, int) or isinstance(issue_number, bool) or issue_number <= 0:
            raise ValueError("invalid GitHub Issue number")
        if not isinstance(owner, str) or not owner or not isinstance(repo, str) or not repo:
            raise ValueError("invalid GitHub repository identity")
        return ScopeMetadata(deepcopy(payload), GithubBackend(issue_number, owner, repo), revision)
    if payload.get("backend") != "local" or payload.get("github") is not None:
        raise ValueError("local Scope cannot have GitHub authority")
    lifecycle = payload.get("lifecycle")
    if not isinstance(lifecycle, dict):
        raise ValueError("local Scope requires lifecycle")
    state = lifecycle.get("state")
    state_revision = lifecycle.get("revision")
    updated_at = lifecycle.get("updated_at")
    if state not in ("open", "completed", "not-planned"):
        raise ValueError("invalid local lifecycle state")
    if not isinstance(state_revision, int) or isinstance(state_revision, bool) or state_revision < 0:
        raise ValueError("invalid local lifecycle revision")
    if not isinstance(updated_at, str) or not updated_at:
        raise ValueError("invalid local lifecycle updated_at")
    backend = LocalBackend(LocalLifecycle(cast("LifecycleState", state), state_revision, updated_at))
    return ScopeMetadata(raw=deepcopy(payload), backend=backend, revision=revision)


def encode_scope_metadata(metadata: ScopeMetadata) -> dict[str, object]:
    result = deepcopy(metadata.raw)
    if result.get("backend") != metadata.backend.kind:
        raise ValueError("Scope backend conversion is not supported")
    result["revision"] = metadata.revision
    if isinstance(metadata.backend, LocalBackend):
        raw_lifecycle = result.get("lifecycle")
        lifecycle = dict(raw_lifecycle) if isinstance(raw_lifecycle, dict) else {}
        lifecycle.update(
            state=metadata.backend.lifecycle.state,
            revision=metadata.backend.lifecycle.revision,
            updated_at=metadata.backend.lifecycle.updated_at,
        )
        result["lifecycle"] = lifecycle
        result["github"] = None
    else:
        raw_github = result.get("github")
        github = dict(raw_github) if isinstance(raw_github, dict) else {}
        github.update(
            issue_number=metadata.backend.issue_number,
            repo_owner=metadata.backend.repo_owner,
            repo_name=metadata.backend.repo_name,
        )
        result["github"] = github
        result["lifecycle"] = None
    return result


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
