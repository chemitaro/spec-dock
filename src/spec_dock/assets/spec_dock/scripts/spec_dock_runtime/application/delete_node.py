from __future__ import annotations

import re
from pathlib import Path
from typing import cast

from ..domain.ids import format_id, parse_id
from ..domain.models import SpecGraph, SpecNode, SpecNodeKind, SpecNodeSeed
from ..domain.tree import build_graph
from ..infra.contracts import ActiveManifest, StoredMetaRecord
from .contracts import (
    DeleteTerminalStatus,
    DeleteNodeRequest,
    DeleteNodeResult,
    DeleteRemoteCloseBuckets,
    DeleteValidationReason,
)
from .ports import Ports

_NUM_RE = re.compile(r"^[0-9]+$")


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


def _empty_remote_close() -> DeleteRemoteCloseBuckets:
    return DeleteRemoteCloseBuckets(
        closed=[],
        noop_already_closed=[],
        failed=[],
        skipped_not_attempted=[],
    )


def _result(
    *,
    status: str,
    target_id: str | None = None,
    offending_node_ids: list[str] | None = None,
    validation_code: str | None = None,
    validation_message: str | None = None,
) -> DeleteNodeResult:
    reasons: list[DeleteValidationReason] = []
    if validation_code is not None:
        reasons.append(
            DeleteValidationReason(
                node_id=target_id,
                code=validation_code,
                message=validation_message or validation_code,
            )
        )
    return DeleteNodeResult(
        status=cast(DeleteTerminalStatus, status),
        target_id=target_id,
        deleted_node_ids=[],
        remaining_node_ids=[target_id] if status == "ok" and target_id is not None else [],
        remote_close=_empty_remote_close() if status == "ok" else None,
        offending_node_ids=sorted(offending_node_ids or []),
        validation_reasons=reasons,
        active_restore_result="not_needed" if status == "ok" else None,
        recovery_guidance=[],
        dependency_scrub_failures=[],
        warnings=[],
    )


def _iter_managed_nodes(graph: SpecGraph) -> list[SpecNode]:
    return [node for node in graph.nodes_by_id.values() if node.kind in ("initiative", "epic", "issue")]


def _resolve_node_id_matches(graph: SpecGraph, raw_input: str) -> tuple[str | None, DeleteNodeResult | None]:
    raw = str(raw_input).strip().lower()
    if not raw:
        return None, _result(
            status="invalid_selector_syntax",
            validation_code="invalid_selector_syntax",
            validation_message="node id selector is required",
        )
    try:
        prefix, is_local, num = parse_id(raw)
    except RuntimeError:
        return None, _result(
            status="invalid_selector_syntax",
            validation_code="invalid_selector_syntax",
            validation_message=f"invalid node id selector: {raw_input}",
        )
    if prefix not in ("init", "epic", "iss"):
        return None, _result(
            status="invalid_selector_syntax",
            validation_code="invalid_selector_syntax",
            validation_message=f"unsupported node id prefix: {prefix}",
        )

    canonical = format_id(prefix, num, local=is_local)
    matches = []
    for node in _iter_managed_nodes(graph):
        try:
            node_prefix, node_local, node_num = parse_id(node.id)
        except RuntimeError:
            # Ignore malformed unrelated ids during selector resolution.
            continue
        if node_prefix == prefix and node_local == is_local and node_num == num:
            matches.append(node.id)

    if not matches:
        return None, _result(
            status="target_not_found",
            validation_code="target_not_found",
            validation_message=f"target not found: {canonical}",
        )
    if len(matches) > 1:
        return None, _result(
            status="ambiguous_target",
            offending_node_ids=matches,
            validation_code="ambiguous_target",
            validation_message=f"ambiguous selector: {canonical}",
        )
    return matches[0], None


def _resolve_github_issue_matches(graph: SpecGraph, raw_input: str) -> tuple[str | None, DeleteNodeResult | None]:
    raw = str(raw_input).strip()
    if not raw or _NUM_RE.fullmatch(raw) is None:
        return None, _result(
            status="invalid_selector_syntax",
            validation_code="invalid_selector_syntax",
            validation_message=f"invalid --github-issue value: {raw_input}",
        )
    issue_number = int(raw)
    if issue_number <= 0:
        return None, _result(
            status="invalid_selector_syntax",
            validation_code="invalid_selector_syntax",
            validation_message=f"--github-issue must be a positive integer: {raw_input}",
        )
    matches = sorted(
        [
            node.id
            for node in _iter_managed_nodes(graph)
            if node.github_issue_number is not None and int(node.github_issue_number) == issue_number
        ]
    )
    if not matches:
        return None, _result(
            status="target_not_found",
            validation_code="target_not_found",
            validation_message=f"no node linked to github issue: {issue_number}",
        )
    if len(matches) > 1:
        return None, _result(
            status="ambiguous_target",
            offending_node_ids=matches,
            validation_code="ambiguous_target",
            validation_message=f"ambiguous github issue selector: {issue_number}",
        )
    return matches[0], None


