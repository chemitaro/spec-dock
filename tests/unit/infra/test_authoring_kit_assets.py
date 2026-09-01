from collections.abc import Mapping
from pathlib import Path
import re
from typing import TypedDict, cast

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
DOCS_ROOT = REPO_ROOT / "src" / "spec_dock" / "assets" / "spec_dock" / "docs"
AUTHORING_ROOT = DOCS_ROOT / "authoring"
DOGFOOD_DOCS_ROOT = REPO_ROOT / "spec-dock" / "docs"
TEMPLATES_ROOT = DOCS_ROOT.parent / "templates"
DOGFOOD_TEMPLATES_ROOT = DOGFOOD_DOCS_ROOT.parent / "templates"
REPOSITORY_GUIDELINES_PATH = REPO_ROOT / "AGENTS.md"

OVERVIEW_LINK_TARGETS = (
    "requirement.md",
    "design.md",
    "issue-plan.md",
    "report.md",
    "scope-layering.md",
    "artifacts.md",
)

STORAGE_CORE_REFERENCE_TARGETS = frozenset({
    "reference_naming.md",
    "reference_deps.md",
    "reference_sync.md",
    "reference_github.md",
})
CURRENT_FIRST_READ_DESTINATIONS = frozenset({
    *STORAGE_CORE_REFERENCE_TARGETS,
    "migration.md",
    "authoring/overview.md",
})
REFERENCE_USE_DESTINATION_PREFIX = "reference-use:"

S06_CURRENT_ASSET_PATHS = (
    "docs/README.md",
    "docs/guide.md",
    "docs/migration.md",
    "docs/authoring/overview.md",
    "templates/README.md",
)
S06_HISTORICAL_ASSET_PATH = "docs/authoring/historical.md"
S06_MANAGED_ASSET_PATHS = (*S06_CURRENT_ASSET_PATHS, S06_HISTORICAL_ASSET_PATH)


RESERVED_SKILL_PATHS = (
    ".agents/skills/spec-dock/SKILL.md",
    ".agents/skills/spec-dock-grill-with-docs/SKILL.md",
)

CURRENT_ARTIFACT_TEMPLATES = (
    "blank",
    "research",
    "interview",
    "disc",
    "decision-candidate",
    "adr",
)

S07_OWNED_ASSET_CATEGORIES = {
    "scope-templates": (
        "templates/initiative/requirement.md",
        "templates/initiative/design.md",
        "templates/initiative/plan.md",
        "templates/initiative/report.md",
        "templates/epic/requirement.md",
        "templates/epic/design.md",
        "templates/epic/plan.md",
        "templates/epic/report.md",
        "templates/issue/requirement.md",
        "templates/issue/design.md",
        "templates/issue/plan.md",
        "templates/issue/report.md",
    ),
    "current-artifact-templates": (
        "templates/artifacts/blank.md",
        "templates/artifacts/research.md",
        "templates/artifacts/interview.md",
        "templates/artifacts/disc.md",
        "templates/artifacts/decision-candidate.md",
        "templates/artifacts/adr.md",
    ),
    "navigation-roots": (
        "templates/README.md",
        "docs/README.md",
        "docs/guide.md",
        "docs/migration.md",
    ),
    "base-authoring-guides": (
        "docs/authoring/issue-plan.md",
        "docs/authoring/scope-layering.md",
    ),
    "current-authoring-guides": (
        "docs/authoring/overview.md",
        "docs/authoring/requirement.md",
        "docs/authoring/design.md",
        "docs/authoring/report.md",
        "docs/authoring/artifacts.md",
        "docs/authoring/historical.md",
    ),
    "planning-level-guides": (
        "docs/authoring/issue-plan-levels/light.md",
        "docs/authoring/issue-plan-levels/standard.md",
        "docs/authoring/issue-plan-levels/strict.md",
        "docs/authoring/issue-plan-levels/critical.md",
    ),
}
S07_OWNED_ASSET_MANIFEST = tuple(
    path for category_paths in S07_OWNED_ASSET_CATEGORIES.values() for path in category_paths
)
S07_PARITY_EXCLUDED_SURFACES = ("tests/unit/infra/test_authoring_kit_assets.py",)

DOCUMENT_RESPONSIBILITIES = {
    "requirement.md": {
        "owns": ("problem", "stakeholder / user outcome", "受け入れ条件"),
        "does_not_own": ("設計詳細", "実装順序"),
    },
    "design.md": {
        "owns": ("Current と Target architecture", "failure contract", "testability"),
        "does_not_own": ("acceptance の再定義", "実装 task の順序"),
    },
    "issue-plan.md": {
        "owns": ("Planning Level", "implementation sequence", "verification strategy", "rollback"),
        "does_not_own": ("acceptance の再定義", "責務境界", "進捗日誌"),
    },
    "report.md": {
        "owns": ("Outcome:", "Verification:", "Residual Risks / Follow-ups:"),
        "does_not_own": ("durable decision の唯一の記録", "仕様本文", "利用記録を必須"),
    },
}

SCOPE_AWARE_PLAN_ROUTING = {
    "requirement.md": (
        "Issue の実装と検証の順序",
        "Initiative / Epic の Plan 責務",
        "各 scope の `plan.md`",
    ),
    "design.md": (
        "Issue の実装順序や verification",
        "Initiative / Epic の Plan 責務",
        "各 scope の `plan.md`",
    ),
    "report.md": (
        "Issue では",
        "Initiative / Epic では",
        "各 scope の `plan.md`",
    ),
}

FOUNDATION_DOCS = (
    "overview.md",
    "requirement.md",
    "design.md",
    "issue-plan.md",
    "report.md",
    "scope-layering.md",
)

S01_OWNED_DOC_PATHS = (
    "README.md",
    "guide.md",
    "authoring/overview.md",
    "authoring/requirement.md",
    "authoring/design.md",
    "authoring/issue-plan.md",
    "authoring/report.md",
    "authoring/scope-layering.md",
)

SCOPES = ("initiative", "epic", "issue")
RDP_DOCUMENTS = ("requirement", "design", "plan")
SCOPE_TEMPLATE_MARKDOWN_FILES = frozenset({
    "requirement.md",
    "design.md",
    "plan.md",
    "report.md",
})

TEMPLATE_HEADINGS = {
    "requirement": (
        "目的",
        "背景",
        "観測可能な要件",
        "スコープ",
        "失敗・境界条件",
        "受け入れ条件",
        "制約・前提",
    ),
    "design": (
        "設計目標",
        "Current / Target",
        "責務・Interface",
        "data / failure",
        "変更対象",
        "移行・互換性・rollback",
        "testability",
        "risk",
    ),
    "plan": (
        "目標",
        "順序・依存",
        "実装step",
        "検証",
        "rollback",
        "exit / handoff",
    ),
}


class ScopeTemplateContract(TypedDict):
    id: str
    title: str
    parent: str | None
    guide_prefix: str
    node_parts: tuple[str, ...]


class DocumentTemplateContract(TypedDict):
    kind: str
    dependencies: str | None
    guide: str | None


SCOPE_TEMPLATE_CONTRACTS: dict[str, ScopeTemplateContract] = {
    "initiative": {
        "id": "<INIT_ID>",
        "title": "<INIT_TITLE>",
        "parent": None,
        "guide_prefix": "../../docs/authoring/",
        "node_parts": ("initiatives", "init-test"),
    },
    "epic": {
        "id": "<EPIC_ID>",
        "title": "<EPIC_TITLE>",
        "parent": '["<INIT_ID>"]',
        "guide_prefix": "../../../../docs/authoring/",
        "node_parts": ("initiatives", "init-test", "epics", "epic-test"),
    },
    "issue": {
        "id": "<ISS_ID>",
        "title": "<ISS_TITLE>",
        "parent": '["<EPIC_ID>", "<INIT_ID>"]',
        "guide_prefix": "../../../../../../docs/authoring/",
        "node_parts": (
            "initiatives",
            "init-test",
            "epics",
            "epic-test",
            "issues",
            "iss-test",
        ),
    },
}

