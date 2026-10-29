"""`spec-dock canonical status`: read the catalog, links, ignore rules, access and tool settings (R-B7).

It writes nothing in the repository, the catalog, .git, the state root or GitHub and never contacts the
remote. Only with --structure does it read GitHub's structure at display freshness, which may refresh the
structure snapshot (iss-00431) and reports how catalog `<ID>/` directories match it (iss-00455). The sync, snapshot and state.json parts come from canonical_status_sync
(iss-00430). The dashboard item is "not_implemented" (iss-00438); without --structure, `structure` is
"not_checked".
"""

from __future__ import annotations

import os
from pathlib import Path
import stat
from typing import TYPE_CHECKING, Protocol

from spec_dock.runtime.application.canonical_catalog import (
    CatalogObservation,
    gitignore_next_step,
    observe_catalog,
    occupied_next_step,
    resolve_layout,
)
from spec_dock.runtime.application.canonical_errors import (
    CANONICAL_FOREIGN_CHECKOUT,
    CANONICAL_FORMAT_UNSUPPORTED,
    CANONICAL_GIT_TOO_OLD,
    CANONICAL_IGNORE_RULES_MISSING,
    CANONICAL_LINK_OCCUPIED,
    CANONICAL_MAIN_NOT_MIGRATED,
    CANONICAL_NOT_LINKED,
    CANONICAL_NOT_LINKED_RECOVERY,
    CANONICAL_PATH_OCCUPIED,
    FOREIGN_CHECKOUT_RECOVERY,
    FORMAT_MISSING_RECOVERY,
    FORMAT_UNSUPPORTED_RECOVERY,
    GIT_TOO_OLD_RECOVERY,
    MAIN_NOT_MIGRATED_NEXT_STEP,
    OS_ACCESS_DENIED,
)
from spec_dock.runtime.application.canonical_link import (
    elsewhere_next_step,
    link_occupied_next_step,
    main_not_migrated_message,
)
from spec_dock.runtime.application.canonical_tools_check import tool_findings
from spec_dock.runtime.application.project_context import probe_workspace_mode
from spec_dock.runtime.domain.canonical_content import CANONICAL_FORMAT, FORMAT_FILE, format_writable, read_format
from spec_dock.runtime.domain.canonical_layout import GITIGNORE_PATH, MINIMUM_GIT_VERSION
from spec_dock.runtime.infra import canonical_git, runtime_environment
from spec_dock.runtime.infra.git_process import GitProcessError
from spec_dock.runtime.presentation.command_data import CanonicalStatusData
from spec_dock.runtime.presentation.envelope import Diagnostic, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.domain.canonical_layout import CatalogLayout
    from spec_dock.runtime.infra.runtime_environment import RuntimeEnvironment


class Problem(Protocol):
    """Record one problem as a warning and return its next step."""

    def __call__(self, item: str, code: str, message: str, next_step: str, **details: object) -> str: ...


_CONFLICT_NEXT_STEP = "Merge each conflict copy's contents into its original file, then delete the copy."


def _not_implemented(owner: str) -> dict[str, object]:
    return {"status": "not_implemented", "next_step": None, "owner": owner}


