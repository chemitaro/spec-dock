"""Schema-3 repositories are untouched by the new commands (AC-430-18), and the public C9 parts (AC-430-20)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from spec_dock.runtime.application.canonical_schedule import request_sync_now
from spec_dock.runtime.domain.canonical_sync_state import (
    CatalogSyncState,
    Hold,
    RegistryEntry,
    SyncRegistry,
    holds_under,
)
from spec_dock.runtime.infra import canonical_scheduling
from spec_dock.runtime.infra.canonical_registry import read_registry, update_registry
from spec_dock.runtime.infra.canonical_state import read_catalog_state, update_catalog_state
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.canonical_repo import bare_remote, clone, isolate_user_state
from tests.support.canonical_sync import FakeScheduler

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any

LEGACY = {"schema_version": 3, "writer_protocol": "specdock.worktree-writer/v1"}


def _run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, dict[str, Any]]:
    capsys.readouterr()
    code = main([*argv, "--json"])
    return code, json.loads(capsys.readouterr().out)


@pytest.mark.parametrize(
    "argv",
    [
        ("canonical", "sync"),
        ("canonical", "accept", "--deletions"),
        ("canonical", "restore"),
        ("canonical", "resume", "--adopt-remote"),
        ("canonical", "remove", "--yes"),
        ("canonical", "link", "--no-schedule"),
    ],
)
def test_schema_three_stops_every_new_command_as_not_migrated_without_writing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], argv: tuple[str, ...]
) -> None:
    isolate_user_state(monkeypatch, tmp_path)
    checkout = clone(bare_remote(tmp_path / "v3.git", declaration=LEGACY), tmp_path / "v3")
    before = tree_digest(checkout)
    code, result = _run(capsys, "--project", str(checkout), *argv)
    assert code == 3 and result["error"]["code"] == "CANONICAL_NOT_MIGRATED", result
    assert tree_digest(checkout) == before and not (tmp_path / "state").exists()


def test_registered_sync_reads_only_the_registry_and_never_a_schema_three_repository(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    isolate_user_state(monkeypatch, tmp_path)
    checkout = clone(bare_remote(tmp_path / "v3.git", declaration=LEGACY), tmp_path / "v3")
    before = tree_digest(checkout)
    monkeypatch.chdir(checkout)
    code, result = _run(capsys, "canonical", "sync", "--registered")
    assert code == 0 and result["status"] == "unchanged" and result["data"]["catalogs"] == []
    assert tree_digest(checkout) == before


def test_request_sync_now_kicks_the_registered_job_and_never_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "state"
    assert request_sync_now(root) is False  # nothing registered
    update_registry(root, lambda registry: SyncRegistry("launchd", ()))
    fake = FakeScheduler("launchd")
    monkeypatch.setattr(canonical_scheduling, "scheduler_for", lambda kind, **_kwargs: fake)
    assert request_sync_now(root) is True and fake.calls == [("kick", "launchd")]

    def broken(**_kwargs: object) -> None:
        raise canonical_scheduling.SchedulerError("launchctl kickstart failed: Operation not permitted")

    monkeypatch.setattr(fake, "kick", lambda spec: broken())
    assert request_sync_now(root) is False


def test_the_state_parts_i5_and_i11_use(tmp_path: Path) -> None:
    root = tmp_path / "state"
    catalog = "/clone/spec-dock/.canonical"
    assert read_catalog_state(root, catalog) is None
    stamp = "2026-10-26T00:00:00Z"

    def seed(current: CatalogSyncState | None) -> CatalogSyncState:
        return CatalogSyncState.new(catalog, at=stamp).evolve(
            holds=(Hold("init-1/epics/epic-2/x.md", "secret", stamp),), remote_contains_head=True
        )

    update_catalog_state(root, catalog, seed)
    dashboard = {"input_hash": "0" * 64, "written_at": stamp, "error": None}
    written = update_catalog_state(root, catalog, lambda current: current.evolve(dashboard=dashboard))  # type: ignore[union-attr]
    state = read_catalog_state(root, catalog)
    assert state == written and state is not None and state.dashboard == dashboard
    assert [hold.path for hold in holds_under(state, "init-1/epics/epic-2")] == ["init-1/epics/epic-2/x.md"]
    assert state.remote_contains_head is True and state.last_cycle is None
    entry = RegistryEntry(catalog, "/clone", "github.com/o/r", "/usr/bin/git", stamp)
    update_registry(root, lambda registry: registry.with_entry(entry))
    assert read_registry(root).catalogs == (entry,)
