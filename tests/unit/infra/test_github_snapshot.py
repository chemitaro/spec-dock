"""Structure snapshot store and freshness levels, with an injected clock and the shared fake GitHub."""

from __future__ import annotations

import fcntl
import json
import os
import stat
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.infra.github_snapshot import (
    SnapshotStore,
    StructureSnapshotService,
    clear_memory,
    ensure_fresh,
)
from spec_dock.runtime.infra.github_structure import (
    GithubApi,
    GithubRepository,
    GithubStructureClient,
    GithubStructureError,
)
from spec_dock.runtime.infra.state_root import resolve_state_root
from tests.support.fake_github import FakeGithub

if TYPE_CHECKING:
    from pathlib import Path

REPOSITORY = GithubRepository.parse("example/repo")


def _world(tmp_path: Path) -> tuple[FakeGithub, StructureSnapshotService, SnapshotStore]:
    fake = FakeGithub()
    initiative = fake.scope("initiative", slug="plan", title="計画")
    epic = fake.scope("epic", slug="core", parent=initiative.number)
    fake.scope("issue", slug="leaf", parent=epic.number)
    clear_memory()
    store = SnapshotStore(tmp_path / "state", REPOSITORY)
    client = GithubStructureClient(REPOSITORY, GithubApi(runner=fake, clock=fake.clock))
    return fake, StructureSnapshotService(REPOSITORY, store=store, client=client, clock=fake.clock), store


def _requests_since(fake: FakeGithub, start: int) -> list[tuple[str, int]]:
    return [(request.endpoint.split("?")[0], request.status) for request in fake.requests[start:]]


def test_state_root_follows_xdg_state_home_only_when_absolute(tmp_path: Path) -> None:
    assert resolve_state_root({"XDG_STATE_HOME": str(tmp_path), "HOME": "/nowhere"}) == tmp_path / "spec-dock"
    assert (
        resolve_state_root({"XDG_STATE_HOME": "relative", "HOME": str(tmp_path)}) == tmp_path / ".local/state/spec-dock"
    )
    assert resolve_state_root({"HOME": str(tmp_path)}) == tmp_path / ".local/state/spec-dock"


def test_first_display_read_probes_fetches_and_stores_both_files(tmp_path: Path) -> None:
    fake, service, store = _world(tmp_path)
    fresh = service.ensure_fresh("display")
    assert (fresh.probe, fresh.refreshed, fresh.stale, fresh.warning) == ("changed", True, False, None)
    assert [scope.id for scope in fresh.require().scopes] == ["init-00001", "epic-00002", "iss-00003"]
    assert fresh.payload() == {"fetched_at": "2026-10-26T00:00:00Z", "stale": False}
    assert store.directory == tmp_path / "state/github/github.com/example/repo"
    assert stat.S_IMODE(store.directory.stat().st_mode) == 0o700
    snapshot = json.loads((store.directory / "snapshot.json").read_text(encoding="utf-8"))
    probe = json.loads((store.directory / "probe.json").read_text(encoding="utf-8"))
    assert snapshot["version"] == 1 and snapshot["issues"]["1"]["title"] == "計画"
    assert probe["version"] == 1 and probe["checked_at"] == "2026-10-26T00:00:00Z" and probe["last_error"] is None
    assert set(probe["etags"]) == {"spec-dock:initiative", "spec-dock:epic", "spec-dock:issue"}
    assert sorted(path.name for path in store.directory.iterdir()) == ["probe.json", "snapshot.json"]
    assert len(fake.graphql_requests()) == 1 and len(fake.requests) == 4


@pytest.mark.parametrize(("elapsed", "probed"), [(59, False), (60, False), (61, True)])
def test_display_probes_only_after_sixty_seconds_and_a_304_sends_nothing_metered(
    tmp_path: Path, elapsed: int, probed: bool
) -> None:
    fake, service, _ = _world(tmp_path)
    service.ensure_fresh("display")
    start, metered = len(fake.requests), len(fake.metered_requests())
    fake.clock.advance(elapsed)
    fresh = service.ensure_fresh("display")
    assert fresh.probe == ("unchanged" if probed else "skipped") and not fresh.refreshed
    assert len(fake.requests) - start == (3 if probed else 0)
    assert len(fake.metered_requests()) == metered and len(fake.graphql_requests()) == 1


