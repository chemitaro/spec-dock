"""Canonical-mode `scope create` and `scope import github` (iss-00432): GitHub first, then the catalog."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from tests.support.canonical_writes import WriteWorld

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def _world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> WriteWorld:
    world = WriteWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "plan")
    return world


def test_an_epic_is_created_on_github_then_published_in_the_catalog_with_one_changeset(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    code, payload = world.write(
        "scope", "create", "epic", "--backend", "github", "--parent", "init-00001", "--title", "Core Work"
    )
    assert code == 0, payload
    fake = world.fake()
    created = fake.issue(2)
    assert created.title == "Core Work" and created.labels == ["spec-dock:epic"]
    assert created.body.endswith("<!-- spec-dock:slug=core-work -->\n") and created.parent == ["example/repo", 1]
    assert [(method, endpoint.split("?")[0]) for method, endpoint, _ in world.writes()] == [
        ("POST", "repos/example/repo/labels"),
        ("POST", "repos/example/repo/issues"),
        ("POST", "repos/example/repo/issues/1/sub_issues"),
    ]
    assert world.writes()[2][2] == {"sub_issue_id": created.id, "replace_parent": False}
    assert world.clock.sleeps == [1.0, 1.0]
    requests = [(item.method, item.endpoint.split("?")[0]) for item in fake.requests]
    assert ("GET", "repos/example/repo/issues/1") in requests[: requests.index(("POST", "repos/example/repo/labels"))]
    directory = world.catalog / "init-00001-plan/epics/epic-00002-core-work"
    assert sorted(path.name for path in directory.iterdir()) == [
        ".workbench", "artifacts", "design.md", "issues", "plan.md", "report.md", "requirement.md"
    ]
    requirement = (directory / "requirement.md").read_text(encoding="utf-8")
    front = requirement.split("---")[1]
    assert 'ID: "epic-00002"' in front and "タイトル" not in front and "親:" not in front
    assert "# epic-00002 Core Work" in requirement
    rules = directory / "artifacts/rules.md"
    assert rules.is_symlink() and os.path.realpath(rules) == os.path.realpath(
        world.main / "spec-dock/docs/rules/epic/artifacts.md"
    )
    assert not list(world.catalog.rglob(".meta.json"))
    (changeset,) = world.changesets()
    assert (changeset["origin"], changeset["command"]) == ("command", "scope create epic")
    assert changeset["paths"] == ["init-00001-plan/epics/epic-00002-core-work"] and changeset["deletions"] == []
    scope = payload["data"]["result"]["scope"]
    assert (scope["id"], scope["title"], scope["path"]) == (
        "epic-00002",
        "Core Work",
        "spec-dock/initiatives/init-00001-plan/epics/epic-00002-core-work",
    )
    graphql = len(fake.graphql_requests())
    code, shown = world.run("scope", "show", "epic-00002")
    assert code == 0 and shown["data"]["result"]["scope"]["parent_id"] == "init-00001"
    assert len(world.fake().graphql_requests()) == graphql


def _create(world: WriteWorld, kind: str, title: str, *extra: str) -> tuple[int, dict[str, object]]:
    return world.write("scope", "create", kind, "--backend", "github", "--title", title, *extra)


def test_an_initiative_and_an_issue_nest_by_their_github_parents(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.scope("epic", 2, "core", parent=1)
    code, payload = _create(world, "initiative", "Next Plan")
    assert code == 0, payload
    assert (world.catalog / "init-00003-next-plan/requirement.md").is_file()
    assert world.fake().issue(3).parent is None
    code, payload = _create(world, "issue", "Leaf Task", "--parent", "epic-00002")
    assert code == 0, payload
    leaf = world.catalog / "init-00001-plan/epics/epic-00002-core/issues/iss-00004-leaf-task"
    front = (leaf / "plan.md").read_text(encoding="utf-8").split("---")[1]
    assert 'ID: "iss-00004"' in front and "親:" not in front
    assert world.fake().issue(4).parent == ["example/repo", 2]
    assert sorted(item["paths"] for item in world.changesets()) == [
        ["init-00001-plan/epics/epic-00002-core/issues/iss-00004-leaf-task"],
        ["init-00003-next-plan"],
    ]


def test_a_parent_closed_only_on_github_is_found_by_the_reread_before_any_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    assert world.run("scope", "show", "init-00001")[0] == 0  # a fresh snapshot that still shows it open

    def close(fake) -> None:  # noqa: ANN001
        fake.issue(1).state, fake.issue(1).state_reason = "closed", "completed"

    world.edit(close)
    code, payload = _create(world, "epic", "Core", "--parent", "init-00001")
    assert (code, payload["error"]["code"]) == (3, "PRECONDITION_FAILED")
    assert world.writes() == [] and world.changesets() == []


def test_unreachable_github_offline_and_a_missing_link_stop_before_writing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.edit(lambda fake: fake.inject(timeout=True, times=20))
    code, payload = _create(world, "epic", "Core", "--parent", "init-00001")
    assert (code, payload["status"], payload["error"]["code"]) == (5, "failed", "GITHUB_UNAVAILABLE")
    world.edit(lambda fake: fake.clear_faults())
    code, payload = world.run(
        "scope", "create", "epic", "--backend", "github", "--parent", "init-00001", "--title", "Core", "--yes", "--offline"
    )
    assert (code, payload["error"]["code"]) == (3, "PRECONDITION_FAILED")
    (world.main / "spec-dock/initiatives").unlink()
    code, payload = _create(world, "epic", "Core", "--parent", "init-00001")
    assert (code, payload["error"]["code"]) == (3, "CANONICAL_NOT_LINKED")
    assert world.writes() == [] and world.changesets() == []
    assert not list(world.catalog.glob("init-00001-plan/epics/*"))


def test_confirmation_and_dry_run_write_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    argv = ("scope", "create", "epic", "--backend", "github", "--parent", "init-00001", "--title", "Core")
    code, payload = world.run(*argv)
    assert (code, payload["error"]["code"]) == (3, "CONFIRMATION_REQUIRED")
    code, payload = world.run(*argv, "--dry-run")
    assert (code, payload["status"]) == (0, "planned")
    assert [item["kind"] for item in payload["effects"]] == ["github-create", "github.sub-issue.add", "scaffold"]
    assert world.writes() == [] and world.changesets() == []


def test_a_failure_after_the_issue_exists_is_partial_and_scope_import_completes_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.edit(lambda fake: fake.inject(status=422, body={"message": "no"}, method="POST", endpoint="/sub_issues"))
    code, payload = _create(world, "epic", "Core", "--parent", "init-00001")
    assert (code, payload["status"]) == (6, "partial")
    assert [(item["kind"], item["status"]) for item in payload["effects"]] == [
        ("github.label.create", "succeeded"),
        ("github-create", "succeeded"),
        ("github.sub-issue.add", "failed"),
        ("scaffold", "not_attempted"),
    ]
    (step,) = payload["recovery"]["instructions"]
    assert "spec-dock scope import github epic gh:example/repo#2 --parent init-00001" in step
    assert world.changesets() == []
    code, payload = world.run(
        "scope", "import", "github", "epic", "gh:example/repo#2", "--parent", "init-00001", "--title", "Core"
    )
    assert code == 0, payload
    assert [item["kind"] for item in payload["effects"]] == ["github.sub-issue.add", "scaffold"]
    fake = world.fake()
    assert len([issue for issue in fake.issues.values() if issue.repository == "example/repo"]) == 2
    assert fake.issue(2).parent == ["example/repo", 1] and world.find("epic-00002").name == "epic-00002-core"
    code, payload = world.run(
        "scope", "import", "github", "epic", "gh:example/repo#2", "--parent", "init-00001", "--title", "Core"
    )
    assert (code, payload["status"], payload["effects"]) == (0, "unchanged", [])


def test_a_lost_create_answer_is_partial_with_an_unknown_issue(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.edit(lambda fake: fake.inject(timeout=True, method="POST", endpoint="repos/example/repo/issues"))
    code, payload = _create(world, "epic", "Core", "--parent", "init-00001")
    assert (code, payload["status"], payload["error"]["code"]) == (6, "partial", "GITHUB_CREATE_IDENTITY_UNKNOWN")
    assert ("github-create", "unknown") in [(item["kind"], item["status"]) for item in payload["effects"]]
    assert "scope import github epic" in payload["recovery"]["instructions"][0]


def test_a_busy_catalog_lock_after_the_github_writes_is_partial(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from spec_dock.runtime.application import canonical_writes
    from spec_dock.runtime.infra.catalog_lock import CatalogLock

    world = _world(tmp_path, monkeypatch, capsys)
    monkeypatch.setattr(canonical_writes, "CATALOG_LOCK_TIMEOUT", 0.0)
    with CatalogLock(world.catalog.resolve(), timeout=0):
        code, payload = _create(world, "epic", "Core", "--parent", "init-00001")
    assert (code, payload["status"], payload["error"]["code"]) == (6, "partial", "CANONICAL_LOCK_BUSY")
    assert payload["effects"][-1] == {"kind": "scaffold", "status": "failed", "target": "epic-00002"}
    assert "scope import github epic gh:example/repo#2" in payload["recovery"]["instructions"][0]


def _import(world: WriteWorld, kind: str, number: int, *extra: str) -> tuple[int, dict[str, object]]:
    return world.run("scope", "import", "github", kind, f"gh:example/repo#{number}", *extra)


def test_import_adds_the_kind_label_marker_parent_and_directory_of_a_plain_issue(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.edit(lambda fake: fake.add_issue(5, title="Existing Work", body="Old body.\r\n"))
    world.edit(lambda fake: fake.add_issue(6, title="Blocker"))
    world.edit(lambda fake: fake.block(5, by=6))
    code, payload = _import(world, "epic", 5, "--parent", "init-00001", "--title", "Existing Work")
    assert code == 0, payload
    assert [(method, endpoint.split("?")[0]) for method, endpoint, _ in world.writes()] == [
        ("POST", "repos/example/repo/labels"),
        ("POST", "repos/example/repo/issues/5/labels"),
        ("PATCH", "repos/example/repo/issues/5"),
        ("POST", "repos/example/repo/issues/1/sub_issues"),
    ]
    issue = world.fake().issue(5)
    assert issue.body == "Old body.\n\n<!-- spec-dock:slug=existing-work -->\n" and issue.labels == ["spec-dock:epic"]
    assert world.find("epic-00005").relative_to(world.catalog).as_posix() == "init-00001-plan/epics/epic-00005-existing-work"
    graphql = len(world.fake().graphql_requests())
    code, shown = world.run("dependency", "list", "epic-00005")
    assert code == 0 and shown["data"]["result"]["external"][0]["number"] == 6
    assert len(world.fake().graphql_requests()) == graphql


def test_import_keeps_an_existing_marker_and_stops_on_conflicts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 2, "other")
    world.edit(lambda fake: fake.add_issue(5, title="Marked", body="<!-- spec-dock:slug=marked -->\n"))
    world.edit(lambda fake: fake.add_issue(7, title="Labelled", labels=["spec-dock:issue"]))
    world.edit(lambda fake: fake.add_issue(8, title="Parented"))
    world.edit(lambda fake: fake.set_parent(8, 2))
    for argv, message in (
        ((5, "--parent", "init-00001", "--title", "Marked", "--slug", "renamed"), "already fixes slug marked"),
        ((7, "--parent", "init-00001", "--title", "Labelled"), "another spec-dock kind label"),
        ((8, "--parent", "init-00001", "--title", "Parented"), "import it with that --parent"),
    ):
        code, payload = _import(world, "epic", *argv)  # type: ignore[arg-type]
        assert (code, payload["error"]["code"]) == (3, "PRECONDITION_FAILED") and message in payload["error"]["message"]
    assert world.writes() == []
    code, payload = _import(world, "epic", 5, "--parent", "init-00001", "--title", "Marked")
    assert code == 0, payload
    assert [endpoint.split("?")[0] for _, endpoint, _ in world.writes()] == [
        "repos/example/repo/labels",
        "repos/example/repo/issues/5/labels",
        "repos/example/repo/issues/1/sub_issues",
    ]
    assert world.find("epic-00005").name == "epic-00005-marked"


def test_importing_an_issue_with_plain_children_does_not_mark_the_snapshot_stale(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.edit(lambda fake: fake.scope("epic", slug="core", number=5))
    world.edit(lambda fake: fake.add_issue(6, title="Plain child"))
    world.edit(lambda fake: fake.set_parent(6, 5))
    code, payload = _import(world, "epic", 5, "--parent", "init-00001", "--title", "Core")
    assert code == 0, payload
    assert [item["code"] for item in payload["warnings"]] == []
