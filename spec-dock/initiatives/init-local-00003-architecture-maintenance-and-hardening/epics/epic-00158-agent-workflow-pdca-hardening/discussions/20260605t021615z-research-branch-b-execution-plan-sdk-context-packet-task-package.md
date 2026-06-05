---
type: research
status: completed
created_at: "2026-06-05T02:16:15Z"
source: "deep-research-use task package"
epic: "epic-00158"
title: "Branch B Deep Research task package for execution plans, Codex SDK, context packets, and regression harnesses"
---

# Branch B Deep Research Task Package: Execution Plans, Codex SDK, Context Packets, and Regression Harnesses

## Status

This is a follow-up Deep Research task package for the active `epic-00158` research library.

Prior library reports:

- `20260605t014300z-research-codex-harness-context-engineering-deep-research-report.md`
- `20260605t021127z-research-branch-a-codex-openai-guidance-deep-research-report.md`

Branch A recommended a deeper branch on execution plans, Codex SDK surfaces, context packet design, and CI/eval regression loops. This package turns that recommendation into a focused Deep Research task.

## Objective

Create a source-backed research report that helps SpecDock define a practical, testable context-packet and execution-plan architecture for Codex-centered workflows.

The report should connect current Codex/OpenAI guidance, execution-plan practices, Codex SDK or automation surfaces, and agent-evaluation patterns into actionable recommendations for `epic-00158 Agent Workflow PDCA Hardening`.

## Research Question

How should a SpecDock-like system design execution plans, context packets, handoff artifacts, and regression/evaluation harnesses for reliable long-running Codex workflows?

Investigate:

- execution plan formats and best practices for coding agents,
- durable goal and progress-log artifacts,
- context packet structure for issue, epic, initiative, research, implementation, review, and verification work,
- Codex SDK or related automation surfaces for launching, monitoring, and evaluating Codex runs,
- OpenAI Agents SDK traces, graders, evals, and regression loops,
- CI/nightly harness designs for agent workflow regression,
- how to avoid stale context, overlong instructions, hidden memory dependency, and unverifiable handoffs,
- how other modern coding-agent ecosystems structure plans, memory, run logs, and eval harnesses when useful as secondary comparison.

## Source Scope

Allowed sources:

- Public web.
- Official OpenAI and Codex documentation, OpenAI Cookbook, OpenAI engineering posts, official OpenAI GitHub repositories, and official examples.
- Primary or near-primary sources for execution-plan formats used by modern coding agents.
- Public GitHub repositories or issues that demonstrate agent plan, context, trace, eval, or CI harness patterns.
- Public documentation from adjacent coding-agent systems only as comparison, clearly marked as secondary.

Preferred time window:

- 2025-2026 sources first.
- Older sources only if they define a still-current format, workflow, or evaluation pattern.

Exclusions:

- Do not use private ChatGPT history, browser history, unpublished local repo files, personal files, secrets, credentials, private logs, or private source code.
- Do not assume hidden OpenAI implementation details.
- Do not treat community conventions as Codex requirements unless corroborated by first-party OpenAI/Codex sources.
- Do not draft final SpecDock requirements, design, or code changes.

## Quality Bar

- Separate first-party sourced claims, secondary-source claims, and inference.
- Preserve source links, source dates, version signals, and repository names.
- Mark freshness risk for each important recommendation.
- Call out preview, beta, experimental, or surface-specific behavior.
- Explicitly flag claims that Codex should directly verify before converting into SpecDock requirements.
- Prefer concrete artifact shapes, schemas, command surfaces, and validation evidence over generic advice.

## Output Shape

Produce a report with these sections:

1. Executive summary.
2. Source map:
   - source,
   - date or freshness signal,
   - surface covered,
   - evidence strength,
   - relevance to SpecDock.
3. Execution-plan patterns:
   - required fields,
   - update lifecycle,
   - stop/resume behavior,
   - validation linkage,
   - anti-patterns.
4. Context-packet architecture:
   - issue packet,
   - epic packet,
   - initiative packet,
   - research packet,
   - implementation packet,
   - review packet,
   - verification packet,
   - handoff/compaction packet.
5. Codex SDK and automation surfaces:
   - what can be launched,
   - what can be monitored,
   - what can be traced,
   - what can be evaluated,
   - what should remain human-gated.
6. Trace/eval/regression harness design:
   - trace capture,
   - grader design,
   - dataset construction,
   - CI/nightly execution,
   - artifact inspection,
   - regression triage.
7. Stale-context and handoff failure modes:
   - causes,
   - detection signals,
   - mitigations,
   - required artifacts.
8. Proposed SpecDock library conventions:
   - document naming,
   - frontmatter,
   - status values,
   - source verification markers,
   - lifecycle transitions.
9. Candidate follow-up issues for `epic-00158`, each with:
   - title,
   - problem,
   - source-backed rationale,
   - likely impacted files or docs,
   - acceptance evidence.
10. Verification checklist before implementation.
11. Sources used and citation list.
12. Uncertainties and recommended next research branches.

## Non-goals

- Do not make implementation changes.
- Do not write final SpecDock requirements, design, or plan documents.
- Do not assume the current local SpecDock repository contents are visible to Deep Research.
- Do not propose a large rewrite unless the source-backed evidence clearly shows that smaller hardening steps are insufficient.
- Do not send or request private local files.

## Deep Research Prompt

