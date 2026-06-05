---
type: research
status: completed
source: chatgpt-use
created_at: "2026-06-05T04:00:00Z"
epic_id: "epic-00158"
title: "ChatGPT skill rewrite targets report"
chatgpt_project: "for codex app"
chatgpt_thread_url: "https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a224793-bae4-83aa-b587-b140081b9bc2"
visible_model: "じっくり思考 Pro"
answer_now_used: false
---

# ChatGPT Skill Rewrite Targets Report

## Retrieval Note

- Prompt source: `20260605t033551z-research-chatgpt-skill-rewrite-targets-task-package.md`
- `今すぐ回答` appeared during generation, but was not selected.
- The response completed normally after long-running reasoning and was retrieved from the completed ChatGPT thread.
- The first send attempt was blocked by a temporary request-frequency notice; after dismissing that notice, the same prompt was submitted and completed.

## ChatGPT Output

Conclusion

Adopt a two-layer rule:

Docs remain the conceptual/reference authority; workflow skills must contain the non-skippable operating procedure.
That means each skill should expose, in the skill body itself, the phase order, entry gates, stop conditions, evidence obligations, and routing decisions an agent must follow even when it does not open linked docs.

Repository inspection was limited to public GitHub web/raw pages on June 5, 2026. I inspected the README, docs tree, current hub/leaf skills, install-root skill copies, and the relevant workflow/phase docs, but I did not clone the repo or run tests. SpecDock currently installs spec-dock/docs, templates, scripts, and a .agents/skills set containing the hub and leaf skills under discussion.
GitHub
+1

1. Recommended section structure
A. spec-driven-tdd-workflow hub skill

Recommended structure:

Markdown
---
name: spec-driven-tdd-workflow
description: Entry skill that routes SpecDock work and exposes non-skippable workflow invariants.
---

# Spec-driven TDD Workflow

## Use this skill when
## Source-of-truth boundary
## Non-negotiable operating invariants
## Routing table
## Must not route when
## Read these docs when...
## Cross-skill handoff rules
## Minimal command guardrails
## Keep out of this skill

Recommended core text:

Markdown
## Source-of-truth boundary

`spec-dock/docs/` remains the detailed authority. This skill only carries the operational gates an agent must not skip before routing work.

Templates are starting scaffolds, not compliance definitions. Add, remove, merge, or reorder sections when needed for correctness, human understanding, or agent executability.

## Non-negotiable operating invariants

- Spec authoring advances only in this order: requirement -> fresh spec-reviewer pass -> design -> fresh spec-reviewer pass -> plan -> fresh spec-reviewer pass -> downstream handoff.
- Missing, stale, failed, unavailable, denied, waived, or provisional reviewer output is not a pass.
- Canonical `requirement.md`, `design.md`, `plan.md`, and `report.md` are main-orchestrator-owned. Delegated outputs are scope-local evidence until adopted into canonical artifacts and recorded in `report.md`.
- Unresolved requirement/design/plan gaps stop the current path. Return to clarification or the relevant authoring phase; do not invent execution assumptions.
- Issue execution starts only after approved/reviewer-pass issue artifacts and executable `plan.md` handoff evidence exist.

Rationale: the current hub already says docs are source of truth, templates are scaffolds, fresh spec-reviewer pass is required, degraded reviewer states are not pass, and leaf skills own details; the rewrite should make those items visually unavoidable instead of buried in a dense bullet block.
GitHub
+1

B. spec-dock-issue-planning

Recommended structure:

Markdown
---
name: spec-dock-issue-planning
description: Plan or repair issue-level requirement/design/plan artifacts and prepare executable handoff.
---

# SpecDock Issue Planning

## Use this skill when
## Source-of-truth boundary
## Must-follow issue planning checklist
## Artifact gates
### Requirement gate
### Design gate
### Plan gate
### Handoff gate
## Delegation and canonical ownership
## Stop and return conditions
## Evidence to record in report.md
## Docs to read
## Keep out of this skill

Recommended core text:

Markdown
## Must-follow issue planning checklist

