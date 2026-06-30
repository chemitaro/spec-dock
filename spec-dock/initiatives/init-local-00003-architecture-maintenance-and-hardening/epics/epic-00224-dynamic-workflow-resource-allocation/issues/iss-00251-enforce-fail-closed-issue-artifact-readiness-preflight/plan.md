---
種別: 実装計画書（Issue）
ID: "iss-00251"
タイトル: "Enforce Fail Closed Issue Artifact Readiness Preflight"
Issue Grade: "strict"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00251 Enforce Fail Closed Issue Artifact Readiness Preflight — Issue 実装計画書（Strict）

## 1. 実装戦略

Manual test F-001〜F-004 を red regression として固定し、readiness 判定を小さく修正する。R0 は後続 G1〜G4 の前提なので、実装範囲を readiness classifier に限定する。

## 2. マイルストーン

| Milestone | 成果 | 検証 |
|---|---|---|
| M0 | 現行 readiness classifier と F-001〜F-004 の再現位置を確認 | focused inspection |
| M1 | requirement / artifact placeholder detector を追加 | unit tests |
| M2 | plan executable predicate と quality marker filter を分離 | CLI runtime tests |
| M3 | design scaffold predicate を explicit marker に限定 | CLI runtime positive/negative tests |
| M4 | 既存 contract 上の reviewer / adoption evidence 欠落を generic block reason として扱う hook を確認 | domain tests or inspected no-op |
| M90 | provider / dogfooding docs の readiness contract を同期 | docs inspection |
| M95 | strict spec review | spec-reviewer pass |
| M99 | issue-local handoff gate | `uv run pytest tests/unit/domain/test_workflow_state.py tests/cli_runtime/test_workflow.py` と `./spec-dock/scripts/spec-dock validate` |

## 3. Behavior Backlog

| Behavior | 内容 | Closure |
|---|---|---|
| B-001 | `REQ-XXX` / `CON-...` / composite placeholder が ready を block する | AC-001 / AC-003 |
| B-002 | quality gate heading だけの plan が ready にならない | AC-002 |
| B-003 | substantive design title の `template` / `placeholder` は false block しない | AC-004 |
| B-004 | `artifact_state: awaiting-assurance-compose` は block する | AC-005 |
| B-005 | 既存 contract が必須化する reviewer / adoption evidence 欠落を generic block reason にできる | AC-006 |
| B-006 | strict-legacy / stale source binding 既存挙動が退行しない | AC-007 |

