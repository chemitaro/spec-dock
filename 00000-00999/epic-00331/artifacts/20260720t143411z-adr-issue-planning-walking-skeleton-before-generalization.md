---
種別: ADR（Architecture Decision Record）
ID: "20260720t143411z-adr"
タイトル: "Issue PlanningのEnd-to-End Walking Skeletonを共通基盤より先に完成させる"
状態: "accepted"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-20"
親: ["epic-00331"]
authority: "accepted"
accepted_authority: "Human Portfolio Approval of the exact Candidate ZIP SHA"
accepted_at: "2026-07-22T11:13:45Z"
accepted_by: "iwasawayuuta"
mirror_eligible: true
approval_transition_contract: "EPIC-ADR-ADOPTION.md"
approval_scope: "Human Portfolio Approval of exact Candidate ZIP SHA"
derived_from:
  - "init-00322 Slicing Contract"
reflected_to:
  - "epic plan"
artifact_type: "adr"
candidate_semantic_key: "planning-and-advisory-review"
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/artifacts/20260720t143411z-adr-issue-planning-walking-skeleton-before-generalization.md"
---

# Issue PlanningのEnd-to-End Walking Skeletonを共通基盤より先に完成させる

## Decision

最初のIssueでIssue Planningをend-to-endに完走させる。CLI skeleton、Git binding、Oracle adapter、Prompt、file placement、Planning Review、tests、docs、projectionを別Issueへ分解しない。二つ目のPortfolio Planning利用例が現れた時点で共通化する。

## Rationale

先行Foundationは未使用surfaceと横スライスIssueを生む。実際のActor Journeyを完成させることで必要最小限のboundaryを実証できる。
