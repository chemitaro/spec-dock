#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
usage: trigger_codex_review.sh --repo OWNER/REPO --pr NUMBER --head-sha SHA

Posts exactly one fixed PR issue comment body, "@codex review", after
verifying that the PR head still matches --head-sha. The script does not accept
caller-provided bodies, endpoints, methods, GraphQL queries, headers, jq
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

owner="${repo%%/*}"
name="${repo#*/}"

TRIGGER_REPO="$repo" \
TRIGGER_OWNER="$owner" \
TRIGGER_NAME="$name" \
TRIGGER_PR="$pr" \
TRIGGER_HEAD_SHA="$head_sha" \
python3 - <<'PY'
import json
import base64
import hashlib
import os
import subprocess
from datetime import datetime, timezone

repo = os.environ["TRIGGER_REPO"]
owner = os.environ["TRIGGER_OWNER"]
name = os.environ["TRIGGER_NAME"]
pr = os.environ["TRIGGER_PR"]
expected_head_sha = os.environ["TRIGGER_HEAD_SHA"]
endpoint = f"repos/{owner}/{name}/issues/{pr}/comments"
fixed_body = "@codex review"
policy_path = ".github/codex/review-policy.md"
policy_max_bytes = 32768


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_gh(args):
    completed = subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode, completed.stdout, completed.stderr


def parse_gh_paginated_stdout(text):
    decoder = json.JSONDecoder()
    index = 0
    payloads = []
    text = text or ""
    while index < len(text):
        while index < len(text) and text[index].isspace():
            index += 1
        if index >= len(text):
            break
        payload, index = decoder.raw_decode(text, index)
        payloads.append(payload)
    if not payloads:
        return []
    if len(payloads) == 1:
        return payloads[0]
    if all(isinstance(payload, list) for payload in payloads):
        merged_list = []
        for payload in payloads:
            merged_list.extend(payload)
        return merged_list
    if all(isinstance(payload, dict) for payload in payloads):
        merged = {}
        for payload in payloads:
            for key, value in payload.items():
                if isinstance(value, list):
                    merged.setdefault(key, [])
                    if isinstance(merged[key], list):
                        merged[key].extend(value)
                    else:
                        merged[key] = value
                elif isinstance(value, int) and key == "total_count":
                    merged[key] = int(merged.get(key, 0) or 0) + value
                else:
                    merged[key] = value
        return merged
    return payloads[-1]


def load_json(text, fallback):
    try:
        return parse_gh_paginated_stdout(text)
    except Exception:
        return fallback


def emit(payload):
    print(json.dumps(payload, separators=(",", ":"), sort_keys=True))


def limitation(code, message, **extra):
    payload = {"code": code, "message": message, "source": "trigger_codex_review.sh"}
    sanitized_extra = {}
    for key, value in extra.items():
        if key.endswith("gh_stderr") or key == "gh_stderr":
            sanitized_extra[f"{key}_sha256"] = hashlib.sha256(str(value or "").encode()).hexdigest()
        else:
            sanitized_extra[key] = value
    payload.update(sanitized_extra)
    return payload


def token_source():
    if os.environ.get("GH_TOKEN"):
        return "GH_TOKEN"
    if os.environ.get("GITHUB_TOKEN"):
        return "GITHUB_TOKEN"
    return "gh_saved_auth"


def is_permission_denied(stderr):
    lowered = (stderr or "").lower()
    return (
        "resource not accessible by personal access token" in lowered
        or "resource not accessible by integration" in lowered
        or "permission denied" in lowered
    )


def trigger_permission_limitation(stderr, exit_code):
    return limitation(
        "github_token_permission_denied",
        "GitHub token lacks permission to post the fixed Codex review trigger comment",
        capability="trigger_comment_write",
        api=endpoint,
        status="permission_denied",
        token_source=token_source(),
        severity="blocking",
        recommended_next_action="fix_github_token_permissions",
        secret_redacted=True,
        stderr_sha256=hashlib.sha256((stderr or "").encode()).hexdigest(),
        exit_code=exit_code,
    )


