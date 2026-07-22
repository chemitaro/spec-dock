---
種別: ADR（Architecture Decision Record）
ID: "20260720t080853z-10-adr"
タイトル: "Outcome-Oriented Vertical Slicing and Per-Issue Merge Boundaries"
状態: "accepted"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-20"
親: ["init-00322"]
authority: "accepted"
accepted_authority: "human"
accepted_at: "2026-07-20"
accepted_by: "Human"
mirror_eligible: true
derived_from:
  - "Initiative Planning dogfooding and over-decomposition analysis"
reflected_to:
  - "spec-dock-initiative-planning"
  - "spec-dock-epic-planning"
  - "spec-dock/docs/workflow_planning.md"
  - "spec-dock/docs/workflow_initiative.md"
  - "spec-dock/docs/workflow_epic.md"
artifact_type: "adr"
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/artifacts/20260720t080853z-10-adr-outcome-oriented-vertical-slicing-and-per-issue-merge-boundaries.md"
---

# Outcome-Oriented Vertical Slicing and Per-Issue Merge Boundaries

## 位置づけ

このADRは、SpecDock自身とSpecDock導入先の双方で、InitiativeをEpicへ、EpicをIssueへ分割する際の標準原則を定める。Dogfood、技術レイヤー、工程、品質活動を分割軸にせず、Actorが完了できるOutcomeと独立merge／rollback境界を分割軸とする。

## ADR 化基準

- hard to reverse: yes。Planning、Node数、PR数、dependency、Review、delivery、Human介入へ横断的に影響する。
- surprising without context: yes。Foundation、QA、Metrics、Dogfood等を原則Issueにせず、Outcome Issueへ含める。
- real tradeoff: yes。Issueを大きめのvertical sliceへ統合する代わりに、MilestoneとExecution Briefで内部複雑性を管理する。

## 結論（Decision）

1. Epicは、完了後に特定Actorが一つの新しい能力・業務成果・運用成果をend-to-endで受け入れられる単位とする。
2. Issueは、必要最小限の独立merge可能なvertical sliceとする。
3. implementation Issueは原則1 branch／1 PR／required CI・Review／Human merge／merged HEAD確認／finishとする。
4. Epic単位のaggregate PRをdefaultにしない。全Issue merge後、default branch上でEpic Delivery Reviewを行う。
5. Foundation、technical layer、schema、registry、tests、QA、Docs、Metrics、Dogfood、Inventory、Packagingを、それだけで独立Epic／Issueにしない。
6. 必要なcode、tests、docs、config、packaging、migration、real-use validationをOutcome Issueへ含める。
7. DogfoodはSpecDock自身を開発するときのRepresentative Real-Use Validationの一例であり、Epicの定義ではない。
8. Issue内部の複雑性はMilestone、Execution Unit、Architecture-Aware Execution Briefで管理する。
9. 固定のEpic数／Issue数を目標にせず、必要条件を満たす範囲で少ない境界を優先する。
10. Horizontal sliceは、独立risk、検証可能な完成状態、current consumer、no-dead-surface、rollback／review safetyをすべて満たす例外に限定する。
11. 事前Final QA Issueをdefaultにせず、Epic Reviewで実装修正が必要な場合だけJIT bounded Issueを作る。

## 背景（Context）

モデルは対象を綺麗に整理すると、Foundation、CLI、Backend、Metrics、Docs、QA等の技術分類をEpic／Issueへ変換しやすい。その結果、各PRの利用価値が小さくなり、依存、handoff、Review固定費、Human介入が増える。SpecDockのPlanningは、整理の美しさではなく、merge後のOutcomeを分割品質の基準にする必要がある。

## 選択肢（Options considered）

### 技術レイヤー／工程別分割

理解しやすいが、horizontal Issue、dead surface、過剰PRを生むため棄却。

### 固定Issue数heuristic

簡単だがEpicごとの必要性を表せず、過剰分割／under-slicingの双方を起こすため棄却。

### Outcome-oriented vertical slicing

独立価値、Review、rollback、per-Issue PRと整合するため採用。

## 判断理由（Rationale）

PR固定費を正当化するのは内部部品ではなく、独立したOutcomeまたはrisk boundaryである。vertical sliceはcode、tests、docs、distributionを一つの価値境界へ戻し、MilestoneとExecution Briefにより実装可能性も維持できる。

## 影響（Consequences）

- Planning PromptとReviewへSlicing Contractを追加する。
- Issue数は減る傾向にあるが、Issue内部PlanとExecution Briefの質がより重要になる。
- Epic Reviewはaggregate PRではなくdefault branch上で実行する。
- SpecDock自身のdogfoodと導入先のreal-use validationを共通概念で扱える。
