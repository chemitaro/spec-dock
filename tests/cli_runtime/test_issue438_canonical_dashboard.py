"""The dashboard of step 7 of `canonical sync` (iss-00438): when it is written, where, and what is recorded."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.runtime.domain.canonical_dashboard import DASHBOARD_FILES
from spec_dock.runtime.infra.canonical_files import is_regular_file
from tests.support.canonical_repo import add_worktree
from tests.support.canonical_sync import SyncPair, catalog_result

if TYPE_CHECKING:
    from tests.support.fake_github import FakeGithub


def _fake_structure(monkeypatch: pytest.MonkeyPatch) -> FakeGithub:
    from spec_dock.runtime.application import canonical_sync
    from spec_dock.runtime.infra.github_snapshot import clear_memory
    from spec_dock.runtime.infra.github_structure import GithubApi
    from tests.support.fake_github import FakeGithub

    fake = FakeGithub("example/repo")
    initiative = fake.scope("initiative", slug="plan", title="仕様の正本")
    epic = fake.scope("epic", slug="core", title="ダッシュボード", parent=initiative.number)
    fake.scope("issue", slug="ready", title="着手できる", parent=epic.number)
    fake.scope("issue", slug="doing-a", title="作業中 A", parent=epic.number, labels=("spec-dock:in-progress",))
    fake.scope("issue", slug="doing-b", title="作業中 B", parent=epic.number, labels=("spec-dock:in-progress",))
    blocked = fake.scope("issue", slug="blocked", title="前提待ち", parent=epic.number)
    fake.block(blocked.number, by=3)
    vendor = fake.add_issue(title="Vendor fix")
    waiting = fake.scope("issue", slug="vendor", title="外部待ち", parent=epic.number)
    fake.block(waiting.number, by=vendor.number)
    fake.scope("issue", slug="done", title="終わった", parent=epic.number, state="closed", state_reason="completed")
    clear_memory()
    monkeypatch.setattr(canonical_sync, "repository_of", lambda *_a, **_k: "github.com/example/repo")
    monkeypatch.setattr(canonical_sync, "github_api_for", lambda cwd: GithubApi(runner=fake, clock=fake.clock))
    return fake


@pytest.fixture
def pair(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> SyncPair:
    return SyncPair.create(tmp_path, monkeypatch, capsys)


def _directory(checkout: Path) -> Path:
    return checkout / "spec-dock"


def _stamps(checkout: Path) -> dict[str, tuple[int, str]]:
    return {
        name: ((_directory(checkout) / name).stat().st_mtime_ns, (_directory(checkout) / name).read_text())
        for name in DASHBOARD_FILES
        if is_regular_file(_directory(checkout) / name)
    }


def _dashboard_state(pair: SyncPair, checkout: Path) -> dict[str, Any] | None:
    state = pair.state(checkout)
    return dict(state.dashboard) if state is not None and state.dashboard is not None else None


def _repository(result: dict[str, Any]) -> dict[str, Any]:
    (repository,) = result["data"]["repositories"]
    return repository


def test_a_cycle_writes_the_five_files_in_the_main_checkout(pair: SyncPair, monkeypatch: pytest.MonkeyPatch) -> None:
    _fake_structure(monkeypatch)
    code, result = pair.sync(pair.a)
    assert code == 0 and _repository(result)["dashboards_written"] == 1, result
    assert sorted(_stamps(pair.a)) == sorted(DASHBOARD_FILES)
    dashboard = (_directory(pair.a) / "dashboard.md").read_text(encoding="utf-8")
    assert "## Doing\n- `iss-00004` 作業中 A\n- `iss-00005` 作業中 B\n" in dashboard
    assert "## Ready\n- `iss-00003` 着手できる\n" in dashboard
    assert "- `iss-00006` 前提待ち (blockers: iss-00003)" in dashboard
    assert "- `iss-00008` 外部待ち (blockers: #7)" in dashboard
    snapshot = pair.state_root / "github/github.com/example/repo/snapshot.json"
    assert f"- snapshot: `{snapshot}`" in dashboard
    tree = (_directory(pair.a) / "tree.puml").read_text(encoding="utf-8")
    assert 'package "init-00001\\n仕様の正本" as Ninit_00001 {' in tree and "iss-00009" not in tree
    assert "iss-00009\\n[DONE]" in (_directory(pair.a) / "tree-all.puml").read_text(encoding="utf-8")
    assert "N_iss_00003 --> " not in tree
    assert "Niss_00003 --> Niss_00006 : blocks" in (_directory(pair.a) / "deps-issues.puml").read_text()
    assert "Niss_00003 --> Niss_00006 : raw_direct" in (_directory(pair.a) / "deps-raw.puml").read_text()
    recorded = _dashboard_state(pair, pair.a)
    assert recorded is not None and recorded["error"] is None and len(recorded["input_hash"]) == 64
    assert recorded["written_at"] is not None


def test_an_unchanged_structure_writes_nothing_and_a_title_change_rewrites(
    pair: SyncPair, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = _fake_structure(monkeypatch)
    pair.sync(pair.a)
    before = _stamps(pair.a)
    recorded = _dashboard_state(pair, pair.a)
    pair.advance(61)
    code, result = pair.sync(pair.a)
    assert code == 0 and _repository(result)["dashboards_written"] == 0
    assert _stamps(pair.a) == before and _dashboard_state(pair, pair.a) == recorded

    fake.issue(3).title = "題名を変えた"
    fake.touch(3)
    pair.advance(61)
    code, result = pair.sync(pair.a)
    assert code == 0 and _repository(result)["dashboards_written"] == 1
    assert "- `iss-00003` 題名を変えた" in (_directory(pair.a) / "dashboard.md").read_text(encoding="utf-8")
    after = _stamps(pair.a)
    assert all(after[name][0] != before[name][0] for name in DASHBOARD_FILES)  # all five are redrawn


def test_only_a_missing_file_is_written_when_the_structure_is_unchanged(
    pair: SyncPair, monkeypatch: pytest.MonkeyPatch
) -> None:
    _fake_structure(monkeypatch)
    pair.sync(pair.a)
    before = _stamps(pair.a)
    (_directory(pair.a) / "deps-raw.puml").unlink()
    pair.advance(61)
    code, result = pair.sync(pair.a)
    assert code == 0 and _repository(result)["dashboards_written"] == 1
    after = _stamps(pair.a)
    assert after["deps-raw.puml"][1] == before["deps-raw.puml"][1]
    assert {name: after[name] for name in after if name != "deps-raw.puml"} == {
        name: before[name] for name in before if name != "deps-raw.puml"
    }


def test_a_directory_or_link_at_a_file_place_is_left_alone_and_recorded(
    pair: SyncPair, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _fake_structure(monkeypatch)
    (_directory(pair.a) / "tree.puml").mkdir()
    target = tmp_path / "elsewhere.txt"
    target.write_text("keep\n", encoding="utf-8")
    (_directory(pair.a) / "deps-raw.puml").symlink_to(target)
    code, result = pair.sync(pair.a)
    assert code == 0 and result["status"] in ("succeeded", "unchanged"), result
    assert catalog_result(result)["result"] == "ok"
    assert (_directory(pair.a) / "tree.puml").is_dir() and target.read_text(encoding="utf-8") == "keep\n"
    assert sorted(_stamps(pair.a)) == ["dashboard.md", "deps-issues.puml", "tree-all.puml"]
    error = _dashboard_state(pair, pair.a)["error"]  # type: ignore[index]
    assert error["code"] == "CANONICAL_DASHBOARD_OCCUPIED"
    assert error["paths"] == [str(_directory(pair.a) / "tree.puml"), str(_directory(pair.a) / "deps-raw.puml")]

    (_directory(pair.a) / "tree.puml").rmdir()
    (_directory(pair.a) / "deps-raw.puml").unlink()
    pair.advance(61)
    code, result = pair.sync(pair.a)
    assert code == 0 and sorted(_stamps(pair.a)) == sorted(DASHBOARD_FILES)
    assert _dashboard_state(pair, pair.a)["error"] is None  # type: ignore[index]


def test_a_linked_worktree_cycle_writes_only_in_the_main_checkout(
    pair: SyncPair, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _fake_structure(monkeypatch)
    worktree = add_worktree(pair.a, tmp_path / "work", "topic")
    code, result = pair.run(worktree, "canonical", "link", "--no-schedule")
    assert code == 0, result
    code, result = pair.sync(worktree)
    assert code == 0 and _repository(result)["dashboards_written"] == 1, result
    assert sorted(_stamps(pair.a)) == sorted(DASHBOARD_FILES)
    assert not any((_directory(worktree) / name).exists() for name in DASHBOARD_FILES)


def test_a_worktree_or_legacy_main_gets_nothing_and_its_state_stays(pair: SyncPair, tmp_path: Path) -> None:
    from spec_dock.runtime.application.canonical_dashboard import refresh_dashboard
    from spec_dock.runtime.domain.canonical_sync_state import RegistryEntry

    pair.write(pair.a, "x.md", "x\n")
    pair.advance(31)
    pair.sync(pair.a)
    catalog = os.path.realpath(pair.catalog(pair.a))
    state = pair.state(pair.a)
    worktree = add_worktree(pair.a, tmp_path / "work", "topic")
    for main, reason in ((worktree, "not_main"), (pair.a, "legacy_mode")):
        if reason == "legacy_mode":
            declaration = _directory(pair.a) / "workspace.json"
            payload = json.loads(declaration.read_text(encoding="utf-8"))
            declaration.write_text(json.dumps({**payload, "schema_version": 3}), encoding="utf-8")
        entry = RegistryEntry(catalog, str(main), "github.com/example/repo", "git", "2026-10-26T00:00:00Z")
        outcome = refresh_dashboard(
            entry,
            None,
            snapshot_path=Path("/s.json"),
            state_root=pair.state_root,
            now="2026-10-26T00:00:00Z",
            registered=False,
        )
        assert outcome.skipped == reason and not outcome.written
        assert pair.state(pair.a) == state
        assert not any((_directory(main) / name).exists() for name in DASHBOARD_FILES)


def test_without_a_snapshot_or_github_nothing_is_written_and_the_failure_is_recorded(
    pair: SyncPair, monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.application import canonical_sync

    monkeypatch.setattr(canonical_sync, "repository_of", lambda *_a, **_k: "github.com/example/repo")
    code, result = pair.sync(pair.a)  # SyncPair's gh api always fails
    assert code == 0 and _repository(result) == {
        "repository": "github.com/example/repo",
        "probe": "failed",
        "refreshed": False,
        "dashboards_written": 0,
    }
    assert _stamps(pair.a) == {}
    assert _dashboard_state(pair, pair.a)["error"]["code"] == "CANONICAL_DASHBOARD_FAILED"  # type: ignore[index]


def test_status_reports_the_dashboard_without_writing_or_asking_github(
    pair: SyncPair, monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    fake = _fake_structure(monkeypatch)
    code, result = pair.run(pair.a, "canonical", "status")
    assert result["data"]["dashboard"]["status"] == "missing"
    assert not [item for item in result["warnings"] if item["details"].get("item") == "dashboard"]
    pair.sync(pair.a)
    requests = len(fake.requests)
    before = tree_digest(pair.state_root), tree_digest(_directory(pair.a))
    code, result = pair.run(pair.a, "canonical", "status")
    assert (tree_digest(pair.state_root), tree_digest(_directory(pair.a))) == before
    assert len(fake.requests) == requests
    item = result["data"]["dashboard"]
    assert code == 0 and item["status"] == "ok" and item["files"] == dict.fromkeys(DASHBOARD_FILES, True)
    assert item["directory"] == str(_directory(pair.a)) and item["written_at"] and item["error"] is None

    (_directory(pair.a) / "tree.puml").unlink()
    (_directory(pair.a) / "tree.puml").mkdir()
    pair.advance(61)
    pair.sync(pair.a)
    code, result = pair.run(pair.a, "canonical", "status")
    item = result["data"]["dashboard"]
    assert code == 0 and item["status"] == "problem" and item["files"]["tree.puml"] is False
    (warning,) = [entry for entry in result["warnings"] if entry["details"].get("item") == "dashboard"]
    assert warning["code"] == "CANONICAL_DASHBOARD_OCCUPIED" and warning["details"]["next_step"]


def test_status_is_not_applicable_without_a_github_repository(pair: SyncPair) -> None:
    code, result = pair.run(pair.a, "canonical", "status")
    assert code == 0 and result["data"]["dashboard"]["status"] == "not_applicable"


def test_remove_plans_and_deletes_only_the_regular_dashboard_files(
    pair: SyncPair, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _fake_structure(monkeypatch)
    pair.sync(pair.a)
    (_directory(pair.a) / "tree.puml").unlink()
    (_directory(pair.a) / "tree.puml").mkdir()
    target = tmp_path / "kept.txt"
    target.write_text("keep\n", encoding="utf-8")
    (_directory(pair.a) / "deps-raw.puml").unlink()
    (_directory(pair.a) / "deps-raw.puml").symlink_to(target)
    files = [str(_directory(pair.a) / name) for name in ("dashboard.md", "tree-all.puml", "deps-issues.puml")]

    code, result = pair.run(pair.a, "canonical", "remove")
    assert code == 0 and result["status"] == "planned", result
    planned = [item["target"] for item in result["effects"] if item["kind"] == "canonical.dashboard.remove"]
    assert sorted(planned) == sorted(files) and all(Path(path).is_file() for path in files)

    code, result = pair.run(pair.a, "canonical", "remove", "--yes")
    assert code == 0, result
    assert not any(Path(path).exists() for path in files)
    assert (_directory(pair.a) / "tree.puml").is_dir() and (_directory(pair.a) / "deps-raw.puml").is_symlink()
    assert target.read_text(encoding="utf-8") == "keep\n"


def _refresh(pair: SyncPair, main: Path, snapshot: object, *, registered: bool = False) -> Any:
    from spec_dock.runtime.application.canonical_dashboard import refresh_dashboard
    from spec_dock.runtime.domain.canonical_sync_state import RegistryEntry

    entry = RegistryEntry(
        os.path.realpath(pair.catalog(pair.a)), str(main), "github.com/example/repo", "git", "2026-10-26T00:00:00Z"
    )
    return refresh_dashboard(
        entry,
        snapshot,  # type: ignore[arg-type]
        snapshot_path=Path("/s.json"),
        state_root=pair.state_root,
        now="2026-10-26T00:00:00Z",
        registered=registered,
    )


def _stored_snapshot(pair: SyncPair) -> Any:
    from spec_dock.runtime.infra.github_snapshot import SnapshotStore
    from spec_dock.runtime.infra.github_structure import GithubRepository

    snapshot, _ = SnapshotStore(pair.state_root, GithubRepository.parse("example/repo")).load()
    assert snapshot is not None
    return snapshot


def test_a_busy_cycle_lock_a_removed_registration_or_no_state_skip_without_touching_state(
    pair: SyncPair, monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.infra.canonical_state import catalog_state_dir, cycle_lock

    _fake_structure(monkeypatch)
    pair.sync(pair.a)
    snapshot = _stored_snapshot(pair)
    for name in DASHBOARD_FILES:
        (_directory(pair.a) / name).unlink()
    state = pair.state(pair.a)
    with cycle_lock(pair.state_root, os.path.realpath(pair.catalog(pair.a))):
        assert _refresh(pair, pair.a, snapshot).skipped == "cycle_busy"
    assert _refresh(pair, pair.a, snapshot, registered=True).skipped == "unregistered"  # --no-schedule link
    assert pair.state(pair.a) == state and _stamps(pair.a) == {}
    (catalog_state_dir(pair.state_root, os.path.realpath(pair.catalog(pair.a))) / "state.json").unlink()
    assert _refresh(pair, pair.a, snapshot).skipped == "no_state"
    assert pair.state(pair.a) is None and _stamps(pair.a) == {}


def test_a_failed_write_keeps_the_old_hash_so_the_next_cycle_redraws_all_five(
    pair: SyncPair, monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.application import canonical_dashboard

    _fake_structure(monkeypatch)
    pair.sync(pair.a)
    snapshot = _stored_snapshot(pair)
    old_hash = _dashboard_state(pair, pair.a)["input_hash"]  # type: ignore[index]
    original = canonical_dashboard.replace_text_file

    def failing(directory: Path, name: str, text: str) -> None:
        if name == "tree.puml":
            raise OSError(28, "No space left on device")
        original(directory, name, text)

    monkeypatch.setattr(canonical_dashboard, "replace_text_file", failing)
    outcome = _refresh(pair, pair.a, snapshot)  # a new snapshot path changes the hash: all five are wanted
    error = _dashboard_state(pair, pair.a)["error"]  # type: ignore[index]
    assert error["code"] == "CANONICAL_DASHBOARD_FAILED" and error["paths"] == [str(_directory(pair.a) / "tree.puml")]
    assert "tree.puml" not in outcome.written and _dashboard_state(pair, pair.a)["input_hash"] == old_hash  # type: ignore[index]
    monkeypatch.setattr(canonical_dashboard, "replace_text_file", original)
    assert sorted(_refresh(pair, pair.a, snapshot).written) == sorted(DASHBOARD_FILES)
    assert _dashboard_state(pair, pair.a)["error"] is None  # type: ignore[index]


def test_workspace_sync_draws_no_dashboard_in_either_mode(
    pair: SyncPair, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from spec_dock.cli import main
    from tests.cli_runtime.test_issue413_dependency import dependency_workspace

    _fake_structure(monkeypatch)
    pair.run(pair.a, "workspace", "sync")  # the bare-path origin stops it early; it never draws either way
    assert _stamps(pair.a) == {}
    (tmp_path / "legacy").mkdir()
    legacy, _parent, _child = dependency_workspace(tmp_path / "legacy")
    capsys.readouterr()
    assert main(["--project", str(legacy), "workspace", "sync", "--json"]) == 0
    assert not any((legacy / "spec-dock" / name).exists() for name in DASHBOARD_FILES)
