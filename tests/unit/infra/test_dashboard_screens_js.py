"""The board, detail and overview screens and the search (iss-00531 T-06, T-07).

The static checks always run. The JavaScript unit checks run the pure helpers (`views/_shared/logic.js`) and the
HTML parts (`views/_shared/parts.js`) under node; they are skipped when node is not installed.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
import textwrap

import pytest

ASSETS = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "dashboard"
VIEWS = ASSETS / "views"
SHARED = VIEWS / "_shared"
MINE = ("board", "scope", "overview")
NEW_FILES = (
    "views/_shared/logic.js",
    "views/_shared/parts.js",
    "views/_shared/parts.css",
    "views/_shared/search.js",
    "views/_shared/search.css",
    "views/board.css",
    "views/scope.css",
    "views/overview.css",
)


# --- T-06: static checks -------------------------------------------------------------------------------------


def test_the_three_screens_keep_the_slot_shape_and_use_the_shared_parts() -> None:
    for name in NEW_FILES:
        assert (ASSETS / name).is_file(), name
    for name in MINE:
        source = (VIEWS / f"{name}.js").read_text()
        assert "export default {" in source and f'id: "{name}"' in source
        assert "render," in source or "render(root, ctx)" in source
        assert '"/assets/views/_shared/parts.css"' in source and f'"/assets/views/{name}.css"' in source
        assert 'from "./_shared/parts.js"' in source and 'from "./_shared/logic.js"' in source
        assert "emptySlot" not in source


def test_no_screen_reads_outside_the_server() -> None:
    for path in [*VIEWS.glob("*.js"), *VIEWS.glob("*.css"), *SHARED.glob("*")]:
        if path.stem in ("graph", "timeline", "slot", "index"):
            continue
        text = path.read_text()
        assert not re.search(r"https?://(?!x\")", text), path  # "http://x" is URL() parsing only
        assert "@import" not in text and "cdn" not in text.lower(), path


def test_user_text_is_escaped_before_it_enters_html() -> None:
    # Every interpolation of a Scope's title, reason, id or a file name goes through esc().
    raw = re.compile(r"\$\{(?:[a-z]+\.)?(title|name|text|branch|path)\}")
    for path in [
        *(VIEWS / f"{name}.js" for name in MINE),
        SHARED / "parts.js",
        SHARED / "search.js",
        SHARED / "scope_tabs.js",
        SHARED / "panel.js",
        SHARED / "agents_tab.js",  # iss-00593
    ]:
        for number, line in enumerate(path.read_text().splitlines(), 1):
            assert not raw.search(line), f"{path.name}:{number}: {line.strip()}"


def test_the_shell_only_gains_the_search_line() -> None:
    app = (ASSETS / "app.js").read_text()
    assert app.count("mountSearch") == 2  # the import and the one call
    assert 'import { mountSearch } from "./views/_shared/search.js";' in app
    calls = [line for line in app.splitlines() if "mountSearch(" in line]
    assert len(calls) == 1 and 'top.querySelector("#search-slot")' in calls[0]


def test_the_screen_styles_stay_inside_the_three_screens() -> None:
    for name in ("parts.css",):
        text = (SHARED / name).read_text()
        # iss-00554: the human-task screens share the parts too
        # iss-00587: and the shared Scope panel
        assert (
            ':is([data-view="board"], [data-view="scope"], [data-view="overview"], [data-view="todos"], .sd-pn)' in text
        )
    for name in MINE:
        text = (VIEWS / f"{name}.css").read_text()
        selectors = [line for line in text.splitlines() if line and not line.startswith((" ", "}", "/*", "@"))]
        assert all(line.startswith(f'[data-view="{name}"]') for line in selectors), selectors
    search = (SHARED / "search.css").read_text()
    selectors = [line for line in search.splitlines() if line and not line.startswith((" ", "}", "/*", "@"))]
    assert all(line.startswith(".sd-search") for line in selectors), selectors


# --- T-07: JavaScript unit checks under node -----------------------------------------------------------------

NODE = shutil.which("node")


def _run(script: str, tmp_path: Path) -> dict:
    runner = tmp_path / "check.mjs"
    runner.write_text(
        f"const logic = await import({json.dumps((SHARED / 'logic.js').as_uri())});\n"
        f"const parts = await import({json.dumps((SHARED / 'parts.js').as_uri())});\n"
        "const out = {};\n" + textwrap.dedent(script) + "\nconsole.log(JSON.stringify(out));\n"
    )
    done = subprocess.run([NODE, str(runner)], capture_output=True, text=True, timeout=60)  # type: ignore[list-item]
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout.strip().splitlines()[-1])


pytestmark_node = pytest.mark.skipif(NODE is None, reason="node is not installed")

SCOPES = """
const scopes = [
  {id: "iss-00001", number: 1, kind: "issue", lane: "ready", state: "ready", rank: 3, parent_id: "epic-00009"},
  {id: "iss-00002", number: 2, kind: "issue", lane: "ready", state: "ready", rank: 2, parent_id: "epic-00009"},
  {id: "iss-00003", number: 3, kind: "issue", lane: "awaiting_merge", state: "doing", merge: "needs_fix", rank: 1},
  {id: "iss-00004", number: 4, kind: "issue", lane: "awaiting_merge", state: "doing", merge: "mergeable", rank: 0},
  {id: "iss-00005", number: 5, kind: "issue", lane: "doing", state: "doing", rank: 4, title: "Draft <b>PR</b>"},
  {id: "iss-00006", number: 6, kind: "issue", lane: "blocked", state: "blocked", rank: 5},
  {id: "iss-00007", number: 7, kind: "issue", lane: "unknown", state: "unknown", rank: 6},
  {id: "iss-00008", number: 8, kind: "issue", lane: "done", state: "done", rank: 8, closed_at: "2026-10-01T00:00:00Z"},
  {id: "iss-00010", number: 10, kind: "issue", lane: "done", state: "done", rank: 7, closed_at: "2026-10-05T00:00:00Z"},
  {id: "epic-00009", number: 9, kind: "epic", lane: "ready", state: "ready", rank: 9, title: "Epic nine"},
];
"""


@pytestmark_node
def test_board_columns_follow_lanes_and_rank(tmp_path: Path) -> None:
    out = _run(
        SCOPES
        + """
        const plain = logic.boardColumns(scopes);
        out.lanes = plain.columns.map((c) => c.lane);
        out.ready = plain.columns[1].items.map((s) => s.id);
        const merge = plain.columns[3];
        out.mergeable = merge.mergeable.map((s) => s.id);
        out.needsFix = merge.needsFix.map((s) => s.id);
        out.unknown = plain.unknown.map((s) => s.id);
        const done = logic.boardColumns(scopes, {done: true});
        out.doneLanes = done.columns.map((c) => c.lane);
        out.doneOrder = done.columns[4].items.map((s) => s.id);
        out.epics = logic.boardColumns(scopes, {kind: "epic"}).columns[1].items.map((s) => s.id);
        out.groups = logic.groupByParent(plain.columns[1].items).map((g) => [g.parent, g.items.length]);
        out.counts = logic.boardCounts(scopes);
        """,
        tmp_path,
    )
    assert out["lanes"] == ["blocked", "ready", "doing", "awaiting_merge"]
    assert out["ready"] == ["iss-00002", "iss-00001", "epic-00009"]  # by rank, not by number
    assert out["mergeable"] == ["iss-00004"] and out["needsFix"] == ["iss-00003"]
    assert out["unknown"] == ["iss-00007"]
    assert out["doneLanes"][-1] == "done" and out["doneOrder"] == ["iss-00010", "iss-00008"]  # newest first
    assert out["epics"] == ["epic-00009"]
    assert out["groups"] == [["epic-00009", 2], [None, 1]]
    counts = out["counts"]
    assert (counts["ready"], counts["merge"], counts["mergeable"], counts["needsFix"]) == (2, 2, 1, 1)
    assert counts["done"] == 2 and counts["total"] == 10 and counts["percent"] == 20


@pytestmark_node
def test_query_options_round_trip(tmp_path: Path) -> None:
    out = _run(
        """
        const path = "/r/github.com/o/r/board?embed=1";
        out.a = logic.withParam(path, "kind", "epic");
        out.b = logic.withParam(out.a, "kind", "");
        out.c = logic.withParam(path, "done", true);
        out.d = logic.withParam(out.c, "done", false);
        out.opts = logic.boardOptions(new URLSearchParams("kind=bogus&group=1&done=1"));
        out.leave = logic.withoutEmbed("/r/github.com/o/r/scopes/iss-00001?tab=docs&embed=1");
        """,
        tmp_path,
    )
    assert out["a"] == "/r/github.com/o/r/board?embed=1&kind=epic"
    assert out["b"] == "/r/github.com/o/r/board?embed=1"
    assert out["c"].endswith("done=1") and out["d"] == "/r/github.com/o/r/board?embed=1"
    assert out["opts"] == {"kind": "", "group": True, "done": True}
    assert out["leave"] == "/r/github.com/o/r/scopes/iss-00001?tab=docs"


@pytestmark_node
def test_search_matches_id_number_and_title(tmp_path: Path) -> None:
    out = _run(
        """
        const scopes = [
          {id: "iss-00531", number: 531, title: "Build Dashboard Board", rank: 5},
          {id: "iss-05310", number: 5310, title: "Other", rank: 1},
          {id: "epic-00427", number: 427, title: "Build Html Spec Dashboard", rank: 0},
        ];
        const ids = (q) => logic.searchScopes(scopes, q).map((s) => s.id);
        out.padless = ids("iss-531");
        out.upper = ids("ISS-00531");
        out.number = ids("531");
        out.hash = ids("#427");
        out.title = ids("dashboard");
        out.empty = ids("   ");
        """,
        tmp_path,
    )
    assert out["padless"][0] == "iss-00531" and out["upper"][0] == "iss-00531"
    assert out["number"][0] == "iss-00531"  # the exact number first, then partial ID matches
    assert out["hash"] == ["epic-00427"]
    assert out["title"] == ["epic-00427", "iss-00531"]  # by rank
    assert out["empty"] == []


@pytestmark_node
def test_change_pr_and_warning_words(tmp_path: Path) -> None:
    out = _run(
        """
        out.isNew = logic.changeWords({kinds: ["new"]}, {state: "ready"});
        out.state = logic.changeWords({kinds: ["state", "pr"], state_before: "blocked", pr_before: "draft"}, {state: "ready"});
        out.none = logic.changeWords(null, {});
        out.pr = logic.prWords({number: 9, state: "open", is_draft: false, checks: "failure", mergeable: "conflicting"});
        out.draft = logic.prWords({number: 8, state: "open", is_draft: true, checks: "pending", mergeable: "unknown"});
        out.prUnknown = logic.pullRequestNotice({pull_requests: {status: "unknown"}}).level;
        out.prOk = logic.pullRequestNotice({pull_requests: {status: "ok"}});
        const w = (s, f) => logic.overviewWarnings(s, f).map((x) => [x.level, x.text]);
        out.stale = w({snapshot: {status: "ok", stale: true, age_seconds: 3 * 3600}, notices: [{code: "SNAPSHOT_STALE"}]});
        out.missing = w({snapshot: {status: "missing"}, notices: []});
        out.anomalies = w({snapshot: {status: "ok", stale: false, age_seconds: 60}, anomalies: [{}, {}], notices: []});
        out.failed = w(null, "HTTP 500");
        out.fine = w({snapshot: {status: "ok", stale: false, age_seconds: 60}, notices: [], pull_requests: {status: "ok"}});
        """,
        tmp_path,
    )
    assert out["isNew"] == "新しい"
    assert out["state"] == "状態が変わった（止められている → 着手できる）・PR が変わった（前は下書きの PR）"
    assert out["none"] is None
    assert out["pr"] == "PR #9 開いている・CI 失敗・衝突がある"
    assert out["draft"] == "PR #8 下書き・CI 実行中"
    assert out["prUnknown"] == "unknown" and out["prOk"] is None
    assert out["stale"] == [["warning", "3時間前から更新されていません（定期の同期を確かめてください）。"]]
    assert out["missing"][0][0] == "error" and "ありません" in out["missing"][0][1]
    assert out["anomalies"] == [["warning", "構造の異常が 2件あります。"]]
    assert out["failed"][0][0] == "error" and "HTTP 500" in out["failed"][0][1]
    assert out["fine"] == []


@pytestmark_node
def test_cards_escape_titles_and_link_to_the_detail(tmp_path: Path) -> None:
    out = _run(
        """
        const ctx = {href: (p) => p + "?embed=1", embed: true, route: {path: "/r/github.com/o/r/board?embed=1&kind=epic"}};
        const scope = {id: "iss-00005", number: 5, kind: "issue", state: "doing", title: "<img src=x onerror=alert(1)>",
          reason: {text: "<script>"}, path: "/r/github.com/o/r/scopes/iss-00005", downstream: 2,
          change: {kinds: ["new"]}, pr: {number: 3, state: "open", is_draft: false, checks: "success", mergeable: "mergeable"}};
        out.card = parts.card(scope, ctx);
        out.newtab = parts.newTabLink(ctx);
        out.noTab = parts.newTabLink({...ctx, embed: false});
        out.legend = parts.legend();
        """,
        tmp_path,
    )
    card = out["card"]
    assert "<img" not in card and "&lt;img src=x" in card and "&lt;script&gt;" in card
    assert 'href="/r/github.com/o/r/scopes/iss-00005?embed=1"' in card and "data-nav" in card
    assert "後に続く 2件" in card and "新しい" in card and "CI 成功" in card
    assert 'href="/r/github.com/o/r/board?kind=epic"' in out["newtab"] and 'target="_blank"' in out["newtab"]
    assert out["noTab"] == ""
    for label in ("作業中", "着手できる", "止められている", "不明", "終わった", "後に続く"):
        assert label in out["legend"], label
