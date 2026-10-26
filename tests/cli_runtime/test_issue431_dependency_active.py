"""canonical dependency and selection reads: blocked-by from the snapshot, links through the catalog (iss-00431)."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

from tests.support.canonical_scopes import CanonicalWorld

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> CanonicalWorld:
    world = CanonicalWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "plan")
    world.scope("epic", 2, "core", parent=1)
    world.scope("issue", 3, "leaf", parent=2)
    world.scope("issue", 4, "base", parent=2)

    def relations(fake: object) -> None:
        fake.add_issue(17, title="Upstream bug")  # type: ignore[attr-defined]
        fake.block(3, by=4)  # type: ignore[attr-defined]
        fake.block(3, by=17)  # type: ignore[attr-defined]

    world.edit(relations)
    return world


def test_dependency_list_shows_scope_and_non_scope_dependencies(world: CanonicalWorld) -> None:
    code, payload = world.run("dependency", "list", "iss-00003")
    assert code == 0, payload
    result = payload["data"]["result"]
    assert (result["declared"], result["effective"]) == (["iss-00004"], ["iss-00004"])
    assert result["external"] == [{"number": 17, "title": "Upstream bug", "state": "open", "declared_by": "iss-00003"}]
    assert result["snapshot"]["fetched_at"]


def test_dependency_check_reports_blockers_and_readiness(world: CanonicalWorld) -> None:
    code, payload = world.run("dependency", "check", "iss-00003")
    assert code == 0, payload
    result = payload["data"]["result"]
    assert result["ready"] is False and result["readiness"]["state"] == "BLOCKED"
    blockers = {(item["code"], item["details"]["number"], item["details"]["role"]) for item in result["blockers"]}
    assert blockers == {("READINESS_BLOCKED", 4, "prerequisite"), ("READINESS_BLOCKED", 17, "external")}
    code, payload = world.run("dependency", "check", "iss-00004")
    assert payload["data"]["result"]["ready"] is True


def test_dependency_check_source_github_refetches(world: CanonicalWorld) -> None:
    world.run("dependency", "check", "iss-00003")
    before = len(world.fake().graphql_requests())
    world.edit(lambda fake: (setattr(fake.issue(4), "state", "closed"), setattr(fake.issue(4), "state_reason", "completed")))
    code, payload = world.run("dependency", "check", "iss-00003", "--source", "github")
    assert code == 0, payload
    assert len(world.fake().graphql_requests()) > before
    roles = [item["details"]["role"] for item in payload["data"]["result"]["blockers"]]
    assert roles == ["external"]


def test_explicit_source_local_and_offline_github_are_refused(world: CanonicalWorld) -> None:
    code, payload = world.run("dependency", "check", "iss-00003", "--source", "local")
    assert (code, payload["error"]["code"]) == (3, "CANONICAL_NOT_APPLICABLE")
    code, payload = world.run("dependency", "check", "iss-00003", "--source", "github", "--offline")
    assert (code, payload["error"]["code"]) == (3, "PRECONDITION_FAILED")


def test_dependency_reads_need_no_link(world: CanonicalWorld) -> None:
    (world.main / "spec-dock/initiatives").unlink()
    assert world.run("dependency", "list", "iss-00003")[0] == 0


def test_active_show_reports_the_selected_scope_place(world: CanonicalWorld) -> None:
    world.select("iss-00003", 3)
    code, payload = world.run("active", "show")
    assert code == 0, payload
    data = payload["data"]
    assert data["selection"]["status"] == "selected" and data["ancestors"] == ["init-00001", "epic-00002"]
    assert data["scope"]["path"] == "spec-dock/initiatives/init-00001-plan/epics/epic-00002-core/issues/iss-00003-leaf"
    assert data["snapshot"]["fetched_at"]


def test_active_set_in_a_linked_worktree_points_links_through_the_catalog(world: CanonicalWorld) -> None:
    linked = world.worktree("feature")
    world.select("iss-00003", 3, checkout=linked)
    code, payload = world.run("active", "set", "iss-00003", "--yes", checkout=linked)
    assert code == 0, payload
    issue = linked / "spec-dock/active/issue"
    assert os.readlink(issue) == "../initiatives/init-00001-plan/epics/epic-00002-core/issues/iss-00003-leaf"
    assert (issue / "requirement.md").is_file()
    assert os.readlink(linked / "spec-dock/active/initiative") == "../initiatives/init-00001-plan"
    for role in ("initiative", "epic", "issue"):
        (linked / "spec-dock/system/active-none" / role).mkdir(parents=True)
    code, payload = world.run("active", "clear", "--all", "--yes", checkout=linked)
    assert code == 0, payload
    assert os.readlink(issue) == "../system/active-none/issue"


def test_active_set_with_a_missing_ancestor_directory_writes_no_link(world: CanonicalWorld) -> None:
    world.select("iss-00003", 3)
    epic = world.catalog / "init-00001-plan/epics/epic-00002-core"
    epic.rename(world.catalog / "moved-away")
    code, payload = world.run("active", "set", "iss-00003", "--yes")
    assert (code, payload["error"]["code"]) == (4, "LOCAL_TARGET_NOT_FOUND")
    assert not (world.main / "spec-dock/active/issue").is_symlink() or "iss-00003" not in os.readlink(
        world.main / "spec-dock/active/issue"
    )


def test_active_set_of_another_scope_requires_work_start(world: CanonicalWorld) -> None:
    world.select("iss-00003", 3)
    code, payload = world.run("active", "set", "iss-00004", "--yes")
    assert (code, payload["error"]["code"]) == (3, "WORK_START_REQUIRED")


def test_artifacts_are_listed_from_the_catalog_in_main_and_linked_worktrees(world: CanonicalWorld) -> None:
    artifacts = world.catalog / "init-00001-plan/epics/epic-00002-core/issues/iss-00003-leaf/artifacts"
    artifacts.mkdir()
    (artifacts / "20261026t000000z-note.md").write_text("# note\n", encoding="utf-8")
    linked = world.worktree("feature")
    for checkout in (world.main, linked):
        code, payload = world.run("artifact", "list", "--scope", "iss-00003", checkout=checkout)
        assert code == 0, payload
        [item] = payload["data"]["result"]["items"]
        assert item["path"].startswith("spec-dock/initiatives/init-00001-plan/epics/")
        assert item["path"].endswith("/artifacts/20261026t000000z-note.md")
        code, payload = world.run("artifact", "show", item["id"], "--scope", "iss-00003", checkout=checkout)
        assert code == 0, payload
        assert payload["data"]["result"]["artifact"]["path"] == item["path"]
