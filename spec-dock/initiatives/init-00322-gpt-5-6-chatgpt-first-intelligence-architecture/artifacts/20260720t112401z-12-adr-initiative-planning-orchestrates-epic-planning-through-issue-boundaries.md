---
種別: ADR（Architecture Decision Record）
ID: "20260720t112401z-12-adr"
タイトル: "Initiative PlanningでEpic PlanningをオーケストレーションしIssue境界まで確定する"
状態: "accepted"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-20"
親: ["init-00322"]
関連:
  - "20260720t080853z-10-adr-outcome-oriented-vertical-slicing-and-per-issue-merge-boundaries"
  - "20260720t080853z-11-adr-prompt-embedded-slicing-contract-and-decomposition-quality-review"
authority: "accepted"
accepted_authority: "human"
accepted_at: "2026-07-20"
accepted_by: "Human"
mirror_eligible: true
derived_from:
  - "Initiative Planning dogfooding through 2026-07-20"
  - "Human decision: Initiative Planning must concretize every Epic through actual Issue boundaries"
reflected_to:
  - "spec-dock-initiative-planning"
  - "spec-dock-epic-planning"
  - "spec-dock/docs/workflow_planning.md"
  - "spec-dock/docs/workflow_initiative.md"
  - "spec-dock/docs/workflow_epic.md"
  - "spec-dock-chatgpt planning create"
  - "spec-dock-chatgpt review planning"
artifact_type: "adr"
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/artifacts/20260720t112401z-12-adr-initiative-planning-orchestrates-epic-planning-through-issue-boundaries.md"
---

# Initiative PlanningでEpic PlanningをオーケストレーションしIssue境界まで確定する

## 位置づけ

このADRは、InitiativeをPlanningするときに、Initiative直下のEpic名・Outcome・依存関係だけを決めて終了するのではなく、**各Candidate EpicをEpic-level Requirement／Design／Planまで具体化し、そのEpic Planから実際の作業単位となるIssue境界まで投影した上で、Initiative全体のEpic分割を確定する**ことを定める。

本Decisionは、Initiative文書をEpicやIssueの詳細で肥大化させることを意味しない。Initiative PlanningというオーケストレーションWorkflowの分析範囲を、Epic PlanningおよびIssue Boundary Projectionまで拡張するものである。

Issueの完全な`requirement.md`、`design.md`、`plan.md`、Milestone、Execution Unit、テストケース、実装詳細は引き続きJust-in-Timeで作成する。

## ADR 化基準

- hard to reverse: yes。Initiative Planning、Epic Planning、Node materialization、Human Gate、Planning Review、Prompt compositionへ横断的に影響する。
- surprising without context: yes。Initiative文書を薄く維持しながら、Initiative Planning Workflow自体は全Epic BundleとIssue境界まで作るため、文書責務とWorkflow責務を分けて理解する必要がある。
- real tradeoff: yes。upfrontのChatGPT分析量、文書数、Review負荷は増えるが、過剰Epic、横スライスIssue、価値の低いPR、Humanの逐次修正介入を削減できる。

## 結論（Decision）

### 1. Initiative Planningの完了条件

Initiative Planningは、次がすべて揃うまで完了としない。

```text
1. Thin Initiative Requirement／Design／Plan
2. Candidate Epic Portfolio
3. 各Candidate EpicのRequirement／Design／Plan
4. 各Epic Plan内のIssue Boundary Map／Issue Seeds
5. cross-Epic dependency map
6. cross-Issue dependency map
7. Portfolio Consolidation Review
8. decomposition-qualityを含むfresh Planning Review
9. Human Portfolio Approval
10. 承認済みEpic／Issue Nodeとdependencyのmaterialization
```

Initiative Planningは、Epicの名前を付けただけ、またはEpic Seedを作っただけでは完了しない。

### 2. Initiative文書は薄く維持する

Initiativeのcanonical三文書は、次だけを所有する。

#### Initiative `requirement.md`

- Initiative Goal。
- Why now。
- Initiative-level Scope／Non-goals。
- cross-Epic constraints。
- Initiative-level Acceptance Criteria。
- Human Gate。
- Initiative completion条件。

#### Initiative `design.md`

- cross-Epic Actor／authority境界。
- cross-cutting architecture decisions。
- Capability Map。
- Epic間責任境界。
- Slicing Contract。
- Initiative-level compatibility／cutover方針。

#### Initiative `plan.md`

- 最終Epic Portfolio。
- Epic Outcome／Acceptance Boundary。
- Epic間dependency。
- Portfolio-level Review／Human Gate。
- Epic／Issue materialization方針。
- Initiative完了順序。

Initiative文書へ、Epicの詳細Design、Issue Seed全文、file単位変更、test case、Milestone、Execution Unitを転記しない。

