---
name: spec-dock-codex-adapter
description: Thin Codex host adapter for spec-dock.
---

# Spec-dock Codex Adapter

- Use this as the Codex entrypoint for spec-dock work.
- Follow `spec-dock/docs/workflow_issue.md` and the fixed protocol from issue-00049.
- Route orchestration to the appropriate leaf skill; do not reimplement protocol or state logic here.
- Keep this adapter thin: wording only, no generated state, no pruning logic, no protocol interpretation.
