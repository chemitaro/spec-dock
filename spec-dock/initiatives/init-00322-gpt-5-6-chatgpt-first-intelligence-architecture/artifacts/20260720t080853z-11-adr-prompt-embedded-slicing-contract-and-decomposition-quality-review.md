---
種別: ADR（Architecture Decision Record）
ID: "20260720t080853z-11-adr"
タイトル: "Prompt-Embedded Slicing Contract and Decomposition Quality Review"
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
  - "Human intervention caused by repeated over-decomposition"
  - "Outcome-Oriented Vertical Slicing ADR"
reflected_to:
  - "spec-dock-initiative-planning"
  - "spec-dock-epic-planning"
  - "spec-dock-chatgpt planning create"
  - "spec-dock-chatgpt review planning"
  - "spec-dock/docs/workflow_review.md"
artifact_type: "adr"
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/artifacts/20260720t080853z-11-adr-prompt-embedded-slicing-contract-and-decomposition-quality-review.md"
---

# Prompt-Embedded Slicing Contract and Decomposition Quality Review

## 位置づけ

このADRは、分割品質をHumanの逐次指摘に依存させず、ChatGPTのPlanning生成PromptとFormal Planning Reviewへ組み込む方法を定める。

## ADR 化基準

- hard to reverse: yes。Prompt composition、Planning Skill、Review Perspective、P1 semanticsへ影響する。
- surprising without context: yes。分割数ではなく、必要性と統合可能性を明示的にReviewする。
- real tradeoff: yes。Planning時の分析量を増やす代わりに不要なEpic／Issue／PR／実装を減らす。

## 結論（Decision）

1. Initiative／Epic Planning Promptへ共有Slicing Contractを一度だけ合成する。
2. Planningは、まず一つのEpic／Issueとして成立するか検討し、materialな境界がある場合だけ分割する。
3. EpicごとにActorと完了後Outcomeを、Issueごとにmerge後Outcomeと独立PR理由を要求する。
4. 技術レイヤー、Foundation、QA、Metrics、Dogfood、Inventory等だけを独立sliceにしない。
5. Issue内部の複雑性はMilestone／Execution Unit／Execution Briefへ残す。
6. 返却前にConsolidation Self-Reviewを行い、境界を維持するmaterialな理由がなければ隣接sliceを統合する。
7. Formal Planning Reviewへ必須Perspective `decomposition-quality`を追加する。
8. Initiative ReviewではInitiative Bundle、全Epic Bundles、全Issue Boundary Maps、dependency、Consolidation rationaleを入力にする。
9. Epic完了時に利用可能な能力がない、horizontal Issue群、dead surface、current consumerのないfoundation、QA／Dogfood等だけのIssue、PR価値のないIssue、review／rollback不能な巨大Issueは原則P1とする。
10. 名称や軽微な統合余地はP2とし、P2／P3だけでは文書を変更しない。
11. slice-focusedな追加確認はTargeted Reviewで行えるが、Formal Planning ReviewとHuman approvalを代替しない。

## 背景（Context）

LLMは与えられた対象を深く整理する能力が高い一方、明示的な制約がなければ分類軸を増やしやすい。分割は後続全設計の前提であり、誤ると合理的な設計が価値の低いIssueへ積み上がる。Slicing knowledgeをPromptとReviewの両方へ埋め込む必要がある。

## 選択肢（Options considered）

### Humanが都度修正

Human負荷と再workが大きく、標準化できないため棄却。

### Runtime schemaでIssue数を制限

意味的必要性を評価できず、モデル更新にも弱いため棄却。

### Prompt Contract＋Formal Perspective

生成と独立Reviewの両側で防止でき、Runtime parserを増やさないため採用。

## 判断理由（Rationale）

生成PromptだけではAuthor biasが残り、Reviewだけでは過剰案を毎回作る。共通Contractとfresh `decomposition-quality` Reviewの二段構成により、モデルの深掘り能力をOutcome境界の分析へ向けられる。

## 影響（Consequences）

- Planning Prompt resourceへSlicing Contractを追加する。
- Review Promptへdecomposition rubricとseverityを追加する。
- Humanに提示するPortfolioへConsolidation rationaleを含める。
- Planning evalへover-decomposition、under-slicing、horizontal slicingを追加する。
