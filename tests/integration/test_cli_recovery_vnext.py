"""D-16 blocking journals survive interruption without blind effect replay."""

from __future__ import annotations

from dataclasses import asdict, replace
import hashlib
import json
from multiprocessing import Process, Queue
import os
from pathlib import Path
import sys
import time
from types import SimpleNamespace

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock.installation.group_journal import (  # noqa: E402
    InstallationGroupRecord,
    InstallationTarget,
    write_group_record,
)
from spec_dock_runtime.application.operation_executor import (  # noqa: E402
    assert_resume_request,
    can_send_effect,
    prepare_operation,
    record_effect_intent,
    record_effect_observation,
    record_effect_result,
)
from spec_dock_runtime.cli import vnext_runtime  # noqa: E402
from spec_dock_runtime.infra import (  # noqa: E402
    failure_receipts,
    operation_journal,
)
from spec_dock_runtime.infra.engine_handover_store import EngineHandoverRecord, write_engine_handover  # noqa: E402
from spec_dock_runtime.infra.finalization_store import FinalizationRecord, write_finalization  # noqa: E402
from spec_dock_runtime.infra.json_store import atomic_write_json, reconcile_atomic_json  # noqa: E402
from spec_dock_runtime.infra.migration_journal import (  # noqa: E402
    MigrationFile,
    MigrationRecord,
    write_migration_record,
)
from spec_dock_runtime.infra.operation_journal import JournalStore  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import _ready_repo  # noqa: E402


def test_migration_prepared_failure_returns_its_authoritative_operation_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    common = _ready_repo(tmp_path)
    repo = common["repo_root"]
    git_common = common["common_dir"]
    worktree_id = common["worktree_id"]
    assert isinstance(repo, Path) and isinstance(git_common, Path) and isinstance(worktree_id, str)
    workspace = repo / "spec-dock/workspace.json"
    before = workspace.read_bytes()
    after = before + b"\n"
    item = MigrationFile(
        str(workspace),
        before,
        after,
        "sha256:" + hashlib.sha256(before).hexdigest(),
        "sha256:" + hashlib.sha256(after).hexdigest(),
    )
    record = MigrationRecord(
        "a" * 32,
        str(git_common),
        "sha256:" + "b" * 64,
        "sha256:" + "c" * 64,
        "d" * 64,
        0,
        ((worktree_id, str(repo)),),
        (item,),
        (),
        "prepared",
    )

    def fail_after_preparation(*args: object, **kwargs: object) -> None:
        write_migration_record(git_common, record, create=True)
        raise OSError("injected after migration preparation")

    monkeypatch.setattr(vnext_runtime, "run_workspace_migrate", fail_after_preparation)
    failed = vnext_runtime.run_vnext(
        ["workspace", "migrate", "--to-schema", "3", "--yes", "--json"],
        invocation_cwd=repo,
        engine_digest="engine-a",
        engine_version="0.2.4",
    )
    payload = json.loads(failed.stdout)
    assert failed.exit_code == 3
    assert payload["operation_id"] == record.operation_id
    assert payload["recovery"]["can_resume"] is True


def test_installation_prepared_failure_returns_group_operation_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    common = _ready_repo(tmp_path)
    repo = common["repo_root"]
    git_common = common["common_dir"]
    worktree_id = common["worktree_id"]
    assert isinstance(repo, Path) and isinstance(git_common, Path) and isinstance(worktree_id, str)
    record = InstallationGroupRecord(
        "b" * 32,
        "update",
        str(git_common),
        0,
        "a" * 64,
        "c" * 40,
        "d" * 64,
        False,
        (InstallationTarget(worktree_id, str(repo), None, False),),
        "preparing",
    )

    def fail_after_preparation(*args: object, **kwargs: object) -> None:
        write_group_record(git_common, record, create=True)
        raise OSError("injected after installation preparation")

    monkeypatch.setattr(vnext_runtime, "run_installation_update", fail_after_preparation)
    failed = vnext_runtime.run_vnext(
        ["installation", "update", "--commit", "c" * 40, "--yes", "--json"],
        invocation_cwd=repo,
        engine_digest="engine-a",
        engine_version="0.2.4",
    )
    payload = json.loads(failed.stdout)
    assert failed.exit_code == 3
    assert payload["operation_id"] == record.operation_id
    assert payload["recovery"]["can_resume"] is True