DOCUMENT_TEMPLATE_CONTRACTS: dict[str, DocumentTemplateContract] = {
    "requirement": {
        "kind": "要件定義書",
        "dependencies": None,
        "guide": "requirement.md",
    },
    "design": {
        "kind": "設計書",
        "dependencies": '["requirement.md"]',
        "guide": "design.md",
    },
    "plan": {
        "kind": "計画書",
        "dependencies": '["requirement.md", "design.md"]',
        "guide": None,
    },
}

REPORT_REQUIRED_HEADINGS = (
    "Outcome",
    "Verification",
    "Residual Risks / Follow-ups",
)

PLANNING_LEVELS = ("light", "standard", "strict", "critical")
PLANNING_LEVELS_ROOT = AUTHORING_ROOT / "issue-plan-levels"
PLANNING_LEVEL_GUIDE_HEADINGS = (
    "完成時の状態",
    "検証とnegative test",
    "rollback / migration",
    "security / privacy / operability",
    "escalation trigger",
)
PLANNING_LEVEL_COMPLETION_TOKENS = {
    "light": (
        "targeted verification",
        "失敗入力",
        "revert",
        "N/A",
        "security",
        "privacy",
        "operability",
        "public contract",
    ),
    "standard": (
        "end-to-end verification",
        "negative test",
        "rollback",
        "N/A",
        "security",
        "privacy",
        "operability",
        "public contract",
    ),
    "strict": (
        "end-to-end verification",
        "compatibility",
        "failure mode",
        "migration failure",
        "forward recovery",
        "N/A",
        "observability",
        "critical",
    ),
    "critical": (
        "end-to-end verification",
        "negative test",
        "failure injection",
        "backup / restore",
        "kill switch",
        "incident response",
        "N/A",
        "auditability",
    ),
}

PLANNING_LEVEL_EXAMPLES = {
    "LEVEL-EX-POS-01": ("局所的", "revert", "`light` 候補"),
    "LEVEL-EX-POS-02": ("public contract", "回復が難しい", "`strict` 候補"),
    "LEVEL-EX-POS-03": ("security / privacy", "不可逆", "`critical` 候補"),
    "LEVEL-EX-NEG-01": ("Priority", "level を上げる根拠にしない"),
    "LEVEL-EX-NEG-02": ("工数", "dependency blocker", "level を上げる根拠にしない"),
    "LEVEL-EX-NEG-03": ("Severity label", "impact / recovery", "label だけでは決めない"),
}


def _read_authoring_doc(name: str) -> str:
    return (AUTHORING_ROOT / name).read_text(encoding="utf-8")


