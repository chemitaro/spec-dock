"""Coordinate one journaled tooling update across every registered worktree."""

from __future__ import annotations

from dataclasses import replace
import os
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

from spec_dock.installation.executor import (
    apply_installation,
    preflight_rollback_installation,
    prepare_installation,
    rollback_installation,
)
from spec_dock.installation.group_journal import (
    InstallationGroupRecord,
    InstallationTarget,
    child_operation_id,
    read_group_record,
    write_group_record,
)
from spec_dock.installation.journal import InstallationRecord, read_record
from spec_dock.installation.source import assert_disjoint_source_target, verify_bundle_integrity
from spec_dock_runtime.application.installation_vnext import InstallationGroup, inspect_installation_group
from spec_dock_runtime.cli.admission import admit_writer
from spec_dock_runtime.infra.control_store import (
    WORKSPACE_SCHEMA,
    WRITER_PROTOCOL,
    ControlState,
    load_control,
    store_control,
)
from spec_dock_runtime.infra.writer_lock import writer_transaction

if TYPE_CHECKING:
    from spec_dock.installation.source import VerifiedBundle


def _child_root(common_dir: Path, group_id: str, worktree_id: str) -> Path:
    return common_dir / "spec-dock" / "control" / "installations" / group_id / "targets" / worktree_id


def _require_maintenance(common_dir: Path, *, minimum_epoch: int, engine_digest: str) -> None:
    control = load_control(common_dir)
    if (
        control is None
        or control.mode != "maintenance"
        or control.epoch < minimum_epoch
        or control.engine_digest != engine_digest
    ):
        raise ValueError("installation group lost its maintenance control")


def _can_restore_ready(control: ControlState) -> bool:
    return all(
        not item.active
        or (
            item.schema_version == WORKSPACE_SCHEMA
            and item.writer_protocol == WRITER_PROTOCOL
            and item.engine_digest == control.engine_digest
        )
        for item in control.worktrees
    )


def _fixed_targets(group: InstallationGroup, group_id: str) -> tuple[InstallationTarget, ...]:
    return tuple(
        InstallationTarget(item.id, item.root, child_operation_id(group_id, item.id), False) for item in group.worktrees
    )


def _check_bundle(
    group: InstallationGroup,
    bundle: VerifiedBundle,
    *,
    source_commit: str | None = None,
    source_digest: str | None = None,
) -> None:
    verify_bundle_integrity(bundle)
    if (source_commit is not None and bundle.source.commit != source_commit) or (
        source_digest is not None and bundle.digest != source_digest
    ):
        raise ValueError("installation recovery bundle differs from the fixed source")
    for target in group.worktrees:
        assert_disjoint_source_target(bundle.root, Path(target.root))


def _quarantine_unjournaled_stage(target: InstallationTarget, journal_root: Path) -> None:
    """Preserve partial preparation bytes before retrying the fixed child ID."""
    assert target.child_operation_id is not None
    area_parent = Path(target.root) / ".spec-dock-installations"
    area = area_parent / target.child_operation_id
    journal_parent = journal_root / "installations"
    journal_area = journal_parent / target.child_operation_id
    for parent, candidate in ((area_parent, area), (journal_parent, journal_area)):
        if parent.is_symlink() or candidate.is_symlink():
            raise ValueError("installation preparation path is redirected")
        if not os.path.lexists(candidate):
            continue
        if not candidate.is_dir():
            raise ValueError("installation preparation path is not a directory")
        if candidate == area and any(os.path.lexists(candidate / name) for name in ("backup", "displaced")):
            raise ValueError("unjournaled installation stage contains replacement evidence")
        candidate.rename(parent / f"{target.child_operation_id}.abandoned-{uuid4().hex}")


def _stage_missing(
    common_dir: Path, record: InstallationGroupRecord, bundle: VerifiedBundle, *, recover_stage: bool = False
) -> InstallationGroupRecord:
    for target in record.targets:
        assert target.child_operation_id is not None
        if target.child_operation_id != child_operation_id(record.operation_id, target.worktree_id):
            raise ValueError("installation child identity differs from the fixed group")
        journal_root = _child_root(common_dir, record.operation_id, target.worktree_id)
        journal_path = journal_root / "installations" / target.child_operation_id / "record.json"
        if os.path.lexists(journal_path):
            child = read_record(journal_root, target.child_operation_id)
        else:
            if recover_stage:
                _quarantine_unjournaled_stage(target, journal_root)
            child = prepare_installation(
                Path(target.root),
                journal_root,
                action="update",
                bundle=bundle,
                operation_id=target.child_operation_id,
            )
        if (
            child.target != target.root
            or child.action != "update"
            or child.source_commit != record.source_commit
            or child.source_digest != record.source_digest
        ):
            raise ValueError("installation child record differs from the fixed group")
    staged = replace(record, phase="staged", error=None)
    write_group_record(common_dir, staged)
    return staged


