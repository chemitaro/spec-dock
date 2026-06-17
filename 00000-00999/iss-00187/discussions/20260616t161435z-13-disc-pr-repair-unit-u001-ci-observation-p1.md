---
種別: disc
ID: "20260616t161435z-13-disc-pr-repair-unit-u001-ci-observation-p1"
タイトル: "U001 CI observation P1 repair"
状態: "implemented"
作成者: "orchestrator"
最終更新: "2026-06-16"
親: ["iss-00187-actions-pr-observation-ci-state"]
関連: ["20260616t161435z-12-disc-pr-repair-batch-after-s399-observation", "https://github.com/chemitaro/spec-dock/pull/190"]
authority: "proposed"
derived_from: ["PR review comment 3418873984", "PR review comment 3418873991", "/private/tmp/spec-dock-pr190-observation-71120a7b/result.json"]
reflected_to: []
---

# U001 CI observation P1 repair

## Unit Metadata

- source_batch: `20260616t161435z-12-disc-pr-repair-batch-after-s399-observation.md`
- unit_id: U001
- covered_ids: INV-001, INV-002
- source_links:
  - PR review comment `3418873984`, thread `PRRT_kwDOQ99OK86Jzt03`
  - PR review comment `3418873991`, thread `PRRT_kwDOQ99OK86Jzt09`
  - Observation result `/private/tmp/spec-dock-pr190-observation-71120a7b/result.json`
- failure_class: `review_feedback:actions-job-expansion-bound`, `review_feedback:external-green-permission-limitation`
- risk_class: blocking
- disposition: fix-now

## Validity Analysis

Both P1 findings are valid and apply to latest head `71120a7bccf638ecd957fa27a2309fb77d1f8c5b`.

INV-001 is valid because the collector currently calls `repos/{repo}/actions/runs/{run_id}/jobs` for every non-terminal run, while run-level status already classifies CI as running/pending. This can consume wait budget or rate limits when a PR has many queued or running workflow runs.

INV-002 is valid because the `elif limitations and any(is_blocking_limitation(item) for item in limitations)` branch can keep CI `unknown` before the external-green fallback gets a chance to pass a no-Actions, green legacy-status repository.

## Need-To-Fix Decision

Fix both P1 findings now. They are part of PR observation CI state correctness and directly affect whether PR #190 can be merge-prepared.

## Root Cause

- INV-001: job expansion has a cap for terminal green runs but no separate cap/defer rule for non-terminal runs.
- INV-002: external-green fallback is ordered after generic blocking-limitation handling.

## Options Considered

- Cap all job expansion globally: rejected because failed-run diagnostics must stay complete enough to explain failures.
- Skip all non-terminal jobs: acceptable if run-level status is decisive, but a small cap gives better progress diagnostics.
- Add a separate non-terminal expansion cap and preserve failed-run expansion: recommended.
- Move external-green fallback before generic blocking limitations: recommended, with strict predicates so failed/pending/unknown external evidence does not pass.
- Downgrade every Checks-read permission denial: rejected because permission denial can still be blocking when no decisive CI evidence exists.

## Recommended Design

1. Add a small non-terminal job expansion cap for running/pending workflow runs. Run-level evidence remains the source for `running` / `pending`; job detail is bounded diagnostic evidence only.
2. Preserve failed-run job expansion and existing jobs-unavailable blocking behavior for failed runs.
3. Add a strict external-green/no-Actions predicate before generic blocking limitation handling:
   - no Actions runs are decisive,
   - commit statuses exist and are all success,
   - no failed/pending/other check or status evidence,
   - required check state is available and merge state is clean,
   - permission limitation is limited to Checks/check-runs coverage and is retained as informational coverage limitation.
4. Sync the dogfooding mirror copy of `pr_observation_checks.py` after provider changes.

## Implementation Plan

1. Add focused tests in `tests/unit/infra/test_init_update.py`:
   - A many-running-runs fixture proves non-terminal job endpoint calls are bounded and CI remains `running`.
   - A no-Actions + green legacy commit-status + check-runs permission-denied fixture proves CI becomes `passed` with non-blocking coverage limitation.
   - Negative coverage proves failed/pending/non-green external status does not pass through the new fallback.
