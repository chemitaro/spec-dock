---
artifact_kind: disc
id: 20260616t005417z-disc-pr-review-completion-signal-contract
issue: iss-00187
title: PR Review Completion Signal Contract Gap
created_at: 2026-06-16T00:54:17Z
status: adopted
adoption_status: partially_adopted
reflected_to:
  - requirement.md
  - design.md
  - plan.md
  - report.md
---

# PR Review Completion Signal Contract Gap

## Purpose

This artifact records a follow-up finding discovered while observing PR #190 after the Actions-primary CI observation implementation.

The goal is to move the analysis out of chat context and into issue-local evidence so the next implementation can proceed from an explicit problem statement, desired contract, design direction, and work plan.

This artifact started as proposed evidence. It has now been partially adopted into `requirement.md`, `design.md`, `plan.md`, and `report.md`; the canonical adoption/disposition record is `report.md` entries `D-007` and `EAL-022`.

## Sources Read

- Active issue docs:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
- Prior discussion artifacts:
  - `discussions/20260615t154753z-01-research-actions-ci-observation-scope.md`
  - `discussions/20260615t154753z-02-interview-actions-only-pass-contract.md`
- Provider source:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
- Dogfooding mirror:
  - `.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
  - `.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
- Regression tests:
  - `tests/unit/infra/test_init_update.py`
- Observation artifacts inspected locally:
  - `/private/tmp/spec-dock-pr190-observation-fc3041f8/result.json`
  - `/private/tmp/spec-dock-pr190-observation-66c6a3be/result.json`

## Observed Situation

### Current PR #190 head

For PR #190 head `fc3041f86a7f9defba2d3fd8b48ff1c48126151a`, the observation result was:

- `status`: `timeout`
- `summary.ci`: `passed`
- `summary.head`: `matched`
- `summary.review`: `none`
- `decision.status_reason`: `wait_timeout`
- `decision.completion_signal`: `none`
- `decision.selected_unresolved_count`: `0`
- `codex_review.lifecycle.status`: `none`
- `codex_review.lifecycle.completion_signal`: `none`
- `codex_review.lifecycle.selected_review_ids`: `[]`
- `codex_review.lifecycle.selected_review_comment_ids`: `[]`
- `codex_review.lifecycle.selected_review_thread_ids`: `[]`

The important point is that CI and head freshness were already satisfactory. The wait loop remained open because no current-boundary review completion signal was observed.

### Earlier PR #190 head

For earlier head `66c6a3be`, the same observation system detected a Codex review:

- `status`: `human_gate`
- `summary.ci`: `passed`
- `summary.head`: `matched`
- `summary.review`: `unresolved`
- `decision.status_reason`: `current_selected_unresolved_thread`
- `decision.completion_signal`: `submitted_pull_request_review`
- `decision.selected_unresolved_count`: `2`
- selected review ids, review comment ids, and review thread ids were populated.

This confirms the script can detect a submitted pull request review when Codex posts one. The new gap is specifically about completion forms where no current-boundary pull request review is submitted.

## Current Implementation Findings

### Completion signal taxonomy is narrow

`fetch_pr_review_snapshot.sh` currently sets review lifecycle completion from these practical sources:

- High confidence:
  - `submitted_pull_request_review`
  - selected Codex-authored current-boundary pull request review exists.
- Low confidence fallback:
  - `fallback_issue_comment`
  - current-boundary Codex issue comment exists and matches a narrow no-major-issues style body.
- No completion:
  - pending review request or pending review signal.
  - blocking collection failure.
  - otherwise lifecycle `none`, completion signal `none`.

The relevant branch is in `fetch_pr_review_snapshot.sh`:

- selected review signals -> `completion_signal = "submitted_pull_request_review"`, confidence `high`.
- current Codex issue comment status signal -> `completion_signal = "fallback_issue_comment"`, confidence `low`.
- otherwise -> `completion_signal = "none"`.

The fallback issue comment path is intentionally conservative. It is currently treated as `human_gate` with `recommended_next_action = "wait_or_resume"`, not as merge-prepared.

### Trigger comment reactions are not currently completion signals

Repository search found no completion-signal branch for:

- trigger comment reactions,
- reaction groups,
- `+1` / thumbs-up reaction,
- review-request disappearance as completion.

