"""Canonical-mode `scope create` and `scope import github` (iss-00432; Epic design ch. 2, 6 and 7).

GitHub gets the Issue (title and kind label only; SpecDock writes nothing in the body) and its parent first; the
Scope directory is then published at `<catalog>/<bucket>/<ID>/` from the template, without the front matter
title and parent lines, under the catalog lock with one changeset. No `.meta.json` is written. A failure after
the Issue exists is partial, and `scope import github` completes it: it adds only what is missing, so running it
again changes nothing.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import os
from pathlib import Path
from typing import TYPE_CHECKING, cast

from spec_dock.runtime.application.canonical_errors import CANONICAL_PATH_OCCUPIED, CanonicalCommandError
from spec_dock.runtime.application.canonical_scopes import kind_change_error
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
    refuse_slug,
)
from spec_dock.runtime.application.scope_scaffold import (
    _create_relative_symlink_at,
    _precheck_pre_github_create_rules_sources,
    _replacements,
    _rules_scaffold_specs,
    _scaffold_file_paths,
)
from spec_dock.runtime.domain.canonical_layout import scope_bucket, scope_relative
from spec_dock.runtime.domain.canonical_scaffold import validate_canonical_title
from spec_dock.runtime.domain.canonical_structure import (
    KIND_LABELS,
    PARENT_KINDS,
    AddBlockedBy,
    ExternalIssue,
    KindChange,
    SetParent,
    UpsertIssue,
    kind_from_labels,
    parse_scope_id,
    scope_id as canonical_scope_id,
)
from spec_dock.runtime.domain.selectors import parse_github_ref
from spec_dock.runtime.infra.canonical_scaffold import BucketOccupied, copy_scope_template_at, prepare_bucket
from spec_dock.runtime.infra.directory_publication import DirectoryPublicationIncomplete, publish_directory
from spec_dock.runtime.infra.json_store import require_directory_publication_support
from spec_dock.runtime.presentation.command_data import DiagnosticData, FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.canonical_writes import WriteSession
    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.scope_query import ScopeView
    from spec_dock.runtime.application.worktree_observation import SelectionObservation
    from spec_dock.runtime.domain.canonical_structure import IssueFacts, StructureChange
    from spec_dock.runtime.domain.selectors import ScopeKind
    from spec_dock.runtime.presentation.envelope import ResultStatus

CANONICAL_TITLE_IGNORED = "CANONICAL_TITLE_IGNORED"
TITLE_IGNORED_NEXT_STEP = "To change the title, run spec-dock scope edit <ID> --title <title>."


def create_scope(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    context.require_writer()
    refuse_slug(namespace)
    if needs_confirmation(namespace):
        return OperationResult(
            namespace.command_path,
            "failed",
            DiagnosticData(),
            3,
            error=Diagnostic("CONFIRMATION_REQUIRED", "GitHub Scope creation requires --yes", {}),
        )
    kind = cast("ScopeKind", namespace.command_path.rsplit(" ", 1)[-1])
    title = validate_canonical_title(namespace.title, field="--title")
    session = open_write_session(context, namespace, link=True)
    selection = session.selection()
    check_expectations(session, namespace, selection, None)
    parent = _parent(session, kind, getattr(namespace, "parent", None), selection)
    _check_scaffold_sources(session, kind)
    require_directory_publication_support()
    ref_repository = session.repository.slug
    preview = FamilyData("scope", {"scope": None, "github_ref": None, "title": title, "changed": False})
    steps: list[tuple[str, str | None]] = [("github-create", ref_repository)]
    if parent is not None:
        steps.append(("github.sub-issue.add", parent.id))
    steps.append(("scaffold", None))
    if namespace.dry_run:
        return planned(
            namespace.command_path,
            FamilyData("scope", {**preview.result, "can_apply": True, "blockers": ()}),
            steps,
            session.warnings,
        )
    if not confirmed_interactively(
        namespace,
        (
            f"Target: {kind} {title}",
            f"Repository: {ref_repository}; catalog: {session.catalog.catalog if session.catalog else None}",
            "Writes: " + ", ".join(kind for kind, _ in steps),
        ),
    ):
        return declined(namespace.command_path, preview)
    label = KIND_LABELS[kind]
    try:
        session.ensure_labels([label])
        created = session.write(
            "github-create",
            ref_repository,
            lambda: session.client.create_issue(title=title, labels=[label]),
            lambda facts: [UpsertIssue(facts)],
        )
    except WriteFailed as error:
        recovery = (
            (
                "GitHub may have created the Issue but its number is unknown: find it in the repository, "
                f"then run {_import_command(kind, '<number>', parent, title)}.",
            )
            if error.cause.uncertain
            else ()
        )
        return session.incomplete(preview, error, pending=steps[1:], recovery=recovery)
    session.facts[created.number] = created
    ref = f"gh:{ref_repository}#{created.number}"
    scope_id = canonical_scope_id(kind, created.number)
    resume = f"Run {_import_command(kind, str(created.number), parent, title)}; it adds only what is missing."
    data = FamilyData("scope", {"scope": None, "github_ref": ref, "title": title, "changed": True})
    try:
        if parent is not None:
            session.write(
                "github.sub-issue.add",
                parent.id,
                lambda: session.client.add_sub_issue(
                    session.node(parent.id).number, child=created.number, child_id=created.database_id
                ),
                lambda _: [SetParent(created.number, session.node(parent.id).number)],
            )
        _publish(session, kind, scope_id, title, created.number, parent)
    except WRITE_FAILURES as error:
        remaining = [step for step in steps if step[0] not in {effect.kind for effect in session.effects}]
        return session.incomplete(
            data, error, pending=remaining, recovery=(resume,), code="SCOPE_PUBLICATION_INCOMPLETE"
        )
    return session.result("succeeded", _scope_data(session, scope_id, ref))


def import_scope(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    context.require_writer()
    refuse_slug(namespace)
    kind = cast("ScopeKind", namespace.command_path.rsplit(" ", 1)[-1])
    if namespace.github_repo is not None or not namespace.github_ref.strip().isdigit():
        parse_github_ref(namespace.github_ref, repo_hint=namespace.github_repo)  # its shape, before reading GitHub
    session = open_write_session(context, namespace, link=True)
    # A bare number names an Issue of this checkout's repository (the recovery of scope create shows one).
    imported = parse_github_ref(namespace.github_ref, repo_hint=namespace.github_repo or session.repository.slug)
    if f"{imported.owner}/{imported.repo}" != session.repository.slug:
        raise ValueError("foreign GitHub Issue import is rejected")
    number = imported.issue_number
    selection = session.selection()
    check_expectations(session, namespace, selection, None)
    parent = _parent(session, kind, getattr(namespace, "parent", None), selection)
    session.reread([number])
    facts = session.facts[number]
    label = KIND_LABELS[kind]
    labelled, anomaly = kind_from_labels(facts.labels)
    if anomaly is not None or (labelled is not None and labelled != kind):
        raise ValueError(f"#{number} already carries another spec-dock kind label; import it as that kind")
    try:
        validate_canonical_title(facts.title, field=f"the GitHub title of #{number}")
    except ValueError as error:
        raise ValueError(f"{error}; fix the title on GitHub, then import again") from error
    scope_id = canonical_scope_id(kind, number)
    _refuse_other_kind_directories(session, number, scope_id)
    github_parent = session.client.get_parent(number)
    if parent is None and github_parent is not None:
        raise ValueError(f"#{number} has a GitHub parent; an Initiative has none")
    if (
        parent is not None
        and github_parent is not None
        and (
            github_parent.repository != session.repository.slug
            or github_parent.number != session.node(parent.id).number
        )
    ):
        raise ValueError(
            f"#{number} already has GitHub parent {github_parent.repository}#{github_parent.number}; "
            "import it with that --parent and then run spec-dock scope move <ID> --parent <parent> if needed, "
            "or fix the parent on GitHub before importing"
        )
    existing = session.catalog.tree.find(scope_id) if session.catalog is not None else None
    if existing is None:
        _check_scaffold_sources(session, kind)
        _check_bucket(session, number)
        require_directory_publication_support()
    _warn_title_ignored(session, namespace.title, facts.title)
    steps: list[tuple[str, str | None]] = []
    if labelled is None:
        steps.append(("github.issue.label", label))
    if parent is not None and github_parent is None:
        steps.append(("github.sub-issue.add", parent.id))
    if existing is None:
        steps.append(("scaffold", scope_id))
    ref = f"gh:{session.repository.slug}#{number}"
    if namespace.dry_run:
        return planned(
            namespace.command_path,
            FamilyData(
                "scope", {"scope": None, "github_ref": ref, "changed": False, "can_apply": True, "blockers": ()}
            ),
            steps,
            session.warnings,
        )
    relations = _relations(session, number)
    try:
        if labelled is None:
            session.ensure_labels([label])
            labels = session.write("github.issue.label", label, lambda: session.client.add_labels(number, [label]))
            facts = _with_labels(facts, labels)
            session.facts[number] = facts
        session.reflect([UpsertIssue(facts), *relations])
        if parent is not None and github_parent is None:
            database_id = facts.database_id
            session.write(
                "github.sub-issue.add",
                parent.id,
                lambda: session.client.add_sub_issue(
                    session.node(parent.id).number, child=number, child_id=database_id
                ),
                lambda _: [SetParent(number, session.node(parent.id).number)],
            )
        if existing is None:
            _publish(session, kind, scope_id, facts.title, number, parent)
    except WRITE_FAILURES as error:
        remaining = [step for step in steps if step[0] not in {effect.kind for effect in session.effects}]
        return session.incomplete(
            FamilyData("scope", {"scope": None, "github_ref": ref, "changed": bool(session.effects)}),
            error,
            pending=remaining,
            recovery=(
                f"Run the same spec-dock scope import github {kind} {number} again; it adds only what is missing.",
            ),
            code="SCOPE_PUBLICATION_INCOMPLETE",
        )
    status: ResultStatus = (
        "succeeded" if any(effect.status == "succeeded" for effect in session.effects) else "unchanged"
    )
    data = _scope_data(session, scope_id, ref, changed=status == "succeeded")
    return session.result(status, data)


def _parent(
    session: WriteSession, kind: ScopeKind, selector: str | None, selection: SelectionObservation
) -> ScopeView | None:
    """Resolve, reread and check the parent: kind rule, open chain and no kind change (all before writes)."""
    required = PARENT_KINDS[kind]
    if required is None:
        if selector is not None:
            raise ValueError("initiative cannot have a parent")
        return None
    if selector is None:
        raise ValueError(f"{kind} requires an explicit parent")
    resolved = session.resolve(selector, selection)
    if resolved.kind != required:
        raise ValueError(f"{kind} parent must be a {required}")
    number = session.node(resolved.id).number
    session.reread([number])
    session.require_kind_unchanged(*session.scopes.lineage(resolved.id))
    require_open_chain(session, resolved.id)
    return session.scopes.view(resolved.id)


def require_open_chain(session: WriteSession, scope_id: str) -> None:
    """The Scope and every ancestor must be open on GitHub (the snapshot after the reread)."""
    current: str | None = scope_id
    seen: set[str] = set()
    while current is not None:
        if current in seen:
            raise ValueError("SCOPE_ANCESTRY_INVALID")
        seen.add(current)
        if session.node(current).state != "open":
            raise ValueError(f"GitHub Scope ancestor {current} is not open")
        current = session.scopes.view(current).parent_id


def _refuse_other_kind_directories(session: WriteSession, number: int, scope_id: str) -> None:
    """A catalog directory of the same number under another kind is a kind change, before any label is added."""
    if session.catalog is None:
        return
    others = tuple(
        sorted(
            item.scope_id
            for item in session.catalog.tree.directories()
            if parse_scope_id(item.scope_id)[1] == number and item.scope_id != scope_id
        )
    )
    if others:
        raise kind_change_error(KindChange(number, scope_id, others))


def _check_bucket(session: WriteSession, number: int) -> None:
    assert session.catalog is not None
    bucket = session.catalog.catalog / scope_bucket(number)
    if os.path.lexists(bucket) and (bucket.is_symlink() or not bucket.is_dir()):
        raise _bucket_occupied(BucketOccupied(bucket))


def _bucket_occupied(error: BucketOccupied) -> CanonicalCommandError:
    return CanonicalCommandError(
        CANONICAL_PATH_OCCUPIED,
        str(error),
        recovery=(f"Check what is at {error.path} and move it away; SpecDock does not remove it.",),
        details={"path": str(error.path)},
    )


def _warn_title_ignored(session: WriteSession, given: str, github_title: str) -> None:
    """The shared parser requires --title; canonical mode keeps GitHub's title (coordinator decision 2026-10-29)."""
    if given.strip() == github_title:
        return
    session.warnings.append(
        Diagnostic(
            CANONICAL_TITLE_IGNORED,
            "--title is not used in canonical mode; the Scope keeps its GitHub title",
            {"given": given, "github_title": github_title, "next_step": TITLE_IGNORED_NEXT_STEP},
        )
    )


