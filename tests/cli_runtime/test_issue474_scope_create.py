"""iss-00474: canonical `scope create` and `scope import github` scaffold a CUE Scope with its assurance level."""

from __future__ import annotations

import json
from pathlib import Path
import shlex
import shutil
import subprocess
from typing import Any

import pytest

from tests.support.canonical_writes import WriteWorld
from tests.support.cue import cue_executable

ROOT = Path(__file__).resolve().parents[2]
SKELETON = ROOT / "src/spec_dock/assets/spec_dock/design-system/explanation-skeleton.html"
CUE_SET = [
    ".workbench",
    "artifacts",
    "design.cue",
    "discussions",
    "explanation.html",
    "plan.cue",
    "report.md",
    "requirement.cue",
]
REASON = "公開の CLI の契約を変えるため"
ASSURANCE = ("--assurance", "strict", "--assurance-reason", REASON)


def _world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> WriteWorld:
    world = WriteWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "plan")
    world.scope("epic", 2, "core", parent=1)
    return world


def _create(world: WriteWorld, kind: str, *extra: str, title: str = "新しい作業") -> tuple[int, dict[str, Any]]:
    parent = {"initiative": (), "epic": ("--parent", "init-00001"), "issue": ("--parent", "epic-00002")}[kind]
    return world.write("scope", "create", kind, "--backend", "github", *parent, "--title", title, *extra)


def _assurance_of(directory: Path) -> object:
    completed = subprocess.run(
        [cue_executable(), "export", "--out", "json", "-e", "assurance", "requirement.cue"],
        cwd=directory,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout)


@pytest.mark.parametrize(("kind", "prefix"), [("initiative", "init"), ("epic", "epic"), ("issue", "iss")])
def test_create_scaffolds_the_cue_set_with_the_given_assurance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], kind: str, prefix: str
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    code, payload = _create(world, kind, *ASSURANCE)
    assert code == 0, payload
    scope_id = f"{prefix}-00003"
    directory = world.catalog / "00000-00999" / scope_id
    assert sorted(path.name for path in directory.iterdir()) == CUE_SET
    assert _assurance_of(directory) == {"level": "strict", "reason": REASON}
    assert (directory / "explanation.html").read_bytes() == SKELETON.read_bytes()
    report = (directory / "report.md").read_text(encoding="utf-8")
    assert (
        f'ID: "{scope_id}"' in report and "タイトル" not in report and "](../../../docs/authoring/report.md)" in report
    )
    linked = world.main / "spec-dock/initiatives/00000-00999" / scope_id
    assert (linked / "../../../docs/authoring/report.md").resolve() == (
        world.main / "spec-dock/docs/authoring/report.md"
    ).resolve()
    assert (directory / ".workbench/README.md").is_file()
    assert "{{" not in (directory / "requirement.cue").read_text(encoding="utf-8")
    (changeset,) = world.changesets()
    assert changeset["paths"] == [f"00000-00999/{scope_id}"]


@pytest.mark.parametrize(
    "reason",
    [
        'He said "fine" \\ and left',
        "一行目\n二行目\tタブ",
        "\\(not.interpolated) and \\n stays",
        "制御\x01\x1b文字\x7f",
        "BOM\ufeffの途中",
        "印 {{ASSURANCE_LEVEL}} {{ASSURANCE_REASON}} YYYY-MM-DD <ISS_ID> ](../docs/authoring/x.md)",
    ],
)
def test_any_reason_reads_back_from_the_created_requirement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], reason: str
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    code, payload = _create(world, "issue", "--assurance", "light", "--assurance-reason", f"  {reason}  ")
    assert code == 0, payload
    assert _assurance_of(world.find("iss-00003")) == {"level": "light", "reason": reason}


@pytest.mark.parametrize(
    "assurance",
    [
        (),
        ("--assurance", "standard"),
        ("--assurance-reason", "理由"),
        ("--assurance", "standard", "--assurance-reason", ""),
        ("--assurance", "standard", "--assurance-reason", " \n\t"),
        ("--assurance", "standard", "--assurance-reason", "　"),
    ],
)
def test_a_missing_or_blank_assurance_stops_before_any_github_request(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], assurance: tuple[str, ...]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.edit(lambda fake: fake.add_issue(7, title="Existing"))
    before = len(world.fake().requests)
    for argv in (
        ("scope", "create", "issue", "--backend", "github", "--parent", "epic-00002", "--title", "X", "--yes"),
        ("scope", "create", "issue", "--backend", "github", "--parent", "epic-00002", "--title", "X", "--dry-run"),
        ("scope", "import", "github", "issue", "7", "--parent", "epic-00002", "--title", "X"),
        ("scope", "import", "github", "issue", "7", "--parent", "epic-00002", "--title", "X", "--dry-run"),
    ):
        code, payload = world.run(*argv, *assurance)
        assert (code, payload["status"], payload["error"]["code"]) == (2, "failed", "ASSURANCE_REQUIRED"), payload
        assert "--assurance" in payload["recovery"]["instructions"][0]
    assert len(world.fake().requests) == before
    assert world.changesets() == [] and not (world.catalog / "00000-00999/iss-00007").exists()


def test_an_unknown_level_is_a_usage_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    code, payload = _create(world, "issue", "--assurance", "medium", "--assurance-reason", "理由")
    assert (code, payload["error"]["code"]) == (2, "USAGE_ERROR")
    assert world.writes() == []


