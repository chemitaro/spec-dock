---
種別: pr-repair-batch
ID: "20260714t154712z-pr-repair-batch"
タイトル: "PR 323 Repair Batch"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-14"
親: ["iss-00319"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260714t154712z-pr-repair-batch PR 323 Repair Batch

## PR / Observation Metadata

- PR URL: https://github.com/chemitaro/spec-dock/pull/323
- PR number: 323
- Repository: chemitaro/spec-dock
- Base branch: main
- Head branch: iss-00319-installed-runtime-dogfood-parity-final-quality-and-mergeable-pr
- Latest head SHA: a57156265e55e87abf857aa673a9a419d717e8c6
- Observation command: fixed-endpoint PR observation workflow
- Observation final JSON / evidence: S100 first observation result
- Observation status: initial timeout; resumed evidence取得後、Codex review complete / Provider CI terminal failure
- Trigger comment id: 4970835673
- Trigger created_at: 2026-07-14T15:17:06Z
- Trigger boundary: このtriggerのresume metadata範囲内
- Resume metadata: available; initial timeoutから同一observationをresume可能
- New trigger approved: no
- Observation limitation: 初回timeout。Resumeによりreview completeとCI terminal failureを取得済みで、repair判断を妨げない
- Batch status: U1 implemented; late unit evidence remediation created after pre-commit spec P1; fresh spec rereview / commit / push / Ubuntu re-observation pending
- Repair unit Artifact: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00312-experimental-local-workbench-and-worktree-handoff/issues/iss-00319-installed-runtime-dogfood-parity-final-quality-and-mergeable-pr/artifacts/20260714t170412z-disc-pr-repair-unit-linux-descriptor-publication.md`
- Late evidence status: Worker handoff originally used equivalent batch F1/U1/S100-R1 content, but the canonical unit Artifact pre-delegation gate was missed. Order compliance is not claimed; remediation enables audit and fresh review before commit.

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
| latest_head_sha | a57156265e55e87abf857aa673a9a419d717e8c6 |
| observation_status | initial timeout resolved by resume evidence; batch triaged |
| required_ci_status | Provider CI run 29344650625 failed; workflow success |
| review_status | Codex review complete; P1 1、P2 3、unresolved threads 4 |
| p0_count | 0 |
| p1_count | 1 |
| p2_count | 3 |
| p3_count | 0 |
| required_ci_failure_count | 1 |
| merge_blocker_count | 2 raw items / 1 root-cause family |
| blocking_family_count | 1 |
| non_blocking_family_count | 4 |
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
| R1 | review | Codex thread 1 | P1 | publisher Linux test surface | not recorded | Linux unlinked temporary-file publication test does not exercise the real Linux descriptor publication path | code-path / contract | a57156265e55e87abf857aa673a9a419d717e8c6 | F1 | triaged |
| R2 | review | Codex thread 2 | P2 | active Workbench reconciliation surface | not recorded | Active Workbench symlink reconciliation can retain stale state | code-path / contract | a57156265e55e87abf857aa673a9a419d717e8c6 | F2 | triaged |
| R3 | review | Codex thread 3 | P2 | staged Artifact publication surface | not recorded | Staged Artifact replacement race remains possible | code-path / contract | a57156265e55e87abf857aa673a9a419d717e8c6 | F3 | triaged |
| R4 | review | Codex thread 4 | P2 | time-sensitive collision test | not recorded | Wall-clock-dependent test can flake | failing-test / contract | a57156265e55e87abf857aa673a9a419d717e8c6 | F4 | triaged |
| R5 | ci | Provider CI run 29344650625 | CI | artifact publisher tests | not recorded | Normal Linux publication returned `publication_unsupported` for all 25 cases; 25 failed / 2573 passed / 75 skipped / 2 warnings | failing-test / repro | a57156265e55e87abf857aa673a9a419d717e8c6 | F1 | triaged |
| R6 | limitation | trigger 4970835673 | unknown | S100 first observation result | not applicable | Initial observation timed out, but resume metadata was available and later yielded complete review plus terminal CI failure | observation | a57156265e55e87abf857aa673a9a419d717e8c6 | F5 | triaged |

Do not keep example rows as active inventory.

## Concern Family Catalog

Group inventory items by shared root cause. Do not repair comments one-by-one.

| family_id | root_cause_family | family_title | protected_domain | invariant_or_contract | related_items | max_reported_priority | decided_priority | merge_blocking | disposition | repair_unit | family_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | artifact_publication.linux_descriptor_link | Linux descriptor publication fails across procfs | yes | Verified staged bytes must publish atomically without overwrite on supported Linux | R1、R5 | P1 / CI | P1 | yes | fix-now | U1 | implemented; late unit evidence created; fresh spec rereview / commit / push / re-observation pending |
| F2 | workbench.active_symlink_reconciliation | Active Workbench symlink reconciliation | no | Active projection should not retain stale Workbench symlink state | R2 | P2 | P2 | no | follow-up | N/A | triaged |
| F3 | artifact_publication.staged_replacement_race | Staged Artifact replacement race | no | Publication must remain bound to verified staged content | R3 | P2 | P2 | no | follow-up | N/A | triaged |
| F4 | artifact_collision.wall_clock_flake | Wall-clock-dependent collision test | no | Collision tests should be deterministic | R4 | P2 | P2 | no | follow-up | N/A | triaged |
| F5 | pr_observation.initial_timeout | Resumable observation timeout | no | Observation limitation must preserve resume boundary and terminal evidence | R6 | unknown | platform | no | no-action | N/A | triaged |

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

### F1 artifact_publication.linux_descriptor_link

- Related inventory IDs: R1、R5
- Reported priorities: P1、CI
- Decided priority: P1
- Merge-blocking: yes
- Protected domain: Linux Artifact publication
- Contract / invariant: Verified staged bytesを、destination no-overwriteとerror mappingを保ってatomic publishする。
- Root cause: `os.link('/proc/self/fd/<fd>', absolute destination, follow_symlinks=True)`がplain linkを選び、procfsを跨ぐため`publication_unsupported`になると強く推定する。
- Why this is one family: R1のtest gapとR5の25 Linux failuresは同じdescriptor publication pathを指す。
- Validity analysis: Reviewと通常Linux CI failureが相互補強し、valid blocking family。
- Need-to-fix decision: yes
- Options considered: Test-only correction、copy fallback、destination parent `dirfd`を使う`linkat` path。
- Recommended disposition: fix-now。Fresh consultationの`dst_dir_fd`案を採用する。
- Repair scope: Provider publisher、dogfood mirror、publisher testのみ。
- Out of scope: F2〜F4、migration、API拡張、fallback copy。
- Quality gates: Focused publisher、Artifact import regression、`make lint`、full pytest、parity、fresh Ubuntu CI/re-review。
- Residual risk: Python 3.10 local validationはenvironment availabilityに依存するため、Ubuntu Provider CIをauthoritativeとする。
- Follow-up handling: U1で実装し、同一PRをre-observeする。

### F2 workbench.active_symlink_reconciliation

- Related inventory IDs: R2
- Reported priorities: P2
- Decided priority: P2
- Merge-blocking: no
- Protected domain: Active Workbench projection
- Contract / invariant: Active symlink stateのreconciliation。
- Root cause: Blocking Linux publisher familyとは独立したstale projection concern。
- Why this is one family: R2単独の責務境界。
- Validity analysis: Valid follow-up候補だがcurrent blocking repairと非結合。
- Need-to-fix decision: follow-up
- Options considered: Current branch repair、別Issue、defer。
- Recommended disposition: defer
- Repair scope: none in this batch
- Out of scope: Current branch mutation
- Quality gates: Follow-up planning時に定義
- Residual risk: P2 unresolved thread
- Follow-up handling: Final merge-prepared reportで明示し、必要なら別Issue化する。

### F3 artifact_publication.staged_replacement_race

- Related inventory IDs: R3
- Reported priorities: P2
- Decided priority: P2
- Merge-blocking: no
- Protected domain: Staged Artifact identity
- Contract / invariant: Verified stageとpublication sourceのidentity維持。
- Root cause: F1のLinux link mechanismとは別のadversarial replacement concern。
- Why this is one family: R3単独のrace boundary。
- Validity analysis: Valid follow-up候補。U1のtest correctionはunlinkではなくsibling renameを使うが、product race修復までは拡張しない。
- Need-to-fix decision: follow-up
- Options considered: U1へ併合、別Issue、defer。
- Recommended disposition: defer
- Repair scope: none in this batch
- Out of scope: Product race semantics変更
- Quality gates: Follow-up planning時に定義
- Residual risk: P2 unresolved thread
- Follow-up handling: Final merge-prepared reportで明示し、必要なら別Issue化する。

### F4 artifact_collision.wall_clock_flake

- Related inventory IDs: R4
- Reported priorities: P2
- Decided priority: P2
- Merge-blocking: no
- Protected domain: Deterministic collision testing
- Contract / invariant: Test結果がwall clock timingに依存しない。
- Root cause: F1と独立したtest determinism concern。
- Why this is one family: R4単独のtest concern。
- Validity analysis: Valid follow-up候補だがrequired CI failureのroot causeではない。
- Need-to-fix decision: follow-up
- Options considered: Current branch修復、別Issue、defer。
- Recommended disposition: defer
- Repair scope: none in this batch
- Out of scope: Current branch mutation
- Quality gates: Follow-up planning時に定義
- Residual risk: P2 unresolved thread
- Follow-up handling: Final merge-prepared reportで明示し、必要なら別Issue化する。

### F5 pr_observation.initial_timeout

- Related inventory IDs: R6
- Reported priorities: unknown
- Decided priority: platform
- Merge-blocking: no
- Protected domain: Observation continuity
- Contract / invariant: Trigger boundaryとresume metadataを保持し、latest-head terminal evidenceを取得する。
- Root cause: Initial observation duration limit。
- Why this is one family: R6単独のobservation limitation。
- Validity analysis: Resume metadataがあり、review completeとCI terminal failureを後から取得済み。
- Need-to-fix decision: no
- Options considered: Resume、新規trigger、人間gate。
- Recommended disposition: no-action。Terminal evidenceによりresolved/superseded。
- Repair scope: none
- Out of scope: Observation tooling変更
- Quality gates: Resume evidenceとtrigger boundary記録
- Residual risk: none for repair decision
- Follow-up handling: Re-observationでもresume metadataを保持する。

## Root-Cause Family and Coupling Analysis

| family_id | root_cause_family | related_items | recurrence_class | coupling | evidence_ref | analysis_result |
| --- | --- | --- | --- | --- | --- | --- |
| F1 | artifact_publication.linux_descriptor_link | R1、R5 | first observed | Provider publisher、dogfood mirror、Linux testsが直接結合 | S100 first observation result / Provider CI run 29344650625 | One blocking repair family。U1を作成 |
| F2 | workbench.active_symlink_reconciliation | R2 | first observed | F1と非結合 | S100 first observation result | P2 follow-up、branch mutationなし |
| F3 | artifact_publication.staged_replacement_race | R3 | first observed | U1 test fixture correctionと隣接するがproduct fixは非結合 | S100 first observation result | P2 follow-up、branch mutationなし |
| F4 | artifact_collision.wall_clock_flake | R4 | first observed | F1と非結合 | S100 first observation result | P2 follow-up、branch mutationなし |
| F5 | pr_observation.initial_timeout | R6 | resolved limitation | Repair codeと非結合 | Trigger 4970835673 resume metadata | Terminal evidence取得によりresolved |

When a `root_cause_family` recurs, re-analyze the current evidence, root-cause
hypothesis, coupling, and prior result. Recurrence alone is not a stop reason.

## Integrated Repair Strategy

- strategy_id: S100-R1
- covered_family_ids: F1
- prior_strategy_id: initial test-only recommendation
- strategy_delta: Normal Linux 25 failuresを踏まえ、test-onlyからprovider publication mechanismのbounded repairへ変更する。
- bounded_scope: Provider publisher + dogfood mirror + publisher testのみ。
- validation_plan: Focused publisher、Artifact import regression、`make lint`、full pytest、provider/dogfood parity、fresh Ubuntu Provider CI、fresh Codex re-review。
- rollback_plan: U1のpublisher/mirror/test差分だけをrevertし、既存unsupported mappingへ戻す。
- re_observation_plan: U1 commit/push後、PR #323をlatest headへbindしてresume/post-once観測する。
- residual_risk: F2〜F4はP2 follow-up。Python 3.10 local availability不足時はUbuntu Provider CIをauthoritativeにする。

The strategy must be bounded, in scope, supported by current evidence, and
materially different from an ineffective prior strategy. Renaming or repeating
the same strategy is not a strategy delta.

## ChatGPT Consultation Gate

- consultation_required: yes
- consultation_required_reason: P1 review findingとrequired Ubuntu CI failureが同一Linux publication familyを形成し、platform-specific repair判断が必要。
- consultation_status: fresh
- consultation_id: pr323-linux-publicatio-repair-consultati-2
- consulted_at: 2026-07-14 S100 repair triage
- bound_head_sha: a57156265e55e87abf857aa673a9a419d717e8c6
- bound_observation_status: Codex review complete / Provider CI terminal failure
- bound_family_ids: F1、F2、F3、F4
- bound_strategy_context: Initial GPT-5.6 Pro test-only recommendation was stale after normal Linux 25 failures; refresh evaluates bounded S100-R1 repair.
- input_summary_ref: S100 first observation result、Provider CI run 29344650625、Concern Family Catalog
- recommendation_summary_ref: Use destination parent dirfd and `os.link(proc_fd_path, destination.name, dst_dir_fd=dirfd, follow_symlinks=True)` to force CPython `linkat` + `AT_SYMLINK_FOLLOW`; preserve macOS/error mapping/no-overwrite; correct adversarial test with verified-stage sibling rename; defer F2〜F4.
- freshness_invalidators: Head change、new Linux failure shape、different root-cause family、required behavior change。
- open_risks: Python 3.10 local availability、fresh Ubuntu CI confirmation、F2〜F4 deferred P2 concerns。
- fallback_approval_status: not_requested
- fallback_invocation_id: N/A
- fallback_approved_by: N/A
- fallback_approved_at: N/A
- fallback_invocation_scope: N/A
- fallback_reason: N/A; consultation succeeded
- fallback_expires_when: N/A
- fallback_manual_analysis_ref: N/A
- fallback_consumed_at: N/A
- orchestrator_disposition_summary: partial-use/use。Linux dirfd publication repairとtest fixture correctionを採用し、F2〜F4はdeferする。

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
| REC-1 | use | Normal Linux publication failureへ直接対応し、macOS/error mapping/no-overwriteを維持できる | Fresh consultation / F1 analysis / Provider CI run 29344650625 | Linux helperまたはinline最小実装 + dogfood mirror + publisher test | S100-R1 | Fresh Ubuntu CIで確認必要 |
| REC-2 | partial-use | Adversarial replacement fixtureはverified stageをsiblingへrenameして実在replacementを置く。Product race修復へは拡張しない | Fresh consultation / R1 / R3 | Publisher test fixture correction only | S100-R1 | F3はP2 follow-up |
| REC-3 | defer | F2〜F4はF1 blocking root causeと非結合で、追加branch mutationを正当化しない | F2〜F4 family analysis | Current branch changeなし | N/A | P2 unresolved threadsをterminal reportへ記録 |

Allowed dispositions are `use`, `partial-use`, `reject`, `defer`, and
`human-gate`. Only the orchestrator may turn dispositioned recommendations into
a bounded worker handoff.

## Blocking Repair Queue

Create repair units only for `P0`/`P1` families, required CI failures, or
blocking merge issues. Do not create repair units for `P2`/`P3` findings unless
they are directly and unavoidably covered by the same `P0`/`P1` root-cause fix.

| unit_id | source_batch | family_id | covered_items | decided_priority | merge_blocking | disposition | repair_unit_disc | status | implementation_plan | quality_gate | commit_evidence | re_observation_result | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U1 | 20260714t154712z-pr-repair-batch | F1 | R1、R5 | P1 | yes | fix-now | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00312-experimental-local-workbench-and-worktree-handoff/issues/iss-00319-installed-runtime-dogfood-parity-final-quality-and-mergeable-pr/artifacts/20260714t170412z-disc-pr-repair-unit-linux-descriptor-publication.md` | implemented; late evidence remediation complete / fresh spec rereview pending | Destination parent dirfdを開き、proc fd sourceからbasename destinationへ`os.link(..., dst_dir_fd=dirfd, follow_symlinks=True)`。macOS/error mapping/no-overwrite維持。Testはverified stage sibling renameでreplacement設置 | Local gates passed。Fresh spec rereview後、fresh Ubuntu Provider CI/latest-head re-review pending | pending | pending | F2〜F4 deferred。Canonical unit Artifact pre-delegation gate omissionをlate evidenceで修復し、order complianceは主張しない |

## Implementation Result

- Bounded changed files: 3。
  - Provider publisher: Linux destination parent `dst_dir_fd` / `linkat` call shape。
  - Dogfood mirror: provider変更のexact mirror。
  - Publisher test: path replacement fixtureをverified stageのsibling renameへ修正。
- Scope boundary: F1 / U1だけを変更。F2〜F4はdeferを維持。
- Focused publisher tests: 41 passed。
- Artifact import full focused tests: 38 passed。
- Code reviewer combined focused tests: 65 passed。
- Linux call-shape mock: 1 passed。
- `make lint`: passed。Ruff、375-file format check、mypy 246-source-filesがpass。
- Full pytest: 2598 passed / 75 skipped / 2 warnings in 1597.89s。
- `git diff --check`: passed。
- Provider/dogfood parity `cmp`: passed。
- Fresh code review: passed、P0〜P3 0。
- Fresh QA review: conditional pass、P0〜P3 0。Remaining conditionはcommit/push、fresh Ubuntu Provider CI、latest-head re-reviewのみ。
- Workflow P1 remediation: Unit Artifactをworker implementation後にlate evidenceとして作成した。Equivalent batch F1/U1/S100-R1 contentはhandoffに使われたが、canonical pre-delegation gate準拠は主張しない。Fresh spec rereview pending。
- Commit evidence: pending。
- Re-observation result: pending。

## Non-Blocking Follow-up Register

Use this section only when a blocking repair commit is already being made and
`P2`/`P3` findings can be recorded without causing an additional record-only
push.

If the latest observation has only `P2`/`P3` findings and no blockers, do not
update this file. Put those findings in the terminal merge-prepared report
instead.

| followup_id | family_id | related_items | priority | rationale_for_no_action | residual_risk | suggested_followup_target |
| --- | --- | --- | --- | --- | --- | --- |
| NB1 | F2 | R2 | P2 | F1と非結合でcurrent blocking repairに含めない | Active symlink stale reconciliation concern | Follow-up Issue candidate |
| NB2 | F3 | R3 | P2 | U1 test fixture correctionを越えるproduct race修復はscope expansion | Staged replacement race concern | Follow-up Issue candidate |
| NB3 | F4 | R4 | P2 | Required CI failureのroot causeではなく追加pushを正当化しない | Wall-clock flake concern | Follow-up Issue candidate |

## Quality Gate Plan

Define family-level gates, not comment-level checks.

| gate_id | family_id | command_or_check | expected_result | covers_items | required_before_push |
| --- | --- | --- | --- | --- | --- |
| G1 | F1 | Focused publisher tests | passed: publisher 41、code-reviewer combined focused 65、Linux call-shape mock 1 | R1、R5 | yes |
| G2 | F1 | Artifact import regression tests | passed: Artifact import full focused 38 | R1、R5 | yes |
| G3 | F1 | `make lint` | passed: Ruff、375-file format、mypy 246 source files | R1、R5 | yes |
| G4 | F1 | Full pytest | passed: 2598 / skipped 75 / warnings 2 in 1597.89s | R1、R5 | yes |
| G5 | F1 | Provider/dogfood parity + `git diff --check` | passed: exact `cmp`、diff check | R1、R5 | yes |
| G6 | F1 | Fresh Ubuntu Provider CI + Codex re-review | Required CI succeeds and no unresolved P0/P1 remains | R1、R5 | after push |

## Re-observation Plan

- Latest head before repair: a57156265e55e87abf857aa673a9a419d717e8c6
- Expected head after repair: U1 implementation/test/report commit SHA
- Re-observation command: fixed-endpoint PR observation workflow for PR #323 latest pushed head
- Trigger mode: resume when valid for the recorded boundary; otherwise workflow-approved post-once
- Resume trigger comment id: 4970835673
- Resume trigger created_at: 2026-07-14T15:17:06Z
- New trigger approved: no
- Re-observation required because: R1 P1 and R5 required CI failure require latest-head Ubuntu CI and Codex re-review evidence.
- Re-observation skipped because: N/A

## Iteration Ledger

| iteration_index | head_sha | observation_status | family_ids | recurrence_class | prior_strategy_id | proposed_strategy_id | strategy_delta | consultation_id/status | orchestrator_disposition | action_taken | fix_commit | re_observation_result | continuation_decision | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | a57156265e55e87abf857aa673a9a419d717e8c6 | Initial timeout; resumed review complete / Provider CI terminal failure | F1〜F5 | first observed | initial test-only recommendation | S100-R1 | Test-onlyからLinux dirfd publication mechanism + adversarial fixture correctionへ変更 | pr323-linux-publicatio-repair-consultati-2 / fresh | F1 use、fixture partial-use、F2〜F4 defer、F5 no-action | U1 implemented; local gates pass; fresh code review pass; QA conditional pass; pre-commit spec P1でmissing canonical unit Artifactを検出しlate evidence remediationを作成 | pending | pending | Fresh spec rereview後にcommit/pushし、fresh Ubuntu Provider CIとlatest-head re-reviewへ進む | Pre-delegation order complianceは回復不能だが、audit/review evidenceをcommit前に補完。Fresh rereview pending |

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
