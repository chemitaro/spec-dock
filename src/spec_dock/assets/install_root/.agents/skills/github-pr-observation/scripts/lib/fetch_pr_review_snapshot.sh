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
    "requested",
    "commented",
    "approved",
    "changes_requested",
    "unresolved",
]
ITEM_BODY_CAP = 64
TOTAL_BODY_CAP = 160
ITEM_COUNT_CAP = 4


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
          comments(first: 20) {
            nodes {
              id
              databaseId
              author { login }
              createdAt
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
    return "commented" if normalized else "commented"


def signal_time(signal):
    return signal.get("created_at") or signal.get("submitted_at") or ""


def is_after_trigger(signal):
    if not trigger_created_at:
        return False
    created_at = signal_time(signal)
    if not created_at:
        return False
    if created_at > trigger_created_at:
        return True
    if created_at < trigger_created_at:
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
            "commit_id": commit_id,
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
for thread in thread_nodes:
    comments = thread_comment_nodes(thread)
    first_comment = comments[0] if comments else {}
    resolved = bool(thread.get("isResolved"))
    outdated = bool(thread.get("isOutdated"))
    state = "resolved" if resolved else "outdated" if outdated else "unresolved"
    threads.append(
        {
            "id": thread.get("id"),
            "state": state,
            "is_resolved": resolved,
            "is_outdated": outdated,
            "comment_count": len(comments),
            "first_comment_id": first_comment.get("databaseId") or first_comment.get("id"),
            "first_comment_author": user_login(first_comment),
            "first_comment_created_at": first_comment.get("createdAt"),
        }
    )

signals.sort(key=lambda item: (signal_time(item), str(item.get("id") or "")))
body_state = {
    "trigger_known": trigger_source in {"explicit", "inferred"} and bool(trigger_created_at),
    "included_count": 0,
    "included_chars": 0,
    "item_count_omitted": 0,
    "body_chars_omitted": 0,
}
for signal in signals:
    add_body_metadata(signal, body_state)

raw_body_artifacts = [
    {
        "kind": item.get("kind"),
        "id": item.get("id"),
        "body_sha256": item.get("body_sha256"),
        "body": item.get("_raw_body_artifact"),
    }
    for item in signals
    if body_state["trigger_known"] and is_after_trigger(item)
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

status_signals = [
    item
    for item in signals
    if not (item.get("kind") == "issue_comment" and item.get("trigger_command"))
]

if blocking_collection_failure:
    status = "unknown"
elif thread_counts["unresolved"] > 0:
    status = "unresolved"
elif any(item.get("state") == "changes_requested" and not item.get("stale") for item in status_signals):
    status = "changes_requested"
elif review_request_signals:
    status = "requested"
elif any(item.get("state") == "commented" and item.get("kind") != "issue_comment" for item in status_signals):
    status = "commented"
elif any(item.get("state") == "approved" and not item.get("stale") for item in status_signals):
    status = "approved"
elif status_signals:
    status = "commented"
else:
    status = "none"

fingerprint_source = {
    "status": status,
    "signal_hashes": [item.get("body_sha256") for item in signals],
    "signal_states": [item.get("state") for item in signals],
    "review_requests": review_request_signals,
    "threads": [
        {"id": item.get("id"), "state": item.get("state")}
        for item in threads
    ],
    "limitations": [item.get("code") for item in limitations],
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
