# 旧group installation / finalization / engine handover試験の退役

D-11/D-12/RQ-413-16に基づき、旧四ファイルの**54関数**（8/7/6/33）を個別に照合した。全worktree登録・central control・epoch・fixed engine pin・journal resume/rollback・whole-group finalizationを成功させる試験は、新仕様と逆向きのため削除する。通常pytestからの条件除外やskipを追加せず、現行公開入口の試験で必要な安全性を維持する。

四ファイル間のfixture importは二箇所だけで、他のsource/testsからのimportはないことをrgで確認した。四ファイルを一緒に退役し、fixtureを互換aliasとして残さない。製品側の旧sourceは別stepで参照閉包を検査して退役する。

後継は `test_issue413_assets.py`、通常wheelの公開entrypoint/CI、provider distribution、writer-admission、Doctor/migrationのsuiteである。既知資産だけのhash照合、明示確認/preview、局所変更、実backup/restore、未知改変・unsafe path拒否、partial/unknown表示、仕様とignored成果物の保全を維持する。

追加した公開static update/uninstallの二casesは、外部backupのnative fsync後に別actorが入力資産を**同じbytes/mode・別inode**へ差し替える。公開CLIはpartial/6で停止し、backup/restore成功を返し、変更/削除は全件not_attemptedとなる。actorのinode/bytes、target tree、Git tree、実backupを保持する。所有する内部moduleをmockせず、OSのfsync境界で現物の外部変更を行う。この追加は既存実装のcharacterizationであり、製品Redではない。

## tests/integration/test_engine_handover_vnext.py

| 旧test関数 | 判断と後継の保証 |
|---|---|
| `test_engine_handover_rotates_locator_and_all_registrations` | locator/control/registrationの回転を廃止。通常wheel/consoleの独立起動は公開entrypoint suite、静的資産の局所変更はassets suiteで確認。 |
| `test_engine_handover_resumes_after_locator_publish` | locator公開後のresumeを廃止。旧optionは公開assets/recovery suiteで拒否。不明効果と保全は局所installationのpartial試験で維持。 |
| `test_engine_handover_rolls_back_before_other_writes` | engine handoverのrollbackを廃止。旧Git領域を書き戻さず、新しい明示操作だけを許す退役診断を確認。 |
| `test_engine_handover_resumes_after_control_publish` | control公開後のresumeを廃止。現行installationはcontrolを作成・更新しない。公開init/updateのGit tree不変とpartial効果を検査。 |
| `test_engine_handover_rollback_rejects_later_control_epoch` | control epochによるrollback契約を廃止。新writerは旧epochへ接続しない。変更済み現物の保全は新しい同bytes差替え試験で維持。 |
| `test_external_entrypoint_allows_only_recorded_engine_handover` | 記録済みhandoverだけの起動制限を廃止。通常entrypointは旧locator有無/破損に依存せず動く公開wheel suiteへ移行済み。 |
| `test_engine_handover_cli_uses_new_engine_with_old_control` | 旧controlと新engineのhandoverを廃止。--activate-engineはARGUMENT_RETIREDで拒否し、旧エンジンへfallbackしない。 |
| `test_commit_pinned_update_can_finalize_after_engine_handover` | commit pinとfinalizeを廃止。外部package更新と各WTのstatic操作へ分離。--commit/--finalizeは副作用前拒否。 |

## tests/integration/test_installation_finalize_vnext.py

| 旧test関数 | 判断と後継の保証 |
|---|---|
| `test_finalize_records_group_then_restores_ready` | whole-group ready/maintenance切替を廃止。明示一WTの公開static init/updateとGit tree不変を確認。 |
| `test_finalize_rejects_noncanonical_installed_version` | installed versionとfixed engine versionの全WT照合を廃止。package resourcesのhash/既知旧hash照合と未知改変拒否を維持。 |
| `test_finalize_resumes_recorded_attempt_after_control_write_stops` | control更新のfinalization resumeを廃止。公開--finalize/--resume拒否、局所partial publication/backup保全へ移行。 |
| `test_ready_control_remains_blocked_until_commit_marker_is_recovered` | 中央commit markerで全writerを止める契約を廃止。自WT宣言のadmissionと旧診断のread-only分離をwriter-admission/Doctor suiteで維持。 |
| `test_installation_update_finalization_cli_needs_no_second_archive` | finalize時のarchive再取得経路を廃止。installationは外部packageのstatic resourcesだけを使い、--finalizeを拒否。 |
| `test_installation_finalization_dry_run_checks_targets_without_writing` | whole-group finalization previewを廃止。現行static update/uninstall previewのeffect planned・tree/backup不変を維持。 |
| `test_finalization_rejects_mixed_workspace_before_publishing_record` | 全WT mixed schemaのfinalization gateを廃止。自WT宣言のfail-closedだけを維持し、別WTの宣言へ一括変更しない。 |

