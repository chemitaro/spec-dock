"""Scope close and reopen are independent from active selection."""

from __future__ import annotations

import json
import os
from pathlib import Path
import pty
import select
import subprocess
import sys
import time
from typing import cast

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.create_local_scope import create_local_scope  # noqa: E402
from spec_dock_runtime.cli.vnext_runtime import run_vnext  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import _ready_repo  # noqa: E402


def _run(repo: Path, *args: str):
    return run_vnext([*args, "--json"], invocation_cwd=repo, engine_digest="engine-a", engine_version="0.2.4")


def test_scope_close_prompts_on_tty_and_respects_denial(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    created = create_local_scope(kind="initiative", title="Plan", parent=None, ancestors=(), **common)
    source = (
        "from pathlib import Path; import sys; "
        "sys.path.insert(0, sys.argv[1]); "
        "from spec_dock_runtime.cli.vnext_runtime import run_vnext; "
        "result=run_vnext(['scope','close',sys.argv[2]], invocation_cwd=Path(sys.argv[3]), "
        "engine_digest='engine-a', engine_version='0.2.4'); "
        "sys.stdout.write(result.stdout); sys.stderr.write(result.stderr); sys.exit(result.exit_code)"
    )
    for answer, expected_code in ((b"no\n", 3), (b"yes\n", 0)):
        master, slave = pty.openpty()
        try:
            child = subprocess.Popen(
                [sys.executable, "-c", source, str(RUNTIME_SCRIPTS), created.id, str(repo)],
                stdin=slave,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            os.close(slave)
            os.write(master, answer)
            stdout, stderr = child.communicate(timeout=10)
            assert child.returncode == expected_code, stdout + stderr
            assert created.id in stderr and "Confirm" in stderr
        finally:
            os.close(master)
    assert json.loads((created.path / ".meta.json").read_text())["lifecycle"]["state"] == "completed"


def test_scope_close_current_prompts_on_tty_without_noninteractive_guard(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    created = create_local_scope(kind="initiative", title="Plan", parent=None, ancestors=(), **common)
    selected = _run(repo, "active", "set", created.id)
    assert selected.exit_code == 0
    metadata = created.path / ".meta.json"
    before = metadata.read_bytes()
    source = (
        "from pathlib import Path; import sys; "
        "sys.path.insert(0, sys.argv[1]); "
        "from spec_dock_runtime.cli.vnext_runtime import run_vnext; "
        "result=run_vnext(['scope','close','@current'], invocation_cwd=Path(sys.argv[2]), "
        "engine_digest='engine-a', engine_version='0.2.4'); "
        "sys.stdout.write(result.stdout); sys.stderr.write(result.stderr); sys.exit(result.exit_code)"
    )
    master, slave = pty.openpty()
    try:
        child = subprocess.Popen(
            [sys.executable, "-c", source, str(RUNTIME_SCRIPTS), str(repo)],
            stdin=slave,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        os.close(slave)
        os.write(master, b"no\n")
        stdout, stderr = child.communicate(timeout=10)
        assert child.returncode == 3, stdout + stderr
        assert f"Target: {created.id}" in stderr
        assert "Confirm [yes/no]" in stderr
        assert metadata.read_bytes() == before
    finally:
        os.close(master)


def test_scope_close_current_json_preserves_requested_selector(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    created = create_local_scope(kind="initiative", title="Plan", parent=None, ancestors=(), **common)
    assert _run(repo, "active", "set", created.id).exit_code == 0
    closed = _run(repo, "scope", "close", "@current", "--expect-current", created.id, "--yes")
    payload = json.loads(closed.stdout)
    assert closed.exit_code == 0
    assert payload["target"]["requested"] == "@current"
    assert payload["target"]["id"] == payload["data"]["scope"]["id"] == created.id


def test_scope_close_current_rejects_selection_change_during_prompt(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    first = create_local_scope(kind="initiative", title="First", parent=None, ancestors=(), **common)
    second = create_local_scope(kind="initiative", title="Second", parent=None, ancestors=(), **common)
    assert _run(repo, "active", "set", first.id).exit_code == 0
    first_meta = first.path / ".meta.json"
    before = first_meta.read_bytes()
    source = (
        "from pathlib import Path; import sys; "
        "sys.path.insert(0, sys.argv[1]); "
        "from spec_dock_runtime.cli.vnext_runtime import run_vnext; "
        "result=run_vnext(['scope','close','@current'], invocation_cwd=Path(sys.argv[2]), "
        "engine_digest='engine-a', engine_version='0.2.4'); "
        "sys.stdout.write(result.stdout); sys.stderr.write(result.stderr); sys.exit(result.exit_code)"
    )
    master, slave = pty.openpty()
    child = subprocess.Popen(
        [sys.executable, "-c", source, str(RUNTIME_SCRIPTS), str(repo)],
        stdin=slave,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    os.close(slave)
    try:
        assert child.stderr is not None
        prompt = bytearray()
        deadline = time.monotonic() + 10
        while b"Confirm [yes/no]" not in prompt and time.monotonic() < deadline:
            ready, _, _ = select.select([child.stderr], [], [], 0.2)
            if ready:
                prompt.extend(os.read(child.stderr.fileno(), 4096))
        assert b"Confirm [yes/no]" in prompt, prompt.decode(errors="replace")
        assert first.id.encode() in prompt
        assert _run(repo, "active", "set", second.id).exit_code == 0
        os.write(master, b"yes\n")
        stdout, stderr = child.communicate(timeout=10)
        assert child.returncode == 3, (stdout + stderr).decode(errors="replace")
        assert b"STATE_CONFLICT" in stderr
        assert first_meta.read_bytes() == before
    finally:
        if child.poll() is None:
            child.kill()
            child.wait(timeout=10)
        os.close(master)


def test_scope_close_reopen_cli_previews_and_updates_local_lifecycle(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    created = create_local_scope(kind="initiative", title="Plan", parent=None, ancestors=(), **common)
    metadata = created.path / ".meta.json"
    before = metadata.read_bytes()
    planned = _run(repo, "scope", "close", created.id, "--dry-run")
    assert planned.exit_code == 0
    assert json.loads(planned.stdout)["status"] == "planned"
    assert metadata.read_bytes() == before
    unconfirmed = _run(repo, "scope", "close", created.id)
    assert unconfirmed.exit_code == 3
    assert metadata.read_bytes() == before
    closed = _run(repo, "scope", "close", created.id, "--yes")
    assert closed.exit_code == 0
    assert json.loads(closed.stdout)["target"]["id"] == created.id
    assert json.loads(metadata.read_text())["lifecycle"]["state"] == "completed"
    operation_id = json.loads(closed.stdout)["operation_id"]
    wrong_action = _run(repo, "scope", "reopen", created.id, "--resume", operation_id, "--yes")
    assert wrong_action.exit_code == 3
    resumed = _run(repo, "scope", "close", created.id, "--resume", operation_id, "--yes")
    assert resumed.exit_code == 0
    unconfirmed_reopen = _run(repo, "scope", "reopen", created.id)
    assert unconfirmed_reopen.exit_code == 3
    assert json.loads(metadata.read_text())["lifecycle"]["state"] == "completed"
    reopened = _run(repo, "scope", "reopen", created.id, "--yes")
    assert reopened.exit_code == 0
    assert json.loads(metadata.read_text())["lifecycle"]["state"] == "open"
    abandoned = _run(repo, "scope", "close", created.id, "--reason", "not-planned", "--yes")
    assert abandoned.exit_code == 0
    abandoned_id = json.loads(abandoned.stdout)["operation_id"]
    implicit_completed = _run(repo, "scope", "close", created.id, "--resume", abandoned_id, "--yes")
    assert implicit_completed.exit_code == 3
    resumed_abandoned = _run(
        repo, "scope", "close", created.id, "--reason", "not-planned", "--resume", abandoned_id, "--yes"
    )
    assert resumed_abandoned.exit_code == 0


def test_scope_close_json_reports_completed_scope_and_same_snapshot(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    created = create_local_scope(kind="initiative", title="Plan", parent=None, ancestors=(), **common)
    closed = _run(repo, "scope", "close", created.id, "--yes")
    assert closed.exit_code == 0
    payload = json.loads(closed.stdout)
    assert payload["target"]["id"] == payload["data"]["scope"]["id"] == created.id
    assert payload["data"]["status"] == {"state": "completed", "source": "local", "stale": False}
    assert payload["target"]["snapshot_id"] == payload["data"]["snapshot_id"]
    assert payload["data"]["project"] == str(repo)
    assert payload["data"]["worktree"] == common["worktree_id"]


def test_scope_mutation_checks_expected_current_and_backend_before_edit(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    created = create_local_scope(kind="initiative", title="Plan", parent=None, ancestors=(), **common)
    metadata = created.path / ".meta.json"
    selected = _run(repo, "active", "set", created.id)
    assert selected.exit_code == 0
    before = metadata.read_bytes()

    missing = _run(repo, "scope", "edit", "@current", "--title", "New")
    assert missing.exit_code == 3
    assert metadata.read_bytes() == before
    mismatched = _run(repo, "scope", "edit", "@current", "--title", "New", "--expect-current", "init-local-99999")
    assert mismatched.exit_code == 3
    assert json.loads(mismatched.stdout)["error"]["code"] == "STATE_CONFLICT"
    assert metadata.read_bytes() == before
    wrong_backend = _run(repo, "scope", "edit", created.id, "--title", "New", "--expect-backend", "github")
    assert wrong_backend.exit_code == 3
    assert json.loads(wrong_backend.stdout)["error"]["code"] == "STATE_CONFLICT"
    assert metadata.read_bytes() == before

    changed = _run(
        repo,
        "scope",
        "edit",
        "@current",
        "--title",
        "New",
        "--expect-current",
        created.id,
        "--expect-backend",
        "local",
    )
    assert changed.exit_code == 0
    assert json.loads(metadata.read_text())["title"] == "New"
