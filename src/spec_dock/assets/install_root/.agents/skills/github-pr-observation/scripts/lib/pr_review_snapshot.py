import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone


def fail_usage(parser):
    parser.print_usage(sys.stderr)
    raise SystemExit(64)


def parse_args(argv):
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--pr", required=True)
    parser.add_argument("--head-sha", default="")
    parser.add_argument("--trigger-comment-id", default="")
    parser.add_argument("--trigger-created-at", default="")
    parser.add_argument(
        "--body-mode",
        default="trigger-window-truncated",
        choices=("none", "trigger-window-truncated", "trigger-window-full", "out-only"),
    )
    parser.add_argument("--out", default="")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        raise SystemExit(0 if exc.code == 0 else 64) from exc
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo):
        fail_usage(parser)
    if not re.fullmatch(r"[1-9][0-9]*", args.pr):
        fail_usage(parser)
    if args.head_sha and not re.fullmatch(r"[0-9A-Fa-f]{7,64}", args.head_sha):
        fail_usage(parser)
    if args.trigger_comment_id and not re.fullmatch(r"[1-9][0-9]*", args.trigger_comment_id):
        fail_usage(parser)
    if args.trigger_created_at and not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(Z|[+-][0-9]{2}:[0-9]{2})?",
        args.trigger_created_at,
    ):
        fail_usage(parser)
    if args.out.startswith("-"):
        fail_usage(parser)
    return args


