---
種別: ADR（Architecture Decision Record）
ID: "20260721t074818z-adr"
タイトル: "Official cutover activationとpost-cutover evaluation／release closureを別Issueへ分ける"
状態: "accepted"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-21"
親: ["epic-00333"]
authority: "accepted"
accepted_authority: "Human Portfolio Approval of the exact Candidate ZIP SHA"
accepted_at: "2026-07-22T11:13:45Z"
accepted_by: "iwasawayuuta"
mirror_eligible: true
approval_transition_contract: "EPIC-ADR-ADOPTION.md"
approval_scope: "Human Portfolio Approval of exact Candidate ZIP SHA"
artifact_type: "adr"
candidate_semantic_key: "epic-completion-and-global-cutover"
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00333-epic-completion-and-global-cutover/artifacts/20260721t074818z-adr-separate-cutover-activation-from-post-cutover-release-closure.md"
---

# Official cutover activationとpost-cutover evaluation／release closureを別Issueへ分ける

## Decision

Epic 3では、official global cutoverを成立させるIssueと、その後の評価・release decisionを成立させるIssueを分離する。

```text
E3-I2 Official Global Cutover and Rollback Activation
→ Human merge activates official cutover
→ E3-I3 Post Cutover Evaluation Release Decision and Initiative Closure
→ Human merge publishes the final release decision package
```

E3-I2 Issue Delivery Reviewはpre-cutover readiness、parity、replay、security、rollback capabilityだけを評価し、存在しないpost-cutover evidenceを要求しない。E3-I3はcutover確認後に開始し、一つのdedicated branch／draft PRで4週間／5件Evidenceを集約する。

## Context

一つのIssue／PRにcutoverとpost-cutover evaluationを含めると、cutoverを成立させるHuman mergeより前にpost-cutover evidenceが必要になる循環が発生する。merge後にEvidenceを集める場合も、そのowner、branch／PR、Formal Review、repository publication boundaryが未定義になる。

## Options considered

### 一つのIssueのまま運用する

post-merge Evidenceをrepositoryへ公開する第二のPRが暗黙に必要となり、1 Issue／1 PR contractと矛盾するため不採用。

### post-cutover Evidenceを外部だけで保持する

final decision packageとrelease authorityをcanonical repositoryへ結び付けられず、audit／Review／Human merge境界が弱いため不採用。

### cutover Issueとrelease-governance Issueを分離する

Human merge、時間的Evidence、rollback、Formal Review、repository publicationを一意にできるため採用。

## Rationale

この分割はQA工程によるhorizontal slicingではない。次のmaterialな境界がある。

- E3-I2: repository-wide route切替とrollback activation。
- E3-I3: cutover後にしか生成できないEvidenceとHuman release decision。
- 異なる開始条件、Evidence、Review時点、Human decision、rollback／continuation route。

## Consequences

- Epic 3のIssue Seedは2件から3件へ増える。
- Candidate Portfolio全体は3 Epic／7 Issue Seedsとなる。
- E3-I3は長期間のdraft PRを持ち得るが、一つのrelease-governance Outcomeへ閉じる。
- floor未達時はPRをmergeせず、continue／follow-up／rollback／terminationへrouteする。
- Epic Delivery ReviewとInitiative closureはE3-I3 merge後の別gateとして維持する。
