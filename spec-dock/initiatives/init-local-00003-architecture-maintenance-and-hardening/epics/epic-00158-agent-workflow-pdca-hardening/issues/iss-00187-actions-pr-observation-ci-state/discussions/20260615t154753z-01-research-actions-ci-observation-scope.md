---
artifact_kind: research
id: 20260615t154753z-research-actions-ci-observation-scope
issue: iss-00187
title: Actions CI Observation Scope Research
created_at: 2026-06-15T15:47:53Z
status: adopted
adoption_status: adopted
reflected_to:
  - requirement.md
  - report.md
---

# Actions CI Observation Scope Research

## Sources Read

- GitHub issue #187, `Use Actions endpoint for PR observation CI state`.
- Active issue docs:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
- Parent epic docs:
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
- Clarification workflow:
  - `.agents/skills/spec-dock-clarification/SKILL.md`
  - `spec-dock/docs/workflow_clarification.md`
- Current PR observation surface:
  - `.agents/skills/github-pr-observation/SKILL.md`
  - `.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`
  - `.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
  - `.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`
- Existing regression tests:
  - `tests/unit/infra/test_init_update.py`
  - `tests/cli_runtime/test_runtime_doctor_s04.py`
- GitHub official REST docs checked live on 2026-06-15:
  - Workflow runs: `GET /repos/{owner}/{repo}/actions/runs`
  - Workflow jobs: `GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs`
  - Check runs: `GET /repos/{owner}/{repo}/commits/{ref}/check-runs`
  - Combined commit status: `GET /repos/{owner}/{repo}/commits/{ref}/status`

## Provisional Understanding

- The issue is not asking for a new PR observation feature category. It asks to preserve the existing PR observation purpose while replacing the CI observation permission dependency that currently blocks fine-grained PAT users.
- Current CI collection primarily uses:
  - check runs for a commit SHA: `repos/{repo}/commits/{sha}/check-runs`
  - combined commit status: `repos/{repo}/commits/{sha}/status`
  - PR rollup through `gh pr view --json mergeStateStatus,statusCheckRollup`
  - Actions jobs only after a failed check run reveals `workflow_run.id`
- Current permission handling treats a permission denial on check runs as `github_token_permission_denied`, `ci.status=unknown`, and `recommended_next_action=fix_github_token_permissions`.
- GitHub docs confirm that:
  - workflow runs list supports fine-grained PATs with `Actions` repository permission read.
  - workflow jobs list supports fine-grained PATs with `Actions` repository permission read.
  - check runs list requires `Checks` repository permission read.
  - combined commit status requires `Commit statuses` repository permission read.
- Therefore, an Actions-first collector can reduce the normal required permission surface for GitHub Actions CI from `Checks` read to `Actions` read.

## Current Implementation Shape

- `fetch_pr_observation_snapshot.sh` owns top-level snapshot classification and calls the CI collector plus review collector.
- `fetch_pr_checks_snapshot.sh` is the CI collector despite the name. It currently emits:
  - `ci.status`
  - `ci.progress_status`
  - `ci.check_runs`
  - `ci.commit_statuses`
  - `ci.checks`
  - `ci.statuses`
  - `ci.failures`
  - `ci.required_check_state`
  - `limitations`
  - `fingerprint`
- `wait_pr_observation.sh` relies on `ci.status`, top-level `limitations`, and existing limitation codes. It does not need to know every collection detail if the collector preserves status taxonomy and limitation semantics.
- Existing tests already execute the provider-side shipped scripts with fake `gh`; this is the right regression lane for the issue.

## Candidate Requirement Boundary

- Must:
  - Use Actions read endpoints as the primary GitHub Actions CI observation surface for head SHA workflow runs and jobs.
  - Preserve the public JSON contract that downstream `github-pr-merge-preparer` and callers use: `ci.status`, `normalized_status`, `recommended_next_action`, `limitations`, failures, and wait semantics.
  - Preserve status taxonomy: `passed`, `failed`, `running`, `pending`, `none`, `unknown`.
  - Preserve false-pass safety: unknown or unsupported CI surfaces must not become `passed` silently.
  - Keep review lifecycle observation out of scope.
  - Keep PR merge automation out of scope.
  - Keep arbitrary caller-provided GitHub API endpoints out of scope.
- Should:
  - Continue reporting actionable failure details from Actions jobs when available.
  - Mention any observation surface limitation in final JSON when Actions cannot prove all relevant CI providers.
  - Update `github-pr-observation/SKILL.md` permission wording away from `fix_github_token_permissions` for unavailable Checks permission as the normal remedy.
- Could:
  - Keep commit statuses or PR rollup as optional supplemental signals if available without making them mandatory for GitHub Actions-centered repos.

## Main Gap

The key requirement ambiguity is whether an Actions-only green result is allowed to produce `ci.status="passed"` when check-run/status-rollup data is unavailable or intentionally non-authoritative.

This matters because:

- If Actions-only green may pass:
  - Fine-grained PAT users can proceed with only `Actions` read for GitHub Actions-centered repos.
  - External check providers and required status contexts may be represented as a limitation rather than a blocker.
- If Actions-only green may not pass:
  - False pass risk is lower for mixed-provider repos.
  - The issue goal is weakened because the workflow may still stop when Checks/status rollup is inaccessible.

## Recommended Pressure-Test Question

Ask the user to choose the product contract for Actions-only green observations:

- Option A: GitHub Actions-centered default. If all workflow runs for the PR head SHA are terminal-success/skipped/neutral and no Actions failures/running/pending are observed, allow `ci.status="passed"` even when Checks/status rollup cannot be read. Include an explicit limitation that only GitHub Actions CI was observed and external providers were not fully proven.
- Option B: Strict full-rollup default. Actions green is not enough to pass unless check/status rollup or commit statuses are also readable. If they are unavailable, return `unknown` with limitation.

Recommendation: Option A, because it directly satisfies #187 while preserving false-pass safety through an explicit limitation for unsupported surfaces.

## Handoff Target

- After the user answers, adopt the answer into:
  - `requirement.md` scope, non-goals, acceptance criteria, and edge cases.
  - `design.md` collector contract and status taxonomy.
  - `plan.md` step ordering and test obligations.
  - `report.md` Evidence Adoption Ledger and Spec Authoring Gate.