def test_installation_init_prepared_failure_returns_group_operation_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    common = _ready_repo(tmp_path)
    repo = common["repo_root"]
    git_common = common["common_dir"]
    worktree_id = common["worktree_id"]
    assert isinstance(repo, Path) and isinstance(git_common, Path) and isinstance(worktree_id, str)
    record = InstallationGroupRecord(
        "e" * 32,
        "init",
        str(git_common),
        0,
        "a" * 64,
        None,
        "d" * 64,
        False,
        (InstallationTarget(worktree_id, str(repo), None, False),),
        "preparing",
    )

    def fail_after_preparation(*args: object, **kwargs: object) -> None:
        write_group_record(git_common, record, create=True)
        raise OSError("injected after installation init preparation")

    monkeypatch.setattr(vnext_runtime, "run_installation_init", fail_after_preparation)
    failed = vnext_runtime.run_vnext(
        ["installation", "init", str(repo), "--yes", "--json"],
        invocation_cwd=repo,
        engine_digest="engine-a",
        engine_version="0.2.4",
    )
    payload = json.loads(failed.stdout)
    assert failed.exit_code == 3
    assert payload["operation_id"] == record.operation_id
    assert payload["recovery"]["can_resume"] is True


@pytest.mark.parametrize(
    ("mode", "epoch", "expected_status"),
    [("maintenance", 4, None), ("ready", 5, "succeeded"), ("maintenance", 5, "unknown")],
)
def test_finalization_receipt_observes_control_transition(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str, epoch: int, expected_status: str | None
) -> None:
    record = FinalizationRecord("f" * 32, str(tmp_path), 4, "a" * 64, ("worktree-a",), "prepared")
    write_finalization(tmp_path, record, create=True)
    monkeypatch.setattr(
        failure_receipts,
        "load_control",
        lambda _common: SimpleNamespace(mode=mode, epoch=epoch, engine_digest="a" * 64),
    )
    receipt = next(
        item for item in failure_receipts.pending_failure_receipts(tmp_path) if item.operation_id == record.operation_id
    )
    assert receipt.effect_started is (expected_status is not None)
    assert [effect.status for effect in receipt.effects] == ([] if expected_status is None else [expected_status])


def test_prepared_engine_handover_receipt_does_not_claim_zero_effect(tmp_path: Path) -> None:
    record = EngineHandoverRecord(
        "e" * 32,
        str(tmp_path),
        "a" * 32,
        4,
        str(tmp_path / "old/bin/spec-dock"),
        str(tmp_path / "old"),
        "a" * 64,
        str(tmp_path / "new/bin/spec-dock"),
        str(tmp_path / "new"),
        "b" * 64,
        ("worktree-a",),
        "prepared",
    )
    write_engine_handover(tmp_path, record, create=True)
    receipt = next(
        item for item in failure_receipts.pending_failure_receipts(tmp_path) if item.operation_id == record.operation_id
    )
    assert receipt.effect_started
    assert receipt.effects == (failure_receipts.ReceiptEffect("engine-handover", "unknown", str(tmp_path)),)


def _prepare_and_hold(common_dir: str, command: str, ready: Queue[str]) -> None:
    store = JournalStore(Path(common_dir))
    prepared = prepare_operation(
        command=command,
        fixed_targets={"target": "iss-00409"},
        request_fingerprint="sha256:request",
        before_revisions={"selection": 2},
        engine_digest="engine-a",
        writer_epoch=7,
        effect_plan=("effect",),
    )
    store.create(prepared)
    ready.put(prepared.operation_id)
    time.sleep(30)


@pytest.mark.parametrize(
    "command",
    [
        "scope.create",
        "scope.import",
        "scope.close",
        "scope.reopen",
        "scope.delete",
        "work.start",
        "work.finish",
        "branch.create",
        "workspace.migrate",
        "installation.init",
        "installation.update",
        "installation.uninstall",
    ],
)
def test_every_recoverable_command_has_a_durable_pending_journal(tmp_path: Path, command: str) -> None:
    ready: Queue[str] = Queue()
    child = Process(target=_prepare_and_hold, args=(str(tmp_path), command, ready))
    child.start()
    try:
        operation_id = ready.get(timeout=5)
    finally:
        child.kill()
        child.join(timeout=5)
    store = JournalStore(tmp_path)
    loaded = store.load(operation_id)
    assert loaded.command == command
    assert loaded.terminal_status == "pending"
    assert [item.operation_id for item in store.pending()] == [operation_id]


