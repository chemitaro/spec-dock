"""A repository type in package spec adds constraints and rules on top of SpecDock's (iss-00472 AC-04, R-B6)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.support.cue import document, evaluate, write_scope

if TYPE_CHECKING:
    from pathlib import Path

# A repository rule set: execution becomes required from standard, requirements need an owner from strict,
# and a local rule lists steps that name no session.
OVERLAY = """package spec

if _rank >= 1 {
	execution!: _
}
if _rank >= 2 {
	requirements: [_]: owner!: string
}
findings: "local-step-without-session": [for k, s in steps if s.session == _|_ {
	id:      k
	message: "\\(k) に session がありません"
	hint:    "plan.cue の steps.\\"\\(k)\\".session を書く"
}]
"""


def _overlay(tmp_path: Path) -> Path:
    directory = tmp_path / "repository-type"
    directory.mkdir()
    (directory / "local.cue").write_text(OVERLAY, encoding="utf-8")
    return directory


def _scope(tmp_path: Path, level: str, *, owner: bool, execution: bool) -> Path:
    requirement: dict[str, object] = {"title": "保存できる", "acceptance": ["読める"]}
    if owner:
        requirement["owner"] = "利用者"
    plan: dict[str, object] = {
        "steps": {
            "S-01": {"title": "保存を作る", "realizes": ["R-01"], "session": "impl"},
            "S-02": {"title": "整える", "realizes": ["R-01"]},
        },
        "tests": {"T-01": {"title": "保存できる", "verifies": ["R-01"]}},
        "rollback": "戻す",
    }
    if execution:
        plan["execution"] = {"sessions": {"impl": {"model": "opus"}}}
    return write_scope(
        tmp_path / "scope",
        document(
            schema="specdock/v1", assurance={"level": level, "reason": "見本"}, requirements={"R-01": requirement}
        ),
        document(design={"D-01": {"title": "保存の部品", "satisfies": ["R-01"]}}),
        document(**plan),
    )


def test_the_repository_rule_joins_the_findings(tmp_path: Path) -> None:
    result = evaluate(_scope(tmp_path, "light", owner=False, execution=False), "issue", overlay=_overlay(tmp_path))
    assert result.ok, result.stderr
    assert result.findings["local-step-without-session"] == [
        {"id": "S-02", "message": "S-02 に session がありません", "hint": 'plan.cue の steps."S-02".session を書く'}
    ]
    # SpecDock's own rules still run beside it: S-01 names a session that execution does not define.
    assert [item["id"] for item in result.findings["execution-reference"]] == ["S-01"]


@pytest.mark.parametrize(
    ("level", "owner", "execution", "missing"),
    [
        ("light", False, False, None),
        ("standard", False, False, "execution"),
        ("standard", False, True, None),
        ("strict", False, True, 'requirements."R-01".owner'),
        ("strict", True, True, None),
        ("critical", True, False, "execution"),
    ],
)
def test_the_repository_constraints_follow_the_assurance_level(
    tmp_path: Path, level: str, owner: bool, execution: bool, missing: str | None
) -> None:
    result = evaluate(_scope(tmp_path, level, owner=owner, execution=execution), "issue", overlay=_overlay(tmp_path))
    if missing is None:
        assert result.ok, result.stderr
    else:
        assert not result.ok and f"{missing}: field is required but not present" in result.stderr, result.stderr


def test_without_the_repository_type_its_constraints_do_not_apply(tmp_path: Path) -> None:
    result = evaluate(_scope(tmp_path, "strict", owner=False, execution=False), "issue")
    assert result.ok, result.stderr
    assert "local-step-without-session" not in result.findings


def test_a_missing_level_is_reported_as_such_even_with_the_repository_conditions(tmp_path: Path) -> None:
    scope = _scope(tmp_path, "strict", owner=False, execution=False)
    requirement = (scope / "requirement.cue").read_text(encoding="utf-8").replace('"level": "strict", ', "")
    (scope / "requirement.cue").write_text(requirement, encoding="utf-8")
    result = evaluate(scope, "issue", overlay=_overlay(tmp_path))
    assert not result.ok
    assert "assurance.level: field is required but not present" in result.stderr and "cycle" not in result.stderr
