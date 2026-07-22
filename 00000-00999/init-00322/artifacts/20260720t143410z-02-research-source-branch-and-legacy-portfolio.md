---
種別: research
ID: "20260720t143410z-02-research"
タイトル: "Source Branchと旧7 Epic Portfolioの置換分析"
状態: "completed"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-21"
親: ["init-00322"]
authority: "research evidence"
derived_from:
  - "GitHub branch codex/init-00322-chatgpt56-planning-pack-adoption"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "LEGACY-PORTFOLIO-RETIREMENT.md"
artifact_type: "research"
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/artifacts/20260720t143410z-02-research-source-branch-and-legacy-portfolio.md"
---

# Source Branchと旧7 Epic Portfolioの置換分析

## Source baseline

```text
Repository: chemitaro/spec-dock
Branch: codex/init-00322-chatgpt56-planning-pack-adoption
HEAD: 2667b4342f803606859a71740b29f0b51b1b3f37
requirement blob: cd27d8ed0f8a7b9af1711c603d222d6fbe67a414
design blob: 27a67f7255747ef92cc90d0e1d2f71c344834dff
plan blob: 2665533b0214e4157a5a7a07e22fc24161ad1ae0
report blob: 4f1098e099974d4830fb2daefe52ed04f7870720
```

## Existing Portfolio

`epic-00324`〜`epic-00330`／GitHub #324〜#330がmaterialize済みで、17 direct dependency edgeを持つ。`epic-00324`はfresh re-review PASS後のHuman Issue-slice approval gateにある。

## Replacement rationale

- Foundation／Review／QA等の工程・レイヤーをCapabilityから分離したため、Epic単体のActor Outcomeが弱い。
- Issue投影がcomponent sliceとなり、per-Issue PRの固定費に見合う価値がない。
- 現行の要件能力は3 Capability Epicへ損失なく再配置できる。
- Candidate v1のEpic 2はdelivery-ready handoffで水平分割されていたため、v2で一つのvertical Issueへ統合した。
- 旧Epic／Issue候補は、Humanが新Candidate ZIPを承認した後にだけsupersedeする。

## Capability mapping

```text
旧 Foundation + Planning + Review
→ Epic 1 Planning and Advisory Review

旧 Issue Execution + Issue-level PR Delivery
→ Epic 2 Issue Execution and Per-Issue Delivery

旧 Epic Delivery + Cutover + Final Dogfood
→ Epic 3 Epic Completion and Global Cutover
```

## Retirement safety

旧Portfolioはdependency reverse-topological orderで、supported Runtime `delete --id ... --yes`により一件ずつretireする。remote close／partial local delete／dependency scrub failureでは停止し、新Portfolioの作成へ進まない。Epic 1 Planning evidenceはInitiative Artifact、Git history、closed GitHub Issue #324で保持する。