1. Resolve the target issue and inspect existing `requirement.md`, `design.md`, `plan.md`, `report.md`, upstream initiative/epic context, ADRs, and `discussions/`.
2. Before editing an artifact, read the matching authoring/workflow docs listed below.
3. Complete or repair `requirement.md` first. It must fix WHAT/WHY/scope/non-scope/success/AC/EC without smuggling HOW into requirements.
4. Run a fresh `spec-reviewer` on requirement. Fix findings and rerun a fresh reviewer until pass. Record the Spec Authoring Gate in `report.md`.
5. Complete or repair `design.md` only after requirement pass. If a requirement gap appears during design, return to requirement and rerun the requirement gate.
6. Run a fresh `spec-reviewer` on design. Fix findings and rerun until pass. Record the gate.
7. Complete or repair `plan.md` only after requirement and design pass. Do not push unresolved design questions into plan.
8. For issue `plan.md`, create an executable behavior-slice contract: closure index, implementation steps, step-local concrete test cases, delegation contract, verification path, report evidence destination, amendment trigger, S90 docs impact, and S99 final quality gate.
9. Run a fresh `spec-reviewer` on plan. Fix findings and rerun until pass. Record the gate and handoff readiness.
10. If any requirement/design/plan ambiguity remains, route to clarification or the relevant authoring phase. Do not hand off to execution.

Rationale: the current issue-planning skill identifies the right docs and already says fresh reviewer pass and report.md gate evidence are required, but it lacks a visible step-by-step procedure.
GitHub
 The underlying spec-authoring doc defines the phase order, fresh reviewer gate, failure handling, lifecycle steps, and report evidence contract.
GitHub
+1

C. spec-dock-issue-execution

Recommended structure:

Markdown
---
name: spec-dock-issue-execution
description: Execute an active SpecDock issue after approved planning artifacts and executable plan handoff.
---

# SpecDock Issue Execution

## Use this skill when
## Entry gate: execution may start only if...
## Must-follow execution checklist
## Per-step execution loop
## Report and decision ledger obligations
## Delegation obligations
## Stop / blocked / incomplete conditions
## Final gates before completion
## Runtime command reminders
## Docs to read
## Keep out of this skill

Recommended core text:

Markdown
## Entry gate: execution may start only if...

- `./spec-dock/scripts/spec-dock issue start <target>` has selected the intended issue, or the active issue has been verified.
- `requirement.md`, `design.md`, and `plan.md` are issue-specific, non-template, approved/reviewer-pass, and recorded as ready.
- `plan.md` is executable without inventing workflow decisions.
- `report.md` has handoff readiness evidence.

If any entry condition fails, stop. Route to `spec-dock-issue-planning` or clarification instead of implementing.

## Must-follow execution checklist

1. Use `spec-dock/active/context-pack.md` and the active issue docs as the execution entrypoint.
2. Treat `plan.md` as the executable workflow contract.
3. Execute one implementation step at a time.
4. For each step, follow: planned behavior goal -> planned obligation -> Red or justified alternative evidence -> bounded implementation -> Green verification -> refactor guardrail -> closure evidence -> report update -> step review/approval -> commit or approved no-op.
5. Record actual evidence in `report.md`; do not store raw worker transcripts, private reasoning, secrets, or unreviewed durable decisions there.
6. If implementation reveals a requirement/design/plan gap, stop and return to planning/clarification. Do not absorb the gap as an execution assumption.
7. Resolve S90 docs impact before final quality gates. Docs impact `none` needs evidence.
8. Run S99 final quality gates: final QA, issue-wide code review, and final spec review. Failed reviewers require fixes and fresh re-review until pass.
9. Only after final gates and final commit evidence, use `github-pr-merge-preparer` for PR delivery and merge-preparation evidence.
10. Run `issue finish` only after completion gates pass; `issue finish` is lifecycle closure, not proof of delivery by itself.

Rationale: the current execution skill already contains many of these rules, but it is a flat reminder and explicitly says it is “only a concise reminder.”
GitHub
 The detailed issue workflow makes issue start/issue finish primary lifecycle commands, distinguishes lifecycle closure from delivery completion, requires S90/S99 gates, and defines strict completion evidence.
GitHub
+1

D. spec-dock-epic-planning

Recommended structure:

Markdown
---
name: spec-dock-epic-planning
description: Plan or repair epic-level artifacts and prepare issue decomposition.
---

# SpecDock Epic Planning

