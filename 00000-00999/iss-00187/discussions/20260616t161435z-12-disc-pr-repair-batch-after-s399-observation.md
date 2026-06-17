---
種別: disc
ID: "20260616t161435z-12-disc-pr-repair-batch-after-s399-observation"
タイトル: "PR #190 repair batch after S399 observation"
状態: "implemented-local"
作成者: "orchestrator"
最終更新: "2026-06-16"
親: ["iss-00187-actions-pr-observation-ci-state"]
関連: ["https://github.com/chemitaro/spec-dock/pull/190"]
authority: "proposed"
derived_from: ["/private/tmp/spec-dock-pr190-observation-71120a7b/result.json"]
reflected_to: []
---

# PR #190 repair batch after S399 observation

## PR / Observation Metadata

- PR URL: https://github.com/chemitaro/spec-dock/pull/190
- PR number: 190
- Repository: `chemitaro/spec-dock`
- Base branch: `main`
- Head branch: `iss-00187-actions-pr-observation-ci-state`
- Latest head SHA: `71120a7bccf638ecd957fa27a2309fb77d1f8c5b`
- Observation command: `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh --repo chemitaro/spec-dock --pr 190 --head-sha 71120a7bccf638ecd957fa27a2309fb77d1f8c5b --timeout-seconds 1800 --poll-interval-seconds 30 --quiet-seconds 60 --same-fingerprint-count 2 --body-mode out-only --progress stderr-summary --out /private/tmp/spec-dock-pr190-observation-71120a7b`
- Observation final JSON / evidence: `/private/tmp/spec-dock-pr190-observation-71120a7b/result.json`
- Observation status: `human_gate`
- Trigger comment id: `4720762427`
- Trigger created_at: `2026-06-16T15:59:48Z`
- Trigger boundary: current trigger selected no new reviews/comments/threads; all current selected unresolved count is `0`
- Resume metadata: not applicable for this first latest-head observation
- New trigger approved: yes for this first latest-head `post-once`; no additional trigger approved after this batch
- Observation limitation: none from the script; residual issue is `review_completion_unknown` plus two pre-trigger non-outdated unresolved P1 review threads
- Batch status: `u001-implemented-local-p2-follow-up-applied`

## Batch Purpose

This batch triages PR #190 latest-head observation after the S399 bounded fixture fix. CI passed and the head matched, but the PR cannot be reported as merge-prepared because two non-outdated P1 review threads remain unresolved on latest head. The current trigger window did not select those threads because they predate trigger `4720762427`, so repair work must be driven from this explicit batch rather than from selected current-boundary review output alone.

## Concern Catalog

| concern_id | concern | related_inventory_ids | suspected_root_cause | repair_unit | notes |
| --- | --- | --- | --- | --- | --- |
| C001 | non-terminal Actions runs still expand jobs on every wait poll | INV-001 | job-detail expansion is capped only for terminal green runs, not for running/pending queued runs where run-level status is already decisive | U001 | preserve failed-run diagnostics; avoid rate/budget pressure during wait |
| C002 | external green commit statuses can be blocked by Checks-read limitation when Actions has no runs | INV-002 | generic blocking limitation branch precedes the external-green fallback, so `github_token_permission_denied` for Checks can keep `ci.status=unknown` even with green commit statuses and clean merge state | U001 | preserve blocking limitations for non-green or ambiguous external status evidence |

## Inventory

