from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from spec_dock_runtime.presentation.contracts import CliText

if TYPE_CHECKING:
    from spec_dock_runtime.application.contracts import AssuranceResult


def render_assurance_text(result: AssuranceResult) -> CliText:
    status_text = "ok" if result.ok else "failed"
    lines = [
        f"assurance {result.operation}: {status_text}",
        f"issue: {result.target.issue_id}",
        f"mode: {result.mode}",
        f"has_contract: {_bool_text(result.has_contract)}",
    ]
    classification = _classification_payload(result)
    if classification is not None:
        lines.extend(
            [
                f"authorized_profile: {classification['authorized_profile']}",
                f"complexity_tier: {classification['complexity_tier']}",
            ]
        )
        if result.has_contract:
            lines.extend(
                [
                    f"lite_candidate: {_bool_text(bool(classification['lite_candidate']))}",
                    f"lite_authorized: {_bool_text(bool(classification['lite_authorized']))}",
                ]
            )
    lines.append(f"reason: {result.reason}")
    if result.details:
        lines.append("details:")
        lines.extend(f"- {detail}" for detail in result.details)
    return CliText(stdout_lines=lines, stderr_lines=[], warnings=[])


def render_assurance_json(result: AssuranceResult) -> str:
    return json.dumps(_result_payload(result), ensure_ascii=False, separators=(",", ":"))


def _result_payload(result: AssuranceResult) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "operation": result.operation,
        "ok": result.ok,
        "status": result.status,
        "issue_id": result.target.issue_id,
        "issue_path": result.target.repo_relative_path,
        "mode": result.mode,
        "has_contract": result.has_contract,
        "reason": result.reason,
        "details": list(result.details),
    }
    if result.dry_run:
        payload["dry_run"] = True
    if result.written_path is not None:
        payload["written_path"] = str(result.written_path)
    classification = _classification_payload(result)
    if classification is not None:
        payload["classification"] = classification
    if result.contract is not None:
        payload["contract"] = result.contract.to_dict()
    return payload


def _classification_payload(result: AssuranceResult) -> dict[str, Any] | None:
    if result.contract is not None:
        return result.contract.classification.to_dict()
    if result.status == "missing" and result.mode == "strict-legacy":
        return {
            "authorized_profile": "strict",
            "complexity_tier": "complex",
            "lite_candidate": False,
            "lite_authorized": False,
            "reason_codes": ["strict_legacy_missing_assurance_contract"],
            "hard_triggers": [],
            "unknown_facts": [],
        }
    return None


def _bool_text(value: bool) -> str:
    return "true" if value else "false"
