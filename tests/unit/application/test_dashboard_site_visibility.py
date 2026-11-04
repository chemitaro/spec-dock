"""The server's listing follows the dashboard settings and the hidden marks (iss-00552 T-01〜T-03, T-05〜T-08)."""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.application.dashboard_http import DashboardHttp, Request, Response
from spec_dock.runtime.application.dashboard_site import DashboardSite, RegistryRow, read_visibility
from spec_dock.runtime.infra.dashboard_store import hide_repository
from spec_dock.runtime.infra.github_structure import GithubRepository
from tests.support.canonical_repo import isolate_user_state
from tests.support.dashboard import NOW
from tests.support.dashboard_site import register, sample, write_snapshot

if TYPE_CHECKING:
    from pathlib import Path

    from spec_dock.runtime.domain.dashboard_visibility import Visibility

R, S = "github.com/o/r", "github.com/o/s"


class Env:
    def __init__(self, tmp_path: Path) -> None:
        self.state = tmp_path / "state"
        self.config = tmp_path / "home" / ".config" / "spec-dock" / "config.json"
        self.r = tmp_path / "r" / "spec-dock" / ".canonical"
        self.s = tmp_path / "s" / "spec-dock" / ".canonical"
        register(self.state, R, self.r)
        register(self.state, S, self.s)
        write_snapshot(self.state, sample(R))
        write_snapshot(self.state, sample(S))
        self.site = DashboardSite(self.state, now=lambda: NOW)

    def user(self, dashboard: object | None = None, *, raw: bytes | None = None) -> None:
        self.config.parent.mkdir(parents=True, exist_ok=True)
        document: dict[str, object] = {"schema": "specdock.config/v1"}
        if dashboard is not None:
            document["dashboard"] = dashboard
        _write(self.config, raw if raw is not None else json.dumps(document).encode())

    def shown(self) -> list[str]:
        return [site.key for site in self.site.repositories()]

    def row(self, key: str) -> RegistryRow:
        return next(row for row in self.site.rows() if row.repository == key)

    def visibility(self, key: str) -> Visibility:
        found = self.row(key).visibility
        assert found is not None
        return found


def _write(path: Path, payload: bytes) -> None:
    """Write and move the mtime forward so a same-size rewrite within one tick is still noticed."""
    before = path.stat().st_mtime_ns if path.exists() else 0
    path.write_bytes(payload)
    stamp = max(before + 1_000_000, path.stat().st_mtime_ns)
    os.utime(path, ns=(stamp, stamp))


def repo_setting(catalog: Path, value: object, *, raw: bytes | None = None) -> None:
    document: dict[str, object] = {"schema": "specdock.dashboard-settings/v1"}
    if value is not None:
        document["visible"] = value
    _write(catalog / "dashboard.json", raw if raw is not None else json.dumps(document).encode())


@pytest.fixture
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Env:
    isolate_user_state(monkeypatch, tmp_path)
    return Env(tmp_path)


def test_no_settings_keep_the_marks_only(env: Env) -> None:
    assert env.shown() == [R, S]
    hide_repository(env.state, GithubRepository("o", "s"), now=NOW)
    assert env.shown() == [R]
    row = env.row(S)
    assert (row.hidden, row.served, env.visibility(S).mark, env.visibility(S).hidden_by) == (
        True,
        False,
        True,
        ("mark",),
    )
    assert env.visibility(R).config.source == "default"
    assert env.site.config_problems() == ()


def test_user_settings_and_the_repository_file_apply_without_a_restart(env: Env) -> None:
    env.user({"visible": False, "repositories": {"o/r": {"visible": True}}})
    assert env.shown() == [R]
    assert env.visibility(S).hidden_by == ("user",)
    repo_setting(env.s, True)
    assert env.shown() == [R, S]
    assert env.visibility(S).config.source == "repository"
    repo_setting(env.r, False)
    assert env.shown() == [S]
    hide_repository(env.state, GithubRepository("o", "s"), now=NOW)
    assert env.shown() == []
    assert env.visibility(S).hidden_by == ("mark",)


def test_a_broken_user_file_hides_everything_until_it_is_fixed(env: Env) -> None:
    env.user(raw=b"{broken")
    assert env.shown() == []
    assert {env.visibility(row.repository).config.source for row in env.site.rows() if row.repository} == {"invalid"}
    (problem,) = env.site.config_problems()
    assert (problem.layer, problem.path) == ("user", str(env.config))
    env.user({"visible": True})
    assert env.shown() == [R, S] and env.site.config_problems() == ()


def test_a_broken_repository_file_and_disagreeing_clones_hide_that_repository(env: Env, tmp_path: Path) -> None:
    repo_setting(env.s, None, raw=b"[")
    assert env.shown() == [R]
    assert [problem.layer for problem in env.site.config_problems()] == ["repository"]
    repo_setting(env.s, None)
    second = tmp_path / "r2" / "spec-dock" / ".canonical"
    register(env.state, R, second)
    repo_setting(second, True)
    assert env.shown() == [S]
    (problem,) = env.site.config_problems()
    assert "disagree" in problem.reason and str(second / "dashboard.json") in problem.path


def test_read_visibility_answers_like_the_server(env: Env, tmp_path: Path) -> None:
    repository = GithubRepository("o", "s")
    env.user({"visible": False})
    assert read_visibility(env.state, repository).to_json()["hidden_by"] == ["user"]
    (env.state / "dashboard").mkdir(parents=True, exist_ok=True)
    (env.state / "dashboard" / "repositories.json").write_text("{broken")
    env.user({"visible": True})
    visibility = read_visibility(env.state, repository)
    assert visibility.hidden and visibility.mark  # unreadable marks hide, as on a fresh server
    assert visibility.hidden == DashboardSite(env.state).visibility(repository.key).hidden
    (env.state / "dashboard" / "repositories.json").unlink()
    unregistered = GithubRepository("o", "t")
    catalog = tmp_path / "t" / "c"
    catalog.mkdir(parents=True)
    repo_setting(catalog, False)
    assert read_visibility(env.state, unregistered).hidden is False
    assert read_visibility(env.state, unregistered, fallback_catalog=catalog).hidden_by == ("repository",)


def _http(site: DashboardSite) -> DashboardHttp:
    return DashboardHttp(
        site,
        hosts=("127.0.0.1",),
        port=47800,
        embed_hosts=("127.0.0.1",),
        local_url="http://127.0.0.1:47800/",
        version="0.5.1",
        started_at="2026-11-04T11:00:00Z",
        now=lambda: NOW,
    )


def _get(http: DashboardHttp, path: str) -> Response:
    return http.handle(Request("GET", path, {}, {"host": "127.0.0.1:47800"}))


def test_direct_urls_name_the_step_that_shows_the_repository(env: Env) -> None:
    http = _http(env.site)
    hide_repository(env.state, GithubRepository("o", "s"), now=NOW)
    page = _get(http, f"/r/{S}/")
    assert page.status == 404 and b"spec-dock dashboard show o/s" in page.body
    body = json.loads(_get(http, f"/api/v1/r/{S}/structure").body)
    assert body["error"]["next_steps"] == ["spec-dock dashboard show o/s"]
    repo_setting(env.r, False)
    page = _get(http, f"/r/{R}/")
    assert b"dashboard show" not in page.body and b"spec-dock dashboard list" in page.body
    assert str(env.r / "dashboard.json").encode() in page.body
    body = json.loads(_get(http, f"/api/v1/r/{R}/structure").body)
    assert body["error"]["next_steps"][0] == "spec-dock dashboard list"
    assert "spec-dock dashboard show o/r" not in body["error"]["next_steps"]