def test_non_recoverable_command_cannot_create_blocking_journal() -> None:
    with pytest.raises(ValueError, match="blocking journal"):
        prepare_operation(
            command="artifact.create",
            fixed_targets={"target": "iss-00409"},
            request_fingerprint="sha256:request",
            before_revisions={},
            engine_digest="engine-a",
            writer_epoch=7,
            effect_plan=("effect",),
        )


def test_resume_uses_original_fixed_target_and_rejects_changed_request(tmp_path: Path) -> None:
    store = JournalStore(tmp_path)
    prepared = prepare_operation(
        command="work.finish",
        fixed_targets={"target": "iss-00409"},
        request_fingerprint="sha256:request",
        before_revisions={"selection": 2},
        engine_digest="engine-a",
        writer_epoch=7,
        effect_plan=("active-clear",),
    )
    store.create(prepared)
    assert_resume_request(
        store.load(prepared.operation_id),
        command="work.finish",
        fixed_targets={"target": "iss-00409"},
        request_fingerprint="sha256:request",
        current_revisions={"selection": 2},
        engine_digest="engine-a",
        writer_epoch=7,
    )
    with pytest.raises(ValueError, match="fixed target"):
        assert_resume_request(
            store.load(prepared.operation_id),
            command="work.finish",
            fixed_targets={"target": "iss-99999"},
            request_fingerprint="sha256:request",
            current_revisions={"selection": 2},
            engine_digest="engine-a",
            writer_epoch=7,
        )


def test_resume_accepts_recorded_partial_revision_and_rejects_other_changes() -> None:
    prepared = prepare_operation(
        command="work.finish",
        fixed_targets={"target": "iss-00409"},
        request_fingerprint="sha256:finish",
        before_revisions={"selection": 2, "metadata": 4},
        engine_digest="engine-a",
        writer_epoch=7,
        effect_plan=("active-clear", "projection"),
    )
    intent = record_effect_intent(prepared, effect_id="active-clear", kind="local", target="iss-00409")
    partial = record_effect_result(
        intent, effect_id="active-clear", status="succeeded", after_revisions={"selection": 3}
    )
    kwargs = {
        "command": "work.finish",
        "fixed_targets": {"target": "iss-00409"},
        "request_fingerprint": "sha256:finish",
        "engine_digest": "engine-a",
        "writer_epoch": 7,
    }
    assert_resume_request(partial, current_revisions={"selection": 3, "metadata": 4}, **kwargs)
    with pytest.raises(ValueError, match="revision"):
        assert_resume_request(partial, current_revisions={"selection": 4, "metadata": 4}, **kwargs)


def test_verified_local_non_application_can_retry_after_remote_create(tmp_path: Path) -> None:
    store = JournalStore(tmp_path)
    prepared = prepare_operation(
        command="scope.create",
        fixed_targets={"target": "iss-00409"},
        request_fingerprint="sha256:request",
        before_revisions={},
        engine_digest="engine-a",
        writer_epoch=7,
        effect_plan=("github-create", "scaffold"),
    )
    store.create(prepared)
    remote_intent = record_effect_intent(prepared, effect_id="github-create", kind="remote", target="example/repo")
    store.update(remote_intent, expected_sequence=prepared.sequence)
    remote_done = record_effect_result(
        remote_intent, effect_id="github-create", status="succeeded", remote_ref="gh:example/repo#409"
    )
    store.update(remote_done, expected_sequence=remote_intent.sequence)
    local_intent = record_effect_intent(remote_done, effect_id="scaffold", kind="local", target="iss-00409")
    store.update(local_intent, expected_sequence=remote_done.sequence)
    local_failed = record_effect_result(local_intent, effect_id="scaffold", status="failed")
    store.update(local_failed, expected_sequence=local_intent.sequence)
    verified_absent = record_effect_observation(local_failed, effect_id="scaffold", outcome="observed_not_applied")
    store.update(verified_absent, expected_sequence=local_failed.sequence)
    retry = record_effect_intent(verified_absent, effect_id="scaffold", kind="local", target="iss-00409")
    store.update(retry, expected_sequence=verified_absent.sequence)
    assert retry.effects[-1].retry_of == "scaffold"
    assert len(retry.effects) == 3


