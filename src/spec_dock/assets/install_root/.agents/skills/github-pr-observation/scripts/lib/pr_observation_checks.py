import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone

repo = os.environ["OBS_REPO"]
pr = int(os.environ["OBS_PR"])
expected_head_sha = os.environ["OBS_HEAD_SHA"]
expected_head_sha_lower = expected_head_sha.lower()
TERMINAL_GREEN_JOB_EXPANSION_CAP = 1


def token_source():
    if os.environ.get("GH_TOKEN"):
        return "GH_TOKEN"
    if os.environ.get("GITHUB_TOKEN"):
        return "GITHUB_TOKEN"
    return "gh_saved_auth"


def classify_github_stderr(stderr):
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


def capability_for_api(api):
    if api == "gh_pr_view.statusCheckRollup":
        return "status_check_rollup_read"
    if api.endswith("/actions/runs") or "/actions/runs?" in api:
        return "actions_read"
    if api.endswith("/check-runs"):
        return "check_runs_read"
    if api.endswith("/status"):
        return "commit_statuses_read"
    if "/actions/runs/" in api and api.endswith("/jobs"):
        return "actions_read"
    return "unknown"


def is_blocking_limitation(limitation):
    return limitation.get("severity") == "blocking" or limitation.get("blocking") is True


def github_failure_limitation(*, api, source, exit_code, stderr, default_code, default_message, default_severity):
    classification = classify_github_stderr(stderr)
    stderr_sha256 = hashlib.sha256((stderr or "").encode()).hexdigest()
    if classification == "permission_denied":
        return {
            "code": "github_token_permission_denied",
            "capability": capability_for_api(api),
            "api": api,
            "source": source,
            "status": "permission_denied",
            "token_source": token_source(),
            "severity": "blocking",
            "message": "GitHub token lacks permission for fixed PR observation API",
            "recommended_next_action": "fix_github_token_permissions",
            "secret_redacted": True,
            "stderr_sha256": stderr_sha256,
            "exit_code": exit_code,
        }
    if classification == "auth_missing":
        return {
            "code": "github_auth_missing",
            "capability": capability_for_api(api),
            "api": api,
            "source": source,
            "status": "auth_missing",
            "token_source": token_source(),
            "severity": "blocking",
            "message": "GitHub authentication is unavailable for fixed PR observation API",
            "recommended_next_action": "authenticate_github_cli",
            "secret_redacted": True,
            "stderr_sha256": stderr_sha256,
            "exit_code": exit_code,
        }
    if classification == "rate_limited":
        return {
            "code": "github_rate_limited",
            "capability": capability_for_api(api),
            "api": api,
            "source": source,
            "status": "rate_limited",
            "token_source": token_source(),
            "severity": "blocking",
            "message": "GitHub rate limit blocked fixed PR observation API",
            "recommended_next_action": "wait_or_retry_later",
            "secret_redacted": True,
            "stderr_sha256": stderr_sha256,
            "exit_code": exit_code,
        }
    if classification == "schema_unavailable":
        return {
            "code": "github_api_schema_unavailable",
            "capability": capability_for_api(api),
            "api": api,
            "source": source,
            "status": "schema_unavailable",
            "token_source": token_source(),
            "severity": "blocking",
            "message": "fixed read-only GitHub API schema is unavailable",
            "recommended_next_action": "inspect_github_api_schema",
            "secret_redacted": True,
            "stderr_sha256": stderr_sha256,
            "exit_code": exit_code,
        }
    if classification == "transient_unknown":
        return {
            "code": "github_transient_unknown",
            "capability": capability_for_api(api),
            "api": api,
            "source": source,
            "status": "transient_unknown",
            "token_source": token_source(),
            "severity": "blocking",
            "message": "transient GitHub failure blocked fixed PR observation API",
            "recommended_next_action": "retry_observation",
            "secret_redacted": True,
            "stderr_sha256": stderr_sha256,
            "exit_code": exit_code,
        }
    return {
        "code": default_code,
        "capability": capability_for_api(api),
        "api": api,
        "source": source,
        "status": classification,
        "token_source": token_source(),
        "severity": default_severity,
        "message": default_message,
        "secret_redacted": True,
        "exit_code": exit_code,
        "stderr_sha256": stderr_sha256,
    }


def sha_prefix_matches(left, right):
    left_lower = str(left or "").lower()
    right_lower = str(right or "").lower()
    return bool(left_lower and right_lower) and (
        left_lower.startswith(right_lower) or right_lower.startswith(left_lower)
    )


