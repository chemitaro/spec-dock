"""Read current Scope lifecycle and same-clone selections without persistence."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from spec_dock.runtime.application.scope_query import load_scope_views
from spec_dock.runtime.application.worktree_observation import observe_worktrees
from spec_dock.runtime.domain.lifecycle import GithubBackend, LocalBackend
from spec_dock.runtime.infra.git_process import GitProcessError
from spec_dock.runtime.infra.github_lifecycle import GithubIssueGateway, RemoteIssueError
from spec_dock.runtime.presentation.command_data import DiagnosticData, SyncData
from spec_dock.runtime.presentation.envelope import Diagnostic, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.domain.lifecycle import ObservedState


def sync_workspace(
    namespace: argparse.Namespace, context: ProjectContext
) -> OperationResult[SyncData | DiagnosticData]:
    try:
        views = load_scope_views(context.root / "spec-dock")
    except (ValueError, OSError) as error:
        finding = Diagnostic("SYNC_INPUT_INVALID", str(error), {"path": str(context.root / "spec-dock")})
        return OperationResult(
            "workspace sync", "failed", DiagnosticData((finding,), ("current Scope tree",)), 7, error=finding
        )
    observations = observe_worktrees(context, timeout=namespace.timeout)
    included = {(view.id, view.github_ref): view for view in views}
    included_ids = {view.id: view for view in views}
    ancestry_findings: list[Diagnostic] = []
    conflicting_lifecycle: set[tuple[str, str | None]] = set()
    for row in observations:
        for view in row.views:
            identity = (view.id, view.github_ref)
            if view.id in included_ids and included_ids[view.id].github_ref != view.github_ref:
                ancestry_findings.append(
                    Diagnostic(
                        "SCOPE_IDENTITY_CONFLICT",
                        "Scope ID has different GitHub linkages between worktrees",
                        {
                            "scope_id": view.id,
                            "path": row.path,
                            "github_refs": (included_ids[view.id].github_ref, view.github_ref),
                        },
                    )
                )
            if (
                identity in included
                and isinstance(included[identity].backend, LocalBackend)
                and isinstance(view.backend, LocalBackend)
                and included[identity].status.state != view.status.state
            ):
                conflicting_lifecycle.add(identity)
                ancestry_findings.append(
                    Diagnostic(
                        "LOCAL_LIFECYCLE_CONFLICT",
                        "Existing local Scope lifecycle differs between worktrees",
                        {
                            "scope_id": view.id,
                            "path": row.path,
                            "states": (included[identity].status.state, view.status.state),
                        },
                    )
                )
            if identity not in included:
                included[identity] = view
                included_ids.setdefault(view.id, view)
            elif (included[identity].kind, included[identity].parent_id) != (view.kind, view.parent_id):
                ancestry_findings.append(
                    Diagnostic(
                        "SCOPE_ANCESTRY_CONFLICT",
                        "Scope parent chains differ between worktrees",
                        {
                            "scope_id": view.id,
                            "path": row.path,
                            "parents": (included[identity].parent_id, view.parent_id),
                        },
                    )
                )
    views = tuple(included.values())
    states = {(view.id, view.github_ref): view.status.state for view in views}
    for identity in conflicting_lifecycle:
        states[identity] = "unknown"
    row_findings: dict[str, tuple[Diagnostic, ...]] = {
        row.path: (
            Diagnostic(
                f"WORKTREE_SELECTION_{row.selection.status.upper()}",
                row.selection.reason or "Worktree selection could not be observed",
                {
                    "path": row.path,
                    "selection_status": row.selection.status,
                    **(row.error.details() if isinstance(row.error, GitProcessError) else {}),
                },
            ),
        )
        for row in observations
        if row.selection.status not in ("selected", "empty")
    }
    selected_ids: dict[str, str] = {}
    selected_refs: dict[str, str] = {}
    for row in observations:
        record = row.selection.record
        if row.selection.status != "selected" or record is None:
            continue
        previous = selected_ids.get(record.scope_id) or selected_refs.get(record.github_ref or "")
        if previous is not None:
            row_findings[row.path] = (
                *row_findings.get(row.path, ()),
                Diagnostic(
                    "SELECTION_DUPLICATE",
                    "More than one worktree selects the same Scope",
                    {"scope_id": record.scope_id, "github_ref": record.github_ref, "paths": (previous, row.path)},
                ),
            )
        selected_ids[record.scope_id] = row.path
        if record.github_ref is not None:
            selected_refs[record.github_ref] = row.path
    selection_complete = not row_findings and not ancestry_findings
    findings = ancestry_findings + [finding for group in row_findings.values() for finding in group]
    if namespace.source == "github":
        if namespace.offline and any(isinstance(view.backend, GithubBackend) for view in views):
            raise ValueError("offline mode cannot fetch required GitHub state")
        gateway = GithubIssueGateway(timeout=namespace.timeout)
        remote_states: dict[str | None, ObservedState] = {}
        for view in views:
            if isinstance(view.backend, GithubBackend) and view.github_ref not in remote_states:
                backend = view.backend
                try:
                    remote_states[view.github_ref] = gateway.get(
                        context.root, f"{backend.repo_owner}/{backend.repo_name}", backend.issue_number
                    ).state
                    if remote_states[view.github_ref] == "unknown":
                        raise RemoteIssueError("GITHUB_STATE_UNKNOWN")
                except RemoteIssueError as error:
                    remote_states[view.github_ref] = "unknown"
                    findings.append(
                        Diagnostic(
                            error.code,
                            "GitHub lifecycle could not be observed",
                            {
                                "github_ref": view.github_ref,
                            },
                        )
                    )
        states.update({
            (view.id, view.github_ref): remote_states[view.github_ref]
            for view in views
            if view.github_ref in remote_states
        })
    rows: tuple[dict[str, object], ...] = tuple(
        {
            "path": row.path,
            "selection": row.selection.view(),
            "lifecycle": states.get((row.selection.record.scope_id, row.selection.record.github_ref), "unknown")
            if row.selection.record
            else "unknown",
            "process_state": "not_observed",
            "findings": row_findings.get(row.path, ()),
        }
        for row in observations
    )
    counts = tuple(
        {
            "scope_id": view.id,
            "direct_selected_count": sum(
                row.selection.status == "selected"
                and row.selection.record is not None
                and row.selection.record.scope_id == view.id
                for row in observations
            ),
            "descendant_selected_count": sum(
                row.selection.status == "selected" and view.id in row.selection.ancestors for row in observations
            ),
            "complete": selection_complete,
        }
        for view in included_ids.values()
    )
    data = SyncData(
        datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        namespace.source,
        not findings,
        rows,
        tuple(
            {"scope_id": view.id, "github_ref": view.github_ref, "lifecycle": states[view.id, view.github_ref]}
            for view in views
        ),
        counts,
        tuple(findings),
    )
    if findings:
        git_details = next((row.error.details() for row in observations if isinstance(row.error, GitProcessError)), {})
        return OperationResult(
            "workspace sync",
            "partial",
            data,
            7,
            error=Diagnostic("SYNC_INCOMPLETE", "Some requested observations are incomplete", git_details),
        )
    return OperationResult("workspace sync", "succeeded", data, 0)
