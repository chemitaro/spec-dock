"""The human-task record `specdock.todo/v1`: its shape, IDs and state changes (epic-00547 D-02-D-04, D-07).

A record stays a JSON object: fields this version does not know are read and kept when it is rewritten. Every
writing command builds the changed record with `new_record` or `transition` and writes it only when `validate`
finds no problem. The same rules are written in CUE (`spec_dock/cue/todo/v1/todo.cue`); the fixtures under
`tests/fixtures/todo/` bind the two.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import datetime
import re
import secrets
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping, Sequence

SCHEMA: Final = "specdock.todo/v1"
ALPHABET: Final = "0123456789abcdefghjkmnpqrstvwxyz"  # Crockford base32 without i, l, o, u
ID_PATTERN: Final = re.compile(r"t-[0-9a-hjkmnp-tv-z]{4}")
SUBTASK_ID_PATTERN: Final = re.compile(r"(t-[0-9a-hjkmnp-tv-z]{4})\.([1-9][0-9]*)")
SCOPE_ID_PATTERN: Final = re.compile(r"(?:init|epic|iss)-(?:[0-9]{5}|[1-9][0-9]{5,})")
EFFORT_PATTERN: Final = re.compile(r"[1-9][0-9]*(?:m|h|d)")
OPTION_KEY_PATTERN: Final = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")
TIMESTAMP_PATTERN: Final = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z")
TITLE_MAX: Final = 200
ID_ATTEMPTS: Final = 20
KINDS: Final = ("decide", "check", "operate", "act", "todo", "checklist")
STATUSES: Final = ("open", "snoozed", "done", "cancelled")
CLOSED: Final = frozenset({"done", "cancelled"})
SUBTASK_STATUSES: Final = ("open", "done", "cancelled")
ACTIONS: Final = (
    "added",
    "updated",
    "done",
    "snoozed",
    "cancelled",
    "reopened",
    "subtask_added",
    "subtask_done",
    "subtask_cancelled",
    "subtask_reopened",
    "subtask_updated",
)
UPDATABLE: Final = (
    "title",
    "body",
    "kind",
    "due",
    "reply_to",
    "effort",
    "options",
    "recommendation",
    "scopes",
    "tags",
    "links",
)


@dataclass(frozen=True)
class Problem:
    """One reason a record does not have the v1 shape; `field` is the dotted path (`subtasks.1.status`)."""

    field: str
    message: str


class TodoError(Exception):
    """A human-task command stops before writing; the application layer renders it with its next step."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        exit_code: int = 3,
        details: dict[str, object] | None = None,
        next_step: str | None = None,
    ) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.exit_code = exit_code
        self.details = details or {}
        self.next_step = next_step


@dataclass
class _Checker:
    problems: list[Problem] = field(default_factory=list)

    def add(self, path: str, message: str) -> None:
        self.problems.append(Problem(path, message))


def is_timestamp(value: object) -> bool:
    if not isinstance(value, str) or TIMESTAMP_PATTERN.fullmatch(value) is None:
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return False
    return True


_NON_BLANK: Final = re.compile(r"[^\t\n\f\r ]")  # the complement of RE2's \s, as the CUE type writes =~"\\S"
RECORD_KEYS: Final = (
    "schema",
    "id",
    "title",
    "kind",
    "status",
    "created_at",
    "updated_at",
    "origin",
    "body",
    "options",
    "recommendation",
    "reply_to",
    "effort",
    "due",
    "snooze_until",
    "scopes",
    "links",
    "tags",
    "subtasks",
    "resolution",
    "history",
)
RESOLUTION_KEYS: Final = ("at", "by", "role", "choice", "note", "record")
SUBTASK_KEYS: Final = ("id", "title", "status", "created_at", "updated_at", "resolution")
HISTORY_KEYS: Final = ("at", "by", "role", "action", "target", "note", "fields")


def _text(value: object) -> bool:
    """A string with a character other than the ASCII spaces CUE's \\s matches."""
    return isinstance(value, str) and _NON_BLANK.search(value) is not None


def _present(check: _Checker, path: str, value: Mapping[str, object], keys: Sequence[str]) -> None:
    """Every v1 key must be present, even when its value may be null (CUE requires it the same way)."""
    for key in keys:
        if key not in value:
            check.add(f"{path}{key}", "is required")


