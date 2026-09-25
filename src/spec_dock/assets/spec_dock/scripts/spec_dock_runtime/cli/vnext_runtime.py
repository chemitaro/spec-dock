"""Typed vNext CLI execution from one resolved Git worktree and engine."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import subprocess
import sys
from typing import TYPE_CHECKING, cast

from spec_dock.installation.source import resolve_fixed_source
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
from spec_dock_runtime.commands.scope_result_vnext import (
    ScopeData,
    ScopeFailureData,
    ScopeStatusData,
    project_scope,
)
from spec_dock_runtime.commands.work_vnext import WorkContext, run_work_finish, run_work_start
from spec_dock_runtime.commands.workbench_vnext import run_workbench_copy
from spec_dock_runtime.commands.workspace_diagnostics_vnext import (
    run_ci_workspace_validation,
    run_workspace_diagnostics,
)
from spec_dock_runtime.commands.workspace_migrate_vnext import run_workspace_migrate
from spec_dock_runtime.commands.workspace_sync_vnext import run_workspace_sync
from spec_dock_runtime.commands.worktree_vnext import run_worktree_change, run_worktree_query
from spec_dock_runtime.domain.selectors import ScopeIdSelector, parse_scope_selector
from spec_dock_runtime.infra.control_store import load_control
from spec_dock_runtime.infra.failure_receipts import pending_failure_receipts, pending_receipt_ids
from spec_dock_runtime.infra.git_cli import git_common_directory, sanitized_git_environment
from spec_dock_runtime.infra.github_lifecycle import GithubIssueGateway, RemoteIssueError
from spec_dock_runtime.infra.writer_lock import WriterLockBusy
from spec_dock_runtime.presentation.envelope import (
    Diagnostic,
    Effect,
    EffectStatus,
    OperationResult,
    Recovery,
    TargetRef,
    render_json,
    render_text,
)
from spec_dock_runtime.presentation.errors import CliMessageData, CompletionData, NonBlockingFailureData

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


_NONBLOCKING_INSPECTION: dict[str, str] = {
    "scope edit": "Run scope show for the fixed Scope ID and compare its title and revision.",
    "active set": "Run active show and compare the focus and revision.",
    "active clear": "Run active show and compare the focus and revision.",
    "branch switch": "Inspect Git HEAD and run branch show for the fixed Scope ID.",
    "dependency add": "Run dependency list for the affected Scope and inspect the declared edge.",
    "dependency remove": "Run dependency list for the affected Scope and inspect the declared edge.",
    "artifact create": "Run artifact list for the fixed Scope and inspect the target entry.",
    "artifact import file": "Run artifact list for the fixed Scope and inspect the target entry.",
    "worktree create": "Run worktree list and inspect the target path and Git branch.",
    "worktree remove": "Run worktree list and inspect the target path and Git branch.",
    "worktree bootstrap": "Run worktree show and inspect project-owned bootstrap effects before retrying.",
    "workbench copy": "Inspect the source and destination Workbench entries before retrying.",
    "workspace sync": "Inspect the published generation pointer and run workspace validate before retrying.",
}
if set(_NONBLOCKING_INSPECTION) != MUTATING_LEAF_PATHS - set(RECOVERY_LEAF_COMMANDS):
    raise RuntimeError("non-blocking failure inspection must cover every non-D16 writer")


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
    command: str,
    code: str,
    message: str,
    exit_code: int,
    *,
    json_mode: bool,
    target: TargetRef | None = None,
    context: WorkContext | None = None,
) -> RuntimeOutput:
    data, target = _failure_data(command, context, target)
    result = OperationResult(
        command=command,
        status="partial" if exit_code == 6 else "failed",
        data=data,
        exit_code=exit_code,
        target=target,
        effects=(Effect("operation", "unknown", None),) if exit_code == 6 else (),
        error=Diagnostic(code, message, {}),
    )
    if json_mode:
        return RuntimeOutput(exit_code, render_json(result), "")
    stdout, stderr = render_text(result)
    return RuntimeOutput(exit_code, stdout, stderr)


def _failure_data(
    command: str, context: WorkContext | None, target: TargetRef | None
) -> tuple[CliMessageData | ScopeFailureData, TargetRef | None]:
    if (
        context is None
        or target is None
        or command
        not in {
            "scope create initiative",
            "scope create epic",
            "scope create issue",
            "scope import github initiative",
            "scope import github epic",
            "scope import github issue",
            "scope show",
            "scope edit",
            "scope close",
            "scope reopen",
        }
    ):
        return CliMessageData(None), target
    try:
        projection = project_scope(context, target.id, requested=target.requested)
    except (LookupError, OSError, ValueError):
        return (
            ScopeFailureData(
                None,
                ScopeData(target.id, target.kind, target.backend, None, None, None),
                ScopeStatusData("unknown", "unknown", True),
                str(context.repo_root),
                context.worktree_id,
                target.snapshot_id,
            ),
            target,
        )
    return (
        ScopeFailureData(
            None,
            projection.scope,
            projection.status,
            projection.project,
            projection.worktree,
            projection.snapshot_id,
        ),
        projection.target,
    )


def _target_for_failure(
    ns: argparse.Namespace,
    context: WorkContext | None,
    target: TargetRef | None,
    requested: str | None,
) -> TargetRef | None:
    if target is not None or context is None:
        return target
    try:
        return _resolved_scope_target(ns, context, requested=requested)
    except (LookupError, OSError, ValueError):
        return None


def _journal_receipt_failure(
    ns: argparse.Namespace,
    common_dir: Path | None,
    before: set[str],
    *,
    json_mode: bool,
    target: TargetRef | None,
    context: WorkContext | None,
) -> RuntimeOutput | None:
    if common_dir is None or ns.command_path not in RECOVERY_LEAF_COMMANDS:
        return None
    command = RECOVERY_LEAF_COMMANDS[ns.command_path]
    try:
        candidates = [
            record
            for record in pending_failure_receipts(common_dir)
            if record.command == command
            and (record.operation_id not in before or record.operation_id in {ns.resume, ns.rollback})
        ]
    except (OSError, ValueError):
        return None
    if len(candidates) != 1:
        return None
    record = candidates[0]
    if target is None:
        resolved = record.fixed_target
        if resolved is not None:
            target = TargetRef(
                requested=resolved,
                id=resolved,
                kind=record.fixed_kind or "scope",
                backend=record.fixed_backend or "unknown",
                snapshot_id="",
            )
    effects = tuple(
        Effect(effect.kind, cast("EffectStatus", effect.status), effect.target) for effect in record.effects
    )
    effect_started = record.effect_started
    data, target = _failure_data(ns.command_path, context, target)
    result = OperationResult(
        command=ns.command_path,
        status="partial" if effect_started else "failed",
        data=data,
        exit_code=6 if effect_started else 3,
        operation_id=record.operation_id,
        target=target,
        effects=effects,
        error=Diagnostic(
            "EFFECT_STATE_UNKNOWN" if effect_started else "RECOVERY_REQUIRED",
            "operation stopped; inspect recorded effects before recovery",
            {},
        ),
        recovery=Recovery(
            record.operation_id,
            True,
            record.can_rollback,
            (),
            "Inspect the fixed target and options in the operation journal before --resume or --rollback.",
        ),
    )
    if json_mode:
        return RuntimeOutput(result.exit_code, render_json(result), "")
    stdout, stderr = render_text(result)
    return RuntimeOutput(result.exit_code, stdout, stderr)


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
    context: WorkContext | None,
    requested: str | None,
) -> RuntimeOutput:
    target = _target_for_failure(ns, context, target, requested)
    receipt = _journal_receipt_failure(ns, common_dir, before, json_mode=json_mode, target=target, context=context)
    if receipt is not None:
        return receipt
    return _failure(ns.command_path, code, message, exit_code, json_mode=json_mode, target=target, context=context)


def _nonblocking_io_receipt(
    ns: argparse.Namespace, context: WorkContext | None, target: TargetRef | None, *, json_mode: bool
) -> RuntimeOutput | None:
    if ns.command_path != "scope edit" or context is None or target is None:
        return None
    try:
        projection = project_scope(context, target.id, requested=target.requested)
        if projection.snapshot_id == target.snapshot_id:
            return None
        views = load_scope_views(context.repo_root / "spec-dock")
        current = show_scope(views, target.id, selection=None)
        observed = "succeeded" if current.title == ns.title.strip() else "unknown"
        data = ScopeFailureData(
            None, projection.scope, projection.status, projection.project, projection.worktree, projection.snapshot_id
        )
        receipt_target = projection.target
    except (LookupError, OSError, ValueError):
        observed = "unknown"
        data = ScopeFailureData(
            None,
            ScopeData(target.id, target.kind, target.backend, None, None, None),
            ScopeStatusData("unknown", "unknown", True),
            str(context.repo_root),
            context.worktree_id,
            target.snapshot_id,
        )
        receipt_target = target
    result = OperationResult(
        command=ns.command_path,
        status="partial",
        data=data,
        exit_code=6,
        target=receipt_target,
        effects=(Effect("metadata", observed, target.id),),
        error=Diagnostic(
            "POST_PUBLISH_FAILURE",
            "local I/O failed with a possible Scope metadata change; inspect the Scope before another edit",
            {"scope_id": target.id, "observed_revision": data.scope.revision},
        ),
        recovery=Recovery(
            None,
            False,
            False,
            (),
            "Run scope show for this ID and compare the title and revision before deciding on another edit.",
        ),
    )
    if json_mode:
        return RuntimeOutput(6, render_json(result), "")
    stdout, stderr = render_text(result)
    return RuntimeOutput(6, stdout, stderr)


def _unknown_nonblocking_receipt(
    ns: argparse.Namespace, context: WorkContext | None, target: TargetRef | None, *, json_mode: bool
) -> RuntimeOutput | None:
    if context is None or ns.command_path not in _NONBLOCKING_INSPECTION:
        return None
    target_id = target.id if target is not None else None
    inspection = _NONBLOCKING_INSPECTION[ns.command_path]
    result = OperationResult(
        command=ns.command_path,
        status="partial",
        data=NonBlockingFailureData(str(context.repo_root), context.worktree_id, target_id, inspection),
        exit_code=6,
        target=target,
        effects=(Effect(ns.command_path.replace(" ", "-"), "unknown", target_id),),
        error=Diagnostic(
            "EFFECT_STATE_UNKNOWN",
            "the command stopped before its effect could be confirmed; inspect the target before retrying",
            {"target_id": target_id, "inspection": inspection},
        ),
        recovery=Recovery(None, False, False, (), inspection),
    )
    if json_mode:
        return RuntimeOutput(6, render_json(result), "")
    stdout, stderr = render_text(result)
    return RuntimeOutput(6, stdout, stderr)


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
    context: WorkContext,
    *,
    invocation_cwd: Path,
    engine_version: str,
    engine_pin: VerifiedEngine | None,
    target_ref: TargetRef | None,
    resolution_state: tuple[str, int] | None,
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
        return _failure(
            ns.command_path,
            "CONFIRMATION_REQUIRED",
            "confirmation requires --yes",
            3,
            json_mode=ns.json,
            target=target_ref,
            context=context,
        )
    target = (
        target_ref.id
        if target_ref is not None
        else (getattr(ns, "target", None) or getattr(ns, "scope", None) or getattr(ns, "worktree_ref", None))
    )
    planned_effects: tuple[Effect, ...] = ()
    migration_plan = None
    source_commit: str | None = None
    before_state = _confirmation_state(ns, context)
    if before_state != resolution_state:
        raise ExpectationMismatch("operation state changed while resolving the confirmation plan")
    if not (getattr(ns, "resume", None) or getattr(ns, "rollback", None) or getattr(ns, "recover", None)):
        preview_ns = type(ns)(**vars(ns))
        preview_ns.dry_run = True
        preview_ns.yes = True
        if ns.command_path == "installation init":
            preview = run_installation_init(
                preview_ns,
                repo_root=context.repo_root,
                common_dir=context.common_dir,
                engine_digest=context.engine_digest,
                engine_version=engine_version,
                engine_pin=engine_pin,
            )
        else:
            preview = _dispatch_regular(
                preview_ns,
                context,
                invocation_cwd=invocation_cwd,
                engine_version=engine_version,
                engine_pin=engine_pin,
            )
        if preview.exit_code:
            if ns.json:
                return RuntimeOutput(preview.exit_code, render_json(preview), "")
            stdout, stderr = render_text(preview)
            return RuntimeOutput(preview.exit_code, stdout, stderr)
        planned_effects = preview.effects
        if ns.command_path == "workspace migrate":
            migration_plan = getattr(preview_ns, "_prepared_migration_plan", None)
        if ns.command_path == "installation update":
            candidate_commit = getattr(preview.data, "source_commit", None)
            if isinstance(candidate_commit, str):
                source_commit = candidate_commit
        if preview.target is not None:
            target = preview.target.id
        if not target:
            target = next((effect.target for effect in planned_effects if effect.target), None)
    else:
        target = target or getattr(ns, "path", None) or getattr(ns, "resume", None) or getattr(ns, "rollback", None)
    print(f"Target: {target or ns.command_path}", file=sys.stderr)
    print(f"Repository: {context.repo_root}", file=sys.stderr)
    if source_commit is not None:
        print(f"Source commit: {source_commit}", file=sys.stderr)
    writes = (
        ", ".join(f"{effect.kind}:{effect.target}" for effect in planned_effects)
        if ns.command_path == "workspace migrate"
        else ", ".join(effect.kind for effect in planned_effects)
    ) or ns.command_path
    print(f"Writes: {writes}", file=sys.stderr)
    print("Confirm [yes/no]: ", end="", file=sys.stderr, flush=True)
    if sys.stdin.readline().strip().lower() not in {"yes", "y"}:
        return _failure(
            ns.command_path,
            "CONFIRMATION_DECLINED",
            "operation was not confirmed",
            3,
            json_mode=ns.json,
            target=target_ref,
            context=context,
        )
    if _confirmation_state(ns, context) != before_state:
        raise ExpectationMismatch("operation state changed while confirmation was pending")
    if source_commit is not None and (ns.version or ns.commit):
        current_source = resolve_fixed_source(version=ns.version, commit=ns.commit, timeout=ns.timeout)
        if current_source.commit != source_commit:
            raise ExpectationMismatch("installation source changed while confirmation was pending")
        ns.version = None
        ns.commit = source_commit
    if migration_plan is not None:
        ns._prepared_migration_plan = migration_plan
    ns.yes = True
    return None


def _confirmation_state(ns: argparse.Namespace, context: WorkContext) -> tuple[str, int] | None:
    if not ns.command_path.startswith(("scope ", "work ", "workbench ")):
        return None
    views = load_scope_views(context.repo_root / "spec-dock")
    selection = show_active_selection(repo_root=context.repo_root, worktree_id=context.worktree_id)
    return list_scopes(views).snapshot_id, selection.revision


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


def _dispatch_regular(
    ns: argparse.Namespace,
    context: WorkContext,
    *,
    invocation_cwd: Path,
    engine_version: str,
    engine_pin: VerifiedEngine | None,
) -> OperationResult[object]:
    command = ns.command_path
    if command in {"scope list", "scope show"}:
        return run_scope_query(ns, context)
    if command in {"scope create initiative", "scope create epic", "scope create issue"}:
        return run_scope_create(ns, context, gateway=GithubIssueGateway(timeout=ns.timeout))
    if command in {"scope import github initiative", "scope import github epic", "scope import github issue"}:
        return run_scope_import(ns, context, gateway=GithubIssueGateway(timeout=ns.timeout))
    if command == "scope delete":
        return run_scope_delete(ns, context)
    if command in {"scope close", "scope reopen"}:
        return run_scope_lifecycle(ns, context, gateway=GithubIssueGateway(timeout=ns.timeout))
    if command in {"branch show", "branch create", "branch switch"}:
        return run_branch_command(ns, context)
    if command in {"dependency list", "dependency check"}:
        return run_dependency_query(ns, context, gateway=GithubIssueGateway(timeout=ns.timeout))
    if command in {"dependency add", "dependency remove"}:
        return run_dependency_change(ns, context)
    if command in {"artifact list", "artifact show"}:
        return run_artifact_query(ns, context)
    if command in {"artifact create", "artifact import file"}:
        return run_artifact_change(ns, context, invocation_cwd=invocation_cwd)
    if command in {"worktree list", "worktree show"}:
        return run_worktree_query(ns, context)
    if command in {"worktree create", "worktree remove", "worktree bootstrap"}:
        return run_worktree_change(ns, context)
    if command == "workbench copy":
        return run_workbench_copy(ns, context)
    if command in {"workspace validate", "workspace doctor"}:
        return run_workspace_diagnostics(ns, context)
    if command == "workspace sync":
        return run_workspace_sync(ns, context, gateway=GithubIssueGateway(timeout=ns.timeout))
    if command == "workspace migrate":
        return run_workspace_migrate(ns, context, invocation_cwd=invocation_cwd)
    if command == "installation show":
        return run_installation_show(ns, context, engine_version=engine_version, invocation_cwd=invocation_cwd)
    if command == "installation update":
        return run_installation_update(
            ns, context, invocation_cwd=invocation_cwd, engine_version=engine_version, engine_pin=engine_pin
        )
    if command == "installation uninstall":
        return run_installation_uninstall(ns, context, invocation_cwd=invocation_cwd)
    if command == "scope edit":
        return run_scope_edit(ns, context)
    if command == "active show":
        return run_active_show(context)
    if command in {"active set", "active clear"}:
        return run_active_change(ns, context)
    if command == "work start":
        return run_work_start(ns, context, gateway=GithubIssueGateway(timeout=ns.timeout))
    return run_work_finish(ns, context, gateway=GithubIssueGateway(timeout=ns.timeout))


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
    context: WorkContext | None = None
    requested_target = getattr(ns, "target", None) or getattr(ns, "scope", None)
    try:
        if ns.command_path in {"help", "completion"}:
            content = explicit_help(ns.help_path) if ns.command_path == "help" else completion_script(ns.shell)
            if json_mode:
                data = CliMessageData(content) if ns.command_path == "help" else CompletionData(ns.shell, content)
                result = OperationResult(ns.command_path, "succeeded", data, 0)
                return RuntimeOutput(0, render_json(result), "")
            return RuntimeOutput(0, content, "")
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
            context = WorkContext(root, common, initial_worktree_id(root), engine_digest, 0)
            journal_common = common
            journal_before = pending_receipt_ids(common)
            declined = _confirm_before_effect(
                ns,
                context,
                invocation_cwd=invocation_cwd,
                engine_version=engine_version,
                engine_pin=engine_pin,
                target_ref=None,
                resolution_state=None,
            )
            if declined is not None:
                return declined
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
        resolution_state = (
            _confirmation_state(ns, context)
            if not ns.dry_run
            and not ns.yes
            and requires_confirmation(
                ns.command_path, backend=getattr(ns, "backend", None), on_conflict=getattr(ns, "on_conflict", None)
            )
            else None
        )
        _enforce_expectations(ns, context)
        target_ref = _resolved_scope_target(ns, context, requested=requested_target)
        declined = _confirm_before_effect(
            ns,
            context,
            invocation_cwd=invocation_cwd,
            engine_version=engine_version,
            engine_pin=engine_pin,
            target_ref=target_ref,
            resolution_state=resolution_state,
        )
        if declined is not None:
            return declined
        journal_common = context.common_dir
        journal_before = pending_receipt_ids(journal_common)
        result = _dispatch_regular(
            ns, context, invocation_cwd=invocation_cwd, engine_version=engine_version, engine_pin=engine_pin
        )
    except WriterLockBusy:
        return _failure(
            ns.command_path,
            "WRITER_LOCK_BUSY",
            "writer lock is busy",
            3,
            json_mode=json_mode,
            target=_target_for_failure(ns, context, target_ref, requested_target),
            context=context,
        )
    except AdmissionError as error:
        return _classified_failure(
            ns,
            journal_common,
            journal_before,
            error.code,
            str(error),
            3,
            json_mode=json_mode,
            target=target_ref,
            context=context,
            requested=requested_target,
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
            context=context,
            requested=requested_target,
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
            context=context,
            requested=requested_target,
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
            context=context,
            requested=requested_target,
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
            context=context,
            requested=requested_target,
        )
    except RuntimeError:
        target_ref = _target_for_failure(ns, context, target_ref, requested_target)
        receipt = _journal_receipt_failure(
            ns, journal_common, journal_before, json_mode=json_mode, target=target_ref, context=context
        )
        if receipt is not None:
            return receipt
        observed = _nonblocking_io_receipt(ns, context, target_ref, json_mode=json_mode)
        if observed is not None:
            return observed
        if ns.command_path != "scope edit":
            uncertain = _unknown_nonblocking_receipt(ns, context, target_ref, json_mode=json_mode)
            if uncertain is not None:
                return uncertain
        return _failure(
            ns.command_path,
            "INTERNAL_ERROR",
            "command failed before any effect",
            1,
            json_mode=json_mode,
            target=target_ref,
            context=context,
        )
    except OSError:
        target_ref = _target_for_failure(ns, context, target_ref, requested_target)
        receipt = _journal_receipt_failure(
            ns, journal_common, journal_before, json_mode=json_mode, target=target_ref, context=context
        )
        if receipt is not None:
            return receipt
        observed = _nonblocking_io_receipt(ns, context, target_ref, json_mode=json_mode)
        if observed is not None:
            return observed
        if ns.command_path != "scope edit":
            uncertain = _unknown_nonblocking_receipt(ns, context, target_ref, json_mode=json_mode)
            if uncertain is not None:
                return uncertain
        return _failure(
            ns.command_path,
            "LOCAL_IO_FAILED",
            "local I/O operation failed",
            5,
            json_mode=json_mode,
            target=target_ref,
            context=context,
        )
    if target_ref is not None:
        if result.target is None:
            result = replace(result, target=target_ref)
        elif result.target.id == target_ref.id and result.target.requested != target_ref.requested:
            result = replace(result, target=replace(result.target, requested=target_ref.requested))
    if json_mode:
        return RuntimeOutput(result.exit_code, render_json(result), "")
    stdout, stderr = render_text(result)
    return RuntimeOutput(result.exit_code, stdout, stderr)
