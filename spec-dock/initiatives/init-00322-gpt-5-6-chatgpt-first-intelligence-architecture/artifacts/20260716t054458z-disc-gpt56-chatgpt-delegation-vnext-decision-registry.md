---
種別: disc
ID: "20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry"
タイトル: "GPT-5.6 / ChatGPT Delegation vNext — Current Effective Decision Snapshot"
状態: "archived"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-16"
親: ["init-00322"]
関連:
  - "https://github.com/chemitaro/spec-dock"
  - "https://github.com/chemitaro/spec-dock/pull/323"
authority: "user-approved"
derived_from:
  - "ChatGPT interview and accepted decisions through Question 69"
  - "chemitaro/spec-dock@main after PR #323"
  - "steipete/oracle public repository and local chatgpt-use wrapper"
  - "openai/codex public review implementation"
  - "previous incremental Decision Registry, retained only as audit evidence"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
---

# GPT-5.6 / ChatGPT Delegation vNext — Current Effective Decision Snapshot

## 位置づけ

- この文書は、GPT-5.6／ChatGPT Delegation vNextについて、**現在有効な意思決定だけを統合した公式Discussion Snapshot**である。
- 本文は、以前の逐次Decision一覧、改訂注記、withdrawn案、legacy ID対応表を置き換える。実装・Initiative Planning・Reviewでは、この文書の現在形だけを参照する。
- 過去の会話ログと旧Registryは監査証拠であり、実装authorityではない。本文と過去ログが矛盾する場合は、本文を優先する。
- すべての`D2-*`は現在有効である。`active`／`revised`／`superseded`等の状態表示は本文に持ち込まない。
- 将来、同じ論点の判断が変わる場合は、このCurrent Snapshot内の該当Decision本文を最新内容へ置換する。履歴は別のaudit surfaceへ残し、この文書へ旧案を併記しない。
- authorityは`user-approved`であるが、Initiativeの`requirement.md`、`design.md`、`plan.md`、ADR、Skill、Runtimeへ反映されるまではcanonical product authorityではない。

## 対象論点 (必須)

- GPT-5.6 Pro、Oracle、Codex Main Orchestrator、Executor、SpecDock Runtimeの責務分離。
- Initiative／Epic／Issue Planning、Formal Review、Targeted Review、Repair Batch、Issue／Epic Execution、PR DeliveryのvNext。
- `spec-dock-chatgpt` CLI、GitHub exact branch／HEAD、Oracle session／artifact、Operator Contextの境界。
- Review Protocol、Temporal Window、BASE SHA、Mutation Frontier、Semantic Expansion、Perspective、Protocol固有JSON。
- Skill／Agent topology、Model／Reasoning policy、Workbench、`report.md`、Runtime state方針。
- 既存Scopeを変換しないWorkflow／Actorの一括cutover。
- Initiative Goal、Non-goals、今後のInitiative Planning入力。

## derived question sheets / research (必須)

- `interview`:
  - `artifacts/20260716t235120z-01-interview-initiative-goal-authority-and-simplification.md`
  - `artifacts/20260716t235120z-02-interview-integrated-planning-and-document-authority.md`
  - `artifacts/20260716t235120z-03-interview-review-protocols-scope-and-perspectives.md`
  - `artifacts/20260716t235120z-04-interview-repair-batch-executor-and-git-boundaries.md`
  - `artifacts/20260716t235120z-05-interview-delivery-topology-pr-and-finish-semantics.md`
  - `artifacts/20260716t235120z-06-interview-skill-agent-oracle-and-model-policy.md`
- `research`:
  - `artifacts/20260716t235120z-11-research-openai-codex-review-target-and-scope-model.md`
  - `artifacts/20260716t235120z-12-research-oracle-thin-adapter-and-github-binding.md`
  - `artifacts/20260716t235120z-13-research-current-repository-workflow-gap-and-migration-impact.md`
  - `artifacts/20260716t131924z-01-research-initiative-bootstrap-repository-baseline.md`
- `disc`:
  - `artifacts/20260716t235120z-07-disc-planning-authority-and-yagni-rationale.md`
  - `artifacts/20260716t235120z-08-disc-review-architecture-decision-rationale.md`
  - `artifacts/20260716t235120z-09-disc-repair-and-delivery-decision-rationale.md`
  - `artifacts/20260716t235120z-10-disc-skill-topology-and-global-cutover-rationale.md`
