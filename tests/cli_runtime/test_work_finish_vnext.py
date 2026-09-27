"""Finishing work closes one Scope and clears only its selected subtree."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import TYPE_CHECKING

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application import work_lifecycle  # noqa: E402
from spec_dock_runtime.application.active_selection import select_scope  # noqa: E402
from spec_dock_runtime.application.scope_completion import change_scope_lifecycle  # noqa: E402
from spec_dock_runtime.application.work_lifecycle import finish_work, plan_finish_work, resume_finish_work  # noqa: E402
from spec_dock_runtime.domain.lifecycle import LocalBackend, SelectionState, decode_scope_metadata  # noqa: E402
from spec_dock_runtime.infra.active_store import load_selection_v3  # noqa: E402
from spec_dock_runtime.infra.github_lifecycle import RemoteIssueError  # noqa: E402
from spec_dock_runtime.infra.json_store import atomic_write_json, read_guarded_json  # noqa: E402
from spec_dock_runtime.infra.operation_journal import JournalStore  # noqa: E402
from tests.cli_runtime.test_active_vnext import _three_scopes  # noqa: E402
from tests.cli_runtime.test_scope_close_vnext import _Gateway  # noqa: E402

if TYPE_CHECKING:
    from spec_dock_runtime.domain.operation import OperationRecord


def test_issue_finish_preserves_selected_epic_and_initiative(tmp_path: Path) -> None:
    _root, views, initiative, epic, issue = _three_scopes(tmp_path)
    selected = select_scope(views, issue.id, current=SelectionState("main", 0, None, None, None, None))
    plan = plan_finish_work(
        views,
        target=issue.id,
        statuses={issue.id: "open"},
        selection=selected,
    )
    assert plan.target_id == issue.id
    assert plan.completion.after == "completed"
    assert plan.selection_after == SelectionState("main", 2, initiative.id, epic.id, None, epic.id)


def test_epic_finish_requires_completed_child_then_preserves_initiative(tmp_path: Path) -> None:
    _root, views, initiative, epic, issue = _three_scopes(tmp_path)
    selected = select_scope(views, issue.id, current=SelectionState("main", 0, None, None, None, None))
    plan = plan_finish_work(
        views,
        target=epic.id,
        statuses={epic.id: "open", issue.id: "completed"},
        selection=selected,
    )
    assert plan.target_id == epic.id
    assert plan.selection_after == SelectionState("main", 2, initiative.id, None, None, initiative.id)


def test_parent_finish_rejects_unfinished_descendant_before_selection_change(tmp_path: Path) -> None:
    _root, views, initiative, epic, issue = _three_scopes(tmp_path)
    selected = select_scope(views, issue.id, current=SelectionState("main", 0, None, None, None, None))
    with pytest.raises(ValueError, match="DESCENDANT_NOT_COMPLETED"):
        plan_finish_work(
            views,
            target=initiative.id,
            statuses={initiative.id: "open", epic.id: "completed", issue.id: "open"},
            selection=selected,
        )
    assert selected.focus_id == issue.id


def test_explicit_finish_outside_selected_chain_does_not_clear_selection(tmp_path: Path) -> None:
    _root, views, initiative, _epic, issue = _three_scopes(tmp_path)
    selected = select_scope(views, initiative.id, current=SelectionState("main", 0, None, None, None, None))
    plan = plan_finish_work(views, target=issue.id, statuses={issue.id: "open"}, selection=selected)
    assert plan.target_id == issue.id
    assert plan.selection_after == selected


def test_local_issue_finish_records_completion_and_clears_only_issue(tmp_path: Path) -> None:
    specdock_dir, views, initiative, epic, issue = _three_scopes(tmp_path)
    from spec_dock_runtime.infra.active_store import save_selection_v3

    selection = select_scope(views, issue.id, current=SelectionState("main", 0, None, None, None, None))
    save_selection_v3(specdock_dir, selection, views=views, expected_identity=None)
    result = finish_work(
        repo_root=specdock_dir.parent,
        common_dir=specdock_dir.parent / ".git",
        worktree_id="main",
        engine_digest="engine-a",
        expected_epoch=1,
        target="@current",
        updated_at="2026-09-25T00:00:00Z",
    )
    assert result.target_id == issue.id
    assert result.completion_changed
    assert result.selection_changed
    assert load_selection_v3(specdock_dir, worktree_id="main")[0] == SelectionState(
        "main", 2, initiative.id, epic.id, None, epic.id
    )
    loaded = read_guarded_json(issue.path / ".meta.json")
    assert loaded is not None
    backend = decode_scope_metadata(loaded[0]).backend
    assert isinstance(backend, LocalBackend) and backend.lifecycle.state == "completed"
    assert JournalStore(specdock_dir.parent / ".git").load(result.operation_id).terminal_status == "succeeded"


def test_finish_resume_after_lifecycle_write_keeps_fixed_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    specdock_dir, views, initiative, epic, issue = _three_scopes(tmp_path)
    from spec_dock_runtime.infra.active_store import save_selection_v3

    selected = select_scope(views, issue.id, current=SelectionState("main", 0, None, None, None, None))
    save_selection_v3(specdock_dir, selected, views=views, expected_identity=None)
    original_save = work_lifecycle.save_selection_v3
    calls = 0

    def fail_once(*args: object, **kwargs: object) -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise OSError("injected selection write failure")
        original_save(*args, **kwargs)

    monkeypatch.setattr(work_lifecycle, "save_selection_v3", fail_once)
    arguments = {
        "repo_root": specdock_dir.parent,
        "common_dir": specdock_dir.parent / ".git",
        "worktree_id": "main",
        "engine_digest": "engine-a",
        "expected_epoch": 1,
    }
    with pytest.raises(OSError, match="injected selection write failure"):
        finish_work(target="@current", updated_at="2026-09-25T00:00:00Z", **arguments)
    pending = JournalStore(arguments["common_dir"]).pending()
    assert len(pending) == 1 and pending[0].command == "work.finish"
    assert dict(pending[0].fixed_targets)["scope"] == issue.id
    assert dict(pending[0].fixed_targets)["worktree"] == "main"
    assert load_selection_v3(specdock_dir, worktree_id="main")[0] == selected
    with pytest.raises(ValueError, match="differs from the recorded request"):
        resume_finish_work(operation_id=pending[0].operation_id, **{**arguments, "worktree_id": "other"})
    recovered = resume_finish_work(operation_id=pending[0].operation_id, **arguments)
    assert recovered.target_id == issue.id
    assert load_selection_v3(specdock_dir, worktree_id="main")[0] == SelectionState(
        "main", 2, initiative.id, epic.id, None, epic.id
    )
    assert JournalStore(arguments["common_dir"]).load(pending[0].operation_id).terminal_status == "succeeded"


def test_already_completed_issue_finish_clears_selection_without_metadata_write(tmp_path: Path) -> None:
    specdock_dir, views, initiative, epic, issue = _three_scopes(tmp_path)
    from spec_dock_runtime.infra.active_store import save_selection_v3

    selected = select_scope(views, issue.id, current=SelectionState("main", 0, None, None, None, None))
    save_selection_v3(specdock_dir, selected, views=views, expected_identity=None)
    arguments = {
        "repo_root": specdock_dir.parent,
        "common_dir": specdock_dir.parent / ".git",
        "worktree_id": "main",
        "engine_digest": "engine-a",
        "expected_epoch": 1,
    }
    change_scope_lifecycle(target_id=issue.id, action="close", updated_at="2026-09-25T00:00:00Z", **arguments)
    before = (issue.path / ".meta.json").read_bytes()
    finished = finish_work(target=issue.id, updated_at="2026-09-25T01:00:00Z", **arguments)
    assert not finished.completion_changed and finished.selection_changed
    assert (issue.path / ".meta.json").read_bytes() == before
    assert load_selection_v3(specdock_dir, worktree_id="main")[0] == SelectionState(
        "main", 2, initiative.id, epic.id, None, epic.id
    )


def test_resume_observes_selection_published_before_journal_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    specdock_dir, views, initiative, epic, issue = _three_scopes(tmp_path)
    from spec_dock_runtime.infra.active_store import save_selection_v3

    selected = select_scope(views, issue.id, current=SelectionState("main", 0, None, None, None, None))
    save_selection_v3(specdock_dir, selected, views=views, expected_identity=None)
    original_update = JournalStore.update
    tripped = False

    def fail_after_selection(self: JournalStore, record: OperationRecord, *, expected_sequence: int) -> None:
        nonlocal tripped
        effects = record.effects
        if not tripped and effects and effects[-1].id == "selection-clear" and effects[-1].status == "succeeded":
            tripped = True
            raise OSError("injected journal publication failure")
        original_update(self, record, expected_sequence=expected_sequence)

    monkeypatch.setattr(JournalStore, "update", fail_after_selection)
    arguments = {
        "repo_root": specdock_dir.parent,
        "common_dir": specdock_dir.parent / ".git",
        "worktree_id": "main",
        "engine_digest": "engine-a",
        "expected_epoch": 1,
    }
    with pytest.raises(OSError, match="injected journal publication failure"):
        finish_work(target=issue.id, updated_at="2026-09-25T00:00:00Z", **arguments)
    current = load_selection_v3(specdock_dir, worktree_id="main")[0]
    assert current == SelectionState("main", 2, initiative.id, epic.id, None, epic.id)
    pending = JournalStore(arguments["common_dir"]).pending()
    assert len(pending) == 1 and pending[0].effects[-1].status == "intent"
    recovered = resume_finish_work(operation_id=pending[0].operation_id, **arguments)
    assert recovered.target_id == issue.id
    assert load_selection_v3(specdock_dir, worktree_id="main")[0] == current


def test_epic_and_initiative_finish_clear_one_selected_level_at_a_time(tmp_path: Path) -> None:
    specdock_dir, views, initiative, epic, issue = _three_scopes(tmp_path)
    from spec_dock_runtime.infra.active_store import save_selection_v3

    selected = select_scope(views, issue.id, current=SelectionState("main", 0, None, None, None, None))
    save_selection_v3(specdock_dir, selected, views=views, expected_identity=None)
    arguments = {
        "repo_root": specdock_dir.parent,
        "common_dir": specdock_dir.parent / ".git",
        "worktree_id": "main",
        "engine_digest": "engine-a",
        "expected_epoch": 1,
    }
    finish_work(target=issue.id, updated_at="2026-09-25T00:00:00Z", **arguments)
    finished_epic = finish_work(target=epic.id, updated_at="2026-09-25T01:00:00Z", **arguments)
    assert finished_epic.completion_changed and finished_epic.selection_changed
    assert load_selection_v3(specdock_dir, worktree_id="main")[0] == SelectionState(
        "main", 3, initiative.id, None, None, initiative.id
    )
    finished_initiative = finish_work(target="@current", updated_at="2026-09-25T02:00:00Z", **arguments)
    assert finished_initiative.target_id == initiative.id
    assert load_selection_v3(specdock_dir, worktree_id="main")[0] == SelectionState("main", 4, None, None, None, None)


def test_finish_resume_rejects_same_revision_metadata_tamper(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    specdock_dir, views, _initiative, _epic, issue = _three_scopes(tmp_path)
    from spec_dock_runtime.infra.active_store import save_selection_v3

    selected = select_scope(views, issue.id, current=SelectionState("main", 0, None, None, None, None))
    save_selection_v3(specdock_dir, selected, views=views, expected_identity=None)
    original_save = work_lifecycle.save_selection_v3

    def fail_selection(*args: object, **kwargs: object) -> None:
        raise OSError("injected selection failure")

    monkeypatch.setattr(work_lifecycle, "save_selection_v3", fail_selection)
    arguments = {
        "repo_root": specdock_dir.parent,
        "common_dir": specdock_dir.parent / ".git",
        "worktree_id": "main",
        "engine_digest": "engine-a",
        "expected_epoch": 1,
    }
    with pytest.raises(OSError, match="injected selection failure"):
        finish_work(target=issue.id, updated_at="2026-09-25T00:00:00Z", **arguments)
    pending = JournalStore(arguments["common_dir"]).pending()[0]
    path = issue.path / ".meta.json"
    metadata = json.loads(path.read_text(encoding="utf-8"))
    metadata["title"] = "Changed outside the operation"
    replacement = path.with_name(".meta-tampered.json")
    replacement.write_text(json.dumps(metadata), encoding="utf-8")
    replacement.replace(path)
    monkeypatch.setattr(work_lifecycle, "save_selection_v3", original_save)
    with pytest.raises(ValueError, match="metadata differs"):
        resume_finish_work(operation_id=pending.operation_id, **arguments)
    assert JournalStore(arguments["common_dir"]).load(pending.operation_id).terminal_status == "pending"


def test_github_issue_finish_updates_remote_then_clears_only_issue(tmp_path: Path) -> None:
    specdock_dir, views, initiative, epic, issue = _three_scopes(tmp_path)
    from spec_dock_runtime.infra.active_store import save_selection_v3

    path = issue.path / ".meta.json"
    loaded = read_guarded_json(path)
    assert loaded is not None
    metadata = loaded[0]
    metadata.update(
        backend="github", github={"issue_number": 47, "repo_owner": "example", "repo_name": "repo"}, lifecycle=None
    )
    atomic_write_json(path, metadata, expected_identity=loaded[1])
    before = path.read_bytes()
    selected = select_scope(views, issue.id, current=SelectionState("main", 0, None, None, None, None))
    save_selection_v3(specdock_dir, selected, views=views, expected_identity=None)
    gateway = _Gateway()
    result = finish_work(
        repo_root=specdock_dir.parent,
        common_dir=specdock_dir.parent / ".git",
        worktree_id="main",
        engine_digest="engine-a",
        expected_epoch=1,
        target=issue.id,
        updated_at="2026-09-25T00:00:00Z",
        gateway=gateway,
    )
    assert result.target_id == issue.id and result.completion_changed and result.selection_changed
    assert gateway.state == "completed" and gateway.set_calls == 1
    assert path.read_bytes() == before
    assert load_selection_v3(specdock_dir, worktree_id="main")[0] == SelectionState(
        "main", 2, initiative.id, epic.id, None, epic.id
    )


def test_github_finish_resume_after_remote_success_does_not_resend(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    specdock_dir, views, initiative, epic, issue = _three_scopes(tmp_path)
    from spec_dock_runtime.infra.active_store import save_selection_v3

    path = issue.path / ".meta.json"
    loaded = read_guarded_json(path)
    assert loaded is not None
    metadata = loaded[0]
    metadata.update(
        backend="github", github={"issue_number": 47, "repo_owner": "example", "repo_name": "repo"}, lifecycle=None
    )
    atomic_write_json(path, metadata, expected_identity=loaded[1])
    selected = select_scope(views, issue.id, current=SelectionState("main", 0, None, None, None, None))
    save_selection_v3(specdock_dir, selected, views=views, expected_identity=None)
    original_save = work_lifecycle.save_selection_v3

    def fail_selection(*args: object, **kwargs: object) -> None:
        raise OSError("injected selection failure")

    monkeypatch.setattr(work_lifecycle, "save_selection_v3", fail_selection)
    arguments = {
        "repo_root": specdock_dir.parent,
        "common_dir": specdock_dir.parent / ".git",
        "worktree_id": "main",
        "engine_digest": "engine-a",
        "expected_epoch": 1,
    }
    gateway = _Gateway()
    with pytest.raises(OSError, match="injected selection failure"):
        finish_work(target=issue.id, updated_at="2026-09-25T00:00:00Z", gateway=gateway, **arguments)
    pending = JournalStore(arguments["common_dir"]).pending()[0]
    assert pending.effects[0].kind == "remote" and pending.effects[0].status == "succeeded"
    monkeypatch.setattr(work_lifecycle, "save_selection_v3", original_save)
    recovered = resume_finish_work(operation_id=pending.operation_id, gateway=gateway, **arguments)
    assert recovered.target_id == issue.id
    assert gateway.set_calls == 1
    assert load_selection_v3(specdock_dir, worktree_id="main")[0] == SelectionState(
        "main", 2, initiative.id, epic.id, None, epic.id
    )


def test_uncertain_github_finish_waits_for_live_completed_observation_before_selection_clear(tmp_path: Path) -> None:
    specdock_dir, views, initiative, epic, issue = _three_scopes(tmp_path)
    from spec_dock_runtime.infra.active_store import save_selection_v3

    path = issue.path / ".meta.json"
    loaded = read_guarded_json(path)
    assert loaded is not None
    metadata = loaded[0]
    metadata.update(
        backend="github", github={"issue_number": 47, "repo_owner": "example", "repo_name": "repo"}, lifecycle=None
    )
    atomic_write_json(path, metadata, expected_identity=loaded[1])
    selected = select_scope(views, issue.id, current=SelectionState("main", 0, None, None, None, None))
    save_selection_v3(specdock_dir, selected, views=views, expected_identity=None)

    class UncertainGateway(_Gateway):
        def set_state(self, *_args: object, **_kwargs: object):
            self.set_calls += 1
            raise RemoteIssueError("GITHUB_TIMEOUT", uncertain=True)

    gateway = UncertainGateway()
    arguments = {
        "repo_root": specdock_dir.parent,
        "common_dir": specdock_dir.parent / ".git",
        "worktree_id": "main",
        "engine_digest": "engine-a",
        "expected_epoch": 1,
    }
    with pytest.raises(RemoteIssueError, match="GITHUB_TIMEOUT"):
        finish_work(target=issue.id, updated_at="2026-09-25T00:00:00Z", gateway=gateway, **arguments)
    pending = JournalStore(arguments["common_dir"]).pending()[0]
    assert pending.effects[0].status == "unknown"
    with pytest.raises(ValueError, match="refusing a blind retry"):
        resume_finish_work(operation_id=pending.operation_id, gateway=gateway, **arguments)
    assert gateway.set_calls == 1
    assert load_selection_v3(specdock_dir, worktree_id="main")[0] == selected
    gateway.state = "completed"
    recovered = resume_finish_work(operation_id=pending.operation_id, gateway=gateway, **arguments)
    assert recovered.target_id == issue.id and gateway.set_calls == 1
    assert load_selection_v3(specdock_dir, worktree_id="main")[0] == SelectionState(
        "main", 2, initiative.id, epic.id, None, epic.id
    )


def test_already_completed_github_issue_clears_selection_without_remote_write(tmp_path: Path) -> None:
    specdock_dir, views, initiative, epic, issue = _three_scopes(tmp_path)
    from spec_dock_runtime.infra.active_store import save_selection_v3

    path = issue.path / ".meta.json"
    loaded = read_guarded_json(path)
    assert loaded is not None
    metadata = loaded[0]
    metadata.update(
        backend="github", github={"issue_number": 47, "repo_owner": "example", "repo_name": "repo"}, lifecycle=None
    )
    atomic_write_json(path, metadata, expected_identity=loaded[1])
    selected = select_scope(views, issue.id, current=SelectionState("main", 0, None, None, None, None))
    save_selection_v3(specdock_dir, selected, views=views, expected_identity=None)
    gateway = _Gateway()
    gateway.state = "completed"
    result = finish_work(
        repo_root=specdock_dir.parent,
        common_dir=specdock_dir.parent / ".git",
        worktree_id="main",
        engine_digest="engine-a",
        expected_epoch=1,
        target=issue.id,
        updated_at="2026-09-25T00:00:00Z",
        gateway=gateway,
    )
    assert not result.completion_changed and result.selection_changed
    assert gateway.set_calls == 0
    assert load_selection_v3(specdock_dir, worktree_id="main")[0] == SelectionState(
        "main", 2, initiative.id, epic.id, None, epic.id
    )


def test_local_epic_finish_uses_live_github_descendant_state(tmp_path: Path) -> None:
    specdock_dir, views, initiative, epic, issue = _three_scopes(tmp_path)
    from spec_dock_runtime.infra.active_store import save_selection_v3

    path = issue.path / ".meta.json"
    loaded = read_guarded_json(path)
    assert loaded is not None
    metadata = loaded[0]
    metadata.update(
        backend="github", github={"issue_number": 47, "repo_owner": "example", "repo_name": "repo"}, lifecycle=None
    )
    atomic_write_json(path, metadata, expected_identity=loaded[1])
    selected = select_scope(views, issue.id, current=SelectionState("main", 0, None, None, None, None))
    save_selection_v3(specdock_dir, selected, views=views, expected_identity=None)
    gateway = _Gateway()
    arguments = {
        "repo_root": specdock_dir.parent,
        "common_dir": specdock_dir.parent / ".git",
        "worktree_id": "main",
        "engine_digest": "engine-a",
        "expected_epoch": 1,
        "gateway": gateway,
    }
    with pytest.raises(ValueError, match="DESCENDANT_NOT_COMPLETED"):
        finish_work(target=epic.id, updated_at="2026-09-25T00:00:00Z", **arguments)
    assert load_selection_v3(specdock_dir, worktree_id="main")[0] == selected
    gateway.state = "completed"
    finished = finish_work(target=epic.id, updated_at="2026-09-25T01:00:00Z", **arguments)
    assert finished.completion_changed and finished.selection_changed
    assert gateway.set_calls == 0
    assert load_selection_v3(specdock_dir, worktree_id="main")[0] == SelectionState(
        "main", 2, initiative.id, None, None, initiative.id
    )
