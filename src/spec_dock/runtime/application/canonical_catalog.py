"""Locate and observe one clone's catalog, guard commands that need it, and write to it (contracts C3, C4).

observe_catalog only reads (Git with --no-optional-locks, no network). require_linked is the first call of
every canonical command that uses the specs; catalog_changes is the only way a command writes the catalog.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
import os
from pathlib import Path
import stat
from typing import TYPE_CHECKING, Literal

from spec_dock.runtime.application.canonical_errors import (
    CANONICAL_FOREIGN_CHECKOUT,
    CANONICAL_FORMAT_UNSUPPORTED,
    CANONICAL_GIT_TOO_OLD,
    CANONICAL_INSIDE_CATALOG,
    CANONICAL_LOCK_BUSY,
    CANONICAL_NOT_LINKED,
    CANONICAL_NOT_LINKED_RECOVERY,
    CANONICAL_UNSUPPORTED_LAYOUT,
    FOREIGN_CHECKOUT_RECOVERY,
    FORMAT_MISSING_RECOVERY,
    FORMAT_UNSUPPORTED_RECOVERY,
    GIT_TOO_OLD_RECOVERY,
    INSIDE_CATALOG_RECOVERY,
    LOCK_BUSY_RECOVERY,
    UNSUPPORTED_LAYOUT_RECOVERY,
    CanonicalCommandError,
)
from spec_dock.runtime.domain.canonical_changeset import Changeset, normalize_catalog_path
from spec_dock.runtime.domain.canonical_content import FORMAT_FILE, format_writable, read_format
from spec_dock.runtime.domain.canonical_layout import (
    CANONICAL_BRANCH,
    EXCLUDE_LINES,
    GITIGNORE_LINES,
    CatalogLayout,
    LinkObservation,
    LinkState,
    link_state,
    missing_lines,
)
from spec_dock.runtime.domain.canonical_structure import format_timestamp
from spec_dock.runtime.infra import canonical_git, runtime_environment
from spec_dock.runtime.infra.canonical_files import count_entries, observe_link, read_text_file
from spec_dock.runtime.infra.catalog_lock import CatalogLock, CatalogLockBusy
from spec_dock.runtime.infra.catalog_runtime import staging_directory, write_changeset
from spec_dock.runtime.infra.catalog_tree import CatalogTree

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    from spec_dock.runtime.application.contracts import GitWorktreeRecord
    from spec_dock.runtime.application.project_context import GitContext, ProjectContext
    from spec_dock.runtime.domain.canonical_changeset import ChangesetOrigin
    from spec_dock.runtime.infra.runtime_environment import RuntimeEnvironment

CatalogState = Literal["ready", "repair", "readd", "absent", "occupied", "elsewhere", "foreign"]


def resolve_layout(context: GitContext) -> CatalogLayout:
    """The main checkout is the parent of a common directory named .git that is that parent's own .git."""
    common = context.common_dir
    marker = common.parent / ".git"
    if common.name != ".git" or not marker.is_dir() or marker.is_symlink() or marker.resolve() != common:
        raise CanonicalCommandError(
            CANONICAL_UNSUPPORTED_LAYOUT,
            f"this clone has no main checkout holding its .git directory ({common})",
            recovery=(UNSUPPORTED_LAYOUT_RECOVERY,),
            details={"common_dir": str(common)},
        )
    return CatalogLayout(common.parent, common, context.root)


@dataclass(frozen=True)
class LinkView:
    checkout: Path
    observed: LinkObservation
    state: LinkState
    expected: str

    def __iter__(self) -> Iterator[object]:
        return iter((self.checkout, self.observed, self.state, self.expected))


@dataclass(frozen=True)
class CatalogObservation:
    layout: CatalogLayout
    state: CatalogState
    registered: GitWorktreeRecord | None
    locked: bool
    moved: bool
    gitdir: Path | None
    entries: int | None
    links: tuple[LinkView, ...]
    exclude_missing: tuple[str, ...]
    gitignore_missing: tuple[str, ...]
    detail: str | None = None
    registered_exists: bool | None = None
    off_branch: str | None = None

    def link_for(self, checkout: Path) -> LinkView:
        return next(view for view in self.links if view.checkout == checkout)


def observe_catalog(layout: CatalogLayout, environment: RuntimeEnvironment, *, timeout: float) -> CatalogObservation:
    records = tuple(
        record
        for record in canonical_git.list_worktrees(layout.main_checkout, timeout=timeout)
        if record.branch == CANONICAL_BRANCH
    )
    catalog = layout.catalog
    fields = _catalog_fields(layout, records, environment)
    catalog_real = Path(os.path.realpath(catalog)) if fields["state"] in ("ready", "repair", "foreign") else None
    links = []
    for checkout in layout.checkouts:
        observed = observe_link(layout.link_path(checkout))
        expected = layout.link_text(checkout)
        links.append(
            LinkView(checkout, observed, link_state(observed, expected_text=expected, catalog=catalog_real), expected)
        )
    return CatalogObservation(
        layout=layout,
        links=tuple(links),
        exclude_missing=missing_lines(read_text_file(layout.common_dir / "info/exclude"), EXCLUDE_LINES),
        gitignore_missing=missing_lines(read_text_file(layout.checkout / "spec-dock/.gitignore"), GITIGNORE_LINES),
        **fields,  # type: ignore[arg-type]
    )


