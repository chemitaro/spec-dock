---
種別: 実装報告書（Issue）
ID: "iss-00233"
タイトル: "Roll Out Adaptive Workflow With Legacy Compatibility And Telemetry"
関連GitHub: ["#233"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00233 Roll Out Adaptive Workflow With Legacy Compatibility And Telemetry — 実装報告

## 仕様解釈・判断台帳
| ID | 状態 | 種別 | 起票元 | 判断 | 根拠 | 処置 | 証跡 | フォローアップ |
|---|---|---|---|---|---|---|---|---|
| D-233-001 | resolved | scope | spec-reviewer | I07 は readiness payload だけでなく strict-legacy workflow、automation-stalled operator surface、efficiency evidence を閉じる | 親 Epic I07 closure が E-RQ-012〜014 / E-AC-013〜016 を含むため | applied | `requirement.md`, `design.md`, `plan.md` | none |
| D-233-002 | resolved | compatibility | implementation | substantive requirement + missing assurance は strict-legacy ready とし、invalid / stale assurance は fail-closed のままにする | 既存 Issue の grandfather path と新 contract の stale safety を両立するため | applied | `workflow.py`; `test_workflow.py` | none |
| D-233-003 | resolved | safety | implementation | repeated blocker fingerprint は `automation_stalled` / human gate として operator-facing payload に出す | 回数上限を risk acceptance にせず human gate へ移すため | applied | `pr_observation_wait.py`; provider/mirror parity test | none |
| D-233-004 | resolved | code-review | code-reviewer | missing assurance は step assurance / context routing projection でも strict-legacy ready として扱う | workflow contract を実装したが context routing regression test が旧期待値のままだったため | applied | `test_workflow_context_routing.py` | none |
| D-233-005 | resolved | code-review | code-reviewer | 同一 blocker fingerprint の初回観測では terminal break せず、required count まで観測してから automation-stalled 判定する | `same_fingerprint_count=2` の default で surface が到達不能になるのを防ぐため | applied | `pr_observation_wait.py` | none |
| D-233-006 | resolved | qa-review | qa-reviewer | automation-stalled は文字列検査ではなく helper 実行で behavior を検証する | operator surface の実動作と `merge_prepared` 不変条件を固定するため | applied | `test_init_update.py` | none |
| D-233-007 | resolved | qa-review | qa-reviewer | E-AC-016 は live telemetry ではなく baseline fixture と missing metrics summary の明示で初期 rollout evidence とする | この Epic では production telemetry backend を追加しないため | applied | `assurance.py`; `test_assurance.py` | future telemetry gate |
| D-233-008 | resolved | spec-review | spec-reviewer | Auto-Lite future adoption gates は accepted ADR / policy version bump / rollout Issue / telemetry gate の 4 点に統一する | 親 Epic と Issue の gate 数がずれていたため | applied | parent Epic docs; issue assertions | none |
| D-233-009 | resolved | spec-review | spec-reviewer | 親 Epic I07 は shadow / opt-in / Standard default 実移行ではなく initial rollout readiness closure として整合させる | initial Epic scope では automatic Lite default を有効化しないため | applied | parent `plan.md`, `report.md` | future rollout Issue |
| D-233-010 | resolved | spec/code-review | reviewers | strict-legacy missing contract でも valid contract と同じ `auto_lite_readiness.efficiency_baseline` shape を返す | public JSON contract を stable に保つため | applied | `assurance_text.py`; `test_assurance_text.py` | none |
| D-233-011 | resolved | code-review | code-reviewer | automation-stalled 判定は `normalized_status=human_gate` のときだけ適用し、CI failed / fix_ci を上書きしない | CI failure priority を維持するため | applied | `pr_observation_wait.py`; provider/mirror parity test | none |

## 証跡採用台帳
| ID | 採用状態 | 出所 | 対象 | 判断理由 | 証跡 | 次アクション |
|---|---|---|---|---|---|---|
| EAL-233-001 | adopted | spec-reviewer | issue plan | P1 指摘を受け、I07 scope を readiness payload から rollout / compatibility / automation-stalled / efficiency へ拡張した | planning review fail findings | fresh re-review |

## 実装サマリー
- `assurance` JSON に `auto_lite_readiness` を追加し、automatic Lite default が初期 rollout で無効であること、future adoption requirements、rollback mode、required metrics、missing metrics summary を機械可読にした。
- `workflow next issue-execution` は substantive requirement + missing assurance を strict-legacy ready として扱い、invalid / stale assurance は既存どおり fail-closed にした。
- PR observation wait に repeated blocker fingerprint の `automation_stalled` operator surface を追加し、merge-prepared へ進めない human gate として出力する。

## セッションログ

### セッションログ（2026-06-23 S01-S03/S90）
#### 実施内容
- S01: `domain.assurance.auto_lite_readiness_report` と presentation JSON output を追加した。
- S02: missing assurance の workflow state を strict-legacy ready に変更した。
- S03: PR observation wait の stable same blocker fingerprint を `automation_stalled` として出力する helper を追加し、provider / dogfooding mirror を同期した。
- S90: Issue requirement / design / plan を planning review 指摘に合わせて拡張した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/domain/test_assurance.py tests/unit/presentation/test_assurance_text.py tests/cli_runtime/test_assurance.py tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py -k 'auto_lite or strict_legacy or missing_assurance or malformed_assurance or stale_source_binding'
# 9 passed, 29 deselected

uv run pytest tests/unit/infra/test_init_update.py -k 'issue_233_pr_observation_wait'
# 1 passed, 508 deselected

diff -u src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py .agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py
# pass
```

#### クロージャ網羅
| closure id | step | 検証証跡 | 結果 | メモ |
|---|---|---|---|---|
| tc-233-001 | S01 | `test_auto_lite_readiness_report_keeps_default_disabled_and_records_adoption_gates`; presentation / CLI assertions | pass | automatic Lite default disabled |
| tc-233-002 | S01 | readiness future adoption / rollback assertions | pass | accepted ADR / policy bump / rollout issue / telemetry gate |
| tc-233-003 | S01 | `test_assurance_show_and_verify_strict_legacy_missing` | pass | strict-legacy missing contract |
| tc-233-004 | S01 | readiness required metrics / missing metrics summary / efficiency baseline assertions | pass | efficiency evidence surface |
| tc-233-005 | S02 | `test_workflow_next_missing_assurance_uses_strict_legacy_execution_authority` | pass | workflow strict-legacy ready |
| tc-233-006 | S03 | `test_issue_233_pr_observation_wait_exposes_automation_stalled_operator_surface` | pass | automation-stalled / human gate |
| tc-233-007 | S90 | issue docs inspection | pass | rollout closure documented |
| tc-233-008 | S99 | final gates | pending | final validation / reviewers |

## 最終品質ゲート
| gate | reviewer / command | evidence | result |
|---|---|---|---|
| focused tests | command | targeted tests above | pass |
| provider / mirror parity | command | wait script diff -> pass | pass |
| lint | command | `make lint` -> ruff check pass; ruff format pass; mypy pass | pass |
| validate | command | `./spec-dock/scripts/spec-dock validate` -> ok nodes=148 | pass |
| assurance verify | command | `./spec-dock/scripts/spec-dock assurance verify --format json` -> strict / complex valid | pass |
| code review | code-reviewer | initial P1/P2 fixed; re-review findings none | pass |
| QA review | qa-reviewer | initial P1 fixed; re-review P2 integration coverage note only | pass |
| spec review | spec-reviewer | initial P1 fixed; strict-legacy readiness shape P2 fixed; re-review findings none | pass |
| final commit | git commit | pending | pending |
