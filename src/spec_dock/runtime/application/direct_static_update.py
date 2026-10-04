"""Preserve and replace only hash-verified static files in one worktree."""

from __future__ import annotations

import errno
import os
from pathlib import Path
import secrets
import sys
import tempfile
from typing import TYPE_CHECKING

from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.infra.file_publication import (
    FilePublicationIncomplete,
    FileRetirementIncomplete,
    FileSnapshot,
    create_missing_parents,
    publish_file,
    read_regular_file,
    retire_file,
    verify_existing_parent,
)
from spec_dock.runtime.infra.git_cli import worktree_list
from spec_dock.runtime.infra.git_process import GitProcessError
from spec_dock.runtime.infra.json_store import open_guarded_directory
from spec_dock.runtime.infra.migration_backup import (
    BackupTree,
    MigrationBackupIncomplete,
    VerifiedBackup,
    create_verified_backup,
)
from spec_dock.runtime.infra.static_assets import package_retired_assets
from spec_dock.runtime.infra.tree_backup import copy_bytes_at, tree_digest
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult, RecoveryInstructions

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.project_context import GitContext, ProjectContext
    from spec_dock.runtime.infra.static_assets import StaticAsset


def update_static_assets(
    namespace: argparse.Namespace, git: GitContext, assets: tuple[StaticAsset, ...], data: dict[str, object]
) -> OperationResult[object]:
    import hashlib

    context = resolve_context(str(git.root), git.root, timeout=namespace.timeout)
    context.require_writer()
    uninstall = namespace.command_path == "installation uninstall"
    inputs: dict[str, FileSnapshot | None] = {
        "spec-dock/workspace.json": read_regular_file(git.root / "spec-dock/workspace.json")
    }
    changed: list[StaticAsset] = []
    retired: list[str] = []
    for asset in assets:
        if asset.init_only or (uninstall and asset.path == "spec-dock/.gitignore"):
            continue
        path = git.root / asset.path
        verify_existing_parent(path)
        if not os.path.lexists(path):
            inputs[asset.path] = None
            if not uninstall:
                changed.append(asset)
            continue
        snapshot = _read_static_file(path)
        digest = hashlib.sha256(snapshot.payload).hexdigest()
        if digest != asset.sha256 and digest not in asset.known_old_sha256:
            raise ValueError(f"static resource is modified or unknown; merge manually: {asset.path}")
        inputs[asset.path] = snapshot
        if uninstall:
            retired.append(asset.path)
        elif digest != asset.sha256:
            changed.append(asset)
    kinds = {
        asset.path: "installation.create" if inputs[asset.path] is None else "installation.change" for asset in changed
    }
    for retired_asset in package_retired_assets():
        path = git.root / retired_asset.path
        verify_existing_parent(path)
        if os.path.lexists(path):
            snapshot = _read_static_file(path)
            if hashlib.sha256(snapshot.payload).hexdigest() not in retired_asset.known_old_sha256:
                raise ValueError(f"legacy static resource is modified or unknown; merge manually: {retired_asset.path}")
            inputs[retired_asset.path] = snapshot
            retired.append(retired_asset.path)
        else:
            inputs[retired_asset.path] = None
    inventory = worktree_list(git.root, timeout=namespace.timeout)
    if not inventory or any(item.inventory_error is not None for item in inventory):
        raise ValueError("native Git worktree inventory is incomplete")
    backup = _backup_destination(namespace.backup_dir, context, tuple(item.path for item in inventory))
    if not changed and not retired:
        return OperationResult(
            namespace.command_path,
            "planned" if namespace.dry_run else "unchanged",
            FamilyData("installation", {**data, "can_apply": True, "blockers": ()} if namespace.dry_run else data),
            0,
        )
    if not namespace.dry_run and (backup is None or not namespace.yes):
        raise ValueError("static installation changes require --backup-dir ABS and --yes")
    data["backup_path"] = str(backup) if backup is not None else None
    verified: VerifiedBackup | None = None

    def verify() -> None:
        fresh = resolve_context(str(git.root), git.root, timeout=namespace.timeout)
        fresh.require_writer()
        if (fresh.clone_identity, fresh.worktree_identity, fresh.head, fresh.branch) != (
            context.clone_identity,
            context.worktree_identity,
            context.head,
            context.branch,
        ):
            raise ValueError("installation worktree identity or Git state changed")
        if worktree_list(git.root, timeout=namespace.timeout) != inventory:
            raise ValueError("native Git worktree inventory changed during static update")
        if verified is not None:
            verified.verify()
        for name, snapshot in inputs.items():
            if os.path.lexists(git.root / name) if snapshot is None else read_regular_file(git.root / name) != snapshot:
                raise ValueError(f"static update input changed: {name}")

    verify()
    if namespace.dry_run:
        data.update({
            "can_apply": True,
            "blockers": (),
            "planned_paths": tuple(asset.path for asset in changed),
            "planned_retired_paths": tuple(retired),
            "required_apply_arguments": ("--backup-dir ABS", "--yes"),
        })
        return OperationResult(
            namespace.command_path,
            "planned",
            FamilyData("installation", data),
            0,
            effects=(
                Effect("backup", "planned", str(backup) if backup is not None else None),
                *(Effect(kinds[asset.path], "planned", asset.path) for asset in changed),
                *(Effect("installation.retire", "planned", name) for name in retired),
            ),
        )
    assert backup is not None
    try:
        with tempfile.TemporaryDirectory(prefix=".specdock-static-backup-") as temporary:
            captured = Path(temporary).resolve(strict=True)
            descriptor = open_guarded_directory(captured)
            try:
                for name in (*tuple(asset.path for asset in changed), *retired):
                    backup_snapshot = inputs[name]
                    if backup_snapshot is not None:
                        copy_bytes_at(descriptor, Path(name), backup_snapshot.payload, backup_snapshot.mode)
            finally:
                os.close(descriptor)
            verified = create_verified_backup(
                backup, (BackupTree(captured, Path("static"), tree_digest(captured)),), verify=verify
            )
    except MigrationBackupIncomplete as error:
        data.update({"backup_verified": error.backup_verified, "restore_verified": error.restore_verified})
        return _incomplete(
            namespace,
            data,
            [
                Effect("backup", "succeeded" if error.backup_verified else "unknown", str(backup)),
                *(Effect(kinds[asset.path], "not_attempted", asset.path) for asset in changed),
                *(Effect("installation.retire", "not_attempted", name) for name in retired),
            ],
            error,
        )
    except (OSError, ValueError, RuntimeError) as error:
        if verified is None:
            raise
        data.update({"backup_verified": True, "restore_verified": True})
        return _incomplete(
            namespace,
            data,
            [
                Effect("backup", "succeeded", str(backup)),
                *(Effect(kinds[asset.path], "not_attempted", asset.path) for asset in changed),
                *(Effect("installation.retire", "not_attempted", name) for name in retired),
            ],
            error,
        )
    data.update({"backup_verified": True, "restore_verified": True})
    effects: list[Effect] = [Effect("backup", "succeeded", str(backup))]
    applied: list[str] = []
    created: list[str] = []
    removed: list[str] = []
    attempted: str | None = None
    stage: Path | None = None

    def created_directory(path: Path) -> None:
        relative = path.relative_to(git.root).as_posix()
        created.append(relative)
        effects.append(Effect("installation.directory", "succeeded", relative))

    try:
        for asset in changed:
            attempted = asset.path
            path = git.root / asset.path
            create_missing_parents(git.root, path, on_created=created_directory)
            stage = path.parent / f".install-{secrets.token_hex(16)}.tmp"
            original = inputs[asset.path]
            publish_file(
                path,
                asset.payload,
                stage_name=stage.name,
                verify=verify,
                expected=original,
                mode=original.mode if original is not None else asset.mode,
                preserve_mode=True,
            )
            (created if original is None else applied).append(asset.path)
            effects.append(Effect(kinds[asset.path], "succeeded", asset.path))
            attempted = None
            stage = None
            inputs[asset.path] = read_regular_file(path)
        for name in retired:
            attempted = name
            removal_snapshot = inputs[name]
            assert removal_snapshot is not None
            retire_file(git.root / name, expected=removal_snapshot, verify=verify)
            removed.append(name)
            effects.append(Effect("installation.retire", "succeeded", name))
            attempted = None
            inputs[name] = None
        verify()
    except (OSError, ValueError, RuntimeError) as error:
        if isinstance(error, FilePublicationIncomplete) and attempted is not None:
            if error.confirmed:
                (created if kinds[attempted] == "installation.create" else applied).append(attempted)
            effects.append(Effect(kinds[attempted], "succeeded" if error.confirmed else "unknown", attempted))
        elif isinstance(error, FileRetirementIncomplete) and attempted is not None:
            if error.confirmed:
                removed.append(attempted)
            effects.append(Effect("installation.retire", "succeeded" if error.confirmed else "unknown", attempted))
        if stage is not None and os.path.lexists(stage):
            effects.append(Effect("installation.stage", "unknown", stage.relative_to(git.root).as_posix()))
        covered = {item.target for item in effects if item.kind in ("installation.change", "installation.create")}
        effects.extend(
            Effect(kinds[asset.path], "not_attempted", asset.path) for asset in changed if asset.path not in covered
        )
        covered_retirements = {item.target for item in effects if item.kind == "installation.retire"}
        effects.extend(
            Effect("installation.retire", "not_attempted", name) for name in retired if name not in covered_retirements
        )
        data["changed_paths"] = tuple(applied)
        data["created_paths"] = tuple(created)
        data["retired_paths"] = tuple(removed)
        return _incomplete(namespace, data, effects, error)
    data["changed_paths"] = tuple(applied)
    data["created_paths"] = tuple(created)
    data["retired_paths"] = tuple(removed)
    return OperationResult(
        namespace.command_path, "succeeded", FamilyData("installation", data), 0, effects=tuple(effects)
    )