def _catalog_fields(
    layout: CatalogLayout, records: tuple[GitWorktreeRecord, ...], environment: RuntimeEnvironment
) -> dict[str, object]:
    catalog = layout.catalog
    base: dict[str, object] = {"registered": None, "locked": False, "moved": False, "gitdir": None, "entries": None}
    kind = _entry_kind(catalog)
    if kind == "absent":
        if not records:
            return {**base, "state": "absent"}
        if len(records) == 1 and _same_place(records[0].path, catalog):
            return {**base, "state": "readd", "registered": records[0], "locked": records[0].locked}
        other = next((record for record in records if not _same_place(record.path, catalog)), records[0])
        return _elsewhere(base, other)
    if kind != "directory":
        return {**base, "state": "occupied", "detail": f"{catalog} is not a directory"}
    gitdir = canonical_git.read_gitdir(catalog)
    admin = layout.common_dir / "worktrees" / gitdir.name if gitdir is not None else None
    if gitdir is None or admin is None or not (admin / "HEAD").is_file():
        return {
            **base,
            "state": "occupied",
            "entries": count_entries(catalog),
            "detail": f"{catalog} is not this clone's catalog",
        }
    gitdir_visible = gitdir.exists()
    gitdir_ok = gitdir_visible and Path(gitdir).samefile(admin)
    if gitdir_visible and not gitdir_ok:
        return {
            **base,
            "state": "occupied",
            "entries": count_entries(catalog),
            "detail": f"{catalog} belongs to another repository ({gitdir})",
        }
    branch = canonical_git.admin_branch(admin)
    if branch != CANONICAL_BRANCH:
        return {
            **base,
            "state": "occupied",
            "gitdir": gitdir,
            "off_branch": branch or "a detached HEAD",
            "detail": f"the catalog has {branch or 'a detached HEAD'} checked out instead of {CANONICAL_BRANCH}",
        }
    registered_path = canonical_git.admin_worktree_path(admin)
    registered = next((record for record in records if record.path == registered_path), None)
    fields = {**base, "registered": registered, "locked": (admin / "locked").exists(), "gitdir": gitdir}
    others = tuple(record for record in records if record.path != registered_path)
    if others:
        return _elsewhere(fields, others[0])
    registered_visible = registered_path is not None and registered_path.exists()
    same_registration = registered_path is not None and registered_visible and registered_path.samefile(catalog)
    if same_registration and gitdir_ok:
        return {**fields, "state": "ready"}
    if registered_visible and not same_registration:
        return {
            **fields,
            "state": "occupied",
            "entries": count_entries(catalog),
            "detail": f"the catalog's Git registration points to another existing directory ({registered_path})",
        }
    # Some recorded path is not visible from this process: a moved main checkout, or a mount elsewhere.
    if environment.container:
        return {
            **fields,
            "state": "foreign",
            "detail": f"the catalog's Git registration is not visible here ({gitdir})",
        }
    return {**fields, "state": "repair", "moved": not registered_visible}


def _entry_kind(path: Path) -> str:
    """absent only for ENOENT; a permission failure is raised instead of being taken for a missing catalog."""
    try:
        observed = path.lstat()
    except FileNotFoundError:
        return "absent"
    if stat.S_ISLNK(observed.st_mode):
        return "symlink"
    return "directory" if stat.S_ISDIR(observed.st_mode) else "other"


def _same_place(registered: Path, catalog: Path) -> bool:
    """A missing catalog's registration matches when it names the same entry in the same real directory."""
    return registered.name == catalog.name and os.path.realpath(registered.parent) == os.path.realpath(catalog.parent)


def _elsewhere(fields: dict[str, object], other: GitWorktreeRecord) -> dict[str, object]:
    return {
        **fields,
        "state": "elsewhere",
        "registered": other,
        "registered_exists": os.path.lexists(other.path),
        "detail": f"spec-dock/canonical is checked out at {other.path}",
    }


def inside_catalog(project: str | None, cwd: Path, *, timeout: float) -> Path | None:
    """The catalog root when the command runs inside a catalog worktree (it has no workspace declaration)."""
    candidate = Path(project).expanduser() if project else cwd
    if not candidate.is_absolute():
        candidate = cwd / candidate
    try:
        top = Path(
            os.fsdecode(
                canonical_git.run_catalog_git(
                    candidate, "rev-parse", "--show-toplevel", read_only=True, timeout=timeout
                ).stdout
            ).strip()
        )
        branch = canonical_git.run_catalog_git(
            top,
            "symbolic-ref",
            "--quiet",
            "--short",
            "HEAD",
            read_only=True,
            timeout=timeout,
            returncodes=frozenset({0, 1}),
        )
    except (OSError, canonical_git.GitProcessError):
        return None
    if os.fsdecode(branch.stdout).strip() != CANONICAL_BRANCH or not (top / FORMAT_FILE).is_file():
        return None
    return top


