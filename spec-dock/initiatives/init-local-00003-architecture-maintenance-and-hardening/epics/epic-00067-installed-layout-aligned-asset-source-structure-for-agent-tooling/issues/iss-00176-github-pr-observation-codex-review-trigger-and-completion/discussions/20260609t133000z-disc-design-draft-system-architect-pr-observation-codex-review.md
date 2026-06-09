---
created_by_role: system-architect
scope_id: iss-00176
source_paths:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/discussions/20260608t085332z-research-chatgpt55-pro-analysis-request-package.md
  - spec-dock/active/issue/discussions/20260608t092803z-research-chatgpt55-pro-codex-review-trigger-completion-analysis.md
  - spec-dock/active/issue/discussions/20260608t111111z-research-deterministic-codex-review-trigger-design.md
  - spec-dock/active/issue/discussions/20260609t030339z-interview-issue-scope-for-deterministic-codex-review-trigger.md
  - spec-dock/active/issue/discussions/20260609t130000z-interview-review-body-output-contract.md
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh
  - spec-dock/active/epic/design.md
intended_targets:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
adoption_status: unreviewed
reflected_to: []
---

# Design Draft: GitHub PR Observation Codex Review Trigger and Completion

## Positioning

This draft proposes the issue-level design for `iss-00176`. It is not canonical until reviewed and reflected into `design.md`.

The parent epic fixes the asset authority at `src/spec_dock/assets/install_root/` and keeps installed paths layout-aligned. Therefore the implementation source of truth for this issue remains:

```text
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/
```

The local dogfooding `spec-dock/` tree is validation context only, not the implementation authority.

## Design Goals

- Make the normal `wait_pr_observation.sh` invocation deterministically create one `@codex review` trigger.
- Keep the write boundary narrow, fixed, testable, and separate from read-only collectors.
- Use the trigger `comment_id` and `created_at` as the only observation boundary for the run.
- Treat Codex-authored submitted Pull Request Review as the primary completion signal.
- Keep CI terminal state and Codex review lifecycle independent until final classification.
- Preserve the output authority boundary:
  - `stdout`: exactly one final JSON result.
  - `stderr`: bounded progress and diagnostics only.
  - `--out`: optional debug and audit copy, never the authority.
- Include selected Codex review body full text in final `stdout` JSON so the caller does not need extra `gh api` or broad comment collection.

## File and Module Responsibilities

### `SKILL.md`

Change the skill contract from read-only only to fixed trigger write plus read-only observation.

Responsibilities:

- Document that the only permitted write is a fixed PR issue comment POST with body `@codex review`.
- Keep the prohibition on arbitrary endpoints, methods, GraphQL, headers, body files, caller-provided bodies, raw `gh` arguments, and caller-provided `jq`.
- Document default `post-once` and explicit `resume` mode.
- State that `stdout` final JSON is the authority and `--out` is only audit/debug.

### `scripts/trigger_codex_review.sh`

Add this script as the fixed write boundary.

Responsibilities:

- Validate only `--repo OWNER/REPO`, `--pr NUMBER`, and `--head-sha SHA`.
- Split `OWNER/REPO` internally after validation.
- Fetch PR head before POST using a fixed read API.
- If current head mismatches expected head, do not POST and return JSON with `status=stale_head`, `trigger.action=not_posted`, and current head evidence.
- POST exactly one issue comment with fixed body `@codex review` to the fixed REST endpoint:

```text
POST repos/{owner}/{repo}/issues/{pr}/comments
body = "@codex review"
```

- Capture returned `id`, `node_id`, `created_at`, `updated_at`, `html_url`, `user.login`, and body hash/equality evidence.
- Re-fetch PR head after POST.
- If head changed after POST, keep trigger metadata but return non-success stale state.
- On POST failure, do not blindly retry.
- If recovery is implemented, use before/after issue comment snapshots and adopt recovery only when exactly one new exact-body `@codex review` comment by the authenticated actor is observed.
- Return exactly one JSON text on stdout.
- Write diagnostics only to stderr.

