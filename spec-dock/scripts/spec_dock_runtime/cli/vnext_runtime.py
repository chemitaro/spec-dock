"""Typed vNext CLI execution from one resolved Git worktree and engine."""

from __future__ import annotations

from dataclasses import dataclass, replace
import json
from pathlib import Path
import subprocess
import sys
from typing import TYPE_CHECKING

from spec_dock_runtime.application.active_selection import show_active_selection
from spec_dock_runtime.application.installation_update_vnext import initial_worktree_id
from spec_dock_runtime.application.scope_query import list_scopes, load_scope_views, show_scope
from spec_dock_runtime.cli.admission import AdmissionError
from spec_dock_runtime.cli.catalog import MUTATING_LEAF_PATHS, RECOVERY_LEAF_COMMANDS, requires_confirmation
from spec_dock_runtime.cli.options import completion_script, explicit_help, parse_vnext_output
from spec_dock_runtime.commands.active_vnext import run_active_change, run_active_show
from spec_dock_runtime.commands.artifact_vnext import run_artifact_change, run_artifact_query
from spec_dock_runtime.commands.branch_vnext import run_branch_command
from spec_dock_runtime.commands.dependency_vnext import run_dependency_change, run_dependency_query
from spec_dock_runtime.commands.installation_vnext import (
    run_installation_init,
    run_installation_show,
    run_installation_uninstall,
    run_installation_update,
)
from spec_dock_runtime.commands.scope_create_vnext import run_scope_create
from spec_dock_runtime.commands.scope_delete_vnext import run_scope_delete
from spec_dock_runtime.commands.scope_import_vnext import run_scope_import
from spec_dock_runtime.commands.scope_lifecycle_vnext import run_scope_lifecycle
from spec_dock_runtime.commands.scope_query_vnext import run_scope_edit, run_scope_query
from spec_dock_runtime.commands.work_vnext import WorkContext, run_work_finish, run_work_start
from spec_dock_runtime.commands.workbench_vnext import run_workbench_copy
from spec_dock_runtime.commands.workspace_diagnostics_vnext import (
    run_ci_workspace_validation,
    run_workspace_diagnostics,
)
from spec_dock_runtime.commands.workspace_migrate_vnext import run_workspace_migrate
from spec_dock_runtime.commands.workspace_sync_vnext import run_workspace_sync
from spec_dock_runtime.commands.worktree_vnext import run_worktree_change, run_worktree_query
from spec_dock_runtime.domain.operation import ROLLBACK_COMMANDS
from spec_dock_runtime.domain.selectors import ScopeIdSelector, parse_scope_selector
from spec_dock_runtime.infra.control_store import load_control
from spec_dock_runtime.infra.git_cli import git_common_directory, sanitized_git_environment
from spec_dock_runtime.infra.github_lifecycle import GithubIssueGateway, RemoteIssueError
from spec_dock_runtime.infra.operation_journal import JournalStore
from spec_dock_runtime.infra.writer_lock import WriterLockBusy
from spec_dock_runtime.presentation.envelope import (
    Diagnostic,
    Effect,
    OperationResult,
    Recovery,
    TargetRef,
    render_json,
    render_text,
)
from spec_dock_runtime.presentation.errors import CliMessageData, CompletionData

if TYPE_CHECKING:
    import argparse
    from collections.abc import Sequence

    from spec_dock.runtime_loader import VerifiedEngine


@dataclass(frozen=True)
class RuntimeOutput:
    exit_code: int
    stdout: str
    stderr: str


class ExpectationMismatch(ValueError):
    """A caller-provided target guard disagrees with the current snapshot."""


