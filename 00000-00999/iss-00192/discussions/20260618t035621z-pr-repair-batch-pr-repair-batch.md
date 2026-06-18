---
種別: pr-repair-batch
ID: "20260618t035621z-pr-repair-batch"
タイトル: "PR Repair Batch"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-18"
親: ["iss-00192"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260618t035621z-pr-repair-batch PR Repair Batch

## PR / Observation Metadata

- PR URL: https://github.com/chemitaro/spec-dock/pull/206
- PR number: 206
- Repository: chemitaro/spec-dock
- Base branch: main
- Head branch: iss-00192-generate-deps-raw-puml
- Latest head SHA: 03b6953ffdfa24835a71cd925f1fc7ec9357be20
- Observation command: `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh --repo chemitaro/spec-dock --pr 206 --head-sha 03b6953ffdfa24835a71cd925f1fc7ec9357be20 --timeout-seconds 1800 --poll-interval-seconds 30 --quiet-seconds 90 --same-fingerprint-count 2 --zero-check-grace-polls 2 --out /private/tmp/spec-dock-pr-206-observation`
- Observation final JSON / evidence: `/private/tmp/spec-dock-pr-206-observation/result.json`
- Observation status: failed; `provider-tests` failed twice, `validate` passed twice, Codex review comment reported no major issues for `03b6953ffd`
- Trigger comment id: 4737654300
- Trigger created_at: 2026-06-18T03:43:23Z
- Trigger boundary: current `@codex review` trigger for head `03b6953ffdfa24835a71cd925f1fc7ec9357be20`
- Resume metadata: N/A; first observation completed with CI failure
- New trigger approved: no
- Observation limitation: none reported in final JSON
- Batch status: repair unit U001 implemented and locally verified; re-observation pending after commit and push

## Batch Purpose

Use this batch to triage review findings, CI failures, merge blockers, and observation limitations after PR observation and before repair delegation. The batch separates validity from need-to-fix, groups related concerns, creates repair units when needed, and records residual risk for the final merge-prepared decision.

## Concern Catalog

| concern_id | concern | related_inventory_ids | suspected_root_cause | repair_unit | notes |
| --- | --- | --- | --- | --- | --- |
| C001 | Required `provider-tests` failure | I001, I002 | checked-in dogfooding `.meta.json` snapshot baseline in `tests/unit/infra/test_init_update.py` lagged the current dogfooding tree | U001 | Both failing Provider CI runs failed on the same test and same root cause. |

## Inventory

| ID | source_type | concern | failure_class | evidence | summary | validity | risk_class | need_to_fix | disposition | repair_unit | status | rationale | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I001 | CI failure | Required `provider-tests` failure | `check_failure:provider-tests` | GitHub Actions run 27735228335, job 82050572340 | `TestInitUpdate.test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json` failed because observed dogfooding `.meta.json` paths and `depends_on` values diverged from the stored cutover snapshot. | valid | blocking | yes | fix-now | U001 | implemented | Required check failure blocks merge-prepared state. The failing baseline is a checked-in dogfooding snapshot and can be updated to the current tree without changing runtime behavior. | Requires re-observation after commit and push. |
| I002 | CI failure | Required `provider-tests` failure | `check_failure:provider-tests` | GitHub Actions run 27735222347, job 82050555742 | Duplicate Provider CI run failed on the same test and same snapshot mismatch. | duplicate | duplicate | no | covered-by | U001 | implemented | Same head SHA, same workflow, same failed test, same root cause as I001. | Covered by U001 re-observation. |

## Classification Values

- `validity`: `valid` / `partially-valid` / `false-positive` / `duplicate` / `unknown`
- `failure_class`: `check_failure:<job_or_check_name>` / `review_feedback:<topic>` / `merge_conflict` / `base_branch_conflict` / `permission_or_auth` / `external_or_flaky` / `timeout` / `unknown`
- `risk_class`: `blocking` / `material-follow-up` / `minor` / `false-positive` / `duplicate`
- `need_to_fix`: `yes` / `no` / `follow-up` / `human-decision`
- `disposition`: `fix-now` / `follow-up` / `no-action` / `covered-by` / `needs-human`
- `status`: `untriaged` / `triaged` / `unit-needed` / `unit-created` / `implemented` / `reobserved-pass` / `blocked`

## Per-Concern Analysis

### C001

- Covered inventory IDs: I001, I002
- Validity analysis: valid for I001 and duplicate for I002. Both failed CI results are for latest head `03b6953ffdfa24835a71cd925f1fc7ec9357be20`.
- Need-to-fix decision: yes for I001 because `provider-tests` is a required check failure; I002 is covered by the same repair unit.
- Root cause: checked-in dogfooding initiatives gained `.meta.json` files that were not reflected in `_CHECKED_IN_DOGFOODING_META_JSON_PATHS` and `_CHECKED_IN_DOGFOODING_DEPENDS_ON_BY_META_PATH`.
- Options considered: leave as residual risk, remove dogfooding metadata, or update the snapshot baseline. Leaving it blocks merge-prepared; removing metadata would mutate dogfooding data outside this issue; updating the baseline is the smallest CI repair.
- Recommended disposition: fix-now through U001.
- Rationale: the failing assertion is explicitly a snapshot baseline for checked-in dogfooding metadata, and the runtime behavior under this issue remains covered by separate deps raw tests.
- Residual risk: the snapshot is broad and may encode unrelated historical dogfooding additions, but the repair does not alter runtime source or shipped assets.

## Repair Queue

| unit_id | source_batch | covered_ids | disposition | risk_class | repair_unit_disc | status | Implementation Plan | Re-observation Result | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U001 | 20260618t035621z-pr-repair-batch | I001, I002 | fix-now | blocking | `20260618t035702z-disc-pr-repair-unit-u001-check-failure-provider-tests.md` | implemented | Regenerate the checked-in dogfooding `.meta.json` path tuple and `depends_on` baseline from the current `spec-dock/initiatives` tree; run the failed focused test and broader unit lane. | Pending after commit and push. | Snapshot breadth is unrelated to deps-raw runtime behavior, but required check must be green for merge-prepared. |

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
