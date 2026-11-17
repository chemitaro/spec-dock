"""The cross-repository structure's notices (iss-00632 R-01, R-02, R-05, F-01).

`overviewWarnings` (views/_shared/logic.js) tells each warning's kind and its value; `splitNotices`
(views/allgraph/notices.js, pure) puts the kinds with a fixed text into one summary row per kind for the page and keeps
the rest, and every warning of a repository that cannot be read, in its frame. Both run in node
(`tests/js/dashboard_allgraph_notices.mjs`).
"""

from __future__ import annotations

import json
import subprocess
from typing import Any

import pytest

from tests.unit.presentation.test_dashboard_graph_js import ASSETS, ROOT, _node

CHECK = ROOT / "tests" / "js" / "dashboard_allgraph_notices.mjs"

OK = {"status": "ok", "stale": False, "age_seconds": 60}
STALE = {"snapshot": {"status": "ok", "stale": True, "age_seconds": 3 * 3600}, "notices": [{"code": "SNAPSHOT_STALE"}]}
STALE_PR = {**STALE, "pull_requests": {"status": "unknown"}}
FINE = {"snapshot": OK, "notices": [], "pull_requests": {"status": "ok"}}
PR = {"snapshot": OK, "notices": [], "pull_requests": {"status": "unknown"}}
AMBIGUOUS = {
    "snapshot": OK,
    "notices": [
        {
            "code": "REPOSITORY_AMBIGUOUS",
            "text": "同じリポジトリのクローンが2つあります。",
            "next_steps": ["spec-dock dashboard list"],
        }
    ],
    "pull_requests": {"status": "ok"},
}
UNREADABLE = {
    "snapshot": {"status": "unreadable", "age_seconds": 7200},
    "notices": [],
    "pull_requests": {"status": "unknown"},
}


