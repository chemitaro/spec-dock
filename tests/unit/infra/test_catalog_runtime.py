"""The catalog's .runtime area: changesets placed atomically and the creation staging area (contract C4)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from spec_dock.runtime.domain.canonical_changeset import Changeset
from spec_dock.runtime.infra.catalog_runtime import staging_directory, write_changeset

CHANGESET = Changeset("command", "scope create", "2026-10-25T12:00:00Z", ("init-00001-plan",), ())


def test_a_changeset_is_placed_under_runtime_changesets_with_its_json(tmp_path: Path) -> None:
    written = write_changeset(tmp_path, CHANGESET, token="0123456789abcdef")
    assert written == tmp_path / ".runtime/changesets/20261025T120000Z-0123456789abcdef.json"
    assert json.loads(written.read_text(encoding="utf-8")) == CHANGESET.to_json()
    assert sorted(entry.name for entry in written.parent.iterdir()) == [written.name]


def test_an_existing_name_is_never_overwritten(tmp_path: Path) -> None:
    first = write_changeset(tmp_path, CHANGESET, token="0123456789abcdef")
    second = write_changeset(tmp_path, CHANGESET, token="0123456789abcdef")
    assert first != second and first.exists() and second.exists()
    assert json.loads(first.read_text(encoding="utf-8")) == json.loads(second.read_text(encoding="utf-8"))


def test_a_redirected_runtime_directory_is_refused(tmp_path: Path) -> None:
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    catalog = tmp_path / "catalog"
    catalog.mkdir()
    (catalog / ".runtime").symlink_to(elsewhere)
    with pytest.raises(OSError):
        write_changeset(catalog, CHANGESET)
    assert list(elsewhere.iterdir()) == []


def test_the_staging_directory_lives_in_the_catalog_runtime_area(tmp_path: Path) -> None:
    staging = staging_directory(tmp_path)
    assert staging == tmp_path / ".runtime/staging" and staging.is_dir()
    assert staging_directory(tmp_path) == staging
    assert not Path(staging).is_symlink()
