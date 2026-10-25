"""Canonical-mode `worktree create`: today's native creation, then the same link steps (R-B4)."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING

from spec_dock.runtime.application.canonical_errors import canonical_not_implemented
from spec_dock.runtime.application.canonical_link import link_after_command
from spec_dock.runtime.application.direct_worktrees import create_native_worktree
from spec_dock.runtime.presentation.command_data import FamilyData

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.presentation.envelope import OperationResult


def create_worktree_and_link(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    if namespace.expect_current is not None:
        # The legacy expectation check reads .meta.json; canonical selection resolution belongs to iss-00431.
        return canonical_not_implemented(namespace.command_path)
    result = create_native_worktree(namespace, context)
    if result.status not in ("succeeded", "planned") or not isinstance(result.data, FamilyData):
        return result
    created = Path(str(result.data.result["path"]))
    follow = link_after_command(created, timeout=namespace.timeout, dry_run=namespace.dry_run)
    data = FamilyData(result.data.kind, {**result.data.result, "canonical_link": follow.link})
    return replace(
        result, data=data, effects=(*result.effects, *follow.effects), warnings=(*result.warnings, *follow.warnings)
    )
