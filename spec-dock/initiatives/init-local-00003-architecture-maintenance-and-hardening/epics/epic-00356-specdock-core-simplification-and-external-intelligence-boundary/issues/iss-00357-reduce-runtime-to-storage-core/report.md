---
種別: 実装報告書（Issue）
ID: "iss-00357"
タイトル: "Reduce Runtime to Storage Core"
関連GitHub: ["#357"]
状態: "approved"
作成者: "main orchestrator"
最終更新: "2026-08-10"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00356", "init-local-00003"]
---

# iss-00357 Reduce Runtime to Storage Core — 実装進行報告

## 現在の結論

- Product Ownerは2026-08-10に、親EpicのRequirement / Design / Planと、本IssueのDraft 1を承認した。
- Draft 1はevidence-onlyの入力として正本`requirement.md`、`design.md`、`plan.md`へ統合し、repository factsと独立review findingsで精度を補った。
- Requirement、Design、Planはすべてapprovedで、各phaseのfresh `spec-reviewer`がpassした。
- `issue start iss-00357`を実行し、branch `iss-00357-reduce-runtime-to-storage-core`とactive contextを確立した。
- E00のread-only inventoryを実行し、retained / removed / sharedのpath、symbol、consumer、Action、ownerを確定した。source / testの変更はまだ行っていない。
- E00のreport evidenceは2回のfresh `spec-reviewer` failを受けて修正し、3回目のfresh reviewでfindingsなしのpass（confidence 0.99）を得た。M0 commitとpost-commit clean checkが終わるまでS01へ進まない。
- PR、merge、`issue finish`はまだ実行していない。正本のlocked expectationを変える必要が生じた場合は、該当stepを停止してR/D/P amendmentとfresh reviewへ戻る。

## 承認済み正本

| 文書 | 状態 | 主な固定内容 |
|---|---|---|
| `requirement.md` | approved | Storage Core CLI、selection-only active、start / finish順序、Current / Historical Artifact、generic import、Fresh scaffold、互換性、handoff |
| `design.md` | approved | 既存`ActiveManifestEntry` / schema v2、dependency-only readiness、partial result、module delta、migration / rollback、ownership |
| `plan.md` | approved | E00〜S99の縦スライス、`CL-357-001`〜`CL-357-015`、step-local delegation、Red / Green、具体テストカード、review gate |

## Spec Interpretation / Decision Ledger

| ID | Status | Type | Trigger | Options Considered | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|
| `DEC-357-E00-001` | resolved | ownership interpretation | 通常CLI外のshipped wrapper `spec-dock-chatgpt`が認知的Runtimeへ直接到達することをE00で確認した | 357のremoved Runtime候補に含める / 357では保持して360へhandoffする | rejected: 357での削除候補化を棄却する。RQ-357-001とAC-357-001のCurrent surfaceは通常`spec-dock` parser / registry / helpで、Design §13の明示Delete候補に別executableのissue-planning経路はない。Design §14に従い、wrapper / `chatgpt_app` / chatgpt CLI / issue-planning Runtime / direct authoring scriptsは360 ownerの`Handoff keep`とする | `requirement.md` RQ-357-001 / AC-357-001、`design.md` §13 / §14、通常`app.main` graphと独立`spec-dock-chatgpt` graphの実在照合 | H91で360向けprovider asset inventory、到達経路、hash evidenceを渡す |

locked expectationの追加・変更はない。E00で見つかった通常CLI外の到達経路は、承認済みDesign §14 / H91のhandoff inventoryへ割り当てた。

## Objective Alignment Ledger

| target | primary objective evidence | secondary requirement evidence | inversion risk | reviewer verdict |
|---|---|---|---|---|
| planning adoption | `requirement.md`のStorage Core縮小と`design.md`のTarget boundaryを`plan.md`の縦スライスへ直接追跡した | compatibility、migration、handoff、step-local review / test evidenceを同じclosureへ従属させた | none | pass |

## Evidence Adoption Ledger

