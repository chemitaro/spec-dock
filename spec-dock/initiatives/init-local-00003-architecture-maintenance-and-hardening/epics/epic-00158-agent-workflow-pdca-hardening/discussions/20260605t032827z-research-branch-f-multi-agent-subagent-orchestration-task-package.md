---
type: research
status: completed
created_at: "2026-06-05T03:28:27Z"
source: "deep-research-use task package"
epic: "epic-00158"
title: "Branch F Deep Research task package for multi-agent, sub-agent, and skill orchestration patterns"
---

# Branch F Deep Research Task Package: Multi-Agent, Sub-Agent, and Skill Orchestration Patterns

## Status

This is a follow-up Deep Research task package for the active `epic-00158` research library.

Prior library reports:

- `20260605t014300z-research-codex-harness-context-engineering-deep-research-report.md`
- `20260605t021127z-research-branch-a-codex-openai-guidance-deep-research-report.md`
- `20260605t024753z-research-branch-b-execution-plan-sdk-context-packet-deep-research-report.md`

Related in-flight branches:

- `20260605t025055z-research-branch-c-agent-workflow-compliance-gates-task-package.md`
- `20260605t030851z-research-branch-d-codex-eval-ci-harness-patterns-task-package.md`
- `20260605t031640z-research-branch-e-codex-context-engineering-patterns-task-package.md`

Branch F narrows into the user's original concern: SpecDock's skills, sub-agents, and workflow orchestration do not reliably behave as intended. This branch focuses on source-backed patterns for when to delegate, how to bound sub-agent tasks, how to preserve reviewer independence, and how to prevent handoff or context contamination.

## Objective

Create a source-backed research report that helps SpecDock improve multi-agent and sub-agent orchestration for Codex-centered workflows, including skill trigger rules, bounded delegation contracts, reviewer independence, task lifecycle boundaries, and handoff evidence requirements.

The report should support future issues under `epic-00158 Agent Workflow PDCA Hardening` without prescribing implementation changes directly.

## Research Question

What are the current public best practices and implementation patterns for designing reliable multi-agent, sub-agent, skill, and reviewer workflows for Codex-like coding agents?

Investigate:

- official OpenAI/Codex guidance for delegation, code review, skills/custom instructions, tools, sandboxing, and long-running work,
- public examples of multi-agent coding workflows and role specialization,
- bounded task contracts for sub-agents: objective, scope, inputs, outputs, constraints, validation, rollback, and evidence,
- reviewer independence and freshness patterns: fresh session, no self-review, evidence links, stale/waived/unavailable semantics,
- skill trigger and routing patterns that avoid both under-use and over-use of skills,
- context handoff patterns between main agent, implementation agent, reviewer agent, researcher, and documentation writer,
- anti-contamination patterns: separating draft reasoning, Deep Research output, source-verified evidence, user instructions, browser state, and repo docs,
- failure modes where agents skip delegation, delegate too broadly, trust stale handoffs, or treat self-reports as verification,
- evaluation approaches for multi-agent compliance and handoff quality,
- adjacent practices from agent frameworks or workflow systems when clearly marked as non-Codex.

## Source Scope

Allowed sources:

- Public web.
- Official OpenAI/Codex documentation, OpenAI Cookbook, OpenAI engineering posts, official OpenAI GitHub repositories, and official examples.
- Public primary or near-primary sources for multi-agent workflows, agent handoff, coding-agent review, prompt/skill routing, task contracts, and evaluation.
- Public GitHub repositories/issues/PRs showing concrete multi-agent or review orchestration patterns.
- Adjacent non-Codex systems such as OpenAI Agents SDK, Swarm, LangGraph, CrewAI, AutoGen, SWE-agent, OpenHands, Aider, Claude Code, Cursor, or Anthropic multi-agent/context guidance may be used only as comparison evidence and must be clearly marked as non-Codex when applicable.

Preferred time window:

- Prefer 2025-2026 sources.
- Include older sources only when foundational and still-current.

Exclusions:

- Do not use private ChatGPT history, browser history, unpublished local repo files, personal files, secrets, credentials, private logs, or private source code.
- Do not assume hidden OpenAI implementation details.
- Do not treat adjacent-tool practices as Codex requirements.
- Do not draft final SpecDock requirements, design, code, or tests.

