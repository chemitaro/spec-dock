---
種別: 実装報告書（Issue）
ID: "iss-00232"
タイトル: "Enforce Blocker Centric PR Repair And Rereview"
関連GitHub: ["#232"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00232 Enforce Blocker Centric PR Repair And Rereview — 実装報告

## 仕様解釈・判断台帳
| ID | 状態 | 種別 | 起票元 | 判断 | 根拠 | 処置 | 証跡 | フォローアップ |
|---|---|---|---|---|---|---|---|---|
| D-232-001 | resolved | implementation | orchestrator | blocker policy は current Codex issue comment の priority token に限定して追加する | 既存 unresolved thread / changes requested / no findings contracts を壊さないため | applied | `pr_review_snapshot.py` | none |
| D-232-002 | resolved | scope | spec-reviewer | full automation-stalled operator surfacing と E-AC-013 formal closure は I07 に残し、この Issue は blocker fingerprint evidence までを閉じる | I06 の repair input と I07 の rollout/telemetry responsibility を分離するため | applied | `blocker_policy.blocker_fingerprints`; Epic I07 follow-up | iss-00233 |
| D-232-003 | resolved | QA coverage | qa-reviewer | P0/P1、one-sided P2、priority-less comment を dedicated regression tests で固定する | blocker policy の誤分類が PR merge gate を誤誘導しないようにするため | applied | `test_issue_232_review_collector_treats_p1_comment_as_blocker`; one-sided / priority-less tests | none |
| D-232-004 | resolved | code-review | code-reviewer | `blocker_policy_no_action` は既存 `reviewDecision` / active changes-requested blocker を上書きしない | P2-only comment が GitHub review state の blocker を消して merge-prepared にしないため | applied | `blocker_policy_no_action_promotes`; reviewDecision regression test | none |
| D-232-005 | resolved | code-review | code-reviewer | protected domain 判定は単語/句境界で行い、`author` 内の `auth` などの substring 誤検知を避ける | promoted P2 の条件を protected domain + machine evidence に限定するため | applied | `has_protected_domain`; `author` negative case | none |
| D-232-006 | resolved | evidence | orchestrator | tc-232-001 / tc-232-002 は red-first 証跡を保持していないため `green-regression` として扱う | 実装と同じセッションで追加した回帰テストであり、失敗証跡を主張できないため | applied | `plan.md` closure table | none |
| D-232-007 | resolved | QA polish | qa-reviewer | P3 default non-blocking branch を dedicated parameter で固定し、parity closure evidence を pass に揃える | QA pass 後の P3 指摘を消化し、ledger inconsistency を残さないため | applied | P3 parameter; tc-232-005 closure row | none |

## 証跡採用台帳
| ID | 採用状態 | 出所 | 対象 | 判断理由 | 証跡 | 次アクション |
|---|---|---|---|---|---|---|
| EAL-232-001 | adopted | Epic ADR / plan | implementation | blocker-centric / P2 suppression / promoted P2 を I06 slice として採用した | `20260623t074447z-adr-blocker-centric-pr-risk-closure-rereview.md`; Epic plan I06 | implementation |

## 実装サマリー
- `pr_review_snapshot.py` に priority-bearing Codex issue comment の `blocker_policy` payload を追加した。
- P2 / P3 only は `blocker_policy_no_action` として merge-prepared を妨げず、protected domain + machine evidence を持つ P2 は `promoted_blocker` として human gate にする。
- Existing changes requested / unresolved thread の blocker behavior は維持した。

## セッションログ

### セッションログ（2026-06-23 S01/S90）
#### 実施内容
- Provider / dogfooding mirror の `pr_review_snapshot.py` に blocker policy helper、payload、decision integration を追加した。
- P2-only no-action、protected P2 promotion、P0/P1 blocker、one-sided P2、priority-less fallback、reviewDecision preservation の regression tests を追加した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/infra/test_init_update.py -k 'issue_232 or issue_182_s01_review_collector_exposes_current_changes_requested_evidence'
# 10 passed, 498 deselected
```

#### クロージャ網羅
| closure id | step | 検証証跡 | 結果 | メモ |
|---|---|---|---|---|
| tc-232-001 | S01 | `test_issue_232_review_collector_treats_p2_only_comment_as_non_blocking` | pass | P2-only no-action |
| tc-232-002 | S01 | `test_issue_232_review_collector_promotes_protected_p2_with_machine_evidence` | pass | protected P2 promotion |
| tc-232-003 | S01 | `test_issue_182_s01_review_collector_exposes_current_changes_requested_evidence` | pass | existing blocker retained |
| tc-232-004 | S01 | issue_232 tests | pass | blocker fingerprints present in payload |
| tc-232-004a | S01 | `test_issue_232_review_collector_treats_p1_comment_as_blocker` | pass | P1 priority blocker |
| tc-232-004b | S01 | `test_issue_232_review_collector_keeps_one_sided_p2_non_blocking` | pass | protected-only / evidence-only P2 remains non-blocking |
| tc-232-004c | S01 | `test_issue_232_review_collector_keeps_priorityless_comment_on_fallback_path` | pass | priority-less current Codex comment remains low-confidence fallback |
| tc-232-004d | S01 | existing GraphQL / review-thread limitation regression tests | pass | existing fail-closed behavior retained |
| tc-232-004e | S01 | `test_issue_232_review_collector_preserves_review_decision_blocker_for_p2_only` | pass | `reviewDecision` blocker is not overwritten by no-action |
| tc-232-004f | S01 | `test_issue_232_review_collector_keeps_one_sided_p2_non_blocking` | pass | P3 remains non-blocking follow-up |
| tc-232-005 | S90 | provider / dogfooding mirror diff | pass | final gate |

## 最終品質ゲート
| gate | reviewer / command | evidence | result |
|---|---|---|---|
| focused tests | command | `uv run pytest tests/unit/infra/test_init_update.py -k 'issue_232 or issue_182_s01_review_collector_exposes_current_changes_requested_evidence'` -> 10 passed | pass |
| parity | command | provider / dogfooding review snapshot script diff -> pass | pass |
| lint | command | `make lint` -> ruff check pass; ruff format pass; mypy pass | pass |
| validate | command | `./spec-dock/scripts/spec-dock validate` -> ok nodes=148 | pass |
| assurance verify | command | `./spec-dock/scripts/spec-dock assurance verify --format json` -> critical / deep valid | pass |
| code review | code-reviewer | pass: no findings after re-review | pass |
| QA review | qa-reviewer | pass: P3 follow-up covered with P3 non-blocking parameter and parity ledger update | pass |
| spec review | spec-reviewer | pass: parent design / plan / report E-AC-013 ownership reconciled | pass |
| final commit | git commit | committed in current issue branch | pass |

## 省略/例外メモ
- Real PR repair loop / actual external re-review は Epic PR preparation で確認する。
- Dedicated automation-stalled UI / report surfacing は I07 rollout / telemetry に送る。
