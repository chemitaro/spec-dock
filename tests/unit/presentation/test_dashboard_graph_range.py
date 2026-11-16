"""The structure graph's range of what is shown: all, now and next (iss-00603), run in node like the other graph checks.

"all" and "now" are the two combinations before iss-00603 ({showDone: true, fold: false} and the default
{showDone: false, fold: true}); their layouts are compared with digests recorded at the start commit 16f0cf122
(`tests/fixtures/issue603/layout-before.json`). "next" leaves out what is done and the cleanup candidates.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from tests.support.dashboard import closed, node, snapshot
from tests.support.dashboard_graph import document, document_of, generated
from tests.unit.presentation.test_dashboard_graph_js import AUDIT_KEYS, SNAPSHOT, _context, _run, _small

BEFORE = Path(__file__).resolve().parents[2] / "fixtures" / "issue603" / "layout-before.json"
# the combinations before iss-00603 that "all" and "now" stand for
OLD = {"all": {"showDone": True, "fold": False}, "now": {}}


def documents() -> dict[str, dict[str, Any]]:
    return {
        "small": _small(),
        "context": _context(),
        "spec-dock": document_of(json.loads(SNAPSHOT.read_text(encoding="utf-8"))),
        "generated": document(generated()),
    }


def cases() -> dict[str, dict[str, Any]]:
    """The ways of showing compared with the start commit, without the range."""
    out: dict[str, dict[str, Any]] = {}
    for deps in ("all", "wait"):
        out[f"tree|{deps}"] = {"mode": "tree", "deps": deps}
        for width in (None, 374):
            out[f"nest|{deps}|{width}"] = {"mode": "nest", "deps": deps, **({"width": width} if width else {})}
    return out


def digest(entry: dict[str, Any]) -> str:
    kept = {key: entry[key] for key in ("nodes", "groups", "edges", "trunks", "wraps")}
    return hashlib.sha256(json.dumps(kept, sort_keys=True).encode("utf-8")).hexdigest()


def request_before() -> dict[str, Any]:
    """The request that recorded the digests at the start commit (`python -m` this module's `record`)."""
    layouts = {
        f"{rng}|{key}|{how}": {**opts, **OLD[rng]}
        for rng in OLD
        for key, opts in cases().items()
        for how in ("plain", "routed")
    }
    docs = documents()
    return {
        "documents": docs,
        "layouts": dict.fromkeys(docs, layouts),
        "routed": {name: [key for key in layouts if key.endswith("|routed")] for name in docs},
        "checks": ["layout"],
    }


# What the range alone, a missing range and a range with stale showDone and fold of the old callers must equal.
VARIANTS: dict[str, list[dict[str, Any]]] = {
    "all": [{"range": "all"}, {"range": "all", "showDone": False, "fold": True}],
    "now": [{"range": "now"}, {}, {"range": "now", "showDone": True, "fold": False}, {"range": "later"}],
}


@pytest.fixture(scope="module")
def same(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    layouts = {}
    for rng, variants in VARIANTS.items():
        for v, extra in enumerate(variants):
            for key, opts in cases().items():
                for how in ("plain", "routed"):
                    layouts[f"{rng}|{key}|{how}|{v}"] = {**opts, **extra}
    docs = documents()
    result = _run(
        tmp_path_factory.mktemp("range-same"),
        {
            "documents": docs,
            "layouts": dict.fromkeys(docs, layouts),
            "routed": {name: [key for key in layouts if "|routed|" in key] for name in docs},
            "checks": ["layout"],
        },
    )
    return result["layout"]


def test_all_and_now_lay_out_as_the_two_old_combinations(same: dict[str, Any]) -> None:
    """T-01, T-02: range all = {showDone: true, fold: false}, range now (and no range) = the old default."""
    before = json.loads(BEFORE.read_text(encoding="utf-8"))["digests"]
    differ = []
    for name, result in same.items():
        for key, entry in result.items():
            rng, rest = key.split("|", 1)
            case, how, _variant = rest.rsplit("|", 2)
            want = before[f"{name}|{rng}|{case}|{how}"]
            if digest(entry) != want:
                differ.append(f"{name}|{key}")
    assert len(same) == 4 and all(len(r) == len(cases()) * 2 * 6 for r in same.values())
    assert differ == []


# --- next: what goes on, without what is done and the cleanup candidates --------------------------------------


def _next() -> dict[str, Any]:
    return document(
        snapshot(
            node(1, "epic"),  # open, with an open and a done child
            node(2, "issue", parent=1),
            closed(3, "issue", parent=1),  # done inside an open parent: grey in now, gone in next
            node(4, "issue", parent=1, blocked_by=(3,)),  # waits for a done one: no line in next
            node(5, "issue", parent=1, blocked_by=(2,)),  # waits for an open one: a line
            node(10, "epic"),  # a: open, every child done
            closed(11, "issue", parent=10),
            closed(12, "issue", parent=10),
            closed(20, "epic", blocked_by=(61,)),  # b with a doing descendant: a frame only
            node(21, "issue", parent=20, in_progress=True),
            node(22, "issue", parent=20),  # c (blocked by its closed parent): not shown
            closed(30, "epic"),  # b holding only a candidate: not shown
            node(31, "issue", parent=30),  # c
            node(40, "epic", blocked_by=(20,)),  # waits for the done frame 20: no line in next
            node(41, "issue", parent=40),
            closed(50, "epic"),  # done with nothing open
            closed(51, "issue", parent=50),
            node(60, "epic"),
            node(61, "issue", parent=60),
        )
    )


SHOWN = {
    "epic-00001",
    "iss-00002",
    "iss-00004",
    "iss-00005",
    "epic-00020",
    "iss-00021",
    "epic-00040",
    "iss-00041",
    "epic-00060",
    "iss-00061",
}
FOCUS = {
    "epic-00010": {"epic-00010"},
    "epic-00020": {"epic-00020", "iss-00021"},
    "epic-00030": {"epic-00030"},
    "epic-00050": {"epic-00050"},
    "iss-00022": {"iss-00022"},
    "iss-00003": {"iss-00003"},
}


@pytest.fixture(scope="module")
def nxt(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    doc = _next()
    layouts: dict[str, dict[str, Any]] = {}
    for mode in ("nest", "tree"):
        for deps in ("all", "wait", "none"):
            for rng in ("all", "now", "next"):
                layouts[f"{mode}|{deps}|{rng}"] = {"mode": mode, "deps": deps, "range": rng}
        for focus in FOCUS:
            layouts[f"{mode}|focus|{focus}"] = {"mode": mode, "range": "next", "focus": focus}
    return {
        "doc": doc,
        **_run(
            tmp_path_factory.mktemp("range-next"),
            {"documents": {"next": doc}, "layouts": {"next": layouts}, "checks": ["layout", "audit"]},
        ),
    }


def _shown(nxt: dict[str, Any], key: str) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in nxt["layout"]["next"][key]["nodes"]}


def _pairs(nxt: dict[str, Any], key: str) -> set[tuple[str, str]]:
    return {(p[0], p[1]) for e in nxt["layout"]["next"][key]["edges"] for p in e["pairs"]}


@pytest.mark.parametrize("mode", ["nest", "tree"])
def test_next_leaves_out_done_scopes_and_cleanup_candidates(nxt: dict[str, Any], mode: str) -> None:
    """T-03: no done box, no candidate box; a and b holding only candidates are gone, b with a doing child a frame."""
    shown = _shown(nxt, f"{mode}|all|next")
    assert set(shown) == SHOWN
    assert shown["epic-00020"]["type"] == ("frame" if mode == "nest" else "tframe")
    assert nxt["layout"]["next"][f"{mode}|all|next"]["groups"] == []
    states = {s["id"]: s["state"] for s in nxt["doc"]["scopes"]}
    candidates = {c["id"] for c in nxt["doc"]["cleanup"]}
    kids = {s["parent_id"] for s in nxt["doc"]["scopes"] if s.get("parent_id")}
    for scope_id in shown:
        if scope_id not in kids:  # a box
            assert states[scope_id] != "done" and scope_id not in candidates, scope_id
    # the same structure in all and now still shows them (the range is what leaves them out)
    assert {"iss-00003", "epic-00010", "iss-00022"} <= set(_shown(nxt, f"{mode}|all|all"))
    assert "iss-00003" in _shown(nxt, f"{mode}|all|now")


@pytest.mark.parametrize("mode", ["nest", "tree"])
def test_next_draws_no_line_from_or_to_a_done_scope(nxt: dict[str, Any], mode: str) -> None:
    """T-04: whatever the line choice, a pair with a done end is not drawn; none draws nothing."""
    done = {s["id"] for s in nxt["doc"]["scopes"] if s["state"] == "done"}
    for deps in ("all", "wait"):
        pairs = _pairs(nxt, f"{mode}|{deps}|next")
        assert ("iss-00002", "iss-00005") in pairs, deps
        assert not {item for pair in pairs for item in pair} & done, deps
    # the frame 20 is shown and its dependencies are open ones: drawn in all, left out in next
    assert {("iss-00061", "epic-00020"), ("epic-00020", "epic-00040")} <= _pairs(nxt, f"{mode}|all|all")
    assert nxt["layout"]["next"][f"{mode}|none|next"]["edges"] == []


@pytest.mark.parametrize("mode", ["nest", "tree"])
@pytest.mark.parametrize("focus", sorted(FOCUS))
def test_next_shows_the_focus_but_not_what_is_done_inside(nxt: dict[str, Any], mode: str, focus: str) -> None:
    """T-05: a done or candidate focus shows (a frame, or a box without children); its done and candidate insides do not."""
    shown = _shown(nxt, f"{mode}|focus|{focus}")
    assert set(shown) == FOCUS[focus]
    assert nxt["layout"]["next"][f"{mode}|focus|{focus}"]["focus"] == focus
    assert nxt["layout"]["next"][f"{mode}|focus|{focus}"]["groups"] == []


def test_next_routes_cleanly(nxt: dict[str, Any]) -> None:
    """T-07 (the synthetic structure): every combination of the node check, next among them, has no audit problem."""
    runs = nxt["audit"]
    assert any(run["opts"].get("range") == "next" for run in runs)
    assert [run for run in runs if any(run[key] for key in AUDIT_KEYS)] == []


def record(out: Path) -> None:
    """Record the digests at the start commit (run there once: `python -c 'from ... import record; record(...)'`)."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        result = _run(Path(tmp), request_before())["layout"]
    digests = {f"{name}|{key}": digest(entry) for name, res in result.items() for key, entry in res.items()}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps({"commit": "16f0cf122cb2053f4f4e24cf844f505f5274c30d", "digests": digests}, indent=1, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