## Use this skill when
## Source-of-truth boundary
## Reuse-before-create rule
## Must-follow epic planning checklist
## Artifact gates
## Issue decomposition handoff
## Delegation boundaries
## Stop conditions
## Evidence to record
## Docs to read

Recommended core text:

Markdown
## Must-follow epic planning checklist

1. Inspect existing epics under the parent initiative before creating/importing.
2. Reuse/update an existing epic if the contract, migration, observability, rollout, and Done definition fit.
3. Create/import only when the design backbone or rollout order would otherwise break; record the rationale in the target epic `discussions/`.
4. Author requirement -> fresh spec-reviewer pass -> design -> fresh spec-reviewer pass -> plan -> fresh spec-reviewer pass.
5. Epic plan must define issue slicing, issue order/tranches, integration checkpoints, rollout/docs impact gates, issue readiness contract, and final exit contract.
6. Do not put issue-internal TDD cadence, commit rhythm, or step slicing into epic plan.
7. Record each Spec Authoring Gate in epic `report.md`.
8. Run `validate` and `sync` after structural changes.

Rationale: the epic workflow already defines reuse-first behavior, create/import conditions, artifact descriptions, phase-promotion gate, quality gates, and validate/sync finish commands.
GitHub
 The epic plan playbook says epic plans own issue slicing, issue order, integration checkpoints, rollout/docs impact, readiness, and final exit, but not issue-internal TDD cadence or commit rhythm.
GitHub

E. spec-dock-initiative-planning

Recommended structure:

Markdown
---
name: spec-dock-initiative-planning
description: Plan or repair initiative-level artifacts and prepare epic decomposition.
---

# SpecDock Initiative Planning

## Use this skill when
## Source-of-truth boundary
## Reuse-before-create rule
## Must-follow initiative planning checklist
## Artifact gates
## Epic decomposition handoff
## Stop conditions
## Evidence to record
## Docs to read

Recommended core text:

Markdown
## Must-follow initiative planning checklist

1. Inspect existing initiatives and current active context before creating/importing.
2. Reuse/update an existing initiative if purpose, success condition, scope, and responsible ownership fit.
3. Create/import only when the investment unit or success metrics would otherwise be wrong; record the rationale in the target initiative `discussions/`.
4. Author requirement -> fresh spec-reviewer pass -> design -> fresh spec-reviewer pass -> plan -> fresh spec-reviewer pass.
5. Initiative plan must define milestones, epic portfolio, sequencing rationale, investment/strategy gates, metric review, epic readiness contract, and final exit contract.
6. Do not put issue-level implementation order, test commands, or per-step review cadence into initiative plan.
7. Record each Spec Authoring Gate in initiative `report.md`.
8. Run `validate` and `sync` after structural changes.

Rationale: the initiative workflow already defines reuse-first behavior, create/import commands, artifact responsibilities, phase promotion, quality gates, and validate/sync finish commands.
GitHub
 The initiative plan playbook says initiative plans own milestone/portfolio/sequencing/strategy/metric/readiness/final-exit concerns, not issue-level implementation order, test commands, or per-step review cadence.
GitHub

