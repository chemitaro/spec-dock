---
種別: ADR（Architecture Decision Record）
ID: "20260721t161956z-17-adr"
artifact_type: "adr"
タイトル: "Planning Workflow capabilityの実装IssueとPlanning lifecycle活動を分離する"
状態: "accepted"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-22"
親: ["init-00322"]
authority: "accepted"
accepted_authority: "Human Gate clarification in the init-00322 planning discussion"
accepted_at: "2026-07-22"
accepted_by: "Human"
mirror_eligible: true
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/artifacts/20260721t161956z-17-adr-planning-workflow-capability-implementation-is-not-downstream-planning.md"
derived_from:
  - "Candidate v8 independent Red-Team Formal Review PASS"
  - "Human Gate clarification after Candidate v8 Review"
  - "ADR 10〜12"
reflected_to:
  - "initiative/requirement.md"
  - "initiative/design.md"
  - "initiative/plan.md"
  - "epics/planning-and-advisory-review/requirement.md"
  - "epics/planning-and-advisory-review/design.md"
  - "epics/planning-and-advisory-review/plan.md"
  - "MATERIALIZATION-MAP.md"
  - "NODE-MATERIALIZATION-MAP.json"
---

# Planning Workflow capabilityの実装IssueとPlanning lifecycle活動を分離する

## 位置づけ

Candidate v8はFormal ReviewをPASSしたが、Human Gateで`Issue Planning End to End`が「他IssueをPlanningするための専属Issue」とも読める曖昧さが発見された。本ADRは、PlanningのLifecycle activityと、その活動を可能にするSpecDock product capability implementationを分離する。

## ADR 化基準

- hard to reverse: yes。Issue boundary、title、Prompt、acceptance evidence、materialization identityへ影響する。
- surprising without context: yes。SpecDock自身がPlanning機能を開発するため、Planningを行う活動とPlanning機能を実装する作業が同じ語で表現される。
- real tradeoff: yes。名称と契約を冗長に明示する代わりに、Human／Codex／Reviewerの誤解と上位Portfolio driftを防ぐ。

## 結論（Decision）

1. Initiative／Epic PlanningはHuman Portfolio Approval前の現在工程で行う。implementation Issue内で再実施または再設計しない。
2. Issue Planningは各Issue開始時に、そのIssue自身へJITで行う。
3. 他IssueのPlanningを代行するためだけのIssueを作成しない。
4. SpecDockがPlanning機能を開発する場合、IssueはPlanning活動ではなく、再利用可能なPlanning／Review Workflow capabilityの実装を成果とする。
5. Planning capability implementation Issueのtitleは`Implement ... Workflow`形式を優先し、実装対象であることをself-describingにする。
6. 主要成果はcode、Skill、Prompt、adapter、tests、docs、provider／installed／dogfood projectionである。実際のPlanning runはAcceptance Evidenceであり主成果ではない。
7. E1-I1〜E1-I3はそれぞれIssue-localに、current Portfolio replanning、downstream Issue Requirement／Design／Plan pre-authoring、Human approval bypass、Planning-only completionを禁止する。
8. materialなPortfolio gapを発見した場合、下位Issue内で修正せず、上位Planningへescalateする。
9. Formal ReviewはtitleだけでなくOutcome、Non-goals、Acceptance Evidenceを検査し、「Planningを行うIssue」と「Planning Workflowを実装するIssue」の混同をP1として扱う。

## 背景（Context）

LLMは与えられた名詞を深掘りして整然と完成させる傾向がある。`Issue Planning End to End`という名称は、文脈を十分に読めばWorkflow capabilityにも解釈できるが、Human GateではPlanning専属Issueと解釈された。Codexも同じprimary identifierをbranch、GitHub Issue、handoff、reportで繰り返し参照するため、文脈推論へ依存するべきではない。

## 選択肢（Options considered）

### 名称を維持し、本文だけで説明する

モデルが全文を正しく読むことへ依存し、GitHub title、branch、一覧表示では曖昧さが残るため不採用。

### Planning関連Issueを削除する

SpecDockにはPlanning Workflow自体を実装するproduct requirementが存在するため不採用。

### `Implement ... Workflow`へ改称し、境界を全文書へ反映する

採用。既存のvertical capability boundaryを維持しつつ、planning activityとの混同を除去できる。

## 判断理由（Rationale）

Issue titleは単なる表示名ではなく、Human、Codex、GitHub、Runtime、Review、handoffが共有する一次interfaceである。重要な責務境界を文脈推論だけに依存させず、名称、Outcome、Non-goals、Evidenceを一致させる方が安全である。

## 影響（Consequences）

### Positive

- Human／CodexがIssueをPlanning専属作業と誤解しにくい。
- 現PortfolioとJIT Issue Planningのauthorityが維持される。
- Dogfoodとproduct outputの主従が明確になる。
- Planning-related Issueのimplementation diffをReviewしやすい。

### Negative／Debt

- titleとsemantic keyの変更により新Candidate versionとfresh Reviewが必要になる。
- Issue titleがやや長くなる。
- 将来Planning capabilityを追加する際も同じ命名／Non-goal disciplineが必要になる。
