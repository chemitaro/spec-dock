"""`canonical resume`: restart a paused catalog after the user decided how to treat the remote (Epic ch. 5).

--adopt-remote (remote_rewritten, merge_failed) takes GitHub's canonical as the new baseline and leaves a
one-time mark: the next cycle re-adopts the local content as one commit whose only parent is GitHub's,
so history GitHub dropped is never pushed back (judgment R2). --push-local (remote_deleted) recreates
GitHub's branch from the local canonical without force. When another PC already recreated it, a
remote_deleted catalog resumes with --adopt-remote instead; while a re-adoption is still pending, --push-local is
refused (the local HEAD still holds the dropped history). The network runs under this catalog's cycle lock
(so no cycle runs meanwhile) and never under the catalog lock.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from spec_dock.runtime.application.canonical_catalog import require_linked
from spec_dock.runtime.application.canonical_errors import (
    CANONICAL_LOCK_BUSY,
    CANONICAL_PAUSED,
    CANONICAL_STATE_UNREADABLE,
    GITHUB_UNAVAILABLE_RECOVERY,
    LOCK_BUSY_RECOVERY,
    STATE_UNREADABLE_NEXT_STEP,
    CanonicalCommandError,
)
from spec_dock.runtime.domain.canonical_layout import CANONICAL_TRACKING_REF
from spec_dock.runtime.infra import canonical_git, runtime_environment
from spec_dock.runtime.infra.canonical_state import (
    CycleBusy,
    StateUnreadable,
    cycle_lock,
    read_catalog_state,
    update_catalog_state,
)
from spec_dock.runtime.infra.git_process import GitProcessError
from spec_dock.runtime.infra.github_structure import GITHUB_UNAVAILABLE
from spec_dock.runtime.infra.state_root import resolve_state_root
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Effect, OperationResult

if TYPE_CHECKING:
    import argparse
    from pathlib import Path

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.domain.canonical_sync_state import CatalogSyncState

_OPTION = {"remote_rewritten": "--adopt-remote", "merge_failed": "--adopt-remote", "remote_deleted": "--push-local"}


def _paused(reason: str, step: str) -> CanonicalCommandError:
    return CanonicalCommandError(
        CANONICAL_PAUSED,
        f"this catalog is paused ({reason}); resume it with spec-dock canonical resume {step}",
        recovery=(f"Check spec-dock canonical status, then run spec-dock canonical resume {step}.",),
        details={"paused": reason, "next_step": f"spec-dock canonical resume {step}"},
    )


def _re_adoption_pending(reason: str) -> CanonicalCommandError:
    """The local HEAD still holds the history GitHub dropped; recreating the branch from it would bring it back."""
    return CanonicalCommandError(
        CANONICAL_PAUSED,
        f"this catalog is paused ({reason}) in the middle of re-adopting GitHub's history; "
        "--push-local would push back the history GitHub dropped",
        recovery=(
            "Check spec-dock/canonical on GitHub from another PC; once it is back, run spec-dock canonical resume "
            "--adopt-remote. Ask the user before recreating it from this PC.",
        ),
        details={
            "paused": reason,
            "adopt_remote_pending": True,
            "next_step": "spec-dock canonical resume --adopt-remote",
        },
    )


def run_canonical_resume(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    environment = runtime_environment.detect_runtime_environment()
    linked = require_linked(context, environment=environment, timeout=namespace.timeout)
    catalog, root = linked.catalog, resolve_state_root()
    git = environment.git.path or "git"
    try:
        with cycle_lock(root, str(catalog), timeout=10.0):
            return _resume(namespace, catalog, root, git)
    except CycleBusy as error:
        raise CanonicalCommandError(CANONICAL_LOCK_BUSY, str(error), recovery=(LOCK_BUSY_RECOVERY,)) from error
    except StateUnreadable as error:
        raise CanonicalCommandError(
            CANONICAL_STATE_UNREADABLE, str(error), recovery=(STATE_UNREADABLE_NEXT_STEP,)
        ) from error


def _resume(namespace: argparse.Namespace, catalog: Path, root: Path, git: str) -> OperationResult[object]:
    state = read_catalog_state(root, str(catalog))
    reason = state.paused if state is not None else None
    data: dict[str, object] = {"catalog": str(catalog), "paused_before": reason, "baseline": None, "pushed": False}
    if state is None or reason is None:
        return OperationResult(namespace.command_path, "unchanged", FamilyData("canonical-resume", data), 0)
    given = "--adopt-remote" if namespace.adopt_remote else ("--push-local" if namespace.push_local else None)
    if given is None:
        raise _paused(reason, _OPTION[reason])
    try:
        presence = canonical_git.remote_canonical(catalog, git=git)
        if presence == "present":
            canonical_git.fetch_canonical(catalog, git=git)
    except GitProcessError as error:
        raise CanonicalCommandError(
            GITHUB_UNAVAILABLE,
            error.stderr.decode("utf-8", errors="replace").strip() or "origin could not be reached",
            exit_code=5,
            recovery=(GITHUB_UNAVAILABLE_RECOVERY,),
        ) from error
    # What GitHub holds now decides, whatever the pause reason was: a remote_deleted branch another PC recreated
    # is adopted like a rewrite, and a rewritten branch that was deleted afterwards is recreated.
    wanted = "--adopt-remote" if presence == "present" else "--push-local"
    if given != wanted:
        raise _paused(reason, wanted)
    if wanted == "--push-local" and state.adopt_remote_pending:
        raise _re_adoption_pending(reason)
    effects: list[Effect] = []
    if wanted == "--adopt-remote":
        remote = canonical_git.resolve_commit(catalog, CANONICAL_TRACKING_REF, git=git)
        assert remote is not None

        def adopt(current: CatalogSyncState | None) -> CatalogSyncState:
            assert current is not None
            return current.evolve(paused=None, last_seen_remote=remote, adopt_remote_pending=True, last_error=None)

        update_catalog_state(root, str(catalog), adopt)
        data["baseline"] = remote
    else:
        pushed = canonical_git.push_canonical(catalog, git=git)
        if pushed.outcome not in ("pushed", "up_to_date"):
            raise CanonicalCommandError(
                GITHUB_UNAVAILABLE,
                pushed.message or f"git push {pushed.outcome}",
                exit_code=5,
                recovery=(GITHUB_UNAVAILABLE_RECOVERY,),
            )
        head = canonical_git.resolve_commit(catalog, "HEAD", git=git)
        effects.append(Effect("canonical.push", "succeeded", str(head)))

        def recreate(current: CatalogSyncState | None) -> CatalogSyncState:
            assert current is not None
            return current.evolve(paused=None, last_seen_remote=head, remote_contains_head=True, last_error=None)

        update_catalog_state(root, str(catalog), recreate)
        data.update(baseline=head, pushed=True)
    effects.append(Effect("canonical.state", "succeeded", str(catalog)))
    return OperationResult(
        namespace.command_path, "succeeded", FamilyData("canonical-resume", data), 0, effects=tuple(effects)
    )
