"""Align human navigation links with a selection outcome; links never decide a selection."""

from __future__ import annotations

from typing import TYPE_CHECKING

from spec_dock.runtime.application.worktree_observation import ancestors_for
from spec_dock.runtime.domain.active_links import ROLES, plan_links
from spec_dock.runtime.infra.active_links import LEGACY_GENERATED, sync_active_links
from spec_dock.runtime.infra.git_process import GitProcessError, run_git
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect

if TYPE_CHECKING:
    from pathlib import Path

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.scope_query import ScopeView


def sync_selection_links(
    context: ProjectContext,
    views: tuple[ScopeView, ...],
    scope_id: str | None,
    *,
    dry_run: bool,
    timeout: float,
) -> tuple[tuple[Effect, ...], tuple[Diagnostic, ...]]:
    """Return link effects and warnings; failures never change the selection result."""
    specdock_dir = context.root / "spec-dock"
    try:
        chain = _chain(specdock_dir.resolve(strict=True), views, scope_id)
    except (OSError, ValueError):
        return (), tuple(_link_warning(role, "selection_unresolved") for role in ROLES)
    if not _ignored(context, timeout=timeout):
        return (), tuple(_link_warning(role, "not_ignored") for role in ROLES)
    links, legacy = sync_active_links(specdock_dir, plan_links(chain), dry_run=dry_run)
    effects: list[Effect] = []
    warnings: list[Diagnostic] = []
    for outcome in links:
        if outcome.status == "skipped":
            warnings.append(_link_warning(outcome.role, outcome.reason))
        elif not (dry_run and outcome.status == "unchanged"):
            effects.append(Effect("active.link", outcome.status, outcome.role))
    for removal in legacy:
        if removal.status == "skipped":
            warnings.append(
                Diagnostic(
                    "ACTIVE_LEGACY_NOT_REMOVED",
                    f"{removal.name}: {removal.reason}",
                    {"name": removal.name, "reason": removal.reason},
                )
            )
        else:
            effects.append(Effect("active.legacy.remove", removal.status, removal.name))
    return tuple(effects), tuple(warnings)


def _chain(specdock_dir: Path, views: tuple[ScopeView, ...], scope_id: str | None) -> tuple[tuple[str, str], ...]:
    if scope_id is None:
        return ()
    matches = [view for view in views if view.id == scope_id]
    if len(matches) != 1:
        raise ValueError("selected Scope is not uniquely present")
    return tuple(
        (view.kind, view.path.relative_to(specdock_dir).as_posix())
        for view in (*ancestors_for(views, matches[0]), matches[0])
    )


def _ignored(context: ProjectContext, *, timeout: float) -> bool:
    paths = tuple(f"spec-dock/active/{name}" for name in (*ROLES, *LEGACY_GENERATED))
    try:
        output = run_git(context.root, "check-ignore", "--no-index", "--", *paths, timeout=timeout, missing_ok=True)
    except (GitProcessError, OSError):
        return False
    return set(output.splitlines()) == {path.encode() for path in paths}


def _link_warning(role: str, reason: str | None) -> Diagnostic:
    return Diagnostic("ACTIVE_LINK_NOT_UPDATED", f"{role}: {reason}", {"role": role, "reason": reason})
