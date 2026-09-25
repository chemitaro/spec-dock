"""Maintenance is cleared only after a recorded whole-group verification."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys
from typing import cast

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application import installation_update_vnext as installation_module  # noqa: E402
from spec_dock_runtime.cli.admission import AdmissionError, admit_writer  # noqa: E402
from spec_dock_runtime.cli.vnext_runtime import run_vnext  # noqa: E402
from spec_dock_runtime.infra.control_store import load_control, store_control  # noqa: E402
from spec_dock_runtime.infra.finalization_store import pending_finalizations  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import _ready_repo  # noqa: E402


def test_finalize_records_group_then_restores_ready(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    git_common = cast("Path", common["common_dir"])
    current = load_control(git_common)
    assert current is not None
    store_control(git_common, replace(current, mode="maintenance", epoch=2), expected_epoch=1)
    version = (repo / "spec-dock/spec-dock.version").read_text(encoding="utf-8").strip()
    record = installation_module.finalize_installation_group(
        repo_root=repo,
        common_dir=git_common,
        worktree_id="main",
        engine_digest="engine-a",
        expected_epoch=2,
        engine_version=version,
    )
    assert record.phase == "committed"
    assert record.targets == ("main",)
    after = load_control(git_common)
    assert after is not None and after.mode == "ready" and after.epoch == 3


def test_finalize_resumes_recorded_attempt_after_control_write_stops(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    git_common = cast("Path", common["common_dir"])
    current = load_control(git_common)
    assert current is not None
    store_control(git_common, replace(current, mode="maintenance", epoch=2), expected_epoch=1)
    version = (repo / "spec-dock/spec-dock.version").read_text(encoding="utf-8").strip()
    original = installation_module.store_control

    def stopped(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("control write stopped")

    monkeypatch.setattr(installation_module, "store_control", stopped)
    with pytest.raises(RuntimeError, match="control write stopped"):
        installation_module.finalize_installation_group(
            repo_root=repo,
            common_dir=git_common,
            worktree_id="main",
            engine_digest="engine-a",
            expected_epoch=2,
            engine_version=version,
        )
    (operation_id,) = pending_finalizations(git_common)
    assert load_control(git_common).mode == "maintenance"
    monkeypatch.setattr(installation_module, "store_control", original)
    resumed = installation_module.resume_installation_finalization(
        repo_root=repo,
        common_dir=git_common,
        worktree_id="main",
        engine_digest="engine-a",
        engine_version=version,
        operation_id=operation_id,
    )
    assert resumed.phase == "committed"
    assert pending_finalizations(git_common) == ()
    assert load_control(git_common).mode == "ready"


def test_ready_control_remains_blocked_until_commit_marker_is_recovered(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    git_common = cast("Path", common["common_dir"])
    current = load_control(git_common)
    assert current is not None
    store_control(git_common, replace(current, mode="maintenance", epoch=2), expected_epoch=1)
    version = (repo / "spec-dock/spec-dock.version").read_text(encoding="utf-8").strip()
    original = installation_module.write_finalization

    def stopped(common_dir: Path, record: installation_module.FinalizationRecord, *, create: bool = False) -> None:
        if record.phase == "committed":
            raise RuntimeError("commit marker stopped")
        original(common_dir, record, create=create)

    monkeypatch.setattr(installation_module, "write_finalization", stopped)
    with pytest.raises(RuntimeError, match="commit marker stopped"):
        installation_module.finalize_installation_group(
            repo_root=repo,
            common_dir=git_common,
            worktree_id="main",
            engine_digest="engine-a",
            expected_epoch=2,
            engine_version=version,
        )
    (operation_id,) = pending_finalizations(git_common)
    assert load_control(git_common).mode == "ready"
    with pytest.raises(AdmissionError, match="pending blocking journal"):
        admit_writer(
            load_control(git_common),
            common_dir=git_common,
            worktree_id="main",
            engine_digest="engine-a",
            expected_epoch=3,
        )
    monkeypatch.setattr(installation_module, "write_finalization", original)
    resumed = installation_module.resume_installation_finalization(
        repo_root=repo,
        common_dir=git_common,
        worktree_id="main",
        engine_digest="engine-a",
        engine_version=version,
        operation_id=operation_id,
    )
    assert resumed.phase == "committed" and pending_finalizations(git_common) == ()


def test_installation_update_finalization_cli_needs_no_second_archive(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    git_common = cast("Path", common["common_dir"])
    current = load_control(git_common)
    assert current is not None
    store_control(git_common, replace(current, mode="maintenance", epoch=2), expected_epoch=1)
    version = (repo / "spec-dock/spec-dock.version").read_text(encoding="utf-8").strip()
    output = run_vnext(
        ["installation", "update", "--finalize", "--yes", "--json"],
        invocation_cwd=repo,
        engine_digest="engine-a",
        engine_version=version,
    )
    assert output.exit_code == 0
    assert load_control(git_common).mode == "ready"


def test_installation_finalization_dry_run_checks_targets_without_writing(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    git_common = cast("Path", common["common_dir"])
    current = load_control(git_common)
    assert current is not None
    store_control(git_common, replace(current, mode="maintenance", epoch=2), expected_epoch=1)
    version = (repo / "spec-dock/spec-dock.version").read_text(encoding="utf-8").strip()
    output = run_vnext(
        ["installation", "update", "--finalize", "--dry-run", "--json"],
        invocation_cwd=repo,
        engine_digest="engine-a",
        engine_version=version,
    )
    assert output.exit_code == 0
    assert load_control(git_common).mode == "maintenance"
    assert pending_finalizations(git_common) == ()


def test_finalization_rejects_mixed_workspace_before_publishing_record(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    git_common = cast("Path", common["common_dir"])
    current = load_control(git_common)
    assert current is not None
    store_control(git_common, replace(current, mode="maintenance", epoch=2), expected_epoch=1)
    version = (repo / "spec-dock/spec-dock.version").read_text(encoding="utf-8").strip()
    workspace = repo / "spec-dock/workspace.json"
    workspace.write_text('{"schema_version":2}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="schema is not ready"):
        installation_module.finalize_installation_group(
            repo_root=repo,
            common_dir=git_common,
            worktree_id="main",
            engine_digest="engine-a",
            expected_epoch=2,
            engine_version=version,
        )
    assert load_control(git_common).mode == "maintenance"
    assert pending_finalizations(git_common) == ()