2. Update provider file `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`.
3. Sync `.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py` from the provider file.
4. Update `report.md` with Red/Green evidence, repair batch status, reviewer state, and residual risk.
5. Run focused selectors first, then the established PR observation / issue_187 lane, `git diff --check`, provider/mirror `cmp`, and `./spec-dock/scripts/spec-dock validate`.

## Validation Plan

- `uv run pytest tests/unit/infra/test_init_update.py -k "non_terminal or external_green or issue_187"`
- `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation or issue_187"`
- `git diff --check`
- `cmp -s src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py .agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
- `./spec-dock/scripts/spec-dock validate`

## Implementation Result

Implemented in the bounded U001 repair scope.

- Added focused regressions:
  - `test_issue_187_u001_multiple_running_runs_do_not_expand_every_job`
  - `test_issue_187_u001_zero_actions_green_legacy_status_passes_with_checks_permission_denied`
  - `test_issue_187_u001_non_terminal_job_failures_are_bounded_by_attempts`
  - `test_issue_187_u001_zero_actions_failed_legacy_status_keeps_checks_permission_blocking`
- Observed Red before implementation:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "u001"` -> `2 failed, 408 deselected`
  - The non-terminal fixture called all three `actions/runs/{id}/jobs` endpoints.
  - The no-Actions + green legacy status + check-runs permission-denied fixture returned `ci.status="unknown"`.
- P2 follow-up evidence:
  - P2-1 Red: after adding `test_issue_187_u001_non_terminal_job_failures_are_bounded_by_attempts`, `uv run pytest tests/unit/infra/test_init_update.py -k "u001"` -> `1 failed, 3 passed, 408 deselected`; failed non-terminal jobs API attempts kept expanding later non-terminal runs because the cap was success-count based.
  - P2-2 coverage-only negative: `test_issue_187_u001_zero_actions_failed_legacy_status_keeps_checks_permission_blocking` proved the same check-runs permission-denied path remains non-pass for failed legacy status and keeps the permission limitation blocking.
- Provider implementation:
  - Added an internal non-terminal Actions job expansion cap of `1`.
  - Changed non-terminal expansion bounding from successful job-collection count to non-terminal attempt count, so a permission-denied or malformed first attempt still stops later non-terminal job-detail expansion.
  - Preserved run-level `running` / `pending` as decisive non-terminal CI evidence when skipped job details are diagnostic-only.
  - Preserved failed-run diagnostics and existing terminal-green bounded behavior.
  - Added a strict no-Actions + green legacy commit-status + clean merge-state fallback that downgrades only `check_runs_read` permission denial to informational coverage evidence.
  - Kept failed/pending/non-green external status evidence non-pass through existing negative regressions.
- Dogfooding mirror:
  - Synced `.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py` from provider and verified byte equality.

Changed files:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
- `.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
- `tests/unit/infra/test_init_update.py`
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00187-actions-pr-observation-ci-state/report.md`
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00187-actions-pr-observation-ci-state/discussions/20260616t161435z-12-disc-pr-repair-batch-after-s399-observation.md`
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00187-actions-pr-observation-ci-state/discussions/20260616t161435z-13-disc-pr-repair-unit-u001-ci-observation-p1.md`

Green verification:

- `uv run pytest tests/unit/infra/test_init_update.py -k "u001"` -> `4 passed, 408 deselected`
- `uv run pytest tests/unit/infra/test_init_update.py -k "u001 or s202_zero_actions_runs_external_non_green or s203_failed_actions"` -> `7 passed, 405 deselected`
- `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation or issue_187"` -> `127 passed, 285 deselected`
- `git diff --check` -> pass
- `cmp -s src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py .agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py` -> pass
- `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=96`

## Commit Evidence

Not committed. Per instruction, no commit and no push were performed.

## Re-observation Result

Pending external PR re-observation. No commit/push was performed in this DevCoder unit, so latest-head PR #190 observation was intentionally not rerun.

## Residual Risk / Follow-up

Residual risk is limited to external PR re-observation after the orchestrator commits and pushes this repair. If Codex does not post a current completion signal after the next push, `review_completion_unknown` must remain a human gate unless a reliable explicit completion signal appears.

No material implementation decisions beyond the approved repair unit.
