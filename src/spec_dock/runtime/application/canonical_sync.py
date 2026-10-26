"""`spec-dock canonical sync`: save, merge and push each catalog once, then refresh the structure (Epic ch. 5).

One catalog's cycle (sync_catalog) runs steps 1-6 under its cycle lock: preconditions, the remote check and
rewrite detection (outside the catalog lock), saving and merging (inside it), the push (outside it) and the
state record. run_cycle runs every catalog without letting one failure stop the others, then step 7
(refresh_structures) once per repository. Nothing here forces a push, rebases or leaves conflict markers.
"""

from __future__ import annotations

from contextlib import contextmanager, suppress
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
from typing import TYPE_CHECKING, Final, Literal

from spec_dock.runtime.application.canonical_errors import (
    ADOPT_HELD_NEXT_STEP,
    CANONICAL_FORMAT_UNSUPPORTED,
    CANONICAL_GIT_IN_PROGRESS,
    CANONICAL_GIT_TOO_OLD,
    CANONICAL_NOT_LINKED,
    CANONICAL_NOT_LINKED_RECOVERY,
    CANONICAL_PUSH_AUTH_FAILED,
    CANONICAL_REGISTRY_UNREADABLE,
    CANONICAL_SAVE_HELD,
    CANONICAL_STATE_UNREADABLE,
    CANONICAL_SYNC_BLOCKED,
    FORMAT_MISSING_RECOVERY,
    FORMAT_UNSUPPORTED_RECOVERY,
    GIT_IN_PROGRESS_NEXT_STEP,
    GIT_TOO_OLD_RECOVERY,
    GITHUB_UNAVAILABLE_RECOVERY,
    OS_ACCESS_DENIED,
    PRIVACY_NEXT_STEP,
    PUSH_AUTH_HTTPS_NEXT_STEP,
    PUSH_AUTH_SSH_NEXT_STEP,
    REGISTRY_UNREADABLE_RECOVERY,
    STATE_UNREADABLE_NEXT_STEP,
    SYNC_BLOCKED_NEXT_STEP,
    canonical_failure,
)
from spec_dock.runtime.domain.canonical_changeset import Changeset
from spec_dock.runtime.domain.canonical_content import FORMAT_FILE, format_writable, read_format
from spec_dock.runtime.domain.canonical_layout import (
    CANONICAL_BRANCH,
    CANONICAL_TRACKING_REF,
    git_supported,
    parse_git_version,
)
from spec_dock.runtime.domain.canonical_structure import format_timestamp
from spec_dock.runtime.domain.canonical_sync_rules import (
    MAX_FILE_BYTES,
    CatalogChange,
    HoldCandidate,
    classify_holds,
    pc_name,
    resolve_conflicts,
    select_paths,
)
from spec_dock.runtime.domain.canonical_sync_state import (
    AcceptedChanges,
    Blocking,
    CatalogSyncState,
    ConflictCopy,
    CycleOutcome,
    Hold,
    LastCycle,
    PauseReason,
    PushAuth,
    RegistryEntry,
    SyncError,
)
from spec_dock.runtime.infra import canonical_git
from spec_dock.runtime.infra.canonical_registry import RegistryUnreadable, read_registry
from spec_dock.runtime.infra.canonical_state import (
    CycleBusy,
    StateUnreadable,
    append_log,
    cycle_lock,
    read_accepted,
    read_catalog_state,
    update_catalog_state,
    write_accepted,
)
from spec_dock.runtime.infra.catalog_lock import CatalogLock, CatalogLockBusy
from spec_dock.runtime.infra.catalog_runtime import CHANGESETS_RELATIVE
from spec_dock.runtime.infra.git_cli import sanitized_git_environment
from spec_dock.runtime.infra.git_process import GitProcessError
from spec_dock.runtime.infra.github_structure import (
    GITHUB_UNAVAILABLE,
    SYSTEM_CLOCK,
    GithubApi,
    GithubRepository,
    GithubStructureError,
)
from spec_dock.runtime.infra.state_root import resolve_state_root
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Effect, OperationResult

if TYPE_CHECKING:
    import argparse
    from collections.abc import Callable, Iterable, Iterator, Sequence
    from datetime import datetime

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.infra.github_structure import GithubClock

PUSH_ATTEMPTS: Final = 3  # the first push and at most two retries after a rejection (Epic ch. 5 step 5)
ProbeLabel = Literal["unchanged", "changed", "failed"]

# Injection points for tests: the clock (now, sleep, monotonic) and the host name.
SYNC_CLOCK: GithubClock = SYSTEM_CLOCK


def hostname() -> str:
    return socket.gethostname()


@dataclass(frozen=True)
class SyncContext:
    state_root: Path
    clock: GithubClock = field(default_factory=lambda: SYNC_CLOCK)
    pc: str = field(default_factory=lambda: pc_name(hostname()))
    github_api: Callable[[Path], GithubApi] = field(default=lambda cwd: GithubApi(cwd=cwd))

    def now(self) -> datetime:
        return self.clock.now()

    def stamp(self) -> str:
        return format_timestamp(self.clock.now())


