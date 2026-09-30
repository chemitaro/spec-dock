"""Materialize committed planning metadata without checkout or a status cache."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from spec_dock.runtime.infra.git_process import run_git

if TYPE_CHECKING:
    from collections.abc import Iterator


@contextmanager
def committed_workspace(root: Path, oid: str, *, timeout: float) -> Iterator[Path]:
    listed = run_git(
        root, "ls-tree", "-r", "-z", oid, "--", "spec-dock/workspace.json", "spec-dock/initiatives", timeout=timeout
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
            if any(part in ("", ".", "..") for part in parts) or parts[0] != "spec-dock":
                raise ValueError("committed planning path is unsafe")
            relative = PurePosixPath(decoded)
            if parts == ["spec-dock", "workspace.json"]:
                metadata = True
            elif len(parts) >= 4 and parts[1] == "initiatives":
                # Scope directories remain observable even when their metadata is missing.
                depth = 4
                while depth < len(parts) and depth < 8 and parts[depth - 1] == ("epics" if depth == 4 else "issues"):
                    depth += 2
                metadata = len(parts) == depth and parts[-1] == ".meta.json"
                directory_parts = parts[: depth - 1]
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
