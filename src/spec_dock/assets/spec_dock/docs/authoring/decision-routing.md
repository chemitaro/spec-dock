# Decision Routing Authoring Guide

This guide helps authoring agents decide where a finding belongs before execution handoff. Workflow docs own the entry rules; this file owns reusable examples and good / bad routing patterns. Keep templates and skills thin: link here instead of copying these examples into generated artifacts.

## Routing Rule

Route by the smallest durable scope that can own the decision without hiding future work.

| Finding type | Destination | Use when | Handoff result |
|---|---|---|---|
| Issue-local implementation tradeoff | Issue | The decision affects only one implementation slice and is reversible or local to the issue. | Record in issue design / plan / report and continue only if the issue remains executable. |
| Cross-issue design backbone | Epic | The decision affects issue decomposition, ownership boundaries, dependency direction, shared component behavior, or workflow policy across multiple issues. | Update the Epic artifact or create Epic-scope follow-up before Issue execution. |
| Cross-epic operating decision | Initiative | The decision affects multiple epics, investment scope, success metrics, product direction, or operating model. | Update the Initiative artifact or create Initiative-scope follow-up before Epic / Issue decomposition depends on it. |
| Long-lived architecture decision | ADR | The decision should be durable, independently discoverable, and reusable beyond one scope tree. | Create or update an ADR candidate, then link the accepted outcome from affected artifacts. |
| Missing source of truth | Clarification | The agent cannot decide scope, acceptance, non-scope, owner intent, or priority from available sources. | Return to clarification and ask one essential question after source-grounded research. |

## Generic Examples

| Finding | Route | Why |
|---|---|---|
| A single issue can choose between two equivalent helper names while preserving public behavior. | Issue-local | The tradeoff is local and does not change decomposition or durable policy. |
| Several issues need the same ownership boundary before any one issue can implement safely. | Epic | The boundary is a cross-issue design backbone. |
| A proposed change alters which teams or product areas are in scope for multiple epics. | Initiative | The decision changes investment scope and operating model. |
| A storage or integration style should become the default for future unrelated work. | ADR | The decision is long-lived and should be discoverable outside the current tree. |
| The issue title asks for implementation, but the sources disagree about the required behavior. | Clarification | Execution would require inventing acceptance criteria. |

## Good Patterns

- good: Keep a reversible local implementation choice in the Issue, with report evidence explaining why no promotion is needed.
- good: Promote a cross-issue dependency direction to Epic before writing issue plans that assume that direction.
- good: Promote a cross-epic success metric or responsibility boundary to Initiative before splitting new epics.
- good: Use ADR for a decision that future initiatives should find without reading this issue's report.
- good: Use clarification when the agent can name the missing decision but cannot infer the owner's intent from source-grounded research.

## Bad Patterns

- bad: Treat a Decision-only Issue as execution-ready because it has a title and a branch.
- bad: Hide a cross-issue ownership decision inside one issue's plan and let sibling issues discover it later.
- bad: Put reusable examples or routing tutorials into templates that will remain in completed artifacts.
- bad: Store a durable decision only in `report.md` when future agents must rely on it.
- bad: Ask the user a broad question before checking existing docs, code, ADRs, discussions, and workflow rules.

## Handoff Checklist

- The finding has one destination: Issue-local, Epic, Initiative, ADR, or clarification.
- The chosen destination is the smallest scope that can safely own the decision.
- Execution handoff does not depend on an unstated durable decision.
- Examples and instructional guidance stay in docs; completed requirement / design / plan artifacts contain only adopted scope-specific facts.
