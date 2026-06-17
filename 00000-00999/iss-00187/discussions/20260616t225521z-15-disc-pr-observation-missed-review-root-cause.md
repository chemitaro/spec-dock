---
種別: disc
ID: "20260616t225521z-15-disc-pr-observation-missed-review-root-cause"
タイトル: "PR observation missed review root cause analysis"
状態: "proposed"
作成者: "orchestrator"
最終更新: "2026-06-17"
親: ["iss-00187-actions-pr-observation-ci-state"]
関連: ["https://github.com/chemitaro/spec-dock/pull/190", "PR review comment 3422572159", "20260616t225521z-14-disc-missed-p2-reserve-next-observation-poll"]
authority: "proposed"
derived_from: ["/private/tmp/spec-dock-pr190-observation-bb50b7a2/result.json", "PR review comment 3422572159", "deep-consultant 019ed29f-a04f-7b61-8c72-4df37a730ad0"]
reflected_to: []
---

# PR observation missed review root cause analysis

## Summary

The current failure has two distinct causes.

1. The newly noticed P2 review `3422572159` was posted after the latest `bb50b7a2` observation had already ended. That specific comment was not missed by the GitHub API call inside that observation; it arrived too late for that run.
2. The observation system still has a real review-coverage defect: it separates all-fetched unresolved review threads from current-trigger selected threads, but downstream decision and operator reporting treat `selected_unresolved_count=0` too strongly. As a result, non-outdated unresolved review threads can remain visible in audit fields while not being elevated into the repair inventory or merge-prepared gate.

Both issues must be handled. The first needs a safer post-review / no-completion waiting contract. The second needs an actionable unresolved review inventory that includes both current-selected blockers and non-outdated carryover blockers.

## Timeline Evidence

### Latest observation

Observation evidence file:

`/private/tmp/spec-dock-pr190-observation-bb50b7a2/result.json`

Key fields:

- `observed_at`: `2026-06-16T16:54:26.145268Z`
- `status`: `human_gate`
- `normalized_status`: `human_gate`
- `summary.ci`: `passed`
- `summary.head`: `matched`
- `summary.review`: `none`
- `decision.status_reason`: `review_completion_unknown`
- `decision.completion_signal`: `none`
- `decision.selected_unresolved_count`: `0`
- `decision.selected_review_thread_ids`: `[]`
- `wait.review_trigger_age_seconds`: `765`
- `wait.ci_passed_age_seconds`: `124`
- `wait.review_completion_unknown_latency_satisfied`: `true`
- `review.threads.unresolved`: `3`

The observation did not claim merge-ready. It stopped at a human gate because current-boundary review completion was unknown.

### Newly noticed P2 review

GitHub PR review comment:

- id: `3422572159`
- created_at: `2026-06-16T16:57:38Z`
- submitted review time from `gh pr view --json latestReviews`: `2026-06-16T16:57:38Z`
- file: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
- line: `1438`
- title: `Reserve time for the next observation poll`

This timestamp is about three minutes after the observation ended. Therefore this P2 review is primarily a late-review race relative to the observation stop time.

## What The Script Did Correctly

The latest `bb50b7a2` observation did not mark the PR as passed or merge-prepared.

It produced:

- `normalized_status="human_gate"`
- `decision.status="unknown"`
- `decision.status_reason="review_completion_unknown"`
- `recommended_next_action="human_gate"`

That part is safer than the original timeout behavior because it avoids claiming success when Codex review completion is not observable.

## What The Script / Workflow Did Incorrectly

### Problem A: late review race

The wait wrapper allowed `review_completion_unknown` after configured latency gates:

- trigger age was `765` seconds, above the `300` second minimum;
- CI passed age was `124` seconds, above the `90` second minimum;
- quiet / same-fingerprint stability was satisfied.

