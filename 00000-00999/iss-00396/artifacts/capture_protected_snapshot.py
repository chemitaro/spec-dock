#!/usr/bin/env python3
"""Capture the fixed Issue #396 protected-tree snapshot without following links."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
from typing import Any


ROOTS = (
    "spec-dock",
    ".agents/skills",
    ".gitignore",
    ".github/workflows/ci.yml",
    "src/spec_dock/assets",
)
EXCLUDED_PATHS = (
    "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/"
    "epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/"
    "issues/iss-00396-build-once-provider-gate-and-regression-policy-cutover/.workbench/evidence",
)


class SnapshotError(Exception):
    """Raised when the protected surface cannot be captured consistently."""


def _stable_stat(left: os.stat_result, right: os.stat_result) -> bool:
    return (
        left.st_dev,
        left.st_ino,
        left.st_mode,
        left.st_size,
        left.st_mtime_ns,
        left.st_ctime_ns,
    ) == (
        right.st_dev,
        right.st_ino,
        right.st_mode,
        right.st_size,
        right.st_mtime_ns,
        right.st_ctime_ns,
    )


def _relative(path: Path, root: Path) -> str:
    value = path.relative_to(root).as_posix()
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:
        raise SnapshotError(f"path is not UTF-8 encodable: {value!r}") from exc
    if value in ("", ".") or any(part in ("", ".", "..") for part in value.split("/")):
        raise SnapshotError(f"invalid repository-relative path: {value!r}")
    return value


def _is_excluded(relative_path: str) -> bool:
    return any(
        relative_path == excluded or relative_path.startswith(excluded + "/")
        for excluded in EXCLUDED_PATHS
    )


def _collect(path: Path, root: Path) -> list[dict[str, Any]]:
    relative_path = _relative(path, root)
    before = path.lstat()
    mode = stat.S_IMODE(before.st_mode)

    if stat.S_ISLNK(before.st_mode):
        target = os.fsencode(os.readlink(path))
        after = path.lstat()
        if not _stable_stat(before, after):
            raise SnapshotError(f"symlink changed while reading: {relative_path}")
        return [{
            "path": relative_path,
            "kind": "symlink",
            "mode": mode,
            "size_bytes": len(target),
            "sha256": hashlib.sha256(target).hexdigest(),
        }]

    if stat.S_ISDIR(before.st_mode):
        names = sorted(os.listdir(path), key=lambda name: os.fsencode(name))
        found = [{
            "path": relative_path,
            "kind": "directory",
            "mode": mode,
            "size_bytes": None,
            "sha256": None,
        }]
        for name in names:
            child = path / name
            child_relative = _relative(child, root)
            if _is_excluded(child_relative):
                continue
            found.extend(_collect(child, root))
        after = path.lstat()
        if not _stable_stat(before, after):
            raise SnapshotError(f"directory changed while reading: {relative_path}")
        return found

    if not stat.S_ISREG(before.st_mode):
        raise SnapshotError(f"unsupported file type: {relative_path}")

    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise SnapshotError(f"cannot safely open {relative_path}: {exc}") from exc
    digest = hashlib.sha256()
    size = 0
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or not _stable_stat(before, opened):
            raise SnapshotError(f"file changed before read: {relative_path}")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
                size += len(chunk)
        after = os.fstat(descriptor)
        path_after = path.lstat()
        if not _stable_stat(opened, after) or not _stable_stat(after, path_after) or size != after.st_size:
            raise SnapshotError(f"file changed while reading: {relative_path}")
    finally:
        os.close(descriptor)
    return [{
        "path": relative_path,
        "kind": "regular-file",
        "mode": mode,
        "size_bytes": size,
        "sha256": digest.hexdigest(),
    }]


def capture(repository: Path) -> dict[str, Any]:
    root = repository.resolve(strict=True)
    entries: list[dict[str, Any]] = []
    seen: set[str] = set()

    for relative_root in ROOTS:
        root_path = root / relative_root
        try:
            root_stat = root_path.lstat()
        except FileNotFoundError as exc:
            raise SnapshotError(f"protected root is missing: {relative_root}") from exc
        del root_stat
        entries.extend(_collect(root_path, root))

    entries.sort(key=lambda entry: entry["path"].encode("utf-8"))
    for entry in entries:
        if entry["path"] in seen:
            raise SnapshotError(f"duplicate protected path: {entry['path']}")
        seen.add(entry["path"])

    return {
        "schema_version": 1,
        "roots": list(ROOTS),
        "excluded_paths": list(EXCLUDED_PATHS),
        "entries": entries,
    }


def _output_is_allowed(output: Path, root: Path) -> Path:
    parent = output.parent.resolve(strict=True)
    candidate = parent / output.name
    try:
        relative = candidate.relative_to(root).as_posix()
    except ValueError:
        return candidate
    if _is_excluded(relative):
        return candidate
    raise SnapshotError("output must be outside protected roots or below the exact excluded evidence path")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        repository = args.repository.resolve(strict=True)
        output = _output_is_allowed(args.output, repository)
        snapshot = capture(repository)
        payload = (json.dumps(snapshot, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(output, flags, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except (OSError, SnapshotError, ValueError) as exc:
        print(f"protected snapshot failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