@dataclass
class CatalogResult:
    catalog: str
    result: CycleOutcome = "ok"
    saved_commit: str | None = None
    merged: bool = False
    pushed: bool = False
    conflicts: list[ConflictCopy] = field(default_factory=list)
    holds: list[Hold] = field(default_factory=list)
    blocking: list[Blocking] = field(default_factory=list)
    skipped_reason: str | None = None
    paused: PauseReason | None = None
    error: SyncError | None = None
    effects: list[Effect] = field(default_factory=list)

    def to_json(self) -> dict[str, object]:
        return {
            "catalog": self.catalog,
            "result": self.result,
            "saved_commit": self.saved_commit,
            "merged": self.merged,
            "pushed": self.pushed,
            "conflicts": [item.to_json() for item in self.conflicts],
            "holds": [item.to_json() for item in self.holds],
            "blocking": [item.to_json() for item in self.blocking],
            "skipped_reason": self.skipped_reason,
            "paused": self.paused,
            "error": self.error.to_json() if self.error else None,
        }


@dataclass(frozen=True)
class RepositoryResult:
    """Step 7 for one repository; iss-00438 adds the dashboards it wrote."""

    repository: str
    probe: ProbeLabel
    refreshed: bool
    dashboards_written: int = 0

    def to_json(self) -> dict[str, object]:
        return {
            "repository": self.repository,
            "probe": self.probe,
            "refreshed": self.refreshed,
            "dashboards_written": self.dashboards_written,
        }


@dataclass(frozen=True)
class CycleResult:
    catalogs: tuple[CatalogResult, ...]
    repositories: tuple[RepositoryResult, ...]


class _Stop(Exception):
    """End this catalog's cycle with the result already recorded on the run."""


@dataclass
class _Run:
    entry: RegistryEntry
    ctx: SyncContext
    state: CatalogSyncState
    result: CatalogResult
    started: str
    catalog: Path
    remote: str | None = None
    offline: bool = False
    baseline: str | None = None
    changes: tuple[CatalogChange, ...] = ()
    held: dict[str, str] = field(default_factory=dict)

    @property
    def git(self) -> str:
        return self.entry.git

    def fail(self, code: str, message: str, next_step: str | None, **extra: object) -> None:
        program = extra.get("program")
        self.result.result = "error"
        self.result.error = SyncError(
            code, message, next_step, tuple(program) if isinstance(program, (list, tuple)) else None, self.ctx.stamp()
        )

    def pause(self, reason: PauseReason, message: str) -> None:
        self.result.result = "paused"
        self.result.paused = reason
        self.result.error = SyncError(reason, message, None, None, self.ctx.stamp())


def sync_catalog(entry: RegistryEntry, ctx: SyncContext) -> CatalogResult:
    """One catalog's cycle (Epic ch. 5 steps 1-6); a second concurrent cycle of it is skipped (judgment Q4)."""
    try:
        with cycle_lock(ctx.state_root, entry.catalog):
            return _cycle(entry, ctx)
    except CycleBusy:
        return CatalogResult(entry.catalog, "skipped", skipped_reason="cycle_busy")


def _cycle(entry: RegistryEntry, ctx: SyncContext) -> CatalogResult:
    started = ctx.stamp()
    result = CatalogResult(entry.catalog)
    try:
        state = read_catalog_state(ctx.state_root, entry.catalog) or CatalogSyncState.new(entry.catalog, at=started)
    except StateUnreadable as error:
        # Never overwrite a state file this SpecDock cannot read: its baseline guards against rewrites.
        result.result = "error"
        result.error = SyncError(CANONICAL_STATE_UNREADABLE, str(error), STATE_UNREADABLE_NEXT_STEP, None, started)
        _log(ctx, result)
        return result
    run = _Run(entry, ctx, state, result, started, Path(entry.catalog), baseline=state.last_seen_remote)
    try:
        if state.paused is not None:
            result.result = "paused"
            result.paused = state.paused
            raise _Stop
        _preconditions(run)
        for attempt in range(PUSH_ATTEMPTS):
            _check_remote(run)
            if not _save_and_merge(run, first=attempt == 0):
                break
            if run.offline or run.result.result == "paused" or not _push(run, last=attempt == PUSH_ATTEMPTS - 1):
                break
        _check_push_auth(run)
    except _Stop:
        pass
    except GitProcessError as error:
        _git_error(run, error)
    except OSError as error:
        _os_error(run, error)
    _record(run)
    _log(ctx, result)
    return result


def _program(run: _Run) -> list[str]:
    return [os.path.realpath(sys.executable), run.git]


