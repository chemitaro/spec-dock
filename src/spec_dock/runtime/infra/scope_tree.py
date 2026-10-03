"""Schema-3 metadata only; never inspect Workbench, cache or old runtime records."""

from __future__ import annotations

from dataclasses import dataclass
import os
import re
import stat
from typing import TYPE_CHECKING

from spec_dock.runtime.domain.ids import parse_id
from spec_dock.runtime.domain.lifecycle import decode_scope_metadata
from spec_dock.runtime.domain.writer_admission import require_scope_structure
from spec_dock.runtime.infra.git_process import run_git
from spec_dock.runtime.infra.json_store import read_guarded_json

if TYPE_CHECKING:
    from pathlib import Path

    from spec_dock.runtime.domain.lifecycle import ScopeMetadata

_PREFIXES = {"initiative": "init", "epic": "epic", "issue": "iss"}


@dataclass(frozen=True)
class StoredScope:
    path: Path
    metadata: ScopeMetadata


class ScopeIdentityConflict(ValueError):
    def __init__(self, message: str, paths: tuple[Path, Path]) -> None:
        self.paths = paths
        super().__init__(message)


def load_scope_tree(
    specdock_dir: Path, *, target_id: str | None = None, timeout: float = 30
) -> tuple[StoredScope, ...]:
    rows: list[StoredScope] = []
    identities: dict[str, Path] = {}
    linkages: dict[tuple[str, str, int], Path] = {}
    selected_children = (
        {path.parent: path for path in _selected_paths(specdock_dir, target_id, timeout=timeout)}
        if target_id is not None
        else None
    )

    def walk(container: Path, kind: str, chain: tuple[str, ...]) -> None:
        if selected_children is not None and container not in selected_children:
            return
        try:
            mode = container.lstat().st_mode
        except FileNotFoundError:
            return
        if not stat.S_ISDIR(mode):
            raise ValueError("Scope container is redirected or not a directory")
        pattern = re.compile(rf"{_PREFIXES[kind]}(?:-local)?-[0-9]+-[a-z0-9]+(?:-[a-z0-9]+)*\Z")
        directories = (selected_children[container],) if selected_children is not None else sorted(container.iterdir())
        for directory in directories:
            if not pattern.fullmatch(directory.name):
                continue
            if not stat.S_ISDIR(directory.lstat().st_mode):
                raise ValueError("Scope path is redirected or not a directory")
            loaded = read_guarded_json(directory / ".meta.json")
            if loaded is None or not isinstance(loaded[0], dict):
                raise ValueError("Scope metadata is missing or invalid")
            require_scope_structure(loaded[0])
            metadata = decode_scope_metadata(loaded[0])
            raw = metadata.raw
            scope_id = raw.get("id")
            title, slug = raw.get("title"), raw.get("slug")
            expected_parent = chain[-1] if chain else None
            if (
                not isinstance(scope_id, str)
                or raw.get("type") != kind
                or not isinstance(title, str)
                or not title.strip()
                or not isinstance(slug, str)
                or directory.name != f"{scope_id}-{slug}"
                or raw.get("parent_id") != expected_parent
                or raw.get("initiative_id") != (chain[0] if chain else None)
                or raw.get("epic_id") != (chain[1] if len(chain) == 2 else None)
            ):
                raise ValueError("Scope metadata does not match its current tree position")
            if scope_id in identities:
                raise ScopeIdentityConflict("duplicate Scope ID", (identities[scope_id], directory))
            identities[scope_id] = directory
            github = raw.get("github")
            if isinstance(github, dict):
                identity = (github["repo_owner"].lower(), github["repo_name"].lower(), github["issue_number"])
                if identity in linkages:
                    raise ScopeIdentityConflict("duplicate GitHub linkage", (linkages[identity], directory))
                linkages[identity] = directory
            dependencies = raw.get("depends_on")
            if not isinstance(dependencies, list) or any(not isinstance(value, str) for value in dependencies):
                raise ValueError("Scope dependencies require an ID array")
            rows.append(StoredScope(directory, metadata))
            if kind == "initiative":
                walk(directory / "epics", "epic", (*chain, scope_id))
            elif kind == "epic":
                walk(directory / "issues", "issue", (*chain, scope_id))

    walk(specdock_dir / "initiatives", "initiative", ())
    return tuple(rows)


def _selected_paths(specdock_dir: Path, target_id: str, *, timeout: float) -> tuple[Path, ...]:
    """Use Git names to locate a current chain without inspecting unrelated Scopes."""
    prefix, _, _ = parse_id(target_id)
    if target_id != target_id.strip().lower():
        raise ValueError("selected Scope ID is not canonical")
    depth = {"init": 1, "epic": 2, "iss": 3}[prefix]
    containers = ("initiatives", "epics", "issues")[:depth]
    prefixes = ("init", "epic", "iss")[:depth]
    components = [specdock_dir.name]
    for index, container in enumerate(containers):
        components.extend((container, f"{target_id}-*" if index == depth - 1 else "*"))
    target_glob = "/".join(components)
    names = run_git(
        specdock_dir.parent,
        "ls-files",
        "--full-name",
        "-z",
        "--cached",
        "--others",
        "--",
        f":(glob){target_glob}",
        f":(glob){target_glob}/**",
        timeout=timeout,
        require_clean_stderr=True,
    )
    if names and not names.endswith(b"\0"):
        raise ValueError("Git Scope pathname output is not NUL-terminated")
    candidates: set[tuple[Path, ...]] = set()
    for name in names.split(b"\0"):
        if not name:
            continue
        parts = os.fsdecode(name).split("/")
        if len(parts) < 1 + depth * 2 or parts[0] != specdock_dir.name:
            raise ValueError("Git Scope pathname is outside the requested hierarchy")
        candidate: list[Path] = []
        parent = specdock_dir
        for index, (container, scope_prefix) in enumerate(zip(containers, prefixes, strict=True)):
            directory_name = parts[2 + index * 2]
            if parts[1 + index * 2] != container or not re.fullmatch(
                rf"{scope_prefix}(?:-local)?-[0-9]+-[a-z0-9]+(?:-[a-z0-9]+)*", directory_name
            ):
                raise ValueError("selected Scope pathname is not a canonical hierarchy")
            if index == depth - 1 and not directory_name.startswith(f"{target_id}-"):
                raise ValueError("Git Scope pathname does not match the selected ID")
            parent = parent / container / directory_name
            candidate.append(parent)
        candidates.add(tuple(candidate))

    matches: list[tuple[Path, ...]] = []
    for chain in sorted(candidates):
        for directory in chain:
            try:
                container_mode = directory.parent.lstat().st_mode
                directory_mode = directory.lstat().st_mode
            except FileNotFoundError:
                break
            if not stat.S_ISDIR(container_mode) or not stat.S_ISDIR(directory_mode):
                raise ValueError("selected Scope path is redirected or not a directory")
        else:
            matches.append(chain)
    if len(matches) > 1:
        raise ValueError("duplicate selected Scope ID")
    return matches[0] if matches else ()
