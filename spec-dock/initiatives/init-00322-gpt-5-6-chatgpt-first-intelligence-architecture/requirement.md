# init-00322 GPT 56 ChatGPT First Intelligence Architecture — 要件定義

## 1. 文書の役割と識別互換性

この文書は、SpecDockのPlanning、Review、Repair、Execution、PR DeliveryをChatGPT Delegation-Firstな構造へ移行するInitiativeの戦略目的、必須能力、非交渉制約、成功条件を定義する。

- Initiative ID: `init-00322`
- 既存filesystem path: `spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture`
- GitHub Issue: `#322`
- repository上の正式タイトル: `GPT 56 ChatGPT First Intelligence Architecture`
- 本Initiative内のvNext program label: `ChatGPT 5.6 Pro Delegation-First Workflow vNext`

### 1.1 タイトル互換性

本改訂では、既存`.meta.json`およびGitHub Issue #322との互換性を優先し、文書タイトルをrepository上の正式タイトルへ合わせる。`ChatGPT 5.6 Pro Delegation-First Workflow vNext`は、対象アーキテクチャとroadmapを識別するprogram labelとして本文内で使用する。

本改訂は`.meta.json`、GitHub Issue、Initiative pathを変更しない。将来タイトルを同期する場合は、Humanの明示判断とSpecDockの管理操作による別の変更として扱い、本Planning Bundleの採用条件にはしない。

### 1.2 文書と証跡のauthority

- `requirement.md`、`design.md`、`plan.md`は、HumanとMain Orchestratorによる採用、および現行SpecDockのreview／promotion手続を経た後にcanonical authorityとなる。
- 同梱またはrepository上のADR、Interview、Discussion、Research、self-reviewは、判断根拠を提供するevidenceである。
- Evidence file内の`状態: accepted`、`authority: accepted`、`user-approved`等の自己申告だけでは、repository上の有効な採用を成立させない。
- ADRを含むevidenceの有効な採用状態は、Humanの明示判断とMain Orchestratorが管理する`report.md`のdispositionによって確定する。
- 本改訂は`report.md`を生成・置換せず、reviewer pass、canonical adoption、execution-ready、PR-ready、merge-ready、Initiative完了、Epic完了を主張しない。

## 2. 目的とWhy now

### 2.1 主目的

SpecDockの高度認知処理をChatGPTへ、repository mutationとWorkflow制御をCodexへ、構造的・決定的な処理をSpecDock Runtimeへ分離し、Human Gateを維持したまま、Planningからmerge確認までを一貫したvNext Workflowとして自動化する。

### 2.2 Why now: GPT-5.5前提からGPT-5.6／ChatGPT Firstへの転換

現行Workflowの主要部分は、GPT-5.5世代のモデル能力と運用上の不確実性を前提に設計されている。そのため、Requirement／Design／Planを段階的に生成し、ChatGPT出力を低authority evidenceとして保存し、Codexがclaimを採否してcanonical文書を再構成し、複数のローカルReviewer Agentとmanual fallbackで品質を補う構造になっている。

Humanは、GPT-5.6 ProをPlanning、Formal Review、Repair設計、高深度分析へ利用するChatGPT First方針を明示的に採用した。この前提では、旧構造を維持するほど次の費用が累積する。

1. 同じ意味をChatGPT、Codex、ledger、reviewerで再生成する二重authoring。
2. Main Orchestratorへ長い調査・review履歴を戻すことによるcontext圧迫。
3. ローカルReviewer／Writer／manual planning経路によるCodex quota消費。
4. Oracle、model、Promptの変更に追従するための複数surface改修。
5. 新しいWorkflowやArtifactを旧authority modelへ追加することによる移行負債。

Workbenchは既に導入済みであり、既存Initiative `init-00322`とGitHub Issue #322も存在する。今の段階でActorとWorkflowの境界を切り替えることで、今後の機能を旧Evidence Laneへ積み増す前に、Planning、Review、Repair、Deliveryの基盤を単純化できる。

### 2.3 副目的

