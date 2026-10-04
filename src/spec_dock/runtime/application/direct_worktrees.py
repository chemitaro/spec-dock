"""Observe and operate native Git worktrees without a SpecDock registry."""

from __future__ import annotations

from dataclasses import replace
import os
from pathlib import Path
from typing import TYPE_CHECKING

from spec_dock.runtime.application.project_context import physical_identity, resolve_context
from spec_dock.runtime.application.scope_query import load_scope_views
from spec_dock.runtime.application.worktree_observation import read_selection, resolve_scope
from spec_dock.runtime.domain.git_ref import parse_commit_oid
from spec_dock.runtime.infra.git_cli import worktree_list
from spec_dock.runtime.infra.git_process import GitProcessError, run_git
from spec_dock.runtime.infra.identity import DirectoryIdentity
from spec_dock.runtime.infra.json_store import open_guarded_directory
from spec_dock.runtime.infra.work_target_store import WorkTargetStore
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import (
    Diagnostic,
    Effect,
    EffectStatus,
    OperationResult,
    RecoveryInstructions,
)

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.contracts import GitWorktreeRecord
    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.infra.work_target_store import StoredSelection


def check_current_expectation(
    namespace: argparse.Namespace, context: ProjectContext, *, stored: StoredSelection | None = None
) -> None:
    if namespace.expect_current is None:
        return
    views = load_scope_views(context.root / "spec-dock")
    selected = read_selection(context, views, stored=stored)
    expected = resolve_scope(context, views, namespace.expect_current, selection=selected).id
    if selected.status != "selected" or selected.record is None or selected.record.scope_id != expected:
        raise ValueError("direct target does not match --expect-current")


