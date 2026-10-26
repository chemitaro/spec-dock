"""Changesets: the version-1 record of what one SpecDock command wrote in the catalog (contract C4)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from spec_dock.runtime.domain.canonical_changeset import (
    Changeset,
    changeset_filename,
    normalize_catalog_path,
)


def test_a_changeset_round_trips_the_epic_json_shape() -> None:
    changeset = Changeset(
        origin="command",
        command="scope create",
        created_at="2026-10-25T12:00:00Z",
        paths=("init-00423-plan/epics/epic-00424-core", "init-00423-plan"),
        deletions=("init-00001-old",),
    )
    payload = changeset.to_json()
    assert payload == {
        "version": 1,
        "origin": "command",
        "command": "scope create",
        "created_at": "2026-10-25T12:00:00Z",
        "paths": ["init-00423-plan", "init-00423-plan/epics/epic-00424-core"],
        "deletions": ["init-00001-old"],
    }
    assert Changeset.from_json(payload) == changeset


def test_paths_are_normalized_deduplicated_and_sorted() -> None:
    changeset = Changeset("finish", "work finish", "2026-10-25T12:00:00Z", ("b/", "a/./c", "b"), ())
    assert changeset.paths == ("a/c", "b")


@pytest.mark.parametrize(
    "value",
    ["", ".", "..", "/abs/path", "a/../b", "a\\b", "a\0b", ".runtime", ".runtime/changesets/x.json", "./.runtime/x"],
)
def test_paths_outside_the_catalog_content_are_refused(value: str) -> None:
    with pytest.raises(ValueError):
        normalize_catalog_path(value)


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        {
            "version": 2,
            "origin": "command",
            "command": "x",
            "created_at": "2026-10-25T12:00:00Z",
            "paths": [],
            "deletions": [],
        },
        {
            "version": 1,
            "origin": "sync",
            "command": "x",
            "created_at": "2026-10-25T12:00:00Z",
            "paths": [],
            "deletions": [],
        },
        {
            "version": 1,
            "origin": "command",
            "command": "",
            "created_at": "2026-10-25T12:00:00Z",
            "paths": [],
            "deletions": [],
        },
        {"version": 1, "origin": "command", "command": "x", "created_at": "yesterday", "paths": [], "deletions": []},
        {
            "version": 1,
            "origin": "command",
            "command": "x",
            "created_at": "2026-10-25T12:00:00Z",
            "paths": "a",
            "deletions": [],
        },
        {
            "version": 1,
            "origin": "command",
            "command": "x",
            "created_at": "2026-10-25T12:00:00Z",
            "paths": ["../x"],
            "deletions": [],
        },
        {
            "version": True,
            "origin": "command",
            "command": "x",
            "created_at": "2026-10-25T12:00:00Z",
            "paths": [],
            "deletions": [],
        },
    ],
)
def test_malformed_changesets_are_refused(payload: object) -> None:
    with pytest.raises(ValueError):
        Changeset.from_json(payload)


def test_the_file_name_sorts_by_utc_time() -> None:
    created = datetime(2026, 10, 25, 12, 0, 1, tzinfo=timezone.utc)
    assert changeset_filename(created, "0123456789abcdef") == "20261025T120001Z-0123456789abcdef.json"
    with pytest.raises(ValueError):
        changeset_filename(created, "not-hex")