def _section(content: str, heading: str) -> str:
    match = re.search(
        rf"^{re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)",
        content,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match is not None, f"missing section: {heading}"
    return match.group("body")


def _section_list(content: str, heading: str) -> str:
    return "\n".join(line for line in _section(content, heading).splitlines() if line.startswith("- "))


def _normalize_markdown_destination(raw_destination: str) -> str:
    raw_destination = raw_destination.strip()
    if raw_destination.startswith("<") and ">" in raw_destination:
        return raw_destination[1 : raw_destination.index(">")]
    return raw_destination.split(maxsplit=1)[0]


def _markdown_link_destinations(content: str) -> tuple[str, ...]:
    inline_destinations = (
        _normalize_markdown_destination(raw_destination)
        for raw_destination in re.findall(r"\[[^\]]*\]\(([^)]+)\)", content)
    )
    reference_uses = (
        f"{REFERENCE_USE_DESTINATION_PREFIX}{match.group('identifier') or match.group('label')}"
        for match in re.finditer(
            r"\[(?P<label>[^\]\n]+)\]\[(?P<identifier>[^\]\n]*)\]",
            content,
        )
    )
    reference_destinations = (
        _normalize_markdown_destination(match.group("destination"))
        for match in re.finditer(
            r"^[ \t]{0,3}\[[^\]]+\]:[ \t]*(?P<destination><[^>\n]+>|[^\s]+)",
            content,
            flags=re.MULTILINE,
        )
    )
    autolink_destinations = (
        match.group("destination")
        for match in re.finditer(
            r"<(?P<destination>(?:[A-Za-z][A-Za-z0-9+.-]*:[^>\s]+|/[^>\s]+|[^<>\s@]+@[^<>\s@]+))>",
            content,
        )
    )
    return (*inline_destinations, *reference_uses, *reference_destinations, *autolink_destinations)


def _relative_markdown_links(content: str) -> tuple[str, ...]:
    relative_paths: list[str] = []
    for destination in _markdown_link_destinations(content):
        if destination.startswith(REFERENCE_USE_DESTINATION_PREFIX):
            continue
        path_without_fragment = destination.split("#", maxsplit=1)[0]
        if not path_without_fragment:
            continue
        if path_without_fragment.startswith("/") or "://" in path_without_fragment:
            continue
        relative_paths.append(path_without_fragment)
    return tuple(relative_paths)


def _has_exact_current_first_read_destinations(content: str) -> bool:
    return set(_markdown_link_destinations(content)) == CURRENT_FIRST_READ_DESTINATIONS


def _read_template(scope: str, document: str) -> str:
    return (TEMPLATES_ROOT / scope / f"{document}.md").read_text(encoding="utf-8")


def _has_exact_scope_template_catalog(filenames: set[str]) -> bool:
    return filenames == SCOPE_TEMPLATE_MARKDOWN_FILES


def _frontmatter(content: str) -> dict[str, str]:
    match = re.match(r"\A---\n(?P<body>.*?)\n---\n", content, flags=re.DOTALL)
    assert match is not None, "missing YAML frontmatter"

    fields: dict[str, str] = {}
    for line in match.group("body").splitlines():
        key, separator, value = line.partition(":")
        assert separator and key and value.strip(), f"invalid frontmatter line: {line}"
        assert key not in fields, f"duplicate frontmatter key: {key}"
        fields[key] = value.strip()
    return fields


def _template_section_prompt(content: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)",
        content,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match is not None, f"missing template section: {heading}"
    lines = [line for line in match.group("body").splitlines() if line.strip()]
    assert len(lines) == 1, f"{heading} must contain exactly one prompt line"
    return lines[0]


def _template_section_body(content: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)",
        content,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match is not None, f"missing template section: {heading}"
    return match.group("body")


def _render_template(content: str) -> str:
    replacements = {
        "<INIT_ID>": "init-test",
        "<INIT_TITLE>": "Initiative Test",
        "<EPIC_ID>": "epic-test",
        "<EPIC_TITLE>": "Epic Test",
        "<ISS_ID>": "iss-test",
        "<ISS_TITLE>": "Issue Test",
        "<GITHUB_ISSUE_NUMBER_OR_URL>": "358",
        "YYYY-MM-DD": "2026-08-10",
    }
    rendered = content
    for placeholder, value in replacements.items():
        rendered = rendered.replace(placeholder, value)
    return rendered


def _owned_manifest_delta(candidate: tuple[str, ...]) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    expected = set(S07_OWNED_ASSET_MANIFEST)
    actual = set(candidate)
    missing = tuple(path for path in S07_OWNED_ASSET_MANIFEST if path not in actual)
    extra = tuple(path for path in candidate if path not in expected)
    duplicates = tuple(path for path in candidate if candidate.count(path) > 1)
    return missing, extra, tuple(dict.fromkeys(duplicates))


def _projection_violations(
    manifest: tuple[str, ...],
    provider_root: Path,
    dogfood_root: Path,
) -> tuple[str, ...]:
    violations: list[str] = []
    for relative_path in manifest:
        provider_path = provider_root / relative_path
        dogfood_path = dogfood_root / relative_path
        if not provider_path.is_file():
            violations.append(f"missing provider: {relative_path}")
        if not dogfood_path.is_file():
            violations.append(f"missing dogfood: {relative_path}")
        if (
            provider_path.is_file()
            and dogfood_path.is_file()
            and provider_path.read_bytes() != dogfood_path.read_bytes()
        ):
            violations.append(f"byte drift: {relative_path}")
    return tuple(violations)


def _relative_link_violations(manifest: tuple[str, ...], scaffold_root: Path) -> tuple[str, ...]:
    violations: list[str] = []
    for relative_path in manifest:
        asset_path = scaffold_root / relative_path
        if not asset_path.is_file():
            continue

        content = asset_path.read_text(encoding="utf-8")
        path_parts = Path(relative_path).parts
        if len(path_parts) == 3 and path_parts[0] == "templates" and path_parts[1] in SCOPE_TEMPLATE_CONTRACTS:
            scope = path_parts[1]
            content = _render_template(content)
            link_base = scaffold_root.joinpath(*SCOPE_TEMPLATE_CONTRACTS[scope]["node_parts"])
        else:
            link_base = asset_path.parent

        for target in _relative_markdown_links(content):
            if not (link_base / target).resolve().is_file():
                violations.append(f"broken relative link: {relative_path} -> {target}")
    return tuple(violations)


def test_s07_parity_owned_asset_manifest_is_exact_and_explicit() -> None:
    assert {category: len(paths) for category, paths in S07_OWNED_ASSET_CATEGORIES.items()} == {
        "scope-templates": 12,
        "current-artifact-templates": 6,
        "navigation-roots": 4,
        "base-authoring-guides": 2,
        "current-authoring-guides": 6,
        "planning-level-guides": 4,
    }
    assert len(S07_OWNED_ASSET_MANIFEST) == 34
    assert _owned_manifest_delta(S07_OWNED_ASSET_MANIFEST) == ((), (), ())
    assert S07_PARITY_EXCLUDED_SURFACES == ("tests/unit/infra/test_authoring_kit_assets.py",)


def test_s07_parity_manifest_rejects_missing_extra_and_duplicate_rows() -> None:
    missing_row = S07_OWNED_ASSET_MANIFEST[1:]
    duplicate_row = (*S07_OWNED_ASSET_MANIFEST, S07_OWNED_ASSET_MANIFEST[0])

    assert _owned_manifest_delta(missing_row)[0] == (S07_OWNED_ASSET_MANIFEST[0],)
    for extra_path in S07_PARITY_EXCLUDED_SURFACES:
        extra_row = (*S07_OWNED_ASSET_MANIFEST, extra_path)
        assert _owned_manifest_delta(extra_row)[1] == (extra_path,)
    assert _owned_manifest_delta(duplicate_row)[2] == (S07_OWNED_ASSET_MANIFEST[0],)


def test_s07_parity_owned_assets_exist_and_match_dogfood_projection_byte_exact() -> None:
    assert not _projection_violations(
        S07_OWNED_ASSET_MANIFEST,
        DOCS_ROOT.parent,
        DOGFOOD_DOCS_ROOT.parent,
    )


def test_s07_parity_detector_rejects_byte_drift(tmp_path: Path) -> None:
    provider_root = tmp_path / "provider"
    dogfood_root = tmp_path / "dogfood"
    relative_path = "docs/authoring/example.md"
    for root in (provider_root, dogfood_root):
        asset_path = root / relative_path
        asset_path.parent.mkdir(parents=True)
        asset_path.write_bytes(b"same\n")
    (dogfood_root / relative_path).write_bytes(b"drift\n")

    assert _projection_violations((relative_path,), provider_root, dogfood_root) == (f"byte drift: {relative_path}",)


@pytest.mark.parametrize("scaffold_root", (DOCS_ROOT.parent, DOGFOOD_DOCS_ROOT.parent))
def test_s07_all_owned_asset_relative_links_resolve(scaffold_root: Path) -> None:
    assert not _relative_link_violations(S07_OWNED_ASSET_MANIFEST, scaffold_root)


def test_s07_relative_link_detector_rejects_broken_link(tmp_path: Path) -> None:
    relative_path = "docs/authoring/example.md"
    asset_path = tmp_path / relative_path
    asset_path.parent.mkdir(parents=True)
    asset_path.write_text("[missing](missing.md)\n", encoding="utf-8")

    assert _relative_link_violations((relative_path,), tmp_path) == (
        f"broken relative link: {relative_path} -> missing.md",
    )


def test_authoring_overview_links_to_each_foundation_guide() -> None:
    overview_path = AUTHORING_ROOT / "overview.md"
    overview = overview_path.read_text(encoding="utf-8")
    relative_links = set(_relative_markdown_links(overview))

    for target in OVERVIEW_LINK_TARGETS:
        assert target in relative_links
        assert (overview_path.parent / target).is_file()


@pytest.mark.parametrize("name", ("README.md", "guide.md"))
def test_current_navigation_roots_link_to_authoring_overview(name: str) -> None:
    navigation_path = DOCS_ROOT / name
    relative_links = set(_relative_markdown_links(navigation_path.read_text(encoding="utf-8")))

    assert "authoring/overview.md" in relative_links
    assert (navigation_path.parent / "authoring/overview.md").is_file()


@pytest.mark.parametrize("name", ("README.md", "guide.md"))
def test_current_navigation_first_read_route_is_storage_core_and_authoring_kit(name: str) -> None:
    content = (DOCS_ROOT / name).read_text(encoding="utf-8")
    current = _section(content, "## Current")
    historical = _section(content, "## Historical")

    assert content.index("## Current") < content.index("## Historical")
    assert _has_exact_current_first_read_destinations(current)
    assert "authoring/historical.md" not in _markdown_link_destinations(current)
    assert _markdown_link_destinations(historical) == ("authoring/historical.md",)
    assert "Current の新規作成手順ではありません" in historical


@pytest.mark.parametrize(
    "extra_link",
    (
        "[absolute workflow](/workflow_issue.md)",
        "[external workflow](https://example.com/workflow_issue.md)",
        "[reserved skill][skill]\n[skill]: </.agents/skills/spec-dock/SKILL.md>",
        "<https://example.com/current-authoring>",
        "<mailto:author@example.com>",
        "<ftp://example.com/current-authoring>",
        "<author@example.com>",
        "[Current recommendation][current]\n[current]: ../overview.md",
    ),
)
def test_current_navigation_first_read_destination_detector_rejects_non_allowlisted_mutations(
    extra_link: str,
) -> None:
    current = "\n".join((
        *(f"[{destination}]({destination})" for destination in CURRENT_FIRST_READ_DESTINATIONS),
        extra_link,
    ))

    assert not _has_exact_current_first_read_destinations(current)


def test_current_navigation_first_read_rejects_reference_use_when_definition_is_outside_section() -> None:
    current = "\n".join((
        *(f"[{destination}]({destination})" for destination in CURRENT_FIRST_READ_DESTINATIONS),
        "[external][x]",
    ))
    definition_outside_section = "[x]: <https://example.com/external>"

    assert f"{REFERENCE_USE_DESTINATION_PREFIX}x" in _markdown_link_destinations(current)
    assert "https://example.com/external" in _markdown_link_destinations(definition_outside_section)
    assert not _has_exact_current_first_read_destinations(current)


def test_authoring_overview_navigation_links_to_all_current_guides() -> None:
    overview_path = AUTHORING_ROOT / "overview.md"
    links = set(_markdown_link_destinations(overview_path.read_text(encoding="utf-8")))
    expected_links = {
        *OVERVIEW_LINK_TARGETS,
        *(f"issue-plan-levels/{level}.md" for level in PLANNING_LEVELS),
    }

    assert links == expected_links
    for relative_path in links:
        assert (overview_path.parent / relative_path).is_file(), f"broken overview link: {relative_path}"


def test_authoring_overview_agent_assistance_reserves_plain_text_skill_paths_without_live_links() -> None:
    overview = _read_authoring_doc("overview.md")
    assistance = _section(overview, "## Agent assistance")
    live_links = set(_markdown_link_destinations(assistance))

    for reserved_path in RESERVED_SKILL_PATHS:
        assert assistance.count(reserved_path) == 1
        assert reserved_path not in live_links
    assert not live_links


@pytest.mark.parametrize(
    "content",
    (
        "[skill](/.agents/skills/spec-dock/SKILL.md)",
        "[skill](https://example.com/.agents/skills/spec-dock/SKILL.md)",
        "[Current recommendation](../overview.md)",
        "[skill][reserved]\n[reserved]: </.agents/skills/spec-dock/SKILL.md>",
        "<https://example.com/current-authoring>",
        "<mailto:author@example.com>",
        "<ftp://example.com/current-authoring>",
        "<author@example.com>",
        "</.agents/skills/spec-dock/SKILL.md>",
        "[Current recommendation][current]\n[current]: ../overview.md",
    ),
)
def test_no_live_link_detector_rejects_absolute_external_and_relative_mutations(content: str) -> None:
    assert _markdown_link_destinations(content)


def test_relative_link_resolver_includes_reference_style_destination() -> None:
    content = "[Current recommendation][current]\n[current]: <../overview.md>"

    assert _relative_markdown_links(content) == ("../overview.md",)


def test_s90_retained_repository_guidelines_match_current_distribution_surface() -> None:
    content = REPOSITORY_GUIDELINES_PATH.read_text(encoding="utf-8")

    assert "src/spec_dock/assets/install_root/" in content
    assert ".agents/skills/spec-dock/SKILL.md" in content
    assert ".agents/skills/spec-dock-grill-with-docs/SKILL.md" in content
    assert ".github/workflows/ci.yml" in content
    assert ".codex/" not in content
    assert ".github/agents/" not in content
    assert "host adapter" not in content.lower()


@pytest.mark.parametrize("scaffold_root", (DOCS_ROOT.parent, DOGFOOD_DOCS_ROOT.parent))
@pytest.mark.parametrize("relative_path", S06_MANAGED_ASSET_PATHS)
def test_s06_navigation_asset_relative_links_resolve(scaffold_root: Path, relative_path: str) -> None:
    asset_path = scaffold_root / relative_path

    assert asset_path.is_file()
    assert asset_path.read_text(encoding="utf-8").strip()
    for target in _relative_markdown_links(asset_path.read_text(encoding="utf-8")):
        assert (asset_path.parent / target).is_file(), f"broken relative link in {relative_path}: {target}"


@pytest.mark.parametrize("relative_path", S06_MANAGED_ASSET_PATHS)
def test_s06_navigation_assets_match_dogfood_projection(relative_path: str) -> None:
    assert (DOCS_ROOT.parent / relative_path).read_bytes() == (DOGFOOD_DOCS_ROOT.parent / relative_path).read_bytes()


@pytest.mark.parametrize("relative_path", S01_OWNED_DOC_PATHS)
def test_s01_authoring_docs_match_dogfood_projection(relative_path: str) -> None:
    assert (DOCS_ROOT / relative_path).read_bytes() == (DOGFOOD_DOCS_ROOT / relative_path).read_bytes()


@pytest.mark.parametrize("name", FOUNDATION_DOCS)
def test_all_relative_markdown_links_in_authoring_foundation_resolve(name: str) -> None:
    document_path = AUTHORING_ROOT / name

    for relative_path in _relative_markdown_links(_read_authoring_doc(name)):
        assert (document_path.parent / relative_path).is_file(), f"broken relative link in {name}: {relative_path}"


@pytest.mark.parametrize(
    "name",
    FOUNDATION_DOCS,
)
def test_authoring_overview_and_document_guides_have_major_headings(name: str) -> None:
    content = _read_authoring_doc(name)

    assert content.strip()
    assert re.search(r"^# [^#\n]+", content, flags=re.MULTILINE)
    assert re.search(r"^## [^#\n]+", content, flags=re.MULTILINE)


@pytest.mark.parametrize(
    ("name", "responsibility"),
    DOCUMENT_RESPONSIBILITIES.items(),
)
def test_document_guides_distinguish_owned_and_unowned_content(
    name: str,
    responsibility: dict[str, tuple[str, ...]],
) -> None:
    content = _read_authoring_doc(name)
    owned_section = _section_list(content, "## この文書が扱うこと")
    unowned_section = _section_list(content, "## この文書に置かないこと")

    for token in responsibility["owns"]:
        assert token in owned_section
        assert token not in unowned_section
    for token in responsibility["does_not_own"]:
        assert token in unowned_section
        assert token not in owned_section


@pytest.mark.parametrize(("name", "routing_tokens"), SCOPE_AWARE_PLAN_ROUTING.items())
def test_document_guides_route_plan_authoring_by_scope(
    name: str,
    routing_tokens: tuple[str, ...],
) -> None:
    content = _read_authoring_doc(name)
    relative_links = set(_relative_markdown_links(content))
    routing_lines = [
        line for line in content.splitlines() if "(issue-plan.md)" in line and "(scope-layering.md)" in line
    ]

    assert {"issue-plan.md", "scope-layering.md"} <= relative_links
    assert len(routing_lines) == 1
    routing_line = routing_lines[0]
    for token in routing_tokens:
        assert token in routing_line
    assert "Planning Level" not in routing_line


def test_scope_layering_distinguishes_each_scope_and_preserves_parent_contracts() -> None:
    content = _read_authoring_doc("scope-layering.md")

    scope_tokens = {
        "Initiative": ("戦略的な problem / outcome", "投資境界"),
        "Epic": ("vertical Issue slice", "cross-Issue contract"),
        "Issue": ("end-to-end で観測できる価値", "具体的 acceptance"),
    }
    for scope, tokens in scope_tokens.items():
        assert scope in content
        for token in tokens:
            assert token in content

    assert "## 親 scope を再定義しない" in content
    assert "Issue の実装 micro-step" in content
    assert "Issue の Planning Level" in content
    assert "親 scope に戻して更新します" in content


def test_scope_layering_distinguishes_plan_responsibilities_by_scope() -> None:
    plan_section = _section(_read_authoring_doc("scope-layering.md"), "## Plan の責務")
    plan_lines = {
        scope: next(line for line in plan_section.splitlines() if line.startswith(f"- {scope} Plan"))
        for scope in ("Initiative", "Epic", "Issue")
    }

    for token in ("Epic を進める順序", "投資上の依存", "全体としての検証"):
        assert token in plan_lines["Initiative"]
    assert "Issue の implementation step は扱いません" in plan_lines["Initiative"]

    for token in ("Issue 分割", "統合する順序", "cross-Issue contract", "横断的な verification"):
        assert token in plan_lines["Epic"]
    assert "個別 Issue の実装 task を再掲しません" in plan_lines["Epic"]

    for token in ("implementation steps", "tests", "migration", "rollback", "handoff"):
        assert token in plan_lines["Issue"]
    assert "親の目的、Issue 分割、依存方向を変更しません" in plan_lines["Issue"]


@pytest.mark.parametrize("template_root", (TEMPLATES_ROOT, DOGFOOD_TEMPLATES_ROOT))
@pytest.mark.parametrize("scope", SCOPES)
def test_template_scope_markdown_catalog_is_exact(
    template_root: Path,
    scope: str,
) -> None:
    filenames = {path.name for path in (template_root / scope).glob("*.md") if path.is_file()}

    assert _has_exact_scope_template_catalog(filenames)


@pytest.mark.parametrize(
    "extra_filename",
    ("plan-light.md", "requirement-copy.md", "design-v2.md"),
)
def test_template_scope_catalog_rejects_extra_rdp_like_alias(extra_filename: str) -> None:
    mutated_catalog = set(SCOPE_TEMPLATE_MARKDOWN_FILES) | {extra_filename}

    assert not _has_exact_scope_template_catalog(mutated_catalog)


def test_template_readme_navigation_catalogs_exact_scope_docs_and_current_artifacts() -> None:
    content = (TEMPLATES_ROOT / "README.md").read_text(encoding="utf-8")
    links = set(_markdown_link_destinations(content))

    for scope in SCOPES:
        assert content.count(f"`{scope}/{{requirement,design,plan,report}}.md`") == 1
        assert f"`{scope}/{{requirement,design,plan}}.md`" not in content

    artifact_catalog = f"`artifacts/{{{','.join(CURRENT_ARTIFACT_TEMPLATES)}}}.md`"
    assert content.count(artifact_catalog) == 1
    for retired_route in ("analysis", "repair", "draft-"):
        assert retired_route not in content.casefold()

    assert links == {
        "../docs/authoring/overview.md",
        "../docs/authoring/requirement.md",
        "../docs/authoring/design.md",
        "../docs/authoring/issue-plan.md",
        "../docs/authoring/report.md",
        "../docs/authoring/artifacts.md",
    }
    for relative_path in links:
        assert (TEMPLATES_ROOT / relative_path).is_file(), f"broken template catalog link: {relative_path}"


@pytest.mark.parametrize(
    ("scope", "document"),
    ((scope, document) for scope in SCOPES for document in RDP_DOCUMENTS),
)
def test_template_rdp_frontmatter_uses_exact_minimal_fields_and_placeholders(
    scope: str,
    document: str,
) -> None:
    content = _read_template(scope, document)
    fields = _frontmatter(content)
    scope_contract = SCOPE_TEMPLATE_CONTRACTS[scope]
    document_contract = DOCUMENT_TEMPLATE_CONTRACTS[document]

    expected_keys = {"種別", "ID", "タイトル", "関連GitHub", "状態", "最終更新"}
    if document_contract["dependencies"] is not None:
        expected_keys.add("依存")
    if scope_contract["parent"] is not None:
        expected_keys.add("親")
    assert set(fields) == expected_keys

    scope_label = scope.capitalize()
    kind = document_contract["kind"]
    if document == "plan" and scope == "issue":
        kind = "実装計画書"
    assert fields["種別"] == f"{kind}（{scope_label}）"
    assert fields["ID"] == f'"{scope_contract["id"]}"'
    assert fields["タイトル"] == f'"{scope_contract["title"]}"'
    assert fields["関連GitHub"] == '["<GITHUB_ISSUE_NUMBER_OR_URL>"]'
    assert fields["状態"] == '"draft"'
    assert fields["最終更新"] == '"YYYY-MM-DD"'

    dependencies = document_contract["dependencies"]
    if dependencies is not None:
        assert fields["依存"] == dependencies
    parent = scope_contract["parent"]
    if parent is not None:
        assert fields["親"] == parent

    expected_placeholders = {
        scope_contract["id"],
        scope_contract["title"],
        "<GITHUB_ISSUE_NUMBER_OR_URL>",
    }
    if scope == "epic":
        expected_placeholders.add("<INIT_ID>")
    if scope == "issue":
        expected_placeholders.update(("<INIT_ID>", "<EPIC_ID>"))
    assert set(re.findall(r"<[A-Z_]+>", content)) == expected_placeholders

    rendered = _render_template(content)
    assert not re.search(r"<[A-Z_]+>", rendered)
    assert "YYYY-MM-DD" not in rendered


@pytest.mark.parametrize(
    ("scope", "document"),
    ((scope, document) for scope in SCOPES for document in RDP_DOCUMENTS),
)
def test_template_rdp_has_exact_headings_and_one_concise_prompt_per_section(
    scope: str,
    document: str,
) -> None:
    content = _read_template(scope, document)
    expected_headings = TEMPLATE_HEADINGS[document]
    if scope == "issue" and document == "plan":
        expected_headings = ("Planning Level", *expected_headings)

    assert tuple(re.findall(r"^## ([^\n]+)$", content, flags=re.MULTILINE)) == expected_headings
    assert not re.search(r"^### ", content, flags=re.MULTILINE)
    assert "<!--" not in content

    for heading in expected_headings:
        prompt = _template_section_prompt(content, heading)
        assert prompt.endswith("。")
        assert len(prompt) <= 100
        assert not prompt.startswith(("- ", "* ", "1. ", "```"))
        assert "..." not in prompt


@pytest.mark.parametrize(
    ("scope", "document"),
    ((scope, document) for scope in SCOPES for document in RDP_DOCUMENTS),
)
def test_template_rdp_guide_link_resolves_from_rendered_node_location(
    scope: str,
    document: str,
) -> None:
    scope_contract = SCOPE_TEMPLATE_CONTRACTS[scope]
    document_contract = DOCUMENT_TEMPLATE_CONTRACTS[document]
    guide = document_contract["guide"]
    if document == "plan":
        guide = "issue-plan.md" if scope == "issue" else "scope-layering.md"
    guide = cast("str", guide)
    expected_link = f"{scope_contract['guide_prefix']}{guide}"

    for template_root in (TEMPLATES_ROOT, DOGFOOD_TEMPLATES_ROOT):
        scaffold_root = template_root.parent
        content = _render_template((template_root / scope / f"{document}.md").read_text(encoding="utf-8"))
        assert _relative_markdown_links(content) == (expected_link,)

        node_path = scaffold_root.joinpath(*scope_contract["node_parts"], f"{document}.md")
        resolved_link = (node_path.parent / expected_link).resolve()
        expected_target = (scaffold_root / "docs" / "authoring" / guide).resolve()
        assert resolved_link == expected_target
        assert resolved_link.is_file()


def test_template_plan_routes_scope_guides_and_limits_planning_level_to_issue() -> None:
    for scope in SCOPES:
        content = _read_template(scope, "plan")
        links = _relative_markdown_links(content)
        if scope == "issue":
            assert links == ("../../../../../../docs/authoring/issue-plan.md",)
            assert tuple(re.findall(r"^## Planning Level$", content, flags=re.MULTILINE)) == ("## Planning Level",)
        else:
            assert links == (f"{SCOPE_TEMPLATE_CONTRACTS[scope]['guide_prefix']}scope-layering.md",)
            assert "Planning Level" not in content


@pytest.mark.parametrize(
    "relative_path",
    (
        "README.md",
        *(f"{scope}/{document}.md" for scope in SCOPES for document in RDP_DOCUMENTS),
    ),
)
def test_template_rdp_assets_match_dogfood_projection(relative_path: str) -> None:
    assert (TEMPLATES_ROOT / relative_path).read_bytes() == (DOGFOOD_TEMPLATES_ROOT / relative_path).read_bytes()


@pytest.mark.parametrize("template_root", (TEMPLATES_ROOT, DOGFOOD_TEMPLATES_ROOT))
@pytest.mark.parametrize("scope", SCOPES)
def test_each_scope_has_exactly_one_canonical_report_template(
    template_root: Path,
    scope: str,
) -> None:
    report_files = {path.name for path in (template_root / scope).glob("report*.md") if path.is_file()}

    assert report_files == {"report.md"}


@pytest.mark.parametrize("scope", SCOPES)
def test_report_frontmatter_uses_exact_minimal_fields_and_placeholders(scope: str) -> None:
    content = _read_template(scope, "report")
    fields = _frontmatter(content)
    scope_contract = SCOPE_TEMPLATE_CONTRACTS[scope]

    expected_keys = {"種別", "ID", "タイトル", "関連GitHub", "最終更新", "依存"}
    if scope_contract["parent"] is not None:
        expected_keys.add("親")
    assert set(fields) == expected_keys

    assert fields["種別"] == f"レポート（{scope.capitalize()}）"
    assert fields["ID"] == f'"{scope_contract["id"]}"'
    assert fields["タイトル"] == f'"{scope_contract["title"]}"'
    assert fields["関連GitHub"] == '["<GITHUB_ISSUE_NUMBER_OR_URL>"]'
    assert fields["最終更新"] == '"YYYY-MM-DD"'
    assert fields["依存"] == '["requirement.md", "design.md", "plan.md"]'
    if scope_contract["parent"] is not None:
        assert fields["親"] == scope_contract["parent"]

    expected_placeholders = {
        scope_contract["id"],
        scope_contract["title"],
        "<GITHUB_ISSUE_NUMBER_OR_URL>",
    }
    if scope == "epic":
        expected_placeholders.add("<INIT_ID>")
    if scope == "issue":
        expected_placeholders.update(("<INIT_ID>", "<EPIC_ID>"))
    assert set(re.findall(r"<[A-Z_]+>", content)) == expected_placeholders

    serialized_frontmatter = "\n".join(f"{key}: {value}" for key, value in fields.items()).casefold()
    for forbidden_field in ("state", "author", "approved", "completed", "状態", "作成者"):
        assert forbidden_field.casefold() not in serialized_frontmatter

    rendered = _render_template(content)
    assert not re.search(r"<[A-Z_]+>", rendered)
    assert "YYYY-MM-DD" not in rendered


@pytest.mark.parametrize("scope", SCOPES)
def test_report_has_exact_result_summary_shape_with_empty_required_bodies(scope: str) -> None:
    content = _read_template(scope, "report")

    assert content.strip()
    assert tuple(re.findall(r"^# ([^#\n]+)$", content, flags=re.MULTILINE)) == ("Result Summary",)
    assert tuple(re.findall(r"^## ([^\n]+)$", content, flags=re.MULTILINE)) == REPORT_REQUIRED_HEADINGS
    assert not re.search(r"^### ", content, flags=re.MULTILINE)
    for heading in REPORT_REQUIRED_HEADINGS:
        assert not _template_section_body(content, heading).strip()


def test_report_guide_allows_optional_notes_while_templates_omit_it() -> None:
    guide = _read_authoring_doc("report.md")

    assert "必要なときだけ" in guide
    assert "`## Notes`" in guide
    for scope in SCOPES:
        assert "## Notes" not in _read_template(scope, "report")


@pytest.mark.parametrize("scope", SCOPES)
def test_report_guide_link_resolves_from_rendered_node_location(scope: str) -> None:
    scope_contract = SCOPE_TEMPLATE_CONTRACTS[scope]
    expected_link = f"{scope_contract['guide_prefix']}report.md"

    for template_root in (TEMPLATES_ROOT, DOGFOOD_TEMPLATES_ROOT):
        scaffold_root = template_root.parent
        content = _render_template((template_root / scope / "report.md").read_text(encoding="utf-8"))
        assert _relative_markdown_links(content) == (expected_link,)

        node_path = scaffold_root.joinpath(*scope_contract["node_parts"], "report.md")
        resolved_link = (node_path.parent / expected_link).resolve()
        expected_target = (scaffold_root / "docs" / "authoring" / "report.md").resolve()
        assert resolved_link == expected_target
        assert resolved_link.is_file()


@pytest.mark.parametrize("scope", SCOPES)
def test_report_templates_match_dogfood_projection(scope: str) -> None:
    relative_path = Path(scope) / "report.md"

    assert (TEMPLATES_ROOT / relative_path).read_bytes() == (DOGFOOD_TEMPLATES_ROOT / relative_path).read_bytes()


def test_report_guide_matches_dogfood_projection() -> None:
    assert (AUTHORING_ROOT / "report.md").read_bytes() == (DOGFOOD_DOCS_ROOT / "authoring" / "report.md").read_bytes()


def test_report_guide_is_non_gating_and_routes_durable_decisions_elsewhere() -> None:
    guide = _read_authoring_doc("report.md")
    durable_section = _section(guide, "## Durableな判断の置き場")

    assert "実行可否や完了の機械的な判定には使いません" in guide
    assert "durable decisionの保管場所でも" in durable_section
    for target in ("requirement.md", "design.md", "issue-plan.md", "scope-layering.md"):
        assert target in _relative_markdown_links(durable_section)


@pytest.mark.parametrize("template_root", (TEMPLATES_ROOT, DOGFOOD_TEMPLATES_ROOT))
def test_issue_has_one_canonical_plan_and_no_level_specific_plan_aliases(
    template_root: Path,
) -> None:
    issue_templates = template_root / "issue"
    plan_files = {path.name for path in issue_templates.glob("plan*.md") if path.is_file()}

    assert plan_files == {"plan.md"}
    for level in PLANNING_LEVELS:
        assert not (issue_templates / f"plan-{level}.md").exists()


def test_issue_plan_base_links_exactly_the_four_completion_guides() -> None:
    base_path = AUTHORING_ROOT / "issue-plan.md"
    content = base_path.read_text(encoding="utf-8")
    level_links = tuple(link for link in _relative_markdown_links(content) if link.startswith("issue-plan-levels/"))

    assert level_links == tuple(f"issue-plan-levels/{level}.md" for level in PLANNING_LEVELS)
    for relative_path in level_links:
        assert (base_path.parent / relative_path).is_file()


@pytest.mark.parametrize("level", PLANNING_LEVELS)
def test_each_completion_guide_is_independent_and_links_only_the_base(level: str) -> None:
    content = (PLANNING_LEVELS_ROOT / f"{level}.md").read_text(encoding="utf-8")

    assert _relative_markdown_links(content) == ("../issue-plan.md",)
    assert tuple(re.findall(r"^## ([^\n]+)$", content, flags=re.MULTILINE)) == PLANNING_LEVEL_GUIDE_HEADINGS
    assert "別 level の Guide" not in content
    assert "順に読む" not in content


@pytest.mark.parametrize("level", PLANNING_LEVELS)
def test_each_completion_guide_contains_level_appropriate_completion_contract(
    level: str,
) -> None:
    content = (PLANNING_LEVELS_ROOT / f"{level}.md").read_text(encoding="utf-8")

    for heading in PLANNING_LEVEL_GUIDE_HEADINGS:
        section = _section(content, f"## {heading}")
        assert re.search(r"^- ", section, flags=re.MULTILINE) or heading == "escalation trigger"
        assert section.strip()
    for token in PLANNING_LEVEL_COMPLETION_TOKENS[level]:
        assert token in content


def test_critical_planning_level_limits_na_to_migration_and_requires_recovery() -> None:
    content = (PLANNING_LEVELS_ROOT / "critical.md").read_text(encoding="utf-8")
    rollback_section = _section(content, "## rollback / migration")
    sentences = tuple(sentence.strip() for sentence in rollback_section.split("。") if sentence.strip())
    na_sentences = tuple(sentence for sentence in sentences if "`N/A`" in sentence)

    assert len(na_sentences) == 1
    migration_na = na_sentences[0]
    for token in ("migration が不要な場合に限り", "migration", "理由"):
        assert token in migration_na
    for token in ("不可逆性", "復旧手段", "backup / restore", "kill switch", "incident response"):
        assert token not in migration_na

    recovery_contract = next(
        (
            sentence
            for sentence in sentences
            if all(
                token in sentence
                for token in (
                    "不可逆性",
                    "復旧手段",
                    "評価",
                    "backup / restore",
                    "kill switch",
                    "incident response",
                )
            )
        ),
        "",
    )
    assert "必ず記録" in recovery_contract
    assert "省略しない" in recovery_contract


@pytest.mark.parametrize(
    "relative_path",
    ("authoring/issue-plan.md", *(f"authoring/issue-plan-levels/{level}.md" for level in PLANNING_LEVELS)),
)
def test_s03_planning_guides_match_dogfood_projection(relative_path: str) -> None:
    assert (DOCS_ROOT / relative_path).read_bytes() == (DOGFOOD_DOCS_ROOT / relative_path).read_bytes()


def test_issue_plan_base_has_exact_selection_heading_and_structural_examples() -> None:
    content = _read_authoring_doc("issue-plan.md")
    selection = _section(content, "## Planning Levelの選び方")
    example_rows = {
        match.group("id"): match.group("row")
        for match in re.finditer(
            r"^\| `(?P<id>LEVEL-EX-(?:POS|NEG)-0[1-3])` (?P<row>\|.*)$",
            selection,
            flags=re.MULTILINE,
        )
    }

    assert content.count("## Planning Levelの選び方") == 1
    assert set(example_rows) == set(PLANNING_LEVEL_EXAMPLES)
    for example_id, expected_tokens in PLANNING_LEVEL_EXAMPLES.items():
        for token in expected_tokens:
            assert token in example_rows[example_id]


def test_issue_plan_records_level_decision_in_the_same_canonical_plan() -> None:
    content = _read_authoring_doc("issue-plan.md")
    selection = _section(content, "## Planning Levelの選び方")
    template_prompt = _template_section_prompt(_read_template("issue", "plan"), "Planning Level")

    assert "同じ canonical `plan.md`" in selection
    for token in ("selected level", "理由", "risk factor", "再評価条件"):
        assert token in selection
    for token in ("level", "理由", "risk factor", "再評価条件"):
        assert token in template_prompt


def test_planning_level_is_docs_only_and_does_not_own_runtime_metadata() -> None:
    selection = _section(_read_authoring_doc("issue-plan.md"), "## Planning Levelの選び方")

    assert "Runtime の default や metadata にはしません" in selection
    assert "Runtime の状態、実行可否" in selection
    for token in ("`.meta.json`", "active manifest", "`.assurance.json`"):
        assert token in selection
    assert "には複製しません" in selection


def test_planning_level_rejects_priority_effort_readiness_and_handoff_as_sufficient_signals() -> None:
    selection = _section(_read_authoring_doc("issue-plan.md"), "## Planning Levelの選び方")
    rejection_line = next(line for line in selection.splitlines() if "だけでは決めません" in line)

    for token in (
        "Priority",
        "Severity",
        "工数",
        "dependency readiness",
        "handoff status",
        "文書量",
    ):
        assert token in rejection_line
    assert "失敗した場合の影響と回復の難しさ" in selection


def test_standard_is_authoring_guidance_not_a_runtime_default() -> None:
    base_selection = _section(_read_authoring_doc("issue-plan.md"), "## Planning Levelの選び方")
    standard = (PLANNING_LEVELS_ROOT / "standard.md").read_text(encoding="utf-8")

    assert "執筆を始める目安" in base_selection
    assert "Runtime の default や metadata にはしません" in base_selection
    assert "執筆を始める目安" in standard
    assert "Runtime default ではありません" in standard


class S09Contract(TypedDict):
    consumer: str
    version: str
    scope_files: tuple[str, ...]
    scope_paths: tuple[str, ...]
    report_required_headings: tuple[str, ...]
    report_optional_heading: str
    report_empty_content_valid: bool
    report_runtime_gate: bool
    current_artifact_types: tuple[str, ...]
    issue_plan_files: tuple[str, ...]
    issue_plan_paths: tuple[str, ...]
    base_plan_guide: str
    level_guides: tuple[str, ...]
    planning_level_runtime_owned: bool
    planning_level_runtime_coupling: dict[str, tuple[str, ...]]
    owned_asset_manifest: tuple[str, ...]
    mismatch_routing: dict[str, str]


S09_SCOPE_FILE_NAMES = ("requirement.md", "design.md", "plan.md", "report.md")
S09_SCOPE_PATHS = tuple(f"templates/{scope}/{document}" for scope in SCOPES for document in S09_SCOPE_FILE_NAMES)
S09_ISSUE_PLAN_PATHS = ("templates/issue/plan.md",)
S09_LEVEL_GUIDE_PATHS = tuple(f"docs/authoring/issue-plan-levels/{level}.md" for level in PLANNING_LEVELS)
S09_CONTENT_OWNER = "Issue 358"
S09_RUNTIME_OWNER = "Epic downstream Runtime Issue"
S09_MISMATCH_ROUTING = {
    "content": S09_CONTENT_OWNER,
    "Guide": S09_CONTENT_OWNER,
    "heading": S09_CONTENT_OWNER,
    "copy": S09_RUNTIME_OWNER,
    "parser": S09_RUNTIME_OWNER,
    "filename": S09_RUNTIME_OWNER,
    "runtime": S09_RUNTIME_OWNER,
}
S09_RUNTIME_COUPLING: dict[str, tuple[str, ...]] = {
    "metadata_fields": (),
    "parser_symbols": (),
    "assurance_fields": (),
}
S09_CONTRACT_CONSUMER = "epic-00356-authoring-integration"
S09_CONTRACT_VERSION = "s09-2026-08-11"
S09_ISSUE_ROOT = (
    REPO_ROOT
    / "spec-dock"
    / "initiatives"
    / "init-local-00003-architecture-maintenance-and-hardening"
    / "epics"
    / "epic-00356-specdock-core-simplification-and-external-intelligence-boundary"
    / "issues"
    / "iss-00358-simplify-authoring-kit-and-document-contracts"
)
S09_DESIGN_PATH = S09_ISSUE_ROOT / "design.md"
S09_DESIGN_CONTRACT_TOKENS = (
    "scope_files = [requirement.md, design.md, plan.md, report.md]",
    f"contract_version = {S09_CONTRACT_VERSION}",
    f"consumer = {S09_CONTRACT_CONSUMER}",
    "report_required_headings = [Outcome, Verification, Residual Risks / Follow-ups]",
    "report_optional_heading = Notes",
    "report_empty_content_valid = true",
    "report_runtime_gate = false",
    "current_artifact_types = [blank, research, interview, disc, decision-candidate, adr]",
    "issue_plan_files = [plan.md]",
    "base_plan_guide = docs/authoring/issue-plan.md",
    "level_guides = docs/authoring/issue-plan-levels/{light,standard,strict,critical}.md",
    "planning_level_runtime_owned = false",
    "content / Guide / heading mismatchは358へ",
    "copy / parser / filename mismatchは該当Runtime Issueへrouting",
)
S09_IC1_CONTRACT: S09Contract = {
    "consumer": S09_CONTRACT_CONSUMER,
    "version": S09_CONTRACT_VERSION,
    "scope_files": S09_SCOPE_FILE_NAMES,
    "scope_paths": S09_SCOPE_PATHS,
    "report_required_headings": REPORT_REQUIRED_HEADINGS,
    "report_optional_heading": "Notes",
    "report_empty_content_valid": True,
    "report_runtime_gate": False,
    "current_artifact_types": CURRENT_ARTIFACT_TEMPLATES,
    "issue_plan_files": ("plan.md",),
    "issue_plan_paths": S09_ISSUE_PLAN_PATHS,
    "base_plan_guide": "docs/authoring/issue-plan.md",
    "level_guides": S09_LEVEL_GUIDE_PATHS,
    "planning_level_runtime_owned": False,
    "planning_level_runtime_coupling": S09_RUNTIME_COUPLING,
    "owned_asset_manifest": S07_OWNED_ASSET_MANIFEST,
    "mismatch_routing": S09_MISMATCH_ROUTING,
}


def _s09_contract_violations(contract: Mapping[str, object]) -> tuple[str, ...]:
    expected: dict[str, object] = {
        "consumer": S09_CONTRACT_CONSUMER,
        "version": S09_CONTRACT_VERSION,
        "scope_files": S09_SCOPE_FILE_NAMES,
        "scope_paths": S09_SCOPE_PATHS,
        "report_required_headings": REPORT_REQUIRED_HEADINGS,
        "report_optional_heading": "Notes",
        "report_empty_content_valid": True,
        "report_runtime_gate": False,
        "current_artifact_types": CURRENT_ARTIFACT_TEMPLATES,
        "issue_plan_files": ("plan.md",),
        "issue_plan_paths": S09_ISSUE_PLAN_PATHS,
        "base_plan_guide": "docs/authoring/issue-plan.md",
        "level_guides": S09_LEVEL_GUIDE_PATHS,
        "planning_level_runtime_owned": False,
        "planning_level_runtime_coupling": S09_RUNTIME_COUPLING,
        "owned_asset_manifest": S07_OWNED_ASSET_MANIFEST,
        "mismatch_routing": S09_MISMATCH_ROUTING,
    }
    violations = [f"{key} mismatch" for key, expected_value in expected.items() if contract.get(key) != expected_value]

    for key in ("scope_files", "scope_paths", "current_artifact_types", "owned_asset_manifest"):
        value = contract.get(key)
        if isinstance(value, tuple) and len(value) != len(set(value)):
            violations.append(f"{key} duplicate")

    routing = contract.get("mismatch_routing")
    if isinstance(routing, dict):
        if set(routing) != set(S09_MISMATCH_ROUTING):
            violations.append("mismatch routing owner missing or extra")
        if any("357" in owner for owner in routing.values()):
            violations.append("direct Issue 357 dependency")
    else:
        violations.append("mismatch routing owner missing")

    return tuple(dict.fromkeys(violations))


def _s09_design_contract_violations(design_section: str) -> tuple[str, ...]:
    return tuple(
        f"missing Design §12 token: {token}" for token in S09_DESIGN_CONTRACT_TOKENS if token not in design_section
    )


def test_s09_ic1_contract_input_is_exact_and_provider_dogfood_complete() -> None:
    assert _s09_contract_violations(S09_IC1_CONTRACT) == ()
    assert S09_IC1_CONTRACT["consumer"] == S09_CONTRACT_CONSUMER
    assert S09_IC1_CONTRACT["version"] == S09_CONTRACT_VERSION
    manifest = S09_IC1_CONTRACT["owned_asset_manifest"]
    assert manifest == S07_OWNED_ASSET_MANIFEST
    assert not _projection_violations(manifest, DOCS_ROOT.parent, DOGFOOD_DOCS_ROOT.parent)

    for relative_path in S09_SCOPE_PATHS + S09_ISSUE_PLAN_PATHS + S09_LEVEL_GUIDE_PATHS:
        assert relative_path in manifest


def test_s09_contract_input_binds_to_canonical_design_section() -> None:
    design = S09_DESIGN_PATH.read_text(encoding="utf-8")
    design_section = _section(design, "## 12. Epic-level IC-1 contract input")

    assert _s09_design_contract_violations(design_section) == ()
    assert f"contract_version = {S09_CONTRACT_VERSION}" in design_section
    assert f"consumer = {S09_CONTRACT_CONSUMER}" in design_section


@pytest.mark.parametrize(
    ("token", "replacement"),
    (
        (f"contract_version = {S09_CONTRACT_VERSION}", "contract_version = stale"),
        (f"consumer = {S09_CONTRACT_CONSUMER}", "consumer = stale"),
        (
            "scope_files = [requirement.md, design.md, plan.md, report.md]",
            "scope_files = [plan.md]",
        ),
        ("content / Guide / heading mismatchは358へ", "content mismatchはruntimeへ"),
    ),
)
def test_s09_design_binding_rejects_canonical_contract_mutations(token: str, replacement: str) -> None:
    design = S09_DESIGN_PATH.read_text(encoding="utf-8")
    design_section = _section(design, "## 12. Epic-level IC-1 contract input")
    mutated_section = design_section.replace(token, replacement, 1)

    assert f"missing Design §12 token: {token}" in _s09_design_contract_violations(mutated_section)


def test_s09_scope_manifest_covers_requirement_design_plan_report_for_each_scope() -> None:
    expected = tuple(f"templates/{scope}/{document}" for scope in SCOPES for document in S09_SCOPE_FILE_NAMES)
    assert S09_IC1_CONTRACT["scope_paths"] == expected
    assert tuple(path for path in S09_IC1_CONTRACT["owned_asset_manifest"] if path in expected) == expected


@pytest.mark.parametrize("scaffold_root", (DOCS_ROOT.parent, DOGFOOD_DOCS_ROOT.parent))
def test_s09_report_contract_is_exact_empty_valid_and_non_gating(scaffold_root: Path) -> None:
    for scope in SCOPES:
        report_path = scaffold_root / "templates" / scope / "report.md"
        content = report_path.read_text(encoding="utf-8")
        assert tuple(re.findall(r"^## ([^\n]+)$", content, flags=re.MULTILINE)) == REPORT_REQUIRED_HEADINGS
        for heading in REPORT_REQUIRED_HEADINGS:
            assert not _template_section_body(content, heading).strip()
        assert "## Notes" not in content

    guide = (scaffold_root / "docs" / "authoring" / "report.md").read_text(encoding="utf-8")
    assert "空でも有効" in guide
    assert "実行可否や完了の機械的な判定には使いません" in guide
    assert "## Notes" in guide


@pytest.mark.parametrize("scaffold_root", (DOCS_ROOT.parent, DOGFOOD_DOCS_ROOT.parent))
def test_s09_artifact_and_one_plan_catalogs_are_exact(scaffold_root: Path) -> None:
    artifact_dir = scaffold_root / "templates" / "artifacts"
    guide = (scaffold_root / "docs" / "authoring" / "artifacts.md").read_text(encoding="utf-8")
    current_catalog = _section(guide, "## Current creation catalog")
    assert tuple(re.findall(r"^\| `([^`]+)` \|", current_catalog, flags=re.MULTILINE)) == CURRENT_ARTIFACT_TEMPLATES
    for artifact_type in CURRENT_ARTIFACT_TEMPLATES:
        assert (artifact_dir / f"{artifact_type}.md").is_file()

    issue_dir = scaffold_root / "templates" / "issue"
    assert tuple(sorted(path.name for path in issue_dir.glob("plan*.md"))) == ("plan.md",)

    base_guide = scaffold_root / S09_IC1_CONTRACT["base_plan_guide"]
    assert base_guide.is_file()
    assert tuple(
        path.relative_to(scaffold_root).as_posix()
        for path in sorted((scaffold_root / "docs/authoring/issue-plan-levels").glob("*.md"))
    ) == tuple(sorted(S09_LEVEL_GUIDE_PATHS))
    assert base_guide.read_bytes() == (AUTHORING_ROOT / "issue-plan.md").read_bytes()


def test_s09_planning_level_is_docs_only_without_runtime_metadata_parser_or_assurance_coupling() -> None:
    assert S09_IC1_CONTRACT["planning_level_runtime_owned"] is False
    assert S09_IC1_CONTRACT["planning_level_runtime_coupling"] == {
        "metadata_fields": (),
        "parser_symbols": (),
        "assurance_fields": (),
    }

    runtime_root = REPO_ROOT / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    runtime_references = tuple(
        path.relative_to(runtime_root).as_posix()
        for path in sorted(runtime_root.rglob("*.py"))
        if re.search(r"planning[_ -]level", path.read_text(encoding="utf-8"), flags=re.IGNORECASE)
    )
    assert runtime_references == ()


def test_s09_mismatch_routing_assigns_content_to_358_and_mechanism_to_downstream_runtime_issue() -> None:
    routing = S09_IC1_CONTRACT["mismatch_routing"]
    for key in ("content", "Guide", "heading"):
        assert routing[key] == S09_CONTENT_OWNER
    for key in ("copy", "parser", "filename", "runtime"):
        assert routing[key] == S09_RUNTIME_OWNER
    assert all("357" not in owner for owner in routing.values())


def test_s09_contract_rejects_missing_scope_path_mutation() -> None:
    variant = {**S09_IC1_CONTRACT, "scope_paths": S09_SCOPE_PATHS[1:]}
    violations = _s09_contract_violations(variant)
    assert "scope_paths mismatch" in violations


def test_s09_contract_rejects_missing_consumer_or_version_mutations() -> None:
    for field in ("consumer", "version"):
        variant = {key: value for key, value in S09_IC1_CONTRACT.items() if key != field}
        assert f"{field} mismatch" in _s09_contract_violations(variant)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("consumer", "epic-00356-runtime-integration"),
        ("version", "s09-2026-08-10"),
    ),
)
def test_s09_contract_rejects_wrong_consumer_or_version_mutations(field: str, value: str) -> None:
    variant = {**S09_IC1_CONTRACT, field: value}
    assert f"{field} mismatch" in _s09_contract_violations(variant)