## 4. 変更対象

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/workflow_state.py`
- 必要な場合のみ `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifact_readiness.py`
- `tests/unit/domain/test_workflow_state.py`
- `tests/cli_runtime/test_workflow.py`
- provider / dogfooding docs の該当 readiness 記述

## 5. 禁止変更

- G1〜G4 の guidance / draft routing / evidence gate を R0 に混ぜない。
- profile template 本文の全面改訂を行わない。
- automatic Lite default を有効化しない。

## 6. Review / commit gate

- M1〜M4 は意味のある runtime regression 単位で review 可能にする。
- M99 では静的解析 / lint / focused tests / validate の実行結果または未実施理由を `report.md` に記録する。
- commit 候補は readiness classifier 修正と regression test を一体のレビュー可能単位とする。

## 7. 実装ステップ / 実行ステップ契約（Executable Step Contract）

| Step | Milestone | 対応Behavior | 実装内容 | Red / 代替証跡 | Green 検証 | Refactor / guardrail | 報告証跡（Report evidence） |
|---|---|---|---|---|---|---|---|
| S00 | M0 | B-001〜B-006 | 現行 readiness 判定の配置、既存 tests、F-001〜F-004 の再現観点を確認する | inspect-only: `application/workflow.py` と既存 `tests/cli_runtime/test_workflow.py` を確認 | 調査結果を report の M0 session に記録 | 実装変更なし | セッションログ、対象関数、既存 coverage |
| S01 | M1 | B-001 | requirement placeholder sentinel と旧 scaffold sentence の block を補強する | failing unit/CLI test または既存 test 不足の inspect evidence | `tests/unit/domain/test_workflow_state.py` または `tests/cli_runtime/test_workflow.py` の該当 test pass | G1〜G4 の wording / routing / evidence policy を変更しない | Red/Green、変更ファイル、AC-001/AC-003 closure |
| S02 | M2 | B-002 / B-003 | plan executable predicate と quality marker / placeholder cell 判定を分離する | quality gate heading だけ、composite placeholder cell、list placeholder の failing test | focused CLI workflow tests pass | ordinary `...` の過剰 block を避ける | AC-002/AC-003 closure |
| S03 | M3 | B-004 / B-006 | design scaffold predicate を explicit marker に限定し、ordinary word `template` / `placeholder` の false block を避ける | title/body に普通語として `template` / `placeholder` を含む substantive design の regression test | positive/negative CLI workflow tests pass | `artifact_state: awaiting-assurance-compose` は引き続き block | AC-004/AC-005/AC-007 closure |
| S04 | M4 | B-005 | 既存 contract が必須化する reviewer / adoption evidence 欠落を generic block reason として扱えるか確認し、必要な最小 hook だけ追加する | inspect-only or failing test: G3 の policy 定義を R0 に持ち込まないことを確認 | existing authority / ledger tests または focused domain test pass | grade-aware evidence requirements の新規定義を追加しない | AC-006 closure / no-op rationale |
| S90 | M90 | B-001〜B-006 | provider / dogfooding docs の readiness contract を必要最小限で同期する | docs inspection | `rg` inspection と `./spec-dock/scripts/spec-dock validate` | source of truth は provider 側を優先 | docs parity evidence |
| S95 | M95 | all | fresh spec review を実行する | review request | `review_status: pass` | fail finding は修正して再レビュー | Reviewer Gate Status |
| S99 | M99 | all | issue-local handoff gate を実行する | N/A | focused tests、必要な静的解析 / lint、`validate` | 未実施理由と残リスクを report に記録 | M99 closure / commit candidate |

### Closure Index

| Closure ID | 対応AC | 対応Step | 必須証跡 |
|---|---|---|---|
| C-001 | AC-001 / AC-003 | S01 | requirement placeholder sentinel / scaffold sentence block test |
| C-002 | AC-002 / AC-003 | S02 | plan quality-marker-only and placeholder-cell block tests |
| C-003 | AC-004 / AC-005 / AC-007 | S03 | design explicit scaffold block and ordinary-word non-block regression |
| C-004 | AC-006 | S04 | generic evidence-readiness hook test or inspected no-op rationale showing G3 policy remains out of R0 |
| C-090 | docs parity | S90 | provider / dogfooding docs inspection and validate |
| C-095 | reviewer gate | S95 | fresh `spec-reviewer` pass |
| C-099 | final handoff | S99 | focused tests, validate, report evidence, commit candidate |

### Plan Amendment Trigger

- 実装中に grade-aware evidence policy、delegated specialist rule、draft routing、または integrated smoke ownership の変更が必要になった場合は、この Issue で吸収せず、G1〜G4 の planning に戻す。
- Existing tests が R0 の AC を十分に覆っている場合は、new test を追加しない no-op を許可する。ただし report に既存 test 名と coverage reason を記録する。

## 8. Epic branch baton / PR policy

- この Issue では個別 PR を作成しない。
- M99 は `iss-00252` に渡せる local closure checkpoint とする。
- PR Delivery Gate / Merge Preparation Gate はこの Issue では実行せず、G4 完了後の Epic 最終品質ゲートに集約する。
- M99 通過後、readiness classifier 修正、regression tests、report evidence を commit し、その HEAD から `iss-00252` の branch を開始する。
- 未完了差分、失敗テスト、未記録の検証結果を次 Issue に混ぜない。
