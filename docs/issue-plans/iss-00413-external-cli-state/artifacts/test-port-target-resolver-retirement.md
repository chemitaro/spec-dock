# 旧target resolver・補完rendererの退役

基準は `a7fbb584345b6e435e28658b6697bf33d8ef027b`。[D-11](../design.md#d-11)と[D-04/D-07](../design.md#d-04)に従う。旧二source filesの246行・10 top-level symbols、旧二test filesの185行・12 test関数を全文確認した。package/絶対/相対/TYPE_CHECKING/from-import子moduleを含む候補外importは0。新しい互換alias、skip、収集除外を追加しない。

## source対応

| 旧module | symbols | 対応 |
|---|---|---|
| application/resolve_target | ScopeSnapshot、_selected_id、_assert_selection_integrity、_resolve_one、resolve_scope_targets | 旧三role selection snapshotを廃止。scope_query/worktree_observationで現在tree・直接一件から解決し、scope_expectationsでguardを検査する |
| application/resolve_target | WorktreeRecord、resolve_worktree_target | registry ID/aliasを廃止。direct_worktreesとnative inventory上の明示絶対pathへ対応 |
| application/resolve_target | resolve_project_root | project_contextのnative Git/cwd/正確な明示rootへ対応。外部shimは固定rootにpinせずargv/cwdを保持する |
| presentation/completion | _children、completion_script | 公開cli/optionsのcatalog/leaf option補完へ統一。既に公開v2出力試験を同入口へ移植済み |

## 十二の旧testへの対応

| 旧test関数 | 維持・変更の理由 | 現在の後継test関数 |
|---|---|---|
| test_implicit_project_uses_nearest_git_root_from_child | native Gitで近いrootを解決し読取だけ行う | test_scope_read_resolves_native_project_context_without_changing_files |
| test_explicit_project_must_name_root_and_match_shim | 明示projectは正確なWT rootへ限定。旧shimの固定project pinは廃止し、argv/cwdを外部CLIへ委譲 | test_scope_read_resolves_native_project_context_without_changing_files、test_shim_forwards_exact_arguments_working_directory_and_exit_without_git |
| test_non_git_project_is_rejected_for_scope_operations | Git環境失敗は原文・exit5・effects空を維持 | test_scope_read_resolves_native_project_context_without_changing_files |
| test_multi_role_selectors_resolve_from_same_selection_snapshot | 現在の直接記録からtarget/parentを解決する。旧三role保存/revision正本は廃止 | test_scope_publication_accepts_canonical_current_and_backend_guards_with_dynamic_parents、test_dynamic_roles_derive_current_ancestors_from_direct_scope |
| test_current_guard_checks_focus_even_for_parent_role | 現在のdirectに対するexpect-currentをtarget/parentの解決と分けて検査 | test_scope_show_checks_resolved_scope_expectations_before_success、test_scope_edit_guard_mismatch_preserves_title_documents_and_direct_record |
| test_empty_active_role_and_missing_id_are_not_found | 空/存在しないrole/IDを他targetへ推測しない | test_scope_query_uses_only_exact_imported_github_linkage_and_rejects_ambiguity、test_dynamic_scope_uses_direct_record_and_keeps_it_stale_when_scope_disappears |
| test_snapshot_rejects_noncanonical_scope_id_before_target_resolution | 保存IDのcanonical codecを維持する。旧ScopeSnapshot wrapperは使わない | test_schema_three_codec_rejects_noncanonical_saved_id |
| test_github_ref_requires_current_repo_and_unique_imported_node | 正規化した完全GH linkageにだけ一致し、未import/他repoはSCOPE_NOT_FOUND/exit4、重複linkageはexit3。旧wrapperの他repo例外classを固定しない | test_scope_query_uses_only_exact_imported_github_linkage_and_rejects_ambiguity |
| test_kind_and_parent_contract_are_checked_after_resolution | 現在treeのkind/親と明示parentの階層整合を維持 | test_all_three_scope_kinds_keep_github_numbered_hierarchy_and_live_parents、test_scope_list_show_and_edit_target_the_same_scope、test_metadata_codec_rejects_kind_and_id_mismatch |
| test_dynamic_selector_rejects_dangling_selection | 現recordと現在treeの対象/linkage/祖先が合わなければstaleを保持 | test_dynamic_scope_uses_direct_record_and_keeps_it_stale_when_scope_disappears |
| test_worktree_selector_is_limited_to_registered_identity | registry ID/aliasを廃止。自cloneのnative Git inventory上の明示絶対pathだけを採用 | test_show_resolves_an_explicit_native_path_without_reading_the_target_workspace、test_show_refuses_paths_that_are_not_an_exact_native_worktree_of_this_clone |
| test_duplicate_worktree_alias_is_ambiguous | 旧registry aliasの名前空間自体を廃止。aliasを受け入れて候補から選ばない | test_show_rejects_retired_aliases_and_relative_paths_before_project_access |

## 実測

公開main/native Git/fileで八caseを追加した。native project context三case、exact/foreign/unimported/missing ID/duplicate GH linkage五caseが退役前に8 passed（0.60秒）、exit0。GitHub GETは外部gateway境界だけで禁止を検証し、own use caseをmockしない。Git/workspaceの全digestとeffects空を検査した。既存Greenのcharacterizationである。

最初の3 failed/5 passed（0.62秒）は診断codeをNOT_FOUNDと書いたfixture誤りで、実authorityのSCOPE_NOT_FOUNDへ訂正した。製品Redに数えない。通常wheelの旧二module実収録禁止はRed 1 failed（0.77秒、exit1）、退役後の同testはGreen 1 passed（13.53秒、exit0）、wheel/sdist/外部非editable venv/実consoleまで完走した。

Scope query/active/edit/guards/native worktree/shim/help七suiteは169 passed（18.55秒）、exit0。最終全Ruff check/format（317 files）、`MYPYPATH=src` を明示した変更二test限定mypy、diff checkが成功した。Ruffが指定したassert改行だけをformat後に確認した。旧helper/test以外のproduction変更0。

元logは既存Epic Workbenchの `iss-00413-implementation/pytest-resolve-retirement-before{,-2}.log`、`pytest-resolve-retirement-source-{red,green}.log`、`pytest-resolve-retirement-related.log`。static inventoryに残る旧consumer資産のhash/pathは保全・退役照合用であり、この変更で書き換えない。残る旧helpers、通常full lint/pytest、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。
