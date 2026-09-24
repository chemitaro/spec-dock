"""Adapt the existing Artifact publishers to explicit vNext Scope selectors."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from spec_dock_runtime.application.artifact_query import ArtifactCatalogEntry, show_artifact
from spec_dock_runtime.application.contracts import CreateArtifactDocRequest, FileArtifactImportRequest
from spec_dock_runtime.application.scope_query import load_scope_views, show_scope
from spec_dock_runtime.cli.admission import admit_writer
from spec_dock_runtime.domain.selectors import ArtifactRootSelector, parse_artifact_selector
from spec_dock_runtime.infra.active_store import load_selection_v3
from spec_dock_runtime.infra.control_store import load_control
from spec_dock_runtime.infra.writer_lock import WriterLock

if TYPE_CHECKING:
    from pathlib import Path

    from spec_dock_runtime.domain.lifecycle import SelectionState

ArtifactCreationType = Literal["blank", "research", "interview", "disc", "decision-candidate", "adr"]


def _selected_scope(
    *, repo_root: Path, worktree_id: str, scope: str, selection: SelectionState | None
) -> tuple[str, str]:
    if selection is None:
        selection, _ = load_selection_v3(repo_root / "spec-dock", worktree_id=worktree_id)
    target = show_scope(load_scope_views(repo_root / "spec-dock"), scope, selection=selection)
    return target.id, target.kind


def create_scope_artifact(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    scope: str,
    artifact_type: ArtifactCreationType,
    title: str,
    slug: str | None,
    selection: SelectionState | None = None,
    lock_timeout: float = 0.0,
) -> ArtifactCatalogEntry:
    """Publish one of six documents under an explicitly resolved Scope."""
    if isinstance(parse_artifact_selector(scope), ArtifactRootSelector):
        raise ValueError("Artifact creation requires a Scope; @root accepts file import only")
    with WriterLock(common_dir, timeout=lock_timeout):
        admit_writer(
            load_control(common_dir),
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
        )
        scope_id, kind = _selected_scope(repo_root=repo_root, worktree_id=worktree_id, scope=scope, selection=selection)
        from spec_dock_runtime.cli.bootstrap import build_runtime

        use_cases = build_runtime(repo_root / "spec-dock", repo_root=repo_root).use_cases
        result = use_cases.create_artifact_doc(
            CreateArtifactDocRequest(
                artifact_type=artifact_type,
                scope_node_id=scope_id,
                title=title,
                slug=slug,
                scope_kind=kind,
            )
        )
        return show_artifact(repo_root=repo_root, scope=scope_id, artifact_id=result.artifact_id)


def import_scope_file(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    scope: str,
    source_path: Path,
    selection: SelectionState | None = None,
    lock_timeout: float = 0.0,
) -> ArtifactCatalogEntry:
    """Publish one opaque file, then return catalog identity without source details."""
    root = isinstance(parse_artifact_selector(scope), ArtifactRootSelector)
    with WriterLock(common_dir, timeout=lock_timeout):
        admit_writer(
            load_control(common_dir),
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
        )
        if root:
            scope_id, kind = "root", "root"
        else:
            scope_id, kind = _selected_scope(
                repo_root=repo_root, worktree_id=worktree_id, scope=scope, selection=selection
            )
        from spec_dock_runtime.cli.bootstrap import build_runtime

        use_cases = build_runtime(repo_root / "spec-dock", repo_root=repo_root).use_cases
        result = use_cases.import_file_artifact(
            FileArtifactImportRequest(
                target_kind=kind,
                target_value=None if root else scope_id,
                source_path=source_path,
            )
        )
        if not result.committed:
            raise RuntimeError("Artifact publication was not committed; inspect the destination before retrying")
        return show_artifact(repo_root=repo_root, scope=scope if root else scope_id, artifact_id=result.artifact_id)
