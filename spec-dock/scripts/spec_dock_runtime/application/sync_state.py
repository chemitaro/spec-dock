from __future__ import annotations

from datetime import datetime
from dataclasses import replace
from pathlib import Path
from typing import Literal, cast

from ..domain.active import infer_active_node_from_branch
from ..domain.deps import build_deps_state, build_effective_deps_map, evaluate_readiness, validate_deps_cycles
from ..domain.models import ActiveSelection, DepsEvaluation, DepsState, IssueSnapshot, NodeId, SpecNodeKind, SpecNodeSeed
from ..domain.status import build_progress_map
from ..domain.tree import build_graph, select_active_chain
from ..domain.validation import validate_graph_and_deps
from ..infra.contracts import ActiveManifest, StoredMetaRecord
from ..presentation.contracts import ArtifactBundle
from ..presentation.json_state import (
    render_context_pack,
    render_deps_issues_artifact,
    render_index_artifact,
    render_tree_artifact,
)
from ..presentation.markdown import render_dashboard
from .contracts import (
    ActiveUpdateOutcome,
    ArtifactWriteFailure,
    ArtifactWriteResult,
    SyncCommandResult,
    SyncRequest,
    SyncStateResult,
)
from .ports import Ports
from .set_active import build_active_manifest, commit_active_state
from .status_context import resolve_issue_status_context


class _ArtifactWriteExecutionError(RuntimeError):
    def __init__(self, *, status: Literal["failed_before_write", "failed_partial_or_stale"], reason: str):
        super().__init__(reason)
        self.status = status
        self.reason = reason


def _append_unique(values: list[str], value: str) -> None:
    if value not in values:
        values.append(value)


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


def _manifest_to_active_selection(manifest: ActiveManifest | None) -> ActiveSelection | None:
    if manifest is None:
        return None
    return ActiveSelection(
        initiative_id=manifest.initiative.id if manifest.initiative is not None else None,
        epic_id=manifest.epic.id if manifest.epic is not None else None,
        issue_id=manifest.issue.id if manifest.issue is not None else None,
    )


def _now_iso_from_ports(ports: Ports) -> str:
    if ports.clock is not None and hasattr(ports.clock, "now_iso"):
        value = ports.clock.now_iso()
        return str(value)
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _require_sync_runner(ports: Ports):
    runner = ports.sync_legacy_runner
    if runner is None:
        raise RuntimeError("sync_legacy_runner is required")
    return runner


def _can_collect_natively(ports: Ports) -> bool:
    return ports.deps_topology_reader is not None


def _can_sync_natively(ports: Ports) -> bool:
    return _can_collect_natively(ports) and ports.artifact_writer is not None


def _load_active_selection(
    ports: Ports,
    *,
    active_manifest_mode: Literal["migrate", "no_migrate"],
) -> tuple[ActiveSelection | None, list[str]]:
    if ports.active_state_store is None:
        return (None, [])

    specdock_dir = _resolve_specdock_dir(ports)
    if active_manifest_mode == "no_migrate":
        load_result = ports.active_state_store.load_active_manifest_no_migrate(specdock_dir)
    else:
        load_result = ports.active_state_store.load_active_manifest(specdock_dir)
    return (_manifest_to_active_selection(load_result.manifest), list(load_result.warnings))


