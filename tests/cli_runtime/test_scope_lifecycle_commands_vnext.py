"""Public Scope close/reopen preserve existing data and direct selection."""

from __future__ import annotations

import io
import json
import subprocess
import sys
from typing import TYPE_CHECKING

from spec_dock.cli import main
from tests.cli_runtime.test_issue413_active import select_fixture
from tests.cli_runtime.test_issue413_finish import github_fixture
from tests.cli_runtime.test_issue413_work_start import committed_workspace
from tests.cli_runtime.test_work_commands_vnext import three_kind_workspace

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


class TerminalAnswer(io.StringIO):
    def isatty(self) -> bool:
        return True


def existing_local_workspace(root: Path) -> tuple[Path, Path]:
    committed_workspace(root)
    path = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    payload = json.loads(path.read_bytes())
    payload.update(
        backend="local",
        github=None,
        lifecycle={"state": "open", "revision": 0, "updated_at": "2026-09-30T00:00:00Z"},
    )
    path.write_text(json.dumps(payload))
    return root, path


def test_scope_close_prompts_and_respects_denial_for_existing_local_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, metadata = existing_local_workspace(tmp_path / "consumer")
    before = metadata.read_bytes()
    for answer, expected in (("no\n", 3), ("yes\n", 0)):
        monkeypatch.setattr(sys, "stdin", TerminalAnswer(answer))
        assert main(["--project", str(root), "scope", "close", "init-00001"]) == expected
        output = capsys.readouterr()
        assert "init-00001" in output.err and "Confirm [yes/no]" in output.err
        if expected == 3:
            assert metadata.read_bytes() == before
    assert json.loads(metadata.read_bytes())["lifecycle"]["state"] == "completed"
    assert not (root / ".git/spec-dock").exists()


def test_scope_close_current_prompts_without_a_noninteractive_guard_and_respects_denial(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    before = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    monkeypatch.setattr(sys, "stdin", TerminalAnswer("no\n"))
    assert main(["--project", str(root), "scope", "close", "@current"]) == 3
    output = capsys.readouterr()
    assert "Target: init-00001" in output.err and "Confirm [yes/no]" in output.err
    assert record.read_bytes() == before
    assert all(json.loads(line)["method"] == "GET" for line in log.read_text().splitlines())
    assert json.loads((tmp_path / "remote-states.json").read_bytes()) == {"1": "open"}


def test_scope_close_current_json_returns_the_resolved_scope_without_clearing_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    before = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "close",
            "@current",
            "--expect-current",
            "init-00001",
            "--yes",
            "--json",
        ])
        == 0
    )
    output = capsys.readouterr()
    payload = json.loads(output.out)
    assert payload["schema_version"] == "specdock.cli/v2" and not output.err
    scope = payload["data"]["result"]["scope"]
    assert scope["id"] == "init-00001" and scope["status"]["state"] == "completed"
    assert scope["status"]["source"] == "github" and scope["status"]["authority"] == "github"
    assert payload["data"]["result"]["changed"] is True
    assert payload["effects"] == [{"kind": "github.issue.close", "status": "succeeded", "target": "gh:example/repo#1"}]
    assert [
        (row["number"], row["body"])
        for row in map(json.loads, log.read_text().splitlines())
        if row["method"] == "PATCH"
    ] == [(1, {"state": "closed", "state_reason": "completed"})]
    assert record.read_bytes() == before


def test_scope_close_reopen_previews_and_updates_only_existing_local_lifecycle(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, metadata = existing_local_workspace(tmp_path / "consumer")
    before = metadata.read_bytes()
    head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"])
    prefix = ["--project", str(root), "scope"]
    assert main([*prefix, "close", "init-00001", "--dry-run", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "planned" and metadata.read_bytes() == before
    for action, state in (("close", "completed"), ("reopen", "open")):
        before = metadata.read_bytes()
        assert main([*prefix, action, "init-00001", "--json"]) == 3
        assert json.loads(capsys.readouterr().out)["effects"] == [] and metadata.read_bytes() == before
        assert main([*prefix, action, "init-00001", "--yes", "--json"]) == 0
        payload = json.loads(capsys.readouterr().out)
        scope = payload["data"]["result"]["scope"]
        assert scope["id"] == "init-00001" and scope["status"]["state"] == state
        assert scope["status"]["source"] == "local" and scope["status"]["authority"] == "local"
        assert payload["effects"] == [{"kind": "scope.lifecycle", "status": "succeeded", "target": "init-00001"}]
        assert json.loads(metadata.read_bytes())["lifecycle"]["state"] == state
    assert main([*prefix, "close", "init-00001", "--reason", "not-planned", "--yes", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["data"]["result"]["scope"]["status"]["state"] == "not-planned"
    assert json.loads(metadata.read_bytes())["lifecycle"]["state"] == "not-planned"
    assert subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"]) == head
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"main\n"
    assert not (root / ".git/spec-dock").exists()


def test_scope_mutation_checks_expected_current_and_backend_before_edit(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = three_kind_workspace(tmp_path / "consumer")
    record = select_fixture(root, scope_id="iss-00003", number=3)
    metadata = (
        root / "spec-dock/initiatives/init-00001-fixture/epics/epic-00002-fixture/issues/iss-00003-fixture/.meta.json"
    )
    before = metadata.read_bytes(), record.read_bytes()
    prefix = ["--project", str(root), "scope", "edit", "@current", "--title", "New", "--json"]
    for guard in (["--expect-current", "init-00001"], ["--expect-backend", "local"]):
        assert main([*prefix, *guard]) == 3
        result = json.loads(capsys.readouterr().out)
        assert result["error"]["code"] == "PRECONDITION_FAILED" and result["effects"] == []
        assert (metadata.read_bytes(), record.read_bytes()) == before
    assert main([*prefix, "--expect-current", "iss-00003", "--expect-backend", "github"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["scope"]["id"] == "iss-00003"
    assert json.loads(metadata.read_bytes())["title"] == "New" and record.read_bytes() == before[1]