parsed_args = parse_args(sys.argv[1:])
repo = parsed_args.repo
owner = repo.split("/", 1)[0]
name = repo.split("/", 1)[1]
pr = int(parsed_args.pr)
expected_head_sha = parsed_args.head_sha or None
trigger_comment_id = (
    int(parsed_args.trigger_comment_id) if parsed_args.trigger_comment_id else None
)
trigger_created_at = parsed_args.trigger_created_at or None
body_mode = parsed_args.body_mode
out_dir = parsed_args.out

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
      reviewDecision
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
    review_decision = None
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
            return [], review_decision, {
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
            return [], review_decision, {
                "code": "thread_state_unavailable",
                "source": "graphql.reviewThreads",
                "severity": "blocking",
                "message": "fixed GraphQL review thread state returned non-JSON output",
            }
        try:
            pull_request = payload["data"]["repository"]["pullRequest"]
            if review_decision is None:
                review_decision = pull_request.get("reviewDecision")
            review_threads = pull_request["reviewThreads"]
            page_nodes = review_threads["nodes"]
        except (KeyError, TypeError):
            return [], review_decision, {
                "code": "thread_state_unavailable",
                "source": "graphql.reviewThreads",
                "severity": "blocking",
                "message": "fixed GraphQL review thread state schema was unavailable",
            }
        if isinstance(page_nodes, list):
            nodes.extend(page_nodes)
        page_info = review_threads.get("pageInfo") if isinstance(review_threads, dict) else {}
        if not isinstance(page_info, dict) or not page_info.get("hasNextPage"):
            return nodes, review_decision, None
        after = page_info.get("endCursor")
        if not after:
            return nodes, review_decision, {
                "code": "thread_state_partial",
                "source": "graphql.reviewThreads",
                "severity": "blocking",
                "message": "fixed GraphQL review thread pagination had no next cursor",
            }
    return nodes, review_decision, {
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


TRUSTED_CODEX_LOGINS = {
    "chatgpt-codex-connector[bot]",
    "codex",
}


def is_codex_authored(login):
    return str(login or "").lower() in TRUSTED_CODEX_LOGINS


def is_trigger_command_body(body):
    for line in str(body or "").splitlines():
        stripped = line.strip().lower()
        if not stripped:
            continue
        return stripped == "@codex review" or stripped.startswith("@codex review ")
    return False


def is_explicit_trigger_comment(comment):
    if trigger_comment_id is None:
        return False
    try:
        return int(comment.get("id") or 0) == trigger_comment_id
    except (TypeError, ValueError):
        return False


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


def numeric_id_sort_key(value):
    try:
        return (0, int(value))
    except (TypeError, ValueError):
        return (1, str(value or ""))


def signal_sort_key(signal):
    return (
        signal_time(signal),
        numeric_id_sort_key(signal.get("id")),
        int(signal.get("_api_index") or 0),
    )


def review_collapse_key(signal):
    return (
        signal_activity_time(signal) or "",
        numeric_id_sort_key(signal.get("id")),
        int(signal.get("_api_index") or 0),
    )


def is_after_trigger(signal):
    if trigger_created_at_dt is None:
        return False
    if signal.get("kind") == "issue_comment" and trigger_comment_id is not None:
        try:
            if int(signal.get("id") or 0) == trigger_comment_id:
                return False
        except (TypeError, ValueError):
            pass
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
        updated_at_dt = parse_iso8601_instant(signal.get("updated_at"))
        created_at_dt = parse_iso8601_instant(signal.get("created_at"))
        if (
            updated_at_dt is not None
            and updated_at_dt >= trigger_created_at_dt
            and created_at_dt is not None
            and created_at_dt < trigger_created_at_dt
        ):
            return True
        try:
            return int(signal.get("id") or 0) > trigger_comment_id
        except (TypeError, ValueError):
            return False
    return False


def body_hash(body):
    return hashlib.sha256(str(body or "").encode()).hexdigest()


def add_body_metadata(signal, body_state):
    raw_body = str(signal.pop("_raw_body", "") or "")
    signal["_raw_body_artifact"] = raw_body
    signal["_fallback_pass_raw_body"] = raw_body
    signal["_selected_full_body"] = raw_body
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


def item_id(item):
    return item.get("id") if isinstance(item, dict) else None


def compact_ids(items):
    ids = [item_id(item) for item in items]
    return [value for value in ids if value is not None]


def boundary_exclusion_reason(item):
    if not body_state["trigger_known"]:
        return "trigger_unknown"
    activity_at = signal_activity_time(item)
    if not activity_at:
        return "activity_time_missing"
    if not is_after_trigger(item):
        return "boundary_before_or_equal_trigger"
    return None


def summarize_signal_collection(items, selected_ids):
    boundary_exclusions = []
    for item in items:
        reason = boundary_exclusion_reason(item)
        if reason is not None:
            boundary_exclusions.append({"id": item.get("id"), "reason": reason})
    return {
        "fetched_count": len(items),
        "fetched_ids": compact_ids(items),
        "selected_ids": selected_ids,
        "boundary_before_excluded_count": len(boundary_exclusions),
        "boundary_before_excluded_ids": [
            item["id"] for item in boundary_exclusions if item.get("id") is not None
        ],
        "boundary_before_exclusion_reasons": boundary_exclusions,
    }


def thread_after_trigger(thread):
    if not body_state["trigger_known"]:
        return False
    activity_at = thread.get("activity_at") if isinstance(thread, dict) else None
    if not activity_at:
        return False
    activity_at_dt = parse_iso8601_instant(activity_at)
    return activity_at_dt is not None and activity_at_dt > trigger_created_at_dt


def summarize_thread_collection(items, selected_ids, current_unresolved_ids):
    boundary_exclusions = []
    for item in items:
        if not body_state["trigger_known"]:
            reason = "trigger_unknown"
        elif not item.get("activity_at"):
            reason = "activity_time_missing"
        elif not thread_after_trigger(item):
            reason = "boundary_before_or_equal_trigger"
        else:
            reason = None
        if reason is not None:
            boundary_exclusions.append({"id": item.get("id"), "reason": reason})
    return {
        "fetched_count": len(items),
        "fetched_ids": compact_ids(items),
        "selected_ids": selected_ids,
        "unresolved_count": len(current_unresolved_ids),
        "unresolved_ids": current_unresolved_ids,
        "boundary_before_excluded_count": len(boundary_exclusions),
        "boundary_before_excluded_ids": [
            item["id"] for item in boundary_exclusions if item.get("id") is not None
        ],
        "boundary_before_exclusion_reasons": boundary_exclusions,
    }


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
thread_nodes, review_decision, thread_limitation = gh_graphql_threads()
if thread_limitation:
    limitations.append(thread_limitation)

issue_comments = as_list(issue_comments_payload)
reviews = as_list(reviews_payload)
review_comments = as_list(review_comments_payload)
requested_reviewers = as_list(pull_payload, "requested_reviewers")
requested_teams = as_list(pull_payload, "requested_teams")
current_pr_head_sha = None
if isinstance(pull_payload, dict) and isinstance(pull_payload.get("head"), dict):
    current_pr_head_sha = pull_payload["head"].get("sha") or None

if trigger_comment_id and not trigger_created_at:
    for comment in issue_comments:
        try:
            if int(comment.get("id") or 0) == trigger_comment_id:
                trigger_created_at = comment.get("created_at")
                break
        except (TypeError, ValueError):
            continue
    if not trigger_created_at:
        limitations.append(
            {
                "code": "trigger_timestamp_unresolved",
                "source": "issue_comments",
                "severity": "informational",
                "message": "explicit trigger comment id did not resolve to an issue comment timestamp",
            }
        )

trigger_source = "none"
if trigger_comment_id and not trigger_created_at:
    trigger_source = "unknown"
elif trigger_comment_id or trigger_created_at:
    trigger_source = "explicit"
elif issue_comments:
    inferred_candidates = []
    for comment in issue_comments:
        body = str(comment.get("body") or "")
        if is_trigger_command_body(body):
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
            "updated_at": comment.get("updated_at"),
            "state": "commented",
            "trigger_command": is_explicit_trigger_comment(comment) or is_trigger_command_body(raw_body),
            "_raw_body": raw_body,
        }
    )