def collect_sync_state(
    req: SyncRequest,
    ports: Ports,
    *,
    active_manifest_mode: Literal["migrate", "no_migrate"] = "migrate",
) -> SyncStateResult:
    if not _can_collect_natively(ports):
        runner = _require_sync_runner(ports)
        result = runner.run_sync(req, active_manifest_mode=active_manifest_mode)
        return result.state

    records = ports.node_reader.load_node_records()
    if not records:
        raise RuntimeError("No nodes found. Create at least one initiative/epic/issue.")
    graph = build_graph([_to_spec_node_seed(record) for record in records])
    specdock_dir = _resolve_specdock_dir(ports)

    warnings: list[str] = []
    deps_preflight_error: str | None = None
    issue_depends_on_map: dict[str, list[str]] = {}

    validation = validate_graph_and_deps(graph, issue_depends_on_map=None, repo_root=ports.repo_root)
    if validation.errors:
        if req.force:
            deps_preflight_error = f"preflight validate failed: {validation.errors[0]}"
            _append_unique(warnings, "deps_preflight_failed")
        else:
            raise RuntimeError(f"preflight validate failed: {validation.errors[0]}")
    else:
        topology = ports.deps_topology_reader.load_issue_depends_on_map(specdock_dir, graph)
        issue_depends_on_map = dict(topology.issue_depends_on_map)
        for warning in topology.warnings:
            _append_unique(warnings, warning)
        try:
            validate_deps_cycles(issue_depends_on_map)
            validate_graph_and_deps(graph, issue_depends_on_map=issue_depends_on_map, repo_root=ports.repo_root)
            effective_deps_map = build_effective_deps_map(graph, issue_depends_on_map)
            validate_deps_cycles(effective_deps_map)
        except RuntimeError as error:
            if req.force:
                deps_preflight_error = str(error)
                _append_unique(warnings, "deps_preflight_failed")
            else:
                raise

    issue_snapshots = None
    github_snapshot_by_issue_number: dict[int, IssueSnapshot] = {}
    if req.github_enabled:
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
            github_snapshot_by_issue_number = {
                int(snapshot.issue_number): snapshot
                for snapshot in issue_snapshots
            }
            linked_numbers = sorted(
                {
                    int(node.github_issue_number)
                    for node in graph.nodes_by_id.values()
                    if node.kind == "issue" and node.github_issue_number is not None
                }
            )
            indexed_numbers = {int(snapshot.issue_number) for snapshot in issue_snapshots}
            missing = [num for num in linked_numbers if num not in indexed_numbers]
            if missing:
                _append_unique(warnings, "gh_index_incomplete")

    cached_issue_status_by_id: dict[str, str] = {}
    if ports.derived_state_reader is not None:
        cached_issue_status_by_id = ports.derived_state_reader.load_cached_issue_status_by_id(specdock_dir)
    status_context = resolve_issue_status_context(
        graph,
        github_enabled=req.github_enabled,
        issue_snapshots=issue_snapshots,
        cached_issue_status_by_id=cached_issue_status_by_id,
    )
    for warning in status_context.warnings:
        _append_unique(warnings, warning)

    active_selection, active_warnings = _load_active_selection(ports, active_manifest_mode=active_manifest_mode)
    for warning in active_warnings:
        _append_unique(warnings, warning)

    deps_state: DepsState
    deps_eval_by_id: dict[str, DepsEvaluation]
    if deps_preflight_error is None:
        effective_deps_map = build_effective_deps_map(graph, issue_depends_on_map)
        deps_state = build_deps_state(
            graph,
            effective_deps_map,
            status_context.issue_statuses,
            active_selection,
            warnings=[],
        )
        deps_eval_by_id = {}
        for node_id, node in graph.nodes_by_id.items():
            if node.kind != "issue":
                continue
            deps_eval_by_id[node_id] = evaluate_readiness(
                graph,
                issue_depends_on_map,
                NodeId(node_id),
                status_context.issue_statuses,
            )
    else:
        deps_state = DepsState(nodes=[], warnings=[])
        deps_eval_by_id = {}

    progress = build_progress_map(graph, status_context.issue_statuses)
    return SyncStateResult(
        graph=graph,
        active=active_selection,
        issue_statuses=status_context.issue_statuses,
        progress=progress,
        deps_state=deps_state,
        deps_eval_by_id=deps_eval_by_id,
        generated_at=_now_iso_from_ports(ports),
        warnings=warnings,
        deps_preflight_error=deps_preflight_error,
        issue_depends_on_map=issue_depends_on_map,
        github_snapshot_by_issue_number=github_snapshot_by_issue_number,
    )


