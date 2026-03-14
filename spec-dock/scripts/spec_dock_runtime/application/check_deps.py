from __future__ import annotations

from pathlib import Path
from typing import cast

from ..domain.deps import inspect_target_deps, validate_deps_cycles
from ..domain.ids import format_id, parse_id
from ..domain.models import NodeId, SpecGraph, SpecNodeKind, SpecNodeSeed
from ..domain.tree import build_graph
from ..infra.contracts import StoredMetaRecord
from .contracts import CheckDepsRequest, DepsCheckResult, TargetRef
from .ports import Ports
from .status_context import resolve_issue_status_context


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
    )


def _resolve_specdock_dir(ports: Ports) -> Path:
    if ports.specdock_dir is not None:
        return ports.specdock_dir
    if ports.repo_root is not None:
        return ports.repo_root / "spec-dock"
    raise RuntimeError("specdock_dir is required")


def _find_existing_id_by_num(graph: SpecGraph, *, prefix: str, num: int, local: bool) -> str | None:
    for node_id in graph.nodes_by_id.keys():
        try:
            parsed_prefix, is_local, parsed_num = parse_id(str(node_id))
        except RuntimeError:
            continue
        if parsed_prefix == prefix and parsed_num == num and is_local == local:
            return str(node_id)
    return None


def _resolve_target_node_id(graph: SpecGraph, target: TargetRef) -> str:
    if target.kind == "github_issue":
        if target.github_issue_number is None:
            raise RuntimeError("TargetRef.github_issue_number is required")
        matches = [
            node
            for node in graph.nodes_by_id.values()
            if node.github_issue_number == int(target.github_issue_number) and node.kind in ("initiative", "epic", "issue")
        ]
        if not matches:
            raise RuntimeError(
                f"No node found for github.issue_number={int(target.github_issue_number)}. Create/link the node first."
            )
        if len(matches) > 1:
            ids = ", ".join(sorted(f"{node.kind}:{node.id}" for node in matches))
            raise RuntimeError(f"Ambiguous github.issue_number={int(target.github_issue_number)}: {ids}")
        return matches[0].id

    if target.kind != "node_id":
        raise RuntimeError(f"Unsupported target kind: {target.kind}")

    if target.node_id is None:
        raise RuntimeError("TargetRef.node_id is required")

    raw_id = str(target.node_id).strip().lower()
    prefix, is_local, num = parse_id(raw_id)
    resolved = _find_existing_id_by_num(graph, prefix=prefix, num=num, local=is_local) or format_id(
        prefix, num, local=is_local
    )
    node = graph.nodes_by_id.get(resolved)
    if node is None or node.kind not in ("initiative", "epic", "issue"):
        raise RuntimeError(f"Node not found: {resolved}")
    return node.id


def _append_unique(warnings: list[str], code: str) -> None:
    if code not in warnings:
        warnings.append(code)


def check_deps(req: CheckDepsRequest, ports: Ports) -> DepsCheckResult:
    if ports.deps_topology_reader is None:
        raise RuntimeError("deps_topology_reader is required")

    records = ports.node_reader.load_node_records()
    if not records:
        raise RuntimeError("No nodes found. Create at least one initiative/epic/issue.")
    graph = build_graph([_to_spec_node_seed(record) for record in records])
    specdock_dir = _resolve_specdock_dir(ports)

    topology = ports.deps_topology_reader.load_issue_depends_on_map(specdock_dir, graph)
    warnings: list[str] = list(topology.warnings)
    issue_depends_on_map = dict(topology.issue_depends_on_map)
    validate_deps_cycles(issue_depends_on_map)

    issue_snapshots = None
    if req.use_github:
        if ports.issue_gateway is None:
            raise RuntimeError("issue_gateway is required when --github is enabled")
        if ports.repo_root is None:
            raise RuntimeError("repo_root is required when --github is enabled")
        try:
            issue_snapshots = ports.issue_gateway.issue_index(ports.repo_root, limit=int(req.issue_limit))
        except RuntimeError:
            _append_unique(warnings, "gh_fetch_failed")
            issue_snapshots = []
        else:
            linked_numbers = sorted(
                {
                    int(node.github_issue_number)
                    for node in graph.nodes_by_id.values()
                    if node.kind == "issue" and node.github_issue_number is not None
                }
            )
            indexed = {int(snapshot.issue_number) for snapshot in issue_snapshots}
            missing = [n for n in linked_numbers if n not in indexed]
            if missing:
                _append_unique(warnings, "gh_index_incomplete")

    cached_issue_status_by_id: dict[str, str] = {}
    if ports.derived_state_reader is not None:
        cached_issue_status_by_id = ports.derived_state_reader.load_cached_issue_status_by_id(specdock_dir)

    status_context = resolve_issue_status_context(
        graph,
        github_enabled=req.use_github,
        issue_snapshots=issue_snapshots,
        cached_issue_status_by_id=cached_issue_status_by_id,
    )
    for warning in status_context.warnings:
        _append_unique(warnings, warning)

    target_node_id = _resolve_target_node_id(graph, req.target)
    active_issue_id = None
    if ports.active_state_store is not None:
        active_issue_id = ports.active_state_store.load_active_issue_id(specdock_dir)

    inspection = inspect_target_deps(
        graph,
        issue_depends_on_map=issue_depends_on_map,
        target_id=NodeId(target_node_id),
        issue_statuses=status_context.issue_statuses,
        active_issue_id=active_issue_id,
    )
    return DepsCheckResult(target=req.target, inspection=inspection, warnings=warnings)
