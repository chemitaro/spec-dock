#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
usage: wait_pr_observation.sh --repo OWNER/REPO --pr NUMBER --head-sha SHA [options]

Options:
  --timeout-seconds NUMBER
  --poll-interval-seconds NUMBER
  --quiet-seconds NUMBER
  --same-fingerprint-count NUMBER
  --zero-check-grace-polls NUMBER
  --trigger-comment-id NUMBER
  --trigger-created-at ISO8601
  --body-mode none|trigger-window-truncated|trigger-window-full|out-only
  --progress stderr-summary|none
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
timeout_seconds="1800"
poll_interval_seconds="30"
quiet_seconds="90"
same_fingerprint_count="2"
zero_check_grace_polls="2"
trigger_comment_id=""
trigger_created_at=""
body_mode="trigger-window-truncated"
progress="stderr-summary"
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
    --timeout-seconds)
      [ "$#" -ge 2 ] || fail_usage
      timeout_seconds="$2"
      shift 2
      ;;
    --poll-interval-seconds)
      [ "$#" -ge 2 ] || fail_usage
      poll_interval_seconds="$2"
      shift 2
      ;;
    --quiet-seconds)
      [ "$#" -ge 2 ] || fail_usage
      quiet_seconds="$2"
      shift 2
      ;;
    --same-fingerprint-count)
      [ "$#" -ge 2 ] || fail_usage
      same_fingerprint_count="$2"
      shift 2
      ;;
    --zero-check-grace-polls)
      [ "$#" -ge 2 ] || fail_usage
      zero_check_grace_polls="$2"
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
    --progress)
      [ "$#" -ge 2 ] || fail_usage
      progress="$2"
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

positive_int() {
  [[ "$1" =~ ^[1-9][0-9]*$ ]]
}

if ! [[ "$repo" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]; then
  fail_usage
fi
if ! [[ "$pr" =~ ^[1-9][0-9]*$ ]]; then
  fail_usage
fi
if ! [[ "$head_sha" =~ ^[0-9A-Fa-f]{7,64}$ ]]; then
  fail_usage
fi
if ! positive_int "$timeout_seconds"; then
  fail_usage
fi
if ! positive_int "$poll_interval_seconds"; then
  fail_usage
fi
if ! positive_int "$quiet_seconds"; then
  fail_usage
fi
if ! positive_int "$same_fingerprint_count"; then
  fail_usage
fi
if ! positive_int "$zero_check_grace_polls"; then
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
case "$progress" in
  stderr-summary|none) ;;
  *) fail_usage ;;
esac
if [ -n "$out_dir" ] && [[ "$out_dir" == -* ]]; then
  fail_usage
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
snapshot_script="$script_dir/fetch_pr_observation_snapshot.sh"
tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/pr-observation-wait.XXXXXX")"
cleanup() {
  rm -rf "$tmp_dir"
}
trap cleanup EXIT

snapshot_args=(
  --repo "$repo"
  --pr "$pr"
  --head-sha "$head_sha"
  --body-mode "$body_mode"
)
if [ -n "$trigger_comment_id" ]; then
  snapshot_args+=(--trigger-comment-id "$trigger_comment_id")
fi
if [ -n "$trigger_created_at" ]; then
  snapshot_args+=(--trigger-created-at "$trigger_created_at")
fi

start_epoch="$(date +%s)"
snapshot_stdout="$tmp_dir/snapshot.json"
snapshot_stderr="$tmp_dir/snapshot.stderr"
set +e
"$snapshot_script" "${snapshot_args[@]}" >"$snapshot_stdout" 2>"$snapshot_stderr"
snapshot_exit=$?
set -e