Non-responsibilities:

- No polling.
- No review selection.
- No `--out`.
- No caller-provided body or body mode.
- No deletion or update of trigger comments.

### `scripts/wait_pr_observation.sh`

Keep this script as the public orchestration entrypoint for trigger plus polling.

Responsibilities:

- Add `--trigger-mode post-once|resume`, defaulting to `post-once`.
- In `post-once` mode:
  - Reject `--trigger-comment-id` or `--trigger-created-at` as usage error.
  - Invoke `trigger_codex_review.sh` exactly once before the polling loop.
  - Capture trigger stdout internally and never pass it through to user-facing stdout.
  - If trigger returns stale or non-success, emit final JSON and stop without converting it to success.
  - Pass the captured `comment_id` and `created_at` to every snapshot poll.
- In `resume` mode:
  - Require both `--trigger-comment-id` and `--trigger-created-at`.
  - Do not call `trigger_codex_review.sh`.
  - Reuse the explicit trigger metadata as the boundary.
- Keep existing polling, quiet/stability, timeout, progress, and `--out` mechanics, but make review completion independent from CI.
- Add `resume` metadata to timeout/limit final JSON when the trigger boundary is known.
- Include the trigger contract, mode, action, and source in final JSON.
- Include selected review body full text in final JSON regardless of `--out`.

### `scripts/fetch_pr_observation_snapshot.sh`

Keep this script read-only.

Responsibilities:

- Continue aggregating PR metadata, CI/check state, and review snapshot.
- Accept trigger metadata from `wait` or direct snapshot usage.
- Pass trigger metadata to `fetch_pr_review_snapshot.sh`.
- Preserve head revalidation before and after collection.
- Treat stale head as non-success.
- Surface review lifecycle and collection summaries from the review collector without becoming a write boundary.

### `scripts/lib/fetch_pr_review_snapshot.sh`

Keep this script read-only and make it the review lifecycle and collection-summary authority.

Responsibilities:

- Collect issue comments, PR reviews, PR review comments, review requests, and GraphQL review threads through fixed APIs.
- Prefer explicit trigger metadata. Inferred trigger may remain for direct diagnostic snapshot, but normal `wait` must use explicit trigger metadata from post-once or resume.
- Select current run output by trigger boundary, expected head SHA, Codex author heuristic, submitted review id, and review comment id.
- Treat Codex-authored submitted PR review as primary completion.
- Treat reaction, Codex issue comment, and quiet window as auxiliary or fallback signals only.
- Emit selected review body full text and selected review comment bodies in final JSON.
- Emit reviews/review_comments/review_threads collection summary with fetched counts, fetched IDs, selected IDs, unresolved thread IDs/counts, and boundary-before exclusion counts/IDs/reasons.
- Keep `--out` raw bodies as audit/debug only.

## Sequence

```text
actor main-agent
participant wait_pr_observation.sh as wait
participant trigger_codex_review.sh as trigger
participant fetch_pr_observation_snapshot.sh as snapshot
participant fetch_pr_review_snapshot.sh as review
participant GitHub

main-agent -> wait: --repo owner/repo --pr 13 --head-sha sha
wait -> wait: parse and validate args; mode defaults to post-once
wait -> trigger: --repo owner/repo --pr 13 --head-sha sha
trigger -> GitHub: read current PR head
trigger -> GitHub: POST fixed issue comment body "@codex review"
trigger -> GitHub: read current PR head again
trigger -> wait: trigger JSON on captured stdout
wait -> snapshot: poll with --trigger-comment-id and --trigger-created-at
snapshot -> GitHub: read PR metadata and CI/check state
snapshot -> review: fixed read-only review collection
review -> GitHub: issue comments, PR reviews, review comments, requested reviewers, reviewThreads
review -> snapshot: review lifecycle, selected output, collection summary
snapshot -> wait: snapshot JSON
wait -> wait: classify CI and review independently; repeat until terminal/stable/timeout
wait -> main-agent: final JSON on stdout
wait -> main-agent: bounded progress on stderr
```

