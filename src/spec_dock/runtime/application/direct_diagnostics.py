"""Read workspace evidence without control, generation caches or repair operations."""

from __future__ import annotations

from dataclasses import asdict
import re
from typing import TYPE_CHECKING

from spec_dock.runtime.application.contracts import GitHubCapabilityProbeRequest
from spec_dock.runtime.application.project_context import NEW_WRITER_PROTOCOL, OLD_WRITER_PROTOCOL, ProjectContext
from spec_dock.runtime.application.scope_expectations import check_scope_expectations
from spec_dock.runtime.application.scope_query import load_scope_views
from spec_dock.runtime.application.workspace_structure import inspect_structure
from spec_dock.runtime.application.worktree_observation import read_selection
from spec_dock.runtime.infra.github_capability_cli import GitHubCapabilityCliGateway
from spec_dock.runtime.infra.legacy_reader import inspect_json_file, inspect_legacy_files
from spec_dock.runtime.presentation.command_data import DiagnosticData
from spec_dock.runtime.presentation.envelope import Diagnostic, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.project_context import GitContext


def diagnose_workspace(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    request = _github_request(namespace)
    views, findings = inspect_structure(context.root)
    if findings and namespace.expect_current:
        raise ValueError("--expect-current cannot be verified from invalid workspace structure")
    selection = read_selection(context, views)
    check_scope_expectations(
        context,
        views,
        selection,
        target=None,
        expected_current=namespace.expect_current,
        expected_backend=namespace.expect_backend,
    )
    if selection.status not in ("empty", "selected"):
        findings += (
            Diagnostic(
                "DIRECT_SELECTION_UNVERIFIED",
                selection.reason or "direct selection cannot be verified",
                {"status": selection.status},
            ),
        )
    incomplete = bool(findings)
    if namespace.legacy:
        legacy_findings, legacy_incomplete = _legacy_diagnostics(context)
        findings += legacy_findings
        incomplete |= legacy_incomplete
    github_findings, unverified, github_incomplete = _probe_github(request, timeout=namespace.timeout)
    findings += github_findings
    incomplete |= github_incomplete
    if namespace.legacy:
        unverified += (
            "Legacy record headers are historical observations; remote effects and active ownership were not reconciled.",
        )
    if any(view.backend.kind == "github" for view in views):
        unverified += ("GitHub Scope lifecycle was not observed by this diagnosis.",)
    return OperationResult(
        namespace.command_path,
        "failed" if incomplete else "succeeded",
        DiagnosticData(findings, unverified),
        7 if incomplete else 0,
        error=Diagnostic("WORKSPACE_DIAGNOSIS_INCOMPLETE", "workspace evidence is incomplete", {})
        if incomplete
        else None,
    )


def diagnose_raw_workspace(namespace: argparse.Namespace, context: GitContext) -> OperationResult[object]:
    request = _github_request(namespace)
    observation = inspect_json_file(context.root / "spec-dock/workspace.json")
    payload = observation.payload
    known = (
        payload is not None
        and type(payload.get("schema_version")) is int
        and payload.get("schema_version") == 3
        and payload.get("writer_protocol") in (NEW_WRITER_PROTOCOL, OLD_WRITER_PROTOCOL)
    )
    if namespace.expect_backend:
        raise ValueError("--expect-backend requires a resolved target Scope")
    if namespace.expect_current:
        if not known:
            raise ValueError("--expect-current cannot be verified from an unknown workspace declaration")
        assert payload is not None
        project = ProjectContext(
            context.root,
            context.common_dir,
            context.clone_identity,
            context.worktree_identity,
            context.head,
            context.branch,
            payload,
        )
        views = load_scope_views(context.root / "spec-dock")
        check_scope_expectations(
            project,
            views,
            read_selection(project, views),
            target=None,
            expected_current=namespace.expect_current,
            expected_backend=None,
        )
    findings = [Diagnostic("WORKSPACE_FILE_OBSERVED", "workspace declaration file information", observation.details())]
    if not known:
        findings.append(
            Diagnostic("WORKSPACE_DECLARATION_UNVERIFIED", "workspace schema or protocol cannot be verified", {})
        )
    incomplete = not known
    if namespace.legacy:
        legacy_findings, legacy_incomplete = _legacy_diagnostics(context)
        findings.extend(legacy_findings)
        incomplete |= legacy_incomplete
    github_findings, unverified, github_incomplete = _probe_github(request, timeout=namespace.timeout)
    findings.extend(github_findings)
    incomplete |= github_incomplete
    if namespace.legacy:
        unverified += (
            "Legacy record headers are historical observations; remote effects and active ownership were not reconciled.",
        )
    return OperationResult(
        namespace.command_path,
        "failed" if incomplete else "succeeded",
        DiagnosticData(tuple(findings), ("Scope and selection bodies were not interpreted in raw mode.", *unverified)),
        7 if incomplete else 0,
        error=Diagnostic("WORKSPACE_DIAGNOSIS_INCOMPLETE", "workspace evidence is incomplete", {})
        if incomplete
        else None,
    )


def _legacy_diagnostics(context: GitContext) -> tuple[tuple[Diagnostic, ...], bool]:
    observations = inspect_legacy_files(context.root, context.common_dir)
    return (
        tuple(
            Diagnostic(
                "LEGACY_FILE_OBSERVED", "retired record file information; no execution or repair", item.details()
            )
            for item in observations
        ),
        any(item.classification not in ("absent", "legacy_header_observed") for item in observations),
    )


def _github_request(namespace: argparse.Namespace) -> GitHubCapabilityProbeRequest | None:
    repo, number, head = namespace.github_repo, namespace.github_pr, namespace.github_head_sha
    supplied = (repo is not None, number is not None, head is not None)
    if not any(supplied) and not namespace.github_extended:
        return None
    if not all(supplied):
        raise ValueError("GitHub capability probe requires repository, PR, and head SHA")
    if (
        re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]*/[A-Za-z0-9_][A-Za-z0-9_.-]*", repo) is None
        or re.fullmatch(r"[1-9][0-9]*", number) is None
        or len(number) > 18
        or re.fullmatch(r"[0-9a-fA-F]{40}", head) is None
    ):
        raise ValueError("GitHub capability probe arguments are invalid")
    if namespace.offline:
        raise ValueError("offline mode cannot execute a GitHub capability probe")
    return GitHubCapabilityProbeRequest(repo, int(number), head, namespace.github_extended)


def _probe_github(
    request: GitHubCapabilityProbeRequest | None, *, timeout: float
) -> tuple[tuple[Diagnostic, ...], tuple[str, ...], bool]:
    if request is None:
        return (), ("GitHub capabilities were not requested.",), False
    observations = GitHubCapabilityCliGateway(timeout=timeout).probe(request)
    findings = tuple(
        Diagnostic(item.code, item.message, {**asdict(item), "requested_target": asdict(request)})
        for item in observations
    )
    incomplete = not observations or any(item.status != "ok" for item in observations)
    return findings, ("Requested GitHub capabilities could not all be observed.",) if incomplete else (), incomplete
