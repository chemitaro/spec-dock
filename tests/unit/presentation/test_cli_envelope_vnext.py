"""Stable vNext CLI output contract."""

from dataclasses import dataclass
import json
from pathlib import Path
import sys

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[3] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.presentation.completion import completion_script  # noqa: E402
from spec_dock_runtime.presentation.envelope import (  # noqa: E402
    Diagnostic,
    Effect,
    OperationResult,
    Recovery,
    render_json,
    render_text,
)


@dataclass(frozen=True)
class ActiveShowData:
    focus_id: str | None
    initiative: str | None
    epic: str | None
    issue: str | None
    revision: int


def test_empty_active_json_is_one_complete_envelope() -> None:
    result = OperationResult(
        command="active.show",
        status="succeeded",
        data=ActiveShowData(None, None, None, None, 0),
        exit_code=0,
    )

    output = render_json(result)

    assert output.endswith("\n") and output.count("\n") == 1
    assert json.loads(output) == {
        "schema_version": "specdock.cli/v1",
        "command": "active.show",
        "status": "succeeded",
        "operation_id": None,
        "target": None,
        "data": {"focus_id": None, "initiative": None, "epic": None, "issue": None, "revision": 0},
        "effects": [],
        "warnings": [],
        "error": None,
        "recovery": None,
    }


def test_partial_result_keeps_unknown_effect_and_recovery_boundary() -> None:
    result = OperationResult(
        command="work.finish",
        status="partial",
        data=ActiveShowData("iss-00409", "init-local-00003", "epic-00356", "iss-00409", 3),
        exit_code=6,
        operation_id="op-123",
        effects=(Effect("github.close", "unknown", "iss-00409"),),
        error=Diagnostic("REMOTE_EFFECT_UNKNOWN", "状態が不明\n確認してください", {"secret_redacted": True}),
        recovery=Recovery(
            "op-123", True, False, (("spec-dock", "work", "finish", "iss-00409", "--resume", "op-123"),), None
        ),
    )

    output = render_json(result)
    decoded = json.loads(output)

    assert output.count("\n") == 1
    assert decoded["effects"][0] == {"kind": "github.close", "status": "unknown", "target": "iss-00409"}
    assert decoded["error"]["message"] == "状態が不明\n確認してください"
    assert decoded["recovery"]["commands"][0][3] == "iss-00409"


def test_result_rejects_success_exit_with_partial_effect() -> None:
    with pytest.raises(ValueError, match="partial"):
        OperationResult(
            command="work.finish",
            status="partial",
            data=ActiveShowData(None, None, None, None, 0),
            exit_code=0,
            effects=(Effect("github.close", "unknown", "iss-00409"),),
            error=Diagnostic("UNKNOWN", "unknown", {}),
        )


def test_text_renderer_reports_same_effect_and_error_codes() -> None:
    result = OperationResult(
        command="work.finish",
        status="partial",
        data=ActiveShowData("iss-00409", None, None, "iss-00409", 4),
        exit_code=6,
        effects=(Effect("github.close", "succeeded", "iss-00409"), Effect("active.clear", "failed", "iss-00409")),
        error=Diagnostic("STATE_CONFLICT", "選択が変更されました", {}),
    )

    stdout, stderr = render_text(result)

    assert "work.finish" in stdout
    assert "github.close" in stdout and "succeeded" in stdout
    assert "active.clear" in stdout and "failed" in stdout
    assert "STATE_CONFLICT" in stderr


@pytest.mark.parametrize("shell", ["bash", "zsh", "fish"])
def test_completion_script_contains_catalog_driven_scope_children(shell: str) -> None:
    script = completion_script(shell)
    assert script.endswith("\n")
    assert "spec-dock" in script
    assert "scope" in script
    assert "initiative" in script
    assert "completion" in script


def test_json_renderer_redacts_secret_bearing_details() -> None:
    result = OperationResult(
        command="workspace.doctor",
        status="failed",
        data=ActiveShowData(None, None, None, None, 0),
        exit_code=5,
        error=Diagnostic("REMOTE_FAILED", "Authorization: Bearer private-value", {"access_token": "private-value"}),
    )

    output = render_json(result)

    assert "private-value" not in output
    assert json.loads(output)["error"]["details"]["access_token"] == "[redacted]"
