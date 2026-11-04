"""`spec-dock dashboard summary` reads local files only (iss-00528, epic-00427 D-01, D-05, D-12)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.cli import main
from tests.support.canonical_repo import bare_remote, clone, git, isolate_user_state
from tests.support.dashboard import node, snapshot

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    isolate_user_state(monkeypatch, tmp_path)
    monkeypatch.chdir(tmp_path)
    _forbid_network(monkeypatch)
    return tmp_path / "state" / "spec-dock"


def _forbid_network(monkeypatch: pytest.MonkeyPatch) -> None:
    import urllib.request

    from spec_dock.runtime.infra import github_structure

    def refuse(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("dashboard summary must not contact GitHub or a server")

    monkeypatch.setattr(github_structure.GithubApi, "__init__", refuse)
    monkeypatch.setattr(urllib.request, "urlopen", refuse)


def _write_snapshot(state: Path, document: object, *, raw: bytes | None = None) -> Path:
    path = state / "github" / "github.com" / "o" / "r" / "snapshot.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw if raw is not None else json.dumps(document).encode())
    return path


def _document(**changes: object) -> dict[str, object]:
    document = snapshot(
        node(1, "epic", created_at="2026-10-20T00:00:00Z"),
        node(2, "issue", parent=1, in_progress=True, title="Doing"),
        node(3, "issue", parent=1, blocked_by=(2,)),
        fetched_at="2026-01-01T00:00:00Z",
    ).to_json()
    document.update(changes)
    return document


def _run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, Any]:
    code = main([*argv, "--json"])
    return code, json.loads(capsys.readouterr().out)


def test_named_repository_works_outside_any_checkout(state: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _write_snapshot(state, _document())
    code, result = _run(capsys, "dashboard", "summary", "o/r")
    assert code == 0, result
    assert (result["command"], result["status"], result["effects"]) == ("dashboard summary", "succeeded", [])
    summary = result["data"]["result"]
    assert result["data"]["kind"] == "dashboard"
    assert summary["schema"] == "specdock.dashboard-summary/v1" and summary["repository"] == "github.com/o/r"
    assert summary["stale"] is True  # fetched months before now
    assert [item["id"] for item in summary["in_progress"]] == ["iss-00002", "epic-00001"]
    assert [item["id"] for item in summary["blocked"]] == ["iss-00003"]
    assert summary["pull_requests"]["status"] == "unknown"
    assert (summary["hidden"], summary["server"]) == (False, None)
    code, again = _run(capsys, "dashboard", "summary", "github.com/o/r")
    assert code == 0 and again["data"]["result"]["repository"] == "github.com/o/r"


def test_inside_a_checkout_the_repository_comes_from_origin(
    tmp_path: Path, state: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    checkout = clone(bare_remote(tmp_path / "remote.git"), tmp_path / "main")
    git(checkout, "remote", "set-url", "origin", "https://github.com/O/R.git")
    _write_snapshot(state, _document())
    code, result = _run(capsys, "--project", str(checkout), "dashboard", "summary")
    assert code == 0, result
    assert result["data"]["result"]["repository"] == "github.com/o/r"


def test_server_url_needs_a_live_pid_and_hidden_marks_are_read(state: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _write_snapshot(state, _document())
    dashboard = state / "dashboard"
    dashboard.mkdir(parents=True)
    record = {
        "schema": "specdock.dashboard-server/v1",
        "urls": {"local": "http://127.0.0.1:47800/", "tailscale": None},
        "pid": os.getpid(),
        "version": "0.6.0",
        "started_at": "2026-11-04T00:00:00Z",
    }
    (dashboard / "server.json").write_text(json.dumps(record))
    (dashboard / "repositories.json").write_text(
        json.dumps({
            "schema": "specdock.dashboard-repositories/v1",
            "repositories": {"github.com/o/r": {"hidden_at": "2026-11-04T00:00:00Z"}},
        })
    )
    summary = _run(capsys, "dashboard", "summary", "o/r")[1]["data"]["result"]
    assert (summary["server"], summary["hidden"]) == ("http://127.0.0.1:47800/", True)
    finished = subprocess.run([sys.executable, "-c", "import os; print(os.getpid())"], capture_output=True, check=True)
    record["pid"] = int(finished.stdout)
    (dashboard / "server.json").write_text(json.dumps(record))
    (dashboard / "repositories.json").write_text("{broken")
    summary = _run(capsys, "dashboard", "summary", "o/r")[1]["data"]["result"]
    # Unreadable marks hide, as on the dashboard server (iss-00552 R-06; before, the summary read them as none).
    assert (summary["server"], summary["hidden"]) == (None, True)


def test_version_2_pull_requests_reach_the_summary(state: Path, capsys: pytest.CaptureFixture[str]) -> None:
    from datetime import datetime, timezone

    fetched = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    pull = {
        "number": 40,
        "state": "open",
        "is_draft": False,
        "head_ref_name": "chemitaro/iss-00002",
        "mergeable": "mergeable",
        "checks": "pending",
        "created_at": "2026-11-03T00:00:00Z",
        "merged_at": None,
        "closed_at": None,
        "url": "https://github.com/o/r/pull/40",
    }
    _write_snapshot(
        state,
        _document(
            version=2,
            fetched_at=fetched,
            pull_requests={"40": pull},
            pull_requests_error=None,
            pull_requests_fetched_at=fetched,
        ),
    )
    summary = _run(capsys, "dashboard", "summary", "o/r")[1]["data"]["result"]
    assert summary["stale"] is False and summary["pull_requests"]["status"] == "fresh"
    assert [(item["id"], item["merge"]) for item in summary["awaiting_merge"]] == [("iss-00002", "mergeable")]


@pytest.mark.parametrize(
    ("content", "code"),
    [
        (None, "DASHBOARD_SNAPSHOT_MISSING"),
        (b"{not json", "DASHBOARD_SNAPSHOT_UNREADABLE"),
        (json.dumps({"version": 1, "repository": "github.com/o/r"}).encode(), "DASHBOARD_SNAPSHOT_UNREADABLE"),
        (json.dumps({"version": 9}).encode(), "DASHBOARD_SNAPSHOT_UNSUPPORTED"),
    ],
)
def test_missing_unreadable_and_unknown_snapshots_stop_with_exit_3(
    state: Path, capsys: pytest.CaptureFixture[str], content: bytes | None, code: str
) -> None:
    if content is not None:
        _write_snapshot(state, None, raw=content)
    exit_code, result = _run(capsys, "dashboard", "summary", "o/r")
    assert (exit_code, result["status"], result["error"]["code"]) == (3, "failed", code)
    assert result["recovery"]["instructions"]
    assert result["effects"] == []


def test_an_invalid_repository_is_a_usage_error(state: Path, capsys: pytest.CaptureFixture[str]) -> None:
    exit_code, result = _run(capsys, "dashboard", "summary", "not a repo")
    assert (exit_code, result["error"]["code"]) == (2, "DASHBOARD_REPOSITORY_INVALID")


def test_text_output_lists_counts_and_items(state: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _write_snapshot(state, _document())
    assert main(["dashboard", "summary", "o/r"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("spec-dock: succeeded (dashboard summary)\n")
    assert (
        "(stale: older than 30 minutes)" in out and "counts done=0 doing=2 blocked=1 ready=0 unknown=0 total=3" in out
    )
    assert "iss-00002 Doing" in out
