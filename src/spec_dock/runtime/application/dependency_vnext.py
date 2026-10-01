"""Read and mutate canonical Scope dependency edges without implicit sync."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Protocol

from spec_dock.runtime.application.dependency_snapshot import read_raw_edges as _read_raw_edges
from spec_dock.runtime.application.scope_query import ScopeView, load_scope_views, show_scope
from spec_dock.runtime.cli.admission import admit_writer
from spec_dock.runtime.domain.dependency_vnext import (
    DependencyListing,
    ReadinessResult,
    dependency_listing,
    evaluate_start_readiness,
    validate_dependency_graph,
)
from spec_dock.runtime.domain.lifecycle import GithubBackend, SelectionState, StatusObservation
from spec_dock.runtime.infra.active_store import load_selection_v3
from spec_dock.runtime.infra.control_store import load_control
from spec_dock.runtime.infra.github_lifecycle import RemoteIssueError
from spec_dock.runtime.infra.json_store import atomic_write_json
from spec_dock.runtime.infra.writer_lock import WriterLock

if TYPE_CHECKING:
    from pathlib import Path

    from spec_dock.runtime.infra.contracts import GithubIssueRecord


class GithubStateGateway(Protocol):
    def get(self, repo_root: Path, repository: str, number: int) -> GithubIssueRecord: ...


@dataclass(frozen=True)
class DependencyMutationResult:
    from_id: str
    to_id: str
    revision: int
    changed: bool


@dataclass(frozen=True)
class _DependencyMutationPlan:
    from_id: str
    to_id: str
    revision: int
    changed: bool
    path: Path
    payload: dict[str, object]
    identity: tuple[int, int]


def validate_scope_dependency_snapshot(views: tuple[ScopeView, ...]) -> None:
    """Read and validate all declared edges without writing derived state."""
    _read_raw_edges(views)


def _selection_for_targets(specdock_dir: Path, worktree_id: str, *targets: str) -> SelectionState | None:
    if any(target.startswith("@") for target in targets):
        return load_selection_v3(specdock_dir, worktree_id=worktree_id)[0]
    return None


def list_scope_dependencies(
    specdock_dir: Path,
    target: str,
    *,
    worktree_id: str | None = None,
) -> DependencyListing:
    views = load_scope_views(specdock_dir)
    if target.startswith("@") and worktree_id is None:
        raise ValueError("active dependency target requires worktree identity")
    selection = _selection_for_targets(specdock_dir, worktree_id or "", target) if target.startswith("@") else None
    source = show_scope(views, target, selection=selection)
    raw, _metadata = _read_raw_edges(views)
    return dependency_listing(views, raw, source.id)


def check_scope_readiness(
    specdock_dir: Path,
    target: str,
    *,
    source: Literal["github", "cache"] = "cache",
    for_start: bool = False,
    allow_stale: bool = False,
    offline: bool = False,
    gateway: GithubStateGateway | None = None,
    gateway_repo_root: Path | None = None,
    worktree_id: str | None = None,
) -> ReadinessResult:
    """Observe only the target chain and effective prerequisites, without writes."""
    if target.startswith("@") and worktree_id is None:
        raise ValueError("active dependency target requires worktree identity")
    views = load_scope_views(specdock_dir)
    selection = _selection_for_targets(specdock_dir, worktree_id or "", target) if target.startswith("@") else None
    selected = show_scope(views, target, selection=selection)
    raw, _metadata = _read_raw_edges(views)
    by_id = {view.id: view for view in views}
    needed = [selected.id]
    parent_id = selected.parent_id
    while parent_id is not None:
        needed.append(parent_id)
        parent_id = by_id[parent_id].parent_id
    needed.extend(edge.target_id for edge in dependency_listing(views, raw, selected.id).effective)
    github_needed = tuple(
        by_id[scope_id] for scope_id in dict.fromkeys(needed) if isinstance(by_id[scope_id].backend, GithubBackend)
    )
    if offline and source == "github" and github_needed:
        raise ValueError("offline mode cannot fetch required GitHub state")
    observations: dict[str, StatusObservation] = {}
    if source == "github" and github_needed:
        if gateway is None:
            raise ValueError("live GitHub readiness requires a gateway")
        for view in github_needed:
            assert isinstance(view.backend, GithubBackend)
            repository = f"{view.backend.repo_owner}/{view.backend.repo_name}"
            try:
                observed = gateway.get(gateway_repo_root or specdock_dir.parent, repository, view.backend.issue_number)
                if observed.repository.lower() != repository.lower() or observed.number != view.backend.issue_number:
                    raise RemoteIssueError("GITHUB_ISSUE_ID_MISMATCH")
                observations[view.id] = StatusObservation(
                    observed.state, "github", "github", observed.updated_at, observed.updated_at, False
                )
            except RemoteIssueError:
                observations[view.id] = StatusObservation("unknown", "github", "unknown", None, None, True)
    return evaluate_start_readiness(
        views,
        raw,
        selected.id,
        source=source,
        mode="start" if for_start else "check",
        allow_stale=allow_stale,
        offline=offline,
        observations=observations,
    )


def mutate_scope_dependency(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    from_target: str,
    to_target: str,
    action: Literal["add", "remove"],
    missing_ok: bool = False,
    lock_timeout: float = 0.0,
) -> DependencyMutationResult:
    """Apply one v3 metadata CAS under the common writer lock."""
    with WriterLock(common_dir, timeout=lock_timeout):
        admit_writer(
            load_control(common_dir),
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
        )
        plan = _plan_dependency_mutation(
            repo_root / "spec-dock", worktree_id, from_target, to_target, action, missing_ok
        )
        if plan.changed:
            atomic_write_json(plan.path, plan.payload, expected_identity=plan.identity)
        return DependencyMutationResult(plan.from_id, plan.to_id, plan.revision, plan.changed)


def preview_mutate_scope_dependency(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    from_target: str,
    to_target: str,
    action: Literal["add", "remove"],
    missing_ok: bool = False,
) -> DependencyMutationResult:
    """Validate a metadata edge change without a writer lock or metadata write."""
    admit_writer(
        load_control(common_dir),
        common_dir=common_dir,
        worktree_id=worktree_id,
        engine_digest=engine_digest,
        expected_epoch=expected_epoch,
    )
    plan = _plan_dependency_mutation(repo_root / "spec-dock", worktree_id, from_target, to_target, action, missing_ok)
    return DependencyMutationResult(plan.from_id, plan.to_id, plan.revision, plan.changed)


def _plan_dependency_mutation(
    specdock_dir: Path,
    worktree_id: str,
    from_target: str,
    to_target: str,
    action: Literal["add", "remove"],
    missing_ok: bool,
) -> _DependencyMutationPlan:
    if action != "remove" and missing_ok:
        raise ValueError("missing_ok is valid only for dependency remove")
    views = load_scope_views(specdock_dir)
    selection = _selection_for_targets(specdock_dir, worktree_id, from_target, to_target)
    source = show_scope(views, from_target, selection=selection)
    destination = show_scope(views, to_target, selection=selection)
    raw, metadata = _read_raw_edges(views)
    existing = raw[source.id]
    changed = True
    if action == "add":
        changed = destination.id not in existing
        candidate = (*existing, destination.id) if changed else existing
    else:
        changed = destination.id in existing
        if not changed and not missing_ok:
            raise LookupError("dependency edge was not found")
        candidate = tuple(item for item in existing if item != destination.id)
    if changed:
        updated_raw = dict(raw)
        updated_raw[source.id] = candidate
        validate_dependency_graph(views, updated_raw)
    payload, identity = metadata[source.id]
    updated = dict(payload)
    if changed:
        updated["depends_on"] = list(candidate)
        updated["revision"] = source.revision + 1
    return _DependencyMutationPlan(
        source.id,
        destination.id,
        source.revision + int(changed),
        changed,
        source.path / ".meta.json",
        updated,
        identity,
    )