| ID | adoption_status | source | target | rationale | evidence | next_action |
|---|---|---|---|---|---|---|
| EAL-357-001 | adopted | `artifacts/20260809t125145z-draft-requirement-strict-vertical-slice-requirement.md` | `requirement.md` | Product OwnerがDraft 1の内容を承認し、親Epic契約と現行Runtime事実に照合して正本化した | `requirement.md`とfresh requirement review pass | execute approved plan |
| EAL-357-002 | adopted | `artifacts/20260809t125146z-draft-design-strict-vertical-slice-design.md` | `design.md` | 承認済み要件を既存layer / model / portへ割り当て、fresh design reviewの精度指摘を反映した | `design.md`とfresh design review pass | execute approved plan |
| EAL-357-003 | adopted | `artifacts/20260809t125147z-draft-plan-strict-vertical-slice-plan.md` | `plan.md` | Draftのvertical sliceをStrict Plan契約へ統合し、closure、failure、delegation、test cardを具体化した | `plan.md`と最終fresh plan review pass | execute approved plan |

未解決のstale / blocked evidenceはない。Draft artifactsは履歴証跡として保持し、正本authorityにはしない。

## Spec Authoring Gate

| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |
|---|---|---|---|---|---|---|
| requirement | 親Epic R/D/P、承認済みDraft 1、CLI / active / lifecycle / Artifact / validateの現行契約を照合した | none | adopted | pass | no | execute approved plan |
| design | 承認済みRequirement、Runtime layered architecture、既存model / ports、module ownership、failure resultを照合した | none | adopted | pass | no | execute approved plan |
| plan | 承認済みR/D、Strict Plan Guide、全RQ / EC / AC、selector / failure / parity test、step-local delegationを照合した | none | adopted | pass | no | execute approved plan |

## Delegated Draft Evidence

| created_by_role | scope_id | artifact draft path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration_result | rejected portions | blockers | reviewer result | promotion decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT-use-strict | iss-00357 | `artifacts/20260809t125145z-draft-requirement-strict-vertical-slice-requirement.md` | 親Epic R/D/P、baseline SHA `2c75e0c02cb65a6e74040a72dc161d342d661091`、approved interview decisions | `requirement.md` | adopted | `requirement.md` | pass: canonical diff inspected and reviewer findings integrated | Draft 1 requirement integrated and repository-grounded | none | none | pass | execute approved plan |
| ChatGPT-use-strict | iss-00357 | `artifacts/20260809t125146z-draft-design-strict-vertical-slice-design.md` | `requirement.md`、親Epic Design / Plan、Runtime source layout | `design.md` | adopted | `design.md` | pass: canonical diff inspected and reviewer findings integrated | Draft 1 design integrated with exact model and module boundaries | none | none | pass | execute approved plan |
| ChatGPT-use-strict | iss-00357 | `artifacts/20260809t125147z-draft-plan-strict-vertical-slice-plan.md` | `requirement.md`、`design.md`、Strict Plan Guide、specialist evidence | `plan.md` | adopted | `plan.md` | pass: canonical diff inspected and final plan review passed | Draft 1 plan integrated as executable step-local contract | none | none | pass | execute approved plan |

## Grade Specialist Evidence Gate

| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
|---|---|---|---|---|---|
| strict | system-architect and implementation-planner | used | system-architectの既存active model / `check_deps` / finish result / copy mechanism / import safety境界を`design.md`へ統合し、implementation-plannerのE00・S01〜S10・S90・H91・S99 slicingを`plan.md`へ統合した | pass | ready |

## Reviewer Gate Status

| phase | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | evidence |
|---|---|---|---|---|---|---|---|
| requirement | requirement phase gate | spec-reviewer | fresh | pass | no | execute approved plan | parent trace、retained CLI、truth table、Historical catalog、validate boundaryを確認 |
| design | design phase gate | spec-reviewer | fresh | pass | no | execute approved plan | model owner、partial result、module dependency deltaを確認 |
| plan | final plan phase gate | spec-reviewer | fresh | pass | no | execute approved plan | findingsなし、overall confidence 0.98、全closure / failure / delegation / test cardを確認 |
| execution E00 review 1 | E00 docs/spec alignment | spec-reviewer | fresh | failed | no | S01 blocked | P1: category / Action / owner重複、report-only wrapper ownership。P2: closure ownerと外周parity evidence |
| execution E00 review 2 | E00 docs/spec alignment re-review | spec-reviewer | fresh | failed | no | S01 blocked | shared bridgeの`dispatch`、command contracts、`build_runtime`、`UseCases.planning_*`、issue-planning graphの明示不足 |
| execution E00 review 3 | E00 docs/spec alignment re-review | spec-reviewer | fresh | pass | no | proceed to M0 commit only | findingsなし、confidence 0.99。排他的symbol inventory、owner / Action、360 handoff、shared planning bridge、test consumer、parity evidenceを確認 |

## Workflow-Scoped Authorization

