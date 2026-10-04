# 新規local Scope作成試験の退役と親差替え保証の移行

確定要件D-09/D-11は新規Scopeを必ずGitHubで発行し、そのIssue番号をIDのSSOTにする。offline/local Scope作成、独自local連番/registry/high-water/予約historyは廃止対象である。既存local metadataのcodec/読取/編集/Closeは維持し、新規作成と混同しない。

旧test_scope_local_vnext.pyの全文・十二test関数と二helpersを確認した。helpersへの候補外importは0なのでファイルごと退役する。各保証を次表で判断し、親差替えのsafetyは現行公開Scope作成へ移した。収集除外やskipを増やさない。旧create_local_scope/registry等sourceは、他のprivate testsがまだ参照するため別stepで整理する。

| 旧test関数 | 判断と後継 |
|---|---|
| `test_each_kind_has_its_own_monotone_local_id_space` | 独自local連番の発行を廃止。公開test_new_local_scope_is_rejected_before_project_accessが三kindを拒否し、GH番号による三階層はtest_all_three_scope_kinds_keep_github_numbered_hierarchy_and_live_parentsで維持。 |
| `test_reservation_gap_is_never_reused_after_failed_create` | local high-water/予約gapを廃止。GHが番号のSSOTなので新registryを作らない。remote成功後の明示import/no第二POSTは公開create/import suiteで維持。 |
| `test_allocator_rejects_corrupt_persisted_high_water` | 旧allocator/registryの起動条件を廃止。旧記録はbounded legacy診断・保全の対象。既存metadata/ID検証は現在のcodec/validateへ維持。 |
| `test_parent_kind_is_explicit_and_local_ancestors_must_be_open` | 新local作成を廃止。親kind/三階層/open検査はGH publicationのscope_ancestorsへ維持。公開missing parent拒否と三kindの明示親試験を対応。 |
| `test_github_ancestor_requires_saved_open_cache_and_warns_stale` | saved cacheを新規作成の判断根拠にしない。GH parentはその場でGETしopenを要求する。旧cache非採用は公開Scope read/Sync試験で維持。 |
| `test_issue_requires_a_matching_open_initiative_ancestor` | 新local Issue作成を廃止。GH Issueのepic/initiative整合を公開三階層試験とscope_ancestorsで維持。 |
| `test_github_ancestor_requires_matching_saved_open_observation` | saved cacheのidentity/TTLを廃止。指定repoとIssueのlive GET確認をGH gateway/公開publicationで維持。異repo/未紐付けimportを拒否。 |
| `test_two_linked_worktrees_share_history_aware_monotone_reservations` | 全WT registryによるlocal番号予約を廃止。GH番号SSOTとStart時だけの排他を採用。全WTへ採番historyを保存しない。 |
| `test_local_initiative_epic_and_issue_scaffold_without_network` | offline/new local作成を廃止。公開local作成拒否・GH番号scaffoldのrequirement/design/plan/rules生成を維持。既存local metadataの読取/編集/Closeは維持。 |
| `test_scaffold_collision_after_id_reservation_does_not_block_other_writers` | local予約/operation journalを廃止。公開GH publicationの既存destination/同一Issueリンク拒否・remote成功後ref保持・新しい明示importを後継とする。 |
| `test_parent_directory_swap_before_publication_cannot_redirect_child` | 新しい公開epic createのnative fsync境界で親を同bytes metadataを持つ別directoryへ置換。scaffold failed/partial、replacement tree不変、旧親とGH refを保持。 |
| `test_parent_swap_at_atomic_publish_never_writes_replacement` | 新しい公開epic createのrename後native fsync境界で同じ親置換を実行。scaffold unknown/partial、replacement tree不変、detachされた旧親内の公開済みScopeを保全。盲目的retryをしない。 |

## native境界での公開保証

新test_parent_directory_swap_during_scaffold_sync_never_writes_the_replacementは実Git/public main/stateful gh stubを使用する。OS fsyncを実行した境界で、外部actorが観測済みinitiative directoryをworkspace外へrenameし、同bytes metadataと独自external.txtを持つreplacementを置く。所有する内側moduleをmockしない。

publication前のstage directory fsyncで差替える一件は、最初の期待をnot_attemptedとして0.72秒で失敗した。scaffoldは既にstageを作成しているため正しい効果値failedへ訂正し、1 passed（0.59秒）。この期待訂正を製品Redと呼ばない。rename後のparent fsyncへ広げた二casesは2 passed（1.15秒）。GH GET一回/POST一回、確定ref #57、partial/6、replacement全tree不変、元metadata bytes保全を検査した。rename後はdetached旧親内のpublished Scopeも残り、scaffold unknownを返す。

関連current publication/import/create/query/lifecycle/migrationの128 tests（38.34秒）、全source/tests Ruff check/format（374 files）、変更publication test限定mypy --follow-imports=silentとdiff checkも成功した。

最初の関連pytest指定は存在しない二file名によりexit4/zero testsだった。元logを保持し、実在するcurrent test_scope_create_commands_vnext/test_scope_import_commands_vnext/test_vnext_runtime_scopeへ訂正した実行の結果だけを回帰証拠とする。既存Epic Workbenchのiss-00413-implementation/pytest-local-creation-retirement-related.log（中断）とpytest-local-creation-retirement-related-2.log（成功）へ保存した。実consumer/既存WT/旧Git領域/live GitHubは未変更。full type/pytest、旧writersの退役、native Windows/別Python、fresh Strictと最終手動検証は継続する。直近通常make lintの407 errorsは未合格のままである。
