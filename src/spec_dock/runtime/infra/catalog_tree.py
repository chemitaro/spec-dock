"""Scope directories in the catalog: always `<catalog>/<bucket>/<ID>`, flat, never searched for (contract C3).

GitHub is the only authority for parents and titles, so a Scope's directory name is its ID and its place is its
number's thousand bucket whatever its kind or parent (Epic design ch. 2, `canonical_layout.scope_relative`).
Untracked new Scopes are seen too (no `git ls-files`). Use it only on a catalog reached through a correct link
(`application.canonical_catalog.require_linked`).
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path, PurePosixPath
import re
import stat
from typing import Final, Literal

from spec_dock.runtime.domain.canonical_layout import BUCKET_NAME_SHAPE, is_bucket_name, scope_relative
from spec_dock.runtime.domain.canonical_structure import parse_scope_id, scope_id as canonical_scope_id

# A name that starts like an ID, in any case; in a bucket it must be exactly one (`iss-00454-foo` is
# pre-migration, `ISS-00454` is not an ID even where the file system ignores case).
SCOPE_NAME_PREFIX: Final = re.compile(r"^(?:init|epic|iss)-[0-9]", re.IGNORECASE)
# Child-layer directories of the retired nested layout, left directly inside a Scope directory.
NESTED_DIRECTORIES: Final = ("epics", "issues")

# root: an ID-shaped name at the catalog root; bucket: a wrong bucket name or an ID in another number's bucket;
# name: an ID-shaped name in a bucket that is not an ID; nested: epics/ or issues/ inside a Scope directory.
MisplacedReason = Literal["root", "bucket", "name", "nested"]


@dataclass(frozen=True)
class ScopeDirectory:
    scope_id: str
    relative: PurePosixPath
    path: Path


@dataclass(frozen=True)
class MisplacedDirectory:
    relative: PurePosixPath
    reason: MisplacedReason
    expected: PurePosixPath | None = None  # where it belongs, when its name is an ID


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


def _children(directory: Path) -> list[os.DirEntry[str]]:
    with os.scandir(directory) as entries:
        return sorted(
            (entry for entry in entries if not entry.name.startswith(".") and entry.is_dir(follow_symlinks=False)),
            key=lambda entry: entry.name,
        )


class CatalogTree:
    def __init__(self, catalog: Path) -> None:
        self.catalog = catalog
        self._directories: tuple[ScopeDirectory, ...] | None = None

    def _buckets(self) -> list[os.DirEntry[str]]:
        return [entry for entry in _children(self.catalog) if is_bucket_name(entry.name)]

    def directories(self) -> tuple[ScopeDirectory, ...]:
        if self._directories is None:
            self._directories = tuple(
                ScopeDirectory(entry.name, PurePosixPath(bucket.name, entry.name), Path(entry.path))
                for bucket in self._buckets()
                for entry in _children(Path(bucket.path))
                if _scope_name(entry.name) and scope_relative(entry.name) == PurePosixPath(bucket.name, entry.name)
            )
        return self._directories

    def find(self, scope_id: str) -> ScopeDirectory | None:
        """Look at `<catalog>/<bucket>/<ID>` directly; a name that is not an ID raises ValueError.

        The stored names must be exactly the bucket and the ID: on a case-insensitive file system `ISS-00454/`
        would open as `iss-00454`, but it is not a Scope directory (the same answer `directories()` gives).
        """
        scope_id = canonical_scope_id(*parse_scope_id(scope_id))
        relative = scope_relative(scope_id)
        bucket = self.catalog / relative.parent.name
        path = bucket / scope_id
        if not _real_directory(bucket) or not _real_directory(path):
            return None
        if scope_id not in {entry.name for entry in bucket.iterdir()}:
            return None
        return ScopeDirectory(scope_id, relative, path)

    def require(self, scope_id: str) -> ScopeDirectory:
        found = self.find(scope_id)
        if found is None:
            raise LookupError(f"{scope_id} has no directory in the catalog")
        return found

    def misplaced(self) -> tuple[MisplacedDirectory, ...]:
        """Scope-like directories outside their bucket, and `epics/` or `issues/` left inside a Scope directory."""
        found: list[MisplacedDirectory] = []
        for entry in _children(self.catalog):
            name = PurePosixPath(entry.name)
            if is_bucket_name(entry.name):
                found.extend(self._misplaced_in(entry))
            elif SCOPE_NAME_PREFIX.match(entry.name):
                found.append(
                    MisplacedDirectory(name, "root", scope_relative(entry.name) if _scope_name(entry.name) else None)
                )
            elif BUCKET_NAME_SHAPE.match(entry.name):
                found.append(MisplacedDirectory(name, "bucket"))
        return tuple(sorted(found, key=lambda item: item.relative.as_posix()))

    @staticmethod
    def _misplaced_in(bucket: os.DirEntry[str]) -> list[MisplacedDirectory]:
        found: list[MisplacedDirectory] = []
        for entry in _children(Path(bucket.path)):
            relative = PurePosixPath(bucket.name, entry.name)
            if _scope_name(entry.name):
                expected = scope_relative(entry.name)
                if expected != relative:
                    found.append(MisplacedDirectory(relative, "bucket", expected))
                    continue
                found.extend(
                    MisplacedDirectory(relative / nested, "nested")
                    for nested in NESTED_DIRECTORIES
                    if _real_directory(Path(entry.path, nested))
                )
            elif SCOPE_NAME_PREFIX.match(entry.name):
                found.append(MisplacedDirectory(relative, "name"))
        return found
