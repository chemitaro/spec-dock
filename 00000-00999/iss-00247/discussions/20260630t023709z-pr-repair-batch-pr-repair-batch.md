---
種別: pr-repair-batch
ID: "20260630t023709z-pr-repair-batch"
タイトル: "PR Repair Batch"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-30"
親: ["iss-00247"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260630t023709z-pr-repair-batch PR Repair Batch

## PR / Observation Metadata

- PR URL: https://github.com/chemitaro/spec-dock/pull/248
- PR number: 248
- Repository: chemitaro/spec-dock
- Base branch: main
- Head branch: iss-00247-move-assurance-compose-scaffold-sources-to-profile-markdown-templates
- Latest head SHA: 1015d98fed80c18d1fca6b08b6d955795977c881
- Observation command: `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh --repo chemitaro/spec-dock --pr 248 --head-sha 1015d98fed80c18d1fca6b08b6d955795977c881`
- Observation final JSON / evidence: stdout final JSON observed at 2026-06-30T02:36:57Z
- Observation status: human_gate; CI passed; Codex review unresolved 3
- Trigger comment id: 4839290584
- Trigger created_at: 2026-06-30T02:19:21Z
- Trigger boundary: current trigger window for head `1015d98fed80c18d1fca6b08b6d955795977c881`
- Resume metadata: N/A
- New trigger approved: no
- Observation limitation: none reported by script; external/non-Actions checks are not claimed as observed
- Batch status: triaged; repair unit U001 implemented; awaiting re-observation

## Batch Purpose

Use this batch to triage review findings, observed GitHub Actions CI failures, merge blockers, and observation limitations after PR observation and before repair delegation. The batch separates validity from need-to-fix, groups related concerns, creates repair units when needed, and records residual risk for the final merge-prepared decision. PR observation intentionally does not observe external/non-Actions checks; record GitHub UI or external CI confirmation as residual risk or a human gate when branch protection depends on them.

## Concern Catalog

| concern_id | concern | related_inventory_ids | suspected_root_cause | repair_unit | notes |
| --- | --- | --- | --- | --- | --- |

| C001 | Template placeholder and milestone gate readiness alignment | I001, I002, I003, I004, I005 | New grade templates introduced `XXX` sentinels, `M...` milestone IDs, `report.md#...` anchors, and milestone commit gates, but readiness detection and workflow completion text still allowed older step-only assumptions | U001 | Single repair unit because all items share the same template-readiness contract boundary |

## Inventory

| ID | source_type | concern | failure_class | evidence | summary | validity | risk_class | need_to_fix | disposition | repair_unit | status | rationale | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

| I001 | review_feedback | C001 | review_feedback:template-readiness | thread PRRT_kwDOQ99OK86NJVIf; comment 3495817493 | Remaining generated placeholder cells/list items can leave composed plan/design executable | valid | blocking | yes | fix-now | U001 | implemented | Readiness now rejects generated placeholder table cells and list items | None after re-observation if latest head review passes |
| I002 | review_feedback | C001 | review_feedback:requirement-sentinel-readiness | thread PRRT_kwDOQ99OK86NJVIh; comment 3495817497 | `SC-XXX` / `BH-XXX` / `AC-XXX` sentinels can remain in approved requirement and bypass scaffold detection | valid | blocking | yes | fix-now | U001 | implemented | Requirement sentinels now block readiness while present | None after re-observation if latest head review passes |
| I003 | review_feedback | C001 | review_feedback:milestone-commit-gates | thread PRRT_kwDOQ99OK86NJVIj; comment 3495817499 | Workflow completion text still implied per-step commit gates despite milestone `commit候補` model | valid | blocking | yes | fix-now | U001 | implemented | Workflow docs now use step / milestone result approval and milestone commit候補 gates | None after re-observation if latest head review passes |
| I004 | review_feedback | C001 | review_feedback:report-anchor-readiness | thread PRRT_kwDOQ99OK86NJyOx; comment 3495980801 | `report.md#...` evidence anchors can remain unresolved while plan is classified executable | valid | blocking | yes | fix-now | U001 | implemented | Readiness now rejects generated report anchor placeholders | None after re-observation if latest head review passes |
| I005 | review_feedback | C001 | review_feedback:milestone-placeholder-readiness | thread PRRT_kwDOQ99OK86NKEkl; comment 3496085594 | `M...` milestone placeholder IDs can remain unresolved while plan is classified executable | valid | blocking | yes | fix-now | U001 | implemented | Readiness now rejects generated unhyphenated placeholder IDs such as `M...` | None after re-observation if latest head review passes |

## Classification Values

- `validity`: `valid` / `partially-valid` / `false-positive` / `duplicate` / `unknown`
- `failure_class`: `check_failure:<actions_job_or_workflow_name>` / `review_feedback:<topic>` / `merge_conflict` / `base_branch_conflict` / `permission_or_auth` / `external_or_flaky` / `timeout` / `unknown`
- `risk_class`: `blocking` / `material-follow-up` / `minor` / `false-positive` / `duplicate`
- `need_to_fix`: `yes` / `no` / `follow-up` / `human-decision`
- `disposition`: `fix-now` / `follow-up` / `no-action` / `covered-by` / `needs-human`
- `status`: `untriaged` / `triaged` / `unit-needed` / `unit-created` / `implemented` / `reobserved-pass` / `blocked`

## Per-Concern Analysis

### C001

- Covered inventory IDs: I001, I002, I003, I004, I005
- Validity analysis: valid. All findings point to contracts introduced or modified by this PR.
- Need-to-fix decision: yes.
- Root cause: Template sentinel conventions, milestone placeholder IDs, report evidence anchors, and milestone-level commit candidates were added without fully updating runtime readiness detection and workflow completion wording.
- Options considered:
  - Only document the limitation: rejected because readiness false positives would remain.
  - Remove `XXX` sentinel guidance: rejected because the template guidance is intentional.
  - Detect generated placeholders and align workflow text: selected because it keeps template guidance while preventing readiness false positives.
- Recommended disposition: fix-now through U001.
- Rationale: The affected surfaces are protected issue readiness and completion gates.
- Residual risk: Requires re-observation on a new head SHA after repair commit.

## Repair Queue

| unit_id | source_batch | covered_ids | disposition | risk_class | repair_unit_disc | status | Implementation Plan | Re-observation Result | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

| U001 | 20260630t023709z-pr-repair-batch | I001, I002, I003, I004, I005 | fix-now | blocking | 20260630t023744z-disc-pr-repair-unit-u001-template-readiness-gates.md | implemented | Added readiness tests, updated placeholder/sentinel/report-anchor/milestone-placeholder detection, aligned workflow completion docs; included in amended repair commit | pending re-observation after push | pending latest-head re-observation |

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
