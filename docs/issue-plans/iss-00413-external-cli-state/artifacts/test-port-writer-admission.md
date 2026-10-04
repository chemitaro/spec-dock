# Writer admissionテストの移行根拠

対象は `tests/integration/test_cli_writer_compatibility_vnext.py`。変更前commit `323caf28084f7d7087e8ea96999e3ee2e2fad033`の12関数・14 casesを末尾まで読取した。RQ-413-02/03/06/16、D-03/D-05/D-06/D-12、P-03〜P-06/P-12に基づき、中央controlと全writer leaseを業務の条件にする旧契約を撤去する。

| 変更前のtest | 判断と後継 |
|---|---|
| `test_all_registered_worktrees_must_use_same_writer_protocol` | 全登録WTの一致をwriter条件にする保証を撤去。自WTの宣言だけでwriterを判定し、旧protocolを持つ別linked WTを変更せず通常Scope編集できる後継へ |
| `test_unregistered_or_stale_writer_is_rejected` 三cases | 登録ID/engine digest/中央epochの拒否を撤去。登録のない新writerは許可し、自WTの旧protocolだけは明示migration前に拒否する公開mainの後継へ。newwriterのschema/required_features拒否は`test_issue413_work_start.py`で維持 |
| `test_only_explicit_blocking_recovery_operations_stop_unrelated_writes` | 旧journalで全writerを止め、operation IDに再開権を与える保証を撤去。旧opaque control/operations filesを変更せず通常writerが動く後継へ。途中失敗の効果・新規操作判断は現行Start/Finishの公開試験で確認 |
| `test_pending_installation_group_blocks_other_writers_and_admits_its_recovery` | 全WT installer groupと再開権を撤去。旧installations filesを権限にしない後継と、`test_issue413_assets.py`の単WT保全・部分失敗へ |
| `test_pending_migration_blocks_other_writers_and_admits_its_recovery` | 全WTのmigration再開権を撤去。通常writerの旧記録非依存を確認し、migration自体の未解決remote停止・保全は`test_issue413_migration.py`へ。通常writerのfixture成功をmigration安全性の証明にしない |
| `test_maintenance_blocks_normal_writer_but_allows_migration` | 中央modeの実行権を撤去。maintenance/未登録/古いdigestがある旧controlを保全したまま自WTの新宣言で判断する後継へ |
| `test_maintenance_can_repair_mixed_registered_worktrees` | maintenance下の全WT一括修復を撤去。自WTだけの明示migrationと、別WT/共通Gitを保持する現行migration試験へ |
| `test_control_store_preserves_epoch_and_detects_stale_update` | 新しいcontrol/epoch writer APIを撤去。旧file bytesの不変を確認する後継へ。optimistic検査は実scope metadata/直接記録の捕捉対象に限定し、`test_issue413_scope_edit.py`およびwork-target store試験で維持 |
| `test_git_common_directory_is_shared_by_linked_worktrees` | 実Gitのmain/linked common-dir一致を後継で維持。登録tableから取得しない |
| `test_second_process_times_out_and_killed_owner_releases_lock` | 全writer用lockをStartだけのOS排他へ限定。`test_start_lock.py::test_start_lock_excludes_another_process_without_creating_files`と`test_terminated_owner_releases_lock_without_cleanup`、`test_issue413_start.py`の実process同時開始/強制停止で維持 |
| `test_worktree_lease_rejects_recursive_exclusive_use` | 全writerのleaseを撤去。Start排他中にも別linked WTの実CLIによるScope編集が成功する後継へ |
| `test_writer_transaction_takes_sorted_worktree_leases` | 全writer/全WT leaseの取得順保証を撤去。同じ後継で共通排他を普通の編集へ拡張しないことを確認。Startの同Scope重複拒否と兄弟Issue並行は現行同時Start試験で維持 |

後継四casesは公開mainまたは別processの`spec_dock.cli:main`を使う。旧control/pendingと書かれた記録は不活性のopaque fixtureで、旧writer/helperを実行しない。これらのfixtureを有効な旧journalの再開証明とは扱わない。元file bytesと他WTを比較し、registry、epoch、pin、journal、直接選択を生成しないことを確認する。

新規保証の製品Redではなく、既存実装のGreen回帰である。OS排他中の別WT編集はmacOSの実processの証拠であり、Windows native保証ではない。runtime内の旧writer実装退役と全体type/pytest gateは別途残る。
