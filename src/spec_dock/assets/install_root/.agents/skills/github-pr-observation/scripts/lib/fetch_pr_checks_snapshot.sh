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
        return None, {
            "code": "github_api_collection_failed",
            "source": path,
            "severity": "blocking",
            "message": "fixed read-only GitHub API collection failed",
            "exit_code": completed.returncode,
            "stderr_sha256": hashlib.sha256(completed.stderr.encode()).hexdigest(),
        }
    try:
        return parse_gh_paginated_stdout(completed.stdout), None
    except json.JSONDecodeError:
        return None, {
            "code": "github_api_schema_unavailable",
            "source": path,
            "severity": "blocking",
            "message": "fixed read-only GitHub API returned non-JSON output",
        }


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

check_runs = as_list(check_runs_payload, "check_runs")
statuses = as_list(statuses_payload, "statuses")

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

if check_counts["failed"] or status_counts["failure"] or status_counts["error"] or check_counts["stale"]:
    ci_status = "failed"
elif limitations and any(item.get("severity") == "blocking" and item.get("code", "").startswith("github_api") for item in limitations):
    ci_status = "unknown"
elif check_counts["running"]:
    ci_status = "running"
elif check_counts["pending"] or status_counts["pending"]:
    ci_status = "pending"
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
    },
    "limitations": limitations,
    "fingerprint": hashlib.sha256(
        json.dumps(fingerprint_source, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest(),
}
print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
PY
