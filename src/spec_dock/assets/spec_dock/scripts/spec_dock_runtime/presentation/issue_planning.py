from __future__ import annotations

import json
from typing import TYPE_CHECKING

from spec_dock_runtime.presentation.contracts import CliText

if TYPE_CHECKING:
    from spec_dock_runtime.domain.issue_planning_contracts import PlanningCommandResult


def render_planning_result_text(result: PlanningCommandResult) -> CliText:
    payload = result.to_dict()
    lines = [
        f"status: {payload['status']}",
        f"reason: {payload['reason']}",
        f"issue_id: {payload['issue_id']}",
    ]
    if payload["output"]:
        lines.append(
            "output: "
            + json.dumps(
                payload["output"],
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
    if payload["details"]:
        lines.append("details:")
        lines.extend(f"- {detail}" for detail in payload["details"])
    return CliText(stdout_lines=lines, stderr_lines=[], warnings=[])


def render_planning_result_json(result: PlanningCommandResult) -> CliText:
    return CliText(
        stdout_lines=[
            json.dumps(
                result.to_dict(),
                ensure_ascii=False,
                separators=(",", ":"),
            )
        ],
        stderr_lines=[],
        warnings=[],
    )
