from __future__ import annotations

from pathlib import Path
from typing import cast

from ..domain.deps import issue_dependency_exists
from ..domain.models import SpecNodeSeed, SpecNodeKind
from ..domain.tree import build_graph
from ..domain.validation import ensure_current_graph_and_deps_valid
from ..infra.contracts import StoredMetaRecord
from .contracts import MutateDepsRequest, MutateDepsResult
from .ports import Ports
from .repo_context import resolve_current_repo_slug


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


def _resolve_specdock_dir(ports: Ports) -> Path:
    if ports.specdock_dir is not None:
        return ports.specdock_dir
    if ports.repo_root is not None:
        return ports.repo_root / "spec-dock"
    raise RuntimeError("specdock_dir is required")


def mutate_deps(req: MutateDepsRequest, ports: Ports) -> MutateDepsResult:
    if req.action != "add":
        raise RuntimeError(f"Unsupported deps mutation action: {req.action}")
    if ports.node_repo is None:
        raise RuntimeError("node_repo is required")
    if ports.deps_topology_reader is None:
        raise RuntimeError("deps_topology_reader is required")

    records = ports.node_reader.load_node_records()
    graph = build_graph([_to_spec_node_seed(record) for record in records])
    topology = ports.deps_topology_reader.load_issue_depends_on_map(_resolve_specdock_dir(ports), graph)
    issue_depends_on_map = dict(topology.issue_depends_on_map)
    ensure_current_graph_and_deps_valid(
        graph,
        issue_depends_on_map,
        repo_root=ports.repo_root,
        current_repo_slug=resolve_current_repo_slug(ports),
        enforce_github_mandatory_linkage=False,
    )

    from_node = graph.nodes_by_id.get(req.from_id)
    to_node = graph.nodes_by_id.get(req.to_id)
    if from_node is None:
        raise RuntimeError(f"Node not found: {req.from_id}")
    if to_node is None:
        raise RuntimeError(f"Node not found: {req.to_id}")
    if from_node.kind != "issue":
        raise RuntimeError(f"unsupported_node_kind: {req.from_id}")
    if to_node.kind != "issue":
        raise RuntimeError(f"unsupported_node_kind: {req.to_id}")

    add_issue_dependency = getattr(ports.node_repo, "add_issue_dependency", None)
    if not callable(add_issue_dependency):
        raise RuntimeError("add_issue_dependency is not configured")

    if issue_dependency_exists(
        issue_depends_on_map,
        from_issue_id=from_node.id,
        to_issue_id=to_node.id,
    ):
        return MutateDepsResult(
            action=req.action,
            from_id=from_node.id,
            to_id=to_node.id,
            result="unchanged",
            warnings=[],
        )

    add_issue_dependency(from_node.meta_path, to_node.id)

    return MutateDepsResult(
        action=req.action,
        from_id=from_node.id,
        to_id=to_node.id,
        result="updated",
        warnings=[],
    )
