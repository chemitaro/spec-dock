---
type: research
status: completed
source: chatgpt-use
created_at: "2026-06-05T03:52:00Z"
epic_id: "epic-00158"
title: "ChatGPT skill docs information architecture report"
chatgpt_project: "for codex app"
chatgpt_thread_url: "https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a224514-06f4-83a3-abc8-03ab87de881f"
visible_model: "じっくり思考 Pro"
answer_now_used: false
---

# ChatGPT Skill Docs Information Architecture Report

## Retrieval Note

- Prompt source: `20260605t033550z-research-chatgpt-skill-docs-information-architecture-task-package.md`
- `今すぐ回答` appeared during generation, but was not selected.
- The response completed normally after long-running reasoning and was retrieved from the completed ChatGPT thread.

## ChatGPT Output

1. Judgment

The hypothesis is sound, with one correction: SpecDock should not move “workflow explanations” wholesale from docs into skills. It should move agent-mandatory workflow obligations into skills as a compact runbook, while keeping docs as the normative source for detailed policy, field semantics, examples, and rationale.

The current repo already points in both directions. The hub says spec-dock/docs/ is the source of truth, skills stay concise, templates are scaffolds, and workflow explanations live in docs. It also already mirrors some hard gates, such as fresh spec-reviewer pass and “missing/stale/failed/unavailable/denied/waived/provisional is not pass.”
GitHub
 The issue-planning skill is much thinner: it mainly routes to docs and states a few core invariants, including main-orchestrator ownership, fresh reviewer pass, unresolved-gap handling, and Spec Authoring Gate evidence.
GitHub
 The issue-execution skill is already closer to an operational runbook, with entry readiness, executable-plan expectations, report ledger obligations, delegation reminders, runtime command reminders, and finish sequencing.
GitHub

So the practical diagnosis is:

The problem is not “docs vs skills.” The problem is that the current boundary is too conceptual. The boundary should be operational: skills must contain the minimum sequence an agent must follow even if it never opens every linked doc. Docs remain authoritative for the details that make those steps precise.

Repository inspection is incomplete: I inspected public main through GitHub pages for the README, skills directory, the three requested skills, issue workflow, issue plan phase docs, issue plan authoring docs, and template docs. I did not audit every branch, test, installer path, or closed issue.

2. Recommended information architecture
Skills

Skills should be agent runbooks, not manuals.

They should contain:

Use when / do not use when

Mandatory read map: “before producing artifact X, read docs A/B/C”

Minimum ordered workflow

Stop conditions

Evidence to record

Exit criteria

Delegation/reviewer routing rules at the level of obligation, not schema detail

A skill should be sufficient for an agent to know: “What do I do next, what must I read, when must I stop, and what evidence makes the step valid?”

Workflow docs

Workflow docs should own normative lifecycle policy.

They should contain:

full lifecycle command contracts;

phase promotion policy;

execution order;

delegation invariants;

reviewer gate mapping;

completion policy;

failure, waiver, unavailable, and recovery behavior;

detailed examples and edge cases.

The current workflow_issue.md already functions this way: it owns issue lifecycle and execution gates, says issue planning goes through the issue-planning skill, issue execution goes through issue-execution, requires reviewer-pass planning artifacts, routes unresolved gaps back to clarification, treats templates as scaffolds, and assigns lifecycle/field-template ownership across docs.
GitHub

Authoring field docs

Authoring docs should own artifact-internal semantics.

They should contain:

field meanings;

required sections;

schema shape;

examples;

reviewer fail conditions;

how to write delegation contract, 具体テストケース一覧, closure indexes, amendment triggers, etc.

This is already the direction in phase_plan_issue.md: it says authoring/issue-plan.md owns executable step schema, delegation contract field semantics, concrete test case card schema, docs-only/inspect-only/manual-required writing, and reviewer fail conditions; workflow_issue.md owns lifecycle, execution order, parent/delegation invariant, reviewer gate mapping, and completion policy; templates own minimal scaffold and example shape.
GitHub

Templates

Templates should remain copyable starting shapes, not compliance authorities.

They should contain:

minimal headings;

lightweight placeholders;

example shape;

links to the owning workflow/authoring docs;

no long normative policy.

The repo’s template docs already describe templates as local-script inputs for new nodes and discussion docs, with canonical templates used to render draft artifacts.
GitHub
 The current issue workflow also explicitly says templates are not completed forms, placeholders may be removed, and necessary sections/diagrams may be added when useful.
GitHub

3. Concrete policy: agent-mandatory workflow steps vs concept/reference details

Use this rule:

A statement belongs in a skill when skipping it can make the agent produce the wrong artifact, move to the wrong phase, implement too early, claim completion incorrectly, or lose required evidence.

Examples that belong in skills:

“Do not start issue execution unless requirement.md, design.md, and plan.md are reviewer-pass and handoff-ready.”

“If any planning artifact is draft/template-only/unresolved/missing pass evidence, stop and return to planning.”

“Before writing an issue plan, read workflow_spec_authoring.md, workflow_issue.md, phase_plan_issue.md, and authoring/issue-plan.md.”

“Fresh spec-reviewer pass is required before requirement → design, design → plan, and plan → execution.”

“Record Spec Authoring Gate evidence in report.md.”

“Unresolved requirement/design/plan gaps go to clarification/authoring, not execution assumptions.”

“For execution, treat plan.md as the executable command queue and report.md as the observed evidence ledger.”

“Before completion, open ledger entries, missing final review pass, missing PR delivery/merge-prep evidence, or template-only docs mean not complete.”

A statement belongs in docs when it explains how to satisfy a mandatory step.

Examples that stay in docs:

exact field semantics for delegation contract;

schema for 具体テストケース一覧;

complete Ledger Note field set;

example plan cards;

diagram catalog;

detailed lifecycle command behavior;

recovery paths;

naming rules;

rationale for why templates are flexible;

full completion-gate evidence matrix.

A practical syntax is:

Skill says: Must do X. Read doc Y for exact schema/details. Stop if Z. Record evidence in W.
Doc says: X means these fields, examples, edge cases, and reviewer failure modes.

4. Risk analysis
Skill bloat

Risk: skills become long enough that agents skim them too. The issue-execution skill is already relatively dense compared with issue-planning, so blindly adding more content would make this worse.
GitHub

Mitigation: use a fixed skill structure and budget. Hub skill should stay routing-only plus global gates. Leaf skills should have a “mandatory runbook” of roughly 10–15 bullets, not full policy prose.

Duplicated truth between skill and docs

Risk: if the skill restates detailed policy, docs and skills diverge.

Mitigation: skill mirrors only obligation-level invariants, not schemas. Each mirrored line should point to the owning doc. For example: “Each implementation step needs a delegation contract; authoring/issue-plan.md owns the field semantics.” This matches the existing doc split where authoring docs own schema and workflow docs own lifecycle.
GitHub

Stale skill summaries

Risk: workflow docs change but skill reminders do not.

Mitigation: add a tiny “skill mirror checklist” to PR review/manual review: whenever a workflow doc changes a mandatory gate, update the owning skill’s runbook or explicitly record “no skill mirror needed.” This can be manual at first; no large tooling is required.

Context overload

Risk: skills instruct agents to read too many docs every time.

Mitigation: make the read map conditional. For issue planning, always read workflow_spec_authoring.md and the target artifact/upstream artifacts; read authoring/issue-plan.md only when producing or validating plan.md. For issue execution, always read spec-dock/active/context-pack.md, issue artifacts, and the execution/completion sections of workflow_issue.md; read field docs only when validating or amending plan structure.

Compliance failures when docs are skipped

Risk: the original problem remains if the skill merely links docs.

Mitigation: skills must include the high-impact stop conditions and exit criteria directly. For example, the issue workflow’s completion condition is extensive: complete status requires non-template issue docs, required sync/validate, required review evidence, closed implementation gates, closure coverage, final docs impact, final QA/code/spec reviews, PR delivery and merge-prep evidence, final commit, and clean worktree evidence; missing required steps must be classified as blocked or incomplete, not complete.
GitHub
 The skill should not copy that whole paragraph, but it must say “completion requires workflow_issue final completion gates; missing any required gate means blocked/incomplete, not complete.”

5. Safeguards to keep skills compact but operationally sufficient

Use a standard leaf-skill format:

Markdown
# Skill Name

## Use when
...

## Must read before writing/changing artifacts
- Always:
- If writing requirement:
- If writing design:
- If writing plan:
- If executing:

## Mandatory workflow
1. ...
2. ...
3. ...

## Stop conditions
- ...
- ...

## Evidence and exit criteria
- ...

Add these safeguards:

One-line mirror rule: each skill may mirror a doc-owned rule in one sentence only, followed by the owning doc path.

No field schema in skills: any field list longer than 3–5 items should move to authoring docs unless the exact fields are needed as worker handoff output.

Skill-owned verbs: use consistent verbs: Read, Stop, Record, Return, Do not claim complete, Route.

Doc-owner annotation: each skill reminder should imply an owner: workflow_issue.md owns lifecycle, authoring/issue-plan.md owns schema, templates/issue/plan.md owns scaffold.

Artifact-specific read map: avoid “read all docs.” Tell the agent exactly which docs to read for the artifact it is producing.

Empirical prompt probes: before merging changes, run 3–5 short manual prompts and check whether the model routes, stops, and records evidence correctly.

6. How to change the three current skills
A. spec-driven-tdd-workflow

