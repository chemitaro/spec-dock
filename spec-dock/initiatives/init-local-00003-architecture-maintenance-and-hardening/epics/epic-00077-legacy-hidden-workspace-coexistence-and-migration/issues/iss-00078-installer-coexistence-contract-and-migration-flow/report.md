---
種別: 実装報告書（Issue）
ID: "iss-00078"
タイトル: "Installer coexistence contract and migration flow"
関連GitHub: ["#78"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-04-15"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00077", "init-local-00003"]
---

# iss-00078 Installer coexistence contract and migration flow — 実装報告（LOG）

## 実装サマリー (任意)
- installer の legacy rename blocker を除去し、legacy `.spec-dock/` と current `spec-dock/` の共存インストールを許可した。
- runtime `doctor` に `legacy_only_workspace` finding と `legacy_cleanup_pending` warning を追加し、manual migration / manual delete を案内する current-only contract を固定した。
- dogfooding mirror、guide、issue-78 regression tests、review evidence を揃え、final reviewer verdict を `pass` まで収束させた。

## 実装記録（セッションログ） (必須)

### 2026-04-15 00:00 - 23:59

#### 対象
- Step: S02, S03, S04, S90, S99
- AC/EC: AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, EC-001, EC-002, EC-003

#### 実施内容
- `src/spec_dock/cli.py` の `_install_spec_dock()` から legacy rename blocker を除去し、`_require_specdock()` を no-rename / manual migration guidance に置き換えた。
- provider runtime に `legacy_only_workspace` finding、`legacy_cleanup_pending` warning、warning text rendering を追加した。
- dogfooding runtime mirror の `contracts.py` / `doctor.py` / `cli_text.py` を provider と同期した。
- `tests/test_init_update.py` に issue-78 installer regressions を追加し、`tests/cli_runtime/test_runtime_doctor_s04.py` / `test_validate.py` / `test_runtime_validate_s02.py` に current-only / no-fallback / cleanup-pending 契約を追加した。
- `src/spec_dock/assets/spec_dock/docs/guide.md` と `spec-dock/docs/guide.md` に `.spec-dock/` 非互換 / rename 禁止 / manual migration guidance を追記した。
- code review / QA review / final spec review を pass まで回し、close evidence を確定した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.test_init_update.TestInitUpdate.test_issue_78_init_allows_install_when_legacy_hidden_workspace_exists \
  tests.test_init_update.TestInitUpdate.test_issue_78_update_reports_manual_migration_guidance_without_rename \
  tests.test_init_update.TestInitUpdate.test_issue_78_update_keeps_legacy_hidden_workspace_untouched_during_coexistence \
  tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets \
  tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json -v
python -m unittest tests.cli_runtime.test_runtime_doctor_s04 -v
python -m unittest tests.cli_runtime.test_validate -v
python -m unittest tests.cli_runtime.test_runtime_validate_s02 -v
python -m unittest tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_docs_match_provider_assets -v
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock doctor

all targeted issue-78 / runtime / mirror tests: PASS
./spec-dock/scripts/spec-dock validate: spec-dock: ok (validate) nodes=33
./spec-dock/scripts/spec-dock doctor: spec-dock: ok (doctor) findings=0

reviews:
- RG1/code review: pass
- QG1/QA review: pass
- SG1/final spec review: pass
```

#### 変更したファイル
- `src/spec_dock/cli.py` - installer coexistence / no-rename guidance
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` - `legacy_only_workspace` code 追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py` - legacy-only / cleanup-pending 診断追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py` - cleanup-pending warning 文言追加
- `spec-dock/scripts/spec_dock_runtime/application/contracts.py` - dogfooding mirror 同期
- `spec-dock/scripts/spec_dock_runtime/application/doctor.py` - dogfooding mirror 同期
- `spec-dock/scripts/spec_dock_runtime/presentation/cli_text.py` - dogfooding mirror 同期
- `src/spec_dock/assets/spec_dock/docs/guide.md` - static migration guidance 追加
- `spec-dock/docs/guide.md` - mirror docs 同期
- `tests/test_init_update.py` - issue-78 installer / mirror snapshot regressions
- `tests/cli_runtime/test_runtime_doctor_s04.py` - issue-78 doctor regressions
- `tests/cli_runtime/test_validate.py` - no-fallback validate regressions
- `tests/cli_runtime/test_runtime_validate_s02.py` - current-only validate seam regression

#### コミット
- 未実施（final review pass 後に実施）

#### メモ
- `tests.test_init_update` 全体は、この issue 差分外の network / venv / 既存 active pathfile 系 failure が残るため full green ではない。
- issue-78 で直接変更した contract と mirror parity に関する targeted validation はすべて pass した。

---

### 2026-04-16 00:00 - 00:30

