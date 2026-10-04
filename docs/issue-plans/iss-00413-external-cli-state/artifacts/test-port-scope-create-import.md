# Scope create / importのテスト移行

変更前は `e6df572544e7bfde5d07669dde0ab71c460be320`。旧二ファイル・二十関数を全文確認し、RQ-413-13、AC-413-22/27/28/29、D-09/D-11の確定契約へ照合した。公開 `spec_dock.cli.main`、native Git、外部gh executableで後継を検査する。旧run_vnext、WorkContext、control登録、local採番、prepare_operation、JournalStoreは入口・fixtureから外す。

| 旧test | 後継・判断 |
|---|---|
| create `test_local_scope_create_cli_uses_explicit_parent_and_dry_run` | 新規local発行は全三kindでproject読取前のexit2へ変更。階層の親子とGH採番は既存publication suiteの `test_all_three_scope_kinds_keep_github_numbered_hierarchy_and_live_parents` で保護 |
| create `test_local_scope_create_json_identifies_created_scope_and_observed_status` | GH作成の承認と返却number57から生成したID、kind、parent、revision、ref、観測state、現物metadata/三文書へ置換。新localの正式IDと旧snapshot/worktree登録IDは撤去 |
| create `test_local_scope_create_preview_returns_normalized_slug` | GH previewで既定slugと明示slugを二cases確認。scope/ref未確定、can_apply、予定効果、全tree不変・POST0を検査 |
| create `test_scope_show_json_uses_same_target_and_scope_snapshot` | 真正の既存local codecのshow/editでID・backend・local authorityと文書本文を保護。v1 target/snapshot欄を復活させない |
| create `test_scope_edit_json_reports_the_changed_revision_and_status` | 同じ既存local後継で更新title/revision=1、changed、local lifecycleと現物metadataを比較 |
| create `test_local_scope_create_cli_rejects_missing_parent` | GH-backed epicの不存在親を公開mainでexit4、remote/write0として維持 |
| create `test_local_scope_create_cli_does_not_retry_a_recovery_request_as_new` | --resumeはsyntax段階でexit2、effects空、tree不変。新規操作として再POSTしない |
| create `test_prepared_create_failure_returns_recorded_recovery_id_without_claiming_effect` | 永続prepared journal/operation IDはD-09/D-11で撤去。確認不足とinvalid parentを効果前で拒否し、旧resume入力を新規作成へ読み替えない |
| create `test_local_scope_create_cli_resumes_original_reserved_id` | local予約・journal replayは撤去。GH応答不明でIDを公開せずPOSTを再送しない保証は既存 `test_unknown_create_response_keeps_scope_unpublished_and_never_retries_post` へ |
| create `test_scope_edit_post_publication_io_failure_reports_observed_partial` | 既存 `test_scope_edit_confirmed_publication_cleanup_failure_keeps_the_updated_scope_and_effect` のfilesystem故障試験へ。確定したmetadata効果を消さずpartialで報告 |
| create `test_scope_edit_guard_failure_keeps_resolved_scope_payload` | 既存 `test_scope_edit_guard_mismatch_preserves_title_documents_and_direct_record` へ。current/backend不一致の効果前停止と現物保全を維持。旧v1 target/snapshot保証は撤去 |
| create `test_scope_edit_io_failure_with_unreadable_after_state_is_partial` | 既存 `test_scope_edit_uncertain_replacement_does_not_claim_an_observed_scope_or_repeat_the_write` へ。不明を確定成功へ変換せず、内部dispatcherのmockを使わない |
| create `test_github_scope_create_cli_previews_and_requires_confirmation` | GH preview二casesと承認不足→--yesの公開後継へ。POST一回、正式IDとref、既存metadata不変を検査 |
| create `test_github_create_confirmation_rejects_origin_change_before_remote_effect` | 端末入力の外部代替が回答時にnative Gitでoriginを変更する。捕捉repositoryとの相違を確認後・POST前にexit3で拒否。内部repository resolverはmockしない。stdin代替をnative PTYの証拠とは扱わない |
| create `test_github_scope_create_cli_resumes_without_second_post` | remote確認後に別actorがローカルpathを占有するfixture。partialにexact refを残し、旧resume拒否後に新しい明示importを実施。POST→GETだけで正式IDを復旧し、占有pathを自動削除しない |
| create `test_github_scope_create_resumes_prepared_record_before_remote_intent` | prepared ID/replayは撤去。新規操作のremote前安全性はpreview/承認/親/確認中origin変更と既存template・staging検査で保護 |
| import `test_scope_import_cli_previews_and_creates_without_post` | 明示refのdry-runとapplyをGETのみで実施。previewのlocal write0とapplyの正式ID・現物metadataを比較。旧GET0期待は最新のIssue確認GETという契約へ変更 |
| import `test_scope_import_json_identifies_linked_scope` | 同じ後継でscope/ref/numberとlive GH source・authority・時刻を比較。lifecycle cacheとv1 snapshot欄を撤去 |
| import `test_scope_import_cli_resumes_after_uncertain_local_publication` | 旧journal update故障によるreplayは撤去し、--resumeをproject読取前に拒否。directory公開後の確定/不明は共有publicationの `test_confirmed_directory_publication_keeps_success_effect_after_descriptor_cleanup_failure` とdirectory adapterの実filesystem故障試験で保護 |
| import `test_scope_import_cli_requires_source_reference` | ref欠落をsyntax段階・project読取前のexit2/effects空として維持 |

後継二ファイルは十三cases。新規localを作らず、真正の既存localの読取・編集互換だけを残す。GitHub採番・観測の試験はhermeticで、live GitHubを変更しない。full suite、native Windows、Strict合格をこの限定移行の結果から推論しない。

初回は、作成前から通常Scope pathをfileで占有したfixtureを、remote後のpartialと期待して一件失敗した。現在のtree検査はその不正pathをPOST前にexit3で拒否するため、製品Redではない。remote確定後に別actorがpathを占有するexternal gh fixtureへ訂正し、捕捉ref・未実行scaffold・POST再送0・明示importを検査した。