Therefore, if Codex marks a no-findings review as complete through a reaction, external state, or some other non-PR-review side effect, the current script has no way to classify it as completed.

### Wait behavior preserves missing completion as pending until timeout

`wait_pr_observation.sh` treats `decision.status_reason == "missing_current_completion_signal"` as pending:

- normalized status remains pending.
- recommended next action remains `wait_or_resume`.
- observation is not complete.

When the deadline expires, `mark_latest_timeout()` overwrites the latest payload into:

- `status = "timeout"`
- `normalized_status = "timeout"`
- `decision.status_reason = "wait_timeout"`
- `recommended_next_action = "wait_or_resume"`

This loses the more specific meaning of the state: CI/head were done, no feedback was unresolved, but review completion was unproven.

### Existing tests intentionally prevent unsafe pass

Existing tests establish conservative behavior:

- `test_issue_182_s02_snapshot_missing_current_completion_signal_is_not_pass`
  - missing completion signal must not become `passed`.
- `test_issue_182_s03_wait_missing_current_completion_signal_stays_pending`
  - wait loop keeps missing completion as pending or timeout, not passed.
- `test_issue_176_s04_snapshot_fallback_issue_comment_is_human_gate`
  - fallback issue comment is not automatically merge-prepared.

The fix should not simply invert these tests. The safer change is to introduce a distinct unknown-completion terminal category.

## Problem Statement

The PR observation contract currently has no durable representation for this state:

> CI passed, head matched, current trigger boundary has no unresolved selected review threads, but no trusted Codex review completion signal was observed.

Today that state collapses into pending wait and finally generic timeout. This causes two operational problems:

1. The system may waste time waiting or resuming even though the only remaining unknown is review completion signal availability.
2. The final result does not distinguish a still-running review from an unknown/no-signal review completion form.

This is not primarily a "reviews endpoint was not queried" problem. The observed earlier head proves submitted reviews can be collected. The likely contract gap is that Codex may have no-findings completion forms that do not create a current-boundary pull request review.

## Desired State

The observation contract should distinguish these states:

| State | Meaning | Safe action |
|---|---|---|
| `submitted_pull_request_review` | A current-boundary pull request review was submitted by Codex. | Trust as high-confidence completion signal. Continue existing unresolved/changes-requested/pass logic. |
| `fallback_issue_comment` | A current-boundary Codex issue comment indicates review status, but confidence is lower. | Keep human gate or low-confidence handling unless promoted by explicit policy. |
| `trigger_comment_reaction` or equivalent | Codex bot reacted to the trigger comment after trigger time. | Treat as secondary evidence only if actor/time/trigger match. Do not auto-pass without policy. |
| `review_completion_unknown` | CI/head are done and no unresolved feedback is selected, but no completion signal was observed. | Stop blind waiting; return a specific unknown/human-gate status that tells the caller review completion is unproven. |
| `missing_current_completion_signal` | Review may still be running or current boundary is not yet stable. | Continue wait/resume while within observation window. |

The non-negotiable safety rule is:

> `selected_comments == 0` or `selected_unresolved_count == 0` is not completion.

No-feedback and not-yet-reviewed are indistinguishable without a completion signal or an explicit unknown-completion classification.

## Proposed Design

### Delegated draft synthesis

Two delegated discussion drafts were produced after the first version of this artifact:

- `discussions/20260616t000000z-03-disc-architect-pr-review-completion-signal-contract.md`
- `discussions/20260616t000000z-04-disc-planner-pr-review-completion-signal-contract.md`

Adoption status in this artifact: partially adopted.

Adopted points:

- The current issue canonical scope is primarily Actions CI observation and explicitly treats Codex review lifecycle changes as out of scope. Implementation should therefore require either a canonical amendment or a follow-up issue.
- Provider source under `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/` remains the authority; `.agents/` is a dogfooding mirror.
- Existing `fallback_issue_comment` semantics should not be silently redefined because tests and operator semantics currently treat it as low-confidence human gate evidence.
- If an allowlisted current-boundary no-findings issue comment exists, it may deserve a distinct signal name rather than reusing `fallback_issue_comment`.
- Wrapper scripts should consume a normalized decision signal from `fetch_pr_review_snapshot.sh`; they should not infer raw comment-body semantics themselves.

