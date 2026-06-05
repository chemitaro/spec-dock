---
type: research
status: completed
created_at: "2026-06-05T02:50:55Z"
source: "deep-research-use task package"
epic: "epic-00158"
title: "Branch C Deep Research task package for agent workflow compliance, gate enforcement, and eval scenarios"
---

# Branch C Deep Research Task Package: Agent Workflow Compliance, Gate Enforcement, and Eval Scenarios

## Status

This is a follow-up Deep Research task package for the active `epic-00158` research library.

Prior library reports:

- `20260605t014300z-research-codex-harness-context-engineering-deep-research-report.md`
- `20260605t021127z-research-branch-a-codex-openai-guidance-deep-research-report.md`
- `20260605t024753z-research-branch-b-execution-plan-sdk-context-packet-deep-research-report.md`

This branch focuses on the user-reported failure mode: capable agents still skip review gates, commits, sequential authoring phases, or required delegation. The goal is to gather source-backed patterns for making workflow compliance observable, enforceable, and evaluable without over-constraining the model.

## Objective

Create a source-backed research report that helps SpecDock harden agent workflow compliance through gate-state design, fail-closed preflight checks, report templates, reviewer freshness contracts, and eval scenarios.

The report should turn current public guidance and implementation patterns into actionable recommendations for multiple follow-up issues under `epic-00158 Agent Workflow PDCA Hardening`.

## Research Question

How should a SpecDock-like coding-agent workflow prevent, detect, and iteratively reduce noncompliance such as skipped review gates, skipped commits, missing delegation, stale reviewer evidence, and premature phase transitions?

Investigate:

- gate-state and state-machine patterns for coding-agent workflows,
- fail-closed preflight/status commands and conservative JSON status design,
- reviewer freshness and evidence validity patterns,
- report/template structures that make blockers and legal next actions visible,
- CI, hook, lint, and eval approaches that catch workflow violations,
- adversarial prompt/eval cases that test whether agents stop, wait, delegate, review, commit, and avoid false pass,
- how to balance enforcement with preserving high model performance,
- migration/compatibility strategies for legacy issues that lack evidence,
- adjacent public patterns from agent frameworks, workflow engines, CI systems, and policy-as-code tools when useful as secondary comparison.

## Source Scope

Allowed sources:

- Public web.
- Official OpenAI/Codex documentation, OpenAI Cookbook, OpenAI engineering posts, official OpenAI GitHub repositories, and official examples.
- Public primary or near-primary sources for agent workflow evaluation, guardrails, human-in-the-loop approvals, policy-as-code, CI checks, and state-machine workflow enforcement.
- Public GitHub repositories/issues that show concrete gate/status/eval/report patterns or contradiction signals.
- Adjacent non-Codex systems only as secondary comparison, clearly marked as non-Codex evidence.

Preferred time window:

- Prefer 2025-2026 sources.
- Include older sources only when they define still-current workflow, CI, policy-as-code, or state-machine patterns.

Exclusions:

- Do not use private ChatGPT history, browser history, unpublished local repo files, personal files, secrets, credentials, private logs, or private source code.
- Do not assume hidden OpenAI implementation details.
- Do not treat unofficial community conventions as Codex requirements unless supported by first-party OpenAI/Codex sources.
- Do not draft final SpecDock requirements, design, or code changes.

## Quality Bar

- Separate first-party OpenAI/Codex claims, secondary-source claims, and inference.
- Preserve source links, dates, version signals, and repository names where available.
- Mark freshness risk for every important recommendation.
- Flag beta, preview, experimental, or surface-specific behavior.
- Explicitly identify what Codex should directly verify before converting a finding into SpecDock requirements.
- Prefer concrete schema examples, command contracts, state enums, evidence rules, eval prompts, and acceptance checks over generic advice.

## Output Shape

Produce a report with these sections:

1. Executive summary.
2. Source map:
   - source,
   - date or freshness signal,
   - surface covered,
   - evidence strength,
   - relevance to SpecDock.
3. Failure-mode taxonomy:
   - skipped review,
   - skipped commit,
   - skipped delegation,
   - parallel requirement/design/plan authoring,
   - stale reviewer evidence,
   - unavailable/waived/provisional evidence falsely treated as pass,
   - premature execution or finish.
4. Gate-state design:
   - state machine concepts,
   - legal next transitions,
   - fail-closed status,
   - warning-only vs blocking fields,
   - machine-readable JSON shape.
5. Reviewer freshness and evidence validity:
   - pass/fail/stale/missing/waived/provisional/unavailable semantics,
   - timestamp and scope matching,
   - source artifact linkage,
   - false-pass prevention.
6. Report/template and CLI affordances:
   - visible blocker format,
   - legal next action,
   - required evidence checklist,
   - preflight/status command designs,
   - how to keep prompts concise.
7. Evaluation and regression harness:
   - adversarial prompts,
   - expected compliant behavior,
   - trace/eval signals,
   - dataset construction,
   - CI/nightly checks.
8. Migration and compatibility:
   - legacy issues without evidence,
   - warning mode,
   - waivers,
   - dogfooding rollout.
9. Performance and ergonomics trade-offs:
   - avoiding over-constraint,
   - minimizing context load,
   - avoiding false blockers,
   - maintaining agent autonomy where safe.
10. Candidate follow-up issues for `epic-00158`, each with:
    - title,
    - problem,
    - source-backed rationale,
    - likely impacted files or docs,
    - acceptance evidence.
11. Verification checklist before implementation.
12. Sources used and citation list.
13. Uncertainties and recommended next research branches.

## Non-goals

- Do not make implementation changes.
- Do not write final SpecDock requirements, design, or plan documents.
- Do not assume the local SpecDock repository contents are visible to Deep Research.
- Do not require a giant workflow-engine rewrite as the first recommendation.
- Do not send or request private local files.

