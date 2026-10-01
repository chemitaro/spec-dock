# 旧dependency writer・試験の退役

## 根拠と境界

採用済み [D-09](../design.md#d-09)、[D-11](../design.md#d-11) と [CLI契約](cli-contract.md) に従う。読取根拠はローカルの `7d71f53bfd2e7e4e84553177e2370aa2cc06d2dd`。旧 application/dependency_vnext.py（235行・10 top-level symbols）と旧 test_dependency_vnext.py（218行・七test関数・二helpers）を全文確認した。

dependency の宣言・継承・循環検査・既存metadata保全を維持する。共通WriterLock、control/epoch admission、三段旧active selection、cache/stale opt-in を前提とする旧adapterを退役する。既存local metadataの読取・依存判定は保全互換性として維持し、新規local Scope発行を追加しない。

候補外のsource/test AST importは、TYPE_CHECKINGとfrom-importの子moduleを含め0。文字列参照の検査後に残るものは通常wheelの不在assertと、既知旧静的資産のpath/hashを保全するstatic-inventoryだけである。alias・fallback・build除外・pytest skip・収集除外を追加しない。

## 七つの旧試験への対応

後継は `tests/cli_runtime/test_issue413_dependency.py` の公開 `spec_dock.cli.main`、一時native Git repository、stateful gh stub、実metadata/直接recordで検証する。旧fixtureのcontrol付き新規local作成は使用しない。

| 旧test関数 | 維持する保証／採用仕様による変更 | 後継test関数 |
|---|---|---|
| test_dependency_add_list_inheritance_duplicate_and_remove | 宣言と継承、重複addのunchanged、remove/missing-ok、非対象metadata保全を維持。台帳/共通writerは使わない | test_dependency_list_derives_inherited_edges_from_current_metadata_without_control、test_dependency_duplicate_add_is_unchanged_and_preserves_every_input、test_dependency_remove_and_missing_ok_keep_absence_distinct_from_a_changed_edge |
| test_dependency_rejects_self_ancestor_and_effective_cycle | self・祖先/子孫・継承した前提を介する循環を効果前に拒否 | test_dependency_add_rejects_self_ancestry_and_inherited_wait_cycles_before_writes、test_dependency_rejects_cross_tree_inheritance_and_parent_completion_cycles |
| test_dependency_rejects_cycle_through_parent_completion_wait | 親の完了待ちを含むcross-tree cycleを拒否し、先に適用済みの辺を保全 | test_dependency_rejects_cross_tree_inheritance_and_parent_completion_cycles |
| test_dependency_all_kind_pairs_preserve_unknown_fields_and_mode | 三kind×三kindの九組で未知field・mode・非対象Scope・直接recordを保全 | test_dependency_all_kind_pairs_preserve_metadata_mode_other_scopes_and_selection |
| test_readiness_checks_target_and_ancestors_without_waiting_for_children | 子の依存で親のStart readinessをblockしない。完了した子で前提の親のcompletedを代用しない | test_readiness_ignores_child_dependencies_and_completed_children_do_not_complete_the_parent |
| test_readiness_rejects_unknown_and_requires_explicit_stale_opt_in | unknown拒否・明示live GETは維持。cache/staleによる開始許可は廃止し、旧引数をproject読取前に拒否 | test_dependency_check_defaults_to_unknown_github_state_and_never_reads_retired_cache、test_retired_dependency_readiness_inputs_are_rejected_before_project_access、test_unavailable_prerequisite_remains_unknown_with_explicit_remote_diagnostic、test_offline_live_dependency_check_refuses_before_any_github_access |
| test_readiness_live_observes_only_relevant_github_scope_without_mutation | 対象・祖先・実効前提だけをGETし、非関連ScopeのGH観測や読取時のwriteをしない。真正の既存local authorityを保持 | test_live_dependency_check_fetches_only_the_target_chain_and_effective_prerequisites、test_dependency_local_check_preserves_genuine_existing_local_authority |

二helpers `_two_trees` / `_mutation_context` は旧control・allocator fixture用として削除する。候補外importは0。後継 `two_dependency_trees` は番号1〜6が異なる二つの既存GH-backed fixture treeを構成するだけで、製品のoffline/local create経路ではない。

## 十symbolsへの対応

| 旧top-level symbol | 後継または退役理由 |
|---|---|
| GithubStateGateway | 通常queryは現行GithubIssueGatewayで必要なrefだけ観測。未使用Protocolを残さない |
| DependencyMutationResult | v2 FamilyDataとEffectへ統合。旧返値型を互換aliasで残さない |
| _DependencyMutationPlan | direct_dependenciesの捕捉metadata・candidate graph・局所publicationへ統合 |
| validate_scope_dependency_snapshot | 現行dependency_snapshot.read_raw_edgesのdecode・graph検証を維持 |
| _selection_for_targets | worktree_observationの一件直接recordと派生selectorへ統合。旧三段selection storeは使わない |
| list_scope_dependencies | direct_dependencies.query_dependenciesで現在metadataから宣言/実効値を導出 |
| check_scope_readiness | 同queryのlocal/github観測へ統合。旧cache reader/stale opt-inを使わない |
| mutate_scope_dependency | direct_dependencies.mutate_dependenciesの一metadata置換へ統合。共通WriterLock/control/epochを撤去 |
| preview_mutate_scope_dependency | 同公開commandのdry-runを維持。stagingも直接recordもwriteしない |
| _plan_dependency_mutation | 現行raw snapshot・pure graph検証・未知field/mode保全と競合確認を維持 |

`domain/dependency_vnext.py` の業務規則と `application/dependency_snapshot.py` は現行callerがあるため削除しない。他の旧private writers/helperの整理は別unitで続ける。

## 実測

追加した公開保証は既存実装のGreen characterizationであり、新機能のRedと偽らない。

- 三kind×三kind：9 passed、2.02秒。
- duplicate addで全tree/record保全：1 passed、0.37秒。
- 継承／親完了待ちcross-tree cycle：2 passed、0.57秒。
- 子の依存と親の完了を混同しない判定：2 passed、0.28秒。
- 通常wheelの旧writer収録禁止：削除前の同testは1 failed、0.77秒。失敗理由は旧application/dependency_vnext.pyの収録だった。
- 旧source/test削除後の同wheel test：1 passed、14.01秒。wheel/sdist・外部非editable venv・実consoleの既存検査も完走。
- dependency / Start / Scope delete / pure domainの関連四suite：188 passed、48.28秒。
- 全source/tests Ruff check/format：355 filesで成功。
- 変更二test file限定mypy `--follow-imports=silent`：成功。通常full type gateの代わりにはしない。

元logは既存Epic Workbenchの `iss-00413-implementation/pytest-dependency-retirement-port.log`、`pytest-dependency-retirement-source-{red,green}.log`、`pytest-dependency-retirement-related.log` に保持する。

## 未完了

直近通常lintの189 errors/32 filesはclean 2c45e885の別snapshotで、現行test型補正と今回退役後の全体lintは別途再実行する。通常全pytest、native OS/別Python、fresh Strict、最終手動確認の合格をこのunitの実績へ含めない。実consumer・既存WT・旧Git領域・live GitHubは未変更。