def test_s09_contract_rejects_duplicate_scope_path_mutation() -> None:
    variant = {**S09_IC1_CONTRACT, "scope_paths": (*S09_SCOPE_PATHS, S09_SCOPE_PATHS[0])}
    violations = _s09_contract_violations(variant)
    assert "scope_paths duplicate" in violations


def test_s09_contract_rejects_missing_owner_mutation() -> None:
    routing = dict(S09_IC1_CONTRACT["mismatch_routing"])
    del routing["heading"]
    violations = _s09_contract_violations({**S09_IC1_CONTRACT, "mismatch_routing": routing})
    assert "mismatch routing owner missing or extra" in violations


def test_s09_contract_rejects_wrong_owner_and_direct_357_routing_mutations() -> None:
    routing = dict(S09_IC1_CONTRACT["mismatch_routing"])
    routing["content"] = S09_RUNTIME_OWNER
    routing["parser"] = "Issue 357"
    violations = _s09_contract_violations({**S09_IC1_CONTRACT, "mismatch_routing": routing})
    assert "mismatch_routing mismatch" in violations
    assert "direct Issue 357 dependency" in violations


@pytest.mark.parametrize(
    ("coupling_key", "coupling_value"),
    (
        ("metadata_fields", (".meta.json",)),
        ("parser_symbols", ("parse_planning_level",)),
        ("assurance_fields", ("planning_level",)),
    ),
)
def test_s09_contract_rejects_planning_level_runtime_coupling_mutations(
    coupling_key: str,
    coupling_value: tuple[str, ...],
) -> None:
    coupling = dict(S09_IC1_CONTRACT["planning_level_runtime_coupling"])
    coupling[coupling_key] = coupling_value
    variant = {**S09_IC1_CONTRACT, "planning_level_runtime_coupling": coupling}
    assert "planning_level_runtime_coupling mismatch" in _s09_contract_violations(variant)
