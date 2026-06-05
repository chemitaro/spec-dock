---
type: research
status: invalidated
source: chatgpt-use task package
created_at: "2026-06-05T02:18:57Z"
epic_id: "epic-00158"
title: "ChatGPT workflow compliance analysis task package"
---

# ChatGPT Workflow Compliance Analysis Task Package

## Purpose

Use ChatGPT in the Codex-only ChatGPT Project, with the strongest available deep reasoning model, as an external architect/reviewer to analyze why the current SpecDock agent workflow instructions are not reliably producing compliant behavior and to propose implementable fixes.

This task package is separate from the parallel Deep Research work. It is a reasoning / architecture analysis prompt, not a source-cited web research request.

## Repository

- Repository URL: <https://github.com/chemitaro/spec-dock>
- Local worktree: `/Users/iwasawayuuta/.codex/worktrees/8d9b/spec-dock`
- Active epic: `epic-00158 Agent Workflow PDCA Hardening`

## User-Reported Failure Modes

- Agents sometimes skip required review gates.
- Agents sometimes skip required commits.
- Agents sometimes do not use the appropriate sub-agent even when the workflow expects delegation.
- Agents sometimes create `requirement.md`, `design.md`, and `plan.md` together instead of progressing through `requirement -> spec-reviewer pass -> design -> spec-reviewer pass -> plan -> spec-reviewer pass`.
- Agents sometimes proceed past phase gates without waiting for the required reviewer pass.
- The desired improvement path is iterative PDCA: create multiple issues, revise skills / docs / instructions, run them, observe failures, and refine again.

## Local Evidence Excerpts

### `workflow_spec_authoring.md`

- Spec authoring order is explicitly defined as `requirement -> spec-reviewer pass -> design -> spec-reviewer pass -> plan -> spec-reviewer pass -> downstream handoff`.
- Each phase promotion requires a fresh `spec-reviewer` result with `review_status: pass`.
- Missing, stale, failed, unavailable, denied, waived, or provisional reviewer results must block or remain incomplete; degraded mode must not be treated as reviewer-gate success.
- Canonical `requirement.md`, `design.md`, `plan.md`, and `report.md` are main-orchestrator single-writer authority.
- Sub-agent authoring outputs are scope-local flat `discussions/` evidence only and must not self-claim accepted authority, reviewer pass, phase completion, implementation readiness, or issue readiness.
- The workflow defines Evidence Adoption Ledger, Promotion Record, delegated draft evidence, failure modes, and phase gates.

### `workflow_issue.md`

- Issue planning routes through `.agents/skills/spec-dock-issue-planning/SKILL.md`; issue execution routes through `.agents/skills/spec-dock-issue-execution/SKILL.md`.
- Requirement / design / plan phase promotion uses `workflow_spec_authoring.md` and must wait for fresh `spec-reviewer` pass before moving to the next artifact.
- Execution may start only after planning artifacts are approved / reviewer-pass and handoff readiness evidence exists.
- Issue execution requires implementation delegation gates, per-step reviewer gates, step commit gates, final QA / code / spec review gates, PR delivery / merge-preparation gates, and final commit evidence before `complete`.
- `1 implementation step = 1 review scope = 1 commit` is the standard.
- Unavailable / denied / waived / provisional reviewer or delegation states are not success.

### `spec-driven-tdd-workflow/SKILL.md`

- The hub skill routes to leaf skills and says docs are source of truth.
- It reminds agents not to move between requirement / design / plan / execution without fresh reviewer pass.
- It says missing, stale, failed, unavailable, denied, waived, or provisional reviewer results are not `review_status: pass`.
- It tells agents to route issue planning to `spec-dock-issue-planning` and issue execution to `spec-dock-issue-execution`.

### `spec-dock-issue-planning/SKILL.md`

- The skill is intentionally concise.
- It points to `workflow_issue.md`, `workflow_spec_authoring.md`, clarification workflow, issue plan playbook, and issue plan authoring contract.
- It repeats that canonical docs remain main-orchestrator-owned.
- It repeats that `system-architect` and `implementation-planner` drafts are evidence only.
- It repeats that agents must not move from requirement to design, design to plan, or plan to execution without fresh `spec-reviewer` pass.