def gh_api(path):
    command = ["gh", "api", path, "--paginate"]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        return None, github_failure_limitation(
            api=path,
            source=path,
            exit_code=completed.returncode,
            stderr=completed.stderr,
            default_code="github_api_collection_failed",
            default_message="fixed read-only GitHub API collection failed",
            default_severity="blocking",
        )
    try:
        return parse_gh_paginated_stdout(completed.stdout), None
    except json.JSONDecodeError:
        return None, github_failure_limitation(
            api=path,
            source=path,
            exit_code=completed.returncode,
            stderr=completed.stderr,
            default_code="github_api_schema_unavailable",
            default_message="fixed read-only GitHub API returned non-JSON output",
            default_severity="blocking",
        )


def gh_pr_view():
    command = ["gh", "pr", "view", str(pr), "--repo", repo, "--json", "mergeStateStatus,statusCheckRollup"]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        return {}, github_failure_limitation(
            api="gh_pr_view.statusCheckRollup",
            source="gh_pr_view",
            exit_code=completed.returncode,
            stderr=completed.stderr,
            default_code="pr_required_check_state_unavailable",
            default_message="fixed read-only PR required check state collection failed",
            default_severity="informational",
        )
    try:
        payload = json.loads(completed.stdout or "{}")
    except json.JSONDecodeError:
        return {}, {
            "code": "pr_required_check_state_unavailable",
            "source": "gh_pr_view",
            "severity": "informational",
            "message": "fixed read-only PR required check state returned non-JSON output",
        }
    return payload if isinstance(payload, dict) else {}, None


def gh_pr_head_oid():
    command = ["gh", "pr", "view", str(pr), "--repo", repo, "--json", "headRefOid"]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        return {}, github_failure_limitation(
            api="gh_pr_view.headRefOid",
            source="gh_pr_view",
            exit_code=completed.returncode,
            stderr=completed.stderr,
            default_code="pr_head_sha_resolution_failed",
            default_message="fixed read-only PR head SHA resolution failed",
            default_severity="blocking",
        )
    try:
        payload = json.loads(completed.stdout or "{}")
    except json.JSONDecodeError:
        return {}, {
            "code": "pr_head_sha_resolution_failed",
            "source": "gh_pr_view",
            "severity": "blocking",
            "message": "fixed read-only PR head SHA resolution returned non-JSON output",
        }
    return payload if isinstance(payload, dict) else {}, None


def parse_gh_paginated_stdout(stdout):
    text = stdout or "{}"
    decoder = json.JSONDecoder()
    index = 0
    payloads = []
    while index < len(text):
        while index < len(text) and text[index].isspace():
            index += 1
        if index >= len(text):
            break
        payload, index = decoder.raw_decode(text, index)
        payloads.append(payload)
    if not payloads:
        return {}
    if len(payloads) == 1:
        return payloads[0]
    return merge_paginated_payloads(payloads)


def merge_paginated_payloads(payloads):
    if all(isinstance(payload, list) for payload in payloads):
        merged_list = []
        for payload in payloads:
            merged_list.extend(payload)
        return merged_list
    if not all(isinstance(payload, dict) for payload in payloads):
        return payloads[-1]

    merged = {}
    for payload in payloads:
        for key, value in payload.items():
            if isinstance(value, list):
                merged.setdefault(key, [])
                if isinstance(merged[key], list):
                    merged[key].extend(value)
                else:
                    merged[key] = value
            elif isinstance(value, int) and key in {"total_count"}:
                merged[key] = int(merged.get(key, 0) or 0) + value
            else:
                merged[key] = value
    return merged


def as_list(payload, key):
    value = payload.get(key) if isinstance(payload, dict) else None
    return value if isinstance(value, list) else []


def normalize_check_status(check):
    status = str(check.get("status") or "").lower()
    conclusion = str(check.get("conclusion") or "").lower()
    if status == "completed":
        if conclusion in {
            "failure",
            "error",
            "cancelled",
            "timed_out",
            "action_required",
            "startup_failure",
            "stale",
        }:
            return "failed"
        if conclusion in {"success", "skipped", "neutral"}:
            return conclusion
        if conclusion:
            return "other"
        return "other"
    if status == "in_progress":
        return "running"
    if status in {"queued", "requested", "waiting", "pending"}:
        return "pending"
    return "other"


def normalize_actions_status(item):
    status = str(item.get("status") or "").lower()
    conclusion = str(item.get("conclusion") or "").lower()
    if status == "completed":
        if conclusion in {
            "failure",
            "error",
            "cancelled",
            "timed_out",
            "action_required",
            "startup_failure",
            "stale",
        }:
            return "failed"
        if conclusion in {"success", "skipped", "neutral"}:
            return conclusion
        return "unknown"
    if status == "in_progress":
        return "running"
    if status in {"queued", "requested", "waiting", "pending"}:
        return "pending"
    return "unknown"


