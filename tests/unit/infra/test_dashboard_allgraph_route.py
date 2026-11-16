"""The cross-repository structure's path, tabs, title and shell route (iss-00614 T-03, R-01).

The routes (`core/route.js`) and the top band (`core/topbar.js`) run under node; the title and the shell's links
are read from `app.js`; the server's shell route goes through `DashboardHttp`; the contract is the shipped
`reference_cli.md`.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import textwrap

import pytest

from tests.unit.application.test_dashboard_todos import Env
from tests.unit.infra.test_dashboard_todos_js import _node

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "src" / "spec_dock" / "assets" / "dashboard"
REFERENCE = ROOT / "src" / "spec_dock" / "assets" / "spec_dock" / "docs" / "reference_cli.md"
TITLE = "横断の構造 · すべてのリポジトリ · SpecDock"


def _run(script: str, tmp_path: Path) -> dict:
    runner = tmp_path / "check.mjs"
    runner.write_text(
        "globalThis.location = new URL('http://127.0.0.1:47800/');\n"
        "globalThis.document = {addEventListener() {}, getElementById() { return null; }};\n"
        f"const route = await import({json.dumps((ASSETS / 'core' / 'route.js').as_uri())});\n"
        f"const topbar = await import({json.dumps((ASSETS / 'core' / 'topbar.js').as_uri())});\n"
        "const out = {};\n" + textwrap.dedent(script) + "\nconsole.log(JSON.stringify(out));\n"
    )
    done = subprocess.run([_node(), str(runner)], capture_output=True, text=True, timeout=60, check=False)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout.strip().splitlines()[-1])


TOP = """
const band = (path) => {
  const target = {innerHTML: "", querySelector: () => ({addEventListener() {}, setAttribute() {}})};
  const mobile = {innerHTML: "", hidden: true};
  topbar.renderTop(target, mobile, {route: route.parseRoute("http://127.0.0.1:47800" + path), repositories: [], data: null});
  const tabs = [...mobile.innerHTML.matchAll(/<a class="tab"[^>]*href="([^"]*)" aria-selected="(true|false)">.*?<span>([^<]*)<\\/span><\\/a>/g)];
  return {tabs: tabs.map((m) => [m[3], m[1].replaceAll("&amp;", "&"), m[2]]), same: target.innerHTML.includes(mobile.innerHTML)};
};
"""


def test_the_path_reads_as_the_cross_repository_structure(tmp_path: Path) -> None:
    out = _run(
        """
        const r = (path) => { const x = route.parseRoute("http://127.0.0.1:47800" + path); return [x.view, x.repository, x.scope, x.todo, x.embed]; };
        out.graph = r("/graph");
        out.slash = r("/graph/");
        out.embed = r("/graph?embed=1");
        out.deeper = r("/graph/x");
        out.todos = r("/todos");
        out.repo = r("/r/github.com/o/r/graph");
        out.path = route.allGraphPath;
        """,
        tmp_path,
    )
    assert out["graph"] == ["allgraph", None, None, None, False]
    assert out["slash"] == ["allgraph", None, None, None, False]
    assert out["embed"] == ["allgraph", None, None, None, True]
    assert out["deeper"] == ["overview", None, None, None, False]
    assert out["todos"] == ["todos", None, None, None, False]
    assert out["repo"] == ["graph", "github.com/o/r", None, None, False]
    assert out["path"] == "/graph"


def test_the_tabs_without_a_repository_are_three_and_keep_embed(tmp_path: Path) -> None:
    out = _run(
        TOP
        + """
        for (const p of ["/", "/todos", "/graph", "/graph?embed=1", "/todos?embed=1", "/r/github.com/o/r/"]) out[p] = band(p);
        """,
        tmp_path,
    )
    names = ["横断の概況", "横断の構造", "人のタスク"]
    for path, selected in (("/", "横断の概況"), ("/todos", "人のタスク"), ("/graph", "横断の構造")):
        tabs = out[path]["tabs"]
        assert [t[0] for t in tabs] == names, path
        assert [t[1] for t in tabs] == ["/", "/graph", "/todos"], path
        assert [t[0] for t in tabs if t[2] == "true"] == [selected], path
        assert out[path]["same"]
    for path in ("/graph?embed=1", "/todos?embed=1"):
        assert [t[1] for t in out[path]["tabs"]] == ["/?embed=1", "/graph?embed=1", "/todos?embed=1"], path
    # a repository's screens keep their four tabs
    assert [t[0] for t in out["/r/github.com/o/r/"]["tabs"]] == ["構造の図", "ボード", "時間の軸", "人のタスク"]


def test_the_shell_knows_the_screen_its_title_and_its_links() -> None:
    topbar = (ASSETS / "core" / "topbar.js").read_text()
    assert '["allgraph", "/graph", "横断の構造", "layers"],' in topbar
    index = (ASSETS / "views" / "index.js").read_text()
    assert 'import allgraph from "./allgraph.js";' in index
    assert re.search(r"export const VIEWS = \{[^}]*\ballgraph\b[^}]*\};", index)
    app = (ASSETS / "app.js").read_text()
    assert f'if (!repo && state.route.view === "allgraph") return "{TITLE}";' in app
    screen = re.search(r"const screen = (.*);\n", app)
    assert screen and 'url.pathname === "/graph"' in screen.group(1)
    allgraph = (ASSETS / "views" / "allgraph.js").read_text()
    assert "export default {" in allgraph and 'id: "allgraph"' in allgraph
    route = (ASSETS / "core" / "route.js").read_text()
    assert 'export const allGraphPath = "/graph";' in route


@pytest.mark.parametrize("path", ["/graph", "/graph/", "/graph?embed=1"])
def test_the_server_returns_the_shell_for_the_path(path: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env = Env(tmp_path, monkeypatch)
    response = env.get(path)
    assert response.status == 200 and response.header("content-type").startswith("text/html")
    assert b'id="view"' in response.body


@pytest.mark.parametrize("path", ["/graph/x", "/graph/x/"])
def test_a_deeper_path_is_not_found(path: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env = Env(tmp_path, monkeypatch)
    assert env.get(path).status == 404


def test_the_contract_names_the_screen_paths() -> None:
    line = next(x for x in REFERENCE.read_text().splitlines() if x.startswith("- **画面の道**"))
    assert "`/graph`（横断の構造）" in line
    assert "`/todos`（人のタスク）" in line
