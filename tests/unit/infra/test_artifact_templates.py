from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = REPO_ROOT / "src/spec_dock/assets/spec_dock"
ARTIFACT_TEMPLATES = ASSET_ROOT / "templates/artifacts"


DIRECT_ARTIFACT_TEMPLATES = {
    "blank.md",
    "research.md",
    "interview.md",
    "disc.md",
    "decision-candidate.md",
    "pr-repair-batch.md",
    "adr.md",
}


def _read_asset(relative_path: str) -> str:
    return (ASSET_ROOT / relative_path).read_text(encoding="utf-8")


def test_provider_artifact_template_catalog_is_direct_only_for_supported_types() -> None:
    artifact_template_names = {path.name for path in ARTIFACT_TEMPLATES.glob("*.md")}

    assert artifact_template_names == DIRECT_ARTIFACT_TEMPLATES


def test_blank_artifact_template_records_identity_without_filename_token() -> None:
    blank = _read_asset("templates/artifacts/blank.md")

    assert 'template: "blank"' in blank
    assert "filename token ではありません" in blank
    assert "`blank` を含める必要はありません" in blank


def test_adr_artifact_template_supports_accepted_authority_and_mirror_surfaces() -> None:
    adr = _read_asset("templates/artifacts/adr.md")
    frontmatter = adr.split("---", 2)[1]

    for expected in (
        '状態: "draft"',
        'authority: "draft"',
        "accepted_authority: \"\"",
        "accepted_at: \"\"",
        "accepted_by: \"\"",
        "mirror_eligible: false",
    ):
        assert expected in frontmatter

    for expected in (
        '状態: "accepted"',
        '`authority: "accepted"`',
        "`accepted_authority: \"accepted ADR\"`",
        "`accepted_at: \"YYYY-MM-DD\"`",
        "`accepted_by: \"<DECISION_OWNER>\"`",
        "`mirror_eligible: true`",
        "accepted_authority",
        "artifacts/",
        "discussions/",
    ):
        assert expected in adr


def test_templates_readme_documents_future_artifact_catalog_and_legacy_routing() -> None:
    readme = _read_asset("templates/README.md")

    for expected in (
        "future `new artifact` catalog",
        "templates/artifacts",
        "draft-requirement",
        "draft-design",
        "draft-plan",
        "templates/issue-profiles/<profile>/design.md",
        "plan.md` を source として render",
        "Issue scope only",
        "unsupported",
        "no-write fail-closed",
        "scratch` は legacy-only",
        "future artifact catalog には追加しません",
        "filename に `blank` token を要求しません",
        "legacy `discussions/`",
        "preservation / legacy surface",
    ):
        assert expected in readme


def test_initiative_and_epic_artifact_rules_document_issue_only_draft_fail_closed_boundary() -> None:
    for scope in ("initiative", "epic"):
        rules = _read_asset(f"docs/rules/{scope}/artifacts.md")

        for expected in (
            "artifacts/",
            "Canonical `requirement.md` / `design.md` / `plan.md` / `report.md` は artifacts ではありません",
            "Legacy `discussions/` は preservation surface",
            "ADR originals may live under future `artifacts/` or legacy `discussions/`",
            "ADR mirror collection must collect both",
            "Direct artifact template catalog",
            "Unsupported issue-only draft artifact types",
            "draft-requirement",
            "draft-design",
            "draft-plan",
            "unsupported",
            "no-write fail-closed",
            "issue-only",
            "scratch` is legacy-only",
            "not part of the future `new artifact` catalog",
        ):
            assert expected in rules

        assert "templates/issue-profiles/<profile>" not in rules


def test_issue_artifact_rules_document_profile_aware_draft_fail_closed_routing() -> None:
    rules = _read_asset("docs/rules/issue/artifacts.md")

    for expected in (
        "Routing-only issue-only artifact types",
        "draft-requirement",
        "draft-design",
        "draft-plan",
        "templates/issue-profiles/<profile>/design.md",
        "templates/issue-profiles/<profile>/plan.md",
        "authorized_profile",
        "no-write fail-closed",
        "issue-only",
    ):
        assert expected in rules