2. Compact “must follow” workflow checklists
Issue planning
Markdown
1. Identify target issue and inspect existing issue docs, upstream epic/initiative, ADRs, discussions, and report.
2. Use `workflow_spec_authoring.md` for phase promotion and `workflow_issue.md` for issue-specific lifecycle/governance.
3. Requirement first: fix WHAT/WHY/scope/non-scope/success/AC/EC; no unresolved scope-impacting TBD.
4. Fresh `spec-reviewer` pass required before design; failed reviewer means fix and fresh rerun.
5. Design second: trace to passed requirement; cover existing implementation/docs/ADR, boundaries, compatibility, migration/rollback, test strategy.
6. Fresh `spec-reviewer` pass required before plan.
7. Plan third: trace to passed requirement/design; define executable behavior-slice steps, closure index, step-local test cases, delegation contract, verification/evidence paths, S90, S99.
8. Fresh `spec-reviewer` pass required before execution handoff.
9. Record every Spec Authoring Gate in `report.md`.
10. Stop on unresolved gaps; route to clarification or the relevant prior phase.
Issue execution
Markdown
1. Start or verify active issue using the shipped runtime path.
2. Confirm `requirement.md`, `design.md`, and `plan.md` are issue-specific, non-template, reviewer-pass, and handoff-ready.
3. Reject non-executable `plan.md`; route back to issue planning.
4. Execute one plan step at a time.
5. For each step: Red/alternative evidence -> bounded implementation -> Green verification -> refactor guardrail -> closure evidence -> report update -> review/approval -> commit or approved no-op.
6. Keep `report.md` as evidence and decision ledger; no raw transcripts, secrets, or private reasoning.
7. Stop on requirement/design/plan gaps; do not invent assumptions.
8. Resolve docs impact before final gates.
9. Run final QA, issue-wide code review, and final spec review to pass.
10. Record PR delivery/merge-prep evidence, then run `issue finish` only after completion gates pass.
Epic / initiative planning
Markdown
1. Inspect existing nodes first; do not default to create/import.
2. Reuse/update an existing node when the scope naturally fits.
3. Create/import only when the planning unit would otherwise be wrong; record rationale in `discussions/`.
4. Author requirement -> fresh spec-reviewer pass -> design -> fresh spec-reviewer pass -> plan -> fresh spec-reviewer pass.
5. Initiative plan decomposes to epics; epic plan decomposes to issues.
6. Keep lower-level implementation detail out of higher-level plans.
7. Record every Spec Authoring Gate in the scope `report.md`.
8. Run `validate` and `sync` after structural changes.
3. “Read these docs when...” matrix
When	Read first	Then read	Skill-visible mandatory rule
Creating/updating requirement.md	workflow_spec_authoring.md	Scope workflow: workflow_initiative.md, workflow_epic.md, or workflow_issue.md; phase_requirement.md; workflow_clarification.md if ambiguity remains	Requirement must fix intent, scope/non-scope, success, AC/EC before design. Fresh spec-reviewer pass is mandatory.
Creating/updating design.md	workflow_spec_authoring.md	phase_design.md; scope workflow; existing code/docs/ADR/discussions; for issue work also workflow_issue.md	Design starts only after requirement pass. Requirement gaps found during design return to requirement.
Creating/updating plan.md	workflow_spec_authoring.md and shared phase_plan.md	Scope playbook: phase_plan_initiative.md, phase_plan_epic.md, or phase_plan_issue.md; for issue plans also authoring/issue-plan.md and workflow_issue.md	Plan starts only after requirement/design pass. Issue plan must be executable without inventing workflow decisions.
Executing an issue	spec-dock-issue-execution and workflow_issue.md	spec-dock/active/context-pack.md, issue requirement.md/design.md/plan.md/report.md, phase_plan_issue.md, authoring/issue-plan.md, workflow_clarification.md if a gap appears	Execution starts only after reviewer-pass artifacts and executable plan handoff. Missing gates mean stop, not degraded success.
Updating shipped docs/templates/skills/workflow text	Relevant target workflow/phase/reference docs	docs/README.md, current target SKILL.md, relevant templates, workflow_issue.md docs-impact/final-gate rules; verify install-root/root skill copies before edit	Route shipped docs/templates/skills/workflow text to doc-writing workflow; update policy in docs, expose only non-skippable operational gates in skills.

The docs README already presents a docs reading order and high-frequency rules: start with guide.md, use scope workflow docs, shared phase playbooks, scope-specific plan playbooks, and reference docs; it also states that requirement/design/plan creation follows workflow_spec_authoring.md and fresh spec-reviewer phase gates.
GitHub

4. Wording that should move into skills vs. stay in docs
Move into skills as short mandatory wording

Use concise paraphrases, not full copied sections.

Source concept	Put into skills as
Phase order and fresh reviewer rule	“Advance only requirement -> fresh reviewer pass -> design -> fresh reviewer pass -> plan -> fresh reviewer pass -> handoff.”
Reviewer degraded states	“Missing/stale/failed/unavailable/denied/waived/provisional is not pass.”
Scope-impacting ambiguity	“Unresolved scope, non-scope, AC, EC, design, or plan gaps block handoff.”
Canonical ownership	“Canonical requirement/design/plan/report are main-orchestrator-owned; delegated drafts are evidence until adopted.”
Report gate evidence	“Record each Spec Authoring Gate in scope report.md.”
Issue execution entry gate	“Do not implement unless requirement/design/plan are approved/reviewer-pass and plan is executable.”
Plan executable contract	“Issue plan.md must contain step-local obligation, verification path, report evidence destination, amendment trigger, closure contract, and concrete test cases.”
Execution loop	“Run one step at a time: Red/alternative evidence, implementation, Green verification, refactor guardrail, closure, report, review, commit/no-op.”
Decision ledger	“Material interpretation/deviation/tradeoff/open question goes in report ledger; open ledger entries block completion.”
Completion rule	“No complete unless required validation, reviews, docs impact, final gates, final commit evidence, PR delivery/merge-prep, and lifecycle closure gates pass.”
Epic/initiative reuse	“Inspect existing nodes first; create/import only when reuse would break the planning unit; record rationale.”

