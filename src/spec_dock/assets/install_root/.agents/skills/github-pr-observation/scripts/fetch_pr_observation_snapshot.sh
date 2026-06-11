#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
usage: fetch_pr_observation_snapshot.sh --repo OWNER/REPO --pr NUMBER [options]

Options:
  --head-sha SHA
  --trigger-comment-id NUMBER
  --trigger-created-at ISO8601
  --body-mode none|trigger-window-truncated|trigger-window-full|out-only
  --out DIR

The script accepts only the fixed PR observation contract. It does not accept
caller-provided endpoints, methods, GraphQL queries, headers, bodies, jq
expressions, or raw gh arguments.
USAGE
}

fail_usage() {
  usage
  exit 64
}

repo=""
pr=""
head_sha=""
trigger_comment_id=""
trigger_created_at=""
body_mode="trigger-window-truncated"
out_dir=""

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
    --trigger-comment-id)
      [ "$#" -ge 2 ] || fail_usage
      trigger_comment_id="$2"
      shift 2
      ;;
    --trigger-created-at)
      [ "$#" -ge 2 ] || fail_usage
      trigger_created_at="$2"
      shift 2
      ;;
    --body-mode)
      [ "$#" -ge 2 ] || fail_usage
      body_mode="$2"
      shift 2
      ;;
    --out)
      [ "$#" -ge 2 ] || fail_usage
      out_dir="$2"
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
if [ -n "$head_sha" ] && ! [[ "$head_sha" =~ ^[0-9A-Fa-f]{7,64}$ ]]; then
  fail_usage
fi
if [ -n "$trigger_comment_id" ] && ! [[ "$trigger_comment_id" =~ ^[1-9][0-9]*$ ]]; then
  fail_usage
fi
if [ -n "$trigger_created_at" ] && ! [[ "$trigger_created_at" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(Z|[+-][0-9]{2}:[0-9]{2})?$ ]]; then
  fail_usage
fi
case "$body_mode" in
  none|trigger-window-truncated|trigger-window-full|out-only) ;;
  *) fail_usage ;;
esac
if [ -n "$out_dir" ] && [[ "$out_dir" == -* ]]; then
  fail_usage
fi

tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/pr-observation-snapshot.XXXXXX")"
cleanup() {
  rm -rf "$tmp_dir"
}
trap cleanup EXIT

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
checks_script="$script_dir/lib/fetch_pr_checks_snapshot.sh"
review_script="$script_dir/lib/fetch_pr_review_snapshot.sh"

gh_stdout="$tmp_dir/gh-pr-view.json"
gh_stderr="$tmp_dir/gh-pr-view.stderr"
set +e
gh pr view "$pr" --repo "$repo" --json headRefOid,url,state,isDraft,number >"$gh_stdout" 2>"$gh_stderr"
gh_exit=$?
set -e

metadata_json="{}"
current_head_sha=""
if [ "$gh_exit" -eq 0 ]; then
  metadata_json="$(cat "$gh_stdout")"
  current_head_sha="$(
    python3 - "$gh_stdout" <<'PY'
import json
import sys

try:
    payload = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception:
    payload = {}
print(payload.get("headRefOid") or "")
PY
  )"
fi

