"""The writers of the dashboard's per-user files (iss-00529 D-07, D-08; T-01)."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.domain.dashboard_model import SeenScope
from spec_dock.runtime.infra.dashboard_files import read_hidden, read_server_url
from spec_dock.runtime.infra.dashboard_store import (
    SEEN_KEEP,
    DashboardStateUnreadable,
    append_seen,
    find_seen,
    hidden_repositories,
    hide_repository,
    read_server_record,
    remove_server_record,
    show_repository,
    write_server_record,
)
from spec_dock.runtime.infra.github_structure import GithubRepository

if TYPE_CHECKING:
    from pathlib import Path

NOW = datetime(2026, 11, 4, 12, 0, tzinfo=timezone.utc)
REPO = GithubRepository("o", "r")
OTHER = GithubRepository("o", "s")


def test_hide_and_show_write_the_marks_atomically(tmp_path: Path) -> None:
    assert hide_repository(tmp_path, REPO, now=NOW) is True
    assert hide_repository(tmp_path, REPO, now=NOW) is False  # unchanged
    assert read_hidden(tmp_path, REPO) and not read_hidden(tmp_path, OTHER)
    document = json.loads((tmp_path / "dashboard" / "repositories.json").read_text())
    assert document == {
        "schema": "specdock.dashboard-repositories/v1",
        "repositories": {"github.com/o/r": {"hidden_at": "2026-11-04T12:00:00Z"}},
    }
    assert hidden_repositories(tmp_path) == frozenset({"github.com/o/r"})
    assert show_repository(tmp_path, REPO) is True
    assert show_repository(tmp_path, REPO) is False
    assert not read_hidden(tmp_path, REPO)
    assert [p.name for p in (tmp_path / "dashboard").iterdir() if p.name.endswith(".tmp")] == []


def test_an_unreadable_marks_file_is_never_overwritten(tmp_path: Path) -> None:
    path = tmp_path / "dashboard" / "repositories.json"
    path.parent.mkdir(parents=True)
    path.write_text("{broken")
    with pytest.raises(DashboardStateUnreadable):
        hide_repository(tmp_path, REPO, now=NOW)
    with pytest.raises(DashboardStateUnreadable):
        show_repository(tmp_path, REPO)
    assert path.read_text() == "{broken"
    assert hidden_repositories(tmp_path) is None


def test_the_server_record_is_removed_only_for_its_own_pid(tmp_path: Path) -> None:
    record = write_server_record(
        tmp_path,
        local="http://127.0.0.1:47800/",
        tailscale=None,
        pid=os.getpid(),
        version="0.5.1",
        started_at="2026-11-04T12:00:00Z",
    )
    assert record["schema"] == "specdock.dashboard-server/v1"
    assert read_server_record(tmp_path) == record
    assert read_server_url(tmp_path) == "http://127.0.0.1:47800/"
    assert remove_server_record(tmp_path, pid=os.getpid() + 1) is False
    assert read_server_record(tmp_path) is not None
    assert remove_server_record(tmp_path, pid=os.getpid()) is True
    assert read_server_record(tmp_path) is None
    assert remove_server_record(tmp_path, pid=os.getpid()) is False


def test_seen_records_keep_the_latest_five_per_repository(tmp_path: Path) -> None:
    scopes = {"iss-00001": SeenScope("ready", "none")}
    ids = [append_seen(tmp_path, REPO, scopes, now=NOW).seen_id for _ in range(SEEN_KEEP + 1)]
    append_seen(tmp_path, OTHER, {"iss-00009": SeenScope("done", None)}, now=NOW)
    assert len(set(ids)) == SEEN_KEEP + 1
    document = json.loads((tmp_path / "dashboard" / "seen.json").read_text())
    assert document["schema"] == "specdock.dashboard-seen/v1"
    records = document["repositories"]["github.com/o/r"]["records"]
    assert [item["seen_id"] for item in records] == ids[1:]
    assert records[-1]["scopes"] == {"iss-00001": {"state": "ready", "pr": "none"}}
    assert find_seen(tmp_path, REPO, ids[0]) is None  # dropped
    latest = find_seen(tmp_path, REPO, None)
    assert latest is not None and latest.seen_id == ids[-1] and latest.scopes == scopes
    assert find_seen(tmp_path, REPO, ids[2]).seen_id == ids[2]  # type: ignore[union-attr]
    assert find_seen(tmp_path, OTHER, None).scopes == {"iss-00009": SeenScope("done", None)}  # type: ignore[union-attr]


def test_an_unreadable_seen_file_reads_as_no_record_and_is_rebuilt(tmp_path: Path) -> None:
    path = tmp_path / "dashboard" / "seen.json"
    path.parent.mkdir(parents=True)
    path.write_text("[]")
    assert find_seen(tmp_path, REPO, None) is None
    record = append_seen(tmp_path, REPO, {}, now=NOW)
    assert find_seen(tmp_path, REPO, None).seen_id == record.seen_id  # type: ignore[union-attr]
