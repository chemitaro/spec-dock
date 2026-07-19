# init-00322 GPT 56 ChatGPT First Intelligence Architecture — 要件定義


## 1. 文書の役割とInitiative identity

この文書は、SpecDockのPlanning、Review、Architecture-Aware Execution Brief、Repair、Execution、Epic／PR DeliveryをChatGPT Delegation-Firstな構造で提供するInitiativeの戦略目的、必須能力、非交渉制約、成功条件を定義する。

### 1.1 Initiative identity

- Initiative ID: `init-00322`
- filesystem path: `spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture`
- GitHub Issue: `#322`
- repository title: `GPT 56 ChatGPT First Intelligence Architecture`
- program label: `ChatGPT 5.6 Pro Delegation-First Workflow vNext`

Initiative ID、filesystem path、GitHub Issue、repository titleはこのInitiativeを識別する安定した外部参照であり、program labelは本Initiativeが実現するWorkflow architectureを示す。

### 1.2 文書と証跡のauthority

- Humanの明示承認とSpecDockのpromotion条件を満たした`requirement.md`、`design.md`、`plan.md`がcanonical authorityである。
- ADRは、Humanが採用し、Main Orchestratorが`report.md`へdispositionを記録した場合にarchitecture authorityを持つ。
- Interview、Discussion、Research、self-review、raw ChatGPT outputは判断根拠となるevidenceであり、それ自体のfront matterだけではcanonical authorityを成立させない。
- Architecture-Aware Execution Briefは、特定Execution Unitに限定されたfrozen subordinate execution contractであり、canonical三文書を置き換えない。
- Repair Batchは、Formal Quality Gateで発見されたaccepted blockerに限定されたfrozen subordinate repair contractであり、canonical三文書を置き換えない。
- 実行状態、採用状態、completion、handoffは`report.md`、Git、GitHub、Oracle session等の各SSOTで管理し、canonical仕様書へ逐次転記しない。

## 2. 目的とWhy now

### 2.1 主目的

SpecDockの高度認知処理をChatGPTへ、repository mutationとWorkflow制御をCodexへ、構造的・決定的処理をSpecDock Runtimeへ分離し、Human Gateを維持したままPlanningからmerge確認までを一貫したvNext Workflowとして自動化する。

Architecture-Aware Execution Briefには、次の二つの目的がある。

1. **分析品質と実装確度の向上**
   ChatGPTの横断調査・高深度分析能力を用いて、最新HEAD上の目的、現状、アーキテクチャ、契約、適用規約、関連Artifact、コード、テスト、設定を統合し、各Execution Unitのテスト戦略と実装戦略を実装前に具体化する。
2. **Codex認知資源の有効活用**
   関連Artifact探索、構造理解、実装候補比較、テスト戦略設計等の高コスト認知をChatGPTへ移し、Codex MainとExecutorのトークン、tool call、試行錯誤を、repository mutation、verification、Workflow制御へ集中させる。

分析品質と実装確度の向上を第一目的、Codex認知資源の有効活用を第二目的とする。コスト削減は重要であるが、品質低下と引き換えにはしない。Execution Briefの導入価値は、より正確な理解、より良いテスト戦略、手戻り削減、明確な停止条件、Codex負荷低減を総合して評価する。

### 2.2 Why now: GPT-5.5前提からGPT-5.6／ChatGPT Firstへの転換

現行Workflowの主要部分は、GPT-5.5世代のモデル能力と運用上の不確実性を前提に設計されている。そのため、Requirement／Design／Planを段階的に生成し、ChatGPT出力を低authority evidenceとして保存し、Codexがclaimを採否してcanonical文書を再構成し、複数のローカルReviewer Agentとmanual fallbackで品質を補う構造になっている。

Humanは、GPT-5.6 ProをPlanning、Formal Review、Repair設計、実装前の高深度分析へ利用するChatGPT First方針を採用した。この前提では、旧構造を維持するほど次の費用が累積する。

1. 同じ意味をChatGPT、Codex、ledger、reviewerで再生成する二重authoring。
2. Main Orchestratorへ長い調査・review履歴を戻すことによるcontext圧迫。
3. ローカルReviewer／Writer／manual planning経路によるCodex quota消費。
4. Execution UnitごとにCodexが関連Artifact、architecture、test seamを再調査する重複コスト。
5. Oracle、model、Promptの変更に追従するための複数surface改修。
6. 新しいWorkflowやArtifactを旧authority modelへ追加することによる移行負債。

