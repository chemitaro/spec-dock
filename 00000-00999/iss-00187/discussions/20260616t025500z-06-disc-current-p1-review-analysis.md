---
artifact_kind: disc
id: 20260616t025500z-disc-current-p1-review-analysis
issue: iss-00187
title: Current PR 190 P1 Review Analysis
created_at: 2026-06-16T02:55:00Z
status: adopted
adoption_status: adopted
reflected_to:
  - design.md
  - plan.md
  - report.md
---

# Current PR 190 P1 Review Analysis

## Purpose

This artifact records the two current P1 review findings on PR #190 and analyzes why they matter before implementation starts.

The goal is not to decide the exact patch yet. The goal is to make the review feedback durable, source-grounded, and actionable for the next implementation step.

## Current Review Summary

Latest PR #190 head:

- `1bb19acdf512d71f45a39ce7a3790862b36b0295`

Latest Codex review:

- submitted at: `2026-06-16T02:35:08Z`
- reviewed commit: `1bb19acdf512d71f45a39ce7a3790862b36b0295`
- state: `COMMENTED`
- selected unresolved count in live snapshot: `2`

Both selected unresolved review threads are P1 and point to:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`

The dogfooding mirror under `.agents/skills/github-pr-observation/...` will also need to stay in sync after provider-side fixes.

## Finding 1: Bound Per-Run Job Collection Inside Wait Snapshots

Review thread:

- id: `PRRT_kwDOQ99OK86JwtEM`
- comment id: `3417784129`
- path: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`
- line: `590`
- severity: P1
- title: `Bound per-run job collection inside wait snapshots`

### Review Claim

When the PR has Actions workflow runs, the script performs one extra jobs API call per workflow run before emitting the snapshot JSON.

This means one snapshot can consume too much of the caller's bounded `--timeout-seconds` budget. Short waits may return `timeout` or `unknown` before reaching stable CI / review states.

### Local Code Finding

The current collector loops over every workflow run and calls:

```python
jobs_payload, job_limitation = gh_api(f"repos/{repo}/actions/runs/{run_id}/jobs")
```

inside the main run loop.

That means the total collector cost is:

```text
one workflow-runs API call
+ one jobs API call per observed workflow run
+ check-runs/status/status-rollup reads
```

The call count can grow with the number of workflow runs for the same head. This is especially relevant inside `wait_pr_observation.sh`, because each poll invokes the snapshot collector.

### Verification Performed

The local command:

```text
uv run pytest tests/unit/infra/test_init_update.py -q
```

completed with:

```text
388 passed in 213.21s
```

The exact review claim that seven tests fail did not reproduce on the latest local head. However, the structural issue remains credible because the collector still performs unbounded per-run job expansion relative to the wait budget.

### Impact

This can cause:

- wait loops to spend most of their budget collecting details rather than observing stability,
- delayed or missing review-state observation,
- `timeout` / `unknown` outputs even when high-level CI and review state would otherwise be available,
- increased rate-limit pressure.

### Desired Fix Shape

The fix should make job-detail expansion bounded or staged.

Candidate approaches:

1. Fetch job details only for failed, running, pending, or unknown runs.
2. Cap the number of run job lists fetched per snapshot.
3. Add a fast summary mode for wait snapshots and a detailed mode for final diagnostic snapshots.
4. Use workflow run conclusions as the decisive green path and defer green job expansion unless explicitly requested.

The safest first fix is likely:

- keep job details for failed/non-terminal/unknown evidence,
- avoid full per-run job expansion for all-green runs during wait polling,
- preserve enough sanitized evidence in the final payload to explain failures.

## Finding 2: Preserve External Green Checks When Actions Has No Runs

Review thread:

- id: `PRRT_kwDOQ99OK86JwtEO`
- comment id: `3417784133`
- path: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`
- line: `1068`
- severity: P1
- title: `Preserve external green checks when Actions has no runs`

### Review Claim

When a repository uses non-Actions CI, the Actions workflow-runs API can legitimately return zero runs while check-runs or commit statuses are green.

The current branch classifies zero Actions runs as `ci.status="none"` before considering successful check/status evidence, so external-CI-only repositories never reach `passed`.

### Local Code Finding

The current status ladder includes:

```python
elif actions_zero_runs:
    ci_status = "none"
    if check_counts["total"] == 0 and status_counts["total"] == 0:
        limitations.append(...)