| authorization source | repo / worktree | active scope | named roles | boundary | result |
|---|---|---|---|---|---|
| ユーザーによるSpecDock workflow利用依頼と2026-08-10の実装開始依頼 | current `spec-dock` checkout | iss-00357 execution E00 | `repo-analyst`、`spec-reviewer`、`git_commit` | current repo / active Issue / current session内のE00 read-only調査、report統合、review、M0 commit。S01 source変更、外部公開、PR、merge、Issue finishは含まない | pass |

## 実装開始契約

| 最初のstep | 担当 | 入力 | 完了条件 |
|---|---|---|---|
| E00 | `repo-analyst` | approved R/D/P、baseline SHA、Runtime / tests / docs | retained / removed / shared inventoryにpath、symbol、consumer、Action、ownerが揃い、曖昧rowがない |
| S01以降 | stepごとのfresh worker | `plan.md` §8の該当contract | Redまたは代替証拠、Green、report更新、fresh reviewer passをstep単位で満たす |

Issue 358とは同時に進められる。ただしparser / registry / Runtimeは357、template prose / Authoring Guideは358のsingle writerとし、共有contractはIC-1で照合する。

## 計画時の検証結果

- Canonical Requirement review: pass。
- Canonical Design review: pass。
- Canonical Plan final review: pass、findingsなし、confidence 0.98。
- Exact-current R/D/P/report readiness review: pass、findingsなし、confidence 0.99。E00/M0のfresh `spec-reviewer` → commit → clean check契約を確認した。
- `git diff --check`: pass。
- SpecDock `workflow status --format json`: `state=ready`、`reason_code=strict-legacy-missing-assurance`、`artifact_readiness=substantive`。
- SpecDock `deps check --no-github`: `ready=true`、blockerなし。cacheは`stale=true`の警告を返したため、実装開始時に必要ならGitHub同期を更新する。
- SpecDock `validate`: pass、`nodes=221`。
- `uv run pytest tests/unit/domain/test_workflow_state.py tests/cli_runtime/test_workflow.py`: 72 passed、44 skipped。
- 正本とDraft artifactは別物として保持し、Draftをauthorityへ昇格していない。

## 実装記録

E00のread-only inventoryを開始した。source / test変更を伴うS01以降の実装は未着手である。

### E00 実行コンテキスト

- active Issue: `iss-00357`
- branch: `iss-00357-reduce-runtime-to-storage-core`
- current HEAD: `e16e97517ea3ab7287eaf6143fab2df943d71b2d`
- baseline: `2c75e0c02cb65a6e74040a72dc161d342d661091`
- baselineからHEADまでの`src/spec_dock`、`tests`、`spec-dock/scripts`差分: なし
- provider / dogfood Runtime Python manifest: `151 / 151` files、SHA-256 manifest差分なし
- E00開始前の`git status --short`: clean

### E00 Retained inventory