- Codex Main Orchestratorの長寿命contextを、詳細調査、実装、Review transcriptから保護する。
- 旧ChatGPT authoring evidence lane、manual planning fallback、ローカルReviewer Agent、巨大Evidence Ledger、過剰なreceipt／registry／state machineを廃止する。
- ChatGPT、Oracle、Codexの将来変更に追従しやすい薄い境界を作る。
- Issue単位または適切なbatch単位でmerge可能なPRを作りやすくし、巨大なEpic-wide PRによる品質ゲート負荷を抑える。
- 日本語ファーストの仕様・文書規約をFormal Reviewで継続的に検証する。

### 2.4 利用者価値・運用価値

- HumanはGoal、Scope分割、materialな価値判断、PR merge判断へ集中できる。
- Main OrchestratorはWorkflow判断、authority、Git transaction、Human Gateへ集中できる。
- ExecutorはPlanning済みのExecution TrancheまたはRepair Batchへ集中できる。
- Reviewの対象、時間範囲、Perspective、判定規則を再現可能にできる。
- Oracle障害時も、処理契約を変えずに別browser経路またはHuman Relayで継続できる。

## 3. スコープと境界

### 3.1 必須スコープ

- ChatGPT、Main Orchestrator、Executor、SpecDock Runtime、Humanの責務とauthorityの再定義。
- Initiative／Epic／Issue PlanningのIntegrated Planning Bundle化。
- Planning、Checkpoint、DeliveryのFormal Review ProtocolとTargeted Review。
- accepted blockerを処理するRepair Batch。
- Executor中心のIssue Execution、Plan-driven Delivery Topology、PR Delivery、Human Merge Gate。
- `spec-dock-chatgpt`による薄いOracle／GitHub連携境界。
- Workbench、Oracle session、Git／GitHub、`report.md`のauthority分離。
- provider、installed、dogfood surfaceの同一責務への整合。
- 既存Scope文書を一括変換しないglobal Workflow cutover。
- 代表WorkflowによるdogfoodとInitiative-level final quality。

### 3.2 禁止事項

- ChatGPT、`spec-dock-chatgpt`、Executor、Runtimeによる隠れたcommit、push、stash、force、merge。
- Humanの明示判断を伴わないInitiative作成、Epic／Issue分割、material Scope変更、PR merge。
- `plan.md`、Review JSON、Repair BatchをRuntimeが意味解析してgate判定すること。
- tracked repository fileをFormal ChatGPT処理へ自動添付してGitHubと二重SSOTにすること。
- Review receipt、Planning state、accepted HEAD registry、Checkpoint DB、Repair iteration DB等の新しいWorkflow databaseを導入すること。
- 旧WorkflowとvNextをScope作成日やversionで長期並行運用すること。

### 3.3 Non-goals

- 既存Scope文書の一括変換または全open Scopeの事前refresh。
- closed／finished Scopeの書き換え。
- 自動merge、auto-merge有効化、Human Merge Gateの削除。
- GitHub上のCodex PR Reviewの即時廃止。
- 汎用`chatgpt-use` Skillの再実装。
- Oracle session／artifact保存機構の再実装。
- Prompt wording、model label、JSONの任意fieldを長期固定すること。
- 全既存Discussion／Report／ADRを新形式へ移行すること。
- 本改訂作業で`.meta.json`、GitHub Issue、`report.md`、Epic Nodeを変更すること。

## 4. ステークホルダーとauthority

| Actor | Initiative-level responsibility | 明示的に所有しないもの |
|---|---|---|
| Human | Initiative Goal、Epic／Issue分割承認、material Scope変更、PR merge、evidence／ADRの最終採用判断 | 日常的なfile mutation、Reviewの逐次実行 |
| ChatGPT | Integrated Planning、Formal／Targeted Review、Repair Batch、高深度分析 | canonical filesystem配置、Git transaction、Node mutation、merge、自己申告だけによるauthority確定 |
| Codex Main Orchestrator | Workflow、target、authority、ChatGPT出力の採否、Executor、Git transaction、Human Gate、`report.md` disposition | 長時間の詳細実装、Review verdictの捏造 |
| Executor | Execution Tranche／Repair Batch内の調査、実装、verification、working tree mutation | commit、push、Plan変更、Scope拡大、Formal Gate |
| SpecDock Runtime | Node、dependency、active scope、validate／sync、Workbench、決定的file／metadata操作 | LLM文書、Review JSON、Repair Batchの意味解析 |
| GitHub／Oracle | tracked repository、PR／CI／Codex Review、ChatGPT browser session／artifact | Planning／Review Contractの意味判断、Human adoption |

