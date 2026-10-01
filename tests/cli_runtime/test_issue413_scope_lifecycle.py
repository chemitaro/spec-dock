"""Scope close/reopen leave direct selection and Git checkout unchanged."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from spec_dock.cli import main
from tests.cli_runtime.test_issue413_active import select_fixture
from tests.cli_runtime.test_issue413_finish import github_fixture
from tests.cli_runtime.test_issue413_work_start import committed_workspace


@pytest.mark.parametrize("action,state", [("close", "open"), ("reopen", "completed")])
def test_lifecycle_dry_run_exposes_a_valid_plan_without_mutating_authority_or_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], action: str, state: str
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    before = record.read_bytes()
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    before_metadata = metadata.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": state})
    assert main(["--project", str(root), "scope", action, "@current", "--dry-run", "--json"]) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["status"] == "planned" and output.err == ""
    assert result["data"]["result"]["can_apply"] is True
    assert result["data"]["result"]["blockers"] == []
    assert result["data"]["result"]["changed"] is False
    assert result["data"]["result"]["scope"]["status"]["state"] == state
    assert result["effects"] == [{"kind": f"github.issue.{action}", "status": "planned", "target": "gh:example/repo#1"}]
    assert [json.loads(line)["method"] for line in log.read_text().splitlines()] == ["GET"]
    assert record.read_bytes() == before and metadata.read_bytes() == before_metadata
    assert not (root / "spec-dock/.agent/staging").exists() and not (root / ".git/spec-dock").exists()


def test_scope_close_confirms_completed_without_releasing_the_direct_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    before_record = record.read_bytes()
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    before_metadata = metadata.read_bytes()
    before_head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"])
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    assert main(["--project", str(root), "scope", "close", "@current", "--yes", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "succeeded"
    assert result["data"]["result"]["scope"]["status"]["state"] == "completed"
    assert result["data"]["result"]["changed"] is True
    assert result["effects"] == [{"kind": "github.issue.close", "status": "succeeded", "target": "gh:example/repo#1"}]
    requests = [json.loads(line) for line in log.read_text().splitlines()]
    assert [request["method"] for request in requests] == ["GET", "GET", "PATCH", "GET"]
    assert requests[2]["body"] == {"state": "closed", "state_reason": "completed"}
    assert record.read_bytes() == before_record and metadata.read_bytes() == before_metadata
    assert subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"]) == before_head
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"main\n"
    assert not (root / ".git/spec-dock").exists()


def test_completed_parent_close_still_checks_unfinished_descendants(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from tests.cli_runtime.test_issue413_contract import add_scope

    root = committed_workspace(tmp_path / "consumer")
    add_scope(root, "epic-00002", "epic", "init-00001", root / "spec-dock/initiatives/init-00001-fixture")
    record = select_fixture(root)
    before = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "completed", "2": "open"})
    assert main(["--project", str(root), "scope", "close", "@current", "--yes", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and "DESCENDANT_NOT_COMPLETED" in result["error"]["message"]
    assert record.read_bytes() == before
    assert [(row["method"], row["number"]) for row in map(json.loads, log.read_text().splitlines())] == [
        ("GET", 1),
        ("GET", 2),
    ]


def test_reopen_even_an_open_child_requires_open_ancestors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from tests.cli_runtime.test_issue413_contract import add_scope

    root = committed_workspace(tmp_path / "consumer")
    add_scope(root, "epic-00002", "epic", "init-00001", root / "spec-dock/initiatives/init-00001-fixture")
    record = select_fixture(root, scope_id="epic-00002", number=2)
    before = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "completed", "2": "open"})
    assert main(["--project", str(root), "scope", "reopen", "@current", "--yes", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert "ANCESTOR_TERMINAL" in result["error"]["message"] and result["effects"] == []
    assert [(row["method"], row["number"]) for row in map(json.loads, log.read_text().splitlines())] == [
        ("GET", 2),
        ("GET", 1),
    ]
    assert record.read_bytes() == before


def test_local_close_retains_confirmed_effect_after_descriptor_cleanup_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    path = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    data = json.loads(path.read_bytes())
    data.update(
        backend="local", github=None, lifecycle={"state": "open", "revision": 0, "updated_at": "2026-09-29T00:00:00Z"}
    )
    path.write_text(json.dumps(data))
    record = select_fixture(root)
    before = record.read_bytes()
    old_identity = (path.stat().st_dev, path.stat().st_ino)
    original_close = os.close
    failed = False

    def close(descriptor: int) -> None:
        nonlocal failed
        observed = os.fstat(descriptor)
        current = path.stat()
        identity = (observed.st_dev, observed.st_ino)
        should_fail = not failed and identity == (current.st_dev, current.st_ino) and identity != old_identity
        original_close(descriptor)
        if should_fail:
            failed = True
            raise OSError("fixture: cleanup after confirmed metadata replacement")

    monkeypatch.setattr(os, "close", close)
    assert main(["--project", str(root), "scope", "close", "init-00001", "--yes", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert failed and result["status"] == "partial" and result["data"]["result"]["changed"] is True
    assert result["data"]["result"]["scope"]["status"]["state"] == "completed"
    assert result["effects"] == [{"kind": "scope.lifecycle", "status": "succeeded", "target": "init-00001"}]
    assert json.loads(path.read_bytes())["lifecycle"]["state"] == "completed"
    assert record.read_bytes() == before


@pytest.mark.skipif(os.name != "posix", reason="native POSIX terminal fixture")
@pytest.mark.parametrize("answer", [b"yes\n", b"no\n"])
def test_scope_close_accepts_a_terminal_confirmation_after_planning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, answer: bytes
) -> None:
    import pty

    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    before = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    master, slave = pty.openpty()
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "spec_dock.cli", "--project", str(root), "scope", "close", "@current"],
            stdin=slave,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[2] / "src")),
        )
        os.write(master, answer)
        stdout, stderr = process.communicate(timeout=8)
    finally:
        os.close(master)
        os.close(slave)
    assert b"Confirm" in stderr and b"init-00001" in stderr, stdout + stderr
    assert process.returncode == (0 if answer == b"yes\n" else 3), stdout + stderr
    requests = [json.loads(line) for line in log.read_text().splitlines()]
    assert sum(row["method"] == "PATCH" for row in requests) == (1 if answer == b"yes\n" else 0)
    assert record.read_bytes() == before


@pytest.mark.skipif(os.name != "posix", reason="native POSIX confirmation and parallel Start processes")
@pytest.mark.parametrize("action,state", [("close", "open"), ("reopen", "completed")])
@pytest.mark.parametrize("guard", [[], ["--expect-current", "init-00001"]])
def test_scope_lifecycle_refuses_a_changed_direct_selection_after_terminal_confirmation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, action: str, state: str, guard: list[str]
) -> None:
    import pty
    import select
    import time

    root = committed_workspace(tmp_path / "consumer")
    source = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    payload = json.loads(source.read_bytes())
    other = source.parent.parent / "init-00002-fixture"
    other.mkdir()
    (other / ".meta.json").write_text(
        json.dumps(dict(payload, id="init-00002", github=dict(payload["github"], issue_number=2)))
    )
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
            "other scope",
        ],
        check=True,
        capture_output=True,
    )
    selected = select_fixture(root)
    metadata_before = {path: path.read_bytes() for path in (root / "spec-dock").rglob(".meta.json")}
    log = github_fixture(tmp_path, monkeypatch, {"1": state, "2": "open"})
    master, slave = pty.openpty()
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "spec_dock.cli",
            "--project",
            str(root),
            "scope",
            action,
            "@current",
            *guard,
        ],
        stdin=slave,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        assert process.stderr is not None
        prompt = bytearray()
        deadline = time.monotonic() + 10
        while b"Confirm [yes/no]" not in prompt and time.monotonic() < deadline:
            ready, _, _ = select.select([process.stderr], [], [], 0.2)
            if ready:
                prompt.extend(os.read(process.stderr.fileno(), 4096))
        assert b"Confirm [yes/no]" in prompt and b"init-00001" in prompt, prompt
        started = subprocess.run(
            [
                sys.executable,
                "-m",
                "spec_dock.cli",
                "--project",
                str(root),
                "work",
                "start",
                "init-00002",
                "--branch",
                "main",
                "--switch-active",
                "--json",
            ],
            capture_output=True,
            timeout=10,
        )
        assert started.returncode == 0, started.stdout + started.stderr
        new_token = json.loads(started.stdout)["data"]["selection_token"]
        new_record = selected.parent / f"target-{new_token}.json"
        before = new_record.read_bytes()
        os.write(master, b"yes\n")
        stdout, stderr = process.communicate(timeout=10)
        assert process.returncode == 3, stdout + stderr
        assert b"selection changed" in stderr
        assert new_record.read_bytes() == before and not selected.exists()
        assert all(path.read_bytes() == exact for path, exact in metadata_before.items())
        assert not any(json.loads(line)["method"] == "PATCH" for line in log.read_text().splitlines())
        assert json.loads((tmp_path / "remote-states.json").read_bytes()) == {"1": state, "2": "open"}
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=10)
        os.close(master)
        os.close(slave)


def test_not_planned_close_lists_children_and_never_closes_them(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from tests.cli_runtime.test_issue413_contract import add_scope

    root = committed_workspace(tmp_path / "consumer")
    add_scope(root, "epic-00002", "epic", "init-00001", root / "spec-dock/initiatives/init-00001-fixture")
    log = github_fixture(tmp_path, monkeypatch, {"1": "open", "2": "open"})
    executable = tmp_path / "gh-bin/gh"
    executable.write_text(
        executable
        .read_text()
        .replace(
            "assert body=={'state':'closed','state_reason':'completed'}",
            "assert body=={'state':'closed','state_reason':'not_planned'}",
        )
        .replace("states[str(number)]='completed'", "states[str(number)]='not-planned'")
    )
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "close",
            "init-00001",
            "--reason",
            "not-planned",
            "--yes",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["scope"]["status"]["state"] == "not-planned"
    assert result["data"]["result"]["descendants"] == ["epic-00002"]
    requests = [json.loads(line) for line in log.read_text().splitlines()]
    assert [(row["number"], row["body"]) for row in requests if row["method"] == "PATCH"] == [
        (1, {"state": "closed", "state_reason": "not_planned"})
    ]
    assert json.loads((tmp_path / "remote-states.json").read_bytes()) == {"1": "not-planned", "2": "open"}


def test_scope_reopen_uses_one_confirmed_patch_and_keeps_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    before = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "not-planned"})
    executable = tmp_path / "gh-bin/gh"
    executable.write_text(
        executable
        .read_text()
        .replace(
            "assert body=={'state':'closed','state_reason':'completed'}",
            "assert body=={'state':'open','state_reason':'reopened'}",
        )
        .replace("states[str(number)]='completed'", "states[str(number)]='open'")
    )
    assert main(["--project", str(root), "scope", "reopen", "@current", "--yes", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["scope"]["status"]["state"] == "open"
    assert result["data"]["result"]["changed"] is True
    assert result["effects"] == [{"kind": "github.issue.reopen", "status": "succeeded", "target": "gh:example/repo#1"}]
    requests = [json.loads(line) for line in log.read_text().splitlines()]
    assert [row["method"] for row in requests] == ["GET", "GET", "PATCH", "GET"]
    assert record.read_bytes() == before


def test_existing_local_scope_close_preserves_unknown_metadata_and_selection_offline(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    payload = json.loads(metadata.read_bytes())
    payload.update(
        backend="local",
        github=None,
        revision=4,
        lifecycle={"state": "open", "revision": 6, "updated_at": "2026-09-29T00:00:00Z", "extra": {"preserve": [1, 2]}},
        extra={"nested": {"preserve": ["日本語", 42]}},
    )
    metadata.write_text(json.dumps(payload))
    record = select_fixture(root)
    before = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    assert main(["--project", str(root), "scope", "close", "init-00001", "--offline", "--yes", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    after = json.loads(metadata.read_bytes())
    assert after["id"] == "init-00001" and after["backend"] == "local" and after["github"] is None
    assert after["revision"] == 5 and after["lifecycle"]["revision"] == 7 and after["lifecycle"]["state"] == "completed"
    assert after["extra"] == payload["extra"] and after["lifecycle"]["extra"] == payload["lifecycle"]["extra"]
    assert result["data"]["result"]["scope"]["status"]["source"] == "local"
    assert result["effects"] == [{"kind": "scope.lifecycle", "status": "succeeded", "target": "init-00001"}]
    assert record.read_bytes() == before and not log.exists() and not (root / ".git/spec-dock").exists()


def test_unconfirmed_close_reports_unknown_and_never_repeats_a_patch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    before = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    executable = tmp_path / "gh-bin/gh"
    original = executable.read_text()
    original = original.replace(
        "state=states[str(number)]\n",
        "state=states[str(number)]\nif state=='completed':\n print('HTTP/2.0 503 Unavailable\\n\\n{}'); sys.exit(1)\n",
    )
    executable.write_text(original)
    assert main(["--project", str(root), "scope", "close", "@current", "--yes", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "partial" and result["error"]["code"] == "GITHUB_EFFECT_UNKNOWN"
    assert result["effects"] == [{"kind": "github.issue.close", "status": "unknown", "target": "gh:example/repo#1"}]
    assert result["data"]["result"]["scope"]["status"] == {
        "state": "unknown",
        "authority": "github",
        "source": "unknown",
        "observed_at": None,
    }
    assert result["recovery"]["can_resume"] is False and result["recovery"]["can_rollback"] is False
    assert [row["method"] for row in map(json.loads, log.read_text().splitlines())] == ["GET", "GET", "PATCH", "GET"]
    assert record.read_bytes() == before


@pytest.mark.parametrize("action", ["close", "reopen"])
def test_lifecycle_help_has_v2_results_without_journal_recovery(
    capsys: pytest.CaptureFixture[str], action: str
) -> None:
    assert main(["help", "scope", action]) == 0
    output = capsys.readouterr().out
    assert "specdock.cli/v2" in output
    assert "--resume" not in output and "--rollback" not in output and "journal" not in output


@pytest.mark.parametrize("action", ["close", "reopen"])
def test_lifecycle_resume_is_retired_before_context(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], action: str
) -> None:
    assert (
        main([
            "--project",
            str(tmp_path / "missing"),
            "scope",
            action,
            "init-00001",
            "--resume",
            "old-operation",
            "--json",
        ])
        == 2
    )
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED" and result["effects"] == []
    assert list(tmp_path.iterdir()) == []
