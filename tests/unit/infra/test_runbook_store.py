from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application.contracts import WorkflowNextRequest
        from spec_dock_runtime.application.workflow import workflow_next
        from spec_dock_runtime.domain.runbook import Runbook
        from spec_dock_runtime.domain.workflow_state import STRICT_LEGACY_AUTHORITY
        from spec_dock_runtime.infra import runbook_store
    finally:
        sys.path.pop(0)
    return WorkflowNextRequest, workflow_next, Runbook, STRICT_LEGACY_AUTHORITY, runbook_store


def _runbook() -> object:
    _, _, Runbook, authority, _ = _runtime_modules()
    return Runbook(
        schema_version="workflow-runbook-v1",
        workflow_target="issue-planning",
        state="requirement-capture",
        next_action="requirement-capture-required",
        reason_code="requirement-scaffold",
        authority=authority,
        commands=("./spec-dock/scripts/spec-dock active show",),
        notes=("Capture requirements first.",),
        stop_conditions=("Do not continue from scaffold requirements.",),
        details=(),
        active_issue_id="iss-00228",
    )


def test_runbook_store_writes_current_projection_paths_atomically(tmp_path: Path) -> None:
    _, _, _, _, runbook_store = _runtime_modules()
    store = runbook_store.RunbookStore(tmp_path)

    result = store.write_current(_runbook())

    assert result.written is True
    assert result.errors == ()
    assert result.paths == (
        "spec-dock/.agent/runbooks/current-runbook.json",
        "spec-dock/.agent/runbooks/current-runbook.md",
        "spec-dock/active/current-runbook.json",
        "spec-dock/active/current-runbook.md",
    )
    payload = json.loads((tmp_path / result.paths[0]).read_text(encoding="utf-8"))
    assert payload["state"] == "requirement-capture"
    assert payload["projection"]["written"] is True
    assert "state: requirement-capture" in (tmp_path / result.paths[3]).read_text(encoding="utf-8")


def test_runbook_store_failure_removes_temp_files_and_reports_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, _, _, _, runbook_store = _runtime_modules()
    store = runbook_store.RunbookStore(tmp_path)

    def fail_replace(_src: object, _dst: object) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr(runbook_store, "_replace_path", fail_replace)

    result = store.write_current(_runbook())

    assert result.written is False
    assert result.paths == ()
    assert result.errors
    assert not (tmp_path / "spec-dock/.agent/runbooks/current-runbook.json").exists()
    assert not list((tmp_path / "spec-dock/.agent/runbooks").glob("*.tmp"))


def test_runbook_store_replace_failure_preserves_existing_projection_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, _, _, _, runbook_store = _runtime_modules()
    store = runbook_store.RunbookStore(tmp_path)
    initial = store.write_current(_runbook())
    assert initial.written is True
    existing = {
        rel_path: (tmp_path / rel_path).read_text(encoding="utf-8")
        for rel_path in runbook_store.CURRENT_RUNBOOK_PATHS
    }
    replace_calls = 0

    def fail_second_replace(src: Path, dst: Path) -> None:
        nonlocal replace_calls
        replace_calls += 1
        if replace_calls == 2:
            raise OSError("replace failed after first path")
        src.replace(dst)

    monkeypatch.setattr(runbook_store, "_replace_path", fail_second_replace)

    result = store.write_current(_runbook())

    assert result.written is False
    assert result.paths == ()
    assert result.errors
    for rel_path, text in existing.items():
        assert (tmp_path / rel_path).read_text(encoding="utf-8") == text
    assert not list((tmp_path / "spec-dock/.agent/runbooks").glob("*.tmp"))
    assert not list((tmp_path / "spec-dock/active").glob("*.tmp"))


def test_workflow_next_returns_blocked_when_projection_write_fails() -> None:
    WorkflowNextRequest, workflow_next, _, _, runbook_store = _runtime_modules()

    result = workflow_next(
        WorkflowNextRequest(workflow_target="issue-planning"),
        store=_NoActiveStore(),
        runbook_store=_FailingRunbookStore(runbook_store.RunbookProjectionResult),
    )

    assert result.state.kind == "blocked"
    assert result.state.reason_code == "runbook-write-failure"
    assert result.runbook is not None
    assert result.runbook.state == "blocked"
    assert "doctor" in " ".join(result.runbook.commands)
    assert result.projection is not None
    assert result.projection.written is False
    assert result.projection.errors == ("cannot write projection",)


class _ActiveMissingError(Exception):
    reason = "active_issue_missing"


class _NoActiveStore:
    def resolve_issue_target(self, target: None) -> object:
        raise _ActiveMissingError

    def read_contract(self, target: object) -> object:
        raise AssertionError("no active target should not read assurance")

    def read_requirement_text(self, target: object) -> str | None:
        raise AssertionError("no active target should not read requirement")


class _FailingRunbookStore:
    def __init__(self, result_type: object) -> None:
        self._result_type = result_type

    def write_current(self, runbook: object) -> object:
        return self._result_type(written=False, paths=(), errors=("cannot write projection",))
