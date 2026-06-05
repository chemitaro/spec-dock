---
種別: research
ID: "20260605t041318z-research"
タイトル: "ChatGPT Requirement Critique for Issue Planning Skill Spine"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-05"
親: ["iss-00159"]
関連:
  - "epic-00158"
  - "20260605t040646z-disc"
authority: "evidence"
answer_now_used: false
thread_url: "https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a224da1-5968-83a6-bc8b-79ae1933982e"
report_path: "spec-dock/active/epic/issues/iss-00159-make-issue-planning-skill-expose-mandatory-authoring-gates/discussions/20260605t042900z-research-chatgpt-requirement-critique-report.md"
---

# 20260605t041318z-research ChatGPT Requirement Critique for Issue Planning Skill Spine

## 目的

`iss-00159` の requirement draft を、ChatGPT `GPT-5.5 Pro` / strongest visible model に critique してもらう。

この task package は、formal `spec-reviewer` の代替ではなく、formal review 前の外部 reasoning evidence である。

## 実行状態

- submitted_at: "2026-06-05T04:14:XXZ"
- thread_url: "https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a224da1-5968-83a6-bc8b-79ae1933982e"
- project_boundary: "Codex-only Project URL under for codex app"
- model_visible: "じっくり思考 Pro"
- initial_signal: "Pro が思考中です"
- answer_now_used: false
- completed_at: "2026-06-05T04:29:XXZ"
- latest_status: "completed and extracted"
- completion_signal:
  - "assistant message present"
  - "stop control absent"
  - "thinking text absent"
  - "stable after second check"
- report_path: "spec-dock/active/epic/issues/iss-00159-make-issue-planning-skill-expose-mandatory-authoring-gates/discussions/20260605t042900z-research-chatgpt-requirement-critique-report.md"

## 背景

ユーザーの最新補足:

- 問題の本質は、workflow をより厳密にすること自体ではなく、現在の skill / docs 構造がモデルにとって確認しにくいことにある。
- 現在の skill は薄く、詳細 docs を参照する構造になっている。この役割分担自体はよい。
- ただし、agent に必ず守ってほしい作業手順が docs 側に埋もれ、複数 docs に分散していると、agent が docs を開かなかった場合に workflow を知らない状態になる。
- そのため、agent が最初に守るべき workflow spine は skill に薄く書く。
- 各 doc / requirement / design / plan の意味、項目の説明、field semantics、詳細 schema は docs に置く。
- skill は、特定 artifact を作るときに読むべき docs を案内する。

## 現在の状況

- Active epic: `epic-00158 Agent Workflow PDCA Hardening`
- Active issue: `iss-00159 Make Issue Planning Skill Expose Mandatory Authoring Gates`
- Issue goal:
  - `spec-dock-issue-planning` skill を、Issue requirement / design / plan authoring で agent が守るべき必須手順を読み飛ばしにくい instruction surface へ改善する。
- Current decision:
  - runtime gate / CLI enforcement / `gate status --json` はこの issue の初手ではない。
  - first implementation target は `spec-dock-issue-planning` skill の workflow spine。
- Formal reviewer status:
  - `spec-reviewer` pass はまだない。
  - design / plan promotion はまだ行わない。

## 関連ファイルと抜粋

### Current skill source

Provider-side source of truth:

`src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`

Dogfooding mirror:

`.agents/skills/spec-dock-issue-planning/SKILL.md`

Current content:

```markdown
---
name: spec-dock-issue-planning
description: Leaf skill for issue requirement, design, and plan planning tasks in spec-dock.
---

# Spec-dock Issue Planning

- Use this skill for issue planning work.
- Typical fit: create or update issue-level requirement/design/plan docs, prepare review readiness, or return unresolved execution gaps to authoring.
- Primary lifecycle / execution workflow: `spec-dock/docs/workflow_issue.md`.
- Spec authoring workflow: `spec-dock/docs/workflow_spec_authoring.md`.
- Clarification workflow for unresolved ambiguity, interview evidence, and source-grounded questions: `spec-dock/docs/workflow_clarification.md`.
- Issue plan phase playbook: `spec-dock/docs/phase_plan_issue.md`.
- Issue plan field semantics and executable step schema: `spec-dock/docs/authoring/issue-plan.md`.
- Keep canonical `requirement.md` / `design.md` / `plan.md` / `report.md` main-orchestrator-owned; this skill does not grant delegated canonical write authority.
- `system-architect` and `implementation-planner` drafts are scope-local evidence only. They do not replace main orchestrator integration, fresh `spec-reviewer` pass, phase promotion, implementation readiness, or issue execution handoff.
- In spec authoring mode, do not move from requirement to design, design to plan, or plan to execution until a fresh `spec-reviewer` returns `review_status: pass`; fix findings and re-run a fresh reviewer until pass.
- If planning reveals unresolved requirement / design / plan gaps, return to `workflow_clarification.md` or the relevant authoring phase instead of absorbing the gap in execution.
- Record each `Spec Authoring Gate` in the issue `report.md`, including investigation, user questions/answers, reviewer verdict, fixes, promotion decision, and handoff readiness.
```