def _relations(session: WriteSession, number: int) -> list[StructureChange]:
    """Reflect the imported Issue's parent, children and blockers as GitHub reports them now."""
    own = session.repository.slug
    changes: list[StructureChange] = []
    parent = session.client.get_parent(number)
    if parent is not None and parent.repository == own:
        changes.append(SetParent(number, parent.number))
    for child in session.client.list_sub_issues(number):
        # Only Scope children are represented; a plain child is no structure, so skipping it is not staleness.
        if child.repository == own and child.number in session.scopes.snapshot.issues:
            changes.append(SetParent(child.number, number))
    for blocker in session.client.list_blocked_by(number):
        if blocker.repository == own:
            external = ExternalIssue(
                blocker.number, blocker.title or "", "closed" if blocker.state == "closed" else "open"
            )
            changes.append(AddBlockedBy(number, blocker.number, external))
    return changes


def _with_labels(facts: IssueFacts, labels: tuple[str, ...]) -> IssueFacts:
    return replace(facts, labels=tuple(labels))


def _check_scaffold_sources(session: WriteSession, kind: ScopeKind) -> None:
    _scaffold_file_paths(session.context.root / "spec-dock/templates" / kind, session.context.root)
    _precheck_pre_github_create_rules_sources(kind=kind, specdock_dir=_main_spec_dock(session))
    discussions = _main_spec_dock(session) / "docs/rules" / kind / "discussions.md"
    if not discussions.is_file():
        raise FileNotFoundError(f"Missing rules source: {discussions}")


