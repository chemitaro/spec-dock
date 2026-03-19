from __future__ import annotations

from pathlib import Path
from typing import cast

from ..domain.models import SpecNodeKind, SpecNodeSeed
from ..domain.tree import build_graph
from ..domain.validation import validate_graph_and_deps
from ..infra.contracts import StoredMetaRecord
from .contracts import ValidateTreeRequest, ValidationResult
from .ports import Ports


def _to_spec_node_seed(record: StoredMetaRecord) -> SpecNodeSeed:
    return SpecNodeSeed(
        kind=cast(SpecNodeKind, record.kind),
        id=record.id,
        title=record.title,
        slug=record.slug,
        path=Path(record.path),
        meta_path=Path(record.meta_path),
        parent_id=record.parent_id,
        initiative_id=record.initiative_id,
        epic_id=record.epic_id,
        github_issue_number=record.github_issue_number,
        github_repo_owner=record.github_repo_owner,
        github_repo_name=record.github_repo_name,
    )


def _normalize_repo_slug_value(slug: str | None) -> str | None:
    text = str(slug or "").strip().lower()
    if not text:
        return None
    owner, sep, repo = text.partition("/")
    if not sep or not owner or not repo:
        return None
    return f"{owner}/{repo}"


def _resolve_current_repo_slug(ports: Ports) -> str | None:
    if ports.git_gateway is None or ports.repo_root is None:
        return None
    resolver = getattr(ports.git_gateway, "origin_github_repo_slug", None)
    if not callable(resolver):
        return None
    try:
        raw = resolver(ports.repo_root)
    except RuntimeError:
        return None
    return _normalize_repo_slug_value(raw)


def validate_tree(req: ValidateTreeRequest, ports: Ports) -> ValidationResult:
    del req
    records = ports.node_reader.load_node_records()
    graph = build_graph([_to_spec_node_seed(record) for record in records])
    issue_depends_on_map: dict[str, list[str]] | None = None
    if ports.deps_topology_reader is not None:
        if ports.specdock_dir is not None:
            specdock_dir = ports.specdock_dir
        elif ports.repo_root is not None:
            specdock_dir = ports.repo_root / "spec-dock"
        else:
            raise RuntimeError("specdock_dir is required when deps_topology_reader is configured")
        topology = ports.deps_topology_reader.load_issue_depends_on_map(specdock_dir, graph)
        issue_depends_on_map = dict(topology.issue_depends_on_map)

    report = validate_graph_and_deps(
        graph,
        issue_depends_on_map=issue_depends_on_map,
        repo_root=ports.repo_root,
        current_repo_slug=_resolve_current_repo_slug(ports),
    )
    return ValidationResult(report=report, checked_node_count=len(records))
