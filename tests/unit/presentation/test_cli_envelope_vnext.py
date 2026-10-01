"""Public v2 CLI output keeps honest effects and stateless recovery guidance."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.cli.options import completion_script
from spec_dock.runtime.presentation.command_data import ActiveData
from spec_dock.runtime.presentation.envelope import (
    Diagnostic,
    Effect,
    OperationResult,
    RecoveryInstructions,
    render_json_v2,
    render_text,
)

if TYPE_CHECKING:
    from spec_dock.runtime.presentation.envelope import ResultStatus


def _active(scope_id: str | None = None) -> ActiveData:
    return ActiveData(
        {
            "status": "selected" if scope_id else "empty",
            "scope_id": scope_id,
            "github_ref": "gh:chemitaro/spec-dock#409" if scope_id else None,
            "selection_token": "b" * 32 if scope_id else None,
            "selected_branch": "iss-00409-redesign-cli" if scope_id else None,
            "current_branch": "iss-00409-redesign-cli" if scope_id else "main",
            "branch_changed": False,
        },
        ("init-local-00003", "epic-00356") if scope_id else (),
    )


def test_empty_active_json_is_one_complete_envelope() -> None:
    result = OperationResult(
        command="active show",
        status="succeeded",
        data=_active(),
        exit_code=0,
    )

    output = render_json_v2(result)

    assert output.endswith("\n") and output.count("\n") == 1
    assert json.loads(output) == {
        "schema_version": "specdock.cli/v2",
        "command": "active show",
        "status": "succeeded",
        "exit_code": 0,
        "data": {"kind": "active", "selection": _active().selection, "ancestors": []},
        "effects": [],
        "warnings": [],
        "error": None,
        "recovery": None,
    }


def test_partial_result_keeps_unknown_effect_and_recovery_boundary() -> None:
    result = OperationResult(
        command="work finish",
        status="partial",
        data=_active("iss-00409"),
        exit_code=6,
        effects=(Effect("github.close", "unknown", "iss-00409"),),
        error=Diagnostic("REMOTE_EFFECT_UNKNOWN", "状態が不明\n確認してください", {"secret_redacted": True}),
        recovery=RecoveryInstructions(("spec-dock active show --json", "Confirm the current GitHub Issue state")),
    )

    output = render_json_v2(result)
    decoded = json.loads(output)

    assert output.count("\n") == 1
    assert decoded["effects"][0] == {"kind": "github.close", "status": "unknown", "target": "iss-00409"}
    assert decoded["error"]["message"] == "状態が不明\n確認してください"
    assert decoded["exit_code"] == 6 and "operation_id" not in decoded and "target" not in decoded
    assert decoded["recovery"] == {
        "instructions": ["spec-dock active show --json", "Confirm the current GitHub Issue state"],
        "can_resume": False,
        "can_rollback": False,
    }
    assert "--resume" not in output and "op-123" not in output


def test_result_rejects_success_exit_with_partial_effect() -> None:
    with pytest.raises(ValueError, match="partial"):
        OperationResult(
            command="work finish",
            status="partial",
            data=_active(),
            exit_code=0,
            effects=(Effect("github.close", "unknown", "iss-00409"),),
            error=Diagnostic("UNKNOWN", "unknown", {}),
        )


@pytest.mark.parametrize(
    ("status", "exit_code", "effects"),
    [
        ("succeeded", 0, (Effect("github.close", "unknown", "iss-00409"),)),
        ("unchanged", 0, (Effect("active.clear", "succeeded", "iss-00409"),)),
        ("planned", 0, (Effect("active.clear", "succeeded", "iss-00409"),)),
        ("failed", 5, (Effect("github.close", "unknown", "iss-00409"),)),
    ],
)
def test_top_level_result_cannot_hide_effect_state(
    status: ResultStatus, exit_code: int, effects: tuple[Effect, ...]
) -> None:
    with pytest.raises(ValueError, match="effect"):
        OperationResult(
            command="work finish",
            status=status,
            data=_active(),
            exit_code=exit_code,
            effects=effects,
            error=Diagnostic("FAILURE", "failure", {}) if status == "failed" else None,
        )


def test_text_renderer_reports_same_effect_and_error_codes() -> None:
    result = OperationResult(
        command="work finish",
        status="partial",
        data=_active("iss-00409"),
        exit_code=6,
        effects=(Effect("github.close", "succeeded", "iss-00409"), Effect("active.clear", "failed", "iss-00409")),
        error=Diagnostic("STATE_CONFLICT", "選択が変更されました", {}),
    )

    stdout, stderr = render_text(result)

    assert "work finish" in stdout
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
        command="workspace doctor",
        status="failed",
        data=_active(),
        exit_code=5,
        error=Diagnostic("REMOTE_FAILED", "Authorization: Bearer private-value", {"access_token": "private-value"}),
    )

    output = render_json_v2(result)

    assert "private-value" not in output
    assert json.loads(output)["error"]["details"]["access_token"] == "[redacted]"