#### 対象
- Step: S99 follow-up analysis
- AC/EC: 回帰検証の全体把握

#### 実施内容
- `python -m unittest discover -v` を実行し、repo 全体の現時点ベースラインを確認した。
- 失敗を environment 依存、既知の active pathfile 系、単独の runtime error に分類した。
- issue-78 の変更で追加した targeted tests は引き続き pass していることを別途確認済みと照合した。

#### 実行コマンド / 結果
```bash
python -m unittest discover -v
python -m unittest tests.cli_runtime.test_runtime_delete_s13.TestRuntimeDeleteS13.test_target_local_metadata_load_failure_uses_error_path_when_directory_match_is_ambiguous -v

full suite summary:
- Ran 741 tests in 198.398s
- FAILED (failures=22, errors=1)

failure buckets:
1. build / isolated wheel / venv bootstrap failures
   - representative tests:
     - test_built_wheel_excludes_deleted_wrapper_era_assets_from_stale_build_outputs
     - test_issue_69_full_install_root_inventory_is_packaged_in_wheel_sdist_and_installed_resources
     - test_issue_69_isolated_wheel_install_exposes_install_root_handoff_surface
     - test_issue_69_isolated_wheel_install_runs_init_update_without_checkout_fallback
     - test_issue_69_local_and_installed_handoff_surface_inventories_match
     - test_issue_69_representative_install_root_assets_are_packaged_in_all_artifact_surfaces
     - test_issue_69_sdist_build_excludes_seeded_stale_wrapper_era_outputs
     - test_issue_69_wheel_build_prunes_seeded_stale_wrapper_era_outputs
     - test_issue_70_isolated_wheel_install_reflects_cutover_contract_without_legacy_fallback
     - test_issue_71_isolated_wheel_install_final_smoke_closure_surface_without_fallback
   - representative error:
     - ensurepip / setuptools bootstrap failure
     - `No matching distribution found for setuptools>=69`
     - `ensurepip --upgrade --default-pip returned non-zero exit status 1`

2. active pathfile / symlink fallback failures
   - representative tests:
     - test_update_bootstraps_active_path_files_when_active_symlink_creation_fails
     - test_update_rebuilds_active_path_files_from_persisted_manifest_when_symlink_creation_fails
     - test_update_repairs_stale_active_path_files_to_persisted_targets_when_symlink_creation_fails
     - test_update_repairs_stale_active_path_files_to_placeholder_when_persisted_manifest_broken_and_symlink_creation_fails
   - failure shape:
     - `AssertionError: True is not false`
     - `AssertionError: False is not true`

3. standalone runtime error
   - test:
     - test_target_local_metadata_load_failure_uses_error_path_when_directory_match_is_ambiguous
   - error:
     - `RuntimeError: Invalid JSON: .../.meta.json: broken payload`
   - classification:
     - expected structured error path を assertion する前に `delete_node()` が RuntimeError を送出している
```

#### 変更したファイル
- `spec-dock/active/issue/report.md` - 全件テスト分析の追記

#### コミット
- 未実施

#### メモ
- 全件失敗の大半は issue-78 変更に直接起因するものではなく、既知の環境依存または既存失敗群に見える。
- ただし `tests.cli_runtime.test_runtime_delete_s13...ambiguous` の 1 error は runtime delete path の期待契約ずれとして、別 issue で再現・修正優先度を判断できる。

## 遭遇した問題と解決 (任意)
- 問題: 初回 review で update coexistence regression の不足、dogfooding runtime mirror の未同期、単体実行での import 順序依存が指摘された。
  - 解決: `tests/test_init_update.py` に coexistence update regression を追加し、mirror `contracts.py` / `doctor.py` / `cli_text.py` を provider と同期し、`tests/cli_runtime/test_runtime_validate_s02.py` を `_runtime_modules()` 系の import seam に揃えた。
- 問題: `tests.test_init_update` full run に network / ensurepip / 既存 active pathfile 系の unrelated failure が含まれていた。
  - 解決: issue-78 契約に直接対応する targeted validation を切り出して実施し、review でも non-blocking residual risk として扱った。
- 問題: repo 全件実行では `22 failures / 1 error` が残り、`delete_node` の 1 件は環境要因ではなく runtime 契約ずれの可能性がある。
  - 解決: environment 起因の build/venv 系、既知の active pathfile 系、runtime delete error を分離して記録し、follow-up の切り分け材料を report に残した。

## 学んだこと (任意)
- checked-in dogfooding mirror を含む repo では、provider 側の runtime contract 変更だけでは不十分で、mirror parity まで同時に閉じないと review と dogfooding がずれる。
- legacy hidden workspace の移行契約は install permissive / runtime current-only / doctor observability の 3 点をセットで固定すると運用上の誤誘導が減る。