def test_failed_remote_effect_cannot_be_reclassified_as_not_applied(tmp_path: Path) -> None:
    store = JournalStore(tmp_path)
    prepared = prepare_operation(
        command="scope.create",
        fixed_targets={"repository": "example/repo"},
        request_fingerprint="sha256:request",
        before_revisions={},
        engine_digest="engine-a",
        writer_epoch=7,
        effect_plan=("github-create",),
    )
    store.create(prepared)
    intent = record_effect_intent(prepared, effect_id="github-create", kind="remote", target="example/repo")
    store.update(intent, expected_sequence=prepared.sequence)
    failed = record_effect_result(intent, effect_id="github-create", status="failed")
    store.update(failed, expected_sequence=intent.sequence)
    with pytest.raises(ValueError, match="unresolved remote or local"):
        record_effect_observation(failed, effect_id="github-create", outcome="observed_not_applied")
    forged = replace(
        failed,
        effects=(*failed.effects[:-1], replace(failed.effects[-1], status="not-applied")),
        sequence=failed.sequence + 1,
    )
    with pytest.raises(ValueError, match="status transition"):
        store.update(forged, expected_sequence=failed.sequence)


def test_journal_update_cannot_retarget_an_existing_operation(tmp_path: Path) -> None:
    store = JournalStore(tmp_path)
    prepared = prepare_operation(
        command="work.start",
        fixed_targets={"target": "iss-00409"},
        request_fingerprint="sha256:request",
        before_revisions={},
        engine_digest="engine-a",
        writer_epoch=7,
        effect_plan=("branch-create",),
    )
    store.create(prepared)
    altered = replace(prepared, fixed_targets=(("target", "iss-99999"),), sequence=1)
    with pytest.raises(ValueError, match="fixed"):
        store.update(altered, expected_sequence=0)


def test_journal_update_uses_identity_of_the_verified_bytes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = JournalStore(tmp_path)
    prepared = prepare_operation(
        command="scope.create",
        fixed_targets={"repository": "example/repo"},
        request_fingerprint="sha256:request",
        before_revisions={},
        engine_digest="engine-a",
        writer_epoch=7,
        effect_plan=("github-create",),
    )
    store.create(prepared)
    first = record_effect_intent(prepared, effect_id="github-create", kind="remote", target="example/repo")
    concurrent = record_effect_result(
        first, effect_id="github-create", status="succeeded", remote_ref="gh:example/repo#47"
    )
    original_write = operation_journal.atomic_write_json

    def replace_after_read(path: Path, data: object, *, expected_identity: tuple[int, int] | None = None) -> None:
        replacement = path.with_name("concurrent.json")
        replacement.write_text(json.dumps(asdict(concurrent)), encoding="utf-8")
        replacement.replace(path)
        original_write(path, data, expected_identity=expected_identity)

    monkeypatch.setattr(operation_journal, "atomic_write_json", replace_after_read)
    with pytest.raises(ValueError, match="identity changed"):
        store.update(first, expected_sequence=0)
    assert store.load(prepared.operation_id) == concurrent


def test_journal_creation_syncs_parent_before_publishing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = JournalStore(tmp_path)
    prepared = prepare_operation(
        command="scope.create",
        fixed_targets={"repository": "example/repo"},
        request_fingerprint="sha256:request",
        before_revisions={},
        engine_digest="engine-a",
        writer_epoch=7,
        effect_plan=("github-create",),
    )
    events: list[str] = []
    original_sync = operation_journal._fsync_directory
    original_write = operation_journal.atomic_write_json

    def sync(path: Path) -> None:
        if path == store.root:
            events.append("operation-parent-synced")
        original_sync(path)

    def write(path: Path, data: object, *, expected_identity: tuple[int, int] | None = None) -> None:
        events.append("journal-published")
        original_write(path, data, expected_identity=expected_identity)

    monkeypatch.setattr(operation_journal, "_fsync_directory", sync)
    monkeypatch.setattr(operation_journal, "atomic_write_json", write)
    store.create(prepared)
    assert events == ["operation-parent-synced", "journal-published"]


