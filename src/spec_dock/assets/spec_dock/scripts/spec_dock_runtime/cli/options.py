"""Strict argument parser for the vNext command catalog."""

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING, Any

from spec_dock_runtime.cli.catalog import LEAF_ARGUMENTS, LEAF_PATHS, MUTATING_LEAF_PATHS
from spec_dock_runtime.cli.legacy import reject_legacy_root

if TYPE_CHECKING:
    from collections.abc import Sequence

_COMMON_SWITCHES = {
    "--json": "json",
    "--non-interactive": "non_interactive",
    "--yes": "yes",
    "-y": "yes",
    "--dry-run": "dry_run",
    "--offline": "offline",
}
_COMMON_VALUES = {
    "--project": "project",
    "--expect-current": "expect_current",
    "--expect-backend": "expect_backend",
    "--lock-timeout": "lock_timeout",
    "--timeout": "timeout",
    "--color": "color",
}


class _StrictParser(argparse.ArgumentParser):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("allow_abbrev", False)
        super().__init__(*args, **kwargs)


def build_vnext_parser() -> argparse.ArgumentParser:
    parser = _StrictParser(prog="spec-dock")
    parents: dict[tuple[str, ...], argparse.ArgumentParser] = {(): parser}
    for leaf in LEAF_PATHS:
        parts = tuple(leaf.split())
        for depth in range(1, len(parts) + 1):
            path = parts[:depth]
            if path in parents:
                continue
            parent = parents[path[:-1]]
            subparsers = next(
                (action for action in parent._actions if isinstance(action, argparse._SubParsersAction)),
                None,
            )
            if subparsers is None:
                subparsers = parent.add_subparsers(dest=f"level_{depth}", required=True, parser_class=_StrictParser)
            parents[path] = subparsers.add_parser(path[-1])
        parents[parts].set_defaults(command_path=leaf)
        for argument in LEAF_ARGUMENTS[leaf]:
            parents[parts].add_argument(*argument.names, **argument.options)
    return parser


def parse_vnext(argv: Sequence[str]) -> argparse.Namespace:
    error_parser = _StrictParser(prog="spec-dock")
    remaining: list[str] = []
    common: dict[str, str | bool | float] = {}
    help_requested = False
    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg == "--":
            remaining.extend(argv[index:])
            break
        name, separator, inline_value = arg.partition("=") if arg.startswith("--") else (arg, "", "")
        if name in _COMMON_SWITCHES:
            if separator:
                error_parser.error(f"{name} does not take a value")
            common[_COMMON_SWITCHES[name]] = True
        elif name in ("--help", "-h"):
            help_requested = True
        elif name in _COMMON_VALUES:
            if separator:
                value = inline_value
            else:
                index += 1
                if index >= len(argv):
                    error_parser.error(f"{name} requires a value")
                value = argv[index]
            if not value:
                error_parser.error(f"{name} requires a nonempty value")
            key = _COMMON_VALUES[name]
            if key in common and common[key] != value:
                error_parser.error(f"conflicting duplicate {name}")
            if key in ("lock_timeout", "timeout"):
                try:
                    duration = float(value)
                except ValueError:
                    error_parser.error(f"{name} requires a number")
                if duration < 0 or (key == "timeout" and duration == 0):
                    error_parser.error(f"{name} requires a positive value")
            if key == "expect_backend" and value not in ("github", "local"):
                error_parser.error("--expect-backend must be github or local")
            if key == "color" and value not in ("auto", "always", "never"):
                error_parser.error("--color must be auto, always, or never")
            common[key] = value
        else:
            remaining.append(arg)
        index += 1
    if help_requested:
        remaining.append("--help")
    reject_legacy_root(remaining)
    parser = build_vnext_parser()
    parsed = parser.parse_args(remaining)
    if parsed.command_path == "active clear" and bool(parsed.from_target) == bool(parsed.all):
        parser.error("active clear requires exactly one of --from or --all")
    if parsed.command_path == "active set" and bool(parsed.target) == bool(parsed.from_branch):
        parser.error("active set requires exactly one of TARGET or --from-branch")
    if parsed.command_path == "installation update" and bool(parsed.version) == bool(parsed.commit):
        parser.error("installation update requires exactly one of --version or --commit")
    if parsed.command_path not in MUTATING_LEAF_PATHS and (common.get("yes") or common.get("dry_run")):
        parser.error("--yes and --dry-run apply only to changing commands")
    for key in (*_COMMON_SWITCHES.values(), *_COMMON_VALUES.values()):
        setattr(parsed, key, common.get(key, False if key in _COMMON_SWITCHES.values() else None))
    return parsed
