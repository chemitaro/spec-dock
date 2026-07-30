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
- Latest observed head SHA: `be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2`
- Observation command: `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh --pr 351 --trigger-mode post-once`
- Observation final JSON / evidence: `20260730t172342z-pr-351-observation-head-be0c84a6.json`; Review `4821379670`
- Observation status: `human_gate/blocker_present`
- Trigger comment id: recorded in the raw observation artifact
- Trigger created_at: recorded in the raw observation artifact
- Trigger boundary: `post-once` trigger for evidence head `be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2`
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
| latest_head_sha | `be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2` |
| observation_status | `human_gate/blocker_present` |
| required_ci_status | `passed` |
| review_status | `completed/findings` |
| p0_count | `0` |
| p1_count | `3` |
| p2_count | `2` |
| p3_count | `0` |
| required_ci_failure_count | `0` |
| merge_blocker_count | `3` |
| blocking_family_count | `3 locally repaired; awaiting new-head observation` |
| non_blocking_family_count | `4` |
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
| R005 | review | Review `4820348714` | P1 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py` | N/A | validated output-directory identity was not retained through the apply evidence lifecycle | code-path/contract | `91715eecf306bd0c978da922f87193151764cdcd` | F005 | triaged |
| R006 | review | Review `4820348714` | P1 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py` | N/A | initial and resume push lacked an exact expected-old remote-ref CAS | code-path/contract | `91715eecf306bd0c978da922f87193151764cdcd` | F006 | triaged |
| R007 | review | Review `4820348714` | P1 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py` | N/A | verified staged identity could still be replaced before pathname-based final publication | code-path/contract | `91715eecf306bd0c978da922f87193151764cdcd` | F007 | triaged |
| R008 | review | Review `4820348714` | P2 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py` | N/A | a crash after Git commit but before durable commit evidence can leave a manual recovery gap | contract | `91715eecf306bd0c978da922f87193151764cdcd` | F008 | triaged |
| R009 | review | comment `3684744601`, Review `4821379670` | P1 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py` | N/A | descriptor-bound publication can succeed after the visible output path is detached, returning a path that does not identify the published Candidate | code-path/contract | `be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2` | F009 | triaged |
| R010 | review | comment `3684744608`, Review `4821379670` | P1 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py` | N/A | a canonical preimage can change after the final global check and before its unconditional replacement | code-path/contract | `be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2` | F010 | triaged |
| R011 | review | comment `3684744611`, Review `4821379670` | P1 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py` | N/A | canonical mutation and rollback can follow a swapped ancestor symlink outside the repository | code-path/contract | `be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2` | F011 | triaged |
| R012 | review | comment `3684744618`, Review `4821379670` | P2 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/oracle_issue_planning.py` | N/A | Oracle session repository-boundary behavior lacks a stronger product-side invariant | contract | `be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2` | F012 | triaged |
| R013 | review | comment `3684744623`, Review `4821379670` | P2 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py` | N/A | mechanical-revision meaning equivalence is not enforced beyond the current closed validation contract | contract | `be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2` | F013 | triaged |

Do not keep example rows as active inventory.

## Concern Family Catalog

Group inventory items by shared root cause. Do not repair comments one-by-one.

| family_id | root_cause_family | family_title | protected_domain | invariant_or_contract | related_items | max_reported_priority | decided_priority | merge_blocking | disposition | repair_unit | family_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F001 | `issue-planning-test.active-pointer-fixture` | S10 companion completeness test depends on a machine-local active pointer | no | Provider CI tests must resolve committed fixtures from a fresh checkout | R001 | CI | required-ci | yes | fix-now | U001 | reobserved-pass |
| F002 | `issue-planning-candidate.output-directory-toctou` | Candidate staging and publication do not remain bound to the validated directory object | yes | candidate creation must not write outside the validated external output directory, including during detected races | R002 | P1 | P1 | yes | fix-now | U002 | local-pass |
| F003 | `issue-planning-apply.archive-preimage-revalidation` | Archive apply can overwrite post-preflight document or companion changes | yes | Human approval applies only to the exact preimage; drift before mutation must fail closed without losing concurrent changes | R003 | P1 | P1 | yes | fix-now | U003 | local-pass |
| F004 | `issue-planning-transport.information-insufficient` | Missing-information questions lack a typed transport result | no | official skill stop condition should be observable by the caller | R004 | P2 | P2 | no | follow-up | N/A | triaged |
| F005 | `issue-planning-apply.output-directory-identity` | Apply evidence lifecycle can escape the validated output directory object | yes | all operation evidence must remain bound to the validated directory identity | R005 | P1 | P1 | yes | fix-now | U004 | local-pass-awaiting-reobservation |
| F006 | `issue-planning-apply.remote-ref-cas` | Push can overwrite or recreate a concurrently changed/deleted remote ref | yes | remote publication must compare the exact expected old ref immediately at push | R006 | P1 | P1 | yes | fix-now | U005 | local-pass-awaiting-reobservation |
| F007 | `issue-planning-candidate.staged-fd-publication` | Candidate final publication can switch away from the verified staged object | yes | final publication must derive from the already verified staged FD without pathname fallback | R007 | P1 | P1 | yes | fix-now | U006 | local-pass-awaiting-reobservation |
| F008 | `issue-planning-apply.post-commit-record-gap` | Commit evidence can lag a successfully created Git commit | no | recovery should eventually classify a post-commit evidence interruption | R008 | P2 | P2 | no | follow-up | N/A | triaged |
| F009 | `issue-planning-candidate.output-path-attachment` | Candidate success can return a visible path detached from the descriptor-published file | yes | a successful create result must identify the exact published Candidate through the visible output path | R009 | P1 | P1 | yes | fix-now | U007 | local-pass-awaiting-reobservation |
| F010 | `issue-planning-apply.per-target-preimage-cas` | canonical or companion drift can occur after the global preflight check | yes | exact preimage comparison must be coupled atomically to each replacement boundary | R010 | P1 | P1 | yes | fix-now | U009 | local-pass-awaiting-reobservation |
| F011 | `issue-planning-apply.repository-target-authority` | pathname mutation and rollback can escape through a replaced ancestor | yes | transaction-owned repository writes and rollback must remain bound to captured no-follow parent descriptors | R011 | P1 | P1 | yes | fix-now | U008 | local-pass-awaiting-reobservation |
| F012 | `issue-planning-oracle.session-repository-boundary` | stronger repository-bound Oracle session assurance is desirable | no | external advisory sessions should remain attributable to the intended repository state | R012 | P2 | P2 | no | follow-up | N/A | triaged |
| F013 | `issue-planning-review.mechanical-meaning-invariant` | mechanical revision meaning equivalence is not independently enforced | no | future assurance may strengthen semantic-preservation evidence without changing this safe success path | R013 | P2 | P2 | no | follow-up | N/A | triaged |

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

### Current strategy S007

- strategy_id: S007
- covered_family_ids: F005, F006, F007
- prior_strategy_id: S006
- strategy_delta: exact-head Review `4820348714` identified three new object-identity/CAS boundaries after S006 passed local review. S007 retains validated output-directory authority through apply, publishes Candidate directly from the verified staged FD, and makes remote publication an exact expected-old CAS.
- bounded_scope: provider Candidate/apply infra; application/port/bootstrap guard plumbing; mechanical dogfood projection; deterministic race and CAS tests. Public schema/status/reason, canonical planning docs, Oracle/configuration, and P2 changes are excluded.
- validation_plan: Candidate OS primitive and staged-name replacement tests; apply output replacement before/after FD capture; initial/resume remote delete/rewind races; exact lease argv and unavailable classification; focused suites; explicit full-regression apply integration; fast tests; lint; provider/projection parity; validate; fresh P0/P1-only review; new-head PR observation.
- rollback_plan: revert Candidate FD publication, apply evidence FD lifecycle, and exact-old CAS as independent units if any changes public contracts or cannot fail closed.
- re_observation_plan: commit/push only after fresh local Spec/Code/QA P0/P1 gates pass; then review the exact code HEAD with fresh ChatGPT and run one fixed `post-once` observation on the final evidence head.
- residual_risk: F008 remains a non-blocking recovery ergonomics gap; it must not cause branch mutation or an additional review cycle by itself.

### Current strategy S008

- strategy_id: S008
- covered_family_ids: F005, F006, F007
- prior_strategy_id: S007
- strategy_delta: fresh local Spec／Code／QA review found three bounded closure gaps in the S007 implementation: capability-gated Linux `AT_EMPTY_PATH`, collapsed absent/unavailable classification at resume entry, and missing application-level guard-identity regression protection. The underlying S007 architecture and public contracts remain unchanged.
- bounded_scope: Linux `_link_exclusive_linux_at` ABI plus one real non-privileged Linux syscall test; resume-entry three-state classification plus two integration tests; one application object-identity propagation test. No production application redesign, public schema/status/reason change, Oracle/configuration change, canonical planning change, or P2 work.
- validation_plan: exact new tests; Candidate infra; application apply; apply unit; explicit full-regression apply integration; ordinary fast lane; lint; provider/projection parity; validate; fresh P0/P1-only Spec/Code/QA review; exact-head ChatGPT review after push; fixed PR observation.
- rollback_plan: revert each of the three independent bounded units if it broadens public behavior or fails its exact platform/race contract.
- re_observation_plan: unchanged; commit/push only after the S008 local review passes, then obtain fresh ChatGPT defect-only review on the exact code HEAD and one fixed PR observation on the final evidence HEAD.
- residual_risk: the real Linux primitive is locally skipped on Darwin and must pass on unprivileged Provider CI; missing/inaccessible procfs or unsupported hard links fail closed.

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
| U004 | 20260730t115808z-pr-repair-batch | F005 | R005 | P1 | yes | fix-now | `20260730t155200z-pr-351-s007-p1-repair-chatgpt-concretization.md` | local-pass-awaiting-reobservation | retain `OutputDirectoryGuard` into resume/transaction and use FD-relative operation evidence lifecycle | apply unit/application `57 passed`; explicit full-regression integration `66 passed`; fast/lint/parity/validate PASS | pending | pending | original directory may become pathname-inaccessible after rename but remains authoritative through its FD |
| U005 | 20260730t115808z-pr-repair-batch | F006 | R006 | P1 | yes | fix-now | `20260730t155200z-pr-351-s007-p1-repair-chatgpt-concretization.md` | local-pass-awaiting-reobservation | one exact-old CAS helper for initial/resume push with pre-push HEAD/parent/tree/branch proof | delete/rewind race and lease-argv tests; apply suites/full verification PASS | pending | pending | failed CAS intentionally leaves the local operation commit for bounded retry |
| U006 | 20260730t115808z-pr-repair-batch | F007 | R007 | P1 | yes | fix-now | `20260730t155200z-pr-351-s007-p1-repair-chatgpt-concretization.md` | local-pass-awaiting-reobservation | Darwin `fclonefileat`／Linux `linkat(AT_EMPTY_PATH)` publication from verified staged FD, no pathname fallback | Candidate infra `34 passed`; OS primitive, source-swap, collision, backend failure coverage PASS | pending | pending | unsupported descriptor-publication backend fails closed |

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
| NB002 | F008 | R008 | P2 | non-blocking recovery gap; branch mutation and another review cycle are prohibited solely for this item | a crash between commit creation and durable commit evidence may require manual recovery | separate follow-up Issue after this PR |
| NB003 | F012 | R012 | P2 | current fixed-head observation classified this as non-blocking; S009 must not change the accepted local Oracle configuration boundary | repository attribution continues to rely on the existing explicit GitHub/branch/head prompt and Oracle evidence contract | later Epic work on stronger advisory-session assurance |
| NB004 | F013 | R013 | P2 | current closed Review/Candidate validation contract has no unsafe success path requiring this PR to expand semantic analysis | a semantically different but mechanically valid revision may require Human detection under the current contract | later Epic work on mechanical-revision assurance |

## Quality Gate Plan

Define family-level gates, not comment-level checks.

| gate_id | family_id | command_or_check | expected_result | covers_items | required_before_push |
| --- | --- | --- | --- | --- | --- |
| G002 | F002 | adversarial output-dir rename/symlink race plus existing candidate publisher suite | no write outside original validated directory; closed failure; existing behavior preserved | R002 | yes |
| G003 | F003 | archive preflight-to-mutation canonical edit and absent-companion create injections plus apply suite | reject before managed mutation and preserve concurrent bytes/existence | R003 | yes |
| G004 | F002,F003 | `make lint`; ordinary fast pytest; explicit required integration; byte parity; validate | all pass | R002,R003 | yes |
| G005 | F009 | visible output path symlink and ordinary-directory detachment tests plus Candidate suite | reject success, remove descriptor-published entry, preserve normal publication contract | R009 | yes |
| G006 | F011 | ancestor swap during forward mutation and rollback plus target-guard unit tests | no external sentinel mutation; descriptor-bound writes only; fail closed on unverifiable recovery | R011 | yes |
| G007 | F010 | per-target canonical edit and absent companion create injections plus apply suite | preserve concurrent bytes/existence, reverse only owned mutations, return existing stale result | R010 | yes |
| G008 | F009,F010,F011 | focused Candidate/Application/Apply, explicit apply full-regression, ordinary fast pytest, lint, parity, validate | all pass | R009,R010,R011 | yes |

## Re-observation Plan

- Latest head before repair: `be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2`
- Expected head after repair: to be recorded after S009 commit/push
- Re-observation command: fixed `wait_pr_observation.sh` for PR #351 and the pushed S002 head
- Trigger mode: `post-once`
- Resume trigger comment id: N/A
- Resume trigger created_at: N/A
- New trigger approved: yes, as the required latest-head observation after bounded P1 repair
- Re-observation required because: three current-head P1 families require branch mutation
- Re-observation skipped because: N/A

## Iteration Ledger

| iteration_index | head_sha | observation_status | family_ids | recurrence_class | prior_strategy_id | proposed_strategy_id | strategy_delta | consultation_id/status | orchestrator_disposition | action_taken | fix_commit | re_observation_result | continuation_decision | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `555dafd6f9e1252ddf8b50cb23c275e20c263266` | required CI failed | F001 | first occurrence | none | S001 | canonical tracked fixture path | `iss00334-pr351-ci-repair-consult`/fresh | use | U001 implemented | `b70f599f1689b2867fc70699c68c3d955d1f18d5` | PASS/no findings | continue to evidence publication | none |
| 2 | `6c9302ab08c7f352e85a199b65bdeb522376171c` | P1=2, P2=1, CI passed | F002,F003,F004 | new families | S001 | S002 | production filesystem safety repairs, not a fixture retry | `iss00334-pr351-s002-p1-repair-2`/fresh | use F002/F003; defer F004 | U002/U003 created | pending | pending | continue bounded implementation | none |
| 3 | `91715eecf306bd0c978da922f87193151764cdcd` | P1=3, P2=1, CI passed | F005,F006,F007,F008 | new families after S006 | S006 | S007 | descriptor-authoritative Candidate/apply publication and exact-old remote CAS | `iss00334-pr351-s007-p1-repair`/fresh | use F005/F006/F007; defer F008 | U004/U005/U006 locally implemented and verified | pending | pending | continue to fresh local review, commit/push, exact-head review and observation | none |
| 4 | local S007 worktree after fresh review | local review P1=3 | F005,F006,F007 | bounded residual closure gaps | S007 | S008 | unprivileged Linux primitive, resume absent/unavailable split, application guard identity test | three fresh ChatGPT sessions/verified Pro | use all three bounded work packets | S008 implemented; full local gates and fresh Spec/Code/QA review PASS | pending | pending | continue to commit/push and exact-head assurance | none |
| 5 | `7cc387201a48f5bd758c25fafa4df8cb20728df6` | fresh ChatGPT P0=0/P1=0; PR conflict detected afterward | F005,F006,F007 | S008 closure and base drift | S008 | S008 plus latest-main integration | no contract change; additive preservation of Issue Planning and explicit-file import ports | `iss00334-s008-final-review`/fresh PASS | use PASS; merge latest main as delivery prerequisite | exact code review PASS; merge commit `99374214ebf943ceb70dc186bf782993784eb481`; post-merge local gates PASS | `7cc387201a48f5bd758c25fafa4df8cb20728df6`, `99374214ebf943ceb70dc186bf782993784eb481` | pending final-head fixed observation | continue to evidence publication and final observation | none |
| 6 | `be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2` | P1=3, P2=2, required CI passed | F009,F010,F011,F012,F013 | new exact-head filesystem race families plus non-blocking assurance observations | S008 | S009 | visible Candidate path attachment proof, repository descriptor authority, per-target atomic preimage compare-and-replace | `iss00334-s009-three-p1`/fresh verified Pro | use F009/F010/F011; defer F012/F013 | U007/U008/U009 implemented; focused, fast, lint, parity and validate PASS | pending | pending | continue to fresh local review, commit/push, exact-head review and observation | none |
| 7 | local S009〜S013 worktree | local P1 findings converged through fresh reviews | F014,F015,F016,F017,F018 | concrete cleanup, write-ahead, resumable rollback, and workspace ownership crash windows | S009 | S010〜S013 | ownership-safe quarantine plus durable mutation/workspace intent for all forward/reverse paths | `iss00334-s010-five-p1`; `iss00334-s011-existing-rollback-workspace`; `iss00334-s012-workspace-preledger-crash`; `iss00334-s013-absent-rollback-intent` / fresh verified Pro | use only confirmed P1 work packets; exclude P2/P3 and redesign | U010〜U014 implemented; S013 integrated gates PASS | pending | pending | continue to fresh local closure review | none |

`iteration_index` is telemetry only; it does not authorize continuation or
stopping. Each row records the evidence-driven semantic decision for that
iteration.

## S010-S012 Local Review Intake

| item_id | source_type | reported_priority | raw_summary | family_id | disposition |
| --- | --- | --- | --- | --- | --- |
| R014 | fresh local review | P1 | Candidate rejection cleanup and absent rollback can delete a replacement entry after an identity check | F014 | fix-now |
| R015 | fresh local review | P1 | staged slot ownership, mutation write-ahead, and rollback progress are not durably coupled to namespace mutation | F015 | fix-now |
| R016 | fresh local review | P1 | existing-preimage reverse rollback can leave an untracked inner workspace after exchange | F016 | fix-now |
| R017 | fresh local review | P1 | forward/reverse workspace creation can precede any durable ownership record | F017 | fix-now |
| R018 | fresh local QA review | P1 | absent rollback alone bypasses the S012 workspace intent before `rollback-prepared` handoff | F018 | fix-now |
| R019 | fresh local code review | P1 | same-UID adversary can replace entries inside private `0700` Candidate/Apply workspaces between final identity check and pathname operation | F019 | no-action |
| R020 | fresh scope-limited code review | P1 | an open FD can write the displaced old inode after atomic replacement and before private cleanup | F019 | no-action |
| R021 | fresh scope-limited code review | P1 | Candidate final path can be replaced after descriptor publication but before ownership capture | F020 | fix-now |
| R022 | fresh scope-limited code review | P1 | canonical target can be atomically replaced after expected FD open but before exchange, leaving transaction bytes canonical | F021 | fix-now |
| R023 | fresh S015 spec review | P1 | accepted repeated-contention fail-closed boundary lacked a direct regression proving bytes/evidence retention and no commit/push | F022 | fix-now |
| R024 | fresh S015 code review | P1 | worktree bytes can change after diff proof and be staged, committed, and pushed without comparing index blobs to operation-authorized bytes | F023 | fix-now |
| R025 | fresh S016 spec review | P1 | real index can change after verified `write-tree` and ordinary `git commit` can create an unauthorized local commit before the post-commit tree check | F024 | fix-now |

| family_id | root_cause_family | invariant | repair_unit | local_status |
| --- | --- | --- | --- | --- |
| F014 | `issue-planning.cleanup-owned-entry-atomicity` | unknown Candidate/decision/companion bytes must never be deleted by check-then-unlink | U010 | local-pass |
| F015 | `issue-planning.apply-durable-mutation-recovery` | mutation intent precedes publication and rollback is idempotent and durably drainable | U011 | local-pass |
| F016 | `issue-planning.apply-existing-rollback-workspace` | reverse exchange workspace remains represented until displaced after bytes are removed and directory cleanup is durable | U012 | local-pass |
| F017 | `issue-planning.apply-workspace-ownership-intent` | workspace name and owned objects become durable evidence before each worktree namespace/write boundary | U013 | local-pass |
| F018 | `issue-planning.apply-absent-rollback-intent` | decision/companion absence rollback reserves and binds its workspace before namespace creation and phase handoff | U014 | local-pass |
| F019 | `issue-planning.private-workspace.same-uid-adversary` | current canonical contract does not define same-UID private-namespace tampering as a security boundary | N/A | not-adopted-out-of-scope |
| F020 | `issue-planning-candidate.prebound-publication-token` | Candidate cleanup authority must be bound before public publication can be concurrently replaced | U015 | local-pass |
| F021 | `issue-planning-apply.actual-displaced-exchange-back` | CAS miss must restore the actual attachment displaced by exchange before reporting target drift | U016 | local-pass |
| F022 | `issue-planning-apply.repeated-exchange-back-contention` | after a second concurrent replacement during compensation, preserve every observed attachment and stop without commit/push when restoration cannot be confirmed | U017 | local-pass |
| F023 | `issue-planning-apply.staged-tree-content-binding` | before commit, all five controlled target entries in the immutable staged tree must equal operation-authorized OIDs or explicit absence | U018 | local-pass |
| F024 | `issue-planning-apply.verified-tree-commit-binding` | any installed local operation commit must consume the already verified tree, have the expected parent/message/path set, and be installed by old-value CAS | U019 | local-pass |

| unit_id | family_ids | allowed_scope | implemented_strategy | validation |
| --- | --- | --- | --- | --- |
| U010 | F014 | Candidate/Apply provider infra and focused tests | descriptor-relative private quarantine with no-replace move and owned-entry deletion only | Candidate native ABI/error tests; decision/companion race tests |
| U011 | F015 | Apply provider infra and focused tests | private workspace, `prepared`/`published`/`rollback-prepared`, exact idempotence, per-entry ledger drain | forward/absent publication crash and rollback interruption tests |
| U012 | F016 | Apply provider infra and focused tests | outer mutation retains reverse workspace/staged identity through all cleanup crash states | reverse exchange pre/post cleanup unit/integration tests |
| U013 | F017 | Apply provider infra and focused tests | singleton `workspace_intent`; reserve before mkdir, bind before child/write, resolve before normal recovery | forward/reverse ordering, boundary classification, ambiguity retention tests |
| U014 | F018 | Apply provider infra and focused tests | reuse singleton intent with purpose `rollback-absent` and staged name `quarantine` | decision/companion pre-handoff crash, boundary classification, ambiguity retention tests |
| U015 | F020 | Candidate provider infra and focused tests | Linux staged-FD token; Darwin private-clone token before no-replace public rename | same-byte distinct-inode post-publication replacement; Linux/Darwin binding tests |
| U016 | F021 | Apply provider infra and focused tests | capture actual displaced attachment and one-shot exchange-back on canonical CAS miss | byte-different/same-byte atomic editor unit tests and archive integration |
| U017 | F022 | Apply integration tests only | inject a second atomic replacement immediately before exchange-back and prove A/B/C bytes, mutation evidence, `recovery_required/restore_mismatch`, and no commit/push | one explicit full-regression characterization PASS |
| U018 | F023 | Apply provider infra and focused unit/integration tests | derive expected OIDs only from immutable operation authority; parse one `git ls-tree -r -z` result for five targets; compare immediately after `write-tree` and before `after_index_stage` | five atomic replacement variants plus index-only poison Red/Green |
| U019 | F024 | Apply provider infra and focused unit/integration tests | run commit hooks against a private index bound to verified tree; use `commit-tree` with signing intent; prove object; install exact checked-out branch ref by fixed old-value CAS | late real-index poison, final-proof race, hook order/mutation/rejection/trailer, signing tests |

### F022 `issue-planning-apply.repeated-exchange-back-contention`

- Related inventory ID: R023
- Reviewer priority: P1
- Orchestrator decision: continuous-latest architectureは不採用のまま、accepted fail-closed boundaryを実証するtest-only修正を採用。
- Evidence: `20260730t212559z-disc-s015-repeated-canonical-contention-boundary.md`
- Concretization: `20260730t213150z-pr-351-s016-two-p1-chatgpt-concretization.md`
- Rationale: 一回の通常並行置換はS015で閉じた。compensation中に第三の置換が発生した場合、実装は最新attachmentをprivate workspaceへ保持し、`recovery_required/restore_mismatch`でcommit／pushせず停止する。継続中multi-writer下のcontinuous-latest guaranteeはlocking／retained storage／retry authorityを必要とし、defect-only review範囲を超える。production behaviorを変えず、既存boundaryを直接実証するintegration regressionだけを追加した。
- Residual risk: repeated contention中はcanonical pathnameが先に捕捉したattachmentを指し、最新attachmentがprivate workspaceへ保持される場合がある。Human recoveryが必要である。
- CI rerun caused by F022 alone: yes。accepted safety boundaryのmissing closure testであったため。

### F023 `issue-planning-apply.staged-tree-content-binding`

- Related inventory ID: R024
- Reviewer priority: P1
- Orchestrator decision: current contract内のunauthorized commit/push defectとしてfix-now。
- Concretization: `20260730t213150z-pr-351-s016-two-p1-chatgpt-concretization.md`
- Red evidence: `after_diff_proof`で5 targetをunauthorized bytesへatomic replacementした5 casesは修正前`ready/adoption_published`まで到達した。index-only poisonは修正前にlocal commitを作成して`recovery_required/post_commit_workspace_changed`となった。
- Green: operation authorityだけからexpected OID／absenceを導出し、`write-tree`直後／`after_index_stage`前にfive target tree entriesをexact比較する。mismatchはcommit前の`planning_commit_failed`として既存rollbackへ接続する。
- Residual risk: Git object-format semanticsは既存repository contractに従う。本修正はpublic schema、status／reason、push CASを変更しない。

### F024 `issue-planning-apply.verified-tree-commit-binding`

- Related inventory ID: R025
- Reviewer priority: P1
- Orchestrator decision: stop-before-commit contract内のlocal commit authority defectとしてfix-now。
- Concretization: `20260730t220930z-pr-351-s017-verified-tree-commit-binding-chatgpt-concretization.md`
- Red evidence: S017追加testsは修正前`3 failed, 3 passed`。late poisonはunauthorized local commit生成後に`restore_mismatch`となり、final-proof後race checkpointは存在せず、private-index mutationもcommit後proofまで到達した。
- Green: private indexでhooksを実行し、verified treeから`commit-tree`でobjectを生成する。tree、single parent、changed paths、operation trailerをref install前に証明し、exact checked-out branch refをexpected HEAD old-value CASで更新する。generic Git validatorの`update-ref`禁止は維持する。
- Hook/signing: pre-install hooksはprivate indexを参照し、mutation／trailer removal／nonzeroをcommit install前に拒否する。`commit.gpgsign=true`は`commit-tree -S`へ反映し、post-commitはCAS install後に既存workspace gateへ接続する。
- Residual risk: commit object生成後／ref install前のunreachable objectはGit object databaseに残り得るがauthorityを持たない。新journal schemaやcleanup scanは導入しない。

### F019 `issue-planning.private-workspace.same-uid-adversary`

- Related inventory IDs: R019, R020
- Reviewer priority: P1
- Orchestrator decision: current P0／P1として不採用、branch mutationなし。
- Evidence: `20260730t202538z-pr-351-s014-private-entry-final-cas-chatgpt-concretization-not-adopted.md`
- Decision: `20260730t202539z-disc-s014-private-same-uid-threat-scope-disposition.md`
- Rationale: canonical Requirement／Designはprivate `0700` namespace内部を能動改変するsame-UID adversaryをsecurity boundaryとして定義していない。提案されたretained storage、same-device eligibility、capacity／purge lifecycleはarchitecture／operation policy追加であり、defect-only reviewの範囲を超える。
- Residual risk: same-UID actorがprivate random namespaceを発見し最終pathname operationへ能動介入するrisk、およびatomic replacement後に旧open FDへ届くwriteが自動保全されないriskは残る。将来要件化する場合は独立threat／concurrency contract Issueで扱う。
- CI rerun caused by F019 alone: no。

S013 integrated validation is recorded in
`20260730t192855z-review-pr-351-s009-s015-local-closure-evidence.md`:
focused `153 passed, 1 skipped`; explicit Apply integration `89 passed`;
ordinary fast `1332 passed, 2188 skipped`; lint, mypy, parity, validate, and
`git diff --check` PASS. Fresh P0/P1-only closure review remains required before
commit/push.

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