def canonical_rules_links(kind: ScopeKind, destination: Path, specdock_dir: Path) -> list[tuple[Path, Path]]:
    """The Artifact and discussion rules links; the catalog has no child-layer rules (epics/, issues/)."""
    artifacts = [
        (link, target)
        for link, target in _rules_scaffold_specs(kind=kind, dest_dir=destination, specdock_dir=specdock_dir)
        if link.parent.name == "artifacts"
    ]
    return [*artifacts, (destination / "discussions/rules.md", specdock_dir / "docs/rules" / kind / "discussions.md")]


def _main_spec_dock(session: WriteSession) -> Path:
    assert session.catalog is not None
    return Path(os.path.realpath(session.catalog.layout.main_checkout)) / "spec-dock"


def _publish(
    session: WriteSession,
    kind: ScopeKind,
    scope_id: str,
    title: str,
    number: int,
    parent: ScopeView | None,
) -> None:
    """Publish `<catalog>/<bucket>/<ID>/` once under the catalog lock and record it in one changeset."""
    linked = session.catalog
    assert linked is not None
    relative = scope_relative(scope_id)
    destination = linked.catalog / relative
    replacements = _replacements(
        kind=kind,
        node_id=scope_id,
        title=title,
        parent_id=parent.id if parent is not None else None,
        initiative_id=(parent.id if kind == "epic" else parent.parent_id) if parent is not None else None,
        github_issue_number=number,
        today=datetime.now(timezone.utc).date().isoformat(),
    )
    templates = session.context.root / "spec-dock/templates" / kind
    rules = canonical_rules_links(kind, destination, _main_spec_dock(session))

    def populate(descriptor: int) -> None:
        copy_scope_template_at(templates, destination, descriptor, replacements)
        for link, target in rules:
            _create_relative_symlink_at(descriptor, node_dir=destination, link_path=link, target_path=target)

    try:
        with session.catalog_changes() as changes:
            try:
                prepare_bucket(linked.catalog, relative.parent.as_posix())
            except BucketOccupied as error:
                raise _bucket_occupied(error) from error
            try:
                publish_directory(
                    destination,
                    staging_dir=changes.staging(),
                    populate=populate,
                    before_stage=lambda _path: None,
                    before_publish=lambda: None,
                )
            except DirectoryPublicationIncomplete as error:
                if error.confirmed:
                    changes.add(relative)
                    session.effects.append(Effect("scaffold", "succeeded", scope_id))
                else:
                    session.effects.append(Effect("scaffold", "unknown", scope_id))
                raise
            changes.add(relative)
    except LOCAL_FAILURES:
        if not any(effect.kind == "scaffold" for effect in session.effects):
            session.effects.append(Effect("scaffold", "failed", scope_id))
        raise
    session.effects.append(Effect("scaffold", "succeeded", scope_id))
    session.reload_catalog()


def _import_command(kind: ScopeKind, number: str, parent: ScopeView | None, title: str) -> str:
    parent_option = f" --parent {parent.id}" if parent is not None else ""
    return f"spec-dock scope import github {kind} {number}{parent_option} --title '{title}'"


def _scope_data(session: WriteSession, scope_id: str, ref: str, *, changed: bool = True) -> FamilyData:
    view = session.scopes.view(scope_id)
    return FamilyData(
        "scope",
        {
            "scope": session.scopes.payload(view),
            "github_ref": ref,
            "changed": changed,
            "snapshot": session.scopes.snapshot_payload(),
        },
    )
