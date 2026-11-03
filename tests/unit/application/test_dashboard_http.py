"""Routes, headers, API, materials and the "seen" endpoint of the dashboard server (iss-00529 T-02〜T-09, T-17)."""

from __future__ import annotations

from dataclasses import replace
import json
import os
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.runtime.application.dashboard_http import DashboardHttp, Request
from spec_dock.runtime.application.dashboard_site import DashboardSite
from spec_dock.runtime.application.dashboard_summary import summarize
from spec_dock.runtime.infra.dashboard_store import hide_repository, write_server_record
from spec_dock.runtime.infra.github_structure import GithubRepository
from tests.support.dashboard import NOW, closed, node, pr, prs, snapshot
from tests.support.dashboard_site import register, sample, scope_dir, snapshot_file, write_snapshot

if TYPE_CHECKING:
    from pathlib import Path

HOST = "127.0.0.1:47800"
ORIGIN = "http://127.0.0.1:47800"
EMBED = "frame-ancestors 'self' http://127.0.0.1:* http://localhost:* http://100.64.0.7:*"


class Env:
    def __init__(self, tmp_path: Path) -> None:
        self.state = tmp_path / "state"
        self.r = tmp_path / "r" / "spec-dock" / ".canonical"
        self.s = tmp_path / "s" / "spec-dock" / ".canonical"
        register(self.state, "github.com/o/r", self.r)
        register(self.state, "github.com/o/s", self.s)
        write_snapshot(self.state, sample("github.com/o/r"))
        write_snapshot(self.state, sample("github.com/o/s"))
        self.site = DashboardSite(self.state, now=lambda: NOW)
        self.http = DashboardHttp(
            self.site,
            hosts=("127.0.0.1", "localhost", "100.64.0.7"),
            port=47800,
            embed_hosts=("127.0.0.1", "localhost", "100.64.0.7"),
            local_url="http://127.0.0.1:47800/",
            version="0.5.1",
            started_at="2026-11-04T11:00:00Z",
            now=lambda: NOW,
        )

    def get(self, path: str, *, host: str = HOST, **headers: str) -> Any:
        target, _, query = path.partition("?")
        params: dict[str, list[str]] = {}
        for pair in filter(None, query.split("&")):
            key, _, value = pair.partition("=")
            params.setdefault(key, []).append(value)
        return self.http.handle(Request("GET", target, params, {"host": host, **headers}))

    def json(self, path: str) -> Any:
        response = self.get(path)
        assert response.header("content-type").startswith("application/json"), path
        return response.status, json.loads(response.body)

    def post_seen(self, repository: str = "github.com/o/r", **overrides: str) -> Any:
        headers = {
            "host": HOST,
            "origin": ORIGIN,
            "x-specdock-dashboard": "1",
            "content-type": "application/json",
            **overrides,
        }
        headers = {key: value for key, value in headers.items() if value != ""}
        return self.http.handle(Request("POST", f"/api/v1/r/{repository}/seen", {}, headers, b"{}"))


@pytest.fixture
def env(tmp_path: Path) -> Env:
    return Env(tmp_path)


# --- Listing (T-02) ------------------------------------------------------------------------------------------


def test_repositories_lists_visible_registered_repositories(env: Env, tmp_path: Path) -> None:
    status, body = env.json("/api/v1/repositories")
    assert status == 200 and body["schema"] == "specdock.dashboard/v1"
    assert [item["repository"] for item in body["repositories"]] == ["github.com/o/r", "github.com/o/s"]
    assert body["repositories"][0]["path"] == "/r/github.com/o/r/"
    assert body["server"]["embed_hosts"] == ["127.0.0.1", "localhost", "100.64.0.7"]
    register(env.state, None, tmp_path / "unknown" / "c")
    register(env.state, "github.com/o/t", tmp_path / "t" / "c")
    _status, body = env.json("/api/v1/repositories")
    assert [item["repository"] for item in body["repositories"]][-1] == "github.com/o/t"  # no restart (R-01)
    assert body["unknown_count"] == 1
    hide_repository(env.state, GithubRepository("o", "s"), now=NOW)
    _status, body = env.json("/api/v1/repositories")
    assert "github.com/o/s" not in [item["repository"] for item in body["repositories"]]
    rows = {row.repository: row for row in env.site.rows()}
    assert rows["github.com/o/s"].hidden and not rows["github.com/o/s"].served
    assert rows[None].problem == "repository_unknown"


