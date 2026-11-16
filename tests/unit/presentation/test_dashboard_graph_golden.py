"""The structure graph draws the same HTML after its parts moved to `views/graph/draw.js` (iss-00614 T-04, R-02).

`tests/fixtures/issue614/graph_dom_golden.json` holds a request (synthetic structures and one stored snapshot, the
nest and tree ways, the three ranges, a focus, cleanup candidates, a selection with its path, the state chips and the
agents' rows of marks) and what `views/graph.js` of the start commit 7f7dd2b1d drew for it in
`tests/js/dashboard_graph_golden.mjs`. The current graph.js must draw exactly the same.
iss-00627 wrote the copy again after its routing fixes (router.js D-04, D-05): only the stored structure's "all" run
moved (its lines, and the world 6px wider); every other run is the same as 7f7dd2b1d drew.

To write the copy again from another tree of assets (only when the drawing is meant to change):
    uv run python -m tests.unit.presentation.test_dashboard_graph_golden <dashboard assets dir>
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from tests.support.dashboard import closed, node, snapshot
from tests.support.dashboard_graph import document, document_of, scope_of
from tests.unit.presentation.test_dashboard_graph_js import ASSETS, ROOT, SNAPSHOT, _node

HARNESS = ROOT / "tests" / "js" / "dashboard_graph_golden.mjs"
GOLDEN = ROOT / "tests" / "fixtures" / "issue614" / "graph_dom_golden.json"
V3 = "specdock.graph.v3"


def _small() -> Any:
    return snapshot(
        node(1, "initiative"),
        node(2, "epic", parent=1),
        node(3, "issue", parent=2),
        node(4, "issue", parent=2, blocked_by=(3,)),
        closed(5, "issue", parent=2),
        node(6, "issue", parent=2, blocked_by=(4,), in_progress=True),
        closed(7, "epic", parent=1),  # closed with an open child: the child is a cleanup candidate
        node(8, "issue", parent=7),
        node(9, "epic"),  # open with every child closed: a cleanup candidate
        closed(10, "issue", parent=9),
        closed(11, "issue", parent=9),
        node(12, "epic"),
        node(13, "issue", parent=12, blocked_by=(4,)),
        node(14, "issue", parent=12),
        node(15, "issue", parent=12, blocked_by=(14, 13)),
        node(16, "issue"),
        closed(17, "issue", blocked_by=(16,)),
        node(18, "issue", blocked_by=(16,)),
    )


def _range_steps() -> list[dict[str, Any]]:
    return [{"act": "range", "range": r} for r in ("all", "now", "next")]


def request() -> dict[str, Any]:
    small = _small()
    doc = document(small)
    scope_docs = {s["id"]: scope_of(small, s["id"]) for s in doc["scopes"]}
    stored = document_of(json.loads(SNAPSHOT.read_text(encoding="utf-8")))
    box = '.gx-world .gx-box[data-id="{}"]'
    head = '.gx-world .gx-fh[data-id="{}"]'
    runs: list[dict[str, Any]] = [
        {
            "name": "nest",
            "doc": "small",
            "saved": None,
            "steps": [
                *_range_steps(),
                {"act": "range", "range": "all"},
                {"hl": "ready"},
                {"hl": "blocked"},
                {"hl": "blocked"},
                {"tap": box.format("iss-00004")},
                {"tap": head.format("epic-00012")},
                {"tap": box.format("iss-00015")},
                {"click": '[data-pn-act="close"]'},
                {"act": "range", "range": "now"},
                {"tap": ".gx-world .gx-clean"},
                {"act": "close"},
                {"act": "legend"},
                {"act": "zin"},
                {"act": "mode"},
            ],
        },
        {
            "name": "tree",
            "doc": "small",
            "saved": {V3: json.dumps({"mode": "tree", "range": "all", "legend": True})},
            "steps": [*_range_steps(), {"tap": box.format("iss-00013")}, {"hl": "doing"}],
        },
        {"name": "focus", "doc": "small", "saved": None, "focus": "epic-00002", "steps": _range_steps()},
        {
            "name": "focus-tree",
            "doc": "small",
            "saved": {V3: json.dumps({"mode": "tree", "range": "next"})},
            "focus": "init-00001",
        },
        {
            "name": "marks",
            "doc": "small",
            "saved": {V3: json.dumps({"mode": "nest", "range": "all"})},
            # agents on a box (three rows), a frame heading and one short one
            "orca": {"iss-00004": [70, 80, 90, 60, 75], "epic-00002": [120, 140, 160], "iss-00016": [40]},
            "steps": [{"news": True}, {"act": "range", "range": "next"}, {"act": "mode"}],
        },
        {"name": "stored", "doc": "stored", "saved": None, "steps": _range_steps()},
        {"name": "empty", "doc": "empty", "saved": None},
        {"name": "unread", "doc": None, "saved": None},
        {"name": "done", "doc": "done", "saved": None, "steps": [{"act": "range", "range": "next"}]},
    ]
    docs = {
        "small": doc,
        "stored": stored,
        "empty": document(snapshot()),
        "done": document(snapshot(closed(1, "epic"), closed(2, "issue", parent=1))),
    }
    return {"docs": docs, "scopes": {"small": scope_docs}, "runs": runs}


def draw(assets: Path, req: dict[str, Any], tmp: Path) -> dict[str, Any]:
    path = tmp / "request.json"
    path.write_text(json.dumps(req), encoding="utf-8")
    result = subprocess.run(
        [_node(), str(HARNESS), str(assets), str(path)], capture_output=True, text=True, timeout=600, check=False
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)["runs"]


def test_the_graph_draws_what_the_start_commit_drew(tmp_path: Path) -> None:
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    assert golden["commit"] == "7f7dd2b1d"
    got = draw(ASSETS, golden["request"], tmp_path)
    assert set(got) == set(golden["runs"])
    for name, shots in golden["runs"].items():
        assert len(got[name]) == len(shots), name
        for i, (a, b) in enumerate(zip(got[name], shots, strict=True)):
            for part in b:
                assert a[part] == b[part], f"{name} step {i} {part}"


def test_the_copy_covers_what_r02_names() -> None:
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    shots = [s for run in golden["runs"].values() for s in run]
    worlds = "".join(s["world"] for s in shots)
    assert {s["data"]["mode"] for s in shots} >= {"nest", "tree"}
    assert {s["data"]["range"] for s in shots} >= {"all", "now", "next"}
    assert 'class="gx-clean"' in worlds and 'class="cln"' in worlds  # the folded group and the candidates' marks
    assert any("is-sel" in c for s in shots for c in s["classes"].values())  # a selection
    assert any("is-root" in c or "is-poff" in c for s in shots for c in s["classes"].values())  # its path
    assert any("is-hl" in c for s in shots for c in s["classes"].values())  # a state chip
    assert any(not s["crumbs"]["hidden"] for s in shots)  # a focus
    assert 'class="orca-mark"' in worlds  # the agents' marks
    # the rows of agents changed the layout: the marks run differs from the plain nest run in the world's size
    marks = golden["runs"]["marks"]
    assert marks[0]["size"] != golden["runs"]["nest"][1]["size"]
    assert any(not s["empty"]["hidden"] for s in shots) and any(not s["none"]["hidden"] for s in shots)


if __name__ == "__main__":  # write the copy from the given assets
    import tempfile

    assets = Path(sys.argv[1]).resolve()
    req = request()
    with tempfile.TemporaryDirectory() as tmp:
        runs = draw(assets, req, Path(tmp))
    GOLDEN.parent.mkdir(parents=True, exist_ok=True)
    GOLDEN.write_text(
        json.dumps({"commit": "7f7dd2b1d", "request": req, "runs": runs}, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(GOLDEN, GOLDEN.stat().st_size)
