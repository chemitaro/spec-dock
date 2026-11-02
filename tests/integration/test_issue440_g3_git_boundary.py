"""Canonical-mode commands keep native Git failures and per-call timeout boundaries (iss-00440).

Replaces tests/integration/test_issue413_git_boundary.py, which ran `work start` on the retired schema-3 committed
workspace with a patched legacy GitHub gateway. Here `work start` is the canonical one against the fake GitHub; it
adds its own follow-up effects (link, active links, GitHub marks), so the native Git effects are compared by kind.
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from tests.support.legacy_contracts_g3 import WORK_TARGET, git_out, make_world

if TYPE_CHECKING:
    from pathlib import Path

    from tests.support.canonical_writes import WriteWorld

SCOPE = "iss-00003"


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> WriteWorld:
    world = make_world(tmp_path, monkeypatch, capsys, write=True)
    world.scope("epic", 2, "Fixture", parent=1)
    world.scope("issue", 3, "Fixture", parent=2)
    return world  # type: ignore[return-value]


def _fake_git(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, imports: str, body: str) -> str:
    real_git = shutil.which("git")
    assert real_git
    binary = tmp_path / "bin"
    binary.mkdir()
    git = binary / "git"
    git.write_text(
        f"#!{sys.executable}\nimport {imports}\n" + body + f"os.execv({real_git!r}, [{real_git!r}, *sys.argv[1:]])\n"
    )
    git.chmod(0o700)
    monkeypatch.setenv("PATH", str(binary) + os.pathsep + os.environ.get("PATH", ""))
    return real_git


def _start(capsys: pytest.CaptureFixture[str], project: Path, *options: str) -> tuple[int, dict, str]:
    code = main(["--project", str(project), "work", "start", SCOPE, *options, "--json"])
    output = capsys.readouterr()
    return code, json.loads(output.out), output.err


def _native(result: dict) -> dict[str, str]:
    """The legacy Start effects; the canonical follow-ups after them must not have been applied."""
    native = ("git.branch.create", "git.checkout", "selection.publish")
    others = [effect for effect in result["effects"] if effect["kind"] not in native]
    assert all(effect["status"] != "succeeded" for effect in others), others
    return {effect["kind"]: effect["status"] for effect in result["effects"] if effect["kind"] in native}


def _commit(root: Path, message: str) -> None:
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", message], check=True, capture_output=True)


@pytest.mark.skipif(os.name == "nt", reason="POSIX executable fixture")
def test_project_git_failure_retains_native_streams_without_mutations(
    world: WriteWorld, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    _fake_git(
        tmp_path,
        monkeypatch,
        "os, sys",
        "if sys.argv[-2:] == ['rev-parse', '--show-toplevel']:\n"
        " sys.stdout.write('fixture stdout\\n')\n"
        " sys.stderr.write('fixture Git error\\nsecond line\\n')\n"
        " sys.exit(19)\n",
    )
    code, result, err = _start(capsys, root, "--base", "HEAD")
    assert code == 5, result
    assert err == ""
    assert result["effects"] == []
    assert result["error"]["code"] == "GIT_FAILED"
    assert result["error"]["details"]["git"]["returncode"] == 19
    assert result["error"]["details"]["git"]["stdout"] == "fixture stdout\n"
    assert result["error"]["details"]["git"]["stderr"] == "fixture Git error\nsecond line\n"
    assert not (root / WORK_TARGET).exists() and world.writes() == []


@pytest.mark.skipif(os.name == "nt", reason="POSIX executable fixture")
def test_created_branch_tip_is_confirmed_before_checkout(
    world: WriteWorld, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    (root / "readme.md").write_text("second commit\n")
    _commit(root, "second fixture")
    real_git = _fake_git(
        tmp_path,
        monkeypatch,
        "os, sys",
        "if len(sys.argv)==6 and sys.argv[3] == 'branch':\n"
        f" os.execv({shutil.which('git')!r}, [{shutil.which('git')!r}, *sys.argv[1:5], 'HEAD~1'])\n",
    )
    code, result, err = _start(capsys, root, "--base", "HEAD")
    assert code == 6, result
    assert err == ""
    assert result["data"]["branch_after"] == "main"
    assert result["data"]["started"] is False
    assert _native(result) == {
        "git.branch.create": "succeeded",
        "git.checkout": "not_attempted",
        "selection.publish": "not_attempted",
    }
    assert subprocess.check_output([real_git, "-C", str(root), "show-ref", "--verify", f"refs/heads/{SCOPE}"])
    assert not (root / WORK_TARGET).exists() and world.writes() == []


@pytest.mark.skipif(os.name == "nt", reason="POSIX executable fixture")
def test_invalid_base_commit_output_stops_before_effects(
    world: WriteWorld, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    _fake_git(
        tmp_path,
        monkeypatch,
        "os, sys",
        "if sys.argv[-1] == 'HEAD^{commit}':\n print('g' * 40); sys.exit(0)\n",
    )
    code, result, err = _start(capsys, root, "--base", "HEAD")
    assert code == 3, result
    assert err == ""
    assert result["effects"] == []
    assert "commit OID" in result["error"]["message"]
    assert not (root / WORK_TARGET).exists() and world.writes() == []


@pytest.mark.skipif(os.name == "nt", reason="POSIX executable fixture")
def test_project_git_uses_requested_timeout_and_retains_captured_output(
    world: WriteWorld, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    _fake_git(
        tmp_path,
        monkeypatch,
        "os, sys, time",
        "if sys.argv[-2:] == ['rev-parse', '--show-toplevel']:\n"
        " sys.stderr.write('fixture Git before timeout\\n'); sys.stderr.flush()\n"
        " time.sleep(2)\n",
    )
    assert main(["--project", str(root), "active", "show", "--timeout", "1", "--json"]) == 5
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == ""
    assert result["effects"] == []
    assert result["error"]["code"] == "GIT_FAILED"
    assert result["error"]["details"]["git"]["returncode"] is None
    assert result["error"]["details"]["git"]["stderr"] == "fixture Git before timeout\n"
    assert result["error"]["details"]["git"]["timed_out"] is True


@pytest.mark.skipif(os.name == "nt", reason="POSIX executable fixture")
@pytest.mark.parametrize("stalled", [False, True])
def test_inventory_git_failure_retains_native_output_and_stops_start(
    world: WriteWorld,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    stalled: bool,
) -> None:
    root = world.main
    _fake_git(
        tmp_path,
        monkeypatch,
        "os, sys, time",
        "if sys.argv[-4:] == ['worktree', 'list', '--porcelain', '-z']:\n"
        " sys.stdout.write('fixture inventory stdout\\n'); sys.stdout.flush()\n"
        " sys.stderr.write('fixture inventory error\\n'); sys.stderr.flush()\n"
        + (" time.sleep(2)\n" if stalled else " sys.exit(19)\n"),
    )
    code, result, err = _start(capsys, root, "--base", "HEAD", "--timeout", "1")
    assert code == 5, result
    assert err == ""
    assert result["effects"] == []
    assert result["error"]["code"] == "GIT_FAILED"
    assert result["error"]["details"]["git"]["stdout"] == "fixture inventory stdout\n"
    assert result["error"]["details"]["git"]["stderr"] == "fixture inventory error\n"
    assert result["error"]["details"]["git"]["returncode"] == (None if stalled else 19)
    assert not (root / WORK_TARGET).exists() and world.writes() == []


@pytest.mark.skipif(os.name == "nt", reason="POSIX native signal fixture")
@pytest.mark.parametrize("interruption", ["signal", "timeout"])
def test_signalled_checkout_is_observed_without_claiming_failure_certainty(
    world: WriteWorld,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    interruption: str,
) -> None:
    root = world.main
    _fake_git(
        tmp_path,
        monkeypatch,
        "os, signal, sys, time",
        "if len(sys.argv)>3 and sys.argv[3] == 'checkout':\n"
        " sys.stderr.write('fixture Git interrupted\\n'); sys.stderr.flush()\n"
        + (" os.kill(os.getpid(), signal.SIGTERM)\n" if interruption == "signal" else " time.sleep(2)\n"),
    )
    code, result, err = _start(capsys, root, "--base", "HEAD", "--timeout", "1")
    assert code == 6, result
    assert err == ""
    assert result["data"]["started"] is False
    assert result["data"]["branch_after"] == "main"
    assert _native(result) == {
        "git.branch.create": "succeeded",
        "git.checkout": "unknown",
        "selection.publish": "not_attempted",
    }
    assert result["error"]["details"]["git"]["stderr"] == "fixture Git interrupted\n"
    assert result["error"]["details"]["git"]["returncode"] == (-15 if interruption == "signal" else None)
    assert result["error"]["details"]["git"]["timed_out"] is (interruption == "timeout")
    assert not (root / WORK_TARGET).exists() and world.writes() == []


@pytest.mark.skipif(os.name == "nt", reason="POSIX executable fixture")
def test_linked_worktree_git_failure_remains_native_and_stops_start(
    world: WriteWorld, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    linked = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "--detach", str(linked), "HEAD"], check=True, capture_output=True
    )
    _fake_git(
        tmp_path,
        monkeypatch,
        "os, sys",
        f"if len(sys.argv)>2 and sys.argv[2] == {str(linked)!r} and sys.argv[-1] == '--show-toplevel':\n"
        " sys.stderr.write('fixture linked worktree error\\n'); sys.exit(19)\n",
    )
    code, result, err = _start(capsys, root, "--base", "HEAD")
    assert code == 5, result
    assert err == ""
    assert result["effects"] == []
    assert result["error"]["code"] == "GIT_FAILED"
    assert result["error"]["details"]["git"]["stderr"] == "fixture linked worktree error\n"
    assert result["error"]["details"]["git"]["returncode"] == 19
    assert not (root / WORK_TARGET).exists() and world.writes() == []


@pytest.mark.skipif(os.name == "nt", reason="POSIX flock boundary with a replaced common directory")
def test_fresh_clone_context_must_match_the_held_start_lock(
    world: WriteWorld, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    import fcntl

    root = world.main
    first_common = root
    displaced_git = tmp_path / "displaced-git"
    (root / ".git").rename(displaced_git)
    for entry in displaced_git.iterdir():
        entry.rename(root / entry.name)
    displaced_git.rmdir()
    (root / ".git").write_text(f"gitdir: {root}\n")
    ignored = "\n".join(
        f"/{name}"
        for name in (
            "HEAD",
            "config",
            "index",
            "objects",
            "refs",
            "logs",
            "worktrees",
            "description",
            "hooks",
            "packed-refs",
            "COMMIT_EDITMSG",
            "info",
            "FETCH_HEAD",
            "ORIG_HEAD",
        )
    )
    exclude = root / "info/exclude"
    exclude.write_text(exclude.read_text() + ignored + "\n")
    # the catalog worktree's back link pointed into the moved directory
    subprocess.run(["git", "-C", str(root), "worktree", "repair"], check=True, capture_output=True)
    linked = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "--detach", str(linked), "HEAD"], check=True, capture_output=True
    )
    second_common = tmp_path / "second-common"
    subprocess.run(["git", "clone", "--bare", str(first_common), str(second_common)], check=True, capture_output=True)
    subprocess.run(
        ["git", "--git-dir", str(second_common), "config", "core.bare", "false"], check=True, capture_output=True
    )
    shutil.copy2(first_common / "index", second_common / "index")
    shutil.copy2(first_common / "info/exclude", second_common / "info/exclude")
    shutil.copytree(first_common / "worktrees", second_common / "worktrees")
    native_flock = fcntl.flock
    redirected = False

    def redirect_after_acquisition(fd, operation):
        nonlocal redirected
        native_flock(fd, operation)
        if operation & fcntl.LOCK_EX and not redirected:
            redirected = True
            (root / ".git").unlink()
            second_common.rename(root / ".git")
            (first_common / "worktrees/linked/commondir").write_text(str(root / ".git") + "\n")

    monkeypatch.setattr(fcntl, "flock", redirect_after_acquisition)
    code, result, err = _start(capsys, linked, "--branch", "unsafe", "--base", "HEAD")
    assert redirected, result
    assert code == 3, result
    assert err == ""
    # canonical start reads every worktree again under the lock and notices the replaced common directory there
    # (PRECONDITION_FAILED) before the legacy fresh-context check (PROJECT_IDENTITY_CHANGED)
    assert result["error"]["code"] in ("PROJECT_IDENTITY_CHANGED", "PRECONDITION_FAILED")
    assert "identity" in result["error"]["message"]
    assert result["effects"] == []
    assert not (linked / WORK_TARGET).exists() and world.writes() == []
    assert (
        subprocess.run(
            ["git", "--git-dir", str(root / ".git"), "show-ref", "--verify", "refs/heads/unsafe"], capture_output=True
        ).returncode
        != 0
    )


@pytest.mark.skipif(os.name == "nt", reason="POSIX native required smudge fixture")
def test_checkout_failure_with_unchanged_head_does_not_hide_changed_files(
    world: WriteWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    old_file = root / "a-remove.txt"
    old_file.write_text("tracked source file\n")
    _commit(root, "source file")
    head_before = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"])
    subprocess.run(["git", "-C", str(root), "checkout", "-qb", "candidate"], check=True, capture_output=True)
    old_file.unlink()
    (root / "z-fail.txt").write_text("candidate file\n")
    (root / ".gitattributes").write_text("z-fail.txt filter=fixture\n")
    _commit(root, "filter candidate")
    subprocess.run(["git", "-C", str(root), "checkout", "-q", "main"], check=True, capture_output=True)
    smudge = tmp_path / "smudge"
    smudge.write_text(f"#!{sys.executable}\nimport sys\nsys.stderr.write('fixture smudge failed\\n')\nsys.exit(1)\n")
    smudge.chmod(0o700)
    git_out(root, "config", "filter.fixture.smudge", shlex.quote(str(smudge)))
    git_out(root, "config", "filter.fixture.required", "true")
    code, result, err = _start(capsys, root, "--branch", "candidate")
    assert code == 6, result
    assert err == ""
    assert subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"]) == head_before
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"main\n"
    assert not old_file.exists()
    assert subprocess.check_output(["git", "-C", str(root), "status", "--porcelain", "-z"])
    assert result["data"]["started"] is False
    assert _native(result) == {
        "git.branch.create": "unchanged",
        "git.checkout": "unknown",
        "selection.publish": "not_attempted",
    }
    assert "fixture smudge failed\n" in result["error"]["details"]["git"]["stderr"]
    assert not (root / WORK_TARGET).exists() and world.writes() == []
