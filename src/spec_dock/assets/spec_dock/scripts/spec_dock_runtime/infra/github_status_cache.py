"""Read saved GitHub status evidence for offline structural operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from spec_dock_runtime.infra.json_store import read_guarded_json

if TYPE_CHECKING:
    from pathlib import Path

    from spec_dock_runtime.domain.lifecycle import GithubBackend


def cached_github_ancestor_open(specdock_dir: Path, scope_id: str, backend: GithubBackend) -> bool:
    """Require a matching saved OPEN observation; this never performs a network call."""
    loaded = read_guarded_json(specdock_dir / ".agent" / "github-status-cache.json")
    if loaded is None:
        raise ValueError("GitHub ancestor status cache is missing")
    payload, _identity = loaded
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("GitHub ancestor status cache schema is invalid")
    items = payload.get("items")
    if not isinstance(items, dict):
        raise ValueError("GitHub ancestor status cache items are invalid")
    item = items.get(scope_id)
    if not isinstance(item, dict):
        raise ValueError("GitHub ancestor status cache has no observation")
    expected_ref = f"gh:{backend.repo_owner.lower()}/{backend.repo_name.lower()}#{backend.issue_number}"
    if item.get("github_ref") != expected_ref:
        raise ValueError("GitHub ancestor cache identity differs from metadata")
    if item.get("state") != "open" or not isinstance(item.get("observed_at"), str) or not item["observed_at"]:
        raise ValueError("GitHub ancestor status cache is not known open")
    return True
