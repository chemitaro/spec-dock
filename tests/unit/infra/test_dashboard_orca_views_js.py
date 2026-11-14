"""orca-web marks in the structure graph, the board and the shared panel (iss-00592 T-03, T-04).

The node checks run the HTML parts and the small DOM helpers; the rest are static markers on the screens'
sources, which need a browser to run.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
import textwrap

import pytest

DASHBOARD = Path(__file__).resolve().parents[3] / "src/spec_dock/assets/dashboard"
VIEWS = DASHBOARD / "views"
SHARED = VIEWS / "_shared"
NODE = shutil.which("node")
needs_node = pytest.mark.skipif(NODE is None, reason="node is not installed")


def run_node(script: str, tmp_path: Path) -> dict:
    runner = tmp_path / "check.mjs"
    runner.write_text(
        'import assert from "node:assert/strict";\n'
        + f"const parts = await import({json.dumps((SHARED / 'parts.js').as_uri())});\n"
        + f"const marks = await import({json.dumps((SHARED / 'orca_marks.js').as_uri())});\n"
        + "const out = {};\n"
        + textwrap.dedent(script)
        + "\nconsole.log(JSON.stringify(out));\n"
    )
    done = subprocess.run([NODE, str(runner)], capture_output=True, text=True, timeout=30)  # type: ignore[list-item]
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout.strip().splitlines()[-1])


def _function(source: str, name: str) -> str:
    start = source.index(f"function {name}(")
    end = source.index("\n}\n", start)
    return source[start:end]


# --- T-03: the slots in the graph and the board -------------------------------------------------------------


@needs_node
def test_the_slot_depends_only_on_the_scope_id_and_max(tmp_path: Path) -> None:
    out = run_node(
        """
        out.slot = parts.orcaSlot('iss-1"<x>', 2);
        out.again = parts.orcaSlot('iss-1"<x>', 2);
        """,
        tmp_path,
    )
    assert out["slot"] == '<span class="sd-orca" data-orca-scope="iss-1&quot;&lt;x&gt;" data-orca-max="2"></span>'
    assert out["again"] == out["slot"]


@needs_node
def test_the_card_holds_a_slot_only_when_asked(tmp_path: Path) -> None:
    out = run_node(
        """
        const ctx = {href: (p) => p, data: {scopes: []}};
        const bare = {id: "iss-00005", number: 5, kind: "issue", state: "doing", title: "t", path: "/p"};
        const marked = {...bare, downstream: 2};
        out.plain = parts.card(bare, ctx);
        out.plainOpts = parts.card(bare, ctx, {});
        out.orca = parts.card(bare, ctx, {orca: true});
        out.orcaMarks = parts.card(marked, ctx, {orca: true});
        out.marks = parts.card(marked, ctx);
        """,
        tmp_path,
    )
    slot = '<span class="sd-orca" data-orca-scope="iss-00005" data-orca-max="4"></span>'
    assert out["plain"] == out["plainOpts"]
    assert "sd-card__meta" not in out["plain"] and "sd-orca" not in out["plain"]
    assert f'<span class="sd-card__meta">{slot}</span>' in out["orca"]
    assert out["orcaMarks"].count("sd-card__meta") == 1
    assert f"{slot}</span>" in out["orcaMarks"]
    assert "sd-orca" not in out["marks"]


def test_graph_boxes_and_frames_end_their_rows_with_a_slot() -> None:
    source = (VIEWS / "graph.js").read_text()
    box = _function(source, "boxHtml")
    assert box.count('<div class="gx-marks">') == 2
    assert box.count("${orcaSlot(s.id, 2)}</div>`") == 2
    frame = _function(source, "frameHtml")
    assert "${orcaSlot(s.id, 3)}</div>`" in frame
    head = frame[frame.index("const head") : frame.index("const meta")]
    assert head.rstrip().endswith("${orcaSlot(s.id, 3)}</div>`;")


def test_the_box_size_does_not_change() -> None:
    layout = (VIEWS / "graph/layout.js").read_text()
    start = layout.index("export const SIZE = {")
    block = layout[start : layout.index("};", start)]
    for value in ("boxW: 178,", "boxH: 88,", "treeFrameW: 236,", "compactW: 236,", "head: 46,"):
        assert value in block, block


def test_graph_and_board_paint_after_drawing_and_on_news() -> None:
    graph = (VIEWS / "graph.js").read_text()
    render = _function(graph, "render")
    assert render.rstrip().endswith("paintOrca();")
    assert "orcaWatch.follow(ctx.orca)" in render
    paint = _function(graph, "paintOrca")
    assert "paintOrcaMarks(V.el.world, V.ctx, V.data)" in paint and "V.pn?.refreshOrca()" in paint
    assert "orcaWatch.stop()" in _function(graph, "dispose")

    board = (VIEWS / "board.js").read_text()
    render = _function(board, "render")
    assert render.index("renderPage(B.page, ctx)") < render.index("paintOrca()")
    assert "orcaWatch.follow(ctx.orca)" in render
    paint = _function(board, "paintOrca")
    assert "paintOrcaMarks(B.page, B.ctx, B.ctx.data)" in paint and "B.pn?.refreshOrca()" in paint
    assert "orcaWatch.stop()" in _function(board, "unmount")
    assert "card(item, ctx, { orca: true })" in board
    assert "card(item, ctx)" not in board


def test_pressing_a_mark_prefers_the_agents_tab() -> None:
    graph = (VIEWS / "graph.js").read_text()
    # A box's mark is pressed through the graph's taps; the panel takes the presses on its own heading's marks.
    tap = _function(graph, "onTap")
    assert 'closest(".sd-orca")' in tap and 'V.pn?.preferTab("agents")' in tap
    assert tap.index("select(id)") < tap.index("preferTab")
    board = _function((VIEWS / "board.js").read_text(), "onCardClick")
    assert 'closest(".sd-orca")' in board and 'B.pn?.preferTab("agents")' in board
    assert board.index("plainClick(event)") < board.index("preferTab")


@needs_node
def test_the_watch_follows_one_reader_at_a_time(tmp_path: Path) -> None:
    out = run_node(
        """
        const log = [];
        const reader = (name) => ({subscribe(fn) {log.push(`on ${name}`); return () => log.push(`off ${name}`);}});
        const a = reader("a"), b = reader("b");
        let calls = 0;
        const watch = marks.createOrcaWatch(() => calls++);
        watch.follow(a); watch.follow(a); watch.follow(b); watch.follow(null); watch.follow(b); watch.stop(); watch.stop();
        out.log = log;
        """,
        tmp_path,
    )
    assert out["log"] == ["on a", "off a", "on b", "off b", "on b", "off b"]


def test_slot_styles_stay_shared_and_leave_the_marks_to_orca_web() -> None:
    parts = (SHARED / "parts.css").read_text()
    assert "& .sd-card__meta:not(:has(> :not(.sd-orca:empty))) { display: none; }" in parts
    for path in [*DASHBOARD.glob("*.css"), *VIEWS.glob("*.css"), *SHARED.glob("*.css")]:
        text = path.read_text()
        assert ".orca-mark" not in text, path
        assert not re.search(r"\.orca-[a-z-]+\s*[{,]", text), path
    panel = (SHARED / "panel.js").read_text()
    assert "data-width" not in panel and "dataset.width" not in panel
