from __future__ import annotations

import base64
from dataclasses import replace
import hashlib
import os
import stat
from typing import TYPE_CHECKING

import pytest

from spec_dock.provider_lifecycle.contracts import ActiveState, CompletionReceipt, InstallationRecord, StageOwner
from spec_dock.provider_lifecycle.private_state import (
    ActiveStateStore,
    CompletionReceiptStore,
    PrivateStateError,
    PrivateStateForeignError,
    StageStore,
    cleanup_token_for,
    resolve_private_namespace,
    tuple_key_for,
)
from spec_dock.provider_lifecycle.wire import serialize_installation_record

if TYPE_CHECKING:
    from pathlib import Path


def _state(root: Path) -> tuple[Path, ActiveState, StageOwner]:
    value = os.lstat(root)
    digest = "a" * 64
    tuple_key = tuple_key_for("update", digest, "preserve-only")
    generation = "0" * 32
    token = cleanup_token_for("b" * 64, tuple_key, "update", generation)
    record = InstallationRecord(
        1,
        "incomplete",
        "update",
        "0.2.4",
        digest,
        "preserve-only",
        {"spec-dock": "0.2.4", "spec-dock-grill-with-docs": "0.2.4"},
    )
    expected_record = serialize_installation_record(record)
    owned = [
        {
            "path": path,
            "original_kind": "absent",
            "original_tree_digest": None,
            "original_inode": None,
            "terminal_kind": "directory",
            "terminal_tree_digest": "c" * 64,
        }
        for path in (
            "spec-dock/docs",
            "spec-dock/templates",
            "spec-dock/system",
            "spec-dock/scripts",
            ".agents/skills/spec-dock",
            ".agents/skills/spec-dock-grill-with-docs",
        )
    ]
    registered = [
        {
            "name": name,
            "target_path": path,
            "candidate_tree_digest": "c" * 64,
            "original_tree_digest": None,
        }
        for name, path in zip(
            ("docs", "templates", "system", "scripts", "slot-spec-dock", "slot-spec-dock-grill-with-docs"),
            (item["path"] for item in owned),
            strict=True,
        )
    ]
    active = ActiveState(
        1,
        "prepared",
        "b" * 64,
        {"device": value.st_dev, "inode": value.st_ino, "euid": os.geteuid()},
        tuple_key,
        generation,
        "update",
        digest,
        "preserve-only",
        "update",
        {"kind": "absent", "bytes_base64": None, "sha256": None, "witness": None},
        {
            "bytes_base64": base64.b64encode(expected_record).decode(),
            "sha256": hashlib.sha256(expected_record).hexdigest(),
        },
        {"disposition": "planned-create", "witness": None},
        owned,
        registered,
        None,
        "d" * 64,
        token,
        {
            "role": "cleanup-retry",
            "invocation_id": "update",
            "cleanup_token": token,
            "rendered_command": "spec-dock update --provider-cleanup-token " + token + " -- /tmp/consumer",
        },
        None,
    )
    owner = StageOwner(
        1,
        "b" * 64,
        tuple_key,
        generation,
        "update",
        digest,
        "preserve-only",
        "update",
        ("docs", "templates", "system", "scripts", "slot-spec-dock", "slot-spec-dock-grill-with-docs"),
        ("c" * 64,) * 6,
        (None,) * 6,
    )
    return resolve_private_namespace(root), active, owner