- その他の根拠:
  - `steipete/oracle`のBrowser Mode、session、reattach、response、artifact、config、follow-up。
  - ローカル`chatgpt-use` SkillとOracle wrapper。
  - `openai/codex`の`ReviewTarget`、merge-base review、review-agent、Review JSON、fresh／detached context。
  - `chemitaro/spec-dock`のPlanning、Execution、Reviewer、PR Delivery、Workbench、Artifact import、Git同期preflight。
  - 現行SpecDockのInitiative／Epic／Issue workflow、Skill、Agent設定、Discussion template、PR #323。

## synthesis (必須)

### 現在の統合アーキテクチャ

```text
ChatGPT / GPT-5.6 Pro
├── Integrated Planning Bundle生成
├── Planning Review
├── Checkpoint Review
├── Issue Delivery Review
├── Epic Delivery Review
├── Targeted Review
├── Repair Batch生成
└── 高度な原因分析・小規模再設計・再計画

Codex Main Orchestrator
├── Workflow制御
├── target／context／authority解決
├── ChatGPT呼び出しと結果採否
├── Executor委任
├── diff／verification確認
├── commit／push
├── Node／dependency操作
├── PR Delivery制御
└── Human Gate管理

Executor
├── repository調査
├── Execution Tranche実装
├── test／verification
├── bounded repair
└── working treeへの変更

SpecDock Runtime
├── Node lifecycle
├── active scope
├── dependency
├── validate／sync
├── Workbench
└── 構造的・決定的なfile／metadata操作
```

### Current Effective Decision Set


## A. Initiative Goal・目的・横断原則

### D2-080

Initiativeの正式な出発点を`ChatGPT 5.6 Pro Delegation-First Workflow vNext`とする。Goalは、SpecDockのPlanning、Review、Repair、Execution、PR Deliveryを、ChatGPT 5.6 Proを高度認知層、Codexをオーケストレーションおよびrepository mutation層、SpecDock Runtimeを構造的・決定的処理層とするアーキテクチャへ一括移行し、既存Scopeとcanonical document形式との互換性を維持しながら、旧ChatGPT authoring evidence lane、manual planning fallback、ローカルReviewer Agent、過剰なstate／receipt／ledgerを廃止して、人間の認知コストとCodex token／quota消費を削減することである。Non-goalsは、既存Scope文書の一括変換、closed Scopeの書き換え、自動merge、GitHub Codex PR Reviewの即時廃止、汎用`chatgpt-use` Skillの再実装、`plan.md`／Review JSON／Repair BatchのRuntime parse、Oracle UI変更へ強く結合した作り込みである。

### D2-001

SpecDockの主要目的は、人間の承認gateを保ちながらPlanning、Execution、Review、Deliveryを徹底自動化し、人間の認知コスト、介入時間、Codex token/quota消費を削減することである。

### D2-002

高度な包括分析、設計、Planning、独立Review、Repair設計はChatGPTへ委譲し、repository mutation、filesystem操作、Runtime command、Git transactionはCodex側が担当する。

### D2-003

Main OrchestratorはEpic全体を1〜3日担当してよい。一方、具体実装はIssue単位のfresh Executorを基本とし、長寿命Mainと短命Workerでcontext rotを分離する。

### D2-004

Initiativeの作成判断とGoal定義は人間が所有する。Agentは候補の発見・提案までで、明示指示なしにInitiativeを作らない。

### D2-005

Initiative作成前workflowを厳密化しない。行き場のない一時資料にはroot Workbenchを利用できるが、専用Pre-Initiative stateやSkillは作らない。

### D2-006

親Planには子Epic/IssueのSeedだけを作り、詳細三文書は子Scope実行直前にJust-in-Time Planningする。子Nodeは依存関係管理のため親Planning承認後に作成する。

### D2-007

Seedと子Nodeの対応は名前と意味で行い、永続Seed ID、mapper、専用registryを作らない。

### D2-008

モデルや外部toolの変更に追従できることを資産とし、現在のモデル能力へ過度に最適化した複雑なRuntime、template parser、state machineを作らない。

## B. Planning・文書・Node materialization

### D2-009

Initiative/Epic/Issueの`requirement.md`、`design.md`、`plan.md`は、一つのChatGPT依頼・一つのfresh sessionで整合したBundleとして生成する。

### D2-010

ChatGPTはPlanning Bundleの完全なファイルを生成し、Codexは内容を書き直さず、出力を識別してcanonical pathへcopyする。

### D2-011

Identifyヘッダー、作成者、最終更新者、親ID等の重複情報を廃止する。Node関係はmetadataとdirectory structureから得る。

### D2-012

`plan.md`を人間・LLM共通のPlanning SSOTとし、`plan.json`、Plan parser、Review recipe、Planning receiptを作らない。

