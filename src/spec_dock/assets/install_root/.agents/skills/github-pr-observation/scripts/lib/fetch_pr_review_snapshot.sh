#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
usage: fetch_pr_review_snapshot.sh --repo OWNER/REPO --pr NUMBER [options]

Options:
  --head-sha SHA
  --trigger-comment-id NUMBER
  --trigger-created-at ISO8601
  --body-mode none|trigger-window-truncated|trigger-window-full|out-only
  --out DIR

Collects issue comments, pull reviews, inline review comments, review requests,
and fixed GraphQL review thread state. The script accepts only this fixed
read-only contract and does not accept caller-provided API endpoints, GraphQL
queries, gh arguments, jq expressions, headers, bodies, or methods.
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

owner="${repo%%/*}"
name="${repo#*/}"

OBS_REPO="$repo" \
OBS_OWNER="$owner" \
OBS_NAME="$name" \
OBS_PR="$pr" \
OBS_HEAD_SHA="$head_sha" \
OBS_TRIGGER_COMMENT_ID="$trigger_comment_id" \
OBS_TRIGGER_CREATED_AT="$trigger_created_at" \
OBS_BODY_MODE="$body_mode" \
OBS_OUT_DIR="$out_dir" \
python3 - <<'PY'
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone

repo = os.environ["OBS_REPO"]
owner = os.environ["OBS_OWNER"]
name = os.environ["OBS_NAME"]
pr = int(os.environ["OBS_PR"])
expected_head_sha = os.environ["OBS_HEAD_SHA"] or None
trigger_comment_id = int(os.environ["OBS_TRIGGER_COMMENT_ID"]) if os.environ["OBS_TRIGGER_COMMENT_ID"] else None
trigger_created_at = os.environ["OBS_TRIGGER_CREATED_AT"] or None
body_mode = os.environ["OBS_BODY_MODE"]
out_dir = os.environ["OBS_OUT_DIR"]

STATUSES = [
    "unknown",
    "none",
    "pending",
    "requested",
    "commented",
    "approved",
    "changes_requested",
    "unresolved",
    "dismissed",
]
ITEM_BODY_CAP = 12000
TOTAL_BODY_CAP = 120000
ITEM_COUNT_CAP = 50


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


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


def gh_graphql_threads():
    query = """
query($owner: String!, $name: String!, $number: Int!, $after: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewThreads(first: 100, after: $after) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          isResolved
          isOutdated
          comments(last: 100) {
            nodes {
              id
              databaseId
              author { login }
              createdAt
              updatedAt
              body
            }
          }
        }
      }
    }
  }
}
""".strip()
    nodes = []
    after = None
    for _ in range(100):
        command = [
            "gh",
            "api",
            "graphql",
            "-F",
            "owner=" + owner,
            "-F",
            "name=" + name,
            "-F",
            "number=" + str(pr),
            "-f",
            "query=" + query,
        ]
        if after:
            command.extend(["-F", "after=" + after])
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            return [], {
                "code": "thread_state_unavailable",
                "source": "graphql.reviewThreads",
                "severity": "blocking",
                "message": "fixed GraphQL review thread state collection failed",
                "exit_code": completed.returncode,
                "stderr_sha256": hashlib.sha256(completed.stderr.encode()).hexdigest(),
            }
        try:
            payload = json.loads(completed.stdout or "{}")
        except json.JSONDecodeError:
            return [], {
                "code": "thread_state_unavailable",
                "source": "graphql.reviewThreads",
                "severity": "blocking",
                "message": "fixed GraphQL review thread state returned non-JSON output",
            }
        try:
            review_threads = payload["data"]["repository"]["pullRequest"]["reviewThreads"]
            page_nodes = review_threads["nodes"]
        except (KeyError, TypeError):
            return [], {
                "code": "thread_state_unavailable",
                "source": "graphql.reviewThreads",
                "severity": "blocking",
                "message": "fixed GraphQL review thread state schema was unavailable",
            }
        if isinstance(page_nodes, list):
            nodes.extend(page_nodes)
        page_info = review_threads.get("pageInfo") if isinstance(review_threads, dict) else {}
        if not isinstance(page_info, dict) or not page_info.get("hasNextPage"):
            return nodes, None
        after = page_info.get("endCursor")
        if not after:
            return nodes, {
                "code": "thread_state_partial",
                "source": "graphql.reviewThreads",
                "severity": "blocking",
                "message": "fixed GraphQL review thread pagination had no next cursor",
            }
    return nodes, {
        "code": "thread_state_partial",
        "source": "graphql.reviewThreads",
        "severity": "blocking",
        "message": "fixed GraphQL review thread pagination exceeded page limit",
    }


