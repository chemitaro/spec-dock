"""Copy one Scope's opaque Workbench using on-demand native Git inventory."""

from __future__ import annotations

from functools import partial
import os
from pathlib import Path
import secrets
import sys
from typing import TYPE_CHECKING

from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.application.scope_query import load_scope_views, show_scope
from spec_dock.runtime.application.start_snapshot import capture_local_inputs, verify_local_inputs
from spec_dock.runtime.application.worktree_observation import read_selection, resolve_scope
from spec_dock.runtime.infra.file_publication import FilePublicationIncomplete, publish_file
from spec_dock.runtime.infra.git_cli import worktree_list
from spec_dock.runtime.infra.git_process import GitProcessError
from spec_dock.runtime.infra.json_store import open_guarded_directory
from spec_dock.runtime.infra.workbench_publication import publish_link
from spec_dock.runtime.infra.workbench_snapshot import read_entry, snapshot_workbench
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult, RecoveryInstructions

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.project_context import ProjectContext


def copy_workbench(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    context.require_writer()
    target_path = Path(namespace.to_worktree).expanduser()
    if not target_path.is_absolute() or ".." in target_path.parts:
        raise ValueError("--to-worktree must name an absolute worktree path")
    target = resolve_context(str(target_path), context.root, timeout=namespace.timeout)
    target.require_writer()
    if target.clone_identity != context.clone_identity or target.worktree_identity == context.worktree_identity:
        raise ValueError("destination must be another worktree in the same clone")
    inventory = worktree_list(context.root, timeout=namespace.timeout)
    if any(entry.inventory_error is not None for entry in inventory):
        raise ValueError("Git worktree inventory is invalid")
    matches = [entry for entry in inventory if entry.path.resolve() == target.root]
    if len(matches) != 1 or matches[0].bare:
        raise ValueError("destination is not a unique native Git working tree")
    views = load_scope_views(context.root / "spec-dock")
    selection = read_selection(context, views)
    scope = resolve_scope(context, views, namespace.scope, selection=selection)
    if namespace.expect_backend is not None and namespace.expect_backend != scope.backend.kind:
        raise ValueError("Scope backend does not match --expect-backend")
    if namespace.expect_current is not None:
        expected = resolve_scope(context, views, namespace.expect_current, selection=selection).id
        if selection.status != "selected" or selection.record is None or selection.record.scope_id != expected:
            raise ValueError("direct target does not match --expect-current")
    target_views = load_scope_views(target.root / "spec-dock")
    target_scope = show_scope(target_views, scope.id)
    if (scope.id, scope.kind, scope.parent_id, scope.backend.kind, scope.github_ref) != (
        target_scope.id,
        target_scope.kind,
        target_scope.parent_id,
        target_scope.backend.kind,
        target_scope.github_ref,
    ):
        raise ValueError("Scope identity or linkage differs between worktrees")
    source = scope.path / ".workbench"
    destination = target_scope.path / ".workbench"
    local_inputs = capture_local_inputs(context, views)
    target_inputs = capture_local_inputs(target, target_views)
    source_files = snapshot_workbench(source)
    if any(entry.link is not None and Path(entry.link).is_absolute() for entry in source_files.values()):
        raise ValueError("Workbench copy requires relative symlink targets")
    paths = source_files.keys()
    destination_files = snapshot_workbench(destination, missing_ok=True, paths=paths)
    if any(
        destination_files[name].kind != entry.kind and "directory" in (entry.kind, destination_files[name].kind)
        for name, entry in source_files.items()
        if name in destination_files
    ):
        raise ValueError("Workbench copy entry type collision")
    pending: list[str] = []
    for name, entry in source_files.items():
        current = destination_files.get(name)
        if name == ".":
            continue
        if current is None or current.kind != entry.kind:
            pending.append(name)
        elif entry.kind == "file" and entry.file is not None and current.file is not None:
            if current.file.payload != entry.file.payload or current.mode != entry.mode:
                pending.append(name)
        elif entry.kind == "symlink" and current.link != entry.link:
            pending.append(name)
    if namespace.on_conflict == "error" and any(name in destination_files for name in pending):
        raise ValueError("Workbench copy stopped at an existing file conflict")

    def verify_contexts() -> None:
        for original, inputs in ((context, local_inputs), (target, target_inputs)):
            current = resolve_context(str(original.root), original.root, timeout=namespace.timeout)
            current.require_writer()
            if (current.clone_identity, current.worktree_identity) != (
                original.clone_identity,
                original.worktree_identity,
            ):
                raise ValueError("Git worktree physical identity changed")
            verify_local_inputs(current, inputs)
        if snapshot_workbench(source) != source_files:
            raise ValueError("Workbench source changed")

    def verify_destination(ignore_name: str | None = None) -> None:
        verify_contexts()
        if snapshot_workbench(destination, missing_ok=True, paths=paths, ignore_path=ignore_name) != destination_files:
            raise ValueError("Workbench destination changed")

    def data(*, dry_run: bool = False) -> FamilyData:
        result: dict[str, object] = {
            "scope_id": scope.id,
            "source_path": str(source),
            "destination_path": str(destination),
            "copied_paths": tuple(copied),
            "remaining_paths": tuple(name for name in pending if name not in copied),
        }
        if dry_run:
            result.update(can_apply=True, blockers=())
        return FamilyData("workbench", result)

    copied: list[str] = []
    verify_destination()
    if namespace.dry_run:
        return OperationResult(
            namespace.command_path,
            "planned",
            data(dry_run=True),
            0,
            effects=(
                (Effect("workbench-directory", "planned", str(destination)),) if "." not in destination_files else ()
            )
            + tuple(
                Effect(
                    "workbench-directory" if source_files[name].kind == "directory" else "workbench-file",
                    "planned",
                    str(destination / name),
                )
                for name in pending
            ),
        )
    if namespace.on_conflict == "overwrite" and not namespace.yes:
        if namespace.json or namespace.non_interactive or not sys.stdin.isatty():
            return OperationResult(
                namespace.command_path,
                "failed",
                data(),
                3,
                error=Diagnostic("CONFIRMATION_REQUIRED", "overwrite requires --yes in non-interactive mode", {}),
            )
        sys.stderr.write(
            "Workbench overwrite planned:\n" + "".join(f"  {name}\n" for name in pending) + "Continue? [y/N] "
        )
        if sys.stdin.readline().strip().lower() not in {"y", "yes"}:
            return OperationResult(
                namespace.command_path,
                "failed",
                data(),
                3,
                error=Diagnostic("CONFIRMATION_DECLINED", "operation was not confirmed", {}),
            )
        verify_destination()
    if not pending and "." in destination_files:
        return OperationResult(namespace.command_path, "unchanged", data(), 0)
    if not namespace.json:
        sys.stderr.write("Workbench copy planned:\n" + "".join(f"  {name}\n" for name in pending))
    effects: list[Effect] = []
    failed_path: str | None = None
    directory_attempted = directory_created = False
    directory_target = destination
    try:
        if not destination.exists():
            parent = open_guarded_directory(destination.parent)
            try:
                directory_attempted = True
                try:
                    os.mkdir(destination.name, dir_fd=parent)
                except FileExistsError as error:
                    directory_attempted = False
                    raise ValueError("Workbench directory changed before creation") from error
                directory_created = True
                effects.append(Effect("workbench-directory", "succeeded", str(destination)))
                os.fsync(parent)
            finally:
                os.close(parent)
            destination_files["."] = read_entry(destination)
        for name in pending:
            verify_destination()
            failed_path = name
            snapshot = source_files[name]
            if snapshot.kind == "directory":
                parent = open_guarded_directory((destination / name).parent)
                try:
                    directory_attempted = True
                    directory_created = False
                    directory_target = destination / name
                    try:
                        os.mkdir((destination / name).name, dir_fd=parent)
                    except FileExistsError as error:
                        directory_attempted = False
                        raise ValueError("Workbench directory changed before creation") from error
                    directory_created = True
                    copied.append(name)
                    effects.append(Effect("workbench-directory", "succeeded", str(destination / name)))
                    failed_path = None
                    os.fsync(parent)
                finally:
                    os.close(parent)
            else:
                stage_name = f".copy-{secrets.token_hex(16)}.tmp"
                stage_path = ((destination / name).parent / stage_name).relative_to(destination).as_posix()
                previous = destination_files.get(name)
                if snapshot.kind == "symlink":
                    assert snapshot.link is not None
                    publish_link(
                        destination / name,
                        snapshot.link,
                        stage_name=stage_name,
                        verify=partial(verify_destination, stage_path),
                        expected=previous,
                    )
                else:
                    assert snapshot.file is not None
                    publish_file(
                        destination / name,
                        snapshot.file.payload,
                        stage_name=stage_name,
                        verify=partial(verify_destination, stage_path),
                        mode=snapshot.mode,
                        expected=(previous.file or previous) if previous is not None else None,
                        preserve_mode=True,
                    )
                copied.append(name)
                effects.append(Effect("workbench-file", "succeeded", str(destination / name)))
                failed_path = None
            destination_files[name] = read_entry(destination / name)
        verify_destination()
    except (OSError, ValueError, RuntimeError) as error:
        if isinstance(error, FilePublicationIncomplete) and failed_path is not None:
            effects.append(
                Effect("workbench-file", "succeeded" if error.confirmed else "unknown", str(destination / failed_path))
            )
            if error.confirmed:
                copied.append(failed_path)
        elif directory_attempted and not directory_created:
            effects.append(Effect("workbench-directory", "unknown", str(directory_target)))
        elif failed_path is not None:
            effects.append(
                Effect(
                    "workbench-directory" if source_files[failed_path].kind == "directory" else "workbench-file",
                    "failed",
                    str(destination / failed_path),
                )
            )
        effects.extend(
            Effect(
                "workbench-directory" if source_files[name].kind == "directory" else "workbench-file",
                "not_attempted",
                str(destination / name),
            )
            for name in pending
            if name not in copied and name != failed_path
        )
        has_effects = any(effect.status in ("succeeded", "unknown") for effect in effects)
        code, details = (
            ("GIT_FAILED", error.details()) if isinstance(error, GitProcessError) else ("WORKBENCH_COPY_FAILED", {})
        )
        return OperationResult(
            namespace.command_path,
            "partial" if has_effects else "failed",
            data(),
            6 if has_effects else (3 if isinstance(error, ValueError) else 5),
            effects=tuple(effects),
            error=Diagnostic(code, str(error), details),
            recovery=RecoveryInstructions((
                "Inspect the reported files before a new explicit copy; no automatic rollback.",
            ))
            if has_effects
            else None,
        )
    return OperationResult(namespace.command_path, "succeeded", data(), 0, effects=tuple(effects))
