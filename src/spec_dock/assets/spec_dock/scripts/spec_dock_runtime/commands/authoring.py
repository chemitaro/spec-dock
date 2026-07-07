from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from spec_dock_runtime.application.authoring_pack.github_sync_preflight import (
    GitHubSyncPreflightRequest,
    run_github_sync_preflight,
)
from spec_dock_runtime.application.authoring_pack.backend_invoke import invoke_backend
from spec_dock_runtime.application.authoring_pack.pack_prepare import prepare_prompt_pack
from spec_dock_runtime.commands.contracts import CommandArgs, CommandOutcome, CommandSpec
from spec_dock_runtime.domain.authoring_pack.backend_invoke_contract import BackendInvokeRequest
from spec_dock_runtime.domain.authoring_pack.prompt_pack_contract import PromptPackPrepareRequest
from spec_dock_runtime.presentation.authoring_pack.diagnostics import render_preflight_json, render_preflight_text
from spec_dock_runtime.presentation.authoring_pack.backend_invoke_renderer import (
    render_backend_invoke_json,
    render_backend_invoke_text,
)
from spec_dock_runtime.presentation.authoring_pack.pack_prepare_renderer import (
    render_pack_prepare_json,
    render_pack_prepare_text,
)
from spec_dock_runtime.presentation.contracts import CliText

if TYPE_CHECKING:
    import argparse

    from spec_dock_runtime.application.contracts import UseCases


@dataclass(frozen=True)
class AuthoringDeferredArgs(CommandArgs):
    command: str
    next_issue: str


@dataclass(frozen=True)
class AuthoringPreflightGithubSyncArgs(CommandArgs):
    evidence_mode: str
    output_format: str
    allow_default_branch_fallback: bool
    repo_root: Path | None
    ref: str | None
    source_paths: tuple[str, ...]
    expected_source_manifest: Path | None
    expected_source_hash: str | None
    provided_context_paths: tuple[str, ...]
    diff_summary: str | None
    unsynced_reason: str | None


@dataclass(frozen=True)
class AuthoringPackPrepareArgs(CommandArgs):
    preflight: Path
    output_dir: Path
    output_format: str
    mode: str | None
    source_manifest: Path | None
    stale_if: Path | None


@dataclass(frozen=True)
class AuthoringBackendInvokeArgs(CommandArgs):
    prompt_pack: Path
    output_dir: Path
    output_format: str
    backend_command: str | None
    slug: str | None
    prompt: str | None
    evidence_mode: str
    timeout_seconds: float | None
    dry_run: bool


_DEFERRED_COMMANDS: dict[str, tuple[str, str]] = {
    "authoring_pack_review": ("authoring pack review", "iss-00301"),
    "authoring_pack_stage": ("authoring pack stage", "iss-00301"),
    "authoring_validate_initiative_epic_candidates": (
        "authoring validate initiative-epic-candidates",
        "iss-00302",
    ),
    "authoring_validate_epic_issue_candidates": ("authoring validate epic-issue-candidates", "iss-00302"),
    "authoring_validate_issue_draft_adoption": ("authoring validate issue-draft-adoption", "iss-00303"),
    "authoring_validate_selected_skeleton_fill": ("authoring validate selected-skeleton-fill", "iss-00303"),
    "authoring_approval_check": ("authoring approval check", "iss-00305"),
}


def command_specs() -> dict[str, CommandSpec]:
    specs = {
        key: CommandSpec(
            add_arguments=_add_deferred_arguments,
            args_factory=_deferred_args_factory(command=command, next_issue=next_issue),
            run=_run_deferred,
        )
        for key, (command, next_issue) in _DEFERRED_COMMANDS.items()
    }
    specs["authoring_preflight_github_sync"] = CommandSpec(
        add_arguments=_add_preflight_github_sync_arguments,
        args_factory=_preflight_github_sync_args,
        run=_run_preflight_github_sync,
    )
    specs["authoring_pack_prepare"] = CommandSpec(
        add_arguments=_add_pack_prepare_arguments,
        args_factory=_pack_prepare_args,
        run=_run_pack_prepare,
    )
    specs["authoring_backend_invoke"] = CommandSpec(
        add_arguments=_add_backend_invoke_arguments,
        args_factory=_backend_invoke_args,
        run=_run_backend_invoke,
    )
    return specs


