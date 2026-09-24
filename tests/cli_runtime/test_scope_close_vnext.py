"""Lifecycle policy uses each descendant's observed state, including no-op closes."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import cast

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.scope_completion import change_scope_lifecycle, plan_close, plan_reopen  # noqa: E402
from spec_dock_runtime.application.scope_query import load_scope_views  # noqa: E402
from spec_dock_runtime.domain.lifecycle import LocalBackend, ObservedState, decode_scope_metadata  # noqa: E402
from spec_dock_runtime.infra.contracts import GithubIssueRecord  # noqa: E402
from spec_dock_runtime.infra.json_store import atomic_write_json, read_guarded_json  # noqa: E402
from tests.cli_runtime.test_active_vnext import _three_scopes  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import _ready_repo  # noqa: E402


def test_completed_parent_rechecks_each_descendant_even_if_already_completed(tmp_path: Path) -> None:
    _root, views, initiative, epic, issue = _three_scopes(tmp_path)
    status = {initiative.id: "completed", epic.id: "completed", issue.id: "completed"}
    assert not plan_close(views, initiative.id, status, reason="completed").changed
    for blocked in ("open", "not-planned", "unknown"):
        status[issue.id] = blocked
        with pytest.raises(ValueError, match="DESCENDANT_NOT_COMPLETED"):
            plan_close(views, initiative.id, status, reason="completed")


def test_empty_parent_can_complete_and_not_planned_is_explicit(tmp_path: Path) -> None:
    _root, views, initiative, epic, issue = _three_scopes(tmp_path)
    status = {initiative.id: "open", epic.id: "open", issue.id: "open"}
    with pytest.raises(ValueError, match="DESCENDANT_NOT_COMPLETED"):
        plan_close(views, initiative.id, status)
    assert plan_close(views, initiative.id, status, reason="not-planned").changed
    status[issue.id] = "completed"
    assert plan_close(views, epic.id, status).changed
    status[epic.id] = "completed"
    assert plan_close(views, initiative.id, status).changed


def test_close_reason_conflict_and_reopen_ancestor_guard(tmp_path: Path) -> None:
    _root, views, initiative, epic, issue = _three_scopes(tmp_path)
    status = {initiative.id: "not-planned", epic.id: "completed", issue.id: "completed"}
    with pytest.raises(ValueError, match="TERMINAL_REASON_CONFLICT"):
        plan_close(views, initiative.id, status, reason="completed")
    with pytest.raises(ValueError, match="ANCESTOR_TERMINAL"):
        plan_reopen(views, issue.id, status)
    assert plan_reopen(views, initiative.id, status).changed


def test_local_close_and_reopen_persist_only_lifecycle(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    from spec_dock_runtime.application.create_local_scope import create_local_scope

    initiative = create_local_scope(kind="initiative", title="Init", parent=None, ancestors=(), **common)
    metadata_path = initiative.path / ".meta.json"
    before = read_guarded_json(metadata_path)
    assert before is not None
    arguments = {k: v for k, v in common.items() if k != "updated_at"}
    completed = change_scope_lifecycle(
        target_id=initiative.id,
        action="close",
        updated_at="2026-09-25T00:00:00Z",
        **arguments,
    )
    assert completed.changed and completed.decision.after == "completed"
    loaded = read_guarded_json(metadata_path)
    assert loaded is not None
    state = decode_scope_metadata(loaded[0])
    assert isinstance(state.backend, LocalBackend)
    assert state.backend.lifecycle.state == "completed"
    assert state.backend.lifecycle.revision == 1
    assert state.revision == 1
    assert load_scope_views(initiative.path.parents[1])[0].status.state == "completed"
    repeated = change_scope_lifecycle(
        target_id=initiative.id,
        action="close",
        updated_at="2026-09-25T01:00:00Z",
        **arguments,
    )
    assert not repeated.changed
    assert read_guarded_json(metadata_path)[0] == loaded[0]
    reopened = change_scope_lifecycle(
        target_id=initiative.id,
        action="reopen",
        updated_at="2026-09-25T02:00:00Z",
        **arguments,
    )
    assert reopened.changed and reopened.decision.after == "open"


class _Gateway:
    def __init__(self) -> None:
        self.state = "open"
        self.get_calls = 0
        self.set_calls = 0

    def _record(self) -> GithubIssueRecord:
        return GithubIssueRecord(
            47,
            "example/repo",
            "Issue",
            cast("ObservedState", self.state),
            "OPEN" if self.state == "open" else "CLOSED",
            None if self.state == "open" else "completed",
            "2026-09-25T00:00:00Z",
            "https://github.com/example/repo/issues/47",
        )

    def get(self, _repo: Path, repository: str, number: int) -> GithubIssueRecord:
        assert (repository, number) == ("example/repo", 47)
        self.get_calls += 1
        return self._record()

    def set_state(
        self, _repo: Path, repository: str, number: int, *, state: str, reason: str | None
    ) -> GithubIssueRecord:
        assert (repository, number) == ("example/repo", 47)
        assert (state, reason) in (("closed", "completed"), ("open", None))
        self.set_calls += 1
        self.state = "completed" if state == "closed" else "open"
        return self._record()


def test_github_close_uses_live_status_and_leaves_metadata_unchanged(tmp_path: Path) -> None:
    specdock_dir, _views, _initiative, epic, issue = _three_scopes(tmp_path)
    metadata_path = issue.path / ".meta.json"
    loaded = read_guarded_json(metadata_path)
    assert loaded is not None
    data = loaded[0]
    data.update(
        backend="github", github={"issue_number": 47, "repo_owner": "example", "repo_name": "repo"}, lifecycle=None
    )
    atomic_write_json(metadata_path, data, expected_identity=loaded[1])
    before = metadata_path.read_bytes()
    common = {
        "repo_root": specdock_dir.parent,
        "common_dir": (specdock_dir.parent / ".git").resolve(),
        "worktree_id": "main",
        "engine_digest": "engine-a",
        "expected_epoch": 1,
    }
    gateway = _Gateway()
    gateway.state = "unknown"
    with pytest.raises(ValueError, match="DESCENDANT_NOT_COMPLETED"):
        change_scope_lifecycle(
            target_id=epic.id,
            action="close",
            updated_at="2026-09-25T00:00:00Z",
            gateway=gateway,
            **common,
        )
    assert gateway.set_calls == 0
    gateway.state = "open"
    result = change_scope_lifecycle(
        target_id=issue.id,
        action="close",
        updated_at="2026-09-25T00:00:00Z",
        gateway=gateway,
        **common,
    )
    assert result.changed and gateway.get_calls == 2 and gateway.set_calls == 1
    assert metadata_path.read_bytes() == before
    repeated = change_scope_lifecycle(
        target_id=issue.id,
        action="close",
        updated_at="2026-09-25T01:00:00Z",
        gateway=gateway,
        **common,
    )
    assert not repeated.changed and gateway.set_calls == 1
    closed_epic = change_scope_lifecycle(
        target_id=epic.id,
        action="close",
        updated_at="2026-09-25T02:00:00Z",
        gateway=gateway,
        **common,
    )
    assert closed_epic.changed and gateway.set_calls == 1
