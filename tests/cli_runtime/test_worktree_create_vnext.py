"""A new worktree is pinned to an explicit base and starts with empty selection."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import cast

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.worktree_vnext import create_worktree, list_worktrees, show_worktree  # noqa: E402
from spec_dock_runtime.cli.options import parse_vnext  # noqa: E402
from spec_dock_runtime.infra.active_store import load_selection_v3  # noqa: E402
from spec_dock_runtime.infra.control_store import load_control  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import _ready_repo  # noqa: E402


def _committed_repo(tmp_path: Path) -> dict[str, object]:
    common = _ready_repo(tmp_path)
    repo_root = cast("Path", common["repo_root"])
    entrypoint = repo_root / "spec-dock" / "scripts" / "spec-dock"
    entrypoint.parent.mkdir(parents=True, exist_ok=True)
    entrypoint.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    (repo_root / "Makefile").write_text("init:\n\ttouch bootstrap-ran\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    return {key: common[key] for key in ("repo_root", "common_dir", "worktree_id", "engine_digest", "expected_epoch")}


def test_create_pins_explicit_base_and_uses_operational_branch_without_bootstrap(tmp_path: Path) -> None:
    common = _committed_repo(tmp_path)
    repo_root = cast("Path", common["repo_root"])
    base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_root, check=True, capture_output=True, text=True)
    result = create_worktree(
        base="HEAD",
        name="planning",
        root=tmp_path / "worktrees",
        **common,
    )
    assert result.id == "wt1"
    assert result.alias == "planning"
    assert result.branch == "worktree/wt1"
    assert result.commit == base.stdout.strip()
    assert result.path.is_dir()
    assert not (result.path / "bootstrap-ran").exists()
    assert load_selection_v3(result.path / "spec-dock", worktree_id=result.id)[0].focus_id is None
    control = load_control(repo_root / ".git")
    assert control is not None and any(item.id == result.id and item.alias == "planning" for item in control.worktrees)
    inventory = list_worktrees(repo_root=repo_root, common_dir=repo_root / ".git")
    observed = next(item for item in inventory if item.id == result.id)
    assert observed.path == result.path and observed.head == result.commit and observed.registered
    assert show_worktree(repo_root=repo_root, common_dir=repo_root / ".git", reference="wt:wt1") == observed
    assert show_worktree(repo_root=repo_root, common_dir=repo_root / ".git", reference="planning") == observed
    assert show_worktree(repo_root=repo_root, common_dir=repo_root / ".git", reference=str(result.path)) == observed


def test_create_rejects_unknown_base_and_reused_name_before_git_effect(tmp_path: Path) -> None:
    common = _committed_repo(tmp_path)
    root = tmp_path / "worktrees"
    with pytest.raises(ValueError, match="base"):
        create_worktree(base="missing-ref", name="planning", root=root, **common)
    assert not root.exists()
    create_worktree(base="HEAD", name="planning", root=root, **common)
    with pytest.raises(ValueError, match="name"):
        create_worktree(
            base="HEAD",
            name="planning",
            root=root,
            expected_epoch=2,
            **{k: v for k, v in common.items() if k != "expected_epoch"},
        )


def test_detached_source_can_create_from_explicit_base(tmp_path: Path) -> None:
    common = _committed_repo(tmp_path)
    repo_root = cast("Path", common["repo_root"])
    subprocess.run(["git", "switch", "--detach", "HEAD"], cwd=repo_root, check=True, capture_output=True)
    created = create_worktree(base="HEAD", name=None, root=tmp_path / "worktrees", **common)
    assert created.branch == "worktree/wt1"


def test_create_failure_records_target_and_refuses_blind_retry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from spec_dock_runtime.application import worktree_vnext as module

    common = _committed_repo(tmp_path)
    root = tmp_path / "worktrees"

    def interrupted(*_args: object) -> None:
        raise RuntimeError("simulated interruption")

    monkeypatch.setattr(module, "_materialize", interrupted)
    with pytest.raises(RuntimeError, match="worktree create stopped"):
        create_worktree(base="HEAD", name="planning", root=root, **common)
    record = cast("Path", common["common_dir"]) / "spec-dock/control/worktree-create/wt1.json"
    payload = json.loads(record.read_text(encoding="utf-8"))
    assert payload["status"] == "partial"
    assert payload["phase"] == "materialization"
    assert payload["branch"] == "worktree/wt1"
    assert payload["path"] == str(root / "repo/repo-wt1")
    with pytest.raises(ValueError, match=r"unresolved.*wt1"):
        create_worktree(base="HEAD", name="planning", root=root, **common)


def test_create_recovery_requires_effects_to_be_absent_before_reusing_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock_runtime.application import worktree_vnext as module

    common = _committed_repo(tmp_path)
    root = tmp_path / "worktrees"
    original = module.git_cli.add_worktree_at_commit

    def interrupted(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("stopped before Git mutation")

    monkeypatch.setattr(module.git_cli, "add_worktree_at_commit", interrupted)
    with pytest.raises(RuntimeError, match="worktree create stopped"):
        create_worktree(base="HEAD", name="planning", root=root, **common)
    with pytest.raises(ValueError, match="path still exists"):
        create_worktree(base="HEAD", name="planning", root=root, recover="wt1", **common)
    shutil.rmtree(root / "repo/repo-wt1")
    monkeypatch.setattr(module.git_cli, "add_worktree_at_commit", original)
    result = create_worktree(base="HEAD", name="planning", root=root, recover="wt1", **common)
    assert result.id == "wt1"
    record = cast("Path", common["common_dir"]) / "spec-dock/control/worktree-create/wt1.json"
    assert json.loads(record.read_text(encoding="utf-8"))["status"] == "succeeded"


def test_create_cli_exposes_explicit_target_recovery() -> None:
    parsed = parse_vnext(["worktree", "create", "--base", "main", "--recover", "wt3"])
    assert parsed.command_path == "worktree create"
    assert parsed.recover == "wt3"
