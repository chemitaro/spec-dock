"""The dashboard's reading of a structure snapshot document (epic-00427 D-12, D-19).

The dashboard reads the file itself so that it can tell a missing, an unreadable and an unknown-version snapshot
apart; `SnapshotStore.load()` reports all three as absent. Parsing, the pull request fields of version 2 and the
Scope of each pull request belong to `canonical_structure` (iss-00537); this module only classifies the
document and decides how far the pull request values can be trusted.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import TYPE_CHECKING, Final, Literal, cast

from spec_dock.runtime.domain.canonical_structure import (
    READABLE_SNAPSHOT_VERSIONS,
    SnapshotFormatError,
    StructureSnapshot,
    parse_timestamp,
    pull_requests_by_scope,
)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from datetime import datetime

    from spec_dock.runtime.domain.canonical_structure import PullRequest, PullRequestsError

PULL_REQUEST_MAX_AGE: Final = timedelta(minutes=30)

PullRequestStatus = Literal["fresh", "stale", "unknown"]


class SnapshotUnreadable(ValueError):
    """The document is malformed, of another repository, or has no integer version."""


class SnapshotUnsupported(ValueError):
    """The document has an integer version this SpecDock does not know."""

    def __init__(self, version: int) -> None:
        super().__init__(f"structure snapshot version {version} is not supported")
        self.version = version


@dataclass(frozen=True)
class PullRequestInfo:
    """The snapshot's pull requests; `fetched_at` None means never fetched (always so for version 1)."""

    fetched_at: str | None
    error: PullRequestsError | None
    items: Mapping[int, PullRequest]
    by_scope: Mapping[str, PullRequest] = field(default_factory=dict)

    @classmethod
    def of(cls, snapshot: StructureSnapshot) -> PullRequestInfo:
        return cls(
            snapshot.pull_requests_fetched_at,
            snapshot.pull_requests_error,
            snapshot.pull_requests,
            pull_requests_by_scope(snapshot),
        )

    def status(self, now: datetime) -> PullRequestStatus:
        """unknown: never fetched, or the last fetch is more than 30 minutes old (no values are used).
        stale: the latest fetch failed but the last values are recent; they are used and marked. fresh: otherwise."""
        if self.fetched_at is None or now - parse_timestamp(self.fetched_at) > PULL_REQUEST_MAX_AGE:
            return "unknown"
        return "stale" if self.error is not None else "fresh"


NO_PULL_REQUESTS: Final = PullRequestInfo(None, None, {})


def structure_confirmed_at(fetched_at: str, probe_checked_at: str | None, probe_failed: bool, now: datetime) -> str:
    """When GitHub's structure was last confirmed (iss-00568): the newer of the snapshot's `fetched_at` and a clean
    probe's `checked_at`. A probe that recorded an error, an unreadable time or one in the future confirms nothing."""
    if probe_checked_at is None or probe_failed:
        return fetched_at
    try:
        checked = parse_timestamp(probe_checked_at)
        if checked > now or checked <= parse_timestamp(fetched_at):
            return fetched_at
    except ValueError:
        return fetched_at
    return probe_checked_at


@dataclass(frozen=True)
class ParsedSnapshot:
    snapshot: StructureSnapshot
    pull_requests: PullRequestInfo


def parse_snapshot_document(payload: object, *, repository: str) -> ParsedSnapshot:
    """Parse a snapshot document of version 1 or 2 for `repository` (host/owner/name)."""
    if not isinstance(payload, dict):
        raise SnapshotUnreadable("structure snapshot is not a JSON object")
    version = cast("dict[str, object]", payload).get("version")
    if type(version) is not int:
        raise SnapshotUnreadable("structure snapshot has no integer version")
    if version not in READABLE_SNAPSHOT_VERSIONS:
        raise SnapshotUnsupported(cast("int", version))
    try:
        snapshot = StructureSnapshot.from_json(payload)
    except SnapshotFormatError as error:
        raise SnapshotUnreadable(str(error)) from error
    if snapshot.repository != repository:
        raise SnapshotUnreadable(f"structure snapshot belongs to {snapshot.repository}, not {repository}")
    return ParsedSnapshot(snapshot, PullRequestInfo.of(snapshot))
