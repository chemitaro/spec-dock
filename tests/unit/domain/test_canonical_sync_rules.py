"""Pure rules of the periodic canonical sync (iss-00430): names, path selection, holds and conflict plans."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from spec_dock.runtime.domain.canonical_sync_rules import (
    MAX_FILE_BYTES,
    CatalogChange,
    ConflictEntry,
    HoldCandidate,
    IndexEntry,
    classify_holds,
    conflict_copy_name,
    pc_name,
    resolve_conflicts,
    select_paths,
)

NOW = datetime(2026, 10, 26, 12, 0, 0, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    ("hostname", "expected"),
    [
        ("Yuta-MacBook-Pro.local", "yuta-macbook-pro"),
        ("build_box 7.example.com", "build-box-7"),
        ("--Weird__Host--", "weird-host"),
        ("", "pc"),
        ("...", "pc"),
        ("a" * 40, "a" * 32),
        ("ホスト", "pc"),
    ],
)
def test_pc_name_follows_the_epic_rule(hostname: str, expected: str) -> None:
    assert pc_name(hostname) == expected


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("epic/design.md", "epic/design.conflict-mac-20261026T120000Z.md"),
        ("epic/archive.tar.gz", "epic/archive.tar.conflict-mac-20261026T120000Z.gz"),
        ("epic/Makefile", "epic/Makefile.conflict-mac-20261026T120000Z"),
        ("epic/.gitignore", "epic/.gitignore.conflict-mac-20261026T120000Z"),
        ("README", "README.conflict-mac-20261026T120000Z"),
        (".env.local", ".env.conflict-mac-20261026T120000Z.local"),
    ],
)
def test_conflict_copy_names_keep_the_extension_after_the_last_dot(path: str, expected: str) -> None:
    assert conflict_copy_name(path, pc="mac", now=NOW, taken=frozenset()) == expected


def test_a_taken_conflict_copy_name_gets_a_counter_after_the_stem() -> None:
    first = "a/b.conflict-mac-20261026T120000Z.md"
    second = "a/b.conflict-mac-20261026T120000Z-2.md"
    assert conflict_copy_name("a/b.md", pc="mac", now=NOW, taken=frozenset({first})) == second
    third = conflict_copy_name("a/b.md", pc="mac", now=NOW, taken=frozenset({first, second}))
    assert third == "a/b.conflict-mac-20261026T120000Z-3.md"


def test_conflict_copy_names_use_utc() -> None:
    local = NOW.astimezone(timezone(timedelta(hours=9)))
    assert conflict_copy_name("x", pc="mac", now=local, taken=frozenset()) == "x.conflict-mac-20261026T120000Z"


def _ago(seconds: float) -> datetime:
    return NOW - timedelta(seconds=seconds)


def test_a_file_quiet_for_30_seconds_is_selected_and_a_fresher_one_waits() -> None:
    changes = [
        CatalogChange("quiet.md", "modified", _ago(30)),
        CatalogChange("busy.md", "modified", _ago(29)),
        CatalogChange("new.md", "added", _ago(45)),
    ]
    selection = select_paths(changes, pending_since={}, now=NOW)
    assert selection.selected == ("new.md", "quiet.md")
    assert selection.pending_since == {
        "quiet.md": "2026-10-26T12:00:00Z",
        "busy.md": "2026-10-26T12:00:00Z",
        "new.md": "2026-10-26T12:00:00Z",
    }


def test_a_file_that_keeps_changing_is_selected_five_minutes_after_it_was_first_seen() -> None:
    first_seen = {"busy.md": "2026-10-26T11:55:00Z", "young.md": "2026-10-26T11:55:01Z"}
    changes = [CatalogChange("busy.md", "modified", _ago(1)), CatalogChange("young.md", "modified", _ago(1))]
    selection = select_paths(changes, pending_since=first_seen, now=NOW)
    assert selection.selected == ("busy.md",)
    assert selection.pending_since == first_seen


def test_a_deletion_counts_from_when_it_was_first_seen() -> None:
    changes = [CatalogChange("gone.md", "deleted", None), CatalogChange("old.md", "deleted", None)]
    first = select_paths(changes, pending_since={"old.md": "2026-10-26T11:59:30Z"}, now=NOW)
    assert first.selected == ("old.md",)
    assert first.pending_since["gone.md"] == "2026-10-26T12:00:00Z"
    later = select_paths(changes, pending_since=first.pending_since, now=NOW + timedelta(seconds=30))
    assert later.selected == ("gone.md", "old.md")


def test_paths_that_are_no_longer_changed_leave_pending_since_and_future_mtimes_count_as_now() -> None:
    changes = [CatalogChange("clock-skew.md", "modified", NOW + timedelta(hours=1))]
    selection = select_paths(changes, pending_since={"saved.md": "2026-10-26T11:00:00Z"}, now=NOW)
    assert selection.selected == ()
    assert selection.pending_since == {"clock-skew.md": "2026-10-26T12:00:00Z"}


def _file(path: str, content: bytes, *, blob: str = "b1", size: int | None = None) -> HoldCandidate:
    return HoldCandidate(path, len(content) if size is None else size, blob, content)


SECRETS = [
    b"token ghp_" + b"A" * 36,
    b"gho_" + b"z9" * 18,
    b"github_pat_" + b"a_" * 41,
    b"key AKIA" + b"ABCDEFGHIJKLMNOP",
    b"-----BEGIN RSA PRIVATE KEY-----\nMIIEow",
    b"-----BEGIN OPENSSH PRIVATE KEY-----\r\nb3Bl",
]


@pytest.mark.parametrize("content", SECRETS)
def test_a_whole_token_shape_is_held_as_secret(content: bytes) -> None:
    decision = classify_holds(
        [_file("notes.md", content)], deletions=(), tracked_count=10, accepted_paths={}, accepted_deletions=()
    )
    assert decision == {"notes.md": "secret"}


@pytest.mark.parametrize(
    "content",
    [
        b"tokens start with ghp_ or github_pat_ and keys with AKIA",
        b"ghp_" + b"A" * 35,
        b"-----BEGIN RSA PRIVATE KEY-----",
        b"-----BEGIN PUBLIC KEY-----\nMIIB",
    ],
)
def test_a_prefix_alone_is_not_a_secret(content: bytes) -> None:
    assert (
        classify_holds(
            [_file("doc.md", content)], deletions=(), tracked_count=10, accepted_paths={}, accepted_deletions=()
        )
        == {}
    )


def test_a_file_over_10_mib_is_held_without_reading_its_content() -> None:
    big = HoldCandidate("big.bin", MAX_FILE_BYTES + 1, "b1", None)
    edge = HoldCandidate("edge.bin", MAX_FILE_BYTES, "b2", b"")
    decision = classify_holds([big, edge], deletions=(), tracked_count=10, accepted_paths={}, accepted_deletions=())
    assert decision == {"big.bin": "too_large"}


def test_an_accepted_blob_lifts_the_hold_until_the_content_changes() -> None:
    secret = SECRETS[0]
    accepted = {"notes.md": "b1", "big.bin": "b9"}
    candidates = [_file("notes.md", secret, blob="b1"), HoldCandidate("big.bin", MAX_FILE_BYTES + 1, "b9", None)]
    assert (
        classify_holds(candidates, deletions=(), tracked_count=10, accepted_paths=accepted, accepted_deletions=()) == {}
    )
    changed = [_file("notes.md", secret, blob="b2")]
    assert classify_holds(changed, deletions=(), tracked_count=10, accepted_paths=accepted, accepted_deletions=()) == {
        "notes.md": "secret"
    }


def test_twenty_deletions_are_all_held_as_a_mass_delete() -> None:
    deleted = [f"d{index}.md" for index in range(20)]
    decision = classify_holds([], deletions=deleted, tracked_count=10_000, accepted_paths={}, accepted_deletions=())
    assert decision == dict.fromkeys(deleted, "mass_delete")
    nineteen = deleted[:19]
    assert classify_holds([], deletions=nineteen, tracked_count=10_000, accepted_paths={}, accepted_deletions=()) == {}


def test_five_deletions_are_a_mass_delete_when_they_are_ten_percent_of_the_tracked_files() -> None:
    five = [f"d{index}.md" for index in range(5)]
    assert classify_holds(
        [], deletions=five, tracked_count=50, accepted_paths={}, accepted_deletions=()
    ) == dict.fromkeys(five, "mass_delete")
    assert classify_holds([], deletions=five, tracked_count=51, accepted_paths={}, accepted_deletions=()) == {}
    four = five[:4]
    assert classify_holds([], deletions=four, tracked_count=4, accepted_paths={}, accepted_deletions=()) == {}


def test_accepted_deletions_are_neither_counted_nor_held() -> None:
    deleted = [f"d{index}.md" for index in range(25)]
    decision = classify_holds(
        [], deletions=deleted, tracked_count=1000, accepted_paths={}, accepted_deletions=deleted[:6]
    )
    assert decision == {}
    partly = classify_holds(
        [], deletions=deleted, tracked_count=1000, accepted_paths={}, accepted_deletions=deleted[:2]
    )
    assert partly == dict.fromkeys(deleted[2:], "mass_delete")


def _entry(stage: int, path: str, oid: str, mode: str = "100644") -> ConflictEntry:
    return ConflictEntry(mode, oid, stage, path)


def test_both_sides_changed_keeps_the_remote_version_and_a_copy_of_the_local_one() -> None:
    entries = [_entry(1, "a/design.md", "base"), _entry(2, "a/design.md", "local"), _entry(3, "a/design.md", "remote")]
    resolution = resolve_conflicts(entries, pc="mac", now=NOW, taken=frozenset({"a/design.md"}))
    copy = "a/design.conflict-mac-20261026T120000Z.md"
    assert resolution.updates == (IndexEntry("100644", "remote", "a/design.md"), IndexEntry("100644", "local", copy))
    assert resolution.removals == ()
    assert resolution.copies == (("a/design.md", copy),)


def test_a_modify_delete_conflict_keeps_the_modified_side() -> None:
    remote_deleted = [_entry(1, "x.md", "base"), _entry(2, "x.md", "local")]
    local_deleted = [_entry(1, "y.md", "base"), _entry(3, "y.md", "remote", "100755")]
    resolution = resolve_conflicts([*remote_deleted, *local_deleted], pc="mac", now=NOW, taken=frozenset())
    assert resolution.updates == (IndexEntry("100644", "local", "x.md"), IndexEntry("100755", "remote", "y.md"))
    assert resolution.copies == ()


def test_an_add_add_conflict_without_a_base_and_a_taken_copy_name() -> None:
    entries = [_entry(2, "n.md", "local"), _entry(3, "n.md", "remote")]
    taken = frozenset({"n.conflict-mac-20261026T120000Z.md"})
    resolution = resolve_conflicts(entries, pc="mac", now=NOW, taken=taken)
    assert resolution.copies == (("n.md", "n.conflict-mac-20261026T120000Z-2.md"),)


def test_two_conflicts_in_one_directory_never_share_a_copy_name() -> None:
    entries = [_entry(2, "d/a", "l1"), _entry(3, "d/a", "r1"), _entry(2, "d/a.md", "l2"), _entry(3, "d/a.md", "r2")]
    resolution = resolve_conflicts(entries, pc="mac", now=NOW, taken=frozenset())
    copies = [copy for _path, copy in resolution.copies]
    assert copies == ["d/a.conflict-mac-20261026T120000Z", "d/a.conflict-mac-20261026T120000Z.md"]
    assert len(set(copies)) == 2


def test_a_path_only_in_the_base_stage_is_removed() -> None:
    resolution = resolve_conflicts([_entry(1, "gone.md", "base")], pc="mac", now=NOW, taken=frozenset())
    assert resolution.updates == () and resolution.removals == ("gone.md",)
