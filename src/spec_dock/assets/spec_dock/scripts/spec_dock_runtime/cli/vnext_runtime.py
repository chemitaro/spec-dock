"""Typed vNext CLI execution from one resolved Git worktree and engine."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import TYPE_CHECKING

from spec_dock_runtime.cli.options import parse_vnext_output
from spec_dock_runtime.commands.active_vnext import run_active_change, run_active_show
from spec_dock_runtime.commands.artifact_vnext import run_artifact_query
from spec_dock_runtime.commands.branch_vnext import run_branch_command
from spec_dock_runtime.commands.dependency_vnext import run_dependency_change, run_dependency_query
from spec_dock_runtime.commands.scope_create_vnext import run_scope_create
from spec_dock_runtime.commands.scope_delete_vnext import run_scope_delete
from spec_dock_runtime.commands.scope_lifecycle_vnext import run_scope_lifecycle
from spec_dock_runtime.commands.scope_query_vnext import run_scope_edit, run_scope_query
from spec_dock_runtime.commands.work_vnext import WorkContext, run_work_finish, run_work_start
from spec_dock_runtime.commands.workspace_diagnostics_vnext import run_workspace_diagnostics
from spec_dock_runtime.commands.worktree_vnext import run_worktree_query
from spec_dock_runtime.infra.control_store import load_control
from spec_dock_runtime.infra.git_cli import git_common_directory
from spec_dock_runtime.infra.github_lifecycle import GithubIssueGateway, RemoteIssueError
from spec_dock_runtime.presentation.envelope import Diagnostic, Effect, OperationResult, render_json, render_text
from spec_dock_runtime.presentation.errors import CliMessageData

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass(frozen=True)
class RuntimeOutput:
    exit_code: int
    stdout: str
    stderr: str


def _repository_root(candidate: Path) -> Path:
    try:
        result = subprocess.run(
            ["git", "-C", str(candidate), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
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
    if control is None or control.engine_digest != engine_digest:
        raise ValueError("external engine does not match repository control")
    matches = [entry for entry in control.worktrees if entry.active and Path(entry.root).resolve(strict=True) == root]
    if len(matches) != 1:
        raise ValueError("current worktree is not uniquely registered")
    return WorkContext(root, common, matches[0].id, engine_digest, control.epoch)


def _failure(command: str, code: str, message: str, exit_code: int, *, json_mode: bool) -> RuntimeOutput:
    result = OperationResult(
        command=command,
        status="partial" if exit_code == 6 else "failed",
        data=CliMessageData(None),
        exit_code=exit_code,
        effects=(Effect("operation", "unknown", None),) if exit_code == 6 else (),
        error=Diagnostic(code, message, {}),
    )
    if json_mode:
        return RuntimeOutput(exit_code, render_json(result), "")
    stdout, stderr = render_text(result)
    return RuntimeOutput(exit_code, stdout, stderr)


def run_vnext(
    argv: Sequence[str],
    *,
    invocation_cwd: Path,
    engine_digest: str,
    engine_version: str,
) -> RuntimeOutput:
    """Parse once, bind to a registered worktree, then dispatch supported leaves."""
    parsed = parse_vnext_output(argv, engine_version=engine_version, engine_digest=engine_digest)
    if parsed.namespace is None:
        assert parsed.exit_code is not None
        return RuntimeOutput(parsed.exit_code, parsed.stdout, parsed.stderr)
    ns = parsed.namespace
    json_mode = bool(ns.json)
    try:
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
            "worktree list",
            "worktree show",
            "workspace validate",
            "workspace doctor",
        }:
            raise ValueError("vNext command execution is not yet connected")
        context = _context(ns, invocation_cwd=invocation_cwd, engine_digest=engine_digest)
        if ns.command_path in {"scope list", "scope show"}:
            result = run_scope_query(ns, context)
        elif ns.command_path in {"scope create initiative", "scope create epic", "scope create issue"}:
            result = run_scope_create(ns, context, gateway=GithubIssueGateway(timeout=ns.timeout))
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
        elif ns.command_path in {"worktree list", "worktree show"}:
            result = run_worktree_query(ns, context)
        elif ns.command_path in {"workspace validate", "workspace doctor"}:
            result = run_workspace_diagnostics(ns, context)
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
    except RemoteIssueError as error:
        return _failure(ns.command_path, error.code, str(error), error.exit_code, json_mode=json_mode)
    except LookupError as error:
        return _failure(ns.command_path, "SCOPE_NOT_FOUND", str(error), 4, json_mode=json_mode)
    except ValueError as error:
        return _failure(ns.command_path, "PRECONDITION_FAILED", str(error), 3, json_mode=json_mode)
    except RuntimeError:
        return _failure(
            ns.command_path,
            "EFFECT_STATE_UNKNOWN",
            "operation stopped; inspect the recorded effects before recovery",
            6,
            json_mode=json_mode,
        )
    except OSError:
        return _failure(ns.command_path, "LOCAL_IO_FAILED", "local I/O operation failed", 5, json_mode=json_mode)
    if json_mode:
        return RuntimeOutput(result.exit_code, render_json(result), "")
    stdout, stderr = render_text(result)
    return RuntimeOutput(result.exit_code, stdout, stderr)
