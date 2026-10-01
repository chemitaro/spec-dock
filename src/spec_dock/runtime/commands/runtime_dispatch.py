"""Normal package command dispatch, with no common control or operation journal."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.application.scope_expectations import check_scope_expectations
from spec_dock.runtime.application.scope_query import list_scopes, load_scope_views
from spec_dock.runtime.application.worktree_observation import read_selection, resolve_scope
from spec_dock.runtime.cli.catalog import MUTATING_LEAF_PATHS
from spec_dock.runtime.infra.git_process import GitProcessError
from spec_dock.runtime.presentation.command_data import ActiveData, DiagnosticData, FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, OperationResult, render_json_v2, render_text

if TYPE_CHECKING:
    import argparse
    from pathlib import Path

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.scope_query import ScopeView


def dispatch(namespace: argparse.Namespace, cwd: Path) -> tuple[int, str, str]:
    command = namespace.command_path
    result: OperationResult[object]
    try:
        context = resolve_context(namespace.project, cwd, timeout=namespace.timeout)
        if command == "work start":
            from spec_dock.runtime.application.work_start import start_work

            result = start_work(namespace, context)
        elif command == "work finish":
            from spec_dock.runtime.application.direct_finish import finish_work

            result = finish_work(namespace, context)
        elif command == "workspace sync":
            from spec_dock.runtime.application.direct_sync import sync_workspace

            result = sync_workspace(namespace, context)
        elif command.startswith("scope create "):
            from spec_dock.runtime.application.direct_scope_publish import create_scope

            result = create_scope(namespace, context)
        elif command.startswith("scope import github "):
            from spec_dock.runtime.application.direct_scope_publish import import_scope

            result = import_scope(namespace, context)
        elif command in ("scope close", "scope reopen"):
            from spec_dock.runtime.application.direct_scope_lifecycle import lifecycle_scope

            result = lifecycle_scope(namespace, context)
        elif command == "scope edit":
            from spec_dock.runtime.application.direct_scope_edit import edit_scope

            result = edit_scope(namespace, context)
        elif command == "scope delete":
            from spec_dock.runtime.application.direct_scope_delete import delete_scope

            result = delete_scope(namespace, context)
        elif command in ("artifact list", "artifact show"):
            from spec_dock.runtime.application.direct_artifact import query_artifact

            result = query_artifact(namespace, context)
        elif command in ("artifact create", "artifact import file"):
            from spec_dock.runtime.application.direct_artifact import mutate_artifact

            result = mutate_artifact(namespace, context, cwd)
        elif command == "worktree create":
            from spec_dock.runtime.application.direct_worktrees import create_native_worktree

            result = create_native_worktree(namespace, context)
        elif command == "worktree list":
            from spec_dock.runtime.application.direct_worktrees import list_native_worktrees

            result = list_native_worktrees(namespace, context)
        elif command == "worktree show":
            from spec_dock.runtime.application.direct_worktrees import show_native_worktree

            result = show_native_worktree(namespace, context)
        elif command == "worktree remove":
            from spec_dock.runtime.application.direct_worktrees import remove_native_worktree

            result = remove_native_worktree(namespace, context)
        elif command == "workbench copy":
            from spec_dock.runtime.application.direct_workbench import copy_workbench

            result = copy_workbench(namespace, context)
        elif command in ("dependency list", "dependency check"):
            from spec_dock.runtime.application.direct_dependencies import query_dependencies

            result = query_dependencies(namespace, context)
        elif command in ("dependency add", "dependency remove"):
            from spec_dock.runtime.application.direct_dependencies import mutate_dependencies

            result = mutate_dependencies(namespace, context)
        elif command in ("branch show", "branch create", "branch switch"):
            from spec_dock.runtime.application.branch_operations import branch_operation

            result = branch_operation(namespace, context)
        elif command == "active show":
            views = load_scope_views(context.root / "spec-dock")
            observation = read_selection(context, views)
            check_scope_expectations(
                context,
                views,
                observation,
                target=None,
                expected_current=namespace.expect_current,
                expected_backend=namespace.expect_backend,
            )
            result = OperationResult(command, "succeeded", ActiveData(observation.view(), observation.ancestors), 0)
        elif command == "active set":
            from spec_dock.runtime.application.direct_active import set_direct

            result = set_direct(namespace, context)
        elif command == "active clear":
            from spec_dock.runtime.application.direct_active import clear_direct

            result = clear_direct(namespace, context)
        elif command == "scope show":
            views = load_scope_views(context.root / "spec-dock")
            selection = read_selection(context, views)
            scope = resolve_scope(context, views, namespace.target, selection=selection)
            check_scope_expectations(
                context,
                views,
                selection,
                target=scope,
                expected_current=namespace.expect_current,
                expected_backend=namespace.expect_backend,
            )
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
            selection = read_selection(context, views)
            check_scope_expectations(
                context,
                views,
                selection,
                target=None,
                expected_current=namespace.expect_current,
                expected_backend=namespace.expect_backend,
            )
            parent = (
                resolve_scope(context, views, namespace.parent, selection=selection).id if namespace.parent else None
            )
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
    if namespace.dry_run and command not in MUTATING_LEAF_PATHS:
        if isinstance(result.data, FamilyData):
            result = replace(
                result,
                data=FamilyData(
                    result.data.kind,
                    {
                        **result.data.result,
                        "can_apply": result.exit_code == 0,
                        "blockers": result.data.result.get("blockers", (result.error,) if result.error else ()),
                    },
                ),
            )
        if result.exit_code == 0:
            result = replace(result, status="planned")
    if namespace.json:
        return result.exit_code, render_json_v2(result), ""
    stdout, stderr = render_text(result, native_git=True, dependency_view=getattr(namespace, "view", None))
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