### 3. 各Epicを完全なEpic Bundleまで具体化する

Initiative Planning Workflowは、各Candidate Epicについて、Epic Planningと同じ意味契約を用いて次を作る。

```text
Epic requirement.md
Epic design.md
Epic plan.md
```

Epic Bundleは、Issue境界を判断できる十分な深さを持つ。

#### Epic Requirementが定義するもの

- Actor／Beneficiary。
- Epic完了後のObservable Outcome。
- Scope／Non-scope。
- Acceptance Criteria。
- 外部依存。
- Risk／rollback boundary。

#### Epic Designが定義するもの

- architecture／responsibility boundary。
- cross-Issue interface。
- state／error／compatibility boundary。
- Review／Delivery boundary。
- 他Epicとのcontract。

#### Epic Planが定義するもの

- actual Issue Seeds。
- Issue間dependency。
- 各IssueのObservable Outcome。
- 各Issueの独立PR／merge boundary。
- 各Issueが独立Issueである理由。
- Epic Delivery ReviewとEpic finish条件。

Epic Bundleでは、Issue内のfile、class、関数、詳細test case、Milestone、Execution Unit、具体的なExecutor sequenceを固定しない。

### 4. Issue Boundary ProjectionをEpic境界の検証に使う

各Issue Seedは、最低限次を示す。

```text
- Actor／Beneficiary
- merge後に成立するObservable Outcome
- end-to-endで含む責務
- 独立PR／Review／rollback boundaryが必要な理由
- dependency
- acceptance evidence
- なぜ隣接IssueのMilestoneではなく独立Issueなのか
```

Issue Seedを作る目的は、下流作業を整理することだけではない。Issue構造を使って、上位Epic境界を逆検証する。

次が見つかった場合は、Issueをさらに細かく整理するのではなく、Epic Portfolioへ戻る。

```text
- IssueがCLI、schema、backend、tests、docs、QA等のhorizontal sliceになる
- Issue単体をmergeしても利用可能なOutcomeがない
- Issue間dependencyが不必要に直列化する
- 一つのEpicに複数の独立能力が混在する
- 隣接Epicが同じIssue責務を重複して持つ
- Foundation／Metrics／Dogfood／QA等が独立Epicまたは必須Issueになる
- Issue数を増やしてもActor Outcomeが明確にならない
```

この場合、Epicを統合、分割、再定義し、全Epic BundleとInitiative Bundleを再整合する。

### 5. Minimum Sufficient Decompositionを適用する

初期仮説は次とする。

```text
Initiative → まず1 Epicとして考える
Epic       → まず1 Issueとして考える
```

独立したCapability、Acceptance Boundary、Risk Boundary、Rollback Boundary、Dependency、Human Decision Boundaryがmaterialに必要な場合だけ分割する。

固定のEpic数・Issue数を目標にしない。必要条件を満たす範囲で、Epic数・Issue数・PR数・dependency edge・handoffを少なくする。

### 6. Epic Planningの単独意味契約は変更しない

`spec-dock-epic-planning`が単独で実行されるときの出力責務は変更しない。

Initiative Planningは、各Candidate Epicについて同じEpic Planning capabilityを内部的にオーケストレーションする。ただし、Portfolio全体を確定する前に、各Epicごとの独立Human GateやNode materializationを順次実行しない。

推奨するオーケストレーションは次である。

```text
Initiative candidate
→ Epic Bundle candidates × N
→ Issue Boundary Projection × N
→ Portfolio Consolidation
→ fresh Review
→ one Human Portfolio Approval
→ Epic／Issue Nodesとdependenciesを一括materialize
```

これにより、Epic 1を承認・materializeした後にEpic 2との境界問題が発覚することを防ぐ。

### 7. Issue NodeはPortfolio承認後にmaterializeする

Issueの詳細PlanningはJITで行うが、Issue境界、Issue Outcome、dependencyはInitiative Portfolio Approval時点で承認済みとする。

Human承認後、Main Orchestratorは次をmaterializeする。

```text
- Epic Nodes
- Issue Nodes
- Epic dependencies
- Issue dependencies
```

Issue Node作成時に完全なIssue三文書は要求しない。Issue SeedをNodeへ対応付け、Issue開始直前に`spec-dock-issue-planning`で完全Bundleを生成する。

実装状況の変化によってIssue境界へmaterialな変更が必要になった場合は、該当Epic Planをamendし、decomposition-qualityを含むfresh Epic Planning Reviewと必要なHuman approvalを行う。通常のJIT Issue Planningで無断resliceしない。

### 8. Human GateはPortfolio単位で一度にする

Humanへは次を統合して提示する。