def test_unknown_remote_effect_requires_observation_before_retry(tmp_path: Path) -> None:
    store = JournalStore(tmp_path)
    prepared = prepare_operation(
        command="work.finish",
        fixed_targets={"target": "iss-00409"},
        request_fingerprint="sha256:request",
        before_revisions={"selection": 2},
        engine_digest="engine-a",
        writer_epoch=7,
        effect_plan=("github-close", "active-clear"),
    )
    store.create(prepared)
    intent = record_effect_intent(
        prepared, effect_id="github-close", kind="remote", target="gh:chemitaro/spec-dock#409"
    )
    store.update(intent, expected_sequence=0)
    unknown = record_effect_result(intent, effect_id="github-close", status="unknown")
    store.update(unknown, expected_sequence=1)
    assert not can_send_effect(store.load(prepared.operation_id), "github-close")
    assert store.load(prepared.operation_id).terminal_status == "pending"
    with pytest.raises(ValueError, match="unresolved"):
        record_effect_intent(unknown, effect_id="active-clear", kind="local", target="iss-00409")
    observed = record_effect_observation(unknown, effect_id="github-close", outcome="observed_applied")
    store.update(observed, expected_sequence=2)
    assert not can_send_effect(observed, "github-close")
    record_effect_intent(observed, effect_id="active-clear", kind="local", target="iss-00409")


def test_remote_create_receipt_survives_restart_and_cannot_be_rewritten(tmp_path: Path) -> None:
    store = JournalStore(tmp_path)
    prepared = prepare_operation(
        command="scope.create",
        fixed_targets={"repository": "example/product", "title": "Plan"},
        request_fingerprint="sha256:create",
        before_revisions={},
        engine_digest="engine-a",
        writer_epoch=7,
        effect_plan=("github-create", "scaffold"),
    )
    store.create(prepared)
    intent = record_effect_intent(
        prepared, effect_id="github-create", kind="remote", target="gh:example/product:create"
    )
    store.update(intent, expected_sequence=0)
    completed = record_effect_result(
        intent, effect_id="github-create", status="succeeded", remote_ref="gh:example/product#21"
    )
    store.update(completed, expected_sequence=1)
    assert store.load(prepared.operation_id).effects[0].remote_ref == "gh:example/product#21"
    changed = replace(
        completed,
        effects=(replace(completed.effects[0], remote_ref="gh:other/product#21"),),
        sequence=3,
    )
    with pytest.raises(ValueError, match="effect"):
        store.update(changed, expected_sequence=2)


def test_observed_not_applied_allows_recorded_retry_only() -> None:
    prepared = prepare_operation(
        command="scope.close",
        fixed_targets={"target": "iss-00409"},
        request_fingerprint="sha256:close",
        before_revisions={},
        engine_digest="engine-a",
        writer_epoch=7,
        effect_plan=("github-close",),
    )
    intent = record_effect_intent(
        prepared, effect_id="github-close", kind="remote", target="gh:chemitaro/spec-dock#409"
    )
    unknown = record_effect_result(intent, effect_id="github-close", status="unknown")
    observed = record_effect_observation(unknown, effect_id="github-close", outcome="observed_not_applied")
    assert can_send_effect(observed, "github-close")
    retry = record_effect_intent(observed, effect_id="github-close", kind="remote", target="gh:chemitaro/spec-dock#409")
    assert len(retry.effects) == 2
    assert retry.effects[0].status == "not-applied"
    assert retry.effects[1].status == "intent"


def test_journal_cannot_erase_effect_or_mark_unknown_as_success(tmp_path: Path) -> None:
    store = JournalStore(tmp_path)
    prepared = prepare_operation(
        command="scope.close",
        fixed_targets={"target": "iss-00409"},
        request_fingerprint="sha256:close",
        before_revisions={},
        engine_digest="engine-a",
        writer_epoch=7,
        effect_plan=("github-close",),
    )
    store.create(prepared)
    intent = record_effect_intent(
        prepared, effect_id="github-close", kind="remote", target="gh:chemitaro/spec-dock#409"
    )
    store.update(intent, expected_sequence=0)
    unknown = record_effect_result(intent, effect_id="github-close", status="unknown")
    store.update(unknown, expected_sequence=1)
    with pytest.raises(ValueError, match="effect"):
        store.update(replace(unknown, effects=(), sequence=3), expected_sequence=2)
    with pytest.raises(ValueError, match="terminal"):
        store.update(replace(unknown, terminal_status="succeeded", sequence=3), expected_sequence=2)


