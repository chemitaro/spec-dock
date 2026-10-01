# 旧Create / Artifact writer群の退役

## 判断と読取範囲

RQ-413-01/02/13/15/17、D-02/D-11/D-12、C-05、P-12に従い、通常CLIから呼ばれない閉じた旧writer群を退役する。`application/create_node.py`全1437行・64 symbols、`create_artifact_doc.py`全879行・37 symbols、`import_file_artifact.py`全728行・19 symbols、旧`test_import_file_artifact.py`全965行・20 test関数を全文確認した。source合計3044行・120 top-level symbolsである。絶対/相対/子module/TYPE_CHECKING/literal importのAST検査では外部production参照0、旧testから一件、群内部の参照だけだった。削除後はsrc/testsの参照0。旧consumer静的inventoryのpath/hashは歴史的資産の識別用に保持する。

現行`direct_artifact.py`全325行を照合した。`direct_scope_publish.py`、`github_scope_scaffold.py`、共有`scope_scaffold.py`、`file_publication.py`、Artifact domain/clock/templatesは保持する。旧Createからre-exportされていた共有scaffold helperをこのunitで削除しない。別test callerのあるbinary publisher、そのports/adapter試験と旧contractsはこのunitの削除対象に含めない。

## 旧symbolsの個別判断

### create_node

| 削除するsymbols | 判断・維持する境界 |
|---|---|
| `_resolve_duration_seconds`, `_resolve_duration_seconds_exclusive`, `_resolve_create_lock_path`, `_build_create_lock_metadata`, `_write_create_lock_payload`, `_read_create_lock_metadata`, `_is_stale_lock`, `_lock_failure_message`, `_runtime_entrypoint_path`, `_specdock_dir_from_lock_path`, `_doctor_guidance_message`, `_acquire_create_lock`, `_release_create_lock` | UUID/PID/TTL付きCreate lockと回収/doctor案内を廃止。排他は現在のWork Start専用OS lockだけ |
| `_post_write_duplicate_guard`, `_resolve_specdock_dir`, `_resolve_repo_root`, `_normalize_repo_slug`, `_resolve_node_repo`, `_resolve_template_scaffolder`, `_to_spec_node_seed`, `_to_spec_node`, `load_graph`, `_prefix_for_kind`, `_resolve_github_mode`, `resolve_parent_for_create`, `_node_github_linkage_key`, `_node_github_repo_slug`, `_resolve_requested_repo_slug`, `guard_github_issue_uniqueness` | 旧Ports/graph型・fallback contextを撤去。現在Scope query/schema3/exact ID/linkage/三階層の検査は保持 |
| `_create_relative_symlink`, `_nearest_existing_parent_dir`, `_preflight_symlink_creation_capability`, `_preflight_rules_symlink_creation_capability`, `_precheck_pre_github_create_symlink_dest_dir`, `_precheck_pre_github_create_symlink_capability`, `_resolve_dest_dir`, `plan_node_creation`, `_resolve_template_dir` | 旧planとrules symlink capability precheckを撤去。現在のScope scaffoldとGitHub-backed候補検査へ統一 |
| `CreatePlanExecutionError`, `create_write_phase_has_local_writes`, `resolve_create_write_phase`, `_claimed_node_tree_identity_at`, `_directory_path_identity`, `_resolve_node_tree_no_replace_rename`, `_require_node_tree_no_replace_rename_capability`, `_rename_node_tree_no_replace_between_at`, `_remove_claimed_directory_contents_at`, `_verified_directory_identity_at`, `_cleanup_node_tree_transaction`, `_cleanup_committed_outer_transaction`, `_close_node_tree_parent_fd`, `execute_create_plan` | 旧多phase transaction/cleanup/復元を撤去。現在の物理identity、no-replace、実effects/partialと残存候補保全は保持 |
| `_github_issue_body`, `_validate_pre_github_create_inputs`, `_precheck_pre_github_create_parent`, `_post_github_recovery_command`, `_post_github_retry_or_cleanup_guidance`, `_post_github_doctor_first_guidance`, `_build_pre_github_create_failure`, `_build_post_github_create_failure`, `create_node_core`, `create_initiative`, `create_epic`, `create_issue` | 旧Create orchestration/private結果/自動復旧案内を撤去。新規ScopeはGitHub番号SSOT、明示create/import、confirmed/unknownを分離 |

### create_artifact_doc

