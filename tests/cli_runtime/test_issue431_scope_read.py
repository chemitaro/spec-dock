"""canonical `scope show` / `scope list`: GitHub structure from the snapshot, directories from the catalog (iss-00431)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.support.canonical_scopes import CanonicalWorld

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> CanonicalWorld:
    world = CanonicalWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, title="計画")
    world.scope("epic", 2, parent=1, title="中心")
    world.scope("issue", 3, parent=2, title="葉", state="closed", state_reason="completed")
    return world


def test_scope_show_reports_github_title_state_directory_and_snapshot_time(world: CanonicalWorld) -> None:
    code, payload = world.run("scope", "show", "iss-00003")
    assert code == 0, payload
    scope = payload["data"]["result"]["scope"]
    assert (scope["id"], scope["kind"], scope["title"], scope["parent_id"]) == (
        "iss-00003",
        "issue",
        "葉",
        "epic-00002",
    )
    assert scope["status"]["state"] == "completed" and scope["state_reason"] == "completed"
    assert scope["path"] == "spec-dock/initiatives/iss-00003"
    assert (scope["number"], scope["github_ref"], scope["directory_found"]) == (3, "gh:example/repo#3", True)
    snapshot = payload["data"]["result"]["snapshot"]
    assert snapshot["fetched_at"] and snapshot["stale"] is False
    assert payload["warnings"] == []


def test_scope_list_filters_and_shows_every_scope(world: CanonicalWorld) -> None:
    code, payload = world.run("scope", "list")
    assert code == 0, payload
    assert [item["id"] for item in payload["data"]["result"]["items"]] == ["init-00001", "epic-00002", "iss-00003"]
    assert payload["data"]["result"]["snapshot"]["fetched_at"]
    code, payload = world.run("scope", "list", "--kind", "issue", "--state", "completed")
    assert [item["id"] for item in payload["data"]["result"]["items"]] == ["iss-00003"]
    code, payload = world.run("scope", "list", "--parent", "init-00001")
    assert [item["id"] for item in payload["data"]["result"]["items"]] == ["epic-00002"]


def test_a_renamed_title_shows_after_the_refetch(world: CanonicalWorld) -> None:
    world.run("scope", "show", "init-00001")

    def rename(fake: object) -> None:
        issue = fake.issue(1)  # type: ignore[attr-defined]
        issue.title = "新しい計画"
        fake.touch(1)  # type: ignore[attr-defined]

    world.edit(rename)
    world.age_probe()
    code, payload = world.run("scope", "show", "init-00001")
    assert code == 0 and payload["data"]["result"]["scope"]["title"] == "新しい計画"


def test_unchanged_structure_reads_only_conditional_checks(world: CanonicalWorld) -> None:
    world.run("scope", "list")
    world.age_probe()
    before = len(world.requests())
    assert world.run("scope", "show", "iss-00003")[0] == 0
    assert world.run("scope", "list")[0] == 0
    after = world.requests()[before:]
    assert [status for _method, _endpoint, status in after] == [304, 304, 304]
    assert all(method == "GET" for method, _endpoint, _status in after)


def test_a_scope_without_a_directory_shows_a_null_path(world: CanonicalWorld) -> None:
    world.scope("issue", 4, parent=2, directory=False)
    code, payload = world.run("scope", "show", "iss-00004")
    assert code == 0
    assert payload["data"]["result"]["scope"]["path"] is None
    assert payload["data"]["result"]["scope"]["directory_found"] is False


def test_an_unknown_scope_is_not_found(world: CanonicalWorld) -> None:
    code, payload = world.run("scope", "show", "iss-00099")
    assert (code, payload["error"]["code"]) == (4, "SCOPE_NOT_FOUND")


def test_offline_with_a_snapshot_shows_it_with_a_stale_warning(world: CanonicalWorld) -> None:
    world.run("scope", "list")
    world.age_probe()
    world.edit(lambda fake: fake.inject(timeout=True, times=10))
    code, payload = world.run("scope", "show", "init-00001")
    assert code == 0, payload
    assert payload["data"]["result"]["snapshot"]["stale"] is True
    [warning] = payload["warnings"]
    assert warning["code"] == "GITHUB_SNAPSHOT_STALE" and warning["details"]["fetched_at"]


def test_offline_without_a_snapshot_stops_with_the_github_code(world: CanonicalWorld) -> None:
    world.edit(lambda fake: fake.inject(timeout=True, times=10))
    code, payload = world.run("scope", "show", "init-00001")
    assert (code, payload["error"]["code"]) == (5, "GITHUB_UNAVAILABLE")


def test_an_unlinked_checkout_stops_before_reading_github(world: CanonicalWorld) -> None:
    (world.main / "spec-dock/initiatives").unlink()
    code, payload = world.run("scope", "show", "init-00001")
    assert (code, payload["error"]["code"]) == (3, "CANONICAL_NOT_LINKED")
    assert payload["recovery"]["instructions"] == ["spec-dock canonical link"]
    assert world.requests() == []


def test_offline_uses_the_stored_snapshot_without_any_request(world: CanonicalWorld) -> None:
    world.run("scope", "list")
    world.age_probe()
    before = len(world.requests())
    code, payload = world.run("scope", "show", "init-00001", "--offline")
    assert code == 0, payload
    assert world.requests()[before:] == []
    assert payload["data"]["result"]["snapshot"]["stale"] is True
    assert [item["code"] for item in payload["warnings"]] == ["GITHUB_SNAPSHOT_STALE"]


def test_offline_without_a_snapshot_is_a_precondition_failure(world: CanonicalWorld) -> None:
    code, payload = world.run("scope", "list", "--offline")
    assert (code, payload["error"]["code"]) == (3, "PRECONDITION_FAILED")
    assert world.requests() == []


def test_a_leftover_named_or_nested_directory_is_never_a_scope_place(world: CanonicalWorld) -> None:
    world.scope("issue", 4, parent=2, directory=False)
    (world.catalog / "iss-00004-old").mkdir()
    (world.catalog / "epic-00002/issues/iss-00004").mkdir(parents=True)
    code, payload = world.run("scope", "list")
    assert code == 0, payload
    paths = {item["id"]: item["path"] for item in payload["data"]["result"]["items"]}
    assert paths["iss-00004"] is None and paths["epic-00002"] == "spec-dock/initiatives/epic-00002"
    assert all(path is None or path.count("/") == 2 for path in paths.values())
