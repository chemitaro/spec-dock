"""The dashboard model (iss-00528, epic-00427 D-04)."""

from __future__ import annotations

from datetime import timedelta
import time

from spec_dock.runtime.domain.canonical_readiness import evaluate_readiness
from spec_dock.runtime.domain.canonical_structure import ExternalIssue, StructureAnomaly
from spec_dock.runtime.domain.dashboard_model import (
    SeenScope,
    build_model,
    child_stages,
    compare_seen,
    downstream_ids,
    recent_events,
    root_waits,
    seen_scopes,
    upstream,
    weekly_totals,
)
from spec_dock.runtime.domain.dashboard_snapshot import NO_PULL_REQUESTS, PullRequestsError
from tests.support.dashboard import NOW, closed, node, pr, prs, snapshot


def sample():
    """The Epic R-10 acceptance structure under Initiative 1."""
    return snapshot(
        node(1, "initiative"),
        node(2, "epic", parent=1),
        node(3, "issue", parent=2, in_progress=True),
        node(4, "issue", parent=2, blocked_by=(5,)),
        node(5, "issue", parent=2),
        node(6, "epic", parent=1, blocked_by=(2,)),
        node(7, "issue", parent=6),
        node(8, "issue", parent=2, blocked_by=(100,)),
        closed(9, "issue", parent=2),
        closed(10, "epic", parent=1),
        node(11, "issue", parent=10),
        node(12, "epic", parent=1),
        closed(13, "issue", parent=12),
        node(14, "epic", parent=1),
        node(15, "issue", parent=14, in_progress=True),
        node(16, "issue", parent=2),
        node(18, "epic", parent=1),
        node(19, "issue", parent=18),
        closed(20, "issue", parent=2),
        node(22, "issue", parent=2),
        node(23, "issue", parent=2, blocked_by=(22,)),
        node(24, "issue", parent=2, blocked_by=(22,)),
        node(25, "issue", parent=2, blocked_by=(5, 22)),
        external=(ExternalIssue(100, "outside", "open"),),
        anomalies=(
            StructureAnomaly(16, "KIND_LABEL_MULTIPLE", "two kind labels"),
            StructureAnomaly(18, "KIND_LABEL_MULTIPLE", "two kind labels"),
            StructureAnomaly(20, "KIND_LABEL_MULTIPLE", "two kind labels"),
        ),
    )


def states(model):
    return {scope.id: scope.state for scope in model.scopes.values()}


# T-01 -----------------------------------------------------------------------------------------------------


def test_states_follow_readiness_and_add_only_descendant_work_for_parents() -> None:
    model = build_model(sample(), now=NOW)
    assert states(model) == {
        "init-00001": "doing",
        "epic-00002": "doing",
        "iss-00003": "doing",
        "iss-00004": "blocked",
        "iss-00005": "ready",
        "epic-00006": "blocked",
        "iss-00007": "blocked",
        "iss-00008": "blocked",
        "iss-00009": "done",
        "epic-00010": "done",
        "iss-00011": "blocked",
        "epic-00012": "ready",
        "iss-00013": "done",
        "epic-00014": "doing",
        "iss-00015": "doing",
        "iss-00016": "unknown",
        "epic-00018": "unknown",
        "iss-00019": "unknown",
        "iss-00020": "done",
        "iss-00022": "ready",
        "iss-00023": "blocked",
        "iss-00024": "blocked",
        "iss-00025": "blocked",
    }


def test_every_issue_state_matches_evaluate_readiness() -> None:
    structure = sample()
    model = build_model(structure, now=NOW)
    names = {"DONE": "done", "UNKNOWN": "unknown", "DOING": "doing", "BLOCKED": "blocked", "READY": "ready"}
    for scope in model.scopes.values():
        if scope.kind == "issue":
            assert scope.state == names[evaluate_readiness(structure, scope.id).state], scope.id