### 2.3 副目的

- Codex Main Orchestratorの長寿命contextを、詳細調査、実装、Review transcriptから保護する。
- Executorが、実装前に十分なEvidence、目的、制約、テスト戦略、停止条件を受け取り、repository factsに基づく実装へ集中できるようにする。
- 特定のアーキテクチャ、フレームワーク、設計手法に依存せず、対象Execution Unitに実際に適用されるConcernを動的に選択する。
- 旧ChatGPT authoring evidence lane、manual planning fallback、ローカルReviewer Agent、巨大Evidence Ledger、過剰なreceipt／registry／state machineを廃止する。
- ChatGPT、Oracle、Codexの将来変更へ追従しやすい薄い境界を作る。
- Issue単位または適切なbatch単位でmerge可能なPRを作りやすくし、巨大なEpic-wide PRによる品質ゲート負荷を抑える。
- 日本語ファーストの仕様・文書規約をFormal Reviewで継続的に検証する。

### 2.4 利用者価値・運用価値

- HumanはGoal、Scope分割、materialな価値判断、PR merge判断へ集中できる。
- Main OrchestratorはWorkflow判断、authority、Git transaction、Human Gateへ集中できる。
- ChatGPTは、複数文書、Artifact、コード、テスト、設定を横断して、Execution Unitの意味と実行方法を高深度に統合できる。
- Executorは、承認済みPlanとArchitecture-Aware Execution BriefまたはRepair Batchへ集中できる。
- Reviewの対象、時間範囲、Perspective、判定規則を再現可能にできる。
- Oracle障害時も、処理契約を変えず別browser経路またはHuman Relayで継続できる。

## 3. スコープと境界

### 3.1 必須スコープ

- ChatGPT、Main Orchestrator、Executor、SpecDock Runtime、Humanの責務とauthorityの再定義。
- Initiative／Epic／Issue PlanningのIntegrated Planning Bundle化。
- Planning、Checkpoint、DeliveryのFormal Review ProtocolとTargeted Review。
- accepted blockerを処理するRepair Batch。
- 非機械的なExecution Unitを実装前に具体化するArchitecture-Aware Execution Brief。
- ChatGPTによる関連Artifact、architecture、目的、制約、code、tests、configuration、repository conventionsの横断的探索とEvidence選択。
- Executor中心のIssue Execution、Plan-driven Delivery Topology、PR Delivery、Human Merge Gate。
- `spec-dock-chatgpt`による薄いOracle／GitHub連携境界。
- Workbench、Oracle session、Git／GitHub、Execution Brief、Repair Batch、`report.md`のauthority分離。
- provider、installed、dogfood surfaceの同一責務への整合。
- 既存Scope文書を一括変換しないglobal Workflow cutover。
- 代表WorkflowによるdogfoodとInitiative-level final quality。

### 3.2 禁止事項

- ChatGPT、`spec-dock-chatgpt`、Executor、Runtimeによる隠れたcommit、push、stash、force、merge。
- Humanの明示判断を伴わないInitiative作成、Epic／Issue分割、material Scope変更、PR merge。
- `plan.md`、Review JSON、Execution Brief、Repair BatchをRuntimeが意味解析してgate判定すること。
- tracked repository fileをFormal ChatGPT処理へ自動添付してGitHubと二重SSOTにすること。
- Codexが関連ADR、Interview、Discussion、Researchを意味的に選別・要約してChatGPT Promptを組み立てることを標準経路にすること。
- Review receipt、Planning state、accepted HEAD registry、Checkpoint DB、Execution Brief DB、Repair iteration DB等の新しいWorkflow databaseを導入すること。
- 旧WorkflowとvNextをScope作成日やversionで長期並行運用すること。
- Architecture-Aware Execution BriefをIssue直下の第四canonical文書、Planning Bundleの一部、またはPlan変更の裏口として扱うこと。
- 対象Execution Unitに存在しないdomain、event、aggregate、bounded context、security boundary、transaction semantics等をモデルが捏造すること。

### 3.3 Non-goals