## Quality Bar

- Separate first-party OpenAI/Codex claims, adjacent-tool claims, public implementation examples, and inference.
- Preserve source links, dates, version signals, repository names, and command names where available.
- Prefer concrete patterns: delegation packet schemas, reviewer handoff templates, role boundary checklists, freshness rules, skill trigger rules, and eval scenarios.
- Mark stale, beta, preview, undocumented, or surface-specific behavior.
- Explicitly identify what Codex should directly verify before converting findings into SpecDock requirements.
- Call out anti-patterns that cause skipped delegation, false independence, stale review, over-broad handoff, or model performance loss from over-constraining agents.

## Output Shape

Produce a report with these sections:

1. Executive summary.
2. Source map with source, date/freshness signal, surface covered, evidence strength, and relevance to SpecDock.
3. Codex/OpenAI guidance on delegation, review, skills, tools, and instruction boundaries.
4. Multi-agent orchestration patterns: roles, lifecycle, main-agent orchestration, worker/reviewer/researcher boundaries, and legal next actions.
5. Bounded task contract patterns: required fields, accepted inputs, expected outputs, evidence requirements, and rollback notes.
6. Reviewer independence and freshness: fresh session rules, no self-review, timestamp/scope matching, stale/waived/unavailable semantics, and false-pass prevention.
7. Skill trigger and routing design: when to invoke skills, how to avoid trigger drift, how to keep prompts compact, and when to stop for clarification.
8. Handoff and contamination prevention: separating source-backed findings, model reasoning, local repo docs, session memory, browser state, and user-provided instructions.
9. Evaluation and regression harness: adversarial prompts, expected compliant behavior, trace signals, and grading rubrics for delegation/review/handoff quality.
10. Candidate SpecDock follow-up issues for `epic-00158` with title, problem, source-backed rationale, likely impacted docs/assets, and acceptance evidence.
11. Anti-patterns and risks.
12. Verification checklist before implementation.
13. Sources used and citation list.
14. Uncertainties and recommended next research branches.

## Deep Research Prompt

