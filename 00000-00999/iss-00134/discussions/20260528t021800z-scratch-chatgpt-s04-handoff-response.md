---
kind: scratch
scope: issue
issue_id: iss-00134
created_at: 2026-05-28T02:18:00Z
created_by: codex
source: ChatGPT Web
thread_url: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a179be7-0ddc-83a3-9288-684da67838a8
prompt: 20260528t021000z-scratch-chatgpt-s04-handoff-prompt.md
adoption_status: unreviewed
reflected_to: []
---

# ChatGPT Response: S04 Existing Skill Handoff Boundary

## Recommendation

ChatGPT recommended a minimal "A plus light B" approach, not a no-op:

- Update `spec-driven-tdd-workflow/SKILL.md` so the new `spec-dock-requirement-grill` skill is discoverable from the top-level routing list.
- Add one short blocker/follow-up sentence to each of:
  - `spec-dock-system-architect/SKILL.md`
  - `spec-dock-implementation-planner/SKILL.md`
- Do not update `spec-dock-issue-execution/SKILL.md`, `spec-dock-adr-facilitation/SKILL.md`, CLI commands, agent wrappers, or template structure in S04.

## Suggested Wording

For `spec-driven-tdd-workflow/SKILL.md`:

```markdown
- `spec-dock-requirement-grill`: issue-level readiness clarification when requirement, design, plan, artifact authority, validation path, or ADR need is ambiguous; use before issue execution or delegated design/planning when local sources cannot resolve readiness gaps.
```

For `spec-dock-system-architect/SKILL.md`:

```markdown
When requirement ambiguity blocks safe design, return the blocker to the main orchestrator and recommend `spec-dock-requirement-grill` as the next clarification workflow; do not invoke it directly or ask the user directly.
```

For `spec-dock-implementation-planner/SKILL.md`:

```markdown
When requirement/design ambiguity blocks safe planning, return the blocker to the main orchestrator and recommend `spec-dock-requirement-grill` as the next clarification workflow; do not invoke it directly or ask the user directly.
```

## Rationale

- A no-op would leave the new skill hard to discover from existing workflow routing.
- Broad edits would create circular responsibility between issue execution, design/planning authoring roles, and requirement clarification.
- The architect/planner additions should preserve their existing rule: they return blockers to the orchestrator and must not ask the user directly.
- `spec-dock-issue-execution` should stay focused on execution, because requirement grill is a pre-execution readiness workflow.

## Suggested Verification

- Inspect references to `spec-dock-requirement-grill` in the three changed skill files.
- Refresh the dogfooding mirror with `uvx --from . spec-dock update .`.
- Run `python -m unittest tests.test_init_update`.

## Adoption Notes

- This is unreviewed ChatGPT output until adopted in `report.md`.
- Codex must independently inspect the files and ensure wording does not grant direct user-question authority, canonical approval authority, phase promotion authority, final review authority, or implementation-start authority.
