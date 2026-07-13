---
種別: pr-repair-batch
ID: "20260713t061405z-pr-repair-batch"
タイトル: "PR Repair Batch"
状態: "active"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["iss-00313"]
関連: []
authority: "proposed"
derived_from: ["PR #320", "Provider CI run 29226830895", "Provider CI run 29226835532", "ChatGPT consultation iss-00313-pr-repair-consultati"]
reflected_to: []
---

# 20260713t061405z-pr-repair-batch PR Repair Batch

## PR / Observation Metadata

- PR URL: https://github.com/chemitaro/spec-dock/pull/320
- PR number: 320
- Repository: chemitaro/spec-dock
- Base branch: main
- Head branch: iss-00313-remove-pr-merge-preparer-repair-attempt-limits
- Latest pushed head SHA: 4eecde13fa17546085bc1b546d8b38f4814e23fa
- Latest local head SHA: ec0239ef1c61a239be8ccccf2a81dbe288f09242（`origin/main` 7ba72714 統合済み）
- Observation command: `wait_pr_observation.sh --repo chemitaro/spec-dock --pr 320 --head-sha 4eecde13fa17546085bc1b546d8b38f4814e23fa`（timeout 後に同一 trigger boundary で resume）
- Observation final JSON / evidence: GitHub Actions run 29226830895 / 29226835532、Codex review 4682070705
- Observation status: failed
- Trigger comment id: 4954782019
- Trigger created_at: 2026-07-13T05:39:52Z
- Trigger boundary: comment 4954782019 以後、head `4eecde13fa17546085bc1b546d8b38f4814e23fa`
- Resume metadata: 同一 trigger comment id / created_at で resume 済み
- New trigger approved: no
- Observation limitation: 初回は Provider CI 実行中のまま timeout。resume 後に CI failure を authoritative に取得。
- Batch status: refreshed-base-all-local-gates-passed-awaiting-commit

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
| latest_head_sha | `4eecde13fa17546085bc1b546d8b38f4814e23fa` |
| observation_status | failed |
| required_ci_status | failed (`Provider CI` 2 runs) |
| review_status | completed、P2 3件 unresolved |
| p0_count | 0 |
| p1_count | 0 |
| p2_count | 3 |
| p3_count | 0 |
| required_ci_failure_count | 2 runs / 1 blocking family |
| merge_blocker_count | 1 family |
| blocking_family_count | 1 |
| non_blocking_family_count | 3 |
| terminal_non_blocking_only | no |
| branch_mutation_required | yes |
| ci_rerun_expected | yes |
| review_clean | no |
| merge_prepared_candidate | no（修復・再観測後に再判定） |

## Raw Intake Inventory

Add one row per observed review finding, required CI failure, merge blocker, or
observation limitation from the same observation batch. Keep raw reviewer
priority separate from the final severity decision.

| item_id | source_type | source_id | reported_priority | path | line | raw_summary | evidence_type | current_head_sha | family_id | intake_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R001 | ci | run 29226830895 / job 86742583987 | CI | `tests/unit/infra/test_init_update.py` | 5209 | branch-head の checked-in `.meta.json` path set が cutover snapshot と不一致 | failing-test | `4eecde13fa17546085bc1b546d8b38f4814e23fa` | F001 | triaged |
| R002 | ci | run 29226835532 / job 86742598885 | CI | `tests/unit/infra/test_init_update.py` | 5209 | PR merge-ref の checked-in `.meta.json` path set が cutover snapshot と不一致 | failing-test | `4eecde13fa17546085bc1b546d8b38f4814e23fa` | F001 | triaged |
| R003 | ci | run 29226835532 / job 86742598885 | CI | `tests/unit/infra/test_init_update.py` | 5313 | PR merge-ref の runtime issue dependency map が cutover snapshot と不一致 | failing-test | `4eecde13fa17546085bc1b546d8b38f4814e23fa` | F001 | triaged |
| R004 | review | comment 3568328449 | P2 | issue evidence artifacts | 32 | host-local path の redaction follow-up | contract | `4eecde13fa17546085bc1b546d8b38f4814e23fa` | F002 | triaged |
| R005 | review | comment 3568328454 | P2 | `report.md` | 201 | base-range の trailing whitespace と記録済み diff-check evidence の差 | repro | `4eecde13fa17546085bc1b546d8b38f4814e23fa` | F003 | triaged |
| R006 | review | comment 3568328457 | P2 | `github-pr-merge-preparer/SKILL.md` | 268 | prose enum に `not_requested` がない | contract | `4eecde13fa17546085bc1b546d8b38f4814e23fa` | F004 | triaged |

