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
if [ "$gh_exit" -eq 0 ] && [ -n "$current_head_sha" ]; then
  checks_head_sha="${head_sha:-$current_head_sha}"
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
    set -e
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
python3 - <<'PY' >"$tmp_dir/result.json"
import hashlib
import json
import os
from datetime import datetime, timezone

script = os.environ["OBS_SCRIPT"]
repo = os.environ["OBS_REPO"]
pr = int(os.environ["OBS_PR"])
expected_head_sha = os.environ["OBS_HEAD_SHA"] or None
current_head_sha = os.environ["OBS_CURRENT_HEAD_SHA"] or None
body_mode = os.environ["OBS_BODY_MODE"]
gh_exit = int(os.environ["OBS_GH_EXIT"])
metadata = {}
try:
    metadata = json.loads(os.environ["OBS_METADATA_JSON"])
except json.JSONDecodeError:
    metadata = {}

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
head_matches_expected = (
    None
    if expected_head_sha is None or current_head_sha is None
    else (
        current_head_sha.lower().startswith(expected_head_sha.lower())
        or expected_head_sha.lower().startswith(current_head_sha.lower())
    )
)
normalized_status = "unknown"
recommended_next_action = "human_gate"
observation_complete = False


def has_blocking_limitation(ignored_codes=None):
    ignored_codes = ignored_codes or set()
    return any(
        item.get("severity") == "blocking"
        and item.get("code") not in ignored_codes
        for item in limitations
        if isinstance(item, dict)
    )


def classify_snapshot():
    ci_status = ci_payload.get("status") or summary.get("ci") or "unknown"
    review_status = review_payload.get("status") or summary.get("review") or "unknown"
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
            return "unknown", "human_gate", False
        return ci_status, "wait", False
    if has_blocking_limitation():
        return "unknown", "human_gate", False
    if ci_status != "passed":
        return "unknown", "human_gate", False
    if review_status in {"none", "approved"}:
        return "passed", "merge_prepared", True
    if review_status in {"requested", "commented", "changes_requested", "unresolved"}:
        return "human_gate", "address_review_feedback", True
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
        {
            "code": "pr_metadata_collection_failed",
            "source": "gh_pr_view",
            "severity": "blocking",
            "message": "fixed read-only PR metadata collection failed",
            "exit_code": gh_exit,
            "stderr_sha256": hashlib.sha256(stderr_text.encode()).hexdigest(),
        }
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
    expected_head_sha
    and current_head_sha
    and not (
        current_head_sha.lower().startswith(expected_head_sha.lower())
        or expected_head_sha.lower().startswith(current_head_sha.lower())
    )
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