| 削除するsymbols | 判断・維持する境界 |
|---|---|
| `ArtifactSetupTarget`, `create_artifact_doc`, `_normalize_artifact_inputs`, `_resolve_scope_node`, `_ensure_scope_path_is_safe`, `_format_artifact_timestamp`, `_format_artifact_date_from_id`, `_resolve_artifact_template_text`, `_load_required_template_text`, `_artifact_replacements` | 旧型/APIを撤去。現行direct_artifactの六template、root/三階層owner、時刻と既存tokenの置換を保持 |
| `_allocate_artifact_destination_under_create_lock` | Create lock下の採番を廃止。ownerごとの時刻slot、最大100候補、明示conflict、上書きなしを保持 |
| `_preflight_artifacts_dir`, `_rules_source_path`, `_preflight_artifacts_rules`, `_ensure_artifacts_setup_for_attempt`, `_preflight_artifacts_setup_for_target`, `_require_artifact_rules_entry` | 動的rules symlinkの生成/必須化/rollback用setupを廃止。現存rules・不透明な証拠と外部directoryを変更しない |
| `PathIdentity`, `_identity_from_stat_result`, `_lstat_identity`, `_lstat_entry_identity`, `_require_created_path_identity`, `_require_created_entry_identity`, `_require_artifacts_directory_path_identity`, `_require_entry_identity` | 旧identity wrapperを撤去。現在のguarded descriptor/metadata bytes/親と候補identity再検査へ統一 |
| `_open_artifacts_directory`, `_claim_artifact_temp_path`, `_write_and_close_claimed_artifact_temp`, `_write_claimed_artifact_temp`, `_publish_artifact_temp_no_replace`, `_close_artifacts_directory` | 旧temporary writerを撤去。現行file_publicationの完成候補、no-replace、確認済み/不明の公開結果とprivate actor保全を保持 |
| `ArtifactMutationJournal`, `_rollback_artifact_attempt`, `_remove_owned_path_or_raise`, `_remove_owned_path`, `_combine_cleanup_errors`, `_committed_cleanup_warning` | mutable mutation journal、rollback、独自warning/cleanup集約を廃止。実行済みdirectory/file effectsをpartialで正直に返し、自動復旧しない |

### import_file_artifact

| 削除するsymbols | 判断・維持する境界 |
|---|---|
| `_FileArtifactTarget`, `import_file_artifact`, `_resolve_target`, `_absolute_path`, `_allocate_generic_destination` | 旧Ports APIと結果型を撤去。公開CLIのexact owner先行、明示単一regular source、opaque bytes/元basename/privacyを保持 |
| `_open_verified_directory`, `_create_bound_fresh_artifacts_setup`, `_ensure_bound_existing_artifacts_setup`, `_open_verified_child_directory`, `_name_max_for_descriptor`, `_matching_directory_statuses`, `_visible_directory_matches`, `_destination_binding_is_current`, `_close_descriptor_noexcept` | 旧bound setup/private directory APIを撤去。現行の名前制限、guarded parent/source、directory差替え拒否、no-overwriteへ統一 |
| `_validate_bound_rules_link`, `_rollback_bound_rules_link`, `_rules_link_identity`, `_merge_cleanup_state`, `_rollback_fresh_artifacts_setup` | rules linkを操作するrollback/cleanup集約を廃止。現在のArtifact操作はrulesを生成・修復・削除しない |

## 旧test関数の全件対応

