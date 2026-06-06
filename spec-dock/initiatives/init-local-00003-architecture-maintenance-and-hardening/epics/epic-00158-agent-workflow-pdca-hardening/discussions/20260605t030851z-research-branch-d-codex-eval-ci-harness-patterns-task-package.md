---
type: research
status: completed
created_at: "2026-06-05T03:08:51Z"
source: "deep-research-use task package"
epic: "epic-00158"
title: "Branch D Deep Research task package for Codex eval, CI, and regression harness implementation patterns"
---

# Branch D Deep Research Task Package: Codex Eval, CI, and Regression Harness Patterns

## Status

This is a follow-up Deep Research task package for the active `epic-00158` research library.

Prior library reports:

- `20260605t014300z-research-codex-harness-context-engineering-deep-research-report.md`
- `20260605t021127z-research-branch-a-codex-openai-guidance-deep-research-report.md`
- `20260605t024753z-research-branch-b-execution-plan-sdk-context-packet-deep-research-report.md`

Related in-flight branch:

- `20260605t025055z-research-branch-c-agent-workflow-compliance-gates-task-package.md`

Branch C focuses on workflow compliance gates. Branch D focuses on practical harness implementation patterns: how public teams and first-party guidance run coding-agent evals, regression suites, CI checks, prompt/instruction tests, and artifact-based verification around Codex-like coding workflows.

## Objective

Create a source-backed research report that helps SpecDock build and dogfood a practical regression harness for Codex-centered workflows, including `codex exec`-style automation, GitHub Actions or local CI integration, trace/log capture, prompt/instruction evals, and artifact verification.

The report should support future issues under `epic-00158 Agent Workflow PDCA Hardening` without prescribing implementation changes directly.

## Research Question

What are the current public best practices and implementation patterns for testing, evaluating, and continuously regressing Codex-like coding-agent workflows in local CLI, CI, and repository-governed environments?

Investigate:

- first-party OpenAI/Codex guidance for non-interactive execution, automation, CI, sandboxing, permissions, logs, and reviews,
- public examples of `codex exec` or comparable coding-agent harnesses,
- patterns for prompt/instruction regression tests and adversarial instruction-following checks,
- trace/log capture formats that make agent decisions, tool calls, approvals, file diffs, and verification evidence auditable,
- how teams integrate coding-agent checks with GitHub Actions, pre-commit hooks, branch protection, or PR review automation,
- how to design small deterministic fixtures and golden outputs for agent workflows without overfitting to model phrasing,
- how to score agent workflow compliance with rubrics, structured outputs, or external graders,
- how to separate deterministic tool-state checks from subjective model-quality checks,
- how to handle flaky or long-running agent evals through retries, quarantine, nightly runs, or confidence bands,
- how to preserve developer ergonomics and model performance while adding regression coverage.

## Source Scope

Allowed sources:

- Public web.
- Official OpenAI/Codex documentation, OpenAI Cookbook, OpenAI engineering posts, official OpenAI GitHub repositories, and official examples.
- Public GitHub repositories, issues, PRs, and CI configs showing concrete coding-agent eval, CLI automation, or regression harness patterns.
- Public primary or near-primary sources for AI eval frameworks, prompt regression, agent tracing, CI integration, and policy/testing automation.
- Adjacent systems such as SWE-agent, OpenHands, Continue, Aider, Claude Code, Cursor, LangSmith, Promptfoo, or OpenAI Evals may be used only as comparison evidence and must be clearly marked as non-Codex when not first-party OpenAI/Codex.

Preferred time window:

- Prefer 2025-2026 sources.
- Include older sources only when still-current and foundational for CI/eval/harness patterns.

Exclusions:

- Do not use private ChatGPT history, browser history, unpublished local repo files, personal files, secrets, credentials, private logs, or private source code.
- Do not assume hidden OpenAI implementation details.
- Do not treat non-Codex tools as Codex requirements.
- Do not draft final SpecDock requirements, design, code, or tests.

## Quality Bar