@pytest.mark.parametrize(
    ("level", "age", "refetched"),
    [
        ("display", 30 * 60, False),
        ("display", 30 * 60 + 1, True),
        ("cycle", 30 * 60, False),
        ("cycle", 30 * 60 + 1, True),
        ("decision", 5 * 60, False),
        ("decision", 5 * 60 + 1, True),
    ],
)
def test_age_limits_force_a_full_refetch_after_the_level_window(
    tmp_path: Path, level: str, age: int, refetched: bool
) -> None:
    fake, service, _ = _world(tmp_path)
    service.ensure_fresh("display")
    fake.clock.advance(age)
    fresh = service.ensure_fresh(level)  # type: ignore[arg-type]
    assert fresh.refreshed is refetched and fresh.probe == "unchanged"
    assert len(fake.graphql_requests()) == (2 if refetched else 1)


def test_decision_and_cycle_always_probe_even_right_after_a_fetch(tmp_path: Path) -> None:
    fake, service, _ = _world(tmp_path)
    service.ensure_fresh("display")
    for level in ("decision", "cycle"):
        start = len(fake.requests)
        assert service.ensure_fresh(level).probe == "unchanged"  # type: ignore[arg-type]
        assert [status for _, status in _requests_since(fake, start)] == [304, 304, 304]


def test_a_changed_list_triggers_a_refetch_that_shows_the_new_title(tmp_path: Path) -> None:
    fake, service, _ = _world(tmp_path)
    service.ensure_fresh("display")
    fake.issue(2).title = "新しい題名"
    fake.touch(2)
    fake.clock.advance(61)
    fresh = service.ensure_fresh("display")
    assert fresh.probe == "changed" and fresh.refreshed and fresh.require().issues[2].title == "新しい題名"


def test_failed_refetch_keeps_old_etags_so_the_next_probe_sees_the_change_again(tmp_path: Path) -> None:
    fake, service, store = _world(tmp_path)
    service.ensure_fresh("display")
    before = json.loads((store.directory / "probe.json").read_text())["etags"]
    fake.touch(3)
    fake.inject(status=502, body={"message": "down"}, method="POST", times=4)
    fake.clock.advance(61)
    stale = service.ensure_fresh("display")
    assert stale.stale is True and stale.warning is not None and stale.warning.code == "GITHUB_SNAPSHOT_STALE"
    assert stale.warning.details["fetched_at"] == "2026-10-26T00:00:00Z"
    probe = json.loads((store.directory / "probe.json").read_text())
    assert probe["etags"] == before and probe["checked_at"] == "2026-10-26T00:00:00Z"
    assert probe["last_error"]["code"] == "GITHUB_UNAVAILABLE"
    retried = service.ensure_fresh("display")
    assert retried.probe == "changed" and retried.refreshed and not retried.stale


def test_unreachable_github_degrades_by_level(tmp_path: Path) -> None:
    fake, service, _ = _world(tmp_path)
    fake.inject(status=503, body={"message": "down"}, times=100)
    with pytest.raises(GithubStructureError) as caught:
        service.ensure_fresh("display")
    assert caught.value.code == "GITHUB_UNAVAILABLE"
    cycle = service.ensure_fresh("cycle")
    assert (cycle.snapshot, cycle.stale, cycle.probe) == (None, True, "failed")
    fake._faults.clear()
    service.ensure_fresh("display")
    fake.inject(status=403, headers={"retry-after": "600"}, body={"message": "secondary rate limit"}, times=100)
    with pytest.raises(GithubStructureError) as caught:
        service.ensure_fresh("decision")
    assert caught.value.code == "GITHUB_RATE_LIMITED" and caught.value.retry_at is not None
    fake.clock.advance(61)
    shown = service.ensure_fresh("display")
    assert shown.stale and shown.require().issues[1].title == "計画"


