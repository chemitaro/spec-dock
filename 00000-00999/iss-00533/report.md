---
種別: レポート（Issue）
ID: "iss-00533"
関連GitHub: ["#533"]
最終更新: "2026-11-04"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

epic-00427 の D-10／R-23 のとおり、定期の同期が main のチェックアウトの `spec-dock/` に書いていた Markdown と PlantUML のダッシュボード（`dashboard.md`、`tree.puml`、`tree-all.puml`、`deps-issues.puml`、`deps-raw.puml`）の生成と、それに付いた契約を撤去した。

- 消したコード：`application/canonical_dashboard.py`、`domain/canonical_dashboard.py`、`presentation/markdown.py`、`presentation/puml.py`、`canonical_sync._refresh_dashboards` とその呼び出し、`SyncView.dashboard_item`、`CanonicalStatusData.dashboard`、`CANONICAL_DASHBOARD_OCCUPIED`／`CANONICAL_DASHBOARD_FAILED` と3つの次の1手の文、`canonical remove` の `canonical.dashboard.remove` の手順、`CatalogSyncState.dashboard`、未使用になった `infra/canonical_files.py` の `FileOccupied`／`is_regular_file`／`replace_text_file`／`_occupied_at`、未使用の `asset_layout.LEGACY_WORKBENCH_IGNORE`。
- 配布資産：`spec-dock/.gitignore` から5つの名前を外し、`docs/canonical.md` から `dashboard` の項目、5つのファイルの段落、`CANONICAL_DASHBOARD_*` の2行を消した（節の名前は「構造のスナップショット」）。`static-inventory.json` の2行の sha256 を新しくし、前の sha256 を `known_old_sha256` に足した。dogfood の写し（`spec-dock/.gitignore`、`spec-dock/docs/canonical.md`）を提供側と同じにした。`reference_cli.md` と `cli-redesign-guide.html` は5つのファイルを記述していないので変えていない（#530 と衝突しない）。
- CLI の説明（`catalog.py`）：`canonical status` の JSON の項目、`canonical sync` の書くもの、`canonical remove` の書くものから5つのファイルを外し、`dashboards_written` に「always 0; kept for compatibility」を添えた。
- テスト：`tests/cli_runtime/test_issue533_dashboard_removal.py`（T-01〜T-07）を足し、wheel のテストの「入らないモジュール」に4つを足した。iss-00438 のテスト5本と fixture `tests/fixtures/issue438/` を消し、`test_issue429_canonical_status.py`、`test_issue430_canonical_sync.py`、`test_issue430_legacy_and_public.py`、`test_canonical_sync_state.py`、`test_issue436_docs.py` を直した。

### 判断

- 統括の決定 (A)（2026-11-04）：`canonical sync` の `repositories[].dashboards_written` は、Epic の「ほかのコマンドの契約は変えない」を優先して項目を残し、常に0を返す。後の版で消す予定。
- `state.json` の版（`STATE_VERSION`）は変えない。古い `dashboard` の欄は形を問わず読み飛ばし、次に書くときに落とす。前の版は欄がなければ `None` として読むので、版を戻しても読める。

### 0.6.0 の移行の注記に要る契約の変更（#534 へ）

- `canonical status` の JSON から `dashboard` の項目が消える（11項目）。`CANONICAL_DASHBOARD_OCCUPIED`／`CANONICAL_DASHBOARD_FAILED` の警告が出なくなる。
- `canonical remove` は5つのファイルを消さない（効果 `canonical.dashboard.remove` がなくなる）。
- `canonical sync` の `repositories[].dashboards_written` は常に0（後の版で消す予定）。
- 定期の同期は5つのファイルを作らない。`state.json` に `dashboard` を書かない。
- 配布する `spec-dock/.gitignore` から5つの名前が外れるので、`installation update` の後、利用者のリポジトリに残った `spec-dock/dashboard.md`、`tree.puml`、`tree-all.puml`、`deps-issues.puml`、`deps-raw.puml` が `git status` に出る。SpecDock は消さない。利用者が消してよい。代わりに `spec-dock dashboard serve` と `spec-dock dashboard summary` を使う。

## Verification

- 仕様のレビュー（spec-reviewer opus/high）：round-1 で pass（P0 0、P1 0、P2 2、P3 1）。P2・P3 は仕様に反映した（R-04 の検索の範囲、D-07 のテストの追加、D-02 の関数名）。CUE のファイルは sha256 で固定した。
- コードのレビュー（code-reviewer opus/high、基準と仕様の2人、06be6b5c）：どちらも pass。仕様の観点は指摘なし。基準の観点の P3 2件（未使用になった `canonical_files` の書き込みの部品、`canonical_status.py` の古い docstring）を af3a2dd6 で直した。
- 1回目の全体の実行（06be6b5c）で見つかった `test_issue436_docs.py` の節の名前と、新しいテストの整形を af3a2dd6 で直した。
- 最終品質ゲート（campaign `iss-00533-r1`、quality-gate-reviewer opus/high 1人）：
  - attempt 01（af3a2dd6）：レビュー pass（P0〜P3 なし）、`make lint` 0、`uv run pytest` 0（3421 passed、7 skipped）。
  - `origin/main`（#531、PR #542、dca159aaf）を取り込んだ（衝突なし、ファイルの重なりなし）ので、最終のコミットでやり直した。
  - attempt 02（**0a57b825b98853184fe4a1d9c7869a7c4b61658b**、最終）：レビューのレーン pass（P0〜P3 なし、網羅完了：functional-correctness、requirements-closure、test-adequacy）。テストのレーン：`make lint` 終了コード0（ruff check、ruff format check、mypy が pass）、`uv run pytest` 終了コード0（3448 passed、7 skipped、26分13秒）。
  - 証拠：`.workbench/final-quality-gate/iss-00533-r1/closure.md`（作業ツリーの Git 管理外）。
- PR #541（https://github.com/chemitaro/spec-dock/pull/541）：head 0a57b825 で CI（SpecDock check、Commit identity、Provider CI）が success、GitHub の状態は MERGEABLE／CLEAN（2026-11-03T20:41:56Z の観測。Actions と Commit Status の範囲）。
- `spec-dock scope check iss-00533`：valid、誤り0、指摘0。

## Residual Risks / Follow-ups

- `dashboards_written` の項目の削除は後の版の課題。
- この dogfood のリポジトリの main のチェックアウトに残った5つのファイルは、カタログの仕様ではないので触れていない。0.6.0 の導入の後に消してよい。
