"""The 0.5.0 bytes of the docs that describe the parent-completion rule stay accepted (iss-00520)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests/fixtures/issue520"
CASES = [
    ("spec-dock/docs/reference_cli.md", "reference_cli.md", "spec_dock/docs/reference_cli.md"),
    ("spec-dock/docs/cli-redesign-guide.html", "cli-redesign-guide.html", "spec_dock/docs/cli-redesign-guide.html"),
    (".agents/skills/spec-dock/SKILL.md", "SKILL.md", "install_root/.agents/skills/spec-dock/SKILL.md"),
]


@pytest.mark.parametrize(("installed", "fixture", "source"), CASES)
def test_the_inventory_accepts_the_0_5_0_bytes(installed: str, fixture: str, source: str) -> None:
    inventory = json.loads((ROOT / "src/spec_dock/assets/static-inventory.json").read_text("utf-8"))
    entry = next(item for item in inventory["files"] if item["path"] == installed)
    previous = (FIXTURES / f"{fixture}.0.5.0.txt").read_bytes()
    current = (ROOT / "src/spec_dock/assets" / source).read_bytes()
    assert hashlib.sha256(previous).hexdigest() in entry["known_old_sha256"]
    assert hashlib.sha256(current).hexdigest() == entry["sha256"]
    assert previous != current
