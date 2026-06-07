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

OBS_SNAPSHOT_SCRIPT="$snapshot_script" \
OBS_REPO="$repo" \
OBS_PR="$pr" \
OBS_HEAD_SHA="$head_sha" \
OBS_TIMEOUT_SECONDS="$timeout_seconds" \
OBS_POLL_INTERVAL_SECONDS="$poll_interval_seconds" \
OBS_QUIET_SECONDS="$quiet_seconds" \
OBS_SAME_FINGERPRINT_COUNT="$same_fingerprint_count" \
OBS_ZERO_CHECK_GRACE_POLLS="$zero_check_grace_polls" \
OBS_TRIGGER_COMMENT_ID="$trigger_comment_id" \
OBS_TRIGGER_CREATED_AT="$trigger_created_at" \
OBS_BODY_MODE="$body_mode" \
OBS_PROGRESS="$progress" \
OBS_OUT_DIR="$out_dir" \
python3 - <<'PY'
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_json(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def limitation_codes(payload: dict) -> list[str]:
    return [
        str(item.get("code"))
        for item in payload.get("limitations", [])
        if isinstance(item, dict) and item.get("code")
    ]


def has_blocking_limitation(payload: dict, ignored_codes: set[str] | None = None) -> bool:
    ignored_codes = ignored_codes or set()
    return any(
        isinstance(item, dict)
        and item.get("severity") == "blocking"
        and item.get("code") not in ignored_codes
        for item in payload.get("limitations", [])
    )


def has_zero_check_limitation(payload: dict) -> bool:
    return any(
        isinstance(item, dict) and item.get("code") == "zero_checks_s03_non_success"
        for item in payload.get("limitations", [])
    )


def semantic_fingerprint(payload: dict) -> str:
    source = {
        "repo": payload.get("repo"),
        "pr": payload.get("pr"),
        "expected_head_sha": payload.get("expected_head_sha"),
        "current_head_sha": payload.get("current_head_sha"),
        "head_matches_expected": payload.get("head_matches_expected"),
        "snapshot_fingerprint": payload.get("fingerprint"),
        "normalized_status": payload.get("normalized_status"),
        "limitations": limitation_codes(payload),
        "ci": {
            "status": payload.get("ci", {}).get("status")
            if isinstance(payload.get("ci"), dict)
            else None,
            "failures": payload.get("ci", {}).get("failures")
            if isinstance(payload.get("ci"), dict)
            else None,
        },
        "review": {
            "status": payload.get("review", {}).get("status")
            if isinstance(payload.get("review"), dict)
            else None,
            "fingerprint": payload.get("review", {}).get("fingerprint")
            if isinstance(payload.get("review"), dict)
            else None,
            "threads": payload.get("review", {}).get("threads")
            if isinstance(payload.get("review"), dict)
            else None,
        },
        "trigger": payload.get("trigger"),
    }
    return sha256_json(source)


def fallback_snapshot(snapshot_exit: int, stdout_text: str, stderr_text: str) -> dict:
    limitations = []
    if snapshot_exit != 0:
        limitations.append(
            {
                "code": "snapshot_script_failed",
                "source": "fetch_pr_observation_snapshot.sh",
                "severity": "blocking",
                "message": "snapshot script failed before final wait classification",
                "exit_code": snapshot_exit,
                "stderr_sha256": hashlib.sha256(stderr_text.encode()).hexdigest(),
                "stdout_sha256": hashlib.sha256(stdout_text.encode()).hexdigest(),
            }
        )
    else:
        limitations.append(
            {
                "code": "snapshot_json_unavailable",
                "source": "fetch_pr_observation_snapshot.sh",
                "severity": "blocking",
                "message": "snapshot script did not return parseable JSON",
                "stdout_sha256": hashlib.sha256(stdout_text.encode()).hexdigest(),
            }
        )
    return {
        "script": "fetch_pr_observation_snapshot.sh",
        "status": "unknown",
        "overall_status": "unknown",
        "normalized_status": "unknown",
        "observation_complete": False,
        "observed_at": utc_now(),
        "repo": os.environ["OBS_REPO"],
        "pr": int(os.environ["OBS_PR"]),
        "expected_head_sha": os.environ["OBS_HEAD_SHA"],
        "current_head_sha": None,
        "head_matches_expected": None,
        "summary": {"ci": "unknown", "review": "unknown", "head": "unknown"},
        "limitations": limitations,
        "recommended_next_action": "human_gate",
        "ci": {"status": "unknown", "checks": [], "failures": []},
        "review": {"status": "unknown", "signals": [], "codex_authored": []},
        "trigger": {"source": "none", "comment_id": None, "created_at": None},
        "artifacts": {},
    }


def timeout_snapshot(timeout_seconds: float, stdout_text: object, stderr_text: object) -> dict:
    if isinstance(stdout_text, bytes):
        stdout_text = stdout_text.decode(errors="replace")
    if isinstance(stderr_text, bytes):
        stderr_text = stderr_text.decode(errors="replace")
    stdout_text = "" if stdout_text is None else str(stdout_text)
    stderr_text = "" if stderr_text is None else str(stderr_text)
    return {
        "script": "fetch_pr_observation_snapshot.sh",
        "status": "timeout",
        "overall_status": "timeout",
        "normalized_status": "timeout",
        "observation_complete": False,
        "observed_at": utc_now(),
        "repo": os.environ["OBS_REPO"],
        "pr": int(os.environ["OBS_PR"]),
        "expected_head_sha": os.environ["OBS_HEAD_SHA"],
        "current_head_sha": None,
        "head_matches_expected": None,
        "summary": {"ci": "unknown", "review": "unknown", "head": "unknown"},
        "limitations": [
            {
                "code": "snapshot_poll_timeout",
                "source": "fetch_pr_observation_snapshot.sh",
                "severity": "blocking",
                "message": "snapshot poll exceeded the remaining wait deadline",
                "timeout_seconds": timeout_seconds,
                "stdout_sha256": hashlib.sha256(stdout_text.encode()).hexdigest(),
                "stderr_sha256": hashlib.sha256(stderr_text.encode()).hexdigest(),
            }
        ],
        "recommended_next_action": "wait_or_rerun",
        "ci": {"status": "unknown", "checks": [], "failures": []},
        "review": {"status": "unknown", "signals": [], "codex_authored": []},
        "trigger": {},
        "artifacts": {},
    }


def append_snapshot_poll_timeout_limitation(
    payload: dict,
    timeout_seconds: float,
    stdout_text: object,
    stderr_text: object,
    *,
    source: str = "fetch_pr_observation_snapshot.sh",
    message: str = "snapshot poll exceeded the remaining wait deadline",
    deadline_reached: bool | None = None,
) -> None:
    if isinstance(stdout_text, bytes):
        stdout_text = stdout_text.decode(errors="replace")
    if isinstance(stderr_text, bytes):
        stderr_text = stderr_text.decode(errors="replace")
    stdout_text = "" if stdout_text is None else str(stdout_text)
    stderr_text = "" if stderr_text is None else str(stderr_text)
    limitations = payload.setdefault("limitations", [])
    if any(
        isinstance(item, dict) and item.get("code") == "snapshot_poll_timeout"
        for item in limitations
    ):
        return
    limitations.append(
        {
            "code": "snapshot_poll_timeout",
            "source": source,
            "severity": "blocking",
            "message": message,
            "timeout_seconds": timeout_seconds,
            "stdout_sha256": hashlib.sha256(stdout_text.encode()).hexdigest(),
            "stderr_sha256": hashlib.sha256(stderr_text.encode()).hexdigest(),
            **({} if deadline_reached is None else {"deadline_reached": deadline_reached}),
        }
    )


def terminate_process_group(proc: subprocess.Popen[str]) -> None:
    try:
        pgid = os.getpgid(proc.pid)
    except ProcessLookupError:
        return
    try:
        os.killpg(pgid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        proc.wait(timeout=1)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(pgid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait()


def run_snapshot(args: list[str], timeout_seconds: float) -> tuple[int, str, str, bool]:
    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        stdout_text, stderr_text = proc.communicate(timeout=timeout_seconds)
        return proc.returncode, stdout_text, stderr_text, False
    except subprocess.TimeoutExpired as exc:
        terminate_process_group(proc)
        stdout_text, stderr_text = proc.communicate()
        if exc.stdout:
            stdout_text = (exc.stdout if isinstance(exc.stdout, str) else exc.stdout.decode(errors="replace")) + (stdout_text or "")
        if exc.stderr:
            stderr_text = (exc.stderr if isinstance(exc.stderr, str) else exc.stderr.decode(errors="replace")) + (stderr_text or "")
        return proc.returncode if proc.returncode is not None else -signal.SIGKILL, stdout_text or "", stderr_text or "", True


def copy_tree_contents(source: Path, destination: Path) -> None:
    if not source.is_dir():
        return
    destination.mkdir(parents=True, exist_ok=True)
    for child in source.iterdir():
        target = destination / child.name
        if child.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(child, target)
        else:
            shutil.copy2(child, target)


def clear_managed_out_artifacts(out_dir: Path) -> None:
    managed_names = [
        "result.json",
        "latest.json",
        "events.ndjson",
        "latest_delta.json",
        "raw",
        "snapshots",
    ]
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in managed_names:
        target = out_dir / name
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists() or target.is_symlink():
            target.unlink()
    (out_dir / "snapshots").mkdir(parents=True, exist_ok=True)
    (out_dir / "raw").mkdir(parents=True, exist_ok=True)


def classify(payload: dict, poll: int, zero_check_grace_polls: int) -> tuple[str, str, str, bool, bool]:
    ci = payload.get("ci") if isinstance(payload.get("ci"), dict) else {}
    review = payload.get("review") if isinstance(payload.get("review"), dict) else {}
    ci_status = ci.get("status") or payload.get("summary", {}).get("ci") or "unknown"
    review_status = review.get("status") or payload.get("summary", {}).get("review") or "unknown"

    if payload.get("head_matches_expected") is False or payload.get("normalized_status") == "stale_head":
        return "stale_head", "stale_head", "rerun_for_current_head", False, True
    if ci_status == "none" and has_zero_check_limitation(payload):
        if has_blocking_limitation(payload, ignored_codes={"zero_checks_s03_non_success"}):
            return "unknown", "unknown", "human_gate", False, True
        if poll < zero_check_grace_polls:
            return "none", "none", "wait", False, False
        return "unknown", "unknown", "human_gate", False, True
    if ci_status == "failed":
        return "failed", "failed", "fix_ci", False, True
    if ci_status in {"pending", "running", "none"}:
        if has_blocking_limitation(payload, ignored_codes={"required_checks_missing_or_pending"}):
            return "unknown", "unknown", "human_gate", False, True
        return ci_status, ci_status, "wait", False, False
    if has_blocking_limitation(payload):
        return "unknown", "unknown", "human_gate", False, True
    if ci_status != "passed":
        return "unknown", "unknown", "human_gate", False, True
    if review_status in {"none", "approved"}:
        return "passed", "passed", "merge_prepared", True, False
    if review_status in {"requested", "commented", "changes_requested", "unresolved"}:
        return "human_gate", "human_gate", "address_review_feedback", True, False
    return "unknown", "unknown", "human_gate", False, True


def progress_line(
    *,
    poll: int,
    elapsed: int,
    remain: int,
    phase: str,
    payload: dict,
    quiet_elapsed: int,
    quiet_required: int,
) -> str:
    ci = payload.get("summary", {}).get("ci") or payload.get("ci", {}).get("status") or "unknown"
    review = payload.get("summary", {}).get("review") or payload.get("review", {}).get("status") or "unknown"
    line = (
        f"poll={poll} elapsed={elapsed} remain={remain} phase={phase} "
        f"ci={ci} review={review} quiet={quiet_elapsed}/{quiet_required} limit=ok final=stdout_json"
    )
    return line[:240]


def mark_latest_timeout(payload: dict, latest_change_monotonic: float, same_count: int) -> None:
    quiet_elapsed = int(max(0, time.monotonic() - latest_change_monotonic))
    append_snapshot_poll_timeout_limitation(
        payload,
        0,
        "",
        "",
        source="wait_pr_observation.sh",
        message="wait deadline expired before quiet/stability completed",
        deadline_reached=True,
    )
    payload["status"] = "timeout"
    payload["overall_status"] = "timeout"
    payload["normalized_status"] = "timeout"
    payload["observation_complete"] = False
    payload["recommended_next_action"] = "wait_or_rerun"
    payload["observed_at"] = utc_now()
    payload.setdefault("wait", {})["deadline_reached"] = True
    payload["wait"]["quiet_seconds_observed"] = quiet_elapsed
    payload["wait"]["same_fingerprint_observed"] = same_count


snapshot_script = os.environ["OBS_SNAPSHOT_SCRIPT"]
repo = os.environ["OBS_REPO"]
pr = os.environ["OBS_PR"]
head_sha = os.environ["OBS_HEAD_SHA"]
timeout_seconds = int(os.environ["OBS_TIMEOUT_SECONDS"])
poll_interval_seconds = int(os.environ["OBS_POLL_INTERVAL_SECONDS"])
quiet_seconds = int(os.environ["OBS_QUIET_SECONDS"])
same_fingerprint_count = int(os.environ["OBS_SAME_FINGERPRINT_COUNT"])
zero_check_grace_polls = int(os.environ["OBS_ZERO_CHECK_GRACE_POLLS"])
trigger_comment_id = os.environ["OBS_TRIGGER_COMMENT_ID"]
trigger_created_at = os.environ["OBS_TRIGGER_CREATED_AT"]
body_mode = os.environ["OBS_BODY_MODE"]
progress = os.environ["OBS_PROGRESS"]
out_dir_text = os.environ["OBS_OUT_DIR"]
out_dir = Path(out_dir_text) if out_dir_text else None

snapshot_args = [
    snapshot_script,
    "--repo",
    repo,
    "--pr",
    pr,
    "--head-sha",
    head_sha,
    "--body-mode",
    body_mode,
]
if trigger_comment_id:
    snapshot_args.extend(["--trigger-comment-id", trigger_comment_id])
if trigger_created_at:
    snapshot_args.extend(["--trigger-created-at", trigger_created_at])

if out_dir:
    clear_managed_out_artifacts(out_dir)

start_monotonic = time.monotonic()
deadline = start_monotonic + timeout_seconds
previous_fingerprint = None
latest_change_monotonic = start_monotonic
same_count = 0
poll = 0
events: list[dict] = []
latest_payload: dict | None = None
latest_snapshot_text = "{}\n"
latest_delta: dict = {}
latest_snapshot_out_dir: Path | None = None
final_phase = "timeout"

while True:
    if latest_payload is not None and time.monotonic() >= deadline:
        final_phase = "timeout"
        mark_latest_timeout(latest_payload, latest_change_monotonic, same_count)
        break

    if latest_payload is not None and (deadline - time.monotonic()) < 0.05:
        final_phase = "timeout"
        mark_latest_timeout(latest_payload, latest_change_monotonic, same_count)
        break

    poll += 1
    now_before = time.monotonic()
    snapshot_timeout = max(0.001, deadline - time.monotonic())
    snapshot_poll_timed_out = False
    poll_snapshot_args = list(snapshot_args)
    poll_out_dir = None
    if out_dir:
        poll_out_dir = out_dir / "snapshots" / f"poll-{poll:04d}-artifacts"
        poll_snapshot_args.extend(["--out", str(poll_out_dir)])
    snapshot_exit, snapshot_stdout, snapshot_stderr, snapshot_poll_timed_out = run_snapshot(
        poll_snapshot_args,
        snapshot_timeout,
    )
    if snapshot_poll_timed_out and latest_payload is not None:
        payload = latest_payload
        append_snapshot_poll_timeout_limitation(
            payload,
            snapshot_timeout,
            snapshot_stdout,
            snapshot_stderr,
        )
        mark_latest_timeout(payload, latest_change_monotonic, same_count)
        snapshot_text = latest_snapshot_text
    elif snapshot_poll_timed_out:
        payload = timeout_snapshot(snapshot_timeout, snapshot_stdout, snapshot_stderr)
        snapshot_text = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    else:
        snapshot_text = snapshot_stdout if snapshot_stdout else "{}\n"
        try:
            payload = json.loads(snapshot_text)
            if not isinstance(payload, dict):
                payload = fallback_snapshot(snapshot_exit, snapshot_text, snapshot_stderr)
                snapshot_text = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
        except Exception:
            payload = fallback_snapshot(snapshot_exit, snapshot_text, snapshot_stderr)
            snapshot_text = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"

    fingerprint = semantic_fingerprint(payload)
    observed_monotonic = time.monotonic()
    if fingerprint == previous_fingerprint:
        same_count += 1
        changed = False
    else:
        latest_change_monotonic = observed_monotonic
        latest_delta = {
            "previous_fingerprint": previous_fingerprint,
            "current_fingerprint": fingerprint,
            "changed": previous_fingerprint is not None,
            "poll": poll,
        }
        same_count = 1
        previous_fingerprint = fingerprint
        changed = True

    quiet_elapsed = int(max(0, time.monotonic() - latest_change_monotonic))
    normalized_status, overall_status, next_action, can_complete_when_stable, terminal_now = classify(
        payload,
        poll,
        zero_check_grace_polls,
    )
    stable = same_count >= same_fingerprint_count and quiet_elapsed >= quiet_seconds
    observation_complete = bool(can_complete_when_stable and stable)
    elapsed = int(max(0, time.monotonic() - start_monotonic))
    remain = int(max(0, deadline - time.monotonic()))
    if observation_complete:
        final_phase = "terminal"
    elif snapshot_poll_timed_out:
        final_phase = "timeout"
        normalized_status = "timeout"
        overall_status = "timeout"
        next_action = "wait_or_rerun"
    elif terminal_now:
        final_phase = "terminal"
    elif time.monotonic() >= deadline:
        final_phase = "timeout"
        mark_latest_timeout(payload, latest_change_monotonic, same_count)
        normalized_status = "timeout"
        overall_status = "timeout"
        next_action = "wait_or_rerun"
    else:
        final_phase = "wait"

    payload["script"] = "wait_pr_observation.sh"
    payload["status"] = normalized_status
    payload["overall_status"] = overall_status
    payload["normalized_status"] = normalized_status
    payload["observation_complete"] = observation_complete
    payload["recommended_next_action"] = next_action
    payload["fingerprint"] = fingerprint
    payload["observed_at"] = utc_now()
    payload["wait"] = {
        "polls": poll,
        "timeout_seconds": timeout_seconds,
        "poll_interval_seconds": poll_interval_seconds,
        "quiet_seconds_required": quiet_seconds,
        "quiet_seconds_observed": quiet_elapsed,
        "same_fingerprint_required": same_fingerprint_count,
        "same_fingerprint_observed": same_count,
        "zero_check_grace_polls": zero_check_grace_polls,
        "latest_change_poll": latest_delta.get("poll", poll),
        "deadline_reached": final_phase == "timeout",
        "contract_phase": "s05_stable_wait_loop",
    }
    payload.setdefault("artifacts", {})
    payload["artifacts"].update(
        {
            "result_json": str(out_dir / "result.json") if out_dir else None,
            "latest_json": str(out_dir / "latest.json") if out_dir else None,
            "events_ndjson": str(out_dir / "events.ndjson") if out_dir else None,
            "latest_delta_json": str(out_dir / "latest_delta.json") if out_dir else None,
            "snapshots_dir": str(out_dir / "snapshots") if out_dir else None,
        }
    )

    latest_payload = payload
    latest_snapshot_text = snapshot_text
    latest_snapshot_out_dir = poll_out_dir
    event = {
        "event": "poll",
        "poll": poll,
        "fingerprint": fingerprint,
        "changed": changed,
        "normalized_status": normalized_status,
        "observation_complete": observation_complete,
        "ci": payload.get("summary", {}).get("ci"),
        "review": payload.get("summary", {}).get("review"),
        "quiet_seconds_observed": quiet_elapsed,
        "same_fingerprint_observed": same_count,
    }
    events.append(event)

    if out_dir:
        (out_dir / "snapshots" / f"poll-{poll:04d}.json").write_text(
            latest_snapshot_text if latest_snapshot_text.endswith("\n") else latest_snapshot_text + "\n",
            encoding="utf-8",
        )

    if progress == "stderr-summary":
        print(
            progress_line(
                poll=poll,
                elapsed=elapsed,
                remain=remain,
                phase=final_phase,
                payload=payload,
                quiet_elapsed=quiet_elapsed,
                quiet_required=quiet_seconds,
            ),
            file=sys.stderr,
        )

    if observation_complete or terminal_now or final_phase == "timeout":
        break

    sleep_seconds = min(poll_interval_seconds, max(0, deadline - time.monotonic()))
    if sleep_seconds <= 0:
        continue
    time.sleep(sleep_seconds)

assert latest_payload is not None
result_text = json.dumps(latest_payload, sort_keys=True, separators=(",", ":")) + "\n"
if out_dir:
    if latest_snapshot_out_dir:
        copy_tree_contents(latest_snapshot_out_dir / "raw", out_dir / "raw")
    (out_dir / "result.json").write_text(result_text, encoding="utf-8")
    (out_dir / "latest.json").write_text(
        latest_snapshot_text if latest_snapshot_text.endswith("\n") else latest_snapshot_text + "\n",
        encoding="utf-8",
    )
    (out_dir / "latest_delta.json").write_text(
        json.dumps(latest_delta or {}, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    (out_dir / "events.ndjson").write_text(
        "".join(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n" for event in events),
        encoding="utf-8",
    )

print(result_text, end="")
PY
