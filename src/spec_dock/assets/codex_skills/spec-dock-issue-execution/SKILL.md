---
name: spec-dock-issue-execution
description: Leaf skill for issue execution tasks in spec-dock.
---

# Spec-dock Issue Execution

- Use this skill for issue execution work.
- Typical fit: implement the active issue via TDD and update `report.md`.
- Start from `spec-dock/active/context-pack.md`, then follow the issue workflow.
- Treat `spec-dock/docs/workflow_issue.md` as the source of truth for issue governance.
- For shared phase authoring method, use:
  - `spec-dock/docs/phase_requirement.md`
  - `spec-dock/docs/phase_design.md`
  - `spec-dock/docs/phase_plan.md`
- Do not skip the docs impact resolution step or the final diff review quality gate.
- Issue execution must not stop with `spec-dock/active/issue/requirement.md`, `design.md`, `plan.md`, or `report.md` still left in template form.
- If `sync`, `validate`, or review is executed, record the result in `spec-dock/active/issue/report.md`; if any of them cannot be executed, record the reason or blocker in `report.md`.
- If those completion conditions are not satisfied, treat the issue as `blocked` or incomplete rather than complete.
- Primary workflow: `spec-dock/docs/workflow_issue.md`.
- `spec-dock/docs/reference_deps.md`
- `spec-dock/docs/reference_sync.md`
- `spec-dock/docs/reference_github.md`
- `spec-dock/docs/reference_naming.md`
