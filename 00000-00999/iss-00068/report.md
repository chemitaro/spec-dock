---
種別: 実装報告書（Issue）
ID: "iss-00068"
タイトル: "Install root tree and asset classification"
関連GitHub: ["#68"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-13"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00068 Install root tree and asset classification — 実装報告（LOG）

## 実装サマリー
- `src/spec_dock/assets/install_root/` を authoritative provider-side tree として追加し、issue-68 の in-scope 11 assets を install-shaped layout に再配置した。
- S01 では installer compatibility を壊さないよう `src/spec_dock/assets/codex_skills/` を mirror のまま維持しつつ、authoritative placement と workflow seed を確認する最小テストを追加した。

## 実装記録（セッションログ）

### 2026-04-13 00:00 - 00:00

#### 対象
- Step: S01
- AC/EC: AC-001, AC-002, EC-001, EC-002, EC-003

#### 実施内容
- `src/spec_dock/assets/install_root/` を新設し、`.agents` / `.codex` / `.github` / `.github/workflows` の authoritative subtree を追加した。
- shared skills 7 件、host-adapters meta 1 件、native shim 2 件、workflow 1 件の合計 11 assets を `install_root` 側へ配置した。
- `tests/test_init_update.py` に S01 用の最小検証として次の 3 テストを追加した。
  - `test_issue_68_install_root_tree_exists`
  - `test_issue_68_authoritative_inventory_paths_are_classified_under_install_root`
  - `test_issue_68_workflow_seed_matches_repo_root_ci_workflow`
- user-approved decision に基づき、shared skill asset の既存 filename convention である `SKILL.md` を uppercase path 例外として issue docs に反映した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_install_root_tree_exists
.
----------------------------------------------------------------------
Ran 1 test in 0.000s

OK

python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_authoritative_inventory_paths_are_classified_under_install_root
.
----------------------------------------------------------------------
Ran 1 test in 0.000s

OK

python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_workflow_seed_matches_repo_root_ci_workflow
.
----------------------------------------------------------------------
Ran 1 test in 0.001s

OK

find src/spec_dock/assets/install_root -print | rg '[A-Z]' | grep -v 'SKILL\.md$'
# no output
```

#### 変更したファイル
- `src/spec_dock/assets/install_root/.agents/skills/*/SKILL.md` - authoritative shared skill assets を追加
- `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json` - authoritative host adapter metadata を追加
- `src/spec_dock/assets/install_root/.codex/agents/spec-dock.toml` - authoritative Codex native shim を追加
- `src/spec_dock/assets/install_root/.github/agents/spec-dock.agent.md` - authoritative GitHub native shim を追加
- `src/spec_dock/assets/install_root/.github/workflows/ci.yml` - authoritative workflow seed を追加
- `tests/test_init_update.py` - S01 の最小検証テストを追加
- `spec-dock/active/issue/requirement.md` - `SKILL.md` 例外を反映
- `spec-dock/active/issue/design.md` - `SKILL.md` 例外と test ownership を反映
- `spec-dock/active/issue/plan.md` - user-approved 例外と gate command を反映
- `spec-dock/active/issue/report.md` - S01 証跡を記録

#### コードレビュー
- reviewer:
  - `code_reviewer`
- verdict:
  - `pass`
- note:
  - `SKILL.md` 例外を issue docs に反映した後、S01 diff は blocking finding なしで pass

#### コミット
- `ff6a997` `feat(assets): install_root正本ツリーを追加`

#### メモ
- `cli.py` / package data / installer cutover は issue-68 の範囲外のため未変更。
- `codex_skills` mirror は compatibility のため残している。parity / duplicate boundary は S02 で追加検証する。

---

### 2026-04-13 00:00 - 00:00

#### 対象
- Step: S02
- AC/EC: AC-003

#### 実施内容
- `tests/test_init_update.py` に declared legacy pair parity と provider-side duplicate boundary を検証する issue-68 専用テストを追加した。
- S02 scope は test 追加のみに閉じ、installer behavior 変更は行っていない。

#### 実行コマンド / 結果
```bash
python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_declared_legacy_pairs_remain_byte_equivalent
.
----------------------------------------------------------------------
Ran 1 test in 0.003s

OK

python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_authority_inventory_disallows_unlisted_provider_duplicates
.
----------------------------------------------------------------------
Ran 1 test in 0.052s

OK

python -m unittest tests.test_init_update.TestInitUpdate.test_bundled_skill_assets_cover_managed_manifest
.
----------------------------------------------------------------------
Ran 1 test in 0.000s

OK

python -m unittest tests.test_init_update.TestInitUpdate.test_bundled_native_shim_assets_satisfy_static_delegation_only_contract
.
----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

#### 変更したファイル
- `tests/test_init_update.py` - declared mirror parity と inventory 外 duplicate 不在の S02 テストを追加
- `spec-dock/active/issue/report.md` - S02 証跡を記録

#### コードレビュー
- reviewer:
  - `code_reviewer`
- verdict:
  - `pass`
- note:
  - S02 diff は tests のみで、no installer behavior changes を維持したまま parity / duplicate boundary を検証できている

#### コミット
- `d6c6f4e` `test(assets): install_root分類検証を追加`

#### メモ
- duplicate boundary テストは inventory に未記載の provider-side duplicate が増えた時点で fail する。

---

### 2026-04-13 00:00 - 00:00

#### 対象
- Step: S90, S99
- AC/EC: final exit contract

#### 実施内容
- final validation を実施し、issue-local targeted tests、`validate`、`sync --github` の closeout evidence を収集した。
- final code review を実施し、実装上の blocking finding なしで `pass` を確認した。
- final spec review を実施し、初回は report の closeout 記録不足で `fail` となったため、この report を更新して closeout evidence と commit hash を補完した。
- `python -m unittest discover -v` は実行したが、issue-68 の acceptance と無関係な既存 failure が残っていることを確認した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_install_root_tree_exists
OK

python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_authoritative_inventory_paths_are_classified_under_install_root
OK

python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_workflow_seed_matches_repo_root_ci_workflow
OK

python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_declared_legacy_pairs_remain_byte_equivalent
OK

python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_authority_inventory_disallows_unlisted_provider_duplicates
OK

python -m unittest tests.test_init_update.TestInitUpdate.test_bundled_skill_assets_cover_managed_manifest
OK

python -m unittest tests.test_init_update.TestInitUpdate.test_bundled_native_shim_assets_satisfy_static_delegation_only_contract
OK

find src/spec_dock/assets/install_root -print | rg '[A-Z]' | grep -v 'SKILL\.md$'
# no output

./spec-dock/scripts/spec-dock validate
spec-dock: ok (validate) nodes=29

./spec-dock/scripts/spec-dock sync --github
spec-dock: ok (sync) wrote=spec-dock/.agent/index-all.json,spec-dock/.agent/tree-all.json,spec-dock/.agent/index.json,spec-dock/.agent/tree.json,spec-dock/tree-all.puml,spec-dock/tree.puml,spec-dock/.agent/deps-issues.json,spec-dock/deps-issues.puml,spec-dock/dashboard.md
spec-dock: sync: active unchanged (matched id in branch: iss-00068)

python -m unittest discover -v
FAILED
```

#### 変更したファイル
- `spec-dock/active/issue/report.md` - final closeout evidence、review verdict、full-suite note を追加

#### レビュー
- final code review:
  - reviewer:
    - `code_reviewer`
  - verdict:
    - `pass`
  - note:
    - 指摘は `report.md` の S02 commit hash 未反映のみで、実装 diff 自体には P0/P1 なし
- final spec review:
  - reviewer:
    - `spec_reviewer`
  - verdict:
    - `pass`
  - note:
    - 初回 fail 理由は S99 closeout evidence 不足と S02 commit 欄未更新だったが、この report 更新で解消した

#### コミット
- final implementation commit:
  - `d6c6f4e` `test(assets): install_root分類検証を追加`
- closeout decision:
  - no additional product commit required
  - issue-68 の product diff は `ff6a997` と `d6c6f4e` で閉じており、この report 更新は closeout evidence の整理に限定する

#### メモ
- `python -m unittest discover -v` の failure は issue-68 scope 外の既存 failure と判断した。
  - `tests.cli_runtime.test_runtime_shell_s11.RuntimeShellS11Tests.test_final_api_call_site_and_structural_regression`
  - `tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json`
  - `tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_subprocess_validate_and_sync_on_cutover_snapshot`
- 上記は runtime architecture regression と dogfooding cutover snapshot expectation に関する failure であり、`install_root` authoritative tree / classification foundation の acceptance を直接否定するものではない。

## 遭遇した問題と解決
- 問題:
  - `SKILL.md` 追加により uppercase path 原則と issue plan の gate が衝突した。
  - 解決:
    - ユーザーが `SKILL.md` 例外を明示承認し、requirement / design / plan にその例外を反映した。

## 今後の推奨事項
- issue-69 以降で `install_root` authoritative source を package / installer / managed ownership へ接続する実装を進める。
- full suite の既存 failure は別 issue で切り分けて扱う。

## 省略/例外メモ
- `SKILL.md` は shared skill asset の既存 filename convention であるため、issue-68 に限り user-approved uppercase path 例外として扱う。
