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

OBS_SCRIPT="fetch_pr_observation_snapshot.sh" \
OBS_REPO="$repo" \
OBS_PR="$pr" \
OBS_HEAD_SHA="$head_sha" \
OBS_CURRENT_HEAD_SHA="$current_head_sha" \
OBS_TRIGGER_COMMENT_ID="$trigger_comment_id" \
OBS_TRIGGER_CREATED_AT="$trigger_created_at" \
OBS_BODY_MODE="$body_mode" \
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
normalized_status = "unknown"
recommended_next_action = "human_gate"

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
elif expected_head_sha and current_head_sha and current_head_sha.lower() != expected_head_sha.lower():
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
    limitations.append(
        {
            "code": "ci_review_collectors_pending",
            "source": "s02_contract",
            "severity": "blocking",
            "message": "CI and review collectors are intentionally stubbed until later implementation steps",
        }
    )

fingerprint_source = {
    "repo": repo,
    "pr": pr,
    "expected_head_sha": expected_head_sha,
    "current_head_sha": current_head_sha,
    "normalized_status": normalized_status,
    "limitations": [item["code"] for item in limitations],
}
fingerprint = hashlib.sha256(
    json.dumps(fingerprint_source, sort_keys=True, separators=(",", ":")).encode()
).hexdigest()

trigger_comment_id = os.environ["OBS_TRIGGER_COMMENT_ID"] or None
trigger_created_at = os.environ["OBS_TRIGGER_CREATED_AT"] or None
trigger = {
    "source": "explicit" if trigger_comment_id or trigger_created_at else "none",
    "comment_id": int(trigger_comment_id) if trigger_comment_id else None,
    "created_at": trigger_created_at,
}

payload = {
    "script": script,
    "status": normalized_status,
    "overall_status": normalized_status,
    "normalized_status": normalized_status,
    "observation_complete": False,
    "observed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "repo": repo,
    "pr": pr,
    "expected_head_sha": expected_head_sha,
    "current_head_sha": current_head_sha,
    "head_matches_expected": (
        None
        if expected_head_sha is None or current_head_sha is None
        else current_head_sha.lower() == expected_head_sha.lower()
    ),
    "fingerprint": fingerprint,
    "summary": summary,
    "limitations": limitations,
    "recommended_next_action": recommended_next_action,
    "ci": {
        "status": "unknown",
        "checks": [],
        "failures": [],
        "collector": "pending_s03",
    },
    "review": {
        "status": "unknown",
        "signals": [],
        "codex_authored": [],
        "collector": "pending_s04",
    },
    "trigger": trigger,
    "body_mode": body_mode,
    "artifacts": {},
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
