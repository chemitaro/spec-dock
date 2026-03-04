---
種別: 実装報告書（Issue）
ID: "iss-00012"
タイトル: "メタデータ（meta.json等）をコーディングエージェントから保護するガードレールを追加する"
関連GitHub: ["#12", "https://github.com/chemitaro/spec-dock/issues/12"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-04"
依存: ["requirement.md", "design.md", "plan.md"]
親: []
---

# iss-00012 メタデータ（meta.json等）をコーディングエージェントから保護するガードレールを追加する — 実装報告（LOG）

## 実装サマリー (任意)
- [実装した内容の概要を2-3文で記載]

## 実装記録（セッションログ） (必須)

### 2026-03-04 07:10 - 07:18

#### 対象
- Step: S01
- AC/EC: AC-001, AC-002

#### 実施内容
- Red: `new/import` の既存テストに `_spec_dock` 最小スキーマ検証を追加し、失敗を確認
- Green: `_write_meta()` に `_spec_dock`（`managed/do_not_edit/edit_via`）を追加
- Refactor: 振る舞い変更なし（最小実装のまま）

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.test_cli.TestCli.test_new_initiative_and_epic_default_to_local_even_when_gh_is_available
# FAILED (期待どおり Red)

python -m unittest -v tests.test_cli.TestCli.test_new_initiative_and_epic_default_to_local_even_when_gh_is_available tests.test_cli.TestCli.test_new_issue_can_create_github_issue_and_use_its_number tests.test_cli.TestCli.test_import_initiative_creates_node_and_runs_sync_without_updating_active tests.test_cli.TestCli.test_import_epic_and_initiative_create_nodes tests.test_cli.TestCli.test_import_issue_creates_node_and_runs_sync_without_updating_active
# OK

python -m unittest discover -v
# OK (136 tests)
```

#### 変更したファイル
- `tests/test_cli.py` - `_spec_dock` 最小スキーマ検証を `new/import` テストに追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py` - `meta.json` 生成に `_spec_dock` を追加

#### コミット
- a616cca feat(meta): new/import生成metaに_spec_dock最小スキーマを追加

#### メモ
- ...

---

### 2026-03-04 07:18 - 07:25

#### 対象
- Step: S02
- AC/EC: AC-001, AC-002

#### 実施内容
- Red: `new/import` の既存テストに「POSIXでmeta.jsonのwrite bitが外れる」検証を追加し、失敗を確認
- Green: `io_json.py` に `_try_make_readonly()` を追加し、`_write_meta()` から best-effort で呼び出し
- Refactor: read-only導入で失敗した既存テストの `meta.json` 上書きをテストヘルパー化して安定化

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.test_cli.TestCli.test_new_initiative_and_epic_default_to_local_even_when_gh_is_available
# FAILED (期待どおり Red)

python -m unittest -v tests.test_cli.TestCli.test_new_initiative_and_epic_default_to_local_even_when_gh_is_available tests.test_cli.TestCli.test_new_issue_can_create_github_issue_and_use_its_number tests.test_cli.TestCli.test_import_initiative_creates_node_and_runs_sync_without_updating_active tests.test_cli.TestCli.test_import_epic_and_initiative_create_nodes tests.test_cli.TestCli.test_import_issue_creates_node_and_runs_sync_without_updating_active
# OK

python -m unittest -v tests.test_cli.TestCli.test_new_rejects_duplicate_id_width_agnostic tests.test_cli.TestCli.test_validate_detects_broken_parent_id tests.test_cli.TestCli.test_validate_detects_issue_initiative_id_mismatch tests.test_cli.TestCli.test_validate_reports_invalid_meta_json_shape tests.test_cli.TestCli.test_validate_detects_duplicate_github_issue_numbers_with_paths tests.test_cli.TestCli.test_sync_fails_when_tree_is_invalid tests.test_cli.TestCli.test_sync_force_continues_when_tree_is_invalid tests.test_cli.TestCli.test_sync_force_continues_when_meta_id_is_invalid tests.test_cli.TestCli.test_active_set_reuses_existing_branch_recomputes_desired_after_checkout_for_github_issue_target tests.test_cli.TestCli.test_active_set_reuses_existing_branch_recomputes_desired_after_checkout_for_node_id_target tests.test_cli.TestCli.test_active_set_fallbacks_to_id_when_id_slug_is_non_ascii tests.test_cli.TestCli.test_active_set_fallbacks_to_id_when_id_slug_is_invalid_ref tests.test_cli.TestCli.test_active_set_re_resolves_node_after_checkout_when_id_format_changes tests.test_cli.TestCli.test_import_fails_when_sync_preflight_fails
# OK

python -m unittest discover -v
# OK (136 tests)
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/io_json.py` - read-only化ヘルパー `_try_make_readonly()` を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py` - `meta.json` 書き込み直後に read-only化を best-effort で試行
- `tests/test_cli.py` - read-only検証追加と、meta編集テストの書き込みヘルパー化

#### コミット
- 269c642 feat(meta): new/import生成meta.jsonをread-only化
- 44197fd fix(test): read-onlyメタ書き換えヘルパーをOS非依存化

#### メモ
- S03 で read-only失敗時の warn + exit 0 を失敗系テストで固定予定

---

### 2026-03-04 07:30 - 07:37

#### 対象
- Step: S03
- AC/EC: EC-001

#### 実施内容
- Red: read-only化失敗をシミュレーションした `new initiative` 実行で warn が出ることを新規テストで先に固定
- Green: `_write_meta()` で `_try_make_readonly()` の戻り値を評価し、失敗時に `_warn()` を1回出して継続するよう実装
- Refactor: 失敗理由メッセージ整形を `_write_meta()` 内に最小追加（例外化はしない）

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.test_cli.TestCli.test_new_initiative_warns_and_continues_when_readonly_lock_fails
# FAILED (期待どおり Red)

python -m unittest -v tests.test_cli.TestCli.test_new_initiative_warns_and_continues_when_readonly_lock_fails tests.test_cli.TestCli.test_new_initiative_and_epic_default_to_local_even_when_gh_is_available tests.test_cli.TestCli.test_import_issue_creates_node_and_runs_sync_without_updating_active
# OK

python -m unittest discover -v
# OK (137 tests)
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py` - read-only化失敗時に `_warn()` を出して継続する処理を追加
- `tests/test_cli.py` - read-only化失敗時に warn + exit 0 を検証するS03テストを追加

#### コミット
- (コミット後に追記)

#### メモ
- warn prefix は `_warn()` 経由で `spec-dock: (warn)` を維持

---

## 遭遇した問題と解決 (任意)
- 問題: ...
  - 解決: ...

## 学んだこと (任意)
- ...
- ...

## 今後の推奨事項 (任意)
- ...
- ...

## 省略/例外メモ (必須)
- 該当なし
