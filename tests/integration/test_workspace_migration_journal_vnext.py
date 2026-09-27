"""Migration recovery records retain exact before and after bytes outside worktrees."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))


def test_migration_journal_round_trip_and_pending_scan(tmp_path: Path) -> None:
    import spec_dock_runtime.infra.migration_journal as journal

    common = tmp_path / "repo.git"
    common.mkdir()
    before = b'{"schema_version":1}\n'
    after = b'{"schema_version":3}\n'
    item = journal.MigrationFile(
        str(tmp_path / "repo/spec-dock/workspace.json"),
        before,
        after,
        "sha256:" + hashlib.sha256(before).hexdigest(),
        "sha256:" + hashlib.sha256(after).hexdigest(),
    )
    record = journal.MigrationRecord(
        "a" * 32,
        str(common),
        "sha256:" + "b" * 64,
        "sha256:" + "c" * 64,
        "d" * 64,
        1,
        (("main", str(tmp_path / "repo")),),
        (item,),
        (),
        "prepared",
    )
    journal.write_migration_record(common, record, create=True)
    assert journal.read_migration_record(common, record.operation_id) == record
    assert journal.pending_migrations(common) == (record.operation_id,)
    journal.write_migration_record(common, replace(record, phase="committed", completed_paths=(item.path,)))
    assert journal.pending_migrations(common) == ()


def test_migration_journal_rejects_modified_after_bytes(tmp_path: Path) -> None:
    import spec_dock_runtime.infra.migration_journal as journal

    common = tmp_path / "repo.git"
    common.mkdir()
    after = b"new\n"
    item = journal.MigrationFile(
        str(tmp_path / "repo/spec-dock/workspace.json"),
        None,
        after,
        None,
        "sha256:" + hashlib.sha256(after).hexdigest(),
    )
    record = journal.MigrationRecord(
        "a" * 32,
        str(common),
        "sha256:" + "b" * 64,
        "sha256:" + "c" * 64,
        "d" * 64,
        1,
        (("main", str(tmp_path / "repo")),),
        (item,),
        (),
        "prepared",
    )
    journal.write_migration_record(common, record, create=True)
    path = common / "spec-dock/control/migrations" / record.operation_id / "record.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["files"][0]["after_digest"] = "sha256:" + "0" * 64
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="snapshot"):
        journal.pending_migrations(common)