def _preconditions(run: _Run) -> None:
    """Step 1: the catalog exists, is readable, is on spec-dock/canonical, is not mid-operation, has a writable
    format, and the registered git is 2.38 or later. A failure skips this catalog with the reason recorded."""
    catalog = run.catalog
    try:
        next(catalog.iterdir(), None)
    except FileNotFoundError:
        run.fail(
            CANONICAL_NOT_LINKED,
            f"the catalog {catalog} is not there (a detached volume, or git clean)",
            CANONICAL_NOT_LINKED_RECOVERY,
        )
        raise _Stop from None
    except PermissionError as error:
        run.fail(OS_ACCESS_DENIED, f"cannot read {catalog}: {error.strerror}", PRIVACY_NEXT_STEP, program=_program(run))
        raise _Stop from None
    version = _git_version(run.git)
    if not git_supported(version):
        run.fail(CANONICAL_GIT_TOO_OLD, f"{run.git} is not Git 2.38 or later", GIT_TOO_OLD_RECOVERY)
        raise _Stop
    gitdir = canonical_git.read_gitdir(catalog)
    branch = canonical_git.admin_branch(gitdir) if gitdir is not None else None
    if gitdir is None or branch != CANONICAL_BRANCH:
        run.fail(
            CANONICAL_NOT_LINKED,
            f"{catalog} is not a worktree of {CANONICAL_BRANCH} (found {branch or 'no branch'})",
            CANONICAL_NOT_LINKED_RECOVERY,
        )
        raise _Stop
    operation = canonical_git.operation_in_progress(gitdir)
    if operation is not None:
        run.fail(
            CANONICAL_GIT_IN_PROGRESS,
            f"{catalog} has an unfinished Git operation ({operation})",
            GIT_IN_PROGRESS_NEXT_STEP,
        )
        raise _Stop
    try:
        declared = read_format((catalog / FORMAT_FILE).read_bytes())
    except FileNotFoundError:
        declared = None
    if not format_writable(declared):
        step = FORMAT_MISSING_RECOVERY if declared is None else FORMAT_UNSUPPORTED_RECOVERY
        run.fail(CANONICAL_FORMAT_UNSUPPORTED, f"the catalog declares canonical format {declared!r}", step)
        raise _Stop


def _git_version(git: str) -> tuple[int, int, int] | None:
    from spec_dock.runtime.infra.runtime_environment import probe_git

    return probe_git(git).version if Path(git).is_absolute() else _path_git_version(git)


def _path_git_version(git: str) -> tuple[int, int, int] | None:
    try:
        completed = subprocess.run(
            [git, "--version"], capture_output=True, check=False, env=sanitized_git_environment(), timeout=10
        )
    except (OSError, subprocess.SubprocessError):
        return None
    lines = completed.stdout.decode("utf-8", errors="replace").splitlines()
    return parse_git_version(lines[0]) if completed.returncode == 0 and lines else None


def _check_remote(run: _Run) -> None:
    """Step 2 (no lock): ls-remote, fetch, and rewrite or deletion detection against the baseline (R-C5)."""
    catalog, git = run.catalog, run.git
    try:
        presence = canonical_git.remote_canonical(catalog, git=git)
        if presence == "present":
            canonical_git.fetch_canonical(catalog, git=git)
    except GitProcessError as error:
        run.offline = True
        run.remote = canonical_git.resolve_commit(catalog, CANONICAL_TRACKING_REF, git=git)
        message = error.stderr.decode("utf-8", errors="replace").strip() or "origin could not be reached"
        run.fail(GITHUB_UNAVAILABLE, message, GITHUB_UNAVAILABLE_RECOVERY)
        return
    if presence == "absent":
        if run.baseline is not None:
            run.pause(
                "remote_deleted", f"GitHub no longer has {CANONICAL_BRANCH}; the last confirmed was {run.baseline}"
            )
            raise _Stop
        head = canonical_git.resolve_commit(catalog, "HEAD", git=git)
        if head is not None and not canonical_git.is_initial_commit(catalog, head):
            # Never recreate a canonical that GitHub lost while this clone has content (I-2 judgment A4).
            run.pause("remote_deleted", f"GitHub has no {CANONICAL_BRANCH} and this catalog holds content")
            raise _Stop
        run.remote = None  # a new repository whose first push has not happened yet
        return
    remote = canonical_git.resolve_commit(catalog, CANONICAL_TRACKING_REF, git=git)
    if remote is None:
        run.fail(GITHUB_UNAVAILABLE, f"fetching {CANONICAL_BRANCH} gave no commit", GITHUB_UNAVAILABLE_RECOVERY)
        run.offline = True
        return
    if run.baseline is not None and run.baseline != remote:
        try:
            descends = canonical_git.is_ancestor(catalog, run.baseline, remote, git=git)
        except GitProcessError:
            descends = False  # the baseline commit is unknown here; never take what cannot be checked
        if not descends:
            run.pause(
                "remote_rewritten",
                f"GitHub {CANONICAL_BRANCH} ({remote}) does not descend from the last confirmed {run.baseline}",
            )
            raise _Stop
    run.remote = remote
    run.baseline = remote


def _save_and_merge(run: _Run, *, first: bool) -> bool:
    """Steps 3 and 4 under the catalog lock; False when the lock is busy (a first attempt skips the catalog)."""
    try:
        with CatalogLock(run.catalog, timeout=0):
            _save(run)
            _merge(run)
    except CatalogLockBusy:
        if first and run.result.result == "ok":
            run.result.result = "skipped"
            run.result.skipped_reason = "lock_busy"
        return False
    return True


