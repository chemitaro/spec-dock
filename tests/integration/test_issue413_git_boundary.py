"""Public commands keep native Git failures and per-call timeout boundaries."""

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
from tests.cli_runtime.test_issue413_work_start import committed_workspace, open_issue

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.skipif(os.name == "nt", reason="POSIX executable fixture")
def test_project_git_failure_retains_native_streams_without_mutations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    real_git = shutil.which("git")
    assert real_git
    binary = tmp_path / "bin"
    binary.mkdir()
    git = binary / "git"
    git.write_text(
        f"#!{sys.executable}\nimport os, sys\n"
        "if sys.argv[-2:] == ['rev-parse', '--show-toplevel']:\n"
        " sys.stdout.write('fixture stdout\\n')\n"
        " sys.stderr.write('fixture Git error\\nsecond line\\n')\n"
        " sys.exit(19)\n"
        f"os.execv({real_git!r}, [{real_git!r}, *sys.argv[1:]])\n"
    )
    git.chmod(0o700)
    monkeypatch.setenv("PATH", str(binary) + os.pathsep + os.environ.get("PATH", ""))
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--json"]) == 5
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == ""
    assert result["effects"] == []
    assert result["error"]["code"] == "GIT_FAILED"
    assert result["error"]["details"]["git"]["returncode"] == 19
    assert result["error"]["details"]["git"]["stdout"] == "fixture stdout\n"
    assert result["error"]["details"]["git"]["stderr"] == "fixture Git error\nsecond line\n"
    assert not (root / "spec-dock/.agent/work-target").exists()


@pytest.mark.skipif(os.name == "nt", reason="POSIX executable fixture")
def test_created_branch_tip_is_confirmed_before_checkout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    (root / "readme.md").write_text("second commit\n")
    subprocess.run(["git", "-C", str(root), "add", "readme.md"], check=True, capture_output=True)
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
            "second fixture",
        ],
        check=True,
        capture_output=True,
    )
    real_git = shutil.which("git")
    assert real_git
    binary = tmp_path / "bin"
    binary.mkdir()
    git = binary / "git"
    git.write_text(
        f"#!{sys.executable}\nimport os, sys\n"
        "if len(sys.argv)==6 and sys.argv[3] == 'branch':\n"
        f" os.execv({real_git!r}, [{real_git!r}, *sys.argv[1:5], 'HEAD~1'])\n"
        f"os.execv({real_git!r}, [{real_git!r}, *sys.argv[1:]])\n"
    )
    git.chmod(0o700)
    monkeypatch.setenv("PATH", str(binary) + os.pathsep + os.environ.get("PATH", ""))
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--json"]) == 6
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == ""
    assert result["data"]["branch_after"] == "main"
    assert result["data"]["started"] is False
    assert {effect["kind"]: effect["status"] for effect in result["effects"]} == {
        "git.branch.create": "succeeded",
        "git.checkout": "not_attempted",
        "selection.publish": "not_attempted",
    }
    assert subprocess.check_output([real_git, "-C", str(root), "show-ref", "--verify", "refs/heads/init-00001-fixture"])
    assert not (root / "spec-dock/.agent/work-target").exists()


@pytest.mark.skipif(os.name == "nt", reason="POSIX executable fixture")
def test_invalid_base_commit_output_stops_before_effects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    real_git = shutil.which("git")
    assert real_git
    binary = tmp_path / "bin"
    binary.mkdir()
    git = binary / "git"
    git.write_text(
        f"#!{sys.executable}\nimport os, sys\n"
        "if sys.argv[-1] == 'HEAD^{commit}':\n"
        " print('g' * 40); sys.exit(0)\n"
        f"os.execv({real_git!r}, [{real_git!r}, *sys.argv[1:]])\n"
    )
    git.chmod(0o700)
    monkeypatch.setenv("PATH", str(binary) + os.pathsep + os.environ.get("PATH", ""))
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--json"]) == 3
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == ""
    assert result["effects"] == []
    assert "commit OID" in result["error"]["message"]
    assert not (root / "spec-dock/.agent/work-target").exists()


