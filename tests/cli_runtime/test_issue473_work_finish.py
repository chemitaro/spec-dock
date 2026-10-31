"""`work finish` checks a CUE Scope before closing it (iss-00473 AC-09..AC-11; R-B7 of epic-00425)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.application import canonical_scopes, canonical_work, canonical_writes
from spec_dock.runtime.application.canonical_catalog import catalog_changes
from spec_dock.runtime.infra import github_structure
from spec_dock.runtime.infra.github_structure import GithubRepository
from tests.support.canonical_repo import git
from tests.support.canonical_scopes import REPOSITORY
from tests.support.canonical_writes import WriteWorld
from tests.support.cue import cue_executable
from tests.support.cue_scopes import hide_cue, place_sample, skeleton_explanation

if TYPE_CHECKING:
    from pathlib import Path

    from tests.support.canonical_sync import FakeScheduler


class _Clock:
    def __init__(self) -> None:
        self.offset = 0.0

    def now(self) -> datetime:
        return datetime.now(timezone.utc) + timedelta(seconds=self.offset)

    def monotonic(self) -> float:
        return self.offset

    def sleep(self, seconds: float) -> None:
        self.offset += seconds


@pytest.fixture
def world(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    periodic_jobs: dict[str, FakeScheduler],
) -> WriteWorld:
    cue_executable()
    world = WriteWorld.create(tmp_path, monkeypatch, capsys)
    git(world.main, "remote", "set-url", "origin", str(tmp_path / "remote.git"))
    repository = GithubRepository.parse(REPOSITORY)
    for module in (github_structure, canonical_writes, canonical_scopes):
        monkeypatch.setattr(module, "repository_for_checkout", lambda root, *, timeout: repository)
    monkeypatch.setattr(canonical_work, "SAVE_CLOCK", _Clock())
    world.scope("initiative", 1, "plan")
    world.scope("epic", 2, "core", parent=1)
    world.scope("issue", 3, "cue leaf", parent=2, documents=())
    world.scope("issue", 4, "markdown leaf", parent=2)
    place_sample(world.catalog / world.relative("issue", 3), "issue-strict-complete")
    with catalog_changes(world.catalog.resolve(), command="test setup") as changes:
        for kind, number in (("initiative", 1), ("epic", 2), ("issue", 3), ("issue", 4)):
            changes.add(world.relative(kind, number).as_posix())
    assert world.run("canonical", "sync")[0] == 0
    for scheduler in periodic_jobs.values():
        scheduler.simulate_run = False

        def kick() -> None:
            code, payload = world.run("canonical", "sync")
            assert code == 0, payload

        scheduler.on_kick = kick
    world.jobs = periodic_jobs  # type: ignore[attr-defined]
    return world


def plan(world: WriteWorld) -> Path:
    return world.find("iss-00003") / "plan.cue"


def break_plan(world: WriteWorld) -> str:
    text = plan(world).read_text(encoding="utf-8")
    plan(world).write_text(text.replace('verifies: ["F-01"]', 'verifies: ["R-01"]'), encoding="utf-8")
    return text


def untouched(world: WriteWorld) -> None:
    assert world.changesets() == [] and world.writes() == []
    assert world.fake().issue(3).state == "open"
    assert world.run("active", "show")[1]["data"]["selection"]["scope_id"] == "iss-00003"


def test_errors_stop_finish_before_anything_is_written(world: WriteWorld) -> None:
    world.select("iss-00003", 3)
    break_plan(world)
    code, payload = world.write("work", "finish", "iss-3")
    assert (code, payload["status"], payload["error"]["code"]) == (3, "failed", "SCOPE_CHECK_FAILED")
    errors = payload["error"]["details"]["errors"]
    assert [(item["code"], item["details"]["rule"]) for item in errors] == [("SPEC_FINDINGS", "failure-without-test")]
    assert errors[0]["details"]["file"] == "spec-dock/initiatives/00000-00999/iss-00003/requirement.cue"
    steps = " ".join(payload["recovery"]["instructions"])
    assert "spec-dock scope check iss-00003" in steps and "spec-dock work finish iss-00003 --yes" in steps
    assert payload["effects"] == []
    untouched(world)


def test_dry_run_stops_the_same_way(world: WriteWorld) -> None:
    world.select("iss-00003", 3)
    break_plan(world)
    code, payload = world.run("work", "finish", "iss-3", "--dry-run")
    assert (code, payload["error"]["code"]) == (3, "SCOPE_CHECK_FAILED")
    untouched(world)


def test_fixing_the_errors_lets_finish_close_and_release(world: WriteWorld) -> None:
    world.select("iss-00003", 3)
    original = break_plan(world)
    assert world.write("work", "finish", "iss-3")[0] == 3
    plan(world).write_text(original, encoding="utf-8")
    code, payload = world.write("work", "finish", "iss-3")
    assert code == 0, payload
    assert world.fake().issue(3).state == "closed"
    assert world.run("active", "show")[1]["data"]["selection"]["status"] == "empty"


def test_explanation_warnings_alone_do_not_stop_finish(world: WriteWorld) -> None:
    (world.find("iss-00003") / "explanation.html").write_text(skeleton_explanation(), encoding="utf-8")
    code, payload = world.write("work", "finish", "iss-3")
    assert code == 0, payload
    assert "EXPLANATION_SKELETON" in {item["code"] for item in payload["warnings"]}
    assert world.fake().issue(3).state == "closed"


def test_a_missing_cue_stops_a_cue_scope_but_not_a_markdown_one(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    hide_cue(monkeypatch)
    code, payload = world.write("work", "finish", "iss-3")
    assert (code, payload["error"]["code"]) == (3, "CUE_NOT_FOUND")
    assert world.changesets() == [] and world.fake().issue(3).state == "open"
    code, payload = world.write("work", "finish", "iss-4")
    assert code == 0, payload
    assert world.fake().issue(4).state == "closed"


def test_an_already_completed_scope_releases_with_warnings(world: WriteWorld, monkeypatch: pytest.MonkeyPatch) -> None:
    world.select("iss-00003", 3)
    break_plan(world)
    world.edit(lambda fake: setattr(fake.issue(3), "state", "closed"))
    world.edit(lambda fake: setattr(fake.issue(3), "state_reason", "completed"))
    code, payload = world.write("work", "finish", "iss-3")
    assert code == 0, payload
    [warning] = [item for item in payload["warnings"] if item["code"] == "SCOPE_CHECK_FAILED"]
    assert warning["details"]["errors"][0]["code"] == "SPEC_FINDINGS"
    assert world.run("active", "show")[1]["data"]["selection"]["status"] == "empty"
    world.select("iss-00003", 3)
    hide_cue(monkeypatch)
    code, payload = world.write("work", "finish", "iss-3")
    assert code == 0, payload
    assert "CUE_NOT_FOUND" in {item["code"] for item in payload["warnings"]}


def test_a_scope_without_a_directory_is_not_checked(world: WriteWorld, monkeypatch: pytest.MonkeyPatch) -> None:
    world.scope("issue", 5, "no directory", parent=2, directory=False)
    hide_cue(monkeypatch)
    code, payload = world.write("work", "finish", "iss-5")
    assert code == 0, payload
    assert world.fake().issue(5).state == "closed"


def test_a_completed_scope_reopened_while_waiting_is_not_closed_with_errors(world: WriteWorld) -> None:
    world.select("iss-00003", 3)
    break_plan(world)  # unsaved: finish writes a changeset and waits for the cycle
    world.edit(lambda fake: setattr(fake.issue(3), "state", "closed"))
    world.edit(lambda fake: setattr(fake.issue(3), "state_reason", "completed"))

    def reopen_then_sync() -> None:
        world.edit(lambda fake: setattr(fake.issue(3), "state", "open"))
        world.edit(lambda fake: setattr(fake.issue(3), "state_reason", None))
        world.edit(lambda fake: fake.touch(3))
        code, payload = world.run("canonical", "sync")
        assert code == 0, payload

    for scheduler in world.jobs.values():  # type: ignore[attr-defined]
        scheduler.on_kick = reopen_then_sync
    code, payload = world.write("work", "finish", "iss-3")
    assert (code, payload["status"], payload["error"]["code"]) == (6, "partial", "SCOPE_CHECK_FAILED"), payload
    assert ("github.issue.close", "not_attempted") in [(item["kind"], item["status"]) for item in payload["effects"]]
    assert world.fake().issue(3).state == "open"
