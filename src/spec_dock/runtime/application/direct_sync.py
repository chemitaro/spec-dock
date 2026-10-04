"""Read current Scope lifecycle and same-clone selections without persistence."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from spec_dock.runtime.application.scope_expectations import check_scope_expectations
from spec_dock.runtime.application.scope_query import load_scope_views
from spec_dock.runtime.application.worktree_observation import observe_worktrees, read_selection
from spec_dock.runtime.domain.lifecycle import LocalBackend
from spec_dock.runtime.domain.selectors import GithubScopeSelector, parse_scope_selector
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
    if namespace.expect_current is not None or namespace.expect_backend is not None:
        selection = read_selection(context, views)
        check_scope_expectations(
            context,
            views,
            selection,
            target=None,
            expected_current=namespace.expect_current,
            expected_backend=namespace.expect_backend,
        )
    observations = observe_worktrees(context, timeout=namespace.timeout)
    included = {(view.id, view.github_ref): view for view in views}
    included_ids = {view.id: view for view in views}
    ancestry_findings: list[Diagnostic] = []
    conflicting_lifecycle: set[tuple[str, str | None]] = set()
    for row in observations:
        for view in row.views:
            identity = (view.id, view.github_ref)
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
    known_records = tuple(
        row.selection.record
        for row in observations
        if row.selection.status in ("selected", "stale", "unavailable") and row.selection.record is not None
    )
    scope_ids = dict.fromkeys(included_ids)
    for known_record in known_records:
        states.setdefault((known_record.scope_id, known_record.github_ref), "unknown")
        scope_ids.setdefault(known_record.scope_id)
    scope_refs: dict[str, str | None] = {}
    ref_scopes: dict[str, str] = {}
    for scope_id, github_ref in states:
        if scope_id in scope_refs and scope_refs[scope_id] != github_ref:
            ancestry_findings.append(
                Diagnostic(
                    "SCOPE_IDENTITY_CONFLICT",
                    "Scope ID has different GitHub linkages between observations",
                    {"scope_id": scope_id, "github_refs": (scope_refs[scope_id], github_ref)},
                )
            )
        if github_ref is not None:
            if github_ref in ref_scopes and ref_scopes[github_ref] != scope_id:
                ancestry_findings.append(
                    Diagnostic(
                        "SCOPE_IDENTITY_CONFLICT",
                        "GitHub linkage has different Scope IDs between observations",
                        {"github_ref": github_ref, "scope_ids": (ref_scopes[github_ref], scope_id)},
                    )
                )
            ref_scopes.setdefault(github_ref, scope_id)
        scope_refs.setdefault(scope_id, github_ref)
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
        if row.selection.status not in ("selected", "stale", "unavailable") or record is None:
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
        if namespace.offline and any(github_ref is not None for _, github_ref in states):
            raise ValueError("offline mode cannot fetch required GitHub state")
        gateway = GithubIssueGateway(timeout=namespace.timeout)
        remote_states: dict[str, ObservedState] = {}
        for _, github_ref in states:
            if github_ref is not None and github_ref not in remote_states:
                selector = parse_scope_selector(github_ref)
                assert isinstance(selector, GithubScopeSelector)
                try:
                    remote_states[github_ref] = gateway.get(
                        context.root, f"{selector.owner}/{selector.repo}", selector.issue_number
                    ).state
                    if remote_states[github_ref] == "unknown":
                        raise RemoteIssueError("GITHUB_STATE_UNKNOWN")
                except RemoteIssueError as error:
                    remote_states[github_ref] = "unknown"
                    findings.append(
                        Diagnostic(
                            error.code,
                            "GitHub lifecycle could not be observed",
                            {
                                "github_ref": github_ref,
                            },
                        )
                    )
        states.update({
            (scope_id, github_ref): remote_states[github_ref]
            for scope_id, github_ref in states
            if github_ref is not None and github_ref in remote_states
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
            "scope_id": scope_id,
            "direct_selected_count": sum(
                row.selection.status in ("selected", "stale", "unavailable")
                and row.selection.record is not None
                and row.selection.record.scope_id == scope_id
                for row in observations
            ),
            "descendant_selected_count": sum(
                row.selection.status == "selected" and scope_id in row.selection.ancestors for row in observations
            ),
            "complete": selection_complete,
        }
        for scope_id in scope_ids
    )
    data = SyncData(
        datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        namespace.source,
        not findings,
        rows,
        tuple(
            {"scope_id": scope_id, "github_ref": github_ref, "lifecycle": state}
            for (scope_id, github_ref), state in states.items()
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