### `spec-dock-issue-execution/SKILL.md`

- The skill is concise and uses `workflow_issue.md` as source of truth.
- It says execution starts only after `requirement.md`, `design.md`, and `plan.md` are approved / reviewer-pass and recorded as ready.
- It routes implementation to `dev-coder`, shipped docs/templates/skills/workflow text to `doc-writer`, and review failures to bounded delegated follow-up.
- It states that unavailable tooling, denied access, host conflicts, waiver requests, and similar blockers are stop/incomplete unless explicit policy says they count as success.

## Working Hypothesis

The problem may not be absence of policy. It may be that the policy is too long, distributed, and reminder-based; agents lack a compact preflight checklist, machine-checkable gate state, hard stop points, or runtime/eval feedback that prevents or detects noncompliance early.

## Prompt To Submit

You are GPT-5.5 Pro / the strongest available deep reasoning model, acting as an external architect and workflow compliance reviewer for SpecDock.

Analyze the following problem using the repository URL and the supplied local evidence excerpts. Do not rely on prior ChatGPT memory or prior conversation history. If you can inspect the public repository at <https://github.com/chemitaro/spec-dock>, use it as supporting context; if you cannot, rely on the excerpts below and clearly mark missing context.

Problem:
SpecDock's agent workflow instructions are not reliably producing compliant behavior. In practice, agents sometimes skip required review gates, skip required commits, fail to use appropriate sub-agents, create requirement/design/plan artifacts together instead of sequentially, or proceed past phase gates without waiting for required reviewer pass. The desired improvement is an iterative PDCA hardening program across multiple issues: revise skills/docs/instructions, run them, observe failures, then refine again.

Known intended contract:
- Spec authoring must be `requirement -> fresh spec-reviewer pass -> design -> fresh spec-reviewer pass -> plan -> fresh spec-reviewer pass -> downstream handoff`.
- Canonical requirement/design/plan/report are main-orchestrator single-writer authority.
- Sub-agent outputs are only scope-local discussion evidence until integrated by main orchestrator and reviewed.
- Missing/stale/failed/unavailable/denied/waived/provisional reviewer results are not pass.
- Issue execution starts only after reviewer-pass planning artifacts and readiness evidence.
- Implementation steps should use delegation gates, per-step reviewer gates, and `1 implementation step = 1 review scope = 1 commit`.

Please produce an implementable analysis with these sections:

1. Executive diagnosis.
2. Failure-mode taxonomy, including why a capable LLM agent would violate this workflow despite the docs saying otherwise.
3. Likely root causes in instruction architecture, skill routing, prompt hierarchy, gate observability, runtime affordances, and human/agent ergonomics.
4. Concrete changes to skills / docs / workflow instructions that would reduce noncompliance.
5. Concrete enforcement or guardrail mechanisms beyond prose, including CLI checks, manifests, state-machine gates, preflight checklists, report templates, or eval harnesses.
6. Suggested PDCA issue breakdown with candidate issue titles, scope, acceptance criteria, and validation method.
7. Immediate triage changes that can be done in one or two small issues.
8. Strategic changes that need more design.
9. Risks and trade-offs, including over-constraining agents, slowing work, or creating false blockers.
10. Open questions that should be answered before implementation.

Bias toward implementable recommendations. Prefer small, testable changes and explicit gate-state contracts over broad abstract advice.

## Expected Output Handling

- Save the completed ChatGPT analysis as a separate `research` report under this epic's `discussions/`.
- Update this package with the ChatGPT thread URL, model/reasoning selection, completion status, and report path after retrieval.

## Submission Record

- Submitted at: `2026-06-05T02:21Z` (approximate; exact seconds not captured)
- ChatGPT Project: `for codex app`
- Thread URL: <https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a2232d6-ee4c-83a2-8479-328a268de994>
- Visible model / reasoning selector before submission: `じっくり思考 Pro`
- Status: invalidated
- Report path: discarded
- Invalidation note: The retrieved report used ChatGPT's `今すぐ回答` action. Per user instruction on 2026-06-05, outputs obtained via `今すぐ回答` must be discarded and must not be used as research evidence. Re-run required without selecting `今すぐ回答`.
