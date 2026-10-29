"""Canonical-mode worktree commands: today's native Git steps plus the catalog's place among the worktrees.

`worktree create` links the new worktree (R-B4, iss-00429). `--expect-current` is checked against the
structure snapshot (iss-00431). `worktree remove` and `worktree bootstrap` run the legacy step on the very record
the expectation was checked on; `worktree create` and `installation` read the record again just before the legacy
step, which captures it once more (a narrow window remains there, iss-00432). The clone's catalog worktree is
shown as such and never removed or bootstrapped here (`canonical remove` detaches it). A worktree whose only
ignored entry is its correct catalog link is removed without --discard-ignored: the link is SpecDock's own and
removing it never touches the catalog. `workbench copy` has nothing to copy: every worktree sees the same catalog.
"""

from __future__ import annotations

from dataclasses import replace
import os
from pathlib import Path
from typing import TYPE_CHECKING

from spec_dock.runtime.application.canonical_catalog import resolve_layout
from spec_dock.runtime.application.canonical_errors import (
    CANONICAL_CATALOG_PROTECTED,
    CANONICAL_WORKBENCH_SHARED,
    CATALOG_PROTECTED_RECOVERY,
    WORKBENCH_SHARED_RECOVERY,
    CanonicalCommandError,
)
from spec_dock.runtime.application.canonical_link import link_after_command
from spec_dock.runtime.application.canonical_scope_read import replace_namespace
from spec_dock.runtime.application.canonical_scopes import check_canonical_expectation, load_canonical_scopes
from spec_dock.runtime.application.direct_bootstrap import _bootstrap_captured_target
from spec_dock.runtime.application.direct_worktrees import (
    _remove_captured_worktree,
    create_native_worktree,
    list_native_worktrees,
    resolve_native_target,
    show_native_worktree,
)
from spec_dock.runtime.domain.canonical_content import FORMAT_FILE
from spec_dock.runtime.domain.canonical_layout import CANONICAL_BRANCH, LINK_RELATIVE, link_state
from spec_dock.runtime.infra.canonical_files import observe_link
from spec_dock.runtime.infra.git_process import GitProcessError, run_git
from spec_dock.runtime.infra.github_structure import GithubStructureError
from spec_dock.runtime.infra.identity import DirectoryIdentity
from spec_dock.runtime.infra.work_target_store import WorkTargetStore
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, RecoveryInstructions

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.contracts import GitWorktreeRecord
    from spec_dock.runtime.application.project_context import GitContext, ProjectContext
    from spec_dock.runtime.infra.work_target_store import StoredSelection
    from spec_dock.runtime.presentation.envelope import OperationResult


def is_catalog(entry: GitWorktreeRecord) -> bool:
    """The same test as the legacy observation exception (iss-00429 D1)."""
    return catalog_at(entry.path, entry.branch)


def catalog_at(path: Path, branch: object) -> bool:
    return branch == CANONICAL_BRANCH and (path / FORMAT_FILE).is_file()


