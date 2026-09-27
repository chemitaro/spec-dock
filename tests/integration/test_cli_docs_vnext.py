"""The shipped operating guide follows the vNext command catalog."""

from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "src/spec_dock/assets/spec_dock"
DOCS = ASSETS / "docs"
sys.path.insert(0, str(ASSETS / "scripts"))


def test_workbench_templates_use_current_destination_flag() -> None:
    for kind in ("root", "initiative", "epic", "issue"):
        readme = (ASSETS / "templates" / kind / ".workbench/README.md").read_text(encoding="utf-8")
        assert "workbench copy --scope <full-id> --to-worktree <linked-worktree>" in readme
        assert "workbench copy --scope <full-id> --to <linked-worktree>" not in readme


def test_command_reference_covers_all_public_leaves() -> None:
    from spec_dock_runtime.cli.catalog import LEAF_PATHS

    reference = (DOCS / "reference_cli.md").read_text()
    for leaf in LEAF_PATHS:
        assert f"`{leaf}`" in reference, leaf
    assert len(LEAF_PATHS) == 44


def test_current_docs_do_not_instruct_removed_commands() -> None:
    current = [ROOT / "README.md", ROOT / "src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md"]
    current += [p for p in DOCS.rglob("*.md") if "historical" not in p.parts and p.name != "migration.md"]
    removed = re.compile(
        r"(?:\./spec-dock/scripts/)?spec-dock\s+(?:new|issue|deps|sync|validate|update|uninstall|delete|close)(?:\s|$)"
    )
    for path in current:
        assert not removed.search(path.read_text()), path


def test_offline_explanation_is_shipped_and_linked() -> None:
    guide = DOCS / "cli-redesign-guide.html"
    assert guide.exists()
    assert "<html" in guide.read_text().lower()
    assert "cli-redesign-guide.html" in (DOCS / "README.md").read_text()
    assert "reference_cli.md" in (DOCS / "README.md").read_text()
