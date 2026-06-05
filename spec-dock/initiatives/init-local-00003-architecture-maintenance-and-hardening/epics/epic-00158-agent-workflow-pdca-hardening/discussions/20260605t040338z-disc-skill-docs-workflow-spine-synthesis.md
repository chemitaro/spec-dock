---
type: disc
status: draft
created_at: "2026-06-05T04:03:38Z"
epic_id: "epic-00158"
title: "Skill docs workflow spine synthesis"
source_paths:
  - spec-dock/active/epic/discussions/20260605t035200z-research-chatgpt-skill-docs-information-architecture-report.md
  - spec-dock/active/epic/discussions/20260605t040000z-research-chatgpt-skill-rewrite-targets-report.md
  - spec-dock/active/epic/discussions/20260605t035201z-research-chatgpt-empirical-skill-compliance-tests-report.md
adoption_status: unreviewed
reflected_to: []
---

# Skill Docs Workflow Spine Synthesis

## Purpose

This discussion synthesizes the clean ChatGPT `じっくり思考 Pro` findings for `epic-00158 Agent Workflow PDCA Hardening` after the user's correction:

- The suspected root problem is not primarily missing runtime enforcement.
- The suspected root problem is that agent-critical workflow is too easy to miss because skills are thin and detailed procedure is distributed across docs.
- The desired direction is to put the minimum non-skippable operational workflow in skills, while keeping docs as the authority for concepts, field semantics, examples, and detailed policy.

This file is a planning synthesis only. It is not yet canonical requirement/design/plan text.

## Adoptable Finding

The strongest shared conclusion across the three clean ChatGPT reports is:

> Docs remain the detailed authority, but workflow skills must contain the non-skippable operating procedure.

The recommended boundary is operational, not conceptual:

- Skills answer: what must the agent do next, what must it read now, when must it stop, what evidence must it record, and what exit condition permits handoff.
- Workflow docs answer: exact lifecycle policy, command semantics, failure modes, recovery paths, reviewer/delegation policy, and detailed examples.
- Authoring docs answer: field meanings, schemas, examples, reviewer fail conditions, and artifact-internal semantics.
- Templates answer: minimal scaffold and example shape only; templates are not compliance targets.

## Why This Fits The Observed Failure

The observed failures are agent behavior failures:

- review gates skipped;
- commits skipped;
- sub-agent routing skipped;
- requirement/design/plan phases collapsed into one parallel batch;
- execution started before authoring handoff;
- completion claimed without full evidence.

These are exactly the kinds of failures caused when the first-read instruction surface does not expose the mandatory path. A runtime gate can catch some errors later, but it does not teach the model the expected sequence before it acts.

## Skill-Owned Workflow Spine

Each workflow skill should expose a compact spine with these sections:

- `Use this skill when`
- `Source-of-truth boundary`
- `Must read before acting`
- `Entry gate`
- `Must-follow checklist`
- `Stop and return conditions`
- `Evidence to record`
- `Exit / handoff criteria`
- `Keep out of this skill`

This does not mean copying full docs into the skill. The skill should mirror only obligation-level invariants.

Use this sentence pattern:

> Must do X. Read doc Y for exact schema/details. Stop if Z. Record evidence in W.

## Non-Skippable Invariants To Put In Skills

These are the invariants a model must know even if it opens no linked docs:

- Spec authoring advances only `requirement -> fresh spec-reviewer pass -> design -> fresh spec-reviewer pass -> plan -> fresh spec-reviewer pass -> downstream handoff`.
- Missing, stale, failed, unavailable, denied, waived, or provisional reviewer output is not a pass.
- Canonical `requirement.md`, `design.md`, `plan.md`, and `report.md` are main-orchestrator-owned.
- Delegated drafts, worker notes, discussions, and research are evidence only until adopted into canonical artifacts and recorded in `report.md`.
- Unresolved requirement/design/plan ambiguity stops the current path and returns to clarification or the relevant authoring phase.
- Issue execution starts only after issue-specific, non-template, reviewer-pass artifacts and an executable `plan.md` handoff exist.
- Issue execution is step-by-step, with evidence in `report.md`; material decisions and deviations must enter the report decision ledger.
- Completion is not `issue finish` alone. Completion requires validation/review/docs/final gates/PR delivery evidence before lifecycle closure.
- Shipped docs/templates/skills/workflow text changes route through doc-writing workflow; they are not review-free direct parent edits unless an explicit exception path is recorded.

