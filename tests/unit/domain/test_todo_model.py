"""Due times, derived states, the list order, counts and filters of human tasks (iss-00549 D-02)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from spec_dock.runtime.domain.todo_model import Filters, count_limits, derived, matches, order, parse_when
from spec_dock.runtime.domain.todo_record import TodoError, new_record, transition

NOW = datetime(2026, 11, 4, 10, 0, tzinfo=timezone.utc)
JST = timezone(timedelta(hours=9))


def task(todo_id: str, due: str, **changes: object) -> dict[str, object]:
    record = new_record(todo_id, title=todo_id, by="human", role=None, kind=None, now="2026-11-01T00:00:00Z", due=due)
    record.update(changes)
    return record


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("30m", "2026-11-04T10:30:00Z"),
        ("4h", "2026-11-04T14:00:00Z"),
        ("2d", "2026-11-06T10:00:00Z"),
        ("2026-11-05", "2026-11-05T14:59:59Z"),
        ("2026-11-05T09:00:00+09:00", "2026-11-05T00:00:00Z"),
        ("2026-11-05T09:00:00Z", "2026-11-05T09:00:00Z"),
    ],
)
def test_due_forms(text: str, expected: str) -> None:
    assert parse_when(text, now=NOW, tz=JST) == expected


@pytest.mark.parametrize("text", ["yesterday", "0h", "31d", "2026-11-03", "2026-11-05T09:00:00", "1h ago"])
def test_bad_or_past_due_is_refused(text: str) -> None:
    with pytest.raises(TodoError) as raised:
        parse_when(text, now=NOW, tz=JST)
    assert (raised.value.code, raised.value.exit_code) == ("TODO_INVALID", 2)


def test_derived_states() -> None:
    late = derived(task("t-0001", "2026-11-04T09:00:00Z"), NOW)
    assert late["overdue"] is True and late["due_soon"] is False and late["effective_status"] == "open"
    soon = derived(task("t-0002", "2026-11-05T09:00:00Z", scopes={"related": [], "blocks": ["iss-00001"]}), NOW)
    assert soon["due_soon"] is True and soon["blocking"] is True and soon["overdue"] is False
    snoozed = task("t-0003", "2026-11-09T00:00:00Z", status="snoozed", snooze_until="2026-11-04T09:59:59Z")
    assert derived(snoozed, NOW)["effective_status"] == "open"
    snoozed["snooze_until"] = "2026-11-05T00:00:00Z"
    assert derived(snoozed, NOW)["effective_status"] == "snoozed" and derived(snoozed, NOW)["overdue"] is False
    parent = task("t-0004", "2026-11-09T00:00:00Z")
    parent = transition(parent, "subtask_add", now="2026-11-02T00:00:00Z", by="human", role=None, title="a")
    view = derived(parent, NOW)
    assert view["parent_closable"] is False and view["open_subtasks"] == [{"id": "t-0004.1", "title": "a"}]
    parent = transition(parent, "done", now="2026-11-02T00:00:00Z", by="human", role=None, target="t-0004.1")
    view = derived(parent, NOW)
    assert view["parent_closable"] is True and view["subtask_counts"] == {"open": 0, "total": 1}


def test_order_puts_overdue_first_then_soon_then_blocking_then_later() -> None:
    later = task("t-000a", "2026-11-20T00:00:00Z")
    blocking = task("t-000b", "2026-11-19T00:00:00Z", scopes={"related": [], "blocks": ["iss-00002"]})
    soon = task("t-000c", "2026-11-04T20:00:00Z")
    old_late = task("t-000d", "2026-11-01T00:00:00Z")
    new_late = task("t-000e", "2026-11-03T00:00:00Z")
    snoozed = task("t-000f", "2026-11-01T00:00:00Z", status="snoozed", snooze_until="2026-11-30T00:00:00Z")
    done = transition(task("t-000g", "2026-11-01T00:00:00Z"), "done", now="2026-11-02T00:00:00Z", by="human", role=None)
    done2 = transition(
        task("t-000h", "2026-11-01T00:00:00Z"), "done", now="2026-11-03T00:00:00Z", by="human", role=None
    )
    records = [later, done, blocking, snoozed, soon, done2, new_late, old_late]
    assert [record["id"] for record in order(records, NOW)] == [
        "t-000d",
        "t-000e",
        "t-000c",
        "t-000b",
        "t-000a",
        "t-000f",
        "t-000h",
        "t-000g",
    ]


def test_counts_skip_people_checklists_closed_and_subtasks() -> None:
    def agent(todo_id: str, kind: str) -> dict[str, object]:
        options = [{"key": "a", "text": "A"}, {"key": "b", "text": "B"}]
        return new_record(
            todo_id,
            title="t",
            by="agent",
            role="r",
            kind=kind,
            now="2026-11-01T00:00:00Z",
            due="2026-11-09T00:00:00Z",
            body="b",
            reply_to="here",
            effort="5m",
            options=options if kind == "decide" else (),
            recommendation={"key": "a", "reason": "r"} if kind == "decide" else None,
            items=("x", "y") if kind == "checklist" else (),
        )

    closed = transition(agent("t-0003", "check"), "done", now="2026-11-02T00:00:00Z", by="human", role=None)
    records = [agent("t-0001", "decide"), agent("t-0002", "checklist"), closed, task("t-0004", "2026-11-09T00:00:00Z")]
    counts = count_limits(records)
    assert counts.agent_parents == 1
    assert counts.open_subtasks == {"t-0001": 0, "t-0002": 2, "t-0003": 0, "t-0004": 0}


def test_filters() -> None:
    related = task("t-0001", "2026-11-09T00:00:00Z", scopes={"related": ["iss-00007"], "blocks": []}, tags=["家"])
    blocking = task("t-0002", "2026-11-01T00:00:00Z", scopes={"related": [], "blocks": ["iss-00007"]})
    other = task("t-0003", "2026-11-09T00:00:00Z")
    records = [related, blocking, other]

    def ids(filters: Filters) -> list[object]:
        return [record["id"] for record in records if matches(record, filters, NOW)]

    assert ids(Filters()) == ["t-0001", "t-0002", "t-0003"]
    assert ids(Filters(scope="iss-00007")) == ["t-0001", "t-0002"]
    assert ids(Filters(blocking=True)) == ["t-0002"]
    assert ids(Filters(overdue=True)) == ["t-0002"]
    assert ids(Filters(tag="家")) == ["t-0001"]
    assert ids(Filters(kind="decide")) == []
    assert ids(Filters(status="done")) == []
    assert ids(Filters(status="all")) == ["t-0001", "t-0002", "t-0003"]


def test_huge_spans_are_refused_without_overflow() -> None:
    from spec_dock.runtime.domain.todo_model import relative
    from spec_dock.runtime.domain.todo_settings import check_values

    assert relative("1000000000d") is None and relative("43200m") is not None
    with pytest.raises(TodoError):
        parse_when("1000000000d", now=NOW, tz=JST)
    assert check_values({"default_due": "99999999999999999999d"}) is not None


def test_a_date_uses_that_day_offset_across_daylight_saving(monkeypatch: pytest.MonkeyPatch) -> None:
    import time

    monkeypatch.setenv("TZ", "America/New_York")
    time.tzset()
    try:
        winter = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)
        assert parse_when("2026-07-01", now=winter, tz=None) == "2026-07-02T03:59:59Z"  # EDT, -04:00
        assert parse_when("2026-01-20", now=winter, tz=None) == "2026-01-21T04:59:59Z"  # EST, -05:00
    finally:
        monkeypatch.undo()
        time.tzset()
