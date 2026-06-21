---
created_by_role: system-architect
scope_id: iss-00222
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/.agent/active.json
  - spec-dock/active/initiative/requirement.md
  - spec-dock/active/initiative/design.md
  - spec-dock/active/initiative/plan.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/discussions/20260620t143349z-adr-forbid-checks-api-in-pr-observation.md
  - spec-dock/active/issue/discussions/20260620t144016z-interview-checks-named-compatibility-boundary.md
  - spec-dock/active/issue/discussions/20260620t141316z-research-actions-only-pr-observation-viability-research.md
  - spec-dock/active/issue/discussions/20260620t141320z-disc-actions-only-collector-design.md
  - spec-dock/active/issue/discussions/20260620t141317z-disc-observation-semantics-and-losses.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/workflow_clarification.md
  - spec-dock/docs/phase_requirement.md
  - spec-dock/docs/phase_design.md
  - spec-dock/docs/reference_sync.md
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_capability_cli.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py
  - tests/unit/infra/test_init_update.py
  - tests/cli_runtime/test_runtime_doctor_s04.py
intended_targets:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: passed
---

# Actions Only PR Observation Design Draft

This is delegated design evidence for `iss-00222`. It is not canonical authority. It does not claim reviewer pass, phase promotion, implementation readiness, or final ownership.

Source requirement revision used: `active:iss-00222` as read from the working tree on 2026-06-20, with repository `HEAD` `c0b339c370ac4ec82cb5389ab2c38009eec883e5`. The working tree already had pre-existing modifications to the issue `requirement.md` and `report.md`; this draft treats the current file content as the source requirement evidence and does not edit those canonical files.

## 1. Requirement Coverage

- AC-001 maps to removing all CI-decision reads of `/check-runs`, `/commits/{sha}/status`, `statusCheckRollup`, and `gh pr checks`-equivalent rollups from PR observation scripts. Tests should fail on any forbidden call, not on the word `checks`.
- AC-002 and AC-003 map to Actions workflow runs/jobs as the only CI decision source. Run-level `status`/`conclusion` is the primary state, and jobs add failure detail when available.
- AC-004 maps to zero Actions runs never becoming `passed`, even if legacy check-runs or commit statuses would have been green.
- AC-005 maps to preserving review/comment/thread observation through the existing S04 collector path. GraphQL `reviewThreads` remains allowed because it is review evidence, not CI status rollup.
- AC-006 maps to doctor/capability probes no longer treating Checks/statuses/status rollup permissions as core PR observation repair targets.
- AC-007 maps to compatibility wording and tests that allow historical `checks` names while forbidding the API surfaces.

## 2. Existing Context Findings

- `pr_observation_checks.py` already collects Actions runs by `GET /repos/{repo}/actions/runs?head_sha=<sha>` and jobs by `GET /repos/{repo}/actions/runs/{run_id}/jobs`.
- The same file then reads forbidden supplemental sources: `gh pr view --json mergeStateStatus,statusCheckRollup`, `/check-runs`, and `/commits/{sha}/status`.
- The current CI status algorithm can let check-runs, commit statuses, and status rollup affect `failed`, `running`, `pending`, `unknown`, and `passed`.
- `ci_coverage_limited_to_github_actions` currently treats missing supplemental Checks/statuses/rollup coverage as a limitation. Under the accepted ADR, not reading those sources is normal.
- `pr_observation_snapshot.py` treats `fetch_pr_checks_snapshot.sh` as the CI collector subprocess and combines its fingerprint with review decision fingerprint. This entrypoint name can remain as a compatibility name.
- `pr_observation_wait.py` computes progress from `ci.check_runs`, so progress and semantic fingerprint fallback need an Actions-based source.
- `pr_review_snapshot.py` emits review `statuses` inside the review payload. Those are review-state labels and must not be confused with legacy commit statuses.
- `github_capability_cli.py` currently probes `check_runs_read`, `commit_statuses_read`, and `status_check_rollup_read` as core capability diagnostics. `actions_read` is extended today, but should become the relevant CI capability for PR observation.
- `doctor.py` fallback diagnostics use `check_runs_read` for skipped/unavailable GitHub target states; these labels should move to a neutral PR observation capability such as `pull_request_read` or `actions_read`.
- Current tests in `tests/unit/infra/test_init_update.py` have many fake `gh` fixtures that expect forbidden calls. New tests should invert these fixtures so forbidden calls exit non-zero and fail the test.
- Current doctor tests in `tests/cli_runtime/test_runtime_doctor_s04.py` assert check-runs/status rollup diagnostics. They should be migrated to Actions and review/comment read capability expectations.

