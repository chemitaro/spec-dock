"""Public fixed-engine CLI and retained internal legacy-installer fixture."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import sys

from spec_dock import __version__
from spec_dock.installer import install, uninstall


def _tool_version() -> str:
    """Return the source version while retaining installed-package support."""

    try:
        pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
        source = pyproject.read_text(encoding="utf-8")
    except OSError:
        return __version__
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"\s*$', source)
    return match.group(1) if match else __version__


def legacy_installer_main(argv: list[str] | None = None) -> int:
    """Exercise the retired directory installer in historical compatibility tests."""
    parser = argparse.ArgumentParser(prog="spec-dock")
    parser.add_argument("--version", action="version", version=f"spec-dock {_tool_version()}")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "update", "uninstall"):
        command = commands.add_parser(name)
        command.add_argument("path", nargs="?", default=".")
        command.add_argument("--json", action="store_true")
        if name == "init":
            command.add_argument("--force", action="store_true", help="Replace existing tooling directories")
        if name == "uninstall":
            command.add_argument("--apply", action="store_true", help="Remove tooling; default is dry-run")
            command.add_argument("--keep-specs", action="store_true", help="Data is always preserved")
            command.add_argument("--remove-specs", action="store_true", help=argparse.SUPPRESS)
    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return int(error.code or 0)
    target = Path(args.path).expanduser().resolve()
    try:
        if args.command == "uninstall":
            if args.remove_specs:
                message = "SpecDock never removes consumer data; --remove-specs is unsupported"
                if args.json:
                    print(json.dumps({"status": "error", "command": args.command, "error": message}))
                else:
                    print(f"error: {message}", file=sys.stderr)
                return 2
            uninstall(target, apply=args.apply)
            status = "completed" if args.apply else "planned"
        else:
            exists = (target / "spec-dock").exists()
            if args.command == "init" and exists and not args.force:
                raise ValueError("spec-dock already exists; use update or init --force")
            if args.command == "update" and not exists:
                raise ValueError("spec-dock is not installed; use init")
            install(target, version=_tool_version(), fresh=not exists)
            status = "completed"
    except (OSError, ValueError, shutil.Error) as error:
        if args.json:
            print(json.dumps({"status": "error", "command": args.command, "error": str(error)}))
        else:
            print(f"error: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps({"status": status, "command": args.command, "target": str(target)}))
    else:
        print(f"spec-dock: {status} ({args.command}) -> {target}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Enter the pinned external engine for every public invocation."""
    from spec_dock.external_cli import main as external_main

    return external_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