def test_t04_prepared_active_precedes_stage_and_p1_only_rebuilds_registered_entries(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    namespace, active, owner = _state(repository)
    active_store = ActiveStateStore(namespace)
    stage = StageStore(namespace, active_store)
    with pytest.raises(PrivateStateError):
        stage.ensure_registered_entries()
    assert not (namespace / "STAGE").exists()

    active_store.save(active)
    stage.ensure_registered_entries()
    stage.save_owner(owner)
    initial_writes = stage.write_count
    assert stage.reuse_if_valid(owner)
    assert stage.write_count == initial_writes

    (namespace / "STAGE" / "docs").rmdir()
    rebuilt: list[str] = []
    stage.rebuild_registered_entries(owner, builder=lambda name, _fd: rebuilt.append(name))
    assert rebuilt == list(owner.entry_names)
    assert stage.write_count == initial_writes + 1
    assert stage.reuse_if_valid(owner)
    assert stage.write_count == initial_writes + 1


def test_t04_stage_root_binding_is_validated_on_p2_reuse(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    namespace, active, owner = _state(repository)
    active_store = ActiveStateStore(namespace)
    stage = StageStore(namespace, active_store)
    active_store.save(active)
    stage.ensure_registered_entries()
    stage.save_owner(owner)
    initial_writes = stage.write_count

    (namespace / "STAGE").chmod(0o755)

    with pytest.raises(PrivateStateForeignError, match="private directory binding is unsafe"):
        stage.reuse_if_valid(owner)
    assert stage.write_count == initial_writes


def test_t04_private_modes_and_record_temp_exception_are_exact(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    namespace, active, _owner = _state(repository)
    store = ActiveStateStore(namespace)
    store.save(active)
    assert stat.S_IMODE(os.lstat(namespace).st_mode) == 0o700
    assert stat.S_IMODE(os.lstat(namespace / "ACTIVE.json").st_mode) == 0o600

    record = InstallationRecord(
        1,
        "ready",
        None,
        "0.2.4",
        "a" * 64,
        "preserve-only",
        {"spec-dock": "0.2.4", "spec-dock-grill-with-docs": "0.2.4"},
    )
    payload = serialize_installation_record(record)
    witness = store.write_record_temp(payload)
    assert witness.mode == 0o644
    assert witness.link_count == 1
    assert witness.size == len(payload)
    assert witness.sha256 == hashlib.sha256(payload).hexdigest()
    assert store.load_record_temp() == payload
    assert not (namespace / "RECORD-TEMP.tmp").exists()

    receipt_store = CompletionReceiptStore(namespace)
    receipt = CompletionReceipt(
        1,
        active.repository_key,
        active.tuple_key,
        active.operation_generation,
        active.operation,
        active.candidate_digest,
        active.seed_policy,
        active.result_family,
        active.terminal_record_digest,
        active.cleanup_token,
        active.cleanup_retry_invocation,
        None,
    )
    receipt_store.save(receipt)
    assert receipt_store.load() == receipt
    assert stat.S_IMODE(os.lstat(namespace / "CLEANUP-COMPLETED.json").st_mode) == 0o600


def test_t04_content_equal_foreign_record_temp_is_preserved_and_blocked(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    namespace, active, _owner = _state(repository)
    store = ActiveStateStore(namespace)
    store.save(active)

    record = InstallationRecord(
        1,
        "ready",
        None,
        "0.2.4",
        active.candidate_digest,
        active.seed_policy,
        {"spec-dock": "0.2.4", "spec-dock-grill-with-docs": "0.2.4"},
    )
    payload = serialize_installation_record(record)
    original_witness = store.write_record_temp(payload)
    store.save(replace(active, record_temp_witness=original_witness))

    record_temp = namespace / "RECORD-TEMP"
    record_temp.unlink()
    record_temp.write_bytes(payload)
    record_temp.chmod(0o644)
    foreign_inode = os.lstat(record_temp).st_ino

    with pytest.raises(PrivateStateForeignError):
        store.write_record_temp(payload)
    assert record_temp.read_bytes() == payload
    assert os.lstat(record_temp).st_ino == foreign_inode
    assert foreign_inode != original_witness.inode


def test_t04_active_identity_replacement_is_preserved_and_blocked(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    namespace, active, _owner = _state(repository)
    store = ActiveStateStore(namespace)
    store.save(active)
    before = (namespace / "ACTIVE.json").read_bytes(), os.lstat(namespace / "ACTIVE.json").st_ino

    replacement = replace(
        active,
        operation_generation="1" * 32,
        cleanup_token=cleanup_token_for(active.repository_key, active.tuple_key, active.result_family, "1" * 32),
    )
    with pytest.raises(PrivateStateForeignError):
        store.save(replacement)
    assert ((namespace / "ACTIVE.json").read_bytes(), os.lstat(namespace / "ACTIVE.json").st_ino) == before


def test_t04_private_intermediate_symlink_is_rejected(tmp_path: Path) -> None:
    real_parent = tmp_path / "real-parent"
    real_parent.mkdir()
    repository = real_parent / "repository"
    repository.mkdir()
    linked_parent = tmp_path / "linked-parent"
    linked_parent.symlink_to(real_parent, target_is_directory=True)

    with pytest.raises(PrivateStateError):
        resolve_private_namespace(linked_parent / "repository")