### D2-013

Planning Skillは文書生成だけでなく、ChatGPT生成、独立Review、P0/P1解消、人間の分割承認、Node作成、dependency登録、validate/syncまでを導くMain向けrunbookである。

### D2-014

GradeとReview TopologyはIntegrated Planning内でChatGPTがRequirement/Design/Planと一貫して決める。Grade別の巨大templateや機械的model routingは作らない。

### D2-015

Planning生成にはadversarial self-reviewを含める。Lite以外の正式Planning Reviewはfresh ChatGPT sessionで行い、P0/P1だけをblockingとする。P2/P3だけならPASSし文書を変更しない。

### D2-016

Human decomposition approval後に子Nodeをmaterializeする。親Planning Bundleを変更しない限り、Node作成だけを理由にPlanning Reviewをやり直さない。

### D2-017

Planning Bundleは実装変更と同一commitへ混ぜず、実装前に独立Planning commitを作る。PushはPlanning完了そのものの独立gateではなく、次のChatGPT呼び出しのGit同期preflightを通すために必要となる。

### D2-078

Initiative／Epic／Issueの3つの公開Planning Skillを維持し、vNext向けに全面改訂する。共通Planning mechanicsは`workflow_planning.md`へ集約し、旧`workflow_spec_authoring.md`は廃止・置換する。汎用`spec-dock-planning` SkillやPlanning Routerは作らない。

## C. `spec-dock-chatgpt`・Oracle・GitHub Context・Skill入口

### D2-018

ChatGPT操作はCore `spec-dock` CLIから分離し、独立CLI名を`spec-dock-chatgpt`とする。

### D2-019

Command hierarchyは能力領域と操作を明示する。主要形は`planning create/revise`、`review planning/checkpoint/delivery/targeted`、`repair-batch generate`とする。targetは明示指定し、Scope kindはmetadataから解決する。

### D2-020

全commandで`-c/--context`、`--context-file`、`--file`を利用できる。前二者はOperator Context、`--file`はGitHub外の補助資料であり、raw prompt overrideは公開しない。

### D2-021

`spec-dock-chatgpt`はOracle専用の薄いwrapperである。Git同期、target解決、prompt合成、Oracle起動だけを所有し、Browser、login、model picker、session、reattach、artifact保存はOracleへ委ねる。

### D2-022

Oracle invocationでは`--engine browser`を必ず固定し、model、ChatGPT Project URL、login、thinking time、timeout等は原則ローカルOracle configへ委ねる。正式workflowはfollow-upを使わずfresh one-shotとする。

### D2-023

ChatGPT処理前にnamed branch、clean working tree、upstream、local HEAD == remote HEADを機械確認する。自動commit/push/stash、Grade別例外、force bypassは作らない。

### D2-024

ChatGPTは`@GitHub`で指定repository、branch、exact HEAD SHAを必ず確認する。確認できなければPlanning/Review/Repairを行わず、default branchや添付、記憶で代替しない。

### D2-025

Git-tracked repository filesを自動添付しない。GitHubをRepository SSOTとし、promptにはtarget/parent/dependency/relevant pathを探索anchorとして渡す。GitHub外資料だけを明示添付する。

### D2-026

Oracle sessionの`prompt.md`、`response.md`、`log.jsonl`、`artifacts/`を実行記録の正本として利用し、wrapper独自`result.json`、stdout/stderr copy、artifact manifest、output-dir protocolを作らない。

### D2-027

Workbenchはprompt、Operator Context、Blocking Intake、候補artifact、長い診断の一時作業領域であり、Oracle outputのcopyは必要な場合だけ行う。workflow authorityにはしない。

### D2-028

汎用的なChatGPT相談はローカル`chatgpt-use` Skillを利用し、SpecDockには再実装しない。SpecDock側はPlanning/Review/Repair等の定型処理だけを提供する。

### D2-029

Oracle UI障害時もWorkflowを旧Codex-only方式へ戻さない。別browser操作、Codex browser、または人間のcopy/pasteで同じprompt/context/result contractを維持する。

### D2-030

Promptの大枠はRepository Source、Target Navigation、Task Contract、Operator Context、Explicit Attachments、Output Contractとするが、文章とtemplate engineeringは実装時のsmoke結果を踏まえて調整する暫定設計である。

### D2-075

共有`spec-dock-chatgpt-authoring` SkillとInitiative/Epic/Issueのmanual planning Skillsを削除する。Initiative/Epic/Issue Planning Skillが`spec-dock-chatgpt` CLIを直接利用し、Oracle/GitHub/Context/Artifactの共通契約は`workflow_chatgpt_delegation.md`へ集約する。

