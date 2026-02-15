---
種別: 実装報告書（Issue）
ID: "issue-5"
タイトル: "active set/new/import の命名・重複リンク整合"
関連GitHub: ["#5"]
状態: "draft"
作成者: "codex"
最終更新: "2026-02-14"
依存: ["requirement.md", "design.md", "plan.md"]
親: []
---

# issue-5 active set/new/import の命名・重複リンク整合 — 実装報告（LOG）

## 実装サマリー (任意)
- DEF-001 対応として、`new --github-issue` での `github.issue_number` 重複リンクを生成源で拒否するように修正。
- 併せて `validate` で `github.issue_number` 重複を検知して失敗させ、競合 node の `type:id` と `meta.json` パスを表示するようにした。
- エラー診断の安定性向上のため、競合一覧は決定的順序（type/id/path）で出力する。

## 実装記録（セッションログ） (必須)

### 2026-02-14 23:00 - 23:40

#### 対象
- Step: S06, S07
- AC/EC: AC-008, AC-009, EC-006

#### 実施内容
- `src/spec_dock/assets/spec_dock/scripts/spec-dock`
  - `_ensure_github_issue_not_linked(...)` を拡張し、`new --github-issue` と `import` 双方で重複リンク拒否時に `type:id` + `meta.json` パスを出力。
  - `new initiative|epic|issue` の `--github-issue` 経路で副作用前に重複チェックを追加。
  - `_validate_github_issue_numbers_unique(...)` を追加し、`_validate_nodes(...)` から実行するように変更。
  - 競合 path は repo ルート相対で表示し、競合一覧は決定的順序で整列。
- `tests/test_cli.py`
  - `test_new_rejects_duplicate_github_issue_link_with_conflict_paths` を追加。
  - `test_validate_detects_duplicate_github_issue_numbers_with_paths` を追加。

#### 実行コマンド / 結果
```bash
python -B -m unittest -v tests/test_cli.py -k duplicate_github_issue
# => OK (2 tests)

python -B -m unittest -v tests/test_cli.py -k github_issue_number
# => OK (3 tests)

python -B -m unittest -q
# => OK (56 tests)
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec-dock` - 重複リンク拒否/重複検知/診断出力の実装
- `tests/test_cli.py` - DEF-001 の再発防止テスト追加
- `tmp/issue-5/report.md` - 実装ログ更新

#### コミット
- （未実施）

#### メモ
- 重複リンク拒否は `import/new --github-issue` の既存番号リンク経路に限定（`gh issue create` 経路は対象外）。

---

### 2026-02-14 23:45 - 24:20

#### 対象
- Step: S08, S09
- AC/EC: AC-010, 非交渉制約（コマンド非依存ガイド）

#### 実施内容
- `src/spec_dock/assets/spec_dock/scripts/spec-dock`
  - `import` 専用 preflight ヘルパ（`_import_preflight_validate`）を追加し、`_import_{initiative,epic,issue}` で **副作用前**に `validate` 相当を実行するよう変更。
  - `import` の実行順序を `preflight validate` → `duplicate link check` → `gh issue view` → FS生成 に修正。
  - 重複リンク拒否の復旧ガイド文言をコマンド非依存化（`--github-issue` 固定文言を除去）。
- `tests/test_cli.py`
  - import重複リンク拒否時に `--github-issue` を含まないことを検証。
  - import preflight失敗時に `gh issue view` が呼ばれないことと、nodeディレクトリが増えないことを検証。
  - new重複リンク拒否テストも新文言に合わせて更新。

#### 実行コマンド / 結果
```bash
python -B -m unittest -v tests/test_cli.py -k "duplicate_github_issue or import_rejects_already_linked_github_issue_number or import_fails_when_sync_preflight_fails"
# => OK

python -B -m unittest -q
# => OK (56 tests)
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec-dock` - import副作用前preflight + 重複エラー文言の非依存化
- `tests/test_cli.py` - S08/S09の回帰テスト追加・更新
- `tmp/issue-5/report.md` - 実装ログ追記

#### コミット
- （未実施）

#### メモ
- preflight 失敗時のエラーは `preflight validate failed: ...` 形式で統一し、validate起因情報を引き継ぐ。

---

### 2026-02-15 00:30 - 00:55

#### 対象
- Step: S10
- AC/EC: AC-011, EC-005

#### 実施内容
- `src/spec_dock/assets/spec_dock/scripts/spec-dock`
  - `active set` の「既存ブランチ再利用」分岐で、checkout 後に scan → target 再解決 → desired 再計算 → `_ensure_active_set_branch_name(...)` を行うよう修正。
  - 対象経路: `active set <github_issue_number|url>` / `active set <node_id>`（GitHub 紐づき node）
- `tests/test_cli.py`
  - `test_active_set_reuses_existing_branch_recomputes_desired_after_checkout_for_github_issue_target` を追加。
  - `test_active_set_reuses_existing_branch_recomputes_desired_after_checkout_for_node_id_target` を追加。

#### 実行コマンド / 結果
```bash
python -B -m unittest -v tests/test_cli.py -k recomputes_desired_after_checkout
# => OK (2 tests)

python -B -m unittest -q
# => OK (58 tests)
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec-dock` - 既存ブランチ再利用後の desired 再評価/命名正規化の保証
- `tests/test_cli.py` - S10（slugズレ再発防止）の回帰テスト追加
- `tmp/issue-5/{requirement,design,plan}.md` - S10の前提/優先順位/テスト独立性の明文化
- `tmp/issue-5/report.md` - 実装ログ追記

#### コミット
- （未実施）

#### メモ
- 既存ブランチ再利用でも、最終的な current ブランチ名は checkout 後に再解決した node の `id/slug` 由来へ寄る。

---

## 遭遇した問題と解決 (任意)
- 問題: ...
  - 解決: ...

## 学んだこと (任意)
- 手動試験で見つかった運用不能ケース（DEF-001）は、生成源ブロック + validate 検知の二段構えが有効。
- エラーに競合 node の path を含めると、既存データの復旧コストを下げられる。

## 今後の推奨事項 (任意)
- 必要なら `active set` の `Ambiguous github.issue_number=<n>` 側にも同等の競合詳細を追加し、調査性をさらに上げる。
- 競合修復ガイド（手順例）を `docs/reference_github.md` に追記すると運用が安定する。

## 省略/例外メモ (必須)
- 該当なし