checks_stdout="$tmp_dir/checks.json"
checks_stderr="$tmp_dir/checks.stderr"
checks_exit=0
review_stdout="$tmp_dir/review.json"
review_stderr="$tmp_dir/review.stderr"
review_exit=0
final_gh_stdout="$tmp_dir/gh-pr-view-final.json"
final_gh_stderr="$tmp_dir/gh-pr-view-final.stderr"
final_gh_exit=0
final_metadata_json="{}"
final_current_head_sha=""
collection_head_sha=""
if [ "$gh_exit" -eq 0 ] && [ -n "$current_head_sha" ]; then
  checks_head_sha="${head_sha:-$current_head_sha}"
  collection_head_sha="$checks_head_sha"
  current_head_sha_lc="$(printf '%s' "$current_head_sha" | tr '[:upper:]' '[:lower:]')"
  head_sha_lc="$(printf '%s' "$head_sha" | tr '[:upper:]' '[:lower:]')"
  if [ -z "$head_sha" ] || [[ "$current_head_sha_lc" == "$head_sha_lc"* ]] || [[ "$head_sha_lc" == "$current_head_sha_lc"* ]]; then
    set +e
    "$checks_script" --repo "$repo" --pr "$pr" --head-sha "$checks_head_sha" >"$checks_stdout" 2>"$checks_stderr"
    checks_exit=$?
    review_args=(--repo "$repo" --pr "$pr" --head-sha "$checks_head_sha" --body-mode "$body_mode")
    if [ -n "$trigger_comment_id" ]; then
      review_args+=(--trigger-comment-id "$trigger_comment_id")
    fi
    if [ -n "$trigger_created_at" ]; then
      review_args+=(--trigger-created-at "$trigger_created_at")
    fi
    if [ -n "$out_dir" ]; then
      review_args+=(--out "$out_dir")
    fi
    "$review_script" "${review_args[@]}" >"$review_stdout" 2>"$review_stderr"
    review_exit=$?
    gh pr view "$pr" --repo "$repo" --json headRefOid,url,state,isDraft,number >"$final_gh_stdout" 2>"$final_gh_stderr"
    final_gh_exit=$?
    set -e
    if [ "$final_gh_exit" -eq 0 ]; then
      final_metadata_json="$(cat "$final_gh_stdout")"
      final_current_head_sha="$(
        python3 - "$final_gh_stdout" <<'PY'
import json
import sys

try:
    payload = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception:
    payload = {}
print(payload.get("headRefOid") or "")
PY
      )"
    fi
  else
    printf '{}\n' >"$checks_stdout"
    printf '{}\n' >"$review_stdout"
  fi
else
  printf '{}\n' >"$checks_stdout"
  printf '{}\n' >"$review_stdout"
fi

OBS_SCRIPT="fetch_pr_observation_snapshot.sh" \
OBS_REPO="$repo" \
OBS_PR="$pr" \
OBS_HEAD_SHA="$head_sha" \
OBS_CURRENT_HEAD_SHA="$current_head_sha" \
OBS_COLLECTION_HEAD_SHA="$collection_head_sha" \
OBS_CHECKS_EXIT="$checks_exit" \
OBS_CHECKS_JSON_PATH="$checks_stdout" \
OBS_CHECKS_STDERR_PATH="$checks_stderr" \
OBS_REVIEW_EXIT="$review_exit" \
OBS_REVIEW_JSON_PATH="$review_stdout" \
OBS_REVIEW_STDERR_PATH="$review_stderr" \
OBS_TRIGGER_COMMENT_ID="$trigger_comment_id" \
OBS_TRIGGER_CREATED_AT="$trigger_created_at" \
OBS_BODY_MODE="$body_mode" \
OBS_OUT_DIR="$out_dir" \
OBS_GH_EXIT="$gh_exit" \
OBS_GH_STDERR_PATH="$gh_stderr" \
OBS_METADATA_JSON="$metadata_json" \
OBS_FINAL_GH_EXIT="$final_gh_exit" \
OBS_FINAL_GH_STDERR_PATH="$final_gh_stderr" \
OBS_FINAL_METADATA_JSON="$final_metadata_json" \
OBS_FINAL_CURRENT_HEAD_SHA="$final_current_head_sha" \
python3 - <<'PY' >"$tmp_dir/result.json"
import hashlib
import json
import os
from datetime import datetime, timezone

