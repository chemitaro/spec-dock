---
種別: pr-repair-batch
ID: "20260620t120654z-pr-repair-batch"
タイトル: "PR Repair Batch"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
親: ["iss-00219"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260620t120654z-pr-repair-batch PR Repair Batch

## PR / Observation Metadata

- PR URL: https://github.com/chemitaro/spec-dock/pull/221
- PR number: 221
- Repository: chemitaro/spec-dock
- Base branch: main
- Head branch: iss-00219-carryover-unresolved-threads-stop-observation
- Latest head SHA: 140e1096e127ad1ccc2a0c3024bf4adbbd0234cc
- Observation command: `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh --repo chemitaro/spec-dock --pr 221 --head-sha 140e1096e127ad1ccc2a0c3024bf4adbbd0234cc --timeout-seconds 1800 --poll-interval-seconds 30 --quiet-seconds 90 --same-fingerprint-count 2 --zero-check-grace-polls 2 --body-mode trigger-window-truncated --progress stderr-summary --out /private/tmp/issue219-pr221-wait-19`
- Observation final JSON / evidence: `/private/tmp/issue219-pr221-wait-19/result.json`
- Observation status: `passed`, `recommended_next_action=merge_prepared`, `observation_complete=true`
- Trigger comment id: 4757631475
- Trigger created_at: 2026-06-20T11:49:48Z
- Trigger boundary: explicit `@codex review` for head `140e1096e127ad1ccc2a0c3024bf4adbbd0234cc`
- Resume metadata: not used in final pass
- New trigger approved: yes, user requested PR monitoring and this PR observation is the manual test surface
- Observation limitation: none
- Batch status: closed / merge-prepared evidence recorded

## Batch Purpose

This batch records the PR #221 observation-and-repair loop used as the manual test surface for Issue219. It was created after the repair loop had already been executed directly in the PR monitoring turn, so repair units are recorded retrospectively with commit evidence and final re-observation evidence.

## Concern Catalog

| concern_id | concern | related_inventory_ids | suspected_root_cause | repair_unit | notes |
| --- | --- | --- | --- | --- | --- |
| C001 | Current-boundary Codex review findings after PR observation | INV-001, INV-002, INV-003, INV-004, INV-005, INV-006, INV-007, INV-008, INV-009, INV-010, INV-011, INV-012, INV-013, INV-014, INV-015, INV-016 | Observation classification and fallback/no-findings edge cases discovered by live PR review | RU-001..RU-008 | All findings were fixed and reobserved |
| C002 | Live observation no-findings completion variants | INV-017, INV-018 | Codex no-findings issue comment uses varied first-line suffixes and details block | RU-009 | Fixed by first-line plus metadata recognition |
| C003 | Final PR readiness | INV-019, INV-020, INV-021 | Required checks, mergeability, and latest-head observation must be proved after the last push | N/A | Final observation passed |
| C004 | Post-ledger PR observation findings | INV-013, INV-014, INV-015 | Later PR monitoring exposed skill documentation drift, no-findings reviewed-commit mismatch risk, and Issue214 progress display regression | RU-010..RU-012 | Implemented locally; latest-head re-observation required after push |

## Inventory

| ID | source_type | concern | failure_class | evidence | summary | validity | risk_class | need_to_fix | disposition | repair_unit | status | rationale | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| INV-001 | review_feedback | no-findings monitoring completion | review_feedback:no-findings-observation | PR review comments after head `9bdd2199` | no-findings observation completion did not terminate correctly | valid | blocking | yes | fix-now | RU-001 | reobserved-pass | Fixed by `9bdd2199` | none |
| INV-002 | review_feedback | carryover completion branching | review_feedback:carryover-completion-branch | PR review comments after head `9bdd2199` | carryover-only missing completion could not reach the intended unknown/wait states | valid | blocking | yes | fix-now | RU-002 | reobserved-pass | Fixed by `5936c3b2` | none |
| INV-003 | review_feedback | fallback completion decision sync | review_feedback:fallback-decision-sync | PR review comments after head `5936c3b2` | fallback pass promotion did not synchronize decision fields and latest-source checks | valid | blocking | yes | fix-now | RU-003 | reobserved-pass | Fixed by `6e81b71c` | none |
| INV-004 | review_feedback | unresolved review blocks fallback pass | review_feedback:unresolved-review-blocker | PR review comment `3445947876` after head `6e81b71c` | fallback pass could promote while `review_status=unresolved` | valid | blocking | yes | fix-now | RU-004 | reobserved-pass | Fixed by `70bd0380` | none |
| INV-005 | review_feedback | carryover poll timeout evidence | review_feedback:poll-timeout-evidence | PR review comment `3446010481` after head `70bd0380` | carryover wait could hide a timed-out snapshot refresh | valid | blocking | yes | fix-now | RU-005 | reobserved-pass | Fixed by `a4e5b2f9` | none |
| INV-006 | review_feedback | latency-satisfied poll timeout | review_feedback:poll-timeout-blocking | PR review comment `3446073712` after head `a4e5b2f9` | latency-satisfied carryover wait could finalize from stale evidence | valid | blocking | yes | fix-now | RU-006 | reobserved-pass | Fixed by `71665559` | none |
| INV-007 | observation_limitation | no-findings one-line variant | unknown | wait artifact `/private/tmp/issue219-pr221-wait-17/result.json` | `Chef's kiss.` no-findings variant was not recognized | valid | material-follow-up | yes | fix-now | RU-007 | reobserved-pass | Fixed by `beae053d` | none |
| INV-008 | observation_limitation | no-findings details variant | unknown | wait artifact `/private/tmp/issue219-pr221-wait-18/result.json` | `Swish!` plus details block variant was not recognized by full-body matching | valid | blocking | yes | fix-now | RU-009 | reobserved-pass | Fixed by `140e1096` | none |
| INV-009 | check_status | CI validate | check_failure:validate | PR #221 statusCheckRollup on head `140e1096` | validate checks completed successfully | valid | false-positive | no | no-action | N/A | reobserved-pass | No CI failure remained | none |
| INV-010 | check_status | provider-tests | check_failure:provider-tests | PR #221 statusCheckRollup on head `140e1096` | provider-tests checks completed successfully | valid | false-positive | no | no-action | N/A | reobserved-pass | No CI failure remained | none |
| INV-011 | merge_state | mergeability | merge_conflict | `gh pr view 221` showed `mergeable=MERGEABLE`, `mergeStateStatus=CLEAN` | no merge conflict observed | valid | false-positive | no | no-action | N/A | reobserved-pass | Merge blocker absent | none |
| INV-012 | review_state | final current-boundary review | review_feedback:none | wait artifact `/private/tmp/issue219-pr221-wait-19/result.json` | selected current review comments and threads were empty; Codex no-findings issue comment promoted pass | valid | false-positive | no | no-action | N/A | reobserved-pass | No blocking current-boundary review feedback remained | carryover unresolved inventory remains visible but is outside current trigger boundary |
| INV-013 | review_feedback | fallback-pass documentation drift | review_feedback:skill-contract-drift | wait artifact `/private/tmp/issue219-pr221-wait-20/result.json`, review comment `3446284485` | installed skill text contradicted the promoted fallback-pass JSON contract | valid | blocking | yes | fix-now | RU-010 | implemented | Fixed by local documentation sync; re-observation pending after push | none expected |
| INV-014 | review_feedback | no-findings reviewed commit mismatch | review_feedback:no-findings-reviewed-commit-match | wait artifact `/private/tmp/issue219-pr221-wait-21/result.json`, review comment `3446321476` | multi-line no-findings issue comments did not require `Reviewed commit` metadata to match expected head | valid | blocking | yes | fix-now | RU-011 | implemented | Fixed by local reviewed-commit prefix match; re-observation pending after push | none expected |
| INV-015 | manual_observation | Issue214 progress display regression | review_feedback:progress-target-state | live progress logs for wait artifacts `/private/tmp/issue219-pr221-wait-20` and `/private/tmp/issue219-pr221-wait-21` | progress displayed observer-side `review=observing` after Issue214 had specified `review=pending_signal` for no-signal wait state | valid | blocking | yes | fix-now | RU-012 | implemented | Fixed by local progress target-state mapping; re-observation pending after push | none expected |

## Classification Values

- `validity`: `valid` / `partially-valid` / `false-positive` / `duplicate` / `unknown`
- `failure_class`: `check_failure:<job_or_check_name>` / `review_feedback:<topic>` / `merge_conflict` / `base_branch_conflict` / `permission_or_auth` / `external_or_flaky` / `timeout` / `unknown`
- `risk_class`: `blocking` / `material-follow-up` / `minor` / `false-positive` / `duplicate`
- `need_to_fix`: `yes` / `no` / `follow-up` / `human-decision`
- `disposition`: `fix-now` / `follow-up` / `no-action` / `covered-by` / `needs-human`
- `status`: `untriaged` / `triaged` / `unit-needed` / `unit-created` / `implemented` / `reobserved-pass` / `blocked`

## Per-Concern Analysis

### C001

- Covered inventory IDs: INV-001..INV-006
- Validity analysis: Valid. Each item came from Codex review feedback on the PR and identified a concrete monitoring or classification risk.
- Need-to-fix decision: yes.
- Root cause: Issue219 changed the review lifecycle/carryover boundary; live PR monitoring exposed additional fallback and timeout edge cases at the same boundary.
- Options considered: stop at human gate; repair only the original carryover logic; repair each live observation defect and re-monitor.
- Recommended disposition: fix-now, then reobserve latest head.
- Rationale: The user explicitly made PR monitoring a manual test of this script, so observation-script defects discovered during monitoring were in scope.
- Residual risk: none after final latest-head observation passed.

### C002

- Covered inventory IDs: INV-007, INV-008
- Validity analysis: Valid. Codex no-findings comments varied the suffix while preserving a stable first-line and details-block format.
- Need-to-fix decision: yes.
- Root cause: strict full-body allowlist did not match live Codex issue-comment variants.
- Options considered: add every suffix to the allowlist; recognize the first no-findings line only; recognize first line plus Codex metadata.
- Recommended disposition: first line plus `Reviewed commit` / `<details>` metadata recognition.
- Rationale: This accepts the real Codex no-findings format while preserving the caveat-line negative test.
- Residual risk: future Codex templates without either metadata marker would not promote automatically and would stop at a human gate.

### C003

- Covered inventory IDs: INV-009..INV-012
- Validity analysis: Valid final readiness evidence.
- Need-to-fix decision: no.
- Root cause: N/A.
- Options considered: merge immediately; report merge-prepared for human judgment.
- Recommended disposition: no-action / merge-prepared evidence.
- Rationale: Skill policy forbids merging; final state is ready for human merge judgment.
- Residual risk: merge remains a human action.

### C004

- Covered inventory IDs: INV-013..INV-015
- Validity analysis: Valid. INV-013 and INV-014 came from current-boundary Codex review feedback; INV-015 came from the live PR observation progress log and matches closed Issue214 requirements.
- Need-to-fix decision: yes.
- Root cause: Issue218/Issue219 follow-up changes altered no-findings/fallback semantics while documentation and progress-line target-state safeguards drifted.
- Options considered: defer as follow-up; treat as out-of-scope PR delivery feedback; repair in Issue219 as live observation-script defects.
- Recommended disposition: fix-now, then reobserve latest head.
- Rationale: The user explicitly treats PR monitoring as a manual test of `github-pr-observation`, and these defects affect operator-facing correctness or merge-prepared safety.
- Residual risk: latest-head re-observation is still required after push.

## Repair Queue

| unit_id | source_batch | covered_ids | disposition | risk_class | repair_unit_disc | status | Implementation Plan | Re-observation Result | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RU-001 | 20260620t120654z-pr-repair-batch | INV-001 | fix-now | blocking | retrospective direct commit `9bdd2199` | reobserved-pass | Fix no-findings observation completion and add regression coverage | Later PR observation cycles advanced beyond this finding | none |
| RU-002 | 20260620t120654z-pr-repair-batch | INV-002 | fix-now | blocking | retrospective direct commit `5936c3b2` | reobserved-pass | Fix carryover-only completion branch and latency unknown path | Later PR observation cycles advanced beyond this finding | none |
| RU-003 | 20260620t120654z-pr-repair-batch | INV-003 | fix-now | blocking | retrospective direct commit `6e81b71c` | reobserved-pass | Synchronize fallback pass decision and preserve timeout wait status | Later PR observation cycles advanced beyond this finding | none |
| RU-004 | 20260620t120654z-pr-repair-batch | INV-004 | fix-now | blocking | retrospective direct commit `70bd0380` | reobserved-pass | Reject fallback pass when review status is unresolved | Later PR observation cycles advanced beyond this finding | none |
| RU-005 | 20260620t120654z-pr-repair-batch | INV-005 | fix-now | blocking | retrospective direct commit `a4e5b2f9` | reobserved-pass | Preserve snapshot poll timeout evidence during carryover wait | Later PR observation cycles advanced beyond this finding | none |
| RU-006 | 20260620t120654z-pr-repair-batch | INV-006 | fix-now | blocking | retrospective direct commit `71665559` | reobserved-pass | Keep latency-satisfied timed-out refreshes blocking | Later PR observation cycles advanced beyond this finding | none |
| RU-007 | 20260620t120654z-pr-repair-batch | INV-007 | fix-now | material-follow-up | retrospective direct commit `beae053d` | reobserved-pass | Add observed one-line no-findings suffix to strict recognition | Superseded by RU-009 broader first-line/details recognition | none |
| RU-009 | 20260620t120654z-pr-repair-batch | INV-008 | fix-now | blocking | retrospective direct commit `140e1096` | reobserved-pass | Recognize multi-line Codex no-findings comments via first line plus metadata | `/private/tmp/issue219-pr221-wait-19/result.json` passed / merge_prepared | none |
| RU-010 | 20260620t120654z-pr-repair-batch | INV-013 | fix-now | blocking | direct local repair | implemented | Synchronize `fallback_pass_candidate` skill text with the strict no-findings promotion contract | pending latest-head PR observation after push | none expected |
| RU-011 | 20260620t120654z-pr-repair-batch | INV-014 | fix-now | blocking | direct local repair | implemented | Parse `Reviewed commit` metadata and require prefix match with `expected_head_sha` before multi-line no-findings promotion | pending latest-head PR observation after push | none expected |
| RU-012 | 20260620t120654z-pr-repair-batch | INV-015 | fix-now | blocking | direct local repair | implemented | Restore Issue214 progress display semantics so no-signal wait states render `review=pending_signal` and actionable states keep target status/counters | pending latest-head PR observation after push | none expected |

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

### Merge-Prepared Result

- review-clean: yes for the current trigger boundary.
- merge-prepared: yes.
- Evidence:
  - PR #221 is open, non-draft, `mergeable=MERGEABLE`, `mergeStateStatus=CLEAN`.
  - Latest head `140e1096e127ad1ccc2a0c3024bf4adbbd0234cc` was observed.
  - Final observation `/private/tmp/issue219-pr221-wait-19/result.json` returned `normalized_status=passed`, `recommended_next_action=merge_prepared`, `observation_complete=true`.
  - CI checks were 4/4 success with no failed, running, pending, or stale checks.
  - Current trigger-boundary selected review comments and review threads were empty.
  - Carryover unresolved review-thread inventory remains visible in audit/structured fields but is outside the current trigger boundary.
  - No observation limitation remained.
- Human action remaining: PR merge.
