"""What a Scope's detail screen reads beside the snapshot (iss-00531 D-03).

The catalog's documents and Artifacts, the assurance level of `requirement.cue` and the worktrees on this PC
whose branch names the Scope. Everything is read only; every part that fails (a missing catalog, a slow or
broken `cue`, a failing `git worktree list`) becomes that part's "unreadable" and the rest still shows
(iss-00531 F-03). External processes run with a short time limit because this runs on every request.
"""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import stat
from typing import TYPE_CHECKING, Final, Protocol
from urllib.parse import quote

from spec_dock.runtime.application.scope_check import read_assurance
from spec_dock.runtime.domain.canonical_layout import scope_relative
from spec_dock.runtime.domain.canonical_structure import branch_names_scope
from spec_dock.runtime.infra.git_cli import worktree_list

if TYPE_CHECKING:
    from spec_dock.runtime.application.contracts import GitWorktreeRecord
    from spec_dock.runtime.application.dashboard_site import SiteRepository
    from spec_dock.runtime.application.scope_check import AssuranceReading

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
        found.append({"key": key, "name": shown, "exists": exists, "href": href})
    return found


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
    assurance_reader: AssuranceReader = read_assurance,
    worktree_lister: WorktreeLister = worktree_list,
) -> dict[str, object]:
    """The `details` of the Scope JSON; never raises for missing or unreadable files."""
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
