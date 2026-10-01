# Scope lifecycle / query / deleteのテスト移行

変更前は `b8c63efa26919fdf073cea37e1514a9bada0e16d`。三filesの十一test関数を全文確認し、RQ-413-07/09/13/16、D-07/D-09/D-11/D-12、CLI v2契約へ照合した。旧内部dispatcher・WorkContext・controlの登録・新規local発行・operation journalを使わず、公開mainの保証へ移す。

| 旧file / test | 維持する保証と後継 |
|---|---|
| `test_scope_lifecycle_commands_vnext.py::test_scope_close_prompts_on_tty_and_respects_denial` | 公開mainと既存local backend codecで確認表示、noによるbytes不変、yesによるcompletedを確認。stdinはTerminalAnswerという外部端末の代替であり、native PTYの証拠とは区別する。実PTYのyes/noは現行`test_issue413_scope_lifecycle.py`で維持 |
| 同file `test_scope_close_current_prompts_on_tty_without_noninteractive_guard` | @currentを表示し、guard省略でも端末でnoを選ぶとremote PATCH0・直接記録不変で終了する後継へ。新規local作成でfixtureを作らない |
| 同file `test_scope_close_current_json_preserves_requested_selector` | 現在のdirectからGH-backed対象を解決し、result.scopeのIDとcompleted、該当Issue一回PATCH、直接記録保持を確認。旧v1 target.requested欄は確定v2 schemaに含まれず、復活させない |
| 同file `test_scope_close_current_rejects_selection_change_during_prompt` | `test_issue413_scope_lifecycle.py::test_scope_lifecycle_refuses_a_changed_direct_selection_after_terminal_confirmation`へ移した。実Startが確認待ち中に選択を変更する競合をRed→Greenで修正済み。本portではguard有無×Close/Reopenの四casesへ広げ、旧guard省略条件も検査 |
| 同file `test_scope_close_reopen_cli_previews_and_updates_local_lifecycle` | 真正の既存local backendのdry-run、承認不足、completed/open/not-planned更新、Git branch/HEAD不変を維持。新規local発行とjournal resumeはD-09/D-11で撤去。旧prepared IDや再開権を持ち込まない |
| 同file `test_scope_close_json_reports_completed_scope_and_same_snapshot` | 上のlocal lifecycle後継でresult.scope.id、state、source/authority=localとmetadata現物を比較。旧v1 snapshot ID/worktree登録IDはv2の保証から撤去 |
| 同file `test_scope_mutation_checks_expected_current_and_backend_before_edit` | GH-backed directに対する既知IDのcurrent不一致、backend不一致でmetadata/record/effects不変。合致する二guardで@currentだけを編集する。旧内部admissionの必須guardや私的STATE_CONFLICT文字列を、現在の公開option/error契約へ変更 |
| `test_vnext_runtime_scope.py::test_scope_list_show_and_edit_target_the_same_scope` | kind/parentのlist、@current show、preview、title/revision更新を同一GH-backed Issueで比較。日本語等の文書本文と直接記録は保持。旧v1登録ID/snapshot fieldを検査しない |
| 同file `test_unexpected_failures_report_effect_uncertainty_by_command_kind` | 自分のdispatcher関数へのmockを撤去。read/edit双方で実subprocessのGit故障を注入し、元stderr・returncode・exit5/effects=[]・repo tree不変を確認。公開後のsucceeded/unknown区別は既存`test_issue413_scope_edit.py`の実filesystem故障試験で維持する |
| 同file `test_runtime_rejects_preflight_identity_change_before_scope_edit` | 旧engine preflightの二root引数を撤去。明示projectが正確なGit rootでない場合は、rootへ勝手にfallbackせず効果前拒否し、全repo bytesを保持する後継へ。操作途中のphysical identity/actor改変検査は現行scope edit/delete/publication suiteで維持 |
| `test_scope_delete_commands_vnext.py::test_scope_delete_cli_requires_confirmation_and_previews_without_writes` | --yes不足とdry-runでwrite0、明示外部backupにmetadata/本文の実bytesを保全してから削除、GitHub/branch保持を公開mainで確認。再操作は既存backupを上書きせず拒否。旧quarantine/replayの成功期待はD-09/D-11/D-12で撤去 |

後継三filesは十cases。確認競合四casesは別fileで実processとして維持する。新規localを作るAPIは実行せず、既存local fixtureの読取・更新互換だけを検査する。GH通信はhermetic executableで、live GitHubの変更はない。新規削除fixtureにバックアップを明示するのは公開契約であり、実consumerの削除を認可したものではない。

最初の移行runの一失敗は、既存backupへ再操作した時にmissing target/exit4を期待したものだった。現在の安全な事前検査はbackup destination already exists/exit3であり、元backupを保持する。期待を訂正し、製品不具合Redとは扱わない。各旧保証の廃止判断を、全テスト除外・一括skip・通常CI省略へ転用しない。
