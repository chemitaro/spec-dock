# 旧dispatcherとcommand層の製品退役

Issue #413 / P-12 / D-11。clean 7e3e0eddを親に、下記18 source files・84 top-level symbolsを全文確認した。名前だけで判断せず、ASTでsource/testsの`import`と`from ... import`（TYPE_CHECKINGを含む）を調べ、候補外からのimportが0であることを確認した。残る動的文字列の検索結果はstatic ownership inventoryの退役path/digestであり、実行moduleではない。このinventoryを消すと既知旧consumer資産の保全ができないため保持する。

固定入口退役と四adapter test退役を先行したため、旧dispatcherへの外部callは残っていない。下記18 filesを一緒に削除し、fallback・deprecated alias・wheel除外条件は追加しない。通常wheelがsourceと同じ一つのruntimeを収録する受入れ試験へ、十八moduleの明示収録禁止を加える。

## Symbolsごとの判断

同じ行のdata types/helpersも候補内専用である。現在のlayerとpublic testへ対応づけ、公開leafを減らさない。

| Source | 退役symbols | 現行保証と判断 |
| --- | --- | --- |
| `commands/active_vnext.py` | `ActiveData`, `_data`, `run_active_show`, `run_active_change` | `commands/runtime_dispatch.py` と `application/direct_active.py`。一つのdirect selectionとv2 dataへ統一し、registered revision/chain編集は廃止する。 |
| `commands/artifact_vnext.py` | `run_artifact_query`, `run_artifact_change` | `application/direct_artifact.py`。public catalog/単一file publicationとOS境界のeffectを維持し、旧active storeとreceipt schemaは使わない。 |
| `commands/branch_vnext.py` | `BranchData`, `run_branch_command` | `application/branch_operations.py`。Git ref/checkoutを使い、Scope branch binding/journal/resumeを廃止する。 |
| `commands/dependency_vnext.py` | `DependencyListData`, `run_dependency_query`, `run_dependency_change` | `application/direct_dependencies.py`。metadataのdeclared/effective edgesとdefault/live readinessを維持し、shared writer admission/cacheは使わない。 |
| `commands/installation_vnext.py` | `InstallationUpdatePlan`, `InstallationUninstallPlan`, `InstallationInitPlan`, `InstallationFinalizePlan`, `EngineHandoverPlan`, `run_installation_init`, `run_installation_show`, `_run_engine_handover`, `run_installation_update`, `run_installation_uninstall` | `application/direct_installation.py`、`direct_static_update.py`。一つの指定WT・package static bytes・外部backupへ統一し、group/fixed archive/maintenance/finalization/engine handoverは廃止する。 |
| `commands/scope_create_vnext.py` | `run_scope_create` | `application/direct_scope_publish.py`。GH番号SSOT・preview/confirmationを維持し、新local Scopeとjournal resumeを廃止する。 |
| `commands/scope_delete_vnext.py` | `ScopeDeleteData`, `run_scope_delete` | `application/direct_scope_delete.py`。明示targetとbackup付き削除を維持し、Git内quarantine/journal recoveryは廃止する。 |
| `commands/scope_import_vnext.py` | `run_scope_import` | `application/direct_scope_publish.py`。既存GH Issueの番号とscaffoldを維持し、recorded operationのresumeを廃止する。 |
| `commands/scope_lifecycle_vnext.py` | `ScopeLifecycleData`, `run_scope_lifecycle` | `application/direct_scope_lifecycle.py`。既存local codecとGH Close/Reopen・confirmation/OCCを維持し、shared admission/journal recoveryは廃止する。 |
| `commands/scope_query_vnext.py` | `ScopeSummary`, `ScopeListData`, `ScopeListFilter`, `ScopeShowData`, `ScopeEditData`, `_summary`, `run_scope_query`, `run_scope_edit` | `commands/runtime_dispatch.py`、`application/scope_query.py` と `direct_scope_edit.py`。現metadataのread/title editへ統一する。 |
| `commands/scope_result_vnext.py` | `ScopeData`, `ScopeStatusData`, `ScopeProjection`, `ScopeWriteData`, `ScopeFailureData`, `planned_scope_write`, `project_scope`, `project_scope_view` | `presentation/command_data.py`、`commands/runtime_dispatch.py` の `scope_payload`。v2 FamilyData/current observationsへ統一し、旧WorkContext固有data types/projectionを廃止する。 |
| `commands/work_vnext.py` | `WorkContext`, `WorkStartData`, `WorkFinishData`, `run_work_start`, `run_work_finish` | `application/work_start.py` と `direct_finish.py`。Startだけの短い排他、GitHub確認、captured recordのFinishへ統一し、epoch・old selection chain・journal/resumeを廃止する。 |
| `commands/workbench_vnext.py` | `WorkbenchCopyData`, `run_workbench_copy` | `application/direct_workbench.py`。同cloneのnative absolute pathとfile単位copy/conflictを維持し、registered aliasとreceiptは使わない。 |
| `commands/workspace_diagnostics_vnext.py` | `WorkspaceDiagnosticsData`, `_result`, `run_workspace_diagnostics`, `run_ci_workspace_validation` | `application/direct_validation.py` と `direct_diagnostics.py`。読取診断/HEAD CI validationを維持し、control必須の旧contextを廃止する。 |
| `commands/workspace_migrate_vnext.py` | `MigrationOutcome`, `MigrationPreviewFile`, `MigrationPreview`, `run_workspace_migrate` | `application/direct_migration.py`。自WT declarationだけを外部backup後に移行し、inventory mapping/whole-group journal/recoveryは廃止する。 |
| `commands/workspace_sync_vnext.py` | `WorkspaceSyncData`, `run_workspace_sync` | `application/direct_sync.py`。現metadataと全native WT観測による出力へ統一し、generation cache/current pointerの中央管理は廃止する。 |
| `commands/worktree_vnext.py` | `WorktreeSummary`, `WorktreeListData`, `WorktreeCreatedData`, `WorktreeRemovedData`, `_summary`, `run_worktree_query`, `run_worktree_change` | `application/direct_worktrees.py`。Git native inventory/create/remove/explicit bootstrapを維持し、registration/epoch/recoverは廃止する。 |
| `cli/vnext_runtime.py` | `RuntimeOutput`, `ExpectationMismatch`, `_repository_root`, `_context`, `_failure`, `_failure_data`, `_target_for_failure`, `_journal_receipt_failure`, `_classified_failure`, `_nonblocking_io_receipt`, `_unknown_nonblocking_receipt`, `_resolved_scope_target`, `_confirm_before_effect`, `_confirmation_state`, `_enforce_expectations`, `_dispatch_regular`, `run_vnext` | `spec_dock.cli:main` と `commands/runtime_dispatch.py`。utilityのcontext不要・v2/error/raw Gitと各leafへの一つのdispatch経路を維持する。旧control/registry/fixed pinのcontextとjournal/receipt分類は廃止する。 |

## 維持する公開証拠

44 leaf contract、context-free utility、normal wheel/sdist/isolated console、Start/Finish/active/branchとnative worktrees、Scope/dependency/artifact/workbench、read-only diagnostics、migration/static installationは現在の`test_issue413_*`、`test_cli_vnext_contract.py`、port済みentrypoint/CI/recovery suiteで検査する。過去の個別test移行判断は本packの`test-port-*.md`を参照する。

先行した実wheelのRedは正常buildしたartifactに候補十八moduleが含まれることで失敗した（1 failed、0.79秒）。source削除後、同じ試験と関連公開suiteの結果はimplementation-reportへ記録する。旧application/control/journal/runtime_loaderはこのsource削除の候補に含めず、現行経路が使うhelpersを先に分離する。未完了の全体型gate・Windows・fresh Strict・手動製品確認をpassへ読み替えない。
