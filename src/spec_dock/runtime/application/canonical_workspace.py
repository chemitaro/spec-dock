"""Canonical-mode `workspace validate/sync/doctor` and the `canonical status --structure` item (iss-00431).

Structure comes from the structure snapshot and directories from the catalog (Epic design ch. 6). Errors are
findings (exit 7 for validate); warnings never change the outcome. Nothing is written except the snapshot.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import os
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Final

from spec_dock.runtime.application.canonical_errors import (
    CANONICAL_NOT_APPLICABLE,
    CHECK_INSTEAD_RECOVERY,
    CanonicalCommandError,
)
from spec_dock.runtime.application.canonical_scope_read import resolve_source
from spec_dock.runtime.application.canonical_scopes import load_canonical_scopes
from spec_dock.runtime.application.canonical_worktrees import is_catalog
from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.application.scope_expectations import check_scope_expectations
from spec_dock.runtime.application.worktree_observation import SelectionObservation, read_selection
from spec_dock.runtime.infra.canonical_git import catalog_change_summary
from spec_dock.runtime.infra.git_cli import worktree_list
from spec_dock.runtime.infra.git_process import GitProcessError
from spec_dock.runtime.infra.github_structure import GithubStructureError
from spec_dock.runtime.infra.work_target_store import WorkTargetStore
from spec_dock.runtime.presentation.command_data import CanonicalDiagnosticData, CanonicalSyncData, FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.canonical_scopes import CanonicalScopes
    from spec_dock.runtime.application.project_context import ProjectContext

REQUIRED_DOCUMENTS: Final = ("requirement.md", "design.md", "plan.md", "report.md")
_NESTING: Final = {"epic": "epics", "issue": "issues"}

SCOPE_DIRECTORY_SLUG_MISMATCH: Final = "SCOPE_DIRECTORY_SLUG_MISMATCH"
SCOPE_DIRECTORY_DUPLICATE: Final = "SCOPE_DIRECTORY_DUPLICATE"
SCOPE_DIRECTORY_MISSING: Final = "SCOPE_DIRECTORY_MISSING"
SCOPE_DIRECTORY_MISPLACED: Final = "SCOPE_DIRECTORY_MISPLACED"
SCOPE_ISSUE_MISSING: Final = "SCOPE_ISSUE_MISSING"
SCOPE_DOCUMENT_MISSING: Final = "SCOPE_DOCUMENT_MISSING"
SCOPE_METADATA_PRESENT: Final = "SCOPE_METADATA_PRESENT"
CANONICAL_CONFLICT_COPY: Final = "CANONICAL_CONFLICT_COPY"
DEPENDENCY_NOT_SCOPE: Final = "DEPENDENCY_NOT_SCOPE"


@dataclass(frozen=True)
class StructureReport:
    errors: tuple[Diagnostic, ...]
    warnings: tuple[Diagnostic, ...]
    misplaced: tuple[dict[str, object], ...]


def misplaced_scopes(scopes: CanonicalScopes) -> tuple[dict[str, object], ...]:
    """Directories not nested under their GitHub parent's directory; a parent without a directory is skipped."""
    found: list[dict[str, object]] = []
    for view in scopes.views:
        directory = scopes.directories.get(view.id)
        if directory is None:
            continue
        name = directory.relative.name
        if view.parent_id is None:
            expected = PurePosixPath(name)
        else:
            parent = scopes.directories.get(view.parent_id)
            if parent is None:
                continue
            expected = parent.relative / _NESTING[view.kind] / name
        if directory.relative != expected:
            next_step = f"spec-dock scope move {view.id}"
            found.append({
                "scope_id": view.id,
                "path": directory.relative.as_posix(),
                "expected": expected.as_posix(),
                "next_step": next_step,
            })
    return tuple(found)


