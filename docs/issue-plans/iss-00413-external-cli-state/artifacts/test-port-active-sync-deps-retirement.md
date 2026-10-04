# 旧Active / Sync / 依存チェック群の退役

## 判断と読取範囲

RQ-413-02/07/08/11/12/15、D-03/D-04/D-07/D-08/D-10/D-11、C-02/C-03/C-05、P-12に従い、通常CLIから呼ばれない閉じた群を退役する。`application/set_active.py`全387行/17 symbols、`sync_state.py`全928行/41 symbols、`check_deps.py`全332行/12 symbols、旧`test_check_deps.py`全991行/18 test methodsを全文・分割して確認した。source合計1647行/70 top-level symbols。ASTの絶対/相対/子module/TYPE_CHECKING/literal importで外部production参照0、群内参照と旧test import一件だけだった。削除後はsrc/testsのAST参照0。旧静的inventoryのpath/hashは識別用に保持する。

現在の`direct_dependencies` query、`dependency_snapshot.py`と`domain/dependency_vnext.py`、`direct_sync.py`全体、Active/同clone観測の公開試験を照合した。新しい状態保存・lock・権限・daemonを足さない。現行のdomain検証にcallerがある旧pure deps/validation、rendererや旧型を利用する他のtestはこのunitの削除対象にしない。

## 旧symbolsの個別判断

### set_active

| 削除するsymbols | 判断・維持する境界 |
|---|---|
| `_to_spec_node_seed`, `_resolve_specdock_dir`, `_resolve_repo_root`, `_to_repo_relative_specdock_path`, `_find_existing_id_by_num`, `resolve_target_node_id` | 旧Ports/graph、path推測、番号/未scoped fallbackを撤去。現在のexact Scope selectorとGH ref・三階層metadataへ統一 |
| `_to_view_entry`, `_to_active_selection`, `_append_unique` | 旧三段manifest/view型を撤去。現在の直接recordと現存祖先からのrole解決を保持 |
| `build_context_pack_text`, `_build_context_pack_text`, `build_active_manifest`, `commit_active_state` | context-pack/三段保存/投影patchとsnapshot/restoreを廃止。直接record一件の読取・捕捉tokenだけの解除へ統一 |
| `show_active`, `checkout_active_target`, `set_active`, `clear_active` | 旧acquisition/checkout APIを撤去。開始はWork Start専用、Active同一direct no-opと明示clear、branch familyの固定Git効果を保持 |

### check_deps

| 削除するsymbols | 判断・維持する境界 |
|---|---|
| `_to_spec_node_seed`, `_resolve_specdock_dir`, `_append_unique`, `_validate_raw_node_dependency_preflight` | 旧compositionを撤去。現在のmetadata再検査、全raw graphのcycle preflight、三階層継承を保持 |
| `_load_cached_issue_last_sync_at_by_id`, `load_cached_high_level_github_state_by_id` | 旧index/cacheから状態・last_sync_atを採用する処理を廃止。過去資料は保全するが今回のreadiness根拠にしない |
| `_normalize_issue_status`, `_status_state_from_snapshot`, `_descendant_issue_ids`, `_descendant_aggregate_state`, `resolve_high_level_status_context` | 子Issue完了から親状態を集約する旧policyを廃止。Scope自身のlive GitHub状態/真正の既存local lifecycleを使用し、親を自動完了しない |
| `check_deps` | 旧private結果/全repo issue_index/fallback cacheを撤去。公開direct_dependenciesのexact対象chainと有効prerequisiteだけのGET、unknown/diagnostic/保全を保持 |

### sync_state

