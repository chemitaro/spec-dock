"""Public console entrypoint for the installed SpecDock package."""

from __future__ import annotations

import sys

from spec_dock.runtime.cli.options import completion_script, explicit_help, parse_vnext_output
from spec_dock.runtime.presentation.envelope import render_diagnostic_json, render_utility_json


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
                sys.stderr.write(f"error [USAGE_ERROR] {error}\n")
            return 2
        sys.stdout.write(render_utility_json(command, text) if namespace.json else text)
        return 0
    # This intermediate milestone deliberately has no business effects.
    # P-04 connects the control-free context; never execute the retired engine.
    message = "business dispatch is not connected to the normal package yet"
    if namespace.json:
        sys.stdout.write(render_diagnostic_json(command, "BUSINESS_NOT_CONNECTED", message, exit_code=3))
    else:
        sys.stderr.write(f"error [BUSINESS_NOT_CONNECTED] {message}\n")
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
