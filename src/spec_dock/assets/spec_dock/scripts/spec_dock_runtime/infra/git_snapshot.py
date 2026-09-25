"""Read one committed Scope graph without changing the current checkout."""

from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path, PurePosixPath
import subprocess
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator


def _git_bytes(repo_root: Path, *arguments: str) -> bytes:
    try:
        result = subprocess.run(["git", *arguments], cwd=repo_root, capture_output=True, check=False, timeout=60.0)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise RuntimeError("committed Scope snapshot could not be read") from error
    if result.returncode != 0:
        raise ValueError("committed Scope snapshot is unavailable")
    return result.stdout


def _safe_relative_path(raw: bytes) -> PurePosixPath:
    try:
        decoded = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("committed Scope path is not UTF-8") from error
    parts = decoded.split("/")
    if len(parts) < 4 or parts[:2] != ["spec-dock", "initiatives"] or any(part in ("", ".", "..") for part in parts):
        raise ValueError("committed Scope path is unsafe")
    return PurePosixPath(decoded)


@contextmanager
def scope_graph_at_commit(repo_root: Path, sha: str, *, status_cache: object | None) -> Iterator[Path]:
    """Materialize only metadata needed for readiness in a disposable directory.

    Git paths are never followed as symlinks. Non-metadata blobs are represented
    only by parent directories so missing node metadata is still detected.
    """
    listed = _git_bytes(repo_root, "ls-tree", "-r", "-z", sha, "--", "spec-dock/initiatives")
    entries = [entry for entry in listed.split(b"\0") if entry]
    with TemporaryDirectory(prefix="spec-dock-snapshot-") as temporary:
        temporary_root = Path(temporary).resolve(strict=True)
        snapshot = temporary_root / "spec-dock"
        (snapshot / "initiatives").mkdir(parents=True)
        for entry in entries:
            header, separator, raw_path = entry.partition(b"\t")
            if not separator or len(header.split()) != 3:
                raise ValueError("committed Scope tree entry is invalid")
            mode, kind, _object_id = header.split()
            relative = _safe_relative_path(raw_path)
            destination = temporary_root.joinpath(*relative.parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            if relative.name in (".meta.json", "meta.json"):
                if mode not in (b"100644", b"100755") or kind != b"blob":
                    raise ValueError("committed Scope metadata is not a regular file")
                payload = _git_bytes(repo_root, "show", f"{sha}:{relative.as_posix()}")
                with destination.open("xb") as target:
                    target.write(payload)
        if status_cache is not None:
            cache_path = snapshot / ".agent" / "github-status-cache.json"
            cache_path.parent.mkdir(parents=True)
            cache_path.write_text(json.dumps(status_cache, ensure_ascii=False), encoding="utf-8")
        yield snapshot
