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
- pending:
  - S01 stage commit を次に作成する

#### メモ
- directory-like obsolete path は `.codex/agents/legacy` のような extensionless path を fail-closed で拒否するよう補強した。
- cleanup 実行順と obsolete path 全 namespace 適用は S02 の責務として残している。

---

### 2026-04-13 00:00 - 00:00

#### 対象
- Step: S02, S03, S90, S99
- AC/EC: pending

#### 実施内容
- pending

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
    - pending_until_execution
  - assertion_summary:
    - pending_until_execution
  - result:
    - pending_until_execution
- installed-package cutover evidence:
  - test_or_command:
    - pending_until_execution
  - assertion_summary:
    - pending_until_execution
  - result:
    - pending_until_execution

## 省略/例外メモ (必須)
- S01 では `_apply_managed_skill_install_plan` の sync/verify/cleanup ordering は未変更。
- validated obsolete exact path 全 namespace への cleanup 適用は code review P2 として S02 に持ち越した。