- 既存Scope文書の一括変換または全open Scopeの事前refresh。
- closed／finished Scopeの書き換え。
- 自動merge、auto-merge有効化、Human Merge Gateの削除。
- GitHub上のCodex PR Reviewの即時廃止。
- 汎用`chatgpt-use` Skillの再実装。
- Oracle session／artifact保存機構の再実装。
- Prompt wording、model label、JSONやMarkdownの任意fieldを長期固定すること。
- 全既存Discussion／Report／ADRを新形式へ移行すること。
- 全Milestoneに固定長・固定sectionの巨大Execution Briefを強制すること。
- DDD、イベント駆動、特定framework、特定language、特定product typeをArchitecture-Aware Execution Briefの前提とすること。
- Initiative identity、GitHub Issue、Node metadata、execution stateをPlanning Bundleから暗黙に変更すること。

## 4. ステークホルダーとauthority

| Actor | Initiative-level responsibility | 明示的に所有しないもの |
|---|---|---|
| Human | Initiative Goal、Epic／Issue分割承認、material Scope変更、PR merge、evidence／ADRの最終採用判断 | 日常的なfile mutation、Reviewの逐次実行 |
| ChatGPT | Integrated Planning、Formal／Targeted Review、Architecture-Aware Execution Brief、Repair Batch、高深度分析 | canonical filesystem配置、Git transaction、Node mutation、merge、自己申告だけによるauthority確定 |
| Codex Main Orchestrator | Workflow、target、authority、ChatGPT出力の採否、Executor、Git transaction、Human Gate、`report.md` disposition | 長時間の詳細実装、Review verdictの捏造、関連Artifactの重い意味的選別 |
| Executor | Execution Unit／Execution Brief／Repair Batch内の調査、実装、verification、working tree mutation | commit、push、Plan変更、Scope拡大、Formal Gate |
| SpecDock Runtime | Node、dependency、active scope、validate／sync、Workbench、決定的file／metadata操作 | LLM文書、Review JSON、Execution Brief、Repair Batchの意味解析 |
| GitHub／Oracle | tracked repository、PR／CI／Codex Review、ChatGPT browser session／artifact | Planning／Review／Brief Contractの意味判断、Human adoption |

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
| REQ-013 | Issue ExecutionをExecution Tranche、Architecture-Aware Execution Brief、Checkpoint、Repair Batch、Final Completion Summary、Issue Exit Contractで制御する。 | representative Issue E2E |
| REQ-014 | Epic PlanがDelivery Topology、Delivery Boundary、Delivery Scope、Delivery Ownerを所有し、Issue ReviewとEpic Reviewを異なるContract Ownerで実行する。 | Epic Planning output、integration E2E |
| REQ-015 | PR Deliveryを一つのWorkflowとして、外部gate観測、blocking repair、fresh再Review、merge-prepared、Human Merge Gate、merge確認まで接続する。 | PR E2E、merge verification |
| REQ-016 | Git、GitHub、Oracle session、Workbench、Execution Brief、Repair Batch、Executor Handoff、`report.md`のauthorityを分離し、新しい意味的state databaseやparserを作らない。 | absence test、Workflow review |
| REQ-017 | 新規・open・active Scopeの次操作をvNextへ一括cutoverし、既存文書は一括移行せず、実際に不足する契約だけを通常のPlanning gapとして局所refreshする。 | legacy Scope replay |
| REQ-018 | provider、installed、dogfoodのSkill、Agent、Workflow、Template、Scriptを同一責務へ揃え、旧surfaceとstale参照を除去する。 | parity test、repository search |
| REQ-019 | Planning、Review、Execution Brief、Repair、Issue Execution、Epic Delivery、PR Deliveryを実際のScopeでdogfoodし、Initiative-level final qualityで統合検証する。 | final dogfood、CI、external Review |
| REQ-020 | 非機械的なMilestoneまたはExecution Unitを開始する前に、ChatGPTがexact GitHub HEAD上の目的、現状、architecture、適用契約、関連Artifact、code、tests、configuration、repository conventionsを横断調査し、具体的なArchitecture-Aware Execution Briefを生成できる。 | Brief dogfood、Evidence review |
| REQ-021 | Architecture-Aware Execution Briefは、対象Unitに実際に適用されるConcernだけをrepository evidenceから動的に選択し、特定のarchitecture、domain model、framework、product typeを必須前提にしない。確認できないmaterial semanticは推測せず`insufficient-evidence`を返す。 | diverse-slice model smoke |
| REQ-022 | Codex／wrapperはrepository、branch、HEAD、Scope paths、canonical anchors、Artifact directories、dependency scopes、Execution Unit IDだけを決定的に提示し、関連Artifactの意味的探索・選別・統合はChatGPTが担う。 | Context assembly test、token／tool-call comparison |
| REQ-023 | Execution Briefは`ready | planning-gap | insufficient-evidence`を返し、`ready`候補だけをMainが採用してIssue `artifacts/`へ内容不変で配置・freezeし、Executorへ渡す。 | lifecycle E2E、Artifact evidence |
| REQ-024 | `plan.md`をIssue全体のPlanning SSOTとして維持し、accepted Execution Briefは特定Execution Unitに限ったfrozen subordinate execution contractとする。Briefは上位Requirement、ADR、Design、Planを変更・上書きできない。 | authority review、conflict test |
| REQ-025 | Execution Briefは、分析品質、Evidence completeness、テスト戦略、実装収束、手戻り、Codex token／tool call／試行錯誤を代表Unitで比較評価し、品質悪化を伴うコスト削減を成功とみなさない。 | controlled evaluation report |

