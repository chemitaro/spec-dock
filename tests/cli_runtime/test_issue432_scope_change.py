"""Canonical-mode `scope edit`, `scope move`, `scope close`, `scope reopen` and `scope delete` (iss-00432)."""

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
    world.scope("issue", 3, "leaf", parent=2)
    return world


def _paths(world: WriteWorld) -> list[str]:
    return [endpoint.split("?")[0] for _, endpoint, _ in world.writes()]


def test_edit_patches_only_the_github_title_and_shows_it_at_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    before = sorted(path.read_bytes() for path in world.find("iss-00003").rglob("*.md"))
    code, payload = world.run("scope", "edit", "iss-00003", "--title", "Renamed Leaf")
    assert code == 0, payload
    assert world.writes() == [("PATCH", "repos/example/repo/issues/3", {"title": "Renamed Leaf"})]
    assert sorted(path.read_bytes() for path in world.find("iss-00003").rglob("*.md")) == before
    assert world.changesets() == []
    graphql = len(world.fake().graphql_requests())
    assert world.run("scope", "show", "iss-00003")[1]["data"]["result"]["scope"]["title"] == "Renamed Leaf"
    assert len(world.fake().graphql_requests()) == graphql
    code, payload = world.run("scope", "edit", "iss-00003", "--title", "Renamed Leaf")
    assert (code, payload["status"]) == (0, "unchanged") and len(world.writes()) == 1


