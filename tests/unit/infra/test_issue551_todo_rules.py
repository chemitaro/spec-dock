"""Human-task rules in the shipped skill and documents (iss-00551)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "src/spec_dock/assets"
SKILL = ASSETS / "install_root/.agents/skills/spec-dock/SKILL.md"
DOCS = ASSETS / "spec_dock/docs"
SECTION = "## 人のタスク"


def _skill_section() -> str:
    text = SKILL.read_text(encoding="utf-8")
    start = text.index(SECTION)
    end = text.find("\n## ", start + len(SECTION))
    return text[start : end if end >= 0 else len(text)]


def test_skill_section_has_the_registration_rules() -> None:
    section = _skill_section()
    for word in (
        "todo add --by agent",
        "--role",
        "--kind",
        "--reply-to",
        "--effort",
        "--blocks",
        "PR のマージ待ち",
        "Orca",
        "decide",
        "秘密",
        "--worktree",
        "会話の中で答えが返る",
    ):
        assert word in section, word


def test_skill_section_has_the_checklist_rules() -> None:
    section = _skill_section()
    for word in ("--kind checklist", "--item", "todo show <親>", "サブタスク", "1回の会話で終わる"):
        assert word in section, word


def test_skill_section_has_the_closing_rules() -> None:
    section = _skill_section()
    for word in ("todo done", "--record", "統括", "todo list"):
        assert word in section, word


def test_skill_commands_exist_in_the_cli_reference() -> None:
    reference = (DOCS / "reference_cli.md").read_text(encoding="utf-8")
    for leaf in ("todo add", "todo show", "todo done", "todo list"):
        assert f"`{leaf}`" in reference, leaf


def test_todo_md_is_shipped_and_linked() -> None:
    todo = (DOCS / "todo.md").read_text(encoding="utf-8")
    for heading in ("## 使い方", "## 記録の形", "## 設定の3段", "## 集約", "## 外部の道具から読む"):
        assert heading in todo, heading
    assert "(reference_cli.md)" in todo
    for entry in ("README.md", "guide.md"):
        assert "(todo.md)" in (DOCS / entry).read_text(encoding="utf-8"), entry
    canonical = (DOCS / "canonical.md").read_text(encoding="utf-8")
    assert "(todo.md)" in canonical and "`todos/`" in canonical
    paths = {entry["path"] for entry in json.loads((ASSETS / "static-inventory.json").read_text())["files"]}
    assert "spec-dock/docs/todo.md" in paths


def test_canonical_md_todo_codes_are_in_the_cli_reference() -> None:
    canonical = (DOCS / "canonical.md").read_text(encoding="utf-8")
    reference = (DOCS / "reference_cli.md").read_text(encoding="utf-8")
    codes = set(re.findall(r"`(TODO_[A-Z_]+)`", canonical))
    assert {"TODO_INVALID", "TODO_SUBTASKS_OPEN", "TODO_REPOSITORY_UNREADABLE"} <= codes
    assert [code for code in sorted(codes) if f"`{code}`" not in reference] == []


def test_dogfood_copies_match_and_inventory_hashes_are_current() -> None:
    entries = {e["path"]: e for e in json.loads((ASSETS / "static-inventory.json").read_text())["files"]}
    pairs = {
        ".agents/skills/spec-dock/SKILL.md": SKILL,
        "spec-dock/docs/todo.md": DOCS / "todo.md",
        "spec-dock/docs/canonical.md": DOCS / "canonical.md",
        "spec-dock/docs/README.md": DOCS / "README.md",
        "spec-dock/docs/guide.md": DOCS / "guide.md",
    }
    for rel, source in pairs.items():
        data = source.read_bytes()
        assert (ROOT / rel).read_bytes() == data, rel
        assert entries[rel]["sha256"] == hashlib.sha256(data).hexdigest(), rel


def test_installation_init_ships_the_skill_rules_and_todo_md(installed_static_consumer: Path) -> None:
    skill = (installed_static_consumer / ".agents/skills/spec-dock/SKILL.md").read_text(encoding="utf-8")
    assert SECTION in skill
    assert (installed_static_consumer / "spec-dock/docs/todo.md").is_file()
