# Work / branchテストの公開入口移行

変更前 `56200de0440b58bf2cc22d11fe520130a5d785af` の次の三files・七test関数を全文確認した。RQ-413-04/05/06/07/09、D-06〜D-08/D-11とCLI v2 schemaに照合し、旧WorkContext・run_vnext・active_store・control/journal APIをfixtureと入口から外す。

| 旧file・test | 維持する保証と変更理由 |
|---|---|
| `test_work_commands_vnext.py::test_work_commands_start_and_finish_all_three_kinds` | 三kindのGit branch作成・checkout、直接選択、dry-run、Finishを三GH-backed公開casesで維持。一WTで三階層を重ねて選択し、後から親へ昇格する期待はD-07により撤去。各caseで一件選択→該当GitHub Issueだけcompleted→捕捉記録解除、branch保持と全metadata不変を検査 |
| 同file `test_work_adapter_plans_start_and_finish_without_writes` | 両dry-runでref/metadata/選択/remote不変、Finishの--yes必須を維持。operation IDの有無を実行権として確認せず、実Git/remote/recordの効果を比較 |
| `test_branch_commands_vnext.py::test_branch_adapter_create_show_switch_and_dry_run` | 公開mainでcreate/show/switch、固定tip、dry-run書込0を維持。永続binding・journal resumeはD-06/D-11で廃止。binding_persisted=falseを検査し、既存refの再createをeffects=[]で拒否、native Git ref不変も追加 |
| `test_vnext_runtime_work.py::test_vnext_cli_executes_three_kind_work_lifecycle_with_json` | 三kind実行は上の三casesへ。公開parserから@current/--expect-currentを解決し、v2・command・data.scope_id・completed・捕捉token解除を確認する後継へ。旧v1 target/snapshot/derived_dirty欄は確定v2 schemaに含まれない |
| 同file `test_vnext_cli_rejects_engine_mismatch_before_work_mutation` | 独自engine digestを実行権にする保証を撤去。自workspaceの旧writer宣言ではFinishがmetadata/remote効果前に停止する後継へ。通常wheel・opaque旧locatorの非依存はentrypoint/writer admission suiteで確認 |
| 同file `test_vnext_cli_requires_base_for_new_work_branch` | 新branchのbase必須、拒否時ref/選択の効果0を公開mainとnative Gitで維持 |
| 同file `test_vnext_active_show_set_clear_and_dry_run` | show、同一direct set、clear/dry-runを維持。空からのsetによる取得とancestor clear後の親昇格はD-07で撤去。前者WORK_START_REQUIRED、後者emptyを確認し、Git branchとremote stateを保持 |

後継九casesは実Gitとstateful gh executableを使い、実GitHubには接続しない。最初の移行時の四失敗は、既存branchの再Startで明示--branchを欠いたことと、旧v1 target欄を期待したことだった。新実装の不具合Redではなく、確定契約に合わないtest期待を訂正した。製品のparserや互換flagは追加しない。

既存のhook/unknown効果/同時Start/遅い解除/guard検査は `test_issue413_branch.py`、`test_issue413_work_start.py`、`test_issue413_active.py`、`test_issue413_finish.py` 等に残す。これらの移行でnative Windowsや全体gateが合格したとは扱わない。