def as_list(payload, key=None):
    if key is not None and isinstance(payload, dict):
        value = payload.get(key)
        return value if isinstance(value, list) else []
    return payload if isinstance(payload, list) else []


def user_login(payload):
    user = payload.get("user") if isinstance(payload, dict) else None
    if isinstance(user, dict):
        return user.get("login")
    author = payload.get("author") if isinstance(payload, dict) else None
    if isinstance(author, dict):
        return author.get("login")
    return None


def is_codex_authored(login):
    return "codex" in str(login or "").lower()


def is_trigger_command_body(body):
    return "@codex review" in str(body or "").lower()


def sha_prefix_matches(left, right):
    if not left or not right:
        return True
    left_lower = str(left).lower()
    right_lower = str(right).lower()
    return left_lower.startswith(right_lower) or right_lower.startswith(left_lower)


def normalize_review_state(state):
    normalized = str(state or "").lower()
    if normalized == "approved":
        return "approved"
    if normalized == "changes_requested":
        return "changes_requested"
    if normalized == "commented":
        return "commented"
    if normalized == "dismissed":
        return "dismissed"
    if normalized == "pending":
        return "pending"
    return "unknown"


def signal_time(signal):
    return signal.get("created_at") or signal.get("submitted_at") or ""


def parse_iso8601_instant(value):
    if not value:
        return None
    normalized = str(value)
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def latest_iso8601_value(values):
    latest_value = None
    latest_dt = None
    for value in values:
        parsed = parse_iso8601_instant(value)
        if parsed is None:
            continue
        if latest_dt is None or parsed > latest_dt:
            latest_dt = parsed
            latest_value = value
    return latest_value


def signal_activity_time(signal):
    return latest_iso8601_value(
        (signal.get("created_at"), signal.get("submitted_at"), signal.get("updated_at"))
    )


def is_after_trigger(signal):
    if trigger_created_at_dt is None:
        return False
    activity_at = signal_activity_time(signal)
    if not activity_at:
        return False
    activity_at_dt = parse_iso8601_instant(activity_at)
    if activity_at_dt is None:
        return False
    if activity_at_dt > trigger_created_at_dt:
        return True
    if activity_at_dt < trigger_created_at_dt:
        return False
    if signal.get("kind") == "issue_comment" and trigger_comment_id is not None:
        try:
            return int(signal.get("id") or 0) > trigger_comment_id
        except (TypeError, ValueError):
            return False
    return True


def body_hash(body):
    return hashlib.sha256(str(body or "").encode()).hexdigest()


def add_body_metadata(signal, body_state):
    raw_body = str(signal.pop("_raw_body", "") or "")
    signal["_raw_body_artifact"] = raw_body
    signal["body_sha256"] = body_hash(raw_body)
    signal["body_original_length"] = len(raw_body)
    signal["body_truncated"] = False
    include_candidate = body_state["trigger_known"] and is_after_trigger(signal)
    if body_mode == "none":
        signal["omitted_reason"] = "body_mode_none"
        return
    if body_mode == "out-only":
        signal["omitted_reason"] = "body_mode_out_only"
        return
    if not include_candidate:
        signal["omitted_reason"] = "outside_trigger_window" if body_state["trigger_known"] else "trigger_unknown"
        return
    if body_mode == "trigger-window-full":
        signal["body"] = raw_body
        body_state["included_count"] += 1
        body_state["included_chars"] += len(raw_body)
        return
    if body_state["included_count"] >= ITEM_COUNT_CAP:
        signal["omitted_reason"] = "item_count_cap"
        body_state["item_count_omitted"] += 1
        body_state["body_chars_omitted"] += len(raw_body)
        return
    remaining_total = TOTAL_BODY_CAP - body_state["included_chars"]
    if remaining_total <= 0:
        signal["omitted_reason"] = "total_body_char_cap"
        body_state["item_count_omitted"] += 1
        body_state["body_chars_omitted"] += len(raw_body)
        return
    allowed = min(ITEM_BODY_CAP, remaining_total)
    if len(raw_body) > allowed:
        signal["body"] = raw_body[:allowed]
        signal["body_truncated"] = True
        body_state["body_chars_omitted"] += len(raw_body) - allowed
    else:
        signal["body"] = raw_body
    body_state["included_count"] += 1
    body_state["included_chars"] += len(signal.get("body", ""))


