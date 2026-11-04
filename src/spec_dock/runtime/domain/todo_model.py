"""Pure rules read from human-task records: due times, derived states, order, counts, filters (epic-00547 D-08, D-09).

The current time is always an argument. Readers decide `effective_status` without rewriting the file, so a
read-only command never writes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone, tzinfo
import re
from typing import TYPE_CHECKING, Final

from spec_dock.runtime.domain.todo_record import CLOSED, TodoError, open_subtasks

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

DUE_SOON: Final = timedelta(hours=24)
MAX_RELATIVE: Final = timedelta(days=30)
_RELATIVE = re.compile(r"([1-9][0-9]*)(m|h|d)")
_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_UNITS: Final = {"m": "minutes", "h": "hours", "d": "days"}


def format_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_time(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def relative(text: str) -> timedelta | None:
    """`30m`, `4h`, `2d` as a duration up to 30 days; anything else is None."""
    matched = _RELATIVE.fullmatch(text)
    if matched is None or len(matched.group(1)) > 6:  # 30 days is at most 43200 minutes; longer cannot fit
        return None
    span = timedelta(**{_UNITS[matched.group(2)]: int(matched.group(1))})
    return span if span <= MAX_RELATIVE else None


def _invalid(text: str, reason: str, field: str) -> TodoError:
    return TodoError(
        "TODO_INVALID",
        f"{text!r} {reason}",
        exit_code=2,
        details={"problems": [{"field": field, "message": reason}], "missing": []},
    )


def parse_when(text: str, *, now: datetime, tz: tzinfo | None, field: str = "due") -> str:
    """A `--due`/`--until` value as UTC `YYYY-MM-DDTHH:MM:SSZ`; past or unreadable values stop with TODO_INVALID."""
    value = text.strip()
    span = relative(value)
    if span is not None:
        moment = now + span
    elif _DATE.fullmatch(value):
        try:
            day = datetime.strptime(value, "%Y-%m-%d")
        except ValueError as error:
            raise _invalid(text, "is not a real date", field) from error
        end = day.replace(hour=23, minute=59, second=59)
        # Without a fixed zone, the PC's own offset of that day (not of today) applies across daylight saving.
        moment = end.replace(tzinfo=tz) if tz is not None else end.astimezone()
    else:
        try:
            moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as error:
            raise _invalid(
                text, "must be 30m, 4h, 2d (up to 30d), YYYY-MM-DD or ISO 8601 with a zone", field
            ) from error
        if moment.tzinfo is None:
            raise _invalid(text, "needs a time zone (Z or +09:00)", field)
    if moment <= now:
        raise _invalid(text, "is not in the future", field)
    return format_time(moment)


def _closed(record: Mapping[str, object]) -> bool:
    return record.get("status") in CLOSED


def effective_status(record: Mapping[str, object], now: datetime) -> str:
    status = str(record.get("status"))
    until = record.get("snooze_until")
    if status == "snoozed" and isinstance(until, str):
        try:
            if parse_time(until) <= now:
                return "open"
        except ValueError:
            return status
    return status


def _due(record: Mapping[str, object]) -> datetime | None:
    value = record.get("due")
    try:
        return parse_time(value) if isinstance(value, str) else None
    except ValueError:
        return None


def is_blocking(record: Mapping[str, object]) -> bool:
    scopes = record.get("scopes")
    blocks = scopes.get("blocks") if isinstance(scopes, dict) else None
    return not _closed(record) and bool(blocks)


def derived(record: Mapping[str, object], now: datetime) -> dict[str, object]:
    """The states readers show next to a record (epic-00547 D-08, D-13)."""
    status = effective_status(record, now)
    due = _due(record)
    overdue = status == "open" and due is not None and due < now
    subtasks = record.get("subtasks") if isinstance(record.get("subtasks"), list) else []
    remaining = open_subtasks(record)
    return {
        "effective_status": status,
        "overdue": overdue,
        "due_soon": status == "open" and not overdue and due is not None and due - now <= DUE_SOON,
        "blocking": is_blocking(record),
        "parent_closable": bool(subtasks) and not remaining and not _closed(record),
        "open_subtasks": [{"id": item.get("id"), "title": item.get("title")} for item in remaining],
        "subtask_counts": {"open": len(remaining), "total": len(subtasks)},  # type: ignore[arg-type]
    }


def _group(record: Mapping[str, object], now: datetime) -> int:
    view = derived(record, now)
    if _closed(record):
        return 5
    if view["effective_status"] == "snoozed":
        return 4
    if view["overdue"]:
        return 0
    if view["due_soon"]:
        return 1
    if view["blocking"]:
        return 2
    return 3


def order(records: Iterable[Mapping[str, object]], now: datetime) -> list[Mapping[str, object]]:
    """Overdue, due soon, blocking, later, snoozed, then closed (newest first) (epic-00547 D-08)."""

    def key(record: Mapping[str, object]) -> tuple[object, ...]:
        group = _group(record, now)
        resolution = record.get("resolution")
        closed_at = str(resolution.get("at")) if isinstance(resolution, dict) else ""
        if group == 5:
            # Newest closed first: invert the timestamp's characters so a plain ascending sort works.
            return (group, tuple(-ord(char) for char in closed_at), str(record.get("id")))
        return (group, str(record.get("due")), str(record.get("created_at")), str(record.get("id")))

    return sorted(records, key=key)


def tally(records: Iterable[Mapping[str, object]], now: datetime) -> dict[str, int]:
    """Parent tasks that are open (snoozed included), blocking, overdue and snoozed (epic-00547 D-08, D-15)."""
    views = [(record, derived(record, now)) for record in records]
    return {
        "open": sum(1 for record, _view in views if not _closed(record)),
        "blocking": sum(1 for _record, view in views if view["blocking"]),
        "overdue": sum(1 for _record, view in views if view["overdue"]),
        "snoozed": sum(1 for _record, view in views if view["effective_status"] == "snoozed"),
    }


@dataclass(frozen=True)
class LimitCounts:
    agent_parents: int
    open_subtasks: dict[str, int]


def count_limits(records: Iterable[Mapping[str, object]]) -> LimitCounts:
    """Open agent tasks that are not checklists, and each task's open subtasks (epic-00547 D-09)."""
    agent = 0
    subtasks: dict[str, int] = {}
    for record in records:
        origin = record.get("origin")
        by = origin.get("by") if isinstance(origin, dict) else None
        if not _closed(record) and by == "agent" and record.get("kind") != "checklist":
            agent += 1
        subtasks[str(record.get("id"))] = len(open_subtasks(record))
    return LimitCounts(agent, subtasks)


