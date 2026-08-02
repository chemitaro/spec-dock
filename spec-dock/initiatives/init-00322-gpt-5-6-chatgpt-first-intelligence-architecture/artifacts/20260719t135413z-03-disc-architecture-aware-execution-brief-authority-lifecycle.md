---
種別: disc
ID: "20260719t135413z-03-disc"
タイトル: "Architecture-Aware Execution Briefのauthorityとlifecycle"
状態: "user-approved"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-19"
親: ["init-00322"]
authority: "user-approved discussion"
derived_from:
  - "Architecture-Aware Execution Brief interview"
  - "GPT-5.6 pre-implementation research"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "20260719t135413z-05-adr-architecture-aware-execution-brief-as-frozen-subordinate-contract.md"
---

# Architecture-Aware Execution Briefのauthorityとlifecycle

## 問題

Issue PlanのMilestone／Execution TrancheはIssue全体の順序、Checkpoint、Verification、Exit Contractを定義するが、実装直前の現在HEADに基づく具体的なテスト戦略と実装戦略までは安定して保持しない。Codexが毎UnitでArtifact探索、architecture理解、候補比較、テスト設計を繰り返すと、認知資源と試行錯誤を消費する。

一方、JIT詳細を`plan.md`へ追記すると、Planning SSOTが不安定になり、Planning Reviewの再実行、第四canonical文書、可変Scope schema等の複雑性が生じる。

## 選択肢

### Option A: Issue直下の第四canonical文書

- 耐久性は高い。
- `plan.md`とのauthority競合、可変文書数、Planning Review循環が発生する。
- 不採用。

### Option B: Workbenchだけの一時文書

- 単純で柔軟。
- セッション越しhandoff、後日の設計意図追跡、Review時の前提確認が弱い。
- candidate用途に限定。

### Option C: ChatGPT出力を直接Artifact化

- 耐久性はある。
- 未確認candidateがauthorityを持つ危険がある。
- Main adoption gateを加えない形は不採用。

### Option D: Workbench candidateからfrozen Artifactへ昇格

- ChatGPTの分析能力を活用できる。
- Mainがbinding、evidence、scopeを確認できる。
- `plan.md`を安定したPlanning SSOTとして維持できる。
- accepted Briefを特定Unitのoperational SSOTとして利用できる。
- 採用。

## Current decision

```text
exact synced HEAD
→ ChatGPT semantic retrieval and analysis
→ Workbench candidate
→ Main validates binding/status/evidence/scope
→ ready only
→ Issue artifactsへ内容不変でcopy
→ freeze
→ Executor
→ Brief + implementation + tests in the same candidate commit
→ Checkpoint／Delivery Review
```

## Authority

```text
Human decision
>
canonical Requirement／accepted ADR／Design／Plan
>
repair scopeではfrozen Repair Batch
>
通常Execution Unitではaccepted Execution Brief
>
Workflow guidance
>
Executor local judgment
>
raw evidence／Workbench
```

Execution Briefは上位Planを変更できず、実施結果やReview結果を追記しない。material conflictはPlanningへ戻す。

## Scope neutrality

`Architecture-Aware`は特定のarchitecture patternを必須とする名称ではない。対象Unitの正しい実装に影響する構造、契約、責任境界、動作原理をrepository evidenceから特定するという意味である。DDD、イベント駆動、security、data、CLI等は動的に選択されるLensである。