## 5. 必須能力

| ID | 能力要件 | 受入証拠の種類 |
|---|---|---|
| REQ-001 | 全WorkflowでHuman、ChatGPT、Main Orchestrator、Executor、SpecDock Runtimeの責務とauthorityを一貫して分離し、Goal、分割、material変更、mergeのHuman Gateを維持する。 | Workflow文書、Skill、Agent設定、E2E |
| REQ-002 | Initiative／Epic／IssueのRequirement、Design、Planを、一つのfresh ChatGPT sessionで相互整合した完全Bundleとして生成し、内部セルフレビューを含める。 | Planning dogfood、成果物比較 |
| REQ-003 | Scope別Planning Skillが、Bundle配置、独立Review、P0／P1解消、Human分割承認、Node／dependency handoffまでを導き、子Scopeの詳細PlanningはJITで行う。 | Planning Skill、Node materialization test |
| REQ-004 | ChatGPT連携をCore Runtimeから分離した薄いapplication boundaryとし、Formal処理をGitHub上のexact repository、branch、HEADへfail closedでbindする。 | adapter test、live smoke |
| REQ-005 | tracked repository contentはGitHubをSSOTとし、Operator ContextとGitHub外資料だけを明示的に補足する。Oracle障害時も同じtask／result contractを維持する。 | context test、Human Relay smoke |
| REQ-006 | Formal ReviewをPlanning、Checkpoint、Deliveryの3 Protocolとして提供し、Targeted Reviewをadvisoryとして分離する。 | Workflow integration、Review dogfood |
| REQ-007 | PlanningはHEAD Snapshot、Checkpoint／Deliveryは意味的BASEからHEADまでを起点とするDelta-bounded Snapshot Review、PR-styleはmerge-baseとして、変更面と現在の契約充足を両方評価する。 | range／binding test、Review evidence |
| REQ-008 | Review PerspectiveをProtocolから分離し、必要な観点だけを適用する。`repository-conventions`は明示された規約だけを評価し、規約がなければN/Aとする。 | Perspective smoke、N/A test |
| REQ-009 | Formal Reviewは構造化結果でP0／P1をblocking、P2／P3のみをnon-blockingとし、証拠不足時のPASSを禁止する。Targeted ReviewはFormal Gateを発生させない。 | output contract、model smoke |
| REQ-010 | Formal Quality Gateのaccepted blockerでrepository mutationが必要な場合、ChatGPTがSource HEADへbindされたRepair Batchを生成し、Mainの採用後にfreezeしてExecutorへ渡す。 | Repair dogfood、Artifact／Git evidence |
| REQ-011 | Executorはbounded implementationとverificationを所有し、Mainはdiff確認、明示的commit／push、Review起動を所有する。Humanだけがmergeする。 | Agent contract、Git ownership test |
| REQ-012 | 主要write-capable sub-agentを一つのcustom Executorへ統合し、read-only specialistを限定して残す。Issue Gradeをmodel／reasoningの自動routingへ使用しない。 | Agent inventory、config test |
| REQ-013 | Issue ExecutionをExecution Tranche、Checkpoint、Repair Batch、Final Completion Summary、Issue Exit Contractで制御する。 | representative Issue E2E |
| REQ-014 | Epic PlanがDelivery Topology、Delivery Boundary、Delivery Scope、Delivery Ownerを所有し、Issue ReviewとEpic Reviewを異なるContract Ownerで実行する。 | Epic Planning output、integration E2E |
| REQ-015 | PR Deliveryを一つのWorkflowとして、外部gate観測、blocking repair、fresh再Review、merge-prepared、Human Merge Gate、merge確認まで接続する。 | PR E2E、merge verification |
| REQ-016 | Git、GitHub、Oracle session、Workbench、Repair Batch、Executor Handoff、`report.md`のauthorityを分離し、新しい意味的state databaseやparserを作らない。 | absence test、Workflow review |
| REQ-017 | 新規・open・active Scopeの次操作をvNextへ一括cutoverし、既存文書は一括移行せず、実際に不足する契約だけを通常のPlanning gapとして局所refreshする。 | legacy Scope replay |
| REQ-018 | provider、installed、dogfoodのSkill、Agent、Workflow、Template、Scriptを同一責務へ揃え、旧surfaceとstale参照を除去する。 | parity test、repository search |
| REQ-019 | Planning、Review、Repair、Issue Execution、Epic Delivery、PR Deliveryを実際のScopeでdogfoodし、Initiative-level final qualityで統合検証する。 | final dogfood、CI、external Review |

