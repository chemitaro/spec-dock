"""Immutable publication and exact observed-name removal (Issue #413 D-03)."""

from __future__ import annotations

from dataclasses import replace
import json
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.domain.work_target import PhysicalIdentity, WorkTarget
from spec_dock.runtime.infra.work_target_store import WorkTargetStore

if TYPE_CHECKING:
    from pathlib import Path


def test_publish_one_immutable_record_without_scope_uuid_or_git_control(tmp_path: Path) -> None:
    (tmp_path / "spec-dock").mkdir()
    record = WorkTarget(
        "specdock.work-target/v1",
        "iss-00413",
        "gh:example/repo#413",
        "fix/issue-413",
        "2026-09-30T00:00:00Z",
        PhysicalIdentity("posix", "1", "2"),
        PhysicalIdentity("posix", "1", "3"),
    )
    with WorkTargetStore(tmp_path) as store:
        assert store.read().status == "empty"
        handle = store.publish(record)
        observation = store.read()
        assert observation.status == "selected"
        assert observation.record == record
        assert observation.handle == handle
        assert store.remove_observed(handle) == "removed"
        assert store.read().status == "empty"
    assert not (tmp_path / ".git").exists()


def _record() -> WorkTarget:
    return WorkTarget(
        "specdock.work-target/v1",
        "iss-00413",
        "gh:example/repo#413",
        "fix/issue-413",
        "2026-09-30T00:00:00Z",
        PhysicalIdentity("posix", "1", "2"),
        PhysicalIdentity("posix", "1", "3"),
    )


def test_late_removal_does_not_delete_new_selection_even_for_same_scope(tmp_path: Path) -> None:
    (tmp_path / "spec-dock").mkdir()
    with WorkTargetStore(tmp_path) as store:
        old = store.publish(_record())
        assert store.remove_observed(old) == "removed"
        new = store.publish(_record())
        assert new.basename != old.basename
        before = (store.path / new.basename).read_bytes()
        assert store.remove_observed(old) == "already_absent"
        assert (store.path / new.basename).read_bytes() == before
        assert store.read().handle == new
        with pytest.raises(FileExistsError):
            store.publish(replace(_record(), scope_id="iss-00414", github_ref="gh:example/repo#414"))


def test_changed_observed_bytes_are_not_deleted_and_bad_json_is_not_empty(tmp_path: Path) -> None:
    (tmp_path / "spec-dock").mkdir()
    with WorkTargetStore(tmp_path) as store:
        handle = store.publish(_record())
        path = store.path / handle.basename
        path.write_bytes(b"not json")
        assert store.read().status == "invalid"
        assert store.remove_observed(handle) == "conflict"
        assert path.read_bytes() == b"not json"
        # Explicit clear can capture a fresh handle without interpreting broken JSON.
        observed = store.read().observed_handles
        assert len(observed) == 1
        assert store.remove_observed(observed[0]) == "removed"


def test_multiple_final_records_are_invalid_instead_of_selecting_one(tmp_path: Path) -> None:
    (tmp_path / "spec-dock").mkdir()
    with WorkTargetStore(tmp_path) as store:
        handle = store.publish(_record())
        original = store.path / handle.basename
        other = store.path / ("target-" + "0" * 32 + ".json")
        other.write_bytes(original.read_bytes())
        observation = store.read()
        assert observation.status == "invalid"
        assert observation.record is None
        assert len(observation.observed_handles) == 2


def test_redirected_parent_cannot_read_or_publish_outside_worktree(tmp_path: Path) -> None:
    (tmp_path / "spec-dock").mkdir()
    external = tmp_path / "external"
    external.mkdir()
    (tmp_path / "spec-dock/.agent").symlink_to(external, target_is_directory=True)
    with WorkTargetStore(tmp_path) as store:
        assert store.read().status == "unavailable"
        with pytest.raises(OSError):
            store.publish(_record())
    assert list(external.iterdir()) == []


def test_failed_sync_does_not_publish_half_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "spec-dock/.agent/work-target").mkdir(parents=True)
    with WorkTargetStore(tmp_path) as store:

        def reject_sync(fd: int) -> None:
            raise OSError("injected disk sync failure")

        monkeypatch.setattr("os.fsync", reject_sync)
        with pytest.raises(OSError, match="injected"):
            store.publish(_record())
        assert not list(store.path.glob("target-*.json"))
        assert store.read().record is None
        assert len(list(store.path.glob(".stage-*"))) == 1


def test_unknown_record_field_is_invalid_and_scope_id_never_changes(tmp_path: Path) -> None:
    (tmp_path / "spec-dock").mkdir()
    with WorkTargetStore(tmp_path) as store:
        record = replace(_record(), scope_id="iss-local-00413")
        handle = store.publish(record)
        assert store.read().record == record
        path = store.path / handle.basename
        data = json.loads(path.read_text())
        data["uuid"] = "obsolete"
        path.write_text(json.dumps(data))
        assert store.read().status == "invalid"
        assert store.read().record is None


@pytest.mark.parametrize("timestamp", ["2026-09-30Z", "2026-09-30 00:00:00Z", "2026-09-30T00:00Z"])
def test_non_rfc3339_record_is_invalid_instead_of_selected(tmp_path: Path, timestamp: str) -> None:
    (tmp_path / "spec-dock").mkdir()
    with WorkTargetStore(tmp_path) as store:
        handle = store.publish(_record())
        path = store.path / handle.basename
        payload = json.loads(path.read_bytes())
        payload["selected_at"] = timestamp
        before = json.dumps(payload).encode()
        path.write_bytes(before)
        assert store.read().status == "invalid"
        assert path.read_bytes() == before