script = os.environ["OBS_SCRIPT"]
repo = os.environ["OBS_REPO"]
pr = int(os.environ["OBS_PR"])
provided_head_sha = os.environ["OBS_HEAD_SHA"] or None
collection_head_sha = os.environ["OBS_COLLECTION_HEAD_SHA"] or None
expected_head_sha = provided_head_sha or collection_head_sha
current_head_sha = os.environ["OBS_CURRENT_HEAD_SHA"] or None
body_mode = os.environ["OBS_BODY_MODE"]
gh_exit = int(os.environ["OBS_GH_EXIT"])
metadata = {}
try:
    metadata = json.loads(os.environ["OBS_METADATA_JSON"])
except json.JSONDecodeError:
    metadata = {}
final_gh_exit = int(os.environ["OBS_FINAL_GH_EXIT"])
final_metadata = {}
try:
    final_metadata = json.loads(os.environ["OBS_FINAL_METADATA_JSON"])
except json.JSONDecodeError:
    final_metadata = {}
final_current_head_sha = os.environ["OBS_FINAL_CURRENT_HEAD_SHA"] or None

limitations = []
summary = {
    "ci": "unknown",
    "review": "unknown",
    "head": "unknown",
}
ci_payload = {
    "status": "unknown",
    "checks": [],
    "failures": [],
    "collector": "pending_s03",
}
review_payload = {
    "status": "unknown",
    "signals": [],
    "codex_authored": [],
    "collector": "pending_s04",
}
review_wrapper_payload = {}
normalized_status = "unknown"
recommended_next_action = "human_gate"
observation_complete = False


def sha_matches(left, right):
    return bool(
        left
        and right
        and (
            left.lower().startswith(right.lower())
            or right.lower().startswith(left.lower())
        )
    )


head_matches_expected = (
    None
    if expected_head_sha is None or current_head_sha is None
    else sha_matches(current_head_sha, expected_head_sha)
)


def has_blocking_limitation(ignored_codes=None):
    ignored_codes = ignored_codes or set()
    return any(
        item.get("severity") == "blocking"
        and item.get("code") not in ignored_codes
        for item in limitations
        if isinstance(item, dict)
    )


def has_permission_limitation():
    return any(
        item.get("code") == "github_token_permission_denied"
        for item in limitations
        if isinstance(item, dict)
    )


def token_source():
    return "GH_TOKEN" if os.environ.get("GH_TOKEN") else "gh_saved_auth"


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