def maybe_auto_update_from_branch(
    state: SyncStateResult,
    ports: Ports,
) -> tuple[SyncStateResult, ActiveUpdateOutcome | None]:
    if ports.repo_root is None or ports.git_gateway is None:
        return (state, None)
    if ports.active_state_store is None:
        raise RuntimeError("active_state_store is required for sync active auto-update")

    try:
        branch = ports.git_gateway.current_branch_or_none(ports.repo_root)
    except RuntimeError:
        return (state, None)
    if not branch:
        return (state, None)

    inferred_node, reason = infer_active_node_from_branch(state.graph, branch=branch)
    if inferred_node is None:
        return (state, ActiveUpdateOutcome(applied=False, reason=reason))

    selection = select_active_chain(state.graph, NodeId(inferred_node.id))
    if state.active == selection:
        return (state, ActiveUpdateOutcome(applied=False, reason=reason or "already active"))

    manifest = build_active_manifest(selection, state.graph)
    context_pack_text = render_context_pack(selection)
    commit_active_state(
        persisted_manifest=manifest,
        patch_manifest=manifest,
        ports=ports,
        context_pack_text=context_pack_text,
    )
    return (
        replace(state, active=selection),
        ActiveUpdateOutcome(applied=True, reason=reason or f"matched branch: {inferred_node.id}"),
    )


def write_sync_artifacts(
    result: SyncStateResult,
    ports: Ports,
) -> ArtifactWriteResult:
    if ports.artifact_writer is None:
        raise RuntimeError("artifact_writer is required")
    specdock_dir = _resolve_specdock_dir(ports)
    bundle = ArtifactBundle(
        index=render_index_artifact(result),
        tree=render_tree_artifact(result),
        deps_issues=render_deps_issues_artifact(result),
        dashboard=render_dashboard(result),
    )
    try:
        return ports.artifact_writer.write(specdock_dir, bundle)
    except Exception as error:
        # FileArtifactWriter writes sequentially and is non-atomic. Any writer exception
        # must preserve partial/stale possibility even when active_update was not applied.
        raise _ArtifactWriteExecutionError(
            status="failed_partial_or_stale",
            reason=str(error),
        ) from error


def _sync_impl(
    req: SyncRequest,
    ports: Ports,
    *,
    active_manifest_mode: Literal["migrate", "no_migrate"],
) -> SyncCommandResult:
    if not _can_sync_natively(ports):
        runner = _require_sync_runner(ports)
        return runner.run_sync(req, active_manifest_mode=active_manifest_mode)

    state = collect_sync_state(req, ports, active_manifest_mode=active_manifest_mode)
    active_update: ActiveUpdateOutcome | None = None
    final_state = state
    if req.update_active_from_branch and not req.force:
        final_state, active_update = maybe_auto_update_from_branch(state, ports)

    try:
        write_result = write_sync_artifacts(final_state, ports)
    except _ArtifactWriteExecutionError as error:
        return SyncCommandResult(
            state=final_state,
            write_result=None,
            active_update=active_update,
            artifact_failure=ArtifactWriteFailure(status=error.status, reason=error.reason),
        )
    except Exception as error:
        status: Literal["failed_before_write", "failed_partial_or_stale"]
        if active_update is not None and active_update.applied:
            status = "failed_partial_or_stale"
        else:
            status = "failed_before_write"
        return SyncCommandResult(
            state=final_state,
            write_result=None,
            active_update=active_update,
            artifact_failure=ArtifactWriteFailure(status=status, reason=str(error)),
        )

    return SyncCommandResult(
        state=final_state,
        write_result=write_result,
        active_update=active_update,
        artifact_failure=None,
    )


def sync(req: SyncRequest, ports: Ports) -> SyncCommandResult:
    return _sync_impl(req, ports, active_manifest_mode="migrate")


def sync_after_import(ports: Ports) -> SyncCommandResult:
    req = SyncRequest(
        force=False,
        github_enabled=False,
        issue_limit=10000,
        update_active_from_branch=False,
    )
    return _sync_impl(req, ports, active_manifest_mode="no_migrate")
