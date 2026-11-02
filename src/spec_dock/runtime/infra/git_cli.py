from __future__ import annotations

import os
from pathlib import Path
import re
from urllib.parse import urlsplit

from spec_dock.runtime.application.contracts import GitWorktreeRecord

DirectoryWitness = tuple[int, int]
DirectoryWitnesses = tuple[tuple[str, DirectoryWitness], ...]


def sanitized_git_environment(environment: dict[str, str] | None = None) -> dict[str, str]:
    """Discard caller-supplied Git repository/config overrides for bound Git calls."""
    source = os.environ if environment is None else environment
    return {key: value for key, value in source.items() if not key.startswith("GIT_")}


_HTTPS_GH_REMOTE_RE = re.compile(
    r"^https?://(?:[^@/]+@)?github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$",
    re.IGNORECASE,
)
_SSH_GH_REMOTE_RE = re.compile(
    r"^(?:ssh://)?git@github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$",
    re.IGNORECASE,
)


def _parse_github_repo_slug(remote_url: str) -> str | None:
    match = _HTTPS_GH_REMOTE_RE.fullmatch(remote_url) or _SSH_GH_REMOTE_RE.fullmatch(remote_url)
    if match is None:
        return None
    owner = match.group("owner").strip().lower()
    repo = match.group("repo").strip().lower()
    if not owner or not repo:
        return None
    return f"{owner}/{repo}"


def _remote_has_userinfo(remote_url: str) -> bool:
    try:
        parsed = urlsplit(remote_url)
    except ValueError:
        return True
    return parsed.username is not None or parsed.password is not None


def worktree_list(repo_root: Path, *, timeout: float = 30) -> list[GitWorktreeRecord]:
    from spec_dock.runtime.infra.git_process import run_git

    output = run_git(repo_root, "worktree", "list", "--porcelain", "-z", timeout=timeout)
    return _parse_worktree_porcelain_nul(os.fsdecode(output))


def _parse_worktree_porcelain_nul(text: str) -> list[GitWorktreeRecord]:
    """Parse Git's unquoted NUL records without stripping path characters."""
    records: list[GitWorktreeRecord] = []
    for group in text.split("\0\0"):
        if not group:
            continue
        attributes: dict[str, str] = {}
        problems: list[str] = []
        for field in group.split("\0"):
            if not field:
                continue
            key, _, value = field.partition(" ")
            if key not in {"worktree", "HEAD", "branch", "detached", "bare", "locked", "prunable"}:
                problems.append(f"unknown Git worktree inventory attribute: {key}")
            if key in {"detached", "bare"} and value:
                problems.append(f"invalid Git worktree inventory attribute value: {key}")
            if key in attributes:
                problems.append(f"duplicate Git worktree inventory attribute: {key}")
                continue
            attributes[key] = value
        path = attributes.get("worktree")
        if not path or not Path(path).is_absolute():
            raise ValueError("Git worktree inventory has no absolute path")
        branch = attributes.get("branch")
        if branch is not None and not branch.startswith("refs/heads/"):
            problems.append("Git worktree inventory has invalid branch ref")
            branch = None
        records.append(
            GitWorktreeRecord(
                path=Path(path),
                head=attributes.get("HEAD"),
                branch=branch.removeprefix("refs/heads/") if branch is not None else None,
                detached="detached" in attributes,
                bare="bare" in attributes,
                locked="locked" in attributes,
                prunable="prunable" in attributes,
                locked_reason=attributes.get("locked") or None,
                prunable_reason=attributes.get("prunable") or None,
                inventory_error="; ".join(problems) or None,
            )
        )
    return records
