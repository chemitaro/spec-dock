---
種別: レポート（Issue）
ID: "iss-00554"
関連GitHub: ["#554"]
最終更新: "2026-11-04"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

ダッシュボードに人のタスクの API と画面を足し、構造の図・ボード・Scope の詳しい画面・横断の概況に、人が止めている印と数を出した（epic-00547 R-12、R-13。設計 D-16、D-11）。見るだけで、書く口・完了のボタン・写せるコマンドは置いていない。

- サーバー：`application/dashboard_todos.py`（カタログの選び方、読み取りの覚え、印、revision の署名）。`todo list --all-repositories` の本体を `todo_aggregate.collect` に切り出し、CLI とサーバーで共有（CLI の出力は不変。#550 のテストがそのまま通る）。`domain/todo_model.scope_marks` を足した。
- API：`GET /api/v1/todos[?status=]`、`/api/v1/todos/revision`、`/api/v1/r/<repo>/todos[?status=]`、`/api/v1/r/<repo>/todos/<ID>`。`structure` の Scope ごとに `todos: {blocking, blocking_with_descendants, related}` と上の `todos` の要約（`dashboard summary` と同じ数）、`scopes/<ID>` に `todos: {status, problem, blocking, related, descendants}`。
- 画面：`/todos`、`/r/<repo>/todos`、`/r/<repo>/todos/<ID>`（`views/todos.js`、`views/todos/logic.js`、`views/todos.css`）。上の帯に「人のタスク」のタブ（リポジトリのない道は「横断の概況」「人のタスク」の2つ）。構造の図の箱と枠、ボードのカード、詳しい画面の見出しに「人 n」（Epic と Initiative は「配下も」）。詳しい画面に「人のタスク」のタブ。横断の概況の札に「人のタスク n」「期限切れ m」。
- revision：`todos/`、年月のディレクトリ、`settings.json`、カタログ自身、利用者の設定の署名と、今の時刻で決まる組（期限切れ・期限間近・延期明け）を入れ、書き込みがなくても期限を過ぎれば画面が描き直される。

### 仮の判断（統括に確かめずに進めたもの）

- 詳しい画面に Markdown を描く道具がないため、本文は「先にすべてエスケープしてから、段落・箇条・コード・太字・`http(s)` のリンクだけを描く」小さな関数で描いた（生の HTML を通さない）。
- 横断の画面の更新のため `/api/v1/todos/revision` を足した（契約にしない）。
- 一覧の API は、読めないリポジトリがあっても 200 で、その行を契約どおり `status: unreadable` にする。503 は1件の要求だけ。
- 横断の概況の札は札全体がリンクなので、人のタスクの画面へのリンクは札の中に置かず、上の帯のタブから入る。

## 次の版の移行の注記に要る契約の変更

- 足すだけ。公開の契約に足すもの：`GET /api/v1/todos`、`GET /api/v1/r/<repo>/todos`（中身は `specdock.todo-list/v1`、`?status=open|snoozed|done|cancelled|all`、既定 `open`、ほかの値は 400 `DASHBOARD_TODO_FILTER_INVALID`）、`GET /api/v1/r/<repo>/todos/<ID>`（`todo show` と同じ1件の形。404 `TODO_NOT_FOUND`／`TODO_INVALID`、409 `TODO_RECORD_INVALID` など、503 カタログが読めない）。画面の道 `/todos`、`/r/<repo>/todos`、`/r/<repo>/todos/<ID>`。
- 契約にしないもの：`/api/v1/todos/revision`、`structure`・`scopes/<ID>` の `todos` の項目。`revision` の値は変わる（意味は同じ）。
- CLI、カタログの形式、`specdock.dashboard-summary/v1`、配布する文書と `static-inventory.json` は変えていない。

## Verification

- 仕様のレビュー（spec-reviewer opus/high）：round-1 で pass（P0/P1 なし。P2 3件・P3 1件は設計と計画に取り込んだ。`.workbench/spec-review/iss-00554/`）。
- コードのレビュー（code-reviewer opus/high、標準と仕様の2人）：9e6d716c6 で2人とも pass（P0/P1 なし）。P2 2件（経緯の言葉の鍵、`todos/` のないカタログの覚え）を 7fe233237 で直し、テストを足した。
- 全体のテスト（7fe233237）：`uv run pytest` 3626 passed、7 skipped。`make lint`（ruff、format、mypy）pass。
- PC のヘッドレス Chrome（一時の状態の置き場 `.workbench/shots/env` に2つのリポジトリと8件のタスクを置き、このブランチのコードでサーバーを立てた。利用者の常駐のサーバーと `~/.local/state/spec-dock/` は使っていない）：全リポジトリ・リポジトリごと・1件・構造の図・ボード・Issue と Epic の詳しい画面のタブ・横断の概況の8画面を、PC 幅（1440px）と 390px、明るい・暗いで写した（32枚）。どの画面も横にはみ出さない（`scrollWidth - clientWidth = 0`）。期限切れは赤い帯・記号・「期限切れ（n時間超過）」で先頭の組に出る。構造の図の Issue の箱に「人 1」、Epic・Initiative の枠に「人 n 配下も」が出る。コンソールの誤りは、最初の画面の `/favicon.ico` の 404 だけ（既存の動き。推定）。
- 写し：この Scope の `artifacts/`（`*--todos-all-pc-light.png` など32枚と `*--screenshots-report.json`）。
- iPhone の Safari での確かめ：未実施（統括が利用者に頼む）。

## 最終品質ゲート

- 合格：7fe233237（campaign `iss-00554-01`、attempt 01。closure は `.workbench/final-quality-gate/iss-00554-01/closure.md`）。
- 審査（quality-gate-reviewer opus/high、1人）：pass、網羅 complete、P0 0・P1 0・P2 0・P3 1（画面側の『人のタスクが読めない』表示（横断の概況の札、詳しい画面のタブ）を確かめるものがない。情報のみ）。
- テスト：`make lint` exit 0（ruff check、format、mypy pass）、`uv run pytest` exit 0（3626 passed、7 skipped）。同じコミット。
- ChatGPT のスキルは無効のため、補助の側はなし。

## Residual Risks / Follow-ups

- iPhone の Safari での確かめ（統括が利用者に頼む）。
- 本文の Markdown は小さな関数で描くため、表や入れ子の箇条は文字のまま出る。
- 上の帯のタブが4つになった。390px では収まることを写しで確かめた。
