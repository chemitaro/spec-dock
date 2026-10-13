"""Align human navigation links with a selection outcome; links never decide a selection."""

from __future__ import annotations

from typing import TYPE_CHECKING

from spec_dock.runtime.application.worktree_observation import ancestors_for
from spec_dock.runtime.domain.active_links import ROLES, plan_links
from spec_dock.runtime.infra.active_links import LEGACY_GENERATED, LegacyOutcome, LinkOutcome, sync_active_links
from spec_dock.runtime.infra.git_process import GitProcessError, run_git
from spec_dock.runtime.infra.start_lock import StartLock, StartLockBusy
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
    """Return link effects and warnings; failures never change the selection result.

    Inspection runs without a lock. Writes run only while the clone's Start lock is held, so no
    Start can check out files into spec-dock/active between the re-inspection and a change. The
    lock is tried without waiting, and only when something must change: a busy lock skips the
    derived links instead of delaying a selection command.
    """
    planned = _sync(context, views, scope_id, dry_run=True, timeout=timeout)
    if dry_run or isinstance(planned, str) or not _writes(planned):
        return _report(planned, dry_run=dry_run)
    try:
        with StartLock(context.common_dir, timeout=0):
            return _report(_sync(context, views, scope_id, dry_run=False, timeout=timeout), dry_run=False)
    except StartLockBusy:
        return (), tuple(_link_warning(role, "start_in_progress") for role in ROLES)
    except (OSError, RuntimeError, ValueError, NotImplementedError) as error:
        return (), tuple(_link_warning(role, f"start_lock_unavailable: {type(error).__name__}") for role in ROLES)


_Outcomes = tuple[tuple[LinkOutcome, ...], tuple[LegacyOutcome, ...]]


def _sync(
    context: ProjectContext,
    views: tuple[ScopeView, ...],
    scope_id: str | None,
    *,
    dry_run: bool,
    timeout: float,
) -> _Outcomes | str:
    """Return outcomes, or a reason that applies to every role."""
    specdock_dir = context.root / "spec-dock"
    try:
        chain = _chain(specdock_dir.resolve(strict=True), views, scope_id)
    except (OSError, ValueError):
        return "selection_unresolved"
    unsafe = _git_unsafe_reason(context, timeout=timeout)
    if unsafe is not None:
        return unsafe
    try:
        return sync_active_links(specdock_dir, plan_links(chain), dry_run=dry_run)
    except OSError as error:
        return f"{type(error).__name__}: {error.strerror or error}"


def _writes(outcomes: _Outcomes) -> bool:
    links, legacy = outcomes
    return any(item.status == "planned" for item in links) or any(item.status == "planned" for item in legacy)


def _report(outcomes: _Outcomes | str, *, dry_run: bool) -> tuple[tuple[Effect, ...], tuple[Diagnostic, ...]]:
    if isinstance(outcomes, str):
        return (), tuple(_link_warning(role, outcomes) for role in ROLES)
    links, legacy = outcomes
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


def _git_unsafe_reason(context: ProjectContext, *, timeout: float) -> str | None:
    """Only untracked, ignored derived names may be written so links never dirty the worktree."""
    paths = tuple(f"spec-dock/active/{name}" for name in (*ROLES, *LEGACY_GENERATED))
    try:
        if run_git(context.root, "ls-files", "-z", "--", "spec-dock/active", timeout=timeout):
            return "tracked"
        output = run_git(context.root, "check-ignore", "--no-index", "--", *paths, timeout=timeout, missing_ok=True)
    except (GitProcessError, OSError):
        return "not_ignored"
    return None if set(output.splitlines()) == {path.encode() for path in paths} else "not_ignored"


def _link_warning(role: str, reason: str | None) -> Diagnostic:
    return Diagnostic("ACTIVE_LINK_NOT_UPDATED", f"{role}: {reason}", {"role": role, "reason": reason})
