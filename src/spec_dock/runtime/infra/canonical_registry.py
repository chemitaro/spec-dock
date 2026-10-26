"""The registry of catalogs this user's periodic job syncs: `<state root>/canonical-registry.json` (contract C9)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from spec_dock.runtime.domain.canonical_sync_state import StateFormatError, SyncRegistry
from spec_dock.runtime.infra.canonical_state import directory_lock, read_json, write_json_atomic

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

REGISTRY_FILE: Final = "canonical-registry.json"


class RegistryUnreadable(Exception):
    """The registry is unreadable, malformed or of an unknown version; it is never overwritten."""

    def __init__(self, path: Path, reason: str) -> None:
        super().__init__(f"{path}: {reason}")
        self.path = path
        self.reason = reason


def registry_path(root: Path) -> Path:
    return root / REGISTRY_FILE


def read_registry(root: Path) -> SyncRegistry:
    """The registry, or an empty one when the file does not exist."""
    path = registry_path(root)
    try:
        payload = read_json(path)
    except (OSError, ValueError) as error:
        raise RegistryUnreadable(path, str(error)) from error
    if payload is None:
        return SyncRegistry(None, ())
    try:
        return SyncRegistry.from_json(payload)
    except StateFormatError as error:
        raise RegistryUnreadable(path, str(error)) from error


def update_registry(
    root: Path, mutate: Callable[[SyncRegistry], SyncRegistry], *, timeout: float = 10.0
) -> tuple[SyncRegistry, SyncRegistry]:
    """Re-read under a flock on the state root, apply `mutate`, write when it changed; return (before, after)."""
    with directory_lock(root, timeout=timeout):
        before = read_registry(root)
        after = mutate(before)
        if after != before:
            write_json_atomic(root, REGISTRY_FILE, after.to_json())
        return before, after