def test_two_clones_serve_the_structure_but_refuse_materials(env: Env, tmp_path: Path) -> None:
    register(env.state, "github.com/o/r", tmp_path / "r2" / "c")
    status, body = env.json("/api/v1/r/github.com/o/r/structure")
    assert status == 200 and body["scopes"]
    assert "REPOSITORY_AMBIGUOUS" in [item["code"] for item in body["notices"]]
    response = env.get("/r/github.com/o/r/files/iss-00002/explanation.html")
    assert response.status == 409 and json.loads(response.body)["code"] == "DASHBOARD_REPOSITORY_AMBIGUOUS"
    assert "sandbox" in response.header("content-security-policy")
    assert env.get("/api/v1/r/github.com/o/s/structure").status == 200


def test_unreadable_hidden_marks_keep_the_last_readable_marks(env: Env) -> None:
    hide_repository(env.state, GithubRepository("o", "s"), now=NOW)
    assert [site.key for site in env.site.repositories()] == ["github.com/o/r"]
    (env.state / "dashboard" / "repositories.json").write_text("{broken")
    assert [site.key for site in env.site.repositories()] == ["github.com/o/r"]


def test_an_unreadable_registry_keeps_the_last_listing(env: Env) -> None:
    assert len(env.site.repositories()) == 2
    (env.state / "canonical-registry.json").write_text("{broken")
    assert len(env.site.repositories()) == 2
    assert env.site.registry_error() is not None


# --- Reading and notices (T-03, T-04) --------------------------------------------------------------------------


def _codes(body: dict[str, Any]) -> list[str]:
    return [item["code"] for item in body["notices"]]


def test_structure_returns_only_its_repository_scopes(env: Env) -> None:
    write_snapshot(env.state, replace(snapshot(node(9, "issue")), repository="github.com/o/s"))
    _status, r = env.json("/api/v1/r/github.com/o/r/structure")
    _status, s = env.json("/api/v1/r/github.com/o/s/structure")
    assert [item["id"] for item in r["scopes"]] == ["epic-00001", "iss-00002", "iss-00003"]
    assert [item["id"] for item in s["scopes"]] == ["iss-00009"]
    item = r["scopes"][2]
    assert item["state"] == "blocked" and item["path"] == "/r/github.com/o/r/scopes/iss-00003"
    assert r["snapshot"] == {
        "status": "ok",
        "fetched_at": "2026-11-04T11:50:00Z",
        "age_seconds": 600,
        "stale": False,
        "detail": None,
    }
    assert _codes(r) == ["PULL_REQUESTS_UNKNOWN"]
    assert r["timeline"]["events"] and r["timeline"]["weeks"]


def test_notices_for_missing_stale_unsupported_and_anomalies(env: Env) -> None:
    path = snapshot_file(env.state, "github.com/o/r")
    path.unlink()
    status, body = env.json("/api/v1/r/github.com/o/r/structure")
    assert status == 200 and body["scopes"] == [] and body["snapshot"]["status"] == "missing"
    assert _codes(body) == ["SNAPSHOT_MISSING"]
    assert "spec-dock canonical link" in body["notices"][0]["next_steps"]
    write_snapshot(env.state, sample(fetched_at="2026-11-04T08:00:00Z"))
    _status, body = env.json("/api/v1/r/github.com/o/r/structure")
    stale = next(item for item in body["notices"] if item["code"] == "SNAPSHOT_STALE")
    assert "4時間前から更新されていません" in stale["text"] and body["snapshot"]["stale"] is True
    document = sample().to_json()
    document["version"] = 99
    write_snapshot(env.state, sample(), raw=json.dumps(document).encode())
    _status, body = env.json("/api/v1/r/github.com/o/r/structure")
    assert body["snapshot"]["status"] == "unsupported" and body["scopes"] == []
    assert _codes(body) == ["SNAPSHOT_UNSUPPORTED"]
    from spec_dock.runtime.domain.canonical_structure import StructureAnomaly

    write_snapshot(env.state, replace(sample(), anomalies=(StructureAnomaly(3, "PARENT_MISSING", "x"),)))
    _status, body = env.json("/api/v1/r/github.com/o/r/structure")
    assert "STRUCTURE_ANOMALIES" in _codes(body) and body["anomalies"][0]["code"] == "PARENT_MISSING"


