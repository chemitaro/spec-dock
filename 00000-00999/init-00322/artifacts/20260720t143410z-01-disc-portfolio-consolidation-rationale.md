---
種別: disc
ID: "20260720t143410z-01-disc"
タイトル: "3 Capability Epic／7 Issue SeedへのPortfolio Consolidation Rationale"
状態: "candidate"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-21"
親: ["init-00322"]
authority: "candidate evidence"
artifact_type: "disc"
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/artifacts/20260720t143410z-01-disc-portfolio-consolidation-rationale.md"
---

# 3 Capability Epic／7 Issue SeedへのPortfolio Consolidation Rationale

## Why not one Epic

Planning、Issue Delivery、multi-Issue Epic Completion／Global Cutoverは、Actor、Contract Owner、Acceptance、Risk／Rollback boundaryが異なる。すべてを一EpicにするとIssue Portfolioが再び大きなProgramとなる。

## Why not seven Epics

Foundation、Review、Cutover、Dogfood／Final Qualityを独立Epicにすると、Epic完了時に利用可能なActor Outcomeが弱く、component Issueと工程Issueを誘発する。

## Why three Epics

- Epic 1はGoal／Seedからreviewed Planning、planning-specific cutover、Node materializationを届ける。
- Epic 2は承認済みIssue Planから実装、formal gates、dedicated PR、Human merge、Issue finishまでを一つのvertical Issueで届ける。
- Epic 3は複数Issue Epicのfinishとremaining global cutover／releaseを届ける。

各Epicは独立利用価値、Acceptance Boundary、Human／Git boundaryを持ち、前Epicのmerge済み能力を実consumerとして利用する。

## Issue consolidation

Candidate v1のEpic 2はdelivery-ready handoffで2 Issueへ水平分割されていた。Actor Journey、PR固定費、context handoffを再評価し、実装からHuman merge／finishまでをE2-I1へ統合した。

7 Issue Seedsはすべて個別PRを正当化するObservable Outcomeまたは高リスク／temporal Human decision boundaryを持つ。CLI、schema、tests、docs、metrics、QA、dogfoodを通常は各Outcome Issueへ統合する。ただしE3-I2 cutover mergeとE3-I3 post-cutover release decisionは、Evidenceが時間的に後からしか存在せず、異なるHuman merge／rollback／continuation boundaryを持つため分離した。E3-I3はQA-onlyではなくrelease-governance Outcomeである。