def run_canonical_status(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    environment = runtime_environment.detect_runtime_environment()
    return status_of(
        context,
        environment,
        command=namespace.command_path,
        timeout=namespace.timeout,
        structure=bool(getattr(namespace, "structure", False)),
        offline=bool(getattr(namespace, "offline", False)),
    )


def status_of(
    context: ProjectContext,
    environment: RuntimeEnvironment,
    *,
    command: str,
    timeout: float,
    structure: bool = False,
    offline: bool = False,
) -> OperationResult[object]:
    layout = resolve_layout(context)
    warnings: list[Diagnostic] = []

    def problem(item: str, code: str, message: str, next_step: str, **details: object) -> str:
        warnings.append(
            Diagnostic(code, f"{message}; next: {next_step}", {"item": item, "next_step": next_step, **details})
        )
        return next_step

    git = environment.git
    git_item: dict[str, object] = {
        "status": "ok" if git.supported else "problem",
        "next_step": None,
        "path": git.path,
        "version": git.reported,
        "supported": git.supported,
        "minimum": ".".join(str(part) for part in MINIMUM_GIT_VERSION),
    }
    if not git.supported:
        git_item["next_step"] = problem(
            "git", CANONICAL_GIT_TOO_OLD, "Git 2.38 or later is required", GIT_TOO_OLD_RECOVERY
        )
    observation: CatalogObservation | None = None
    inspect_error: OSError | None = None
    if git.supported:
        try:
            observation = observe_catalog(layout, environment, timeout=timeout)
        except GitProcessError:
            observation = None
        except OSError as error:
            # Report the denied path as the access problem and keep reporting the other items.
            inspect_error = error
    catalog_item = _catalog_item(layout, observation, problem)
    main_migrated = layout.is_main or probe_workspace_mode(layout.main_checkout) == "canonical"
    link_item = _link_item(observation, problem, main_migrated=main_migrated)
    exclude_item = _exclude_item(layout, observation, problem)
    access_item = _access_item(layout, observation, problem, sandboxed=environment.codex_sandbox and not layout.is_main)
    if inspect_error is not None:
        denied = inspect_error.filename or layout.catalog
        access_item["status"] = "problem"
        access_item["next_step"] = problem(
            "access",
            OS_ACCESS_DENIED,
            f"this process cannot inspect {denied}: {inspect_error.strerror or inspect_error}",
            f"Check the permissions of {denied}.",
            path=str(denied),
        )
    tools_item, tool_warnings = tool_findings(layout, environment)
    warnings.extend(tool_warnings)
    format_item = _format_item(layout, observation, problem)
    changes_item = _changes_item(layout, observation, timeout=timeout)
    from spec_dock.runtime.application.canonical_status_sync import SyncView

    view = SyncView.read(layout, environment, problem, timeout=timeout)
    view.extend_changes(changes_item)
    view.extend_git(git_item)
    data = CanonicalStatusData(
        catalog=catalog_item,
        link=link_item,
        exclude=exclude_item,
        access=access_item,
        tools=tools_item,
        sync=view.sync_item(),
        changes=changes_item,
        format=format_item,
        git=git_item,
        snapshot=view.snapshot_item(),
        dashboard=_not_implemented("iss-00438"),
        structure=_structure_item(context, timeout=timeout, offline=offline, warnings=warnings)
        if structure
        else _NOT_CHECKED,
    )
    return OperationResult(command, "succeeded", data, 0, warnings=tuple(warnings))


_NOT_CHECKED: dict[str, object] = {"status": "not_checked", "next_step": None}


def _structure_item(
    context: ProjectContext, *, timeout: float, offline: bool, warnings: list[Diagnostic]
) -> dict[str, object]:
    """Only with --structure: the snapshot at display freshness and the four directory anomalies (iss-00455)."""
    from spec_dock.runtime.application.canonical_workspace import structure_item

    item, found = structure_item(context, timeout=timeout, offline=offline)
    warnings.extend(found)
    return item


def _catalog_item(layout: CatalogLayout, observation: CatalogObservation | None, problem: Problem) -> dict[str, object]:
    catalog = layout.catalog
    item: dict[str, object] = {
        "status": "unknown",
        "next_step": None,
        "path": str(catalog),
        "state": None,
        "exists": _is_directory(catalog),
        "branch": None,
        "head": None,
        "locked": None,
        "registered_path": None,
        "registration_matches": None,
    }
    if observation is None:
        return item
    registered = observation.registered
    item.update(
        state=observation.state,
        branch=registered.branch if registered is not None else None,
        head=registered.head if registered is not None else None,
        locked=observation.locked,
        registered_path=str(registered.path) if registered is not None else None,
        registration_matches=registered is not None and _same_entry(registered.path, catalog),
    )
    state = observation.state
    if state == "ready" and observation.locked:
        item["status"] = "ok"
        return item
    item["status"] = "problem"
    if state == "foreign":
        item["next_step"] = problem(
            "catalog",
            CANONICAL_FOREIGN_CHECKOUT,
            f"this checkout looks mounted; {observation.detail}",
            FOREIGN_CHECKOUT_RECOVERY,
        )
    elif state in ("occupied", "elsewhere"):
        message = observation.detail or f"{catalog} is occupied"
        if state == "elsewhere":
            registered_path = registered.path if registered is not None else None
            step = elsewhere_next_step(registered_path, exists=bool(observation.registered_exists))
        else:
            step = occupied_next_step(observation)
        item["next_step"] = problem("catalog", CANONICAL_PATH_OCCUPIED, message, step, path=str(catalog))
    else:
        reasons = {
            "ready": "the catalog is not locked",
            "repair": "the catalog's Git registration does not match its place (was the main checkout moved?)",
            "readd": "the catalog directory is missing but still registered (for example after git clean -ffdx)",
            "absent": "this clone has no catalog yet",
        }
        item["next_step"] = problem("catalog", CANONICAL_NOT_LINKED, reasons[state], CANONICAL_NOT_LINKED_RECOVERY)
    return item


def _is_directory(path: Path) -> bool:
    """pathlib raises PermissionError for EACCES; a status report treats an unreadable path as not there."""
    try:
        return stat.S_ISDIR(path.stat().st_mode)
    except OSError:
        return False


def _same_entry(left: Path, right: Path) -> bool:
    try:
        return left.samefile(right)
    except OSError:
        return False


def _link_item(observation: CatalogObservation | None, problem: Problem, *, main_migrated: bool) -> dict[str, object]:
    if observation is None:
        return {"status": "unknown", "next_step": None, "links": []}
    links = [
        {
            "checkout": str(view.checkout),
            "path": str(view.observed.path),
            "expected": view.expected,
            "actual": view.observed.text,
            "state": view.state,
            "entries": view.observed.entries,
        }
        for view in observation.links
    ]
    item: dict[str, object] = {"status": "ok", "next_step": None, "links": links}
    for view in observation.links:
        if view.state == "correct":
            continue
        item["status"] = "problem"
        path = view.observed.path
        if not main_migrated and view.checkout == observation.layout.main_checkout:
            next_step = problem(
                "link",
                CANONICAL_MAIN_NOT_MIGRATED,
                main_not_migrated_message(path),
                MAIN_NOT_MIGRATED_NEXT_STEP,
                path=str(path),
            )
        elif view.state == "occupied":
            step = link_occupied_next_step(path)
            next_step = problem(
                "link",
                CANONICAL_LINK_OCCUPIED,
                f"{path} is a real {view.observed.kind}, not a link",
                step,
                path=str(path),
            )
        else:
            next_step = problem(
                "link",
                CANONICAL_NOT_LINKED,
                f"{path} is {view.state.replace('_', ' ')}",
                CANONICAL_NOT_LINKED_RECOVERY,
                path=str(path),
            )
        item["next_step"] = item["next_step"] or next_step
    return item


def _exclude_item(layout: CatalogLayout, observation: CatalogObservation | None, problem: Problem) -> dict[str, object]:
    exclude_path = layout.common_dir / "info/exclude"
    gitignore_path = layout.checkout / GITIGNORE_PATH
    if observation is None:
        return {
            "status": "unknown",
            "next_step": None,
            "info_exclude": {"path": str(exclude_path), "missing": None},
            "gitignore": {"path": str(gitignore_path), "missing": None},
        }
    item: dict[str, object] = {
        "status": "ok",
        "next_step": None,
        "info_exclude": {"path": str(exclude_path), "missing": list(observation.exclude_missing)},
        "gitignore": {"path": str(gitignore_path), "missing": list(observation.gitignore_missing)},
    }
    if observation.exclude_missing:
        item["status"] = "problem"
        item["next_step"] = problem(
            "exclude",
            CANONICAL_IGNORE_RULES_MISSING,
            f"{exclude_path} lacks {', '.join(observation.exclude_missing)}",
            CANONICAL_NOT_LINKED_RECOVERY,
        )
    if observation.gitignore_missing:
        item["status"] = "problem"
        step = problem(
            "exclude",
            CANONICAL_IGNORE_RULES_MISSING,
            f"{gitignore_path} lacks {', '.join(observation.gitignore_missing)}",
            gitignore_next_step(layout),
        )
        item["next_step"] = item["next_step"] or step
    return item


def _access_item(
    layout: CatalogLayout, observation: CatalogObservation | None, problem: Problem, *, sandboxed: bool
) -> dict[str, object]:
    catalog = layout.catalog
    if observation is None or observation.state not in ("ready", "repair") or not _is_directory(catalog):
        return {"status": "unknown", "next_step": None, "readable": None, "writable": None}
    readable = os.access(catalog, os.R_OK | os.X_OK)
    writable = os.access(catalog, os.W_OK)
    item: dict[str, object] = {"status": "ok", "next_step": None, "readable": readable, "writable": writable}
    # In a Codex sandbox of a linked worktree the tools item reports the exact setting line instead.
    if not readable or (not writable and not sandboxed):
        item["status"] = "problem"
        item["next_step"] = problem(
            "access",
            OS_ACCESS_DENIED,
            f"this process cannot {'read' if not readable else 'write'} {catalog}",
            f"Check the permissions of {catalog}.",
        )
    elif not writable:
        item["status"] = "problem"
        item["next_step"] = problem(
            "access",
            OS_ACCESS_DENIED,
            f"this sandbox cannot write {catalog}",
            "Add the one setting line shown by the tools item (data.tools.codex.line) to the Codex configuration.",
        )
    return item


def _format_item(layout: CatalogLayout, observation: CatalogObservation | None, problem: Problem) -> dict[str, object]:
    if observation is None or observation.state not in ("ready", "repair"):
        return {
            "status": "unknown",
            "next_step": None,
            "version": None,
            "supported_max": CANONICAL_FORMAT,
            "writable": None,
        }
    try:
        version = read_format((layout.catalog / FORMAT_FILE).read_bytes())
    except OSError:
        version = None
    writable = format_writable(version)
    step = FORMAT_MISSING_RECOVERY if version is None else FORMAT_UNSUPPORTED_RECOVERY
    item: dict[str, object] = {
        "status": "ok" if writable else "problem",
        "next_step": None,
        "version": version,
        "supported_max": CANONICAL_FORMAT,
        "writable": writable,
    }
    if not writable:
        item["next_step"] = problem(
            "format",
            CANONICAL_FORMAT_UNSUPPORTED,
            f"the catalog declares canonical format {version!r}",
            step,
        )
    return item


def _changes_item(
    layout: CatalogLayout, observation: CatalogObservation | None, *, timeout: float
) -> dict[str, object]:
    item: dict[str, object] = {
        "status": "unknown",
        "next_step": None,
        "unsaved": None,
        "conflict_files": [],
        "unpushed": None,
        "oldest_unpushed_at": None,
        "holds": [],
        "blocking": [],
    }
    if observation is None or observation.state != "ready":
        return item
    catalog = Path(os.path.realpath(layout.catalog))
    try:
        summary = canonical_git.catalog_change_summary(catalog, timeout=timeout)
        unpushed = canonical_git.unpushed(catalog, timeout=timeout)
    except GitProcessError:
        return item
    item.update(
        status="ok",
        unsaved=summary.unsaved,
        conflict_files=list(summary.conflict_files),
        unpushed=unpushed[0] if unpushed is not None else None,
        oldest_unpushed_at=unpushed[1] if unpushed is not None else None,
    )
    if summary.conflict_files:
        item.update(status="problem", next_step=_CONFLICT_NEXT_STEP)
    return item