def test_a_broken_snapshot_keeps_the_last_readable_model(env: Env) -> None:
    env.json("/api/v1/r/github.com/o/r/structure")
    write_snapshot(env.state, sample(), raw=b"{half")
    _status, body = env.json("/api/v1/r/github.com/o/r/structure")
    assert body["snapshot"]["status"] == "unreadable" and len(body["scopes"]) == 3
    assert _codes(body)[0] == "SNAPSHOT_UNREADABLE" and "最後に読めた" in body["notices"][0]["text"]
    status, error = env.json("/api/v1/r/github.com/o/r/summary")
    assert status == 503 and error["error"]["code"] == "DASHBOARD_SNAPSHOT_UNREADABLE"
    fresh = DashboardSite(env.state, now=lambda: NOW)
    view = fresh.view(fresh.repositories()[0])
    assert view.status == "unreadable" and view.model is None  # never read: nothing to keep


def test_pull_request_notices(env: Env) -> None:
    write_snapshot(env.state, prs(sample(), pr(10, "iss-00002")))
    _status, body = env.json("/api/v1/r/github.com/o/r/structure")
    assert "PULL_REQUESTS_UNKNOWN" not in _codes(body)
    assert body["scopes"][1]["pr"]["number"] == 10 and body["scopes"][1]["lane"] == "awaiting_merge"


def test_revision_follows_the_snapshot_and_not_seen(env: Env) -> None:
    _status, first = env.json("/api/v1/r/github.com/o/r/revision")
    assert len(first["revision"]) == 16
    assert env.post_seen().status == 200
    _status, again = env.json("/api/v1/r/github.com/o/r/revision")
    assert again["revision"] == first["revision"]
    path = write_snapshot(env.state, sample(fetched_at="2026-11-04T11:55:00Z"))
    os.utime(path, ns=(1, 1))
    _status, changed = env.json("/api/v1/r/github.com/o/r/revision")
    assert changed["revision"] != first["revision"]


# --- Routes and headers (T-05, T-06) -------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path",
    [
        "/",
        "/r/github.com/o/r/",
        "/r/github.com/o/r",
        "/r/github.com/o/r/graph",
        "/r/github.com/o/r/board",
        "/r/github.com/o/r/timeline",
        "/r/github.com/o/r/scopes/iss-00002",
    ],
)
def test_every_screen_path_returns_the_shell(env: Env, path: str) -> None:
    response = env.get(path)
    assert response.status == 200 and b'id="view"' in response.body
    csp = response.header("content-security-policy")
    assert csp.endswith("frame-ancestors 'self'") and "script-src 'self'" in csp
    embedded = env.get(path + "?embed=1")
    assert embedded.header("content-security-policy").endswith(EMBED)
    for item in (response, embedded):
        assert item.header("x-frame-options") is None and item.header("access-control-allow-origin") is None
        assert item.header("x-content-type-options") == "nosniff"


def test_hidden_and_unknown_repositories(env: Env) -> None:
    hide_repository(env.state, GithubRepository("o", "r"), now=NOW)
    for path in ("/r/github.com/o/r/", "/r/github.com/o/r/files/iss-00002/explanation.html"):
        response = env.get(path)
        assert response.status == 404 and "spec-dock dashboard show o/r" in response.body.decode()
        assert b"Scope 2" not in response.body
    status, body = env.json("/api/v1/r/github.com/o/r/structure")
    assert status == 404 and body["error"]["next_steps"] == ["spec-dock dashboard show o/r"]
    assert env.get("/r/github.com/o/zz/").status == 404
    assert env.get("/r/github.com/o/s/nope").status == 404
    assert env.get("/nope").status == 404


def test_methods_and_hosts(env: Env) -> None:
    for method in ("PUT", "DELETE", "PATCH", "OPTIONS"):
        assert env.http.handle(Request(method, "/", {}, {"host": HOST})).status == 405
    assert env.http.handle(Request("POST", "/api/v1/repositories", {}, {"host": HOST})).status == 405
    assert env.get("/", host="evil.example:47800").status == 421
    assert env.get("/", host="127.0.0.1:1").status == 421
    assert env.get("/", host="").status == 421
    assert env.get("/", host="localhost:47800").status == 200
    assert env.get("/", host="100.64.0.7:47800").status == 200
    for bad in ("/r/github.com/o/r/../s/", "/assets/%2e%2e/x", "/r/github.com/o/r/files/iss-00002/%2Fetc", "x"):
        assert env.get(bad).status in (400, 404), bad


