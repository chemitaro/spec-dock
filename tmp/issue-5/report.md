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
