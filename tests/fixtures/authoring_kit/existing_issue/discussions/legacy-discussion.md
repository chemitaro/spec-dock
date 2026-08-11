---
種別: pr-repair-batch
ID: "20260630t083605z-pr-repair-batch"
タイトル: "PR Repair Batch"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-30"
親: ["iss-00246"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260630t083605z-pr-repair-batch PR Repair Batch

## PR / Observation Metadata

- PR URL: https://github.com/chemitaro/spec-dock/pull/249
- PR number: 249
- Repository: chemitaro/spec-dock
- Base branch: main
- Head branch: iss-00246-dogfooding-update-runtime-mirror-sync
- Latest head SHA: 6d9d8aa243e3323141046c58f14292c1b1b6e961
- Observation command: `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh --repo chemitaro/spec-dock --pr 249 --head-sha 6d9d8aa243e3323141046c58f14292c1b1b6e961 --timeout-seconds 1800 --poll-interval-seconds 30 --quiet-seconds 90 --same-fingerprint-count 2 --out /private/tmp/spec-dock-pr-249-observation-1`
- Observation final JSON / evidence: `/private/tmp/spec-dock-pr-249-observation-1/result.json`
- Observation status: failed; `provider-tests` failed in `Run provider static analysis`
- Trigger comment id: 4841448638
- Trigger created_at: 2026-06-30T08:35:05Z
- Trigger boundary: current trigger boundary for head `6d9d8aa243e3323141046c58f14292c1b1b6e961`
- Resume metadata: none yet; first observation posted the trigger
- New trigger approved: no
- Observation limitation: none reported by PR observation
- Batch status: repair implemented; awaiting latest-head re-observation

## Batch Purpose

Use this batch to triage review findings, observed GitHub Actions CI failures, merge blockers, and observation limitations after PR observation and before repair delegation. The batch separates validity from need-to-fix, groups related concerns, creates repair units when needed, and records residual risk for the final merge-prepared decision. PR observation intentionally does not observe external/non-Actions checks; record GitHub UI or external CI confirmation as residual risk or a human gate when branch protection depends on them.

## Concern Catalog

| concern_id | concern | related_inventory_ids | suspected_root_cause | repair_unit | notes |
| --- | --- | --- | --- | --- | --- |
| C001 | `provider-tests` lint failure | INV-001 | `tests/unit/infra/test_init_update.py` is not in `ruff format` canonical style after the Issue 246 test additions | U001 | CI log shows `ruff format check` would reformat one file; no runtime logic failure was observed. |

## Inventory

| ID | source_type | concern | failure_class | evidence | summary | validity | risk_class | need_to_fix | disposition | repair_unit | status | rationale | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| INV-001 | GitHub Actions CI | C001 | `check_failure:provider-tests` | PR observation `/private/tmp/spec-dock-pr-249-observation-1/result.json`; `gh run view 28431280075 --job 84246330373 --log` | `make lint` failed because `ruff format check` would reformat `tests/unit/infra/test_init_update.py` | valid | blocking | yes | fix-now | U001 | implemented | Protected CI gate failure; formatting-only repair was applied and local checks passed. | Latest-head re-observation still required. |

## Classification Values

- `validity`: `valid` / `partially-valid` / `false-positive` / `duplicate` / `unknown`
- `failure_class`: `check_failure:<actions_job_or_workflow_name>` / `review_feedback:<topic>` / `merge_conflict` / `base_branch_conflict` / `permission_or_auth` / `external_or_flaky` / `timeout` / `unknown`
- `risk_class`: `blocking` / `material-follow-up` / `minor` / `false-positive` / `duplicate`
- `need_to_fix`: `yes` / `no` / `follow-up` / `human-decision`
- `disposition`: `fix-now` / `follow-up` / `no-action` / `covered-by` / `needs-human`
- `status`: `untriaged` / `triaged` / `unit-needed` / `unit-created` / `implemented` / `reobserved-pass` / `blocked`

## Per-Concern Analysis

### C001

- Covered inventory IDs: INV-001
- Validity analysis: valid. The CI log deterministically identifies a `ruff format check` failure in `tests/unit/infra/test_init_update.py`.
- Need-to-fix decision: yes. The failure blocks the Provider CI gate.
- Root cause: Issue 246 test additions and a reviewer follow-up assertion were committed before running the repository format check.
- Options considered:
  - Run the formatter for the single file and keep the diff formatting-only.
  - Manually apply the exact formatting suggested by `ruff format check`.
- Recommended disposition: fix-now via U001.
- Rationale: A single-file format repair is the smallest safe fix.
- Residual risk: Until the branch is re-pushed and re-observed, CI remains blocking.

## Repair Queue

| unit_id | source_batch | covered_ids | disposition | risk_class | repair_unit_disc | status | Implementation Plan | Re-observation Result | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U001 | `20260630t083605z-pr-repair-batch` | INV-001 | fix-now | blocking | `20260630t083631z-disc-pr-repair-unit-u001-check-failure-provider-tests.md` | implemented | Format only `tests/unit/infra/test_init_update.py`; run local format check and focused Issue 246 tests; commit and push. | pending | Pending latest-head re-observation. |

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
- No observed GitHub Actions CI failure remains.
- External/non-Actions check state has either been confirmed outside PR observation or is recorded as a human gate/residual risk; do not treat missing Checks API/status rollup evidence as observed pass evidence.
- No blocking review feedback remains.
- No visible merge conflict or equivalent merge blocker remains.
- No `untriaged` inventory item remains.
- No unresolved `needs-human` item remains.
- No `blocking` item has an incomplete `fix-now` repair unit.
- Every `follow-up`, `no-action`, `covered-by`, `duplicate`, or `false-positive` item has rationale and residual risk where relevant.
- Observation limitation handling, resume metadata, trigger boundary, and new trigger approval status are recorded.
- Review-thread unresolved state is known, or any unresolved-thread limitation is explicitly waived and recorded as residual risk.
- `review-clean` is reported separately from `merge-prepared`; `review-clean: no` may still be `merge-prepared: yes` when all remaining items are triaged and non-blocking.
