"""Native process termination preserves visible immutable-selection boundaries."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from typing import TYPE_CHECKING

import pytest

from tests.cli_runtime.test_issue413_work_start import committed_workspace

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.skipif(os.name == "nt", reason="POSIX native kill and directory flock fixture")
@pytest.mark.parametrize("phase", ["stage", "rename", "unlink"])
def test_killed_start_at_record_boundary_requires_no_operation_journal(tmp_path: Path, phase: str) -> None:
    import fcntl

    root = committed_workspace(tmp_path / "main")
    first = root / "spec-dock/initiatives/init-00001-fixture"
    second = first.parent / "init-00002-second"
    second.mkdir()
    metadata = json.loads((first / ".meta.json").read_bytes())
    (second / ".meta.json").write_text(
        json.dumps(dict(metadata, id="init-00002", slug="second", github=dict(metadata["github"], issue_number=2)))
    )
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
            "second scope",
        ],
        check=True,
        capture_output=True,
    )
    binary = tmp_path / "bin"
    binary.mkdir()
    gh = binary / "gh"
    gh.write_text(
        f"#!{sys.executable}\nimport json, sys\n"
        "if '--method' not in sys.argv or sys.argv[sys.argv.index('--method')+1] != 'GET': sys.exit(99)\n"
        "number=int(sys.argv[-1].rsplit('/', 1)[1])\n"
        "print('HTTP/2 200 OK\\n\\n' + json.dumps({"
        "'number':number,'repository_url':'https://api.github.com/repos/example/repo',"
        "'html_url':'https://github.com/example/repo/issues/' + str(number),'title':'Fixture',"
        "'state':'open','state_reason':None,'updated_at':'2026-09-30T00:00:00Z'}))\n"
    )
    gh.chmod(0o700)
    environment = dict(os.environ, PATH=str(binary) + os.pathsep + os.environ.get("PATH", ""))
    entrypoint = "import sys; from spec_dock.cli import main; sys.exit(main(sys.argv[1:]))"
    prefix = [sys.executable, "-c", entrypoint, "--project", str(root)]
    state = root / "spec-dock/.agent/work-target"
    target = "init-00002" if phase == "unlink" else "init-00001"
    if phase == "unlink":
        seed = subprocess.run(
            [*prefix, "work", "start", "init-00001", "--branch", "seed", "--base", "HEAD", "--json"],
            env=environment,
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert seed.returncode == 0, seed.stdout + seed.stderr
    marker = tmp_path / "record-boundary"
    driver = (
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
            str(root),
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
        deadline = time.monotonic() + 15
        while not marker.exists():
            assert process.poll() is None, process.communicate()
            assert time.monotonic() < deadline, "record boundary was not reached"
            time.sleep(0.01)
        process.kill()
        stdout, stderr = process.communicate(timeout=5)
        assert process.returncode == -9
        assert stdout == stderr == ""
        fd = os.open(root / ".git", os.O_RDONLY | os.O_DIRECTORY)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            os.close(fd)
        assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"interrupted\n"
        assert not (root / ".git/spec-dock").exists()
        active = subprocess.run(
            [*prefix, "active", "show", "--json"], env=environment, capture_output=True, text=True, timeout=15
        )
        assert active.returncode == 0, active.stdout + active.stderr
        selection = json.loads(active.stdout)["data"]["selection"]
        assert selection["status"] == {"stage": "invalid", "rename": "selected", "unlink": "empty"}[phase]
        if phase == "stage":
            assert list(state.glob(".stage-*"))
            assert not list(state.glob("target-*.json"))
        elif phase == "rename":
            assert selection["scope_id"] == "init-00001"
            assert len(list(state.glob("target-*.json"))) == 1
        else:
            assert not list(state.iterdir())
        retry = subprocess.run(
            [*prefix, "work", "start", target, "--branch", "interrupted", "--json"],
            env=environment,
            capture_output=True,
            text=True,
            timeout=20,
        )
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