@pytest.mark.skipif(os.name == "nt", reason="POSIX executable fixture")
def test_project_git_uses_requested_timeout_and_retains_captured_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    real_git = shutil.which("git")
    assert real_git
    binary = tmp_path / "bin"
    binary.mkdir()
    git = binary / "git"
    git.write_text(
        f"#!{sys.executable}\nimport os, sys, time\n"
        "if sys.argv[-2:] == ['rev-parse', '--show-toplevel']:\n"
        " sys.stderr.write('fixture Git before timeout\\n'); sys.stderr.flush()\n"
        " time.sleep(2)\n"
        f"os.execv({real_git!r}, [{real_git!r}, *sys.argv[1:]])\n"
    )
    git.chmod(0o700)
    monkeypatch.setenv("PATH", str(binary) + os.pathsep + os.environ.get("PATH", ""))
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
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], stalled: bool
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    real_git = shutil.which("git")
    assert real_git
    binary = tmp_path / "bin"
    binary.mkdir()
    git = binary / "git"
    git.write_text(
        f"#!{sys.executable}\nimport os, sys, time\n"
        "if sys.argv[-4:] == ['worktree', 'list', '--porcelain', '-z']:\n"
        " sys.stdout.write('fixture inventory stdout\\n'); sys.stdout.flush()\n"
        " sys.stderr.write('fixture inventory error\\n'); sys.stderr.flush()\n"
        + (" time.sleep(2)\n" if stalled else " sys.exit(19)\n")
        + f"os.execv({real_git!r}, [{real_git!r}, *sys.argv[1:]])\n"
    )
    git.chmod(0o700)
    monkeypatch.setenv("PATH", str(binary) + os.pathsep + os.environ.get("PATH", ""))
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    assert (
        main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--timeout", "1", "--json"]) == 5
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == ""
    assert result["effects"] == []
    assert result["error"]["code"] == "GIT_FAILED"
    assert result["error"]["details"]["git"]["stdout"] == "fixture inventory stdout\n"
    assert result["error"]["details"]["git"]["stderr"] == "fixture inventory error\n"
    assert result["error"]["details"]["git"]["returncode"] == (None if stalled else 19)
    assert not (root / "spec-dock/.agent/work-target").exists()


@pytest.mark.skipif(os.name == "nt", reason="POSIX native signal fixture")
@pytest.mark.parametrize("interruption", ["signal", "timeout"])
def test_signalled_checkout_is_observed_without_claiming_failure_certainty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], interruption: str
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    real_git = shutil.which("git")
    assert real_git
    binary = tmp_path / "bin"
    binary.mkdir()
    git = binary / "git"
    git.write_text(
        f"#!{sys.executable}\nimport os, signal, sys, time\n"
        "if len(sys.argv)>3 and sys.argv[3] == 'checkout':\n"
        " sys.stderr.write('fixture Git interrupted\\n'); sys.stderr.flush()\n"
        + (" os.kill(os.getpid(), signal.SIGTERM)\n" if interruption == "signal" else " time.sleep(2)\n")
        + f"os.execv({real_git!r}, [{real_git!r}, *sys.argv[1:]])\n"
    )
    git.chmod(0o700)
    monkeypatch.setenv("PATH", str(binary) + os.pathsep + os.environ.get("PATH", ""))
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    assert (
        main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--timeout", "1", "--json"]) == 6
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == ""
    assert result["data"]["started"] is False
    assert result["data"]["branch_after"] == "main"
    effects = {effect["kind"]: effect["status"] for effect in result["effects"]}
    assert effects == {
        "git.branch.create": "succeeded",
        "git.checkout": "unknown",
        "selection.publish": "not_attempted",
    }
    assert result["error"]["details"]["git"]["stderr"] == "fixture Git interrupted\n"
    assert result["error"]["details"]["git"]["returncode"] == (-15 if interruption == "signal" else None)
    assert result["error"]["details"]["git"]["timed_out"] is (interruption == "timeout")
    assert not (root / "spec-dock/.agent/work-target").exists()


@pytest.mark.skipif(os.name == "nt", reason="POSIX executable fixture")
def test_linked_worktree_git_failure_remains_native_and_stops_start(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    linked = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "--detach", str(linked), "HEAD"], check=True, capture_output=True
    )
    real_git = shutil.which("git")
    assert real_git
    binary = tmp_path / "bin"
    binary.mkdir()
    git = binary / "git"
    git.write_text(
        f"#!{sys.executable}\nimport os, sys\n"
        f"if len(sys.argv)>2 and sys.argv[2] == {str(linked)!r} and sys.argv[-1] == '--show-toplevel':\n"
        " sys.stderr.write('fixture linked worktree error\\n'); sys.exit(19)\n"
        f"os.execv({real_git!r}, [{real_git!r}, *sys.argv[1:]])\n"
    )
    git.chmod(0o700)
    monkeypatch.setenv("PATH", str(binary) + os.pathsep + os.environ.get("PATH", ""))
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--json"]) == 5
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == ""
    assert result["effects"] == []
    assert result["error"]["code"] == "GIT_FAILED"
    assert result["error"]["details"]["git"]["stderr"] == "fixture linked worktree error\n"
    assert result["error"]["details"]["git"]["returncode"] == 19
    assert not (root / "spec-dock/.agent/work-target").exists()