- Separate first-party OpenAI/Codex claims, public implementation examples, adjacent-tool practices, and inference.
- Preserve source links, dates, version signals, repository names, command names, and CI file paths where available.
- Prefer concrete examples: commands, JSONL/event schemas, GitHub Actions snippets, fixture layouts, grading rubrics, and artifact contracts.
- Mark stale, beta, preview, undocumented, or surface-specific behavior.
- Identify what Codex should directly verify before converting findings into SpecDock issues.
- Explicitly call out anti-patterns that create false confidence, such as snapshotting model prose too tightly or treating self-reported completion as evidence.

## Output Shape

Produce a report with these sections:

1. Executive summary.
2. Source map:
   - source,
   - date or freshness signal,
   - surface covered,
   - evidence strength,
   - relevance to SpecDock.
3. Codex-specific automation surface:
   - non-interactive execution,
   - permissions/sandboxing,
   - logging/JSONL/trace capture,
   - CI suitability,
   - current limitations or unknowns.
4. Public harness implementation patterns:
   - fixture layout,
   - command runner,
   - expected artifacts,
   - diff capture,
   - report capture,
   - cleanup strategy.
5. Prompt and instruction regression patterns:
   - adversarial prompts,
   - AGENTS/instruction hierarchy tests,
   - skill invocation tests,
   - context compaction/handoff tests,
   - reviewer independence tests.
6. Scoring and grading:
   - deterministic checks,
   - rubric checks,
   - model-as-judge cautions,
   - structured output checks,
   - confidence and flake handling.
7. CI and developer workflow integration:
   - GitHub Actions,
   - pre-commit/local checks,
   - nightly or quarantine lanes,
   - branch protection or PR review use,
   - cost and runtime controls.
8. Artifact and trace schema recommendations:
   - event fields,
   - status fields,
   - evidence links,
   - error/unknown handling,
   - privacy/redaction.
9. Candidate SpecDock follow-up issues for `epic-00158`, each with:
   - title,
   - problem,
   - source-backed rationale,
   - likely impacted files/docs,
   - acceptance evidence.
10. Anti-patterns and risks.
11. Verification checklist before implementation.
12. Sources used and citation list.
13. Uncertainties and recommended next research branches.

## Non-goals

- Do not implement the harness.
- Do not write final SpecDock requirement/design/plan documents.
- Do not use or request private local files.
- Do not require a large new eval platform as the first step.
- Do not treat generic LLM eval advice as sufficient unless it maps to coding-agent workflow evidence.

## Deep Research Prompt

