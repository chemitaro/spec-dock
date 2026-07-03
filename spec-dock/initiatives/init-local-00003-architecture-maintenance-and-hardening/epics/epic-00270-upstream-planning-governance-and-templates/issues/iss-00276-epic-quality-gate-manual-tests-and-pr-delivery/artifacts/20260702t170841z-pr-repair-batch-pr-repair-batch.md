---
種別: pr-repair-batch
ID: "20260702t170841z-pr-repair-batch"
タイトル: "PR Repair Batch"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["iss-00276"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260702t170841z-pr-repair-batch PR Repair Batch

## PR / Observation Metadata

- PR URL:
- PR URL: `https://github.com/chemitaro/spec-dock/pull/277`
- PR number: `277`
- Repository: `chemitaro/spec-dock`
- Base branch: `main`
- Head branch: `iss-00276-epic-quality-gate-manual-tests-and-pr-delivery`
- Latest head SHA: `6f9369b7568945454a3b90b9abb8fc1448196cf8`
- Observation command: `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh --repo chemitaro/spec-dock --pr 277 --head-sha 6f9369b7568945454a3b90b9abb8fc1448196cf8 ...`
- Observation final JSON / evidence: `/private/tmp/spec-dock-pr277-observation-4/result.json`
- Observation status: `human_gate`
- Trigger comment id: `4868190859`
- Trigger created_at: `2026-07-02T16:48:17Z`
- Trigger boundary: explicit trigger for head `6f9369b7568945454a3b90b9abb8fc1448196cf8`
- Resume metadata: not needed; terminal observation returned
- New trigger approved: no
- Observation limitation: none; blocker is reviewer P1
- Batch status: blocking repair required

## Batch Purpose

Use this repo-persistent batch to triage and repair blocking PR observation
results. A blocking result is a `P0`/`P1` review finding, required GitHub Actions
CI failure, visible merge conflict, blocking observation limitation, or other
merge-prepared blocker.

This batch separates raw intake from severity decisions, groups related findings
by `root_cause_family`, creates repair units only for blocking families, records
non-blocking findings only when a blocking repair commit is already being made,
and preserves residual risk for the final merge-prepared decision.

`root_cause_family` is documentation and LLM judgment vocabulary for this
discussion artifact. It is not a required runtime JSON field, parser contract,
blocker fingerprint, or stalled-observation contract.

## Persistence Policy

This file is for blocking repair work.

Use this repo-persistent batch when:

- `P0`/`P1` review findings exist.
- Required GitHub Actions CI failures exist.
- Merge blockers exist.
- Blocking observation limitations require repair or human-gate tracking.
- Branch mutation is already required for blocking repair and non-blocking
  findings can be recorded in the same commit without causing an extra CI run.

Do not update this batch solely to record terminal `P2`/`P3` findings after the
latest pushed head has no blockers. Record terminal `P2`/`P3` findings in the
final merge-prepared report instead, unless the user explicitly requests
separate follow-up tracking outside the current PR branch.

## Observation Batch Summary

| field | value |
| --- | --- |
| latest_head_sha | `6f9369b7568945454a3b90b9abb8fc1448196cf8` |
| observation_status | `human_gate` / `automation_stalled` |
| required_ci_status | pass (`CI`, `Provider CI`) |
| review_status | unresolved |
| p0_count | 0 |
| p1_count | 1 |
| p2_count | 2 current selected findings |
| p3_count | 0 current selected findings |
| blocking_repair_units | `RU-277-004` |

## Raw Intake Inventory

| item_id | source | reported_priority | root_cause_family | summary | decided_priority | merge_blocking | disposition | status |
|---|---|---|---|---|---|---|---|---|
| `3514851104` | PR review comment | P1 | `epic-execution.report-gate` | `spec-dock-epic-execution` Overview / bootstrap wording still treats Epic `report.md` as reviewer-gated. | P1 | yes | fix-now | unit-created |
| `3514851110` | PR review comment | P2 | `initiative-template.epic-completion-contract` | Initiative plan template can understate canonical Epic design / plan completion. | P2 | no | follow-up | triaged |
| `3514851117` | PR review comment | P2 | `epic-handoff.draft-plan-prereq` | `draft-plan` handoff command needs assurance prerequisite documentation. | P2 | no | follow-up | triaged |

## Repair Units

| unit_id | root_cause_family | covered_ids | decided_priority | status | artifact |
|---|---|---|---|---|---|
| `RU-277-004` | `epic-execution.report-gate` | `3514851104`, `PRRT_kwDOQ99OK86N-QDD` | P1 | implemented | `20260702t170858z-disc-pr-repair-unit-epic-execution-report-gate.md` |

## Non-Blocking Follow-up Register

| root_cause_family | priority | disposition | rationale |
|---|---|---|---|
| `initiative-template.epic-completion-contract` | P2 | follow-up | Non-blocking per review. Not directly covered by the P1 report-gate repair, so no branch expansion under `github-pr-merge-preparer` policy. |
| `epic-handoff.draft-plan-prereq` | P2 | follow-up | Non-blocking per review. Not directly covered by the P1 report-gate repair, so no branch expansion under `github-pr-merge-preparer` policy. |
| p3_count | 0 |
| required_ci_failure_count | 0 |
| merge_blocker_count | 0 |
| blocking_family_count | 1 |
| non_blocking_family_count | 2 |
| terminal_non_blocking_only | no |
| branch_mutation_required | yes |
| ci_rerun_expected | yes |
| review_clean | no |
| merge_prepared_candidate | no, until P1 is repaired and re-observed |

## Concern Family Catalog

| family_id | root_cause_family | family_title | protected_domain | invariant_or_contract | related_items | max_reported_priority | decided_priority | merge_blocking | disposition | repair_unit | family_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `F277-004` | `epic-execution.report-gate` | Epic report ledger must not be reviewer-gated | no | Epic execution reads `report.md` as evidence ledger, not planning phase artifact | `3514851104` | P1 | P1 | yes | fix-now | `RU-277-004` | implemented |
| `F277-005` | `initiative-template.epic-completion-contract` | Initiative template should distinguish Epic readiness seed from completion | yes | Epic completion requires canonical `requirement.md` / `design.md` / `plan.md` | `3514851110` | P2 | P2 | no | follow-up | N/A | triaged |
| `F277-006` | `epic-handoff.draft-plan-prereq` | Draft-plan handoff should document assurance prerequisite | yes | `new artifact draft-plan` requires valid issue assurance contract | `3514851117` | P2 | P2 | no | follow-up | N/A | triaged |

## Classification Values

- `reported_priority`: `P0` / `P1` / `P2` / `P3` / `CI` / `unknown`
- `decided_priority`: `P0` / `P1` / `P2` / `P3` / `required-ci` / `platform` / `unknown`
- `merge_blocking`: `yes` / `no` / `platform-only` / `unknown`
- `validity`: `valid` / `partially-valid` / `false-positive` / `duplicate` / `unknown`
- `failure_class`: `check_failure:<actions_job_or_workflow_name>` / `review_feedback:<stable_topic>` / `merge_conflict` / `base_branch_conflict` / `permission_or_auth` / `external_or_flaky` / `platform_conversation_resolution` / `timeout` / `unknown`
- `need_to_fix`: `yes` / `no` / `follow-up` / `human-decision`
- `disposition`: `fix-now` / `follow-up` / `no-action` / `covered-by` / `needs-human`
- `status`: `untriaged` / `triaged` / `unit-needed` / `unit-created` / `implemented` / `reobserved-pass` / `blocked`

## Per-Family Analysis

### F277-004 `epic-execution.report-gate`

- Related inventory IDs: `3514851104`
- Reported priorities: P1
- Decided priority: P1
- Merge-blocking: yes
- Protected domain: no
- Contract / invariant: Epic `requirement.md` / `design.md` / `plan.md` are reviewer-gated; Epic `report.md` is evidence ledger.
- Root cause: `spec-dock-epic-execution` skill Overview / bootstrap bullet still listed `report.md` as reviewer-gated.
- Why this is one family: Both affected lines are in the same skill and describe the same handoff gate.
- Validity analysis: valid.
- Need-to-fix decision: fix now.
- Options considered: Overview-only fix was rejected because bootstrap bullet would still be misleading.
- Recommended disposition: provider / dogfooding skill wording repair.
- Repair scope: `.agents/skills/spec-dock-epic-execution/SKILL.md` and `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md`.
- Out of scope: P2 template / draft prerequisite follow-ups.
- Quality gates: mirror parity, `validate`, `assurance verify`, `git diff --check`, PR re-observation.
- Residual risk: none after re-observation if P1 disappears.
- Follow-up handling: P2 findings remain non-blocking.

## Blocking Repair Queue

Create repair units only for `P0`/`P1` families, required CI failures, or
blocking merge issues. Do not create repair units for `P2`/`P3` findings unless
they are directly and unavoidably covered by the same `P0`/`P1` root-cause fix.

| unit_id | source_batch | family_id | covered_items | decided_priority | merge_blocking | disposition | repair_unit_disc | status | implementation_plan | quality_gate | commit_evidence | re_observation_result | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `RU-277-004` | `20260702t170841z-pr-repair-batch` | `F277-004` | `3514851104` | P1 | yes | fix-now | `20260702t170858z-disc-pr-repair-unit-epic-execution-report-gate.md` | implemented | provider / dogfooding skill wording repair | mirror parity, `validate`, `assurance verify`, `git diff --check`, PR re-observation | pending commit | pending re-observation | P2 follow-ups remain non-blocking |

## Non-Blocking Follow-up Register

Use this section only when a blocking repair commit is already being made and
`P2`/`P3` findings can be recorded without causing an additional record-only
push.

If the latest observation has only `P2`/`P3` findings and no blockers, do not
update this file. Put those findings in the terminal merge-prepared report
instead.

| followup_id | family_id | related_items | priority | rationale_for_no_action | residual_risk | suggested_followup_target |
| --- | --- | --- | --- | --- | --- | --- |
| `NB277-005` | `F277-005` | `3514851110` | P2 | Non-blocking per review and outside P1 root cause. | Initiative handoff wording can be improved later. | future follow-up issue or later planning hardening |
| `NB277-006` | `F277-006` | `3514851117` | P2 | Non-blocking per review and outside P1 root cause. | Draft handoff prerequisite can be clarified later. | future follow-up issue or later planning hardening |

## Quality Gate Plan

Define family-level gates, not comment-level checks.

| gate_id | family_id | command_or_check | expected_result | covers_items | required_before_push |
| --- | --- | --- | --- | --- | --- |
| `G277-004-a` | `F277-004` | `diff -u src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md .agents/skills/spec-dock-epic-execution/SKILL.md` | no diff | `3514851104` | yes |
| `G277-004-b` | `F277-004` | `./spec-dock/scripts/spec-dock validate` | pass | `3514851104` | yes |
| `G277-004-c` | `F277-004` | `./spec-dock/scripts/spec-dock assurance verify` | pass | `3514851104` | yes |
| `G277-004-d` | `F277-004` | `git diff --check` | pass | `3514851104` | yes |

## Re-observation Plan

- Latest head before repair: `6f9369b7568945454a3b90b9abb8fc1448196cf8`
- Expected head after repair: pending commit
- Re-observation command: `wait_pr_observation.sh --repo chemitaro/spec-dock --pr 277 --head-sha <new-head>`
- Trigger mode: post-once
- Resume trigger comment id: N/A
- Resume trigger created_at: N/A
- New trigger approved: yes / no
- Re-observation required because: P1 repair changes PR head.
- Re-observation skipped because: N/A

## Loop Control

| iteration | head_sha | observation_status | family_id | action_taken | fix_commit | reappeared_after_fix | next_action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `6f9369b7568945454a3b90b9abb8fc1448196cf8` | `human_gate` / P1 blocker | `F277-004` | wording repair implemented | pending commit | no, first repair for this family in this batch | commit, push, re-observe |

Stop at a human gate when the same `root_cause_family` reappears after a repair
commit, unless a human explicitly approves a new strategy.

## Terminal Non-Blocking Report Boundary

When final re-observation contains only `P2`/`P3` findings:

- Do not update this batch solely to record them.
- Do not push a record-only commit.
- Do not trigger another review.
- Report those findings in the final response grouped by `root_cause_family`.
- State `branch mutation: no`.
- State `ci rerun avoided: yes`.
- State `review-clean: no`.
- State `merge-prepared: yes` if all blocking predicates are satisfied.

## Stop Conditions

Stop at a human gate when any condition applies:

- Any blocking inventory item remains `untriaged`.
- Any unresolved blocking `needs-human` item remains.
- A `P0`/`P1` `fix-now` repair unit is incomplete or repeatedly fails.
- The same `root_cause_family` reappears after a repair commit.
- Observation output is not for the latest head SHA.
- Timeout or observation limitation lacks resume metadata.
- Resume would cross the recorded trigger boundary.
- A new trigger would be required but has not been approved.
- Scope expansion, requirement expansion, breaking change, migration, secret,
  deployment setting, permission/auth, external/flaky, or ambiguous review
  intent is involved.
- Loop limits for the same root-cause family or total repair attempts are
  reached.
- GitHub branch protection requires conversation resolution for unresolved
  `P2`/`P3` threads; this is a platform human gate, not a code repair target.

## Merge-Prepared Gate

Report `merge-prepared: yes` only when all conditions are true:

- PR is open.
- Latest observation is complete and matches the latest head SHA.
- No observed required GitHub Actions CI failure remains.
- External/non-Actions check state has either been confirmed outside PR
  observation or is recorded as a human gate/residual risk.
- No unresolved `P0`/`P1` review feedback remains.
- Remaining `P2`/`P3` findings, if any, are grouped and reported as
  non-blocking terminal findings or recorded here because a blocking repair
  commit was already required.
- No visible merge conflict or equivalent semantic merge blocker remains.
- No blocking `untriaged` inventory item remains.
- No unresolved blocking `needs-human` item remains.
- No blocking item has an incomplete `fix-now` repair unit.
- Every repo-persistent `follow-up`, `no-action`, `covered-by`, `duplicate`, or
  `false-positive` item has rationale and residual risk where relevant.
- Observation limitation handling, resume metadata, trigger boundary, and new
  trigger approval status are recorded.
- Review-thread unresolved state is known, or unresolved-thread limitations are
  disclosed. If platform conversation resolution is required, stop at a human
  gate instead of claiming GitHub mergeability.
- `review-clean` is reported separately from `merge-prepared`.
- `github-mergeable` is not claimed unless platform requirements were confirmed.
