---
name: spec-dock-copilot-adapter
description: Thin Copilot host adapter for spec-dock.
---

# Spec-dock Copilot Adapter

- Use this as the Copilot entrypoint for spec-dock work.
- Follow `spec-dock/docs/workflow_issue.md` and the fixed protocol from issue-00049.
- Route orchestration to the appropriate leaf skill; do not reimplement protocol or state logic here.
- Keep this adapter thin: wording only, no generated state, no pruning logic, no protocol interpretation.
- For issue work, do not treat the task as complete until the active issue is set and `spec-dock/active/issue/requirement.md`, `design.md`, `plan.md`, and `report.md` are filled with real issue data.
- If any of those active issue docs remain templated or effectively blank, report the work as incomplete or blocked instead of complete.