```text
Objective:
Create a source-backed research report for a SpecDock epic named "Agent Workflow PDCA Hardening". The report should help SpecDock build and dogfood a practical regression harness for Codex-centered workflows, including non-interactive execution, CI integration, trace/log capture, prompt/instruction evals, and artifact verification.

Research question:
What are the current public best practices and implementation patterns for testing, evaluating, and continuously regressing Codex-like coding-agent workflows in local CLI, CI, and repository-governed environments?

Investigate:
- first-party OpenAI/Codex guidance for non-interactive execution, automation, CI, sandboxing, permissions, logs, and reviews,
- public examples of codex exec or comparable coding-agent harnesses,
- patterns for prompt/instruction regression tests and adversarial instruction-following checks,
- trace/log capture formats that make agent decisions, tool calls, approvals, file diffs, and verification evidence auditable,
- how teams integrate coding-agent checks with GitHub Actions, pre-commit hooks, branch protection, or PR review automation,
- how to design small deterministic fixtures and golden outputs for agent workflows without overfitting to model phrasing,
- how to score agent workflow compliance with rubrics, structured outputs, or external graders,
- how to separate deterministic tool-state checks from subjective model-quality checks,
- how to handle flaky or long-running agent evals through retries, quarantine, nightly runs, or confidence bands,
- how to preserve developer ergonomics and model performance while adding regression coverage.

Source scope:
- Use public web sources.
- Prioritize official OpenAI/Codex documentation, OpenAI Cookbook, OpenAI engineering posts, official OpenAI GitHub repositories, and official examples.
- Use public GitHub repositories, issues, PRs, and CI configs showing concrete coding-agent eval, CLI automation, or regression harness patterns.
- Use public primary or near-primary sources for AI eval frameworks, prompt regression, agent tracing, CI integration, and policy/testing automation.
- Adjacent systems such as SWE-agent, OpenHands, Continue, Aider, Claude Code, Cursor, LangSmith, Promptfoo, or OpenAI Evals may be used only as comparison evidence and must be clearly marked as non-Codex when not first-party OpenAI/Codex.
- Prefer 2025-2026 sources. Use older sources only when still-current and foundational for CI/eval/harness patterns.

Exclusions and privacy:
- Do not use private ChatGPT history, browser history, unpublished local repo files, personal files, secrets, credentials, private logs, or private source code.
- Do not assume hidden OpenAI implementation details.
- Do not treat non-Codex tools as Codex requirements.
- Do not draft final SpecDock requirements, design, code, or tests.

Quality bar:
- Separate first-party OpenAI/Codex claims, public implementation examples, adjacent-tool practices, and inference.
- Preserve source links, dates, version signals, repository names, command names, and CI file paths where available.
- Prefer concrete examples: commands, JSONL/event schemas, GitHub Actions snippets, fixture layouts, grading rubrics, and artifact contracts.
- Mark stale, beta, preview, undocumented, or surface-specific behavior.
- Identify what Codex should directly verify before converting findings into SpecDock issues.
- Explicitly call out anti-patterns that create false confidence, such as snapshotting model prose too tightly or treating self-reported completion as evidence.

Output shape:
1. Executive summary.
2. Source map with source, date/freshness signal, surface covered, evidence strength, and relevance to SpecDock.
3. Codex-specific automation surface: non-interactive execution, permissions/sandboxing, logging/JSONL/trace capture, CI suitability, current limitations or unknowns.
4. Public harness implementation patterns: fixture layout, command runner, expected artifacts, diff capture, report capture, cleanup strategy.
5. Prompt and instruction regression patterns: adversarial prompts, AGENTS/instruction hierarchy tests, skill invocation tests, context compaction/handoff tests, reviewer independence tests.
6. Scoring and grading: deterministic checks, rubric checks, model-as-judge cautions, structured output checks, confidence and flake handling.
7. CI and developer workflow integration: GitHub Actions, pre-commit/local checks, nightly or quarantine lanes, branch protection or PR review use, cost and runtime controls.
8. Artifact and trace schema recommendations: event fields, status fields, evidence links, error/unknown handling, privacy/redaction.
9. Candidate SpecDock follow-up issues for epic-00158 with title, problem, source-backed rationale, likely impacted files/docs, and acceptance evidence.
10. Anti-patterns and risks.
11. Verification checklist before implementation.
12. Sources used and citation list.
13. Uncertainties and recommended next research branches.
```

## Local Tracking

- label: `branch-d-codex-eval-ci-harness-patterns`
- project_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/project`
- thread_or_report_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a223e66-d5a4-83a2-b8d6-2519a9bc14ac`
- current_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a223e66-d5a4-83a2-b8d6-2519a9bc14ac`
- report_file: `spec-dock/active/epic/discussions/20260605t034636z-01-research-branch-d-codex-eval-ci-harness-patterns-deep-research-report.md`
- download_file: `/Users/iwasawayuuta/Downloads/deep-research-report (4).md`
- state: `completed`
- source_scope: `public web; official OpenAI/Codex and public coding-agent eval/CI/harness examples preferred; no private local data`
- registered_at: `2026-06-05T03:08:51Z`
- submitted_at: `2026-06-05T03:13:06Z`
- started_at: `2026-06-05T03:13:06Z`
- completed_at: `2026-06-05T03:46:36Z`
- last_checked_at: `2026-06-05T03:46:36Z`
- exported_at: `2026-06-05T03:46:36Z`
- visible_plan: `Agent Workflow PDCA Hardening Research plan shown and accepted; visible steps cover official OpenAI/Codex docs, public GitHub harness and CI examples, agent-eval and prompt-regression patterns from 2024-2026, JSONL traces, GitHub Actions snippets, fixture layouts, and follow-up issue synthesis.`
- visible_state: `Completed; visible completion showed 16m, 23 citations, 143 searches. Markdown exported and copied into epic discussions.`
- handoff: `Completed report copied into epic discussions; downloaded Markdown remains in Downloads.`
