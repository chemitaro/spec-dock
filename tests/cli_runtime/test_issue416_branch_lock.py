"""Branch switch joins the Start lock so SpecDock checkouts and link writes never overlap."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from spec_dock.runtime.cli.options import parse_vnext_output
from spec_dock.runtime.infra.start_lock import StartLock
from tests.cli_runtime.test_issue413_work_start import committed_workspace

if TYPE_CHECKING:
    from pathlib import Path


def test_branch_switch_accepts_lock_timeout() -> None:
    result = parse_vnext_output(
        ["branch", "switch", "iss-00416", "--name", "candidate", "--lock-timeout", "0"], public_v2=True
    )
    assert result.namespace is not None
    assert result.namespace.lock_timeout == 0


def test_branch_switch_lock_timeout_defaults_to_five_seconds() -> None:
    result = parse_vnext_output(["branch", "switch", "iss-00416", "--name", "candidate"], public_v2=True)
    assert result.namespace is not None
    assert result.namespace.lock_timeout == 5


@pytest.mark.parametrize(
    "arguments",
    [
        ["branch", "create", "iss-00416", "--base", "HEAD", "--lock-timeout", "0"],
        ["branch", "show", "iss-00416", "--lock-timeout", "0"],
        ["active", "set", "@current", "--lock-timeout", "0"],
    ],
)
def test_lock_timeout_is_rejected_outside_start_and_branch_switch(arguments: list[str]) -> None:
    result = parse_vnext_output(arguments, public_v2=True)
    assert result.namespace is None
    assert result.exit_code == 2


def _held_switch_workspace(tmp_path: Path) -> Path:
    root = committed_workspace(tmp_path / "consumer")
    subprocess.run(["git", "-C", str(root), "branch", "candidate"], check=True, capture_output=True)
    return root


def _git_tree(root: Path) -> set[str]:
    return {str(path.relative_to(root / ".git")) for path in (root / ".git").rglob("*")}


def test_branch_switch_waits_for_the_start_lock_and_stops_without_checkout(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _held_switch_workspace(tmp_path)
    before_git = _git_tree(root)
    with StartLock(root / ".git", timeout=0):
        code = main([
            "--project",
            str(root),
            "branch",
            "switch",
            "init-00001",
            "--name",
            "candidate",
            "--lock-timeout",
            "0",
            "--json",
        ])
    result = json.loads(capsys.readouterr().out)
    assert code == 3
    assert result["status"] == "failed"
    assert result["error"]["code"] == "START_LOCK_BUSY"
    assert result["effects"] == []
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"main\n"
    assert not subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"])
    assert _git_tree(root) == before_git


def test_branch_switch_dry_run_does_not_take_the_start_lock(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = _held_switch_workspace(tmp_path)
    with StartLock(root / ".git", timeout=0):
        code = main([
            "--project",
            str(root),
            "branch",
            "switch",
            "init-00001",
            "--name",
            "candidate",
            "--dry-run",
            "--json",
        ])
    result = json.loads(capsys.readouterr().out)
    assert code == 0
    assert result["effects"] == [{"kind": "git.checkout", "status": "planned", "target": "candidate"}]


def test_branch_switch_checks_out_once_the_start_lock_is_free(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _held_switch_workspace(tmp_path)
    with StartLock(root / ".git", timeout=0):
        pass
    code = main([
        "--project",
        str(root),
        "branch",
        "switch",
        "init-00001",
        "--name",
        "candidate",
        "--lock-timeout",
        "0",
        "--json",
    ])
    result = json.loads(capsys.readouterr().out)
    assert code == 0
    assert result["effects"] == [{"kind": "git.checkout", "status": "succeeded", "target": "candidate"}]
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"candidate\n"
