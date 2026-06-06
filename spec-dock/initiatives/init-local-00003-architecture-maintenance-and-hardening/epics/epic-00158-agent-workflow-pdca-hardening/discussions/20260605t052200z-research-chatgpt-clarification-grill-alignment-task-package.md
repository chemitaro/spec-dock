---
種別: research
ID: "20260605t052200z-research"
タイトル: "ChatGPT Task Package For Clarification Grill Alignment"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-05"
親: ["epic-00158"]
関連:
  - "20260605t050100z-disc"
authority: "proposal"
derived_from:
  - "user request 2026-06-05: analyze spec-dock-clarification as Grill with me / Grill with dog integration skill"
reflected_to: []
---

# 20260605t052200z-research ChatGPT Task Package For Clarification Grill Alignment

## 目的

SpecDock の `spec-dock-clarification` skill を、単なる docs-aware clarification ではなく、Matt Pocock 氏の `Grill with me` / `Grill with dog` 的な対話ワークフローを SpecDock に統合する skill として見直す。

この分析は、epic `epic-00158 Agent Workflow PDCA Hardening` の次 wave で、`skill / docs / templates` の住み分けと具体的な修正 issue を決めるために使う。

## 背景

ここまでの分析では、主因は「ルールが足りない」ことよりも、モデルが最初に読む context surface が薄く、分散しており、お手本として弱いことだと整理した。

そのため、当面の主戦場は `skill / docs / templates` 全体を一度整理し、次の住み分けをどこから読んでも分かる状態にすること。

- skills: モデルが必ず守る operational workflow spine。
- docs: 概念、項目の意味、詳細判断、source of truth。
- templates: scaffold、evidence slots、良い記入例。

今回の追加観点は、`spec-dock-clarification` が `Grill with me` / `Grill with dog` 的な「質問で考えを深める」スキルとしてはまだ薄いのではないか、という点。

## 現在の状況

Provider-side source of truth:

- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_clarification.md`
- `src/spec_dock/assets/spec_dock/templates/discussions/interview.md`
- `src/spec_dock/assets/spec_dock/templates/discussions/research.md`
- `src/spec_dock/assets/spec_dock/templates/discussions/disc.md`

Dogfooding mirror:

- `.agents/skills/spec-dock-clarification/SKILL.md`
- `spec-dock/docs/workflow_clarification.md`

The dogfooding mirror is verification only. Implementation authority is provider-side.

## 関連ファイルと抜粋

### Current `spec-dock-clarification` skill

```markdown
---
name: spec-dock-clarification
description: First-class docs-aware clarification workflow for source-grounded questions, analysis-only clarification, and spec authoring handoff.
---

# Spec-Dock Clarification

Use this skill when the user asks to clarify requirements, sharpen wording, resolve ambiguity, prepare questions, or align understanding before requirement / design / plan authoring.

Keep this skill concise. `spec-dock/docs/workflow_clarification.md` is the source of truth.

## Reminders

- Read source first: active docs, parent docs, `discussions/`, related code/tests/templates, and ADRs.
- Do not ask the user about anything local context can answer.
- Traverse the decision tree and ask at most one essential question at a time through the orchestrator.
- For important decisions, create an unanswered `interview` artifact before asking; complete the same artifact after the answer.
- Sharpen domain language with existing docs/code terms, concrete scenarios, and edge cases.
- Use `research` for facts, `disc` for synthesis / ADR triage, and ADR only for durable tradeoff decisions.
- Support analysis-only / draft-only mode without forcing canonical docs.
- In authoring mode, route adoption through canonical docs and `report.md` Evidence Adoption Ledger / Objective Alignment Ledger / Spec Authoring Gate.
- Specialist agents return question candidates to the orchestrator; they do not question the human directly.

## Handoff

Return:

- sources read
- unresolved questions, or `none`
- recommended next question, if any
- suggested artifact: `scratch` / `research` / `interview` / `disc` / `adr`
- authoring mode: analysis-only / draft-only / canonical authoring
- adoption evidence needed in `report.md`
```

### Current `workflow_clarification.md`

Important facts from the doc:

- It defines clarification as a first-class entrypoint, not merely an issue planning sub-section.
- It requires source-grounded read before asking the human.
- It says decision tree traversal should decompose ambiguity and pick only one essential next question.
- Human-facing essential questions are asked by the orchestrator one at a time.
- Specialist agents return question candidates, rationale, affected artifact, and recommended answer to the orchestrator.
- It distinguishes `analysis-only mode` and `authoring mode`.
- It distinguishes artifacts:
  - `scratch`: raw capture.
  - `research`: facts / uncertainty / terms / implications.
  - `interview`: formal one-question artifact for important decisions.
  - `disc`: synthesis / ADR triage.
  - `adr`: durable decision.
  - `report.md`: evidence adoption / objective alignment / spec authoring gate ledger.
- Formal question trigger applies when the answer affects requirement / design / plan / ADR / scope / workflow / template / agent role, changes implementation/test/review/migration, needs multiple artifact reflection, requires tradeoff choice, or needs adoption tracking.
- Issue execution handoff only concerns unresolved specification gaps and readiness evidence; it should not expand into issue planning/execution redesign.

## 既知の不確実性

- Codex currently has not independently fetched the exact public text of Matt Pocock's original `Grill with me` / `Grill with dog` skill. If you know it, use that knowledge cautiously and mark it as model-memory-derived. If you do not know it exactly, infer only from the user's stated intent: a skill that grills the user with focused, iterative, pressure-tested questions to improve clarity.
- Do not claim exact fidelity to Matt Pocock's original text unless you can justify it from supplied context or clearly mark it uncertain.
- The goal is not to copy another skill verbatim. The goal is to adapt the interaction pattern into SpecDock's source-grounded, artifact-aware workflow.

## 制約と非ゴール

- Do not recommend runtime gates or automated regression checks as the first fix.
- Do not make templates compliance authorities.
- Do not copy all docs into the skill.
- Do not make `spec-dock-clarification` a generic coaching skill detached from SpecDock artifacts.
- Keep the skill first-read useful: the model should know the actual interaction loop without needing to read a long doc first.
- Keep docs as the place for definitions, artifact semantics, formal trigger details, and adoption ledgers.
- Keep templates as scaffold/example surfaces.

## 依頼

Analyze how `spec-dock-clarification` should be revised if it is understood as the SpecDock integration of a `Grill with me` / `Grill with dog` style workflow.

Please answer these:

1. What is the core workflow spine that should be visible in `spec-dock-clarification/SKILL.md` itself?
2. What should remain in `workflow_clarification.md` instead of being copied into the skill?
3. What should be reflected in `templates/discussions/interview.md`, `research.md`, or `disc.md` so that the examples/scaffolds teach the same behavior?
4. Does this deserve its own issue, or should it be part of the broader `Align Skill Docs Template Context Surfaces` cleanup issue?
5. If it deserves a concrete issue, propose a concise issue title, scope, non-scope, acceptance criteria, and verification.
6. What are the risks of overfitting to `Grill with me` and losing SpecDock's source-grounded / artifact-aware behavior?
7. What are the risks of underfitting and leaving the current skill too bland?

## 望ましい出力形式

Please produce a structured analysis with:

- Executive conclusion.
- Recommended workflow spine for the skill.
- Skill/docs/templates boundary.
- Concrete rewrite outline.
- Issue decomposition recommendation.
- Acceptance criteria.
- Risks and mitigations.
- Any uncertainty about the original Matt Pocock skills clearly marked.