def thread_comment_nodes(thread):
    comments = thread.get("comments") if isinstance(thread, dict) else None
    nodes = comments.get("nodes") if isinstance(comments, dict) else None
    return nodes if isinstance(nodes, list) else []


limitations = []
issue_comments_payload, limitation = gh_api(f"repos/{repo}/issues/{pr}/comments")
if limitation:
    limitations.append(limitation)
    issue_comments_payload = []
reviews_payload, limitation = gh_api(f"repos/{repo}/pulls/{pr}/reviews")
if limitation:
    limitations.append(limitation)
    reviews_payload = []
review_comments_payload, limitation = gh_api(f"repos/{repo}/pulls/{pr}/comments")
if limitation:
    limitations.append(limitation)
    review_comments_payload = []
pull_payload, limitation = gh_api(f"repos/{repo}/pulls/{pr}")
if limitation:
    limitations.append(limitation)
    pull_payload = {}
thread_nodes, thread_limitation = gh_graphql_threads()
if thread_limitation:
    limitations.append(thread_limitation)

issue_comments = as_list(issue_comments_payload)
reviews = as_list(reviews_payload)
review_comments = as_list(review_comments_payload)
requested_reviewers = as_list(pull_payload, "requested_reviewers")
requested_teams = as_list(pull_payload, "requested_teams")

trigger_source = "none"
if trigger_comment_id or trigger_created_at:
    trigger_source = "explicit"
elif issue_comments:
    inferred_candidates = []
    for comment in issue_comments:
        body = str(comment.get("body") or "")
        if "@codex review" in body.lower():
            inferred_candidates.append(comment)
    if inferred_candidates:
        inferred_candidates.sort(key=lambda item: (str(item.get("created_at") or ""), int(item.get("id") or 0)))
        latest = inferred_candidates[-1]
        trigger_comment_id = int(latest.get("id")) if latest.get("id") is not None else None
        trigger_created_at = latest.get("created_at")
        trigger_source = "inferred"
        limitations.append(
            {
                "code": "trigger_inferred",
                "source": "issue_comments",
                "severity": "informational",
                "message": "latest @codex review issue comment was inferred as trigger",
            }
        )
    else:
        trigger_source = "unknown"
        limitations.append(
            {
                "code": "trigger_unknown",
                "source": "issue_comments",
                "severity": "informational",
                "message": "no explicit trigger and no @codex review comment were available",
            }
        )
else:
    trigger_source = "unknown"
    limitations.append(
        {
            "code": "trigger_unknown",
            "source": "issue_comments",
            "severity": "informational",
            "message": "no explicit trigger and no issue comments were available",
        }
    )

trigger_created_at_dt = parse_iso8601_instant(trigger_created_at)
if trigger_created_at and trigger_created_at_dt is None:
    limitations.append(
        {
            "code": "trigger_timestamp_unparseable",
            "source": "trigger_created_at",
            "severity": "blocking",
            "message": "trigger timestamp could not be parsed as an aware instant",
        }
    )

signals = []
for comment in issue_comments:
    raw_body = comment.get("body") or ""
    signals.append(
        {
            "kind": "issue_comment",
            "id": comment.get("id"),
            "author": user_login(comment),
            "codex_authored": is_codex_authored(user_login(comment)),
            "created_at": comment.get("created_at"),
            "state": "commented",
            "trigger_command": is_trigger_command_body(raw_body),
            "_raw_body": raw_body,
        }
    )