Do not keep example rows as active inventory.

## Concern Family Catalog

Group inventory items by shared root cause. Do not repair comments one-by-one.

| family_id | root_cause_family | family_title | protected_domain | invariant_or_contract | related_items | max_reported_priority | decided_priority | merge_blocking | disposition | repair_unit | family_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F001 | checked-in-dogfooding-cutover-snapshot-drift | branch-head と PR merge-ref で異なる実ツリーに対する3連動 snapshot drift | no | checked-in dogfooding tree と path / per-path depends_on / non-empty issue map の期待値が一致する | R001, R002, R003 | CI | required-ci | yes | fix-now | U001, U002 | implemented |
| F002 | evidence-host-path-redaction | evidence provenance の host-local path | yes | 公開 evidence の provenance hygiene | R004 | P2 | P2 | no | follow-up | N/A | triaged |
| F003 | validation-ledger-base-range | base-range diff-check evidence の精度 | no | report evidence と検証対象 range の一致 | R005 | P2 | P2 | no | follow-up | N/A | triaged |
| F004 | fallback-status-prose-enum | skill prose と template enum の整合 | yes | `fallback_approval_status` の advisory contract | R006 | P2 | P2 | no | follow-up | N/A | triaged |

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

### F001 checked-in-dogfooding-cutover-snapshot-drift

- Related inventory IDs: R001, R002, R003
- Reported priorities: CI
- Decided priority: required-ci
- Merge-blocking: yes
- Protected domain: no
- Contract / invariant: checked-in dogfooding tree と3つの cutover snapshot が一致し、push と PR merge-ref の Provider CI が同じ収束済みツリーで通ること。
- Root cause: branch が `origin/main` より6コミット behind のまま issue 313 を追加し、branch-head と synthetic merge-ref で異なる `.meta.json` tree を検証した。3つの連動 snapshot はどちらの最新 tree にも追従していない。
- Why this is one family: path set、per-path `depends_on`、runtime non-empty issue map は同じ `.meta.json` tree から導出される3観測面であり、merge-ref の追加症状は main 側の依存関係付き Issue で説明できる。
- Validity analysis: 2 run の checkout target、7つの追加 node、4つの non-empty dependency が failure diff と一致するため valid。
- Need-to-fix decision: required CI blocker のため yes。
- Options considered: path tuple だけ追記（reject）、runtime/assertion を緩和（reject）、最新 main 統合後に3 snapshot を原子的同期（use）。
- Recommended disposition: fix-now。
- Repair scope: nonforce merge で最新 `origin/main` を統合し、`tests/unit/infra/test_init_update.py` の3 snapshot 定数だけを実 tree に同期する。
- Out of scope: provider/runtime/observation contract、managed `.meta.json`、P2 指摘箇所の修正。
- Quality gates: failed 2 tests の再現、個別 Green、両順序 Green、checked-in dogfooding family、module、validate/sync、CLI runtime、`make lint`、`uv run pytest`。
- Residual risk: 実 tree からの導出差分が想定7 node / 4 dependency を超える場合は regression を期待値へ吸収する危険があるため停止する。
- Follow-up handling: 修復後も runtime test 単独 failure が残る場合のみ別 family `dogfooding-validate-sync-state-or-order-dependency` として再分類する。

