# mypy: disable-error-code="index, attr-defined, call-overload, has-type, misc, operator, arg-type"
"""Inputs of the legacy dashboard renderers built from a structure snapshot (iss-00438)."""

from __future__ import annotations

from dataclasses import replace

from spec_dock.runtime.domain.canonical_dashboard import dashboard_inputs, input_hash
from spec_dock.runtime.domain.canonical_structure import (
    ExternalIssue,
    LocalWrite,
    ScopeNode,
    StructureAnomaly,
    StructureSnapshot,
)

_PREFIX = {"initiative": "init", "epic": "epic", "issue": "iss"}


def node(number: int, kind: str, *, parent: int | None = None, **changes: object) -> ScopeNode:
    base = ScopeNode(
        number=number,
        database_id=1000 + number,
        id=f"{_PREFIX[kind]}-{number:05d}",
        kind=kind,  # type: ignore[arg-type]
        slug=f"s{number}",
        title=f"Scope {number}",
        state="open",
        state_reason=None,
        labels=(f"spec-dock:{kind}",),
        assignees=(),
        in_progress=False,
        parent=parent,
        sub_issues=(),
        blocked_by=(),
        blocking=(),
        updated_at="2026-10-26T00:00:00Z",
        url=f"https://github.com/o/r/issues/{number}",
        created_at="2026-10-25T00:00:00Z",
        closed_at=None,
    )
    return replace(base, **changes)  # type: ignore[arg-type]


def closed(number: int, kind: str, *, parent: int | None = None, reason: str = "completed") -> ScopeNode:
    return node(number, kind, parent=parent, state="closed", state_reason=reason, closed_at="2026-10-26T01:00:00Z")


def world() -> StructureSnapshot:
    nodes = (
        node(1, "initiative", title="計画"),
        node(2, "epic", parent=1, title='"引用" の Epic'),
        node(3, "issue", parent=2, title="着手できる"),
        node(4, "issue", parent=2, in_progress=True, title="作業中 A"),
        node(5, "issue", parent=2, in_progress=True, title="作業中 B"),
        closed(6, "issue", parent=2),
        node(7, "issue", parent=2, blocked_by=(3,), title="前提待ち"),
        node(8, "issue", parent=2, blocked_by=(50,), title="外部待ち"),
        node(9, "issue", parent=2, title="異常"),
        closed(10, "epic", parent=1),
        node(11, "issue", parent=10, title="閉じた Epic の下"),
        node(12, "issue", parent=2, blocked_by=(6,), title="前提は完了"),
    )
    return StructureSnapshot(
        "github.com/o/r",
        "2026-10-26T00:00:00Z",
        "2026-10-26T00:00:00Z",
        {item.number: item for item in nodes},
        {50: ExternalIssue(50, "Vendor fix", "open")},
        (StructureAnomaly(9, "SLUG_MARKER_MULTIPLE", "#9 has two markers"),),
        (),
    )


def test_index_nodes_take_the_state_and_blockers_from_readiness() -> None:
    nodes = dashboard_inputs(world()).index_nodes
    assert sorted(nodes) == [f"iss-{n:05d}" for n in (3, 4, 5, 6, 7, 8, 9, 11, 12)]
    states = {key: (value["board_state"], value["deps"]["blockers_top"]) for key, value in nodes.items()}  # type: ignore[index]
    assert states == {
        "iss-00003": ("READY", []),
        "iss-00004": ("DOING", []),
        "iss-00005": ("DOING", []),
        "iss-00006": ("DONE", []),
        "iss-00007": ("BLOCKED", ["iss-00003"]),
        "iss-00008": ("BLOCKED", ["#50"]),
        "iss-00009": ("UNKNOWN", []),
        "iss-00011": ("BLOCKED", ["epic-00010"]),
        "iss-00012": ("READY", []),
    }
    assert nodes["iss-00006"]["status"] == "done" and nodes["iss-00003"]["status"] == "open"  # type: ignore[index]
    assert nodes["iss-00003"] == {
        "type": "issue",
        "title": "着手できる",
        "status": "open",
        "board_state": "READY",
        "deps": {"ready": True, "blockers_top": []},
    }


def test_the_tree_nests_issues_under_epics_under_initiatives_in_id_order() -> None:
    tree = dashboard_inputs(world()).tree["tree"]
    assert [item["id"] for item in tree] == ["init-00001"]  # type: ignore[index]
    epics = tree[0]["epics"]  # type: ignore[index]
    assert [(epic["id"], epic["title"]) for epic in epics] == [
        ("epic-00002", '"引用" の Epic'),
        ("epic-00010", "Scope 10"),
    ]
    assert [issue["id"] for issue in epics[0]["issues"]] == [f"iss-{n:05d}" for n in (3, 4, 5, 6, 7, 8, 9, 12)]
    assert epics[1]["issues"][0]["board_state"] == "BLOCKED"


def test_a_scope_whose_parent_is_not_the_expected_kind_stays_out_of_the_tree() -> None:
    snapshot = world()
    issues = dict(snapshot.issues)
    issues[13] = node(13, "issue", parent=1)
    tree = dashboard_inputs(replace(snapshot, issues=issues)).tree["tree"]
    ids = [issue["id"] for epic in tree[0]["epics"] for issue in epic["issues"]]  # type: ignore[index]
    assert "iss-00013" not in ids


