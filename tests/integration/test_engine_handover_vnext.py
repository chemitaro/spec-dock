"""Old and new fixed engines hand over through a recoverable maintenance record."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock.runtime_loader import (  # noqa: E402
    EnginePin,
    digest_distribution,
    read_engine_pin,
    verify_engine_pin,
    write_engine_pin,
)
from spec_dock_runtime.application import engine_handover_vnext as handover_module  # noqa: E402
from spec_dock_runtime.application.installation_update_vnext import (  # noqa: E402
    finalize_installation_group,
    update_installation_group,
)
from spec_dock_runtime.cli.admission import AdmissionError, admit_writer  # noqa: E402
from spec_dock_runtime.cli.vnext_runtime import run_vnext  # noqa: E402
from spec_dock_runtime.infra.control_store import load_control, store_control  # noqa: E402
from spec_dock_runtime.infra.engine_handover_store import pending_engine_handovers  # noqa: E402
from tests.integration.test_installation_group_update_vnext import _group_fixture  # noqa: E402


def _fixed_pin(tmp_path: Path, name: str, checkout: Path):
    root = tmp_path / name
    executable = root / "bin/spec-dock"
    executable.parent.mkdir(parents=True)
    executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    executable.chmod(0o755)
    (root / "identity.txt").write_text(name, encoding="utf-8")
    return verify_engine_pin(EnginePin(executable, root, digest_distribution(root)), checkout_root=checkout)


def _handover_fixture(tmp_path: Path):
    repo, second, common_dir, _epoch, _digest, bundle = _group_fixture(tmp_path)
    bundle = replace(bundle, source=replace(bundle.source, version=None))
    prior = _fixed_pin(tmp_path, "old-engine", repo)
    next_engine = _fixed_pin(tmp_path, "new-engine", repo)
    control = load_control(common_dir)
    assert control is not None
    replacement = replace(
        control,
        epoch=control.epoch + 1,
        engine_digest=prior.distribution_digest,
        worktrees=tuple(replace(item, engine_digest=prior.distribution_digest) for item in control.worktrees),
    )
    store_control(common_dir, replacement, expected_epoch=control.epoch)
    write_engine_pin(common_dir, prior)
    update = update_installation_group(
        repo_root=repo,
        common_dir=common_dir,
        worktree_id="main",
        engine_digest=prior.distribution_digest,
        expected_epoch=replacement.epoch,
        bundle=bundle,
        keep_maintenance=True,
    )
    assert update.phase == "committed" and load_control(common_dir).mode == "maintenance"
    return repo, second, common_dir, bundle, prior, next_engine, update


def test_engine_handover_rotates_locator_and_all_registrations(tmp_path: Path) -> None:
    repo, _second, common_dir, bundle, prior, next_engine, update = _handover_fixture(tmp_path)
    before = load_control(common_dir)
    assert before is not None
    record = handover_module.activate_engine_group(
        repo_root=repo,
        common_dir=common_dir,
        worktree_id="main",
        old_digest=prior.distribution_digest,
        expected_epoch=before.epoch,
        next_engine=next_engine,
        update_id=update.operation_id,
        bundle=bundle,
    )
    assert record.phase == "committed" and record.targets == tuple(item.worktree_id for item in update.targets)
    after = load_control(common_dir)
    assert after is not None and after.mode == "maintenance" and after.epoch == before.epoch + 1
    assert after.engine_digest == next_engine.distribution_digest
    assert all(item.engine_digest == next_engine.distribution_digest for item in after.worktrees)
    assert read_engine_pin(common_dir, checkout_root=repo) == next_engine
    assert pending_engine_handovers(common_dir) == ()


def test_engine_handover_resumes_after_locator_publish(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, _second, common_dir, bundle, prior, next_engine, update = _handover_fixture(tmp_path)
    before = load_control(common_dir)
    assert before is not None
    original = handover_module.store_control

    def stopped(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("control publish stopped")

    monkeypatch.setattr(handover_module, "store_control", stopped)
    with pytest.raises(RuntimeError, match="control publish stopped"):
        handover_module.activate_engine_group(
            repo_root=repo,
            common_dir=common_dir,
            worktree_id="main",
            old_digest=prior.distribution_digest,
            expected_epoch=before.epoch,
            next_engine=next_engine,
            update_id=update.operation_id,
            bundle=bundle,
        )
    (operation_id,) = pending_engine_handovers(common_dir)
    assert read_engine_pin(common_dir, checkout_root=repo, require_control_match=False) == next_engine
    assert load_control(common_dir).engine_digest == prior.distribution_digest
    with pytest.raises(AdmissionError, match="pending blocking journal"):
        admit_writer(
            load_control(common_dir),
            common_dir=common_dir,
            worktree_id="main",
            engine_digest=prior.distribution_digest,
            expected_epoch=before.epoch,
            maintenance_command="installation.update",
        )
    monkeypatch.setattr(handover_module, "store_control", original)
    resumed = handover_module.resume_engine_handover(
        repo_root=repo,
        common_dir=common_dir,
        worktree_id="main",
        next_engine=next_engine,
        operation_id=operation_id,
        bundle=bundle,
    )
    assert resumed.phase == "committed" and pending_engine_handovers(common_dir) == ()
    assert read_engine_pin(common_dir, checkout_root=repo) == next_engine


def test_engine_handover_rolls_back_before_other_writes(tmp_path: Path) -> None:
    repo, _second, common_dir, bundle, prior, next_engine, update = _handover_fixture(tmp_path)
    before = load_control(common_dir)
    assert before is not None
    record = handover_module.activate_engine_group(
        repo_root=repo,
        common_dir=common_dir,
        worktree_id="main",
        old_digest=prior.distribution_digest,
        expected_epoch=before.epoch,
        next_engine=next_engine,
        update_id=update.operation_id,
        bundle=bundle,
    )
    restored = handover_module.rollback_engine_handover(
        repo_root=repo,
        common_dir=common_dir,
        worktree_id="main",
        operation_id=record.operation_id,
        expected_next_digest=next_engine.distribution_digest,
    )
    assert restored.phase == "rolled-back" and pending_engine_handovers(common_dir) == ()
    assert read_engine_pin(common_dir, checkout_root=repo) == prior
    control = load_control(common_dir)
    assert control is not None and control.mode == "maintenance" and control.engine_digest == prior.distribution_digest


def test_engine_handover_resumes_after_control_publish(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, _second, common_dir, bundle, prior, next_engine, update = _handover_fixture(tmp_path)
    before = load_control(common_dir)
    assert before is not None
    original = handover_module.write_engine_handover

    def stopped(common: Path, record: handover_module.EngineHandoverRecord, *, create: bool = False) -> None:
        if record.phase == "committed":
            raise RuntimeError("commit marker stopped")
        original(common, record, create=create)

    monkeypatch.setattr(handover_module, "write_engine_handover", stopped)
    with pytest.raises(RuntimeError, match="commit marker stopped"):
        handover_module.activate_engine_group(
            repo_root=repo,
            common_dir=common_dir,
            worktree_id="main",
            old_digest=prior.distribution_digest,
            expected_epoch=before.epoch,
            next_engine=next_engine,
            update_id=update.operation_id,
            bundle=bundle,
        )
    (operation_id,) = pending_engine_handovers(common_dir)
    assert read_engine_pin(common_dir, checkout_root=repo) == next_engine
    assert load_control(common_dir).engine_digest == next_engine.distribution_digest
    monkeypatch.setattr(handover_module, "write_engine_handover", original)
    recovered = handover_module.resume_engine_handover(
        repo_root=repo,
        common_dir=common_dir,
        worktree_id="main",
        next_engine=next_engine,
        operation_id=operation_id,
        bundle=bundle,
    )
    assert recovered.phase == "committed" and pending_engine_handovers(common_dir) == ()


def test_engine_handover_rollback_rejects_later_control_epoch(tmp_path: Path) -> None:
    repo, _second, common_dir, bundle, prior, next_engine, update = _handover_fixture(tmp_path)
    before = load_control(common_dir)
    assert before is not None
    record = handover_module.activate_engine_group(
        repo_root=repo,
        common_dir=common_dir,
        worktree_id="main",
        old_digest=prior.distribution_digest,
        expected_epoch=before.epoch,
        next_engine=next_engine,
        update_id=update.operation_id,
        bundle=bundle,
    )
    current = load_control(common_dir)
    assert current is not None
    store_control(common_dir, replace(current, epoch=current.epoch + 1), expected_epoch=current.epoch)
    with pytest.raises(ValueError, match="epoch changed"):
        handover_module.rollback_engine_handover(
            repo_root=repo,
            common_dir=common_dir,
            worktree_id="main",
            operation_id=record.operation_id,
            expected_next_digest=next_engine.distribution_digest,
        )
    assert read_engine_pin(common_dir, checkout_root=repo) == next_engine


def test_external_entrypoint_allows_only_recorded_engine_handover(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, _second, common_dir, bundle, _prior, next_engine, update = _handover_fixture(tmp_path)
    import spec_dock.external_cli as external_module
    import spec_dock_runtime.commands.installation_vnext as command_module

    monkeypatch.setattr(external_module, "_executing_engine", lambda **_kwargs: next_engine)
    monkeypatch.setattr(command_module, "resolve_fixed_source", lambda **_kwargs: bundle.source)
    monkeypatch.setattr(command_module, "download_pinned_archive", lambda *_args, **_kwargs: b"archive")
    monkeypatch.setattr(command_module, "verify_pinned_archive", lambda *_args, **_kwargs: bundle)
    monkeypatch.setattr(command_module, "assert_candidate_assets_match_engine", lambda *_args: None)
    code = external_module.run_external(
        ["installation", "update", "--activate-engine", "--from-update", update.operation_id, "--yes", "--json"],
        executable=next_engine.executable,
        invocation_cwd=repo,
    )
    assert code == 0, capsys.readouterr()
    assert read_engine_pin(common_dir, checkout_root=repo) == next_engine


def test_engine_handover_cli_uses_new_engine_with_old_control(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, _second, common_dir, bundle, _prior, next_engine, update = _handover_fixture(tmp_path)
    import spec_dock_runtime.commands.installation_vnext as command_module

    monkeypatch.setattr(command_module, "resolve_fixed_source", lambda **_kwargs: bundle.source)
    monkeypatch.setattr(command_module, "download_pinned_archive", lambda *_args, **_kwargs: b"archive")
    monkeypatch.setattr(command_module, "verify_pinned_archive", lambda *_args, **_kwargs: bundle)
    monkeypatch.setattr(command_module, "assert_candidate_assets_match_engine", lambda *_args: None)
    result = run_vnext(
        ["installation", "update", "--activate-engine", "--from-update", update.operation_id, "--yes", "--json"],
        invocation_cwd=repo,
        engine_digest=next_engine.distribution_digest,
        engine_version="0.2.4",
        engine_pin=next_engine,
    )
    assert result.exit_code == 0, result.stdout
    assert json.loads(result.stdout)["data"]["phase"] == "committed"
    assert load_control(common_dir).engine_digest == next_engine.distribution_digest


def test_commit_pinned_update_can_finalize_after_engine_handover(tmp_path: Path) -> None:
    repo, _second, common_dir, bundle, prior, next_engine, update = _handover_fixture(tmp_path)
    before = load_control(common_dir)
    assert before is not None
    handover_module.activate_engine_group(
        repo_root=repo,
        common_dir=common_dir,
        worktree_id="main",
        old_digest=prior.distribution_digest,
        expected_epoch=before.epoch,
        next_engine=next_engine,
        update_id=update.operation_id,
        bundle=bundle,
    )
    after = load_control(common_dir)
    assert after is not None
    finalized = finalize_installation_group(
        repo_root=repo,
        common_dir=common_dir,
        worktree_id="main",
        engine_digest=next_engine.distribution_digest,
        expected_epoch=after.epoch,
        engine_version="0.2.4",
    )
    assert finalized.phase == "committed"
    assert load_control(common_dir).mode == "ready"
