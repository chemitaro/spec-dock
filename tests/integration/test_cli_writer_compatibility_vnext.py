"""Shared writer admission and lock compatibility across linked worktrees."""

from __future__ import annotations

from multiprocessing import Process, Queue
import os
from pathlib import Path
import subprocess
import sys

import pytest

from spec_dock.installation.group_journal import (
    InstallationGroupRecord,
    InstallationTarget,
    write_group_record,
)

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.operation_executor import prepare_operation  # noqa: E402
from spec_dock_runtime.cli.admission import AdmissionError, admit_writer  # noqa: E402
from spec_dock_runtime.infra.control_store import (  # noqa: E402
    ControlState,
    WorktreeRegistration,
    load_control,
    store_control,
)
from spec_dock_runtime.infra.git_cli import git_common_directory  # noqa: E402
from spec_dock_runtime.infra.installation_group_store import pending_installation_groups  # noqa: E402
from spec_dock_runtime.infra.migration_journal import MigrationRecord, write_migration_record  # noqa: E402
from spec_dock_runtime.infra.operation_journal import JournalStore  # noqa: E402
from spec_dock_runtime.infra.writer_lock import (  # noqa: E402
    WorktreeLease,
    WriterLock,
    WriterLockBusy,
    writer_transaction,
)


def _control(*, mode: str = "ready", schema: int = 3, digest: str = "engine-a") -> ControlState:
    return ControlState(
        schema_version=schema,
        writer_protocol="specdock.writer/v1",
        epoch=12,
        engine_digest=digest,
        mode=mode,
        worktrees=(
            WorktreeRegistration("wt-one", "/project/one", 3, "specdock.writer/v1", "engine-a", True),
            WorktreeRegistration("wt-two", "/project/two", 3, "specdock.writer/v1", "engine-a", True),
        ),
    )


def test_all_registered_worktrees_must_use_same_writer_protocol(tmp_path: Path) -> None:
    admit_writer(_control(), common_dir=tmp_path, worktree_id="wt-one", engine_digest="engine-a", expected_epoch=12)
    bad = _control()
    incompatible = WorktreeRegistration("wt-two", "/project/two", 2, "specdock.writer/v0", "engine-a", True)
    bad = ControlState(
        bad.schema_version,
        bad.writer_protocol,
        bad.epoch,
        bad.engine_digest,
        bad.mode,
        (bad.worktrees[0], incompatible),
    )
    with pytest.raises(AdmissionError, match="protocol"):
        admit_writer(bad, common_dir=tmp_path, worktree_id="wt-one", engine_digest="engine-a", expected_epoch=12)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"worktree_id": "unregistered"},
        {"engine_digest": "engine-old"},
        {"expected_epoch": 11},
    ],
)
def test_unregistered_or_stale_writer_is_rejected(tmp_path: Path, kwargs: dict[str, object]) -> None:
    valid: dict[str, object] = {
        "common_dir": tmp_path,
        "worktree_id": "wt-one",
        "engine_digest": "engine-a",
        "expected_epoch": 12,
    }
    valid.update(kwargs)
    with pytest.raises(AdmissionError):
        admit_writer(_control(), **valid)


def test_only_explicit_blocking_recovery_operations_stop_unrelated_writes(tmp_path: Path) -> None:
    admit_writer(_control(), common_dir=tmp_path, worktree_id="wt-one", engine_digest="engine-a", expected_epoch=12)
    blocking = prepare_operation(
        command="work.start",
        fixed_targets={"target": "iss-00409"},
        request_fingerprint="sha256:start",
        before_revisions={},
        engine_digest="engine-a",
        writer_epoch=12,
        effect_plan=("branch-create",),
    )
    JournalStore(tmp_path).create(blocking)
    with pytest.raises(AdmissionError, match="recovery"):
        admit_writer(
            _control(),
            common_dir=tmp_path,
            worktree_id="wt-two",
            engine_digest="engine-a",
            expected_epoch=12,
        )
    admit_writer(
        _control(),
        common_dir=tmp_path,
        worktree_id="wt-one",
        engine_digest="engine-a",
        expected_epoch=12,
        recovery_operation_id=blocking.operation_id,
    )


def test_pending_installation_group_blocks_other_writers_and_admits_its_recovery(tmp_path: Path) -> None:
    record = InstallationGroupRecord(
        "a" * 32,
        "update",
        str(tmp_path),
        12,
        "b" * 64,
        "c" * 40,
        "d" * 64,
        True,
        (InstallationTarget("wt-one", "/project/one", None, False),),
        "preparing",
    )
    write_group_record(tmp_path, record, create=True)
    assert pending_installation_groups(tmp_path) == (record.operation_id,)
    with pytest.raises(AdmissionError, match="recovery"):
        admit_writer(_control(), common_dir=tmp_path, worktree_id="wt-two", engine_digest="engine-a", expected_epoch=12)
    admit_writer(
        _control(mode="maintenance"),
        common_dir=tmp_path,
        worktree_id="wt-one",
        engine_digest="engine-a",
        expected_epoch=12,
        recovery_operation_id=record.operation_id,
    )