def repo(key: str, structure: Any = None, failure: str | None = None, *, failed: bool = False) -> dict[str, Any]:
    owner, name = key.split("/")[-2:]
    return {
        "repository": key,
        "owner": owner,
        "name": name,
        "failed": failed,
        "structure": structure,
        "failure": failure,
    }


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    request = {
        "warnings": {
            "stale": [STALE, None],
            "missing": [{"snapshot": {"status": "missing"}, "notices": []}, None],
            "unsupported": [{"snapshot": {"status": "unsupported"}, "notices": []}, None],
            "unreadable": [UNREADABLE, None],
            "unreadable_no_age": [{"snapshot": {"status": "unreadable"}, "notices": []}, None],
            "anomalies": [{"snapshot": OK, "anomalies": [{}, {}], "notices": []}, None],
            "pr": [PR, None],
            "ambiguous": [AMBIGUOUS, None],
            "failure": [None, "HTTP 500"],
            "fine": [FINE, None],
        },
        "split": {
            "two_stale_one_pr": [
                repo("github.com/a/one", STALE),
                repo("github.com/a/two", STALE_PR),
                repo("github.com/a/three", FINE),
            ],
            "same_name": [
                repo("github.com/a/tool", PR),
                repo("github.com/b/tool", PR),
                repo("github.com/b/other", PR),
            ],
            "order": [
                repo("github.com/a/one", PR),
                repo("github.com/a/two", {"snapshot": OK, "anomalies": [{}], "notices": []}),
                repo("github.com/a/three", STALE),
                repo("github.com/a/four", {"snapshot": {"status": "missing"}, "notices": []}, failed=False),
            ],
            "own": [
                repo("github.com/a/broken", None, "HTTP 500", failed=True),
                repo("github.com/a/twice", {**AMBIGUOUS, "pull_requests": {"status": "unknown"}}),
                repo("github.com/a/unread", UNREADABLE, failed=True),
                {
                    "repository": "github.com/a/loading",
                    "owner": "a",
                    "name": "loading",
                    "failed": False,
                    "warnings": None,
                },
            ],
            "quiet": [repo("github.com/a/one", FINE), repo("github.com/a/two", FINE)],
        },
    }
    path = tmp_path_factory.mktemp("notices") / "request.json"
    path.write_text(json.dumps(request), encoding="utf-8")
    result = subprocess.run(
        [_node(), str(CHECK), str(ASSETS), str(path)], capture_output=True, text=True, timeout=120, check=False
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_every_warning_tells_its_kind_and_keeps_its_words(out: dict[str, Any]) -> None:
    w = out["warnings"]
    kinds = {name: [x.get("kind") for x in found] for name, found in w.items()}
    assert kinds == {
        "stale": ["stale"],
        "missing": ["snapshot-missing"],
        "unsupported": ["snapshot-unsupported"],
        "unreadable": ["snapshot-unreadable", "pr-unknown"],
        "unreadable_no_age": ["snapshot-unreadable"],
        "anomalies": ["anomalies"],
        "pr": ["pr-unknown"],
        "ambiguous": ["ambiguous"],
        "failure": ["failure"],
        "fine": [],
    }
    # the words, levels and next steps stay as they were (R-05)
    assert w["stale"][0]["text"] == "3時間前から更新されていません（定期の同期を確かめてください）。"
    assert w["stale"][0]["level"] == "warning" and w["stale"][0]["next"] == ["spec-dock canonical status"]
    assert w["failure"][0]["text"] == "このリポジトリを読めませんでした（HTTP 500）。"
    assert w["pr"][0] == {"level": "info", "text": "PR の状態が分かりません。", "next": [], "kind": "pr-unknown"}
    assert w["ambiguous"][0]["text"] == "同じリポジトリのクローンが2つあります。"


def test_the_kinds_carry_their_value(out: dict[str, Any]) -> None:
    w = out["warnings"]
    assert w["stale"][0]["detail"] == "3時間"
    assert w["unreadable"][0]["detail"] == "2時間"
    assert "detail" not in w["unreadable_no_age"][0]
    assert w["anomalies"][0]["detail"] == "2件"
    for name in ("missing", "unsupported", "pr", "ambiguous", "failure"):
        assert "detail" not in w[name][0], name


def test_the_summary_has_one_row_per_kind_with_the_repositories_in_the_lists_order(out: dict[str, Any]) -> None:
    s = out["split"]["two_stale_one_pr"]
    assert [(r["kind"], r["level"]) for r in s["summary"]] == [("stale", "warning"), ("pr-unknown", "info")]
    stale, pr = s["summary"]
    assert stale["text"] == "構造が更新されていません"
    assert stale["repos"] == [
        {"repository": "github.com/a/one", "label": "one", "detail": "3時間"},
        {"repository": "github.com/a/two", "label": "two", "detail": "3時間"},
    ]
    assert stale["next"] == ["spec-dock canonical status"]  # once, for the row
    assert pr["text"] == "PR の状態が分かりません" and pr["next"] == []
    assert [r["repository"] for r in pr["repos"]] == ["github.com/a/two"]
    assert "detail" not in pr["repos"][0] or pr["repos"][0]["detail"] is None
    # no frame keeps a summarised warning
    assert s["own"] == {"github.com/a/one": [], "github.com/a/two": [], "github.com/a/three": []}


def test_owner_and_name_only_when_two_repositories_share_a_name(out: dict[str, Any]) -> None:
    (row,) = out["split"]["same_name"]["summary"]
    assert [r["label"] for r in row["repos"]] == ["a/tool", "b/tool", "other"]


def test_the_rows_go_by_level_then_by_the_shared_kinds_order(out: dict[str, Any]) -> None:
    rows = out["split"]["order"]["summary"]
    assert [r["kind"] for r in rows] == ["snapshot-missing", "stale", "anomalies", "pr-unknown"]
    assert [r["level"] for r in rows] == ["error", "warning", "warning", "info"]
    assert rows[2]["repos"] == [{"repository": "github.com/a/two", "label": "two", "detail": "1件"}]
    assert out["shared"] == [
        "snapshot-missing",
        "snapshot-unsupported",
        "snapshot-unreadable",
        "stale",
        "anomalies",
        "pr-unknown",
    ]


def test_a_repository_that_cannot_be_read_keeps_every_warning_in_its_frame(out: dict[str, Any]) -> None:
    s = out["split"]["own"]
    own = s["own"]
    assert [w["kind"] for w in own["github.com/a/broken"]] == ["failure"]
    # failed: the unreadable snapshot and the unknown pull requests are its reasons, in its frame (F-01)
    assert [w["kind"] for w in own["github.com/a/unread"]] == ["snapshot-unreadable", "pr-unknown"]
    # readable: the two clones stay, the unknown pull requests go up
    assert [w["kind"] for w in own["github.com/a/twice"]] == ["ambiguous"]
    assert [(r["kind"], [x["repository"] for x in r["repos"]]) for r in s["summary"]] == [
        ("pr-unknown", ["github.com/a/twice"])
    ]
    # a repository still loading is not counted
    assert "github.com/a/loading" not in own


def test_no_warning_no_summary(out: dict[str, Any]) -> None:
    assert out["split"]["quiet"]["summary"] == []
