"""Public installer adapter for the provider lifecycle engine.

The installer deliberately contains no lifecycle state machine.  It parses
the public command line, normalizes the target, delegates to
``ProviderLifecycleEngine``, and emits the already-validated Wire result.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from typing import cast

from spec_dock import __version__
from spec_dock.provider_lifecycle.contracts import LifecycleMode, LifecycleRequest
from spec_dock.provider_lifecycle.engine import ProviderLifecycleEngine
from spec_dock.provider_lifecycle.wire import serialize_public_result


def _tool_version() -> str:
    """Return the source version while retaining installed-package support."""

    try:
        pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
        source = pyproject.read_text(encoding="utf-8")
    except OSError:
        return __version__
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"\s*$', source)
    return match.group(1) if match else __version__


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="spec-dock")
    parser.add_argument("--version", action="version", version=f"spec-dock {_tool_version()}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Install the provider lifecycle into a project")
    init.add_argument("path", nargs="?", default=".", help="Target project path (default: current directory)")
    init.add_argument("--force", action="store_true", help="Replace provider-owned tooling in the target")
    init.add_argument("--json", action="store_true", help="Emit exactly one JSON object on stdout")
    init.add_argument("--provider-cleanup-token", help=argparse.SUPPRESS)

    update = subparsers.add_parser("update", help="Update provider-owned tooling in a project")
    update.add_argument("path", nargs="?", default=".", help="Target project path (default: current directory)")
    update.add_argument("--json", action="store_true", help="Emit exactly one JSON object on stdout")
    update.add_argument("--provider-cleanup-token", help=argparse.SUPPRESS)

    uninstall = subparsers.add_parser("uninstall", help="Remove provider tooling while preserving consumer data")
    uninstall.add_argument("path", nargs="?", default=".", help="Target project path (default: current directory)")
    uninstall.add_argument("--apply", action="store_true", help="Apply the uninstall operation")
    specs = uninstall.add_mutually_exclusive_group()
    specs.add_argument("--keep-specs", action="store_true", help="Preserve the consumer spec history")
    specs.add_argument("--remove-specs", action="store_true", help="Deprecated: spec history is never removed")
    uninstall.add_argument("--json", action="store_true", help="Emit exactly one JSON object on stdout")
    uninstall.add_argument("--provider-cleanup-token", help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def _target(path: str) -> Path:
    return Path(path).expanduser().resolve()


def _request(namespace: argparse.Namespace, target: Path) -> LifecycleRequest:
    if namespace.command == "init":
        return LifecycleRequest(
            str(target),
            "apply",
            True,
            operation="install",
            seed_policy="create-if-absent",
        )
    if namespace.command == "update":
        return LifecycleRequest(
            str(target),
            "apply",
            True,
            operation="update",
            seed_policy="preserve-only",
        )
    mode = cast("LifecycleMode", "apply" if namespace.apply else "dry-run")
    return LifecycleRequest(
        str(target),
        mode,
        bool(namespace.apply),
        specs_mode="remove" if namespace.remove_specs else "keep" if namespace.keep_specs else None,
        operation="uninstall",
        seed_policy="preserve-only",
    )


def _exit_code(status: str) -> int:
    if status in {"completed", "completed_with_warnings", "planned"}:
        return 0
    if status == "error":
        return 2
    return 1


def _render_text(result) -> str:
    line = f"spec-dock: {result.status} ({result.code}) -> {result.target}"
    if result.retry_command is not None:
        line += f"\nretry: {result.retry_command}"
    if result.errors:
        line += f"\nerror: {result.errors[0]}"
    return line


def main(argv: list[str] | None = None) -> int:
    """Run the public installer command and return its process status."""

    namespace = _parse_args(sys.argv[1:] if argv is None else argv)
    target = _target(namespace.path)
    json_requested = bool(getattr(namespace, "json", False))
    if not target.is_dir():
        if json_requested:
            print(f'{{"error":"target path is not a directory: {target}"}}')
        else:
            print(f"error: target path is not a directory: {target}", file=sys.stderr)
        return 2

    request = _request(namespace, target)
    result = ProviderLifecycleEngine().execute(
        request,
        force=True if namespace.command == "init" and namespace.force else None,
        cleanup_token=getattr(namespace, "provider_cleanup_token", None),
    )
    if json_requested:
        print(serialize_public_result(result).decode("utf-8"), end="")
    else:
        print(_render_text(result))
    return _exit_code(result.status)


if __name__ == "__main__":
    raise SystemExit(main())