## Root-Cause Family and Coupling Analysis

| family_id | root_cause_family | related_items | recurrence_class | coupling | evidence_ref | analysis_result |
| --- | --- | --- | --- | --- | --- | --- |
| F001 | checked-in-dogfooding-cutover-snapshot-drift | R001, R002, R003 | first-observed | 3 snapshot は同一 `.meta.json` tree に結合 | Provider CI run 29226830895 / 29226835532 | 1 family、base sync 後の原子的同期が必要 |
| F001 | checked-in-dogfooding-cutover-snapshot-drift | R001, R002, R003 | same-family-base-advance | 旧 repair 後に main が Initiative metadata 1件を追加 | origin/main `7ba72714`、refresh consultation | 同じ family。path / per-path map の追加と non-empty map ゼロ差分を再導出する |

When a `root_cause_family` recurs, re-analyze the current evidence, root-cause
hypothesis, coupling, and prior result. Recurrence alone is not a stop reason.

## Integrated Repair Strategy

- strategy_id: S002-refresh-main-7ba72714-single-node-snapshot-rederive
- covered_family_ids: F001
- prior_strategy_id: S001-base-converged-atomic-snapshot-refresh
- strategy_delta: S001 を main `3acdd76c` に対して全 gate 検証した後、main が `7ba72714` へ進み、依存なし Initiative metadata を1件追加した。S002 は既存 repair を保全して `7ba72714` を中間 push なしで統合し、3 snapshot を最終 tree から再導出する。許可する追加 delta は `init-00322/.meta.json` path と空 per-path `depends_on` のみで、non-empty Issue map はゼロ差分を証明する。focused、module、validate/sync、lint、full provider gate を最終 tree で再実行する。
- bounded_scope: base merge、`tests/unit/infra/test_init_update.py` の3定数、この repair batch のみ。
- validation_plan: focused 2 tests、両順序、checked-in dogfooding family、module、validate/sync、CLI runtime、`make lint`、`uv run pytest`。
- rollback_plan: push 前は merge/snapshot repair unit を破棄可能。push 後は force-push せず標準 revert。managed node は削除しない。
- re_observation_plan: repair commit push 後の新 head に対し post-once で Codex review と Actions を再観測する。
- residual_risk: push 前に `origin/main` が進んだ場合は consultation と snapshot evidence を stale として再取得する。

The strategy must be bounded, in scope, supported by current evidence, and
materially different from an ineffective prior strategy. Renaming or repeating
the same strategy is not a strategy delta.

## ChatGPT Consultation Gate

