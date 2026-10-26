"""State-root files of the periodic sync: state.json, the registry, the cycle lock and the log (iss-00430)."""

from __future__ import annotations

import json
import threading
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.domain.canonical_sync_state import CatalogSyncState, RegistryEntry, state_key
from spec_dock.runtime.infra.canonical_registry import RegistryUnreadable, read_registry, update_registry
from spec_dock.runtime.infra.canonical_state import (
    CycleBusy,
    StateUnreadable,
    append_log,
    catalog_state_dir,
    cycle_lock,
    move_catalog_state,
    read_catalog_state,
    remove_catalog_state,
    update_catalog_state,
)

if TYPE_CHECKING:
    from pathlib import Path

AT = "2026-10-26T00:00:00Z"


def test_a_missing_state_reads_as_none_and_update_creates_it(tmp_path: Path) -> None:
    root = tmp_path / "state"
    assert read_catalog_state(root, "/c") is None
    written = update_catalog_state(root, "/c", lambda current: current or CatalogSyncState.new("/c", at=AT))
    path = root / "catalogs" / state_key("/c") / "state.json"
    assert catalog_state_dir(root, "/c") == path.parent
    assert json.loads(path.read_text()) == written.to_json()
    assert read_catalog_state(root, "/c") == written
    assert [entry.name for entry in path.parent.iterdir()] == ["state.json"]  # no temporary file is left


def test_a_broken_state_is_reported_and_never_overwritten(tmp_path: Path) -> None:
    root = tmp_path / "state"
    directory = catalog_state_dir(root, "/c")
    directory.mkdir(parents=True)
    (directory / "state.json").write_text('{"version": 9}')
    with pytest.raises(StateUnreadable):
        read_catalog_state(root, "/c")
    with pytest.raises(StateUnreadable):
        update_catalog_state(root, "/c", lambda current: CatalogSyncState.new("/c", at=AT))
    assert (directory / "state.json").read_text() == '{"version": 9}'


def test_the_cycle_lock_skips_a_second_cycle_of_the_same_catalog(tmp_path: Path) -> None:
    root = tmp_path / "state"
    with cycle_lock(root, "/c"):
        with pytest.raises(CycleBusy), cycle_lock(root, "/c"):
            pass
        with cycle_lock(root, "/other"):
            pass
        # Writing state while a cycle runs takes a different lock, so the cycle itself can write.
        update_catalog_state(root, "/c", lambda current: CatalogSyncState.new("/c", at=AT))
    with cycle_lock(root, "/c"):
        pass


def test_the_cycle_lock_can_wait(tmp_path: Path) -> None:
    root = tmp_path / "state"
    held = threading.Event()
    release = threading.Event()

    def hold() -> None:
        with cycle_lock(root, "/c"):
            held.set()
            release.wait(5)

    thread = threading.Thread(target=hold)
    thread.start()
    held.wait(5)
    with pytest.raises(CycleBusy), cycle_lock(root, "/c", timeout=0.1):
        pass
    release.set()
    with cycle_lock(root, "/c", timeout=5):
        pass
    thread.join()


def test_moving_and_removing_a_catalog_state(tmp_path: Path) -> None:
    root = tmp_path / "state"
    update_catalog_state(root, "/old", lambda current: CatalogSyncState.new("/old", at=AT).evolve(last_seen_remote="b"))
    assert move_catalog_state(root, "/old", "/new") is True
    moved = read_catalog_state(root, "/new")
    assert moved is not None and moved.catalog == "/new" and moved.last_seen_remote == "b"
    assert read_catalog_state(root, "/old") is None
    update_catalog_state(root, "/old", lambda current: CatalogSyncState.new("/old", at=AT))
    assert move_catalog_state(root, "/old", "/new") is False  # the new key already has a state
    assert remove_catalog_state(root, "/new") is True
    assert remove_catalog_state(root, "/new") is False


def test_the_log_rotates_one_generation_above_its_limit(tmp_path: Path) -> None:
    root = tmp_path / "state"
    append_log(root, "first", limit=10)
    append_log(root, "second line", limit=10)
    append_log(root, "third", limit=10)
    log = root / "canonical-sync.log"
    assert (root / "canonical-sync.log.1").read_text() == "first\nsecond line\n"
    assert log.read_text() == "third\n"


def test_the_registry_reads_empty_and_updates_atomically(tmp_path: Path) -> None:
    root = tmp_path / "state"
    assert read_registry(root).catalogs == ()
    entry = RegistryEntry("/c", "/m", "github.com/o/r", "/usr/bin/git", AT)
    before, after = update_registry(root, lambda registry: registry.with_entry(entry))
    assert before.catalogs == () and after.catalogs == (entry,)
    assert read_registry(root) == after
    (root / "canonical-registry.json").write_text("not json")
    with pytest.raises(RegistryUnreadable):
        read_registry(root)
    with pytest.raises(RegistryUnreadable):
        update_registry(root, lambda registry: registry)
    assert (root / "canonical-registry.json").read_text() == "not json"
