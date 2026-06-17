---
artifact_kind: disc
id: 20260616t025000z-disc-current-review-observation-gap
issue: iss-00187
title: Current PR Review Observation Gap After Review Completion Unknown
created_at: 2026-06-16T02:50:00Z
status: adopted
adoption_status: adopted
reflected_to:
  - design.md
  - plan.md
  - report.md
---

# Current PR Review Observation Gap After Review Completion Unknown

## Purpose

This artifact records the currently observed PR #190 monitoring problem before any additional implementation work starts.

The goal is to separate three related but different facts:

1. The latest PR #190 state now has a submitted Codex pull request review with two unresolved P1 threads.
2. The earlier wait observation returned `review_completion_unknown` / human gate before that review was visible to the monitor.
3. The scripts therefore need both review-feedback handling and a review-timing / completion-contract hardening pass.

## Sources Inspected

- GitHub PR #190 live state:
  - `gh pr view 190 --json number,url,state,headRefOid,mergeable,reviewDecision,reviews,comments`
  - `gh pr checks 190`
  - `gh api graphql` review thread query for PR #190
- Current observation scripts:
  - `.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
- Latest live snapshot command:
  - `./.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh --repo chemitaro/spec-dock --pr 190 --head-sha 1bb19acdf512d71f45a39ce7a3790862b36b0295`
- Verification command:
  - `uv run pytest tests/unit/infra/test_init_update.py -q`

## Current Live PR State

As of the latest inspection, PR #190 is:

- PR state: `OPEN`
- Head SHA: `1bb19acdf512d71f45a39ce7a3790862b36b0295`
- Merge state: `MERGEABLE` / `CLEAN`
- CI checks:
  - `validate`: pass
  - `provider-tests`: pass
- Latest Codex review:
  - author: `chatgpt-codex-connector`
  - submitted at: `2026-06-16T02:35:08Z`
  - reviewed commit: `1bb19acdf512d71f45a39ce7a3790862b36b0295`
  - state: `COMMENTED`
- Latest selected unresolved review threads:
  - `PRRT_kwDOQ99OK86JwtEM`
  - `PRRT_kwDOQ99OK86JwtEO`

The live snapshot now returns:

- `status`: `human_gate`
- `summary.ci`: `passed`
- `summary.head`: `matched`
- `summary.review`: `unresolved`
- `decision.status_reason`: `current_selected_unresolved_thread`
- `decision.completion_signal`: `submitted_pull_request_review`
- `decision.selected_unresolved_count`: `2`
- `recommended_next_action`: `address_review_feedback`

This means the current snapshot collector can detect the latest review feedback after the review exists.

## Important Timeline Interpretation

The earlier monitor result that motivated the `review_completion_unknown` addendum did not mean the review endpoints were never queried.

It likely meant this narrower state:

1. A latest `@codex review` trigger existed.
2. CI became passed and head remained matched.
3. At the time the wait loop finalized, no current-boundary Codex pull request review had appeared.
4. The wait wrapper promoted the stable no-completion state to `review_completion_unknown`.
5. Later, Codex submitted a pull request review for the same latest head with two P1 threads.

The key risk is therefore timing-sensitive:

> `review_completion_unknown` can be emitted before Codex review completion has actually materialized as a submitted review.

The intent of `review_completion_unknown` was safe non-pass termination instead of blind timeout. That remains directionally useful. However, the current promotion criteria may be too eager for real Codex review latency.

## Problem Statement

The monitoring contract currently has a race window between CI completion and Codex review publication.

When CI passes before Codex publishes a pull request review, the wait wrapper can see:

- CI passed,
- head matched,
- no selected unresolved review threads,
- no current completion signal,
- stable fingerprint / quiet window satisfied.

The wrapper can then return a non-pass `human_gate` with `decision.status_reason="review_completion_unknown"`.

That result is safer than `passed`, but it is still operationally incomplete if the normal Codex review is still in flight. It can cause the orchestrator to stop monitoring or report a review-completion unknown state shortly before actionable P1 feedback arrives.

## Desired State

The monitor should distinguish:

| State | Meaning | Expected action |
|---|---|---|
| Current submitted Codex PR review with unresolved threads | Review completed with actionable feedback | `human_gate`, `address_review_feedback` |
| CI passed, head matched, no review yet, still inside Codex review latency allowance | Review likely still in flight | keep waiting or resume monitoring |
| CI passed, head matched, no review yet, beyond explicit review latency allowance | Completion evidence unavailable | `review_completion_unknown`, `human_gate` |
| Explicit no-findings completion signal | Review completed without findings | follow the explicit signal contract only |

The safety rule remains unchanged:

> `selected_unresolved_count == 0` is not proof of review completion.

The new nuance is:

> `completion_signal == "none"` shortly after CI passes is not proof of no-review completion or permanent unknown completion.

## Analysis of the Existing Addendum

The S100-S101 addendum introduced `review_completion_unknown` to prevent generic timeouts when no completion signal is available.

This is still useful as a terminal-like non-pass state, but it needs a stronger temporal contract:

- Do not promote to `review_completion_unknown` immediately after CI pass if the current trigger is still within an allowed Codex review completion window.
- Record the age of the trigger and the age of the CI-passed state when deciding promotion.
- Keep `review_completion_unknown` non-pass and human-gated even after the timing guard is added.
- Do not rely on selected comment/thread counts alone.

## Proposed Follow-Up Design Direction

### 1. Add explicit review-latency gating

`wait_pr_observation.sh` should require a minimum elapsed interval after the current trigger, and possibly after CI first becomes passed, before promoting a missing completion signal to `review_completion_unknown`.

The exact duration should be explicit and test-covered. It should not be an implicit side effect of `--quiet-seconds` or `--same-fingerprint-required`.

Candidate fields:

- `wait.review_trigger_age_seconds`
- `wait.ci_passed_age_seconds`
- `wait.review_completion_unknown_min_age_seconds`
- `decision.status_reason="missing_current_completion_signal"` before the threshold
- `decision.status_reason="review_completion_unknown"` only after the threshold

### 2. Preserve current unresolved-review behavior

When the current submitted review arrives, the current logic should continue to select:

- current review id,
- current review comment ids,
- current review thread ids,
- unresolved count.

The latest live snapshot already demonstrates this path works for the current P1 review.

### 3. Keep no-findings completion separate

If Codex provides an explicit no-findings artifact such as a trigger comment reaction or allowlisted issue comment, that should be modeled as a distinct completion signal. It should not be conflated with `review_completion_unknown`.

### 4. Add regression coverage for the race

Tests should include:

- current trigger, CI passed, no review yet, elapsed below threshold -> pending / wait.
- same state beyond threshold -> `review_completion_unknown`.
- submitted review appears after earlier no-completion state -> unresolved feedback wins.
- submitted review with P1 threads -> `address_review_feedback`.

## Evidence From Latest Commands

The latest full unit file run completed successfully:

```text
uv run pytest tests/unit/infra/test_init_update.py -q
388 passed in 213.21s
```

This means the current local tests do not catch the latest timing gap. The absence of failing tests is not proof that the monitor contract is sufficient.

## Open Questions

- What default review latency allowance is appropriate for Codex review after `@codex review`?
- Should the threshold be fixed, configurable by environment variable, or controlled by wait script flags?
- Should the monitor continue beyond the ordinary wait deadline if CI passed but review completion is still inside the review-latency allowance?
- Should a new PR observation run always re-check once after `review_completion_unknown` before reporting final merge-preparation state?

## Recommended Next Work

1. Treat PR #190 as not merge-ready until the latest P1 review threads are addressed.
2. Add a new implementation-plan step for review-completion timing hardening.
3. Add failing fake-`gh` tests for the no-review-yet race window.
4. Modify `wait_pr_observation.sh` only after extracting or isolating the Python logic enough to make the change reviewable.
5. Re-run PR observation on the latest head after fixes are pushed.
