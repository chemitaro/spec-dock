---
artifact_kind: interview
id: 20260615t154753z-interview-actions-only-pass-contract
issue: iss-00187
title: Actions Only Pass Contract
created_at: 2026-06-15T15:47:53Z
status: answered
adoption_status: adopted
reflected_to:
  - requirement.md
  - report.md
---

# Actions Only Pass Contract

## Context

GitHub issue #187 asks PR observation to stop requiring an unavailable `Checks` read permission as the normal solution for fine-grained PAT users, and instead use the `Actions` read permission surface for CI state.

Local investigation found that the current collector uses check runs, commit statuses, PR status rollup, and Actions jobs. GitHub official docs confirm that workflow runs/jobs are available with `Actions` read, while check runs require `Checks` read and commit status requires `Commit statuses` read.

## Question

When all GitHub Actions workflow runs for the PR head SHA are terminal-success/skipped/neutral, but Checks/status rollup or external check-provider data is unavailable, should PR observation allow `ci.status="passed"`?

## Options

### Option A: GitHub Actions-centered default

Allow `ci.status="passed"` from Actions-only green evidence for GitHub Actions-centered repositories.

Conditions:

- All observed workflow runs for the head SHA are terminal-success/skipped/neutral.
- No observed workflow run/job is failed, running, pending, queued, requested, waiting, cancelled, timed out, action_required, or stale.
- The final JSON includes an explicit limitation when external providers or full rollup were not proven.
- Unsupported or ambiguous data still returns `unknown`, not `passed`.

Impact:

- Satisfies #187 for normal fine-grained PAT operation with `Actions` read.
- Preserves a visible limitation for non-GitHub-Actions providers.

### Option B: Strict full-rollup default

Do not allow Actions-only green evidence to produce `ci.status="passed"` unless check/status rollup or commit statuses are also readable.

Impact:

- Minimizes false-pass risk for mixed-provider repositories.
- May continue blocking fine-grained PAT users in the exact situation #187 is meant to fix.

## Recommendation

Option A.

Rationale:

- #187 explicitly frames GitHub Actions-centered observation as the practical replacement surface.
- False-pass safety can be preserved by making unobserved external provider coverage explicit in `limitations` and by keeping unsupported/ambiguous states as `unknown`.
- The downstream contract can continue to use `ci.status` and `recommended_next_action` while seeing the limitation.

## User Answer

許可する。

Adopted interpretation:

- Use Option A as the issue requirement contract.
- GitHub Actions-only green evidence may produce `ci.status="passed"` when all observed workflow runs for the PR head SHA are terminal-success/skipped/neutral.
- The result must still expose a limitation when full check/status rollup or external check-provider coverage is not proven.
- Unsupported, ambiguous, failed, running, pending, queued, requested, waiting, cancelled, timed out, action_required, or stale observations must not be promoted to `passed`.

## Adoption Target

- `requirement.md`: scope, acceptance criteria, edge cases.
- `design.md`: CI collector status contract and limitation semantics.
- `plan.md`: test obligations for Actions-only pass, Actions failure, Actions pending/running, and unsupported external provider limitation.
- `report.md`: Evidence Adoption Ledger and Spec Authoring Gate.
