from __future__ import annotations

from pathlib import Path
from typing import Any

from ..domain.ids import deps_node_sort_key, find_existing_id_by_num, format_id, parse_id
from ..domain.models import SpecGraph
from .contracts import DepsTopologyLoadResult
from .json_store import load_json


def _load_deps_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": 1, "depends_on": []}

    data = load_json(path)
    if not isinstance(data, dict):
        raise RuntimeError(f"Invalid deps.json schema: {path}: expected a JSON object")

    if data.get("schema_version") != 1:
        raise RuntimeError(f"Invalid deps.json schema: {path}: schema_version must be 1")

    depends_on = data.get("depends_on")
    if not isinstance(depends_on, list):
        raise RuntimeError(f"Invalid deps.json schema: {path}: depends_on must be a list")

    for i, ref in enumerate(depends_on):
        if isinstance(ref, bool):
            raise RuntimeError(f"Invalid deps.json schema: {path}: depends_on[{i}] must be a string or int")
        if isinstance(ref, (str, int)):
            continue
        raise RuntimeError(f"Invalid deps.json schema: {path}: depends_on[{i}] must be a string or int")

    return {"schema_version": 1, "depends_on": depends_on}


def _find_node_by_github_issue_number(graph: SpecGraph, *, issue_number: int) -> str:
    matches = [
        node
        for node in graph.nodes_by_id.values()
        if node.github_issue_number == issue_number and node.kind in ("initiative", "epic", "issue")
    ]
    if not matches:
        raise RuntimeError(f"No node found for github.issue_number={issue_number}. Create/link the node first.")
    if len(matches) > 1:
        ids = ", ".join(sorted(f"{node.kind}:{node.id}" for node in matches))
        raise RuntimeError(f"Ambiguous github.issue_number={issue_number}: {ids}")
    return matches[0].id


def _resolve_dep_ref(graph: SpecGraph, ref: Any, *, src_path: Path) -> str:
    if isinstance(ref, bool):
        raise RuntimeError(f"Unresolved dependency ref: {ref!r} (in {src_path})")

    if isinstance(ref, int):
        try:
            return _find_node_by_github_issue_number(graph, issue_number=int(ref))
        except RuntimeError as e:
            raise RuntimeError(f"Unresolved dependency ref: {ref!r} (in {src_path}): {e}") from e

    if isinstance(ref, str):
        raw = ref.strip()
        if not raw:
            raise RuntimeError(f"Unresolved dependency ref: {ref!r} (in {src_path})")
        if raw.isdigit():
            try:
                return _find_node_by_github_issue_number(graph, issue_number=int(raw))
            except RuntimeError as e:
                raise RuntimeError(f"Unresolved dependency ref: {ref!r} (in {src_path}): {e}") from e

        try:
            prefix, is_local, num = parse_id(raw.lower())
        except RuntimeError as e:
            raise RuntimeError(f"Unresolved dependency ref: {ref!r} (in {src_path}): {e}") from e
        if prefix not in ("init", "epic", "iss"):
            raise RuntimeError(
                f"Unresolved dependency ref: {ref!r} (in {src_path}): unsupported id prefix: {prefix}"
            )

        existing = find_existing_id_by_num(graph.nodes_by_id, prefix=prefix, num=num, local=is_local)
        if not existing:
            normalized = format_id(prefix, num, local=is_local)
            raise RuntimeError(f"Unresolved dependency ref: {ref!r} (in {src_path}): node not found ({normalized})")
        return existing

    raise RuntimeError(
        f"Unresolved dependency ref: {ref!r} (in {src_path}): unsupported type: {type(ref).__name__}"
    )


def _is_descendant(graph: SpecGraph, *, src_id: str, candidate_dep_id: str) -> bool:
    current_id = candidate_dep_id
    visited: set[str] = set()
    while True:
        current = graph.nodes_by_id.get(current_id)
        if current is None or not current.parent_id:
            return False
        parent_id = current.parent_id
        if parent_id == src_id:
            return True
        if parent_id in visited:
            return False
        visited.add(parent_id)
        current_id = parent_id