@pytest.mark.parametrize("content", [b"{broken", b'{"version": 2}', b"[]"])
def test_unreadable_or_unknown_snapshot_versions_are_refetched(tmp_path: Path, content: bytes) -> None:
    fake, service, store = _world(tmp_path)
    service.ensure_fresh("display")
    (store.directory / "snapshot.json").write_bytes(content)
    clear_memory()
    fresh = service.ensure_fresh("display")
    assert fresh.refreshed and len(fake.graphql_requests()) == 2


def test_refetch_merge_keeps_a_write_reflected_while_the_fetch_was_running(tmp_path: Path) -> None:
    from dataclasses import replace

    from spec_dock.runtime.domain.canonical_structure import UpsertIssue

    fake, service, store = _world(tmp_path)
    service.ensure_fresh("display")
    client = service.client
    original = client.fetch_structure

    def fetch_with_concurrent_write():
        fetched = original()
        facts = replace(client.get_issue(3), title="Written during the fetch")
        fake.clock.advance(1)
        store.reflect([UpsertIssue(facts)], command="scope edit", at="2026-10-26T00:30:02Z")
        return fetched

    client.fetch_structure = fetch_with_concurrent_write  # type: ignore[method-assign]
    fake.clock.advance(30 * 60 + 1)
    fresh = service.ensure_fresh("display")
    assert fresh.refreshed and fresh.require().issues[3].title == "Written during the fetch"
    stored = json.loads((store.directory / "snapshot.json").read_text())
    assert stored["issues"]["3"]["title"] == "Written during the fetch"
    assert [write["command"] for write in stored["local_writes"]] == ["scope edit"]


def test_reflect_and_reread_update_the_snapshot_without_a_refetch(tmp_path: Path) -> None:
    from spec_dock.runtime.domain.canonical_structure import SetParent

    fake, service, _ = _world(tmp_path)
    service.ensure_fresh("display")
    reflected = service.reflect([SetParent(3, 1)], command="scope move")
    assert reflected is not None and reflected.issues[3].parent == 1
    fake.issue(3).title = "Edited on GitHub"
    reread = service.reread([3], command="work start")
    assert reread.issues[3].title == "Edited on GitHub" and reread.issues[3].parent == 1
    assert [write.command for write in reread.local_writes] == ["scope move", "work start (reread)"]
    assert service.ensure_fresh("display").require().issues[3].title == "Edited on GitHub"
    assert len(fake.graphql_requests()) == 1


def test_refresh_refetches_without_waiting_for_a_change(tmp_path: Path) -> None:
    fake, service, _ = _world(tmp_path)
    service.ensure_fresh("display")
    assert service.refresh().refreshed and len(fake.graphql_requests()) == 2


def test_unwritable_state_root_keeps_the_snapshot_in_memory(tmp_path: Path) -> None:
    fake, service, store = _world(tmp_path)
    (tmp_path / "state").mkdir()
    (tmp_path / "state").chmod(0o555)
    try:
        fresh = service.ensure_fresh("display")
        assert fresh.refreshed and not fresh.stale and store.persisted is False
        assert not (tmp_path / "state/github").exists()
        fake.clock.advance(30)
        start = len(fake.requests)
        again = SnapshotStore(tmp_path / "state", REPOSITORY).load()
        assert again[0] is not None and again[0].issues[1].title == "計画"
        assert service.ensure_fresh("display").probe == "skipped" and len(fake.requests) == start
    finally:
        (tmp_path / "state").chmod(0o755)


def test_a_busy_directory_lock_falls_back_to_memory(tmp_path: Path) -> None:
    fake, service, store = _world(tmp_path)
    service.ensure_fresh("display")
    held = os.open(store.directory, os.O_RDONLY)
    try:
        fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
        busy = SnapshotStore(tmp_path / "state", REPOSITORY, lock_timeout=0.05)
        busy_service = StructureSnapshotService(REPOSITORY, store=busy, client=service.client, clock=fake.clock)
        assert busy_service.refresh().refreshed and busy.persisted is False
    finally:
        os.close(held)