def _apply_children(common_dir: Path, record: InstallationGroupRecord) -> InstallationGroupRecord:
    minimum_epoch = record.control_epoch + 1
    engine_digest = record.engine_digest
    for index, target in enumerate(record.targets):
        assert target.child_operation_id is not None
        journal_root = _child_root(common_dir, record.operation_id, target.worktree_id)
        child = read_record(journal_root, target.child_operation_id)
        if (
            child.target != target.root
            or child.action != "update"
            or child.source_commit != record.source_commit
            or child.source_digest != record.source_digest
        ):
            raise ValueError("installation child record differs from the fixed group")
        if child.phase != "committed":
            apply_installation(
                journal_root,
                target.child_operation_id,
                enter_maintenance=lambda _child: _require_maintenance(
                    common_dir, minimum_epoch=minimum_epoch, engine_digest=engine_digest
                ),
            )
        targets = list(record.targets)
        targets[index] = replace(target, completed=True)
        record = replace(record, phase="applying", targets=tuple(targets), error=None)
        write_group_record(common_dir, record)
    return record


def _commit_group(common_dir: Path, record: InstallationGroupRecord) -> InstallationGroupRecord:
    control = load_control(common_dir)
    if control is None or control.engine_digest != record.engine_digest or control.epoch < record.control_epoch + 1:
        raise ValueError("installation control changed before completion")
    if not record.keep_maintenance:
        if not _can_restore_ready(control):
            raise ValueError("registered worktrees are not ready for the new writer")
        if control.mode == "maintenance":
            store_control(
                common_dir, replace(control, mode="ready", epoch=control.epoch + 1), expected_epoch=control.epoch
            )
        elif control.mode != "ready":
            raise ValueError("installation control has an invalid terminal mode")
    elif control.mode != "maintenance":
        raise ValueError("installation maintenance state changed before completion")
    completed = replace(record, phase="committed", error=None)
    write_group_record(common_dir, completed)
    return completed


def update_installation_group(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    bundle: VerifiedBundle,
    keep_maintenance: bool,
    lock_timeout: float = 0.0,
) -> InstallationGroupRecord:
    """Stage every target before replacing one, and preserve recovery on failure."""
    before = inspect_installation_group(repo_root=repo_root, common_dir=common_dir)
    if any(item.version is None for item in before.worktrees):
        raise ValueError("installation group contains an unversioned target")
    _check_bundle(before, bundle)
    with writer_transaction(common_dir, worktree_ids=tuple(item.id for item in before.worktrees), timeout=lock_timeout):
        current = inspect_installation_group(repo_root=repo_root, common_dir=common_dir)
        if current != before:
            raise ValueError("installation group changed before the update lock")
        control = load_control(common_dir)
        assert control is not None
        admit_writer(
            control,
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
            maintenance_command="installation.update",
        )
        if not keep_maintenance and not _can_restore_ready(control):
            raise ValueError("mixed writer versions require --maintenance")
        group_id = uuid4().hex
        record = InstallationGroupRecord(
            group_id,
            "update",
            str(common_dir),
            control.epoch,
            engine_digest,
            bundle.source.commit,
            bundle.digest,
            keep_maintenance,
            _fixed_targets(current, group_id),
            "preparing",
        )
        write_group_record(common_dir, record, create=True)
        try:
            store_control(
                common_dir, replace(control, mode="maintenance", epoch=control.epoch + 1), expected_epoch=control.epoch
            )
            record = _stage_missing(common_dir, record, bundle)
            record = _apply_children(common_dir, record)
            return _commit_group(common_dir, record)
        except Exception as error:
            record = replace(read_group_record(common_dir, group_id), phase="recovery-required", error=str(error))
            write_group_record(common_dir, record)
            raise


def resume_installation_group(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    operation_id: str,
    bundle: VerifiedBundle,
    lock_timeout: float = 0.0,
) -> InstallationGroupRecord:
    """Resume only the fixed targets and source captured by the group journal."""
    record = read_group_record(common_dir, operation_id)
    if record.action != "update" or record.phase in {"committed", "rolled-back"}:
        raise ValueError("installation group is not resumable")
    group = inspect_installation_group(repo_root=repo_root, common_dir=common_dir)
    if tuple((item.id, item.root) for item in group.worktrees) != tuple(
        (item.worktree_id, item.root) for item in record.targets
    ):
        raise ValueError("installation recovery target inventory changed")
    _check_bundle(group, bundle, source_commit=record.source_commit, source_digest=record.source_digest)
    with writer_transaction(common_dir, worktree_ids=tuple(item.id for item in group.worktrees), timeout=lock_timeout):
        record = read_group_record(common_dir, operation_id)
        current = inspect_installation_group(repo_root=repo_root, common_dir=common_dir)
        if current != group:
            raise ValueError("installation recovery inventory changed before the lock")
        control = load_control(common_dir)
        if control is None:
            raise ValueError("installation control is missing")
        admit_writer(
            control,
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=control.epoch,
            recovery_operation_id=operation_id,
        )
        if control.epoch == record.control_epoch and control.mode in {"ready", "maintenance"}:
            store_control(
                common_dir, replace(control, mode="maintenance", epoch=control.epoch + 1), expected_epoch=control.epoch
            )
        elif control.mode not in {"maintenance", "ready"} or control.epoch < record.control_epoch + 1:
            raise ValueError("installation control is not at a recoverable epoch")
        try:
            record = _stage_missing(common_dir, record, bundle, recover_stage=True)
            record = _apply_children(common_dir, record)
            return _commit_group(common_dir, record)
        except Exception as error:
            record = replace(read_group_record(common_dir, operation_id), phase="recovery-required", error=str(error))
            write_group_record(common_dir, record)
            raise


