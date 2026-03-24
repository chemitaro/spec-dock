from __future__ import annotations

from ..domain.models import SpecGraph, SpecNode
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


def has_partial_repo_scope(owner: str | None, repo: str | None) -> bool:
    has_owner = bool(str(owner or "").strip())
    has_repo = bool(str(repo or "").strip())
    return has_owner != has_repo


def collect_safe_current_repo_backfill_node_ids(
    graph: SpecGraph,
    *,
    current_repo_slug: str | None,
    trusted_current_repo_node_ids: set[str] | None = None,
) -> list[str]:
    normalized_current_repo_slug = normalize_repo_slug_value(current_repo_slug)
    if normalized_current_repo_slug is None:
        return []
    trusted_node_ids = {node_id for node_id in (trusted_current_repo_node_ids or set()) if node_id}

    linked_by_issue_number: dict[int, list[SpecNode]] = {}
    for node in graph.nodes_by_id.values():
        if node.kind not in ("initiative", "epic", "issue"):
            continue
        if node.github_issue_number is None:
            continue
        linked_by_issue_number.setdefault(int(node.github_issue_number), []).append(node)

    eligible_node_ids: list[str] = []
    for issue_number in sorted(linked_by_issue_number.keys()):
        linked_nodes = linked_by_issue_number[issue_number]
        if any(has_partial_repo_scope(node.github_repo_owner, node.github_repo_name) for node in linked_nodes):
            continue

        current_scope_candidates: list[SpecNode] = []
        for node in linked_nodes:
            explicit_repo_slug = normalize_repo_slug(node.github_repo_owner, node.github_repo_name)
            if explicit_repo_slug == normalized_current_repo_slug:
                current_scope_candidates.append(node)
                continue
            if explicit_repo_slug is None and node.id in trusted_node_ids:
                current_scope_candidates.append(node)

        if len(current_scope_candidates) != 1:
            continue

        candidate = current_scope_candidates[0]
        # Backfill only legacy unscoped linkage; explicit scope is already normalized.
        if normalize_repo_slug(candidate.github_repo_owner, candidate.github_repo_name) is not None:
            continue
        eligible_node_ids.append(candidate.id)

    return sorted(eligible_node_ids)


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