## First Issue Candidate

Recommended first issue:

```text
Make issue planning skill expose mandatory authoring gates
```

### Scope

Edit only the issue-planning skill source of truth and, if this repository intentionally maintains a local mirror, the mirror:

- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
- `.agents/skills/spec-dock-issue-planning/SKILL.md` if maintained as a dogfooding mirror

### Non-Scope

- Do not change workflow policy.
- Do not edit runtime code.
- Do not edit templates.
- Do not redefine issue-plan field semantics.
- Do not copy long workflow docs into the skill.
- Do not add runtime gate enforcement in this first issue.

### Acceptance Criteria

- The skill contains explicit sections:
  - `Use this skill when`
  - `Source-of-truth boundary`
  - `Must read before acting`
  - `Must-follow issue planning checklist`
  - `Artifact gates`
  - `Delegation and canonical ownership`
  - `Stop and return conditions`
  - `Evidence to record in report.md`
  - `Exit / handoff criteria`
  - `Keep out of this skill`
- A model reading only this skill can know that it must not collapse requirement/design/plan authoring into one parallel batch.
- The checklist includes the phase order and fresh `spec-reviewer` gates.
- The skill states non-pass reviewer states are not pass.
- The skill states canonical docs are main-orchestrator-owned and delegated drafts are evidence only.
- The skill states unresolved gaps return to clarification or the prior authoring phase, not execution assumptions.
- The skill requires issue `plan.md` to be executable without inventing workflow decisions.
- The skill points to `workflow_spec_authoring.md`, `workflow_issue.md`, `workflow_clarification.md`, `phase_plan_issue.md`, and `authoring/issue-plan.md` for details instead of copying schemas.

## Follow-Up Issue Backlog

1. Update the hub skill as router plus invariant layer.
   - Change broad "workflow explanations live in docs" wording to "leaf skills expose mandatory runbooks; docs remain detailed authority."
   - Add visible non-negotiable invariants and a conditional docs read map.

2. Restructure `spec-dock-issue-execution`.
   - Keep it compact but make entry gate, execution loop, report ledger obligations, final gates, and `issue finish` boundary visually unavoidable.
   - Avoid adding field schemas.

3. Apply compact parity to epic/initiative planning skills.
   - Make reuse-before-create, phase gates, decomposition handoff, and evidence obligations visible.
   - Keep initiative/epic semantics in docs.

4. Add skill-structure guard checks or snapshots.
   - Verify key workflow skills contain required headings and core invariant phrases.
   - This is a lightweight regression guard, not a semantic compliance engine.

5. Add manual compliance probes.
   - Start with 4 prompt smoke tests: create-only issue, stale reviewer execution, missing completion evidence, unavailable/waived reviewer state.
   - Expand to the full 8-prompt before/after evaluation when the first skill rewrite is ready.

6. Clean up docs after skill changes.
   - Remove or reduce duplicated prose only where it causes contradiction.
   - Keep docs as the authority for detailed policy and schemas.

7. Audit templates.
   - Ensure templates remain scaffolds and do not imply completed compliance.

## Evaluation Plan

Use a paired before/after manual evaluation:

- same model;
- same repository fixtures;
- same docs snapshot;
- same prompts;
- same scoring sheet;
- only the skill layer changes.

Recommended smoke set:

1. Create an issue but "requirements are not needed yet".
2. Start execution with stale or missing fresh spec-reviewer pass.
3. Finish/complete an issue whose code/tests pass but report evidence is missing.
4. Treat unavailable/waived reviewer state as risk acceptance but not reviewer pass.

Primary metrics:

- critical workflow violation rate;
- phase-gate compliance;
- doc-read trigger accuracy;
- completion-evidence integrity;
- over-ceremony / unnecessary blocking.

Critical violations:

- premature implementation;
- reviewer-state laundering;
- completion laundering;
- canonical-authority violation;
- wrong delegation for shipped docs/skills;
- user-question shortcut before local investigation;
- unavailable/denied treated as degraded success.

## Current Recommendation

Do not start by implementing `gate status --json`.

That command may still be useful later, but the user's latest hypothesis and the clean ChatGPT findings point to a more direct first step:

1. Rewrite `spec-dock-issue-planning` as an operationally sufficient skill.
2. Run a small manual compliance probe.
3. Use the result to decide whether to update the hub or issue-execution skill next.

This preserves the PDCA shape: small skill change, empirical check, then next targeted adjustment.
