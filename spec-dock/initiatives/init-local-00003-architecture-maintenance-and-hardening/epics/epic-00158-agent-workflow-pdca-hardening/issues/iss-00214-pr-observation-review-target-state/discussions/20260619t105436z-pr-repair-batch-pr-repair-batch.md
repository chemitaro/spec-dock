---
種別: pr-repair-batch
ID: "20260619t105436z-pr-repair-batch"
タイトル: "PR Repair Batch"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["iss-00214"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260619t105436z-pr-repair-batch PR Repair Batch

## PR / Observation Metadata

- PR URL: https://github.com/chemitaro/spec-dock/pull/216
- PR number: 216
- Repository: chemitaro/spec-dock
- Base branch: main
- Head branch: iss-00214-pr-observation-review-target-state
- Latest head SHA: f3b95994d94923c3e700e4fc54e52f5e70ee8c92
- Observation command: `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh --repo chemitaro/spec-dock --pr 216 --head-sha f3b95994d94923c3e700e4fc54e52f5e70ee8c92 --timeout-seconds 900 --poll-interval-seconds 30 --quiet-seconds 30 --same-fingerprint-count 2 --progress stderr-summary`
- Observation final JSON / evidence: `normalized_status=failed`, `recommended_next_action=fix_ci`, `head_matches_expected=true`
- Observation status: failed
- Trigger comment id: 4750792642
- Trigger created_at: 2026-06-19T10:41:29Z
- Trigger boundary: fixed trigger comment for head `f3b95994d94923c3e700e4fc54e52f5e70ee8c92`; repair push requires a new latest-head observation.
- Resume metadata: not used; observation completed with CI failure.
- New trigger approved: no
- Observation limitation: Codex review returned a low-confidence fallback issue comment with no blocking finding; provider CI failed.
- Batch status: repair-needed

## Batch Purpose

Use this batch to triage review findings, CI failures, merge blockers, and observation limitations after PR observation and before repair delegation. The batch separates validity from need-to-fix, groups related concerns, creates repair units when needed, and records residual risk for the final merge-prepared decision.

## Concern Catalog

| concern_id | concern | related_inventory_ids | suspected_root_cause | repair_unit | notes |
| --- | --- | --- | --- | --- | --- |
| C001 | Provider CI `provider-tests` failed after PR observation | INV-001 | checked-in dogfooding `.meta.json` path/dependency baseline omitted newly imported `iss-00214` metadata | U001 | Snapshot-only repair; no runtime behavior change intended. |

## Inventory

| ID | source_type | concern | failure_class | evidence | summary | validity | risk_class | need_to_fix | disposition | repair_unit | status | rationale | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| INV-001 | ci | `Provider CI / provider-tests` failed | check_failure:provider-tests | GitHub Actions run `27820892612`, job `82333463397`; `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_initiatives_use_meta_json_dependencies` assertion reported one extra `iss-00214.../.meta.json` path | The PR imported/started `iss-00214`, but the checked-in dogfooding metadata snapshot in `test_init_update.py` was not updated. | valid | blocking | yes | fix-now | U001 | unit-created | Required CI check cannot pass while checked-in dogfooding tree and baseline diverge. | Low; repair should only align test baseline with committed dogfooding metadata. |

## Classification Values

- `validity`: `valid` / `partially-valid` / `false-positive` / `duplicate` / `unknown`
- `failure_class`: `check_failure:<job_or_check_name>` / `review_feedback:<topic>` / `merge_conflict` / `base_branch_conflict` / `permission_or_auth` / `external_or_flaky` / `timeout` / `unknown`
- `risk_class`: `blocking` / `material-follow-up` / `minor` / `false-positive` / `duplicate`
- `need_to_fix`: `yes` / `no` / `follow-up` / `human-decision`
- `disposition`: `fix-now` / `follow-up` / `no-action` / `covered-by` / `needs-human`
- `status`: `untriaged` / `triaged` / `unit-needed` / `unit-created` / `implemented` / `reobserved-pass` / `blocked`

## Per-Concern Analysis

### CXXX

### C001

- Covered inventory IDs: INV-001
- Validity analysis: Valid CI failure. The checked-in dogfooding tree contains `iss-00214-pr-observation-review-target-state/.meta.json`; the cutover snapshot in `tests/unit/infra/test_init_update.py` does not.
- Need-to-fix decision: Fix now because `Provider CI / provider-tests` is a merge-blocking check.
- Root cause: Issue scaffold/import changed the checked-in dogfooding metadata surface after the earlier local targeted validation, but the snapshot constants were not updated.
- Options considered:
  - Update only `_CHECKED_IN_DOGFOODING_META_JSON_PATHS`.
  - Update both `_CHECKED_IN_DOGFOODING_META_JSON_PATHS` and `_CHECKED_IN_DOGFOODING_DEPENDS_ON_BY_META_PATH`.
- Recommended disposition: Update both snapshot constants so path and dependency baselines remain internally consistent.
- Rationale: `iss-00214` currently has no `depends_on` values, so the correct dependency baseline entry is an empty list.
- Residual risk: Full provider test runtime is longer than the focused failure, so re-observation is still required after push.

## Repair Queue

| unit_id | source_batch | covered_ids | disposition | risk_class | repair_unit_disc | status | Implementation Plan | Re-observation Result | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U001 | 20260619t105436z-pr-repair-batch | INV-001 | fix-now | blocking | `20260619t105634z-disc-pr-repair-unit-u001-ci-snapshot.md` | implemented | Add `iss-00214.../.meta.json` to both checked-in dogfooding snapshot constants and run the focused failing test. | Pending repair push and latest-head observation. | Low; snapshot-only change. |

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
