"""Delete one explicitly selected local subtree after a verified real backup."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
from typing import TYPE_CHECKING, Literal

from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.application.scope_query import load_scope_views
from spec_dock.runtime.application.start_snapshot import capture_local_inputs, verify_local_inputs
from spec_dock.runtime.application.worktree_observation import ancestors_for, read_selection, resolve_scope
from spec_dock.runtime.infra.direct_json import (
    MetadataPublicationIncomplete,
    _create_guarded_directory,
    replace_existing_json,
)
from spec_dock.runtime.infra.git_process import GitProcessError, run_git
from spec_dock.runtime.infra.json_store import open_guarded_directory, read_guarded_json_bytes
from spec_dock.runtime.infra.tree_backup import copy_bytes_at, copy_tree_at, tree_digest, verify_backup_root
from spec_dock.runtime.infra.tree_removal import TreeRemovalIncomplete, remove_tree
from spec_dock.runtime.infra.work_target_store import SelectionRemovalUnknown, WorkTargetStore
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult, RecoveryInstructions

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.project_context import ProjectContext


def delete_scope(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    context.require_writer()
    if (
        not namespace.yes
        and not namespace.dry_run
        and (namespace.json or namespace.non_interactive or not sys.stdin.isatty())
    ):
        return OperationResult(
            namespace.command_path,
            "failed",
            FamilyData(
                "deletion", {"removed_ids": (), "changed_paths": (), "remaining_paths": (), "backup_path": None}
            ),
            3,
            error=Diagnostic("CONFIRMATION_REQUIRED", "Scope deletion requires --yes", {}),
        )
    if namespace.backup_dir is None:
        raise ValueError("Scope deletion requires --backup-dir ABS")
    backup = Path(namespace.backup_dir)
    if not backup.is_absolute():
        raise ValueError("--backup-dir must be absolute")
    backup = Path(os.path.normpath(backup))
    if os.path.lexists(backup):
        raise ValueError("backup destination already exists")
    if any(path.is_symlink() for path in (backup.parent, *backup.parent.parents)):
        raise ValueError("backup parent must not be redirected")
    existing_parent = backup.parent
    while not os.path.lexists(existing_parent):
        existing_parent = existing_parent.parent
    if not existing_parent.is_dir():
        raise ValueError("backup parent must be a directory")
    parent_probe = open_guarded_directory(existing_parent)
    os.close(parent_probe)
    views = load_scope_views(context.root / "spec-dock")
    selection = read_selection(context, views)
    if selection.status in ("invalid", "unavailable"):
        raise ValueError(selection.reason or "direct selection cannot be safely observed")
    target = resolve_scope(context, views, namespace.target, selection=selection)
    if namespace.expect_backend is not None and target.backend.kind != namespace.expect_backend:
        raise ValueError("target backend does not match --expect-backend")
    if namespace.expect_current is not None:
        guarded = resolve_scope(context, views, namespace.expect_current, selection=selection).id
        if selection.status != "selected" or selection.record is None or selection.record.scope_id != guarded:
            raise ValueError("direct target does not match --expect-current")
    descendants = tuple(view for view in views if target.id in {parent.id for parent in ancestors_for(views, view)})
    if descendants and not namespace.recursive:
        raise ValueError("RECURSIVE_REQUIRED")
    deleted_ids = (target.id, *(view.id for view in descendants))
    clear = selection.record is not None and selection.record.scope_id in deleted_ids
    if clear and not namespace.clear_active:
        raise ValueError("CLEAR_ACTIVE_REQUIRED")
    if clear and (selection.status != "selected" or selection.handle is None):
        raise ValueError("direct selection cannot be safely cleared")
    relative = target.path.relative_to(context.root)
    if (
        backup.is_relative_to(target.path)
        or target.path.is_relative_to(backup)
        or backup.is_relative_to(context.common_dir)
    ):
        raise ValueError("backup must not overlap the deleted subtree or Git metadata")
    inputs = capture_local_inputs(context, views)
    surviving_edits = tuple(
        (view, item, json.loads(item.payload))
        for view in views
        if view.id not in deleted_ids
        for item in inputs
        if item.relative_path == (view.path / ".meta.json").relative_to(context.root).as_posix()
        if any(scope_id in deleted_ids for scope_id in json.loads(item.payload)["depends_on"])
    )
    if surviving_edits and not namespace.detach_dependencies:
        raise ValueError("DETACH_DEPENDENCIES_REQUIRED")
    record_path = (
        context.root / "spec-dock/.agent/work-target" / selection.handle.basename
        if clear and selection.handle
        else None
    )
    record_bytes: bytes | None = None
    if record_path is not None and selection.handle is not None:
        loaded_record = read_guarded_json_bytes(record_path)
        if (
            loaded_record is None
            or loaded_record[2] != selection.handle.file_identity
            or hashlib.sha256(loaded_record[1]).hexdigest() != selection.handle.content_hash
        ):
            raise ValueError("captured selection changed before backup")
        record_bytes = loaded_record[1]
    expected_entries = {
        path.relative_to(target.path).as_posix(): path.lstat() for path in (target.path, *target.path.rglob("*"))
    }
    expected = tree_digest(target.path)
    observed = target.path.stat()
    identity = observed.st_dev, observed.st_ino

    def verify_source(*, removed: bool = False) -> None:
        fresh = resolve_context(str(context.root), context.root, timeout=namespace.timeout)
        if fresh.clone_identity != context.clone_identity or fresh.worktree_identity != context.worktree_identity:
            raise ValueError("Git project physical identity changed")
        fresh.require_writer()
        remaining_inputs = (
            tuple(item for item in inputs if not Path(item.relative_path).is_relative_to(relative))
            if removed
            else inputs
        )
        verify_local_inputs(fresh, remaining_inputs)
        if removed:
            if os.path.lexists(target.path):
                raise ValueError("deleted subtree reappeared")
            return
        current = target.path.stat()
        if (current.st_dev, current.st_ino) != identity or tree_digest(target.path) != expected:
            raise ValueError("delete subtree changed")

    def verify_stage(path: Path) -> None:
        verify_source()
        if not run_git(
            context.root,
            "check-ignore",
            "--no-index",
            "--",
            path.relative_to(context.root).as_posix(),
            missing_ok=True,
            timeout=namespace.timeout,
        ):
            raise ValueError("metadata staging path must be ignored by Git")

    verify_source()
    if surviving_edits:
        verify_stage(context.root / "spec-dock/.agent/staging/.stage-probe")
    if namespace.dry_run:
        planned_paths = [item.relative_path for _view, item, _payload in surviving_edits]
        planned_effects = [Effect("backup", "planned", str(backup))]
        planned_effects.extend(Effect("metadata", "planned", view.id) for view, _item, _payload in surviving_edits)
        if clear and selection.handle is not None and record_path is not None:
            planned_paths.append(record_path.relative_to(context.root).as_posix())
            planned_effects.append(Effect("selection.clear", "planned", selection.handle.token))
        planned_paths.append(relative.as_posix())
        planned_effects.append(Effect("scope.delete", "planned", relative.as_posix()))
        return OperationResult(
            namespace.command_path,
            "planned",
            FamilyData(
                "deletion",
                {
                    "removed_ids": (),
                    "changed_paths": (),
                    "remaining_paths": tuple(planned_paths),
                    "backup_path": str(backup),
                    "can_apply": True,
                    "blockers": (),
                },
            ),
            0,
            effects=tuple(planned_effects),
        )
    if not namespace.yes:
        print(f"Target: {target.id}; subtree: {target.path}", file=sys.stderr)
        print(f"Backup: {backup}; removed Scopes: {', '.join(deleted_ids)}", file=sys.stderr)
        print(
            f"Incoming dependency edits: {', '.join(view.id for view, _item, _payload in surviving_edits) or 'none'}",
            file=sys.stderr,
        )
        print(f"Clear captured direct selection: {'yes' if clear else 'no'}", file=sys.stderr)
        print("Confirm [yes/no]: ", end="", file=sys.stderr, flush=True)
        if sys.stdin.readline().strip().lower() not in {"yes", "y"}:
            return OperationResult(
                namespace.command_path,
                "failed",
                FamilyData(
                    "deletion",
                    {
                        "removed_ids": (),
                        "changed_paths": (),
                        "remaining_paths": (relative.as_posix(),),
                        "backup_path": str(backup),
                    },
                ),
                3,
                error=Diagnostic("CONFIRMATION_DECLINED", "operation was not confirmed", {}),
            )
        verify_source()
    backup_claimed = False
    backup_attempted = False
    backup_verified = False
    try:
        parent_fd = _create_guarded_directory(backup.parent)
        try:
            backup_attempted = True
            try:
                os.mkdir(backup.name, mode=0o700, dir_fd=parent_fd)
            except FileExistsError as error:
                raise ValueError("backup destination appeared before creation") from error
            backup_claimed = True
        finally:
            os.close(parent_fd)
        backup_fd = open_guarded_directory(backup)
        destination = backup / relative
        try:
            copy_tree_at(backup_fd, relative, target.path)
            verify_backup_root(backup, backup_fd)
            for _view, item, _payload in surviving_edits:
                copy_bytes_at(
                    backup_fd,
                    Path(item.relative_path),
                    item.payload,
                    stat.S_IMODE((context.root / item.relative_path).stat().st_mode),
                )
                verify_backup_root(backup, backup_fd)
                if (backup / item.relative_path).read_bytes() != item.payload:
                    raise ValueError("survivor metadata backup differs")
            if record_path is not None and record_bytes is not None:
                copy_bytes_at(
                    backup_fd,
                    record_path.relative_to(context.root),
                    record_bytes,
                    stat.S_IMODE(record_path.stat().st_mode),
                )
                verify_backup_root(backup, backup_fd)
                if (backup / record_path.relative_to(context.root)).read_bytes() != record_bytes:
                    raise ValueError("direct selection backup differs")
        finally:
            os.close(backup_fd)
        if tree_digest(destination) != expected:
            raise ValueError("backup content verification failed")
        backup_verified = True
        verify_source()
    except (ValueError, OSError, RuntimeError) as error:
        if not backup_claimed and (not backup_attempted or isinstance(error, ValueError)):
            raise
        pending = [Effect("metadata", "not_attempted", view.id) for view, _item, _payload in surviving_edits]
        remaining = [item.relative_path for _view, item, _payload in surviving_edits]
        if clear and selection.handle is not None and record_path is not None:
            pending.append(Effect("selection.clear", "not_attempted", selection.handle.token))
            remaining.append(record_path.relative_to(context.root).as_posix())
        pending.append(Effect("scope.delete", "not_attempted", relative.as_posix()))
        remaining.append(relative.as_posix())
        return _incomplete(
            namespace.command_path,
            backup,
            [],
            remaining,
            [Effect("backup", "succeeded" if backup_verified else "unknown", str(backup)), *pending],
            error,
        )
    effects = [Effect("backup", "succeeded", str(backup))]
    changed_paths: list[str] = []

    for index, (view, item, payload) in enumerate(surviving_edits):
        updated = {
            **payload,
            "depends_on": [scope_id for scope_id in payload["depends_on"] if scope_id not in deleted_ids],
            "revision": view.revision + 1,
        }
        try:
            published = replace_existing_json(
                context.root / item.relative_path,
                updated,
                expected_bytes=item.payload,
                expected_identity=item.identity,
                staging_dir=context.root / "spec-dock/.agent/staging",
                before_replace=verify_source,
                before_stage=verify_stage,
            )
        except (ValueError, OSError, RuntimeError) as error:
            confirmed = isinstance(error, MetadataPublicationIncomplete) and error.published is not None
            uncertain = isinstance(error, MetadataPublicationIncomplete) and not confirmed
            if confirmed:
                changed_paths.append(item.relative_path)
            effects.append(
                Effect(
                    "metadata",
                    "succeeded"
                    if confirmed
                    else "unknown"
                    if uncertain
                    else "not_attempted"
                    if isinstance(error, ValueError)
                    else "failed",
                    view.id,
                )
            )
            remaining = [value.relative_path for _scope, value, _data in surviving_edits[index + int(confirmed) :]]
            effects.extend(
                Effect("metadata", "not_attempted", scope.id) for scope, _value, _data in surviving_edits[index + 1 :]
            )
            if clear and selection.handle is not None and record_path is not None:
                effects.append(Effect("selection.clear", "not_attempted", selection.handle.token))
                remaining.append(record_path.relative_to(context.root).as_posix())
            effects.append(Effect("scope.delete", "not_attempted", relative.as_posix()))
            remaining.append(relative.as_posix())
            return _incomplete(namespace.command_path, backup, changed_paths, remaining, effects, error)
        inputs = tuple(
            replace(value, payload=published.payload, identity=published.identity) if value == item else value
            for value in inputs
        )
        changed_paths.append(item.relative_path)
        effects.append(Effect("metadata", "succeeded", view.id))
    if clear and selection.handle is not None and record_path is not None:
        clear_attempted = False
        outcome: str | None = None
        try:
            verify_source()
            clear_attempted = True
            with WorkTargetStore(context.root) as store:
                outcome = store.remove_observed(selection.handle)
            if outcome == "conflict":
                raise ValueError("captured selection changed before clear")
        except (ValueError, OSError, RuntimeError) as error:
            confirmed_clear = outcome in ("removed", "already_absent")
            if outcome == "removed":
                changed_paths.append(record_path.relative_to(context.root).as_posix())
            clear_status: Literal["succeeded", "unchanged", "not_attempted", "unknown", "failed"] = (
                "succeeded"
                if outcome == "removed"
                else "unchanged"
                if outcome == "already_absent"
                else "not_attempted"
                if not clear_attempted
                else "unknown"
                if isinstance(error, SelectionRemovalUnknown)
                else "failed"
            )
            effects.extend((
                Effect("selection.clear", clear_status, selection.handle.token),
                Effect("scope.delete", "not_attempted", relative.as_posix()),
            ))
            remaining = [] if confirmed_clear else [record_path.relative_to(context.root).as_posix()]
            remaining.append(relative.as_posix())
            return _incomplete(namespace.command_path, backup, changed_paths, remaining, effects, error)
        effects.append(
            Effect("selection.clear", "succeeded" if outcome == "removed" else "unchanged", selection.handle.token)
        )
        if outcome == "removed":
            changed_paths.append(record_path.relative_to(context.root).as_posix())
    try:
        verify_source()
    except (ValueError, OSError, RuntimeError) as error:
        effects.append(Effect("scope.delete", "not_attempted", relative.as_posix()))
        return _incomplete(namespace.command_path, backup, changed_paths, [relative.as_posix()], effects, error)
    try:
        remove_tree(target.path, expected_entries=expected_entries)
    except TreeRemovalIncomplete as error:

        def path_for(value: str) -> str:
            return relative.as_posix() if value == "." else (relative / value).as_posix()

        changed_paths.extend(path_for(value) for value in error.applied)
        effects.extend(Effect("scope.delete", "succeeded", path_for(value)) for value in error.applied)
        effects.extend(
            Effect(
                "scope.delete",
                "unknown" if value == error.failed_path and error.attempted else "not_attempted",
                path_for(value),
            )
            for value in error.remaining
        )
        removed = tuple(
            view.id for view in (target, *descendants) if view.path.relative_to(target.path).as_posix() in error.applied
        )
        return _incomplete(
            namespace.command_path,
            backup,
            changed_paths,
            [path_for(value) for value in error.remaining],
            effects,
            error.cause,
            removed=removed,
        )
    changed_paths.append(relative.as_posix())
    effects.append(Effect("scope.delete", "succeeded", relative.as_posix()))
    try:
        verify_source(removed=True)
    except (ValueError, OSError, RuntimeError) as error:
        return _incomplete(namespace.command_path, backup, changed_paths, [], effects, error, removed=deleted_ids)
    return OperationResult(
        namespace.command_path,
        "succeeded",
        FamilyData(
            "deletion",
            {
                "removed_ids": deleted_ids,
                "changed_paths": tuple(changed_paths),
                "remaining_paths": (),
                "backup_path": str(backup),
            },
        ),
        0,
        effects=tuple(effects),
    )


def _incomplete(
    command: str,
    backup: Path,
    changed: list[str],
    remaining: list[str],
    effects: list[Effect],
    error: ValueError | OSError | RuntimeError,
    *,
    removed: tuple[str, ...] = (),
) -> OperationResult[object]:
    return OperationResult(
        command,
        "partial",
        FamilyData(
            "deletion",
            {
                "removed_ids": removed,
                "changed_paths": tuple(changed),
                "remaining_paths": tuple(remaining),
                "backup_path": str(backup),
            },
        ),
        6,
        effects=tuple(effects),
        error=Diagnostic(
            "GIT_FAILED" if isinstance(error, GitProcessError) else "SCOPE_DELETE_INCOMPLETE",
            str(error),
            error.details() if isinstance(error, GitProcessError) else {},
        ),
        recovery=RecoveryInstructions((
            "Inspect retained backups and current paths before a new explicit operation; no automatic rollback or resume.",
        )),
    )
