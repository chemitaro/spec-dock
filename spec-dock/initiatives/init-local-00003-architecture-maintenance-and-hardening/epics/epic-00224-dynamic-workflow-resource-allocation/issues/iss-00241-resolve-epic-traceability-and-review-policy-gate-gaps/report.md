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

## 証跡採用台帳

| ID | adoption_status | source | target | rationale | evidence | next_action |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | research | `requirement.md`, `design.md`, `plan.md` | Epic audit の P0/P1/P2 gap を corrective Issue scope と AC/EC へ採用した | `../../discussions/20260627t025746z-research-epic-quality-gate-traceability-audit.md` | spec-reviewer |
| EAL-002 | adopted | spec-reviewer | `requirement.md`, `design.md`, `plan.md` | Spec reviewer が audit findings を false positive ではないと判定したため、blocking remediation scope として採用した | `../../discussions/20260627t030737z-disc-spec-reviewer-epic-traceability-gate.md` | spec-reviewer |
| EAL-003 | adopted | ADR | `requirement.md`, `design.md`, `plan.md` | Trusted base SHA policy failure は human gate という accepted decision を AC-001 / S01 へ反映した | `../../discussions/20260623t074444z-adr-trusted-base-sha-github-review-policy.md` | S01 |
| EAL-004 | adopted | ADR / issue evidence | `requirement.md`, `design.md`, `plan.md` | Fixed skill kernel の current operational surface を `guidance <target>` stdout authority として反映した | `../../discussions/20260623t074441z-adr-fixed-skill-kernel-compiled-runbook-authority.md`, `../iss-00238-stdout-runbook-handoff-instead-of-generated-workflow-files/discussions/20260624t083737z-research-stdout-runbook-handoff-current-state.md`, `../iss-00238-stdout-runbook-handoff-instead-of-generated-workflow-files/report.md` | S90 |
| EAL-005 | adopted | research | `requirement.md`, `design.md`, `plan.md` | `iss-00239` の placeholder scaffold 推奨案を、吸収 scope として AC-006 / AC-007 / S03 へ採用した | `../iss-00239-compose-issue-planning-templates-after-assurance-classification/discussions/20260624t113051z-research-assurance-compose-scaffold-analysis.md` | S03 |
| EAL-006 | adopted | interview | `requirement.md`, `design.md`, `plan.md`, Epic report | `iss-00239` を `iss-00241` に吸収するユーザー判断を採用した | `discussions/20260627t031736z-interview-corrective-issue-scope-confirmation.md` | S04 |

## 目的整合台帳

| 対象 | 主要目的の証跡 | 副次要件の証跡 | 逆転リスク | レビュアー判定 |
|---|---|---|---|---|
| OAL-001 | Epic 00224 の取りこぼした品質ゲート問題を単一 corrective Issue で解決する | PR review policy、skill wording、guidance docs、template lifecycle、Epic report reconciliation | low: scope は audit / spec-reviewer findings と user-approved absorption に限定 | pending |

## 仕様 authoring ゲート

| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |
|---|---|---|---|---|---|---|
| requirement | Epic requirement/design/plan/report、accepted ADR、Epic audit、spec-reviewer report、Issue 239 research、Issue 241 interview、current runtime / skill / tests search | `iss-00239` の扱いは user-approved: `iss-00241` に吸収 | EAL-001〜006 を採用して `requirement.md` を具体化 | passed: fresh `spec-reviewer` final re-review returned no findings, review_status=pass, confidence=0.88 | no | promoted to implementation-ready planning package with design/plan |
| design | reviewer-pass済み requirement package、現行 provider/dogfooding skill/script、runtime guidance、artifact composer/new issue tests、Issue 239 research | 追加質問なし | 同じ証跡を `design.md` へ反映し、module/file boundaries と test strategy を固定 | passed: fresh `spec-reviewer` final re-review returned no findings, review_status=pass, confidence=0.88 | no | promoted to implementation-ready planning package with plan |
| plan | reviewer-pass済み requirement/design package、workflow_spec_authoring、phase_plan_issue、authoring/issue-plan、workflow_issue | 追加質問なし | S01〜S04/S90/S99 の executable step contract と closure index を作成 | passed: fresh `spec-reviewer` final re-review returned no findings, review_status=pass, confidence=0.88 | no | ready for issue execution handoff |

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
- Fresh `spec-reviewer` final re-review は findings なし、`review_status=pass`、confidence 0.88。

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
- Requirement / design / plan / report は final fresh `spec-reviewer` pass を受け、planning package として implementation handoff ready。
- 実装着手時は `spec-dock-issue-execution` workflow に従い、plan の S01 から順に step review / commit gate を通す。

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
| spec-reviewer | requirement / design / plan / report / Epic docs alignment | attempt 1: delegation contract / seeds / evidence path findings; attempt 2: EAL path finding; attempt 3: EC-004 marker-preserved direct-edit coverage finding; final: no findings | 3 | pass |
