---
種別: disc
ID: "20260620t051223z-disc"
タイトル: "PR Repair Unit U003"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
親: ["iss-00218"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260620t051223z-disc PR Repair Unit U003

## Repair Unit Metadata

- source_batch: 20260620t051224z-pr-repair-batch
- unit_id: U003
- covered_ids: I001, I002, I003
- source_links:
  - https://github.com/chemitaro/spec-dock/pull/220#discussion_r3445490964
  - https://github.com/chemitaro/spec-dock/pull/220#discussion_r3445490965
  - https://github.com/chemitaro/spec-dock/pull/220#discussion_r3445490966
- failure_class: review_feedback:no-findings-promotion-blockers
- risk_class: blocking
- disposition: fix-now

## Validity Analysis

All three review findings are valid against the current implementation in `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`.

- I001 is valid because `is_codex_authored(login)` currently returns true for any login containing `codex`, so a non-Codex account such as `codex-helper` could be treated as the trusted source of a no-findings completion issue comment.
- I002 is valid because the no-findings branch sets `recommended_next_action=review_completion_observed` but leaves `decision_status_reason=passed`; consumers that inspect `status_reason` cannot distinguish this medium-confidence issue-comment completion transport.
- I003 is valid because `review_decision_requires_review` is false when requested reviewers or teams exist, so `REVIEW_REQUIRED` can fail to block no-findings promotion in the exact case where GitHub is still requiring review.

## Need-To-Fix Decision

Need to fix now. The affected path can emit decision-facing `passed` / `merge_prepared` evidence. A false promotion would let downstream automation or a human merge decision rely on a completion signal that is either untrusted or contradicted by branch protection.

## Root Cause

The initial no-findings issue-comment promotion was deliberately conservative about current head, unresolved threads, changes-requested reviews, and collection failures, but it reused two older coarse concepts:

- `codex_authored` as substring login detection rather than an exact trusted bot allow-list.
- `review_decision_requires_review` as a pending review condition only when GitHub had no explicit review request metadata.

Those concepts are tolerable for broad audit/debug grouping but too weak for promotion to a decision-facing pass. The decision reason also remained generic because the previous final branch did not distinguish submitted-review completion from no-findings issue-comment completion.

## Options Considered

- Option A: Only tighten `is_codex_authored()`.
  - Pros: smallest code change.
  - Cons: leaves `REVIEW_REQUIRED` with requested reviewers and `status_reason` ambiguity unfixed.
- Option B: Add a separate `trusted_codex_authored` flag only for no-findings comments.
  - Pros: avoids changing all existing `codex_authored` audit semantics.
  - Cons: duplicates author semantics and makes future promotion checks easier to misuse.
- Option C: Make `is_codex_authored()` exact allow-list based and use it consistently.
  - Pros: one source of truth, simpler tests, safer for every decision-facing Codex-authored filter.
  - Cons: requires choosing current trusted logins explicitly.
- Option D: Treat every `REVIEW_REQUIRED` as a blocker and report `codex_no_findings_issue_comment` as the decision status reason on the no-findings pass path.
  - Pros: aligns with GitHub branch protection and collector contract.
  - Cons: callers that expected generic `passed` status_reason must use `status` for pass/fail and `status_reason` for why.

## Recommended Design

Combine Option C and Option D:

- Change `is_codex_authored()` to exact trusted login matching for known Codex review bot identities: `codex` and `chatgpt-codex-connector[bot]`.
- Compute `review_decision_requires_review` directly from `reviewDecision == REVIEW_REQUIRED`, independent of requested reviewer/team metadata.
- Keep `review_request_signals` as a pending lifecycle input, but do not let it neutralize the branch-protection blocker.
- When the decision passes due to `completion_signal == codex_no_findings_issue_comment`, set `decision_status_reason` to `codex_no_findings_issue_comment`.
- Add focused regressions for spoofed Codex-like login, `REVIEW_REQUIRED` with requested reviewers, and status reason on successful no-findings promotion.

## Implementation Plan

1. Update `pr_review_snapshot.py` author trust and review-required logic.
2. Update or add focused tests in `tests/unit/infra/test_init_update.py`.
3. Run the focused tests around issue 218 no-findings promotion behavior.
4. Run the narrower CLI/runtime test lane if focused tests pass.
5. Commit, push, trigger a fresh latest-head Codex review, and manually poll PR #220.

## Validation Plan

- `uv run pytest tests/unit/infra/test_init_update.py -k "issue_218_s01_review_collector"`
- If focused tests pass, run `uv run pytest tests/unit/infra/test_init_update.py -k "issue_218"`
- After push, direct polling:
  - `gh pr view 220 --repo chemitaro/spec-dock --json ...`
  - `gh pr checks 220 --repo chemitaro/spec-dock`
  - `gh api` for comments, reviews, inline comments, and GraphQL review thread counts.

## Implementation Result

- Implemented exact trusted Codex login matching through `TRUSTED_CODEX_LOGINS`.
- Implemented `REVIEW_REQUIRED` as a blocker independent of requested reviewer/team metadata.
- Implemented `decision_status_reason=codex_no_findings_issue_comment` when the no-findings issue-comment completion branch is the pass reason.
- Mirrored the provider-side observation script into the checked-in `.agents` dogfooding copy to preserve install_root parity.
- Added focused regressions for requested-reviewer review-required blocking, Codex-like login spoofing, and no-findings pass status reason.

## Commit Evidence

Pending commit and push.

## Re-observation Result

Pending latest-head re-observation.

## Residual Risk / Follow-up

Validation completed before commit:

- `uv run pytest tests/unit/infra/test_init_update.py -k 'issue_218'`: 22 passed.
- `uv run pytest tests/unit/infra/test_init_update.py`: 463 passed.

Potential residual risk is future GitHub/Codex bot login drift. If GitHub changes the Codex bot login, the allow-list should be updated with a regression fixture based on observed API payloads.

## 推奨反映先 (必須)
- `requirement.md`:
  - ...
- `design.md`:
  - ...
- `plan.md`:
  - ...
- `ADR`:
  - ...
- `report.md` Evidence Adoption Ledger:
  - ...

## 未採用 / deferred 理由 (必須)
- 未採用:
  - ...
- deferred:
  - ...

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - ...
- 追加で作る discussion docs:
  - ...