| ID | source_type | concern | failure_class | evidence | summary | validity | risk_class | need_to_fix | disposition | repair_unit | status | rationale | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| INV-001 | review_feedback | C001 | `review_feedback:actions-job-expansion-bound` | PR review comment `3418873984`, thread `PRRT_kwDOQ99OK86Jzt03`, `pr_observation_checks.py:539` | Bound job expansion for non-terminal Actions runs | valid | blocking | yes | fix-now | U001 | implemented-local-p2-applied | Non-terminal run-level status is enough to keep CI running/pending; U001 now caps non-terminal job expansion at `1` by attempt count, so failed first job-detail attempts do not expand every later non-terminal run; failed-run diagnostics are preserved | External PR re-observation remains pending after orchestrator commit/push |
| INV-002 | review_feedback | C002 | `review_feedback:external-green-permission-limitation` | PR review comment `3418873991`, thread `PRRT_kwDOQ99OK86Jzt09`, `pr_observation_checks.py:1062` | Allow green commit statuses despite missing Checks read | valid | blocking | yes | fix-now | U001 | implemented-local-p2-applied | U001 allows no-Actions + green legacy commit statuses + clean merge state to pass when only Checks/check-runs read is permission-denied, retaining that limitation as informational; direct failed legacy status + same permission-denied path is covered and remains non-pass/blocking | Non-green/pending/failed external status evidence remains non-pass; external PR re-observation remains pending |
| INV-003 | observation | review completion unknown | `unknown` | `/private/tmp/spec-dock-pr190-observation-71120a7b/result.json` | Current trigger window has no completion signal after CI passed | valid | material-follow-up | human-decision | needs-human | none | triaged | This is the designed `review_completion_unknown` human gate, not a script timeout or CI failure | After U001 is fixed and pushed, latest-head PR observation must be rerun; if Codex again posts no current review, final state must remain explicitly human-gated unless user accepts it |

## Per-Concern Analysis

### C001

- Covered inventory IDs: INV-001
- Validity analysis: valid P1. The current collector expands jobs for every non-green run even when run-level status already classifies CI as running/pending.
- Need-to-fix decision: fix now.
- Root cause: `TERMINAL_GREEN_JOB_EXPANSION_CAP` is applied only to `success`, `neutral`, and `skipped` runs.
- Options considered: expand every non-terminal job; skip all non-terminal jobs; cap non-terminal job expansion separately while preserving failed-run details.
- Recommended disposition: cap or defer non-terminal job expansion separately; run-level status remains decisive for running/pending.
- Rationale: This protects wait-loop budget without weakening failure diagnostics.
- Residual risk: A single running job detail may be enough for visibility, but tests should assert bounded expansion and `jobs_summary.collection` evidence.

### C002

- Covered inventory IDs: INV-002
- Validity analysis: valid P1. The green external-status fallback can be shadowed by a generic blocking Checks-read limitation.
- Need-to-fix decision: fix now.
- Root cause: the blocking limitation branch runs before the final pass fallback for commit statuses.
- Options considered: make all Checks-read permission limitations informational; special-case only external-green/no-Actions evidence; move the fallback before generic limitations.
- Recommended disposition: special-case external-green/no-Actions evidence before blocking limitation promotion, with a coverage limitation retained as informational.
- Rationale: This matches the issue requirement while preserving false-pass safety for ambiguous or non-green statuses.
- Residual risk: Non-Actions repos with partial status evidence must remain non-pass when statuses are failed, pending, other, missing, or merge state is not clean.

## Repair Queue

| unit_id | source_batch | covered_ids | disposition | risk_class | repair_unit_disc | status | Implementation Plan | Re-observation Result | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U001 | `20260616t161435z-12-disc-pr-repair-batch-after-s399-observation.md` | INV-001, INV-002 | fix-now | blocking | `20260616t161435z-13-disc-pr-repair-unit-u001-ci-observation-p1.md` | implemented-local-p2-applied | Added focused regressions, updated provider collector, applied P2 follow-up for attempt-based non-terminal cap and failed legacy-status negative coverage, synced dogfooding mirror, and ran focused/broad PR observation tests | pending external re-observation after commit/push | Failed-run diagnostics and non-green external blockers preserved by focused guard selectors; no commit/push was performed in this unit |

## Unit Discussion Plan

Repair unit `20260616t161435z-13-disc-pr-repair-unit-u001-ci-observation-p1.md` is the source of truth for implementation. The worker must not use the raw PR comments alone as the implementation plan.

## Stop Conditions

- Stop at a human gate if U001 requires requirement expansion, new GitHub permissions, a new dependency, or a behavior change outside PR observation CI classification.
- Stop at a human gate if focused tests cannot reproduce either P1 without broad fixture rewrites.
- Stop at a human gate if latest-head re-observation after U001 still has unresolved blocking review feedback.
- Do not post another `@codex review` trigger except through the fixed observation script after a new push.

## Merge-Prepared Gate

`merge-prepared: yes` is not currently satisfied. The current PR state has CI passed and mergeable true, but two non-outdated unresolved P1 threads remain and current review completion is `review_completion_unknown`.
