---
種別: 実装報告書（Issue）
ID: "iss-00014"
タイトル: "ディスカッション資料の格納先を discussions/ に統一（adrs/artifacts の統合）"
関連GitHub: ["#14", "https://github.com/chemitaro/spec-dock/issues/14"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-06"
依存: ["requirement.md", "design.md", "plan.md"]
親: []
---

# iss-00014 ディスカッション資料の格納先を discussions/ に統一（adrs/artifacts の統合） — 実装報告（LOG）

## 実装サマリー (任意)
- S02として、テンプレ生成物を `adrs/` + `artifacts/` から `discussions/` に統合した。
- `spec-dock/templates/discussions/` に `adr/note/disc/research` テンプレを同梱し、各scopeに `discussions/rules.md` を追加した。
- `init/update` 後に `discussions/` が削除される不具合（legacy prune）を修正し、回帰テストを更新した。

## 実装記録（セッションログ） (必須)

### 2026-03-06 15:50 - 16:35

#### 対象
- Step: S02
- AC/EC: AC-001, AC-003, AC-005, AC-006, EC-002

#### 実施内容
- テンプレート変更:
  - `templates/adr.md` を `templates/discussions/adr.md` へ移動
  - `templates/discussions/{note,disc,research}.md` を追加
  - `templates/{initiative,epic,issue}/discussions/rules.md` を追加
  - `templates/{initiative,epic,issue}/{adrs,artifacts}` を削除
  - `templates/README.md` のマッピングと注意書きを更新
- 追加修正:
  - `src/spec_dock/cli.py` の `_prune_legacy_scaffold` を更新し、`discussions/` を削除しないよう修正
  - 代わりに legacy の `adrs/` / `artifacts/` を prune するよう変更
- テスト更新:
  - `tests/test_cli.py` を S02 要件に追随（`discussions/rules.md`、`adrs/artifacts` 不在、`new-adr` ラッパ不在、typeテンプレ同梱）

#### 実行コマンド / 結果
```bash
python -m unittest discover -v
# 1回目: FAIL (3件)
# - discussions が生成されない/保持されない
# - new node 配下に adrs が残る
#
# 修正後
python -m unittest discover -v
# OK (Ran 142 tests)
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/templates/README.md` - discussions統合に合わせた説明へ更新
- `src/spec_dock/assets/spec_dock/templates/discussions/adr.md` - ADRテンプレ移設
- `src/spec_dock/assets/spec_dock/templates/discussions/note.md` - noteテンプレ追加
- `src/spec_dock/assets/spec_dock/templates/discussions/disc.md` - discテンプレ追加
- `src/spec_dock/assets/spec_dock/templates/discussions/research.md` - researchテンプレ追加
- `src/spec_dock/assets/spec_dock/templates/initiative/discussions/rules.md` - initiative用 rules 追加
- `src/spec_dock/assets/spec_dock/templates/epic/discussions/rules.md` - epic用 rules 追加
- `src/spec_dock/assets/spec_dock/templates/issue/discussions/rules.md` - issue用 rules 追加
- `src/spec_dock/assets/spec_dock/templates/adr.md` - 削除（discussions配下へ移動）
- `src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/adrs/new-adr` - 削除
- `src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/artifacts/_template.md` - 削除
- `src/spec_dock/cli.py` - legacy prune 条件を S02仕様に修正
- `tests/test_cli.py` - S02 要件アサートへ更新

#### コミット
- なし（コミット前）
- 追記: a139aba feat(templates): discussions/ へ統一したスキャフォールドを追加

#### メモ
- S02スコープの実装とテスト通過まで完了。
- `spec-dock new adr` は S03 未着手のため現状は失敗する（`templates/adr.md` 参照のまま）。S03で `templates/discussions/adr.md` へ追随させる。
- 追記: S03（e4c84fc）で `spec-dock new adr` の `discussions/` 追随が完了した。
- 次は reviewer レビュー（指摘対応→再レビュー）を経て S02コミットへ進む。

---

### 2026-03-06 16:35 - 16:55

#### 対象
- Step: S03
- AC/EC: AC-002, EC-001

#### 実施内容
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py`
  - `_new_adr` の出力先を `adrs/` から `discussions/` に変更
  - `_new_adr` のテンプレ参照を `templates/adr.md` から `templates/discussions/adr.md` に変更
  - ADR採番/重複判定コメントを `discussions/` 前提へ更新
  - `_next_id` の ADR fallback scan を `rglob("discussions/adr-*.md")` に変更
- `tests/test_cli.py`
  - `new adr` の生成テストを `discussions/` 前提で追加
  - EC-001（`--id` 明示重複は非0失敗）テストを追加

#### 実行コマンド / 結果
```bash
python -m unittest discover -v
# OK (Ran 144 tests)
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py` - S03 runtime 変更
- `tests/test_cli.py` - S03 テスト追加

#### コミット
- なし（コミット前）
- 追記: e4c84fc fix(runtime): ADR を discussions/ に作成する

#### メモ
- これで `spec-dock new adr` は `discussions/adr-xxxxx-<slug>.md` に生成される。

---

### 2026-03-06 16:35 - 16:40

#### 対象
- Step: S05
- AC/EC: AC-005（導線固定）

#### 実施内容
- `src/spec_dock/assets/spec_dock/docs/*.md` と skill を `discussions/` 運用へ統一
  - `adrs/` / `artifacts/` / `new-adr` wrapper 前提の記述を除去
  - ADR 導線を `./spec-dock/scripts/spec-dock new adr --{issue|epic|initiative} ...` へ置換
  - `discussions/rules.md` と `spec-dock/templates/discussions/*.md` を参照する説明に統一
- `docs/discussion-sheets/01_tree_root_location.md` の構成例を `discussions/` 表記へ更新
- `tests/test_cli.py` の skill アサートを更新
  - `artifacts/` 前提を削除
  - `discussions/` と runtime `new adr` 導線を検証

#### 実行コマンド / 結果
```bash
python -m unittest discover -v
# OK (Ran 144 tests)
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/docs/guide.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_adr.md`
- `src/spec_dock/assets/spec_dock/docs/README.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- `src/spec_dock/assets/codex_skills/spec-driven-tdd-workflow/SKILL.md`
- `docs/discussion-sheets/01_tree_root_location.md`
- `tests/test_cli.py`

#### コミット
- なし（コミット前）

#### メモ
- S05 のドキュメント導線は `discussions/` 1本で整合した。

## 遭遇した問題と解決 (任意)
- 問題: `init/update` 後に `templates/**/discussions/` が消えるため、S02要件を満たせなかった
  - 解決: `_prune_legacy_scaffold` が `discussions` を legacy 扱いで削除していたため、削除対象を `adrs` / `artifacts` に置換した

## 学んだこと (任意)
- `S02` はテンプレ差し替えだけでなく、installer 側の legacy prune ルール更新が必須だった。
- 空ディレクトリは git 管理されないため、`rules.md` 同梱は仕様・実装の両面で有効だった。

## 今後の推奨事項 (任意)
- （将来）採番衝突の自動回避が必要になったら、`new doc` を別Issueで追加し、typeごとの採番テストで固定する。
- S06で最終品質ゲート（main差分レビュー）を実施する。

## 省略/例外メモ (必須)
- 該当なし
