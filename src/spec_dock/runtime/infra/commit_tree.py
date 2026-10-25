"""Read one commit tree and its blobs; never the working tree, index or locks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from spec_dock.runtime.infra.git_process import run_git

if TYPE_CHECKING:
    from pathlib import Path

TreeEntryKind = Literal["regular", "symlink", "gitlink", "other"]


@dataclass(frozen=True)
class TreeEntry:
    """One blob or gitlink of a commit tree; undecodable path bytes are backslash-escaped."""

    path: str
    kind: TreeEntryKind
    object_id: str


def resolve_commit(root: Path, revision: str, *, timeout: float) -> str | None:
    """Return the full commit ID a revision names, or None when it names no commit."""
    resolved = run_git(
        root,
        "rev-parse",
        "--verify",
        "--quiet",
        "--end-of-options",
        f"{revision}^{{commit}}",
        timeout=timeout,
        missing_ok=True,
    )
    return resolved.decode("ascii").strip() or None


def list_commit_tree(root: Path, commit: str, *, timeout: float) -> tuple[TreeEntry, ...]:
    """List every blob and gitlink of the commit tree in Git's path order."""
    listed = run_git(root, "ls-tree", "-r", "--full-tree", "-z", commit, timeout=timeout)
    entries: list[TreeEntry] = []
    for record in listed.split(b"\0"):
        if not record:
            continue
        header, separator, raw_path = record.partition(b"\t")
        fields = header.split()
        if not separator or len(fields) != 3:
            raise ValueError("commit tree entry is invalid")
        mode, object_type, object_id = (field.decode("ascii") for field in fields)
        entries.append(
            TreeEntry(raw_path.decode("utf-8", errors="backslashreplace"), _kind(mode, object_type), object_id)
        )
    return tuple(entries)


def _kind(mode: str, object_type: str) -> TreeEntryKind:
    if object_type == "blob" and mode in ("100644", "100755"):
        return "regular"
    if object_type == "blob" and mode == "120000":
        return "symlink"
    if object_type == "commit" and mode == "160000":
        return "gitlink"
    return "other"


def read_blob(root: Path, object_id: str, *, timeout: float) -> bytes:
    """Read one committed blob by object ID."""
    return run_git(root, "cat-file", "blob", object_id, timeout=timeout)
