---
種別: disc
ID: "20260620t025616z-disc"
タイトル: "PR Repair Unit U002 Codex Review Feedback"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
親: ["iss-00218"]
関連: ["#220"]
authority: "proposed"
derived_from: ["20260619t184139z-pr-repair-batch"]
reflected_to: ["report.md"]
---

# PR Repair Unit U002 Codex Review Feedback

## Repair Unit Metadata

- source_batch: `20260619t184139z-pr-repair-batch`
- unit_id: `U002`
- covered_ids: `I007`, `I008`, `I009`, `I010`
- PR: https://github.com/chemitaro/spec-dock/pull/220
- source_links:
  - https://github.com/chemitaro/spec-dock/pull/220#discussion_r3445140688
  - https://github.com/chemitaro/spec-dock/pull/220#discussion_r3445140690
  - https://github.com/chemitaro/spec-dock/pull/220#discussion_r3445140692
  - https://github.com/chemitaro/spec-dock/pull/220#discussion_r3445140695
- failure_class: `review_feedback:no-findings-promotion-guards`
- risk_class: `blocking`
- disposition: `fix-now`

## Validity Analysis

The four PR review comments are valid. They point to the same boundary bug family: a strict Codex no-findings issue comment was allowed to promote PR review completion without enough proof that it is the latest current Codex issue signal and without honoring all active review blockers.

## Need-To-Fix Decision

Fix now. The feedback affects the merge-prepared decision produced by the PR observation skill. If left unchanged, the tool can incorrectly classify a PR as review-complete even when a later Codex issue comment, GitHub `REVIEW_REQUIRED`, or active `CHANGES_REQUESTED` review still requires human action.

## Root Cause

- The no-findings candidate list accepted any current Codex issue comment matching the strict no-findings allow-list, instead of requiring the latest current Codex issue comment to be no-findings.
- The promotion gate excluded `CHANGES_REQUESTED` GraphQL review decisions, but did not exclude `REVIEW_REQUIRED`.
- The promotion gate did not account for active REST review signals with `changes_requested` state when GraphQL reviewDecision was absent or unavailable.
- `no_completion_evidence` treated submitted pull request reviews as explicit completion but did not treat `codex_no_findings_issue_comment` as explicit completion after it became a trusted completion signal.

## Options Considered

- Option A: strengthen no-findings promotion guards in the collector and keep the existing `codex_no_findings_issue_comment` additive signal.
  - Pros: smallest behavior-preserving fix; keeps the user-approved Option A semantics while closing false-positive paths.
  - Cons: retains strict allow-list maintenance burden for future Codex wording changes.
- Option B: revert no-findings issue comments to non-promoting fallback.
  - Pros: conservative.
  - Cons: rejects the issue requirement and reintroduces the PR #216 false-block class.
- Option C: defer to follow-up.
  - Pros: avoids expanding current PR.
  - Cons: leaves a blocking review correctness bug in the active PR.

## Recommended Design

Adopt Option A.

- Only the latest current Codex issue comment can provide `codex_no_findings_issue_comment`.
- `REVIEW_REQUIRED` and active `changes_requested` reviews block no-findings promotion.
- `codex_no_findings_issue_comment` is explicit completion evidence when it passes the stronger promotion gate.

## Implementation Plan

1. Update the provider-side PR review snapshot script under `src/spec_dock/assets/install_root/`.
2. Sync the dogfooding `.agents/` mirror from the provider asset.
3. Add regression tests for:
   - no-findings followed by a later generic Codex issue comment,
   - no-findings while GitHub reviewDecision is `REVIEW_REQUIRED`,
   - no-findings while an active REST review is `CHANGES_REQUESTED`,
   - no-findings as explicit completion evidence.
4. Run focused and broader PR observation regression tests.

## Validation Plan

- `uv run pytest tests/unit/infra/test_init_update.py -k "issue_218_s01" --maxfail=1 -vv`
- `uv run pytest tests/unit/infra/test_init_update.py -k "github_pr_observation or pr_observation or fallback_issue_comment or no_findings or issue_218" --maxfail=1 -vv`
- `./spec-dock/scripts/spec-dock validate`
- `git diff --check`

## Implementation Result

- The provider and dogfooding PR review snapshot scripts now require the latest current Codex issue comment to be the strict no-findings signal.
- No-findings promotion now blocks on `REVIEW_REQUIRED` and active `changes_requested` reviews.
- `codex_no_findings_issue_comment` now counts as explicit completion evidence for `no_completion_evidence`.
- Regression tests were added for all four review comments.

## Commit Evidence

- Pending at creation time; this repair unit is expected to be committed with the U002 fix.

## Re-observation Result

- Pending at creation time. PR re-observation must be performed after the U002 commit is pushed.

## Residual Risk / Follow-up

- Strict no-findings wording remains intentionally narrow. Future Codex wording changes may require an explicit allow-list update.
- This unit does not resolve the separate SpecDock script review-trigger bug mentioned by the user; that is a follow-up outside PR #220.