def test_deps_issues_holds_open_issues_and_blocking_edges_to_prerequisite_scopes() -> None:
    payload = dashboard_inputs(world()).deps_issues
    assert sorted(payload["nodes"]) == [f"iss-{n:05d}" for n in (3, 4, 5, 7, 8, 9, 11, 12)]  # type: ignore[arg-type]
    assert payload["nodes"]["iss-00007"] == {"type": "issue", "state": "blocked", "ready": False}  # type: ignore[index]
    assert payload["nodes"]["iss-00004"] == {"type": "issue", "state": "doing", "ready": True}  # type: ignore[index]
    assert payload["edges"] == [{"from": "iss-00007", "to": "iss-00003", "state": "blocking"}]


def test_deps_issues_shows_a_high_level_prerequisite_with_its_github_state() -> None:
    snapshot = world()
    issues = dict(snapshot.issues)
    issues[14] = node(14, "epic", parent=1)
    issues[3] = replace(issues[3], blocked_by=(14,))
    payload = dashboard_inputs(replace(snapshot, issues=issues)).deps_issues
    assert payload["nodes"]["epic-00014"] == {"type": "epic", "state": "open", "ready": False}  # type: ignore[index]
    assert {"from": "iss-00003", "to": "epic-00014", "state": "blocking"} in payload["edges"]  # type: ignore[operator]


def test_deps_raw_draws_unsatisfied_declared_dependencies_with_their_ancestors() -> None:
    payload = dashboard_inputs(world()).deps_raw
    assert payload["edges"] == [{"from": "iss-00007", "to": "iss-00003"}]
    (initiative,) = payload["tree"]  # type: ignore[misc]
    assert (initiative["id"], initiative["state"], initiative["state_source"]) == ("init-00001", "open", "github")
    (epic,) = initiative["epics"]
    assert epic["id"] == "epic-00002" and epic["state"] == "open"
    assert [(issue["id"], issue["state"]) for issue in epic["issues"]] == [
        ("iss-00003", "ready"),
        ("iss-00007", "blocked"),
    ]


def test_deps_raw_skips_a_high_level_scope_whose_issues_are_all_closed() -> None:
    snapshot = world()
    issues = dict(snapshot.issues)
    issues[20] = node(20, "epic", parent=1)
    issues[21] = closed(21, "issue", parent=20)
    issues[22] = node(22, "epic", parent=1, blocked_by=(20,))
    issues[23] = node(23, "issue", parent=22)
    payload = dashboard_inputs(replace(snapshot, issues=issues)).deps_raw
    assert {"from": "epic-00022", "to": "epic-00020"} not in payload["edges"]  # type: ignore[operator]


def test_the_input_hash_follows_issues_and_external_only() -> None:
    snapshot = world()
    same = replace(
        snapshot,
        fetched_at="2026-10-26T09:00:00Z",
        local_writes=(LocalWrite("2026-10-26T09:00:00Z", "scope edit", (3,)),),
    )
    assert input_hash(snapshot) == input_hash(same) and len(input_hash(snapshot)) == 64
    issues = dict(snapshot.issues)
    issues[3] = replace(issues[3], title="題名を変えた")
    assert input_hash(replace(snapshot, issues=issues)) != input_hash(snapshot)
    assert input_hash(replace(snapshot, external={50: ExternalIssue(50, "Vendor fix", "closed")})) != input_hash(
        snapshot
    )


def test_blockers_are_scopes_in_id_order_then_non_scope_issues_cut_to_five() -> None:
    snapshot = world()
    issues = dict(snapshot.issues)
    prerequisites = (31, 30, 33, 32, 34)
    for number in prerequisites:
        issues[number] = node(number, "issue", parent=2)
    issues[40] = node(40, "issue", parent=2, blocked_by=(*prerequisites, 51, 50))
    external = {50: ExternalIssue(50, "Vendor", "open"), 51: ExternalIssue(51, "Other", "open")}
    nodes = dashboard_inputs(replace(snapshot, issues=issues, external=external)).index_nodes
    assert nodes["iss-00040"]["deps"]["blockers_top"] == [  # type: ignore[index]
        "iss-00030",
        "iss-00031",
        "iss-00032",
        "iss-00033",
        "iss-00034",
    ]
    issues[40] = replace(issues[40], blocked_by=(31, 51, 50))
    nodes = dashboard_inputs(replace(snapshot, issues=issues, external=external)).index_nodes
    assert nodes["iss-00040"]["deps"]["blockers_top"] == ["iss-00031", "#50", "#51"]  # type: ignore[index]


def test_the_input_hash_follows_anomalies_the_format_and_the_snapshot_path() -> None:
    snapshot = world()
    foreign = StructureAnomaly(3, "DEPENDENCY_FOREIGN_REPOSITORY", "#3 has a blocker in another repository")
    changed = replace(snapshot, anomalies=(*snapshot.anomalies, foreign))
    assert input_hash(changed) != input_hash(snapshot)
    assert dashboard_inputs(changed).index_nodes["iss-00003"]["board_state"] == "UNKNOWN"  # type: ignore[index]
    assert input_hash(snapshot, snapshot_path="/a/snapshot.json") != input_hash(snapshot, snapshot_path="/b")
