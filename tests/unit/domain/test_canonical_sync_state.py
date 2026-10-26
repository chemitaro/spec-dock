"""The version-1 sync state, registry, accepted changes and runner records (contract C9, iss-00430)."""

from __future__ import annotations

import hashlib
import json

import pytest

from spec_dock.runtime.domain.canonical_sync_state import (
    AcceptedChanges,
    CatalogSyncState,
    Hold,
    RegistryEntry,
    RunnerRecord,
    StateFormatError,
    SyncRegistry,
    holds_under,
    state_key,
)

EPIC_STATE = {
    "version": 1,
    "catalog": "/repo/spec-dock/.canonical",
    "updated_at": "2026-10-25T12:00:00Z",
    "last_cycle": {"started_at": "2026-10-25T11:59:58Z", "finished_at": "2026-10-25T12:00:00Z", "result": "ok"},
    "last_success_at": "2026-10-25T12:00:00Z",
    "last_error": None,
    "paused": None,
    "head": "a" * 40,
    "last_seen_remote": "b" * 40,
    "remote_contains_head": True,
    "unpushed_since": None,
    "pending_since": {"x.md": "2026-10-25T11:59:40Z"},
    "holds": [{"path": "big.bin", "kind": "too_large", "since": "2026-10-25T11:00:00Z"}],
    "conflicts": [{"path": "a.md", "copy": "a.conflict-mac-20261025T110000Z.md", "at": "2026-10-25T11:00:00Z"}],
    "blocking": [{"path": "b.md", "reason": "local_edit"}],
    "consumed_changesets": ["20261025T115900Z-0123456789abcdef.json"],
    "push_auth": {"result": "ok", "at": "2026-10-25T12:00:00Z", "message": None},
    "dashboard": {"input_hash": "c" * 64, "written_at": "2026-10-25T12:00:00Z", "error": None},
    "allow_unrelated_once": False,
}


def test_the_epic_state_shape_round_trips() -> None:
    state = CatalogSyncState.from_json(EPIC_STATE)
    assert state.last_cycle is not None and state.last_cycle.finished_at == "2026-10-25T12:00:00Z"
    assert state.holds == (Hold("big.bin", "too_large", "2026-10-25T11:00:00Z"),)
    assert state.to_json() == EPIC_STATE


def test_a_new_state_has_unknown_push_auth_and_nothing_else() -> None:
    state = CatalogSyncState.new("/c", at="2026-10-26T00:00:00Z")
    payload = state.to_json()
    assert payload["push_auth"] == {"result": "unknown", "at": "2026-10-26T00:00:00Z", "message": None}
    assert payload["last_seen_remote"] is None and payload["paused"] is None and payload["holds"] == []
    assert CatalogSyncState.from_json(json.loads(json.dumps(payload))) == state


def test_an_error_keeps_its_program_and_time() -> None:
    payload = dict(EPIC_STATE)
    payload["last_error"] = {
        "code": "OS_ACCESS_DENIED",
        "message": "Operation not permitted",
        "next_step": "allow",
        "program": ["/py", "/git"],
        "at": "2026-10-25T12:00:00Z",
    }
    assert CatalogSyncState.from_json(payload).to_json() == payload


@pytest.mark.parametrize(
    "change",
    [
        {"version": 2},
        {"version": True},
        {"paused": "sleeping"},
        {"holds": [{"path": "x", "kind": "odd", "since": "2026-10-25T11:00:00Z"}]},
        {"head": 7},
        {"pending_since": []},
    ],
)
def test_an_unknown_version_or_malformed_state_is_refused(change: dict[str, object]) -> None:
    with pytest.raises(StateFormatError):
        CatalogSyncState.from_json({**EPIC_STATE, **change})


def test_holds_under_a_scope_directory() -> None:
    state = CatalogSyncState.from_json({
        **EPIC_STATE,
        "holds": [
            {"path": "init-1/epics/epic-2/a.md", "kind": "secret", "since": "2026-10-25T11:00:00Z"},
            {"path": "init-1/epics/epic-20/b.md", "kind": "secret", "since": "2026-10-25T11:00:00Z"},
            {"path": "init-1/epics/epic-2", "kind": "mass_delete", "since": "2026-10-25T11:00:00Z"},
        ],
    })
    assert [hold.path for hold in holds_under(state, "init-1/epics/epic-2")] == [
        "init-1/epics/epic-2/a.md",
        "init-1/epics/epic-2",
    ]


def test_the_state_key_is_the_first_16_hex_of_the_real_path_digest() -> None:
    assert state_key("/repo/spec-dock/.canonical") == hashlib.sha256(b"/repo/spec-dock/.canonical").hexdigest()[:16]


def test_the_registry_keeps_one_entry_per_catalog() -> None:
    first = RegistryEntry("/a/.canonical", "/a", "github.com/o/r", "/usr/bin/git", "2026-10-26T00:00:00Z")
    moved = RegistryEntry("/a/.canonical", "/a", None, "/opt/git", "2026-10-26T01:00:00Z")
    other = RegistryEntry("/b/.canonical", "/b", "github.com/o/r", "/usr/bin/git", "2026-10-26T00:00:00Z")
    registry = SyncRegistry(None, ()).with_entry(first).with_entry(other).with_entry(moved)
    assert registry.catalogs == (moved, other)
    assert registry.entry_for("/b/.canonical") == other
    payload = registry.to_json()
    assert payload["version"] == 1 and payload["scheduler"] is None
    assert SyncRegistry.from_json(payload) == registry
    assert registry.without("/a/.canonical").catalogs == (other,)
    with pytest.raises(StateFormatError):
        SyncRegistry.from_json({**payload, "scheduler": "cron"})


def test_accepted_changes_and_runner_records_round_trip() -> None:
    accepted = AcceptedChanges({"a.md": "f" * 40}, ("gone.md",))
    assert AcceptedChanges.from_json(accepted.to_json()) == accepted
    assert AcceptedChanges.empty().to_json() == {"version": 1, "paths": {}, "deletions": []}
    runner = RunnerRecord(123, "2026-10-26T00:00:00Z", "0.2.4")
    assert RunnerRecord.from_json(runner.to_json()) == runner
    with pytest.raises(StateFormatError):
        AcceptedChanges.from_json({"version": 1, "paths": {"a": 1}, "deletions": []})