## 6. 非機能要件

### NFR-001 変更容易性

- Prompt、model label、Oracle UI、Review field、Execution Brief Concern catalog等の可変部分を交換可能なadapter、prompt resource、Protocol contractへ局所化する。
- Runtimeへ意味parserやWorkflow state machineを追加しない。
- exact module path、Prompt本文、JSON／Markdown field、model labelはEpic Planning／implementationで検証可能な詳細として扱う。
- Concern catalogへ新しいarchitecture lensを追加してもcanonical file schema migrationを要求しない。

### NFR-002 Git・side effect安全性

- `spec-dock-chatgpt`、ChatGPT、Executor、Review処理、Execution Brief処理、隠れたautomationはcommit、push、stash、force、mergeを実行しない。
- Main Orchestratorは、PlanまたはWorkflowで定めたtransitionにおいて、working tree、diff、verification、必要な`report.md`更新を確認した後に限り、明示的にcommit／pushできる。
- Preflight failureを解消するためにCLIやsub-agentが自動commit／push／stashを行わない。
- PR mergeはHumanだけが実行し、Mainはmerge後の状態確認とfinish反映だけを行う。
- secret、token、cookie、private key、production dumpをPromptやArtifactへ含めない。
- shell invocationは可能な限りdirect argvとし、Promptやpathのshell injectionを防ぐ。

### NFR-003 信頼性・回復性

- transport failure、`insufficient-evidence`、`planning-gap`、Formal Review FAILを異なる状態として扱う。
- Oracle sessionを確認・再接続できる既存機能を利用し、同じtaskの無根拠な重複実行を抑える。
- Review BASEまたはExecution Brief Source HEADを復元できない場合、狭い範囲を推測せず安全側へ倒す。
- GitHub repository／branch／HEADを確認できないFormal処理とExecution Brief生成は停止する。
- accepted Briefを実装結果に合わせて書き換えず、前提がmaterialに変わった場合は再生成またはPlanningへ戻る。

### NFR-004 分析品質・性能・コスト

- Execution Briefの第一目的を、ChatGPTの高深度分析による目的理解、architecture理解、Evidence completeness、テスト戦略、実装品質、収束性の向上とする。
- Codex token／quota、tool call、repository探索、試行錯誤の削減を重要な副次目的として評価する。
- tracked file自動添付、巨大共通schema、同一HEADへの重複ChatGPT処理を避ける。
- 高度認知をChatGPTへ外部化し、Mainへraw transcriptを戻さない。
- Issue Gradeによる自動model escalationを行わない。
- 安定したtoken telemetryがない場合はtool call数、handoff byte数、failure cycle数、Briefなしbaselineとの差をproxyとして利用する。

### NFR-005 保守性・可読性

- Planning、Review、Execution Brief、Repair、Execution、DeliveryのWorkflow authorityを共有文書と公開Skillへ明確に分離する。
- canonical仕様書、主要Artifact、利用者向けsummaryは日本語ファーストとする。
- 明示的なRepository Convention違反をReview対象とする。
- 古いDecisionと現在のDecisionを同一Snapshotへ混在させない。
- Architecture-Aware Execution Briefの基本sectionと動的Concern sectionを分け、非適用項目の大量`N/A`を避ける。

