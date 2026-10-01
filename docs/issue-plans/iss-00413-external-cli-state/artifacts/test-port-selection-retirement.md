# 旧Active・branch・Scope deleteの試験とwriterの退役

D-07/D-11、CLI契約C-05に従い、直接一件の選択、registryを持たないbranch操作、明示backup付きlocal subtree削除へ置換する。旧三test files全815行・28 test関数と二fixtures、旧三source files全1400行・53 symbolsを全文確認した。以下の公開試験はtest_issue413_active.py、test_issue413_branch.py、test_issue413_scope_delete.pyおよびWorkTarget/Start/Finishの現在の試験を指す。

## 28 test関数の個別判断

| 旧test | 判断・公開側の後継 |
|---|---|
| `test_select_each_scope_builds_exact_chain_and_same_target_is_noop` | 三階層とsame direct noopを保持。test_dynamic_roles_derive_current_ancestors_from_direct_scope、test_active_set_same_direct_is_unchanged_and_preserves_exact_recordと三kindの公開Startへ。lock外のactive setによる新取得・保存済み親IDは廃止。 |
| `test_clear_from_scope_preserves_ancestors_and_nonmember_is_noop` | nonmember noop/unknown拒否を保持。test_active_clear_from_removes_whole_direct_only_for_its_current_chainへ。親自動昇格はD-07により廃止し、該当direct全体だけを解除する。 |
| `test_selection_store_checks_revision_and_identity` | OCCを保持しrevision/active.jsonを廃止。WorkTarget公開Start/clearのexact captured token/bytes/identity比較、replacement/concurrent old-name removalの公開試験へ。 |
| `test_active_change_is_independent_of_scope_metadata_and_noop_does_not_write` | metadata/recordの不変とsame direct noopを保持。test_active_set_same_direct_is_unchanged_and_preserves_exact_recordとtest_active_clear_all_removes_observed_record_without_git_or_remote_effectsへ。共通WriterLock/epoch admissionは廃止。 |
| `test_branch_binding_rejects_second_scope_or_name_and_survives_id_reservation` | registry binding/ID reservation自体を廃止。ID重複はGitHub番号と現在tree/refの検査がauthority。既存refを上書きしない保証は新test_branch_create_preserves_existing_refs_and_rejects_non_ascii_names_before_any_effectへ。 |
| `test_branch_create_records_binding_without_checkout_or_tracked_change` | branch作成だけ・元checkout/資料保全を維持。test_branch_create_only_creates_ref_at_fixed_baseとbranch adapterへ。binding_persisted=falseを明示し、永久bindingと同Scopeに別明示名を禁じる台帳規則は廃止。 |
| `test_branch_create_rejects_existing_unregistered_ref` | 既存refの不採用/非resetを維持。新test_branch_create_preserves_existing_refs_and_rejects_non_ascii_names_before_any_effectのexisting caseでeffects空・全tree不変を確認。 |
| `test_branch_switch_requires_clean_tree_and_keeps_active_selection` | 保持。新test_branch_switch_refuses_unfinished_changes_and_preserves_the_direct_recordのtracked/untracked二casesと既存test_branch_switch_keeps_immutable_selection_and_changes_only_checkoutでdirty拒否・record bytes保全を検査。 |
| `test_active_from_branch_uses_only_exact_registered_binding` | from-branch取得/registry bindingをD-07に従い廃止。test_active_retired_acquisition_inputs_fail_before_project_accessでsyntax拒否し、新取得はwork startだけ。branch showは候補refの現物観測として維持。 |
| `test_branch_create_rejects_base_without_scope_and_invalid_unicode_name` | 保持。test_branch_create_rejects_base_without_target_before_creating_refと新non-ASCII name caseで候補graph/ASCII境界、effects空・全tree保全を検査。 |
| `test_branch_switch_rejects_ref_moved_to_snapshot_without_scope` | 保持。新test_branch_switch_refuses_a_moved_ref_without_the_scope_and_keeps_selectionでcandidate欠落をcheckout前に拒否しrecord/branch/treeを保持。 |
| `test_branch_switch_rejects_other_worktree_owner` | 保持。test_branch_switch_other_worktree_occupancy_is_checked_before_checkoutのdry/applyでnative inventoryの所有を確認。 |
| `test_branch_switch_reports_post_checkout_hook_mutation` | 保持。公開hook dirty/record change/native failure/clone replacement試験でcheckout効果と元Git errorを保持してpartialを返し、隠蔽・巻戻しをしない。 |
| `test_branch_create_resume_binds_fixed_ref_after_registry_failure` | journal resume/bindingを廃止。test_branch_create_native_failure_does_not_hide_already_created_refとretired journal inputsの拒否で現物再観測とconfirmed/unknownを維持。 |
| `test_branch_create_resume_reconciles_binding_after_journal_failure` | journal/binding reconcileを廃止。公開fixed-tip/選択変化のpartialとcan_resume/can_rollback=falseへ。 |
| `test_branch_create_resume_can_apply_prepared_fixed_operation` | 保存intentからのGit操作を廃止。branch previewはrefを予約せず、新しい明示createで現物を確認。公開dry-runとretired recovery拒否へ。 |
| `test_delete_requires_explicit_recursive_active_and_dependency_choices` | 明示recursive/clearを保持。test_scope_delete_refuses_a_non_recursive_parent_without_creating_a_backup、test_recursive_delete_requires_clear_active_for_the_captured_direct_descendantへ。親への選択昇格は廃止。 |
| `test_delete_boundary_dependency_requires_explicit_detach` | survivorへ影響するincoming依存の明示detachを保持。test_delete_refuses_incoming_dependencies_without_explicit_detachmentとbackup付きsurvivor編集へ。 |
| `test_deleted_scope_ids_remain_reserved_in_shared_registry` | local tombstone/共有予約を廃止。GitHub番号SSOTと現在treeのID/ref検査で新規重複を防ぐ。local資料削除でGitHub Issueを変更せず、予約台帳を新設しない。 |
| `test_import_does_not_reuse_deleted_github_scope_id` | 永久local tombstoneによるimport拒否を廃止。明示importはGitHub現物を確認して同番号からIDを決め、現在treeの重複を拒否する。新local ID発行やUUIDによる別Identityは復活しない。 |
| `test_delete_quarantines_only_target_tree_and_keeps_branch_binding` | subtree/親資料/Git ref保全を維持しquarantine journal/bindingを廃止。test_scope_delete_backs_up_the_exact_subtree_and_preserves_other_scopes_and_githubにtracked targetとnative branchを加え、backup bytes/元ref/checkoutを確認。 |
| `test_delete_detaches_survivor_dependency_and_clears_selected_issue` | 明示detach/clearを保持。test_delete_backs_up_survivor_metadata_and_clears_only_the_captured_direct_recordでsurvivor前像/metadata revision/任意fieldとcaptured解除を確認。親自動昇格は廃止。 |
| `test_delete_resumes_after_tree_move_before_journal_receipt` | operation journal resumeを廃止。公開post-removal Git failure/unknown unlinkでverified backupとconfirmed/unknown/path別結果を維持し新しい明示操作を案内。 |
| `test_recursive_delete_moves_subtree_and_retains_all_ids` | recursive範囲/backupを保持。公開parent拒否、recursive preview/captured descendant clearとsubtree bytes backupへ。ID tombstone保存は廃止。 |
| `test_delete_recovery_rejects_quarantine_identity_replacement` | resume/quarantineを廃止しidentity保全を維持。公開backup redirect/actor metadata/file/new entryの保全試験で変更された実体を削除・上書きしない。 |
| `test_delete_rollback_restores_quarantined_tree_after_verified_partial_failure` | rollback leaf/自動復元を廃止。公開verified backup・途中効果/path別結果・can_rollback=falseへ。人による現物確認用backupを維持。 |
| `test_delete_rollback_restores_dependency_and_active_before_images` | journal前像の書戻しを廃止。backupに変更元metadataを保全し、unknown detachmentで停止、actor selectionを復元/上書きしない公開試験へ。 |
| `test_delete_rollback_rejects_modified_quarantine_bytes` | rollbackを廃止しactor bytes非上書きを維持。test_subtree_removal_preserves_a_file_changed_after_backup_and_before_its_unlinkとbackup実体のredirect拒否へ。 |

