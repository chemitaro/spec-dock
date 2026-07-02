---
種別: artifact
ID: "20260702t014409z-01"
タイトル: "Phase 3 V3 Planning Pack Full Intake"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
template: "blank"
authority: "raw"
derived_from:
  - "/Users/iwasawayuuta/.codex/attachments/e09821b7-10dd-485c-89f1-b4e284810ccb/spec-dock-phase3-upstream-planning-pack-v3-clean.zip"
reflected_to: []
---

# 20260702t014409z-01 Phase 3 V3 Planning Pack Full Intake

## Purpose

This artifact preserves the full Markdown contents of the V3 clean planning pack for `epic-00270` as raw working evidence.
The previous V2 attachment is intentionally not adopted for this Epic concretization pass; V3 supersedes it for planning intake.

This file is not canonical `requirement.md`, `design.md`, `plan.md`, or `report.md`. Any adopted claims must be reflected through canonical Epic artifacts and recorded in `report.md` evidence.

## Intake Summary

- ZIP: `/Users/iwasawayuuta/.codex/attachments/e09821b7-10dd-485c-89f1-b4e284810ccb/spec-dock-phase3-upstream-planning-pack-v3-clean.zip`
- Markdown files captured: 24
- Root folder in ZIP: `spec-dock-phase3-upstream-planning-pack-v3-final/`
- Intended parent initiative: `init-local-00003 Architecture Maintenance and Hardening`
- Intended Epic: `epic-00270 Upstream Planning Governance And Templates`
- Adoption status: unreviewed raw evidence

## File Manifest

- `spec-dock-phase3-upstream-planning-pack-v3-final/README.md`
- `spec-dock-phase3-upstream-planning-pack-v3-final/codex-handoff.md`
- `spec-dock-phase3-upstream-planning-pack-v3-final/epic/epic-level-planning-analysis.md`
- `spec-dock-phase3-upstream-planning-pack-v3-final/epic/epic-upstream-planning-governance-and-templates-v2.md`
- `spec-dock-phase3-upstream-planning-pack-v3-final/issues/issue-01-redesign-initiative-templates.md`
- `spec-dock-phase3-upstream-planning-pack-v3-final/issues/issue-02-redesign-epic-templates.md`
- `spec-dock-phase3-upstream-planning-pack-v3-final/issues/issue-03-update-planning-skills-and-workflow-docs.md`
- `spec-dock-phase3-upstream-planning-pack-v3-final/issues/issue-04-update-epic-execution-handoff-workflow.md`
- `spec-dock-phase3-upstream-planning-pack-v3-final/issues/issue-05-add-upstream-planning-smoke-tests.md`
- `spec-dock-phase3-upstream-planning-pack-v3-final/issues/issue-06-epic-quality-gate-manual-tests-and-pr-delivery.md`
- `spec-dock-phase3-upstream-planning-pack-v3-final/reference/current-state-summary.md`
- `spec-dock-phase3-upstream-planning-pack-v3-final/reference/guardrails.md`
- `spec-dock-phase3-upstream-planning-pack-v3-final/reference/manual-test-and-delivery-checklist.md`
- `spec-dock-phase3-upstream-planning-pack-v3-final/reference/quality-gate-plan.md`
- `spec-dock-phase3-upstream-planning-pack-v3-final/reference/revised-issue-slicing-rationale.md`
- `spec-dock-phase3-upstream-planning-pack-v3-final/reference/suggested-file-map.md`
- `spec-dock-phase3-upstream-planning-pack-v3-final/reference/analysis-coverage-and-reading-order.md`
- `spec-dock-phase3-upstream-planning-pack-v3-final/reference/upstream-abstraction-model.md`
- `spec-dock-phase3-upstream-planning-pack-v3-final/reference/discovery-to-canonical-specs.md`
- `spec-dock-phase3-upstream-planning-pack-v3-final/reference/initiative-design-playbook.md`
- `spec-dock-phase3-upstream-planning-pack-v3-final/reference/epic-design-playbook.md`
- `spec-dock-phase3-upstream-planning-pack-v3-final/reference/epic-to-issue-slicing-and-handoff.md`
- `spec-dock-phase3-upstream-planning-pack-v3-final/reference/issue-tdd-handoff-model.md`
- `spec-dock-phase3-upstream-planning-pack-v3-final/reference/reviewer-anti-patterns.md`

## Full Captured Contents

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/README.md`

```markdown
# SpecDock Phase 3 Pack v2 — Upstream Planning Governance and Templates

This pack replaces the previous Phase 3 plan with a corrected Epic-level slicing model.

## Important correction from the prior pack

The previous pack had an Issue named `Define Scope Layering Reference For Initiative Epic Issue`. That was the wrong abstraction level.

Scope-layering, planning-boundary, and Initiative/Epic/Issue responsibility analysis are **Epic-level design and planning decisions**. They must be settled in the Epic requirement/design/plan, then decomposed into executable Issues.

This revised pack therefore:

- moves the scope-layering analysis into `epic/epic-level-planning-analysis.md`;
- removes the non-executable scope-layering Issue;
- slices the work into concrete implementation Issues;
- adds a final Epic-level quality gate / manual-test / PR delivery Issue.

## How to give this pack to Codex

Recommended order:

1. `codex-handoff.md`
2. `epic/epic-upstream-planning-governance-and-templates-v2.md`
3. `epic/epic-level-planning-analysis.md`
4. `reference/*.md`
5. `issues/*.md` in numeric order

## Parent initiative

Use the existing initiative:

```text
init-local-00003 Architecture Maintenance and Hardening
```

Do **not** create a new Initiative.

## Epic name

```text
Upstream Planning Governance And Templates
```

## Revised Issue set

```text
01. Redesign Initiative Requirement Design Plan Templates
02. Redesign Epic Requirement Design Plan Templates
03. Update Initiative And Epic Planning Skills And Workflow Docs
04. Update Epic Execution Handoff And Issue Readiness Workflow
05. Add Upstream Planning Smoke Tests And Template Validation
06. Epic Quality Gate Manual Tests And PR Delivery
```

## What changed in v2

- The scope-layering reference is **not an Issue**.
- The Epic itself owns the scope-layering analysis.
- Issues now perform concrete implementation slices.
- The last Issue explicitly performs final Epic QA, manual testing, PR readiness, review repair, and delivery.


## v3 completeness update

This v3 clean pack includes the upstream planning analysis that was previously only implicit in the conversation. Codex should not need the full chat transcript for Phase 3 implementation.

Additional analysis references:

- `reference/analysis-coverage-and-reading-order.md`
- `reference/upstream-abstraction-model.md`
- `reference/discovery-to-canonical-specs.md`
- `reference/initiative-design-playbook.md`
- `reference/epic-design-playbook.md`
- `reference/epic-to-issue-slicing-and-handoff.md`
- `reference/issue-tdd-handoff-model.md`
- `reference/reviewer-anti-patterns.md`

These files are not extra Issues. They are the Epic-level planning basis for the concrete Issue work.
```

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/codex-handoff.md`

