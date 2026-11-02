"""Execute an explicit native worktree's project init without receipts or shared locks."""

from __future__ import annotations

import stat
from typing import TYPE_CHECKING

from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.infra.file_publication import read_regular_file
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
    from spec_dock.runtime.infra.identity import DirectoryIdentity
    from spec_dock.runtime.infra.work_target_store import StoredSelection


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