旧_three_scopes/_committed_repo fixturesも退役。新local発行/control/epoch/registryを使うfixtureを残さず、既存GH-backed native Git fixtureを使用する。

## 53 symbolsの個別判断

| 旧source/symbol | 判断・現在の責務 |
|---|---|
| active / `ActiveChangeResult` | 親三件/revision付き型を廃止し公開SelectionViewへ。 |
| active / `show_active_selection` | 旧active.json reader入口を退役。WorkTargetと現在treeから選択を観測。 |
| active / `_parent` | 保存chain composerを廃止。現在metadataから動的祖先を導出。 |
| active / `select_scope` | lock外の新取得/親三件保存を廃止。Startだけがdirect一件を取得。 |
| active / `clear_selection` | 親へ昇格するpure変更を廃止。現chainと捕捉tokenでdirect全体を解除。 |
| active / `_decide_selection` | from-branch/acquisition composerを廃止。同direct unchangedと明示clearだけを公開Activeが扱う。 |
| active / `preview_active_change` | 旧chain previewを退役。現行公開previewは書込みなしでplanned clearを返す。 |
| active / `change_active_selection` | WriterLock/control/epoch/v3 writerを廃止。WorkTargetの局所remove_observedへ。 |
| branch / `_git` | 一般errorへ変換する旧subprocess wrapperを廃止。git_process.run_gitが元Git出力とtyped outcomeを保持。 |
| branch / `_resolve_commit` | 旧commit解決を廃止。native run_gitとparse_commit_oidへ。 |
| branch / `_branch_exists` | 旧ref probeを廃止。current branch_operationで現refを観測。 |
| branch / `_validate_name` | ASCII/literal refの境界をcurrent branch_operationへ保持。 |
| branch / `_verify_scope_at_commit` | target/祖先/graphの候補検証をstart_snapshot.read_candidate/verify_candidateへ保持。 |
| branch / `_binding_for_scope` | registry binding探索を廃止。明示nameまたは従来形式の候補を観測。 |
| branch / `_branch_fingerprint` | journal request保存を廃止。 |
| branch / `show_scope_branch` | 永久bindingの返却を廃止。公開showはrefのtipとbinding_persisted=falseを返す。 |
| branch / `resolve_branch_scope` | v3 active付きresolverを廃止。現在Scope views/直接選択でtargetを解決。 |
| branch / `preview_scope_branch_switch` | control付きpreviewを廃止。current公開dry-runが同じ候補/dirty/他WT占有を検査。 |
| branch / `scope_from_current_branch` | shared bindingからの新選択取得を廃止。 |
| branch / `_finish_failed_git_effect` | journal intent/result保存を廃止。現物refのconfirmed/unknownを返す。 |
| branch / `_plan_scope_branch_create` | registry排他予約を廃止。current createが明示base/target/名前/既存refを検査。 |
| branch / `preview_scope_branch_create` | control/epoch付きpreviewを廃止。current dry-runは予約・ref作成0。 |
| branch / `BranchCreateReceipt` | operation_id receipt型を廃止。公開v2 result/effectsへ。 |
| branch / `create_scope_branch_with_receipt` | WriterLock/epoch/journal/binding writerを廃止。current branch_operationがnative refだけを作り、固定tipと選択不変を確認。 |
| branch / `create_scope_branch` | 旧receipt facadeを廃止。current公開branch createへ。 |
| branch / `resume_scope_branch_create` | 保存intentからの継続/再送を廃止。現物確認後の新しい明示要求へ。 |
| branch / `switch_scope_branch` | 共通WriterLock/binding writerを廃止。current branch_operationがclean/candidate/他WT/捕捉選択を検査し、元Git errorとcheckout効果を返す。 |
| delete / `ScopeDeletePlan` | 保存chain/tombstone用型を廃止。現行削除範囲・survivor編集・captured selectionの局所planへ。 |
| delete / `ScopeDeleteResult` | quarantine/operation_id型を廃止。公開removed_ids/changed_paths/remaining_paths/backup_pathへ。 |
| delete / `plan_scope_delete` | parent promotion/registry前提planを廃止。recursive/incoming依存/captured directの必要flagを現在の削除planで検査。 |
| delete / `preview_scope_delete` | control付きpreviewを廃止。公開previewはbackup/書込みを作らず同安全条件を検査。 |
| delete / `_canonical` | journal画像codecを廃止。通常metadata codecは既存authorityを使用。 |
| delete / `_fingerprint` | journal fixed request保存を廃止。 |
| delete / `_tree_digest` | quarantine resume検査を廃止。tree_backupによる現在のverified backup/bytes/identity検査へ。 |
| delete / `_selection_text` | 親chainのjournal前像保存を廃止。 |
| delete / `_selection_from_text` | journal親chainの再構成を廃止。 |
| delete / `_safe_relative` | journal path解決を廃止。currentは明示backup/path境界と保持handleを検査。 |
| delete / `_prepare_survivor_edits` | survivorの前像保全をcurrent metadata snapshotとbackupへ保持。 |
| delete / `_decode_edits` | journal画像からの編集復元を廃止。 |
| delete / `_apply_edits` | journal再適用を廃止。current局所publicationでcaptured bytes/identityを確認。 |
| delete / `_apply_selection` | 親昇格/v3保存を廃止。captured direct tokenだけをremove_observed。 |
| delete / `_prepare_quarantine_parent` | hidden quarantine生成を廃止。明示backupの安全な局所作成へ。 |
| delete / `_apply_quarantine` | journalからのtree move/再確認を廃止。verified backup後のpath別削除とactor保全へ。 |
| delete / `_apply_tombstones` | 共有ID予約/tombstone保存を廃止。 |
| delete / `_complete_effect` | 保存effect順序のresumeを廃止。今回のv2 effectsだけを返す。 |
| delete / `_run_delete` | journal付き四効果実行を廃止。current deleteがbackup→必要編集/解除→subtree削除とpartial/unknownを扱う。 |
| delete / `delete_scope` | WriterLock/control/epoch/UUID quarantine/journalを廃止。current direct_scope_deleteへ。 |
| delete / `resume_scope_delete` | 永続operation IDによる再開を廃止。 |
| delete / `_rollback_preflight` | rollback前像/registry照合を廃止。actor保全は各通常変更の直前照合として維持。 |
| delete / `_restore_quarantined_tree` | 自動tree復元を廃止。verified backupから人が現物確認する。 |
| delete / `_restore_selection` | parent chain/元recordの自動復元を廃止。新しいactorの記録を保持。 |
| delete / `_restore_edits` | journal前像の自動書戻しを廃止。現在metadata/backupを保全。 |
| delete / `rollback_scope_delete` | rollback leafを廃止。can_rollback=falseの現物確認案内へ。 |

