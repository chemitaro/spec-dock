---
種別: 実装報告書（Issue）
ID: "iss-00031"
タイトル: "Replace Wrapper Scripts With Symlink Rules"
関連GitHub: ["#31"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-26"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-local-00001", "init-local-00003"]
---

# iss-00031 Replace Wrapper Scripts With Symlink Rules — 実装報告（LOG）

## 実装サマリー (任意)
- `new-epic` / `new-issue` wrapper を廃止し、新規 initiative / epic / issue の child directory が `rules.md` symlink 経由で `spec-dock/docs/rules/**` の canonical rules を参照する contract に揃えた。
- provider-side `src/spec_dock/assets/spec_dock/docs/rules/**` は package に同梱する authoring/source files として保持し、`init/update` と checked-in mirror が `spec-dock/docs/rules/**` へ同内容を展開することを tests で固定した。

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
- `1cd9be02602d42d6b77296cb783c299af022aafe` `docs(rules): wrapper 廃止後の docs と回帰試験を整合`

#### メモ
- code_reviewer / qa_reviewer / spec_reviewer による S03 scoped review は pass。
- S03 では runtime 実装の変更は不要で、docs/tests/dogfooding parity の整理で acceptance を閉じた。

---

### 2026-03-26 17:45 - 18:08

#### 対象
- Step: S99
- AC/EC: final gate evidence / actionable close-out

#### 実施内容
- final-review 指摘に従い、`pyproject.toml` の `tool.setuptools.exclude-package-data.spec_dock` guard に加えて、stale build output を混ぜた local wheel build でも wrapper-era template asset が wheel に入らないことを `tests/test_init_update.py` で可視化した。
- `tests/test_init_update.py` に checked-in runtime mirror parity guard を追加し、`spec-dock/scripts/spec_dock_runtime/application/create_node.py` が provider runtime asset と一致し続けることを固定した。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py` と checked-in runtime mirror の双方で、GitHub issue 作成前に symlink capability を preflight するように修正し、remote side effect より先に fail-fast するよう整えた。
- `workflow_issue.md` の command examples を guaranteed runtime path に揃え、関連 docs/tests/spec artifact を最新の SoR 判断へ追随させた。
- `./spec-dock/scripts/spec-dock validate` と `./spec-dock/scripts/spec-dock sync --github` を実行し、generated state を更新して `iss-00031` が GitHub authority / `OPEN` / `stale=false` で観測される状態まで反映した。
- `main` merge-base `dc31512a47ab320552faed60446534a8ac88e968` との差分を最終確認し、final code review / final QA review / final spec review は PASS と判断した。
- uppercase path non-increase を確認し、今回の最終差分で新たな uppercase path 追加はなく、変更対象は既存の uppercase filename のみであることを記録した。

#### 実行コマンド / 結果
```bash
git --no-pager diff --name-only dc31512a47ab320552faed60446534a8ac88e968...HEAD
python -m unittest tests.test_init_update.TestInitUpdate.test_built_wheel_excludes_deleted_wrapper_era_assets_from_stale_build_outputs -v
python -m unittest tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets -v
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync --github
python -m unittest discover -v

final diff review completed
1 test OK
1 test OK
validate OK (nodes=4)
sync --github OK
464 tests OK
```

#### 変更したファイル
- `pyproject.toml` - stale build output 向けの wrapper-era template asset exclusion を追加
- `tests/test_init_update.py` - observable wheel-build packaging regression、checked-in runtime mirror parity guard、workflow_issue guidance / packaging guard を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py` - GitHub issue 作成前の symlink capability preflight を追加
- `spec-dock/scripts/spec_dock_runtime/application/create_node.py` - checked-in runtime mirror を provider runtime asset に同期
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` / `spec-dock/docs/workflow_issue.md` - guaranteed runtime path guidance に更新
- `spec-dock/active/issue/design.md` / `requirement.md` / `spec-dock/active/epic/report.md` - latest SoR / close-out wording に整合
- `spec-dock/active/issue/report.md` - S99 final gate evidence を更新

#### コミット
- 未コミット（final-review close-out の作業ツリー差分）

#### メモ
- final diff review 対象 merge-base: `dc31512a47ab320552faed60446534a8ac88e968`
- final code review: PASS
- final QA review: PASS
- final spec review: PASS（actionable close-out items 充足）
- latest full test evidence: `python -m unittest discover -v` 464 tests OK
- workflow finish evidence: `./spec-dock/scripts/spec-dock validate` OK / `./spec-dock/scripts/spec-dock sync --github` OK
- generated state after sync: `iss-00031` / authority=`github` / state=`OPEN` / stale=`false`
- uppercase path non-increase: PASS（新規 uppercase path 追加なし。既存 uppercase filename の変更のみ）

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
