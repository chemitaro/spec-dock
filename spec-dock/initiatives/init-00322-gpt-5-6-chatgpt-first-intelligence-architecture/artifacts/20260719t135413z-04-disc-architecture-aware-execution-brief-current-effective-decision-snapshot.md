---
種別: disc
ID: "20260719t135413z-04-disc"
タイトル: "Architecture-Aware Execution Brief — Current Effective Decision Snapshot"
状態: "user-approved"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-19"
親: ["init-00322"]
authority: "current-effective discussion snapshot"
derived_from:
  - "20260719t135413z-01-interview-architecture-aware-execution-brief-current-decisions.md"
  - "20260719t135413z-02-research-gpt56-general-purpose-preimplementation-analysis.md"
  - "20260719t135413z-03-disc-architecture-aware-execution-brief-authority-lifecycle.md"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
---

# Architecture-Aware Execution Brief — Current Effective Decision Snapshot

この文書はExecution Briefに関する現在有効な判断だけを記録する。

1. 名称は`Architecture-Aware Execution Brief`。
2. 特定のarchitecture、framework、DDD、イベント駆動、language、product typeを前提にしない。
3. ChatGPTがexact HEADから対象Unitの目的、現状、契約、関連Artifact、code、tests、configuration、repository conventionsを横断調査する。
4. ChatGPTはrepository evidenceに基づき、対象UnitにmaterialなConcernだけを動的に選択する。
5. 第一目的は、理解、Evidence completeness、テスト戦略、実装戦略、実装品質、収束性の向上。
6. 第二目的は、Codex token、tool call、探索、試行錯誤の削減。
7. Codex／wrapperはdeterministic anchorだけを提供し、関連Artifactを意味的に選別・要約しない。
8. 非機械的なExecution Unitでは原則生成し、明白なmechanical changeでは省略できる。
9. `plan.md`はIssue全体のPlanning SSOT。
10. accepted BriefはExecution Unit限定のfrozen subordinate execution contract。
11. candidateはWorkbenchへ置き、`ready`だけをIssue Artifactへ昇格する。
12. statusは`ready | planning-gap | insufficient-evidence`。
13. Briefは実施結果を追記せず、上位Requirement／ADR／Design／Planを変更できない。
14. ExecutorはBriefを利用するが、repository factsとcanonical contractにmaterial conflictがあれば停止する。
15. Briefと対応実装は原則同じcandidate commitへ含める。
16. quality、resource、latencyを別々に評価し、quality悪化を伴う削減を成功としない。
17. Briefなし、generic Brief、Architecture-Aware Briefを多様なtask shapeで比較する。
18. 既存Scopeへ第四canonical文書を要求せず、Workflow capabilityとしてcutoverする。