```text
- Initiative Goal／Non-goals
- Final Epic Portfolio
- Epic Bundle × N
- Issue Boundary Map × N
- Epic／Issue dependency graph
- per-Issue PR boundaries
- Consolidation rationale
- decomposition-quality Review result
```

Humanは、Initiative、Epic境界、Issue境界、dependency、Delivery Policyを一度のPortfolio Approvalで承認する。

HumanがEpicごと、Issueごとに「細かすぎる」「これはIssueではない」と逐次修正し続けることを標準Workflowにしない。

### 9. Formal Planning Reviewの対象を拡張する

Initiative Planning Reviewは、Initiative三文書だけでなく次を入力とする。

```text
- Initiative Bundle
- 全Epic Bundles
- 全Issue Seeds／Issue Boundary Maps
- Epic／Issue dependency graph
- Consolidation rationale
```

必須Perspective:

```text
- specification
- architecture
- executability
- decomposition-quality
- repository-conventions（適用規約がある場合）
```

`decomposition-quality`は次を検査する。

```text
- Initiative文書がEpic詳細を吸収して肥大化していないか
- EpicがCapability／Outcome単位か
- Issueがverticalか
- Issue merge後にObservable Outcomeがあるか
- IssueがPR固定費を正当化するか
- 隣接Epic／Issueを統合できないか
- Foundation／QA／Metrics／Dogfood／Inventory等を独立sliceにしていないか
- Issue境界検証後にEpic Portfolioを再評価しているか
- Issue詳細をJITの範囲を超えて先取りしていないか
- 逆にIssueが巨大すぎてReview／rollback不能でないか
```

### 10. ChatGPT Promptへ階層別Depth Contractを含める

モデルへ単に「浅く書く」と要求しない。どの階層で何を深掘りするかを明示する。

```text
Initiative:
- Goal、Capability Portfolio、cross-Epic boundaryへ深く考える
- file、test case、Issue Milestoneへ入らない

Epic:
- Actor Outcome、architecture boundary、Issue boundaryへ深く考える
- exact implementation、file変更、詳細test caseへ入らない

Issue:
- Requirement、Design、Execution Tranche、test obligation、Exit Contractへ深く考える

Execution Brief:
- exact HEAD、concrete tests、implementation strategy、stop conditionへ深く考える
```

Initiative Planning Promptは、Candidate Epicを列挙して終了せず、各EpicをIssue境界まで投影し、その結果でPortfolioを再構成することを要求する。

## 背景（Context）

SpecDock自身によるInitiative Planningのdogfoodingでは、Initiative段階で詳細設計を深掘りし、その内容を工程・技術レイヤー別Epicへ分割し、さらにEpicをcomponent別Issueへ分割した。その結果、Inventory、CLI Skeleton、Binding、Metrics、Distribution、Final QA等の低価値なhorizontal Issue候補が増えた。

一方、Initiativeを薄く保ち、Epic名だけを決めてEpic Planningを完全にJITへ送る方式では、HumanがEpicごとに過剰分割を修正する必要があり、Initiative全体の統合性を事前に検証できない。

言語モデルは、与えられた対象を深く整理することは得意だが、上位Scopeで自発的に深さを止め、下位境界へフィードバックすることは安定しない。そのため、モデルの深掘り能力を抑制するのではなく、Initiative、Epic、Issue、Execution Unitごとに深掘り対象を明確に配分する必要がある。

ChatGPTはarchitecture review、境界分析、test strategy、synthesis、plan review等の高深度分析へ利用できるため、各Epic BundleとIssue Boundary Projectionを作り、Portfolio Integratorとして再評価する認知処理に適している。

## 選択肢（Options considered）

### Option A — Thin Initiative BundleとEpic Seedだけを作り、Epic Planningを完全JITにする

- 将来Epicを過剰設計しにくい。
- Initiative承認時点でIssue境界が見えず、Epic間重複、horizontal Issue、過剰分割を検出しにくい。
- HumanがEpicごとに同じSlicing修正を繰り返す。
- 棄却。

### Option B — Initiative三文書へ全Epic・Issue詳細を埋め込む

- 一つの文書群で全体を確認できる。
- Initiative文書が巨大化し、Epic文書と重複し、authorityが曖昧になる。
- 将来Epicの設計が陳腐化しやすい。
- 棄却。

### Option C — Initiative Planningが各Epic BundleとIssue境界を作り、Portfolioを統合Reviewする

- Initiative文書を薄く維持できる。
- Epicの詳細分析能力を使える。
- Issue ProjectionでEpic境界を検証できる。
- Issue詳細はJITへ残せる。
- 採用。

### Option D — Initiative Planningで全Issueの完全三文書とMilestoneまで作る

- 初期時点では詳細な全体計画を得られる。
- future HEAD、先行Issueの実装結果、実際のtest seamを予測して固定するため陳腐化と過剰設計が大きい。
- Issue PlanningとExecution Briefの責務を奪う。
- 棄却。

