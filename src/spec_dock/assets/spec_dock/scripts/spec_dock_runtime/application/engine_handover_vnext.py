"""Journal the transition between two fixed external engine generations."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING

from spec_dock.installation.executor import verify_installation_after
from spec_dock.installation.group_journal import read_group_record
from spec_dock.installation.journal import read_record
from spec_dock.runtime_loader import (
    EnginePin,
    VerifiedEngine,
    read_engine_pin,
    replace_engine_pin,
    verify_engine_pin,
)
from spec_dock_runtime.application.installation_vnext import inspect_installation_group
from spec_dock_runtime.cli.admission import admit_writer
from spec_dock_runtime.infra.control_store import ControlState, load_control, store_control
from spec_dock_runtime.infra.engine_handover_store import (
    EngineHandoverRecord,
    new_engine_handover,
    pending_engine_handovers,
    read_engine_handover,
    write_engine_handover,
)
from spec_dock_runtime.infra.writer_lock import writer_transaction

if TYPE_CHECKING:
    from spec_dock.installation.source import VerifiedBundle


def verify_source_update(
    *, repo_root: Path, common_dir: Path, update_id: str, bundle: VerifiedBundle | None, allow_bootstrap: bool = False
) -> tuple[str, ...]:
    update = read_group_record(common_dir, update_id)
    if (
        update.action != "update"
        or update.phase != "committed"
        or not update.keep_maintenance
        or (update.bootstrap and not allow_bootstrap)
    ):
        raise ValueError("engine handover requires a committed maintenance update")
    if bundle is not None and (bundle.source.commit != update.source_commit or bundle.digest != update.source_digest):
        raise ValueError("engine handover candidate differs from the installed update")
    group = inspect_installation_group(repo_root=repo_root, common_dir=common_dir)
    targets = tuple(item.id for item in group.worktrees)
    if tuple((item.id, item.root) for item in group.worktrees) != tuple(
        (item.worktree_id, item.root) for item in update.targets
    ):
        raise ValueError("engine handover target inventory changed")
    for target in update.targets:
        if not target.completed or target.child_operation_id is None:
            raise ValueError("engine handover source update is incomplete")
        child_root = common_dir / "spec-dock/control/installations" / update_id / "targets" / target.worktree_id
        child = read_record(child_root, target.child_operation_id)
        if (
            child.phase != "committed"
            or child.target != target.root
            or child.source_commit != update.source_commit
            or child.source_digest != update.source_digest
            or (update.version_tracked and child.requested_version != update.requested_version)
        ):
            raise ValueError("engine handover child update changed")
        verify_installation_after(child_root, target.child_operation_id)
    return targets


def _engine_from_record(record: EngineHandoverRecord, *, repo_root: Path, prior: bool) -> VerifiedEngine:
    if prior:
        pin = EnginePin(Path(record.prior_executable), Path(record.prior_distribution_root), record.prior_digest)
    else:
        pin = EnginePin(Path(record.next_executable), Path(record.next_distribution_root), record.next_digest)
    return verify_engine_pin(pin, checkout_root=repo_root)


def _rotated_control(control: ControlState, new_digest: str) -> ControlState:
    return replace(
        control,
        mode="maintenance",
        epoch=control.epoch + 1,
        engine_digest=new_digest,
        worktrees=tuple(replace(item, engine_digest=new_digest) for item in control.worktrees),
    )


def handover_candidate(
    common_dir: Path,
    *,
    update_id: str | None,
    operation_id: str | None,
    expected_next_digest: str,
) -> tuple[str, str]:
    """Resolve the fixed archive identity without exposing journal storage to the command adapter."""
    if (update_id is None) == (operation_id is None):
        raise ValueError("engine handover requires one source operation")
    if operation_id is not None:
        handover = read_engine_handover(common_dir, operation_id)
        if handover.next_digest != expected_next_digest:
            raise ValueError("engine handover requires its recorded new engine")
        update_id = handover.source_update_id
    assert update_id is not None
    update = read_group_record(common_dir, update_id)
    if update.source_commit is None:
        raise ValueError("engine handover update has no fixed source commit")
    return update_id, update.source_commit


def plan_engine_handover(
    *, repo_root: Path, common_dir: Path, update_id: str, bundle: VerifiedBundle, next_engine: VerifiedEngine
) -> tuple[str, ...]:
    targets = verify_source_update(repo_root=repo_root, common_dir=common_dir, update_id=update_id, bundle=bundle)
    control = load_control(common_dir)
    prior = read_engine_pin(common_dir, checkout_root=repo_root)
    verify_engine_pin(
        EnginePin(next_engine.executable, next_engine.distribution_root, next_engine.distribution_digest),
        checkout_root=repo_root,
    )
    if (
        control is None
        or control.mode != "maintenance"
        or control.engine_digest != prior.distribution_digest
        or prior.distribution_digest == next_engine.distribution_digest
        or pending_engine_handovers(common_dir)
    ):
        raise ValueError("engine handover is not eligible")
    return targets


def activate_engine_group(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    old_digest: str,
    expected_epoch: int,
    next_engine: VerifiedEngine,
    update_id: str,
    bundle: VerifiedBundle,
    lock_timeout: float = 0.0,
) -> EngineHandoverRecord:
    """Switch locator then control under one prepared record while maintenance holds."""
    next_engine = verify_engine_pin(
        EnginePin(next_engine.executable, next_engine.distribution_root, next_engine.distribution_digest),
        checkout_root=repo_root,
    )
    targets = verify_source_update(repo_root=repo_root, common_dir=common_dir, update_id=update_id, bundle=bundle)
    with writer_transaction(common_dir, worktree_ids=targets, timeout=lock_timeout):
        if (
            verify_source_update(repo_root=repo_root, common_dir=common_dir, update_id=update_id, bundle=bundle)
            != targets
        ):
            raise ValueError("engine handover targets changed before the lock")
        control = load_control(common_dir)
        admit_writer(
            control,
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=old_digest,
            expected_epoch=expected_epoch,
            maintenance_command="installation.update",
        )
        if control is None or control.mode != "maintenance" or old_digest == next_engine.distribution_digest:
            raise ValueError("engine handover requires maintenance with a different engine")
        if read_group_record(common_dir, update_id).engine_digest != control.engine_digest:
            raise ValueError("engine handover source update used another engine")
        prior = read_engine_pin(common_dir, checkout_root=repo_root)
        if prior.distribution_digest != old_digest or pending_engine_handovers(common_dir):
            raise ValueError("engine handover prior identity or recovery state changed")
        record = new_engine_handover(
            common_dir,
            source_update_id=update_id,
            control_epoch=control.epoch,
            prior_executable=str(prior.executable),
            prior_distribution_root=str(prior.distribution_root),
            prior_digest=prior.distribution_digest,
            next_executable=str(next_engine.executable),
            next_distribution_root=str(next_engine.distribution_root),
            next_digest=next_engine.distribution_digest,
            targets=targets,
        )
        write_engine_handover(common_dir, record, create=True)
        replace_engine_pin(common_dir, prior=prior, next_engine=next_engine)
        store_control(
            common_dir, _rotated_control(control, next_engine.distribution_digest), expected_epoch=control.epoch
        )
        completed = replace(record, phase="committed")
        write_engine_handover(common_dir, completed)
        return completed


def resume_engine_handover(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    next_engine: VerifiedEngine,
    operation_id: str,
    bundle: VerifiedBundle,
    lock_timeout: float = 0.0,
) -> EngineHandoverRecord:
    record = read_engine_handover(common_dir, operation_id)
    if record.phase != "prepared" or record.next_digest != next_engine.distribution_digest:
        raise ValueError("engine handover record is not resumable by this engine")
    with writer_transaction(common_dir, worktree_ids=record.targets, timeout=lock_timeout):
        if read_engine_handover(common_dir, operation_id) != record:
            raise ValueError("engine handover record changed before recovery")
        if (
            verify_source_update(
                repo_root=repo_root, common_dir=common_dir, update_id=record.source_update_id, bundle=bundle
            )
            != record.targets
        ):
            raise ValueError("engine handover source inventory changed")
        prior = _engine_from_record(record, repo_root=repo_root, prior=True)
        next_engine = _engine_from_record(record, repo_root=repo_root, prior=False)
        control = load_control(common_dir)
        if control is None or control.mode != "maintenance":
            raise ValueError("engine handover maintenance control is unavailable")
        admit_writer(
            control,
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=control.engine_digest,
            expected_epoch=control.epoch,
            recovery_operation_id=operation_id,
        )
        current_pin = read_engine_pin(common_dir, checkout_root=repo_root, require_control_match=False)
        if current_pin == prior and control.engine_digest == prior.distribution_digest:
            replace_engine_pin(common_dir, prior=prior, next_engine=next_engine)
        elif current_pin != next_engine:
            raise ValueError("engine handover locator is ambiguous")
        if control.engine_digest == prior.distribution_digest and control.epoch == record.control_epoch:
            store_control(
                common_dir, _rotated_control(control, next_engine.distribution_digest), expected_epoch=control.epoch
            )
        elif control.engine_digest != next_engine.distribution_digest or control.epoch != record.control_epoch + 1:
            raise ValueError("engine handover control transition is ambiguous")
        completed = replace(record, phase="committed")
        write_engine_handover(common_dir, completed)
        return completed


def rollback_engine_handover(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    operation_id: str,
    expected_next_digest: str,
    lock_timeout: float = 0.0,
) -> EngineHandoverRecord:
    """Restore the prior engine only when the handover epoch is still current."""
    record = read_engine_handover(common_dir, operation_id)
    if record.next_digest != expected_next_digest:
        raise ValueError("engine handover rollback requires its recorded new engine")
    if record.phase == "rolled-back":
        return record
    with writer_transaction(common_dir, worktree_ids=record.targets, timeout=lock_timeout):
        record = read_engine_handover(common_dir, operation_id)
        if record.next_digest != expected_next_digest:
            raise ValueError("engine handover rollback engine changed")
        if record.phase not in {"prepared", "committed", "rolling-back"}:
            raise ValueError("engine handover record cannot be rolled back")
        if (
            verify_source_update(
                repo_root=repo_root, common_dir=common_dir, update_id=record.source_update_id, bundle=None
            )
            != record.targets
        ):
            raise ValueError("engine handover source inventory changed")
        prior = _engine_from_record(record, repo_root=repo_root, prior=True)
        next_engine = _engine_from_record(record, repo_root=repo_root, prior=False)
        control = load_control(common_dir)
        if control is None or control.mode != "maintenance":
            raise ValueError("engine handover maintenance control is unavailable")
        admit_writer(
            control,
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=control.engine_digest,
            expected_epoch=control.epoch,
            maintenance_command="installation.update" if record.phase == "committed" else None,
            recovery_operation_id=operation_id if record.phase != "committed" else None,
        )
        if (control.engine_digest, control.epoch) not in {
            (prior.distribution_digest, record.control_epoch),
            (prior.distribution_digest, record.control_epoch + 2),
            (next_engine.distribution_digest, record.control_epoch + 1),
        }:
            raise ValueError("engine handover control epoch changed after the operation")
        if record.phase != "rolling-back":
            record = replace(record, phase="rolling-back")
            write_engine_handover(common_dir, record)
        current_pin = read_engine_pin(common_dir, checkout_root=repo_root, require_control_match=False)
        if current_pin == next_engine:
            replace_engine_pin(common_dir, prior=next_engine, next_engine=prior)
        elif current_pin != prior:
            raise ValueError("engine handover locator is ambiguous")
        if control.engine_digest == next_engine.distribution_digest:
            store_control(
                common_dir, _rotated_control(control, prior.distribution_digest), expected_epoch=control.epoch
            )
        completed = replace(record, phase="rolled-back")
        write_engine_handover(common_dir, completed)
        return completed
