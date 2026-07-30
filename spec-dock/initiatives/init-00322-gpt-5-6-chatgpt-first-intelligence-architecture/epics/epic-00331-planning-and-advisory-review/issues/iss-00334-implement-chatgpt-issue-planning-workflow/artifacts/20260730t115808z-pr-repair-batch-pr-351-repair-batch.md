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
- Latest head SHA: `6c9302ab08c7f352e85a199b65bdeb522376171c`
- Observation command: `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh --pr 351 --trigger-mode post-once`
- Observation final JSON / evidence: GitHub Actions runs `30542196314`, `30542196080`, `30542189677`; Review `4818771681`; decision fingerprint `c39fd464126bdf8e871967029a7c08d313d71fc981d8552b2c0ed3d5ca37f71c`
- Observation status: `human_gate/blocker_present`
- Trigger comment id: `5130741381`
- Trigger created_at: `2026-07-30T12:21:25Z`
- Trigger boundary: `post-once` trigger for evidence head `6c9302ab08c7f352e85a199b65bdeb522376171c`
- Resume metadata: not applicable; explicit Review completed with current-head findings
- New trigger approved: yes after a bounded P1 repair is committed and pushed
- Observation limitation: none; `automation_stalled` reflects repeated stable blocker fingerprints, not missing evidence
- Batch status: `local-pass-awaiting-reobservation`

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
| latest_head_sha | `6c9302ab08c7f352e85a199b65bdeb522376171c` |
| observation_status | `human_gate/blocker_present` |
| required_ci_status | `passed` |
| review_status | `completed/findings` |
| p0_count | `0` |
| p1_count | `2` |
| p2_count | `1` |
| p3_count | `0` |
| required_ci_failure_count | `0` |
| merge_blocker_count | `2` |
| blocking_family_count | `2 open; 1 repaired` |
| non_blocking_family_count | `1` |
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
| R001 | ci | `Provider CI / provider-tests` run `30540472689`, job `90863805552` | CI | `tests/unit/domain/test_issue_planning_candidate.py` | 425 | `test_s10_current_v4_guide_satisfies_completeness_contract` opens a Git-untracked active-pointer path and fails with `FileNotFoundError` in a fresh GitHub Actions checkout | failing-test | `555dafd6f9e1252ddf8b50cb23c275e20c263266` | F001 | triaged |
| R002 | review | comment `3682683838`, Review `4818771681` | P1 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py` | 447 | output directory may be renamed and replaced by a symlink after validation; pathname-based staging can write outside the guarded directory before rejection | code-path/contract | `6c9302ab08c7f352e85a199b65bdeb522376171c` | F002 | triaged |
| R003 | review | comment `3682683856`, Review `4818771681` | P1 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py` | 1164 | archive apply does not revalidate canonical and companion preimages at the mutation boundary, allowing a concurrent edit/create to be overwritten | code-path/contract | `6c9302ab08c7f352e85a199b65bdeb522376171c` | F003 | triaged |
| R004 | review | comment `3682683844`, Review `4818771681` | P2 | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md` | 30 | documented `information_insufficient` output is reduced to `oracle_artifact_missing`, so missing-information questions are not returned through a typed transport | contract | `6c9302ab08c7f352e85a199b65bdeb522376171c` | F004 | triaged |

Do not keep example rows as active inventory.

## Concern Family Catalog

Group inventory items by shared root cause. Do not repair comments one-by-one.

| family_id | root_cause_family | family_title | protected_domain | invariant_or_contract | related_items | max_reported_priority | decided_priority | merge_blocking | disposition | repair_unit | family_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F001 | `issue-planning-test.active-pointer-fixture` | S10 companion completeness test depends on a machine-local active pointer | no | Provider CI tests must resolve committed fixtures from a fresh checkout | R001 | CI | required-ci | yes | fix-now | U001 | reobserved-pass |
| F002 | `issue-planning-candidate.output-directory-toctou` | Candidate staging and publication do not remain bound to the validated directory object | yes | candidate creation must not write outside the validated external output directory, including during detected races | R002 | P1 | P1 | yes | fix-now | U002 | local-pass |
| F003 | `issue-planning-apply.archive-preimage-revalidation` | Archive apply can overwrite post-preflight document or companion changes | yes | Human approval applies only to the exact preimage; drift before mutation must fail closed without losing concurrent changes | R003 | P1 | P1 | yes | fix-now | U003 | local-pass |
| F004 | `issue-planning-transport.information-insufficient` | Missing-information questions lack a typed transport result | no | official skill stop condition should be observable by the caller | R004 | P2 | P2 | no | follow-up | N/A | triaged |

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

### F002 `issue-planning-candidate.output-directory-toctou`

- Related inventory IDs: R002
- Reported priorities: P1
- Decided priority: P1
- Merge-blocking: yes
- Protected domain: yes, external-path and symlink safety.
- Contract / invariant: after accepting an external output directory, Candidate staging, fsync, no-replace publication, and cleanup must remain descriptor-bound to that same directory object.
- Root cause: `build_and_publish_candidate()` uses `output_guard.path` for `mkdtemp`, subsequent file operations, and final rename after a pathname-only guard, leaving a validation-to-use rename/symlink race.
- Why this is one family: staging and final publication share the same directory identity boundary.
- Validity analysis: provisionally valid from the concrete code path; fresh consultation and regression design must confirm the smallest descriptor-relative repair.
- Need-to-fix decision: yes if consultation confirms.
- Options considered:
  - revalidate the pathname more often: rejected because the write can already occur before revalidation.
  - hold the validated external directory descriptor and perform staging/publication/cleanup relative to it: proposed.
- Recommended disposition: fix-now, bounded to candidate publisher and focused tests.
- Repair scope: provider candidate infra, mechanical dogfood projection if required, and focused candidate publisher tests.
- Out of scope: Oracle, Prompt, Candidate schema/content, review/apply semantics, canonical docs.
- Quality gates: adversarial rename/symlink injection test must prove no repository/outside write; existing collision/determinism tests; focused and full regression.
- Residual risk: platform-specific descriptor-relative rename/no-replace behavior must retain Darwin/Linux support.
- Follow-up handling: none if re-observation closes the P1.

### F003 `issue-planning-apply.archive-preimage-revalidation`

- Related inventory IDs: R003
- Reported priorities: P1
- Decided priority: P1
- Merge-blocking: yes
- Protected domain: yes, canonical document and Human-authority safety.
- Contract / invariant: mutation may begin only while canonical target and companion destination preimages still match the preflight evidence.
- Root cause: archive mode bypasses `_git_bound_targets_are_stale()`, while snapshots taken later are treated as restore baselines without comparing them to the operation's pre-apply evidence.
- Why this is one family: canonical edits and absent-companion creation are both preimage drift at the same mutation boundary.
- Validity analysis: provisionally valid from the archive-mode early return and transaction ordering; consultation must confirm the existing evidence fields and failure result.
- Need-to-fix decision: yes if consultation confirms.
- Options considered:
  - reuse git-bound reviewed-HEAD comparison for archive mode: insufficient when the preflight preimage is a working-tree byte state rather than only HEAD.
  - compare transaction-boundary snapshots to the operation's recorded preimage OIDs/existence before any managed write: proposed.
- Recommended disposition: fix-now, bounded to archive preimage validation and race-injection tests.
- Repair scope: provider apply infra, mechanical dogfood projection if required, focused unit/integration tests.
- Out of scope: Human decision schema, Candidate identity, git-bound behavior redesign, publication policy.
- Quality gates: inject canonical edit and absent-companion create after application preflight; require rejection/no mutation/preservation; existing rollback/recovery/apply tests.
- Residual risk: new failure reason must use an existing closed result contract unless a schema change is proven necessary.
- Follow-up handling: none if re-observation closes the P1.

### F004 `issue-planning-transport.information-insufficient`

- Related inventory IDs: R004
- Reported priorities: P2
- Decided priority: P2
- Merge-blocking: no
- Protected domain: no.
- Contract / invariant: recovery guidance should eventually expose typed missing-information questions.
- Root cause: authoring artifact snapshot expects a ZIP and maps absence to `oracle_artifact_missing`.
- Validity analysis: plausible non-blocking contract gap; it does not open an unsafe success path or break the successful default workflow.
- Need-to-fix decision: follow-up only.
- Options considered: typed adapter result or removing the unsupported documented output; neither is required for the blocking repair.
- Recommended disposition: follow-up.
- Repair scope: none in this iteration.
- Out of scope: all R004 code and skill changes.
- Quality gates: N/A.
- Residual risk: callers receive a less specific failure when ChatGPT asks for missing information.
- Follow-up handling: report as non-blocking; do not create a repair unit or mutate the branch solely for R004.

## Root-Cause Family and Coupling Analysis

| family_id | root_cause_family | related_items | recurrence_class | coupling | evidence_ref | analysis_result |
| --- | --- | --- | --- | --- | --- | --- |
| F001 | `issue-planning-test.active-pointer-fixture` | R001 | first occurrence | test-only | GitHub Actions run `30540472689`, job `90863805552` | isolated required-CI fixture lookup defect |
| F002 | `issue-planning-candidate.output-directory-toctou` | R002 | first occurrence | candidate external-output safety | Review `4818771681`, comment `3682683838`; source line 447 | distinct blocking family |
| F003 | `issue-planning-apply.archive-preimage-revalidation` | R003 | first occurrence | archive apply mutation safety | Review `4818771681`, comment `3682683856`; source line 1164 | distinct blocking family; may share filesystem-safety validation patterns with F002 but not implementation |
| F004 | `issue-planning-transport.information-insufficient` | R004 | first occurrence | skill/adapter error transport | Review `4818771681`, comment `3682683844` | independent non-blocking family |

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

### Current strategy S002

- strategy_id: S002
- covered_family_ids: F002, F003
- prior_strategy_id: S001
- strategy_delta: new diagnosis and implementation domains. S001 fixed only a CI fixture; S002 hardens two production filesystem mutation boundaries with adversarial race tests. It does not repeat or extend the fixture repair.
- bounded_scope: candidate publisher directory-object binding; archive apply preimage comparison at the mutation boundary; required provider/dogfood parity; focused tests.
- ordering: implement F002 and F003 as independent repair units, then run their focused suites together before full verification.
- validation_plan: Red race tests per family; focused infra tests; explicit full-regression integration paths; `make lint`; ordinary fast pytest; provider/projection byte parity; validate; new-head PR observation.
- rollback_plan: revert each unit independently if it changes public result/schema or cannot preserve existing platform support.
- re_observation_plan: one new `post-once` observation only after both P1 units are committed and pushed.
- residual_risk: F004 remains non-blocking and unresolved; GitHub conversation resolution may require Human action after semantic blockers close.

### Current strategy S003

- strategy_id: S003
- covered_family_ids: F002, F003
- prior_strategy_id: S002
- strategy_delta: fresh defect-only Spec/Code review found that S002 did not retain the private stage entry identity from creation through cleanup; fresh QA review found that S002 checked archive preimages before, rather than after, the existing `after_operation_recorded` race boundary. S003 keeps the same two root-cause families and closes only these demonstrated residual windows.
- bounded_scope: candidate private stage/ZIP object identity checks and deterministic replacement tests; apply post-hook preimage recheck, discard-only `BACKED_UP` recovery, and deterministic post-check drift tests.
- ordering: implement F002 and F003 independently from the fresh consultation, then repeat focused tests and fresh defect-only review.
- validation_plan: replacement between stage mkdir/open, stage replacement before cleanup, staged ZIP replacement before publication; canonical edit and companion creation through `after_operation_recorded`; discard-cleanup interruption/recovery; focused infra tests; explicit full-regression apply integration; `make lint`; ordinary fast pytest; provider/projection byte parity; validate; new-head PR observation.
- rollback_plan: revert each S003 unit independently if it changes public schema/identity or broadens the threat model beyond the accepted deterministic race boundaries.
- re_observation_plan: one new `post-once` observation only after both S003 units pass fresh local review, are committed, and are pushed.
- residual_risk: the final identity-check-to-`unlink`/`rmdir` syscall-sized interval and post-final-preimage-check external multiwriter race are outside the accepted bounded threat model; F004 remains non-blocking.

### Current strategy S004

- strategy_id: S004
- covered_family_ids: F003
- prior_strategy_id: S003
- strategy_delta: fresh Spec／Code review confirmed that S003 closed the post-hook lost-update race but unconditionally reclassified a no-drift `BACKED_UP` crash as `stale`. S004 changes only recovery result classification while retaining discard-only safety.
- bounded_scope: load the durable backup before `BACKED_UP` recovery; compare current branch／HEAD／canonical／companion to backup snapshots; return `stale/apply_target_changed` only for actual drift and preserve pre-S003 `rolled_back/planning_commit_failed` for no drift.
- validation_plan: dedicated no-drift `after_operation_recorded` crash recovery; drifted cleanup-interruption recovery; restore-not-called assertions; apply unit and explicit full-regression integration; fresh defect-only review.
- rollback_plan: revert only S004 classification/helper/test changes if public result semantics or `MUTATING`+ rollback changes.
- re_observation_plan: unchanged; one new `post-once` observation after all local gates pass and the integrated repair is committed/pushed.
- residual_risk: point-in-time classification can race a later external writer, but `BACKED_UP` recovery never writes or restores managed targets.

### Current strategy S005

- strategy_id: S005
- covered_family_ids: F002, F003
- prior_strategy_id: S004
- strategy_delta: fresh Code review demonstrated that directory ownership was first observed after `mkdirat`, allowing a pre-stat replacement to be trusted, and that unknown durable state could enter destructive restore. S005 removes the non-atomic stage-directory ownership step and closes recovery-state admissibility before destructive helpers.
- bounded_scope: direct atomic hidden staged ZIP creation under the validated output descriptor; closed durable-state vocabulary and transaction-state classifier; deterministic replacement/collision/invalid-evidence tests.
- validation_plan: candidate atomic-create flags/no directory stage, immediate staged-name replacement, bounded collision retry; unknown and known-invalid transaction states with no backup/restore/discard helper calls; valid S004 and `MUTATING`+ recovery regression; focused, fast, lint, parity, validate, fresh defect-only review.
- rollback_plan: revert atomic staged-file or state-classifier units independently if deterministic ZIP/public result semantics change.
- re_observation_plan: unchanged; commit/push only after S005 fresh local review passes, then one new `post-once` PR observation.
- residual_risk: accepted final identity-check-to-name-operation syscall interval and same-credential substitution of a different valid durable state remain outside the bounded threat model.

### Current strategy S006

- strategy_id: S006
- covered_family_ids: F003
- prior_strategy_id: S005
- strategy_delta: fresh Code review demonstrated that S005 classified durable state only when `transaction/` existed. S006 extends the same closed classifier to the no-transaction route before attempt recording and durably records successful rollback completion.
- bounded_scope: commit／transaction／no-transaction route ordering; no-transaction start states `OPERATION_RECORDED`／`ROLLED_BACK`; invalid-state/orphan-publication fail-closed; rollback final-state durability; focused retry and evidence-preservation tests.
- validation_plan: natural backup-remove/state-write failure, unknown／known invalid no-transaction matrix, orphan publication, legitimate `OPERATION_RECORDED`／`ROLLED_BACK` retry, commit/transaction recovery regressions; focused, fast, lint, parity, validate, fresh final review.
- rollback_plan: revert only S006 route/classifier and rollback-state changes if valid retry or resume semantics regress.
- re_observation_plan: unchanged; commit/push after S006 final local review pass, followed by one new `post-once` PR observation.
- residual_risk: same-credential rewrite to a different semantically valid private state remains outside the ownership/permission threat model.

The strategy must be bounded, in scope, supported by current evidence, and
materially different from an ineffective prior strategy. Renaming or repeating
the same strategy is not a strategy delta.

## ChatGPT Consultation Gate

- consultation_required: yes
- consultation_required_reason: PR merge-preparation repair requires a fresh bounded ChatGPT consultation before worker handoff.
- consultation_status: fresh
- consultation_id: `required-repository-connector-context-github-20` (follow-up to `iss00334-pr351-s003-race-closure`)
- consulted_at: `2026-07-30`
- bound_head_sha: `6c9302ab08c7f352e85a199b65bdeb522376171c`
- bound_observation_status: `human_gate/blocker_present`
- bound_family_ids: F002, F003, F004
- bound_strategy_context: S006
- input_summary_ref: this batch plus the exact candidate/apply/skill sources and focused tests
- recommendation_summary_ref: `20260730t145257z-pr-351-s006-no-transaction-state-chatgpt-followup.md`
- freshness_invalidators: new head, changed finding inventory/grouping, different source behavior, or changed S006 strategy
- open_risks: accepted syscall-sized cleanup race, post-final-check single-writer residual, and P2 platform-thread handling
- fallback_approval_status: not_requested / approved_for_invocation / fallback_approval_denied / expired
- fallback_invocation_id:
- fallback_approved_by:
- fallback_approved_at:
- fallback_invocation_scope:
- fallback_reason:
- fallback_expires_when:
- fallback_manual_analysis_ref:
- fallback_consumed_at:
- orchestrator_disposition_summary: `use` for C002/C003 and `defer` for C004. Exact-head ChatGPT consultation confirmed F002/F003 as independent P1 repairs and narrowed their implementation/test contracts. U002/U003 are authorized; F004 remains non-blocking with no branch mutation.

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
| C002 | use | Descriptor-relative publication is the smallest design that closes both pre-write and post-check pathname replacement races while preserving Candidate contracts | `20260730t130735z-01-pr-351-s002-p1-repair-chatgpt-consultation.md`; R002/F002 | authorize provider candidate infra and focused tests only | S002/U002 | Darwin native descriptor-relative rename validation |
| C003 | use | Transaction-boundary preimage comparison closes canonical and companion lost-update windows without schema expansion | `20260730t130735z-01-pr-351-s002-p1-repair-chatgpt-consultation.md`; R003/F003 | authorize provider apply infra and focused unit/integration tests only | S002/U003 | post-boundary single-writer assumption remains |
| C004 | defer | P2 incomplete-input transport does not block the safe successful workflow and is independent of both P1 roots | R004/F004 | no source/skill/schema mutation in this PR repair | N/A | less-specific failure remains until follow-up |

Allowed dispositions are `use`, `partial-use`, `reject`, `defer`, and
`human-gate`. Only the orchestrator may turn dispositioned recommendations into
a bounded worker handoff.

## Blocking Repair Queue

Create repair units only for `P0`/`P1` families, required CI failures, or
blocking merge issues. Do not create repair units for `P2`/`P3` findings unless
they are directly and unavoidably covered by the same `P0`/`P1` root-cause fix.

| unit_id | source_batch | family_id | covered_items | decided_priority | merge_blocking | disposition | repair_unit_disc | status | implementation_plan | quality_gate | commit_evidence | re_observation_result | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U001 | 20260730t115808z-pr-repair-batch | F001 | R001 | required-ci | yes | fix-now | `20260730t120701z-disc-pr-repair-unit-active-pointer-fixture.md` | reobserved-pass | replaced only the test fixture path with the tracked canonical Issue ZIP path | exact `1 passed`; module `54 passed`; fast pytest `1141 passed, 2119 skipped`; lint PASS; validate `nodes=227`; diff-check PASS | `b70f599f1689b2867fc70699c68c3d955d1f18d5` | Actions 3 runs PASS; Codex explicit no-findings completion; blockers/threads/limitations 0; `merge_prepared` | historical fixture path coupling only |
| U002 | 20260730t115808z-pr-repair-batch | F002 | R002 | P1 | yes | fix-now | `20260730t130735z-disc-pr-repair-unit-candidate-output-directory-toctou.md` | unit-created | descriptor-bound candidate staging/publication/cleanup with adversarial rename/symlink test | focused candidate infra tests, platform behavior, full verification, fresh observation | pending | pending | platform-specific directory-descriptor operations |
| U003 | 20260730t115808z-pr-repair-batch | F003 | R003 | P1 | yes | fix-now | `20260730t130735z-02-disc-pr-repair-unit-archive-preimage-revalidation.md` | unit-created | archive preimage revalidation immediately before mutation with concurrent edit/create tests | focused apply unit/integration tests, full verification, fresh observation | pending | pending | closed failure reason and snapshot ordering |

## Non-Blocking Follow-up Register

Use this section only when a blocking repair commit is already being made and
`P2`/`P3` findings can be recorded without causing an additional record-only
push.

If the latest observation has only `P2`/`P3` findings and no blockers, do not
update this file. Put those findings in the terminal merge-prepared report
instead.

| followup_id | family_id | related_items | priority | rationale_for_no_action | residual_risk | suggested_followup_target |
| --- | --- | --- | --- | --- | --- | --- |
| NB001 | F004 | R004 | P2 | non-blocking incomplete-input recovery only; must not expand S002 | missing-information questions remain unavailable through the typed result | separate follow-up Issue after this PR |

## Quality Gate Plan

Define family-level gates, not comment-level checks.

| gate_id | family_id | command_or_check | expected_result | covers_items | required_before_push |
| --- | --- | --- | --- | --- | --- |
| G002 | F002 | adversarial output-dir rename/symlink race plus existing candidate publisher suite | no write outside original validated directory; closed failure; existing behavior preserved | R002 | yes |
| G003 | F003 | archive preflight-to-mutation canonical edit and absent-companion create injections plus apply suite | reject before managed mutation and preserve concurrent bytes/existence | R003 | yes |
| G004 | F002,F003 | `make lint`; ordinary fast pytest; explicit required integration; byte parity; validate | all pass | R002,R003 | yes |

## Re-observation Plan

- Latest head before repair: `6c9302ab08c7f352e85a199b65bdeb522376171c`
- Expected head after repair: to be recorded after S002 commit/push
- Re-observation command: fixed `wait_pr_observation.sh` for PR #351 and the pushed S002 head
- Trigger mode: `post-once`
- Resume trigger comment id: N/A
- Resume trigger created_at: N/A
- New trigger approved: yes, as the required latest-head observation after bounded P1 repair
- Re-observation required because: two current-head P1 families require branch mutation
- Re-observation skipped because: N/A

## Iteration Ledger

| iteration_index | head_sha | observation_status | family_ids | recurrence_class | prior_strategy_id | proposed_strategy_id | strategy_delta | consultation_id/status | orchestrator_disposition | action_taken | fix_commit | re_observation_result | continuation_decision | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `555dafd6f9e1252ddf8b50cb23c275e20c263266` | required CI failed | F001 | first occurrence | none | S001 | canonical tracked fixture path | `iss00334-pr351-ci-repair-consult`/fresh | use | U001 implemented | `b70f599f1689b2867fc70699c68c3d955d1f18d5` | PASS/no findings | continue to evidence publication | none |
| 2 | `6c9302ab08c7f352e85a199b65bdeb522376171c` | P1=2, P2=1, CI passed | F002,F003,F004 | new families | S001 | S002 | production filesystem safety repairs, not a fixture retry | `iss00334-pr351-s002-p1-repair-2`/fresh | use F002/F003; defer F004 | U002/U003 created | pending | pending | continue bounded implementation | none |

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
