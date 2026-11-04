"""`dashboard list`, `hide`, `show`, `summary` and `todo list` follow the dashboard settings (iss-00552 T-03, T-04, T-06, T-09)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.cli import main
from tests.support.canonical_repo import isolate_user_state
from tests.support.dashboard_site import register, sample, write_snapshot

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    isolate_user_state(monkeypatch, tmp_path)
    monkeypatch.chdir(tmp_path)
    root = tmp_path / "state" / "spec-dock"
    for key, catalog in (("github.com/o/r", "r"), ("github.com/o/s", "s")):
        register(root, key, tmp_path / catalog / "spec-dock" / ".canonical")
        write_snapshot(root, sample(key))
    return root


def _config(tmp_path: Path) -> Path:
    return tmp_path / "home" / ".config" / "spec-dock" / "config.json"


def _user(tmp_path: Path, dashboard: object) -> None:
    path = _config(tmp_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"schema": "specdock.config/v1", "dashboard": dashboard}))


def _run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, Any]:
    code = main([*argv, "--json"])
    return code, json.loads(capsys.readouterr().out)


def _rows(capsys: pytest.CaptureFixture[str]) -> dict[str, Any]:
    result = _run(capsys, "dashboard", "list")[1]["data"]["result"]
    return {row["repository"]: row for row in result["repositories"]}


def test_list_shows_the_mark_the_setting_and_its_source(
    state: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rows = _rows(capsys)
    assert {key: (row["hidden"], row["mark"], row["config"], row["hidden_by"]) for key, row in rows.items()} == {
        "github.com/o/r": (False, False, {"visible": True, "source": "default"}, []),
        "github.com/o/s": (False, False, {"visible": True, "source": "default"}, []),
    }
    _user(tmp_path, {"visible": False, "repositories": {"o/r": {"visible": True}}})
    (tmp_path / "r" / "spec-dock" / ".canonical" / "dashboard.json").write_text(
        json.dumps({"schema": "specdock.dashboard-settings/v1", "visible": False})
    )
    assert _run(capsys, "dashboard", "hide", "o/s")[0] == 0
    rows = _rows(capsys)
    assert (rows["github.com/o/r"]["config"], rows["github.com/o/r"]["hidden_by"]) == (
        {"visible": False, "source": "repository"},
        ["repository"],
    )
    assert rows["github.com/o/s"]["hidden_by"] == ["mark", "user"] and rows["github.com/o/s"]["served"] is False
    assert main(["dashboard", "list"]) == 0
    text = capsys.readouterr().out
    assert "github.com/o/r hidden by=repository config=repository" in text
    assert "github.com/o/s hidden by=mark,user config=user" in text


def test_list_reports_broken_settings(state: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _config(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text("{broken")
    result = _run(capsys, "dashboard", "list")[1]["data"]["result"]
    assert all(row["hidden_by"] == ["invalid"] for row in result["repositories"])
    (problem,) = result["config_problems"]
    assert (problem["layer"], problem["path"]) == ("user", str(path)) and problem["reason"]
    assert main(["dashboard", "list"]) == 0
    assert f"config problem: user {path}:" in capsys.readouterr().out


def test_hide_and_show_report_the_final_value(state: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, hidden = _run(capsys, "dashboard", "hide", "o/s")
    assert code == 0 and hidden["data"]["result"] == {
        "repository": "github.com/o/s",
        "hidden": True,
        "changed": True,
        "registered": True,
        "mark": True,
        "config": {"visible": True, "source": "default"},
        "hidden_by": ["mark"],
    }
    assert hidden["warnings"] == []
    _user(tmp_path, {"repositories": {"github.com/o/s": {"visible": False}}})
    code, shown = _run(capsys, "dashboard", "show", "o/s")
    result = shown["data"]["result"]
    assert code == 0 and (result["changed"], result["hidden"], result["mark"], result["hidden_by"]) == (
        True,
        True,
        False,
        ["user"],
    )
    (warning,) = shown["warnings"]
    assert warning["code"] == "DASHBOARD_HIDDEN_BY_CONFIG"
    assert warning["details"]["hidden_by"] == ["user"] and warning["details"]["repository"] == "github.com/o/s"
    _user(tmp_path, {})
    code, shown = _run(capsys, "dashboard", "show", "o/s")
    assert code == 0 and shown["data"]["result"]["hidden"] is False and shown["warnings"] == []


def test_the_commands_never_write_a_settings_file(
    state: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    for argv in (("dashboard", "hide", "o/r"), ("dashboard", "show", "o/r"), ("dashboard", "list")):
        assert _run(capsys, *argv)[0] == 0
    assert not _config(tmp_path).exists()
    assert not (tmp_path / "r" / "spec-dock" / ".canonical" / "dashboard.json").exists()


def test_todo_list_hidden_follows_the_settings(state: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _user(tmp_path, {"visible": False})
    code, listed = _run(capsys, "todo", "list", "--all-repositories")
    assert code == 0, listed
    assert {row["repository"]: row["hidden"] for row in listed["data"]["result"]["repositories"]} == {
        "github.com/o/r": True,
        "github.com/o/s": True,
    }


def test_summary_hidden_follows_the_settings(state: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert _run(capsys, "dashboard", "summary", "o/r")[1]["data"]["result"]["hidden"] is False
    _user(tmp_path, {"repositories": {"o/r": {"visible": False}}})
    assert _run(capsys, "dashboard", "summary", "o/r")[1]["data"]["result"]["hidden"] is True
    _user(tmp_path, {})
    second = tmp_path / "r2" / "spec-dock" / ".canonical"
    register(state, "github.com/o/s", second)
    (second / "dashboard.json").write_text(json.dumps({"schema": "specdock.dashboard-settings/v1", "visible": True}))
    summary = _run(capsys, "dashboard", "summary", "o/s")[1]["data"]["result"]
    rows = _rows(capsys)
    assert summary["hidden"] is rows["github.com/o/s"]["hidden"] is True  # clones disagree: hidden everywhere
