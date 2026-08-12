#!/usr/bin/env python3
"""Safely finalize one CLI-published SpecDock Artifact."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys


class FinalizeError(RuntimeError):
    """Raised when the Artifact cannot be finalized without following links."""


def _required_flag(name: str) -> int:
    value = getattr(os, name, None)
    if not isinstance(value, int):
        raise FinalizeError(f"platform does not provide required {name} support")
    return value


def _directory_flags() -> int:
    return os.O_RDONLY | _required_flag("O_DIRECTORY") | _required_flag("O_NOFOLLOW") | getattr(os, "O_CLOEXEC", 0)


def _file_flags() -> int:
    return os.O_WRONLY | _required_flag("O_NOFOLLOW") | getattr(os, "O_CLOEXEC", 0)


def _artifact_parts(raw: str, repo_root: str) -> tuple[str, ...]:
    if not raw or "\\" in raw:
        raise FinalizeError("artifact path must be a non-empty POSIX repository-relative path")
    lexical_parts = tuple(raw.split("/"))
    if any(part in {"", ".", ".."} for part in lexical_parts):
        raise FinalizeError("artifact path contains an empty or traversal component")
    parsed = PurePosixPath(raw)
    if parsed.is_absolute() or tuple(parsed.parts) != lexical_parts:
        raise FinalizeError("artifact path must remain repository-relative and lexical")
    repo_name = Path(repo_root).name
    if lexical_parts[:3] == (repo_name, "spec-dock", "initiatives"):
        lexical_parts = lexical_parts[1:]
    if lexical_parts[:2] != ("spec-dock", "initiatives"):
        raise FinalizeError("artifact path is outside spec-dock/initiatives")
    if len(lexical_parts) < 5 or lexical_parts[-2] != "artifacts":
        raise FinalizeError("artifact path must be a direct child of a scope artifacts directory")
    filename = lexical_parts[-1]
    if filename == "rules.md" or not filename.endswith(".md"):
        raise FinalizeError("artifact filename must be a new Markdown Artifact, not rules.md")
    return lexical_parts


def _open_parent(repo_root: str, parts: tuple[str, ...]) -> int:
    root_path = Path(repo_root)
    if not root_path.is_absolute():
        raise FinalizeError("repo root must be absolute")
    try:
        root_info = os.lstat(root_path)
    except OSError as exc:
        raise FinalizeError(f"cannot inspect repo root: {exc}") from exc
    if stat.S_ISLNK(root_info.st_mode) or not stat.S_ISDIR(root_info.st_mode):
        raise FinalizeError("repo root must be an ordinary directory, not a symlink")

    try:
        current_fd = os.open(root_path, _directory_flags())
    except OSError as exc:
        raise FinalizeError(f"cannot open repo root without following symlinks: {exc}") from exc

    try:
        for component in parts[:-1]:
            try:
                next_fd = os.open(component, _directory_flags(), dir_fd=current_fd)
            except OSError as exc:
                raise FinalizeError(
                    f"unsafe directory component '{component}' (symlink or non-directory): {exc}"
                ) from exc
            os.close(current_fd)
            current_fd = next_fd
        return current_fd
    except BaseException:
        os.close(current_fd)
        raise


def _stat_artifact(parent_fd: int, filename: str) -> os.stat_result:
    try:
        info = os.stat(filename, dir_fd=parent_fd, follow_symlinks=False)
    except OSError as exc:
        raise FinalizeError(f"cannot lstat Artifact without following symlinks: {exc}") from exc
    if not stat.S_ISREG(info.st_mode):
        raise FinalizeError("Artifact is not an ordinary file; symlink and special files are rejected")
    if info.st_nlink != 1:
        raise FinalizeError("Artifact must have exactly one hard link")
    return info


def _identity(repo_root: str, artifact: str) -> int:
    parts = _artifact_parts(artifact, repo_root)
    parent_fd = _open_parent(repo_root, parts)
    try:
        info = _stat_artifact(parent_fd, parts[-1])
    finally:
        os.close(parent_fd)
    print(
        json.dumps(
            {
                "ctime_ns": info.st_ctime_ns,
                "device": info.st_dev,
                "inode": info.st_ino,
            },
            sort_keys=True,
        )
    )
    return 0


def _write_all(fd: int, body: bytes) -> None:
    view = memoryview(body)
    written = 0
    while written < len(view):
        count = os.write(fd, view[written:])
        if count <= 0:
            raise FinalizeError("Artifact write made no progress")
        written += count


def _finalize(
    repo_root: str,
    artifact: str,
    *,
    expected_device: int,
    expected_inode: int,
    expected_ctime_ns: int,
) -> int:
    body = sys.stdin.buffer.read()
    if not body:
        raise FinalizeError("final Artifact body must be non-empty")

    parts = _artifact_parts(artifact, repo_root)
    parent_fd = _open_parent(repo_root, parts)
    file_fd: int | None = None
    try:
        before = _stat_artifact(parent_fd, parts[-1])
        expected = (expected_device, expected_inode, expected_ctime_ns)
        observed_before = (before.st_dev, before.st_ino, before.st_ctime_ns)
        if observed_before != expected:
            raise FinalizeError(
                f"Artifact identity changed before open: expected={expected} observed={observed_before}"
            )
        try:
            file_fd = os.open(parts[-1], _file_flags(), dir_fd=parent_fd)
        except OSError as exc:
            raise FinalizeError(f"cannot open Artifact without following symlinks: {exc}") from exc
        opened = os.fstat(file_fd)
        observed_opened = (opened.st_dev, opened.st_ino, opened.st_ctime_ns)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_nlink != 1
            or observed_opened != expected
            or observed_opened != observed_before
        ):
            raise FinalizeError(
                f"Artifact identity changed during open: expected={expected} observed={observed_opened}"
            )

        os.ftruncate(file_fd, 0)
        _write_all(file_fd, body)
        os.fsync(file_fd)

        after = _stat_artifact(parent_fd, parts[-1])
        observed_after = (after.st_dev, after.st_ino)
        expected_after = (expected_device, expected_inode)
        if observed_after != expected_after:
            raise FinalizeError(
                f"Artifact identity changed after write: expected={expected_after} observed={observed_after}"
            )
    finally:
        if file_fd is not None:
            os.close(file_fd)
        os.close(parent_fd)

    print(f"spec-dock: ok (finalize artifact) path={artifact}")
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_path_arguments(command: argparse.ArgumentParser) -> None:
        command.add_argument("--repo-root", required=True)
        command.add_argument("--artifact", required=True)

    identity = subparsers.add_parser("identity", help="Read a no-follow Artifact identity")
    add_path_arguments(identity)

    finalize = subparsers.add_parser("finalize", help="Finalize the pinned Artifact from stdin")
    add_path_arguments(finalize)
    finalize.add_argument("--expected-device", type=int, required=True)
    finalize.add_argument("--expected-inode", type=int, required=True)
    finalize.add_argument("--expected-ctime-ns", type=int, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        if args.command == "identity":
            return _identity(args.repo_root, args.artifact)
        return _finalize(
            args.repo_root,
            args.artifact,
            expected_device=args.expected_device,
            expected_inode=args.expected_inode,
            expected_ctime_ns=args.expected_ctime_ns,
        )
    except (FinalizeError, OSError) as exc:
        print(
            f"error: {exc}; path={args.artifact}; partial Artifact requires operator recovery",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