def _title(check: _Checker, path: str, value: object) -> None:
    if not _text(value):
        check.add(path, "must be a non-blank string")
    elif "\n" in value or "\r" in value:  # type: ignore[operator]
        check.add(path, "must be one line")
    elif len(value) > TITLE_MAX:  # type: ignore[arg-type]
        check.add(path, f"must be at most {TITLE_MAX} characters")


def _time(check: _Checker, path: str, value: object, *, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    if not is_timestamp(value):
        check.add(path, "must be a UTC time YYYY-MM-DDTHH:MM:SSZ")


def _optional_text(check: _Checker, path: str, value: object) -> None:
    if value is not None and not isinstance(value, str):
        check.add(path, "must be a string or null")


def _strings(check: _Checker, path: str, value: object, *, pattern: re.Pattern[str] | None = None) -> None:
    if not isinstance(value, list):
        check.add(path, "must be a list of strings")
        return
    for index, item in enumerate(value):
        if not _text(item):
            check.add(f"{path}.{index}", "must be a non-blank string")
        elif pattern is not None and pattern.fullmatch(item) is None:
            check.add(f"{path}.{index}", f"must match {pattern.pattern}")


def _resolution(check: _Checker, path: str, value: object, *, status: str, keys: set[str] | None) -> None:
    closed = status in CLOSED
    if not closed:
        if value is not None:
            check.add(path, f"must be null while the status is {status}")
        return
    if not isinstance(value, dict):
        check.add(path, f"must be an object while the status is {status}")
        return
    _present(check, f"{path}.", value, RESOLUTION_KEYS)
    _time(check, f"{path}.at", value.get("at"))
    if value.get("by") not in ("agent", "human"):
        check.add(f"{path}.by", "must be agent or human")
    for name in ("role", "choice", "note", "record"):
        _optional_text(check, f"{path}.{name}", value.get(name))
    choice = value.get("choice")
    if isinstance(choice, str) and keys is None:
        check.add(f"{path}.choice", "must be null for a subtask")
    elif isinstance(choice, str) and choice not in keys:  # type: ignore[operator]
        check.add(f"{path}.choice", "must be the key of one of the options")
    if status == "cancelled" and not _text(value.get("note")):
        check.add(f"{path}.note", "must give the reason of the cancellation")


def validate(record: Mapping[str, object]) -> tuple[Problem, ...]:
    """Every shape problem of one v1 record; an empty tuple means it may be written (epic-00547 D-04)."""
    check = _Checker()
    if record.get("schema") != SCHEMA:
        check.add("schema", f"must be {SCHEMA}")
        return tuple(check.problems)
    _present(check, "", record, RECORD_KEYS)
    todo_id = record.get("id")
    if not isinstance(todo_id, str) or ID_PATTERN.fullmatch(todo_id) is None:
        check.add("id", "must be t- and four lowercase Crockford base32 letters")
    _title(check, "title", record.get("title"))
    kind = record.get("kind")
    if kind not in KINDS:
        check.add("kind", f"must be one of {', '.join(KINDS)}")
    status = record.get("status")
    if status not in STATUSES:
        check.add("status", f"must be one of {', '.join(STATUSES)}")
    for name in ("created_at", "updated_at", "due"):
        _time(check, name, record.get(name))
    origin = record.get("origin")
    agent = False
    if not isinstance(origin, dict) or origin.get("by") not in ("agent", "human"):
        check.add("origin.by", "must be agent or human")
    else:
        agent = origin["by"] == "agent"
        _present(check, "origin.", origin, ("role",))
        _optional_text(check, "origin.role", origin.get("role"))
        if agent and not _text(origin.get("role")):
            check.add("origin.role", "is required for an agent")
    if kind == "todo" and agent:
        check.add("kind", "todo is only for a task a person registered")
    for name in ("body", "reply_to", "effort"):
        _optional_text(check, name, record.get(name))
    if agent:
        for name in ("body", "reply_to"):
            if not _text(record.get(name)):
                check.add(name, "is required for an agent")
    effort = record.get("effort")
    if (agent or effort is not None) and (not isinstance(effort, str) or EFFORT_PATTERN.fullmatch(effort) is None):
        check.add("effort", "must be like 10m, 2h or 1d")
    keys = _options(check, record.get("options"))
    recommendation = record.get("recommendation")
    if recommendation is not None:
        if not isinstance(recommendation, dict):
            check.add("recommendation", "must be an object or null")
        else:
            if keys is None or recommendation.get("key") not in keys:
                check.add("recommendation.key", "must be the key of one of the options")
            if not _text(recommendation.get("reason")):
                check.add("recommendation.reason", "must be a non-blank string")
    if agent and kind == "decide":
        if keys is None or len(keys) < 2:
            check.add("options", "an agent's decide needs at least two options")
        if recommendation is None:
            check.add("recommendation", "an agent's decide needs a recommendation")
    snooze = record.get("snooze_until")
    if status == "snoozed":
        _time(check, "snooze_until", snooze)
    else:
        _time(check, "snooze_until", snooze, nullable=True)
    scopes = record.get("scopes")
    if not isinstance(scopes, dict):
        check.add("scopes", "must be an object with related and blocks")
    else:
        for name in ("related", "blocks"):
            _strings(check, f"scopes.{name}", scopes.get(name), pattern=SCOPE_ID_PATTERN)
    for name in ("links", "tags"):
        _strings(check, name, record.get(name))
    _subtasks(check, record.get("subtasks"), todo_id if isinstance(todo_id, str) else "")
    if isinstance(status, str) and status in STATUSES:
        _resolution(check, "resolution", record.get("resolution"), status=status, keys=keys)
    _history(check, record.get("history"))
    return tuple(check.problems)


def _options(check: _Checker, value: object) -> set[str] | None:
    if not isinstance(value, list):
        check.add("options", "must be a list")
        return None
    keys: set[str] = set()
    for index, item in enumerate(value):
        path = f"options.{index}"
        if not isinstance(item, dict):
            check.add(path, "must be an object with key and text")
            continue
        key = item.get("key")
        if not isinstance(key, str) or OPTION_KEY_PATTERN.fullmatch(key) is None:
            check.add(f"{path}.key", "must be letters, digits, _, . or - and start with a letter or digit")
        elif key in keys:
            check.add(f"{path}.key", "must not repeat another option's key")
        else:
            keys.add(key)
        if not _text(item.get("text")):
            check.add(f"{path}.text", "must be a non-blank string")
    return keys


def _subtasks(check: _Checker, value: object, parent: str) -> None:
    if not isinstance(value, list):
        check.add("subtasks", "must be a list")
        return
    seen: set[str] = set()
    for index, item in enumerate(value):
        path = f"subtasks.{index}"
        if not isinstance(item, dict):
            check.add(path, "must be an object")
            continue
        _present(check, f"{path}.", item, SUBTASK_KEYS)
        subtask_id = item.get("id")
        matched = SUBTASK_ID_PATTERN.fullmatch(subtask_id) if isinstance(subtask_id, str) else None
        if matched is None or matched.group(1) != parent:
            check.add(f"{path}.id", "must be the parent's ID and .<number>")
        elif subtask_id in seen:
            check.add(f"{path}.id", "must not repeat another subtask's ID")
        else:
            seen.add(subtask_id)  # type: ignore[arg-type]
        _title(check, f"{path}.title", item.get("title"))
        status = item.get("status")
        if status not in SUBTASK_STATUSES:
            check.add(f"{path}.status", f"must be one of {', '.join(SUBTASK_STATUSES)}")
        for name in ("created_at", "updated_at"):
            _time(check, f"{path}.{name}", item.get(name))
        if isinstance(status, str) and status in SUBTASK_STATUSES:
            _resolution(check, f"{path}.resolution", item.get("resolution"), status=status, keys=None)


def _history(check: _Checker, value: object) -> None:
    if not isinstance(value, list):
        check.add("history", "must be a list")
        return
    for index, item in enumerate(value):
        path = f"history.{index}"
        if not isinstance(item, dict):
            check.add(path, "must be an object")
            continue
        _present(check, f"{path}.", item, HISTORY_KEYS)
        _time(check, f"{path}.at", item.get("at"))
        if item.get("by") not in ("agent", "human"):
            check.add(f"{path}.by", "must be agent or human")
        if item.get("action") not in ACTIONS:
            check.add(f"{path}.action", "must be a known action")
        for name in ("role", "target", "note"):
            _optional_text(check, f"{path}.{name}", item.get(name))
        fields_value = item.get("fields")
        if not isinstance(fields_value, list) or not all(isinstance(name, str) for name in fields_value):
            check.add(f"{path}.fields", "must be a list of strings")


def agent_missing(record: Mapping[str, object]) -> tuple[str, ...]:
    """The names of the fields an agent must give and did not (epic-00547 R-03 acceptance)."""
    origin = record.get("origin")
    if not isinstance(origin, dict) or origin.get("by") != "agent":
        return ()
    missing = [name for name in ("role",) if not _text(origin.get("role"))]
    missing += [name for name in ("body", "reply_to", "effort") if record.get(name) in (None, "")]
    if record.get("kind") == "decide":
        if not record.get("options"):
            missing.append("options")
        if record.get("recommendation") is None:
            missing.append("recommendation")
    if record.get("kind") is None:
        missing.append("kind")
    return tuple(missing)


def require_valid(record: Mapping[str, object]) -> None:
    """Stop with TODO_INVALID, naming each problem and each missing agent field."""
    problems = validate(record)
    if problems:
        raise TodoError(
            "TODO_INVALID",
            "the task would not have the specdock.todo/v1 shape: "
            + "; ".join(f"{item.field} {item.message}" for item in problems),
            exit_code=2,
            details={
                "problems": [{"field": item.field, "message": item.message} for item in problems],
                "missing": list(agent_missing(record)),
            },
        )


def new_id(taken: Iterable[str], *, choose: Callable[[str], str] = secrets.choice) -> str:
    """A new `t-xxxx` not in `taken` (every record name, closed ones included)."""
    names = set(taken)
    for _ in range(ID_ATTEMPTS):
        candidate = "t-" + "".join(choose(ALPHABET) for _ in range(4))
        if candidate not in names:
            return candidate
    raise TodoError(
        "TODO_ID_EXHAUSTED",
        f"{ID_ATTEMPTS} new task IDs in a row were already taken",
        details={"attempts": ID_ATTEMPTS},
        next_step="Run the same command again.",
    )


def normalize_id(value: str) -> str:
    """A task or subtask ID from input, case-insensitively; anything else stops with TODO_INVALID."""
    text = value.strip().lower()
    if ID_PATTERN.fullmatch(text) is None and SUBTASK_ID_PATTERN.fullmatch(text) is None:
        raise TodoError(
            "TODO_INVALID",
            f"{value!r} is not a task ID (t-xxxx) or a subtask ID (t-xxxx.N)",
            exit_code=2,
            details={"problems": [{"field": "id", "message": "must be t-xxxx or t-xxxx.N"}], "missing": []},
        )
    return text


def parent_id(todo_id: str) -> str:
    return todo_id.split(".", 1)[0]


def _history_entry(
    action: str,
    *,
    now: str,
    by: str,
    role: str | None,
    target: str | None = None,
    note: str | None = None,
    fields_changed: Sequence[str] = (),
) -> dict[str, object]:
    return {
        "at": now,
        "by": by,
        "role": role,
        "action": action,
        "target": target,
        "note": note,
        "fields": list(fields_changed),
    }


def new_record(
    todo_id: str,
    *,
    title: str,
    by: str,
    role: str | None,
    kind: str | None,
    now: str,
    due: str,
    body: str | None = None,
    options: Sequence[Mapping[str, object]] = (),
    recommendation: Mapping[str, object] | None = None,
    reply_to: str | None = None,
    effort: str | None = None,
    related: Sequence[str] = (),
    blocks: Sequence[str] = (),
    links: Sequence[str] = (),
    tags: Sequence[str] = (),
    items: Sequence[str] = (),
) -> dict[str, object]:
    """A new open record with every v1 field; a person needs only the title (epic-00547 D-02)."""
    record: dict[str, object] = {
        "schema": SCHEMA,
        "id": todo_id,
        "title": title,
        "kind": kind if kind is not None else ("todo" if by == "human" else None),
        "status": "open",
        "created_at": now,
        "updated_at": now,
        "origin": {"by": by, "role": role},
        "body": body,
        "options": [dict(item) for item in options],
        "recommendation": dict(recommendation) if recommendation is not None else None,
        "reply_to": reply_to,
        "effort": effort,
        "due": due,
        "snooze_until": None,
        "scopes": {"related": list(dict.fromkeys(related)), "blocks": list(dict.fromkeys(blocks))},
        "links": list(links),
        "tags": list(dict.fromkeys(tags)),
        "subtasks": [],
        "resolution": None,
        "history": [_history_entry("added", now=now, by=by, role=role)],
    }
    record["subtasks"] = [_subtask(f"{todo_id}.{number}", item, now) for number, item in enumerate(items, start=1)]
    require_valid(record)
    return record


def _subtask(subtask_id: str, title: str, now: str) -> dict[str, object]:
    return {
        "id": subtask_id,
        "title": title,
        "status": "open",
        "created_at": now,
        "updated_at": now,
        "resolution": None,
    }


def _subtask_list(record: Mapping[str, object]) -> list[dict[str, object]]:
    value = record.get("subtasks")
    return value if isinstance(value, list) else []  # type: ignore[return-value]


def open_subtasks(record: Mapping[str, object]) -> list[dict[str, object]]:
    return [item for item in _subtask_list(record) if item.get("status") == "open"]


def _resolution_value(
    now: str, by: str, role: str | None, *, choice: str | None, note: str | None, record_ref: str | None
) -> dict[str, object]:
    return {"at": now, "by": by, "role": role, "choice": choice, "note": note, "record": record_ref}


def _state_error(todo_id: str, status: object, action: str) -> TodoError:
    return TodoError(
        "TODO_STATE_INVALID",
        f"{todo_id} is {status}; it cannot be {action}",
        details={"id": todo_id, "status": status, "action": action},
        next_step=f"spec-dock todo show {todo_id}",
    )


def transition(
    record: Mapping[str, object],
    action: str,
    *,
    now: str,
    by: str,
    role: str | None,
    target: str | None = None,
    note: str | None = None,
    choice: str | None = None,
    record_ref: str | None = None,
    until: str | None = None,
    due: str | None = None,
    include_subtasks: bool = False,
    title: str | None = None,
    changes: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """The record after one change, checked with `validate`; the input is never changed.

    `action` is done, cancel, snooze, reopen, update or subtask_add. `target` names a subtask
    (`t-xxxx.N`) for done, cancel, reopen and update; None means the task itself.
    """
    result = copy.deepcopy(dict(record))
    todo_id = str(result.get("id"))
    history = result.setdefault("history", [])
    assert isinstance(history, list)
    if target is not None and target != todo_id:
        if choice is not None or include_subtasks:
            raise TodoError(
                "TODO_INVALID",
                "a subtask takes no --choice or --include-subtasks",
                exit_code=2,
                details={"problems": [{"field": "id", "message": "names a subtask"}], "missing": []},
            )
        _subtask_transition(
            result,
            history,
            action,
            target=target,
            now=now,
            by=by,
            role=role,
            note=note,
            title=title,
            record_ref=record_ref,
        )
        require_valid(result)
        return result
    status = result.get("status")
    if action in ("done", "cancel"):
        if status in CLOSED:
            raise _state_error(todo_id, status, "closed again")
        closing = "done" if action == "done" else "cancelled"
        if action == "cancel" and not _text(note):
            raise TodoError(
                "TODO_INVALID",
                "a cancellation needs a reason (--reason)",
                exit_code=2,
                details={"problems": [{"field": "resolution.note", "message": "is required"}], "missing": []},
            )
        remaining = open_subtasks(result)
        if remaining and not include_subtasks:
            raise TodoError(
                "TODO_SUBTASKS_OPEN",
                f"{todo_id} still has {len(remaining)} open subtasks",
                details={"open_subtasks": [item["id"] for item in remaining]},
                next_step=f"Close the subtasks first, or run spec-dock todo {action} {todo_id} --include-subtasks.",
            )
        for item in remaining:
            item["status"] = closing
            item["updated_at"] = now
            item["resolution"] = _resolution_value(now, by, role, choice=None, note=note, record_ref=record_ref)
            history.append(_history_entry(f"subtask_{closing}", now=now, by=by, role=role, target=str(item["id"])))
        result["status"] = closing
        result["snooze_until"] = None
        result["resolution"] = _resolution_value(now, by, role, choice=choice, note=note, record_ref=record_ref)
        history.append(_history_entry(closing, now=now, by=by, role=role, note=note))
    elif action == "snooze":
        if status in CLOSED:
            raise _state_error(todo_id, status, "snoozed")
        result["status"] = "snoozed"
        result["snooze_until"] = until
        if due is not None:
            result["due"] = due
        history.append(_history_entry("snoozed", now=now, by=by, role=role, note=note))
    elif action == "reopen":
        if status not in CLOSED:
            raise _state_error(todo_id, status, "reopened")
        previous = result.get("resolution")
        result["status"] = "open"
        result["resolution"] = None
        result["snooze_until"] = None
        if due is not None:
            result["due"] = due
        entry = _history_entry("reopened", now=now, by=by, role=role, note=note)
        entry["resolution"] = previous  # the earlier answer stays in history (epic-00547 D-12)
        history.append(entry)
    elif action == "subtask_add":
        if status in CLOSED:
            raise TodoError(
                "TODO_PARENT_CLOSED",
                f"{todo_id} is {status}; reopen it before adding a subtask",
                details={"id": todo_id, "status": status},
                next_step=f"spec-dock todo reopen {todo_id}",
            )
        subtasks = result.setdefault("subtasks", [])
        assert isinstance(subtasks, list)
        numbers = [
            int(matched.group(2))
            for item in subtasks
            if isinstance(item, dict)
            and isinstance(item.get("id"), str)
            and (matched := SUBTASK_ID_PATTERN.fullmatch(item["id"])) is not None
        ]
        subtask_id = f"{todo_id}.{max(numbers, default=0) + 1}"
        subtasks.append(_subtask(subtask_id, title or "", now))
        history.append(_history_entry("subtask_added", now=now, by=by, role=role, target=subtask_id))
    elif action == "update":
        changed = [name for name, value in (changes or {}).items() if result.get(name) != value]
        if not changed:
            return dict(copy.deepcopy(dict(record)))
        for name in changed:
            result[name] = copy.deepcopy((changes or {})[name])
        history.append(_history_entry("updated", now=now, by=by, role=role, note=note, fields_changed=changed))
    else:
        raise ValueError(f"unknown task action {action!r}")
    result["updated_at"] = now
    require_valid(result)
    return result


def _subtask_transition(
    result: dict[str, object],
    history: list[object],
    action: str,
    *,
    target: str,
    now: str,
    by: str,
    role: str | None,
    note: str | None,
    title: str | None,
    record_ref: str | None = None,
) -> None:
    todo_id = str(result.get("id"))
    item = next((entry for entry in _subtask_list(result) if entry.get("id") == target), None)
    if item is None:
        raise TodoError(
            "TODO_NOT_FOUND",
            f"{todo_id} has no subtask {target}",
            details={"id": target},
            next_step=f"spec-dock todo show {todo_id}",
        )
    status = item.get("status")
    if action in ("done", "cancel"):
        if status in CLOSED:
            raise _state_error(target, status, "closed again")
        if action == "cancel" and not _text(note):
            raise TodoError(
                "TODO_INVALID",
                "a cancellation needs a reason (--reason)",
                exit_code=2,
                details={"problems": [{"field": "resolution.note", "message": "is required"}], "missing": []},
            )
        closing = "done" if action == "done" else "cancelled"
        item["status"] = closing
        item["resolution"] = _resolution_value(now, by, role, choice=None, note=note, record_ref=record_ref)
        history.append(_history_entry(f"subtask_{closing}", now=now, by=by, role=role, target=target, note=note))
    elif action == "reopen":
        if result.get("status") in CLOSED:
            raise TodoError(
                "TODO_PARENT_CLOSED",
                f"{todo_id} is {result.get('status')}; reopen it before reopening its subtask",
                details={"id": todo_id, "status": result.get("status")},
                next_step=f"spec-dock todo reopen {todo_id}",
            )
        if status not in CLOSED:
            raise _state_error(target, status, "reopened")
        previous = item.get("resolution")
        item["status"] = "open"
        item["resolution"] = None
        entry = _history_entry("subtask_reopened", now=now, by=by, role=role, target=target, note=note)
        entry["resolution"] = previous
        history.append(entry)
    elif action == "update":
        if title is None or title == item.get("title"):
            return
        item["title"] = title
        history.append(
            _history_entry(
                "subtask_updated", now=now, by=by, role=role, target=target, note=note, fields_changed=["title"]
            )
        )
    else:
        raise TodoError(
            "TODO_INVALID",
            f"a subtask cannot be {action}d; only done, cancel, reopen and update take a subtask ID",
            exit_code=2,
            details={"problems": [{"field": "id", "message": "must name the task, not a subtask"}], "missing": []},
        )
    item["updated_at"] = now
    result["updated_at"] = now
