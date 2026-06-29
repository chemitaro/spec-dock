from __future__ import annotations

from pathlib import Path
import sys


def _runtime_scripts_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"


def _artifact_composer_module():
    sys.path.insert(0, str(_runtime_scripts_dir()))
    try:
        from spec_dock_runtime.domain import artifact_composer
    finally:
        sys.path.pop(0)
    return artifact_composer


def _assurance_module():
    sys.path.insert(0, str(_runtime_scripts_dir()))
    try:
        from spec_dock_runtime.domain import assurance
    finally:
        sys.path.pop(0)
    return assurance


def _manifest():
    artifact_composer = _artifact_composer_module()
    manifest_path = (
        Path(__file__).resolve().parents[3]
        / "src"
        / "spec_dock"
        / "assets"
        / "spec_dock"
        / "templates"
        / "assurance"
        / "profile-sections.json"
    )
    return artifact_composer.load_profile_section_manifest(manifest_path.read_text(encoding="utf-8"))


def _plan_placeholder() -> str:
    return """---
artifact_state: awaiting-assurance-compose
---
# iss-test — 実装計画 placeholder

このファイルはまだ合成されていません。

先に `requirement.md` を具体化し、`assurance classify --stage requirement` を実行してください。
その後、`assurance compose --artifact all` を実行して、この Issue の分類に応じた実装計画テンプレートを合成してください。

この状態のまま実装計画本文を書き始めないでください。
"""


def test_profile_selection_uses_authorized_profile_for_all_profiles() -> None:
    artifact_composer = _artifact_composer_module()
    assurance = _assurance_module()
    manifest = _manifest()

    expected_plan_sections = {
        assurance.AssuranceProfile.LITE: ("plan.lite-contract",),
        assurance.AssuranceProfile.STANDARD: ("plan.step-contract",),
        assurance.AssuranceProfile.STRICT: ("plan.step-contract", "plan.strict-review"),
        assurance.AssuranceProfile.CRITICAL: (
            "plan.step-contract",
            "plan.strict-review",
            "plan.critical-review",
        ),
    }

    for profile, expected_section_ids in expected_plan_sections.items():
        result = artifact_composer.compose_artifact(
            _plan_placeholder(),
            manifest,
            "plan",
            profile,
        )

        assert result.ok
        assert result.added_section_ids == expected_section_ids
        assert result.output_text is not None
        for section_id in expected_section_ids:
            assert f'id="{section_id}"' in result.output_text


def test_lite_candidate_does_not_select_lite_without_authorized_lite() -> None:
    artifact_composer = _artifact_composer_module()
    assurance = _assurance_module()
    manifest = _manifest()

    standard_candidate = artifact_composer.compose_artifact(
        _plan_placeholder(),
        manifest,
        "plan",
        assurance.AssuranceProfile.STANDARD,
        lite_candidate=True,
    )
    explicit_lite = artifact_composer.compose_artifact(
        _plan_placeholder(),
        manifest,
        "plan",
        assurance.AssuranceProfile.LITE,
        lite_candidate=True,
    )

    assert standard_candidate.ok
    assert standard_candidate.added_section_ids == ("plan.step-contract",)
    assert standard_candidate.output_text is not None
    assert 'id="plan.lite-contract"' not in standard_candidate.output_text
    assert explicit_lite.added_section_ids == ("plan.lite-contract",)


def test_compose_twice_is_idempotent() -> None:
    artifact_composer = _artifact_composer_module()
    assurance = _assurance_module()
    manifest = _manifest()

    first = artifact_composer.compose_artifact(
        "# Report\n",
        manifest,
        "report",
        assurance.AssuranceProfile.STRICT,
    )
    assert first.ok
    assert first.output_text is not None

    second = artifact_composer.compose_artifact(
        first.output_text,
        manifest,
        "report",
        assurance.AssuranceProfile.STRICT,
    )

    assert second.ok
    assert second.output_text == first.output_text
    assert not second.changed
    assert second.added_section_ids == ()


