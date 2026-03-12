from __future__ import annotations

from .models import SpecGraph, SpecNode, SpecNodeSeed


def build_graph(seeds: list[SpecNodeSeed]) -> SpecGraph:
    """Build an immutable-friendly graph map from normalized node seeds."""
    nodes_by_id: dict[str, SpecNode] = {}

    for seed in seeds:
        node_id = str(seed.id).strip()
        if node_id in nodes_by_id:
            raise RuntimeError(f"Duplicate id detected: {node_id} ({seed.meta_path})")
        nodes_by_id[node_id] = SpecNode(
            kind=seed.kind,
            id=node_id,
            title=seed.title,
            slug=seed.slug,
            path=seed.path,
            meta_path=seed.meta_path,
            parent_id=seed.parent_id,
            initiative_id=seed.initiative_id,
            epic_id=seed.epic_id,
            github_issue_number=seed.github_issue_number,
        )

    return SpecGraph(nodes_by_id=nodes_by_id)

