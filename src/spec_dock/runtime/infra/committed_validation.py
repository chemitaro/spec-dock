"""Read one committed structure, fetching only declaration and Scope metadata bodies."""

from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Literal

from spec_dock.runtime.infra.git_process import run_git

if TYPE_CHECKING:
    from collections.abc import Iterator

EntryRole = Literal["directory", "metadata", "artifact"]
_SCOPE_NAMES = tuple(
    re.compile(rf"{prefix}(?:-local)?-[0-9]+-[a-z0-9]+(?:-[a-z0-9]+)*\Z") for prefix in ("init", "epic", "iss")
)


class CommittedStructureInvalid(ValueError):
    """A committed structural entry cannot be represented safely."""


@contextmanager
def committed_validation(root: Path, oid: str, *, timeout: float) -> Iterator[Path]:
    listed = run_git(root, "ls-tree", "-r", "-t", "-z", oid, "--", "spec-dock", timeout=timeout)
    with TemporaryDirectory(prefix="spec-dock-validate-") as temporary:
        snapshot = Path(temporary).resolve(strict=True)
        for entry in listed.split(b"\0"):
            if not entry:
                continue
            header, separator, raw_path = entry.partition(b"\t")
            fields = header.split()
            if not separator or len(fields) != 3:
                raise CommittedStructureInvalid("committed tree entry is invalid")
            mode, kind, object_id = fields
            parts = tuple(os.fsdecode(raw_path).split("/"))
            role = _entry_role(parts)
            if role is None:
                continue
            _require_safe_path(parts)
            destination = snapshot.joinpath(*parts)
            if role == "directory":
                if mode != b"040000" or kind != b"tree":
                    raise CommittedStructureInvalid("committed structural directory is redirected or invalid")
                destination.mkdir(parents=True, exist_ok=True)
            elif role == "metadata":
                if mode not in (b"100644", b"100755") or kind != b"blob":
                    raise CommittedStructureInvalid("committed planning metadata is not a regular file")
                payload = run_git(root, "cat-file", "blob", object_id.decode("ascii"), timeout=timeout)
                destination.parent.mkdir(parents=True, exist_ok=True)
                with destination.open("xb") as target:
                    target.write(payload)
            else:
                # The catalog needs names and regular/nonregular types, never bodies or link targets.
                destination.parent.mkdir(parents=True, exist_ok=True)
                if mode in (b"100644", b"100755") and kind == b"blob":
                    destination.touch(exist_ok=False)
                else:
                    destination.mkdir()
        yield snapshot


def _entry_role(parts: tuple[str, ...]) -> EntryRole | None:
    if parts in (("spec-dock",), ("spec-dock", "initiatives"), ("spec-dock", "artifacts")):
        return "directory"
    if parts == ("spec-dock", "workspace.json"):
        return "metadata"
    if len(parts) == 3 and parts[:2] == ("spec-dock", "artifacts"):
        return "artifact"
    if parts[:2] != ("spec-dock", "initiatives"):
        return None
    index = 2
    for depth, pattern in enumerate(_SCOPE_NAMES):
        if len(parts) <= index or pattern.fullmatch(parts[index]) is None:
            return None
        owner_end = index + 1
        tail = parts[owner_end:]
        if not tail or tail == ("artifacts",):
            return "directory"
        if tail == (".meta.json",):
            return "metadata"
        if len(tail) == 2 and tail[0] == "artifacts":
            return "artifact"
        if depth == 2 or tail[0] != ("epics" if depth == 0 else "issues"):
            return None
        if len(tail) == 1:
            return "directory"
        index += 2
    return None


def _require_safe_path(parts: tuple[str, ...]) -> None:
    if any(part in ("", ".", "..") or "\\" in part or ":" in part for part in parts):
        raise CommittedStructureInvalid("committed structural path is unsafe")
    try:
        "/".join(parts).encode("utf-8")
    except UnicodeError as error:
        raise CommittedStructureInvalid("committed structural path encoding is invalid") from error
