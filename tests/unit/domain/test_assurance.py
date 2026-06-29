from __future__ import annotations

import ast
from pathlib import Path
import sys

import pytest


def _assurance_module():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.domain import assurance
    finally:
        sys.path.pop(0)
    return assurance


def _source_binding():
    assurance = _assurance_module()
    return assurance.SourceBinding(
        artifacts=(
            assurance.SourceArtifact(
                path="spec-dock/initiatives/init-local-00003/epics/epic-00224/issues/iss-00227/requirement.md",
                display_path="spec-dock/active/issue/requirement.md",
                role="requirement",
                sha256="0" * 64,
            ),
        ),
    )


def test_default_contract_serialization_is_deterministic_and_omits_volatile_fields() -> None:
    assurance = _assurance_module()

    first = assurance.build_assurance_contract(
        issue_id="iss-00227",
        stage=assurance.ClassificationStage.REQUIREMENT,
        source_binding=_source_binding(),
    )
    second = assurance.build_assurance_contract(
        issue_id="iss-00227",
        stage=assurance.ClassificationStage.REQUIREMENT,
        source_binding=_source_binding(),
    )

    first_bytes = assurance.canonical_json_bytes(first)
    second_bytes = assurance.canonical_json_bytes(second)
    assert first_bytes == second_bytes
    assert b"generated_at" not in first_bytes
    assert b"classified_at" not in first_bytes
    assert b"proposed_profile" not in first_bytes

    payload = first.to_dict()
    assert payload["policy_version"] == "assurance-policy-v1"
    assert payload["stage"] == "requirement"
    assert payload["status"] == "provisional"
    assert payload["mode"] == "adaptive"
    assert payload["classification"] == {
        "authorized_profile": "standard",
        "complexity_tier": "normal",
        "lite_candidate": False,
        "lite_authorized": False,
        "reason_codes": [
            "fact_default_docs_only_change",
            "fact_default_explicit_lite_opt_in",
            "fact_default_lite_evidence_gate_passed",
            "fact_default_migration_or_persistence_change",
            "fact_default_public_contract_change",
            "fact_default_rollback_difficulty_high",
            "fact_default_runtime_behavior_change",
            "fact_default_security_or_privacy_sensitive",
            "hard_trigger_migration_unknown",
            "hard_trigger_public_contract_unknown",
            "hard_trigger_rollback_unknown",
            "hard_trigger_security_unknown",
            "lite_evidence_gate_missing_or_unknown",
            "lite_opt_in_missing_or_unknown",
            "lite_predicate_docs_only_unknown",
            "lite_predicate_runtime_behavior_unknown",
            "standard_default",
        ],
        "hard_triggers": [],
        "unknown_facts": [
            "migration_or_persistence_change",
            "public_contract_change",
            "rollback_difficulty_high",
            "security_or_privacy_sensitive",
        ],
    }
    assert [fact["key"] for fact in payload["risk_facts"]] == [
        "docs_only_change",
        "explicit_lite_opt_in",
        "lite_evidence_gate_passed",
        "migration_or_persistence_change",
        "public_contract_change",
        "rollback_difficulty_high",
        "runtime_behavior_change",
        "security_or_privacy_sensitive",
    ]
    assert {fact["reason_code"] for fact in payload["risk_facts"]} == {
        f"fact_default_{fact['key']}" for fact in payload["risk_facts"]
    }


def test_lite_authorization_fails_closed_for_unknowns_and_requires_explicit_gates() -> None:
    assurance = _assurance_module()

    default_classification = assurance.classify_risk_facts(assurance.default_risk_facts())
    assert default_classification.authorized_profile == assurance.AssuranceProfile.STANDARD
    assert not default_classification.lite_candidate
    assert not default_classification.lite_authorized

    all_positive_without_gates = assurance.classify_risk_facts(
        assurance.risk_facts_from_values(
            {
                "docs_only_change": "true",
                "runtime_behavior_change": "false",
                "public_contract_change": "false",
                "migration_or_persistence_change": "false",
                "security_or_privacy_sensitive": "false",
                "rollback_difficulty_high": "false",
                "explicit_lite_opt_in": "false",
                "lite_evidence_gate_passed": "false",
            },
            source="requirement",
            reason_prefix="fixture",
        ),
    )
    assert all_positive_without_gates.authorized_profile == assurance.AssuranceProfile.STANDARD
    assert all_positive_without_gates.lite_candidate
    assert not all_positive_without_gates.lite_authorized
    assert "lite_opt_in_missing_or_unknown" in all_positive_without_gates.reason_codes
    assert "lite_evidence_gate_missing_or_unknown" in all_positive_without_gates.reason_codes


def test_auto_lite_readiness_report_keeps_default_disabled_and_records_adoption_gates() -> None:
    assurance = _assurance_module()
    classification = assurance.classify_risk_facts(assurance.default_risk_facts())

    report = assurance.auto_lite_readiness_report(classification)

    assert report["automatic_lite_default_enabled"] is False
    assert report["lite_candidate"] is False
    assert report["lite_authorized"] is False
    assert report["future_adoption_requires"] == [
        "accepted_adr",
        "policy_version_bump",
        "rollout_issue",
        "telemetry_gate",
    ]
    assert report["rollback_mode"] == "strict-legacy"
    assert report["automation_stalled_routes_to"] == "human_gate"
    assert "missing_metrics_summary" in report["required_metrics"]
    assert report["missing_metrics_summary"]["present"] is True
    baseline = report["efficiency_baseline"]["profiles"]
    assert baseline["lite"]["invocation_count"] < baseline["standard"]["invocation_count"]
    assert baseline["lite"]["runbook_sections"] < baseline["standard"]["runbook_sections"]
    assert baseline["lite"]["review_generation_required"] is False
    assert baseline["standard"]["review_generation_required"] is True
    assert baseline["standard"]["wall_clock_token_proxy"] < baseline["strict"]["wall_clock_token_proxy"]
    assert (
        report["efficiency_baseline"]["comparison"]["lite_vs_standard_wall_clock_token_proxy_delta"]
        == baseline["lite"]["wall_clock_token_proxy"] - baseline["standard"]["wall_clock_token_proxy"]
    )