def normalize_status_state(status):
    state = str(status.get("state") or "").lower()
    if state in {"failure", "error"}:
        return "failed"
    if state == "pending":
        return "pending"
    if state == "success":
        return "success"
    return "other"


def check_run_failure_fallback(check, limitation=None):
    payload = {
        "kind": "check_run",
        "name": check.get("name"),
        "check_run_id": check.get("id"),
        "status": check.get("status"),
        "conclusion": check.get("conclusion"),
        "html_url": check.get("html_url"),
        "details_url": check.get("details_url"),
    }
    if limitation:
        payload["limitation"] = limitation
    return payload


def job_matches_check(job, check_id):
    if check_id is None:
        return True
    check_run_url = str(job.get("check_run_url") or "")
    terminal_segment = check_run_url.rstrip("/").rsplit("/", 1)[-1]
    return terminal_segment == str(check_id)


FAILED_ACTION_CONCLUSIONS = {
    "failure",
    "error",
    "cancelled",
    "timed_out",
    "action_required",
    "startup_failure",
    "stale",
}


def failed_action_steps(job):
    steps = job.get("steps") if isinstance(job.get("steps"), list) else []
    return [
        {
            "number": step.get("number"),
            "name": step.get("name"),
            "status": step.get("status"),
            "conclusion": step.get("conclusion"),
        }
        for step in steps
        if str(step.get("conclusion") or "").lower() in FAILED_ACTION_CONCLUSIONS
    ]


def actions_failure_entry(run, job=None):
    run_id = run.get("id")
    run_attempt = (
        (job or {}).get("run_attempt")
        or run.get("run_attempt")
        or run.get("run_number")
    )
    job_id = (job or {}).get("id")
    dedupe_key = (
        f"actions:{run_id}:{job_id}:{run_attempt}"
        if job_id is not None
        else f"actions:{run_id}:run"
    )
    return {
        "kind": "github_actions_job",
        "source": "actions",
        "workflow_run_id": run_id,
        "workflow_name": run.get("name"),
        "workflow_status": run.get("status"),
        "workflow_conclusion": run.get("conclusion"),
        "workflow_run_attempt": run_attempt,
        "job_id": job_id,
        "job_name": (job or {}).get("name"),
        "job_status": (job or {}).get("status"),
        "job_conclusion": (job or {}).get("conclusion"),
        "html_url": (job or {}).get("html_url") or run.get("html_url"),
        "failed_steps": failed_action_steps(job or {}),
        "dedupe_key": dedupe_key,
    }


limitations = []
supplemental_limitations = []
actions_failures = []
actions_failure_dedupe_keys = set()
if len(expected_head_sha_lower) < 40:
    head_payload, head_limitation = gh_pr_head_oid()
    if head_limitation:
        limitations.append(head_limitation)
    current_head_sha = str(head_payload.get("headRefOid") or "").lower()
    if (
        len(current_head_sha) == 40
        and all(char in "0123456789abcdef" for char in current_head_sha)
        and current_head_sha.startswith(expected_head_sha_lower)
    ):
        expected_head_sha = current_head_sha
        expected_head_sha_lower = current_head_sha
    else:
        limitations.append(
            {
                "code": "pr_head_sha_resolution_failed",
                "source": "gh_pr_view",
                "severity": "blocking",
                "message": "abbreviated PR head SHA could not be resolved to the current full head SHA",
            }
        )

actions_runs_payload, actions_limitation = gh_api(
    f"repos/{repo}/actions/runs?head_sha={expected_head_sha}"
)
actions_available = actions_limitation is None
if actions_limitation:
    limitations.append(actions_limitation)
    actions_runs_payload = {}
