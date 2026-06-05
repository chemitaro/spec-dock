---
type: research
status: completed
created_at: "2026-06-05T03:16:40Z"
source: "deep-research-use task package"
epic: "epic-00158"
title: "Branch E Deep Research task package for Codex context engineering patterns"
---

# Branch E Deep Research Task Package: Codex Context Engineering Patterns

## Status

This is a follow-up Deep Research task package for the active `epic-00158` research library.

Prior library reports:

- `20260605t014300z-research-codex-harness-context-engineering-deep-research-report.md`
- `20260605t021127z-research-branch-a-codex-openai-guidance-deep-research-report.md`
- `20260605t024753z-research-branch-b-execution-plan-sdk-context-packet-deep-research-report.md`

Related in-flight branches:

- `20260605t025055z-research-branch-c-agent-workflow-compliance-gates-task-package.md`
- `20260605t030851z-research-branch-d-codex-eval-ci-harness-patterns-task-package.md`

Branch B covered long-running workflow artifacts and context packets. Branch E narrows into context engineering itself: how to design instruction hierarchy, progressive disclosure, context refresh, compaction handoff, memory boundaries, retrieval, and repo-doc source-of-truth patterns for Codex-like coding agents.

## Objective

Create a source-backed research report that helps SpecDock improve Codex-centered context engineering for long-running, multi-agent, repo-governed workflows.

The report should support future issues under `epic-00158 Agent Workflow PDCA Hardening`, especially improvements to skills, sub-agent handoffs, discussion/report templates, active context projections, and context packet design.

## Research Question

What are the current public best practices and implementation patterns for context engineering in Codex-like coding-agent workflows, especially for long-running tasks, multi-agent delegation, repository-local instructions, compaction, memory boundaries, and progressive disclosure?

Investigate:

- official OpenAI/Codex guidance for instructions, AGENTS-style repository context, context limits, custom instructions, skills, model/tool boundaries, and long-running work,
- context engineering practices for coding agents: instruction hierarchy, source-of-truth docs, context packets, handoff packets, progress logs, and externalized state,
- progressive disclosure and retrieval strategies that avoid loading all docs while keeping agents grounded,
- compaction and resume strategies for preserving role, goal, current state, open blockers, and evidence without relying on chat memory,
- multi-agent handoff patterns: bounded contracts, artifact references, freshness, review independence, and avoiding stale or contaminated context,
- memory and trust boundaries: local repo docs vs session memory vs browser history vs private connectors vs public web,
- prompt and skill design techniques that reduce workflow drift while preserving autonomy,
- examples from Codex, OpenAI Cookbook, coding-agent frameworks, and adjacent systems when clearly marked as non-Codex.

## Source Scope

Allowed sources:

- Public web.
- Official OpenAI/Codex documentation, OpenAI Cookbook, OpenAI engineering posts, official OpenAI GitHub repositories, and official examples.
- Public primary or near-primary sources for context engineering, prompt engineering, coding-agent instructions, retrieval-augmented agent workflows, memory boundaries, and multi-agent handoff.
- Public GitHub repositories/issues that include concrete instruction hierarchy, context packet, memory, handoff, or agent workflow documentation.
- Adjacent non-Codex systems such as Claude Code, Cursor, Aider, OpenHands, SWE-agent, Continue, LangGraph, LangSmith, Promptfoo, or Anthropic context-engineering guidance may be used only as comparison evidence and must be clearly marked as non-Codex.

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
- Preserve source links, dates, version signals, and repository names where available.
- Prefer concrete patterns: context packet schemas, handoff templates, progress log fields, instruction file layout, freshness rules, retrieval rules, and context pruning policies.
- Mark stale, beta, preview, undocumented, or surface-specific behavior.
- Explicitly identify what Codex should directly verify before converting findings into SpecDock requirements.
- Call out anti-patterns that cause context drift, false confidence, stale memory, prompt injection, or over-constrained agents.

## Output Shape

Produce a report with these sections:

