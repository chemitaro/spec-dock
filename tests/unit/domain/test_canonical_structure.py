"""Canonical structure representation: labels, IDs, kind changes and the structure snapshot."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable


def test_kind_labels_and_label_definitions_are_fixed_values() -> None:
    from spec_dock.runtime.domain.canonical_structure import IN_PROGRESS_LABEL, KIND_LABELS, LABEL_DEFINITIONS

    assert KIND_LABELS == {
        "initiative": "spec-dock:initiative",
        "epic": "spec-dock:epic",
        "issue": "spec-dock:issue",
    }
    assert IN_PROGRESS_LABEL == "spec-dock:in-progress"
    assert [definition.name for definition in LABEL_DEFINITIONS] == [*KIND_LABELS.values(), IN_PROGRESS_LABEL]
    assert all(
        len(definition.color) == 6 and int(definition.color, 16) >= 0 and definition.description
        for definition in LABEL_DEFINITIONS
    )


@pytest.mark.parametrize(
    ("labels", "expected"),
    [
        ((), (None, None)),
        (("bug", "spec-dock:in-progress"), (None, None)),
        (("spec-dock:epic",), ("epic", None)),
        (("bug", "spec-dock:issue", "spec-dock:in-progress"), ("issue", None)),
        (("spec-dock:epic", "spec-dock:issue"), (None, "KIND_LABEL_MULTIPLE")),
    ],
)
def test_kind_comes_from_exactly_one_kind_label(labels: tuple[str, ...], expected: tuple[object, object]) -> None:
    from spec_dock.runtime.domain.canonical_structure import kind_from_labels

    assert kind_from_labels(labels) == expected


def test_scope_ids_use_the_padded_issue_number() -> None:
    from spec_dock.runtime.domain.canonical_structure import parse_scope_id, scope_id

    assert scope_id("initiative", 423) == "init-00423"
    assert scope_id("epic", 424) == "epic-00424"
    assert scope_id("issue", 123456) == "iss-123456"
    assert scope_id("issue", 1) == "iss-00001"
    assert scope_id("issue", 99999) == "iss-99999"
    assert scope_id("issue", 100000) == "iss-100000"
    assert parse_scope_id("iss-00428") == ("issue", 428)
    assert parse_scope_id(" EPIC-00424 ") == ("epic", 424)
    assert parse_scope_id("iss-100000") == ("issue", 100000)
    assert parse_scope_id("iss-123456") == ("issue", 123456)


@pytest.mark.parametrize(
    "invalid",
    [
        "init-local-00002",
        "adr-00001",
        "iss-",
        "428",
        "iss-0000x",
        "iss-454",
        "iss-0454",
        "iss-000454",
        "iss-00000",
        "iss-00454-foo",
        "issue-00454",
    ],
)
def test_names_outside_the_epic_id_pattern_are_not_ids(invalid: str) -> None:
    from spec_dock.runtime.domain.canonical_structure import parse_scope_id
    from spec_dock.runtime.domain.ids import CANONICAL_ID_RE

    with pytest.raises(ValueError):
        parse_scope_id(invalid)
    assert CANONICAL_ID_RE.pattern == r"^(init|epic|iss)-(?:[0-9]{5}|[1-9][0-9]{5,})$"


REPOSITORY = "github.com/example/repo"
FETCHED_AT = "2026-10-26T00:10:00Z"
STARTED_AT = "2026-10-26T00:09:58Z"


def _facts(number: int, *labels: str, state: str = "open", reason: str | None = None):
    from spec_dock.runtime.domain.canonical_structure import IssueFacts

    return IssueFacts(
        number=number,
        database_id=1_000_000 + number * 7,
        title=f"Title {number}",
        state=state,
        state_reason=reason,
        labels=labels,
        assignees=(),
        updated_at=f"2026-10-25T00:00:{number % 60:02d}Z",
        url=f"https://github.com/example/repo/issues/{number}",
    )


def _ref(number: int, repository: str = "example/repo", *, title: str | None = None, state: str | None = None):
    from spec_dock.runtime.domain.canonical_structure import RelatedIssue

    return RelatedIssue(number, repository, title, state)


def _scope(number: int, kind: str, *, parent=None, children=(), blocked_by=(), extra=(), **facts):
    """A fetched Scope Issue; its body is never read, so none is modelled."""
    from spec_dock.runtime.domain.canonical_structure import FetchedIssue

    labels = (f"spec-dock:{kind}", *extra) if kind else extra
    return FetchedIssue(
        _facts(number, *labels, **facts),
        parent,
        tuple(children),
        tuple(blocked_by),
    )


def _build(*issues):
    from spec_dock.runtime.domain.canonical_structure import build_snapshot

    return build_snapshot(REPOSITORY, issues, fetched_at=FETCHED_AT, fetch_started_at=STARTED_AT)


def test_a_kind_label_alone_gives_the_id_and_no_body_or_slug_is_kept() -> None:
    import dataclasses

    from spec_dock.runtime.domain.canonical_structure import IssueFacts, ScopeNode

    snapshot = _build(_scope(1, "initiative"), _scope(100000, "issue", parent=_ref(1)))
    assert [node.id for node in snapshot.scopes] == ["init-00001", "iss-100000"]
    assert "body" not in {field.name for field in dataclasses.fields(IssueFacts)}
    assert "slug" not in {field.name for field in dataclasses.fields(ScopeNode)}
    assert all("slug" not in item and "body" not in item for item in snapshot.to_json()["issues"].values())


def test_valid_structure_builds_ids_relations_external_and_reverse_edges() -> None:
    snapshot = _build(
        _scope(1, "initiative", children=[_ref(2)]),
        _scope(2, "epic", parent=_ref(1), children=[_ref(5), _ref(3)]),
        _scope(
            3,
            "issue",
            parent=_ref(2),
            blocked_by=[_ref(5), _ref(4, title="Vendor fix", state="OPEN")],
            extra=("spec-dock:in-progress", "bug"),
        ),
        _scope(5, "issue", parent=_ref(2), state="closed", reason="completed"),
    )
    assert snapshot.anomalies == ()
    assert [node.id for node in snapshot.scopes] == ["init-00001", "epic-00002", "iss-00003", "iss-00005"]
    epic = snapshot.issues[2]
    assert epic.sub_issues == (5, 3) and epic.parent == 1 and epic.kind == "epic"
    third = snapshot.find("iss-00003")
    assert third is not None and third.blocked_by == (4, 5) and third.in_progress is True
    assert third.labels == ("bug", "spec-dock:in-progress", "spec-dock:issue")
    assert snapshot.issues[5].blocking == (3,) and snapshot.issues[5].state_reason == "completed"
    assert snapshot.external[4].title == "Vendor fix" and snapshot.external[4].state == "open"
    assert snapshot.find("iss-00004") is None
    assert snapshot.to_json()["issues"]["3"] == {
        "number": 3,
        "database_id": 1_000_021,
        "id": "iss-00003",
        "kind": "issue",
        "title": "Title 3",
        "state": "open",
        "state_reason": None,
        "labels": ["bug", "spec-dock:in-progress", "spec-dock:issue"],
        "assignees": [],
        "in_progress": True,
        "parent": 2,
        "sub_issues": [],
        "blocked_by": [4, 5],
        "blocking": [],
        "updated_at": "2026-10-25T00:00:03Z",
        "url": "https://github.com/example/repo/issues/3",
    }
    assert snapshot.to_json()["external"] == {"4": {"number": 4, "title": "Vendor fix", "state": "open"}}


def _codes(snapshot) -> set[tuple[int, str]]:
    return {(anomaly.number, anomaly.code) for anomaly in snapshot.anomalies}


def test_rule_violations_are_anomalies_and_undetermined_scopes_have_no_id() -> None:
    snapshot = _build(
        _scope(1, "initiative"),
        _scope(2, "epic", parent=_ref(1)),
        _scope(3, "issue", parent=_ref(2)),
        _scope(10, "epic", parent=_ref(1), extra=("spec-dock:issue",)),
        _scope(13, "epic", parent=_ref(3)),
        _scope(14, "issue"),
        _scope(15, "initiative", parent=_ref(1)),
        _scope(16, "issue", parent=_ref(99)),
    )
    assert _codes(snapshot) == {
        (10, "KIND_LABEL_MULTIPLE"),
        (13, "PARENT_INVALID"),
        (14, "PARENT_MISSING"),
        (15, "PARENT_INVALID"),
        (16, "PARENT_INVALID"),
    }
    assert (snapshot.issues[10].kind, snapshot.issues[10].id) == (None, None)
    assert snapshot.issues[13].id == "epic-00013"
    assert all(anomaly.message for anomaly in snapshot.anomalies)
    assert snapshot.anomalies_for(14)[0].code == "PARENT_MISSING"


def test_dependency_rules_report_invalid_edges_and_every_cycle_member() -> None:
    snapshot = _build(
        _scope(1, "initiative"),
        _scope(2, "epic", parent=_ref(1), blocked_by=[_ref(3)]),
        _scope(3, "issue", parent=_ref(2)),
        _scope(4, "issue", parent=_ref(2), blocked_by=[_ref(4)]),
        _scope(5, "epic", parent=_ref(1)),
        _scope(6, "issue", parent=_ref(5), blocked_by=[_ref(7)]),
        _scope(7, "issue", parent=_ref(5), blocked_by=[_ref(6)]),
        _scope(8, "issue", parent=_ref(5), blocked_by=[_ref(3)]),
    )
    assert _codes(snapshot) == {
        (2, "DEPENDENCY_INVALID"),
        (4, "DEPENDENCY_INVALID"),
        (6, "DEPENDENCY_CYCLE"),
        (7, "DEPENDENCY_CYCLE"),
    }
    assert snapshot.issues[3].blocking == (2, 8)


def test_inherited_dependency_cycle_through_a_parent_is_reported() -> None:
    snapshot = _build(
        _scope(1, "initiative"),
        _scope(2, "epic", parent=_ref(1), blocked_by=[_ref(3)]),
        _scope(3, "epic", parent=_ref(1)),
        _scope(4, "issue", parent=_ref(2)),
        _scope(5, "issue", parent=_ref(3), blocked_by=[_ref(4)]),
    )
    assert {code for _, code in _codes(snapshot)} == {"DEPENDENCY_CYCLE"}
    assert {number for number, _ in _codes(snapshot)} == {3, 4, 5}


def test_foreign_relations_stay_out_of_every_relation_and_become_anomalies() -> None:
    snapshot = _build(
        _scope(1, "initiative", children=[_ref(2), _ref(9, "other/repo")]),
        _scope(2, "epic", parent=_ref(1), blocked_by=[_ref(4, "other/repo", title="Away", state="OPEN")]),
        _scope(3, "issue", parent=_ref(7, "other/repo")),
    )
    assert _codes(snapshot) == {
        (1, "SUB_ISSUE_FOREIGN_REPOSITORY"),
        (2, "DEPENDENCY_FOREIGN_REPOSITORY"),
        (3, "PARENT_FOREIGN_REPOSITORY"),
    }
    assert snapshot.issues[1].sub_issues == (2,)
    assert snapshot.issues[2].blocked_by == () and snapshot.external == {}
    assert snapshot.issues[3].parent is None
    assert "other/repo#9" in snapshot.anomalies_for(1)[0].message
    assert "other/repo#4" in snapshot.anomalies_for(2)[0].message
    assert "other/repo#7" in snapshot.anomalies_for(3)[0].message


def _sample():
    return _build(
        _scope(1, "initiative"),
        _scope(2, "epic", parent=_ref(1), children=[_ref(3)]),
        _scope(3, "issue", parent=_ref(2), blocked_by=[_ref(4, title="Plain", state="CLOSED")]),
        _scope(9, "issue", parent=_ref(2), extra=("spec-dock:epic",)),
    )


def test_json_round_trip_keeps_every_field_and_the_version_one_shape() -> None:
    import json

    from spec_dock.runtime.domain.canonical_structure import StructureSnapshot

    snapshot = _sample()
    payload = json.loads(json.dumps(snapshot.to_json()))
    assert payload["version"] == 1 and payload["repository"] == REPOSITORY
    assert (payload["fetched_at"], payload["fetch_started_at"]) == (FETCHED_AT, STARTED_AT)
    assert list(payload["issues"]) == ["1", "2", "3", "9"]
    assert payload["anomalies"] == [
        {"number": 9, "code": "KIND_LABEL_MULTIPLE", "message": payload["anomalies"][0]["message"]}
    ]
    assert payload["local_writes"] == []
    assert StructureSnapshot.from_json(payload) == snapshot


@pytest.mark.parametrize(
    "mutate",
    [
        lambda payload: payload.update(version=2),
        lambda payload: payload.update(version=True),
        lambda payload: payload.pop("external"),
        lambda payload: payload["issues"]["3"].pop("blocking"),
        lambda payload: payload["issues"]["3"].update(number="3"),
        lambda payload: payload["issues"]["3"].update(slug="leaf"),
        lambda payload: payload["issues"]["3"].update(id=None),
        lambda payload: payload["issues"]["3"].update(id="epic-00003"),
        lambda payload: payload["issues"]["9"].update(id="iss-00009"),
        lambda payload: payload["issues"]["3"].update(state="merged"),
        lambda payload: payload["issues"].update({"4": payload["issues"].pop("3")}),
        lambda payload: payload["anomalies"].append({"number": 1}),
        lambda payload: payload["local_writes"].append({"at": "x", "command": "c", "numbers": ["1"]}),
    ],
)
def test_unknown_versions_and_malformed_documents_are_rejected(mutate: Callable[[dict[str, Any]], object]) -> None:
    import json

    from spec_dock.runtime.domain.canonical_structure import SnapshotFormatError, StructureSnapshot

    payload = json.loads(json.dumps(_sample().to_json()))
    mutate(payload)
    with pytest.raises(SnapshotFormatError):
        StructureSnapshot.from_json(payload)
    with pytest.raises(SnapshotFormatError):
        StructureSnapshot.from_json(["not", "an", "object"])


def _relations():
    return _build(
        _scope(1, "initiative", children=[_ref(2), _ref(6)]),
        _scope(2, "epic", parent=_ref(1), children=[_ref(3)]),
        _scope(3, "issue", parent=_ref(2), blocked_by=[_ref(4, title="Plain", state="OPEN")]),
        _scope(5, "issue", parent=_ref(2), blocked_by=[_ref(3)]),
        _scope(6, "epic", parent=_ref(1)),
        _scope(8, "issue", parent=_ref(7, "other/repo")),
    )


def test_created_scope_and_parent_link_are_reflected_and_recorded() -> None:
    from spec_dock.runtime.domain.canonical_structure import SetParent, UpsertIssue, apply_changes

    created = _scope(20, "epic").facts
    snapshot = apply_changes(_relations(), [UpsertIssue(created)], at="2026-10-26T00:20:00Z", command="scope create")
    assert snapshot.find("epic-00020") is not None and (20, "PARENT_MISSING") in _codes(snapshot)
    snapshot = apply_changes(snapshot, [SetParent(20, 1)], at="2026-10-26T00:20:01Z", command="scope create")
    assert snapshot.issues[20].parent == 1 and snapshot.issues[1].sub_issues == (2, 6, 20)
    assert (20, "PARENT_MISSING") not in _codes(snapshot)
    assert [(item.at, item.command, item.numbers) for item in snapshot.local_writes] == [
        ("2026-10-26T00:20:00Z", "scope create", (20,)),
        ("2026-10-26T00:20:01Z", "scope create", (1, 20)),
    ]


def test_title_change_keeps_relations_and_kind_removal_turns_a_blocker_external() -> None:
    from dataclasses import replace

    from spec_dock.runtime.domain.canonical_structure import UpsertIssue, apply_changes

    base = _relations()
    facts = _scope(3, "issue").facts
    renamed = apply_changes(
        base, [UpsertIssue(replace(facts, title="日本語の題名"))], at=FETCHED_AT, command="scope edit"
    )
    node = renamed.issues[3]
    assert (node.id, node.title, node.parent, node.blocked_by, node.blocking) == (
        "iss-00003",
        "日本語の題名",
        2,
        (4,),
        (5,),
    )
    removed = apply_changes(
        base, [UpsertIssue(replace(facts, labels=("bug",), state="closed"))], at=FETCHED_AT, command="scope delete"
    )
    assert 3 not in removed.issues and removed.find("iss-00003") is None
    assert removed.external[3].state == "closed" and removed.issues[5].blocked_by == (3,)
    assert 4 not in removed.external


def test_parent_replacement_and_dependency_edits_update_both_ends() -> None:
    from spec_dock.runtime.domain.canonical_structure import (
        AddBlockedBy,
        ExternalIssue,
        RemoveBlockedBy,
        SetParent,
        apply_changes,
    )

    snapshot = apply_changes(
        _relations(),
        [SetParent(3, 6), AddBlockedBy(3, 7, ExternalIssue(7, "Vendor", "open")), RemoveBlockedBy(3, 4)],
        at=FETCHED_AT,
        command="scope move",
    )
    assert snapshot.issues[2].sub_issues == () and snapshot.issues[6].sub_issues == (3,)
    assert snapshot.issues[3].blocked_by == (7,) and set(snapshot.external) == {7}
    assert snapshot.local_writes[-1].numbers == (2, 3, 4, 6, 7)
    relinked = apply_changes(_relations(), [SetParent(8, 6)], at=FETCHED_AT, command="scope move")
    assert (8, "PARENT_FOREIGN_REPOSITORY") not in _codes(relinked) and relinked.issues[8].parent == 6


def test_refresh_merge_keeps_writes_reflected_after_the_fetch_started() -> None:
    from dataclasses import replace

    from spec_dock.runtime.domain.canonical_structure import UpsertIssue, apply_changes, build_snapshot, merge_refresh

    old = _relations()
    current = apply_changes(
        old, [UpsertIssue(_scope(9, "issue").facts)], at="2026-10-26T00:05:00Z", command="scope create"
    )
    current = apply_changes(
        current,
        [UpsertIssue(replace(_scope(3, "issue").facts, title="Renamed during fetch"))],
        at="2026-10-26T00:09:58Z",
        command="scope edit",
    )
    current = apply_changes(
        current,
        [UpsertIssue(_scope(20, "issue").facts)],
        at="2026-10-26T00:09:59Z",
        command="scope create",
    )
    fresh = build_snapshot(
        REPOSITORY,
        [
            _scope(1, "initiative"),
            _scope(2, "epic", parent=_ref(1), children=[_ref(3)]),
            _scope(3, "issue", parent=_ref(2)),
            _scope(9, "issue", parent=_ref(2)),
        ],
        fetched_at=FETCHED_AT,
        fetch_started_at=STARTED_AT,
    )
    merged = merge_refresh(current, fresh)
    assert merged.issues[3].title == "Renamed during fetch"
    assert 20 in merged.issues and merged.issues[9].parent == 2
    assert [item.command for item in merged.local_writes] == ["scope edit", "scope create"]
    assert merged.fetched_at == FETCHED_AT and merge_refresh(None, fresh) == fresh


def test_dependency_violations_preview_a_new_edge_on_the_snapshot() -> None:
    from spec_dock.runtime.domain.canonical_structure import dependency_violations

    snapshot = _relations()
    assert dependency_violations(snapshot, 3, 6) == ()
    assert {item.code for item in dependency_violations(snapshot, 3, 5)} == {"DEPENDENCY_CYCLE"}
    assert {item.code for item in dependency_violations(snapshot, 3, 2)} == {"DEPENDENCY_INVALID"}
    assert {item.code for item in dependency_violations(snapshot, 3, 3)} == {"DEPENDENCY_INVALID"}
    assert snapshot.issues[3].blocked_by == (4,)


def test_lenient_reflection_skips_changes_whose_numbers_are_not_in_the_snapshot() -> None:
    from spec_dock.runtime.domain.canonical_structure import (
        AddBlockedBy,
        ExternalIssue,
        RemoveBlockedBy,
        SetParent,
        StructureChange,
        UpsertIssue,
        apply_changes_lenient,
    )

    unknown: list[StructureChange] = [
        SetParent(99, 1),
        SetParent(3, 98),
        AddBlockedBy(97, 3),
        AddBlockedBy(3, 96),
        RemoveBlockedBy(95, 3),
    ]
    known: list[StructureChange] = [
        UpsertIssue(_scope(20, "issue").facts),
        SetParent(20, 2),
        AddBlockedBy(3, 94, ExternalIssue(94, "Plain", "open")),
        SetParent(5, None),
    ]
    snapshot, skipped = apply_changes_lenient(
        _relations(), [*unknown, *known], at="2026-10-26T00:20:00Z", command="dependency add"
    )
    assert skipped == tuple(unknown)
    assert snapshot.issues[20].parent == 2 and 94 in snapshot.issues[3].blocked_by and snapshot.external[94].title
    assert snapshot.issues[5].parent is None
    assert [(item.command, item.numbers) for item in snapshot.local_writes] == [("dependency add", (2, 3, 5, 20, 94))]


def _kinds():
    return _build(
        _scope(1, "initiative"),
        _scope(2, "epic", parent=_ref(1)),
        _scope(454, "epic", parent=_ref(1)),
        _scope(455, "issue", parent=_ref(2)),
        _scope(456, "issue", parent=_ref(2), extra=("spec-dock:epic",)),
    )


def test_a_catalog_name_whose_number_github_now_gives_another_kind_is_a_kind_change() -> None:
    from spec_dock.runtime.domain.canonical_structure import SCOPE_KIND_CHANGED, KindChange, kind_changes

    names = ["init-00001", "epic-00002", "iss-00454", "init-00454", "iss-00455", "iss-00456", "iss-00999", "notes"]
    assert SCOPE_KIND_CHANGED == "SCOPE_KIND_CHANGED"
    assert kind_changes(_kinds(), names) == {454: KindChange(454, "epic-00454", ("init-00454", "iss-00454"))}
    assert kind_changes(_kinds(), ["epic-00454", "iss-00454"])[454].directories == ("iss-00454",)
    assert kind_changes(_kinds(), ["epic-00454", "iss-00455-old", "iss-000455"]) == {}


def test_an_old_id_resolves_to_the_scope_github_now_gives_that_number() -> None:
    from spec_dock.runtime.domain.canonical_structure import renamed_scope

    snapshot = _kinds()
    found = renamed_scope(snapshot, "iss-00454")
    assert found is not None and found.id == "epic-00454"
    assert renamed_scope(snapshot, " ISS-00454 ") is found
    for unchanged in ("epic-00454", "iss-00455", "iss-00456", "epic-00456", "iss-00999", "iss-454", "@current"):
        assert renamed_scope(snapshot, unchanged) is None


@pytest.mark.parametrize(
    ("branch", "expected"),
    [
        ("iss-00454", True),
        ("iss-00454-foo", True),
        ("chemitaro/iss-00454-foo", True),
        ("team/a/iss-00454", True),
        ("iss-004541", False),
        ("iss-00454foo", False),
        ("epic-00454", False),
        ("iss-00454/foo", False),
        ("x-iss-00454", False),
    ],
)
def test_a_branch_names_a_scope_by_its_last_segment(branch: str, expected: bool) -> None:
    from spec_dock.runtime.domain.canonical_structure import branch_names_scope

    assert branch_names_scope(branch, "iss-00454") is expected


def test_branch_matching_needs_a_canonical_id() -> None:
    from spec_dock.runtime.domain.canonical_structure import branch_names_scope

    with pytest.raises(ValueError):
        branch_names_scope("iss-454", "iss-454")
