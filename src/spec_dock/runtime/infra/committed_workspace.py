"""Materialize committed planning metadata without checkout or a status cache."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path, PurePosixPath
import re
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from spec_dock.runtime.infra.git_process import run_git

if TYPE_CHECKING:
    from collections.abc import Iterator


@contextmanager
def committed_workspace(root: Path, oid: str, *, timeout: float) -> Iterator[Path]:
    listed = run_git(
        root,
        "ls-tree",
        "-r",
        "-t",
        "-z",
        oid,
        "--",
        "spec-dock/workspace.json",
        "spec-dock/initiatives",
        ".gitignore",
        "spec-dock/.gitignore",
        "spec-dock/.agent",
        timeout=timeout,
    )
    with TemporaryDirectory(prefix="spec-dock-start-") as temporary:
        temporary_root = Path(temporary).resolve(strict=True)
        workspace = temporary_root / "spec-dock"
        (workspace / "initiatives").mkdir(parents=True)
        for entry in listed.split(b"\0"):
            if not entry:
                continue
            header, separator, raw_path = entry.partition(b"\t")
            if not separator or len(header.split()) != 3:
                raise ValueError("committed planning tree entry is invalid")
            mode, kind, object_id = header.split()
            decoded = raw_path.decode("utf-8")
            parts = decoded.split("/")
            rules = decoded in (".gitignore", "spec-dock/.gitignore", "spec-dock/.agent/.gitignore")
            if decoded in ("spec-dock/.agent", "spec-dock/.agent/work-target") or decoded.startswith(
                "spec-dock/.agent/work-target/"
            ):
                raise ValueError("candidate work target state or its parent is tracked by Git")
            if any(part in ("", ".", "..") for part in parts) or (parts[0] != "spec-dock" and not rules):
                raise ValueError("committed planning path is unsafe")
            if parts[:2] == ["spec-dock", "initiatives"]:
                scope_path = True
                for index, (container, prefix) in enumerate((
                    ("initiatives", "init"),
                    ("epics", "epic"),
                    ("issues", "iss"),
                )):
                    position = 2 + index * 2
                    if len(parts) <= position or parts[position - 1] != container:
                        break
                    if not re.fullmatch(rf"{prefix}(?:-local)?-[0-9]+-[a-z0-9]+(?:-[a-z0-9]+)*", parts[position]):
                        scope_path = False
                        break
                if not scope_path:
                    continue
            relative = PurePosixPath(decoded)
            structure = (
                parts == ["spec-dock"]
                or parts == ["spec-dock", "initiatives"]
                or (len(parts) == 3 and parts[:2] == ["spec-dock", "initiatives"])
                or (len(parts) == 4 and parts[:2] == ["spec-dock", "initiatives"] and parts[3] == "epics")
                or (len(parts) == 5 and parts[:2] == ["spec-dock", "initiatives"] and parts[3] == "epics")
                or (
                    len(parts) == 6
                    and parts[:2] == ["spec-dock", "initiatives"]
                    and parts[3] == "epics"
                    and parts[5] == "issues"
                )
                or (
                    len(parts) == 7
                    and parts[:2] == ["spec-dock", "initiatives"]
                    and parts[3] == "epics"
                    and parts[5] == "issues"
                )
            )
            if structure:
                if mode != b"040000" or kind != b"tree":
                    raise ValueError("committed Scope or container is not a directory")
                if any("\\" in part or ":" in part for part in parts):
                    raise ValueError("committed planning path is unsafe on Windows")
                temporary_root.joinpath(*parts).mkdir(parents=True, exist_ok=True)
                continue
            if kind == b"tree":
                continue
            if rules or parts == ["spec-dock", "workspace.json"]:
                metadata = True
            elif len(parts) >= 4 and parts[1] == "initiatives":
                # Scope directories remain observable even when their metadata is missing.
                depth = 4
                while depth < len(parts) and depth < 8 and parts[depth - 1] == ("epics" if depth == 4 else "issues"):
                    depth += 2
                metadata = len(parts) == depth and parts[-1] == ".meta.json"
                directory_parts = parts[: depth - 1]
                if any("\\" in part or ":" in part for part in directory_parts):
                    raise ValueError("committed planning path is unsafe on Windows")
                temporary_root.joinpath(*directory_parts).mkdir(parents=True, exist_ok=True)
            else:
                continue
            if metadata:
                if mode not in (b"100644", b"100755") or kind != b"blob":
                    raise ValueError("committed planning metadata is not a regular file")
                payload = run_git(root, "cat-file", "blob", object_id.decode("ascii"), timeout=timeout)
                destination = temporary_root.joinpath(*relative.parts)
                destination.parent.mkdir(parents=True, exist_ok=True)
                with destination.open("xb") as target:
                    target.write(payload)
        yield workspace