## Deep Research Prompt

```text
Objective:
Create a source-backed research report for a SpecDock epic named "Agent Workflow PDCA Hardening". The report should help harden coding-agent workflow compliance through gate-state design, fail-closed preflight checks, report templates, reviewer freshness contracts, and eval scenarios.

Research question:
How should a SpecDock-like coding-agent workflow prevent, detect, and iteratively reduce noncompliance such as skipped review gates, skipped commits, missing delegation, stale reviewer evidence, and premature phase transitions?

Investigate:
- gate-state and state-machine patterns for coding-agent workflows,
- fail-closed preflight/status commands and conservative JSON status design,
- reviewer freshness and evidence validity patterns,
- report/template structures that make blockers and legal next actions visible,
- CI, hook, lint, and eval approaches that catch workflow violations,
- adversarial prompt/eval cases that test whether agents stop, wait, delegate, review, commit, and avoid false pass,
- how to balance enforcement with preserving high model performance,
- migration/compatibility strategies for legacy issues that lack evidence,
- adjacent public patterns from agent frameworks, workflow engines, CI systems, and policy-as-code tools when useful as secondary comparison.

Source scope:
- Use public web sources.
- Prioritize official OpenAI/Codex documentation, OpenAI Cookbook, OpenAI engineering posts, official OpenAI GitHub repositories, and official examples.
- Use public primary or near-primary sources for agent workflow evaluation, guardrails, human-in-the-loop approvals, policy-as-code, CI checks, and state-machine workflow enforcement.
- Use public GitHub repositories/issues only to show concrete gate/status/eval/report patterns or contradiction signals.
- Adjacent non-Codex systems may be compared only as secondary evidence and must be clearly marked as non-Codex.
- Prefer 2025-2026 sources. Use older sources only when they define still-current workflow, CI, policy-as-code, or state-machine patterns.

Exclusions and privacy:
- Do not use private ChatGPT history, browser history, unpublished local repo files, personal files, secrets, credentials, private logs, or private source code.
- Do not assume hidden OpenAI implementation details.
- Do not treat unofficial community conventions as Codex requirements unless supported by first-party OpenAI/Codex sources.
- Do not draft final SpecDock requirements, design, or code changes.

Quality bar:
- Separate first-party OpenAI/Codex claims, secondary-source claims, and inference.
- Preserve source links, dates, version signals, and repository names where available.
- Mark freshness risk for every important recommendation.
- Flag beta, preview, experimental, or surface-specific behavior.
- Explicitly identify what Codex should directly verify before converting a finding into SpecDock requirements.
- Prefer concrete schema examples, command contracts, state enums, evidence rules, eval prompts, and acceptance checks over generic advice.

Output shape:
1. Executive summary.
2. Source map with source, date/freshness signal, surface covered, evidence strength, and relevance to SpecDock.
3. Failure-mode taxonomy: skipped review, skipped commit, skipped delegation, parallel requirement/design/plan authoring, stale reviewer evidence, unavailable/waived/provisional evidence falsely treated as pass, premature execution or finish.
4. Gate-state design: state machine concepts, legal next transitions, fail-closed status, warning-only vs blocking fields, machine-readable JSON shape.
5. Reviewer freshness and evidence validity: pass/fail/stale/missing/waived/provisional/unavailable semantics, timestamp and scope matching, source artifact linkage, false-pass prevention.
6. Report/template and CLI affordances: visible blocker format, legal next action, required evidence checklist, preflight/status command designs, concise prompts.
7. Evaluation and regression harness: adversarial prompts, expected compliant behavior, trace/eval signals, dataset construction, CI/nightly checks.
8. Migration and compatibility: legacy issues without evidence, warning mode, waivers, dogfooding rollout.
9. Performance and ergonomics trade-offs: avoiding over-constraint, minimizing context load, avoiding false blockers, maintaining safe autonomy.
10. Candidate follow-up issues for epic-00158 with title, problem, source-backed rationale, likely impacted files/docs, and acceptance evidence.
11. Verification checklist before implementation.
12. Sources used and citation list.
13. Uncertainties and recommended next research branches.
```

## Local Tracking

- label: `branch-c-agent-workflow-compliance-gates`
- project_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/project`
- thread_or_report_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a223cc6-d31c-83a2-93ce-471f12095d26`
- current_url: `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a223cc6-d31c-83a2-93ce-471f12095d26`
- report_file: `spec-dock/active/epic/discussions/20260605t034636z-research-branch-c-agent-workflow-compliance-gates-deep-research-report.md`
- download_file: `/Users/iwasawayuuta/Downloads/deep-research-report (3).md`
- state: `completed`
- source_scope: `public web; official OpenAI/Codex and primary guardrail/eval/workflow sources preferred; no private local data`
- registered_at: `2026-06-05T02:50:55Z`
- submitted_at: `2026-06-05T03:06:29Z`
- started_at: `2026-06-05T03:06:29Z`
- completed_at: `2026-06-05T03:46:36Z`
- last_checked_at: `2026-06-05T03:46:36Z`
- exported_at: `2026-06-05T03:46:36Z`
- visible_plan: `SpecDock Agent Workflow PDCA Hardening plan shown and accepted; visible steps cover official OpenAI/Codex documentation, state-machine/CI/policy-as-code sources, reviewer/preflight/JSON status schemas, adversarial eval prompts, and synthesis into source-annotated report.`
- visible_state: `Completed; visible completion showed 31m, 24 citations, 124 searches. Markdown exported and copied into epic discussions.`
- handoff: `Completed report copied into epic discussions; downloaded Markdown remains in Downloads.`
