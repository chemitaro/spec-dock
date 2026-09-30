"""Start's memory-only candidate planning graph at a fixed commit."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import json
from typing import TYPE_CHECKING

from spec_dock.runtime.application.project_context import read_workspace_declaration
from spec_dock.runtime.application.scope_query import load_scope_views, show_scope
from spec_dock.runtime.application.worktree_observation import ancestors_for
from spec_dock.runtime.domain.dependency_vnext import (
    dependency_listing,
    evaluate_start_readiness,
    validate_dependency_graph,
)
from spec_dock.runtime.domain.lifecycle import GithubBackend, StatusObservation, decode_scope_metadata
from spec_dock.runtime.domain.writer_admission import require_scope_write
from spec_dock.runtime.infra.committed_workspace import committed_workspace
from spec_dock.runtime.infra.git_process import run_git
from spec_dock.runtime.infra.github_lifecycle import GithubIssueGateway
from spec_dock.runtime.infra.json_store import read_guarded_json_bytes

if TYPE_CHECKING:
    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.scope_query import ScopeView
    from spec_dock.runtime.domain.dependency_vnext import ReadinessResult


@dataclass(frozen=True)
class CandidateSnapshot:
    oid: str
    views: tuple[ScopeView, ...]
    metadata: tuple[tuple[str, bytes], ...]
    dependencies: tuple[tuple[str, tuple[str, ...]], ...]


@dataclass(frozen=True)
class LocalInput:
    relative_path: str
    payload: bytes
    identity: tuple[int, int]


class StartSnapshotError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def capture_local_inputs(context: ProjectContext, views: tuple[ScopeView, ...]) -> tuple[LocalInput, ...]:
    inputs: list[LocalInput] = []
    paths = (context.root / "spec-dock/workspace.json", *(view.path / ".meta.json" for view in views))
    by_path = {view.path / ".meta.json": view for view in views}
    for path in paths:
        loaded = read_guarded_json_bytes(path)
        if loaded is None or not isinstance(loaded[0], dict):
            raise ValueError("local planning input disappeared")
        payload, exact, identity = loaded
        if path in by_path:
            view = by_path[path]
            require_scope_write(payload)
            metadata = decode_scope_metadata(payload)
            if (
                metadata.backend != view.backend
                or metadata.revision != view.revision
                or (payload.get("id"), payload.get("type"), payload.get("title"), payload.get("parent_id"))
                != (view.id, view.kind, view.title, view.parent_id)
            ):
                raise ValueError("local Scope changed while capturing Start inputs")
        elif payload != context.workspace:
            raise ValueError("workspace changed while capturing Start inputs")
        inputs.append(LocalInput(path.relative_to(context.root).as_posix(), exact, identity))
    return tuple(inputs)


def verify_local_inputs(context: ProjectContext, inputs: tuple[LocalInput, ...]) -> None:
    current_views = load_scope_views(context.root / "spec-dock")
    current_paths = {
        "spec-dock/workspace.json",
        *((view.path / ".meta.json").relative_to(context.root).as_posix() for view in current_views),
    }
    if current_paths != {expected.relative_path for expected in inputs}:
        raise ValueError("local Start planning metadata paths changed")
    for expected in inputs:
        loaded = read_guarded_json_bytes(context.root / expected.relative_path)
        if loaded is None or loaded[1] != expected.payload or loaded[2] != expected.identity:
            raise ValueError(f"local Start input changed: {expected.relative_path}")


def read_candidate(
    context: ProjectContext,
    oid: str,
    target: ScopeView,
    current_views: tuple[ScopeView, ...],
    *,
    timeout: float,
    proposed_token: str,
) -> CandidateSnapshot:
    with committed_workspace(context.root, oid, timeout=timeout) as workspace:
        for basename in (f"target-{proposed_token}.json", f".stage-{proposed_token}"):
            if not run_git(
                workspace.parent,
                f"--git-dir={context.common_dir}",
                f"--work-tree={workspace.parent}",
                "check-ignore",
                "--no-index",
                "--",
                f"spec-dock/.agent/work-target/{basename}",
                timeout=timeout,
                missing_ok=True,
            ):
                raise StartSnapshotError(
                    "WORK_TARGET_PATH_NOT_IGNORED", "candidate work target state must be ignored by Git"
                )
        replace(context, workspace=read_workspace_declaration(workspace / "workspace.json")).require_writer()
        views = load_scope_views(workspace)
        for view in views:
            require_scope_write(json.loads((view.path / ".meta.json").read_bytes()))
        try:
            candidate = show_scope(views, target.id)
        except LookupError as error:
            raise ValueError("target Scope is absent from the candidate commit") from error
        candidate_chain = (*ancestors_for(views, candidate), candidate)
        current_chain = (*ancestors_for(current_views, target), target)
        if tuple(
            (view.id, view.kind, view.parent_id, view.backend.kind, view.github_ref) for view in candidate_chain
        ) != tuple((view.id, view.kind, view.parent_id, view.backend.kind, view.github_ref) for view in current_chain):
            raise ValueError("candidate Scope identity or linkage differs")
        dependencies = {
            view.id: tuple(json.loads((view.path / ".meta.json").read_bytes())["depends_on"]) for view in views
        }
        validate_dependency_graph(views, dependencies)
        payloads = tuple(
            (path.relative_to(workspace.parent).as_posix(), path.read_bytes())
            for path in (workspace / "workspace.json", *(view.path / ".meta.json" for view in views))
        )
        current_paths = tuple(
            replace(view, path=context.root / view.path.relative_to(workspace.parent)) for view in views
        )
        return CandidateSnapshot(oid, current_paths, payloads, tuple(dependencies.items()))


def verify_candidate(context: ProjectContext, candidate: CandidateSnapshot) -> None:
    actual = load_scope_views(context.root / "spec-dock")
    expected_paths = {relative for relative, _ in candidate.metadata}
    actual_paths = {
        "spec-dock/workspace.json",
        *((view.path / ".meta.json").relative_to(context.root).as_posix() for view in actual),
    }
    if expected_paths != actual_paths:
        raise ValueError("checkout planning metadata paths differ from candidate")
    for relative, expected in candidate.metadata:
        loaded = read_guarded_json_bytes(context.root / relative)
        if loaded is None or loaded[1] != expected:
            raise ValueError(f"checkout planning metadata differs from candidate: {relative}")


def observe_readiness(
    context: ProjectContext, candidate: CandidateSnapshot, target_id: str, *, timeout: float, offline: bool
) -> ReadinessResult:
    views = candidate.views
    raw = dict(candidate.dependencies)
    target = show_scope(views, target_id)
    necessary = dict.fromkeys([
        target.id,
        *(view.id for view in ancestors_for(views, target)),
        *(edge.target_id for edge in dependency_listing(views, raw, target_id).effective),
    ])
    by_id = {view.id: view for view in views}
    if offline and any(isinstance(by_id[scope_id].backend, GithubBackend) for scope_id in necessary):
        raise ValueError("offline mode cannot fetch required GitHub state")
    gateway = GithubIssueGateway(timeout=timeout)
    observed: dict[str, StatusObservation] = {}
    for scope_id in necessary:
        backend = by_id[scope_id].backend
        if isinstance(backend, GithubBackend):
            record = gateway.get(context.root, f"{backend.repo_owner}/{backend.repo_name}", backend.issue_number)
            observed[scope_id] = StatusObservation(
                record.state,
                "github",
                "github",
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                record.updated_at,
                False,
            )
    return evaluate_start_readiness(
        views, raw, target_id, source="github", mode="start", offline=offline, observations=observed
    )
