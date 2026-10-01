# 旧Worktree試験・writerの退役

AC-413-34/D-11に沿って、Gitの現物一覧・明示NAME/base/path・明示bootstrapをauthorityにする。旧三test filesの全433行・20 test関数と三fixture、旧worktree_vnext.py全645行・22 symbolsとworktree_bootstrap_vnext.py全164行・六symbolsを全文確認した。次表の公開試験はtest_issue413_worktree.py、test_issue413_worktree_remove.py、test_issue413_worktree_bootstrap.pyを指す。

## 20 test関数の個別判断

| 旧test | 判断・公開側の後継 |
|---|---|
| `test_create_pins_explicit_base_and_uses_operational_branch_without_bootstrap` | 固定base・新規選択なし・bootstrapなしを保持。test_create_uses_the_explicit_name_and_fixed_base_without_registration_or_bootstrapに既存source選択を加え、元record bytes不変・作成先.agentなしを確認。固定wt1/alias/control登録は廃止し、明示NAMEのbranch/pathとGit起源のlist/showへ置換。 |
| `test_create_rejects_unknown_base_and_reused_name_before_git_effect` | 保持。新test_create_rejects_an_unknown_base_or_existing_name_before_any_effectのmissing-base/path/branch三casesでeffects空・全tree不変を確認。台帳上のalias重複ではなく現物の衝突を扱う。 |
| `test_detached_source_can_create_from_explicit_base` | 保持。新test_create_from_a_detached_source_keeps_its_head_and_pins_the_explicit_baseでsourceのdetached/HEADを保持し、明示baseの新branch/Worktreeを検査。匿名名の自動採番は廃止。 |
| `test_create_failure_records_target_and_refuses_blind_retry` | control receiptを廃止。test_create_reports_a_confirmed_worktree_even_when_native_git_returns_a_hook_failureとbranch/source変化の公開試験で現物再観測・confirmed/unknown/effects/raw errorとno rollbackを保持する。 |
| `test_create_recovery_requires_effects_to_be_absent_before_reusing_target` | recover/台帳再利用を廃止。公開のretired recovery syntax拒否、missing native inventory target/actor path collision、fixed branch tip再検査で、現物確認なしの再使用を防ぐ。 |
| `test_create_cli_requires_an_explicit_name_and_retires_target_recovery` | 公開mainで維持。test_create_requires_an_explicit_name_before_reading_the_projectとtest_worktree_rejects_retired_recovery_before_project_accessへ対応。 |
| `test_dry_run_and_offline_never_evaluate_make` | 保持。test_bootstrap_does_not_evaluate_make_for_preview_offline_or_missing_confirmationがmake評価のtrap/実Popenを検査し、dry-offlineも副作用なし。 |
| `test_explicit_bootstrap_runs_make_and_keeps_diagnostic_record` | 明示make実行を保持しreceiptだけ廃止。test_bootstrap_runs_make_init_only_in_the_explicit_native_worktreeで一回・指定pathのみ・Git control/.agent生成なしを確認。 |
| `test_timeout_is_partial_and_does_not_block_unrelated_writers` | 保持。test_bootstrap_timeout_keeps_applied_project_files_and_stops_its_child_groupとtest_bootstrap_runs_while_start_exclusion_is_heldでnative timeout/unknown/部分成果保存・Start lockと独立した操作を検査。旧epoch admissionは廃止。 |
| `test_partial_bootstrap_requires_explicit_target_recovery_without_rerunning_make` | receipt/reconcileを廃止。test_bootstrap_failure_omits_hook_output_and_only_runs_again_for_a_new_explicit_requestで元効果を保持し、新しい明示要求だけが再実行する。 |
| `test_bootstrap_recovery_cannot_acknowledge_a_live_attempt` | recovery leafとbootstrap leaseを廃止するため退役。公開retired recovery拒否・実行中timeoutのprocess group停止を維持する。Start以外の共通排他は導入しない。 |
| `test_bootstrap_cli_recovery_is_retired_and_the_target_requires_an_absolute_path` | 公開syntax/helpとtest_show_rejects_retired_aliases_and_relative_paths_before_project_access、retired recovery拒否へ対応。管理ID/aliasではなく絶対native pathを使用する。 |
| `test_missing_target_fails_before_make_or_record` | 保持。新test_bootstrap_rejects_a_missing_or_non_native_target_without_running_a_hookの二casesでexit4/effects空/全tree不変・hook未実行・新controlなしを検査。 |
| `test_output_capture_is_bounded_and_redacts_obvious_credentials` | 出力を保持せず省略する保証を保持。新test_successful_bootstrap_omits_large_and_secret_hook_output_from_both_streamsで10万字のstdout/stderrを省略し、公開応答5000字未満・secret非露出・明示成果/Makefile保全を確認。 |
| `test_bootstrap_never_exposes_arbitrary_hook_output` | 保持。新成功時試験と既存failure時試験で、labelのない値もstdout/stderrへ出さない。 |
| `test_remove_keeps_branch_and_retires_registration` | branch保持を維持しcontrol登録の廃止操作を退役。test_remove_operates_on_native_inventory_and_retains_the_branch_and_outside_contentがnative removal/元ref/outside bytesを検査。 |
| `test_remove_rejects_untracked_even_with_discard_ignored` | 保持。test_remove_never_discards_tracked_or_untracked_changes_even_with_discard_ignoredで二種のdirty・dry/applyを拒否し、payload bytesを保存。 |
| `test_remove_rejects_current_and_ignored_without_explicit_flag` | 保持。main/current拒否とtest_remove_requires_discard_ignored_before_any_effectでignored evidenceを保全。 |
| `test_remove_discards_only_explicitly_allowed_ignored_payload` | 保持。test_explicit_discard_removes_only_ignored_content_inside_the_targetがdry/applyとoutside保全を検査。 |
| `test_locked_worktree_requires_explicit_unlock` | 保持。test_remove_requires_unlock_for_a_native_locked_worktreeとtest_remove_unlocks_only_the_explicit_target_or_plans_both_effects_without_writingがnative lock理由・dry/apply・明示unlockだけを扱う。 |

