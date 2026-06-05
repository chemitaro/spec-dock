---
type: research
status: completed
created_at: "2026-06-05T01:48:28Z"
completed_at: "2026-06-05T02:11:27Z"
source: "deep-research-use task package"
epic: "epic-00158"
title: "Branch A Deep Research task package for Codex and OpenAI guidance"
---

# Branch A Deep Research Task Package: Codex and OpenAI Guidance

## Status

This is a follow-up Deep Research task package for the active research library.

The prior broad report is:

- `20260605t014300z-research-codex-harness-context-engineering-deep-research-report.md`

This branch narrows the scope to Codex and OpenAI-specific current guidance so that later SpecDock issues can rely on up-to-date first-party behavior and terminology.

Deep Research completed and was exported as Markdown from Chrome.

The exported report was downloaded as `/Users/iwasawayuuta/Downloads/deep-research-report (1).md` and copied into this epic's `discussions/` directory as:

- `20260605t021127z-research-branch-a-codex-openai-guidance-deep-research-report.md`

## Objective

Create a source-backed, Codex/OpenAI-specific research report for `epic-00158 Agent Workflow PDCA Hardening`.

The report should convert current OpenAI/Codex guidance into actionable harness-engineering recommendations for SpecDock skills, subagents, context packets, permission profiles, verification loops, research workflows, and source-controlled knowledge accumulation.

## Research Question

What do current OpenAI and Codex official or primary sources say about designing reliable Codex-centered coding-agent workflows, including:

- `AGENTS.md` and repository instructions,
- Goals and long-running task continuity,
- compaction and context preservation,
- sandbox and approval policy design,
- auto-review and reviewer-agent boundaries,
- MCP and tool integration,
- skill or prompt-packaging patterns,
- Codex CLI / Codex app / app server integration surfaces,
- logging, traces, evaluations, and regression loops,
- safe use of web, browser, and external research?

## Source Scope

Allowed sources:

- Public web.
- Official OpenAI documentation, Codex documentation, OpenAI Cookbook, OpenAI engineering posts, release notes, API docs, model or eval docs, and official GitHub repositories.
- Public primary sources from OpenAI staff or OpenAI-maintained repos when clearly relevant.
- Public docs from adjacent first-party OpenAI agent tooling only when they clarify Codex harness design.

Secondary sources:

- Public GitHub issues, blog posts, or community notes may be used only as implementation experience or contradiction signals, not as strong evidence for current OpenAI behavior.

Time window:

- Prefer sources from 2025-2026.
- Include older OpenAI sources only when they remain directly relevant or define a still-current concept.

Exclusions:

- Do not use private ChatGPT history, browser history, personal files, local unpublished files, secrets, credentials, or private logs.
- Do not treat unofficial summaries as evidence for current Codex behavior unless they link to first-party sources.
- Do not rely on marketing pages unless they contain technical behavior, docs links, or release details.

## Quality Bar

- Separate first-party sourced claims from inference.
- Preserve source links and visible source dates where available.
- Mark freshness risk for each important claim.
- Mark any claim that depends on beta, preview, or product-surface-specific behavior.
- Identify contradictions or gaps between Codex CLI, Codex app, ChatGPT Codex, OpenAI API, and OpenAI agent SDK guidance.
- Explicitly state which findings Codex should independently verify before turning them into SpecDock requirements.

## Output Shape

Produce a report with these sections:

1. Executive summary.
2. Current Codex/OpenAI source map:
   - source,
   - date or freshness signal,
   - surface covered,
   - evidence strength,
   - relevance to SpecDock.
3. Terminology:
   - harness,
   - context,
   - goal,
   - compaction,
   - approval,
   - sandbox,
   - review,
   - tool/MCP,
   - eval/trace.
4. Codex workflow primitives:
   - how Codex expects repo instructions to be discovered,
   - how long-running goals should be represented,
   - how context should be compacted or handed off,
   - how permissions should be bounded,
   - how tool access should be routed.
5. Best practices for SpecDock:
   - context packet design,
   - skill and subagent boundary design,
   - spec-manager responsibilities,
   - reviewer independence,
   - browser / web research boundaries,
   - issue start / finish gates,
   - report and trace artifacts.
6. Anti-patterns:
   - overlong always-on prompts,
   - hidden session memory as source of truth,
   - mixed read/write/review permissions,
   - unsupported tool assumptions,
   - benchmark overfitting,
   - stale or unverifiable context.
7. Candidate follow-up issues for `epic-00158`, each with:
   - title,
   - problem,
   - source-backed rationale,
   - likely impacted files or docs,
   - acceptance evidence.
8. Verification checklist for Codex to perform before implementation.
9. Sources used and citation list.
10. Uncertainties and next research branches.

## Non-goals

- Do not draft final SpecDock requirements, design, or plan documents.
- Do not propose broad rewrites without evidence.
- Do not make code changes.
- Do not assume private OpenAI implementation details.
- Do not use private user data or private local repo contents as Deep Research input.

## Local Tracking

- label: `branch-a-codex-openai-guidance`
- project_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/project`
- thread_or_report_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a222bc1-b630-83a5-86de-5d31ebada6f2`
- current_url: `https://chatgpt.com/c/6a222bc1-b630-83a5-86de-5d31ebada6f2`
- report_file: `20260605t021127z-research-branch-a-codex-openai-guidance-deep-research-report.md`
- download_file: `/Users/iwasawayuuta/Downloads/deep-research-report (1).md`
- state: `completed`
- source_scope: `public web; official OpenAI/Codex docs and primary OpenAI sources preferred; no private local data`
- registered_at: `2026-06-05T01:48:28Z`
- submitted_at: `2026-06-05T01:52:00Z`
- started_at: `2026-06-05T01:54:00Z`
- completed_at: `2026-06-05T02:11:27Z`
- last_checked_at: `2026-06-05T02:11:27Z`
- exported_at: `2026-06-05T02:11:27Z`
- exported_bytes: `38833`
- exported_lines: `166`
- visible_completion: `リサーチが完了しました。所要時間: 16m・27件の引用・100件の検索`
- visible_research_plan: `Codex OpenAI guidance mapping`
- visible_activity:
  - `Collect official OpenAI and Codex docs and repos from 2024-2026.`
  - `Extract guidance on agents, context, tools, and permissions.`
  - `Map findings to SpecDock harness components and gaps.`
  - `Draft actionable recommendations and verification checklist.`
  - `Assemble source-backed report with citations and uncertainties.`
- visible_progress: `Confirming auto-review and sandbox boundaries...`
- visible_search_count: `100`
- handoff: `completed and exported; Chrome tab can be closed during cleanup.`
