# 旧Workbench / Worktree helper群の退役

変更前は`a24ba25b86a2bf82de7d43abd13083014092b3a8`。AC-413-33/34、D-11とCLI v2に沿い、現在の公開copy/native Worktree familyを維持する。旧application三filesの全文1366行・54 top-level symbolsと、旧unit試験416行・13 test関数を確認した。

全source/testsのASTをTYPE_CHECKING、relative import、from-import子module、literal importまで確認した。候補外production importは0、test importは退役する旧test_workbench.pyからworkbenchへの一件だけ。三module間の参照はworkbench→worktree/targetとworktree→targetで閉じている。CLI/setup/pyproject/scripts/CIの文字列も確認した。wheelの収録禁止とlegacy static inventoryは区別し、旧asset path/hashをownership証拠として維持する。

## 旧test十三関数の判断

次表の公開試験はtest_issue413_workbench.py、native Worktree三suiteと現行selector/contract suiteを指す。

| 旧test | 判断・後継 |
|---|---|
| `test_copy_resolves_same_scope_id_independently_when_slugs_differ` | 後継test_copy_resolves_existing_scope_ids_independently_of_each_worktrees_slugで両WTの別slug/path、opaque bytes、metadata不変を公開main/native Gitで確認する。 |
| `test_copy_normalizes_trimmed_uppercase_scope_id` | 同後継でtrim/大文字入力を確認する。既存local codecも保全し、新規local Scopeは作成しない。 |
| `test_invalid_scope_identifier_is_stable_and_precedes_inventory` | task/短い番号の拒否は現行selector/公開contract suiteへ。旧fake inventoryの呼出し順・固有error型はv2の保証として固定しない。init-local等の一律拒否は新要件と矛盾するため退役し、真正の既存local IDのcopyを後継で確認する。 |
| `test_scope_failure_is_side_specific_and_precedes_copy` | 後継test_copy_rejects_invalid_scope_inventory_before_copying_any_fileでsource/destination各三欠陥（missing/malformed/duplicate）と全tree不変を確認。旧private side/error型ではなくv2診断を使う。 |
| `test_target_ineligibility_precedes_scope_loading_and_copy` | 現在のsame-clone/context/native target preflightへ。公開test_copy_refuses_other_clone_self_or_scope_identity_mismatch_before_writingとworktreeのbare/absolute-path試験で保護。旧registered target型を要求しない。 |
| `test_missing_source_workbench_is_no_source_without_target_mutation` | 後継test_copy_missing_source_workbench_preserves_the_entire_destinationの二casesでmissing/existing destinationの全tree不変を確認。旧private no_source結果はv2のmissing target/exit4へ。source Workbenchは存在を要求する。 |
| `test_empty_source_workbench_is_success_and_enters_copy_after_preflight` | 既存公開test_empty_source_workbench_creates_an_empty_destination_without_a_registryへ。空directoryを許し、中央登録は作らない。 |
| `test_malformed_workbench_root_fails_before_copy` | 公開test_copy_rejects_unsafe_source_or_destination_without_following_external_content、directory conflict/type collisionとcurrent snapshot境界へ。file/symlinkをdirectoryとして使用しない。 |
| `test_ancestry_guard_failure_is_unsafe_path_before_copy` | fake gatewayの例外を現行の物理boundaryへ置換。新しいredirected scope六casesと既存Workbench root/link差替え試験でコピー前の拒否とoutside保全を確認する。 |
| `test_scope_ancestor_symlink_is_rejected_before_external_metadata_reader_runs` | 後継test_copy_rejects_redirected_scope_ancestors_before_opening_external_metadataで三階層×両WTの六cases。CLI実行中の外部metadata inodeのopenを直接禁止し、元と外部の全treeを比較する。 |
| `test_unexpected_metadata_symlink_is_rejected_before_external_reader_runs` | 現行treeは非Scope位置のmetadataを読み込まない。後継test_copy_ignores_unrelated_metadata_links_without_opening_their_external_targetで二位置の外部openゼロ/bytes保全を確認。一律拒否を同等保証として主張しない。 |
| `test_copy_failure_is_mapped_without_raw_error_or_success` | 公開unknown second-file/atomic overwrite/directory failure/raw Git試験へ。適用済み/unknown/未実施、退出値とno rollbackを維持。旧private mutation_started bool/result型はv2 effectsへ。 |
| `test_scope_outside_its_worktree_is_rejected_before_scope_path_inspection` | fake StoredMetaRecordの任意outside pathは現行のtreeから構成できない。両WTのScope ancestor六cases、外部root拒否、read_guarded_json/open_guarded_directoryでoutside非参照を保護する。 |

