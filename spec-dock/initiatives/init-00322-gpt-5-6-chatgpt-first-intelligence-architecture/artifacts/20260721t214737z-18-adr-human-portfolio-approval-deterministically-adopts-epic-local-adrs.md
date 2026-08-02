---
種別: ADR（Architecture Decision Record）
ID: "20260721t214737z-18-adr"
artifact_type: "adr"
タイトル: "Human Portfolio ApprovalでEpic-local ADRを決定的にaccepted authorityへ遷移させる"
状態: "accepted"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-22"
親: ["init-00322"]
authority: "accepted"
accepted_authority: "Human direction to resolve Candidate v9 Formal Review"
accepted_at: "2026-07-22"
accepted_by: "Human"
mirror_eligible: true
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/artifacts/20260721t214737z-18-adr-human-portfolio-approval-deterministically-adopts-epic-local-adrs.md"
derived_from:
  - "Candidate v9 independent Red-Team Formal Review RT-V9-004"
  - "Human direction to update specifications, ADRs, and artifacts"
reflected_to:
  - "EPIC-ADR-ADOPTION.md"
  - "ARTIFACT-MATERIALIZATION-MAP.json"
  - "CANONICAL-BUNDLE-REPLACEMENT.md"
  - "NEW-PORTFOLIO-MATERIALIZATION-RECOVERY.md"
  - "initiative/requirement.md"
  - "initiative/design.md"
  - "initiative/plan.md"
---

# Human Portfolio ApprovalでEpic-local ADRを決定的にaccepted authorityへ遷移させる

## 位置づけ

Candidate Portfolioには、Epic固有のarchitecture decisionをHuman approval前からReview可能にするため、Epic-local ADR proposal templatesを含める。一方、proposal bytesをそのままcanonical pathへcopyすると、Human approval後も`proposed`／`candidate`のままとなり、accepted architecture authorityとmirror eligibilityが成立しない。本ADRはReview identityとadoption authorityを分離し、Human approval後の決定的なtransitionを定める。

## ADR 化基準

- hard to reverse: yes。Human approval、ADR authority、mirror／discovery、materialization parityへ影響する。
- surprising without context: yes。Candidate ZIP内ではproposalであり、canonical repositoryではacceptedへ遷移する。
- real tradeoff: yes。proposalをReview可能に保つ代わりに、closed renderと追加parityが必要になる。

## 結論（Decision）

1. Epic-local ADRはCandidate ZIP内では`状態: proposed`、`authority: candidate`とする。
2. Human Portfolio Approvalは、exact Candidate ZIP SHAと4 Epic-local ADRのadoptionを明示した場合だけadoption authorityとなる。
3. Materializerはproposal bytesを直接copyせず、`EPIC-ADR-ADOPTION.md`のclosed renderを使用する。
4. 動的に設定できるのはbound Epic ID／path、exact Candidate SHA、Human approver、approval timeだけとする。
5. canonical ADRは`状態: accepted`、`authority: accepted`、accepted authority fields、`mirror_eligible: true`を持つ。
6. body、Decision、Rationale、filename-derived ID／type、その他front matterを変更しない。
7. accepted canonical bytesをsource Runtime parser／accepted-ADR collectorで検証し、4／4検出できなければmaterializationをPASSしない。
8. Human approvalがproposal inclusionだけを意味する曖昧な運用を禁止する。adoptionしない場合はCandidateを改訂し、mapとHuman approval textをproposal semanticsへ変更してfresh Reviewする。

## 背景（Context）

Candidate v9では4 Epic-local ADRがproposal／candidateのままなのに、Artifact mapとHuman ReviewはHuman approval後にadopted architecture authorityになると主張していた。決定的なfront-matter transitionがないため、repositoryから採用状態を一意に判定できなかった。

## 選択肢（Options considered）

### Candidate内で最初からacceptedにする

Human approval前のself-claimになるため不採用。

### Human approvalはproposal inclusionだけを意味する

Epic canonical docsがauthorityを持つため技術的には可能だが、Human Reviewとmapがadoptionを意図しており、ADR mirror／discoveryを失うため不採用。

### proposal templateをHuman approval後にclosed renderする

採用。Review前のproposal statusとapproval後のaccepted authorityを両立できる。

## 判断理由（Rationale）

Human approvalは内容だけでなくadoption scopeを明示する必要がある。Candidate SHA、approval evidence、bound Epic identityへrenderをbindし、bodyを不変にすることで、Reviewerが確認したDecisionとcanonical authorityを一致させられる。

## 影響（Consequences）

### Positive

- Human approval、canonical metadata、mirror eligibility、report dispositionが一致する。
- proposalをReview前からacceptedとself-claimしない。
- resume／rollbackをcontent-addressedに実装できる。

### Negative／Debt

- Artifact placementにclosed render stepが増える。
- Human approval evidenceにapprover／time／Candidate SHAが必要になる。
