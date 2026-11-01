"""`canonical remove`: take this clone's catalog, links and sync registration away (R-B8, Epic ch. 3).

Every stop condition is checked before writing, under the clone Start lock and this catalog's cycle lock
(a running cycle finishes first and no later cycle starts): unsaved or unpushed changes, and ignored files
other than .runtime/ that a worktree removal would delete. Without --yes only the plan is returned. The
dashboard files of the main checkout go (iss-00438); branches (local and GitHub) and the structure snapshot stay.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import TYPE_CHECKING

from spec_dock.runtime.application.canonical_catalog import observe_catalog, require_git, resolve_layout
from spec_dock.runtime.application.canonical_dashboard import dashboard_directory
from spec_dock.runtime.application.canonical_errors import (
    CANONICAL_IGNORED_FILES_PRESENT,
    CANONICAL_LOCK_BUSY,
    CANONICAL_PATH_OCCUPIED,
    CANONICAL_REGISTRY_UNREADABLE,
    CANONICAL_SANDBOX_DENIED,
    CANONICAL_UNSAVED_CHANGES,
    IGNORED_FILES_RECOVERY,
    LOCK_BUSY_RECOVERY,
    PERMISSION_DENIED_RECOVERY,
    REGISTRY_UNREADABLE_RECOVERY,
    START_LOCK_BUSY,
    STATUS_RECOVERY,
    UNSAVED_CHANGES_RECOVERY,
    CanonicalCommandError,
)
from spec_dock.runtime.domain.canonical_dashboard import DASHBOARD_FILES
from spec_dock.runtime.domain.canonical_layout import EXCLUDE_LINES, LINK_RELATIVE, link_state
from spec_dock.runtime.domain.canonical_scheduler import SchedulerSpec
from spec_dock.runtime.domain.canonical_sync_state import SyncRegistry
from spec_dock.runtime.infra import canonical_git, canonical_scheduling, runtime_environment
from spec_dock.runtime.infra.canonical_files import is_regular_file, observe_link
from spec_dock.runtime.infra.canonical_registry import RegistryUnreadable, read_registry, registry_path, update_registry
from spec_dock.runtime.infra.canonical_state import (
    CycleBusy,
    catalog_state_dir,
    cycle_lock,
    remove_catalog_state,
)
from spec_dock.runtime.infra.catalog_lock import CatalogLock, CatalogLockBusy
from spec_dock.runtime.infra.git_process import GitProcessError
from spec_dock.runtime.infra.start_lock import StartLock, StartLockBusy
from spec_dock.runtime.infra.state_root import resolve_state_root
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult, RecoveryInstructions

if TYPE_CHECKING:
    import argparse
    from collections.abc import Callable

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.domain.canonical_layout import CatalogLayout
    from spec_dock.runtime.infra.runtime_environment import RuntimeEnvironment

# A cycle normally ends in seconds; one whose every network attempt times out can run longer, and remove then
# stops with CANONICAL_LOCK_BUSY before writing anything, so the same command can simply be run again.
REMOVE_CYCLE_WAIT = 150.0
REMOVE_AGAIN_RECOVERY = "Check spec-dock canonical status, then run spec-dock canonical remove --yes again."


@dataclass(frozen=True)
class _Step:
    kind: str
    target: str
    action: Callable[[], object]
    writes: tuple[Path, ...]


def run_canonical_remove(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    environment = runtime_environment.detect_runtime_environment()
    require_git(environment)
    layout = resolve_layout(context)
    root = resolve_state_root()
    catalog = os.path.realpath(layout.catalog)
    apply = bool(namespace.yes) and not namespace.dry_run
    try:
        with StartLock(layout.common_dir, timeout=5.0):
            if not apply:
                return _remove(namespace, layout, environment, root, catalog, apply=False)
            # Taking the cycle lock creates its file: check that the state root is writable first.
            if not _writable(catalog_state_dir(root, catalog)):
                raise CanonicalCommandError(
                    CANONICAL_SANDBOX_DENIED,
                    f"this process cannot write the state root {root}",
                    recovery=(PERMISSION_DENIED_RECOVERY,),
                    details={"paths": [str(root)], "next_step": PERMISSION_DENIED_RECOVERY},
                )
            # A running cycle finishes first and no later cycle starts while the catalog goes away.
            with cycle_lock(root, catalog, timeout=REMOVE_CYCLE_WAIT):
                return _remove(namespace, layout, environment, root, catalog, apply=True)
    except StartLockBusy as error:
        raise CanonicalCommandError(START_LOCK_BUSY, str(error), recovery=(LOCK_BUSY_RECOVERY,)) from error
    except CycleBusy as error:
        raise CanonicalCommandError(CANONICAL_LOCK_BUSY, str(error), recovery=(LOCK_BUSY_RECOVERY,)) from error
    except RegistryUnreadable as error:
        raise CanonicalCommandError(
            CANONICAL_REGISTRY_UNREADABLE,
            str(error),
            recovery=(REGISTRY_UNREADABLE_RECOVERY,),
            details={"path": str(error.path), "next_step": REGISTRY_UNREADABLE_RECOVERY},
        ) from error


def _remove(
    namespace: argparse.Namespace,
    layout: CatalogLayout,
    environment: RuntimeEnvironment,
    root: Path,
    catalog: str,
    *,
    apply: bool,
) -> OperationResult[object]:
    timeout = namespace.timeout
    observation = observe_catalog(layout, environment, timeout=timeout)
    if observation.state in ("occupied", "elsewhere", "foreign"):
        # Not a catalog this command can check for unsaved work: stop before taking anything away.
        raise CanonicalCommandError(
            CANONICAL_PATH_OCCUPIED,
            observation.detail or f"{layout.catalog} is not this clone's catalog in a removable state",
            recovery=(STATUS_RECOVERY,),
            details={"catalog_state": observation.state, "next_step": STATUS_RECOVERY},
        )
    present = observation.state in ("ready", "repair") and Path(catalog).is_dir()
    lock = CatalogLock(Path(catalog), timeout=10.0) if present and apply else None
    if lock is not None:
        try:
            lock.__enter__()
        except CatalogLockBusy as error:
            raise CanonicalCommandError(CANONICAL_LOCK_BUSY, str(error), recovery=(LOCK_BUSY_RECOVERY,)) from error
    try:
        # Checked under the catalog lock when applying, so no command can write in between.
        if present:
            _refuse_unsaved(Path(catalog), timeout=timeout)
        steps = _steps(layout, environment, root, catalog, present=present, timeout=timeout)
        denied = sorted({str(path) for step in steps for path in step.writes if not _writable(path)})
        if denied:
            raise CanonicalCommandError(
                CANONICAL_SANDBOX_DENIED,
                "this process cannot write where canonical remove must write: " + ", ".join(denied),
                recovery=(PERMISSION_DENIED_RECOVERY,),
                details={"paths": denied, "next_step": PERMISSION_DENIED_RECOVERY},
            )
        data = FamilyData("canonical-remove", {"catalog": catalog, "removed": False})
        if not apply:
            planned = tuple(Effect(step.kind, "planned", step.target) for step in steps)
            return OperationResult(namespace.command_path, "planned", data, 0, effects=planned)
        return _apply(namespace.command_path, catalog, steps)
    finally:
        if lock is not None:
            lock.__exit__(None, None, None)


def _apply(command: str, catalog: str, steps: list[_Step]) -> OperationResult[object]:
    effects: list[Effect] = []
    data = FamilyData("canonical-remove", {"catalog": catalog, "removed": False})
    for index, step in enumerate(steps):
        try:
            outcome = step.action()
        except (
            GitProcessError,
            OSError,
            TimeoutError,
            canonical_scheduling.SchedulerError,
            RegistryUnreadable,
        ) as error:
            effects.append(Effect(step.kind, "failed", step.target))
            effects.extend(Effect(item.kind, "not_attempted", item.target) for item in steps[index + 1 :])
            message = (
                error.stderr.decode(errors="replace").strip() if isinstance(error, GitProcessError) else str(error)
            )
            applied = any(effect.status == "succeeded" for effect in effects)
            return OperationResult(
                command,
                "partial" if applied else "failed",
                data,
                6 if applied else 5,
                effects=tuple(effects),
                error=Diagnostic("CANONICAL_REMOVE_FAILED", f"{step.kind}: {message}", {"target": step.target}),
                recovery=RecoveryInstructions((REMOVE_AGAIN_RECOVERY,)),
            )
        effects.append(Effect(step.kind, "unchanged" if outcome is False else "succeeded", step.target))
    data = FamilyData("canonical-remove", {"catalog": catalog, "removed": True})
    changed = any(effect.status == "succeeded" for effect in effects)
    return OperationResult(command, "succeeded" if changed else "unchanged", data, 0, effects=tuple(effects))


def _refuse_unsaved(catalog: Path, *, timeout: float) -> None:
    summary = canonical_git.catalog_change_summary(catalog, timeout=timeout)
    unpushed = canonical_git.unpushed(catalog, timeout=timeout)
    head = canonical_git.resolve_commit(catalog, "HEAD", timeout=timeout)
    if unpushed is not None:
        count = unpushed[0]
    else:  # never fetched: only content beyond the initial commit is at stake
        count = 1 if head is not None and not canonical_git.is_initial_commit(catalog, head) else 0
    if summary.unsaved or count:
        raise CanonicalCommandError(
            CANONICAL_UNSAVED_CHANGES,
            f"the catalog has {summary.unsaved} unsaved change(s) and {count} unpushed commit(s)",
            recovery=(UNSAVED_CHANGES_RECOVERY,),
            details={"unsaved": summary.unsaved, "unpushed": count, "next_step": STATUS_RECOVERY},
        )
    # OS junk files are never saved (iss-00493), yet removing the catalog would delete them as well.
    ignored = tuple(sorted({*canonical_git.ignored_files(catalog, timeout=timeout), *summary.local_junk}))
    if ignored:
        raise CanonicalCommandError(
            CANONICAL_IGNORED_FILES_PRESENT,
            f"the catalog holds ignored or OS files that removing it would delete: {', '.join(ignored[:10])}",
            recovery=(IGNORED_FILES_RECOVERY,),
            details={"paths": list(ignored), "next_step": IGNORED_FILES_RECOVERY},
        )


def _steps(
    layout: CatalogLayout, environment: RuntimeEnvironment, root: Path, catalog: str, *, present: bool, timeout: float
) -> list[_Step]:
    main = layout.main_checkout
    steps: list[_Step] = []
    checkouts = {main, layout.checkout}
    for record in canonical_git.list_worktrees(main, timeout=timeout):
        if record.path is not None and os.path.realpath(record.path) != catalog and Path(record.path).is_dir():
            checkouts.add(record.path)
    for checkout in sorted(checkouts):
        link = checkout / LINK_RELATIVE
        observed = observe_link(link)
        if link_state(observed, expected_text=layout.link_text(checkout), catalog=Path(catalog)) == "correct":
            steps.append(_Step("canonical.link.remove", str(link), link.unlink, (link.parent,)))
    if present:
        steps.append(
            _Step(
                "git.worktree.remove",
                catalog,
                lambda: _remove_worktree(main, Path(catalog), timeout=timeout),
                (layout.common_dir / "worktrees", Path(catalog).parent),
            )
        )
    dashboard = dashboard_directory(main)
    for name in DASHBOARD_FILES:  # only regular files: a directory or link there is not SpecDock's (iss-00438)
        path = dashboard / name
        if is_regular_file(path):
            steps.append(_Step("canonical.dashboard.remove", str(path), path.unlink, (dashboard,)))
    exclude = layout.common_dir / "info/exclude"
    if _has_exclude_lines(exclude):
        steps.append(_Step("git.info.exclude", str(exclude), lambda: _drop_exclude_lines(exclude), (exclude.parent,)))
    registry = read_registry(root)
    others = [entry for entry in registry.catalogs if entry.catalog != catalog]
    if registry.scheduler is not None and not others and registry.entry_for(catalog) is not None:
        # The job goes before the registry entry, so a failure here can be retried by the same command.
        kind = registry.scheduler
        scheduler = canonical_scheduling.scheduler_for(kind, state_root=root, environment=environment)
        spec = SchedulerSpec(Path("/"), root, Path("/"), environment.home or Path.home())
        if canonical_scheduling.foreign_state_root(scheduler, root, spec.home) is None:  # never another root's job
            steps.append(
                _Step("canonical.scheduler", kind, lambda: scheduler.remove(spec), scheduler.write_paths(spec))
            )
    if registry.entry_for(catalog) is not None:
        steps.append(_Step("canonical.registry", str(registry_path(root)), lambda: _unregister(root, catalog), (root,)))
    if catalog_state_dir(root, catalog).exists():
        steps.append(
            _Step(
                "canonical.state",
                str(catalog_state_dir(root, catalog)),
                lambda: remove_catalog_state(root, catalog),
                (root,),
            )
        )
    return steps


def _remove_worktree(main: Path, catalog: Path, *, timeout: float) -> None:
    canonical_git.run_catalog_git(
        main, "worktree", "unlock", str(catalog), mutation=True, timeout=timeout, returncodes=frozenset({0, 128})
    )
    canonical_git.run_catalog_git(main, "worktree", "remove", str(catalog), mutation=True, timeout=timeout)


def _has_exclude_lines(path: Path) -> bool:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (FileNotFoundError, UnicodeDecodeError):
        return False
    return any(line in EXCLUDE_LINES for line in lines)


def _drop_exclude_lines(path: Path) -> None:
    """Remove only the three canonical lines; every other line of info/exclude stays as it was."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    kept = "".join(line for line in lines if line.rstrip("\r\n") not in EXCLUDE_LINES)
    temporary = path.with_name(f".{path.name}.spec-dock-{os.getpid()}")
    try:
        temporary.write_text(kept, encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _unregister(root: Path, catalog: str) -> None:
    def mutate(registry: SyncRegistry) -> SyncRegistry:
        remaining = registry.without(catalog)
        return SyncRegistry(remaining.scheduler if remaining.catalogs else None, remaining.catalogs)

    update_registry(root, mutate)


def _writable(path: Path) -> bool:
    candidate = path
    while not os.path.lexists(candidate):
        if candidate.parent == candidate:
            return False
        candidate = candidate.parent
    return os.access(candidate, os.W_OK)
