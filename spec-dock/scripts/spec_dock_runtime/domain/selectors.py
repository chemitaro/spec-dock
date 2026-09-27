"""Strict, typed selectors for vNext CLI targets."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Literal, cast

ScopeKind = Literal["initiative", "epic", "issue"]
ActiveRole = Literal["current", "initiative", "epic", "issue"]


@dataclass(frozen=True)
class ScopeIdSelector:
    id: str
    kind: ScopeKind


@dataclass(frozen=True)
class GithubScopeSelector:
    owner: str
    repo: str
    issue_number: int


@dataclass(frozen=True)
class ActiveScopeSelector:
    role: ActiveRole


@dataclass(frozen=True)
class ArtifactRootSelector:
    pass


@dataclass(frozen=True)
class WorktreeIdSelector:
    id: str


@dataclass(frozen=True)
class WorktreeAliasSelector:
    name: str


@dataclass(frozen=True)
class WorktreePathSelector:
    path: str


ScopeSelector = ScopeIdSelector | GithubScopeSelector | ActiveScopeSelector
ArtifactSelector = ScopeSelector | ArtifactRootSelector
WorktreeSelector = WorktreeIdSelector | WorktreeAliasSelector | WorktreePathSelector

_SCOPE_ID = re.compile(r"^(?P<prefix>init|epic|iss)(?P<local>-local)?-(?P<number>[0-9]+)$")
_GITHUB_SCOPE = re.compile(
    r"^gh:(?P<owner>[A-Za-z0-9][A-Za-z0-9-]*)/(?P<repo>[A-Za-z0-9_.-]+)#(?P<number>[0-9]+)$",
    re.IGNORECASE,
)
_GITHUB_ISSUE_URL = re.compile(
    r"^https://github\.com/(?P<owner>[A-Za-z0-9][A-Za-z0-9-]*)/(?P<repo>[A-Za-z0-9_.-]+)/issues/(?P<number>[0-9]+)$",
    re.IGNORECASE,
)
_REPO_ID = re.compile(r"^(?P<owner>[A-Za-z0-9][A-Za-z0-9-]*)/(?P<repo>[A-Za-z0-9_.-]+)$")
_KIND_BY_PREFIX: dict[str, ScopeKind] = {"init": "initiative", "epic": "epic", "iss": "issue"}
_ACTIVE_ROLES = {"@current", "@initiative", "@epic", "@issue"}
_WORKTREE_NAME = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def parse_scope_selector(value: str) -> ScopeSelector:
    raw = value.strip()
    if raw in _ACTIVE_ROLES:
        return ActiveScopeSelector(cast("ActiveRole", raw[1:]))
    match = _SCOPE_ID.fullmatch(raw.lower())
    if match is not None:
        number = int(match.group("number"))
        if number <= 0:
            raise ValueError("Scope ID number must be positive")
        prefix = match.group("prefix")
        local = match.group("local") or ""
        return ScopeIdSelector(f"{prefix}{local}-{number:05d}", _KIND_BY_PREFIX[prefix])
    match = _GITHUB_SCOPE.fullmatch(raw)
    if match is not None:
        number = int(match.group("number"))
        if number <= 0:
            raise ValueError("GitHub Issue number must be positive")
        return GithubScopeSelector(match.group("owner").lower(), match.group("repo").lower(), number)
    raise ValueError("invalid Scope selector; use a complete ID, gh:OWNER/REPO#NUMBER, or an active role")


def parse_github_ref(value: str, *, repo_hint: str | None = None) -> GithubScopeSelector:
    hint: tuple[str, str] | None = None
    if repo_hint is not None:
        match = _REPO_ID.fullmatch(repo_hint.strip())
        if match is None:
            raise ValueError("invalid GitHub repository hint")
        hint = (match.group("owner").lower(), match.group("repo").lower())
    raw = value.strip()
    parsed: GithubScopeSelector
    if raw.startswith("gh:"):
        selector = parse_scope_selector(raw)
        if not isinstance(selector, GithubScopeSelector):
            raise ValueError("invalid GitHub reference")
        parsed = selector
    elif match := _GITHUB_ISSUE_URL.fullmatch(raw):
        parsed = GithubScopeSelector(
            match.group("owner").lower(), match.group("repo").lower(), int(match.group("number"))
        )
    elif re.fullmatch(r"[0-9]+", raw) and hint is not None:
        parsed = GithubScopeSelector(hint[0], hint[1], int(raw))
    else:
        raise ValueError(
            "GitHub reference requires gh:OWNER/REPO#NUMBER, exact Issue URL, or NUMBER with --github-repo"
        )
    if parsed.issue_number <= 0:
        raise ValueError("GitHub Issue number must be positive")
    if hint is not None and (parsed.owner, parsed.repo) != hint:
        raise ValueError("GitHub reference and --github-repo disagree")
    return parsed


def parse_artifact_selector(value: str) -> ArtifactSelector:
    if value.strip() == "@root":
        return ArtifactRootSelector()
    return parse_scope_selector(value)


def parse_worktree_selector(value: str) -> WorktreeSelector:
    raw = value
    if raw.startswith("wt:"):
        worktree_id = raw[3:]
        if not _WORKTREE_NAME.fullmatch(worktree_id):
            raise ValueError("invalid stable worktree ID")
        return WorktreeIdSelector(worktree_id)
    if raw.startswith("/"):
        if ".." in raw.split("/") or "\x00" in raw:
            raise ValueError("worktree path must be absolute without traversal")
        return WorktreePathSelector(raw)
    if _WORKTREE_NAME.fullmatch(raw):
        return WorktreeAliasSelector(raw)
    raise ValueError("worktree selector requires wt:ID, registered alias, or absolute path")