Not fully adopted:

- The architect draft recommends a new no-findings issue-comment signal that may promote to merge-ready. This is a valid design option, but it does not cover the full observed `fc3041...` symptom by itself because the reported selected review/comment/thread ids were all empty and completion signal was `none`.
- Therefore this artifact separates two related but different fixes:
  - Track A: classify stable "no completion signal observed" as `review_completion_unknown` so wait does not collapse into generic timeout.
  - Track B: optionally add an explicit `codex_no_findings_issue_comment` completion signal if a strict current-boundary no-findings issue comment is actually observable.

Recommended sequencing:

1. Implement Track A first because it directly addresses the wasted wait/timeout even when no secondary signal exists.
2. Implement Track B only after the exact GitHub artifact shape is known and can be covered with fake `gh` tests.

### Layer 1: Snapshot contract in `fetch_pr_review_snapshot.sh`

Keep `submitted_pull_request_review` as the primary completion signal.

Add a more explicit lifecycle/decision category when all of these are true:

- current trigger boundary is known,
- CI/head state is available to the wrapper as passed/matched at the combined snapshot level, or review snapshot has enough context to avoid calling this while collection is still incomplete,
- review collection did not fail in a blocking way,
- no selected current unresolved review thread exists,
- no current selected changes-requested evidence exists,
- no current pending review signal or review-request signal exists,
- no trusted completion signal exists.

Candidate output:

```json
{
  "codex_review": {
    "lifecycle": {
      "status": "completion_unknown",
      "completion_signal": "none",
      "confidence": "medium"
    }
  },
  "decision": {
    "status": "unknown",
    "status_reason": "review_completion_unknown",
    "recommended_next_action": "human_gate",
    "observation_complete": true
  }
}
```

Alternative status naming:

- `review_completion_unknown`
- `unknown_review_completion`
- `missing_review_completion_signal_after_ci_pass`

Recommended name: `review_completion_unknown`, because it describes the domain gap rather than the mechanism.

### Layer 2: Observation wrapper in `fetch_pr_observation_snapshot.sh`

If the review collector returns `review_completion_unknown`, the combined snapshot should preserve it rather than collapsing it into generic pending.

Recommended combined behavior:

- `normalized_status`: `unknown` or `human_gate`
- `recommended_next_action`: `human_gate`
- `observation_complete`: `true`
- `summary.ci`: preserved as `passed`
- `summary.head`: preserved as `matched`
- `summary.review`: `unknown` or `completion_unknown`
- `decision.status_reason`: `review_completion_unknown`

Choosing between `unknown` and `human_gate`:

- `unknown` is semantically accurate: automation cannot prove review completion.
- `human_gate` is operationally safer: a human or orchestrator must inspect GitHub state before merge.

Recommended top-level status: `human_gate` if existing downstream workflows use `human_gate` as the stop-and-inspect state; otherwise `unknown`.

The important part is that `recommended_next_action` should not remain `wait_or_resume` once the condition has stabilized.

### Layer 3: Wait loop in `wait_pr_observation.sh`

The wait loop should treat `review_completion_unknown` as a terminal or terminal-like state:

- do not wait until timeout,
- do not overwrite the status into `wait_timeout`,
- preserve the specific decision reason,
- attach resume metadata only if useful for manual inspection, not as the primary action.

Candidate normalization:

```python
if decision_reason == "review_completion_unknown":
    return "human_gate", "human_gate", "human_gate", False, True
```

or, if `unknown` is preferred:

```python
if decision_reason == "review_completion_unknown":
    return "unknown", "unknown", "human_gate", False, True
```

### Layer 4: Optional secondary signals

Secondary completion signals should be added only with explicit evidence and tests.

Recommended order:

1. Keep existing `submitted_pull_request_review` as high confidence.
2. Keep `fallback_issue_comment` low confidence and non-promoting.
3. If the no-findings issue-comment form is observable, add a distinct completion signal such as `codex_no_findings_issue_comment` or `codex_no_findings_completion`.
   - It must require a strict allowlist body such as `No major issues found.`
   - It must be Codex-authored and current-boundary.
   - It must be ignored when current selected unresolved threads or changes-requested evidence exist.
   - It should not be implemented by changing generic `fallback_issue_comment` into a pass signal.