| 旧test関数 | 判断・後継 |
|---|---|
| `test_root_import_commits_opaque_bytes_after_source_guard` | 公開`test_import_one_opaque_file_to_root_preserves_bytes_name_source_and_privacy`と既存source/nonregular境界へ統合。opaque bytes・元source・private情報非表示を保持 |
| `test_source_guard_failure_precedes_root_artifact_setup` | 公開source errors/nonregular試験を保持。失敗時artifacts directory未作成・effects=[] |
| `test_existing_artifacts_rules_creation_is_bound_to_opened_directory` | 動的rules link生成は廃止。新しいdirectory差替え二caseで現存rules/opaque evidence/actor filesを両物理directoryに保全 |
| `test_undecodable_source_basename_is_content_free_stable_failure` | 保全するdomainのsurrogate basename拒否試験を維持。公開source privacyの新ValueError caseを追加。元private結果型/コードや未実施OSのnative成功は主張しない |
| `test_unknown_source_guard_fault_is_precommit_runtime_failed_without_private_detail` | 公開source errorの`invalid` caseへ移す。ValueErrorにprivate parent/path/body sentinelを含めてもstdout/stderrへ出さず、directory/effectsなし。現行公開分類はprecondition/exit3 |
| `test_missing_or_kind_mismatched_target_precedes_source_guard_and_setup` | 新しいexact owner先行二case。initの番号1をissとして推測せず、missing IDもsource open前SCOPE_NOT_FOUND/exit4。旧role別flagはgeneric --scopeへ統一 |
| `test_generic_markdown_filename_is_not_a_malformed_typed_candidate` | 純粋な分類試験を`tests/unit/domain/test_artifacts.py`へ移動。opaque Markdownはgeneric・typedではない・malformedではないという全assertionsを保持 |
| `test_publication_warning_maps_to_committed_retry_not_needed` | 旧warning/private retry型を廃止。現行confirmed file/descriptor cleanup failure、unknown link、post-publication Git原文partialの公開試験を保持 |
| `test_create_lock_release_fault_after_commit_is_warning_and_not_retryable` | ArtifactがCreate lockを取らなくなるため旧解放faultを廃止。現行別process Start lock中にもArtifactを作成できる試験を保持 |
| `test_known_precommit_os_faults_are_runtime_failed_and_safe_to_retry` | 現行missing/EACCES/EIO source、redirected directory、uncertain mkdir試験を保持。実effectsに応じた4/5/3/6を分離し、自動retry分類を足さない |
| `test_result_destination_is_validated_before_publisher_commit` | 旧Port返値のbindingを廃止。現在のheld parent/stage/metadata identity再検査と差替え拒否、外部directory/actor保全を公開試験で確認 |
| `test_noncooperative_destination_race_rescans_and_preserves_cleanup_state` | 自動rescan/retry/cleanup-state集約を廃止。現行shared-slot同時conflict/no-overwrite、差替えstage保全と明示的新操作へ統一 |
| `test_cooperative_same_timestamp_imports_receive_distinct_slots` | Create lockによる同時両者成功は廃止。既存slotからの順序採番と、同時claim時一方をconflictにして上書きしない公開試験を保持 |
| `test_shared_slot_exhaustion_is_not_committed_and_does_not_call_publisher` | 公開create/import二caseへ移す。typed/untyped/genericを混在させ100slot使用、LOCAL_IO_FAILED/exit5・effects=[]・全証拠/source/metadata不変・candidateなし。既存pure allocator試験も保持 |
| `test_noncooperative_race_exhaustion_keeps_retained_cleanup_and_closes_once` | 最大100回のpublisher自動retryとprivate close-count/cleanup状態を廃止。allocationの有限上限と、conflict時actor/証拠保全は別の公開結果で確認 |
| `test_fresh_target_name_max_failure_is_precommit_and_rolls_back_setup` | 旧descriptorごとのpathconf差分とsetup rollbackを廃止。現在のUTF-8/NAME_MAX純粋試験、source/privacy、allocation-before-directory境界を保持。fresh directory成功後失敗は削除せずpartial |
| `test_fresh_target_same_name_max_identity_replacement_fails_before_publisher` | 新しいowner/artifacts差替え二case。native fsync後に同path別物理directoryを置き、公開前exit3・effects=[]、両側の証拠/actorを保全 |
| `test_fresh_rules_link_replacement_fails_closed_without_deleting_replacement` | 動的rules linkの作成/検証/削除を廃止。差替え二caseは現存rulesとactor filesを保全し、既存redirected Artifact directory二caseも保持 |
| `test_rules_link_rollback_preserves_reused_inode_replacement_with_new_ctime` | 旧rollback identity/ctimeのprivate契約を廃止。現行Artifactはrulesにunlink/修復を行わず、既存rules bytesを保全 |
| `test_rules_link_rollback_preserves_same_identity_replacement_without_unlink` | rules rollbackとmonkeypatchによる旧identity一致のcleanup契約を廃止。現行はrulesを操作せず、actor/外部directory/現存証拠の保全を保持 |

旧Create lock下のcooperative採番、自動rescan/retry、mutation journal、rules symlinkの動的生成/rollback、cleanup warning/private retry状態を同等保証として残さない。現在の公開境界は、exact owner→source→有限slot allocation→捕捉metadata/owner/catalog再検査→完成候補no-replaceである。新規ScopeのGitHub番号SSOTと真正の既存local metadataの保全は別の契約として維持する。

## 実測と残り

- source削除前の後継/保全十一cases: **11 passed、107 deselected、1.36秒、exit0**。既存Greenのcharacterizationであり、製品Redとは区別する。
- 通常wheelの旧三module収録禁止: **Red 1 failed、0.88秒、exit1**。ImportError/collection failureではなく実wheel内容のassertion失敗を確認。
- 同じ通常wheel testのGreen: **1 passed、15.35秒、exit0**。
- Artifact/Scope create・import/domainと保持するbinary publisher/portsの六suite: **235 passed、1 skipped、37.91秒、exit0**。skipは既存Linux O_TMPFILE capability testでありDarwinでのnative成功ではない。
- 実Python 3.10.15のprefix/provider import元を照合した後継/保全十一cases: **11 passed、107 deselected、1.32秒、exit0**。
- 全Ruff check/format（300 files）、MYPYPATH=srcの変更三test限定mypy、diff checkが成功。
- 通常make lint: **Ruff成功、mypy 17 errors/8旧source files（219 source files）、make exit2**。残る旧Active/Sync/deps graphと保持するshared sourceを引き続き処理する。型ignoreや対象除外で成功にしない。

元logsは既存Epic Workbenchの`iss-00413-implementation/pytest-create-artifact-helper-retirement-{port,red,green,related,python310}.log`へ保持する。skip/型ignore/収集除外を増やさず、既存assertionsを弱めない。全体gate、残る旧source、Windows native、fresh Strict、最終手動確認は別途継続する。実consumer/live GitHubは未変更。