## 判断理由（Rationale）

1. Issue境界を作らなければ、Epicが本当にCapability単位か検証できない。
2. Issue詳細まで作ると、将来状態を先取りしすぎる。
3. Initiative文書へEpic詳細を入れると、authorityと変更範囲が肥大化する。
4. Epic Bundleを独立文書として作れば、階層ごとのSSOTを維持できる。
5. Portfolio横断Reviewにより、モデルが各Epicを局所最適化することを防げる。
6. 一度のHuman Portfolio Approvalで、Humanの逐次Slicing介入を減らせる。
7. Issue Nodesとdependencyを早期materializeすることで、SpecDockの実装順管理能力を利用できる。
8. Issueの完全PlanningをJITに残すことで、最新HEADと先行成果を利用できる。

## 影響（Consequences）

### Positive

- Initiative全体のEpic／Issue境界を実装前に統合検証できる。
- 過剰Epic、horizontal Issue、future-only foundation、QA／Metrics／Dogfood専用Issueを減らせる。
- Humanの「細かすぎる」という逐次介入を標準Workflowから除去できる。
- Issue dependency graphを早期に管理できる。
- モデルの深掘り能力を階層ごとに適切な対象へ配分できる。
- Issue詳細をJITへ残し、現在HEADによる具体化を維持できる。

### Negative／Cost

- Initiative Planning時のChatGPT call、生成文書、Review量が増える。
- 複数Epic BundleとIssue Seedの整合管理が必要になる。
- Human Portfolio Approvalの確認量が増える。
- 将来EpicのIssue境界が実装時に変わる可能性があり、amendment手順が必要になる。
- Main Orchestratorはcandidate Bundle、Portfolio Integration、materializationをatomicに扱う必要がある。

### Risks and mitigations

- Risk: Initiative Planningが全Issue詳細まで深掘りする。
  - Mitigation: Issue Seedの必須項目と禁止詳細をPromptへ明示する。
- Risk: 将来EpicのBundleが陳腐化する。
  - Mitigation: Epic開始前にReadiness Checkを行い、material差異だけをamendする。
- Risk: Initiative文書とEpic文書に重複する。
  - Mitigation: InitiativeはPortfolio、EpicはCapability Design、IssueはJIT implementation contractとauthorityを分離する。
- Risk: Human Gateが重くなる。
  - Mitigation: Portfolio Map、Issue Boundary Map、Consolidation Rationaleを要約面として提供する。
- Risk: Node materialization後に境界変更が発生する。
  - Mitigation: material変更時だけEpic Plan amendment、fresh decomposition-quality Review、Human approvalを要求する。

## 運用上の必須変更

- `spec-dock-initiative-planning`を、Epic Seed生成だけでなくEpic Bundle／Issue Boundary Projection／Portfolio Consolidationまで行うorchestratorへ改訂する。
- `spec-dock-epic-planning`の単独責務は維持する。
- `workflow_planning.md`へ階層別Depth Contractを追加する。
- `workflow_initiative.md`へPortfolio Planningと一括Human Gateを追加する。
- `workflow_epic.md`へIssue Boundary Mapと「IssueではなくMilestoneではない理由」を追加する。
- Planning PromptへPortfolio Consolidation Contractを追加する。
- Initiative Planning Reviewへ全Epic Bundle／Issue Seedsを入力し、`decomposition-quality`を必須化する。
- Initiative承認後にEpic／Issue Nodesとdependenciesを一括materializeする。

## 検証シナリオ

1. 一つの能力しかないGoalでは、Initiative Admission Testが失敗し、Epic Planningへrouteされる。
2. 複数Candidate EpicをIssueへ投影した結果、horizontal IssueだけになるEpicは統合または再定義される。
3. Issue Seedにfile／class／test case詳細が混入した場合、decomposition-quality ReviewがFAILする。
4. 隣接Issueを統合してもOutcome／Review／rollback境界を失わない場合、Consolidation Reviewが統合を要求する。
5. Human Portfolio Approval後、Epic／Issue Nodesとdependencyが一括materializeされる。
6. Issue開始時は完全BundleをJIT生成し、Initiative Planning時のSeedをそのまま実装計画として使わない。
7. Epic開始前にmaterialな前提変更がある場合、Epic Plan amendmentへrouteされる。

## 参照（References）

- ADR 10: Outcome-Oriented Vertical Slicing and Per-Issue Merge Boundaries。
- ADR 11: Prompt-Embedded Slicing Contract and Decomposition Quality Review。
- Local `chatgpt-use` guidance: high-depth architecture review、boundary analysis、test strategy、synthesis、plan reviewをChatGPTへ委譲する方針。