- consultation_required: yes
- consultation_required_reason: required CI failure による repair branch mutation 前の fresh strategy review。
- consultation_status: fresh
- consultation_id: iss-00313-pr-repair-consultati-2
- consulted_at: 2026-07-13T07:18:30Z
- bound_head_sha: local `e3544752` + uncommitted S001 repair、pushed `4eecde13fa17546085bc1b546d8b38f4814e23fa`
- bound_observation_status: failed、S001 local gates passed、base freshness invalidated by `7ba72714`
- bound_family_ids: F001
- bound_strategy_context: origin/main が S001 後に `7ba72714` へ進行。追加は `init-00322.../.meta.json` と canonical docs/rules のみで、metadata に `depends_on` なし。
- input_summary_ref: Raw Intake Inventory / F001 Per-Family Analysis
- recommendation_summary_ref: Orchestrator Disposition / S001
- freshness_invalidators: origin/main の `7ba72714` 以後への進行、head の想定外変更、追加 failure family、単一 node を超える path/dependency delta、merge conflict。
- open_risks: S001 の full pass は旧 base 証拠。S002 最終 tree で lint / full provider suite を再実行する必要がある。
- fallback_approval_status: not_requested
- fallback_invocation_id: N/A
- fallback_approved_by: N/A
- fallback_approved_at: N/A
- fallback_invocation_scope: N/A
- fallback_reason: N/A
- fallback_expires_when: N/A
- fallback_manual_analysis_ref: N/A
- fallback_consumed_at: N/A
- orchestrator_disposition_summary: S001 を旧 base 証拠として保持し、refresh recommendation を採用。`7ba72714` 統合後に3 snapshot を再導出し、path / per-path 空 entry だけを追加、non-empty map ゼロ差分を必須化する。provider/runtime/observation/P2/managed metadata の変更は引き続き却下。

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
| REC-001 | use | push と PR merge-ref の実 tree を収束させない限り同じ静的 snapshot で両 CI を通せない | run 29226830895 / 29226835532、consultation | 最新 main の nonforce merge を追加 | S001-base-converged-atomic-snapshot-refresh | merge conflict 時は human gate |
| REC-002 | use | 3定数は同じ `.meta.json` tree の連動契約で、部分更新は不完全 | F001、consultation | test snapshot 3定数だけを原子的同期 | S001-base-converged-atomic-snapshot-refresh | 想定外 delta は吸収せず停止 |
| REC-003 | reject | provider/runtime/observation は failure 原因でない | local/CI evidence | 実装スコープを拡張しない | S001-base-converged-atomic-snapshot-refresh | なし |
| REC-004 | reject | P2 は明示的 non-blocking で、独立 repair target にしない | review 4682070705 | P2 指摘箇所を変更しない | S001-base-converged-atomic-snapshot-refresh | terminal follow-up として報告 |
| REC-005 | use | main の進行が freshness を失効させ、追加1 node を最終 tree snapshot に含める必要がある | origin/main `7ba72714`、consultation `iss-00313-pr-repair-consultati-2` | S001 repair を保全して最新 main を再統合 | S002-refresh-main-7ba72714-single-node-snapshot-rederive | main 再進行時は再度 stale |
| REC-006 | use | non-empty map 不変は仮定ではなく再導出で証明する必要がある | init-00322 metadata、refresh consultation | 3 projection を再導出、2定数のみ差分許可 | S002-refresh-main-7ba72714-single-node-snapshot-rederive | 想定外 delta なら stop |

Allowed dispositions are `use`, `partial-use`, `reject`, `defer`, and
`human-gate`. Only the orchestrator may turn dispositioned recommendations into
a bounded worker handoff.

## Blocking Repair Queue

Create repair units only for `P0`/`P1` families, required CI failures, or
blocking merge issues. Do not create repair units for `P2`/`P3` findings unless
they are directly and unavoidably covered by the same `P0`/`P1` root-cause fix.

| unit_id | source_batch | family_id | covered_items | decided_priority | merge_blocking | disposition | repair_unit_disc | status | implementation_plan | quality_gate | commit_evidence | re_observation_result | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U001 | 20260713t061405z-pr-repair-batch | F001 | R001, R002, R003 | required-ci | yes | fix-now | N/A（単一 test snapshot repair unit） | implemented | 最新 main の nonforce merge 後、3 snapshot 定数を実 tree に同期 | G001-G008 | merge `e3544752`、repair commit は最終 gate 後 | pending | 想定外 tree delta / merge conflict は stop |
| U002 | 20260713t061405z-pr-repair-batch | F001 | R001, R002, R003 | required-ci | yes | fix-now | N/A（same-family base freshness refresh） | implemented | `7ba72714` merge 後、init-00322 path / empty per-path entry のみ追加し3 projection再導出 | G009-G014 | merge `ec0239ef`、repair commit は最終 gate 後 | pending | main再進行、想定外delta、conflictはstop |

## Non-Blocking Follow-up Register

Use this section only when a blocking repair commit is already being made and
`P2`/`P3` findings can be recorded without causing an additional record-only
push.

If the latest observation has only `P2`/`P3` findings and no blockers, do not
update this file. Put those findings in the terminal merge-prepared report
instead.

