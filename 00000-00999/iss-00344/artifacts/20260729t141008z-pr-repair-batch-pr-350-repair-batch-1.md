---
種別: pr-repair-batch
ID: "20260729t141008z-pr-repair-batch"
タイトル: "PR 350 Repair Batch 1"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-29"
親: ["iss-00344"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260729t141008z-pr-repair-batch PR 350 Repair Batch 1

## PR / Observation Metadata

- PR URL: https://github.com/chemitaro/spec-dock/pull/350
- PR number: 350
- Repository: `chemitaro/spec-dock`
- Base branch: `main`
- Head branch: `iss-00344-workbench-shell-scaffolding`
- Latest head SHA: `7bac5ee606e235df52c3a23be433fba3cdbf491a`
- Observation command: fixed `wait_pr_observation.sh` for PR 350 and exact head
- Observation final JSON / evidence: trigger comment `5118793199`; review `4809194073`; review comment `3675040563`; thread `PRRT_kwDOQ99OK86UyP0v`
- Observation status: `human_gate` / CI `passed` / review `unresolved`
- Trigger comment id: `5118793199`
- Trigger created_at: `2026-07-29T14:01:35Z`
- Trigger boundary: exact head `7bac5ee606e235df52c3a23be433fba3cdbf491a`
- Resume metadata: not applicable; branch-changing repair requires a new exact-head trigger
- New trigger approved: no
- Observation limitation: none; one current-boundary P1 finding is present
- Batch status: implementation complete / candidate commit pending

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
| latest_head_sha | `7bac5ee606e235df52c3a23be433fba3cdbf491a` |
| observation_status | `human_gate` |
| required_ci_status | `passed` |
| review_status | `unresolved` |
| p0_count | 0 |
| p1_count | 1 |
| p2_count | 0 |
| p3_count | 0 |
| required_ci_failure_count | 0 |
| merge_blocker_count | 1 |
| blocking_family_count | 1 |
| non_blocking_family_count | 0 |
| terminal_non_blocking_only | no |
| branch_mutation_required | yes |
| ci_rerun_expected | yes |
| review_clean | no |
| merge_prepared_candidate | no |

## Raw Intake Inventory

Add one row per observed review finding, required CI failure, merge blocker, or
observation limitation from the same observation batch. Keep raw reviewer
priority separate from the final severity decision.

| item_id | source_type | source_id | reported_priority | path | line | raw_summary | evidence_type | current_head_sha | family_id | intake_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R001 | review | `3675040563` | P1 | `src/spec_dock/cli.py` | 811 | fresh root Workbench README is not registered in scaffold uninstall sources, so unchanged managed output survives `uninstall --apply --remove-specs` | code-path / public uninstall contract / exact-head observation | `7bac5ee606e235df52c3a23be433fba3cdbf491a` | F001 | triaged |

Do not keep example rows as active inventory.

## Concern Family Catalog

Group inventory items by shared root cause. Do not repair comments one-by-one.

| family_id | root_cause_family | family_title | protected_domain | invariant_or_contract | related_items | max_reported_priority | decided_priority | merge_blocking | disposition | repair_unit | family_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F001 | uninstall-managed-inventory | Fresh root README uninstall ownership | yes | Installer-generated exact bytes must be recognized as managed and removed; mismatched user content must remain preserved | R001 | P1 | P1 | yes | fix-now | U001 | unit-created |

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

Create one subsection per real family.

### F001 uninstall-managed-inventory

- Related inventory IDs: R001
- Reported priorities: P1
- Decided priority: P1
- Merge-blocking: yes
- Protected domain: uninstall / generated-file ownership
- Contract / invariant: fresh initが生成したunchanged managed fileは`--remove-specs`で除去し、bytesが異なる利用者変更は既存exact-match分類で保存する。
- Root cause: `_build_scaffold_uninstall_sources()`がmanaged directories、`.gitignore`、`spec-dock.version`だけを列挙し、fresh-only root `.workbench/README.md` assetを列挙していない。
- Why this is one family: generationとuninstall inventoryの対称性欠落という単一原因である。
- Validity analysis: valid。provider sourceと既存uninstall exact-match pathからdeterministicに確認した。
- Need-to-fix decision: yes。このPRが新規生成した公開uninstall契約の欠陥である。
- Options considered: exact assetを既存inventoryへ追加、special-case削除、Worktree全体をmanaged directory化。
- Recommended disposition: exact assetを既存inventoryへ追加し、既存exact-match/mismatch-preservation helperを再利用する。
- Repair scope: `src/spec_dock/cli.py`とuninstall regression tests、必要なIssue-local evidenceだけ。
- Out of scope: Workbench payload削除、existing scope backfill、generic import、Issue 345/346実装。
- Quality gates: focused uninstall tests、fresh init/remove-specs、mismatch preservation、Issue 344 aggregate、lint/default lane。
- Residual risk: cleanup順序とretry marker除去はfocused regressionで確認する。
- Follow-up handling: none if re-observation passes.

## Root-Cause Family and Coupling Analysis

| family_id | root_cause_family | related_items | recurrence_class | coupling | evidence_ref | analysis_result |
| --- | --- | --- | --- | --- | --- | --- |
| F001 | uninstall-managed-inventory | R001 | first-observed | root Workbench asset generationとscaffold uninstall inventoryが直接coupled | review comment `3675040563`; `src/spec_dock/cli.py` | single bounded repair family |

When a `root_cause_family` recurs, re-analyze the current evidence, root-cause
hypothesis, coupling, and prior result. Recurrence alone is not a stop reason.

## Integrated Repair Strategy

- strategy_id: S350-001
- covered_family_ids: F001
- prior_strategy_id: none
- strategy_delta: initial exact-path ownership repair。特殊削除ではなく既存exact-match inventoryへ生成assetを対称登録する。
- bounded_scope: installer uninstall source inventory、focused tests、Issue-local repair evidence
- validation_plan: Red reproduction、exact-match removal、modified READMEとarbitrary payload preservation、retry marker persistence/idempotent rerun、Issue 344 aggregate、lint/default pytest
- rollback_plan: bounded commitをrevertし、P1 human gateへ戻す
- re_observation_plan: push後の新exact HEADで固定`wait_pr_observation.sh`をpost-once実行
- residual_risk: current shipped bytesとのexact-match ownershipはolder-version READMEを保守的に保存し得る

The strategy must be bounded, in scope, supported by current evidence, and
materially different from an ineffective prior strategy. Renaming or repeating
the same strategy is not a strategy delta.

## ChatGPT Consultation Gate

- consultation_required: yes
- consultation_required_reason: P1 blocking repair will mutate the PR branch
- consultation_status: fresh
- consultation_id: `iss-00344-pr350-u001-consultati`
- consulted_at: `2026-07-29`
- bound_head_sha: `818a48303f7a59b625d10681e6a2182767828279`
- bound_observation_status: `human_gate` / F001
- bound_family_ids: F001
- bound_strategy_context: S350-001 exact-path ownership repair
- input_summary_ref: this batch and U001 discussion
- recommendation_summary_ref: `artifacts/20260729t142442z-chatgpt-output-pr-350-u001-blocking-repair-consultation-818a4830.md`; SHA-256 `acac05832884e9702aec9b192a0f0287656e52b26969a6c6565f1712061a5eb7`; 8,759 bytes
- freshness_invalidators: head, inventory, family grouping, or strategy change
- open_risks: exact-match provenance blindness、older-version README under-delete、symlink/non-regular/read-error preservation
- fallback_approval_status: not_requested
- fallback_invocation_id: N/A
- fallback_approved_by: N/A
- fallback_approved_at: N/A
- fallback_invocation_scope: N/A
- fallback_reason: N/A
- fallback_expires_when: N/A
- fallback_manual_analysis_ref: N/A
- fallback_consumed_at: N/A
- orchestrator_disposition_summary: REC-001をpartial-use。exact-path inventory repairと4 focused casesを採用し、retry marker削除は既存idempotent rerun契約を破壊するためreject。

Use only sanitized, repository-relative evidence references.
Do not paste raw model conversation, secrets, tokens, or absolute host paths. ChatGPT output is
advisory evidence and never authorizes branch mutation or a repair strategy.

A stale consultation must be refreshed first. Only when consultation and its
defined recovery are hard-unrecoverable may an explicit human approval permit
a one-invocation, local-only fallback. Record its scope, reason, and expiry; do
not represent fallback use as consultation success. A denied, missing, expired,
out-of-scope, or reused fallback approval requires a human gate.

`fallback_approval_denied` is an unconditional stop. An expired or consumed
fallback approval is an unconditional stop. A fallback approval is bound to
exactly one `fallback_invocation_id` and must not be reused. Record the manual
analysis in `fallback_manual_analysis_ref` and the orchestrator disposition
before any bounded worker handoff.

## Orchestrator Disposition

| recommendation_id | orchestrator_disposition | rationale | evidence_refs | scope_effect | resulting_strategy_id | residual_risk |
| --- | --- | --- | --- | --- | --- | --- |
| REC-001 | partial-use | core P1はvalid。既存exact-match seamを再利用する。retry marker残存はintentionalでF001原因ではないためmarker削除だけreject | consultation Artifact、`src/spec_dock/cli.py`、existing rerun test | `src/spec_dock/cli.py`とfocused uninstall testsだけ。marker lifecycle変更なし | S350-001 | older-version READMEはcurrent bytes mismatchで保存され得る |

Allowed dispositions are `use`, `partial-use`, `reject`, `defer`, and
`human-gate`. Only the orchestrator may turn dispositioned recommendations into
a bounded worker handoff.

## Blocking Repair Queue

Create repair units only for `P0`/`P1` families, required CI failures, or
blocking merge issues. Do not create repair units for `P2`/`P3` findings unless
they are directly and unavoidably covered by the same `P0`/`P1` root-cause fix.

| unit_id | source_batch | family_id | covered_items | decided_priority | merge_blocking | disposition | repair_unit_disc | status | implementation_plan | quality_gate | commit_evidence | re_observation_result | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U001 | 20260729t141008z-pr-repair-batch | F001 | R001 | P1 | yes | fix-now | `artifacts/20260729t141053z-disc-pr-350-repair-u001-uninstall-managed-inventory.md` | implemented | one exact target/source mapping; 4 focused Red/Green cases; retry marker preserved | G001-G003 pass / G004 pending | candidate commit pending | pending | current-byte exact ownership conservatively preserves older-version README |

## Non-Blocking Follow-up Register

Use this section only when a blocking repair commit is already being made and
`P2`/`P3` findings can be recorded without causing an additional record-only
push.

If the latest observation has only `P2`/`P3` findings and no blockers, do not
update this file. Put those findings in the terminal merge-prepared report
instead.

| followup_id | family_id | related_items | priority | rationale_for_no_action | residual_risk | suggested_followup_target |
| --- | --- | --- | --- | --- | --- | --- |

## Quality Gate Plan

Define family-level gates, not comment-level checks.

| gate_id | family_id | command_or_check | expected_result | covers_items | required_before_push |
| --- | --- | --- | --- | --- | --- |
| G001 | F001 | focused Red/Green uninstall exact node(s) | pass: Red `4 failed` by unmanaged classification; Green `4 passed` | R001 | yes |
| G002 | F001 | mismatch/payload preservation and retry regression | pass: selected `3 passed`; root Workbench `4 passed`; aggregate `46 passed`; CLI uninstall full `8 passed` | R001 | yes |
| G003 | F001 | Issue 344 aggregate + `make lint` + default pytest | pass: focused `11 passed`; node/copy `52 passed`; lint pass; default `672 passed / 2051 skipped` | R001 | yes |
| G004 | F001 | fixed exact-head PR observation | CI passes and no P0/P1 remains | R001 | yes |

## Re-observation Plan

- Latest head before repair: `7bac5ee606e235df52c3a23be433fba3cdbf491a`
- Expected head after repair:
- Re-observation command: fixed `wait_pr_observation.sh` with new exact head
- Trigger mode: post-once / resume
- Resume trigger comment id:
- Resume trigger created_at:
- New trigger approved: yes; required by the user-requested mergeable-PR workflow after branch-changing repair
- Re-observation required because: repair push changes PR head and stales the current review
- Re-observation skipped because: not applicable

## Iteration Ledger

| iteration_index | head_sha | observation_status | family_ids | recurrence_class | prior_strategy_id | proposed_strategy_id | strategy_delta | consultation_id/status | orchestrator_disposition | action_taken | fix_commit | re_observation_result | continuation_decision | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `7bac5ee606e235df52c3a23be433fba3cdbf491a` | human_gate / P1 | F001 | first-observed | none | S350-001 | exact generated assetを既存uninstall inventoryへ対称登録し、marker契約を分離 | `iss-00344-pr350-u001-consultati` / fresh at `818a4830` | REC-001 partial-use | U001 implemented and locally verified | pending | pending | create/push candidate, rerun fresh gates | none |

`iteration_index` is telemetry only; it does not authorize continuation or
stopping. Each row records the evidence-driven semantic decision for that
iteration.

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

## Semantic Stop / Human-Gate Conditions

Stop at a human gate when any condition applies:

- Any blocking inventory item remains `untriaged`.
- Any unresolved blocking `needs-human` item remains.
- A blocking repair unit has no bounded material `strategy_delta`, or only the
  same ineffective strategy remains.
- Observation output is not for the latest head SHA.
- Timeout or observation limitation lacks resume metadata.
- Resume would cross the recorded trigger boundary.
- A new trigger would be required but has not been approved.
- Scope expansion, requirement expansion, breaking change, migration, secret,
  deployment setting, permission/auth, external/flaky, or ambiguous review
  intent is involved.
- Current evidence is stale or incomplete and cannot be safely refreshed.
- No bounded, materially different strategy is supported by current evidence.
- The proposed strategy repeats an ineffective strategy without a material
  `strategy_delta`.
- Consultation is not fresh, unless a valid one-invocation, local-only fallback
  approval applies.
- Consultation or recovery is hard-unrecoverable and no valid fallback approval
  applies.
- The orchestrator cannot disposition a safe in-scope strategy.
- GitHub branch protection requires conversation resolution for unresolved
  `P2`/`P3` threads; this is a platform human gate, not a code repair target.

Continue repair only when current evidence is fresh, no hard stop applies, a
bounded material `strategy_delta` exists, consultation is fresh or the explicit
fallback applies, and validation plus re-observation can be completed safely.

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
