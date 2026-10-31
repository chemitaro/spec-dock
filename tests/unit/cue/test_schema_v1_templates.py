"""The CUE templates pass the type at every level once their markers are filled (iss-00472 AC-05, RQ-13, RQ-14).

The templates live here as test fixtures; I-3 (iss-00474) moves them to spec-dock/templates/cue/<kind>/.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.support.cue import SCOPE_FILES, cue_string_body, evaluate

TEMPLATES = Path(__file__).resolve().parents[2] / "fixtures/cue/v1/templates"
KINDS = ("initiative", "epic", "issue")
LEVELS = ("light", "standard", "strict", "critical")
REASONS = [
    "既定の理由",
    'He said "fine" \\ and left',
    "一行目\n二行目\tタブ",
    "\\(not.interpolated) and \\n stays literal",
    "制御文字\x01と\x7fを含む",
]


def _fill(text: str, level: str, reason: str) -> str:
    return text.replace("{{ASSURANCE_LEVEL}}", level).replace("{{ASSURANCE_REASON}}", cue_string_body(reason))


def test_every_kind_has_the_three_documents_and_markers_only_in_its_requirement() -> None:
    for kind in KINDS:
        texts = {name: (TEMPLATES / kind / name).read_text(encoding="utf-8") for name in SCOPE_FILES}
        assert sorted(path.name for path in (TEMPLATES / kind).iterdir()) == sorted(SCOPE_FILES)
        requirement = texts["requirement.cue"]
        assert requirement.count('"{{ASSURANCE_LEVEL}}"') == 1 and requirement.count('"{{ASSURANCE_REASON}}"') == 1
        assert requirement.count('schema: "specdock/v1"') == 1
        for name in ("design.cue", "plan.cue"):
            assert "{{" not in texts[name] and "schema:" not in texts[name] and "assurance" not in texts[name]
        assert all(text.startswith("package spec\n") or "\npackage spec\n" in text for text in texts.values())


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("level", LEVELS)
@pytest.mark.parametrize("reason", REASONS)
def test_a_filled_template_passes_with_no_finding(tmp_path: Path, kind: str, level: str, reason: str) -> None:
    for name in SCOPE_FILES:
        (tmp_path / name).write_text(
            _fill((TEMPLATES / kind / name).read_text(encoding="utf-8"), level, reason), "utf-8"
        )
    result = evaluate(tmp_path, kind)
    assert result.ok, result.stderr
    assert result.reported_rules() == set()
    assert result.data is not None
    assert result.data["assurance"] == {"level": level, "reason": reason}
    assert result.data["kind"] == kind


@pytest.mark.parametrize("kind", KINDS)
def test_an_unfilled_template_does_not_pass(tmp_path: Path, kind: str) -> None:
    for name in SCOPE_FILES:
        (tmp_path / name).write_text((TEMPLATES / kind / name).read_text(encoding="utf-8"), "utf-8")
    result = evaluate(tmp_path, kind)
    assert not result.ok and "assurance.level" in result.stderr, result.stderr