def test_cors_only_on_shared_parts(env: Env) -> None:
    ds = env.get("/ds/ds.css")
    assert ds.status == 200 and ds.header("access-control-allow-origin") == "*"
    assert ds.header("content-type").startswith("text/css")
    copy = env.get("/r/github.com/o/design-system/ds.js")
    assert copy.status == 200 and copy.body == env.get("/ds/ds.js").body
    vendor = env.get("/vendor/highlightjs/11.11.1/LICENSE")
    assert vendor.status == 200 and vendor.header("access-control-allow-origin") == "*"
    for path in (
        "/api/v1/repositories",
        "/api/v1/r/github.com/o/r/structure",
        "/api/v1/r/github.com/o/r/summary",
        "/r/github.com/o/r/",
        "/assets/app.js",
    ):
        assert env.get(path).header("access-control-allow-origin") is None, path
    assert env.get("/assets/app.js").header("content-type").startswith("text/javascript")


# --- Materials (T-07) ----------------------------------------------------------------------------------------


def test_materials_are_sandboxed_with_the_embedding_ancestors(env: Env) -> None:
    directory = scope_dir(env.r, "iss-00002")
    (directory / "explanation.html").write_text("<script>parent.document</script>")
    (directory / "artifacts").mkdir()
    (directory / "artifacts" / "a.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'><script/></svg>")
    (directory / "artifacts" / "data.bin").write_bytes(b"\x00\x01")
    for name, kind in (
        ("explanation.html", "text/html"),
        ("artifacts/a.svg", "image/svg+xml"),
        ("artifacts/data.bin", "application/octet-stream"),
    ):
        response = env.get(f"/r/github.com/o/r/files/iss-00002/{name}")
        assert response.status == 200 and response.header("content-type").startswith(kind), name
        csp = response.header("content-security-policy")
        assert csp == f"sandbox allow-scripts allow-popups; {EMBED}", name
        assert "allow-same-origin" not in csp and response.header("x-content-type-options") == "nosniff"
        assert response.header("access-control-allow-origin") is None
    missing = env.get("/r/github.com/o/r/files/iss-00002/none.html")
    assert missing.status == 404 and "sandbox" in missing.header("content-security-policy")


def test_materials_refuse_links_parents_directories_and_bad_ids(env: Env, tmp_path: Path) -> None:
    directory = scope_dir(env.r, "iss-00002")
    secret = tmp_path / "secret.txt"
    secret.write_text("secret")
    (directory / "link.txt").symlink_to(secret)
    (directory / "sub").mkdir()
    linked = scope_dir(env.r, "iss-00003").parent / "iss-00004"
    linked.symlink_to(directory)
    for path in (
        "/r/github.com/o/r/files/iss-00002/link.txt",
        "/r/github.com/o/r/files/iss-00002/sub",
        "/r/github.com/o/r/files/iss-00002/../iss-00003/x",
        "/r/github.com/o/r/files/iss-2/explanation.html",
        "/r/github.com/o/r/files/iss-00004/link.txt",
        "/r/github.com/o/r/files/iss-00002",
    ):
        response = env.get(path)
        assert response.status in (400, 404) and b"secret" not in response.body, path


# --- Seen (T-08) ---------------------------------------------------------------------------------------------


def test_seen_is_guarded(env: Env) -> None:
    for overrides in (
        {"origin": "http://evil.example"},
        {"origin": "http://127.0.0.1:1"},
        {"origin": ""},
        {"x-specdock-dashboard": ""},
        {"x-specdock-dashboard": "0"},
        {"content-type": "text/plain"},
        {"content-type": "application/x-www-form-urlencoded"},
    ):
        response = env.post_seen(**overrides)
        assert response.status == 403, overrides
        assert response.header("access-control-allow-origin") is None
    assert not (env.state / "dashboard" / "seen.json").exists()
    assert env.post_seen(origin="http://localhost:47800").status == 200
    assert env.post_seen(**{"content-type": "application/json; charset=utf-8"}).status == 200
    assert env.post_seen("github.com/o/zz").status == 404