def _add_deferred_arguments(parser: argparse.ArgumentParser) -> None:
    del parser


def _add_preflight_github_sync_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--evidence-mode", choices=("github-synced", "local-context"), default="github-synced")
    parser.add_argument("--format", choices=("text", "json"), default="text", dest="output_format")
    parser.add_argument("--allow-default-branch-fallback", action="store_true")
    parser.add_argument("--repo-root")
    parser.add_argument("--ref")
    parser.add_argument("--source-path", action="append")
    parser.add_argument("--expected-source-manifest")
    parser.add_argument("--expected-source-hash")
    parser.add_argument("--provided-context-path", action="append")
    parser.add_argument("--diff-summary")
    parser.add_argument("--unsynced-reason")


def _add_pack_prepare_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--preflight", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--format", choices=("text", "json"), default="text", dest="output_format")
    parser.add_argument("--mode", choices=("initiative", "epic", "issue", "selected-skeleton"))
    parser.add_argument("--source-manifest")
    parser.add_argument("--stale-if")


def _add_backend_invoke_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--prompt-pack", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--format", choices=("text", "json"), default="text", dest="output_format")
    parser.add_argument("--backend-command")
    parser.add_argument("--slug")
    parser.add_argument("--prompt")
    parser.add_argument("--evidence-mode", choices=("github-synced", "local-context"), default="github-synced")
    parser.add_argument("--timeout-seconds", type=float)
    parser.add_argument("--dry-run", action="store_true")


def _preflight_github_sync_args(ns: argparse.Namespace) -> CommandArgs:
    return AuthoringPreflightGithubSyncArgs(
        evidence_mode=ns.evidence_mode,
        output_format=ns.output_format,
        allow_default_branch_fallback=bool(ns.allow_default_branch_fallback),
        repo_root=Path(ns.repo_root) if ns.repo_root else None,
        ref=ns.ref,
        source_paths=tuple(ns.source_path or ()),
        expected_source_manifest=Path(ns.expected_source_manifest) if ns.expected_source_manifest else None,
        expected_source_hash=ns.expected_source_hash,
        provided_context_paths=tuple(ns.provided_context_path or ()),
        diff_summary=ns.diff_summary,
        unsynced_reason=ns.unsynced_reason,
    )


def _pack_prepare_args(ns: argparse.Namespace) -> CommandArgs:
    return AuthoringPackPrepareArgs(
        preflight=Path(ns.preflight),
        output_dir=Path(ns.output_dir),
        output_format=ns.output_format,
        mode=ns.mode,
        source_manifest=Path(ns.source_manifest) if ns.source_manifest else None,
        stale_if=Path(ns.stale_if) if ns.stale_if else None,
    )


def _backend_invoke_args(ns: argparse.Namespace) -> CommandArgs:
    return AuthoringBackendInvokeArgs(
        prompt_pack=Path(ns.prompt_pack),
        output_dir=Path(ns.output_dir),
        output_format=ns.output_format,
        backend_command=ns.backend_command,
        slug=ns.slug,
        prompt=ns.prompt,
        evidence_mode=ns.evidence_mode,
        timeout_seconds=ns.timeout_seconds,
        dry_run=bool(ns.dry_run),
    )


def _deferred_args_factory(*, command: str, next_issue: str):
    def _deferred_args(ns: argparse.Namespace) -> CommandArgs:
        del ns
        return AuthoringDeferredArgs(command=command, next_issue=next_issue)

    return _deferred_args


def _run_preflight_github_sync(args: CommandArgs, use_cases: UseCases) -> CommandOutcome:
    del use_cases
    preflight_args = _expect_preflight_github_sync_args(args)
    try:
        result = run_github_sync_preflight(
            GitHubSyncPreflightRequest(
                repo_root=preflight_args.repo_root,
                evidence_mode=preflight_args.evidence_mode,  # type: ignore[arg-type]
                ref=preflight_args.ref,
                allow_default_branch_fallback=preflight_args.allow_default_branch_fallback,
                source_paths=preflight_args.source_paths,
                expected_source_manifest=preflight_args.expected_source_manifest,
                expected_source_hash=preflight_args.expected_source_hash,
                provided_context_paths=preflight_args.provided_context_paths,
                diff_summary=preflight_args.diff_summary,
                unsynced_reason=preflight_args.unsynced_reason,
            )
        )
    except ValueError as error:
        return CommandOutcome(
            exit_code=2,
            text=CliText(stdout_lines=[], stderr_lines=[f"error: {error}"], warnings=[]),
        )
    exit_code = 0 if result.status == "pass" else 1
    if preflight_args.output_format == "json":
        stdout_lines = [render_preflight_json(result)]
    else:
        stdout_lines = render_preflight_text(result)
    return CommandOutcome(
        exit_code=exit_code,
        text=CliText(stdout_lines=stdout_lines, stderr_lines=[], warnings=[]),
    )


