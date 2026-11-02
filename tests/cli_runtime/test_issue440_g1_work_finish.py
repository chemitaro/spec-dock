"""`work finish` confirms completion before clearing its captured direct record, in canonical mode.

Replaces the common-contract tests of tests/cli_runtime/test_issue413_finish.py, the work lifecycle tests of
tests/cli_runtime/test_vnext_runtime_work.py and tests/cli_runtime/test_work_commands_vnext.py (iss-00440).
Canonical finish first waits until the Scope's catalog places reached GitHub (a sync cycle runs on the scheduler
kick), closes the Issue through the fake GitHub and then removes the in-progress mark; the REST GET/PATCH counts
of the legacy gateway become checks on the fake GitHub's state and writes.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
import shutil
import sys
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.application import canonical_scopes, canonical_work, canonical_writes
from spec_dock.runtime.application.canonical_catalog import catalog_changes
from spec_dock.runtime.infra import github_structure
from spec_dock.runtime.infra.github_structure import GithubRepository
from spec_dock.runtime.infra.start_lock import StartLock
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.canonical_repo import git
from tests.support.canonical_scopes import REPOSITORY
from tests.support.legacy_contracts_g1 import chain_world, commit, records, run_err, select_record, token

if TYPE_CHECKING:
    from pathlib import Path

    from tests.support.canonical_sync import FakeScheduler
    from tests.support.canonical_writes import WriteWorld


ROLES = ("initiative", "epic", "issue")


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
    """init-1 / epic-2 / iss-3 (iss-3 in progress), saved and pushed; a sync cycle runs on each scheduler kick."""
    world: WriteWorld = chain_world(tmp_path, monkeypatch, capsys, write=True)  # type: ignore[assignment]
    # The catalog pushes to the temporary bare remote; only the structure stays on the fake GitHub repository.
    git(world.main, "remote", "set-url", "origin", str(tmp_path / "remote.git"))
    repository = GithubRepository.parse(REPOSITORY)
    for module in (github_structure, canonical_writes, canonical_scopes):
        monkeypatch.setattr(module, "repository_for_checkout", lambda root, *, timeout: repository)
    monkeypatch.setattr(canonical_work, "SAVE_CLOCK", _Clock())
    world.edit(lambda fake: fake.issue(3).labels.append("spec-dock:in-progress"))
    with catalog_changes(world.catalog.resolve(), command="test setup") as changes:
        for kind, number in (("initiative", 1), ("epic", 2), ("issue", 3)):
            changes.add(world.relative(kind, number).as_posix())
    assert world.run("canonical", "sync")[0] == 0
    for scheduler in periodic_jobs.values():
        scheduler.simulate_run = False
    world.jobs = periodic_jobs  # type: ignore[attr-defined]
    _on_kick(world)
    return world


def _on_kick(world: WriteWorld, also: object = None) -> None:
    def kick() -> None:
        code, payload = world.run("canonical", "sync")
        assert code == 0, payload
        if callable(also):
            also()

    for scheduler in world.jobs.values():  # type: ignore[attr-defined]
        scheduler.on_kick = kick


def _close(world: WriteWorld, *numbers: int, reason: str | None = "completed") -> None:
    def change(fake: object) -> None:
        for number in numbers:
            issue = fake.issue(number)  # type: ignore[attr-defined]
            issue.state, issue.state_reason = "closed", reason
            fake.touch(number)  # type: ignore[attr-defined]

    world.edit(change)


def _close_writes(world: WriteWorld) -> list[str]:
    return [endpoint for method, endpoint, payload in world.writes() if method == "PATCH" and "state" in str(payload)]


def _states(world: WriteWorld) -> dict[int, str]:
    fake = world.fake()
    return {number: fake.issue(number).state for number in (1, 2, 3)}


def test_explicit_finish_rejects_corrupt_selection_before_remote_observation(world: WriteWorld) -> None:
    record = select_record(world, "iss-00003", 3)
    record.write_bytes(b"{broken selection\n")
    before = record.read_bytes(), (world.main / ".git/HEAD").read_bytes()
    code, result = world.write("work", "finish", "iss-00003")
    assert code == 3, result
    assert result["error"]["code"] == "PRECONDITION_FAILED"
    assert result["effects"] == [] and world.writes() == [] and world.changesets() == []
    assert (record.read_bytes(), (world.main / ".git/HEAD").read_bytes()) == before


@pytest.mark.parametrize("dry_run", [False, True])
def test_explicit_finish_rejects_redirected_selection_before_remote_observation(
    world: WriteWorld, tmp_path: Path, dry_run: bool
) -> None:
    record = select_record(world, "iss-00003", 3)
    saved = tmp_path / "saved-selections"
    record.parent.rename(saved)
    outside = tmp_path / "outside"
    outside.mkdir()
    sentinel = outside / "keep.txt"
    sentinel.write_bytes(b"foreign content\n")
    record.parent.symlink_to(outside, target_is_directory=True)
    before = (saved / record.name).read_bytes(), (world.main / ".git/HEAD").read_bytes()
    code, result = world.run("work", "finish", "iss-00003", "--dry-run" if dry_run else "--yes")
    assert code == 3, result
    assert result["error"]["code"] == "PRECONDITION_FAILED"
    assert "unavailable" in result["error"]["message"]
    assert result["effects"] == [] and world.writes() == []
    assert ((saved / record.name).read_bytes(), (world.main / ".git/HEAD").read_bytes()) == before
    assert list(outside.iterdir()) == [sentinel] and sentinel.read_bytes() == b"foreign content\n"
    assert record.parent.is_symlink()


def test_explicit_finish_keeps_valid_empty_selection_and_closes_fixed_target(world: WriteWorld) -> None:
    head_before = (world.main / ".git/HEAD").read_bytes()
    code, result = world.write("work", "finish", "iss-00003")
    assert code == 0, result
    assert result["data"]["completed"] is True and result["data"]["selection_token"] is None
    # Canonical finish also removes the in-progress label; there is still no selection effect.
    assert [(item["kind"], item["status"]) for item in result["effects"]] == [
        ("github.issue.close", "succeeded"),
        ("github.issue.label", "succeeded"),
    ]
    assert result["effects"][0]["target"] == "gh:example/repo#3"
    assert len(_close_writes(world)) == 1
    assert (world.main / ".git/HEAD").read_bytes() == head_before
    assert not (world.main / "spec-dock/.agent/work-target").exists()


def test_finish_native_git_failure_retains_original_diagnostic_and_confirmed_effects(
    world: WriteWorld, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Only the failure before closing is checked here: canonical finish runs no Git command between the close and
    # the release; the partial result after a write is tests/cli_runtime/test_issue432_work_finish.py's
    # test_a_git_failure_after_the_changeset_is_partial_with_the_changeset.
    record = select_record(world, "iss-00003", 3)
    before = record.read_bytes()
    real_git = shutil.which("git")
    assert real_git is not None
    wrapper = tmp_path / "git-bin"
    wrapper.mkdir()
    original_error = "fatal: fixture Git observation refused\nsecond original line\n"
    executable = wrapper / "git"
    executable.write_text(
        f"#!{sys.executable}\nimport os,sys\n"
        "if '--untracked-files=all' in sys.argv:\n"
        f" sys.stderr.write({original_error!r}); sys.exit(73)\n"
        f"os.execv({real_git!r},['git',*sys.argv[1:]])\n"
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(wrapper) + os.pathsep + os.environ["PATH"])
    code, result, err = run_err(world, "work", "finish", "@current", "--yes")
    assert code == 5, result
    assert result["error"]["code"] == "GIT_FAILED"
    assert result["error"]["details"]["git"]["stderr"] == original_error
    assert result["error"]["details"]["git"]["returncode"] == 73
    assert result["status"] == "failed" and result["effects"] == [] and err == ""
    assert _close_writes(world) == [] and world.fake().issue(3).state == "open"
    assert record.read_bytes() == before


def test_finish_dry_run_needs_no_approval_and_preserves_remote_and_selection(world: WriteWorld) -> None:
    record = select_record(world, "iss-00003", 3)
    before = record.read_bytes()
    code, result = world.run("work", "finish", "@current", "--dry-run")
    assert code == 0, result
    assert result["status"] == "planned"
    assert result["data"]["completed"] is False
    assert record.read_bytes() == before
    assert world.writes() == [] and world.changesets() == []
    assert result["effects"] == [
        {"kind": "github.issue.close", "status": "planned", "target": "gh:example/repo#3"},
        {"kind": "selection.clear", "status": "planned", "target": token(record)},
    ]


def test_finish_completed_parent_still_requires_all_descendants_completed(world: WriteWorld) -> None:
    _close(world, 2)
    record = select_record(world, "epic-00002", 2)
    before = record.read_bytes()
    code, result = world.write("work", "finish", "@current")
    assert code == 3, result
    assert result["effects"] == []
    assert "DESCENDANT_NOT_COMPLETED" in result["error"]["message"]
    assert record.read_bytes() == before
    assert world.writes() == [] and world.changesets() == []


def test_finish_explicit_child_preserves_directly_selected_ancestor(world: WriteWorld) -> None:
    record = select_record(world, "init-00001", 1)
    exact_record = record.read_bytes()
    code, result, err = run_err(world, "work", "finish", "iss-00003", "--yes")
    assert code == 0, result
    assert result["data"]["scope_id"] == "iss-00003" and result["data"]["completed"] is True
    assert result["data"]["branch_after"] == "main" and not err
    assert [effect["kind"] for effect in result["effects"]] == ["github.issue.close", "github.issue.label"]
    assert result["effects"][0] == {"kind": "github.issue.close", "status": "succeeded", "target": "gh:example/repo#3"}
    assert record.read_bytes() == exact_record and records(world.main) == [record]
    assert _states(world) == {1: "open", 2: "open", 3: "closed"}


def test_finish_parent_releases_captured_descendant_without_selecting_parent(world: WriteWorld) -> None:
    _close(world, 3)
    record = select_record(world, "iss-00003", 3)
    code, result = world.write("work", "finish", "@epic")
    assert code == 0, result
    assert result["data"]["scope_id"] == "epic-00002"
    assert result["data"]["selection_token"] is None
    assert not record.exists()
    assert world.run("active", "show")[1]["data"]["selection"]["status"] == "empty"
    assert _close_writes(world) == ["repos/example/repo/issues/2"]


def test_finish_offline_refuses_before_any_remote_call_or_local_change(world: WriteWorld) -> None:
    record = select_record(world, "iss-00003", 3)
    before = record.read_bytes()
    requests = len(world.fake().requests)
    code, result = world.run("work", "finish", "@current", "--yes", "--offline")
    assert code == 3, result
    assert result["effects"] == []
    assert len(world.fake().requests) == requests
    assert record.read_bytes() == before


def test_finish_expected_direct_target_guard_precedes_remote_observation(world: WriteWorld) -> None:
    record = select_record(world, "iss-00003", 3)
    before = record.read_bytes()
    code, result = world.write("work", "finish", "iss-00003", "--expect-current", "epic-00002")
    assert code == 3, result
    assert result["effects"] == []
    assert world.writes() == [] and world.changesets() == []
    assert record.read_bytes() == before


def test_finish_unknown_target_state_never_patches_or_releases_selection(world: WriteWorld) -> None:
    _close(world, 3, reason=None)  # closed without a reason: neither completed nor not planned
    record = select_record(world, "iss-00003", 3)
    before = record.read_bytes()
    code, result = world.write("work", "finish", "@current")
    assert code == 3, result
    assert "SCOPE_STATUS_UNKNOWN" in result["error"]["message"]
    assert result["effects"] == []
    assert record.read_bytes() == before
    assert world.writes() == []


def test_finish_concurrent_remote_completion_is_reported_unchanged_without_patch(world: WriteWorld) -> None:
    record = select_record(world, "iss-00003", 3)
    _on_kick(world, lambda: _close(world, 3))  # another PC closes it while finish waits for the save
    code, result = world.write("work", "finish", "@current")
    assert code == 0, result
    assert result["effects"][0] == {"kind": "github.issue.close", "status": "unchanged", "target": "gh:example/repo#3"}
    assert not record.exists()
    assert _close_writes(world) == []


def test_finish_uncertain_close_retains_capture_and_reports_unknown_effect(world: WriteWorld) -> None:
    record = select_record(world, "iss-00003", 3)
    before = record.read_bytes()
    world.edit(lambda fake: fake.inject(status=503, body={"message": "x"}, method="PATCH", endpoint="/issues/3"))
    code, result = world.write("work", "finish", "@current")
    assert code == 6, result
    assert result["status"] == "partial"
    assert result["data"]["completed"] is False
    # Canonical finish reports no selection token on a stopped close; the legacy result echoed the captured one.
    assert result["data"]["selection_token"] is None
    assert result["effects"] == [
        {"kind": "github.issue.close", "status": "unknown", "target": "gh:example/repo#3"},
        {"kind": "selection.clear", "status": "not_attempted", "target": token(record)},
    ]
    assert record.read_bytes() == before


def test_finish_confirmed_patch_rejection_reports_clear_not_attempted(world: WriteWorld) -> None:
    record = select_record(world, "iss-00003", 3)
    before = record.read_bytes()
    world.edit(lambda fake: fake.inject(status=422, body={"message": "no"}, method="PATCH", endpoint="/issues/3"))
    code, result = world.write("work", "finish", "@current")
    assert code == 5, result
    assert result["status"] == "failed"
    assert result["data"]["completed"] is False
    assert result["effects"] == [
        {"kind": "github.issue.close", "status": "failed", "target": "gh:example/repo#3"},
        {"kind": "selection.clear", "status": "not_attempted", "target": token(record)},
    ]
    assert record.read_bytes() == before
    assert world.fake().issue(3).state == "open"


def test_finish_keeps_new_selection_published_during_remote_wait(world: WriteWorld) -> None:
    old = select_record(world, "iss-00003", 3)
    replaced: list[object] = []

    def reselect() -> None:
        old.unlink()
        replaced.append(select_record(world, "iss-00003", 3))

    _on_kick(world, reselect)
    code, result = world.write("work", "finish", "iss-00003")
    assert code == 0, result
    new = replaced[-1]
    assert not old.exists() and new.exists()  # type: ignore[attr-defined]
    assert token(new) != token(old)  # type: ignore[arg-type]
    assert result["effects"][-1] == {"kind": "selection.clear", "status": "unchanged", "target": token(old)}
    # Canonical finish returns selection_token null after its clear step; the legacy result named the new token.
    assert result["data"]["selection_token"] is None
    assert len(_close_writes(world)) == 1


@pytest.mark.skipif(os.name != "posix", reason="native POSIX flock boundary")
def test_finish_native_process_does_not_participate_in_start_lock(world: WriteWorld) -> None:
    record = select_record(world, "iss-00003", 3)
    # The lock is held on another open file description, so a finish that waited for it would stop busy.
    with StartLock(world.main / ".git", timeout=0):
        code, result = world.write("work", "finish", "@current")
    assert code == 0, result
    assert result["data"]["completed"] is True
    assert not record.exists()


def test_finish_retry_observes_completion_and_avoids_duplicate_patch(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    record = select_record(world, "iss-00003", 3)
    real_unlink = os.unlink

    def unlinking(path, *args, **kwargs):
        if path == record.name:
            raise PermissionError("fixture clear refused")
        return real_unlink(path, *args, **kwargs)

    with monkeypatch.context() as clearing:
        clearing.setattr(os, "unlink", unlinking)
        code, result = world.write("work", "finish", "@current")
        assert code == 6, result
        assert result["data"]["completed"] is True
        assert record.exists()
        assert result["effects"][-1] == {"kind": "selection.clear", "status": "failed", "target": token(record)}
    code, result = world.write("work", "finish", "@current")
    assert code == 0, result
    assert result["effects"][0]["status"] == "unchanged"
    assert not record.exists()
    assert len(_close_writes(world)) == 1


def test_finish_unavailable_observation_reports_gateway_failure_without_effects(world: WriteWorld) -> None:
    record = select_record(world, "iss-00003", 3)
    before = record.read_bytes()
    world.edit(lambda fake: fake.inject(status=503, body={"message": "unavailable"}, times=50))
    code, result = world.write("work", "finish", "@current")
    assert (code, result["error"]["code"]) == (5, "GITHUB_UNAVAILABLE"), result
    assert result["status"] == "failed"
    assert result["effects"] == []
    assert record.read_bytes() == before
    assert world.fake().issue(3).state == "open"


def test_finish_resolves_dynamic_target_and_handle_from_one_observation(world: WriteWorld) -> None:
    _close(world, 3)
    old = select_record(world, "iss-00003", 3)
    replaced: list[object] = []

    def reselect() -> None:
        old.unlink()
        replaced.append(select_record(world, "iss-00003", 3))

    _on_kick(world, reselect)
    code, result = world.write("work", "finish", "@current")
    assert code == 0, result
    new = replaced[-1]
    assert new.exists()  # type: ignore[attr-defined]
    assert result["data"]["scope_id"] == "iss-00003"
    # Canonical finish returns selection_token null after its clear step; the replacement record is kept.
    assert result["data"]["selection_token"] is None
    assert result["effects"][-1] == {"kind": "selection.clear", "status": "unchanged", "target": token(old)}


def test_public_work_lifecycle_resolves_current_selector_and_returns_v2_json(world: WriteWorld) -> None:
    code, started, err = run_err(world, "work", "start", "iss-00003", "--base", "HEAD")
    assert code == 0, started
    assert not err and started["schema_version"] == "specdock.cli/v2" and started["command"] == "work start"
    selection = started["data"]["selection_token"]
    code, finished, err = run_err(world, "work", "finish", "@current", "--expect-current", "iss-00003", "--yes")
    assert code == 0, finished
    assert not err and finished["schema_version"] == "specdock.cli/v2" and finished["command"] == "work finish"
    assert finished["data"]["scope_id"] == "iss-00003" and finished["data"]["completed"] is True
    assert finished["data"]["selection_token"] is None
    assert not (world.main / "spec-dock/.agent/work-target" / f"target-{selection}.json").exists()


def test_public_active_show_same_set_and_ancestor_clear_do_not_promote_a_parent(world: WriteWorld) -> None:
    code, rejected = world.run("active", "set", "iss-00003", "--dry-run")
    assert code == 3, rejected
    assert rejected["error"]["code"] == "WORK_START_REQUIRED" and rejected["effects"] == []
    assert not (world.main / "spec-dock/.agent").exists()
    code, started = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert code == 0, started
    record = world.main / "spec-dock/.agent/work-target" / f"target-{started['data']['selection_token']}.json"
    before = record.read_bytes()
    writes = world.writes()
    for operation in (["show"], ["set", "@current"]):
        code, result = world.run("active", *operation)
        assert code == 0, result
        # Canonical set reports the already aligned links as unchanged active.link effects.
        assert result["data"]["selection"]["scope_id"] == "iss-00003"
        assert {effect["status"] for effect in result["effects"]} <= {"unchanged"}
        assert record.read_bytes() == before
    code, result = world.run("active", "clear", "--from", "epic-00002", "--dry-run")
    assert (code, result["status"]) == (0, "planned") and record.read_bytes() == before
    code, cleared = world.run("active", "clear", "--from", "epic-00002")
    assert code == 0, cleared
    assert cleared["data"]["selection"]["status"] == "empty" and not record.exists()
    code, result = world.run("active", "clear", "--all")
    assert code == 0, result
    assert result["status"] == "unchanged"
    assert world.writes() == writes
    assert git(world.main, "branch", "--show-current") == "iss-00003"
    assert _states(world) == {1: "open", 2: "open", 3: "open"}
    assert not (world.main / ".git/spec-dock").exists()


@pytest.mark.parametrize("target,number", [("init-00001", 1), ("epic-00002", 2), ("iss-00003", 3)])
def test_work_commands_start_and_finish_all_three_kinds(world: WriteWorld, target: str, number: int) -> None:
    _close(world, *range(number + 1, 4))  # the descendants are already completed
    code, started = world.run("work", "start", target, "--base", "HEAD")
    assert code == 0, started
    assert started["status"] == "succeeded" and started["data"]["scope_id"] == target
    branch = started["data"]["branch_after"]
    record = world.main / "spec-dock/.agent/work-target" / f"target-{started['data']['selection_token']}.json"
    assert records(world.main) == [record]
    before = record.read_bytes()
    code, preview = world.run("work", "start", target, "--branch", branch, "--dry-run")
    assert code == 0, preview
    assert preview["status"] == "planned" and preview["data"]["branch_after"] == branch
    assert record.read_bytes() == before
    code, finished = world.write("work", "finish", target)
    assert code == 0, finished
    assert finished["data"]["completed"] is True and finished["data"]["scope_id"] == target
    assert finished["data"]["branch_after"] == branch and finished["data"]["selection_token"] is None
    assert not record.exists()
    assert git(world.main, "branch", "--show-current") == branch
    assert _close_writes(world) == [f"repos/example/repo/issues/{number}"]
    assert _states(world) == {1: "open" if number > 1 else "closed", 2: "open" if number > 2 else "closed", 3: "closed"}
    assert not (world.main / ".git/spec-dock").exists()
    assert git(world.main, "status", "--porcelain") == ""


def test_work_adapter_plans_start_and_finish_without_writes(world: WriteWorld) -> None:
    digest = tree_digest(world.main)
    branches = git(world.main, "show-ref")
    code, start = world.run("work", "start", "iss-00003", "--base", "HEAD", "--dry-run")
    assert code == 0, start
    assert start["status"] == "planned" and start["data"]["scope_id"] == "iss-00003"
    assert start["data"]["selection_token"] is None
    assert all(effect["status"] in ("planned", "unchanged") for effect in start["effects"])
    code, finish = world.run("work", "finish", "iss-00003", "--dry-run")
    assert code == 0, finish
    assert finish["status"] == "planned" and finish["data"]["completed"] is False
    assert finish["effects"] == [{"kind": "github.issue.close", "status": "planned", "target": "gh:example/repo#3"}]
    code, refused = world.run("work", "finish", "iss-00003")
    assert code == 3, refused
    assert "requires --yes" in refused["error"]["message"]
    assert world.writes() == [] and world.changesets() == []
    assert _states(world) == {1: "open", 2: "open", 3: "open"}
    assert git(world.main, "show-ref") == branches
    assert git(world.main, "status", "--porcelain") == ""
    assert tree_digest(world.main) == digest
    assert not (world.main / "spec-dock/.agent").exists() and not (world.main / ".git/spec-dock").exists()


def _fallback_links(world: WriteWorld) -> dict[str, str]:
    active = world.main / "spec-dock/active"
    return {role: str((active / role).readlink()) for role in ROLES if (active / role).is_symlink()}


def _started_with_fallback(world: WriteWorld) -> None:
    for role in ROLES:
        fallback = world.main / "spec-dock/system/active-none" / role
        fallback.mkdir(parents=True)
        (fallback / "README.md").write_text(f"# no {role}\n", encoding="utf-8")
    commit(world.main, "fallback", "spec-dock/system")
    code, result = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert code == 0, result


def test_work_finish_that_clears_the_selection_restores_the_fallback(world: WriteWorld) -> None:
    # Moved from tests/cli_runtime/test_issue416_active_links.py.
    _started_with_fallback(world)
    code, preview = world.run("work", "finish", "iss-00003", "--dry-run")
    assert code == 0 and preview["status"] == "planned", preview
    # Canonical finish plans only the close and the selection clear; the links follow a real clear.
    assert [effect["kind"] for effect in preview["effects"]] == ["github.issue.close", "selection.clear"]
    assert _fallback_links(world)["issue"] == "../initiatives/00000-00999/iss-00003"
    code, result = world.write("work", "finish", "iss-00003")
    assert code == 0 and result["status"] == "succeeded", result
    assert _fallback_links(world) == {role: f"../system/active-none/{role}" for role in ROLES}
    assert [
        (effect["target"], effect["status"]) for effect in result["effects"] if effect["kind"] == "active.link"
    ] == [(role, "succeeded") for role in ROLES]
    assert git(world.main, "status", "--porcelain") == ""


def test_link_target_errors_never_turn_a_completed_finish_into_a_failure(world: WriteWorld) -> None:
    # Moved from tests/cli_runtime/test_issue416_active_links.py.
    _started_with_fallback(world)
    fallback = world.main / "spec-dock/system/active-none"
    fallback.chmod(0)
    try:
        code, result = world.write("work", "finish", "iss-00003")
    finally:
        fallback.chmod(0o755)
    assert code == 0 and result["status"] == "succeeded", result
    assert result["data"]["completed"] is True
    assert ("selection.clear", "succeeded") in [(effect["kind"], effect["status"]) for effect in result["effects"]]
    assert {item["code"] for item in result["warnings"]} >= {"ACTIVE_LINK_NOT_UPDATED"}
    assert {item["code"] for item in result["warnings"]} <= {"ACTIVE_LINK_NOT_UPDATED", "SCOPE_IN_PROGRESS"}