def list_native_worktrees(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    if namespace.expect_backend is not None:
        raise ValueError("--expect-backend requires one existing Scope target")
    check_current_expectation(namespace, context)
    inventory = worktree_list(context.root, timeout=namespace.timeout)
    if not inventory or any(entry.inventory_error is not None for entry in inventory):
        raise ValueError("native Git worktree inventory is incomplete")
    items = tuple(
        {
            "path": str(entry.path),
            "branch": entry.branch,
            "head": entry.head,
            "bare": entry.bare,
            "locked": entry.locked,
            "prunable": entry.prunable,
        }
        for entry in inventory
    )
    return OperationResult(namespace.command_path, "succeeded", FamilyData("worktree-list", {"items": items}), 0)


def show_native_worktree(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    if namespace.expect_backend is not None:
        raise ValueError("--expect-backend requires one existing Scope target")
    check_current_expectation(namespace, context)
    entry = resolve_native_target(namespace.worktree_ref, context, timeout=namespace.timeout)
    result: dict[str, object] = {
        "path": str(entry.path),
        "branch": entry.branch,
        "head": entry.head,
        "changed": False,
        "observed": {
            "bare": entry.bare,
            "locked": entry.locked,
            "prunable": entry.prunable,
            "detached": entry.detached,
        },
    }
    return OperationResult(namespace.command_path, "succeeded", FamilyData("worktree", result), 0)


def resolve_native_target(reference: str, context: ProjectContext, *, timeout: float) -> GitWorktreeRecord:
    requested = Path(reference).expanduser()
    if not requested.is_absolute() or ".." in requested.parts:
        raise ValueError("worktree reference requires an absolute native path")
    with DirectoryIdentity(requested) as held:
        inventory = worktree_list(context.root, timeout=timeout)
        if not inventory or any(entry.inventory_error is not None for entry in inventory):
            raise ValueError("native Git worktree inventory is incomplete")
        matches = [entry for entry in inventory if entry.path.resolve() == requested.resolve()]
        if len(matches) != 1:
            raise LookupError("path is not a unique native Git worktree in this clone")
        entry = matches[0]
        common_text = os.fsdecode(run_git(requested, "rev-parse", "--git-common-dir", timeout=timeout)).removesuffix(
            "\n"
        )
        common = Path(common_text)
        if not common.is_absolute():
            common = requested / common
        if physical_identity(common.resolve(strict=True)) != context.clone_identity:
            raise ValueError("worktree is attached to another physical clone")
        held.verify()
        return entry


def _removal_observation(context: ProjectContext, path: Path, *, timeout: float) -> dict[str, object]:
    inventory = worktree_list(context.root, timeout=timeout)
    if not inventory or any(row.inventory_error is not None for row in inventory):
        raise ValueError("native Git worktree inventory is incomplete")
    present = any(row.path.resolve() == path.resolve() for row in inventory)
    path_present = os.path.lexists(path)
    return {"removed": not present and not path_present, "inventory_present": present, "path_present": path_present}


def remove_native_worktree(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    context.require_writer()
    if namespace.expect_backend is not None:
        raise ValueError("--expect-backend requires one existing Scope target")
    with WorkTargetStore(context.root) as store:
        captured_selection = store.read()
    if captured_selection.status not in ("empty", "selected"):
        raise ValueError("source direct selection cannot be captured for a Git mutation")
    if captured_selection.record is not None and (
        captured_selection.record.clone_identity,
        captured_selection.record.worktree_identity,
    ) != (context.clone_identity, context.worktree_identity):
        raise ValueError("source direct selection physical identity mismatch")
    check_current_expectation(namespace, context, stored=captured_selection)
    if not namespace.yes and not namespace.dry_run:
        raise ValueError("worktree removal requires --yes")
    entry = resolve_native_target(namespace.worktree_ref, context, timeout=namespace.timeout)
    result: OperationResult[object] | None = None
    try:
        with DirectoryIdentity(entry.path) as held_target:
            result = _remove_captured_worktree(namespace, context, entry, captured_selection, held_target)
    except OSError as error:
        if result is None:
            raise
        partial = any(effect.status in ("succeeded", "unknown") for effect in result.effects)
        diagnostic = (
            Diagnostic(result.error.code, result.error.message, {**result.error.details, "cleanup_error": str(error)})
            if result.error is not None
            else Diagnostic("LOCAL_IO_FAILED", str(error), {})
        )
        return replace(
            result,
            status="partial" if partial else "failed",
            exit_code=6 if partial else 5,
            effects=tuple(
                replace(effect, status="not_attempted") if effect.status == "planned" else effect
                for effect in result.effects
            ),
            error=diagnostic,
            recovery=RecoveryInstructions((
                "Inspect native inventory and the target path before a new explicit operation.",
            ))
            if partial
            else None,
        )
    return result


def _remove_captured_worktree(
    namespace: argparse.Namespace,
    context: ProjectContext,
    entry: GitWorktreeRecord,
    captured_selection: StoredSelection,
    held_target: DirectoryIdentity,
) -> OperationResult[object]:
    if entry.locked and not namespace.unlock:
        raise ValueError("locked worktree removal requires --unlock")
    git_dir = Path(
        os.fsdecode(run_git(entry.path, "rev-parse", "--absolute-git-dir", timeout=namespace.timeout)).removesuffix(
            "\n"
        )
    )
    if entry.bare or physical_identity(git_dir.resolve(strict=True)) == context.clone_identity:
        raise ValueError("main or bare worktrees cannot be removed")
    if physical_identity(entry.path) == context.worktree_identity:
        raise ValueError("the current worktree cannot be removed")
    if run_git(entry.path, "status", "--porcelain=v1", "-z", "--untracked-files=all", timeout=namespace.timeout):
        raise ValueError("worktree removal requires no tracked or untracked changes")
    ignored = run_git(
        entry.path,
        "ls-files",
        "--others",
        "--ignored",
        "--exclude-standard",
        "--directory",
        "-z",
        timeout=namespace.timeout,
    )
    if ignored and not namespace.discard_ignored:
        raise ValueError("ignored worktree content requires --discard-ignored and explicit confirmation")
    captured_observed: dict[str, object] = {"removed": False}
    data: dict[str, object] = {
        "path": str(entry.path),
        "branch": entry.branch,
        "head": entry.head,
        "changed": False,
        "observed": captured_observed,
    }
    effects: list[Effect] = []

    def verify_source() -> None:
        fresh = resolve_context(str(context.root), context.root, timeout=namespace.timeout)
        fresh.require_writer()
        if (fresh.clone_identity, fresh.worktree_identity, fresh.branch, fresh.head, fresh.workspace) != (
            context.clone_identity,
            context.worktree_identity,
            context.branch,
            context.head,
            context.workspace,
        ):
            raise ValueError("source Git worktree context changed")
        with WorkTargetStore(context.root) as store:
            if store.read() != captured_selection:
                raise ValueError("source direct selection changed during the Git operation")

    def verify_target(*, locked: bool) -> None:
        nonlocal captured_observed
        held_target.verify()
        fresh_target = resolve_native_target(str(entry.path), context, timeout=namespace.timeout)
        if (
            fresh_target.branch,
            fresh_target.head,
            fresh_target.bare,
            fresh_target.detached,
            fresh_target.prunable,
        ) != (
            entry.branch,
            entry.head,
            entry.bare,
            entry.detached,
            entry.prunable,
        ) or fresh_target.locked != locked:
            captured_observed = {
                "removed": False,
                "branch": fresh_target.branch,
                "head": fresh_target.head,
                "locked": fresh_target.locked,
            }
            data["observed"] = captured_observed
            raise ValueError("native worktree branch, HEAD or flags changed before removal")
        if run_git(entry.path, "status", "--porcelain=v1", "-z", "--untracked-files=all", timeout=namespace.timeout):
            raise ValueError("worktree changed before removal")
        if not namespace.discard_ignored and run_git(
            entry.path,
            "ls-files",
            "--others",
            "--ignored",
            "--exclude-standard",
            "--directory",
            "-z",
            timeout=namespace.timeout,
        ):
            raise ValueError("ignored worktree content changed before removal")
        held_target.verify()

    verify_source()
    verify_target(locked=entry.locked)
    if namespace.dry_run:
        data.update(can_apply=True, blockers=())
        if entry.locked:
            effects.append(Effect("git.worktree.unlock", "planned", str(entry.path)))
        effects.append(Effect("git.worktree.remove", "planned", str(entry.path)))
        return OperationResult(
            namespace.command_path, "planned", FamilyData("worktree", data), 0, effects=tuple(effects)
        )
    attempted: str | None = None
    try:
        verify_source()
        verify_target(locked=entry.locked)
        if entry.locked:
            attempted = "git.worktree.unlock"
            run_git(context.root, "worktree", "unlock", "--", str(entry.path), mutation=True, timeout=namespace.timeout)
            unlocked = resolve_native_target(str(entry.path), context, timeout=namespace.timeout)
            if unlocked.locked:
                raise ValueError("native Git worktree remains locked after unlock")
            effects.append(Effect("git.worktree.unlock", "succeeded", str(entry.path)))
            attempted = None
            held_target.verify()
            verify_source()
        verify_target(locked=False)
        attempted = "git.worktree.remove"
        run_git(context.root, "worktree", "remove", "--", str(entry.path), mutation=True, timeout=namespace.timeout)
        removed_observation = _removal_observation(context, entry.path, timeout=namespace.timeout)
        captured_observed = removed_observation
        data["observed"] = removed_observation
        if removed_observation["removed"] is not True:
            raise ValueError("Git removal did not leave both the native inventory and target path absent")
        effects.append(Effect("git.worktree.remove", "succeeded", str(entry.path)))
        attempted = None
        verify_source()
    except (GitProcessError, OSError, ValueError, RuntimeError, LookupError) as error:
        status: EffectStatus = (
            "unknown"
            if not isinstance(error, GitProcessError) or error.returncode is not None or error.uncertain
            else "failed"
        )
        details = error.details() if isinstance(error, GitProcessError) else {}
        observed: dict[str, object] = {"removed": None} if attempted is not None else dict(captured_observed)
        if attempted == "git.worktree.unlock":
            try:
                held_target.verify()
                actual = resolve_native_target(str(entry.path), context, timeout=namespace.timeout)
                observed = {"removed": False, "locked": actual.locked, "branch": actual.branch, "head": actual.head}
                if not actual.locked and (
                    not isinstance(error, GitProcessError) or error.returncode is not None or error.uncertain
                ):
                    status = "succeeded"
            except (OSError, ValueError, RuntimeError, LookupError) as verification_error:
                details["verification_error"] = str(verification_error)
        if attempted == "git.worktree.remove":
            try:
                observed = _removal_observation(context, entry.path, timeout=namespace.timeout)
                if observed["removed"] is True:
                    status = "succeeded"
            except (OSError, ValueError, RuntimeError) as verification_error:
                details["verification_error"] = str(verification_error)
        if attempted is not None:
            effects.append(Effect(attempted, status, str(entry.path)))
        if entry.locked and not any(effect.kind == "git.worktree.unlock" for effect in effects):
            effects.append(Effect("git.worktree.unlock", "not_attempted", str(entry.path)))
        if not any(effect.kind == "git.worktree.remove" for effect in effects):
            effects.append(Effect("git.worktree.remove", "not_attempted", str(entry.path)))
        partial = any(effect.status in ("succeeded", "unknown") for effect in effects)
        data.update(changed=any(effect.status == "succeeded" for effect in effects), observed=observed)
        return OperationResult(
            namespace.command_path,
            "partial" if partial else "failed",
            FamilyData("worktree", data),
            6 if partial else (3 if isinstance(error, ValueError) else 5),
            effects=tuple(effects),
            error=Diagnostic(
                "GIT_FAILED" if isinstance(error, GitProcessError) else "WORKTREE_REMOVE_FAILED", str(error), details
            ),
            recovery=RecoveryInstructions((
                "Inspect native inventory and the target path before a new explicit operation.",
            ))
            if partial
            else None,
        )
    data.update(changed=True, observed={"removed": True})
    return OperationResult(namespace.command_path, "succeeded", FamilyData("worktree", data), 0, effects=tuple(effects))


def create_native_worktree(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    context.require_writer()
    if namespace.expect_backend is not None:
        raise ValueError("--expect-backend requires one existing Scope target")
    if run_git(context.root, "status", "--porcelain=v1", "-z", "--untracked-files=all", timeout=namespace.timeout):
        raise ValueError("worktree creation requires a clean source")
    name = namespace.name
    if not name or any(character not in "abcdefghijklmnopqrstuvwxyz0123456789-" for character in name):
        raise ValueError("worktree name requires lowercase letters, digits and hyphens")
    placement = namespace.root if namespace.root is not None else os.environ.get("SPEC_DOCK_WORKTREE_ROOT")
    if not placement:
        raise ValueError("worktree root requires --root or SPEC_DOCK_WORKTREE_ROOT")
    container = Path(placement).expanduser()
    if not container.is_absolute() or ".." in container.parts:
        raise ValueError("worktree root requires an absolute directory")
    path, branch = container / name, f"worktree/{name}"
    tip = parse_commit_oid(
        run_git(
            context.root,
            "rev-parse",
            "--verify",
            "--end-of-options",
            f"{namespace.base}^{{commit}}",
            timeout=namespace.timeout,
        )
    )
    if os.path.lexists(path) or run_git(
        context.root,
        "rev-parse",
        "--verify",
        "--quiet",
        f"refs/heads/{branch}",
        timeout=namespace.timeout,
        missing_ok=True,
    ):
        raise ValueError("worktree path or branch already exists")
    inventory = worktree_list(context.root, timeout=namespace.timeout)
    if not inventory or any(entry.inventory_error is not None for entry in inventory):
        raise ValueError("native Git worktree inventory is incomplete")
    if any(entry.path.resolve() == path.resolve() for entry in inventory):
        raise ValueError("worktree path is already present in native inventory")
    effects: list[Effect] = []
    data: dict[str, object] = {"path": str(path), "branch": branch, "head": tip, "changed": False, "observed": {}}
    with WorkTargetStore(context.root) as store:
        captured_selection = store.read()
    if captured_selection.status not in ("empty", "selected"):
        raise ValueError("source direct selection cannot be captured for a Git mutation")
    if captured_selection.record is not None and (
        captured_selection.record.clone_identity,
        captured_selection.record.worktree_identity,
    ) != (context.clone_identity, context.worktree_identity):
        raise ValueError("source direct selection physical identity mismatch")
    check_current_expectation(namespace, context, stored=captured_selection)

    def verify_source() -> None:
        fresh = resolve_context(str(context.root), context.root, timeout=namespace.timeout)
        fresh.require_writer()
        if (fresh.clone_identity, fresh.worktree_identity, fresh.branch, fresh.head, fresh.workspace) != (
            context.clone_identity,
            context.worktree_identity,
            context.branch,
            context.head,
            context.workspace,
        ):
            raise ValueError("source Git worktree context changed")
        with WorkTargetStore(context.root) as store:
            if store.read() != captured_selection:
                raise ValueError("source direct selection changed during the Git operation")
        if run_git(context.root, "status", "--porcelain=v1", "-z", "--untracked-files=all", timeout=namespace.timeout):
            raise ValueError("worktree creation source changed")

    missing_directories: list[Path] = []
    anchor = container
    while not os.path.lexists(anchor):
        missing_directories.append(anchor)
        anchor = anchor.parent
    missing_directories.reverse()
    with DirectoryIdentity(anchor) as held_anchor:
        anchor_identity = held_anchor.identity
    container_identity = anchor_identity if anchor == container else None
    verify_source()
    if namespace.dry_run:
        data.update(can_apply=True, blockers=())
        planned = tuple(Effect("worktree-directory", "planned", str(directory)) for directory in missing_directories)
        planned += (Effect("git.branch.create", "planned", branch), Effect("git.worktree.add", "planned", str(path)))
        return OperationResult(namespace.command_path, "planned", FamilyData("worktree", data), 0, effects=planned)
    attempted: str | None = None
    directory_attempted = directory_created = False
    directory_target = container
    try:
        for directory_target in missing_directories:
            verify_source()
            expected_parent = anchor_identity if directory_target.parent == anchor else container_identity
            if physical_identity(directory_target.parent) != expected_parent:
                raise ValueError("placement ancestor physical identity changed")
            parent = open_guarded_directory(directory_target.parent)
            try:
                directory_attempted = True
                directory_created = False
                try:
                    os.mkdir(directory_target.name, dir_fd=parent)
                except FileExistsError as error:
                    directory_attempted = False
                    raise ValueError("placement directory changed before creation") from error
                directory_created = True
                effects.append(Effect("worktree-directory", "succeeded", str(directory_target)))
                with DirectoryIdentity(directory_target) as created_directory:
                    container_identity = created_directory.identity
                    os.fsync(parent)
                    created_directory.verify()
            finally:
                os.close(parent)
        with DirectoryIdentity(container) as held:
            if held.identity != container_identity:
                raise ValueError("placement root physical identity changed")
            verify_source()
            attempted = "git.branch.create"
            run_git(context.root, "branch", "--", branch, tip, mutation=True, timeout=namespace.timeout)
            effects.append(Effect(attempted, "succeeded", branch))
            attempted = None
            held.verify()
            verify_source()
            actual_tip = parse_commit_oid(
                run_git(context.root, "rev-parse", "--verify", f"refs/heads/{branch}", timeout=namespace.timeout)
            )
            if actual_tip != tip:
                data["observed"] = {"branch": branch, "head": actual_tip}
                raise ValueError("created branch no longer matches the fixed base")
            if os.path.lexists(path):
                raise ValueError("worktree path changed before Git attachment")
            attempted = "git.worktree.add"
            run_git(context.root, "worktree", "add", "--", str(path), branch, mutation=True, timeout=namespace.timeout)
            effects.append(Effect(attempted, "succeeded", str(path)))
            attempted = None
            held.verify()
            verify_source()
            created = resolve_native_target(str(path), context, timeout=namespace.timeout)
            if created.branch != branch or created.head != tip:
                raise ValueError("created worktree does not match the fixed branch and base")
            data["observed"] = {
                "bare": created.bare,
                "locked": created.locked,
                "prunable": created.prunable,
                "detached": created.detached,
            }
            if run_git(path, "status", "--porcelain=v1", "-z", "--untracked-files=all", timeout=namespace.timeout):
                raise ValueError("created worktree is not clean")
    except (GitProcessError, OSError, ValueError, RuntimeError, LookupError) as error:
        details = error.details() if isinstance(error, GitProcessError) else {}
        if directory_attempted and not directory_created:
            effects.append(Effect("worktree-directory", "unknown", str(directory_target)))
        effects.extend(
            Effect("worktree-directory", "not_attempted", str(directory))
            for directory in missing_directories
            if not any(effect.target == str(directory) for effect in effects)
        )
        if attempted is not None:
            observed_status: EffectStatus = (
                "unknown" if isinstance(error, GitProcessError) and error.uncertain else "failed"
            )
            if isinstance(error, GitProcessError):
                try:
                    if attempted == "git.branch.create":
                        actual = run_git(
                            context.root,
                            "rev-parse",
                            "--verify",
                            "--quiet",
                            f"refs/heads/{branch}",
                            timeout=namespace.timeout,
                            missing_ok=True,
                        )
                        if actual:
                            observed_status = "succeeded" if parse_commit_oid(actual) == tip else "unknown"
                    elif os.path.lexists(path):
                        observed_status = "unknown"
                        created = resolve_native_target(str(path), context, timeout=namespace.timeout)
                        data["observed"] = {
                            "branch": created.branch,
                            "head": created.head,
                            "bare": created.bare,
                            "locked": created.locked,
                            "prunable": created.prunable,
                            "detached": created.detached,
                        }
                        if created.branch == branch and created.head == tip:
                            observed_status = "succeeded"
                    verify_source()
                except (OSError, ValueError, RuntimeError, LookupError) as verification_error:
                    details["verification_error"] = str(verification_error)
            effects.append(
                Effect(attempted, observed_status, branch if attempted == "git.branch.create" else str(path))
            )
        if not any(effect.kind == "git.branch.create" for effect in effects):
            effects.append(Effect("git.branch.create", "not_attempted", branch))
        if not any(effect.kind == "git.worktree.add" for effect in effects):
            effects.append(Effect("git.worktree.add", "not_attempted", str(path)))
        partial = any(effect.status in ("succeeded", "unknown") for effect in effects)
        data["changed"] = any(effect.status == "succeeded" for effect in effects)
        return OperationResult(
            namespace.command_path,
            "partial" if partial else "failed",
            FamilyData("worktree", data),
            6 if partial else (3 if isinstance(error, ValueError) else 5),
            effects=tuple(effects),
            error=Diagnostic(
                "GIT_FAILED" if isinstance(error, GitProcessError) else "WORKTREE_CREATE_FAILED", str(error), details
            ),
            recovery=RecoveryInstructions((
                "Inspect the branch, native inventory and target path before a new explicit operation.",
            ))
            if partial
            else None,
        )
    data["changed"] = True
    return OperationResult(namespace.command_path, "succeeded", FamilyData("worktree", data), 0, effects=tuple(effects))