```markdown
# Codex Handoff — Phase 3 v2

## Mission

Implement Phase 3 of SpecDock hardening: upgrade Initiative and Epic authoring templates, workflows, skills, handoffs, and validation so they correctly feed the already-updated grade-aware Issue templates and TDD execution plans.

## Parent Initiative

```text
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/
```

Do not create a new Initiative.

## Create or update this Epic

```text
Epic title: Upstream Planning Governance And Templates
```

If an equivalent Epic already exists, update it. Otherwise create it under `init-local-00003`.

## Core correction

Do not create a separate Issue just to define scope/planning boundaries.

The analysis of:

- Initiative vs Epic vs Issue responsibility;
- Requirement vs Design vs Plan vs Report responsibility;
- Discovery artifacts vs canonical specs;
- Epic-to-Issue slicing policy;
- Handoff contracts;
- scope drift anti-patterns;

belongs to the **Epic design and Epic plan**.

After that Epic-level design is clear, implement the concrete Issues listed below.

## Concrete Issues to implement

1. `Redesign Initiative Requirement Design Plan Templates`
2. `Redesign Epic Requirement Design Plan Templates`
3. `Update Initiative And Epic Planning Skills And Workflow Docs`
4. `Update Epic Execution Handoff And Issue Readiness Workflow`
5. `Add Upstream Planning Smoke Tests And Template Validation`
6. `Epic Quality Gate Manual Tests And PR Delivery`

## Hard guardrails

- Do not redesign the Issue grade templates created in Phase 1 unless a direct compatibility fix is required.
- Do not rename legacy `discussions/` directories.
- Do not move legacy discussion files.
- Do not make `artifacts/` canonical authority.
- Do not remove fresh `spec-reviewer` phase gates.
- Do not let specialist drafts directly replace canonical docs.
- Do not over-specify private implementation details at Initiative or Epic level.
- Do not convert this into a DDD-only tool; the templates may support DDD/EDA but should remain generally useful.
- Provider-side sources are primary: update `src/spec_dock/assets/...` first. Then inspect dogfooding mirror impact.

## Current repo facts to preserve

- New working artifacts are now created under `artifacts/`; legacy `discussions/` remains preservation evidence and should not be the recommended destination for new working artifacts.
- Generated nodes include `artifacts/rules.md`.
- Local test lanes include `uv run pytest tests/unit`, `make lint`, `uv run pytest tests/cli_runtime`, and full `uv run pytest`.
- `manual-tests/` is reserved for local manual test workspaces. Do not track raw fixtures/logs/captures under it; summarize evidence in the relevant SpecDock report/artifact.

## Required analysis references

Before editing files, read these references in addition to the Epic and Issue files:

1. `reference/analysis-coverage-and-reading-order.md`
2. `reference/upstream-abstraction-model.md`
3. `reference/discovery-to-canonical-specs.md`
4. `reference/initiative-design-playbook.md`
5. `reference/epic-design-playbook.md`
6. `reference/epic-to-issue-slicing-and-handoff.md`
7. `reference/issue-tdd-handoff-model.md`
8. `reference/reviewer-anti-patterns.md`

These references contain the upstream planning analysis from the design discussion. Do not create a separate Issue to implement these references as standalone work. Use them to shape the Initiative/Epic templates, skills, workflow docs, reviewer checklists, smoke tests, and final delivery gate.

## Expected final outcome

At the end of this Epic:

- Initiative templates express strategic planning: capability, context ownership, source of truth, strategic invariants, transition architecture, Epic handoff.
- Epic templates express target model planning: target model envelope, lifecycle, shared invariants, contract portfolio, issue slicing, issue handoff.
- Initiative/Epic skills guide agents through artifacts -> requirement -> design -> plan -> reviewer gates -> handoff.
- Epic execution skill coordinates downstream Issues and reports Epic-level evidence.
- Smoke tests validate the upstream authoring surface.
- Final delivery Issue runs automated checks, manual tests, review repair, and prepares a mergeable PR.
```

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/epic/epic-level-planning-analysis.md`

```markdown
# Epic-Level Planning Analysis — Do Not Make This a Separate Issue

This document captures the Epic-level design/planning decisions that must be settled before decomposing implementation Issues.

## 1. Why this belongs at Epic level

The previous Phase 3 pack proposed an Issue for defining Initiative/Epic/Issue planning boundaries. That is the wrong level because all subsequent implementation Issues depend on those boundaries.

If a single implementation Issue owns the layering model, then other Issues cannot correctly plan their own scope until that Issue is finished. Worse, a concrete implementation Issue becomes the owner of a cross-Issue design decision.

Therefore, the following are Epic-level design and planning responsibilities:

- Initiative / Epic / Issue responsibility model;
- Requirement / Design / Plan / Report responsibility model;
- Discovery artifact adoption model;
- Epic-to-Issue slicing policy;
- Issue handoff contract;
- scope drift detection;
- final Epic quality and delivery model.

## 2. Scope layering model

| Scope | Owns | Must not own |
|---|---|---|
| Initiative | Strategic change, capability landscape, context ownership, source of truth, strategic invariants, transition architecture | Aggregate methods, issue-level TDD cycles, private implementation details |
| Epic | One capability or model envelope, cross-Issue invariants, lifecycle, contract portfolio, design slice catalog, Issue handoff | Product-wide source-of-truth changes, private helpers, issue execution order beyond Issue slicing |
| Issue | One observable behavior or local model delta, local contract delta, local verification implications | Redefining Epic boundaries, broad Initiative decisions, unrelated refactors |
| Issue Plan | Execution order, Milestones, Behavior Backlog, TDD cycles, validation gates, report evidence mapping | New requirements, new design contracts, parent model changes |
| Report | Observed evidence, deviations, reviewer verdicts, adoption ledger, delivery evidence | Planned obligations, future architecture decisions |

## 3. Phase artifacts model