旧testのfake NodeReader/Environment/Git/Filesystem/Ports helperも一緒に退役する。別callerの残るpresentation/cli_textとその旧presentation test、現在のinfra.contracts/git_cli/git_helper/DirectoryIdentityは保持する。scope ID codec、三階層、既存metadata、opaque Workbenchの用途を変更しない。

## 旧source五十四symbolsの判断

各sourceのASTの名前集合と次表を照合し、重複・漏れがないことを確認した。

| 旧source / symbols | 判断・現在のauthority |
|---|---|
| workbench.py / `workbench_copy` | 公開入口はdirect_workbench.copy_workbenchへ。native Git一覧、同clone、Scope linkage、error/overwrite、file単位のpartialを維持する。 |
| workbench.py / `_require_ports` | 退役したPorts構成のadmissionを除去。現在はProjectContextのwriter宣言を確認する。 |
| workbench.py / `_validate_scope_id` | 現在のparse_scope_selectorへ。trim/大文字入力と既存ID codecを保全し、旧local IDの無条件拒否は退役する。 |
| workbench.py / `_load_scope`, `_resolve_scope` | 現在のscope_query.load_scope_views/show_scopeへ。両WTのmetadataを個別に読み、ID/kind/parent/backend/linkageを照合する。 |
| workbench.py / `_preflight_scope_root`, `_path_kind`, `_guard_ancestry`, `_guard_inventory` | 現在のscope_tree、open_guarded_directory、workbench_snapshotへ。必要なScope/containerはno-follow。無関係なmetadata linkの一律拒否は外し、外部本文を開かず無視する。 |
| worktree.py / `_WorktreeClassificationContext`, `_worktree_classification_context`, `_worktree_origin`, `_raw_worktree_id`, `_is_managed_path`, `_is_relative_to`, `_path_exists` | namespaceに属するかをSpecDock独自IDへ分類する方式を退役。native Git inventoryと物理identityを毎回観測する。 |
| worktree.py / `_pin_worktree_source`, `_open_source_directory_for_filesystem_probe`, `_materialize_and_verify_worktree` | 旧repo-local entrypointのmaterializationを退役。現在のcreateは明示baseのtipとnative Git attach、source/targetのidentity、checkout結果を確認する。 |
| worktree.py / `_open_directory_no_follow`, `_open_exclusive_worktree`, `_open_exclusive_worktree_at`, `_open_created_exclusive_worktree`, `_verify_worktree_path_binding`, `_open_exclusive_existing_worktree`, `_open_nonlocking_worktree`, `_open_nonlocking_worktree_bound_to_exclusive`, `_close_fd` | 旧Worktree directoryの独自flock/helperを退役。現在のDirectoryIdentityを保持してpath差替えを確認する。共通排他はStartだけとする。 |
| worktree.py / `_require_same_filesystem` | 旧materializationが要求したsource/target同一FS制約を退役。native Git attachと物理identityの確認を現行authorityとし、file公開は同directoryのstageで行う。 |
| worktree.py / `worktree_create`, `worktree_list`, `worktree_show`, `worktree_remove` | 公開familyはdirect_worktreesの四操作で維持する。登録ID/alias、独自管理originは返さず、明示path/branch/HEADとeffectを返す。 |
| worktree.py / `_remove_original_worktree_directory` | 旧materialization途中の自動directory cleanupを退役。途中成果を保持し、対象の削除は新しい明示removeだけで行う。 |
| worktree.py / `_normalize_label`, `_candidate_id` | 匿名label/衝突ごとの独自採番を退役。createは明示NAMEを必須とする。 |
| worktree.py / `_resolve_worktree_root`, `_validate_worktree_root`, `_invalid_worktree_root_message`, `_preflight_collision`, `_canonical_path` | 現在のcreateの明示/configured root検証、衝突検査とnative path/identity確認へ。旧採番root解決は温存しない。 |
| worktree.py / `_require_repo_and_gateways`, `_git_worktree_list`, `_build_inventory`, `_build_inventory_from_records` | 現在のProjectContextとinfra.git_cli.worktree_listへ。中央登録/旧gatewayのjoinをしない。 |
| worktree.py / `_remove_blockers`, `_non_bypassable_remove_blockers`, `_guard_remove_containment`, `_protected_cleanup_paths` | 現在のremoveのmain/current/bare、dirty/locked/ignored、必要な明示flag、保持した物理対象の再確認へ。branch/outside/後続recordを保全する。 |
| worktree.py / `_format_worktree_error`, `_coordination_failure_kind`, `_artifact_state` | 現在のGitProcessError、Effect、OperationResultへ。raw Git診断と確認済み/unknown/未実施を分け、旧receiptは作らない。 |
| worktree_target.py / `resolve_worktree_target`, `_canonical_path` | 登録ID/basename/alias resolverを退役。current Worktree/Workbenchは明示絶対pathと同cloneのnative観測だけを使う。 |

