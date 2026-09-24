"""D-16 blocking journals survive interruption without blind effect replay."""

from __future__ import annotations

from dataclasses import replace
from multiprocessing import Process, Queue
import os
from pathlib import Path
import sys
import time

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.operation_executor import (  # noqa: E402
    assert_resume_request,
    can_send_effect,
    prepare_operation,
    record_effect_intent,
    record_effect_observation,
    record_effect_result,
)
from spec_dock_runtime.infra.json_store import atomic_write_json  # noqa: E402
from spec_dock_runtime.infra.operation_journal import JournalStore  # noqa: E402


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


def test_atomic_json_rename_failure_keeps_previous_bytes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "state.json"
    path.write_bytes(b'{"original":true}\n')
    original = path.read_bytes()

    def fail_replace(*args: object, **kwargs: object) -> None:
        raise OSError("injected rename failure")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(OSError, match="rename failure"):
        identity = path.stat()
        atomic_write_json(path, {"new": True}, expected_identity=(identity.st_dev, identity.st_ino))
    assert path.read_bytes() == original
    assert sorted(item.name for item in tmp_path.iterdir()) == ["state.json"]


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