def test_reasons_name_the_closed_parent_own_inherited_and_external_waits() -> None:
    model = build_model(sample(), now=NOW)
    reason = {scope.id: scope.reason for scope in model.scopes.values()}
    assert (reason["iss-00011"].code, reason["iss-00011"].numbers) == ("parent_closed", (10,))
    assert (reason["iss-00004"].code, reason["iss-00004"].numbers, reason["iss-00004"].text) == (
        "waiting",
        (5,),
        "#5 を待つ",
    )
    assert (reason["iss-00007"].code, reason["iss-00007"].numbers) == ("inherited_waiting", (2,))
    assert "epic-00006" in reason["iss-00007"].text
    assert (reason["iss-00008"].code, reason["iss-00008"].numbers) == ("waiting_external", (100,))
    assert (reason["epic-00014"].code, reason["epic-00014"].numbers) == ("descendant_in_progress", (15,))
    assert reason["iss-00003"].code == "in_progress"
    assert reason["iss-00016"].code == "KIND_LABEL_MULTIPLE"
    assert reason["iss-00009"].code == "closed" and reason["iss-00005"].code == "no_waits"


def test_a_closed_descendant_with_a_stale_in_progress_label_does_not_make_the_parent_doing() -> None:
    model = build_model(
        snapshot(node(1, "initiative"), node(2, "epic", parent=1), closed(3, "issue", parent=2, in_progress=True)),
        now=NOW,
    )
    assert model.scope("epic-00002").state == "ready"


def test_an_anomaly_keeps_the_rest_of_the_model() -> None:
    model = build_model(sample(), now=NOW)
    assert model.scope("iss-00019").state == "unknown" and model.scope("iss-00005").state == "ready"
    assert len(model.anomalies) == 3


# T-02 -----------------------------------------------------------------------------------------------------


def merge_sample():
    return snapshot(
        node(1, "initiative"),
        node(2, "epic", parent=1),
        node(3, "issue", parent=2, in_progress=True),
        node(4, "issue", parent=2, in_progress=True),
        node(5, "issue", parent=2, in_progress=True),
        node(6, "issue", parent=2, in_progress=True),
        node(7, "issue", parent=2, in_progress=True),
        node(8, "issue", parent=2, in_progress=True),
        node(9, "issue", parent=2, in_progress=True),
    )


def merge_prs(**options):
    return prs(
        pr(103, "iss-00003"),
        pr(104, "chemitaro/iss-00004", checks="failure"),
        pr(105, "iss-00005", draft=True),
        pr(106, "iss-00006-fix", mergeable="conflicting"),
        pr(107, "iss-00007", checks="pending", mergeable="unknown"),
        pr(108, "iss-00008", checks="none"),
        pr(109, "iss-00009", state="merged", merged_at="2026-11-03T00:00:00Z"),
        **options,
    )


def test_awaiting_merge_splits_mergeable_and_needs_fix_and_drafts_stay_doing() -> None:
    model = build_model(merge_sample(), merge_prs(), now=NOW)
    lanes = {scope.id: (scope.lane, scope.merge) for scope in model.scopes.values() if scope.kind == "issue"}
    assert lanes == {
        "iss-00003": ("awaiting_merge", "mergeable"),
        "iss-00004": ("awaiting_merge", "needs_fix"),
        "iss-00005": ("doing", None),
        "iss-00006": ("awaiting_merge", "needs_fix"),
        "iss-00007": ("awaiting_merge", "mergeable"),
        "iss-00008": ("awaiting_merge", "mergeable"),
        "iss-00009": ("doing", None),
    }
    assert all(model.scope(f"iss-0000{n}").state == "doing" for n in range(3, 10))
    assert model.scope("iss-00004").reason.code == "pr_needs_fix"
    assert model.scope("iss-00007").reason.text == "PR #107 をマージできる（CI は実行中）"
    assert model.lane("awaiting_merge") == ("iss-00003", "iss-00007", "iss-00008", "iss-00004", "iss-00006")