def pr_metadata_failure_limitation(*, exit_code, stderr, default_code, default_message):
    classification = classify_github_stderr(stderr)
    stderr_sha256 = hashlib.sha256((stderr or "").encode()).hexdigest()
    base = {
        "capability": "pull_request_read",
        "api": "gh pr view --json headRefOid,url,state,isDraft,number",
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


def classify_snapshot():
    ci_status = ci_payload.get("status") or summary.get("ci") or "unknown"
    review_status = review_payload.get("status") or summary.get("review") or "unknown"
    codex_review = (
        review_wrapper_payload.get("codex_review")
        if isinstance(review_wrapper_payload, dict) and isinstance(review_wrapper_payload.get("codex_review"), dict)
        else (
            review_payload.get("codex_review")
            if isinstance(review_payload, dict) and isinstance(review_payload.get("codex_review"), dict)
            else {}
        )
    )
    codex_lifecycle = codex_review.get("lifecycle") if isinstance(codex_review.get("lifecycle"), dict) else {}
    completion_signal = codex_lifecycle.get("completion_signal")
    if head_matches_expected is False or normalized_status == "stale_head":
        return "stale_head", "rerun_for_current_head", False
    if metadata.get("isDraft") is True:
        return "human_gate", "mark_pr_ready_for_review", False
    if metadata.get("state") and str(metadata.get("state") or "").upper() != "OPEN":
        return "human_gate", "reopen_or_use_open_pr", False
    if ci_status == "failed":
        return "failed", "fix_ci", False
    if ci_status in {"pending", "running", "none"}:
        if has_blocking_limitation(ignored_codes={"required_checks_missing_or_pending"}):
            if has_permission_limitation():
                return "unknown", "fix_github_token_permissions", False
            return "unknown", "human_gate", False
        return ci_status, "wait", False
    if has_permission_limitation():
        return "unknown", "fix_github_token_permissions", False
    if has_blocking_limitation():
        return "unknown", "human_gate", False
    if ci_status != "passed":
        return "unknown", "human_gate", False
    if completion_signal == "fallback_issue_comment":
        return "human_gate", "wait_or_resume", False
    if review_status in {"requested", "commented", "changes_requested", "unresolved"}:
        return "human_gate", "address_review_feedback", True
    if completion_signal != "submitted_pull_request_review":
        return "pending", "wait", False
    if review_status in {"none", "approved"}:
        return "passed", "merge_prepared", True
    return "unknown", "human_gate", False

if gh_exit != 0:
    stderr_text = ""
    stderr_path = os.environ["OBS_GH_STDERR_PATH"]
    if stderr_path:
        try:
            stderr_text = open(stderr_path, encoding="utf-8", errors="replace").read()
        except OSError:
            stderr_text = ""
    limitations.append(
        pr_metadata_failure_limitation(
            exit_code=gh_exit,
            stderr=stderr_text,
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
elif (
    provided_head_sha
    and current_head_sha
    and not sha_matches(current_head_sha, provided_head_sha)
):
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
        stderr_text = ""
        stderr_path = os.environ["OBS_FINAL_GH_STDERR_PATH"]
        if stderr_path:
            try:
                stderr_text = open(stderr_path, encoding="utf-8", errors="replace").read()
            except OSError:
                stderr_text = ""
        limitations.append(
            pr_metadata_failure_limitation(
                exit_code=final_gh_exit,
                stderr=stderr_text,
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
        head_matches_expected = (
            None
            if expected_head_sha is None
            else sha_matches(current_head_sha, expected_head_sha)
        )
    if summary["head"] != "stale":
        summary["head"] = "matched" if expected_head_sha else "observed"
    checks_exit = int(os.environ["OBS_CHECKS_EXIT"])
    checks_path = os.environ["OBS_CHECKS_JSON_PATH"]
    checks_payload = {}
    try:
        checks_payload = json.load(open(checks_path, encoding="utf-8"))
    except Exception:
        checks_payload = {}
    if checks_exit == 0 and isinstance(checks_payload.get("ci"), dict):
        ci_payload = checks_payload["ci"]
        summary["ci"] = ci_payload.get("status") or "unknown"
        limitations.extend(checks_payload.get("limitations", []))
    else:
        stderr_text = ""
        stderr_path = os.environ["OBS_CHECKS_STDERR_PATH"]
        if stderr_path:
            try:
                stderr_text = open(stderr_path, encoding="utf-8", errors="replace").read()
            except OSError:
                stderr_text = ""
        limitations.append(
            {
                "code": "ci_collection_failed",
                "source": "fetch_pr_checks_snapshot.sh",
                "severity": "blocking",
                "message": "fixed CI/check/status collector failed",
                "exit_code": checks_exit,
                "stderr_sha256": hashlib.sha256(stderr_text.encode()).hexdigest(),
            }
        )
    review_exit = int(os.environ["OBS_REVIEW_EXIT"])
    review_path = os.environ["OBS_REVIEW_JSON_PATH"]
    review_wrapper_payload = {}
    try:
        review_wrapper_payload = json.load(open(review_path, encoding="utf-8"))
    except Exception:
        review_wrapper_payload = {}
    if review_exit == 0 and isinstance(review_wrapper_payload.get("review"), dict):
        review_payload = review_wrapper_payload["review"]
        summary["review"] = review_payload.get("status") or "unknown"
        limitations.extend(review_wrapper_payload.get("limitations", []))
    else:
        stderr_text = ""
        stderr_path = os.environ["OBS_REVIEW_STDERR_PATH"]
        if stderr_path:
            try:
                stderr_text = open(stderr_path, encoding="utf-8", errors="replace").read()
            except OSError:
                stderr_text = ""
        limitations.append(
            {
                "code": "review_collection_failed",
                "source": "fetch_pr_review_snapshot.sh",
                "severity": "blocking",
                "message": "fixed review/comment/thread collector failed",
                "exit_code": review_exit,
                "stderr_sha256": hashlib.sha256(stderr_text.encode()).hexdigest(),
            }
        )

normalized_status, recommended_next_action, observation_complete = classify_snapshot()
review_collector_fingerprint = (
    review_wrapper_payload.get("fingerprint")
    if "review_wrapper_payload" in locals() and isinstance(review_wrapper_payload, dict)
    else None
)
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

fingerprint_source = {
    "repo": repo,
    "pr": pr,
    "expected_head_sha": expected_head_sha,
    "current_head_sha": current_head_sha,
    "normalized_status": normalized_status,
    "limitations": [item["code"] for item in limitations],
    "ci_status": ci_payload.get("status"),
    "ci_fingerprint": checks_payload.get("fingerprint") if "checks_payload" in locals() else None,
    "review_status": review_payload.get("status"),
    "review_fingerprint": review_collector_fingerprint,
}
fingerprint = hashlib.sha256(
    json.dumps(fingerprint_source, sort_keys=True, separators=(",", ":")).encode()
).hexdigest()

trigger_comment_id = os.environ["OBS_TRIGGER_COMMENT_ID"] or None
trigger_created_at = os.environ["OBS_TRIGGER_CREATED_AT"] or None
out_dir = os.environ["OBS_OUT_DIR"] or None
trigger = {
    "source": (
        review_wrapper_payload.get("trigger", {}).get("source")
        if isinstance(review_wrapper_payload.get("trigger"), dict)
        else ("explicit" if trigger_comment_id or trigger_created_at else "none")
    ),
    "comment_id": int(trigger_comment_id) if trigger_comment_id else None,
    "created_at": trigger_created_at,
}
if isinstance(review_wrapper_payload.get("trigger"), dict):
    trigger["comment_id"] = review_wrapper_payload["trigger"].get("comment_id")
    trigger["created_at"] = review_wrapper_payload["trigger"].get("created_at")

payload = {
    "script": script,
    "status": normalized_status,
    "overall_status": normalized_status,
    "normalized_status": normalized_status,
    "observation_complete": observation_complete,
    "observed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "repo": repo,
    "pr": pr,
    "expected_head_sha": expected_head_sha,
    "current_head_sha": current_head_sha,
    "head_matches_expected": head_matches_expected,
    "fingerprint": fingerprint,
    "summary": summary,
    "limitations": limitations,
    "recommended_next_action": recommended_next_action,
    "ci": {
        **ci_payload,
    },
    "review": review_payload,
    "codex_review": codex_review_payload,
    "trigger": trigger,
    "body_mode": body_mode,
    "artifacts": {
        "result_json": f"{out_dir}/result.json" if out_dir else None,
        "latest_json": f"{out_dir}/latest.json" if out_dir else None,
        "events_ndjson": f"{out_dir}/events.ndjson" if out_dir else None,
        "latest_delta_json": f"{out_dir}/latest_delta.json" if out_dir else None,
        "snapshots_dir": f"{out_dir}/snapshots" if out_dir else None,
    },
    "pr_metadata": metadata,
}
print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
PY

if [ -n "$out_dir" ]; then
  mkdir -p "$out_dir/raw"
  cp "$tmp_dir/result.json" "$out_dir/result.json"
  cp "$tmp_dir/result.json" "$out_dir/latest.json"
  printf '{}\n' >"$out_dir/latest_delta.json"
  printf '{"event":"snapshot","result":"stdout_json"}\n' >"$out_dir/events.ndjson"
  if [ -s "$gh_stdout" ]; then
    cp "$gh_stdout" "$out_dir/raw/pr_view.json"
  fi
  if [ -s "$gh_stderr" ]; then
    cp "$gh_stderr" "$out_dir/raw/pr_view.stderr"
  fi
fi

cat "$tmp_dir/result.json"