## Mode Contract

### Default `post-once`

Invocation:

```sh
wait_pr_observation.sh --repo owner/repo --pr 13 --head-sha abc123
```

Contract:

- Creates a new fixed `@codex review` trigger exactly once for this wait process.
- Does not auto-reuse existing `@codex review` comments, even on the same head SHA.
- Uses the created trigger as the only boundary.
- Fails closed on stale head, permission failure, POST failure, ambiguous recovery, or schema failure.

### Explicit `resume`

Invocation:

```sh
wait_pr_observation.sh \
  --repo owner/repo \
  --pr 13 \
  --head-sha abc123 \
  --trigger-mode resume \
  --trigger-comment-id 456 \
  --trigger-created-at 2026-06-09T10:00:00Z
```

Contract:

- Does not POST.
- Requires both trigger metadata fields.
- Continues collection from the same trigger boundary to current time.
- Captures reviews/review comments/review threads that appeared after the previous timeout and before resume start.
- Treats head mismatch as stale/non-success.

## JSON Contract

The final `stdout` JSON should remain one JSON text and include these stable top-level areas:

```json
{
  "script": "wait_pr_observation.sh",
  "status": "passed|failed|pending|running|none|timeout|stale_head|unknown|human_gate",
  "overall_status": "passed|failed|pending|running|none|timeout|stale_head|unknown|human_gate",
  "normalized_status": "passed|failed|pending|running|none|timeout|stale_head|unknown|human_gate",
  "observation_complete": true,
  "repo": "owner/repo",
  "pr": 13,
  "expected_head_sha": "abc123",
  "current_head_sha": "abc123",
  "head": {
    "expected": "abc123",
    "before_trigger": "abc123",
    "after_trigger": "abc123",
    "current": "abc123",
    "matches_expected": true,
    "stale_phase": null
  },
  "trigger": {
    "mode": "post-once",
    "source": "created_by_wait",
    "action": "posted",
    "body": "@codex review",
    "body_sha256": "<sha256>",
    "comment_id": 456,
    "node_id": "IC_kw...",
    "created_at": "2026-06-09T10:00:00Z",
    "updated_at": "2026-06-09T10:00:00Z",
    "html_url": "https://github.com/owner/repo/pull/13#issuecomment-456",
    "author": "github-login",
    "head_sha_before_post": "abc123",
    "head_sha_after_post": "abc123",
    "recovered_after_post_error": false
  },
  "summary": {
    "ci": "passed",
    "review": "commented",
    "head": "matched"
  },
  "ci": {
    "status": "passed"
  },
  "codex_review": {
    "lifecycle": {
      "status": "completed",
      "completion_signal": "submitted_pull_request_review",
      "confidence": "high",
      "selected_review_ids": [987],
      "selected_review_comment_ids": [654],
      "selected_review_thread_ids": ["PRRT_..."]
    },
    "selected_reviews": [
      {
        "id": 987,
        "author": "codex",
        "state": "commented",
        "submitted_at": "2026-06-09T10:05:00Z",
        "commit_id": "abc123",
        "body": "full selected review body text"
      }
    ],
    "selected_review_comments": [
      {
        "id": 654,
        "review_id": 987,
        "author": "codex",
        "created_at": "2026-06-09T10:06:00Z",
        "path": "src/example.py",
        "line": 12,
        "body": "full selected review comment body text"
      }
    ],
    "collection_summary": {
      "reviews": {
        "fetched_count": 1,
        "fetched_ids": [987],
        "selected_ids": [987],
        "boundary_before_excluded_count": 0,
        "boundary_before_excluded_ids": [],
        "boundary_before_exclusion_reasons": []
      },
      "review_comments": {
        "fetched_count": 1,
        "fetched_ids": [654],
        "selected_ids": [654],
        "boundary_before_excluded_count": 0,
        "boundary_before_excluded_ids": [],
        "boundary_before_exclusion_reasons": []
      },
      "review_threads": {
        "fetched_count": 1,
        "fetched_ids": ["PRRT_..."],
        "selected_ids": ["PRRT_..."],
        "unresolved_count": 0,
        "unresolved_ids": [],
        "boundary_before_excluded_count": 0,
        "boundary_before_excluded_ids": [],
        "boundary_before_exclusion_reasons": []
      }
    }
  },
  "review": {
    "status": "commented"
  },
  "resume": {
    "available": false,
    "reason": null,
    "command_hint": null,
    "trigger_comment_id": 456,
    "trigger_created_at": "2026-06-09T10:00:00Z",
    "head_sha": "abc123"
  },
  "limitations": [],
  "recommended_next_action": "merge_ready|address_review_feedback|wait_or_resume|rerun_for_current_head|human_gate"
}
```

