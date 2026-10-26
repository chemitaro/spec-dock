"""Canonical-mode Scope, dependency, selection and Artifact reads (iss-00431; Epic design ch. 6)."""

from __future__ import annotations

import copy
from dataclasses import asdict
import os
import stat
from typing import TYPE_CHECKING, Final

from spec_dock.runtime.application.active_links import sync_selection_links
from spec_dock.runtime.application.artifact_query import ArtifactCatalogEntry
from spec_dock.runtime.application.canonical_errors import CANONICAL_NOT_APPLICABLE, CanonicalCommandError
from spec_dock.runtime.application.canonical_scopes import OFFLINE_MESSAGE, load_canonical_scopes
from spec_dock.runtime.application.direct_artifact import _view
from spec_dock.runtime.application.scope_expectations import check_scope_expectations
from spec_dock.runtime.application.scope_query import list_scopes
from spec_dock.runtime.application.worktree_observation import ancestors_for, read_selection, resolve_scope
from spec_dock.runtime.domain.artifacts import (
    GenericImportedArtifactFilename,
    SequentialArtifactFilename,
    can_create_artifact_type,
    parse_existing_artifact_filename,
    scan_artifact_slot_ledger,
)
from spec_dock.runtime.domain.canonical_layout import LINK_RELATIVE
from spec_dock.runtime.domain.canonical_readiness import evaluate_readiness
from spec_dock.runtime.domain.dependency_vnext import dependency_listing
from spec_dock.runtime.infra.json_store import open_guarded_directory
from spec_dock.runtime.infra.work_target_store import SelectionRemovalUnknown, WorkTargetStore
from spec_dock.runtime.presentation.command_data import ActiveData, CanonicalActiveData, DiagnosticData, FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult

if TYPE_CHECKING:
    import argparse
    from pathlib import Path

    from spec_dock.runtime.application.canonical_scopes import CanonicalScopes
    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.scope_query import ScopeView
    from spec_dock.runtime.application.worktree_observation import SelectionObservation

SOURCE_LOCAL_RECOVERY: Final = (
    "Omit --source to read the structure snapshot, or use --source github to refetch it from GitHub."
)


