"""Finish confirms completion before clearing its captured direct record."""

from __future__ import annotations

from dataclasses import replace
import json
import os
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from tests.cli_runtime.test_issue413_active import select_fixture
from tests.cli_runtime.test_issue413_work_start import committed_workspace, open_issue

if TYPE_CHECKING:
    from pathlib import Path


def test_finish_already_completed_uses_live_observation_and_clears_capture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    before = metadata.read_bytes()
    calls = []

    def observed(_, repo_root, repository, number):
        calls.append((repository, number))
        return replace(
            open_issue(repo_root, repository, number), state="completed", raw_state="closed", state_reason="completed"
        )

    monkeypatch.setattr("spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", observed)
    assert main(["--project", str(root), "work", "finish", "@current", "--yes", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"] == {
        "kind": "work-finish",
        "scope_id": "init-00001",
        "completed": True,
        "branch_before": "main",
        "branch_after": "main",
        "selection_token": None,
    }
    assert calls == [("example/repo", 1)]
    assert not record.exists()
    assert metadata.read_bytes() == before
    assert result["effects"] == [
        {"kind": "github.issue.close", "status": "unchanged", "target": "gh:example/repo#1"},
        {"kind": "selection.clear", "status": "succeeded", "target": record.name[7:-5]},
    ]
    assert not (root / ".git/spec-dock").exists()


def github_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, states: dict[str, str]) -> Path:
    bin_dir = tmp_path / "gh-bin"
    bin_dir.mkdir()
    state_file = tmp_path / "remote-states.json"
    state_file.write_text(json.dumps(states))
    log = tmp_path / "requests.jsonl"
    executable = bin_dir / "gh"
    executable.write_text(
        f"#!{sys.executable}\n"
        "import json,sys\nfrom pathlib import Path\n"
        f"states_path=Path({str(state_file)!r})\nlog=Path({str(log)!r})\n"
        "args=sys.argv[1:]\nmethod=args[args.index('--method')+1]\n"
        "endpoint=args[args.index('--method')+2]\nnumber=int(endpoint.rsplit('/',1)[1])\n"
        "assert endpoint==f'repos/example/repo/issues/{number}'\n"
        "assert method in ('GET','PATCH')\nbody=json.load(sys.stdin) if method=='PATCH' else None\n"
        "with log.open('a') as stream: stream.write(json.dumps({'method':method,'number':number,'body':body})+'\\n')\n"
        "states=json.loads(states_path.read_bytes())\n"
        "if method=='PATCH':\n"
        " assert body=={'state':'closed','state_reason':'completed'}\n"
        " states[str(number)]='completed'\n states_path.write_text(json.dumps(states))\n"
        "state=states[str(number)]\n"
        "payload={'number':number,'title':'Fixture','repository_url':'https://api.github.com/repos/example/repo',"
        "'html_url':f'https://github.com/example/repo/issues/{number}',"
        "'state':'unrecognized' if state=='unknown' else 'open' if state=='open' else 'closed',"
        "'state_reason':None if state=='open' else 'not_planned' if state=='not-planned' else 'completed',"
        "'updated_at':'2026-09-30T00:00:00Z'}\n"
        "print('HTTP/2.0 200 OK\\n\\n'+json.dumps(payload))\n"
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])
    return log


@pytest.mark.parametrize("request_count,exit_code", [(2, 5), (4, 6)])
def test_finish_native_git_failure_retains_original_diagnostic_and_confirmed_effects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    request_count: int,
    exit_code: int,
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    before = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    real_git = shutil.which("git")
    assert real_git is not None
    executable = tmp_path / "gh-bin/git"
    original_error = "fatal: fixture Git observation refused\nsecond original line\n"
    executable.write_text(
        f"#!{sys.executable}\nimport os,sys\nfrom pathlib import Path\n"
        f"log=Path({str(log)!r})\n"
        f"if '--show-toplevel' in sys.argv and log.exists() and len(log.read_text().splitlines())>={request_count}:\n"
        f" sys.stderr.write({original_error!r}); sys.exit(73)\n"
        f"os.execv({real_git!r},['git',*sys.argv[1:]])\n"
    )
    executable.chmod(0o755)
    assert main(["--project", str(root), "work", "finish", "@current", "--yes", "--json"]) == exit_code
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["error"]["code"] == "GIT_FAILED"
    assert result["error"]["details"]["git"]["stderr"] == original_error
    assert result["error"]["details"]["git"]["returncode"] == 73
    assert result["data"]["completed"] is (request_count == 4) and output.err == ""
    if request_count == 2:
        assert result["status"] == "failed" and result["effects"] == []
        expected_methods = ["GET", "GET"]
    else:
        assert result["status"] == "partial"
        assert result["effects"] == [
            {"kind": "github.issue.close", "status": "succeeded", "target": "gh:example/repo#1"},
            {"kind": "selection.clear", "status": "not_attempted", "target": record.name[7:-5]},
        ]
        expected_methods = ["GET", "GET", "PATCH", "GET"]
    assert [json.loads(line)["method"] for line in log.read_text().splitlines()] == expected_methods
    assert record.read_bytes() == before