| 削除するsymbols | 判断・維持する境界 |
|---|---|
| `_append_unique`, `_is_safe_unscoped_snapshot`, `_load_cached_issue_last_sync_at_by_id`, `_to_spec_node_seed`, `_resolve_specdock_dir`, `_manifest_to_active_selection`, `_now_iso_from_ports`, `_require_sync_runner`, `_path_for_output`, `_can_collect_natively`, `_can_sync_natively`, `_load_active_selection` | 旧Ports composition、legacy runner fallback、単一manifest・cache採用を撤去。現在treeとGit inventoryの必要対象/祖先を今回だけ観測する |
| `_AdrMirrorSource`, `_AdrFrontMatter`, `_AdrMirrorProbeLocation`, `_parse_required_adr_front_matter`, `_front_matter_scalar`, `_artifact_adr_mirror_eligible`, `_adr_doc_id_from_basename`, `_artifact_adr_doc_id_from_basename`, `_ensure_collectable_artifacts_dir`, `_collect_adr_mirror_sources`, `_preflight_adr_mirror_sources`, `_unlink_any`, `_ensure_empty_dir`, `_is_environment_symlink_unsupported`, `_resolve_adr_mirror_probe_location`, `_build_adr_mirror_probe_path`, `_preflight_adr_mirror_symlink_support`, `_rebuild_adr_mirror` | 本文走査、UUID probeと中央ADR mirror再生成/rmtreeを廃止。旧ADR/Artifact/不透明な投影を変更せず、別の現在Artifact catalogで必要時identityを読む |
| `collect_sync_state`, `_raw_node_depends_on_map` | 全repo snapshots/graph/単一activeの旧集約を撤去。現在direct_syncの同clone各WT、必要な対象/祖先、unknownとknown countsへ統一 |
| `maybe_auto_update_from_branch` | branch名からActive推測/三段更新を廃止。branch切替は記録不変、選択・lifecycle・processを独立して表示 |
| `_ArtifactWriteExecutionError`, `write_sync_artifacts`, `_sync_impl`, `sync` | 中央index/tree/deps/dashboardとADR mirrorの書込、private failure型を廃止。現在readonly Syncのscopes/worktrees/counts、effects=[]、不完全exit7を保持 |
| `sync_after_import`, `sync_after_mutation`, `post_mutation_sync`, `skipped_post_mutation_sync` | mutation後の自動Sync/callbackと旧結果集約を撤去。独立した明示readonly Syncへ統一 |

## 旧test methodsの全件対応

| 旧test method | 判断・後継 |
|---|---|
| `test_repo_scoped_target_resolution_matches_set_active_without_ports` | 旧graph resolverと未scoped fallbackのprivate一致を廃止。現在共通exact selector/GitHub ref、Scope identity conflict試験を維持。番号だけから異なるrepositoryへfallbackする保証は残さない |
| `test_no_github_uses_cached_status_and_last_sync_without_fetching_github` | cacheによるreadyを廃止。公開retired cache二caseはvalid CLOSED/不正indexを保全し、今回未観測GHをunknownとしてblocked、通信/effectsなし |
| `test_effective_depends_on_merges_parents_and_dedups_without_cli` | 新しい公開継承二caseへ移す。Issue/Epicで両祖先の依存を重複なく併合、declared/effectiveを分離し全metadata/recordを保全 |
| `test_effective_depends_on_merges_epic_and_initiative_without_cli` | 同じ公開継承二caseと既存三階層/全kind pair試験へ統合。旧private graph型とsortの実装を固定しない |
| `test_deps_check_fails_raw_node_preflight_before_empty_container_ready` | 新しい公開empty Epic二者cycle case。GitHub GET前PRECONDITION_FAILED/exit3・effects=[]、入力保全。現在全graph/継承cycle検査も保持 |
| `test_deps_check_blocks_empty_initiative_direct_node_dependency` | 新しい高level十六casesで空/子ありInitiative・Epic、GH/local、open/completedを確認。prerequisite自身openはblocked、状態を子Issueへ展開しない |
| `test_deps_check_keeps_direct_node_status_separate_from_issue_readiness` | Scope自身の状態とreadinessを分ける現在公開試験へ統合。旧child doneによる親satisfiedは廃止し、既存completed childrenが親を完了しない二caseを保持 |
| `test_no_github_missing_cache_defaults_to_unknown_and_blocks` | 既存default未知・retired cache二caseを保持。cacheが無い/有るとも今回のGH未観測はunknown、readyに補完しない |
| `test_github_index_incomplete_warns_and_leaves_missing_dependency_unknown` | 全repo index取得/補完を廃止。現在exact必要refだけのGETとunavailable prerequisiteのunknown/明示remote diagnosticを保持 |
| `test_github_fetch_failure_warns_and_blocks_on_unknown_dependency` | 既存公開unavailable prerequisite/GITHUB_REMOTE_UNAVAILABLE・effects=[]を保持。Syncは別のreadonly partial/exit7として検証 |
| `test_github_snapshots_drive_ready_and_blocked_states_without_cli` | 現在live GETのchain/prerequisite試験と新しいGH/local高level十六casesへ統合。open/未観測をcompletedへ補完しない |
| `test_deps_check_passes_empty_open_high_level_context_to_readiness` | 新しい十六casesの空GH Epic/Initiative openをblockedにする。旧reason/privatecontextではなく公開READINESS_BLOCKED/detailsを使う |
| `test_deps_check_exposes_satisfied_closed_high_level_context` | 新しい十六casesの空/子ありGH/local completedをreadyにする。GETは必要chain+一prerequisiteだけ、sourceとmetadata不変 |
| `test_deps_check_exposes_satisfied_open_high_level_context_when_descendants_done` | open親を子Issueのdoneからsatisfiedにする旧policyを廃止。現在completed childrenはopen親を完了しない公開試験を保持 |
| `test_no_github_uses_cached_high_level_github_state_from_sync_artifact` | 旧index-all/indexのCLOSED採用を廃止。valid CLOSED/不正index二caseで未観測unknown・全bytes保全・内容非表示を確認 |
| `test_github_linked_empty_high_level_dependency_without_cache_fails_unknown` | 現在default未観測GHのunknown/blocked試験、liveUnavailableのexplicit診断を保持。cacheや空childrenからreadyを生成しない |
| `test_local_empty_high_level_dependency_preserves_open_status` | 十六casesで真正の既存local高level empty/openをblockedにし、通信なし/lifecycle/全metadata保全を確認 |
| `test_local_high_level_default_open_does_not_mask_done_descendant_aggregate` | 子done優先で親openを上書きする旧policyを廃止。現在local親自身の状態と、completed childrenが親を完了しない公開試験を保持 |