OBS_SNAPSHOT_PATH="$snapshot_stdout" \
OBS_SNAPSHOT_EXIT="$snapshot_exit" \
OBS_SCRIPT="wait_pr_observation.sh" \
OBS_TIMEOUT_SECONDS="$timeout_seconds" \
OBS_POLL_INTERVAL_SECONDS="$poll_interval_seconds" \
OBS_QUIET_SECONDS="$quiet_seconds" \
OBS_SAME_FINGERPRINT_COUNT="$same_fingerprint_count" \
OBS_ZERO_CHECK_GRACE_POLLS="$zero_check_grace_polls" \
python3 - <<'PY' >"$tmp_dir/result.json"
import hashlib
import json
import os
from datetime import datetime, timezone

snapshot_path = os.environ["OBS_SNAPSHOT_PATH"]
snapshot_exit = int(os.environ["OBS_SNAPSHOT_EXIT"])
try:
    payload = json.load(open(snapshot_path, encoding="utf-8"))
except Exception:
    payload = {}

if not payload:
    payload = {
        "overall_status": "unknown",
        "normalized_status": "unknown",
        "observation_complete": False,
        "summary": {"ci": "unknown", "review": "unknown", "head": "unknown"},
        "limitations": [],
        "recommended_next_action": "human_gate",
        "ci": {"status": "unknown", "checks": [], "failures": []},
        "review": {"status": "unknown", "signals": [], "codex_authored": []},
        "trigger": {"source": "none", "comment_id": None, "created_at": None},
        "artifacts": {},
    }

if snapshot_exit != 0:
    payload.setdefault("limitations", []).append(
        {
            "code": "snapshot_script_failed",
            "source": "fetch_pr_observation_snapshot.sh",
            "severity": "blocking",
            "message": "snapshot script failed before final wait classification",
            "exit_code": snapshot_exit,
        }
    )
    payload["overall_status"] = "unknown"
    payload["normalized_status"] = "unknown"
    payload["observation_complete"] = False

payload["script"] = os.environ["OBS_SCRIPT"]
payload["wait"] = {
    "polls": 1,
    "timeout_seconds": int(os.environ["OBS_TIMEOUT_SECONDS"]),
    "poll_interval_seconds": int(os.environ["OBS_POLL_INTERVAL_SECONDS"]),
    "quiet_seconds": int(os.environ["OBS_QUIET_SECONDS"]),
    "same_fingerprint_count": int(os.environ["OBS_SAME_FINGERPRINT_COUNT"]),
    "zero_check_grace_polls": int(os.environ["OBS_ZERO_CHECK_GRACE_POLLS"]),
    "contract_phase": "s02_single_snapshot_boundary",
}
payload["observed_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
payload.setdefault("artifacts", {})
payload["artifacts"]["result_json"] = None
payload["artifacts"]["latest_json"] = None
payload["artifacts"]["events_ndjson"] = None
payload["fingerprint"] = hashlib.sha256(
    json.dumps(
        {
            "fingerprint": payload.get("fingerprint"),
            "normalized_status": payload.get("normalized_status"),
            "limitations": [item.get("code") for item in payload.get("limitations", [])],
            "wait": payload["wait"],
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
).hexdigest()
print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
PY

if [ -n "$out_dir" ]; then
  mkdir -p "$out_dir/snapshots"
  cp "$tmp_dir/result.json" "$out_dir/result.json"
  cp "$snapshot_stdout" "$out_dir/latest.json"
  cp "$snapshot_stdout" "$out_dir/snapshots/poll-0001.json"
  printf '{}\n' >"$out_dir/latest_delta.json"
  printf '{"event":"poll","poll":1,"result":"snapshot"}\n' >"$out_dir/events.ndjson"
fi

if [ "$progress" = "stderr-summary" ]; then
  now_epoch="$(date +%s)"
  elapsed=$((now_epoch - start_epoch))
  remain=$((timeout_seconds - elapsed))
  if [ "$remain" -lt 0 ]; then
    remain=0
  fi
  printf 'poll=1 elapsed=%s remain=%s phase=terminal ci=unknown review=unknown quiet=0/%s limit=ok final=stdout_json\n' \
    "$elapsed" "$remain" "$quiet_seconds" >&2
fi

cat "$tmp_dir/result.json"
