"""Normal package command dispatch, with no common control or operation journal."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.application.scope_query import list_scopes, load_scope_views
from spec_dock.runtime.application.worktree_observation import read_selection, resolve_scope
from spec_dock.runtime.infra.git_process import GitProcessError
from spec_dock.runtime.presentation.envelope import Diagnostic, OperationResult, render_json_v2, render_text

if TYPE_CHECKING:
    import argparse
    from pathlib import Path

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.scope_query import ScopeView


@dataclass(frozen=True)
class FamilyData:
    kind: str
    result: dict[str, object]


@dataclass(frozen=True)
class DiagnosticData:
    findings: tuple[Diagnostic, ...] = ()
    unverified: tuple[str, ...] = ()
    kind: str = "diagnostic"


@dataclass(frozen=True)
class ActiveData:
    selection: dict[str, object]
    ancestors: tuple[str, ...]
    kind: str = "active"


def dispatch(namespace: argparse.Namespace, cwd: Path) -> tuple[int, str, str]:
    command = namespace.command_path
    result: OperationResult[object]
    try:
        context = resolve_context(namespace.project, cwd, timeout=namespace.timeout)
        if command == "work start":
            from spec_dock.runtime.application.work_start import start_work

            result = start_work(namespace, context)
        elif command == "active show":
            observation = read_selection(context, load_scope_views(context.root / "spec-dock"))
            result = OperationResult(command, "succeeded", ActiveData(observation.view(), observation.ancestors), 0)
        elif command == "scope show":
            scope = resolve_scope(context, load_scope_views(context.root / "spec-dock"), namespace.target)
            result = OperationResult(
                command,
                "succeeded",
                FamilyData(
                    "scope",
                    {
                        "scope": scope_payload(scope, context),
                        "github_ref": scope.github_ref,
                        "changed": False,
                    },
                ),
                0,
            )
        elif command == "scope list":
            views = load_scope_views(context.root / "spec-dock")
            parent = resolve_scope(context, views, namespace.parent).id if namespace.parent else None
            listed = list_scopes(views, kind=namespace.kind, parent_id=parent, state=namespace.state)
            unknown_filtered = sum(
                view.status.state == "unknown" and namespace.state not in (None, "unknown")
                for view in views
                if (namespace.kind is None or view.kind == namespace.kind)
                and (parent is None or view.parent_id == parent)
            )
            result = OperationResult(
                command,
                "succeeded",
                FamilyData(
                    "scope-list",
                    {
                        "items": [scope_payload(scope, context) for scope in listed.items],
                        "unknown_filtered_count": unknown_filtered,
                    },
                ),
                0,
            )
        else:
            result = failure(command, "BUSINESS_NOT_CONNECTED", "business command is not connected yet", 3)
    except GitProcessError as error:
        result = OperationResult(
            command, "failed", DiagnosticData(), 5, error=Diagnostic("GIT_FAILED", str(error), error.details())
        )
    except FileNotFoundError as error:
        result = failure(command, "LOCAL_TARGET_NOT_FOUND", str(error), 4)
    except LookupError as error:
        result = failure(command, "SCOPE_NOT_FOUND", str(error), 4)
    except ValueError as error:
        result = failure(command, "PRECONDITION_FAILED", str(error), 3)
    except (OSError, RuntimeError) as error:
        result = failure(command, "LOCAL_IO_FAILED", str(error), 5)
    if namespace.json:
        return result.exit_code, render_json_v2(result), ""
    stdout, stderr = render_text(result, native_git=True)
    return result.exit_code, stdout, stderr


def scope_payload(scope: ScopeView, context: ProjectContext) -> dict[str, object]:
    return {
        "id": scope.id,
        "kind": scope.kind,
        "title": scope.title,
        "parent_id": scope.parent_id,
        "backend": scope.backend.kind,
        "github_ref": scope.github_ref,
        "path": str(scope.path.relative_to(context.root)),
        "revision": scope.revision,
        "status": {
            "state": scope.status.state,
            "authority": scope.status.authority,
            "source": scope.status.source,
            "observed_at": scope.status.observed_at,
        },
    }


def failure(command: str, code: str, message: str, exit_code: int) -> OperationResult[DiagnosticData]:
    return OperationResult(command, "failed", DiagnosticData(), exit_code, error=Diagnostic(code, message, {}))