def head_matches(actual, expected):
    actual_lc = (actual or "").lower()
    expected_lc = (expected or "").lower()
    return bool(actual_lc and expected_lc and actual_lc.startswith(expected_lc))


def base_payload():
    return {
        "script": "trigger_codex_review.sh",
        "repo": repo,
        "pr": int(pr),
        "expected_head_sha": expected_head_sha,
        "current_head_sha": None,
        "final_head_sha": None,
        "base_sha": None,
        "head_matches_expected": False,
        "success": False,
        "overall_status": "unknown",
        "normalized_status": "unknown",
        "recommended_next_action": "unknown",
        "review_policy": {
            "source": "fixed_default",
            "path": policy_path,
            "base_sha": None,
            "hash": None,
            "bytes": 0,
            "status": "not_requested",
        },
        "trigger": {
            "action": "none",
            "body": fixed_body,
            "body_matches_expected": None,
            "comment_id": None,
            "created_at": None,
            "endpoint": endpoint,
            "mode": "post-once",
            "url": None,
        },
        "recovery": {
            "attempted": False,
            "accepted": False,
            "new_exact_comment_count": 0,
        },
        "limitations": [],
        "generated_at": now_iso(),
    }


payload = base_payload()


def block_review_policy_gate():
    payload["success"] = False
    payload["overall_status"] = "human_gate"
    payload["normalized_status"] = "human_gate"
    payload["recommended_next_action"] = "human_gate"
    payload["trigger"]["action"] = "blocked"
    emit(payload)
    raise SystemExit(0)

metadata_exit, metadata_stdout, metadata_stderr = run_gh(
    ["pr", "view", pr, "--repo", repo, "--json", "headRefOid,baseRefOid,url,state,isDraft,number"]
)
metadata = load_json(metadata_stdout, {}) if metadata_exit == 0 else {}
current_head_sha = metadata.get("headRefOid") or ""
base_sha = metadata.get("baseRefOid") or ""
payload["current_head_sha"] = current_head_sha or None
payload["base_sha"] = base_sha or None
payload["head_matches_expected"] = head_matches(current_head_sha, expected_head_sha)

if metadata_exit != 0 or not current_head_sha:
    payload["overall_status"] = "metadata_failed"
    payload["trigger"]["action"] = "failed"
    payload["limitations"].append(
        limitation(
            "pr_metadata_collection_failed",
            "could not read PR head before posting trigger comment",
            gh_exit=metadata_exit,
            gh_stderr=metadata_stderr.strip(),
        )
    )
    emit(payload)
    raise SystemExit(0)

if not payload["head_matches_expected"]:
    payload["overall_status"] = "stale_head"
    payload["trigger"]["action"] = "stale"
    payload["limitations"].append(
        limitation(
            "pre_trigger_head_mismatch",
            "PR head did not match expected --head-sha before trigger comment POST",
            current_head_sha=current_head_sha,
            expected_head_sha=expected_head_sha,
        )
    )
    emit(payload)
    raise SystemExit(0)

if metadata.get("isDraft") is True:
    payload["overall_status"] = "draft_pr"
    payload["trigger"]["action"] = "skipped"
    payload["limitations"].append(
        limitation(
            "draft_pr_trigger_skipped",
            "draft PR cannot receive the deterministic Codex review trigger",
        )
    )
    emit(payload)
    raise SystemExit(0)

pr_state = str(metadata.get("state") or "").upper()
if pr_state and pr_state != "OPEN":
    payload["overall_status"] = "non_open_pr"
    payload["trigger"]["action"] = "skipped"
    payload["limitations"].append(
        limitation(
            "non_open_pr_trigger_skipped",
            "non-open PR cannot receive the deterministic Codex review trigger",
            state=metadata.get("state"),
        )
    )
    emit(payload)
    raise SystemExit(0)

if not base_sha:
    payload["review_policy"].update({"source": "base_sha", "status": "base_sha_missing"})
    payload["limitations"].append(
        limitation(
            "review_policy_base_sha_missing",
            "PR metadata did not include baseRefOid; trusted base review policy cannot be loaded",
            severity="blocking",
        )
    )