## tests/integration/test_installation_group_init_vnext.py

| 旧test関数 | 判断と後継の保証 |
|---|---|
| `test_init_installs_all_worktrees_and_marks_control_ready` | 全WT初期化とready controlを廃止。公開linked init/update/uninstall試験で明示一WTだけの変更とmain/common-dir不変を確認。 |
| `test_init_resumes_after_first_worktree` | 一WT完了後のgroup resumeを廃止。現行initはpartialと各not_attemptedを返す。公開--resumeを拒否し、現物を観測し直す。 |
| `test_init_rollback_restores_fresh_state_and_allows_retry` | fresh stateへの自動rollbackを廃止。公開initの既存path拒否・既存bytes保全とpartial表示を維持。 |
| `test_init_rollback_refuses_later_consumer_changes` | rollback前の後続編集検査を廃止。rollback入口拒否、現行staticの未知改変/同bytes差替え拒否で編集保全を維持。 |
| `test_init_accepts_the_executing_packaged_assets` | 実行中fixed engineとasset bundleの整合APIを廃止。provider distribution、wheel収録、Traversable archiveのstatic resources照合を維持。 |
| `test_installation_init_cli_previews_and_requires_confirmation` | 旧init adapterを廃止。公開initのpreview/--yes/既存先拒否、局所宣言・static資産だけの公開をassets suiteで維持。 |

## tests/integration/test_installation_group_update_vnext.py

