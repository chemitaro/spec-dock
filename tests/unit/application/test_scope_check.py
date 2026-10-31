"""One Scope's check (iss-00473): format, contract K1 evaluation, findings, assurance and explanation shape."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.runtime.application.canonical_errors import CanonicalCommandError
from spec_dock.runtime.application.scope_check import check_scope_documents, read_assurance, scope_format
from tests.support.cue import cue_executable
from tests.support.cue_scopes import (
    hide_cue,
    install_fake_cue,
    place_sample,
    sample_expectation,
    sample_names,
    skeleton_explanation,
)

if TYPE_CHECKING:
    from pathlib import Path

SHOWN = "spec-dock/initiatives/00000-00999/iss-00003"
pytestmark = pytest.mark.usefixtures("real_cue")


@pytest.fixture
def real_cue() -> None:
    cue_executable()  # the real cue must be on PATH; a test that hides it does so explicitly


def check(scope: Path, kind: str = "issue", *, repository: Path | None = None):  # type: ignore[no-untyped-def]
    return check_scope_documents(
        scope, kind=kind, shown=SHOWN, repository_root=repository or scope.parent / "repo", timeout=60
    )


def codes(items: tuple[object, ...]) -> list[str]:
    return [item.code for item in items]  # type: ignore[attr-defined]


def test_the_format_is_decided_by_the_requirement_file(tmp_path: Path) -> None:
    assert scope_format(tmp_path) == "markdown"
    (tmp_path / "requirement.md").write_text("# r\n", encoding="utf-8")
    assert scope_format(tmp_path) == "markdown"
    (tmp_path / "requirement.cue").write_text("package spec\n", encoding="utf-8")
    assert scope_format(tmp_path) == "conflict"
    (tmp_path / "requirement.md").unlink()
    assert scope_format(tmp_path) == "cue"


def test_a_markdown_scope_is_not_checked_and_needs_no_cue(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    hide_cue(monkeypatch)
    scope = tmp_path / "scope"
    scope.mkdir()
    (scope / "requirement.md").write_text("# r\n", encoding="utf-8")
    report = check(scope)
    assert (report.format, report.checked, report.errors, report.warnings) == ("markdown", False, (), ())
    assert report.assurance.source == "unset"


def test_a_complete_scope_has_no_errors(tmp_path: Path) -> None:
    report = check(place_sample(tmp_path / "scope", "issue-strict-complete"))
    assert (report.format, report.checked, report.errors, report.warnings) == ("cue", True, (), ())
    assert report.schema == "specdock/v1"
    assert (report.assurance.level, report.assurance.source) == ("strict", "cue")
    assert report.findings is not None and not any(report.findings.values())
    assert report.cue_version == "v0.17.1"


@pytest.mark.parametrize("sample", sample_names())
def test_every_v1_sample_checks_as_recorded(tmp_path: Path, sample: str) -> None:
    expected: Any = sample_expectation(sample)
    report = check(place_sample(tmp_path / "scope", sample), expected["kind"])
    if "export" in expected:
        export = expected["export"]
        assert report.findings == export["findings"]
        found = [(item.details["rule"], item.details["id"]) for item in report.errors]
        wanted = [(rule, item["id"]) for rule, items in sorted(export["findings"].items()) for item in items]
        assert found == wanted
        assert set(codes(report.errors)) <= {"SPEC_FINDINGS"}
    else:
        fields = {item.details["field"] for item in report.errors if item.code == "CUE_INVALID"}
        assert set(expected["error_paths"]) <= fields
        assert not any(field and field.startswith("_") for field in fields)
        assert report.findings is None and report.cue_output


def test_a_shape_error_names_the_file_line_field_and_a_fix(tmp_path: Path) -> None:
    report = check(place_sample(tmp_path / "scope", "issue-strict-missing-impact"))
    [first, *_] = report.errors
    assert first.code == "CUE_INVALID"
    details = first.details
    assert details["field"] == 'failures."F-01".impact'
    assert details["file"] == "<spec_dock>/cue/v1/requirement_type.cue"
    assert isinstance(details["line"], int) and isinstance(details["column"], int)
    assert details["hint"] and details["cue_message"] == "field is required but not present"
    assert details["positions"][0]["file"] == details["file"]


def test_an_error_in_a_scope_file_points_at_that_file(tmp_path: Path) -> None:
    scope = place_sample(tmp_path / "scope", "issue-strict-complete")
    plan = scope / "plan.cue"
    plan.write_text(plan.read_text(encoding="utf-8").replace('status: "doing"', 'status: "nope"'), encoding="utf-8")
    report = check(scope)
    assert codes(report.errors) == ["CUE_INVALID", "CUE_INVALID"]
    fields = {item.details["field"] for item in report.errors}
    assert fields == {'steps."S-02".status'}
    assert {item.details["file"] for item in report.errors} == {f"{SHOWN}/plan.cue"}
    assert all(item.details["line"] == 5 for item in report.errors)
    assert "nope" in str(report.cue_output)


def test_findings_name_the_rule_the_number_the_file_and_the_fix(tmp_path: Path) -> None:
    report = check(place_sample(tmp_path / "scope", "issue-standard-gaps"))
    assert set(codes(report.errors)) == {"SPEC_FINDINGS"}
    by_rule = {item.details["rule"]: item for item in report.errors}
    unknown = by_rule["unknown-reference"]
    assert unknown.details["file"] == f"{SHOWN}/design.cue" and unknown.details["hint"]
    assert unknown.message
    assert by_rule["requirement-without-test"].details["file"] == f"{SHOWN}/requirement.cue"


def test_raising_the_level_requires_more_and_writing_it_passes(tmp_path: Path) -> None:
    scope = place_sample(tmp_path / "scope", "issue-strict-complete")
    requirement = scope / "requirement.cue"
    text = requirement.read_text(encoding="utf-8")
    without = text.replace('\timpact:   "利用者のファイルを上書きしない"\n', "")
    requirement.write_text(without.replace('"strict"', '"standard"'), encoding="utf-8")
    assert check(scope).errors == ()
    requirement.write_text(without, encoding="utf-8")
    assert {item.details["field"] for item in check(scope).errors} == {'failures."F-01".impact'}
    requirement.write_text(text, encoding="utf-8")
    assert check(scope).errors == ()


def test_a_missing_schema_is_a_schema_error_before_evaluation(tmp_path: Path) -> None:
    scope = place_sample(tmp_path / "scope", "issue-strict-complete")
    requirement = scope / "requirement.cue"
    requirement.write_text(requirement.read_text(encoding="utf-8").replace('schema: "specdock/v1"\n', ""), "utf-8")
    report = check(scope)
    assert codes(report.errors) == ["CUE_INVALID"]
    assert (report.errors[0].details["field"], report.errors[0].details["file"]) == (
        "schema",
        f"{SHOWN}/requirement.cue",
    )
    assert report.checked is False


@pytest.mark.parametrize("value", ['"other/v1"', "1", '"specdock/v01"'])
def test_a_malformed_schema_is_a_schema_error(tmp_path: Path, value: str) -> None:
    scope = place_sample(tmp_path / "scope", "issue-strict-complete")
    requirement = scope / "requirement.cue"
    requirement.write_text(requirement.read_text(encoding="utf-8").replace('"specdock/v1"', value), "utf-8")
    report = check(scope)
    assert codes(report.errors) == ["CUE_INVALID"] and report.errors[0].details["field"] == "schema"


def test_a_version_this_package_lacks_stops_and_names_the_shipped_ones(tmp_path: Path) -> None:
    scope = place_sample(tmp_path / "scope", "issue-strict-complete")
    requirement = scope / "requirement.cue"
    requirement.write_text(requirement.read_text(encoding="utf-8").replace("specdock/v1", "specdock/v9"), "utf-8")
    with pytest.raises(CanonicalCommandError) as raised:
        check(scope)
    assert (raised.value.code, raised.value.exit_code) == ("CUE_SCHEMA_UNSUPPORTED", 3)
    assert raised.value.details["shipped"] == ["specdock/v1"]
    assert "specdock/v1" in raised.value.recovery[0]


def test_an_assurance_written_outside_the_requirement_is_an_error(tmp_path: Path) -> None:
    scope = place_sample(tmp_path / "scope", "issue-strict-complete")
    requirement, design = scope / "requirement.cue", scope / "design.cue"
    text = requirement.read_text(encoding="utf-8")
    block = re.search(r"assurance: \{.*?\n\}\n", text, re.S)
    assert block is not None
    requirement.write_text(text.replace(block.group(0), ""), encoding="utf-8")
    design.write_text(design.read_text(encoding="utf-8") + "\n" + block.group(0), encoding="utf-8")
    report = check(scope)
    assert codes(report.errors) == ["ASSURANCE_UNREADABLE"]
    assert report.errors[0].details["file"] == f"{SHOWN}/requirement.cue"
    assert report.assurance.source == "unreadable"


def test_a_missing_level_is_reported_once_by_the_type(tmp_path: Path) -> None:
    scope = place_sample(tmp_path / "scope", "issue-strict-complete")
    requirement = scope / "requirement.cue"
    requirement.write_text(requirement.read_text(encoding="utf-8").replace('\tlevel:  "strict"\n', ""), "utf-8")
    report = check(scope)
    assert "ASSURANCE_UNREADABLE" not in codes(report.errors)
    assert "assurance.level" in {item.details["field"] for item in report.errors}


def test_a_repository_type_adds_its_constraint_and_rule(tmp_path: Path) -> None:
    repository = tmp_path / "repo"
    (repository / "spec-dock/cue").mkdir(parents=True)
    (repository / "spec-dock/cue/team.cue").write_text(
        "package spec\n\n"
        "if _rank >= 2 {\n\texecution!: _\n}\n\n"
        'findings: "team-owner": [for k, s in steps if s.owner == _|_ {id: k, message: "owner がない", hint: "plan.cue に owner を書く"}]\n',
        encoding="utf-8",
    )
    scope = place_sample(tmp_path / "scope", "issue-strict-complete")
    report = check(scope, repository=repository)
    assert [(item.code, item.details["rule"], item.details["id"]) for item in report.errors] == [
        ("SPEC_FINDINGS", "team-owner", key) for key in ("S-01", "S-02", "S-03")
    ]
    assert report.errors[0].details["file"] == f"{SHOWN}/plan.cue"
    plan = scope / "plan.cue"
    plan.write_text(plan.read_text(encoding="utf-8").split("execution:")[0], encoding="utf-8")
    report = check(scope, repository=repository)
    assert {item.details["field"] for item in report.errors if item.code == "CUE_INVALID"} == {"execution"}


def test_an_error_in_the_repository_type_points_at_its_file(tmp_path: Path) -> None:
    repository = tmp_path / "repo"
    (repository / "spec-dock/cue").mkdir(parents=True)
    (repository / "spec-dock/cue/team.cue").write_text("package spec\n\npurpose: 3\n", encoding="utf-8")
    report = check(place_sample(tmp_path / "scope", "issue-strict-complete"), repository=repository)
    assert "spec-dock/cue/team.cue" in {
        position["file"] for item in report.errors for position in item.details["positions"]
    }


def test_a_missing_plan_is_a_document_error_and_the_rest_is_still_checked(tmp_path: Path) -> None:
    scope = place_sample(tmp_path / "scope", "issue-strict-complete")
    (scope / "plan.cue").unlink()
    report = check(scope)
    assert "SCOPE_DOCUMENT_MISSING" in codes(report.errors)
    assert report.errors[0].details["file"] == f"{SHOWN}/plan.cue"
    assert report.checked is True


def test_a_conflicting_scope_is_one_error_without_cue(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    scope = place_sample(tmp_path / "scope", "issue-strict-complete")
    (scope / "requirement.md").write_text("# r\n", encoding="utf-8")
    hide_cue(monkeypatch)
    report = check(scope)
    assert (report.format, codes(report.errors)) == ("conflict", ["SCOPE_FORMAT_CONFLICT"])
    assert report.assurance.source == "unreadable"


@pytest.mark.parametrize(
    ("kind", "sample", "severity"),
    [
        ("issue", "issue-strict-complete", "warning"),
        ("initiative", "initiative-critical-complete", "warning"),
        ("epic", "epic-standard-uncovered", "error"),
    ],
)
def test_a_missing_or_skeleton_explanation_weighs_by_kind(
    tmp_path: Path, kind: str, sample: str, severity: str
) -> None:
    scope = place_sample(tmp_path / "scope", sample, explanation=skeleton_explanation())
    report = check(scope, kind)
    found = codes(report.errors if severity == "error" else report.warnings)
    assert "EXPLANATION_SKELETON" in found
    (scope / "explanation.html").unlink()
    report = check(scope, kind)
    found = codes(report.errors if severity == "error" else report.warnings)
    assert "EXPLANATION_MISSING" in found
    assert report.warnings[0].details["file"] == f"{SHOWN}/explanation.html" if severity == "warning" else True


def test_a_broken_explanation_is_an_error_for_every_kind(tmp_path: Path) -> None:
    broken = skeleton_explanation().replace('id="ds-source"', 'id="other"')
    report = check(place_sample(tmp_path / "scope", "issue-strict-complete", explanation=broken))
    assert codes(report.errors) == ["EXPLANATION_INVALID"]
    assert codes(report.warnings) == ["EXPLANATION_SKELETON"]
    assert report.errors[0].details["problem"]


def test_a_missing_cue_stops_a_cue_scope(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    scope = place_sample(tmp_path / "scope", "issue-strict-complete")
    hide_cue(monkeypatch)
    with pytest.raises(CanonicalCommandError) as raised:
        check(scope)
    assert (raised.value.code, raised.value.exit_code) == ("CUE_NOT_FOUND", 3)


def test_output_that_is_not_json_stops_as_a_failed_tool(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    scope = place_sample(tmp_path / "scope", "issue-strict-complete")
    install_fake_cue(tmp_path, monkeypatch, export_stdout="not json")
    with pytest.raises(CanonicalCommandError) as raised:
        check(scope)
    assert (raised.value.code, raised.value.exit_code) == ("CUE_FAILED", 5)


class TestReadAssurance:
    def test_no_directory_or_a_markdown_scope_is_unset(self, tmp_path: Path) -> None:
        assert read_assurance(None, timeout=30).payload() == {
            "level": None,
            "reason": None,
            "source": "unset",
            "problem": None,
        }
        assert read_assurance(tmp_path, timeout=30).source == "unset"

    def test_the_requirement_values_are_read(self, tmp_path: Path) -> None:
        scope = place_sample(tmp_path / "scope", "issue-strict-complete")
        assert read_assurance(scope, timeout=30).payload() == {
            "level": "strict",
            "reason": "公開の CLI の契約を変える",
            "source": "cue",
            "problem": None,
        }

    @pytest.mark.parametrize(
        ("old", "new", "code"),
        [
            ('level:  "strict"', 'level:  "high"', "ASSURANCE_UNREADABLE"),
            ('reason: "公開の CLI の契約を変える"', 'reason: "\\u3000 "', "ASSURANCE_UNREADABLE"),
            ('\treason: "公開の CLI の契約を変える"\n', "", "ASSURANCE_UNREADABLE"),
            ("assurance: {", "other: {", "ASSURANCE_UNREADABLE"),
            ("assurance: {", "assurance: {{", "CUE_INVALID"),
        ],
        ids=["bad-level", "blank-reason", "no-reason", "no-assurance", "syntax"],
    )
    def test_each_unreadable_case_has_a_problem(self, tmp_path: Path, old: str, new: str, code: str) -> None:
        scope = place_sample(tmp_path / "scope", "issue-strict-complete")
        requirement = scope / "requirement.cue"
        text = requirement.read_text(encoding="utf-8")
        assert old in text
        requirement.write_text(text.replace(old, new, 1), encoding="utf-8")
        reading = read_assurance(scope, timeout=30).payload()
        assert (reading["level"], reading["reason"], reading["source"]) == (None, None, "unreadable")
        assert reading["problem"]["code"] == code and reading["problem"]["message"]  # type: ignore[index]

    def test_a_conflict_and_a_missing_cue_are_unreadable(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        scope = place_sample(tmp_path / "scope", "issue-strict-complete")
        hide_cue(monkeypatch)
        assert read_assurance(scope, timeout=30).problem.code == "CUE_NOT_FOUND"  # type: ignore[union-attr]
        (scope / "requirement.md").write_text("# r\n", encoding="utf-8")
        assert read_assurance(scope, timeout=30).problem.code == "SCOPE_FORMAT_CONFLICT"  # type: ignore[union-attr]


def test_the_report_keeps_the_whole_evaluation_and_the_k1_file_order(tmp_path: Path) -> None:
    from spec_dock.runtime.application.scope_check import k1_files
    from spec_dock.runtime.infra.cue_schemas import schema_directory

    scope = place_sample(tmp_path / "scope", "issue-strict-complete")
    report = check(scope)
    assert report.evaluation is not None and report.evaluation["steps"]["S-01"]["status"] == "done"
    repository = tmp_path / "repo"
    (repository / "spec-dock/cue").mkdir(parents=True)
    (repository / "spec-dock/cue/b.cue").write_text("package spec\n", encoding="utf-8")
    (repository / "spec-dock/cue/a.cue").write_text("package spec\n", encoding="utf-8")
    types = schema_directory("specdock/v1")
    assert types is not None
    files = k1_files(types, repository, scope)
    assert [path.name for path in files] == [
        "base.cue",
        "design_type.cue",
        "plan_type.cue",
        "requirement_type.cue",
        "rules.cue",
        "a.cue",
        "b.cue",
        "requirement.cue",
        "design.cue",
        "plan.cue",
    ]
    assert all(path.is_absolute() for path in files)


def test_a_tool_failure_while_reading_the_level_stops_instead_of_blaming_the_document(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.application import scope_check
    from spec_dock.runtime.application.scope_check import AssuranceReading
    from spec_dock.runtime.presentation.envelope import Diagnostic

    scope = place_sample(tmp_path / "scope", "issue-strict-complete")
    timed_out = AssuranceReading(None, None, "unreadable", Diagnostic("CUE_TIMEOUT", "cue did not finish", {}))
    monkeypatch.setattr(scope_check, "read_assurance", lambda *args, **kwargs: timed_out)
    with pytest.raises(CanonicalCommandError) as raised:
        check(scope)
    assert (raised.value.code, raised.value.exit_code) == ("CUE_TIMEOUT", 5)