elif base_sha:
    policy_endpoint = f"repos/{owner}/{name}/contents/{policy_path}?ref={base_sha}"
    policy_exit, policy_stdout, policy_stderr = run_gh(["api", policy_endpoint])
    policy_payload = load_json(policy_stdout, {}) if policy_exit == 0 else {}
    encoded_content = policy_payload.get("content") if isinstance(policy_payload, dict) else None
    if policy_exit == 0 and isinstance(encoded_content, str):
        try:
            policy_text = base64.b64decode("".join(encoded_content.split()), validate=False).decode("utf-8")
        except Exception:
            policy_text = ""
        policy_bytes = policy_text.encode("utf-8") if policy_text else b""
        if policy_bytes and len(policy_bytes) <= policy_max_bytes:
            policy_hash = hashlib.sha256(policy_bytes).hexdigest()
            fixed_body = "\n".join(
                (
                    "@codex review",
                    "",
                    "Trusted review policy:",
                    f"- source: {repo}@{base_sha}:{policy_path}",
                    f"- policy_sha256: {policy_hash}",
                    f"- reviewed_head_sha: {expected_head_sha}",
                    "",
                    policy_text.rstrip(),
                )
            )
            payload["review_policy"].update(
                {
                    "source": "base_sha",
                    "base_sha": base_sha,
                    "hash": policy_hash,
                    "bytes": len(policy_bytes),
                    "status": "loaded",
                }
            )
            payload["trigger"]["body"] = fixed_body
        elif policy_bytes:
            payload["review_policy"].update(
                {
                    "source": "base_sha",
                    "base_sha": base_sha,
                    "bytes": len(policy_bytes),
                    "status": "too_large",
                }
            )
            payload["limitations"].append(
                limitation(
                    "review_policy_too_large",
                    "trusted base review policy exceeds the maximum accepted size",
                    api=policy_endpoint,
                    max_bytes=policy_max_bytes,
                    severity="blocking",
                )
            )
        else:
            payload["review_policy"].update({"source": "base_sha", "base_sha": base_sha, "status": "invalid"})
            payload["limitations"].append(
                limitation(
                    "review_policy_invalid",
                    "trusted base review policy could not be decoded as non-empty UTF-8 text",
                    api=policy_endpoint,
                    severity="blocking",
                )
            )
    else:
        payload["review_policy"].update({"source": "base_sha", "base_sha": base_sha, "status": "missing"})
        payload["limitations"].append(
            limitation(
                "review_policy_missing",
                "trusted base review policy could not be loaded",
                api=policy_endpoint,
                gh_exit=policy_exit,
                gh_stderr=policy_stderr.strip(),
                severity="blocking",
            )
        )

if payload["review_policy"]["status"] != "loaded":
    block_review_policy_gate()

before_exit, before_stdout, before_stderr = run_gh(["api", endpoint, "--paginate"])
before_comments_raw = load_json(before_stdout, None) if before_exit == 0 else None
before_comments_trusted = isinstance(before_comments_raw, list)
before_comments = before_comments_raw if before_comments_trusted else []
if not before_comments_trusted:
    payload["limitations"].append(
        limitation(
            "before_comments_snapshot_untrusted",
            "could not trust before-comment snapshot; POST failure recovery will not be accepted",
            gh_exit=before_exit,
            gh_stderr=before_stderr.strip(),
        )
    )
before_ids = {comment.get("id") for comment in before_comments if isinstance(comment, dict)}

post_exit, post_stdout, post_stderr = run_gh(
    ["api", endpoint, "--method", "POST", "--raw-field", f"body={fixed_body}"]
)
post_payload = load_json(post_stdout, {}) if post_exit == 0 else {}

if post_exit == 0 and isinstance(post_payload, dict):
    payload["trigger"].update(
        {
            "action": "posted",
            "body_matches_expected": post_payload.get("body") == fixed_body,
            "comment_id": post_payload.get("id"),
            "created_at": post_payload.get("created_at"),
            "url": post_payload.get("html_url") or post_payload.get("url"),
        }
    )
    if payload["trigger"]["body_matches_expected"] and payload["trigger"]["comment_id"] and payload["trigger"]["created_at"]:
        payload["success"] = True
        payload["overall_status"] = "trigger_posted"
    else:
        payload["overall_status"] = "trigger_response_invalid"
        payload["limitations"].append(
            limitation(
                "trigger_response_invalid",
                "POST succeeded but response did not contain exact trigger metadata",
            )
        )