| followup_id | family_id | related_items | priority | rationale_for_no_action | residual_risk | suggested_followup_target |
| --- | --- | --- | --- | --- | --- | --- |
| NB001 | F002 | R004 | P2 | blocking family と root cause が異なり、Codex review が branch update 不要と明示 | provenance hygiene debt | 別 issue または次回 evidence authoring maintenance |
| NB002 | F003 | R005 | P2 | snapshot CI blocker と独立し、今回の repair scope 外 | report evidence range の誤認余地 | 別 issue または report quality maintenance |
| NB003 | F004 | R006 | P2 | snapshot CI blocker と独立し、今回の repair scope 外 | prose/template enum の軽微な不整合 | 別 issue または skill contract maintenance |
## Quality Gate Plan

Define family-level gates, not comment-level checks.

| gate_id | family_id | command_or_check | expected_result | covers_items | required_before_push |
| --- | --- | --- | --- | --- | --- |
| G001 | F001 | failed 2 tests を base merge 後・修正前に個別実行 | snapshot mismatch として Red | R001-R003 | yes |
| G002 | F001 | failed 2 tests を修正後に個別実行 | 各 pass | R001-R003 | yes |
| G003 | F001 | failed 2 tests を両順序で実行 | 両順序 pass | R001-R003 | yes |
| G004 | F001 | `pytest test_init_update.py -k checked_in_dogfooding` | pass | R001-R003 | yes |
| G005 | F001 | `pytest tests/unit/infra/test_init_update.py` | pass | R001-R003 | yes |
| G006 | F001 | `spec-dock validate` / `sync` 後の再検証 | valid、意図しない差分なし | R001-R003 | yes |
| G007 | F001 | `uv run pytest tests/cli_runtime` / `make lint` | pass | R001-R003 | yes |
| G008 | F001 | `uv run pytest` | full provider suite pass | R001-R003 | yes |
| G009 | F001 | origin/main freshness / nonforce merge | `7ba72714` を競合なく統合 | R001-R003 | yes |
| G010 | F001 | 3 snapshot 再導出 | init-00322 path + empty entry のみ、non-empty map delta 0 | R001-R003 | yes |
| G011 | F001 | focused 2 tests / checked-in dogfooding family / module | pass | R001-R003 | yes |
| G012 | F001 | validate / sync / post-sync focused | valid、意図しない差分なし、pass | R001-R003 | yes |
| G013 | F001 | `make lint` | pass | R001-R003 | yes |
| G014 | F001 | `uv run pytest` | final tree full provider suite pass | R001-R003 | yes |

### Validation Results

