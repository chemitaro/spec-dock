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
- (コミット後に追記)

#### メモ
- ...

---

### YYYY-MM-DD HH:MM - HH:MM

#### 対象
- Step: ...
- AC/EC: ...

#### 実施内容
- ...

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