| Artifact | Role | Notes |
|---|---|---|
| artifacts/* | Working evidence: discovery, research, notes, candidates, drafts | Not canonical authority |
| requirement.md | What / why / acceptance / constraints | Should not contain implementation sequence |
| design.md | Responsibility, boundary, contract, model envelope or model delta | Should not become a step-by-step implementation plan |
| plan.md | Execution plan and verification sequence | Should not create new requirements/design decisions |
| report.md | Observed evidence ledger | Should not be the plan |

## 4. Handoff chain

```text
Initiative Design
  -> Initiative Plan
    -> Epic Requirement
      -> Epic Design
        -> Epic Plan
          -> Issue Requirement
            -> Issue Design
              -> Issue Plan
                -> Issue Report
```

Each handoff should identify:

- parent design IDs;
- inherited constraints;
- allowed delta;
- forbidden changes;
- required evidence;
- suggested downstream grade or workflow weight;
- open questions or escalation triggers.

## 5. Epic-to-Issue slicing policy

Good Issue slices are:

- executable;
- independently reviewable;
- tied to a capability/design slice;
- not decision-only containers;
- narrow enough for TDD execution;
- broad enough to produce an observable result.

Bad Issue slices:

- “define all planning boundaries”;
- “think about architecture”;
- “update many docs somehow”;
- “implement everything in this Epic”;
- “private helper refactor” without observable outcome;
- “Endpoint only” when the actual behavior spans domain/application/adapter.

## 6. Revised Epic issue slicing

The Epic-level analysis is captured here. Concrete implementation Issues are:

1. Redesign Initiative Templates.
2. Redesign Epic Templates.
3. Update Planning Skills and Workflow Docs.
4. Update Epic Execution Handoff Workflow.
5. Add Smoke Tests and Template Validation.
6. Final Epic Quality Gate, Manual Tests, and PR Delivery.

## 7. Final delivery policy

This Epic is delivered as one PR if possible. The last Issue owns:

- final automated validation;
- manual tests;
- dogfooding inspection;
- documentation/template consistency review;
- review comment repair loop;
- final report evidence;
- PR readiness.
```

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/epic/epic-upstream-planning-governance-and-templates-v2.md`

```markdown
# Epic — Upstream Planning Governance And Templates

## Parent

```text
init-local-00003 Architecture Maintenance and Hardening
```

## Status

```text
draft
```

## Purpose

Upgrade Initiative and Epic authoring so that upstream planning produces clear, bounded, executable downstream Issues that feed the existing grade-aware Issue templates and TDD execution plans.

This Epic does **not** create a separate Issue for defining planning boundaries. The planning-boundary model is owned by this Epic design and plan.

## Background

Phase 1 completed the Issue grade templates and Issue planning workflow. Phase 2 completed the `artifacts/` future working-artifact surface. Initiative and Epic templates remain comparatively thin and do not yet encode the upstream planning model needed to keep coding agents from drifting.

Current Initiative/Epic templates exist, but they are generic scaffolds. Initiative design currently has general system context and guardrail slots. Epic design currently has component/module, package dependency, domain model, contract, data boundary, flow, state/activity, failure, migration, and test strategy slots. These are useful, but they do not yet form a complete upstream handoff model for agent-safe Issue slicing.

## Design intent

Provide a durable upstream authoring governance layer:

- Initiative = strategic change and context/capability ownership.
- Epic = target capability/model envelope and Issue slicing.
- Issue = local executable model delta and TDD plan.
- Plan = execution order and evidence mapping.
- Report = observed evidence.

## Inherited constraints

- Preserve fresh `spec-reviewer` phase gates.
- Preserve main-orchestrator ownership of canonical docs.
- Specialist drafts remain evidence only.
- Preserve `artifacts/` as working evidence, not canonical authority.
- Do not rename `discussions/`.
- Do not redesign Issue grade templates.
- Provider-side assets are primary.

## In scope

- Initiative requirement/design/plan templates.
- Epic requirement/design/plan templates.
- Initiative planning skill.
- Epic planning skill.
- Epic execution skill.
- workflow_initiative.md / workflow_epic.md.
- phase docs where needed.
- reviewer/smoke test guidance.
- final Epic quality and PR delivery plan.

## Out of scope

- Issue grade template redesign.
- artifacts runtime command changes.
- GitHub integration behavior changes, except PR delivery guidance in final Issue.
- Automatic migration of existing docs.
- Making Initiative/Epic grade-specific template families.

## Target Epic design model

### Initiative templates should support

- Strategic purpose and success metrics.
- Actor/stakeholder landscape.
- Capability landscape.
- Subdomain/investment profile where useful.
- Context map / dependency map.
- Source of truth and decision ownership.
- Strategic invariants.
- Quality strategy.
- Transition architecture.
- Epic handoff.

### Epic templates should support

- Capability outcome and acceptance.
- Actor / trigger / use-case landscape.
- Target model envelope.
- Lifecycle/state model.
- Shared invariants.
- Command/query/event or operation portfolio when applicable.
- Contract portfolio.
- Consistency/failure/migration strategy.
- Design slice catalog.
- Issue handoff including suggested Issue grade.

### Skills should support

- Reading relevant artifacts without treating them as canonical.
- Creating canonical requirement/design/plan in the correct phase.
- Running fresh `spec-reviewer` gates.
- Using `system-architect` draft evidence for non-trivial Initiative/Epic planning.
- Preventing decision-only Issues from being execution-ready.
- Recording Spec Authoring Gate evidence in report.md.

## Issue list

| Issue | Title | Grade | Purpose |
|---|---|---|---|
| 01 | Redesign Initiative Requirement Design Plan Templates | strict | Update Initiative templates for strategic planning and Epic handoff |
| 02 | Redesign Epic Requirement Design Plan Templates | strict | Update Epic templates for target model envelope and Issue slicing |
| 03 | Update Initiative And Epic Planning Skills And Workflow Docs | strict | Align skills/docs with new templates and handoffs |
| 04 | Update Epic Execution Handoff And Issue Readiness Workflow | strict | Make Epic execution coordinate downstream Issues correctly |
| 05 | Add Upstream Planning Smoke Tests And Template Validation | strict | Validate templates, skills, and authoring flow |
| 06 | Epic Quality Gate Manual Tests And PR Delivery | critical | Run final automated/manual gates and prepare mergeable PR |

## Epic final gate

The Epic is complete only when:

- all six Issues are complete;
- Initiative/Epic templates are updated in provider assets;
- dogfooding mirror impact is inspected;
- workflow/skill docs are consistent;
- automated checks pass;
- manual tests are executed and summarized;
- PR is ready for review/merge;
- review feedback, if any, is repaired and re-validated.
```

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/issues/issue-01-redesign-initiative-templates.md`

```markdown
# Issue 01 — Redesign Initiative Requirement Design Plan Templates

## Suggested grade

```text
strict
```

## Purpose

Update Initiative `requirement.md`, `design.md`, and `plan.md` templates so they support strategic planning, capability/context ownership, transition architecture, and Epic handoff.

This Issue implements a concrete part of the Epic-level design. It does not own the scope-layering model; it applies that model to Initiative templates.

## Scope

### In scope

- `src/spec_dock/assets/spec_dock/templates/initiative/requirement.md`
- `src/spec_dock/assets/spec_dock/templates/initiative/design.md`
- `src/spec_dock/assets/spec_dock/templates/initiative/plan.md`
- Provider-side docs references if strictly required.
- Dogfooding mirror inspection.

### Out of scope

- Epic templates.
- Issue templates.
- Runtime commands.
- Planning skill updates.
- Smoke tests beyond local targeted validation.

## Required template direction

### Initiative requirement should capture

- strategic purpose;
- business/product outcome;
- success metrics;
- actor/stakeholder landscape;
- capability candidates;
- scope / non-goals / unchanged;
- constraints and quality requirements;
- transition/migration requirements;
- discovery artifacts as input;
- open questions and escalation triggers.

### Initiative design should capture

- design intent / domain vision;
- current strategic landscape;
- target capability landscape;
- subdomain or investment profile where useful;
- context map delta;
- decision/data ownership and source of truth;
- strategic invariants;
- context interaction strategy;
- quality strategy;
- transition architecture;
- risk/control;
- Epic design handoff;
- optional PlantUML/C4 diagrams.

### Initiative plan should capture

- capability/design slice catalog;
- Epic portfolio;
- Epic sequencing;
- transition tranches;
- dependency/blocker management;
- Epic readiness criteria;
- cross-Epic review gates;
- Epic handoff package;
- Initiative final gate.

## Acceptance criteria

- Initiative templates no longer read like generic task templates.
- Initiative design does not ask for aggregate methods, private classes, or TDD cycles.
- Initiative plan does not contain Issue-level execution steps.
- Templates support artifacts as discovery input but do not make artifacts canonical.
- Templates include handoff fields that downstream Epic planning can use.
- Templates are human-readable and agent-usable.
- PlantUML/C4 sections are optional and do not over-specify implementation.

## Suggested validation

- Inspect generated templates.
- `rg "private|TDD Cycle|Red-Green" src/spec_dock/assets/spec_dock/templates/initiative` should not reveal issue-level obligations except explicit “do not” guidance.
- Run relevant template/scaffold tests if available.
- Record dogfooding mirror impact in report.md.
```

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/issues/issue-02-redesign-epic-templates.md`

```markdown
# Issue 02 — Redesign Epic Requirement Design Plan Templates

## Suggested grade

```text
strict
```

## Purpose

Update Epic `requirement.md`, `design.md`, and `plan.md` templates so they support target capability/model envelope, cross-Issue invariants, design slice catalog, and Issue handoff.

This Issue applies the Epic-level slicing policy. It does not redefine the entire Initiative/Epic/Issue planning model.

## Scope

### In scope

- `src/spec_dock/assets/spec_dock/templates/epic/requirement.md`
- `src/spec_dock/assets/spec_dock/templates/epic/design.md`
- `src/spec_dock/assets/spec_dock/templates/epic/plan.md`
- Provider-side docs references if required.
- Dogfooding mirror inspection.

### Out of scope

- Initiative templates.
- Issue grade templates.
- Runtime commands.
- Skill changes.
- Full test harness.

## Required template direction

### Epic requirement should capture

- capability outcome;
- parent Initiative linkage;
- actor/trigger/use-case landscape;
- acceptance criteria;
- scope / non-goals / unchanged;
- cross-Issue constraints;
- quality/compatibility requirements;
- discovery artifacts;
- candidate Issue slices;
- open questions.

### Epic design should capture

- design intent;
- inherited Initiative constraints;
- target capability/model envelope;
- ubiquitous language delta;
- aggregate/model envelope where applicable;
- lifecycle/state model;
- shared invariants;
- operation/command/query/event portfolio where applicable;
- contract portfolio;
- consistency model;
- runtime scenarios;
- migration/compatibility strategy;
- design slice catalog;
- Issue design handoff.

### Epic plan should capture

- Issue slicing policy;
- design slice to Issue mapping;
- Issue list;
- suggested Issue grade;
- dependency graph;
- Issue readiness criteria;
- cross-Issue integration gates;
- artifact adoption rules;
- Epic completion gate.

## Acceptance criteria

- Epic requirement describes capability-level outcome, not implementation tasks.
- Epic design defines shared target model envelope and cross-Issue constraints.
- Epic plan produces executable Issue slices, not decision-only Issues.
- Epic plan can recommend downstream Issue grade.
- Epic handoff package includes enough detail to create Issue requirement/design/plan.
- Templates do not force private class/method design.
- PlantUML diagrams are optional but supported for model, dependency, sequence, state, and slicing views.

## Suggested validation

- Inspect templates for handoff fields.
- Verify no “decision-only Issue as execution-ready” wording.
- Run template/scaffold tests if available.
- Record dogfooding mirror impact in report.md.
```

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/issues/issue-03-update-planning-skills-and-workflow-docs.md`

```markdown
# Issue 03 — Update Initiative And Epic Planning Skills And Workflow Docs

## Suggested grade

```text
strict
```

## Purpose

Update Initiative/Epic planning skills and workflow docs so agents use the new upstream templates correctly and preserve phase gates.

## Scope

### In scope

- `spec-dock-initiative-planning/SKILL.md`
- `spec-dock-epic-planning/SKILL.md`
- `workflow_initiative.md`
- `workflow_epic.md`
- `phase_requirement.md`, `phase_design.md`, `phase_plan.md` if needed.
- `authoring/decision-routing.md` if needed.
- Guidance around artifacts as evidence.

### Out of scope

- Issue planning skill redesign.
- Runtime command implementation.
- Full guidance compiler rewrite.
- Spec-reviewer implementation.

## Required behavior

- Initiative planning skill must guide:
  - artifacts/discovery input;
  - requirement authoring;
  - fresh spec-reviewer gate;
  - design authoring;
  - fresh spec-reviewer gate;
  - plan authoring;
  - fresh spec-reviewer gate;
  - Epic handoff.

- Epic planning skill must guide:
  - artifacts/discovery input;
  - requirement authoring;
  - fresh spec-reviewer gate;
  - design authoring;
  - fresh spec-reviewer gate;
  - plan authoring;
  - fresh spec-reviewer gate;
  - Issue handoff.

- Both skills must explain that artifacts are evidence/input, not canonical authority.
- Both skills must preserve main-orchestrator ownership of canonical docs.
- Both skills must preserve `system-architect` draft as evidence only.
- Both skills must route scope expansion, destructive actions, external publishing, credentialed external mutation, private external systems, and out-of-workflow roles to user confirmation.

## Acceptance criteria

- Initiative planning skill matches new Initiative templates.
- Epic planning skill matches new Epic templates.
- Fresh `spec-reviewer` phase gates are preserved.
- system-architect draft rules are preserved and clarified.
- Decision-only containers are not treated as execution-ready.
- `artifacts/` is the recommended place for new working artifacts.
- Legacy `discussions/` is not recommended for new work.
- Skills are concise enough to be first-read routing guidance.

## Suggested validation

- `rg "discussions/" src/spec_dock/assets/install_root/.agents/skills src/spec_dock/assets/spec_dock/docs` and confirm legacy wording is intentional.
- Manual read-through: from skill alone, an agent knows what to do next.
- Fresh reviewer gate references remain.
```

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/issues/issue-04-update-epic-execution-handoff-workflow.md`

```markdown
# Issue 04 — Update Epic Execution Handoff And Issue Readiness Workflow

## Suggested grade

```text
strict
```

## Purpose

Update Epic execution workflow so an Epic can coordinate downstream Issues created from Epic plan handoff, track cross-Issue integration, and record Epic-level evidence.

## Scope

### In scope

- `spec-dock-epic-execution/SKILL.md`
- `workflow_epic.md`
- `phase_plan_epic.md`
- Epic report evidence guidance if present.
- Issue readiness criteria and handoff package definition.

### Out of scope

- Issue execution lifecycle redesign.
- PR merge automation.
- GitHub mutation command changes.

## Required behavior

Epic execution must be able to coordinate:

- which Issues are ready;
- which Issues are blocked;
- dependency edges;
- suggested Issue grades;
- parent Epic design IDs inherited by each Issue;
- cross-Issue integration gates;
- docs/template/skill impact;
- Epic completion evidence.

## Handoff package from Epic plan to Issue

Each Issue slice should include:

- Issue title;
- purpose;
- related Epic Requirement IDs;
- related Epic Design IDs;
- allowed Model/Contract Delta;
- forbidden parent boundary changes;
- suggested Issue Grade;
- required Acceptance Criteria;
- required Verification Level;
- dependency edges;
- relevant artifacts;
- open questions or escalation triggers.

## Acceptance criteria

- Epic execution skill can coordinate ready Issues based on Epic plan handoff.
- Epic plan warns against decision-only Issues as execution-ready.
- Epic completion gate includes downstream Issue completion, cross-Issue integration, docs impact, and report evidence.
- Epic execution can record skipped/deferred/follow-up Issues.
- Issue grade templates are referenced as downstream surfaces.
- Existing Issue execution path is not redesigned.

## Suggested validation

- Manual read-through of Epic execution skill.
- Validate no contradiction with issue start/finish lifecycle.
- Template/skill smoke with one sample Epic plan handoff.
```

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/issues/issue-05-add-upstream-planning-smoke-tests.md`

```markdown
# Issue 05 — Add Upstream Planning Smoke Tests And Template Validation

## Suggested grade

```text
strict
```

## Purpose

Add smoke tests or validation checks showing that the updated Initiative/Epic templates and skills form a coherent authoring flow.

## Scope

### In scope

- Template existence checks.
- Required section checks.
- Skill text smoke checks.
- Workflow doc smoke checks.
- Provider-side template validation.
- Dogfooding mirror inspection.
- `validate` / `sync` smoke if appropriate.

### Out of scope

- Real subagent execution.
- GitHub mutation.
- Full E2E project generation beyond lightweight smoke.
- Issue grade template retesting except as downstream compatibility.

## Acceptance criteria

- Initiative requirement/design/plan templates contain required strategic sections.
- Epic requirement/design/plan templates contain required target model and issue slicing sections.
- Initiative planning skill references the new flow and reviewer gates.
- Epic planning skill references the new flow and reviewer gates.
- Epic execution skill references issue handoff and grade-aware downstream authoring.
- Templates do not ask for Issue-level TDD cycles at Initiative/Epic level.
- Templates do not require private class/method design at Initiative/Epic level.
- New artifact guidance uses `artifacts/`, not `discussions/`, for new working artifacts.
- `validate` / `sync` smoke passes or any failure is documented.

## Suggested test ideas

- Unit test reads template files and checks required headings.
- Runtime scaffold smoke creates Initiative/Epic and verifies template shape.
- Skill text smoke checks for fresh spec-reviewer gate wording.
- Skill text smoke checks for `artifacts/` guidance.
- Negative grep checks for banned phrases where appropriate.

## Suggested commands

```bash
uv run pytest tests/unit
uv run pytest tests/cli_runtime
make lint
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync
```

Use the repository's available commands; do not invent unsupported ones.
```

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/issues/issue-06-epic-quality-gate-manual-tests-and-pr-delivery.md`

```markdown
# Issue 06 — Epic Quality Gate Manual Tests And PR Delivery

## Suggested grade

```text
critical
```

## Purpose

Perform the final Epic-level quality gate, run manual tests, repair review feedback, and prepare a mergeable pull request for the entire Epic.

This Issue is intentionally a delivery/quality Issue. It exists because the Epic is expected to be delivered as a coherent PR, and final integration quality cannot be guaranteed by the earlier implementation Issues alone.

## Scope

### In scope

- Full Epic validation.
- Automated tests.
- Static analysis.
- SpecDock validate/sync.
- Manual tests using `manual-tests/` guidance.
- Dogfooding workspace inspection.
- Provider vs dogfooding mirror review.
- Documentation/template/skill consistency review.
- Review feedback repair loop.
- Final report evidence.
- PR readiness checklist.
- PR creation if authorized in the active Codex environment.

### Out of scope

- New feature work beyond fixing issues found by quality gates.
- New Initiative/Epic planning decisions.
- Destructive operations.
- Credentialed external mutation without explicit authorization.
- Merging the PR unless explicitly authorized.

## Manual test policy

Use the repository's `manual-tests/` guidance:

- Create a trial directory under `manual-tests/`.
- Initialize an independent Git repository inside the trial directory if SpecDock state is needed.
- Keep trial repositories self-contained.
- Do not rely on the parent repository's Git history, index, or active SpecDock state as test data.
- Do not track raw manual-test workspaces, fixtures, logs, captures, or evidence files in the parent repo.
- Summarize any useful evidence in the relevant SpecDock report/artifact.

## Required automated gates

Use available project commands:

```bash
uv run pytest tests/unit
uv run pytest tests/cli_runtime
make lint
uv run pytest
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync
```

If a command is unavailable or inappropriate, record the reason in report.md.

## Required manual tests

At minimum, manually verify:

1. A new Initiative scaffold uses updated Initiative templates.
2. A new Epic scaffold uses updated Epic templates.
3. Initiative planning skill points to the correct workflow and phase docs.
4. Epic planning skill points to the correct workflow and phase docs.
5. Epic execution skill can be read as a handoff/execution coordinator.
6. `artifacts/` is referenced for new working artifacts.
7. Legacy `discussions/` is not suggested as the primary new working artifact destination.
8. The new Initiative/Epic templates do not include Issue-level TDD cycles.
9. The new Initiative/Epic templates do not force private implementation details.
10. Generated/dogfooding docs remain coherent after sync/validate.

## Pull request delivery checklist

- [ ] Branch is clean except intended changes.
- [ ] Commit history is coherent.
- [ ] All earlier Issues are completed or explicitly deferred.
- [ ] All automated gates are passing or documented with acceptable waiver.
- [ ] Manual test evidence is summarized in report.md or artifact.
- [ ] Reviewer comments are addressed.
- [ ] Re-run relevant checks after review repair.
- [ ] PR description includes scope, validation, manual tests, and follow-ups.
- [ ] PR does not include raw manual-test workspaces.
- [ ] PR is mergeable, but merge is not performed unless authorized.

## Acceptance criteria

- Epic-level quality gate is complete.
- Manual tests have been executed and summarized.
- Automated tests and lint are passing or documented with clear reason.
- SpecDock validate/sync evidence is recorded.
- Provider and dogfooding mirror impact is reviewed.
- Any review comments are repaired and revalidated.
- PR is ready for review/merge.
- report.md contains final delivery evidence.

## Stop conditions

- Manual tests reveal broken scaffold/skill workflow.
- Full validation reveals serious regression.
- Raw manual-test files are accidentally staged.
- PR would require credentialed external mutation without authorization.
- New design decisions are needed beyond this Epic's approved scope.
```

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/reference/current-state-summary.md`

```markdown
# Current State Summary

These observations are based on the current public repository state at the time this pack was prepared.

## Useful facts

- `spec-dock` is a scaffold tool. After `init`, day-to-day operations are done via `./spec-dock/scripts/spec-dock`.
- New working artifacts are now created under `artifacts/` with `new artifact <type>`.
- Existing `discussions/` docs are legacy/preservation evidence and should not be the recommended destination for new working artifacts.
- Generated nodes include `artifacts/rules.md`.
- The repository has `manual-tests/`, reserved for local manual test workspaces.
- The repository test lanes include `tests/unit`, `tests/cli_runtime`, `tests/integration`, `make lint`, and full `uv run pytest`.

## Current upstream templates are thin

Current Initiative templates are short scaffolds. They need stronger strategic planning structure.

Current Epic templates have useful sections, including component/module, package dependency, domain model, contracts, data boundary, flow, state/activity, failure, migration, observability/security, and test strategy. They need to become target model / issue slicing / handoff templates.

## Current skills already have valuable constraints

Initiative and Epic planning skills already:

- require fresh `spec-reviewer` pass before phase promotion;
- route decision-only containers away from execution-ready lower scopes;
- treat specialist drafts as evidence only;
- keep canonical docs under main orchestrator authority;
- point to `artifacts/` for new rationale.

Do not weaken these constraints.
```

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/reference/guardrails.md`

```markdown
# Phase 3 Guardrails

## Do

- Update provider-side assets first.
- Keep Initiative/Epic abstractions higher than Issue execution details.
- Preserve fresh spec-reviewer gates.
- Preserve artifacts as working evidence.
- Add optional PlantUML sections for human readability.
- Ensure downstream Issue handoff includes suggested Issue grade and required verification levels.
- Add final Epic quality/PR delivery Issue.

## Do not

- Create a separate Issue for defining the entire scope-layering model.
- Redesign Issue grade templates.
- Rename legacy `discussions/`.
- Move or rewrite legacy links.
- Remove fresh reviewer gates.
- Make artifacts canonical.
- Let system-architect or other specialists directly replace canonical docs.
- Force Initiative/Epic templates to include private class/method details.
- Put TDD cycle details into Initiative/Epic templates.
- Skip manual tests in the final delivery Issue.
```

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/reference/manual-test-and-delivery-checklist.md`

```markdown
# Manual Test and Delivery Checklist

Use this in Issue 06.

## Manual test setup

- Create a trial directory under `manual-tests/`.
- Initialize a separate Git repository inside the trial directory if SpecDock state is needed.
- Do not rely on parent repository Git history/index/active state.
- Do not commit raw manual-test workspaces, fixtures, logs, captures, or evidence files.
- Summarize evidence in the relevant report/artifact.

## Manual test scenarios

1. Initialize or simulate a fresh SpecDock workspace.
2. Create a new Initiative and inspect template shape.
3. Create a new Epic and inspect template shape.
4. Confirm Initiative templates do not include Issue-level TDD cycles.
5. Confirm Epic templates include Issue handoff and suggested grade fields.
6. Confirm Initiative planning skill guides artifacts -> requirement -> review -> design -> review -> plan -> review -> Epic handoff.
7. Confirm Epic planning skill guides artifacts -> requirement -> review -> design -> review -> plan -> review -> Issue handoff.
8. Confirm Epic execution skill coordinates Issue readiness and Epic evidence.
9. Confirm `artifacts/` is the recommended destination for new working artifacts.
10. Confirm legacy `discussions/` is not mutated.

## Automated checks

Use available commands:

```bash
uv run pytest tests/unit
uv run pytest tests/cli_runtime
make lint
uv run pytest
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync
```

Record missing or failing commands with reason.

## PR delivery

- Prepare a PR with scope/validation/manual-test/follow-up sections.
- Address review comments.
- Re-run relevant checks after repair.
- Do not merge unless explicitly authorized.
```

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/reference/quality-gate-plan.md`

```markdown
# Epic Quality Gate Plan

The final Issue owns Epic-level quality and delivery.

## Quality dimensions

- Requirement/design/plan consistency.
- Initiative template correctness.
- Epic template correctness.
- Planning skill correctness.
- Epic execution skill correctness.
- Handoff completeness.
- Artifact/canonical boundary correctness.
- Automated tests.
- Manual tests.
- PR delivery readiness.

## Minimum gates

- Unit tests.
- CLI runtime tests.
- Static analysis.
- Validate/sync.
- Manual scaffold/skill review.
- Dogfooding mirror inspection.
- Report evidence.

## Repair loop

If review comments appear:

1. Record comment.
2. Classify whether it is bug, scope drift, template insufficiency, docs inconsistency, or new requirement.
3. Fix only in-scope issues.
4. Re-run affected tests.
5. Update report evidence.
6. Re-request review.

## PR readiness

A PR is ready when:

- all Issues complete or explicitly deferred;
- quality gates pass or waivers are documented;
- manual test evidence is summarized;
- raw manual-test files are not committed;
- PR description explains scope, validation, manual tests, and follow-ups.
```

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/reference/revised-issue-slicing-rationale.md`

```markdown
# Revised Issue Slicing Rationale

## Why the previous Issue 1 was removed

The previous pack put scope-layering analysis into an Issue. That made an Issue responsible for decisions that all other Issues depend on.

This creates a planning dependency problem:

```text
Issue A defines the rules
Issue B/C/D cannot be planned correctly until A is complete
```

But those rules are not an implementation slice. They are the Epic's own design and planning basis.

## Correct slicing

Epic design owns the rules. Issues implement concrete deltas:

1. Initiative templates.
2. Epic templates.
3. Skills and workflow docs.
4. Epic execution/handoff workflow.
5. Smoke tests.
6. Final quality and PR delivery.

Each Issue is now concrete, executable, and reviewable.
```

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/reference/suggested-file-map.md`

```markdown
# Suggested File Map

## Templates

```text
src/spec_dock/assets/spec_dock/templates/initiative/requirement.md
src/spec_dock/assets/spec_dock/templates/initiative/design.md
src/spec_dock/assets/spec_dock/templates/initiative/plan.md

src/spec_dock/assets/spec_dock/templates/epic/requirement.md
src/spec_dock/assets/spec_dock/templates/epic/design.md
src/spec_dock/assets/spec_dock/templates/epic/plan.md
```

## Skills

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md  # only if needed
```

## Docs

```text
src/spec_dock/assets/spec_dock/docs/workflow_initiative.md
src/spec_dock/assets/spec_dock/docs/workflow_epic.md
src/spec_dock/assets/spec_dock/docs/phase_requirement.md
src/spec_dock/assets/spec_dock/docs/phase_design.md
src/spec_dock/assets/spec_dock/docs/phase_plan.md
src/spec_dock/assets/spec_dock/docs/phase_plan_initiative.md
src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md
src/spec_dock/assets/spec_dock/docs/authoring/decision-routing.md
src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md  # if added
```

## Tests

```text
tests/unit/...
tests/cli_runtime/...
manual-tests/README.md  # reference only; do not add raw trial files to git
```

## Dogfooding mirror

Inspect or update only when needed:

```text
spec-dock/templates/initiative/...
spec-dock/templates/epic/...
spec-dock/docs/...
.agents/skills/...
```
```

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/reference/analysis-coverage-and-reading-order.md`

```markdown
# Analysis Coverage and Reading Order

This v3 pack is designed so Codex can work without the prior chat transcript.

The v2 pack had the corrected Issue slicing and final delivery Issue, but it was too thin on the upstream planning reasoning behind those decisions. This v3 pack adds durable references for the analysis that should live at Epic level rather than in a separate implementation Issue.

## Coverage added in v3

- Initiative / Epic / Issue abstraction boundaries.
- Requirement / Design / Plan / Report responsibility boundaries.
- Discovery artifacts vs canonical specs.
- Initiative strategic design model.
- Epic target model / design envelope model.
- Epic-to-Issue slicing and handoff model.
- Issue-to-TDD handoff model.
- Reviewer anti-patterns and scope-drift detection.

## Recommended reading order

1. `codex-handoff.md`
2. `epic/epic-upstream-planning-governance-and-templates-v2.md`
3. `epic/epic-level-planning-analysis.md`
4. `reference/upstream-abstraction-model.md`
5. `reference/discovery-to-canonical-specs.md`
6. `reference/initiative-design-playbook.md`
7. `reference/epic-design-playbook.md`
8. `reference/epic-to-issue-slicing-and-handoff.md`
9. `reference/issue-tdd-handoff-model.md`
10. `reference/reviewer-anti-patterns.md`
11. `reference/*.md` remaining files
12. `issues/*.md` in numeric order

## Important instruction

Do not create a separate Issue for these reference concepts.

The concepts in this directory are Epic-level planning and design input. The concrete implementation Issues remain the six Issues already listed in `issues/`.
```

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/reference/upstream-abstraction-model.md`

```markdown
# Upstream Abstraction Model

This reference defines the abstraction boundaries that Phase 3 must encode into templates, workflows, and skills.

## 1. Two hierarchies must not be confused

SpecDock work hierarchy:

```text
Initiative
└── Epic
    └── Issue
        └── Issue Plan
            └── TDD Cycle
```

Domain/model hierarchy, when relevant:

```text
Domain
└── Subdomain
    └── Bounded Context
        └── Aggregate / Model / Read Model / Process
            └── Operation / Behavior
```

These are not one-to-one.

Invalid fixed mappings:

```text
Initiative = Bounded Context
Epic       = Aggregate
Issue      = Endpoint
```

## 2. Scope ownership

| Scope | Primary question | Owns | Must not own |
|---|---|---|---|
| Initiative | What strategic product/domain change are we making? | Capability landscape, context ownership, source of truth, strategic invariants, transition architecture | Aggregate method signatures, Issue TDD cycles, private implementation structure |
| Epic | What capability/model envelope must multiple Issues share? | Target model envelope, lifecycle, cross-Issue invariants, contract portfolio, design slice catalog, Issue handoff | Product-wide context ownership changes, private helpers, detailed TDD cycles |
| Issue | What concrete observable behavior or local model delta will be implemented? | Requirement acceptance, local design delta, local contract delta, verification implications | Redefining Epic envelope, new strategic decisions, unrelated refactors |
| Issue Plan | How will this Issue be executed and verified? | Milestones, Behavior Backlog, Active TDD Cycle, validation ladder, report evidence mapping | New requirements, new design contracts, parent model changes |
| Report | What actually happened? | Evidence, Red/Green results, review verdicts, deviations, artifact adoption ledger | Planned obligations, future architecture decisions |

## 3. Artifact ownership

| Artifact | Role | Authority |
|---|---|---|
| `artifacts/*` | Discovery, research, notes, drafts, candidates, evidence | Working evidence only |
| `requirement.md` | What must be true and why | Canonical requirement artifact |
| `design.md` | How responsibilities, boundaries, contracts, and model deltas make the requirement possible | Canonical design artifact |
| `plan.md` | How to implement and verify | Canonical planned execution artifact |
| `report.md` | What was observed and decided during/after execution | Canonical evidence ledger |

## 4. Decision Radius rule

A decision belongs at the lowest scope that can fully own its consequences without hiding future work.

| Decision radius | Correct owner |
|---|---|
| Multiple Initiatives or global architecture | ADR / architecture docs |
| Multiple Epics in one Initiative | Initiative design |
| Multiple Issues in one Epic | Epic design |
| One Issue | Issue design |
| One implementation sequence | Issue plan |
| One local private implementation detail | Code/tests |

## 5. Promotion direction

Upper scopes constrain lower scopes. Lower scopes may discover new information, but broad decisions must be promoted upward before becoming canonical.

```text
Discovery artifact
  -> hypothesis
    -> accepted design decision
      -> downstream handoff
        -> implementation evidence
```

If an Issue discovers an Epic boundary problem, it should not silently redefine the Epic model. It should record evidence in `report.md` and update Epic design or create a follow-up.

## 6. What Phase 3 must encode

- Initiative templates ask for strategic design, not implementation details.
- Epic templates ask for shared model/capability envelopes, not private code structure.
- Epic plans slice work into executable Issues with handoff packages.
- Skills guide agents to use artifacts as inputs but canonical docs as authority.
- Reviewers can detect scope drift.
```

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/reference/discovery-to-canonical-specs.md`

```markdown
# Discovery to Canonical Specs

Phase 2 introduced or stabilized `artifacts/` as the future working artifact surface. Phase 3 must connect that surface to Initiative and Epic authoring.

## 1. Discovery is not canonical design

Discovery outputs can contain observations, contradictory language, abandoned hypotheses, and exploratory diagrams. They must not be treated as accepted requirements or design decisions.

Examples:

- actor-goal-map
- big-picture-eventstorming
- process-eventstorming
- use-case-notes
- context-candidate
- aggregate-candidate
- state-model-candidate
- contract-candidate
- research
- interview
- decision-candidate
- blank notes

## 2. Maturity statuses

| Status | Meaning |
|---|---|
| raw | Unprocessed notes or transcript-like material |
| observed | A grounded observation with source/context |
| hypothesis | A possible interpretation or design direction |
| candidate | A possible capability/context/model/slice/decision |
| proposed | Proposed for adoption into canonical docs |
| adopted | Reflected into requirement/design/plan/ADR |
| partially-adopted | Some parts reflected, some not |
| rejected | Considered and not adopted |
| superseded | Replaced by a newer artifact or decision |

## 3. Adoption rule

Artifacts become useful to Codex only when the relevant facts are reflected into canonical docs or explicitly adopted in report evidence.

```text
artifact note
  -> requirement/design/plan update
  -> report adoption evidence
```

Do not implement directly from raw artifacts when canonical specs disagree or are missing.

## 4. Initiative Discovery

Used when domain/capability boundaries are not yet clear.

Good artifacts:

- actor ecosystem
- actor-goal map
- big-picture event storming
- current process map
- capability candidates
- bounded-context candidates
- source-of-truth analysis
- strategic risk research
- transition risk notes

Feeds Initiative requirement/design:

- strategic purpose
- capability landscape
- context map
- source of truth
- strategic invariants
- transition architecture

## 5. Epic Discovery

Used when a capability is known but model envelope and Issue slices are unclear.

Good artifacts:

- process event storming
- use-case model
- command/event/policy candidates
- lifecycle candidates
- aggregate/model envelope candidates
- read-model candidates
- contract candidates
- Issue slice candidates

Feeds Epic requirement/design/plan:

- capability outcome
- target model envelope
- lifecycle
- cross-Issue invariants
- contract portfolio
- design slice catalog
- Issue handoff

## 6. EventStorming levels

| EventStorming form | Typical scope | Output |
|---|---|---|
| Big Picture | Initiative discovery | events, hotspots, phases, capability/context candidates |
| Process Modelling | Epic discovery | actor/command/event/policy/read model candidates |
| Software Design | Epic design or Issue design | model candidates, operations, events, policies |

Do not finalize Aggregates from Big Picture EventStorming alone. Treat them as candidates and validate at Epic design level.

## 7. Use case modelling levels

| Use case form | Typical scope |
|---|---|
| Actor-goal map without fixed system boundary | Initiative discovery |
| Use case diagram around a primary context/capability | Epic discovery/requirement |
| Single use case scenario with preconditions/alternatives | Issue requirement |

## 8. Phase 3 implication

Initiative/Epic templates and skills should ask:

- Which artifacts were considered?
- Which were adopted?
- Which were rejected or deferred?
- Which canonical sections reflect them?
- What remains open?
```

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/reference/initiative-design-playbook.md`

```markdown
# Initiative Design Playbook

An Initiative design is not a larger Epic design. It is a strategic change design.

## 1. Definition

```text
Initiative Design
=
Strategic intent
+ Current/Target capability landscape
+ Subdomain investment profile
+ Bounded Context map delta
+ Source of Truth / decision ownership
+ Strategic invariants
+ Context interaction strategy
+ Quality strategy
+ Transition architecture
+ Epic design handoff
```

## 2. Initiative Requirement

Initiative requirement answers:

```text
Why is this strategic change needed?
What business/product outcome must be achieved?
How will success be measured?
What is in scope / out of scope / unchanged?
What constraints and quality requirements shape the work?
```

It should include:

- strategic purpose
- business / product outcomes
- success metrics
- actors / stakeholders
- capability candidates
- scope / non-goals / unchanged
- constraints
- quality requirements
- transition or rollout requirements
- discovery artifacts
- open questions

It should not include Aggregate methods, endpoint schemas, Issue-level TDD steps, or file edit order.

## 3. Initiative Design

Initiative design answers:

```text
What future domain/capability landscape makes the requirement possible?
Which contexts own which decisions/data?
How do contexts interact?
What strategic invariants must every Epic obey?
How can we transition safely from current to target?
```

Core sections:

### Design Intent / Domain Vision

Short statement of the strategic model direction and where design investment matters.

### Current Strategic Landscape

Current capabilities, actors, context boundaries, manual steps, integration pain, source-of-truth ambiguity.

### Target Capability Landscape

Table of capability, actor/trigger, owning context, observable result.

### Subdomain / Investment Profile

Classify subdomains as Core / Supporting / Generic when useful. This directs modelling effort.

### Context Map Delta

Describe current and target Bounded Context relationships, ownership, upstream/downstream, ACL/published language, and what changes.

### Decision / Data Ownership

Matrix:

| Concept / Decision | Source of Truth | Consumers | Write authority | Consistency |
|---|---|---|---|---|

### Strategic Invariants

Cross-Epic rules, for example:

- Only one context writes a given business decision.
- No distributed transaction across contexts.
- Sensitive data does not cross unauthorized boundaries.
- Legacy and target systems do not both own the same write decision.

### Context Interaction Strategy

For each interaction: producer, consumer, business meaning, style, consistency, failure behavior, delegated Epic detail.

### Quality Strategy

Map quality requirements to design strategies, not just metrics.

### Transition Architecture

Current, target, valid intermediate states, coexistence, rollback / forward-only boundaries, decommission criteria.

### Epic Design Handoff

For each proposed Epic, provide:

- capability slice
- primary context
- strategic invariants
- source-of-truth constraints
- context interaction semantics
- transition constraints
- forbidden decisions
- quality evidence required

## 4. Initiative Plan

Initiative plan answers:

```text
Which Epics will realize the target design, in what sequence, under what dependencies and gates?
```

It should include:

- design slice / capability slice catalog
- Epic portfolio
- dependency and sequencing
- transition tranches
- risk-first validation order
- Epic readiness criteria
- cross-Epic integration / quality gates
- handoff package for each Epic

## 5. PlantUML suggestions

Useful diagrams:

- context map
- capability map
- sequence across contexts
- transition state diagram
- dependency graph of Epics

Do not draw implementation class diagrams at Initiative level.

## 6. Anti-patterns

- Initiative design lists endpoint payloads.
- Initiative plan lists file edits.
- Initiative design declares private methods.
- Initiative plan creates Issue lists directly without Epic design handoff.
- Initiative docs copy all Epic content instead of defining strategic envelope.
```

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/reference/epic-design-playbook.md`

```markdown
# Epic Design Playbook

An Epic design is not a larger Issue design. It is a shared design envelope for multiple Issues.

## 1. Definition

```text
Epic Design
=
Inherited Initiative constraints
+ Target capability model
+ Target model / aggregate envelope
+ lifecycle / state model
+ shared cross-Issue invariants
+ command / query / event portfolio
+ contract portfolio
+ consistency model
+ runtime scenarios
+ design slice catalog
+ Issue handoff
```

## 2. Epic Requirement

Epic requirement answers:

```text
What capability must be delivered?
Who or what triggers it?
What observable outcomes and acceptance conditions matter?
What cross-Issue constraints apply?
```

It should include:

- capability outcome
- actors / triggers / use cases
- acceptance criteria
- scope / non-goals / unchanged
- cross-Issue constraints
- quality / compatibility requirements
- discovery artifacts
- Issue slice candidates
- open questions

It should not include private helpers, exact TDD cycles, detailed file edit order, or complete Issue design deltas.

## 3. Epic Design

Epic design answers:

```text
What shared model/capability envelope must downstream Issues implement consistently?
```

Core sections:

### Design Intent

What model/capability direction is being established?

### Inherited Initiative Constraints

Source of truth, context ownership, strategic invariants, context interaction semantics, transition constraints.

### Target Capability Model

What capabilities exist at Epic completion? Who triggers them? What is observable?

### Ubiquitous Language Delta

Terms, definitions, excluded meanings, context-specific differences.

### Target Model / Aggregate Envelope

When DDD applies, define the envelope:

- model/aggregate/root name
- responsibility
- boundary
- owned concepts
- external references
- major invariants
- lifecycle
- concurrency unit
- repository or persistence boundary
- events or facts emitted

If not DDD, use the equivalent component/model envelope.

### Lifecycle / State Model

State diagram and state meaning across Issues.

### Shared Invariants

Rules that all downstream Issues must preserve.

### Command / Query / Event Portfolio

Portfolio, not full Issue contract.

### Contract Portfolio

APIs, events, templates, metadata, CLI contracts at portfolio level. Full schemas belong to Issue or machine-readable contract files.

### Runtime Scenarios

Representative flows:

- main success flow
- important failure flow
- duplicate/retry/recovery flow
- cross-context/event flow when relevant

### Consistency Model

Synchronous boundary, eventual boundary, idempotency, ordering, retry, recovery.

### Design Slice Catalog

Bridge to Epic plan.

| Slice ID | Capability slice | Owner model/context | Result | Dependencies | Suggested Issue grade |
|---|---|---|---|---|---|

## 4. Epic Plan

Epic plan answers:

```text
How will the target model/capability be sliced into executable Issues?
```

It should include:

- Issue slicing policy
- design slice to Issue mapping
- Issue list
- suggested Issue grade
- dependency graph
- Issue readiness criteria
- Issue handoff package
- cross-Issue integration gates
- Epic completion gate

## 5. Good Issue slices

Good Issue:

- has one main actor/trigger or one coherent system trigger;
- has one observable result;
- has one primary model/context responsibility;
- is independently reviewable;
- can be tested/verified;
- has a clear handoff from Epic design.

Bad Issue:

- “define all planning boundaries”;
- “think about architecture”;
- “implement the Epic”;
- “edit all docs somehow”;
- “refactor private helpers” without observable result;
- “create an endpoint” while hiding domain/application/persistence implications.

## 6. PlantUML suggestions

Useful diagrams:

- package/component model envelope
- class/model diagram for aggregate envelope
- state diagram for lifecycle
- sequence diagram for representative runtime flow
- dependency graph of design slices / Issues

Do not over-specify private methods or helper structures.

## 7. Anti-patterns

- Epic design becomes a giant Issue design.
- Epic plan becomes a task checklist with no design-slice mapping.
- Epic design fixes all method signatures before TDD.
- Epic allows each Issue to redefine shared lifecycle.
- Epic hands off Issues without required design IDs or verification levels.
```

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/reference/epic-to-issue-slicing-and-handoff.md`

```markdown
# Epic to Issue Slicing and Handoff

This reference defines how Epic design and plan produce executable Issues.

## 1. Design Slice before Issue

An Epic should first identify design slices or capability slices. An Issue is then created from one or more coherent slices.

```text
Epic Target Model
  -> Design Slice Catalog
    -> Issue Candidate
      -> Issue Requirement
        -> Issue Design
          -> Issue Plan
```

## 2. Design Slice Catalog

Example table:

| Slice ID | Capability slice | Owner | Trigger | Result | Shared constraints | Suggested Issue grade |
|---|---|---|---|---|---|---|
| SL-001 | Create draft | Settlement | command | draft exists | INV-001 | standard |
| SL-002 | Finalize | Settlement | command | finalized event | INV-002, OUTBOX | strict |
| SL-003 | Consumer projection | Projection | event | read model updated | idempotency | strict |

## 3. Issue handoff package

Each downstream Issue should receive:

- parent Initiative/Epic IDs
- applicable parent requirement IDs
- applicable parent design IDs
- allowed local delta
- forbidden changes
- acceptance criteria seed
- model/contract/lifecycle constraints
- expected evidence type
- suggested Issue grade
- dependencies
- escalation triggers

## 4. Issue readiness criteria

Do not create an execution-ready Issue until:

- the parent Epic design envelope is sufficient;
- the Issue has one coherent observable outcome;
- required parent constraints are known;
- major open questions are resolved or explicitly scoped;
- suggested grade is known;
- the Issue can be reviewed independently.

## 5. Vertical slicing

Prefer vertical slices:

```text
trigger -> application coordination -> model decision -> persistence/contract -> observable result
```

Avoid horizontal slices:

```text
build all domain classes
then build all repositories
then build all APIs
then write tests
```

A vertical Issue may touch multiple layers if they serve one behavior.

## 6. Endpoint is not always Issue boundary

An endpoint can be a good Issue if it represents one use case. But an Issue should be behavior-based, not endpoint-based.

Bad:

```text
Add POST /finalize
```

Better:

```text
Finalize ready settlement and record outbox event atomically
```

## 7. Suggested grade from Epic plan

The Epic plan should suggest Issue grade based on risk:

| Signal | Suggested grade |
|---|---|
| docs-only or wording | lite |
| normal local behavior | standard |
| public/shared contract, compatibility, migration, workflow, metadata | strict |
| safety/security/privacy/destructive/GitHub mutation/rollback-hard | critical |

## 8. Avoid decision-only Issues

Decision-only work belongs in Epic design, Initiative design, ADR, or artifacts depending on scope. Do not create an Issue that only says “analyze boundaries” unless it produces an accepted canonical artifact and is explicitly a planning/doc Issue.

For Phase 3, the scope-layering model belongs in the Epic itself, not an Issue.
```

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/reference/issue-tdd-handoff-model.md`

```markdown
# Issue TDD Handoff Model

This reference explains how upstream Initiative/Epic planning should connect to the already-updated Issue templates and TDD execution plans.

## 1. Issue Requirement

Issue requirement defines:

- observable outcome
- actors/triggers
- scope / non-goals / unchanged
- acceptance criteria
- constraints
- edge cases
- grade signals
- design handoff inputs

It must not define class details, method internals, TDD cycle order, or file edit sequence.

## 2. Issue Design

Issue design defines:

- inherited parent constraints
- current state
- target model delta
- responsibility model
- contract/interface delta
- failure/compatibility semantics
- verification implications
- plan handoff

It should not become the implementation plan.

## 3. Issue Plan

Issue plan converts requirement/design into execution:

```text
Acceptance Envelope
└── Milestones
    └── Behavior Backlog
        └── Active TDD Cycle
```

Plan owns:

- implementation order
- TDD cycle planning
- validation ladder
- stop/replan rules
- report evidence mapping

Plan must not create new requirements or design contracts.

## 4. Report

Report records observed evidence:

- Red evidence
- Green evidence
- refactor evidence
- contract checks
- reviewer decisions
- deviations
- artifact adoption
- final quality gate

## 5. TDD cycle size

The inner TDD unit is not strictly “one test function”. It is one independent behavioral hypothesis.

One cycle may include multiple test cases only if:

- they express the same invariant/state transition;
- they fail for the same expected reason;
- one coherent production change makes them pass.

Split when:

- failure causes differ;
- responsibilities differ;
- contract and behavior are mixed;
- migration and normal behavior are mixed;
- recovery and normal path are mixed;
- changes cross another bounded context/scope.

## 6. Double loop model

For many Issues:

```text
Outer guiding scenario / acceptance envelope
  -> inner TDD cycles
    -> milestone gate
      -> final quality gate
```

Lite Issues may use checklist verification instead of full TDD.

Strict/Critical Issues require extra gates:

- contract
- compatibility
- migration/update
- failure/recovery
- safety/manual where relevant

## 7. Upstream handoff requirement

Epic plan must provide enough information for Issue requirement/design/plan without forcing the Issue to re-discover parent decisions.

Minimum handoff:

- parent design IDs
- slice outcome
- allowed delta
- forbidden changes
- suggested grade
- required evidence levels
- dependencies
- escalation triggers
```

## Source File: `spec-dock-phase3-upstream-planning-pack-v3-final/reference/reviewer-anti-patterns.md`

```markdown
# Reviewer Anti-patterns and Heuristics

Use this reference when updating reviewer checklists, skills, workflow docs, and final smoke tests.

## 1. Scope drift anti-patterns

### Initiative drift

- Initiative design lists class methods or private helpers.
- Initiative plan lists file edits.
- Initiative design chooses Issue-level TDD order.
- Initiative design copies all Epic content instead of defining strategic envelope.

### Epic drift

- Epic design becomes a giant Issue design.
- Epic plan is only a task checklist, not an Issue slicing plan.
- Epic fixes private class structures or exact method signatures prematurely.
- Epic does not provide Issue handoff IDs/constraints.
- Epic lets each Issue redefine lifecycle/invariants.

### Issue drift

- Issue design redefines parent context/source-of-truth decisions.
- Issue plan creates new requirements.
- Issue plan changes normative design without updating design.md.
- Issue includes multiple unrelated outcomes.

## 2. Artifact misuse

- Raw discovery artifact treated as canonical requirement/design.
- Candidate model implemented without adoption into design.md.
- Research notes override parent design silently.
- Artifact adoption is not recorded in report.md.

## 3. TDD drift

- A TDD cycle contains multiple independent behavioral hypotheses.
- Red failure reason is not checked before production code changes.
- Refactor happens while tests are red.
- Test expectations are changed to make implementation pass.
- Plan has no report evidence destination.

## 4. Handoff insufficiency

Poor Epic-to-Issue handoff:

- “Implement finalize endpoint” with no parent design IDs.
- No suggested Issue grade.
- No inherited constraints.
- No forbidden changes.
- No expected verification level.

Good handoff:

- parent design IDs
- behavior outcome
- allowed delta
- forbidden changes
- suggested grade
- acceptance seed
- verification seed
- dependencies
- escalation triggers

## 5. Reviewer focus by scope

### Initiative reviewer

Check:

- strategic purpose clear
- source of truth clear
- context ownership clear
- strategic invariants present
- transition states safe
- Epic handoff sufficient

### Epic reviewer

Check:

- target model envelope clear
- cross-Issue invariants clear
- lifecycle/state clear
- contract portfolio clear
- design slice catalog useful
- Issue handoff sufficient

### Issue reviewer

Check:

- one coherent outcome
- parent constraints inherited
- design delta local
- plan executable
- TDD granularity appropriate
- report evidence destinations present

## 6. Review gate principle

Fresh reviewer pass remains required for phase promotion. The reviewer focus changes by artifact and scope; the gate should not disappear.
```