def inspect_canonical_structure(scopes: CanonicalScopes, *, timeout: float) -> StructureReport:
    errors: list[Diagnostic] = [
        Diagnostic(item.code, item.message, {"number": item.number}) for item in scopes.snapshot.anomalies
    ]
    warnings: list[Diagnostic] = []
    for view in scopes.views:
        node = scopes.node(view.id)
        for number in node.blocked_by:
            external = scopes.snapshot.external.get(number)
            if external is not None:
                warnings.append(
                    Diagnostic(
                        DEPENDENCY_NOT_SCOPE,
                        f"{view.id} depends on #{number}, which is not a Scope",
                        {"scope_id": view.id, "number": number, "state": external.state},
                    )
                )
    misplaced: tuple[dict[str, object], ...] = ()
    catalog = scopes.catalog
    if catalog is not None:
        known = {view.id for view in scopes.views}
        for view in scopes.views:
            if view.id in scopes.ambiguous:
                errors.append(
                    Diagnostic(
                        SCOPE_DIRECTORY_DUPLICATE,
                        f"{view.id} has more than one directory in the catalog",
                        {
                            "scope_id": view.id,
                            "paths": [item.relative.as_posix() for item in scopes.ambiguous[view.id]],
                        },
                    )
                )
                continue
            directory = scopes.directories.get(view.id)
            if directory is None:
                errors.append(
                    Diagnostic(
                        SCOPE_DIRECTORY_MISSING, f"{view.id} has no directory in the catalog", {"scope_id": view.id}
                    )
                )
                continue
            slug = scopes.node(view.id).slug
            if directory.relative.name != f"{view.id}-{slug}":
                errors.append(
                    Diagnostic(
                        SCOPE_DIRECTORY_SLUG_MISMATCH,
                        f"{directory.relative} does not match the GitHub slug {slug!r} of {view.id}",
                        {"scope_id": view.id, "path": directory.relative.as_posix(), "slug": slug},
                    )
                )
            real = catalog.catalog / directory.relative.as_posix()
            missing = [name for name in REQUIRED_DOCUMENTS if not (real / name).is_file()]
            if missing:
                errors.append(
                    Diagnostic(
                        SCOPE_DOCUMENT_MISSING,
                        f"{view.id} lacks {', '.join(missing)}",
                        {"scope_id": view.id, "path": directory.relative.as_posix(), "missing": missing},
                    )
                )
        for item in catalog.tree.directories():
            if item.scope_id not in known:
                errors.append(
                    Diagnostic(
                        SCOPE_ISSUE_MISSING,
                        f"{item.relative} has no Scope Issue in GitHub",
                        {"scope_id": item.scope_id, "path": item.relative.as_posix()},
                    )
                )
        errors.extend(
            Diagnostic(SCOPE_METADATA_PRESENT, f"{path} is a legacy .meta.json in the catalog", {"path": path})
            for path in _metadata_files(catalog.catalog)
        )
        misplaced = misplaced_scopes(scopes)
        warnings.extend(
            Diagnostic(
                SCOPE_DIRECTORY_MISPLACED,
                f"{item['scope_id']} is at {item['path']}; GitHub places it at {item['expected']}",
                dict(item),
            )
            for item in misplaced
        )
        warnings.extend(
            Diagnostic(
                CANONICAL_CONFLICT_COPY,
                f"{path} is a conflict copy; merge it into its original file, then delete it",
                {"path": path},
            )
            for path in catalog_change_summary(catalog.catalog, timeout=timeout).conflict_files
        )
    return StructureReport(tuple(errors), tuple(warnings), misplaced)


def _metadata_files(catalog: Path) -> list[str]:
    found: list[str] = []
    for directory, names, files in os.walk(catalog):
        names[:] = sorted(name for name in names if not name.startswith("."))
        if ".meta.json" in files:
            found.append((Path(directory) / ".meta.json").relative_to(catalog).as_posix())
    return sorted(found)


