"""Canonical-mode `scope edit`, `scope move`, `scope close`, `scope reopen` and `scope delete` (iss-00432).

Titles, states and parents change on GitHub after a `decision` check and a reread of the target; directories
follow the GitHub parent in the catalog under the catalog lock. `scope delete` takes the Scope out of the
structure (kind labels, parent, incoming dependencies) and removes its directory after a verified backup; the
Issue itself is never closed or deleted.
"""

from __future__ import annotations

from dataclasses import replace
import hashlib
import os
from pathlib import Path, PurePosixPath
import stat
from typing import TYPE_CHECKING, cast

from spec_dock.runtime.application.canonical_scope_create import require_open_chain
from spec_dock.runtime.application.canonical_scopes import SCOPE_NESTING
from spec_dock.runtime.application.canonical_writes import (
    LOCAL_FAILURES,
    WriteFailed,
    check_expectations,
    confirmed_interactively,
    declined,
    needs_confirmation,
    open_write_session,
    planned,
)
from spec_dock.runtime.application.scope_completion_plan import plan_close, plan_reopen
from spec_dock.runtime.application.worktree_observation import ancestors_for
from spec_dock.runtime.domain.canonical_structure import (
    KIND_LABELS,
    PARENT_KINDS,
    SUB_ISSUE_FOREIGN_REPOSITORY,
    RemoveBlockedBy,
    SetParent,
    UpsertIssue,
)
from spec_dock.runtime.infra.canonical_scaffold import move_directory
from spec_dock.runtime.infra.direct_json import _create_guarded_directory
from spec_dock.runtime.infra.json_store import open_guarded_directory, read_guarded_json_bytes
from spec_dock.runtime.infra.tree_backup import copy_bytes_at, copy_tree_at, tree_digest, verify_backup_root
from spec_dock.runtime.infra.tree_removal import TreeRemovalIncomplete, remove_tree
from spec_dock.runtime.infra.work_target_store import SelectionRemovalUnknown, WorkTargetStore
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.canonical_writes import WriteSession
    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.scope_completion_plan import CompletionReason
    from spec_dock.runtime.application.scope_query import ScopeView
    from spec_dock.runtime.domain.lifecycle import ObservedState