def _read_changesets(catalog: Path, consumed: Sequence[str]) -> list[tuple[str, Changeset]]:
    directory = catalog / CHANGESETS_RELATIVE
    try:
        names = sorted(entry.name for entry in os.scandir(directory) if entry.name.endswith(".json"))
    except FileNotFoundError:
        return []
    changesets = []
    for name in names:
        if name.startswith(".") or name in consumed:
            continue
        try:
            changesets.append((name, Changeset.from_json(json.loads((directory / name).read_text(encoding="utf-8")))))
        except (OSError, ValueError):
            continue  # left in place; its paths fall back to the 30-second rule
    return changesets


def _covers(prefixes: Iterable[str], path: str) -> bool:
    return any(path == prefix or path.startswith(prefix + "/") for prefix in prefixes)


def _candidate(run: _Run, change: CatalogChange, accepted: dict[str, str]) -> HoldCandidate:
    target = run.catalog / change.path
    observed = target.lstat()
    blob = canonical_git.blob_of(run.catalog, change.path, git=run.git) if change.path in accepted else ""
    content = None
    if not target.is_symlink() and observed.st_size <= MAX_FILE_BYTES:
        content = target.read_bytes()
    return HoldCandidate(change.path, observed.st_size, blob, content)


def _save(run: _Run) -> None:
    """Step 3: changesets at once (one commit each), other paths after 30 s or 5 min, holds excluded."""
    catalog, git, now = run.catalog, run.git, run.ctx.now()
    canonical_git.reset_index(catalog, git=git)
    changes = canonical_git.list_changes(catalog, git=git)
    changesets = _read_changesets(catalog, run.state.consumed_changesets)
    try:
        accepted = read_accepted(catalog)
    except StateUnreadable:
        accepted = None
    accepted_paths = dict(accepted.paths) if accepted else {}
    accepted_deletions = tuple(accepted.deletions) if accepted else ()
    claimed: dict[str, list[CatalogChange]] = {}
    taken: set[str] = set()
    command_scope: list[str] = []
    for name, changeset in changesets:
        scope = (*changeset.paths, *changeset.deletions)
        if changeset.origin == "command":
            command_scope.extend(scope)
        mine = [change for change in changes if change.path not in taken and _covers(scope, change.path)]
        taken.update(change.path for change in mine)
        claimed[name] = mine
    remaining = [change for change in changes if change.path not in taken]
    selection = select_paths(remaining, pending_since=run.state.pending_since, now=now)
    to_save = {change.path for change in changes if change.path in taken} | set(selection.selected)
    kinds = {change.path: change for change in changes}
    candidates = [
        _candidate(run, kinds[path], accepted_paths) for path in sorted(to_save) if kinds[path].kind != "deleted"
    ]
    deletions = [
        change.path for change in changes if change.kind == "deleted" and not _covers(command_scope, change.path)
    ]
    held = classify_holds(
        candidates,
        deletions=deletions,
        tracked_count=canonical_git.tracked_count(catalog, git=git),
        accepted_paths=accepted_paths,
        accepted_deletions=accepted_deletions,
    )
    run.held = dict(held)
    head = canonical_git.resolve_commit(catalog, "HEAD", git=git)
    assert head is not None
    saved: set[str] = set()
    batches = [(name, [change.path for change in mine if change.path not in held]) for name, mine in claimed.items()]
    batches.append(("", sorted(path for path in selection.selected if path not in held)))
    consumed = list(run.state.consumed_changesets)
    for name, paths in batches:
        if paths:
            head = canonical_git.save_commit(
                catalog, paths, message=f"spec-dock: save {len(paths)} files ({run.ctx.pc})", parent=head, git=git
            )
            run.result.saved_commit = head
            run.result.effects.append(Effect("canonical.save", "succeeded", head))
            saved.update(paths)
        if name:
            consumed.append(name)
            (catalog / CHANGESETS_RELATIVE / name).unlink(missing_ok=True)
    pending = {path: since for path, since in selection.pending_since.items() if path not in saved}
    previous = {(hold.path, hold.kind): hold.since for hold in run.state.holds}
    stamp = format_timestamp(now)
    holds = tuple(Hold(path, kind, previous.get((path, kind), stamp)) for path, kind in sorted(held.items()))
    run.result.holds = list(holds)
    run.state = run.state.evolve(pending_since=pending, holds=holds, consumed_changesets=tuple(consumed))
    if accepted is not None and saved & (set(accepted_paths) | set(accepted_deletions)):
        write_accepted(
            catalog,
            AcceptedChanges(
                {path: blob for path, blob in accepted_paths.items() if path not in saved},
                tuple(path for path in accepted_deletions if path not in saved),
            ),
        )


def _overlaps(changed: Iterable[str], local: Iterable[str]) -> list[str]:
    local_paths = sorted(set(local))
    hits = set()
    for path in changed:
        for edited in local_paths:
            if path == edited or path.startswith(edited + "/") or edited.startswith(path + "/"):
                hits.add(edited)
    return sorted(hits)


