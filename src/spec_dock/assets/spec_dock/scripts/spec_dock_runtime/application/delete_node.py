from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path
from typing import cast

from ..domain.ids import format_id, parse_id
from ..domain.models import SpecGraph, SpecNode, SpecNodeKind, SpecNodeSeed
from ..domain.tree import build_graph
from ..infra.contracts import ActiveManifest, ActiveStateSnapshot, StoredMetaRecord
from .contracts import (
    DeleteTerminalStatus,
    DeleteNodeRequest,
    DeleteNodeResult,
    DeleteRemoteCloseBuckets,
    DeleteValidationReason,
)
from .github_issue_targets import normalize_repo_slug
from .ports import Ports

_NUM_RE = re.compile(r"^[0-9]+$")


@dataclass(frozen=True)
class _CanonicalRemoteIssue:
    repo_slug: str
    issue_number: int
    identifier: str


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


def _metadata_failure_result(
    *,
    target_id: str | None,
    offending_node_ids: list[str],
    messages_by_node_id: dict[str, str],
) -> DeleteNodeResult:
    sorted_ids = sorted(offending_node_ids)
    return DeleteNodeResult(
        status="metadata_validation_failed",
        target_id=target_id,
        deleted_node_ids=[],
        remaining_node_ids=[],
        remote_close=_empty_remote_close(),
        offending_node_ids=sorted_ids,
        validation_reasons=[
            DeleteValidationReason(
                node_id=node_id,
                code="metadata_validation_failed",
                message=messages_by_node_id.get(node_id, "metadata_validation_failed"),
            )
            for node_id in sorted_ids
        ],
        active_restore_result=None,
        recovery_guidance=[],
        dependency_scrub_failures=[],
        warnings=[],
    )


def _remote_close_failed_result(
    *,
    target_id: str,
    remote_close: DeleteRemoteCloseBuckets,
    warnings: list[str] | None = None,
) -> DeleteNodeResult:
    return DeleteNodeResult(
        status="remote_close_failed",
        target_id=target_id,
        deleted_node_ids=[],
        remaining_node_ids=[],
        remote_close=remote_close,
        offending_node_ids=[],
        validation_reasons=[],
        active_restore_result=None,
        recovery_guidance=[],
        dependency_scrub_failures=[],
        warnings=list(warnings or []),
    )


def _iter_managed_nodes(graph: SpecGraph) -> list[SpecNode]:
    return [node for node in graph.nodes_by_id.values() if node.kind in ("initiative", "epic", "issue")]


def _normalize_issue_number(value: object) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    if isinstance(value, str):
        raw = value.strip()
        if not raw or _NUM_RE.fullmatch(raw) is None:
            return None
        normalized = int(raw)
        return normalized if normalized > 0 else None
    return None


