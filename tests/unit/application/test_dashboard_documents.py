"""The dashboard's document pages, check results and plan progress (iss-00535 T-01〜T-06)."""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.runtime.application.dashboard_http import DashboardHttp, Request
from spec_dock.runtime.application.dashboard_site import DashboardSite
from tests.support.cue import cue_executable
from tests.support.cue_scopes import install_fake_cue, place_sample
from tests.support.dashboard import NOW, node, snapshot
from tests.support.dashboard_site import register, scope_dir, write_snapshot

if TYPE_CHECKING:
    from pathlib import Path

HOST = "127.0.0.1:47800"
BASE = "/r/github.com/o/r/scopes"
EMBED = "frame-ancestors 'self' http://127.0.0.1:*"


class Env:
    def __init__(self, tmp_path: Path) -> None:
        self.state = tmp_path / "state"
        self.catalog = tmp_path / "r" / "spec-dock" / ".canonical"
        register(self.state, "github.com/o/r", self.catalog)
        structure = snapshot(
            node(1, "epic", title="The epic"),
            node(2, "issue", parent=1, title="A CUE <b>Issue</b>"),
            node(3, "issue", parent=1, title="A Markdown Issue"),
        )
        write_snapshot(self.state, structure.__class__(**{**structure.__dict__, "repository": "github.com/o/r"}))
        self.site = DashboardSite(self.state, now=lambda: NOW)
        self.http = DashboardHttp(
            self.site,
            hosts=("127.0.0.1",),
            port=47800,
            embed_hosts=("127.0.0.1",),
            local_url="http://127.0.0.1:47800/",
            version="0.6.0",
            started_at="2026-11-04T11:00:00Z",
            now=lambda: NOW,
        )

    def get(self, path: str) -> Any:
        return self.http.handle(Request("GET", path, {}, {"host": HOST}))

    def details(self, scope_id: str) -> dict[str, Any]:
        response = self.get(f"/api/v1/r/github.com/o/r/scopes/{scope_id}")
        assert response.status == 200, response.body
        return json.loads(response.body)["details"]


@pytest.fixture
def env(tmp_path: Path) -> Env:
    return Env(tmp_path)


@pytest.fixture
def real_cue() -> None:
    cue_executable()


def _sandboxed(response: Any) -> None:
    policy = response.header("content-security-policy")
    assert policy.startswith("sandbox allow-scripts allow-popups;") and EMBED in policy
    assert "allow-same-origin" not in policy
    assert response.header("x-content-type-options") == "nosniff"


# --- CUE: the drawn page (T-01) ------------------------------------------------------------------------------


@pytest.mark.usefixtures("real_cue")
def test_a_cue_scope_is_drawn_reading_only_the_servers_design_system(env: Env) -> None:
    place_sample(scope_dir(env.catalog, "iss-00002"), "issue-strict-complete")
    response = env.get(f"{BASE}/iss-00002/doc")
    assert response.status == 200
    assert response.header("content-type") == "text/html; charset=utf-8"
    _sandboxed(response)
    page = response.body.decode()
    assert '<link rel="stylesheet" href="/ds/ds.css">' in page and '<script src="/ds/ds.js"></script>' in page
    assert '<meta name="ds-vendor-base" content="/vendor/">' in page
    assert "<title>iss-00002 A CUE &lt;b&gt;Issue&lt;/b&gt;</title>" in page
    assert not re.search(r"(src|href)=\"https?:", page)  # nothing from the internet (R-01)
    assert "書き出しを作る" in page  # the step of plan.cue, drawn from the CUE files


def test_a_markdown_scope_or_an_unknown_scope_has_no_cue_page(env: Env) -> None:
    (scope_dir(env.catalog, "iss-00003") / "requirement.md").write_text("# req\n")
    assert env.get(f"{BASE}/iss-00003/doc").status == 404
    response = env.get(f"{BASE}/iss-00099/doc")
    assert response.status == 404 and b"iss-00099" not in response.body
    _sandboxed(response)


# --- Markdown documents and ADRs (T-03) ----------------------------------------------------------------------