1. Executive summary.
2. Source map:
   - source,
   - date or freshness signal,
   - surface covered,
   - evidence strength,
   - relevance to SpecDock.
3. Codex/OpenAI context guidance:
   - repository instructions,
   - custom instructions,
   - tool and connector boundaries,
   - long-running task context,
   - limitations and unknowns.
4. Context architecture patterns:
   - source-of-truth hierarchy,
   - context packet,
   - handoff packet,
   - progress log,
   - evidence ledger,
   - active projection.
5. Progressive disclosure and retrieval:
   - what to load first,
   - what to defer,
   - how to refresh,
   - how to avoid stale assumptions,
   - how to bound source scope.
6. Compaction and resume:
   - minimum handoff fields,
   - preserving objective and status,
   - open tab/download/task handoff,
   - what not to rely on.
7. Multi-agent context contracts:
   - bounded task packets,
   - accepted inputs,
   - expected outputs,
   - review and freshness,
   - contamination prevention.
8. Memory and trust boundaries:
   - repo docs,
   - session summaries,
   - private connectors,
   - browser state,
   - public web,
   - Deep Research output.
9. Skill and prompt design recommendations:
   - trigger rules,
   - mandatory checks,
   - concise context,
   - stop/wait rules,
   - autonomy preservation.
10. Candidate SpecDock follow-up issues for `epic-00158`, each with:
   - title,
   - problem,
   - source-backed rationale,
   - likely impacted files/docs,
   - acceptance evidence.
11. Anti-patterns and risks.
12. Verification checklist before implementation.
13. Sources used and citation list.
14. Uncertainties and recommended next research branches.

## Non-goals

- Do not implement any changes.
- Do not write final SpecDock requirement/design/plan documents.
- Do not use private local files.
- Do not assume every context-engineering pattern from adjacent tools is suitable for Codex.
- Do not recommend a giant rewrite as the first step.

## Deep Research Prompt

