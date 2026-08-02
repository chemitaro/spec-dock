---
種別: disc
ID: "20260721t161956z-01-disc"
artifact_type: "disc"
タイトル: "Candidate v8 Human Gate — Planning Workflow implementation boundary clarification"
状態: "user-approved"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-22"
親: ["init-00322"]
authority: "current-effective discussion evidence"
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/artifacts/20260721t161956z-01-disc-human-gate-planning-workflow-capability-clarification.md"
derived_from:
  - "Candidate v8 independent Red-Team Formal Review PASS"
  - "Human Gate discussion after Formal Review"
reflected_to:
  - "20260721t161956z-17-adr-planning-workflow-capability-implementation-is-not-downstream-planning.md"
  - "initiative/requirement.md"
  - "initiative/design.md"
  - "initiative/plan.md"
  - "epics/planning-and-advisory-review/plan.md"
---

# Candidate v8 Human Gate — Planning Workflow implementation boundary clarification

## Observed Human Gate concern

`E1-I1 — Issue Planning End to End`は、SpecDockへPlanning Workflowを実装するIssueではなく、後続IssueのPlanningを専属で行うIssueとも読めた。後者は、Initiative／Epic Planningをimplementation中に変更し、各IssueのJIT Planningを上位Issueへ外出しするため不適切である。

## Clarified intent

E1-I1の意図は、各Issueが自分自身をJIT Planningできる再利用可能なSpecDock Workflowを実装することである。E1-I2も、現在のPortfolio Planningをやり直すIssueではなく、将来のInitiative／Epic Portfolio Planning Workflowを実装する。E1-I3もTargeted Review／planning cutover capabilityを実装する。

## Effective correction

```text
E1-I1
Issue Planning End to End
→ Implement ChatGPT Issue Planning Workflow

E1-I2
Initiative Epic Portfolio Planning and Materialization
→ Implement Initiative Epic Portfolio Planning Workflow

E1-I3
Targeted Review and Planning Specific Surface Cutover
→ Implement Targeted Review and Planning Surface Cutover
```

All three Issues now use implementation-centered outcomes and an Issue-local mandatory four-item Non-goal matrix: no current Portfolio replanning, no downstream Issue Requirement／Design／Plan pre-authoring, no Human approval bypass, and no Planning-only completion. Actual Planning runs are acceptance evidence only.

## Gate consequence

Candidate v8 PASS remains frozen evidence for its exact SHA, but Human approval was not granted. The semantic identity change requires Candidate v9 and a fresh independent Formal Review.