workflow_runs = as_list(actions_runs_payload or {}, "workflow_runs")
action_run_counts = {
    "success": 0,
    "neutral": 0,
    "skipped": 0,
    "failed": 0,
    "running": 0,
    "pending": 0,
    "unknown": 0,
}
action_job_counts = {
    "success": 0,
    "neutral": 0,
    "skipped": 0,
    "failed": 0,
    "running": 0,
    "pending": 0,
    "unknown": 0,
}
sanitized_action_runs = []
sanitized_action_jobs = []
action_job_collection_successes = 0
action_job_collection_failures = 0
action_job_collection_skipped_green_runs = 0
for run in workflow_runs:
    run_head_sha = str(run.get("head_sha") or "")
    if run_head_sha and not sha_prefix_matches(run_head_sha, expected_head_sha_lower):
        action_run_counts["unknown"] += 1
        continue
    run_classification = normalize_actions_status(run)
    if run_classification in action_run_counts:
        action_run_counts[run_classification] += 1
    else:
        action_run_counts["unknown"] += 1
    run_id = run.get("id")
    sanitized_action_runs.append(
        {
            "id": run_id,
            "name": run.get("name"),
            "status": run.get("status"),
            "conclusion": run.get("conclusion"),
            "head_sha": run.get("head_sha"),
            "html_url": run.get("html_url"),
        }
    )
    if run_id is None:
        action_job_collection_failures += 1
        action_job_counts["unknown"] += 1
        limitations.append(
            {
                "code": "github_actions_jobs_unavailable",
                "source": "actions_collector",
                "capability": "actions_read",
                "severity": "blocking",
                "message": "GitHub Actions workflow run did not include an id, so jobs could not be collected",
            }
        )
        if run_classification == "failed":
            failure = actions_failure_entry(run)
            if failure["dedupe_key"] not in actions_failure_dedupe_keys:
                actions_failure_dedupe_keys.add(failure["dedupe_key"])
                actions_failures.append(failure)
        continue
    if (
        run_classification in {"success", "neutral", "skipped"}
        and action_job_collection_successes >= TERMINAL_GREEN_JOB_EXPANSION_CAP
    ):
        action_job_collection_skipped_green_runs += 1
        continue
    jobs_payload, job_limitation = gh_api(f"repos/{repo}/actions/runs/{run_id}/jobs")
    if job_limitation:
        action_job_collection_failures += 1
        limitations.append(job_limitation)
        if run_classification == "failed":
            failure = actions_failure_entry(run)
            if failure["dedupe_key"] not in actions_failure_dedupe_keys:
                actions_failure_dedupe_keys.add(failure["dedupe_key"])
                actions_failures.append(failure)
        continue
    run_failed_jobs = []
    jobs = (jobs_payload or {}).get("jobs") if isinstance(jobs_payload, dict) else None
    if not isinstance(jobs, list):
        action_job_collection_failures += 1
        action_job_counts["unknown"] += 1
        limitations.append(
            {
                "code": "github_actions_jobs_unavailable",
                "source": "actions_collector",
                "capability": "actions_read",
                "severity": "blocking",
                "message": "GitHub Actions jobs response did not include a jobs list",
            }
        )
        if run_classification == "failed":
            failure = actions_failure_entry(run)
            if failure["dedupe_key"] not in actions_failure_dedupe_keys:
                actions_failure_dedupe_keys.add(failure["dedupe_key"])
                actions_failures.append(failure)
        continue
    action_job_collection_successes += 1
    for job in jobs:
        job_classification = normalize_actions_status(job)
        if job_classification in action_job_counts:
            action_job_counts[job_classification] += 1
        else:
            action_job_counts["unknown"] += 1
        sanitized_action_jobs.append(
            {
                "id": job.get("id"),
                "run_id": job.get("run_id") or run_id,
                "name": job.get("name"),
                "status": job.get("status"),
                "conclusion": job.get("conclusion"),
                "html_url": job.get("html_url"),
            }
        )
        if job_classification == "failed":
            run_failed_jobs.append(job)
            failure = actions_failure_entry(run, job)
            if failure["dedupe_key"] not in actions_failure_dedupe_keys:
                actions_failure_dedupe_keys.add(failure["dedupe_key"])
                actions_failures.append(failure)
    if run_classification == "failed" and not run_failed_jobs:
        failure = actions_failure_entry(run)
        if failure["dedupe_key"] not in actions_failure_dedupe_keys:
            actions_failure_dedupe_keys.add(failure["dedupe_key"])
            actions_failures.append(failure)

if actions_available and not workflow_runs:
    limitations.append(
        {
            "code": "zero_actions_runs_non_success",
            "source": "actions_collector",
            "capability": "actions_read",
            "severity": "informational",
            "blocking": False,
            "message": "no GitHub Actions workflow runs were observed for the expected PR head SHA",
        }
    )

actions_jobs_collection = {
    "successful_runs": action_job_collection_successes,
    "failed_runs": action_job_collection_failures,
}
if action_job_collection_skipped_green_runs:
    actions_jobs_collection.update(
        {
            "mode": "bounded",
            "expanded_runs": action_job_collection_successes + action_job_collection_failures,
            "skipped_green_runs": action_job_collection_skipped_green_runs,
            "cap": TERMINAL_GREEN_JOB_EXPANSION_CAP,
        }
    )
