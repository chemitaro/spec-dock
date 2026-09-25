"""Run the verified external package engine against a repository worktree."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from typing import TYPE_CHECKING

from spec_dock import __version__
from spec_dock.installer import ASSETS
from spec_dock.runtime_loader import EnginePin, VerifiedEngine, digest_distribution, read_engine_pin, verify_engine_pin

if TYPE_CHECKING:
    import argparse
    from collections.abc import Sequence


def _json_requested(argv: Sequence[str]) -> bool:
    return "--json" in argv[: argv.index("--") if "--" in argv else len(argv)]


def _preflight_failure(message: str, *, json_mode: bool) -> None:
    if not json_mode:
        print(f"spec-dock: {message}", file=sys.stderr)
        return
    print(
        json.dumps(
            {
                "schema_version": "specdock.cli/v1",
                "command": "entrypoint",
                "status": "failed",
                "operation_id": None,
                "target": None,
                "data": {"help": None},
                "effects": [],
                "warnings": [],
                "error": {"code": "ENGINE_PREFLIGHT_FAILED", "message": message, "details": {}},
                "recovery": None,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
    )


def _git_root(candidate: Path) -> Path | None:
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    environment.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    try:
        completed = subprocess.run(
            ["git", "-C", str(candidate), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
            env=environment,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0 or not completed.stdout.strip():
        return None
    return Path(completed.stdout.strip()).resolve(strict=True)


def _project_candidate(namespace: argparse.Namespace, invocation_cwd: Path) -> Path:
    if getattr(namespace, "command_path", None) == "installation init":
        raw = namespace.path
    else:
        raw = getattr(namespace, "project", None)
        if raw is None and getattr(namespace, "command_path", "").startswith("installation "):
            raw = getattr(namespace, "target", None)
    if raw is None:
        return invocation_cwd
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = invocation_cwd / candidate
    return candidate.resolve(strict=True)


def _executing_engine(*, executable: Path, checkout_root: Path) -> VerifiedEngine:
    if not executable.is_absolute() or executable.is_symlink() or executable.parent.name != "bin":
        raise ValueError("external engine must run from an absolute distribution bin path")
    distribution = executable.parent.parent
    package_file = Path(__file__).resolve(strict=True)
    assets = ASSETS.resolve(strict=True)
    fixed_package = distribution / "lib/spec_dock"
    if (
        package_file != fixed_package / "external_cli.py"
        or assets != fixed_package / "assets"
        or not (fixed_package / "version.txt").is_file()
    ):
        raise ValueError("external engine must use the fixed distribution layout")
    digest = digest_distribution(distribution)
    return verify_engine_pin(EnginePin(executable, distribution, digest), checkout_root=checkout_root)


def run_external(argv: Sequence[str], *, executable: Path, invocation_cwd: Path) -> int:
    """Verify self and repository pin before loading any checkout runtime."""
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ASSETS / "spec_dock/scripts"))
    from spec_dock_runtime.cli.options import parse_vnext_output
    from spec_dock_runtime.cli.vnext_runtime import run_vnext

    parsed = parse_vnext_output(argv, engine_version=__version__)
    if parsed.namespace is None:
        if parsed.stdout:
            sys.stdout.write(parsed.stdout)
        if parsed.stderr:
            sys.stderr.write(parsed.stderr)
        assert parsed.exit_code is not None
        return parsed.exit_code
    namespace = parsed.namespace
    if namespace.command_path in {"help", "completion"}:
        output = run_vnext(argv, invocation_cwd=invocation_cwd, engine_digest="", engine_version=__version__)
        if output.stdout:
            sys.stdout.write(output.stdout)
        if output.stderr:
            sys.stderr.write(output.stderr)
        return output.exit_code
    candidate = invocation_cwd if namespace is None else _project_candidate(namespace, invocation_cwd)
    project_root = _git_root(candidate)
    engine = _executing_engine(executable=executable, checkout_root=project_root or candidate)
    effective_argv = argv
    if (
        project_root is not None
        and namespace.command_path in {"installation show", "installation update", "installation uninstall"}
        and namespace.project is None
        and namespace.target is not None
    ):
        effective_argv = ("--project", str(project_root), *argv)
    if project_root is not None:
        from spec_dock.runtime_loader import git_common_directory

        verify_engine_pin(
            EnginePin(engine.executable, engine.distribution_root, engine.distribution_digest),
            checkout_root=project_root,
        )
        common = git_common_directory(project_root)
        control_path = common / "spec-dock/control/control.json"
        if control_path.exists() and namespace is not None:
            pinned = read_engine_pin(common, checkout_root=project_root)
            if pinned != engine:
                raise ValueError("executing engine differs from repository pin")
    output = run_vnext(
        effective_argv,
        invocation_cwd=invocation_cwd,
        engine_digest=engine.distribution_digest,
        engine_version=__version__,
        engine_pin=engine,
    )
    if output.stdout:
        sys.stdout.write(output.stdout)
    if output.stderr:
        sys.stderr.write(output.stderr)
    return output.exit_code


def main(argv: Sequence[str] | None = None) -> int:
    sys.dont_write_bytecode = True
    arguments = sys.argv[1:] if argv is None else argv
    try:
        return run_external(
            arguments,
            executable=Path(sys.argv[0]).absolute(),
            invocation_cwd=Path.cwd(),
        )
    except (OSError, ValueError) as error:
        _preflight_failure(str(error), json_mode=_json_requested(arguments))
        return 3
