---
種別: 実装計画書（Issue）
ID: "iss-00093"
タイトル: "Automatic Sync After State Mutations"
関連GitHub: ["#93"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-13"
依存: ["requirement.md", "design.md"]
親: ["epic-00090", "init-local-00003"]
---

# iss-00093 Automatic Sync After State Mutations — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001, AC-002, AC-003, AC-004
- EC:
  - EC-001, EC-002, EC-003
- 制約:
  - layered architecture、provider-side source of truth、hermetic tests、sync failure visibility

## マイルストーン一覧
- M1:
  - 対象: post-mutation sync contract
  - 完了条件: common helper / result contract / CLI summary の方針が test で固定される
- M2:
  - 対象: local structure and deps mutations
  - 完了条件: `new` と `deps add/remove` が成功後 artifact を更新する
- M3:
  - 対象: destructive / GitHub state mutations
  - 完了条件: `delete`、`close`、`issue finish` の sync policy と tests が固定される
- M4:
  - 対象: docs and final regression
  - 完了条件: sync reference / command help 影響を解消し、targeted と full regression を通す

## 依存関係から導く実装順序
- step 順序メモ:
  - 先に共通 contract を決める。
  - 次に GitHub に依存しない `new` / `deps` で behavior を固める。
  - 最後に `close` / `issue finish` の GitHub 状態反映を gh stub で固定する。
- step 依存 summary:
  - S01:
    - 依存: 既存 `sync_state` contract
    - unblock: 全 mutation の post-sync 呼び出し
    - 対象ファイル: `application/sync_state.py`, `application/contracts.py`, `presentation/cli_text.py`
  - S02:
    - 依存: S01
    - unblock: local mutation artifact refresh
    - 対象ファイル: `application/create_node.py`, `application/mutate_deps.py`, relevant tests
  - S03:
    - 依存: S01, S02
    - unblock: destructive / GitHub mutation artifact refresh
    - 対象ファイル: `application/delete_node.py`, `application/close_node.py`, `application/issue_lifecycle.py`, relevant tests

## ステップ一覧
- S01:
  - 観測可能な振る舞い: mutation result が post-sync success / skipped / failure を表現できる
  - 依存: なし
  - unblock: S02, S03
  - 対象ファイル: application contract, sync helper, CLI text helper
  - 閉じる要件: AC-004, EC-003
- S02:
  - 観測可能な振る舞い: `new` と `deps add/remove` 後に artifact が更新される
  - 依存: S01
  - unblock: S03
  - 対象ファイル: create/deps use cases, CLI runtime tests
  - 閉じる要件: AC-001, AC-002, EC-001, EC-002
- S03:
  - 観測可能な振る舞い: `delete`、`close`、`issue finish` 後に stale artifact が残らない
  - 依存: S01
  - unblock: S90, S99
  - 対象ファイル: delete/close/lifecycle use cases, gh stub tests
  - 閉じる要件: AC-003
- S90:
  - 観測可能な振る舞い: reference docs / command help の sync timing 説明が実装と一致する
  - 依存: S01-S03
  - 閉じる要件: docs impact
- S99:
  - 観測可能な振る舞い: targeted regression と full relevant regression が成功し、report が実行証跡を持つ
  - 依存: S90

## 要件 ↔ ステップ対応
- AC-001 -> S02
- AC-002 -> S02
- AC-003 -> S03
- AC-004 -> S01
- EC-001 -> S02
- EC-002 -> S02
- EC-003 -> S01

## Spec-Locked Closure Index（仕様固定クロージャ索引）

| id | phase / step | slice | type | spec link | locked expectation | observable input/state | bug class guarded | required | evidence level | closure evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | post-sync failure contract | negative | AC-004, EC-003 | artifact failure is visible and not silently swallowed | artifact writer failure after mutation success | silent stale state | yes | red-required | report step closure |
| tc-002 | S02 | new issue post-sync | acceptance | AC-001 | new node appears in generated index/dashboard without manual sync | `new issue` CLI | manual sync omission | yes | red-required | report step closure |
| tc-003 | S02 | deps mutation post-sync | acceptance | AC-002 | deps projection reflects add/remove without manual sync | `deps add/remove` CLI | stale dependency graph | yes | red-required | report step closure |
| tc-004 | S02 | unchanged deps skip | negative | EC-002 | unchanged mutation does not claim artifact refresh as required work | duplicate `deps add` | unnecessary sync / misleading output | yes | red-required | report step closure |
| tc-005 | S03 | close / finish post-sync | acceptance | AC-003 | linked GitHub close path leaves generated state refreshed according to policy | gh stub close / finish | stale GitHub status | yes | red-required | report step closure |

## 実装ステップ

### S01 — post-mutation sync contract
- behavior slice execution:
  - 許可範囲: result 型、sync helper、CLI text helper、unit / presentation tests
  - 禁止範囲: 各 mutation command への本適用
- 検証:
  - targeted command: `uv run pytest` または該当 unittest module
- step closure contract:
  - closure id: tc-001
  - close 条件: sync failure が result と CLI 出力に残る
  - 残リスク: mutation 本体成功と artifact failure の exit code 方針

### S02 — new and deps mutation post-sync
- behavior slice execution:
  - 許可範囲: `create_node.py`, `mutate_deps.py`, CLI renderer, CLI runtime tests
  - 禁止範囲: GitHub close policy の確定
- 検証:
  - targeted command: `uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_deps.py`
- step closure contract:
  - closure id: tc-002, tc-003, tc-004
  - close 条件: `new` / `deps updated` 後に generated artifact が手動 sync なしで更新される
  - 残リスク: large workspace での sync コスト

### S03 — delete, close, and issue finish post-sync
- behavior slice execution:
  - 許可範囲: `delete_node.py`, `close_node.py`, `issue_lifecycle.py`, gh stub tests
  - 禁止範囲: live GitHub 前提の test
- 検証:
  - targeted command: `uv run pytest tests/cli_runtime/test_delete.py tests/cli_runtime/test_close.py tests/cli_runtime/test_issue_lifecycle.py`
- step closure contract:
  - closure id: tc-005
  - close 条件: destructive / GitHub mutation 後に stale artifact が残らない
  - 残リスク: offline close 後の GitHub state 取得失敗時 UX

### S90 — docs impact resolution / docs refresh
- 対象:
  - `spec-dock/docs/reference_sync.md`
  - command help / workflow docs if they mention manual sync timing
- 対応:
  - 自動 sync 対象 command と手動 sync が残る場面を明記する。
- spec/doc review:
  - reviewer: spec-reviewer
  - pass 条件: docs が実装後の behavior と一致する

### S99 — final quality gate
- branch diff 範囲:
  - runtime application / presentation / tests / docs / issue report
- 必須 validation:
  - targeted runtime tests
  - `python -m unittest discover -v` if feasible
  - `./spec-dock/scripts/spec-dock validate`
- final QA gate:
  - reviewer: qa-reviewer
  - 範囲: Issue 全体の test 十分性と integration test 要否
  - pass 条件: reviewer pass
- final code review ゲート:
  - reviewer: code-reviewer
  - pass 条件: reviewer pass
