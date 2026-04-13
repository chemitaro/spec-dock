---
種別: 実装報告書（Issue）
ID: "iss-00070"
タイトル: "Installer source discovery and managed ownership"
関連GitHub: ["#70"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-13"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00070 Installer source discovery and managed ownership — 実装報告（LOG）

## 実装サマリー
- `S01` で installer の canonical input を `install_root` authority へ切り替え、host-adapters manifest の top-level obsolete exact path schema を固定した。
- current managed inventory は `install_root` recursive file inventory から構築されるようになり、workflow を含む current managed set と top-level obsolete set の overlap / invalid manifest は fail-closed で拒否される。

## 実装記録（セッションログ） (必須)

### 2026-04-13 00:00 - 00:00

#### 対象
- Step: S01
- AC/EC: AC-003, AC-005(manifest-invalid branch)

#### 実施内容
- `_HOST_ADAPTER_META_ASSET_REL` を `install_root/.agents/host-adapters/meta.json` へ切り替えた。
- `install_root/.agents/host-adapters/meta.json` を top-level `managed_assets.obsolete_exact_file_paths` schema へ更新し、required host `source_of_truth_asset` を `install_root/...` relative path に固定した。
- `_ManagedSkillInstallPlan` を `current_file_mappings` / `obsolete_exact_rel_paths` を持つ形へ拡張し、`install_root` recursive inventory から current managed set を構築するよう変更した。
- top-level obsolete exact path に対して namespace / duplicate / overlap / current-directory / directory-like / windows-drive / parent-traversal の fail-closed validation を追加した。
- `tests/test_init_update.py` に S01 向けの inventory / malformed manifest / overlap negative regression を追加し、旧 host-local obsolete path 前提の negative tests を top-level schema 前提へ更新した。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.test_init_update.TestInitUpdate.test_init_installs_host_adapter_metadata_with_fixed_contract tests.test_init_update.TestInitUpdate.test_issue_70_build_plan_uses_install_root_recursive_inventory_including_workflow tests.test_init_update.TestInitUpdate.test_issue_70_update_rejects_missing_or_invalid_managed_assets_obsolete_manifest tests.test_init_update.TestInitUpdate.test_issue_70_update_rejects_current_obsolete_overlap_before_writes tests.test_init_update.TestInitUpdate.test_update_rejects_current_dir_obsolete_exact_file_paths tests.test_init_update.TestInitUpdate.test_update_rejects_directory_like_obsolete_exact_file_paths tests.test_init_update.TestInitUpdate.test_update_rejects_parent_traversal_native_shim_paths tests.test_init_update.TestInitUpdate.test_update_rejects_windows_drive_relative_native_shim_paths tests.test_init_update.TestInitUpdate.test_update_rejects_obsolete_exact_file_paths_outside_managed_prefixes tests.test_init_update.TestInitUpdate.test_update_rejects_required_host_native_shim_target_file_swaps tests.test_init_update.TestInitUpdate.test_init_preflight_rejects_invalid_host_manifest_before_scaffold_write tests.test_init_update.TestInitUpdate.test_update_rejects_non_mapping_host_target_entries

----------------------------------------------------------------------
Ran 12 tests in 1.181s

OK
```

#### 変更したファイル
- `src/spec_dock/cli.py` - `install_root` authority、current inventory builder、top-level obsolete exact path validation を追加
- `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json` - issue-70 canonical manifest schema へ更新
- `tests/test_init_update.py` - S01 regression と top-level manifest negative tests を追加 / 更新

#### レビュー
- spec review:
  - requirement/design/plan:
    - `pass`
- code review:
  - verdict:
    - `pass`
  - note:
    - non-blocking 指摘として、validated obsolete exact path 全 namespace への cleanup 適用はまだ `_apply_managed_skill_install_plan` 側で未実装のため S02 で閉じる

#### コミット
- `8d3e0e8` `feat(installer): install_root正本の事前検証を導入`

#### メモ
- directory-like obsolete path は `.codex/agents/legacy` のような extensionless path を fail-closed で拒否するよう補強した。
- cleanup 実行順と obsolete path 全 namespace 適用は S02 の責務として残している。

---

### 2026-04-13 00:00 - 00:00

#### 対象
- Step: S02
- AC/EC: AC-001, AC-002, AC-004, AC-005(target-conflict branch), AC-006, EC-001, EC-002, EC-003

#### 実施内容
- target repo に対する current/obsolete exact file path の directory/container conflict preflight を追加し、`init/update` ともに `_install_spec_dock` 前で fail-closed になるようにした。
- current sync source を `plan.current_file_mappings` に統一し、workflow を含む `install_root` inventory から actual copy されるようにした。
- apply pipeline を `current sync -> post-sync verify -> obsolete exact cleanup` の順に揃え、verify failure 時は cleanup を実行しないようにした。
- obsolete cleanup の適用範囲を top-level `managed_assets.obsolete_exact_file_paths` 全体へ拡張し、native shim prefix 限定を撤廃した。
- current managed path replacement、custom unmanaged path preservation、legacy `codex_skills` duplicate 非参照、source-side transition coverage を regression として追加した。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.test_init_update.TestInitUpdate.test_issue_70_init_rejects_current_managed_directory_conflict_before_writes tests.test_init_update.TestInitUpdate.test_issue_70_init_rejects_current_managed_container_file_conflict_before_writes tests.test_init_update.TestInitUpdate.test_issue_70_update_rejects_current_managed_directory_conflict_before_writes tests.test_init_update.TestInitUpdate.test_issue_70_update_rejects_obsolete_managed_directory_conflict_before_writes tests.test_init_update.TestInitUpdate.test_issue_70_update_syncs_workflow_and_prunes_obsolete_exact_workflow_only tests.test_init_update.TestInitUpdate.test_issue_70_update_skips_obsolete_cleanup_when_post_sync_verify_fails tests.test_init_update.TestInitUpdate.test_update_manages_native_shims_with_gate_2_five_subchecks tests.test_init_update.TestInitUpdate.test_issue_70_update_reflection_ignores_legacy_codex_skills_duplicates tests.test_init_update.TestInitUpdate.test_issue_70_provider_transition_detects_removed_current_paths_without_obsolete_coverage tests.test_init_update.TestInitUpdate.test_issue_70_provider_transition_accepts_removed_current_paths_with_obsolete_coverage tests.test_init_update.TestInitUpdate.test_init_generated_native_shims_satisfy_static_delegation_only_contract tests.test_init_update.TestInitUpdate.test_update_copies_legacy_codex_native_shim_instructions_key_as_is tests.test_init_update.TestInitUpdate.test_init_copies_legacy_codex_native_shim_instructions_key_as_is tests.test_init_update.TestInitUpdate.test_update_copies_codex_native_shim_without_instruction_keys_as_is tests.test_init_update.TestInitUpdate.test_issue_70_build_plan_uses_install_root_recursive_inventory_including_workflow tests.test_init_update.TestInitUpdate.test_issue_70_update_rejects_missing_or_invalid_managed_assets_obsolete_manifest tests.test_init_update.TestInitUpdate.test_issue_70_update_rejects_current_obsolete_overlap_before_writes tests.test_init_update.TestInitUpdate.test_init_preflight_rejects_invalid_host_manifest_before_scaffold_write

----------------------------------------------------------------------
Ran 18 tests in 1.045s

OK
```

#### 変更したファイル
- `src/spec_dock/cli.py` - target conflict preflight、current sync、post-sync verify、obsolete exact cleanup を issue-70 contract に合わせて再構成
- `tests/test_init_update.py` - S02 の conflict / workflow / cleanup / legacy divergence / transition regression を追加

#### レビュー
- code review:
  - verdict:
    - `pass`
  - note:
    - `8d3e0e8` を基準にした未コミット S02 diff に対して、high-impact blockers なし

#### コミット
- `936e5fd` `feat(installer): current同期とobsolete cleanupを切替`

#### メモ
- workflow obsolete cleanup は manifest override fixture で contract を担保しており、default manifest 値そのものはこの step では増やしていない。
- legacy `codex_skills` duplicate は source discovery から外れたが、physical deletion や final cleanup は issue-72 へ残している。

---

### 2026-04-13 00:00 - 00:00

#### 対象
- Step: S03
- AC/EC: AC-007

#### 実施内容
- issue-69 の isolated non-editable wheel install harness を再利用し、package-installed `spec-dock init/update` が issue-70 cutover contract を満たす regression を追加した。
- installed package の `site-packages` assets から plan snapshot を取得し、current managed source がすべて `install_root/...` であり、legacy `codex_skills` が source discovery に含まれないことを検証した。
- package-installed runtime で `.agents`、`.codex`、`.github`、`.github/workflows` の current managed files が canonical relative path のまま反映されることを確認した。
- package-installed update で obsolete exact paths だけが削除され、managed 外 custom skill / codex agent / workflow は保持されることを検証した。
- installed assets 配下の legacy `codex_skills` duplicate を stale content / invalid JSON に変えても、target repo には installed `install_root` content だけが反映されることを確認した。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.test_init_update.TestInitUpdate.test_issue_70_isolated_wheel_install_reflects_cutover_contract_without_legacy_fallback tests.test_init_update.TestInitUpdate.test_issue_69_isolated_wheel_install_runs_init_update_without_checkout_fallback

----------------------------------------------------------------------
Ran 2 tests in 9.165s

OK
```

#### 変更したファイル
- `tests/test_init_update.py` - installed plan snapshot helper と package-installed issue-70 cutover regression を追加

#### レビュー
- code review:
  - verdict:
    - `pass`
  - note:
    - new helper / new test の scope は S03 意図と一致し、P0/P1 指摘なし

#### コミット
- pending:
  - S03 stage commit を次に作成する

#### メモ
- test は local wheelhouse と temp venv を使うため、issue-69 の hermetic build/install contract を前提にしている。

## 遭遇した問題と解決 (任意)
- 問題: ...
  - 解決: ...

## 学んだこと (任意)
- ...
- ...

## 今後の推奨事項 (任意)
- ...
- ...

## handoff-validation-evidence (必須)
- source inventory / manifest assertions:
  - test_or_command:
    - `python -m unittest -v tests.test_init_update.TestInitUpdate.test_init_installs_host_adapter_metadata_with_fixed_contract tests.test_init_update.TestInitUpdate.test_issue_70_build_plan_uses_install_root_recursive_inventory_including_workflow`
  - assertion_summary:
    - `install_root/.agents/host-adapters/meta.json` が issue-70 canonical schema を満たし、current managed inventory は workflow を含む `install_root` recursive file inventory と一致する
  - result:
    - pass
- invalid manifest negative test coverage:
  - test_or_command:
    - `python -m unittest -v tests.test_init_update.TestInitUpdate.test_issue_70_update_rejects_missing_or_invalid_managed_assets_obsolete_manifest tests.test_init_update.TestInitUpdate.test_issue_70_update_rejects_current_obsolete_overlap_before_writes tests.test_init_update.TestInitUpdate.test_update_rejects_current_dir_obsolete_exact_file_paths tests.test_init_update.TestInitUpdate.test_update_rejects_directory_like_obsolete_exact_file_paths tests.test_init_update.TestInitUpdate.test_update_rejects_parent_traversal_native_shim_paths tests.test_init_update.TestInitUpdate.test_update_rejects_windows_drive_relative_native_shim_paths tests.test_init_update.TestInitUpdate.test_update_rejects_obsolete_exact_file_paths_outside_managed_prefixes`
  - assertion_summary:
    - missing / null / wrong-type `managed_assets`、overlap、current-directory、directory-like、outside-prefix、windows-drive、parent-traversal の obsolete exact path はすべて write 前に fail-closed で拒否される
  - result:
    - pass
- current managed / obsolete managed boundary assertions:
  - test_or_command:
    - `python -m unittest -v tests.test_init_update.TestInitUpdate.test_issue_70_init_rejects_current_managed_directory_conflict_before_writes tests.test_init_update.TestInitUpdate.test_issue_70_init_rejects_current_managed_container_file_conflict_before_writes tests.test_init_update.TestInitUpdate.test_issue_70_update_rejects_current_managed_directory_conflict_before_writes tests.test_init_update.TestInitUpdate.test_issue_70_update_rejects_obsolete_managed_directory_conflict_before_writes tests.test_init_update.TestInitUpdate.test_issue_70_update_syncs_workflow_and_prunes_obsolete_exact_workflow_only tests.test_init_update.TestInitUpdate.test_issue_70_update_skips_obsolete_cleanup_when_post_sync_verify_fails tests.test_init_update.TestInitUpdate.test_issue_70_update_reflection_ignores_legacy_codex_skills_duplicates tests.test_init_update.TestInitUpdate.test_issue_70_provider_transition_detects_removed_current_paths_without_obsolete_coverage tests.test_init_update.TestInitUpdate.test_issue_70_provider_transition_accepts_removed_current_paths_with_obsolete_coverage`
  - assertion_summary:
    - current managed / obsolete exact path の directory/container conflict は write 前に fail-closed で拒否される
    - workflow を含む current managed files は canonical asset で sync され、obsolete exact path だけが cleanup される
    - verify failure 時は obsolete cleanup がスキップされ、custom unmanaged path は保持される
    - legacy `codex_skills` duplicate は reflection authority を持たず、removed current path は obsolete-or-transfer coverage が必要
  - result:
    - pass
- installed-package cutover evidence:
  - test_or_command:
    - `python -m unittest -v tests.test_init_update.TestInitUpdate.test_issue_70_isolated_wheel_install_reflects_cutover_contract_without_legacy_fallback tests.test_init_update.TestInitUpdate.test_issue_69_isolated_wheel_install_runs_init_update_without_checkout_fallback`
  - assertion_summary:
    - package-installed runtime でも current managed source は installed `install_root` 由来であり、`.agents/.codex/.github/.github/workflows` が canonical relative path のまま反映される
    - obsolete exact paths だけが削除され、managed 外 custom files は保持される
    - checkout fallback と legacy `codex_skills` source discovery に依存しない
  - result:
    - pass

## 省略/例外メモ (必須)
- S01 では `_apply_managed_skill_install_plan` の sync/verify/cleanup ordering は未変更。
- validated obsolete exact path 全 namespace への cleanup 適用は code review P2 として S02 に持ち越した。
