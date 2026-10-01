"""Run one explicitly selected project's init hook without bootstrap receipts."""

from __future__ import annotations

import errno
import json
import os
import shlex
import shutil
import signal
import subprocess
import sys
import time
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from tests.cli_runtime.test_issue413_active import select_fixture
from tests.cli_runtime.test_issue413_contract import add_scope
from tests.cli_runtime.test_issue413_worktree_remove import linked_workspace

if TYPE_CHECKING:
    from pathlib import Path


def test_bootstrap_runs_make_init_only_in_the_explicit_native_worktree(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other = linked_workspace(tmp_path)
    (other / "Makefile").write_text("init:\n\t@printf 'one run\\n' >> bootstrap-ran\n", encoding="utf-8")
    assert main(["--project", str(root), "worktree", "bootstrap", str(other), "--yes", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert (other / "bootstrap-ran").read_bytes() == b"one run\n" and not (root / "bootstrap-ran").exists()
    assert result["data"]["result"]["path"] == str(other) and result["data"]["result"]["changed"] is True
    assert result["data"]["result"]["observed"]["started"] is True
    assert result["data"]["result"]["observed"]["returncode"] == 0
    assert result["effects"] == [{"kind": "worktree-bootstrap", "status": "succeeded", "target": str(other)}]
    assert not (root / ".git/spec-dock").exists() and not (root / "spec-dock/.agent").exists()
    assert not (other / "spec-dock/.agent").exists()


@pytest.mark.parametrize("unsafe", ["missing", "symlink", "directory", "hardlink"])
def test_bootstrap_requires_a_project_owned_regular_makefile_before_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], unsafe: str
) -> None:
    root, other = linked_workspace(tmp_path)
    outside = tmp_path / "outside.make"
    outside.write_text("init:\n\t@touch trap-ran\n", encoding="utf-8")
    makefile = other / "Makefile"
    if unsafe == "symlink":
        makefile.symlink_to(outside)
    elif unsafe == "directory":
        makefile.mkdir()
    elif unsafe == "hardlink":
        os.link(outside, makefile)
    native_popen = subprocess.Popen
    make_calls: list[object] = []

    def popen(argv, *args, **kwargs):
        if argv[0] == "make":
            make_calls.append(argv)
        return native_popen(argv, *args, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", popen)
    assert main(["--project", str(root), "worktree", "bootstrap", str(other), "--yes", "--json"]) == 3
    assert json.loads(capsys.readouterr().out)["effects"] == [] and make_calls == []
    assert outside.read_text(encoding="utf-8") == "init:\n\t@touch trap-ran\n"
    assert not (other / "trap-ran").exists()


@pytest.mark.parametrize("inherited", ["MAKEFILES", "MAKEFLAGS", "MFLAGS"])
def test_bootstrap_uses_the_explicit_project_without_inherited_make_injection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], inherited: str
) -> None:
    root, other = linked_workspace(tmp_path)
    (other / "Makefile").write_text("init:\n\t@touch bootstrap-ran\n", encoding="utf-8")
    trap = tmp_path / "outside-trap"
    outside = tmp_path / "injected.make"
    outside.write_text(f"INJECTED := $(shell touch '{trap}')\n", encoding="utf-8")
    monkeypatch.setenv(inherited, str(outside) if inherited == "MAKEFILES" else "-n")
    assert main(["--project", str(root), "worktree", "bootstrap", str(other), "--yes", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["effects"][0]["status"] == "succeeded"
    assert (other / "bootstrap-ran").exists() and not trap.exists()


@pytest.mark.parametrize("mode", ["dry", "offline", "unconfirmed", "dry-offline"])
def test_bootstrap_does_not_evaluate_make_for_preview_offline_or_missing_confirmation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], mode: str
) -> None:
    root, other = linked_workspace(tmp_path)
    (other / "Makefile").write_text(
        "TRAP := $(shell touch trap-ran)\ninit:\n\t@touch bootstrap-ran\n", encoding="utf-8"
    )
    native_popen = subprocess.Popen
    calls: list[object] = []

    def popen(argv, *args, **kwargs):
        if argv[0] == "make":
            calls.append(argv)
        return native_popen(argv, *args, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", popen)
    flags = {
        "dry": ["--dry-run"],
        "offline": ["--offline", "--yes"],
        "unconfirmed": [],
        "dry-offline": ["--dry-run", "--offline"],
    }[mode]
    dry_run = mode in ("dry", "dry-offline")
    assert main(["--project", str(root), "worktree", "bootstrap", str(other), *flags, "--json"]) == (
        0 if dry_run else 3
    )
    result = json.loads(capsys.readouterr().out)
    assert calls == [] and not (other / "trap-ran").exists() and not (other / "bootstrap-ran").exists()
    assert not (root / ".git/spec-dock").exists() and not (other / "spec-dock/.agent").exists()
    if dry_run:
        assert result["data"]["result"]["can_apply"] is True and result["data"]["result"]["changed"] is False
        assert result["effects"] == [{"kind": "worktree-bootstrap", "status": "planned", "target": str(other)}]
    else:
        assert result["effects"] == []


@pytest.mark.skipif(os.name != "posix", reason="native POSIX process-group termination")
def test_bootstrap_timeout_keeps_applied_project_files_and_stops_its_child_group(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other = linked_workspace(tmp_path)
    (other / "Makefile").write_text(
        "init:\n\t@printf 'partial effect' > before-timeout\n\t@sleep 0.5; touch after-timeout\n", encoding="utf-8"
    )
    assert (
        main(["--project", str(root), "worktree", "bootstrap", str(other), "--yes", "--timeout", "0.1", "--json"]) == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert (other / "before-timeout").read_bytes() == b"partial effect"
    assert result["data"]["result"]["observed"]["started"] is True
    assert result["data"]["result"]["observed"]["timed_out"] is True
    assert result["effects"] == [{"kind": "worktree-bootstrap", "status": "unknown", "target": str(other)}]
    assert result["recovery"]["can_resume"] is False and result["recovery"]["can_rollback"] is False
    time.sleep(0.7)
    assert not (other / "after-timeout").exists() and not (root / ".git/spec-dock").exists()


def test_bootstrap_failure_omits_hook_output_and_only_runs_again_for_a_new_explicit_request(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other = linked_workspace(tmp_path)
    makefile = other / "Makefile"
    secret = "unlabelled-hook-secret"
    makefile.write_text(
        f"init:\n\t@printf 'first run\\n' >> run-count\n\t@printf '{secret}\\n'; exit 1\n", encoding="utf-8"
    )
    assert main(["--project", str(root), "worktree", "bootstrap", str(other), "--yes", "--json"]) == 6
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert secret not in output.out + output.err and result["data"]["result"]["observed"]["returncode"] != 0
    assert result["effects"] == [{"kind": "worktree-bootstrap", "status": "unknown", "target": str(other)}]
    assert (other / "run-count").read_bytes() == b"first run\n"
    makefile.write_text("init:\n\t@printf 'second run\\n' >> run-count\n", encoding="utf-8")
    assert main(["--project", str(root), "worktree", "bootstrap", str(other), "--yes", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "succeeded"
    assert (other / "run-count").read_bytes() == b"first run\nsecond run\n"
    assert not (root / ".git/spec-dock").exists()


def test_bootstrap_preserves_a_source_selection_change_and_does_not_run_the_hook(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other = linked_workspace(tmp_path)
    (other / "Makefile").write_text("init:\n\t@touch bootstrap-ran\n", encoding="utf-8")
    record = select_fixture(root)
    native_run = subprocess.run
    cleared = False

    def run(argv, *args, **kwargs):
        nonlocal cleared
        result = native_run(argv, *args, **kwargs)
        if not cleared and tuple(argv[:5]) == ("git", "-C", str(root), "worktree", "list"):
            cleared = True
            record.unlink()
        return result

    monkeypatch.setattr(subprocess, "run", run)
    assert (
        main([
            "--project",
            str(root),
            "worktree",
            "bootstrap",
            str(other),
            "--expect-current",
            "gh:example/repo#1",
            "--yes",
            "--json",
        ])
        == 3
    )
    assert json.loads(capsys.readouterr().out)["effects"] == []
    assert cleared and not record.exists() and not (other / "bootstrap-ran").exists()


@pytest.mark.parametrize("fault", ["replacement", "close"])
def test_bootstrap_keeps_completed_effects_after_target_identity_or_cleanup_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], fault: str
) -> None:
    root, other = linked_workspace(tmp_path)
    (other / "Makefile").write_text("init:\n\t@touch bootstrap-ran\n", encoding="utf-8")
    parked = tmp_path / "parked"
    initial = other.stat()
    target_identity = (initial.st_dev, initial.st_ino)
    native_wait = subprocess.Popen.wait
    native_close = os.close
    finished = injected = False

    def wait(process, *args, **kwargs):
        nonlocal finished, injected
        result = native_wait(process, *args, **kwargs)
        if not finished and process.args[0] == "make":
            assert result == 0
            finished = True
            if fault == "replacement":
                other.rename(parked)
                shutil.copytree(parked, other)
                injected = True
        return result

    def close(descriptor: int) -> None:
        nonlocal injected
        observed = os.fstat(descriptor)
        native_close(descriptor)
        if fault == "close" and finished and not injected and (observed.st_dev, observed.st_ino) == target_identity:
            injected = True
            raise OSError(errno.EIO, "fixture target close failure")

    monkeypatch.setattr(subprocess.Popen, "wait", wait)
    monkeypatch.setattr(os, "close", close)
    assert main(["--project", str(root), "worktree", "bootstrap", str(other), "--yes", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert finished and injected and result["data"]["result"]["changed"] is True
    assert result["effects"] == [{"kind": "worktree-bootstrap", "status": "succeeded", "target": str(other)}]
    assert (other / "bootstrap-ran").exists()
    if fault == "replacement":
        assert (parked / "bootstrap-ran").exists() and parked.stat().st_ino == initial.st_ino


@pytest.mark.parametrize("change", ["content", "priority"])
def test_bootstrap_preserves_a_changed_makefile_before_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], change: str
) -> None:
    root, other = linked_workspace(tmp_path)
    makefile = other / "Makefile"
    makefile.write_text("init:\n\t@touch original-ran\n", encoding="utf-8")
    actor_file = makefile if change == "content" else other / "GNUmakefile"
    actor_bytes = b"init:\n\t@touch actor-ran\n"
    native_run = subprocess.run
    branch_reads = 0
    changed = False

    def run(argv, *args, **kwargs):
        nonlocal branch_reads, changed
        result = native_run(argv, *args, **kwargs)
        if tuple(argv[:4]) == ("git", "-C", str(root), "symbolic-ref"):
            branch_reads += 1
            if branch_reads == 2:
                changed = True
                actor_file.write_bytes(actor_bytes)
        return result

    monkeypatch.setattr(subprocess, "run", run)
    assert main(["--project", str(root), "worktree", "bootstrap", str(other), "--yes", "--json"]) == 3
    assert json.loads(capsys.readouterr().out)["effects"] == [] and changed
    assert actor_file.read_bytes() == actor_bytes and not (other / "actor-ran").exists()
    assert not (other / "original-ran").exists()


@pytest.mark.parametrize("project", ["main", "linked"])
def test_bootstrap_allows_a_main_or_current_native_worktree(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], project: str
) -> None:
    root, other = linked_workspace(tmp_path)
    (root / "Makefile").write_text("init:\n\t@touch bootstrap-ran\n", encoding="utf-8")
    source = root if project == "main" else other
    assert main(["--project", str(source), "worktree", "bootstrap", str(root), "--yes", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "succeeded" and (root / "bootstrap-ran").exists()
    assert not (other / "bootstrap-ran").exists()


def test_bootstrap_can_initialize_a_native_target_without_a_workspace_declaration(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other = linked_workspace(tmp_path)
    (other / "spec-dock/workspace.json").unlink()
    (other / "Makefile").write_text("init:\n\t@touch bootstrap-ran\n", encoding="utf-8")
    assert main(["--project", str(root), "worktree", "bootstrap", str(other), "--yes", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "succeeded" and (other / "bootstrap-ran").exists()


@pytest.mark.parametrize("guard", ["matching-current", "other-current", "backend"])
def test_bootstrap_checks_canonical_source_guards_and_preserves_the_direct_record(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], guard: str
) -> None:
    root, other = linked_workspace(tmp_path)
    add_scope(root, "epic-00002", "epic", "init-00001", root / "spec-dock/initiatives/init-00001-fixture")
    record = select_fixture(root)
    original = record.read_bytes()
    (other / "Makefile").write_text("init:\n\t@touch bootstrap-ran\n", encoding="utf-8")
    flags = (
        ["--expect-backend", "github"]
        if guard == "backend"
        else ["--expect-current", "gh:example/repo#1" if guard == "matching-current" else "gh:example/repo#2"]
    )
    matches = guard == "matching-current"
    assert main(["--project", str(root), "worktree", "bootstrap", str(other), "--yes", *flags, "--json"]) == (
        0 if matches else 3
    )
    result = json.loads(capsys.readouterr().out)
    assert record.read_bytes() == original and (other / "bootstrap-ran").exists() is matches
    if not matches:
        assert result["effects"] == []


def test_bootstrap_reports_a_process_start_failure_without_an_unknown_hook_effect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other = linked_workspace(tmp_path)
    (other / "Makefile").write_text("init:\n\t@touch bootstrap-ran\n", encoding="utf-8")
    native_popen = subprocess.Popen
    calls = 0

    def popen(argv, *args, **kwargs):
        nonlocal calls
        if argv[0] == "make":
            calls += 1
            raise FileNotFoundError(errno.ENOENT, "fixture make not installed")
        return native_popen(argv, *args, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", popen)
    assert main(["--project", str(root), "worktree", "bootstrap", str(other), "--yes", "--json"]) == 5
    result = json.loads(capsys.readouterr().out)
    assert calls == 1 and result["data"]["result"]["observed"]["started"] is False
    assert result["effects"] == [{"kind": "worktree-bootstrap", "status": "failed", "target": str(other)}]
    assert not (other / "bootstrap-ran").exists() and result["recovery"] is None


@pytest.mark.skipif(os.name != "posix", reason="native POSIX process signal")
def test_bootstrap_reports_a_native_signal_as_an_unknown_hook_outcome(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other = linked_workspace(tmp_path)
    (other / "Makefile").write_text("init:\n\t@sleep 5\n", encoding="utf-8")
    native_popen = subprocess.Popen
    calls = 0

    def popen(argv, *args, **kwargs):
        nonlocal calls
        process = native_popen(argv, *args, **kwargs)
        if argv[0] == "make":
            calls += 1
            os.killpg(process.pid, signal.SIGTERM)
        return process

    monkeypatch.setattr(subprocess, "Popen", popen)
    assert main(["--project", str(root), "worktree", "bootstrap", str(other), "--yes", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert calls == 1 and result["data"]["result"]["observed"]["returncode"] == -signal.SIGTERM
    assert result["data"]["result"]["observed"]["timed_out"] is False
    assert result["effects"] == [{"kind": "worktree-bootstrap", "status": "unknown", "target": str(other)}]


@pytest.mark.skipif(os.name != "posix", reason="native POSIX Start exclusion in another process")
def test_bootstrap_runs_while_start_exclusion_is_held(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root, other = linked_workspace(tmp_path)
    (other / "Makefile").write_text("init:\n\t@touch bootstrap-ran\n", encoding="utf-8")
    holder = subprocess.Popen(
        [
            sys.executable,
            "-c",
            "import fcntl,os,sys; fd=os.open(sys.argv[1],os.O_RDONLY); "
            "fcntl.flock(fd,fcntl.LOCK_EX); print('ready',flush=True); sys.stdin.readline(); os.close(fd)",
            str(root / ".git"),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        assert holder.stdout is not None and holder.stdout.readline() == "ready\n"
        assert main(["--project", str(root), "worktree", "bootstrap", str(other), "--yes", "--json"]) == 0
        assert json.loads(capsys.readouterr().out)["status"] == "succeeded" and (other / "bootstrap-ran").exists()
    finally:
        holder.communicate("\n", timeout=10)
    assert holder.returncode == 0


@pytest.mark.skipif(os.name != "posix", reason="native POSIX termination response failure")
def test_bootstrap_keeps_a_started_hook_unknown_when_process_termination_reports_io_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other = linked_workspace(tmp_path)
    (other / "Makefile").write_text("init:\n\t@touch before-timeout\n\t@sleep 5\n", encoding="utf-8")
    native_killpg = os.killpg
    calls = 0

    def killpg(pid: int, sig: int) -> None:
        nonlocal calls
        calls += 1
        native_killpg(pid, sig)
        raise OSError(errno.EIO, "fixture failure after process-group termination")

    monkeypatch.setattr(os, "killpg", killpg)
    # The CLI timeout also bounds native Git preflight. Allow process startup
    # while keeping this deadline below the hook's five-second sleep.
    assert (
        main(["--project", str(root), "worktree", "bootstrap", str(other), "--yes", "--timeout", "2.0", "--json"]) == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert calls == 1 and (other / "before-timeout").exists()
    assert result["data"]["result"]["observed"]["started"] is True
    assert result["data"]["result"]["observed"]["timed_out"] is True
    assert result["effects"] == [{"kind": "worktree-bootstrap", "status": "unknown", "target": str(other)}]


def test_successful_bootstrap_omits_large_and_secret_hook_output_from_both_streams(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other = linked_workspace(tmp_path)
    script = (
        'import sys; print("hook-secret-413"); print("x" * 100000); '
        'print("error-secret-413", file=sys.stderr); print("e" * 100000, file=sys.stderr)'
    )
    makefile = other / "Makefile"
    makefile.write_text(
        f"init:\n\t@{shlex.quote(sys.executable)} -c {shlex.quote(script)}\n\t@printf 'one run\\n' > bootstrap-ran\n",
        encoding="utf-8",
    )
    exact_makefile = makefile.read_bytes()
    assert main(["--project", str(root), "worktree", "bootstrap", str(other), "--yes", "--json"]) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["status"] == "succeeded" and result["data"]["result"]["observed"]["returncode"] == 0
    assert result["data"]["result"]["observed"]["diagnostic"] == "make init finished; output omitted"
    assert "hook-secret-413" not in output.out + output.err and "error-secret-413" not in output.out + output.err
    assert len(output.out + output.err) < 5000 and not output.err
    assert (other / "bootstrap-ran").read_bytes() == b"one run\n" and makefile.read_bytes() == exact_makefile
    assert not (root / "bootstrap-ran").exists() and not (root / ".git/spec-dock").exists()


@pytest.mark.parametrize("exists", [False, True])
def test_bootstrap_rejects_a_missing_or_non_native_target_without_running_a_hook(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], exists: bool
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root, other = linked_workspace(tmp_path)
    target = tmp_path / "not-a-worktree"
    if exists:
        target.mkdir()
        (target / "Makefile").write_text("init:\n\t@touch trap-ran\n", encoding="utf-8")
    before = tree_digest(tmp_path)
    assert main(["--project", str(root), "worktree", "bootstrap", str(target), "--yes", "--json"]) == 4
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["status"] == "failed" and result["effects"] == [] and not output.err
    assert tree_digest(tmp_path) == before
    assert not (target / "trap-ran").exists() and not (other / "bootstrap-ran").exists()
    assert not (root / ".git/spec-dock").exists()
