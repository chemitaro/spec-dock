"""Read the required Scope parent chain and verify open ancestors."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from spec_dock.runtime.domain.lifecycle import GithubBackend, LocalBackend, decode_scope_metadata
from spec_dock.runtime.domain.selectors import ScopeIdSelector, parse_scope_selector
from spec_dock.runtime.infra.json_store import read_guarded_json

if TYPE_CHECKING:
    from spec_dock.runtime.domain.selectors import ScopeKind
    from spec_dock.runtime.infra.contracts import GithubIssueRecord, StoredMetaRecord


class AncestorGateway(Protocol):
    def get(self, repo_root: Path, repository: str, number: int) -> GithubIssueRecord: ...


def _parent_records(
    *, kind: ScopeKind, parent_id: str | None, records: dict[str, StoredMetaRecord]
) -> tuple[StoredMetaRecord, ...]:
    required = {"initiative": None, "epic": "initiative", "issue": "epic"}[kind]
    if required is None:
        if parent_id is not None:
            raise ValueError("initiative cannot have a parent")
        return ()
    if parent_id is None:
        raise ValueError(f"{kind} requires an explicit parent")
    selector = parse_scope_selector(parent_id)
    if not isinstance(selector, ScopeIdSelector) or selector.id != parent_id or selector.kind != required:
        raise ValueError(f"{kind} parent must be a canonical {required} ID")
    parent = records.get(parent_id)
    if parent is None or parent.kind != required:
        raise ValueError(f"{required} parent is missing")
    if kind == "epic":
        return (parent,)
    initiative = records.get(parent.initiative_id or "")
    if initiative is None or initiative.kind != "initiative" or parent.parent_id != initiative.id:
        raise ValueError("issue requires its matching initiative ancestor")
    return parent, initiative


def _require_open_ancestors(
    *,
    ancestors: tuple[StoredMetaRecord, ...],
    repo_root: Path,
    repository: str,
    gateway: AncestorGateway,
) -> tuple[int, int] | None:
    parent_meta_identity: tuple[int, int] | None = None
    for index, ancestor in enumerate(ancestors):
        loaded = read_guarded_json(Path(ancestor.meta_path))
        if loaded is None or not isinstance(loaded[0], dict):
            raise ValueError("Scope ancestor metadata is missing")
        if index == 0:
            parent_meta_identity = loaded[1]
        metadata = decode_scope_metadata(loaded[0])
        if metadata.raw.get("id") != ancestor.id:
            raise ValueError("Scope ancestor identity changed")
        if isinstance(metadata.backend, LocalBackend):
            if metadata.backend.lifecycle.state != "open":
                raise ValueError("Scope ancestor is terminal")
            continue
        assert isinstance(metadata.backend, GithubBackend)
        if f"{metadata.backend.repo_owner}/{metadata.backend.repo_name}".lower() != repository.lower():
            raise ValueError("GitHub Scope ancestor belongs to a different repository")
        observed = gateway.get(repo_root, repository, metadata.backend.issue_number)
        if observed.state != "open":
            raise ValueError("GitHub Scope ancestor is not open")
    return parent_meta_identity
