"""Public console entrypoint for the installed SpecDock package."""

from __future__ import annotations

from pathlib import Path
import sys

from spec_dock.runtime.cli.options import completion_script, explicit_help, parse_vnext_output
from spec_dock.runtime.presentation.envelope import redact_text, render_diagnostic_json, render_utility_json


def main(argv: list[str] | None = None) -> int:
    """Run the package runtime, without a fixed bundle or repository engine pin."""
    from spec_dock import __version__

    arguments = sys.argv[1:] if argv is None else argv
    outcome = parse_vnext_output(arguments, engine_version=__version__, public_v2=True)
    if outcome.namespace is None:
        sys.stdout.write(outcome.stdout)
        sys.stderr.write(outcome.stderr)
        return outcome.exit_code if outcome.exit_code is not None else 2
    namespace = outcome.namespace
    command = namespace.command_path
    if command in ("help", "completion"):
        try:
            text = explicit_help(namespace.help_path) if command == "help" else completion_script(namespace.shell)
        except ValueError as error:
            if namespace.json:
                sys.stdout.write(render_diagnostic_json(command, "USAGE_ERROR", str(error), exit_code=2))
            else:
                sys.stderr.write(f"error [USAGE_ERROR] {redact_text(str(error))}\n")
            return 2
        sys.stdout.write(render_utility_json(command, text) if namespace.json else text)
        return 0
    from spec_dock.runtime.commands.runtime_dispatch import dispatch

    exit_code, stdout, stderr = dispatch(namespace, Path.cwd())
    sys.stdout.write(stdout)
    sys.stderr.write(stderr)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
