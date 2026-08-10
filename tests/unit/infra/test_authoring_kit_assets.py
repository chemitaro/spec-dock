from pathlib import Path
import re

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
DOCS_ROOT = REPO_ROOT / "src" / "spec_dock" / "assets" / "spec_dock" / "docs"
AUTHORING_ROOT = DOCS_ROOT / "authoring"
DOGFOOD_DOCS_ROOT = REPO_ROOT / "spec-dock" / "docs"
TEMPLATES_ROOT = DOCS_ROOT.parent / "templates"
DOGFOOD_TEMPLATES_ROOT = DOGFOOD_DOCS_ROOT.parent / "templates"

OVERVIEW_LINK_TARGETS = (
    "requirement.md",
    "design.md",
    "issue-plan.md",
    "report.md",
    "scope-layering.md",
)

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

KNOWN_LEGACY_ROUTE_MARKERS = (
    "spec-dock-issue-planning",
    "chatgpt-first",
    "assurance compose",
    "spec-dock-chatgpt",
)

MANDATORY_WORKFLOW_PATTERNS = (
    re.compile(
        r"(?:agent|provider|model|workflow|reviewer|review 手順|ChatGPT|Oracle|Codex|Claude|Gemini|GPT-[0-9]+(?:\.[0-9]+)*).{0,40}"
        r"(?:を必須とします|が必須です|を使用してください|を使ってください|を前提とします|を前提にします)",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"(?:必ず|必須で).{0,40}"
        r"(?:agent|provider|model|workflow|reviewer|review 手順|ChatGPT|Oracle|Codex|Claude|Gemini|GPT-[0-9]+(?:\.[0-9]+)*)",
        flags=re.IGNORECASE,
    ),
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

SCOPE_TEMPLATE_CONTRACTS = {
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

DOCUMENT_TEMPLATE_CONTRACTS = {
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

FORBIDDEN_TEMPLATE_PATTERNS = (
    re.compile(r"\bartifact_state\b", flags=re.IGNORECASE),
    re.compile(r"\bworkflow\b", flags=re.IGNORECASE),
    re.compile(r"\breviewer\b", flags=re.IGNORECASE),
    re.compile(r"\bgrade\b", flags=re.IGNORECASE),
    re.compile(r"\beal\b", flags=re.IGNORECASE),
    re.compile(r"\bassurance\b", flags=re.IGNORECASE),
    re.compile(r"\bauthority\b", flags=re.IGNORECASE),
    re.compile(r"\bpromotion\b", flags=re.IGNORECASE),
    re.compile(r"\bdelegated[ _-]+authoring\b", flags=re.IGNORECASE),
    re.compile(r"\bphase[ _-]+gate\b", flags=re.IGNORECASE),
    re.compile(r"\bpr[ _-]+status\b", flags=re.IGNORECASE),
)

REPORT_REQUIRED_HEADINGS = (
    "Outcome",
    "Verification",
    "Residual Risks / Follow-ups",
)
REPORT_FORBIDDEN_PATTERNS = (
    re.compile(r"\bdecision[ _-]+ledger\b|仕様解釈・判断台帳", flags=re.IGNORECASE),
    re.compile(r"\beal\b", flags=re.IGNORECASE),
    re.compile(r"\bevidence[ _-]+adoption(?:[ _-]+ledger)?\b|証跡採用台帳", flags=re.IGNORECASE),
    re.compile(r"\bauthoring[ _-]+gate\b|authoring ゲート", flags=re.IGNORECASE),
    re.compile(r"\breviewer[ _-]+gate\b|レビューゲート", flags=re.IGNORECASE),
    re.compile(r"\bcompletion[ _-]+gate\b|完了ゲート", flags=re.IGNORECASE),
    re.compile(r"\bsession[ _-]+log\b|セッションログ", flags=re.IGNORECASE),
    re.compile(r"\bprogress[ _-]+summary\b|進捗サマリー", flags=re.IGNORECASE),
    re.compile(r"\bworkflow\b", flags=re.IGNORECASE),
    re.compile(r"\bauthority\b", flags=re.IGNORECASE),
    re.compile(r"\bpromotion\b", flags=re.IGNORECASE),
)
REPORT_TEMPLATE_FORBIDDEN_PATTERNS = (*FORBIDDEN_TEMPLATE_PATTERNS, *REPORT_FORBIDDEN_PATTERNS)
REPORT_GUIDE_GENERIC_FORBIDDEN_PATTERNS = (
    re.compile(r"\bgrade\b", flags=re.IGNORECASE),
    re.compile(r"\bassurance\b", flags=re.IGNORECASE),
    re.compile(r"\bdelegated[ _-]+authoring\b", flags=re.IGNORECASE),
    re.compile(r"\bpr[ _-]+status\b", flags=re.IGNORECASE),
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


def _relative_markdown_links(content: str) -> tuple[str, ...]:
    destinations = re.findall(r"\[[^\]]*\]\(([^)]+)\)", content)
    relative_paths: list[str] = []
    for destination in destinations:
        destination = destination.strip().strip("<>").split(maxsplit=1)[0]
        path_without_fragment = destination.split("#", maxsplit=1)[0]
        if not path_without_fragment:
            continue
        if path_without_fragment.startswith("/") or "://" in path_without_fragment:
            continue
        relative_paths.append(path_without_fragment)
    return tuple(relative_paths)


def _requires_specific_workflow(content: str) -> bool:
    return any(pattern.search(content) is not None for pattern in MANDATORY_WORKFLOW_PATTERNS)


def _report_template_has_forbidden_contract(content: str) -> bool:
    return any(pattern.search(content) is not None for pattern in REPORT_TEMPLATE_FORBIDDEN_PATTERNS)


def _report_guide_has_forbidden_contract(content: str) -> bool:
    return _requires_specific_workflow(content) or any(
        pattern.search(content) is not None
        for pattern in (*REPORT_FORBIDDEN_PATTERNS, *REPORT_GUIDE_GENERIC_FORBIDDEN_PATTERNS)
    )


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


@pytest.mark.parametrize(
    "content",
    (
        "特定の agent を使用してください。",
        "指定 provider が必須です。",
        "特定の model を前提とします。",
        "この workflow を必須とします。",
        "指定の review 手順を使ってください。",
        "必ず approved model を利用します。",
        "ChatGPT を必須とします。",
        "GPT-5.6 を使用してください。",
        "Codex を前提とします。",
    ),
)
def test_mandatory_workflow_patterns_reject_required_tools(content: str) -> None:
    assert _requires_specific_workflow(content)


@pytest.mark.parametrize(
    "content",
    (
        "特定の agent、model、provider、review 手順を前提にしません。",
        "必要に応じて任意の model や provider を選べます。",
        ".agents/ と .codex/ の利用は必須ではありません。",
    ),
)
def test_mandatory_workflow_patterns_allow_optional_tools(content: str) -> None:
    assert not _requires_specific_workflow(content)


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


@pytest.mark.parametrize("relative_path", S01_OWNED_DOC_PATHS)
def test_current_authoring_foundation_does_not_require_a_specific_workflow(
    relative_path: str,
) -> None:
    content = (DOCS_ROOT / relative_path).read_text(encoding="utf-8")

    assert not _requires_specific_workflow(content)

    if relative_path.startswith("authoring/"):
        normalized_content = content.casefold()
        for marker in KNOWN_LEGACY_ROUTE_MARKERS:
            assert marker not in normalized_content

    if relative_path == "authoring/overview.md":
        assert "特定の agent、model、provider、review 手順を前提にしません" in content
    if relative_path == "authoring/issue-plan.md":
        assert "特定の agent、provider、review 手順を前提にしません" in content


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


def test_template_rdp_catalog_readme_lists_only_the_nine_rdp_templates() -> None:
    content = (TEMPLATES_ROOT / "README.md").read_text(encoding="utf-8")

    for scope in SCOPES:
        assert content.count(f"`{scope}/{{requirement,design,plan}}.md`") == 1
    assert "report.md" not in content.casefold()
    assert "artifact" not in content.casefold()


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
    ("scope", "document"),
    ((scope, document) for scope in SCOPES for document in RDP_DOCUMENTS),
)
def test_template_rdp_excludes_legacy_workflow_and_quality_gate_contracts(
    scope: str,
    document: str,
) -> None:
    content = _read_template(scope, document)

    for pattern in FORBIDDEN_TEMPLATE_PATTERNS:
        assert pattern.search(content) is None, f"forbidden template contract: {pattern.pattern}"


@pytest.mark.parametrize(
    "content",
    ("delegated_authoring", "phase_gate", "pr_status"),
)
def test_template_forbidden_patterns_reject_snake_case_variants(content: str) -> None:
    assert any(pattern.search(content) is not None for pattern in FORBIDDEN_TEMPLATE_PATTERNS)


@pytest.mark.parametrize(
    "content",
    ("delegated task", "authoring guidance", "deployment phase", "quality gate", "PR reference", "status note"),
)
def test_template_forbidden_patterns_allow_unrelated_terms(content: str) -> None:
    assert all(pattern.search(content) is None for pattern in FORBIDDEN_TEMPLATE_PATTERNS)


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


@pytest.mark.parametrize(
    "path",
    (
        *(TEMPLATES_ROOT / scope / "report.md" for scope in SCOPES),
        *(DOGFOOD_TEMPLATES_ROOT / scope / "report.md" for scope in SCOPES),
    ),
)
def test_report_templates_exclude_heavy_and_generic_workflow_contracts(path: Path) -> None:
    content = path.read_text(encoding="utf-8")

    assert not _report_template_has_forbidden_contract(content), f"forbidden Report template contract in {path}"


@pytest.mark.parametrize(
    "path",
    (AUTHORING_ROOT / "report.md", DOGFOOD_DOCS_ROOT / "authoring" / "report.md"),
)
def test_report_guides_exclude_heavy_and_generic_workflow_contracts(path: Path) -> None:
    content = path.read_text(encoding="utf-8")

    assert not _report_guide_has_forbidden_contract(content), f"forbidden Report Guide contract in {path}"


@pytest.mark.parametrize(
    "content",
    (
        "reviewer",
        "Grade",
        "Assurance",
        "delegated authoring",
        "delegated-authoring",
        "delegated_authoring",
        "PR status",
        "PR-status",
        "PR_status",
    ),
)
def test_report_template_forbidden_contract_detector_rejects_generic_variants(content: str) -> None:
    assert _report_template_has_forbidden_contract(content)


@pytest.mark.parametrize(
    "content",
    (
        "Grade",
        "Assurance",
        "delegated authoring",
        "delegated-authoring",
        "delegated_authoring",
        "PR status",
        "PR-status",
        "PR_status",
    ),
)
def test_report_guide_forbidden_contract_detector_rejects_generic_variants(content: str) -> None:
    assert _report_guide_has_forbidden_contract(content)


def test_report_guide_allows_nonmandatory_reviewer_boundary_but_rejects_mandatory_reviewer() -> None:
    assert not _report_guide_has_forbidden_contract("特定の reviewer による利用記録を必須にする項目を置きません。")
    assert _report_guide_has_forbidden_contract("特定の reviewer を必須とします。")


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