| path / symbol | current consumer / reachability | Action | owner |
|---|---|---|---|
| `scripts/spec-dock` | `spec_dock_runtime.app::main`を起動する通常入口 | Modify in S01 | 357 |
| `app.py::{main,_parse_args,_find_repo_root_for_legacy_doctor}` | 通常CLIのparse / dispatchとdoctor fallback | Modify in S01 | 357 |
| `cli/{parser,registry}.py` | `app.main`の通常CLI parser / registry graph | Modify in S01 | 357 |
| `commands/new.py::{command_specs,_run_new_*}` | `new_{initiative,epic,issue,artifact}`。parserからregistryへ到達 | Modify in S05/S08 | 357 |
| `commands/artifact_import.py::{command_specs,ArtifactImportFileArgs,_add_file_arguments,_file_args_factory,_run_file}` | `artifact_import_file -> UseCases.import_file_artifact` | Modify in S01/S07 | 357 |
| `commands/active.py` | `active_{set,show,clear}` | Modify in S01/S02 | 357 |
| `commands/issue.py` | `issue_{start,finish}` | Modify in S03/S04 | 357 |
| `commands/deps.py` | `deps_{check,add,remove}` | Modify in S03 | 357 |
| `commands/import_cmd.py` | `import_{initiative,epic,issue}` | Keep | 357 |
| `commands/{worktree,workbench,delete,close,update,uninstall,sync,validate,doctor}.py` | Target inventoryの対応leaf | Keep | 357 |
| `application/{set_active,issue_lifecycle,check_deps}.py` | active / start / finish / dependency projection | Modify in S02/S03/S04 | 357 |
| `application/{create_node,create_artifact_doc}.py` | `new.py`のnode / Artifact leaf | Modify in S05/S08 | 357 |
| `application/{import_node,delete_node,close_node,doctor}.py` | retained command handlerから`UseCases`経由 | Modify in S04/S09 | 357 |
| `domain/{active,artifacts,deps,validation,discussion_docs}.py` | retained active / deps / Artifact / node / validation applicationのstatic import | Modify in S02/S03/S05/S06/S09 | 357 |
| `domain/ids.py`の`normalize_id_input`以外、`domain/models.py`のplanning bridge対象以外、`domain/tree.py`の`build_graph`以外 | retained ID / node / tree operations | Modify in S02/S03/S05/S09 | 357 |
| `infra/contracts.py::{ActiveManifest,ActiveManifestEntry}` | `set_active`、`active_store`、`issue_lifecycle` | Modify in S02 | 357 |
| `infra/active_store.py` | bootstrap active storeからretained active / lifecycleへ到達 | Modify in S02 | 357 |
| `presentation/{json_state,markdown,puml}.py`、`presentation/contracts.py`の`CliText`以外 | retained command / application result renderer | Modify in S01/S04/S07/S09 | 357 |
| `presentation/cli_text.py`のprovider Artifact import renderer以外 | retained command / application result renderer（explicit file branchを含む） | Modify in S01/S04/S07/S09 | 357 |
| Runtime retention / projection tests | `tests/cli_runtime/{test_active,test_issue_lifecycle,test_new,test_artifact_import_file,test_validate,test_doctor,test_wrappers}.py` | Modify in corresponding Sxx | 357 |

### E00 Shared inventory — Delete禁止

| path / symbol | retained consumer evidence | Action | owner |
|---|---|---|---|
| `application/import_file_artifact.py::import_file_artifact` | `_run_file -> UseCases.import_file_artifact` | Keep | 357 |
| `cli/dispatch.py::dispatch` | 通常`app.main`と360 `chatgpt_app.main`が同じregistry dispatchを使用 | Keep | 357 |
| `commands/contracts.py::{CommandArgs,CommandOutcome,CommandSpec,CommandRegistry}` | 通常 / ChatGPT parser・registry・command handlerが共有 | Keep | 357 |
| `app.py::_find_specdock_dir` | 通常`app.main`と360 `chatgpt_app.main`が同じrepo-local scope解決を使用 | Keep | 357 |
| `cli/bootstrap.py::{BootstrapContext,build_runtime,_NodeReader,_Clock}`のstructural assembly | 通常`app.main`と360 `chatgpt_app.main`が同じ`Ports` / `UseCases` / context、node reader、clockを構築 | Modify in S01 preserving planning callbacks | 357 |
| `application/validate_tree.py::validate_tree`、`application/sync_state.py::sync` | retained validate / sync commandと360 `build_runtime.planning_apply`のvalidation / sync callbackが共有 | Keep | 357 |
| `application/contracts.py::{ValidateTreeRequest,SyncRequest}` | retained validate / sync commandと360 `build_runtime.planning_apply` callbackが共有 | Keep | 357 |
| `domain/ids.py::normalize_id_input` | retained node / lifecycle pathと360 planning request / contract validationが共有 | Keep | 357 |
| `domain/models.py::{SpecNodeKind,SpecNodeSeed,SpecGraph}`、`domain/tree.py::build_graph` | retained graph pathと`build_runtime.load_planning_state`が共有 | Keep | 357 |
| `infra/contracts.py::{StoredMetaRecord,DirectDependencyResolution}` | retained node / deps pathと360 planning state / dependency snapshotが共有 | Keep | 357 |
| `application/ports.py::{ValidateNodeReader,Clock,Ports.node_reader,Ports.clock}` | retained validate / node / timestamp pathと360 planning state / dependenciesがnode readerとclockを共有 | Keep | 357 |
| `infra/deps_reader.py::load_direct_dependency_resolutions` | retained deps pathと360 `planning_create` dependency loaderが共有 | Keep | 357 |
| `infra/git_cli.py::origin_github_repo_slug` | retained `GitGateway`と360 issue-planning repository resolverが共有 | Keep | 357 |
| `application/contracts.py::UseCases.{create_initiative,create_epic,create_issue,create_artifact_doc,import_initiative,import_epic,import_issue,set_active,show_active,clear_active,sync,check_deps,mutate_deps,delete_node,close_node,issue_start,issue_finish,validate_tree,doctor,worktree_create,worktree_list,worktree_show,worktree_remove,workbench_copy,import_file_artifact}` | 通常registryのretained `CommandSpec.run`が同一`UseCases` instanceを使用 | Modify in S01 | 357 |
| `presentation/contracts.py::CliText` | shared dispatch、通常 / ChatGPT `CommandOutcome` rendererが使用 | Keep | 357 |
| `application/contracts.py::{FileArtifactImport*,ExplicitFileSourcePreflightRequest,ExplicitFileArtifactPublishRequest}` | `import_file_artifact.py`のrequest / result / error | Keep | 357 |
| `application/ports.py::{ExplicitFileSourceGuard,ExplicitFileArtifactPublisher}` | `import_file_artifact.py`が`Ports`経由で使用 | Keep | 357 |
| `infra/binary_artifact_publisher.py::FilesystemBinaryArtifactPublisher` | opaque byte copy、publication、source guard | Keep | 357 |
| `infra/template_scaffolder.py::copy_scaffolded_tree` | bootstrap scaffolderから`create_node.py`へ到達 | Keep | 357 |
| `infra/{fs_repo,git_cli,github_cli}.py`の上記shared symbol以外のstructural adapters | node / deps / start / finish / closeのretained path | Keep | 357 |
| `application/ports.py::{NodeRepository,IssueGateway,GitGateway,ActiveStateStore,TemplateScaffolder}` | bootstrapの対応adapter assemblyとretained use case | Keep | 357 |
| `tests/cli_runtime/test_authoring.py` | removed通常`authoring` CLI casesと360 authoring-pack direct / compatibility coverageが同居 | Modify in S01 preserving 360 cases | 357 |
| `tests/cli_runtime/test_artifact_import_s04.py`、`tests/unit/application/test_binary_artifact_import_ports.py` | provider Artifact importとretained explicit-file branchのcoverageが同居 | Modify in S07 preserving explicit-file cases | 357 |

