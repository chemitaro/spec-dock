"""Canonical-mode `scope edit`, `scope move`, `scope close`, `scope reopen` and `scope delete` (iss-00432).

Titles, states and parents change on GitHub after a `decision` check and a reread of the target; the flat
catalog directories never move. `scope delete` takes the Scope out of the structure (kind labels, parent,
incoming dependencies) and removes each `<bucket>/<ID>/` after a verified backup; the Issue itself is never
closed or deleted.
"""

from __future__ import annotations

from dataclasses import replace
import hashlib
import os
from pathlib import Path, PurePosixPath
import stat
from typing import TYPE_CHECKING, cast

from spec_dock.runtime.application.canonical_scope_create import require_open_chain
from spec_dock.runtime.application.canonical_writes import (
    LOCAL_FAILURES,
    WRITE_FAILURES,
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
from spec_dock.runtime.domain.canonical_scaffold import validate_canonical_title
from spec_dock.runtime.domain.canonical_structure import (
    KIND_LABELS,
    PARENT_KINDS,
    SUB_ISSUE_FOREIGN_REPOSITORY,
    RemoveBlockedBy,
    SetParent,
    UpsertIssue,
)
from spec_dock.runtime.infra.canonical_scaffold import remove_empty_bucket
from spec_dock.runtime.infra.direct_json import _create_guarded_directory
from spec_dock.runtime.infra.git_process import GitProcessError
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
    from spec_dock.runtime.domain.lifecycle import ObservedState


def edit_scope(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    """Change only the GitHub title; catalog files keep their creation-time headings."""
    context.require_writer()
    title = validate_canonical_title(namespace.title, field="--title")
    session = open_write_session(context, namespace, link=False)
    selection = session.selection()
    target = session.resolve(namespace.target, selection)
    check_expectations(session, namespace, selection, target)
    session.require_kind_unchanged(target.id)
    number = session.node(target.id).number
    session.reread([number])
    if session.node(target.id).title == title:
        data = _scope_data(session, target.id, changed=False)
        if namespace.dry_run:
            return planned(namespace.command_path, _dry(data), (), session.warnings)
        return session.result("unchanged", data)
    if namespace.dry_run:
        return planned(
            namespace.command_path,
            _dry(_scope_data(session, target.id, changed=False)),
            (("github.issue.title", target.id),),
            session.warnings,
        )
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
    session.require_kind_unchanged(target.id)
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
            lambda: (
                session.client.update_issue(
                    number,
                    state="closed",
                    state_reason="completed" if reason == "completed" else "not_planned",
                )
                if close
                else session.client.update_issue(number, state="open")
            ),
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
    """Change only the GitHub parent (replace_parent); the flat catalog directory stays where it is."""
    context.require_writer()
    session = open_write_session(context, namespace, link=False)
    selection = session.selection()
    target = session.resolve(namespace.target, selection)
    check_expectations(session, namespace, selection, target)
    required = PARENT_KINDS[target.kind]
    if required is None:
        raise ValueError("an initiative has no parent to change")
    new_parent = session.resolve(namespace.parent, selection)
    if new_parent.kind != required:
        raise ValueError(f"{target.kind} parent must be a {required}")
    child_number, parent_number = session.node(target.id).number, session.node(new_parent.id).number
    session.reread([child_number, parent_number])
    session.reread_parent(child_number)
    session.reread_parent(parent_number)
    session.require_kind_unchanged(target.id, *session.scopes.lineage(new_parent.id))
    parent_view = session.scopes.view(new_parent.id)
    if new_parent.id == target.id or target.id in {
        view.id for view in ancestors_for(session.scopes.views, parent_view)
    }:
        raise ValueError("a Scope cannot move below itself or its descendants")
    require_open_chain(session, new_parent.id)
    before = session.scopes.view(target.id).parent_id
    changed = before != new_parent.id

    def data(changed: bool) -> FamilyData:
        base = _scope_data(session, target.id, changed=changed)
        after = session.scopes.view(target.id).parent_id
        return FamilyData("scope", {**base.result, "parent_before": before, "parent_after": after})

    steps: list[tuple[str, str | None]] = [("github.sub-issue.add", new_parent.id)] if changed else []
    if namespace.dry_run:
        return planned(namespace.command_path, _dry(data(False)), steps, session.warnings)
    if not changed:
        return session.result("unchanged", data(False))
    child = session.node(target.id)
    try:
        session.write(
            "github.sub-issue.add",
            new_parent.id,
            lambda: session.client.add_sub_issue(
                parent_number, child=child.number, child_id=child.database_id, replace_parent=True
            ),
            lambda _: [SetParent(child.number, parent_number)],
        )
    except WriteFailed as error:
        return session.incomplete(
            data(False),
            error,
            recovery=(f"Inspect the GitHub parent of {target.github_ref} before a new explicit move.",),
        )
    _follow_moved_selections(session, target.id, namespace.timeout)
    return session.result("succeeded", data(True))


def _follow_moved_selections(session: WriteSession, moved: str, timeout: float) -> None:
    """spec-dock/active also links the ancestors: align this checkout, warn for other worktrees (never fails)."""
    from spec_dock.runtime.application.active_links import sync_selection_links
    from spec_dock.runtime.application.canonical_workspace import _observe_rows

    scopes = session.scopes
    moved_ids = {moved} | {view.id for view in scopes.views if moved in scopes.lineage(view.id)[1:]}
    try:
        rows = _observe_rows(session.context, scopes, timeout=timeout)
    except (OSError, ValueError, RuntimeError, GitProcessError):
        return
    own = session.context.root.resolve()
    for row in rows:
        record = row.selection.record
        if record is None or record.scope_id not in moved_ids:
            continue
        if Path(row.path).resolve() == own:
            effects, warnings = sync_selection_links(
                session.context, scopes.views, record.scope_id, dry_run=False, timeout=timeout
            )
            session.effects.extend(effects)
            session.warnings.extend(warnings)
            continue
        step = f"In {row.path}, run spec-dock active set {record.scope_id}."
        session.warnings.append(
            Diagnostic(
                "ACTIVE_LINK_NOT_UPDATED",
                f"{row.path} selects {record.scope_id}, whose GitHub parent chain changed; next: {step}",
                {"path": row.path, "scope_id": record.scope_id, "next_step": step},
            )
        )


def delete_scope(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    """Back up, then remove each flat directory, then detach on GitHub (dependencies, parent, kind labels)."""
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
    # The unchecked GitHub parent chain: a kind change may break the checked chain, and delete must still work.
    descendants = tuple(view for view in views if target.id in session.scopes.lineage(view.id)[1:])
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
    # A rerun after a stopped step finds some directories already gone and only finishes the rest.
    relatives = _deleted_directories(session, deleted_ids)
    roots = {relative: linked.catalog / relative for relative in relatives}
    if any(backup.is_relative_to(root) or root.is_relative_to(backup) for root in roots.values()) or any(
        backup.is_relative_to(path) for path in (linked.catalog, context.common_dir)
    ):
        raise ValueError("backup must not overlap the catalog, the deleted directories or Git metadata")
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
    expected_entries = {
        relative: {path.relative_to(root).as_posix(): path.lstat() for path in (root, *root.rglob("*"))}
        for relative, root in roots.items()
    }
    expected = {relative: tree_digest(root) for relative, root in roots.items()}
    parent_number = session.node(target.id).parent
    shown = [relative.as_posix() for relative in relatives]
    steps: list[tuple[str, str | None]] = []
    if relatives:
        steps.append(("backup", str(backup)))
    if clear and selection.handle is not None:
        steps.append(("selection.clear", selection.handle.token))
    steps.extend(("scope.delete", path) for path in shown)
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
            FamilyData("deletion", {**data((), [], shown).result, "can_apply": True, "blockers": ()}),
            steps,
            session.warnings,
        )
    if not confirmed_interactively(
        namespace,
        (
            f"Target: {target.id}; directories: {', '.join(shown) or 'none (already removed)'}",
            f"Backup: {backup}; removed Scopes: {', '.join(deleted_ids)}",
            f"Incoming dependencies detached: {', '.join(scope_id for scope_id, _ in incoming) or 'none'}",
            f"Clear captured direct selection: {'yes' if clear else 'no'}",
        ),
    ):
        return declined(namespace.command_path, data((), [], shown))
    changed: list[str] = []
    try:
        if relatives:
            try:
                _write_backup(backup, roots, expected, record_path, record_bytes, context.root)
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
        if relatives:
            with session.catalog_changes() as changes:
                for relative, root in roots.items():
                    if tree_digest(root) != expected[relative]:
                        raise ValueError(f"{relative} changed after the backup")
                for relative, root in roots.items():
                    try:
                        remove_tree(root, expected_entries=expected_entries[relative])
                    except TreeRemovalIncomplete as error:
                        if error.applied:
                            changes.delete(relative)
                            session.effects.append(Effect("scope.delete", "unknown", relative.as_posix()))
                        raise error.cause from error
                    changes.delete(relative)
                    changed.append(relative.as_posix())
                    session.effects.append(Effect("scope.delete", "succeeded", relative.as_posix()))
                for bucket in sorted({relative.parent.as_posix() for relative in relatives}):
                    remove_empty_bucket(linked.catalog, bucket)
        for scope_id, blocker in incoming:
            _detach_dependency(session, scope_id, blocker)
        node = session.node(target.id)
        if parent_number is not None:
            session.write(
                "github.sub-issue.remove",
                target.id,
                lambda: session.client.remove_sub_issue(parent_number, child=node.number, child_id=node.database_id),
                lambda _: [SetParent(node.number, None)],
            )
        for scope_id in reversed(deleted_ids):
            _remove_kind_label(session, scope_id)
    except WRITE_FAILURES as error:
        done = {(effect.kind, effect.target) for effect in session.effects}
        return session.incomplete(
            data((), changed, [path for path in shown if path not in changed]),
            error,
            pending=[step for step in steps if step not in done],
            code="SCOPE_DELETE_INCOMPLETE",
            recovery=(
                f"Inspect the retained backup and GitHub, then run the same spec-dock scope delete {target.id} with a "
                "new --backup-dir; it skips what is already done and finishes the rest.",
            ),
        )
    return session.result("succeeded", data(deleted_ids, changed, []))


def _detach_dependency(session: WriteSession, scope_id: str, blocker: int) -> None:
    number = session.node(scope_id).number
    blocker_id = session.scopes.snapshot.issues[blocker].database_id
    session.write(
        "dependency-edge",
        f"{scope_id}->{_id_of(session, blocker)}",
        lambda: session.client.remove_blocked_by(number, blocker=blocker, blocker_id=blocker_id),
        lambda _: [RemoveBlockedBy(number, blocker)],
    )


def _remove_kind_label(session: WriteSession, scope_id: str) -> None:
    """The Issue stops being a Scope; it is never closed or deleted."""
    removed = session.node(scope_id)
    if removed.kind is None:
        return
    kind_label = KIND_LABELS[removed.kind]
    facts = session.known_facts(removed.number)
    session.write(
        "github.issue.label",
        scope_id,
        lambda: session.client.remove_label(removed.number, kind_label),
        lambda _: [UpsertIssue(replace(facts, labels=tuple(label for label in facts.labels if label != kind_label)))],
    )


def _deleted_directories(session: WriteSession, deleted_ids: tuple[str, ...]) -> tuple[PurePosixPath, ...]:
    """Each deleted Scope's `<bucket>/<ID>/` and its number's old-kind directories, as far as they still exist."""
    linked = session.catalog
    assert linked is not None
    found: list[PurePosixPath] = []
    for scope_id in deleted_ids:
        directory = linked.tree.find(scope_id)
        if directory is not None:
            found.append(directory.relative)
        change = session.scopes.kind_changes.get(session.node(scope_id).number)
        for name in change.directories if change is not None else ():
            old = linked.tree.find(name)
            if old is not None:
                found.append(old.relative)
    return tuple(dict.fromkeys(found))


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
    roots: dict[PurePosixPath, Path],
    expected: dict[PurePosixPath, str],
    record_path: Path | None,
    record_bytes: bytes | None,
    checkout: Path,
) -> None:
    """Copy each directory to `<backup>/<bucket>/<name>` (and the cleared selection record) and verify it."""
    parent_fd = _create_guarded_directory(backup.parent)
    try:
        os.mkdir(backup.name, mode=0o700, dir_fd=parent_fd)
    finally:
        os.close(parent_fd)
    backup_fd = open_guarded_directory(backup)
    try:
        for relative, root in roots.items():
            copy_tree_at(backup_fd, Path(relative), root)
            verify_backup_root(backup, backup_fd)
        if record_path is not None and record_bytes is not None:
            copy_bytes_at(
                backup_fd, record_path.relative_to(checkout), record_bytes, stat.S_IMODE(record_path.stat().st_mode)
            )
            verify_backup_root(backup, backup_fd)
    finally:
        os.close(backup_fd)
    for relative in roots:
        if tree_digest(backup / relative) != expected[relative]:
            raise ValueError(f"backup content verification failed for {relative}")


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