### D2-076

Formal Planning/Checkpoint/Delivery Review用の独立Skillは作らず、各Workflow Ownerが`spec-dock-chatgpt review ...`を直接利用する。ローカルの`spec-reviewer`、`code-reviewer`、`qa-reviewer` Agentとinstalled mirrorは削除するが、GitHub上のCodex PR Reviewは維持する。一方、ユーザーが任意対象とPerspectiveを直接指定する公開entrypointとして`spec-dock-targeted-review` Skillを設ける。このSkillはadvisory workflowであり、formal gate、Repair Batch起動、commit/push、finish権限を持たない。

### D2-077

Targeted Reviewの出力はFormal Reviewの`pass/fail`と分離したadvisory専用JSONとする。`assessment_status`は`completed`または`insufficient_evidence`を使用し、P0〜P3はfindingの重要度として保持するが、その結果だけでFormal Gate、Repair Batch、repository mutationを発生させない。

## D. Review Protocol・Scope・Perspective・Result

### D2-031

Formal Review ProtocolはPlanning、Checkpoint、Deliveryの3つ。Targeted Reviewはadvisoryでありformal gateを代替しない。Milestone Reviewという名称は廃止する。

### D2-032

Review ScopeはContract Owner、HEAD Snapshot、optional BASE..HEAD、Structural Anchors、Mutation Frontier、Semantic Expansionで定義する。Perspectiveは別軸とする。

### D2-033

Checkpoint/DeliveryはDelta-bounded Snapshot Reviewとする。BASE..HEADで変更面を特定し、HEADの最終状態を契約へ照合し、必要なcallers/tests/config/docsへImpact/Integration Closureする。

### D2-034

Planning ReviewはHEAD SnapshotでBASEなし。Checkpoint、Issue Delivery、Epic Deliveryは意味的なimmutable `--base-sha`を毎回明示し、HEADはcurrent synced HEADを自動使用する。PR-style Reviewだけmerge-baseを使う。

### D2-035

Review Requestは毎回self-containedとし、隠れたReview Stateに依存しない。BASE専用state、tracked receipt、custom Git refを作らず、喪失時はGit/Oracleから復旧し、不明ならより古い安全なBASEへ広げる。

### D2-036

Mutation Frontierはhard path boundaryではない。変更をseedに、具体的影響を証明するために必要な周辺範囲まで追跡するが、無関係なrepository全体監査は行わない。

### D2-037

Findingは今回のdeltaで導入・悪化・顕在化した問題、または今回のContract未達へ限定する。無関係な既存問題や一般改善案を報告しない。

### D2-038

PerspectiveはProtocolと分離し、spec、architecture、executability、code、qa、compatibility、security、operability、completion-summary等を必要に応じて合成する。選択されていないPerspective promptは渡さない。

### D2-039

`repository-conventions` Perspectiveを追加する。明示されたAGENTS.md、規約文書、formatter/linter設定等だけを評価し、規約がなければN/A。明示的MUST違反は原則P1、推奨違反はP2/P3またはfindingなし。

### D2-040

Review結果はProtocol固有JSONとする。Runtimeではparse/validateせずMainが解釈する。P0/P1があればFAIL、P2/P3のみならPASS、証拠不足・GitHub未確認ではPASSを禁止する。共通巨大Envelopeは作らない。

### D2-041

Fresh Reviewには前回finding、Authorの自己弁護、期待verdictを渡さない。修正後は修正版repository stateをfreshに評価する。

### D2-042

Issue Delivery ReviewとEpic Delivery Reviewを両方実施する。前者はIssue契約、後者はcross-Issue integrationとEpic契約を検証し、同一観点の重複reviewにしない。

### D2-043

ChatGPT Delivery ReviewとCodex PR Reviewは当面併用する。期限を固定せず実測で一本化または継続を判断する。

## E. Repair Batch

### D2-044

Repair BatchはPR固有ではなく、Checkpoint、Issue Delivery、Epic Delivery、PR/CI等のformal quality gateで発生したaccepted blocking setを処理する小規模な設計書兼実装計画書である。Planning Reviewは原則Planning Bundle Revisionで処理する。

### D2-045

branch mutationを伴うaccepted P0/P1、required CI failure、merge conflict等では原則ChatGPTにRepair Batchを生成させる。P2/P3のみ、false positive、no-change、human gateだけでは作らない。

### D2-046

CLIは`spec-dock-chatgpt repair-batch generate <execution-owner-issue>`一つだけとする。candidateの修正も追加context付きfresh generationで行い、create/reviseを分けない。

