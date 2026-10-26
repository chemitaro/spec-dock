"""canonical `workspace validate/sync/doctor` and `canonical status --structure` (iss-00431)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

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
    return world


def codes(items: list[dict[str, Any]]) -> set[str]:
    return {item["code"] for item in items}


def test_a_consistent_workspace_is_valid(world: CanonicalWorld) -> None:
    code, payload = world.run("workspace", "validate", "--require-nodes")
    assert code == 0, payload
    result = payload["data"]["result"]
    assert (result["valid"], result["node_count"], result["findings"]) == (True, 3, [])
    assert result["snapshot"]["fetched_at"] and payload["warnings"] == []


def test_validate_finds_every_error_item(world: CanonicalWorld) -> None:
    world.scope("issue", 4, "nodir", parent=2, directory=False)
    world.scope("issue", 5, "thin", parent=2, documents=("requirement.md",))
    world.edit(lambda fake: fake.add_issue(6, title="no marker", labels=["spec-dock:issue"]))
    world.directory("issue", 7, "stray", parent=2)
    world.directory("issue", 3, "copy", parent=2)
    world.scope("issue", 8, "named", parent=2, directory=False)
    world.directory("issue", 8, "other-name", parent=2)
    (world.catalog / "init-00001-plan/.meta.json").write_text("{}", encoding="utf-8")

    def cycle(fake: Any) -> None:
        fake.scope("issue", slug="a", number=9, parent=2)
        fake.scope("issue", slug="b", number=10, parent=2)
        fake.block(9, by=10)
        fake.block(10, by=9)

    world.edit(cycle)
    world.directory("issue", 9, "a", parent=2)
    world.directory("issue", 10, "b", parent=2)
    code, payload = world.run("workspace", "validate")
    assert (code, payload["error"]["code"]) == (7, "WORKSPACE_VALIDATION_FAILED")
    found = codes(payload["data"]["result"]["findings"])
    assert {
        "SCOPE_DIRECTORY_MISSING",
        "SCOPE_DOCUMENT_MISSING",
        "SLUG_MARKER_MISSING",
        "SCOPE_ISSUE_MISSING",
        "SCOPE_DIRECTORY_DUPLICATE",
        "SCOPE_DIRECTORY_SLUG_MISMATCH",
        "SCOPE_METADATA_PRESENT",
        "DEPENDENCY_CYCLE",
    } <= found


def test_validate_finds_kind_and_parent_errors(world: CanonicalWorld) -> None:
    world.scope("issue", 4, "orphan")  # an Issue directly under no Epic
    code, payload = world.run("workspace", "validate")
    assert code == 7
    assert codes(payload["data"]["result"]["findings"]) & {"PARENT_MISSING", "PARENT_INVALID"}


def test_validate_warns_about_drift_conflicts_and_non_scope_dependencies(world: CanonicalWorld) -> None:
    world.scope("epic", 4, "moved", parent=1, directory=False)
    world.directory("epic", 4, "moved")  # at the catalog root instead of under init-00001
    leaf = world.catalog / "init-00001-plan/epics/epic-00002-core/issues/iss-00003-leaf"
    (leaf / "requirement.conflict-20261026.md").write_text("x", encoding="utf-8")

    def external(fake: Any) -> None:
        fake.add_issue(17, title="Upstream")
        fake.block(3, by=17)

    world.edit(external)
    code, payload = world.run("workspace", "validate")
    assert code == 0, payload
    warnings = {item["code"]: item for item in payload["warnings"]}
    assert set(warnings) == {"SCOPE_DIRECTORY_MISPLACED", "CANONICAL_CONFLICT_COPY", "DEPENDENCY_NOT_SCOPE"}
    assert warnings["SCOPE_DIRECTORY_MISPLACED"]["details"]["next_step"] == "spec-dock scope move epic-00004"
    assert warnings["SCOPE_DIRECTORY_MISPLACED"]["details"]["expected"] == "init-00001-plan/epics/epic-00004-moved"


def test_validate_ci_points_at_canonical_check(world: CanonicalWorld) -> None:
    code, payload = world.run("workspace", "validate", "--ci")
    assert (code, payload["error"]["code"]) == (3, "CANONICAL_NOT_APPLICABLE")
    assert payload["recovery"]["instructions"] == ["Run spec-dock canonical check to check a commit in CI."]


def test_sync_observes_worktrees_without_the_catalog(world: CanonicalWorld) -> None:
    linked = world.worktree("feature")
    world.select("iss-00003", 3, checkout=linked)
    code, payload = world.run("workspace", "sync")
    assert code == 0, payload
    data = payload["data"]
    assert data["source"] == "snapshot" and data["snapshot"]["fetched_at"]
    rows = {row["path"]: row for row in data["worktrees"]}
    assert set(rows) == {str(world.main), str(linked)}
    assert rows[str(linked)]["selection"]["scope_id"] == "iss-00003" and rows[str(linked)]["lifecycle"] == "open"
    assert {item["scope_id"] for item in data["scopes"]} == {"init-00001", "epic-00002", "iss-00003"}


def test_sync_source_github_refetches_and_explicit_local_is_refused(world: CanonicalWorld) -> None:
    world.run("workspace", "sync")
    before = len(world.fake().graphql_requests())
    code, payload = world.run("workspace", "sync", "--source", "github")
    assert code == 0 and payload["data"]["source"] == "github"
    assert len(world.fake().graphql_requests()) > before
    code, payload = world.run("workspace", "sync", "--source", "local")
    assert (code, payload["error"]["code"]) == (3, "CANONICAL_NOT_APPLICABLE")


def test_doctor_shows_the_canonical_status_items(world: CanonicalWorld) -> None:
    code, payload = world.run("workspace", "doctor")
    assert code == 0, payload
    assert set(payload["data"]["canonical"]) >= {"catalog", "link", "structure", "snapshot"}


def test_doctor_without_a_link_reports_it_as_a_finding(world: CanonicalWorld) -> None:
    (world.main / "spec-dock/initiatives").unlink()
    code, payload = world.run("workspace", "doctor")
    assert code == 7
    assert "CANONICAL_NOT_LINKED" in codes(payload["data"]["findings"])
    assert payload["data"]["canonical"]["link"]["status"] != "ok"


def test_status_structure_is_not_checked_without_the_flag(world: CanonicalWorld) -> None:
    code, payload = world.run("canonical", "status")
    assert code == 0
    assert payload["data"]["structure"] == {"status": "not_checked", "next_step": None}
    assert world.requests() == []


def test_status_structure_reports_nesting_drift(world: CanonicalWorld) -> None:
    world.scope("epic", 4, "moved", parent=1, directory=False)
    world.directory("epic", 4, "moved")
    code, payload = world.run("canonical", "status", "--structure")
    assert code == 0, payload
    item = payload["data"]["structure"]
    assert item["status"] == "problem" and item["next_step"] == "spec-dock scope move epic-00004"
    assert [entry["scope_id"] for entry in item["misplaced"]] == ["epic-00004"]
    assert item["snapshot"]["fetched_at"]
    assert any(warning["code"] == "SCOPE_DIRECTORY_MISPLACED" for warning in payload["warnings"])


def test_an_initiative_with_a_parent_is_a_finding_not_a_crash(world: CanonicalWorld) -> None:
    world.scope("initiative", 4, "nested", parent=1, directory=False)
    world.directory("initiative", 4, "nested")
    code, payload = world.run("workspace", "validate")
    assert (code, payload["error"]["code"]) == (7, "WORKSPACE_VALIDATION_FAILED")
    assert "PARENT_INVALID" in codes(payload["data"]["result"]["findings"])
    code, payload = world.run("canonical", "status", "--structure")
    assert code == 0, payload
    assert payload["data"]["structure"]["status"] in ("ok", "problem")
    assert world.run("workspace", "doctor")[0] == 7


def test_each_snapshot_anomaly_is_a_validate_finding(world: CanonicalWorld) -> None:
    def broken(fake: Any) -> None:
        fake.add_issue(
            4, title="two kinds", labels=["spec-dock:issue", "spec-dock:epic"], body="<!-- spec-dock:slug=two -->"
        )
        fake.add_issue(
            5,
            title="two markers",
            labels=["spec-dock:issue"],
            body="<!-- spec-dock:slug=a -->\n<!-- spec-dock:slug=b -->",
        )
        fake.add_issue(6, title="bad marker", labels=["spec-dock:issue"], body="<!-- spec-dock:slug=Bad_Slug -->")
        fake.add_foreign_issue("other/repo", 9)
        fake.block(3, by=9, repository="other/repo")

    world.edit(broken)
    code, payload = world.run("workspace", "validate")
    assert code == 7
    assert {
        "KIND_LABEL_MULTIPLE",
        "SLUG_MARKER_MULTIPLE",
        "SLUG_MARKER_INVALID",
        "DEPENDENCY_FOREIGN_REPOSITORY",
    } <= codes(payload["data"]["result"]["findings"])


def test_doctor_reports_an_unreadable_structure_as_a_finding(world: CanonicalWorld) -> None:
    code, payload = world.run("workspace", "doctor", "--offline")
    assert code == 7, payload
    assert payload["data"]["canonical"] is not None
    assert "PRECONDITION_FAILED" in codes(payload["data"]["findings"])


def test_sync_observes_a_schema_three_worktree_and_an_unreadable_one(world: CanonicalWorld) -> None:
    import json

    from tests.support.canonical_repo import add_worktree

    legacy = add_worktree(world.main, world.tmp_path / "legacy", "legacy")
    (legacy / "spec-dock/workspace.json").write_text(
        json.dumps({"schema_version": 3, "writer_protocol": "specdock.worktree-writer/v1"}), encoding="utf-8"
    )
    broken = add_worktree(world.main, world.tmp_path / "broken", "broken")
    (broken / "spec-dock/workspace.json").write_text("{", encoding="utf-8")
    code, payload = world.run("workspace", "sync")
    rows = {row["path"]: row for row in payload["data"]["worktrees"]}
    assert rows[str(legacy)]["selection"]["status"] == "empty"
    assert [item["code"] for item in rows[str(broken)]["findings"]] == ["WORKTREE_SELECTION_UNAVAILABLE"]
    assert (code, payload["status"]) == (7, "partial")