### E00 Removed inventory — 到達性遮断後のDelete候補

| path / module | current consumer / reachability | Action | owner |
|---|---|---|---|
| `commands/assurance.py` | parser / registryのassurance四leaf | Delete candidate after S01 removes all four registry keys | 357 |
| `commands/authoring.py` | parser / registryのauthoring 11 leaf | Delete candidate after S01 removes authoring registry keys | 357 |
| `commands/workflow.py` | `guidance` / `workflow_status` | Delete candidate after S01 removes both registry keys | 357 |
| `commands/delegated_authoring.py` | delegated-authoring三leaf | Delete candidate after S01 removes all registry keys | 357 |
| `commands/artifact_import.py::{ArtifactImportChatGptOutputArgs,_add_arguments,_args_factory,_run}` | `command_specs`が生成するprovider-specific `artifact_import_chatgpt_output` keyとbootstrap wiring | Delete candidate after S01 removes key and S07 retains file branch | 357 |
| `application/import_artifact.py::import_artifact` | provider-specific command symbolだけがconsumer | Delete candidate after S01 removes `UseCases.import_artifact` wiring | 357 |
| `application/{assurance,workflow,delegated_authoring}.py` | removed command adapterとbootstrap callback | Delete candidate after S01 removes command and bootstrap consumers | 357 |
| `application/contracts.py::{ShowAssuranceRequest,ClassifyAssuranceRequest,VerifyAssuranceRequest,ComposeAssuranceRequest,WorkflowStatusRequest,WorkflowNextRequest,RunbookProjectionResult,WorkflowResult,ArtifactImportRequest,ArtifactImportResult,ArtifactImportError,UseCases.import_artifact,UseCases.show_assurance,UseCases.classify_assurance,UseCases.verify_assurance,UseCases.compose_assurance,UseCases.workflow_status,UseCases.workflow_next,UseCases.repo_root,UseCases.specdock_dir}` | removed command / delegated-authoring application contract。Runbook / WorkflowStateを含むworkflow result typeを明示 | Delete candidate after S01 removes corresponding adapters and bootstrap wiring | 357 |
| `application/ports.py::{WorkbenchSourceGuard,BinaryArtifactPublisher}` | provider-specific Artifact importだけがconsumer | Delete candidate after S07 removes provider import consumers | 357 |
| `domain/authority.py` | `set_active.py`、`issue_lifecycle.py`、`validate_tree.py`、`active_store.py`にretained consumerあり | Delete candidate after S02/S03/S04/S09 detaches every listed consumer | 357 |
| `domain/{assurance,artifact_composer}.py` | assurance commandとprofile template composer | Delete candidate after S05 removes profile/draft routing | 357 |
| `domain/delegated_authoring.py` | `application/delegated_authoring.py`だけがstatic importし、retained / 360 consumerなし | Delete candidate after S01 removes delegated-authoring command / application | 357 |
| `domain/{runbook,workflow_state}.py`、`infra/runbook_store.py` | `application/workflow.py`、`presentation/workflow.py`、bootstrap `workflow_next` wiringだけがconsumer | Delete candidate after S01 removes workflow command / wiring / contracts | 357 |
| `infra/assurance_store.py`、`infra/artifact_store.py::{ArtifactStore,IssueArtifact}` | bootstrapとprofile design / plan template path | Delete candidate after S05 removes profile template consumer | 357 |
| `presentation/{assurance_text,workflow}.py` | removed assurance / workflow command | Delete candidate after S01 removes rendering consumers | 357 |
| `presentation/cli_text.py::{render_artifact_import_text,render_artifact_import_json,render_artifact_import_error_text,render_artifact_import_error_json}` | removed provider Artifact import branchだけがconsumer | Delete candidate after S01 removes provider key and S07 retains explicit file renderers | 357 |
| `tests/cli_runtime/{test_assurance.py,test_assurance_compose.py,test_delegated_authoring.py,test_workflow.py,test_workflow_context_routing.py,test_artifact_import_chatgpt_output.py}` | removed assurance / delegated / workflow / provider import CLIだけをcover | Delete candidate after S01/S07 absence tests replace assertion role | 357 |
| `tests/unit/application/test_assurance.py`、`tests/unit/domain/{test_assurance.py,test_delegated_authoring.py,test_workflow_state.py}`、`tests/unit/infra/test_assurance_store.py`、`tests/unit/presentation/test_assurance_text.py` | removed assurance / delegated / workflow Runtimeだけをcover | Delete candidate after S01 removes corresponding Runtime | 357 |
| `tests/unit/commands/test_artifact_import_chatgpt_output.py`、`tests/unit/presentation/test_artifact_import_chatgpt_output.py` | removed provider Artifact import branchだけをcover | Delete candidate after S07 retains explicit-file tests | 357 |

