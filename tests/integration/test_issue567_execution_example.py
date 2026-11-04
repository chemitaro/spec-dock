"""The shipped execution examples separate the spec session from the impl session (iss-00567 R-01, R-02)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "src/spec_dock/assets"
FIXTURES = ROOT / "tests/fixtures/issue567"
GUIDE = ASSETS / "spec_dock/docs/authoring/cue.md"
TEMPLATE = ASSETS / "spec_dock/templates/cue/issue/plan.cue"
SHIPPED = {
    "spec-dock/docs/authoring/cue.md": GUIDE,
    "spec-dock/templates/cue/issue/plan.cue": TEMPLATE,
}
BEFORE = {
    "spec-dock/docs/authoring/cue.md": FIXTURES / "cue.md.before.txt",
    "spec-dock/templates/cue/issue/plan.cue": FIXTURES / "issue-plan-cue-before.txt",
}
OLD_EXAMPLE = '"仕様化と実装"'
NOTE = "セッションのモデルと推論は起動のときに決まる"


def test_no_shipped_example_puts_spec_and_impl_in_one_session() -> None:
    for path in SHIPPED.values():
        assert OLD_EXAMPLE not in path.read_text("utf-8"), path


def test_the_examples_split_spec_and_impl_sessions() -> None:
    guide = GUIDE.read_text("utf-8")
    template = TEMPLATE.read_text("utf-8")
    assert guide.count("spec: {task:") >= 1 and guide.count('impl: {task: "実装"') >= 2
    assert "spec: {task:" in template and 'impl: {task: "実装"' in template
    assert "実装のセッション（`impl`）" in guide


def test_the_start_time_note_is_in_the_guide_and_template() -> None:
    assert NOTE in GUIDE.read_text("utf-8")
    assert NOTE in TEMPLATE.read_text("utf-8")


def test_the_inventory_and_dogfood_copies_follow_and_accept_the_previous_bytes() -> None:
    entries = {
        item["path"]: item for item in json.loads((ASSETS / "static-inventory.json").read_text("utf-8"))["files"]
    }
    for path, provider in SHIPPED.items():
        entry = entries[path]
        assert entry["sha256"] == hashlib.sha256(provider.read_bytes()).hexdigest()
        assert hashlib.sha256(BEFORE[path].read_bytes()).hexdigest() in entry["known_old_sha256"]
        assert (ROOT / path).read_bytes() == provider.read_bytes()