Current hub wording says docs are source of truth, skills stay concise, templates are scaffolds, and workflow explanations live in docs.
GitHub
 Change that to a more precise IA contract:

Skills carry the mandatory agent runbook: route, required reads, stop conditions, evidence, and exit criteria. Docs remain source of truth for detailed workflow policy, concepts, field semantics, templates, examples, and edge cases.

Recommended edits:

Keep the hub as router, not a full workflow.

Keep global hard gates: fresh reviewer pass; non-pass states are not pass.

Add one sentence: “After routing, follow the leaf skill’s Must read map before producing or changing canonical artifacts.”

Remove or reduce the broad “Direct references” list if it encourages random doc skimming. Replace it with “leaf skills declare required docs.”

Keep the reminder that templates are scaffolds, but phrase it as a global invariant: “Do not treat template presence as completion.”

B. spec-dock-issue-planning

This needs the most improvement. The current skill links the primary lifecycle/execution workflow, spec authoring workflow, clarification workflow, issue plan playbook, and issue plan authoring contract; it also states main-orchestrator ownership, delegated drafts as evidence only, fresh reviewer pass, unresolved gap handling, and Spec Authoring Gate report evidence.
GitHub
 That is good but too sparse for a model that may not open every doc.

Add a compact runbook:

Markdown
## Must read
- Always before issue planning: active/upstream issue/epic/initiative artifacts, `workflow_spec_authoring.md`, and the issue-specific authoring section of `workflow_issue.md`.
- If ambiguity affects scope, acceptance, terms, or responsibility boundaries: read `workflow_clarification.md` before writing forward.
- If writing/updating `plan.md`: read `phase_plan_issue.md` and `authoring/issue-plan.md`.
- If using templates: treat them as scaffolds, not completion targets.

## Mandatory workflow
1. Inspect existing node and upstream context before create/import/update.
2. Author in order: requirement -> fresh spec-reviewer pass -> design -> fresh spec-reviewer pass -> plan -> fresh spec-reviewer pass -> execution handoff.
3. Main orchestrator owns canonical `requirement.md`, `design.md`, `plan.md`, and `report.md`.
4. Sub-agent/system-architect/implementation-planner output is discussion evidence only until adopted into canonical docs and recorded in `report.md`.
5. If a requirement/design/plan gap appears, return to clarification or the prior phase; do not push the gap into execution.
6. For issue `plan.md`, ensure executable handoff readiness: step-local scope, obligations, verification, report evidence destination, amendment triggers, S90 docs impact, and S99 final quality gate are represented via the owning docs.
7. Record each `Spec Authoring Gate` in `report.md`.

## Exit criteria
- Requirement/design/plan are issue-specific, non-template, internally consistent, and fresh reviewer-pass.
- `plan.md` is executable without inventing workflow decisions.
- `report.md` contains gate and handoff readiness evidence.
- No open spec ambiguity blocks execution.

The skill should not copy the complete issue-plan schema. The authoring doc already owns required issue-plan items and executable step schema, including closure index, delegation contract, concrete test cases, behavior slice execution, S90, S99, and final exit contract.
GitHub

C. spec-dock-issue-execution

This skill is not simply “too thin”; it is dense but not optimally navigable. It already has many mandatory reminders: readiness, executable plan, unresolved-gap return, report ledger, delegation, runtime command reminders, and final PR/finish sequencing.
GitHub

Recommended change: reorganize it into a top-loaded runbook and move any excessive schema detail back to docs.

Add or promote this near the top:

Markdown
## Must read before execution
- `spec-dock/active/context-pack.md`
- active issue `requirement.md`, `design.md`, `plan.md`, `report.md`
- `workflow_issue.md` execution contract and completion policy
- `phase_plan_issue.md` and `authoring/issue-plan.md` when validating or amending plan structure

## Entry preflight
- Stop unless requirement/design/plan are issue-specific, non-template, fresh reviewer-pass, and handoff-ready.
- Stop if `plan.md` is not executable as a step-local workflow contract.
- Stop if unresolved spec/design/plan gaps remain; return to planning/clarification.

## Execution loop
1. Use `issue start <target>` as primary lifecycle start.
2. Execute steps in plan order.
3. For each step: confirm closure contract, delegate or record approved local exception, verify Red/alternative evidence, implement bounded batch, run Green verification, record report evidence, run mapped reviewer gate, fix/re-review to pass, commit or approved-no-op.
4. Material worker decisions must become report ledger entries; worker proposals are not accepted decisions.
5. S90 resolves docs impact before final quality gate.
6. S99 runs final QA, issue-wide code review, and final spec review to pass.
7. Use PR delivery / merge-preparation workflow before `issue finish`.
8. Use `issue finish` only after completion gates pass; missing gates mean blocked/incomplete.

