"""Reading structure snapshot documents of version 1 and 2 for the dashboard (iss-00528, D-19)."""

from __future__ import annotations

from datetime import timedelta

import pytest

from spec_dock.runtime.domain.dashboard_snapshot import (
    SnapshotUnreadable,
    SnapshotUnsupported,
    parse_snapshot_document,
    structure_confirmed_at,
)
from tests.support.dashboard import NOW, node, snapshot


def v1_document() -> dict[str, object]:
    """A version-1 file as SpecDock 0.5 wrote it: no pull request fields."""
    document = snapshot(node(1, "epic"), node(2, "issue", parent=1, in_progress=True)).to_json()
    for key in ("pull_requests", "pull_requests_error", "pull_requests_fetched_at"):
        document.pop(key)
    document["version"] = 1
    return document


def pr_json(number: int, branch: str, **changes: object) -> dict[str, object]:
    item: dict[str, object] = {
        "number": number,
        "state": "open",
        "is_draft": False,
        "head_ref_name": branch,
        "mergeable": "mergeable",
        "checks": "success",
        "created_at": "2026-11-01T00:00:00Z",
        "merged_at": None,
        "closed_at": None,
        "url": f"https://github.com/o/r/pull/{number}",
    }
    item.update(changes)
    return item


def v2_document(
    *items: dict[str, object], error: object = None, fetched: object = "2026-11-04T11:50:00Z"
) -> dict[str, object]:
    document = v1_document()
    document["version"] = 2
    document["pull_requests"] = {str(item["number"]): item for item in items}
    document["pull_requests_error"] = error
    document["pull_requests_fetched_at"] = fetched
    return document


def test_version_1_is_read_and_its_pull_requests_are_unknown() -> None:
    parsed = parse_snapshot_document(v1_document(), repository="github.com/o/r")
    assert [scope.id for scope in parsed.snapshot.scopes] == ["epic-00001", "iss-00002"]
    assert parsed.pull_requests.status(NOW) == "unknown"


def test_version_2_maps_pull_requests_to_scopes_by_branch_name() -> None:
    parsed = parse_snapshot_document(
        v2_document(
            pr_json(10, "chemitaro/iss-00002", state="closed", closed_at="2026-11-02T00:00:00Z"),
            pr_json(11, "iss-00002-retry", created_at="2026-10-30T00:00:00Z"),
            pr_json(12, "feature/other"),
        ),
        repository="github.com/o/r",
    )
    info = parsed.pull_requests
    assert info.status(NOW) == "fresh"
    assert sorted(info.items) == [10, 11, 12]
    assert {scope: item.number for scope, item in info.by_scope.items()} == {"iss-00002": 11}


def test_an_empty_fresh_list_means_no_pull_requests() -> None:
    parsed = parse_snapshot_document(v2_document(), repository="github.com/o/r")
    assert parsed.pull_requests.status(NOW) == "fresh" and parsed.pull_requests.items == {}


def test_pull_request_status_is_unknown_without_a_recent_fetch_and_stale_after_an_error() -> None:
    never = parse_snapshot_document(v2_document(fetched=None), repository="github.com/o/r").pull_requests
    assert never.status(NOW) == "unknown"
    error = {"code": "GITHUB_UNAVAILABLE", "message": "down", "at": "2026-11-04T11:59:00Z"}
    failed = parse_snapshot_document(v2_document(pr_json(3, "iss-00002"), error=error), repository="github.com/o/r")
    assert failed.pull_requests.status(NOW) == "stale" and failed.pull_requests.error is not None
    old = (NOW - timedelta(minutes=31)).strftime("%Y-%m-%dT%H:%M:%SZ")
    assert (
        parse_snapshot_document(v2_document(fetched=old), repository="github.com/o/r").pull_requests.status(NOW)
        == "unknown"
    )
    recent = (NOW - timedelta(minutes=29)).strftime("%Y-%m-%dT%H:%M:%SZ")
    assert (
        parse_snapshot_document(v2_document(fetched=recent), repository="github.com/o/r").pull_requests.status(NOW)
        == "fresh"
    )


@pytest.mark.parametrize("version", [0, 3, 99])
def test_an_unknown_integer_version_is_unsupported(version: int) -> None:
    document = v1_document()
    document["version"] = version
    with pytest.raises(SnapshotUnsupported) as raised:
        parse_snapshot_document(document, repository="github.com/o/r")
    assert raised.value.version == version


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.pop("version"),
        lambda d: d.update(version="2"),
        lambda d: d.update(issues=[]),
        lambda d: d.update(repository="github.com/o/other"),
        lambda d: d.update(version=2),
        lambda d: d.update(
            version=2, pull_requests={"5": pr_json(6, "x")}, pull_requests_error=None, pull_requests_fetched_at=None
        ),
        lambda d: d.update(
            version=2,
            pull_requests={"5": pr_json(5, "x", state="draft")},
            pull_requests_error=None,
            pull_requests_fetched_at=None,
        ),
        lambda d: d.update(
            version=2, pull_requests={}, pull_requests_error={"code": "X"}, pull_requests_fetched_at=None
        ),
        lambda d: d.update(version=2, pull_requests={}, pull_requests_error=None, pull_requests_fetched_at="yesterday"),
        lambda d: d.update(
            version=2,
            pull_requests={"5": {**pr_json(5, "x"), "extra": 1}},
            pull_requests_error=None,
            pull_requests_fetched_at=None,
        ),
    ],
)
def test_malformed_documents_are_unreadable(mutate) -> None:
    document = v1_document()
    mutate(document)
    with pytest.raises(SnapshotUnreadable):
        parse_snapshot_document(document, repository="github.com/o/r")


def test_a_non_object_document_is_unreadable() -> None:
    with pytest.raises(SnapshotUnreadable):
        parse_snapshot_document([], repository="github.com/o/r")


# iss-00568 T-01: the time the structure was last confirmed -------------------------------------------------


def _ago(minutes: int) -> str:
    return (NOW - timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")


@pytest.mark.parametrize(
    ("fetched", "checked", "failed", "expected"),
    [
        (31, 1, False, 1),  # a recent probe keeps an unchanged structure fresh
        (31, 31, False, 31),
        (5, 20, False, 5),  # a probe older than the snapshot adds nothing
        (31, 1, True, 31),  # a failing probe is not a confirmation
        (31, None, False, 31),
    ],
)
def test_structure_confirmed_at_takes_the_newer_of_snapshot_and_clean_probe(
    fetched: int, checked: int | None, failed: bool, expected: int
) -> None:
    checked_at = _ago(checked) if checked is not None else None
    assert structure_confirmed_at(_ago(fetched), checked_at, failed, NOW) == _ago(expected)


@pytest.mark.parametrize("bad", ["not-a-time", "2026-11-04T13:00:00Z"])
def test_structure_confirmed_at_ignores_an_invalid_or_future_probe_time(bad: str) -> None:
    assert structure_confirmed_at(_ago(31), bad, False, NOW) == _ago(31)