### NFR-006 互換性

- Initiative ID、filesystem path、Node metadata、canonical file名、dependency commandを安定した互換interfaceとして扱う。
- Initiative identityの変更は本InitiativeのWorkflow実装とは分離し、Humanの明示判断と管理操作を必要とする。
- closed／finished Scopeのhistorical artifactを不変の履歴として扱う。
- GitHub上のCodex PR Reviewを初期cutoverで廃止しない。
- Architecture-Aware Execution Briefを新しい必須top-level文書にせず、canonical Scope schemaを三文書中心に保つ。

### NFR-007 汎用性とarchitecture neutrality

- Architecture-Aware Execution Briefは、DDD、イベント駆動、Hexagonal、MVC、CLI、UI、data pipeline、build、deployment、documentation等のいずれも必須前提にしない。
- ChatGPTは、対象Unitに適用されるConcernをrepository evidenceから選択する。
- domain、event、transaction、security等が非適用の場合、存在しない概念を生成しない。
- 簡単なmechanical changeではBriefを省略できるか、最小構成で生成できる。

## 7. 受入条件

| ID | 受入条件 |
|---|---|
| AC-001 | `init-00322`の三文書が相互に矛盾せず、REQ-001〜REQ-025と7 Epicのtraceabilityを持つ。 |
| AC-002 | Actor responsibilityとHuman GateがPlanning、Review、Execution Brief、Repair、Execution、Deliveryで一貫し、ChatGPT evidenceの自己申告だけでauthorityが成立しない。 |
| AC-003 | Initiative／Epic／Issue Planningが完全Bundle生成、セルフレビュー、内容不変配置、必要なHuman分割承認を実行できる。 |
| AC-004 | ChatGPT連携境界がGitHub exact repository／branch／HEADへfail closedでbindされ、default branchまたはtracked file添付へ黙ってfallbackしない。 |
| AC-005 | Planning、Checkpoint、Issue Delivery、Epic DeliveryのReviewがP0／P1、P2／P3、証拠不足を意図したsemanticsで扱う。 |
| AC-006 | `repository-conventions`が規約あり／なしの双方で動作し、未定義規約を捏造しない。 |
| AC-007 | Targeted Reviewが対象とPerspectiveを受け、advisory結果だけを返し、Formal Gateやrepository mutationを発生させない。 |
| AC-008 | Repair BatchがSource HEADへbindされ、Mainの採用後にfreezeされ、materialな契約変更をPlanningへ返せる。 |
| AC-009 | Executor、`spec-dock-chatgpt`、隠れたautomationがGit transactionを行わず、Mainが定義済みtransitionで明示的にcommit／pushし、Humanだけがmergeする。 |
| AC-010 | 主要write Agentがcustom Executor一つへ統合され、不要なWriter／Reviewer／Analyzer経路がmaintained surfaceから除去される。 |
| AC-011 | Issue ExecutionがExecution Tranche、Architecture-Aware Execution Brief、Checkpoint、Repair、Issue Delivery、Issue Exit ContractをE2Eで処理できる。 |
| AC-012 | Epic DeliveryがIssue ReviewとEpic Reviewを区別し、Delivery Ownerとintegration verificationを用いてPR Deliveryへ進める。 |
| AC-013 | PR DeliveryがP0／P1またはrequired CI failureを修復し、新HEADで必要なgateを再観測してmerge-preparedで停止する。 |
| AC-014 | P2／P3だけではbranch mutation、再CI、再Reviewを行わない。 |
| AC-015 | Human merge前にMerge Exitの`issue finish`／`epic finish`を行わず、merge後に最終reviewed headを確認する。 |
| AC-016 | provider、installed、dogfoodでSkill／Agent／Workflow／Template／Scriptの責務parityが確認され、旧必須surfaceが残っていない。 |
| AC-017 | 既存open Scopeが文書migrationなしでvNext Workflowへ入り、不足契約だけを局所Planning refreshできる。 |
| AC-018 | 代表dogfoodとInitiative-level final qualityが完了条件を満たし、各Epicが独立したmerge boundaryでHuman mergeまで完了する。 |
| AC-019 | 非機械的な代表Milestoneで、ChatGPTがexact HEADから関連Artifactとrepository evidenceを横断調査し、目的、現状、適用Concern、テスト戦略、実装戦略、停止条件を含むBriefを生成する。 |
| AC-020 | DDD／イベント駆動を含むUnitでは該当Concernを選択し、CLI／build／documentation等のUnitでは非該当Concernを強制せず、存在しないdomain／event概念を捏造しない。 |
| AC-021 | `ready` BriefだけがWorkbench candidateからIssue Artifactへ昇格・freezeされ、`planning-gap`／`insufficient-evidence`ではExecutorを開始しない。 |
| AC-022 | accepted Briefが`plan.md`を変更せず、特定Execution Unitのsubordinate contractとしてExecutorへ渡され、Briefと対応実装が同一candidate commitに含まれる。 |
| AC-023 | ChatGPTが関連Artifactを意味的に選択し、Codex／wrapperは決定的なnavigation anchorsだけを提供する。Mainはraw Artifactを再分析せず、binding、status、evidence、scopeを確認する。 |
| AC-024 | Briefなし、汎用Brief、Architecture-Aware Briefを代表Unitで比較し、Architecture-Aware BriefがEvidence completeness、test strategy、first-pass convergence、または手戻りで改善し、品質を悪化させない。 |
| AC-025 | Codex tokenまたはproxyとしてのtool call、探索回数、failure cycle、handoff量の少なくとも一つが改善し、改善しない場合も品質効果と総遅延を含む継続判断が記録される。 |

