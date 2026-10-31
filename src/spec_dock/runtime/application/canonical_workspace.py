"""Canonical-mode `workspace validate/sync/doctor` and the `canonical status --structure` item (iss-00431).

Structure comes from the structure snapshot and directories from the catalog (Epic design ch. 6). Errors are
findings (exit 7 for validate); warnings never change the outcome. Nothing is written except the snapshot.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import os
from pathlib import Path
from typing import TYPE_CHECKING, Final

from spec_dock.runtime.application.canonical_errors import (
    CANONICAL_NOT_APPLICABLE,
    CHECK_INSTEAD_RECOVERY,
    CanonicalCommandError,
)
from spec_dock.runtime.application.canonical_scope_read import resolve_source
from spec_dock.runtime.application.canonical_scopes import (
    check_canonical_scope_expectations,
    load_canonical_scopes,
    refuse_old_ids,
)
from spec_dock.runtime.application.canonical_worktrees import is_catalog
from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.application.scope_check import (
    CUE_DOCUMENTS,
    MARKDOWN_DOCUMENTS,
    SCOPE_FORMAT_CONFLICT,
    scope_format,
)
from spec_dock.runtime.application.worktree_observation import SelectionObservation, read_selection
from spec_dock.runtime.domain.canonical_layout import scope_relative
from spec_dock.runtime.domain.canonical_structure import SCOPE_KIND_CHANGED, parse_scope_id
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
    from spec_dock.runtime.infra.catalog_tree import MisplacedDirectory

# A Markdown Scope's documents; a CUE Scope (requirement.cue) needs CUE_DOCUMENTS instead (iss-00473).
REQUIRED_DOCUMENTS: Final = MARKDOWN_DOCUMENTS

SCOPE_DIRECTORY_MISSING: Final = "SCOPE_DIRECTORY_MISSING"
SCOPE_DIRECTORY_MISPLACED: Final = "SCOPE_DIRECTORY_MISPLACED"
SCOPE_ISSUE_MISSING: Final = "SCOPE_ISSUE_MISSING"
SCOPE_DOCUMENT_MISSING: Final = "SCOPE_DOCUMENT_MISSING"
SCOPE_METADATA_PRESENT: Final = "SCOPE_METADATA_PRESENT"
CANONICAL_CONFLICT_COPY: Final = "CANONICAL_CONFLICT_COPY"
DEPENDENCY_NOT_SCOPE: Final = "DEPENDENCY_NOT_SCOPE"
MISPLACED_NEXT_STEP: Final = (
    "Move the Scope contents it holds into spec-dock/initiatives/<bucket>/<ID>/ for each ID (the bucket is the ID "
    "number's thousand range, e.g. 00000-00999/iss-00454) and delete the emptied directory."
)
DIRECTORY_MISSING_NEXT_STEP: Final = (
    "Create spec-dock/initiatives/{path}/ with the Scope documents, or put back the directory that was moved "
    "or renamed."
)
ISSUE_MISSING_NEXT_STEP: Final = (
    "Check GitHub Issue #{number} and its spec-dock kind label; if the Scope is gone, move the directory's contents "
    "out of the catalog and delete it."
)


@dataclass(frozen=True)
class StructureReport:
    errors: tuple[Diagnostic, ...]
    warnings: tuple[Diagnostic, ...]


@dataclass(frozen=True)
class DirectoryReport:
    """How catalog `<bucket>/<ID>/` directories match GitHub (Epic design ch. 2): three errors and one warning code."""

    errors: tuple[Diagnostic, ...]
    warnings: tuple[Diagnostic, ...]


def directory_anomalies(scopes: CanonicalScopes) -> DirectoryReport:
    """SCOPE_KIND_CHANGED once per number, never also MISSING or ISSUE_MISSING for it; nothing without a catalog."""
    catalog = scopes.catalog
    if catalog is None:
        return DirectoryReport((), ())
    changed = scopes.kind_changes
    errors: list[Diagnostic] = [
        Diagnostic(item.code, item.message, dict(item.details))
        for item in scopes.kind_change_warnings()
        if item.code == SCOPE_KIND_CHANGED
    ]
    for node in scopes.snapshot.scopes:
        scope_id = str(node.id)
        if scope_id not in scopes.directories and node.number not in changed:
            path = scope_relative(scope_id).as_posix()
            errors.append(
                Diagnostic(
                    SCOPE_DIRECTORY_MISSING,
                    f"{scope_id} has no directory {path}/ in the catalog",
                    {"scope_id": scope_id, "path": path, "next_step": DIRECTORY_MISSING_NEXT_STEP.format(path=path)},
                )
            )
    for item in catalog.tree.directories():
        number = parse_scope_id(item.scope_id)[1]
        if number not in scopes.snapshot.issues:
            errors.append(
                Diagnostic(
                    SCOPE_ISSUE_MISSING,
                    f"{item.relative} has no Scope Issue in GitHub",
                    {
                        "scope_id": item.scope_id,
                        "path": item.relative.as_posix(),
                        "next_step": ISSUE_MISSING_NEXT_STEP.format(number=number),
                    },
                )
            )
    warnings = tuple(
        Diagnostic(
            SCOPE_DIRECTORY_MISPLACED,
            _misplaced_message(item),
            {
                "path": item.relative.as_posix(),
                "reason": item.reason,
                "expected": None if item.expected is None else item.expected.as_posix(),
                "next_step": MISPLACED_NEXT_STEP,
            },
        )
        for item in catalog.tree.misplaced()
    )
    return DirectoryReport(tuple(errors), warnings)


def _misplaced_message(item: MisplacedDirectory) -> str:
    if item.reason == "root":
        return f"{item.relative} is at the catalog root; Scope directories live under their number's bucket"
    if item.reason == "bucket":
        if item.expected is None:
            return f"{item.relative} is not a bucket of its numbers"
        return f"{item.relative} is in another number's bucket; it belongs in {item.expected}"
    if item.reason == "name":
        return f"{item.relative} is not a Scope directory <ID>/ in its bucket"
    return f"{item.relative} is left from the nested layout inside a Scope directory"


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
    catalog = scopes.catalog
    if catalog is not None:
        directories = directory_anomalies(scopes)
        errors.extend(directories.errors)
        warnings.extend(directories.warnings)
        for view in scopes.views:
            directory = scopes.directories.get(view.id)
            if directory is None:
                continue
            found = scope_format(directory.path)
            if found == "conflict":
                errors.append(
                    Diagnostic(
                        SCOPE_FORMAT_CONFLICT,
                        f"{view.id} has both requirement.md and requirement.cue; keep one format",
                        {"scope_id": view.id, "path": directory.relative.as_posix()},
                    )
                )
                continue
            required = CUE_DOCUMENTS if found == "cue" else REQUIRED_DOCUMENTS
            missing = [name for name in required if not (directory.path / name).is_file()]
            if missing:
                errors.append(
                    Diagnostic(
                        SCOPE_DOCUMENT_MISSING,
                        f"{view.id} lacks {', '.join(missing)}",
                        {"scope_id": view.id, "path": directory.relative.as_posix(), "missing": missing},
                    )
                )
        errors.extend(
            Diagnostic(SCOPE_METADATA_PRESENT, f"{path} is a legacy .meta.json in the catalog", {"path": path})
            for path in _metadata_files(catalog.catalog)
        )
        warnings.extend(
            Diagnostic(
                CANONICAL_CONFLICT_COPY,
                f"{path} is a conflict copy; merge it into its original file, then delete it",
                {"path": path},
            )
            for path in catalog_change_summary(catalog.catalog, timeout=timeout).conflict_files
        )
    return StructureReport(tuple(errors), tuple(warnings))


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
    refuse_old_ids(scopes, namespace.expect_current)  # an old ID is SCOPE_KIND_CHANGED, not a structure failure
    if findings and namespace.expect_current:
        raise ValueError("--expect-current cannot be verified from invalid workspace structure")
    check_canonical_scope_expectations(
        context,
        scopes,
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
        warnings=(*scopes.snapshot_warnings(), *report.warnings),
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
        check_canonical_scope_expectations(
            context,
            scopes,
            read_selection(context, scopes.views),
            target=None,
            expected_current=namespace.expect_current,
            expected_backend=namespace.expect_backend,
        )
    rows = _observe_rows(context, scopes, timeout=namespace.timeout)
    states: dict[tuple[str, str | None], str] = {(view.id, view.github_ref): view.status.state for view in scopes.views}
    titles = {view.id: view.title for view in scopes.views}
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
            # The GitHub title, in any language (AC-09, iss-00432); None for a selection of an unknown Scope.
            {"scope_id": scope_id, "github_ref": github_ref, "lifecycle": state, "title": titles.get(scope_id)}
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
    except (GitProcessError, OSError) as error:
        findings += (
            Diagnostic("GIT_FAILED" if isinstance(error, GitProcessError) else "LOCAL_IO_FAILED", str(error), {}),
        )
    scopes: CanonicalScopes | None
    try:
        scopes = load_canonical_scopes(context, timeout=namespace.timeout, link=False, offline=namespace.offline)
    except (GithubStructureError, ValueError, GitProcessError, OSError) as error:
        if isinstance(error, GithubStructureError):
            finding = Diagnostic(error.code, error.message, {"endpoint": error.endpoint, "retry_at": error.retry_at})
        else:
            finding = Diagnostic(
                "GIT_FAILED" if isinstance(error, GitProcessError) else "PRECONDITION_FAILED", str(error), {}
            )
        findings += (finding,)
        unverified += ("The GitHub structure could not be read.",)
        if namespace.expect_current:
            raise ValueError("--expect-current cannot be verified without the GitHub structure") from error
        scopes = None
    if scopes is not None:
        report = inspect_canonical_structure(scopes, timeout=namespace.timeout)
        findings += report.errors
        warnings += (*scopes.snapshot_warnings(), *report.warnings)
        refuse_old_ids(scopes, namespace.expect_current)
        if report.errors and namespace.expect_current:
            raise ValueError("--expect-current cannot be verified from invalid workspace structure")
        selection = read_selection(context, scopes.views)
        check_canonical_scope_expectations(
            context,
            scopes,
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


def structure_item(
    context: ProjectContext, *, timeout: float, offline: bool = False
) -> tuple[dict[str, object], tuple[Diagnostic, ...]]:
    """`canonical status --structure`: the four directory anomalies at display freshness; failures stay inside."""
    try:
        scopes = load_canonical_scopes(context, timeout=timeout, link=True, offline=offline)
    except CanonicalCommandError as error:
        return _unavailable(error.code, error.message, error.recovery[0] if error.recovery else None), ()
    except GithubStructureError as error:
        return _unavailable(error.code, error.message, "Check the network connection and run gh auth status."), ()
    except (ValueError, GitProcessError) as error:
        return _unavailable("PRECONDITION_FAILED", str(error), "Check that origin points at the GitHub repository."), ()
    except (OSError, RuntimeError) as error:
        return _unavailable(
            "LOCAL_IO_FAILED", str(error), "Check that the state root and the catalog are readable."
        ), ()
    try:
        report = directory_anomalies(scopes)
    except OSError as error:  # an unreadable Scope directory stays inside this item
        return _unavailable(
            "LOCAL_IO_FAILED", str(error), "Check that the state root and the catalog are readable."
        ), scopes.snapshot_warnings()
    found = (*(("error", item) for item in report.errors), *(("warning", item) for item in report.warnings))
    next_steps = [item.details["next_step"] for _, item in found if "next_step" in item.details]
    entry: dict[str, object] = {
        "status": "problem" if found else "ok",
        "next_step": next_steps[0] if next_steps else None,
        "snapshot": scopes.snapshot_payload(),
        "anomalies": [
            {"code": item.code, "severity": severity, "message": item.message, "details": dict(item.details)}
            for severity, item in found
        ],
    }
    warnings = tuple(Diagnostic(item.code, item.message, {"item": "structure", **item.details}) for _, item in found)
    return entry, (*scopes.snapshot_warnings(), *warnings)


def _unavailable(code: str, message: str, next_step: str | None) -> dict[str, object]:
    return {"status": "unavailable", "code": code, "message": message, "next_step": next_step}
