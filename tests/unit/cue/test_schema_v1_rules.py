"""Connection rules: each violation reaches `findings` from its stage up, and only there (iss-00472 AC-01, AC-12).

Every case starts from a Scope that satisfies all rules at critical and adds one violation. The expected rules
and stages are written out from the rule table in design.md section 5, not computed from the type.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import pytest

from tests.support.cue import Evaluation, document, evaluate, write_scope

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

LEVELS = ("light", "standard", "strict", "critical")
STAGES = {
    "unknown-reference": 0,
    "requirement-without-step": 0,
    "requirement-without-design": 1,
    "requirement-without-test": 1,
    "orphan-step": 2,
    "failure-without-test": 2,
    "rollback-missing": 3,
    "execution-reference": 0,
}
SCOPE_FILES = ("requirement.cue", "design.cue", "plan.cue")

Docs = dict[str, dict[str, Any]]


def _requirement_doc() -> dict[str, Any]:
    return {
        "schema": "specdock/v1",
        "assurance": {"level": "critical", "reason": "見本"},
        "requirements": {
            "R-01": {"title": "保存できる", "acceptance": ["保存した値を読める"]},
            "R-02": {"title": "消せる", "acceptance": ["消した値は読めない"]},
        },
        "failures": {"F-01": {"title": "壊れた入力は保存しない", "impact": "ない", "recovery": "入力を直す"}},
    }


def issue_base() -> Docs:
    return {
        "requirement": _requirement_doc(),
        "design": {
            "design": {
                "D-01": {"title": "保存の部品", "satisfies": ["R-01"]},
                "D-02": {"title": "削除の部品", "satisfies": ["R-02", "F-01"]},
            }
        },
        "plan": {
            "steps": {
                "S-01": {"title": "保存を作る", "realizes": ["R-01"], "status": "done", "session": "impl"},
                "S-02": {"title": "削除を作る", "realizes": ["R-02", "F-01"], "after": ["S-01"], "session": "impl"},
            },
            "tests": {
                "T-01": {"title": "保存できる", "verifies": ["R-01"]},
                "T-02": {"title": "消せる", "verifies": ["R-02"]},
                "T-03": {"title": "壊れた入力を拒む", "verifies": ["F-01"]},
            },
            "rollback": "この PR を戻す",
            "execution": {
                "sessions": {"impl": {"model": "opus", "effort": "high"}},
                "reviews": {"code": {"after": "S-02", "model": "opus", "effort": "high"}},
            },
        },
    }


def parent_base(child: str) -> Docs:
    first, second = f"{child}-00001", f"{child}-00002"
    return {
        "requirement": _requirement_doc(),
        "design": {
            "design": {
                "D-01": {"title": "保存の契約", "satisfies": ["R-01"]},
                "D-02": {"title": "削除の契約", "satisfies": ["R-02"]},
            }
        },
        "plan": {
            "slices": {
                first: {"covers": ["R-01", "F-01"], "session": "coord"},
                second: {"covers": ["R-02"], "after": [first]},
            },
            "rollback": "子の PR を戻す",
            "execution": {
                "sessions": {"coord": {"model": "opus", "effort": "high"}},
                "reviews": {"gate": {"after": second}},
            },
        },
    }


@dataclass(frozen=True)
class Case:
    name: str
    mutate: Callable[[Docs], None]
    expected: dict[str, list[str]]  # rule -> ids, sorted


def _set(path: tuple[str, ...], value: object) -> Callable[[Docs], None]:
    def mutate(docs: Docs) -> None:
        target: Any = docs
        for key in path[:-1]:
            target = target.setdefault(key, {})
        target[path[-1]] = value

    return mutate


def _all(*changes: Callable[[Docs], None]) -> Callable[[Docs], None]:
    def mutate(docs: Docs) -> None:
        for change in changes:
            change(docs)

    return mutate


def _drop(path: tuple[str, ...]) -> Callable[[Docs], None]:
    def mutate(docs: Docs) -> None:
        target: Any = docs
        for key in path[:-1]:
            target = target[key]
        del target[path[-1]]

    return mutate


R03 = ("requirement", "requirements", "R-03")
R03_VALUE = {"title": "一覧できる", "acceptance": ["一覧に出る"]}

ISSUE_CASES = [
    Case(
        "design-satisfies-unknown",
        _set(("design", "design", "D-01", "satisfies"), ["R-01", "R-09"]),
        {"unknown-reference": ["D-01"]},
    ),
    Case(
        "step-realizes-unknown",
        _set(("plan", "steps", "S-02", "realizes"), ["R-02", "F-01", "F-09"]),
        {"unknown-reference": ["S-02"]},
    ),
    Case("step-after-unknown", _set(("plan", "steps", "S-02", "after"), ["S-09"]), {"unknown-reference": ["S-02"]}),
    Case(
        "test-verifies-unknown",
        _set(("plan", "tests", "T-01", "verifies"), ["R-01", "R-1"]),
        {"unknown-reference": ["T-01"]},
    ),
    Case(
        "requirement-without-step",
        _all(
            _set(R03, R03_VALUE),
            _set(("design", "design", "D-03"), {"title": "一覧の部品", "satisfies": ["R-03"]}),
            _set(("plan", "tests", "T-04"), {"title": "一覧できる", "verifies": ["R-03"]}),
        ),
        {"requirement-without-step": ["R-03"]},
    ),
    Case(
        "requirement-realized-only-by-a-dropped-step",
        _all(
            _set(R03, R03_VALUE),
            _set(("design", "design", "D-03"), {"title": "一覧の部品", "satisfies": ["R-03"]}),
            _set(("plan", "steps", "S-03"), {"title": "一覧を作る", "realizes": ["R-03"], "status": "dropped"}),
            _set(("plan", "tests", "T-04"), {"title": "一覧できる", "verifies": ["R-03"]}),
        ),
        {"requirement-without-step": ["R-03"]},
    ),
    Case(
        "requirement-without-design",
        _all(
            _set(R03, R03_VALUE),
            _set(("plan", "steps", "S-03"), {"title": "一覧を作る", "realizes": ["R-03"]}),
            _set(("plan", "tests", "T-04"), {"title": "一覧できる", "verifies": ["R-03"]}),
        ),
        {"requirement-without-design": ["R-03"]},
    ),
    Case(
        "requirement-without-test",
        _all(
            _set(R03, R03_VALUE),
            _set(("design", "design", "D-03"), {"title": "一覧の部品", "satisfies": ["R-03"]}),
            _set(("plan", "steps", "S-03"), {"title": "一覧を作る", "realizes": ["R-03"]}),
        ),
        {"requirement-without-test": ["R-03"]},
    ),
    Case(
        "orphan-step",
        _set(("plan", "steps", "S-03"), {"title": "掃除する", "realizes": []}),
        {"orphan-step": ["S-03"]},
    ),
    Case(
        "dropped-step-with-no-requirement",
        _set(("plan", "steps", "S-03"), {"title": "掃除する", "realizes": [], "status": "dropped"}),
        {},
    ),
    Case(
        "failure-without-test",
        _set(("requirement", "failures", "F-02"), {"title": "空の入力", "impact": "ない", "recovery": "入力する"}),
        {"failure-without-test": ["F-02"]},
    ),
    Case("rollback-missing", _drop(("plan", "rollback")), {"rollback-missing": ["rollback"]}),
    Case(
        "step-session-unknown", _set(("plan", "steps", "S-01", "session"), "review"), {"execution-reference": ["S-01"]}
    ),
    Case(
        "review-after-unknown",
        _set(("plan", "execution", "reviews", "code", "after"), "S-09"),
        {"execution-reference": ["execution.reviews.code"]},
    ),
    Case("step-session-without-execution", _drop(("plan", "execution")), {"execution-reference": ["S-01", "S-02"]}),
]


def parent_cases(child: str) -> list[Case]:
    first, second, third = f"{child}-00001", f"{child}-00002", f"{child}-00003"
    return [
        Case(
            "design-satisfies-unknown",
            _set(("design", "design", "D-02", "satisfies"), ["R-02", "F-09"]),
            {"unknown-reference": ["D-02"]},
        ),
        Case(
            "slice-covers-unknown",
            _set(("plan", "slices", first, "covers"), ["R-01", "F-01", "R-09"]),
            {"unknown-reference": [first]},
        ),
        Case(
            "slice-after-unknown",
            _set(("plan", "slices", second, "after"), [f"{child}-00009"]),
            {"unknown-reference": [second]},
        ),
        Case(
            "requirement-not-covered",
            _all(
                _set(R03, R03_VALUE), _set(("design", "design", "D-03"), {"title": "一覧の契約", "satisfies": ["R-03"]})
            ),
            {"requirement-without-step": ["R-03"], "requirement-without-test": ["R-03"]},
        ),
        Case(
            "requirement-without-design",
            _all(_set(R03, R03_VALUE), _set(("plan", "slices", second, "covers"), ["R-02", "R-03"])),
            {"requirement-without-design": ["R-03"]},
        ),
        Case("orphan-slice", _set(("plan", "slices", third), {"covers": []}), {"orphan-step": [third]}),
        Case(
            "failure-not-covered",
            _set(("requirement", "failures", "F-02"), {"title": "空の入力", "impact": "ない", "recovery": "入力する"}),
            {"failure-without-test": ["F-02"]},
        ),
        Case("rollback-missing", _drop(("plan", "rollback")), {"rollback-missing": ["rollback"]}),
        Case(
            "slice-session-unknown",
            _set(("plan", "slices", second, "session"), "missing"),
            {"execution-reference": [second]},
        ),
        Case(
            "review-after-unknown",
            _set(("plan", "execution", "reviews", "gate", "after"), "S-01"),
            {"execution-reference": ["execution.reviews.gate"]},
        ),
        Case("slice-session-without-execution", _drop(("plan", "execution")), {"execution-reference": [first]}),
    ]


KINDS: dict[str, tuple[Callable[[], Docs], list[Case]]] = {
    "issue": (issue_base, ISSUE_CASES),
    "epic": (lambda: parent_base("iss"), parent_cases("iss")),
    "initiative": (lambda: parent_base("epic"), parent_cases("epic")),
}
MATRIX = [
    pytest.param(kind, case, level, id=f"{kind}-{case.name}-{level}")
    for kind, (_, cases) in KINDS.items()
    for case in cases
    for level in LEVELS
]


def _evaluate(tmp_path: Path, kind: str, docs: Docs, level: str) -> Evaluation:
    docs = copy.deepcopy(docs)
    docs["requirement"]["assurance"]["level"] = level
    scope = write_scope(tmp_path, document(**docs["requirement"]), document(**docs["design"]), document(**docs["plan"]))
    return evaluate(scope, kind)


def _active_rules(level: str, *, execution: bool) -> set[str]:
    rank = LEVELS.index(level)
    return {rule for rule, stage in STAGES.items() if stage <= rank and (rule != "execution-reference" or execution)}


@pytest.mark.parametrize("kind", list(KINDS))
@pytest.mark.parametrize("level", LEVELS)
def test_the_complete_scope_has_no_finding_and_lists_every_rule_of_its_level(
    tmp_path: Path, kind: str, level: str
) -> None:
    result = _evaluate(tmp_path, kind, KINDS[kind][0](), level)
    assert result.ok, result.stderr
    assert result.reported_rules() == set()
    assert set(result.findings) == _active_rules(level, execution=True)


@pytest.mark.parametrize(("kind", "case", "level"), MATRIX)
def test_one_violation_reaches_exactly_its_rules_from_their_stage_up(
    tmp_path: Path, kind: str, case: Case, level: str
) -> None:
    docs = KINDS[kind][0]()
    case.mutate(docs)
    result = _evaluate(tmp_path, kind, docs, level)
    assert result.ok, result.stderr
    rank = LEVELS.index(level)
    expected = {rule: ids for rule, ids in case.expected.items() if STAGES[rule] <= rank}
    reported = {rule: [item["id"] for item in items] for rule, items in result.findings.items() if items}
    assert reported == expected


def test_every_rule_is_exercised_for_every_kind() -> None:
    for _, cases in KINDS.values():
        assert set().union(*(case.expected for case in cases)) == set(STAGES)


@pytest.mark.parametrize(("kind", "case"), [(kind, case) for kind, (_, cases) in KINDS.items() for case in cases])
def test_every_finding_names_its_item_and_the_file_to_fix(tmp_path: Path, kind: str, case: Case) -> None:
    docs = KINDS[kind][0]()
    case.mutate(docs)
    result = _evaluate(tmp_path, kind, docs, "critical")
    assert result.ok, result.stderr
    for items in result.findings.values():
        assert items == sorted(items, key=lambda item: (item["id"], item["message"]))
        for item in items:
            assert item["id"] and item["message"].strip() and item["hint"].strip(), item
            assert any(name in item["hint"] for name in SCOPE_FILES), item
