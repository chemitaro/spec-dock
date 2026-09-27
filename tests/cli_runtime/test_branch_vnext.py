"""Canonical branches bind one Scope to one existing Git ref without adoption."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
from typing import cast

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.active_selection import change_active_selection  # noqa: E402
from spec_dock_runtime.application.branch_vnext import (  # noqa: E402
    create_scope_branch,
    resume_scope_branch_create,
    scope_from_current_branch,
    show_scope_branch,
    switch_scope_branch,
)
from spec_dock_runtime.application.create_local_scope import create_local_scope  # noqa: E402
from spec_dock_runtime.domain.branch_binding import BranchBinding, bind_branch  # noqa: E402
from spec_dock_runtime.domain.registry import LocalIdRegistry  # noqa: E402
from spec_dock_runtime.infra.operation_journal import JournalStore  # noqa: E402
from spec_dock_runtime.infra.registry_store import RegistryStore  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import _ready_repo  # noqa: E402


def _committed_repo(tmp_path: Path):
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "commit",
            "--allow-empty",
            "-qm",
            "initial",
        ],
        check=True,
        capture_output=True,
    )
    initiative = create_local_scope(kind="initiative", title="Alpha", parent=None, ancestors=(), **common)
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "commit",
            "-qm",
            "fixture",
        ],
        check=True,
        capture_output=True,
    )
    return common, initiative


def test_branch_binding_rejects_second_scope_or_name_and_survives_id_reservation() -> None:
    state = LocalIdRegistry.empty()
    first = BranchBinding("init-local-00001", "init-local-00001-alpha", "a" * 40)
    bound = bind_branch(state, first)
    assert bound.branches == (first,)
    assert bind_branch(bound, first) == bound
    with pytest.raises(ValueError, match="already bound"):
        bind_branch(bound, BranchBinding("init-local-00001", "another", "a" * 40))
    with pytest.raises(ValueError, match="already bound"):
        bind_branch(bound, BranchBinding("init-local-00002", first.name, "a" * 40))


def test_branch_create_records_binding_without_checkout_or_tracked_change(tmp_path: Path) -> None:
    common, initiative = _committed_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    current = subprocess.run(
        ["git", "-C", str(repo), "branch", "--show-current"], check=True, capture_output=True, text=True
    ).stdout.strip()
    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    created = create_scope_branch(
        scope_id=initiative.id, base=head, name=None, **{k: v for k, v in common.items() if k != "updated_at"}
    )
    assert created.name == f"{initiative.id}-alpha"
    assert show_scope_branch(repo, cast("Path", common["common_dir"]), initiative.id) == created
    assert RegistryStore(cast("Path", common["common_dir"])).load()[0].branches[0].scope_id == initiative.id
    assert (
        subprocess.run(
            ["git", "-C", str(repo), "branch", "--show-current"], check=True, capture_output=True, text=True
        ).stdout.strip()
        == current
    )
    assert (
        subprocess.run(
            ["git", "-C", str(repo), "status", "--porcelain"], check=True, capture_output=True, text=True
        ).stdout.strip()
        == ""
    )
    with pytest.raises(ValueError, match="already bound"):
        create_scope_branch(
            scope_id=initiative.id, base=head, name=None, **{k: v for k, v in common.items() if k != "updated_at"}
        )


def test_branch_create_rejects_existing_unregistered_ref(tmp_path: Path) -> None:
    common, initiative = _committed_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    branch = f"{initiative.id}-alpha"
    subprocess.run(["git", "-C", str(repo), "branch", branch, head], check=True, capture_output=True)
    with pytest.raises(ValueError, match="BRANCH_ADOPTION_REQUIRED"):
        create_scope_branch(
            scope_id=initiative.id, base=head, name=None, **{k: v for k, v in common.items() if k != "updated_at"}
        )


def test_branch_switch_requires_clean_tree_and_keeps_active_selection(tmp_path: Path) -> None:
    common, initiative = _committed_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    created = create_scope_branch(
        scope_id=initiative.id, base=head, name=None, **{k: v for k, v in common.items() if k != "updated_at"}
    )
    scratch = repo / "dirty.txt"
    scratch.write_text("dirty", encoding="utf-8")
    with pytest.raises(ValueError, match="clean"):
        switch_scope_branch(scope_id=initiative.id, **{k: v for k, v in common.items() if k != "updated_at"})
    scratch.unlink()
    switched = switch_scope_branch(scope_id=initiative.id, **{k: v for k, v in common.items() if k != "updated_at"})
    assert switched.name == created.name
    assert (
        subprocess.run(
            ["git", "-C", str(repo), "branch", "--show-current"], check=True, capture_output=True, text=True
        ).stdout.strip()
        == created.name
    )


def test_active_from_branch_uses_only_exact_registered_binding(tmp_path: Path) -> None:
    common, initiative = _committed_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    arguments = {k: v for k, v in common.items() if k != "updated_at"}
    with pytest.raises(LookupError, match="canonical"):
        scope_from_current_branch(repo, cast("Path", common["common_dir"]))
    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    create_scope_branch(scope_id=initiative.id, base=head, name=None, **arguments)
    with pytest.raises(LookupError, match="canonical"):
        change_active_selection(from_branch=True, **arguments)
    switch_scope_branch(scope_id=initiative.id, **arguments)
    assert scope_from_current_branch(repo, cast("Path", common["common_dir"])) == initiative.id
    result = change_active_selection(from_branch=True, **arguments)
    assert result.changed and result.selection.focus_id == initiative.id


def test_branch_create_rejects_base_without_scope_and_invalid_unicode_name(tmp_path: Path) -> None:
    common, initiative = _committed_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    prior = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD^"], check=True, capture_output=True, text=True
    ).stdout.strip()
    arguments = {k: v for k, v in common.items() if k != "updated_at"}
    with pytest.raises(ValueError, match="missing Scope"):
        create_scope_branch(scope_id=initiative.id, base=prior, name=None, **arguments)
    with pytest.raises(ValueError, match="branch name"):
        create_scope_branch(scope_id=initiative.id, base="HEAD", name="日本語", **arguments)
    assert RegistryStore(cast("Path", common["common_dir"])).load()[0].branches == ()


def test_branch_switch_rejects_ref_moved_to_snapshot_without_scope(tmp_path: Path) -> None:
    common, initiative = _committed_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    arguments = {k: v for k, v in common.items() if k != "updated_at"}
    created = create_scope_branch(scope_id=initiative.id, base="HEAD", name=None, **arguments)
    subprocess.run(["git", "-C", str(repo), "branch", "-f", created.name, "HEAD^"], check=True, capture_output=True)
    with pytest.raises(ValueError, match="missing Scope"):
        switch_scope_branch(scope_id=initiative.id, **arguments)


def test_branch_switch_rejects_other_worktree_owner(tmp_path: Path) -> None:
    common, initiative = _committed_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    arguments = {k: v for k, v in common.items() if k != "updated_at"}
    created = create_scope_branch(scope_id=initiative.id, base="HEAD", name=None, **arguments)
    other = tmp_path / "other"
    subprocess.run(
        ["git", "-C", str(repo), "worktree", "add", str(other), created.name], check=True, capture_output=True
    )
    with pytest.raises(ValueError, match="another worktree"):
        switch_scope_branch(scope_id=initiative.id, **arguments)


def test_branch_switch_reports_post_checkout_hook_mutation(tmp_path: Path) -> None:
    common, initiative = _committed_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    arguments = {k: v for k, v in common.items() if k != "updated_at"}
    create_scope_branch(scope_id=initiative.id, base="HEAD", name=None, **arguments)
    hook = repo / ".git" / "hooks" / "post-checkout"
    hook.write_text("#!/bin/sh\necho changed > hook-change.txt\n", encoding="utf-8")
    hook.chmod(0o755)
    with pytest.raises(RuntimeError, match="checkout changed"):
        switch_scope_branch(scope_id=initiative.id, **arguments)


def test_branch_create_resume_binds_fixed_ref_after_registry_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    common, initiative = _committed_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    arguments = {k: v for k, v in common.items() if k != "updated_at"}
    original_bind = RegistryStore.bind_locked

    def fail_bind(_store: RegistryStore, _binding: BranchBinding):
        raise OSError("injected registry failure")

    monkeypatch.setattr(RegistryStore, "bind_locked", fail_bind)
    with pytest.raises(OSError, match="injected"):
        create_scope_branch(scope_id=initiative.id, base="HEAD", name=None, **arguments)
    monkeypatch.setattr(RegistryStore, "bind_locked", original_bind)
    common_dir = cast("Path", common["common_dir"])
    pending = JournalStore(common_dir).pending()
    assert len(pending) == 1 and pending[0].command == "branch.create"
    assert RegistryStore(common_dir).load()[0].branches == ()
    with pytest.raises(ValueError, match="recorded request"):
        resume_scope_branch_create(
            operation_id=pending[0].operation_id,
            expected_scope_id="init-local-99999",
            **arguments,
        )
    assert RegistryStore(common_dir).load()[0].branches == ()
    resumed = resume_scope_branch_create(
        operation_id=pending[0].operation_id, expected_scope_id=initiative.id, **arguments
    )
    assert resumed.name == f"{initiative.id}-alpha"
    assert show_scope_branch(repo, common_dir, initiative.id) == resumed
    assert JournalStore(common_dir).pending() == ()
    assert resume_scope_branch_create(operation_id=pending[0].operation_id, **arguments) == resumed


def test_branch_create_resume_reconciles_binding_after_journal_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    common, initiative = _committed_repo(tmp_path)
    arguments = {k: v for k, v in common.items() if k != "updated_at"}
    original_update = JournalStore.update

    def fail_after_bind(store: JournalStore, record, *, expected_sequence: int):
        if record.effects and record.effects[-1].id == "registry-bind" and record.effects[-1].status == "succeeded":
            raise OSError("injected journal failure")
        return original_update(store, record, expected_sequence=expected_sequence)

    monkeypatch.setattr(JournalStore, "update", fail_after_bind)
    with pytest.raises(OSError, match="injected"):
        create_scope_branch(scope_id=initiative.id, base="HEAD", name=None, **arguments)
    monkeypatch.setattr(JournalStore, "update", original_update)
    common_dir = cast("Path", common["common_dir"])
    pending = JournalStore(common_dir).pending()
    assert len(pending) == 1
    assert RegistryStore(common_dir).load()[0].branches[0].scope_id == initiative.id
    resumed = resume_scope_branch_create(operation_id=pending[0].operation_id, **arguments)
    assert resumed.scope_id == initiative.id
    assert JournalStore(common_dir).pending() == ()


def test_branch_create_resume_can_apply_prepared_fixed_operation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    common, initiative = _committed_repo(tmp_path)
    arguments = {k: v for k, v in common.items() if k != "updated_at"}
    original_update = JournalStore.update

    def fail_before_git(_store: JournalStore, _record, *, expected_sequence: int):
        raise OSError("injected intent failure")

    monkeypatch.setattr(JournalStore, "update", fail_before_git)
    with pytest.raises(OSError, match="injected"):
        create_scope_branch(scope_id=initiative.id, base="HEAD", name=None, **arguments)
    monkeypatch.setattr(JournalStore, "update", original_update)
    common_dir = cast("Path", common["common_dir"])
    pending = JournalStore(common_dir).pending()
    assert len(pending) == 1 and pending[0].effects == ()
    resumed = resume_scope_branch_create(operation_id=pending[0].operation_id, **arguments)
    assert resumed.scope_id == initiative.id
    assert JournalStore(common_dir).pending() == ()
