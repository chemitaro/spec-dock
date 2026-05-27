---
created_by_role: spec-dock-system-architect
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

# S04 System Architect Smoke Discussion

## Requirement Coverage

This smoke note addresses the S04 evidence shape for `iss-00131`: fresh-spawn callability and one new scope-local discussion Markdown write for `system-architect`. It is evidence only for the allowed discussion authoring surface and does not close AC-003, AC-004, or AC-005 by itself.

## Existing Context Findings

The active issue defines the recovery path as guarded `workspace-write`, not a hard path allow-list. The relevant contract is: one new flat Markdown file under the task-local issue `discussions/` directory, no existing discussion updates, and no canonical or implementation edits by the delegated role.

## Design Decisions

The delegated role should produce only a proposal/evidence artifact. The main orchestrator remains responsible for post-run diff guard, Evidence Adoption Ledger disposition, canonical integration, and any later reviewer gate.

## Alternatives Considered

- Read-only smoke only: rejected for this S04 purpose because it would not verify the recovered discussion authoring surface.
- Forbidden path write probe: rejected because the plan explicitly says not to run destructive or forbidden-path write probes.
- Canonical report update by this role: rejected because canonical `report.md` remains main-orchestrator-only.

## Boundary / Contract Model

Allowed write for this smoke is exactly this file:

`spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00131-debug-codex-subagent-permission-profile-callability/discussions/20260527t001627z-disc-s04-system-architect-smoke.md`

Forbidden writes include all canonical issue docs, existing discussions, implementation files, tests, package/config files, `.agents`, `.codex`, `.github`, `.env*`, deletes, renames, symlinks, nested directories, and any second file.

## Dependency Analysis

S04 depends on S01-S03 having updated the role TOML, role instructions, workflow docs, and dogfooding mirror. This note does not independently verify those steps; it assumes the active `plan.md` and `report.md` S01-S03 evidence are the current source context.

## Source of Record

- Requirement source: `spec-dock/active/issue/requirement.md`, ID `iss-00131`, last updated `2026-05-27`.
- Design source: `spec-dock/active/issue/design.md`, ID `iss-00131`, last updated `2026-05-27`.
- Plan source: `spec-dock/active/issue/plan.md`, S04 manual smoke contract.
- Report source: `spec-dock/active/issue/report.md`, S01-S03 evidence and current ledger state.

## Data Flow / Domain Model / Interface Contract

Input is task-local consent plus the active issue docs. Output is this single discussion draft with provenance fields. The orchestrator should inspect `git status` and `git diff --name-status` after the run, then record the result in `report.md` if adopting this smoke evidence.

## File / Module Change Plan

No module or implementation changes are proposed. The only produced file is this discussion Markdown. Any report update, if desired, is a separate main-orchestrator action.

## Migration / Compatibility / Rollback

No migration is required. If the diff guard finds any out-of-scope change, the orchestrator should mark the run adoption-ineligible and handle rollback outside this delegated artifact.

## Observability

Expected observations for the orchestrator:

- the target filename matches `<ts>-<kind>-<slug>.md`;
- the target is a direct child of the issue `discussions/` directory;
- no existing discussion file is modified;
- no canonical, implementation, test, package/config, agent config, GitHub workflow, secret, delete, rename, symlink, nested directory, or second-file change is introduced by this smoke.

## Test Strategy

Use read-only inspection commands after the run:

- `git status --short`
- `git diff --name-status`
- content inspection of this file for provenance fields and required sections

Do not run a forbidden-path write probe.

## ADR Candidates

None for this smoke. The broader ADR candidate remains whether future canonical draft authoring should stay discussion-only with diff guards or require stricter isolation such as separate sessions, worktrees, or exact-target manifests.

## Risks

- `workspace-write` remains a soft workflow boundary, not a hard path allow-list.
- This note proves only that the role could create the requested file in this run; it does not prove both delegated roles or all future hosts behave identically.
- Existing dirty worktree state must be separated from this smoke's newly added file before adoption.

## Requirement Clarification Requests

none

## Integration Notes for Main Orchestrator

Suggested report integration, if the post-run diff guard passes:

- role: `spec-dock-system-architect`
- phase: `requirement/design`
- scope: `iss-00131`
- source artifacts read:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
- draft artifact path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00131-debug-codex-subagent-permission-profile-callability/discussions/20260527t001627z-disc-s04-system-architect-smoke.md`
- draft status: `produced`
- authority: `proposed`
- adoption_status: `unreviewed`
- reflected_to: `[]`
- intended_targets:
  - `spec-dock/active/issue/report.md`
- diff_guard_result: `pending`
- integration notes: main orchestrator should record the smoke result only after confirming this is the sole new file from this delegated run.
- rejected portions: none
- blockers: none
- canonical artifacts edited: `none`
- final authority claimed: `no`

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