def create_worktree_and_link(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    checked = _captured_selection(namespace, context)
    check_canonical_expectation(context, namespace, stored=checked, refuse_kind_changed=True)
    _require_unchanged_selection(context, checked)
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
    kind_changes = _reading_warnings(context, namespace)
    result = list_native_worktrees(replace_namespace(namespace, expect_current=None), context)
    if not isinstance(result.data, FamilyData):
        return result
    items = tuple(
        {**item, "catalog": catalog_at(Path(str(item["path"])), item["branch"])}
        for item in result.data.result["items"]  # type: ignore[attr-defined]
    )
    data = FamilyData(result.data.kind, {**result.data.result, "items": items})
    return replace(result, data=data, warnings=(*result.warnings, *kind_changes))


def show_worktree(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    kind_changes = _reading_warnings(context, namespace)
    result = show_native_worktree(replace_namespace(namespace, expect_current=None), context)
    if not isinstance(result.data, FamilyData):
        return result
    shown = result.data.result
    catalog = catalog_at(Path(str(shown["path"])), shown["branch"])
    data = FamilyData(result.data.kind, {**shown, "catalog": catalog})
    return replace(result, data=data, warnings=(*result.warnings, *kind_changes))


def remove_worktree(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    """The legacy `remove_native_worktree` with the canonical expectation on the record its inner step verifies."""
    _refuse_catalog(namespace, context)
    context.require_writer()
    if namespace.expect_backend is not None:
        raise ValueError("--expect-backend requires one existing Scope target")
    captured = _capture_source_selection(context, "a Git mutation")
    check_canonical_expectation(context, namespace, stored=captured)
    if not namespace.yes and not namespace.dry_run:
        raise ValueError("worktree removal requires --yes")
    entry = resolve_native_target(namespace.worktree_ref, context, timeout=namespace.timeout)
    legacy = replace_namespace(namespace, expect_current=None)
    if not namespace.discard_ignored and _only_ignored_is_the_link(context, entry.path, timeout=namespace.timeout):
        legacy = replace_namespace(legacy, discard_ignored=True)
    result: OperationResult[object] | None = None
    try:
        with DirectoryIdentity(entry.path) as held_target:
            result = _remove_captured_worktree(legacy, context, entry, captured, held_target)
    except OSError as error:
        if result is None:
            raise
        return _cleanup_failure(
            result,
            error,
            "cleanup_error",
            "LOCAL_IO_FAILED",
            ("Inspect native inventory and the target path before a new explicit operation.",),
        )
    return result


def bootstrap_worktree(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    """The legacy `bootstrap_native_worktree` with the canonical expectation on the record its inner step uses."""
    _refuse_catalog(namespace, context)
    context.require_writer()
    if namespace.expect_backend is not None:
        raise ValueError("--expect-backend requires one existing Scope target")
    if not namespace.yes and not namespace.dry_run:
        raise ValueError("worktree bootstrap requires --yes")
    if namespace.offline and not namespace.dry_run:
        raise ValueError("worktree bootstrap cannot guarantee offline project hooks")
    captured = _capture_source_selection(context, "bootstrap")
    check_canonical_expectation(context, namespace, stored=captured)
    entry = resolve_native_target(namespace.worktree_ref, context, timeout=namespace.timeout)
    if entry.bare or entry.head is None:
        raise ValueError("bootstrap requires a non-bare worktree with a HEAD")
    legacy = replace_namespace(namespace, expect_current=None)
    result: OperationResult[object] | None = None
    try:
        with DirectoryIdentity(entry.path) as held_target:
            result = _bootstrap_captured_target(legacy, context, entry, captured, held_target)
            held_target.verify()
    except (OSError, ValueError) as error:
        if result is None:
            raise
        return _cleanup_failure(
            result,
            error,
            "post_hook_error",
            "BOOTSTRAP_CONTEXT_FAILED",
            ("Inspect project-owned hook effects before another explicit bootstrap.",),
            exit_code=3 if isinstance(error, ValueError) else 5,
        )
    return result


def _capture_source_selection(context: ProjectContext, purpose: str) -> StoredSelection:
    with WorkTargetStore(context.root) as store:
        captured = store.read()
    if captured.status not in ("empty", "selected"):
        raise ValueError(f"source direct selection cannot be captured for {purpose}")
    if captured.record is not None and (captured.record.clone_identity, captured.record.worktree_identity) != (
        context.clone_identity,
        context.worktree_identity,
    ):
        raise ValueError("source direct selection physical identity mismatch")
    return captured


def _cleanup_failure(
    result: OperationResult[object],
    error: Exception,
    key: str,
    code: str,
    recovery: tuple[str, ...],
    *,
    exit_code: int = 5,
) -> OperationResult[object]:
    """The legacy wrappers' handling of a failure while leaving the held target (copied, legacy unchanged)."""
    partial = any(effect.status in ("succeeded", "unknown") for effect in result.effects)
    diagnostic = (
        Diagnostic(result.error.code, result.error.message, {**result.error.details, key: str(error)})
        if result.error is not None
        else Diagnostic(code, str(error), {})
    )
    return replace(
        result,
        status="partial" if partial else "failed",
        exit_code=6 if partial else exit_code,
        effects=tuple(
            replace(effect, status="not_attempted") if effect.status == "planned" else effect
            for effect in result.effects
        ),
        error=diagnostic,
        recovery=RecoveryInstructions(recovery) if partial else None,
    )


def _only_ignored_is_the_link(context: ProjectContext, path: Path, *, timeout: float) -> bool:
    """True when the worktree's ignored content is exactly its correct spec-dock/initiatives link."""
    ignored = run_git(
        path, "ls-files", "--others", "--ignored", "--exclude-standard", "--directory", "-z", timeout=timeout
    )
    if [item for item in ignored.split(b"\0") if item] != [os.fsencode(LINK_RELATIVE.as_posix())]:
        return False
    try:
        layout = resolve_layout(context)
    except (OSError, ValueError, RuntimeError):
        return False
    observed = observe_link(path / LINK_RELATIVE)
    catalog = Path(os.path.realpath(layout.catalog))
    return link_state(observed, expected_text=layout.link_text(path), catalog=catalog) == "correct"


def _reading_warnings(context: ProjectContext, namespace: argparse.Namespace) -> tuple[Diagnostic, ...]:
    """Kind-change warnings for `worktree list/show` (Epic design ch. 2).

    --expect-current is checked as before. Without it the warnings are best effort: these commands need neither
    GitHub nor the catalog, so a structure or catalog that cannot be read adds no warning and changes nothing.
    """
    if namespace.expect_current is not None:
        return check_canonical_expectation(context, namespace)
    try:
        scopes = load_canonical_scopes(
            context, timeout=namespace.timeout, link=False, offline=bool(getattr(namespace, "offline", False))
        )
    except (CanonicalCommandError, GithubStructureError, GitProcessError, ValueError, OSError):
        return ()
    return scopes.kind_change_warnings()


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
    checked = _captured_selection(namespace, project)
    check_canonical_expectation(project, namespace, stored=checked)
    _require_unchanged_selection(project, checked)
    return install_static_assets(replace_namespace(namespace, expect_current=None), target)


def _captured_selection(namespace: argparse.Namespace, context: ProjectContext) -> StoredSelection | None:
    """The record the expectation is checked on (None without --expect-current)."""
    if namespace.expect_current is None:
        return None
    with WorkTargetStore(context.root) as store:
        return store.read()


def _require_unchanged_selection(context: ProjectContext, checked: StoredSelection | None) -> None:
    """Read the record again just before a legacy step that captures it itself (create, installation).

    The legacy step's own capture follows this check, so a change in between is not seen: a narrow window that
    remove and bootstrap do not have (they hand the checked record to the legacy inner step).
    """
    if checked is None:
        return
    with WorkTargetStore(context.root) as store:
        current = store.read()
    if (current.record, current.handle) != (checked.record, checked.handle):
        raise ValueError("direct selection changed after --expect-current was checked")


def _refuse_catalog(namespace: argparse.Namespace, context: ProjectContext) -> None:
    entry = resolve_native_target(namespace.worktree_ref, context, timeout=namespace.timeout)
    if is_catalog(entry):
        raise CanonicalCommandError(
            CANONICAL_CATALOG_PROTECTED,
            f"{entry.path} is this clone's spec catalog; worktree commands do not remove or bootstrap it",
            recovery=(CATALOG_PROTECTED_RECOVERY,),
            details={"path": str(entry.path), "next_step": CATALOG_PROTECTED_RECOVERY},
        )
