# 旧generation・状態cache・cache付きGit snapshotの退役

## 根拠と読取

[RQ-413-11 / AC-413-23/24](../requirement.md#rq-413-11)、[D-10](../design.md#d-10)、[D-11](../design.md#d-11)は必要時のSyncと今回のGETを採用し、保存世代/cacheを採用しない。固定HEADのCI検査と明示candidateのStart検査は必要なmetadataだけで行う。

三source filesを末尾まで読み、299行・11 top-level symbolsを確認した。旧generation test fileも末尾まで読み、60行・三test関数を確認した。source/tests/scriptsのASTで絶対/相対/TYPE_CHECKING/from-import子moduleを検査し、唯一の参照は同時に退役するgeneration testだった。setup/pyproject/CIの文字列検索も実行した。候補外importは0。legacy静的inventoryの旧path/hashは保全対象で、呼出しではない。

| 退役source | 責務と処置 |
|---|---|
| infra/generation_store.py — 188行/7 symbols | Generation、guard/exclusive write/fsync/paths、load/publish。UUID directory/manifest/atomic current pointerを保存する仕組みを削除する。新Syncは保存しない |
| infra/github_status_cache.py — 34行/1 symbol | cached_github_ancestor_open。保存OPENを新規操作のauthorityにしない。必要な操作は今回のGETを使い、readerはunknownを返す |
| infra/git_snapshot.py — 77行/3 symbols | _git_bytes/_safe_relative_path/scope_graph_at_commit。status_cacheをmaterializeするsnapshotを削除する。現行の固定OID/metadataだけのreaderを保持する |

json_storeの原子publicationや現行WorkTargetStoreは削除しない。既存consumerのgeneration/cacheを削除/修復/自動変換せず、legacy診断の境界も維持する。

## 旧三testの個別判断

| 旧test | 判断と現行の確認 |
|---|---|
| test_generation_publish_and_read_immutable_bytes | 保存世代/current切替の成功契約を廃止。test_local_sync_is_readonly_and_includes_unselected_scopes と test_sync_ignores_and_preserves_retired_generations_and_current_pointer が表示と不変性を確認する |
| test_failure_before_pointer_retains_previous_generation | generation stage/current pointerのtransactionを廃止。test_unavailable_github_observation_is_partial_without_effects_or_cached_fallback がpartial/unknown/effects空・現在選択と旧cache保全を確認する。pointer rollbackを再実装する意味ではない |
| test_corrupt_pointer_and_redirected_generation_are_rejected | 実bodyは不正generation IDの拒否試験。新Syncは旧pointerをauthorityにしないため、test_sync_ignores_and_preserves_retired_generations_and_current_pointer の不正pointer caseで旧bytesを保全する。現行直接記録の不正は test_unreadable_worktree_record_keeps_known_counts_incomplete_and_preserves_bytes が別途検査する |

Git snapshotの必要保証は test_ci_uses_the_captured_oid_even_if_head_moves_during_the_read、test_ci_fetches_only_metadata_bodies_and_never_artifact_or_runtime_bodies、test_start_reads_three_level_candidate_metadata_before_checkout、test_explicit_branch_start_uses_candidate_readiness_instead_of_current_dependencies で保持する。cache非採用は test_scope_query_ignores_retired_github_status_cache と test_github_sync_separates_lifecycle_from_selection_without_a_cache でも確認する。

## 検証

- 新しい公開Syncの正常/不正旧pointer二caseは退役前から2 passed/24 deselected（0.49秒、exit0）。既存Greenのcharacterizationである。
- 通常wheelの旧三module禁止を先行し、実build後の収録でRed 1 failed（0.71秒、exit1）。source/test削除後、同testはGreen 1 passed（13.55秒、exit0）。
- 関連六suite（Sync/Validate/Doctor/query/Start/wheel）は231 passed（65.73秒、exit0）。fresh wheel/sdist/外部非editable venv/実consoleを含む。
- 全Ruff check/format（313 files）、MYPYPATH=srcの変更二test限定mypy、git diff --checkは成功。skip/収集除外/互換alias/build除外を増やさない。
- 37 errorsの通常make lintは変更前clean 32c372e1の別snapshot。現在のfull gate、native OS/別Python、fresh Strict、最終手動確認は未完了。実consumer/live GitHubは未変更。

原logは既存Epic Workbenchの iss-00413-implementation/pytest-generated-state-retirement-{before,source-red,source-green,related}.log に保持した。