現在のdirect_workbench、workbench_snapshot、workbench_publication、direct_worktrees、WorkTargetStoreはこのunitで変更しない。旧root採番やflock、registered IDのcompatibility alias、fallback、build exclusionを追加しない。旧同一FS制約・一律metadata link拒否・private result型を同等保証として温存したふりをしない。

## 検証記録

後継十八casesは **18 passed、3.90秒、exit0**。現行Greenのcharacterizationであり、新しい製品機能のRedではない。最初の追加hunkの余分なplusによるcollection errorと、外部open禁止spyを試験自身の事後hash読取まで適用した六失敗はfixtureを修正した。spyをCLI実行中だけに限定し、製品のoutside非参照・事後bytes/mode/entry比較のassertionsは維持した。元logsを保持し、製品Redには数えない。

通常wheelの三module収録禁止は、正常build後に **1 failed、0.75秒、exit1**。削除後の同試験は **1 passed、12.86秒、exit0**。fresh wheel/sdist、外部非editable venv、実console、provider静的資産の一致を確認した。退役後のsource/test全ASTでは旧module/fixture import 0、三source path不在を確認した。

Workbench rootがregular fileのsource/destination二casesも **2 passed、0.48秒、exit0**。Worktree三family・公開adapter・Git観測・opaque filesystemを含む関連九suiteは **245 passed、37.68秒、exit0**。実Python 3.10.15の新二十casesは **20 passed、4.35秒、exit0**。全Ruff（307 files）、MYPYPATH=srcの変更二Python files限定mypy、diff checkが成功した。通常make lintはRuff成功・mypy **30 errors/10 files（226 filesを検査）、make exit2**。この限定Greenをfull gateへ読み替えない。

元logsは既存Epic Workbenchのiss-00413-implementation/pytest-workbench-group-port.log（collection失敗）、同-port-2.log（spy失敗）、同-port-3.log（後継成功）、pytest-workbench-root-file-port.log、pytest-workbench-group-source-{red,green}.log、pytest-workbench-group-related.log、pytest-workbench-group-python310.log、lint-workbench-group-retirement.logへ保持する。test選択の除外・新skip・ignore/castは増やさない。実consumer・既存WT・live GitHubは未変更。full gates、Linux全件再検証、Windows native、fresh Strict、最終手動確認は別途継続する。