These are the operational parts agents skip when they only see links. The detailed docs already contain them across workflow_spec_authoring.md, workflow_issue.md, and phase_plan_issue.md.
GitHub
+3
GitHub
+3
GitHub
+3

Keep in docs

Keep these as reference-only details:

Keep in docs	Reason
Exact Promotion Record fields and active-manifest hash/grant validation	Too detailed for skill; belongs to lifecycle/reference policy.
Full issue finish failure/recovery semantics	Important, but too long for skill. Skill should only say finish is gated lifecycle closure.
Full authoring/issue-plan.md schema and field semantics	Skill should require executable plan; docs should define every field.
Bug/performance diagnosis loops, instrumentation cleanup, regression evidence details	Skill should route; workflow docs should explain.
Naming, GitHub URL, foreign URL, deps, sync, worktree, migration, and update edge cases	Reference docs own command contracts and failure modes.
Optional diagram catalog and examples	Skill should say add useful diagrams; phase_design.md should define options.
Template shape and examples	Templates stay scaffolds; skills should not become template copies.
Full delegation consent/provenance/adoption schemas	Skill needs boundary and stop rules only; docs define admissible evidence.
Epic-wide PR endpoint evidence and deep review details	Epic workflow should remain authority.
5. Avoid skill bloat while preventing skipped workflow

Use this rule: skills contain gates and stop conditions; docs contain semantics and examples.

Practical limits:

Keep each leaf skill to roughly one screen of sections plus one checklist. Do not paste long command catalogs.

Use one “must-follow checklist” with 8–10 numbered steps. Agents obey numbered lists better than dense prose.

Put doc links immediately after the mandatory rule they refine.

Put full matrices only in the hub skill. Leaf skills should list only the docs they actually need.

Use a fixed vocabulary across skills: Entry gate, Fresh reviewer pass, Stop and return, Evidence to record, Completion gate.

Treat templates as scaffolds and skills as procedure. Do not make templates carry hidden compliance requirements.

Add a small repository test or snapshot check later: each workflow skill must include required headings and core phrases such as fresh spec-reviewer pass, not pass, report.md, and Stop.

6. Recommended invariant: what an agent must know even if it reads no linked docs
Markdown
SpecDock invariant:

Docs are the detailed authority, but the agent must still obey these gates without opening docs.

1. Do not skip phase gates: requirement, design, and plan each require a fresh `spec-reviewer` pass before the next phase or execution.
2. Missing, stale, failed, unavailable, denied, waived, or provisional review is not pass.
3. Canonical `requirement.md`, `design.md`, `plan.md`, and `report.md` are main-orchestrator-owned; delegated drafts are evidence until adopted.
4. Stop on unresolved requirement/design/plan ambiguity. Return to clarification or the relevant phase; do not implement by assumption.
5. Issue execution requires issue-specific, non-template, reviewer-pass artifacts and an executable `plan.md`.
6. Execute issue plans step-by-step with evidence in `report.md`.
7. Material decisions, deviations, tradeoffs, and open questions go into the report decision ledger; unresolved entries block completion.
8. Completion is not `issue finish` alone. Completion requires validation/review/docs/final gates/PR delivery evidence and then lifecycle closure.
7. Minimal first issue
Issue title
Markdown
Make issue planning skill expose mandatory authoring gates
Scope

Edit only:

Markdown
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md
.agents/skills/spec-dock-issue-planning/SKILL.md   # only if this root copy is maintained as a mirror

I saw both root .agents/skills and install-root .agents/skills copies for the target skills; the generated assets appear to live under src/spec_dock/assets/install_root, but this should be verified in the repo before editing.
GitHub
+2
GitHub
+2

