from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from ..application.contracts import UseCases
from ..application.delegated_authoring import (
    DelegatedAuthoringManifestRequest,
    generate_delegated_authoring_manifest,
)
from ..presentation.contracts import CliText
from .contracts import CommandArgs, CommandOutcome, CommandSpec


@dataclass(frozen=True)
class DelegatedAuthoringManifestArgs(CommandArgs):
    role: str
    scope: str
    target: str
    host_surface: str
    input_authority_file: Path


def command_specs() -> dict[str, CommandSpec]:
    return {
        "delegated_authoring_manifest": CommandSpec(
            add_arguments=_add_manifest_arguments,
            args_factory=_manifest_args,
            run=_run_manifest,
        ),
    }


def _add_manifest_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--role", required=True, choices=("system-architect", "implementation-planner"))
    parser.add_argument("--scope", required=True, help="Scope node id, e.g. iss-00126")
    parser.add_argument("--target", required=True, choices=("design", "plan"))
    parser.add_argument("--host-surface", required=True, choices=("cli", "desktop"))
    parser.add_argument("--input-authority-file", required=True, type=Path)


def _manifest_args(ns: argparse.Namespace) -> CommandArgs:
    return DelegatedAuthoringManifestArgs(
        role=str(ns.role),
        scope=str(ns.scope),
        target=str(ns.target),
        host_surface=str(ns.host_surface),
        input_authority_file=Path(ns.input_authority_file),
    )


def _run_manifest(args: CommandArgs, use_cases: UseCases) -> CommandOutcome:
    del use_cases
    typed = _expect_manifest_args(args)
    repo_root = Path.cwd()
    result = generate_delegated_authoring_manifest(
        DelegatedAuthoringManifestRequest(
            role=typed.role,
            scope_id=typed.scope,
            target=typed.target,
            host_surface=typed.host_surface,
            input_authority_file=typed.input_authority_file,
            repo_root=repo_root,
            specdock_dir=repo_root / "spec-dock",
        )
    )
    return CommandOutcome(exit_code=0 if result.ok else 1, text=_render_result(result))


def _expect_manifest_args(args: CommandArgs) -> DelegatedAuthoringManifestArgs:
    if not isinstance(args, DelegatedAuthoringManifestArgs):
        raise RuntimeError("Invalid command args for delegated-authoring manifest")
    return args


def _render_result(result) -> CliText:
    lines = [
        "spec-dock: ok (delegated-authoring manifest)"
        if result.ok
        else "spec-dock: blocked (delegated-authoring manifest)",
        f"status={result.status}",
        f"reason={result.reason}",
        f"role={result.role}",
        f"scope={result.scope_id}",
        f"target={result.target}",
        f"host_surface={result.host_surface}",
        f"host_surface_acceptance_eligible={str(result.host_surface_acceptance_eligible).lower()}",
        f"acceptance_counted={str(result.acceptance_counted).lower()}",
    ]
    if result.target_artifact_path is not None:
        lines.append(f"target_artifact_path={result.target_artifact_path.as_posix()}")
    if result.paths is not None:
        lines.extend(
            [
                f"manifest_path={result.paths.manifest_path.as_posix()}",
                f"permission_profile_path={result.paths.permission_profile_path.as_posix()}",
                f"probe_plan_path={result.paths.probe_plan_path.as_posix()}",
                f"session_invocation_path={result.paths.session_invocation_path.as_posix()}",
            ]
        )
    if result.manifest_hash is not None:
        lines.append(f"manifest_hash={result.manifest_hash}")
    if result.permission_profile_name is not None:
        lines.append(f"permission_profile_name={result.permission_profile_name}")
    if result.permission_profile_hash is not None:
        lines.append(f"permission_profile_hash={result.permission_profile_hash}")
    if result.session_invocation_hash is not None:
        lines.append(f"session_invocation_hash={result.session_invocation_hash}")
    for detail in result.details:
        lines.append(f"detail={detail}")
    return CliText(stdout_lines=lines, stderr_lines=[], warnings=[])