## 3. Design Decisions

- Use GitHub Actions workflow runs/jobs as the only PR observation CI source of truth.
- Remove forbidden API calls from CI collection, fallback, limitations, progress, and fingerprint sources.
- Preserve compatibility names such as `fetch_pr_checks_snapshot.sh` when useful, but make the payload explicitly Actions-only.
- Keep review/comment/thread observation independent from CI observation. Review GraphQL is allowed only for review threads and must not request `statusCheckRollup`.
- Treat zero Actions runs, Actions API unavailable, and jobs unavailable as non-pass states. They may be `none`, `unknown`, or a human gate depending on the existing status vocabulary, but not `passed`.
- Treat external/non-Actions checks as intentionally unobserved, not as permission failure.
- Make doctor/capability guidance ask for `Actions: read` and PR/comment read capability, not Checks or Commit statuses permission.

## 4. Alternatives Considered

- Keep commit statuses as fallback: rejected because the user clarified legacy commit statuses are also forbidden.
- Keep status rollup only for merge blocking state: rejected because it reintroduces the exact forbidden PR checks aggregation surface.
- Rename every public surface containing `checks`: rejected because the user clarified this is not a word ban. Compatibility names may remain if the implementation does not call forbidden APIs.
- Delete old JSON compatibility fields immediately: possible but high blast radius. Prefer explicit empty/deprecated compatibility fields where downstream tests or scripts already rely on shape.

## 5. Boundary / Contract Model

Allowed CI sources:

- `GET /repos/{owner}/{repo}/actions/runs?head_sha=<head_sha>`
- `GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs`

Forbidden CI sources:

- `GET /repos/{owner}/{repo}/commits/{ref}/check-runs`
- `GET /repos/{owner}/{repo}/commits/{sha}/status`
- `gh pr view --json statusCheckRollup`
- `gh pr checks` or equivalent rollup
- Any branch-protection/mergeability inference that effectively restores status rollup as CI truth

Unaffected observation boundary:

- PR metadata: `headRefOid`, `url`, `state`, `isDraft`, `number`
- Review evidence: issue comments, PR reviews, PR review comments, review requests, GraphQL review threads
- Existing write path for explicitly triggering Codex review comments remains outside this issue's CI source change.

Payload compatibility recommendation:

- Keep top-level `script: "fetch_pr_checks_snapshot.sh"` if this is the compatibility entrypoint.
- Add or preserve an explicit marker such as `ci.source_policy: "github_actions_only"` and `ci.forbidden_sources: [...]`.
- Keep `ci.check_runs`, `ci.commit_statuses`, `ci.checks`, `ci.statuses`, and `ci.required_check_state` only as empty/deprecated compatibility fields if removing them is broader than this issue. If kept, set clear metadata that they are not collected and not decision inputs.
- Do not leave empty compatibility fields in the fingerprint as if they were observed source data.

## 6. Dependency Analysis

- `pr_observation_checks.py` is the primary implementation boundary. It owns GitHub CI collection, CI classification, limitations, failure details, and CI fingerprint.
- `pr_observation_snapshot.py` depends on the CI collector payload. It should not need large structural changes if the CI collector keeps compatible top-level fields.
- `pr_observation_wait.py` depends on CI payload shape for progress and semantic fingerprint. It should consume `ci.actions.workflow_runs.counts` and `ci.actions.jobs_summary.counts`, not `ci.check_runs`.
- `pr_review_snapshot.py` is an unaffected sibling collector. Its review `statuses` vocabulary should remain intact.
- `github_capability_cli.py` and `doctor.py` are separate runtime surfaces shipped under provider-side `src/spec_dock/assets/spec_dock/...`; they need capability vocabulary migration in the same issue or a clearly planned docs-impact step.
- Tests in `tests/unit/infra/test_init_update.py` cover shipped script behavior and should be the main regression surface for forbidden calls.
- Tests in `tests/cli_runtime/test_runtime_doctor_s04.py` cover runtime doctor capability output and should be updated with the capability migration.

