"""The shipped operating guide follows the vNext command catalog."""

from __future__ import annotations

from pathlib import Path
import re
import shlex

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "src/spec_dock/assets/spec_dock"
DOCS = ASSETS / "docs"


def test_workbench_templates_use_current_destination_flag() -> None:
    # `workbench copy` was removed in 0.5.0, so no shipped .workbench/README.md may point at it.
    readmes = [ASSETS / "templates/root/.workbench/README.md"]
    readmes += [ASSETS / "templates/cue" / kind / ".workbench/README.md" for kind in ("initiative", "epic", "issue")]
    for path in readmes:
        assert "workbench copy" not in path.read_text(encoding="utf-8"), path


def test_command_reference_covers_all_public_leaves() -> None:
    from spec_dock.runtime.cli.catalog import LEAF_PATHS

    reference = (DOCS / "reference_cli.md").read_text()
    for leaf in LEAF_PATHS:
        assert f"`{leaf}`" in reference, leaf
    assert len(LEAF_PATHS) == 53


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


def readme_creation_commands() -> list[list[str]]:
    commands = [
        shlex.split(line)[1:]
        for line in (ROOT / "README.md").read_text().splitlines()
        if line.startswith("spec-dock scope create ")
    ]
    assert [command[2] for command in commands] == ["initiative", "epic", "issue"]
    return commands


def test_current_operating_links_and_sync_examples_follow_observation_contract() -> None:
    from spec_dock.runtime.cli.options import parse_vnext

    guide = (ROOT / "docs/sync-aggregation.md").read_text()
    commands = [shlex.split(line)[1:] for line in guide.splitlines() if line.startswith("spec-dock ")]
    assert [parse_vnext(command).command_path for command in commands] == [
        "workspace validate",
        "workspace sync",
        "workspace sync",
        "workspace doctor",
    ]
    assert [parse_vnext(command).source for command in commands if command[:2] == ["workspace", "sync"]] == [
        None,
        "github",
    ]
    assert "再生成せず" in guide and "unknown／partial" in guide and "自動修復しません" in guide
    agents = (ROOT / "AGENTS.md").read_text()
    current = agents.split("## SpecDock Agent-First Operations", 1)[1].split("## Dogfooding Warning", 1)[0]
    assert "PR #414 merged on 2026-10-04" in current
    assert "merge does not establish installation" in current
    assert "merge, and publication remain pending" not in current
    for relative in ("AGENTS.md", "docs/github-issue-integration.md", "docs/sync-aggregation.md"):
        path = ROOT / relative
        for link in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if not link.startswith(("https:", "http:", "#")):
                assert (path.parent / link.split("#", 1)[0]).exists(), (relative, link)
    reference = (DOCS / "reference_cli.md").read_text()
    assert "裸番号＋`--github-repo OWNER/REPO`" in reference
    assert "裸番号・Issue URL・任意filesystem pathは使えません" in reference
