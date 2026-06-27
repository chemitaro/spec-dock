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
- まだ実装は開始していない。
- 本 report は Issue planning 中の evidence adoption / authoring gate を記録する。

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

### Step Commit Gate

| step | review scope | step reviewer verdict | commit scope | closure state | commit evidence | post-commit clean check |
|---|---|---|---|---|---|---|
| S01 | trigger helper scripts and focused trigger tests | code-reviewer pass, no findings, confidence 0.89 | S01 runtime/test/report evidence only | committed | S01 scope commit created; exact hash is external git evidence | pass: post-commit `git status --short` clean |
| S02 | PR observation skill text and focused text assertion | spec-reviewer pass, no findings, confidence 0.88 | S02 skill-doc/test/report evidence only | committed | S02 scope commit created; exact hash is external git evidence | pass: post-commit `git status --short` clean |
| S03 | issue design/plan placeholders, compose materialization/no-overwrite behavior, focused CLI runtime tests | code-reviewer pass after one P1 fix, no findings, confidence 0.88 | S03 runtime/template/test/report evidence only | committed | S03 scope commit created; exact hash is external git evidence | pass: post-commit `git status --short` clean except this report amendment |
| S04 | report-only supersession evidence for `iss-00239` / `iss-00241` | spec-reviewer pass after one P1 fix, no findings, confidence 0.88 | S04 report evidence only | ready_to_commit | pending | pending: commit after S04 reviewer gate |

## 最終品質ゲート

### ドキュメント影響の解消ステップ S90
| 対象 | 更新要否 | 担当 | 証跡 | 仕様レビュアー結果 |
|---|---|---|---|---|
| Epic requirement/design/plan/report, skill docs, issue reports | yes | doc-writer | planned in S02/S04/S90 | pending |

### 最終 QA ゲート
| reviewer | 範囲 | integration test decision | evidence | result |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | pending | pending | pending |

### 最終コードレビューゲート
| reviewer | 範囲 | findings / fixes | re-review count | result |
|---|---|---|---|---|
| code-reviewer | runtime / tests / scaffold behavior | pending | 0 | pending |

### 最終 spec review ゲート
| reviewer | 範囲 | findings / fixes | re-review count | result |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / Epic docs alignment | planning-stage reviews passed before S04/S90/S99 execution; current final gate remains pending until S04 supersession evidence and S90/S99 Epic traceability updates are reviewed | 7 | pending |
