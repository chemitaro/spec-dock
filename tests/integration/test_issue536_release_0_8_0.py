"""SpecDock 0.8.0: the version, its migration notes, and the upgrade path from the 0.7.0 assets (iss-00536)."""

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
F536 = ROOT / "tests/fixtures/issue536"
# Installed path -> (provider source, the bytes 0.7.0 shipped). A 0.7.0 consumer must be able to `installation update`.
CHANGED = {
    "spec-dock/docs/reference_cli.md": (SCAFFOLD / "docs/reference_cli.md", F536 / "reference_cli.md.0.7.0.txt"),
    "spec-dock/docs/authoring/cue.md": (SCAFFOLD / "docs/authoring/cue.md", F536 / "cue.md.0.7.0.txt"),
    "spec-dock/templates/cue/issue/plan.cue": (
        SCAFFOLD / "templates/cue/issue/plan.cue",
        F536 / "issue-plan.cue.0.7.0.txt",
    ),
    "spec-dock/docs/migration.md": (SCAFFOLD / "docs/migration.md", F536 / "migration.md.0.7.0.txt"),
    "spec-dock/system/spec-dock-version": (SCAFFOLD / "system/spec-dock-version", F536 / "spec-dock-version.0.7.0.txt"),
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_the_version_is_0_8_0_in_every_place() -> None:
    project = re.search(r'^version = "([^"]+)"', (ROOT / "pyproject.toml").read_text("utf-8"), re.M)
    assert project is not None and project.group(1) == "0.8.0"
    locked = re.search(
        r'\[\[package\]\]\nname = "spec-dock"\nversion = "([^"]+)"', (ROOT / "uv.lock").read_text("utf-8")
    )
    assert locked is not None and locked.group(1) == "0.8.0"
    assert (SCAFFOLD / "system/spec-dock-version").read_text("utf-8") == "0.8.0\n"
    assert (ROOT / "spec-dock/system/spec-dock-version").read_text("utf-8") == "0.8.0\n"


def test_the_migration_notes_describe_0_8_0_and_the_dogfood_copy_matches() -> None:
    text = (SCAFFOLD / "docs/migration.md").read_text("utf-8")
    headings = re.findall(r"^## (.+)$", text, re.M)
    assert headings.index("0.8.0 への更新") == headings.index("0.7.0 への更新") + 1
    [section] = re.findall(r"^## 0\.8\.0 への更新\n(.*?)(?=^## )", text, re.M | re.S)
    for token in (
        "installation update",
        "/scopes/<ID>/doc",
        "SERVER_RESTART_REQUIRED",
        "details",
        "/api/v1/todos",
        "/api/v1/r/<repo>/todos",
        "specdock.todo-list/v1",
        "DASHBOARD_TODO_FILTER_INVALID",
        "/todos",
        "docs/authoring/cue.md",
        "templates/cue/issue/plan.cue",
        "age_seconds",
        "自動で起動し直",
    ):
        assert token in section, token
    installed = ROOT / "spec-dock/docs/migration.md"
    if installed.exists():
        assert installed.read_bytes() == (SCAFFOLD / "docs/migration.md").read_bytes()


def test_the_inventory_accepts_the_0_7_0_bytes_once() -> None:
    entries = {
        item["path"]: item for item in json.loads((ASSETS / "static-inventory.json").read_text("utf-8"))["files"]
    }
    for relative, (source, previous) in CHANGED.items():
        entry = entries[relative]
        assert entry["sha256"] == _sha(source.read_bytes()), relative
        assert _sha(previous.read_bytes()) in entry["known_old_sha256"], relative
        assert len(entry["known_old_sha256"]) == len(set(entry["known_old_sha256"])), relative
        assert previous.read_bytes() != source.read_bytes(), relative


def _run(capsys: pytest.CaptureFixture[str], *arguments: str) -> tuple[int, dict[str, Any]]:
    code = main([*arguments, "--json"])
    return code, json.loads(capsys.readouterr().out)


def test_installation_update_upgrades_a_0_7_0_consumer(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert _run(capsys, "installation", "init", str(target), "--yes")[0] == 0
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
    for relative, (source, previous) in CHANGED.items():
        assert (target / relative).read_bytes() == source.read_bytes(), relative
        assert (backup / "static" / relative).read_bytes() == previous.read_bytes(), relative
