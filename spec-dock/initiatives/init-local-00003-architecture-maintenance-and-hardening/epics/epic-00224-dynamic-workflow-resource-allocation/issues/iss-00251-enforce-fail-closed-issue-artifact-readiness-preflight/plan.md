---
種別: 実装計画書（Issue）
ID: "iss-00251"
タイトル: "Enforce Fail Closed Issue Artifact Readiness Preflight"
Issue Grade: "strict"
状態: "draft"
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
| M4 | stale reviewer / missing adoption evidence block を接続 | domain tests |
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
| B-005 | stale reviewer / missing adoption evidence は block reason になる | AC-006 |
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

## 7. Epic branch baton / PR policy

- この Issue では個別 PR を作成しない。
- M99 は `iss-00252` に渡せる local closure checkpoint とする。
- M99 通過後、readiness classifier 修正、regression tests、report evidence を commit し、その HEAD から `iss-00252` の branch を開始する。
- 未完了差分、失敗テスト、未記録の検証結果を次 Issue に混ぜない。