def _merge(run: _Run) -> None:
    """Step 4: fast-forward, or merge-tree with the stage rules; never over an unsaved or held file.

    After resume --adopt-remote the merged content becomes one commit whose only parent is R, so history
    that GitHub dropped is never pushed back (judgment R2).
    """
    catalog, git, remote = run.catalog, run.git, run.remote
    local = canonical_git.resolve_commit(catalog, "HEAD", git=git)
    assert local is not None
    adopt = run.state.adopt_remote_pending
    run.state = run.state.evolve(blocking=())
    if remote is None or remote == local:
        if remote is not None and adopt:
            run.state = run.state.evolve(adopt_remote_pending=False)
        return
    copies: tuple[tuple[str, str], ...] = ()
    if canonical_git.is_ancestor(catalog, local, remote, git=git):
        target, mode = remote, "fast-forward"
    elif not adopt and canonical_git.is_ancestor(catalog, remote, local, git=git):
        return  # already ahead of GitHub; the push sends it
    else:
        tree, copies = _merged_tree(run, local, remote, unrelated=adopt)
        if adopt:
            if _adopt_holds(run, remote, tree):
                raise _Stop
            target = canonical_git.commit_on(
                catalog, tree, remote, message=f"spec-dock: adopt remote ({run.ctx.pc})", git=git
            )
            mode = "reset"
        else:
            message = f"spec-dock: merge ({run.ctx.pc})"
            target, mode = (
                canonical_git.commit_merge(catalog, tree, local, remote, message=message, git=git),
                "fast-forward",
            )
    edited = {change.path for change in canonical_git.list_changes(catalog, git=git)}
    blocked = _overlaps(canonical_git.changed_paths(catalog, local, target, git=git), edited)
    if blocked:
        run.state = run.state.evolve(
            blocking=tuple(Blocking(path, "held" if path in run.held else "local_edit") for path in blocked)
        )
        run.result.blocking = list(run.state.blocking)
        return
    try:
        if mode == "reset":
            canonical_git.reset_keep(catalog, target, git=git)
        else:
            canonical_git.fast_forward(catalog, target, git=git)
    except GitProcessError as error:
        message = error.stderr.decode("utf-8", errors="replace").strip()
        run.fail(CANONICAL_SYNC_BLOCKED, message or "the merge would overwrite local files", SYNC_BLOCKED_NEXT_STEP)
        return
    run.result.merged = True
    run.result.effects.append(Effect("canonical.merge", "succeeded", target))
    stamp = run.ctx.stamp()
    added = tuple(ConflictCopy(path, copy, stamp) for path, copy in copies)
    run.result.conflicts = list(added)
    run.state = run.state.evolve(conflicts=(*run.state.conflicts, *added), adopt_remote_pending=False)


def _merged_tree(run: _Run, local: str, remote: str, *, unrelated: bool) -> tuple[str, tuple[tuple[str, str], ...]]:
    """merge-tree L R resolved by stage; anything the stage rules cannot express pauses as merge_failed."""
    catalog, git = run.catalog, run.git
    merged = canonical_git.merge_tree(catalog, local, remote, allow_unrelated=unrelated, git=git)
    if merged.tree is None:
        run.pause("merge_failed", merged.message or f"git merge-tree exited {merged.code}")
        raise _Stop
    tree = merged.tree
    copies: tuple[tuple[str, str], ...] = ()
    if merged.code == 1:
        work = {change.path for change in canonical_git.list_changes(catalog, git=git)}
        resolution = resolve_conflicts(
            merged.entries,
            pc=run.ctx.pc,
            now=run.ctx.now(),
            taken=canonical_git.tree_paths(catalog, tree, git=git) | work,
        )
        try:
            tree = canonical_git.write_resolution(catalog, tree, resolution, git=git)
        except GitProcessError as error:
            run.pause("merge_failed", error.stderr.decode("utf-8", errors="replace").strip() or "unresolvable conflict")
            raise _Stop from error
        copies = resolution.copies
    # A directory/file conflict makes Git invent paths such as `name~branch`; never commit those.
    known = canonical_git.tree_paths(catalog, local, git=git) | canonical_git.tree_paths(catalog, remote, git=git)
    invented = sorted(canonical_git.tree_paths(catalog, tree, git=git) - known - {pair[1] for pair in copies})
    if invented:
        run.pause("merge_failed", "the merge produced paths the stage rules cannot express: " + ", ".join(invented))
        raise _Stop
    return tree, copies


