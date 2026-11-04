"""The human-task record `specdock.todo/v1`: shape checks, IDs and state changes (iss-00549 D-01)."""

from __future__ import annotations

import copy
import itertools

import pytest

from spec_dock.runtime.domain import todo_record
from spec_dock.runtime.domain.todo_record import TodoError, new_id, new_record, transition, validate

NOW = "2026-11-04T10:00:00Z"
LATER = "2026-11-04T11:00:00Z"


def human(**changes: object) -> dict[str, object]:
    record = new_record(
        "t-7k3m", title="窓口に電話する", by="human", role=None, kind=None, now=NOW, due="2026-11-04T14:00:00Z"
    )
    record.update(changes)
    return record


def agent_decide() -> dict[str, object]:
    return new_record(
        "t-abcd",
        title="方式を選ぶ",
        by="agent",
        role="iss-00549 の担当",
        kind="decide",
        now=NOW,
        due="2026-11-04T14:00:00Z",
        body="A と B のどちらにするか",
        options=[{"key": "a", "text": "A"}, {"key": "b", "text": "B"}],
        recommendation={"key": "a", "reason": "速い"},
        reply_to="Orca の担当",
        effort="10m",
    )


def fields(record: dict[str, object]) -> set[str]:
    return {problem.field for problem in validate(record)}


def test_a_human_record_needs_only_a_title_and_fills_every_field() -> None:
    record = human()
    assert validate(record) == ()
    assert record["kind"] == "todo" and record["status"] == "open" and record["schema"] == "specdock.todo/v1"
    assert record["scopes"] == {"related": [], "blocks": []} and record["subtasks"] == []
    assert record["body"] is None and record["resolution"] is None
    assert [entry["action"] for entry in record["history"]] == ["added"]  # type: ignore[attr-defined]


def test_an_agent_record_names_every_missing_required_field() -> None:
    with pytest.raises(TodoError) as raised:
        new_record("t-abcd", title="x", by="agent", role=None, kind="decide", now=NOW, due=LATER)
    assert raised.value.code == "TODO_INVALID" and raised.value.exit_code == 2
    assert set(raised.value.details["missing"]) == {  # type: ignore[call-overload]
        "role",
        "body",
        "reply_to",
        "effort",
        "options",
        "recommendation",
    }
    assert validate(agent_decide()) == ()


@pytest.mark.parametrize(
    ("change", "field"),
    [
        ({"id": "T-7K3M"}, "id"),
        ({"id": "t-7k3u"}, "id"),
        ({"title": "  "}, "title"),
        ({"title": "a\nb"}, "title"),
        ({"title": "x" * 201}, "title"),
        ({"kind": "other"}, "kind"),
        ({"status": "closed"}, "status"),
        ({"due": "2026-11-04 14:00"}, "due"),
        ({"due": "2026-13-04T14:00:00Z"}, "due"),
        ({"status": "snoozed"}, "snooze_until"),
        ({"status": "done"}, "resolution"),
        ({"scopes": {"related": ["iss-531"], "blocks": []}}, "scopes.related.0"),
        ({"tags": [""]}, "tags.0"),
        ({"effort": "0m"}, "effort"),
    ],
)
def test_shape_problems_name_the_field(change: dict[str, object], field: str) -> None:
    assert field in fields(human(**change))


def test_cross_field_rules() -> None:
    record = agent_decide()
    record["recommendation"] = {"key": "z", "reason": "r"}
    assert "recommendation.key" in fields(record)
    record = agent_decide()
    record["options"] = [{"key": "a", "text": "A"}, {"key": "a", "text": "B"}]
    assert "options.1.key" in fields(record)
    record = agent_decide()
    record["kind"] = "todo"
    assert "kind" in fields(record)
    record = human()
    record["subtasks"] = [
        {"id": "t-zzzz.1", "title": "s", "status": "open", "created_at": NOW, "updated_at": NOW, "resolution": None}
    ]
    assert "subtasks.0.id" in fields(record)


def test_unknown_fields_are_kept_and_not_errors() -> None:
    record = human(future={"x": 1})
    assert validate(record) == ()
    done = transition(record, "done", now=LATER, by="human", role=None, note="済んだ")
    assert done["future"] == {"x": 1} and done["status"] == "done"


def test_ids_avoid_taken_names_and_give_up_after_twenty_collisions() -> None:
    letters = iter("0000" + "0001")
    assert new_id({"t-0000"}, choose=lambda alphabet: next(letters)) == "t-0001"
    with pytest.raises(TodoError) as raised:
        new_id({"t-0000"}, choose=lambda alphabet: "0")
    assert raised.value.code == "TODO_ID_EXHAUSTED"
    assert todo_record.ID_PATTERN.fullmatch(new_id(set()))


