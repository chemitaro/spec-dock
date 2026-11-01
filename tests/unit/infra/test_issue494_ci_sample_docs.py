"""The CI sample and the canonical guide explain hosted runner cost and how to adapt it (iss-00494)."""

from __future__ import annotations

from pathlib import Path

from spec_dock.runtime.application.canonical_check import WORKFLOW_BRANCH_LINE

ROOT = Path(__file__).resolve().parents[3]
DOCS = ROOT / "src/spec_dock/assets/spec_dock/docs"
SAMPLE = DOCS / "ci/spec-dock-check.yml"
GUIDE = DOCS / "canonical.md"
HOOK_COMMAND = "spec-dock canonical check --json"


def test_the_sample_comments_explain_cost_and_adaptation() -> None:
    text = SAMPLE.read_text(encoding="utf-8")
    comments = "\n".join(line for line in text.splitlines() if line.lstrip().startswith("#"))
    for needle in ("費用", "workflow_dispatch", "runs-on", "pre-push", HOOK_COMMAND):
        assert needle in comments, needle


def test_the_sample_keeps_its_runtime_contract() -> None:
    text = SAMPLE.read_text(encoding="utf-8")
    assert text.count(WORKFLOW_BRANCH_LINE) == 1
    assert "runs-on: ubuntu-latest" in text
    assert f"run: {HOOK_COMMAND}" in text


def test_the_canonical_guide_explains_cost_and_the_pre_push_form() -> None:
    text = GUIDE.read_text(encoding="utf-8")
    for needle in ("費用", "workflow_dispatch", "runs-on", ".githooks/pre-push", HOOK_COMMAND):
        assert needle in text, needle


def test_the_dogfood_copies_match_the_shipped_assets() -> None:
    for relative in ("canonical.md", "ci/spec-dock-check.yml"):
        assert (ROOT / "spec-dock/docs" / relative).read_bytes() == (DOCS / relative).read_bytes(), relative


def test_the_inventory_accepts_the_previous_bytes() -> None:
    import json

    files = {
        e["path"]: e for e in json.loads((ROOT / "src/spec_dock/assets/static-inventory.json").read_text())["files"]
    }
    previous = {
        "spec-dock/docs/canonical.md": "4ee1612fa7f5ccdfc51fbd3167f280ce6dd49283cf1e89a31bdb93fbd9689f2e",
        "spec-dock/docs/ci/spec-dock-check.yml": "715ba5868ad31ea235acbfbcadbccb6f0d67a98062b9fd6a2bde5c516419cc70",
    }
    for path, digest in previous.items():
        assert digest in files[path]["known_old_sha256"], path
        assert files[path]["sha256"] != digest, path