def rollback_installation_group(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    operation_id: str,
    lock_timeout: float = 0.0,
) -> InstallationGroupRecord:
    """Restore a pending update or an untouched committed maintenance update."""
    record = read_group_record(common_dir, operation_id)
    if record.action != "update" or (record.phase == "committed" and not record.keep_maintenance):
        raise ValueError("installation group is not rollback eligible")
    if record.phase == "rolled-back":
        return record
    group = inspect_installation_group(repo_root=repo_root, common_dir=common_dir)
    if tuple((item.id, item.root) for item in group.worktrees) != tuple(
        (item.worktree_id, item.root) for item in record.targets
    ):
        raise ValueError("installation rollback target inventory changed")
    with writer_transaction(common_dir, worktree_ids=tuple(item.id for item in group.worktrees), timeout=lock_timeout):
        record = read_group_record(common_dir, operation_id)
        if record.action != "update" or (record.phase == "committed" and not record.keep_maintenance):
            raise ValueError("installation group is not rollback eligible")
        if inspect_installation_group(repo_root=repo_root, common_dir=common_dir) != group:
            raise ValueError("installation rollback inventory changed before the lock")
        control = load_control(common_dir)
        if control is None:
            raise ValueError("installation control is missing")
        if record.phase == "committed":
            if control.mode != "maintenance" or control.epoch != record.control_epoch + 1:
                raise ValueError("installation maintenance state changed after completion")
            admit_writer(
                control,
                common_dir=common_dir,
                worktree_id=worktree_id,
                engine_digest=engine_digest,
                expected_epoch=control.epoch,
                maintenance_command="installation.update",
            )
        else:
            admit_writer(
                control,
                common_dir=common_dir,
                worktree_id=worktree_id,
                engine_digest=engine_digest,
                expected_epoch=control.epoch,
                recovery_operation_id=operation_id,
            )
        if control.epoch == record.control_epoch and control.mode in {"ready", "maintenance"}:
            store_control(
                common_dir, replace(control, mode="maintenance", epoch=control.epoch + 1), expected_epoch=control.epoch
            )
        else:
            _require_maintenance(common_dir, minimum_epoch=record.control_epoch + 1, engine_digest=engine_digest)
        try:
            children: list[InstallationRecord | None] = []
            for target in record.targets:
                if target.child_operation_id != child_operation_id(record.operation_id, target.worktree_id):
                    raise ValueError("installation child identity differs from the fixed group")
                journal_root = _child_root(common_dir, record.operation_id, target.worktree_id)
                journal_path = journal_root / "installations" / target.child_operation_id / "record.json"
                if not os.path.lexists(journal_path):
                    if target.completed:
                        raise ValueError("completed installation child has no journal")
                    children.append(None)
                    continue
                child = preflight_rollback_installation(journal_root, target.child_operation_id, allow_committed=True)
                if (
                    child.target != target.root
                    or child.action != "update"
                    or child.source_commit != record.source_commit
                    or child.source_digest != record.source_digest
                ):
                    raise ValueError("installation child record differs from the fixed group")
                children.append(child)
            for target, rollback_child in reversed(tuple(zip(record.targets, children, strict=True))):
                if rollback_child is None or rollback_child.phase == "rolled-back":
                    continue
                assert target.child_operation_id is not None
                rollback_installation(
                    _child_root(common_dir, record.operation_id, target.worktree_id),
                    target.child_operation_id,
                    enter_maintenance=lambda _child: _require_maintenance(
                        common_dir, minimum_epoch=record.control_epoch + 1, engine_digest=engine_digest
                    ),
                    allow_committed=True,
                )
            rolled_back = replace(record, phase="rolled-back", error=None)
            write_group_record(common_dir, rolled_back)
            return rolled_back
        except Exception as error:
            failed = replace(read_group_record(common_dir, operation_id), phase="recovery-required", error=str(error))
            write_group_record(common_dir, failed)
            raise
