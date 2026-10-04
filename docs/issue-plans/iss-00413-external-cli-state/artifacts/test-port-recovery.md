# 旧復旧テストの移行・分離

対象: `tests/integration/test_cli_recovery_vnext.py`。旧31関数を読取り、23件のoperation/control/journal前提を確定仕様のD-11/D-12へ対応させた。無条件skipや通常pytestの除外は追加しない。

新しい公開matrixは、旧十二種類の操作に対する `--resume` と `--rollback` を、project/Git/ghにアクセスできない条件で拒否する。exit2、v2診断、effects空、recovery=null、operation IDなし、旧証拠bytesとtree不変を検査する。過去のremote送信意図や操作対象を新processへ移植しない。

低水準atomic JSONの八関数とprocess helperは、operation fixtureを取り除いた別fileへ**同じ本文で移動**した。これらは既存低水準APIの検査であり、新しいScope/selection writerの経路そのものではない。旧transaction APIと共有native rename/read helpersは、providerの参照閉包を確認して別stepで整理する。この移動だけで旧provider実装の退役完了とは扱わない。

## 個別の対応

| 旧test関数 | 判断と維持する保証 |
|---|---|
| `test_migration_prepared_failure_returns_its_authoritative_operation_id` | 永続operation IDとresumeは廃止。新matrixで副作用前拒否。`test_issue413_migration.py` の公開後中断とfresh retryで現宣言の再観測を確認。 |
| `test_installation_prepared_failure_returns_group_operation_id` | 全WT group IDを廃止。新matrixでupdateのresume/rollback拒否。`test_issue413_assets.py` の実backupとuncertain retirementが後継。 |
| `test_installation_init_prepared_failure_returns_group_operation_id` | group IDとinit再開を廃止。新matrixと現行assetsのpartial publicationで、成功/未実施を区別。 |
| `test_finalization_receipt_observes_control_transition` | control/finalization receipt契約を廃止。局所init/updateと外部package更新へ移行。新matrixで過去操作の実行0。 |
| `test_prepared_engine_handover_receipt_does_not_claim_zero_effect` | engine handover/世代receiptを廃止。現行assetsのunknown/succeeded効果表示を維持し、旧resumeを拒否。 |
| `test_scope_delete_recovery_commands_do_not_repeat_original_plan_flags` | resume/rollbackコマンド生成を廃止。新matrixはdelete両flagを拒否。公開deleteの確認・preview・backup保全は `test_scope_delete_commands_vnext.py` に移行済み。 |
| `test_every_recoverable_command_has_a_durable_pending_journal` | 十二操作のdurable journalを廃止。新公開matrixは十二操作×二flag=24 casesで退役診断・効果0・旧証拠不変を確認。 |
| `test_non_recoverable_command_cannot_create_blocking_journal` | 操作登録とblocking journal型を廃止。通常のread-only・diagnosticsは旧journalから権限を導出しない。現行Doctorのdefault/legacy分離で確認。 |
| `test_resume_uses_original_fixed_target_and_rejects_changed_request` | resume request比較を廃止。新matrixは保存対象へ再接続しない。公開Scope/Startのexact guard、確認時の再検査を後継とする。 |
| `test_resume_accepts_recorded_partial_revision_and_rejects_other_changes` | partial revisionのjournal再生を廃止。新matrixで拒否し、現物のOCCはScope edit/metadata保全の公開試験で維持。 |
| `test_verified_local_non_application_can_retry_after_remote_create` | 旧effect planの再実行を廃止。`test_scope_create_commands_vnext.py` の確定remote ref→新explicit importはGETだけで復旧しPOSTを繰返さない。 |
| `test_failed_remote_effect_cannot_be_reclassified_as_not_applied` | journal内effect変換を廃止。不明remoteをnot_attemptedに偽らない保証は公開Scope create/Finishのunknown effect・送信一回の試験で維持。 |
| `test_journal_update_cannot_retarget_an_existing_operation` | journal更新APIを廃止。新matrixがretarget/replayを入口で拒否。公開操作のfixed target/metadata再検査を維持。 |
| `test_journal_update_uses_identity_of_the_verified_bytes` | journal fileのidentity比較は不要。直接対象の捕捉record/token解除とmetadata publicationのidentity安全性に移行。 |
| `test_journal_creation_syncs_parent_before_publishing` | journal作成そのものを廃止。現行direct record/scaffoldのfsync・publication失敗保全を保護。低水準atomic JSON八件は本checkpointで変更せず分離。 |
| `test_unknown_remote_effect_requires_observation_before_retry` | 永続remote intentの観測型を廃止。公開Finishはfresh GETでcompletedを確認し、未確定ならselectionを保持する。createのunknownは正式IDなし・再POSTなし。 |
| `test_remote_create_receipt_survives_restart_and_cannot_be_rewritten` | create receiptの永続保存を廃止。今回返した確定refと明示importで扱う。fresh processから失われた過去送信意図を推測しない。 |
| `test_observed_not_applied_allows_recorded_retry_only` | recorded retryを廃止。新matrixで再生要求0。新しい利用者操作が現状を読み直す契約へ変更。 |
| `test_journal_cannot_erase_effect_or_mark_unknown_as_success` | journal更新検査を廃止。公開envelopeのunknown/succeededとpartialの整合、失われた応答のFinish/create試験を後継とする。 |
| `test_unimplemented_rollback_cannot_clear_a_pending_journal` | 未実装rollback executorを廃止。新matrixで全旧対象のrollbackを副作用前に拒否し、既存証拠を保持。 |
| `test_planned_effects_cannot_be_skipped_or_reordered_to_clear_blocker` | journal effect-plan完了判定を廃止。公開操作で今回の成功/不明/未実施を正直に返す。永続blockerを新設しない。 |
| `test_atomic_json_exchange_failure_keeps_previous_bytes` | 関数本文を変更せず `test_atomic_json_publication.py` へ移動。低水準の旧atomic APIの保全確認であり、新writerの永続journal保証へは読み替えない。 |
| `test_atomic_json_exchange_preserves_racing_destination` | 関数本文を変更せず `test_atomic_json_publication.py` へ移動。低水準の旧atomic APIの保全確認であり、新writerの永続journal保証へは読み替えない。 |
| `test_atomic_json_exchange_error_after_effect_blocks_blind_retry` | 関数本文を変更せず `test_atomic_json_publication.py` へ移動。低水準の旧atomic APIの保全確認であり、新writerの永続journal保証へは読み替えない。 |
| `test_atomic_json_create_only_has_no_second_hardlink` | 関数本文を変更せず `test_atomic_json_publication.py` へ移動。低水準の旧atomic APIの保全確認であり、新writerの永続journal保証へは読み替えない。 |
| `test_journal_create_preserves_original_publish_error_with_retained_stage` | JournalStoreとそのstage生成を廃止対象へ移す。公開Scope/Finish/migration/installationのnativeエラー・backup・unknown効果保全を後継とする。 |
| `test_atomic_json_killed_after_exchange_retains_old_and_blocks_retry` | 関数本文を変更せず `test_atomic_json_publication.py` へ移動。低水準の旧atomic APIの保全確認であり、新writerの永続journal保証へは読み替えない。 |
| `test_atomic_json_refuses_symlink_destination` | 関数本文を変更せず `test_atomic_json_publication.py` へ移動。低水準の旧atomic APIの保全確認であり、新writerの永続journal保証へは読み替えない。 |
| `test_atomic_json_refuses_symlink_ancestor` | 関数本文を変更せず `test_atomic_json_publication.py` へ移動。低水準の旧atomic APIの保全確認であり、新writerの永続journal保証へは読み替えない。 |
| `test_atomic_json_rejects_hardlinked_target_and_accidental_replace` | 関数本文を変更せず `test_atomic_json_publication.py` へ移動。低水準の旧atomic APIの保全確認であり、新writerの永続journal保証へは読み替えない。 |
| `test_corrupt_journal_is_not_treated_as_completed` | JournalStore.pending admissionを廃止。現行Doctor --legacyはinvalid JSONを報告してbytesを保全。migrationは未照合remoteを拒否し、完了へ偽装しない。 |

## 実行結果

二ファイルは32 passed（0.14秒）。最初の二runの各24失敗は、testでv2 schema名とrecovery fieldの不在を誤って期待したものだった。確定CLI契約の `specdock.cli/v2` と `recovery=null` へ訂正し、製品Redには数えない。旧八関数は初回から全件成功した。

関連Scope create/import/Finishとmigrationを合わせて148 passed（39.36秒）。全source/tests Ruff check/format（424 files）、変更二test限定mypy --follow-imports=silent、diff checkも成功した。全体type/pytest、native Windows、fresh Strict、実consumer切替と最終手動確認は別の未完了条件である。
