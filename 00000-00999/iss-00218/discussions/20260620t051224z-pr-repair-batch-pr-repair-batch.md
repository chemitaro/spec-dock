---
種別: pr-repair-batch
ID: "20260620t051224z-pr-repair-batch"
タイトル: "PR Repair Batch"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
親: ["iss-00218"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260620t051224z-pr-repair-batch PR Repair Batch

## PR / Observation Metadata

- PR URL: https://github.com/chemitaro/spec-dock/pull/220
- PR number: 220
- Repository: chemitaro/spec-dock
- Base branch: main
- Head branch: iss-00218-codex-review-fallback-signal-semantics
- Latest head SHA: fa33c967197a6195c66f7bfc05247f1d901d8bc7
- Observation command: manual polling with `gh api`, `gh pr checks`, `gh pr view`, and `sleep`; observation scripts intentionally not used because the current script is known broken in this workflow.
- Observation final JSON / evidence: PR review 4536548634, inline comments 3445490964, 3445490965, 3445490966, unresolved non-outdated review thread count 3.
- Observation status: Codex review completed for latest head with 3 actionable inline findings; CI checks pass; PR is open and mergeStateStatus=CLEAN.
- Trigger comment id: 4756519816
- Trigger created_at: 2026-06-20T04:52:47Z
- Trigger boundary: latest manual `@codex review` comment for head fa33c967197a6195c66f7bfc05247f1d901d8bc7
- Resume metadata: N/A; this batch starts from a completed latest-head Codex review, not a timeout continuation.
- New trigger approved: yes, explicitly requested by user for this manual polling loop.
- Observation limitation: automated observation script not used; direct GitHub REST/GraphQL polling succeeded after occasional connection retries.
- Batch status: implemented; re-observation pending.

## Batch Purpose

Use this batch to triage review findings, CI failures, merge blockers, and observation limitations after PR observation and before repair delegation. The batch separates validity from need-to-fix, groups related concerns, creates repair units when needed, and records residual risk for the final merge-prepared decision.

## Concern Catalog

| concern_id | concern | related_inventory_ids | suspected_root_cause | repair_unit | notes |
| --- | --- | --- | --- | --- | --- |
| C001 | No-findings issue comment promotion can overstate review completion | I001, I002, I003 | The no-findings promotion branch lacks a strict trusted Codex author gate, treats some branch-protection review-required states too narrowly, and does not expose the specific status reason when the medium-confidence issue-comment transport is promoted. | U003 | Same root cause and same function surface; one unit is sufficient. |

## Inventory

| ID | source_type | concern | failure_class | evidence | summary | validity | risk_class | need_to_fix | disposition | repair_unit | status | rationale | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I001 | codex_review_inline_comment | C001 | review_feedback:no-findings-promotion-blockers | comment 3445490964 line 1046 | Require exact trusted Codex login before allowing no-findings issue comments to promote completion. | valid | blocking | yes | fix-now | U003 | implemented | Substring author matching can classify unrelated users/bots as Codex-authored and incorrectly promote completion. | None after exact allow-list and regression test. |
| I002 | codex_review_inline_comment | C001 | review_feedback:no-findings-promotion-blockers | comment 3445490965 line 1333 | Report `codex_no_findings_issue_comment` as the decision status reason when that branch promotes. | valid | minor | yes | fix-now | U003 | implemented | The contract distinguishes completion transports; consumers should not infer this from secondary fields only. | None after decision reason assertion. |
| I003 | codex_review_inline_comment | C001 | review_feedback:no-findings-promotion-blockers | comment 3445490966 line 1081 | Block no-findings promotion when GitHub reports `REVIEW_REQUIRED`, including cases with requested reviewers or teams. | valid | blocking | yes | fix-now | U003 | implemented | Branch protection review-required state is an explicit blocker even when requested reviewer metadata is present. | None after review-required/requested-reviewer regression test. |

## Classification Values

- `validity`: `valid` / `partially-valid` / `false-positive` / `duplicate` / `unknown`
- `failure_class`: `check_failure:<job_or_check_name>` / `review_feedback:<topic>` / `merge_conflict` / `base_branch_conflict` / `permission_or_auth` / `external_or_flaky` / `timeout` / `unknown`
- `risk_class`: `blocking` / `material-follow-up` / `minor` / `false-positive` / `duplicate`
- `need_to_fix`: `yes` / `no` / `follow-up` / `human-decision`
- `disposition`: `fix-now` / `follow-up` / `no-action` / `covered-by` / `needs-human`
- `status`: `untriaged` / `triaged` / `unit-needed` / `unit-created` / `implemented` / `reobserved-pass` / `blocked`

## Per-Concern Analysis

### C001

- Covered inventory IDs: I001, I002, I003
- Validity analysis: valid. All three findings point to the same promotion branch in `pr_review_snapshot.py` and can affect the decision-facing `passed` / `merge_prepared` result.
- Need-to-fix decision: yes. The feature intentionally permits a medium-confidence no-findings issue-comment completion signal, so its trust boundary and blockers must be explicit.
- Root cause: no-findings completion promotion was added with correct head/thread/change-request blockers, but retained broad `is_codex_authored()` substring matching, modeled `REVIEW_REQUIRED` as blocked only when no review-request signals existed, and left `decision_status_reason` as generic `passed`.
- Options considered:
  - Tighten only the author check. Rejects spoofed Codex-like logins but leaves branch-protection and observability gaps.
  - Tighten only the promotion predicate. Preserves author ambiguity and weakens trust in the medium-confidence transport.
  - Tighten trusted author, review-required blockers, and status reason together. This is the smallest complete repair for the three review findings.
- Recommended disposition: fix-now through U003.
- Rationale: one localized implementation and focused regressions can close all three findings without changing the submitted-review completion path.
- Residual risk: trusted login allow-list may need expansion if GitHub changes the Codex bot login; current evidence from PR #220 uses `chatgpt-codex-connector[bot]`.

## Repair Queue

| unit_id | source_batch | covered_ids | disposition | risk_class | repair_unit_disc | status | Implementation Plan | Re-observation Result | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U003 | 20260620t051224z-pr-repair-batch | I001, I002, I003 | fix-now | blocking | 20260620t051223z-disc-pr-repair-unit-u003-no-findings-promotion-blockers.md | implemented | Implemented exact trusted Codex login, review-required blocker, no-findings status reason, mirror parity, and regressions. | Pending latest-head re-observation after commit and push. | Bot login allow-list may need future update if GitHub changes Codex identity. |

## Unit Discussion Plan

Create a repair unit `disc` for each `fix-now` item and each `needs-human` item that needs implementation analysis, design judgment, or options comparison. The worker must use the repair unit discussion, not raw findings, as the source of truth.

Required repair unit checklist:

- `source_batch`
- `unit_id`
- `covered_ids`
- `source_links`
- `failure_class`
- `risk_class`
- `disposition`
- `Validity Analysis`
- `Need-To-Fix Decision`
- `Root Cause`
- `Options Considered`
- `Recommended Design`
- `Implementation Plan`
- `Validation Plan`
- `Implementation Result`
- `Commit Evidence`
- `Re-observation Result`
- `Residual Risk / Follow-up`

## Stop Conditions

Stop at a human gate when any condition applies:

- Any inventory item remains `untriaged`.
- Any unresolved `needs-human` item remains.
- A `blocking` `fix-now` repair unit is incomplete or repeatedly fails.
- Observation output is not for the latest head SHA.
- Timeout or observation limitation lacks resume metadata.
- Resume would cross the recorded trigger boundary.
- A new trigger would be required but has not been approved.
- Scope expansion, requirement expansion, breaking change, migration, secret, deployment setting, permission/auth, external/flaky, or ambiguous review intent is involved.
- Loop limits for the same failure class or total repair attempts are reached.

## Merge-Prepared Gate

Report `merge-prepared: yes` only when all conditions are true:

- PR is open.
- Latest head re-observation is complete and matches the latest head SHA.
- No required check failure remains.
- No non-required check failure remains unless the check is known optional or the user explicitly waived it; waived or optional non-required failures are recorded as residual risk.
- No blocking review feedback remains.
- No visible merge conflict or equivalent merge blocker remains.
- No `untriaged` inventory item remains.
- No unresolved `needs-human` item remains.
- No `blocking` item has an incomplete `fix-now` repair unit.
- Every `follow-up`, `no-action`, `covered-by`, `duplicate`, or `false-positive` item has rationale and residual risk where relevant.
- Observation limitation handling, resume metadata, trigger boundary, and new trigger approval status are recorded.
- Review-thread unresolved state is known, or any unresolved-thread limitation is explicitly waived and recorded as residual risk.
- `review-clean` is reported separately from `merge-prepared`; `review-clean: no` may still be `merge-prepared: yes` when all remaining items are triaged and non-blocking.