actions_jobs_summary = {
    "total": len(sanitized_action_jobs),
    "counts": action_job_counts,
    "collection": actions_jobs_collection,
}
actions_summary = {
    "available": actions_available,
    "workflow_runs": {
        "total": len(sanitized_action_runs),
        "counts": action_run_counts,
    },
    "runs": sanitized_action_runs,
    "jobs": sanitized_action_jobs,
    "jobs_summary": actions_jobs_summary,
    "jobs_detail": sanitized_action_jobs,
}
actions_decisive_green = (
    actions_available
    and actions_summary["workflow_runs"]["total"] > 0
    and (
        action_job_collection_successes + action_job_collection_skipped_green_runs
        == actions_summary["workflow_runs"]["total"]
    )
    and action_job_collection_failures == 0
    and not (
        action_run_counts["failed"]
        or action_run_counts["running"]
        or action_run_counts["pending"]
        or action_run_counts["unknown"]
        or action_job_counts["failed"]
        or action_job_counts["running"]
        or action_job_counts["pending"]
        or action_job_counts["unknown"]
    )
)
actions_decisive_non_terminal = (
    actions_available
    and actions_summary["workflow_runs"]["total"] > 0
    and (
        action_job_collection_successes + action_job_collection_skipped_green_runs
        == actions_summary["workflow_runs"]["total"]
    )
    and action_job_collection_failures == 0
    and not (
        action_run_counts["failed"]
        or action_run_counts["unknown"]
        or action_job_counts["failed"]
        or action_job_counts["unknown"]
    )
    and bool(
        action_run_counts["running"]
        or action_run_counts["pending"]
        or action_job_counts["running"]
        or action_job_counts["pending"]
    )
)
actions_decisive_failed = (
    actions_available
    and actions_summary["workflow_runs"]["total"] > 0
    and (
        action_job_collection_successes + action_job_collection_skipped_green_runs
        == actions_summary["workflow_runs"]["total"]
    )
    and action_job_collection_failures == 0
    and not (action_run_counts["unknown"] or action_job_counts["unknown"])
    and bool(action_run_counts["failed"] or action_job_counts["failed"])
)
check_runs_payload, limitation = gh_api(f"repos/{repo}/commits/{expected_head_sha}/check-runs")
if limitation:
    supplemental_limitations.append(limitation)
    check_runs_payload = {}
statuses_payload, limitation = gh_api(f"repos/{repo}/commits/{expected_head_sha}/status")
if limitation:
    supplemental_limitations.append(limitation)
    statuses_payload = {}
pr_view_payload, limitation = gh_pr_view()
if limitation:
    supplemental_limitations.append(limitation)

if (
    actions_decisive_green or actions_decisive_non_terminal or actions_decisive_failed
) and supplemental_limitations:
    limitations.append(
        {
            "code": "ci_coverage_limited_to_github_actions",
            "source": "actions_collector",
            "severity": "informational",
            "blocking": False,
            "message": "GitHub Actions evidence determines CI state; supplemental check/status rollup coverage was unavailable",
            "supplemental_unavailable": [
                {
                    "code": item.get("code"),
                    "capability": item.get("capability"),
                    "source": item.get("source"),
                    "status": item.get("status"),
                    "secret_redacted": item.get("secret_redacted"),
                    "stderr_sha256": item.get("stderr_sha256"),
                    "exit_code": item.get("exit_code"),
                }
                for item in supplemental_limitations
            ],
        }
    )
else:
    limitations.extend(supplemental_limitations)

check_runs = as_list(check_runs_payload, "check_runs")
statuses = as_list(statuses_payload, "statuses")
aggregate_status_state = (
    str(statuses_payload.get("state") or "").lower()
    if isinstance(statuses_payload, dict)
    else ""
)
aggregate_status_classification = normalize_status_state({"state": aggregate_status_state})
aggregate_status_pending_backstop = aggregate_status_classification == "pending" and bool(statuses)
aggregate_status_failed_backstop = aggregate_status_classification == "failed" and bool(statuses)
status_check_rollup = as_list(pr_view_payload, "statusCheckRollup")
merge_state_status = str(pr_view_payload.get("mergeStateStatus") or "").upper()

check_counts = {
    "total": len(check_runs),
    "success": 0,
    "skipped": 0,
    "neutral": 0,
    "failed": 0,
    "running": 0,
    "pending": 0,
    "other": 0,
    "stale": 0,
}
status_counts = {
    "total": len(statuses),
    "aggregate_state": aggregate_status_state or None,
    "success": 0,
    "failure": 0,
    "pending": 0,
    "error": 0,
    "other": 0,
}