Compatibility note:

- Existing `review` can remain for compatibility, but `codex_review.lifecycle` should become the clearer issue-level contract for Codex review completion.
- `review.signals` may still exist, but callers should not need to infer selected Codex review bodies from raw signals.

## Status and Completion Rules

- `passed`: head matches expected, CI is passed, submitted Codex PR review is observed or review state is explicitly merge-ready, and no blocking limitations remain.
- `human_gate`: CI/review result requires human or main-agent action, such as changes requested, unresolved threads, ambiguous completion, fallback-only completion, draft PR, or permission uncertainty.
- `failed`: CI failed or fixed collection failed in a way that gives a terminal non-success result.
- `timeout`: deadline/limit reached before both CI and Codex review lifecycle complete.
- `stale_head`: expected head mismatched before trigger, after trigger, or during observation.

Completion primary:

- `codex_review.lifecycle.completion_signal=submitted_pull_request_review`.

Fallback signals:

- Codex issue comment, reaction, review-comment-only activity, and quiet window may support `confidence=low|medium`, but must not be reported as primary completion.

## Stale Head Handling

The design uses three stale checkpoints:

1. Before trigger:
   - `trigger_codex_review.sh` reads current PR head.
   - If mismatched, no POST occurs.
   - Final JSON reports stale/non-success.
2. Immediately after trigger:
   - Trigger metadata is retained.
   - Final JSON reports stale/non-success.
   - The trigger comment is not deleted.
3. During polling:
   - Snapshot head revalidation detects drift.
   - Wait terminates as stale/non-success.
   - Resume metadata may be present for audit but should recommend rerun for the current head, not reuse as success.

## `--out` Boundary

`--out` remains optional debug/audit storage.

Allowed artifacts:

- `result.json`: exact copy of stdout final JSON.
- `latest.json`: latest snapshot.
- `events.ndjson`: bounded polling events.
- `latest_delta.json`: latest diff metadata.
- `snapshots/`: per-poll copies.
- `raw/`: fixed raw GitHub collection output and body audit files.

Boundary:

- `--out` must not contain the only copy of selected review body full text.
- `--out` must not redefine final status.
- The main agent should be able to decide the next action from stdout alone.

## Test Strategy

Use `tests/unit/infra/test_init_update.py` because existing github-pr-observation tests already install and execute shipped asset scripts with fake `gh`.

### Trigger write tests

- Default `wait_pr_observation.sh` invokes `trigger_codex_review.sh` exactly once.
- The fixed POST call uses only:
  - `gh api --method POST repos/owner/repo/issues/13/comments -f body=@codex review`
- No caller-provided body, endpoint, method, GraphQL, header, `jq`, body file, or raw `gh` args can pass usage validation.
- Trigger stdout is captured and does not leak into user-facing stdout.
- Trigger diagnostics do not appear in stdout.
- POST failure does not cause blind retry.
- Exact one-comment recovery after POST response failure is accepted.
- Zero or multiple recovery candidates fail closed.

### Mode validation tests