Keep doc pointers for exact details. workflow_issue.md already owns the execution contract, including parent-agent invariant, step order, implementation delegation gate, reviewer mapping, one step/one review/one commit standard, S90/S99 gates, and strict completion conditions.
GitHub

GitHub

GitHub

7. Small PDCA plan: first 3–5 issues
Issue 1 — Define the IA policy in one short doc section

Add a short “Skills vs docs vs templates” policy, probably in spec-dock/docs/guide.md or a small reference doc. Outcome: a stable rule that skills carry mandatory runbooks, workflow docs carry lifecycle detail, authoring docs carry field semantics, templates carry minimal scaffold.

Acceptance: the policy includes the “agent-mandatory workflow step” test and the “concept/reference detail” test.

Issue 2 — Update the hub skill wording

Change the hub from “workflow explanations live in docs” to “leaf skills contain mandatory runbooks; docs remain detailed source of truth.” Keep routing and global reviewer gate reminders.

Acceptance: hub routes to leaf skills and tells agents to follow the leaf skill’s Must read map before producing artifacts.

Issue 3 — Refactor spec-dock-issue-planning into a runbook

Add Must read, Mandatory workflow, Stop conditions, and Exit criteria. Do not add field schemas.

Acceptance: a model reading only the issue-planning skill knows that it must read the right docs, must proceed requirement → design → plan with fresh reviewer pass, must return unresolved gaps to clarification, and must record gate/handoff evidence.

Issue 4 — Reorganize spec-dock-issue-execution

Do not substantially expand it. Move the execution sequence to the top, add a conditional read map, and trim any content that is more field-schema than runbook.

Acceptance: the first half of the skill is enough to prevent premature execution, missing per-step review, skipped S90/S99, and premature issue finish.

Issue 5 — Add lightweight compliance probes

Add 3–5 manual test prompts under the existing manual-test area or a docs QA note. The repo has a manual-tests directory at the top level.
GitHub

Acceptance: each probe has expected observable behavior and a simple pass/fail checklist.

8. Success criteria and lightweight empirical tests
Success criteria

Routing correctness: agents route issue planning to spec-dock-issue-planning and execution only to spec-dock-issue-execution.

Doc-read behavior: agents mention or record the artifact-specific docs they used before authoring or execution.

Premature execution reduction: agents stop when planning artifacts are draft/template-only/missing reviewer-pass.

Gap handling: agents return unresolved ambiguity to clarification or prior authoring phase instead of inventing assumptions.

Plan quality: issue plans contain executable step-local contracts, concrete test seeds, closure mapping, S90, S99, and final exit contract.

Completion accuracy: agents classify missing gates as blocked/incomplete, not complete.

Compactness: hub remains short; leaf skills remain readable; detailed field schemas remain in docs.

Probe 1 — Missing plan reviewer pass

Prompt: “Start implementing this active issue. requirement.md and design.md passed review, but plan.md is draft.”

Expected: agent refuses execution, routes to issue planning, reads/plans around workflow_spec_authoring.md, records blocked/handoff gap. No implementation.

Probe 2 — Template-only issue docs

Prompt: “This issue has generated requirement.md, design.md, plan.md, and report.md; please finish it.”

Expected: agent identifies template-only docs as incomplete and does not claim complete. This aligns with workflow policy that untouched/template/placeholder issue docs are not completion.
GitHub

Probe 3 — Plan authoring

Prompt: “Write the issue plan.md from an approved requirement/design.”

Expected: agent reads phase_plan_issue.md and authoring/issue-plan.md, then produces a plan with required issue-plan structures such as closure index, delegation contract, concrete test cases, behavior-slice execution, S90, S99, and final exit contract.
GitHub

Probe 4 — Execution with a discovered spec gap

Prompt: “During S20 implementation, the API behavior conflicts with requirement wording. Continue with the likely intended behavior.”

Expected: agent stops execution for that step, records the gap, and returns to clarification or authoring. It must not absorb the gap as an execution assumption.

Probe 5 — Docs-only shipped artifact change

Prompt: “Update a skill/workflow text as part of an issue execution step.”

Expected: plan/agent routes shipped docs/templates/skills/workflow text to doc-writer, uses docs/spec alignment review, and records delegation/review evidence rather than treating docs-only work as review-free. The workflow and authoring docs already identify doc-writer as the primary worker for shipped docs/templates/skills/workflow text and map docs-only/template-only/skill-text-only review to spec-reviewer alignment.
GitHub

Bottom line

Proceed with the hypothesis as a small IA correction, not a rewrite:

Make every leaf skill operationally sufficient for the mandatory path. Keep every detailed explanation in docs. Add conditional “must read” maps so agents read the right docs at the moment they produce a specific artifact.

The first dogfood target should be spec-dock-issue-planning, because it currently has the largest gap between “links to docs” and “agent can safely execute the workflow from the skill.”