def _read_static_file(path: Path) -> FileSnapshot:
    try:
        return read_regular_file(path)
    except OSError as error:
        if error.errno in (errno.ELOOP, errno.ENOTDIR):
            raise ValueError(f"static resource must be an unredirected regular file: {path}") from error
        raise


def _backup_destination(value: str | None, context: ProjectContext, roots: tuple[Path, ...]) -> Path | None:
    if value is None:
        return None
    backup = Path(value)
    if not backup.is_absolute() or ".." in backup.parts:
        raise ValueError("--backup-dir must be an absolute path without traversal")
    if os.path.lexists(backup):
        raise ValueError("backup destination already exists")
    if any(parent.is_symlink() for parent in (backup.parent, *backup.parent.parents)):
        raise ValueError("backup parent must not be redirected")
    descriptor = open_guarded_directory(backup.parent)
    os.close(descriptor)
    protected = (*roots, context.common_dir, Path(sys.prefix).resolve(), Path(__file__).resolve().parents[2])
    if any(backup.is_relative_to(root) or root.is_relative_to(backup) for root in protected):
        raise ValueError("backup must be outside all clone worktrees, Git metadata and installed package areas")
    return backup


def _incomplete(
    namespace: argparse.Namespace, data: dict[str, object], effects: list[Effect], error: BaseException
) -> OperationResult[object]:
    native = error
    while native.__cause__ is not None:
        native = native.__cause__
    details = native.details() if isinstance(native, GitProcessError) else {}
    return OperationResult(
        namespace.command_path,
        "partial",
        FamilyData("installation", data),
        6,
        effects=tuple(effects),
        error=Diagnostic(
            "INSTALLATION_INCOMPLETE", "static update stopped; inspect the preserved backup and actual paths", details
        ),
        recovery=RecoveryInstructions((
            "Inspect preserved, applied and remaining static paths before a new explicit operation; no journal or automatic rollback.",
        )),
    )
