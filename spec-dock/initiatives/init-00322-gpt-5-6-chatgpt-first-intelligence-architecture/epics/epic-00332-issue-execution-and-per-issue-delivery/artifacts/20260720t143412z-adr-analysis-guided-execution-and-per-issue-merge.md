---
種別: ADR（Architecture Decision Record）
ID: "20260720t143412z-adr"
タイトル: "Analysis-Guided Issue Executionとper-Issue mergeを一つのvertical Issueとして接続する"
状態: "accepted"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-21"
親: ["epic-00332"]
authority: "accepted"
accepted_authority: "Human Portfolio Approval of the exact Candidate ZIP SHA"
accepted_at: "2026-07-22T11:13:45Z"
accepted_by: "iwasawayuuta"
mirror_eligible: true
approval_transition_contract: "EPIC-ADR-ADOPTION.md"
approval_scope: "Human Portfolio Approval of exact Candidate ZIP SHA"
artifact_type: "adr"
candidate_semantic_key: "issue-execution-and-per-issue-delivery"
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00332-issue-execution-and-per-issue-delivery/artifacts/20260720t143412z-adr-analysis-guided-execution-and-per-issue-merge.md"
---

# Analysis-Guided Issue Executionとper-Issue mergeを一つのvertical Issueとして接続する

## Decision

Issue ExecutionはArchitecture-Aware Execution Brief、single custom Executor、Checkpoint、Repair、Issue Delivery Review、dedicated PR、external gates、Human merge、reviewed HEAD確認、Issue finishまでを一つのvertical implementation Issueとして届ける。`delivery-ready`は同じIssue内部のformal gateであり、別Issue／別PRにしない。Epic-wide PRへ集約しない。

主要write-capable roleは`executor`一つに限定する。read-only closed setはbuilt-in `explorer`、custom `researcher`、`consultant`、`deep-consultant`だけとし、その他のnamed roleをmaintained official pathで禁止する。provider／installed／dogfoodのexact setと権限を検証し、Issue Gradeをmodel／reasoningの自動routingへ使用しない。

Checkpoint／Issue Deliveryは明示semantic BASEからreviewed HEAD、PR-style Reviewはmerge-baseからPR HEADを評価し、mutation frontierと現在のIssue Contract全体を検証する。BASE／ancestryを確認できなければPASSしない。

## Rationale

実装からrepository publication／Node completionまでが一つのActor Outcomeであり、中間gateでIssueを分けるとserial PR、handoff、context再構築が増える。権限分離はIssue境界ではなく、Executor、Main、HumanのActor authorityとMilestone／formal gateで実現できる。
