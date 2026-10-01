"""Read-only leaves honor explicit expectations using one direct selection."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from tests.cli_runtime.test_issue413_active import select_fixture
from tests.cli_runtime.test_issue413_dependency import dependency_workspace
from tests.cli_runtime.test_issue413_work_start import open_issue

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize("guard", ["current", "backend"])
def test_branch_show_checks_expectations_and_preserves_the_direct_record(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], guard: str
) -> None:
    root, _parent, _child = dependency_workspace(tmp_path)
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = record.read_bytes()
    option = ["--expect-current", "gh:example/repo#1"] if guard == "current" else ["--expect-backend", "local"]
    assert main(["--project", str(root), "branch", "show", "@current", *option, "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and record.read_bytes() == before
    assert (
        main([
            "--project",
            str(root),
            "branch",
            "show",
            "@current",
            "--expect-current",
            "gh:example/repo#3",
            "--expect-backend",
            "github",
            "--json",
        ])
        == 0
    )
    assert json.loads(capsys.readouterr().out)["effects"] == [] and record.read_bytes() == before


@pytest.mark.parametrize("guard", ["current", "backend"])
def test_scope_show_checks_resolved_scope_expectations_before_success(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], guard: str
) -> None:
    root, _parent, _child = dependency_workspace(tmp_path)
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = record.read_bytes()
    option = ["--expect-current", "gh:example/repo#1"] if guard == "current" else ["--expect-backend", "local"]
    assert main(["--project", str(root), "scope", "show", "@current", *option, "--json"]) == 3
    assert json.loads(capsys.readouterr().out)["effects"] == [] and record.read_bytes() == before
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "show",
            "@current",
            "--expect-current",
            "gh:example/repo#3",
            "--expect-backend",
            "github",
            "--json",
        ])
        == 0
    )
    assert json.loads(capsys.readouterr().out)["data"]["result"]["scope"]["id"] == "iss-00003"
    assert record.read_bytes() == before


@pytest.mark.parametrize("guard", ["current", "backend"])
def test_active_show_checks_expectations_without_claiming_a_single_scope_backend(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], guard: str
) -> None:
    root, _parent, _child = dependency_workspace(tmp_path)
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = record.read_bytes()
    option = ["--expect-current", "gh:example/repo#1"] if guard == "current" else ["--expect-backend", "github"]
    assert main(["--project", str(root), "active", "show", *option, "--json"]) == 3
    assert json.loads(capsys.readouterr().out)["effects"] == [] and record.read_bytes() == before
    assert main(["--project", str(root), "active", "show", "--expect-current", "gh:example/repo#3", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["selection"]["scope_id"] == "iss-00003" and record.read_bytes() == before


@pytest.mark.parametrize("leaf", ["list", "check"])
@pytest.mark.parametrize("guard", ["current", "backend"])
def test_dependency_queries_apply_expectations_before_any_github_get(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], leaf: str, guard: str
) -> None:
    root, _parent, _child = dependency_workspace(tmp_path)
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = record.read_bytes()
    gets: list[int] = []

    def get(_gateway, project, repository, number):
        gets.append(number)
        return open_issue(project, repository, number)

    monkeypatch.setattr("spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", get)
    option = ["--expect-current", "gh:example/repo#1"] if guard == "current" else ["--expect-backend", "local"]
    source = ["--source", "github"] if leaf == "check" else []
    assert main(["--project", str(root), "dependency", leaf, "@current", *source, *option, "--json"]) == 3
    assert json.loads(capsys.readouterr().out)["effects"] == [] and gets == [] and record.read_bytes() == before
    assert (
        main([
            "--project",
            str(root),
            "dependency",
            leaf,
            "@current",
            *source,
            "--expect-current",
            "gh:example/repo#3",
            "--expect-backend",
            "github",
            "--json",
        ])
        == 0
    )
    assert json.loads(capsys.readouterr().out)["data"]["result"]["scope_id"] == "iss-00003"
    assert record.read_bytes() == before
    assert bool(gets) is (leaf == "check")


@pytest.mark.parametrize("leaf", ["list", "show"])
@pytest.mark.parametrize("guard", ["current", "backend"])
def test_artifact_queries_check_owner_expectations_without_disclosing_or_changing_evidence(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], leaf: str, guard: str
) -> None:
    root, _parent, child = dependency_workspace(tmp_path)
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = record.read_bytes()
    artifacts = child.parent / "artifacts"
    artifacts.mkdir()
    evidence = artifacts / "20261001t000000z--private.bin"
    evidence.write_bytes(b"private evidence must remain opaque")
    operand = [evidence.name] if leaf == "show" else []
    option = ["--expect-current", "gh:example/repo#1"] if guard == "current" else ["--expect-backend", "local"]
    assert main(["--project", str(root), "artifact", leaf, *operand, "--scope", "@current", *option, "--json"]) == 3
    assert json.loads(capsys.readouterr().out)["effects"] == [] and record.read_bytes() == before
    assert (
        main([
            "--project",
            str(root),
            "artifact",
            leaf,
            *operand,
            "--scope",
            "@current",
            "--expect-current",
            "gh:example/repo#3",
            "--expect-backend",
            "github",
            "--json",
        ])
        == 0
    )
    output = capsys.readouterr().out
    assert "private evidence must remain opaque" not in output
    assert record.read_bytes() == before and evidence.read_bytes() == b"private evidence must remain opaque"


@pytest.mark.parametrize("guard", ["current", "backend"])
def test_scope_list_checks_current_guard_and_rejects_a_backend_without_one_target(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], guard: str
) -> None:
    root, _parent, _child = dependency_workspace(tmp_path)
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = record.read_bytes()
    option = ["--expect-current", "gh:example/repo#1"] if guard == "current" else ["--expect-backend", "github"]
    assert main(["--project", str(root), "scope", "list", *option, "--json"]) == 3
    assert json.loads(capsys.readouterr().out)["effects"] == [] and record.read_bytes() == before
    assert main(["--project", str(root), "scope", "list", "--expect-current", "gh:example/repo#3", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert {item["id"] for item in result["data"]["result"]["items"]} == {
        "init-00001",
        "epic-00002",
        "epic-00004",
        "iss-00003",
    }
    assert record.read_bytes() == before


@pytest.mark.parametrize("guard", ["current", "backend"])
def test_sync_checks_expectations_before_observing_remote_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], guard: str
) -> None:
    root, _parent, _child = dependency_workspace(tmp_path)
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = record.read_bytes()
    gets: list[int] = []

    def get(_gateway, project, repository, number):
        gets.append(number)
        return open_issue(project, repository, number)

    monkeypatch.setattr("spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", get)
    option = ["--expect-current", "gh:example/repo#1"] if guard == "current" else ["--expect-backend", "github"]
    assert main(["--project", str(root), "workspace", "sync", "--source", "github", *option, "--json"]) == 3
    assert json.loads(capsys.readouterr().out)["effects"] == [] and gets == [] and record.read_bytes() == before
    assert (
        main([
            "--project",
            str(root),
            "workspace",
            "sync",
            "--source",
            "github",
            "--expect-current",
            "gh:example/repo#3",
            "--json",
        ])
        == 0
    )
    assert json.loads(capsys.readouterr().out)["data"]["kind"] == "sync"
    assert set(gets) == {1, 2, 3, 4} and len(gets) == 4 and record.read_bytes() == before


@pytest.mark.parametrize("leaf", ["list", "show"])
def test_root_artifact_query_checks_current_but_has_no_scope_backend(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], leaf: str
) -> None:
    root, _parent, _child = dependency_workspace(tmp_path)
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = record.read_bytes()
    artifacts = root / "spec-dock/artifacts"
    artifacts.mkdir()
    evidence = artifacts / "20261001t010000z--opaque.bin"
    evidence.write_bytes(b"opaque root evidence")
    operand = [evidence.name] if leaf == "show" else []
    for option in (["--expect-current", "gh:example/repo#1"], ["--expect-backend", "github"]):
        assert main(["--project", str(root), "artifact", leaf, *operand, "--scope", "@root", *option, "--json"]) == 3
        assert json.loads(capsys.readouterr().out)["effects"] == []
    assert (
        main([
            "--project",
            str(root),
            "artifact",
            leaf,
            *operand,
            "--scope",
            "@root",
            "--expect-current",
            "gh:example/repo#3",
            "--json",
        ])
        == 0
    )
    output = capsys.readouterr().out
    assert "opaque root evidence" not in output
    assert record.read_bytes() == before and evidence.read_bytes() == b"opaque root evidence"
    assert not (root / ".git/spec-dock").exists()


@pytest.mark.parametrize("status", ["empty", "stale"])
def test_scope_query_current_guard_does_not_accept_empty_or_stale_selection(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], status: str
) -> None:
    root, _parent, _child = dependency_workspace(tmp_path)
    record = select_fixture(root, scope_id="iss-00003", number=999) if status == "stale" else None
    before = record.read_bytes() if record is not None else None
    assert (
        main(["--project", str(root), "scope", "show", "init-00001", "--expect-current", "gh:example/repo#1", "--json"])
        == 3
    )
    assert json.loads(capsys.readouterr().out)["effects"] == []
    assert record is None or record.read_bytes() == before
    assert main(["--project", str(root), "scope", "show", "init-00001", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["data"]["result"]["scope"]["id"] == "init-00001"