## 7. Source of Record

- Architecture decision source: accepted ADR `20260620t143349z-adr-forbid-checks-api-in-pr-observation.md`.
- Requirement source: `spec-dock/active/issue/requirement.md`, current working-tree revision read for this draft.
- Compatibility boundary source: answered interview `20260620t144016z-interview-checks-named-compatibility-boundary.md`.
- Implementation source of truth: provider-side files under `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/` and `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/...`.
- Dogfooding mirror: `.agents/` and `spec-dock/` are validation targets only; do not make implementation edits there first.
- This draft is evidence only and should be integrated by the main orchestrator into canonical `design.md` and `report.md` if adopted.

## 8. Data Flow / Domain Model / Interface Contract

Recommended CI collector flow:

```text
PR metadata head SHA
  -> Actions runs by head_sha
  -> bounded jobs fetch per relevant run
  -> Actions-only run/job classification
  -> CI payload + limitations + fingerprint
  -> snapshot classifier
  -> wait progress / stability
```

State classification recommendation:

- `passed`: Actions available, at least one matching run, all relevant run/job states terminal green, no Actions unknowns, no blocking review/head limitation.
- `failed`: any matching Actions run/job is failed/cancelled/timed out/action-required by existing failure vocabulary.
- `running` / `pending`: Actions has non-terminal run/job state.
- `none`: Actions available and zero matching runs, if the current vocabulary can distinguish no observed Actions CI.
- `unknown`: Actions unavailable, schema invalid, jobs unavailable where run-level data is insufficient, abbreviated head cannot resolve, or payload is internally inconsistent.

Interface contract recommendation:

- `limitations` should include Actions API/job collection limitations.
- Do not emit limitation codes that imply Checks/statuses/status rollup coverage is missing.
- `failures` should contain Actions run/job failure entries only. No `commit_status`, `commit_status_aggregate`, `status_check_rollup`, or check-run fallback failure entries.
- `fingerprint` should hash head SHA, CI status, Actions run/job summary, Actions failure detail, and current limitations only.

## 9. File / Module Change Plan

```text
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/
|-- scripts/lib/pr_observation_checks.py
|   `-- change: remove forbidden supplemental collectors, status rollup classification, commit-status/check-run fallback, and Actions-limited coverage warning
|-- scripts/lib/pr_observation_snapshot.py
|   `-- change: keep compatibility subprocess path; adjust any CI compatibility/default payload assumptions if needed
|-- scripts/lib/pr_observation_wait.py
|   `-- change: compute CI progress from Actions run/job counts instead of ci.check_runs
|-- scripts/lib/pr_review_snapshot.py
|   `-- inspect-only: preserve review/comment/thread observation and avoid confusing review statuses with commit statuses
|
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
|-- infra/github_capability_cli.py
|   `-- change: remove Checks/statuses/statusCheckRollup from PR observation core probes; make actions_read relevant
|-- application/doctor.py
|   `-- change: neutral skipped/unavailable capability labels and repair guidance
|
tests/
|-- unit/infra/test_init_update.py
|   `-- change: fake-gh forbidden-call red tests; Actions green/failed/pending/zero-runs/jobs-unavailable cases; review unaffected cases
|-- cli_runtime/test_runtime_doctor_s04.py
|   `-- change: doctor expectations for Actions and PR/comment read capability, not Checks/statuses/status rollup
```

Do not edit dogfooding mirror first. If shipped asset update is later performed, verify mirror behavior through the repo's update/sync validation path rather than treating mirror files as source.

## 10. Migration / Compatibility / Rollback

- Migration is a one-way contract update from mixed CI rollup observation to Actions-only observation.
- Compatibility names may remain. They should carry explicit Actions-only wording so future maintainers do not infer GitHub Checks API usage from names.
- Existing JSON consumers should receive either the new Actions-centered fields or empty/deprecated legacy fields. The implementation should not silently repurpose legacy `check_runs` as if it were observed check-runs data.
- Rollback to Checks/statuses/status rollup should require a new ADR or explicit requirement change because the current accepted ADR forbids those surfaces.
- Status-only repositories and external-CI-only repositories migrate to `none` / `unknown` / human gate rather than observed pass.