### D2-047

Repair BatchはSource HEAD/Blocking Cycleごとに一つのGit管理Artifactとして配置し、Executor開始前にfreezeする。実施結果、commit SHA、CI、再review結果は追記しない。

### D2-048

Repair Batchは上位Requirement/Design/Planに従属し、Scope、Requirement、Architecture、Public Contract、Review Topologyのmaterial変更が必要ならPlanningへ戻る。

### D2-049

Repair Batchの起動条件と修復後の復帰先はIssue Execution、Epic Execution/Delivery、PR Delivery等のWorkflow Ownerが所有する。共通詳細は`workflow_repair_batch.md`へ置き、独立Repair Batch Skillは作らない。

### D2-050

ChatGPT候補はMainが採用・棄却・partial-use判断を行い、採用済み内容だけをfreezeしてExecutorへ渡す。ChatGPT分析自体はrepair authorizationではない。

## F. Executor・Sub-agent・Model Policy

### D2-051

ExecutorはExecution TrancheまたはRepair Batchの意味的契約内で、Planに列挙されていない関連source/test/config/docs/mirrorも必要に応じて変更できる。materialな仕様・設計・Scope変更が必要なら停止する。

### D2-052

Executorの基本寿命はIssue単位。同一Issueのbounded review repairは原則同じExecutorへ戻し、Plan破綻・仕切り直し時だけfresh Executorへ切り替える。

### D2-053

Executorはcommit/pushしない。Mainがgit status/diff/verificationを確認し、report.mdを整えてcommit/pushし、正式Reviewを起動する。

### D2-054

Executor最終応答は薄いspineを持つ自由Markdownとする。専用JSON state/handoff fileを作らず、長い詳細だけWorkbenchへ退避する。

### D2-055

主要write agentはカスタムExecutor一つ。Docs専用agentは統合し、default Workerは非推奨のまま利用しない。

### D2-056

Read-only agentはbuilt-in Explorer、Researcher、Consultant、Deep Consultantを残す。Custom ExplorerとRepository Analystは削除し、ExplorerはCodex標準を無改変で使う。

### D2-057

Main Orchestratorのmodel/reasoningはユーザー環境が所有し、SpecDockは指定しない。Executorもmodel/reasoningを固定せず、Mainが必要時だけ明示overrideする。

### D2-058

ResearcherはGPT-5.6 Luna + 軽量Reasoning。ConsultantはGPT-5.6 SolでDeep Consultantより1段低いReasoning、Deep ConsultantはGPT-5.6 Sol + Max。Ultraは使わない。

### D2-059

Issue GradeはReview/Verification/Human Gateの強度であり、model/reasoningを自動選択する入力ではない。

## G. Issue／Epic Execution・Delivery・Finish

### D2-060

Epic PlanがDelivery Topologyを所有し、各Issue列のどこにDelivery Boundaryを置くか、どのIssueがDelivery Ownerかを明示する。per-Issue、Epic-wide、batch PRを表現できる。

### D2-061

Issue SeedにはExit expectationを、Issue `plan.md`には具体的なIssue Exit Contractを記述する。Invocation contextだけで実行時の終了境界を切り替えない。

### D2-062

Issue ExecutionはPlan-drivenなconditional end-to-end orchestratorである。Handoff ExitではDelivery Review後にIssue finishして次Issueへ、Merge ExitではPR Delivery、Human Merge Gate、merge確認後にIssue finishする。

### D2-063

`issue finish`と`epic finish`はPlan完了の構造的反映である。Merge Exitではmerge-preparedではfinishせず、人間がmergeし、reviewed headとの一致を確認してからfinishする。

### D2-064

Epic PlanはDelivery Owner Issueを明示する。小規模/単一Issue Epicでは通常Issueへ包含できるが、複数Issue・統合リスクのあるEpicでは専用Final Quality/Delivery Issueを推奨する。特殊Node型は作らない。

### D2-065

Delivery Owner Issueは既存Epic契約内のbounded integration/quality/PR repairを所有できる。新Scope、materialな要件/設計変更、独立workstreamはEpic Planningへ戻して新Issue化する。

### D2-066

PR Deliveryは一つの簡素なWorkflow Skillとして、PR作成/特定、CI/Codex Review観測、Blocking Set、Repair Batch、Executor修復、push、fresh ChatGPT Delivery Review、再観測、merge-preparedまでを所有する。旧Consultation state machineや巨大iteration ledgerは廃止する。

### D2-067

P2/P3だけを理由にbranch mutation、再CI、再Reviewを行わない。P0/P1とrequired CI failureだけをrepair scopeとする。