def edit_scope(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    """Change only the GitHub title; catalog files keep their creation-time headings."""
    context.require_writer()
    title = namespace.title.strip()
    if not title:
        raise ValueError("Scope title must not be empty")
    session = open_write_session(context, namespace, link=False)
    selection = session.selection()
    target = session.resolve(namespace.target, selection)
    check_expectations(session, namespace, selection, target)
    number = session.node(target.id).number
    session.reread([number])
    if session.node(target.id).title == title:
        data = _scope_data(session, target.id, changed=False)
        if namespace.dry_run:
            return planned(namespace.command_path, _dry(data), (), session.warnings)
        return session.result("unchanged", data)
    if namespace.dry_run:
        return planned(namespace.command_path, _dry(_scope_data(session, target.id, changed=False)),
                       (("github.issue.title", target.id),), session.warnings)
    try:
        session.write(
            "github.issue.title",
            target.id,
            lambda: session.client.update_issue(number, title=title),
            lambda facts: [UpsertIssue(facts)],
        )
    except WriteFailed as error:
        return session.incomplete(
            _scope_data(session, target.id, changed=False),
            error,
            recovery=(f"Inspect the GitHub Issue {target.github_ref} before a new explicit edit.",),
        )
    return session.result("succeeded", _scope_data(session, target.id, changed=True))


def lifecycle_scope(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    """Close or reopen with today's rules; descendants and ancestors come from the GitHub parents."""
    context.require_writer()
    if needs_confirmation(namespace):
        raise ValueError("Scope lifecycle mutation requires --yes")
    close = namespace.command_path == "scope close"
    reason = cast("CompletionReason", getattr(namespace, "reason", "completed"))
    session = open_write_session(context, namespace, link=False)
    selection = session.selection()
    target = session.resolve(namespace.target, selection)
    check_expectations(session, namespace, selection, target)
    number = session.node(target.id).number
    session.reread([number])
    views = session.scopes.views
    states: dict[str, ObservedState] = {view.id: view.status.state for view in views}
    if close and reason == "completed":
        require_known_descendants(session, target.id)
    decision = plan_close(views, target.id, states, reason=reason) if close else plan_reopen(views, target.id, states)
    kind = "github.issue.close" if close else "github.issue.reopen"
    reference = session.scopes.view(target.id).github_ref

    def data(changed: bool) -> FamilyData:
        base = _scope_data(session, target.id, changed=changed)
        return FamilyData("scope", {**base.result, "descendants": decision.descendants})

    if namespace.dry_run:
        return planned(namespace.command_path, _dry(data(False)), ((kind, reference),), session.warnings)
    if not confirmed_interactively(
        namespace,
        (
            f"Target: {target.id} ({reference}); {decision.before} -> {decision.after}",
            f"Writes: {kind}; descendants: {', '.join(decision.descendants) or 'none'}",
        ),
    ):
        return declined(namespace.command_path, data(False))
    if not decision.changed:
        return session.result("unchanged", data(False), effects=(Effect(kind, "unchanged", reference),))
    try:
        session.write(
            kind,
            reference,
            lambda: session.client.update_issue(
                number,
                state="closed",
                state_reason="completed" if reason == "completed" else "not_planned",
            )
            if close
            else session.client.update_issue(number, state="open"),
            lambda facts: [UpsertIssue(facts)],
        )
    except WriteFailed as error:
        return session.incomplete(
            data(False),
            error,
            recovery=(
                f"Inspect the exact Scope {target.id} on GitHub before a new explicit operation; "
                "do not blindly repeat a mutation.",
            ),
        )
    return session.result("succeeded", data(True))


def move_scope(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    """Re-parent on GitHub (with --parent), then move the directory under the GitHub parent's directory."""
    context.require_writer()
    session = open_write_session(context, namespace, link=True)
    assert session.catalog is not None
    selection = session.selection()
    target = session.resolve(namespace.target, selection)
    check_expectations(session, namespace, selection, target)
    numbers = [session.node(target.id).number]
    new_parent: ScopeView | None = None
    if namespace.parent is not None:
        required = PARENT_KINDS[target.kind]
        if required is None:
            raise ValueError("initiative cannot have a parent")
        new_parent = session.resolve(namespace.parent, selection)
        if new_parent.kind != required:
            raise ValueError(f"{target.kind} parent must be a {required}")
        if new_parent.id == target.id or target.id in {view.id for view in ancestors_for(session.scopes.views, new_parent)}:
            raise ValueError("a Scope cannot move below itself or its descendants")
        numbers.append(session.node(new_parent.id).number)
    session.reread(numbers)
    for number in numbers:
        session.reread_parent(number)
    target = session.scopes.view(target.id)
    if new_parent is not None:
        if target.id in {view.id for view in ancestors_for(session.scopes.views, session.scopes.view(new_parent.id))}:
            raise ValueError("a Scope cannot move below itself or its descendants")
        require_open_chain(session, new_parent.id)
    source = session.scopes.directory(target.id)
    if source is None:
        raise FileNotFoundError(f"{target.id} has no directory in the catalog")
    parent_id = new_parent.id if new_parent is not None else target.parent_id
    if target.kind != "initiative" and parent_id is None:
        raise ValueError(f"{target.id} has no GitHub parent; give --parent")
    expected = source.relative.name if parent_id is None else None
    if parent_id is not None:
        parent_directory = session.scopes.directory(parent_id)
        if parent_directory is None:
            raise FileNotFoundError(f"{parent_id} has no directory in the catalog")
        expected = (parent_directory.relative / SCOPE_NESTING[target.kind] / source.relative.name).as_posix()
    assert expected is not None
    destination = PurePosixPath(expected)
    if destination != source.relative and os.path.lexists(session.catalog.catalog / destination):
        raise ValueError(f"{destination} already exists in the catalog")
    reparent = new_parent is not None and target.parent_id != new_parent.id
    steps: list[tuple[str, str | None]] = []
    if reparent:
        steps.append(("github.sub-issue.add", new_parent.id if new_parent else None))
    if destination != source.relative:
        steps.append(("catalog.move", destination.as_posix()))

    def data(changed: bool) -> FamilyData:
        base = _scope_data(session, target.id, changed=changed)
        return FamilyData(
            "scope", {**base.result, "moved_from": source.relative.as_posix(), "moved_to": destination.as_posix()}
        )

    if namespace.dry_run:
        return planned(namespace.command_path, _dry(data(False)), steps, session.warnings)
    if not steps:
        return session.result("unchanged", data(False))
    try:
        if reparent:
            assert new_parent is not None
            child = session.node(target.id)
            parent_number = session.node(new_parent.id).number
            session.write(
                "github.sub-issue.add",
                new_parent.id,
                lambda: session.client.add_sub_issue(
                    parent_number, child=child.number, child_id=child.database_id, replace_parent=True
                ),
                lambda _: [SetParent(child.number, parent_number)],
            )
        if destination != source.relative:
            with session.catalog_changes() as changes:
                move_directory(session.catalog.catalog / source.relative, session.catalog.catalog / destination)
                changes.add(destination)
                changes.delete(source.relative)
            session.effects.append(Effect("catalog.move", "succeeded", destination.as_posix()))
            session.reload_catalog()
            _follow_moved_selections(session, target.id, namespace.timeout)
    except (WriteFailed, *LOCAL_FAILURES) as error:
        remaining = [step for step in steps if step[0] not in {effect.kind for effect in session.effects}]
        return session.incomplete(
            data(False),
            error,
            pending=remaining,
            recovery=(f"Run spec-dock scope move {target.id}; it moves the directory to the GitHub parent.",),
            code="SCOPE_MOVE_INCOMPLETE",
        )
    return session.result("succeeded", data(True))


def delete_scope(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    """Back up, then detach on GitHub (dependencies, parent, kind labels), then remove the directory."""
    context.require_writer()
    empty = FamilyData("deletion", {"removed_ids": (), "changed_paths": (), "remaining_paths": (), "backup_path": None})
    if needs_confirmation(namespace):
        return OperationResult(
            namespace.command_path,
            "failed",
            empty,
            3,
            error=Diagnostic("CONFIRMATION_REQUIRED", "Scope deletion requires --yes", {}),
        )
    backup = _backup_destination(namespace.backup_dir)
    # Every relation decides this command (descendants, incoming dependencies): refetch the whole structure.
    session = open_write_session(context, namespace, link=True, refresh=True)
    linked = session.catalog
    assert linked is not None
    selection = session.selection()
    if selection.status in ("invalid", "unavailable"):
        raise ValueError(selection.reason or "direct selection cannot be safely observed")
    target = session.resolve(namespace.target, selection)
    check_expectations(session, namespace, selection, target)
    views = session.scopes.views
    descendants = tuple(view for view in views if target.id in {parent.id for parent in ancestors_for(views, view)})
    if descendants and not namespace.recursive:
        raise ValueError("RECURSIVE_REQUIRED")
    deleted_ids = (target.id, *(view.id for view in descendants))
    clear = selection.record is not None and selection.record.scope_id in deleted_ids
    if clear and not namespace.clear_active:
        raise ValueError("CLEAR_ACTIVE_REQUIRED")
    if clear and (selection.status != "selected" or selection.handle is None):
        raise ValueError("direct selection cannot be safely cleared")
    deleted_numbers = {session.node(scope_id).number for scope_id in deleted_ids}
    incoming = tuple(
        (view.id, blocker)
        for view in views
        if view.id not in deleted_ids
        for blocker in session.node(view.id).blocked_by
        if blocker in deleted_numbers
    )
    if incoming and not namespace.detach_dependencies:
        raise ValueError("DETACH_DEPENDENCIES_REQUIRED")
    source = session.scopes.directory(target.id)
    for view in descendants:
        found = session.scopes.directory(view.id)
        if source is not None and found is not None and not found.relative.is_relative_to(source.relative):
            raise ValueError(
                f"{view.id} lies outside {source.relative}; run spec-dock scope move {view.id} first, "
                "so its directory is backed up and removed with the subtree"
            )
    # A rerun after a stopped GitHub step finds the directory already gone and only finishes the GitHub steps.
    relative = source.relative if source is not None else None
    root = linked.catalog / relative if relative is not None else None
    if root is not None and (
        backup.is_relative_to(root) or root.is_relative_to(backup) or backup.is_relative_to(context.common_dir)
    ):
        raise ValueError("backup must not overlap the deleted subtree or Git metadata")
    record_path = (
        context.root / "spec-dock/.agent/work-target" / selection.handle.basename
        if clear and selection.handle is not None
        else None
    )
    record_bytes: bytes | None = None
    if record_path is not None and selection.handle is not None:
        loaded = read_guarded_json_bytes(record_path)
        if (
            loaded is None
            or loaded[2] != selection.handle.file_identity
            or hashlib.sha256(loaded[1]).hexdigest() != selection.handle.content_hash
        ):
            raise ValueError("captured selection changed before backup")
        record_bytes = loaded[1]
    expected_entries = (
        {path.relative_to(root).as_posix(): path.lstat() for path in (root, *root.rglob("*"))} if root else {}
    )
    expected = tree_digest(root) if root is not None else None
    parent_number = session.node(target.id).parent
    shown = relative.as_posix() if relative is not None else target.id
    steps: list[tuple[str, str | None]] = []
    if root is not None:
        steps.append(("backup", str(backup)))
    if clear and selection.handle is not None:
        steps.append(("selection.clear", selection.handle.token))
    if relative is not None:
        steps.append(("scope.delete", shown))
    steps.extend(("dependency-edge", f"{scope_id}->{_id_of(session, blocker)}") for scope_id, blocker in incoming)
    if parent_number is not None:
        steps.append(("github.sub-issue.remove", target.id))
    steps.extend(("github.issue.label", scope_id) for scope_id in reversed(deleted_ids))

    def data(removed: tuple[str, ...], changed: list[str], remaining: list[str]) -> FamilyData:
        return FamilyData(
            "deletion",
            {
                "removed_ids": removed,
                "changed_paths": tuple(changed),
                "remaining_paths": tuple(remaining),
                "backup_path": str(backup),
            },
        )

    if namespace.dry_run:
        return planned(
            namespace.command_path,
            FamilyData("deletion", {**data((), [], [shown]).result, "can_apply": True, "blockers": ()}),
            steps,
            session.warnings,
        )
    if not confirmed_interactively(
        namespace,
        (
            f"Target: {target.id}; subtree: {root or 'none (already removed)'}",
            f"Backup: {backup}; removed Scopes: {', '.join(deleted_ids)}",
            f"Incoming dependencies detached: {', '.join(scope_id for scope_id, _ in incoming) or 'none'}",
            f"Clear captured direct selection: {'yes' if clear else 'no'}",
        ),
    ):
        return declined(namespace.command_path, data((), [], [shown]))
    changed: list[str] = []
    try:
        if root is not None and relative is not None and expected is not None:
            try:
                _write_backup(backup, relative, root, expected, record_path, record_bytes, context.root)
            except LOCAL_FAILURES:
                session.effects.append(
                    Effect("backup", "unknown" if os.path.lexists(backup) else "failed", str(backup))
                )
                raise
            session.effects.append(Effect("backup", "succeeded", str(backup)))
        if clear and selection.handle is not None:
            with WorkTargetStore(context.root) as store:
                try:
                    outcome = store.remove_observed(selection.handle)
                except SelectionRemovalUnknown:
                    session.effects.append(Effect("selection.clear", "unknown", selection.handle.token))
                    raise
            if outcome == "conflict":
                session.effects.append(Effect("selection.clear", "failed", selection.handle.token))
                raise ValueError("captured selection changed before clear")
            session.effects.append(
                Effect("selection.clear", "succeeded" if outcome == "removed" else "unchanged", selection.handle.token)
            )
        if root is not None and relative is not None:
            with session.catalog_changes() as changes:
                if tree_digest(root) != expected:
                    raise ValueError("delete subtree changed after the backup")
                try:
                    remove_tree(root, expected_entries=expected_entries)
                except TreeRemovalIncomplete as error:
                    if error.applied:
                        changes.delete(relative)
                        session.effects.append(Effect("scope.delete", "unknown", shown))
                    raise error.cause from error
                changes.delete(relative)
            changed.append(shown)
            session.effects.append(Effect("scope.delete", "succeeded", shown))
        for scope_id, blocker in incoming:
            number = session.node(scope_id).number
            blocker_id = session.scopes.snapshot.issues[blocker].database_id
            session.write(
                "dependency-edge",
                f"{scope_id}->{_id_of(session, blocker)}",
                lambda number=number, blocker=blocker, blocker_id=blocker_id: session.client.remove_blocked_by(
                    number, blocker=blocker, blocker_id=blocker_id
                ),
                lambda _, number=number, blocker=blocker: [RemoveBlockedBy(number, blocker)],
            )
        node = session.node(target.id)
        if parent_number is not None:
            session.write(
                "github.sub-issue.remove",
                target.id,
                lambda: session.client.remove_sub_issue(parent_number, child=node.number, child_id=node.database_id),
                lambda _: [SetParent(node.number, None)],
            )
        for scope_id in reversed(deleted_ids):
            removed = session.node(scope_id)
            kind_label = KIND_LABELS[removed.kind] if removed.kind else None
            if kind_label is None:
                continue
            facts = session.known_facts(removed.number)
            session.write(
                "github.issue.label",
                scope_id,
                lambda removed=removed, kind_label=kind_label: session.client.remove_label(removed.number, kind_label),
                lambda _, facts=facts, kind_label=kind_label: [
                    UpsertIssue(replace(facts, labels=tuple(label for label in facts.labels if label != kind_label)))
                ],
            )
    except (WriteFailed, *LOCAL_FAILURES) as error:
        remaining = [step for step in steps if step[0] not in {effect.kind for effect in session.effects}]
        return session.incomplete(
            data((), changed, [] if changed else [shown]),
            error,
            pending=remaining,
            code="SCOPE_DELETE_INCOMPLETE",
            recovery=(
                f"Inspect the retained backup and GitHub, then run the same spec-dock scope delete {target.id} with a "
                "new --backup-dir; it skips what is already done and finishes the GitHub steps.",
            ),
        )
    return session.result("succeeded", data(deleted_ids, changed, []))


def require_known_descendants(session: WriteSession, scope_id: str) -> None:
    """Completion needs every Scope child known: a foreign or undecided child cannot be checked as completed."""
    snapshot = session.scopes.snapshot
    pending = [session.node(scope_id).number]
    seen: set[int] = set()
    while pending:
        number = pending.pop()
        if number in seen:
            continue
        seen.add(number)
        if any(item.code == SUB_ISSUE_FOREIGN_REPOSITORY for item in snapshot.anomalies_for(number)):
            raise ValueError(f"DESCENDANT_STATUS_UNKNOWN: #{number} has a sub-issue in another repository")
        node = snapshot.issues.get(number)
        for child in node.sub_issues if node is not None else ():
            child_node = snapshot.issues.get(child)
            if child_node is None:
                continue  # a plain Issue is no Scope
            if child_node.id is None:
                raise ValueError(f"DESCENDANT_STATUS_UNKNOWN: #{child} has a Scope label but no decided ID")
            pending.append(child)


def _follow_moved_selections(session: WriteSession, moved: str, timeout: float) -> None:
    """Point this checkout's active links at the new place; warn for other worktrees selecting the moved range."""
    from spec_dock.runtime.application.active_links import sync_selection_links
    from spec_dock.runtime.application.canonical_workspace import _observe_rows

    views = session.scopes.views
    moved_ids = {moved} | {view.id for view in views if moved in {item.id for item in ancestors_for(views, view)}}
    for row in _observe_rows(session.context, session.scopes, timeout=timeout):
        record = row.selection.record
        if record is None or record.scope_id not in moved_ids:
            continue
        if Path(row.path).resolve() == session.context.root.resolve():
            effects, warnings = sync_selection_links(session.context, views, record.scope_id, dry_run=False, timeout=timeout)
            session.effects.extend(effects)
            session.warnings.extend(warnings)
        else:
            step = f"In {row.path}, run spec-dock active set {record.scope_id}."
            session.warnings.append(
                Diagnostic(
                    "ACTIVE_LINK_NOT_UPDATED",
                    f"{row.path} selects {record.scope_id}, whose directory moved; next: {step}",
                    {"path": row.path, "scope_id": record.scope_id, "next_step": step},
                )
            )


def _backup_destination(value: str | None) -> Path:
    if value is None:
        raise ValueError("Scope deletion requires --backup-dir ABS")
    backup = Path(value)
    if not backup.is_absolute():
        raise ValueError("--backup-dir must be absolute")
    backup = Path(os.path.normpath(backup))
    if os.path.lexists(backup):
        raise ValueError("backup destination already exists")
    if any(path.is_symlink() for path in (backup.parent, *backup.parent.parents)):
        raise ValueError("backup parent must not be redirected")
    existing = backup.parent
    while not os.path.lexists(existing):
        existing = existing.parent
    if not existing.is_dir():
        raise ValueError("backup parent must be a directory")
    os.close(open_guarded_directory(existing))
    return backup


def _write_backup(
    backup: Path,
    relative: PurePosixPath,
    root: Path,
    expected: str,
    record_path: Path | None,
    record_bytes: bytes | None,
    checkout: Path,
) -> None:
    """Copy the subtree (and the cleared selection record) to the new backup directory and verify it."""
    parent_fd = _create_guarded_directory(backup.parent)
    try:
        os.mkdir(backup.name, mode=0o700, dir_fd=parent_fd)
    finally:
        os.close(parent_fd)
    backup_fd = open_guarded_directory(backup)
    try:
        copy_tree_at(backup_fd, Path(relative), root)
        verify_backup_root(backup, backup_fd)
        if record_path is not None and record_bytes is not None:
            copy_bytes_at(
                backup_fd, record_path.relative_to(checkout), record_bytes, stat.S_IMODE(record_path.stat().st_mode)
            )
            verify_backup_root(backup, backup_fd)
    finally:
        os.close(backup_fd)
    if tree_digest(backup / relative) != expected:
        raise ValueError("backup content verification failed")


def _id_of(session: WriteSession, number: int) -> str:
    node = session.scopes.snapshot.issues.get(number)
    return node.id if node is not None and node.id is not None else f"#{number}"


def _scope_data(session: WriteSession, scope_id: str, *, changed: bool) -> FamilyData:
    view = session.scopes.view(scope_id)
    return FamilyData(
        "scope",
        {
            "scope": session.scopes.payload(view),
            "github_ref": view.github_ref,
            "changed": changed,
            "snapshot": session.scopes.snapshot_payload(),
        },
    )


def _dry(data: FamilyData) -> FamilyData:
    return FamilyData(data.kind, {**data.result, "can_apply": True, "blockers": ()})