def _validate_node_metadata(
    node: SpecNode,
    *,
    require_meta_file: bool = True,
) -> tuple[_CanonicalRemoteIssue | None, str | None]:
    if require_meta_file and not node.meta_path.exists():
        return None, f"missing metadata file: {node.meta_path.as_posix()}"

    owner = node.github_repo_owner
    repo = node.github_repo_name
    issue_number_raw = node.github_issue_number
    has_owner = owner is not None
    has_repo = repo is not None
    has_issue = issue_number_raw is not None
    present_count = int(has_owner) + int(has_repo) + int(has_issue)
    if present_count == 0:
        return None, None
    if present_count != 3:
        return None, "partial github linkage is invalid"
    if not isinstance(owner, str) or not isinstance(repo, str):
        return None, "github repo scope must be string values"
    repo_slug = normalize_repo_slug(owner, repo)
    if repo_slug is None:
        return None, "github repo scope must be non-empty strings"
    issue_number = _normalize_issue_number(issue_number_raw)
    if issue_number is None:
        return None, "github issue number must be a positive integer"
    return _CanonicalRemoteIssue(
        repo_slug=repo_slug,
        issue_number=issue_number,
        identifier=f"{repo_slug}#{issue_number}",
    ), None


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
    matches: list[SpecNode] = []
    for node in _iter_managed_nodes(graph):
        try:
            node_prefix, node_local, node_num = parse_id(node.id)
        except RuntimeError:
            # Ignore malformed unrelated ids during selector resolution.
            continue
        if node_prefix == prefix and node_local == is_local and node_num == num:
            matches.append(node)

    if not matches:
        return None, _result(
            status="target_not_found",
            validation_code="target_not_found",
            validation_message=f"target not found: {canonical}",
        )
    invalid_messages: dict[str, str] = {}
    for node in matches:
        _canonical_remote, validation_error = _validate_node_metadata(
            node,
            require_meta_file=node.path.exists(),
        )
        if validation_error is not None:
            invalid_messages[node.id] = validation_error
    if invalid_messages:
        sorted_invalid_ids = sorted(invalid_messages)
        resolved_target_id = sorted_invalid_ids[0] if len(sorted_invalid_ids) == 1 else None
        return None, _metadata_failure_result(
            target_id=resolved_target_id,
            offending_node_ids=sorted_invalid_ids,
            messages_by_node_id=invalid_messages,
        )

    if len(matches) > 1:
        return None, _result(
            status="ambiguous_target",
            offending_node_ids=[node.id for node in matches],
            validation_code="ambiguous_target",
            validation_message=f"ambiguous selector: {canonical}",
        )
    return matches[0].id, None


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
    matches: list[SpecNode] = []
    for node in _iter_managed_nodes(graph):
        normalized_issue_number = _normalize_issue_number(node.github_issue_number)
        if normalized_issue_number == issue_number:
            matches.append(node)
    if not matches:
        return None, _result(
            status="target_not_found",
            validation_code="target_not_found",
            validation_message=f"no node linked to github issue: {issue_number}",
        )
    invalid_messages: dict[str, str] = {}
    for node in matches:
        _canonical_remote, validation_error = _validate_node_metadata(
            node,
            require_meta_file=node.path.exists(),
        )
        if validation_error is not None:
            invalid_messages[node.id] = validation_error
    if invalid_messages:
        sorted_invalid_ids = sorted(invalid_messages)
        resolved_target_id = sorted_invalid_ids[0] if len(sorted_invalid_ids) == 1 else None
        return None, _metadata_failure_result(
            target_id=resolved_target_id,
            offending_node_ids=sorted_invalid_ids,
            messages_by_node_id=invalid_messages,
        )

    if len(matches) > 1:
        return None, _result(
            status="ambiguous_target",
            offending_node_ids=[node.id for node in matches],
            validation_code="ambiguous_target",
            validation_message=f"ambiguous github issue selector: {issue_number}",
        )
    return matches[0].id, None


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


def _subtree_remote_close_targets(
    *,
    subtree_ids: set[str],
    graph: SpecGraph,
) -> tuple[list[_CanonicalRemoteIssue] | None, DeleteNodeResult | None]:
    invalid_messages: dict[str, str] = {}
    canonical_targets: dict[tuple[str, int], _CanonicalRemoteIssue] = {}
    for node_id in sorted(subtree_ids):
        node = graph.nodes_by_id.get(node_id)
        if node is None:
            continue
        canonical_remote, validation_error = _validate_node_metadata(node)
        if validation_error is not None:
            invalid_messages[node.id] = validation_error
            continue
        if canonical_remote is None:
            continue
        canonical_targets[(canonical_remote.repo_slug, canonical_remote.issue_number)] = canonical_remote
    if invalid_messages:
        return None, _metadata_failure_result(
            target_id=None,
            offending_node_ids=sorted(invalid_messages),
            messages_by_node_id=invalid_messages,
        )
    ordered_keys = sorted(canonical_targets.keys(), key=lambda item: (item[0], item[1]))
    ordered_targets = [canonical_targets[key] for key in ordered_keys]
    return ordered_targets, None