@pytest.mark.skipif(os.name == "nt", reason="POSIX flock boundary with native separate git-dir clones")
def test_fresh_clone_context_must_match_the_held_start_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    import fcntl

    root = committed_workspace(tmp_path / "main")
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
        )
    )
    (root / "info/exclude").write_text(ignored + "\n")
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
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    assert (
        main([
            "--project",
            str(linked),
            "work",
            "start",
            "init-00001",
            "--branch",
            "unsafe",
            "--base",
            "HEAD",
            "--json",
        ])
        == 3
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert redirected, result
    assert output.err == ""
    assert result["error"]["code"] == "PROJECT_IDENTITY_CHANGED"
    assert result["effects"] == []
    assert not (linked / "spec-dock/.agent/work-target").exists()
    assert (
        subprocess.run(
            ["git", "--git-dir", str(root / ".git"), "show-ref", "--verify", "refs/heads/unsafe"], capture_output=True
        ).returncode
        != 0
    )


@pytest.mark.skipif(os.name == "nt", reason="POSIX native required smudge fixture")
def test_checkout_failure_with_unchanged_head_does_not_hide_changed_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "main")
    old_file = root / "a-remove.txt"
    old_file.write_text("tracked source file\n")
    subprocess.run(["git", "-C", str(root), "add", "a-remove.txt"], check=True, capture_output=True)
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
            "source file",
        ],
        check=True,
        capture_output=True,
    )
    head_before = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"])
    subprocess.run(["git", "-C", str(root), "checkout", "-qb", "candidate"], check=True, capture_output=True)
    old_file.unlink()
    (root / "z-fail.txt").write_text("candidate file\n")
    (root / ".gitattributes").write_text("z-fail.txt filter=fixture\n")
    subprocess.run(["git", "-C", str(root), "add", "."], check=True, capture_output=True)
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
            "filter candidate",
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "-C", str(root), "checkout", "-q", "main"], check=True, capture_output=True)
    smudge = tmp_path / "smudge"
    smudge.write_text(f"#!{sys.executable}\nimport sys\nsys.stderr.write('fixture smudge failed\\n')\nsys.exit(1)\n")
    smudge.chmod(0o700)
    subprocess.run(
        ["git", "-C", str(root), "config", "filter.fixture.smudge", shlex.quote(str(smudge))],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(root), "config", "filter.fixture.required", "true"], check=True, capture_output=True
    )
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    assert main(["--project", str(root), "work", "start", "init-00001", "--branch", "candidate", "--json"]) == 6
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == ""
    assert subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"]) == head_before
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"main\n"
    assert not old_file.exists()
    assert subprocess.check_output(["git", "-C", str(root), "status", "--porcelain", "-z"])
    assert result["data"]["started"] is False
    assert {effect["kind"]: effect["status"] for effect in result["effects"]} == {
        "git.branch.create": "unchanged",
        "git.checkout": "unknown",
        "selection.publish": "not_attempted",
    }
    assert "fixture smudge failed\n" in result["error"]["details"]["git"]["stderr"]
    assert not (root / "spec-dock/.agent/work-target").exists()