def test_markdown_documents_and_adrs_are_wrapped_in_the_thin_page(env: Env) -> None:
    directory = scope_dir(env.catalog, "iss-00003")
    for name in ("requirement.md", "design.md", "plan.md", "report.md"):
        (directory / name).write_text(f"# {name}\n\n</script><script>alert(1)</script>\n")
    (directory / "artifacts").mkdir()
    (directory / "artifacts" / "20260101t000000z-adr-keep-it.md").write_text("# ADR\n")
    (directory / "discussions").mkdir()
    (directory / "discussions" / "20260101t000000z-01-adr-old.md").write_text("# old ADR\n")
    for path in (
        "requirement.md",
        "design.md",
        "plan.md",
        "report.md",
        "artifacts/20260101t000000z-adr-keep-it.md",
        "discussions/20260101t000000z-01-adr-old.md",
    ):
        response = env.get(f"{BASE}/iss-00003/doc/{path}")
        assert response.status == 200, path
        _sandboxed(response)
        page = response.body.decode()
        assert '<script src="/ds/ds.js"></script>' in page and '<meta name="ds-vendor-base" content="/vendor/">' in page
        assert page.count("</script>") == 2  # the source block and ds.js: the document cannot close it (F-02)
    details = env.details("iss-00003")
    assert details["adrs"] == [
        {
            "name": "20260101t000000z-adr-keep-it.md",
            "path": "artifacts/20260101t000000z-adr-keep-it.md",
            "view": f"{BASE}/iss-00003/doc/artifacts/20260101t000000z-adr-keep-it.md",
        },
        {
            "name": "20260101t000000z-01-adr-old.md",
            "path": "discussions/20260101t000000z-01-adr-old.md",
            "view": f"{BASE}/iss-00003/doc/discussions/20260101t000000z-01-adr-old.md",
        },
    ]
    views = {item["key"]: item["view"] for item in details["documents"]}
    assert views["requirement"] == f"{BASE}/iss-00003/doc/requirement.md"
    assert views["report"] == f"{BASE}/iss-00003/doc/report.md"
    assert views["explanation"] is None
    assert details["spec"] is None and details["check"] is None and details["progress"] is None


def test_other_paths_links_and_missing_documents_are_refused(env: Env, tmp_path: Path) -> None:
    directory = scope_dir(env.catalog, "iss-00003")
    (directory / "notes.md").write_text("x")
    (directory / "artifacts").mkdir()
    (directory / "artifacts" / "plain-note.md").write_text("x")
    (tmp_path / "secret.md").write_text("secret")
    (directory / "report.md").symlink_to(tmp_path / "secret.md")
    (directory / "artifacts" / "x-adr-link.md").symlink_to(tmp_path / "secret.md")
    for path in (
        "notes.md",
        "artifacts/plain-note.md",
        "report.md",
        "artifacts/x-adr-link.md",
        "design.md",
        "requirement.cue",
        "..%2Fsecret.md",
        "artifacts/../report.md",
    ):
        response = env.get(f"{BASE}/iss-00003/doc/{path}")
        assert response.status in (400, 404), path
        assert b"secret" not in response.body
    assert env.details("iss-00003")["adrs"] == []


def test_an_ambiguous_catalog_refuses_documents_like_materials(env: Env, tmp_path: Path) -> None:
    register(env.state, "github.com/o/r", tmp_path / "r2" / "c")
    response = env.get(f"{BASE}/iss-00002/doc")
    assert response.status == 409 and json.loads(response.body)["code"] == "DASHBOARD_REPOSITORY_AMBIGUOUS"
    _sandboxed(response)


# --- Check results and plan progress (T-02, T-04) ------------------------------------------------------------


@pytest.mark.usefixtures("real_cue")
def test_a_complete_scope_reports_no_errors_and_its_progress(env: Env) -> None:
    place_sample(scope_dir(env.catalog, "iss-00002"), "issue-strict-complete")
    details = env.details("iss-00002")
    assert details["spec"] == f"{BASE}/iss-00002/doc"
    assert details["check"] == {"status": "ok", "complete": True, "errors": [], "warnings": [], "next_steps": []}
    # S-01 done, S-02 doing, S-03 dropped: dropped leaves the total (R-04).
    assert details["progress"] == {
        "total": 2,
        "done": 1,
        "doing": 1,
        "todo": 0,
        "dropped": 1,
        "doing_steps": [{"id": "S-02", "title": "上書きを止める"}],
    }
    views = {item["key"]: item["view"] for item in details["documents"]}
    assert views["requirement"] == views["design"] == views["plan"] == f"{BASE}/iss-00002/doc"
    assert views["report"] == f"{BASE}/iss-00002/doc/report.md"