failed_checks = []
stale_checks = []
for check in check_runs:
    check_head_sha = str(check.get("head_sha") or "")
    if check_head_sha and not sha_prefix_matches(check_head_sha, expected_head_sha_lower):
        check_counts["stale"] += 1
        stale_checks.append(check)
        continue
    classification = normalize_check_status(check)
    if classification == "failed":
        check_counts["failed"] += 1
        failed_checks.append(check)
    elif classification == "running":
        check_counts["running"] += 1
    elif classification == "pending":
        check_counts["pending"] += 1
    elif classification in {"success", "skipped", "neutral"}:
        check_counts[classification] += 1
    else:
        check_counts["other"] += 1

for status in statuses:
    classification = normalize_status_state(status)
    if classification == "failed":
        state = str(status.get("state") or "").lower()
        if state == "error":
            status_counts["error"] += 1
        else:
            status_counts["failure"] += 1
    elif classification == "pending":
        status_counts["pending"] += 1
    elif classification == "success":
        status_counts["success"] += 1
    else:
        status_counts["other"] += 1

if stale_checks:
    limitations.append(
        {
            "code": "stale_head_check",
            "source": "check_runs",
            "severity": "blocking",
            "message": "check run head SHA did not match expected head SHA",
            "count": len(stale_checks),
        }
    )

required_check_state = {
    "available": limitation is None,
    "merge_state_status": merge_state_status or None,
    "status_check_rollup_total": len(status_check_rollup),
    "status_check_rollup_states": [],
}
for item in status_check_rollup:
    state = str(item.get("state") or item.get("status") or "").upper()
    conclusion = str(item.get("conclusion") or "").upper()
    required_check_state["status_check_rollup_states"].append(
        {
            "name": item.get("name") or item.get("context"),
            "state": state or None,
            "conclusion": conclusion or None,
        }
    )

required_check_rollup_pending = any(
    item.get("state") in {"EXPECTED", "PENDING", "QUEUED", "REQUESTED", "WAITING"}
    for item in required_check_state["status_check_rollup_states"]
)
required_check_rollup_running = any(
    item.get("state") in {"IN_PROGRESS", "RUNNING"}
    for item in required_check_state["status_check_rollup_states"]
)
required_check_rollup_failed = any(
    item.get("state") in {"FAILURE", "FAILED", "ERROR", "CANCELLED"}
    or item.get("conclusion")
    in {
        "FAILURE",
        "ERROR",
        "CANCELLED",
        "TIMED_OUT",
        "ACTION_REQUIRED",
        "STARTUP_FAILURE",
        "STALE",
    }
    for item in required_check_state["status_check_rollup_states"]
)

failures = []
failures.extend(actions_failures)
for status in statuses:
    if normalize_status_state(status) == "failed":
        failures.append(
            {
                "kind": "commit_status",
                "context": status.get("context"),
                "status": status.get("state"),
                "description": status.get("description"),
                "target_url": status.get("target_url"),
            }
        )
if aggregate_status_failed_backstop and not (
    status_counts["failure"] or status_counts["error"]
):
    failures.append(
        {
            "kind": "commit_status_aggregate",
            "state": aggregate_status_state,
            "description": "combined commit status aggregate state was non-success",
        }
    )
for item in required_check_state["status_check_rollup_states"]:
    if item.get("state") in {"FAILURE", "FAILED", "ERROR", "CANCELLED"} or item.get(
        "conclusion"
    ) in {
        "FAILURE",
        "ERROR",
        "CANCELLED",
        "TIMED_OUT",
        "ACTION_REQUIRED",
        "STARTUP_FAILURE",
        "STALE",
    }:
        failures.append(
            {
                "kind": "status_check_rollup",
                "name": item.get("name"),
                "state": item.get("state"),
                "conclusion": item.get("conclusion"),
            }
        )