else:
    payload["trigger"]["action"] = "failed"
    payload["overall_status"] = "trigger_post_failed"
    if is_permission_denied(post_stderr):
        payload["limitations"].append(trigger_permission_limitation(post_stderr, post_exit))
    payload["limitations"].append(
        limitation(
            "trigger_post_failed",
            "fixed trigger comment POST failed; blind retry is not allowed",
            gh_exit=post_exit,
            gh_stderr=post_stderr.strip(),
        )
    )
    payload["recovery"]["attempted"] = True
    after_exit, after_stdout, after_stderr = run_gh(["api", endpoint, "--paginate"])
    after_comments_raw = load_json(after_stdout, None) if after_exit == 0 else None
    after_comments_trusted = isinstance(after_comments_raw, list)
    after_comments = after_comments_raw if after_comments_trusted else []
    if not before_comments_trusted:
        payload["limitations"].append(
            limitation(
                "trigger_recovery_unavailable",
                "POST failure recovery requires a trusted before-comment snapshot",
            )
        )
    if not after_comments_trusted:
        payload["limitations"].append(
            limitation(
                "after_comments_snapshot_untrusted",
                "POST failure recovery requires a trusted after-comment snapshot",
                gh_exit=after_exit,
                gh_stderr=after_stderr.strip(),
            )
        )
    new_exact_comments = [
        comment for comment in after_comments
        if isinstance(comment, dict)
        and comment.get("id") not in before_ids
        and comment.get("body") == fixed_body
    ]
    payload["recovery"]["new_exact_comment_count"] = len(new_exact_comments)
    if before_comments_trusted and after_comments_trusted and len(new_exact_comments) == 1:
        recovered = new_exact_comments[0]
        payload["recovery"]["accepted"] = True
        payload["trigger"].update(
            {
                "action": "recovered",
                "body_matches_expected": True,
                "comment_id": recovered.get("id"),
                "created_at": recovered.get("created_at"),
                "url": recovered.get("html_url") or recovered.get("url"),
            }
        )
        payload["success"] = bool(payload["trigger"]["comment_id"] and payload["trigger"]["created_at"])
        payload["overall_status"] = "trigger_recovered" if payload["success"] else "trigger_recovery_invalid"
    else:
        payload["limitations"].append(
            limitation(
                "trigger_recovery_ambiguous",
                "POST failure recovery requires exactly one new exact @codex review comment",
                after_gh_exit=after_exit,
                after_gh_stderr=after_stderr.strip(),
                new_exact_comment_count=len(new_exact_comments),
            )
        )

final_exit, final_stdout, final_stderr = run_gh(
    ["pr", "view", pr, "--repo", repo, "--json", "headRefOid,baseRefOid,url,state,isDraft,number"]
)
final_metadata = load_json(final_stdout, {}) if final_exit == 0 else {}
final_head_sha = final_metadata.get("headRefOid") or ""
payload["final_head_sha"] = final_head_sha or None

if final_exit != 0 or not final_head_sha:
    payload["limitations"].append(
        limitation(
            "post_trigger_metadata_failed",
            "could not read PR head after trigger comment POST",
            gh_exit=final_exit,
            gh_stderr=final_stderr.strip(),
            severity="warning" if payload["success"] else "blocking",
        )
    )
    if not payload["success"]:
        payload["overall_status"] = "metadata_failed_after_trigger"
elif not head_matches(final_head_sha, expected_head_sha):
    payload["success"] = False
    payload["overall_status"] = "stale_head"
    payload["limitations"].append(
        limitation(
            "post_trigger_head_mismatch",
            "PR head changed after trigger comment POST",
            current_head_sha=final_head_sha,
            expected_head_sha=expected_head_sha,
        )
    )

emit(payload)
PY
