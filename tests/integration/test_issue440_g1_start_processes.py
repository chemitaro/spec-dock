"""Real `work start` processes share one Start lock, survive a kill, and leave other writers alone (canonical mode).

Replaces tests/integration/test_issue413_start.py, tests/integration/test_issue413_record_kill.py and the
common-contract tests of tests/integration/test_cli_writer_compatibility_vnext.py (iss-00440). Child processes run
the package this test imported, with the fake GitHub on PATH and temporary user state.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
import time
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.infra.start_lock import StartLock
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.canonical_repo import git
from tests.support.legacy_contracts_g1 import (
    CHILD_ENTRY,
    CHILD_SETUP,
    chain_world,
    child_environment,
    records,
    run_process,
)

if TYPE_CHECKING:
    from pathlib import Path

    from tests.support.canonical_writes import WriteWorld

ENTRYPOINT = CHILD_ENTRY


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> WriteWorld:
    return chain_world(tmp_path, monkeypatch, capsys, write=True, sibling=True)  # type: ignore[return-value]


def _gated_gh(world: WriteWorld, barrier: Path) -> dict[str, str]:
    """A `gh` before the fake one: each CLI process waits at its first call until both arrived; calls are serial."""
    binary = world.tmp_path / "gated-gh-bin"
    binary.mkdir()
    gh = binary / "gh"
    gh.write_text(
        f"#!{sys.executable}\n"
        "import fcntl, os, sys, time\nfrom pathlib import Path\n"
        f"barrier=Path({str(barrier)!r})\n"
        "mine=barrier / str(os.getppid())\n"
        "if not mine.exists():\n"
        " mine.touch()\n"
        " deadline=time.monotonic()+20\n"
        " while len(list(barrier.iterdir())) < 2:\n"
        "  if time.monotonic()>deadline: sys.exit(97)\n"
        "  time.sleep(.01)\n"
        f"fd=os.open({str(world.tmp_path / 'gh.lock')!r}, os.O_RDWR | os.O_CREAT, 0o600)\n"
        "fcntl.flock(fd, fcntl.LOCK_EX)\n"
        "os.set_inheritable(fd, True)\n"
        f"os.execv({str(world.gh.bin_dir / 'gh')!r}, ['gh', *sys.argv[1:]])\n"
    )
    gh.chmod(0o700)
    environment = child_environment()
    environment["PATH"] = str(binary) + os.pathsep + environment["PATH"]
    return environment


@pytest.mark.skipif(os.name == "nt", reason="POSIX native lock and process fixture")
@pytest.mark.parametrize("same_scope", [True, False])
def test_concurrent_starts_share_exclusion_and_only_same_scope_conflicts(world: WriteWorld, same_scope: bool) -> None:
    linked = world.worktree("linked")
    targets = ("iss-00003", "iss-00003") if same_scope else ("iss-00003", "iss-00004")
    barrier = world.tmp_path / "barrier"
    barrier.mkdir()
    environment = _gated_gh(world, barrier)
    processes = []
    try:
        for path, branch, target in ((world.main, "left", targets[0]), (linked, "right", targets[1])):
            processes.append(
                subprocess.Popen(
                    [
                        sys.executable,
                        "-c",
                        ENTRYPOINT,
                        "--project",
                        str(path),
                        "work",
                        "start",
                        target,
                        "--branch",
                        branch,
                        "--base",
                        "HEAD",
                        "--json",
                    ],
                    env=environment,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
            )
        results = []
        for process in processes:
            stdout, stderr = process.communicate(timeout=90)
            assert stderr == "", stderr
            results.append((process.returncode, json.loads(stdout)))
        assert sorted(code for code, _ in results) == ([0, 3] if same_scope else [0, 0]), results
        if same_scope:
            loser = next(result for code, result in results if code == 3)
            assert loser["error"]["code"] == "SCOPE_ALREADY_SELECTED"
            assert loser["effects"] == []
        assert len(list(barrier.iterdir())) == 2
        assert sum(len(records(path)) for path in (world.main, linked)) == (1 if same_scope else 2)
        assert not (world.main / ".git/spec-dock").exists()
    finally:
        for process in processes:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)


@pytest.mark.skipif(os.name == "nt", reason="POSIX native process termination fixture")
def test_killed_start_preserves_checkout_and_next_start_needs_no_journal(world: WriteWorld) -> None:
    marker = world.tmp_path / "checkout-completed"
    hook = world.main / ".git/hooks/post-checkout"
    hook.write_text(f"#!/bin/sh\nprintf ready > {shlex.quote(str(marker))}\nsleep 2\n")
    hook.chmod(0o700)
    command = [sys.executable, "-c", ENTRYPOINT, "--project", str(world.main), "work", "start", "iss-00003"]
    process = subprocess.Popen(
        [*command, "--base", "HEAD", "--branch", "interrupted", "--json"],
        env=child_environment(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        deadline = time.monotonic() + 30
        while not marker.exists():
            assert process.poll() is None, process.communicate()
            assert time.monotonic() < deadline, "native post-checkout barrier was not reached"
            time.sleep(0.01)
        process.kill()
        assert process.wait(timeout=5) == -9
        with StartLock(world.main / ".git", timeout=0):
            pass
        stdout, _stderr = process.communicate(timeout=5)
        assert stdout == ""
        assert git(world.main, "branch", "--show-current") == "interrupted"
        assert not (world.main / "spec-dock/.agent/work-target").exists()
        assert not (world.main / ".git/spec-dock").exists()
        hook.unlink()
        next_result = run_process(world, "work", "start", "iss-00003", "--branch", "interrupted", timeout=60)
        assert next_result.returncode == 0, next_result.stdout + next_result.stderr
        assert next_result.stderr == ""
        assert json.loads(next_result.stdout)["data"]["started"] is True
        assert len(records(world.main)) == 1
    finally:
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=5)


@pytest.mark.skipif(os.name == "nt", reason="POSIX native kill and directory flock fixture")
@pytest.mark.parametrize("phase", ["stage", "rename", "unlink"])
def test_killed_start_at_record_boundary_requires_no_operation_journal(world: WriteWorld, phase: str) -> None:
    import fcntl

    environment = child_environment()
    prefix = [sys.executable, "-c", ENTRYPOINT, "--project", str(world.main)]
    state = world.main / "spec-dock/.agent/work-target"
    target = "iss-00004" if phase == "unlink" else "iss-00003"
    if phase == "unlink":
        seed = run_process(world, "work", "start", "iss-00003", "--branch", "seed", "--base", "HEAD", timeout=60)
        assert seed.returncode == 0, seed.stdout + seed.stderr
    marker = world.tmp_path / "record-boundary"
    driver = CHILD_SETUP + (
        "import os, stat, sys, time\nfrom pathlib import Path\n"
        f"state=Path({str(state)!r}); marker=Path({str(marker)!r}); phase={phase!r}\n"
        "native_sync=os.fsync; native_unlink=os.unlink\n"
        "def pause():\n marker.write_text(phase); time.sleep(60)\n"
        "def fsync(fd):\n"
        " observed=os.fstat(fd)\n"
        " if phase=='rename' and stat.S_ISDIR(observed.st_mode) and state.exists():\n"
        "  direct=state.stat()\n"
        "  if (observed.st_dev,observed.st_ino)==(direct.st_dev,direct.st_ino) and list(state.glob('target-*.json')):\n"
        "   pause()\n"
        " native_sync(fd)\n"
        " if phase=='stage' and stat.S_ISREG(observed.st_mode) and state.exists():\n"
        "  for path in state.glob('.stage-*'):\n"
        "   staged=path.stat()\n"
        "   if (observed.st_dev,observed.st_ino)==(staged.st_dev,staged.st_ino): pause()\n"
        "def unlink(path,*args,**kwargs):\n"
        " native_unlink(path,*args,**kwargs)\n"
        " if phase=='unlink' and isinstance(path,str) and path.startswith('target-') and path.endswith('.json'): pause()\n"
        "os.fsync=fsync; os.unlink=unlink\n"
        "from spec_dock.cli import main\nsys.exit(main(sys.argv[1:]))\n"
    )
    process = subprocess.Popen(
        [
            sys.executable,
            "-c",
            driver,
            "--project",
            str(world.main),
            "work",
            "start",
            target,
            "--branch",
            "interrupted",
            "--base",
            "HEAD",
            *(["--switch-active"] if phase == "unlink" else []),
            "--json",
        ],
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        deadline = time.monotonic() + 30
        while not marker.exists():
            assert process.poll() is None, process.communicate()
            assert time.monotonic() < deadline, "record boundary was not reached"
            time.sleep(0.01)
        process.kill()
        stdout, stderr = process.communicate(timeout=5)
        assert process.returncode == -9
        assert stdout == stderr == ""
        fd = os.open(world.main / ".git", os.O_RDONLY | os.O_DIRECTORY)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            os.close(fd)
        assert git(world.main, "branch", "--show-current") == "interrupted"
        assert not (world.main / ".git/spec-dock").exists()
        active = subprocess.run(
            [*prefix, "active", "show", "--json"], env=environment, capture_output=True, text=True, timeout=30
        )
        assert active.returncode == 0, active.stdout + active.stderr
        selection = json.loads(active.stdout)["data"]["selection"]
        assert selection["status"] == {"stage": "invalid", "rename": "selected", "unlink": "empty"}[phase]
        if phase == "stage":
            assert list(state.glob(".stage-*"))
            assert not list(state.glob("target-*.json"))
        elif phase == "rename":
            assert selection["scope_id"] == "iss-00003"
            assert len(list(state.glob("target-*.json"))) == 1
        else:
            assert not list(state.iterdir())
        retry = run_process(world, "work", "start", target, "--branch", "interrupted", timeout=60)
        assert retry.returncode == (3 if phase == "stage" else 0), retry.stdout + retry.stderr
        result = json.loads(retry.stdout)
        if phase == "stage":
            assert result["effects"] == []
            assert list(state.glob(".stage-*"))
        else:
            assert result["data"]["started"] is True
            assert len(list(state.glob("target-*.json"))) == 1
    finally:
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=5)


def test_linked_worktrees_share_git_identity_without_requiring_matching_writer_declarations(
    world: WriteWorld,
) -> None:
    linked = world.worktree("linked")
    common = {(root / git(root, "rev-parse", "--git-common-dir")).resolve() for root in (world.main, linked)}
    assert common == {(world.main / ".git").resolve()}
    declaration = linked / "spec-dock/workspace.json"
    declaration.write_text('{"schema_version":4,"writer_protocol":"specdock.writer/v1"}\n')
    other_before = tree_digest(linked / "spec-dock")
    code, payload = world.run("scope", "edit", "iss-00003", "--title", "Current worktree")
    assert code == 0, payload
    assert world.fake().issue(3).title == "Current worktree"
    assert tree_digest(linked / "spec-dock") == other_before
    assert not (linked / "spec-dock/.agent").exists()


@pytest.mark.skipif(os.name != "posix", reason="native POSIX directory Start lock across worktrees")
def test_start_exclusion_allows_a_public_scope_edit_in_a_different_worktree(world: WriteWorld) -> None:
    linked = world.worktree("linked")
    before = tree_digest(world.main / "spec-dock")
    with StartLock(world.main / ".git", timeout=0):
        result = run_process(
            world, "scope", "edit", "iss-00003", "--title", "Parallel writer", checkout=linked, timeout=60
        )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "specdock.cli/v2" and not result.stderr
    assert world.fake().issue(3).title == "Parallel writer"
    assert tree_digest(world.main / "spec-dock") == before
    assert not (world.main / "spec-dock/.agent").exists() and not (linked / "spec-dock/.agent/work-target").exists()