## 6. 非機能要件

### NFR-001 変更容易性

- Prompt、model label、Oracle UI、Review field等の可変部分を交換可能なadapter、prompt resource、Protocol contractへ局所化する。
- Runtimeへ意味parserやWorkflow state machineを追加しない。
- exact module path、Prompt本文、JSON field、model labelはEpic Planning／implementationで検証可能な詳細として扱う。

### NFR-002 Git・side effect安全性

- `spec-dock-chatgpt`、ChatGPT、Executor、Review処理、隠れたautomationは、commit、push、stash、force、mergeを実行しない。
- Main Orchestratorは、PlanまたはWorkflowで定めたtransitionにおいて、working tree、diff、verification、必要な`report.md`更新を確認した後に限り、明示的にcommit／pushできる。
- Preflight failureを解消するために、CLIやsub-agentが自動commit／push／stashを行わない。
- PR mergeはHumanだけが実行し、Mainはmerge後の状態確認とfinish反映だけを行う。
- secret、token、cookie、private key、production dumpをPromptやArtifactへ含めない。
- shell invocationは可能な限りdirect argvとし、Promptやpathのshell injectionを防ぐ。

### NFR-003 信頼性・回復性

- transport failure、insufficient evidence、Formal Review FAILを異なる状態として扱う。
- Oracle sessionを確認・再接続できる既存機能を利用し、同じtaskの無根拠な重複実行を抑える。
- Review BASEを復元できない場合は、狭い範囲を推測せず、より古い安全なBASEへ広げる。
- GitHub repository／branch／HEADを確認できないFormal処理は停止する。

### NFR-004 性能・コスト

- tracked file自動添付、巨大共通JSON、同一HEADへの重複ChatGPT Reviewを避ける。
- 高度認知をChatGPTへ外部化し、Mainへraw transcriptを戻さない。
- Issue Gradeによる自動model escalationを行わない。
- 実測可能な場合はtoken／quotaを記録し、安定したtelemetryがない場合は後述のproxyで評価する。

### NFR-005 保守性・可読性

- Planning、Review、Repair、Execution、DeliveryのWorkflow authorityを共有文書と公開Skillへ明確に分離する。
- canonical仕様書、主要Artifact、利用者向けsummaryは日本語ファーストとする。
- 明示的なRepository Convention違反をReview対象とする。
- 古いDecisionと現在のDecisionを同一Snapshotへ混在させない。

### NFR-006 互換性

- `init-00322`、既存filesystem path、Node metadata、canonical file名、dependency commandを維持する。
- 本改訂ではrepository title、`.meta.json`、GitHub Issue #322を変更しない。
- closed／finished Scopeのhistorical artifactを変更しない。
- GitHub上のCodex PR Reviewを初期cutoverで廃止しない。

## 7. 受入条件

