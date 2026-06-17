---
種別: disc
ID: "20260616t225521z-14-disc-missed-p2-reserve-next-observation-poll"
タイトル: "Missed P2 review: reserve time for the next observation poll"
状態: "proposed"
作成者: "orchestrator"
最終更新: "2026-06-17"
親: ["iss-00187-actions-pr-observation-ci-state"]
関連: ["https://github.com/chemitaro/spec-dock/pull/190", "PR review comment 3422572159"]
authority: "proposed"
derived_from: ["PR review comment 3422572159", "/private/tmp/spec-dock-pr190-observation-bb50b7a2/result.json", "deep-consultant 019ed29f-a04f-7b61-8c72-4df37a730ad0"]
reflected_to: []
---

# Missed P2 review: reserve time for the next observation poll

## Summary

PR review comment `3422572159` is valid and should be fixed.

The review points at `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py:1438`, where the wait loop sleeps until the deadline without reserving enough time for the next snapshot poll. If the current poll is non-terminal only because quiet / same-fingerprint stability has not been reached, the loop can consume the remaining deadline in sleep, then start a final snapshot with only a tiny budget. That final snapshot can timeout and overwrite a previously meaningful latest payload with a less useful timeout result.

This is not a deliberate no-fix decision. The prior implementation did not address this review. It passed the existing full unit file, but the existing test shape did not prove the edge case where the first meaningful payload is followed by an under-budget final poll.

## Observed Facts

- PR: `https://github.com/chemitaro/spec-dock/pull/190`
- Head: `bb50b7a27144dc1a5af2f542db170ad21204ef2d`
- Review comment id: `3422572159`
- Review author: `chatgpt-codex-connector[bot]`
- Review created_at: `2026-06-16T16:57:38Z`
- Review file: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
- Review line: `1438`
- Review priority: P2
- Review title: `Reserve time for the next observation poll`
- Current line:

```python
sleep_seconds = min(poll_interval_seconds, max(0, deadline - time.monotonic()))
```

The latest recorded `bb50b7a2` observation result ended at `2026-06-16T16:54:26.145268Z`. The P2 review was submitted at `2026-06-16T16:57:38Z`, after that observation had already stopped. Therefore this specific P2 comment could not have been fetched by that observation run.

## Validity Analysis

The review is valid because the sleep policy does not preserve a budget for another complete snapshot.

The wait loop has a deadline for the entire observation. Each loop performs a snapshot, evaluates stability, and then sleeps. When the payload is already semantically good but still lacks quiet / same-fingerprint stability, the sleep must leave enough time for the next snapshot to complete. Otherwise, the next loop can enter `run_snapshot` with only a fractional remainder and produce a snapshot timeout rather than the stable final payload the wait was trying to confirm.

The important failure mode is not only that the command times out. It is that `timeout_snapshot()` can replace the latest useful payload with `summary.ci/review/head=unknown`, `normalized_status=timeout`, and a less actionable decision. That makes the final observation less truthful than the previous poll.

## Root Cause

The loop currently treats remaining wall-clock time as sleepable time:

1. A poll returns a meaningful but non-terminal payload.
2. The payload is non-terminal because stability requirements are not yet satisfied.
3. The loop sleeps up to `min(poll_interval_seconds, remaining_until_deadline)`.
4. The next iteration starts a snapshot with the tiny leftover budget.
5. The final snapshot times out.
6. The result can degrade from the previous meaningful payload to a generic timeout snapshot.

The missing concept is `next_snapshot_budget`: time that must be reserved before sleeping or starting another poll.

## Desired State

The wait loop should never intentionally sleep away all time needed for the next observation poll.

Required behavior:

- Before sleeping, reserve enough time for another snapshot attempt.
- Before starting a snapshot, detect whether the remaining budget is sufficient.
- If there is not enough budget for a meaningful next poll, stop using the latest valid payload and classify the observation as a deadline / stability failure without overwriting it with an under-budget snapshot timeout.
- Preserve `latest.json` / `result.json` usefulness whenever the latest payload has valid CI/head/review evidence.

## Proposed Design

Add a small internal poll-budget guard to `pr_observation_wait.py`.

The guard should be intentionally conservative and local to the wait wrapper:

- Track the elapsed duration of recent successful snapshot calls.
- Compute `next_poll_min_budget_seconds` as the larger of:
  - a small floor that avoids fractional-time snapshot calls, and
  - recent snapshot elapsed time plus a small slack.
- Before sleeping:
  - compute `remaining = deadline - time.monotonic()`;
  - if `remaining <= next_poll_min_budget_seconds`, do not sleep into the deadline;
  - otherwise sleep at most `remaining - next_poll_min_budget_seconds`.
- Before starting a new snapshot:
  - if `latest_payload` exists and remaining time is below `next_poll_min_budget_seconds`, stop and emit the latest payload with explicit wait metadata indicating the deadline was reached without enough budget for another poll.
- Do not convert the last useful payload into a synthetic all-unknown timeout snapshot solely because the loop started a poll with an obviously insufficient budget.

The exact field names can be finalized during implementation, but proposed metadata is:

- `wait.next_poll_min_budget_seconds`
- `wait.next_poll_budget_reserved`
- `wait.last_snapshot_elapsed_seconds`
- `wait.final_poll_skipped_reason="insufficient_next_snapshot_budget"`

## Implementation Plan

Add this as a new repair unit after the already implemented steps.

1. Add a red test for the P2 condition using fake snapshot calls where a good non-terminal payload appears before stability is satisfied and a final under-budget snapshot would previously overwrite it.
2. Add a test that sleep leaves enough budget for the next poll when quiet / same-fingerprint stability requires one more observation.
3. Add a test that, when there is not enough budget for a next poll, the wait result keeps the latest useful payload and records an explicit insufficient-budget reason rather than replacing it with an all-unknown snapshot timeout.
4. Implement the budget guard in provider `pr_observation_wait.py`.
5. Sync the dogfooding mirror `.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`.
6. Run focused wait tests, the PR observation selector, provider/mirror equality, `git diff --check`, and `./spec-dock/scripts/spec-dock validate`.

## Verification Targets

- Focused selector for the new P2 tests.
- Existing regression:
  - `test_issue_75_pr_observation_wait_completes_after_stable_fingerprint_and_quiet`
- Broader selector:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation_wait or review_completion_unknown or issue_187"`
- Provider/mirror equality:
  - `cmp -s src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py .agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
- Repository checks:
  - `git diff --check`
  - `./spec-dock/scripts/spec-dock validate`

## Stop Conditions

- Stop if preserving latest payload would change a real failed / stale-head / unresolved-review terminal result into a softer state. The guard is only for under-budget polling, not for hiding terminal failures.
- Stop if the test can only be made to pass by increasing global timeouts. The fix should reserve poll budget, not mask the race by making the suite slower.
- Stop if the implementation requires changing public shell CLI options. This should be internal wait-loop hardening.

