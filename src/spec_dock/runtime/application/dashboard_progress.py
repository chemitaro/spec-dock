"""The plan progress of the Issues in progress, for the structure list (iss-00574 D-07).

Only `plan.cue` is evaluated, without the types (`cue export -e steps`), and only for the Issues the caller names
(the ones in progress). A count is remembered per catalog by the file's time and size, so the 5-second refresh runs
`cue` only after a plan changed. External processes of one request share one time limit; past it, values are None
and not remembered, so a later request reads them (F-01). Nothing is written.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import stat
import threading
import time
from typing import TYPE_CHECKING, Final, Protocol

from spec_dock.runtime.domain.canonical_layout import scope_relative
from spec_dock.runtime.infra.cue_tool import CueToolError, locate_cue

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

    from spec_dock.runtime.application.dashboard_site import SiteRepository
    from spec_dock.runtime.domain.dashboard_model import DashboardModel
    from spec_dock.runtime.infra.cue_tool import CueTool

TIMEOUT: Final = 3.0
_STATUSES: Final = ("done", "doing", "todo", "dropped")


class StepsReader(Protocol):
    def __call__(
        self, directory: Path, *, timeout: float, tool: CueTool | None = None
    ) -> Mapping[str, object] | None: ...


class CueLocator(Protocol):
    def __call__(self, *, timeout: float) -> CueTool: ...


def read_plan_steps(directory: Path, *, timeout: float, tool: CueTool | None = None) -> Mapping[str, object] | None:
    """The `steps` of `plan.cue` alone, or None when cue cannot evaluate it. A missing cue raises CueToolError."""
    tool = tool or locate_cue(timeout=timeout)
    where = directory.resolve()
    run = tool.export([where / "plan.cue"], cwd=where, timeout=timeout, expression="steps")
    if run.returncode != 0:
        return None
    try:
        value = json.loads(run.stdout)
    except ValueError:
        return None
    return value if isinstance(value, dict) else None


def plan_counts(steps: Mapping[str, object] | None) -> dict[str, int] | None:
    """Counts of the steps by status (a missing or unknown status is todo); `total` leaves dropped out."""
    if not steps:
        return None
    counts = dict.fromkeys(_STATUSES, 0)
    for value in steps.values():
        status = value.get("status", "todo") if isinstance(value, dict) else "todo"
        # Untyped: a status may be any value (a list, a struct); only a known word counts as itself.
        counts[status if isinstance(status, str) and status in counts else "todo"] += 1
    return {"total": counts["done"] + counts["doing"] + counts["todo"], **counts}


@dataclass(frozen=True)
class _Remembered:
    mtime_ns: int
    size: int
    progress: dict[str, object] | None


@dataclass
class PlanProgressCache:
    """The counts read so far, per catalog, keyed by `plan.cue`'s time and size; lives as long as the server."""

    catalogs: dict[str, dict[str, _Remembered]] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)


def _regular(path: Path) -> os.stat_result | None:
    try:
        info = os.lstat(path)
    except OSError:
        return None
    return info if stat.S_ISREG(info.st_mode) else None


def _is_directory(path: Path) -> bool:
    try:
        return stat.S_ISDIR(os.lstat(path).st_mode)
    except OSError:
        return False


def _at(info: os.stat_result) -> str:
    return datetime.fromtimestamp(info.st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def plan_file(catalog: Path, scope_id: str) -> Path | None:
    try:
        return catalog / Path(*scope_relative(scope_id).parts) / "plan.cue"
    except ValueError:
        return None


def read_plan_progress(
    site: SiteRepository,
    scope_ids: Sequence[str],
    cache: PlanProgressCache,
    *,
    prune: bool = True,
    timeout: float = TIMEOUT,
    clock: Callable[[], float] = time.monotonic,
    steps_reader: StepsReader | None = None,
    cue_locator: CueLocator | None = None,
) -> dict[str, dict[str, object] | None]:
    """`{ID: {total, done, doing, todo, dropped, modified_at} | None}`; never raises.

    With `prune`, the remembered counts of the Scopes not named are dropped (the structure list names every Issue
    in progress); without it (one Scope's detail), only the named ones are added or replaced.
    """
    reader = steps_reader or read_plan_steps
    locate = cue_locator or locate_cue
    found: dict[str, dict[str, object] | None] = dict.fromkeys(scope_ids)
    catalog = site.catalog
    if catalog is None or not _is_directory(catalog):
        return found
    deadline = clock() + timeout
    key = str(catalog)
    with cache.lock:
        old = dict(cache.catalogs.get(key, {}))
    kept: dict[str, _Remembered] = {}
    tool: CueTool | None = None
    no_tool = False
    for scope_id in scope_ids:
        path = plan_file(catalog, scope_id)
        info = _regular(path) if path is not None else None
        if path is None or info is None:
            continue
        remembered = old.get(scope_id)
        if remembered is not None and (remembered.mtime_ns, remembered.size) == (info.st_mtime_ns, info.st_size):
            kept[scope_id] = remembered
            found[scope_id] = remembered.progress
            continue
        left = deadline - clock()
        if no_tool or left <= 0:
            continue
        try:
            if tool is None:
                tool = locate(timeout=left)
                left = deadline - clock()
                if left <= 0:
                    continue
            steps = reader(path.parent, timeout=left, tool=tool)
        except CueToolError:
            no_tool = True
            continue
        except Exception:  # a broken read never takes the structure down (F-01)
            continue
        if steps is None and clock() >= deadline:
            continue  # most likely stopped by the time limit: read again later
        counts = plan_counts(steps)
        progress: dict[str, object] | None = None if counts is None else {**counts, "modified_at": _at(info)}
        kept[scope_id] = _Remembered(info.st_mtime_ns, info.st_size, progress)
        found[scope_id] = progress
    with cache.lock:
        if prune:
            cache.catalogs[key] = kept
        else:
            cache.catalogs[key] = {**cache.catalogs.get(key, {}), **kept}
    return found


def issues_in_progress(model: DashboardModel | None) -> list[str]:
    """The Issues whose state is doing, in ID order: the only ones whose plan is read."""
    if model is None:
        return []
    return sorted(scope.id for scope in model.scopes.values() if scope.kind == "issue" and scope.state == "doing")


def plan_signature(catalog: Path | None, scope_ids: Sequence[str]) -> tuple[tuple[str, int, int] | None, ...] | None:
    """Time and size of each named Scope's `plan.cue` (`lstat` only), for the structure's revision (D-08)."""
    if catalog is None:
        return None
    parts: list[tuple[str, int, int] | None] = []
    for scope_id in scope_ids:
        path = plan_file(catalog, scope_id)
        info = _regular(path) if path is not None else None
        parts.append(None if info is None else (scope_id, info.st_mtime_ns, info.st_size))
    return tuple(parts)
