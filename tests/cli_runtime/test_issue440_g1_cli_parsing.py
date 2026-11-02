"""Mode-independent argument and help contracts moved off the schema-3 test modules (iss-00440).

Moved unchanged from tests/cli_runtime/test_issue413_active.py, test_issue413_work_start.py,
test_issue413_finish.py and test_issue416_branch_lock.py, whose fixtures were legacy-only.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from spec_dock.runtime.cli.options import parse_vnext_output

if TYPE_CHECKING:
    from pathlib import Path


def test_active_help_describes_start_only_acquisition_and_direct_clear(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["help", "active", "set"]) == 0
    help_text = capsys.readouterr().out
    assert "work start" in help_text
    assert "unchanged" in help_text
    assert "--from-branch" not in help_text
    assert main(["help", "active", "clear"]) == 0
    help_text = capsys.readouterr().out
    assert "observed" in help_text
    assert "--all --yes" in help_text
    assert "promot" in help_text


@pytest.mark.parametrize("flag", ["--from-branch", "--resume", "--rollback"])
def test_active_retired_acquisition_inputs_fail_before_project_access(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], flag: str
) -> None:
    args = (
        ["active", "set", "--from-branch"] if flag == "--from-branch" else ["active", "clear", "--all", flag, "0" * 32]
    )
    assert main(["--project", str(tmp_path / "absent"), *args, "--json"]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED"
    assert result["effects"] == []


@pytest.mark.parametrize(
    "retired",
    [["--source", "cache"], ["--source=cache"], ["--allow-stale"], ["--resume", "0" * 32], ["--rollback", "0" * 32]],
)
def test_start_rejects_retired_inputs_before_project_access(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], retired: list[str]
) -> None:
    assert main(["--project", str(tmp_path / "missing"), "work", "start", "iss-00413", *retired, "--json"]) == 2
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED"
    assert result["effects"] == []
    assert output.err == ""
    assert list(tmp_path.iterdir()) == []


def test_finish_rejects_journal_recovery_input_before_project_access(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert (
        main(["--project", str(tmp_path / "missing"), "work", "finish", "iss-00413", "--resume", "0" * 32, "--json"])
        == 2
    )
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED"
    assert result["effects"] == []
    assert list(tmp_path.iterdir()) == []


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
