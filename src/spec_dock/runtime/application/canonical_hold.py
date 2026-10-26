"""`canonical accept` and `canonical restore`: the user's answer to a hold (Epic ch. 5 holds, R-C4).

accept records the current blob of named files (or the held deletions) in .runtime/accepted.json for the
next sync; restore brings held paths back from the catalog HEAD. Both run under the catalog lock, re-read
the work tree there, never commit and never write state.json. restore only touches what is still held
now (judgment Q1 and the document review): a file recreated or fixed since the last cycle is left alone.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from spec_dock.runtime.application.canonical_catalog import require_linked
from spec_dock.runtime.application.canonical_errors import (
    CANONICAL_LOCK_BUSY,
    CANONICAL_NOT_HELD,
    CANONICAL_NOT_RESTORABLE,
    CANONICAL_PATH_NOT_FOUND,
    CANONICAL_STATE_UNREADABLE,
    LOCK_BUSY_RECOVERY,
    NOT_HELD_RECOVERY,
    NOT_RESTORABLE_RECOVERY,
    PATH_NOT_FOUND_RECOVERY,
    STATE_UNREADABLE_NEXT_STEP,
    CanonicalCommandError,
)
from spec_dock.runtime.domain.canonical_changeset import normalize_catalog_path
from spec_dock.runtime.domain.canonical_sync_rules import MAX_FILE_BYTES, HoldCandidate, is_secret
from spec_dock.runtime.domain.canonical_sync_state import AcceptedChanges
from spec_dock.runtime.infra import canonical_git, runtime_environment
from spec_dock.runtime.infra.canonical_state import StateUnreadable, read_accepted, read_catalog_state, write_accepted
from spec_dock.runtime.infra.catalog_lock import CatalogLock, CatalogLockBusy
from spec_dock.runtime.infra.state_root import resolve_state_root
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Effect, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.domain.canonical_sync_state import CatalogSyncState, Hold


def _state(catalog: Path) -> CatalogSyncState | None:
    try:
        return read_catalog_state(resolve_state_root(), str(catalog))
    except StateUnreadable as error:
        raise CanonicalCommandError(
            CANONICAL_STATE_UNREADABLE,
            str(error),
            recovery=(STATE_UNREADABLE_NEXT_STEP,),
            details={"path": str(error.path)},
        ) from error


def _lock(catalog: Path) -> CatalogLock:
    lock = CatalogLock(catalog, timeout=10.0)
    try:
        lock.__enter__()
    except CatalogLockBusy as error:
        raise CanonicalCommandError(CANONICAL_LOCK_BUSY, str(error), recovery=(LOCK_BUSY_RECOVERY,)) from error
    return lock


def _relative(path: str, linked_root: Path, cwd: Path) -> str:
    """A path given relative to the catalog, or as a path through spec-dock/initiatives or the catalog."""
    candidate = os.path.realpath(path if Path(path).is_absolute() else cwd / path)
    root = os.path.realpath(linked_root)
    if candidate == root or candidate.startswith(root + os.sep):
        return normalize_catalog_path(os.path.relpath(candidate, root))
    return normalize_catalog_path(path)


def run_canonical_accept(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    environment = runtime_environment.detect_runtime_environment()
    linked = require_linked(context, environment=environment, timeout=namespace.timeout)
    catalog = linked.catalog
    paths = []
    for raw in namespace.paths:
        try:
            paths.append(_relative(raw, catalog, context.root))
        except ValueError as error:
            raise CanonicalCommandError(
                CANONICAL_PATH_NOT_FOUND, str(error), recovery=(PATH_NOT_FOUND_RECOVERY,)
            ) from error
    state = _state(catalog) if namespace.deletions else None
    lock = _lock(catalog)
    try:
        for path in paths:
            target = catalog / path
            if not (target.is_symlink() or target.is_file()):
                raise CanonicalCommandError(
                    CANONICAL_PATH_NOT_FOUND,
                    f"{path} is not a file in the catalog",
                    recovery=(PATH_NOT_FOUND_RECOVERY,),
                    details={"path": path, "next_step": PATH_NOT_FOUND_RECOVERY},
                )
        current = read_accepted(catalog)
        blobs = {path: canonical_git.blob_of(catalog, path) for path in paths}
        held_deletions = tuple(hold.path for hold in (state.holds if state else ()) if hold.kind == "mass_delete")
        accepted = AcceptedChanges({**current.paths, **blobs}, tuple(sorted({*current.deletions, *held_deletions})))
        changed = accepted != current
        if changed:
            write_accepted(catalog, accepted)
    except StateUnreadable as error:
        raise CanonicalCommandError(
            CANONICAL_STATE_UNREADABLE, str(error), recovery=(STATE_UNREADABLE_NEXT_STEP,)
        ) from error
    finally:
        lock.__exit__(None, None, None)
    data = FamilyData(
        "canonical-accept",
        {"catalog": str(catalog), "paths": blobs, "deletions": list(held_deletions), "changed": changed},
    )
    effect = Effect(
        "canonical.accept", "succeeded" if changed else "unchanged", str(catalog / ".runtime/accepted.json")
    )
    return OperationResult(namespace.command_path, "succeeded" if changed else "unchanged", data, 0, effects=(effect,))


def _still_held(catalog: Path, hold: Hold, deleted: set[str]) -> bool:
    """Is the hold still true of the work tree now? (never restore over a recreated or fixed file)"""
    target = catalog / hold.path
    if hold.kind == "mass_delete":
        return hold.path in deleted
    if not target.is_file() or target.is_symlink():
        return False
    size = target.stat().st_size
    if hold.kind == "too_large":
        return size > MAX_FILE_BYTES
    candidate = HoldCandidate(hold.path, size, "", target.read_bytes() if size <= MAX_FILE_BYTES else None)
    return candidate.content is not None and is_secret(candidate.content)


def run_canonical_restore(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    environment = runtime_environment.detect_runtime_environment()
    linked = require_linked(context, environment=environment, timeout=namespace.timeout)
    catalog = linked.catalog
    state = _state(catalog)
    holds = {hold.path: hold for hold in (state.holds if state else ())}
    lock = _lock(catalog)
    try:
        canonical_git.reset_index(catalog)
        deleted = {change.path for change in canonical_git.list_changes(catalog) if change.kind == "deleted"}
        if namespace.paths:
            targets = []
            for raw in namespace.paths:
                path = _relative(raw, catalog, context.root)
                hold = holds.get(path)
                if hold is None or not _still_held(catalog, hold, deleted):
                    raise CanonicalCommandError(
                        CANONICAL_NOT_HELD,
                        f"{path} is not held now (see changes.holds of spec-dock canonical status)",
                        recovery=(NOT_HELD_RECOVERY,),
                        details={"path": path, "next_step": NOT_HELD_RECOVERY},
                    )
                targets.append(path)
        else:
            targets = sorted(path for path, hold in holds.items() if hold.kind == "mass_delete" and path in deleted)
        in_head = canonical_git.tree_paths(catalog, "HEAD")
        missing = [path for path in targets if path not in in_head]
        if missing:
            raise CanonicalCommandError(
                CANONICAL_NOT_RESTORABLE,
                f"HEAD has no version of {', '.join(missing)}; restoring would delete it",
                recovery=(NOT_RESTORABLE_RECOVERY,),
                details={"paths": missing, "next_step": NOT_RESTORABLE_RECOVERY},
            )
        if targets:
            canonical_git.restore_from_head(catalog, targets)
    finally:
        lock.__exit__(None, None, None)
    data = FamilyData("canonical-restore", {"catalog": str(catalog), "restored": targets})
    effects = tuple(Effect("canonical.restore", "succeeded", path) for path in targets)
    return OperationResult(namespace.command_path, "succeeded" if targets else "unchanged", data, 0, effects=effects)