for check in failed_checks:
    workflow_run = check.get("workflow_run") if isinstance(check.get("workflow_run"), dict) else {}
    workflow_run_id = workflow_run.get("id")
    run_attempt = workflow_run.get("run_attempt")
    if workflow_run_id is None:
        failures.append(check_run_failure_fallback(check, "workflow_job_steps_unavailable"))
        continue

    jobs_payload, job_limitation = gh_api(f"repos/{repo}/actions/runs/{workflow_run_id}/jobs")
    jobs = as_list(jobs_payload or {}, "jobs")
    matching_failed_jobs = [
        job
        for job in jobs
        if job_matches_check(job, check.get("id"))
        and str(job.get("conclusion") or "").lower()
        in {"failure", "error", "cancelled", "timed_out", "action_required", "startup_failure", "stale"}
    ]
    if job_limitation or not matching_failed_jobs:
        failures.append(check_run_failure_fallback(check, "workflow_job_steps_unavailable"))
        if job_limitation:
            limitations.append(job_limitation)
        continue

    for job in matching_failed_jobs:
        run = {
            "id": workflow_run_id,
            "run_attempt": run_attempt,
            "name": check.get("workflow_name"),
            "status": check.get("status"),
            "conclusion": check.get("conclusion"),
            "html_url": check.get("details_url"),
        }
        failure = actions_failure_entry(run, job)
        if failure["dedupe_key"] not in actions_failure_dedupe_keys:
            actions_failure_dedupe_keys.add(failure["dedupe_key"])
            failures.append(failure)

required_checks_missing_or_pending = (
    merge_state_status == "BLOCKED"
    and required_check_rollup_pending
    and not (
        check_counts["failed"]
        or status_counts["failure"]
        or status_counts["error"]
        or aggregate_status_failed_backstop
        or required_check_rollup_failed
        or check_counts["stale"]
    )
    and not (
        check_counts["running"]
        or check_counts["pending"]
        or status_counts["pending"]
        or aggregate_status_pending_backstop
        or required_check_rollup_running
    )
)
merge_state_blocking = (
    bool(merge_state_status)
    and merge_state_status not in {"CLEAN", "HAS_HOOKS", "UNKNOWN"}
    and not required_checks_missing_or_pending
    and not (
        check_counts["failed"]
        or status_counts["failure"]
        or status_counts["error"]
        or aggregate_status_failed_backstop
        or required_check_rollup_failed
        or check_counts["stale"]
    )
    and not (
        check_counts["running"]
        or check_counts["pending"]
        or status_counts["pending"]
        or aggregate_status_pending_backstop
        or required_check_rollup_running
        or required_check_rollup_pending
    )
)
merge_state_unknown = merge_state_status == "UNKNOWN"

if required_checks_missing_or_pending:
    limitations.append(
        {
            "code": "required_checks_missing_or_pending",
            "source": "gh_pr_view.mergeStateStatus",
            "severity": "blocking",
            "message": "PR merge state indicates required checks are not yet satisfied",
            "merge_state_status": merge_state_status,
        }
    )
elif merge_state_blocking:
    limitations.append(
        {
            "code": "pr_merge_state_blocking",
            "source": "gh_pr_view.mergeStateStatus",
            "severity": "blocking",
            "message": "PR merge state requires human or branch action before merge",
            "merge_state_status": merge_state_status,
        }
    )

actions_primary_unavailable = any(
    item.get("capability") == "actions_read" and item.get("severity") == "blocking"
    for item in limitations
) and not actions_available
head_sha_resolution_failed = any(
    item.get("code") == "pr_head_sha_resolution_failed"
    and item.get("severity") == "blocking"
    for item in limitations
)
actions_zero_runs = actions_available and actions_summary["workflow_runs"]["total"] == 0
actions_failed = bool(action_run_counts["failed"] or action_job_counts["failed"])
actions_running = bool(action_run_counts["running"] or action_job_counts["running"])
actions_pending = bool(action_run_counts["pending"] or action_job_counts["pending"])
actions_unknown = bool(action_run_counts["unknown"] or action_job_counts["unknown"])
actions_jobs_unavailable = actions_available and action_job_collection_failures > 0

if actions_primary_unavailable or head_sha_resolution_failed:
    ci_status = "unknown"
elif actions_failed or (
    check_counts["failed"]
    or status_counts["failure"]
    or status_counts["error"]
    or aggregate_status_failed_backstop
    or required_check_rollup_failed
    or check_counts["stale"]
):
    ci_status = "failed"
elif actions_running or check_counts["running"] or required_check_rollup_running:
    ci_status = "running"
elif (
    actions_pending
    or check_counts["pending"]
    or status_counts["pending"]
    or aggregate_status_pending_backstop
    or required_check_rollup_pending
    or required_checks_missing_or_pending
    or merge_state_unknown
):
    ci_status = "pending"
elif actions_unknown or actions_jobs_unavailable:
    ci_status = "unknown"
elif actions_decisive_green and not (
    check_counts["failed"]
    or status_counts["failure"]
    or status_counts["error"]
    or aggregate_status_failed_backstop
    or required_check_rollup_failed
    or check_counts["stale"]
    or check_counts["running"]
    or check_counts["pending"]
    or status_counts["pending"]
    or aggregate_status_pending_backstop
    or required_check_rollup_running
    or required_check_rollup_pending
    or required_checks_missing_or_pending
    or merge_state_unknown
    or merge_state_blocking
    or check_counts["other"]
    or status_counts["other"]
):
    ci_status = "passed"
