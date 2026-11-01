"""SpecDock 0.4.1: the version, its migration notes, and the upgrade path from the 0.4.0 assets (iss-00491)."""

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
SCAFFOLD = ROOT / "src/spec_dock/assets/spec_dock"
FIXTURES = ROOT / "tests/fixtures/issue491"
# The bytes 0.4.0 shipped (v0.4.0); a consumer holding them must be able to `installation update`.
PREVIOUS = {
    "spec-dock/docs/migration.md": FIXTURES / "migration-0.4.0.txt",
    "spec-dock/system/spec-dock-version": FIXTURES / "spec-dock-version-0.4.0.txt",
}
PROVIDER = {
    "spec-dock/docs/migration.md": SCAFFOLD / "docs/migration.md",
    "spec-dock/system/spec-dock-version": SCAFFOLD / "system/spec-dock-version",
}


def test_the_version_is_0_4_1_in_every_place() -> None:
    project = re.search(r'^version = "([^"]+)"', (ROOT / "pyproject.toml").read_text("utf-8"), re.M)
    assert project is not None and project.group(1) == "0.4.1"
    locked = re.search(r'\[\[package\]\]\nname = "spec-dock"\nversion = "([^"]+)"', (ROOT / "uv.lock").read_text("utf-8"))
    assert locked is not None and locked.group(1) == "0.4.1"
    for path in PROVIDER.values():
        assert path.exists()
    assert PROVIDER["spec-dock/system/spec-dock-version"].read_text("utf-8") == "0.4.1\n"


def test_the_migration_notes_describe_0_4_1_and_the_dogfood_copy_matches() -> None:
    text = PROVIDER["spec-dock/docs/migration.md"].read_text("utf-8")
    [section] = re.findall(r"^## 0\.4\.1 への更新\n(.*?)(?=^## )", text, re.M | re.S)
    for token in ("installation update", "details.cue_related", "SPEC_NO_TESTS", "--design-system"):
        assert token in section, token
    for relative, path in PROVIDER.items():
        assert (ROOT / relative).read_bytes() == path.read_bytes()


def test_the_inventory_accepts_the_0_4_0_bytes() -> None:
    entries = {
        item["path"]: item for item in json.loads((ROOT / "src/spec_dock/assets/static-inventory.json").read_text("utf-8"))["files"]
    }
    for relative, previous in PREVIOUS.items():
        entry = entries[relative]
        assert entry["sha256"] == hashlib.sha256(PROVIDER[relative].read_bytes()).hexdigest()
        assert hashlib.sha256(previous.read_bytes()).hexdigest() in entry["known_old_sha256"]


def _run(capsys: pytest.CaptureFixture[str], *arguments: str) -> tuple[int, dict[str, Any]]:
    code = main([*arguments, "--json"])
    return code, json.loads(capsys.readouterr().out)


def test_installation_update_upgrades_a_0_4_0_consumer(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert _run(capsys, "installation", "init", str(target), "--yes")[0] == 0
    for relative, previous in PREVIOUS.items():
        (target / relative).write_bytes(previous.read_bytes())
    backup = tmp_path / "backup"
    code, applied = _run(capsys, "installation", "update", "--target", str(target), "--backup-dir", str(backup), "--yes")
    assert (code, applied["status"]) == (0, "succeeded"), applied["error"]
    assert sorted(applied["data"]["result"]["changed_paths"]) == sorted(PREVIOUS)
    for relative, path in PROVIDER.items():
        assert (target / relative).read_bytes() == path.read_bytes()
        assert (backup / "static" / relative).read_bytes() == PREVIOUS[relative].read_bytes()