def test_unknown_pull_requests_never_make_awaiting_merge_but_stale_ones_do() -> None:
    unknown = build_model(merge_sample(), NO_PULL_REQUESTS, now=NOW)
    assert unknown.pull_request_status == "unknown" and not unknown.lane("awaiting_merge")
    assert all(scope.pr is None for scope in unknown.scopes.values())
    stale = build_model(
        merge_sample(),
        merge_prs(error=PullRequestsError("GITHUB_UNAVAILABLE", "down", "2026-11-04T11:55:00Z")),
        now=NOW,
    )
    assert stale.pull_request_status == "stale" and stale.scope("iss-00003").lane == "awaiting_merge"


# T-03 -----------------------------------------------------------------------------------------------------


def test_downstream_counts_waiters_their_descendants_and_waiters_of_ancestors() -> None:
    model = build_model(sample(), now=NOW)
    # 5 is waited by 4 and 25; Epic 2 (its parent) is waited by Epic 6 and its child 7.
    assert model.scope("iss-00005").downstream == 4
    assert model.scope("iss-00022").downstream == 5
    assert model.scope("iss-00004").downstream == 2
    assert model.scope("iss-00009").downstream == 0
    path = downstream_ids(model, "iss-00005")
    assert (path.direct, path.indirect) == (("iss-00004", "iss-00025"), ("epic-00006", "iss-00007"))


def test_waits_count_unfinished_prerequisites_and_open_external_issues() -> None:
    model = build_model(sample(), now=NOW)
    assert {scope.id: scope.waits for scope in model.scopes.values() if scope.state == "blocked"} == {
        "iss-00004": 1,
        "epic-00006": 1,
        "iss-00007": 1,
        "iss-00008": 1,
        "iss-00011": 0,
        "iss-00023": 1,
        "iss-00024": 1,
        "iss-00025": 2,
    }


def test_recommended_order_puts_the_most_waited_ready_first_and_the_fewest_waits_blocked_first() -> None:
    model = build_model(sample(), now=NOW)
    assert model.lane("ready") == ("iss-00022", "iss-00005", "epic-00012")
    assert model.lane("blocked") == (
        "iss-00011",
        "iss-00004",
        "iss-00008",
        "iss-00023",
        "iss-00024",
        "epic-00006",
        "iss-00007",
        "iss-00025",
    )


def test_done_is_ordered_newest_closed_first() -> None:
    model = build_model(
        snapshot(
            closed(1, "issue", closed_at="2026-10-01T00:00:00Z"),
            closed(2, "issue", closed_at="2026-10-03T00:00:00Z"),
            closed(3, "issue", closed_at="2026-10-02T00:00:00Z"),
        ),
        now=NOW,
    )
    assert model.lane("done") == ("iss-00002", "iss-00003", "iss-00001")


# T-04 -----------------------------------------------------------------------------------------------------


def test_cleanup_lists_finished_open_parents_and_closed_parents_with_open_descendants() -> None:
    model = build_model(sample(), now=NOW)
    assert [(item.scope_id, item.code) for item in model.cleanup] == [
        ("epic-00012", "all_descendants_closed"),
        ("iss-00011", "open_under_closed_parent"),
        ("epic-00010", "closed_with_open_descendants"),
    ]
    assert model.cleanup[1].text == "閉じた親 epic-00010 の下で開いている"
    assert model.cleanup[0].text == "配下の 1件がすべて終わったのに、開いたまま"
    assert model.scope("epic-00010").keep_visible and not model.scope("iss-00009").keep_visible


def test_an_open_epic_without_children_is_not_a_cleanup_candidate() -> None:
    model = build_model(snapshot(node(1, "initiative"), node(2, "epic", parent=1)), now=NOW)
    assert model.cleanup == ()


# T-05 -----------------------------------------------------------------------------------------------------


def staged():
    return snapshot(
        node(1, "initiative"),
        node(2, "epic", parent=1),
        node(3, "epic", parent=1, blocked_by=(2,)),
        node(4, "issue", parent=3, blocked_by=(10,)),
        node(5, "epic", parent=1),
        node(6, "issue", parent=5, blocked_by=(4,)),
        node(7, "epic", parent=1, blocked_by=(8,)),
        node(8, "epic", parent=1, blocked_by=(7,)),
        node(9, "issue", parent=2, blocked_by=(200,)),
        closed(10, "issue"),
        external=(ExternalIssue(200, "outside", "open"),),
    )