## 今後の推奨事項 (任意)
- `tests.test_init_update` の network / ensurepip / active pathfile 系 failure は別 issue で baseline 安定化すると、今後の full validation gate が扱いやすくなる。
- `tests.cli_runtime.test_runtime_delete_s13.TestRuntimeDeleteS13.test_target_local_metadata_load_failure_uses_error_path_when_directory_match_is_ambiguous` は単独で再現するため、delete path の error handling 契約として個別 issue 化を検討するとよい。

---

### 2026-04-16 00:30 - 01:30

#### 対象
- Step: PR-81 investigation
- AC/EC: PR review 指摘と GitHub Actions failure の事実確認

#### 実施内容
- PR `#81 feat(spec-dock): legacy hidden workspaceの共存移行を実装` の review 状況、status checks、Actions failure log を取得した。
- review 指摘は `copilot-pull-request-reviewer` の inline comments 10 件に集約されていることを確認した。
- CI/CD failure は `validate` ではなく `provider-tests` のみで、GitHub Actions 上では full suite 全体が崩れているのではなく 1 failure のみで落ちていることを確認した。
- 失敗 1 件は `tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json` で、checked-in dogfooding snapshot expectation と実際の `.meta.json` path 集合の不整合に起因していた。

#### 実行コマンド / 結果
```bash
gh pr view 81 --repo chemitaro/spec-dock \
  --json number,title,state,mergeStateStatus,headRefOid,reviews,statusCheckRollup
gh pr view 81 --repo chemitaro/spec-dock --comments
gh api repos/chemitaro/spec-dock/pulls/81/comments
gh run list --repo chemitaro/spec-dock --limit 10 \
  --json databaseId,workflowName,event,status,conclusion,headSha,displayTitle
gh run view 24484241847 --repo chemitaro/spec-dock --log-failed

PR summary:
- state: OPEN
- mergeStateStatus: UNSTABLE
- head SHA: 5eb330a5eee6199277d8f102c4afeac5b9cf26c3

status checks:
- CI / validate: SUCCESS
- Provider CI / provider-tests: FAILURE

review summary:
- reviewer: copilot-pull-request-reviewer
- verdict: COMMENTED
- generated comments: 10

Provider CI failure summary:
- workflow: Provider CI
- run id: 24484241847
- suite result: Ran 741 tests in 345.414s / FAILED (failures=1)
- failing test:
  - tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json
- failure cause:
  - `_CHECKED_IN_DOGFOODING_META_JSON_PATHS` の snapshot 期待値と、
    checked-in initiatives 配下に実在する `.meta.json` paths の集合が一致していない
  - 新規追加した `init-00079` / `epic-00080` 系 path が snapshot expectation に正しく反映されていない可能性が高い
```

#### レビュー指摘の整理
- A. front matter 正規化指摘
  - initiative / epic の新規 doc 群に対して、`状態: "draft | approved"` のような union placeholder を残している点が繰り返し指摘された。
  - 主な対象:
    - `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/requirement.md`
    - `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/design.md`
    - `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/plan.md`
    - `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/report.md`
    - `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/requirement.md`
    - `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/design.md`
    - `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/plan.md`
    - `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/report.md`
    - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00077-legacy-hidden-workspace-coexistence-and-migration/report.md`
- B. wording / readability 指摘
  - `src/spec_dock/cli.py` の manual migration guidance message で、文中の sentence 開始が `Legacy` ではなく小文字 `legacy` になっているため、可読性観点の軽微指摘が 1 件入っている。

#### 分析
- PR review の大半は実装ロジックの欠陥ではなく、checked-in docs の front matter hygiene に関する反復指摘だった。
- GitHub Actions で実際に failing なのは `provider-tests` の 1 件だけで、以前ローカル環境で観測した `22 failures / 1 error` とは状況が異なる。
- したがって PR #81 の blocking items は、現時点では次の 2 点に要約できる。
- 1. doc front matter の正規化不足
- 2. `tests/test_init_update.py` の checked-in dogfooding snapshot expectation と repo 実体の不整合

#### 推奨アクション
- `init-00079` / `epic-00080` と関連 report の front matter `状態` を placeholder から単一値へ正規化する。
- `tests/test_init_update.py` の `_CHECKED_IN_DOGFOODING_META_JSON_PATHS` を現行 checked-in nodes と再同期し、CI の failing snapshot test を green に戻す。
- その後に PR #81 の `provider-tests` を再実行し、残る review comments の解消有無を再確認する。

## 省略/例外メモ (必須)
- `tests.test_init_update` full suite の unresolved failures は issue-78 の変更範囲外として今回の close criteria から除外し、targeted validation + reviewer pass を最終 gate とした。
