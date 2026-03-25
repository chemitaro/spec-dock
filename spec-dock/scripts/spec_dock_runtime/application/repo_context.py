from __future__ import annotations

from .ports import Ports


def normalize_repo_slug_value(slug: str | None) -> str | None:
    text = str(slug or "").strip().lower()
    if not text:
        return None
    owner, sep, repo = text.partition("/")
    if not sep or not owner or not repo:
        return None
    return f"{owner}/{repo}"


def normalize_repo_slug(owner: str | None, repo: str | None) -> str | None:
    normalized_owner = str(owner or "").strip().lower()
    normalized_repo = str(repo or "").strip().lower()
    if not normalized_owner or not normalized_repo:
        return None
    return f"{normalized_owner}/{normalized_repo}"


def split_repo_slug(slug: str | None) -> tuple[str, str] | None:
    normalized = normalize_repo_slug_value(slug)
    if normalized is None:
        return None
    owner, _sep, repo = normalized.partition("/")
    return (owner, repo)


def resolve_current_repo_slug(ports: Ports) -> str | None:
    if ports.git_gateway is None or ports.repo_root is None:
        return None
    resolver = getattr(ports.git_gateway, "origin_github_repo_slug", None)
    if not callable(resolver):
        return None
    try:
        raw = resolver(ports.repo_root)
    except RuntimeError:
        return None
    return normalize_repo_slug_value(raw)
