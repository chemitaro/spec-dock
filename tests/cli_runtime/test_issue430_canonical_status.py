"""The sync, snapshot, changes and git items of `canonical status` (iss-00430, AC-430-11, -12, -15)."""

from __future__ import annotations

from datetime import timedelta
import os
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.runtime.domain.canonical_sync_state import Blocking, Hold, PushAuth
from spec_dock.runtime.infra.canonical_state import update_catalog_state
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.canonical_repo import git
from tests.support.canonical_sync import SyncPair

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def pair(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> SyncPair:
    created = SyncPair.create(tmp_path, monkeypatch, capsys, link=False)
    assert created.run(created.a, "canonical", "link")[0] == 0
    return created


def _status(pair: SyncPair, checkout: Path | None = None) -> dict[str, Any]:
    code, result = pair.run(checkout or pair.a, "canonical", "status")
    assert code == 0 and result["status"] == "succeeded", result
    return result


def _codes(result: dict[str, Any]) -> set[str]:
    return {item["code"] for item in result["warnings"]}


def _mutate(pair: SyncPair, **changes: object) -> None:
    catalog = os.path.realpath(pair.catalog(pair.a))
    update_catalog_state(pair.state_root, catalog, lambda current: current.evolve(**changes))  # type: ignore[union-attr]


def test_a_registered_catalog_whose_job_never_ran_says_so(pair: SyncPair) -> None:
    result = _status(pair)
    sync = result["data"]["sync"]
    assert sync["registered"] is True and sync["scheduler"] == "launchd"
    assert sync["job"] == {"installed": True, "active": True, "detail": None}
    assert "CANONICAL_SYNC_NOT_CONFIRMED" in _codes(result)
    assert result["data"]["git"]["registered"]["path"] == result["data"]["git"]["path"]


def test_holds_blocking_pause_auth_and_errors_each_have_a_next_step(pair: SyncPair) -> None:
    pair.sync(pair.a)
    _mutate(
        pair,
        holds=(
            Hold("big.bin", "too_large", "2026-10-26T00:00:00Z"),
            Hold("d/1.md", "mass_delete", "2026-10-26T00:00:00Z"),
        ),
        blocking=(Blocking("busy.md", "local_edit"),),
        paused="remote_rewritten",
        push_auth=PushAuth("failed", "2026-10-26T00:00:00Z", "Authentication failed"),
    )
    result = _status(pair)
    codes = _codes(result)
    assert {"CANONICAL_SAVE_HELD", "CANONICAL_SYNC_BLOCKED", "CANONICAL_PAUSED", "CANONICAL_PUSH_AUTH_FAILED"} <= codes
    holds = {hold["path"]: hold["next_step"] for hold in result["data"]["changes"]["holds"]}
    assert "accept <path>" in holds["big.bin"] and "accept --deletions" in holds["d/1.md"]
    assert result["data"]["changes"]["blocking"] == [{"path": "busy.md", "reason": "local_edit"}]
    assert result["data"]["sync"]["paused"] == "remote_rewritten"
    assert "resume --adopt-remote" in result["data"]["sync"]["next_step"]
    auth = next(item for item in result["warnings"] if item["code"] == "CANONICAL_PUSH_AUTH_FAILED")
    assert "gh auth setup-git" in auth["details"]["next_step"]  # origin is a local path, not ssh


def test_commits_unpushed_for_more_than_ten_minutes_are_warned(pair: SyncPair) -> None:
    pair.sync(pair.a)
    since = (pair.clock.now() - timedelta(minutes=11)).strftime("%Y-%m-%dT%H:%M:%SZ")
    _mutate(pair, unpushed_since=since, remote_contains_head=False)
    assert "CANONICAL_UNPUSHED_STALE" in _codes(_status(pair))
    recent = (pair.clock.now() - timedelta(minutes=9)).strftime("%Y-%m-%dT%H:%M:%SZ")
    _mutate(pair, unpushed_since=recent)
    assert "CANONICAL_UNPUSHED_STALE" not in _codes(_status(pair))


def test_a_job_that_stopped_recording_cycles_is_warned(pair: SyncPair) -> None:
    pair.sync(pair.a)
    assert "CANONICAL_SYNC_NOT_CONFIRMED" not in _codes(_status(pair))
    pair.advance(4 * 60)
    assert "CANONICAL_SYNC_NOT_CONFIRMED" not in _codes(_status(pair))
    pair.advance(2 * 60)
    result = _status(pair)
    warning = next(item for item in result["warnings"] if item["code"] == "CANONICAL_SYNC_NOT_CONFIRMED")
    assert warning["details"]["last_cycle_at"] == result["data"]["sync"]["last_cycle"]["finished_at"]


def test_status_writes_nothing_and_never_contacts_the_remote_or_github(
    pair: SyncPair, monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.application import canonical_sync
    from tests.support.fake_github import FakeGithub, install_fake_gh

    fake = FakeGithub("example/repo")
    handle = install_fake_gh(pair.tmp_path, monkeypatch, fake)
    monkeypatch.setattr(canonical_sync, "repository_of", lambda *_a, **_k: "github.com/example/repo")
    pair.write(pair.a, "draft.md", "d\n")
    first = _status(pair)
    git(pair.a, "remote", "set-url", "origin", str(pair.tmp_path / "nowhere.git"))
    roots = (pair.a, pair.catalog(pair.a).resolve(), pair.state_root, pair.remote)
    before = tuple(tree_digest(root) for root in roots)
    second = _status(pair)
    assert tuple(tree_digest(root) for root in roots) == before
    assert handle.load().requests == []
    assert second["data"]["sync"] == first["data"]["sync"] and second["data"]["changes"] == first["data"]["changes"]
    assert second["data"]["snapshot"]["repository"] == "github.com/example/repo"
    assert second["data"]["snapshot"]["fetched_at"] is None


def test_the_snapshot_item_reads_the_stored_snapshot(pair: SyncPair, monkeypatch: pytest.MonkeyPatch) -> None:
    from spec_dock.runtime.application import canonical_sync
    from spec_dock.runtime.infra.github_snapshot import clear_memory
    from spec_dock.runtime.infra.github_structure import GithubApi
    from tests.support.fake_github import FakeGithub

    fake = FakeGithub("example/repo")
    fake.scope("initiative", slug="plan", title="計画")
    clear_memory()
    monkeypatch.setattr(canonical_sync, "repository_of", lambda *_a, **_k: "github.com/example/repo")
    monkeypatch.setattr(canonical_sync, "github_api_for", lambda cwd: GithubApi(runner=fake, clock=fake.clock))
    assert pair.run(pair.a, "canonical", "link")[0] == 0  # the registry now records the repository
    pair.sync(pair.a)
    snapshot = _status(pair)["data"]["snapshot"]
    assert snapshot["status"] == "ok" and snapshot["fetched_at"] and snapshot["checked_at"]
    assert snapshot["anomalies"] == 0 and snapshot["path"].endswith("github/github.com/example/repo")