### E00 360 handoff keep — Current通常CLIの範囲外

| path / symbol | current consumer / reachability | Action | owner |
|---|---|---|---|
| `app.py`の`main` / `_parse_args` / `_find_specdock_dir` / `_find_repo_root_for_legacy_doctor`以外のlegacy helper symbols | current `main()`から未呼出しだが一部runtime testsがmonkeypatch | Handoff keep | 360 |
| `scripts/spec-dock-chatgpt` | 独立executableから`chatgpt_app.main`へ到達 | Handoff keep | 360 |
| `chatgpt_app.py::main` | `build_registry -> build_parser -> build_runtime -> dispatch` | Handoff keep | 360 |
| `cli/chatgpt_parser.py` module全体 | `build_parser` / `_bind_leaf` / `_required_spec`がplanning create / revise / apply / reviewの四keyをbind | Handoff keep | 360 |
| `cli/chatgpt_registry.py` module全体 | `build_registry`が`commands.issue_planning::command_specs()`だけをregistry化 | Handoff keep | 360 |
| `commands/issue_planning.py` module全体 | Args / factories / runners / outputを含み、ChatGPT registryからshared dispatchと`UseCases.planning_*`へ到達 | Handoff keep | 360 |
| `cli/bootstrap.py::{_IssuePlanningGateway,_planning_node_seed,planning_create,planning_revise,planning_review,planning_apply}`とnested `load_planning_state` | `build_runtime`内でissue-planning dependencies、planning graph、四callbackを構築 | Handoff keep | 360 |
| `application/contracts.py::UseCases.{planning_create,planning_revise,planning_review,planning_apply}` | `commands/issue_planning.py::_run_*`が直接呼出し | Handoff keep | 360 |
| `application/issue_planning.py` module全体 | planning request定義、create / revise / review / apply runner、validation / publication helperの定義元 | Handoff keep | 360 |
| `application/ports.py::{VerifiedIssueCandidateView,PublishedCandidateView,PublishedPlanningReviewView,ExpectedPlanningTargetsView,PlanningApplyOperationView,PlanningApplyExecutionView,IssuePlanningCandidateOutputGuard,IssuePlanningCandidateArchiveRejected,IssuePlanningCandidateBuildFailed,IssuePlanningCandidateCollision,IssuePlanningCandidateOutputRejected,IssuePlanningCandidatePublicationFailed,IssuePlanningApplyOutputRejected,IssuePlanningGateway,IssuePlanningDependencies,Ports.issue_planning}` | bootstrapが構築し`application.issue_planning`がstatic importするplanning専用view / guard / error / gateway / dependencies | Handoff keep | 360 |
| `application/issue_planning_prompt.py` | issue-planning prompt assembly | Handoff keep | 360 |
| `domain/{issue_planning_candidate,issue_planning_contracts}.py` module全体 | candidate material、planning contract validation、`PlanningCommandResult`の定義元 | Handoff keep | 360 |
| `infra/{issue_planning_apply,issue_planning_candidate,issue_planning_chatgpt,issue_planning_oracle_artifact,issue_planning_review}.py` | `_IssuePlanningGateway`とplanning closuresのcandidate / backend / review / apply operation | Handoff keep | 360 |
| `presentation/issue_planning.py` module全体 | planning command outputとreview summary | Handoff keep | 360 |
| `{application,domain,infra,presentation}/authoring_pack/**` | `application/issue_planning.py`がpreflight、authority boundary、ZIP contractをstatic import | Handoff keep | 360 |
| `tests/cli_runtime/test_chatgpt_cli.py`、`tests/{unit,integration}/**/test_issue_planning*.py` | ChatGPT parser / dispatch / UseCases / build_runtimeとissue-planning domain / infra / presentation / E2Eの専用tests | Handoff keep | 360 |
| `tests/unit/authoring_pack/**`、`tests/unit/domain/test_authoring_source_manifest_workbench.py`、`tests/manual_tests/{test_prepare_chatgpt_authoring_pack.py,test_review_chatgpt_authoring_pack.py,test_stage_chatgpt_authoring_pack.py,test_validate_issue_candidates.py}`、`tests/fixtures/authoring_pack/**` | 360 issue-planningがstatic importするauthoring-pack contracts / preflight / ZIP / compatibilityの専用test / fixture | Handoff keep | 360 |
| `scripts/authoring-pack/**` | 通常`spec-dock` parser / registry外のdirect shipped scripts | Handoff keep | 360 |
| `src/spec_dock/assets/install_root/**` managed skills | Runtime外のmanaged distribution surface | Handoff keep | 360 |

