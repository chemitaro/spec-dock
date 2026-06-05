---
type: research
status: completed
created_at: "2026-06-05T04:14:38Z"
source: "deep-research-use task package"
epic: "epic-00158"
title: "Branch H Deep Research task package for agent harness security observability and tool policy"
---

# Branch H Deep Research Task Package: Agent Harness Security, Observability, and Tool Policy

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

Branch H narrows into reliability controls around agent harness operation: observability, traces, audit logs, tool policy, permissioning, prompt-injection boundaries, untrusted content handling, sandboxing, and evidence retention.

## Objective

Create a source-backed research report that identifies current best practices for making coding-agent harnesses observable, auditable, and resistant to prompt injection or unsafe tool use.

The report should support future SpecDock issues that harden skill workflows, sub-agent delegation, browser/connector trust boundaries, command approvals, trace evidence, and review gates.

## Research Question

What are the current public best practices and implementation patterns for coding-agent harness security, observability, traceability, tool permissions, sandboxing, prompt-injection resistance, and audit evidence?

Investigate:

- OpenAI Codex, OpenAI Agents SDK, OpenAI tool/security guidance, and relevant cookbook examples.
- Public agent security and prompt-injection guidance from major vendors, OWASP/industry guidance where applicable, public research papers, and public framework documentation.
- Observability and tracing patterns for agents, including OpenTelemetry, LangSmith/LangGraph, Agents SDK tracing, eval traces, audit logs, and CI artifacts.
- Tool policy patterns: command allow/deny, human approval gates, browser/connector boundaries, file upload/download rules, sandbox modes, destructive action confirmation, and untrusted content handling.
- Evidence retention: what to log, what not to log, how to avoid leaking secrets, how to make review evidence sufficient without recording hidden chain-of-thought.

## Source Scope

- Public web only.
- Prefer primary sources: official docs, standards, security guidance, research papers, official repositories, release notes, engineering blogs, and maintainer-authored implementation docs.
- Secondary sources are allowed only when they link to primary sources.
- Exclude private repos, private browser history, local unpublished files, secrets, credentials, user personal data, and ordinary ChatGPT memory/history.
- Time window: emphasize 2024-2026, with older security standards only when still current and explicitly marked.

## Quality Bar

- Separate directly sourced claims from inference.
- Mark source freshness, likely staleness, and uncertainty.
- Prefer concrete controls and evidence requirements over broad security slogans.
- Identify conflicting guidance and unresolved trade-offs.
- Flag high-risk claims that SpecDock should independently verify before implementation.

## Output Shape

Produce a Markdown report with:

1. Executive summary.
2. Source map with source, date/freshness, surface covered, evidence strength, and relevance to SpecDock.
3. Threat and trust-boundary model for Codex-like coding-agent harnesses.
4. Prompt injection and untrusted content handling patterns.
5. Tool permission and approval-gate patterns.
6. Browser, connector, file, and shell boundary patterns.
7. Sandboxing and destructive-action controls.
8. Observability, tracing, audit log, and evidence retention patterns.
9. Eval and regression tests for security/observability controls.
10. Privacy and secret-handling constraints.
11. Transferable recommendations for SpecDock.
12. Anti-patterns and risks.
13. Candidate follow-up issues for `epic-00158` with title, problem, source-backed rationale, likely impacted docs/assets, and acceptance evidence.
14. Verification checklist before implementation.
15. Sources used and citation list.
16. Uncertainties and recommended next research branches.

## Non-Goals

- Do not inspect private user data, secrets, browser history, cookies, local storage, or local unpublished repositories.
- Do not produce implementation changes directly.
- Do not provide legal, compliance, or security certification advice.
- Do not treat Deep Research findings as independently verified security conclusions.

## Verification Request

Explicitly distinguish:

- Public primary-source facts.
- Deep Research inferences.
- Conflicting or stale sources.
- Claims requiring direct source verification or security review before SpecDock issue planning.

## Local Tracking

- label: `branch-h-agent-harness-security-observability`
- project_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/project`
- thread_or_report_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a2251dd-5dc4-83ab-bb3a-58b6e43744de`
- current_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a2251dd-5dc4-83ab-bb3a-58b6e43744de`
- report_file: `20260605t055403z-research-branch-h-agent-harness-security-observability-deep-research-report.md`
- download_file: `/Users/iwasawayuuta/Downloads/deep-research-report (8).md`
- state: `completed`
- source_scope: `public web; official security/tool/tracing docs, standards, research papers, official repositories, and maintainer-authored implementation docs preferred; no private local data`
- registered_at: `2026-06-05T04:14:38Z`
- submitted_at: `2026-06-05T04:35:26Z`
- started_at: `2026-06-05T05:43:05Z`
- completed_at: `2026-06-05T06:09:23Z`
- last_checked_at: `2026-06-05T06:09:23Z`
- exported_at: `2026-06-05T06:09:23Z`
- visible_plan: `pending`
- visible_state: `Deep Research completed in the Codex-only Project. Visual report card showed completion with about 17m runtime, 28 citations, and 165 searches. Markdown export produced /Users/iwasawayuuta/Downloads/deep-research-report (8).md, which was stable at 52205 bytes after a 60-second recheck.`
- handoff: `Completed and imported as 20260605t055403z-research-branch-h-agent-harness-security-observability-deep-research-report.md. Treat report claims as Deep Research output until cited sources are independently verified before issue planning.`
