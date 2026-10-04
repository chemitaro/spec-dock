"""Observe or initialize only the explicit worktree's package-owned static files."""

from __future__ import annotations

import errno
import hashlib
import os
from pathlib import Path
import secrets
from typing import TYPE_CHECKING

from spec_dock import __version__
from spec_dock.runtime.application.project_context import resolve_context, resolve_git_context
from spec_dock.runtime.application.scope_expectations import check_scope_expectations
from spec_dock.runtime.application.scope_query import load_scope_views
from spec_dock.runtime.application.worktree_observation import read_selection
from spec_dock.runtime.infra.file_publication import (
    FilePublicationIncomplete,
    FileSnapshot,
    publish_file,
    read_regular_file,
)
from spec_dock.runtime.infra.identity import DirectoryIdentity
from spec_dock.runtime.infra.json_store import open_guarded_directory
from spec_dock.runtime.infra.legacy_reader import inspect_json_file
from spec_dock.runtime.infra.static_assets import package_static_assets
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult, RecoveryInstructions

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.project_context import GitContext


def installation_context(namespace: argparse.Namespace, cwd: Path) -> GitContext:
    value = namespace.path if namespace.command_path == "installation init" else namespace.target
    if value is not None:
        target = Path(value).expanduser()
        if not target.is_absolute() or ".." in target.parts:
            raise ValueError("installation target must be an absolute Git worktree root")
        if namespace.project is not None and Path(namespace.project).expanduser().resolve(
            strict=True
        ) != target.resolve(strict=True):
            raise ValueError("installation target conflicts with --project")
        return resolve_git_context(str(target), cwd, timeout=namespace.timeout)
    return resolve_git_context(namespace.project, cwd, timeout=namespace.timeout)


