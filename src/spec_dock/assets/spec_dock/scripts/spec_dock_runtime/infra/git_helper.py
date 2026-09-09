"""Run a Git child while retaining its bound repository lease descriptors."""

from __future__ import annotations

import argparse
import os
import stat
import subprocess
import sys

sys.dont_write_bytecode = True


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m spec_dock_runtime.infra.git_helper")
    parser.add_argument("--lease-fd", type=int, action="append", required=True)
    parser.add_argument("--expected-device", type=int, action="append", required=True)
    parser.add_argument("--expected-inode", type=int, action="append", required=True)
    parser.add_argument("--cwd-fd", type=int, required=True)
    parser.add_argument("argv", nargs=argparse.REMAINDER)
    return parser


def _validate_fd(fd: int, expected_device: int, expected_inode: int) -> None:
    if fd < 0:
        raise RuntimeError("lease fd must be non-negative")
    try:
        value = os.fstat(fd)
    except OSError as error:
        raise RuntimeError("lease fd is unavailable") from error
    if not stat.S_ISDIR(value.st_mode):
        raise RuntimeError("lease fd is not a directory")
    if value.st_dev != expected_device or value.st_ino != expected_inode:
        raise RuntimeError("lease fd binding does not match expected repository")


def main(argv: list[str] | None = None) -> int:
    namespace = _parser().parse_args(sys.argv[1:] if argv is None else argv)
    child_argv = list(namespace.argv)
    if child_argv and child_argv[0] == "--":
        child_argv.pop(0)
    if not child_argv:
        print("error: Git helper requires a child argv", file=sys.stderr)
        return 2
    try:
        if not (len(namespace.lease_fd) == len(namespace.expected_device) == len(namespace.expected_inode)):
            raise RuntimeError("lease fd bindings must have matching lengths")
        for fd, device, inode in zip(
            namespace.lease_fd,
            namespace.expected_device,
            namespace.expected_inode,
            strict=True,
        ):
            _validate_fd(fd, device, inode)
            os.set_inheritable(fd, True)
        if namespace.cwd_fd not in namespace.lease_fd:
            raise RuntimeError("cwd fd must be one of the validated lease fds")
        os.fchdir(namespace.cwd_fd)
        child = subprocess.Popen(child_argv, pass_fds=tuple(namespace.lease_fd))
        return int(child.wait())
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"error: executable not found: {child_argv[0]}", file=sys.stderr)
        return 127
    except OSError as error:
        print(f"error: Git helper failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
