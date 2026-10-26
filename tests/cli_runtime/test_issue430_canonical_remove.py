"""`canonical remove` (iss-00430, AC-430-08, -28): stop conditions, the plan, what goes and what stays."""

from __future__ import annotations

import os
import threading
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.infra.canonical_registry import read_registry
from spec_dock.runtime.infra.canonical_state import catalog_state_dir, cycle_lock
from tests.support.canonical_repo import add_worktree, git
from tests.support.canonical_sync import SyncPair

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def pair(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> SyncPair:
    created = SyncPair.create(tmp_path, monkeypatch, capsys, link=False)
    code, result = created.run(created.a, "canonical", "link")
    assert code == 0, result
    created.write(created.a, "plan.md", "p\n")
    created.advance(31)
    created.sync(created.a)
    return created


def _catalog(pair: SyncPair) -> str:
    return os.path.realpath(pair.catalog(pair.a))


def test_without_yes_remove_only_reports_the_plan(pair: SyncPair) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    before = tree_digest(pair.state_root), tree_digest(pair.a)
    code, result = pair.run(pair.a, "canonical", "remove")
    assert (tree_digest(pair.state_root), tree_digest(pair.a)) == before
    assert code == 0 and result["status"] == "planned", result
    kinds = [item["kind"] for item in result["effects"]]
    assert kinds == [
        "canonical.link.remove",
        "git.worktree.remove",
        "git.info.exclude",
        "canonical.scheduler",  # before the registry entry, so a failure can be retried by the same command
        "canonical.registry",
        "canonical.state",
    ]

    assert pair.catalog(pair.a).is_dir() and read_registry(pair.state_root).catalogs


@pytest.mark.parametrize("problem", ["unsaved", "unpushed", "ignored"])
def test_remove_stops_before_writing_on_unsaved_unpushed_or_ignored_files(pair: SyncPair, problem: str) -> None:
    catalog = pair.catalog(pair.a)
    if problem == "unsaved":
        pair.write(pair.a, "draft.md", "not saved\n")
        expected = "CANONICAL_UNSAVED_CHANGES"
    elif problem == "unpushed":
        git(pair.a, "remote", "set-url", "origin", str(pair.tmp_path / "gone.git"))
        pair.write(pair.a, "late.md", "l\n")
        pair.advance(31)
        pair.sync(pair.a)
        expected = "CANONICAL_UNSAVED_CHANGES"
    else:
        (catalog / "plan.workbench").mkdir()
        (catalog / ".gitignore").write_text((catalog / ".gitignore").read_text() + "*.workbench/\n")
        git(catalog, "add", ".gitignore")
        git(catalog, "commit", "-qm", "ignore")
        git(catalog, "push", "-q", "origin", "HEAD:refs/heads/spec-dock/canonical")
        git(catalog, "fetch", "-q", "origin")
        (catalog / "plan.workbench/notes.txt").write_text("keep me\n")
        expected = "CANONICAL_IGNORED_FILES_PRESENT"
    code, result = pair.run(pair.a, "canonical", "remove", "--yes")
    assert code == 3 and result["error"]["code"] == expected and result["effects"] == [], result
    assert catalog.is_dir() and (pair.a / "spec-dock/initiatives").is_symlink()
    if problem == "ignored":
        assert result["error"]["details"]["paths"] == ["plan.workbench/notes.txt"]


def test_remove_takes_away_links_catalog_exclude_registry_state_and_the_job(pair: SyncPair, tmp_path: Path) -> None:
    linked = add_worktree(pair.a, tmp_path / "linked", "feature")
    pair.run(linked, "canonical", "link")
    code, result = pair.run(pair.a, "canonical", "remove", "--yes")
    assert code == 0 and result["status"] == "succeeded", result
    assert not os.path.lexists(pair.a / "spec-dock/initiatives") and not os.path.lexists(
        linked / "spec-dock/initiatives"
    )
    assert not pair.catalog(pair.a).exists()
    exclude = (pair.a / ".git/info/exclude").read_text()
    assert "/spec-dock/.canonical/" not in exclude and "/spec-dock/initiatives" not in exclude
    assert read_registry(pair.state_root).catalogs == () and read_registry(pair.state_root).scheduler is None
    assert not catalog_state_dir(pair.state_root, _catalog(pair)).exists()
    assert ("remove", "launchd") in pair.schedulers["launchd"].calls
    assert git(pair.a, "rev-parse", "--verify", "refs/heads/spec-dock/canonical")
    assert pair.remote_file("plan.md") == "p"


def test_remove_keeps_the_job_while_another_catalog_is_registered(pair: SyncPair) -> None:
    pair.run(pair.b, "canonical", "link")
    code, result = pair.run(pair.a, "canonical", "remove", "--yes")
    assert code == 0, result
    assert ("remove", "launchd") not in pair.schedulers["launchd"].calls
    registry = read_registry(pair.state_root)
    assert [entry.catalog for entry in registry.catalogs] == [os.path.realpath(pair.catalog(pair.b))]
    assert registry.scheduler == "launchd"


def test_remove_waits_for_a_running_cycle_of_the_catalog(pair: SyncPair) -> None:
    held, release = threading.Event(), threading.Event()

    def cycle() -> None:
        with cycle_lock(pair.state_root, _catalog(pair)):
            held.set()
            release.wait(5)

    thread = threading.Thread(target=cycle)
    thread.start()
    held.wait(5)
    threading.Timer(0.5, release.set).start()
    code, result = pair.run(pair.a, "canonical", "remove", "--yes")
    thread.join()
    assert code == 0 and result["status"] == "succeeded", result


def test_a_failure_in_the_middle_is_partial_with_each_effect(pair: SyncPair, monkeypatch: pytest.MonkeyPatch) -> None:
    from spec_dock.runtime.application import canonical_remove

    def broken(path: object) -> None:
        raise OSError(5, "Input/output error")

    monkeypatch.setattr(canonical_remove, "_drop_exclude_lines", broken)
    code, result = pair.run(pair.a, "canonical", "remove", "--yes")
    assert code == 6 and result["status"] == "partial", result
    statuses = {item["kind"]: item["status"] for item in result["effects"]}
    assert statuses["git.worktree.remove"] == "succeeded" and statuses["git.info.exclude"] == "failed"
    assert statuses["canonical.registry"] == "not_attempted"


def test_remove_keeps_the_structure_snapshot(pair: SyncPair) -> None:
    snapshot = pair.state_root / "github/github.com/example/repo/snapshot.json"
    snapshot.parent.mkdir(parents=True)
    snapshot.write_text("{}")
    assert pair.run(pair.a, "canonical", "remove", "--yes")[0] == 0
    assert snapshot.read_text() == "{}"


def test_remove_stops_when_the_catalog_is_on_another_branch(pair: SyncPair) -> None:
    git(pair.catalog(pair.a), "switch", "-q", "-c", "elsewhere")
    code, result = pair.run(pair.a, "canonical", "remove", "--yes")
    assert code == 3 and result["error"]["code"] == "CANONICAL_PATH_OCCUPIED" and result["effects"] == []
    assert read_registry(pair.state_root).catalogs
