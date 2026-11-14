"""What a Scope's detail screen reads beside the snapshot (iss-00531 D-03).

The catalog's documents and Artifacts, the assurance level of `requirement.cue` and the worktrees on this PC
whose branch names the Scope. Everything is read only; every part that fails (a missing catalog, a slow or
broken `cue`, a failing `git worktree list`) becomes that part's "unreadable" and the rest still shows
(iss-00531 F-03). External processes run with a short time limit because this runs on every request.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import os
from pathlib import Path
import stat
import threading
import time
from typing import TYPE_CHECKING, Final, Literal, Protocol
from urllib.parse import quote

from spec_dock.runtime.application.scope_check import read_assurance
from spec_dock.runtime.domain.canonical_layout import scope_relative
from spec_dock.runtime.domain.canonical_structure import branch_names_scope
from spec_dock.runtime.domain.explanation_shape import SKELETON_MARKER
from spec_dock.runtime.infra.cue_tool import CueToolError, locate_cue
from spec_dock.runtime.infra.git_cli import worktree_list

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from spec_dock.runtime.application.contracts import GitWorktreeRecord
    from spec_dock.runtime.application.dashboard_site import SiteRepository
    from spec_dock.runtime.application.scope_check import AssuranceReading
    from spec_dock.runtime.infra.cue_tool import CueTool

TIMEOUT: Final = 3.0
ARTIFACT_LIMIT: Final = 300
# (key, names in order of preference): a CUE Scope's files first, then an older Markdown Scope's.
DOCUMENTS: Final = (
    ("requirement", ("requirement.cue", "requirement.md")),
    ("design", ("design.cue", "design.md")),
    ("plan", ("plan.cue", "plan.md")),
    ("explanation", ("explanation.html",)),
    ("report", ("report.md",)),
)
_LINKED: Final = frozenset({"explanation"})  # documents the screen opens in a new tab (served isolated)


class AssuranceReader(Protocol):
    def __call__(self, directory: Path | None, *, timeout: float) -> AssuranceReading: ...


class WorktreeLister(Protocol):
    def __call__(self, repo_root: Path, *, timeout: float) -> list[GitWorktreeRecord]: ...


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


def _files_path(site: SiteRepository, scope_id: str, *parts: str) -> str:
    return f"/r/{site.key}/files/{scope_id}/" + "/".join(quote(part, safe="") for part in parts)


def _documents(site: SiteRepository, scope_id: str, directory: Path) -> list[dict[str, object]]:
    found: list[dict[str, object]] = []
    for key, names in DOCUMENTS:
        name = next((item for item in names if _regular(directory / item) is not None), None)
        exists = name is not None
        shown = name or names[0]
        href = _files_path(site, scope_id, shown) if exists and key in _LINKED else None
        document: dict[str, object] = {"key": key, "name": shown, "exists": exists, "href": href}
        if key == "explanation":
            document["skeleton"] = _explanation_skeleton(directory / shown) if exists else None
        found.append(document)
    return found


def _explanation_skeleton(path: Path) -> bool | None:
    try:
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0))
        with os.fdopen(descriptor, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                return None
            return SKELETON_MARKER.encode("utf-8") in stream.read(256 * 1024)
    except OSError:
        return None


def _artifacts(
    site: SiteRepository, scope_id: str, directory: Path, limit: int
) -> tuple[list[dict[str, object]], bool]:
    folder = directory / "artifacts"
    if not _is_directory(folder):
        return [], False
    try:
        names = sorted(item.name for item in os.scandir(folder))
    except OSError:
        return [], False
    items: list[dict[str, object]] = []
    for name in names:
        if name.startswith("."):
            continue
        info = _regular(folder / name)
        if info is None:
            continue  # links (rules.md) and directories are not served as materials
        if len(items) == limit:
            return items, True
        modified = datetime.fromtimestamp(info.st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        items.append({
            "name": name,
            "size": info.st_size,
            "modified_at": modified,
            "html": name.lower().endswith((".html", ".htm")),
            "href": _files_path(site, scope_id, "artifacts", name),
        })
    return items, False


def _assurance(directory: Path, reader: AssuranceReader, timeout: float) -> dict[str, object]:
    if _regular(directory / "requirement.cue") is None:
        return {"level": None, "source": "unset", "problem": None}
    try:
        reading = reader(directory, timeout=timeout)
    except Exception as error:  # a slow or broken cue never takes the screen down (F-03)
        return {"level": None, "source": "unreadable", "problem": f"{type(error).__name__}: {error}"}
    problem = None if reading.problem is None else reading.problem.message
    return {"level": reading.level, "source": reading.source, "problem": problem}


def _worktrees(catalog: Path | None, scope_id: str, lister: WorktreeLister, timeout: float) -> dict[str, object]:
    if catalog is None or not _is_directory(catalog):
        return {"status": "unreadable", "items": []}
    try:
        records = lister(catalog, timeout=timeout)
    except Exception:  # git missing, slow or failing: only this field is unknown (F-03)
        return {"status": "unreadable", "items": []}
    items = [
        {"path": str(record.path), "branch": record.branch}
        for record in records
        if record.branch is not None and branch_names_scope(record.branch, scope_id)
    ]
    return {"status": "ok", "items": items}


def read_scope_details(
    site: SiteRepository,
    scope_id: str,
    *,
    timeout: float = TIMEOUT,
    artifact_limit: int = ARTIFACT_LIMIT,
    assurance_reader: AssuranceReader | None = None,
    worktree_lister: WorktreeLister | None = None,
) -> dict[str, object]:
    """The `details` of the Scope JSON; never raises for missing or unreadable files."""
    assurance_reader = assurance_reader or read_assurance
    worktree_lister = worktree_lister or worktree_list
    catalog = site.catalog
    worktrees = _worktrees(catalog, scope_id, worktree_lister, timeout)
    empty: dict[str, object] = {
        "documents": [],
        "artifacts": [],
        "artifacts_truncated": False,
        "assurance": {"level": None, "source": "unreadable", "problem": None},
        "worktrees": worktrees,
    }
    if catalog is None:
        return {
            "catalog": "ambiguous",
            "next_steps": ["spec-dock dashboard list", "spec-dock canonical remove"],
            **empty,
        }
    if not _is_directory(catalog):
        return {"catalog": "missing", "next_steps": ["spec-dock canonical link", "spec-dock canonical status"], **empty}
    try:
        directory = catalog / Path(*scope_relative(scope_id).parts)
    except ValueError:
        directory = None
    if directory is None or not _is_directory(directory):
        return {
            "catalog": "scope_missing",
            "next_steps": ["spec-dock canonical status", "spec-dock canonical link"],
            **empty,
        }
    artifacts, truncated = _artifacts(site, scope_id, directory, artifact_limit)
    return {
        "catalog": "ok",
        "next_steps": [],
        "documents": _documents(site, scope_id, directory),
        "artifacts": artifacts,
        "artifacts_truncated": truncated,
        "assurance": _assurance(directory, assurance_reader, timeout),
        "worktrees": worktrees,
    }


def scope_facts(details: dict[str, object]) -> dict[str, object]:
    """The structure fields `assurance` and `branch` of one Scope, from its details (iss-00544 D-02)."""
    assurance = details.get("assurance")
    worktrees = details.get("worktrees")
    level = assurance.get("level") if isinstance(assurance, dict) else None
    items = worktrees.get("items") if isinstance(worktrees, dict) else None
    branch = items[0].get("branch") if isinstance(items, list) and items and isinstance(items[0], dict) else None
    return {
        "assurance": level if isinstance(level, str) else None,
        "branch": branch if isinstance(branch, str) else None,
        "worktrees": items if isinstance(items, list) else [],
    }


# --- The structure list: every Scope's assurance level and this PC's branch (iss-00544 D-02) -------------------


class StructureAssuranceReader(Protocol):
    def __call__(self, directory: Path | None, *, timeout: float, tool: CueTool | None = None) -> AssuranceReading: ...


class CueLocator(Protocol):
    def __call__(self, *, timeout: float) -> CueTool: ...


@dataclass(frozen=True)
class _Remembered:
    mtime_ns: int
    size: int
    level: str | None


@dataclass
class StructureFactsCache:
    """The assurance levels read so far, per catalog, keyed by `requirement.cue`'s time and size.

    It lives as long as the server process and is never written anywhere. Requests are served in parallel, so the
    table of a catalog is read and replaced under the lock; the external processes run outside it.
    """

    catalogs: dict[str, dict[str, _Remembered]] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)


@dataclass(frozen=True)
class StructureFacts:
    """Scope readings and the clone-wide inventory, from one worktree listing."""

    readings: dict[str, dict[str, object]]
    worktrees_status: Literal["ok", "unreadable"] = "unreadable"
    paths: tuple[str, ...] = ()


def read_structure_facts(
    site: SiteRepository,
    scope_ids: Sequence[str],
    cache: StructureFactsCache,
    *,
    timeout: float = TIMEOUT,
    clock: Callable[[], float] = time.monotonic,
    assurance_reader: StructureAssuranceReader | None = None,
    worktree_lister: WorktreeLister | None = None,
    cue_locator: CueLocator | None = None,
) -> StructureFacts:
    """Scope assurance/branch/worktree readings and clone-wide paths; unknown scalar values are None.

    `git worktree list` runs once. A level is read with `cue` only when `requirement.cue`'s time or size changed;
    the external processes of one request share `timeout`. Past it, levels stay None and unremembered, so a later
    request reads them (F-02).
    """
    reader = assurance_reader or read_assurance
    lister = worktree_lister or worktree_list
    locate = cue_locator or locate_cue
    facts: dict[str, dict[str, object]] = {
        item: {"assurance": None, "branch": None, "worktrees": []} for item in scope_ids
    }
    catalog = site.catalog
    if catalog is None or not _is_directory(catalog):
        return StructureFacts(facts)
    deadline = clock() + timeout
    status: Literal["ok", "unreadable"] = "ok"
    try:
        records = lister(catalog, timeout=timeout)
    except Exception:  # an unavailable inventory never supplies matching hints
        records, status = [], "unreadable"
    paths = tuple(str(record.path) for record in records)
    for scope_id in scope_ids:
        items = [
            {"path": str(record.path), "branch": record.branch}
            for record in records
            if record.branch is not None and branch_names_scope(record.branch, scope_id)
        ]
        facts[scope_id]["worktrees"] = items
        facts[scope_id]["branch"] = items[0]["branch"] if items else None
    key = str(catalog)
    with cache.lock:
        old = dict(cache.catalogs.get(key, {}))
    kept: dict[str, _Remembered] = {}
    tool: CueTool | None = None
    no_tool = False
    for scope_id in scope_ids:
        try:
            directory = catalog / Path(*scope_relative(scope_id).parts)
        except ValueError:
            continue
        info = _regular(directory / "requirement.cue")
        if info is None:
            continue  # a Markdown Scope, or none in the catalog: no level
        remembered = old.get(scope_id)
        if remembered is not None and (remembered.mtime_ns, remembered.size) == (info.st_mtime_ns, info.st_size):
            kept[scope_id] = remembered
            facts[scope_id]["assurance"] = remembered.level
            continue
        left = deadline - clock()
        if no_tool or left <= 0:
            continue  # no cue, or past the limit: None now, read on a later request (F-02)
        try:
            if tool is None:
                tool = locate(timeout=left)
                left = deadline - clock()
                if left <= 0:
                    continue
            reading = reader(directory, timeout=left, tool=tool)
        except CueToolError:
            no_tool = True
            continue
        except Exception:  # a broken read never takes the structure down (F-01)
            continue
        level = reading.level if reading.source == "cue" else None
        if level is None and clock() >= deadline:
            continue  # most likely stopped by the time limit: read again later
        kept[scope_id] = _Remembered(info.st_mtime_ns, info.st_size, level)
        facts[scope_id]["assurance"] = level
    with cache.lock:
        cache.catalogs[key] = kept
    return StructureFacts(facts, status, paths)