for review in reviews:
    commit_id = review.get("commit_id")
    stale = bool(expected_head_sha and commit_id and not sha_prefix_matches(commit_id, expected_head_sha))
    signals.append(
        {
            "kind": "pull_review",
            "id": review.get("id"),
            "author": user_login(review),
            "codex_authored": is_codex_authored(user_login(review)),
            "submitted_at": review.get("submitted_at"),
            "commit_id": commit_id,
            "stale": stale,
            "state": normalize_review_state(review.get("state")),
            "_raw_body": review.get("body") or "",
        }
    )

for comment in review_comments:
    commit_id = comment.get("commit_id")
    stale = bool(expected_head_sha and commit_id and not sha_prefix_matches(commit_id, expected_head_sha))
    signals.append(
        {
            "kind": "pull_review_comment",
            "id": comment.get("id"),
            "review_id": comment.get("pull_request_review_id"),
            "author": user_login(comment),
            "codex_authored": is_codex_authored(user_login(comment)),
            "created_at": comment.get("created_at"),
            "updated_at": comment.get("updated_at"),
            "commit_id": commit_id,
            "original_commit_id": comment.get("original_commit_id"),
            "path": comment.get("path"),
            "line": comment.get("line"),
            "stale": stale,
            "state": "commented",
            "_raw_body": comment.get("body") or "",
        }
    )

review_request_signals = []
for reviewer in requested_reviewers:
    login = reviewer.get("login") if isinstance(reviewer, dict) else None
    review_request_signals.append(
        {
            "kind": "review_request",
            "target_type": "user",
            "target": login,
            "codex_authored": is_codex_authored(login),
            "state": "requested",
        }
    )
for team in requested_teams:
    slug = team.get("slug") if isinstance(team, dict) else None
    review_request_signals.append(
        {
            "kind": "review_request",
            "target_type": "team",
            "target": slug,
            "codex_authored": False,
            "state": "requested",
        }
    )

threads = []
thread_comment_states = {}
for thread in thread_nodes:
    comments = thread_comment_nodes(thread)
    first_comment = comments[0] if comments else {}
    latest_comment_created_at = latest_iso8601_value(
        comment.get("createdAt") for comment in comments
    )
    latest_comment_updated_at = latest_iso8601_value(
        comment.get("updatedAt") for comment in comments
    )
    activity_at = latest_iso8601_value(
        timestamp
        for comment in comments
        for timestamp in (comment.get("createdAt"), comment.get("updatedAt"))
    )
    resolved = bool(thread.get("isResolved"))
    outdated = bool(thread.get("isOutdated"))
    state = "resolved" if resolved else "outdated" if outdated else "unresolved"
    comment_ids = []
    for comment in comments:
        comment_id = comment.get("databaseId")
        if comment_id is None:
            comment_id = comment.get("id")
        if comment_id is not None:
            comment_ids.append(comment_id)
            thread_comment_states[str(comment_id)] = {
                "thread_id": thread.get("id"),
                "state": state,
            }
    threads.append(
        {
            "id": thread.get("id"),
            "state": state,
            "is_resolved": resolved,
            "is_outdated": outdated,
            "comment_count": len(comments),
            "comment_ids": comment_ids,
            "first_comment_id": first_comment.get("databaseId") or first_comment.get("id"),
            "first_comment_author": user_login(first_comment),
            "first_comment_created_at": first_comment.get("createdAt"),
            "latest_comment_created_at": latest_comment_created_at,
            "latest_comment_updated_at": latest_comment_updated_at,
            "activity_at": activity_at,
        }
    )