def test_finish_closes_github_issue_once_before_releasing_capture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    assert main(["--project", str(root), "work", "finish", "@current", "--yes", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["completed"] is True
    assert result["data"]["selection_token"] is None
    assert not record.exists()
    requests = [json.loads(line) for line in log.read_text().splitlines()]
    assert [request["method"] for request in requests] == ["GET", "GET", "PATCH", "GET"]
    assert all(request["number"] == 1 for request in requests)
    assert result["effects"][0] == {"kind": "github.issue.close", "status": "succeeded", "target": "gh:example/repo#1"}


def test_finish_dry_run_needs_no_approval_and_preserves_remote_and_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    before = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    assert main(["--project", str(root), "work", "finish", "@current", "--dry-run", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "planned"
    assert result["data"]["completed"] is False
    assert record.read_bytes() == before
    assert [json.loads(line)["method"] for line in log.read_text().splitlines()] == ["GET"]
    assert result["effects"] == [
        {"kind": "github.issue.close", "status": "planned", "target": "gh:example/repo#1"},
        {"kind": "selection.clear", "status": "planned", "target": record.name[7:-5]},
    ]


def test_finish_completed_parent_still_requires_all_descendants_completed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from tests.cli_runtime.test_issue413_contract import add_scope

    root = committed_workspace(tmp_path / "consumer")
    add_scope(root, "epic-00002", "epic", "init-00001", root / "spec-dock/initiatives/init-00001-fixture")
    record = select_fixture(root)
    before = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "completed", "2": "open"})
    assert main(["--project", str(root), "work", "finish", "@current", "--yes", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert "DESCENDANT_NOT_COMPLETED" in result["error"]["message"]
    assert record.read_bytes() == before
    requests = [json.loads(line) for line in log.read_text().splitlines()]
    assert [(request["method"], request["number"]) for request in requests] == [("GET", 1), ("GET", 2)]


def test_finish_explicit_child_preserves_directly_selected_ancestor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest
    from tests.cli_runtime.test_work_commands_vnext import three_kind_workspace

    root = three_kind_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    before = tree_digest(root)
    exact_record = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "open", "2": "open", "3": "open"})
    assert main(["--project", str(root), "work", "finish", "iss-00003", "--yes", "--json"]) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["data"]["scope_id"] == "iss-00003" and result["data"]["completed"] is True
    assert result["data"]["branch_after"] == "main" and not output.err
    assert result["effects"] == [{"kind": "github.issue.close", "status": "succeeded", "target": "gh:example/repo#3"}]
    assert record.read_bytes() == exact_record and tree_digest(root) == before
    requests = [json.loads(line) for line in log.read_text().splitlines()]
    assert [(request["method"], request["number"]) for request in requests] == [
        ("GET", 3),
        ("GET", 3),
        ("PATCH", 3),
        ("GET", 3),
    ]
    assert json.loads((tmp_path / "remote-states.json").read_bytes()) == {"1": "open", "2": "open", "3": "completed"}


def test_existing_local_parent_finish_requires_live_completed_github_descendant(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest
    from tests.cli_runtime.test_work_commands_vnext import three_kind_workspace

    root = three_kind_workspace(tmp_path / "consumer")
    metadata = root / "spec-dock/initiatives/init-00001-fixture/epics/epic-00002-fixture/.meta.json"
    existing = json.loads(metadata.read_bytes())
    existing.update(
        backend="local",
        github=None,
        lifecycle={"state": "open", "revision": 3, "updated_at": "2020-01-01T00:00:00Z", "optional": True},
        optional={"keep": [1, 2]},
    )
    metadata.write_text(json.dumps(existing))
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = tree_digest(root)
    exact_record = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"3": "open"})
    assert main(["--project", str(root), "work", "finish", "@epic", "--yes", "--json"]) == 3
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert "DESCENDANT_NOT_COMPLETED" in result["error"]["message"]
    assert result["effects"] == [] and not output.err
    assert record.read_bytes() == exact_record and tree_digest(root) == before
    assert [json.loads(line) for line in log.read_text().splitlines()] == [{"method": "GET", "number": 3, "body": None}]
    other_metadata = {path: path.read_bytes() for path in (root / "spec-dock").rglob(".meta.json") if path != metadata}
    (tmp_path / "remote-states.json").write_text(json.dumps({"3": "completed"}))
    assert main(["--project", str(root), "work", "finish", "@epic", "--yes", "--json"]) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["data"]["scope_id"] == "epic-00002" and result["data"]["completed"] is True
    assert result["data"]["selection_token"] is None and result["data"]["branch_after"] == "main"
    assert not record.exists() and not list(record.parent.glob("target-*.json")) and not output.err
    after = json.loads(metadata.read_bytes())
    assert after["revision"] == existing["revision"] + 1
    assert after["lifecycle"]["state"] == "completed" and after["lifecycle"]["revision"] == 4
    assert after["lifecycle"]["optional"] is True
    assert {key: value for key, value in after.items() if key not in ("revision", "lifecycle")} == {
        key: value for key, value in existing.items() if key not in ("revision", "lifecycle")
    }
    assert all(path.read_bytes() == payload for path, payload in other_metadata.items())
    assert [json.loads(line) for line in log.read_text().splitlines()] == [
        {"method": "GET", "number": 3, "body": None},
        {"method": "GET", "number": 3, "body": None},
    ]
    assert [effect["kind"] for effect in result["effects"]] == ["scope.lifecycle", "selection.clear"]
    assert all(effect["status"] == "succeeded" for effect in result["effects"])
    assert not list(root.rglob(".specdock-json-transactions")) and not (root / ".git/spec-dock").exists()


def test_finish_parent_releases_captured_descendant_without_selecting_parent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from tests.cli_runtime.test_issue413_contract import add_scope

    root = committed_workspace(tmp_path / "consumer")
    epic = add_scope(root, "epic-00002", "epic", "init-00001", root / "spec-dock/initiatives/init-00001-fixture")
    add_scope(root, "iss-00003", "issue", "epic-00002", epic)
    record = select_fixture(root, scope_id="iss-00003", number=3)
    log = github_fixture(tmp_path, monkeypatch, {"1": "completed", "2": "open", "3": "completed"})
    assert main(["--project", str(root), "work", "finish", "@epic", "--yes", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["scope_id"] == "epic-00002"
    assert result["data"]["selection_token"] is None
    assert not record.exists()
    requests = [json.loads(line) for line in log.read_text().splitlines()]
    assert [(request["method"], request["number"]) for request in requests] == [
        ("GET", 2),
        ("GET", 3),
        ("GET", 2),
        ("PATCH", 2),
        ("GET", 2),
    ]


def test_finish_offline_refuses_before_any_remote_call_or_local_change(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    before = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    assert main(["--project", str(root), "work", "finish", "@current", "--yes", "--offline", "--json"]) == 3
    assert json.loads(capsys.readouterr().out)["effects"] == []
    assert not log.exists()
    assert record.read_bytes() == before


def test_finish_expected_direct_target_guard_precedes_remote_observation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from tests.cli_runtime.test_issue413_contract import add_scope

    root = committed_workspace(tmp_path / "consumer")
    add_scope(root, "epic-00002", "epic", "init-00001", root / "spec-dock/initiatives/init-00001-fixture")
    record = select_fixture(root)
    before = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "open", "2": "completed"})
    assert (
        main([
            "--project",
            str(root),
            "work",
            "finish",
            "init-00001",
            "--expect-current",
            "epic-00002",
            "--yes",
            "--json",
        ])
        == 3
    )
    assert json.loads(capsys.readouterr().out)["effects"] == []
    assert not log.exists()
    assert record.read_bytes() == before


def test_finish_unknown_target_state_never_patches_or_releases_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    before = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "unknown"})
    assert main(["--project", str(root), "work", "finish", "@current", "--yes", "--json"]) == 3
    assert json.loads(capsys.readouterr().out)["effects"] == []
    assert record.read_bytes() == before
    assert [json.loads(line)["method"] for line in log.read_text().splitlines()] == ["GET"]