def _repository_root(candidate: Path) -> Path:
    try:
        result = subprocess.run(
            ["git", "-C", str(candidate), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
            env=sanitized_git_environment(),
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ValueError("project Git worktree could not be resolved") from error
    if result.returncode != 0 or not result.stdout.strip():
        raise ValueError("project is not a Git worktree")
    return Path(result.stdout.strip()).resolve(strict=True)


def _context(ns: object, *, invocation_cwd: Path, engine_digest: str) -> WorkContext:
    raw_project = getattr(ns, "project", None)
    candidate = (
        Path(raw_project).expanduser().resolve(strict=True) if raw_project else invocation_cwd.resolve(strict=True)
    )
    root = _repository_root(candidate)
    if raw_project and root != candidate:
        raise ValueError("--project must name the Git worktree root")
    common = git_common_directory(root)
    control = load_control(common)
    if getattr(ns, "command_path", None) == "installation update" and (
        control is None or control.mode == "uninitialized"
    ):
        if control is not None and control.engine_digest != engine_digest:
            raise ValueError("external engine does not match uninitialized repository control")
        return WorkContext(
            root, common, initial_worktree_id(root), engine_digest, 0 if control is None else control.epoch
        )
    if (
        control is not None
        and getattr(ns, "command_path", None) == "installation update"
        and getattr(ns, "activate_engine", False)
        and control.mode == "maintenance"
    ):
        matches = [
            entry for entry in control.worktrees if entry.active and Path(entry.root).resolve(strict=True) == root
        ]
        if len(matches) != 1:
            raise ValueError("current worktree is not uniquely registered")
        return WorkContext(root, common, matches[0].id, control.engine_digest, control.epoch)
    if control is None or control.engine_digest != engine_digest:
        raise ValueError("external engine does not match repository control")
    matches = [entry for entry in control.worktrees if entry.active and Path(entry.root).resolve(strict=True) == root]
    if len(matches) != 1:
        raise ValueError("current worktree is not uniquely registered")
    return WorkContext(root, common, matches[0].id, engine_digest, control.epoch)


def _failure(
    command: str, code: str, message: str, exit_code: int, *, json_mode: bool, target: TargetRef | None = None
) -> RuntimeOutput:
    result = OperationResult(
        command=command,
        status="partial" if exit_code == 6 else "failed",
        data=CliMessageData(None),
        exit_code=exit_code,
        target=target,
        effects=(Effect("operation", "unknown", None),) if exit_code == 6 else (),
        error=Diagnostic(code, message, {}),
    )
    if json_mode:
        return RuntimeOutput(exit_code, render_json(result), "")
    stdout, stderr = render_text(result)
    return RuntimeOutput(exit_code, stdout, stderr)


def _journal_receipt_failure(
    ns: argparse.Namespace,
    common_dir: Path | None,
    before: set[str],
    *,
    json_mode: bool,
    target: TargetRef | None,
) -> RuntimeOutput | None:
    if common_dir is None or ns.command_path not in RECOVERY_LEAF_COMMANDS:
        return None
    command = RECOVERY_LEAF_COMMANDS[ns.command_path]
    try:
        candidates = [
            record
            for record in JournalStore(common_dir).pending()
            if record.command == command
            and (record.operation_id not in before or record.operation_id in {ns.resume, ns.rollback})
            and any(effect.status in {"intent", "succeeded", "unknown"} for effect in record.effects)
        ]
    except (OSError, ValueError):
        return None
    if len(candidates) != 1:
        return None
    record = candidates[0]
    fixed = dict(record.fixed_targets)
    if target is None:
        resolved = fixed.get("scope") or fixed.get("target")
        if resolved is not None:
            target = TargetRef(
                requested=resolved,
                id=resolved,
                kind=fixed.get("kind", "scope"),
                backend=fixed.get("backend", "unknown"),
                snapshot_id="",
            )
    effects = tuple(
        Effect(
            effect.id,
            "unknown"
            if effect.status in {"intent", "unknown"}
            else "succeeded"
            if effect.status == "succeeded"
            else "failed",
            effect.target,
        )
        for effect in record.effects
    )
    result = OperationResult(
        command=ns.command_path,
        status="partial",
        data=CliMessageData(None),
        exit_code=6,
        operation_id=record.operation_id,
        target=target,
        effects=effects,
        error=Diagnostic("EFFECT_STATE_UNKNOWN", "operation stopped; inspect recorded effects before recovery", {}),
        recovery=Recovery(
            record.operation_id,
            True,
            command in ROLLBACK_COMMANDS,
            (),
            "Inspect the fixed target and options in the operation journal before --resume or --rollback.",
        ),
    )
    if json_mode:
        return RuntimeOutput(6, render_json(result), "")
    stdout, stderr = render_text(result)
    return RuntimeOutput(6, stdout, stderr)


def _classified_failure(
    ns: argparse.Namespace,
    common_dir: Path | None,
    before: set[str],
    code: str,
    message: str,
    exit_code: int,
    *,
    json_mode: bool,
    target: TargetRef | None,
) -> RuntimeOutput:
    receipt = _journal_receipt_failure(ns, common_dir, before, json_mode=json_mode, target=target)
    if receipt is not None:
        return receipt
    return _failure(ns.command_path, code, message, exit_code, json_mode=json_mode, target=target)


def _resolved_scope_target(
    ns: argparse.Namespace, context: WorkContext, *, requested: str | None = None
) -> TargetRef | None:
    if not ns.command_path.startswith(("scope ", "work ", "branch ", "dependency ", "artifact ", "workbench ")):
        return None
    selector = getattr(ns, "target", None) or getattr(ns, "scope", None)
    if not isinstance(selector, str):
        return None
    views = load_scope_views(context.repo_root / "spec-dock")
    if selector == "@root" and ns.command_path.startswith("artifact "):
        return TargetRef("@root", "@root", "workspace", "local", list_scopes(views).snapshot_id)
    selection = show_active_selection(repo_root=context.repo_root, worktree_id=context.worktree_id)
    try:
        view = show_scope(views, selector, selection=selection)
    except LookupError:
        if getattr(ns, "resume", None) or getattr(ns, "rollback", None):
            return None
        raise
    return TargetRef(
        requested=requested or selector,
        id=view.id,
        kind=view.kind,
        backend="github" if view.github_ref is not None else "local",
        snapshot_id=list_scopes(views).snapshot_id,
    )


def _confirm_before_effect(
    ns: argparse.Namespace,
    argv: Sequence[str],
    *,
    invocation_cwd: Path,
    engine_digest: str,
    engine_version: str,
    engine_pin: VerifiedEngine | None,
) -> RuntimeOutput | None:
    if ns.command_path.startswith("scope create ") and getattr(ns, "resume", None):
        return None
    if (
        ns.dry_run
        or ns.yes
        or not requires_confirmation(
            ns.command_path, backend=getattr(ns, "backend", None), on_conflict=getattr(ns, "on_conflict", None)
        )
    ):
        return None
    if ns.non_interactive or not sys.stdin.isatty():
        return _failure(ns.command_path, "CONFIRMATION_REQUIRED", "confirmation requires --yes", 3, json_mode=ns.json)
    target = getattr(ns, "target", None) or getattr(ns, "scope", None) or getattr(ns, "worktree_ref", None)
    planned_effects: list[dict[str, object]] = []
    if not (getattr(ns, "resume", None) or getattr(ns, "rollback", None) or getattr(ns, "recover", None)):
        preview = run_vnext(
            [*argv, "--dry-run", "--json"],
            invocation_cwd=invocation_cwd,
            engine_digest=engine_digest,
            engine_version=engine_version,
            engine_pin=engine_pin,
        )
        payload = json.loads(preview.stdout)
        if preview.exit_code:
            error = payload.get("error") or {}
            return _failure(
                ns.command_path,
                str(error.get("code", "PRECONDITION_FAILED")),
                str(error.get("message", "confirmation plan failed")),
                preview.exit_code,
                json_mode=ns.json,
            )
        planned_effects = payload.get("effects", [])
        target_ref = payload.get("target")
        if isinstance(target_ref, dict):
            target = target_ref.get("id") or target
        if not target:
            target = next((effect.get("target") for effect in planned_effects if effect.get("target")), None)
    else:
        target = target or getattr(ns, "path", None) or getattr(ns, "resume", None) or getattr(ns, "rollback", None)
    project = getattr(ns, "project", None) or invocation_cwd
    print(f"Target: {target or ns.command_path}", file=sys.stderr)
    print(f"Repository: {Path(project).expanduser().resolve()}", file=sys.stderr)
    writes = ", ".join(str(effect.get("kind")) for effect in planned_effects) or ns.command_path
    print(f"Writes: {writes}", file=sys.stderr)
    print("Confirm [yes/no]: ", end="", file=sys.stderr, flush=True)
    if sys.stdin.readline().strip().lower() not in {"yes", "y"}:
        return _failure(ns.command_path, "CONFIRMATION_DECLINED", "operation was not confirmed", 3, json_mode=ns.json)
    ns.yes = True
    return None


def _enforce_expectations(ns: argparse.Namespace, context: WorkContext) -> None:
    command = ns.command_path
    selectors = {
        field: value
        for field in ("target", "parent", "scope", "from_target", "to_target")
        if isinstance((value := getattr(ns, field, None)), str)
    }
    active_fields = {
        field: value for field, value in selectors.items() if value in {"@current", "@initiative", "@epic", "@issue"}
    }
    uses_current = bool(active_fields)
    expected_current = getattr(ns, "expect_current", None)
    if uses_current and command in MUTATING_LEAF_PATHS and ns.non_interactive and not expected_current:
        raise ValueError("--expect-current is required for a non-interactive active selector mutation")
    selection = None
    if expected_current is not None:
        parsed = parse_scope_selector(expected_current)
        if not isinstance(parsed, ScopeIdSelector):
            raise ValueError("--expect-current requires a complete Scope ID")
        selection = show_active_selection(repo_root=context.repo_root, worktree_id=context.worktree_id)
        if selection.focus_id != parsed.id:
            raise ExpectationMismatch("current Scope changed since the expected selection")

    views = None
    if uses_current and command in MUTATING_LEAF_PATHS:
        if selection is None:
            selection = show_active_selection(repo_root=context.repo_root, worktree_id=context.worktree_id)
        views = load_scope_views(context.repo_root / "spec-dock")
        for field, value in active_fields.items():
            setattr(ns, field, show_scope(views, value, selection=selection).id)

    expected_backend = getattr(ns, "expect_backend", None)
    if expected_backend is None:
        return
    target = getattr(ns, "target", None) or getattr(ns, "scope", None)
    if not isinstance(target, str) or command.startswith(("scope create", "scope import")):
        raise ValueError("--expect-backend requires one existing Scope target")
    if selection is None:
        selection = show_active_selection(repo_root=context.repo_root, worktree_id=context.worktree_id)
    if views is None:
        views = load_scope_views(context.repo_root / "spec-dock")
    view = show_scope(views, target, selection=selection)
    actual_backend = "github" if view.github_ref is not None else "local"
    if actual_backend != expected_backend:
        raise ExpectationMismatch("Scope backend changed since the expected target")


def run_vnext(
    argv: Sequence[str],
    *,
    invocation_cwd: Path,
    engine_digest: str,
    engine_version: str,
    engine_pin: VerifiedEngine | None = None,
    preflight_root: Path | None = None,
    preflight_common: Path | None = None,
) -> RuntimeOutput:
    """Parse once, bind to a registered worktree, then dispatch supported leaves."""
    parsed = parse_vnext_output(argv, engine_version=engine_version, engine_digest=engine_digest)
    if parsed.namespace is None:
        assert parsed.exit_code is not None
        return RuntimeOutput(parsed.exit_code, parsed.stdout, parsed.stderr)
    ns = parsed.namespace
    json_mode = bool(ns.json)
    journal_common: Path | None = None
    journal_before: set[str] = set()
    target_ref: TargetRef | None = None
    requested_target = getattr(ns, "target", None) or getattr(ns, "scope", None)
    try:
        if ns.command_path in {"help", "completion"}:
            content = explicit_help(ns.help_path) if ns.command_path == "help" else completion_script(ns.shell)
            if json_mode:
                data = CliMessageData(content) if ns.command_path == "help" else CompletionData(ns.shell, content)
                result = OperationResult(ns.command_path, "succeeded", data, 0)
                return RuntimeOutput(0, render_json(result), "")
            return RuntimeOutput(0, content, "")
        declined = _confirm_before_effect(
            ns,
            argv,
            invocation_cwd=invocation_cwd,
            engine_digest=engine_digest,
            engine_version=engine_version,
            engine_pin=engine_pin,
        )
        if declined is not None:
            return declined
        if ns.command_path not in {
            "work start",
            "work finish",
            "active show",
            "active set",
            "active clear",
            "scope list",
            "scope show",
            "scope edit",
            "scope create initiative",
            "scope create epic",
            "scope create issue",
            "scope import github initiative",
            "scope import github epic",
            "scope import github issue",
            "scope delete",
            "scope close",
            "scope reopen",
            "branch show",
            "branch create",
            "branch switch",
            "dependency list",
            "dependency check",
            "dependency add",
            "dependency remove",
            "artifact list",
            "artifact show",
            "artifact create",
            "artifact import file",
            "worktree list",
            "worktree show",
            "worktree create",
            "worktree remove",
            "worktree bootstrap",
            "workbench copy",
            "workspace validate",
            "workspace doctor",
            "workspace sync",
            "workspace migrate",
            "installation show",
            "installation init",
            "installation update",
            "installation uninstall",
        }:
            raise ValueError("vNext command execution is not yet connected")
        if ns.command_path == "installation init":
            requested = Path(ns.path).expanduser()
            if not requested.is_absolute():
                requested = invocation_cwd / requested
            requested = requested.resolve(strict=True)
            root = _repository_root(requested)
            if preflight_root is not None and root != preflight_root:
                raise ValueError("runtime project differs from verified preflight root")
            common = git_common_directory(root)
            if preflight_common is not None and common != preflight_common:
                raise ValueError("runtime Git common directory differs from verified preflight")
            if root != requested:
                raise ValueError("installation init PATH must name a Git worktree root")
            if ns.project and Path(ns.project).expanduser().resolve(strict=True) != requested:
                raise ValueError("--project and installation init PATH must name the same worktree")
            result = run_installation_init(
                ns,
                repo_root=root,
                common_dir=common,
                engine_digest=engine_digest,
                engine_version=engine_version,
                engine_pin=engine_pin,
            )
            if json_mode:
                return RuntimeOutput(result.exit_code, render_json(result), "")
            stdout, stderr = render_text(result)
            return RuntimeOutput(result.exit_code, stdout, stderr)
        if ns.command_path == "workspace validate" and ns.ci:
            raw_project = getattr(ns, "project", None)
            candidate = Path(raw_project).expanduser().resolve(strict=True) if raw_project else invocation_cwd
            root = _repository_root(candidate)
            if raw_project and root != candidate:
                raise ValueError("--project must name the Git worktree root")
            result = run_ci_workspace_validation(ns, root)
            if json_mode:
                return RuntimeOutput(result.exit_code, render_json(result), "")
            stdout, stderr = render_text(result)
            return RuntimeOutput(result.exit_code, stdout, stderr)
        context = _context(ns, invocation_cwd=invocation_cwd, engine_digest=engine_digest)
        if preflight_root is not None and context.repo_root != preflight_root:
            raise ValueError("runtime project differs from verified preflight root")
        if preflight_common is not None and context.common_dir != preflight_common:
            raise ValueError("runtime Git common directory differs from verified preflight")
        _enforce_expectations(ns, context)
        target_ref = _resolved_scope_target(ns, context, requested=requested_target)
        journal_common = context.common_dir
        journal_before = {record.operation_id for record in JournalStore(journal_common).pending()}
        if ns.command_path in {"scope list", "scope show"}:
            result = run_scope_query(ns, context)
        elif ns.command_path in {"scope create initiative", "scope create epic", "scope create issue"}:
            result = run_scope_create(ns, context, gateway=GithubIssueGateway(timeout=ns.timeout))
        elif ns.command_path in {
            "scope import github initiative",
            "scope import github epic",
            "scope import github issue",
        }:
            result = run_scope_import(ns, context, gateway=GithubIssueGateway(timeout=ns.timeout))
        elif ns.command_path == "scope delete":
            result = run_scope_delete(ns, context)
        elif ns.command_path in {"scope close", "scope reopen"}:
            result = run_scope_lifecycle(ns, context, gateway=GithubIssueGateway(timeout=ns.timeout))
        elif ns.command_path in {"branch show", "branch create", "branch switch"}:
            result = run_branch_command(ns, context)
        elif ns.command_path in {"dependency list", "dependency check"}:
            result = run_dependency_query(ns, context, gateway=GithubIssueGateway(timeout=ns.timeout))
        elif ns.command_path in {"dependency add", "dependency remove"}:
            result = run_dependency_change(ns, context)
        elif ns.command_path in {"artifact list", "artifact show"}:
            result = run_artifact_query(ns, context)
        elif ns.command_path in {"artifact create", "artifact import file"}:
            result = run_artifact_change(ns, context, invocation_cwd=invocation_cwd)
        elif ns.command_path in {"worktree list", "worktree show"}:
            result = run_worktree_query(ns, context)
        elif ns.command_path in {"worktree create", "worktree remove", "worktree bootstrap"}:
            result = run_worktree_change(ns, context)
        elif ns.command_path == "workbench copy":
            result = run_workbench_copy(ns, context)
        elif ns.command_path in {"workspace validate", "workspace doctor"}:
            result = run_workspace_diagnostics(ns, context)
        elif ns.command_path == "workspace sync":
            result = run_workspace_sync(ns, context, gateway=GithubIssueGateway(timeout=ns.timeout))
        elif ns.command_path == "workspace migrate":
            result = run_workspace_migrate(ns, context, invocation_cwd=invocation_cwd)
        elif ns.command_path == "installation show":
            result = run_installation_show(ns, context, engine_version=engine_version, invocation_cwd=invocation_cwd)
        elif ns.command_path == "installation update":
            result = run_installation_update(
                ns, context, invocation_cwd=invocation_cwd, engine_version=engine_version, engine_pin=engine_pin
            )
        elif ns.command_path == "installation uninstall":
            result = run_installation_uninstall(ns, context, invocation_cwd=invocation_cwd)
        elif ns.command_path == "scope edit":
            result = run_scope_edit(ns, context)
        elif ns.command_path == "active show":
            result = run_active_show(context)
        elif ns.command_path in {"active set", "active clear"}:
            result = run_active_change(ns, context)
        elif ns.command_path == "work start":
            gateway = GithubIssueGateway(timeout=ns.timeout)
            result = run_work_start(ns, context, gateway=gateway)
        else:
            gateway = GithubIssueGateway(timeout=ns.timeout)
            result = run_work_finish(ns, context, gateway=gateway)
    except WriterLockBusy:
        return _failure(
            ns.command_path, "WRITER_LOCK_BUSY", "writer lock is busy", 3, json_mode=json_mode, target=target_ref
        )
    except AdmissionError as error:
        return _classified_failure(
            ns, journal_common, journal_before, error.code, str(error), 3, json_mode=json_mode, target=target_ref
        )
    except RemoteIssueError as error:
        return _classified_failure(
            ns,
            journal_common,
            journal_before,
            error.code,
            str(error),
            error.exit_code,
            json_mode=json_mode,
            target=target_ref,
        )
    except LookupError as error:
        return _classified_failure(
            ns,
            journal_common,
            journal_before,
            "SCOPE_NOT_FOUND",
            str(error),
            4,
            json_mode=json_mode,
            target=target_ref,
        )
    except ExpectationMismatch as error:
        return _classified_failure(
            ns,
            journal_common,
            journal_before,
            "STATE_CONFLICT",
            str(error),
            3,
            json_mode=json_mode,
            target=target_ref,
        )
    except ValueError as error:
        return _classified_failure(
            ns,
            journal_common,
            journal_before,
            "PRECONDITION_FAILED",
            str(error),
            3,
            json_mode=json_mode,
            target=target_ref,
        )
    except RuntimeError:
        receipt = _journal_receipt_failure(ns, journal_common, journal_before, json_mode=json_mode, target=target_ref)
        if receipt is not None:
            return receipt
        return _failure(
            ns.command_path,
            "INTERNAL_ERROR",
            "command failed before any effect",
            1,
            json_mode=json_mode,
            target=target_ref,
        )
    except OSError:
        receipt = _journal_receipt_failure(ns, journal_common, journal_before, json_mode=json_mode, target=target_ref)
        if receipt is not None:
            return receipt
        return _failure(
            ns.command_path, "LOCAL_IO_FAILED", "local I/O operation failed", 5, json_mode=json_mode, target=target_ref
        )
    if target_ref is not None and result.target is None:
        result = replace(result, target=target_ref)
    if json_mode:
        return RuntimeOutput(result.exit_code, render_json(result), "")
    stdout, stderr = render_text(result)
    return RuntimeOutput(result.exit_code, stdout, stderr)
