"""Cheap worktree-inventory revision evidence without launching Git (iss-00591)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

Stamp = tuple[str, int | None, int | None]


def _stamp(root: Path, name: str) -> Stamp:
    try:
        info = (root / name).stat()
        return name, info.st_mtime_ns, info.st_size
    except OSError:
        return name, None, None


def worktree_signature(checkout: Path | None) -> tuple[Stamp, ...] | None:
    """Stat main HEAD, the worktrees directory, and each registered HEAD/gitdir, in name order."""
    if checkout is None:
        return None
    root = checkout / ".git"
    try:
        if not root.is_dir():
            return None
    except OSError:
        return None
    stamps = [_stamp(root, "HEAD"), _stamp(root, "worktrees")]
    try:
        names = sorted(item.name for item in (root / "worktrees").iterdir())
    except FileNotFoundError:
        names = []
    except OSError:
        return (*stamps, ("worktrees/*", None, None))
    for name in names:
        stamps.extend(_stamp(root, f"worktrees/{name}/{leaf}") for leaf in ("HEAD", "gitdir"))
    return tuple(stamps)