signals.sort(key=lambda item: (signal_time(item), str(item.get("id") or "")))
body_state = {
    "trigger_known": trigger_source in {"explicit", "inferred"} and trigger_created_at_dt is not None,
    "included_count": 0,
    "included_chars": 0,
    "item_count_omitted": 0,
    "body_chars_omitted": 0,
}
for signal in signals:
    add_body_metadata(signal, body_state)
    if signal.get("kind") == "pull_review_comment":
        thread_state = thread_comment_states.get(str(signal.get("id")))
        if thread_state:
            signal["thread_id"] = thread_state.get("thread_id")
            signal["thread_state"] = thread_state.get("state")

raw_body_artifacts = [
    {
        "kind": item.get("kind"),
        "id": item.get("id"),
        "body_sha256": item.get("body_sha256"),
        "body": item.get("_raw_body_artifact"),
    }
    for item in signals
    if body_mode == "out-only" and body_state["trigger_known"] and is_after_trigger(item)
]
for signal in signals:
    signal.pop("_raw_body_artifact", None)

if body_mode == "trigger-window-full":
    limitations.append(
        {
            "code": "body_mode_full_stdout_risk",
            "source": "body_mode",
            "severity": "informational",
            "message": "trigger-window-full may produce large stdout JSON",
        }
    )

blocking_collection_failure = any(
    item.get("code") in {
        "github_api_collection_failed",
        "github_api_schema_unavailable",
        "thread_state_unavailable",
        "trigger_timestamp_unparseable",
    }
    and item.get("severity") == "blocking"
    for item in limitations
)

counts = {
    "all": {
        "total": len(signals) + len(review_request_signals),
        "issue_comments": sum(1 for item in signals if item.get("kind") == "issue_comment"),
        "reviews": sum(1 for item in signals if item.get("kind") == "pull_review"),
        "review_comments": sum(1 for item in signals if item.get("kind") == "pull_review_comment"),
        "review_requests": len(review_request_signals),
    },
    "codex_authored": {
        "total": sum(1 for item in signals if item.get("codex_authored"))
        + sum(1 for item in review_request_signals if item.get("codex_authored")),
    },
}
thread_counts = {
    "total": len(threads),
    "unresolved": sum(1 for item in threads if item.get("state") == "unresolved"),
    "resolved": sum(1 for item in threads if item.get("state") == "resolved"),
    "outdated": sum(1 for item in threads if item.get("state") == "outdated"),
    "state_available": thread_limitation is None,
    "items": threads,
}

def is_current_status_signal(item):
    if item.get("kind") == "issue_comment" and item.get("trigger_command"):
        return False
    if item.get("stale"):
        return False
    if trigger_source in {"explicit", "inferred"}:
        return body_state["trigger_known"] and is_after_trigger(item)
    return item.get("kind") in {"pull_review", "pull_review_comment"} and bool(expected_head_sha)


status_signals = [item for item in signals if is_current_status_signal(item)]
current_review_by_author = {}
for item in status_signals:
    if item.get("kind") != "pull_review":
        continue
    if item.get("state") == "dismissed":
        continue
    author_key = item.get("author") or f"id:{item.get('id')}"
    previous = current_review_by_author.get(author_key)
    if previous is None or (signal_activity_time(item) or "") >= (signal_activity_time(previous) or ""):
        current_review_by_author[author_key] = item
active_review_signals = list(current_review_by_author.values())
active_comment_signals = [
    item
    for item in status_signals
    if item.get("kind") == "pull_review_comment"
    and item.get("thread_state") not in {"resolved", "outdated"}
]

if blocking_collection_failure:
    status = "unknown"
elif any(item.get("state") == "unresolved" for item in threads):
    status = "unresolved"
elif any(item.get("state") == "changes_requested" for item in active_review_signals):
    status = "changes_requested"
elif review_request_signals:
    status = "requested"
elif any(item.get("state") == "commented" for item in active_review_signals) or active_comment_signals:
    status = "commented"
elif any(item.get("state") == "approved" for item in active_review_signals):
    status = "approved"
elif any(item.get("state") == "commented" and item.get("kind") == "issue_comment" for item in status_signals):
    status = "commented"
elif any(item.get("state") == "pending" for item in status_signals):
    status = "pending"
elif any(item.get("state") == "unknown" for item in status_signals):
    status = "unknown"
else:
    status = "none"