```text
Objective:
Create a source-backed research report for a SpecDock epic named "Agent Workflow PDCA Hardening". The report should help SpecDock improve multi-agent and sub-agent orchestration for Codex-centered workflows, including skill trigger rules, bounded delegation contracts, reviewer independence, task lifecycle boundaries, and handoff evidence requirements.

Research question:
What are the current public best practices and implementation patterns for designing reliable multi-agent, sub-agent, skill, and reviewer workflows for Codex-like coding agents?

Investigate:
- official OpenAI/Codex guidance for delegation, code review, skills/custom instructions, tools, sandboxing, and long-running work,
- public examples of multi-agent coding workflows and role specialization,
- bounded task contracts for sub-agents: objective, scope, inputs, outputs, constraints, validation, rollback, and evidence,
- reviewer independence and freshness patterns: fresh session, no self-review, evidence links, stale/waived/unavailable semantics,
- skill trigger and routing patterns that avoid both under-use and over-use of skills,
- context handoff patterns between main agent, implementation agent, reviewer agent, researcher, and documentation writer,
- anti-contamination patterns: separating draft reasoning, Deep Research output, source-verified evidence, user instructions, browser state, and repo docs,
- failure modes where agents skip delegation, delegate too broadly, trust stale handoffs, or treat self-reports as verification,
- evaluation approaches for multi-agent compliance and handoff quality,
- adjacent practices from agent frameworks or workflow systems when clearly marked as non-Codex.

Source scope:
- Use public web sources.
- Prioritize official OpenAI/Codex documentation, OpenAI Cookbook, OpenAI engineering posts, official OpenAI GitHub repositories, and official examples.
- Use public primary or near-primary sources for multi-agent workflows, agent handoff, coding-agent review, prompt/skill routing, task contracts, and evaluation.
- Use public GitHub repositories/issues/PRs showing concrete multi-agent or review orchestration patterns.
- Adjacent non-Codex systems such as OpenAI Agents SDK, Swarm, LangGraph, CrewAI, AutoGen, SWE-agent, OpenHands, Aider, Claude Code, Cursor, or Anthropic multi-agent/context guidance may be used only as comparison evidence and must be clearly marked as non-Codex when applicable.
- Prefer 2025-2026 sources. Include older sources only when foundational and still-current.

Exclusions and privacy:
- Do not use private ChatGPT history, browser history, unpublished local repo files, personal files, secrets, credentials, private logs, or private source code.
- Do not assume hidden OpenAI implementation details.
- Do not treat adjacent-tool practices as Codex requirements.
- Do not draft final SpecDock requirements, design, code, or tests.

Quality bar:
- Separate first-party OpenAI/Codex claims, adjacent-tool claims, public implementation examples, and inference.
- Preserve source links, dates, version signals, repository names, and command names where available.
- Prefer concrete patterns: delegation packet schemas, reviewer handoff templates, role boundary checklists, freshness rules, skill trigger rules, and eval scenarios.
- Mark stale, beta, preview, undocumented, or surface-specific behavior.
- Explicitly identify what Codex should directly verify before converting findings into SpecDock requirements.
- Call out anti-patterns that cause skipped delegation, false independence, stale review, over-broad handoff, or model performance loss from over-constraining agents.

Output shape:
1. Executive summary.
2. Source map with source, date/freshness signal, surface covered, evidence strength, and relevance to SpecDock.
3. Codex/OpenAI guidance on delegation, review, skills, tools, and instruction boundaries.
4. Multi-agent orchestration patterns: roles, lifecycle, main-agent orchestration, worker/reviewer/researcher boundaries, and legal next actions.
5. Bounded task contract patterns: required fields, accepted inputs, expected outputs, evidence requirements, and rollback notes.
6. Reviewer independence and freshness: fresh session rules, no self-review, timestamp/scope matching, stale/waived/unavailable semantics, and false-pass prevention.
7. Skill trigger and routing design: when to invoke skills, how to avoid trigger drift, how to keep prompts compact, and when to stop for clarification.
8. Handoff and contamination prevention: separating source-backed findings, model reasoning, local repo docs, session memory, browser state, and user-provided instructions.
9. Evaluation and regression harness: adversarial prompts, expected compliant behavior, trace signals, and grading rubrics for delegation/review/handoff quality.
10. Candidate SpecDock follow-up issues for epic-00158 with title, problem, source-backed rationale, likely impacted docs/assets, and acceptance evidence.
11. Anti-patterns and risks.
12. Verification checklist before implementation.
13. Sources used and citation list.
14. Uncertainties and recommended next research branches.
```

## Local Tracking

- label: `branch-f-multi-agent-subagent-orchestration`
- project_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/project`
- thread_or_report_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a2243c8-4d58-83a2-9c2b-22ae1a1e1c1b`
- current_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a2243c8-4d58-83a2-9c2b-22ae1a1e1c1b`
- report_file: `spec-dock/active/epic/discussions/20260605t041113z-01-research-branch-f-multi-agent-subagent-orchestration-deep-research-report.md`
- download_file: `/Users/iwasawayuuta/Downloads/deep-research-report (6).md`
- state: `completed`
- source_scope: `public web; official OpenAI/Codex and public multi-agent/sub-agent/reviewer orchestration sources preferred; no private local data`
- registered_at: `2026-06-05T03:28:27Z`
- submitted_at: `2026-06-05T03:38:58Z`
- started_at: `2026-06-05T03:46:36Z`
- completed_at: `2026-06-05T04:10:18Z`
- last_checked_at: `2026-06-05T04:11:13Z`
- exported_at: `2026-06-05T04:10:41Z`
- visible_plan: `SpecDock multi-agent PDCA hardening research plan visible; steps cover official OpenAI/Codex guidance, public multi-agent coding workflows and GitHub examples, bounded task contract and reviewer independence patterns, skill trigger/handoff/contamination/failure-mode patterns, and evaluation criteria/follow-up issue synthesis.`
- visible_state: `Completed report view available inside the Codex-only Project. Visible completion signal: research completed; elapsed 22m; 24 citations; 127 searches. Markdown exported to Downloads and copied into the active epic discussions directory.`
- handoff: `Completed. Downloaded Markdown retained in Downloads; report artifact copied to active epic discussions. Do not treat Deep Research citations as independently verified unless checked separately.`