def validate_workspace(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    if namespace.ci:
        raise CanonicalCommandError(
            CANONICAL_NOT_APPLICABLE,
            "workspace validate --ci checks committed .meta.json; a canonical workspace keeps no specs on this branch",
            recovery=(CHECK_INSTEAD_RECOVERY,),
            details={"next_step": CHECK_INSTEAD_RECOVERY},
        )
    scopes = load_canonical_scopes(context, timeout=namespace.timeout, link=True, offline=namespace.offline)
    report = inspect_canonical_structure(scopes, timeout=namespace.timeout)
    findings = report.errors
    if findings and namespace.expect_current:
        raise ValueError("--expect-current cannot be verified from invalid workspace structure")
    check_scope_expectations(
        context,
        scopes.views,
        read_selection(context, scopes.views) if namespace.expect_current else None,
        target=None,
        expected_current=namespace.expect_current,
        expected_backend=namespace.expect_backend,
    )
    if namespace.require_nodes and not scopes.views:
        findings += (Diagnostic("NODES_REQUIRED", "at least one safely validated Scope is required", {}),)
    valid = not findings
    return OperationResult(
        namespace.command_path,
        "succeeded" if valid else "failed",
        FamilyData(
            "validation",
            {
                "valid": valid,
                "findings": findings,
                "snapshot_source": "github-snapshot",
                "snapshot_oid": None,
                "node_count": len(scopes.views),
                "snapshot": scopes.snapshot_payload(),
            },
        ),
        0 if valid else 7,
        warnings=(*scopes.warnings(), *report.warnings),
        error=None
        if valid
        else Diagnostic("WORKSPACE_VALIDATION_FAILED", "workspace structure is invalid or incomplete", {}),
    )


@dataclass(frozen=True)
class _Row:
    path: str
    selection: SelectionObservation
    error: Exception | None = None


def _observe_rows(context: ProjectContext, scopes: CanonicalScopes, *, timeout: float) -> tuple[_Row, ...]:
    rows: list[_Row] = []
    seen: set[object] = set()
    for entry in worktree_list(context.root, timeout=timeout):
        stored = None
        try:
            if entry.inventory_error is not None:
                raise ValueError(entry.inventory_error)
            if entry.bare:
                raise ValueError("bare repository is not a working tree")
            if is_catalog(entry):
                continue
            other = resolve_context(str(entry.path), context.root, timeout=timeout)
            if other.clone_identity != context.clone_identity:
                raise ValueError("worktree common directory identity mismatch")
            if other.worktree_identity in seen:
                continue
            seen.add(other.worktree_identity)
            with WorkTargetStore(other.root) as store:
                stored = store.read()
            rows.append(_Row(str(entry.path), read_selection(other, scopes.views, stored=stored)))
        except (OSError, ValueError, RuntimeError) as error:
            record = stored.record if stored is not None else None
            handle = stored.handle if stored is not None else None
            rows.append(
                _Row(
                    str(entry.path),
                    SelectionObservation("unavailable", record, handle, entry.branch, reason=str(error)),
                    error,
                )
            )
    return tuple(rows)


def sync_workspace(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    refresh, offline = resolve_source(namespace)
    scopes = load_canonical_scopes(context, timeout=namespace.timeout, link=False, refresh=refresh, offline=offline)
    if namespace.expect_current is not None or namespace.expect_backend is not None:
        check_scope_expectations(
            context,
            scopes.views,
            read_selection(context, scopes.views),
            target=None,
            expected_current=namespace.expect_current,
            expected_backend=namespace.expect_backend,
        )
    rows = _observe_rows(context, scopes, timeout=namespace.timeout)
    states: dict[tuple[str, str | None], str] = {(view.id, view.github_ref): view.status.state for view in scopes.views}
    for row in rows:
        record = row.selection.record
        if record is not None and row.selection.status in ("selected", "stale", "unavailable"):
            states.setdefault((record.scope_id, record.github_ref), "unknown")
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
        for row in rows
        if row.selection.status not in ("selected", "empty")
    }
    selected: dict[str, str] = {}
    for row in rows:
        record = row.selection.record
        if row.selection.status not in ("selected", "stale", "unavailable") or record is None:
            continue
        previous = selected.get(record.scope_id)
        if previous is not None:
            row_findings[row.path] = (
                *row_findings.get(row.path, ()),
                Diagnostic(
                    "SELECTION_DUPLICATE",
                    "More than one worktree selects the same Scope",
                    {"scope_id": record.scope_id, "github_ref": record.github_ref, "paths": (previous, row.path)},
                ),
            )
        selected[record.scope_id] = row.path
    findings = tuple(finding for group in row_findings.values() for finding in group)
    complete = not findings
    data = CanonicalSyncData(
        datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "github" if refresh else "snapshot",
        complete,
        tuple(
            {
                "path": row.path,
                "selection": row.selection.view(),
                "lifecycle": states.get((row.selection.record.scope_id, row.selection.record.github_ref), "unknown")
                if row.selection.record
                else "unknown",
                "process_state": "not_observed",
                "findings": row_findings.get(row.path, ()),
            }
            for row in rows
        ),
        tuple(
            {"scope_id": scope_id, "github_ref": github_ref, "lifecycle": state}
            for (scope_id, github_ref), state in states.items()
        ),
        tuple(
            {
                "scope_id": scope_id,
                "direct_selected_count": sum(
                    row.selection.status in ("selected", "stale", "unavailable")
                    and row.selection.record is not None
                    and row.selection.record.scope_id == scope_id
                    for row in rows
                ),
                "descendant_selected_count": sum(
                    row.selection.status == "selected" and scope_id in row.selection.ancestors for row in rows
                ),
                "complete": complete,
            }
            for scope_id in dict.fromkeys(scope_id for scope_id, _ in states)
        ),
        findings,
        snapshot=scopes.snapshot_payload(),
    )
    if findings:
        return OperationResult(
            namespace.command_path,
            "partial",
            data,
            7,
            warnings=scopes.warnings(),
            error=Diagnostic("SYNC_INCOMPLETE", "Some requested observations are incomplete", {}),
        )
    return OperationResult(namespace.command_path, "succeeded", data, 0, warnings=scopes.warnings())


def diagnose_workspace(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    """Today's doctor items plus the canonical status items; the link is not required (problems are findings)."""
    from spec_dock.runtime.application.canonical_catalog import require_linked
    from spec_dock.runtime.application.canonical_status import status_of
    from spec_dock.runtime.application.direct_diagnostics import _github_request, _legacy_diagnostics, _probe_github
    from spec_dock.runtime.infra import runtime_environment

    request = _github_request(namespace)
    findings: tuple[Diagnostic, ...] = ()
    warnings: tuple[Diagnostic, ...] = ()
    unverified: tuple[str, ...] = ()
    try:
        require_linked(context, timeout=namespace.timeout)
    except CanonicalCommandError as error:
        findings += (Diagnostic(error.code, error.message, dict(error.details)),)
    try:
        scopes = load_canonical_scopes(context, timeout=namespace.timeout, link=False, offline=namespace.offline)
    except GithubStructureError as error:
        findings += (Diagnostic(error.code, error.message, {"endpoint": error.endpoint, "retry_at": error.retry_at}),)
        unverified += ("The GitHub structure could not be read.",)
        if namespace.expect_current:
            raise ValueError("--expect-current cannot be verified without the GitHub structure") from error
        scopes = None
    if scopes is not None:
        report = inspect_canonical_structure(scopes, timeout=namespace.timeout)
        findings += report.errors
        warnings += (*scopes.warnings(), *report.warnings)
        if report.errors and namespace.expect_current:
            raise ValueError("--expect-current cannot be verified from invalid workspace structure")
        selection = read_selection(context, scopes.views)
        check_scope_expectations(
            context,
            scopes.views,
            selection,
            target=None,
            expected_current=namespace.expect_current,
            expected_backend=namespace.expect_backend,
        )
        if selection.status not in ("empty", "selected"):
            findings += (
                Diagnostic(
                    "DIRECT_SELECTION_UNVERIFIED",
                    selection.reason or "direct selection cannot be verified",
                    {"status": selection.status},
                ),
            )
    incomplete = bool(findings)
    if namespace.legacy:
        legacy_findings, legacy_incomplete = _legacy_diagnostics(context)
        findings += legacy_findings
        incomplete |= legacy_incomplete
    github_findings, github_unverified, github_incomplete = _probe_github(request, timeout=namespace.timeout)
    findings += github_findings
    unverified += github_unverified
    incomplete |= github_incomplete
    status = status_of(
        context,
        runtime_environment.detect_runtime_environment(),
        command=namespace.command_path,
        timeout=namespace.timeout,
    )
    warnings += status.warnings
    return OperationResult(
        namespace.command_path,
        "failed" if incomplete else "succeeded",
        CanonicalDiagnosticData(findings, unverified, canonical=asdict(status.data)),  # type: ignore[call-overload]
        7 if incomplete else 0,
        warnings=warnings,
        error=Diagnostic("WORKSPACE_DIAGNOSIS_INCOMPLETE", "workspace evidence is incomplete", {})
        if incomplete
        else None,
    )


def structure_item(context: ProjectContext, *, timeout: float) -> tuple[dict[str, object], tuple[Diagnostic, ...]]:
    """`canonical status --structure`: nesting drift at display freshness; failures stay inside the item."""
    try:
        scopes = load_canonical_scopes(context, timeout=timeout, link=True)
    except CanonicalCommandError as error:
        return _unavailable(error.code, error.message, error.recovery[0] if error.recovery else None), ()
    except GithubStructureError as error:
        return _unavailable(error.code, error.message, "Check the network connection and run gh auth status."), ()
    except (ValueError, GitProcessError) as error:
        return _unavailable("PRECONDITION_FAILED", str(error), "Check that origin points at the GitHub repository."), ()
    misplaced = misplaced_scopes(scopes)
    warnings = tuple(
        Diagnostic(
            SCOPE_DIRECTORY_MISPLACED,
            f"{item['scope_id']} is at {item['path']}; GitHub places it at {item['expected']}; next: {item['next_step']}",
            {"item": "structure", **item},
        )
        for item in misplaced
    )
    item: dict[str, object] = {
        "status": "problem" if misplaced else "ok",
        "next_step": misplaced[0]["next_step"] if misplaced else None,
        "snapshot": scopes.snapshot_payload(),
        "misplaced": list(misplaced),
    }
    return item, (*scopes.warnings(), *warnings)


def _unavailable(code: str, message: str, next_step: str | None) -> dict[str, object]:
    return {"status": "unavailable", "code": code, "message": message, "next_step": next_step}