elif actions_decisive_green and not (...):
    ci_status = "passed"
```

This means `actions_zero_runs` wins before any external green-only pass branch can run.

The branch only adds a limitation when both `check_counts["total"] == 0` and `status_counts["total"] == 0`; it does not pass when check/status evidence is present and green.

### Impact

This is a direct false-negative for repositories that use:

- external GitHub Checks providers,
- commit statuses,
- non-Actions CI systems,
- hybrid setups where Actions is absent but status rollup is valid.

It can make the observer report no CI / human gate / wait behavior even though CI is actually complete.

### Desired Fix Shape

The status ladder should treat zero Actions runs as "no Actions evidence", not as globally no CI.

Candidate rule:

- If Actions is available and returns zero runs:
  - if check-runs/statuses/required rollup show failure or pending, use those states.
  - if readable external check/status evidence is all green and no required checks are missing/pending, return `passed`.
  - if no external evidence exists, keep `none` with the existing zero-check limitation.

This preserves the original safety constraint:

> zero Actions runs alone must not pass.

But it avoids the new unsafe assumption:

> zero Actions runs means no CI exists.

## Relationship Between the Two P1 Findings

The two findings point in the same architectural direction:

- The Actions collector was promoted to primary CI evidence.
- The implementation then became too Actions-centric in both performance and status taxonomy.

Finding 1 says the collector gathers too much Actions detail during bounded polling.

Finding 2 says the status ladder treats absence of Actions runs as absence of CI, even when external CI evidence exists.

Together, they suggest the next design should split:

- high-level CI state classification,
- optional diagnostic detail collection,
- external check/status fallback,
- wait-loop budget control.

## Proposed Test Cards

### tc-review-p1-001: zero Actions runs with green external checks passes

Input:

- Actions workflow-runs API returns `total_count=0`, `workflow_runs=[]`.
- check-runs or commit statuses for the expected head are green.
- head matches.

Expected:

- `ci.status="passed"`.
- `ci.actions.workflow_runs.total=0`.
- no `zero_checks_s03_non_success` limitation unless external evidence is also absent.

### tc-review-p1-002: zero Actions runs with no external evidence remains non-pass

Input:

- Actions workflow-runs API returns zero runs.
- check-runs total is zero.
- statuses total is zero.

Expected:

- `ci.status="none"` or another explicit non-pass state.
- `zero_checks_s03_non_success` remains blocking.

### tc-review-p1-003: wait snapshot does not expand every green run job list

Input:

- multiple successful Actions workflow runs.
- wait-polling mode or default bounded wait context.

Expected:

- the collector avoids unbounded per-run job calls for all-green runs, or enforces a documented cap.
- high-level `ci.status` remains `passed`.

### tc-review-p1-004: failed Actions still includes useful job/step diagnostics

Input:

- failed workflow run and failed job details are available.

Expected:

- `ci.status="failed"`.
- sanitized failure evidence remains available.
- bounding green job expansion does not remove failed job diagnostics.

## Open Questions

- Should the collector expose an explicit `--mode wait|diagnostic` flag, or should the default behavior be bounded for all callers?
- How many Actions runs should be expanded per snapshot if a cap is used?
- Is workflow run conclusion alone sufficient for green pass when Actions is decisive, or do required job-level checks need to be observed for all green runs?
- Should external green checks pass when Actions returns zero runs but status rollup access is partial?

## Recommended Next Work

1. Add implementation-plan steps for both P1 review threads.
2. Fix the zero-Actions / external-green status ladder first because it is a direct logical defect.
3. Refactor or bound Actions job expansion before adding more status logic.
4. Keep provider source as authority and mirror `.agents/...` after provider changes.
5. Re-run current PR observation after the fix to confirm selected unresolved count changes.
