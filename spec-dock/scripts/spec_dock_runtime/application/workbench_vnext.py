"""Copy noncanonical Workbench payload between exact registered Scope snapshots."""

from __future__ import annotations

from dataclasses import dataclass
import fcntl
from typing import TYPE_CHECKING, Literal

from spec_dock_runtime.application.contracts import WorkbenchCopyError, WorkbenchFilesystemError
from spec_dock_runtime.application.scope_query import load_scope_views, show_scope
from spec_dock_runtime.application.worktree import _close_fd, _open_directory_no_follow, _verify_worktree_path_binding
from spec_dock_runtime.application.worktree_vnext import list_worktrees, show_worktree
from spec_dock_runtime.cli.admission import admit_writer
from spec_dock_runtime.infra import fs_cli
from spec_dock_runtime.infra.active_store import load_selection_v3
from spec_dock_runtime.infra.control_store import load_control
from spec_dock_runtime.infra.writer_lock import WriterLock

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class WorkbenchCopied:
    scope_id: str
    source_worktree_id: str
    target_worktree_id: str
    target_path: Path


def _guard_workbench_path(root: Path, scope_path: Path, *, allow_missing_workbench: bool) -> Path:
    specdock_dir = root / "spec-dock"
    fs_cli.guard_workbench_ancestry(root, specdock_dir)
    fs_cli.guard_workbench_inventory(specdock_dir)
    fs_cli.guard_workbench_ancestry(root, scope_path)
    workbench = scope_path / ".workbench"
    fs_cli.guard_workbench_ancestry(root, workbench, allow_missing_leaf=allow_missing_workbench)
    return workbench


def copy_workbench(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    scope: str,
    to_worktree: str,
    on_conflict: Literal["error", "overwrite"] = "error",
    lock_timeout: float = 0.0,
) -> WorkbenchCopied:
    """Preflight all conflicts and copy only one Scope's opaque Workbench tree."""
    if on_conflict not in ("error", "overwrite"):
        raise ValueError("Workbench conflict policy is invalid")
    with WriterLock(common_dir, timeout=lock_timeout):
        admit_writer(
            load_control(common_dir),
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
        )
        inventory = list_worktrees(repo_root=repo_root, common_dir=common_dir)
        source = next((item for item in inventory if item.id == worktree_id and item.registered), None)
        if source is None or source.path.resolve(strict=True) != repo_root.resolve(strict=True):
            raise WorkbenchCopyError(code="source_unavailable", message="current worktree is not registered")
        target = show_worktree(repo_root=repo_root, common_dir=common_dir, reference=to_worktree)
        if target.id is None or not target.registered or target.id == worktree_id or target.bare:
            raise WorkbenchCopyError(code="target_ineligible", message="destination worktree is not eligible")
        leases: list[int] = []
        try:
            for worktree in sorted((source, target), key=lambda item: item.id or ""):
                descriptor = _open_directory_no_follow(worktree.path)
                try:
                    fcntl.flock(
                        descriptor,
                        (fcntl.LOCK_SH if worktree.id == worktree_id else fcntl.LOCK_EX) | fcntl.LOCK_NB,
                    )
                    _verify_worktree_path_binding(worktree.path, descriptor)
                    leases.append(descriptor)
                except BaseException:
                    _close_fd(descriptor)
                    raise
            source_selection, _ = load_selection_v3(repo_root / "spec-dock", worktree_id=worktree_id)
            source_scope = show_scope(load_scope_views(repo_root / "spec-dock"), scope, selection=source_selection)
            target_scope = show_scope(load_scope_views(target.path / "spec-dock"), source_scope.id)
            if target_scope.id != source_scope.id or target_scope.kind != source_scope.kind:
                raise WorkbenchCopyError(code="scope_mismatch", message="Scope differs between worktrees")
            source_workbench = _guard_workbench_path(repo_root, source_scope.path, allow_missing_workbench=False)
            target_workbench = _guard_workbench_path(target.path, target_scope.path, allow_missing_workbench=True)
            if fs_cli.path_kind(source_workbench) != "directory":
                raise WorkbenchCopyError(code="no_source", message="source Workbench is not a directory")
            if fs_cli.path_kind(target_workbench) not in {"missing", "directory"}:
                raise WorkbenchCopyError(code="target_ineligible", message="destination Workbench root is invalid")
            try:
                fs_cli.copy_workbench(
                    source_workbench,
                    target_workbench,
                    on_conflict=on_conflict,
                    relative_symlinks_only=True,
                )
            except WorkbenchFilesystemError as error:
                raise WorkbenchCopyError(
                    code="copy_failed",
                    message="Workbench copy stopped at a conflict or unsafe path",
                    mutation_started=error.mutation_started,
                ) from error
            return WorkbenchCopied(source_scope.id, worktree_id, target.id, target_workbench)
        finally:
            for descriptor in reversed(leases):
                _close_fd(descriptor)
