"""Change only the local title of an existing Scope."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from spec_dock_runtime.cli.admission import admit_writer
from spec_dock_runtime.domain.lifecycle import decode_scope_metadata
from spec_dock_runtime.domain.selectors import ScopeIdSelector, parse_scope_selector
from spec_dock_runtime.infra import fs_repo
from spec_dock_runtime.infra.control_store import load_control
from spec_dock_runtime.infra.json_store import atomic_write_json, read_guarded_json
from spec_dock_runtime.infra.writer_lock import WriterLock


@dataclass(frozen=True)
class ScopeEditResult:
    id: str
    path: Path
    revision: int
    changed: bool


def edit_scope_title(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    target_id: str,
    title: str,
    lock_timeout: float = 0.0,
) -> ScopeEditResult:
    """Apply a guarded title-only CAS; retain metadata and document bytes."""
    selector = parse_scope_selector(target_id)
    if not isinstance(selector, ScopeIdSelector) or selector.id != target_id:
        raise ValueError("Scope edit requires a canonical Scope ID")
    normalized_title = title.strip()
    if not normalized_title:
        raise ValueError("Scope title must not be empty")
    specdock_dir = repo_root / "spec-dock"
    if specdock_dir.is_symlink() or not specdock_dir.is_dir():
        raise ValueError("SpecDock workspace root is missing or redirected")
    with WriterLock(common_dir, timeout=lock_timeout):
        admit_writer(
            load_control(common_dir),
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
        )
        records = [record for record in fs_repo.load_node_records(specdock_dir) if record.id == selector.id]
        if len(records) != 1 or records[0].kind != selector.kind:
            raise LookupError("Scope was not found")
        record = records[0]
        scope_path = Path(record.path).resolve(strict=True)
        if not scope_path.is_relative_to(specdock_dir.resolve(strict=True)):
            raise ValueError("Scope path is outside this workspace")
        metadata_path = Path(record.meta_path)
        loaded = read_guarded_json(metadata_path)
        if loaded is None or not isinstance(loaded[0], dict):
            raise ValueError("Scope metadata is missing or invalid")
        metadata = decode_scope_metadata(loaded[0])
        if (
            metadata.raw.get("id") != record.id
            or metadata.raw.get("type") != record.kind
            or metadata.raw.get("parent_id") != record.parent_id
            or metadata.raw.get("title") != record.title
        ):
            raise ValueError("Scope metadata changed during edit")
        if metadata.raw["title"] == normalized_title:
            return ScopeEditResult(record.id, scope_path, metadata.revision, False)
        updated = dict(metadata.raw)
        updated["title"] = normalized_title
        updated["revision"] = metadata.revision + 1
        atomic_write_json(metadata_path, updated, expected_identity=loaded[1])
        return ScopeEditResult(record.id, scope_path, metadata.revision + 1, True)
