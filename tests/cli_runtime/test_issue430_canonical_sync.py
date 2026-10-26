"""`spec-dock canonical sync` between two clones of a bare origin (iss-00430): save, merge, push, holds, pauses."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest

from tests.support.canonical_repo import git
from tests.support.canonical_sync import SyncPair, catalog_result

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def pair(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> SyncPair:
    return SyncPair.create(tmp_path, monkeypatch, capsys)


def test_a_file_is_saved_after_30_quiet_seconds_and_reaches_the_other_clone(pair: SyncPair) -> None:
    pair.write(pair.a, "init-00001-plan/requirement.md", "draft\n")
    code, result = pair.sync(pair.a)
    assert code == 0 and result["status"] == "unchanged", result
    assert pair.remote_file("init-00001-plan/requirement.md") is None
    pair.advance(31)
    code, result = pair.sync(pair.a, pc="mac-a")
    item = catalog_result(result)
    assert code == 0 and result["status"] == "succeeded", result
    assert item["result"] == "ok" and item["pushed"] is True and item["saved_commit"] == pair.remote_head()
    assert pair.remote_file("init-00001-plan/requirement.md") == "draft"
    subject = git(pair.catalog(pair.a), "log", "-1", "--format=%s|%an <%ae>")
    assert subject == "spec-dock: save 1 files (mac-a)|Fixture <fixture@example.invalid>"
    code, result = pair.sync(pair.b)
    assert catalog_result(result)["merged"] is True
    assert (pair.specs(pair.b) / "init-00001-plan/requirement.md").read_text() == "draft\n"
    assert git(pair.catalog(pair.b), "status", "--porcelain") == ""


def test_a_cycle_without_changes_commits_nothing(pair: SyncPair) -> None:
    before = git(pair.catalog(pair.a), "rev-parse", "HEAD")
    pair.advance(31)
    code, result = pair.sync(pair.a)
    assert code == 0 and result["status"] == "unchanged" and result["effects"] == []
    assert git(pair.catalog(pair.a), "rev-parse", "HEAD") == before
    state = pair.state(pair.a)
    assert state is not None and state.last_cycle is not None and state.last_cycle.result == "ok"
    assert state.remote_contains_head is True and state.push_auth is not None and state.push_auth.result == "ok"


def test_the_same_file_edited_in_two_clones_keeps_both_versions(pair: SyncPair) -> None:
    pair.write(pair.a, "doc.md", "base\n")
    pair.advance(31)
    pair.sync(pair.a)
    pair.sync(pair.b)
    pair.write(pair.a, "doc.md", "from a\n")
    pair.write(pair.b, "doc.md", "from b\n")
    pair.advance(31)
    pair.sync(pair.a, pc="mac-a")
    code, result = pair.sync(pair.b, pc="mac-b")
    item = catalog_result(result)
    assert code == 0 and item["merged"] and item["pushed"], result
    (copy,) = item["conflicts"]
    assert copy["path"] == "doc.md" and copy["copy"].startswith("doc.conflict-mac-b-") and copy["copy"].endswith(".md")
    pair.sync(pair.a)
    for checkout in (pair.a, pair.b):
        assert (pair.specs(checkout) / "doc.md").read_text() == "from a\n"
        assert (pair.specs(checkout) / copy["copy"]).read_text() == "from b\n"
        texts = "".join(path.read_text() for path in pair.specs(checkout).rglob("*.md"))
        assert "<<<<<<<" not in texts and ">>>>>>>" not in texts
        assert git(pair.catalog(checkout), "status", "--porcelain") == ""


def test_a_modify_delete_conflict_keeps_the_modification(pair: SyncPair) -> None:
    pair.write(pair.a, "keep.md", "v1\n")
    pair.write(pair.a, "Makefile", "all:\n")
    pair.advance(31)
    pair.sync(pair.a)
    pair.sync(pair.b)
    (pair.specs(pair.a) / "keep.md").unlink()
    pair.write(pair.b, "keep.md", "v2\n")
    pair.write(pair.a, "Makefile", "a:\n")
    pair.write(pair.b, "Makefile", "b:\n")
    pair.sync(pair.a)  # a deletion is saved 30 seconds after it was first seen
    pair.advance(31)
    _code, first = pair.sync(pair.a, pc="mac-a")
    assert catalog_result(first)["pushed"] is True and pair.remote_file("keep.md") is None
    _code, result = pair.sync(pair.b, pc="mac-b")
    copies = [item["copy"] for item in catalog_result(result)["conflicts"]]
    assert (pair.specs(pair.b) / "keep.md").read_text() == "v2\n"
    (makefile_copy,) = copies
    assert re.fullmatch(r"Makefile\.conflict-mac-b-\d{8}T\d{6}Z", makefile_copy), makefile_copy
    pair.sync(pair.a)
    assert (pair.specs(pair.a) / "keep.md").read_text() == "v2\n"


def test_an_incoming_change_to_a_file_being_edited_waits_without_breaking_anything(pair: SyncPair) -> None:
    pair.write(pair.a, "busy.md", "v1\n")
    pair.advance(31)
    pair.sync(pair.a)
    pair.sync(pair.b)
    pair.write(pair.a, "busy.md", "remote edit\n")
    pair.advance(31)
    pair.sync(pair.a)
    pair.write(pair.b, "busy.md", "still typing\n")
    head = git(pair.catalog(pair.b), "rev-parse", "HEAD")
    code, result = pair.sync(pair.b)
    item = catalog_result(result)
    assert code == 0 and item["result"] == "ok" and item["merged"] is False
    assert item["blocking"] == [{"path": "busy.md", "reason": "local_edit"}]
    assert (pair.specs(pair.b) / "busy.md").read_text() == "still typing\n"
    assert git(pair.catalog(pair.b), "rev-parse", "HEAD") == head
    state = pair.state(pair.b)
    assert state is not None and [item.path for item in state.blocking] == ["busy.md"]
    pair.advance(31)
    code, result = pair.sync(pair.b, pc="mac-b")
    item = catalog_result(result)
    assert item["merged"] and item["blocking"] == [] and item["conflicts"][0]["path"] == "busy.md"
    assert (pair.specs(pair.b) / "busy.md").read_text() == "remote edit\n"
    assert (pair.specs(pair.b) / item["conflicts"][0]["copy"]).read_text() == "still typing\n"


def test_failing_hooks_and_commit_signing_do_not_stop_the_sync(pair: SyncPair) -> None:
    common = pair.a / ".git"
    hooks = common / "hooks"
    hooks.mkdir(exist_ok=True)
    for name in ("pre-commit", "post-checkout", "post-merge", "pre-push", "commit-msg", "reference-transaction"):
        (hooks / name).write_text("#!/bin/sh\nexit 1\n")
        (hooks / name).chmod(0o755)
    git(pair.a, "config", "commit.gpgSign", "true")
    git(pair.a, "config", "push.gpgSign", "true")
    pair.write(pair.b, "from-b.md", "b\n")
    pair.write(pair.a, "from-a.md", "a\n")
    pair.advance(31)
    pair.sync(pair.b)
    code, result = pair.sync(pair.a)
    item = catalog_result(result)
    assert code == 0 and item["result"] == "ok" and item["merged"] and item["pushed"], result
    assert pair.remote_file("from-a.md") == "a" and pair.remote_file("from-b.md") == "b"


def test_a_held_catalog_lock_skips_the_catalog_and_a_staged_index_does_not_stop_the_merge(pair: SyncPair) -> None:
    from spec_dock.runtime.infra.catalog_lock import CatalogLock

    pair.write(pair.a, "half.md", "half written\n")
    pair.advance(31)
    with CatalogLock(pair.catalog(pair.a)):
        code, result = pair.sync(pair.a)
    item = catalog_result(result)
    assert code == 0 and item["result"] == "skipped" and item["skipped_reason"] == "lock_busy"
    assert pair.remote_file("half.md") is None
    pair.write(pair.b, "other.md", "o\n")
    pair.advance(31)
    pair.sync(pair.b)
    git(pair.catalog(pair.a), "add", "half.md")
    code, result = pair.sync(pair.a)
    item = catalog_result(result)
    assert item["result"] == "ok" and item["merged"] and item["pushed"]
    assert pair.remote_file("half.md") == "half written"


def test_an_unreachable_origin_keeps_saving_locally_and_pushes_later(pair: SyncPair) -> None:
    url = git(pair.a, "remote", "get-url", "origin")
    git(pair.a, "remote", "set-url", "origin", str(pair.tmp_path / "missing.git"))
    pair.write(pair.a, "offline.md", "o\n")
    pair.advance(31)
    code, result = pair.sync(pair.a)
    item = catalog_result(result)
    assert code == 6 and result["status"] == "partial" and item["result"] == "error"
    assert item["error"]["code"] == "GITHUB_UNAVAILABLE" and item["saved_commit"] is not None
    state = pair.state(pair.a)
    assert state is not None and state.remote_contains_head is False and state.unpushed_since is not None
    git(pair.a, "remote", "set-url", "origin", url)
    code, result = pair.sync(pair.a)
    assert code == 0 and catalog_result(result)["pushed"] is True
    assert pair.remote_file("offline.md") == "o"
    state = pair.state(pair.a)
    assert state is not None and state.remote_contains_head is True and state.unpushed_since is None


def _commit_on_remote(pair: SyncPair, files: dict[str, str], *, parent: str | None) -> str:
    """A commit made straight in the bare origin (a push from somewhere else), without any clone."""
    import os
    import subprocess

    index = pair.tmp_path / "remote-index"
    environment = {**os.environ, "GIT_INDEX_FILE": str(index), "GIT_DIR": str(pair.remote)}
    environment.update({"GIT_AUTHOR_NAME": "x", "GIT_AUTHOR_EMAIL": "x@x", "GIT_COMMITTER_NAME": "x"})
    environment["GIT_COMMITTER_EMAIL"] = "x@x"

    def run(*args: str, data: bytes | None = None) -> str:
        return (
            subprocess
            .run(["git", *args], check=True, capture_output=True, env=environment, input=data)
            .stdout.decode()
            .strip()
        )

    if parent is None:
        run("read-tree", "--empty")
    else:
        run("read-tree", parent)
    for path, text in files.items():
        oid = run("hash-object", "-w", "--stdin", data=text.encode())
        run("update-index", "--add", "--cacheinfo", f"100644,{oid},{path}")
    tree = run("write-tree")
    index.unlink()
    return run("commit-tree", tree, *(("-p", parent) if parent else ()), "-m", "elsewhere")


def test_a_command_changeset_is_saved_at_once_as_one_commit_and_its_deletions_are_not_held(pair: SyncPair) -> None:
    from spec_dock.runtime.application.canonical_catalog import catalog_changes

    for index in range(25):
        pair.write(pair.a, f"old/{index}.md", f"{index}\n")
    pair.advance(31)
    pair.sync(pair.a)
    catalog = pair.catalog(pair.a).resolve()
    with catalog_changes(catalog, command="scope delete") as changes:
        for index in range(25):
            (catalog / f"old/{index}.md").unlink()
        (catalog / "new.md").write_text("fresh\n")
        changes.delete("old")
        changes.add("new.md")
    before = git(catalog, "rev-parse", "HEAD")
    code, result = pair.sync(pair.a)
    item = catalog_result(result)
    assert code == 0 and item["holds"] == [] and item["pushed"], result
    assert git(catalog, "rev-list", "--count", f"{before}..HEAD") == "1"
    assert pair.remote_file("new.md") == "fresh" and pair.remote_file("old/0.md") is None
    assert list((catalog / ".runtime/changesets").iterdir()) == []


def test_twenty_five_deletions_are_held_and_not_pushed_even_from_a_finish_changeset(pair: SyncPair) -> None:
    from spec_dock.runtime.application.canonical_catalog import catalog_changes

    for index in range(25):
        pair.write(pair.a, f"specs/{index}.md", f"{index}\n")
    pair.advance(31)
    pair.sync(pair.a)
    remote_before = pair.remote_head()
    catalog = pair.catalog(pair.a).resolve()
    with catalog_changes(catalog, command="work finish", origin="finish") as changes:
        for index in range(25):
            (catalog / f"specs/{index}.md").unlink()
        changes.delete("specs")
    code, result = pair.sync(pair.a)
    item = catalog_result(result)
    assert code == 0 and item["pushed"] is False and len(item["holds"]) == 25
    assert {hold["kind"] for hold in item["holds"]} == {"mass_delete"}
    pair.advance(600)
    pair.sync(pair.a)
    assert pair.remote_head() == remote_before and pair.remote_file("specs/0.md") == "0"
    state = pair.state(pair.a)
    assert state is not None and len(state.holds) == 25


def test_a_secret_or_a_large_file_is_held_but_a_prefix_is_saved(pair: SyncPair) -> None:
    pair.write(pair.a, "token.md", "ghp_" + "Q" * 36 + "\n")
    pair.write(pair.a, "notes.md", "tokens look like ghp_ and github_pat_\n")
    big = pair.specs(pair.a) / "big.bin"
    with big.open("wb") as stream:
        stream.truncate(10 * 1024 * 1024 + 1)
    pair.advance(31)
    _code, result = pair.sync(pair.a)
    item = catalog_result(result)
    assert sorted((hold["path"], hold["kind"]) for hold in item["holds"]) == [
        ("big.bin", "too_large"),
        ("token.md", "secret"),
    ]
    assert pair.remote_file("notes.md") is not None and pair.remote_file("token.md") is None
    log = (pair.state_root / "canonical-sync.log").read_text()
    assert "ghp_" not in log


def test_a_force_pushed_remote_pauses_the_catalog_without_taking_anything(pair: SyncPair) -> None:
    pair.write(pair.a, "a.md", "a\n")
    pair.advance(31)
    pair.sync(pair.a)
    pair.sync(pair.b)
    rewritten = _commit_on_remote(pair, {"other.md": "rewritten\n"}, parent=None)
    git(pair.remote, "update-ref", "refs/heads/spec-dock/canonical", rewritten)
    pair.write(pair.b, "local.md", "mine\n")
    pair.advance(31)
    head = git(pair.catalog(pair.b), "rev-parse", "HEAD")
    code, result = pair.sync(pair.b)
    item = catalog_result(result)
    assert code == 3 and result["status"] == "failed" and result["error"]["code"] == "remote_rewritten", result
    assert item["result"] == "paused" and item["paused"] == "remote_rewritten"
    assert git(pair.catalog(pair.b), "rev-parse", "HEAD") == head
    assert (pair.specs(pair.b) / "local.md").read_text() == "mine\n" and not (pair.specs(pair.b) / "other.md").exists()
    assert pair.remote_head() == rewritten
    code, result = pair.sync(pair.b)
    assert code == 3 and result["status"] == "failed" and catalog_result(result)["paused"] == "remote_rewritten"


def test_a_deleted_remote_branch_pauses_the_catalog(pair: SyncPair) -> None:
    pair.write(pair.a, "a.md", "a\n")
    pair.advance(31)
    pair.sync(pair.a)
    git(pair.remote, "update-ref", "-d", "refs/heads/spec-dock/canonical")
    code, result = pair.sync(pair.a)
    item = catalog_result(result)
    assert code == 3 and item["result"] == "paused" and item["paused"] == "remote_deleted"
    assert git(pair.remote, "rev-parse", "--verify", "--quiet", "refs/heads/spec-dock/canonical", check=False) == ""


def test_a_directory_file_conflict_pauses_as_merge_failed_and_commits_nothing(pair: SyncPair) -> None:
    pair.write(pair.a, "seed.md", "s\n")
    pair.advance(31)
    pair.sync(pair.a)
    pair.sync(pair.b)
    pair.write(pair.a, "topic", "a file\n")
    pair.write(pair.b, "topic/inner.md", "a directory\n")
    pair.advance(31)
    pair.sync(pair.a)
    head = git(pair.catalog(pair.b), "rev-parse", "HEAD")
    _code, result = pair.sync(pair.b)
    item = catalog_result(result)
    assert item["result"] == "paused" and item["paused"] == "merge_failed", result
    assert git(pair.catalog(pair.b), "rev-parse", "HEAD") != pair.remote_head()
    assert git(pair.catalog(pair.b), "rev-list", "--count", f"{head}..HEAD") == "1"  # only its own save
    assert (pair.specs(pair.b) / "topic/inner.md").read_text() == "a directory\n"
    assert not any("~" in path.name for path in pair.specs(pair.b).rglob("*"))


def test_a_broken_state_file_is_left_alone_and_reported(pair: SyncPair) -> None:
    import os

    from spec_dock.runtime.infra.canonical_state import catalog_state_dir

    directory = catalog_state_dir(pair.state_root, os.path.realpath(pair.catalog(pair.a)))
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "state.json").write_text("{broken")
    pair.write(pair.a, "x.md", "x\n")
    pair.advance(31)
    code, result = pair.sync(pair.a)
    item = catalog_result(result)
    assert code == 3 and item["result"] == "error" and item["error"]["code"] == "CANONICAL_STATE_UNREADABLE"
    assert (directory / "state.json").read_text() == "{broken" and pair.remote_file("x.md") is None


def test_a_rejected_push_is_retried_from_the_fetch_twice(pair: SyncPair, monkeypatch: pytest.MonkeyPatch) -> None:
    from spec_dock.runtime.infra import canonical_git

    real = canonical_git.push_canonical
    calls: list[bool] = []

    def flaky(catalog: Path, *, dry_run: bool = False, git: str = "git", timeout: float = 60.0) -> object:
        calls.append(dry_run)
        if not dry_run and len([item for item in calls if not item]) <= 2:
            return canonical_git.PushResult("rejected", "fetch first")
        return real(catalog, dry_run=dry_run, git=git, timeout=timeout)

    monkeypatch.setattr(canonical_git, "push_canonical", flaky)
    pair.write(pair.a, "retry.md", "r\n")
    pair.advance(31)
    code, result = pair.sync(pair.a)
    assert code == 0 and catalog_result(result)["pushed"] is True
    assert calls.count(False) == 3 and pair.remote_file("retry.md") == "r"
