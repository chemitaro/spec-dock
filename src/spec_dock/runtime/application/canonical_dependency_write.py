"""Canonical-mode `dependency add` and `dependency remove` (iss-00432; Epic design ch. 2 and 6).

The edge is GitHub's blocked-by between two Scope Issues. Both ends are read again and the source's current
blocked-by list replaces the snapshot's before deciding; a cycle or a rule violation stops before the write.
No `.meta.json` and no catalog file is written.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from spec_dock.runtime.application.canonical_scope_read import _raw_edges
from spec_dock.runtime.application.canonical_writes import WriteFailed, check_expectations, open_write_session
from spec_dock.runtime.domain.canonical_structure import AddBlockedBy, RemoveBlockedBy, dependency_violations
from spec_dock.runtime.domain.dependency_vnext import dependency_listing
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Effect, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.canonical_writes import WriteSession
    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.presentation.envelope import EffectStatus, ResultStatus


def mutate_dependency(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    context.require_writer()
    remove = namespace.command_path == "dependency remove"
    session = open_write_session(context, namespace, link=False)
    selection = session.selection()
    source = session.resolve(namespace.from_target, selection)
    destination = session.resolve(namespace.to_target, selection)
    check_expectations(session, namespace, selection, source)
    session.require_kind_unchanged(source.id, destination.id)
    number, blocker = session.node(source.id).number, session.node(destination.id).number
    session.reread([number, blocker])
    session.reread_blockers(number)
    session.require_kind_unchanged(source.id, destination.id)  # a kind change only the reread saw
    present = blocker in session.node(source.id).blocked_by
    if remove:
        changed = present
        if not changed and not namespace.missing_ok:
            raise LookupError("dependency edge was not found")
    else:
        changed = not present
        violations = dependency_violations(session.scopes.snapshot, number, blocker) if changed else ()
        if violations:
            details = "; ".join(f"{item.code}: {item.message}" for item in violations)
            raise ValueError(f"adding {source.id} blocked by {destination.id} is not allowed ({details})")
    edge = f"{source.id}->{destination.id}"
    if namespace.dry_run:
        effect: EffectStatus = "planned" if changed else "unchanged"
        return _result(session, source.id, "planned", effect, edge, can_apply=True)
    if not changed:
        return _result(session, source.id, "unchanged", "unchanged", edge)
    blocker_id = session.node(destination.id).database_id
    try:
        if remove:
            session.write(
                "dependency-edge",
                edge,
                lambda: session.client.remove_blocked_by(number, blocker=blocker, blocker_id=blocker_id),
                lambda _: [RemoveBlockedBy(number, blocker)],
            )
        else:
            session.write(
                "dependency-edge",
                edge,
                lambda: session.client.add_blocked_by(number, blocker=blocker, blocker_id=blocker_id),
                lambda _: [AddBlockedBy(number, blocker)],
            )
    except WriteFailed as error:
        return session.incomplete(
            _data(session, source.id, applied=False),
            error,
            recovery=(
                f"Inspect the blocked-by dependencies of {source.github_ref} on GitHub before a new explicit operation.",
            ),
        )
    return session.result("succeeded", _data(session, source.id, applied=True))


def _result(
    session: WriteSession,
    scope_id: str,
    status: ResultStatus,
    effect: EffectStatus,
    edge: str,
    *,
    can_apply: bool = False,
) -> OperationResult[object]:
    data = _data(session, scope_id, applied=False)
    if can_apply:
        data = FamilyData("dependency", {**data.result, "can_apply": True})
    return session.result(status, data, effects=(Effect("dependency-edge", effect, edge),))


def _data(session: WriteSession, scope_id: str, *, applied: bool) -> FamilyData:
    listing = dependency_listing(session.scopes.views, _raw_edges(session.scopes), scope_id)
    return FamilyData(
        "dependency",
        {
            "scope_id": scope_id,
            "declared": tuple(edge.target_id for edge in listing.declared),
            "effective": tuple(edge.target_id for edge in listing.effective),
            "ready": None,
            "blockers": (),
            "changed": applied,
            "snapshot": session.scopes.snapshot_payload(),
        },
    )
