---
種別: 実装報告書（Issue）
ID: "iss-00241"
タイトル: "Resolve Epic Traceability And Review Policy Gate Gaps"
関連GitHub: ["#241"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-27"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00241 Resolve Epic Traceability And Review Policy Gate Gaps — 実装報告

## 仕様解釈・判断台帳

| ID | Status | Type | Raised By | Gap | Options Considered | Decision | Rationale | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | user / orchestrator | `iss-00239` が scaffold のまま残り Epic close readiness を block している | A: `iss-00241` に吸収; B: 独立 Issue として残す; C: defer | `iss-00241` に吸収し、`iss-00239` は superseded / closed として扱う | ユーザーが一つの corrective Issue で複数の取りこぼしを解決する方針を明示した | promoted_to_requirement / promoted_to_design / promoted_to_plan | `discussions/20260627t031736z-interview-corrective-issue-scope-confirmation.md` | `iss-00239` supersession evidence を S04 で記録する |
| D-002 | resolved | interpretation | spec-reviewer / audit | trusted base policy failure が fallback success として実装・テスト固定されている | A: fallback 維持; B: head policy fallback; C: POST なし human gate | POST なし human gate | Accepted ADR と Epic requirement が fail-closed を要求する | promoted_to_requirement / promoted_to_design / promoted_to_plan | Epic audit / spec reviewer report | S01 で実装 |
| D-003 | resolved | interpretation | issue 238 / audit | `workflow next` と generated projection authority の stale wording が Epic 正本に残る | A: `workflow next` alias 追加; B: docs を `guidance <target>` に更新 | `guidance <target>` stdoutを agent handoff authority とし、projection は human/debug-only | Current runtime / skills / tests は guidance model へ移行済み | promoted_to_requirement / promoted_to_design / promoted_to_plan | `iss-00238` evidence, Epic audit | S90 で反映 |
| D-004 | resolved | implementation-boundary | dev-coder / orchestrator / code-reviewer | assurance compose の既存 stale source binding gate が design / plan direct edit を composer の no-overwrite conflict として観測する前に止めていた | A: 既存どおり stale_source_binding のみ; B: design / plan direct edit は composer conflict を優先し、conflict がなければ stale_source_binding を維持 | B を採用 | S03 は destructive overwrite 防止を compose 境界で観測可能にする必要がある。requirement stale protection は維持され、code-reviewer が S03 slice 内で必要かつ安全と判定した | applied_to_s03 | S03 code-reviewer pass, `tests/cli_runtime/test_assurance_compose.py` | issue-local decision; no broader contract change |
| D-005 | resolved | implementation-boundary | S99 dev-coder / orchestrator | issue design/plan template が awaiting-compose placeholder になったことで draft discussion docs が marker を継承した | A: draft docs も placeholder 化する; B: draft discussion docs は post-render で marker を除去し draft contract に正規化する | B を採用 | discussion draft は canonical planning artifact ではなく、assurance compose の実行対象でもないため marker を持つと誤誘導になる | applied_to_s99 | `tests/cli_runtime/test_new.py` draft artifact regression, manual temp repo flow | none |
| D-006 | resolved | implementation-boundary | S99 dev-coder / spec-reviewer | trigger permission-denied path が human gate に正規化される際、permission repair action が `human_gate` に潰れていた | A: top-level action は常に `human_gate`; B: permission signal がある場合は `fix_github_token_permissions` を保持する | B を採用 | human gate のままでも operator が直すべき capability が明確になる。trusted base policy fail-closed/no-comment contract は維持される | applied_to_s99 | `test_issue_180_s02_wait_maps_trigger_comment_permission_denied_to_human_gate`, final code review | none |
| D-007 | resolved | dogfooding-parity | S99 dev-coder / orchestrator | provider runtime/template/agent-tooling を変更したが dogfooding mirror が stale だと focused suite と実運用検証が red になる | A: provider のみ更新; B: provider source of truth に合わせて checked-in dogfooding mirror も同期する | B を採用 | repo の dogfooding rules は provider-side authority と local consumer workspace の parity inspection を要求する | applied_to_s99 | provider/mirror parity diff checks, full focused suite `578 passed, 5 skipped` | none |
| D-008 | resolved | follow-up-boundary | user / orchestrator / oracle | `guidance issue-execution` の dynamic step selection は複雑で、plan-centric model へ簡素化するべきだが、`iss-00241` に本体実装を混ぜると scope が肥大化する | A: `iss-00241` で全面実装; B: `iss-00241` は方針記録と最小安定化に留め、follow-up Issue へ移管 | B を採用 | 本件は issue planning / issue execution / runtime guidance / tests を横断する workflow architecture 変更であり、現在の corrective PR の mergeability を守るには別 Issue が適切 | transferred_to_follow_up | `discussions/20260627t121356z-disc-plan-centric-execution-model-analysis.md`, `discussions/20260627t122855z-disc-plan-pattern-taxonomy-and-guidance-simplification.md` | `iss-00244` |

## 証跡採用台帳

| ID | adoption_status | source | target | rationale | evidence | next_action |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | research | `requirement.md`, `design.md`, `plan.md` | Epic audit の P0/P1/P2 gap を corrective Issue scope と AC/EC へ採用した | `../../discussions/20260627t025746z-research-epic-quality-gate-traceability-audit.md` | spec-reviewer |
| EAL-002 | adopted | spec-reviewer | `requirement.md`, `design.md`, `plan.md` | Spec reviewer が audit findings を false positive ではないと判定したため、blocking remediation scope として採用した | `../../discussions/20260627t030737z-disc-spec-reviewer-epic-traceability-gate.md` | spec-reviewer |
| EAL-003 | adopted | ADR | `requirement.md`, `design.md`, `plan.md` | Trusted base SHA policy failure は human gate という accepted decision を AC-001 / S01 へ反映した | `../../discussions/20260623t074444z-adr-trusted-base-sha-github-review-policy.md` | S01 |
| EAL-004 | adopted | ADR / issue evidence | `requirement.md`, `design.md`, `plan.md` | Fixed skill kernel の current operational surface を `guidance <target>` stdout authority として反映した | `../../discussions/20260623t074441z-adr-fixed-skill-kernel-compiled-runbook-authority.md`, `../iss-00238-stdout-runbook-handoff-instead-of-generated-workflow-files/discussions/20260624t083737z-research-stdout-runbook-handoff-current-state.md`, `../iss-00238-stdout-runbook-handoff-instead-of-generated-workflow-files/report.md` | S90 |
| EAL-005 | adopted | research | `requirement.md`, `design.md`, `plan.md` | `iss-00239` の placeholder scaffold 推奨案を、吸収 scope として AC-006 / AC-007 / S03 へ採用した | `../iss-00239-compose-issue-planning-templates-after-assurance-classification/discussions/20260624t113051z-research-assurance-compose-scaffold-analysis.md` | S03 |
| EAL-006 | adopted | interview | `requirement.md`, `design.md`, `plan.md`, Epic report | `iss-00239` を `iss-00241` に吸収するユーザー判断を採用した | `discussions/20260627t031736z-interview-corrective-issue-scope-confirmation.md` | S04 |
| EAL-007 | adopted | user cross-check / audit refinement | `requirement.md`, `design.md`, `plan.md` | QG-006〜QG-008 は AC-010 に包括されるだけでなく、S90/S99 の必須 traceability ledger 項目として明示する必要がある | current planning chat cross-check, Epic audit QG-006〜QG-008 | S90/S99 |
| EAL-008 | transferred | oracle / discussion | `iss-00244` research handoff | plan-centric execution model、planning-time review pattern taxonomy、`guidance issue-execution` simplification は `iss-00241` の要件・設計・計画へ追加せず、follow-up Issue の調査材料として移管する | `discussions/20260627t112517z-research-guidance-step-selection-regression-analysis.md`, `discussions/20260627t114637z-disc-guidance-execution-model-stability-analysis.md`, `discussions/20260627t121356z-disc-plan-centric-execution-model-analysis.md`, `discussions/20260627t122855z-disc-plan-pattern-taxonomy-and-guidance-simplification.md` | `iss-00244` |

## 目的整合台帳

| 対象 | 主要目的の証跡 | 副次要件の証跡 | 逆転リスク | レビュアー判定 |
|---|---|---|---|---|
| OAL-001 | Epic 00224 の取りこぼした品質ゲート問題を単一 corrective Issue で解決する | PR review policy、skill wording、guidance docs、template lifecycle、Epic report reconciliation | low: scope は audit / spec-reviewer findings と user-approved absorption に限定 | passed: fresh comprehensive `spec-reviewer` coverage review returned no findings, confidence=0.91 |

## 仕様 authoring ゲート

| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |
|---|---|---|---|---|---|---|
| requirement | Epic requirement/design/plan/report、accepted ADR、Epic audit、spec-reviewer report、Issue 239 research、Issue 241 interview、current runtime / skill / tests search | `iss-00239` の扱いは user-approved: `iss-00241` に吸収 | EAL-001〜007 を採用して `requirement.md` を具体化 | passed: post-amendment `spec-reviewer` final re-review returned no findings, review_status=pass, confidence=0.92 | no | promoted to implementation-ready planning package with design/plan |
| design | reviewer-pass済み requirement package、現行 provider/dogfooding skill/script、runtime guidance、artifact composer/new issue tests、Issue 239 research、QG-006〜QG-008 refinement | 追加質問なし | 同じ証跡を `design.md` へ反映し、Epic Traceability Gate Detail を固定 | passed: post-amendment `spec-reviewer` final re-review returned no findings, review_status=pass, confidence=0.92 | no | promoted to implementation-ready planning package with plan |
| plan | reviewer-pass済み requirement/design package、workflow_spec_authoring、phase_plan_issue、authoring/issue-plan、workflow_issue、QG-006〜QG-008 refinement | 追加質問なし | S01〜S04/S90/S99 の executable step contract と closure index を作成し、`tc-010`〜`tc-012` を追加 | passed: post-amendment `spec-reviewer` final re-review returned no findings, review_status=pass, confidence=0.92 | no | ready for issue execution handoff |

## 委任ドラフト証跡
- 委任 authoring の使用:
  - not used
- 未使用の場合:
  - 今回は main orchestrator が Epic audit、spec-reviewer report、ADR、Issue 239 research、user interview を統合して canonical docs を作成した。Delegated draft を promotion evidence として使っていない。

| ロール | 範囲 | ドラフトパス | 参照元 | 予定反映先 | 採用状態 | 反映先 | 差分ガード結果 | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果 | 昇格判断 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 該当なし | iss-00241 | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pending | delegated draft promotion なし |

## 実装サマリー
- S01〜S04 は実装 / 証跡記録済み。
- S90 は Epic requirement/design/plan/report と本 report の docs-only reconciliation として実施済み。
- S90 reviewer gate と commit gate はまだ pending。
- `guidance issue-execution` を plan-centric preflight validator へ簡素化する本体実装は `iss-00241` では行わず、follow-up `iss-00244` へ移管した。

## 実装記録

### セッションログ（2026-06-27）

#### 対象
- Step: planning / requirement-design-plan authoring
- AC/EC: AC-001〜AC-010, EC-001〜EC-005

#### 実施内容
- `iss-00241` を active issue として start した。
- `./spec-dock/scripts/spec-dock guidance issue-planning` により `state=requirement-capture` / `next_action=requirement-capture-required` を確認した。
- Epic audit、spec-reviewer report、accepted ADR、Issue 239 research、Issue 241 interview を読み、`requirement.md` / `design.md` / `plan.md` を具体化した。
- Fresh `spec-reviewer` attempt 1 は `review_status=fail`。S02/S04/S90 delegation contract 不足、S01 failure-path seeds 不足、`iss-00238` evidence path placeholder、authoring gate evidence pending が指摘された。
- 指摘を受け、plan の S01 seeds、S02/S04/S90 delegation contract、report の evidence path と authoring gate記録を修正した。
- Fresh `spec-reviewer` attempt 2 は `review_status=fail`。EAL relative path の誤りが指摘されたため、Epic discussion references を `../../discussions/...` に修正し、shell で file existence を確認した。
- Fresh `spec-reviewer` attempt 3 は `review_status=fail`。EC-004 marker-preserved direct-edit の S03 coverage が不足していたため、closure `tc-009` と `tc-s03-004` negative test seed を追加した。
- Fresh `spec-reviewer` final re-review は findings なし、`review_status=pass`、confidence 0.88。これは QG-006〜QG-008 明示化前の planning package に対する verdict。
- 実装開始前の追加再確認で、QG-006 step closure audit、QG-007 context routing evidence audit、QG-008 Auto-Lite readiness audit が AC-010 に包括されている一方、S90/S99 の具体チェックとしては抽象的であると確認した。
- 指摘を受け、AC-010 の期待結果、design の Epic Traceability Gate Detail、plan の closure `tc-010` / `tc-011` / `tc-012` と S90/S99 必須検証を追加した。
- Fresh `spec-reviewer` post-amendment review は `review_status=fail`。missing metrics が通常 follow-up で閉じられるように読める design wording と、post-amendment reviewer verdict の記録不足が指摘されたため修正した。
- Fresh `spec-reviewer` post-amendment re-review 2 は `review_status=fail`。authoring gate 表に pre-amendment pass を現行 readiness と誤読できる記録が残っていたため、current review pending として修正した。
- Fresh `spec-reviewer` post-amendment re-review 3 は `review_status=fail`。メモ欄に pre-amendment pass に基づく stale implementation-ready claim が残っていたため、post-amendment pass まで blocked として修正した。
- Fresh `spec-reviewer` post-amendment final re-review は findings なし、`review_status=pass`、confidence 0.92。
- 手戻り防止のため、別の fresh `spec-reviewer` に Epic audit / Epic spec-reviewer report と現行 `iss-00241` requirement / design / plan / report の網羅対応を独立レビューさせた。findings なし、`review_status=pass`、confidence 0.91。

#### 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock issue start iss-00241 --force
# spec-dock: ok (issue start) target=iss-00241 ...

./spec-dock/scripts/spec-dock guidance issue-planning
# state: requirement-capture
# next_action: requirement-capture-required
# active_issue: iss-00241
```

#### メモ
- `--force` は unfinished active issue guard bypass として使われた。依存未解決を bypass したものではない。
- Requirement / design / plan / report は QG-006〜QG-008 明示化後の post-amendment `spec-reviewer` pass を受け、planning package として implementation handoff ready。
- 実装着手時は `spec-dock-issue-execution` workflow に従い、plan の S01 から順に step review / commit gate を通す。

## 実装ステップ証跡

### Implementation Delegation Gate

| step | decision | required reason | delegated role | scope | allowed changes | forbidden changes | required verification | stop conditions | result |
|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | runtime / tests / shipped asset behavior を含むため | dev-coder | Trusted review trigger failure path only | provider/dogfooding `trigger_codex_review.sh`, focused trigger tests | head policy fallback, caller-provided body, broad PR observation refactor, S02+ docs/templates | focused pytest, provider/dogfooding script parity, code-reviewer pass | fake gh POST なし判定不能、JSON consumer impact不明 | passed: worker returned bounded S01 diff, no material decisions beyond approved plan |
| S02 | delegated | shipped skill text / public contract と text assertion を含むため | doc-writer | PR observation skill contract wording only | provider/dogfooding `github-pr-observation/SKILL.md`, focused text assertion | runtime script changes, PR trigger behavior changes, S03+ templates/docs | focused pytest, stale wording inspection, provider/dogfooding skill parity, spec-reviewer pass | S01 behavior と skill wording が一致しない | passed: worker returned bounded S02 diff, no material decisions beyond approved plan |
| S03 | delegated | runtime / scaffold behavior / tests を含むため | dev-coder | Issue design/plan awaiting-compose placeholder and compose materialization | issue design/plan templates, artifact composer, assurance compose orchestration needed to expose no-overwrite conflicts, focused CLI runtime tests | removing design/plan files, broad validator/active/sync rewrite, S04/S90 docs | focused and broader CLI runtime tests, code-reviewer pass | placeholder cannot satisfy active/sync/validate without broader migration | passed: worker returned bounded S03 diff; D-004 adopted as issue-local implementation-boundary decision |
| S04 | delegated | docs / lifecycle evidence only, no code changes | doc-writer / SpecDock operator | `iss-00239` supersession evidence for Epic 00224 close-readiness | `iss-00239` report and `iss-00241` report body ledger entries | requirement/design/plan edits, source code changes, metadata front matter edits, deleting `iss-00239` scaffold history | lifecycle command evidence, GitHub issue state inspection, report inspection, spec-reviewer pass before step completion | close command mutates wrong issue, GitHub state contradicts report, reviewer gate not run | passed: S04 evidence recorded; spec-reviewer re-review returned no findings |
| S90 | delegated | Epic canonical docs / report-only reconciliation, no code changes | doc-writer | Epic current operational contract, corrective issue inclusion ledger, QG-006〜QG-008 traceability, S90 issue report evidence | Epic requirement/design/plan/report and this issue report | source code, tests, templates, skills, historical ADR rewrite, false pass on pending gates | `rg "workflow next" spec-dock/active/epic/{requirement.md,design.md,plan.md,report.md}`, docs diff inspection, traceability ledger inspection | stale current-entrypoint wording remains, trusted base policy contradicts S01/S02, corrective issues or QG ledger omit required pending/formal statuses | passed: S90 docs reconciliation recorded; spec-reviewer returned no findings |
| S99 | delegated | runtime / tests / dogfooding parity / manual validation を含む final gate のため | dev-coder / orchestrator | S99 focused regression fix, full focused suite, sync/validate, manual guidance/compose validation, final reviewer gates | provider runtime, dogfooding mirrors, focused tests, final report evidence | unrelated refactor, weakening S01 fail-closed policy, reverting S03 placeholder contract, false pass on reviewer gates | focused pytest, sync, validate, stale wording inspection, manual temp repo flow, qa/code/spec reviewer pass | full focused suite red, provider/mirror parity diverges, manual flow cannot materialize placeholder, PR observation permission signal regresses | passed: S99 fixes, validation, and final reviewer gates recorded; ready for Step Commit Gate |

### Step Contract Closure

| step | closure id | close condition | evidence | result |
|---|---|---|---|---|
| S01 | tc-001 | base SHA missing / policy missing / invalid / non-UTF-8 / oversized / unreadable は POST なし human gate | focused pytest `trigger_helper and (policy or base_sha or trusted_base)`、broader `trigger_helper`、code-reviewer pass | pass |
| S01 | tc-002 | valid base policy は deterministic multiline body を投稿 | focused pytest `trigger_helper and (policy or base_sha or trusted_base)`、broader `trigger_helper`、code-reviewer pass | pass |
| S02 | tc-003 | skill text は deterministic body / human gate を説明し、fixed bare body を唯一の write として説明しない | text assertion、stale wording `rg` inspection、provider/dogfooding skill parity、spec-reviewer pass | pass |
| S03 | tc-004 | new issue の design / plan は awaiting-assurance-compose placeholder | new issue CLI test, broader S03 runtime test, code-reviewer pass | pass |
| S03 | tc-005 | compose は placeholder を materialize し、substantive content を上書きしない | compose placeholder/no-overwrite tests, broader S03 runtime test, code-reviewer pass | pass |
| S03 | tc-009 | marker が残った direct edit は conflict / fail-closed になり上書きされない | marker-plus-direct-edit compose test, code-reviewer pass | pass |
| S04 | tc-006 | `iss-00239` は `iss-00241` に supersede され、unresolved corrective scaffold として Epic 00224 close-readiness を block しない | `iss-00239` report supersession ledger; `./spec-dock/scripts/spec-dock close iss-00239` -> exit 0 with `state=CLOSED already_closed=true`; `gh issue view 239 --json number,state,title,url,closedAt` -> `state=CLOSED`, `closedAt=2026-06-27T05:17:44Z`, `url=https://github.com/chemitaro/spec-dock/issues/239`; spec-reviewer re-review pass | pass |
| S90 | tc-007 | Epic 正本は `guidance <target>` stdout authority / projection human-debug-only を示し、`workflow next` を current entrypoint として残さない | Epic requirement/design/plan updated; report current operational contract ledger added; `rg "workflow next" ...` returned only historical/superseded hits; spec-reviewer pass | pass |
| S90 | tc-008 | Epic report は corrective issues と gate status を矛盾なく示す | Epic report includes `iss-00237`, `iss-00238`, `iss-00239`, `iss-00241`; `iss-00239` formal supersede; `iss-00241` final reviewer pass; spec-reviewer pass | pass |
| S90 | tc-010 | Step closure / reviewer gate / commit gate cross-issue audit を false pass なしで記録する | Epic traceability quality gate ledger QG-006 now records final pass after S99 reviewer gates; spec-reviewer pass | pass |
| S90 | tc-011 | context packet / clean-room / bounded return evidence audit を false pass なしで記録する | Epic traceability quality gate ledger QG-007 now records final pass after S99 reviewer gates; spec-reviewer pass | pass |
| S90 | tc-012 | Auto-Lite readiness / automatic Lite default disabled / efficiency evidence audit を false pass なしで記録する | Epic traceability quality gate ledger QG-008 now records final pass after S99 reviewer gates; spec-reviewer pass | pass |
| S99 | tc-004 / tc-005 / tc-009 | S03 placeholder / compose / no-overwrite behavior remains valid after S99 regressions | targeted pytest and full focused pytest; manual temp repo new issue -> classify -> compose flow | pass |
| S99 | tc-007 / tc-008 / tc-010 / tc-011 / tc-012 | final validation confirms guidance contract, corrective issue ledger, and traceability gates are not contradicted by implementation state | `sync`, `validate`, stale wording inspections, qa/code/spec reviewer pass | pass |

### Test Contract Closure

| closure id | step | evidence level | pre-implementation evidence | verification command | result |
|---|---|---|---|---|---|
| tc-001 | S01 | red-required | dev-coder 実装前 characterization: `5 failed, 1 passed, 509 deselected`; old behavior posted bare `@codex review` for failure paths | `uv run pytest tests/unit/infra/test_init_update.py -k "trigger_helper and (policy or base_sha or trusted_base)"` | pass: `6 passed, 509 deselected` |
| tc-002 | S01 | covered-existing | valid trusted policy path existed and was preserved while failure paths changed | `uv run pytest tests/unit/infra/test_init_update.py -k "trigger_helper"` | pass: `21 passed, 494 deselected` |
| tc-003 | S02 | inspect-only | stale skill wording existed: fixed bare body was described as the only write contract | `uv run pytest tests/unit/infra/test_init_update.py -k 'issue_75_pr_monitor_assets_retired_and_observation_scaffold_present or issue_231_trigger_helper or issue_176_s01_trigger_helper_blocks_when_base_sha_missing'` | pass: `7 passed, 508 deselected` |
| tc-004 | S03 | red-required | dev-coder characterization: new issue still produced normal scaffold, not placeholder | `uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_assurance_compose.py -k "placeholder or substantive or stale_requirement"` | pass: `4 passed, 53 deselected` |
| tc-005 | S03 | red-required | dev-coder characterization: substantive non-placeholder content was not exposed as the planned compose no-overwrite conflict; reviewer follow-up found placeholder body remained after compose (`1 failed, 3 passed`) | `uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_assurance_compose.py tests/cli_runtime/test_workflow.py -k "issue or compose or guidance"` | pass: `32 passed, 2 skipped, 34 deselected` |
| tc-009 | S03 | red-required | marker plus direct edit lacked explicit S03 conflict coverage before new test | `uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_assurance_compose.py -k "placeholder or substantive or stale_requirement"` | pass: `4 passed, 53 deselected` |
| tc-006 | S04 | inspect-only | `iss-00239` scaffold history existed, but its unresolved corrective scope had already been absorbed into `iss-00241` | `./spec-dock/scripts/spec-dock close iss-00239`; `gh issue view 239 --json number,state,title,url,closedAt`; report inspection; spec-reviewer re-review | pass: lifecycle command exit 0 and GitHub `#239` closed; no local diff from lifecycle command because GitHub issue was already closed |
| tc-007 | S90 | inspect-only | Epic docs had stale current-entrypoint wording for `workflow next` / generated projection authority | Epic docs inspection; `rg "workflow next" spec-dock/active/epic/{requirement.md,design.md,plan.md,report.md}`; spec-reviewer | pass: current-entrypoint wording updated; remaining `workflow next` hits are historical/superseded only |
| tc-008 | S90 | inspect-only | Epic report needed corrective issue inclusion and current close-readiness state | Epic report inspection; spec-reviewer | pass: corrective issue ledger added with pass / formal supersede / final reviewer statuses |
| tc-010 | S90 | inspect-only | QG-006 was required as explicit cross-issue audit, not implicit AC-010 coverage | Epic traceability ledger inspection; spec-reviewer | pass: QG-006 recorded as pass after final reviewer confirmation |
| tc-011 | S90 | inspect-only | QG-007 was required as explicit context routing evidence audit, not implicit AC-010 coverage | Epic traceability ledger inspection; spec-reviewer | pass: QG-007 recorded as pass after final reviewer confirmation |
| tc-012 | S90 | inspect-only | QG-008 was required as explicit Auto-Lite readiness audit, not implicit AC-010 coverage | Epic traceability ledger inspection; spec-reviewer | pass: QG-008 recorded as pass after final reviewer confirmation |
| S99-focused | S99 | red-required | first full focused suite exposed 9 failures: stale full scaffold expectations, draft-doc placeholder leakage, dogfooding mirror drift, permission-denied next-action regression | targeted pytest subsets, provider/mirror parity inspections | pass: `2 passed, 43 deselected`; `7 passed, 508 deselected`; parity diffs clean |
| S99-full | S99 | required | after S99 fixes, full focused suite had one dogfooding `.meta.json` snapshot failure, then snapshot was updated | `uv run pytest tests/unit/infra/test_init_update.py tests/cli_runtime/test_new.py tests/cli_runtime/test_assurance_compose.py tests/cli_runtime/test_workflow.py` | pass: `578 passed, 5 skipped` |
| S99-sync-validate | S99 | required | final repo projections and validation must be current | `./spec-dock/scripts/spec-dock sync`; `./spec-dock/scripts/spec-dock validate` | pass: sync wrote derived artifacts; validate `nodes=152` |
| S99-manual | S99 | manual-required | real command flow must preserve Issue execution/guidance behavior | temp git repo with fake `gh`; init, new initiative/epic/issue, requirement edit, active set, classify, compose, guidance issue-execution | pass: design/plan placeholders initially `1`; after compose markers `0`, managed sections `1`; guidance authority/projection counts `1` |

### Closure Coverage

| closure id | requirement / expectation | evidence | status |
|---|---|---|---|
| tc-001 | AC-001 / EC-001〜EC-003: trusted base policy failure is POSTなし human gate | tests assert no POST, `success=false`, `overall_status=human_gate`, `normalized_status=human_gate`, `recommended_next_action=human_gate`, `trigger.action=blocked`, blocking limitations | pass |
| tc-002 | AC-002: valid base policy posts deterministic multiline body | tests assert source, policy hash, reviewed head SHA, and posted body match expected multiline trigger | pass |
| tc-003 | AC-003: skill public contract matches runtime behavior | text assertion requires runtime-composed deterministic body, trusted policy evidence, no comment on base policy failure, caller-provided body prohibition; stale fixed-bare-body phrases absent by `rg` | pass |
| tc-004 | AC-006: new issue design/plan are assurance compose placeholders | new issue test asserts `artifact_state: awaiting-assurance-compose`, `assurance classify --stage requirement`, `assurance compose --artifact all`, and no managed sections yet | pass |
| tc-005 | AC-007: compose safely materializes placeholder / does not overwrite substantive content | compose tests assert marker and placeholder body are removed, managed sections are added, substantive non-placeholder content remains unchanged on conflict | pass |
| tc-009 | EC-004: marker plus direct edit is not overwritten | compose test asserts `substantive_content_conflict` and unchanged artifact text | pass |
| tc-006 | AC-008: `iss-00239` is superseded by `iss-00241` | `iss-00239` report now records formal supersession without deleting scaffold history; lifecycle close command returned `state=CLOSED already_closed=true`; GitHub `#239` is `CLOSED` with `closedAt=2026-06-27T05:17:44Z`; no local diff was produced by the lifecycle command because the GitHub issue was already closed; spec-reviewer re-review returned no findings | pass |
| tc-007 | AC-004 / AC-005 / EC-005: guidance stdout authority and projection human/debug-only boundary | Epic requirement/design/plan/report now describe `guidance <target>` stdout as current handoff and projection files as non-canonical human/debug output; spec-reviewer pass | pass |
| tc-008 | AC-009 / AC-010: Epic report current close-readiness | Epic report records current operational contract, trusted base policy fail-closed behavior, corrective issue inclusion, and final reviewer pass | pass |
| tc-010 | AC-010: step closure / reviewer gate / commit gate cross-issue audit | QG-006 ledger added and final reviewer gates passed; spec-reviewer pass | pass |
| tc-011 | AC-010: context packet / clean-room / bounded return evidence audit | QG-007 ledger added and final reviewer gates passed; spec-reviewer pass | pass |
| tc-012 | AC-010: Auto-Lite readiness / automatic Lite default disabled / efficiency evidence audit | QG-008 ledger added; automatic Lite default remains disabled; final reviewer gates passed | pass |
| S99-focused | AC-006 / AC-007 / EC-004: placeholder and compose behavior remains usable in real workflows | new issue placeholder test, compose tests, draft-doc normalization, manual temp repo classify/compose flow | pass |
| S99-review-policy | AC-001〜AC-003: trusted base review and observation behavior remains aligned | focused suite, permission-denied regression fix, stale fixed-bare-body inspection | pass |
| S99-final-validation | AC-009 / AC-010: final quality gate evidence | focused suite, sync, validate, stale wording inspections, manual guidance flow, qa/code/spec reviewer pass | pass |

### Closure Delta

| step | added / changed closure | reason | re-review |
|---|---|---|---|
| S03 | direct edits to `design.md` / `plan.md` now surface as `substantive_content_conflict`; stale requirement still surfaces as `stale_source_binding` | make S03 no-overwrite safety observable at compose boundary while preserving requirement stale protection | code-reviewer pass |

### Reviewer Gate Status

| gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision |
|---|---|---|---|---|---|
| S01 code review | code-reviewer | fresh uncommitted S01 diff after focused tests | passed | none | S01 eligible for Step Commit Gate |
| S02 spec review | spec-reviewer | fresh uncommitted S02 diff after focused tests and inspections | passed | none | S02 eligible for Step Commit Gate |
| S03 code review | code-reviewer | fresh uncommitted S03 diff after P1 fix and focused/broader tests | passed | none | S03 eligible for Step Commit Gate |
| S04 spec review | spec-reviewer | fresh uncommitted S04 report-only diff after final gate pending correction | passed | none | S04 eligible for Step Commit Gate |
| S90 spec review | spec-reviewer | fresh uncommitted S90 docs/report diff after `workflow next` inspection and `git diff --check` | passed | none | S90 eligible for Step Commit Gate |
| S99 final QA review | qa-reviewer | fresh uncommitted S99 diff after focused suite, sync/validate, manual flow, and report update | passed | none | S99 eligible for Step Commit Gate |
| S99 final code review | code-reviewer | fresh uncommitted S99 runtime/test/mirror/report diff after P2 report ledger fix | passed | none | S99 eligible for Step Commit Gate |
| S99 final spec review | spec-reviewer | fresh uncommitted S99 diff after P1 trigger usage fix and P2 Epic completion reconciliation | passed | none | S99 eligible for Step Commit Gate |

### Step Commit Gate

| step | review scope | step reviewer verdict | commit scope | closure state | commit evidence | post-commit clean check |
|---|---|---|---|---|---|---|
| S01 | trigger helper scripts and focused trigger tests | code-reviewer pass, no findings, confidence 0.89 | S01 runtime/test/report evidence only | committed | S01 scope commit created; exact hash is external git evidence | pass: post-commit `git status --short` clean |
| S02 | PR observation skill text and focused text assertion | spec-reviewer pass, no findings, confidence 0.88 | S02 skill-doc/test/report evidence only | committed | S02 scope commit created; exact hash is external git evidence | pass: post-commit `git status --short` clean |
| S03 | issue design/plan placeholders, compose materialization/no-overwrite behavior, focused CLI runtime tests | code-reviewer pass after one P1 fix, no findings, confidence 0.88 | S03 runtime/template/test/report evidence only | committed | S03 scope commit created; exact hash is external git evidence | pass: post-commit `git status --short` clean except this report amendment |
| S04 | report-only supersession evidence for `iss-00239` / `iss-00241` | spec-reviewer pass after one P1 fix, no findings, confidence 0.88 | S04 report evidence only | committed | S04 scope commit created; exact hash is external git evidence | pass: post-commit `git status --short` clean |
| S90 | Epic docs/report reconciliation and `iss-00241` S90 evidence | spec-reviewer pass, no findings, confidence 0.90 | S90 docs/report evidence only | committed | S90 scope commit created; exact hash is external git evidence | pass: post-commit `git status --short` clean |
| S99 | final validation fixes, focused suite, sync/validate, manual flow, final report evidence | qa-reviewer pass confidence 0.89; code-reviewer pass confidence 0.86; spec-reviewer pass confidence 0.91 | S99 runtime/test/mirror/report evidence only | committed | S99 scope commit created; exact hash is external git evidence | pass: post-commit `git status --short` clean |

## 最終品質ゲート

### ドキュメント影響の解消ステップ S90
| 対象 | 更新要否 | 担当 | 証跡 | 仕様レビュアー結果 |
|---|---|---|---|---|
| Epic requirement/design/plan/report, skill docs, issue reports | yes | doc-writer / orchestrator | S02/S04/S90/S99 evidence recorded | pass: qa/code/spec reviewer gates passed |

### 最終 QA ゲート
| reviewer | 範囲 | integration test decision | evidence | result |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | focused suite, sync/validate, manual flow, skipped-test assessment | pass: no findings, confidence 0.89 |

### 最終コードレビューゲート
| reviewer | 範囲 | findings / fixes | re-review count | result |
|---|---|---|---|---|
| code-reviewer | runtime / tests / scaffold behavior | initial P2 report ledger finding fixed; final re-review findings none | 1 | pass |

### 最終 spec review ゲート
| reviewer | 範囲 | findings / fixes | re-review count | result |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / Epic docs alignment | final review P1 stale trigger usage and P2 Epic completion reconciliation fixed; final re-review findings none | 9 | pass |
