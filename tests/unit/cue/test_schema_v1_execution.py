"""`execution` is checked only for its references; model and effort may be any string (iss-00472 AC-03, R-D4)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.support.cue import document, evaluate, write_scope

if TYPE_CHECKING:
    from pathlib import Path

NAMES = [
    "",
    "opus",
    "claude-opus-5-5",
    "xhigh",
    "推論・高",
    "x/y:z@1 [beta]",
    "  ",
    "line\nbreak",
    "\\(not interpolated)",
]


def _scope(tmp_path: Path, execution: object) -> Path:
    requirement = document(
        schema="specdock/v1",
        assurance={"level": "critical", "reason": "見本"},
        requirements={"R-01": {"title": "保存できる", "acceptance": ["読める"]}},
    )
    design = document(design={"D-01": {"title": "保存の部品", "satisfies": ["R-01"]}})
    plan = document(
        steps={"S-01": {"title": "保存を作る", "realizes": ["R-01"], "session": "impl"}},
        tests={"T-01": {"title": "保存できる", "verifies": ["R-01"]}},
        rollback="戻す",
        execution=execution,
    )
    return write_scope(tmp_path, requirement, design, plan)


@pytest.mark.parametrize("name", NAMES)
def test_any_model_or_effort_string_is_accepted(tmp_path: Path, name: str) -> None:
    execution = {
        "sessions": {"impl": {"task": "実装する", "model": name, "effort": name, "rationale": "見本"}},
        "reviews": {"code": {"role": name, "after": "S-01", "model": name, "effort": name}},
    }
    result = evaluate(_scope(tmp_path, execution), "issue")
    assert result.ok, result.stderr
    assert result.findings["execution-reference"] == []
    assert result.data is not None
    assert result.data["execution"]["sessions"]["impl"]["model"] == name


def test_sessions_and_reviews_need_no_field_at_all(tmp_path: Path) -> None:
    result = evaluate(_scope(tmp_path, {"sessions": {"impl": {}}, "reviews": {"final": {}}}), "issue")
    assert result.ok, result.stderr
    assert result.reported_rules() == set()


def test_a_review_after_a_dropped_step_still_names_an_existing_step(tmp_path: Path) -> None:
    scope = _scope(tmp_path, {"sessions": {"impl": {}}, "reviews": {"code": {"after": "S-02"}}})
    plan = (scope / "plan.cue").read_text(encoding="utf-8")
    plan += '"steps": "S-02": {"title": "やめた", "realizes": ["R-01"], "status": "dropped"}\n'
    (scope / "plan.cue").write_text(plan, encoding="utf-8")
    result = evaluate(scope, "issue")
    assert result.ok, result.stderr
    assert result.findings["execution-reference"] == []
