---
種別: ADR（Architecture Decision Record）
ID: "20260719t135413z-05-adr"
タイトル: "Architecture-Aware Execution Briefをfrozen subordinate execution contractとして扱う"
状態: "accepted"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-19"
親: ["init-00322"]
authority: "user-approved; repository adoption requires report disposition"
derived_from:
  - "20260719t135413z-01-interview-architecture-aware-execution-brief-current-decisions.md"
  - "20260719t135413z-02-research-gpt56-general-purpose-preimplementation-analysis.md"
  - "20260719t135413z-03-disc-architecture-aware-execution-brief-authority-lifecycle.md"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "spec-dock/docs/workflow_issue.md"
---

# Architecture-Aware Execution Briefをfrozen subordinate execution contractとして扱う

## ADR化基準

- hard to reverse: yes。Issue Execution、Artifact、ChatGPT/Codex責務、Git commit、Planning authorityへ横断的に影響する。
- surprising without context: yes。Artifactでありながら特定Execution Unitのoperational SSOTとして使い、第四canonical文書にはしない。
- real tradeoff: yes。分析品質とCodex資源効率を得る代わりに、ChatGPT latency、Artifact増加、stale管理、Main adoption gateが必要になる。

## Decision

Accepted.

非機械的なExecution Unitでは、実装開始前にChatGPTがexact GitHub HEADを調査し、Architecture-Aware Execution Brief候補を生成する。

SpecDock／wrapperはdeterministic anchorだけを提供する。ChatGPTが関連Artifact、code、tests、configuration、repository conventionsを意味的に探索し、EvidenceとApplicable Concernを選択する。

候補はWorkbenchへ置く。MainがSource HEAD、status、Evidence Used／Gaps、scope、上位contractとの整合を確認し、`ready`だけをIssue `artifacts/`へ内容不変で配置してfreezeする。

`plan.md`はIssue全体のPlanning SSOTとして維持する。accepted Briefは特定Execution Unitに限定されたfrozen subordinate execution contractであり、Requirement、accepted ADR、Design、Planを変更・上書きできない。

Briefは実施結果、changed paths、commit SHA、CI、Review resultを追記しない。原則としてBriefと対応実装を同じcandidate commitへ含める。

## Context

Issue Planning時点では後続Unitの現在コード、追加済みhelper、test seam、dependency stateを完全に予測できない。実装直前のJIT分析は、初期Planを過度に詳細化せず、最新HEADに即したHowを具体化できる。

CodexにArtifact探索、architecture理解、テスト戦略、候補比較を毎回行わせると、希少な認知資源と試行錯誤を消費する。ChatGPTは複数文書とrepository evidenceの横断分析に適しており、この認知処理を担当できる。

## Options considered

### Fourth canonical document

Authority競合、Planning Review循環、可変Scope schemaのため棄却。

### Workbench-only note

耐久性、handoff、後日の意図追跡が不足するためcandidate用途に限定。

### Direct Artifact without adoption

未検証出力がauthorityを持つため棄却。

### Candidate to frozen Artifact

Planning SSOTを安定させ、ChatGPT分析、Main adoption、Executor handoff、Git耐久性を両立するため採用。

## Consequences

### Positive

- 実装前の目的、Evidence、architecture、テスト戦略、停止条件を明確化できる。
- CodexのArtifact探索、設計具体化、試行錯誤を削減できる。
- セッションを跨ぐExecutor handoffとReview前提追跡が安定する。
- 特定architectureへ固定せず、多様なtaskへ動的Concern選択を適用できる。

### Negative／Debt

- ChatGPT呼び出しとArtifactが増える。
- Mainはadoptionとstale判断を行う必要がある。
- 誤ったBriefを盲信すると実装品質を下げるため、non-invention、Evidence Gaps、planning-gap routingが必要。
- 利用価値はquality、resource、latencyの実測で検証しなければならない。

## Follow-ups

- `spec-dock-chatgpt execution-brief generate`。
- `workflow_issue.md`または専用共有section。
- Workbench candidate／Artifact promotion。
- prompt／output contract。
- Briefなし／generic／Architecture-Aware比較eval。
