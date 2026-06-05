---
type: research
status: rate_limited
created_at: "2026-06-05T04:14:38Z"
source: "deep-research-use task package"
epic: "epic-00158"
title: "Branch G Deep Research task package for public coding-agent harness implementations"
---

# Branch G Deep Research Task Package: Public Coding-Agent Harness Implementations

## Status

This follow-up Deep Research branch extends the active `epic-00158` research library after the initial broad report and branches A-F.

Prior Deep Research reports:

- `20260605t014300z-research-codex-harness-context-engineering-deep-research-report.md`
- `20260605t021127z-research-branch-a-codex-openai-guidance-deep-research-report.md`
- `20260605t024753z-research-branch-b-execution-plan-sdk-context-packet-deep-research-report.md`
- `20260605t034636z-research-branch-c-agent-workflow-compliance-gates-deep-research-report.md`
- `20260605t034636z-01-research-branch-d-codex-eval-ci-harness-patterns-deep-research-report.md`
- `20260605t041113z-research-branch-e-codex-context-engineering-patterns-deep-research-report.md`
- `20260605t041113z-01-research-branch-f-multi-agent-subagent-orchestration-deep-research-report.md`

Branch G narrows into public coding-agent harness implementations and operational patterns across open-source and public product documentation. The goal is to identify concrete harness structures that SpecDock can learn from without treating any one tool as authoritative.

## Objective

Create a source-backed research report that maps current public coding-agent harness implementations and their best practices for repo-local instruction loading, task planning, tool execution, sandboxing, evaluation, trace capture, pull request workflows, and long-running resume behavior.

The report should help SpecDock decide which harness concepts deserve follow-up issues under `epic-00158 Agent Workflow PDCA Hardening`.

## Research Question

What do current public coding-agent harnesses and coding-agent frameworks implement for reliable long-running software engineering workflows, and which patterns are transferable to SpecDock's skill, sub-agent, and workflow design?

Investigate:

- OpenAI Codex public docs and cookbook examples where relevant.
- Public/open-source coding-agent harnesses and frameworks, such as SWE-agent, OpenHands, Aider, Continue, Goose, Claude Code public docs, Cursor public docs, Devin public docs where public, LangGraph/LangChain agent workflows, AutoGen, CrewAI, and other relevant 2024-2026 coding-agent systems.
- Harness structure: repo context loading, instruction hierarchy, planning artifacts, task state, tool routing, shell/browser controls, sandbox or permission gates, diff/PR workflows, evaluation loops, reviewer workflows, and resume/handoff behavior.
- Concrete artifacts: config files, prompt files, runbooks, trace files, benchmark harnesses, eval scripts, GitHub Actions patterns, and PR review loops.

## Source Scope

- Public web only.
- Prefer primary sources: official docs, official repositories, release notes, engineering blogs, benchmark papers, and maintainer-authored implementation docs.
- Secondary sources are allowed only when they summarize current practice and link to primary sources.
- Exclude private repos, private browser history, local unpublished files, user personal data, and ordinary ChatGPT memory/history.
- Time window: emphasize 2024-2026, with older sources only when still foundational and explicitly marked.

## Quality Bar

- Separate directly sourced claims from inference.
- Mark source freshness, likely staleness, and uncertainty.
- Prefer implementation details over marketing claims.
- Include direct links/citations for each named framework or product.
- Flag where public docs are insufficient to determine actual runtime behavior.
- Avoid recommending adoption without identifying verification steps.

## Output Shape

Produce a Markdown report with:

1. Executive summary.
2. Source map with source, date/freshness, surface covered, evidence strength, and relevance to SpecDock.
3. Comparative matrix of public harnesses/frameworks and their relevant mechanisms.
4. Common harness architecture patterns.
5. Repo-context and instruction-loading patterns.
6. Planning, state, handoff, and resume patterns.
7. Tool execution, sandboxing, and permission-gate patterns.
8. Evaluation, CI, benchmark, and regression-harness patterns.
9. PR/review and human-in-the-loop patterns.
10. Transferable recommendations for SpecDock.
11. Anti-patterns and risks.
12. Candidate follow-up issues for `epic-00158` with title, problem, source-backed rationale, likely impacted docs/assets, and acceptance evidence.
13. Verification checklist before implementation.
14. Sources used and citation list.
15. Uncertainties and recommended next research branches.

## Non-Goals

- Do not inspect private user data or local unpublished repositories.
- Do not produce implementation changes directly.
- Do not rank tools as products for purchase.
- Do not use unsourced claims from social media as primary evidence.

## Verification Request

Explicitly distinguish:

- Public primary-source facts.
- Deep Research inferences.
- Conflicting or stale sources.
- Claims that SpecDock should independently verify before issue planning.

## Local Tracking

- label: `branch-g-public-coding-agent-harness-implementations`
- project_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/project`
- thread_or_report_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a224f59-7314-83a9-9769-20b6d59ffb93`
- current_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a224f59-7314-83a9-9769-20b6d59ffb93`
- report_file: `pending`
- download_file: `pending`
- state: `rate_limited_before_research_start`
- source_scope: `public web; official docs, official repositories, release notes, engineering blogs, benchmark papers, and maintainer-authored implementation docs preferred; no private local data`
- registered_at: `2026-06-05T04:14:38Z`
- submitted_at: `2026-06-05T04:17:38Z`
- started_at: `pending`
- completed_at: `pending`
- last_checked_at: `2026-06-05T04:36:27Z`
- exported_at: `pending`
- visible_plan: `pending`
- visible_state: `Project conversation exists and contains the Branch G prompt plus a retry message asking ChatGPT to run the prior prompt as Deep Research. A transient "回答を停止" appeared after retry, but final status check showed the same rate-limit modal again: "リクエストが多すぎます ... 数分待ってから、もう一度お試しください。" No export control, completed report, or active research state was visible.`
- handoff: `Retry inside the same Project conversation after a longer cooldown. Avoid duplicate Project threads unless this one becomes unusable. When a report completes, export Markdown from the UI and import the downloaded .md into this epic discussion folder. Do not use "今すぐ回答" as evidence.`
