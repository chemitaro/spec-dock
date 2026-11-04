---
種別: レポート（Issue）
ID: "iss-00550"
関連GitHub: ["#550"]
最終更新: "2026-11-04"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

このPCの登録簿にある全リポジトリの人のタスクの集約と、`dashboard summary` の人のタスクの数を足した。公開のコマンドの数（71）は変えていない。

- `todo list --all-repositories`／`--repository R`（くり返し可、`--all-repositories` を含む）：登録簿の全行のカタログの `todos/` を、チェックアウトもサーバーもなしに読み、`specdock.todo-list/v1` の `mode: all_repositories` で返す。並びは D-08 と同じで、リポジトリをまたいで1つに並べる。
  - 行の `status`：`ok`、`unreadable`（カタログか `todos/` が読めない。`problem` と次の1手 `spec-dock --project <main_checkout> canonical link`、警告 `TODO_REPOSITORY_UNREADABLE`）、`duplicate`（同じリポジトリの2つ目のクローン。`main_checkout` の順で最初の行だけを読む。警告 `TODO_REPOSITORY_DUPLICATE`）。`unreadable`／`duplicate` の `counts` は null。
  - 隠したリポジトリも `hidden: true` で返す。`repository` が null の行は `repository`／`ref` が null。登録簿にない `--repository` は警告 `TODO_REPOSITORY_UNKNOWN`。登録簿が読めなければ `TODO_REGISTRY_UNREADABLE`（3）、REPOSITORY の形の誤りは `TODO_REPOSITORY_INVALID`（2）。
- `todo show <REF>`（`owner/name/t-xxxx`、`github.com/owner/name/t-xxxx`、サブタスクの ID も可）：チェックアウトの外で、登録簿のそのリポジトリのカタログから1件を返す。
- `dashboard summary` の `todos: {status, open, blocking, overdue, problem}`：親のタスクだけを数える（`open` は延期中を含む）。チェックアウトの中でリンクが正しければそのカタログ（`--no-schedule` でも数が出る）、ほかは登録簿のカタログ。読めなければ `status: unavailable` で、要約は成功する。サーバーの `/api/v1/r/<repo>/summary` も同じ選び方と数え方（`registry_summary_todos`）で同じ数を返す。
- 部品：新しい `application/todo_aggregate.py`。iss-00549 の `classify`／`load_record` を `TodoStore` で受ける形に割り、`show_from_store`、`counts_of`、`todo_model.tally`、`todo_document.repository_row` を共有した（チェックアウトの道の振る舞いは変えていない）。
- 文書：`reference_cli.md`（C54、C63、C64、要約の契約の表の `todos`、人のタスクの契約の節の冒頭・一覧の説明・エラーと警告）、ヘルプ（葉の要約、前提、読むもの、JSON の説明、対象）。dogfood の写しと `static-inventory.json` の1行（sha256 と `known_old_sha256`）を更新した。
- iss-00549 のゲートの P2 の2件：`gh` の stub のテストで `reopen`、`update`、`snooze`、`cancel` も実行する。Scope の判定の文字の確かめに `application/canonical_work.py` を足した。

コミット：`08e764855`（実装）、`1311634a1`（コードのレビューの P3 の修正：`next_step` の道を `shlex.quote` で引用）、`1ee5bee82`（`origin/main` の取り込み。衝突なし）。

### 仮の判断・Epic との違い

- 登録簿にない `--repository` は止めずに警告 `TODO_REPOSITORY_UNKNOWN`（Epic は決めていない。集約の閉じ込めの決まりに合わせた）。
- 2つ目のクローンの行に警告 `TODO_REPOSITORY_DUPLICATE` も出す。`problem` は `{code, message, next_step: spec-dock dashboard list}`。
- `todo show <REF>` で登録簿にないリポジトリは `TODO_REPOSITORY_UNKNOWN`（3）、読めないカタログは `TODO_REPOSITORY_UNREADABLE`（3）。
- `filters` に `repositories`（`--repository` の鍵の配列）を足した（チェックアウトの道では空の配列）。
- サーバーの summary は要求ごとに登録簿とカタログを読む（キャッシュは iss-00554 の D-16）。

## Verification

- 仕様のレビュー（spec-reviewer opus/high）：1回目で合格（P0 0、P1 0、P2 2、P3 0）。P2 の2件（duplicate の行の `problem` の形、文書とヘルプの直す範囲）は仕様に反映した。記録は `.workbench/spec-review/iss-00550/`。
- コードのレビュー（code-reviewer opus/high、規約の面と仕様の面の2人、`1f5c042..08e7648`）：どちらも合格（規約の面は P3 1、仕様の面は指摘0）。P3（`next_step` の道の引用）は `1311634a1` で直し、テストを足した。記録は `.workbench/code-review/iss-00550/`。
- 最終品質ゲート（quality-gate-reviewer opus/high、1人、`1ee5bee82`、base は `origin/main` との merge-base `233008513`）：
  - レビューの側：合格。範囲を見終え（coverage_complete）、P0 0、P1 0、P2 0、P3 2。
  - テストの側：合格。`make lint` は終了コード0。`uv run pytest` は終了コード0（3602 passed、7 skipped、27分36秒）。
  - 記録は `.workbench/final-quality-gate/iss-00550-g1/closure.md`。ChatGPT のレーンは使っていない（無効）。
- `spec-dock scope check iss-00550`：誤り0、警告0。
- PR：https://github.com/chemitaro/spec-dock/pull/559（head `1ee5bee82`）。CI（Provider CI、Commit identity、SpecDock check）はすべて success、GitHub は MERGEABLE／CLEAN（2026-11-04T05:47Z の観測。Actions と Commit Status だけを見た）。マージは利用者が行う。

## Residual Risks / Follow-ups

ゲートの情報だけの指摘（直していない）：
- P3：集約の `items` の同順位（同じ組・同じ期限・同じ作った時刻）の並びが、設計の「リポジトリの鍵、道の順」ではなく記録の ID で決まる。
- P3：テキストの出力の `duplicate` の行の書式が、設計の `<repo>: duplicate (reads <カタログ>)` と少し違う（`<repo>: duplicate <カタログ> (<message>)`）。

- 登録簿は PC ごとで、`canonical link --no-schedule` のカタログは集約に入らない（文書に書いた）。

次の版の移行の注記に要る契約の変更（iss-00553 の `migration.md` 向け）：
- `specdock.todo-list/v1` に `mode: all_repositories`、`repositories[].status` の `unreadable`／`duplicate`、`filters.repositories` が足される（版は変えない）。
- `specdock.dashboard-summary/v1` に `todos` が足される（版は変えない）。`dashboard summary` は登録簿とカタログの `todos/` も読む（何も書かない）。サーバーの summary の API も同じ `todos` を返す。
- 新しい引数：`todo list --all-repositories`、`--repository`。`todo show` が `REF` を受ける。コマンドの数は71のまま。
- 新しいエラー・警告のコード：`TODO_REGISTRY_UNREADABLE`、`TODO_REPOSITORY_INVALID`、`TODO_REPOSITORY_UNKNOWN`、`TODO_REPOSITORY_UNREADABLE`、`TODO_REPOSITORY_DUPLICATE`。
- 配布の文書 `reference_cli.md` が変わった（各リポジトリでは `installation update` で入れ替わる）。
