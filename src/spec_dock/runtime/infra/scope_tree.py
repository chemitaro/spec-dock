"""Schema-3 metadata only; never inspect Workbench, cache or old runtime records."""

from __future__ import annotations

from dataclasses import dataclass
import re
import stat
from typing import TYPE_CHECKING

from spec_dock.runtime.domain.lifecycle import decode_scope_metadata
from spec_dock.runtime.infra.json_store import read_guarded_json

if TYPE_CHECKING:
    from pathlib import Path

    from spec_dock.runtime.domain.lifecycle import ScopeMetadata

_PREFIXES = {"initiative": "init", "epic": "epic", "issue": "iss"}


@dataclass(frozen=True)
class StoredScope:
    path: Path
    metadata: ScopeMetadata


def load_scope_tree(specdock_dir: Path) -> tuple[StoredScope, ...]:
    rows: list[StoredScope] = []
    identities: set[str] = set()
    linkages: set[tuple[str, str, int]] = set()

    def walk(container: Path, kind: str, chain: tuple[str, ...]) -> None:
        try:
            mode = container.lstat().st_mode
        except FileNotFoundError:
            return
        if not stat.S_ISDIR(mode):
            raise ValueError("Scope container is redirected or not a directory")
        pattern = re.compile(rf"{_PREFIXES[kind]}(?:-local)?-[0-9]+-[a-z0-9]+(?:-[a-z0-9]+)*\Z")
        for directory in sorted(container.iterdir()):
            if not pattern.fullmatch(directory.name):
                continue
            if not stat.S_ISDIR(directory.lstat().st_mode):
                raise ValueError("Scope path is redirected or not a directory")
            loaded = read_guarded_json(directory / ".meta.json")
            if loaded is None or not isinstance(loaded[0], dict):
                raise ValueError("Scope metadata is missing or invalid")
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
                raise ValueError("duplicate Scope ID")
            identities.add(scope_id)
            github = raw.get("github")
            if isinstance(github, dict):
                identity = (github["repo_owner"].lower(), github["repo_name"].lower(), github["issue_number"])
                if identity in linkages:
                    raise ValueError("duplicate GitHub linkage")
                linkages.add(identity)
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
