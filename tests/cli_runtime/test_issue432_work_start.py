"""Canonical-mode `work start` (iss-00432): the legacy Start effects plus link, active links and in-progress mark."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.support.canonical_repo import add_worktree, git
from tests.support.canonical_writes import WriteWorld

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def _world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> WriteWorld:
    world = WriteWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "plan")
    world.scope("epic", 2, "core", parent=1)
    world.scope("issue", 3, "日本語の葉", parent=2)
    return world


def test_start_creates_the_id_branch_selects_aligns_links_and_marks_in_progress(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    head = git(world.main, "rev-parse", "HEAD")
    code, payload = world.run("work", "start", "iss-3", "--base", "HEAD")
    assert code == 0, payload
    assert git(world.main, "branch", "--show-current") == "iss-00003"
    assert git(world.main, "rev-parse", "iss-00003") == head
    result = payload["data"]
    assert (result["scope_id"], result["started"], result["branch_after"]) == ("iss-00003", True, "iss-00003")
    kinds = [item["kind"] for item in payload["effects"]]
    assert kinds[:3] == ["git.branch.create", "git.checkout", "selection.publish"]
    assert "active.link" in kinds and kinds[-2:] == ["github.issue.label", "github.issue.assignee"]
    assert (world.main / "spec-dock/active/issue").resolve() == (world.catalog / "00000-00999/iss-00003").resolve()
    issue = world.fake().issue(3)
    assert "spec-dock:in-progress" in issue.labels and issue.assignees == ["fixture-user"]
    assert world.run("active", "show")[1]["data"]["selection"]["scope_id"] == "iss-00003"
    code, payload = world.run("work", "start", "iss-00003", "--branch", "iss-00003")
    assert (code, payload["status"]) == (0, "unchanged"), payload
    assert [item["code"] for item in payload["warnings"]] == ["SCOPE_IN_PROGRESS"]


def test_a_worktree_without_a_link_gets_one_and_its_active_links(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    plain = add_worktree(world.main, tmp_path / "plain", "plain")
    code, payload = world.run("work", "start", "iss-00003", "--base", "HEAD", checkout=plain)
    assert code == 0, payload
    assert (plain / "spec-dock/initiatives").is_symlink()
    assert (plain / "spec-dock/active/issue/requirement.md").is_file()


def test_a_blocked_link_place_is_a_warning_and_start_still_succeeds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    plain = add_worktree(world.main, tmp_path / "plain", "plain")
    (plain / "spec-dock/initiatives").unlink(missing_ok=True)
    (plain / "spec-dock/initiatives").write_text("occupied\n", encoding="utf-8")
    git(plain, "update-index", "--assume-unchanged", "spec-dock/initiatives", check=False)
    code, payload = world.run("work", "start", "iss-00003", "--base", "HEAD", checkout=plain)
    assert code == 0, payload
    assert payload["status"] == "succeeded"
    codes = [item["code"] for item in payload["warnings"]]
    assert "ACTIVE_LINK_NOT_UPDATED" in codes
    assert any("canonical link" in str(item["details"].get("next_step", "")) for item in payload["warnings"])


def test_a_base_with_specs_and_unready_scopes_stop_before_any_effect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    old = add_worktree(world.main, tmp_path / "old", "legacy-specs")
    (old / "spec-dock/initiatives").unlink(missing_ok=True)
    (old / "spec-dock/initiatives/x").mkdir(parents=True)
    (old / "spec-dock/initiatives/x/a.md").write_text("a\n", encoding="utf-8")
    git(old, "add", "-f", "spec-dock/initiatives")
    git(old, "commit", "-qm", "specs")
    git(world.main, "worktree", "remove", "--force", str(old))
    before = git(world.main, "rev-parse", "HEAD"), git(world.main, "branch", "--show-current")
    code, payload = world.run("work", "start", "iss-00003", "--base", "legacy-specs")
    assert (code, payload["error"]["code"]) == (3, "CANONICAL_BASE_HAS_SPECS")
    world.scope("issue", 4, "blocker", parent=2)
    world.edit(lambda fake: fake.block(3, by=4))
    code, payload = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert (code, payload["error"]["code"]) == (3, "READINESS_NOT_SATISFIED")
    assert payload["error"]["details"]["state"] == "BLOCKED"
    assert payload["error"]["details"]["blockers"][0]["scope_id"] == "iss-00004"
    world.edit(lambda fake: fake.issue(3).labels.append("spec-dock:in-progress"))
    code, payload = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert (code, payload["error"]["code"]) == (3, "READINESS_NOT_SATISFIED")
    assert (git(world.main, "rev-parse", "HEAD"), git(world.main, "branch", "--show-current")) == before
    assert git(world.main, "rev-parse", "--verify", "--quiet", "iss-00003", check=False) == ""
    assert world.run("active", "show")[1]["data"]["selection"]["status"] == "empty"
    assert world.writes() == []


def test_a_ready_scope_in_progress_warns_and_a_failed_mark_is_only_a_warning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.edit(lambda fake: fake.issue(3).labels.append("spec-dock:in-progress"))
    world.edit(lambda fake: fake.issue(3).assignees.append("someone"))
    world.edit(lambda fake: fake.inject(status=500, body={"message": "x"}, method="POST", endpoint="/assignees"))
    code, payload = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert (code, payload["status"]) == (0, "succeeded"), payload
    by_code = {item["code"]: item for item in payload["warnings"]}
    assert by_code["SCOPE_IN_PROGRESS"]["details"]["assignees"] == ["someone"]
    mark = by_code["CANONICAL_PROGRESS_MARK_FAILED"]["details"]
    assert mark["writes"] == [{"kind": "github.issue.assignee", "status": "unknown"}] or mark["writes"] == [
        {"kind": "github.issue.assignee", "status": "failed"}
    ]
    assert all(item["status"] == "succeeded" for item in payload["effects"] if item["kind"].startswith("github"))


def test_a_kind_change_of_an_ancestor_stops_start(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.edit(lambda fake: setattr(fake.issue(2), "labels", ["spec-dock:initiative"]))
    code, payload = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert (code, payload["error"]["code"]) == (3, "SCOPE_KIND_CHANGED")
    assert git(world.main, "rev-parse", "--verify", "--quiet", "iss-00003", check=False) == ""
    assert world.writes() == []
