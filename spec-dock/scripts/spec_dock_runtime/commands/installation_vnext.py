"""Thin read-only adapter for installation inventory."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from spec_dock.installation.source import (
    assert_disjoint_source_target,
    download_pinned_archive,
    resolve_fixed_source,
    verify_bundle_integrity,
    verify_pinned_archive,
)
from spec_dock_runtime.application.installation_update_vnext import (
    resume_installation_group,
    resume_uninstall_installation_group,
    rollback_installation_group,
    uninstall_installation_group,
    update_installation_group,
)
from spec_dock_runtime.application.installation_vnext import (
    InstallationView,
    inspect_installation_group,
    show_installation,
)
from spec_dock_runtime.presentation.envelope import Effect, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock.installation.group_journal import InstallationGroupRecord
    from spec_dock_runtime.commands.work_vnext import WorkContext


@dataclass(frozen=True)
class InstallationUpdatePlan:
    source_commit: str
    source_digest: str
    targets: tuple[str, ...]
    keep_maintenance: bool


@dataclass(frozen=True)
class InstallationUninstallPlan:
    targets: tuple[str, ...]
    preserve_consumer_data: bool


def run_installation_show(
    ns: argparse.Namespace, context: WorkContext, *, engine_version: str, invocation_cwd: Path
) -> OperationResult[InstallationView]:
    target = Path(ns.target).expanduser() if ns.target else None
    if target is not None and not target.is_absolute():
        target = invocation_cwd / target
    view = show_installation(
        repo_root=context.repo_root,
        common_dir=context.common_dir,
        engine_version=engine_version,
        engine_digest=context.engine_digest,
        target=target,
    )
    return OperationResult(command=ns.command_path, status="succeeded", data=view, exit_code=0)


def run_installation_update(
    ns: argparse.Namespace, context: WorkContext, *, invocation_cwd: Path
) -> OperationResult[InstallationGroupRecord | InstallationUpdatePlan]:
    target = Path(ns.target).expanduser() if ns.target else context.repo_root
    if not target.is_absolute():
        target = invocation_cwd / target
    show_installation(
        repo_root=context.repo_root,
        common_dir=context.common_dir,
        engine_version="bound",
        engine_digest=context.engine_digest,
        target=target,
    )
    if ns.rollback:
        if ns.dry_run or ns.version or ns.commit or ns.maintenance:
            raise ValueError("installation rollback accepts no source, maintenance, or dry-run option")
        record = rollback_installation_group(
            repo_root=context.repo_root,
            common_dir=context.common_dir,
            worktree_id=context.worktree_id,
            engine_digest=context.engine_digest,
            operation_id=ns.rollback,
            lock_timeout=ns.lock_timeout,
        )
        return OperationResult(
            ns.command_path,
            "succeeded",
            record,
            0,
            effects=(Effect("installation-rollback", "succeeded", record.operation_id),),
        )
    if ns.offline:
        raise ValueError("installation update requires the fixed source archive; offline mode supports rollback only")
    source = resolve_fixed_source(version=ns.version, commit=ns.commit, timeout=ns.timeout)
    archive = download_pinned_archive(source, timeout=ns.timeout)
    with TemporaryDirectory(prefix="specdock-install-") as directory:
        bundle = verify_pinned_archive(source, archive, Path(directory) / "bundle")
        if ns.dry_run:
            if ns.resume:
                raise ValueError("installation resume cannot be a dry run")
            group = inspect_installation_group(repo_root=context.repo_root, common_dir=context.common_dir)
            verify_bundle_integrity(bundle)
            for item in group.worktrees:
                assert_disjoint_source_target(bundle.root, Path(item.root))
            plan = InstallationUpdatePlan(
                source.commit,
                bundle.digest,
                tuple(item.root for item in group.worktrees),
                bool(ns.maintenance),
            )
            return OperationResult(
                ns.command_path, "planned", plan, 0, effects=(Effect("installation", "planned", None),)
            )
        if ns.resume:
            record = resume_installation_group(
                repo_root=context.repo_root,
                common_dir=context.common_dir,
                worktree_id=context.worktree_id,
                engine_digest=context.engine_digest,
                operation_id=ns.resume,
                bundle=bundle,
                lock_timeout=ns.lock_timeout,
            )
        else:
            record = update_installation_group(
                repo_root=context.repo_root,
                common_dir=context.common_dir,
                worktree_id=context.worktree_id,
                engine_digest=context.engine_digest,
                expected_epoch=context.expected_epoch,
                bundle=bundle,
                keep_maintenance=bool(ns.maintenance),
                lock_timeout=ns.lock_timeout,
            )
    return OperationResult(
        ns.command_path,
        "succeeded",
        record,
        0,
        effects=(Effect("installation", "succeeded", record.operation_id),),
    )


def run_installation_uninstall(
    ns: argparse.Namespace, context: WorkContext, *, invocation_cwd: Path
) -> OperationResult[InstallationGroupRecord | InstallationUninstallPlan]:
    target = Path(ns.target).expanduser() if ns.target else context.repo_root
    if not target.is_absolute():
        target = invocation_cwd / target
    show_installation(
        repo_root=context.repo_root,
        common_dir=context.common_dir,
        engine_version="bound",
        engine_digest=context.engine_digest,
        target=target,
    )
    if ns.dry_run:
        if ns.resume or ns.rollback:
            raise ValueError("installation uninstall recovery cannot be previewed")
        group = inspect_installation_group(repo_root=context.repo_root, common_dir=context.common_dir)
        return OperationResult(
            ns.command_path,
            "planned",
            InstallationUninstallPlan(tuple(item.root for item in group.worktrees), True),
            0,
            effects=(Effect("installation-uninstall", "planned", None),),
        )
    if not ns.yes:
        raise ValueError("installation uninstall requires --yes")
    common = {
        "repo_root": context.repo_root,
        "common_dir": context.common_dir,
        "worktree_id": context.worktree_id,
        "engine_digest": context.engine_digest,
        "lock_timeout": ns.lock_timeout,
    }
    if ns.rollback:
        record = rollback_installation_group(operation_id=ns.rollback, expected_action="uninstall", **common)
    elif ns.resume:
        record = resume_uninstall_installation_group(operation_id=ns.resume, **common)
    else:
        record = uninstall_installation_group(expected_epoch=context.expected_epoch, **common)
    if record.action != "uninstall":
        raise ValueError("installation recovery operation is not an uninstall")
    return OperationResult(
        ns.command_path,
        "succeeded",
        record,
        0,
        operation_id=record.operation_id,
        effects=(Effect("installation-uninstall", "succeeded", record.operation_id),),
    )
