"""Group update stages all linked worktrees and resumes a partly applied group."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys
from typing import cast

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock.installation.group_journal import read_group_record  # noqa: E402
from spec_dock_runtime.application.installation_update_vnext import (  # noqa: E402
    resume_installation_group,
    update_installation_group,
)
from spec_dock_runtime.application.worktree_vnext import create_worktree  # noqa: E402
from spec_dock_runtime.infra.control_store import load_control, store_control  # noqa: E402
from spec_dock_runtime.infra.installation_group_store import pending_installation_groups  # noqa: E402
from tests.cli_runtime.test_worktree_create_vnext import _committed_repo  # noqa: E402
from tests.integration.test_installation_journal_vnext import _bundle  # noqa: E402


def _group_fixture(tmp_path: Path):
    common = _committed_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    second = create_worktree(base="HEAD", name="planning", root=tmp_path / "worktrees", **common)
    common_dir = repo / ".git"
    control = load_control(common_dir)
    assert control is not None
    digest = "e" * 64
    next_control = replace(
        control,
        epoch=control.epoch + 1,
        engine_digest=digest,
        worktrees=tuple(replace(item, engine_digest=digest) for item in control.worktrees),
    )
    store_control(common_dir, next_control, expected_epoch=control.epoch)
    return repo, second.path, common_dir, next_control.epoch, digest, _bundle(tmp_path)


def test_group_update_keeps_all_worktrees_in_maintenance(tmp_path: Path) -> None:
    repo, second, common_dir, epoch, digest, bundle = _group_fixture(tmp_path)
    result = update_installation_group(
        repo_root=repo,
        common_dir=common_dir,
        worktree_id="main",
        engine_digest=digest,
        expected_epoch=epoch,
        bundle=bundle,
        keep_maintenance=True,
    )
    assert result.phase == "committed"
    assert len(result.targets) == 2 and all(target.completed for target in result.targets)
    assert pending_installation_groups(common_dir) == ()
    assert load_control(common_dir).mode == "maintenance"
    for root in (repo, second):
        assert (root / "spec-dock/docs/source.txt").read_text(encoding="utf-8") == "spec-dock/docs"


def test_group_update_resumes_after_one_child_completed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, second, common_dir, epoch, digest, bundle = _group_fixture(tmp_path)
    import spec_dock_runtime.application.installation_update_vnext as update_module

    real_apply = update_module.apply_installation
    attempts = 0

    def fail_second(*args: object, **kwargs: object):
        nonlocal attempts
        attempts += 1
        if attempts == 2:
            raise RuntimeError("injected group stop")
        return real_apply(*args, **kwargs)

    monkeypatch.setattr(update_module, "apply_installation", fail_second)
    with pytest.raises(RuntimeError, match="group stop"):
        update_installation_group(
            repo_root=repo,
            common_dir=common_dir,
            worktree_id="main",
            engine_digest=digest,
            expected_epoch=epoch,
            bundle=bundle,
            keep_maintenance=True,
        )
    (group_id,) = pending_installation_groups(common_dir)
    pending = read_group_record(common_dir, group_id)
    assert pending.phase == "recovery-required" and pending.targets[0].completed
    assert not pending.targets[1].completed
    monkeypatch.setattr(update_module, "apply_installation", real_apply)
    completed = resume_installation_group(
        repo_root=repo,
        common_dir=common_dir,
        worktree_id="main",
        engine_digest=digest,
        operation_id=group_id,
        bundle=bundle,
    )
    assert completed.phase == "committed" and pending_installation_groups(common_dir) == ()
    assert (second / "spec-dock/docs/source.txt").is_file()