def _run_pack_prepare(args: CommandArgs, use_cases: UseCases) -> CommandOutcome:
    del use_cases
    pack_args = _expect_pack_prepare_args(args)
    result = prepare_prompt_pack(
        PromptPackPrepareRequest(
            preflight_path=pack_args.preflight,
            output_dir=pack_args.output_dir,
            output_format=pack_args.output_format,  # type: ignore[arg-type]
            mode=pack_args.mode,  # type: ignore[arg-type]
            source_manifest_path=pack_args.source_manifest,
            stale_if_path=pack_args.stale_if,
        )
    )
    exit_code = 0 if result.status == "pass" else 1
    if pack_args.output_format == "json":
        stdout_lines = [render_pack_prepare_json(result)]
    else:
        stdout_lines = render_pack_prepare_text(result)
    return CommandOutcome(
        exit_code=exit_code,
        text=CliText(stdout_lines=stdout_lines, stderr_lines=[], warnings=[]),
    )


def _run_backend_invoke(args: CommandArgs, use_cases: UseCases) -> CommandOutcome:
    del use_cases
    backend_args = _expect_backend_invoke_args(args)
    result = invoke_backend(
        BackendInvokeRequest(
            prompt_pack=backend_args.prompt_pack,
            output_dir=backend_args.output_dir,
            output_format=backend_args.output_format,  # type: ignore[arg-type]
            backend_command=backend_args.backend_command,
            slug=backend_args.slug,
            prompt=backend_args.prompt,
            evidence_mode=backend_args.evidence_mode,  # type: ignore[arg-type]
            timeout_seconds=backend_args.timeout_seconds,
            dry_run=backend_args.dry_run,
        )
    )
    exit_code = 0 if result.status == "pass" else 1
    if backend_args.output_format == "json":
        stdout_lines = [render_backend_invoke_json(result)]
    else:
        stdout_lines = render_backend_invoke_text(result)
    return CommandOutcome(
        exit_code=exit_code,
        text=CliText(stdout_lines=stdout_lines, stderr_lines=[], warnings=[]),
    )


def _run_deferred(args: CommandArgs, use_cases: UseCases) -> CommandOutcome:
    del use_cases
    deferred_args = _expect_deferred_args(args)
    return CommandOutcome(
        exit_code=1,
        text=CliText(
            stdout_lines=[
                f"spec-dock: deferred (authoring) command={deferred_args.command}",
                "status=deferred",
                "authority=evidence_only",
                f"next_issue={deferred_args.next_issue}",
                "reason=not_implemented_in_this_issue",
            ],
            stderr_lines=[],
            warnings=[],
        ),
    )


def _expect_deferred_args(args: CommandArgs) -> AuthoringDeferredArgs:
    if not isinstance(args, AuthoringDeferredArgs):
        raise RuntimeError("Invalid command args for authoring")
    return args


def _expect_preflight_github_sync_args(args: CommandArgs) -> AuthoringPreflightGithubSyncArgs:
    if not isinstance(args, AuthoringPreflightGithubSyncArgs):
        raise RuntimeError("Invalid command args for authoring preflight github-sync")
    return args


def _expect_pack_prepare_args(args: CommandArgs) -> AuthoringPackPrepareArgs:
    if not isinstance(args, AuthoringPackPrepareArgs):
        raise RuntimeError("Invalid command args for authoring pack prepare")
    return args


def _expect_backend_invoke_args(args: CommandArgs) -> AuthoringBackendInvokeArgs:
    if not isinstance(args, AuthoringBackendInvokeArgs):
        raise RuntimeError("Invalid command args for authoring backend invoke")
    return args
