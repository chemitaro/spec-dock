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
- `0916c5ac97c32388eb52a24aebab3afbbb2c77fc` `test(init): canonical rules 契約に合わせて init/update 回帰試験を更新`

#### メモ
- code_reviewer / qa_reviewer による S02 scoped review は pass。
- installer 実装本体の変更は不要で、provider assets 配布契約は既存実装で満たしていた。

---

### 2026-03-26 07:31 - 17:45

#### 対象
- Step: S03
- AC/EC: AC-003

#### 実施内容
- DevCoder で wrapper 前提の docs/tests を `spec-dock/docs/rules/**` 正本 + `rules.md` symlink 導線前提へ更新した。
- `tests/cli_runtime/test_wrappers.py` を置き換え、new/import node の no-wrapper contract、workflow/reference wording、discussion `new doc` / `validate` non-regression を initiative / epic / issue の 3 scope で検証するようにした。
- `tests/cli_runtime/test_import.py` と `tests/cli_runtime/test_runtime_import_s10.py` を強化し、import initiative / epic / issue でも canonical rules symlink が張られ、legacy `new-*` wrapper が生成されないことを確認するようにした。
- provider-side docs と checked-in dogfooding mirror を同期し、`spec-dock/docs/rules/**` の mirror 実体追加、workflow/reference/template wording の更新、mirror `templates/` subtree の stale wrapper-era files 削除を行った。
- review 指摘に基づき、rules docs に repo root 実行ガイダンスを追加し、`tests/test_init_update.py` で checked-in mirror parity と installed `templates/` parity を exact tree/content match として固定した。
- active issue plan の S03 design ref wording も `docs/rules/**` 正本 + runtime command documented execution path に合わせて補正した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_wrappers -v
python -m unittest tests.cli_runtime.test_import -v
python -m unittest tests.cli_runtime.test_runtime_import_s10 -v
python -m unittest tests.test_init_update -v
python -m unittest discover -v

6 tests OK
32 tests OK
17 tests OK
77 tests OK
460 tests OK
```

#### 変更したファイル
- `tests/cli_runtime/test_wrappers.py` - docs wording / no-wrapper / discussion new doc + validate regression を 3 scope で検証
- `tests/cli_runtime/test_import.py` - import initiative / epic の rules symlink / no-wrapper contract を追加
- `tests/cli_runtime/test_runtime_import_s10.py` - import issue の rules symlink / no-wrapper contract を追加
- `tests/test_init_update.py` - checked-in mirror docs/rules/templates parity と installed templates parity / legacy wrapper pruning を検証
- `src/spec_dock/assets/spec_dock/templates/README.md` - canonical rules source / runtime command guidance へ更新
- `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md` - wrapper guidance を削除し guaranteed runtime path / canonical rules guidance へ更新
- `src/spec_dock/assets/spec_dock/docs/workflow_epic.md` - wrapper guidance を削除し guaranteed runtime path / canonical rules guidance へ更新
- `src/spec_dock/assets/spec_dock/docs/reference_github.md` - rules symlink / runtime path / validate/sync guidance を更新
- `src/spec_dock/assets/spec_dock/docs/rules/initiative/epics.md` - repo root 実行 guidance を追加
- `src/spec_dock/assets/spec_dock/docs/rules/initiative/discussions.md` - repo root 実行 guidance を追加
- `src/spec_dock/assets/spec_dock/docs/rules/epic/issues.md` - repo root 実行 guidance を追加
- `src/spec_dock/assets/spec_dock/docs/rules/epic/discussions.md` - repo root 実行 guidance を追加
- `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md` - repo root 実行 guidance を追加
- `spec-dock/templates/README.md` - dogfooding mirror を provider docs に同期
- `spec-dock/docs/workflow_initiative.md` - dogfooding mirror を provider docs に同期
- `spec-dock/docs/workflow_epic.md` - dogfooding mirror を provider docs に同期
- `spec-dock/docs/reference_github.md` - dogfooding mirror を provider docs に同期
- `spec-dock/docs/rules/initiative/epics.md` - dogfooding mirror canonical rules を追加
- `spec-dock/docs/rules/initiative/discussions.md` - dogfooding mirror canonical rules を追加
- `spec-dock/docs/rules/epic/issues.md` - dogfooding mirror canonical rules を追加
- `spec-dock/docs/rules/epic/discussions.md` - dogfooding mirror canonical rules を追加
- `spec-dock/docs/rules/issue/discussions.md` - dogfooding mirror canonical rules を追加
- `spec-dock/templates/adr.md` ほか legacy wrapper-era mirror template files - provider assets と一致するよう削除
- `spec-dock/active/issue/plan.md` - S03 design ref wording を SoR 決定に合わせて補正

#### コミット
- （この直後に S03 scope をコミット）

#### メモ
- code_reviewer / qa_reviewer / spec_reviewer による S03 scoped review は pass。
- S03 では runtime 実装の変更は不要で、docs/tests/dogfooding parity の整理で acceptance を閉じた。

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