def test_existing_substantive_managed_section_is_preserved() -> None:
    artifact_composer = _artifact_composer_module()
    assurance = _assurance_module()
    manifest = _manifest()
    text = """# Report

<!-- spec-dock:managed-section begin id="report.step-evidence" -->
## Step Evidence
- Human-written evidence must stay.
<!-- spec-dock:managed-section end id="report.step-evidence" -->
"""

    result = artifact_composer.compose_artifact(
        text,
        manifest,
        "report",
        assurance.AssuranceProfile.STANDARD,
    )

    assert result.ok
    assert result.output_text == text
    assert result.preserved_section_ids == ("report.step-evidence",)
    assert "Human-written evidence must stay." in result.output_text


def test_downgrade_does_not_delete_stronger_sections() -> None:
    artifact_composer = _artifact_composer_module()
    assurance = _assurance_module()
    manifest = _manifest()
    strict = artifact_composer.compose_artifact(
        "# Report\n",
        manifest,
        "report",
        assurance.AssuranceProfile.STRICT,
    )
    assert strict.output_text is not None

    downgraded = artifact_composer.compose_artifact(
        strict.output_text,
        manifest,
        "report",
        assurance.AssuranceProfile.STANDARD,
    )

    assert downgraded.ok
    assert downgraded.output_text == strict.output_text
    assert 'id="report.strict-evidence"' in downgraded.output_text


def test_marker_conflict_stops_without_output_text() -> None:
    artifact_composer = _artifact_composer_module()
    assurance = _assurance_module()
    manifest = _manifest()

    duplicate_text = """# Plan

<!-- spec-dock:managed-section begin id="plan.step-contract" -->
## Step Obligation Contract
one
<!-- spec-dock:managed-section end id="plan.step-contract" -->

<!-- spec-dock:managed-section begin id="plan.step-contract" -->
## Step Obligation Contract
two
<!-- spec-dock:managed-section end id="plan.step-contract" -->
"""
    duplicate = artifact_composer.compose_artifact(
        duplicate_text,
        manifest,
        "plan",
        assurance.AssuranceProfile.STANDARD,
    )

    assert not duplicate.ok
    assert duplicate.output_text is None
    assert duplicate.errors[0].kind == "duplicated_marker"

    unclosed = artifact_composer.compose_artifact(
        '<!-- spec-dock:managed-section begin id="plan.step-contract" -->\n',
        manifest,
        "plan",
        assurance.AssuranceProfile.STANDARD,
    )
    assert not unclosed.ok
    assert unclosed.output_text is None
    assert unclosed.errors[0].kind == "unclosed_marker"

    mismatched = artifact_composer.compose_artifact(
        '<!-- spec-dock:managed-section begin id="plan.step-contract" -->\n'
        '<!-- spec-dock:managed-section end id="plan.strict-review" -->\n',
        manifest,
        "plan",
        assurance.AssuranceProfile.STANDARD,
    )
    assert not mismatched.ok
    assert mismatched.output_text is None
    assert mismatched.errors[0].kind == "mismatched_marker"

    malformed = artifact_composer.compose_artifact(
        '<!-- spec-dock:managed-section begin id="plan.step-contract" --\n',
        manifest,
        "plan",
        assurance.AssuranceProfile.STANDARD,
    )
    assert not malformed.ok
    assert malformed.output_text is None
    assert malformed.errors[0].kind == "malformed_marker"


def test_marker_token_in_plain_prose_is_not_a_conflict() -> None:
    artifact_composer = _artifact_composer_module()
    assurance = _assurance_module()
    manifest = _manifest()

    result = artifact_composer.compose_artifact(
        "# Report\n\nThe token spec-dock:managed-section may be documented in prose.\n",
        manifest,
        "report",
        assurance.AssuranceProfile.STANDARD,
    )

    assert result.ok
    assert result.output_text is not None
    assert 'id="report.step-evidence"' in result.output_text
