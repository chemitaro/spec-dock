"""Canonical-mode `scope create` and `scope import github` (iss-00432; Epic design ch. 2 and 6).

GitHub gets the Issue, its kind label, its body slug marker and its parent first; the Scope directory is then
published in the catalog from the template, without the front matter title and parent lines, under the catalog
lock with one changeset. No `.meta.json` is written. A failure after the Issue exists is partial, and
`scope import github` completes it: it adds only what is missing, so running it again changes nothing.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import os
from pathlib import Path
from typing import TYPE_CHECKING, cast

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
from spec_dock.runtime.application.scope_scaffold import (
    _create_relative_symlink_at,
    _precheck_pre_github_create_rules_sources,
    _replacements,
    _rules_scaffold_specs,
    _scaffold_file_paths,
)
from spec_dock.runtime.domain.canonical_structure import (
    KIND_LABELS,
    PARENT_KINDS,
    SLUG_MARKER_MISSING,
    AddBlockedBy,
    ExternalIssue,
    SetParent,
    UpsertIssue,
    append_slug_marker,
    kind_from_labels,
    read_slug_marker,
    scope_id as canonical_scope_id,
)
from spec_dock.runtime.domain.ids import resolve_input_title_and_slug
from spec_dock.runtime.domain.selectors import parse_github_ref
from spec_dock.runtime.infra.canonical_scaffold import copy_scope_template_at
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


def create_scope(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    context.require_writer()
    if needs_confirmation(namespace):
        return OperationResult(
            namespace.command_path,
            "failed",
            DiagnosticData(),
            3,
            error=Diagnostic("CONFIRMATION_REQUIRED", "GitHub Scope creation requires --yes", {}),
        )
    kind = cast("ScopeKind", namespace.command_path.rsplit(" ", 1)[-1])
    title, slug = resolve_input_title_and_slug(namespace.title, namespace.slug)
    session = open_write_session(context, namespace, link=True)
    selection = session.selection()
    check_expectations(session, namespace, selection, None)
    parent = _parent(session, kind, getattr(namespace, "parent", None), selection)
    _check_scaffold_sources(session, kind)
    require_directory_publication_support()
    ref_repository = session.repository.slug
    preview = FamilyData("scope", {"scope": None, "github_ref": None, "title": title, "slug": slug, "changed": False})
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
            lambda: session.client.create_issue(
                title=title, body=append_slug_marker(f"Created by SpecDock.\n\nType: {kind}\n", slug), labels=[label]
            ),
            lambda facts: [UpsertIssue(facts)],
        )
    except WriteFailed as error:
        recovery = (
            (
                "GitHub may have created the Issue but its number is unknown: find it in the repository, "
                f"then run spec-dock scope import github {kind} gh:{ref_repository}#<number> "
                + _import_options(parent, title, slug),
            )
            if error.cause.uncertain
            else ()
        )
        return session.incomplete(preview, error, pending=steps[1:], recovery=recovery)
    session.facts[created.number] = created
    ref = f"gh:{ref_repository}#{created.number}"
    scope_id = canonical_scope_id(kind, created.number)
    resume = (
        f"Run spec-dock scope import github {kind} {ref} {_import_options(parent, title, slug)}; "
        "it adds only what is missing."
    )
    data = FamilyData("scope", {"scope": None, "github_ref": ref, "title": title, "slug": slug, "changed": True})
    try:
        if parent is not None:
            session.write(
                "github.sub-issue.add",
                parent.id,
                lambda: session.client.add_sub_issue(session.node(parent.id).number, child=created.number, child_id=created.database_id),
                lambda _: [SetParent(created.number, session.node(parent.id).number)],
            )
        _publish(session, kind, scope_id, slug, title, created.number, parent)
    except (WriteFailed, *LOCAL_FAILURES) as error:
        remaining = [step for step in steps if step[0] not in {effect.kind for effect in session.effects}]
        return session.incomplete(
            data, error, pending=remaining, recovery=(resume,), code="SCOPE_PUBLICATION_INCOMPLETE"
        )
    return session.result("succeeded", _scope_data(session, scope_id, ref))


def import_scope(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    context.require_writer()
    kind = cast("ScopeKind", namespace.command_path.rsplit(" ", 1)[-1])
    imported = parse_github_ref(namespace.github_ref, repo_hint=namespace.github_repo)
    session = open_write_session(context, namespace, link=True)
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
    marker = read_slug_marker(facts.body)
    if marker.anomaly is not None and marker.anomaly != SLUG_MARKER_MISSING:
        raise ValueError(f"#{number} has an unusable slug marker ({marker.anomaly}); keep exactly one valid line")
    if marker.slug is not None:
        if namespace.slug is not None and namespace.slug != marker.slug:
            raise ValueError(f"#{number} already fixes slug {marker.slug}; the slug never changes after creation")
        slug = marker.slug
    else:
        slug = resolve_input_title_and_slug(namespace.title, namespace.slug)[1]
    github_parent = session.client.get_parent(number)
    if parent is None and github_parent is not None:
        raise ValueError(f"#{number} has a GitHub parent; an Initiative has none")
    if parent is not None and github_parent is not None and (
        github_parent.repository != session.repository.slug or github_parent.number != session.node(parent.id).number
    ):
        raise ValueError(
            f"#{number} already has GitHub parent {github_parent.repository}#{github_parent.number}; "
            "import it with that --parent and then run spec-dock scope move <ID> --parent <parent> if needed, "
            "or fix the parent on GitHub before importing"
        )
    scope_id = canonical_scope_id(kind, number)
    existing = session.catalog.tree.find(scope_id) if session.catalog is not None else None
    if existing is not None and existing.relative.name != f"{scope_id}-{slug}":
        raise ValueError(f"the catalog directory {existing.relative} does not carry slug {slug}")
    if existing is None:
        _check_scaffold_sources(session, kind)
        require_directory_publication_support()
    steps: list[tuple[str, str | None]] = []
    if labelled is None:
        steps.append(("github.issue.label", label))
    if marker.slug is None:
        steps.append(("github.issue.body", f"#{number}"))
    if parent is not None and github_parent is None:
        steps.append(("github.sub-issue.add", parent.id))
    if existing is None:
        steps.append(("scaffold", scope_id))
    ref = f"gh:{session.repository.slug}#{number}"
    if namespace.dry_run:
        return planned(
            namespace.command_path,
            FamilyData(
                "scope", {"scope": None, "github_ref": ref, "slug": slug, "changed": False, "can_apply": True, "blockers": ()}
            ),
            steps,
            session.warnings,
        )
    relations = _relations(session, number)
    try:
        if labelled is None:
            session.ensure_labels([label])
            labels = session.write(
                "github.issue.label", label, lambda: session.client.add_labels(number, [label])
            )
            facts = _with_labels(facts, labels)
            session.facts[number] = facts
        session.reflect([UpsertIssue(facts), *relations])
        if marker.slug is None:
            marked = append_slug_marker(facts.body or "", slug)
            facts = session.write(
                "github.issue.body",
                f"#{number}",
                lambda: session.client.update_issue(number, body=marked),
                lambda updated: [UpsertIssue(updated)],
            )
            session.facts[number] = facts
        if parent is not None and github_parent is None:
            database_id = facts.database_id
            session.write(
                "github.sub-issue.add",
                parent.id,
                lambda: session.client.add_sub_issue(session.node(parent.id).number, child=number, child_id=database_id),
                lambda _: [SetParent(number, session.node(parent.id).number)],
            )
        if existing is None:
            _publish(session, kind, scope_id, slug, facts.title, number, parent)
    except (WriteFailed, *LOCAL_FAILURES) as error:
        remaining = [step for step in steps if step[0] not in {effect.kind for effect in session.effects}]
        return session.incomplete(
            FamilyData("scope", {"scope": None, "github_ref": ref, "slug": slug, "changed": bool(session.effects)}),
            error,
            pending=remaining,
            recovery=(f"Run the same spec-dock scope import github {kind} {ref} again; it adds only what is missing.",),
            code="SCOPE_PUBLICATION_INCOMPLETE",
        )
    status = "succeeded" if any(effect.status == "succeeded" for effect in session.effects) else "unchanged"
    data = _scope_data(session, scope_id, ref, changed=status == "succeeded")
    return session.result(status, data)


def _parent(
    session: WriteSession, kind: ScopeKind, selector: str | None, selection: SelectionObservation
) -> ScopeView | None:
    """Resolve, reread and check the parent: kind rule, open chain and a catalog directory (all before writes)."""
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
    require_open_chain(session, resolved.id)
    session.scopes.require_directory(resolved.id)
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
            external = ExternalIssue(blocker.number, blocker.title or "", "closed" if blocker.state == "closed" else "open")
            changes.append(AddBlockedBy(number, blocker.number, external))
    return changes


def _with_labels(facts: IssueFacts, labels: tuple[str, ...]) -> IssueFacts:
    return replace(facts, labels=tuple(labels))


def _check_scaffold_sources(session: WriteSession, kind: ScopeKind) -> None:
    _scaffold_file_paths(session.context.root / "spec-dock/templates" / kind, session.context.root)
    _precheck_pre_github_create_rules_sources(kind=kind, specdock_dir=_main_spec_dock(session))


def _main_spec_dock(session: WriteSession) -> Path:
    assert session.catalog is not None
    return Path(os.path.realpath(session.catalog.layout.main_checkout)) / "spec-dock"


def _publish(
    session: WriteSession,
    kind: ScopeKind,
    scope_id: str,
    slug: str,
    title: str,
    number: int,
    parent: ScopeView | None,
) -> None:
    """Publish the Scope directory once under the catalog lock and record it in one changeset."""
    linked = session.catalog
    assert linked is not None
    if parent is None:
        container = linked.catalog
        parent_id = initiative_id = None
    else:
        found = session.scopes.directory(parent.id)
        if found is None:
            raise FileNotFoundError(f"{parent.id} has no directory in the catalog")
        container = linked.catalog / found.relative / SCOPE_NESTING[kind]
        parent_id = parent.id
        initiative_id = parent.id if kind == "epic" else parent.parent_id
    destination = container / f"{scope_id}-{slug}"
    replacements = _replacements(
        kind=kind,
        node_id=scope_id,
        title=title,
        parent_id=parent_id,
        initiative_id=initiative_id,
        github_issue_number=number,
        today=datetime.now(timezone.utc).date().isoformat(),
    )
    templates = session.context.root / "spec-dock/templates" / kind
    rules = _rules_scaffold_specs(kind=kind, dest_dir=destination, specdock_dir=_main_spec_dock(session))

    def populate(descriptor: int) -> None:
        copy_scope_template_at(templates, destination, descriptor, replacements)
        for link, target in rules:
            _create_relative_symlink_at(descriptor, node_dir=destination, link_path=link, target_path=target)

    try:
        with session.catalog_changes() as changes:
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
                    changes.add(destination.relative_to(linked.catalog))
                    session.effects.append(Effect("scaffold", "succeeded", scope_id))
                else:
                    session.effects.append(Effect("scaffold", "unknown", scope_id))
                raise
            changes.add(destination.relative_to(linked.catalog))
    except LOCAL_FAILURES:
        if not any(effect.kind == "scaffold" for effect in session.effects):
            session.effects.append(Effect("scaffold", "failed", scope_id))
        raise
    session.effects.append(Effect("scaffold", "succeeded", scope_id))
    session.reload_catalog()


def _import_options(parent: ScopeView | None, title: str, slug: str) -> str:
    parent_option = f"--parent {parent.id} " if parent is not None else ""
    return f"{parent_option}--title '{title}' --slug {slug}"


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
