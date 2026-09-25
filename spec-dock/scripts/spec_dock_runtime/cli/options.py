"""Strict argument parser for the vNext command catalog."""

from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from io import StringIO
import math
import re
from typing import TYPE_CHECKING, Any

from spec_dock_runtime.cli.catalog import (
    HELP_EFFECTS,
    LEAF_ARGUMENTS,
    LEAF_PATHS,
    MUTATING_LEAF_PATHS,
    RECOVERY_LEAF_COMMANDS,
)
from spec_dock_runtime.cli.legacy import LegacyCommandError, reject_legacy_root
from spec_dock_runtime.domain.operation import ROLLBACK_COMMANDS
from spec_dock_runtime.presentation.envelope import Diagnostic, OperationResult, render_json
from spec_dock_runtime.presentation.errors import CliMessageData, VersionData

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass(frozen=True)
class ParseOutcome:
    namespace: argparse.Namespace | None
    exit_code: int | None
    stdout: str
    stderr: str


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
        kwargs.setdefault("formatter_class", argparse.RawDescriptionHelpFormatter)
        super().__init__(*args, **kwargs)


def _recovery_help(leaf: str) -> str:
    command = RECOVERY_LEAF_COMMANDS.get(leaf)
    if command is not None:
        rollback = (
            "; --rollback OPERATION_ID is available for verified local rollback" if command in ROLLBACK_COMMANDS else ""
        )
        return f"Inspect the operation record, then use --resume OPERATION_ID with the same target{rollback}."
    if leaf == "worktree create":
        return "Inspect the target record, path, Git ref, and registration; --recover ID retries only after all effects are absent."
    if leaf == "worktree bootstrap":
        return "Inspect the target record and project effects; --recover --yes only acknowledges the attempt, then retry separately."
    if leaf == "workspace sync":
        return "Inspect the published generation pointer, then retry with the same source; there is no --resume."
    if leaf in MUTATING_LEAF_PATHS:
        return "Inspect the target and observed effects before retrying; there is no --resume."
    return "No mutation to recover; correct the reported input or environment and rerun."


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
        parents[parts].epilog = f"Effects:\n  {HELP_EFFECTS[leaf]}\n\nRecovery:\n  {_recovery_help(leaf)}"
    return parser


def explicit_help(command_path: Sequence[str]) -> str:
    """Render a known command or group from the same parser as execution."""
    current = build_vnext_parser()
    for component in command_path:
        action = next((item for item in current._actions if isinstance(item, argparse._SubParsersAction)), None)
        if action is None or component not in action.choices:
            raise ValueError("help target is not a known command path")
        current = action.choices[component]
    return current.format_help()


