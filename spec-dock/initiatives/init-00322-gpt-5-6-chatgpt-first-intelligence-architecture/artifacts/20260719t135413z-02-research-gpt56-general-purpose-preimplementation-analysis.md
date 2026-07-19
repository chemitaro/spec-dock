---
種別: research
ID: "20260719t135413z-02-research"
タイトル: "GPT-5.6を用いた汎用的な実装前横断分析"
状態: "completed"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-19"
親: ["init-00322"]
authority: "research evidence"
derived_from:
  - "OpenAI GPT-5.6 prompting guidance"
  - "OpenAI Codex review implementation research"
  - "Current SpecDock initiative decisions"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
---

# GPT-5.6を用いた汎用的な実装前横断分析

## Research question

各Milestone／Execution Unitの実装開始前に、ChatGPTが現在HEAD、canonical docs、関連Artifact、code、tests、configurationを横断調査し、テスト戦略と実装戦略をExecution Briefとして具体化する方式は、特定architectureへ限定せず有効か。

## Facts

- GPT-5.6のPrompt guidanceは、Goal、Authoritative Context、Constraints、Required Evidence、Success Criteria、Output Contractを明確にし、重複命令や不要な内部手順を減らす方向を推奨する。
- Lean Promptは詳細な成果物を禁止しない。Promptは簡潔に、成果物はtaskに必要な深さで具体化できる。
- Codex reviewはdiff等の決定的なanchorを起点に、正しさを判断するために必要な周辺contextへ意味的に展開する。
- 独自または複雑なrepositoryでは、一般知識による補完より、current code、tests、configuration、ADR、repository conventionsを根拠にする必要がある。

## Inference

最適な責務分担は、Codex／wrapperがdeterministic anchorを用意し、ChatGPTがsemantic retrievalと高深度分析を行い、Mainが採用判断、Executorが実装と実証を行う構造である。

```text
Deterministic anchors
+
ChatGPT semantic retrieval
+
Evidence-bearing Execution Brief
+
Executor implementation and verification
```

## General-purpose concern model

対象Unitに適用されるConcernは動的に選択する。

- purpose／user-visible behavior
- architecture／responsibility boundary
- framework／extension mechanism
- domain model／business invariant
- event／message flow
- transaction／consistency
- concurrency／ordering／idempotency
- data／persistence／migration
- API／compatibility
- security／privacy
- CLI／UX
- build／deployment／operations
- documentation／repository conventions
- testability／observability

すべてを必須にしない。`applicable`、`not-applicable`、`insufficient-evidence`を区別し、materialなConcernが`insufficient-evidence`なら`ready`を返さない。

## Prompt design

Promptでは、次を一度ずつ記述する。

1. Goal。
2. exact repository／branch／HEADとdeterministic anchors。
3. preserved contractとapproval boundary。
4. Evidence requirementとnon-invention rule。
5. Output contract。
6. final quality requirement。

内部の思考手順、固定architecture、全Concernの網羅を強制しない。

## Evaluation

少なくとも次を比較する。

```text
A. Briefなし
B. generic implementation brief
C. Architecture-Aware Execution Brief
```

品質:

- material Evidence omission
- unsupported assumption
- wrong Concern selection
- test strategy completeness
- first Checkpoint PASS
- Repair発生
- 手戻り

資源:

- Codex token
- tool call
- repository探索command
- failure cycle
- handoff量

運用:

- ChatGPT latencyを含むwall-clock
- Human intervention
- stale Brief／planning-gap／insufficient-evidenceのrouting

品質を悪化させるresource削減は採用しない。