4. Add trigger comment reaction only if the GitHub API data is reliable enough:
   - reaction is on the exact trigger comment,
   - reaction user is Codex bot or accepted Codex identity,
   - reaction timestamp is after trigger created_at if the API provides it,
   - reaction content is an accepted completion marker.
5. Treat review-request disappearance as diagnostic evidence only. Do not use it as completion by itself.

If reaction timestamps are unavailable or actor identity is ambiguous, reaction support should remain out of scope for the first fix.

## Non-Goals

- Do not make "no selected comments" a pass condition.
- Do not automatically merge or mark merge-prepared without a trusted completion signal.
- Do not weaken existing handling of unresolved threads or changes-requested reviews.
- Do not remove `submitted_pull_request_review` as the primary signal.
- Do not make arbitrary GitHub API endpoints configurable by callers.
- Do not conflate CI timeout, snapshot API timeout, and review completion unknown.

## Proposed Implementation Plan

### S01: Add review completion unknown snapshot contract

Target files:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
- `tests/unit/infra/test_init_update.py`

Work:

- Add a branch after pending/review-request/blocking-failure handling that classifies stable no-completion state as `review_completion_unknown`.
- Preserve existing branches for:
  - selected unresolved threads,
  - selected changes-requested evidence,
  - `submitted_pull_request_review`,
  - `fallback_issue_comment`,
  - blocking collection failure.
- Add fields to the lifecycle payload only additively if useful:
  - `completion_unknown_reason`
  - `completion_signal_candidates`
  - `completion_signal_evidence`

Tests:

- Current-boundary trigger, no reviews, no comments, no threads, no pending review request -> `decision.status_reason == "review_completion_unknown"`.
- Same fixture must not produce `passed`.
- Existing `missing_current_completion_signal` test should be updated or split so truly unstable/pending remains pending.

Review gate:

- code-reviewer should verify false-pass safety and no regression of existing fallback/unresolved behavior.

Commit boundary:

- One commit for snapshot review contract.

### S02: Preserve review completion unknown in combined snapshot and wait

Target files:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
- `tests/unit/infra/test_init_update.py`

Work:

- Ensure combined snapshot does not collapse `review_completion_unknown` into pending.
- Add wait normalization branch for `review_completion_unknown`.
- Prevent timeout handling from overwriting the specific reason when the state is already terminal-like.

Tests:

- Snapshot with CI passed/head matched/review completion unknown -> top-level `human_gate` or `unknown`, not `pending`, not `passed`.
- Wait with stable review completion unknown -> exits before timeout/stability deadline as terminal-like result.
- Final payload preserves:
  - `summary.ci = passed`,
  - `summary.head = matched`,
  - `decision.status_reason = review_completion_unknown`,
  - `recommended_next_action = human_gate`.

Review gate:

- code-reviewer should verify no blind wait loop remains for this state.

Commit boundary:

- One commit for wrapper/wait classification.

### S03: Evaluate explicit secondary completion signals

Target files:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
- `tests/unit/infra/test_init_update.py`

Work:

- First, determine whether a no-findings issue comment exists in the current trigger window for the observed failure mode. If yes, prefer an explicit `codex_no_findings_issue_comment` signal over reusing `fallback_issue_comment`.
- Inspect whether current GitHub API responses used by the script can collect trigger comment reactions with sufficient actor/time evidence.
- If reliable, add a low/medium confidence signal such as `trigger_comment_reaction`.
- If not reliable, record as deferred in `report.md` or a follow-up discussion.

Tests if implemented:

- Exact current trigger boundary has Codex-authored `No major issues found.` issue comment and no blockers -> explicit no-findings signal.
- Same no-findings comment plus unresolved selected thread -> human gate, not pass.
- Same no-findings comment plus changes-requested selected evidence -> human gate, not pass.
- Generic current Codex issue comment remains `fallback_issue_comment`, not pass.
- Exact trigger comment has Codex-authored accepted reaction -> completion signal is `trigger_comment_reaction`, confidence low/medium.
- Reaction on older trigger comment -> ignored.
- Reaction by non-Codex actor -> ignored.
- Reaction without timestamp/actor evidence -> ignored or low-confidence human gate, not pass.