elif any(
    item.get("code") == "github_token_permission_denied"
    and is_blocking_limitation(item)
    for item in limitations
):
    ci_status = "unknown"
elif limitations and any(is_blocking_limitation(item) for item in limitations):
    ci_status = "unknown"
elif merge_state_blocking or (
    not required_check_state["available"] and (check_counts["total"] or status_counts["total"])
):
    ci_status = "unknown"
elif check_counts["total"] == 0 and status_counts["total"] == 0:
    ci_status = "none"
    limitations.append(
        {
            "code": "zero_checks_s03_non_success",
            "source": "ci_collector",
            "severity": "blocking",
            "message": "no check runs or commit statuses were observed; S03 keeps this non-success until S05 grace/deadline handling",
        }
    )
elif check_counts["other"] or status_counts["other"]:
    ci_status = "unknown"
else:
    ci_status = "passed"

sanitized_checks = []
for check in check_runs:
    sanitized_checks.append(
        {
            "id": check.get("id"),
            "name": check.get("name"),
            "head_sha": check.get("head_sha"),
            "status": check.get("status"),
            "conclusion": check.get("conclusion"),
            "html_url": check.get("html_url"),
            "details_url": check.get("details_url"),
            "workflow_name": check.get("workflow_name"),
            "workflow_run_id": (check.get("workflow_run") or {}).get("id")
            if isinstance(check.get("workflow_run"), dict)
            else None,
        }
    )

sanitized_statuses = []
for status in statuses:
    sanitized_statuses.append(
        {
            "context": status.get("context"),
            "state": status.get("state"),
            "target_url": status.get("target_url"),
            "description": status.get("description"),
        }
    )

fingerprint_source = {
    "head_sha": expected_head_sha,
    "ci_status": ci_status,
    "actions": {
        "available": actions_summary.get("available"),
        "workflow_runs": actions_summary.get("workflow_runs"),
        "jobs_summary": actions_summary.get("jobs_summary"),
        "runs": [
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "status": item.get("status"),
                "conclusion": item.get("conclusion"),
                "head_sha": item.get("head_sha"),
            }
            for item in sanitized_action_runs
        ],
        "jobs": [
            {
                "id": item.get("id"),
                "run_id": item.get("run_id"),
                "name": item.get("name"),
                "status": item.get("status"),
                "conclusion": item.get("conclusion"),
            }
            for item in sanitized_action_jobs
        ],
        "failures": [
            {
                "kind": item.get("kind"),
                "source": item.get("source"),
                "workflow_run_id": item.get("workflow_run_id"),
                "workflow_name": item.get("workflow_name"),
                "workflow_status": item.get("workflow_status"),
                "workflow_conclusion": item.get("workflow_conclusion"),
                "workflow_run_attempt": item.get("workflow_run_attempt"),
                "job_id": item.get("job_id"),
                "job_name": item.get("job_name"),
                "job_status": item.get("job_status"),
                "job_conclusion": item.get("job_conclusion"),
                "failed_steps": item.get("failed_steps"),
                "dedupe_key": item.get("dedupe_key"),
            }
            for item in actions_failures
            if item.get("source") == "actions"
        ],
    },
    "check_runs": [
        {
            "id": item.get("id"),
            "name": item.get("name"),
            "head_sha": item.get("head_sha"),
            "status": item.get("status"),
            "conclusion": item.get("conclusion"),
        }
        for item in sanitized_checks
    ],
    "statuses": [
        {
            "context": item.get("context"),
            "state": item.get("state"),
        }
        for item in sanitized_statuses
    ],
    "limitations": [item.get("code") for item in limitations],
    "required_check_state": required_check_state,
}

payload = {
    "script": "fetch_pr_checks_snapshot.sh",
    "status": ci_status,
    "observed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "repo": repo,
    "pr": pr,
    "expected_head_sha": expected_head_sha,
    "ci": {
        "status": ci_status,
        "progress_status": ci_status,
        "check_runs": check_counts,
        "commit_statuses": status_counts,
        "actions": actions_summary,
        "checks": sanitized_checks,
        "statuses": sanitized_statuses,
        "failures": failures,
        "collector": "s03",
        "required_check_state": required_check_state,
    },
    "limitations": limitations,
    "fingerprint": hashlib.sha256(
        json.dumps(fingerprint_source, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest(),
}
print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
