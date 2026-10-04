# 旧Scope発行・取り込み・復旧の退役

## 根拠と対象

採用済み [RQ-413-13](../requirement.md#rq-413-13) / [D-09](../design.md#d-09) / [CLI契約](cli-contract.md) / [第11回レビューの分析](code-review-p06-11-analysis.md) に従う。読取基準はローカル `db3d959c140327d094e487930397171d9a17fa0a`。旧五source filesの1478行・27 top-level symbolsと、test_scope_github_vnext.pyの698行・19 test関数を全文確認した。

新規ScopeはGitHubだけで番号を確定する。現在treeのID/linkage重複、親子の三階層、明示title/slug、GETだけのimport、成功・不明・未実施の効果と既存資料の保全を維持する。旧local採番、control/epoch、registry/tombstone、共通WriterLock、operation marker、永続journal、fingerprint固定によるresumeを退役する。真正の既存local metadata codecは維持する。

候補外source/test AST importはTYPE_CHECKING/from-import子moduleを含め0。退役後の文字列参照はwheel不在assert、fresh-processの旧module非load assert、既知旧資産のpath/hash inventoryだけ。alias、fallback、build除外、pytest skip、収集除外を増やさない。実consumer内の旧コピーをこのunitで変更しない。

## 十九の旧試験への対応

公開seamは `spec_dock.cli.main`、native Git、一時workspace、OS境界、実gh executable stub。旧control付きfixtureと旧local発行を後継fixtureに持ち込まない。

| 旧test関数 | 維持／採用仕様による変更 | 後継test関数 |
|---|---|---|
| test_remote_receipt_is_durable_before_local_scaffold_and_cannot_be_replayed | 一POSTと確定refの後の局所公開を維持。receipt/journalは保存せず、不明効果を自動再送しない | test_create_uses_the_confirmed_github_number_without_control_or_a_marker、test_unknown_create_response_keeps_scope_unpublished_and_never_retries_post |
| test_remote_failure_records_confirmed_or_unknown_outcome | 確定拒否はfailed/5、不明はpartial/6、正式IDは未発行。journalのstate更新をv2 effectsへ置換 | test_confirmed_create_rejection_keeps_all_inputs_and_does_not_retry_or_allocate_an_id、test_unknown_create_response_keeps_scope_unpublished_and_never_retries_post |
| test_remote_timeout_observation_recovers_exact_match_without_repost | marker検索で成功へ回復する期待は廃止。不明を保持し、新しい明示importだけを案内 | test_unknown_create_response_keeps_scope_unpublished_and_never_retries_post、test_create_has_fixed_repository_minimal_payload_and_no_timeout_retry |
| test_remote_timeout_with_duplicate_markers_stays_unknown | marker検索自体を廃止。不明効果からlocal IDを確定しない保証を維持 | test_unknown_create_response_keeps_scope_unpublished_and_never_retries_post |
| test_github_initiative_create_scaffolds_v3_after_recorded_remote_effect | schema3/返却番号ID/明示titleと一POSTを維持。journal順序を局所公開の前後効果へ置換 | test_create_uses_the_confirmed_github_number_without_control_or_a_marker、test_all_three_scope_kinds_keep_github_numbered_hierarchy_and_live_parents |
| test_github_epic_and_issue_require_explicit_open_parent_chain | 明示親・kind・正しい祖先・live openを維持。旧local作成fixtureは除去 | test_github_scope_create_rejects_missing_parent_before_remote_effect、test_all_three_scope_kinds_keep_github_numbered_hierarchy_and_live_parents |
| test_closed_github_parent_is_rejected_before_remote_create | 完了/not-plannedの親・祖先はPOST前に拒否、全入力を保全 | test_scope_create_rejects_a_live_closed_parent_or_ancestor_before_post_and_keeps_all_inputs |
| test_remote_only_success_keeps_receipt_when_local_destination_collides | 確定refとpartial、既存pathの保全を維持。永続receiptは持たない | test_confirmed_remote_create_can_be_imported_explicitly_without_a_second_post |
| test_remote_only_create_resumes_local_scaffold_without_second_post | resumeを廃止し、競合解消後の明示GET-only importへ変更。二POST目は0 | test_confirmed_remote_create_can_be_imported_explicitly_without_a_second_post |
| test_unknown_remote_create_requires_marker_and_never_reposts | marker必須/recovery成功を廃止。不明を未送信へ巻き戻さず自動再POSTしない | test_unknown_create_response_keeps_scope_unpublished_and_never_retries_post、test_import_resume_is_retired_before_project_access |
| test_published_scaffold_is_reconciled_after_journal_write_failure | journal/reconcileは廃止。公開済みの局所効果をcleanup失敗で消さない保証を維持 | test_confirmed_directory_publication_keeps_success_effect_after_descriptor_cleanup_failure |
| test_github_create_refuses_duplicate_local_issue_link | 現在tree内のID/linkage二重登録を拒否。永久tombstoneを復活させない | test_confirmed_create_number_already_linked_in_current_tree_is_not_published_twice |
| test_import_existing_issue_uses_explicit_title_and_never_posts | 明示title、番号ID、GET-onlyを維持 | test_import_publishes_the_confirmed_issue_number_with_get_only |
| test_import_confirmed_collision_ends_without_blocking_retry | 競合file/mode/metadata/Gitを保全し、競合解消後は新しい明示操作で取り込める。journal解除は不要 | test_import_preserves_an_occupied_destination_and_accepts_a_new_explicit_operation_after_resolution |
| test_import_published_scaffold_resumes_after_journal_failure | journal/resume期待は廃止。公開済み効果と並行公開の診断を維持 | test_import_reports_both_paths_when_a_competing_publication_links_the_same_issue、test_confirmed_directory_publication_keeps_success_effect_after_descriptor_cleanup_failure |
| test_import_operation_identity_fixes_slug_and_normalizes_github_ref | 永続operation identity/slug固定を廃止。各明示操作のslug正規化・exact ref正規化を維持 | test_github_scope_preview_normalizes_slug_without_allocating_an_id、test_import_accepts_existing_exact_reference_forms |
| test_import_rejects_foreign_duplicate_and_missing_title_without_post | 現在native repositoryへのbinding、重複と必須title/refの拒否を維持。旧operation identityは不要 | test_import_rejects_unbound_or_offline_refs_before_github、test_import_of_an_already_linked_ref_fails_without_a_mutation_or_partial_success、test_scope_import_requires_an_exact_source_reference_before_project_access |
| test_import_epic_and_issue_with_explicit_parent_and_read_only_github | 明示親/祖先をlive GETし、schema3の階層を保ち、元metadata/unknown field/mode/Gitを保全 | test_import_keeps_explicit_live_parent_hierarchy_and_existing_metadata_with_get_only |
| test_import_rejects_pull_request_before_local_write | PR、foreign応答、不正GETは局所公開前に拒否 | test_import_stops_on_a_rejected_or_unverified_get_without_publishing |

## 二十七symbolsへの対応

| 旧module / symbol | 後継／退役理由 |
|---|---|
| create_github_scope / GithubScopeGateway | 現行GithubIssueGatewayの最小create/getを使う。旧marker/recovery gateway protocolは除去 |
| create_github_scope / GithubScopeCreated | v2 FamilyData、確定Scope/refとeffectsへ統合。operation_idを返さない |
| create_github_scope / GithubScopeCreatePreview | v2 planned出力へ統合。IDを予約しない |
| create_github_scope / preview_github_scope_create | direct_scope_publishのdry-runへ統合 |
| create_github_scope / create_github_scope | 同現行公開writerと局所directory_publicationへ統合。共通WriterLock/control/journalなし |
| github_create_effect / GithubCreateGateway | 旧marker検索protocolを除去。現行gatewayのcreate境界を維持 |
| github_create_effect / operation_marker | UUID markerを発行・保存・検索しないため退役 |
| github_create_effect / create_github_issue_effect | 一回createと確定/不明のv2 effectsへ統合。journal/resumeを除去 |
| import_github_scope / GithubScopeImported | v2 Scope/ref/effectsへ統合。operation_idなし |
| import_github_scope / GithubScopeImportPreview | v2 dry-run GET-only出力へ統合 |
| import_github_scope / _import_fingerprint | 永続操作identityを持たないため退役。現操作の入力照合はcapture_local_inputs/verify_local_inputsで維持 |
| import_github_scope / preview_import_github_scope | direct_scope_publishのimport dry-runへ統合 |
| import_github_scope / import_github_scope | 同GET-only公開writerへ統合 |
| import_github_scope / resume_github_scope_import | resume optionをsyntaxで拒否。新しい明示importへ変更 |
| resume_github_scope / _fingerprint | 永続操作再開契約を廃止 |
| resume_github_scope / _remote_issue | 過去送信意図の復元を廃止。今回のGET/create応答だけ使う |
| resume_github_scope / _published_scope_matches | journalとのreconcileを廃止。現writerの公開後ID/ref/path確認を維持 |
| resume_github_scope / _assert_no_unfinished_transaction | 旧intent一覧とoperation resumeを廃止 |
| resume_github_scope / resume_local_scaffold | 旧scaffold journal再実行を廃止。競合解消後の新操作へ変更 |
| resume_github_scope / resume_github_scope_create | marker/recovery token付き再開を廃止 |
| create_local_scope / AncestorState | 新規local発行のstale cache snapshotを廃止。現行scope_ancestorsのlive open guardを維持 |
| create_local_scope / LocalScopePlan | 新規local発行をsyntax拒否するため退役 |
| create_local_scope / LocalScopeCreated | 同上。既存local metadata codecとは別 |
| create_local_scope / plan_local_scope_create | 独自local採番のplanningを廃止 |
| create_local_scope / _build_local_scaffold | 新規local Scope scaffoldを廃止。既存localを変換しない |
| create_local_scope / create_local_scope | 予約/high-water/control/journalを廃止 |
| create_local_scope / resume_local_scope | 旧local予約ID/journal続行を廃止 |

`github_scope_scaffold.py` は現行direct_scope_publishが使うpure builderなので保持する。`scope_ancestors.py`、`scope_scaffold.py`、既存local codecも保持する。旧control/journal/registry等の別callerとgateway内marker scanは別unitで個別に検査し、広域削除しない。

## 実測

- Epic/IssueのGET-only import、明示親/祖先・unknown metadata/mode/Git保全：2 passed、1.47秒。
- 完了/not-plannedの親・祖先をPOST前に拒否：6 passed、2.49秒。
- GET中の占有fileを保全し、競合解消後の明示再import：1 passed、0.88秒。
- 最初の衝突試験は起動前から不正Scope pathを置き、GET前のguard/3を公開失敗/5と期待したため1 failed（0.20秒）。確認済みGET後の競合を測る障害注入へ訂正した。製品Redではなく、失敗logも保持する。
- 確定拒否400/410/422のfailed/5・ID未発行・一POST・全入力保全：3 passed、1.37秒。
- 通常wheelの五旧module不在assertは実収録により1 failed（0.76秒）。source/test退役後の同testは1 passed（13.82秒）。通常wheel/sdist/外部非editable venv/実consoleまで完走。
- 現行Scope create/import、公開adapter、GitHub gatewayの関連五suite：99 passed、27.76秒。
- 全source/tests Ruff check/format：347 filesで成功。
- 変更三test限定mypy `--follow-imports=silent` とdiff check：成功。

追加公開確認は既存Greenのcharacterizationである。元logは既存Epic Workbenchの `iss-00413-implementation/pytest-scope-github-retirement-port.log`、`pytest-scope-github-retirement-source-{red,green}.log`、`pytest-scope-github-retirement-related.log` に保持した。

## 未完了

通常full lint/pytest、残る旧private helpers、native OS/別Python、fresh Strict、最終手動確認は未完了。95 errorsのlintはclean 82240b58の別snapshotで、このunit後の現在値ではない。実consumer・既存WT・旧Git領域・live GitHubは変更していない。