def install_static_assets(namespace: argparse.Namespace, context: GitContext) -> OperationResult[object]:
    if namespace.expect_backend is not None:
        raise ValueError("--expect-backend requires one existing Scope target")
    if namespace.expect_current is not None:
        project = resolve_context(str(context.root), context.root, timeout=namespace.timeout)
        views = load_scope_views(context.root / "spec-dock")
        check_scope_expectations(
            project,
            views,
            read_selection(project, views),
            target=None,
            expected_current=namespace.expect_current,
            expected_backend=None,
        )
    assets = package_static_assets()
    data: dict[str, object] = {
        "target": str(context.root),
        "package_version": __version__,
        "created_paths": (),
        "changed_paths": (),
        "retired_paths": (),
        "backup_path": None,
    }
    if namespace.command_path == "installation show":
        declaration = inspect_json_file(context.root / "spec-dock/workspace.json")
        header = (
            declaration.payload
            if declaration.classification == "observed" and isinstance(declaration.payload, dict)
            else {}
        )
        data["workspace"] = {
            "classification": declaration.classification,
            "schema_version": header.get("schema_version") if type(header.get("schema_version")) is int else None,
            "writer_protocol": header.get("writer_protocol")
            if header.get("writer_protocol") in ("specdock.writer/v1", "specdock.worktree-writer/v1")
            else None,
        }
        observed: list[dict[str, object]] = []
        for asset in assets:
            path = context.root / asset.path
            classification = "missing"
            if os.path.lexists(path):
                try:
                    digest = hashlib.sha256(read_regular_file(path).payload).hexdigest()
                except (OSError, ValueError):
                    classification = "unsafe"
                else:
                    classification = (
                        "current"
                        if digest == asset.sha256
                        else "known-old"
                        if digest in asset.known_old_sha256
                        else "unknown"
                    )
            observed.append({"path": asset.path, "classification": classification})
        data["assets"] = tuple(observed)
        return OperationResult(namespace.command_path, "succeeded", FamilyData("installation", data), 0)
    if namespace.command_path in ("installation update", "installation uninstall"):
        from spec_dock.runtime.application.direct_static_update import update_static_assets

        return update_static_assets(namespace, context, assets, data)
    if namespace.command_path != "installation init":
        raise ValueError("unsupported installation command")
    for asset in assets:
        _verify_parent_chain(context.root / asset.path)
        if os.path.lexists(context.root / asset.path):
            raise ValueError(f"installation destination already exists: {asset.path}")
    if not namespace.dry_run and not namespace.yes:
        raise ValueError("installation init apply requires --yes")
    if namespace.dry_run:
        data.update({"can_apply": True, "blockers": (), "planned_paths": tuple(asset.path for asset in assets)})
        return OperationResult(
            namespace.command_path,
            "planned",
            FamilyData("installation", data),
            0,
            effects=tuple(Effect("installation.create", "planned", asset.path) for asset in assets),
        )
    effects: list[Effect] = []
    published: dict[str, FileSnapshot] = {}
    created: list[str] = []
    attempted_path: str | None = None
    stage: Path | None = None

    def verify() -> None:
        with DirectoryIdentity(context.root) as root, DirectoryIdentity(context.common_dir) as common:
            if (root.identity, common.identity) != (context.worktree_identity, context.clone_identity):
                raise ValueError("installation worktree physical identity changed")
        for name, snapshot in published.items():
            if read_regular_file(context.root / name) != snapshot:
                raise ValueError(f"installed asset changed during publication: {name}")

    try:
        verify()
        for asset in assets:
            attempted_path = asset.path
            path = context.root / asset.path
            directory = context.root
            for part in path.parent.relative_to(context.root).parts:
                directory /= part
                _ensure_directory(directory, context.root, created, effects)
            stage = path.parent / f".install-{secrets.token_hex(16)}.tmp"
            publish_file(path, asset.payload, stage_name=stage.name, verify=verify, mode=asset.mode, preserve_mode=True)
            created.append(asset.path)
            effects.append(Effect("installation.create", "succeeded", asset.path))
            attempted_path = None
            stage = None
            published[asset.path] = read_regular_file(path)
        verify()
    except (OSError, ValueError, RuntimeError) as error:
        if isinstance(error, FilePublicationIncomplete) and attempted_path is not None:
            if error.confirmed:
                created.append(attempted_path)
            effects.append(Effect("installation.create", "succeeded" if error.confirmed else "unknown", attempted_path))
        if stage is not None and os.path.lexists(stage):
            effects.append(Effect("installation.stage", "unknown", stage.relative_to(context.root).as_posix()))
        covered = {item.target for item in effects if item.kind == "installation.create"}
        effects.extend(
            Effect("installation.create", "not_attempted", asset.path) for asset in assets if asset.path not in covered
        )
        data["created_paths"] = tuple(created)
        partial = any(item.status in ("succeeded", "unknown") for item in effects)
        return OperationResult(
            namespace.command_path,
            "partial" if partial else "failed",
            FamilyData("installation", data),
            6 if partial else 5,
            effects=tuple(effects),
            error=Diagnostic("INSTALLATION_INCOMPLETE", "static installation stopped; inspect observed paths", {}),
            recovery=RecoveryInstructions((
                "Inspect the static files and retained candidates before a new operation; no journal or automatic rollback.",
            )),
        )
    data["created_paths"] = tuple(created)
    return OperationResult(
        namespace.command_path, "succeeded", FamilyData("installation", data), 0, effects=tuple(effects)
    )


def _verify_parent_chain(path: Path) -> None:
    parent = path.parent
    while not os.path.lexists(parent):
        parent = parent.parent
    if any(item.is_symlink() for item in (parent, *parent.parents)):
        raise ValueError("static installation parent must not be a symbolic link")
    try:
        descriptor = open_guarded_directory(parent)
    except OSError as error:
        if error.errno in (errno.ENOTDIR, errno.ELOOP):
            raise ValueError("static installation parent must be a regular directory") from error
        raise
    os.close(descriptor)


def _ensure_directory(path: Path, root: Path, created: list[str], effects: list[Effect]) -> None:
    parent = open_guarded_directory(path.parent)
    try:
        try:
            os.mkdir(path.name, mode=0o755, dir_fd=parent)
        except FileExistsError:
            pass
        else:
            relative = path.relative_to(root).as_posix()
            created.append(relative)
            effects.append(Effect("installation.directory", "succeeded", relative))
            os.fsync(parent)
        opened = open_guarded_directory(path)
        os.close(opened)
    finally:
        os.close(parent)