候補六files以外からのAST importは0で、退役後もTYPE_CHECKING/from-import子moduleを含む全source/test imports 0を確認した。残る文字列は通常wheelの収録禁止とstatic-inventoryの旧asset path/digestだけ。後者はownership証拠として保持する。新alias/fallback/build除外/skip/収集除外を追加しない。

## 検証

公開focused試験は既存ref/非ASCII拒否2 passed（0.30秒）、tracked/untracked拒否2 passed（0.49秒）、Scopeを失った候補refの切替拒否1 passed（0.31秒）、tracked subtreeのbackup/元branch/checkout/GH保全1 passed（0.39秒）。全て既存Greenのcharacterizationであり製品Redではない。

通常wheelの旧三modules収録禁止はRed 1 failed（0.80秒）、source退役後の同testはGreen 1 passed（15.49秒）。fresh wheel/sdist・外部非editable venv・実console/static操作/入力保全を確認。関連Active/branch/Scope delete/Finishは148 passed（34.11秒）。全source/tests Ruff check/format（357 files）、変更三test限定mypy --follow-imports=silent、diff checkが成功した。

元logは既存Epic Workbenchのiss-00413-implementation/pytest-selection-retirement-port.log、pytest-selection-retirement-source-{red,green}.log、pytest-selection-retirement-related.logへ保持。直近通常lintは別snapshotの313 errorsで未合格であり、今回の限定成功をfull gates/native OS/別Pythonへ読み替えない。残る旧Source/testsと現行型問題、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。
