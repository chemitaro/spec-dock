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


def _profile_template(artifact: str, profile: str, body: str):
    artifact_composer = _artifact_composer_module()
    return artifact_composer.ProfileArtifactTemplate(
        profile=profile,
        artifact=artifact,
        repo_relative_path=f"spec-dock/templates/issue-profiles/{profile}/{artifact}.md",
        body=body,
    )


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


def _design_placeholder() -> str:
    return """---
ID: "iss-test"
artifact_state: awaiting-assurance-compose
---
# iss-test — 設計 placeholder

このファイルはまだ合成されていません。

先に `requirement.md` を具体化し、`assurance classify --stage requirement` を実行してください。
その後、`assurance compose --artifact all` を実行して、この Issue の分類に応じた設計書テンプレートを合成してください。

この状態のまま設計本文を書き始めないでください。
"""


def test_design_and_plan_compose_materializes_profile_markdown_template_body() -> None:
    artifact_composer = _artifact_composer_module()
    assurance = _assurance_module()
    manifest = _manifest()

    design = artifact_composer.compose_artifact(
        _design_placeholder(),
        manifest,
        "design",
        assurance.AssuranceProfile.STRICT,
        profile_template=_profile_template(
            "design",
            "strict",
            "# Strict Design Template\n\nMarkdown body from strict design template.\n",
        ),
    )
    plan = artifact_composer.compose_artifact(
        _plan_placeholder(),
        manifest,
        "plan",
        assurance.AssuranceProfile.STRICT,
        profile_template=_profile_template(
            "plan",
            "strict",
            "# Strict Plan Template\n\nMarkdown body from strict plan template.\n",
        ),
    )

    assert design.ok
    assert design.output_text is not None
    assert "artifact_state: awaiting-assurance-compose" not in design.output_text
    assert 'ID: "iss-test"' in design.output_text
    assert "Markdown body from strict design template." in design.output_text
    assert plan.ok
    assert plan.output_text is not None
    assert "Markdown body from strict plan template." in plan.output_text


def test_profile_markdown_template_compose_is_idempotent() -> None:
    artifact_composer = _artifact_composer_module()
    assurance = _assurance_module()
    manifest = _manifest()
    template = _profile_template(
        "plan",
        "standard",
        "# Standard Plan Template\n\nMarkdown body from standard plan template.\n",
    )

    first = artifact_composer.compose_artifact(
        _plan_placeholder(),
        manifest,
        "plan",
        assurance.AssuranceProfile.STANDARD,
        profile_template=template,
    )
    assert first.ok
    assert first.output_text is not None

    second = artifact_composer.compose_artifact(
        first.output_text,
        manifest,
        "plan",
        assurance.AssuranceProfile.STANDARD,
        profile_template=template,
    )

    assert second.ok
    assert second.output_text == first.output_text
    assert not second.changed


def test_profile_markdown_template_leaves_old_managed_section_design_and_plan_unchanged() -> None:
    artifact_composer = _artifact_composer_module()
    assurance = _assurance_module()
    manifest = _manifest()
    cases = (
        (
            "design",
            """---
ID: "iss-test"
状態: "approved"
---
# Design

<!-- spec-dock:managed-section begin id="design.step-contract" -->
## Step Contract
Old managed design content must stay unchanged.
<!-- spec-dock:managed-section end id="design.step-contract" -->
""",
            "# Standard Design Template\n\nNEW_DESIGN_TEMPLATE_BODY_MUST_NOT_APPEND\n",
        ),
        (
            "plan",
            """---
ID: "iss-test"
状態: "approved"
---
# Plan

<!-- spec-dock:managed-section begin id="plan.step-contract" -->
## Step Contract
Old managed plan content must stay unchanged.
<!-- spec-dock:managed-section end id="plan.step-contract" -->
""",
            "# Standard Plan Template\n\nNEW_PLAN_TEMPLATE_BODY_MUST_NOT_APPEND\n",
        ),
    )

    for artifact, old_text, template_body in cases:
        result = artifact_composer.compose_artifact(
            old_text,
            manifest,
            artifact,
            assurance.AssuranceProfile.STANDARD,
            profile_template=_profile_template(artifact, "standard", template_body),
        )

        assert result.ok
        assert result.output_text == old_text
        assert not result.changed
        assert "MUST_NOT_APPEND" not in result.output_text