### D2-068

自動mergeは行わない。merge-preparedで人間に停止し、明示的な人間操作後にmerge状態を再取得する。

### D2-069

`report.md`は巨大Evidence Ledgerではなく、Issue/Epic完了時のFinal Completion Summaryと後続handoffを担う。Repair BatchやReview transcriptを全文転記しない。

## H. Workbench・Runtime State・変更耐性・Decision運用

### D2-070

Workbenchはrootおよび各ScopeのGit非管理一時領域として、prompt/context/candidate/external material/long diagnosticsに利用する。正本・lifecycle state・Review receiptにはしない。

### D2-071

Review receipt、Planning state、accepted HEAD registry、Checkpoint state、Repair iteration DB、custom Git refs等の新しい永続状態を作らない。状態喪失時はGit/GitHub/Oracleから再取得または広いfresh Reviewで回復する。

### D2-072

Runtimeは構造的で決定的な操作だけを担い、`plan.md`、Review JSON、Repair Batchの意味をparseしてgate判定しない。Main/ChatGPT/Codexが意味的に解釈する。

### D2-073

Prompt、model名、Oracle UI、Review schema等の可変部分を交換可能な薄い境界へ閉じ込め、変更容易性をSpecDockの主要価値とする。

### D2-074

Decision Registry自体もappend-onlyな誤解を避ける。改訂時は旧IDの状態と置換先を記録し、定期的にcurrent-effective registryを再生成する。

## I. vNext Cutover・既存Scope互換性

### D2-079

vNext導入は文書schemaやScope構造のmigrationではなく、全Scopeに対するWorkflow/Actorの一括cutoverである。既存Initiative/Epic/Issueの`requirement.md`、`design.md`、`plan.md`、`report.md`、artifactsを一括変換・再生成・編集しない。closed Scopeはhistorical artifactとして不変、open/active Scopeも既存canonical文書をそのまま利用して次の操作からvNext Workflowへ入る。vNextの次操作に必要なGrade、Review Topology、Exit Contract等が実際に不足する場合だけ、通常のPlanning gapとして対象Scopeを局所refreshする。旧Workflowとの並行運用、新規Scopeだけの段階導入、全open Scopeの事前refreshは行わない。


## 現在の標準Workflow

### Initiative Planning

```text
HumanがInitiativeとGoalを明示
→ Context／GitHub同期preflight
→ ChatGPTがInitiative requirement/design/planとEpic分解案を一括生成・セルフレビュー
→ Codexが内容不変でcanonical pathへ配置
→ Planning commit
→ fresh Planning Review
→ P0/P1ならPlanning Revision
→ HumanがEpic分解を承認
→ Epic Node／dependencyを作成
→ validate／sync
```

Initiativeを新設するかどうかはHuman authorityであり、Agentは候補提案までに留める。

### Epic Planning

```text
Epic target／parent Initiative確認
→ Context／GitHub同期preflight
→ ChatGPTがEpic Bundle、Issue Seeds、dependency、Delivery Topologyを生成
→ canonical配置／Planning commit
→ fresh Planning Review
→ P0/P1ならRevision
→ HumanがIssue分割を承認
→ Issue Node／dependencyを作成
→ validate／sync
```

Epic Planは、Issue実装順、Delivery Boundary、Delivery Scope、Delivery Owner Issue、Epic-level integration obligationsを所有する。

### Issue Planning

```text
Issue／parent Epic／Seed確認
→ Context／GitHub同期preflight
→ ChatGPTがIssue Bundleを生成
   - Grade
   - Execution Tranches
   - Checkpoint Review Topology
   - Verification obligations
   - Issue Exit Contract
→ canonical配置／Planning commit
→ Lite以外はfresh Planning Review
→ P0/P1ならRevision
→ execution-ready handoff
```

### Issue Execution

```text
Issue PlanのExecution Trancheを一つ選ぶ
→ Executorへ委任
→ Mainがworking tree／verificationを確認
→ commit
→ Planで必要な場合はpush
→ Checkpoint Review
   ├── PASS: 次Tranche
   └── FAIL(P0/P1): Repair BatchまたはPlanningへ戻る
→ 全Tranche完了
→ report.mdをFinal Completion Summaryとして完成
→ Issue Delivery Review
→ Issue Exit Contractを実行
```

### Epic Delivery

```text
各IssueがIssue-level Delivery Reviewを通過
→ Delivery Owner IssueがEpic-level integration／E2E／docs／parityを完了
→ Delivery Owner Issue自身のIssue Review
→ Epic Delivery Review
→ PR Delivery
```