- base integration: `git merge origin/main`、merge commit `e3544752`、競合なし。
- observed tree delta: `iss-00313`、`epic-00312`、`iss-00315`〜`iss-00319` の7 node 追加、削除なし、既存 dependency 変更なし。
- new non-empty dependencies: `iss-00316 -> [iss-00315]`、`iss-00317 -> [iss-00315]`、`iss-00318 -> [iss-00317]`、`iss-00319 -> [iss-00315, iss-00316, iss-00317, iss-00318]` の4件のみ。
- G001 Red: path-set test と runtime issue-dependency-map test が想定した snapshot drift で失敗。
- G002 Green: 個別実行は各 `1 passed`。
- G003 Green: 両順序で各 `2 passed`。
- G004 Green: `45 passed, 501 deselected`。
- G005 Green: `546 passed in 354.54s`。
- Ruff check / format check / `git diff --check`: pass。
- G006 Green: `spec-dock validate` は `nodes=210`、`sync` は active unchanged、sync 後の対象2テストは各 `1 passed`、意図しない tracked 差分なし。
- G007 Green: `uv run pytest tests/cli_runtime` は `1119 passed, 75 skipped, 2 warnings in 1227.52s`。`make lint` は Ruff check / format check（349 files）/ mypy（220 source files）すべて pass。
- G008 Green: `uv run pytest` は `2306 passed, 75 skipped, 2 warnings in 1585.01s`。
- warnings: duplicate ZIP entry 拒否テストが意図的に発生させる `UserWarning` 2件。
- final diff gate: `git diff --check` pass。tracked repair diff は `tests/unit/infra/test_init_update.py` の3 snapshot 定数、29 insertions のみ。テストによる意図しない tracked 差分なし。
- G009 Green: `origin/main` は `7ba72714c2f5e83916e057ed1db3352c955928f0`、通常 merge commit `ec0239ef1c61a239be8ccccf2a81dbe288f09242`、競合なし。再 fetch 後も main は同 SHA で HEAD の祖先。
- G010 Green: S001 比で path 1件と同 path の空 `depends_on` entry 1件のみ追加。removed / existing dependency change / non-empty Issue map delta は0。path / per-path projection は各211件で exact。
- G011 Green: focused 個別は `1 passed in 1.59s` / `1 passed in 6.67s`、同時 `2 passed in 6.17s`、family `45 passed, 501 deselected in 36.62s`、module `546 passed in 354.07s`。
- S002 diff gate: `git diff --check` pass。tracked repair diff は S001 29行 + S002 2行の計31 insertions。
- G012 Green: `spec-dock validate` は `nodes=211`、`sync` は active unchanged、意図しない tracked 差分なし、post-sync focused は `2 passed in 6.58s`。
- G013 Green: `make lint` exit 0。Ruff check / format check（349 files）/ mypy（220 source files）すべて pass。
- G014 Green: `uv run pytest` は `2306 passed, 75 skipped, 2 warnings in 1988.00s`。warnings は duplicate ZIP entry 拒否テスト由来。
- final freshness: 再 fetch 後も `origin/main=7ba72714c2f5e83916e057ed1db3352c955928f0`、`HEAD=ec0239ef1c61a239be8ccccf2a81dbe288f09242`、origin/main は HEAD の ancestor。

## Re-observation Plan

- Latest head before repair: `4eecde13fa17546085bc1b546d8b38f4814e23fa`
- Expected head after repair: pending
- Re-observation command: `wait_pr_observation.sh --repo chemitaro/spec-dock --pr 320 --head-sha <new-head-sha>`
- Trigger mode: post-once
- Resume trigger comment id: N/A（新 head の初回観測）
- Resume trigger created_at: N/A（新 head の初回観測）
- New trigger approved: yes（ユーザーが PR merge-prepared 完了までの workflow を明示依頼）
- Re-observation required because: required CI blocker を修復する新 head を push するため。
- Re-observation skipped because: N/A

## Iteration Ledger

| iteration_index | head_sha | observation_status | family_ids | recurrence_class | prior_strategy_id | proposed_strategy_id | strategy_delta | consultation_id/status | orchestrator_disposition | action_taken | fix_commit | re_observation_result | continuation_decision | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `4eecde13fa17546085bc1b546d8b38f4814e23fa` | failed | F001 | first-observed | pre-push-validation | S001-base-converged-atomic-snapshot-refresh | base tree 収束後に3 snapshot を原子的に再導出し、CI同一 gate まで拡張 | iss-00313-pr-repair-consultati / fresh | use REC-001/002、reject REC-003/004 | main merge、3 snapshot 同期、G001-G008 Green | pending | pending | continue-to-commit-and-reobserve | なし |
| 2 | local `e3544752` / pushed `4eecde13fa` | base freshness invalidated | F001 | same-family-base-advance | S001-base-converged-atomic-snapshot-refresh | S002-refresh-main-7ba72714-single-node-snapshot-rederive | main `7ba72714` の単一 metadata node を最終 tree に統合し3 projectionを再導出 | iss-00313-pr-repair-consultati-2 / fresh | use REC-005/006 | `ec0239ef` merge、2 snapshot entry同期、G009-G014 Green、main fresh | pending | pending | continue-to-commit-and-reobserve | なし |

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
