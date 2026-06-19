---
種別: pr-repair-batch
ID: "20260619t184139z-pr-repair-batch"
タイトル: "PR Repair Batch"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["iss-00218"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260619t184139z-pr-repair-batch PR Repair Batch

## PR / Observation Metadata

- PR URL: https://github.com/chemitaro/spec-dock/pull/220
- PR number: 220
- Repository: chemitaro/spec-dock
- Base branch: main
- Head branch: iss-00218-codex-review-fallback-signal-semantics
- Latest head SHA: db9495fd9c539e395caf994d5ca276c8451f04b5
- Observation command: `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh --repo chemitaro/spec-dock --pr 220 --head-sha fc9a8ad07ec327bf409cd15e5a9df403aca19f69 --timeout-seconds 900 --poll-interval-seconds 30 --quiet-seconds 60 --same-fingerprint-count 2 --out /private/tmp/spec-dock-pr220-observation`
- Observation final JSON / evidence: `/private/tmp/spec-dock-pr220-observation/result.json`
- Observation status: failed / `recommended_next_action=fix_ci`
- Trigger comment id: 4753926299
- Trigger created_at: 2026-06-19T18:33:31Z
- Trigger boundary: post-once fixed `@codex review` for PR #220 at latest head
- Resume metadata: not used; observation reached terminal CI failure
- New trigger approved: no
- Observation limitation: Codex review returned usage-limit issue comment; review completion is not clean and remains a human gate after CI is repaired unless a later observation produces a trusted completion signal.
- Batch status: U001 reobserved-pass at latest head `db9495fd9c539e395caf994d5ca276c8451f04b5`; stopped at I006 human gate for Codex review usage limit

## Batch Purpose

Use this batch to triage review findings, CI failures, merge blockers, and observation limitations after PR observation and before repair delegation. The batch separates validity from need-to-fix, groups related concerns, creates repair units when needed, and records residual risk for the final merge-prepared decision.

## Concern Catalog

| concern_id | concern | related_inventory_ids | suspected_root_cause | repair_unit | notes |
| --- | --- | --- | --- | --- | --- |
| C001 | Provider CI snapshot/parity failures | I001, I002, I003, I004, I005 | Branch changed dogfooding issue docs and PR observation assets without updating checked-in snapshot/parity expectations and dogfooding mirror | U001 | All five CI failures are deterministic local snapshot/parity regressions from the same branch delta |

## Inventory

| ID | source_type | concern | failure_class | evidence | summary | validity | risk_class | need_to_fix | disposition | repair_unit | status | rationale | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I001 | CI failure | C001 | check_failure:provider-tests | run 27842323053; `test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json` | New `iss-00218` `.meta.json` is checked in but snapshot allow-list lacks the path | valid | blocking | yes | fix-now | U001 | reobserved-pass | dogfooding issue scaffold is intentionally added by this branch and snapshot was updated locally | latest-head CI pass confirmed |
| I002 | CI failure | C001 | check_failure:provider-tests | run 27842323053; `test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets` | checked-in `.agents/skills/github-pr-observation/SKILL.md` no longer matches provider install_root asset | valid | blocking | yes | fix-now | U001 | reobserved-pass | shipped skill docs changed in S90 and dogfooding mirror parity was synced from provider install_root | latest-head CI pass confirmed |
| I003 | CI failure | C001 | check_failure:provider-tests | run 27842323053; `test_issue_75_pr_monitor_assets_retired_and_observation_scaffold_present` | observation scaffold parity also detects the stale dogfooding skill file | duplicate | duplicate | yes | covered-by | U001 | reobserved-pass | same root cause as I002 and covered by mirror sync | latest-head CI pass confirmed |
| I004 | CI failure | C001 | check_failure:provider-tests | run 27842323053; `test_issue_182_s03_wait_progress_uses_decision_current_counts_not_audit_threads` | expected `wait_or_resume` was not updated to `manual_review_required_non_retryable` after fallback action change | valid | blocking | yes | fix-now | U001 | reobserved-pass | S99 changed fallback action semantics and the remaining expectation was updated locally | latest-head CI pass confirmed |
| I005 | CI failure | C001 | check_failure:provider-tests | run 27842323053; `test_issue_197_pr_review_snapshot_provider_wrapper_invokes_python_entrypoint` | provider wrapper fixture snapshot is stale after `pr_review_snapshot.py` output-shape edits | valid | blocking | yes | fix-now | U001 | reobserved-pass | branch changed provider Python entrypoint and dogfooding mirror was synced from provider install_root | latest-head CI pass confirmed |
| I006 | Review observation | Codex usage limit comment | permission_or_auth | `/private/tmp/spec-dock-pr220-observation-latest-readonly/result.json`; comment 4753968203 | Codex review could not run because code review usage limit was reached | valid | material-follow-up | human-decision | needs-human | N/A | blocked | Not fixable in repo; latest-head CI and merge state are clean, but review-clean cannot be claimed unless review is retried after quota is available or explicitly waived | review-clean cannot be claimed from this observation |

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

- Covered inventory IDs: I001, I002, I003, I004, I005
- Validity analysis: valid deterministic CI failures; I003 duplicates I002.
- Need-to-fix decision: yes.
- Root cause: branch changed dogfooding issue inventory and PR observation shipped assets/semantics, while CI snapshot/parity tests expect checked-in dogfooding and provider fixture surfaces to move together.
- Options considered: update snapshots/parity fixtures now; waive Provider CI; remove dogfooding scaffold from branch.
- Recommended disposition: fix-now via U001.
- Rationale: failures are local deterministic tests and align with intended shipped/dogfooding changes.
- Residual risk: low after full targeted Provider CI failures and broad issue selector pass.

## Repair Queue

| unit_id | source_batch | covered_ids | disposition | risk_class | repair_unit_disc | status | Implementation Plan | Re-observation Result | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U001 | 20260619t184139z-pr-repair-batch | I001, I002, I003, I004, I005 | fix-now | blocking | `20260619t184214z-disc-pr-repair-unit-u001-ci-snapshot-parity.md` | reobserved-pass | Updated dogfooding meta snapshot, dogfooding skill mirror, fallback action expectations, and provider wrapper fixture snapshot; targeted CI failure tests and broad S99 selector passed locally | latest head `db9495fd9c539e395caf994d5ca276c8451f04b5`: `validate` pass, `provider-tests` pass, merge state `CLEAN`; read-only snapshot result `/private/tmp/spec-dock-pr220-observation-latest-readonly/result.json` | low for CI repair; Codex usage-limit remains separate I006 human gate |

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
