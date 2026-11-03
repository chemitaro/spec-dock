"""The dashboard's reading of a structure snapshot document: versions 1 and 2 and the pull request fields (D-19).

The dashboard reads the file itself so that it can tell a missing, an unreadable and an unknown-version snapshot
apart (epic-00427 D-12); `SnapshotStore.load()` reports all three as absent. The structure part goes through
`StructureSnapshot.from_json`, so the structure rules are not copied here. The pull request fields of version 2
are parsed here until the snapshot owner (iss-00537) exposes them; whichever merges later folds one into the other.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Final, Literal, cast

from spec_dock.runtime.domain.canonical_structure import (
    SNAPSHOT_VERSION,
    SnapshotFormatError,
    StructureSnapshot,
    branch_names_scope,
    parse_timestamp,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

KNOWN_VERSIONS: Final = frozenset({1, 2})
PULL_REQUEST_KEYS: Final = ("pull_requests", "pull_requests_error", "pull_requests_fetched_at")
PULL_REQUEST_MAX_AGE: Final = timedelta(minutes=30)

PullRequestState = Literal["open", "closed", "merged"]
Mergeable = Literal["mergeable", "conflicting", "unknown"]
Checks = Literal["success", "failure", "pending", "none"]
PullRequestStatus = Literal["fresh", "stale", "unknown"]

_STATES: Final = frozenset({"open", "closed", "merged"})
_MERGEABLE: Final = frozenset({"mergeable", "conflicting", "unknown"})
_CHECKS: Final = frozenset({"success", "failure", "pending", "none"})
_PR_FIELDS: Final = frozenset({
    "number",
    "state",
    "is_draft",
    "head_ref_name",
    "mergeable",
    "checks",
    "created_at",
    "merged_at",
    "closed_at",
    "url",
})


class SnapshotUnreadable(ValueError):
    """The document is malformed, of another repository, or has no integer version."""


class SnapshotUnsupported(ValueError):
    """The document has an integer version this SpecDock does not know."""

    def __init__(self, version: int) -> None:
        super().__init__(f"structure snapshot version {version} is not supported")
        self.version = version


@dataclass(frozen=True)
class PullRequest:
    number: int
    state: PullRequestState
    is_draft: bool
    head_ref_name: str
    mergeable: Mergeable
    checks: Checks
    created_at: str
    merged_at: str | None
    closed_at: str | None
    url: str


@dataclass(frozen=True)
class PullRequestsError:
    code: str
    message: str
    at: str


@dataclass(frozen=True)
class PullRequestInfo:
    """What the snapshot says about pull requests; `fetched_at` None means never fetched (or version 1)."""

    version: int
    fetched_at: str | None
    error: PullRequestsError | None
    items: Mapping[int, PullRequest]

    def status(self, now: datetime) -> PullRequestStatus:
        """unknown: version 1, never fetched, or the last fetch is more than 30 minutes old (no values are used).
        stale: the latest fetch failed but the last values are recent; they are used and marked. fresh: otherwise."""
        if self.version < 2 or self.fetched_at is None:
            return "unknown"
        if now - parse_timestamp(self.fetched_at) > PULL_REQUEST_MAX_AGE:
            return "unknown"
        return "stale" if self.error is not None else "fresh"

    def for_scope(self, scope_id: str) -> PullRequest | None:
        """The Scope's pull request by branch name: open first, then the newest created, then the highest number."""
        matches = [item for item in self.items.values() if branch_names_scope(item.head_ref_name, scope_id)]
        if not matches:
            return None
        return min(
            matches,
            key=lambda item: (item.state != "open", -parse_timestamp(item.created_at).timestamp(), -item.number),
        )


NO_PULL_REQUESTS: Final = PullRequestInfo(1, None, None, {})


@dataclass(frozen=True)
class ParsedSnapshot:
    snapshot: StructureSnapshot
    pull_requests: PullRequestInfo