| ID | 受入条件 |
|---|---|
| AC-001 | `init-00322`の三文書が相互に矛盾せず、REQ-001〜REQ-019と7 Epicのtraceabilityを持つ。 |
| AC-002 | Actor responsibilityとHuman GateがPlanning、Review、Repair、Execution、Deliveryで一貫し、ChatGPT evidenceの自己申告だけでauthorityが成立しない。 |
| AC-003 | Initiative／Epic／Issue Planningが完全Bundle生成、セルフレビュー、内容不変配置、必要なHuman分割承認を実行できる。 |
| AC-004 | ChatGPT連携境界がGitHub exact repository／branch／HEADへfail closedでbindされ、default branchまたはtracked file添付へ黙ってfallbackしない。 |
| AC-005 | Planning、Checkpoint、Issue Delivery、Epic DeliveryのReviewが、P0／P1、P2／P3、証拠不足を意図したsemanticsで扱う。 |
| AC-006 | `repository-conventions`が規約あり／なしの双方で動作し、未定義規約を捏造しない。 |
| AC-007 | Targeted Reviewが対象とPerspectiveを受け、advisory結果だけを返し、Formal Gateやrepository mutationを発生させない。 |
| AC-008 | Repair BatchがSource HEADへbindされ、Mainの採用後にfreezeされ、materialな契約変更をPlanningへ返せる。 |
| AC-009 | Executor、`spec-dock-chatgpt`、隠れたautomationがGit transactionを行わず、Mainが定義済みtransitionで明示的にcommit／pushし、Humanだけがmergeする。 |
| AC-010 | 主要write Agentがcustom Executor一つへ統合され、不要なWriter／Reviewer／Analyzer経路がmaintained surfaceから除去される。 |
| AC-011 | Issue ExecutionがExecution Tranche、Checkpoint、Repair、Issue Delivery、Issue Exit ContractをE2Eで処理できる。 |
| AC-012 | Epic DeliveryがIssue ReviewとEpic Reviewを区別し、Delivery Ownerとintegration verificationを用いてPR Deliveryへ進める。 |
| AC-013 | PR DeliveryがP0／P1またはrequired CI failureを修復し、新HEADで必要なgateを再観測してmerge-preparedで停止する。 |
| AC-014 | P2／P3だけではbranch mutation、再CI、再Reviewを行わない。 |
| AC-015 | Human merge前にMerge Exitの`issue finish`／`epic finish`を行わず、merge後に最終reviewed headを確認する。 |
| AC-016 | provider、installed、dogfoodでSkill／Agent／Workflow／Template／Scriptの責務parityが確認され、旧必須surfaceが残っていない。 |
| AC-017 | 既存open Scopeが文書migrationなしでvNext Workflowへ入り、不足契約だけを局所Planning refreshできる。 |
| AC-018 | 代表dogfoodとInitiative-level final qualityが完了条件を満たし、各Epicが独立したmerge boundaryでHuman mergeまで完了する。 |

## 8. 成功指標と評価方法

評価期間は、vNext cutover後の**最低4週間かつ5件以上の代表Workflow実行**のうち、遅い方までとする。代表実行には、Planning、Checkpoint Repair、Issue Delivery、Epic Delivery、PR Deliveryを少なくとも1件ずつ含める。比較baselineはEpic 1で、可能な範囲で直近3件以上の旧Workflow実行から取得する。