def inside_catalog_error(catalog: Path) -> CanonicalCommandError:
    return CanonicalCommandError(
        CANONICAL_INSIDE_CATALOG,
        f"this command ran inside the catalog worktree {catalog}, which has no workspace declaration",
        recovery=(INSIDE_CATALOG_RECOVERY,),
        details={"catalog": str(catalog), "next_step": INSIDE_CATALOG_RECOVERY},
    )


@dataclass(frozen=True)
class LinkedCatalog:
    layout: CatalogLayout
    catalog: Path
    tree: CatalogTree


def require_git(environment: RuntimeEnvironment) -> None:
    if not environment.git.supported:
        found = environment.git.reported or "no git on PATH"
        raise CanonicalCommandError(
            CANONICAL_GIT_TOO_OLD,
            f"canonical mode needs Git 2.38 or later for merge-tree --write-tree; found {found}",
            recovery=(GIT_TOO_OLD_RECOVERY,),
            details={"git": environment.git.path, "version": environment.git.reported},
        )


def foreign_error(observation: CatalogObservation) -> CanonicalCommandError:
    return CanonicalCommandError(
        CANONICAL_FOREIGN_CHECKOUT,
        f"this checkout looks mounted from another machine; {observation.detail}",
        recovery=(FOREIGN_CHECKOUT_RECOVERY,),
        details={"catalog": str(observation.layout.catalog), "gitdir": str(observation.gitdir)},
    )


def require_linked(
    context: ProjectContext, *, environment: RuntimeEnvironment | None = None, timeout: float = 30.0
) -> LinkedCatalog:
    """Stop without writing unless this checkout's link and the catalog are correct (R-B5)."""
    current = environment or runtime_environment.detect_runtime_environment()
    require_git(current)
    layout = resolve_layout(context)
    observation = observe_catalog(layout, current, timeout=timeout)
    if observation.state == "foreign":
        raise foreign_error(observation)
    link = observation.link_for(layout.checkout)
    if observation.state != "ready" or link.state != "correct":
        raise CanonicalCommandError(
            CANONICAL_NOT_LINKED,
            f"spec-dock/initiatives is not linked to this clone's catalog (catalog {observation.state}, link {link.state})",
            recovery=(CANONICAL_NOT_LINKED_RECOVERY,),
            details={
                "catalog_state": observation.state,
                "link_state": link.state,
                "next_step": CANONICAL_NOT_LINKED_RECOVERY,
            },
        )
    catalog = Path(os.path.realpath(layout.catalog))
    return LinkedCatalog(layout, catalog, CatalogTree(catalog))


@dataclass
class CatalogChanges:
    catalog: Path
    paths: list[str] = field(default_factory=list)
    deletions: list[str] = field(default_factory=list)
    written: Path | None = None

    def add(self, path: str | os.PathLike[str]) -> None:
        self.paths.append(normalize_catalog_path(os.fspath(path)))

    def delete(self, path: str | os.PathLike[str]) -> None:
        self.deletions.append(normalize_catalog_path(os.fspath(path)))

    def staging(self) -> Path:
        return staging_directory(self.catalog)


@contextmanager
def catalog_changes(
    catalog: Path,
    *,
    command: str,
    origin: ChangesetOrigin = "command",
    timeout: float = 10.0,
    clock: Callable[[], datetime] | None = None,
) -> Iterator[CatalogChanges]:
    """Hold the catalog lock, refuse an unknown format before writing, and leave one changeset for sync."""
    try:
        lock = CatalogLock(catalog, timeout=timeout).__enter__()
    except CatalogLockBusy as error:
        raise CanonicalCommandError(
            CANONICAL_LOCK_BUSY, str(error), recovery=(LOCK_BUSY_RECOVERY,), details={"catalog": str(catalog)}
        ) from error
    try:
        try:
            version = read_format((catalog / FORMAT_FILE).read_bytes())
        except FileNotFoundError:
            version = None
        if not format_writable(version):
            raise CanonicalCommandError(
                CANONICAL_FORMAT_UNSUPPORTED,
                f"the catalog declares canonical format {version!r}; this SpecDock writes format 1",
                recovery=(FORMAT_MISSING_RECOVERY if version is None else FORMAT_UNSUPPORTED_RECOVERY,),
                details={"catalog": str(catalog), "format": version},
            )
        changes = CatalogChanges(catalog)
        try:
            yield changes
        finally:
            if changes.paths or changes.deletions:
                created = (clock or (lambda: datetime.now(timezone.utc)))()
                changeset = Changeset(
                    origin, command, format_timestamp(created), tuple(changes.paths), tuple(changes.deletions)
                )
                changes.written = write_changeset(catalog, changeset)
    finally:
        lock.__exit__(None, None, None)
