"""Raising the assurance level adds required fields; lowering it removes them (iss-00472 AC-02, R-B2)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.support.cue import document, evaluate, write_scope

if TYPE_CHECKING:
    from pathlib import Path

LEVELS = ("light", "standard", "strict", "critical")


def _requirement(level: str, requirement: dict[str, object], failure: dict[str, object]) -> str:
    return document(
        schema="specdock/v1",
        assurance={"level": level, "reason": "見本"},
        requirements={"R-01": requirement},
        failures={"F-01": failure},
    )


@pytest.mark.parametrize("level", LEVELS)
def test_acceptance_is_required_from_standard(tmp_path: Path, level: str) -> None:
    requirement = _requirement(
        level, {"title": "保存できる"}, {"title": "壊れた入力", "impact": "ない", "recovery": "直す"}
    )
    result = evaluate(write_scope(tmp_path / "without", requirement), "issue")
    if level == "light":
        assert result.ok, result.stderr
    else:
        assert not result.ok and 'requirements."R-01".acceptance' in result.stderr, result.stderr
    completed = _requirement(
        level,
        {"title": "保存できる", "acceptance": ["保存した値を読める"]},
        {"title": "壊れた入力", "impact": "ない", "recovery": "直す"},
    )
    assert evaluate(write_scope(tmp_path / "with", completed), "issue").ok


@pytest.mark.parametrize("level", LEVELS)
@pytest.mark.parametrize("missing", ["impact", "recovery"])
def test_failure_impact_and_recovery_are_required_from_strict(tmp_path: Path, level: str, missing: str) -> None:
    failure: dict[str, object] = {"title": "壊れた入力", "impact": "ない", "recovery": "直す"}
    del failure[missing]
    requirement = _requirement(level, {"title": "保存できる", "acceptance": ["読める"]}, failure)
    result = evaluate(write_scope(tmp_path, requirement), "issue")
    if level in ("light", "standard"):
        assert result.ok, result.stderr
    else:
        assert not result.ok and f'failures."F-01".{missing}' in result.stderr, result.stderr


def test_changing_standard_to_strict_fails_until_the_strict_fields_are_written(tmp_path: Path) -> None:
    standard = _requirement("standard", {"title": "保存できる", "acceptance": ["読める"]}, {"title": "壊れた入力"})
    assert evaluate(write_scope(tmp_path / "standard", standard), "issue").ok
    strict = standard.replace('"standard"', '"strict"')
    result = evaluate(write_scope(tmp_path / "strict", strict), "issue")
    assert not result.ok
    assert 'failures."F-01".impact' in result.stderr and 'failures."F-01".recovery' in result.stderr
    added = _requirement(
        "strict",
        {"title": "保存できる", "acceptance": ["読める"]},
        {"title": "壊れた入力", "impact": "ない", "recovery": "直す"},
    )
    assert evaluate(write_scope(tmp_path / "added", added), "issue").ok


@pytest.mark.parametrize("level", LEVELS)
def test_a_document_complete_for_critical_passes_at_every_lower_level(tmp_path: Path, level: str) -> None:
    requirement = _requirement(
        level,
        {"title": "保存できる", "acceptance": ["読める"]},
        {"title": "壊れた入力", "impact": "ない", "recovery": "直す"},
    )
    assert evaluate(write_scope(tmp_path, requirement), "issue").ok
