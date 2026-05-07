---
name: spec-dock-issue-execution
description: Leaf skill for issue execution tasks in spec-dock.
---

# Spec-dock Issue Execution

- Use this skill for issue execution work.
- Typical fit: implement the active issue through approved behavior-slice execution and update `report.md`.
- Start from `spec-dock/active/context-pack.md`, then follow the issue workflow.
- `spec-dock/docs/workflow_issue.md` is the source of truth for issue execution and completion.
- Normal lifecycle path: start with `./spec-dock/scripts/spec-dock issue start <target>` and finish with `./spec-dock/scripts/spec-dock issue finish`.
`issue finish` is lifecycle closure only: it closes or confirms the linked GitHub issue and clears active state, but it does not guarantee commit, push, PR, merge, validate, test, or review completion; delivery completion still requires separate evidence in tests, reviews, reports, and PR/merge workflow.
- Treat direct `./spec-dock/scripts/spec-dock active set ...` as a manual / recovery command, not the primary issue execution path.
- For shared phase authoring method, use:
  - `spec-dock/docs/phase_requirement.md`
  - `spec-dock/docs/phase_design.md`
  - `spec-dock/docs/phase_plan.md`
  - `spec-dock/docs/phase_plan_issue.md`
- Keep templates as scaffolds. Use the docs above for authoring guidance, including Issue dependency analysis, `Module Dependency Diagram`, Linux `tree` style file-change planning, and step ordering.
- Spec authoring mode: shape `requirement.md`, `design.md`, and `plan.md` for the project. Add, remove, merge, reorder, or rewrite template sections when it improves correctness, human understanding, or agent executability. Remove irrelevant placeholders.
- In spec authoring mode, use the optional diagram catalog in `spec-dock/docs/phase_design.md` as the authoritative source for diagram choices. Add catalog-listed or project-specific sections only when they clarify the issue.
- Execution mode: follow the approved issue docs. If the docs are missing required detail or contradict the implementation path, update/review the docs before implementation continues.
- Record delivery completion evidence in `spec-dock/active/issue/report.md` before running `./spec-dock/scripts/spec-dock issue finish`, because `issue finish` clears active state after lifecycle closure.
- Treat `Spec-Locked Closure Index` as the issue-wide coverage ledger, not as a single test-case catalog. Execute and close work through each step's `step closure contract`.
- Before implementation starts, stop if any required closure id in `plan.md` is not referenced from a behavior slice `closure ids` / `test ids` list, or if a required closure row has no step-local close condition, verification command, or evidence path.
- Do not change a required closure row, `locked expectation`, `required`, or meaning-bearing `spec link` during implementation without first updating the plan/design and getting re-review.
- Do not report complete unless every required closure id is closed in `spec-dock/active/issue/report.md` through `Step Contract Closure`, `Test Contract Closure`, and `Closure Coverage`.
- Record additions, removals, changed rows, intentionally unimplemented rows, and re-review decisions in `Closure Delta`.
- Do not skip the docs impact resolution step or the final diff review quality gate.
- Delivery completion must be confirmed before `issue finish` while the active issue is still set and confirmable, and `spec-dock/active/issue/requirement.md`, `design.md`, `plan.md`, and `report.md` contain issue-specific content rather than template, placeholder, or effectively blank content.
- `spec-dock/active/issue/report.md` must record command evidence for required `sync`, `validate`, and review steps, including whether each required step succeeded, passed, or reached approval.
- Do not run `issue finish` until every required step has been executed, every required `sync` / `validate` step has succeeded or passed, every required review step has reached approval or pass, and the delivery completion evidence is recorded in `spec-dock/active/issue/report.md`.
- After `issue finish`, do not require the active issue to remain set. Treat `issue finish` as lifecycle closure / GitHub close / active clear only.
- If any required step is skipped, or executed without a successful, pass, or approved outcome, classify the issue as `blocked` or `incomplete`, record the reason and next action in `spec-dock/active/issue/report.md`, and do not report the issue as complete.
- Treat the issue as `blocked` only when an external dependency, missing permission, unavailable service, or other environment condition prevents the next required action.
- When blocked, record the reason and next action in `spec-dock/active/issue/report.md`. Include blocker type and impact when applicable.
- Keep environment blockers separate from product gaps; missing implementation, missing docs updates, or missing evidence are incomplete unless an environment blocker prevents progress.
- When incomplete, record the reason and next action in `spec-dock/active/issue/report.md`.
- Do not report the issue as complete while it is incomplete or blocked.
- Primary workflow: `spec-dock/docs/workflow_issue.md`.
- `spec-dock/docs/reference_deps.md`
- `spec-dock/docs/reference_sync.md`
- `spec-dock/docs/reference_github.md`
- `spec-dock/docs/reference_naming.md`

## Runtime command reminders

- Use runtime command path only: `./spec-dock/scripts/spec-dock ...`
- Normal issue execution lifecycle:
  - `./spec-dock/scripts/spec-dock issue start <target>`
  - `./spec-dock/scripts/spec-dock issue finish`
- `issue start -f` / `--force` bypasses only the unfinished active issue guard for switching away from another unfinished issue branch. It does not bypass dependency readiness, target validation, or checkout safety.
- `issue start` from `main` / `master` / `develop` / `staging` or another non-issue branch is allowed; the unfinished guard is for another unfinished active issue branch only.
- Use direct `active set` only for manual / recovery work. It remains outside the unfinished issue guard.
- After `issue finish`, avoid running `sync --github` on the just-finished issue branch when you need active clear to remain clear. `sync --github` can restore active from branch-derived issue context; move to `main` or another non-issue branch before final sync, or skip post-finish sync.
- Dependency mutation is command-first:
  - `./spec-dock/scripts/spec-dock deps add --from <issue-id> --to <issue-id>`
  - `./spec-dock/scripts/spec-dock deps remove --from <issue-id> --to <issue-id>`
  - `./spec-dock/scripts/spec-dock deps check <target> --github`
- Keep report evidence aligned with workflow checks:
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync --github`