def test_children_split_into_stages_counting_descendant_dependencies() -> None:
    model = build_model(staged(), now=NOW)
    stages = child_stages(model, "init-00001")
    assert stages.stages == (("epic-00002",), ("epic-00003",), ("epic-00005",))
    assert stages.cyclic == ("epic-00007", "epic-00008")
    assert stages.external == (("epic-00002", 200), ("epic-00003", 10))


def test_open_only_stages_drop_closed_targets_and_top_level_lists_roots() -> None:
    model = build_model(staged(), now=NOW)
    assert child_stages(model, "init-00001", open_only=True).external == (("epic-00002", 200),)
    assert child_stages(model, None).stages == (("iss-00010",), ("init-00001",))
    assert child_stages(model, None, open_only=True).stages == (("init-00001",),)


def test_upstream_and_root_waits_reach_the_unblocked_end() -> None:
    model = build_model(staged(), now=NOW)
    path = upstream(model, "iss-00006")
    assert path.direct == ("iss-00004",)
    assert path.indirect == ("epic-00002", "iss-00009", "iss-00010")
    waits = root_waits(model, "iss-00006")
    assert waits.scope_ids == ()  # Epic 2 still has its open child 9, which waits for #200
    assert waits.external == (200,)
    simple = build_model(sample(), now=NOW)
    assert root_waits(simple, "iss-00025").scope_ids == ("iss-00022", "iss-00005")
    assert root_waits(simple, "iss-00005") == root_waits(simple, "iss-00003")


def test_root_waits_skip_an_in_progress_middle_and_a_parent_with_open_children() -> None:
    model = build_model(
        snapshot(
            node(1, "epic"),
            node(2, "issue", parent=1),
            node(3, "issue", blocked_by=(4,), in_progress=True),
            node(4, "issue"),
            node(5, "issue", blocked_by=(1, 3)),
        ),
        now=NOW,
    )
    assert model.scope("iss-00003").state == "doing"
    assert root_waits(model, "iss-00005").scope_ids == ("iss-00004", "iss-00002")


# T-06 -----------------------------------------------------------------------------------------------------


def test_compare_seen_finds_state_new_and_pr_changes_only() -> None:
    before_snapshot = snapshot(node(1, "issue"), node(2, "issue"), node(3, "issue", in_progress=True))
    before = seen_scopes(build_model(before_snapshot, prs(), now=NOW))
    after_snapshot = snapshot(
        node(1, "issue", title="Renamed", in_progress=True),
        node(2, "issue", title="Renamed"),
        node(3, "issue", in_progress=True),
        node(4, "issue"),
    )
    model = build_model(after_snapshot, prs(pr(30, "iss-00003")), now=NOW)
    changes = compare_seen(model, before)
    assert {key: sorted(value.kinds) for key, value in changes.items()} == {
        "iss-00001": ["state"],
        "iss-00003": ["pr"],
        "iss-00004": ["new"],
    }
    assert changes["iss-00003"].pr_before == "none"
    assert seen_scopes(model)["iss-00003"] == SeenScope("doing", "open")


def test_compare_seen_needs_a_baseline_and_known_pr_phases() -> None:
    structure = snapshot(node(1, "issue", in_progress=True))
    assert compare_seen(build_model(structure, now=NOW), None) == {}
    unknown = build_model(structure, NO_PULL_REQUESTS, now=NOW)
    assert compare_seen(unknown, {"iss-00001": SeenScope("doing", "none")}) == {}
    known = build_model(structure, prs(pr(5, "iss-00001", state="merged", merged_at="2026-11-02T00:00:00Z")), now=NOW)
    assert seen_scopes(known)["iss-00001"].pr == "merged"


# T-07 -----------------------------------------------------------------------------------------------------