def fingerprint_signal(item):
    return {
        "kind": item.get("kind"),
        "id": item.get("id"),
        "review_id": item.get("review_id"),
        "author": item.get("author"),
        "codex_authored": item.get("codex_authored"),
        "created_at": item.get("created_at"),
        "submitted_at": item.get("submitted_at"),
        "updated_at": item.get("updated_at"),
        "activity_at": signal_activity_time(item),
        "state": item.get("state"),
        "commit_id": item.get("commit_id"),
        "original_commit_id": item.get("original_commit_id"),
        "stale": item.get("stale"),
        "trigger_command": item.get("trigger_command"),
        "path": item.get("path"),
        "line": item.get("line"),
        "thread_id": item.get("thread_id"),
        "thread_state": item.get("thread_state"),
        "body_sha256": item.get("body_sha256"),
        "body_truncated": item.get("body_truncated"),
        "body_original_length": item.get("body_original_length"),
        "omitted_reason": item.get("omitted_reason"),
    }


def fingerprint_thread(item):
    return {
        "id": item.get("id"),
        "state": item.get("state"),
        "is_resolved": item.get("is_resolved"),
        "is_outdated": item.get("is_outdated"),
        "comment_count": item.get("comment_count"),
        "comment_ids": item.get("comment_ids"),
        "first_comment_id": item.get("first_comment_id"),
        "first_comment_created_at": item.get("first_comment_created_at"),
        "latest_comment_created_at": item.get("latest_comment_created_at"),
        "latest_comment_updated_at": item.get("latest_comment_updated_at"),
        "activity_at": item.get("activity_at"),
    }


fingerprint_source = {
    "status": status,
    "signals": [fingerprint_signal(item) for item in signals],
    "codex_authored": [
        fingerprint_signal(item)
        for item in signals
        if item.get("codex_authored")
    ],
    "review_requests": review_request_signals,
    "threads": [fingerprint_thread(item) for item in threads],
    "body_mode": {
        "mode": body_mode,
        "included_count": body_state["included_count"],
        "included_chars": body_state["included_chars"],
        "item_count_omitted": body_state["item_count_omitted"],
        "body_chars_omitted": body_state["body_chars_omitted"],
    },
    "limitations": limitations,
}
fingerprint = hashlib.sha256(
    json.dumps(fingerprint_source, sort_keys=True, separators=(",", ":")).encode()
).hexdigest()

payload = {
    "script": "fetch_pr_review_snapshot.sh",
    "collector": "s04",
    "observed_at": now_iso(),
    "repo": repo,
    "pr": pr,
    "expected_head_sha": expected_head_sha,
    "fingerprint": fingerprint,
    "review": {
        "collector": "s04",
        "status": status,
        "progress_status": status,
        "statuses": STATUSES,
        "signals": signals,
        "review_requests": review_request_signals,
        "codex_authored": [
            item for item in signals + review_request_signals if item.get("codex_authored")
        ],
        "summary": counts,
        "threads": thread_counts,
        "body_mode": {
            "mode": body_mode,
            "item_body_char_cap": None if body_mode == "trigger-window-full" else ITEM_BODY_CAP,
            "total_body_char_cap": None if body_mode == "trigger-window-full" else TOTAL_BODY_CAP,
            "item_count_cap": None if body_mode == "trigger-window-full" else ITEM_COUNT_CAP,
            "included_count": body_state["included_count"],
            "included_chars": body_state["included_chars"],
            "item_count_omitted": body_state["item_count_omitted"],
            "body_chars_omitted": body_state["body_chars_omitted"],
        },
    },
    "trigger": {
        "source": trigger_source,
        "comment_id": trigger_comment_id,
        "created_at": trigger_created_at,
    },
    "limitations": limitations,
}

if out_dir:
    os.makedirs(os.path.join(out_dir, "raw"), exist_ok=True)
    with open(os.path.join(out_dir, "raw", "review_bodies.json"), "w", encoding="utf-8") as handle:
        json.dump(
            raw_body_artifacts,
            handle,
            sort_keys=True,
            separators=(",", ":"),
        )

print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
PY
