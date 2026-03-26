---
種別: 実装報告書（Issue）
ID: "iss-00031"
タイトル: "Replace Wrapper Scripts With Symlink Rules"
関連GitHub: ["#31"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-26"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-local-00001", "init-local-00003"]
---

# iss-00031 Replace Wrapper Scripts With Symlink Rules — 実装報告（LOG）

## 実装サマリー (任意)
- [実装した内容の概要を2-3文で記載]

## 実装記録（セッションログ） (必須)

### 2026-03-26 06:17 - 07:04

#### 対象
- Step: S01
- AC/EC: AC-002, EC-002

#### 実施内容
- DevCoder で Red → Green → Refactor を回し、provider-side の中央管理 rules 原本を `src/spec_dock/assets/spec_dock/docs/rules/` に追加した。
- runtime create flow を更新し、新規 initiative / epic / issue 作成時に wrapper ではなく相対 `rules.md` symlink を生成するようにした。
- review 指摘に基づき、rules source 欠落、link collision、空 parent path collision、symlinked parent collision、symlink capability failure を scaffold copy 前に弾く preflight を追加した。
- GitHub issue 作成前に `docs/rules` 原本欠落を検知する precheck を追加し、remote side effect 前に失敗させるようにした。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_runtime_new_s08 -v
python -m unittest tests.cli_runtime.test_new -v
python -m unittest tests.cli_runtime.test_runtime_new_doc_s09 -v

39 tests OK
32 tests OK
9 tests OK
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py` - rules symlink 生成と preflight を追加
- `src/spec_dock/assets/spec_dock/docs/rules/initiative/epics.md` - initiative 配下 epic 作成 rules 原本を追加
- `src/spec_dock/assets/spec_dock/docs/rules/initiative/discussions.md` - initiative discussion rules 原本を追加
- `src/spec_dock/assets/spec_dock/docs/rules/epic/issues.md` - epic 配下 issue 作成 rules 原本を追加
- `src/spec_dock/assets/spec_dock/docs/rules/epic/discussions.md` - epic discussion rules 原本を追加
- `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md` - issue discussion rules 原本を追加
- `src/spec_dock/assets/spec_dock/templates/initiative/epics/new-epic` - wrapper asset を削除
- `src/spec_dock/assets/spec_dock/templates/epic/issues/new-issue` - wrapper asset を削除
- `src/spec_dock/assets/spec_dock/templates/initiative/discussions/rules.md` - copied rules asset を削除
- `src/spec_dock/assets/spec_dock/templates/epic/discussions/rules.md` - copied rules asset を削除
- `src/spec_dock/assets/spec_dock/templates/issue/discussions/rules.md` - copied rules asset を削除
- `tests/cli_runtime/test_new.py` - rules symlink / pre-GitHub failure coverage を追加
- `tests/cli_runtime/test_runtime_new_s08.py` - create-flow preflight / no-write regression を追加
- `tests/cli_runtime/test_runtime_new_doc_s09.py` - minimal fixture に rules source を追加

#### コミット
- `7cda3197f53578a4e792067cea26b4c1d1cd88c7` `feat(runtime): rules.md symlink scaffold を導入`

#### メモ
- code_reviewer による S01 scoped review は pass。
- wrapper-facing docs / installer parity / broader regression cleanup は後続 step で扱う。

---

### 2026-03-26 07:04 - 07:31

#### 対象
- Step: S02
- AC/EC: AC-001, EC-001, EC-003

#### 実施内容
- DevCoder で `tests.test_init_update` の failing surface を更新し、installer の正本を削除済み template rules ではなく `spec-dock/docs/rules/**` に切り替えた。
- `init` の検証を更新し、legacy `templates/**/discussions/rules.md` 非存在と canonical `docs/rules/**` 配布を明示した。
- `update` の検証を強化し、5 本すべての canonical rules file を破損させた上で provider assets からの完全復元を確認した。
- review / QA 指摘に基づき、legacy template path の削除確認、canonical rules file の個別内容確認、provider asset との exact match 確認を追加した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.test_init_update -v

75 tests OK
```

#### 変更したファイル
- `tests/test_init_update.py` - init/update の canonical rules contract、refresh、legacy path removal、asset exact-match を検証

#### コミット
- （この直後に S02 scope をコミット）

#### メモ
- code_reviewer / qa_reviewer による S02 scoped review は pass。
- installer 実装本体の変更は不要で、provider assets 配布契約は既存実装で満たしていた。

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