def test_hard_trigger_escalation_is_monotonic_and_drives_complexity_without_lite_override() -> None:
    assurance = _assurance_module()

    cases = [
        ("public_contract_change", assurance.AssuranceProfile.STRICT, assurance.ComplexityTier.COMPLEX),
        ("migration_or_persistence_change", assurance.AssuranceProfile.STRICT, assurance.ComplexityTier.COMPLEX),
        ("rollback_difficulty_high", assurance.AssuranceProfile.STRICT, assurance.ComplexityTier.COMPLEX),
        ("security_or_privacy_sensitive", assurance.AssuranceProfile.CRITICAL, assurance.ComplexityTier.DEEP),
    ]

    for fact_key, expected_profile, expected_tier in cases:
        values = assurance.lite_positive_values()
        values[fact_key] = "true"
        values["explicit_lite_opt_in"] = "true"
        values["lite_evidence_gate_passed"] = "true"
        classification = assurance.classify_risk_facts(
            assurance.risk_facts_from_values(values, source="requirement", reason_prefix="fixture"),
        )
        assert classification.authorized_profile == expected_profile, fact_key
        assert classification.complexity_tier == expected_tier, fact_key
        assert not classification.lite_candidate, fact_key
        assert not classification.lite_authorized, fact_key
        assert fact_key in classification.hard_triggers, fact_key

    values = assurance.lite_positive_values()
    values["public_contract_change"] = "true"
    values["security_or_privacy_sensitive"] = "true"
    classification = assurance.classify_risk_facts(
        assurance.risk_facts_from_values(values, source="requirement", reason_prefix="fixture"),
    )
    assert classification.authorized_profile == assurance.AssuranceProfile.CRITICAL
    assert classification.complexity_tier == assurance.ComplexityTier.DEEP


def test_classification_rejects_duplicate_raw_risk_fact_keys() -> None:
    assurance = _assurance_module()
    facts = assurance.default_risk_facts()
    duplicate_fact = assurance.RiskFact(
        key=facts[0].key,
        value="true",
        source="fixture",
        reason_code="fixture_duplicate",
    )

    with pytest.raises(ValueError, match="duplicate assurance facts: docs_only_change"):
        assurance.classify_risk_facts((*facts, duplicate_fact))


def test_classification_rejects_invalid_raw_risk_fact_values() -> None:
    assurance = _assurance_module()
    facts = list(assurance.default_risk_facts())
    facts[0] = assurance.RiskFact(
        key=facts[0].key,
        value="maybe",
        source=facts[0].source,
        reason_code=facts[0].reason_code,
    )

    with pytest.raises(ValueError, match="unsupported assurance fact value for docs_only_change: maybe"):
        assurance.classify_risk_facts(tuple(facts))


def test_build_contract_rejects_explicit_empty_risk_facts() -> None:
    assurance = _assurance_module()

    with pytest.raises(ValueError, match="missing supported assurance facts:"):
        assurance.build_assurance_contract(
            issue_id="iss-00227",
            stage=assurance.ClassificationStage.REQUIREMENT,
            source_binding=_source_binding(),
            risk_facts=(),
        )


def test_contract_validation_rejects_missing_source_binding_artifacts() -> None:
    assurance = _assurance_module()
    contract = assurance.build_assurance_contract(
        issue_id="iss-00227",
        stage=assurance.ClassificationStage.REQUIREMENT,
        source_binding=assurance.SourceBinding(artifacts=()),
    )

    assert "missing_source_binding_artifacts" in assurance.validate_assurance_contract(contract)


def test_contract_validation_rejects_non_durable_source_binding_paths() -> None:
    assurance = _assurance_module()

    for path in (
        "/Users/iwasawayuuta/workspace/spec-dock/requirement.md",
        "spec-dock/active/issue/requirement.md",
    ):
        contract = assurance.build_assurance_contract(
            issue_id="iss-00227",
            stage=assurance.ClassificationStage.REQUIREMENT,
            source_binding=assurance.SourceBinding(
                artifacts=(
                    assurance.SourceArtifact(
                        path=path,
                        display_path="spec-dock/active/issue/requirement.md",
                        role="requirement",
                        sha256="0" * 64,
                    ),
                ),
            ),
        )

        assert "non_durable_source_binding_path" in assurance.validate_assurance_contract(contract)


def test_domain_assurance_has_no_runtime_adapter_imports() -> None:
    module_path = (
        Path(__file__).resolve().parents[3]
        / "src"
        / "spec_dock"
        / "assets"
        / "spec_dock"
        / "scripts"
        / "spec_dock_runtime"
        / "domain"
        / "assurance.py"
    )
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)

    forbidden_fragments = (
        "spec_dock_runtime.infra",
        "spec_dock_runtime.commands",
        "spec_dock_runtime.cli",
        "spec_dock_runtime.presentation",
        "github",
        "subprocess",
        "pathlib",
    )
    assert not any(
        imported == fragment or imported.startswith(f"{fragment}.")
        for imported in imported_modules
        for fragment in forbidden_fragments
    )
