"""D-16 blocking journals survive interruption without blind effect replay."""

from __future__ import annotations

from dataclasses import replace
from multiprocessing import Process, Queue
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


def test_journal_update_cannot_retarget_an_existing_operation(tmp_path: Path) -> None:
    store = JournalStore(tmp_path)
    prepared = prepare_operation(
        command="work.start",
        fixed_targets={"target": "iss-00409"},
        request_fingerprint="sha256:request",
        before_revisions={},
        engine_digest="engine-a",
        writer_epoch=7,
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


def test_atomic_json_rename_failure_keeps_previous_bytes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "state.json"
    path.write_bytes(b'{"original":true}\n')
    original = path.read_bytes()

    def fail_replace(self: Path, target: Path) -> None:
        raise OSError("injected rename failure")

    monkeypatch.setattr(Path, "replace", fail_replace)
    with pytest.raises(OSError, match="rename failure"):
        atomic_write_json(path, {"new": True})
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


def test_corrupt_journal_is_not_treated_as_completed(tmp_path: Path) -> None:
    store = JournalStore(tmp_path)
    prepared = prepare_operation(
        command="work.start",
        fixed_targets={"target": "iss-00409"},
        request_fingerprint="sha256:request",
        before_revisions={},
        engine_digest="engine-a",
        writer_epoch=7,
    )
    store.create(prepared)
    journal_path = store.root / prepared.operation_id / "journal.json"
    journal_path.write_text("{bad json", encoding="utf-8")
    with pytest.raises(ValueError, match="journal JSON"):
        store.pending()