Review gate:

- code-reviewer should verify trigger boundary safety.

Commit boundary:

- Separate commit only if reaction support is implemented.

### S90: Sync provider/dogfooding mirror and update docs

Target files:

- `.agents/skills/github-pr-observation/scripts/...`
- Optional provider/mirror `SKILL.md` if operator guidance changes.
- `spec-dock/active/issue/report.md` if this issue absorbs the follow-up.

Work:

- Copy provider script changes into dogfooding mirror or run the established sync path.
- Document `review_completion_unknown` as a non-pass terminal review state.
- Record evidence adoption and reviewer gates if canonical docs are updated.

Tests:

- `cmp` provider and mirror changed files.
- `git diff --check`.

Commit boundary:

- One docs/mirror commit after code behavior is reviewed.

### S99: Final verification

Commands:

```bash
uv run pytest tests/unit/infra/test_init_update.py -k "review_completion_unknown or completion_signal or fallback_issue_comment or missing_current_completion_signal or issue_182 or issue_176"
uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation or issue_187"
git diff --check
./spec-dock/scripts/spec-dock validate
```

If the focused test selector becomes too broad or slow, record the narrower command and why it covers the changed contract.

Reviewer gates:

- code-reviewer for implementation.
- qa-reviewer for false-pass and wait-loop behavior.
- spec-reviewer if canonical issue docs are updated.

## Test Contract Suggestions

| ID | Scenario | Expected |
|---|---|---|
| `tc-review-unknown-001` | CI passed, head matched, no review/comment/thread/pending signal in current trigger boundary | `review_completion_unknown`, not pass, terminal-like human gate/unknown |
| `tc-review-unknown-002` | Same state through wait loop | does not degrade to generic `wait_timeout`; recommended action is not blind `wait_or_resume` |
| `tc-review-primary-001` | Current Codex pull request review exists with no unresolved threads | existing high-confidence `submitted_pull_request_review` pass behavior preserved |
| `tc-review-primary-002` | Current Codex pull request review has unresolved threads | existing `current_selected_unresolved_thread` human gate preserved |
| `tc-review-fallback-001` | Current Codex issue comment fallback exists | existing `fallback_issue_comment_low_confidence` human gate preserved |
| `tc-review-no-findings-001` | Current Codex allowlisted no-findings issue comment exists, no PR review exists, no blockers exist | optional explicit no-findings signal; pass only if canonical policy adopts this signal |
| `tc-review-no-findings-002` | Same no-findings comment plus unresolved/changes-requested current evidence | current blockers win; human gate |
| `tc-review-pending-001` | Current pending review or review request exists | remains pending/wait; not `review_completion_unknown` |
| `tc-review-reaction-001` | Accepted trigger reaction exists, if implemented | classified as secondary signal, not pass unless explicitly adopted |

## Open Decisions

1. Should top-level `review_completion_unknown` normalize to `unknown` or `human_gate`?
   - Recommendation: `human_gate` if downstream automation already treats it as the safe inspection gate.
2. Should `fallback_issue_comment` ever promote to pass?
   - Recommendation: no for this fix. Keep it low-confidence unless the Codex no-findings comment contract is explicit and stable.
3. Should trigger comment reactions be implemented in the same PR?
   - Recommendation: only after confirming the GitHub API provides actor/time evidence. Otherwise defer.
4. Should a strict allowlisted no-findings issue comment be treated as completion?
   - Recommendation: yes only as a distinct signal with explicit fake `gh` coverage and current-boundary safeguards. Do not reuse generic `fallback_issue_comment`.
5. Should this be absorbed into `iss-00187` or split into a follow-up issue?
   - Recommendation: split if PR #190's current scope should remain Actions CI observation. Absorb only if the goal is to finish PR observation hardening before merge.

## Recommended Next Action

Create or adopt a follow-up implementation slice with this scope:

> Add an explicit `review_completion_unknown` terminal-like state to PR observation so CI-passed/head-matched observations do not wastefully timeout when Codex does not submit a pull request review and no trusted completion signal is available.

This is small enough for a focused follow-up issue, but material enough that it should have its own test contract and review gate.
