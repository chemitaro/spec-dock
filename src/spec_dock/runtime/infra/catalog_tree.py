"""Find Scope directories in the catalog by name, not by nesting position (contract C3).

GitHub is the structure's authority; the directory nesting is only a view of it, so commands keep working
when the two drift. Untracked new Scopes are found too (no `git ls-files`). Use it only on a catalog reached
through a correct link (`application.canonical_catalog.require_linked`).
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path, PurePosixPath
import re
from typing import TYPE_CHECKING, Final

from spec_dock.runtime.domain.canonical_structure import parse_scope_id, scope_id as canonical_scope_id
from spec_dock.runtime.domain.ids import INPUT_SLUG_KEBAB_RE

if TYPE_CHECKING:
    from collections.abc import Mapping

SCOPE_DIRECTORY_NAME: Final = re.compile(r"^((?:init|epic|iss)-[0-9]{5,})-([a-z0-9]+(?:-[a-z0-9]+)*)$")


@dataclass(frozen=True)
class ScopeDirectory:
    scope_id: str
    relative: PurePosixPath
    path: Path


class ScopeDirectoryAmbiguous(ValueError):
    """Two directories claim one Scope ID: a precondition failure (PRECONDITION_FAILED), not a missing Scope."""

    def __init__(self, scope_id: str, matches: tuple[ScopeDirectory, ...]) -> None:
        self.scope_id = scope_id
        self.matches = matches
        listed = ", ".join(str(match.relative) for match in matches)
        super().__init__(f"{scope_id} has more than one directory in the catalog: {listed}")


class CatalogTree:
    def __init__(self, catalog: Path) -> None:
        self.catalog = catalog
        self._directories: tuple[ScopeDirectory, ...] | None = None

    def directories(self) -> tuple[ScopeDirectory, ...]:
        if self._directories is None:
            found: list[ScopeDirectory] = []
            self._walk(self.catalog, PurePosixPath(), found)
            self._directories = tuple(sorted(found, key=lambda item: item.relative.as_posix()))
        return self._directories

    def _walk(self, directory: Path, relative: PurePosixPath, found: list[ScopeDirectory]) -> None:
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.name.startswith(".") or not entry.is_dir(follow_symlinks=False):
                    continue
                child = relative / entry.name
                matched = SCOPE_DIRECTORY_NAME.fullmatch(entry.name)
                if matched is not None and INPUT_SLUG_KEBAB_RE.fullmatch(matched.group(2)):
                    found.append(ScopeDirectory(matched.group(1), child, self.catalog / child))
                self._walk(Path(entry.path), child, found)

    def find(self, scope_id: str) -> ScopeDirectory | None:
        scope_id = canonical_scope_id(*parse_scope_id(scope_id))
        matches = tuple(item for item in self.directories() if item.scope_id == scope_id)
        if len(matches) > 1:
            raise ScopeDirectoryAmbiguous(scope_id, matches)
        return matches[0] if matches else None

    def require(self, scope_id: str) -> ScopeDirectory:
        found = self.find(scope_id)
        if found is None:
            raise LookupError(f"{scope_id} has no directory in the catalog")
        return found

    def duplicates(self) -> Mapping[str, tuple[ScopeDirectory, ...]]:
        grouped: dict[str, list[ScopeDirectory]] = {}
        for item in self.directories():
            grouped.setdefault(item.scope_id, []).append(item)
        return {scope_id: tuple(items) for scope_id, items in grouped.items() if len(items) > 1}
