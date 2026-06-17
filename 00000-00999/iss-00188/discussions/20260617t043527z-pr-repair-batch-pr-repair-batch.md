---
種別: pr-repair-batch
ID: "20260617t043527z-pr-repair-batch"
タイトル: "PR Repair Batch"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
親: ["iss-00188"]
関連: []
authority: "proposed"
derived_from:
  - "https://github.com/chemitaro/spec-dock/pull/195"
  - "/private/tmp/pr-195-observation/result.json"
reflected_to: []
---

# 20260617t043527z-pr-repair-batch PR Repair Batch

## PR / Observation Metadata

- PR URL: https://github.com/chemitaro/spec-dock/pull/195
- PR number: 195
- Repository: chemitaro/spec-dock
- Base branch: main
- Head branch: iss-00188-prevent-duplicate-discussion-timestamp-slots
- Latest head SHA: 821eb10993b299e3daaa0dba8496c88e1062c034
- Observation command: `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh --repo chemitaro/spec-dock --pr 195 --head-sha 821eb10993b299e3daaa0dba8496c88e1062c034 --timeout-seconds 1800 --poll-interval-seconds 30 --quiet-seconds 90 --same-fingerprint-count 2 --zero-check-grace-polls 2 --body-mode trigger-window-truncated --out /private/tmp/pr-195-observation`
- Observation final JSON / evidence: `/private/tmp/pr-195-observation/result.json`
- Observation status: failed; `recommended_next_action=fix_ci`; `status_reason=ci_failed`
- Trigger comment id: 4725934579
- Trigger created_at: 2026-06-17T04:24:37Z
- Trigger boundary: explicit `@codex review` posted by wait script for current head SHA
- Resume metadata: not applicable yet; failure is terminal CI failure, not timeout
- New trigger approved: no
- Observation limitation: none reported; failed check run has `limitation=workflow_job_steps_unavailable` but log was available through `gh run view --log-failed`
- Batch status: repair-implemented

## Batch Purpose

Use this batch to triage review findings, CI failures, merge blockers, and observation limitations after PR observation and before repair delegation. The batch separates validity from need-to-fix, groups related concerns, creates repair units when needed, and records residual risk for the final merge-prepared decision.

## Concern Catalog

| concern_id | concern | related_inventory_ids | suspected_root_cause | repair_unit | notes |
| --- | --- | --- | --- | --- | --- |
| C001 | provider-tests layer import failure | I001 | `commands/new.py` imports `domain.discussion_docs`, violating shell layer rule that `commands/*` must not import domain/infra/app directly | U001 | Local focused tests did not include `test_runtime_shell_s11.py`; CI full provider suite caught it |

## Inventory

| ID | source_type | concern | failure_class | evidence | summary | validity | risk_class | need_to_fix | disposition | repair_unit | status | rationale | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I001 | CI check | C001 | check_failure:provider-tests | `gh run view 27665658157 --log-failed`; failed test `tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression` | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py` directly imports `domain.discussion_docs`, which is forbidden for the command shell layer | valid | blocking | yes | fix-now | U001 | implemented | The layer contract is explicit and the failure is reproducible from CI logs. Local repair verification passed; re-observation pending. | pending PR re-observation |

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
- Validity analysis: valid. `test_runtime_shell_s11.py` enforces that `commands/*` remain thin and do not directly import `domain`, `infra`, or `app`.
- Need-to-fix decision: yes.
- Root cause: S02/S04 reused the shared discussion catalog in `commands/new.py` for help text, but placed that import directly in the command layer instead of passing the creatable doc type list through an application/contract boundary or duplicating a presentation-safe constant.
- Options considered:
  - Move help text derivation back to local command-layer constant, accepting drift risk.
  - Expose a command-safe helper/constant outside `domain` and keep shared catalog semantics.
  - Update the structural test to allow this domain import.
- Recommended disposition: fix-now via U001.
- Rationale: The CI failure is blocking and the structural rule should remain intact.
- Residual risk: none expected if focused structural test and relevant new-doc tests pass.

## Repair Queue

| unit_id | source_batch | covered_ids | disposition | risk_class | repair_unit_disc | status | Implementation Plan | Re-observation Result | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U001 | `20260617t043527z-pr-repair-batch` | I001 | fix-now | blocking | `20260617t043551z-disc-pr-repair-unit-u001-provider-tests-layer-import.md` | implemented | Remove forbidden command-layer domain import while preserving `pr-repair-batch` help/catalog behavior; run structural and focused new-doc tests. | pending PR re-observation | pending PR re-observation |

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
