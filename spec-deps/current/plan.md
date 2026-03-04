---
種別: 実装計画書（Issue）
ID: "iss-00010"
タイトル: "deps v2: shorthand 依存（initiative/epic）を issue 依存へ還元し、Readyボード（矢印なしツリー）で一目瞭然にする"
関連GitHub: ["TBD"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-04"
依存: ["requirement.md", "design.md"]
親: []
---

# iss-00010 deps v2 — 実装計画（TDD: Red → Green → Refactor）

## この計画で満たす要件ID (必須)
- 対象AC:
  - AC-001..006
  - AC-007..010
  - AC-011..013
- 対象EC: EC-001..005
- 対象制約（Always / 非交渉）:
  - unknown は blocked（安全側）に倒す
  - 出力は決定的順序（ソート）
  - `sync --force` でも stale を残さない（無効プレースホルダで上書き）
  - runtime は stdlib only
  - GitHub Issue を更新しない（取得のみ）

## ステップ一覧（観測可能な振る舞い） (必須)
- [ ] S01: `sync` が all/todo の JSON 観測点を生成する（パス/集合の契約）
- [ ] S02: `deps.json` shorthand を compile して canonical issue→issue edges を生成する
- [ ] S03: issue の deps 派生（closure/ready/blockers）を `index*.json` / `tree*.json` に統合する
- [ ] S04: issue-only 投影 `deps-issues.json` と可視化 `deps-issues.puml` を生成する
- [ ] S05: Readyボード（`tree*.puml`）と `dashboard.md` を `spec-dock/` 直下へ生成し、`.gitignore` で無視できる
- [ ] S06: `deps check`（`--json` 含む）が v2 の導出結果で ready/blockers を返す
- [ ] S07: `active set` が deps guard（+ `--force`）を v2 で正しく適用する
- [ ] S08: `sync --force` が deps 無効化プレースホルダで stale を残さず、legacy v1 deps 生成物を除去する
- [ ] S09: `--github` enrich / `--gh-limit` 劣化時の warnings + unknown=blocked が成立する
- [ ] S10: runtime を `spec_dock_runtime/` に責務分割し、entrypoint を薄く保つ（symlink-safe import）
- [ ] S11: shipped docs（`reference_sync.md` / `reference_deps.md`）を v2 の生成物/挙動に更新する
- [ ] S12: runtime の保守性改善（`spec_dock_runtime/app.py` の肥大化解消のため、設計に沿って追加のモジュール分割を行う。外部仕様は不変）

### UML（任意） (任意)
```plantuml
@startuml
skinparam shadowing false

rectangle "S01\n(sync views)" as S01
rectangle "S02\n(compile edges)" as S02
rectangle "S03\n(derive deps fields)" as S03
rectangle "S04\n(deps-issues.{json,puml})" as S04
rectangle "S05\n(tree*.puml + dashboard.md\n+ .gitignore)" as S05
rectangle "S06\n(deps check v2)" as S06
rectangle "S07\n(active guard v2)" as S07
rectangle "S08\n(sync --force placeholders\n+ remove legacy v1)" as S08
rectangle "S09\n(--github enrich + warnings)" as S09
rectangle "S10\n(refactor modules)" as S10
rectangle "S11\n(update shipped docs)" as S11
rectangle "S12\n(refactor modules 2)\n(shrink app.py)" as S12

S01 --> S02 --> S03 --> S04 --> S05 --> S06 --> S07 --> S08 --> S09 --> S10 --> S11 --> S12
@enduml
```

### 要件 ↔ ステップ対応表 (必須)
- AC-001 → S01, S02, S03, S04, S05
- AC-002/003 → S02, S06
- AC-004/005 → S07
- AC-006 → S05
- AC-007 → S06, S07
- AC-008 → S09
- AC-009 → S08
- AC-010 → S08
- AC-011/012 → S04
- AC-013 → S05
- AC-014 → S12
- EC-001..004 → S02, S06, S08
- EC-005 → S09
- Docs（shipped reference）→ S11
- 非交渉制約（stdlib only / GH更新しない）→ S01..S12（継続監視）
- 内部品質（保守性: モジュール分割）→ S12

---

## 実装ステップ（各ステップは“観測可能な振る舞い”を1つ） (必須)

### 共通の品質ゲート（全ステップで必須）
- 各ステップ末尾に **全テスト**を実行し成功させる:
  - `python -m unittest discover -v`
- 各ステップ末尾にコミットする（Conventional Commits、日本語、複数行）
- 各ステップ完了ごとに reviewer のレビューを通してから次へ進む（multi-agent 運用）
- 各ステップで **Red → Green → Refactor** を明示して回す（S02 以降も、S01 の構成をテンプレとして `update_plan` / テスト / 末尾チェックを省略しない）

### S01 — `sync` が all/todo の JSON 観測点を生成する（パス/集合の契約） (必須)
- 対象: AC-001
- 設計参照:
  - 対象IF/API: CLI-001 / IF-003 / MODEL-004 / MODEL-005
  - 対象テスト: `tests/test_cli.py`（sync 生成物の回帰）
- このステップで「追加しないこと（スコープ固定）」:
  - deps の compile/closure（S02/S03 で実施）
  - PlantUML / dashboard の生成（S04/S05 で実施）
  - GitHub enrich（S09）

#### update_plan（着手時に登録） (必須)
- [ ] `update_plan` に、このステップの作業ステップ（調査/Red/Green/Refactor/品質ゲート/報告/コミット）を登録した
- 登録例（必須の粒度）:
  - （調査）既存の `sync` 生成物とテストを確認
  - （Red）期待するファイル（index/tree all/todo）が無いことをテストで失敗させる
  - （Green）最小実装でファイルを出す（中身は最小でもよい）
  - （Refactor）命名/関数分割の最小整理
  - （品質ゲート）`python -m unittest discover -v`
  - （コミット）S01 完了コミット

#### 期待する振る舞い（テストケース） (必須)
- Given: 最小の spec ツリー（initiative/epic/issue）を作成済み
- When: `spec-dock/scripts/spec-dock sync` を実行する
- Then:
  - `spec-dock/.agent/index-all.json` / `tree-all.json` が生成される
  - `spec-dock/.agent/index.json` / `tree.json` が生成される
  - `index.json` と `tree.json` のノード集合が一致する（todo 集合の安定）
- 観測点: 生成ファイルの存在 + `schema_version` + nodes 集合
- 追加/更新するテスト（案）:
  - `tests/test_cli.py::test_sync_emits_all_and_todo_json_views`（新規）

#### Red（失敗するテストを先に書く） (任意)
- 期待する失敗:
  - `sync` 後に `index-all.json` / `tree-all.json` が存在しない

#### Green（最小実装） (任意)
- 変更予定ファイル:
- Modify: `src/spec_dock/assets/spec_dock/scripts/spec-dock`
- Modify: `tests/test_cli.py`
- 追加する概念（このステップで導入する最小単位）:
- `index-all.json` / `tree-all.json` の “all view”
- `index.json` / `tree.json` の “todo view”（S01 は中身最小で可）
- 実装方針（最小で。余計な最適化は禁止）:
- 既存 `index/tree` 生成ロジックを崩しすぎず、ファイル名と集合の契約を先に固定する

#### Refactor（振る舞い不変で整理） (任意)
- 目的: 次ステップ（deps compile/derive）を追加しやすくするための最小整理
- 変更対象: `sync` 周辺の emit を小さな helper に分割（過剰分割はしない）

#### ステップ末尾（省略しない） (必須)
- [ ] `python -m unittest discover -v` を実行し、成功した
- [ ] `update_plan` を更新し、このステップの作業ステップを完了にした
- [ ] コミットした（エージェント）

---

### S02 — `deps.json` shorthand を compile して canonical issue→issue edges を生成する (必須)
- 対象: AC-001, AC-002, AC-003, EC-001..004
- 追加/更新するテスト（案）:
  - `tests/test_cli.py::test_sync_compiles_shorthand_to_issue_edges`
  - `tests/test_cli.py::test_sync_warns_when_shorthand_expands_to_empty`
  - `tests/test_cli.py::test_sync_fails_on_unresolved_ref`
  - `tests/test_cli.py::test_sync_fails_on_descendant_dependency`
  - `tests/test_cli.py::test_sync_fails_on_self_or_cycle`
- 主要変更予定ファイル:
  - Modify: `src/spec_dock/assets/spec_dock/scripts/spec-dock`
  - Modify: `tests/test_cli.py`
- 品質ゲート: `python -m unittest discover -v`

### S03 — issue の deps 派生（closure/ready/blockers）を `index*.json` / `tree*.json` に統合する (必須)
- 対象: AC-001, AC-003, AC-008（unknown=blocked の土台）
- 追加/更新するテスト（案）:
  - `tests/test_cli.py::test_sync_derives_deps_fields_ready_and_blockers`
  - `tests/test_cli.py::test_unknown_is_not_ready`
  - `tests/test_cli.py::test_sync_outputs_are_deterministically_sorted`
- 主要変更予定ファイル: `src/spec_dock/assets/spec_dock/scripts/spec-dock`, `tests/test_cli.py`
- 品質ゲート: `python -m unittest discover -v`

### S04 — issue-only 投影 `deps-issues.json` と可視化 `deps-issues.puml` を生成する (必須)
- 対象: AC-011, AC-012
- 追加/更新するテスト（案）:
  - `tests/test_cli.py::test_sync_emits_deps_issues_json_and_puml_todo_only`
  - `tests/test_cli.py::test_sync_emits_deps_issues_puml_uses_ortho_linetype`
- 主要変更予定ファイル: `src/spec_dock/assets/spec_dock/scripts/spec-dock`, `tests/test_cli.py`
- 品質ゲート: `python -m unittest discover -v`

### S05 — Readyボード（`tree*.puml`）と `dashboard.md` を `spec-dock/` 直下へ生成し、`.gitignore` で無視できる (必須)
- 対象: AC-006, AC-013
- 追加/更新するテスト（案）:
  - `tests/test_cli.py::test_sync_emits_tree_puml_ready_board_at_spec_dock_root`
  - `tests/test_cli.py::test_sync_emits_dashboard_md_at_spec_dock_root`
  - `tests/test_cli.py::test_spec_dock_gitignore_ignores_human_facing_artifacts`
- 主要変更予定ファイル:
  - Modify: `src/spec_dock/assets/spec_dock/.gitignore`
  - Modify: `src/spec_dock/assets/spec_dock/scripts/spec-dock`
  - Modify: `tests/test_cli.py`
- 品質ゲート: `python -m unittest discover -v`

### S06 — `deps check`（`--json` 含む）が v2 の導出結果で ready/blockers を返す (必須)
- 対象: AC-002, AC-003, AC-007
- 追加/更新するテスト（案）:
  - `tests/test_cli.py::test_deps_check_returns_ready_and_blockers_and_closure_json`
  - `tests/test_cli.py::test_deps_check_without_github_uses_index_snapshot_when_present`
  - `tests/test_cli.py::test_deps_check_without_github_falls_back_to_unknown_when_snapshot_missing`
- 主要変更予定ファイル: `src/spec_dock/assets/spec_dock/scripts/spec-dock`, `tests/test_cli.py`
- 品質ゲート: `python -m unittest discover -v`

### S07 — `active set` が deps guard（+ `--force`）を v2 で正しく適用する (必須)
- 対象: AC-004, AC-005, AC-007
- 追加/更新するテスト（案）:
  - `tests/test_cli.py::test_active_set_is_blocked_when_deps_not_ready`
  - `tests/test_cli.py::test_active_set_force_overrides_deps_guard`
  - `tests/test_cli.py::test_active_set_without_github_uses_index_snapshot_when_present`
  - `tests/test_cli.py::test_active_set_without_github_blocks_when_snapshot_missing`
- 主要変更予定ファイル: `src/spec_dock/assets/spec_dock/scripts/spec-dock`, `tests/test_cli.py`
- 品質ゲート: `python -m unittest discover -v`

### S08 — `sync --force` が deps 無効化プレースホルダで stale を残さず、legacy v1 deps 生成物を除去する (必須)
- 対象: AC-010, AC-009
- 追加/更新するテスト（案）:
  - `tests/test_cli.py::test_sync_fails_on_deps_structural_error_without_force`
  - `tests/test_cli.py::test_sync_force_sets_deps_valid_false_and_emits_placeholders`
  - `tests/test_cli.py::test_sync_force_removes_legacy_v1_deps_artifacts`
- 主要変更予定ファイル: `src/spec_dock/assets/spec_dock/scripts/spec-dock`, `tests/test_cli.py`
- 品質ゲート: `python -m unittest discover -v`

### S09 — `--github` enrich / `--gh-limit` 劣化時の warnings + unknown=blocked が成立する (必須)
- 対象: AC-008, EC-005
- 追加/更新するテスト（案）:
  - `tests/test_cli.py::test_sync_github_limit_warns_incomplete_and_unknown_blocks`
  - `tests/test_cli.py::test_github_fetch_failed_warns_and_unknown_blocks`
- 主要変更予定ファイル: `src/spec_dock/assets/spec_dock/scripts/spec-dock`, `tests/test_cli.py`
- 品質ゲート: `python -m unittest discover -v`

### S10 — runtime を `spec_dock_runtime/` に責務分割し、entrypoint を薄く保つ（symlink-safe import） (必須)
- 対象: 非交渉制約（保守性）/ 設計のモジュール方針
- 位置づけ:
  - `S10` は「分割の土台（最低限の責務分離 + import 構造）」を導入するステップとし、残った肥大化の解消や最終整理は `S12` で行う。
- 追加/更新するテスト（案）:
  - `tests/test_cli.py::test_runtime_entrypoint_imports_modules_when_invoked_via_wrapper`（必要なら）
- 主要変更予定ファイル:
  - Add: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**`
  - Modify: `src/spec_dock/assets/spec_dock/scripts/spec-dock`
- 品質ゲート: `python -m unittest discover -v`

### S11 — shipped docs（`reference_sync.md` / `reference_deps.md`）を v2 の生成物/挙動に更新する (必須)
- 対象: 設計の deliverables（生成物/観測点の説明責任）
- 変更予定ファイル:
  - Modify: `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
  - Modify: `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
- 検証:
  - `python -m unittest discover -v`
  - docs 内の生成物パス（`.agent/*.json` と `spec-dock/*.puml`/`dashboard.md`）が ADR-00009 と一致する

---

### S12 — runtime の保守性改善（`spec_dock_runtime/app.py` の肥大化解消のため、設計に沿って追加のモジュール分割を行う。外部仕様は不変） (必須)
- 対象: AC-014（内部品質: 保守性）
- 目的:
  - runtime 実装が `spec_dock_runtime/app.py` に集中し過ぎている状態を解消し、保守・理解・レビューコストを下げる。
  - 外部仕様（CLI / 生成物 / exit code / JSON schema）を不変に保ちつつ、責務ごとにモジュール分割する。
- 位置づけ:
  - `S12` は `S10` で導入した分割（骨格）を前提に、残っている肥大化を解消して `app.py` を薄くする「最終整理」のステップとする。
- 追加/更新するテスト（案）:
  - `tests/test_cli.py::test_runtime_is_split_into_modules_after_init`（runtime 配置後に `spec_dock_runtime/` のモジュール群が存在する）
  - `tests/test_cli.py::test_runtime_help_succeeds_after_refactor`（`spec-dock/scripts/spec-dock --help` が exit=0）
  - 既存回帰（`tests/test_cli.py` の sync/new/active/deps 系）が全て通ること（最重要）
- 主要変更予定ファイル:
  - Modify: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py`
  - Add/Modify: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/ids.py`
  - Add/Modify: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/io_json.py`
  - Add/Modify: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/nodes.py`
  - Add/Modify: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/deps.py`
  - Add/Modify: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/github.py`
  - Add/Modify: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/active.py`
  - Add/Modify: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/render_puml.py`
  - Add/Modify: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/render_md.py`
- 方針（設計からの転記）:
  - entrypoint は維持: `spec-dock/scripts/spec-dock` → `spec_dock_runtime.app:main`
  - `app.py` は argparse/dispatch/例外整形を中心に薄くし、ドメインロジックを各モジュールへ移設する
  - 循環importを避けるため、依存方向（`app` → 各モジュール、各モジュール → `ids`/`io_json`）を固定する
  - runtime は stdlib only（依存追加なし）
- 進め方（TDD: 小さな Red → Green → Refactor を回す）:
  - Red:
    - まず「期待するモジュール群が存在する」「help が成功する」をテストで固定し、失敗させる
  - Green:
    - 1モジュールずつ最小移設（import で動かす）→ 全テスト → コミット
  - Refactor:
    - 重複削除・命名整理・責務境界の微調整（外部仕様不変）
- レビュー/QA（このステップの完了条件に含める）:
  - reviewer に **今回のリファクタ全体スコープ**でレビューを依頼し、指摘があれば修正→全テスト→再レビュー
  - QA エンジニアに評価（全テスト + smoke）を依頼し、指摘があれば修正→全テスト→再評価

---

## 未確定事項（TBD） (必須)
- 該当なし

## 完了条件（Definition of Done） (必須)
- 対象AC/ECがすべて満たされ、テストで保証されている
- MUST NOT / OUT OF SCOPE を破っていない
- 品質ゲート（フォーマット/リント/テストのうち該当するもの）が満たされている

## 省略/例外メモ (必須)
- 該当なし