旧fixture三つ（_committed_repoと二filesそれぞれの_created）も一緒に退役する。control/epoch/engine digestを準備するhelperを残さず、公開main/native Gitの既存fixtureを使う。

## 28 symbolsの個別判断

| 旧symbol | 判断・現行authority |
|---|---|
| `WorktreeCreated` | id/alias/control_epoch付き型を廃止。FamilyDataの明示path/branch/head/changedへ。 |
| `WorktreeView` | 登録型を廃止。Git起源のWorktree inventoryと公開FamilyDataへ。 |
| `WorktreeRemoved` | control_epoch付き型を廃止。公開path/changed/observed/effectsへ。 |
| `WorktreeCreatePreview` | 自動管理IDを廃止。公開dry-runの明示NAME/path/baseとplanned effectsへ。 |
| `WorktreeRemovePreview` | 登録IDを廃止。公開path/observed/can_applyとplanned effectsへ。 |
| `list_worktrees` | controlとのjoinを廃止。direct_worktrees.list_native_worktreesでGit現物を取得。 |
| `show_worktree` | ID/alias selectorを廃止。direct_worktrees.resolve_native_target/show_native_worktreeで絶対path・同clone・物理identityを検査。 |
| `_validated_name` | 匿名名/aliasを廃止。create_native_worktreeで必須NAMEを検査。 |
| `_worktree_root` | 明示/configured rootの必要条件はcurrent createへ保持。 |
| `_branch_exists` | private Git subprocessを廃止。current run_gitでnative refを観測。 |
| `_next_id` | 自動wt番号の台帳採番を廃止。明示NAMEを使用。 |
| `_create_attempt_path` | 共通Git control receipt pathを廃止。 |
| `_unresolved_create_attempt` | receipt一覧による再開判定を廃止。native inventory/path/refを検査。 |
| `_publish_create_attempt` | running/partial/succeededの共通receipt保存を廃止。v2 effects/diagnosticを返す。 |
| `_reconcile_create_attempt` | 管理IDに基づくrecoverを廃止。現物確認後の新しい明示操作へ。 |
| `_materialize` | 旧consumer runtime/entrypointの特別materializationを廃止。normal native Git attachと固定tip/target identity/clean判定をcurrent createが担う。 |
| `preview_create_worktree` | control/registry付きpreviewを廃止。current createの公開dry-runへ。 |
| `create_worktree` | WriterLock/control/epoch/receipt付きwriterを廃止。current createが元選択保全・native effectsの再観測・partial/unknownを提供。 |
| `_target_payload_state` | tracked/untracked/ignoredの区別をcurrent removeのnative安全検査へ保持。 |
| `_discard_ignored_payload` | private cleanup入口を廃止。current removeの明示discardだけが対象内のignoredを扱い、outside/branchを保全。 |
| `preview_remove_worktree` | control付きpreviewを廃止。current removeの公開dry-run/同一安全条件へ。 |
| `remove_worktree` | 登録retire/WriterLock/epochを廃止。current removeがconfirmation/dirty/ignored/unlock/identity再検査・元Git errorとbranch保持を担う。 |
| `BootstrapOutcome` | 管理ID付き型を廃止。公開path/changed/observed/effectsへ。 |
| `_record_path` | bootstrap receipt pathを廃止。 |
| `_stamp` | receipt時刻保存を廃止。 |
| `_publish_record` | 共通Git bootstrap状態保存を廃止。 |
| `_run_make` | native project_hook.run_make_initへ置換済み。出力を捨て、開始/終了/timeoutの観測結果だけを返す。 |
| `bootstrap_worktree` | registry/recover/lease/WriterLock/epochを廃止。direct_bootstrapで明示targetとmakefile/選択/identityを検査して実行。 |