def test_unimplemented_rollback_cannot_clear_a_pending_journal(tmp_path: Path) -> None:
    store = JournalStore(tmp_path)
    prepared = prepare_operation(
        command="scope.delete",
        fixed_targets={"target": "iss-00409"},
        request_fingerprint="sha256:delete",
        before_revisions={},
        engine_digest="engine-a",
        writer_epoch=7,
        effect_plan=("local-delete",),
    )
    store.create(prepared)
    with pytest.raises(ValueError, match="rollback"):
        store.update(replace(prepared, terminal_status="rolled-back", sequence=1), expected_sequence=0)


def test_planned_effects_cannot_be_skipped_or_reordered_to_clear_blocker() -> None:
    prepared = prepare_operation(
        command="work.finish",
        fixed_targets={"target": "iss-00409"},
        request_fingerprint="sha256:finish",
        before_revisions={},
        engine_digest="engine-a",
        writer_epoch=7,
        effect_plan=("github-close", "active-clear"),
    )
    with pytest.raises(ValueError, match="effect plan"):
        replace(prepared, terminal_status="succeeded", sequence=1)
    with pytest.raises(ValueError, match="effect plan"):
        record_effect_intent(prepared, effect_id="active-clear", kind="local", target="iss-00409")


def test_atomic_json_exchange_failure_keeps_previous_bytes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "state.json"
    path.write_bytes(b'{"original":true}\n')
    original = path.read_bytes()

    def fail_exchange(*args: object, **kwargs: object) -> None:
        raise OSError("injected exchange failure")

    monkeypatch.setattr("spec_dock_runtime.infra.json_store._rename_exchange_at", fail_exchange)
    with pytest.raises(OSError, match="exchange failure"):
        identity = path.stat()
        atomic_write_json(path, {"new": True}, expected_identity=(identity.st_dev, identity.st_ino))
    assert path.read_bytes() == original


