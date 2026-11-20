"""The Unscoped row's items (iss-00668 T-02), run in node like the other graph checks.

`views/graph/unscoped.js` turns the structure API's git worktree list (`worktrees.items`), orca-web's summary, the
command pairs and their places into the items of one repository's row: the main checkout (`Primary`) first, the
worktrees linked to no Scope (`Unlinked`), the ends of the command lines that fall in the row, and `+N` for the idle
Unlinked worktrees. Every value is synthetic: no real path, address or session id.
"""

from __future__ import annotations

import copy
import json
import subprocess
from typing import TYPE_CHECKING, Any

import pytest

from tests.unit.presentation.test_dashboard_graph_command import OTHER, ag, structure, summary, wt
from tests.unit.presentation.test_dashboard_graph_js import ASSETS, ROOT, _node

if TYPE_CHECKING:
    from pathlib import Path

CHECK = ROOT / "tests" / "js" / "dashboard_graph_unscoped.mjs"


def _run(tmp_path: Path, request: dict[str, Any]) -> dict[str, Any]:
    path = tmp_path / "request.json"
    path.write_text(json.dumps(request), encoding="utf-8")
    result = subprocess.run(
        [_node(), str(CHECK), str(ASSETS), str(path)], capture_output=True, text=True, timeout=600, check=False
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def row(path: str, branch: str | None, *, main: bool = False, head: str = "0123456789abcdef") -> dict[str, Any]:
    return {"path": path, "branch": branch, "head": head, "main": main, "detached": branch is None, "locked": False}


def git(*rows: dict[str, Any], status: str = "ok") -> dict[str, Any]:
    """The small structure with its Scope records and the git list of the main checkout, the records and `rows`."""
    doc = structure(status=status)
    doc["worktrees"]["items"] = [
        row("/w/r", "main", main=True),
        *(row(p, p.rsplit("/", 1)[-1]) for p in ("/w/r-21", "/w/r-22")),
        *rows,
    ]
    doc["worktrees"]["paths"] = [*doc["worktrees"]["paths"], *(r["path"] for r in rows)]
    return doc


MAIN = wt("wt-main", "/w/r", "main", [ag("a-coord")], main=True)

CASES: dict[str, dict[str, Any]] = {
    # R-02, F-02: no summary, no pair: the main checkout alone
    "bare": {"structure": git(), "summary": None},
    # R-02: no command line; the coordinator in the main checkout
    "idle-coord": {"structure": git(), "summary": summary(MAIN)},
    # R-03, R-04, F-04: two Unlinked worktrees with agents (one with a trailing /), one idle, a Scope's worktree not shown
    "unlinked": {
        "structure": git(row("/w/u-b", "topic-b"), row("/w/u-a/", "topic-a"), row("/w/old-1", "old-1")),
        "summary": summary(
            MAIN,
            wt("wt-21", "/w/r-21", "iss-00021", [ag("a-21")]),
            wt("wt-b", "/w/u-b", "topic-b", [ag("b-1"), ag("b-2", "waiting")]),
            wt("wt-a", "/w/u-a", "topic-a", [ag("a-1")]),
        ),
    },
    # R-04: three idle Unlinked worktrees (one detached) fold into one +N
    "fold": {
        "structure": git(
            row("/w/old-2", "old-2"), row("/w/old-1", "old-1"), row("/w/d", None, head="abcdef0123456789")
        ),
        "summary": summary(MAIN),
    },
    # R-09: every agent of one worktree in one item, in orderOf's order (also the agents of no command line)
    "order": {
        "structure": git(row("/w/u", "topic")),
        "summary": summary(MAIN, wt("wt-u", "/w/u", "topic", [ag(f"x{i}") for i in range(1, 6)])),
        "order": {"wt-u": ["x5", "x3", "x1", "x2", "x4"]},
    },
    # F-04: two worktrees of the summary with one path; the second one's end moves to the first one's item
    "merge": {
        "structure": git(row("/w/u", "topic")),
        "summary": summary(
            MAIN,
            wt("wt-u1", "/w/u", "topic", [ag("u-1", parent="a-coord")]),
            wt("wt-u2", "/w/u/", "topic", [ag("u-2", parent="u-1")]),
        ),
    },
    # R-03: the ends in no item of git stay as today's items: an orca-only worktree of this project, another repository
    "ends": {
        "structure": git(row("/w/u", "topic")),
        "summary": summary(
            MAIN,
            wt("wt-u", "/w/u", "topic", [ag("u-1", parent="a-coord")]),
            wt("wt-z", "/w/r-z", "zeta", [ag("z-1", parent="a-coord")]),
            wt("wt-o", "/x/other", "main", [ag("o-1", parent="a-coord")], project=OTHER, main=True),
        ),
    },
    # iss-00676 R-02: the same items in every range; idle and non-commanding Unlinked worktrees, no count
    **{
        name: {
            "range": rng,
            "structure": git(row("/w/u1", "u1"), row("/w/u2", "u2"), row("/w/u3", "u3"), row("/w/u4", "u4")),
            "summary": summary(
                wt("wt-main", "/w/r", "main", [ag("a-coord")], main=True),
                wt("wt-21", "/w/r-21", "iss-00021", [ag("a-21", parent="a-coord")]),
                wt(
                    "wt-u1",
                    "/w/u1",
                    "u1",
                    [
                        ag("a-1", parent="a-coord"),
                        ag("a-3", parent="a-1", agentType="codex"),
                        ag("a-4", parent="a-1"),
                        ag("a-5", parent="a-3"),
                    ],
                ),
                wt("wt-u2", "/w/u2", "u2", [ag("a-u2")]),
            ),
        }
        for name, rng in (("next", "next"), ("all", "all"), ("now", "now"))
    },
    # F-03: no main row (the first row was bare and left out by the server): no Primary
    "no-main": {
        "structure": git(row("/w/u", "topic")),
        "summary": summary(MAIN),
    },
    # iss-00676 R-02: "next" keeps the Unlinked worktree whose agent directs nobody
    "next-idle": {
        "range": "next",
        "structure": git(row("/w/u", "topic")),
        "summary": summary(MAIN, wt("wt-u", "/w/u", "topic", [ag("u-1")])),
    },
}
_no_main = copy.deepcopy(CASES["no-main"]["structure"])
_no_main["worktrees"]["items"] = [r for r in _no_main["worktrees"]["items"] if not r["main"]]
CASES["no-main"]["structure"] = _no_main
# F-01: no git list in the structure (an old server): today's band items, the main one marked Primary
_old = structure()
CASES["old"] = {
    "structure": _old,
    "summary": summary(MAIN, wt("wt-o", "/x/other", "main", [ag("o-1", parent="a-coord")], project=OTHER, main=True)),
}
_unread = git(row("/w/u", "topic"), status="unreadable")
CASES["unreadable"] = {"structure": _unread, "summary": summary(MAIN)}


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    return _run(
        tmp_path_factory.mktemp("unscoped"),
        {
            "cases": CASES,
            "labels": [
                [{"branch": "main", "main": True}, True],
                [{"branch": None, "head": "abcdef0123456789", "main": False}, True],
                [{"branch": None, "main": False}, True],
                [{"branch": "main", "main": True, "project": {"id": "p", "name": "other"}}, False],
            ],
        },
    )


@pytest.fixture(scope="module")
def got(out: dict[str, Any]) -> dict[str, Any]:
    return out["cases"]


def _items(entry: dict[str, Any]) -> list[tuple[str, str | None, list[str]]]:
    return [(it["label"], it["badge"], it["agents"]) for it in entry["items"]]


def test_the_words_and_the_fold(out: dict[str, Any]) -> None:
    """T-02: the English words of the row in one place."""
    words = out["consts"]["UNSCOPED"]
    assert words["lead"] == "Unscoped"
    assert words["leadTitle"] == "Worktrees not shown as a Scope box"
    assert words["primary"] == {"text": "Primary", "title": "The main checkout of this repository"}
    assert words["unlinked"] == {
        "text": "Unlinked",
        "title": "Not linked to any Scope. Link it with `spec-dock work start`.",
    }
    assert words["count"] is None  # iss-00676 D-03: no count's words
    assert out["consts"]["FOLD"] == 2
    assert {"childCount", "countTitle", "commanding"}.isdisjoint(out["exports"])


def test_primary_is_there_without_agents_summary_or_pairs(got: dict[str, Any]) -> None:
    """T-02 / R-02, F-02: the main checkout from git alone."""
    assert got["bare"]["items"] == [
        {
            "key": "git:/w/r",
            "kind": "worktree",
            "label": "main",
            "badge": "primary",
            "own": True,
            "main": True,
            "path": "/w/r",
            "agents": [],
            "agentWorktrees": [],
            "worktree": {"id": None, "agents": []},
            "idle": True,
            "folded": None,
            "fields": ["agents", "badge", "folded", "idle", "key", "kind", "label", "main", "own", "path", "worktree"],
        }
    ]
    assert got["bare"]["git"][0] == row("/w/r", "main", main=True)


def test_primary_holds_the_coordinator_directing_nobody(got: dict[str, Any]) -> None:
    """T-02 / R-02: the key is the band's key of the summary's worktree."""
    entry = got["idle-coord"]
    assert _items(entry) == [("main", "primary", ["a-coord"])]
    assert entry["items"][0]["key"] == entry["bandKeys"]["wt-main"] == "wt-main"
    assert entry["items"][0]["idle"] is False


def test_unlinked_worktrees_and_a_thin_idle_one(got: dict[str, Any]) -> None:
    """T-02 / R-03, R-04, F-04: Scope worktrees are left out; a single idle Unlinked worktree is thin, not folded."""
    entry = got["unlinked"]
    assert _items(entry) == [
        ("main", "primary", ["a-coord"]),
        ("old-1", "unlinked", []),
        ("topic-a", "unlinked", ["a-1"]),
        ("topic-b", "unlinked", ["b-1", "b-2"]),
    ]
    assert [it["idle"] for it in entry["items"]] == [False, True, False, False]
    assert [it["key"] for it in entry["items"]] == ["wt-main", "git:/w/old-1", "wt-a", "wt-b"]
    assert entry["items"][2]["path"] == "/w/u-a"  # the trailing / is the same worktree
    assert all("count" not in it["fields"] for it in entry["items"])


def test_two_or_more_idle_unlinked_worktrees_fold_into_plus_n(got: dict[str, Any]) -> None:
    """T-02 / R-04: every idle Unlinked worktree in one +N, last, with their labels and paths; detached shows its HEAD."""
    items = got["fold"]["items"]
    assert [(it["kind"], it["label"]) for it in items] == [("worktree", "main"), ("fold", "+3")]
    fold = items[-1]
    assert fold["key"] == "fold"
    assert fold["agents"] == [] and fold["idle"] is True and fold["badge"] is None
    assert fold["folded"] == [
        {"label": "detached @abcdef0", "path": "/w/d"},
        {"label": "old-1", "path": "/w/old-1"},
        {"label": "old-2", "path": "/w/old-2"},
    ]


def test_every_agent_of_a_worktree_in_one_item_in_order(got: dict[str, Any]) -> None:
    """T-02 / R-09: the agents of no command line too, in orderOf's order."""
    assert got["order"]["items"][1]["agents"] == ["x5", "x3", "x1", "x2", "x4"]


def test_two_summary_worktrees_of_one_path_make_one_item(got: dict[str, Any]) -> None:
    """T-02 / F-04 and the review's P3: the second worktree's agents join the first one's item, its end's key follows."""
    entry = got["merge"]
    item = entry["items"][1]
    assert (item["key"], item["badge"], item["agents"]) == ("wt-u1", "unlinked", ["u-1", "u-2"])
    assert item["agentWorktrees"] == ["wt-u1", "wt-u2"]
    assert item["worktree"] == {"id": "wt-u1", "agents": ["u-1", "u-2"]}  # the merged worktree
    assert entry["placesBefore"]["u-2"] == {"kind": "band", "key": "wt-u2"}
    assert entry["places"]["u-2"] == {"kind": "band", "key": "wt-u1"}
    assert entry["places"]["u-1"] == {"kind": "band", "key": "wt-u1"}
    assert len(entry["items"]) == 2


def test_ends_outside_git_stay_as_todays_items(got: dict[str, Any]) -> None:
    """T-02 / R-03: an end matching an item joins it; the others keep today's items without a badge, after Unlinked."""
    entry = got["ends"]
    assert _items(entry) == [
        ("main", "primary", ["a-coord"]),
        ("topic", "unlinked", ["u-1"]),
        ("zeta", None, ["z-1"]),
        ("other · main", None, ["o-1"]),
    ]
    assert [it["key"] for it in entry["items"]] == ["wt-main", "wt-u", "wt-z", "wt-o"]
    assert [entry["places"][a] for a in ("a-coord", "u-1", "z-1", "o-1")] == [
        {"kind": "band", "key": k} for k in ("wt-main", "wt-u", "wt-z", "wt-o")
    ]
    assert [it["own"] for it in entry["items"]] == [True, True, True, False]


@pytest.mark.parametrize("name", ["next", "all", "now"])
def test_every_range_shows_every_unlinked_without_counts(got: dict[str, Any], name: str) -> None:
    """iss-00676 T-02 / R-02: no count in any range; the idle ones fold; the non-commanding one stays."""
    entry = got[name]
    assert [(it["kind"], it["label"]) for it in entry["items"]] == [
        ("worktree", "main"),
        ("worktree", "u1"),
        ("worktree", "u2"),
        ("fold", "+2"),
    ]
    assert all("count" not in it["fields"] and "countParts" not in it["fields"] for it in entry["items"])


def test_next_has_the_items_and_the_places_of_all_and_now(got: dict[str, Any]) -> None:
    """iss-00676 T-02 / R-01, R-02: the range given to unscopedItems changes nothing; "next" places its ends."""
    assert got["next"]["items"] == got["all"]["items"] == got["now"]["items"]
    assert got["next"]["places"] == got["all"]["places"]
    assert got["next"]["places"]["a-coord"] == {"kind": "band", "key": "wt-main"}


def test_next_keeps_the_unlinked_worktree_directing_nobody(got: dict[str, Any]) -> None:
    """iss-00676 T-02 / R-02: the main checkout and the Unlinked worktree of an agent directing nobody."""
    entry = got["next-idle"]
    assert _items(entry) == [("main", "primary", ["a-coord"]), ("topic", "unlinked", ["u-1"])]


def test_without_a_main_row_there_is_no_primary(got: dict[str, Any]) -> None:
    """T-02 / F-03."""
    assert [it["badge"] for it in got["no-main"]["items"]] == ["unlinked"]


def test_without_the_git_list_the_band_items_mark_main_primary(got: dict[str, Any]) -> None:
    """T-02 / F-01: today's ends only; the summary's main is Primary."""
    for name in ("old", "unreadable"):
        assert got[name]["git"] is None
    assert _items(got["old"]) == [("main", "primary", ["a-coord"]), ("other · main", None, ["o-1"])]
    assert got["unreadable"]["items"] == []


def test_band_labels(out: dict[str, Any]) -> None:
    """T-02 / R-02: the main checkout's branch, detached @HEAD, the unknown branch, another repository."""
    assert out["labels"] == ["main", "detached @abcdef0", "ブランチ不明", "other · main"]