def _close_remote_issues_barrier(
    *,
    target_id: str,
    required_targets: list[_CanonicalRemoteIssue],
    ports: Ports,
    active_snapshot: ActiveStateSnapshot | None,
) -> tuple[DeleteRemoteCloseBuckets, DeleteNodeResult | None]:
    remote_close = _empty_remote_close()
    if not required_targets:
        return remote_close, None

    if ports.issue_gateway is None or ports.repo_root is None:
        first = required_targets[0].identifier
        remote_close.failed.append(first)
        remote_close.skipped_not_attempted.extend([item.identifier for item in required_targets[1:]])
        return remote_close, _remote_close_failed_result(
            target_id=target_id,
            remote_close=remote_close,
            warnings=["issue_gateway_unavailable_for_delete"],
        )

    for index, target in enumerate(required_targets):
        try:
            current = ports.issue_gateway.issue_view_snapshot(
                ports.repo_root,
                target.issue_number,
                repo_slug=target.repo_slug,
            )
        except RuntimeError:
            remote_close.failed.append(target.identifier)
            remote_close.skipped_not_attempted.extend([item.identifier for item in required_targets[index + 1 :]])
            warnings: list[str] = []
            if ports.active_state_store is not None and active_snapshot is not None:
                try:
                    ports.active_state_store.restore_previous_state(_resolve_specdock_dir(ports), active_snapshot)
                except Exception:
                    warnings.append("active_restore_failed")
            return remote_close, _remote_close_failed_result(
                target_id=target_id,
                remote_close=remote_close,
                warnings=warnings,
            )

        if str(current.state).strip().upper() == "CLOSED":
            remote_close.noop_already_closed.append(target.identifier)
            continue

        try:
            closed = ports.issue_gateway.issue_close(
                ports.repo_root,
                target.issue_number,
                repo_slug=target.repo_slug,
            )
        except RuntimeError:
            remote_close.failed.append(target.identifier)
            remote_close.skipped_not_attempted.extend([item.identifier for item in required_targets[index + 1 :]])
            warnings = []
            if ports.active_state_store is not None and active_snapshot is not None:
                try:
                    ports.active_state_store.restore_previous_state(_resolve_specdock_dir(ports), active_snapshot)
                except Exception:
                    warnings.append("active_restore_failed")
            return remote_close, _remote_close_failed_result(
                target_id=target_id,
                remote_close=remote_close,
                warnings=warnings,
            )

        if str(closed.state).strip().upper() == "CLOSED":
            remote_close.closed.append(target.identifier)
            continue
        remote_close.failed.append(target.identifier)
        remote_close.skipped_not_attempted.extend([item.identifier for item in required_targets[index + 1 :]])
        warnings = []
        if ports.active_state_store is not None and active_snapshot is not None:
            try:
                ports.active_state_store.restore_previous_state(_resolve_specdock_dir(ports), active_snapshot)
            except Exception:
                warnings.append("active_restore_failed")
        return remote_close, _remote_close_failed_result(
            target_id=target_id,
            remote_close=remote_close,
            warnings=warnings,
        )
    return remote_close, None


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

    required_remote_targets, subtree_metadata_failure = _subtree_remote_close_targets(
        subtree_ids=subtree_ids,
        graph=graph,
    )
    if subtree_metadata_failure is not None:
        return DeleteNodeResult(
            status="metadata_validation_failed",
            target_id=target.id,
            deleted_node_ids=[],
            remaining_node_ids=[],
            remote_close=subtree_metadata_failure.remote_close,
            offending_node_ids=subtree_metadata_failure.offending_node_ids,
            validation_reasons=subtree_metadata_failure.validation_reasons,
            active_restore_result=None,
            recovery_guidance=[],
            dependency_scrub_failures=[],
            warnings=[],
        )
    if required_remote_targets is None:
        return _metadata_failure_result(
            target_id=target.id,
            offending_node_ids=[],
            messages_by_node_id={},
        )

    active_snapshot: ActiveStateSnapshot | None = None
    if required_remote_targets and ports.active_state_store is not None:
        active_snapshot = ports.active_state_store.snapshot_current_state(_resolve_specdock_dir(ports))

    remote_close, remote_failure = _close_remote_issues_barrier(
        target_id=target.id,
        required_targets=required_remote_targets,
        ports=ports,
        active_snapshot=active_snapshot,
    )
    if remote_failure is not None:
        return remote_failure

    # S01 I2 scope: metadata + remote-close barrier contract only. Actual local delete starts from later slices.
    return _result(
        status="confirmation_required",
        target_id=target.id,
        validation_code="confirmation_required",
        validation_message="preflight and remote-close barrier passed; local delete is deferred in S01 I2",
    )
