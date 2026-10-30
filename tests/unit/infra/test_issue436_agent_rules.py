"""The agent rules section (iss-00436, Epic R-H1 and design ch. 10) in the shipped skill and in AGENTS.md."""

from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / "src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md"
AGENTS = ROOT / "AGENTS.md"
HEADING = "## 仕様の扱い（canonical モード）"

# One phrase per item of the Epic design ch. 10 section and of the items iss-00436 adds (R-436-01).
REQUIRED = (
    "`schema_version` が 4",
    "3 のリポジトリでは、今までどおり",
    "`spec-dock/initiatives/`",
    "`git add`",
    "`stash`",
    "`reset`",
    "`checkout`",
    "`clean`",
    "名前を変えたり",
    "1〜2分",
    "`spec-dock canonical link`",
    "普通の端末",
    "`spec-dock canonical status`",
    "自分でツールの設定を変えない",
    "`rg 語 spec-dock/initiatives/`",
    "`spec-dock/initiatives/<区切り>/<ID>/`",
    "`spec-dock/initiatives/00000-00999/iss-00454/`",
    "`spec-dock scope show <ID> --json`",
    "SpecDock のコマンドだけで変える",
    "`*.conflict-*`",
    "`--worktree`",
    "`spec-dock work finish`",
    "180秒",
    "`rm spec-dock/initiatives`",
    "`git clean -ff`",
    "`iss-454`",
    "`--slug`",
    "GitHub の題名が正本",
    "既定のブランチ名は `<ID>`",
    "`spec-dock scope move <ID> --parent <親>`",
    "`SCOPE_KIND_CHANGED`",
    "`SCOPE_IN_PROGRESS`",
)


def _section(text: str) -> str:
    start = text.index(HEADING)
    end = text.find("\n## ", start + len(HEADING))
    return text[start : end if end >= 0 else len(text)]


def _items(section: str) -> list[str]:
    return [line for line in section.splitlines() if line.startswith("- ")]


def test_the_skill_and_agents_md_carry_the_same_rules_section() -> None:
    skill, agents = _section(SKILL.read_text(encoding="utf-8")), _section(AGENTS.read_text(encoding="utf-8"))
    assert _items(skill) == _items(agents)
    assert len(_items(skill)) >= 13  # the 11 items of ch. 10 and the two iss-00436 adds
    for phrase in REQUIRED:
        assert phrase in skill, phrase


def test_canonical_remove_needs_an_exact_destructive_instruction_in_both() -> None:
    skill = SKILL.read_text(encoding="utf-8")
    destructive = skill[skill.index("## Destructive boundary") :]
    assert "`canonical remove`" in destructive.split("\n## ")[0]
    agents = AGENTS.read_text(encoding="utf-8")
    (line,) = [item for item in agents.splitlines() if "explicit destructive outcome" in item]
    assert "`canonical remove`" in line


def test_the_section_states_the_flat_id_rules_without_slug_directories() -> None:
    section = _section(SKILL.read_text(encoding="utf-8"))
    assert not re.search(r"iss-\d{5}-[a-z]", section)  # no <ID>-<slug> directory or branch examples
