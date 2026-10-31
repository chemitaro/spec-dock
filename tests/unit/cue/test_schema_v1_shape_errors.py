"""Shape errors fail the evaluation and name the field at fault, never a cycle (iss-00472 AC-06)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.support.cue import document, evaluate, write_scope

if TYPE_CHECKING:
    from pathlib import Path

GOOD = {"level": "strict", "reason": "公開の契約を変える"}


def _assert_fails_naming(
    tmp_path: Path, requirement: str, field: str, *, kind: str | None = "issue", design: str = "", plan: str = ""
) -> None:
    result = evaluate(write_scope(tmp_path, requirement, design, plan), kind)
    assert result.returncode != 0 and result.data is None, result
    assert field in result.stderr, result.stderr
    assert "cycle" not in result.stderr, result.stderr


@pytest.mark.parametrize(
    ("fields", "field"),
    [
        ({"assurance": GOOD}, "schema"),
        ({"schema": "specdock/v2", "assurance": GOOD}, "schema"),
        ({"schema": "specdock/v1"}, "assurance.level"),
        ({"schema": "specdock/v1", "assurance": {"reason": "理由"}}, "assurance.level"),
        ({"schema": "specdock/v1", "assurance": {"level": "medium", "reason": "理由"}}, "assurance.level"),
        ({"schema": "specdock/v1", "assurance": {"level": "Strict", "reason": "理由"}}, "assurance.level"),
        ({"schema": "specdock/v1", "assurance": {"level": "strict"}}, "assurance.reason"),
        ({"schema": "specdock/v1", "assurance": {"level": "strict", "reason": ""}}, "assurance.reason"),
        ({"schema": "specdock/v1", "assurance": {"level": "strict", "reason": " \n\t"}}, "assurance.reason"),
    ],
)
def test_a_missing_or_malformed_common_field_is_a_shape_error_naming_it(
    tmp_path: Path, fields: dict[str, object], field: str
) -> None:
    _assert_fails_naming(tmp_path, document(**fields), field)


@pytest.mark.parametrize("kind", [None, "task"])
def test_a_missing_or_unknown_kind_tag_is_a_shape_error_naming_kind(tmp_path: Path, kind: str | None) -> None:
    _assert_fails_naming(tmp_path, document(schema="specdock/v1", assurance=GOOD), "kind", kind=kind)


@pytest.mark.parametrize("rank", [0, 1, 3])
def test_a_document_cannot_move_the_rank_away_from_the_declared_level(tmp_path: Path, rank: int) -> None:
    requirement = document(schema="specdock/v1", assurance=GOOD) + f"_rank: {rank}\n"
    _assert_fails_naming(tmp_path, requirement, "_specdock.rank")


def test_a_document_may_restate_the_rank_of_its_declared_level(tmp_path: Path) -> None:
    requirement = document(schema="specdock/v1", assurance=GOOD) + "_rank: 2\n"
    assert evaluate(write_scope(tmp_path, requirement), "issue").ok


def _requirement(**fields: object) -> str:
    return document(schema="specdock/v1", assurance={"level": "light", "reason": "局所的"}, **fields)


@pytest.mark.parametrize(
    ("fields", "field"),
    [
        ({"requirements": {"R1": {"title": "保存できる"}}}, "requirements.R1"),
        ({"requirements": {"r-01": {"title": "保存できる"}}}, 'requirements."r-01"'),
        ({"requirements": {"R-1": {"title": "保存できる"}}}, 'requirements."R-1"'),
        ({"requirements": {"R-01": {}}}, 'requirements."R-01".title'),
        ({"requirements": {"R-01": {"title": "  "}}}, 'requirements."R-01".title'),
        ({"requirements": {"R-01": {"title": "一行目\n二行目"}}}, 'requirements."R-01".title'),
        ({"requirements": {"R-01": {"title": "保存できる", "text": ""}}}, 'requirements."R-01".text'),
        ({"failures": {"F1": {"title": "壊れた入力"}}}, "failures.F1"),
        ({"failures": {"F-01": {}}}, 'failures."F-01".title'),
        ({"purpose": ""}, "purpose"),
        ({"includes": [""]}, "includes"),
    ],
)
def test_a_malformed_requirement_document_is_a_shape_error_naming_the_field(
    tmp_path: Path, fields: dict[str, object], field: str
) -> None:
    _assert_fails_naming(tmp_path, _requirement(**fields), field)


@pytest.mark.parametrize(
    ("fields", "field"),
    [
        ({"design": {"D1": {"title": "評価の単位", "satisfies": []}}}, "design.D1"),
        ({"design": {"D-01": {"satisfies": []}}}, 'design."D-01".title'),
        ({"design": {"D-01": {"title": "評価の単位"}}}, 'design."D-01".satisfies'),
        ({"design": {"D-01": {"title": "評価の単位", "satisfies": "R-01"}}}, 'design."D-01".satisfies'),
        ({"current": " "}, "current"),
    ],
)
def test_a_malformed_design_document_is_a_shape_error_naming_the_field(
    tmp_path: Path, fields: dict[str, object], field: str
) -> None:
    _assert_fails_naming(tmp_path, _requirement(), design=document(**fields), field=field)


@pytest.mark.parametrize(
    ("fields", "field"),
    [
        ({"steps": {"S1": {"title": "型を書く", "realizes": []}}}, "steps.S1"),
        ({"steps": {"S-01": {"realizes": []}}}, 'steps."S-01".title'),
        ({"steps": {"S-01": {"title": "型を書く"}}}, 'steps."S-01".realizes'),
        ({"steps": {"S-01": {"title": "型を書く", "realizes": [], "status": "wip"}}}, 'steps."S-01".status'),
        ({"steps": {"S-01": {"title": "型を書く", "realizes": [], "after": "S-02"}}}, 'steps."S-01".after'),
        ({"steps": {"S-01": {"title": "型を書く", "realizes": [], "session": 1}}}, 'steps."S-01".session'),
        ({"tests": {"T1": {"title": "通る", "verifies": []}}}, "tests.T1"),
        ({"tests": {"T-01": {"title": "通る"}}}, 'tests."T-01".verifies'),
        ({"rollback": ""}, "rollback"),
        ({"execution": {"sessions": {"impl": {"model": 5}}}}, "execution.sessions.impl.model"),
        ({"execution": {"reviews": {"code": {"after": ["S-01"]}}}}, "execution.reviews.code.after"),
        ({"slices": {"iss-00001": {"covers": []}}}, 'slices."iss-00001"'),
    ],
)
def test_a_malformed_issue_plan_is_a_shape_error_naming_the_field(
    tmp_path: Path, fields: dict[str, object], field: str
) -> None:
    _assert_fails_naming(tmp_path, _requirement(), plan=document(**fields), field=field)


@pytest.mark.parametrize("kind", ["epic", "initiative"])
@pytest.mark.parametrize(
    ("fields", "field"),
    [
        ({"slices": {"iss-1": {"covers": []}}}, 'slices."iss-1"'),
        ({"slices": {"task-00001": {"covers": []}}}, 'slices."task-00001"'),
        ({"slices": {"iss-00001": {}}}, 'slices."iss-00001".covers'),
        ({"slices": {"iss-00001": {"covers": [], "after": "epic-00002"}}}, 'slices."iss-00001".after'),
        ({"steps": {"S-01": {"title": "型を書く", "realizes": []}}}, 'steps."S-01"'),
        ({"tests": {"T-01": {"title": "通る", "verifies": []}}}, 'tests."T-01"'),
    ],
)
def test_a_malformed_epic_or_initiative_plan_is_a_shape_error_naming_the_field(
    tmp_path: Path, kind: str, fields: dict[str, object], field: str
) -> None:
    _assert_fails_naming(tmp_path, _requirement(), plan=document(**fields), field=field, kind=kind)


@pytest.mark.parametrize(
    ("kind", "fields", "advice"),
    [
        ("issue", {"slices": {"iss-00001": {"covers": []}}}, "steps"),
        ("epic", {"steps": {"S-01": {"title": "型を書く", "realizes": []}}}, "slices"),
        ("initiative", {"tests": {"T-01": {"title": "通る", "verifies": []}}}, "slices"),
    ],
)
def test_a_field_of_the_other_kind_says_where_the_work_belongs(
    tmp_path: Path, kind: str, fields: dict[str, object], advice: str
) -> None:
    result = evaluate(write_scope(tmp_path, _requirement(), plan=document(**fields)), kind)
    assert not result.ok and "plan.cue" in result.stderr and advice in result.stderr, result.stderr