@dataclass(frozen=True)
class Filters:
    """`todo list` filters; status `open` (the default) means effective_status open, `all` means every task."""

    status: str = "open"
    scope: str | None = None
    kind: str | None = None
    tag: str | None = None
    blocking: bool = False
    overdue: bool = False
    repositories: tuple[str, ...] = ()  # `--repository` keys (iss-00550); matching rows is the aggregator's job

    def to_json(self) -> dict[str, object]:
        return {
            "status": self.status,
            "scope": self.scope,
            "kind": self.kind,
            "tag": self.tag,
            "blocking": self.blocking,
            "overdue": self.overdue,
            "repositories": list(self.repositories),
        }


def matches(record: Mapping[str, object], filters: Filters, now: datetime) -> bool:
    view = derived(record, now)
    if filters.status != "all":
        current = view["effective_status"] if filters.status in ("open", "snoozed") else record.get("status")
        if current != filters.status:
            return False
    scopes = record.get("scopes")
    if filters.scope is not None:
        linked = [*scopes.get("related", []), *scopes.get("blocks", [])] if isinstance(scopes, dict) else []
        if filters.scope not in linked:
            return False
    if filters.kind is not None and record.get("kind") != filters.kind:
        return False
    tags = record.get("tags")
    if filters.tag is not None and (not isinstance(tags, list) or filters.tag not in tags):
        return False
    if filters.blocking and not view["blocking"]:
        return False
    return not (filters.overdue and not view["overdue"])