```text
Objective:
Create a source-backed research report for a SpecDock epic named "Agent Workflow PDCA Hardening". The report should help SpecDock improve Codex-centered context engineering for long-running, multi-agent, repo-governed workflows.

Research question:
What are the current public best practices and implementation patterns for context engineering in Codex-like coding-agent workflows, especially for long-running tasks, multi-agent delegation, repository-local instructions, compaction, memory boundaries, and progressive disclosure?

Investigate:
- official OpenAI/Codex guidance for instructions, AGENTS-style repository context, context limits, custom instructions, skills, model/tool boundaries, and long-running work,
- context engineering practices for coding agents: instruction hierarchy, source-of-truth docs, context packets, handoff packets, progress logs, and externalized state,
- progressive disclosure and retrieval strategies that avoid loading all docs while keeping agents grounded,
- compaction and resume strategies for preserving role, goal, current state, open blockers, and evidence without relying on chat memory,
- multi-agent handoff patterns: bounded contracts, artifact references, freshness, review independence, and avoiding stale or contaminated context,
- memory and trust boundaries: local repo docs vs session memory vs browser history vs private connectors vs public web,
- prompt and skill design techniques that reduce workflow drift while preserving autonomy,
- examples from Codex, OpenAI Cookbook, coding-agent frameworks, and adjacent systems when clearly marked as non-Codex.

Source scope:
- Use public web sources.
- Prioritize official OpenAI/Codex documentation, OpenAI Cookbook, OpenAI engineering posts, official OpenAI GitHub repositories, and official examples.
- Use public primary or near-primary sources for context engineering, prompt engineering, coding-agent instructions, retrieval-augmented agent workflows, memory boundaries, and multi-agent handoff.
- Use public GitHub repositories/issues that include concrete instruction hierarchy, context packet, memory, handoff, or agent workflow documentation.
- Adjacent non-Codex systems such as Claude Code, Cursor, Aider, OpenHands, SWE-agent, Continue, LangGraph, LangSmith, Promptfoo, or Anthropic context-engineering guidance may be used only as comparison evidence and must be clearly marked as non-Codex.
- Prefer 2025-2026 sources. Include older sources only when foundational and still-current.

Exclusions and privacy:
- Do not use private ChatGPT history, browser history, unpublished local repo files, personal files, secrets, credentials, private logs, or private source code.
- Do not assume hidden OpenAI implementation details.
- Do not treat adjacent-tool practices as Codex requirements.
- Do not draft final SpecDock requirements, design, code, or tests.

Quality bar:
- Separate first-party OpenAI/Codex claims, adjacent-tool claims, public implementation examples, and inference.
- Preserve source links, dates, version signals, and repository names where available.
- Prefer concrete patterns: context packet schemas, handoff templates, progress log fields, instruction file layout, freshness rules, retrieval rules, and context pruning policies.
- Mark stale, beta, preview, undocumented, or surface-specific behavior.
- Explicitly identify what Codex should directly verify before converting findings into SpecDock requirements.
- Call out anti-patterns that cause context drift, false confidence, stale memory, prompt injection, or over-constrained agents.

Output shape:
1. Executive summary.
2. Source map with source, date/freshness signal, surface covered, evidence strength, and relevance to SpecDock.
3. Codex/OpenAI context guidance: repository instructions, custom instructions, tool and connector boundaries, long-running task context, limitations and unknowns.
4. Context architecture patterns: source-of-truth hierarchy, context packet, handoff packet, progress log, evidence ledger, active projection.
5. Progressive disclosure and retrieval: what to load first, what to defer, how to refresh, how to avoid stale assumptions, how to bound source scope.
6. Compaction and resume: minimum handoff fields, preserving objective and status, open tab/download/task handoff, what not to rely on.
7. Multi-agent context contracts: bounded task packets, accepted inputs, expected outputs, review and freshness, contamination prevention.
8. Memory and trust boundaries: repo docs, session summaries, private connectors, browser state, public web, Deep Research output.
9. Skill and prompt design recommendations: trigger rules, mandatory checks, concise context, stop/wait rules, autonomy preservation.
10. Candidate SpecDock follow-up issues for epic-00158 with title, problem, source-backed rationale, likely impacted files/docs, and acceptance evidence.
11. Anti-patterns and risks.
12. Verification checklist before implementation.
13. Sources used and citation list.
14. Uncertainties and recommended next research branches.
```

## Local Tracking

- label: `branch-e-codex-context-engineering-patterns`
- project_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/project`
- thread_or_report_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a22402d-78dc-83a5-8fcd-d44b93d50215`
- current_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a22402d-78dc-83a5-8fcd-d44b93d50215`
- report_file: `spec-dock/active/epic/discussions/20260605t041113z-research-branch-e-codex-context-engineering-patterns-deep-research-report.md`
- download_file: `/Users/iwasawayuuta/Downloads/deep-research-report (5).md`
- state: `completed`
- source_scope: `public web; official OpenAI/Codex and public context-engineering/instruction-handoff examples preferred; no private local data`
- registered_at: `2026-06-05T03:16:40Z`
- submitted_at: `2026-06-05T03:20:49Z`
- started_at: `2026-06-05T03:20:49Z`
- completed_at: `2026-06-05T04:09:14Z`
- last_checked_at: `2026-06-05T04:11:13Z`
- exported_at: `2026-06-05T04:09:54Z`
- visible_plan: `SpecDock Codex Context Research plan shown and accepted; visible steps cover official OpenAI/Codex documentation and engineering posts, recent 2024-2026 coding-agent frameworks and GitHub examples, concrete packet/handoff/log/compaction patterns, progressive disclosure/retrieval/memory-boundary strategies, and source-backed recommendations.`
- visible_state: `Completed report view available inside the Codex-only Project. Visible completion signal: research completed; elapsed 44m; 27 citations; 96 searches. Markdown exported to Downloads and copied into the active epic discussions directory.`
- handoff: `Completed. Downloaded Markdown retained in Downloads; report artifact copied to active epic discussions.`
