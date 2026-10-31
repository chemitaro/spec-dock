"""`spec-dock scope check <ID>` on a canonical catalog (iss-00473; K3 of epic-00425)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.cli import main
from tests.support.canonical_repo import bare_remote, clone, isolate_user_state
from tests.support.canonical_scopes import CanonicalWorld
from tests.support.cue import cue_executable
from tests.support.cue_scopes import hide_cue, install_fake_cue, place_sample, skeleton_explanation

if TYPE_CHECKING:
    from pathlib import Path

SHOWN = "spec-dock/initiatives/00000-00999/iss-00003"


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> CanonicalWorld:
    cue_executable()
    world = CanonicalWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "Plan")
    world.scope("epic", 2, "Core", parent=1)
    world.scope("issue", 3, "Leaf", parent=2, documents=())
    world.scope("issue", 4, "Markdown leaf", parent=2)
    place_sample(world.catalog / world.relative("issue", 3), "issue-strict-complete")
    return world


def files_of(root: Path) -> dict[str, bytes]:
    """Every regular file under root (Git metadata aside), by its relative path."""
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink() and ".git" not in path.relative_to(root).parts
    }


def scope_dir(world: CanonicalWorld, number: int = 3) -> Path:
    return world.catalog / world.relative("issue", number)


def text_run(world: CanonicalWorld, *argv: str) -> tuple[int, str, str]:
    world.capsys.readouterr()
    code = main(["--project", str(world.main), *argv])
    captured = world.capsys.readouterr()
    return code, captured.out, captured.err


def test_a_clean_cue_scope_passes_without_writing(world: CanonicalWorld) -> None:
    before = (files_of(world.catalog.resolve()), files_of(world.main))
    code, payload = world.run("scope", "check", "iss-3")
    assert code == 0, payload
    assert (payload["command"], payload["status"], payload["error"]) == ("scope check", "succeeded", None)
    assert payload["data"]["kind"] == "scope-check"
    result = payload["data"]["result"]
    assert (result["scope_id"], result["kind"], result["path"], result["format"]) == (
        "iss-00003",
        "issue",
        SHOWN,
        "cue",
    )
    assert (result["checked"], result["valid"], result["errors"], result["warnings"]) == (True, True, [], [])
    assert result["schema"] == "specdock/v1" and result["cue"] == {"version": "v0.17.1"}
    assert result["assurance"] == {
        "level": "strict",
        "reason": "公開の CLI の契約を変える",
        "source": "cue",
        "problem": None,
    }
    assert result["findings"] and not any(result["findings"].values())
    assert result["snapshot"]["repository"]
    assert (files_of(world.catalog.resolve()), files_of(world.main)) == before


def test_shape_errors_and_findings_fail_with_exit_7_and_name_file_field_and_fix(world: CanonicalWorld) -> None:
    plan = scope_dir(world) / "plan.cue"
    plan.write_text(plan.read_text(encoding="utf-8").replace('status: "doing"', 'status: "nope"'), encoding="utf-8")
    code, payload = world.run("scope", "check", "iss-00003")
    assert (code, payload["status"], payload["error"]["code"]) == (7, "failed", "SCOPE_CHECK_FAILED")
    errors = payload["data"]["result"]["errors"]
    assert {item["code"] for item in errors} == {"CUE_INVALID"}
    assert {item["details"]["file"] for item in errors} == {f"{SHOWN}/plan.cue"}
    assert {item["details"]["field"] for item in errors} == {'steps."S-02".status'}
    assert all(item["details"]["line"] == 5 and item["details"]["hint"] for item in errors)
    assert payload["data"]["result"]["valid"] is False and "nope" in payload["data"]["result"]["cue_output"]
    assert "spec-dock scope check iss-00003" in payload["recovery"]["instructions"][0]
    plan.write_text(plan.read_text(encoding="utf-8").replace('status: "nope"', 'status: "doing"'), encoding="utf-8")
    design = scope_dir(world) / "design.cue"
    design.write_text(design.read_text(encoding="utf-8").replace('satisfies: ["F-01"]', 'satisfies: ["R-09"]'), "utf-8")
    code, payload = world.run("scope", "check", "iss-00003")
    assert code == 7
    found = {
        (item["code"], item["details"]["rule"], item["details"]["id"]) for item in payload["data"]["result"]["errors"]
    }
    assert ("SPEC_FINDINGS", "unknown-reference", "D-02") in found
    assert all(item["details"]["file"] and item["details"]["hint"] for item in payload["data"]["result"]["errors"])


def test_the_text_output_lists_each_error_with_its_fix(world: CanonicalWorld) -> None:
    design = scope_dir(world) / "design.cue"
    design.write_text(design.read_text(encoding="utf-8").replace('satisfies: ["F-01"]', 'satisfies: ["R-09"]'), "utf-8")
    code, out, err = text_run(world, "scope", "check", "iss-3")
    assert code == 7
    assert "scope_id=iss-00003 format=cue checked=true valid=false" in out
    assert f'error [SPEC_FINDINGS] file="{SHOWN}/design.cue"' in out
    assert "  hint: " in out
    assert "error [SCOPE_CHECK_FAILED]" in err


def test_warnings_alone_pass_and_are_shown(world: CanonicalWorld) -> None:
    (scope_dir(world) / "explanation.html").write_text(skeleton_explanation(), encoding="utf-8")
    code, payload = world.run("scope", "check", "iss-3")
    assert code == 0
    assert [item["code"] for item in payload["data"]["result"]["warnings"]] == ["EXPLANATION_SKELETON"]
    assert "EXPLANATION_SKELETON" in {item["code"] for item in payload["warnings"]}
    code, out, _err = text_run(world, "scope", "check", "iss-3")
    assert code == 0 and "warning [EXPLANATION_SKELETON]" in out


def test_it_works_without_reaching_github(world: CanonicalWorld) -> None:
    code, _ = world.run("scope", "check", "iss-3")
    assert code == 0
    world.age_probe(4000)
    world.edit(lambda fake: fake.inject(status=503, times=50))
    code, payload = world.run("scope", "check", "iss-3")
    assert code == 0, payload
    assert "GITHUB_SNAPSHOT_STALE" in {item["code"] for item in payload["warnings"]}
    code, payload = world.run("scope", "check", "iss-3", "--offline")
    assert code == 0, payload


def test_a_markdown_scope_succeeds_unchecked_without_cue(
    world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    hide_cue(monkeypatch)
    code, payload = world.run("scope", "check", "iss-4")
    assert code == 0, payload
    result = payload["data"]["result"]
    assert (result["format"], result["checked"], result["valid"], result["errors"]) == ("markdown", False, True, [])
    assert result["assurance"]["source"] == "unset" and result["cue"] is None


def test_both_requirement_files_are_a_format_conflict(world: CanonicalWorld) -> None:
    (scope_dir(world) / "requirement.md").write_text("# r\n", encoding="utf-8")
    code, payload = world.run("scope", "check", "iss-3")
    assert code == 7
    assert [item["code"] for item in payload["data"]["result"]["errors"]] == ["SCOPE_FORMAT_CONFLICT"]


@pytest.mark.parametrize(
    ("options", "code", "exit_code"),
    [
        ({"version": "cue version v0.16.0"}, "CUE_VERSION_UNSUPPORTED", 3),
        ({"version": "cue version (devel)"}, "CUE_VERSION_UNSUPPORTED", 3),
        ({"export_stdout": "not json"}, "CUE_FAILED", 5),
    ],
)
def test_an_unusable_cue_stops_with_its_code_and_next_step(
    world: CanonicalWorld,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    options: dict[str, Any],
    code: str,
    exit_code: int,
) -> None:
    before = files_of(world.catalog.resolve())
    install_fake_cue(tmp_path, monkeypatch, **options)
    result_code, payload = world.run("scope", "check", "iss-3")
    assert (result_code, payload["error"]["code"]) == (exit_code, code)
    assert payload["recovery"]["instructions"]
    assert files_of(world.catalog.resolve()) == before


def test_a_missing_cue_stops_with_the_install_step(world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch) -> None:
    hide_cue(monkeypatch)
    code, payload = world.run("scope", "check", "iss-3")
    assert (code, payload["error"]["code"]) == (3, "CUE_NOT_FOUND")
    assert "go install cuelang.org/go/cmd/cue@v0.17.1" in payload["recovery"]["instructions"][0]


def test_a_hanging_cue_times_out(world: CanonicalWorld, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    install_fake_cue(tmp_path, monkeypatch)
    import os

    script = tmp_path / "fake-cue-bin" / "cue"
    script.write_text(
        script.read_text(encoding="utf-8").replace(
            "time.sleep(0.0)", "time.sleep(0 if sys.argv[1:2] == ['version'] else 5)"
        ),
        encoding="utf-8",
    )
    assert os.access(script, os.X_OK)
    code, payload = world.run("scope", "check", "iss-3", "--timeout", "1")
    assert (code, payload["error"]["code"]) == (5, "CUE_TIMEOUT")


def test_cue_is_called_with_the_k1_argument_list(
    world: CanonicalWorld, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (world.main / "spec-dock/cue").mkdir()
    (world.main / "spec-dock/cue/team.cue").write_text("package spec\n", encoding="utf-8")
    fake = install_fake_cue(tmp_path, monkeypatch, export_stdout='"specdock/v1"')
    world.run("scope", "check", "iss-3")
    calls = fake.calls()
    assert calls[0] == ["version"]
    assert calls[1][:5] == ["export", "--out", "json", "-e", "schema"]
    evaluation = next(call for call in calls if "-t" in call)
    assert evaluation[:5] == ["export", "--out", "json", "-t", "kind=issue"]
    files = [name.rsplit("/", 2)[-2:] for name in evaluation[5:]]
    assert files == [
        ["v1", "base.cue"],
        ["v1", "design_type.cue"],
        ["v1", "plan_type.cue"],
        ["v1", "requirement_type.cue"],
        ["v1", "rules.cue"],
        ["cue", "team.cue"],
        ["iss-00003", "requirement.cue"],
        ["iss-00003", "design.cue"],
        ["iss-00003", "plan.cue"],
    ]


def test_an_unknown_type_version_stops_and_names_the_shipped_ones(world: CanonicalWorld) -> None:
    requirement = scope_dir(world) / "requirement.cue"
    requirement.write_text(requirement.read_text(encoding="utf-8").replace("specdock/v1", "specdock/v9"), "utf-8")
    code, payload = world.run("scope", "check", "iss-3")
    assert (code, payload["error"]["code"]) == (3, "CUE_SCHEMA_UNSUPPORTED")
    assert payload["error"]["details"]["shipped"] == ["specdock/v1"]


def test_a_scope_without_a_directory_is_not_found(world: CanonicalWorld) -> None:
    world.scope("issue", 5, parent=2, directory=False)
    code, payload = world.run("scope", "check", "iss-5")
    assert (code, payload["error"]["code"]) == (4, "LOCAL_TARGET_NOT_FOUND")


def test_schema_three_is_not_migrated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    isolate_user_state(monkeypatch, tmp_path)
    legacy = {"schema_version": 3, "writer_protocol": "specdock.worktree-writer/v1"}
    checkout = clone(bare_remote(tmp_path / "v3.git", declaration=legacy), tmp_path / "v3")
    before = files_of(checkout)
    capsys.readouterr()
    code = main(["--project", str(checkout), "scope", "check", "iss-1", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert (code, payload["error"]["code"]) == (3, "CANONICAL_NOT_MIGRATED")
    assert files_of(checkout) == before


def test_help_and_completion_name_the_read_only_leaf(capsys: pytest.CaptureFixture[str]) -> None:
    capsys.readouterr()
    assert main(["help", "scope", "check"]) == 0
    text = capsys.readouterr().out
    assert "None; this command only reads." in text and "scope-check" in text and "exit 7" in text
    assert main(["scope", "check", "--help"]) == 0
    assert "usage: spec-dock scope check" in capsys.readouterr().out
    assert main(["completion", "zsh"]) == 0
    assert "check" in capsys.readouterr().out
