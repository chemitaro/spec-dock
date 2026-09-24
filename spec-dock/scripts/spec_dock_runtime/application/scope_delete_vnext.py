"""Plan local Scope deletion without contacting or changing GitHub."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import os
from pathlib import Path
import stat
from typing import TYPE_CHECKING
import uuid

from spec_dock_runtime.application.active_selection import clear_selection
from spec_dock_runtime.application.dependency_vnext import _read_raw_edges
from spec_dock_runtime.application.operation_executor import (
    prepare_operation,
    record_effect_intent,
    record_effect_result,
)
from spec_dock_runtime.application.scope_completion import _descendants
from spec_dock_runtime.application.scope_query import load_scope_views, show_scope
from spec_dock_runtime.cli.admission import admit_writer
from spec_dock_runtime.domain.lifecycle import SelectionState
from spec_dock_runtime.infra.active_store import load_selection_v3, save_selection_v3
from spec_dock_runtime.infra.control_store import load_control
from spec_dock_runtime.infra.json_store import atomic_write_json, read_guarded_json
from spec_dock_runtime.infra.operation_journal import JournalStore
from spec_dock_runtime.infra.registry_store import RegistryStore
from spec_dock_runtime.infra.writer_lock import WriterLock

if TYPE_CHECKING:
    from collections.abc import Mapping

    from spec_dock_runtime.application.scope_query import ScopeView
    from spec_dock_runtime.domain.operation import OperationRecord


@dataclass(frozen=True)
class ScopeDeletePlan:
    target_id: str
    deleted_ids: tuple[str, ...]
    selection_after: SelectionState
    boundary_edges: tuple[tuple[str, str], ...]
    survivor_dependencies: dict[str, tuple[str, ...]]


@dataclass(frozen=True)
class ScopeDeleteResult:
    target_id: str
    deleted_ids: tuple[str, ...]
    quarantine_path: Path
    operation_id: str


def plan_scope_delete(
    views: tuple[ScopeView, ...],
    *, target: str, selection: SelectionState,
    dependencies: Mapping[str, tuple[str, ...]], recursive: bool = False,
    clear_active: bool = False, detach_dependencies: bool = False,
) -> ScopeDeletePlan:
    """Fix the local subtree and every cross-boundary dependency before mutation."""
    scope = show_scope(views, target, selection=selection)
    descendants = _descendants(views, scope)
    if descendants and not recursive:
        raise ValueError("RECURSIVE_REQUIRED")
    deleted_ids = (scope.id, *(view.id for view in descendants))
    deleted = set(deleted_ids)
    ids = {view.id for view in views}
    if set(dependencies) != ids or any(destination not in ids for edges in dependencies.values() for destination in edges):
        raise ValueError("dependency snapshot does not match Scope graph")
    selection_intersects = bool(deleted.intersection(
        (selection.initiative_id, selection.epic_id, selection.issue_id)
    ))
    if selection_intersects and not clear_active:
        raise ValueError("CLEAR_ACTIVE_REQUIRED")
    selection_after = (
        clear_selection(views, current=selection, from_target=scope.id)
        if selection_intersects else selection
    )
    boundary_edges = tuple(sorted(
        (source, destination)
        for source, destinations in dependencies.items()
        for destination in destinations
        if (source in deleted) != (destination in deleted)
    ))
    if boundary_edges and not detach_dependencies:
        raise ValueError("DETACH_DEPENDENCIES_REQUIRED")
    survivor_dependencies = {
        source: tuple(destination for destination in destinations if destination not in deleted)
        for source, destinations in dependencies.items()
        if source not in deleted and any(destination in deleted for destination in destinations)
    }
    return ScopeDeletePlan(scope.id, deleted_ids, selection_after, boundary_edges, survivor_dependencies)


def _canonical(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _fingerprint(fixed: dict[str, str]) -> str:
    return "sha256:" + hashlib.sha256(_canonical(fixed).encode("utf-8")).hexdigest()


def _selection_text(value: SelectionState) -> str:
    return _canonical([value.initiative_id, value.epic_id, value.issue_id, value.focus_id])


def _selection_from_text(raw: str, *, worktree_id: str, revision: int) -> SelectionState:
    fields = json.loads(raw)
    if not isinstance(fields, list) or len(fields) != 4 or any(
        item is not None and not isinstance(item, str) for item in fields
    ):
        raise ValueError("recorded delete selection is invalid")
    return SelectionState(worktree_id, revision, *fields)


def _safe_relative(repo_root: Path, raw: str) -> Path:
    relative = Path(raw)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts or relative.parts[0] != "spec-dock":
        raise ValueError("recorded delete path is outside the workspace")
    path = repo_root / relative
    if any(parent.is_symlink() for parent in (path.parent, *path.parent.parents)):
        raise ValueError("recorded delete parent is redirected")
    return path


def _prepare_survivor_edits(
    repo_root: Path, views: tuple[ScopeView, ...], plan: ScopeDeletePlan
) -> tuple[tuple[str, dict[str, object], dict[str, object]], ...]:
    by_id = {view.id: view for view in views}
    result: list[tuple[str, dict[str, object], dict[str, object]]] = []
    for scope_id, edges in sorted(plan.survivor_dependencies.items()):
        view = by_id[scope_id]
        loaded = read_guarded_json(view.path / ".meta.json")
        if loaded is None or not isinstance(loaded[0], dict) or loaded[0].get("revision") != view.revision:
            raise ValueError("surviving Scope metadata changed before delete")
        before = loaded[0]
        after = dict(before)
        after["depends_on"] = list(edges)
        after["revision"] = view.revision + 1
        relative = (view.path / ".meta.json").relative_to(repo_root).as_posix()
        result.append((relative, before, after))
    return tuple(result)


def _decode_edits(raw: str) -> tuple[tuple[str, dict[str, object], dict[str, object]], ...]:
    loaded = json.loads(raw)
    if not isinstance(loaded, list):
        raise ValueError("recorded delete edits are invalid")
    result: list[tuple[str, dict[str, object], dict[str, object]]] = []
    for item in loaded:
        if not isinstance(item, list) or len(item) != 3 or not isinstance(item[0], str) or not all(
            isinstance(part, dict) for part in item[1:]
        ):
            raise ValueError("recorded delete edit is invalid")
        result.append((item[0], item[1], item[2]))
    if len({item[0] for item in result}) != len(result):
        raise ValueError("recorded delete edit path is duplicated")
    return tuple(result)


def _apply_edits(repo_root: Path, raw: str, *, write: bool) -> None:
    for relative, before, after in _decode_edits(raw):
        path = _safe_relative(repo_root, relative)
        loaded = read_guarded_json(path)
        if loaded is None or not isinstance(loaded[0], dict):
            raise ValueError("surviving Scope metadata is missing during delete")
        if loaded[0] == after:
            continue
        if loaded[0] != before or not write:
            raise ValueError("surviving Scope metadata differs from recorded delete image")
        atomic_write_json(path, after, expected_identity=loaded[1])


def _apply_selection(
    repo_root: Path, fixed: dict[str, str], revision: int, *, write: bool
) -> None:
    specdock_dir = repo_root / "spec-dock"
    before = _selection_from_text(fixed["selection_before"], worktree_id=fixed["worktree"], revision=revision)
    after = _selection_from_text(
        fixed["selection_after"], worktree_id=fixed["worktree"],
        revision=revision + (fixed["selection_before"] != fixed["selection_after"]),
    )
    selection, identity = load_selection_v3(specdock_dir, worktree_id=fixed["worktree"])
    if selection == after:
        return
    if selection != before or not write:
        raise ValueError("active selection differs from recorded delete image")
    if after != before:
        save_selection_v3(specdock_dir, after, views=load_scope_views(specdock_dir), expected_identity=identity)


def _prepare_quarantine_parent(path: Path) -> None:
    missing: list[Path] = []
    cursor = path
    while not cursor.exists():
        missing.append(cursor)
        cursor = cursor.parent
    if cursor.is_symlink() or not cursor.is_dir():
        raise ValueError("delete quarantine parent is redirected")
    for directory in reversed(missing):
        directory.mkdir(mode=0o700)
        descriptor = os.open(directory.parent, os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0))
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    if any(item.is_symlink() for item in (path, *path.parents)):
        raise ValueError("delete quarantine parent is redirected")


def _apply_quarantine(repo_root: Path, fixed: dict[str, str], *, write: bool) -> None:
    source = _safe_relative(repo_root, fixed["source_path"])
    destination = _safe_relative(repo_root, fixed["quarantine_path"])
    expected = (int(fixed["target_device"]), int(fixed["target_inode"]))
    source_exists = os.path.lexists(source)
    destination_exists = os.path.lexists(destination)
    if destination_exists:
        found = destination.lstat()
        if source_exists or not stat.S_ISDIR(found.st_mode) or (found.st_dev, found.st_ino) != expected:
            raise ValueError("delete quarantine differs from the recorded tree")
        return
    if not source_exists or not write:
        raise ValueError("delete source tree is missing before quarantine")
    found = source.lstat()
    if not stat.S_ISDIR(found.st_mode) or (found.st_dev, found.st_ino) != expected:
        raise ValueError("delete source tree identity changed")
    _prepare_quarantine_parent(destination.parent)
    flags = os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0)
    source_fd = os.open(source.parent, flags)
    destination_fd = os.open(destination.parent, flags)
    try:
        if os.fstat(destination_fd).st_dev != expected[0]:
            raise ValueError("delete quarantine must use the target filesystem")
        bound = os.stat(source.name, dir_fd=source_fd, follow_symlinks=False)
        if (bound.st_dev, bound.st_ino) != expected or not stat.S_ISDIR(bound.st_mode):
            raise ValueError("delete source tree changed before quarantine")
        try:
            os.stat(destination.name, dir_fd=destination_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise ValueError("delete quarantine destination already exists")
        os.rename(source.name, destination.name, src_dir_fd=source_fd, dst_dir_fd=destination_fd)
        os.fsync(source_fd)
        os.fsync(destination_fd)
    finally:
        os.close(source_fd)
        os.close(destination_fd)
    _apply_quarantine(repo_root, fixed, write=False)


def _apply_tombstones(common_dir: Path, fixed: dict[str, str], revision: int, *, write: bool) -> None:
    deleted = json.loads(fixed["deleted_ids"])
    if not isinstance(deleted, list) or not all(isinstance(item, str) for item in deleted):
        raise ValueError("recorded deleted Scope IDs are invalid")
    registry = RegistryStore(common_dir)
    state, _ = registry.load()
    requested = frozenset(deleted)
    if requested.issubset(state.deleted_ids):
        if state.revision not in (revision, revision + 1):
            raise ValueError("delete registry revision changed")
        return
    if state.revision != revision or not write:
        raise ValueError("delete registry differs from recorded before image")
    registry.mark_deleted_locked(tuple(deleted))


def _complete_effect(
    operation: OperationRecord, journal: JournalStore, *, effect_id: str, kind: str,
    target: str, index: int, apply: object,
) -> OperationRecord:
    if len(operation.effects) == index:
        advanced = record_effect_intent(operation, effect_id=effect_id, kind=kind, target=target)
        journal.update(advanced, expected_sequence=operation.sequence)
        operation = advanced
    if len(operation.effects) < index + 1:
        raise ValueError("recorded delete effect sequence differs")
    effect = operation.effects[index]
    if (effect.id, effect.kind, effect.target) != (effect_id, kind, target):
        raise ValueError("recorded delete effect identity differs")
    if effect.status not in ("intent", "succeeded"):
        raise ValueError("recorded delete effect cannot be resumed")
    apply(write=effect.status == "intent")
    if effect.status == "succeeded":
        return operation
    advanced = record_effect_result(operation, effect_id=effect_id, status="succeeded")
    journal.update(advanced, expected_sequence=operation.sequence)
    return advanced


def _run_delete(
    *, repo_root: Path, common_dir: Path, journal: JournalStore,
    operation: OperationRecord,
) -> ScopeDeleteResult:
    fixed = dict(operation.fixed_targets)
    revisions = dict(operation.before_revisions)
    operation = _complete_effect(
        operation, journal, effect_id="dependency-detach", kind="local", target=fixed["scope"], index=0,
        apply=lambda *, write: _apply_edits(repo_root, fixed["survivor_edits"], write=write),
    )
    operation = _complete_effect(
        operation, journal, effect_id="selection-clear", kind="local", target=fixed["worktree"], index=1,
        apply=lambda *, write: _apply_selection(repo_root, fixed, revisions["selection"], write=write),
    )
    operation = _complete_effect(
        operation, journal, effect_id="quarantine-move", kind="local", target=fixed["scope"], index=2,
        apply=lambda *, write: _apply_quarantine(repo_root, fixed, write=write),
    )
    operation = _complete_effect(
        operation, journal, effect_id="registry-tombstone", kind="local", target=fixed["scope"], index=3,
        apply=lambda *, write: _apply_tombstones(common_dir, fixed, revisions["registry"], write=write),
    )
    terminal = replace(operation, phase="complete", terminal_status="succeeded", sequence=operation.sequence + 1)
    journal.update(terminal, expected_sequence=operation.sequence)
    deleted = json.loads(fixed["deleted_ids"])
    return ScopeDeleteResult(
        fixed["scope"], tuple(deleted), _safe_relative(repo_root, fixed["quarantine_path"]), operation.operation_id
    )


def delete_scope(
    *, repo_root: Path, common_dir: Path, worktree_id: str, engine_digest: str,
    expected_epoch: int, target: str, recursive: bool = False, clear_active: bool = False,
    detach_dependencies: bool = False, lock_timeout: float = 0.0,
) -> ScopeDeleteResult:
    """Move the fixed local tree to retained quarantine without remote effects."""
    specdock_dir = repo_root / "spec-dock"
    with WriterLock(common_dir, timeout=lock_timeout):
        control = load_control(common_dir)
        admit_writer(
            control, common_dir=common_dir, worktree_id=worktree_id,
            engine_digest=engine_digest, expected_epoch=expected_epoch,
        )
        views = load_scope_views(specdock_dir)
        selection, _ = load_selection_v3(specdock_dir, worktree_id=worktree_id)
        dependencies, _ = _read_raw_edges(views)
        plan = plan_scope_delete(
            views, target=target, selection=selection, dependencies=dependencies,
            recursive=recursive, clear_active=clear_active, detach_dependencies=detach_dependencies,
        )
        scope = show_scope(views, plan.target_id)
        target_stat = scope.path.lstat()
        if not stat.S_ISDIR(target_stat.st_mode):
            raise ValueError("delete target is not a directory")
        edits = _prepare_survivor_edits(repo_root, views, plan)
        registry_state, _ = RegistryStore(common_dir).load()
        quarantine_relative = f"spec-dock/.agent/delete-quarantine/{uuid.uuid4().hex}/{scope.path.name}"
        fixed = {
            "scope": scope.id, "worktree": worktree_id,
            "source_path": scope.path.relative_to(repo_root).as_posix(),
            "quarantine_path": quarantine_relative,
            "target_device": str(target_stat.st_dev), "target_inode": str(target_stat.st_ino),
            "deleted_ids": _canonical(list(plan.deleted_ids)), "survivor_edits": _canonical(edits),
            "selection_before": _selection_text(selection), "selection_after": _selection_text(plan.selection_after),
            "recursive": str(recursive).lower(), "clear_active": str(clear_active).lower(),
            "detach_dependencies": str(detach_dependencies).lower(),
        }
        assert control is not None
        operation = prepare_operation(
            command="scope.delete",
            effect_plan=("dependency-detach", "selection-clear", "quarantine-move", "registry-tombstone"),
            fixed_targets=fixed, request_fingerprint=_fingerprint(fixed),
            before_revisions={"selection": selection.revision, "registry": registry_state.revision},
            engine_digest=engine_digest, writer_epoch=control.epoch,
        )
        operation = replace(operation, backup_refs=(quarantine_relative,))
        journal = JournalStore(common_dir)
        journal.create(operation)
        return _run_delete(repo_root=repo_root, common_dir=common_dir, journal=journal, operation=operation)


def resume_scope_delete(
    *, repo_root: Path, common_dir: Path, worktree_id: str, engine_digest: str,
    expected_epoch: int, operation_id: str, lock_timeout: float = 0.0,
) -> ScopeDeleteResult:
    """Resume only the recorded local images and fixed quarantine target."""
    with WriterLock(common_dir, timeout=lock_timeout):
        journal = JournalStore(common_dir)
        operation = journal.load(operation_id)
        fixed = dict(operation.fixed_targets)
        if (
            operation.command != "scope.delete"
            or operation.effect_plan != ("dependency-detach", "selection-clear", "quarantine-move", "registry-tombstone")
            or set(fixed) != {
                "scope", "worktree", "source_path", "quarantine_path", "target_device", "target_inode",
                "deleted_ids", "survivor_edits", "selection_before", "selection_after", "recursive",
                "clear_active", "detach_dependencies",
            }
            or fixed["worktree"] != worktree_id
            or operation.request_fingerprint != _fingerprint(fixed)
            or operation.engine_digest != engine_digest
            or operation.writer_epoch != expected_epoch
            or operation.backup_refs != (fixed["quarantine_path"],)
            or set(dict(operation.before_revisions)) != {"selection", "registry"}
        ):
            raise ValueError("scope delete recovery differs from the recorded request")
        if operation.terminal_status == "succeeded":
            return ScopeDeleteResult(
                fixed["scope"], tuple(json.loads(fixed["deleted_ids"])),
                _safe_relative(repo_root, fixed["quarantine_path"]), operation_id,
            )
        if operation.terminal_status != "pending":
            raise ValueError("scope delete recovery requires a pending operation")
        admit_writer(
            load_control(common_dir), common_dir=common_dir, worktree_id=worktree_id,
            engine_digest=engine_digest, expected_epoch=expected_epoch,
            recovery_operation_id=operation_id,
        )
        return _run_delete(repo_root=repo_root, common_dir=common_dir, journal=journal, operation=operation)
