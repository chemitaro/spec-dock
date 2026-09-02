from pathlib import Path
import re

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
PROVIDER_ASSET_ROOT = REPO_ROOT / "src/spec_dock/assets/spec_dock"
DOGFOOD_ASSET_ROOT = REPO_ROOT / "spec-dock"
ARTIFACT_TEMPLATE_DIRECTORY = Path("templates/artifacts")
ARTIFACT_GUIDE = Path("docs/authoring/artifacts.md")

CURRENT_ARTIFACT_TYPES = (
    "blank",
    "research",
    "interview",
    "disc",
    "decision-candidate",
    "adr",
)
PHYSICAL_ARTIFACT_TEMPLATES = {
    *(f"{artifact_type}.md" for artifact_type in CURRENT_ARTIFACT_TYPES),
}


def _read_asset(root: Path, relative_path: Path | str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def _section(content: str, heading: str) -> str:
    match = re.search(
        rf"^{re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)",
        content,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match is not None, f"missing section: {heading}"
    return match.group("body")


def _frontmatter(content: str) -> str:
    match = re.match(r"\A---\n(?P<body>.*?)\n---\n", content, flags=re.DOTALL)
    assert match is not None, "missing YAML frontmatter"
    return match.group("body")


def _current_catalog_types(guide: str) -> tuple[str, ...]:
    section = _section(guide, "## Current creation catalog")
    return tuple(re.findall(r"^\| `([^`]+)` \|", section, flags=re.MULTILINE))


def _relative_markdown_links(content: str) -> tuple[str, ...]:
    destinations = re.findall(r"\[[^\]]*\]\(([^)]+)\)", content)
    relative_paths: list[str] = []
    for destination in destinations:
        path_without_fragment = destination.strip().strip("<>").split(maxsplit=1)[0].split("#", 1)[0]
        if path_without_fragment and not path_without_fragment.startswith("/") and "://" not in path_without_fragment:
            relative_paths.append(path_without_fragment)
    return tuple(relative_paths)


def test_physical_catalog_current_catalog_is_exact_six() -> None:
    physical_template_names = {path.name for path in (PROVIDER_ASSET_ROOT / ARTIFACT_TEMPLATE_DIRECTORY).glob("*.md")}
    guide = _read_asset(PROVIDER_ASSET_ROOT, ARTIFACT_GUIDE)

    assert physical_template_names == PHYSICAL_ARTIFACT_TEMPLATES
    current_catalog_types = _current_catalog_types(guide)
    assert len(current_catalog_types) == len(CURRENT_ARTIFACT_TYPES)
    assert set(current_catalog_types) == set(CURRENT_ARTIFACT_TYPES)


@pytest.mark.parametrize("artifact_type", CURRENT_ARTIFACT_TYPES)
def test_current_artifact_templates_exist_are_nonempty_and_match_dogfood(
    artifact_type: str,
) -> None:
    relative_path = ARTIFACT_TEMPLATE_DIRECTORY / f"{artifact_type}.md"
    provider_bytes = (PROVIDER_ASSET_ROOT / relative_path).read_bytes()

    assert provider_bytes.strip()
    assert provider_bytes == (DOGFOOD_ASSET_ROOT / relative_path).read_bytes()


def test_artifact_guide_exists_is_nonempty_and_matches_dogfood() -> None:
    provider_bytes = (PROVIDER_ASSET_ROOT / ARTIFACT_GUIDE).read_bytes()

    assert provider_bytes.strip()
    assert provider_bytes == (DOGFOOD_ASSET_ROOT / ARTIFACT_GUIDE).read_bytes()


@pytest.mark.parametrize(
    ("artifact_type", "expected_tokens"),
    (
        ("blank", ("自由形式", "事実、メモ、図、リンク", "## Evidence")),
        (
            "research",
            ("一つの source-grounded investigation", "## Source", "複数の証拠", "`disc`"),
        ),
        ("interview", ("明示的な質問と回答", "## Question", "## Answer", "自動で採用されません")),
        ("disc", ("複数の証拠", "trade-off", "一つの source", "`research`")),
        ("decision-candidate", ("未採用", "durable authority ではありません", "## Candidate")),
        ("adr", ("architecture / contract / migration", "明示的に `accepted`", "durable authority")),
    ),
)
def test_current_artifact_templates_distinguish_type_semantics(
    artifact_type: str,
    expected_tokens: tuple[str, ...],
) -> None:
    content = _read_asset(
        PROVIDER_ASSET_ROOT,
        ARTIFACT_TEMPLATE_DIRECTORY / f"{artifact_type}.md",
    )

    for token in expected_tokens:
        assert token in content


def test_blank_template_identity_does_not_constrain_filename_or_format() -> None:
    blank = _read_asset(PROVIDER_ASSET_ROOT, ARTIFACT_TEMPLATE_DIRECTORY / "blank.md")

    assert 'template: "blank"' in blank
    assert "filename token ではありません" in blank
    assert "`blank` を含める必要はありません" in blank


@pytest.mark.parametrize("artifact_type", CURRENT_ARTIFACT_TYPES[:-1])
def test_non_adr_artifacts_route_adopted_content_to_durable_authority(
    artifact_type: str,
) -> None:
    content = _read_asset(
        PROVIDER_ASSET_ROOT,
        ARTIFACT_TEMPLATE_DIRECTORY / f"{artifact_type}.md",
    )

    assert "Requirement / Design / Plan または accepted ADR に再記述" in content


def test_adr_defaults_to_draft_and_preserves_accepted_mirror_fields() -> None:
    adr = _read_asset(PROVIDER_ASSET_ROOT, ARTIFACT_TEMPLATE_DIRECTORY / "adr.md")
    frontmatter = _frontmatter(adr)

    for expected in (
        '状態: "draft"',
        'authority: "draft"',
        'accepted_authority: ""',
        'accepted_at: ""',
        'accepted_by: ""',
        "mirror_eligible: false",
    ):
        assert expected in frontmatter

    for accepted_field in (
        '状態: "accepted"',
        '`authority: "accepted"`',
        '`accepted_authority: "accepted ADR"`',
        '`accepted_at: "YYYY-MM-DD"`',
        '`accepted_by: "<DECISION_OWNER>"`',
        "`mirror_eligible: true`",
    ):
        assert accepted_field in adr
    assert "accepted ADR の mirror source" in adr
    assert "artifacts/" in adr
    assert "discussions/" in adr


def test_artifact_guide_fixes_type_meanings_and_research_disc_boundary() -> None:
    guide = _read_asset(PROVIDER_ASSET_ROOT, ARTIFACT_GUIDE)
    current_catalog = _section(guide, "## Current creation catalog")

    expected_meanings = {
        "blank": ("自由形式", "Requirement / Design / Plan", "accepted ADR"),
        "research": ("一つの source-grounded investigation", "facts / constraints"),
        "interview": ("明示的な質問と回答", "採用する回答"),
        "disc": ("複数の evidence", "trade-off"),
        "decision-candidate": ("未採用", "明示的な判断後"),
        "adr": ("architecture decision candidate / record", "accepted", "durable authority"),
    }
    for artifact_type, tokens in expected_meanings.items():
        row = next(line for line in current_catalog.splitlines() if line.startswith(f"| `{artifact_type}` |"))
        for token in tokens:
            assert token in row

    assert "`research` は一つの source" in current_catalog
    assert "複数の source や回答を統合" in current_catalog
    assert "`disc` を使います" in current_catalog


def test_artifact_guide_preserves_durable_authority_flow() -> None:
    guide = _read_asset(PROVIDER_ASSET_ROOT, ARTIFACT_GUIDE)
    authority_flow = _section(guide, "## Authority flow")
    flow_block = re.search(r"```text\n(?P<flow>.*?)\n```", authority_flow, flags=re.DOTALL)

    assert flow_block is not None
    assert flow_block.group("flow").splitlines() == [
        "Artifact evidence",
        "  -> 人間または agent による synthesis / review",
        "    -> Requirement / Design / Plan または accepted ADR",
        "      -> implementation",
        "        -> thin Report result summary",
    ]


def test_artifact_guide_rejects_automatic_promotion_of_evidence_and_report() -> None:
    guide = _read_asset(PROVIDER_ASSET_ROOT, ARTIFACT_GUIDE)
    authority_flow = _section(guide, "## Authority flow")

    for evidence_source in ("Artifact", "外部 ZIP", "delegated draft", "ChatGPT output", "Report"):
        assert evidence_source in authority_flow
    assert "自動で durable authority に昇格せず" in authority_flow
    assert "Report は durable decision store でもありません" in authority_flow
    assert "正本へ明示的に再記述" in authority_flow


def test_draft_document_state_and_adr_draft_authority_are_not_historical_routes() -> None:
    guide = _read_asset(PROVIDER_ASSET_ROOT, ARTIFACT_GUIDE)

    assert "初期状態としての `draft`" in _section(guide, "## Historical retention")
    for artifact_type in CURRENT_ARTIFACT_TYPES:
        content = _read_asset(
            PROVIDER_ASSET_ROOT,
            ARTIFACT_TEMPLATE_DIRECTORY / f"{artifact_type}.md",
        )
        assert '状態: "draft"' in _frontmatter(content)
    assert 'authority: "draft"' in _frontmatter(
        _read_asset(PROVIDER_ASSET_ROOT, ARTIFACT_TEMPLATE_DIRECTORY / "adr.md")
    )


@pytest.mark.parametrize("root", (PROVIDER_ASSET_ROOT, DOGFOOD_ASSET_ROOT))
def test_relative_links_in_artifact_guide_resolve_when_present(root: Path) -> None:
    guide_path = root / ARTIFACT_GUIDE

    for relative_path in _relative_markdown_links(guide_path.read_text(encoding="utf-8")):
        assert (guide_path.parent / relative_path).is_file(), f"broken relative link: {relative_path}"


def test_templates_readme_explains_template_guide_usage() -> None:
    readme = _read_asset(PROVIDER_ASSET_ROOT, "templates/README.md")

    assert "各テンプレートは対応する Guide を参照して記入する" in readme


def test_current_initiative_and_epic_artifact_rules_keep_historical_types_non_creatable() -> None:
    for scope in ("initiative", "epic"):
        rules = _read_asset(PROVIDER_ASSET_ROOT, f"docs/rules/{scope}/artifacts.md")

        for expected in (
            "artifacts/",
            "Canonical `requirement.md` / `design.md` / `plan.md` / `report.md` は artifacts ではありません",
            "Legacy `discussions/` は preservation surface",
            "ADR originals may live under Current `artifacts/` or legacy `discussions/`",
            "ADR mirror collection must collect both",
            "Direct artifact template catalog",
            "Historical-only types",
            "pr-repair-batch",
            "draft-requirement",
            "draft-design",
            "draft-plan",
            "Currentの新規作成catalogには含めません",
        ):
            assert expected in rules


def test_current_issue_artifact_rules_keep_profile_routes_historical_only() -> None:
    rules = _read_asset(PROVIDER_ASSET_ROOT, "docs/rules/issue/artifacts.md")

    for expected in (
        "Historical-only types",
        "pr-repair-batch",
        "draft-requirement",
        "draft-design",
        "draft-plan",
        ".assurance.json",
        "Currentの新規作成catalogやtemplate routingには含めません",
    ):
        assert expected in rules
