# 旧四CLI adapter suiteの退役判断

Issue #413 / P-12。中央control、registered worktree、fixed engineを前提にした旧dispatcherの最後の四test filesを全文確認した。公開CLI `spec_dock.cli.main` を使う既存後継suiteへ一件ずつ対応づける。passing testの数を維持するために同じ保証を重複させず、旧実装を参照するfixtureと十二関数を退役する。pytestのskipや収集除外は追加しない。

## Installation show（四関数）

後継: `tests/integration/test_issue413_assets.py`。

| 旧関数 | 判断と後継保証 |
| --- | --- |
| `test_installation_show_reports_bound_engine_and_installed_worktrees` | bound engine/control/全WT inventoryは廃止。`test_installation_show_does_not_require_a_workspace_or_control_record` が一つの指定WT・package version・効果0を検査する。 |
| `test_installation_show_rejects_unregistered_target` | registrationは不要。非Git directoryだけはnative Git失敗として拒否する新 `test_installation_show_preserves_a_non_git_target_and_reports_the_native_git_error` で補う。旧exit3へエラーを隠蔽せずv2/exit5/raw argv・stderrを確認する。 |
| `test_installation_group_fixes_every_registered_git_worktree` | whole group固定は廃止。`test_init_in_a_linked_worktree_does_not_install_into_main_or_shared_git` が指定linked WTだけをinit/showしmain/common Gitの不変を検査する。 |
| `test_installation_group_rejects_foreign_git_worktree` | native linked WTを未登録という理由で拒否する旧条件は逆向きのため廃止。同上のpublic linked WT試験がregistration不要の後継を検査する。 |

## Dependency（二関数）

後継: `tests/cli_runtime/test_issue413_dependency.py`。

| 旧関数 | 判断と後継保証 |
| --- | --- |
| `test_dependency_list_and_check_cli_use_same_scope_graph` | metadataの継承とdefault unknownを維持。`test_dependency_list_derives_inherited_edges_from_current_metadata_without_control`、`test_dependency_check_defaults_to_unknown_github_state_and_never_reads_retired_cache`、`test_live_dependency_check_fetches_only_the_target_chain_and_effective_prerequisites` へ対応する。v2のeffective resultを使い、旧declared_by出力schemaへ戻さない。 |
| `test_dependency_change_cli_previews_and_applies_one_edge` | `test_dependency_add_updates_only_the_source_metadata_and_preserves_optional_fields`、`test_dependency_add_dry_run_plans_edges_without_creating_stage_or_changing_metadata`、`test_dependency_remove_and_missing_ok_keep_absence_distinct_from_a_changed_edge` がrevision・preview・add/remove・missing_ok・入力保全を検査する。 |

## Artifact（四関数）

後継: `tests/cli_runtime/test_issue413_artifact.py`。

| 旧関数 | 判断と後継保証 |
| --- | --- |
| `test_artifact_list_show_cli_return_only_catalog_metadata` | `test_root_artifact_catalog_reads_only_identity_without_control_or_body` がopaque bodyを出力せずidentityと元bytesを保持する。 |
| `test_artifact_create_cli_previews_then_publishes_under_local_scope` | six creation types/previewを維持。`test_create_artifact_preserves_six_type_template_and_existing_scope_files`、`test_artifact_dry_run_plans_an_identity_without_directory_stage_or_source_change`、`test_root_create_supports_all_templates_and_preview_without_unrelated_scope_metadata` へ対応する。D-11で認めたroot作成を拒否する旧条件は廃止。新local Scope作成のfixtureも使わない。 |
| `test_artifact_post_publication_io_failure_reports_unknown_local_effect` | owned dispatcherへのmonkeypatchとv1 receiptは廃止。`test_unknown_link_outcome_preserves_artifact_and_candidate_without_automatic_retry`、`test_confirmed_artifact_survives_descriptor_cleanup_failure` がOS境界のunknown/confirmedを分け、公開後のfile保全と自動retryなしを検査する。 |
| `test_artifact_import_cli_keeps_external_file_private` | `test_import_one_opaque_file_to_root_preserves_bytes_name_source_and_privacy`、`test_artifact_dry_run_plans_an_identity_without_directory_stage_or_source_change` がsource path/bodyの非開示、opaque bytesとpreview書込0を検査する。 |

## Workbench（二関数）

後継: `tests/cli_runtime/test_issue413_workbench.py`。

| 旧関数 | 判断と後継保証 |
| --- | --- |
| `test_copy_local_scope_defaults_to_conflict_error_and_supports_explicit_overwrite` | registered alias/old private copy入口は廃止。`test_copy_publishes_scope_file_to_native_linked_worktree_without_control`、`test_default_conflict_preflights_every_file_before_creating_any_destination_entry`、`test_overwrite_replaces_complete_file_and_preserves_destination_only_evidence` がnative path・conflict前の書込0・explicit overwriteと既存証拠を検査する。 |
| `test_workbench_copy_cli_preview_conflict_and_explicit_overwrite` | `test_overwrite_requires_confirmation_and_dry_run_leaves_missing_destination_absent`、同上conflict/overwrite試験がpreview・confirmation・成功後bytesを検査する。native absolute pathへ統一し新コマンドは増やさない。 |

## 証拠の境界

四ファイルへのsource/test importはなかった。旧dispatcherのtest importもこの四ファイルが最後だった。新Installation show一件は既存実装のGreen回帰であり、製品Redではない。後継四suiteの実行結果はimplementation-reportに記録する。source側の旧dispatcher・command・controlの削除は別の参照閉包監査で行い、このtest退役だけで完了とは扱わない。
