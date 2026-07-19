---
種別: research
ID: "20260716t131924z-research"
タイトル: "Initiative Bootstrap Repository Baseline"
状態: "completed"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-16"
親: ["init-00322"]
authority: "source-grounded"
derived_from:
  - "chemitaro/spec-dock@3ee6d9047506a40b938407ecfffbb341a3ca76af"
  - "GitHub Issue #322"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
---

# Initiative Bootstrap Repository Baseline

## 調査目的

本Artifactは、Planning Bundleをどこへ配置し、何を既存資産として扱うかを固定するためのbootstrap調査である。

## 確認済み事実

- GitHub Issue `#322`はopenで、Typeはinitiativeである。
- repositoryには既に`init-00322`が存在する。
- Initiative pathは`spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture`である。
- 現在の`requirement.md`、`design.md`、`plan.md`、`report.md`はいずれもtemplate scaffoldであり、主要sectionが未記入である。
- Workbench機能はPR #323で`main`へmerge済みであり、本Initiativeの追加migration対象ではない。
- 現行repositoryには、vNextで削除・改訂対象となるChatGPT authoring Skill、manual Planning Skill、local Reviewer Agent、Issue／Epic Execution Workflow、PR Delivery Workflow、provider／installed mirrorが存在する。
- 現行のGitHub Issueタイトルは`GPT 56 ChatGPT First Intelligence Architecture`である。

## 採用する解釈

- 新しいInitiative Nodeを作成せず、既存`init-00322`を利用する。
- canonical titleは`ChatGPT 5.6 Pro Delegation-First Workflow vNext`へ更新する。
- 本Planning Bundleはlegacy Identify frontmatterを持たず、既存template fileを完全置換する。
- `report.md`はこのbootstrap packでは置換しない。Final Completion Summaryへの変更は実装Epicで行う。
- closed／historical Scopeを変更しない。
- repository baselineは実装開始時に再確認し、file-by-file inventoryはEpic 1で完成させる。

## Source references

- `spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/requirement.md`
- `spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/design.md`
- `spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/plan.md`
- `spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/report.md`
- GitHub Issue `#322`
- `artifacts/20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md`
