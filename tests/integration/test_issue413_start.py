"""Real concurrent public Start processes share exclusion, never a registry."""

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
from tests.cli_runtime.test_issue413_work_start import committed_workspace

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize("same_scope", [True, False])
def test_concurrent_starts_share_exclusion_and_only_same_scope_conflicts(tmp_path: Path, same_scope: bool) -> None:
    root = committed_workspace(tmp_path / "main")
    targets = ("init-00001", "init-00001")
    if not same_scope:
        initiative = root / "spec-dock/initiatives/init-00001-fixture"
        original = json.loads((initiative / ".meta.json").read_bytes())
        epic = initiative / "epics/epic-00002-fixture"
        for path, scope_id, kind, number, parent, epic_id in (
            (epic, "epic-00002", "epic", 2, "init-00001", None),
            (epic / "issues/iss-00003-fixture", "iss-00003", "issue", 3, "epic-00002", "epic-00002"),
            (epic / "issues/iss-00004-fixture", "iss-00004", "issue", 4, "epic-00002", "epic-00002"),
        ):
            path.mkdir(parents=True, exist_ok=True)
            metadata = dict(
                original, id=scope_id, type=kind, parent_id=parent, initiative_id="init-00001", epic_id=epic_id
            )
            metadata["github"] = dict(original["github"], issue_number=number)
            (path / ".meta.json").write_text(json.dumps(metadata))
        subprocess.run(["git", "-C", str(root), "add", "spec-dock"], check=True, capture_output=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "-c",
                "user.name=Fixture",
                "-c",
                "user.email=fixture@example.invalid",
                "commit",
                "-qm",
                "sibling issues",
            ],
            check=True,
            capture_output=True,
        )
        targets = ("iss-00003", "iss-00004")
    linked = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "--detach", str(linked), "HEAD"],
        check=True,
        capture_output=True,
    )
    binary = tmp_path / "bin"
    binary.mkdir()
    barrier = tmp_path / "barrier"
    barrier.mkdir()
    gh = binary / "gh"
    gh.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys, time\nfrom pathlib import Path\n"
        "if '--method' not in sys.argv or sys.argv[sys.argv.index('--method')+1] != 'GET': sys.exit(99)\n"
        "if not sys.argv[-1].startswith('repos/example/repo/issues/'): sys.exit(98)\n"
        "number=int(sys.argv[-1].rsplit('/', 1)[1])\n"
        "barrier=Path(os.environ['SPECDOCK_TEST_BARRIER'])\n"
        "(barrier / str(os.getpid())).touch()\n"
        "deadline=time.monotonic()+10\n"
        "while len(list(barrier.iterdir())) < 2:\n"
        " if time.monotonic()>deadline: sys.exit(97)\n"
        " time.sleep(.01)\n"
        "print('HTTP/2 200 OK\\n\\n' + json.dumps({"
        "'number':number,'repository_url':'https://api.github.com/repos/example/repo',"
        "'html_url':'https://github.com/example/repo/issues/' + str(number),"
        "'title':'Fixture','state':'open','state_reason':None,'updated_at':'2026-09-30T00:00:00Z'}))\n"
    )
    gh.chmod(0o700)
    environment = dict(os.environ, PATH=str(binary) + os.pathsep + os.environ.get("PATH", ""))
    environment["SPECDOCK_TEST_BARRIER"] = str(barrier)
    processes = []
    try:
        for path, branch, target in ((root, "left", targets[0]), (linked, "right", targets[1])):
            processes.append(
                subprocess.Popen(
                    [
                        sys.executable,
                        "-c",
                        "import sys; from spec_dock.cli import main; sys.exit(main(sys.argv[1:]))",
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
            stdout, stderr = process.communicate(timeout=30)
            assert stderr == "", stderr
            results.append((process.returncode, json.loads(stdout)))
        assert sorted(code for code, _ in results) == ([0, 3] if same_scope else [0, 0]), results
        if same_scope:
            loser = next(result for code, result in results if code == 3)
            assert loser["error"]["code"] == "SCOPE_ALREADY_SELECTED"
            assert loser["effects"] == []
        assert sum(
            len(list((path / "spec-dock/.agent/work-target").glob("target-*.json"))) for path in (root, linked)
        ) == (1 if same_scope else 2)
        assert not (root / ".git/spec-dock").exists()
    finally:
        for process in processes:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)


@pytest.mark.skipif(os.name == "nt", reason="POSIX native process termination fixture")
def test_killed_start_preserves_checkout_and_next_start_needs_no_journal(tmp_path: Path) -> None:
    root = committed_workspace(tmp_path / "main")
    marker = tmp_path / "checkout-completed"
    hook = root / ".git/hooks/post-checkout"
    hook.write_text(f"#!/bin/sh\nprintf ready > {shlex.quote(str(marker))}\nsleep 2\n")
    hook.chmod(0o700)
    binary = tmp_path / "bin"
    binary.mkdir()
    gh = binary / "gh"
    gh.write_text(
        f"#!{sys.executable}\nimport json, sys\n"
        "if '--method' not in sys.argv or sys.argv[sys.argv.index('--method')+1] != 'GET': sys.exit(99)\n"
        "print('HTTP/2 200 OK\\n\\n' + json.dumps({"
        "'number':1,'repository_url':'https://api.github.com/repos/example/repo',"
        "'html_url':'https://github.com/example/repo/issues/1','title':'Fixture',"
        "'state':'open','state_reason':None,'updated_at':'2026-09-30T00:00:00Z'}))\n"
    )
    gh.chmod(0o700)
    environment = dict(os.environ, PATH=str(binary) + os.pathsep + os.environ.get("PATH", ""))
    command = [
        sys.executable,
        "-c",
        "import sys; from spec_dock.cli import main; sys.exit(main(sys.argv[1:]))",
        "--project",
        str(root),
        "work",
        "start",
        "init-00001",
    ]
    process = subprocess.Popen(
        [*command, "--base", "HEAD", "--branch", "interrupted", "--json"],
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        deadline = time.monotonic() + 10
        while not marker.exists():
            assert process.poll() is None, process.communicate()
            assert time.monotonic() < deadline, "native post-checkout barrier was not reached"
            time.sleep(0.01)
        process.kill()
        assert process.wait(timeout=5) == -9
        with StartLock(root / ".git", timeout=0):
            pass
        stdout, _stderr = process.communicate(timeout=5)
        assert stdout == ""
        assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"interrupted\n"
        assert not (root / "spec-dock/.agent/work-target").exists()
        assert not (root / ".git/spec-dock").exists()
        hook.unlink()
        next_result = subprocess.run(
            [*command, "--branch", "interrupted", "--json"],
            env=environment,
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert next_result.returncode == 0, next_result.stdout + next_result.stderr
        assert next_result.stderr == ""
        assert json.loads(next_result.stdout)["data"]["started"] is True
        assert len(list((root / "spec-dock/.agent/work-target").glob("target-*.json"))) == 1
    finally:
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=5)