| 旧test関数 | 判断と後継の保証 |
|---|---|
| `test_legacy_update_bootstraps_maintenance_control_without_migrating_data` | maintenance controlをbootstrapする契約を廃止。workspace宣言は独立した明示migrationへ分離し、static updateはScope bytesを変更しない。 |
| `test_legacy_update_cli_dry_run_then_bootstraps` | legacy group dry-run/bootstrapを廃止。現行static update preview/applyで主/linked/Git不変、既知hashだけの変更を検査。 |
| `test_legacy_update_cli_resolves_symlinked_system_tempdir` | fixed archive取得用のTempDirectory経路を廃止。外部package資産はTraversable archive試験で取得し、backup用temporary実体は安全な現物copyとして扱う。 |
| `test_installation_update_requires_confirmation_before_source_fetch` | source fetchを廃止し確認条件を維持。現行updateは--yesと外部backupなしで効果0。GitHub/fixed archive取得を行わない。 |
| `test_installation_update_rejects_another_candidates_assets_before_writes` | 別candidate engineのassets照合を廃止。公開assets inventoryのruntime混入拒否・hash検査と未知改変の効果前拒否を後継とする。 |
| `test_legacy_update_resumes_if_control_publish_stops` | control公開中断のresumeを廃止。旧flagを拒否。新局所publication/retirementのunknownと保全は公開assets suiteで検査。 |
| `test_legacy_update_can_rollback_before_control_is_published` | control未公開時のgroup rollbackを廃止。旧flagを拒否し既存証拠を保持。手動の保全照合はmigration runbookへ移す。 |
| `test_legacy_update_rollback_restores_tooling_and_disables_writer` | tooling全復元とwriter無効化のrollbackを廃止。既知staticだけの変更/保全を維持し、中央writer modeを増やさない。 |
| `test_group_update_keeps_all_worktrees_in_maintenance` | 全WT maintenance滞在を廃止。linked init/update/uninstallで明示WTだけを変更、main/common-dir不変を確認。 |
| `test_existing_group_accepts_new_candidate_assets_only_under_maintenance` | maintenance中だけ別candidateを許す契約を廃止。外部package更新はCLI外、未知staticの上書きは常に拒否。 |
| `test_group_update_resumes_after_one_child_completed` | 子WT完了後のgroup resumeを廃止。新局所操作のpartial/未実施pathを表示し、新しい明示操作へ導く。 |
| `test_group_update_resumes_after_unjournaled_stage` | unjournaled stageのgroup resumeを廃止。新stageの保全/効果表示と旧resume拒否を後継とする。 |
| `test_group_recovers_interrupted_marker_publication_with_fixed_child_record` | fixed child markerのresume/rollbackを廃止。現行partial publication、unknown stage、not_attemptedを検査し、旧journalを移植しない。 |
| `test_group_resume_refuses_target_changed_after_planned_child` | planned child再開の変化検査を廃止。新公開同bytes差替え試験で、backup中に変わった現物を上書き/削除しないことを確認。 |
| `test_group_resume_preserves_original_version_request` | 元version requestをjournalへ保存する契約を廃止。--version/--resumeを公開入口で拒否し、外部package versionを表示する。 |
| `test_commit_origin_resume_ignores_version_alias` | commit由来resumeとversion alias比較を廃止。--commit/--version/--resumeを公開入口で拒否。 |
| `test_group_upgrades_planned_child_origin_from_fixed_parent` | fixed parentからchild originを補完する移行を廃止。新journalを作らず、旧記録はlegacy診断/保全だけで扱う。 |
| `test_group_rollback_rechecks_each_child_after_batch_preflight` | batch rollbackの子再検査を廃止。新公開同bytes差替え試験と未知static拒否により、観測後変更を保全する。 |
| `test_public_update_resume_preserves_source_origin` | public resumeのsource origin保持を廃止。通常wheel配布と副作用前の旧version/commit/resume拒否へ移す。 |
| `test_public_version_alias_update_persists_canonical_identity` | version aliasのgroup canonical化を廃止。外部packageだけをversion authorityとし、CLIでengine sourceを取得しない。 |
| `test_group_commit_refuses_replaced_marker_after_child_apply` | 中央marker差替え検査を廃止。実資産のidentity/bytes再検査と新公開同bytes差替え試験に安全条件を移す。 |
| `test_group_commit_refuses_same_content_published_swap` | whole-group commit時の同bytes inode差替え検査を廃止。新公開static update/uninstall試験で現物inode変化を検出し、変更効果0・backup保全を確認。 |
| `test_finalization_refuses_same_content_published_swap` | finalizationの同bytes差替え検査を廃止。--finalizeを拒否し、新公開static操作のidentity検査で現物を保全。 |
| `test_group_update_rolls_back_a_completed_child` | 完了した子WTのrollbackを廃止。外部backupを残し、成功済み/未実施を公開partialで区別。自動復元をしない。 |
| `test_group_rollback_checks_all_children_before_restoring` | 全子WTのrollback前一括検査を廃止。明示一WTの未知改変拒否と保全を維持し、別WTを復元しない。 |
| `test_installation_update_cli_updates_registered_group` | registered group更新CLIを廃止。公開linked init/update/uninstallはpath指定一WTだけを変更する。 |
| `test_installation_update_cli_rolls_back_without_source` | sourceなしのoffline group rollbackを廃止。公開rollback拒否、局所backup保全・新しい明示操作の契約へ変更。 |
| `test_installation_update_dry_run_preserves_targets` | registered group previewを廃止。現行static previewのtree/Git/backup不変とplanned効果を維持。 |
| `test_group_uninstall_preserves_spec_data_and_can_restore_tooling` | group uninstall/rollbackを廃止。公開uninstallは明示WTの既知資産だけを退役し、仕様・ignored選択・未知extensionを保全。 |
| `test_group_uninstall_resumes_offline_after_one_worktree` | offline group uninstall resumeを廃止。旧flagを拒否。現行retirementのunknown/成功済み効果・backup保全を確認。 |
| `test_installation_uninstall_cli_requires_yes_and_rolls_back_offline` | 全WT uninstallのrollbackを廃止。公開uninstallの--yes、preview/外部backup、仕様と未知fileの保全を維持。 |
| `test_committed_maintenance_update_can_be_rolled_back_before_resume` | committed maintenance updateのrollbackを廃止。旧flagを拒否し、中央mode/epochへの接続0を公開assets試験で確認。 |
| `test_committed_update_rollback_rejects_later_control_epoch` | 後続control epochでrollbackを拒否する契約を廃止。新writerは旧epochをauthorityとせず、現物の入力snapshot再検査へ限定。 |

## 検証

新しいsame-bytes試験はまずupdate一件を実行して1 passed（2.42秒）を確認し、uninstallへ広げた二casesも2 passed（4.52秒）。公開assets/通常wheel/provider/recoveryを合わせて99 passed（74.91秒）。全source/tests Ruff check/format（420 files）、変更一test限定mypy --follow-imports=silent、diff checkも成功した。実consumer、既存linked worktree、旧.git領域、live GitHubの切替は行わない。native Windows、full type/pytest、fresh Strictと最終手動確認は未完了。
