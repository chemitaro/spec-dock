"""The `cue` boundary: find it, check its version, call it with an argument list, read its errors (iss-00473)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.infra.cue_tool import CueError, CuePosition, CueToolError, locate_cue, parse_cue_errors
from tests.support.cue import cue_executable
from tests.support.cue_scopes import hide_cue, install_fake_cue

if TYPE_CHECKING:
    from pathlib import Path


def test_a_missing_cue_stops_with_the_install_step(monkeypatch: pytest.MonkeyPatch) -> None:
    hide_cue(monkeypatch)
    with pytest.raises(CueToolError) as raised:
        locate_cue(timeout=5)
    assert (raised.value.code, raised.value.exit_code) == ("CUE_NOT_FOUND", 3)
    assert "go install cuelang.org/go/cmd/cue@v0.17.1" in raised.value.next_step


@pytest.mark.parametrize(
    "version", ["cue version v0.17.0", "cue version v0.9.9", "cue version (devel)", "", "cue version 0.17.1"]
)
def test_an_old_or_unreadable_version_stops_naming_what_was_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, version: str
) -> None:
    install_fake_cue(tmp_path, monkeypatch, version=version)
    with pytest.raises(CueToolError) as raised:
        locate_cue(timeout=5)
    assert (raised.value.code, raised.value.exit_code) == ("CUE_VERSION_UNSUPPORTED", 3)
    assert "v0.17.1" in raised.value.next_step


@pytest.mark.parametrize("version", ["cue version v0.17.1", "cue version v0.18.0-alpha.1", "cue version v1.0.0"])
def test_the_minimum_version_or_a_later_one_is_used(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, version: str
) -> None:
    fake = install_fake_cue(tmp_path, monkeypatch, version=version + "\n\nCUE language version v0.17.1")
    tool = locate_cue(timeout=5)
    assert tool.executable == str(fake.directory / "cue")
    assert tool.version == version.split()[-1]
    assert fake.calls() == [["version"]]


def test_a_version_check_that_hangs_times_out(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    install_fake_cue(tmp_path, monkeypatch, sleep=5)
    with pytest.raises(CueToolError) as raised:
        locate_cue(timeout=0.5)
    assert (raised.value.code, raised.value.exit_code) == ("CUE_TIMEOUT", 5)


def test_a_failing_version_check_is_a_failed_tool(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    install_fake_cue(tmp_path, monkeypatch, version_code=2)
    with pytest.raises(CueToolError) as raised:
        locate_cue(timeout=5)
    assert (raised.value.code, raised.value.exit_code) == ("CUE_FAILED", 5)


def test_export_passes_one_argument_list_in_order(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake = install_fake_cue(tmp_path, monkeypatch, export_stdout='{"a": 1}', export_stderr="w", export_code=1)
    tool = locate_cue(timeout=5)
    odd = tmp_path / "a b;$(touch x)" / "plan.cue"
    run = tool.export(
        [tmp_path / "base.cue", odd], cwd=tmp_path, timeout=5, tags={"kind": "issue"}, expression="schema"
    )
    assert (run.returncode, run.stdout, run.stderr) == (1, '{"a": 1}', "w")
    assert fake.calls()[-1] == [
        "export",
        "--out",
        "json",
        "-t",
        "kind=issue",
        "-e",
        "schema",
        str(tmp_path / "base.cue"),
        str(odd),
    ]
    assert not (tmp_path / "x").exists()


def test_an_export_that_hangs_times_out(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    install_fake_cue(tmp_path, monkeypatch)
    tool = locate_cue(timeout=5)
    install_fake_cue(tmp_path, monkeypatch, sleep=5)
    with pytest.raises(CueToolError) as raised:
        tool.export([tmp_path / "a.cue"], cwd=tmp_path, timeout=0.5)
    assert raised.value.code == "CUE_TIMEOUT"


def test_real_cue_errors_split_into_paths_messages_and_resolved_positions(tmp_path: Path) -> None:
    import subprocess

    scope = tmp_path / "scope"
    scope.mkdir()
    (scope / "requirement.cue").write_text(
        'package spec\nlevel: "x" & =~"^(a|b)$"\nsteps: {"S-01": {status: 3 & string}}\n', encoding="utf-8"
    )
    completed = subprocess.run(
        [cue_executable(), "export", "--out", "json", str(scope / "requirement.cue")],
        cwd=scope,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 1
    errors = parse_cue_errors(completed.stderr, cwd=scope)
    by_path = {error.path: error for error in errors}
    assert set(by_path) == {"level", 'steps."S-01".status'}
    assert "out of bound" in by_path["level"].message
    assert by_path["level"].positions[-1] == CuePosition(scope / "requirement.cue", 2, 8)
    assert all(not error.message.endswith(":") for error in errors)


def test_an_error_without_a_field_path_keeps_its_message(tmp_path: Path) -> None:
    text = "expected '}', found 'EOF':\n    ./requirement.cue:5:8\n"
    assert parse_cue_errors(text, cwd=tmp_path) == (
        CueError(None, "expected '}', found 'EOF'", (CuePosition(tmp_path / "requirement.cue", 5, 8),)),
    )


def test_relative_positions_resolve_against_the_working_directory(tmp_path: Path) -> None:
    (tmp_path / "a" / "b").mkdir(parents=True)
    text = 'x."R-01".title: conflicting values 3 and string:\n    ../../types/base.cue:49:9\n    ./plan.cue:2:3\n'
    [error] = parse_cue_errors(text, cwd=tmp_path / "a" / "b")
    assert error.path == 'x."R-01".title'
    assert [position.file for position in error.positions] == [tmp_path / "types/base.cue", tmp_path / "a/b/plan.cue"]


def test_a_header_line_without_positions_and_an_unknown_line_stay_errors(tmp_path: Path) -> None:
    text = (
        'steps."S-01".status: 2 errors in empty disjunction:\n'
        'steps."S-01".status: conflicting values "todo" and "nope":\n'
        "    ./plan.cue:2:58\n"
        "some trailing note\n"
    )
    errors = parse_cue_errors(text, cwd=tmp_path)
    assert [(error.path, error.message) for error in errors] == [
        ('steps."S-01".status', "2 errors in empty disjunction"),
        ('steps."S-01".status', 'conflicting values "todo" and "nope"'),
        (None, "some trailing note"),
    ]
    assert errors[0].positions == () and len(errors[1].positions) == 1


def test_empty_error_text_has_no_errors(tmp_path: Path) -> None:
    assert parse_cue_errors("", cwd=tmp_path) == ()