### Requirement draft summary

`iss-00159/requirement.md` currently defines:

- Purpose:
  - improve `spec-dock-issue-planning` skill so issue authoring agents cannot easily miss the mandatory issue authoring workflow.
- Scope:
  - add mandatory workflow spine to the skill.
  - make requirement -> fresh `spec-reviewer` pass -> design -> fresh `spec-reviewer` pass -> plan -> fresh `spec-reviewer` pass -> execution handoff visible in the skill.
  - state that missing / stale / failed / unavailable / denied / waived / provisional reviewer states are not pass.
  - state that canonical requirement/design/plan/report are main-orchestrator-owned and delegated drafts are evidence only.
  - state unresolved requirement/design/plan gaps return to clarification or prior authoring phase.
  - state issue `plan.md` must be executable before execution handoff.
  - keep detailed schema in docs, not in the skill.
- Non-scope:
  - runtime gate, CLI command, validation logic.
  - workflow policy changes.
  - long issue-plan field schema copy into skill.
  - hub skill, issue-execution skill, epic/initiative skills.
  - manual compliance harness.
  - `gate status --json`.
- Acceptance criteria:
  - AC-001: skill alone exposes phase order.
  - AC-002: non-pass reviewer states are not pass.
  - AC-003: unresolved gaps return to clarification / phase, not execution assumptions.
  - AC-004: delegated drafts are not canonical without main orchestrator adoption and report evidence.
  - AC-005: skill does not over-copy field schema or long policy.
  - AC-006: provider source and dogfooding mirror are consistent or report records why not.
- Open question:
  - whether to update root `.agents/skills/...` mirror in the same issue.
  - current recommended answer: update provider source and dogfooding mirror together.

## 制約と非ゴール

- Do not treat this as a formal `spec-reviewer` pass.
- Do not propose changing runtime enforcement in this issue unless explicitly marked as follow-up.
- Do not propose copying long docs, field schema, or detailed semantics into the skill.
- Focus on the user hypothesis:
  - workflow procedures that agents must obey belong in skill.
  - conceptual meaning, field semantics, detailed authoring guidance belong in docs.
- Keep the first issue small and PDCA-friendly.
- Treat ChatGPT output as third-party critique evidence only.
- `今すぐ回答` / `Answer now` must not be used.

## 既知の不確実性

- Exact section headings and wording for the rewritten skill are not fixed yet.
- Formal `spec-reviewer` has not been run.
- The eventual implementation owner will likely be `doc-writer`; this task is still requirement critique.
- The current skill already contains some gate reminders, but may still be too compact / bullet-only for reliable model compliance.

## ChatGPT への依頼

Please critique the `iss-00159` requirement draft from the perspective of instruction design for coding agents.

Primary question:

Does this issue correctly capture the user's latest insight: "mandatory agent workflow should be visible in the skill, while detailed conceptual meaning and field semantics should remain in docs"?

Please answer with:

1. Overall judgment:
   - Is the requirement ready to send to a formal `spec-reviewer`, or should Codex revise it first?
   - This is advisory only, not a formal pass/fail.
2. Findings ordered by severity:
   - missing requirement scope,
   - over-scoped requirement,
   - ambiguous wording,
   - acceptance criteria that are not testable,
   - risks that still lean too much toward runtime gates instead of skill readability.
3. Specific recommended edits to `requirement.md`:
   - exact short wording suggestions are welcome.
4. Recommended follow-up issues:
   - only if they are clearly separate from this first small issue.
5. Risks for later `design.md` and `plan.md`:
   - especially how to keep the skill operationally sufficient without duplicating docs.
6. What not to do:
   - call out any tempting but counterproductive changes.

Quality bar:

- Be concrete and actionable.
- Distinguish confirmed facts from assumptions.
- Avoid inventing repository state not included above.
- Assume Codex will preserve repo docs as the source of truth.
- Assume the next step is requirement revision or formal `spec-reviewer`, not implementation.