def test_weekly_totals_are_cumulative_by_monday_weeks() -> None:
    model = build_model(
        snapshot(
            node(1, "epic", created_at="2026-10-14T10:00:00Z"),
            closed(2, "issue", parent=1, created_at="2026-10-19T00:00:00Z", closed_at="2026-10-27T00:00:00Z"),
            node(3, "issue", parent=1, created_at="2026-10-25T23:00:00Z"),
        ),
        now=NOW,
    )
    assert [(w.week_start, w.created, w.closed) for w in weekly_totals(model, now=NOW)] == [
        ("2026-10-12", 1, 0),
        ("2026-10-19", 3, 0),
        ("2026-10-26", 3, 1),
        ("2026-11-02", 3, 1),
    ]
    assert [(w.created, w.closed) for w in weekly_totals(model, now=NOW, kinds=("issue",))] == [(2, 0), (2, 1), (2, 1)]


def test_recent_events_mix_scope_and_pr_events_newest_first() -> None:
    model = build_model(
        snapshot(
            node(1, "issue", created_at="2026-10-01T00:00:00Z", in_progress=True),
            closed(2, "issue", created_at="2026-10-02T00:00:00Z", closed_at="2026-10-05T00:00:00Z"),
        ),
        prs(pr(9, "iss-00001", state="merged", created_at="2026-10-03T00:00:00Z", merged_at="2026-10-04T00:00:00Z")),
        now=NOW,
    )
    assert [(e.kind, e.number) for e in recent_events(model)] == [
        ("closed", 2),
        ("pr_merged", 9),
        ("pr_opened", 9),
        ("created", 2),
        ("created", 1),
    ]
    assert len(recent_events(model, limit=2)) == 2


def test_recent_events_include_every_mapped_pull_request_and_none_while_unknown() -> None:
    structure = snapshot(node(5, "issue", created_at="2026-10-01T00:00:00Z", in_progress=True))
    pulls = prs(
        pr(10, "iss-00005", state="merged", created_at="2026-10-02T00:00:00Z", merged_at="2026-10-03T00:00:00Z"),
        pr(12, "iss-00005-fix", created_at="2026-10-04T00:00:00Z"),
        pr(13, "feature/other", created_at="2026-10-05T00:00:00Z"),
    )
    model = build_model(structure, pulls, now=NOW)
    chosen = model.scope("iss-00005").pr
    assert chosen is not None and chosen.number == 12
    assert [(e.kind, e.number, e.scope_id) for e in recent_events(model)] == [
        ("pr_opened", 12, "iss-00005"),
        ("pr_merged", 10, "iss-00005"),
        ("pr_opened", 10, "iss-00005"),
        ("created", 5, "iss-00005"),
    ]
    unknown = build_model(structure, prs(pr(12, "iss-00005"), fetched_at=None), now=NOW)
    assert [e.kind for e in recent_events(unknown)] == ["created"]


# T-09 -----------------------------------------------------------------------------------------------------


def test_stale_is_strictly_more_than_thirty_minutes() -> None:
    fresh = (NOW - timedelta(minutes=29)).strftime("%Y-%m-%dT%H:%M:%SZ")
    old = (NOW - timedelta(minutes=31)).strftime("%Y-%m-%dT%H:%M:%SZ")
    assert not build_model(snapshot(node(1, "issue"), fetched_at=fresh), now=NOW).stale
    assert build_model(snapshot(node(1, "issue"), fetched_at=old), now=NOW).stale


# T-13 -----------------------------------------------------------------------------------------------------


def test_a_250_scope_structure_builds_quickly() -> None:
    nodes = [node(1, "initiative")]
    for epic in range(2, 22):
        nodes.append(node(epic, "epic", parent=1, blocked_by=(epic - 1,) if epic > 2 else ()))
    number = 22
    for epic in range(2, 22):
        for offset in range(11):
            nodes.append(node(number, "issue", parent=epic, blocked_by=(number - 1,) if offset else ()))
            number += 1
    structure = snapshot(*nodes)
    started = time.perf_counter()
    model = build_model(structure, now=NOW)
    elapsed = time.perf_counter() - started
    assert len(model.scopes) == 241 and elapsed < 2.0