| 指標 | Baseline | Target | 計測方法 |
|---|---|---|---|
| M-001 Unplanned Human Intervention | 旧Workflowの代表3件から、予定外の質問、copy／paste、manual triage、retry判断を数える | 5件中4件以上で予定外介入0。Goal、分割承認、material変更、merge等の計画済みHuman Gateは除外 | Workflow logとuser-facing eventをplanned／unplannedへ分類 |
| M-002 Main Context Protection | 旧代表実行でMainへ注入されたsub-agent／reviewer outputの総文字数またはtoken、raw transcript読込回数 | raw transcriptの必須読込0。Mainへ渡すhandoff payloadの中央値をbaseline比30%以上削減 | stable token telemetryがあればtoken、なければUTF-8 byte／文字数を使用 |
| M-003 Codex Cognitive Route Proxy | 旧Workflowでのlocal reviewer、manual planner、Docs Writer、Repository Analyst等のinvocation数 | cutover後のmaintained Workflowで必須invocation 0 | Agent／Skill invocation logとrepository inventory |
| M-004 Human Gate Integrity | 旧運用で手順依存 | 自動merge0、未承認Node分割0、material変更の無承認実行0 | PR／Runtime event audit |
| M-005 Minimal State | 旧receipt／ledger／registry surfaceの件数 | vNextの新規semantic state artifact 0 | maintained asset inventoryとrepository search |
| M-006 Asset Parity | provider／installed／dogfood間の差分 | 対象surface 100% parity | parity testとinstall／dogfood smoke |
| M-007 Workflow Reliability | vNext baselineなし | 5つの代表Workflowが、定義済みHuman Gateを除き、同じcontractで完走または明確にfail closedする | E2E report、CI、Oracle／GitHub evidence |
| M-008 Changeability Drill | vNext baselineなし | Prompt、model label、Review fieldの代表的な1変更がRuntime schema migrationなしで局所変更できる | Epic 7のchange drill |

Codex token／quotaの実量削減は、providerが安定した比較可能telemetryを提供しない限り**戦略仮説**として扱う。M-002とM-003を実用proxyとし、実量が取得できた場合のみ補助指標として報告する。

## 9. 主要リスク

| ID | リスク | 緩和策 |
|---|---|---|
| R-001 | Oracle／ChatGPT UI変更でFormal処理が停止する。 | 薄いadapter、operator config、Human Relay、live smoke、同一contract維持。 |
| R-002 | ChatGPTがGitHub branch／HEADを誤認する。 | local preflight、exact SHA binding、observed HEAD確認、fail closed。 |
| R-003 | ChatGPT生成ファイルまたはJSON形式が揺れる。 | complete file contract、self-review、Protocol別最小contract、model smoke。 |
| R-004 | Review／Repairが重くなり開発速度が落ちる。 | P0／P1のみblocking、P2／P3 no-mutation、selected Perspective、同一HEAD重複Review回避。 |
| R-005 | Repair BatchがPlanningの裏口になる。 | authority hierarchy、freeze、forbidden scope、Planning escalation。 |
| R-006 | 旧surfaceの参照漏れで二重Workflowが残る。 | asset inventory、parity test、global search、cutover Epic、final dogfood。 |
| R-007 | Existing Scopeに必要契約がなく実行不能になる。 | migrationではなく通常のPlanning gapとして局所refresh。 |
| R-008 | Initiative規模が大きくPRが肥大化する。 | 各Epicを独立merge boundaryとし、Epic内でも小さいPRを優先する。 |
| R-009 | evidence fileのauthority自己申告をcanonical authorityと誤認する。 | Human decisionと`report.md` dispositionを唯一のadoption gateとして明示する。 |

## 10. Epic handoff seed

本Initiativeは次の7 Epicへ分割する。

1. **Delegation Foundation, Asset Inventory, and Thin ChatGPT Adapter**
2. **Integrated Planning Bundle and Planning Workflow Cutover**
3. **Contract-Driven Review Protocols and Targeted Review**
4. **Repair Batch and Executor-Centered Issue Execution**
5. **Plan-Driven Epic and PR Delivery**
6. **Global Cutover, Asset Parity, and Legacy Surface Removal**
7. **End-to-End Dogfood, Final Quality, and Release**

Epicの依存、成果物、Requirement／AC coverage、評価指標への責務は`plan.md`で定義する。

## 11. Epic Planningへ委譲する事項

Initiative-levelのHuman判断として未確定事項はない。次はreplaceable implementation detailであり、Epic Planningとrepository調査／live smokeに基づいて具体化する。

- Python package内のmodule／class／file path。
- `spec-dock-chatgpt`の最終command／flag表現とerror code。
- Oracleのconfig key、session path、output discovery。
- Protocol別JSONの最終field名と型。
- Prompt本文、few-shot、Perspective wording。
- Agent runtimeが受理するmodel label／reasoning enum。
- PR observer／pollingの具体的統合方法。
- 成功指標baselineの採取手段とstable telemetryの有無。
