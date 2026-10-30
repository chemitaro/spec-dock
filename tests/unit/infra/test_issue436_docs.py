"""Usage documents for canonical mode (iss-00436): canonical.md, the CLI reference, the HTML guide and help."""

from __future__ import annotations

from pathlib import Path
import re
from typing import TYPE_CHECKING

from spec_dock.runtime.cli.catalog import LEAF_PATHS
from spec_dock.runtime.domain.canonical_tools import claude_setting_line, codex_setting_line

if TYPE_CHECKING:
    import pytest

ROOT = Path(__file__).resolve().parents[3]
RUNTIME = ROOT / "src/spec_dock/runtime"
DOCS = ROOT / "src/spec_dock/assets/spec_dock/docs"
CANONICAL = DOCS / "canonical.md"
SECTIONS = (
    "## モードと置き場",
    "## 用意と状態",
    "## ツールの設定",
    "## 保存と同期",
    "## 同期が止まったとき",
    "## Linux とコンテナ",
    "## 構造のスナップショットとダッシュボード",
    "## 制約",
    "## 既定のブランチの検査",
    "## エラーと次の1手",
)
CODE_PREFIXES = ("CANONICAL_", "GITHUB_", "SCOPE_", "DEPENDENCY_", "PARENT_", "KIND_", "SUB_ISSUE_", "READINESS_")
LITERAL = re.compile(r'"(CANONICAL_[A-Z0-9_]+)"')
CONSTANT = re.compile(r'^([A-Z][A-Z0-9_]+)(?::\s*Final)?\s*=\s*"([A-Z][A-Z0-9_]+)"', re.MULTILINE)


def _section(text: str, heading: str) -> str:
    start = text.index(heading)
    end = text.find("\n## ", start + len(heading))
    return text[start : end if end >= 0 else len(text)]


def _runtime_codes() -> set[str]:
    """Public codes of canonical mode: the code constants of its modules (Epic design ch. 12, C8)."""
    sources = [*RUNTIME.glob("application/canonical_*.py"), *RUNTIME.glob("domain/canonical_*.py")]
    sources += [RUNTIME / "infra/github_structure.py", RUNTIME / "infra/github_snapshot.py"]
    codes: set[str] = set()
    for source in sources:
        text = source.read_text(encoding="utf-8")
        every = source.name in ("canonical_errors.py", "canonical_check.py")
        for name, value in CONSTANT.findall(text):
            if name == value and (every or value.startswith(CODE_PREFIXES)):
                codes.add(value)
        codes.update(LITERAL.findall(text))  # codes written in place, such as CANONICAL_REMOVE_FAILED
    return codes


def _documented_codes() -> dict[str, str]:
    """Each backticked code in the first cell of the error table, with that row's next step."""
    table = _section(CANONICAL.read_text(encoding="utf-8"), "## エラーと次の1手")
    rows: dict[str, str] = {}
    for line in table.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not line.startswith("|") or len(cells) < 3 or set(cells[0]) <= {"-", ":"}:
            continue
        for code in re.findall(r"`([A-Z][A-Z0-9_]+)`", cells[0]):
            rows[code] = cells[-1]
    return rows


def test_canonical_md_has_every_section_and_is_linked_from_the_entry_documents() -> None:
    text = CANONICAL.read_text(encoding="utf-8")
    for heading in SECTIONS:
        assert heading in text, heading
    for entry in ("README.md", "guide.md", "migration.md", "reference_cli.md"):
        assert "(canonical.md)" in (DOCS / entry).read_text(encoding="utf-8"), entry
    assert "spec-dock/docs/canonical.md" in (ROOT / "README.md").read_text(encoding="utf-8")


def test_canonical_md_shows_the_exact_tool_lines_canonical_status_prints() -> None:
    tools = _section(CANONICAL.read_text(encoding="utf-8"), "## ツールの設定")
    catalog = Path("<カタログ>")
    assert claude_setting_line(catalog) in tools
    assert codex_setting_line(catalog) in tools
    for phrase in ("permissions.additionalDirectories", "[sandbox_workspace_write]", "CLAUDE_CONFIG_DIR", "--worktree"):
        assert phrase in tools, phrase
    assert tools.count("/spec-dock/.canonical") >= 10  # the five catalogs listed in one array, for both tools


def test_canonical_md_covers_the_handed_over_constraints() -> None:
    text = CANONICAL.read_text(encoding="utf-8")
    for phrase in (
        "`<区切り>/<ID>/`",
        "`iss-454`",
        "`--adopt-remote`",
        "`--push-local`",
        "`merge_failed`",
        "linger",
        "2.38",
        "22.04",
        "`CANONICAL_FOREIGN_CHECKOUT`",
        "workspace sync --source github",
        "30分",
        "sparse-checkout",
        "`GIT_ASKPASS`",
        "`--no-schedule`",
        "`XDG_STATE_HOME`",
        "0.3.0",
        "`--discard-ignored`",
        "`anomalies`",
        "`--structure`",
        "`--offline`",
        "180秒",
    ):
        assert phrase in text, phrase


def test_the_error_table_matches_the_runtime_codes_and_names_a_next_step() -> None:
    documented = _documented_codes()
    assert _runtime_codes() <= set(documented)
    source = "\n".join(path.read_text(encoding="utf-8") for path in RUNTIME.rglob("*.py"))
    assert [code for code in set(documented) - _runtime_codes() if code not in source] == []
    assert [code for code, step in documented.items() if not step] == []
    assert "CANONICAL_NOT_IMPLEMENTED" not in documented


def test_the_reference_and_the_html_guide_list_all_53_commands() -> None:
    reference = (DOCS / "reference_cli.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\| C(\d\d) \| `([^`]+)` \|", reference, re.MULTILINE)
    assert [int(number) for number, _ in rows] == list(range(1, 54))
    assert {leaf for _, leaf in rows} == set(LEAF_PATHS)
    assert "公開53 leaf" in reference and "全53 leaf" in (DOCS / "README.md").read_text(encoding="utf-8")
    html = (DOCS / "cli-redesign-guide.html").read_text(encoding="utf-8")
    assert "全53コマンド" in html and "全44コマンド" not in html and "44 leaf" not in html
    listed = set(re.findall(r"<td><code>([a-z][a-z ]+?)</code>", html))
    assert set(LEAF_PATHS) <= listed


def _help(capsys: pytest.CaptureFixture[str], *leaf: str) -> str:
    from spec_dock.cli import main

    capsys.readouterr()
    assert main([*leaf, "--help"]) == 0
    return capsys.readouterr().out


def test_help_names_the_schema4_places_ids_and_writes(capsys: pytest.CaptureFixture[str]) -> None:
    link = _help(capsys, "canonical", "link")
    for phrase in ("set-branches", "update-ref", "registry", "periodic job", "baseline"):
        assert phrase in link, phrase
    create = _help(capsys, "scope", "create", "issue")
    assert "spec-dock/initiatives/<bucket>/<ID>/" in create and "CANONICAL_NOT_APPLICABLE" in create
    assert "CANONICAL_TITLE_IGNORED" in _help(capsys, "scope", "import", "github", "epic")
    start = _help(capsys, "work", "start")
    assert "<ID>" in start and "iss-454" in start and "SCOPE_IN_PROGRESS" in start
    finish = _help(capsys, "work", "finish")
    assert "180 seconds" in finish and "CANONICAL_SAVE_UNCONFIRMED" in finish