Issue ReviewとEpic Reviewは異なるContract Ownerを検証し、相互の代替ではない。

### PR Delivery

```text
pre-PR ChatGPT Delivery Review PASS
→ PR作成／既存PR特定
→ CI＋GitHub Codex PR Review
→ blocking setを統合
→ Repair Batch生成・freeze
→ Executor修復
→ Mainがcommit／push
→ new HEADでfresh ChatGPT Delivery Review＋CI＋Codex Review
→ merge-prepared
→ Human Merge Gate
→ Humanがmerge
→ Mainがmerged PRとreviewed headを確認
→ issue finish／必要ならepic finish
```

P2／P3だけではbranchを変更しない。自動mergeは行わない。

## 現在のSkill／Agent／文書トポロジー

### 維持・全面改訂する公開Skill

```text
spec-dock-initiative-planning
spec-dock-epic-planning
spec-dock-issue-planning
spec-dock-issue-execution
spec-dock-epic-execution
spec-dock-targeted-review
PR Delivery Skill
```

### 削除するSkill／Agent

```text
spec-dock-chatgpt-authoring
spec-dock-initiative-planning-manual
spec-dock-epic-planning-manual
spec-dock-issue-planning-manual

local spec-reviewer
local code-reviewer
local qa-reviewer

custom Explorer
Repository Analyst
Docs Writer
旧default Worker利用経路
```

GitHub上のCodex PR Reviewは削除しない。

### 残すAgent

```text
built-in Explorer
custom Executor
Researcher
Consultant
Deep Consultant
```

### 新設・置換する共有文書

```text
workflow_planning.md
workflow_chatgpt_delegation.md
workflow_review.md
workflow_repair_batch.md

workflow_initiative.md   # vNextへ全面改訂
workflow_epic.md         # vNextへ全面改訂
workflow_issue.md        # vNextへ全面改訂
```

旧`workflow_spec_authoring.md`は`workflow_planning.md`へ置換する。

### 新設するCLI

```text
spec-dock-chatgpt
```

主要command:

```text
planning create
planning revise
review planning
review checkpoint
review delivery
review targeted
repair-batch generate
```

## Current Interface Contracts

### Supplemental Context

```text
-c / --context
→ 短いOperator Context

--context-file
→ UTF-8 Markdown／textをOperator Contextへ統合

--file
→ GitHub外の補助資料をOracleへ明示添付
```

tracked repository fileを自動添付しない。raw prompt overrideを公開しない。

### Formal Review

```text
Planning Review:
- HEAD Snapshot
- BASEなし

Checkpoint／Delivery:
- --base-shaを明示
- HEADはGitHub同期済みcurrent HEAD
- BASE..HEADをMutation Frontierにする
- HEADの最終状態をContractへ照合

PR-style:
- merge-baseを使用
```

### Review Gate

```text
P0/P1:
FAIL

P2/P3 only:
PASS

No findings:
PASS

GitHub／HEAD／必要証拠を確認できない:
PASS禁止
```

### Targeted Review

```text
assessment_status:
- completed
- insufficient_evidence
```

Targeted Reviewはadvisoryであり、Formal Gateやmutationを発生させない。

### Repair Batch

```text
Input:
accepted blocking set bound to a Source HEAD

Output:
frozen Markdown repair contract

Contains:
- Blocking Set
- Root-Cause Families
- Repair Design
- Allowed／Forbidden Scope
- Implementation Plan
- Validation／Re-review
- Stop／Escalation Conditions

Does not contain:
- implementation result
- commit SHA
- CI result
- fresh review result
```

## 既存Scopeへの適用

- vNextはdocument schema migrationではなく、Workflow／Actorの一括cutoverである。
- 既存のInitiative／Epic／Issue文書、Artifact、Workbench構造を一括変換しない。
- open／active Scopeも次の操作からvNext Workflowを使用する。
- 次の操作に必要なGrade、Checkpoint、Exit Contract等が本当に不足する場合だけ、通常のPlanning gapとして対象Scopeを局所refreshする。
- 旧Workflowとの並行運用、新規Scopeだけへの限定導入、全open Scopeの事前refreshを行わない。

## 選択肢 / tradeoff (必須)

- Current Snapshot方式:
  - Pros:
    - 実装Agentは現行規則だけを読める。
    - 旧案、改訂注記、legacy mappingに迷わない。
    - Initiative Planningの直接入力として利用できる。
  - Cons:
    - 変更履歴の確認には別の会話ログ／audit evidenceが必要。
