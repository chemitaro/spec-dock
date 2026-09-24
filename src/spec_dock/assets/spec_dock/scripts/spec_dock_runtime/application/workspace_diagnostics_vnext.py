"""Read-only validation and operational diagnostics for the v3 workspace."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
import subprocess
from typing import TYPE_CHECKING, Literal

from spec_dock_runtime.application.artifact_query import list_artifacts
from spec_dock_runtime.application.contracts import GitHubCapabilityDiagnostic, GitHubCapabilityProbeRequest
from spec_dock_runtime.application.dependency_vnext import validate_scope_dependency_snapshot
from spec_dock_runtime.application.scope_query import ScopeView, load_scope_views
from spec_dock_runtime.infra.active_store import load_selection_v3
from spec_dock_runtime.infra.control_store import WORKSPACE_SCHEMA, WRITER_PROTOCOL, load_control
from spec_dock_runtime.infra.generation_store import load_generation
from spec_dock_runtime.infra.github_capability_cli import GitHubCapabilityCliGateway
from spec_dock_runtime.infra.json_store import read_guarded_json
from spec_dock_runtime.infra.operation_journal import JournalStore
from spec_dock_runtime.infra.registry_store import RegistryStore

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class WorkspaceFinding:
    code: str
    severity: Literal["error", "warning"]
    message: str


@dataclass(frozen=True)
class WorkspaceDiagnostics:
    node_count: int
    findings: tuple[WorkspaceFinding, ...]
    github: tuple[GitHubCapabilityDiagnostic, ...] = ()

    @property
    def valid(self) -> bool:
        return not any(item.severity == "error" for item in self.findings) and not any(
            item.severity == "blocking" for item in self.github
        )

    @property
    def exit_code(self) -> int:
        return 0 if self.valid else 7


def _finding(code: str, severity: Literal["error", "warning"], message: str) -> WorkspaceFinding:
    return WorkspaceFinding(code, severity, message)


def _load_workspace_schema(specdock_dir: Path, findings: list[WorkspaceFinding]) -> None:
    try:
        loaded = read_guarded_json(specdock_dir / "workspace.json")
    except (OSError, ValueError, RuntimeError):
        findings.append(_finding("workspace_schema_unreadable", "error", "workspace schema cannot be read safely"))
        return
    if loaded is None:
        findings.append(_finding("workspace_schema_missing", "error", "workspace schema is missing"))
        return
    payload = loaded[0]
    if (
        not isinstance(payload, dict)
        or payload.get("schema_version") != WORKSPACE_SCHEMA
        or payload.get("writer_protocol") != WRITER_PROTOCOL
    ):
        findings.append(_finding("workspace_schema_mismatch", "error", "workspace schema or protocol differs"))


def _inspect_views(specdock_dir: Path, findings: list[WorkspaceFinding]) -> tuple[ScopeView, ...]:
    try:
        views = load_scope_views(specdock_dir)
    except (OSError, ValueError, RuntimeError):
        findings.append(_finding("scope_unreadable", "error", "Scope metadata cannot be read safely"))
        return ()
    by_id = {item.id: item for item in views}
    if len(by_id) != len(views):
        findings.append(_finding("scope_duplicate_id", "error", "Scope IDs are duplicated"))
    for item in views:
        parent_kind = {"initiative": None, "epic": "initiative", "issue": "epic"}[item.kind]
        parent = by_id.get(item.parent_id or "")
        if (parent_kind is None and item.parent_id is not None) or (
            parent_kind is not None and (parent is None or parent.kind != parent_kind)
        ):
            findings.append(_finding("scope_parent_invalid", "error", f"Scope parent is invalid: {item.id}"))
        if item.status.source == "unknown":
            findings.append(_finding("status_unknown", "warning", f"Scope status is not observed: {item.id}"))
    return views


def _inspect_dependencies_and_artifacts(
    repo_root: Path, views: tuple[ScopeView, ...], findings: list[WorkspaceFinding]
) -> None:
    if not any(item.code == "scope_parent_invalid" for item in findings):
        try:
            validate_scope_dependency_snapshot(views)
        except (OSError, ValueError, RuntimeError):
            findings.append(_finding("dependency_invalid", "error", "Scope dependency graph is invalid"))
    for scope in ("@root", *(item.id for item in views)):
        try:
            list_artifacts(repo_root=repo_root, scope=scope)
        except (OSError, ValueError, RuntimeError):
            findings.append(_finding("artifact_invalid", "error", f"Artifact catalog is invalid: {scope}"))


def _inspect_selection_and_generation(
    specdock_dir: Path, *, worktree_id: str, views: tuple[ScopeView, ...], findings: list[WorkspaceFinding]
) -> None:
    selection = None
    try:
        selection, _identity = load_selection_v3(specdock_dir, worktree_id=worktree_id)
    except (OSError, ValueError, RuntimeError):
        findings.append(_finding("active_invalid", "error", "active selection is invalid"))
    if selection is not None:
        by_id = {item.id: item for item in views}
        for role, scope_id in (
            ("initiative", selection.initiative_id),
            ("epic", selection.epic_id),
            ("issue", selection.issue_id),
        ):
            if scope_id is not None and (scope_id not in by_id or by_id[scope_id].kind != role):
                findings.append(_finding("active_target_missing", "error", "active Scope is absent or has wrong kind"))
                break
    try:
        generation = load_generation(specdock_dir)
    except (OSError, ValueError, RuntimeError):
        findings.append(_finding("generation_invalid", "error", "published generation is unreadable or changed"))
        return
    if generation is None:
        findings.append(_finding("generation_missing", "warning", "derived generation has not been published"))
        return
    if not generation.valid:
        findings.append(_finding("generation_invalid_snapshot", "error", "published generation records invalid input"))
    if selection is not None and generation.selection_revision != selection.revision:
        findings.append(_finding("projection_stale", "warning", "derived generation precedes active selection"))
    for source_name, projection_name in (("index.json", "index-all.json"), ("tree.json", "tree-all.json")):
        try:
            expected = json.loads(generation.files[source_name])
            observed = read_guarded_json(specdock_dir / ".agent" / projection_name)
        except (KeyError, OSError, ValueError, RuntimeError):
            observed = None
        if observed is None or observed[0] != expected:
            findings.append(_finding("projection_stale", "warning", "fixed-name derived projection differs"))
            break


def _inspect_control(
    common_dir: Path, *, worktree_id: str, engine_digest: str | None, findings: list[WorkspaceFinding]
) -> None:
    try:
        control = load_control(common_dir)
    except (OSError, ValueError, RuntimeError):
        findings.append(_finding("control_invalid", "error", "repository control is unreadable"))
        return
    if control is None:
        findings.append(_finding("control_missing", "error", "repository control is missing"))
        return
    if control.schema_version != WORKSPACE_SCHEMA or control.writer_protocol != WRITER_PROTOCOL:
        findings.append(_finding("writer_mismatch", "error", "repository writer protocol differs"))
    if engine_digest is not None and control.engine_digest != engine_digest:
        findings.append(_finding("engine_mismatch", "error", "installed engine differs from repository control"))
    registered = {item.id: item for item in control.worktrees}
    if worktree_id not in registered or not registered[worktree_id].active:
        findings.append(_finding("worktree_unregistered", "error", "current worktree is not active in control"))
    if any(
        item.active
        and (
            item.schema_version != WORKSPACE_SCHEMA
            or item.writer_protocol != WRITER_PROTOCOL
            or item.engine_digest != control.engine_digest
        )
        for item in control.worktrees
    ):
        findings.append(_finding("worktree_protocol_mismatch", "error", "a registered worktree uses another protocol"))
    if control.mode != "ready":
        findings.append(_finding("control_not_ready", "error", "repository control is not ready"))
    try:
        pending = JournalStore(common_dir).pending()
    except (OSError, ValueError, RuntimeError):
        findings.append(_finding("journal_invalid", "error", "operation journal is unreadable"))
    else:
        for operation in pending:
            findings.append(
                _finding("operation_pending", "error", f"operation requires diagnosis: {operation.operation_id}")
            )


def _inspect_branch(repo_root: Path, common_dir: Path, findings: list[WorkspaceFinding]) -> None:
    try:
        completed = subprocess.run(
            ["git", "symbolic-ref", "--quiet", "--short", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        findings.append(_finding("git_branch_unavailable", "warning", "current Git branch could not be observed"))
        return
    if completed.returncode != 0:
        return
    branch = completed.stdout.strip()
    if re.fullmatch(r"(?:init|epic|iss)-[0-9]+-.+", branch) is None:
        return
    try:
        registry, _identity = RegistryStore(common_dir).load()
    except (OSError, ValueError, RuntimeError):
        findings.append(_finding("registry_invalid", "error", "canonical branch registry is unreadable"))
        return
    if not any(binding.name == branch for binding in registry.branches):
        findings.append(_finding("legacy_branch_unbound", "warning", "current Scope branch has no canonical binding"))


def validate_workspace(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str | None = None,
    require_nodes: bool = False,
) -> WorkspaceDiagnostics:
    """Inspect the workspace without repairing, syncing, or probing GitHub."""
    findings: list[WorkspaceFinding] = []
    specdock_dir = repo_root / "spec-dock"
    _load_workspace_schema(specdock_dir, findings)
    views = _inspect_views(specdock_dir, findings)
    _inspect_dependencies_and_artifacts(repo_root, views, findings)
    if require_nodes and not views:
        findings.append(_finding("nodes_required", "error", "at least one Scope is required"))
    _inspect_selection_and_generation(specdock_dir, worktree_id=worktree_id, views=views, findings=findings)
    _inspect_control(common_dir, worktree_id=worktree_id, engine_digest=engine_digest, findings=findings)
    _inspect_branch(repo_root, common_dir, findings)
    return WorkspaceDiagnostics(len(views), tuple(findings))


def doctor_workspace(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str | None = None,
    github_repo: str | None = None,
    github_pr: int | None = None,
    github_head_sha: str | None = None,
    github_extended: bool = False,
    capability_gateway: GitHubCapabilityCliGateway | None = None,
) -> WorkspaceDiagnostics:
    """Add an explicitly requested all-or-none GitHub capability probe."""
    supplied = (github_repo is not None, github_pr is not None, github_head_sha is not None)
    if any(supplied) and not all(supplied):
        raise ValueError("GitHub capability probe requires repository, PR, and head SHA")
    if github_extended and not all(supplied):
        raise ValueError("extended GitHub probe requires repository, PR, and head SHA")
    report = validate_workspace(
        repo_root=repo_root, common_dir=common_dir, worktree_id=worktree_id, engine_digest=engine_digest
    )
    if not all(supplied):
        return report
    assert github_repo is not None and github_pr is not None and github_head_sha is not None
    if (
        re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", github_repo) is None
        or github_pr <= 0
        or re.fullmatch(r"[0-9a-fA-F]{40}", github_head_sha) is None
    ):
        raise ValueError("GitHub capability probe arguments are invalid")
    gateway = capability_gateway if capability_gateway is not None else GitHubCapabilityCliGateway()
    diagnostics = gateway.probe(GitHubCapabilityProbeRequest(github_repo, github_pr, github_head_sha, github_extended))
    return WorkspaceDiagnostics(report.node_count, report.findings, tuple(diagnostics))
