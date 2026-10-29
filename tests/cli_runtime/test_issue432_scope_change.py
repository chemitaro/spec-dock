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
    code, payload = world.write("scope", "close", "iss-00003")
    assert code == 0, payload
    writes = len(world.writes())
    code, payload = world.write("scope", "close", "epic-00002")
    assert code == 3 and payload["error"]["message"].startswith("DESCENDANT_STATUS_UNKNOWN")
    assert len(world.writes()) == writes


def test_move_reparents_only_on_github_and_leaves_the_catalog_alone(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.scope("epic", 4, "spare", parent=1)
    before = sorted(path.relative_to(world.catalog).as_posix() for path in world.catalog.rglob("*"))
    code, payload = world.run("scope", "move", "iss-3", "--parent", "EPIC-4")
    assert code == 0, payload
    assert world.writes() == [
        (
            "POST",
            "repos/example/repo/issues/4/sub_issues",
            {"sub_issue_id": world.fake().issue(3).id, "replace_parent": True},
        )
    ]
    assert world.fake().issue(3).parent == ["example/repo", 4]
    assert payload["data"]["result"]["scope"]["parent_id"] == "epic-00004"
    assert sorted(path.relative_to(world.catalog).as_posix() for path in world.catalog.rglob("*")) == before
    assert world.changesets() == []
    graphql = len(world.fake().graphql_requests())
    assert world.run("scope", "show", "iss-00003")[1]["data"]["result"]["scope"]["parent_id"] == "epic-00004"
    assert len(world.fake().graphql_requests()) == graphql
    code, payload = world.run("scope", "move", "iss-00003", "--parent", "epic-00004")
    assert (code, payload["status"]) == (0, "unchanged")


def test_move_needs_parent_and_stops_before_writing_on_wrong_kinds_cycles_and_kind_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    code, payload = world.run("scope", "move", "iss-00003")
    assert (code, payload["error"]["code"]) == (2, "USAGE_ERROR") and "--parent" in payload["error"]["message"]
    for argv in (("iss-00003", "--parent", "init-00001"), ("init-00001", "--parent", "epic-00002")):
        code, payload = world.run("scope", "move", *argv)
        assert (code, payload["error"]["code"]) == (3, "PRECONDITION_FAILED")
    world.scope("epic", 4, "spare", parent=1)
    world.edit(lambda fake: setattr(fake.issue(4), "labels", ["spec-dock:initiative"]))
    world.directory("initiative", 4)
    code, payload = world.run("scope", "move", "iss-00003", "--parent", "epic-00004")
    assert (code, payload["error"]["code"]) == (3, "SCOPE_KIND_CHANGED")
    assert world.writes() == [] and world.changesets() == []


def test_delete_backs_up_and_removes_each_flat_directory_then_detaches_on_github(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.scope("epic", 4, "spare", parent=1)
    world.scope("issue", 1234, "far", parent=2)
    world.edit(lambda fake: fake.block(4, by=3))
    backup = tmp_path / "backup"
    code, payload = world.write("scope", "delete", "epic-00002", "--backup-dir", str(backup))
    assert (code, payload["error"]["message"]) == (3, "RECURSIVE_REQUIRED")
    code, payload = world.write("scope", "delete", "epic-00002", "--backup-dir", str(backup), "--recursive")
    assert (code, payload["error"]["message"]) == (3, "DETACH_DEPENDENCIES_REQUIRED")
    assert world.writes() == [] and not backup.exists()
    code, payload = world.write(
        "scope", "delete", "epic-2", "--backup-dir", str(backup), "--recursive", "--detach-dependencies"
    )
    assert code == 0, payload
    assert [(effect["kind"], effect["target"]) for effect in payload["effects"]][:4] == [
        ("backup", str(backup)),
        ("scope.delete", "00000-00999/epic-00002"),
        ("scope.delete", "00000-00999/iss-00003"),
        ("scope.delete", "01000-01999/iss-01234"),
    ]
    assert [effect["kind"] for effect in payload["effects"]][4:] == [
        "dependency-edge",
        "github.sub-issue.remove",
        "github.issue.label",
        "github.issue.label",
        "github.issue.label",
    ]
    for relative in ("00000-00999/epic-00002", "00000-00999/iss-00003", "01000-01999/iss-01234"):
        assert (backup / relative / "plan.md").is_file() and not (world.catalog / relative).exists()
    assert (world.catalog / "00000-00999/epic-00004").is_dir() and not (world.catalog / "01000-01999").exists()
    (changeset,) = world.changesets()
    assert changeset["paths"] == []
    assert changeset["deletions"] == ["00000-00999/epic-00002", "00000-00999/iss-00003", "01000-01999/iss-01234"]
    fake = world.fake()
    assert fake.issue(2).state == "open" and fake.issue(2).labels == [] and fake.issue(3).labels == []
    assert fake.issue(2).parent is None and fake.issue(4).blocked_by == []
    assert payload["data"]["result"]["removed_ids"] == ["epic-00002", "iss-00003", "iss-01234"]


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


def test_a_delete_with_some_directories_already_gone_removes_only_the_rest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    import shutil

    shutil.rmtree(world.find("iss-00003"))
    backup = tmp_path / "b"
    code, payload = world.write("scope", "delete", "epic-00002", "--backup-dir", str(backup), "--recursive")
    assert code == 0, payload
    assert [(item["kind"], item["target"]) for item in payload["effects"] if item["kind"] == "scope.delete"] == [
        ("scope.delete", "00000-00999/epic-00002")
    ]
    assert (backup / "00000-00999/epic-00002/plan.md").is_file() and not (backup / "00000-00999/iss-00003").exists()
    assert world.fake().issue(3).labels == []


def test_delete_of_a_kind_changed_scope_backs_up_and_removes_the_old_kind_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.edit(lambda fake: setattr(fake.issue(3), "labels", ["spec-dock:epic"]))
    code, payload = world.run("scope", "edit", "epic-00003", "--title", "X")
    assert (code, payload["error"]["code"]) == (3, "SCOPE_KIND_CHANGED")
    code, payload = world.run("scope", "close", "iss-00003", "--yes")
    assert (code, payload["error"]["code"]) == (3, "SCOPE_KIND_CHANGED")
    assert world.writes() == []
    backup = tmp_path / "b"
    code, payload = world.write("scope", "delete", "epic-00003", "--backup-dir", str(backup))
    assert code == 0, payload
    assert (backup / "00000-00999/iss-00003/plan.md").is_file()
    assert not (world.catalog / "00000-00999/iss-00003").exists()
    assert world.fake().issue(3).labels == []
