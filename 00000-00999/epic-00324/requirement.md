---

種別: 要件定義書（Epic）
ID: "epic-00324"
タイトル: "Delegation Foundation Asset Inventory and Thin ChatGPT Adapter"
関連GitHub: ["#324"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-20"
親: ["init-00322"]
---

# epic-00324 Delegation Foundation Asset Inventory and Thin ChatGPT Adapter — 要件定義

## 1. 文書の役割とEpic identity

この文書は、`init-00322`が定める7 Epic構成の第1 Epicとして、後続Epicが共用するDelegation Foundationの要求、責務境界、受入条件、互換性、運用条件を定義する。

* Epic ID: `epic-00324`
* normalized node title: `Delegation Foundation Asset Inventory and Thin ChatGPT Adapter`
* canonical long name in parent plan: `Delegation Foundation, Asset Inventory, and Thin ChatGPT Adapter`
* filesystem path: `spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00324-delegation-foundation-asset-inventory-and-thin-chatgpt-adapter`
* GitHub Issue: `#324`
* Parent Initiative: `init-00322` / GitHub Issue `#322`
* Epic dependency: なし
* Delivery Boundary: Issue単位のmerge boundary。各Issueは依存Issueのmerge後に更新済みmainから専用branchを作成し、個別PRのreviewとHuman mergeを完了する。全Issueのmerge確認後にのみEpic completionを反映する。

本書、対応する`design.md`、`plan.md`はPlanning Bundle候補であり、ChatGPTが生成したという事実だけではcanonical authority、reviewer pass、execution-ready、Issue作成承認、PR-ready、merge-ready、Epic completionを成立させない。

## 2. 結論

本Epicは、ChatGPT Delegation-First Workflow vNextの意味仕様を完成させるEpicではなく、後続EpicがPlanning、Review、Execution Brief、Repair、Deliveryの各意味契約を安全に実装できるようにする共通基盤を提供する。

本Epicが提供する能力は次の5群である。

1. Skill、Agent、Workflow、Template、Scriptを横断するmaintained asset inventory。
2. Core `spec-dock` CLIから分離された薄い`spec-dock-chatgpt` application boundaryとcommand skeleton。
3. exact target resolution、GitHub sync preflight、deterministic anchor assembly、tracked-content非添付を保証する決定的処理。
4. operator-configured backend／Oracle invocationと、同一request／result contractを維持するHuman Relay。
5. M-001〜M-013のbaseline／telemetry feasibilityと、M-008 changeability drillを可能にする観測・変更境界。

本Epicは、ChatGPTが生成するPlanning、Review、Execution Brief、Repair Batchの最終的な意味、Prompt本文、動的Concern選択、Artifact lifecycle、Workflow cutoverを実装しない。

## 3. 背景とWhy

現行repositoryには、次の複数surfaceが存在する。

* provider implementation authorityである`src/spec_dock/`
* installed agent-tooling authorityである`src/spec_dock/assets/install_root/`
* shipped workspace／runtime authorityである`src/spec_dock/assets/spec_dock/`
* consumer／dogfood projectionである`spec-dock/`
* current ChatGPT authoring evidence laneである`spec-dock-chatgpt-authoring`
* Core repo-local Runtimeの`spec-dock authoring` command群

この状態で後続Epicが各自の都合でChatGPT integration、Git preflight、Oracle invocation、target resolution、metricsを実装すると、次の問題が生じる。

* PlanningとReviewが別々の外部adapterを持ち、GitHub binding semanticsがずれる。
* provider、installed、dogfoodのどのassetがauthorityか分からなくなる。
* tracked repository contentがGitHubとattachmentの二重SSOTになる。
* Codexが関連Artifactの意味的選択まで担い、REQ-022の責務分離が崩れる。
* Oracleのprivate path、browser profile、特定implementationがSpecDock product dependencyになる。
* adapterやautomationがGit transactionを隠れて実行する危険が生じる。
* M-001〜M-013の比較に必要なbaselineが導入後まで取得されず、継続判断が不可能になる。
* Prompt、backend、model label、output fieldの変更がCore Runtime migrationへ波及する。

本Epicはこれらを先に解消し、Epic 2とEpic 3が同一のfoundation上で並列に実装できる状態を作る。

## 4. Actorとauthority boundary

| Actor / Boundary                   | 本Epicで所有する責務                                                                                                                                  | 本Epicで所有しない責務                                                                            |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Human                              | Issue slice承認、material Scope変更承認、backend利用環境の選択、Human Relay実行、PR merge                                                                        | 日常的なtarget解決、anchor組立、adapter実装                                                          |
| ChatGPT                            | GitHub exact branch／HEADを参照する高深度分析、complete outputの生成                                                                                         | canonical file write、Git transaction、Node作成、自己申告によるadoption／review pass                  |
| Codex Main Orchestrator            | target指定、authority確認、adapter起動、output採否、明示的commit／push、Human Gate、`report.md` disposition                                                     | 関連Artifactの重い意味的選別を標準経路として再実行すること、ChatGPT verdictの捏造                                     |
| `spec-dock-chatgpt`                | deterministic target binding、strict preflight、anchor assembly、外部context policy、backend invocation、transport-level diagnostics、relay package生成 | canonical adoption、semantic review、Brief readiness、commit、push、stash、merge、Node mutation |
| SpecDock Runtime                   | Node metadata、dependency、active scope、validate／sync、決定的file操作、および再利用可能なread-only deterministic service                                        | ChatGPT outputの意味解析、Promptの意味判断、Brief／Review verdictの判定                                  |
| Operator-configured backend／Oracle | browser automation、login、model selection、session、reattach、response／artifact保存                                                                 | repository authority、Git transaction、SpecDock lifecycle gate                             |
| GitHub                             | tracked repository、branch、commit、PR、CIのSSOT                                                                                                   | canonical adoption、Human approval、ChatGPT outputの正しさの判定                                  |
| Executor                           | 後続Epicで定義されるbounded implementationとworking-tree mutation                                                                                      | 本EpicのPlanning候補からの自動開始、Git transaction                                                  |

### 4.1 Evidence authority

次はevidenceであり、それ自体はcanonical authorityを持たない。

* ChatGPT output
* Oracle session output
* Workbench内のrequest／result candidate
* asset inventoryとinventory validation report
* metrics feasibility／baseline record
* live smoke output
* generated anchor manifest
* adapter dry-run output

次がauthorityを持つ。

* Human承認とpromotion条件を満たしたcanonical `requirement.md`、`design.md`、`plan.md`
* Human採用と`report.md` dispositionが確認されたADR
* Node／dependencyに関するSpecDock metadata
* tracked repositoryに関するGitHub exact branch／HEAD
* completion／handoffに関する`report.md`
* mergeに関するHuman decisionとGitHub PR state

## 5. Capability envelope

### 5.1 必須capability

本Epicは次を実現しなければならない。

1. **Delegation asset inventory**

   * Skill、Agent、Workflow、Template、Scriptを列挙する。
   * provider authority path、shipped／installed path、dogfood path、owner、責務、lifecycle分類、verification方法を追跡する。
   * maintained surfaceとcompatibility surfaceを区別する。
   * 本Epicでは旧surfaceを削除しない。

2. **Thin application boundary**

   * `spec-dock-chatgpt`をCore `spec-dock` CLIとは別のrepo-local executableとして提供する。
   * 現行repositoryのlayered architectureに合わせ、CLI、commands、application、domain、infra、presentationを分離する。
   * command treeには少なくとも`execution-brief generate`を含める。
   * Planning、Review、Repairを含む将来command名の予約とhelp skeletonを提供できる。
   * semantic handlerが未実装のcommandは、別経路へfallbackせず明示的な`capability_not_materialized`相当で停止する。

3. **Target and source binding**

   * exact Scope IDまたはexact repo-relative node pathを解決する。
   * repository、branch、expected HEAD、target／parent／dependency pathsを固定する。
   * named branch、clean tree、origin upstream、fetch結果、local HEAD＝remote HEADを検査する。
   * default branch、memory、tracked attachment、local-contextへ黙ってfallbackしない。
   * preflight failure時はremediationを返すだけで、commit、push、stash、checkout、reset、merge、rebaseを行わない。

4. **Deterministic anchor assembly**

   * repository slug、branch、expected HEAD、Scope paths、canonical document paths、Artifact directories、dependency Scope IDs／paths、Execution Unit IDを意味判断なしで組み立てる。
   * ADR、Interview、Discussion、Research、dependency report、code、tests、configurationの関連性をadapterが意味的に選択しない。
   * 同一入力から同一canonical representationとdigestを生成する。

5. **Thin backend／Oracle adapter**

   * operator-configured executable argvをdirect invocationする。
   * shell、private wrapper path、browser profile、cookie storage、特定Oracle implementation selectorをproduct dependencyにしない。
   * backendが返すsession reference、output reference、exit statusをopaque transport resultとして扱う。
   * ChatGPT output本文をRuntime stateへ変換しない。

6. **Human Relay**

   * backend利用不能時も、同一task、binding、anchors、constraints、output contractを保持するrelay packageを生成する。
   * Humanが承認済みUIで実行したcomplete outputをWorkbenchへ戻し、通常のpreservation、EAL disposition、canonical adoption workflowへ再接続できる。
   * Human RelayをCodex-only semantic fallbackへ読み替えない。

7. **Workflow documentation**

   * `workflow_chatgpt_delegation.md`にauthority、normal path、failure path、Human Relay、no-hidden-Git、security、evidence handlingを記述する。
   * existing `workflow_chatgpt_authoring_pack.md`との併存境界を示す。
   * global cutoverや旧surface削除を宣言しない。

8. **Metrics foundation**

   * M-001〜M-013ごとにdirect telemetry、proxy、deferred measurement、unavailableを分類する。
   * source、unit、collector、sample boundary、privacy、limitations、downstream ownerを記録する。
   * 利用可能なhistorical evidenceから旧Workflowのbaselineを採取する。
   * Prompt、backend command、model label、output fieldの変更容易性をM-008で計測できる契約を定義する。

### 5.2 Capability boundary

本Epicのoutputは、後続Epicが意味契約をplug inできるfoundationである。次は本Epicに含めない。

* final Architecture-Aware Execution Brief Prompt
* dynamic Applicable Concern selection
* `ready | planning-gap | insufficient-evidence`の最終意味とrouting
* Workbench candidateからIssue ArtifactへのBrief adoption／freeze
* Integrated Planning Bundleの正式cutover
* Formal／Targeted Review Protocol
* Repair Batch semantics
* full Issue Executionとcustom Executor integration
* Epic Delivery Topology、PR Delivery、Human merge後finish
* global legacy surface removal
* Initiative-wide comparative evaluationとfinal closure
* automatic canonical adoption
* automatic Issue／Epic Node creation
* semantic state database、Brief registry、accepted HEAD registry
* Oracle session管理やbrowser automationの再実装
* 特定model label、thinking label、private wrapper locationの固定

## 6. Epic requirements

| ID       | 要件                                                                                                                     | Parent trace                                                                  | 観測可能な成果                                                                                                    |
| -------- | ---------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| E-RQ-001 | Human、ChatGPT、Main、`spec-dock-chatgpt`、Runtime、backendの責務を分離し、ChatGPT outputやinventoryの自己申告だけでauthorityを成立させない。        | REQ-001。主実装責任: AC-002。共同証拠: AC-001、AC-003。M-004、M-005。                        | authority表、result envelope、workflow doc、negative testsで責務越境がない。                                            |
| E-RQ-002 | Skill／Agent／Workflow／Template／Scriptのmaintained inventoryを、provider／installed／dogfood pathとownerを含めて維持できる。             | REQ-018。共同実装／証拠: AC-016、AC-018。M-003、M-005、M-006、M-008。                       | versioned inventory、coverage validation、path existence／projection parity evidenceがある。                      |
| E-RQ-003 | Core `spec-dock`から分離した薄い`spec-dock-chatgpt` application boundaryと、`execution-brief generate`を含むcommand skeletonを提供する。  | REQ-004、REQ-005。主実装責任: AC-004。共同証拠: AC-003、AC-021。M-007、M-008。                | separate executable、help tree、dry-run request contract、未materialize capabilityのfail-closed resultがある。      |
| E-RQ-004 | Formal delegation requestをexact repository、named branch、expected HEAD、target Scopeへbindし、GitHub syncをfail closedで検査する。 | REQ-004、REQ-005。主実装責任: AC-004。M-004、M-007。                                    | synced temp-repo tests、mismatch／dirty／detached／missing upstream tests、exact branch／HEAD live smokeがある。     |
| E-RQ-005 | Codex／adapterが提示するcontextをdeterministic anchorsへ限定し、関連Artifactの意味的探索をChatGPTへ残す。                                       | REQ-022。共同実装／証拠: AC-019、AC-023。M-002、M-009、M-011、M-012。                       | stable anchor manifestとdigestが生成され、semantic artifact selectorが存在しない。                                       |
| E-RQ-006 | backend／Oracle invocationをoperator-configuredなthin portとし、特定implementation、browser profile、private pathへ依存しない。         | REQ-004、REQ-005。主実装責任: AC-004。M-007、M-008、M-013。                              | direct argv spy、config resolution、timeout／spawn failure、redaction testsがある。                                |
| E-RQ-007 | backend障害時に、bindingとoutput contractを変えないHuman Relayを提供する。                                                              | REQ-005。共同実装／証拠: AC-018、AC-023。M-001、M-007、M-013。                             | relay package digest、manual round-trip smoke、通常adoption laneへのre-entry guidanceがある。                        |
| E-RQ-008 | `spec-dock-chatgpt`とそのautomationはhidden Git transactionを行わず、Git preflight failureを自動修復しない。                             | REQ-001、REQ-004、REQ-005。主実装責任: AC-009。M-004、M-005。                            | subprocess argv spy、HEAD／index／worktree before-after test、forbidden Git command absence testがある。           |
| E-RQ-009 | provider、shipped consumer、dogfoodの新foundation surfaceを整合させ、current authoring laneを壊さず追加導入する。                           | REQ-018。共同実装／証拠: AC-001、AC-003、AC-016、AC-018、AC-021。M-005、M-006、M-007。        | installer init／update test、provider-dogfood parity、current authoring regressionがある。                        |
| E-RQ-010 | M-001〜M-013のbaseline／telemetry feasibilityを定義し、取得可能な旧Workflow baselineを保存する。                                           | REQ-018。REQ-025を支援するがfinal verificationはEpic 7が所有する。共同証拠: AC-025。M-001〜M-013。 | metric feasibility matrix、historical baseline record、unavailable／deferred理由、downstream ownerがある。           |
| E-RQ-011 | target、preflight、transport、output、relayのfailureを区別し、retry、idempotency、observability、securityを一貫して扱う。                   | REQ-004、REQ-005。主実装責任: AC-004、AC-009。M-007、M-008、M-013。                       | stable symbolic status、bounded diagnostics、retry policy、secret/path redaction、duplicate invocation防止契約がある。 |
| E-RQ-012 | Epic 1の各Issueを独立したbranch／PR／review／Human merge boundaryとして扱い、依存Issueは先行PRがmainへmergeされた後に開始する。                 | HumanによるEpic 1 Delivery Topology変更。ADR-07のPlan-driven Delivery原則をIssue単位へ具体化する。 | Issueごとのbase main SHA、branch、PR、review、merged SHAが追跡され、未mergeの依存成果を暗黙に継承しない。 |

## 7. 利用シナリオ

### 7.1 正常系

#### SC-N01: exact targetのdry-run

1. Mainがexact Issue IDとExecution Unit IDを`execution-brief generate`へ渡す。
2. adapterが`.meta.json`とdependency metadataからtarget、parent、dependencyを決定的に解決する。
3. strict GitHub sync preflightがnamed branch、clean tree、upstream、local／remote HEAD一致を確認する。
4. adapterがdeterministic anchor manifestとdigestを生成する。
5. `--dry-run`ではbackendを起動せず、evidence-only request envelopeを返す。
6. final Brief Prompt、Concern selection、Brief statusは生成しない。

#### SC-N02: operator-configured backend invocation

1. operatorがbackend commandをCLI optionまたはapproved environment configurationで指定する。
2. adapterがshellを介さずdirect argvでbackendを起動する。
3. backendがbrowser、login、model、session、artifact handlingを所有する。
4. adapterはtransport status、session／output reference、bounded diagnosticsだけを返す。
5. returned contentはevidenceとして扱われ、canonical adoptionはMainとdownstream workflowへ戻る。

#### SC-N03: inventory確認

1. maintainerがinventory validationを実行する。
2. validatorがprovider authority paths、shipped paths、installed paths、dogfood pathsの存在と分類を確認する。
3. maintained assetの未登録、duplicate logical ID、invalid owner、missing projectionを報告する。
4. validatorはassetを削除、rename、rewriteしない。

### 7.2 Failure scenarios

#### SC-F01: dirtyまたはdetached repository

* preflightは`preflight_blocked`として停止する。
* adapterはstash、checkout、commit、reset、cleanを実行しない。
* Main／operatorがremediationを明示的に実行した後、同一commandを再実行する。

#### SC-F02: local／remote HEAD mismatch

* ahead、behind、diverged、unresolved remote HEADを区別する。
* default branchへfallbackしない。
* staleまたはblockedとして停止し、expected HEADを推測しない。

#### SC-F03: target missing／ambiguous

* fuzzy title matchを使用しない。
* exact IDまたはexact repo-relative pathが一意に解決できなければ停止する。
* active Scopeや同名Nodeへ黙ってfallbackしない。

#### SC-F04: forbidden attachment

* Git-tracked file、`.env*`、credential-like path、symlink、path traversal、unsupported directoryを拒否する。
* tracked contentはGitHub exact HEADから参照させ、添付へコピーしない。

#### SC-F05: backend spawn／timeout／nonzero

* canonical docs、Node、Git stateを変更しない。
* transport failureをsemantic failureとして解釈しない。
* retryable条件とoperator recovery条件を示す。
* automatic duplicate invocationを行わない。

#### SC-F06: semantic capability未materialize

* Epic 2〜Epic 5が所有するsemantic handlerが存在しないcommandは、`capability_not_materialized`相当で停止する。
* current authoring lane、manual semantic analysis、default Promptへfallbackしない。

### 7.3 Recovery scenarios

#### SC-R01: preflight recovery

* operatorがremote configuration、authentication、repository stateを修正する。
* adapterは同じtargetとcommand contractでpreflightを再実行する。
* 新しいobserved HEADが以前のexpected HEADと異なる場合、新しいrequest bindingを明示的に作り直す。

#### SC-R02: Human Relay

1. adapterがrequest body、binding、anchor digest、constraints、output contract、external file digestsを含むrelay packageを生成する。
2. Humanがapproved ChatGPT UIまたはapproved browser routeで同じtaskを実行する。
3. ChatGPTがGitHub exact repository／branch／HEADを確認できなければ回答を継続しない。
4. Humanがcomplete outputをWorkbenchへ配置する。
5. Mainがpreservation checkpoint、EAL disposition、canonical adoption、fresh reviewer gateへ戻す。
6. relay packageやoutputはcompletionを自己申告しない。

### 7.4 Operator scenarios

#### SC-O01: backend configuration変更

* operatorはprivate absolute pathやbackend-specific fixed argumentsを自分のconfigに置く。
* SpecDock assetsにはprivate path、profile、cookie、account dataを保存しない。
* backend commandの変更はadapter core migrationを要求しない。

#### SC-O02: baseline採取

* operator／Mainが利用可能な旧Workflow evidenceを選ぶ。
* metric collectorがM-001〜M-013の取得可否と値を記録する。
* 値を取得できない指標は推測せず、proxy、deferred measurement、unavailableのいずれかと理由を記録する。
* qualityとresource／latencyを同一の単一scoreへ潰さない。

## 8. Epic acceptance criteria

| ID       | 前提                                                                                | 操作                                                                                                                            | 期待結果                                                                                                                                                                                                          | 観測点とParent trace                                                                                                                   |
| -------- | --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| E-AC-001 | provider、installed、dogfoodのasset treeが存在する。                                       | inventoryを生成または検証する。                                                                                                          | Skill／Agent／Workflow／Template／Scriptの各maintained assetが一意なlogical ID、authority path、projection path、owner、lifecycle、verification modeを持つ。未登録assetとmissing pathは失敗になる。旧surfaceは削除されない。                         | inventory file、coverage report、path tests。E-RQ-002、E-RQ-009。REQ-018。AC-016／AC-018共同証拠。M-003、M-005、M-006。                           |
| E-AC-002 | cleanなinitialized consumer repositoryがある。                                         | `spec-dock-chatgpt --help`およびsubcommand helpを実行する。                                                                            | Core `spec-dock`とは別のexecutableとして起動し、Planning／Review／Execution Brief／Repairのreserved command groupsと`execution-brief generate`を表示する。semantic未実装commandは明示的に停止し、authorityやreadinessを主張しない。                     | CLI help tests、result envelope assertions。E-RQ-001、E-RQ-003。REQ-001、REQ-004。AC-002、AC-004。M-007、M-008。                             |
| E-AC-003 | named branch、origin upstream、clean tree、remote-visible commitがある。                 | strict preflightを実行し、次にdirty、detached、ahead、behind、diverged、missing upstreamを個別に再現する。                                         | 正常時だけexact repository／branch／HEAD bindingを返す。各異常時はblockedまたはstaleになり、default branch、local-context、tracked attachmentへfallbackせずremediationを返す。                                                                | hermetic Git tests、CLI JSON、exact HEAD fields。E-RQ-004、E-RQ-011。REQ-004、REQ-005。AC-004。M-004、M-007。                                |
| E-AC-004 | exact Scope ID、dependency metadata、optional Execution Unit IDがある。                 | anchor assemblyを同一入力で複数回実行する。                                                                                                 | 同一ordered anchor setとdigestを返し、repository、branch、HEAD、Scope／canonical／artifact／dependency paths、Unit ID以外のsemantic artifact選択を含まない。                                                                           | golden fixture、digest stability test、negative selector search。E-RQ-005。REQ-022。AC-019／AC-023共同証拠。M-002、M-009、M-011、M-012。          |
| E-AC-005 | operator-configured backend stubと、private backend detailsを含まないpublic contractがある。 | normal、missing executable、timeout、nonzero exitを実行する。                                                                          | shellを使用せずdirect argvで呼び出し、backend選択、browser、model、session internalsをoperator側へ残す。failureをtyped transport resultへ分類し、secret／absolute host pathをredactする。                                                      | subprocess spy、timeout test、redaction test。E-RQ-006、E-RQ-011。REQ-004、REQ-005。AC-004。M-007、M-008、M-013。                             |
| E-AC-006 | backend routeが利用不能で、同一request bindingが保持されている。                                    | relay packageを生成し、approved UIを使ったround-trip smokeを行う。                                                                         | relay packageとnormal backend routeが同じtask／binding／anchors／constraints／output contractを共有し、complete outputを通常のevidence adoption laneへ戻せる。Codex-only semantic fallbackは発生しない。                                   | relay manifest digest、manual smoke record、workflow doc。E-RQ-007。REQ-005。AC-018／AC-023共同証拠。M-001、M-007、M-013。                       |
| E-AC-007 | adapterの全subprocess境界をspyできる。                                                     | normal、blocked、transport failure、relay生成を実行する。                                                                                | commit、push、stash、checkout、switch、reset、clean、merge、rebase、cherry-pick、revert、tag、update-ref、force操作が実行されない。HEAD、local branch、index、worktree contentが不変であり、明示preflight fetchによるremote-tracking ref観測だけが許容される。 | argv allowlist／denylist、repository before-after snapshot。E-RQ-008。REQ-001、REQ-004、REQ-005。AC-009。M-004、M-005。                      |
| E-AC-008 | adapter output、inventory、smoke resultが存在する。                                       | output metadataとworkflow guidanceを検査する。                                                                                       | `authority=evidence_only`相当、`canonical_written=false`、`git_transaction_performed=false`を示し、adoption、reviewer pass、execution-ready、PR-ready、merge-ready、completionを自己申告しない。                                    | contract tests、forbidden-claim tests、docs review。E-RQ-001、E-RQ-003、E-RQ-007。REQ-001。AC-002、AC-003共同証拠。M-004、M-005。                 |
| E-AC-009 | provider assetから新規consumer init／updateを実行できる。                                     | temp repositoryへinit／updateし、dogfood projectionとcurrent authoring laneを検査する。                                                  | new executable、package、inventory、workflow docがinstallされ、provider sourceとの期待parityを持つ。current `spec-dock authoring`と`spec-dock-chatgpt-authoring`は引き続き利用可能で、旧surface削除やglobal cutoverは発生しない。                   | installer tests、provider-dogfood diff、existing authoring regression。E-RQ-002、E-RQ-009。REQ-018。AC-016／AC-018共同証拠。M-005、M-006、M-007。 |
| E-AC-010 | parent InitiativeのM-001〜M-013定義と利用可能なhistorical evidenceがある。                      | metric feasibility matrixとbaseline recordを作成する。                                                                               | 全13 metricがsource、unit、collector、availability、limitations、downstream ownerを持つ。3件以上の適格historical runが存在する場合は3件以上を記録し、存在しない場合は全件と不足理由を記録する。未観測値を捏造しない。                                                          | metrics schema、baseline artifact、coverage assertion。E-RQ-010。REQ-018。AC-025共同証拠。M-001〜M-013。                                       |
| E-AC-011 | Prompt resource、backend config、output fixtureを交換できるfoundation designがある。          | M-008 changeability rehearsalを設計し、代表変更をtest fixture上で試す。                                                                      | Prompt、backend command／model label、output field変更が局所resource／adapter testの変更で済み、Core Runtime semantic migration、新state DB、canonical schema migrationを要求しないことを測定できる。                                           | changed-file set、test set、migration absence assertion。E-RQ-002、E-RQ-003、E-RQ-006、E-RQ-010。REQ-018。M-008。                           |
| E-AC-012 | Epic実装Issueの各PRがmainへ統合され、final quality Issueの専用branchがremote-visibleである。 | final quality laneでfull tests、current branch／HEAD GitHub connector smoke、Human Relay smoke、rollback-by-revert rehearsalを実行する。 | smokeが実行時のexact repository／branch／HEADを一致確認し、不一致やconnector access failureでfail closedになる。rollback後もcurrent Core Runtimeとauthoring laneが動作し、新semantic stateが残らない。 | full test summary、observed SHA、smoke output、rollback evidence。E-RQ-003〜E-RQ-012。AC-004、AC-009、AC-018共同証拠。M-006、M-007、M-008、M-013。 |
| E-AC-013 | Human承認済みIssue Nodeとdependency graphがある。 | 各Issueについて、全依存Issueのmerged SHAを含むthen-current mainから専用branchを作成し、実装・検証・PR reviewを行い、Humanがmergeする。 | Issueごとに1 PRが存在し、blocking review／CI解消後にmergeされる。次の依存Issueは更新済みmainから開始する。並列Issueのbaseが古くなった場合はmainへ追随してaffected checks／reviewを更新する。 | Issue report、base SHA、branch、PR URL、review／CI evidence、merged SHA。E-RQ-012。 |

## 9. 非機能要件

### 9.1 変更容易性

* Oracle／backend、Prompt resource、task output contract、model labelを別々に交換できる。
* `spec-dock-chatgpt`のOracle dependencyをinfra portへ閉じ込める。
* Core `spec-dock` RuntimeはChatGPT outputの意味をparseしない。
* inventoryとmetrics schemaはversioned static assetであり、Workflow state databaseとして扱わない。
* 後続Epicがsemantic handlerを追加してもroot command、binding、anchor、transport contractを再設計しない。
* M-008で変更file数、変更layer、必要test、migration有無を観測できる。

### 9.2 信頼性と一貫性

* preflightとanchor dry-runは同一入力に対してdeterministicである。
* repository snapshot中にHEAD、worktree、source pathが変わった場合は`concurrent_repo_change`相当で停止する。
* backend invocationは非冪等な外部処理として扱い、session／output discoveryを確認せず自動重複実行しない。
* relay packageは同一requestから同一content digestを生成する。
* transport failure、binding stale、unsafe input、semantic capability未materializeを別状態として扱う。

### 9.3 Git安全性

* adapterはcommit、push、stash、force、mergeを行わない。
* adapterはindex、working tree、local branch、local HEADを変更しない。
* explicit preflight fetchはremote-tracking ref観測のための公開された操作としてのみ許可する。
* fetch failureを権限変更、shell wrapper、agent-owned raw fetch、automatic retry escalationで補わない。
* Mainだけがreviewed transitionで明示的commit／pushを行い、Humanだけがmergeする。

### 9.4 セキュリティと秘密

* secret、token、cookie、browser profile、private key、`.env*`、production dumpをPrompt、inventory、metrics artifact、relay packageへ含めない。
* direct argvを使用し、`shell=True`、pipe、redirect、command substitutionを使用しない。
* external fileは明示指定、regular file、non-symlink、non-secret-like、Git-untrackedまたはrepository外でなければならない。
* stdout／stderr、argv、path、environment由来のdiagnosticsをboundedかつredactedにする。
* backend configのprivate absolute pathをdurable outputへ保存しない。

### 9.5 観測性

* textとJSONの両方で、operation、status、target ID、repo、branch、expected／observed HEAD、anchor digest、blockers、remediation、backend source class、duration、relay digest、authority boundaryを観測できる。
* raw ChatGPT transcriptやsecret-like valuesを標準diagnosticへ含めない。
* M-001〜M-013の収集可否を機械的にcoverage確認できる。
* ChatGPT latencyをadapter／backend／Human Relayで区分して記録できる。

### 9.6 性能とresource

* adapterは関連Artifactの意味的探索やrepository全体のcontent要約を行わない。
* target resolutionはNode metadata、dependency metadata、固定path conventionを対象とする。
* anchor assemblyは対象Scopeとdependency数に比例する決定的処理とする。
* external backend latencyに固定SLOを設けず、M-013のwall-clock evidenceとして記録する。
* token telemetryが安定して取得できない場合はtool call、探索回数、handoff byte数、failure cycleをproxyとして扱う。

### 9.7 互換性

* Initiative／Epic／Issue ID、`.meta.json`、canonical file名、dependency metadataを変更しない。
* current `spec-dock` CLIのcommand contractを壊さない。
* current `spec-dock authoring` laneと`spec-dock-chatgpt-authoring` Skillを削除しない。
* existing open／closed Scope文書を移行しない。
* top-level fourth canonical documentを追加しない。
* Python 3.10+とstdlib-firstの現行project constraintを維持する。
* new executableは`spec-dock init`／`update`でmanaged assetとして配布する。
* rollbackはGit revertで行え、新しいdata migrationやsemantic state cleanupを必要としない。

### 9.8 Issue単位Delivery Topology

* Epic全体を一つのdelivery branch／PRへ集約しない。
* 各Issueは、依存IssueのPRがHumanによりmainへmergeされ、そのmerged SHAを確認した後、then-current mainから専用feature branchを作成する。
* 各Issueは独立したPRを作成し、required checks、code／spec／QA reviewのうちIssue契約で必要なgateを通過してからHuman mergeへ進む。
* mergeされていない先行Issueのbranchを次Issueのbaseとして使用しない。
* 並列可能なIssueは同じthen-current mainから開始できる。ただし一方のmergeでbaseが進んだ場合、後続merge前に最新mainを取り込み、影響する検証とreview freshnessを再確認する。
* final quality Issueも独立したbranch／PRを持つ。役割は全merged成果の統合確認とbounded repairであり、先行Issueの未merge差分を一括配送することではない。
* Epic completionは全Issue PRのmerge、merged HEADの確認、Epic-level closure確認後にのみ成立する。

## 10. 外部依存

| Dependency                             | 用途                                          | Failure時の扱い                                                             |
| -------------------------------------- | ------------------------------------------- | ----------------------------------------------------------------------- |
| Git executableとorigin remote           | branch／HEAD／worktree／upstreamの観測、明示fetch    | fail closed。自動修復やdefault fallbackを行わない。                                 |
| GitHub remoteとChatGPT側GitHub connector | tracked repositoryのexact branch／HEAD参照      | Formal delegationを停止する。Human Relayでも同じbinding requirementを維持する。         |
| Operator-configured backend／Oracle     | browser、login、model、session、output保存        | recoverまたはHuman Relayへ進む。private implementationをproduct dependencyにしない。 |
| ChatGPT account／approved UI            | cognitive processing                        | unavailable時は未実行として扱い、Codex-only semantic substituteを標準化しない。            |
| SpecDock installer／repo-local Runtime  | managed asset配布、Node metadata、validate／sync | current contractを保持し、semantic ChatGPT processingをCore Runtimeへ移さない。     |

## 11. 後続Epicへのhandoff

### Epic 2へ渡すもの

* separate `spec-dock-chatgpt` command boundary
* exact target／branch／HEAD binding
* deterministic anchor contract
* operator backend port
* Human Relay
* Planning routeで利用可能なmetrics hooks
* authority／no-hidden-Git invariants

Epic 2へ渡さないもの:

* complete Planning Bundle Prompt
* Planning create／reviseのsemantic output contract
* canonical placement／review loop
* Human decomposition gate implementation

### Epic 3へ渡すもの

* same binding／anchor／transport foundation
* BASEを将来追加できるpreflight extension seam
* transport and diagnostics contract
* Review routeで利用可能なmetrics hooks

Epic 3へ渡さないもの:

* Formal Review Protocol
* Perspective catalog
* P0／P1、P2／P3、insufficient evidence semantics
* Targeted Review result contract

### Epic 4へ渡す共同証拠

* `execution-brief generate` command skeleton
* exact Issue／Unit anchor fields
* exact HEAD smoke evidence
* no semantic Artifact selection invariant
* backend／Human Relay foundation
* baseline／telemetry schema

Epic 4へ渡さないもの:

* final Execution Brief Prompt
* dynamic Concern selection
* `ready | planning-gap | insufficient-evidence`
* candidate adoption／freeze
* Executor handoff／same-commit lifecycle

### Epic 6／Epic 7へのhandoff

* asset inventory baseline
* compatibility surface classification
* provider／installed／dogfood projection evidence
* M-001〜M-013 feasibility matrix
* M-008 changeability measurement design
* exact branch／HEAD smoke evidence
* no-hidden-Git evidence
* residual risksとunavailable telemetry

Epic 1はAC-001〜AC-025のInitiative-level final verificationやclosureを所有しない。

## 12. 未確定事項

Scope、non-scope、E-RQ、E-ACに関する未確定事項はない。

次はIssue planningへ意図的に委譲するreplaceable implementation detailであり、本Epicのacceptance boundaryを変更してはならない。

* Python module／class／functionの細分化
* numeric exit codeの割当
* argparse helperの具体名
* current preflight implementationからの抽出単位
* backend timeoutとbounded retryの具体値
* relay packageの非意味的file naming
* baseline evidence artifactのtimestamped filename
* individual test file名
* later Epicが登録するPrompt resource名とsemantic output field
