"""Real concurrent public Start processes share exclusion, never a registry."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

from tests.cli_runtime.test_issue413_work_start import committed_workspace

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.skipif(os.name == "nt", reason="Windows native immutable store is not connected yet")
def test_concurrent_starts_of_one_scope_publish_one_target_and_loser_has_no_effects(tmp_path: Path) -> None:
    root = committed_workspace(tmp_path / "main")
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
        "if sys.argv[-1] != 'repos/example/repo/issues/1': sys.exit(98)\n"
        "barrier=Path(os.environ['SPECDOCK_TEST_BARRIER'])\n"
        "(barrier / str(os.getpid())).touch()\n"
        "deadline=time.monotonic()+10\n"
        "while len(list(barrier.iterdir())) < 2:\n"
        " if time.monotonic()>deadline: sys.exit(97)\n"
        " time.sleep(.01)\n"
        "print('HTTP/2 200 OK\\n\\n' + json.dumps({"
        "'number':1,'repository_url':'https://api.github.com/repos/example/repo',"
        "'html_url':'https://github.com/example/repo/issues/1',"
        "'title':'Fixture','state':'open','state_reason':None,'updated_at':'2026-09-30T00:00:00Z'}))\n"
    )
    gh.chmod(0o700)
    environment = dict(os.environ, PATH=str(binary) + os.pathsep + os.environ.get("PATH", ""))
    environment["SPECDOCK_TEST_BARRIER"] = str(barrier)
    processes = []
    try:
        for path, branch in ((root, "left"), (linked, "right")):
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
                        "init-00001",
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
        assert sorted(code for code, _ in results) == [0, 3]
        loser = next(result for code, result in results if code == 3)
        assert loser["error"]["code"] == "SCOPE_ALREADY_SELECTED"
        assert loser["effects"] == []
        assert (
            sum(len(list((path / "spec-dock/.agent/work-target").glob("target-*.json"))) for path in (root, linked))
            == 1
        )
        assert not (root / ".git/spec-dock").exists()
    finally:
        for process in processes:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
