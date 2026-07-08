---
name: spec-dock-chatgpt-authoring
description: Shared evidence-lane skill for using ChatGPT / Oracle with SpecDock planning workflows, including sync/local-context modes, prompt packs, ZIP/tree outputs, validation, and adoption boundaries.
---

# Spec-Dock ChatGPT Authoring

Use this skill when ChatGPT / Oracle is requested for SpecDock planning authoring. It is a shared evidence lane for Initiative, Epic, and Issue planning workflows; it does not own canonical docs, reviewer gates, assurance state, execution readiness, or PR delivery.

This skill is an operational kernel. Keep canonical adoption in the relevant planning skill and keep global invariants in `spec-dock-hub`.

Contract anchor: ChatGPT / Oracle output is evidence-only until the main orchestrator adopts or rejects it in `report.md`, integrates accepted claims into canonical docs, and obtains the required fresh reviewer pass.

## Read First

- Current state: `./spec-dock/scripts/spec-dock active show`
- Relevant planning entrypoint:
  - Initiative decomposition: `spec-dock-initiative-planning`
  - Epic Issue slicing or draft handoff: `spec-dock-epic-planning`
  - Issue draft adoption or formalization: `spec-dock-issue-planning`
- Active or parent scope docs: `requirement.md`, `design.md`, `plan.md`, `report.md`, and scope-local `artifacts/`
- Authoring runtime help when available:
  - `./spec-dock/scripts/spec-dock authoring --help`
  - `./spec-dock/scripts/spec-dock authoring preflight --help`
  - `./spec-dock/scripts/spec-dock authoring pack --help`
  - `./spec-dock/scripts/spec-dock authoring validate --help`

## Evidence Modes

- `github-synced`: use when the branch and relevant commits are pushed and visible to GitHub-backed tools. Record the sync evidence used for the prompt pack.
- `local-context`: use when GitHub sync is intentionally unavailable or not required. Attach local docs, diffs, tree snapshots, or artifacts directly, label output as lower-confidence local-context evidence, and do not claim GitHub-synced coverage.

## Operating Spine

1. Resolve the active scope and target planning workflow.
   - If the requested scope is unclear, return to the relevant planning skill or `spec-dock-clarification`.
2. Choose `github-synced` or `local-context`.
   - Stop if synced evidence is required but missing or stale.
3. Prepare the prompt pack and output contract.
   - Include source constraints, target scope, expected artifact shape, and forbidden authority claims.
4. Invoke only an operator-configured backend or runtime path.
   - Do not require private local wrapper paths, account state, or browser profile details as SpecDock product dependencies.
5. Review returned ZIP/tree output, candidate reports, draft docs, or summaries as evidence.
   - Preserve raw output separately from adopted canonical text.
6. Validate candidates or draft-adoption input when runtime support exists.
   - Runtime validation can make evidence easier to review; it is not a reviewer pass.
7. Route back to the relevant planning skill for canonical adoption.
   - Initiative planning owns Initiative docs and Epic decomposition approval.
   - Epic planning owns Epic docs, Issue slicing, and human approval before Issue node creation.
   - Issue planning owns Issue `requirement.md`, `design.md`, `plan.md`, Evidence Adoption Ledger entries, fresh `spec-reviewer`, and execution handoff.

## Evidence Contract

- Record prompt source, evidence mode, invocation summary, output location, validation result, adoption/rejection decision, and reviewer gate status in the relevant `report.md`.
- Treat generated Requirement / Design / Plan text, Issue drafts, candidate lists, ZIPs, staged trees, review reports, and validation reports as source evidence.
- Adopt only specific claims that are source-grounded, locally checked, and integrated by the main orchestrator.
- Keep rejected, unsafe, stale, or unverifiable claims out of canonical docs and record why they were rejected when material.

## Forbidden Claims

ChatGPT authoring output, runtime validation, ZIP review, candidate validation, or staged draft artifacts must not claim:

- canonical adoption completed
- canonical docs were written or approved by ChatGPT / Oracle
- `.assurance.json` mutation
- `authorized_profile` decision
- reviewer pass, including fresh `spec-reviewer`, `code-reviewer`, or `qa-reviewer` pass
- execution-ready
- PR-ready
- merge-ready
- Issue finish
- Epic completion
- PR delivery

## Stop Conditions

- Active scope or target planning workflow is missing or contradictory.
- `github-synced` evidence is required but branch, commit, or GitHub visibility evidence is stale or missing.
- ChatGPT / Oracle output is unreviewed, unsafe, unverifiable, or not traceable to provided sources.
- Human approval before Epic or Issue node creation is missing.
- Issue docs are draft-only, template-only, or lack Evidence Adoption Ledger entries for draft adoption.
- Fresh `spec-reviewer` pass is missing after canonical doc changes.
- Any output claims canonical authority, assurance mutation, reviewer pass, readiness, finish/completion, mergeability, or PR delivery.