def test_atomic_json_exchange_preserves_racing_destination(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "state.json"
    path.write_bytes(b'{"original":true}\n')
    expected = path.stat()
    competitor = tmp_path / "competitor.json"
    competitor.write_bytes(b'{"competitor":true}\n')

    from spec_dock_runtime.infra import json_store

    real_exchange = json_store._rename_exchange_at
    raced = False

    def race_then_exchange(source_fd: int, source_name: str, target_fd: int, target_name: str) -> None:
        nonlocal raced
        if not raced:
            competitor.replace(path)
            raced = True
        real_exchange(source_fd, source_name, target_fd, target_name)

    monkeypatch.setattr(json_store, "_rename_exchange_at", race_then_exchange)
    with pytest.raises(ValueError, match="identity changed"):
        atomic_write_json(path, {"new": True}, expected_identity=(expected.st_dev, expected.st_ino))
    candidates = [item.read_bytes() for item in tmp_path.rglob("*") if item.is_file()]
    assert b'{"competitor":true}\n' in candidates
    assert path.read_bytes() == b'{"competitor":true}\n'


def test_atomic_json_exchange_error_after_effect_blocks_blind_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "state.json"
    path.write_bytes(b'{"original":true}\n')
    identity = path.stat()
    from spec_dock_runtime.infra import json_store

    real_exchange = json_store._rename_exchange_at

    def effect_then_error(source_fd: int, source_name: str, target_fd: int, target_name: str) -> None:
        real_exchange(source_fd, source_name, target_fd, target_name)
        raise OSError("injected post-effect error")

    monkeypatch.setattr(json_store, "_rename_exchange_at", effect_then_error)
    with pytest.raises(OSError, match="post-effect"):
        atomic_write_json(path, {"new": True}, expected_identity=(identity.st_dev, identity.st_ino))
    assert path.read_bytes() == b'{"new":true}\n'
    with pytest.raises(RuntimeError, match="recovery is required"):
        atomic_write_json(path, {"newer": True}, expected_identity=(path.stat().st_dev, path.stat().st_ino))


def test_atomic_json_create_only_has_no_second_hardlink(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    atomic_write_json(path, {"created": True})
    assert path.stat().st_nlink == 1
    assert path.read_bytes() == b'{"created":true}\n'


def test_journal_create_preserves_original_publish_error_with_retained_stage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    record = prepare_operation(
        command="scope.create",
        fixed_targets={"target": "init-local-00001"},
        request_fingerprint="sha256:request",
        before_revisions={},
        engine_digest="engine-a",
        writer_epoch=1,
        effect_plan=("scaffold",),
    )

    def fail_publish(*args: object, **kwargs: object) -> None:
        raise OSError("injected publish failure")

    monkeypatch.setattr("spec_dock_runtime.infra.json_store._rename_no_replace_at", fail_publish)
    with pytest.raises(OSError, match="injected publish failure"):
        JournalStore(tmp_path).create(record)
    operation_dir = JournalStore(tmp_path).root / record.operation_id
    assert not (operation_dir / "journal.json").exists()
    assert any((operation_dir / ".specdock-json-transactions").iterdir())


def _exchange_then_hold(path_value: str, ready: Queue[str]) -> None:
    from spec_dock_runtime.infra import json_store

    path = Path(path_value)
    identity = path.stat()
    real_exchange = json_store._rename_exchange_at

    def exchange_then_pause(source_fd: int, source_name: str, target_fd: int, target_name: str) -> None:
        real_exchange(source_fd, source_name, target_fd, target_name)
        ready.put("exchanged")
        time.sleep(30)

    json_store._rename_exchange_at = exchange_then_pause
    json_store.atomic_write_json(path, {"new": True}, expected_identity=(identity.st_dev, identity.st_ino))


def test_atomic_json_killed_after_exchange_retains_old_and_blocks_retry(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    path.write_bytes(b'{"original":true}\n')
    ready: Queue[str] = Queue()
    child = Process(target=_exchange_then_hold, args=(str(path), ready))
    child.start()
    try:
        assert ready.get(timeout=5) == "exchanged"
    finally:
        child.kill()
        child.join(timeout=5)
    assert path.read_bytes() == b'{"new":true}\n'
    candidates = [item.read_bytes() for item in tmp_path.rglob("*") if item.is_file()]
    assert b'{"original":true}\n' in candidates
    with pytest.raises(RuntimeError, match="recovery is required"):
        atomic_write_json(path, {"newer": True}, expected_identity=(path.stat().st_dev, path.stat().st_ino))
    assert reconcile_atomic_json(path) == ("published",)
    identity = path.stat()
    atomic_write_json(path, {"newer": True}, expected_identity=(identity.st_dev, identity.st_ino))
    assert path.read_bytes() == b'{"newer":true}\n'


def test_atomic_json_refuses_symlink_destination(tmp_path: Path) -> None:
    original = tmp_path / "original.json"
    original.write_text("{}\n", encoding="utf-8")
    link = tmp_path / "link.json"
    link.symlink_to(original)
    with pytest.raises(ValueError, match="symlink"):
        atomic_write_json(link, {"changed": True})
    assert original.read_text(encoding="utf-8") == "{}\n"


def test_atomic_json_refuses_symlink_ancestor(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    nested = outside / "nested"
    nested.mkdir(parents=True)
    alias = tmp_path / "alias"
    alias.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        atomic_write_json(alias / "nested" / "data.json", {"changed": True})
    assert not (nested / "data.json").exists()


def test_atomic_json_rejects_hardlinked_target_and_accidental_replace(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    alias = tmp_path / "alias.json"
    path.write_text("{}\n", encoding="utf-8")
    os.link(path, alias)
    identity = path.stat()
    with pytest.raises(ValueError, match="hardlink"):
        atomic_write_json(path, {"changed": True}, expected_identity=(identity.st_dev, identity.st_ino))
    normal = tmp_path / "normal.json"
    normal.write_text("{}\n", encoding="utf-8")
    with pytest.raises(FileExistsError):
        atomic_write_json(normal, {"changed": True})
    assert path.read_text(encoding="utf-8") == alias.read_text(encoding="utf-8") == "{}\n"


def test_corrupt_journal_is_not_treated_as_completed(tmp_path: Path) -> None:
    store = JournalStore(tmp_path)
    prepared = prepare_operation(
        command="work.start",
        fixed_targets={"target": "iss-00409"},
        request_fingerprint="sha256:request",
        before_revisions={},
        engine_digest="engine-a",
        writer_epoch=7,
        effect_plan=("branch-create",),
    )
    store.create(prepared)
    journal_path = store.root / prepared.operation_id / "journal.json"
    journal_path.write_text("{bad json", encoding="utf-8")
    with pytest.raises(ValueError, match="journal JSON"):
        store.pending()