Proposed body
Markdown
## Goal

Make `spec-dock-issue-planning` self-contained enough that an agent cannot miss requirement/design/plan phase order, fresh reviewer gates, report evidence, executable plan handoff, or stop/return conditions.

## Non-goals

- Do not change workflow policy.
- Do not edit docs/templates/scripts.
- Do not redefine issue-plan field semantics.
- Do not duplicate long workflow docs.

## Acceptance criteria

- Skill has explicit sections:
  - Use this skill when
  - Source-of-truth boundary
  - Must-follow issue planning checklist
  - Artifact gates
  - Delegation and canonical ownership
  - Stop and return conditions
  - Evidence to record in report.md
  - Docs to read
  - Keep out of this skill
- Checklist contains requirement -> fresh reviewer pass -> design -> fresh reviewer pass -> plan -> fresh reviewer pass -> execution handoff.
- Skill states degraded reviewer states are not pass.
- Skill states canonical docs are main-orchestrator-owned and delegated drafts are evidence only.
- Skill states unresolved gaps return to clarification or prior phase, not execution.
- Skill states issue `plan.md` must be executable and must include step-local obligations, verification/evidence paths, amendment triggers, concrete test cases, S90, and S99.
- Skill links to docs instead of copying detailed schemas.

This is easy to review because it changes only one skill’s procedural visibility and does not alter docs policy.

8. Follow-up issues
Follow-up 1: Rewrite hub skill as routing + invariant + doc matrix

Scope:

Markdown
src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md
.agents/skills/spec-driven-tdd-workflow/SKILL.md   # if mirrored

Acceptance criteria:

Markdown
- Hub has a visible Non-negotiable operating invariants section.
- Hub has a routing table for initiative/epic/issue planning, issue execution, clarification, ADR, system architect, implementation planner.
- Hub has the “read these docs when...” matrix.
- Hub says leaf skills own workflow details.
- Hub does not duplicate issue execution lifecycle details.
Follow-up 2: Restructure issue execution skill into entry gate + execution loop + final gates

Scope:

Markdown
spec-dock-issue-execution/SKILL.md

Acceptance criteria:

Markdown
- Entry gate blocks execution unless requirement/design/plan are reviewer-pass and plan is executable.
- Per-step loop is explicit.
- Decision ledger obligations are explicit.
- S90/S99/final reviewer/PR delivery/issue finish order is explicit.
- Detailed command semantics remain in docs.
Follow-up 3: Apply compact parity to epic and initiative planning skills

Scope:

Markdown
spec-dock-epic-planning/SKILL.md
spec-dock-initiative-planning/SKILL.md

Acceptance criteria:

Markdown
- Both skills have reuse-before-create rules.
- Both expose phase gates and report evidence.
- Initiative skill keeps issue-level details out of initiative plan.
- Epic skill keeps issue-internal TDD cadence out of epic plan.
- Epic skill preserves bounded delegation/depth constraints in compact form.
Follow-up 4: Add skill-structure guard tests or snapshot checks

Acceptance criteria:

Markdown
- Each workflow skill contains required headings.
- Each planning skill contains fresh reviewer pass and degraded-not-pass wording.
- Issue execution skill contains entry gate, per-step loop, report ledger, final gates, and issue finish lifecycle wording.
- Install-root and root skill copies are checked for intended sync or documented divergence.
Follow-up 5: Docs cleanup after skills are rewritten

Acceptance criteria:

Markdown
- Docs continue to be the detailed authority.
- Docs point readers to skills for agent-entry operational checklists.
- Duplicated prose is reduced only where it causes contradictions.
- Workflow docs retain exact policies, command semantics, field schemas, failure modes, and examples.
Follow-up 6: Template audit

Acceptance criteria:

Markdown
- Templates remain minimal scaffolds.
- No template implies it is the full compliance contract.
- Template comments point to the relevant skill for mandatory procedure and docs for details.
Follow-up 7: README/guide update for skill-vs-doc contract

Acceptance criteria:

Markdown
- README or docs/README states: skills contain non-skippable operational gates; docs contain detailed authority.
- It explains that agents should not treat templates as compliance targets.
- It links hub skill, workflow_spec_authoring, workflow_issue, and scope plan playbooks.
