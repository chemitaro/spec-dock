"""Execute an explicit native worktree's project init without receipts or shared locks."""

from __future__ import annotations

from dataclasses import replace
import stat
from typing import TYPE_CHECKING

from spec_dock.runtime.application.direct_worktrees import check_current_expectation, resolve_native_target
from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.infra.file_publication import read_regular_file
from spec_dock.runtime.infra.identity import DirectoryIdentity
from spec_dock.runtime.infra.project_hook import run_make_init
from spec_dock.runtime.infra.work_target_store import WorkTargetStore
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult, RecoveryInstructions

if TYPE_CHECKING:
    import argparse
    from pathlib import Path

    from spec_dock.runtime.application.contracts import GitWorktreeRecord
    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.infra.file_publication import FileSnapshot
    from spec_dock.runtime.infra.work_target_store import StoredSelection


def bootstrap_native_worktree(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    context.require_writer()
    if namespace.expect_backend is not None:
        raise ValueError("--expect-backend requires one existing Scope target")
    if not namespace.yes and not namespace.dry_run:
        raise ValueError("worktree bootstrap requires --yes")
    if namespace.offline and not namespace.dry_run:
        raise ValueError("worktree bootstrap cannot guarantee offline project hooks")
    with WorkTargetStore(context.root) as store:
        captured_selection = store.read()
    if captured_selection.status not in ("empty", "selected"):
        raise ValueError("source direct selection cannot be captured for bootstrap")
    if captured_selection.record is not None and (
        captured_selection.record.clone_identity,
        captured_selection.record.worktree_identity,
    ) != (context.clone_identity, context.worktree_identity):
        raise ValueError("source direct selection physical identity mismatch")
    check_current_expectation(namespace, context, stored=captured_selection)
    entry = resolve_native_target(namespace.worktree_ref, context, timeout=namespace.timeout)
    if entry.bare or entry.head is None:
        raise ValueError("bootstrap requires a non-bare worktree with a HEAD")
    result: OperationResult[object] | None = None
    try:
        with DirectoryIdentity(entry.path) as held_target:
            result = _bootstrap_captured_target(namespace, context, entry, captured_selection, held_target)
            held_target.verify()
    except (OSError, ValueError) as error:
        if result is None:
            raise
        partial = any(effect.status in ("succeeded", "unknown") for effect in result.effects)
        diagnostic = (
            Diagnostic(result.error.code, result.error.message, {**result.error.details, "post_hook_error": str(error)})
            if result.error is not None
            else Diagnostic("BOOTSTRAP_CONTEXT_FAILED", str(error), {})
        )
        return replace(
            result,
            status="partial" if partial else "failed",
            exit_code=6 if partial else 3 if isinstance(error, ValueError) else 5,
            effects=tuple(
                replace(effect, status="not_attempted") if effect.status == "planned" else effect
                for effect in result.effects
            ),
            error=diagnostic,
            recovery=RecoveryInstructions(("Inspect project-owned hook effects before another explicit bootstrap.",))
            if partial
            else None,
        )
    return result


def _capture_makefile(path: Path) -> tuple[Path, FileSnapshot]:
    for name in ("GNUmakefile", "makefile", "Makefile"):
        candidate = path / name
        try:
            observed = candidate.lstat()
        except FileNotFoundError:
            continue
        if not stat.S_ISREG(observed.st_mode) or observed.st_nlink != 1:
            raise ValueError("project init makefile must be a single-link regular file")
        return candidate, read_regular_file(candidate)
    raise ValueError("project-owned makefile is required for bootstrap")


def _bootstrap_captured_target(
    namespace: argparse.Namespace,
    context: ProjectContext,
    entry: GitWorktreeRecord,
    captured_selection: StoredSelection,
    held_target: DirectoryIdentity,
) -> OperationResult[object]:
    data: dict[str, object] = {
        "path": str(entry.path),
        "branch": entry.branch,
        "head": entry.head,
        "changed": False,
        "observed": {},
    }
    makefile = _capture_makefile(entry.path)
    fresh_source = resolve_context(str(context.root), context.root, timeout=namespace.timeout)
    fresh_source.require_writer()
    if (
        fresh_source.clone_identity,
        fresh_source.worktree_identity,
        fresh_source.branch,
        fresh_source.head,
        fresh_source.workspace,
    ) != (
        context.clone_identity,
        context.worktree_identity,
        context.branch,
        context.head,
        context.workspace,
    ):
        raise ValueError("source Git worktree context changed before bootstrap")
    with WorkTargetStore(context.root) as store:
        if store.read() != captured_selection:
            raise ValueError("source direct selection changed before bootstrap")
    if _capture_makefile(entry.path) != makefile:
        raise ValueError("project-owned makefile changed before bootstrap")
    held_target.verify()
    if namespace.dry_run:
        data.update(can_apply=True, blockers=())
        return OperationResult(
            namespace.command_path,
            "planned",
            FamilyData("worktree", data),
            0,
            effects=(Effect("worktree-bootstrap", "planned", str(entry.path)),),
        )
    outcome = run_make_init(entry.path, timeout=namespace.timeout)
    completed = outcome.started and outcome.returncode == 0 and not outcome.timed_out
    data.update(
        changed=completed,
        observed={
            "started": outcome.started,
            "returncode": outcome.returncode,
            "timed_out": outcome.timed_out,
            "diagnostic": outcome.diagnostic,
        },
    )
    effects = (
        Effect(
            "worktree-bootstrap",
            "succeeded" if completed else "unknown" if outcome.started else "failed",
            str(entry.path),
        ),
    )
    return OperationResult(
        namespace.command_path,
        "succeeded" if completed else "partial" if outcome.started else "failed",
        FamilyData("worktree", data),
        0 if completed else 6 if outcome.started else 5,
        effects=effects,
        error=None if completed else Diagnostic("BOOTSTRAP_FAILED", outcome.diagnostic, {}),
        recovery=RecoveryInstructions(("Inspect project-owned hook effects before another explicit bootstrap.",))
        if outcome.started and not completed
        else None,
    )