## 8. 成功指標と評価方法

評価期間は、vNext cutover後の**最低4週間かつ5件以上の代表Workflow実行**のうち遅い方までとする。Execution Brief評価は、少なくとも次の異なるtask shapeを含む。

- 複数moduleまたは複数layerへまたがる機能変更。
- 独自frameworkまたは非標準architectureを利用する変更。
- API／compatibilityまたはdata／persistenceへ影響する変更。
- CLI、build、deployment、documentation等、domain／event concernが非適用な変更。
- 明白なmechanical changeでBrief省略が妥当な変更。

| 指標 | Baseline | Target | 計測方法 |
|---|---|---|---|
| M-001 Unplanned Human Intervention | 旧Workflow代表3件 | 5件中4件以上で予定外介入0 | Workflow logをplanned／unplannedへ分類 |
| M-002 Main Context Protection | 旧代表実行のsub-agent／reviewer payload | raw transcript必須読込0、handoff中央値30%以上削減 | tokenまたはUTF-8 byte／文字数 |
| M-003 Codex Cognitive Route Proxy | local reviewer、manual planner、Writer、Analyzer invocation | maintained Workflowで必須invocation 0 | Agent／Skill invocation log |
| M-004 Human Gate Integrity | 旧運用手順 | 自動merge0、未承認分割0、無承認material変更0 | PR／Runtime event audit |
| M-005 Minimal State | 旧receipt／ledger／registry件数 | 新規semantic state DB 0 | asset inventory／search |
| M-006 Asset Parity | provider／installed／dogfood差分 | 100% parity | parity test／smoke |
| M-007 Workflow Reliability | vNext baselineなし | 代表Workflowが完走または明確にfail closed | E2E report、CI、Oracle／GitHub evidence |
| M-008 Changeability Drill | vNext baselineなし | Prompt、model label、Review／Brief fieldの変更がRuntime migrationなしで局所変更可能 | Epic 7 change drill |
| M-009 Brief Evidence Quality | Briefなし／汎用Brief | material Evidence omission、unsupported assumption、wrong Concern selectionを減らす | Brief review rubric、Checkpoint finding分類 |
| M-010 Implementation Convergence | Briefなしbaseline | first Checkpoint PASS率改善、またはfailure cycle／手戻り削減 | Executor log、Review result |
| M-011 Codex Resource Shift | Briefなしbaseline | tokenが取れる場合はCodex token削減。取れない場合はtool call、探索command、handoff量、failure cycleの一つ以上を改善 | telemetryまたはproxy |
| M-012 General Applicability | architecture別baselineなし | 複数task shapeで適用Concernが妥当。非適用Concern捏造0 | model smoke、Human／Review classification |
| M-013 Total Delivery Efficiency | Briefなしbaseline | ChatGPT latencyを含む総時間を記録し、品質向上・Codex削減・総遅延のtradeoffを明示 | wall-clock、Oracle session、Executor timing |

