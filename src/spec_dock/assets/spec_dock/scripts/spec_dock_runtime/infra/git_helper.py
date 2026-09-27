"""Run one Git child from a descriptor-bound worktree directory."""

from __future__ import annotations

import argparse
import os
import stat
import subprocess
import sys

from spec_dock_runtime.infra.git_cli import sanitized_git_environment

sys.dont_write_bytecode = True


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m spec_dock_runtime.infra.git_helper")
    parser.add_argument("--cwd-fd", type=int, required=True)
    parser.add_argument("--expected-device", type=int, required=True)
    parser.add_argument("--expected-inode", type=int, required=True)
    parser.add_argument("argv", nargs=argparse.REMAINDER)
    return parser


def _validate_cwd_fd(fd: int, expected_device: int, expected_inode: int) -> None:
    if fd < 0:
        raise RuntimeError("cwd fd must be non-negative")
    try:
        value = os.fstat(fd)
    except OSError as error:
        raise RuntimeError("cwd fd is unavailable") from error
    if not stat.S_ISDIR(value.st_mode):
        raise RuntimeError("cwd fd is not a directory")
    if value.st_dev != expected_device or value.st_ino != expected_inode:
        raise RuntimeError("cwd fd binding does not match expected target")


def main(argv: list[str] | None = None) -> int:
    namespace = _parser().parse_args(sys.argv[1:] if argv is None else argv)
    child_argv = list(namespace.argv)
    if child_argv and child_argv[0] == "--":
        child_argv.pop(0)
    if not child_argv:
        print("error: Git helper requires a child argv", file=sys.stderr)
        return 2
    try:
        _validate_cwd_fd(namespace.cwd_fd, namespace.expected_device, namespace.expected_inode)
        os.fchdir(namespace.cwd_fd)
        os.close(namespace.cwd_fd)
        child = subprocess.Popen(child_argv, env=sanitized_git_environment())
        return int(child.wait())
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print("error: Git helper child executable is unavailable", file=sys.stderr)
        return 127
    except OSError:
        print("error: Git helper could not execute the bound-cwd child", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
