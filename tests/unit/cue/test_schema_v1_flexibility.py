"""Only what is really needed is required; fields the type does not know may be added (iss-00472 AC-11, R-B1)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.support.cue import document, evaluate, write_scope

if TYPE_CHECKING:
    from pathlib import Path

EXTRA: dict[str, object] = {"owner": "利用者", "links": ["https://example.invalid/x"], "note": {"text": "自由な形"}}


def _issue(extra: dict[str, object]) -> tuple[str, str, str]:
    requirement = document(
        schema="specdock/v1",
        assurance={"level": "critical", "reason": "見本", **extra},
        requirements={"R-01": {"title": "保存できる", "acceptance": ["読める"], **extra}},
        failures={"F-01": {"title": "壊れた入力", "impact": "ない", "recovery": "直す", **extra}},
        glossary=extra,
    )
    design = document(design={"D-01": {"title": "保存の部品", "satisfies": ["R-01", "F-01"], **extra}}, diagrams=extra)
    plan = document(
        steps={"S-01": {"title": "保存を作る", "realizes": ["R-01"], "session": "impl", **extra}},
        tests={"T-01": {"title": "保存できる", "verifies": ["R-01", "F-01"], **extra}},
        rollback="戻す",
        execution={"sessions": {"impl": dict(extra)}, "reviews": {"code": {"after": "S-01", **extra}}, **extra},
        milestones=extra,
    )
    return requirement, design, plan


def test_an_issue_may_add_fields_everywhere_and_they_come_out_unchanged(tmp_path: Path) -> None:
    result = evaluate(write_scope(tmp_path, *_issue(EXTRA)), "issue")
    assert result.ok, result.stderr
    data = result.data
    assert data is not None
    assert result.reported_rules() == set()
    for item in (
        data["assurance"],
        data["requirements"]["R-01"],
        data["failures"]["F-01"],
        data["design"]["D-01"],
        data["steps"]["S-01"],
        data["tests"]["T-01"],
        data["execution"],
        data["execution"]["sessions"]["impl"],
        data["execution"]["reviews"]["code"],
    ):
        assert {key: item[key] for key in EXTRA} == EXTRA
    assert data["glossary"] == data["diagrams"] == data["milestones"] == EXTRA


@pytest.mark.parametrize("kind", ["epic", "initiative"])
def test_a_slice_may_add_fields(tmp_path: Path, kind: str) -> None:
    child = "iss-00001" if kind == "epic" else "epic-00001"
    requirement = document(
        schema="specdock/v1",
        assurance={"level": "light", "reason": "見本"},
        requirements={"R-01": {"title": "保存できる"}},
    )
    plan = document(slices={child: {"covers": ["R-01"], **EXTRA}})
    result = evaluate(write_scope(tmp_path, requirement, "", plan), kind)
    assert result.ok, result.stderr
    assert result.data is not None
    assert {key: result.data["slices"][child][key] for key in EXTRA} == EXTRA


@pytest.mark.parametrize(
    ("file", "fields", "field"),
    [
        ("requirement", {"requirements": {"REQ-01": {"title": "保存できる"}}}, 'requirements."REQ-01"'),
        ("requirement", {"failures": {"E-01": {"title": "壊れた入力"}}}, 'failures."E-01"'),
        ("design", {"design": {"note": {"title": "メモ", "satisfies": []}}}, "design.note"),
        ("plan", {"steps": {"step-1": {"title": "作る", "realizes": []}}}, 'steps."step-1"'),
        ("plan", {"tests": {"T-a": {"title": "通る", "verifies": []}}}, 'tests."T-a"'),
    ],
)
def test_a_numbered_map_takes_only_numbered_keys(
    tmp_path: Path, file: str, fields: dict[str, object], field: str
) -> None:
    files = {
        "requirement": document(schema="specdock/v1", assurance={"level": "light", "reason": "見本"}),
        "design": "",
        "plan": "",
    }
    files[file] = (files[file] or "package spec\n") + document(**fields).removeprefix("package spec\n")
    result = evaluate(write_scope(tmp_path, files["requirement"], files["design"], files["plan"]), "issue")
    assert not result.ok and field in result.stderr and "not allowed" in result.stderr, result.stderr
