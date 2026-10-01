# 旧三段Active保存・投影adapterの退役

## 仕様と読取範囲

[RQ-413-04](../requirement.md#rq-413-04)、[D-03](../design.md#d-03)、[D-07](../design.md#d-07)は直接対象一件と現存祖先の導出を採用し、取得はStartだけ、Active setは同一妥当directのunchangedだけとする。D-06/D-07のpartialと解除は自動rollbackを提供しない。

infra/active_store.pyの645行・29 top-level functions、旧二test filesの1067行・18 test関数を全て読んだ。絶対/相対/TYPE_CHECKING/子moduleを含むAST importで、参照は同時に退役する二test filesの八箇所だけ。candidate外のsource/test importは0。setup/pyproject/scripts/CIと文字列参照も照合し、旧静的inventoryの保全用path/hashは維持する。

| 旧source責務 | 判断 |
|---|---|
| load_selection_v3/save_selection_v3 | 三役/revision/focusを固定active.jsonへ保存する旧方式を撤去。現行WorkTargetStoreを保持 |
| legacy manifest normalize/read/write、.work自動prune | 新writerが旧選択を自動取得/書換/削除する機能を撤去。legacy readerはread-onlyの別authority |
| active entry/path/placeholder、symlink/.path/context-pack投影 | 現存祖先を必要時に導出。旧投影へのwriteをしない |
| index-all/tree-all/index/treeのactive patch | cache/派生一覧を更新しない。Syncはその場の観測 |
| managed JSON guard、snapshot/restoreと外部symlink先の復元 | 旧multifile transactionを撤去。現recordのnofollow/identity/bytes/捕捉token解除を別途維持 |

application/set_active.pyとそれを使う残る旧private graphの退役は未完了。このunitはprovider全体の旧Activeを全て削除したという記録ではない。現行直接record・Start lock・ordinary reader・json_storeは削除しない。

## 旧18 testの個別判断

| 旧test関数 | 廃止する旧期待と維持する保証 |
|---|---|
| test_set_active_resolves_id_and_repo_scoped_github_target_without_cli | 任意対象の取得をStartへ限定。同一妥当directのID/short ID/完全ref/@currentは test_active_set_existing_direct_resolves_exact_selectors_without_acquisition_or_remote_calls で維持 |
| test_set_active_all_selectors_avoid_readiness_github_and_git_ports | Startを迂回する取得は廃止。同一directへのunchangedではGH/Start lockなし・Git/file不変を上記公開testで維持。物理Git contextの読取自体は必要 |
| test_repo_scoped_github_target_infers_single_unscoped_legacy_node_without_git | repoのないGH linkageからの推測取得を廃止。test_scope_query_uses_only_exact_imported_github_linkage_and_rejects_ambiguity で完全ref/誤repo/重複/未登録の境界を維持。metadataを書き換える移行はしない |
| test_repo_scoped_github_target_reports_not_found_or_ambiguous_without_writing | 同上の公開query testがexact linkage/不成立時全tree不変を維持。test_active_set_empty_requires_start_without_acquiring_selection が未選択からの取得も拒否 |
| test_active_manifest_and_context_pack_are_structural_only | 三段manifest/context packを生成しない。test_publish_one_immutable_record_without_scope_uuid_or_git_control と test_dynamic_roles_derive_current_ancestors_from_direct_scope で直接一件/導出祖先を検査 |
| test_commit_active_state_rolls_back_every_write_phase_to_legacy_snapshot | legacy/current三段投影とcacheのtransaction/自動rollbackを廃止。test_active_clear_preserves_legacy_manifests_projections_and_cache_bytes でCRLF/不正旧directory/旧cacheを変更せず保全 |
| test_commit_active_state_rolls_back_agent_manifest_verbatim | 旧agent activeの書込/rollbackを廃止。同上の公開clear testで旧manifest bytesを保全。test_legacy_active_is_preserved_but_never_automatically_adopted_after_writer_migration で移行後の非採用も検査 |
| test_commit_active_state_rejects_hard_linked_managed_json_before_mutation | 旧index等を新writerの書込対象にしない。上記legacy保全testの旧cache hardlinkを保持。test_active_refuses_a_hardlinked_current_record_without_changing_the_record_or_external_alias は現recordのhardlinkをSet/Clearで拒否 |
| test_commit_active_state_accepts_single_link_managed_json | 旧cache/activeへの書込成功を廃止。test_active_set_same_direct_is_unchanged_and_preserves_exact_record が現recordのunchangedを維持。現record/parent redirectは test_redirected_parent_cannot_read_or_publish_outside_worktree が拒否 |
| test_commit_active_state_rolls_back_root_symlink_and_external_projection | 旧active rootを追跡して更新/復元しない。test_legacy_doctor_preserves_unsafe_and_unknown_records_and_omits_bodies とlegacy非採用testで安全な観測/保全。新recordのredirect防止は上記WorkTargetStore test |
| test_commit_active_state_rolls_back_all_managed_agent_files_verbatim | 旧index/treeのCRLF/symlink対象にwrite/rollbackをしない。公開legacy保全testと上記Doctor testで旧bytes/外部対象を保持 |
| test_commit_active_state_rolls_back_directory_path_trees_verbatim | 旧JSON pathがdirectoryでも破壊して復元しない。公開legacy保全testがnested binaryを含む旧生成directoryを保持 |
| test_write_manifest_prefers_agent_active_and_prunes_legacy_work_files | 旧manifest生成と.work自動pruneを廃止。公開legacy保全testで.work/旧agentが不変。直接選択は test_publish_one_immutable_record_without_scope_uuid_or_git_control が確認 |
| test_write_manifest_serializes_exact_minimal_schema_v2 | 旧schema2三段writerを廃止。上記WorkTargetStore testがspecdock.work-target/v1の一件形式を確認。test_unknown_record_field_is_invalid_and_scope_id_never_changes で現在recordのstrict schema/既存ID保全 |
| test_legacy_extra_fields_are_tolerated_without_rewriting_bytes | legacy未知fieldは新選択へ変換しない。公開legacy保全testがfuture_field/CRLFを保持し、上記Doctor/legacy非採用testでopaque扱いを確認 |
| test_apply_active_pointers_uses_repo_relative_paths_and_placeholders_without_cli | symlink/.path/context-pack/runbookの更新を廃止。test_dynamic_roles_derive_current_ancestors_from_direct_scope と公開legacy保全testで導出/既存資料保全 |
| test_apply_active_pointers_refuses_generated_projection_directories | 生成projectionを削除する操作そのものを廃止。公開legacy保全testのdirectories-and-hardlink caseでnested binaryを不変に保持 |
| test_patch_agent_state_updates_cached_active_fields_without_rebuilding_indexes | 保存index/treeへactiveをpatchしない。公開legacy保全testと test_local_sync_is_readonly_and_includes_unselected_scopes が保存値不変/必要時表示を確認 |

旧snapshot復元が新しいrecordのtransactionへそのまま移ったとは主張しない。現行は成功済み効果/unknownを返し、Gitや旧recordを自動復活させない。test_clear_from_preserves_replacement_after_target_resolution、test_finish_keeps_new_selection_published_during_remote_wait、test_killed_start_at_record_boundary_requires_no_operation_journal が別process/解除/killの境界を確認する。

## 実測

- 退役前の公開characterization: selector四caseとlegacy file/directory/hardlink保全二caseで6 passed/38 deselected（0.53秒、exit0）。製品Redではない。
- 通常wheelの旧active_store収録禁止: 実build後にRed 1 failed（0.73秒、exit1）→source/test退役後、同test Green 1 passed（14.47秒、exit0）。
- 関連七suite（Active/WorkTargetStore/Finish/native record kill/Sync/Doctor/wheel）: 185 passed（49.75秒、exit0）。
- 後から追加した現record hardlinkのSet/Clear拒否: 別runで2 passed/44 deselected（0.25秒、exit0）。recordと外部alias・全treeが不変、exit3/effects空。上記185へ加算しない。
- 全Ruff check/format（310 files）、MYPYPATH=srcの変更二test限定mypy、git diff --checkが成功。skip/収集除外/compatibility alias/build除外を増やさない。
- 通常make lintはc93100ba基準にこのunitのPython差分を適用した状態でRuff成功・mypy 32 errors/11旧source files（229 source files）、make exit2。37 errorsは旧32c372e1の別snapshot。通常full gateの合格ではない。

原logは既存Epic Workbenchの iss-00413-implementation/pytest-old-active-infra-retirement-{before,source-red,source-green,related}.log、pytest-old-active-infra-hardlink.log、lint-p12-old-active-infra.log に保持した。実consumer/live GitHubは未変更。P-12、残る旧graph、full gates、native OS/別Python、fresh Strict、最終手動確認は継続中。