def _adopt_holds(run: _Run, remote: str, tree: str) -> bool:
    """Apply the hold rules to what re-adopting would add on top of R; on a hit stay paused (judgment R2)."""
    catalog, git = run.catalog, run.git
    before = canonical_git.tree_entries(catalog, remote, git=git)
    after = canonical_git.tree_entries(catalog, tree, git=git)
    try:
        accepted = read_accepted(catalog)
    except StateUnreadable:
        accepted = AcceptedChanges.empty()
    candidates = []
    for path, entry in sorted(after.items()):
        if before.get(path) == entry:
            continue
        size = entry.size or 0
        content = None
        if entry.mode != "120000" and size <= MAX_FILE_BYTES:
            content = canonical_git.blob_bytes(catalog, entry.oid, git=git)
        candidates.append(HoldCandidate(path, size, entry.oid, content))
    held = classify_holds(
        candidates,
        deletions=sorted(set(before) - set(after)),
        tracked_count=len(before),
        accepted_paths=dict(accepted.paths),
        accepted_deletions=tuple(accepted.deletions),
    )
    if not held:
        return False
    stamp = run.ctx.stamp()
    holds = tuple(Hold(path, kind, stamp) for path, kind in sorted(held.items()))
    run.state = run.state.evolve(holds=holds)
    run.result.holds = list(holds)
    run.result.result = "paused"
    run.result.paused = "remote_rewritten"
    run.result.error = SyncError(
        CANONICAL_SAVE_HELD,
        "re-adopting GitHub's canonical would push held content: "
        + ", ".join(f"{path} ({kind})" for path, kind in sorted(held.items())),
        ADOPT_HELD_NEXT_STEP,
        None,
        stamp,
    )
    return True


def _push(run: _Run, *, last: bool) -> bool:
    """Step 5 (no lock): push without force; True asks for another attempt after a rejection."""
    catalog, git, remote = run.catalog, run.git, run.remote
    local = canonical_git.resolve_commit(catalog, "HEAD", git=git)
    assert local is not None
    if remote is not None and (local == remote or not canonical_git.is_ancestor(catalog, remote, local, git=git)):
        return False  # nothing ahead of GitHub, or not yet merged (a blocked merge waits for the next cycle)
    pushed = canonical_git.push_canonical(catalog, git=git)
    if pushed.outcome in ("pushed", "up_to_date"):
        run.baseline = local
        run.remote = local
        run.state = run.state.evolve(push_auth=PushAuth("ok", run.ctx.stamp()))
        if pushed.outcome == "pushed":
            run.result.pushed = True
            run.result.effects.append(Effect("canonical.push", "succeeded", local))
        return False
    if pushed.outcome == "rejected":
        return not last
    if pushed.outcome == "auth_failed":
        _auth_failed(run, pushed.message)
        return False
    run.fail(GITHUB_UNAVAILABLE, pushed.message or "git push failed", GITHUB_UNAVAILABLE_RECOVERY)
    return False


def _auth_failed(run: _Run, message: str) -> None:
    step = auth_next_step(canonical_git.push_url(run.catalog, git=run.git))
    run.state = run.state.evolve(push_auth=PushAuth("failed", run.ctx.stamp(), message))
    run.fail(CANONICAL_PUSH_AUTH_FAILED, message or "git push could not authenticate", step)


def auth_next_step(url: str | None) -> str:
    if url is not None and (url.startswith("ssh://") or ("@" in url and ":" in url and "://" not in url)):
        return PUSH_AUTH_SSH_NEXT_STEP
    return PUSH_AUTH_HTTPS_NEXT_STEP


def _check_push_auth(run: _Run) -> None:
    """The first cycle after link checks authentication with a dry-run push even when nothing is sent (Q5)."""
    auth = run.state.push_auth
    if run.offline or run.result.result in ("paused", "skipped") or (auth is not None and auth.result != "unknown"):
        return
    probe = canonical_git.push_canonical(run.catalog, dry_run=True, git=run.git)
    if probe.outcome in ("pushed", "up_to_date", "rejected"):
        run.state = run.state.evolve(push_auth=PushAuth("ok", run.ctx.stamp()))
    elif probe.outcome == "auth_failed":
        _auth_failed(run, probe.message)


def _git_error(run: _Run, error: GitProcessError) -> None:
    text = error.stderr.decode("utf-8", errors="replace").strip()
    if "Operation not permitted" in text or "Permission denied" in text:
        run.fail(OS_ACCESS_DENIED, text, PRIVACY_NEXT_STEP, program=_program(run))
    else:
        run.fail("GIT_FAILED", text or str(error), "Check spec-dock canonical status and the sync log.")


def _os_error(run: _Run, error: OSError) -> None:
    if isinstance(error, PermissionError):
        run.fail(OS_ACCESS_DENIED, str(error), PRIVACY_NEXT_STEP, program=_program(run))
    else:
        run.fail("LOCAL_IO_FAILED", str(error), "Check spec-dock canonical status and the sync log.")


