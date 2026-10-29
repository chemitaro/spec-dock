---
種別: 実装計画書（Issue）
ID: "iss-00438"
タイトル: "Regenerate Dashboard From Structure Snapshot"
関連GitHub: ["#438"]
状態: "draft"
最終更新: "2026-10-29"
依存: ["requirement.md", "design.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00438 Regenerate Dashboard From Structure Snapshot — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

- **standard**（Epic の計画の選択のまま）。
- 理由：書くのは、Git で無視されるダッシュボードの5つのファイルと、状態の置き場の `state.json` の `dashboard` だけで、利用者の仕様、カタログ、GitHub には書かない。版4のリポジトリは I-10 まで利用者の環境にないので、失敗しても PR の revert で戻る。
- risk factor：C10 の形（`created_at`、`closed_at`）は epic-00427 が読む契約になる。描く関数は従来モードと共有のコードである。I-5 と同じファイルを変える。
- 再評価の条件：C9、C10、着手の判定の部品の公開の形を、項目の追加のほかに変える必要が出たとき、従来の出力が変わる必要が出たときは、統括に聞き、strict に上げるかを決める。

## 目標

requirement.md の AC-438-01〜11 を満たし、PR をマージできる状態（CI が通っている）で止まる。

## 順序・依存

- 前提：I-1〜I-4、I-7、I-8 が `main` にある（`cee4c896b`）。2026-10-29 に、I-14（PR #459）と I-16（PR #461）を含む `origin/main`（`a23d7d175`）をマージで取り込んだ（`bf9442a62`）。
- 並行：I-5（`iss-00432`）が別のworktreeで進む。`domain/canonical_structure.py`（`ScopeNode`、`IssueFacts`）、`infra/github_structure.py`、`application/canonical_status.py`、`cli/catalog.py`、`tests/support/fake_github.py` で衝突しうる。先に `main` に入った方を、`origin/main` のマージで取り込む（rebase しない）。
- この Issue の中の順：S1（C10）→ S2（入力の辞書と描く関数）→ S3（書く部品と手順7）→ S4（status と remove）→ S5（全体）。S2 は S1 の `ScopeNode` に依存しない部分から始めてよい。

## 実装step

テストを先に書き（`tdd`）、区切りのよいところでコミットする。

- **S0 文書**：requirement、design、plan を書き、この会話を知らないサブエージェントにレビューさせ、指摘を分析して直す。見本の5つのファイルを `tests/fixtures/issue438/legacy-dashboard/` に写す（元は変えない）。
- **S1 C10 の時刻**（AC-438-01）：偽の `gh` に `created_at` と `closed_at`、`IssueFacts`、`ScopeNode`、JSON の読み書き、GraphQL の問い合わせと REST の読み取り。古い形の取り直しと、要求の数のテスト。既存のテストの `IssueFacts(...)` と `ScopeNode(...)` を直接作る箇所に、新しい引数を足す。
- **S2 入力の辞書と描く関数**（AC-438-02、03、09）：`presentation/puml.py` の `board_state`（従来の出力が変わらないテストを先に）、`domain/canonical_dashboard.py`、`render_dashboard_files`。見本との比較のテスト。
- **S3 書く部品と手順7**（AC-438-04〜06）：`application/canonical_dashboard.refresh_dashboard`、`refresh_structures` の変更、`canonical_errors` のコード、`canonical sync` のヘルプ。I-3 の `dashboards_written` のテストを直す。
- **S4 status と remove**（AC-438-07、08）：`SyncView.dashboard_item()`、`canonical remove` の手順、ヘルプ。
- **S5 全体**（AC-438-10、11）：`make lint`、`uv run pytest`。`git diff origin/main -- tests/` で変えた既存のテストを一覧にし、版3のテストがないことを確かめる。
- **S6 実装のレビュー**：`code-review` の観点で、規約と仕様を、独立した2つのサブエージェントにレビューさせ、指摘を `analyze-review-findings` で分析して直す。
- **S7 最終品質ゲート**：`origin/main` をマージし、すべてをコミットして通常の push をし、その SHA で `make lint` と `uv run pytest`、新しい2つのサブエージェントのレビュー（規約と仕様）。指摘を直したら、新しい SHA でやり直す（レビューは前のゲートからの差分と、前の指摘が直ったことに絞る）。
- **S8 報告と PR**：`report.md` を書き、`github-pr-creator` で PR を作り、`github-pr-checks` で CI を確かめる。マージはしない。`work finish` は実行しない。

## 検証

| AC | 確かめ方 |
|---|---|
| AC-438-01 | `tests/unit/domain/test_canonical_structure.py`、`tests/unit/infra/test_github_structure.py`、`tests/unit/infra/test_github_snapshot.py`（偽の `gh` の記録で GraphQL の要求の数を比べる。古い形の `snapshot.json` を置いて取り直し） |
| AC-438-02 | `tests/unit/application/test_canonical_dashboard_golden.py`（見本との比較、日本語と `"` の題名） |
| AC-438-03 | `tests/unit/domain/test_canonical_dashboard.py` と、周期のテストの中身の確かめ |
| AC-438-04〜08 | `tests/cli_runtime/test_issue438_canonical_dashboard.py`（`SyncPair`、偽の `gh`、一時の状態の置き場、更新の時刻と中身の比較） |
| AC-438-09 | `tests/unit/presentation/test_dashboard_board_state.py`（変更の前の関数の写しとの比較）と `tests/unit/presentation/` の今のテスト |
| AC-438-10 | 版3のテストが変更なしで通る。`git diff origin/main --stat -- tests/` の確認 |
| AC-438-11 | `make lint`、`uv run pytest` |

- 実機の確かめ：この Issue は launchd と systemd に触れない（手順7の中の処理だけ）。I-3 の周期の上で動くことは、CLI のテストで確かめる。spec-dock の本物のmainのチェックアウトでの確かめは、I-10 の AC-17 で統括が行う（この Issue では「未確認」と報告書に書く）。

## 安全と運用

- security：秘密情報を扱わない。書く先は、Git で無視されるmainのチェックアウトの5つのファイルと、利用者ごとの状態の置き場だけで、一時ファイルはリンクをたどらずに作る（`O_NOFOLLOW`、`O_EXCL`）。書く場所のシンボリックリンクとディレクトリは触れない。
- operability：失敗は `state.json` の `dashboard.error` と `canonical status` の `dashboard` に出る。同期の結果は変えない。手で直すことは、示したパスの退避だけである。

## 残るリスク

- 見本は2026-09-21 の spec-dock の状態で、BLOCKED、DOING、依存の辺を含まない。それらの形は従来の規則から書いた単体のテストでだけ確かめる。
- I-5 と同じファイルを変えるので、後に入る方のマージで衝突しうる。
- 実機（spec-dock の本物のmainのチェックアウト）での確かめは I-10 で行う。

## rollback

- PR を `git revert` する。足した `snapshot.json` の項目は、戻した版の形の検査で落ちて取り直される。ダッシュボードのファイルは Git で無視されるので、残っても害はない。

## exit / handoff

- 完了：AC-438-01〜11 を満たし、最終品質ゲートに合格し、PR の CI が通り、`report.md` を書いた。PR はマージできる状態で止め、マージは人が行う。`work finish` はマージの後に統括が指示する。
- 引き渡し：
  - 統括：Epic の12章のエラーのコードの表に `CANONICAL_DASHBOARD_OCCUPIED` と `CANONICAL_DASHBOARD_FAILED` を足すこと。
  - 統括：Epic の13章の「作り直す時」の SHA-256 の範囲を、`issues` と `external` に、異常の一覧、描く形の版、スナップショットのパスを足したものに直すこと（文書のレビューの DR-6、DR-13。異常だけの変化で状態が変わるのに書き直さない抜けを防ぐ）。
  - I-9：使う側の文書（`spec-dock/docs/canonical.md`）のダッシュボードの節（置き場、新しさ、`canonical status` の `dashboard`、2つのコード）。
  - I-10：spec-dock のmainのチェックアウトで、最初の周期が2026-09-21 の5つのファイルを置き換えることの確かめ（AC-17）。
  - epic-00427：`snapshot.json` の `created_at` と `closed_at`（版1）。

## 統括の判断

- **2026-10-26（Orca の ask への回答）**：
  1. `state.json` の `dashboard.error` は null か `{code, message, at, paths}`。コードは `CANONICAL_DASHBOARD_OCCUPIED`（書く場所にディレクトリかシンボリックリンク）と `CANONICAL_DASHBOARD_FAILED`（スナップショットがない、mainの `spec-dock/` がない、書き込みの失敗）の2つ。`canonical status` の `dashboard` は、`error` があれば `problem` にし、警告（終了コード0）にする。Epic の12章への追記は統括が後で行う。
  2. 作業中を複数の Issue で示すため、`presentation/puml.py` の `_issue_ready_board_state` に `board_state` の分岐を足す。従来の呼び出しの出力が変わらないことをテストで確かめる。
  3. 手順7のダッシュボードは、カタログごとに `cycle.lock` を取り（取れなければ今回は飛ばす）、`--registered` のときは登録簿から外れたカタログを飛ばす。mainのチェックアウトの宣言が canonical でないときと、作業用のworktreeでは書かない。
  4. 構造の SHA-256 が変われば5つを書き直し、同じなら欠けたものだけを書く。
  5. Observability の行は、構造のスナップショットの絶対パスでよい（Git で無視されるファイルなので、コミットされない）。
- **2026-10-29（方針の変更。Epic の `plan.md` の I-11 の節と再開の依頼）**：slug、本文の印、入れ子の置き場がなくなり、置き場は `<区切り>/<ID>/` になった。上の1〜5は、どれも slug とディレクトリに頼らないので、新しい方針と食い違わず、そのまま正とする。変わったのは次の2つである。
  - 全体を読む問い合わせから `body` が外れた（I-14）。取り込みでは `createdAt` と `closedAt` だけを残した。テストの `fake.scope(slug=…)` の引数を外した。
  - 印のない、種類のラベルの付いた Issue も ID を持ち、ダッシュボードに出る。種類の付け替えは、GitHub の今の種類と ID で示す。見本との比べ合わせの期待値は変わらない。
  - 再開の時点で S0〜S4 は済んでおり（`c9ebdf34b`）、S5 から続ける。
