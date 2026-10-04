"""The public parser reaches direct work and active behavior without control."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING

from spec_dock.cli import main
from tests.cli_runtime.test_issue413_finish import github_fixture
from tests.cli_runtime.test_work_commands_vnext import three_kind_workspace

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_public_work_lifecycle_resolves_current_selector_and_returns_v2_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = three_kind_workspace(tmp_path / "consumer")
    github_fixture(tmp_path, monkeypatch, {"1": "open", "2": "open", "3": "open"})
    arguments = ["--project", str(root)]
    assert main([*arguments, "work", "start", "iss-00003", "--base", "HEAD", "--json"]) == 0
    output = capsys.readouterr()
    started = json.loads(output.out)
    assert not output.err and started["schema_version"] == "specdock.cli/v2" and started["command"] == "work start"
    token = started["data"]["selection_token"]
    assert main([*arguments, "work", "finish", "@current", "--expect-current", "iss-00003", "--yes", "--json"]) == 0
    output = capsys.readouterr()
    finished = json.loads(output.out)
    assert not output.err and finished["schema_version"] == "specdock.cli/v2" and finished["command"] == "work finish"
    assert finished["data"]["scope_id"] == "iss-00003" and finished["data"]["completed"] is True
    assert finished["data"]["selection_token"] is None
    assert not (root / "spec-dock/.agent/work-target" / f"target-{token}.json").exists()


def test_public_cli_rejects_own_old_writer_before_work_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = three_kind_workspace(tmp_path / "consumer")
    log = github_fixture(tmp_path, monkeypatch, {"1": "open", "2": "open", "3": "open"})
    declaration = root / "spec-dock/workspace.json"
    declaration.write_text('{"schema_version":3,"writer_protocol":"specdock.writer/v1"}\n')
    before = {path: path.read_bytes() for path in (root / "spec-dock").rglob(".meta.json")}
    assert main(["--project", str(root), "work", "finish", "iss-00003", "--yes", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "PRECONDITION_FAILED" and result["effects"] == []
    assert all(path.read_bytes() == value for path, value in before.items())
    assert not log.exists() and not (root / ".git/spec-dock").exists()


def test_public_cli_requires_base_for_new_work_branch(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = three_kind_workspace(tmp_path / "consumer")
    before = subprocess.check_output(["git", "-C", str(root), "show-ref"])
    assert main(["--project", str(root), "work", "start", "iss-00003", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert "requires --base" in result["error"]["message"] and result["effects"] == []
    assert subprocess.check_output(["git", "-C", str(root), "show-ref"]) == before
    assert not (root / "spec-dock/.agent").exists()


def test_public_active_show_same_set_and_ancestor_clear_do_not_promote_a_parent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = three_kind_workspace(tmp_path / "consumer")
    log = github_fixture(tmp_path, monkeypatch, {"1": "open", "2": "open", "3": "open"})
    arguments = ["--project", str(root)]
    assert main([*arguments, "active", "set", "iss-00003", "--dry-run", "--json"]) == 3
    rejected = json.loads(capsys.readouterr().out)
    assert rejected["error"]["code"] == "WORK_START_REQUIRED" and rejected["effects"] == []
    assert not log.exists() and not (root / "spec-dock/.agent").exists()
    assert main([*arguments, "work", "start", "iss-00003", "--base", "HEAD", "--json"]) == 0
    started = json.loads(capsys.readouterr().out)
    record = root / "spec-dock/.agent/work-target" / f"target-{started['data']['selection_token']}.json"
    before = record.read_bytes()
    for operation in (["show"], ["set", "@current"]):
        assert main([*arguments, "active", *operation, "--json"]) == 0
        result = json.loads(capsys.readouterr().out)
        assert result["data"]["selection"]["scope_id"] == "iss-00003" and result["effects"] == []
        assert record.read_bytes() == before
    calls = log.read_bytes()
    assert main([*arguments, "active", "clear", "--from", "epic-00002", "--dry-run", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "planned" and record.read_bytes() == before
    assert main([*arguments, "active", "clear", "--from", "epic-00002", "--json"]) == 0
    cleared = json.loads(capsys.readouterr().out)
    assert cleared["data"]["selection"]["status"] == "empty" and not record.exists()
    assert main([*arguments, "active", "clear", "--all", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "unchanged"
    assert log.read_bytes() == calls
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"iss-00003-fixture\n"
    assert json.loads((tmp_path / "remote-states.json").read_bytes()) == {"1": "open", "2": "open", "3": "open"}
    assert not (root / ".git/spec-dock").exists()