## 11. Observability

- The payload should reveal `ci.source_policy = "github_actions_only"` or equivalent.
- Limitations should distinguish Actions API unavailable, Actions jobs unavailable, zero Actions runs, stale head, and review blockers.
- Progress output should show Actions run/job progress, not check-run progress.
- Wait stability should remain based on semantic fingerprint, but the CI portion of that fingerprint must exclude forbidden sources and include only Actions data.
- Doctor output should guide users toward Actions read and PR/comment read capability, not Checks/Commit statuses permission.

## 12. Test Strategy

High-value regression tests:

- Fake `gh` exits with a unique failure if any forbidden command is invoked: `/check-runs`, `/commits/{sha}/status`, `statusCheckRollup`, or `gh pr checks`.
- Actions success run/job produces `passed` without supplemental limitation.
- Actions failure produces `failed` and failure detail from run/job data only.
- Actions pending/running produces non-terminal status and wait progress from Actions counts.
- Zero Actions runs plus green legacy check/status fixtures does not pass. Ideally the fake `gh` should fail if legacy endpoints are called at all.
- Jobs API unavailable with failed run preserves failed status from run-level conclusion and records job detail limitation.
- Review/comment/thread fixtures still produce human gate or approval states while forbidden CI endpoints remain unused.
- Doctor capability diagnostics no longer require Checks/statuses/status rollup for PR observation.
- Static scan should target forbidden API strings and `statusCheckRollup` in live source/test fixtures, with allowlisted historical discussions and this issue's evidence docs excluded or reviewed separately.

Static scan scope:

- Search provider-side runtime and installed skill scripts for `/check-runs`, `/commits/{sha}/status`, `statusCheckRollup`, `gh pr checks`, `commit_statuses_read`, `check_runs_read`, and `ci_coverage_limited_to_github_actions`.
- Do not fail solely on the token `checks`; compatibility filenames and historical docs may legitimately contain it.

## 13. ADR Candidates

- No new ADR is required for the core decision because `20260620t143349z-adr-forbid-checks-api-in-pr-observation.md` already fixes the Actions-only decision and forbidden surfaces.
- A follow-up ADR may be warranted only if the project later wants to remove compatibility names/fields broadly or reintroduce a non-Actions CI source.

## 14. Risks

- Downstream consumers may rely on `ci.check_runs` counts. Mitigate with explicit compatibility fields or migration notes.
- Keeping `checks` named compatibility files may confuse future maintainers. Mitigate with source policy markers, docs wording, and forbidden-call tests.
- Removing status rollup means SpecDock can report Actions CI green while GitHub UI has an external required check failing. This is intentional loss, but merge-preparer wording must avoid saying all required checks passed.
- Jobs fetch bounding can hide some green job details. The design should ensure run-level classification remains authoritative and failures are not hidden by bounds.
- Doctor migration can accidentally under-report missing PR review/comment capability if it only focuses on Actions. Keep PR metadata and review/comment reads in the capability model.

## 15. Requirement Clarification Requests

None. The requirement, accepted ADR, and answered compatibility interview resolve the blocking boundaries:

- legacy commit statuses are forbidden;
- `checks` as a word or compatibility name is not forbidden;
- review/comment/thread observation remains in scope;
- external/non-Actions CI loss is intentional.

## 16. Integration Notes for Main Orchestrator

- Recommended canonical `design.md` sections to update: purpose/constraints, existing implementation understanding, design decisions/tradeoffs, dependency analysis, interface contract, sequence/data flow, file change plan, requirement-design mapping, test strategy, migration/rollback, risks.
- Recommended `report.md` entry: delegated draft evidence record with this artifact path, source requirement revision, `adoption_status: unreviewed`, `reflected_to: []`, and post-run diff guard result once the orchestrator runs it.
- This draft should not be treated as implementation-ready. The canonical design still needs main-orchestrator adoption and a fresh `spec-reviewer` pass.
- Leaf evidence used: none beyond the provided/read repository sources and existing discussion evidence.
- Forbidden actions avoided: no canonical docs, implementation files, tests, package/config, `.agents`, `.github`, or GitHub state were edited by this draft.

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
