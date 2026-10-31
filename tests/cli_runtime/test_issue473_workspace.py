"""`workspace validate` and `doctor` with Markdown and CUE Scopes side by side (iss-00473 AC-12; R-H2)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from tests.support.canonical_scopes import CanonicalWorld
from tests.support.cue_scopes import hide_cue, place_sample

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> CanonicalWorld:
    hide_cue(monkeypatch)  # neither command calls cue
    world = CanonicalWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "Plan")
    world.scope("epic", 2, "Core", parent=1)
    world.scope("issue", 3, "CUE leaf", parent=2, documents=())
    world.scope("issue", 4, "Markdown leaf", parent=2)
    place_sample(world.catalog / world.relative("issue", 3), "issue-strict-complete")
    return world


def findings(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return payload["data"]["result"]["findings"]


def test_cue_and_markdown_scopes_side_by_side_are_valid(world: CanonicalWorld) -> None:
    code, payload = world.run("workspace", "validate", "--require-nodes")
    assert code == 0, payload
    assert findings(payload) == []
    code, payload = world.run("workspace", "doctor")
    assert not [item for item in payload["data"]["findings"] if item["code"].startswith("SCOPE_")], payload


def test_a_cue_scope_needs_its_own_document_set(world: CanonicalWorld) -> None:
    (world.catalog / world.relative("issue", 3) / "plan.cue").unlink()
    (world.catalog / world.relative("issue", 4) / "plan.md").unlink()
    code, payload = world.run("workspace", "validate")
    assert code == 7
    missing = {
        item["details"]["scope_id"]: item["details"]["missing"]
        for item in findings(payload)
        if item["code"] == "SCOPE_DOCUMENT_MISSING"
    }
    assert missing == {"iss-00003": ["plan.cue"], "iss-00004": ["plan.md"]}


def test_both_requirement_files_are_a_format_conflict(world: CanonicalWorld) -> None:
    (world.catalog / world.relative("issue", 3) / "requirement.md").write_text("# r\n", encoding="utf-8")
    code, payload = world.run("workspace", "validate")
    assert code == 7
    [conflict] = [item for item in findings(payload) if item["code"] == "SCOPE_FORMAT_CONFLICT"]
    assert conflict["details"] == {"scope_id": "iss-00003", "path": "00000-00999/iss-00003"}
    assert "SCOPE_DOCUMENT_MISSING" not in {item["code"] for item in findings(payload)}
    code, payload = world.run("workspace", "doctor")
    assert "SCOPE_FORMAT_CONFLICT" in {item["code"] for item in payload["data"]["findings"]}


def test_the_explanation_is_not_judged_here(world: CanonicalWorld) -> None:
    (world.catalog / world.relative("issue", 3) / "explanation.html").unlink()
    code, payload = world.run("workspace", "validate")
    assert code == 0, payload