```text
Objective:
Create a source-backed research report for a SpecDock epic named "Agent Workflow PDCA Hardening". The report should help design execution plans, context packets, handoff artifacts, and regression/evaluation harnesses for reliable long-running Codex-centered workflows.

Research question:
How should a SpecDock-like system design execution plans, context packets, handoff artifacts, and regression/evaluation harnesses for reliable long-running Codex workflows?

Investigate:
- execution plan formats and best practices for coding agents,
- durable goal and progress-log artifacts,
- context packet structure for issue, epic, initiative, research, implementation, review, verification, and handoff/compaction work,
- Codex SDK or related automation surfaces for launching, monitoring, tracing, and evaluating Codex runs,
- OpenAI Agents SDK traces, graders, evals, and regression loops,
- CI/nightly harness designs for agent workflow regression,
- stale-context, overlong-instruction, hidden-memory, and unverifiable-handoff failure modes,
- adjacent modern coding-agent ecosystems only as secondary comparison when useful.

Source scope:
- Use public web sources.
- Prioritize official OpenAI and Codex documentation, OpenAI Cookbook, OpenAI engineering posts, official OpenAI GitHub repositories, and official examples.
- Use primary or near-primary sources for execution-plan formats used by modern coding agents.
- Use public GitHub repositories or issues only to demonstrate real-world plan/context/trace/eval/CI harness patterns or contradiction signals.
- Adjacent coding-agent systems may be compared only as secondary evidence and must be clearly marked as non-Codex sources.
- Prefer 2025-2026 sources. Use older sources only when they define a still-current format, workflow, or evaluation pattern.

Exclusions and privacy:
- Do not use private ChatGPT history, browser history, unpublished local repo files, personal files, secrets, credentials, private logs, or private source code.
- Do not assume hidden OpenAI implementation details.
- Do not treat community conventions as Codex requirements unless corroborated by first-party OpenAI/Codex sources.
- Do not draft final SpecDock requirements, design, or code changes.

Quality bar:
- Separate first-party sourced claims, secondary-source claims, and inference.
- Preserve source links, source dates, version signals, and repository names.
- Mark freshness risk for each important recommendation.
- Call out preview, beta, experimental, or surface-specific behavior.
- Explicitly flag claims Codex should directly verify before converting into SpecDock requirements.
- Prefer concrete artifact shapes, schemas, command surfaces, and validation evidence over generic advice.

Output shape:
1. Executive summary.
2. Source map with source, date/freshness signal, surface covered, evidence strength, and relevance to SpecDock.
3. Execution-plan patterns: required fields, update lifecycle, stop/resume behavior, validation linkage, anti-patterns.
4. Context-packet architecture: issue packet, epic packet, initiative packet, research packet, implementation packet, review packet, verification packet, handoff/compaction packet.
5. Codex SDK and automation surfaces: what can be launched, monitored, traced, evaluated, and what should remain human-gated.
6. Trace/eval/regression harness design: trace capture, grader design, dataset construction, CI/nightly execution, artifact inspection, regression triage.
7. Stale-context and handoff failure modes: causes, detection signals, mitigations, required artifacts.
8. Proposed SpecDock library conventions: document naming, frontmatter, status values, source verification markers, lifecycle transitions.
9. Candidate follow-up issues for epic-00158 with title, problem, source-backed rationale, likely impacted files/docs, and acceptance evidence.
10. Verification checklist before implementation.
11. Sources used and citation list.
12. Uncertainties and recommended next research branches.
```

## Local Tracking

- label: `branch-b-execution-plan-sdk-context-packet`
- project_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/project`
- thread_or_report_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a22329e-ab60-83a7-9e1f-955963f9947c`
- current_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a22329e-ab60-83a7-9e1f-955963f9947c`
- report_file: `20260605t024753z-research-branch-b-execution-plan-sdk-context-packet-deep-research-report.md`
- download_file: `/Users/iwasawayuuta/Downloads/deep-research-report (2).md`
- state: `completed`
- source_scope: `public web; official OpenAI/Codex and primary execution-plan/eval sources preferred; no private local data`
- registered_at: `2026-06-05T02:16:15Z`
- submitted_at: `2026-06-05T02:21:00Z`
- started_at: `2026-06-05T02:23:38Z`
- completed_at: `2026-06-05T02:46:54Z`
- last_checked_at: `2026-06-05T02:48:34Z`
- exported_at: `2026-06-05T02:47:53Z`
- visible_research_plan: `SpecDock Agent PDCA Research`
- visible_activity:
  - `Collect official OpenAI/Codex docs, SDKs, and engineering posts from 2024-2026.`
  - `Survey execution-plan formats and agent orchestration patterns in primary sources.`
  - `Catalog context-packet schemas and durable artifact examples from repos and docs.`
  - `Analyze tracing, evals, graders, and CI harness designs for agent regression testing.`
  - `Synthesize recommendations, risks, and follow-up issues with source-backed evidence.`
- visible_progress: `completed and exported`
- visible_search_count: `91`
- visible_completion: `リサーチが完了しました。所要時間: 23m・32件の引用・91件の検索`
- visible_completed_steps:
  - `Collect official OpenAI/Codex docs, SDKs, and engineering posts from 2024-2026.`
  - `Survey execution-plan formats and agent orchestration patterns in primary sources.`
- exported_bytes: `45880`
- exported_lines: `187`
- handoff: `completed and exported; Chrome tab can be closed during cleanup.`
