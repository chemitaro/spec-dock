"""Switch only this schema-3 workspace declaration after real preservation."""

from __future__ import annotations

from dataclasses import replace
import os
from pathlib import Path
import sys
from typing import TYPE_CHECKING

from spec_dock.runtime.application.project_context import NEW_WRITER_PROTOCOL, OLD_WRITER_PROTOCOL, resolve_context
from spec_dock.runtime.application.scope_expectations import check_scope_expectations
from spec_dock.runtime.application.start_snapshot import capture_local_inputs, verify_local_inputs
from spec_dock.runtime.application.workspace_structure import inspect_structure
from spec_dock.runtime.application.worktree_observation import read_selection
from spec_dock.runtime.domain.writer_admission import require_workspace_write
from spec_dock.runtime.infra.direct_json import MetadataPublicationIncomplete, replace_existing_json
from spec_dock.runtime.infra.git_cli import worktree_list
from spec_dock.runtime.infra.git_process import GitProcessError, run_git
from spec_dock.runtime.infra.json_store import open_guarded_directory
from spec_dock.runtime.infra.legacy_reader import inspect_json_file, inspect_legacy_files
from spec_dock.runtime.infra.migration_backup import (
    BackupTree,
    MigrationBackupIncomplete,
    VerifiedBackup,
    create_verified_backup,
)
from spec_dock.runtime.infra.tree_backup import tree_digest
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult, RecoveryInstructions

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.project_context import ProjectContext


