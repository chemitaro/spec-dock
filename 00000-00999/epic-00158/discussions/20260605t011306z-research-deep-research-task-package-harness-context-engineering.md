---
type: research
status: completed
created_at: "2026-06-05T01:13:06Z"
completed_at: "2026-06-05T01:43:00Z"
source: "deep-research-use task package"
epic: "epic-00158"
title: "Deep Research task package for Codex harness and context engineering"
---

# Deep Research Task Package: Codex Harness and Context Engineering

## Status

Deep Research completed in the Codex-only ChatGPT Project.

The exported report was downloaded by Chrome as `/Users/iwasawayuuta/Downloads/deep-research-report.md` and copied into this epic's `discussions/` directory as:

- `20260605t014300z-research-codex-harness-context-engineering-deep-research-report.md`

Earlier connection note:

- The first attempt could not start because the Codex Chrome Extension connection was unavailable.
- A later retry succeeded, and the prompt package below was submitted to Deep Research.

## Objective

Create a source-backed research library for `epic-00158 Agent Workflow PDCA Hardening` about the latest practices in Codex-centered harness engineering and context engineering.

The output should help improve SpecDock skills, subagents, workflow instructions, task handoffs, research loops, and dogfooding feedback cycles.

## Research Question

What are the current state of the art and practical best practices for using Codex-style coding agents in:

- harness engineering for agentic coding workflows,
- context engineering for long-running or multi-agent software work,
- skill / subagent / instruction design,
- evaluation and feedback loops for agent workflow quality,
- repository-grounded agent orchestration,
- source-controlled research and knowledge accumulation?

## Source Scope

Allowed sources:

- Public web.
- Official OpenAI and Codex documentation, release notes, and product guidance.
- Public engineering blogs and docs from agentic coding tools and frameworks.
- Public research papers, technical reports, and benchmarks about coding agents, tool-using agents, prompt/context engineering, agent evaluation, and software engineering agents.
- Public repositories and docs for relevant agent harnesses, evaluation harnesses, and context management frameworks.

Preferred source families:

- Official product documentation and changelogs.
- Primary research papers or benchmark reports.
- Maintainer-authored engineering writeups.
- Repositories with active usage signals and recent updates.
- Postmortems or case studies that include concrete failure modes.

Time window:

- Prefer sources from 2024-2026.
- Include older sources only when they established still-relevant terminology, benchmark methodology, or workflow patterns.

Languages:

- English and Japanese sources are allowed.

Exclusions:

- Do not use private ChatGPT history, browser history, personal email, local unpublished files, secrets, credentials, or private logs.
- Do not treat marketing pages as strong evidence unless they link to technical details, docs, or benchmark methodology.
- Do not rely on uncited social media claims except as leads for better sources.

## Quality Bar

- Separate directly sourced claims from inference.
- Prefer official or primary sources for current product behavior.
- Mark claims as weak when sources are stale, inaccessible, marketing-only, anecdotal, or contradictory.
- For each trend, identify why it matters for SpecDock skill/subagent/workflow improvement.
- Include source dates and freshness risk where visible.
- Preserve citations or source links for every substantial claim.
- Highlight unresolved uncertainty and concrete follow-up research questions.

## Output Shape

Produce a report with these sections:

1. Executive summary.
2. Vocabulary and taxonomy:
   - harness engineering,
   - context engineering,
   - skill design,
   - subagent orchestration,
   - evaluation harness,
   - workflow memory,
   - source-controlled knowledge library.
3. Current practice map:
   - what leading tools and teams appear to be doing now,
   - which practices are broadly converging,
   - which practices remain experimental or disputed.
4. Best practices for Codex-centered harness engineering:
   - repo inspection,
   - tool routing,
   - browser / external research boundaries,
   - permission and sandbox design,
   - verification and completion auditing,
   - failure recovery,
   - human handoff.
5. Best practices for context engineering:
   - context packet design,
   - memory and source-of-truth separation,
   - summarization and compaction,
   - long-running goal continuity,
   - active issue / epic context,
   - avoiding stale or hallucinated context.
6. Skill and subagent instruction design patterns:
   - progressive disclosure,
   - trigger descriptions,
   - role boundaries,
   - delegated authorship,
   - reviewer independence,
   - evidence handoff,
   - failure-mode instructions.
7. Evaluation and PDCA loops:
   - task-level success criteria,
   - workflow regression tests,
   - transcript review,
   - rubric design,
   - adversarial or skeptical review,
   - dogfooding feedback intake.
8. Applicability to SpecDock:
   - actionable recommendations for `epic-00158`,
   - candidate follow-up issues,
   - risks and anti-patterns to avoid,
   - suggested structure for the `discussions/` research library.
9. Comparison tables:
   - source / year / claim / evidence strength / relevance to SpecDock,
   - practice / benefit / risk / verification method,
   - tool or framework / harness concept / context concept / evaluation concept.
10. Sources used and citation list.
11. Uncertainties and next research branches.

## Non-goals

- Do not draft final SpecDock requirements, design, or plan documents yet.
- Do not propose broad rewrites without evidence.
- Do not assume current SpecDock implementation details beyond the prompt.
- Do not include secrets, local private files, or personal browsing history.
- Do not perform direct code changes.

## Verification Request

For each important claim:

- State whether it is directly sourced or inferred.
- Link the source.
- Mark the source type: official docs, research paper, benchmark report, repo docs, engineering blog, case study, or anecdotal.
- Mark evidence strength: strong, medium, weak.
- Mark freshness risk: low, medium, high.
- Explain how the claim could be verified independently by Codex later.

## Follow-up Research Branches

Run separate Deep Research tasks if the first report is too broad:

- Branch A: Codex and OpenAI-specific current guidance for agentic coding workflows.
- Branch B: Context engineering patterns for long-running coding agents.
- Branch C: Evaluation harnesses and regression testing for software engineering agents.
- Branch D: Skill / subagent instruction design and progressive disclosure.
- Branch E: Repository-grounded workflow memory, source-of-truth, and handoff design.

## Local Tracking

- label: `codex-harness-context-engineering-research`
- project_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/project`
- thread_or_report_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a2223ec-5788-83a4-85cc-f231e0ae93ea`
- report_file: `20260605t014300z-research-codex-harness-context-engineering-deep-research-report.md`
- download_file: `/Users/iwasawayuuta/Downloads/deep-research-report.md`
- state: `completed`
- source_scope: `public web; official docs; research papers; engineering blogs; public repos; no private local data`
- registered_at: `2026-06-05T01:13:06Z`
- submitted_at: `2026-06-05T01:22:15Z`
- completed_at: `2026-06-05T01:43:00Z`
- last_checked_at: `2026-06-05T01:43:00Z`
- exported_at: `2026-06-05T01:43:00Z`
- exported_bytes: `37992`
- exported_lines: `237`
- visible_research_plan: `Codex harness and context research`
- visible_activity:
  - `Survey official OpenAI/Codex docs and release notes from 2023-2026.`
  - `Collect engineering blogs, repo READMEs, and case studies on agentic coding workflows.`
  - `Gather academic papers and benchmark reports on coding agents and context engineering.`
  - `Extract best practices and map them to SpecDock epic-00158 actionable items.`
  - `Assemble citation table with evidence strength, freshness risk, and verification steps.`
