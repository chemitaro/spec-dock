"""`spec-dock todo settings`: the effective values and where each comes from (epic-00547 D-10; iss-00549 D-06).

It always answers on the repository-independent path. Inside a schema-4 checkout the repository layer is read
after the link check (F-03); outside any checkout that layer is `not_applicable`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from spec_dock.runtime.application.todo_common import command_error, open_repository, settings_warnings
from spec_dock.runtime.domain.todo_record import TodoError
from spec_dock.runtime.domain.todo_settings import Layer, resolve
from spec_dock.runtime.infra.user_config import read_user_todo_settings
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import OperationResult

if TYPE_CHECKING:
    import argparse
    from pathlib import Path


def show_settings(namespace: argparse.Namespace, cwd: Path) -> OperationResult[object]:
    from spec_dock.runtime.application.project_context import WorkspaceNotMigrated, resolve_context
    from spec_dock.runtime.infra.git_process import GitProcessError

    try:
        context = resolve_context(namespace.project, cwd, timeout=namespace.timeout)
    except WorkspaceNotMigrated:
        raise
    except (ValueError, OSError, GitProcessError):  # not a Git worktree or no workspace declaration
        context = None
    try:
        if context is None:
            effective = resolve((read_user_todo_settings(), Layer("repository", None, "not_applicable", None, {})))
        else:
            effective = open_repository(context, namespace).settings
    except TodoError as error:
        raise command_error(error) from error
    return OperationResult(
        namespace.command_path,
        "succeeded",
        FamilyData("todo", effective.to_json()),
        0,
        warnings=settings_warnings(effective.layers),
    )