def test_pending_migration_blocks_other_writers_and_admits_its_recovery(tmp_path: Path) -> None:
    record = MigrationRecord(
        "a" * 32,
        str(tmp_path),
        "sha256:" + "b" * 64,
        "sha256:" + "c" * 64,
        "d" * 64,
        12,
        (("wt-one", "/project/one"),),
        (),
        (),
        "prepared",
    )
    write_migration_record(tmp_path, record, create=True)
    with pytest.raises(AdmissionError, match="recovery"):
        admit_writer(_control(), common_dir=tmp_path, worktree_id="wt-two", engine_digest="engine-a", expected_epoch=12)
    admit_writer(
        _control(mode="maintenance"),
        common_dir=tmp_path,
        worktree_id="wt-one",
        engine_digest="engine-a",
        expected_epoch=12,
        recovery_operation_id=record.operation_id,
    )


def test_maintenance_blocks_normal_writer_but_allows_migration(tmp_path: Path) -> None:
    with pytest.raises(AdmissionError, match="maintenance"):
        admit_writer(
            _control(mode="maintenance"),
            common_dir=tmp_path,
            worktree_id="wt-one",
            engine_digest="engine-a",
            expected_epoch=12,
        )
    admit_writer(
        _control(mode="maintenance"),
        common_dir=tmp_path,
        worktree_id="wt-one",
        engine_digest="engine-a",
        expected_epoch=12,
        maintenance_command="workspace.migrate",
    )


def test_maintenance_can_repair_mixed_registered_worktrees(tmp_path: Path) -> None:
    ready = _control()
    outdated = WorktreeRegistration("wt-two", "/project/two", 2, "specdock.writer/v0", "engine-old", True)
    mixed = ControlState(
        ready.schema_version,
        ready.writer_protocol,
        ready.epoch,
        ready.engine_digest,
        "maintenance",
        (ready.worktrees[0], outdated),
    )
    admit_writer(
        mixed,
        common_dir=tmp_path,
        worktree_id="wt-one",
        engine_digest="engine-a",
        expected_epoch=12,
        maintenance_command="workspace.migrate",
    )


def test_control_store_preserves_epoch_and_detects_stale_update(tmp_path: Path) -> None:
    assert load_control(tmp_path) is None
    store_control(tmp_path, _control(), expected_epoch=None)
    assert load_control(tmp_path) == _control()
    next_state = ControlState(3, "specdock.writer/v1", 13, "engine-a", "maintenance", _control().worktrees)
    with pytest.raises(ValueError, match="epoch"):
        store_control(tmp_path, next_state, expected_epoch=11)
    store_control(tmp_path, next_state, expected_epoch=12)
    assert load_control(tmp_path) == next_state


def test_git_common_directory_is_shared_by_linked_worktrees(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    linked = tmp_path / "linked"
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    (repo / "readme.txt").write_text("fixture\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "--", "readme.txt"], check=True, capture_output=True)
    identity = {
        **os.environ,
        "GIT_AUTHOR_NAME": "test",
        "GIT_AUTHOR_EMAIL": "test@example.invalid",
        "GIT_COMMITTER_NAME": "test",
        "GIT_COMMITTER_EMAIL": "test@example.invalid",
    }
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "fixture"], check=True, env=identity, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "worktree", "add", "--detach", str(linked)], check=True, capture_output=True
    )
    assert git_common_directory(repo) == git_common_directory(linked)


def _hold_lock(common_dir: str, ready: Queue[bool]) -> None:
    with WriterLock(Path(common_dir), timeout=0):
        ready.put(True)
        import time

        time.sleep(30)


def test_second_process_times_out_and_killed_owner_releases_lock(tmp_path: Path) -> None:
    ready: Queue[bool] = Queue()
    child = Process(target=_hold_lock, args=(str(tmp_path), ready))
    child.start()
    try:
        assert ready.get(timeout=5) is True
        with pytest.raises(WriterLockBusy), WriterLock(tmp_path, timeout=0):
            pass
    finally:
        child.kill()
        child.join(timeout=5)
    with WriterLock(tmp_path, timeout=0):
        pass


def test_worktree_lease_rejects_recursive_exclusive_use(tmp_path: Path) -> None:
    with (
        WorktreeLease(tmp_path, "wt-one", exclusive=False, timeout=0),
        pytest.raises(WriterLockBusy),
        WorktreeLease(tmp_path, "wt-one", exclusive=True, timeout=0),
    ):
        pass


def test_writer_transaction_takes_sorted_worktree_leases(tmp_path: Path) -> None:
    with (
        writer_transaction(tmp_path, worktree_ids=("wt-two", "wt-one"), timeout=0),
        pytest.raises(WriterLockBusy),
        WorktreeLease(tmp_path, "wt-one", exclusive=True, timeout=0),
    ):
        pass
    with WorktreeLease(tmp_path, "wt-one", exclusive=True, timeout=0):
        pass
