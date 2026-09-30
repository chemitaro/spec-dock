"""Observe dependency edges from the current Scope tree without shared control."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import json
import secrets
from typing import TYPE_CHECKING

from spec_dock.runtime.application.dependency_vnext import _read_raw_edges
from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.application.scope_query import load_scope_views
from spec_dock.runtime.application.start_snapshot import capture_local_inputs, verify_local_inputs
from spec_dock.runtime.application.worktree_observation import ancestors_for, read_selection, resolve_scope
from spec_dock.runtime.domain.dependency_vnext import (
    dependency_listing,
    evaluate_start_readiness,
    validate_dependency_graph,
)
from spec_dock.runtime.domain.lifecycle import GithubBackend, StatusObservation
from spec_dock.runtime.infra.direct_json import MetadataPublicationIncomplete, replace_existing_json
from spec_dock.runtime.infra.git_process import GitProcessError, run_git
from spec_dock.runtime.infra.github_lifecycle import GithubIssueGateway, RemoteIssueError
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult, RecoveryInstructions

if TYPE_CHECKING:
    import argparse
    from pathlib import Path

    from spec_dock.runtime.application.project_context import ProjectContext


def query_dependencies(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    views = load_scope_views(context.root / "spec-dock")
    target = resolve_scope(context, views, namespace.target)
    raw, _metadata = _read_raw_edges(views)
    listing = dependency_listing(views, raw, target.id)
    ready: bool | None = None
    blockers: tuple[Diagnostic, ...] = ()
    errors: list[Diagnostic] = []
    if namespace.command_path == "dependency check":
        observations: dict[str, StatusObservation] = {}
        if namespace.source == "github":
            by_id = {view.id: view for view in views}
            needed = dict.fromkeys([
                target.id,
                *(view.id for view in ancestors_for(views, target)),
                *(edge.target_id for edge in listing.effective),
            ])
            if namespace.offline and any(isinstance(by_id[scope_id].backend, GithubBackend) for scope_id in needed):
                raise ValueError("offline mode cannot fetch required GitHub state")
            gateway = GithubIssueGateway(timeout=namespace.timeout)
            for scope_id in needed:
                backend = by_id[scope_id].backend
                if isinstance(backend, GithubBackend):
                    try:
                        remote = gateway.get(
                            context.root, f"{backend.repo_owner}/{backend.repo_name}", backend.issue_number
                        )
                    except RemoteIssueError as error:
                        errors.append(
                            Diagnostic(
                                error.code, str(error), {"scope_id": scope_id, "github_ref": by_id[scope_id].github_ref}
                            )
                        )
                        continue
                    observations[scope_id] = StatusObservation(
                        remote.state,
                        "github",
                        "github",
                        datetime.now(timezone.utc).isoformat(),
                        remote.updated_at,
                        False,
                    )
        readiness = evaluate_start_readiness(views, raw, target.id, source=namespace.source, observations=observations)
        ready = readiness.ready
        blockers = tuple(
            Diagnostic(
                "READINESS_BLOCKED",
                f"{blocker.scope_id} requires {blocker.required_state}; observed {blocker.observed_state}",
                {
                    "scope_id": blocker.scope_id,
                    "required_state": blocker.required_state,
                    "observed_state": blocker.observed_state,
                    "source": blocker.source,
                    "stale": blocker.stale,
                },
            )
            for blocker in readiness.blockers
        )
    return OperationResult(
        namespace.command_path,
        "failed" if errors else "succeeded",
        FamilyData(
            "dependency",
            {
                "scope_id": listing.scope_id,
                "declared": tuple(edge.target_id for edge in listing.declared),
                "effective": tuple(edge.target_id for edge in listing.effective),
                "ready": ready,
                "blockers": blockers,
                "changed": False,
            },
        ),
        5 if errors else 0,
        error=errors[0] if errors else None,
        warnings=tuple(errors[1:]),
    )


def mutate_dependencies(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    context.require_writer()
    views = load_scope_views(context.root / "spec-dock")
    selection = read_selection(context, views)
    source = resolve_scope(context, views, namespace.from_target, selection=selection)
    destination = resolve_scope(context, views, namespace.to_target, selection=selection)
    if namespace.expect_backend is not None and source.backend.kind != namespace.expect_backend:
        raise ValueError("source backend does not match --expect-backend")
    if namespace.expect_current is not None:
        expected = resolve_scope(context, views, namespace.expect_current, selection=selection).id
        if selection.status != "selected" or selection.record is None or selection.record.scope_id != expected:
            raise ValueError("direct target does not match --expect-current")
    raw, metadata = _read_raw_edges(views)
    inputs = capture_local_inputs(context, views)
    by_path = {item.relative_path: item for item in inputs}
    if any(
        json.loads(by_path[(view.path / ".meta.json").relative_to(context.root).as_posix()].payload)
        != metadata[view.id][0]
        for view in views
    ):
        raise ValueError("dependency metadata changed while capturing inputs")
    existing = raw[source.id]
    if namespace.command_path == "dependency remove":
        changed = destination.id in existing
        if not changed and not namespace.missing_ok:
            raise LookupError("dependency edge was not found")
        candidate = tuple(scope_id for scope_id in existing if scope_id != destination.id)
    else:
        changed = destination.id not in existing
        candidate = (*existing, destination.id) if changed else existing
    proposed = {**raw, source.id: candidate}
    validate_dependency_graph(views, proposed)
    payload = {**metadata[source.id][0], "depends_on": list(candidate), "revision": source.revision + int(changed)}

    def verify_source() -> None:
        fresh = resolve_context(str(context.root), context.root, timeout=namespace.timeout)
        if fresh.clone_identity != context.clone_identity or fresh.worktree_identity != context.worktree_identity:
            raise ValueError("Git project physical identity changed")
        fresh.require_writer()
        verify_local_inputs(fresh, inputs)

    def verify_stage(path: Path) -> None:
        verify_source()
        if not run_git(
            context.root,
            "check-ignore",
            "--no-index",
            "--",
            path.relative_to(context.root).as_posix(),
            missing_ok=True,
            timeout=namespace.timeout,
        ):
            raise ValueError("metadata staging path must be ignored by Git")

    def result_data(graph: dict[str, tuple[str, ...]], applied: bool) -> dict[str, object]:
        listing = dependency_listing(views, graph, source.id)
        return {
            "scope_id": source.id,
            "declared": tuple(edge.target_id for edge in listing.declared),
            "effective": tuple(edge.target_id for edge in listing.effective),
            "ready": None,
            "blockers": (),
            "changed": applied,
        }

    if changed:
        verify_stage(context.root / "spec-dock/.agent/staging" / f".stage-{secrets.token_hex(16)}")
    if changed and not namespace.dry_run:
        captured = by_path[(source.path / ".meta.json").relative_to(context.root).as_posix()]
        confirmed = False
        try:
            published = replace_existing_json(
                source.path / ".meta.json",
                payload,
                expected_bytes=captured.payload,
                expected_identity=captured.identity,
                staging_dir=context.root / "spec-dock/.agent/staging",
                before_replace=verify_source,
                before_stage=verify_stage,
            )
            confirmed = True
            inputs = tuple(
                replace(item, payload=published.payload, identity=published.identity) if item == captured else item
                for item in inputs
            )
            verify_source()
        except (ValueError, OSError, RuntimeError) as error:
            if isinstance(error, MetadataPublicationIncomplete):
                confirmed = error.published is not None
            uncertain = isinstance(error, MetadataPublicationIncomplete) and not confirmed
            partial = confirmed or uncertain
            data = result_data(proposed if confirmed else raw, confirmed)
            data["metadata_observation"] = "confirmed-publication" if confirmed else "before-operation"
            return OperationResult(
                namespace.command_path,
                "partial" if partial else "failed",
                FamilyData("dependency", data),
                6 if partial else 5 if isinstance(error, (OSError, RuntimeError)) else 3,
                effects=(
                    Effect(
                        "dependency-edge",
                        "succeeded"
                        if confirmed
                        else "unknown"
                        if uncertain
                        else "not_attempted"
                        if isinstance(error, ValueError)
                        else "failed",
                        f"{source.id}->{destination.id}",
                    ),
                ),
                error=Diagnostic(
                    "GIT_FAILED" if isinstance(error, GitProcessError) else "DEPENDENCY_UPDATE_INCOMPLETE",
                    str(error),
                    error.details() if isinstance(error, GitProcessError) else {},
                ),
                recovery=RecoveryInstructions((
                    f"Inspect the current metadata for {source.id} and validate the graph before a new explicit operation; no automatic rollback or resume.",
                )),
            )
    data = result_data(proposed, changed and not namespace.dry_run)
    if namespace.dry_run:
        data["can_apply"] = True
    return OperationResult(
        namespace.command_path,
        "planned" if namespace.dry_run else "succeeded" if changed else "unchanged",
        FamilyData("dependency", data),
        0,
        effects=(
            Effect(
                "dependency-edge",
                "planned" if namespace.dry_run else "succeeded" if changed else "unchanged",
                f"{source.id}->{destination.id}",
            ),
        ),
    )