@pytest.mark.usefixtures("real_cue")
def test_errors_and_warnings_are_listed(env: Env) -> None:
    from tests.support.cue_scopes import skeleton_explanation

    place_sample(scope_dir(env.catalog, "iss-00002"), "issue-standard-gaps", explanation=skeleton_explanation())
    check = env.details("iss-00002")["check"]
    assert check["status"] == "invalid" and check["next_steps"] == ["spec-dock scope check iss-00002"]
    assert check["errors"] and {item["code"] for item in check["errors"]} == {"SPEC_FINDINGS"}
    assert [item["code"] for item in check["warnings"]] == ["EXPLANATION_SKELETON"]
    assert check["warnings"][0]["file"] == "iss-00002/explanation.html"


def test_plan_progress_counts_by_status() -> None:
    from spec_dock.runtime.application.dashboard_documents import plan_progress

    steps = {
        "S-01": {"title": "a", "status": "done"},
        "S-02": {"title": "b", "status": "doing"},
        "S-03": {"title": "c"},
        "S-04": {"title": "d", "status": "dropped"},
        "S-05": {"title": "e", "status": "doing"},
        "S-06": {"title": "f", "status": "done"},
    }
    assert plan_progress({"steps": steps}) == {
        "total": 5,
        "done": 2,
        "doing": 2,
        "todo": 1,
        "dropped": 1,
        "doing_steps": [{"id": "S-02", "title": "b"}, {"id": "S-05", "title": "e"}],
    }
    assert plan_progress({"steps": {}}) is None and plan_progress({}) is None and plan_progress(None) is None


# --- Failures (T-05) and remembering (T-06) ------------------------------------------------------------------