def migrate_workspace(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    if namespace.to_schema != "3" or namespace.to_writer_protocol != NEW_WRITER_PROTOCOL:
        raise ValueError("migration supports only schema 3 and specdock.worktree-writer/v1")
    path = context.root / "spec-dock/workspace.json"
    observed = inspect_json_file(path)
    if observed.classification != "observed" or observed.payload != context.workspace:
        raise ValueError("workspace declaration cannot be verified for migration")
    candidate = {**context.workspace, "writer_protocol": NEW_WRITER_PROTOCOL}
    candidate.pop("control_epoch", None)
    require_workspace_write(candidate)
    views, findings = inspect_structure(context.root)
    if findings:
        raise ValueError("workspace structure must be valid before migration; inspect workspace doctor")
    inputs = capture_local_inputs(context, views)
    check_scope_expectations(
        context,
        views,
        read_selection(context, views),
        target=None,
        expected_current=namespace.expect_current,
        expected_backend=namespace.expect_backend,
    )
    data: dict[str, object] = {
        "target": str(context.root),
        "before_protocol": context.workspace["writer_protocol"],
        "after_protocol": context.workspace["writer_protocol"],
        "changed_paths": (),
        "backup_path": None,
        "backup_verified": False,
        "restore_verified": False,
        "scope_count": len(views),
    }
    if context.workspace["writer_protocol"] == NEW_WRITER_PROTOCOL:
        context.require_writer()
        return OperationResult(namespace.command_path, "unchanged", FamilyData("migration", data), 0)
    if not namespace.dry_run and (
        namespace.backup_dir is None or not namespace.confirm_old_writers_stopped or not namespace.yes
    ):
        raise ValueError("migration apply requires --backup-dir ABS, --confirm-old-writers-stopped and --yes")
    legacy = inspect_legacy_files(context.root, context.common_dir)
    data["legacy_files"] = tuple(item.details() for item in legacy)
    active = next(item for item in legacy if item.record_kind == "active")
    data["legacy_active"] = {
        "path": str(active.path),
        "classification": active.classification,
        "policy": "preserved-not-imported",
    }
    if any(item.classification not in ("absent", "legacy_header_observed") for item in legacy):
        return OperationResult(
            namespace.command_path,
            "failed",
            FamilyData("migration", data),
            3,
            error=Diagnostic(
                "LEGACY_IMPACT_UNVERIFIED", "inspect and preserve unresolved legacy evidence before cutover", {}
            ),
        )
    inventory = worktree_list(context.root, timeout=namespace.timeout)
    if not inventory or any(item.inventory_error is not None for item in inventory):
        raise ValueError("native Git worktree inventory is incomplete")
    backup = _backup_destination(namespace.backup_dir, context, tuple(item.path for item in inventory))
    data["backup_path"] = str(backup) if backup is not None else None
    staging = context.root / "spec-dock/.agent/staging"
    if os.path.lexists(staging):
        descriptor = open_guarded_directory(staging)
        os.close(descriptor)
    if not run_git(
        context.root,
        "check-ignore",
        "--no-index",
        "--",
        "spec-dock/.agent/staging/.stage-probe",
        missing_ok=True,
        timeout=namespace.timeout,
    ):
        raise ValueError("metadata staging path must be ignored by Git")
    roots: tuple[tuple[Path, Path], ...] = ((context.root, Path("checkout")),)
    if not context.common_dir.is_relative_to(context.root):
        roots += ((context.common_dir, Path("common-git")),)
    sources = tuple(BackupTree(root, relative, tree_digest(root)) for root, relative in roots)
    exclusions: frozenset[str] = frozenset()
    verified: VerifiedBackup | None = None

    def verify_source(*, published: bool = False) -> None:
        if verified is not None:
            verified.verify()
        fresh = resolve_context(str(context.root), context.root, timeout=namespace.timeout)
        if (fresh.clone_identity, fresh.worktree_identity, fresh.head, fresh.branch) != (
            context.clone_identity,
            context.worktree_identity,
            context.head,
            context.branch,
        ):
            raise ValueError("Git worktree identity or state changed during migration")
        if worktree_list(context.root, timeout=namespace.timeout) != inventory:
            raise ValueError("native worktree inventory changed during migration")
        if not published:
            verify_local_inputs(fresh, inputs)
        for source in sources:
            ignored = exclusions if source.source == context.root else frozenset()
            if published and source.source == context.root:
                ignored |= frozenset({"spec-dock/workspace.json"})
                assert backup is not None
                expected = tree_digest(backup / source.relative, excluded_entries=ignored)
            else:
                expected = source.digest
            if tree_digest(source.source, excluded_entries=ignored) != expected:
                raise ValueError("preserved source changed during migration")

    def verify_stage(stage: Path) -> None:
        nonlocal exclusions
        verify_source()
        ignored = {stage.relative_to(context.root).as_posix()}
        for parent in (staging, staging.parent):
            if not os.path.lexists(parent):
                ignored.add(parent.relative_to(context.root).as_posix())
        exclusions = frozenset(ignored)

    verify_source()
    if namespace.dry_run:
        data.update({
            "can_apply": True,
            "blockers": (),
            "planned_paths": ("spec-dock/workspace.json",),
            "required_apply_arguments": ("--backup-dir ABS", "--confirm-old-writers-stopped", "--yes"),
        })
        return OperationResult(
            namespace.command_path,
            "planned",
            FamilyData("migration", data),
            0,
            effects=(
                Effect("backup", "planned", str(backup) if backup is not None else None),
                Effect("workspace.migrate", "planned", "spec-dock/workspace.json"),
            ),
        )
    assert backup is not None
    try:
        verified = create_verified_backup(backup, sources, verify=verify_source)
    except MigrationBackupIncomplete as error:
        data.update({"backup_verified": error.backup_verified, "restore_verified": error.restore_verified})
        return _incomplete(
            namespace,
            data,
            (
                Effect("backup", "succeeded" if error.backup_verified else "unknown", str(backup)),
                Effect("workspace.migrate", "not_attempted", "spec-dock/workspace.json"),
            ),
            error,
        )
    data.update({"backup_verified": True, "restore_verified": True})
    effects: tuple[Effect, ...] = (Effect("backup", "succeeded", str(backup)),)
    original = next(item for item in inputs if item.relative_path == "spec-dock/workspace.json")
    try:
        published = replace_existing_json(
            path,
            candidate,
            expected_bytes=original.payload,
            expected_identity=original.identity,
            staging_dir=staging,
            before_replace=verify_source,
            before_stage=verify_stage,
        )
        effects += (Effect("workspace.migrate", "succeeded", "spec-dock/workspace.json"),)
        data.update({"after_protocol": NEW_WRITER_PROTOCOL, "changed_paths": ("spec-dock/workspace.json",)})
        fresh = resolve_context(str(context.root), context.root, timeout=namespace.timeout)
        new_inputs = tuple(
            replace(item, payload=published.payload, identity=published.identity)
            if item.relative_path == original.relative_path
            else item
            for item in inputs
        )
        verify_local_inputs(fresh, new_inputs)
        verify_source(published=True)
    except MetadataPublicationIncomplete as error:
        confirmed = error.published is not None
        if confirmed:
            data.update({"after_protocol": NEW_WRITER_PROTOCOL, "changed_paths": ("spec-dock/workspace.json",)})
        return _incomplete(
            namespace,
            data,
            (
                *effects,
                Effect("workspace.migrate", "succeeded" if confirmed else "unknown", "spec-dock/workspace.json"),
            ),
            error,
        )
    except (OSError, ValueError, RuntimeError) as error:
        if len(effects) == 1:
            effects += (Effect("workspace.migrate", "not_attempted", "spec-dock/workspace.json"),)
        return _incomplete(namespace, data, effects, error)
    return OperationResult(namespace.command_path, "succeeded", FamilyData("migration", data), 0, effects=effects)


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
    namespace: argparse.Namespace, data: dict[str, object], effects: tuple[Effect, ...], error: BaseException
) -> OperationResult[object]:
    current = inspect_json_file(Path(str(data["target"])) / "spec-dock/workspace.json").payload
    protocol = current.get("writer_protocol") if current is not None else None
    data["after_protocol"] = (
        protocol
        if (
            current is not None
            and type(current.get("schema_version")) is int
            and current.get("schema_version") == 3
            and protocol in (NEW_WRITER_PROTOCOL, OLD_WRITER_PROTOCOL)
        )
        else None
    )
    native: GitProcessError | None = None
    cause: BaseException | None = error
    seen: set[int] = set()
    while cause is not None and id(cause) not in seen:
        if isinstance(cause, GitProcessError):
            native = cause
            break
        seen.add(id(cause))
        cause = cause.__cause__ or cause.__context__
    return OperationResult(
        namespace.command_path,
        "partial",
        FamilyData("migration", data),
        6,
        effects=effects,
        error=Diagnostic(
            "GIT_FAILED" if native is not None else "MIGRATION_INCOMPLETE",
            str(native)
            if native is not None
            else "preserve the backup and inspect current declaration and observed effects",
            native.details() if native is not None else {},
        ),
        recovery=RecoveryInstructions((
            "Inspect actual workspace bytes and the retained backup before a new explicit migration.",
            "Do not replay legacy records or automatically roll back; legacy active was not imported.",
        )),
    )
