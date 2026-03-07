---
name: spec-driven-tdd-workflow
description: Entry skill that routes work to the correct spec-dock leaf workflow.
---

# Spec-driven TDD Workflow (Hub)

- Use this as the entry/routing skill for spec-dock work.
- Keep `spec-dock/docs/` as the source of truth; skills stay concise.

## Route to leaf skills

- `spec-dock-initiative-planning`: initiative-level requirement/design/plan planning.
- `spec-dock-epic-planning`: epic-level requirement/design/plan planning.
- `spec-dock-issue-execution`: issue-level TDD execution and report updates.
- `spec-dock-adr-facilitation`: ADR drafting/decision facilitation linked to the current workflow.

## Direct references

- `spec-dock/docs/reference_github.md`
- `spec-dock/docs/reference_deps.md`
- `spec-dock/docs/reference_sync.md`
- `spec-dock/docs/reference_naming.md`

## Quick reminders

- Put interview and investigation notes under `discussions/` in the active node.
- ADR creation example: `./spec-dock/scripts/spec-dock new adr --issue iss-00123 --title "..."`