def _record(run: _Run) -> None:
    """Step 6: the head, the baseline, whether GitHub holds the head, and the outcome."""
    result = run.result
    if result.result == "skipped":
        return
    finished = run.ctx.stamp()
    head = None
    contains = run.state.remote_contains_head
    try:
        if Path(run.catalog).is_dir():
            head = canonical_git.resolve_commit(run.catalog, "HEAD", git=run.git)
        if head is not None and run.baseline is not None:
            contains = head == run.baseline or canonical_git.is_ancestor(run.catalog, head, run.baseline, git=run.git)
        elif head is not None:
            contains = False  # nothing confirmed on GitHub yet
    except (GitProcessError, OSError):
        head = run.state.head
    unpushed = None if contains else (run.state.unpushed_since or finished)
    paused = result.paused if result.result == "paused" else run.state.paused
    base = run.state

    def mutate(current: CatalogSyncState | None) -> CatalogSyncState:
        latest = current or base
        return base.evolve(
            updated_at=finished,
            last_cycle=LastCycle(run.started, finished, result.result),
            last_success_at=finished if result.result == "ok" else latest.last_success_at,
            last_error=None if result.result == "ok" else result.error,
            paused=paused,
            head=head or latest.head,
            last_seen_remote=run.baseline,
            remote_contains_head=contains,
            unpushed_since=unpushed,
            conflicts=tuple(item for item in base.conflicts if os.path.lexists(run.catalog / item.copy)),
            dashboard=latest.dashboard,
        )

    # When the record cannot be written the Git state is still right; the next cycle writes it again.
    with suppress(OSError, TimeoutError, StateUnreadable):
        run.state = update_catalog_state(run.ctx.state_root, run.entry.catalog, mutate)


def _log(ctx: SyncContext, result: CatalogResult) -> None:
    code = result.error.code if result.error else "-"
    line = (
        f"{ctx.stamp()} catalog={result.catalog} result={result.result} saved={result.saved_commit or '-'} "
        f"merged={result.merged} pushed={result.pushed} holds={len(result.holds)} code={code}"
    )
    with suppress(OSError, TimeoutError):
        append_log(ctx.state_root, line)


def run_cycle(
    entries: Sequence[RegistryEntry], ctx: SyncContext, *, stop: Callable[[], bool] | None = None
) -> CycleResult:
    """Every catalog in order (one failure never stops another), then step 7 once per repository.

    `stop` is checked between catalogs: a termination request ends the cycle after the current catalog.
    """
    catalogs: list[CatalogResult] = []
    for entry in entries:
        if stop is not None and stop():
            break
        try:
            catalogs.append(sync_catalog(entry, ctx))
        except Exception as error:  # a defect in one catalog's cycle must not stop the others
            failed = CatalogResult(entry.catalog, "error")
            failed.error = SyncError("SYNC_FAILED", f"{type(error).__name__}: {error}", None, None, ctx.stamp())
            catalogs.append(failed)
            _log(ctx, failed)
    return CycleResult(tuple(catalogs), tuple(refresh_structures(entries, ctx)))


def refresh_structures(entries: Sequence[RegistryEntry], ctx: SyncContext) -> list[RepositoryResult]:
    """Step 7: ensure_fresh(repository, "cycle") once per repository after every catalog, even paused ones.

    Its failures stay in probe.json and never change steps 1-6. iss-00438 adds the dashboards here.
    """
    from spec_dock.runtime.infra.github_snapshot import ensure_fresh

    results: list[RepositoryResult] = []
    seen: set[str] = set()
    for entry in entries:
        if entry.repository is None or entry.repository in seen:
            continue
        seen.add(entry.repository)
        try:
            repository = GithubRepository.parse(entry.repository)
            fresh = ensure_fresh(
                repository, "cycle", state_root=ctx.state_root, api=ctx.github_api(Path(entry.main_checkout))
            )
        except (GithubStructureError, OSError, ValueError, TimeoutError):
            results.append(RepositoryResult(entry.repository, "failed", False))
            continue
        probe: ProbeLabel = (
            "failed" if fresh.probe == "failed" else ("changed" if fresh.probe == "changed" else "unchanged")
        )
        results.append(RepositoryResult(entry.repository, probe, fresh.refreshed))
    return results


def cycle_operation_result(command: str, cycle: CycleResult) -> OperationResult[object]:
    """succeeded or unchanged when every catalog is ok or skipped; otherwise partial with effects, else failed (Q7)."""
    effects = tuple(effect for item in cycle.catalogs for effect in item.effects)
    failed = any(item.result in ("paused", "error") for item in cycle.catalogs)
    data = FamilyData(
        "canonical-sync",
        {
            "catalogs": [item.to_json() for item in cycle.catalogs],
            "repositories": [item.to_json() for item in cycle.repositories],
        },
    )
    if not failed:
        return OperationResult(command, "succeeded" if effects else "unchanged", data, 0, effects=effects)
    first = next(item.error for item in cycle.catalogs if item.result in ("paused", "error"))
    from spec_dock.runtime.presentation.envelope import Diagnostic, RecoveryInstructions

    code = first.code if first else "SYNC_FAILED"
    diagnostic = Diagnostic(code, first.message if first else "a catalog could not be synced", {})
    recovery = RecoveryInstructions(("spec-dock canonical status",))
    if effects:
        return OperationResult(command, "partial", data, 6, effects=effects, error=diagnostic, recovery=recovery)
    return OperationResult(command, "failed", data, 3, effects=effects, error=diagnostic, recovery=recovery)


def registry_unreadable_result(command: str, error: RegistryUnreadable) -> OperationResult[object]:
    return canonical_failure(
        command,
        CANONICAL_REGISTRY_UNREADABLE,
        str(error),
        3,
        (REGISTRY_UNREADABLE_RECOVERY,),
        {"path": str(error.path)},
    )