三段Active/context-pack/中央ADR mirrorの生成、branchからの自動選択、全repo index/cache採用、子のdoneを親状態へ昇格するpolicy、自動Sync/rollbackは同等保証として残さない。現在のexact Scope自身の状態・今回のlive GET・readonly必要時観測と、直接record/元資料/他WTの保全へ統一する。test削除をskipや収集除外に置き換えず、当初要求の三階層/依存を維持する。

## 実測と残り

- source削除前の高level/循環/旧cacheの公開十九cases: **19 passed、47 deselected、4.33秒、exit0**。既存Greenのcharacterizationであり、製品Redとは区別。
- 通常wheelの旧三module収録禁止: **Red 1 failed、0.83秒、exit1**。実wheelの内容をassertし、ImportError/collection failureをRedに数えない。
- 同じ通常wheel testのGreen: **1 passed、14.76秒、exit0**。
- 追加した公開継承二cases: **2 passed、66 deselected、0.53秒、exit0**。
- 現行Active/Dependency/Sync、同clone Sync/Start、保持するpure Validateの六suite: **243 passed、60.26秒、exit0**。初回は誤ったtest pathでexit4/no tests ranとなり、実在file `tests/unit/application/test_validate.py`へ直した。このharness errorは製品Redにしない。
- 実Python 3.10.15のprefix/provider import元を照合した高level/循環/旧cache/継承二十一cases: **21 passed、47 deselected、4.59秒、exit0**。
- 全Ruff check/format（296 files）、MYPYPATH=srcの変更二test限定mypy、diff checkが成功。skip/型ignore/収集除外追加0。
- 通常make lint: **Ruff成功、mypy 10 errors/5 files（215 source files）、make exit2**。保持するshared sourceの型契約修正を後続へ分ける。限定成功をfull gate合格にしない。

元logsは既存Epic Workbenchの`iss-00413-implementation/pytest-old-active-sync-deps-retirement-{port,red,green,inheritance,related,related-2,python310}.log`、`lint-old-active-sync-deps-retirement.log`へ保持する。全体gate、残るshared source、Windows native、fresh Strict、最終手動確認は別途継続する。実consumer/live GitHubは未変更。
