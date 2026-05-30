---
kind: disc
title: remove local only node creation option surface handoff scratch
created_at: 2026-05-29T15:35:34Z
status: scratch
authority: proposed
---

# Handoff Scratch

## User intent

- Remove the non-GitHub / local-only creation option from SpecDock's node creation UX.
- Initiative, epic, and issue nodes should always have a GitHub issue as their backing entity.
- Do not allow creation of local-only initiative / epic / issue nodes.
- This request is for issue/worktree bootstrap only. Do not author requirement.md, design.md, or plan.md yet.

## Existing context observed during bootstrap

- Parent epic: `epic-00033` (`GitHub backed identity and ADR mirror workflow`).
- Existing issue `iss-00034` already implemented the main GitHub mandatory create contract.
- Current `new issue --help` still exposes `--no-github` as a rejected contract option:
  - `--create-github-issue | --github-issue GITHUB_ISSUE | --no-github`
  - help text says local-only issue creation is no longer supported.
- The follow-up likely needs to remove the local-only option surface itself, not merely keep it as a rejected path.

## Initial investigation targets

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
- `tests/cli_runtime/test_new.py`
- `tests/cli_runtime/test_runtime_new_s08.py`
- Provider docs and dogfooding docs that still mention `--no-github` or local-only node creation.

## Suggested next steps

- Confirm whether `--no-github` is still exposed for `new initiative`, `new epic`, and `new issue`.
- Decide whether removal means parser-level unknown option errors, docs removal, and test updates, while preserving mandatory GitHub-backed behavior.
- Keep existing GitHub mandatory validation from `iss-00034`; avoid reworking repo-scope validation unless a direct dependency appears.
- After planning is requested, write requirement/design/plan from this scratch and fresh code/docs inspection.