- No `--trigger-mode` defaults to `post-once`.
- Default `post-once` plus `--trigger-comment-id` or `--trigger-created-at` is usage error.
- `--trigger-mode resume` without either trigger metadata field is usage error.
- `resume` does not call trigger script or POST endpoint.
- `resume` passes explicit trigger metadata to every snapshot poll.

### Head SHA tests

- Pre-trigger mismatch does not POST and returns stale/non-success JSON.
- Post-trigger mismatch retains trigger metadata and returns stale/non-success JSON.
- Polling mismatch returns stale/non-success and does not delete trigger.

### Review lifecycle tests

- A Codex-authored submitted PR review after trigger is primary completion.
- Non-Codex submitted PR review after trigger is not selected as Codex completion.
- PR review before trigger is excluded with boundary-before evidence.
- PR review comment linked to selected review is included with full body.
- Review thread unresolved IDs/counts are surfaced.
- Reviews/review_comments/review_threads fetched counts, fetched IDs, selected IDs, and boundary-before exclusion evidence are present.
- Quiet window fallback is low-confidence and not primary completion.

### Stdout/stderr/out tests

- `stdout` parses as exactly one JSON text.
- Final JSON contains selected review body full text.
- `stderr` contains bounded progress only.
- `--progress none` suppresses progress.
- `--out/result.json` equals stdout.
- `summary.md` is not generated.
- Selected review body full text is not available only under `--out`.

### Scaffold/package tests

- Installed asset list includes new `scripts/trigger_codex_review.sh`.
- Package data includes hidden install-root path and the new script.
- Update/init tests continue to verify the installed layout mirrors `install_root`.

## Requirement Mapping

- AC-001: `wait` default `post-once`, trigger script called once, trigger metadata retained.
- AC-002: `trigger_codex_review.sh` fixed POST only, strict validation.
- AC-003: `wait` captures trigger stdout, emits one final JSON, preserves stderr/`--out` boundary, includes selected body full text.
- AC-004: `fetch_pr_review_snapshot.sh` selects Codex-authored submitted PR review as primary completion.
- AC-005: `wait` and snapshot classification keep CI and review lifecycle independent until final status.
- AC-006: trigger and snapshot head checks produce stale/non-success across all three phases.
- AC-007: trigger POST failure recovery is exact-match only; no blind retry.
- AC-008: `resume` mode reuses explicit trigger metadata without POST and collects reviews/comments/threads from the original boundary.
- EC-001: trigger POST permission failure becomes JSON limitation/non-success.
- EC-002: missing submitted PR review becomes timeout, fallback, or human gate with confidence/limitations.
- EC-003: CI failure plus review completion remains non-merge-ready.
- EC-004: CI completion without review completion continues waiting or times out as review pending.
- EC-005: existing trigger comments are not reused in default mode.
- EC-006: `--out` is copy/debug only.
- EC-007: timeout final JSON exposes resume metadata and collection evidence for resume.

## Risks and Tradeoffs

- Output size grows because selected review body full text is included in stdout. This is intentional because stdout is the authority and avoids unsafe or noisy follow-up API exploration.
- Codex author login may vary. The collector should keep the current heuristic initially, record selected author evidence, and express uncertainty through `confidence` and `limitations`.
- Existing inferred-trigger behavior is useful for direct diagnostic snapshot, but normal wait must not depend on it.
- Adding a write to a formerly read-only skill is a contract change. The mitigation is a separate fixed write script, strict validation, explicit documentation, and fake-`gh` tests proving the endpoint/body boundary.
- Recovery after POST failure can be tricky. If exact one-comment recovery is not implemented in the first implementation slice, the safe fallback is fail closed with no retry.

## Open Questions

- None blocking for design adoption.
- Implementation should verify the exact GitHub response fields available from the fixed comment POST and record any schema limitations as machine-readable `limitations`.
- Implementation should decide whether the new trigger script is public entrypoint in `SKILL.md` or internal-only. Recommended: document it as a fixed helper called by `wait`, not as a normal user workflow, to avoid shifting trigger choice back to the caller.
