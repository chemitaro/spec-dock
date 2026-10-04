# Workspace migrate / syncのテスト移行

変更前は `26560fa00c9b9503616a8b90d341eb3e18add65e`。旧二ファイル・十二関数を全文確認し、RQ-413-10/17/18、D-09/D-10/D-11/D-12とCLI v2へ照合した。移行は自workspace宣言だけ、Syncは都度読取だけとする。旧control登録・mapping・operation journal・local新規発行・生成cacheを通常入口へ復活させない。

| 旧test | 後継・判断 |
|---|---|
| migrate `test_workspace_migrate_dry_run_inventories_all_worktrees` | native main/linkedを作り、別WTの未知宣言は保持したまま、自分の宣言一fileだけをpreviewする。全tree/他WT不変、backup/state作成0。旧全WTの登録inventory・repository UID出力を撤去。実Git inventoryの整合性検査は維持 |
| migrate `test_workspace_migrate_dry_run_requires_exact_mapping_inventory` | mapping-fileはproject/ファイル読取前のexit2へ。旧全WT/backend/binding mappingは確定方式の入力ではない。現物保全の検査はself applyと現行migration suiteで維持 |
| migrate `test_migration_plan_parses_the_same_mapping_bytes_as_its_identity` | mapping読取自体を撤去。schema3の実workspace bytes/identity・保全物を捕捉して検証する現行migrationへ。旧mapping private readerのmockを保持しない |
| migrate `test_mapping_snapshot_rejects_path_swap_before_descriptor_open` | 旧mapping inputのcodecは通常経路から撤去。現在のbackup差替え/入力改変/descriptor安全性は `test_migration_rechecks_verified_backup_before_publication`、`test_migration_detects_an_unrelated_user_edit_after_backup_and_leaves_it_intact` とdirect JSON/backup adapter試験へ |
| migrate `test_workspace_migrate_apply_and_rollback_use_fixed_operation_id` | 公開mainで承認不足write0→実backup/restore検証→自宣言だけ更新・全Scope bytes保持を確認。old rollbackはsyntax拒否し現在tree不変。operation ID・journal replay・全schema変換は撤去 |
| migrate `test_workspace_migrate_confirmation_rejects_mapping_swap` | mappingと端末対話は撤去。applyは--backup-dir ABS/--confirm-old-writers-stopped/--yesの三明示入力を要求し、その欠落は現行 `test_migration_requires_every_apply_confirmation_before_any_write` で効果前停止。途中の現物変更は同suiteのbackup/input OCCで保護 |
| migrate `test_workspace_migrate_confirmation_shows_write_paths_and_applies_fixed_plan` | JSON previewのplanned_pathsを自宣言一fileへ固定し、applyのchanged_paths/verified backup/restoreを現物へ比較。三明示入力なしのTTY回答だけで実行する旧契約は復活させない |
| sync `test_workspace_sync_cli_preview_and_publish_preserve_selection` | 公開mainの通常/dry-runとも記録・全tree・opaque旧generation不変。dry-run status=plannedは公開dispatcherの共通契約。source=local、selection/count/lifecycleを返し、generation ID・保存出力を撤去 |
| sync `test_empty_and_local_workspace_sync_leave_selection_unchanged` | 真正の既存local codecのopen lifecycleと未選択count0、空treeのcomplete/scopes/countsを全tree不変として保護。new local create fixtureは使わない |
| sync `test_live_failure_is_incomplete_and_does_not_mark_unknown_fresh` | 実external ghのGET失敗でpartial/exit7、complete=false、unknown lifecycle、exact ref finding、記録/全tree不変を確認。offlineとcache fallback拒否は既存公開sync suiteで維持 |
| sync `test_invalid_parent_requires_diagnostic_opt_in` | 安全に解釈できないparent metadataを、通常/--allow-invalidともfailed/7・SYNC_INPUT_INVALID・write0とする。表示可能な不完全観測は現行sync suiteのancestry/selection conflictでpartialとして維持。--allow-invalidでmetadata安全性や未知schemaを迂回しない |
| sync `test_projection_failure_keeps_generation_readable` | 保存projection・generation書込みはD-10/D-11で撤去。opaque旧generationを公開Syncが書換え/修復/採用しない後継へ。存在しない公開処理をowned atomic_write mockで故障させる試験は撤去 |

後継二ファイルは九cases。旧metadata/active/cacheは実consumerで編集しない。hermetic/native Git fixtureと現行integration suiteで維持保証を確認し、通常全体suiteのskip・除外は追加しない。

初回の一失敗は、dry-runの公開statusをsucceededと期待したものだった。use caseの戻り値は公開dispatcherがplannedへ正規化するため、preview=plannedへ訂正した。source/state/effects/bytesの保証は変えず、製品Redには数えない。