def registered_entries(state_root: Path) -> tuple[RegistryEntry, ...]:
    return read_registry(state_root).catalogs


def _state_root(namespace: argparse.Namespace) -> Path:
    override = Path(namespace.state_root) if getattr(namespace, "state_root", None) else None
    return resolve_state_root(override=override)


def run_registered_sync(namespace: argparse.Namespace, cwd: Path) -> OperationResult[object] | None:
    """`canonical sync --registered` needs no repository; plain `canonical sync` declines to the mode dispatch."""
    del cwd
    if not namespace.registered:
        return None
    command = namespace.command_path
    root = _state_root(namespace)
    if namespace.loop:
        return _loop_result(command, root, detach=namespace.detach)
    try:
        entries = read_registry(root).catalogs
    except RegistryUnreadable as error:
        return registry_unreadable_result(command, error)
    with deferred_termination() as stop:
        cycle = run_cycle(entries, SyncContext(root), stop=stop)
    return cycle_operation_result(command, cycle)


def run_cycle_once(root: Path) -> CycleResult | None:
    """One resident-runner cycle over the current registry; an unreadable registry is logged and skipped."""
    try:
        entries = read_registry(root).catalogs
    except RegistryUnreadable as error:
        with suppress(OSError, TimeoutError):
            append_log(root, f"registry unreadable: {error}")
        return None
    return run_cycle(entries, SyncContext(root))


def run_canonical_sync(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    """`canonical sync` in this checkout: this clone's catalog, registered or not (`--no-schedule`)."""
    from spec_dock.runtime.application.canonical_catalog import require_linked
    from spec_dock.runtime.infra import runtime_environment

    environment = runtime_environment.detect_runtime_environment()
    linked = require_linked(context, environment=environment, timeout=namespace.timeout)
    root = _state_root(namespace)
    catalog = str(linked.catalog)
    try:
        entry = read_registry(root).entry_for(catalog)
    except RegistryUnreadable as error:
        return registry_unreadable_result(namespace.command_path, error)
    if entry is None:
        entry = RegistryEntry(
            catalog,
            str(linked.layout.main_checkout),
            repository_of(linked.layout.main_checkout, timeout=namespace.timeout),
            environment.git.path or "git",
            format_timestamp(SYNC_CLOCK.now()),
        )
    with deferred_termination() as stop:
        cycle = run_cycle([entry], SyncContext(root), stop=stop)
    return cycle_operation_result(namespace.command_path, cycle)


def repository_of(main_checkout: Path, *, timeout: float) -> str | None:
    """`github.com/<owner>/<repo>` of the origin remote, or None when origin is not one GitHub repository."""
    from spec_dock.runtime.infra.github_structure import repository_for_checkout

    try:
        return repository_for_checkout(main_checkout, timeout=timeout).key
    except (ValueError, GitProcessError, OSError, RuntimeError):
        return None


@contextmanager
def deferred_termination() -> Iterator[Callable[[], bool]]:
    """Turn SIGTERM and SIGINT into a request to stop after the current catalog (bootout must not cut a merge)."""
    import signal
    import threading

    requested = {"stop": False}
    if threading.current_thread() is not threading.main_thread():
        yield lambda: requested["stop"]
        return

    def handler(_signum: int, _frame: object) -> None:
        requested["stop"] = True

    previous = {sig: signal.signal(sig, handler) for sig in (signal.SIGTERM, signal.SIGINT)}
    try:
        yield lambda: requested["stop"]
    finally:
        for sig, old in previous.items():
            signal.signal(sig, old)


def _loop_result(command: str, root: Path, *, detach: bool) -> OperationResult[object]:
    """`--loop` runs the resident runner here; `--detach` starts it in a new session and returns at once."""
    from spec_dock import __version__
    from spec_dock.runtime.infra import canonical_scheduler_loop, canonical_scheduling

    data = FamilyData("canonical-sync-runner", {"state_root": str(root)})
    if detach:
        if canonical_scheduler_loop.runner_running(root):
            return OperationResult(
                command, "unchanged", data, 0, effects=(Effect("canonical.runner", "unchanged", str(root)),)
            )
        try:
            executable = canonical_scheduling.spec_dock_executable()
            pid = canonical_scheduler_loop.detach(root, executable=executable)
        except canonical_scheduling.SchedulerError as error:
            from spec_dock.runtime.application.canonical_errors import (
                CANONICAL_SCHEDULER_FAILED,
                SCHEDULER_FAILED_RECOVERY,
            )

            return canonical_failure(command, CANONICAL_SCHEDULER_FAILED, str(error), 3, (SCHEDULER_FAILED_RECOVERY,))
        return OperationResult(
            command,
            "succeeded",
            FamilyData("canonical-sync-runner", {"state_root": str(root), "pid": pid}),
            0,
            effects=(Effect("canonical.runner", "succeeded", str(root)),),
        )
    outcome = canonical_scheduler_loop.run_loop(root, cycle=lambda: run_cycle_once(root), version=__version__)
    if outcome == "already_running":
        return OperationResult(command, "unchanged", data, 0)
    return OperationResult(command, "succeeded", data, 0)
