---
種別: pr-repair-batch
ID: "20260730t115808z-pr-repair-batch"
タイトル: "PR 351 Repair Batch"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-30"
親: ["iss-00334"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260730t115808z-pr-repair-batch PR 351 Repair Batch

## PR / Observation Metadata

- PR URL: `https://github.com/chemitaro/spec-dock/pull/351`
- PR number: `351`
- Repository: `chemitaro/spec-dock`
- Base branch: `main`
- Head branch: `iss-00334-implement-chatgpt-issue-planning-workflow`
- Latest head SHA: `555dafd6f9e1252ddf8b50cb23c275e20c263266`
- Observation command: `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh --pr 351 --trigger-mode post-once`
- Observation final JSON / evidence: required check `Provider CI / provider-tests`, run `30540472689`, job `90863805552`
- Observation status: `failed`
- Trigger comment id: `5130515748`
- Trigger created_at: `2026-07-30T11:57:12Z`
- Trigger boundary: `post-once` trigger for head `555dafd6f9e1252ddf8b50cb23c275e20c263266`
- Resume metadata: old-head resume boundary must not be reused after repair push
- New trigger approved: yes, after a new repair head is pushed
- Observation limitation: review observation stopped at the required-CI failure; no terminal Codex review verdict is available for this head
- Batch status: `implemented`

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
| latest_head_sha | `555dafd6f9e1252ddf8b50cb23c275e20c263266` |
| observation_status | `failed` |
| required_ci_status | `failure` |
| review_status | `not-terminal` |
| p0_count | `0 observed` |
| p1_count | `0 observed` |
| p2_count | `0 observed` |
| p3_count | `0 observed` |
| required_ci_failure_count | `1` |
| merge_blocker_count | `1` |
| blocking_family_count | `1` |
| non_blocking_family_count | `0` |
| terminal_non_blocking_only | no |
| branch_mutation_required | yes |
| ci_rerun_expected | yes |
| review_clean | unknown |
| merge_prepared_candidate | no |

## Raw Intake Inventory

Add one row per observed review finding, required CI failure, merge blocker, or
observation limitation from the same observation batch. Keep raw reviewer
priority separate from the final severity decision.

| item_id | source_type | source_id | reported_priority | path | line | raw_summary | evidence_type | current_head_sha | family_id | intake_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R001 | ci | `Provider CI / provider-tests` run `30540472689`, job `90863805552` | CI | `tests/unit/domain/test_issue_planning_candidate.py` | 425 | `test_s10_current_v4_guide_satisfies_completeness_contract` opens a Git-untracked active-pointer path and fails with `FileNotFoundError` in a fresh GitHub Actions checkout | failing-test | `555dafd6f9e1252ddf8b50cb23c275e20c263266` | F001 | triaged |

Do not keep example rows as active inventory.

## Concern Family Catalog

Group inventory items by shared root cause. Do not repair comments one-by-one.

| family_id | root_cause_family | family_title | protected_domain | invariant_or_contract | related_items | max_reported_priority | decided_priority | merge_blocking | disposition | repair_unit | family_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F001 | `issue-planning-test.active-pointer-fixture` | S10 companion completeness test depends on a machine-local active pointer | no | Provider CI tests must resolve committed fixtures from a fresh checkout | R001 | CI | required-ci | yes | fix-now | U001 | implemented |

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

### F001 `issue-planning-test.active-pointer-fixture`

- Related inventory IDs: R001
- Reported priorities: CI
- Decided priority: required-ci
- Merge-blocking: yes
- Protected domain: no
- Contract / invariant: committed test fixtures must be reachable from a fresh checkout without a developer-local active symlink.
- Root cause: the test constructs its ZIP path through `spec-dock/active/issue`, which is an untracked local symlink. The exact ZIP is tracked under the canonical `iss-00334` artifact directory.
- Why this is one family: one failing test and one environment-sensitive fixture lookup share the same direct cause.
- Validity analysis: valid. GitHub Actions produced a concrete `FileNotFoundError`; `git ls-files` confirms the canonical ZIP is tracked and the active symlink is not.
- Need-to-fix decision: yes.
- Options considered:
  - Track or synthesize the active pointer in CI: rejected as a broader environment coupling.
  - Change the test fixture path to the tracked canonical artifact: selected as the smallest deterministic repair.
- Recommended disposition: fix-now.
- Repair scope: change only the ZIP fixture path in `test_s10_current_v4_guide_satisfies_completeness_contract`.
- Out of scope: product runtime, Oracle invocation/configuration, canonical requirement/design/plan, ZIP bytes, active-pointer lifecycle.
- Quality gates: exact test, the complete candidate domain test module, ordinary fast pytest, lint, SpecDock validate, and fresh PR observation on the pushed repair head.
- Residual risk: a long canonical path is coupled to this historical dogfood fixture, but that coupling already exists in the test's named S10/v4 contract and is deterministic in CI.
- Follow-up handling: none unless fresh observation exposes a distinct blocker.

## Root-Cause Family and Coupling Analysis

| family_id | root_cause_family | related_items | recurrence_class | coupling | evidence_ref | analysis_result |
| --- | --- | --- | --- | --- | --- | --- |
| F001 | `issue-planning-test.active-pointer-fixture` | R001 | first occurrence | test-only | GitHub Actions run `30540472689`, job `90863805552` | isolated required-CI fixture lookup defect |

When a `root_cause_family` recurs, re-analyze the current evidence, root-cause
hypothesis, coupling, and prior result. Recurrence alone is not a stop reason.

## Integrated Repair Strategy

- strategy_id: S001
- covered_family_ids: F001
- prior_strategy_id: none
- strategy_delta: first repair strategy; replace an environment-local pointer lookup with the exact tracked canonical artifact path.
- bounded_scope: one path construction in `tests/unit/domain/test_issue_planning_candidate.py`.
- validation_plan: run the exact failed test, the full test module, ordinary fast pytest, `make lint`, `./spec-dock/scripts/spec-dock validate`, and diff/status inspection.
- rollback_plan: revert only the one test-path change if the canonical fixture is not available or the completeness assertions no longer target the intended ZIP.
- re_observation_plan: commit and push the repair, then invoke a new `post-once` observation for PR #351 at the new head; do not resume the old-head trigger boundary.
- residual_risk: review status for the old head is not terminal because required CI failed first.

The strategy must be bounded, in scope, supported by current evidence, and
materially different from an ineffective prior strategy. Renaming or repeating
the same strategy is not a strategy delta.

## ChatGPT Consultation Gate

- consultation_required: yes
- consultation_required_reason: PR merge-preparation repair requires a fresh bounded ChatGPT consultation before worker handoff.
- consultation_status: fresh
- consultation_id: `iss00334-pr351-ci-repair-consult`
- consulted_at: `2026-07-30`
- bound_head_sha: `555dafd6f9e1252ddf8b50cb23c275e20c263266`
- bound_observation_status: `failed`
- bound_family_ids: F001
- bound_strategy_context: S001
- input_summary_ref: this batch, R001/F001/S001, and `tests/unit/domain/test_issue_planning_candidate.py`
- recommendation_summary_ref: `20260730t120701z-01-pr-351-required-ci-repair-chatgpt-consultation.md`
- freshness_invalidators: a new head, different failed check, different fixture identity, or evidence that the canonical ZIP is absent
- open_risks: long canonical historical-fixture path may be mistyped; the exact focused test detects this directly
- fallback_approval_status: not_requested / approved_for_invocation / fallback_approval_denied / expired
- fallback_invocation_id:
- fallback_approved_by:
- fallback_approved_at:
- fallback_invocation_scope:
- fallback_reason:
- fallback_expires_when:
- fallback_manual_analysis_ref:
- fallback_consumed_at:
- orchestrator_disposition_summary: `use`. ChatGPT independently confirmed F001 and S001 against the exact branch/HEAD. U001 is authorized with a one-test write allowlist; architecture, product runtime, Oracle boundary, canonical docs, and ZIP bytes remain excluded.

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
| C001 | use | Exact-branch consultation confirmed the CI root cause and the one-test fixture path correction as the smallest correct repair | `20260730t120701z-01-pr-351-required-ci-repair-chatgpt-consultation.md`; R001/F001 | no scope expansion; authorize U001 only | S001 | path transcription error, caught by focused test |

Allowed dispositions are `use`, `partial-use`, `reject`, `defer`, and
`human-gate`. Only the orchestrator may turn dispositioned recommendations into
a bounded worker handoff.

## Blocking Repair Queue

Create repair units only for `P0`/`P1` families, required CI failures, or
blocking merge issues. Do not create repair units for `P2`/`P3` findings unless
they are directly and unavoidably covered by the same `P0`/`P1` root-cause fix.

| unit_id | source_batch | family_id | covered_items | decided_priority | merge_blocking | disposition | repair_unit_disc | status | implementation_plan | quality_gate | commit_evidence | re_observation_result | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U001 | 20260730t115808z-pr-repair-batch | F001 | R001 | required-ci | yes | fix-now | `20260730t120701z-disc-pr-repair-unit-active-pointer-fixture.md` | implemented | replaced only the test fixture path with the tracked canonical Issue ZIP path | exact `1 passed`; module `54 passed`; fast pytest `1141 passed, 2119 skipped`; lint PASS; validate `nodes=227`; diff-check PASS | pending commit | pending new-head observation | historical fixture path coupling only |

## Non-Blocking Follow-up Register

Use this section only when a blocking repair commit is already being made and
`P2`/`P3` findings can be recorded without causing an additional record-only
push.

If the latest observation has only `P2`/`P3` findings and no blockers, do not
update this file. Put those findings in the terminal merge-prepared report
instead.

| followup_id | family_id | related_items | priority | rationale_for_no_action | residual_risk | suggested_followup_target |
| --- | --- | --- | --- | --- | --- | --- |
| NBXXX | FXXX | RXXX | P2 / P3 |  |  |  |

## Quality Gate Plan

Define family-level gates, not comment-level checks.

| gate_id | family_id | command_or_check | expected_result | covers_items | required_before_push |
| --- | --- | --- | --- | --- | --- |
| GXXX | FXXX |  |  | RXXX | yes / no |

## Re-observation Plan

- Latest head before repair:
- Expected head after repair:
- Re-observation command:
- Trigger mode: post-once / resume
- Resume trigger comment id:
- Resume trigger created_at:
- New trigger approved: yes / no
- Re-observation required because:
- Re-observation skipped because:

## Iteration Ledger

| iteration_index | head_sha | observation_status | family_ids | recurrence_class | prior_strategy_id | proposed_strategy_id | strategy_delta | consultation_id/status | orchestrator_disposition | action_taken | fix_commit | re_observation_result | continuation_decision | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

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
