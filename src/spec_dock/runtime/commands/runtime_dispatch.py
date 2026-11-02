"""Normal package command dispatch, with no common control or operation journal."""

from __future__ import annotations

from dataclasses import replace
import sys
from typing import TYPE_CHECKING

from spec_dock.runtime.cli.catalog import MUTATING_LEAF_PATHS
from spec_dock.runtime.presentation.command_data import DiagnosticData, FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, OperationResult, render_json_v2, render_text

if TYPE_CHECKING:
    import argparse
    from pathlib import Path


def dispatch(namespace: argparse.Namespace, cwd: Path) -> tuple[int, str, str]:
    command = namespace.command_path
    if sys.platform not in ("linux", "darwin"):
        return _render_result(
            namespace,
            failure(command, "UNSUPPORTED_PLATFORM", "business commands support Linux and macOS", 3),
        )
    from spec_dock.runtime.application.canonical_errors import (
        CanonicalCommandError,
        canonical_not_migrated,
        github_error_result,
    )
    from spec_dock.runtime.application.project_context import WorkspaceNotMigrated, require_migrated, resolve_context
    from spec_dock.runtime.commands.canonical_dispatch import dispatch_canonical, dispatch_repository_independent
    from spec_dock.runtime.infra.git_process import GitProcessError
    from spec_dock.runtime.infra.github_structure import GithubStructureError

    result: OperationResult[object]
    try:
        independent = dispatch_repository_independent(namespace, cwd)
        if independent is not None:
            return _render_result(namespace, independent)
        if command.startswith("installation "):
            from spec_dock.runtime.application.direct_installation import install_static_assets, installation_context

            target = installation_context(namespace, cwd)
            require_migrated(target.root)
            if namespace.expect_current is not None:
                from spec_dock.runtime.application.canonical_worktrees import install_with_expectation

                result = install_with_expectation(namespace, target)
            else:
                result = install_static_assets(namespace, target)
            return _render_result(namespace, result)
        if command == "workspace doctor" and namespace.raw:
            from spec_dock.runtime.application.project_context import declares_schema_4, resolve_git_context

            git = resolve_git_context(namespace.project, cwd, timeout=namespace.timeout)
            require_migrated(git.root)
            if not declares_schema_4(git.root):
                from spec_dock.runtime.application.direct_diagnostics import diagnose_raw_workspace

                return _render_result(namespace, diagnose_raw_workspace(namespace, git))
        try:
            context = resolve_context(namespace.project, cwd, timeout=namespace.timeout)
        except WorkspaceNotMigrated:
            raise
        except ValueError:
            from spec_dock.runtime.application.canonical_catalog import inside_catalog, inside_catalog_error

            # Only on this failure path: a catalog worktree has no declaration; name the next step.
            catalog = inside_catalog(namespace.project, cwd, timeout=namespace.timeout)
            if catalog is not None:
                raise inside_catalog_error(catalog) from None
            raise
        result = dispatch_canonical(namespace, context)
    except WorkspaceNotMigrated:
        result = canonical_not_migrated(command)
    except GitProcessError as error:
        result = OperationResult(
            command, "failed", DiagnosticData(), 5, error=Diagnostic("GIT_FAILED", str(error), error.details())
        )
    except CanonicalCommandError as error:
        result = error.result(command)
    except GithubStructureError as error:
        result = github_error_result(command, error)
    except FileNotFoundError as error:
        result = failure(command, "LOCAL_TARGET_NOT_FOUND", str(error), 4)
    except LookupError as error:
        result = failure(command, "SCOPE_NOT_FOUND", str(error), 4)
    except ValueError as error:
        result = failure(command, "PRECONDITION_FAILED", str(error), 3)
    except (OSError, RuntimeError) as error:
        result = failure(command, "LOCAL_IO_FAILED", str(error), 5)
    return _render_result(namespace, result)


def _render_result(namespace: argparse.Namespace, result: OperationResult[object]) -> tuple[int, str, str]:
    command = namespace.command_path
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


def failure(command: str, code: str, message: str, exit_code: int) -> OperationResult[DiagnosticData]:
    return OperationResult(command, "failed", DiagnosticData(), exit_code, error=Diagnostic(code, message, {}))