def show_scope(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    scopes = load_canonical_scopes(context, timeout=namespace.timeout, link=True, offline=namespace.offline)
    selection = read_selection(context, scopes.views)
    scope = resolve_scope(context, scopes.views, namespace.target, selection=selection)
    check_scope_expectations(
        context,
        scopes.views,
        selection,
        target=scope,
        expected_current=namespace.expect_current,
        expected_backend=namespace.expect_backend,
    )
    result = {
        "scope": scopes.payload(scope),
        "github_ref": scope.github_ref,
        "changed": False,
        "snapshot": scopes.snapshot_payload(),
    }
    return OperationResult(
        namespace.command_path, "succeeded", FamilyData("scope", result), 0, warnings=scopes.warnings()
    )


def list_scope(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    scopes = load_canonical_scopes(context, timeout=namespace.timeout, link=True, offline=namespace.offline)
    selection = read_selection(context, scopes.views)
    check_scope_expectations(
        context,
        scopes.views,
        selection,
        target=None,
        expected_current=namespace.expect_current,
        expected_backend=namespace.expect_backend,
    )
    parent = (
        resolve_scope(context, scopes.views, namespace.parent, selection=selection).id if namespace.parent else None
    )
    listed = list_scopes(scopes.views, kind=namespace.kind, parent_id=parent, state=namespace.state)
    result = {
        "items": [scopes.payload(scope) for scope in listed.items],
        "unknown_filtered_count": 0,
        "snapshot": scopes.snapshot_payload(),
    }
    return OperationResult(
        namespace.command_path, "succeeded", FamilyData("scope-list", result), 0, warnings=scopes.warnings()
    )


def _source(namespace: argparse.Namespace) -> tuple[bool, bool]:
    """(refresh, offline): `--source github` refetches; an explicit `--source local` does not apply."""
    if getattr(namespace, "source_explicit", False) and namespace.source == "local":
        raise CanonicalCommandError(
            CANONICAL_NOT_APPLICABLE,
            "--source local reads .meta.json; this workspace keeps structure in GitHub",
            recovery=(SOURCE_LOCAL_RECOVERY,),
        )
    refresh = namespace.source == "github"
    if refresh and namespace.offline:
        raise ValueError(OFFLINE_MESSAGE)
    return refresh, bool(namespace.offline)


def _raw_edges(scopes: CanonicalScopes) -> dict[str, tuple[str, ...]]:
    """Each Scope's blocked-by Scopes as IDs; non-Scope and undecided dependencies are left to readiness."""
    known = {view.id for view in scopes.views}
    raw: dict[str, tuple[str, ...]] = {}
    for view in scopes.views:
        targets = (scopes.snapshot.issues.get(number) for number in scopes.node(view.id).blocked_by)
        raw[view.id] = tuple(node.id for node in targets if node is not None and node.id in known)
    return raw


def _external(scopes: CanonicalScopes, chain: tuple[str, ...]) -> list[dict[str, object]]:
    found: dict[int, dict[str, object]] = {}
    for scope_id in chain:
        for number in scopes.node(scope_id).blocked_by:
            item = scopes.snapshot.external.get(number)
            if item is not None and number not in found:
                found[number] = {"number": number, "title": item.title, "state": item.state, "declared_by": scope_id}
    return list(found.values())


def query_dependencies(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    refresh, offline = _source(namespace) if namespace.command_path == "dependency check" else (False, namespace.offline)
    scopes = load_canonical_scopes(context, timeout=namespace.timeout, link=False, refresh=refresh, offline=offline)
    selection = read_selection(context, scopes.views)
    target = resolve_scope(context, scopes.views, namespace.target, selection=selection)
    check_scope_expectations(
        context,
        scopes.views,
        selection,
        target=target,
        expected_current=namespace.expect_current,
        expected_backend=namespace.expect_backend,
    )
    listing = dependency_listing(scopes.views, _raw_edges(scopes), target.id)
    chain = (target.id, *(view.id for view in ancestors_for(scopes.views, target)))
    result: dict[str, object] = {
        "scope_id": listing.scope_id,
        "declared": tuple(edge.target_id for edge in listing.declared),
        "effective": tuple(edge.target_id for edge in listing.effective),
        "external": _external(scopes, chain),
        "ready": None,
        "blockers": (),
        "changed": False,
        "snapshot": scopes.snapshot_payload(),
    }
    if namespace.command_path == "dependency check":
        readiness = evaluate_readiness(scopes.snapshot, target.id)
        source = "github" if refresh else "cache"
        result["ready"] = readiness.ready
        result["blockers"] = (
            *(
                Diagnostic(
                    "READINESS_BLOCKED",
                    f"#{item.number} requires {item.required_state}; observed {item.observed_state}",
                    {
                        "scope_id": item.scope_id,
                        "required_state": item.required_state,
                        "observed_state": item.observed_state,
                        "source": source,
                        "stale": scopes.fresh.stale,
                        "number": item.number,
                        "role": item.role,
                        "declared_by": item.declared_by,
                    },
                )
                for item in readiness.blockers
            ),
            *(
                Diagnostic(
                    "READINESS_UNKNOWN",
                    item.message,
                    {"number": item.number, "scope_id": item.scope_id, "code": item.code},
                )
                for item in readiness.unknown
            ),
        )
        result["readiness"] = {
            "state": readiness.state,
            "ready": readiness.ready,
            "in_progress": readiness.in_progress,
            "blockers": [asdict(item) for item in readiness.blockers],
            "unknown": [asdict(item) for item in readiness.unknown],
        }
    return OperationResult(
        namespace.command_path, "succeeded", FamilyData("dependency", result), 0, warnings=scopes.warnings()
    )


def show_active(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    scopes = load_canonical_scopes(context, timeout=namespace.timeout, link=True, offline=namespace.offline)
    observation = read_selection(context, scopes.views)
    check_scope_expectations(
        context,
        scopes.views,
        observation,
        target=None,
        expected_current=namespace.expect_current,
        expected_backend=namespace.expect_backend,
    )
    selected = (
        scopes.payload(scopes.view(observation.record.scope_id))
        if observation.status == "selected" and observation.record is not None
        else None
    )
    data = CanonicalActiveData(observation.view(), observation.ancestors, scope=selected, snapshot=scopes.snapshot_payload())
    return OperationResult(namespace.command_path, "succeeded", data, 0, warnings=scopes.warnings())


def set_active(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    """Keep the same direct selection and repair its links; links never dangle (every chain directory exists)."""
    context.require_writer()
    scopes = load_canonical_scopes(context, timeout=namespace.timeout, link=True, offline=namespace.offline)
    target = resolve_scope(context, scopes.views, namespace.target)
    selection = read_selection(context, scopes.views)
    _check_guards(namespace, context, scopes, selection, target)
    if selection.status != "selected" or selection.record is None or selection.record.scope_id != target.id:
        return OperationResult(
            namespace.command_path,
            "failed",
            DiagnosticData(),
            3,
            error=Diagnostic("WORK_START_REQUIRED", "Use work start to acquire a direct selection", {}),
        )
    for view in (*ancestors_for(scopes.views, target), target):
        scopes.require_directory(view.id)
    effects, warnings = sync_selection_links(
        context, scopes.views, target.id, dry_run=namespace.dry_run, timeout=namespace.timeout
    )
    statuses = {effect.status for effect in effects}
    return OperationResult(
        namespace.command_path,
        "succeeded" if "succeeded" in statuses else "planned" if "planned" in statuses else "unchanged",
        ActiveData(selection.view(), selection.ancestors),
        0,
        effects=effects,
        warnings=(*scopes.warnings(), *warnings),
    )


def clear_active(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    """The legacy `active clear` steps; structure is read only for --from and --expect-* (no link is needed)."""
    context.require_writer()
    selected_handles = None
    scopes: CanonicalScopes | None = None
    if namespace.from_target is not None or namespace.expect_current is not None or namespace.expect_backend is not None:
        scopes = load_canonical_scopes(context, timeout=namespace.timeout, link=False, offline=namespace.offline)
        selection = read_selection(context, scopes.views)
        target = (
            resolve_scope(context, scopes.views, namespace.from_target)
            if namespace.from_target is not None
            else resolve_scope(context, scopes.views, selection.record.scope_id)
            if selection.record is not None
            else None
        )
        _check_guards(namespace, context, scopes, selection, target)
        if selection.status not in ("selected", "empty"):
            raise ValueError(selection.reason or "selection is not valid")
        if selection.record is not None and (
            target is not None and target.id not in (*selection.ancestors, selection.record.scope_id)
        ):
            return OperationResult(
                namespace.command_path, "unchanged", ActiveData(selection.view(), selection.ancestors), 0
            )
        selected_handles = (selection.handle,) if selection.record is not None and selection.handle is not None else ()
    views = scopes.views if scopes is not None else ()
    effects: list[Effect] = []
    try:
        with WorkTargetStore(context.root) as store:
            captured = store.read()
            handles = captured.observed_handles if selected_handles is None else selected_handles
            if captured.status == "unavailable":
                raise ValueError(captured.reason or "selection cannot be read safely")
            invalid = captured.status == "invalid" or (
                captured.record is not None
                and (
                    captured.record.clone_identity != context.clone_identity
                    or captured.record.worktree_identity != context.worktree_identity
                )
            )
            if invalid and ((not namespace.yes and not namespace.dry_run) or not captured.observed_handles):
                raise ValueError("invalid selection requires --all --yes and safely observed regular records")
            if namespace.dry_run:
                observed = _observe(context, views)
                planned_links, planned_warnings = sync_selection_links(
                    context, (), None, dry_run=True, timeout=namespace.timeout
                )
                return OperationResult(
                    namespace.command_path,
                    "planned",
                    ActiveData(observed.view(), observed.ancestors),
                    0,
                    effects=(
                        *(Effect("selection.clear", "planned", handle.token) for handle in handles),
                        *planned_links,
                    ),
                    warnings=planned_warnings,
                )
            for index, handle in enumerate(handles):
                try:
                    outcome = store.remove_observed(handle)
                    if outcome == "conflict":
                        raise ValueError("observed selection changed")
                except (ValueError, OSError, RuntimeError) as error:
                    effects.append(
                        Effect(
                            "selection.clear",
                            "unknown" if isinstance(error, SelectionRemovalUnknown) else "failed",
                            handle.token,
                        )
                    )
                    effects.extend(
                        Effect("selection.clear", "not_attempted", other.token) for other in handles[index + 1 :]
                    )
                    raise
                effects.append(
                    Effect("selection.clear", "succeeded" if outcome == "removed" else "unchanged", handle.token)
                )
        observed = _observe(context, views)
        link_warnings: tuple[Diagnostic, ...] = ()
        if observed.status == "empty":
            link_effects, link_warnings = sync_selection_links(
                context, (), None, dry_run=False, timeout=namespace.timeout
            )
            effects.extend(link_effects)
    except (ValueError, OSError, RuntimeError) as error:
        if effects:
            applied = any(effect.status in ("succeeded", "unknown") for effect in effects)
            return OperationResult(
                namespace.command_path,
                "partial" if applied else "failed",
                DiagnosticData(),
                6 if applied else 5 if isinstance(error, (OSError, RuntimeError)) else 3,
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
        warnings=link_warnings,
    )


def _observe(context: ProjectContext, views: tuple[ScopeView, ...]) -> SelectionObservation:
    with WorkTargetStore(context.root) as store:
        observed = store.read()
    return read_selection(context, views, stored=observed)


def _check_guards(
    namespace: argparse.Namespace,
    context: ProjectContext,
    scopes: CanonicalScopes,
    selection: SelectionObservation,
    target: ScopeView | None,
) -> None:
    if namespace.expect_backend is not None and (target is None or target.backend.kind != namespace.expect_backend):
        raise ValueError("target backend does not match --expect-backend")
    if namespace.expect_current is not None:
        expected = resolve_scope(context, scopes.views, namespace.expect_current).id
        if selection.status != "selected" or selection.record is None or selection.record.scope_id != expected:
            raise ValueError("direct target does not match --expect-current")


def query_artifact(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    """Scope Artifacts from the catalog's real path, shown under spec-dock/initiatives; @root stays legacy."""
    if namespace.scope == "@root" and namespace.expect_current is None:
        from spec_dock.runtime.application.direct_artifact import query_artifact as query_root

        return query_root(namespace, context)
    scopes = load_canonical_scopes(context, timeout=namespace.timeout, link=True, offline=namespace.offline)
    selection = read_selection(context, scopes.views)
    target = None if namespace.scope == "@root" else resolve_scope(context, scopes.views, namespace.scope, selection=selection)
    check_scope_expectations(
        context,
        scopes.views,
        selection,
        target=target,
        expected_current=namespace.expect_current,
        expected_backend=namespace.expect_backend,
    )
    if target is None:
        from spec_dock.runtime.application.direct_artifact import query_artifact as query_root

        return query_root(replace_namespace(namespace, expect_current=None), context)
    scopes.require_directory(target.id)
    directory = scopes.directories[target.id]
    assert scopes.catalog is not None
    items = catalog_artifacts(
        scopes.catalog.catalog / directory.relative.as_posix(),
        (LINK_RELATIVE / directory.relative).as_posix(),
        target.id,
    )
    if namespace.command_path == "artifact list":
        data = FamilyData(
            "artifact-list",
            {"scope_id": target.id, "items": tuple(map(_view, items)), "snapshot": scopes.snapshot_payload()},
        )
    else:
        matches = [item for item in items if item.artifact_id == namespace.artifact_id]
        if not matches:
            raise LookupError("Artifact was not found")
        if len(matches) != 1:
            raise ValueError("ARTIFACT_CATALOG_INVALID")
        data = FamilyData(
            "artifact", {"artifact": _view(matches[0]), "changed": False, "snapshot": scopes.snapshot_payload()}
        )
    return OperationResult(namespace.command_path, "succeeded", data, 0, warnings=scopes.warnings())


def replace_namespace(namespace: argparse.Namespace, **changes: object) -> argparse.Namespace:
    copied = copy.copy(namespace)
    for key, value in changes.items():
        setattr(copied, key, value)
    return copied


def catalog_artifacts(owner: Path, shown: str, scope_id: str) -> tuple[ArtifactCatalogEntry, ...]:
    """The legacy `list_artifacts` checks on a real catalog path; paths are shown as `<shown>/artifacts/<name>`."""
    artifacts_dir = owner / "artifacts"
    if not os.path.lexists(artifacts_dir):
        return ()
    if artifacts_dir.is_symlink() or not artifacts_dir.is_dir():
        raise ValueError("ARTIFACT_CATALOG_INVALID")
    descriptor = open_guarded_directory(artifacts_dir)
    entries: list[ArtifactCatalogEntry] = []
    try:
        problem, _ledger = scan_artifact_slot_ledger(artifacts_dir, directory_fd=descriptor)
        if problem is not None:
            raise ValueError("ARTIFACT_CATALOG_INVALID")
        with os.scandir(descriptor) as directory:
            for entry in directory:
                if entry.name == "rules.md":
                    continue
                parsed = parse_existing_artifact_filename(entry.name)
                if parsed is None:
                    continue
                info = entry.stat(follow_symlinks=False)
                if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                    raise ValueError("ARTIFACT_CATALOG_INVALID")
                creation_type: str | None = None
                if isinstance(parsed, GenericImportedArtifactFilename):
                    observed_type = "generic-file"
                elif isinstance(parsed, SequentialArtifactFilename):
                    observed_type = f"historical-{parsed.artifact_type}"
                elif parsed.artifact_type != "blank" and can_create_artifact_type(parsed.artifact_type):
                    creation_type = parsed.artifact_type
                    observed_type = "current-typed"
                elif parsed.artifact_type == "blank":
                    observed_type = "untyped-markdown"
                else:
                    observed_type = f"historical-{parsed.artifact_type}"
                entries.append(
                    ArtifactCatalogEntry(
                        parsed.artifact_id,
                        scope_id,
                        f"{shown}/artifacts/{entry.name}",
                        creation_type,
                        observed_type,
                        "unverified",
                    )
                )
        fresh = open_guarded_directory(artifacts_dir)
        try:
            before, after = os.fstat(descriptor), os.fstat(fresh)
            if (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino):
                raise ValueError("ARTIFACT_CATALOG_INVALID")
        finally:
            os.close(fresh)
    finally:
        os.close(descriptor)
    return tuple(sorted(entries, key=lambda item: item.artifact_id))