def test_done_writes_the_resolution_and_history_and_refuses_twice() -> None:
    record = agent_decide()
    done = transition(record, "done", now=LATER, by="human", role=None, choice="a", note="A で", record_ref="log.md")
    assert done["resolution"] == {
        "at": LATER,
        "by": "human",
        "role": None,
        "choice": "a",
        "note": "A で",
        "record": "log.md",
    }
    assert done["history"][-1]["action"] == "done" and validate(done) == ()  # type: ignore[index]
    assert record["status"] == "open"  # the input is not changed
    with pytest.raises(TodoError) as raised:
        transition(done, "done", now=LATER, by="human", role=None)
    assert raised.value.code == "TODO_STATE_INVALID"
    reopened = transition(done, "reopen", now=LATER, by="human", role=None)
    assert reopened["status"] == "open" and reopened["resolution"] is None and validate(reopened) == ()
    with pytest.raises(TodoError) as raised:
        transition(record, "done", now=LATER, by="human", role=None, choice="z")
    assert raised.value.code == "TODO_INVALID"


def test_cancel_needs_a_reason_and_snooze_sets_the_time() -> None:
    with pytest.raises(TodoError):
        transition(human(), "cancel", now=LATER, by="human", role=None, note=" ")
    snoozed = transition(human(), "snooze", now=LATER, by="human", role=None, until="2026-11-05T00:00:00Z")
    assert snoozed["status"] == "snoozed" and snoozed["snooze_until"] == "2026-11-05T00:00:00Z"
    done = transition(snoozed, "done", now=LATER, by="human", role=None)
    assert done["snooze_until"] is None and validate(done) == ()


def test_subtasks_number_up_close_one_by_one_and_block_the_parent() -> None:
    record = human()
    for title in ("一", "二", "三"):
        record = transition(record, "subtask_add", now=LATER, by="human", role=None, title=title)
    assert [item["id"] for item in record["subtasks"]] == ["t-7k3m.1", "t-7k3m.2", "t-7k3m.3"]  # type: ignore[attr-defined]
    record = transition(record, "cancel", now=LATER, by="human", role=None, target="t-7k3m.3", note="不要")
    record = transition(record, "subtask_add", now=LATER, by="human", role=None, title="四")
    assert record["subtasks"][-1]["id"] == "t-7k3m.4"  # type: ignore[index]
    with pytest.raises(TodoError) as raised:
        transition(record, "done", now=LATER, by="human", role=None)
    assert raised.value.code == "TODO_SUBTASKS_OPEN"
    assert raised.value.details["open_subtasks"] == ["t-7k3m.1", "t-7k3m.2", "t-7k3m.4"]
    closed = transition(record, "done", now=LATER, by="human", role=None, include_subtasks=True)
    assert {item["status"] for item in closed["subtasks"]} == {"done", "cancelled"}  # type: ignore[attr-defined]
    assert validate(closed) == ()
    with pytest.raises(TodoError) as raised:
        transition(closed, "subtask_add", now=LATER, by="human", role=None, title="五")
    assert raised.value.code == "TODO_PARENT_CLOSED"
    with pytest.raises(TodoError) as raised:
        transition(closed, "reopen", now=LATER, by="human", role=None, target="t-7k3m.1")
    assert raised.value.code == "TODO_PARENT_CLOSED"


def test_update_records_the_changed_fields_only() -> None:
    record = human()
    changed = transition(record, "update", now=LATER, by="human", role=None, changes={"title": "新しい題名"})
    assert changed["history"][-1]["fields"] == ["title"]  # type: ignore[index]
    same = transition(record, "update", now=LATER, by="human", role=None, changes={"title": "窓口に電話する"})
    assert same == record


def test_validation_is_independent_of_the_input_object() -> None:
    record = human()
    snapshot = copy.deepcopy(record)
    for _ in itertools.repeat(None, 2):
        validate(record)
    assert record == snapshot


def test_a_subtask_keeps_its_record_and_refuses_task_only_options() -> None:
    record = transition(human(), "subtask_add", now=LATER, by="human", role=None, title="一")
    done = transition(record, "done", now=LATER, by="human", role=None, target="t-7k3m.1", record_ref="log.md")
    assert done["subtasks"][0]["resolution"]["record"] == "log.md"  # type: ignore[index]
    for options in ({"choice": "a"}, {"include_subtasks": True}):
        with pytest.raises(TodoError) as raised:
            transition(record, "done", now=LATER, by="human", role=None, target="t-7k3m.1", **options)  # type: ignore[arg-type]
        assert raised.value.code == "TODO_INVALID"
    reopened = transition(done, "reopen", now=LATER, by="human", role=None, target="t-7k3m.1")
    assert reopened["history"][-1]["resolution"]["record"] == "log.md"  # type: ignore[index]


def test_reopen_keeps_the_earlier_answer_in_history() -> None:
    done = transition(agent_decide(), "done", now=LATER, by="human", role=None, choice="a", record_ref="log.md")
    reopened = transition(done, "reopen", now=LATER, by="human", role=None)
    entry = reopened["history"][-1]  # type: ignore[index]
    assert entry["action"] == "reopened" and entry["resolution"]["choice"] == "a"  # type: ignore[index]
    assert entry["resolution"]["record"] == "log.md" and validate(reopened) == ()  # type: ignore[index]
