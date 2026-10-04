# 旧control・registry・writer lock helpersの退役

## 対象と判断

採用済み[設計D-05](../design.md#d-05)と[旧source置換表](../design.md#d-11)に従う。読取基準は `5e28013ffea2f0550a16db6ff637dd0ce25e53a9`。旧七source files、1002行、38 top-level symbolsを全文確認した。絶対／相対／TYPE_CHECKING／from-import子moduleを含む候補外importは0。文字列参照は既知旧資産のpath/hash、fresh-process非load検査、通常wheel不在検査だけである。

Git共通領域へcontrol、epoch、全worktree登録、local採番予約、永久branch binding、復旧journal、全writer lock file／worktree lifetime leaseを作る旧helpersを削除する。互換alias、fallback、代替台帳は設けない。通常writerの現schema/protocol検査、Startだけの短い排他、各WTの直接選択と捕捉token解除、read-only旧情報診断は現行moduleで維持する。旧Git領域の実データは削除／修復しない。

## 三十八symbolsへの対応

同じrowのsymbolsには同じ判断を適用する。

| 旧module | symbols | 現行の保証／退役理由 |
|---|---|---|
| infra/control_store | WorktreeRegistration、ControlState、control_directory、decode_control、load_control、store_control | 全writerのready/epoch/engine登録正本とGit内control writerを廃止。project_contextのworkspace宣言検査とlegacy_readerの明示readonly診断を維持 |
| infra/engine_handover_store | EngineHandoverRecord、new_engine_handover、_path、write_engine_handover、read_engine_handover、pending_engine_handovers | 固定engine世代のhandover/UUID phase記録・pending gateを廃止。通常外部packageとcurrent一WTのstatic updateを使う |
| infra/finalization_store | FinalizationRecord、new_finalization、_path、write_finalization、read_finalization、pending_finalizations | 全WTのmaintenance→ready／epoch確定journalを廃止。自workspace一fileのwriter宣言切替と実保全を維持 |
| infra/installation_group_store | pending_installation_groups | 全writerを止める共通installation group pending検査を廃止。旧recordはlegacy_readerで未知／不完全性を含め報告し、replayしない |
| infra/operation_journal | _pairs、_decode、JournalStore、_fsync_directory、_ensure_durable_directory、_assert_journal_transition | 固定target/engine/epoch/UUID/intent/retry/resumeのGit内journalを廃止。今回操作のmemory effects・partial/unknownを返し、後続processは現物を再観測する |
| infra/registry_store | _decode_registry、_encode_registry、_working_tree_ids、historical_local_ids、RegistryStore | 全WT・全Git履歴を走査するlocal high-water/予約/tombstone/branch binding台帳を廃止。新番号はGitHub、既存ID/metadata codecは保持し、IDを一括変更しない |
| infra/writer_lock | WriterLockBusy、_lock_file、_try_lock、_unlock、_AdvisoryLock、WriterLock、WorktreeLease、writer_transaction | 全writerとWT寿命のfile lockを廃止。current start_lockは既存common directoryのPOSIX flock／Windows物理identity mutexを使い、Git内entryを作らない。Windows native対応の認定は別試験が必要 |

今回既存test関数の削除は0。旧group_journal等の別package、domainの台帳／復旧型とその他の旧helpersは別unitで利用箇所を確認する。`domain/writer_admission.py`、`infra/migration_backup.py`、`start_lock.py`、`work_target_store.py`、`legacy_reader.py` は保持する。

## 現行の公開保証

- `test_start_creates_checks_out_and_selects_without_git_control`：branch作成→checkout→選択を行い、Git内controlを作らない。
- `test_start_dry_run_does_not_take_lock_or_create_branch_or_selection`：previewは予約やlockにしない。
- `test_concurrent_starts_share_exclusion_and_only_same_scope_conflicts`：実別processの同clone排他と重複検査を維持する。
- `test_killed_start_preserves_checkout_and_next_start_needs_no_journal` と `test_killed_start_at_record_boundary_requires_no_operation_journal`：中断後のGit現物・選択境界を保全し、journal replayを要求しない。
- `test_legacy_doctor_reports_pending_remote_effects_without_resuming_or_executing_old_engine` と `test_legacy_doctor_classifies_old_migration_and_installation_records_without_replaying_them`：旧記録を再実行せず診断する。
- `test_update_retires_only_known_legacy_runtime_files_after_preservation`、`test_static_changes_refuse_unknown_current_or_retired_files_before_preservation`、`test_update_retains_the_backup_and_reports_uncertain_retirement_without_rollback`：保全と未知改変拒否・不確定な部分結果を維持する。

## 実測

通常wheelの旧七module実収録禁止はRed 1 failed（0.90秒）。source退役後の同testはGreen 1 passed（16.52秒）、wheel/sdist・外部非editable venv・実consoleまで完走した。

Start／lock options／Doctor／別process競合・kill／migration／static assetsの七suiteは259 passed（120.89秒）、exit0。全source/tests Ruff check/formatは333 filesで成功。変更wheel test限定mypy `--follow-imports=silent` とdiff checkも成功した。skip／収集除外を追加していない。

元logは既存Epic Workbenchの `iss-00413-implementation/pytest-control-retirement-source-{red,green}.log` と `pytest-control-retirement-related.log` に保持した。

通常full lintの55 errorsは旧clean d7f47fc0のsnapshotであり、現在値ではない。残る旧source、通常full gates、native OS／別Python、fresh Strictと最終手動確認は未完了。実consumer／GitHub／他WTは変更していない。
