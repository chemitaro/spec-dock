"""Group update stages all linked worktrees and resumes a partly applied group."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from typing import cast

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock.installation.group_journal import read_group_record  # noqa: E402
from spec_dock.installation.journal import read_record  # noqa: E402
from spec_dock.installer import TOOL_DIRECTORIES  # noqa: E402
from spec_dock.runtime_loader import EnginePin, digest_distribution, verify_engine_pin  # noqa: E402
from spec_dock_runtime.application.installation_update_vnext import (  # noqa: E402
    resume_installation_group,
    rollback_installation_group,
    update_installation_group,
)
from spec_dock_runtime.application.migrate_workspace_vnext import inspect_workspace_migration  # noqa: E402
from spec_dock_runtime.application.worktree_vnext import create_worktree  # noqa: E402
from spec_dock_runtime.cli.vnext_runtime import run_vnext  # noqa: E402
from spec_dock_runtime.infra.control_store import load_control, store_control  # noqa: E402
from spec_dock_runtime.infra.installation_group_store import pending_installation_groups  # noqa: E402
from tests.cli_runtime.test_worktree_create_vnext import _committed_repo  # noqa: E402
from tests.integration.test_installation_group_init_vnext import _fresh_repo  # noqa: E402
from tests.integration.test_installation_journal_vnext import _bundle  # noqa: E402


def _legacy_fixture(tmp_path: Path):
    repo, second = _fresh_repo(tmp_path)
    for root in (repo, second):
        for relative in TOOL_DIRECTORIES:
            directory = root / relative
            directory.mkdir(parents=True)
            (directory / "old.txt").write_text("old", encoding="utf-8")
        (root / "spec-dock/spec-dock.version").write_text("legacy\n", encoding="utf-8")
        (root / "spec-dock/workspace.json").write_text('{"schema_version":1}\n', encoding="utf-8")
    distribution = tmp_path / "external"
    executable = distribution / "bin/spec-dock"
    executable.parent.mkdir(parents=True)
    executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    executable.chmod(0o755)
    pin = verify_engine_pin(EnginePin(executable, distribution, digest_distribution(distribution)), checkout_root=repo)
    return repo, second, pin, _bundle(tmp_path)


def test_legacy_update_bootstraps_maintenance_control_without_migrating_data(tmp_path: Path) -> None:
    repo, second, pin, bundle = _legacy_fixture(tmp_path)
    result = update_installation_group(
        repo_root=repo,
        common_dir=repo / ".git",
        worktree_id="main",
        engine_digest=pin.distribution_digest,
        expected_epoch=0,
        bundle=bundle,
        keep_maintenance=True,
        engine_pin=pin,
    )
    assert result.phase == "committed" and result.bootstrap
    assert load_control(repo / ".git").mode == "maintenance"
    assert all(item.schema_version == 1 for item in load_control(repo / ".git").worktrees)
    inventory = inspect_workspace_migration(repo)
    assert {item.registration_id for item in inventory.worktrees} == {
        item.id for item in load_control(repo / ".git").worktrees
    }
    for root in (repo, second):
        assert (root / "spec-dock/docs/source.txt").is_file()
        assert (root / "spec-dock/workspace.json").read_text(encoding="utf-8") == '{"schema_version":1}\n'


def test_legacy_update_cli_dry_run_then_bootstraps(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, second, pin, bundle = _legacy_fixture(tmp_path)
    import spec_dock_runtime.commands.installation_vnext as command_module

    monkeypatch.setattr(command_module, "resolve_fixed_source", lambda **_kwargs: bundle.source)
    monkeypatch.setattr(command_module, "download_pinned_archive", lambda *_args, **_kwargs: b"archive")
    monkeypatch.setattr(command_module, "verify_pinned_archive", lambda *_args, **_kwargs: bundle)
    monkeypatch.setattr(command_module, "assert_candidate_assets_match_engine", lambda *_args: None)
    command = ["installation", "update", "--commit", bundle.source.commit, "--maintenance", "--json"]
    preview = run_vnext(
        [*command, "--dry-run"],
        invocation_cwd=repo,
        engine_digest=pin.distribution_digest,
        engine_version="0.2.4",
        engine_pin=pin,
    )
    assert preview.exit_code == 0 and load_control(repo / ".git") is None
    result = run_vnext(
        [*command, "--yes"],
        invocation_cwd=repo,
        engine_digest=pin.distribution_digest,
        engine_version="0.2.4",
        engine_pin=pin,
    )
    assert result.exit_code == 0
    assert {item["root"] for item in json.loads(result.stdout)["data"]["targets"]} == {str(repo), str(second)}
    assert load_control(repo / ".git").mode == "maintenance"


def test_legacy_update_cli_resolves_symlinked_system_tempdir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, _, pin, bundle = _legacy_fixture(tmp_path)
    import spec_dock_runtime.commands.installation_vnext as command_module

    real_temp = tmp_path / "real-temp"
    real_temp.mkdir()
    aliased_temp = tmp_path / "temp-alias"
    aliased_temp.symlink_to(real_temp, target_is_directory=True)

    def aliased_temporary_directory(*, prefix: str) -> TemporaryDirectory[str]:
        return TemporaryDirectory(prefix=prefix, dir=aliased_temp)

    def checked_archive(_source: object, _archive: bytes, destination: Path):
        assert destination.parent == destination.parent.resolve(strict=True)
        return bundle

    monkeypatch.setattr(command_module, "TemporaryDirectory", aliased_temporary_directory)
    monkeypatch.setattr(command_module, "resolve_fixed_source", lambda **_kwargs: bundle.source)
    monkeypatch.setattr(command_module, "download_pinned_archive", lambda *_args, **_kwargs: b"archive")
    monkeypatch.setattr(command_module, "verify_pinned_archive", checked_archive)
    monkeypatch.setattr(command_module, "assert_candidate_assets_match_engine", lambda *_args: None)

    preview = run_vnext(
        ["installation", "update", "--commit", bundle.source.commit, "--maintenance", "--dry-run", "--json"],
        invocation_cwd=repo,
        engine_digest=pin.distribution_digest,
        engine_version="0.2.4",
        engine_pin=pin,
    )

    assert preview.exit_code == 0
    assert load_control(repo / ".git") is None


def test_installation_update_requires_confirmation_before_source_fetch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _, pin, bundle = _legacy_fixture(tmp_path)
    import spec_dock_runtime.commands.installation_vnext as command_module

    def unexpected_source(**_kwargs: object) -> None:
        raise AssertionError("source must not be fetched without confirmation")

    monkeypatch.setattr(command_module, "resolve_fixed_source", unexpected_source)
    result = run_vnext(
        ["installation", "update", "--commit", bundle.source.commit, "--maintenance", "--json"],
        invocation_cwd=repo,
        engine_digest=pin.distribution_digest,
        engine_version="0.2.4",
        engine_pin=pin,
    )
    assert result.exit_code != 0
    assert "--yes" in result.stdout
    assert load_control(repo / ".git") is None


def test_installation_update_rejects_another_candidates_assets_before_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _, pin, bundle = _legacy_fixture(tmp_path)
    import spec_dock_runtime.commands.installation_vnext as command_module

    monkeypatch.setattr(command_module, "resolve_fixed_source", lambda **_kwargs: bundle.source)
    monkeypatch.setattr(command_module, "download_pinned_archive", lambda *_args, **_kwargs: b"archive")
    monkeypatch.setattr(command_module, "verify_pinned_archive", lambda *_args, **_kwargs: bundle)
    result = run_vnext(
        ["installation", "update", "--commit", bundle.source.commit, "--maintenance", "--yes", "--json"],
        invocation_cwd=repo,
        engine_digest=pin.distribution_digest,
        engine_version="0.2.4",
        engine_pin=pin,
    )
    assert result.exit_code != 0
    assert "candidate assets differ" in result.stdout
    assert load_control(repo / ".git") is None


def test_legacy_update_resumes_if_control_publish_stops(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, second, pin, bundle = _legacy_fixture(tmp_path)
    import spec_dock_runtime.application.installation_update_vnext as module

    real_store = module.store_control

    def stop_before_control(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("control publish stopped")

    monkeypatch.setattr(module, "store_control", stop_before_control)
    with pytest.raises(RuntimeError, match="control publish stopped"):
        update_installation_group(
            repo_root=repo,
            common_dir=repo / ".git",
            worktree_id="main",
            engine_digest=pin.distribution_digest,
            expected_epoch=0,
            bundle=bundle,
            keep_maintenance=True,
            engine_pin=pin,
        )
    (operation_id,) = pending_installation_groups(repo / ".git")
    assert load_control(repo / ".git") is None
    monkeypatch.setattr(module, "store_control", real_store)
    completed = resume_installation_group(
        repo_root=repo,
        common_dir=repo / ".git",
        worktree_id="main",
        engine_digest=pin.distribution_digest,
        operation_id=operation_id,
        bundle=bundle,
        engine_pin=pin,
    )
    assert completed.phase == "committed" and completed.bootstrap
    assert load_control(repo / ".git").mode == "maintenance"
    assert (second / "spec-dock/docs/source.txt").is_file()


def test_legacy_update_can_rollback_before_control_is_published(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, second, pin, bundle = _legacy_fixture(tmp_path)
    import spec_dock_runtime.application.installation_update_vnext as module

    def stop_before_control(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("control publish stopped")

    monkeypatch.setattr(module, "store_control", stop_before_control)
    with pytest.raises(RuntimeError, match="control publish stopped"):
        update_installation_group(
            repo_root=repo,
            common_dir=repo / ".git",
            worktree_id="main",
            engine_digest=pin.distribution_digest,
            expected_epoch=0,
            bundle=bundle,
            keep_maintenance=True,
            engine_pin=pin,
        )
    (operation_id,) = pending_installation_groups(repo / ".git")
    with pytest.raises(ValueError, match="rollback eligible"):
        rollback_installation_group(
            repo_root=repo,
            common_dir=repo / ".git",
            worktree_id="main",
            engine_digest=pin.distribution_digest,
            operation_id=operation_id,
            expected_source_commit="f" * 40,
        )
    assert pending_installation_groups(repo / ".git") == (operation_id,)
    restored = rollback_installation_group(
        repo_root=repo,
        common_dir=repo / ".git",
        worktree_id="main",
        engine_digest=pin.distribution_digest,
        operation_id=operation_id,
        expected_source_commit=bundle.source.commit,
    )
    assert restored.phase == "rolled-back" and load_control(repo / ".git") is None
    for root in (repo, second):
        assert (root / "spec-dock/docs/old.txt").read_text(encoding="utf-8") == "old"


def test_legacy_update_rollback_restores_tooling_and_disables_writer(tmp_path: Path) -> None:
    repo, second, pin, bundle = _legacy_fixture(tmp_path)
    committed = update_installation_group(
        repo_root=repo,
        common_dir=repo / ".git",
        worktree_id="main",
        engine_digest=pin.distribution_digest,
        expected_epoch=0,
        bundle=bundle,
        keep_maintenance=True,
        engine_pin=pin,
    )
    restored = rollback_installation_group(
        repo_root=repo,
        common_dir=repo / ".git",
        worktree_id="main",
        engine_digest=pin.distribution_digest,
        operation_id=committed.operation_id,
    )
    assert restored.phase == "rolled-back"
    assert load_control(repo / ".git").mode == "uninitialized"
    for root in (repo, second):
        assert (root / "spec-dock/docs/old.txt").read_text(encoding="utf-8") == "old"


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
    assert result.requested_version == "0.2.4" and result.version_tracked
    assert len(result.targets) == 2 and all(target.completed for target in result.targets)
    assert pending_installation_groups(common_dir) == ()
    assert load_control(common_dir).mode == "maintenance"
    for root in (repo, second):
        assert (root / "spec-dock/docs/source.txt").read_text(encoding="utf-8") == "spec-dock/docs"


def test_existing_group_accepts_new_candidate_assets_only_under_maintenance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, second, common_dir, _epoch, digest, bundle = _group_fixture(tmp_path)
    import spec_dock_runtime.commands.installation_vnext as command_module

    monkeypatch.setattr(command_module, "resolve_fixed_source", lambda **_kwargs: bundle.source)
    monkeypatch.setattr(command_module, "download_pinned_archive", lambda *_args, **_kwargs: b"archive")
    monkeypatch.setattr(command_module, "verify_pinned_archive", lambda *_args, **_kwargs: bundle)
    monkeypatch.setattr(
        command_module,
        "assert_candidate_assets_match_engine",
        lambda *_args: (_ for _ in ()).throw(ValueError("candidate assets differ from engine")),
    )
    command = ["installation", "update", "--commit", bundle.source.commit, "--yes", "--json"]
    refused = run_vnext(command, invocation_cwd=repo, engine_digest=digest, engine_version="0.2.4")
    assert refused.exit_code != 0 and "candidate assets differ" in refused.stdout
    assert load_control(common_dir).mode == "ready"
    accepted = run_vnext([*command, "--maintenance"], invocation_cwd=repo, engine_digest=digest, engine_version="0.2.4")
    assert accepted.exit_code == 0, accepted.stdout
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


def test_group_update_resumes_after_unjournaled_stage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, _, common_dir, epoch, digest, bundle = _group_fixture(tmp_path)
    import spec_dock_runtime.application.installation_update_vnext as update_module

    real_prepare = update_module.prepare_installation

    def stop_during_stage(target: Path, journal_root: Path, **kwargs: object):
        operation_id = kwargs["operation_id"]
        assert isinstance(operation_id, str)
        area = target / ".spec-dock-installations" / operation_id
        area.mkdir(mode=0o700, parents=True)
        (area / "stage").mkdir()
        raise RuntimeError("injected staging stop")

    monkeypatch.setattr(update_module, "prepare_installation", stop_during_stage)
    with pytest.raises(RuntimeError, match="staging stop"):
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
    monkeypatch.setattr(update_module, "prepare_installation", real_prepare)
    completed = resume_installation_group(
        repo_root=repo,
        common_dir=common_dir,
        worktree_id="main",
        engine_digest=digest,
        operation_id=group_id,
        bundle=bundle,
    )
    assert completed.phase == "committed"
    assert pending_installation_groups(common_dir) == ()


@pytest.mark.parametrize("recover_by", ["resume", "rollback"])
def test_group_recovers_interrupted_marker_publication_with_fixed_child_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, recover_by: str
) -> None:
    repo, _second, common_dir, epoch, digest, bundle = _group_fixture(tmp_path)
    import spec_dock.installation.executor as executor

    with monkeypatch.context() as patch:
        patch.setattr(executor.os, "link", lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("marker stop")))
        with pytest.raises(OSError, match="marker stop"):
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
    group = read_group_record(common_dir, group_id)
    first = group.targets[0]
    assert first.child_operation_id is not None
    # The group store's fixed child root is the authoritative location.
    from spec_dock_runtime.application.installation_update_vnext import _child_root

    child = read_record(_child_root(common_dir, group_id, first.worktree_id), first.child_operation_id)
    assert child.phase == "planned"
    if recover_by == "resume":
        result = resume_installation_group(
            repo_root=repo,
            common_dir=common_dir,
            worktree_id="main",
            engine_digest=digest,
            operation_id=group_id,
            bundle=bundle,
        )
        assert result.phase == "committed"
    else:
        result = rollback_installation_group(
            repo_root=repo,
            common_dir=common_dir,
            worktree_id="main",
            engine_digest=digest,
            operation_id=group_id,
            expected_source_commit=bundle.source.commit,
        )
        assert result.phase == "rolled-back"
    assert (Path(first.root) / ".spec-dock-installations/.gitignore").read_bytes() == b"*\n"
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=first.root,
        check=True,
        capture_output=True,
        text=True,
    )
    assert ".spec-dock-installations" not in status.stdout


def test_group_resume_refuses_target_changed_after_planned_child(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _second, common_dir, epoch, digest, bundle = _group_fixture(tmp_path)
    import spec_dock.installation.executor as executor

    with monkeypatch.context() as patch:
        patch.setattr(executor.os, "link", lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("marker stop")))
        with pytest.raises(OSError, match="marker stop"):
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
    group = read_group_record(common_dir, group_id)
    first = group.targets[0]
    version = Path(first.root) / "spec-dock/spec-dock.version"
    version.write_text("changed after interruption\n", encoding="utf-8")
    with pytest.raises(ValueError, match="changed after planning"):
        resume_installation_group(
            repo_root=repo,
            common_dir=common_dir,
            worktree_id="main",
            engine_digest=digest,
            operation_id=group_id,
            bundle=bundle,
        )
    assert version.read_text(encoding="utf-8") == "changed after interruption\n"
    assert pending_installation_groups(common_dir) == (group_id,)


def test_group_resume_preserves_original_version_request(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, second, common_dir, epoch, digest, versioned_bundle = _group_fixture(tmp_path)
    bundle = replace(versioned_bundle, source=replace(versioned_bundle.source, version=None))
    import spec_dock.installation.executor as executor

    with monkeypatch.context() as patch:
        patch.setattr(executor.os, "link", lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("marker stop")))
        with pytest.raises(OSError, match="marker stop"):
            update_installation_group(
                repo_root=repo,
                common_dir=common_dir,
                worktree_id="main",
                engine_digest=digest,
                expected_epoch=epoch,
                bundle=bundle,
                requested_version="0.2.4",
                keep_maintenance=True,
            )
    (group_id,) = pending_installation_groups(common_dir)
    resumed = resume_installation_group(
        repo_root=repo,
        common_dir=common_dir,
        worktree_id="main",
        engine_digest=digest,
        operation_id=group_id,
        bundle=bundle,
    )
    assert resumed.phase == "committed"
    assert resumed.requested_version == "0.2.4"
    for root in (repo, second):
        assert (root / "spec-dock/spec-dock.version").read_text(encoding="utf-8") == "0.2.4\n"


def test_commit_origin_resume_ignores_version_alias(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, second, common_dir, epoch, digest, versioned_bundle = _group_fixture(tmp_path)
    commit_bundle = replace(versioned_bundle, source=replace(versioned_bundle.source, version=None))
    import spec_dock.installation.executor as executor

    with monkeypatch.context() as patch:
        patch.setattr(executor.os, "link", lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("marker stop")))
        with pytest.raises(OSError, match="marker stop"):
            update_installation_group(
                repo_root=repo,
                common_dir=common_dir,
                worktree_id="main",
                engine_digest=digest,
                expected_epoch=epoch,
                bundle=commit_bundle,
                keep_maintenance=True,
            )
    (group_id,) = pending_installation_groups(common_dir)
    assert read_group_record(common_dir, group_id).requested_version is None
    resumed = resume_installation_group(
        repo_root=repo,
        common_dir=common_dir,
        worktree_id="main",
        engine_digest=digest,
        operation_id=group_id,
        bundle=versioned_bundle,
    )
    assert resumed.phase == "committed"
    for root in (repo, second):
        assert (root / "spec-dock/spec-dock.version").read_text(encoding="utf-8") == commit_bundle.source.commit + "\n"


def test_group_upgrades_planned_child_origin_from_fixed_parent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, second, common_dir, epoch, digest, versioned_bundle = _group_fixture(tmp_path)
    commit_bundle = replace(versioned_bundle, source=replace(versioned_bundle.source, version=None))
    import spec_dock.installation.executor as executor

    with monkeypatch.context() as patch:
        patch.setattr(executor.os, "link", lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("marker stop")))
        with pytest.raises(OSError, match="marker stop"):
            update_installation_group(
                repo_root=repo,
                common_dir=common_dir,
                worktree_id="main",
                engine_digest=digest,
                expected_epoch=epoch,
                bundle=commit_bundle,
                keep_maintenance=True,
            )
    (group_id,) = pending_installation_groups(common_dir)
    first = read_group_record(common_dir, group_id).targets[0]
    assert first.child_operation_id is not None
    child_root = common_dir / "spec-dock/control/installations" / group_id / "targets" / first.worktree_id
    journal_file = child_root / "installations" / first.child_operation_id / "record.json"
    payload = json.loads(journal_file.read_text(encoding="utf-8"))
    payload.pop("version_tracked")
    journal_file.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    resumed = resume_installation_group(
        repo_root=repo,
        common_dir=common_dir,
        worktree_id="main",
        engine_digest=digest,
        operation_id=group_id,
        bundle=versioned_bundle,
    )
    assert resumed.phase == "committed"
    for root in (repo, second):
        assert (root / "spec-dock/spec-dock.version").read_text(encoding="utf-8") == commit_bundle.source.commit + "\n"


def test_group_rollback_rechecks_each_child_after_batch_preflight(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, second, common_dir, epoch, digest, bundle = _group_fixture(tmp_path)
    group = update_installation_group(
        repo_root=repo,
        common_dir=common_dir,
        worktree_id="main",
        engine_digest=digest,
        expected_epoch=epoch,
        bundle=bundle,
        keep_maintenance=True,
    )
    import spec_dock.installation.executor as executor

    real_preflight = executor.preflight_rollback_installation
    changed = False

    def change_after_child_preflight(journal_root: Path, operation_id: str, *, allow_committed: bool = False):
        nonlocal changed
        record = real_preflight(journal_root, operation_id, allow_committed=allow_committed)
        if not changed:
            changed = True
            version = Path(record.target) / "spec-dock/spec-dock.version"
            inode = version.stat().st_ino
            version.write_text("9.2.4\n", encoding="utf-8")
            assert version.stat().st_ino == inode
        return record

    monkeypatch.setattr(executor, "preflight_rollback_installation", change_after_child_preflight)
    with pytest.raises(ValueError, match="later changes"):
        rollback_installation_group(
            repo_root=repo,
            common_dir=common_dir,
            worktree_id="main",
            engine_digest=digest,
            operation_id=group.operation_id,
        )
    assert changed
    assert read_group_record(common_dir, group.operation_id).phase == "recovery-required"
    assert pending_installation_groups(common_dir) == (group.operation_id,)
    assert (second / "spec-dock/spec-dock.version").read_text(encoding="utf-8") == "9.2.4\n"


@pytest.mark.parametrize(
    ("initial_kind", "resume_kind", "expected_version"),
    [
        ("commit", "commit", "sha"),
        ("commit", "version", "sha"),
        ("version", "commit", "0.2.4"),
        ("version", "version", "0.2.4"),
    ],
)
def test_public_update_resume_preserves_source_origin(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    initial_kind: str,
    resume_kind: str,
    expected_version: str,
) -> None:
    repo, second, common_dir, _epoch, digest, versioned_bundle = _group_fixture(tmp_path)
    import spec_dock.installation.executor as executor
    import spec_dock_runtime.commands.installation_vnext as command_module

    def resolve_source(**kwargs: object):
        version = "0.2.4" if kwargs.get("version") else None
        return replace(versioned_bundle.source, version=version)

    monkeypatch.setattr(command_module, "resolve_fixed_source", resolve_source)
    monkeypatch.setattr(command_module, "download_pinned_archive", lambda *_args, **_kwargs: b"archive")
    monkeypatch.setattr(
        command_module,
        "verify_pinned_archive",
        lambda source, *_args: replace(versioned_bundle, source=source),
    )
    monkeypatch.setattr(command_module, "assert_candidate_assets_match_engine", lambda *_args: None)
    with monkeypatch.context() as patch:
        patch.setattr(executor.os, "link", lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("marker stop")))
        stopped = run_vnext(
            [
                "installation",
                "update",
                f"--{initial_kind}",
                versioned_bundle.source.commit if initial_kind == "commit" else "0.2.4",
                "--maintenance",
                "--yes",
                "--json",
            ],
            invocation_cwd=repo,
            engine_digest=digest,
            engine_version="0.2.4",
        )
    assert stopped.exit_code != 0
    (group_id,) = pending_installation_groups(common_dir)
    resumed = run_vnext(
        [
            "installation",
            "update",
            f"--{resume_kind}",
            versioned_bundle.source.commit if resume_kind == "commit" else "0.2.4",
            "--resume",
            group_id,
            "--yes",
            "--json",
        ],
        invocation_cwd=repo,
        engine_digest=digest,
        engine_version="0.2.4",
    )
    assert resumed.exit_code == 0, resumed.stdout
    label = versioned_bundle.source.commit if expected_version == "sha" else expected_version
    for root in (repo, second):
        assert (root / "spec-dock/spec-dock.version").read_text(encoding="utf-8") == label + "\n"


def test_group_commit_refuses_replaced_marker_after_child_apply(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _second, common_dir, epoch, digest, bundle = _group_fixture(tmp_path)
    import spec_dock_runtime.application.installation_update_vnext as update_module

    real_apply = update_module.apply_installation
    changed = False

    def replace_after_apply(*args: object, **kwargs: object):
        nonlocal changed
        result = real_apply(*args, **kwargs)
        if not changed:
            marker = repo / ".spec-dock-installations/.gitignore"
            replacement = marker.parent / "replacement"
            replacement.write_bytes(b"*\n")
            replacement.replace(marker)
            changed = True
        return result

    monkeypatch.setattr(update_module, "apply_installation", replace_after_apply)
    with pytest.raises(ValueError, match="changed identity"):
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
    assert read_group_record(common_dir, group_id).phase == "recovery-required"


def test_group_commit_refuses_same_content_published_swap(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, _second, common_dir, epoch, digest, bundle = _group_fixture(tmp_path)
    import spec_dock_runtime.application.installation_update_vnext as update_module

    real_apply = update_module.apply_installation
    changed = False

    def replace_after_apply(*args: object, **kwargs: object):
        nonlocal changed
        result = real_apply(*args, **kwargs)
        if not changed:
            installed = repo / "spec-dock/spec-dock.version"
            replacement = installed.with_name("same-content")
            replacement.write_bytes(installed.read_bytes())
            replacement.chmod(installed.stat().st_mode)
            replacement.replace(installed)
            changed = True
        return result

    monkeypatch.setattr(update_module, "apply_installation", replace_after_apply)
    with pytest.raises(ValueError, match="changed identity"):
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
    assert read_group_record(common_dir, group_id).phase == "recovery-required"


def test_finalization_refuses_same_content_published_swap(tmp_path: Path) -> None:
    repo, _second, common_dir, epoch, digest, bundle = _group_fixture(tmp_path)
    import spec_dock_runtime.application.installation_update_vnext as update_module

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
    installed = repo / "spec-dock/spec-dock.version"
    replacement = installed.with_name("same-content")
    replacement.write_bytes(installed.read_bytes())
    replacement.chmod(installed.stat().st_mode)
    replacement.replace(installed)
    group = update_module.inspect_installation_group(repo_root=repo, common_dir=common_dir)
    with pytest.raises(ValueError, match="changed identity"):
        update_module._verify_latest_installed_children(common_dir, group)


def test_group_update_rolls_back_a_completed_child(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
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
    assert (repo / "spec-dock/docs/source.txt").is_file()
    rolled_back = update_module.rollback_installation_group(
        repo_root=repo,
        common_dir=common_dir,
        worktree_id="main",
        engine_digest=digest,
        operation_id=group_id,
    )
    assert rolled_back.phase == "rolled-back"
    assert pending_installation_groups(common_dir) == ()
    assert load_control(common_dir).mode == "maintenance"
    assert not (repo / "spec-dock/docs/source.txt").exists()
    assert not (second / "spec-dock/docs/source.txt").exists()


def test_group_rollback_checks_all_children_before_restoring(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
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
    (second / "spec-dock/docs/later.txt").write_text("later\n", encoding="utf-8")
    with pytest.raises(ValueError, match="later changes"):
        update_module.rollback_installation_group(
            repo_root=repo,
            common_dir=common_dir,
            worktree_id="main",
            engine_digest=digest,
            operation_id=group_id,
        )
    assert pending_installation_groups(common_dir) == (group_id,)
    assert (repo / "spec-dock/docs/source.txt").is_file()


def test_installation_update_cli_updates_registered_group(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, second, _, _, digest, bundle = _group_fixture(tmp_path)
    import spec_dock_runtime.commands.installation_vnext as command_module

    monkeypatch.setattr(command_module, "resolve_fixed_source", lambda **_kwargs: bundle.source, raising=False)
    monkeypatch.setattr(command_module, "download_pinned_archive", lambda *_args, **_kwargs: b"archive", raising=False)
    monkeypatch.setattr(command_module, "verify_pinned_archive", lambda *_args, **_kwargs: bundle, raising=False)
    monkeypatch.setattr(command_module, "assert_candidate_assets_match_engine", lambda *_args: None)
    result = run_vnext(
        [
            "installation",
            "update",
            "--target",
            str(repo),
            "--commit",
            bundle.source.commit,
            "--maintenance",
            "--yes",
            "--json",
        ],
        invocation_cwd=repo,
        engine_digest=digest,
        engine_version="0.2.4",
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["data"]["phase"] == "committed"
    assert {target["root"] for target in payload["data"]["targets"]} == {str(repo), str(second)}


def test_installation_update_cli_rolls_back_without_source(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, _, common_dir, epoch, digest, bundle = _group_fixture(tmp_path)
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
    output = run_vnext(
        ["installation", "update", "--rollback", group_id, "--offline", "--yes", "--json"],
        invocation_cwd=repo,
        engine_digest=digest,
        engine_version="0.2.4",
    )
    assert output.exit_code == 0
    assert json.loads(output.stdout)["data"]["phase"] == "rolled-back"


def test_installation_update_dry_run_preserves_targets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, second, common_dir, epoch, digest, bundle = _group_fixture(tmp_path)
    import spec_dock_runtime.commands.installation_vnext as command_module

    monkeypatch.setattr(command_module, "resolve_fixed_source", lambda **_kwargs: bundle.source)
    monkeypatch.setattr(command_module, "download_pinned_archive", lambda *_args, **_kwargs: b"archive")
    monkeypatch.setattr(command_module, "verify_pinned_archive", lambda *_args, **_kwargs: bundle)
    monkeypatch.setattr(command_module, "assert_candidate_assets_match_engine", lambda *_args: None)
    output = run_vnext(
        ["installation", "update", "--commit", bundle.source.commit, "--dry-run", "--json"],
        invocation_cwd=repo,
        engine_digest=digest,
        engine_version="0.2.4",
    )
    assert output.exit_code == 0
    assert json.loads(output.stdout)["status"] == "planned"
    assert load_control(common_dir).epoch == epoch
    assert pending_installation_groups(common_dir) == ()
    assert not (repo / "spec-dock/docs/source.txt").exists()
    assert not (second / "spec-dock/docs/source.txt").exists()


def test_group_uninstall_preserves_spec_data_and_can_restore_tooling(tmp_path: Path) -> None:
    repo, second, common_dir, epoch, digest, _bundle_value = _group_fixture(tmp_path)
    import spec_dock_runtime.application.installation_update_vnext as update_module

    data = repo / "spec-dock/initiatives/kept.md"
    data.parent.mkdir(parents=True, exist_ok=True)
    data.write_text("consumer data\n", encoding="utf-8")
    before_version = (repo / "spec-dock/spec-dock.version").read_bytes()
    completed = update_module.uninstall_installation_group(
        repo_root=repo,
        common_dir=common_dir,
        worktree_id="main",
        engine_digest=digest,
        expected_epoch=epoch,
    )
    assert completed.action == "uninstall" and completed.phase == "committed"
    assert load_control(common_dir).mode == "maintenance"
    for root in (repo, second):
        assert not (root / "spec-dock/docs").exists()
        assert not (root / "spec-dock/spec-dock.version").exists()
    assert data.read_text(encoding="utf-8") == "consumer data\n"
    restored = update_module.rollback_installation_group(
        repo_root=repo,
        common_dir=common_dir,
        worktree_id="main",
        engine_digest=digest,
        operation_id=completed.operation_id,
        expected_action="uninstall",
    )
    assert restored.phase == "rolled-back"
    assert (repo / "spec-dock/spec-dock.version").read_bytes() == before_version
    assert (second / "spec-dock/docs").is_dir()
    assert data.read_text(encoding="utf-8") == "consumer data\n"


def test_group_uninstall_resumes_offline_after_one_worktree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, second, common_dir, epoch, digest, _bundle_value = _group_fixture(tmp_path)
    import spec_dock_runtime.application.installation_update_vnext as update_module

    real_apply = update_module.apply_installation
    attempts = 0

    def fail_second(*args: object, **kwargs: object):
        nonlocal attempts
        attempts += 1
        if attempts == 2:
            raise RuntimeError("injected uninstall stop")
        return real_apply(*args, **kwargs)

    monkeypatch.setattr(update_module, "apply_installation", fail_second)
    with pytest.raises(RuntimeError, match="uninstall stop"):
        update_module.uninstall_installation_group(
            repo_root=repo,
            common_dir=common_dir,
            worktree_id="main",
            engine_digest=digest,
            expected_epoch=epoch,
        )
    (group_id,) = pending_installation_groups(common_dir)
    monkeypatch.setattr(update_module, "apply_installation", real_apply)
    completed = update_module.resume_uninstall_installation_group(
        repo_root=repo,
        common_dir=common_dir,
        worktree_id="main",
        engine_digest=digest,
        operation_id=group_id,
    )
    assert completed.phase == "committed"
    assert pending_installation_groups(common_dir) == ()
    assert not (second / "spec-dock/docs").exists()


def test_installation_uninstall_cli_requires_yes_and_rolls_back_offline(tmp_path: Path) -> None:
    repo, second, common_dir, _epoch, digest, _bundle_value = _group_fixture(tmp_path)
    unconfirmed = run_vnext(
        ["installation", "uninstall", "--target", str(repo), "--json"],
        invocation_cwd=repo,
        engine_digest=digest,
        engine_version="0.2.4",
    )
    assert unconfirmed.exit_code == 3
    completed = run_vnext(
        ["installation", "uninstall", "--target", str(repo), "--yes", "--json"],
        invocation_cwd=repo,
        engine_digest=digest,
        engine_version="0.2.4",
    )
    assert completed.exit_code == 0
    operation_id = json.loads(completed.stdout)["operation_id"]
    assert not (second / "spec-dock/docs").exists()
    wrong_recovery = run_vnext(
        ["installation", "update", "--rollback", operation_id, "--offline", "--yes", "--json"],
        invocation_cwd=repo,
        engine_digest=digest,
        engine_version="0.2.4",
    )
    assert wrong_recovery.exit_code == 3
    assert not (second / "spec-dock/docs").exists()
    restored = run_vnext(
        ["installation", "uninstall", "--rollback", operation_id, "--offline", "--yes", "--json"],
        invocation_cwd=repo,
        engine_digest=digest,
        engine_version="0.2.4",
    )
    assert restored.exit_code == 0
    assert json.loads(restored.stdout)["data"]["phase"] == "rolled-back"
    assert (repo / "spec-dock/docs").is_dir()
    assert pending_installation_groups(common_dir) == ()


def test_committed_maintenance_update_can_be_rolled_back_before_resume(tmp_path: Path) -> None:
    repo, second, common_dir, epoch, digest, bundle = _group_fixture(tmp_path)
    completed = update_installation_group(
        repo_root=repo,
        common_dir=common_dir,
        worktree_id="main",
        engine_digest=digest,
        expected_epoch=epoch,
        bundle=bundle,
        keep_maintenance=True,
    )
    assert (repo / "spec-dock/docs/source.txt").is_file()
    import spec_dock_runtime.application.installation_update_vnext as update_module

    rolled_back = update_module.rollback_installation_group(
        repo_root=repo,
        common_dir=common_dir,
        worktree_id="main",
        engine_digest=digest,
        operation_id=completed.operation_id,
    )
    assert rolled_back.phase == "rolled-back"
    assert load_control(common_dir).mode == "maintenance"
    assert not (repo / "spec-dock/docs/source.txt").exists()
    assert not (second / "spec-dock/docs/source.txt").exists()


def test_committed_update_rollback_rejects_later_control_epoch(tmp_path: Path) -> None:
    repo, _, common_dir, epoch, digest, bundle = _group_fixture(tmp_path)
    completed = update_installation_group(
        repo_root=repo,
        common_dir=common_dir,
        worktree_id="main",
        engine_digest=digest,
        expected_epoch=epoch,
        bundle=bundle,
        keep_maintenance=True,
    )
    control = load_control(common_dir)
    assert control is not None
    store_control(common_dir, replace(control, epoch=control.epoch + 1), expected_epoch=control.epoch)
    import spec_dock_runtime.application.installation_update_vnext as update_module

    with pytest.raises(ValueError, match="changed after completion"):
        update_module.rollback_installation_group(
            repo_root=repo,
            common_dir=common_dir,
            worktree_id="main",
            engine_digest=digest,
            operation_id=completed.operation_id,
        )
    assert (repo / "spec-dock/docs/source.txt").is_file()