@pytest.mark.parametrize("kind", ["initiative", "epic", "issue"])
def test_the_created_scope_shows_its_assurance_and_only_the_skeleton_finding(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], kind: str
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    code, payload = _create(world, kind, "--assurance", "critical", "--assurance-reason", REASON)
    assert code == 0, payload
    scope_id = payload["data"]["result"]["scope"]["id"]
    code, shown = world.run("scope", "show", scope_id, "--offline")
    assert code == 0, shown
    assert shown["data"]["result"]["assurance"] == {
        "level": "critical",
        "reason": REASON,
        "source": "cue",
        "problem": None,
    }
    code, checked = world.run("scope", "check", scope_id, "--offline")
    result = checked["data"]["result"]
    assert result["checked"] is True and result["format"] == "cue"
    if kind == "epic":
        assert (code, [item["code"] for item in result["errors"]]) == (7, ["EXPLANATION_SKELETON"])
        assert result["warnings"] == []
    else:
        assert (code, result["errors"]) == (0, [])
        assert [item["code"] for item in result["warnings"]] == ["EXPLANATION_SKELETON"]


def test_import_scaffolds_the_cue_set_and_an_existing_directory_is_left_as_it_is(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.edit(lambda fake: fake.add_issue(7, title="既存の作業"))
    code, payload = world.run(
        "scope", "import", "github", "issue", "7", "--parent", "epic-00002", "--title", "既存の作業", *ASSURANCE
    )
    assert code == 0, payload
    directory = world.find("iss-00007")
    assert sorted(path.name for path in directory.iterdir()) == CUE_SET
    assert _assurance_of(directory) == {"level": "strict", "reason": REASON}
    assert payload["warnings"] == []
    before = {path: path.read_bytes() for path in directory.rglob("*") if path.is_file()}
    code, payload = world.run(
        "scope", "import", "github", "issue", "7", "--parent", "epic-00002", "--title", "既存の作業",
        "--assurance", "light", "--assurance-reason", "別の理由",
    )  # fmt: skip
    assert (code, payload["status"]) == (0, "unchanged"), payload
    assert {path: path.read_bytes() for path in directory.rglob("*") if path.is_file()} == before
    (warning,) = payload["warnings"]
    assert warning["code"] == "ASSURANCE_NOT_WRITTEN" and warning["details"]["scope_id"] == "iss-00007"
    assert "requirement.cue" in warning["details"]["next_step"]
    # A Markdown Scope that already exists is kept too.
    code, payload = world.run(
        "scope", "import", "github", "epic", "2", "--parent", "init-00001", "--title", "core", *ASSURANCE
    )
    assert code == 0, payload
    assert [item["code"] for item in payload["warnings"]] == ["ASSURANCE_NOT_WRITTEN"]
    assert not (world.find("epic-00002") / "requirement.cue").exists()


@pytest.mark.parametrize("breakage", ["directory", "file", "marker"])
def test_outdated_templates_stop_create_and_import_before_any_github_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], breakage: str
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.edit(lambda fake: fake.add_issue(7, title="Plain"))
    templates = world.main / "spec-dock/templates/cue/issue"
    if breakage == "directory":
        shutil.rmtree(world.main / "spec-dock/templates/cue")
    elif breakage == "file":
        (templates / "explanation.html").unlink()
    else:
        requirement = templates / "requirement.cue"
        requirement.write_text(requirement.read_text("utf-8").replace("{{ASSURANCE_REASON}}", "x"), "utf-8")
    for argv in (
        ("scope", "create", "issue", "--backend", "github", "--parent", "epic-00002", "--title", "X", "--yes"),
        ("scope", "import", "github", "issue", "7", "--parent", "epic-00002", "--title", "Plain"),
    ):
        code, payload = world.run(*argv, *ASSURANCE)
        assert (code, payload["error"]["code"]) == (3, "SCOPE_TEMPLATES_OUTDATED"), payload
        assert "spec-dock installation update" in payload["recovery"]["instructions"][0]
        assert payload["error"]["details"]["path"] == "spec-dock/templates/cue/issue"
    assert world.writes() == [] and world.changesets() == []
    assert world.fake().issue(7).labels == []


@pytest.mark.parametrize("reason", ["Don't break", "-urgent", "--yes"])
def test_the_recovery_import_carries_the_assurance_and_runs_as_shown(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], reason: str
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.edit(lambda fake: fake.inject(status=422, body={"message": "no"}, method="POST", endpoint="/sub_issues"))
    code, payload = _create(world, "issue", "--assurance", "standard", f"--assurance-reason={reason}")
    assert (code, payload["status"]) == (6, "partial"), payload
    (step,) = payload["recovery"]["instructions"]
    command = step[step.index("spec-dock scope import") : step.index(";")]
    argv = shlex.split(command)
    assert argv[:2] == ["spec-dock", "scope"] and "--assurance" in argv
    world.edit(lambda fake: fake.clear_faults())
    code, payload = world.run(*argv[1:])
    assert code == 0, payload
    assert _assurance_of(world.find("iss-00003")) == {"level": "standard", "reason": reason}


def test_help_names_the_assurance_arguments_and_codes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from spec_dock.cli import main

    for leaf in (["scope", "create", "issue"], ["scope", "import", "github", "issue"]):
        assert main(["help", *leaf]) == 0
        text = capsys.readouterr().out
        assert "--assurance" in text and "--assurance-reason" in text
        assert "ASSURANCE_REQUIRED" in text and "SCOPE_TEMPLATES_OUTDATED" in text
        assert "--assurance standard --assurance-reason" in text
