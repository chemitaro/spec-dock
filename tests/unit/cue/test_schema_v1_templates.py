"""The CUE templates pass the type at every level once their markers are filled (iss-00472 AC-05, RQ-13, RQ-14).

I-3 (iss-00474) moved them from the test fixtures to the shipped templates/cue/<kind>/ and fills the markers with
the runtime's own replacements.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from spec_dock.runtime.domain.assurance import Assurance, assurance_replacements
from tests.support.cue import SCOPE_FILES, cue_string_body, evaluate

TEMPLATES = Path(__file__).resolve().parents[3] / "src/spec_dock/assets/spec_dock/templates/cue"
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
    for marker, value in assurance_replacements(Assurance(level, reason)).items():
        text = text.replace(marker, value)
    return text


def _fill_with_the_test_helper(text: str, level: str, reason: str) -> str:
    return text.replace("{{ASSURANCE_LEVEL}}", level).replace("{{ASSURANCE_REASON}}", cue_string_body(reason))


def test_every_kind_has_the_three_documents_and_markers_only_in_its_requirement() -> None:
    for kind in KINDS:
        texts = {name: (TEMPLATES / kind / name).read_text(encoding="utf-8") for name in SCOPE_FILES}
        assert set(SCOPE_FILES) <= {path.name for path in (TEMPLATES / kind).iterdir()}
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


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("reason", REASONS)
def test_the_runtime_and_the_test_helper_fill_the_same_value(tmp_path: Path, kind: str, reason: str) -> None:
    """The two escapes may differ as text; what `cue` reads back from either is the same reason."""
    values = []
    for fill, name in ((_fill, "runtime"), (_fill_with_the_test_helper, "helper")):
        directory = tmp_path / name
        directory.mkdir()
        for document in SCOPE_FILES:
            text = (TEMPLATES / kind / document).read_text(encoding="utf-8")
            (directory / document).write_text(fill(text, "standard", reason), "utf-8")
        result = evaluate(directory, kind)
        assert result.ok, result.stderr
        assert result.data is not None
        values.append(result.data["assurance"])
    assert values[0] == values[1] == {"level": "standard", "reason": reason}