def test_module_entry_uses_the_xdg_state_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeGithub()
    fake.scope("initiative", slug="plan")
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "xdg"))
    fresh = ensure_fresh(REPOSITORY, "display", api=GithubApi(runner=fake, clock=fake.clock))
    assert fresh.require().find("init-00001") is not None
    assert (tmp_path / "xdg/spec-dock/github/github.com/example/repo/snapshot.json").is_file()


def test_state_root_override_uses_the_same_value_the_environment_gives(tmp_path: Path) -> None:
    from pathlib import Path

    environment = {"HOME": str(tmp_path)}
    computed = resolve_state_root(environment)
    assert resolve_state_root(environment, override=computed) == computed
    assert resolve_state_root({}, override=tmp_path / "explicit") == tmp_path / "explicit"
    with pytest.raises(ValueError):
        resolve_state_root(environment, override=Path("relative/root"))


def test_display_without_a_snapshot_keeps_the_original_failure_code(tmp_path: Path) -> None:
    fake, service, _ = _world(tmp_path)
    fake.inject(status=401, body={"message": "Bad credentials"}, times=10)
    with pytest.raises(GithubStructureError) as caught:
        service.ensure_fresh("display")
    assert caught.value.code == "GITHUB_ACCESS_DENIED"


def test_an_older_refetch_never_replaces_a_newer_one(tmp_path: Path) -> None:
    from spec_dock.runtime.domain.canonical_structure import build_snapshot
    from spec_dock.runtime.infra.github_snapshot import ProbeRecord

    _, service, store = _world(tmp_path)
    service.ensure_fresh("display")
    newer = json.loads((store.directory / "snapshot.json").read_text())
    older = build_snapshot(
        REPOSITORY.key, [], fetched_at="2026-10-25T23:59:59Z", fetch_started_at="2026-10-25T23:59:58Z"
    )
    kept = store.commit_refresh(older, ProbeRecord("2026-10-25T23:59:58Z", {}, None))
    assert kept.fetched_at == newer["fetched_at"] and 1 in kept.issues
    assert json.loads((store.directory / "snapshot.json").read_text()) == newer
    assert json.loads((store.directory / "probe.json").read_text())["checked_at"] == "2026-10-26T00:00:00Z"


def test_a_memory_reflection_wins_over_a_file_with_the_same_fetch_time(tmp_path: Path) -> None:
    from spec_dock.runtime.domain.canonical_structure import SetParent

    _, service, store = _world(tmp_path)
    service.ensure_fresh("display")
    held = os.open(store.directory, os.O_RDONLY)
    try:
        fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
        busy = SnapshotStore(tmp_path / "state", REPOSITORY, lock_timeout=0.05)
        reflected = busy.reflect([SetParent(3, 1)], command="scope move", at="2026-10-26T00:00:01Z")
        assert reflected is not None and busy.persisted is False
    finally:
        os.close(held)
    loaded, _ = SnapshotStore(tmp_path / "state", REPOSITORY).load()
    assert loaded is not None and loaded.issues[3].parent == 1


def test_a_refetch_reports_its_graphql_cost(tmp_path: Path) -> None:
    fake, service, _ = _world(tmp_path)
    assert service.ensure_fresh("display").graphql_cost == 1
    fake.clock.advance(61)
    assert service.ensure_fresh("display").graphql_cost is None


def test_reread_of_a_plain_blocker_updates_external_only(tmp_path: Path) -> None:
    fake, service, _ = _world(tmp_path)
    plain = fake.add_issue(title="Vendor", state="open")
    fake.block(3, by=plain.number)
    fake.touch(3)
    service.ensure_fresh("decision")
    fake.issue(plain.number).state = "closed"
    reread = service.reread([plain.number], command="work start")
    assert plain.number not in reread.issues and reread.external[plain.number].state == "closed"
