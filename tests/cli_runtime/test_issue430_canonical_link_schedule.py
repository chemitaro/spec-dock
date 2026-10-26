"""`canonical link` steps 6 and 7 (iss-00430): registry, baseline, the periodic job, its first run and warnings."""

from __future__ import annotations

from dataclasses import replace
import os
import shutil
from typing import TYPE_CHECKING, Any, cast

import pytest

from spec_dock.runtime.domain.canonical_sync_state import RegistryEntry, SyncError
from spec_dock.runtime.infra import runtime_environment
from spec_dock.runtime.infra.canonical_registry import read_registry, update_registry
from spec_dock.runtime.infra.canonical_state import update_catalog_state
from tests.support.canonical_repo import environment, git
from tests.support.canonical_sync import FakeScheduler, SyncPair, catalog_result

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def pair(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> SyncPair:
    return SyncPair.create(tmp_path, monkeypatch, capsys, link=False)


def _effects(result: dict[str, Any]) -> dict[str, str]:
    return {item["kind"]: item["status"] for item in result["effects"]}


def _codes(result: dict[str, Any]) -> list[str]:
    return [item["code"] for item in result["warnings"]]


def _catalog(pair: SyncPair) -> str:
    return os.path.realpath(pair.catalog(pair.a))


def test_link_registers_the_catalog_installs_the_job_and_runs_it_once(pair: SyncPair) -> None:
    code, result = pair.run(pair.a, "canonical", "link")
    assert code == 0 and result["status"] == "succeeded", result
    effects = _effects(result)
    assert (effects["canonical.registry"], effects["canonical.baseline"], effects["canonical.scheduler"]) == (
        "succeeded",
        "succeeded",
        "succeeded",
    )
    registry = read_registry(pair.state_root)
    assert registry.scheduler == "launchd"
    (entry,) = registry.catalogs
    assert entry.catalog == _catalog(pair) and entry.main_checkout == str(pair.a) and entry.git == shutil.which("git")
    launchd = pair.schedulers["launchd"]
    assert launchd.calls == [("ensure", "launchd"), ("kick", "launchd")]
    (spec,) = launchd.specs
    assert spec.state_root == pair.state_root and spec.arguments()[-2:] == ("--state-root", str(pair.state_root))
    state = pair.state(pair.a)
    assert state is not None and state.last_seen_remote == pair.remote_head() and state.schedule is None
    assert "CANONICAL_SYNC_NOT_CONFIRMED" in _codes(result)  # the fake job did not run within the wait
    code, again = pair.run(pair.a, "canonical", "link")
    assert code == 0 and again["status"] == "unchanged", again
    assert launchd.calls == [("ensure", "launchd"), ("kick", "launchd")]  # the second link writes nothing


def test_the_recorded_state_root_works_without_xdg_state_home(pair: SyncPair, monkeypatch: pytest.MonkeyPatch) -> None:
    pair.run(pair.a, "canonical", "link")
    (spec,) = pair.schedulers["launchd"].specs
    pair.write(pair.a, "x.md", "x\n")
    pair.advance(31)
    monkeypatch.delenv("XDG_STATE_HOME")
    code, result = pair.run(pair.a, "canonical", "sync", "--registered", "--state-root", str(spec.state_root))
    assert code == 0 and catalog_result(result)["pushed"] is True, result
    assert pair.remote_file("x.md") == "x"
    assert not (pair.tmp_path / "home/.local/state/spec-dock/canonical-registry.json").exists()


def test_a_first_run_that_reports_problems_returns_them_as_warnings(pair: SyncPair) -> None:
    def job_ran() -> None:
        def mutate(current: Any) -> Any:
            error = SyncError("OS_ACCESS_DENIED", "Operation not permitted", "allow", ("/py", "/git"), None)
            from spec_dock.runtime.domain.canonical_sync_state import LastCycle, PushAuth

            stamp = "2999-01-01T00:00:00Z"
            return current.evolve(
                last_cycle=LastCycle(stamp, stamp, "error"),
                last_error=error,
                push_auth=PushAuth("failed", stamp, "Authentication failed"),
            )

        update_catalog_state(pair.state_root, _catalog(pair), mutate)

    from tests.support.canonical_sync import FakeScheduler

    pair.schedulers["launchd"] = FakeScheduler("launchd", on_kick=job_ran)
    code, result = pair.run(pair.a, "canonical", "link")
    assert code == 0
    codes = _codes(result)
    assert "OS_ACCESS_DENIED" in codes and "CANONICAL_PUSH_AUTH_FAILED" in codes
    assert "CANONICAL_SYNC_NOT_CONFIRMED" not in codes
    denied = next(item for item in result["warnings"] if item["code"] == "OS_ACCESS_DENIED")
    assert denied["details"]["programs"] == ["/py", "/git"] and "Privacy & Security" in denied["details"]["next_step"]


def test_no_schedule_records_only_the_baseline_and_survives_worktree_create(
    pair: SyncPair, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    code, result = pair.run(pair.a, "canonical", "link", "--no-schedule")
    assert code == 0 and "canonical.registry" not in _effects(result)
    assert pair.schedulers == {} and not (pair.state_root / "canonical-registry.json").exists()
    state = pair.state(pair.a)
    assert state is not None and state.schedule == "none" and state.last_seen_remote == pair.remote_head()
    code, result = pair.run(
        pair.a, "worktree", "create", "feature", "--base", "HEAD", "--root", str(tmp_path / "wt"), "--yes"
    )
    assert code == 0, result
    assert pair.schedulers == {} and not (pair.state_root / "canonical-registry.json").exists()
    code, result = pair.run(pair.a, "canonical", "status")
    sync = result["data"]["sync"]
    assert sync["registered"] is False and sync["next_step"].startswith("Run spec-dock canonical link")
    code, result = pair.run(pair.a, "canonical", "link")
    assert code == 0 and _effects(result)["canonical.registry"] == "succeeded"
    state = pair.state(pair.a)
    assert state is not None and state.schedule is None


def test_a_refused_job_registration_is_partial_and_keeps_the_baseline(pair: SyncPair) -> None:
    from tests.support.canonical_sync import FakeScheduler

    pair.schedulers["launchd"] = FakeScheduler("launchd", fail_ensure=True)
    code, result = pair.run(pair.a, "canonical", "link")
    assert code == 6 and result["status"] == "partial", result
    assert result["error"]["code"] == "CANONICAL_SCHEDULER_FAILED"
    assert result["recovery"]["instructions"] == ["Check the reported output, then run spec-dock canonical link again."]
    effects = _effects(result)
    assert effects["canonical.scheduler"] == "unknown" and effects["canonical.baseline"] == "succeeded"
    assert pair.state(pair.a) is not None


@pytest.mark.parametrize(
    ("facts", "kind", "warning"),
    [
        (
            {"systemd_present": True, "systemd_user": True, "linger": False, "user": "dev"},
            "systemd",
            "CANONICAL_LINGER_DISABLED",
        ),
        ({"systemd_present": False, "systemd_user": False}, "loop", "CANONICAL_RUNNER_RESTART"),
    ],
)
def test_linux_chooses_systemd_or_the_loop_and_says_what_the_user_must_add(
    pair: SyncPair, monkeypatch: pytest.MonkeyPatch, facts: dict[str, object], kind: str, warning: str
) -> None:
    linux = replace(environment(), system="linux", **cast("dict[str, Any]", facts))
    monkeypatch.setattr(runtime_environment, "detect_runtime_environment", lambda *a, **k: linux)
    code, result = pair.run(pair.a, "canonical", "link")
    assert code == 0 and read_registry(pair.state_root).scheduler == kind
    found = next(item for item in result["warnings"] if item["code"] == warning)
    if kind == "loop":
        assert found["details"]["line"] == (
            f"spec-dock canonical sync --registered --loop --detach --state-root {pair.state_root}"
        )
    else:
        assert found["details"]["next_step"].startswith("Run loginctl enable-linger dev")


def test_choosing_again_removes_the_previous_job_and_keeps_a_working_recorded_git(
    pair: SyncPair, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake_git = tmp_path / "tools/git"
    fake_git.parent.mkdir()
    fake_git.symlink_to(shutil.which("git") or "/usr/bin/git")
    entry = RegistryEntry(_catalog(pair), str(pair.a), None, str(fake_git), "2026-10-26T00:00:00Z")
    update_registry(pair.state_root, lambda registry: replace(registry.with_entry(entry), scheduler="systemd"))
    linux = replace(environment(), system="linux", systemd_present=False, systemd_user=False)
    monkeypatch.setattr(runtime_environment, "detect_runtime_environment", lambda *a, **k: linux)
    code, result = pair.run(pair.a, "canonical", "link")
    assert code == 0, result
    assert ("remove", "systemd") in pair.schedulers["systemd"].calls
    registry = read_registry(pair.state_root)
    assert registry.scheduler == "loop" and registry.catalogs[0].git == str(fake_git)


def test_unwritable_state_root_stops_before_anything_is_written(pair: SyncPair) -> None:
    pair.state_root.parent.mkdir(parents=True)
    pair.state_root.parent.chmod(0o555)
    try:
        code, result = pair.run(pair.a, "canonical", "link")
    finally:
        pair.state_root.parent.chmod(0o755)
    assert code == 3 and result["error"]["code"] == "CANONICAL_SANDBOX_DENIED", result
    assert not pair.catalog(pair.a).exists()
    assert all(scheduler.calls == [] for scheduler in pair.schedulers.values())


def test_a_moved_main_checkout_moves_its_registry_entry_and_baseline(pair: SyncPair, tmp_path: Path) -> None:
    pair.run(pair.a, "canonical", "link")
    old = _catalog(pair)
    before = pair.state(pair.a)
    assert before is not None
    moved = tmp_path / "moved"
    shutil.move(str(pair.a), moved)
    code, result = pair.run(moved, "canonical", "link")
    assert code == 0, result
    registry = read_registry(pair.state_root)
    new = os.path.realpath(moved / "spec-dock/.canonical")
    assert [item.catalog for item in registry.catalogs] == [new] and old != new
    from spec_dock.runtime.infra.canonical_state import read_catalog_state

    after = read_catalog_state(pair.state_root, new)
    assert after is not None and after.last_seen_remote == before.last_seen_remote
    assert read_catalog_state(pair.state_root, old) is None


def test_a_clone_whose_github_canonical_vanished_guards_its_content(pair: SyncPair) -> None:
    pair.run(pair.a, "canonical", "link", "--no-schedule")
    pair.write(pair.a, "keep.md", "k\n")
    pair.advance(31)
    pair.sync(pair.a)
    git(pair.remote, "update-ref", "-d", "refs/heads/spec-dock/canonical")
    from spec_dock.runtime.infra.canonical_state import catalog_state_dir

    shutil.rmtree(catalog_state_dir(pair.state_root, _catalog(pair)))  # no baseline (state root lost)
    git(pair.catalog(pair.a), "update-ref", "-d", "refs/remotes/origin/spec-dock/canonical")
    code, result = pair.run(pair.a, "canonical", "link", "--no-schedule")
    assert code == 0, result
    state = pair.state(pair.a)
    assert state is not None and state.last_seen_remote == git(pair.catalog(pair.a), "rev-parse", "HEAD")
    code, result = pair.sync(pair.a)
    assert catalog_result(result)["paused"] == "remote_deleted"
    assert git(pair.remote, "rev-parse", "--verify", "--quiet", "refs/heads/spec-dock/canonical", check=False) == ""


def test_a_second_link_writes_nothing_even_with_a_read_only_state_root(pair: SyncPair) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    assert pair.run(pair.a, "canonical", "link")[0] == 0
    before = tree_digest(pair.state_root)
    for directory in [pair.state_root, *pair.state_root.rglob("*")]:
        if directory.is_dir():
            directory.chmod(0o555)
    try:
        code, result = pair.run(pair.a, "canonical", "link")
    finally:
        for directory in [pair.state_root, *pair.state_root.rglob("*")]:
            if directory.is_dir():
                directory.chmod(0o755)
    assert code == 0 and result["status"] == "unchanged", result
    assert tree_digest(pair.state_root) == before


def test_a_working_recorded_job_executable_is_kept(pair: SyncPair, tmp_path: Path) -> None:
    from tests.support.canonical_sync import FakeScheduler

    installed = tmp_path / "tool/bin/spec-dock"
    installed.parent.mkdir(parents=True)
    installed.write_text("#!/bin/sh\n")
    installed.chmod(0o755)
    pair.schedulers["launchd"] = FakeScheduler("launchd", recorded=installed)
    pair.run(pair.a, "canonical", "link")
    (spec,) = pair.schedulers["launchd"].specs
    assert spec.executable == installed


def test_a_link_from_another_path_keeps_the_jobs_gh_directory(
    pair: SyncPair, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    tools = tmp_path / "tools/bin"
    tools.mkdir(parents=True)
    (tools / "gh").write_text("#!/bin/sh\n")
    (tools / "gh").chmod(0o755)
    monkeypatch.setenv("PATH", f"{tools}{os.pathsep}{os.environ['PATH']}")
    linked = replace(environment(), environ=dict(os.environ))
    monkeypatch.setattr(runtime_environment, "detect_runtime_environment", lambda *a, **k: linked)
    pair.run(pair.a, "canonical", "link")
    (spec,) = pair.schedulers["launchd"].specs
    assert spec.gh_dir == tools
    other = replace(environment(), environ={**os.environ, "PATH": "/usr/bin:/bin"})
    monkeypatch.setattr(runtime_environment, "detect_runtime_environment", lambda *a, **k: other)
    code, result = pair.run(pair.a, "canonical", "link")
    assert code == 0 and result["status"] == "unchanged", result
    assert pair.schedulers["launchd"].calls == [("ensure", "launchd"), ("kick", "launchd")]


def test_a_no_schedule_link_still_moves_the_baseline_of_a_moved_main(pair: SyncPair, tmp_path: Path) -> None:
    pair.run(pair.a, "canonical", "link", "--no-schedule")
    before = pair.state(pair.a)
    assert before is not None
    moved = tmp_path / "moved"
    shutil.move(str(pair.a), moved)
    code, result = pair.run(moved, "canonical", "link", "--no-schedule")
    assert code == 0, result
    from spec_dock.runtime.infra.canonical_state import read_catalog_state

    after = read_catalog_state(pair.state_root, os.path.realpath(moved / "spec-dock/.canonical"))
    assert after is not None and after.last_seen_remote == before.last_seen_remote


def test_an_offline_link_registers_but_asks_for_no_cycle_now(pair: SyncPair) -> None:
    code, result = pair.run(pair.a, "canonical", "link", "--offline")
    assert code == 0, result
    assert pair.schedulers["launchd"].calls == [("ensure", "launchd")]


def test_a_link_from_another_state_root_never_repoints_the_job(
    pair: SyncPair, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    assert pair.run(pair.a, "canonical", "link")[0] == 0
    launchd = pair.schedulers["launchd"]
    calls = list(launchd.calls)
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "other-state"))
    code, result = pair.run(pair.b, "canonical", "link")
    assert code == 3 and result["error"]["code"] == "CANONICAL_STATE_ROOT_MISMATCH", result
    assert result["error"]["details"]["recorded_state_root"] == str(pair.state_root)
    assert launchd.calls == calls and launchd.specs[-1].state_root == pair.state_root
    assert not (tmp_path / "other-state/spec-dock/canonical-registry.json").exists()


def test_status_and_remove_from_another_state_root_leave_the_job_alone(
    pair: SyncPair, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    assert pair.run(pair.a, "canonical", "link")[0] == 0
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "other-state"))
    assert pair.run(pair.b, "canonical", "link", "--no-schedule")[0] == 0
    other = tmp_path / "other-state/spec-dock"
    git_path = shutil.which("git")
    assert git_path is not None
    entry = RegistryEntry(os.path.realpath(pair.catalog(pair.b)), str(pair.b), None, git_path, "2026-01-01T00:00:00Z")
    update_registry(other, lambda registry: replace(registry.with_entry(entry), scheduler="launchd"))
    code, result = pair.run(pair.b, "canonical", "status")
    assert code == 0 and "CANONICAL_STATE_ROOT_MISMATCH" in _codes(result), result
    code, result = pair.run(pair.b, "canonical", "remove", "--yes")
    assert code == 0, result
    assert ("remove", "launchd") not in pair.schedulers["launchd"].calls


def test_gh_beside_git_seen_again_through_an_alias_directory_changes_nothing(
    pair: SyncPair, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    tools = tmp_path / "usr-bin"
    tools.mkdir()
    git_path = shutil.which("git")
    assert git_path is not None
    (tools / "git").symlink_to(git_path)
    (tools / "gh").write_text("#!/bin/sh\nexit 0\n")
    (tools / "gh").chmod(0o755)
    alias = tmp_path / "bin"
    alias.symlink_to(tools)  # merged /usr: /bin is /usr/bin, so the job's PATH tail shows the same gh again
    monkeypatch.setenv("PATH", f"{tools}:{os.environ['PATH']}")
    launchd = pair.schedulers.setdefault("launchd", FakeScheduler("launchd"))
    launchd.tail = f"{alias}:/usr/bin:/bin"
    assert pair.run(pair.a, "canonical", "link")[0] == 0
    code, again = pair.run(pair.a, "canonical", "link")
    assert code == 0 and again["status"] == "unchanged", again
    assert launchd.specs[-1].gh_dir == tools
