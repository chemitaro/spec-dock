"""Scope directories in the catalog: always `<catalog>/<ID>`, flat, never searched for (contract C3).

GitHub is the only authority for parents and titles, so a Scope's directory name is its ID and its place is
the catalog root whatever its kind or parent (Epic design ch. 2). Untracked new Scopes are seen too (no
`git ls-files`). Use it only on a catalog reached through a correct link
(`application.canonical_catalog.require_linked`).
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path, PurePosixPath
import re
import stat
from typing import Final, Literal

from spec_dock.runtime.domain.canonical_structure import parse_scope_id, scope_id as canonical_scope_id

# A name that starts like an ID, in any case; at the catalog root it must be exactly one (`iss-00454-foo` is
# pre-migration, `ISS-00454` is not an ID even where the file system ignores case).
SCOPE_NAME_PREFIX: Final = re.compile(r"^(?:init|epic|iss)-[0-9]", re.IGNORECASE)
# Child-layer directories of the retired nested layout, left directly inside a Scope directory.
NESTED_DIRECTORIES: Final = ("epics", "issues")


@dataclass(frozen=True)
class ScopeDirectory:
    scope_id: str
    relative: PurePosixPath
    path: Path


@dataclass(frozen=True)
class MisplacedDirectory:
    relative: PurePosixPath
    reason: Literal["name", "nested"]


def _scope_name(name: str) -> bool:
    try:
        return canonical_scope_id(*parse_scope_id(name)) == name
    except ValueError:
        return False


def _real_directory(path: Path) -> bool:
    try:
        return stat.S_ISDIR(path.lstat().st_mode)
    except FileNotFoundError:
        return False


class CatalogTree:
    def __init__(self, catalog: Path) -> None:
        self.catalog = catalog
        self._directories: tuple[ScopeDirectory, ...] | None = None

    def _children(self) -> list[os.DirEntry[str]]:
        with os.scandir(self.catalog) as entries:
            return sorted(
                (entry for entry in entries if not entry.name.startswith(".") and entry.is_dir(follow_symlinks=False)),
                key=lambda entry: entry.name,
            )

    def directories(self) -> tuple[ScopeDirectory, ...]:
        if self._directories is None:
            self._directories = tuple(
                ScopeDirectory(entry.name, PurePosixPath(entry.name), self.catalog / entry.name)
                for entry in self._children()
                if _scope_name(entry.name)
            )
        return self._directories

    def find(self, scope_id: str) -> ScopeDirectory | None:
        """Look at `<catalog>/<ID>` directly; a name that is not an ID raises ValueError.

        The stored name must be exactly the ID: on a case-insensitive file system `ISS-00454/` would open as
        `iss-00454`, but it is not a Scope directory (the same answer `directories()` gives).
        """
        scope_id = canonical_scope_id(*parse_scope_id(scope_id))
        path = self.catalog / scope_id
        if not _real_directory(path) or scope_id not in {entry.name for entry in self.catalog.iterdir()}:
            return None
        return ScopeDirectory(scope_id, PurePosixPath(scope_id), path)

    def require(self, scope_id: str) -> ScopeDirectory:
        found = self.find(scope_id)
        if found is None:
            raise LookupError(f"{scope_id} has no directory in the catalog")
        return found

    def misplaced(self) -> tuple[MisplacedDirectory, ...]:
        """ID-shaped root names that are not IDs, and `epics/` or `issues/` left right inside a Scope directory."""
        found: list[MisplacedDirectory] = []
        for entry in self._children():
            if _scope_name(entry.name):
                found.extend(
                    MisplacedDirectory(PurePosixPath(entry.name, nested), "nested")
                    for nested in NESTED_DIRECTORIES
                    if _real_directory(Path(entry.path, nested))
                )
            elif SCOPE_NAME_PREFIX.match(entry.name):
                found.append(MisplacedDirectory(PurePosixPath(entry.name), "name"))
        return tuple(sorted(found, key=lambda item: item.relative.as_posix()))