def _resolved_direct_depends_on(graph: SpecGraph, src_id: str) -> list[str]:
    src = graph.nodes_by_id.get(src_id)
    if src is None:
        raise RuntimeError(f"Internal error: missing node: {src_id}")
    deps_path = src.path / "deps.json"
    deps = _load_deps_json(deps_path)
    resolved = [_resolve_dep_ref(graph, ref, src_path=deps_path) for ref in (deps.get("depends_on") or [])]
    deduped = sorted(set(resolved), key=deps_node_sort_key)
    for dep_id in deduped:
        if _is_descendant(graph, src_id=src_id, candidate_dep_id=dep_id):
            raise RuntimeError(f"Invalid dependency: {src_id} cannot depend on its descendant {dep_id} (in {deps_path})")
    return deduped


def _issue_ids_for_dep_node(graph: SpecGraph, node_id: str) -> list[str]:
    node = graph.nodes_by_id.get(node_id)
    if node is None:
        raise RuntimeError(f"Node not found: {node_id}")
    if node.kind == "issue":
        return [node.id]
    if node.kind == "epic":
        return sorted(
            [n.id for n in graph.nodes_by_id.values() if n.kind == "issue" and n.epic_id == node.id],
            key=deps_node_sort_key,
        )
    if node.kind == "initiative":
        return sorted(
            [n.id for n in graph.nodes_by_id.values() if n.kind == "issue" and n.initiative_id == node.id],
            key=deps_node_sort_key,
        )
    raise RuntimeError(f"Unsupported dependency node type: {node.kind} ({node_id})")


def load_issue_depends_on_map(specdock_dir: Path, graph: SpecGraph) -> DepsTopologyLoadResult:
    del specdock_dir
    dep_node_ids = sorted(
        [node_id for node_id, node in graph.nodes_by_id.items() if node.kind in ("initiative", "epic", "issue")],
        key=deps_node_sort_key,
    )
    issue_ids = sorted(
        [node_id for node_id, node in graph.nodes_by_id.items() if node.kind == "issue"],
        key=deps_node_sort_key,
    )
    issue_depends_on: dict[str, set[str]] = {issue_id: set() for issue_id in issue_ids}

    warning_codes: list[str] = []
    warned_empty_refs: set[tuple[str, str]] = set()

    for src_id in dep_node_ids:
        src_issue_ids = _issue_ids_for_dep_node(graph, src_id)
        if not src_issue_ids:
            continue
        src_node = graph.nodes_by_id[src_id]
        deps_path = src_node.path / "deps.json"
        direct_dep_node_ids = _resolved_direct_depends_on(graph, src_id)

        for dep_node_id in direct_dep_node_ids:
            dep_issue_ids = _issue_ids_for_dep_node(graph, dep_node_id)
            if not dep_issue_ids:
                key = (src_id, dep_node_id)
                if key not in warned_empty_refs:
                    warned_empty_refs.add(key)
                    if "deps_ref_expanded_to_empty" not in warning_codes:
                        warning_codes.append("deps_ref_expanded_to_empty")
                continue

            for src_issue_id in src_issue_ids:
                for dep_issue_id in dep_issue_ids:
                    if dep_issue_id == src_issue_id:
                        raise RuntimeError(
                            "Invalid dependency: self edge produced: "
                            f"{src_issue_id} depends_on={dep_node_id} (in {deps_path})"
                        )
                    issue_depends_on[src_issue_id].add(dep_issue_id)

    compiled = {
        issue_id: sorted(list(issue_depends_on.get(issue_id, set())), key=deps_node_sort_key)
        for issue_id in issue_ids
    }
    return DepsTopologyLoadResult(issue_depends_on_map=compiled, warnings=warning_codes)