def test_profile_markdown_template_does_not_overwrite_substantive_content() -> None:
    artifact_composer = _artifact_composer_module()
    assurance = _assurance_module()
    manifest = _manifest()

    result = artifact_composer.compose_artifact(
        '---\nID: "iss-test"\n---\n# Human Design\n\nHuman-authored design body.\n',
        manifest,
        "design",
        assurance.AssuranceProfile.STANDARD,
        profile_template=_profile_template(
            "design",
            "standard",
            "# Standard Design Template\n\nTemplate body must not overwrite humans.\n",
        ),
    )

    assert not result.ok
    assert result.output_text is None
    assert result.errors[0].kind == "substantive_content_conflict"


def test_profile_markdown_template_invalid_marker_fails_closed() -> None:
    artifact_composer = _artifact_composer_module()
    assurance = _assurance_module()
    manifest = _manifest()

    result = artifact_composer.compose_artifact(
        _design_placeholder(),
        manifest,
        "design",
        assurance.AssuranceProfile.STANDARD,
        profile_template=_profile_template(
            "design",
            "standard",
            '# Standard Design Template\n\n<!-- spec-dock:managed-section begin id="design.invalid" -->\n',
        ),
    )

    assert not result.ok
    assert result.output_text is None
    assert result.changed is False
    assert result.errors[0].kind == "unclosed_marker"


def test_authorized_standard_lite_candidate_uses_standard_markdown_template_not_lite() -> None:
    artifact_composer = _artifact_composer_module()
    assurance = _assurance_module()
    manifest = _manifest()

    standard_candidate = artifact_composer.compose_artifact(
        _plan_placeholder(),
        manifest,
        "plan",
        assurance.AssuranceProfile.STANDARD,
        lite_candidate=True,
        profile_template=_profile_template(
            "plan",
            "standard",
            "# Standard Plan Template\n\nSTANDARD_ONLY_TEMPLATE_BODY\n",
        ),
    )

    assert standard_candidate.ok
    assert standard_candidate.output_text is not None
    assert "STANDARD_ONLY_TEMPLATE_BODY" in standard_candidate.output_text
    assert "Lite Plan Template" not in standard_candidate.output_text


def test_profile_sections_manifest_keeps_only_report_prose_sections() -> None:
    manifest = _manifest()

    assert manifest.sections
    assert {section.artifact for section in manifest.sections.values()} == {"report"}
    for profile in ("lite", "standard", "strict", "critical"):
        assert manifest.sections_for(profile, "design") == ()
        assert manifest.sections_for(profile, "plan") == ()
        assert manifest.sections_for(profile, "report")


def test_report_profile_selection_uses_authorized_profile_for_all_profiles() -> None:
    artifact_composer = _artifact_composer_module()
    assurance = _assurance_module()
    manifest = _manifest()

    expected_report_sections = {
        assurance.AssuranceProfile.LITE: ("report.lite-evidence",),
        assurance.AssuranceProfile.STANDARD: ("report.step-evidence",),
        assurance.AssuranceProfile.STRICT: ("report.step-evidence", "report.strict-evidence"),
        assurance.AssuranceProfile.CRITICAL: (
            "report.step-evidence",
            "report.strict-evidence",
            "report.critical-evidence",
        ),
    }

    for profile, expected_section_ids in expected_report_sections.items():
        result = artifact_composer.compose_artifact(
            "# Report\n",
            manifest,
            "report",
            profile,
        )

        assert result.ok
        assert result.added_section_ids == expected_section_ids
        assert result.output_text is not None
        for section_id in expected_section_ids:
            assert f'id="{section_id}"' in result.output_text


def test_report_lite_candidate_does_not_select_lite_without_authorized_lite() -> None:
    artifact_composer = _artifact_composer_module()
    assurance = _assurance_module()
    manifest = _manifest()

    standard_candidate = artifact_composer.compose_artifact(
        "# Report\n",
        manifest,
        "report",
        assurance.AssuranceProfile.STANDARD,
        lite_candidate=True,
    )
    explicit_lite = artifact_composer.compose_artifact(
        "# Report\n",
        manifest,
        "report",
        assurance.AssuranceProfile.LITE,
        lite_candidate=True,
    )

    assert standard_candidate.ok
    assert standard_candidate.added_section_ids == ("report.step-evidence",)
    assert standard_candidate.output_text is not None
    assert 'id="report.lite-evidence"' not in standard_candidate.output_text
    assert explicit_lite.added_section_ids == ("report.lite-evidence",)


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
