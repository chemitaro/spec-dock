---
種別: ADR（Architecture Decision Record）
ID: "20260716t123423z-06-adr"
タイトル: "Main Orchestrator・Executor・Git transactionの所有境界"
状態: "accepted"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-16"
親: ["init-00322"]
authority: "accepted"
derived_from:
  - "20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md#D2-051"
  - "20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md#D2-052"
  - "20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md#D2-053"
  - "20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md#D2-054"
reflected_to:
  - "design.md"
  - "plan.md"
---

# 20260716t123423z-06-adr Main Orchestrator・Executor・Git transactionの所有境界

## 位置づけ

このADRは、長寿命Main Orchestrator、Issue単位Executor、working tree、Git transaction、Formal Reviewの所有境界を固定する。

## ADR 化基準

- hard to reverse:
  - yes。全Issue Execution、Repair、PR DeliveryのAgent権限とhandoffを変更する。
- surprising without context:
  - yes。実装を行ったExecutorではなくMainがcommit／pushを所有する。
- real tradeoff:
  - yes。Executorの自律性を一部制限する代わりに、Review candidate、BASE／HEAD、CI triggerをMainが一貫して管理できる。
- ADR として残す理由:
  - Git transactionは単なるfile操作ではなくWorkflow state transitionであり、将来のAgent再編でも維持すべき境界である。

## 結論（Decision）

- Main OrchestratorはEpic全体を1〜3日担当してよい。
- ExecutorはIssue単位を基本寿命とし、同一Issueのbounded repairは原則同じExecutorへ戻す。
- Plan破綻、戦略変更、仕切り直し時だけfresh Executorへ切り替える。
- ExecutorはExecution TrancheまたはRepair Batchの意味的契約内で、Planに列挙されていない関連source、test、config、docs、mirrorも変更できる。
- Requirement、Architecture、Public Contract、Scope、Review Topologyのmaterial変更が必要なら停止してMainへ返す。
- Executorはcommit／pushしない。
- Mainが`git status`、diff、verification、`report.md`を確認してcommit／pushし、Formal Reviewを起動する。
- Executor Handoffは薄いspineを持つ自由Markdownとし、専用JSON stateやhandoff fileを作らない。
- 主要write agentはcustom Executor一つとし、Docs Writerを統合する。
- Built-in Explorer、Researcher、Consultant、Deep Consultantをread-only agentとして残す。
- Issue Gradeからmodel／reasoningを自動選択しない。

## 背景（Context）

pushはGitHub上のCI、Codex Review、ChatGPT Review対象を変更する。Executorが独自判断でpushすると、Mainが管理するReview candidateと外部gateの状態がずれる。一方、Executorをpath allow-listへ閉じ込めると、必要なtest、config、docsを変更できずPlanningが過剰に詳細化する。

## 選択肢（Options considered）

### Option A: Executorは実装・verificationまで、Mainがcommit／push

- Pros:
  - Workflow transitionと実装責務が分離される。
  - Review対象HEADをMainが管理できる。
  - 意図しない変更をcommit前に確認できる。
- Cons:
  - MainのGit操作が増える。
- Decision:
  - Accepted.

### Option B: Executorがcommitし、Mainがpush

- Pros:
  - 実装者がcommit scopeを作れる。
- Cons:
  - Mainは結局commit内容を再確認する必要がある。
  - Final reportやReview boundaryとの整合が曖昧になる。
- Decision:
  - Rejected.

### Option C: Executorがcommit／pushまで行う

- Pros:
  - handoffが少ない。
- Cons:
  - CI／Review triggerを実装Agentが所有し、Workflow境界が崩れる。
- Decision:
  - Rejected.

## 判断理由（Rationale）

意味的裁量とGit権限を分離することで、Executorは強い実装能力を持ちながら、Mainは外部品質ゲートとReview candidateを一貫して制御できる。

## 影響（Consequences）

- Positive:
  - Review、CI、PRのHEAD管理が明確になる。
  - ExecutorをIssue単位で再利用できる。
  - Docs専用Agentと固定path allow-listが不要になる。
- Negative / debt:
  - Mainはdiffとverificationを必ず確認する必要がある。
  - Agent frameworkのinheritance／override仕様を実装時に確認する必要がある。
- Migration:
  - `dev-coder`／`doc-writer`等の旧role routingをcustom Executorへ統合する。
  - agent configとprovider／installed mirrorを同時に更新する。
- Rollback:
  - 未merge変更をrevertできるが、Executor push ownershipへ戻す場合はReview／CI contractの再設計が必要になる。

## 参考（References）

- `design.md#9-Executor・Agent設計`
- `plan.md#Epic-4`