def test_changes_keep_their_baseline_until_the_next_page_load(env: Env) -> None:
    write_snapshot(env.state, sample())
    _status, first = env.json("/api/v1/r/github.com/o/r/structure")
    assert first["seen"] == {"latest_id": None, "baseline_id": None} and first["changes_count"] == 0
    baseline = json.loads(env.post_seen().body)["seen_id"]
    changed = snapshot(
        node(1, "epic"),
        closed(2, "issue", parent=1, title="Doing"),
        node(3, "issue", parent=1, blocked_by=(2,)),
        node(4, "issue", parent=1),
        fetched_at="2026-11-04T11:55:00Z",
    )
    write_snapshot(env.state, prs(replace(changed, repository="github.com/o/r"), pr(11, "iss-00003", draft=True)))
    _status, body = env.json(f"/api/v1/r/github.com/o/r/structure?baseline={baseline}")
    marks = {item["id"]: item["change"] for item in body["scopes"] if item["change"]}
    assert set(marks) == {"epic-00001", "iss-00002", "iss-00003", "iss-00004"}  # the epic is no longer doing
    assert marks["iss-00004"]["kinds"] == ["new"] and marks["iss-00002"]["state_before"] == "doing"
    assert body["changes_count"] == 4 and body["seen"]["baseline_id"] == baseline
    second = json.loads(env.post_seen().body)["seen_id"]  # another device opens the screen
    _status, kept = env.json(f"/api/v1/r/github.com/o/r/structure?baseline={baseline}")
    assert kept["changes_count"] == 4 and kept["seen"]["latest_id"] == second
    _status, cleared = env.json("/api/v1/r/github.com/o/r/structure")
    assert cleared["changes_count"] == 0 and cleared["seen"]["baseline_id"] == second
    _status, gone = env.json("/api/v1/r/github.com/o/r/structure?baseline=0000")
    assert gone["seen"]["baseline_id"] == second  # unknown baseline: compare with the latest
    _status, detail = env.json(f"/api/v1/r/github.com/o/r/scopes/iss-00004?baseline={baseline}")
    assert detail["scope"]["change"]["kinds"] == ["new"] and detail["upstream"] == {"direct": [], "indirect": []}


def test_seen_without_a_structure_is_refused(env: Env) -> None:
    snapshot_file(env.state, "github.com/o/r").unlink()
    assert env.post_seen().status == 409


# --- Summary and scope (T-09) --------------------------------------------------------------------------------


def test_summary_matches_the_cli(env: Env) -> None:
    write_server_record(
        env.state, local="http://127.0.0.1:47800/", tailscale=None, pid=os.getpid(), version="x", started_at="y"
    )
    status, served = env.json("/api/v1/r/github.com/o/r/summary")
    cli = summarize("dashboard summary", GithubRepository("o", "r"), state_root=env.state, now=lambda: NOW)
    assert status == 200 and served == cli.data.result  # type: ignore[attr-defined]
    assert served["server"] == "http://127.0.0.1:47800/" and served["hidden"] is False
    snapshot_file(env.state, "github.com/o/r").unlink()
    status, error = env.json("/api/v1/r/github.com/o/r/summary")
    assert status == 503 and error["error"]["code"] == "DASHBOARD_SNAPSHOT_MISSING"


def test_scope_detail_and_unknown_scope(env: Env) -> None:
    status, body = env.json("/api/v1/r/github.com/o/r/scopes/epic-00001")
    assert status == 200 and body["child_stages"]["stages"] == [["iss-00002"], ["iss-00003"]]
    assert env.json("/api/v1/r/github.com/o/r/scopes/iss-00099")[0] == 404


def test_one_repository_failure_stays_in_its_responses(env: Env, monkeypatch: pytest.MonkeyPatch) -> None:
    real = env.site.view

    def broken(site: Any) -> Any:
        if site.key == "github.com/o/r":
            raise RuntimeError("boom")
        return real(site)

    monkeypatch.setattr(env.site, "view", broken)
    assert env.json("/api/v1/r/github.com/o/r/structure")[0] == 500
    assert env.json("/api/v1/r/github.com/o/s/structure")[0] == 200


# --- Read only (T-17) ----------------------------------------------------------------------------------------


def test_reading_everything_writes_nothing_but_seen(env: Env) -> None:
    directory = scope_dir(env.r, "iss-00002")
    (directory / "explanation.html").write_text("x")

    def tree() -> dict[str, bytes]:
        found: dict[str, bytes] = {}
        for root in (env.r, env.state):
            for path in sorted(root.rglob("*")):
                if path.is_file() and "dashboard" not in path.parts:
                    found[str(path)] = path.read_bytes()
        return found

    before = tree()
    for path in (
        "/",
        "/api/v1/repositories",
        "/r/github.com/o/r/board",
        "/api/v1/r/github.com/o/r/structure",
        "/api/v1/r/github.com/o/r/summary",
        "/api/v1/r/github.com/o/r/revision",
        "/api/v1/r/github.com/o/r/scopes/iss-00002",
        "/r/github.com/o/r/files/iss-00002/explanation.html",
    ):
        assert env.get(path).status == 200, path
    assert tree() == before
