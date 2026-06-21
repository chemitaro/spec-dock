#!/usr/bin/env python3
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

PR_METADATA_FIELDS = "headRefOid,baseRefName,headRefName,headRepositoryOwner,url,state,isDraft,number,mergeable"
GITHUB_ACTIONS_APP_ID = 15368
ANY_SOURCE_REQUIRED_CHECK_APP_ID = -1
ACTIONS_SATISFIABLE_REQUIRED_CHECK_APP_IDS = {
    GITHUB_ACTIONS_APP_ID,
    ANY_SOURCE_REQUIRED_CHECK_APP_ID,
    None,
}


@dataclass(frozen=True)
class Args:
    repo: str
    pr: int
    head_sha: str | None
    trigger_comment_id: str | None
    trigger_created_at: str | None
    body_mode: str
    out_dir: str | None


def parse_args(argv: list[str]) -> Args:
    values = {
        "repo": None,
        "pr": None,
        "head_sha": None,
        "trigger_comment_id": None,
        "trigger_created_at": None,
        "body_mode": "trigger-window-truncated",
        "out_dir": None,
    }
    idx = 0
    while idx < len(argv):
        flag = argv[idx]
        if flag not in {
            "--repo",
            "--pr",
            "--head-sha",
            "--trigger-comment-id",
            "--trigger-created-at",
            "--body-mode",
            "--out",
        }:
            raise SystemExit(64)
        if idx + 1 >= len(argv):
            raise SystemExit(64)
        value = argv[idx + 1]
        if flag == "--repo":
            values["repo"] = value
        elif flag == "--pr":
            values["pr"] = value
        elif flag == "--head-sha":
            values["head_sha"] = value or None
        elif flag == "--trigger-comment-id":
            values["trigger_comment_id"] = value or None
        elif flag == "--trigger-created-at":
            values["trigger_created_at"] = value or None
        elif flag == "--body-mode":
            values["body_mode"] = value
        elif flag == "--out":
            values["out_dir"] = value or None
        idx += 2
    if values["repo"] is None or values["pr"] is None:
        raise SystemExit(64)
    return Args(
        repo=str(values["repo"]),
        pr=int(str(values["pr"])),
        head_sha=values["head_sha"],
        trigger_comment_id=values["trigger_comment_id"],
        trigger_created_at=values["trigger_created_at"],
        body_mode=str(values["body_mode"]),
        out_dir=values["out_dir"],
    )


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def load_json_path(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def run_to_files(command: list[str], stdout_path: Path, stderr_path: Path) -> int:
    with stdout_path.open("wb") as stdout_file, stderr_path.open("wb") as stderr_file:
        try:
            result = subprocess.run(command, stdout=stdout_file, stderr=stderr_file, check=False)
        except OSError as exc:
            message = exc.strerror or exc.__class__.__name__
            stderr_file.write(f"{command[0]}: {message}\n".encode("utf-8", errors="replace"))
            if isinstance(exc, FileNotFoundError):
                return 127
            if isinstance(exc, PermissionError):
                return 126
            return 1
    return result.returncode


def sha_matches(left: str | None, right: str | None) -> bool:
    return bool(
        left
        and right
        and (
            left.lower().startswith(right.lower())
            or right.lower().startswith(left.lower())
        )
    )


def token_source() -> str:
    if os.environ.get("GH_TOKEN"):
        return "GH_TOKEN"
    if os.environ.get("GITHUB_TOKEN"):
        return "GITHUB_TOKEN"
    return "gh_saved_auth"


def classify_github_stderr(stderr: str) -> str:
    lowered = (stderr or "").lower()
    if (
        "resource not accessible by personal access token" in lowered
        or "resource not accessible by integration" in lowered
        or "permission denied" in lowered
    ):
        return "permission_denied"
    if (
        "requires authentication" in lowered
        or "authentication required" in lowered
        or "not logged into" in lowered
        or "http 401" in lowered
    ):
        return "auth_missing"
    if "rate limit" in lowered or "http 429" in lowered:
        return "rate_limited"
    if "unknown json field" in lowered:
        return "schema_unavailable"
    if (
        "http 5" in lowered
        or "timeout" in lowered
        or "timed out" in lowered
        or "temporarily unavailable" in lowered
        or "connection reset" in lowered
    ):
        return "transient_unknown"
    return "unknown"


def github_api_failure_limitation(
    *,
    api: str,
    source: str,
    capability: str,
    exit_code: int,
    stderr: str,
    default_code: str,
    default_message: str,
) -> dict[str, object]:
    classification = classify_github_stderr(stderr)
    stderr_sha256 = hashlib.sha256((stderr or "").encode()).hexdigest()
    base = {
        "capability": capability,
        "api": api,
        "source": source,
        "token_source": token_source(),
        "secret_redacted": True,
        "stderr_sha256": stderr_sha256,
        "exit_code": exit_code,
    }
    if classification == "permission_denied":
        return {
            **base,
            "code": "github_token_permission_denied",
            "status": "permission_denied",
            "severity": "blocking",
            "message": "GitHub token lacks permission for fixed PR observation metadata API",
            "recommended_next_action": "fix_github_token_permissions",
        }
    if classification == "auth_missing":
        return {
            **base,
            "code": "github_auth_missing",
            "status": "auth_missing",
            "severity": "blocking",
            "message": "GitHub authentication is unavailable for fixed PR observation metadata API",
            "recommended_next_action": "authenticate_github_cli",
        }
    if classification == "rate_limited":
        return {
            **base,
            "code": "github_rate_limited",
            "status": "rate_limited",
            "severity": "blocking",
            "message": "GitHub rate limit blocked fixed PR observation metadata API",
            "recommended_next_action": "wait_or_retry_later",
        }
    if classification == "schema_unavailable":
        return {
            **base,
            "code": "github_api_schema_unavailable",
            "status": "schema_unavailable",
            "severity": "blocking",
            "message": "fixed read-only PR observation metadata schema is unavailable",
            "recommended_next_action": "inspect_github_api_schema",
        }
    if classification == "transient_unknown":
        return {
            **base,
            "code": "github_transient_unknown",
            "status": "transient_unknown",
            "severity": "blocking",
            "message": "transient GitHub failure blocked fixed PR observation metadata API",
            "recommended_next_action": "retry_observation",
        }
    return {
        **base,
        "code": default_code,
        "status": classification,
        "severity": "blocking",
        "message": default_message,
        "recommended_next_action": "human_gate",
    }


def optional_github_api_failure_limitation(
    *,
    api: str,
    source: str,
    capability: str,
    exit_code: int,
    stderr: str,
    default_code: str,
    default_message: str,
    recommended_next_action: str = "continue_with_available_metadata",
) -> dict[str, object]:
    limitation = github_api_failure_limitation(
        api=api,
        source=source,
        capability=capability,
        exit_code=exit_code,
        stderr=stderr,
        default_code=default_code,
        default_message=default_message,
    )
    limitation["severity"] = "warning"
    limitation["recommended_next_action"] = recommended_next_action
    if limitation.get("code") == "github_token_permission_denied":
        limitation["code"] = default_code
    limitation["message"] = default_message
    return limitation


def is_not_found(stderr: str) -> bool:
    lowered = (stderr or "").lower()
    return "http 404" in lowered or "not found" in lowered


def pr_metadata_failure_limitation(
    *, exit_code: int, stderr: str, default_code: str, default_message: str
) -> dict[str, object]:
    classification = classify_github_stderr(stderr)
    stderr_sha256 = hashlib.sha256((stderr or "").encode()).hexdigest()
    base = {
        "capability": "pull_request_read",
        "api": f"gh pr view --json {PR_METADATA_FIELDS}",
        "source": "gh_pr_view",
        "token_source": token_source(),
        "secret_redacted": True,
        "stderr_sha256": stderr_sha256,
        "exit_code": exit_code,
    }
    if classification == "permission_denied":
        return {
            **base,
            "code": "github_token_permission_denied",
            "status": "permission_denied",
            "severity": "blocking",
            "message": "GitHub token lacks permission for fixed PR metadata API",
            "recommended_next_action": "fix_github_token_permissions",
        }
    if classification == "auth_missing":
        return {
            **base,
            "code": "github_auth_missing",
            "status": "auth_missing",
            "severity": "blocking",
            "message": "GitHub authentication is unavailable for fixed PR metadata API",
            "recommended_next_action": "authenticate_github_cli",
        }
    if classification == "rate_limited":
        return {
            **base,
            "code": "github_rate_limited",
            "status": "rate_limited",
            "severity": "blocking",
            "message": "GitHub rate limit blocked fixed PR metadata API",
            "recommended_next_action": "wait_or_retry_later",
        }
    if classification == "schema_unavailable":
        return {
            **base,
            "code": "github_api_schema_unavailable",
            "status": "schema_unavailable",
            "severity": "blocking",
            "message": "fixed read-only PR metadata schema is unavailable",
            "recommended_next_action": "inspect_github_api_schema",
        }
    if classification == "transient_unknown":
        return {
            **base,
            "code": "github_transient_unknown",
            "status": "transient_unknown",
            "severity": "blocking",
            "message": "transient GitHub failure blocked fixed PR metadata API",
            "recommended_next_action": "retry_observation",
        }
    return {
        "code": default_code,
        "source": "gh_pr_view",
        "severity": "blocking",
        "message": default_message,
        "exit_code": exit_code,
        "stderr_sha256": stderr_sha256,
    }


def collector_decision_payload(review_wrapper_payload: dict[str, object], review_payload: dict[str, object]) -> dict[str, object]:
    wrapper_decision = review_wrapper_payload.get("decision")
    if isinstance(wrapper_decision, dict):
        return wrapper_decision
    review_decision = review_payload.get("decision")
    if isinstance(review_decision, dict):
        return review_decision
    return {}


def decision_int(decision: dict[str, object], key: str, default: int = 0) -> int:
    value = decision.get(key)
    return value if isinstance(value, int) else default


def decision_list(decision: dict[str, object], key: str) -> list[object]:
    value = decision.get(key)
    return value if isinstance(value, list) else []


def current_selected_actionable_reason(decision: dict[str, object]) -> str | None:
    selected_unresolved_thread_ids = decision_list(decision, "selected_unresolved_thread_ids")
    selected_unresolved_count = decision_int(
        decision,
        "selected_unresolved_count",
        len(selected_unresolved_thread_ids),
    )
    current_selected_unresolved_count = decision_int(
        decision,
        "current_selected_unresolved_count",
        selected_unresolved_count,
    )
    selected_changes_requested_evidence = decision_list(decision, "selected_changes_requested_evidence")
    decision_status_reason = (
        decision.get("status_reason") if isinstance(decision.get("status_reason"), str) else None
    )
    if (
        decision_status_reason == "current_selected_unresolved_thread"
        or selected_unresolved_count > 0
        or current_selected_unresolved_count > 0
    ):
        return "current_selected_unresolved_thread"
    if decision_status_reason == "current_selected_changes_requested" or selected_changes_requested_evidence:
        return "current_selected_changes_requested"
    return None


def carryover_inventory_reason(decision: dict[str, object]) -> str | None:
    carryover_unresolved_count = decision_int(decision, "carryover_unresolved_count")
    carryover_unresolved_thread_ids = decision_list(decision, "carryover_unresolved_thread_ids")
    decision_status_reason = (
        decision.get("status_reason") if isinstance(decision.get("status_reason"), str) else None
    )
    if (
        decision_status_reason == "carryover_non_outdated_unresolved_thread"
        or carryover_unresolved_count > 0
        or bool(carryover_unresolved_thread_ids)
    ):
        return "carryover_non_outdated_unresolved_thread"
    return None


def explicit_actionable_unresolved_reason(decision: dict[str, object]) -> str | None:
    actionable_unresolved_count = decision_int(decision, "actionable_unresolved_count")
    actionable_unresolved_thread_ids = decision_list(decision, "actionable_unresolved_thread_ids")
    if actionable_unresolved_count > 0 or actionable_unresolved_thread_ids:
        return "actionable_unresolved_thread"
    return None


def trusted_completion_actionable_reason(
    decision: dict[str, object], completion_signal: object
) -> str | None:
    current_reason = current_selected_actionable_reason(decision)
    if current_reason:
        return current_reason
    fallback_pass_candidate = decision.get("fallback_pass_candidate")
    if (
        completion_signal == "fallback_issue_comment"
        and isinstance(fallback_pass_candidate, dict)
        and fallback_pass_candidate.get("promotes_top_level_status") is True
    ):
        return explicit_actionable_unresolved_reason(decision)
    if completion_signal == "submitted_pull_request_review":
        return carryover_inventory_reason(decision)
    return None


def has_blocking_limitation(limitations: list[object], ignored_codes: set[str] | None = None) -> bool:
    ignored_codes = ignored_codes or set()
    return any(
        isinstance(item, dict)
        and item.get("severity") == "blocking"
        and item.get("code") not in ignored_codes
        for item in limitations
    )


def has_permission_limitation(limitations: list[object]) -> bool:
    return any(
        isinstance(item, dict)
        and item.get("code") == "github_token_permission_denied"
        and item.get("severity") == "blocking"
        for item in limitations
    )


def has_waitable_required_actions_context_limitation(limitations: list[object]) -> bool:
    return any(
        isinstance(item, dict)
        and item.get("code") == "required_actions_context_pending"
        and item.get("recommended_next_action") == "wait"
        for item in limitations
    )


def mergeability_status(metadata: dict[str, object]) -> str | None:
    value = metadata.get("mergeable")
    if not isinstance(value, str) or not value:
        return None
    return value.upper()


def classify_snapshot(
    *,
    summary: dict[str, object],
    ci_payload: dict[str, object],
    review_payload: dict[str, object],
    review_wrapper_payload: dict[str, object],
    metadata: dict[str, object],
    limitations: list[object],
    head_matches_expected: bool | None,
    normalized_status: str,
    trigger_comment_id: str | None,
    trigger_created_at: str | None,
) -> tuple[str, str, bool, str | None]:
    ci_status = ci_payload.get("status") or summary.get("ci") or "unknown"
    review_status = review_payload.get("status") or summary.get("review") or "unknown"
    decision = collector_decision_payload(review_wrapper_payload, review_payload)
    decision_status = decision.get("status") if isinstance(decision.get("status"), str) else None
    decision_status_reason = (
        decision.get("status_reason") if isinstance(decision.get("status_reason"), str) else None
    )
    decision_action = (
        decision.get("recommended_next_action")
        if isinstance(decision.get("recommended_next_action"), str)
        else None
    )
    decision_observation_complete = decision.get("observation_complete")
    selected_changes_requested_evidence = decision_list(decision, "selected_changes_requested_evidence")
    codex_review = (
        review_wrapper_payload.get("codex_review")
        if isinstance(review_wrapper_payload.get("codex_review"), dict)
        else (
            review_payload.get("codex_review")
            if isinstance(review_payload.get("codex_review"), dict)
            else {}
        )
    )
    codex_lifecycle = codex_review.get("lifecycle") if isinstance(codex_review.get("lifecycle"), dict) else {}
    completion_signal = decision.get("completion_signal") or codex_lifecycle.get("completion_signal")
    actionable_reason = trusted_completion_actionable_reason(decision, completion_signal)
    if head_matches_expected is False or normalized_status == "stale_head":
        return "stale_head", "rerun_for_current_head", False, "stale_head"
    if metadata.get("isDraft") is True:
        return "human_gate", "mark_pr_ready_for_review", False, "draft_pr"
    if metadata.get("state") and str(metadata.get("state") or "").upper() != "OPEN":
        return "human_gate", "reopen_or_use_open_pr", False, "non_open_pr"
    if ci_status == "failed":
        return "failed", "fix_ci", False, "ci_failed"
    mergeable = mergeability_status(metadata)
    if mergeable == "CONFLICTING":
        return "human_gate", "resolve_merge_conflict", False, "pr_merge_conflict"
    if ci_status in {"pending", "running", "none"}:
        if has_blocking_limitation(limitations, ignored_codes={"required_checks_missing_or_pending"}):
            if has_permission_limitation(limitations):
                return "unknown", "fix_github_token_permissions", False, "blocking_limitation"
            return "unknown", "human_gate", False, "blocking_limitation"
        return str(ci_status), "wait", False, "ci_pending"
    if ci_status == "unknown" and has_waitable_required_actions_context_limitation(limitations):
        if has_blocking_limitation(limitations, ignored_codes={"required_checks_missing_or_pending"}):
            if has_permission_limitation(limitations):
                return "unknown", "fix_github_token_permissions", False, "blocking_limitation"
            return "unknown", "human_gate", False, "blocking_limitation"
        return "pending", "wait", False, "ci_pending"
    if ci_status == "passed" and actionable_reason:
        return "human_gate", "address_review_feedback", True, actionable_reason
    if has_permission_limitation(limitations):
        return "unknown", "fix_github_token_permissions", False, "blocking_limitation"
    if has_blocking_limitation(limitations):
        return "unknown", "human_gate", False, "blocking_limitation"
    if ci_status == "passed" and has_waitable_required_actions_context_limitation(limitations):
        return "pending", "wait", False, "ci_pending"
    if ci_status != "passed":
        return "unknown", "human_gate", False, "blocking_limitation"
    if mergeable == "UNKNOWN":
        return "pending", "wait", False, "pr_mergeability_pending"
    if mergeable != "MERGEABLE":
        return "human_gate", "human_gate", False, "pr_mergeability_unknown"
    if decision_status_reason == "current_selected_changes_requested" or selected_changes_requested_evidence:
        return "human_gate", "address_review_feedback", True, "current_selected_changes_requested"
    fallback_pass_candidate = decision.get("fallback_pass_candidate")
    if (
        completion_signal == "fallback_issue_comment"
        and isinstance(fallback_pass_candidate, dict)
        and fallback_pass_candidate.get("promotes_top_level_status") is True
        and review_status not in {"changes_requested", "requested", "pending", "unknown", "unresolved"}
    ):
        decision["status"] = "passed"
        decision["status_reason"] = "fallback_issue_comment_no_major_issues"
        decision["recommended_next_action"] = "merge_prepared"
        decision["observation_complete"] = True
        return "passed", "merge_prepared", True, "fallback_issue_comment_no_major_issues"
    if completion_signal == "fallback_issue_comment":
        return "human_gate", "manual_review_required_non_retryable", False, "fallback_issue_comment_low_confidence"
    if decision_status_reason == "missing_current_completion_signal":
        missing_status = decision_status if decision_status not in {None, "", "unknown"} else "pending"
        missing_action = decision_action or "wait_or_resume"
        if (
            missing_action == "wait_or_resume"
            and not trigger_comment_id
            and not trigger_created_at
        ):
            missing_action = "wait"
        return str(missing_status), missing_action, False, "missing_current_completion_signal"
    if (
        completion_signal == "codex_no_findings_issue_comment"
        and decision_status == "passed"
        and decision_action == "review_completion_observed"
    ):
        return "passed", "merge_prepared", True, "codex_no_findings_issue_comment"
    if decision_status == "passed":
        return "passed", "merge_prepared", True, "passed"
    if decision_status_reason:
        return (
            decision_status or "unknown",
            decision_action or "human_gate",
            bool(decision_observation_complete) if isinstance(decision_observation_complete, bool) else False,
            decision_status_reason,
        )
    if review_status in {"requested", "commented", "changes_requested", "unresolved"}:
        return "human_gate", "address_review_feedback", True, (
            "current_selected_changes_requested"
            if review_status == "changes_requested"
            else "current_selected_unresolved_thread"
        )
    if completion_signal != "submitted_pull_request_review":
        return "pending", "wait", False, "missing_current_completion_signal"
    if review_status in {"none", "approved"}:
        return "passed", "merge_prepared", True, "passed"
    return "unknown", "human_gate", False, decision_status_reason


def load_metadata(path: Path) -> tuple[dict[str, object], str]:
    payload = load_json_path(path)
    if not isinstance(payload, dict):
        return {}, ""
    head = payload.get("headRefOid")
    return payload, head if isinstance(head, str) else ""


def parse_paginated_gh_api_json(stdout: str) -> object:
    text = stdout.strip()
    if not text:
        return {}
    decoder = json.JSONDecoder()
    documents: list[object] = []
    index = 0
    while index < len(text):
        document, end_index = decoder.raw_decode(text, index)
        documents.append(document)
        index = end_index
        while index < len(text) and text[index].isspace():
            index += 1
    if len(documents) == 1:
        return documents[0]
    if all(isinstance(document, dict) and isinstance(document.get("jobs"), list) for document in documents):
        jobs: list[object] = []
        total_count = 0
        saw_total_count = False
        for document in documents:
            if not isinstance(document, dict):
                continue
            page_jobs = document.get("jobs")
            if isinstance(page_jobs, list):
                jobs.extend(page_jobs)
            page_total_count = document.get("total_count")
            if isinstance(page_total_count, int):
                total_count += page_total_count
                saw_total_count = True
        return {"total_count": total_count if saw_total_count else len(jobs), "jobs": jobs}
    return documents


def run_gh_api_json(path: str, *, paginate: bool = False) -> tuple[object, int, str]:
    command = ["gh", "api", path]
    if paginate:
        command.append("--paginate")
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        return {}, completed.returncode, completed.stderr or ""
    try:
        payload = parse_paginated_gh_api_json(completed.stdout) if paginate else json.loads(completed.stdout or "{}")
        return payload, 0, completed.stderr or ""
    except json.JSONDecodeError:
        return {}, 1, "fixed read-only GitHub API returned non-JSON output"


def successful_actions_contexts(ci_payload: dict[str, object]) -> set[str]:
    actions = ci_payload.get("actions") if isinstance(ci_payload.get("actions"), dict) else {}
    contexts: set[str] = set()
    for job in actions.get("jobs", []) if isinstance(actions.get("jobs"), list) else []:
        if not isinstance(job, dict):
            continue
        name = job.get("name")
        status = str(job.get("status") or "").lower()
        conclusion = str(job.get("conclusion") or "").lower()
        if isinstance(name, str) and name and status == "completed" and conclusion in {"success", "neutral", "skipped"}:
            contexts.add(name)
    return contexts


def actions_jobs_collection(ci_payload: dict[str, object]) -> dict[str, object]:
    actions = ci_payload.get("actions") if isinstance(ci_payload.get("actions"), dict) else {}
    jobs_summary = actions.get("jobs_summary") if isinstance(actions.get("jobs_summary"), dict) else {}
    collection = jobs_summary.get("collection") if isinstance(jobs_summary.get("collection"), dict) else {}
    return collection if isinstance(collection, dict) else {}


def has_skipped_green_run_jobs(ci_payload: dict[str, object]) -> bool:
    skipped = actions_jobs_collection(ci_payload).get("skipped_green_runs")
    return isinstance(skipped, int) and skipped > 0


def successful_jobs_from_payload(payload: object) -> set[str] | None:
    if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
        return None
    contexts: set[str] = set()
    for job in payload.get("jobs", []):
        if not isinstance(job, dict):
            continue
        name = job.get("name")
        status = str(job.get("status") or "").lower()
        conclusion = str(job.get("conclusion") or "").lower()
        if isinstance(name, str) and name and status == "completed" and conclusion in {"success", "neutral", "skipped"}:
            contexts.add(name)
    return contexts


def expand_successful_actions_contexts(
    *, repo: str, ci_payload: dict[str, object], missing_contexts: list[str]
) -> tuple[set[str], bool, list[dict[str, object]]]:
    contexts = successful_actions_contexts(ci_payload)
    if not missing_contexts or not has_skipped_green_run_jobs(ci_payload):
        return contexts, False, []
    actions = ci_payload.get("actions") if isinstance(ci_payload.get("actions"), dict) else {}
    limitations: list[dict[str, object]] = []
    expanded_all = True
    for run in actions.get("runs", []) if isinstance(actions.get("runs"), list) else []:
        if not isinstance(run, dict):
            continue
        run_id = run.get("id")
        if not isinstance(run_id, int):
            expanded_all = False
            continue
        jobs_api = f"repos/{repo}/actions/runs/{run_id}/jobs"
        jobs_payload, jobs_exit, jobs_stderr = run_gh_api_json(jobs_api, paginate=True)
        if jobs_exit != 0:
            expanded_all = False
            limitations.append(
                {
                    "code": "required_actions_context_expansion_unavailable",
                    "source": jobs_api,
                    "capability": "actions_read",
                    "severity": "info",
                    "message": "fixed Actions jobs expansion could not verify required contexts",
                    "recommended_next_action": "wait",
                    "exit_code": jobs_exit,
                    "stderr_classification": classify_github_stderr(jobs_stderr),
                }
            )
            continue
        expanded = successful_jobs_from_payload(jobs_payload)
        if expanded is None:
            expanded_all = False
            limitations.append(
                {
                    "code": "required_actions_context_expansion_unavailable",
                    "source": jobs_api,
                    "capability": "actions_read",
                    "severity": "info",
                    "message": "fixed Actions jobs expansion returned an unexpected schema",
                    "recommended_next_action": "wait",
                }
            )
            continue
        contexts.update(expanded)
    return contexts, not expanded_all, limitations


def required_status_contexts(protection_payload: object) -> tuple[set[str], set[str], bool]:
    if not isinstance(protection_payload, dict):
        return set(), set(), False
    required_status_checks = protection_payload.get("required_status_checks")
    if required_status_checks is None:
        return set(), set(), True
    if not isinstance(required_status_checks, dict):
        return set(), set(), False
    legacy_contexts: set[str] = set()
    actions_contexts: set[str] = set()
    non_actions_contexts: set[str] = set()
    raw_contexts = required_status_checks.get("contexts")
    if isinstance(raw_contexts, list):
        for context in raw_contexts:
            if isinstance(context, str) and context:
                legacy_contexts.add(context)
    raw_checks = required_status_checks.get("checks")
    if isinstance(raw_checks, list):
        for check in raw_checks:
            if not isinstance(check, dict):
                return actions_contexts, non_actions_contexts, False
            context = check.get("context")
            if not isinstance(context, str) or not context:
                continue
            if check.get("app_id") in ACTIONS_SATISFIABLE_REQUIRED_CHECK_APP_IDS:
                actions_contexts.add(context)
            else:
                non_actions_contexts.add(context)
    concrete_contexts = actions_contexts | non_actions_contexts
    actions_contexts.update(legacy_contexts - concrete_contexts)
    non_actions_contexts.difference_update(actions_contexts)
    return actions_contexts, non_actions_contexts, True


def current_review_satisfies_simple_required_reviews(
    required_pull_request_reviews: object, review_payload: dict[str, object]
) -> bool:
    if not isinstance(required_pull_request_reviews, dict):
        return False
    required_count = required_pull_request_reviews.get("required_approving_review_count")
    if not isinstance(required_count, int):
        return False
    if required_count > 1:
        return False
    if required_pull_request_reviews.get("dismiss_stale_reviews") is True:
        return False
    if required_pull_request_reviews.get("require_code_owner_reviews") is True:
        return False
    if required_pull_request_reviews.get("require_last_push_approval") is True:
        return False
    status = review_payload.get("status")
    if isinstance(status, str) and status.lower() == "approved":
        return True
    decision = collector_decision_payload({}, review_payload)
    decision_status = decision.get("status")
    decision_action = decision.get("recommended_next_action")
    return decision_status == "passed" and decision_action == "merge_prepared"


def head_owner_login(metadata: dict[str, object]) -> str | None:
    owner = metadata.get("headRepositoryOwner")
    if not isinstance(owner, dict):
        return None
    login = owner.get("login")
    if isinstance(login, str) and login:
        return login
    name = owner.get("name")
    if isinstance(name, str) and name:
        return name
    return None


def collect_merge_blocker_metadata(
    *,
    repo: str,
    metadata: dict[str, object],
    ci_payload: dict[str, object],
    review_payload: dict[str, object] | None = None,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    limitations: list[dict[str, object]] = []
    base_ref = metadata.get("baseRefName")
    head_ref = metadata.get("headRefName")
    if not isinstance(base_ref, str) or not base_ref or not isinstance(head_ref, str) or not head_ref:
        return {
            "compare": {"available": False},
            "branch_protection": {"available": False},
        }, [
            {
                "code": "pr_branch_metadata_schema_unavailable",
                "source": "gh_pr_view",
                "severity": "blocking",
                "message": "fixed PR metadata did not include usable baseRefName and headRefName",
            }
        ]

    encoded_base = quote(base_ref, safe="")
    base_repo_owner = repo.split("/", 1)[0]
    head_owner = head_owner_login(metadata)
    encoded_head = (
        f"{quote(head_owner, safe='')}:{quote(head_ref, safe='')}"
        if head_owner and head_owner != base_repo_owner
        else quote(head_ref, safe="")
    )
    compare_api = f"repos/{repo}/compare/{encoded_base}...{encoded_head}"
    compare_payload, compare_exit, compare_stderr = run_gh_api_json(compare_api)
    compare_metadata: dict[str, object] = {"available": compare_exit == 0, "api": compare_api}
    if compare_exit != 0:
        limitations.append(
            optional_github_api_failure_limitation(
                api=compare_api,
                source=compare_api,
                capability="compare_read",
                exit_code=compare_exit,
                stderr=compare_stderr,
                default_code="pr_compare_metadata_unavailable",
                default_message="fixed compare metadata could not verify PR branch freshness",
            )
        )
    elif not isinstance(compare_payload, dict):
        compare_metadata["available"] = False
        limitations.append(
            {
                "code": "pr_compare_metadata_unavailable",
                "source": compare_api,
                "severity": "warning",
                "message": "fixed compare metadata returned an unexpected schema",
                "recommended_next_action": "continue_with_available_metadata",
            }
        )
    else:
        status = compare_payload.get("status")
        behind_by = compare_payload.get("behind_by")
        ahead_by = compare_payload.get("ahead_by")
        compare_metadata.update(
            {
                "status": status,
                "behind_by": behind_by,
                "ahead_by": ahead_by,
            }
        )
    branch_is_behind = (
        compare_metadata.get("status") in {"behind", "diverged"}
        or (
            isinstance(compare_metadata.get("behind_by"), int)
            and compare_metadata.get("behind_by") > 0
        )
    )

    def add_strict_behind_limitation(source: str) -> None:
        limitations.append(
            {
                "code": "pr_branch_behind",
                "source": source,
                "severity": "blocking",
                "message": "PR head branch is behind or diverged from a strict required-check base branch",
                "recommended_next_action": "update_pr_branch",
                "compare_status": compare_metadata.get("status"),
                "behind_by": compare_metadata.get("behind_by"),
            }
        )

    branch_api = f"repos/{repo}/branches/{encoded_base}"
    branch_payload, branch_exit, branch_stderr = run_gh_api_json(branch_api)
    protection_metadata: dict[str, object] = {
        "available": branch_exit == 0,
        "api": branch_api,
    }
    if branch_exit != 0:
        limitations.append(
            optional_github_api_failure_limitation(
                api=branch_api,
                source=branch_api,
                capability="branch_metadata_read",
                exit_code=branch_exit,
                stderr=branch_stderr,
                default_code="branch_metadata_unavailable",
                default_message="fixed branch metadata could not verify protection state",
            )
        )
    elif not isinstance(branch_payload, dict) or not isinstance(branch_payload.get("protected"), bool):
        protection_metadata["available"] = False
        limitations.append(
            {
                "code": "branch_metadata_unavailable",
                "source": branch_api,
                "capability": "branch_metadata_read",
                "severity": "blocking",
                "message": "fixed branch metadata returned an unexpected protection schema",
                "recommended_next_action": "human_gate",
            }
        )
    elif branch_payload.get("protected") is False:
        protection_metadata.update(
            {
                "available": True,
                "protected": False,
                "status": "unprotected",
            }
        )
    else:
        protection_api = f"repos/{repo}/branches/{encoded_base}/protection"
        protection_payload, protection_exit, protection_stderr = run_gh_api_json(protection_api)
        protection_metadata.update(
            {
                "protected": True,
                "protection_api": protection_api,
                "protection_available": protection_exit == 0,
            }
        )
        if protection_exit != 0:
            limitations.append(
                optional_github_api_failure_limitation(
                    api=protection_api,
                    source=protection_api,
                    capability="branch_protection_read",
                    exit_code=protection_exit,
                    stderr=protection_stderr,
                    default_code="branch_protection_read_optional",
                    default_message="fixed branch protection metadata could not be verified",
                )
            )
            return {
                "compare": compare_metadata,
                "branch_protection": protection_metadata,
            }, limitations
        required_status_checks = (
            protection_payload.get("required_status_checks")
            if isinstance(protection_payload, dict)
            else None
        )
        strict_required_checks = (
            isinstance(required_status_checks, dict)
            and required_status_checks.get("strict") is True
        )
        protection_metadata["strict"] = strict_required_checks
        if branch_is_behind and strict_required_checks:
            add_strict_behind_limitation(protection_api)
        lock_branch = (
            protection_payload.get("lock_branch")
            if isinstance(protection_payload, dict)
            else None
        )
        lock_branch_enabled = (
            isinstance(lock_branch, dict)
            and lock_branch.get("enabled") is True
        )
        protection_metadata["lock_branch"] = {
            "enabled": lock_branch_enabled,
        }
        if lock_branch_enabled:
            limitations.append(
                {
                    "code": "protected_branch_locked",
                    "source": protection_api,
                    "capability": "branch_protection_read",
                    "severity": "blocking",
                    "message": "base branch protection marks the branch as locked/read-only",
                    "recommended_next_action": "human_gate",
                }
            )
        required_pull_request_reviews = (
            protection_payload.get("required_pull_request_reviews")
            if isinstance(protection_payload, dict)
            else None
        )
        pull_request_review_metadata = {
            "required": required_pull_request_reviews is not None,
        }
        if isinstance(required_pull_request_reviews, dict):
            pull_request_review_metadata.update(
                {
                    "required_approving_review_count": required_pull_request_reviews.get(
                        "required_approving_review_count"
                    ),
                    "dismiss_stale_reviews": required_pull_request_reviews.get(
                        "dismiss_stale_reviews"
                    ),
                    "require_code_owner_reviews": required_pull_request_reviews.get(
                        "require_code_owner_reviews"
                    ),
                    "require_last_push_approval": required_pull_request_reviews.get(
                        "require_last_push_approval"
                    ),
                }
            )
            review_satisfied = current_review_satisfies_simple_required_reviews(
                required_pull_request_reviews,
                review_payload if isinstance(review_payload, dict) else {},
            )
            pull_request_review_metadata["satisfied_by_observed_review_evidence"] = review_satisfied
            if not review_satisfied:
                limitations.append(
                    {
                        "code": "required_pull_request_reviews_unverified",
                        "source": protection_api,
                        "capability": "pull_request_reviews_read",
                        "severity": "blocking",
                        "message": "branch protection requires pull request reviews that cannot be fully proven by the observation script",
                        "recommended_next_action": "human_gate",
                        "required_pull_request_reviews": pull_request_review_metadata,
                    }
                )
        protection_metadata["required_pull_request_reviews"] = pull_request_review_metadata
        contexts, non_actions_contexts, schema_ok = required_status_contexts(protection_payload)
        if not schema_ok:
            limitations.append(
                {
                    "code": "branch_protection_metadata_unavailable",
                    "source": protection_api,
                    "capability": "branch_protection_read",
                    "severity": "blocking",
                    "message": "branch protection metadata returned an unexpected required status checks schema",
                    "recommended_next_action": "human_gate",
                }
            )
        observed_contexts = successful_actions_contexts(ci_payload)
        missing = sorted(context for context in contexts if context not in observed_contexts)
        expansion_incomplete = False
        expansion_limitations: list[dict[str, object]] = []
        if missing and has_skipped_green_run_jobs(ci_payload):
            observed_contexts, expansion_incomplete, expansion_limitations = expand_successful_actions_contexts(
                repo=repo,
                ci_payload=ci_payload,
                missing_contexts=missing,
            )
            limitations.extend(expansion_limitations)
            missing = sorted(context for context in contexts if context not in observed_contexts)
        ci_status = str(ci_payload.get("status") or "unknown")
        protection_metadata.update(
            {
                "protected": True,
                "strict": strict_required_checks,
                "required_status_contexts": sorted(contexts | non_actions_contexts),
                "required_github_actions_contexts": sorted(contexts),
                "required_non_actions_contexts": sorted(non_actions_contexts),
                "observed_successful_actions_contexts": sorted(observed_contexts),
                "missing_required_status_contexts": missing,
                "unprovable_required_status_contexts": sorted(non_actions_contexts),
            }
        )
        if non_actions_contexts:
            limitations.append(
                {
                    "code": "required_non_actions_context_unprovable_by_actions",
                    "source": protection_api,
                    "capability": "branch_protection_read",
                    "severity": "blocking",
                    "message": "branch protection requires non-GitHub-Actions status contexts that cannot be proven with Actions evidence",
                    "recommended_next_action": "human_gate",
                    "unprovable_required_status_contexts": sorted(non_actions_contexts),
                }
            )
        if missing:
            if ci_status in {"pending", "running", "none", "unknown"} or expansion_incomplete:
                limitations.append(
                    {
                        "code": "required_actions_context_pending",
                        "source": protection_api,
                        "capability": "branch_protection_read",
                        "severity": "info",
                        "message": "branch protection requires GitHub Actions contexts that are not observed successful yet",
                        "recommended_next_action": "wait",
                        "missing_required_status_contexts": missing,
                    }
                )
                return {
                    "compare": compare_metadata,
                    "branch_protection": protection_metadata,
                }, limitations
            limitations.append(
                {
                    "code": "required_actions_context_unobserved",
                    "source": protection_api,
                    "capability": "branch_protection_read",
                    "severity": "blocking",
                    "message": "branch protection requires status contexts not observed as successful GitHub Actions runs or jobs",
                    "recommended_next_action": "human_gate",
                    "missing_required_status_contexts": missing,
                }
            )
    return {
        "compare": compare_metadata,
        "branch_protection": protection_metadata,
    }, limitations


def observation_snapshot(args: Args, script_dir: Path, tmp_dir: Path) -> str:
    checks_script = script_dir / "lib" / "fetch_pr_checks_snapshot.sh"
    review_script = script_dir / "lib" / "fetch_pr_review_snapshot.sh"

    gh_stdout = tmp_dir / "gh-pr-view.json"
    gh_stderr = tmp_dir / "gh-pr-view.stderr"
    gh_exit = run_to_files(
        ["gh", "pr", "view", str(args.pr), "--repo", args.repo, "--json", PR_METADATA_FIELDS],
        gh_stdout,
        gh_stderr,
    )

    metadata: dict[str, object] = {}
    current_head_sha = ""
    if gh_exit == 0:
        metadata, current_head_sha = load_metadata(gh_stdout)

    checks_stdout = tmp_dir / "checks.json"
    checks_stderr = tmp_dir / "checks.stderr"
    review_stdout = tmp_dir / "review.json"
    review_stderr = tmp_dir / "review.stderr"
    final_gh_stdout = tmp_dir / "gh-pr-view-final.json"
    final_gh_stderr = tmp_dir / "gh-pr-view-final.stderr"

    checks_exit = 0
    review_exit = 0
    final_gh_exit = 0
    final_metadata: dict[str, object] = {}
    final_current_head_sha = ""
    collection_head_sha = ""

    if gh_exit == 0 and current_head_sha:
        checks_head_sha = args.head_sha or current_head_sha
        collection_head_sha = checks_head_sha
        if not args.head_sha or sha_matches(current_head_sha, args.head_sha):
            checks_exit = run_to_files(
                [str(checks_script), "--repo", args.repo, "--pr", str(args.pr), "--head-sha", checks_head_sha],
                checks_stdout,
                checks_stderr,
            )
            review_args = [
                str(review_script),
                "--repo",
                args.repo,
                "--pr",
                str(args.pr),
                "--head-sha",
                checks_head_sha,
                "--body-mode",
                args.body_mode,
            ]
            if args.trigger_comment_id:
                review_args.extend(["--trigger-comment-id", args.trigger_comment_id])
            if args.trigger_created_at:
                review_args.extend(["--trigger-created-at", args.trigger_created_at])
            if args.out_dir:
                review_args.extend(["--out", args.out_dir])
            review_exit = run_to_files(review_args, review_stdout, review_stderr)
            final_gh_exit = run_to_files(
                ["gh", "pr", "view", str(args.pr), "--repo", args.repo, "--json", PR_METADATA_FIELDS],
                final_gh_stdout,
                final_gh_stderr,
            )
            if final_gh_exit == 0:
                final_metadata, final_current_head_sha = load_metadata(final_gh_stdout)
        else:
            checks_stdout.write_text("{}\n", encoding="utf-8")
            review_stdout.write_text("{}\n", encoding="utf-8")
    else:
        checks_stdout.write_text("{}\n", encoding="utf-8")
        review_stdout.write_text("{}\n", encoding="utf-8")

    provided_head_sha = args.head_sha
    expected_head_sha = provided_head_sha or collection_head_sha or None
    current_head_value = current_head_sha or None
    head_matches_expected = (
        None
        if expected_head_sha is None or current_head_value is None
        else sha_matches(current_head_value, expected_head_sha)
    )
    limitations: list[object] = []
    summary: dict[str, object] = {"ci": "unknown", "review": "unknown", "head": "unknown"}
    ci_payload: dict[str, object] = {
        "status": "unknown",
        "checks": [],
        "failures": [],
        "collector": "pending_s03",
    }
    review_payload: dict[str, object] = {
        "status": "unknown",
        "signals": [],
        "codex_authored": [],
        "collector": "pending_s04",
    }
    review_wrapper_payload: dict[str, object] = {}
    merge_blocker_metadata: dict[str, object] = {
        "compare": {"available": False},
        "branch_protection": {"available": False},
    }
    normalized_status = "unknown"
    recommended_next_action = "human_gate"

    if gh_exit != 0:
        limitations.append(
            pr_metadata_failure_limitation(
                exit_code=gh_exit,
                stderr=read_text(gh_stderr),
                default_code="pr_metadata_collection_failed",
                default_message="fixed read-only PR metadata collection failed",
            )
        )
    elif not metadata or not current_head_sha:
        limitations.append(
            {
                "code": "pr_metadata_schema_unavailable",
                "source": "gh_pr_view",
                "severity": "blocking",
                "message": "fixed PR metadata collection did not return a usable headRefOid",
            }
        )
    elif provided_head_sha and current_head_sha and not sha_matches(current_head_sha, provided_head_sha):
        normalized_status = "stale_head"
        summary["head"] = "stale"
        recommended_next_action = "rerun_for_current_head"
        limitations.append(
            {
                "code": "stale_head",
                "source": "pr_metadata",
                "severity": "blocking",
                "message": "current PR head SHA does not match expected head SHA",
            }
        )
    else:
        if final_gh_exit != 0:
            limitations.append(
                pr_metadata_failure_limitation(
                    exit_code=final_gh_exit,
                    stderr=read_text(final_gh_stderr),
                    default_code="pr_head_revalidation_failed",
                    default_message="fixed read-only PR head revalidation failed after snapshot collection",
                )
            )
        elif not final_current_head_sha:
            limitations.append(
                {
                    "code": "pr_head_revalidation_schema_unavailable",
                    "source": "gh_pr_view",
                    "severity": "blocking",
                    "message": "fixed PR head revalidation did not return a usable headRefOid",
                }
            )
        elif collection_head_sha and not sha_matches(final_current_head_sha, collection_head_sha):
            current_head_sha = final_current_head_sha
            if final_metadata:
                metadata = final_metadata
            normalized_status = "stale_head"
            summary["head"] = "stale"
            recommended_next_action = "rerun_for_current_head"
            head_matches_expected = False
            limitations.append(
                {
                    "code": "stale_head",
                    "source": "pr_metadata_revalidation",
                    "severity": "blocking",
                    "message": "current PR head SHA changed during snapshot collection",
                }
            )
        elif final_current_head_sha:
            current_head_sha = final_current_head_sha
            if final_metadata:
                metadata = final_metadata
            head_matches_expected = None if expected_head_sha is None else sha_matches(current_head_sha, expected_head_sha)
        if summary["head"] != "stale":
            summary["head"] = "matched" if expected_head_sha else "observed"

        checks_payload_raw = load_json_path(checks_stdout)
        checks_payload = checks_payload_raw if isinstance(checks_payload_raw, dict) else {}
        ci_raw = checks_payload.get("ci")
        if checks_exit == 0 and isinstance(ci_raw, dict):
            ci_payload = ci_raw
            summary["ci"] = ci_payload.get("status") or "unknown"
            limitations.extend(checks_payload.get("limitations", []))
        else:
            limitations.append(
                {
                    "code": "ci_collection_failed",
                    "source": "fetch_pr_checks_snapshot.sh",
                    "severity": "blocking",
                    "message": "fixed CI/check/status collector failed",
                    "exit_code": checks_exit,
                    "stderr_sha256": hashlib.sha256(read_text(checks_stderr).encode()).hexdigest(),
                }
            )

        review_payload_raw = load_json_path(review_stdout)
        review_wrapper_payload = review_payload_raw if isinstance(review_payload_raw, dict) else {}
        review_raw = review_wrapper_payload.get("review")
        if review_exit == 0 and isinstance(review_raw, dict):
            review_payload = review_raw
            summary["review"] = review_payload.get("status") or "unknown"
            limitations.extend(review_wrapper_payload.get("limitations", []))
        else:
            limitations.append(
                {
                    "code": "review_collection_failed",
                    "source": "fetch_pr_review_snapshot.sh",
                    "severity": "blocking",
                    "message": "fixed review/comment/thread collector failed",
                    "exit_code": review_exit,
                    "stderr_sha256": hashlib.sha256(read_text(review_stderr).encode()).hexdigest(),
                }
            )
        merge_blocker_metadata, merge_blocker_limitations = collect_merge_blocker_metadata(
            repo=args.repo,
            metadata=metadata,
            ci_payload=ci_payload,
            review_payload=review_payload,
        )
        limitations.extend(merge_blocker_limitations)
    normalized_status, recommended_next_action, observation_complete, status_reason = classify_snapshot(
        summary=summary,
        ci_payload=ci_payload,
        review_payload=review_payload,
        review_wrapper_payload=review_wrapper_payload,
        metadata=metadata,
        limitations=limitations,
        head_matches_expected=head_matches_expected,
        normalized_status=normalized_status,
        trigger_comment_id=args.trigger_comment_id,
        trigger_created_at=args.trigger_created_at,
    )
    if status_reason in {"current_selected_unresolved_thread", "carryover_non_outdated_unresolved_thread"}:
        summary["review"] = "unresolved"

    review_collector_fingerprint = review_wrapper_payload.get("fingerprint") if isinstance(review_wrapper_payload, dict) else None
    review_decision_payload = collector_decision_payload(review_wrapper_payload, review_payload)
    review_decision_fingerprint = (
        review_wrapper_payload.get("decision_fingerprint")
        if isinstance(review_wrapper_payload, dict) and review_wrapper_payload.get("decision_fingerprint")
        else review_decision_payload.get("fingerprint")
    )
    review_audit_fingerprint = review_wrapper_payload.get("audit_fingerprint") if isinstance(review_wrapper_payload, dict) else None
    if isinstance(review_payload, dict) and review_collector_fingerprint:
        review_payload = {**review_payload, "fingerprint": review_collector_fingerprint}
    codex_review_payload = (
        review_wrapper_payload.get("codex_review")
        if isinstance(review_wrapper_payload.get("codex_review"), dict)
        else (
            review_payload.get("codex_review")
            if isinstance(review_payload, dict) and isinstance(review_payload.get("codex_review"), dict)
            else {}
        )
    )

    checks_payload_for_fingerprint = load_json_path(checks_stdout)
    if not isinstance(checks_payload_for_fingerprint, dict):
        checks_payload_for_fingerprint = {}
    ci_actions = ci_payload.get("actions") if isinstance(ci_payload.get("actions"), dict) else {}
    fingerprint_source = {
        "repo": args.repo,
        "pr": args.pr,
        "expected_head_sha": expected_head_sha,
        "current_head_sha": current_head_sha or None,
        "normalized_status": normalized_status,
        "limitations": [item["code"] for item in limitations if isinstance(item, dict) and "code" in item],
        "ci_status": ci_payload.get("status"),
        "ci_source_policy": checks_payload_for_fingerprint.get("source_policy")
        or ci_payload.get("source_policy"),
        "ci_actions": {
            "available": ci_actions.get("available"),
            "workflow_runs": ci_actions.get("workflow_runs"),
            "jobs_summary": ci_actions.get("jobs_summary"),
        },
        "merge_blocker_metadata": merge_blocker_metadata,
        "ci_fingerprint": checks_payload_for_fingerprint.get("fingerprint"),
        "review_decision_fingerprint": review_decision_fingerprint,
    }
    fingerprint = hashlib.sha256(
        json.dumps(fingerprint_source, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    trigger = {
        "source": (
            review_wrapper_payload.get("trigger", {}).get("source")
            if isinstance(review_wrapper_payload.get("trigger"), dict)
            else ("explicit" if args.trigger_comment_id or args.trigger_created_at else "none")
        ),
        "comment_id": int(args.trigger_comment_id) if args.trigger_comment_id else None,
        "created_at": args.trigger_created_at,
    }
    if isinstance(review_wrapper_payload.get("trigger"), dict):
        trigger["comment_id"] = review_wrapper_payload["trigger"].get("comment_id")
        trigger["created_at"] = review_wrapper_payload["trigger"].get("created_at")

    decision_payload = {
        **review_decision_payload,
        "status": normalized_status,
        "status_reason": status_reason,
        "recommended_next_action": recommended_next_action,
        "observation_complete": observation_complete,
        "fingerprint": fingerprint,
    }
    decision_payload.setdefault("scope", "current_trigger_boundary")
    decision_payload.setdefault("trigger", trigger)
    decision_payload.setdefault("completion_signal", None)
    decision_payload.setdefault("fallback_pass_candidate", {"present": False, "promotes_top_level_status": False})

    payload = {
        "script": "fetch_pr_observation_snapshot.sh",
        "status": normalized_status,
        "overall_status": normalized_status,
        "normalized_status": normalized_status,
        "observation_complete": observation_complete,
        "observed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "repo": args.repo,
        "pr": args.pr,
        "expected_head_sha": expected_head_sha,
        "current_head_sha": current_head_sha or None,
        "head_matches_expected": head_matches_expected,
        "fingerprint": fingerprint,
        "decision_fingerprint": fingerprint,
        "audit_fingerprint": review_audit_fingerprint or review_collector_fingerprint,
        "summary": summary,
        "limitations": limitations,
        "recommended_next_action": recommended_next_action,
        "ci": {**ci_payload},
        "review": review_payload,
        "decision": decision_payload,
        "codex_review": codex_review_payload,
        "trigger": trigger,
        "body_mode": args.body_mode,
        "merge_blocker_metadata": merge_blocker_metadata,
        "artifacts": {
            "result_json": f"{args.out_dir}/result.json" if args.out_dir else None,
            "latest_json": f"{args.out_dir}/latest.json" if args.out_dir else None,
            "events_ndjson": f"{args.out_dir}/events.ndjson" if args.out_dir else None,
            "latest_delta_json": f"{args.out_dir}/latest_delta.json" if args.out_dir else None,
            "snapshots_dir": f"{args.out_dir}/snapshots" if args.out_dir else None,
        },
        "pr_metadata": metadata,
    }
    result_json = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"

    if args.out_dir:
        out_dir = Path(args.out_dir)
        (out_dir / "raw").mkdir(parents=True, exist_ok=True)
        (out_dir / "result.json").write_text(result_json, encoding="utf-8")
        (out_dir / "latest.json").write_text(result_json, encoding="utf-8")
        (out_dir / "latest_delta.json").write_text("{}\n", encoding="utf-8")
        (out_dir / "events.ndjson").write_text('{"event":"snapshot","result":"stdout_json"}\n', encoding="utf-8")
        if gh_stdout.exists() and gh_stdout.stat().st_size > 0:
            shutil.copyfile(gh_stdout, out_dir / "raw" / "pr_view.json")
        if gh_stderr.exists() and gh_stderr.stat().st_size > 0:
            shutil.copyfile(gh_stderr, out_dir / "raw" / "pr_view.stderr")
    return result_json


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    script_dir = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="pr-observation-snapshot.") as tmp:
        sys.stdout.write(observation_snapshot(args, script_dir, Path(tmp)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