Codex token／quota実量削減は、providerが安定した比較可能telemetryを提供しない限り戦略仮説として扱う。M-009、M-010を第一級の品質指標、M-011を資源指標、M-013を総合運用指標とする。

## 9. 主要リスク

| ID | リスク | 緩和策 |
|---|---|---|
| R-001 | Oracle／ChatGPT UI変更でFormal処理が停止する。 | 薄いadapter、operator config、Human Relay、live smoke。 |
| R-002 | ChatGPTがGitHub branch／HEADを誤認する。 | local preflight、exact SHA binding、observed HEAD、fail closed。 |
| R-003 | ChatGPT生成ファイル／JSON／Brief形式が揺れる。 | complete output contract、self-review、最小schema、model smoke。 |
| R-004 | Review／Execution Brief／Repairが重くなり開発速度が落ちる。 | mechanical skip、selected Concern、重複回避、総遅延計測。 |
| R-005 | Repair BatchまたはExecution BriefがPlanningの裏口になる。 | authority hierarchy、freeze、forbidden scope、Planning escalation。 |
| R-006 | 旧surfaceの参照漏れで二重Workflowが残る。 | inventory、parity test、global search、cutover Epic。 |
| R-007 | Existing Scopeに必要契約がなく実行不能になる。 | 通常のPlanning gapとして局所refresh。 |
| R-008 | Initiative規模が大きくPRが肥大化する。 | 各Epic独立merge boundary、小PR、Final Quality Issue。 |
| R-009 | evidence fileのauthority自己申告をcanonical authorityと誤認する。 | Human decisionと`report.md` disposition。 |
| R-010 | Briefが特定architecture／設計手法へ偏り、非適用概念を捏造する。 | 動的Concern選択、architecture-neutral prompt、diverse smoke。 |
| R-011 | ChatGPTのArtifact探索が重要判断を見落とす。 | deterministic anchors、Evidence Used／Gaps、`insufficient-evidence`、review。 |
| R-012 | Codex削減を優先しすぎて分析品質または総時間が悪化する。 | 品質指標を第一級とし、resourceとwall-clockを別計測。 |
| R-013 | Briefが古いHEADや変更済みPlanへbindされたまま使われる。 | Source HEAD binding、material change時再生成、stale check。 |
| R-014 | MilestoneごとのBriefでArtifactが増殖する。 | semantic Execution Unit単位、mechanical skip、immutable naming、reportは主要参照のみ。 |
| R-015 | ExecutorがBriefを盲信しrepository factsとの矛盾を無視する。 | authority分離、Executor stop condition、planning-gap routing。 |

## 10. Epic handoff seed

本Initiativeは次の7 Epicへ分割する。

1. **Delegation Foundation, Asset Inventory, and Thin ChatGPT Adapter**
2. **Integrated Planning Bundle and Planning Workflow Cutover**
3. **Contract-Driven Review Protocols and Targeted Review**
4. **Architecture-Aware Execution Brief, Repair Batch, and Executor-Centered Issue Execution**
5. **Plan-Driven Epic and PR Delivery**
6. **Global Cutover, Asset Parity, and Legacy Surface Removal**
7. **End-to-End Dogfood, Final Quality, and Release**

Epicの依存、成果物、Requirement／AC coverage、評価指標への責務は`plan.md`で定義する。

## 11. Epic Planningへ委譲する事項

Initiative-levelのHuman判断として未確定事項はない。次はreplaceable implementation detailであり、Epic Planningとrepository調査／live smokeに基づいて具体化する。

- Python package内のmodule／class／file path。
- `spec-dock-chatgpt`の最終command／flag表現とerror code。
- Oracleのconfig key、session path、output discovery。
- Review JSONとExecution Brief Markdownの最終field名・型・section。
- Prompt本文、few-shot、Concern catalog wording。
- Agent runtimeが受理するmodel label／reasoning enum。
- PR observer／pollingの具体的統合方法。
- Execution Unit IDの解決方式とMilestone／Tranche mapping。
- Brief生成を省略できるmechanical change判定の運用例。
- 成功指標baselineの採取手段とstable telemetryの有無。
