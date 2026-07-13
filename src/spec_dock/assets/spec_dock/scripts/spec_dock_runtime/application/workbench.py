from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from spec_dock_runtime.application.contracts import (
    WorkbenchCopyRequest,
    WorkbenchCopyResult,
    WorktreeListRequest,
)
from spec_dock_runtime.application.worktree import worktree_list
from spec_dock_runtime.application.worktree_target import resolve_worktree_target
from spec_dock_runtime.domain.ids import parse_id

if TYPE_CHECKING:
    from spec_dock_runtime.application.ports import Ports
    from spec_dock_runtime.infra.contracts import StoredMetaRecord


def workbench_copy(req: WorkbenchCopyRequest, ports: Ports) -> WorkbenchCopyResult:
    _require_ports(ports)
    scope_id = _validate_scope_id(req.scope_id)

    inventory = worktree_list(WorktreeListRequest(), ports).worktrees
    target = resolve_worktree_target(req.target, inventory, command="copy")
    source = next((record for record in inventory if record.current), None)
    if source is None:
        raise RuntimeError("workbench copy requires the current worktree record")
    if target.current or "bare_worktree" in target.remove_blockers or not target.path_exists:
        raise RuntimeError("workbench copy target is not eligible")

    assert ports.repo_root is not None
    assert ports.specdock_dir is not None
    assert ports.node_repo is not None
    assert ports.filesystem_gateway is not None
    try:
        specdock_relative = ports.specdock_dir.relative_to(ports.repo_root)
    except ValueError as exc:
        raise RuntimeError("workbench copy requires spec-dock inside the current repository") from exc

    source_specdock = ports.specdock_dir
    target_specdock = target.path / specdock_relative
    source_scope = _resolve_scope(ports.node_repo.load_node_records(source_specdock), scope_id, side="source")
    target_scope = _resolve_scope(ports.node_repo.load_node_records(target_specdock), scope_id, side="target")

    source_workbench = Path(source_scope.path) / ".workbench"
    target_workbench = Path(target_scope.path) / ".workbench"
    ports.filesystem_gateway.copy_workbench(source_workbench, target_workbench)
    return WorkbenchCopyResult(
        scope_id=scope_id,
        source_worktree=source,
        target_worktree=target,
        target_workbench_path=target_workbench,
    )


def _require_ports(ports: Ports) -> None:
    if ports.repo_root is None or ports.specdock_dir is None:
        raise RuntimeError("workbench copy requires repository and spec-dock roots")
    if ports.node_repo is None:
        raise RuntimeError("workbench copy requires a node repository")
    if ports.filesystem_gateway is None:
        raise RuntimeError("workbench copy requires a filesystem gateway")


def _validate_scope_id(value: str) -> str:
    scope_id = value.strip().lower()
    prefix, is_local, _ = parse_id(scope_id)
    if prefix not in {"init", "epic", "iss"} or is_local:
        raise RuntimeError("workbench copy requires a full initiative, epic, or issue id")
    return scope_id


def _resolve_scope(records: list[StoredMetaRecord], scope_id: str, *, side: str) -> StoredMetaRecord:
    matches = [record for record in records if record.id == scope_id]
    if len(matches) != 1:
        raise RuntimeError(f"workbench copy could not resolve {side} scope: {scope_id}")
    return matches[0]