worktree_target.pyは別の旧workbench.py/worktree.pyからまだ参照されるため、このunitでは削除しない。参照0だけでまとめて削除せず、残るcallerを別unitで対応する。

五files退役後、source/testsの全AST（TYPE_CHECKING/from-import子moduleを含む）で旧module/fixture import 0を確認。残る文字列は通常wheelの収録禁止とstatic-inventoryの旧asset path/digestで、後者はownership証拠として維持する。新fallback/alias/build除外/skip/収集除外を追加しない。実consumer/live GitHubは未変更。

## 検証

公開保証のfocused実行は元選択保持1 passed（0.50秒）、detached base1 passed（0.49秒）、base/path/branch拒否3 passed（0.39秒）、成功hookの大出力省略1 passed（0.26秒）、非native/欠落target2 passed（0.30秒）。全て既存Greenのcharacterizationであり製品Redではない。欠落pathのerrorを最初exit5と誤期待して1 failed/1 passed（0.32秒）になったが、v2のLOCAL_TARGET_NOT_FOUND/exit4に訂正し同testを再実行した。元失敗logを保持する。

通常wheel収録禁止は旧二modulesを含むRed 1 failed（0.78秒）、source退役後の同testはGreen 1 passed（13.87秒）。fresh wheel/sdist・外部非editable venv・実console・static資産操作/仕様保全を確認。関連Worktree create/remove/bootstrap/commandsとGit観測は124 passed（23.14秒）。全source/tests Ruff check/format（363 files）、変更三test限定mypy --follow-imports=silent、diff checkが成功した。

元logは既存Epic Workbenchのiss-00413-implementation/pytest-worktree-retirement-port.log、pytest-worktree-retirement-source-{red,green}.log、pytest-worktree-retirement-related.logへ保持する。直近通常make lintは別snapshotの313 errors/40 filesで未合格であり、今回の限定成功をfull gate/Windows/Python coverageに読み替えない。残る旧writersの参照整理、現行型問題、full pytest、native OS/別Python、fresh Strict、最終手動製品確認を継続する。