def test_finish_rechecks_metadata_after_gateway_get_before_patch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    before = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    executable = tmp_path / "gh-bin/gh"
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    code = executable.read_text()
    # Change the original target during the gateway's own final GET, rather than the first app GET.
    code = code.replace(
        "states=json.loads(states_path.read_bytes())",
        (
            f"metadata=Path({str(metadata)!r})\n"
            "if method=='GET' and len(log.read_text().splitlines())==2:\n"
            " changed=json.loads(metadata.read_bytes())\n changed['title']='concurrent edit'\n"
            " metadata.write_text(json.dumps(changed))\n"
            "states=json.loads(states_path.read_bytes())"
        ),
    )
    executable.write_text(code)
    assert main(["--project", str(root), "work", "finish", "@current", "--yes", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert record.read_bytes() == before
    assert [json.loads(line)["method"] for line in log.read_text().splitlines()] == ["GET", "GET"]


def test_finish_concurrent_remote_completion_is_reported_unchanged_without_patch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    executable = tmp_path / "gh-bin/gh"
    code = executable.read_text().replace(
        "states=json.loads(states_path.read_bytes())",
        "states=json.loads(states_path.read_bytes())\n"
        "if method=='GET' and len(log.read_text().splitlines())==2: states[str(number)]='completed'",
    )
    executable.write_text(code)
    assert main(["--project", str(root), "work", "finish", "@current", "--yes", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["effects"][0]["status"] == "unchanged"
    assert not record.exists()
    assert [json.loads(line)["method"] for line in log.read_text().splitlines()] == ["GET", "GET"]


def test_finish_uncertain_close_retains_capture_and_reports_unknown_effect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    before = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    executable = tmp_path / "gh-bin/gh"
    code = executable.read_text().replace(
        "states[str(number)]='completed'", "print('HTTP/2.0 503 Unavailable\\n\\n{}'); sys.exit(1)"
    )
    executable.write_text(code)
    assert main(["--project", str(root), "work", "finish", "@current", "--yes", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "partial"
    assert result["data"]["completed"] is False
    assert result["data"]["selection_token"] == record.name[7:-5]
    assert result["effects"] == [
        {"kind": "github.issue.close", "status": "unknown", "target": "gh:example/repo#1"},
        {"kind": "selection.clear", "status": "not_attempted", "target": record.name[7:-5]},
    ]
    assert record.read_bytes() == before
    assert [json.loads(line)["method"] for line in log.read_text().splitlines()] == ["GET", "GET", "PATCH", "GET"]


def test_finish_confirmed_close_with_clear_sync_failure_reports_completed_partial(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    github_fixture(tmp_path, monkeypatch, {"1": "open"})
    real_fsync = os.fsync
    directory = record.parent

    def syncing(fd):
        if os.fstat(fd).st_ino == directory.stat().st_ino and not record.exists():
            raise OSError("fixture clear sync refused")
        real_fsync(fd)

    monkeypatch.setattr(os, "fsync", syncing)
    assert main(["--project", str(root), "work", "finish", "@current", "--yes", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["completed"] is True
    assert result["effects"] == [
        {"kind": "github.issue.close", "status": "succeeded", "target": "gh:example/repo#1"},
        {"kind": "selection.clear", "status": "unknown", "target": record.name[7:-5]},
    ]
    assert not record.exists()


def test_finish_confirmed_patch_rejection_reports_clear_not_attempted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    before = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    executable = tmp_path / "gh-bin/gh"
    executable.write_text(
        executable.read_text().replace(
            "states[str(number)]='completed'", "print('HTTP/2.0 422 Rejected\\n\\n{}'); sys.exit(1)"
        )
    )
    assert main(["--project", str(root), "work", "finish", "@current", "--yes", "--json"]) == 5
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "failed"
    assert result["data"]["completed"] is False
    assert result["effects"] == [
        {"kind": "github.issue.close", "status": "failed", "target": "gh:example/repo#1"},
        {"kind": "selection.clear", "status": "not_attempted", "target": record.name[7:-5]},
    ]
    assert record.read_bytes() == before
    assert [json.loads(line)["method"] for line in log.read_text().splitlines()] == ["GET", "GET", "PATCH"]


def test_finish_verified_close_keeps_capture_when_metadata_changes_before_clear(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    before = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    executable = tmp_path / "gh-bin/gh"
    executable.write_text(
        executable.read_text().replace(
            "states=json.loads(states_path.read_bytes())",
            f"metadata=Path({str(metadata)!r})\n"
            "if method=='GET' and len(log.read_text().splitlines())==4:\n"
            " changed=json.loads(metadata.read_bytes())\n changed['title']='concurrent preserve'\n"
            " metadata.write_text(json.dumps(changed))\n"
            "states=json.loads(states_path.read_bytes())",
        )
    )
    assert main(["--project", str(root), "work", "finish", "@current", "--yes", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["completed"] is True
    assert result["effects"] == [
        {"kind": "github.issue.close", "status": "succeeded", "target": "gh:example/repo#1"},
        {"kind": "selection.clear", "status": "not_attempted", "target": record.name[7:-5]},
    ]
    assert record.read_bytes() == before
    assert json.loads(metadata.read_bytes())["title"] == "concurrent preserve"
    assert [json.loads(line)["method"] for line in log.read_text().splitlines()] == ["GET", "GET", "PATCH", "GET"]


def test_finish_rejects_journal_recovery_input_before_project_access(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert (
        main(["--project", str(tmp_path / "missing"), "work", "finish", "iss-00413", "--resume", "0" * 32, "--json"])
        == 2
    )
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED"
    assert result["effects"] == []
    assert list(tmp_path.iterdir()) == []


def test_finish_keeps_new_selection_published_during_remote_wait(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from pathlib import Path

    root = committed_workspace(tmp_path / "consumer")
    old = select_fixture(root)
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    marker = tmp_path / "child-result.json"
    executable = tmp_path / "gh-bin/gh"
    code = executable.read_text().replace("import json,sys", "import json,sys,subprocess,os")
    # A native child replaces A by a new Start of A while Finish is waiting on its first GET.
    child = (
        "import sys; from spec_dock.cli import main; "
        f"assert main(['--project',{str(root)!r},'active','clear','--all','--json'])==0; "
        f"sys.exit(main(['--project',{str(root)!r},'work','start','init-00001','--branch','main','--json']))"
    )
    code = code.replace(
        "args=sys.argv[1:]", (f"marker=Path({str(marker)!r})\nchild_code={child!r}\nargs=sys.argv[1:]")
    ).replace(
        "states=json.loads(states_path.read_bytes())",
        (
            "if len(log.read_text().splitlines())==1 and not marker.exists():\n"
            " marker.write_text('running')\n"
            f" env=dict(os.environ,PYTHONPATH={str(Path(__file__).resolve().parents[2] / 'src')!r})\n"
            " child=subprocess.run([sys.executable,'-c',child_code],env=env,capture_output=True,text=True,timeout=10)\n"
            " assert child.returncode==0,child.stderr+child.stdout\n marker.write_text(child.stdout)\n"
            "states=json.loads(states_path.read_bytes())"
        ),
    )
    executable.write_text(code)
    assert main(["--project", str(root), "work", "finish", "@current", "--yes", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    child_results = [json.loads(line) for line in marker.read_text().splitlines()]
    new_token = child_results[-1]["data"]["selection_token"]
    assert not old.exists()
    assert new_token != old.name[7:-5]
    new_path = old.parent / f"target-{new_token}.json"
    assert new_path.exists()
    assert result["data"]["selection_token"] == new_token
    assert result["effects"][-1] == {"kind": "selection.clear", "status": "unchanged", "target": old.name[7:-5]}
    assert [
        request["number"] for request in map(json.loads, log.read_text().splitlines()) if request["method"] == "PATCH"
    ] == [1]


def test_finish_gateway_unknown_fresh_state_stops_before_patch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    before = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    executable = tmp_path / "gh-bin/gh"
    code = executable.read_text().replace(
        "states=json.loads(states_path.read_bytes())",
        "states=json.loads(states_path.read_bytes())\n"
        "if method=='GET' and len(log.read_text().splitlines())==2: states[str(number)]='unknown'",
    )
    executable.write_text(code)
    assert main(["--project", str(root), "work", "finish", "@current", "--yes", "--json"]) == 5
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "GITHUB_STATE_UNKNOWN"
    assert record.read_bytes() == before
    assert [json.loads(line)["method"] for line in log.read_text().splitlines()] == ["GET", "GET"]


@pytest.mark.skipif(os.name != "posix", reason="native POSIX flock boundary")
def test_finish_native_process_does_not_participate_in_start_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import fcntl
    from pathlib import Path

    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    github_fixture(tmp_path, monkeypatch, {"1": "open"})
    descriptor = os.open(root / ".git", os.O_RDONLY)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                "from spec_dock.cli import main; import sys; sys.exit(main(sys.argv[1:]))",
                "--project",
                str(root),
                "work",
                "finish",
                "@current",
                "--yes",
                "--json",
            ],
            env=dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[2] / "src")),
            capture_output=True,
            timeout=5,
        )
    finally:
        os.close(descriptor)
    assert completed.returncode == 0, completed.stderr + completed.stdout
    assert json.loads(completed.stdout)["data"]["completed"] is True
    assert not record.exists()


def test_finish_retry_observes_completion_and_avoids_duplicate_patch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    real_unlink = os.unlink

    def unlinking(path, *args, **kwargs):
        if path == record.name:
            raise PermissionError("fixture clear refused")
        return real_unlink(path, *args, **kwargs)

    with monkeypatch.context() as clearing:
        clearing.setattr(os, "unlink", unlinking)
        assert main(["--project", str(root), "work", "finish", "@current", "--yes", "--json"]) == 6
        result = json.loads(capsys.readouterr().out)
        assert result["data"]["completed"] is True
        assert record.exists()
        assert result["effects"][-1] == {"kind": "selection.clear", "status": "failed", "target": record.name[7:-5]}
    assert main(["--project", str(root), "work", "finish", "@current", "--yes", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["effects"][0]["status"] == "unchanged"
    assert not record.exists()
    assert [request["method"] for request in map(json.loads, log.read_text().splitlines())].count("PATCH") == 1


def test_finish_unavailable_observation_reports_gateway_failure_without_effects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    before = record.read_bytes()
    github_fixture(tmp_path, monkeypatch, {"1": "open"})
    executable = tmp_path / "gh-bin/gh"
    executable.write_text(
        executable.read_text().replace(
            "print('HTTP/2.0 200 OK\\n\\n'+json.dumps(payload))",
            "print('HTTP/2.0 503 Unavailable\\n\\n{}'); sys.exit(1)",
        )
    )
    assert main(["--project", str(root), "work", "finish", "@current", "--yes", "--json"]) == 5
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "GITHUB_REMOTE_UNAVAILABLE"
    assert result["effects"] == []
    assert record.read_bytes() == before


def test_finish_preserves_existing_local_backend_and_optional_metadata_without_control(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from spec_dock.runtime.application.project_context import resolve_context
    from spec_dock.runtime.domain.work_target import WorkTarget
    from spec_dock.runtime.infra.work_target_store import WorkTargetStore

    root = committed_workspace(tmp_path / "consumer")
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    existing = json.loads(metadata.read_bytes())
    existing.update(
        backend="local",
        github=None,
        revision=5,
        lifecycle={"state": "open", "revision": 3, "updated_at": "2020-01-01T00:00:00Z", "optional": {"keep": True}},
        optional={"keep": [1, 2]},
    )
    metadata.write_text(json.dumps(existing))
    context = resolve_context(str(root), root)
    with WorkTargetStore(root) as store:
        handle = store.publish(
            WorkTarget(
                "specdock.work-target/v1",
                "init-00001",
                None,
                "main",
                "2026-09-30T00:00:00Z",
                context.clone_identity,
                context.worktree_identity,
            )
        )
        record = store.path / handle.basename
    assert main(["--project", str(root), "work", "finish", "@current", "--yes", "--offline", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["completed"] is True
    assert not record.exists()
    after = json.loads(metadata.read_bytes())
    assert after["revision"] == 6
    assert after["lifecycle"]["state"] == "completed"
    assert after["lifecycle"]["revision"] == 4
    assert after["lifecycle"]["updated_at"] != existing["lifecycle"]["updated_at"]
    assert after["lifecycle"]["optional"] == existing["lifecycle"]["optional"]
    assert {k: v for k, v in after.items() if k not in ("revision", "lifecycle")} == {
        k: v for k, v in existing.items() if k not in ("revision", "lifecycle")
    }
    assert result["effects"][0] == {"kind": "scope.lifecycle", "status": "succeeded", "target": "init-00001"}
    assert not list(root.rglob(".specdock-json-transactions"))
    assert not (root / ".git/spec-dock").exists()


def test_local_finish_redirected_private_parent_never_creates_external_stage(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    original = json.loads(metadata.read_bytes())
    original.update(
        backend="local", github=None, lifecycle={"state": "open", "revision": 0, "updated_at": "2020-01-01T00:00:00Z"}
    )
    metadata.write_text(json.dumps(original))
    before = metadata.read_bytes()
    outside = tmp_path / "outside"
    outside.mkdir()
    (root / "spec-dock/.agent").symlink_to(outside, target_is_directory=True)
    assert main(["--project", str(root), "work", "finish", "init-00001", "--yes", "--offline", "--json"]) == 5
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert metadata.read_bytes() == before
    assert list(outside.iterdir()) == []


def test_local_finish_stage_collision_preserves_foreign_stage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    original = json.loads(metadata.read_bytes())
    original.update(
        backend="local", github=None, lifecycle={"state": "open", "revision": 0, "updated_at": "2020-01-01T00:00:00Z"}
    )
    metadata.write_text(json.dumps(original))
    before = metadata.read_bytes()
    real_open = os.open
    collisions = []

    def opening(path, *args, **kwargs):
        if isinstance(path, str) and path.startswith(".stage-"):
            descriptor = real_open(path, *args, **kwargs)
            os.write(descriptor, b"foreign preserve")
            os.close(descriptor)
            collisions.append(root / "spec-dock/.agent/staging" / path)
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(os, "open", opening)
    assert main(["--project", str(root), "work", "finish", "init-00001", "--yes", "--json"]) == 5
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert metadata.read_bytes() == before
    assert len(collisions) == 1
    assert collisions[0].read_bytes() == b"foreign preserve"


def test_local_finish_replace_cleanup_failure_preserves_confirmed_completion_effect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    original = json.loads(metadata.read_bytes())
    original.update(
        backend="local", github=None, lifecycle={"state": "open", "revision": 0, "updated_at": "2020-01-01T00:00:00Z"}
    )
    metadata.write_text(json.dumps(original))
    real_close = os.close
    triggered = False

    def closing(descriptor):
        nonlocal triggered
        stage = root / "spec-dock/.agent/staging"
        is_stage = stage.exists() and os.fstat(descriptor).st_ino == stage.stat().st_ino
        real_close(descriptor)
        if is_stage and not triggered and json.loads(metadata.read_bytes())["lifecycle"]["state"] == "completed":
            triggered = True
            raise OSError("fixture stage cleanup refused")

    monkeypatch.setattr(os, "close", closing)
    assert main(["--project", str(root), "work", "finish", "init-00001", "--yes", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert triggered
    assert result["data"]["completed"] is True
    assert result["effects"] == [{"kind": "scope.lifecycle", "status": "succeeded", "target": "init-00001"}]
    assert json.loads(metadata.read_bytes())["lifecycle"]["state"] == "completed"


def test_local_finish_replacement_parent_redirect_is_unknown_and_preserves_new_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    original = json.loads(metadata.read_bytes())
    original.update(
        backend="local", github=None, lifecycle={"state": "open", "revision": 0, "updated_at": "2020-01-01T00:00:00Z"}
    )
    metadata.write_text(json.dumps(original))
    parent_identity = metadata.parent.stat().st_ino
    real_fsync = os.fsync
    triggered = False

    def syncing(descriptor):
        nonlocal triggered
        real_fsync(descriptor)
        if os.fstat(descriptor).st_ino == parent_identity and not triggered:
            triggered = True
            metadata.parent.rename(tmp_path / "moved-scope")
            metadata.parent.mkdir()
            metadata.write_text(json.dumps(dict(original, title="external preserve")))

    monkeypatch.setattr(os, "fsync", syncing)
    assert main(["--project", str(root), "work", "finish", "init-00001", "--yes", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert triggered
    assert result["data"]["completed"] is False
    assert result["effects"] == [{"kind": "scope.lifecycle", "status": "unknown", "target": "init-00001"}]
    assert json.loads(metadata.read_bytes())["lifecycle"]["state"] == "open"
    assert json.loads(metadata.read_bytes())["title"] == "external preserve"


def test_local_finish_requires_ignored_stage_before_creating_private_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    original = json.loads(metadata.read_bytes())
    original.update(
        backend="local", github=None, lifecycle={"state": "open", "revision": 0, "updated_at": "2020-01-01T00:00:00Z"}
    )
    metadata.write_text(json.dumps(original))
    before = metadata.read_bytes()
    (root / "spec-dock/.gitignore").write_text("")
    assert main(["--project", str(root), "work", "finish", "init-00001", "--yes", "--json"]) == 3
    assert json.loads(capsys.readouterr().out)["effects"] == []
    assert metadata.read_bytes() == before
    assert not (root / "spec-dock/.agent").exists()


def test_local_finish_preserves_metadata_permissions_during_atomic_replace(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    original = json.loads(metadata.read_bytes())
    original.update(
        backend="local", github=None, lifecycle={"state": "open", "revision": 0, "updated_at": "2020-01-01T00:00:00Z"}
    )
    metadata.write_text(json.dumps(original))
    metadata.chmod(0o660)
    previous_umask = os.umask(0o022)
    try:
        assert main(["--project", str(root), "work", "finish", "init-00001", "--yes", "--json"]) == 0
        assert json.loads(capsys.readouterr().out)["data"]["completed"] is True
    finally:
        os.umask(previous_umask)
    assert metadata.stat().st_mode & 0o777 == 0o660


def test_local_finish_inflight_metadata_edit_is_preserved_without_replace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    original = json.loads(metadata.read_bytes())
    original.update(
        backend="local", github=None, lifecycle={"state": "open", "revision": 0, "updated_at": "2020-01-01T00:00:00Z"}
    )
    metadata.write_text(json.dumps(original))
    real_fsync = os.fsync
    changed = False

    def syncing(descriptor):
        nonlocal changed
        real_fsync(descriptor)
        if not changed and os.fstat(descriptor).st_ino != metadata.parent.stat().st_ino:
            changed = True
            metadata.write_text(json.dumps(dict(original, title="concurrent preserve")))

    monkeypatch.setattr(os, "fsync", syncing)
    assert main(["--project", str(root), "work", "finish", "init-00001", "--yes", "--json"]) == 3
    assert json.loads(capsys.readouterr().out)["effects"] == []
    assert changed
    assert json.loads(metadata.read_bytes())["title"] == "concurrent preserve"
    assert json.loads(metadata.read_bytes())["lifecycle"]["state"] == "open"
    assert list((root / "spec-dock/.agent/staging").iterdir()) == []


def test_finish_resolves_dynamic_target_and_handle_from_one_observation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    old = select_fixture(root)
    github_fixture(tmp_path, monkeypatch, {"1": "completed"})
    real_close = os.close
    replaced = False
    selection_closes = 0
    new = None

    def closing(descriptor):
        nonlocal replaced, new, selection_closes
        is_selection = os.fstat(descriptor).st_ino == old.parent.stat().st_ino
        real_close(descriptor)
        if is_selection:
            selection_closes += 1
        if selection_closes == 2 and not replaced:
            replaced = True
            old.unlink()
            new = select_fixture(root)

    monkeypatch.setattr(os, "close", closing)
    assert main(["--project", str(root), "work", "finish", "@current", "--yes", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert replaced and new is not None
    assert new.exists()
    assert result["data"]["selection_token"] == new.name[7:-5]
    assert result["effects"][-1] == {"kind": "selection.clear", "status": "unchanged", "target": old.name[7:-5]}
