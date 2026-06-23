from __future__ import annotations

import json
from pathlib import Path
import sys


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application import contracts as app_contracts
        from spec_dock_runtime.domain import assurance as domain_assurance
        from spec_dock_runtime.presentation import assurance_text
    finally:
        sys.path.pop(0)
    return app_contracts, domain_assurance, assurance_text


def _target(app_contracts):
    return app_contracts.AssuranceTargetView(
        issue_id="iss-00227",
        repo_relative_path="spec-dock/initiatives/init/epics/epic/issues/iss-00227-target",
    )


def _contract(domain_assurance):
    return domain_assurance.build_assurance_contract(
        issue_id="iss-00227",
        stage=domain_assurance.ClassificationStage.REQUIREMENT,
        source_binding=domain_assurance.SourceBinding(
            artifacts=(
                domain_assurance.SourceArtifact(
                    path="spec-dock/initiatives/init/epics/epic/issues/iss-00227-target/requirement.md",
                    display_path="spec-dock/active/issue/requirement.md",
                    role="requirement",
                    sha256="0" * 64,
                ),
            ),
        ),
    )


def test_renders_valid_adaptive_text_and_stable_json_without_policy_recomputation() -> None:
    app_contracts, domain_assurance, assurance_text = _runtime_modules()
    result = app_contracts.AssuranceResult(
        operation="show",
        ok=True,
        status="valid",
        target=_target(app_contracts),
        mode="adaptive",
        reason="ok",
        details=(),
        contract=_contract(domain_assurance),
    )

    text = assurance_text.render_assurance_text(result)
    payload = json.loads(assurance_text.render_assurance_json(result))

    assert text.stdout_lines == [
        "assurance show: ok",
        "issue: iss-00227",
        "mode: adaptive",
        "has_contract: true",
        "authorized_profile: standard",
        "complexity_tier: normal",
        "lite_candidate: false",
        "lite_authorized: false",
        "reason: ok",
    ]
    assert payload["operation"] == "show"
    assert payload["ok"] is True
    assert payload["mode"] == "adaptive"
    assert payload["has_contract"] is True
    assert payload["classification"]["authorized_profile"] == "standard"
    assert payload["classification"]["reason_codes"][0] == "fact_default_docs_only_change"


def test_renders_strict_legacy_missing_as_success_without_contract() -> None:
    app_contracts, _domain_assurance, assurance_text = _runtime_modules()
    result = app_contracts.AssuranceResult(
        operation="verify",
        ok=True,
        status="missing",
        target=_target(app_contracts),
        mode="strict-legacy",
        reason="missing_assurance_contract",
        details=(),
        contract=None,
    )

    text = assurance_text.render_assurance_text(result)
    payload = json.loads(assurance_text.render_assurance_json(result))

    assert text.stdout_lines == [
        "assurance verify: ok",
        "issue: iss-00227",
        "mode: strict-legacy",
        "has_contract: false",
        "authorized_profile: strict",
        "complexity_tier: complex",
        "reason: missing_assurance_contract",
    ]
    assert payload == {
        "operation": "verify",
        "ok": True,
        "status": "missing",
        "issue_id": "iss-00227",
        "issue_path": "spec-dock/initiatives/init/epics/epic/issues/iss-00227-target",
        "mode": "strict-legacy",
        "has_contract": False,
        "reason": "missing_assurance_contract",
        "details": [],
        "classification": {
            "authorized_profile": "strict",
            "complexity_tier": "complex",
            "lite_candidate": False,
            "lite_authorized": False,
            "reason_codes": ["strict_legacy_missing_assurance_contract"],
            "hard_triggers": [],
            "unknown_facts": [],
        },
    }


def test_renders_invalid_result_with_machine_reason_and_details() -> None:
    app_contracts, _domain_assurance, assurance_text = _runtime_modules()
    result = app_contracts.AssuranceResult(
        operation="verify",
        ok=False,
        status="invalid",
        target=_target(app_contracts),
        mode="invalid",
        reason="invalid_schema",
        details=("missing_policy_version",),
        contract=None,
    )

    text = assurance_text.render_assurance_text(result)
    payload = json.loads(assurance_text.render_assurance_json(result))

    assert text.stdout_lines == [
        "assurance verify: failed",
        "issue: iss-00227",
        "mode: invalid",
        "has_contract: false",
        "reason: invalid_schema",
        "details:",
        "- missing_policy_version",
    ]
    assert payload == {
        "operation": "verify",
        "ok": False,
        "status": "invalid",
        "issue_id": "iss-00227",
        "issue_path": "spec-dock/initiatives/init/epics/epic/issues/iss-00227-target",
        "mode": "invalid",
        "has_contract": False,
        "reason": "invalid_schema",
        "details": ["missing_policy_version"],
    }

