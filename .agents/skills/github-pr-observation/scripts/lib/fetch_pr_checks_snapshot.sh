#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
usage: fetch_pr_checks_snapshot.sh --repo OWNER/REPO --pr NUMBER --head-sha SHA

Collects check runs, commit statuses, and fixed GitHub Actions failure detail
for the expected PR head SHA. The script accepts only this fixed read-only
contract and does not accept caller-provided gh api arguments.
USAGE
}

fail_usage() {
  usage
  exit 64
}

repo=""
pr=""
head_sha=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --repo)
      [ "$#" -ge 2 ] || fail_usage
      repo="$2"
      shift 2
      ;;
    --pr)
      [ "$#" -ge 2 ] || fail_usage
      pr="$2"
      shift 2
      ;;
    --head-sha)
      [ "$#" -ge 2 ] || fail_usage
      head_sha="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail_usage
      ;;
  esac
done

if ! [[ "$repo" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]; then
  fail_usage
fi
if ! [[ "$pr" =~ ^[1-9][0-9]*$ ]]; then
  fail_usage
fi
if ! [[ "$head_sha" =~ ^[0-9A-Fa-f]{7,64}$ ]]; then
  fail_usage
fi

OBS_REPO="$repo" \
OBS_PR="$pr" \
OBS_HEAD_SHA="$head_sha" \
python3 - <<'PY'
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone

repo = os.environ["OBS_REPO"]
pr = int(os.environ["OBS_PR"])
expected_head_sha = os.environ["OBS_HEAD_SHA"]
expected_head_sha_lower = expected_head_sha.lower()


def token_source():
    return "GH_TOKEN" if os.environ.get("GH_TOKEN") else "gh_saved_auth"


def classify_github_stderr(stderr):
    lowered = (stderr or "").lower()
    if "resource not accessible by personal access token" in lowered or "permission denied" in lowered:
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
    if api.endswith("/check-runs"):
        return "check_runs_read"
    if api.endswith("/status"):
        return "commit_statuses_read"
    if "/actions/runs/" in api and api.endswith("/jobs"):
        return "actions_read"
    return "unknown"


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
        "source": source,
        "severity": default_severity,
        "message": default_message,
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
        return None, {
            "code": "github_api_schema_unavailable",
            "source": path,
            "severity": "blocking",
            "message": "fixed read-only GitHub API returned non-JSON output",
        }


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


limitations = []
check_runs_payload, limitation = gh_api(f"repos/{repo}/commits/{expected_head_sha}/check-runs")
if limitation:
    limitations.append(limitation)
    check_runs_payload = {}
statuses_payload, limitation = gh_api(f"repos/{repo}/commits/{expected_head_sha}/status")
if limitation:
    limitations.append(limitation)
    statuses_payload = {}
pr_view_payload, limitation = gh_pr_view()
if limitation:
    limitations.append(limitation)

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
    item.get("state") in {"EXPECTED", "IN_PROGRESS", "PENDING", "QUEUED", "REQUESTED", "WAITING"}
    for item in required_check_state["status_check_rollup_states"]
)

failures = []
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
        steps = job.get("steps") if isinstance(job.get("steps"), list) else []
        failed_steps = [
            {
                "number": step.get("number"),
                "name": step.get("name"),
                "status": step.get("status"),
                "conclusion": step.get("conclusion"),
            }
            for step in steps
            if str(step.get("conclusion") or "").lower()
            in {"failure", "error", "cancelled", "timed_out", "action_required", "startup_failure", "stale"}
        ]
        failures.append(
            {
                "kind": "github_actions_job",
                "workflow_name": check.get("workflow_name"),
                "workflow_run_id": workflow_run_id,
                "workflow_run_attempt": run_attempt or job.get("run_attempt"),
                "job_name": job.get("name"),
                "job_id": job.get("id"),
                "check_run_id": check.get("id"),
                "status": job.get("status"),
                "conclusion": job.get("conclusion"),
                "failed_steps": failed_steps,
                "html_url": job.get("html_url"),
                "details_url": check.get("details_url"),
            }
        )

required_checks_missing_or_pending = (
    merge_state_status == "BLOCKED"
    and required_check_rollup_pending
    and not (
        check_counts["failed"]
        or status_counts["failure"]
        or status_counts["error"]
        or aggregate_status_failed_backstop
        or check_counts["stale"]
    )
    and not (
        check_counts["running"]
        or check_counts["pending"]
        or status_counts["pending"]
        or aggregate_status_pending_backstop
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
        or check_counts["stale"]
    )
    and not (
        check_counts["running"]
        or check_counts["pending"]
        or status_counts["pending"]
        or aggregate_status_pending_backstop
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

if any(item.get("code") == "github_token_permission_denied" for item in limitations):
    ci_status = "unknown"
elif (
    check_counts["failed"]
    or status_counts["failure"]
    or status_counts["error"]
    or aggregate_status_failed_backstop
    or check_counts["stale"]
):
    ci_status = "failed"
elif limitations and any(item.get("severity") == "blocking" and item.get("code", "").startswith("github_api") for item in limitations):
    ci_status = "unknown"
elif check_counts["running"]:
    ci_status = "running"
elif (
    check_counts["pending"]
    or status_counts["pending"]
    or aggregate_status_pending_backstop
    or required_checks_missing_or_pending
    or merge_state_unknown
):
    ci_status = "pending"
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
PY