def parse_snapshot_document(payload: object, *, repository: str) -> ParsedSnapshot:
    """Parse a snapshot document of version 1 or 2 for `repository` (host/owner/name)."""
    if not isinstance(payload, dict):
        raise SnapshotUnreadable("structure snapshot is not a JSON object")
    document = cast("dict[str, object]", payload)
    version = document.get("version")
    if type(version) is not int:
        raise SnapshotUnreadable("structure snapshot has no integer version")
    if version not in KNOWN_VERSIONS:
        raise SnapshotUnsupported(version)
    structure = dict(document)
    info = NO_PULL_REQUESTS
    if version == 2:
        missing = [key for key in PULL_REQUEST_KEYS if key not in structure]
        if missing:
            raise SnapshotUnreadable(f"structure snapshot version 2 lacks {', '.join(missing)}")
        info = _pull_requests(*(structure.pop(key) for key in PULL_REQUEST_KEYS))
    structure["version"] = SNAPSHOT_VERSION
    try:
        snapshot = StructureSnapshot.from_json(structure)
    except SnapshotFormatError as error:
        raise SnapshotUnreadable(str(error)) from error
    if snapshot.repository != repository:
        raise SnapshotUnreadable(f"structure snapshot belongs to {snapshot.repository}, not {repository}")
    return ParsedSnapshot(snapshot, info)


def _fail(message: str) -> SnapshotUnreadable:
    return SnapshotUnreadable(f"structure snapshot pull requests: {message}")


def _time(value: object, what: str, *, optional: bool = False) -> str | None:
    if optional and value is None:
        return None
    if not isinstance(value, str):
        raise _fail(f"{what} must be a timestamp")
    try:
        parse_timestamp(value)
    except ValueError as error:
        raise _fail(f"{what} is not a timestamp") from error
    return value


def _choice(value: object, allowed: frozenset[str], what: str) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise _fail(f"{what} must be one of {', '.join(sorted(allowed))}")
    return value


def _pull_requests(raw_items: object, raw_error: object, raw_fetched: object) -> PullRequestInfo:
    if not isinstance(raw_items, dict):
        raise _fail("pull_requests must be an object")
    items: dict[int, PullRequest] = {}
    for key, raw in cast("dict[object, object]", raw_items).items():
        item = _pull_request(raw)
        if key != str(item.number):
            raise _fail("a key does not match its number")
        items[item.number] = item
    error: PullRequestsError | None = None
    if raw_error is not None:
        if not isinstance(raw_error, dict) or set(raw_error) != {"code", "message", "at"}:
            raise _fail("pull_requests_error must have code, message and at")
        fields = cast("dict[str, object]", raw_error)
        if not isinstance(fields["code"], str) or not isinstance(fields["message"], str):
            raise _fail("pull_requests_error code and message must be strings")
        error = PullRequestsError(fields["code"], fields["message"], cast("str", _time(fields["at"], "error time")))
    return PullRequestInfo(2, _time(raw_fetched, "pull_requests_fetched_at", optional=True), error, items)


def _pull_request(raw: object) -> PullRequest:
    if not isinstance(raw, dict) or set(raw) != _PR_FIELDS:
        raise _fail("a pull request has unexpected keys")
    item = cast("dict[str, object]", raw)
    number = item["number"]
    if type(number) is not int or cast("int", number) <= 0:
        raise _fail("number must be a positive integer")
    if type(item["is_draft"]) is not bool:
        raise _fail("is_draft must be a boolean")
    for name in ("head_ref_name", "url"):
        if not isinstance(item[name], str):
            raise _fail(f"{name} must be a string")
    return PullRequest(
        number=cast("int", number),
        state=cast("PullRequestState", _choice(item["state"], _STATES, "state")),
        is_draft=cast("bool", item["is_draft"]),
        head_ref_name=cast("str", item["head_ref_name"]),
        mergeable=cast("Mergeable", _choice(item["mergeable"], _MERGEABLE, "mergeable")),
        checks=cast("Checks", _choice(item["checks"], _CHECKS, "checks")),
        created_at=cast("str", _time(item["created_at"], "created_at")),
        merged_at=_time(item["merged_at"], "merged_at", optional=True),
        closed_at=_time(item["closed_at"], "closed_at", optional=True),
        url=cast("str", item["url"]),
    )