### E00 観測コマンド

- parser / registry / bootstrap、command key、wrapper、test / docs consumerを`rg`で逆引きした。
- `git diff --quiet 2c75e0c02cb65a6e74040a72dc161d342d661091..HEAD -- src/spec_dock tests spec-dock/scripts`: pass。
- provider / dogfood Runtime Python treeの`find '*.py' | sort | shasum -a 256` manifest比較: `151 / 151` files、差分なし。
- provider / dogfood `scripts/spec-dock-chatgpt`はSHA-256 `5bdaa7fa06d4d2499294e35436946ba369e99bea2122b8d19b11ce997374f082`で一致した。
- provider / dogfood `scripts/authoring-pack/**`は`13 / 13` files、sorted SHA-256 manifest差分なし。
- `domain.authority`のretained static consumerを`set_active.py`、`issue_lifecycle.py`、`validate_tree.py`、`active_store.py`で確認した。
- `spec-dock-chatgpt -> chatgpt_app.py -> cli/chatgpt_{parser,registry}.py`の通常CLI外到達経路を確認し、360 handoff keepへ一意に分類した。
- workerはrepositoryを変更していない。`No material implementation decisions beyond the approved plan.`

### Step Contract Closure

| step | closure ids | planned close condition | observed evidence | result | notes |
|---|---|---|---|---|---|
| E00 | `CL-357-001/012/013` | retained / removed / shared inventoryの全rowにpath、symbol、consumer、Action、ownerがある | 本reportのE00 inventory、provider / dogfood `151 / 151` manifest一致、baseline差分なし、動的wrapper到達性、retained authority consumer、fresh review passを確認 | M0 commit pending | M0 commit、post-commit clean check後にcloseする |

### Test Contract Closure

| test id | step | evidence level | pre-implementation evidence | verification path | observed result |
|---|---|---|---|---|---|
| `tc-e00-001` | E00 | inspect-only | baselineと現在HEADのRuntime / tests / scripts差分なし | parser / registry / wrapper / import / consumer逆引き、Runtime Python / wrapper / authoring-packのprovider / dogfood比較 | pass: symbol単位で排他的分類、Action / ownerは単一、曖昧rowゼロ、条件未達のDelete候補を明示 |

