"""`spec-dock canonical link`: find or create this clone's catalog, protect it, and link checkouts (Epic ch. 3).

Steps 1-5 and 8 of the Epic design. Every stop condition is checked before anything is written; network
work (ls-remote, fetch, the initial push) runs outside the clone Start lock and local writes run inside it.
I-3 adds step 6 (registry and periodic job) and step 7 (baseline) between the links and the tool settings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from typing import TYPE_CHECKING, Literal

from spec_dock.runtime.application.canonical_catalog import (
    CatalogObservation,
    foreign_error,
    gitignore_next_step,
    observe_catalog,
    occupied_next_step,
    require_git,
    resolve_layout,
)
from spec_dock.runtime.application.canonical_errors import (
    CANONICAL_CHECKOUT_NOT_MIGRATED,
    CANONICAL_FORMAT_UNSUPPORTED,
    CANONICAL_IGNORE_RULES_MISSING,
    CANONICAL_LINK_OCCUPIED,
    CANONICAL_MAIN_MOVED,
    CANONICAL_MAIN_NOT_MIGRATED,
    CANONICAL_NOT_LINKED,
    CANONICAL_NOT_MIGRATED,
    CANONICAL_PATH_OCCUPIED,
    CANONICAL_REGISTRY_UNREADABLE,
    CANONICAL_REMOTE_MISSING,
    CANONICAL_SANDBOX_DENIED,
    CANONICAL_STATE_ROOT_MISMATCH,
    CHECKOUT_NOT_MIGRATED_NEXT_STEP,
    FORMAT_MISSING_RECOVERY,
    FORMAT_UNSUPPORTED_RECOVERY,
    GIT_IDENTITY_RECOVERY,
    LINK_AGAIN_RECOVERY,
    LINK_NETWORK_RECOVERY,
    MAIN_MOVED_NEXT_STEP,
    MAIN_NOT_MIGRATED_NEXT_STEP,
    NOT_MIGRATED_RECOVERY,
    PERMISSION_DENIED_RECOVERY,
    REGISTRY_UNREADABLE_RECOVERY,
    REMOTE_MISSING_NEXT_STEP,
    SANDBOX_DENIED_RECOVERY,
    START_LOCK_BUSY,
    START_LOCK_BUSY_RECOVERY,
    STATE_ROOT_MISMATCH_NEXT_STEP,
    CanonicalCommandError,
)
from spec_dock.runtime.application.canonical_schedule import (
    JobServesAnotherRoot,
    ScheduleFailed,
    SchedulePlan,
    apply_schedule,
    plan_schedule,
)
from spec_dock.runtime.application.canonical_tools_check import tool_findings
from spec_dock.runtime.application.project_context import probe_workspace_mode
from spec_dock.runtime.domain.canonical_content import FORMAT_FILE, format_writable, read_format
from spec_dock.runtime.domain.canonical_layout import (
    CANONICAL_BRANCH,
    CANONICAL_REF,
    CANONICAL_TRACKING_REF,
    EXCLUDE_LINES,
    GITIGNORE_PATH,
    LINK_RELATIVE,
)
from spec_dock.runtime.infra import canonical_git, runtime_environment
from spec_dock.runtime.infra.canonical_files import LinkOccupied, append_exclude, place_link
from spec_dock.runtime.infra.canonical_registry import RegistryUnreadable
from spec_dock.runtime.infra.git_process import GitProcessError
from spec_dock.runtime.infra.github_structure import GITHUB_UNAVAILABLE
from spec_dock.runtime.infra.start_lock import StartLock, StartLockBusy
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import (
    Diagnostic,
    Effect,
    OperationResult,
    RecoveryInstructions,
    ResultStatus,
)

if TYPE_CHECKING:
    import argparse
    from collections.abc import Callable
    from pathlib import Path

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.domain.canonical_layout import CatalogLayout
    from spec_dock.runtime.infra.runtime_environment import RuntimeEnvironment

Source = Literal["remote", "local", "new"]
_NETWORK_KINDS = frozenset({"git.fetch", "canonical.remote.create"})


def run_canonical_link(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    return link_checkout(
        context,
        runtime_environment.detect_runtime_environment(),
        command=namespace.command_path,
        timeout=namespace.timeout,
        dry_run=namespace.dry_run,
        schedule=not namespace.no_schedule,
        offline=namespace.offline,
    )


@dataclass(frozen=True)
class _Creation:
    source: Source
    add_fetch_branch: bool
    push_local: str | None  # 4a: the unpushed initial commit on the local branch
    remote_missing: bool  # 4b: a local branch with content and nothing on GitHub
    stale_initial: str | None = None  # a local branch holding only an initial commit that GitHub may supersede


@dataclass(frozen=True)
class _Step:
    kind: str
    target: str
    action: Callable[[], object]
    writes: tuple[Path, ...]


@dataclass
class _Run:
    command: str
    effects: list[Effect] = field(default_factory=list)
    source: Source | None = None
    pushed: bool | None = None
    initial: str | None = None
    exclude_added: tuple[str, ...] = ()


class _StepFailed(Exception):
    def __init__(self, code: str, message: str, details: dict[str, object], *, exit_code: int, recovery: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details
        self.exit_code = exit_code
        self.recovery = recovery


def link_checkout(
    context: ProjectContext,
    environment: RuntimeEnvironment,
    *,
    command: str,
    timeout: float,
    dry_run: bool,
    schedule: bool = True,
    follow_up: bool = False,
    offline: bool = False,
) -> OperationResult[object]:
    """Steps 1-8; `schedule=False` (--no-schedule) skips step 6, and a follow-up honours an earlier --no-schedule."""
    require_git(environment)
    layout = resolve_layout(context)
    # A main checkout on an unmigrated commit keeps working in legacy mode: never put a link there.
    skip_main = not layout.is_main and probe_workspace_mode(layout.main_checkout) != "canonical"
    observation = observe_catalog(layout, environment, timeout=timeout)
    _refuse_blocked(observation, skip_main=skip_main)
    plan = _plan_schedule(layout, observation, environment, schedule=schedule, follow_up=follow_up, timeout=timeout)
    scheduled = _Step("canonical.schedule", str(plan.state_root), lambda: None, plan.write_paths())
    predicted = (*_local_steps(observation, None, timeout=timeout, skip_main=skip_main), scheduled)
    # Check writability before any network call: a sandbox without network must still get the right answer.
    _refuse_unwritable(predicted, environment)
    creation = _plan_creation(layout, timeout=timeout) if observation.state == "absent" else None
    run = _Run(command, source=creation.source if creation else None)
    network = _network_steps(layout, creation, run, timeout=timeout)
    local = _local_steps(observation, creation, timeout=timeout, skip_main=skip_main)
    _refuse_unwritable((*network, *local, scheduled), environment)
    if dry_run:
        planned = (*(Effect(step.kind, "planned", step.target) for step in (*network, *local)), *plan.planned())
        return OperationResult(
            command, "planned", FamilyData("canonical-link", _data(observation, run, changed=False)), 0, effects=planned
        )
    try:
        for index, step in enumerate(network):
            _execute(run, step, remaining=(*network[index + 1 :], *local))
        if network or local:
            _write_locally(run, layout, environment, creation, local, timeout=timeout, skip_main=skip_main)
        else:
            run.effects.extend(_unchanged_effects(observation, (), skip_main=skip_main))
        final = observe_catalog(layout, environment, timeout=timeout)
        broken = [
            str(view.observed.path)
            for view in final.links
            if view.state != "correct" and not (skip_main and view.checkout == layout.main_checkout)
        ]
        if final.state != "ready" or broken:
            raise _StepFailed(
                CANONICAL_NOT_LINKED,
                f"the catalog ({final.state}) or a link is still not correct after linking: {', '.join(broken)}",
                {"catalog_state": final.state, "links": broken},
                exit_code=3,
                recovery=LINK_AGAIN_RECOVERY,
            )
        try:
            schedule_effects, schedule_warnings = apply_schedule(plan, offline=offline)
        except ScheduleFailed as failure:
            run.effects.extend(failure.effects)
            raise _StepFailed(failure.code, failure.message, {}, exit_code=3, recovery=failure.recovery) from failure
        run.effects.extend(schedule_effects)
    except _StepFailed as failure:
        return _failure_result(run, failure)
    except (GitProcessError, OSError, ValueError) as error:
        # An observation between the steps failed: report what was applied instead of hiding it.
        recorded = {(effect.kind, effect.target) for effect in run.effects}
        run.effects.extend(
            Effect(step.kind, "not_attempted", step.target)
            for step in local
            if (step.kind, step.target) not in recorded
        )
        return _failure_result(run, _unexpected_failure(error))
    warnings = _warnings(
        final,
        creation,
        moved=observation.moved,
        environment=environment,
        skip_main=skip_main,
        schedule=tuple(schedule_warnings),
    )
    changed = any(effect.status == "succeeded" for effect in run.effects)
    status: ResultStatus = "succeeded" if changed else "unchanged"
    return OperationResult(
        command,
        status,
        FamilyData("canonical-link", _data(final, run, changed=changed)),
        0,
        effects=tuple(run.effects),
        warnings=warnings,
    )


def _plan_schedule(
    layout: CatalogLayout,
    observation: CatalogObservation,
    environment: RuntimeEnvironment,
    *,
    schedule: bool,
    follow_up: bool,
    timeout: float,
) -> SchedulePlan:
    """Decide steps 6-7 before writing; an unreadable registry stops here with nothing written."""
    moved_from = None
    if observation.moved and observation.registered is not None:
        moved_from = os.path.realpath(observation.registered.path)
    try:
        return plan_schedule(
            layout, environment, moved_from=moved_from, schedule=schedule, follow_up=follow_up, timeout=timeout
        )
    except JobServesAnotherRoot as error:
        raise CanonicalCommandError(
            CANONICAL_STATE_ROOT_MISMATCH,
            str(error),
            recovery=(STATE_ROOT_MISMATCH_NEXT_STEP,),
            details={
                "recorded_state_root": str(error.recorded),
                "state_root": str(error.state_root),
                "next_step": STATE_ROOT_MISMATCH_NEXT_STEP,
            },
        ) from error
    except RegistryUnreadable as error:
        raise CanonicalCommandError(
            CANONICAL_REGISTRY_UNREADABLE,
            str(error),
            recovery=(REGISTRY_UNREADABLE_RECOVERY,),
            details={"path": str(error.path), "next_step": REGISTRY_UNREADABLE_RECOVERY},
        ) from error


def _write_locally(
    run: _Run,
    layout: CatalogLayout,
    environment: RuntimeEnvironment,
    creation: _Creation | None,
    local: tuple[_Step, ...],
    *,
    timeout: float,
    skip_main: bool,
) -> None:
    """Re-observe and write under the clone Start lock; no network inside."""
    try:
        with StartLock(layout.common_dir, timeout=5.0):
            current = observe_catalog(layout, environment, timeout=timeout)
            try:
                _refuse_blocked(current, skip_main=skip_main)
            except CanonicalCommandError as error:
                run.effects.extend(Effect(step.kind, "not_attempted", step.target) for step in local)
                raise _StepFailed(
                    error.code, error.message, error.details, exit_code=error.exit_code, recovery=error.recovery[0]
                ) from error
            if current.state == "absent" and creation is None:
                # The catalog vanished after the first observation; creating it needs a fresh plan.
                run.effects.extend(Effect(step.kind, "not_attempted", step.target) for step in local)
                raise _StepFailed(
                    CANONICAL_NOT_LINKED,
                    "the catalog disappeared while linking",
                    {"catalog": str(layout.catalog)},
                    exit_code=3,
                    recovery=LINK_AGAIN_RECOVERY,
                )
            steps = _local_steps(current, creation, timeout=timeout, pushed=run.pushed, skip_main=skip_main)
            for index, step in enumerate(steps):
                _execute(run, step, remaining=steps[index + 1 :])
            run.effects.extend(_unchanged_effects(current, steps, skip_main=skip_main))
    except StartLockBusy as error:
        run.effects.extend(Effect(step.kind, "not_attempted", step.target) for step in local)
        raise _StepFailed(START_LOCK_BUSY, str(error), {}, exit_code=3, recovery=START_LOCK_BUSY_RECOVERY) from error


def _refuse_unwritable(steps: tuple[_Step, ...], environment: RuntimeEnvironment) -> None:
    denied = sorted({str(path) for step in steps for path in step.writes if not _writable(path)})
    if not denied:
        return
    recovery = SANDBOX_DENIED_RECOVERY if environment.codex_sandbox else PERMISSION_DENIED_RECOVERY
    raise CanonicalCommandError(
        CANONICAL_SANDBOX_DENIED,
        "this process cannot write where canonical link must write: " + ", ".join(denied),
        recovery=(recovery,),
        details={"paths": denied, "next_step": recovery},
    )


def _refuse_blocked(observation: CatalogObservation, *, skip_main: bool = False) -> None:
    """Stop before writing on a mounted checkout, an occupied catalog path or an occupied link path."""
    catalog = observation.layout.catalog
    if observation.state == "foreign":
        raise foreign_error(observation)
    if observation.state == "occupied":
        step = occupied_next_step(observation)
        raise CanonicalCommandError(
            CANONICAL_PATH_OCCUPIED,
            observation.detail or f"{catalog} holds something that is not this clone's catalog",
            recovery=(step,),
            details={"path": str(catalog), "entries": observation.entries, "next_step": step},
        )
    if observation.state == "elsewhere":
        registered = observation.registered.path if observation.registered is not None else None
        step = elsewhere_next_step(registered, exists=bool(observation.registered_exists))
        raise CanonicalCommandError(
            CANONICAL_PATH_OCCUPIED,
            f"spec-dock/canonical is checked out at {registered}, not at {catalog}",
            recovery=(step,),
            details={
                "path": str(catalog),
                "registered_path": str(registered),
                "registered_exists": observation.registered_exists,
                "next_step": step,
            },
        )
    for view in observation.links:
        if view.state != "occupied" or (skip_main and view.checkout == observation.layout.main_checkout):
            continue
        path = view.observed.path
        step = link_occupied_next_step(path)
        raise CanonicalCommandError(
            CANONICAL_LINK_OCCUPIED,
            f"{path} is a real {view.observed.kind} with {view.observed.entries or 0} entries, not a link",
            recovery=(step,),
            details={
                "path": str(path),
                "kind": view.observed.kind,
                "entries": view.observed.entries,
                "next_step": step,
            },
        )


def elsewhere_next_step(registered: Path | None, *, exists: bool) -> str:
    if exists:
        return (
            f"In {registered}, switch to another branch (git -C {registered} switch <branch>) so spec-dock/canonical "
            "is free, then run spec-dock canonical link; SpecDock does not touch that worktree."
        )
    return (
        f"Inspect the Git registration of {registered}; run git worktree unlock {registered} if it is locked, "
        f"then git worktree remove {registered}, and run spec-dock canonical link again."
    )


def link_occupied_next_step(path: Path) -> str:
    return (
        f"Inspect {path} and move its contents aside, then run spec-dock canonical link; SpecDock does not delete it. "
        "After checking out a pre-migration commit, switch back first."
    )


def _plan_creation(layout: CatalogLayout, *, timeout: float) -> _Creation:
    main = layout.main_checkout
    try:
        remote = canonical_git.remote_canonical(main, timeout=timeout)
    except GitProcessError as error:
        raise CanonicalCommandError(
            GITHUB_UNAVAILABLE,
            "could not ask origin whether spec-dock/canonical exists",
            exit_code=5,
            recovery=(LINK_NETWORK_RECOVERY,),
            details=error.details(),
        ) from error
    add_fetch_branch = not canonical_git.fetch_covers_canonical(main, timeout=timeout)
    local = canonical_git.resolve_commit(main, CANONICAL_REF, timeout=timeout)
    initial = local if local is not None and canonical_git.is_initial_commit(main, local, timeout=timeout) else None
    if remote == "present":
        # A local branch with only an unpushed initial commit holds nothing; GitHub's canonical replaces it.
        return _Creation("remote", add_fetch_branch, None, remote_missing=False, stale_initial=initial)
    if local is not None:
        if initial is not None:
            return _Creation("new", add_fetch_branch, local, remote_missing=False, stale_initial=initial)
        return _Creation("local", False, None, remote_missing=True)
    default = canonical_git.resolve_commit(main, "refs/remotes/origin/HEAD", timeout=timeout) or "HEAD"
    has_head = canonical_git.resolve_commit(main, default, timeout=timeout) is not None
    if has_head and canonical_git.tree_has_path(main, default, str(LINK_RELATIVE), timeout=timeout):
        raise CanonicalCommandError(
            CANONICAL_NOT_MIGRATED,
            "GitHub has no spec-dock/canonical and the default branch still tracks spec-dock/initiatives; "
            "an empty canonical would hide those specs",
            recovery=(NOT_MIGRATED_RECOVERY,),
            details={"default_ref": default, "path": str(LINK_RELATIVE), "next_step": NOT_MIGRATED_RECOVERY},
        )
    return _Creation("new", add_fetch_branch, None, remote_missing=False)


def _network_steps(
    layout: CatalogLayout, creation: _Creation | None, run: _Run, *, timeout: float
) -> tuple[_Step, ...]:
    """Network work outside the Start lock: the initial push and the fetch of origin/spec-dock/canonical."""
    if creation is None or creation.source == "local":
        return ()
    main, common = layout.main_checkout, layout.common_dir
    tracking = "origin/" + CANONICAL_BRANCH
    steps: list[_Step] = []
    if creation.source == "new":
        if creation.push_local is None:

            def create() -> str:
                run.initial = canonical_git.create_initial_commit(main, timeout=timeout)
                return run.initial

            # A local step kept apart from the push, so an identity problem is not reported as a network one.
            steps.append(_Step("git.commit.create", CANONICAL_BRANCH, create, (common,)))

        def push() -> bool:
            oid = creation.push_local or run.initial
            if oid is None:
                raise ValueError("no initial canonical commit to push")
            return canonical_git.push_initial(main, oid, timeout=timeout) == "pushed"

        steps.append(_Step("canonical.remote.create", tracking, push, (common,)))
    steps.append(_Step("git.fetch", tracking, lambda: canonical_git.fetch_canonical(main, timeout=timeout), (common,)))
    return tuple(steps)


def _local_steps(
    observation: CatalogObservation,
    creation: _Creation | None,
    *,
    timeout: float,
    pushed: bool | None = None,
    skip_main: bool = False,
) -> tuple[_Step, ...]:
    layout = observation.layout
    main, common, catalog = layout.main_checkout, layout.common_dir, layout.catalog
    admin = common / "worktrees" / observation.gitdir.name if observation.gitdir is not None else common / "worktrees"
    steps: list[_Step] = []
    lock = _Step(
        "git.worktree.lock", str(catalog), lambda: canonical_git.lock_worktree(main, catalog, timeout=timeout), (admin,)
    )
    if observation.state == "ready":
        if not observation.locked:
            steps.append(lock)
    elif observation.state == "repair":
        steps.append(
            _Step(
                "git.worktree.repair",
                str(catalog),
                lambda: canonical_git.repair_worktree(main, catalog, timeout=timeout),
                (admin, catalog, common),
            )
        )
        if not observation.locked:
            steps.append(lock)
    elif observation.state == "readd":
        steps.append(
            _Step(
                "git.worktree.add",
                str(catalog),
                lambda: canonical_git.add_catalog_worktree(main, catalog, mode="readd", timeout=timeout),
                (common / "worktrees", catalog.parent, common),
            )
        )
        steps.append(_Step("git.worktree.lock", str(catalog), lock.action, (common / "worktrees",)))
    elif observation.state == "absent" and creation is not None:
        if creation.add_fetch_branch:
            steps.append(
                _Step(
                    "git.remote.set-branches",
                    "origin",
                    lambda: _add_fetch_branch_once(main, timeout=timeout),
                    (common,),
                )
            )
        stale = creation.stale_initial
        if stale is not None and (creation.source == "remote" or pushed is False):
            initial = stale
            steps.append(
                _Step(
                    "git.branch.reset",
                    CANONICAL_BRANCH,
                    lambda: _reset_to_tracking(main, expected=initial, timeout=timeout),
                    (common,),
                )
            )
        mode: Literal["local"] | None = "local" if creation.source == "local" else None
        steps.append(
            _Step(
                "git.worktree.add",
                str(catalog),
                lambda: _add_absent(main, catalog, mode=mode, timeout=timeout),
                (common / "worktrees", catalog.parent, common),
            )
        )
        steps.append(_Step("git.worktree.lock", str(catalog), lock.action, (common / "worktrees",)))
    elif observation.state == "absent":
        # Before the creation plan exists (the pre-network writability check): the catalog write sites only.
        steps.append(
            _Step("git.worktree.add", str(catalog), lambda: None, (common / "worktrees", catalog.parent, common))
        )
    if observation.exclude_missing:
        exclude = common / "info/exclude"
        steps.append(
            _Step("git.info.exclude", str(exclude), lambda: append_exclude(common, EXCLUDE_LINES), (common / "info",))
        )
    for view in observation.links:
        if skip_main and view.checkout == main:
            continue
        observed = view.observed
        if observed.kind == "absent" or (observed.kind == "symlink" and observed.text != view.expected):
            path = observed.path
            steps.append(_Step("canonical.link", str(path), _placer(path, view.expected), (path.parent,)))
    return tuple(steps)


def _add_fetch_branch_once(main: Path, *, timeout: float) -> bool:
    """set-branches --add does not deduplicate, so re-check coverage under the lock first."""
    if canonical_git.fetch_covers_canonical(main, timeout=timeout):
        return False
    canonical_git.add_fetch_branch(main, timeout=timeout)
    return True


def _placer(path: Path, text: str) -> Callable[[], object]:
    return lambda: place_link(path.parent, path.name, text)


def _reset_to_tracking(main: Path, *, expected: str, timeout: float) -> bool:
    tracking = canonical_git.resolve_commit(main, CANONICAL_TRACKING_REF, timeout=timeout)
    if tracking is None:
        raise ValueError("origin/spec-dock/canonical was not fetched")
    if tracking == expected:
        return False
    canonical_git.reset_branch(main, tracking, expected=expected, timeout=timeout)
    return True


def _add_absent(main: Path, catalog: Path, *, mode: Literal["local"] | None, timeout: float) -> None:
    if mode is None:
        mode = "local" if canonical_git.resolve_commit(main, CANONICAL_REF, timeout=timeout) else None
    canonical_git.add_catalog_worktree(main, catalog, mode=mode or "track", timeout=timeout)


def _writable(path: Path) -> bool:
    candidate = path
    while not os.path.lexists(candidate):
        if candidate.parent == candidate:
            return False
        candidate = candidate.parent
    return os.access(candidate, os.W_OK)


def _execute(run: _Run, step: _Step, *, remaining: tuple[_Step, ...]) -> None:
    try:
        outcome = step.action()
    except (GitProcessError, OSError, ValueError) as error:
        uncertain = isinstance(error, GitProcessError) and error.uncertain
        run.effects.append(Effect(step.kind, "unknown" if uncertain else "failed", step.target))
        run.effects.extend(Effect(item.kind, "not_attempted", item.target) for item in remaining)
        if _permission_denied(error):
            raise _StepFailed(
                CANONICAL_SANDBOX_DENIED,
                f"{step.kind} was denied: {str(error).strip()}",
                error.details() if isinstance(error, GitProcessError) else {"target": step.target},
                exit_code=3,
                recovery=PERMISSION_DENIED_RECOVERY,
            ) from error
        if isinstance(error, GitProcessError):
            raise _git_failure(error, network=step.kind in _NETWORK_KINDS, kind=step.kind) from error
        if isinstance(error, LinkOccupied):
            raise _StepFailed(
                CANONICAL_LINK_OCCUPIED, str(error), {"path": step.target}, exit_code=3, recovery=LINK_AGAIN_RECOVERY
            ) from error
        raise _StepFailed(
            "LOCAL_IO_FAILED", str(error), {"target": step.target}, exit_code=5, recovery=LINK_AGAIN_RECOVERY
        ) from error
    if step.kind == "canonical.remote.create":
        run.pushed = bool(outcome)
        run.effects.append(Effect(step.kind, "succeeded" if outcome else "unchanged", step.target))
        if not outcome:
            run.source = "remote"
        return
    if step.kind in ("git.remote.set-branches", "git.branch.reset") and outcome is False:
        run.effects.append(Effect(step.kind, "unchanged", step.target))
        return
    if step.kind == "git.info.exclude":
        run.exclude_added = tuple(outcome) if isinstance(outcome, tuple) else ()
        run.effects.append(Effect(step.kind, "succeeded" if run.exclude_added else "unchanged", step.target))
        return
    if step.kind == "canonical.link" and outcome == "unchanged":
        run.effects.append(Effect(step.kind, "unchanged", step.target))
        return
    run.effects.append(Effect(step.kind, "succeeded", step.target))


def _git_failure(error: GitProcessError, *, network: bool, kind: str) -> _StepFailed:
    stderr = error.stderr.decode("utf-8", errors="replace")
    if "Author identity unknown" in stderr or "Please tell me who you are" in stderr:
        recovery = GIT_IDENTITY_RECOVERY
    else:
        recovery = LINK_NETWORK_RECOVERY if network else LINK_AGAIN_RECOVERY
    return _StepFailed(
        GITHUB_UNAVAILABLE if network else "GIT_FAILED",
        stderr.strip() or f"{kind} failed",
        error.details(),
        exit_code=5,
        recovery=recovery,
    )


def _unexpected_failure(error: Exception) -> _StepFailed:
    """An observation between the steps failed after something may have been written."""
    if _permission_denied(error):
        details = error.details() if isinstance(error, GitProcessError) else {}
        return _StepFailed(
            CANONICAL_SANDBOX_DENIED, str(error).strip(), details, exit_code=3, recovery=PERMISSION_DENIED_RECOVERY
        )
    if isinstance(error, GitProcessError):
        return _git_failure(error, network=False, kind="observation")
    return _StepFailed("LOCAL_IO_FAILED", str(error), {}, exit_code=5, recovery=LINK_AGAIN_RECOVERY)


def _permission_denied(error: Exception) -> bool:
    """A sandbox can refuse a write that access(2) allowed (Linux Landlock); name it so."""
    if isinstance(error, PermissionError):
        return True
    if isinstance(error, GitProcessError):
        text = error.stderr.decode("utf-8", errors="replace")
        return "Operation not permitted" in text or "Permission denied" in text
    return False


def _unchanged_effects(
    observation: CatalogObservation, steps: tuple[_Step, ...], *, skip_main: bool = False
) -> tuple[Effect, ...]:
    """Report the parts that were already in place, so a repeated link answers unchanged."""
    layout = observation.layout
    kinds = {step.kind for step in steps}
    targets = {step.target for step in steps}
    effects: list[Effect] = []
    if not kinds & {"git.worktree.add", "git.worktree.repair", "git.worktree.lock", "git.branch.reset"}:
        effects.append(Effect("canonical.catalog", "unchanged", str(layout.catalog)))
    if "git.info.exclude" not in kinds:
        effects.append(Effect("git.info.exclude", "unchanged", str(layout.common_dir / "info/exclude")))
    effects.extend(
        Effect("canonical.link", "unchanged", str(view.observed.path))
        for view in observation.links
        if str(view.observed.path) not in targets and not (skip_main and view.checkout == layout.main_checkout)
    )
    return tuple(effects)


def _failure_result(run: _Run, failure: _StepFailed) -> OperationResult[object]:
    applied = any(effect.status in ("succeeded", "unknown") for effect in run.effects)
    diagnostic = Diagnostic(failure.code, failure.message, failure.details)
    recovery = RecoveryInstructions((failure.recovery,))
    data = FamilyData("canonical-link", {"changed": any(effect.status == "succeeded" for effect in run.effects)})
    if applied:
        return OperationResult(
            run.command, "partial", data, 6, effects=tuple(run.effects), error=diagnostic, recovery=recovery
        )
    return OperationResult(
        run.command, "failed", data, failure.exit_code, effects=tuple(run.effects), error=diagnostic, recovery=recovery
    )


def _warnings(
    observation: CatalogObservation,
    creation: _Creation | None,
    *,
    moved: bool,
    environment: RuntimeEnvironment,
    skip_main: bool,
    schedule: tuple[Diagnostic, ...] = (),
) -> tuple[Diagnostic, ...]:
    layout = observation.layout
    warnings: list[Diagnostic] = []
    if skip_main:
        warnings.append(main_not_migrated_warning(layout))
    if moved:
        warnings.append(
            Diagnostic(
                CANONICAL_MAIN_MOVED,
                "The main checkout moved; git worktree repair reconnected the catalog and may also have reconnected "
                f"the linked worktrees' .git files. {MAIN_MOVED_NEXT_STEP}",
                {"catalog": str(layout.catalog), "next_step": MAIN_MOVED_NEXT_STEP},
            )
        )
    if creation is not None and creation.remote_missing:
        warnings.append(
            Diagnostic(
                CANONICAL_REMOTE_MISSING,
                f"GitHub has no spec-dock/canonical; the catalog uses the local branch. {REMOTE_MISSING_NEXT_STEP}",
                {"next_step": REMOTE_MISSING_NEXT_STEP},
            )
        )
    try:
        version = read_format((layout.catalog / FORMAT_FILE).read_bytes())
    except OSError:
        version = None
    if not format_writable(version):
        step = FORMAT_MISSING_RECOVERY if version is None else FORMAT_UNSUPPORTED_RECOVERY
        warnings.append(
            Diagnostic(
                CANONICAL_FORMAT_UNSUPPORTED,
                f"the catalog declares canonical format {version!r}; SpecDock will not write it. {step}",
                {"format": version, "next_step": step},
            )
        )
    if observation.gitignore_missing:
        path = layout.checkout / GITIGNORE_PATH
        step = gitignore_next_step(layout)
        warnings.append(
            Diagnostic(
                CANONICAL_IGNORE_RULES_MISSING,
                f"{path} lacks {', '.join(observation.gitignore_missing)}. {step}",
                {
                    "item": "exclude",
                    "path": str(path),
                    "missing": list(observation.gitignore_missing),
                    "next_step": step,
                },
            )
        )
    _item, tools = tool_findings(layout, environment)
    return (*warnings, *schedule, *tools)


def main_not_migrated_message(path: Path) -> str:
    return f"the main checkout does not declare workspace schema 4, so {path} was left untouched"


def main_not_migrated_warning(layout: CatalogLayout) -> Diagnostic:
    path = layout.link_path(layout.main_checkout)
    return Diagnostic(
        CANONICAL_MAIN_NOT_MIGRATED,
        f"{main_not_migrated_message(path)}; next: {MAIN_NOT_MIGRATED_NEXT_STEP}",
        {"item": "link", "path": str(path), "next_step": MAIN_NOT_MIGRATED_NEXT_STEP},
    )


def _data(observation: CatalogObservation, run: _Run, *, changed: bool) -> dict[str, object]:
    layout = observation.layout
    return {
        "main_checkout": str(layout.main_checkout),
        "checkout": str(layout.checkout),
        "catalog": str(layout.catalog),
        "catalog_state": observation.state,
        "source": run.source,
        "links": [
            {
                "checkout": str(view.checkout),
                "path": str(view.observed.path),
                "expected": view.expected,
                "state": view.state,
            }
            for view in observation.links
        ],
        "exclude": {"path": str(layout.common_dir / "info/exclude"), "added": list(run.exclude_added)},
        "changed": changed,
    }


@dataclass(frozen=True)
class LinkFollowUp:
    """What another command adds to its own result after running the link steps for one checkout."""

    effects: tuple[Effect, ...]
    warnings: tuple[Diagnostic, ...]
    link: dict[str, object]


def link_after_command(
    checkout: Path,
    *,
    environment: RuntimeEnvironment | None = None,
    timeout: float = 30.0,
    dry_run: bool = False,
) -> LinkFollowUp:
    """Run the link steps for `checkout` without changing the caller's result (R-B4).

    The caller must not hold the clone Start lock: this function takes it. Failures, including
    START_LOCK_BUSY, come back as warnings with the next step; effects are only succeeded, unchanged or
    (dry run) planned ones, so a caller's succeeded or planned result stays valid.
    """
    from spec_dock.runtime.application.project_context import resolve_context

    link_path = checkout / LINK_RELATIVE

    def failed(code: str, message: str, step: str, details: dict[str, object]) -> LinkFollowUp:
        # Every follow-up step ends in linking this checkout, never in re-running the caller's command.
        if "spec-dock canonical link" not in step:
            step = f"{step} Then run spec-dock canonical link in {checkout}."
        warning = Diagnostic(code, f"{message}; next: {step}", {**details, "next_step": step})
        return LinkFollowUp((), (warning,), {"path": str(link_path), "state": "failed"})

    if not os.path.lexists(checkout):
        if dry_run:
            return LinkFollowUp(
                (Effect("canonical.link", "planned", str(link_path)),), (), {"path": str(link_path), "state": "planned"}
            )
        return failed(CANONICAL_NOT_LINKED, f"{checkout} does not exist", LINK_AGAIN_RECOVERY, {"path": str(checkout)})
    if probe_workspace_mode(checkout) != "canonical":
        warning = Diagnostic(
            CANONICAL_CHECKOUT_NOT_MIGRATED,
            f"{checkout} does not declare workspace schema 4, so it was not linked; next: {CHECKOUT_NOT_MIGRATED_NEXT_STEP}",
            {"path": str(checkout), "next_step": CHECKOUT_NOT_MIGRATED_NEXT_STEP},
        )
        return LinkFollowUp((), (warning,), {"path": str(link_path), "state": "skipped"})
    current = environment or runtime_environment.detect_runtime_environment()
    try:
        context = resolve_context(str(checkout), checkout, timeout=timeout)
        result = link_checkout(
            context, current, command="canonical link", timeout=timeout, dry_run=dry_run, follow_up=True
        )
    except CanonicalCommandError as error:
        return failed(
            error.code, error.message, error.recovery[0] if error.recovery else LINK_AGAIN_RECOVERY, error.details
        )
    except (GitProcessError, OSError, ValueError, RuntimeError) as error:
        code = "GIT_FAILED" if isinstance(error, GitProcessError) else "LOCAL_IO_FAILED"
        return failed(code, str(error), LINK_AGAIN_RECOVERY, {})
    if result.status in ("failed", "partial"):
        assert result.error is not None
        recovery = result.recovery
        step = recovery.instructions[0] if isinstance(recovery, RecoveryInstructions) else LINK_AGAIN_RECOVERY
        effects = [{"kind": item.kind, "status": item.status, "target": item.target} for item in result.effects]
        follow = failed(result.error.code, result.error.message, step, {**result.error.details, "effects": effects})
        kept = tuple(effect for effect in result.effects if effect.status in ("succeeded", "unchanged"))
        return LinkFollowUp(kept, follow.warnings, follow.link)
    return LinkFollowUp(
        result.effects, result.warnings, {"path": str(link_path), "state": "planned" if dry_run else "correct"}
    )