def _resolve_target_id(req: DeleteNodeRequest, graph: SpecGraph) -> tuple[str | None, DeleteNodeResult | None]:
    selectors = 0
    has_positional = bool(str(req.positional_target or "").strip())
    has_node_id = bool(str(req.node_id or "").strip())
    has_github_issue = req.github_issue is not None and str(req.github_issue).strip() != ""
    selectors += 1 if has_positional else 0
    selectors += 1 if has_node_id else 0
    selectors += 1 if has_github_issue else 0

    if selectors == 0:
        return None, _result(
            status="invalid_selector_combination",
            validation_code="invalid_selector_combination",
            validation_message="target selector is required",
        )
    if selectors > 1:
        return None, _result(
            status="invalid_selector_combination",
            validation_code="invalid_selector_combination",
            validation_message="choose exactly one of <target>, --id, --github-issue",
        )

    if has_github_issue:
        return _resolve_github_issue_matches(graph, str(req.github_issue))
    if has_node_id:
        return _resolve_node_id_matches(graph, str(req.node_id))
    return _resolve_node_id_matches(graph, str(req.positional_target))


def _subtree_ids(target: SpecNode, graph: SpecGraph) -> set[str]:
    ids = {target.id}
    if target.kind == "initiative":
        for node in graph.nodes_by_id.values():
            if node.initiative_id == target.id:
                ids.add(node.id)
    elif target.kind == "epic":
        for node in graph.nodes_by_id.values():
            if node.epic_id == target.id:
                ids.add(node.id)
    return ids


def _subtree_issue_ids(target: SpecNode, graph: SpecGraph) -> set[str]:
    if target.kind == "issue":
        return {target.id}
    if target.kind == "epic":
        return {node.id for node in graph.nodes_by_id.values() if node.kind == "issue" and node.epic_id == target.id}
    return {
        node.id
        for node in graph.nodes_by_id.values()
        if node.kind == "issue" and node.initiative_id == target.id
    }


def _active_ids(manifest: ActiveManifest | None) -> set[str]:
    if manifest is None:
        return set()
    out: set[str] = set()
    if manifest.initiative is not None:
        out.add(manifest.initiative.id)
    if manifest.epic is not None:
        out.add(manifest.epic.id)
    if manifest.issue is not None:
        out.add(manifest.issue.id)
    return out


def delete_node(req: DeleteNodeRequest, ports: Ports) -> DeleteNodeResult:
    records = ports.node_reader.load_node_records()
    if not records:
        return _result(
            status="target_not_found",
            validation_code="target_not_found",
            validation_message="no nodes found",
        )
    graph = build_graph([_to_spec_node_seed(record) for record in records])

    target_id, selector_failure = _resolve_target_id(req, graph)
    if selector_failure is not None:
        return selector_failure
    if target_id is None:
        return _result(
            status="target_not_found",
            validation_code="target_not_found",
            validation_message="target not found",
        )
    target = graph.nodes_by_id.get(target_id)
    if target is None:
        return _result(
            status="target_not_found",
            validation_code="target_not_found",
            validation_message=f"target not found: {target_id}",
        )
    if not target.path.exists():
        return _result(
            status="target_not_found",
            target_id=target.id,
            validation_code="target_not_found",
            validation_message=f"target path missing: {target.path.as_posix()}",
        )

    if not req.confirmed:
        return _result(
            status="confirmation_required",
            target_id=target.id,
            validation_code="confirmation_required",
            validation_message="destructive delete requires --yes",
        )
    if target.kind in ("initiative", "epic") and not req.recursive:
        return _result(
            status="recursive_required",
            target_id=target.id,
            validation_code="recursive_required",
            validation_message=f"{target.kind} delete requires --recursive",
        )

    subtree_ids = _subtree_ids(target, graph)
    if not req.force and ports.active_state_store is not None:
        specdock_dir = _resolve_specdock_dir(ports)
        active_manifest = ports.active_state_store.load_active_manifest(specdock_dir).manifest
        active_conflicts = sorted(_active_ids(active_manifest) & subtree_ids)
        if active_conflicts:
            return _result(
                status="active_conflict",
                target_id=target.id,
                offending_node_ids=active_conflicts,
                validation_code="active_conflict",
                validation_message="active selection intersects delete target",
            )

    if not req.force and ports.deps_topology_reader is not None:
        specdock_dir = _resolve_specdock_dir(ports)
        topology = ports.deps_topology_reader.load_issue_depends_on_map(specdock_dir, graph)
        dep_map = dict(topology.issue_depends_on_map)
        subtree_issue_ids = _subtree_issue_ids(target, graph)
        dep_conflicts: set[str] = set()

        for issue_id in sorted(subtree_issue_ids):
            for dep_id in sorted(dep_map.get(issue_id, [])):
                if dep_id not in subtree_issue_ids:
                    dep_conflicts.add(issue_id)
                    dep_conflicts.add(dep_id)
        for issue_id, deps in dep_map.items():
            if issue_id in subtree_issue_ids:
                continue
            for dep_id in deps:
                if dep_id in subtree_issue_ids:
                    dep_conflicts.add(issue_id)
                    dep_conflicts.add(dep_id)

        if dep_conflicts:
            return _result(
                status="dependency_conflict",
                target_id=target.id,
                offending_node_ids=sorted(dep_conflicts),
                validation_code="dependency_conflict",
                validation_message="dependency edge crosses delete subtree boundary",
            )

    # S01 I1 scope: preflight contract only. Actual delete starts from later slices.
    return _result(
        status="confirmation_required",
        target_id=target.id,
        validation_code="confirmation_required",
        validation_message="preflight passed; delete execution is deferred in S01 I1",
    )