def completion_script(shell: str) -> str:
    """Generate command-name completion from the canonical leaf catalog."""
    if shell not in {"bash", "zsh", "fish"}:
        raise ValueError("completion shell is unsupported")
    children: dict[str, set[str]] = {}
    for leaf in LEAF_PATHS:
        parts = leaf.split()
        for index, word in enumerate(parts):
            children.setdefault(" ".join(parts[:index]), set()).add(word)
        children.setdefault(leaf, set()).update(
            name for argument in LEAF_ARGUMENTS[leaf] for name in argument.names if name.startswith("-")
        )
        children[leaf].update((*_COMMON_SWITCHES, *_COMMON_VALUES, "--help"))
    entries = [(key, " ".join(sorted(values))) for key, values in sorted(children.items())]
    if shell == "fish":
        lines = [
            "function __spec_dock_path_is",
            "  set -l seen (commandline -opc)",
            "  test (string join ' ' $seen[2..]) = \"$argv[1]\"",
            "end",
            "complete -c spec-dock -f",
        ]
        for path, words in entries:
            lines.append(f"complete -c spec-dock -n '__spec_dock_path_is \"{path}\"' -a '{words}'")
        return "\n".join(lines) + "\n"
    cases = "\n".join(f'    "{path}") choices="{words}" ;;' for path, words in entries)
    if shell == "bash":
        return (
            "_spec_dock_complete() {\n"
            '  local key="" choices="" word i\n'
            "  for ((i=1; i<COMP_CWORD; i++)); do\n"
            '    word="${COMP_WORDS[i]}"\n'
            '    [[ "$word" == -* ]] || key="${key:+$key }$word"\n'
            "  done\n"
            f'  case "$key" in\n{cases}\n  esac\n'
            '  COMPREPLY=( $(compgen -W "$choices" -- "${COMP_WORDS[COMP_CWORD]}") )\n'
            "}\ncomplete -F _spec_dock_complete spec-dock\n"
        )
    return (
        "#compdef spec-dock\n_spec_dock_complete() {\n"
        '  local key="" choices="" word i\n'
        "  for ((i=2; i<CURRENT; i++)); do\n"
        '    word="${words[i]}"\n'
        '    [[ "$word" == -* ]] || key="${key:+$key }$word"\n'
        "  done\n"
        f'  case "$key" in\n{cases}\n  esac\n'
        "  compadd -- ${(z)choices}\n}\ncompdef _spec_dock_complete spec-dock\n"
    )


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
            normalized_value: str | float = value
            if key in ("lock_timeout", "timeout"):
                try:
                    duration = float(value)
                except ValueError:
                    error_parser.error(f"{name} requires a number")
                if not math.isfinite(duration) or duration < 0 or (key == "timeout" and duration == 0):
                    error_parser.error(f"{name} requires a positive value")
                normalized_value = duration
            if key in common and common[key] != normalized_value:
                error_parser.error(f"conflicting duplicate {name}")
            if key == "expect_backend" and value not in ("github", "local"):
                error_parser.error("--expect-backend must be github or local")
            if key == "color" and value not in ("auto", "always", "never"):
                error_parser.error("--color must be auto, always, or never")
            common[key] = normalized_value
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
    if parsed.command_path == "installation update":
        if parsed.activate_engine:
            if parsed.version or parsed.commit or parsed.maintenance or parsed.finalize:
                parser.error("installation update --activate-engine accepts no source, maintenance, or finalize")
            if sum(bool(item) for item in (parsed.from_update, parsed.resume, parsed.rollback)) != 1:
                parser.error("installation update --activate-engine requires one update or recovery operation ID")
            if parsed.from_update and re.fullmatch(r"[0-9a-f]{32}", parsed.from_update) is None:
                parser.error("--from-update requires a 32-character lowercase operation ID")
        elif parsed.from_update:
            parser.error("--from-update requires --activate-engine")
        elif parsed.finalize:
            if parsed.version or parsed.commit or parsed.maintenance or parsed.rollback:
                parser.error("installation update --finalize accepts no source, maintenance, or rollback")
        elif (parsed.rollback and (parsed.version or parsed.commit)) or (
            not parsed.rollback and bool(parsed.version) == bool(parsed.commit)
        ):
            parser.error("installation update requires one source for update/resume and no source for rollback")
    resume = getattr(parsed, "resume", None)
    rollback = getattr(parsed, "rollback", None)
    if resume and rollback:
        parser.error("--resume and --rollback are mutually exclusive")
    if any(value is not None and re.fullmatch(r"[0-9a-f]{32}", value) is None for value in (resume, rollback)):
        parser.error("recovery requires a 32-character lowercase operation ID")
    if parsed.command_path == "branch create" and not resume and not parsed.base:
        parser.error("branch create requires --base unless --resume is specified")
    if parsed.command_path == "worktree create" and parsed.recover and common.get("dry_run"):
        parser.error("worktree create --recover cannot be combined with --dry-run")
    if parsed.command_path == "worktree bootstrap" and parsed.recover and common.get("dry_run"):
        parser.error("worktree bootstrap --recover cannot be combined with --dry-run")
    if parsed.command_path not in MUTATING_LEAF_PATHS and (common.get("yes") or common.get("dry_run")):
        parser.error("--yes and --dry-run apply only to changing commands")
    for key in (*_COMMON_SWITCHES.values(), *_COMMON_VALUES.values()):
        setattr(parsed, key, common.get(key, False if key in _COMMON_SWITCHES.values() else None))
    parsed.non_interactive = bool(parsed.non_interactive or parsed.json)
    parsed.lock_timeout = 0.0 if parsed.lock_timeout is None else parsed.lock_timeout
    parsed.timeout = (
        (300.0 if parsed.command_path == "worktree bootstrap" else 30.0) if parsed.timeout is None else parsed.timeout
    )
    return parsed


def parse_vnext_output(
    argv: Sequence[str], *, engine_version: str | None = None, engine_digest: str | None = None
) -> ParseOutcome:
    json_mode = _json_requested(argv)
    if [token for token in argv if token != "--json"] in (["--version"], ["-V"]):
        if engine_version is None:
            return _parse_failure("ENGINE_VERSION_UNAVAILABLE", "engine version is unavailable", json_mode)
        if json_mode:
            result = OperationResult(
                command="version",
                status="succeeded",
                data=VersionData(engine_version, engine_digest),
                exit_code=0,
            )
            return ParseOutcome(None, 0, render_json(result), "")
        return ParseOutcome(None, 0, f"spec-dock {engine_version}\n", "")
    captured_stdout = StringIO()
    captured_stderr = StringIO()
    try:
        with redirect_stdout(captured_stdout), redirect_stderr(captured_stderr):
            namespace = parse_vnext(argv)
    except LegacyCommandError as error:
        return _parse_failure(error.error_code, str(error), json_mode)
    except SystemExit as error:
        code = int(error.code or 0)
        if code == 0:
            help_text = captured_stdout.getvalue()
            if json_mode:
                result = OperationResult(
                    command="help",
                    status="succeeded",
                    data=CliMessageData(help_text),
                    exit_code=0,
                )
                return ParseOutcome(None, 0, render_json(result), "")
            return ParseOutcome(None, 0, help_text, "")
        message = captured_stderr.getvalue().strip().splitlines()[-1]
        return _parse_failure("USAGE_ERROR", message, json_mode)
    return ParseOutcome(namespace, None, "", "")


def _json_requested(argv: Sequence[str]) -> bool:
    for token in argv:
        if token == "--":
            return False
        if token == "--json":
            return True
    return False


def _parse_failure(code: str, message: str, json_mode: bool) -> ParseOutcome:
    if json_mode:
        result = OperationResult(
            command="cli.parse",
            status="failed",
            data=CliMessageData(None),
            exit_code=2,
            error=Diagnostic(code, message, {}),
        )
        return ParseOutcome(None, 2, render_json(result), "")
    return ParseOutcome(None, 2, "", f"error [{code}] {message}\n")
