from __future__ import annotations

from ..application.contracts import (
    ActiveClearResult,
    ActiveSetResult,
    ActiveViewResult,
    CreateDiscussionDocResult,
    CreateNodeResult,
    DepsCheckResult,
    ImportNodeResult,
    SyncCommandResult,
    ValidationResult,
)
from .contracts import CliText


def render_validate_text(result: ValidationResult) -> CliText:
    if result.report.errors:
        return CliText(
            stdout_lines=[],
            stderr_lines=[result.report.errors[0]],
            warnings=result.report.warnings,
        )
    return CliText(
        stdout_lines=[f"spec-dock: ok (validate) nodes={result.checked_node_count}"],
        stderr_lines=[],
        warnings=result.report.warnings,
    )


def _rel_path_for_output(path_text: str) -> str:
    parts = path_text.replace("\\", "/").split("/")
    if "spec-dock" in parts:
        index = parts.index("spec-dock")
        return "/".join(parts[index:])
    return path_text


def render_new_node_text(result: CreateNodeResult) -> CliText:
    node = result.node
    rel = _rel_path_for_output(node.path.as_posix())
    gh = f" github=#{node.github_issue_number}" if node.github_issue_number is not None else ""

    if node.kind == "initiative":
        line = f"spec-dock: ok (new initiative) id={node.id} path={rel}{gh}"
    elif node.kind == "epic":
        line = (
            "spec-dock: ok (new epic) "
            f"id={node.id} initiative={node.initiative_id} path={rel}{gh}"
        )
    else:
        line = (
            "spec-dock: ok (new issue) "
            f"id={node.id} epic={node.epic_id} initiative={node.initiative_id} path={rel}{gh}"
        )
    return CliText(stdout_lines=[line], stderr_lines=[], warnings=list(result.warnings))


def render_new_doc_text(result: CreateDiscussionDocResult) -> CliText:
    rel = _rel_path_for_output(result.path.as_posix())
    line = (
        "spec-dock: ok (new doc) "
        f"type={result.doc_type} id={result.doc_id} scope={result.scope_node_id} path={rel}"
    )
    return CliText(stdout_lines=[line], stderr_lines=[], warnings=list(result.warnings))


def render_import_text(result: ImportNodeResult) -> CliText:
    node = result.node
    rel = _rel_path_for_output(node.path.as_posix())
    issue_number = int(result.imported_issue.issue_number)

    if node.kind == "initiative":
        line = f"spec-dock: ok (import initiative) id={node.id} path={rel} github=#{issue_number}"
    elif node.kind == "epic":
        line = (
            "spec-dock: ok (import epic) "
            f"id={node.id} initiative={node.initiative_id} path={rel} github=#{issue_number}"
        )
    else:
        line = (
            "spec-dock: ok (import issue) "
            f"id={node.id} epic={node.epic_id} initiative={node.initiative_id} path={rel} github=#{issue_number}"
        )

    warnings = list(result.warnings)
    for warning in result.post_import_sync.state.warnings:
        if warning not in warnings:
            warnings.append(warning)
    if result.post_import_sync.artifact_failure is not None:
        warnings.append("import_post_sync_failed")
    return CliText(stdout_lines=[line], stderr_lines=[], warnings=warnings)


def render_deps_check_text(result: DepsCheckResult) -> CliText:
    target_id = result.inspection.target_id.value
    blockers = list(result.inspection.evaluation.blockers)
    if result.inspection.evaluation.ready:
        return CliText(
            stdout_lines=[f"spec-dock: ok (deps check) target={target_id} ready=true blockers=0"],
            stderr_lines=[],
            warnings=list(result.warnings),
        )
    return CliText(
        stdout_lines=[],
        stderr_lines=[
            f"spec-dock: blocked (deps check) target={target_id} ready=false blockers={len(blockers)}",
            *[f"- {blocker}" for blocker in blockers],
        ],
        warnings=list(result.warnings),
    )


def render_active_show_text(result: ActiveViewResult) -> CliText:
    def _format_entry(entry_id: str | None, entry_path: str | None) -> str:
        if entry_id and entry_path:
            return f"{entry_id} ({entry_path})"
        if entry_id:
            return entry_id
        return "(none)"

    all_none = (
        result.initiative.id is None
        and result.epic.id is None
        and result.issue.id is None
    )
    if all_none:
        stdout_lines = ["spec-dock: active: (not set)"]
    else:
        stdout_lines = [
            f"initiative: {_format_entry(result.initiative.id, result.initiative.path)}",
            f"epic: {_format_entry(result.epic.id, result.epic.path)}",
            f"issue: {_format_entry(result.issue.id, result.issue.path)}",
        ]

    return CliText(stdout_lines=stdout_lines, stderr_lines=[], warnings=list(result.warnings))


def render_active_set_text(result: ActiveSetResult, *, target_display: str) -> CliText:
    ini = result.selection.initiative_id or "(none)"
    epic = result.selection.epic_id or "(none)"
    issue = result.selection.issue_id or "(none)"
    stdout_lines = [
        f"spec-dock: ok (active set) target={target_display} initiative={ini} epic={epic} issue={issue}",
    ]
    if result.branch is not None:
        stdout_lines.append(f"spec-dock: ok (active checkout) branch={result.branch.desired}")
    return CliText(stdout_lines=stdout_lines, stderr_lines=[], warnings=list(result.warnings))


def render_active_clear_text(result: ActiveClearResult) -> CliText:
    del result
    return CliText(stdout_lines=["spec-dock: ok (active clear)"], stderr_lines=[], warnings=[])


def render_sync_text(result: SyncCommandResult) -> CliText:
    if result.artifact_failure is not None:
        stderr_lines = [
            (
                "spec-dock: failed (sync) "
                f"status={result.artifact_failure.status} "
                f"reason={result.artifact_failure.reason}"
            )
        ]
        if result.artifact_failure.status == "failed_partial_or_stale":
            stderr_lines.append("spec-dock: sync: artifacts may be stale or partially written")
        return CliText(
            stdout_lines=[],
            stderr_lines=stderr_lines,
            warnings=list(result.state.warnings),
        )

    line = (
        "spec-dock: ok (sync) "
        f"wrote={result.write_result.index_all_path},"
        f"{result.write_result.tree_all_path},"
        f"{result.write_result.index_todo_path},"
        f"{result.write_result.tree_todo_path},"
        f"{result.write_result.tree_all_puml_path},"
        f"{result.write_result.tree_todo_puml_path},"
        f"{result.write_result.deps_issues_json_path},"
        f"{result.write_result.deps_issues_puml_path},"
        f"{result.write_result.dashboard_md_path}"
        if result.write_result is not None
        else "spec-dock: ok (sync)"
    )
    stderr_lines: list[str] = []
    if result.state.deps_preflight_error:
        stderr_lines.append(result.state.deps_preflight_error)
    if result.active_update is not None:
        if result.active_update.applied:
            stderr_lines.append(f"spec-dock: sync: active updated ({result.active_update.reason or 'updated'})")
        else:
            stderr_lines.append(f"spec-dock: sync: active unchanged ({result.active_update.reason or 'unchanged'})")
    return CliText(stdout_lines=[line], stderr_lines=stderr_lines, warnings=list(result.state.warnings))