for review_index, review in enumerate(reviews):
    commit_id = review.get("commit_id")
    stale = bool(expected_head_sha and commit_id and not sha_prefix_matches(commit_id, expected_head_sha))
    signals.append(
        {
            "kind": "pull_review",
            "id": review.get("id"),
            "_api_index": review_index,
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
            "thread_id": comment.get("thread_id"),
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

review_decision_requires_review = str(review_decision or "").upper() == "REVIEW_REQUIRED"
review_decision_changes_requested = str(review_decision or "").upper() == "CHANGES_REQUESTED"

threads = []
thread_comment_states = {}
thread_states_by_thread_id = {}
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
    resolved = thread.get("isResolved")
    outdated = thread.get("isOutdated")
    if resolved is True:
        state = "resolved"
    elif resolved is False and outdated is True:
        state = "outdated"
    elif resolved is False and outdated is False:
        state = "unresolved"
    elif resolved is False:
        state = "unknown_outdated"
    else:
        state = "unknown"
    thread_id = thread.get("id")
    if thread_id is not None:
        thread_states_by_thread_id[str(thread_id)] = {
            "thread_id": thread_id,
            "state": state,
        }
    comment_ids = []
    for comment in comments:
        comment_id = comment.get("databaseId")
        if comment_id is None:
            comment_id = comment.get("id")
        if comment_id is not None:
            comment_ids.append(comment_id)
            thread_comment_states[str(comment_id)] = {
                "thread_id": thread_id,
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

signals.sort(key=signal_sort_key)
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
        if not thread_state and signal.get("thread_id") is not None:
            thread_state = thread_states_by_thread_id.get(str(signal.get("thread_id")))
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
    item.get("severity") == "blocking" for item in limitations
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


for signal in signals:
    signal["current_status_signal"] = is_current_status_signal(signal)
status_signals = [item for item in signals if item.get("current_status_signal")]
current_review_by_author = {}
for item in status_signals:
    if item.get("kind") != "pull_review":
        continue
    if item.get("state") == "dismissed":
        continue
    author_key = item.get("author") or f"id:{item.get('id')}"
    previous = current_review_by_author.get(author_key)
    if previous is None or review_collapse_key(item) >= review_collapse_key(previous):
        current_review_by_author[author_key] = item
active_review_signals = list(current_review_by_author.values())
active_comment_signals = [
    item
    for item in status_signals
    if item.get("kind") == "pull_review_comment"
    and item.get("thread_state") not in {"resolved", "outdated"}
]
selected_review_signals = [
    item
    for item in active_review_signals
    if item.get("codex_authored")
    and item.get("state") in {"commented", "approved", "changes_requested"}
]
selected_review_ids = [
    item.get("id") for item in selected_review_signals if item.get("id") is not None
]
selected_review_id_set = {str(value) for value in selected_review_ids}
selected_comment_signals = [
    item
    for item in active_comment_signals
    if item.get("review_id") is not None
    and str(item.get("review_id")) in selected_review_id_set
]
selected_review_comment_ids = [
    item.get("id") for item in selected_comment_signals if item.get("id") is not None
]
selected_thread_ids = []
for item in selected_comment_signals:
    thread_id = item.get("thread_id")
    if thread_id is not None and thread_id not in selected_thread_ids:
        selected_thread_ids.append(thread_id)
current_unresolved_thread_ids = [
    item.get("id")
    for item in threads
    if item.get("state") == "unresolved"
    and item.get("id") is not None
    and (not body_state["trigger_known"] or thread_after_trigger(item))
]
unresolved_thread_id_set = {
    str(item.get("id"))
    for item in threads
    if item.get("state") == "unresolved" and item.get("id") is not None
}
selected_unresolved_thread_ids = [
    thread_id
    for thread_id in selected_thread_ids
    if str(thread_id) in unresolved_thread_id_set
]
selected_unresolved_thread_id_set = {
    str(thread_id) for thread_id in selected_unresolved_thread_ids
}
carryover_non_outdated_unresolved_threads = [
    item
    for item in threads
    if item.get("state") == "unresolved"
    and item.get("id") is not None
    and str(item.get("id")) not in selected_unresolved_thread_id_set
]
carryover_unresolved_thread_ids = [
    item.get("id") for item in carryover_non_outdated_unresolved_threads
]
actionable_unresolved_thread_ids = list(selected_unresolved_thread_ids)
for thread_id in carryover_unresolved_thread_ids:
    if thread_id not in actionable_unresolved_thread_ids:
        actionable_unresolved_thread_ids.append(thread_id)

def selected_review_item(item):
    raw_body = str(item.get("_selected_full_body", "") or "")
    return {
        "id": item.get("id"),
        "author": item.get("author"),
        "state": item.get("state"),
        "submitted_at": item.get("submitted_at"),
        "commit_id": item.get("commit_id"),
        "stale": item.get("stale"),
        "body": raw_body,
        "body_sha256": item.get("body_sha256"),
        "body_original_length": len(raw_body),
        "body_collection_status": "present" if raw_body else "empty",
    }


def selected_review_comment_item(item):
    raw_body = str(item.get("_selected_full_body", "") or "")
    return {
        "id": item.get("id"),
        "review_id": item.get("review_id"),
        "thread_id": item.get("thread_id"),
        "thread_state": item.get("thread_state"),
        "author": item.get("author"),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
        "commit_id": item.get("commit_id"),
        "original_commit_id": item.get("original_commit_id"),
        "path": item.get("path"),
        "line": item.get("line"),
        "stale": item.get("stale"),
        "body": raw_body,
        "body_sha256": item.get("body_sha256"),
        "body_original_length": len(raw_body),
        "body_collection_status": "present" if raw_body else "empty",
    }


reviews_for_summary = [item for item in signals if item.get("kind") == "pull_review"]
review_comments_for_summary = [
    item for item in signals if item.get("kind") == "pull_review_comment"
]
review_collection_summary = {
    "reviews": summarize_signal_collection(reviews_for_summary, selected_review_ids),
    "review_comments": summarize_signal_collection(
        review_comments_for_summary,
        selected_review_comment_ids,
    ),
    "review_threads": summarize_thread_collection(
        threads,
        selected_thread_ids,
        current_unresolved_thread_ids,
    ),
}
review_collection_summary["review_threads"]["non_outdated_unresolved_ids"] = [
    item.get("id")
    for item in threads
    if item.get("state") == "unresolved" and item.get("id") is not None
]
review_collection_summary["review_threads"]["carryover_non_outdated_unresolved_ids"] = (
    carryover_unresolved_thread_ids
)


def normalized_body_text(value):
    return " ".join(str(value or "").strip().split()).casefold()


def is_strict_no_findings_issue_comment(item):
    raw_body = str(
        item.get("_fallback_pass_raw_body")
        or item.get("_raw_body_artifact")
        or item.get("body")
        or ""
    )
    allowed_full_bodies = {
        "no major issues found",
        "no major issues found.",
        "no major issues were found",
        "no major issues were found.",
        "codex review: didn't find any major issues. breezy!",
    }
    return normalized_body_text(raw_body) in allowed_full_bodies


current_codex_issue_comments = [
    item
    for item in signals
    if item.get("kind") == "issue_comment"
    and item.get("codex_authored")
    and item.get("current_status_signal")
]
latest_current_codex_issue_comment = (
    current_codex_issue_comments[-1] if current_codex_issue_comments else None
)
latest_current_codex_issue_comment_is_no_findings = (
    latest_current_codex_issue_comment is not None
    and is_strict_no_findings_issue_comment(latest_current_codex_issue_comment)
)
no_findings_source_ids = (
    [latest_current_codex_issue_comment.get("id")]
    if latest_current_codex_issue_comment_is_no_findings
    and latest_current_codex_issue_comment.get("id") is not None
    else []
)
stale_codex_head_context_present = any(
    item.get("codex_authored")
    and item.get("stale")
    and item.get("kind") in {"pull_review", "pull_review_comment"}
    and body_state["trigger_known"]
    and is_after_trigger(item)
    for item in signals
)
active_changes_requested_review_present = any(
    item.get("state") == "changes_requested" for item in active_review_signals
)
no_findings_completion_promotes = bool(
    expected_head_sha
    and current_pr_head_sha
    and sha_prefix_matches(current_pr_head_sha, expected_head_sha)
    and no_findings_source_ids
    and not stale_codex_head_context_present
    and not actionable_unresolved_thread_ids
    and not review_decision_changes_requested
    and not review_decision_requires_review
    and not active_changes_requested_review_present
    and not blocking_collection_failure
)
if selected_review_signals:
    lifecycle_status = "unresolved" if selected_thread_ids else "completed"
    completion_signal = "submitted_pull_request_review"
    lifecycle_confidence = "high"
elif no_findings_completion_promotes:
    lifecycle_status = "completed"
    completion_signal = "codex_no_findings_issue_comment"
    lifecycle_confidence = "medium"
elif current_codex_issue_comments:
    lifecycle_status = "fallback"
    completion_signal = "fallback_issue_comment"
    lifecycle_confidence = "low"
elif any(
    item.get("kind") == "pull_review"
    and item.get("codex_authored")
    and item.get("state") == "pending"
    and item.get("current_status_signal")
    for item in signals
):
    lifecycle_status = "pending"
    completion_signal = "none"
    lifecycle_confidence = "medium"
elif review_request_signals or review_decision_requires_review:
    lifecycle_status = "pending"
    completion_signal = "none"
    lifecycle_confidence = "medium"
elif blocking_collection_failure:
    lifecycle_status = "unknown"
    completion_signal = "none"
    lifecycle_confidence = "low"
else:
    lifecycle_status = "none"
    completion_signal = "none"
    lifecycle_confidence = "medium"
selected_changes_requested_reviews = [
    item for item in selected_review_signals if item.get("state") == "changes_requested"
]
selected_changes_requested_review_ids = [
    item.get("id") for item in selected_changes_requested_reviews if item.get("id") is not None
]
selected_changes_requested_review_id_set = {
    str(value) for value in selected_changes_requested_review_ids
}
selected_changes_requested_comments = [
    item
    for item in status_signals
    if item.get("review_id") is not None
    and str(item.get("review_id")) in selected_changes_requested_review_id_set
    and item.get("kind") == "pull_review_comment"
]
selected_changes_requested_comment_ids = [
    item.get("id") for item in selected_changes_requested_comments if item.get("id") is not None
]
selected_changes_requested_evidence = [
    {
        "kind": "pull_review",
        "id": item.get("id"),
        "state": item.get("state"),
    }
    for item in selected_changes_requested_reviews
]
selected_changes_requested_evidence.extend(
    {
        "kind": "pull_review_comment",
        "id": item.get("id"),
        "review_id": item.get("review_id"),
        "thread_id": item.get("thread_id"),
    }
    for item in selected_changes_requested_comments
)
pending_review_present = lifecycle_status == "pending"
blocking_limitation_present = bool(blocking_collection_failure)
selected_blocker_present = bool(selected_unresolved_thread_ids or selected_changes_requested_evidence)
explicit_completion_present = completion_signal in {
    "submitted_pull_request_review",
    "codex_no_findings_issue_comment",
}
fallback_issue_comment_present = completion_signal == "fallback_issue_comment"
if selected_blocker_present:
    no_completion_category = "selected_blocker"
elif explicit_completion_present:
    no_completion_category = "explicit_completion"
elif fallback_issue_comment_present:
    no_completion_category = "fallback_issue_comment"
elif pending_review_present:
    no_completion_category = "pending_review"
elif blocking_limitation_present:
    no_completion_category = "blocking_limitation"
else:
    no_completion_category = "missing_current_completion_signal"
no_completion_present = no_completion_category == "missing_current_completion_signal"
no_completion_evidence = {
    "present": no_completion_present,
    "category": no_completion_category,
    "reason": (
        "current_boundary_has_no_completion_or_blocking_signal"
        if no_completion_present
        else None
    ),
    "requires_wait_stability": no_completion_present,
    "promotes_top_level_status": False,
    "pending_review_present": pending_review_present,
    "blocking_limitation_present": blocking_limitation_present,
    "selected_blocker_present": selected_blocker_present,
    "explicit_completion_present": explicit_completion_present,
    "fallback_issue_comment_present": fallback_issue_comment_present,
}
codex_review_payload = {
    "lifecycle": {
        "status": lifecycle_status,
        "completion_signal": completion_signal,
        "confidence": lifecycle_confidence,
        "selected_review_ids": selected_review_ids,
        "selected_review_comment_ids": selected_review_comment_ids,
        "selected_review_thread_ids": selected_thread_ids,
        "trigger_source": trigger_source,
        "no_completion_evidence": no_completion_evidence,
    },
    "selected_reviews": [selected_review_item(item) for item in selected_review_signals],
    "selected_review_comments": [
        selected_review_comment_item(item) for item in selected_comment_signals
    ],
    "collection_summary": review_collection_summary,
}
for signal in signals:
    signal.pop("_api_index", None)
    signal.pop("_selected_full_body", None)

if blocking_collection_failure:
    status = "unknown"
elif current_unresolved_thread_ids:
    status = "unresolved"
elif any(item.get("state") == "changes_requested" for item in active_review_signals):
    status = "changes_requested"
elif review_decision_changes_requested:
    status = "changes_requested"
elif review_request_signals:
    status = "requested"
elif review_decision_requires_review:
    status = "requested"
elif any(item.get("state") == "commented" for item in active_review_signals) or active_comment_signals:
    status = "commented"
elif any(item.get("state") == "commented" and item.get("kind") == "issue_comment" for item in status_signals):
    status = "commented"
elif any(item.get("state") == "approved" for item in active_review_signals):
    status = "approved"
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
        "current_status_signal": item.get("current_status_signal"),
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


fallback_pass_source_ids = [
    item.get("id")
    for item in current_codex_issue_comments
    if item.get("id") is not None and is_strict_no_findings_issue_comment(item)
]
for signal in signals:
    signal.pop("_fallback_pass_raw_body", None)
fallback_pass_candidate = {
    "present": bool(completion_signal == "fallback_issue_comment" and fallback_pass_source_ids),
    "source": "issue_comment" if fallback_pass_source_ids else None,
    "source_ids": fallback_pass_source_ids,
    "reason": "current_boundary_no_major_issues_comment" if fallback_pass_source_ids else None,
    "promotes_top_level_status": False,
}
no_findings_completion_candidate = {
    "present": bool(no_findings_completion_promotes),
    "source": "issue_comment" if no_findings_source_ids else None,
    "source_ids": no_findings_source_ids,
    "reason": (
        "current_boundary_codex_no_findings_comment"
        if no_findings_completion_promotes
        else None
    ),
    "promotes_top_level_status": bool(no_findings_completion_promotes),
}
if selected_unresolved_thread_ids:
    decision_status_reason = "current_selected_unresolved_thread"
    decision_status = "human_gate"
    decision_action = "address_review_feedback"
elif selected_changes_requested_evidence:
    decision_status_reason = "current_selected_changes_requested"
    decision_status = "human_gate"
    decision_action = "address_review_feedback"
elif completion_signal == "fallback_issue_comment":
    decision_status_reason = "fallback_issue_comment_low_confidence"
    decision_status = "human_gate"
    decision_action = "manual_review_required_non_retryable"
elif blocking_collection_failure:
    decision_status_reason = "blocking_limitation"
    decision_status = "unknown"
    decision_action = "human_gate"
elif completion_signal == "none":
    decision_status_reason = "missing_current_completion_signal"
    decision_status = "unknown"
    decision_action = "wait_or_resume"
else:
    decision_status_reason = (
        "codex_no_findings_issue_comment"
        if completion_signal == "codex_no_findings_issue_comment"
        else "passed"
    )
    decision_status = "passed"
    decision_action = (
        "review_completion_observed"
        if completion_signal == "codex_no_findings_issue_comment"
        else "merge_prepared"
    )
decision_scope = (
    "current_trigger_boundary"
    if trigger_source == "explicit"
    else "inferred_current_boundary"
    if trigger_source == "inferred"
    else "unknown_current_boundary"
)
trigger_payload = {
    "source": trigger_source,
    "comment_id": trigger_comment_id,
    "created_at": trigger_created_at,
}
decision_source = {
    "scope": decision_scope,
    "trigger": trigger_payload,
    "expected_head_sha": expected_head_sha,
    "status": decision_status,
    "status_reason": decision_status_reason,
    "recommended_next_action": decision_action,
    "observation_complete": decision_status == "passed",
    "selected_review_ids": selected_review_ids,
    "selected_review_comment_ids": selected_review_comment_ids,
    "selected_review_thread_ids": selected_thread_ids,
    "selected_unresolved_thread_ids": selected_unresolved_thread_ids,
    "current_selected_unresolved_thread_ids": selected_unresolved_thread_ids,
    "current_selected_unresolved_count": len(selected_unresolved_thread_ids),
    "carryover_unresolved_thread_ids": carryover_unresolved_thread_ids,
    "carryover_unresolved_count": len(carryover_unresolved_thread_ids),
    "actionable_unresolved_thread_ids": actionable_unresolved_thread_ids,
    "actionable_unresolved_count": len(actionable_unresolved_thread_ids),
    "selected_unresolved_count": len(selected_unresolved_thread_ids),
    "selected_changes_requested_review_ids": selected_changes_requested_review_ids,
    "selected_changes_requested_review_comment_ids": selected_changes_requested_comment_ids,
    "selected_changes_requested_evidence": selected_changes_requested_evidence,
    "completion_signal": completion_signal,
    "confidence": lifecycle_confidence,
    "fallback_pass_candidate": fallback_pass_candidate,
    "no_findings_completion_candidate": no_findings_completion_candidate,
    "no_completion_evidence": no_completion_evidence,
    "blocking_limitations": [
        item.get("code")
        for item in limitations
        if item.get("severity") == "blocking"
    ],
}
decision_fingerprint = hashlib.sha256(
    json.dumps(decision_source, sort_keys=True, separators=(",", ":")).encode()
).hexdigest()
decision_payload = dict(decision_source)
decision_payload["fingerprint"] = decision_fingerprint

audit_fingerprint_source = {
    "status": status,
    "signals": [fingerprint_signal(item) for item in signals],
    "codex_authored": [
        fingerprint_signal(item)
        for item in signals
        if item.get("codex_authored")
    ],
    "review_requests": review_request_signals,
    "review_decision": review_decision,
    "threads": [fingerprint_thread(item) for item in threads],
    "body_mode": {
        "mode": body_mode,
        "included_count": body_state["included_count"],
        "included_chars": body_state["included_chars"],
        "item_count_omitted": body_state["item_count_omitted"],
        "body_chars_omitted": body_state["body_chars_omitted"],
    },
    "codex_review": codex_review_payload,
    "limitations": limitations,
}
audit_fingerprint = hashlib.sha256(
    json.dumps(audit_fingerprint_source, sort_keys=True, separators=(",", ":")).encode()
).hexdigest()
fingerprint = audit_fingerprint

review_current_payload = {
    "scope": decision_scope,
    "signals": status_signals,
    "codex_authored": [
        item
        for item in status_signals + review_request_signals
        if item.get("codex_authored")
    ],
    "selected_reviews": [selected_review_item(item) for item in selected_review_signals],
    "selected_review_comments": [
        selected_review_comment_item(item) for item in selected_comment_signals
    ],
    "selected_review_ids": selected_review_ids,
    "selected_review_comment_ids": selected_review_comment_ids,
    "selected_thread_ids": selected_thread_ids,
    "selected_unresolved_thread_ids": selected_unresolved_thread_ids,
    "current_selected_unresolved_thread_ids": selected_unresolved_thread_ids,
    "current_selected_unresolved_count": len(selected_unresolved_thread_ids),
    "carryover_non_outdated_unresolved_thread_ids": carryover_unresolved_thread_ids,
    "carryover_non_outdated_unresolved_count": len(carryover_unresolved_thread_ids),
    "actionable_unresolved_thread_ids": actionable_unresolved_thread_ids,
    "actionable_unresolved_count": len(actionable_unresolved_thread_ids),
    "selected_changes_requested_evidence": selected_changes_requested_evidence,
}
review_audit_payload = {
    "scope": "all_fetched",
    "decision_authoritative": False,
    "signals": signals,
    "codex_authored": [
        item for item in signals + review_request_signals if item.get("codex_authored")
    ],
    "threads": thread_counts,
    "non_outdated_unresolved_thread_ids": review_collection_summary["review_threads"][
        "non_outdated_unresolved_ids"
    ],
    "unknown_outdated_unresolved_thread_ids": [
        item.get("id")
        for item in threads
        if item.get("state") == "unknown_outdated" and item.get("id") is not None
    ],
    "fingerprint": audit_fingerprint,
}

payload = {
    "script": "fetch_pr_review_snapshot.sh",
    "collector": "s04",
    "observed_at": now_iso(),
    "repo": repo,
    "pr": pr,
    "expected_head_sha": expected_head_sha,
    "fingerprint": fingerprint,
    "decision_fingerprint": decision_fingerprint,
    "audit_fingerprint": audit_fingerprint,
    "decision": decision_payload,
    "review": {
        "collector": "s04",
        "status": status,
        "progress_status": status,
        "statuses": STATUSES,
        "signals": signals,
        "signals_scope": "all_fetched",
        "signals_decision_authoritative": False,
        "review_requests": review_request_signals,
        "review_decision": review_decision,
        "codex_authored": [
            item for item in signals + review_request_signals if item.get("codex_authored")
        ],
        "codex_authored_scope": "all_fetched",
        "codex_authored_decision_authoritative": False,
        "summary": counts,
        "threads": thread_counts,
        "threads_scope": "all_fetched",
        "threads_decision_authoritative": False,
        "current": review_current_payload,
        "audit": review_audit_payload,
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
        "codex_review": codex_review_payload,
    },
    "codex_review": codex_review_payload,
    "trigger": trigger_payload,
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
