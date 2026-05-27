---
created_by_role: spec-dock-implementation-planner
scope_id: iss-00131
source_paths:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
intended_targets:
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# S04 Implementation Planner Smoke Draft

## Plan Summary

This draft records S04 implementation-planner smoke evidence for `iss-00131`.
The observed planning contract is limited to fresh-spawn discussion authoring:
create one new scope-local discussion Markdown file and leave canonical docs,
source, tests, config, agent assets, GitHub workflow files, secrets, existing
discussion files, deletes, renames, symlinks, and nested directories untouched.

## Requirement / Design Traceability

- `requirement.md` AC-003 requires the delegated role to respond instead of
  returning `agent type is currently not available`.
- `requirement.md` AC-004 requires exactly one allowed scope-local discussion
  draft to be created as the positive write path.
- `requirement.md` AC-005 and `design.md` require post-run diff guard
  classification for forbidden changes.
- `design.md` treats `workspace-write` as a soft workflow boundary, not a hard
  path allow-list.
- `plan.md` S04 owns the manual smoke and discussion write evidence.

## Milestones

- Confirm source docs and S04 constraints.
- Create the single task-local discussion draft requested by the orchestrator.
- Hand off the draft as proposed evidence with `adoption_status: unreviewed`
  and `diff_guard_result: pending`.

## Dependency-Derived Execution Order

S04 depends on S01-S03 completing the role TOML, guidance, docs, and mirror
parity work. This smoke draft should be consumed only after the main
orchestrator verifies the current run diff and records the result in
`report.md`.

## Issue / Step Slicing

- Slice: S04 positive write smoke for `implementation-planner`.
- In scope: one new direct-child Markdown file under the target issue
  `discussions/`.
- Out of scope: canonical report edits, reviewer approval, phase promotion,
  implementation readiness, issue finish, and existing draft updates.

## Test Strategy Mapping

- Maps to `tc-007` by demonstrating the role can respond in the static adapter
  path.
- Maps to `tc-008` by producing one allowed discussion Markdown file for later
  diff guard inspection.
- Requires main-orchestrator verification with `git status`, `git diff
  --name-status`, and content inspection before any adoption.

## Review Gates

This draft does not claim a reviewer pass. The main orchestrator should run or
record the fresh reviewer gate required by the issue plan after diff guard
classification.

## Rollback / Compatibility

If the diff guard finds any forbidden change, this delegated output should be
classified as adoption-ineligible. No canonical integration is implied by this
file.

## Docs Impact

No docs changes are proposed here. The only intended canonical target is
`report.md` evidence, and that integration remains main-orchestrator-only.

## Final Quality Gate

Before adoption, verify that the only change attributable to this delegated run
is this new Markdown file and that the frontmatter remains parseable with
`adoption_status: unreviewed` and `diff_guard_result: pending`.

## Plan Blockers

none

## Integration Notes for Main Orchestrator

Delegated Draft Evidence:

- role: `spec-dock-implementation-planner`
- phase: plan
- scope: `iss-00131`
- source artifacts read:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
- draft artifact path:
  `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00131-debug-codex-subagent-permission-profile-callability/discussions/20260527t002046z-disc-s04-implementation-planner-smoke.md`
- draft status: `produced`
- authority: `proposed`
- adoption_status: `unreviewed`
- reflected_to: `[]`
- intended_targets:
  - `spec-dock/active/issue/report.md`
- diff_guard_result: `pending`
- integration notes: record this as S04 smoke evidence only after the
  orchestrator diff guard confirms the run touched no forbidden path.
- rejected portions: none
- blockers: none
- canonical artifacts edited: `none`
- final authority claimed: `no`

Adoption ledger note: the main orchestrator must decide whether and how to
integrate this draft into canonical `report.md`.