### Delegated Worker Evidence

| step | delegated role | worker summary | changed files | tests or docs-only verification | reviewer verdict | unresolved risks | integration decision |
|---|---|---|---|---|---|---|---|
| E00 | `repo-analyst` | 初回inventoryを作成し、2回のreview fail後のfollow-upでsymbol単位の排他的分類、shared bridge、単一Action / owner、360 handoff keep、外周parityを確定した | none | read-only `rg` / import / manifest / wrapper / authoring-pack inspection | review 1 / 2 failed; fresh review 3 passed with no findings (0.99) | reviewer確認済みの未解決riskなし | revised evidence adopted; proceed to M0 commit |

### Implementation Delegation Gate

| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | observed result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E00 | delegated | Runtime inventoryの横断read-only分析が必要 | `repo-analyst` | retained / removed / shared inventory | approved `requirement.md` / `design.md` / `plan.md` | read-only repository inspectionとmainによるreport統合 | source / tests / docs / metadata / deps / active / Git mutation | `tc-e00-001` inspect evidence | owner不明、公開surface変更、retained consumerを持つDelete候補 | inventory、path / symbol evidence、risk、next action | pass: source mutationなし、evidence統合済み、fresh review pass |

### Closure Coverage

| closure range | owner steps | planning evidence | implementation evidence | state |
|---|---|---|---|---|
| `CL-357-001` | S01 | E00 baseline registry / import inventory | Current / removed / handoff surfaceを排他的に分類 | baseline evidence only; not closed |
| `CL-357-012` | S10 | E00 provider / dogfood parity inventory | Runtime Python `151 / 151`、wrapper hash、authoring-pack `13 / 13`一致 | baseline evidence only; not closed |
| `CL-357-013` | H91 | E00 owner / destination inventory | 360 handoff keepのpath / symbol / reachability / parity evidence | baseline evidence only; not closed |
| `CL-357-002`〜`011`, `CL-357-014/015` | Planの各owner step | `plan.md`のClosure Index | 該当stepで記録する | not started |

### Closure Delta

| change | closure ids | reason | plan amendment required | re-review required | current result |
|---|---|---|---|---|---|
| none | `CL-357-001`〜`CL-357-015` | E00 inventoryはapproved ownershipとlocked expectationを変更せず、実在到達経路を既存S10 / H91へ割り当てた | no | E00 docs/spec alignment review completed | inventory complete、review pass、M0 commit pending |

### Docs Impact Resolution

| step | target | planned verification | current state |
|---|---|---|---|
| S90 | 357-owned Runtime reference / migration docs | help照合、relative-link scan、fresh spec review | not started |

### Milestone / Commit Candidate Gate

| milestone / step | reviewer verdict | commit candidate / scope | closure state | commit evidence | post-commit clean check |
|---|---|---|---|---|---|
| M0 / E00 | fresh `spec-reviewer` docs/spec alignment pass、findingsなし、confidence 0.99 | `docs(iss-00357): Runtime baseline inventoryを記録` / E00 report evidence | inventory / review complete、commit pending | this M0 commit candidate | run immediately after commit |
| M99 / S99 | not reviewed because execution has not started | `docs(iss-00357): 最終実装証跡を確定` / final report ledger | planned | not created because execution has not started | not run |

## 残余リスクと停止条件

- Runtime削除対象にretained consumerが見つかった場合はE00で停止する。
- `domain.authority`とprofile Artifact経路はretained consumerが残っているため、現時点でDeleteしない。S02 / S04 / S05 / S08 / S09でconsumerを外してからS10で再判定する。
- `spec-dock-chatgpt`、issue-planning Runtime、direct authoring scripts、legacy helperは357では削除せず、360へhandoffする。
- schema v2互換、GitHub partial failure、Artifact path safety、Existing Historical preservationのlocked expectationを変えない。
- Issue 358のtemplate / Guide内容を357から修正しない。IC-1 mismatchはcontentとmechanismへ一意にroutingする。
- PR、merge、Issue close、Epic完了は別workflowであり、本報告では許可・実行しない。

## 次のアクション

M0 commit `docs(iss-00357): Runtime baseline inventoryを記録`を作成し、post-commit clean checkでE00をcloseする。次turnからS01のsource / test implementationへ進む。
