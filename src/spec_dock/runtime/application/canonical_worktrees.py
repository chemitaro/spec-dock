"""Canonical-mode worktree commands: today's native Git steps plus the catalog's place among the worktrees.

`worktree create` links the new worktree (R-B4, iss-00429). `--expect-current` is checked against the
structure snapshot (iss-00431). The clone's catalog worktree is shown as such and never removed or
bootstrapped here (`canonical remove` detaches it). `workbench copy` has nothing to copy: every worktree sees the
same catalog.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING

from spec_dock.runtime.application.canonical_errors import (
    CANONICAL_CATALOG_PROTECTED,
    CANONICAL_WORKBENCH_SHARED,
    CATALOG_PROTECTED_RECOVERY,
    WORKBENCH_SHARED_RECOVERY,
    CanonicalCommandError,
)
from spec_dock.runtime.application.canonical_link import link_after_command
from spec_dock.runtime.application.canonical_scope_read import replace_namespace
from spec_dock.runtime.application.canonical_scopes import check_canonical_expectation
from spec_dock.runtime.application.direct_bootstrap import bootstrap_native_worktree
from spec_dock.runtime.application.direct_worktrees import (
    create_native_worktree,
    list_native_worktrees,
    remove_native_worktree,
    resolve_native_target,
    show_native_worktree,
)
from spec_dock.runtime.domain.canonical_content import FORMAT_FILE
from spec_dock.runtime.domain.canonical_layout import CANONICAL_BRANCH
from spec_dock.runtime.presentation.command_data import FamilyData

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.contracts import GitWorktreeRecord
    from spec_dock.runtime.application.project_context import GitContext, ProjectContext
    from spec_dock.runtime.presentation.envelope import OperationResult


def is_catalog(entry: GitWorktreeRecord) -> bool:
    """The same test as the legacy observation exception (iss-00429 D1)."""
    return entry.branch == CANONICAL_BRANCH and (entry.path / FORMAT_FILE).is_file()


def create_worktree_and_link(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    check_canonical_expectation(context, namespace)
    result = create_native_worktree(replace_namespace(namespace, expect_current=None), context)
    if result.status not in ("succeeded", "planned") or not isinstance(result.data, FamilyData):
        return result
    created = Path(str(result.data.result["path"]))
    follow = link_after_command(created, timeout=namespace.timeout, dry_run=namespace.dry_run)
    data = FamilyData(result.data.kind, {**result.data.result, "canonical_link": follow.link})
    return replace(
        result, data=data, effects=(*result.effects, *follow.effects), warnings=(*result.warnings, *follow.warnings)
    )


def list_worktrees(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    check_canonical_expectation(context, namespace)
    result = list_native_worktrees(replace_namespace(namespace, expect_current=None), context)
    if not isinstance(result.data, FamilyData):
        return result
    items = tuple(
        {**item, "catalog": item["branch"] == CANONICAL_BRANCH and (Path(str(item["path"])) / FORMAT_FILE).is_file()}
        for item in result.data.result["items"]  # type: ignore[attr-defined]
    )
    return replace(result, data=FamilyData(result.data.kind, {**result.data.result, "items": items}))


def show_worktree(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    check_canonical_expectation(context, namespace)
    result = show_native_worktree(replace_namespace(namespace, expect_current=None), context)
    if not isinstance(result.data, FamilyData):
        return result
    entry = resolve_native_target(namespace.worktree_ref, context, timeout=namespace.timeout)
    return replace(result, data=FamilyData(result.data.kind, {**result.data.result, "catalog": is_catalog(entry)}))


def remove_worktree(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    _refuse_catalog(namespace, context)
    check_canonical_expectation(context, namespace)
    return remove_native_worktree(replace_namespace(namespace, expect_current=None), context)


def bootstrap_worktree(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    _refuse_catalog(namespace, context)
    check_canonical_expectation(context, namespace)
    return bootstrap_native_worktree(replace_namespace(namespace, expect_current=None), context)


def refuse_workbench_copy(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    del namespace, context
    raise CanonicalCommandError(
        CANONICAL_WORKBENCH_SHARED,
        "every worktree of this clone reads the same catalog, so each Scope's .workbench is already shared",
        recovery=(WORKBENCH_SHARED_RECOVERY,),
        details={"next_step": WORKBENCH_SHARED_RECOVERY},
    )


def install_with_expectation(namespace: argparse.Namespace, target: GitContext) -> OperationResult[object]:
    """Schema-4 `installation show/update/uninstall --expect-current`: check the snapshot, then install as today."""
    from spec_dock.runtime.application.direct_installation import install_static_assets
    from spec_dock.runtime.application.project_context import resolve_context

    project = resolve_context(str(target.root), target.root, timeout=namespace.timeout)
    check_canonical_expectation(project, namespace)
    return install_static_assets(replace_namespace(namespace, expect_current=None), target)


def _refuse_catalog(namespace: argparse.Namespace, context: ProjectContext) -> None:
    entry = resolve_native_target(namespace.worktree_ref, context, timeout=namespace.timeout)
    if is_catalog(entry):
        raise CanonicalCommandError(
            CANONICAL_CATALOG_PROTECTED,
            f"{entry.path} is this clone's spec catalog; worktree commands do not remove or bootstrap it",
            recovery=(CATALOG_PROTECTED_RECOVERY,),
            details={"path": str(entry.path), "next_step": CATALOG_PROTECTED_RECOVERY},
        )
