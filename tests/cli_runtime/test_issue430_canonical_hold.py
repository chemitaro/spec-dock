"""`canonical accept` and `canonical restore` answering holds (iss-00430, AC-430-02, -14, -26)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.support.canonical_repo import git
from tests.support.canonical_sync import SyncPair, catalog_result

if TYPE_CHECKING:
    from pathlib import Path

TOKEN = "ghp_" + "Z" * 36


@pytest.fixture
def pair(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> SyncPair:
    return SyncPair.create(tmp_path, monkeypatch, capsys)


def _seed(pair: SyncPair, count: int = 25) -> None:
    for index in range(count):
        pair.write(pair.a, f"d/{index}.md", f"{index}\n")
    pair.advance(31)
    pair.sync(pair.a)


def _delete(pair: SyncPair, count: int = 25) -> None:
    for index in range(count):
        (pair.specs(pair.a) / f"d/{index}.md").unlink()
    pair.sync(pair.a)
    pair.advance(31)
    _code, result = pair.sync(pair.a)
    assert len(catalog_result(result)["holds"]) == count


def test_accepted_deletions_are_saved_and_pushed_by_the_next_sync(pair: SyncPair) -> None:
    _seed(pair)
    _delete(pair)
    assert pair.remote_file("d/0.md") == "0"
    code, result = pair.run(pair.a, "canonical", "accept", "--deletions")
    assert code == 0 and result["status"] == "succeeded" and len(result["data"]["result"]["deletions"]) == 25
    assert git(pair.catalog(pair.a), "status", "--porcelain", "--ignored", ".runtime") != ""
    code, result = pair.sync(pair.a)
    item = catalog_result(result)
    assert item["holds"] == [] and item["pushed"] is True
    assert pair.remote_file("d/0.md") is None
    accepted = (pair.catalog(pair.a) / ".runtime/accepted.json").read_text()
    assert '"deletions": []' in accepted


def test_restore_brings_held_deletions_back_and_leaves_recreated_files_alone(pair: SyncPair) -> None:
    _seed(pair)
    _delete(pair)
    pair.write(pair.a, "d/3.md", "recreated after the hold\n")
    code, result = pair.run(pair.a, "canonical", "restore")
    assert code == 0 and result["status"] == "succeeded", result
    restored = result["data"]["result"]["restored"]
    assert len(restored) == 24 and "d/3.md" not in restored
    assert (pair.specs(pair.a) / "d/0.md").read_text() == "0\n"
    assert (pair.specs(pair.a) / "d/3.md").read_text() == "recreated after the hold\n"
    assert git(pair.catalog(pair.a), "diff", "--cached", "--name-only") == ""
    code, result = pair.run(pair.a, "canonical", "restore", "d/3.md")
    assert code == 3 and result["error"]["code"] == "CANONICAL_NOT_HELD"
    assert (pair.specs(pair.a) / "d/3.md").read_text() == "recreated after the hold\n"


def test_an_accepted_secret_is_saved_until_its_content_changes(pair: SyncPair) -> None:
    pair.write(pair.a, "keys.md", TOKEN + "\n")
    pair.advance(31)
    _code, result = pair.sync(pair.a)
    assert catalog_result(result)["holds"][0]["kind"] == "secret"
    code, result = pair.run(pair.a, "canonical", "accept", "spec-dock/initiatives/keys.md")
    assert code == 0 and list(result["data"]["result"]["paths"]) == ["keys.md"]
    _code, result = pair.sync(pair.a)
    assert catalog_result(result)["holds"] == [] and pair.remote_file("keys.md") == TOKEN
    pair.write(pair.a, "keys.md", TOKEN + "\nmore " + "ghp_" + "Y" * 36 + "\n")
    pair.advance(31)
    _code, result = pair.sync(pair.a)
    assert [hold["path"] for hold in catalog_result(result)["holds"]] == ["keys.md"]
    assert pair.remote_file("keys.md") == TOKEN


def test_restore_of_a_held_file_absent_from_head_refuses_and_keeps_it(pair: SyncPair) -> None:
    pair.write(pair.a, "new-secret.md", TOKEN + "\n")
    pair.advance(31)
    pair.sync(pair.a)
    code, result = pair.run(pair.a, "canonical", "restore", "new-secret.md")
    assert code == 3 and result["error"]["code"] == "CANONICAL_NOT_RESTORABLE"
    assert (pair.specs(pair.a) / "new-secret.md").exists()


def test_a_fixed_secret_is_no_longer_restorable_and_saves_itself(pair: SyncPair) -> None:
    pair.write(pair.a, "notes.md", "plain\n")
    pair.advance(31)
    pair.sync(pair.a)
    pair.write(pair.a, "notes.md", TOKEN + "\n")
    pair.advance(31)
    pair.sync(pair.a)
    pair.write(pair.a, "notes.md", "fixed\n")
    code, result = pair.run(pair.a, "canonical", "restore", "notes.md")
    assert code == 3 and result["error"]["code"] == "CANONICAL_NOT_HELD"
    assert (pair.specs(pair.a) / "notes.md").read_text() == "fixed\n"
    pair.advance(31)
    pair.sync(pair.a)
    assert pair.remote_file("notes.md") == "fixed"


def test_accept_of_a_missing_path_writes_nothing(pair: SyncPair) -> None:
    code, result = pair.run(pair.a, "canonical", "accept", "nope.md")
    assert code == 3 and result["error"]["code"] == "CANONICAL_PATH_NOT_FOUND"
    assert not (pair.catalog(pair.a) / ".runtime/accepted.json").exists()


def test_an_expired_deletion_accept_never_lets_a_later_mass_delete_through(pair: SyncPair) -> None:
    _seed(pair)
    _delete(pair)
    remote_before = pair.remote_head()
    assert pair.run(pair.a, "canonical", "accept", "--deletions")[0] == 0
    assert pair.run(pair.a, "canonical", "restore")[0] == 0  # the user changed their mind
    pair.sync(pair.a)
    _delete(pair)  # the same 25 files are deleted again later
    pair.advance(31)
    _code, result = pair.sync(pair.a)
    assert len(catalog_result(result)["holds"]) == 25 and pair.remote_head() == remote_before