But the P2 review arrived at `2026-06-16T16:57:38Z`, after the wrapper stopped at `2026-06-16T16:54:26Z`. This proves the current latency thresholds can still be too short for actual Codex review publication in this case.

Because `review_completion_unknown` is a non-pass human gate, this is not a false merge-ready pass. It is still operationally harmful: the orchestration flow can stop observing and report a human gate before Codex has finished publishing feedback, which lets a later review escape the immediate repair batch.

### Problem B: all-fetched unresolved threads were not elevated

The same observation result contains `review.threads.unresolved=3`. Those threads are all-fetched audit data, not the authoritative current-boundary decision set.

At the same time:

- `decision.selected_unresolved_count=0`
- `decision.selected_unresolved_thread_ids=[]`
- `codex_review.collection_summary.review_threads.selected_ids=[]`

The scripts intentionally distinguish selected current-boundary feedback from historical / carryover feedback. That distinction is useful for avoiding stale-review false positives. The defect is that non-outdated carryover feedback on the latest head is not separately represented as actionable review work.

The result is confusing and unsafe for orchestration:

- `summary.review="none"` reads as if there is no review work.
- `selected_unresolved_count=0` reads as if there is no unresolved review blocker.
- `review.threads.unresolved=3` quietly contradicts that at the audit layer.
- Merge-preparer / orchestrator can focus on selected current-boundary data and miss unresolved all-fetched non-outdated review threads.

This is not a GitHub API retrieval failure. It is a classification and gate-design failure.

## Root Cause

Root cause 1: `review_completion_unknown` is time-gated, but the current gate does not prove Codex has finished publishing review feedback. It only proves the observed no-completion state was stable for the configured window. In PR #190, that window ended before the P2 review was submitted.

Root cause 2: the observation output has no first-class `actionable_unresolved_review_count` that combines:

- current-trigger selected unresolved threads, and
- carryover non-outdated unresolved threads still attached to the latest head.

Root cause 3: the operator workflow did not treat `review.threads.unresolved>0` as a mandatory repair-inventory input when `selected_unresolved_count=0`. This allowed the repair batch to proceed from selected P1 comments and miss later or non-selected feedback.

## Desired State

The merge-prepared / closeout gate must require all of the following:

- CI passed.
- Head matched.
- Review completion is trusted, or the state is explicitly human-gated as unknown.
- `actionable_unresolved_review_count == 0`.
- No blocking collection limitation exists.

`selected_unresolved_count == 0` must never be treated as sufficient. It is only one component of the review inventory.

## Proposed Design

### Review thread inventory

Add a first-class review thread inventory that separates three scopes:

- `review_threads.all_fetched.non_outdated_unresolved[]`
  - all GitHub-fetched review threads that are unresolved and not outdated.
- `review_threads.current_selected.unresolved[]`
  - unresolved threads selected by the current trigger / review boundary.
- `review_threads.carryover_non_outdated_unresolved[]`
  - unresolved, non-outdated threads that are not selected by the current trigger boundary but still apply to the latest diff.

Then add decision fields:

- `decision.actionable_unresolved_count`
- `decision.current_selected_unresolved_count`
- `decision.carryover_unresolved_count`
- `decision.actionable_unresolved_thread_ids`
- `decision.carryover_unresolved_thread_ids`

### Decision semantics

Decision precedence should become:

1. current-selected changes requested / unresolved thread;
2. carryover non-outdated unresolved thread;
3. blocking collection limitation;
4. pending review signal;
5. explicit trusted completion signal;
6. stable no-completion evidence -> `review_completion_unknown`.

If any current-selected or carryover non-outdated unresolved review exists:

- `summary.review` should be `unresolved`;
- `recommended_next_action` should be `address_review_feedback`;
- `decision.status_reason` should be either `current_selected_unresolved_thread` or `carryover_non_outdated_unresolved_thread`;
- `review_completion_unknown` must not be emitted.

### Late review race handling

Keep `review_completion_unknown` non-pass, but make it safer:

- Increase or make configurable the review publication latency gates.
- Add an explicit post-unknown audit recommendation: after `review_completion_unknown`, orchestration must refresh PR reviews/comments once more before reporting the repair inventory final.
- Consider a second short observation pass when `completion_signal=none` and no selected blocker exists, especially immediately after CI first passed.
- Record `latest_review_activity_at` and `latest_review_activity_age_seconds` where available.
- If any review activity appears after the trigger and before stop time, require quiet time relative to that review activity as well as CI/head fingerprint stability.

The key invariant is that `review_completion_unknown` stops blind waiting, but it does not prove review absence.

### Operator / merge-preparer gate

The PR merge-preparer should not use selected current-boundary data alone.

Before declaring merge-prepared, it must inspect or receive:

- current-selected unresolved review inventory;
- carryover non-outdated unresolved review inventory;
- latest review submission/comment timestamps;
- completion signal and no-completion reason.

If `review_completion_unknown` appears, the merge-preparer must report a human gate and include the complete actionable review inventory. It must not summarize the PR as having no review work unless `actionable_unresolved_count == 0` after a fresh review inventory pass.

## Implementation Plan

Add a follow-up repair sequence after the current completed implementation steps.

1. Add discussion-derived design updates to `design.md`:
   - define actionable review inventory;
   - define carryover non-outdated unresolved threads;
   - state that `selected_unresolved_count==0` is not sufficient;
   - state that `review_completion_unknown` is not proof of review absence.
2. Append implementation steps to `plan.md`:
   - one step for inventory fields and classification;
   - one step for wait / merge-preparer gate behavior;
   - one step for P2 poll-budget reservation;
   - one step for final live PR re-observation and review inventory proof.
3. Add tests where selected IDs are empty but all-fetched non-outdated unresolved threads exist. Expected result: human gate / `address_review_feedback`, not `review_completion_unknown`.
4. Add tests where all fetched unresolved threads are outdated only. Expected result: audit-only, not actionable blocker.
5. Add tests where both current-selected and carryover unresolved exist. Expected result: current-selected blocker takes precedence while carryover remains listed.
6. Add tests for late-review handling metadata and `review_completion_unknown` being non-pass and not review-absence proof.
7. Implement provider changes first, then sync dogfooding mirror.
8. Rerun PR #190 observation after pushing the fix and verify that current review inventory includes P2 `3422572159` until resolved or superseded.

## Verification Targets

- Focused tests for:
  - current-selected unresolved;
  - carryover non-outdated unresolved;
  - outdated-only unresolved audit data;
  - `review_completion_unknown` with no actionable review inventory;
  - P2 poll-budget reservation.
- Existing PR observation tests:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation or issue_187"`
- Provider/mirror equality for touched scripts.
- `git diff --check`
- `./spec-dock/scripts/spec-dock validate`
- Live PR #190 observation after push, with explicit report of:
  - `decision.actionable_unresolved_count`;
  - current selected unresolved IDs;
  - carryover unresolved IDs;
  - comment id `3422572159` if still unresolved and non-outdated.

## Immediate Operational Decision

PR #190 should not be considered merge-prepared while P2 `3422572159` remains unresolved.

The next repair batch should include:

- P2 `3422572159`: reserve budget for the next observation poll.
- Observation-system defect: elevate non-outdated carryover unresolved threads into actionable review inventory.
- Workflow defect: require a fresh all-actionable review inventory before reporting merge-prepared after `review_completion_unknown`.

## Open Questions

- What default latency should gate `review_completion_unknown` after CI first passes? The existing `90` seconds after CI pass was insufficient for PR #190.
- Should `review_completion_unknown` trigger an automatic short recheck before returning, or should that remain a merge-preparer responsibility?
- Should carryover non-outdated unresolved threads block every run, or only block merge-prepared / closeout while remaining separate from current-trigger review completion?