- Incremental Registry方式:
  - この文書では採用しない。履歴と現行authorityが混在し、古い案を実装する危険がある。
- 採用:
  - Current Snapshot方式。履歴は本文外のaudit evidenceへ分離する。

## reflection proposal (必須)

- canonical docs／workflow／template／skill guidanceへ反映すべき内容:
  - 本文のInitiative GoalとNon-goalsをInitiative `requirement.md`へ反映する。
  - Actor responsibility、CLI、Review Scope、Repair Batch、Delivery Topologyを`design.md`へ反映する。
  - Skill／Agent／Workflow／Script inventoryと移行順を`plan.md`へ反映する。
  - 長期的に安定する境界だけをADRへ分離する。
- この文書がまだDiscussionである理由:
  - 対象Initiative Nodeとcanonical Planning Bundleがまだ作成されていない。
  - CLI argv、prompt本文、Protocol別JSON schema、Oracle live behaviorは実装時検証が必要。

## adoption target / 採用先候補 (必須)

- `requirement.md`:
  - Initiative Goal／Non-goals。
  - Human Gate、GitHub fail-closed、ChatGPT／Codex／Runtime責務。
  - Formal Review、Repair Batch、Delivery、cutoverの必須結果。
- `design.md`:
  - `spec-dock-chatgpt`、Oracle adapter、Context、Review Protocol、Agent／Skill topology。
  - Delta-bounded Snapshot Review、Repair Batch、Issue Exit Contract、Delivery Owner。
- `plan.md`:
  - 現行asset inventory。
  - provider／installed／dogfood mirror。
  - 削除／改訂／新設順序。
  - live smoke、Protocol JSON安定性、dual-review評価。
- `ADR`:
  - ChatGPT／Codex／Runtime responsibility boundary。
  - Oracle thin-wrapper boundary。
  - Review Scope model。
  - Repair Batch as frozen subordinate contract。
  - Plan-driven Delivery Topology／Issue Exit Contract。
- `report.md`:
  - Final Completion Summaryの導入と旧Evidence Ledgerの除去結果。

## ADR triage / ADR candidate triage (必須)

- ADR candidateか:
  - yes。単一巨大ADRではなく、長期境界ごとに分ける。
- hard to reverse:
  - yes。Actor、Review、Delivery、Skill topologyへ横断的影響がある。
- surprising without context:
  - yes。Issue finishとmergeの関係、Repair Batchの従属性、GitHub exact HEAD、Runtime非parse方針は説明が必要。
- real tradeoff:
  - yes。自動化対Human Gate、fresh review対cost、永続Repair Contract対state肥大化のtradeoffがある。
- ADR化しないもの:
  - model label、prompt wording、Oracle selector、可変JSON field等はDesign／Skill guidanceに留める。

## 推奨案 (必須)

- 本Current Effective Decision Snapshotを、Initiative Planningと実装inventoryの唯一のDiscussion authorityとして利用する。
- 過去のDecision一覧、改訂履歴、legacy mappingを実装Agentへ渡さない。
- 次の工程では、このSnapshotを入力にInitiativeのRequirement／Design／PlanとEpic分割を生成する。

## 推奨反映先 (必須)

- `requirement.md`:
  - Goal、Non-goals、必須Workflow結果、互換性、Human Gate。
- `design.md`:
  - Actor、CLI、Oracle、Review、Repair、Skill／Agent、State boundary。
- `plan.md`:
  - inventory、Epic分割、dependency、cutover sequence、verification。
- `ADR`:
  - 長期境界だけを選別。
- `report.md`:
  - Initiative実装の最終Completion Summary。

## 未採用 / deferred 理由 (必須)

- 未採用:
  - 旧案と改訂案を同じ本文へ併記する方式。
  - legacy D番号を実装authorityとして参照する方式。
  - current Decisionごとに`active`／`revised`状態を残す方式。
- deferred:
  - `spec-dock-chatgpt`の正確なargv／exit code／config precedence。
  - Protocol別promptとJSON schema。
  - `report.md`の最終template。
  - PR Delivery Skillの詳細なpoll／repair implementation。
  - Oracle＋`@GitHub` exact branch／SHA live smoke。
  - Codexが受理する最終model label／reasoning enum。

## 次アクション (必須)

- 本SnapshotをInitiative Planningの入力とする。
- Initiative `requirement.md`、`design.md`、`plan.md`を生成し、Epicへ分割する。
- Initiative Planning内で、現行Skill／Agent／Workflow／Template／Scriptの完全inventoryを作る。
- 実装前に、Oracle＋`@GitHub` exact branch／SHA、生成file、Protocol JSONをlive smokeする。
