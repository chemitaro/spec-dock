---
種別: pr-repair-batch
ID: "20260619t113109z-pr-repair-batch"
タイトル: "PR Repair Batch"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["iss-00211"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260619t113109z-pr-repair-batch PR Repair Batch

## PR / Observation Metadata

- PR URL: https://github.com/chemitaro/spec-dock/pull/217
- PR number: 217
- Repository: chemitaro/spec-dock
- Base branch: main
- Head branch: iss-00211-epic-execution-coordinator-skill
- Latest head SHA: 881ef59eb1e1f95b9bfdf5a61eb9f7d25dabbb13
- Observation command: `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh --repo chemitaro/spec-dock --pr 217 --head-sha 881ef59eb1e1f95b9bfdf5a61eb9f7d25dabbb13`
- Observation final JSON / evidence: stdout final JSON, observed_at `2026-06-19T11:31:02.320328Z`, fingerprint `401b4e40e4fc3715877807a154f4f2882592852410649d5dd99be4682b6fefe7`
- Observation status: failed
- Trigger comment id: 4751023793
- Trigger created_at: 2026-06-19T11:17:39Z
- Trigger boundary: current trigger boundary for head `881ef59eb1e1f95b9bfdf5a61eb9f7d25dabbb13`
- Resume metadata: N/A; first observation completed with CI failure
- New trigger approved: no
- Observation limitation: none; review-thread state available with 0 unresolved threads
- Batch status: implemented; re-observation pending

## Batch Purpose

Use this batch to triage review findings, CI failures, merge blockers, and observation limitations after PR observation and before repair delegation. The batch separates validity from need-to-fix, groups related concerns, creates repair units when needed, and records residual risk for the final merge-prepared decision.

## Concern Catalog

| concern_id | concern | related_inventory_ids | suspected_root_cause | repair_unit | notes |
| --- | --- | --- | --- | --- | --- |
| C001 | Provider CI snapshot drift on PR merge ref | I001 | base `main` added `iss-00214-pr-observation-review-target-state` after this issue branch was cut; PR merge ref includes the new `.meta.json`, but this branch's checked-in dogfooding meta path snapshot does not. | U001 | Repair should merge/reconcile `origin/main` and update the snapshot, then re-run focused provider test. |

## Inventory

| ID | source_type | concern | failure_class | evidence | summary | validity | risk_class | need_to_fix | disposition | repair_unit | status | rationale | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I001 | CI failure | C001 | check_failure:provider-tests | Provider CI run 27822529397, job 82338831912, failed step `Run provider pytest suite`; failing test `TestInitUpdate.test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json`; left contains one more path `spec-dock/.../issues/iss-00214-pr-observation-review-target-state/.meta.json`. | Checked-in dogfooding `.meta.json` snapshot diverges after base branch drift. | valid | blocking | yes | fix-now | U001 | implemented | Required check failure blocks merge-prepared state; local focused repair verification passed. | Low after snapshot repair and re-observation; without repair the PR remains UNSTABLE. |

## Classification Values

- `validity`: `valid` / `partially-valid` / `false-positive` / `duplicate` / `unknown`
- `failure_class`: `check_failure:<job_or_check_name>` / `review_feedback:<topic>` / `merge_conflict` / `base_branch_conflict` / `permission_or_auth` / `external_or_flaky` / `timeout` / `unknown`
- `risk_class`: `blocking` / `material-follow-up` / `minor` / `false-positive` / `duplicate`
- `need_to_fix`: `yes` / `no` / `follow-up` / `human-decision`
- `disposition`: `fix-now` / `follow-up` / `no-action` / `covered-by` / `needs-human`
- `status`: `untriaged` / `triaged` / `unit-needed` / `unit-created` / `implemented` / `reobserved-pass` / `blocked`

## Per-Concern Analysis

### C001

- Covered inventory IDs: I001
- Validity analysis: valid. GitHub Actions ran on PR merge ref `5e961b36...`, which includes base `main` commit `ce53d53a` and branch head `881ef59e`; local branch is `7 ahead / 2 behind` relative to `origin/main`.
- Need-to-fix decision: yes. Required `provider-tests` failed and merge-prepared predicate requires no required check failures.
- Root cause: base branch drift introduced Issue 214 scaffold metadata after the Issue 211 branch was cut. The PR merge ref contains the new `.meta.json`, but the snapshot tuple in `tests/unit/infra/test_init_update.py` on this branch does not.
- Options considered: rerun CI only; merge/rebase main and update snapshot; ignore as external base failure.
- Recommended disposition: fix-now via U001.
- Rationale: The failure is deterministic from merge-ref content and can be repaired with a bounded snapshot/base reconciliation.
- Residual risk: If main advances again with new dogfooding scaffold metadata before merge, the same snapshot test may need another reconciliation.

## Repair Queue

| unit_id | source_batch | covered_ids | disposition | risk_class | repair_unit_disc | status | Implementation Plan | Re-observation Result | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U001 | 20260619t113109z-pr-repair-batch | I001 | fix-now | blocking | `20260619t113206z-disc-pr-repair-unit-u001-provider-tests-snapshot.md` | implemented | Merged `origin/main`, updated checked-in dogfooding meta snapshot for Issue 214, ran focused failing test and `git diff --check`. | pending | Low; repair is snapshot/base reconciliation only. |

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
