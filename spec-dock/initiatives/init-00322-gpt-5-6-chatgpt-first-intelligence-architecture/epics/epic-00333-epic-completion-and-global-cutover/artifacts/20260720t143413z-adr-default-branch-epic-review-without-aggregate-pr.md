---
種別: ADR（Architecture Decision Record）
ID: "20260720t143413z-adr"
タイトル: "個別Issue merge後のdefault branchでEpic Reviewを行いaggregate Epic PRを作らない"
状態: "accepted"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-20"
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
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00333-epic-completion-and-global-cutover/artifacts/20260720t143413z-adr-default-branch-epic-review-without-aggregate-pr.md"
---

# 個別Issue merge後のdefault branchでEpic Reviewを行いaggregate Epic PRを作らない

## Decision

すべてのimplementation Issueを個別PRでHuman mergeする。全Issue merge後、最初のincluded Issue変更前に明示したsemantic BASEからreview対象default-branch HEADまでをEpic Delivery Reviewし、mutation frontierとEpic Contract全体を評価する。P0／P1の修正が必要な場合だけJIT bounded Issue／PRを追加する。aggregate Epic PRと事前Final QA Issueを作らない。BASE／ancestryを確認できなければPASSしない。

## Rationale

Issue PRですでにreview／mergeされた変更を再び一つの巨大PRへ集約すると、Review重複、merge conflict、rollback複雑性を増やす。Epic ReviewはEpic Contractとcross-Issue integrationへ集中すべきである。official cutover activationとpost-cutover evaluation／release closureの時間境界は、同Epicの別ADRとE3-I2／E3-I3で定義する。
