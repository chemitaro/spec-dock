"""Active operations never acquire a new direct selection outside Start."""

from __future__ import annotations

from typing import TYPE_CHECKING

from spec_dock.runtime.application.scope_query import load_scope_views
from spec_dock.runtime.application.worktree_observation import SelectionObservation, read_selection, resolve_scope
from spec_dock.runtime.infra.work_target_store import SelectionRemovalUnknown, WorkTargetStore
from spec_dock.runtime.presentation.command_data import ActiveData, DiagnosticData
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.scope_query import ScopeView


def set_direct(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    context.require_writer()
    views = load_scope_views(context.root / "spec-dock")
    target = resolve_scope(context, views, namespace.target)
    selection = read_selection(context, views)
    _check_guards(namespace, context, views, selection, target)
    if selection.status == "selected" and selection.record is not None and selection.record.scope_id == target.id:
        return OperationResult(
            namespace.command_path, "unchanged", ActiveData(selection.view(), selection.ancestors), 0
        )
    return OperationResult(
        namespace.command_path,
        "failed",
        DiagnosticData(),
        3,
        error=Diagnostic("WORK_START_REQUIRED", "Use work start to acquire a direct selection", {}),
    )


def clear_direct(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    context.require_writer()
    selected_handles = None
    if (
        namespace.from_target is not None
        or namespace.expect_current is not None
        or namespace.expect_backend is not None
    ):
        views = load_scope_views(context.root / "spec-dock")
        selection = read_selection(context, views)
        target = (
            resolve_scope(context, views, namespace.from_target)
            if namespace.from_target is not None
            else resolve_scope(context, views, selection.record.scope_id)
            if selection.record is not None
            else None
        )
        _check_guards(namespace, context, views, selection, target)
        if selection.status not in ("selected", "empty"):
            raise ValueError(selection.reason or "selection is not valid")
        if selection.record is None or (
            target is not None and target.id not in (*selection.ancestors, selection.record.scope_id)
        ):
            return OperationResult(
                namespace.command_path, "unchanged", ActiveData(selection.view(), selection.ancestors), 0
            )
        selected_handles = (selection.handle,) if selection.handle is not None else ()
    effects: list[Effect] = []
    try:
        with WorkTargetStore(context.root) as store:
            captured = store.read()
            handles = captured.observed_handles if selected_handles is None else selected_handles
            if captured.status == "unavailable":
                raise ValueError(captured.reason or "selection cannot be read safely")
            if captured.status == "invalid" and (
                (not namespace.yes and not namespace.dry_run) or not captured.observed_handles
            ):
                raise ValueError("invalid selection requires --all --yes and safely observed regular records")
            if namespace.dry_run:
                observed = _observe(context)
                return OperationResult(
                    namespace.command_path,
                    "planned",
                    ActiveData(observed.view(), observed.ancestors),
                    0,
                    effects=tuple(Effect("selection.clear", "planned", handle.token) for handle in handles),
                )
            for handle in handles:
                try:
                    outcome = store.remove_observed(handle)
                except SelectionRemovalUnknown:
                    effects.append(Effect("selection.clear", "unknown", handle.token))
                    raise
                if outcome == "conflict":
                    raise ValueError("observed selection changed")
                effects.append(
                    Effect("selection.clear", "succeeded" if outcome == "removed" else "unchanged", handle.token)
                )
        observed = _observe(context)
    except (ValueError, OSError, RuntimeError) as error:
        if any(effect.status in ("succeeded", "unknown") for effect in effects):
            return OperationResult(
                namespace.command_path,
                "partial",
                DiagnosticData(),
                6,
                effects=tuple(effects),
                error=Diagnostic("SELECTION_CLEAR_INCOMPLETE", str(error), {}),
            )
        raise
    return OperationResult(
        namespace.command_path,
        "succeeded" if any(effect.status == "succeeded" for effect in effects) else "unchanged",
        ActiveData(observed.view(), observed.ancestors),
        0,
        effects=tuple(effects),
    )


def _observe(context: ProjectContext) -> SelectionObservation:
    with WorkTargetStore(context.root) as store:
        observed = store.read()
    views = (
        load_scope_views(context.root / "spec-dock", target_id=observed.record.scope_id)
        if observed.record is not None
        else ()
    )
    return read_selection(context, views)


def _check_guards(
    namespace: argparse.Namespace,
    context: ProjectContext,
    views: tuple[ScopeView, ...],
    selection: SelectionObservation,
    target: ScopeView | None,
) -> None:
    if namespace.expect_backend is not None and (target is None or target.backend.kind != namespace.expect_backend):
        raise ValueError("target backend does not match --expect-backend")
    if namespace.expect_current is not None:
        expected = resolve_scope(context, views, namespace.expect_current).id
        if selection.status != "selected" or selection.record is None or selection.record.scope_id != expected:
            raise ValueError("direct target does not match --expect-current")
