"""Public work leaves keep one direct target and finish it through GitHub."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from tests.cli_runtime.test_issue413_contract import add_scope, make_workspace
from tests.cli_runtime.test_issue413_finish import github_fixture

if TYPE_CHECKING:
    from pathlib import Path


def three_kind_workspace(root: Path) -> Path:
    make_workspace(root)
    initiative = root / "spec-dock/initiatives/init-00001-fixture"
    epic = add_scope(root, "epic-00002", "epic", "init-00001", initiative)
    add_scope(root, "iss-00003", "issue", "epic-00002", epic)
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
            "fixture",
        ],
        check=True,
        capture_output=True,
    )
    return root


@pytest.mark.parametrize("target,number", [("init-00001", 1), ("epic-00002", 2), ("iss-00003", 3)])
def test_work_commands_start_and_finish_all_three_kinds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], target: str, number: int
) -> None:
    root = three_kind_workspace(tmp_path / "consumer")
    states = {"1": "open", "2": "completed" if number == 1 else "open", "3": "completed" if number < 3 else "open"}
    log = github_fixture(tmp_path, monkeypatch, states)
    metadata = {path: path.read_bytes() for path in (root / "spec-dock").rglob(".meta.json")}
    arguments = ["--project", str(root)]
    assert main([*arguments, "work", "start", target, "--base", "HEAD", "--json"]) == 0
    started = json.loads(capsys.readouterr().out)
    assert started["status"] == "succeeded" and started["data"]["scope_id"] == target
    branch = started["data"]["branch_after"]
    record = root / "spec-dock/.agent/work-target" / f"target-{started['data']['selection_token']}.json"
    assert json.loads(record.read_bytes())["scope_id"] == target
    assert list(record.parent.glob("target-*.json")) == [record]
    before = record.read_bytes()
    assert main([*arguments, "work", "start", target, "--branch", branch, "--dry-run", "--json"]) == 0
    preview = json.loads(capsys.readouterr().out)
    assert preview["status"] == "planned" and preview["data"]["branch_after"] == branch
    assert record.read_bytes() == before
    assert main([*arguments, "work", "finish", target, "--yes", "--json"]) == 0
    finished = json.loads(capsys.readouterr().out)
    assert finished["data"]["completed"] is True and finished["data"]["scope_id"] == target
    assert finished["data"]["branch_after"] == branch and finished["data"]["selection_token"] is None
    assert not record.exists()
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"], text=True).strip() == branch
    requests = [json.loads(line) for line in log.read_text().splitlines()]
    assert [(row["method"], row["number"]) for row in requests if row["method"] == "PATCH"] == [("PATCH", number)]
    assert json.loads((tmp_path / "remote-states.json").read_bytes()) == {**states, str(number): "completed"}
    assert all(path.read_bytes() == exact for path, exact in metadata.items())
    assert not (root / ".git/spec-dock").exists()
    assert subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"]) == b""


def test_work_adapter_plans_start_and_finish_without_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = three_kind_workspace(tmp_path / "consumer")
    log = github_fixture(tmp_path, monkeypatch, {"1": "open", "2": "open", "3": "open"})
    metadata = {path: path.read_bytes() for path in (root / "spec-dock").rglob(".meta.json")}
    branches = subprocess.check_output(["git", "-C", str(root), "show-ref"])
    arguments = ["--project", str(root)]
    assert main([*arguments, "work", "start", "iss-00003", "--base", "HEAD", "--dry-run", "--json"]) == 0
    start = json.loads(capsys.readouterr().out)
    assert start["status"] == "planned" and start["data"]["scope_id"] == "iss-00003"
    assert start["data"]["selection_token"] is None
    assert all(effect["status"] in ("planned", "unchanged") for effect in start["effects"])
    assert main([*arguments, "work", "finish", "iss-00003", "--dry-run", "--json"]) == 0
    finish = json.loads(capsys.readouterr().out)
    assert finish["status"] == "planned" and finish["data"]["completed"] is False
    assert finish["effects"] == [{"kind": "github.issue.close", "status": "planned", "target": "gh:example/repo#3"}]
    calls = log.read_bytes()
    assert main([*arguments, "work", "finish", "iss-00003", "--json"]) == 3
    assert "requires --yes" in json.loads(capsys.readouterr().out)["error"]["message"]
    assert log.read_bytes() == calls
    assert all(path.read_bytes() == exact for path, exact in metadata.items())
    assert json.loads((tmp_path / "remote-states.json").read_bytes()) == {"1": "open", "2": "open", "3": "open"}
    assert subprocess.check_output(["git", "-C", str(root), "show-ref"]) == branches
    assert subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"]) == b""
    assert not (root / "spec-dock/.agent").exists() and not (root / ".git/spec-dock").exists()