def test_close_writes_state_reasons_and_checks_descendants(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    code, payload = world.write("scope", "close", "epic-00002")
    assert (code, payload["error"]["message"]) == (3, "DESCENDANT_NOT_COMPLETED")
    code, payload = world.write("scope", "close", "iss-00003", "--reason", "not-planned")
    assert code == 0, payload
    assert world.writes()[-1][2] == {"state": "closed", "state_reason": "not_planned"}
    code, payload = world.write("scope", "reopen", "iss-00003")
    assert code == 0 and world.writes()[-1][2] == {"state": "open"}
    code, payload = world.write("scope", "close", "iss-00003")
    assert code == 0 and world.writes()[-1][2] == {"state": "closed", "state_reason": "completed"}
    code, payload = world.write("scope", "close", "epic-00002")
    assert code == 0, payload
    assert payload["data"]["result"]["descendants"] == ["iss-00003"]
    code, payload = world.write("scope", "reopen", "iss-00003")
    assert (code, payload["error"]["message"]) == (3, "ANCESTOR_TERMINAL")
    code, payload = world.run("scope", "close", "iss-00003")
    assert (code, payload["error"]["code"]) == (3, "PRECONDITION_FAILED")


def test_close_stops_on_a_child_in_another_repository(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.edit(lambda fake: fake.add_foreign_issue("other/repo", 9))
    world.edit(lambda fake: fake.set_foreign_child(2, "other/repo", 9))
    world.edit(lambda fake: fake.touch(2))
    world.age_probe()
    code, payload = world.write("scope", "close", "iss-00003")
    assert code == 0, payload
    writes = len(world.writes())
    code, payload = world.write("scope", "close", "epic-00002")
    assert code == 3 and payload["error"]["message"].startswith("DESCENDANT_STATUS_UNKNOWN")
    assert len(world.writes()) == writes


def test_move_reparents_on_github_and_moves_the_directory_with_one_changeset(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.scope("epic", 4, "spare", parent=1)
    world.select("iss-00003", 3)
    code, payload = world.run("scope", "move", "iss-00003", "--parent", "epic-00004")
    assert code == 0, payload
    assert world.writes() == [
        (
            "POST",
            "repos/example/repo/issues/4/sub_issues",
            {"sub_issue_id": world.fake().issue(3).id, "replace_parent": True},
        )
    ]
    assert world.fake().issue(3).parent == ["example/repo", 4]
    moved = world.find("iss-00003")
    assert moved.relative_to(world.catalog).as_posix() == "init-00001-plan/epics/epic-00004-spare/issues/iss-00003-leaf"
    (changeset,) = world.changesets()
    assert changeset["paths"] == ["init-00001-plan/epics/epic-00004-spare/issues/iss-00003-leaf"]
    assert changeset["deletions"] == ["init-00001-plan/epics/epic-00002-core/issues/iss-00003-leaf"]
    issue_link = world.main / "spec-dock/active/issue"
    assert issue_link.resolve() == moved.resolve()
    code, payload = world.run("scope", "move", "iss-00003")
    assert (code, payload["status"]) == (0, "unchanged")


def test_move_without_parent_follows_a_parent_changed_only_on_github(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.scope("epic", 4, "spare", parent=1)
    assert world.run("scope", "show", "iss-00003")[0] == 0
    world.edit(lambda fake: fake.set_parent(3, 4))  # the GitHub UI; the change check cannot see it
    code, payload = world.run("scope", "move", "iss-00003")
    assert code == 0, payload
    assert world.writes() == []
    assert world.find("iss-00003").parent.parent.name == "epic-00004-spare"


def test_move_stops_before_writing_on_wrong_kinds_and_cycles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    for argv in (("iss-00003", "--parent", "init-00001"), ("init-00001", "--parent", "epic-00002")):
        code, payload = world.run("scope", "move", *argv)
        assert (code, payload["error"]["code"]) == (3, "PRECONDITION_FAILED")
    assert world.writes() == [] and world.changesets() == []


def test_delete_backs_up_removes_the_directory_then_detaches_on_github(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.scope("epic", 4, "spare", parent=1)
    world.edit(lambda fake: fake.block(4, by=3))
    backup = tmp_path / "backup"
    code, payload = world.write("scope", "delete", "epic-00002", "--backup-dir", str(backup))
    assert (code, payload["error"]["message"]) == (3, "RECURSIVE_REQUIRED")
    code, payload = world.write("scope", "delete", "epic-00002", "--backup-dir", str(backup), "--recursive")
    assert (code, payload["error"]["message"]) == (3, "DETACH_DEPENDENCIES_REQUIRED")
    assert world.writes() == [] and not backup.exists()
    code, payload = world.write(
        "scope", "delete", "epic-00002", "--backup-dir", str(backup), "--recursive", "--detach-dependencies"
    )
    assert code == 0, payload
    assert [effect["kind"] for effect in payload["effects"]] == [
        "backup",
        "scope.delete",
        "dependency-edge",
        "github.sub-issue.remove",
        "github.issue.label",
        "github.issue.label",
    ]
    assert (backup / "init-00001-plan/epics/epic-00002-core/issues/iss-00003-leaf/plan.md").is_file()
    assert not (world.catalog / "init-00001-plan/epics/epic-00002-core").exists()
    (changeset,) = world.changesets()
    assert changeset["deletions"] == ["init-00001-plan/epics/epic-00002-core"] and changeset["paths"] == []
    fake = world.fake()
    assert fake.issue(2).state == "open" and fake.issue(2).labels == [] and fake.issue(3).labels == []
    assert fake.issue(2).parent is None and fake.issue(4).blocked_by == []
    assert payload["data"]["result"]["removed_ids"] == ["epic-00002", "iss-00003"]


def test_a_delete_stopped_on_github_finishes_when_run_again(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.edit(lambda fake: fake.inject(status=500, body={"message": "x"}, method="DELETE", endpoint="/sub_issue"))
    code, payload = world.write("scope", "delete", "iss-00003", "--backup-dir", str(tmp_path / "b1"))
    assert (code, payload["status"], payload["error"]["code"]) == (6, "partial", "GITHUB_EFFECT_UNKNOWN")
    assert [(item["kind"], item["status"]) for item in payload["effects"]] == [
        ("backup", "succeeded"),
        ("scope.delete", "succeeded"),
        ("github.sub-issue.remove", "unknown"),
        ("github.issue.label", "not_attempted"),
    ]
    assert "run the same spec-dock scope delete iss-00003" in payload["recovery"]["instructions"][0]
    code, payload = world.write("scope", "delete", "iss-00003", "--backup-dir", str(tmp_path / "b2"))
    assert code == 0, payload
    assert [item["kind"] for item in payload["effects"]] == ["github.sub-issue.remove", "github.issue.label"]
    assert world.fake().issue(3).labels == [] and not (tmp_path / "b2").exists()


def test_delete_stops_when_a_descendant_directory_lies_elsewhere(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    leaf = world.find("iss-00003")
    leaf.rename(world.catalog / "init-00001-plan" / leaf.name)
    code, payload = world.write(
        "scope", "delete", "epic-00002", "--backup-dir", str(tmp_path / "b"), "--recursive"
    )
    assert code == 3 and "spec-dock scope move iss-00003" in payload["error"]["message"]
    assert world.writes() == []
