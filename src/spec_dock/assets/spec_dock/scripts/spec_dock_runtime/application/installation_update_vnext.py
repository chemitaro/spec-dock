"""Coordinate one journaled tooling update across every registered worktree."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import re
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
from spec_dock.runtime_loader import EnginePin, VerifiedEngine, verify_engine_pin, write_engine_pin
from spec_dock_runtime.application.engine_handover_vnext import verify_source_update
from spec_dock_runtime.application.installation_vnext import (
    InstallationGroup,
    InstalledWorktree,
    inspect_installation_group,
    installation_targets,
)
from spec_dock_runtime.cli.admission import admit_writer
from spec_dock_runtime.infra.control_store import (
    WORKSPACE_SCHEMA,
    WRITER_PROTOCOL,
    ControlState,
    WorktreeRegistration,
    load_control,
    store_control,
)
from spec_dock_runtime.infra.engine_handover_store import read_engine_handover
from spec_dock_runtime.infra.finalization_store import (
    FinalizationRecord,
    new_finalization,
    pending_finalizations,
    read_finalization,
    write_finalization,
)
from spec_dock_runtime.infra.git_cli import worktree_list
from spec_dock_runtime.infra.installation_group_store import pending_installation_groups
from spec_dock_runtime.infra.json_store import read_guarded_json
from spec_dock_runtime.infra.migration_journal import pending_migrations
from spec_dock_runtime.infra.operation_journal import JournalStore
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


def _commit_update_matches_engine(*, repo_root: Path, common_dir: Path, version: str, engine_digest: str) -> bool:
    updates = common_dir / "spec-dock/control/installations"
    if updates.is_symlink() or not updates.is_dir():
        return False
    handovers = common_dir / "spec-dock/control/engine-handovers"
    if handovers.is_symlink():
        raise ValueError("engine handover record directory is unsafe")
    approved_updates: set[str] = set()
    if handovers.is_dir():
        for path in sorted(handovers.glob("*.json")):
            record = read_engine_handover(common_dir, path.stem)
            if record.phase == "committed" and record.next_digest == engine_digest:
                approved_updates.add(record.source_update_id)
    for directory in sorted(updates.iterdir()):
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError("installation group record directory is unsafe")
        record = read_group_record(common_dir, directory.name)
        if (
            record.action != "update"
            or record.phase != "committed"
            or record.source_commit != version
            or (record.engine_digest != engine_digest and record.operation_id not in approved_updates)
        ):
            continue
        try:
            verify_source_update(
                repo_root=repo_root,
                common_dir=common_dir,
                update_id=record.operation_id,
                bundle=None,
                allow_bootstrap=True,
            )
        except ValueError:
            continue
        return True
    return False


def _verify_finalization_targets(
    group: InstallationGroup, *, repo_root: Path, common_dir: Path, engine_version: str, engine_digest: str
) -> None:
    versions = {item.version for item in group.worktrees}
    if not group.worktrees or len(versions) != 1:
        raise ValueError("registered worktree installation versions differ from the executing engine")
    (version,) = versions
    if version != engine_version and (
        version is None
        or re.fullmatch(r"[0-9a-f]{40}", version) is None
        or not _commit_update_matches_engine(
            repo_root=repo_root, common_dir=common_dir, version=version, engine_digest=engine_digest
        )
    ):
        raise ValueError("registered worktree installation versions differ from the executing engine")
    for item in group.worktrees:
        loaded = read_guarded_json(Path(item.root) / "spec-dock/workspace.json")
        if (
            loaded is None
            or not isinstance(loaded[0], dict)
            or (
                loaded[0].get("schema_version") != WORKSPACE_SCHEMA
                or loaded[0].get("writer_protocol") != WRITER_PROTOCOL
            )
        ):
            raise ValueError(f"registered worktree schema is not ready: {item.id}")


def plan_installation_finalization(
    *, repo_root: Path, common_dir: Path, engine_digest: str, engine_version: str
) -> InstallationGroup:
    """Read-only eligibility snapshot for the final maintenance transition."""
    group = inspect_installation_group(repo_root=repo_root, common_dir=common_dir)
    control = load_control(common_dir)
    if control is None or control.mode != "maintenance" or control.engine_digest != engine_digest:
        raise ValueError("installation group is not in this engine's maintenance state")
    if not _can_restore_ready(control):
        raise ValueError("registered worktree protocol differs from the engine")
    if (
        pending_installation_groups(common_dir)
        or pending_migrations(common_dir)
        or pending_finalizations(common_dir)
        or JournalStore(common_dir).pending()
    ):
        raise ValueError("installation finalization has unresolved operations")
    _verify_finalization_targets(
        group, repo_root=repo_root, common_dir=common_dir, engine_version=engine_version, engine_digest=engine_digest
    )
    return group


def finalize_installation_group(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    engine_version: str,
    lock_timeout: float = 0.0,
) -> FinalizationRecord:
    """Journal the final maintenance-to-ready transition for one complete group."""
    group = inspect_installation_group(repo_root=repo_root, common_dir=common_dir)
    with writer_transaction(common_dir, worktree_ids=tuple(item.id for item in group.worktrees), timeout=lock_timeout):
        if inspect_installation_group(repo_root=repo_root, common_dir=common_dir) != group:
            raise ValueError("installation group changed before finalization")
        control = load_control(common_dir)
        admit_writer(
            control,
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
            maintenance_command="installation.update",
        )
        if control is None or control.mode != "maintenance" or not _can_restore_ready(control):
            raise ValueError("installation group is not ready to leave maintenance")
        if pending_finalizations(common_dir):
            raise ValueError("a finalization attempt requires explicit recovery")
        _verify_finalization_targets(
            group,
            repo_root=repo_root,
            common_dir=common_dir,
            engine_version=engine_version,
            engine_digest=engine_digest,
        )
        record = new_finalization(
            common_dir,
            control_epoch=control.epoch,
            engine_digest=engine_digest,
            targets=tuple(item.id for item in group.worktrees),
        )
        write_finalization(common_dir, record, create=True)
        store_control(common_dir, replace(control, mode="ready", epoch=control.epoch + 1), expected_epoch=control.epoch)
        completed = replace(record, phase="committed")
        write_finalization(common_dir, completed)
        return completed


def resume_installation_finalization(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    engine_version: str,
    operation_id: str,
    lock_timeout: float = 0.0,
) -> FinalizationRecord:
    """Finish the same prepared transition after observing control and all targets."""
    record = read_finalization(common_dir, operation_id)
    if record.phase != "prepared" or record.engine_digest != engine_digest:
        raise ValueError("finalization recovery record does not match this engine")
    with writer_transaction(common_dir, worktree_ids=record.targets, timeout=lock_timeout):
        if read_finalization(common_dir, operation_id) != record:
            raise ValueError("finalization record changed before recovery")
        control = load_control(common_dir)
        if control is None or control.mode not in {"maintenance", "ready"}:
            raise ValueError("finalization control is unavailable")
        admit_writer(
            control,
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=control.epoch,
            recovery_operation_id=operation_id,
        )
        group = inspect_installation_group(repo_root=repo_root, common_dir=common_dir)
        if tuple(item.id for item in group.worktrees) != record.targets or not _can_restore_ready(control):
            raise ValueError("finalization worktree inventory changed")
        _verify_finalization_targets(
            group,
            repo_root=repo_root,
            common_dir=common_dir,
            engine_version=engine_version,
            engine_digest=engine_digest,
        )
        if control.mode == "maintenance" and control.epoch == record.control_epoch:
            store_control(
                common_dir, replace(control, mode="ready", epoch=control.epoch + 1), expected_epoch=control.epoch
            )
        elif control.mode != "ready" or control.epoch != record.control_epoch + 1:
            raise ValueError("finalization control transition is ambiguous")
        completed = replace(record, phase="committed")
        write_finalization(common_dir, completed)
        return completed


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
    common_dir: Path, record: InstallationGroupRecord, bundle: VerifiedBundle | None, *, recover_stage: bool = False
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
                action=record.action,
                bundle=bundle,
                operation_id=target.child_operation_id,
            )
        if (
            child.target != target.root
            or child.action != record.action
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
            or child.action != record.action
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


def _fresh_group(repo_root: Path, common_dir: Path, engine_digest: str) -> InstallationGroup:
    """Fix the real Git worktree inventory before publishing initial control."""
    control = load_control(common_dir)
    if control is not None and (control.mode != "uninitialized" or control.engine_digest != engine_digest):
        raise ValueError("repository already has installation control")
    records = worktree_list(repo_root)
    roots: set[Path] = set()
    targets: list[InstalledWorktree] = []
    for record in records:
        root = record.path
        if record.bare or not root.is_absolute() or root.is_symlink() or not root.is_dir():
            raise ValueError("Git worktree inventory contains an unavailable worktree")
        if root.resolve(strict=True) != root or root in roots:
            raise ValueError("Git worktree inventory has an unstable path")
        roots.add(root)
        worktree_id = initial_worktree_id(root)
        if (root / "spec-dock/spec-dock.version").exists():
            raise ValueError("installation init requires every worktree to be uninstalled")
        targets.append(
            InstalledWorktree(worktree_id, str(root), None, WORKSPACE_SCHEMA, WRITER_PROTOCOL, engine_digest, True)
        )
    if repo_root not in roots or not targets:
        raise ValueError("installation init target is not a Git worktree root")
    if len({item.id for item in targets}) != len(targets):
        raise ValueError("installation worktree identity collision")
    targets.sort(key=lambda item: item.id)
    if control is not None and tuple((item.id, item.root) for item in targets) != tuple(
        (item.id, item.root) for item in control.worktrees
    ):
        raise ValueError("uninitialized installation worktree inventory changed")
    return InstallationGroup(str(common_dir), 0 if control is None else control.epoch, "uninitialized", tuple(targets))


def _check_init_inventory(repo_root: Path, record: InstallationGroupRecord) -> None:
    observed: set[tuple[str, str]] = set()
    for item in worktree_list(repo_root):
        root = item.path
        if item.bare or root.is_symlink() or not root.is_dir() or root.resolve(strict=True) != root:
            raise ValueError("installation init worktree inventory is unavailable")
        worktree_id = initial_worktree_id(root)
        observed.add((worktree_id, str(root)))
    fixed = {(target.worktree_id, target.root) for target in record.targets}
    if observed != fixed or len(observed) != len(record.targets):
        raise ValueError("installation init worktree inventory changed")


def initial_worktree_id(root: Path) -> str:
    return "main" if (root / ".git").is_dir() else f"wt-{hashlib.sha256(str(root).encode()).hexdigest()[:16]}"


def _legacy_group(repo_root: Path, common_dir: Path, engine_digest: str) -> InstallationGroup:
    """Inventory installed legacy worktrees without trusting their runtime code."""
    targets: list[InstalledWorktree] = []
    for root in installation_targets(repo_root):
        version_path = root / "spec-dock/spec-dock.version"
        workspace_path = root / "spec-dock/workspace.json"
        if version_path.is_symlink() or workspace_path.is_symlink():
            raise ValueError("legacy installation metadata is redirected")
        try:
            version = version_path.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeError) as error:
            raise ValueError("legacy installation version is unavailable") from error
        if not version or "\n" in version or "\r" in version:
            raise ValueError("legacy installation version is invalid")
        try:
            workspace = json.loads(workspace_path.read_text(encoding="utf-8")) if workspace_path.exists() else {}
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ValueError("legacy workspace marker is invalid") from error
        if not isinstance(workspace, dict) or workspace.get("schema_version", 1) not in (1, 3):
            raise ValueError("legacy workspace schema requires explicit migration inspection")
        schema = workspace.get("schema_version", 1)
        protocol = workspace.get("writer_protocol", "legacy")
        if not isinstance(protocol, str) or not protocol:
            raise ValueError("legacy writer protocol is invalid")
        targets.append(
            InstalledWorktree(initial_worktree_id(root), str(root), version, schema, protocol, engine_digest, True)
        )
    targets.sort(key=lambda item: item.id)
    if len({item.id for item in targets}) != len(targets):
        raise ValueError("legacy worktree identities collide")
    return InstallationGroup(str(common_dir), 0, "uninitialized", tuple(targets))


def inspect_legacy_installation(repo_root: Path, common_dir: Path, engine_digest: str) -> InstallationGroup:
    """Read legacy installation targets without publishing writer control."""
    control = load_control(common_dir)
    if control is not None and control.mode != "uninitialized":
        raise ValueError("installation is already controlled")
    group = _legacy_group(repo_root, common_dir, engine_digest)
    return replace(group, control_epoch=0 if control is None else control.epoch)


def _initial_control(record: InstallationGroupRecord) -> ControlState:
    registrations = tuple(
        WorktreeRegistration(
            target.worktree_id, target.root, WORKSPACE_SCHEMA, WRITER_PROTOCOL, record.engine_digest, True
        )
        for target in record.targets
    )
    return ControlState(
        WORKSPACE_SCHEMA,
        WRITER_PROTOCOL,
        record.control_epoch + 1,
        record.engine_digest,
        "maintenance",
        registrations,
    )


def plan_init_installation_group(*, repo_root: Path, common_dir: Path, engine_digest: str) -> InstallationGroup:
    """Inspect a fresh group without creating control or journals."""
    group = _fresh_group(repo_root, common_dir, engine_digest)
    if pending_installation_groups(common_dir):
        raise ValueError("installation init has a pending operation; resume or rollback it")
    return group


def bind_installation_engine(*, repo_root: Path, common_dir: Path, engine: VerifiedEngine) -> None:
    """Recheck the external distribution before the first control transition."""
    checked = verify_engine_pin(
        EnginePin(engine.executable, engine.distribution_root, engine.distribution_digest),
        checkout_root=repo_root,
    )
    if checked != engine:
        raise ValueError("executing engine identity changed")
    write_engine_pin(common_dir, checked)


def init_installation_group(
    *, repo_root: Path, common_dir: Path, engine_digest: str, bundle: VerifiedBundle, lock_timeout: float = 0.0
) -> InstallationGroupRecord:
    """Journal a fixed fresh distribution across every Git worktree."""
    before = plan_init_installation_group(repo_root=repo_root, common_dir=common_dir, engine_digest=engine_digest)
    _check_bundle(before, bundle)
    with writer_transaction(common_dir, worktree_ids=tuple(item.id for item in before.worktrees), timeout=lock_timeout):
        if _fresh_group(repo_root, common_dir, engine_digest) != before or pending_installation_groups(common_dir):
            raise ValueError("installation inventory changed before the init lock")
        group_id = uuid4().hex
        record = InstallationGroupRecord(
            group_id,
            "init",
            str(common_dir),
            before.control_epoch,
            engine_digest,
            bundle.source.commit,
            bundle.digest,
            False,
            _fixed_targets(before, group_id),
            "preparing",
        )
        write_group_record(common_dir, record, create=True)
        try:
            previous = load_control(common_dir)
            store_control(
                common_dir,
                _initial_control(record),
                expected_epoch=None if previous is None else previous.epoch,
            )
            record = _stage_missing(common_dir, record, bundle)
            record = _apply_children(common_dir, record)
            return _commit_group(common_dir, record)
        except Exception as error:
            failed = replace(read_group_record(common_dir, group_id), phase="recovery-required", error=str(error))
            write_group_record(common_dir, failed)
            raise


def resume_init_installation_group(
    *,
    repo_root: Path,
    common_dir: Path,
    engine_digest: str,
    operation_id: str,
    bundle: VerifiedBundle,
    lock_timeout: float = 0.0,
) -> InstallationGroupRecord:
    """Complete a fixed fresh install after a stopped staging or replacement phase."""
    record = read_group_record(common_dir, operation_id)
    if record.action != "init" or record.phase in {"committed", "rolled-back"} or record.engine_digest != engine_digest:
        raise ValueError("installation init group is not resumable")
    _check_init_inventory(repo_root, record)
    group = InstallationGroup(
        str(common_dir),
        record.control_epoch,
        "uninitialized",
        tuple(
            InstalledWorktree(item.worktree_id, item.root, None, WORKSPACE_SCHEMA, WRITER_PROTOCOL, engine_digest, True)
            for item in record.targets
        ),
    )
    _check_bundle(group, bundle, source_commit=record.source_commit, source_digest=record.source_digest)
    with writer_transaction(
        common_dir, worktree_ids=tuple(item.worktree_id for item in record.targets), timeout=lock_timeout
    ):
        record = read_group_record(common_dir, operation_id)
        if record.action != "init" or record.phase in {"committed", "rolled-back"}:
            raise ValueError("installation init group is not resumable")
        _check_init_inventory(repo_root, record)
        control = load_control(common_dir)
        expected = _initial_control(record)
        if control is None:
            if record.control_epoch != 0:
                raise ValueError("installation init lost its previous control")
            store_control(common_dir, expected, expected_epoch=None)
        elif control.mode == "uninitialized" and control.epoch == record.control_epoch:
            store_control(common_dir, expected, expected_epoch=control.epoch)
        elif control != expected:
            if not (
                control.mode == "ready"
                and control.epoch == record.control_epoch + 2
                and replace(control, mode="maintenance", epoch=record.control_epoch + 1) == expected
                and all(item.completed for item in record.targets)
            ):
                raise ValueError("installation init control changed during recovery")
        try:
            record = _stage_missing(common_dir, record, bundle, recover_stage=True)
            record = _apply_children(common_dir, record)
            return _commit_group(common_dir, record)
        except Exception as error:
            failed = replace(read_group_record(common_dir, operation_id), phase="recovery-required", error=str(error))
            write_group_record(common_dir, failed)
            raise


def rollback_init_installation_group(
    *, repo_root: Path, common_dir: Path, engine_digest: str, operation_id: str, lock_timeout: float = 0.0
) -> InstallationGroupRecord:
    """Restore untouched pre-init paths in every worktree and disable the new writer."""
    record = read_group_record(common_dir, operation_id)
    if record.action != "init" or record.engine_digest != engine_digest:
        raise ValueError("installation rollback target is not an init operation")
    if record.phase == "rolled-back":
        return record
    _check_init_inventory(repo_root, record)
    with writer_transaction(
        common_dir, worktree_ids=tuple(item.worktree_id for item in record.targets), timeout=lock_timeout
    ):
        record = read_group_record(common_dir, operation_id)
        if record.action != "init" or record.phase == "rolled-back":
            raise ValueError("installation init rollback state changed")
        _check_init_inventory(repo_root, record)
        control = load_control(common_dir)
        if control is not None:
            allowed = {
                ("maintenance", record.control_epoch + 1),
                ("ready", record.control_epoch + 2),
                ("maintenance", record.control_epoch + 3),
                ("uninitialized", record.control_epoch + 2),
                ("uninitialized", record.control_epoch + 4),
            }
            if control.engine_digest != engine_digest or (control.mode, control.epoch) not in allowed:
                raise ValueError("installation init control changed before rollback")
        children: list[InstallationRecord | None] = []
        for target in record.targets:
            assert target.child_operation_id is not None
            journal_root = _child_root(common_dir, record.operation_id, target.worktree_id)
            child_path = journal_root / "installations" / target.child_operation_id / "record.json"
            if not os.path.lexists(child_path):
                if target.completed:
                    raise ValueError("completed installation child has no journal")
                children.append(None)
                continue
            child = preflight_rollback_installation(journal_root, target.child_operation_id, allow_committed=True)
            if (
                child.action != "init"
                or child.target != target.root
                or child.source_commit != record.source_commit
                or child.source_digest != record.source_digest
            ):
                raise ValueError("installation init child identity changed")
            children.append(child)
        if control is not None and control.mode == "ready":
            store_control(
                common_dir, replace(control, mode="maintenance", epoch=control.epoch + 1), expected_epoch=control.epoch
            )
        try:
            for target, rollback_child in reversed(tuple(zip(record.targets, children, strict=True))):
                if rollback_child is None or rollback_child.phase == "rolled-back":
                    continue
                assert target.child_operation_id is not None
                rollback_installation(
                    _child_root(common_dir, record.operation_id, target.worktree_id),
                    target.child_operation_id,
                    enter_maintenance=lambda _child: None,
                    allow_committed=True,
                )
            current = load_control(common_dir)
            if current is not None and current.mode != "uninitialized":
                if current.mode != "maintenance" or current.engine_digest != engine_digest:
                    raise ValueError("installation init maintenance control changed")
                store_control(
                    common_dir,
                    replace(current, mode="uninitialized", epoch=current.epoch + 1),
                    expected_epoch=current.epoch,
                )
            rolled_back = replace(record, phase="rolled-back", error=None)
            write_group_record(common_dir, rolled_back)
            return rolled_back
        except Exception as error:
            failed = replace(read_group_record(common_dir, operation_id), phase="recovery-required", error=str(error))
            write_group_record(common_dir, failed)
            raise


def update_installation_group(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    bundle: VerifiedBundle,
    keep_maintenance: bool,
    engine_pin: VerifiedEngine | None = None,
    lock_timeout: float = 0.0,
) -> InstallationGroupRecord:
    """Stage every target before replacing one, and preserve recovery on failure."""
    original_control = load_control(common_dir)
    bootstrap = original_control is None or original_control.mode == "uninitialized"
    if bootstrap:
        if not keep_maintenance or engine_pin is None or engine_pin.distribution_digest != engine_digest:
            raise ValueError("legacy installation update requires --maintenance and a verified external engine")
        before = _legacy_group(repo_root, common_dir, engine_digest)
        if original_control is not None:
            if original_control.engine_digest != engine_digest or tuple(
                (item.id, item.root) for item in original_control.worktrees
            ) != tuple((item.id, item.root) for item in before.worktrees):
                raise ValueError("uninitialized installation inventory changed")
            before = replace(before, control_epoch=original_control.epoch)
        if pending_installation_groups(common_dir):
            raise ValueError("legacy installation has an unfinished group operation")
    else:
        before = inspect_installation_group(repo_root=repo_root, common_dir=common_dir)
    if any(item.version is None for item in before.worktrees):
        raise ValueError("installation group contains an unversioned target")
    if bundle.source.commit is None:
        raise ValueError("installation update requires a pinned source commit")
    _check_bundle(before, bundle)
    with writer_transaction(common_dir, worktree_ids=tuple(item.id for item in before.worktrees), timeout=lock_timeout):
        current = (
            replace(_legacy_group(repo_root, common_dir, engine_digest), control_epoch=before.control_epoch)
            if bootstrap
            else inspect_installation_group(repo_root=repo_root, common_dir=common_dir)
        )
        if current != before:
            raise ValueError("installation group changed before the update lock")
        control = load_control(common_dir)
        if bootstrap:
            if control != original_control or expected_epoch != before.control_epoch:
                raise ValueError("legacy installation control changed before update")
            if worktree_id not in {item.id for item in current.worktrees}:
                raise ValueError("legacy installation caller is not a registered worktree")
        else:
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
            before.control_epoch,
            engine_digest,
            bundle.source.commit,
            bundle.digest,
            keep_maintenance,
            _fixed_targets(current, group_id),
            "preparing",
            bootstrap=bootstrap,
        )
        write_group_record(common_dir, record, create=True)
        try:
            if bootstrap:
                assert engine_pin is not None
                bind_installation_engine(repo_root=repo_root, common_dir=common_dir, engine=engine_pin)
                registrations = tuple(
                    WorktreeRegistration(
                        item.id, item.root, item.schema_version, item.writer_protocol, engine_digest, True
                    )
                    for item in current.worktrees
                )
                store_control(
                    common_dir,
                    ControlState(
                        WORKSPACE_SCHEMA,
                        WRITER_PROTOCOL,
                        before.control_epoch + 1,
                        engine_digest,
                        "maintenance",
                        registrations,
                    ),
                    expected_epoch=None if control is None else control.epoch,
                )
            else:
                assert control is not None
                store_control(
                    common_dir,
                    replace(control, mode="maintenance", epoch=control.epoch + 1),
                    expected_epoch=control.epoch,
                )
            record = _stage_missing(common_dir, record, bundle)
            record = _apply_children(common_dir, record)
            return _commit_group(common_dir, record)
        except Exception as error:
            record = replace(read_group_record(common_dir, group_id), phase="recovery-required", error=str(error))
            write_group_record(common_dir, record)
            raise


def uninstall_installation_group(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    lock_timeout: float = 0.0,
) -> InstallationGroupRecord:
    """Remove only managed tooling across the fixed registered worktree group."""
    before = inspect_installation_group(repo_root=repo_root, common_dir=common_dir)
    if any(item.version is None for item in before.worktrees):
        raise ValueError("installation group contains an unversioned target")
    with writer_transaction(common_dir, worktree_ids=tuple(item.id for item in before.worktrees), timeout=lock_timeout):
        if inspect_installation_group(repo_root=repo_root, common_dir=common_dir) != before:
            raise ValueError("installation group changed before the uninstall lock")
        control = load_control(common_dir)
        assert control is not None
        admit_writer(
            control,
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
            maintenance_command="installation.uninstall",
        )
        group_id = uuid4().hex
        record = InstallationGroupRecord(
            group_id,
            "uninstall",
            str(common_dir),
            control.epoch,
            engine_digest,
            None,
            None,
            True,
            _fixed_targets(before, group_id),
            "preparing",
        )
        write_group_record(common_dir, record, create=True)
        try:
            store_control(
                common_dir, replace(control, mode="maintenance", epoch=control.epoch + 1), expected_epoch=control.epoch
            )
            record = _stage_missing(common_dir, record, None)
            record = _apply_children(common_dir, record)
            return _commit_group(common_dir, record)
        except Exception as error:
            failed = replace(read_group_record(common_dir, group_id), phase="recovery-required", error=str(error))
            write_group_record(common_dir, failed)
            raise


def resume_installation_group(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    operation_id: str,
    bundle: VerifiedBundle,
    engine_pin: VerifiedEngine | None = None,
    lock_timeout: float = 0.0,
) -> InstallationGroupRecord:
    """Resume only the fixed targets and source captured by the group journal."""
    record = read_group_record(common_dir, operation_id)
    if record.action != "update" or record.phase in {"committed", "rolled-back"}:
        raise ValueError("installation group is not resumable")
    control_before = load_control(common_dir)
    legacy_before = record.bootstrap and (control_before is None or control_before.mode == "uninitialized")
    group = (
        _legacy_group(repo_root, common_dir, engine_digest)
        if legacy_before
        else inspect_installation_group(repo_root=repo_root, common_dir=common_dir)
    )
    if tuple((item.id, item.root) for item in group.worktrees) != tuple(
        (item.worktree_id, item.root) for item in record.targets
    ):
        raise ValueError("installation recovery target inventory changed")
    _check_bundle(group, bundle, source_commit=record.source_commit, source_digest=record.source_digest)
    with writer_transaction(common_dir, worktree_ids=tuple(item.id for item in group.worktrees), timeout=lock_timeout):
        record = read_group_record(common_dir, operation_id)
        current = (
            _legacy_group(repo_root, common_dir, engine_digest)
            if legacy_before
            else inspect_installation_group(repo_root=repo_root, common_dir=common_dir)
        )
        if current != group:
            raise ValueError("installation recovery inventory changed before the lock")
        control = load_control(common_dir)
        if legacy_before:
            if (
                control != control_before
                or engine_pin is None
                or engine_pin.distribution_digest != engine_digest
                or record.engine_digest != engine_digest
                or worktree_id not in {item.id for item in current.worktrees}
            ):
                raise ValueError("legacy installation recovery identity changed")
            bind_installation_engine(repo_root=repo_root, common_dir=common_dir, engine=engine_pin)
            registrations = tuple(
                WorktreeRegistration(item.id, item.root, item.schema_version, item.writer_protocol, engine_digest, True)
                for item in current.worktrees
            )
            store_control(
                common_dir,
                ControlState(
                    WORKSPACE_SCHEMA,
                    WRITER_PROTOCOL,
                    record.control_epoch + 1,
                    engine_digest,
                    "maintenance",
                    registrations,
                ),
                expected_epoch=None if control is None else control.epoch,
            )
        else:
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
                    common_dir,
                    replace(control, mode="maintenance", epoch=control.epoch + 1),
                    expected_epoch=control.epoch,
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


def resume_uninstall_installation_group(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    operation_id: str,
    lock_timeout: float = 0.0,
) -> InstallationGroupRecord:
    """Resume fixed uninstall targets from local journal bytes without a source bundle."""
    record = read_group_record(common_dir, operation_id)
    if record.action != "uninstall" or record.phase in {"committed", "rolled-back"}:
        raise ValueError("installation uninstall group is not resumable")
    group = inspect_installation_group(repo_root=repo_root, common_dir=common_dir)
    if tuple((item.id, item.root) for item in group.worktrees) != tuple(
        (item.worktree_id, item.root) for item in record.targets
    ):
        raise ValueError("installation recovery target inventory changed")
    with writer_transaction(common_dir, worktree_ids=tuple(item.id for item in group.worktrees), timeout=lock_timeout):
        record = read_group_record(common_dir, operation_id)
        if record.action != "uninstall" or record.phase in {"committed", "rolled-back"}:
            raise ValueError("installation uninstall group is not resumable")
        if inspect_installation_group(repo_root=repo_root, common_dir=common_dir) != group:
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
        elif control.mode != "maintenance" or control.epoch < record.control_epoch + 1:
            raise ValueError("installation control is not at a recoverable epoch")
        try:
            record = _stage_missing(common_dir, record, None, recover_stage=True)
            record = _apply_children(common_dir, record)
            return _commit_group(common_dir, record)
        except Exception as error:
            failed = replace(read_group_record(common_dir, operation_id), phase="recovery-required", error=str(error))
            write_group_record(common_dir, failed)
            raise


def rollback_installation_group(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    operation_id: str,
    expected_action: str = "update",
    lock_timeout: float = 0.0,
) -> InstallationGroupRecord:
    """Restore a pending or untouched committed update/uninstall group."""
    record = read_group_record(common_dir, operation_id)
    if (
        record.action != expected_action
        or expected_action not in {"update", "uninstall"}
        or (record.phase == "committed" and not record.keep_maintenance)
    ):
        raise ValueError("installation group is not rollback eligible")
    if record.phase == "rolled-back":
        return record
    control_before = load_control(common_dir)
    legacy_before = record.bootstrap and (control_before is None or control_before.mode == "uninitialized")
    group = (
        _legacy_group(repo_root, common_dir, engine_digest)
        if legacy_before
        else inspect_installation_group(repo_root=repo_root, common_dir=common_dir)
    )
    if tuple((item.id, item.root) for item in group.worktrees) != tuple(
        (item.worktree_id, item.root) for item in record.targets
    ):
        raise ValueError("installation rollback target inventory changed")
    with writer_transaction(common_dir, worktree_ids=tuple(item.id for item in group.worktrees), timeout=lock_timeout):
        record = read_group_record(common_dir, operation_id)
        if (
            record.action != expected_action
            or expected_action not in {"update", "uninstall"}
            or (record.phase == "committed" and not record.keep_maintenance)
        ):
            raise ValueError("installation group is not rollback eligible")
        current_group = (
            _legacy_group(repo_root, common_dir, engine_digest)
            if legacy_before
            else inspect_installation_group(repo_root=repo_root, common_dir=common_dir)
        )
        if current_group != group:
            raise ValueError("installation rollback inventory changed before the lock")
        control = load_control(common_dir)
        if legacy_before:
            if control != control_before or record.engine_digest != engine_digest:
                raise ValueError("legacy installation rollback control changed")
        elif control is None:
            raise ValueError("installation control is missing")
        elif record.phase == "committed":
            if control.mode != "maintenance" or control.epoch != record.control_epoch + 1:
                raise ValueError("installation maintenance state changed after completion")
            admit_writer(
                control,
                common_dir=common_dir,
                worktree_id=worktree_id,
                engine_digest=engine_digest,
                expected_epoch=control.epoch,
                maintenance_command=f"installation.{record.action}",
            )
        else:
            assert control is not None
            admit_writer(
                control,
                common_dir=common_dir,
                worktree_id=worktree_id,
                engine_digest=engine_digest,
                expected_epoch=control.epoch,
                recovery_operation_id=operation_id,
            )
        if legacy_before:
            pass
        elif control is not None and control.epoch == record.control_epoch and control.mode in {"ready", "maintenance"}:
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
                    or child.action != record.action
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
                    enter_maintenance=(
                        (lambda _child: None)
                        if legacy_before
                        else lambda _child: _require_maintenance(
                            common_dir, minimum_epoch=record.control_epoch + 1, engine_digest=engine_digest
                        )
                    ),
                    allow_committed=True,
                )
            if record.bootstrap:
                current_control = load_control(common_dir)
                if current_control is not None and current_control.mode == "maintenance":
                    store_control(
                        common_dir,
                        replace(current_control, mode="uninitialized", epoch=current_control.epoch + 1),
                        expected_epoch=current_control.epoch,
                    )
                elif current_control is not None and current_control.mode != "uninitialized":
                    raise ValueError("bootstrap rollback lost maintenance control")
            rolled_back = replace(record, phase="rolled-back", error=None)
            write_group_record(common_dir, rolled_back)
            return rolled_back
        except Exception as error:
            failed = replace(read_group_record(common_dir, operation_id), phase="recovery-required", error=str(error))
            write_group_record(common_dir, failed)
            raise