def test_without_cue_the_page_names_the_next_step_and_the_rest_continues(
    env: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    from tests.support.cue_scopes import hide_cue

    place_sample(scope_dir(env.catalog, "iss-00002"), "issue-strict-complete")
    hide_cue(monkeypatch)
    response = env.get(f"{BASE}/iss-00002/doc")
    assert response.status == 503
    _sandboxed(response)
    assert "CUE_NOT_FOUND" in response.body.decode() and "spec-dock scope check iss-00002" in response.body.decode()
    details = env.details("iss-00002")
    assert details["check"]["status"] == "failed" and details["check"]["code"] == "CUE_NOT_FOUND"
    assert details["check"]["next_steps"] == [
        "cue v0.17.1 以上を PATH に入れる（cue version で確かめる）",
        "spec-dock scope check iss-00002",
    ]
    assert details["progress"] is None
    assert details["catalog"] == "ok" and details["documents"][0]["key"] == "requirement"


def test_a_time_out_is_a_failure_that_is_not_remembered(
    env: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    place_sample(scope_dir(env.catalog, "iss-00002"), "issue-strict-complete")
    env.http.documents.timeout = 0.2
    fake = install_fake_cue(tmp_path, monkeypatch, sleep=1.0)
    first = env.details("iss-00002")["check"]
    assert first["status"] == "failed" and first["code"] == "CUE_TIMEOUT"
    before = len(fake.calls())
    env.details("iss-00002")
    assert len(fake.calls()) > before  # tried again (F-01)


@pytest.mark.usefixtures("real_cue")
def test_cue_runs_again_only_after_a_file_changed(env: Env) -> None:
    directory = place_sample(scope_dir(env.catalog, "iss-00002"), "issue-strict-complete")
    calls: list[str] = []
    original = env.http.documents.render

    def counting(*args: Any, **kwargs: Any) -> Any:
        calls.append("render")
        return original(*args, **kwargs)

    env.http.documents.render = counting
    env.details("iss-00002")
    env.get(f"{BASE}/iss-00002/doc")
    env.details("iss-00002")
    assert calls == ["render"]
    plan = directory / "plan.cue"
    plan.write_text(plan.read_text().replace('status: "doing"', 'status: "done"'))
    assert env.details("iss-00002")["progress"]["done"] == 2 and calls == ["render", "render"]
    types = env.catalog.parent / "spec-dock" / "cue"  # the repository's types below the registry's main checkout
    types.mkdir(parents=True)
    (types / "extra.cue").write_text("package spec\n")
    env.details("iss-00002")
    assert len(calls) == 3


# --- The screens (T-07; the drawn look is T-08, checked in a browser and kept in report.md) -----------------


def _asset(name: str) -> str:
    from spec_dock.runtime.infra.dashboard_assets import screen_asset

    asset = screen_asset(name.split("/"))
    assert asset is not None, name
    return asset.body.decode("utf-8")


def test_the_detail_screen_frames_documents_in_a_sandbox_and_shows_check_errors() -> None:
    scope = _asset("views/_shared/scope_tabs.js")  # the tabs moved out of scope.js (iss-00587 D-03)
    assert 'const FRAME_SANDBOX = "allow-scripts allow-popups";' in scope
    assert 'sandbox="${FRAME_SANDBOX}"' in scope and "allow-same-origin" not in scope
    assert 'referrerpolicy="no-referrer"' in scope
    for marker in (
        "details.spec",
        "details.adrs",
        "details.check",
        'data-code="render-failed"',
        'data-code="check-invalid"',
        'class="sd-framebox" data-frame="docs"',
        '<nav class="sd-seg" aria-label="文書">',
        'env.paramLink("doc"',
    ):
        assert marker in scope, marker
    # the plan progress stays only in the summary tab (iss-00589 R-03)
    docs = scope[scope.index("function docsTab(") : scope.index("function artifactsTab(")]
    assert "planProgress(" not in docs and "details.progress" not in docs
    summary = scope[scope.index("function summaryTab(") : scope.index("function depsTab(")]
    assert "planProgress(progress)" in summary and 'data-code="plan-progress"' in scope and "doing_steps" in scope


def test_the_top_band_asks_for_a_restart_only_when_the_server_says_so() -> None:
    topbar = _asset("core/topbar.js")
    assert "if (!server?.restart_required) return null;" in topbar
    assert 'code: "SERVER_RESTART_REQUIRED"' in topbar and '"spec-dock dashboard serve"' in topbar
    app = _asset("app.js")
    assert "setInterval(checkServer, SERVER_MS);" in app and "const SERVER_MS = 60000;" in app
    assert "renderNotices(noticeArea, state.data, state.error, state.server)" in app


def test_the_listing_says_when_a_restart_is_required(env: Env) -> None:
    status_body = env.get("/api/v1/repositories")
    server = json.loads(status_body.body)["server"]
    assert server["restart_required"] is False
    env.http.installed_version = "0.7.0"
    server = json.loads(env.get("/api/v1/repositories").body)["server"]
    assert server == {**server, "version": "0.6.0", "installed_version": "0.7.0", "restart_required": True}


@pytest.mark.usefixtures("real_cue")
def test_a_new_title_or_kind_draws_again(tmp_path: Path) -> None:
    from spec_dock.runtime.application.dashboard_documents import ScopeDocuments

    directory = place_sample(tmp_path / "iss-00002", "issue-strict-complete")
    documents = ScopeDocuments()
    first = documents.drawn(
        scope_id="iss-00002", kind="issue", title="Old", directory=directory, repository_root=tmp_path
    )
    assert (
        documents.drawn(scope_id="iss-00002", kind="issue", title="Old", directory=directory, repository_root=tmp_path)
        is first
    )
    renamed = documents.drawn(
        scope_id="iss-00002", kind="issue", title="New", directory=directory, repository_root=tmp_path
    )
    assert renamed is not first and renamed.html is not None and "iss-00002 New" in renamed.html


def test_a_markdown_page_has_its_title_and_keeps_its_own_front_matter_readable(env: Env) -> None:
    directory = scope_dir(env.catalog, "iss-00003")
    (directory / "requirement.md").write_text('---\n種別: 要件定義書\nID: "iss-00003"\n---\n\n# 要件\n')
    (directory / "report.md").write_text("# 報告\n")
    page = env.get(f"{BASE}/iss-00003/doc/requirement.md").body.decode()
    source = page.split('<script type="text/markdown" id="ds-source">\n', 1)[1]
    assert source.startswith(
        '---\ntitle: "iss-00003 A Markdown Issue"\nlead: "requirement.md"\ncategory: "Markdown の要件"\n---\n'
    )
    assert '```yaml\n種別: 要件定義書\nID: "iss-00003"\n```' in source and source.count("\n---\n") == 1
    report = env.get(f"{BASE}/iss-00003/doc/report.md").body.decode()
    assert 'category: "報告"' in report and "```yaml" not in report


@pytest.mark.usefixtures("real_cue")
def test_adding_and_removing_requirement_md_draws_again(env: Env) -> None:
    directory = place_sample(scope_dir(env.catalog, "iss-00002"), "issue-strict-complete")
    assert env.details("iss-00002")["check"]["status"] == "ok"
    (directory / "requirement.md").write_text("# old\n")
    check = env.details("iss-00002")["check"]
    assert check["status"] == "invalid" and [item["code"] for item in check["errors"]] == ["SCOPE_FORMAT_CONFLICT"]
    (directory / "requirement.md").unlink()
    assert env.details("iss-00002")["check"]["status"] == "ok"
