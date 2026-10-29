"""Canonical-mode `dependency add` and `dependency remove` (iss-00432): blocked-by edges on GitHub only."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.support.canonical_writes import WriteWorld

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def _world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> WriteWorld:
    world = WriteWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "plan")
    world.scope("epic", 2, "core", parent=1)
    world.scope("issue", 5, "first", parent=2)
    world.scope("issue", 6, "second", parent=2)
    return world


def test_add_and_remove_write_blocked_by_with_issue_ids_and_show_at_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    before = sorted(path.relative_to(world.catalog).as_posix() for path in world.catalog.rglob("*"))
    code, payload = world.run("dependency", "add", "--from", "iss-5", "--to", "ISS-00006")
    assert code == 0, payload
    blocker_id = world.fake().issue(6).id
    assert world.writes() == [("POST", "repos/example/repo/issues/5/dependencies/blocked_by", {"issue_id": blocker_id})]
    result = payload["data"]["result"]
    assert (result["scope_id"], result["declared"], result["changed"]) == ("iss-00005", ["iss-00006"], True)
    assert payload["effects"] == [{"kind": "dependency-edge", "status": "succeeded", "target": "iss-00005->iss-00006"}]
    requests = [(item.method, item.endpoint.split("?")[0]) for item in world.fake().requests]
    first_write = requests.index(("POST", "repos/example/repo/issues/5/dependencies/blocked_by"))
    assert ("GET", "repos/example/repo/issues/5") in requests[:first_write]
    assert ("GET", "repos/example/repo/issues/6") in requests[:first_write]
    graphql = len(world.fake().graphql_requests())
    code, shown = world.run("dependency", "list", "iss-00005")
    assert code == 0 and shown["data"]["result"]["declared"] == ["iss-00006"]
    assert len(world.fake().graphql_requests()) == graphql
    code, payload = world.run("dependency", "add", "--from", "iss-00005", "--to", "iss-00006")
    assert (code, payload["status"]) == (0, "unchanged") and len(world.writes()) == 1
    code, payload = world.run("dependency", "remove", "--from", "iss-00005", "--to", "iss-00006")
    assert code == 0, payload
    assert world.writes()[-1] == ("DELETE", f"repos/example/repo/issues/5/dependencies/blocked_by/{blocker_id}", None)
    assert world.fake().issue(5).blocked_by == []
    code, payload = world.run("dependency", "remove", "--from", "iss-00005", "--to", "iss-00006")
    assert (code, payload["error"]["code"]) == (4, "SCOPE_NOT_FOUND")
    code, payload = world.run("dependency", "remove", "--from", "iss-00005", "--to", "iss-00006", "--missing-ok")
    assert (code, payload["status"]) == (0, "unchanged") and len(world.writes()) == 2
    assert sorted(path.relative_to(world.catalog).as_posix() for path in world.catalog.rglob("*")) == before
    assert world.changesets() == []


def test_a_cycle_or_a_kind_change_stops_before_any_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.edit(lambda fake: fake.block(6, by=5))
    code, payload = world.run("dependency", "add", "--from", "iss-00005", "--to", "iss-00006")
    assert (code, payload["error"]["code"]) == (3, "PRECONDITION_FAILED")
    assert "DEPENDENCY_CYCLE" in payload["error"]["message"]
    world.edit(lambda fake: setattr(fake.issue(6), "labels", ["spec-dock:epic"]))
    code, payload = world.run("dependency", "remove", "--from", "iss-00005", "--to", "epic-00006")
    assert (code, payload["error"]["code"]) == (3, "SCOPE_KIND_CHANGED")
    assert world.writes() == []


def test_an_edge_added_only_on_github_is_found_by_the_reread(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    assert world.run("scope", "show", "iss-00005")[0] == 0
    world.edit(lambda fake: fake.block(5, by=6))  # the GitHub UI; the change check may not see it
    code, payload = world.run("dependency", "add", "--from", "iss-00005", "--to", "iss-00006")
    assert (code, payload["status"]) == (0, "unchanged")
    assert world.writes() == []
