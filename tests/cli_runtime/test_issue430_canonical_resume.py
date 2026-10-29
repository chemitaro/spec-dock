"""Pauses and `canonical resume` (iss-00430, AC-430-03, -22): rewrite, deletion, re-adoption without old history."""

from __future__ import annotations

import os
import subprocess
from typing import TYPE_CHECKING

import pytest

from tests.support.canonical_repo import git
from tests.support.canonical_sync import SyncPair, catalog_result

if TYPE_CHECKING:
    from pathlib import Path

TOKEN = "ghp_" + "K" * 36


@pytest.fixture
def pair(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> SyncPair:
    return SyncPair.create(tmp_path, monkeypatch, capsys)


def _remote_commit(pair: SyncPair, files: dict[str, str], *, parent: str | None) -> str:
    index = pair.tmp_path / "remote-index"
    environment = {**os.environ, "GIT_INDEX_FILE": str(index), "GIT_DIR": str(pair.remote)}
    for key in ("AUTHOR", "COMMITTER"):
        environment[f"GIT_{key}_NAME"] = "elsewhere"
        environment[f"GIT_{key}_EMAIL"] = "elsewhere@example.invalid"

    def run(*args: str, data: bytes | None = None) -> str:
        return (
            subprocess
            .run(["git", *args], check=True, capture_output=True, env=environment, input=data)
            .stdout.decode()
            .strip()
        )

    run("read-tree", parent) if parent else run("read-tree", "--empty")
    for path, text in files.items():
        oid = run("hash-object", "-w", "--stdin", data=text.encode())
        run("update-index", "--add", "--cacheinfo", f"100644,{oid},{path}")
    tree = run("write-tree")
    index.unlink()
    return run("commit-tree", tree, *(("-p", parent) if parent else ()), "-m", "elsewhere")


def _force(pair: SyncPair, commit: str) -> None:
    git(pair.remote, "update-ref", "refs/heads/spec-dock/canonical", commit)


def _history(pair: SyncPair) -> set[str]:
    return set(git(pair.remote, "rev-list", "refs/heads/spec-dock/canonical").split())


def test_adopting_a_rewritten_remote_keeps_local_content_and_never_pushes_the_dropped_history(pair: SyncPair) -> None:
    pair.write(pair.a, "base.md", "base\n")
    pair.advance(31)
    pair.sync(pair.a)
    first = pair.remote_head()
    pair.write(pair.a, "dropped.md", "a commit GitHub will drop\n")
    pair.advance(31)
    pair.sync(pair.a)
    dropped = pair.remote_head()
    rewritten = _remote_commit(pair, {"theirs.md": "after the rewrite\n"}, parent=first)
    _force(pair, rewritten)
    pair.write(pair.a, "mine.md", "local only\n")
    pair.advance(31)
    code, result = pair.sync(pair.a)
    assert catalog_result(result)["paused"] == "remote_rewritten"
    code, result = pair.run(pair.a, "canonical", "resume")
    assert code == 3 and result["error"]["code"] == "CANONICAL_PAUSED"
    assert result["error"]["details"]["next_step"] == "spec-dock canonical resume --adopt-remote"
    code, result = pair.run(pair.a, "canonical", "resume", "--push-local")
    assert code == 3 and result["error"]["code"] == "CANONICAL_PAUSED"
    code, result = pair.run(pair.a, "canonical", "resume", "--adopt-remote")
    assert code == 0 and result["data"]["result"]["baseline"] == rewritten, result
    code, result = pair.sync(pair.a)
    item = catalog_result(result)
    assert code == 0 and item["merged"] and item["pushed"], result
    head = pair.remote_head()
    assert git(pair.remote, "show", "-s", "--format=%P", head) == rewritten  # one parent: GitHub's
    assert dropped not in _history(pair)
    for path, text in (
        ("base.md", "base"),
        ("dropped.md", "a commit GitHub will drop"),
        ("theirs.md", "after the rewrite"),
        ("mine.md", "local only"),
    ):
        assert pair.remote_file(path) == text
    state = pair.state(pair.a)
    assert state is not None and state.paused is None and state.adopt_remote_pending is False


def test_adopting_an_unrelated_history_keeps_both_versions_of_a_file(pair: SyncPair) -> None:
    pair.write(pair.a, "doc.md", "local\n")
    pair.advance(31)
    pair.sync(pair.a)
    _force(
        pair, _remote_commit(pair, {"doc.md": "remote\n", ".spec-dock-canonical.json": '{"format": 1}\n'}, parent=None)
    )
    _code, result = pair.sync(pair.a)
    assert catalog_result(result)["paused"] == "remote_rewritten"
    pair.run(pair.a, "canonical", "resume", "--adopt-remote")
    _code, result = pair.sync(pair.a, pc="mac-a")
    item = catalog_result(result)
    assert item["pushed"] and item["conflicts"][0]["path"] == "doc.md"
    assert pair.remote_file("doc.md") == "remote" and pair.remote_file(item["conflicts"][0]["copy"]) == "local"


def test_adopting_stays_paused_when_the_rewrite_removed_a_secret_that_would_come_back(pair: SyncPair) -> None:
    pair.write(pair.a, "base.md", "base\n")
    pair.write(pair.a, "leak.md", TOKEN + "\n")
    pair.advance(31)
    pair.sync(pair.a)
    pair.run(pair.a, "canonical", "accept", "leak.md")
    pair.sync(pair.a)
    leaked = pair.remote_head()
    assert pair.remote_file("leak.md") == TOKEN
    cleaned = _remote_commit(pair, {"base.md": "base\n", ".spec-dock-canonical.json": '{"format": 1}\n'}, parent=None)
    _force(pair, cleaned)
    (pair.catalog(pair.a) / ".runtime/accepted.json").unlink()
    pair.sync(pair.a)
    pair.run(pair.a, "canonical", "resume", "--adopt-remote")
    _code, result = pair.sync(pair.a)
    item = catalog_result(result)
    assert item["result"] == "paused" and item["error"]["code"] == "CANONICAL_SAVE_HELD", result
    assert [hold["path"] for hold in item["holds"]] == ["leak.md"]
    assert pair.remote_head() == cleaned and leaked not in _history(pair)
    (pair.specs(pair.a) / "leak.md").unlink()
    pair.run(pair.a, "canonical", "resume", "--adopt-remote")
    pair.sync(pair.a)
    pair.advance(31)
    _code, result = pair.sync(pair.a)
    assert catalog_result(result)["pushed"] is True and pair.remote_file("leak.md") is None
    assert leaked not in _history(pair)


def test_push_local_recreates_a_deleted_remote_branch(pair: SyncPair) -> None:
    pair.write(pair.a, "keep.md", "k\n")
    pair.advance(31)
    pair.sync(pair.a)
    git(pair.remote, "update-ref", "-d", "refs/heads/spec-dock/canonical")
    _code, result = pair.sync(pair.a)
    assert catalog_result(result)["paused"] == "remote_deleted"
    code, result = pair.run(pair.a, "canonical", "resume", "--adopt-remote")
    assert code == 3 and result["error"]["details"]["next_step"] == "spec-dock canonical resume --push-local"
    code, result = pair.run(pair.a, "canonical", "resume", "--push-local")
    assert code == 0 and result["data"]["result"]["pushed"] is True, result
    assert pair.remote_file("keep.md") == "k"
    code, result = pair.sync(pair.a)
    assert code == 0 and catalog_result(result)["result"] == "ok"


def test_the_baseline_survives_git_clean_and_still_detects_a_rewrite(pair: SyncPair) -> None:
    pair.write(pair.a, "a.md", "a\n")
    pair.advance(31)
    pair.sync(pair.a)
    git(pair.a, "clean", "-ffdx", "-q")
    assert not pair.catalog(pair.a).exists()
    code, result = pair.run(pair.a, "canonical", "link", "--no-schedule")
    assert code == 0, result
    _force(pair, _remote_commit(pair, {"x.md": "x\n"}, parent=None))
    _code, result = pair.sync(pair.a)
    assert catalog_result(result)["paused"] == "remote_rewritten"


def test_a_merge_failure_resumes_by_adoption(pair: SyncPair) -> None:
    pair.write(pair.a, "seed.md", "s\n")
    pair.advance(31)
    pair.sync(pair.a)
    pair.sync(pair.b)
    pair.write(pair.a, "topic", "file\n")
    pair.write(pair.b, "topic/inner.md", "dir\n")
    pair.advance(31)
    pair.sync(pair.a)
    _code, result = pair.sync(pair.b)
    assert catalog_result(result)["paused"] == "merge_failed"
    code, result = pair.run(pair.b, "canonical", "resume", "--adopt-remote")
    assert code == 0, result
    _code, result = pair.sync(pair.b)
    item = catalog_result(result)
    assert item["result"] == "paused" and item["paused"] == "merge_failed"  # still not expressible: stays paused
    assert (pair.specs(pair.b) / "topic/inner.md").read_text() == "dir\n"


def test_a_second_pc_resumes_remote_deleted_by_adopting_what_the_first_recreated(pair: SyncPair) -> None:
    pair.write(pair.a, "keep.md", "k\n")
    pair.advance(31)
    pair.sync(pair.a)
    pair.sync(pair.b)
    git(pair.remote, "update-ref", "-d", "refs/heads/spec-dock/canonical")
    for checkout in (pair.a, pair.b):
        _code, result = pair.sync(checkout)
        assert catalog_result(result)["paused"] == "remote_deleted"
    assert pair.run(pair.a, "canonical", "resume", "--push-local")[0] == 0
    code, result = pair.run(pair.b, "canonical", "resume", "--push-local")
    assert code == 3 and result["error"]["details"]["next_step"] == "spec-dock canonical resume --adopt-remote"
    code, result = pair.run(pair.b, "canonical", "resume", "--adopt-remote")
    assert code == 0, result
    _code, result = pair.sync(pair.b)
    assert catalog_result(result)["result"] == "ok"


def test_accepting_held_deletions_of_a_re_adoption_lets_it_finish(pair: SyncPair) -> None:
    for index in range(25):
        pair.write(pair.a, f"d/{index}.md", f"{index}\n")
    pair.advance(31)
    pair.sync(pair.a)
    old = pair.remote_head()
    for index in range(25):
        (pair.specs(pair.a) / f"d/{index}.md").unlink()
    pair.sync(pair.a)
    pair.advance(31)
    pair.sync(pair.a)
    pair.run(pair.a, "canonical", "accept", "--deletions")
    pair.sync(pair.a)
    assert pair.remote_file("d/0.md") is None
    _force(pair, old)  # GitHub goes back to the commit that still had the 25 files
    pair.sync(pair.a)
    pair.run(pair.a, "canonical", "resume", "--adopt-remote")
    _code, result = pair.sync(pair.a)
    item = catalog_result(result)
    assert item["paused"] == "remote_rewritten" and {hold["kind"] for hold in item["holds"]} == {"mass_delete"}
    code, result = pair.run(pair.a, "canonical", "accept", "--deletions")
    assert code == 0 and len(result["data"]["result"]["deletions"]) == 25
    pair.run(pair.a, "canonical", "resume", "--adopt-remote")
    _code, result = pair.sync(pair.a)
    item = catalog_result(result)
    assert item["result"] == "ok" and item["pushed"] is True, result
    assert pair.remote_file("d/0.md") is None


def test_a_rewrite_whose_branch_was_deleted_afterwards_resumes_by_push_local(pair: SyncPair) -> None:
    pair.write(pair.a, "a.md", "a\n")
    pair.advance(31)
    pair.sync(pair.a)
    _force(pair, _remote_commit(pair, {"x.md": "x\n"}, parent=None))
    _code, result = pair.sync(pair.a)
    assert catalog_result(result)["paused"] == "remote_rewritten"
    git(pair.remote, "update-ref", "-d", "refs/heads/spec-dock/canonical")
    code, result = pair.run(pair.a, "canonical", "resume", "--adopt-remote")
    assert code == 3 and result["error"]["details"]["next_step"] == "spec-dock canonical resume --push-local"
    code, result = pair.run(pair.a, "canonical", "resume", "--push-local")
    assert code == 0 and result["data"]["result"]["pushed"] is True, result
    assert pair.remote_file("a.md") == "a"


def test_accepting_a_fixed_but_unsaved_file_never_pushes_the_old_secret(pair: SyncPair) -> None:
    pair.write(pair.a, "base.md", "base\n")
    pair.write(pair.a, "leak.md", TOKEN + "\n")
    pair.advance(31)
    pair.sync(pair.a)
    pair.run(pair.a, "canonical", "accept", "leak.md")
    pair.sync(pair.a)
    cleaned = _remote_commit(pair, {"base.md": "base\n", ".spec-dock-canonical.json": '{"format": 1}\n'}, parent=None)
    _force(pair, cleaned)
    (pair.catalog(pair.a) / ".runtime/accepted.json").unlink()
    pair.sync(pair.a)
    pair.run(pair.a, "canonical", "resume", "--adopt-remote")
    pair.sync(pair.a)  # held: the secret would come back
    pair.write(pair.a, "leak.md", "fixed\n")
    pair.run(pair.a, "canonical", "accept", "leak.md")  # accepts the fixed, not yet saved content
    pair.run(pair.a, "canonical", "resume", "--adopt-remote")
    pair.sync(pair.a)
    assert TOKEN not in (pair.remote_file("leak.md") or "")
    pair.advance(31)
    pair.sync(pair.a)
    pair.sync(pair.a)
    assert pair.remote_file("leak.md") in (None, "fixed")


def test_an_accepted_file_under_a_clean_filter_lets_a_re_adoption_finish(pair: SyncPair) -> None:
    from pathlib import Path

    common = git(pair.catalog(pair.a), "rev-parse", "--path-format=absolute", "--git-common-dir")
    (Path(common) / "info").mkdir(exist_ok=True)
    (Path(common) / "info/attributes").write_text("*.md text eol=lf\n")  # CRLF in the file, LF committed
    pair.write(pair.a, "base.md", "base\n")
    (pair.write(pair.a, "leak.md", "")).write_bytes(TOKEN.encode() + b"\r\n")
    pair.advance(31)
    pair.sync(pair.a)
    pair.run(pair.a, "canonical", "accept", "leak.md")
    pair.sync(pair.a)
    assert pair.remote_file("leak.md") == TOKEN
    cleaned = _remote_commit(pair, {"base.md": "base\n", ".spec-dock-canonical.json": '{"format": 1}\n'}, parent=None)
    _force(pair, cleaned)
    (pair.catalog(pair.a) / ".runtime/accepted.json").unlink()
    pair.sync(pair.a)
    pair.run(pair.a, "canonical", "resume", "--adopt-remote")
    _code, result = pair.sync(pair.a)
    assert [hold["path"] for hold in catalog_result(result)["holds"]] == ["leak.md"]
    assert pair.run(pair.a, "canonical", "accept", "leak.md")[0] == 0  # the user accepts it once more
    pair.run(pair.a, "canonical", "resume", "--adopt-remote")
    _code, result = pair.sync(pair.a)
    item = catalog_result(result)
    assert item["holds"] == [] and item["pushed"] is True, result
    assert pair.remote_file("leak.md") == TOKEN


def test_a_re_adoption_waiting_for_a_held_fix_never_pushes_the_rewound_history(pair: SyncPair) -> None:
    pair.write(pair.a, "safe.md", "safe\n")
    pair.advance(31)
    pair.sync(pair.a)
    before = pair.remote_head()
    pair.write(pair.a, "secret.md", TOKEN + "\n")
    pair.advance(31)
    pair.sync(pair.a)
    pair.run(pair.a, "canonical", "accept", "secret.md")
    pair.sync(pair.a)
    dropped = pair.remote_head()
    assert dropped != before
    _force(pair, before)  # GitHub rewinds to an ancestor of the local HEAD, dropping the secret
    pair.advance(61)
    _code, result = pair.sync(pair.a)
    assert catalog_result(result)["paused"] == "remote_rewritten"
    assert pair.run(pair.a, "canonical", "resume", "--adopt-remote")[0] == 0
    (pair.specs(pair.a) / "secret.md").unlink()  # the fix, not saved yet within 30 seconds
    pair.advance(5)
    _code, result = pair.sync(pair.a)
    assert catalog_result(result)["pushed"] is False and pair.remote_head() == before, result
    pair.advance(31)
    pair.sync(pair.a)
    _code, result = pair.sync(pair.a)
    assert pair.remote_file("secret.md") is None and pair.remote_file("safe.md") == "safe"
    assert dropped not in _history(pair)


def test_push_local_is_refused_while_a_re_adoption_is_pending(pair: SyncPair) -> None:
    """iss-00436 (I-3 gate 8 ST-1): a branch deleted mid re-adoption is never recreated from the dropped history."""
    pair.write(pair.a, "safe.md", "safe\n")
    pair.advance(31)
    pair.sync(pair.a)
    before = pair.remote_head()
    pair.write(pair.a, "secret.md", TOKEN + "\n")
    pair.advance(31)
    pair.sync(pair.a)
    pair.run(pair.a, "canonical", "accept", "secret.md")
    pair.sync(pair.a)
    _force(pair, before)
    pair.advance(61)
    pair.sync(pair.a)
    assert pair.run(pair.a, "canonical", "resume", "--adopt-remote")[0] == 0
    git(pair.remote, "update-ref", "-d", "refs/heads/spec-dock/canonical")  # GitHub deletes it meanwhile
    pair.advance(61)
    _code, result = pair.sync(pair.a)
    assert catalog_result(result)["paused"] == "remote_deleted", result
    code, result = pair.run(pair.a, "canonical", "resume", "--push-local")
    assert (code, result["status"], result["error"]["code"]) == (3, "failed", "CANONICAL_PAUSED"), result
    assert result["error"]["details"]["adopt_remote_pending"] is True
    assert result["effects"] == [] and result["recovery"]
    assert git(pair.remote, "branch", "--list", "spec-dock/canonical") == ""
    state = pair.state(pair.a)
    assert state is not None and state.paused == "remote_deleted" and state.adopt_remote_pending is True
