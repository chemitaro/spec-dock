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
- 0f2b52e fix(meta): read-only失敗時もwarnしてnew/importを継続

#### メモ
- warn prefix は `_warn()` 経由で `spec-dock: (warn)` を維持

---

### 2026-03-04 07:40 - 07:48

#### 対象
- Step: S04
- AC/EC: EC-002

#### 実施内容
- Red: 既存ノード化した `meta.json` に対して `sync/validate` 後の期待をわざと誤らせ、失敗を確認
- Green: `sync/validate` 実行前後で `meta.json` の text/mode が不変、かつ `_spec_dock` が復活しないことを新規テストで固定
- Refactor: mode比較を POSIX 限定にして、write bit 状態が変化していないことも追加検証

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.test_cli.TestCli.test_sync_and_validate_do_not_backfill_or_relock_existing_meta_json
# FAILED (期待どおり Red)

python -m unittest -v tests.test_cli.TestCli.test_sync_and_validate_do_not_backfill_or_relock_existing_meta_json
# OK

python -m unittest discover -v
# OK (138 tests)
```

#### 変更したファイル
- `tests/test_cli.py` - 既存 `meta.json` が `sync/validate` で後追い変更されないことを固定するS04テストを追加

#### コミット
- faffc71 test(meta): sync/validateで既存meta.jsonを後追い変更しないことを固定

#### メモ
- runtime 実装変更は不要（テストのみで EC-002 を固定）

---

### 2026-03-04 08:10 - 08:32

#### 対象
- Step: Dotfile migration (runtime/wrapper)
- AC/EC: AC-001, EC-001, EC-002

#### 実施内容
- `meta.json` 正本を `.meta.json` に切り替えるため、runtime の定数/走査/出力先を更新
- legacy 互換として `.meta.json` 不在かつ `meta.json` 存在時に best-effort rename 移行を追加
- `.meta.json` と `meta.json` が共存する場合は `.meta.json` を優先し、legacy は warn して無視
- wrapper scripts を `.meta.json` 優先 + `meta.json` fallback の導線へ更新

#### 実行コマンド / 結果
```bash
python -m unittest discover -v
# OK (140 tests)
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py` - `.meta.json` 正本化と legacy `meta.json` 移行/共存warnを追加
- `src/spec_dock/assets/spec_dock/templates/initiative/epics/new-epic` - `.meta.json` 優先 + legacy fallback を追加
- `src/spec_dock/assets/spec_dock/templates/epic/issues/new-issue` - `.meta.json` 優先 + legacy fallback を追加
- `src/spec_dock/assets/spec_dock/templates/initiative/adrs/new-adr` - `.meta.json` 優先 + legacy fallback を追加
- `src/spec_dock/assets/spec_dock/templates/epic/adrs/new-adr` - `.meta.json` 優先 + legacy fallback を追加
- `src/spec_dock/assets/spec_dock/templates/issue/adrs/new-adr` - `.meta.json` 優先 + legacy fallback を追加

#### コミット
- 54912d1 refactor(meta): runtimeとwrapperを.meta.json基準に移行

#### メモ
- rename は best-effort。失敗時は warn して処理継続（exit code 0）を維持

---

### 2026-03-04 08:32 - 08:38

#### 対象
- Step: Dotfile migration (docs)
- AC/EC: AC-001

#### 実施内容
- shipped docs / scripts README の `meta.json` 表記を `.meta.json` へ更新
- SSOT の説明、図、エラーメッセージ例の表記を runtime 実装と一致させた

#### 実行コマンド / 結果
```bash
python -m unittest discover -v
# OK (140 tests)
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/docs/guide.md`
- `src/spec_dock/assets/spec_dock/docs/reference_github.md`
- `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
- `src/spec_dock/assets/spec_dock/scripts/README.md`

#### コミット
- 4a54e88 docs(meta): .meta.json への表記統一を反映

#### メモ
- 振る舞い変更はなく、ドキュメント整合のみ

---

### 2026-03-04 09:00 - 09:18

#### 対象
- Step: review follow-up (P1)
- AC/EC: EC-002

#### 実施内容
- runtime の legacy rename を migrate モード時だけ有効化
  - `_resolve_node_meta_path(..., migrate=...)`
  - `_iter_node_meta_paths(..., migrate=...)`
  - `_scan_nodes(..., migrate_legacy_meta=False)`（既定）
- `sync` / `validate` だけ `migrate_legacy_meta=True` で走査するよう変更
- `import preflight` と通常コマンド経路は `migrate_legacy_meta=False` のまま維持
- テスト追加/更新:
  - wrapper/new 実行時は legacy `meta.json` を読めても rename しないことを固定
  - import の preflight 失敗（`gh issue view` 失敗）時に legacy `meta.json` が rename されないことを固定

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.test_cli.TestCli.test_wrapper_uses_legacy_meta_json_when_dot_meta_missing tests.test_cli.TestCli.test_import_preflight_does_not_migrate_legacy_meta_on_gh_issue_view_failure
# FAILED (期待どおり Red)

python -m unittest -v tests.test_cli.TestCli.test_wrapper_uses_legacy_meta_json_when_dot_meta_missing tests.test_cli.TestCli.test_import_preflight_does_not_migrate_legacy_meta_on_gh_issue_view_failure tests.test_cli.TestCli.test_validate_and_sync_migrate_legacy_meta_json_without_backfill_or_relock tests.test_cli.TestCli.test_validate_prefers_dot_meta_json_and_warns_when_legacy_coexists tests.test_cli.TestCli.test_import_aborts_without_local_changes_when_gh_issue_view_fails
# OK

python -m unittest discover -v
# OK (142 tests)
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py`
- `tests/test_cli.py`

#### コミット
- (この追記を含むコミットで反映)

#### メモ
- preflight の副作用を抑えつつ、`sync/validate` での legacy 移行要件は維持

---

### 2026-03-04 (follow-up)

#### 対象
- Step: design update (breaking change accepted)
- AC/EC: EC-002

#### 方針変更（決定）
- 後方互換性が不要という意思決定により、レガシー `meta.json` の互換/移行方針を撤回
  - runtime / wrapper / docs / tests から `meta.json` の読み取り/移行/互換を削除
  - `sync` / `validate` はレガシー `meta.json` を検出したらエラーで停止し、移行ガイダンスを出す

#### メモ
- 直前の「`sync/validate` の best-effort rename 移行」方針は `adr-00003` により Superseded

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
