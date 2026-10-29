"""Canonical-mode `work finish` (iss-00432, AC-13): close only after the Scope's catalog places reach GitHub."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.application import canonical_scopes, canonical_work, canonical_writes
from spec_dock.runtime.application.canonical_catalog import catalog_changes
from spec_dock.runtime.domain.canonical_sync_state import CatalogSyncState, Hold
from spec_dock.runtime.infra import github_structure
from spec_dock.runtime.infra.canonical_state import update_catalog_state
from spec_dock.runtime.infra.github_structure import GithubRepository
from spec_dock.runtime.infra.state_root import resolve_state_root
from tests.support.canonical_repo import clone, git
from tests.support.canonical_scopes import REPOSITORY
from tests.support.canonical_writes import WriteWorld

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
    world = WriteWorld.create(tmp_path, monkeypatch, capsys)
    # The catalog pushes to the temporary bare remote; only the structure stays on the fake GitHub repository.
    git(world.main, "remote", "set-url", "origin", str(tmp_path / "remote.git"))
    repository = GithubRepository.parse(REPOSITORY)
    for module in (github_structure, canonical_writes, canonical_scopes):
        monkeypatch.setattr(module, "repository_for_checkout", lambda root, *, timeout: repository)
    clock = _Clock()
    monkeypatch.setattr(canonical_work, "SAVE_CLOCK", clock)
    world.scope("initiative", 1, "plan")
    world.scope("epic", 2, "core", parent=1)
    world.scope("issue", 3, "leaf", parent=2)
    world.edit(lambda fake: fake.issue(3).labels.append("spec-dock:in-progress"))
    with catalog_changes(world.catalog.resolve(), command="test setup") as changes:
        for kind, number in (("initiative", 1), ("epic", 2), ("issue", 3)):
            changes.add(world.relative(kind, number).as_posix())
    assert world.run("canonical", "sync")[0] == 0  # the Scope directories are saved and pushed at once
    for scheduler in periodic_jobs.values():
        scheduler.simulate_run = False
    world.jobs = periodic_jobs  # type: ignore[attr-defined]
    world.save_clock = clock  # type: ignore[attr-defined]
    return world


def _run_cycle_on_kick(world: WriteWorld, also: object = None) -> None:
    def kick() -> None:
        code, payload = world.run("canonical", "sync")
        assert code == 0, payload
        if callable(also):
            also()

    for scheduler in world.jobs.values():  # type: ignore[attr-defined]
        scheduler.on_kick = kick


def _remote_file(world: WriteWorld, relative: str) -> str:
    return git(world.tmp_path / "remote.git", "show", f"spec-dock/canonical:{relative}")


def test_finish_saves_waits_for_the_push_then_closes_unmarks_and_releases(world: WriteWorld) -> None:
    world.select("iss-00003", 3)
    design = world.find("iss-00003") / "design.md"
    design.write_text("# design\n\nchanged before finish\n", encoding="utf-8")
    _run_cycle_on_kick(world)
    code, payload = world.write("work", "finish", "iss-3")
    assert code == 0, payload
    kinds = [(item["kind"], item["status"]) for item in payload["effects"]]
    assert kinds[0] == ("catalog.changeset", "succeeded")
    assert ("github.issue.close", "succeeded") in kinds and ("github.issue.label", "succeeded") in kinds
    assert ("selection.clear", "succeeded") in kinds
    assert "changed before finish" in _remote_file(world, "00000-00999/iss-00003/design.md")
    issue = world.fake().issue(3)
    assert (issue.state, issue.state_reason) == ("closed", "completed")
    assert "spec-dock:in-progress" not in issue.labels
    assert world.run("active", "show")[1]["data"]["selection"]["status"] == "empty"
    assert payload["data"]["completed"] is True


def test_a_deleted_directory_is_saved_before_closing(world: WriteWorld) -> None:
    import shutil

    shutil.rmtree(world.find("iss-00003"))
    _run_cycle_on_kick(world)
    code, payload = world.write("work", "finish", "iss-00003")
    assert code == 0, payload
    assert payload["effects"][0]["kind"] == "catalog.changeset"
    assert not git(world.tmp_path / "remote.git", "ls-tree", "-r", "spec-dock/canonical", "00000-00999/iss-00003")


def test_no_cycle_within_the_wait_keeps_the_issue_open(world: WriteWorld) -> None:
    (world.find("iss-00003") / "plan.md").write_text("# plan\n\nunsaved\n", encoding="utf-8")
    code, payload = world.write("work", "finish", "iss-00003")
    assert (code, payload["status"], payload["error"]["code"]) == (6, "partial", "CANONICAL_SAVE_UNCONFIRMED")
    assert [(item["kind"], item["status"]) for item in payload["effects"]][:2] == [
        ("catalog.changeset", "succeeded"),
        ("github.issue.close", "not_attempted"),
    ]
    assert "spec-dock canonical status" in payload["recovery"]["instructions"][0]
    assert world.fake().issue(3).state == "open"
    assert world.save_clock.offset >= 180  # type: ignore[attr-defined]
    world.save_clock.offset = 0  # type: ignore[attr-defined]
    for path in (world.catalog / ".runtime/changesets").glob("*.json"):
        path.unlink()
    git(world.catalog, "checkout", "--", ".")

    def older_cycle(current: CatalogSyncState | None) -> CatalogSyncState:
        assert current is not None and current.last_cycle is not None
        old = "2026-01-01T00:00:00Z"
        return current.evolve(last_cycle=replace(current.last_cycle, started_at=old, finished_at=old))

    update_catalog_state(resolve_state_root(), str(world.catalog.resolve()), older_cycle)
    code, payload = world.write("work", "finish", "iss-00003")
    assert (code, payload["status"], payload["error"]["code"]) == (3, "failed", "CANONICAL_SAVE_UNCONFIRMED")
    assert world.fake().issue(3).state == "open"


def test_a_hold_under_the_scope_stops_before_writing(world: WriteWorld, tmp_path: Path) -> None:
    def hold(current: CatalogSyncState | None) -> CatalogSyncState:
        assert current is not None
        return current.evolve(holds=(Hold("00000-00999/iss-00003/key.pem", "secret", "2026-10-29T00:00:00Z"),))

    update_catalog_state(resolve_state_root(), str(world.catalog.resolve()), hold)
    code, payload = world.write("work", "finish", "iss-00003")
    assert (code, payload["error"]["code"]) == (3, "CANONICAL_SAVE_HELD")
    assert "canonical accept" in " ".join(payload["recovery"]["instructions"])
    assert world.changesets() == [] and world.fake().issue(3).state == "open"


def test_a_child_reopened_while_waiting_stops_before_closing(world: WriteWorld) -> None:
    world.scope("issue", 4, "done child", parent=2, state="closed", state_reason="completed")
    world.select("epic-00002", 2)
    (world.find("epic-00002") / "plan.md").write_text("# plan\n\nepic change\n", encoding="utf-8")

    def reopen() -> None:
        world.edit(lambda fake: setattr(fake.issue(4), "state", "open"))
        world.edit(lambda fake: fake.touch(4))

    world.edit(lambda fake: setattr(fake.issue(3), "state", "closed"))
    world.edit(lambda fake: setattr(fake.issue(3), "state_reason", "completed"))
    _run_cycle_on_kick(world, reopen)
    code, payload = world.write("work", "finish", "epic-00002")
    assert (code, payload["status"]) == (6, "partial"), payload
    assert "DESCENDANT_NOT_COMPLETED" in payload["error"]["message"]
    assert world.fake().issue(2).state == "open"
    assert "spec-dock work finish epic-00002 --yes" in payload["recovery"]["instructions"][0]


def test_a_push_from_another_clone_taken_in_is_confirmed(world: WriteWorld, tmp_path: Path) -> None:
    other = clone(tmp_path / "remote.git", tmp_path / "other")
    code, payload = world.run("canonical", "link", checkout=other)
    assert code == 0, payload
    (other / "spec-dock/initiatives/00000-00999/iss-00003/report.md").write_text("# from other\n", encoding="utf-8")
    with catalog_changes((other / "spec-dock/.canonical").resolve(), command="test edit") as changes:
        changes.add("00000-00999/iss-00003/report.md")
    assert world.run("canonical", "sync", checkout=other)[0] == 0
    assert "from other" in _remote_file(world, "00000-00999/iss-00003/report.md")
    world.select("iss-00003", 3)
    _run_cycle_on_kick(world)
    code, payload = world.write("work", "finish", "iss-00003")
    assert code == 0, payload
    assert payload["effects"][0]["kind"] == "github.issue.close"
    assert (world.find("iss-00003") / "report.md").read_text(encoding="utf-8") == "# from other\n"
    assert world.fake().issue(3).state == "closed"


def test_a_kind_change_of_a_descendant_stops_finish(world: WriteWorld) -> None:
    world.select("epic-00002", 2)
    world.edit(lambda fake: setattr(fake.issue(3), "labels", ["spec-dock:epic"]))
    code, payload = world.write("work", "finish", "epic-00002")
    assert (code, payload["error"]["code"]) == (3, "SCOPE_KIND_CHANGED")
    assert world.writes() == [] and world.changesets() == []


def test_a_git_failure_after_the_changeset_is_partial_with_the_changeset(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.infra.git_process import GitProcessError

    world.select("iss-00003", 3)
    (world.find("iss-00003") / "plan.md").write_text("# plan\n\nunsaved\n", encoding="utf-8")
    original = canonical_work.run_catalog_git

    def failing(cwd, *args, **kwargs):
        if args[:1] == ("rev-parse",):
            raise GitProcessError(("git", *args), b"injected", 128)
        return original(cwd, *args, **kwargs)

    monkeypatch.setattr(canonical_work, "run_catalog_git", failing)
    _run_cycle_on_kick(world)
    code, payload = world.write("work", "finish", "iss-00003")
    assert (code, payload["status"]) == (6, "partial"), payload
    assert payload["effects"][0] == {
        "kind": "catalog.changeset",
        "status": "succeeded",
        "target": payload["effects"][0]["target"],
    }
    assert world.fake().issue(3).state == "open"


def test_a_selection_failure_after_closing_keeps_the_close_in_a_partial_result(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.infra.work_target_store import SelectionRemovalUnknown, WorkTargetStore

    world.select("iss-00003", 3)

    def unknown(self, handle):
        raise SelectionRemovalUnknown(handle.token, OSError("lost"))

    monkeypatch.setattr(WorkTargetStore, "remove_observed", unknown)
    _run_cycle_on_kick(world)
    code, payload = world.write("work", "finish", "iss-00003")
    assert (code, payload["status"]) == (6, "partial"), payload
    kinds = [(item["kind"], item["status"]) for item in payload["effects"]]
    assert ("github.issue.close", "succeeded") in kinds and ("selection.clear", "unknown") in kinds
    assert world.fake().issue(3).state == "closed"


def test_after_finish_the_snapshot_shows_the_scope_closed_without_a_refetch(world: WriteWorld) -> None:
    world.select("iss-00003", 3)
    _run_cycle_on_kick(world)
    code, payload = world.write("work", "finish", "iss-00003")
    assert code == 0, payload
    graphql = len(world.fake().graphql_requests())
    code, shown = world.run("scope", "show", "iss-00003")
    assert code == 0 and shown["data"]["result"]["scope"]["status"]["state"] == "completed", shown
    assert len(world.fake().graphql_requests()) == graphql
