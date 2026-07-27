import json
from pathlib import Path
import sys

import pytest

RUNTIME_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
)
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))

from spec_dock_runtime.domain.issue_planning_contracts import PlanningCommandResult  # noqa: E402
from spec_dock_runtime.presentation.issue_planning import (  # noqa: E402
    render_planning_result_json,
    render_planning_result_text,
)


@pytest.mark.parametrize(
    ("status", "reason"),
    [
        ("ok", "candidate_created"),
        ("ready", "adoption_published"),
        ("blocked", "missing_evidence"),
        ("stale", "source_drift"),
        ("rejected", "identity_mismatch"),
        ("rolled_back", "validation_failed"),
        ("recovery_required", "restore_unconfirmed"),
        ("publication_pending", "push_failed"),
        ("blocked_remote_diverged", "remote_diverged"),
    ],
)
def test_text_and_json_preserve_status_reason_and_issue_id(status: str, reason: str) -> None:
    result = PlanningCommandResult(
        status=status,
        reason=reason,
        issue_id="iss-00003",
        output={"path": "candidate.zip"},
        details=("detail",),
    )
    text = render_planning_result_text(result)
    payload = json.loads(render_planning_result_json(result).stdout_lines[0])
    assert text.stdout_lines[:3] == [
        f"status: {payload['status']}",
        f"reason: {payload['reason']}",
        f"issue_id: {payload['issue_id']}",
    ]
    assert text.stderr_lines == []


def test_renderer_does_not_promote_ok_to_ready() -> None:
    result = PlanningCommandResult(
        status="ok",
        reason="review_completed",
        issue_id="iss-00003",
    )
    assert "status: ok" in render_planning_result_text(result).stdout_lines
    assert json.loads(render_planning_result_json(result).stdout_lines[0])["status"] == "ok"
