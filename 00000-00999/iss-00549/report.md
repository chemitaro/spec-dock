---
種別: レポート（Issue）
ID: "iss-00549"
関連GitHub: ["#549"]
最終更新: "2026-11-04"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

人のタスクの記録 `specdock.todo/v1` と、`spec-dock todo` の10のコマンド（集約なし）を足した。公開のコマンドは61から71になった。

- 記録はカタログの `todos/<YYYY-MM>/t-xxxx.json` に1件1つ。GitHub には要求を送らない。閉じてもファイルは動かさない。
- 書く前に Python の型（`domain/todo_record.validate`）で確かめる。`todo check` は、Python の検査に加えて `cue vet`（`src/spec_dock/cue/todo/v1/todo.cue` の `#Records`／`#Todo`）でも確かめる。`tests/fixtures/todo/` の見本（正しいもの8件、誤ったもの33件）で、2つの型がファイルごとに一致することをテストで縛った。
- サブタスク（1段）、会話の束（`checklist --item`）、期限・延期・並び・派生の状態、件数の警告、3段の設定（初めの値 < `$XDG_CONFIG_HOME/spec-dock/config.json` < `todos/settings.json`）と `todo settings`、Scope との結び付き（印だけ）、衝突の写し・ID の重なり・壊れた記録の扱い。
- 文書：`reference_cli.md`（C62〜C71 と契約の節）、`docs/README.md`、`cli-redesign-guide.html`、リポジトリの `README.md`。dogfood の写しと `static-inventory.json` の3行（sha256 と `known_old_sha256`）を更新した。

コミット：`022b5a1b2`（実装）、`9fed37bab`（コードのレビューの指摘の修正）。

### 仮の判断・Epic との違い

- `cue vet` の呼び方：Epic D-05 の「ファイルを並べて渡す」形は、`cue` v0.17.1 では最初に誤ったファイルの誤りしか出ない。そのため、全部の記録を `{カタログからの相対の道: 記録}` の1つの JSON にまとめ、標準入力で `#Records` に渡す形にした。さらに `cue` は、ほかの誤りがある実行では「欄がない」の誤りを出さないので、まだ誤りの出ていない記録だけで繰り返す。統括が了承し、Epic D-05 は統括が直した。
- CUE の型の欄は、値が null でよいものも含めて必須（`!`）にした。Python も、v1 の鍵がそろっていることを確かめる（2つの型を一致させるため）。
- サブタスクの `resolution.choice` は null だけとした。`reopen` の経緯の項目には、前の `resolution` を写す。
- 集約の引数（`--all-repositories`、`--repository`）と `todo show <REF>` は、この Issue では足していない（iss-00550 が足す）。

## Verification

- 仕様のレビュー（spec-reviewer opus/high）：1回目で合格（P0 0、P1 0、P2 1、P3 4）。P2・P3 は仕様に反映した。記録は `.workbench/spec-review/iss-00549/`。
- コードのレビュー（code-reviewer opus/high、決まりの面と仕様の面の2人、`ae8c724..022b5a1`）：どちらも合格（決まりの面は P2 2・P3 2、仕様の面は P2 2・P3 5）。P2・P3 はすべて直し、テストを足した（`9fed37bab`）。記録は `.workbench/code-review/iss-00549/`。
- 最終品質ゲート（quality-gate-reviewer opus/high、1人、`9fed37bab`）：
  - レビューの側：合格。範囲を見終え（coverage_complete）、P0 0、P1 0、P2 2、P3 2。
  - テストの側：合格。`make lint` は終了コード0。`uv run pytest` は終了コード0（3583 passed、7 skipped、27分36秒）。
  - 記録は `.workbench/final-quality-gate/iss-00549-g1/closure.md`。ChatGPT のレーンは使っていない（無効）。
- `cue` v0.17.1 の環境で `tests/unit/cue/test_todo_type_parity.py` を通した（Provider CI も固定版の `cue` を入れる）。
- `spec-dock scope check iss-00549`：誤り0、警告0。

## Residual Risks / Follow-ups

ゲートの情報だけの指摘（直していない）：
- P2：「`gh` の stub が呼ばれない」のテストが、`update`、`snooze`、`cancel`、`reopen` を実行していない。
- P2：Scope の判定が変わらないことの文字の確かめが、`canonical_work.py` ではなく `application/work_start.py` を読んでいる（実際のコードは `todo` を参照していない）。
- P3：年が 0000 の時刻だけ、Python は誤りとし、CUE の `#Time` は通す。
- P3：スナップショットにある Scope の ID に `TODO_SCOPE_UNKNOWN` が出ないことを、テストで確かめていない。

次の版の移行の注記に要る契約の変更（iss-00553 の `migration.md` 向け）：
- 公開のコマンドが10増える（61 → 71）：`todo add|list|show|update|done|snooze|cancel|reopen|check|settings`。
- 新しい公開の契約：`specdock.todo/v1`（記録）、`specdock.todo-list/v1`（この版は `mode: repository`）、`specdock.config/v1` の `todo` の節（利用者の設定。SpecDock は作らない）、`specdock.todo-settings/v1`（`todos/settings.json`）。
- カタログに `todos/` ができる（最初の `todo add` が作る）。カタログの形式、`workspace.json` の版、構造のスナップショット、ほかのコマンドの契約は変えていない。
- 配布の文書が変わった（`reference_cli.md`、`docs/README.md`、`cli-redesign-guide.html`）。各リポジトリでは `installation update` で入れ替わる。
