---
種別: レポート（Issue）
ID: "iss-00438"
タイトル: "Regenerate Dashboard From Structure Snapshot"
関連GitHub: ["#438"]
最終更新: "2026-10-29"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00424", "init-00423"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

- **C10 の時刻**（AC-438-01）：構造のスナップショットの `issues` の各要素に `created_at` と `closed_at` を足した（`IssueFacts`、`ScopeNode`、`_NODE_KEYS`、JSON の読み書き、全体を読む GraphQL の `createdAt closedAt`、REST の読み取り）。版は1のまま。2つの項目がない版1のファイルは、鍵の集合が合わずに取り直される。要求の数は変わらない。
- **入力の辞書と描く関数**（AC-438-02、03、09）：`domain/canonical_dashboard.py` が、スナップショットと I-4 の `evaluate_all` から、今の描く関数（`presentation/markdown.py`、`puml.py`）の入力を作る。作業中を複数の Issue で示すため、`_issue_ready_board_state` に `board_state` の分岐を足した（従来の呼び出しの出力は変わらない）。
- **書く部品と周期の手順7**（AC-438-04〜06）：`application/canonical_dashboard.py` の `refresh_dashboard`。カタログごとに `cycle.lock` を取り、mainのチェックアウトにだけ、構造の SHA-256 が変わったら5つを、同じなら欠けたものだけを、`infra/canonical_files.replace_text_file`（ディレクトリの記述子に固定、`O_EXCL | O_NOFOLLOW` の一時ファイル、fsync、rename）で書く。ディレクトリかシンボリックリンクのある場所は書かずに `CANONICAL_DASHBOARD_OCCUPIED`、スナップショットがない・mainの `spec-dock/` がディレクトリでない・書き込みの失敗は `CANONICAL_DASHBOARD_FAILED` を `state.json` の `dashboard.error` に記録する。作業用のworktree、版3の main、登録簿から外れたカタログ、`state.json` がないときは書かない。
- **`canonical status` と `canonical remove`**（AC-438-07、08）：`dashboard` の項目（`ok`、`missing`、`problem`、`not_applicable`）と、5つのファイルの削除（`--yes` なしは予定だけ。ディレクトリとリンクは消さない）。
- **2026-10-29 の方針の変更への対応**：`origin/main`（I-14、I-16 を含む `a23d7d175`）をマージで取り込んだ（`bf9442a62`）。衝突は2つ（全体を読む問い合わせから `body` を外し `createdAt closedAt` を残す、`canonical_status.py` の docstring）。テストの `fake.scope(slug=…)` を外した。ダッシュボードは ID とスナップショットの `parent` だけを使い、ディレクトリに頼らないので、描く部分に変更は要らなかった。前の担当の未コミットの変更はなく、捨てたものはない。
- 実現しなかったもの：なし。

### この Issue が変えた既存のテスト（AC-438-10）

版3のテストは変えていない。変えたのは canonical のテストだけである。

- `tests/cli_runtime/test_issue429_canonical_status.py`：`dashboard` の `not_implemented` を、GitHub のリポジトリがないときの `not_applicable` に。
- `tests/cli_runtime/test_issue430_canonical_sync.py`：最初の周期の `dashboards_written` を 0 から 1 に。
- `tests/unit/domain/test_canonical_readiness.py`、`tests/unit/domain/test_canonical_structure.py`：`ScopeNode` と JSON に `created_at`、`closed_at` を足した。
- `tests/unit/infra/test_github_snapshot.py`：時刻の項目のテストを足し、取り込みで `fake.scope(slug=…)` を外した。
- `tests/support/fake_github.py`：偽の `gh` に `created_at`、`closed_at`。

## Verification

### 最終品質ゲート（Claude だけのゲート。ChatGPT のゲートは利用者の設定で無効）

- **ゲート1**（SHA `730dbbb6a08bd05855f8a8e77b7453e599b0e612`、push 済み）
  - `make lint`：終了コード0（ruff check、ruff format、mypy すべて pass）。
  - `uv run pytest`：終了コード0、3087 passed、8 skipped（993.65s）。
  - レビュー（`code-reviewer`、opus/high、`origin/main...730dbbb6a` の全差分）：Standards は pass（P3 が1件：設計書の手順5の一時ファイルの書き方が実装と違う）。Spec は pass（P2 が1件：mainの `spec-dock/` がない・ファイル・リンクのとき、宣言を読めずに `legacy_mode` で黙って飛ばし、R-438-04 の `CANONICAL_DASHBOARD_FAILED` を記録しない）。
  - 対応：どちらも `analyze-review-findings` で根拠を確かめた。P2 は implementation-remediation（`spec-dock/` が（リンクでない）ディレクトリのときだけ宣言で従来モードと判定する。3つの場合の周期のテストを Red → Green で足した）。P3 は documentation-correction。ゲートの規則では P2/P3 は止めないが、要件の明示の違反なので直した。
- **ゲート2**（SHA `3df18e6f69f9e5d2d314ed4abeb4cc251d71a28e`、push 済み）
  - `make lint`：終了コード0（ruff check、ruff format、mypy すべて pass）。
  - `uv run pytest`：終了コード0、3090 passed、8 skipped（983.79s）。合格。
  - レビュー：全体の差分はゲート1で2つのレビューを通っているので、新しい2つのレビューアー（opus/high）に、`730dbbb6a..3df18e6f6` の差分と前の指摘が直ったことの確かめに絞って頼んだ。Standards、Spec とも pass（P0〜P3 なし）。P3 と P2 が直り、版3の main（AC-438-06）、作業用のworktree、従来モード（AC-15）が変わらないことを確かめた。
- ゲート2の後のコミットは、この `report.md` だけである（コードに触れないので、ゲートはやり直していない）。

### そのほか

- 文書のレビュー：前の担当が S0 で、この会話を知らないサブエージェントのレビューを済ませた（DR-6、DR-13 など。plan.md の引き渡しに反映）。再開での文書の変更は、方針の変更の記録だけで小さいので、文書のレビューはやり直していない。
- 実装のレビュー（手順6）は、最終品質ゲート1の2つのレビューに兼ねさせた（トークンの節約。同じ観点を同じ差分に重ねないため）。
- 実機：この Issue は launchd と systemd に触れず、周期の中の処理だけなので、I-3 の `SyncPair` と偽の `gh` の CLI のテストで確かめた。

### 未確認

- spec-dock の本物のmainのチェックアウトで、最初の周期が2026-09-21 の5つのファイルを置き換えること（AC-17。I-10 で統括が確かめる）。
- Linux（systemd）の上の周期での動作（CI の Linux の実行を除く）。

## Residual Risks / Follow-ups

- 見本は2026-09-21 の状態で、BLOCKED、DOING、依存の辺を含まない。それらの形は従来の規則から書いた単体のテストでだけ確かめた。
- I-5（`iss-00432`）が同じファイル（`ScopeNode`、`canonical status`、`cli/catalog.py`）を変える。後に入る方が `origin/main` のマージで取り込む。
- 統括への引き渡し：
  - Epic の12章のエラーのコードの表に `CANONICAL_DASHBOARD_OCCUPIED` と `CANONICAL_DASHBOARD_FAILED` を足す。
  - Epic の13章の「作り直す時」の SHA-256 の範囲を、`issues` と `external` に、異常の一覧、描く形の版、スナップショットのパスを足したものに直す。
  - I-9：使う側の文書のダッシュボードの節。I-10：AC-17 の確かめ。epic-00427：`snapshot.json` の `created_at` と `closed_at`（版1）。
