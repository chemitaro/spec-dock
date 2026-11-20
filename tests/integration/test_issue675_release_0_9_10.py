"""SpecDock 0.9.10 release and upgrade coverage (iss-00675)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import TYPE_CHECKING, Any

from spec_dock.cli import main
from tests.integration.test_issue413_assets import uninitialized_worktree

if TYPE_CHECKING:
    import pytest

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "src/spec_dock/assets"
SCAFFOLD = ASSETS / "spec_dock"
FIXTURES = ROOT / "tests/fixtures/issue675"
MIGRATION = SCAFFOLD / "docs/migration.md"
CHANGED = {
    "spec-dock/docs/canonical.md": (SCAFFOLD / "docs/canonical.md", FIXTURES / "canonical.md.0.9.9.txt"),
    "spec-dock/docs/migration.md": (MIGRATION, FIXTURES / "migration.md.0.9.9.txt"),
    "spec-dock/docs/reference_cli.md": (SCAFFOLD / "docs/reference_cli.md", FIXTURES / "reference_cli.md.0.9.9.txt"),
    "spec-dock/system/spec-dock-version": (
        SCAFFOLD / "system/spec-dock-version",
        FIXTURES / "spec-dock-version.0.9.9.txt",
    ),
}


def test_the_version_is_0_9_10_in_every_place() -> None:
    project = re.search(r'^version = "([^"]+)"', (ROOT / "pyproject.toml").read_text("utf-8"), re.M)
    assert project is not None and project.group(1) == "0.9.10"
    locked = re.search(
        r'\[\[package\]\]\nname = "spec-dock"\nversion = "([^"]+)"', (ROOT / "uv.lock").read_text("utf-8")
    )
    assert locked is not None and locked.group(1) == "0.9.10"
    assert (SCAFFOLD / "system/spec-dock-version").read_bytes() == b"0.9.10\n"
    assert (ROOT / "spec-dock/system/spec-dock-version").read_bytes() == b"0.9.10\n"


def test_the_migration_notes_describe_0_9_10_and_the_dogfood_copy_matches() -> None:
    current = MIGRATION.read_bytes()
    assert (ROOT / "spec-dock/docs/migration.md").read_bytes() == current
    text = current.decode("utf-8")
    headings = re.findall(r"^## (.+)$", text, re.M)
    assert headings.index("0.9.10 への更新") == headings.index("0.9.9 への更新") + 1
    [section] = re.findall(r"^## 0\.9\.10 への更新\n(.*?)(?=^## )", text, re.M | re.S)
    for token in (
        "installation update",
        "#677",
        "#678",
        "#679",
        "Antigravity",
        "~/.gemini/antigravity-cli/settings.json",
        "permissions.allow",
        "read_file",
        "write_file",
        "tools.antigravity",
        "CANONICAL_TOOL_SETTING_MISSING",
        "ANTIGRAVITY_AGENT",
        "Gemini",
        "4ad7471",
        "これから",
        "指揮の線",
        "子の数",
        "canonical.md",
        "reference_cli.md",
        "契約",
        "自動で起動し直",
        "0.9.9 に戻",
    ):
        assert token in section, token


def test_the_0_9_9_migration_section_only_gains_the_0_9_10_note() -> None:
    section_pattern = re.compile(r"^## 0\.9\.9 への更新\n(.*?)(?=^## )", re.M | re.S)
    [previous] = section_pattern.findall((FIXTURES / "migration.md.0.9.9.txt").read_bytes().decode("utf-8"))
    [current] = section_pattern.findall(MIGRATION.read_bytes().decode("utf-8"))
    lines = current.splitlines(keepends=True)
    [note_index] = [index for index, line in enumerate(lines) if line.startswith("- 0.9.10 の注")]
    assert note_index > 0 and lines[note_index - 1].startswith("- 『これから』")
    note = lines.pop(note_index)
    for token in ("0.9.10 への更新", "これから", "指揮の線", "Unscoped", "子の数"):
        assert token in note, token
    assert "".join(lines) == previous


def test_the_inventory_accepts_the_0_9_9_bytes_once() -> None:
    entries = {
        item["path"]: item for item in json.loads((ASSETS / "static-inventory.json").read_text("utf-8"))["files"]
    }
    for relative, (source, previous) in CHANGED.items():
        entry = entries[relative]
        current_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        previous_hash = hashlib.sha256(previous.read_bytes()).hexdigest()
        assert entry["sha256"] == current_hash, relative
        assert current_hash != previous_hash, relative
        assert entry["known_old_sha256"].count(previous_hash) == 1, relative
        assert len(entry["known_old_sha256"]) == len(set(entry["known_old_sha256"])), relative


def _run(capsys: pytest.CaptureFixture[str], *arguments: str) -> tuple[int, dict[str, Any]]:
    code = main([*arguments, "--json"])
    return code, json.loads(capsys.readouterr().out)


def test_installation_update_upgrades_a_0_9_9_consumer(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    code, initialized = _run(capsys, "installation", "init", str(target), "--yes")
    assert (code, initialized["status"]) == (0, "succeeded"), initialized["error"]
    for relative, (_, previous) in CHANGED.items():
        (target / relative).write_bytes(previous.read_bytes())

    backup = tmp_path / "backup"
    code, applied = _run(
        capsys, "installation", "update", "--target", str(target), "--backup-dir", str(backup), "--yes"
    )

    assert (code, applied["status"]) == (0, "succeeded"), applied["error"]
    result = applied["data"]["result"]
    assert sorted(result["changed_paths"]) == sorted(CHANGED)
    assert result["created_paths"] == []
    assert result["retired_paths"] == []
    for relative, (source, previous) in CHANGED.items():
        assert (target / relative).read_bytes() == source.read_bytes(), relative
        assert (backup / "static" / relative).read_bytes() == previous.read_bytes(), relative
