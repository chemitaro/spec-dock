---
created_by_role: implementation-planner
scope_id: iss-00187
status: adopted
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/discussions/20260616t025000z-05-disc-current-review-observation-gap.md
  - spec-dock/active/issue/discussions/20260616t025500z-06-disc-current-p1-review-analysis.md
  - spec-dock/active/issue/discussions/20260616t030000z-07-disc-python-extraction-from-shell-scripts.md
  - tests/unit/infra/test_init_update.py
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/workflow_clarification.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/phase_plan.md
  - spec-dock/docs/reference_deps.md
  - spec-dock/docs/reference_sync.md
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: adopted
reflected_to:
  - plan.md
  - report.md
diff_guard_result: passed
---

# Additional Implementation Plan After S199

## 1. Plan Summary

This draft proposes S200+ steps to append after the current S199 addendum lane.

The new lane addresses four concrete gaps observed after PR #190 monitoring:

- The checks collector logic is still embedded as a large Python heredoc in `fetch_pr_checks_snapshot.sh`, making the current P1 repairs risky to review.
- PR #190 has two current P1 review findings in the checks collector:
  - unbounded per-run Actions job collection inside wait snapshots;
  - zero Actions runs incorrectly overriding green external check/status evidence.
- `review_completion_unknown` is currently safe as non-pass, but can be emitted too soon before a Codex review arrives.
- Provider assets, dogfooding mirror files, tests, reviewer gates, and per-step commits need to stay one-step-at-a-time.

The proposed order is:

1. S200: canonical adoption planning gate for this draft.
2. S201: extract only the checks collector Python into `pr_observation_checks.py` while preserving the shell contract.
3. S202: fix zero Actions runs with green external checks.
4. S203: bound Actions jobs collection while preserving failure diagnostics.
5. S204: harden `review_completion_unknown` timing.
6. S290: provider/mirror docs and asset sync.
7. S299: final validation, reviewer gates, PR observation, and final commit gate.

No implementation patch is included here.

## 2. Requirement / Design Traceability

- AC-001 / AC-002 / EC-002:
  - S202 and S203 preserve Actions-centered CI observation while preventing Actions absence or green-run job expansion from creating false blockers.
- AC-003:
  - S203 preserves failed Actions run/job diagnostic evidence and `ci.failures[]` detail.
- AC-004:
  - S203 preserves pending/running wait semantics while reducing per-poll job API expansion.
- AC-005 / EC-004:
  - S201 must preserve fixed script surface, stdout JSON authority, stderr diagnostic boundary, and secret redaction.
- AC-006 / AC-007:
  - S204 keeps `review_completion_unknown` non-pass, but requires explicit timing allowance before promotion.
- Provider/mirror constraint:
  - S290 aligns provider assets under `src/spec_dock/assets/install_root/.agents/...` with dogfooding mirror `.agents/...`.
- Existing design decisions reused:
  - provider source first;
  - fixed read-only GitHub API surface;
  - no caller-provided API proxy;
  - supplemental checks/statuses remain meaningful compatibility evidence;
  - `review_completion_unknown` is a human gate, not merge-ready.

Design gap note:

- The exact review latency allowance was left open in discussion 05. This draft makes it executable with a conservative fixed internal default:
  - `review_completion_unknown_min_trigger_age_seconds = 300`
  - `review_completion_unknown_min_ci_passed_age_seconds = 90`
- These values should be adopted only through canonical plan integration and fresh spec-reviewer review.

## 3. Milestones

- M1: Extraction safety milestone
  - S201 proves `fetch_pr_checks_snapshot.sh` remains the same public shell command while Python moves into `scripts/lib/pr_observation_checks.py`.
- M2: P1 logical correctness milestone
  - S202 proves zero Actions runs do not mask green external check/status evidence.
- M3: P1 bounded polling milestone
  - S203 proves wait/default snapshots do not expand every successful Actions run job list and still preserve failed job diagnostics.
- M4: Review timing safety milestone
  - S204 proves stable no-completion evidence is not promoted to `review_completion_unknown` before trigger and CI-passed age thresholds.
- M5: Shipping consistency milestone
  - S290 proves provider and mirror changed files match and docs describe the new extraction/timing behavior.
- M6: Final evidence milestone
  - S299 proves focused tests, broad unit file tests, `git diff --check`, `spec-dock validate`, reviewers, PR observation, and commit gates are complete or explicitly blocked.

## 4. Dependency-Derived Execution Order

- S200 depends on current S199 evidence and this discussion draft.
- S201 depends on no implementation files being changed by this delegated planner; it must run before P1 code changes so review diff is readable.
- S202 depends on S201 because the status ladder should be changed in extracted Python, not in the heredoc.
- S203 depends on S201 and should run after S202 so zero-Actions fallback behavior is fixed before job collection policy is narrowed.
- S204 depends on existing S100/S101 behavior and can run after S203; it touches wait timing, not checks classification.
- S290 depends on S201-S204 because mirror sync must happen after provider behavior is settled.
- S299 depends on S201-S204 and S290.

Step graph:

```text
S200
  -> S201
      -> S202
      -> S203
          -> S204
              -> S290
                  -> S299
```

## 5. Issue / Step Slicing

### S200 - Plan adoption gate for S200+ lane

- Behavior goal:
  - Main orchestrator decides whether and how to adopt this draft into canonical `plan.md` and `report.md`.
- Dependencies:
  - current S199 report evidence;
  - discussions 05, 06, 07;
  - this discussion draft.
- Target files:
  - canonical adoption target only: `spec-dock/active/issue/plan.md`, `spec-dock/active/issue/report.md`.
- Planned contract:
  - adopt, partially adopt, or reject this draft in Evidence Adoption Ledger;
  - run fresh spec-reviewer after canonical plan changes;
  - do not begin implementation until adopted canonical plan has a fresh pass.
- Test / evidence:
  - inspect-only: Evidence Adoption Ledger entry and fresh spec-reviewer result.
- Review gate:
  - spec-reviewer pass for canonical plan amendment.
- Commit gate:
  - plan/report amendment commit only after spec-reviewer pass.
- Rollback:
  - revert canonical plan/report amendment commit; discussion draft can remain as unadopted evidence.

### S201 - Extract checks collector Python without shell contract change

- Behavior goal:
  - Move embedded Python from `fetch_pr_checks_snapshot.sh` into standalone `scripts/lib/pr_observation_checks.py`; keep the shell command name, flags, validation, stdout final JSON, stderr behavior, and exit semantics.
- Dependencies:
  - S200 adopted and reviewed.
- Target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
  - `tests/unit/infra/test_init_update.py`
- Forbidden changes:
  - no behavior change to CI classification;
  - no mirror files in this step unless canonical plan explicitly makes S201 include mirror characterization;
  - no review/wait script changes.
- Delegated role:
  - dev-coder.
- Test cards:
  - `tc-s201-001` characterization: existing checks collector scenarios stay byte-contract compatible
    - 前提: current fake-`gh` issue_187 checks collector fixtures.
    - 操作: run focused checks collector tests before and after extraction.
    - 期待結果: final JSON fields currently asserted by tests remain unchanged.
    - 失敗検出: extraction changes stdout JSON, exit status, or secret redaction.
    - 検証方法: `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187 and actions"`.
  - `tc-s201-002` negative: unsafe inputs are rejected before `gh`
    - 前提: fake `gh` logs every call.
    - 操作: call `fetch_pr_checks_snapshot.sh` with invalid repo, PR, and SHA arguments.
    - 期待結果: exit 64 and fake `gh` is not called.
    - 失敗検出: wrapper stopped owning validation or Python receives unsafe caller input.
    - 検証方法: add or extend a focused wrapper validation test.
  - `tc-s201-003` scaffold: installed asset includes new Python file
    - 前提: temp target initialized or updated by installer.
    - 操作: inspect generated `.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`.
    - 期待結果: new file is copied by installer/update asset surface.
    - 失敗検出: provider extraction works locally but shipped asset omits the Python file.
    - 検証方法: existing init/update asset test assertion or focused inspection.
- Red / green evidence expectation:
  - Red can be characterization-only for behavior preservation; new file presence test should fail before extraction.
  - Green: focused issue_187 checks collector tests pass after extraction.
- Review gate:
  - code-reviewer pass focused on shell/Python boundary, fixed CLI surface, import-free/no-dependency Python, secret redaction, and stdout/stderr contract.
- Commit gate:
  - one S201 commit after reviewer pass and `git diff --check`.
- Rollback:
  - revert S201 commit restores heredoc-only collector; no data migration required.

### S202 - Zero Actions runs with green external checks

- Behavior goal:
  - Treat zero Actions runs as "no Actions evidence", not as global "no CI"; green check-runs or commit statuses can still produce `ci.status="passed"` when no failures, pending states, missing required checks, merge blockers, or unknown states are present.
- Dependencies:
  - S201.
- Target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
  - `tests/unit/infra/test_init_update.py`
- Forbidden changes:
  - no wait/review timing changes;
  - no automatic pass when both Actions and external evidence are absent.
- Delegated role:
  - dev-coder.
- Test cards:
  - `tc-s202-001` acceptance: zero Actions runs plus green check-runs passes
    - 前提: Actions returns `total_count=0`; check-runs for expected head are completed success; statuses are success; rollup has no blockers.
    - 操作: run `fetch_pr_checks_snapshot.sh`.
    - 期待結果: `ci.status="passed"`; Actions total remains 0; no blocking `zero_checks_s03_non_success`.
    - 失敗検出: external-CI-only repositories remain false-negative non-pass.
    - 検証方法: fake-`gh` collector test.
  - `tc-s202-002` acceptance: zero Actions runs plus green commit statuses passes
    - 前提: Actions returns zero runs; check-runs are absent or unavailable non-blocking; commit statuses are all success.
    - 操作: run collector.
    - 期待結果: `ci.status="passed"` if no blocking rollup/required-check limitation exists.
    - 失敗検出: status-only CI cannot pass.
    - 検証方法: fake-`gh` collector test.
  - `tc-s202-003` negative: zero Actions runs plus zero external evidence remains non-pass
    - 前提: Actions, check-runs, and statuses all have zero observed items.
    - 操作: run collector.
    - 期待結果: `ci.status` is `none` or `unknown`; blocking zero-check limitation remains.
    - 失敗検出: absence of all CI evidence becomes green.
    - 検証方法: update existing `test_issue_187_zero_actions_runs_is_never_passed`.
  - `tc-s202-004` negative: external pending/failure still wins
    - 前提: Actions returns zero; check-runs or statuses include pending/failure.
    - 操作: run collector.
    - 期待結果: `ci.status` is `pending`, `running`, or `failed`, never `passed`.
    - 失敗検出: zero-Actions fallback ignores external blockers.
    - 検証方法: parameterized fake-`gh` collector tests.
- Red / green evidence expectation:
  - Red: `tc-s202-001` should fail on current status ladder because `actions_zero_runs` wins before external green.
  - Green: focused selector passes after status ladder change.
- Review gate:
  - code-reviewer pass focused on false-pass safety, external-CI compatibility, existing zero-check grace, limitation severity, and no token/raw stderr leak.
- Commit gate:
  - one S202 commit after reviewer pass and focused tests.
- Rollback:
  - revert S202 commit returns to Actions-zero non-pass behavior; safe but reopens PR #190 P1.

### S203 - Bound Actions jobs collection while preserving diagnostics

- Behavior goal:
  - Avoid one jobs API call per successful Actions workflow run during wait/default snapshots, while preserving failed run/job/step diagnostics.
- Dependencies:
  - S201 and S202.
- Target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
  - `tests/unit/infra/test_init_update.py`
- Planned collection policy:
  - Do not fetch jobs for all terminal-green workflow runs by default; workflow run conclusion is enough for green classification.
  - Fetch jobs for failed, unknown, or explicitly diagnostic-relevant runs.
  - Keep a fixed internal cap for jobs-detail run expansion; do not add caller-provided endpoint or raw `gh` arguments.
  - If the cap prevents full diagnostics, emit a non-secret limitation such as `github_actions_jobs_collection_limited`; do not make green runs false-pass solely because skipped job expansion hides a known failed run.
- Forbidden changes:
  - no new public mode flag unless canonical design is amended;
  - no loss of failed job/step detail when failed run jobs are within cap.
- Delegated role:
  - dev-coder.
- Test cards:
  - `tc-s203-001` performance/regression: multiple green runs avoid per-run jobs expansion
    - 前提: fake `gh` returns several completed success workflow runs and fails if jobs endpoint is called for every green run.
    - 操作: run collector.
    - 期待結果: `ci.status="passed"`; job calls are zero or bounded by the documented internal policy.
    - 失敗検出: one snapshot still scales linearly with every successful run.
    - 検証方法: fake-`gh` call log assertion.
  - `tc-s203-002` acceptance: failed Actions still fetches useful job details
    - 前提: one failed workflow run has a failed job and failed step.
    - 操作: run collector.
    - 期待結果: `ci.status="failed"` and `ci.failures[]` keeps sanitized workflow/job/step evidence.
    - 失敗検出: bounding removes actionable repair details.
    - 検証方法: existing failed-job tests plus explicit call log.
  - `tc-s203-003` negative: expansion cap is explicit and non-secret
    - 前提: more failed/unknown runs exist than the internal expansion cap.
    - 操作: run collector.
    - 期待結果: collector remains bounded, returns non-pass if unresolved failure-risk evidence exists, and emits sanitized limitation.
    - 失敗検出: unbounded API calls or silent omission of failure-risk evidence.
    - 検証方法: fake-`gh` call count and limitation assertions.
  - `tc-s203-004` regression: check-run-derived failure fallback still dedupes
    - 前提: check-run and Actions jobs can both point to the same failed run/job.
    - 操作: run collector.
    - 期待結果: stable `dedupe_key` prevents duplicate `ci.failures[]`.
    - 失敗検出: extraction/bounding regresses S02/S99 dedupe behavior.
    - 検証方法: existing issue_75/issue_187 failure-dedupe tests.
- Red / green evidence expectation:
  - Red: `tc-s203-001` should fail on current code because it calls jobs for every workflow run.
  - Green: focused selector including `issue_187`, jobs summary, failed job, and call-log tests passes.
- Review gate:
  - code-reviewer pass focused on wait-budget impact, bounded API calls, failure diagnostics, and compatibility of `ci.actions.jobs`, `jobs_detail`, and `jobs_summary`.
- Commit gate:
  - one S203 commit after reviewer pass.
- Rollback:
  - revert S203 commit restores unbounded detail collection; correctness mostly remains, performance/rate risk returns.

### S204 - Review completion unknown timing hardening

- Behavior goal:
  - Prevent premature `review_completion_unknown` before Codex review has a reasonable chance to appear, while keeping the state non-pass and human-gated after stability and latency allowance.
- Dependencies:
  - S100/S101 existing no-completion evidence;
  - S203, to reduce wait-loop collector cost before timing hardening is evaluated.
- Target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - `tests/unit/infra/test_init_update.py`
- Planned timing contract:
  - Introduce internal constants in the embedded wait Python:
    - `review_completion_unknown_min_trigger_age_seconds = 300`
    - `review_completion_unknown_min_ci_passed_age_seconds = 90`
  - Promotion to `review_completion_unknown` requires:
    - CI passed;
    - head matched;
    - no selected current blocker;
    - no pending review signal;
    - no blocking collection failure;
    - same fingerprint and quiet window satisfied;
    - trigger age is at least 300 seconds;
    - CI-passed observation age is at least 90 seconds.
  - Before thresholds are met, final output remains pending/timeout with `wait_or_resume`, not `review_completion_unknown`.
  - Add machine-readable wait fields:
    - `wait.review_trigger_age_seconds`
    - `wait.ci_passed_age_seconds`
    - `wait.review_completion_unknown_min_trigger_age_seconds`
    - `wait.review_completion_unknown_min_ci_passed_age_seconds`
- Forbidden changes:
  - no promotion to passed/merge-ready from missing completion signal;
  - no completion inference from selected counts alone;
  - no new GitHub endpoint.
- Delegated role:
  - dev-coder.
- Test cards:
  - `tc-s204-001` negative: below trigger-age threshold keeps waiting
    - 前提: CI passed, head matched, stable no-completion evidence, trigger-created-at is recent.
    - 操作: run `wait_pr_observation.sh` fake snapshots with short timeout.
    - 期待結果: no `review_completion_unknown`; result is pending/timeout with `wait_or_resume`.
    - 失敗検出: PR #190 race where unknown emits before review arrives.
    - 検証方法: fake snapshot wait test.
  - `tc-s204-002` negative: below CI-passed-age threshold keeps waiting
    - 前提: trigger is old enough, but CI first becomes passed inside the current wait window.
    - 操作: run wait with snapshots transitioning pending -> passed.
    - 期待結果: no immediate unknown on first stable passed snapshot until CI-passed age threshold is met.
    - 失敗検出: CI completion instant becomes no-review terminal-like state.
    - 検証方法: fake snapshot sequence test.
  - `tc-s204-003` acceptance: beyond both thresholds promotes to human-gate unknown
    - 前提: trigger is old enough, CI has been passed long enough, fingerprint/quiet stability is satisfied, no blockers/pending review exist.
    - 操作: run wait.
    - 期待結果: `normalized_status="human_gate"`, `decision.status_reason="review_completion_unknown"`, `recommended_next_action="human_gate"`, wait age fields present.
    - 失敗検出: hardening disables intended S101 no-completion escape hatch.
    - 検証方法: update S101 stable no-completion test with old trigger/CI-passed conditions.
  - `tc-s204-004` regression: submitted review arriving later wins
    - 前提: first snapshots have stable no-completion below threshold; later snapshot has submitted Codex review with unresolved thread.
    - 操作: run wait sequence.
    - 期待結果: final action is `address_review_feedback`, not `review_completion_unknown`.
    - 失敗検出: timing hardening still loses late actionable review feedback.
    - 検証方法: fake snapshot sequence test.
- Red / green evidence expectation:
  - Red: `tc-s204-001` should fail on current S101 behavior because stability alone can promote unknown.
  - Green: focused selector for `review_completion_unknown`, `issue_187_s101`, and new timing tests passes.
- Review gate:
  - code-reviewer pass focused on timing semantics, wait deadline behavior, non-pass status, no false completion, and field compatibility.
- Commit gate:
  - one S204 commit after reviewer pass.
- Rollback:
  - revert S204 commit restores earlier S101 stability-only unknown promotion; safe non-pass remains, but timing race returns.

### S290 - Provider/mirror sync and docs impact

- Behavior goal:
  - Ship the extracted Python asset and timing/P1 behavior consistently in provider and dogfooding mirror, with operator docs aligned.
- Dependencies:
  - S201-S204.
- Target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - `.agents/skills/github-pr-observation/SKILL.md`
  - `.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
  - `.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - any provider/mirror script files changed by S201-S204.
- Delegated roles:
  - doc-writer for `SKILL.md`;
  - utility-worker or dev-coder for mechanical mirror sync.
- Test / inspection cards:
  - `tc-s290-001` docs: skill docs describe extracted helper and timing unknown
    - 前提: S201-S204 behavior is implemented.
    - 操作: inspect provider and mirror `SKILL.md`.
    - 期待結果: docs mention bounded Actions collection, external check fallback, and delayed `review_completion_unknown` as human gate.
    - 失敗検出: operator docs still imply immediate unknown or Actions-only worldview.
    - 検証方法: docs inspection and spec-reviewer.
  - `tc-s290-002` mirror: provider and dogfooding mirror match
    - 前提: changed provider files have mirror counterparts.
    - 操作: compare provider/mirror changed files.
    - 期待結果: files are byte-identical where intended; any intentional difference is recorded.
    - 失敗検出: PR #190 dogfooding uses stale mirror behavior.
    - 検証方法: `cmp -s` or equivalent file comparison.
  - `tc-s290-003` scaffold: install/update carries new Python asset
    - 前提: temp target runs init/update.
    - 操作: inspect generated `.agents/.../pr_observation_checks.py`.
    - 期待結果: new Python file appears and wrapper references adjacent path.
    - 失敗検出: provider asset tree ships a wrapper that cannot find its Python entrypoint.
    - 検証方法: focused installer asset test.
- Red / green evidence expectation:
  - Red for new asset presence may fail before S201/S290; docs inspection is inspect-only.
  - Green: mirror `cmp`, focused asset tests, and `git diff --check` pass.
- Review gate:
  - spec-reviewer for docs/spec alignment;
  - code-reviewer for mirror script sync and scaffold behavior.
- Commit gate:
  - one S290 commit after docs and sync reviewer gates pass.
- Rollback:
  - revert S290 commit may desync mirror from provider; if rollback is needed, revert S201-S204 or rerun mirror sync consistently.

### S299 - Final quality, reviewer, PR observation, and commit gate

- Behavior goal:
  - Close S200+ lane with tests, validation, reviewer gates, PR #190 observation, and clean commit boundaries.
- Dependencies:
  - S201-S204 and S290 committed or approved-no-op where allowed.
- Target files:
  - issue-wide diff.
- Required checks:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187 or pr_observation or actions or review_completion_unknown"`
  - `uv run pytest tests/unit/infra/test_init_update.py -q`
  - `git diff --check`
  - `./spec-dock/scripts/spec-dock validate`
  - provider/mirror `cmp -s` for changed assets.
- PR observation evidence:
  - rerun PR observation on latest PR #190 head after push or local mirror update;
  - record whether previous selected unresolved threads are resolved, superseded, or still blocking;
  - do not claim merge readiness while P1 threads remain unresolved.
- Review gates:
  - qa-reviewer pass for test sufficiency and race coverage;
  - issue-wide code-reviewer pass for integrated scripts/tests/docs diff;
  - final spec-reviewer pass for requirement/design/plan/report alignment.
- Commit gate:
  - S299 final report/evidence commit only after final reviewers pass.
  - It must not bundle uncommitted S201-S204 implementation changes.
- Rollback:
  - revert the specific failed step commit first; if final evidence only is wrong, amend/recommit report evidence without touching implementation behavior.

## 6. Test Strategy Mapping

| Test ID | Step | Requirement / risk | Evidence expectation |
|---|---|---|---|
| tc-s201-001 | S201 | Shell contract preservation | characterization green before/after extraction |
| tc-s201-002 | S201 | Fixed unsafe input rejection | red/green if new test is added |
| tc-s201-003 | S201/S290 | New Python asset ships | red before asset inclusion, green after |
| tc-s202-001 | S202 | External check-runs pass with zero Actions | red-required |
| tc-s202-002 | S202 | External statuses pass with zero Actions | red-required |
| tc-s202-003 | S202 | No CI evidence never passes | covered-existing plus updated regression |
| tc-s202-004 | S202 | External pending/failure wins | red-required |
| tc-s203-001 | S203 | Bounded green run job collection | red-required call-log test |
| tc-s203-002 | S203 | Failed Actions diagnostics preserved | covered-existing plus call-log regression |
| tc-s203-003 | S203 | Cap limitation explicit | red-required if cap path implemented |
| tc-s203-004 | S203 | Failure dedupe preserved | covered-existing |
| tc-s204-001 | S204 | No premature unknown below trigger age | red-required |
| tc-s204-002 | S204 | No premature unknown below CI-passed age | red-required |
| tc-s204-003 | S204 | Unknown still works after thresholds | red/green update to S101 test |
| tc-s204-004 | S204 | Late submitted review wins | red-required |
| tc-s290-001 | S290 | Docs reflect behavior | inspect-only |
| tc-s290-002 | S290 | Provider/mirror sync | inspect-only / cmp |
| tc-s290-003 | S290 | Installer/update carries Python asset | red/green if asset test absent |
| tc-s299-001 | S299 | Final lane closure | manual-required plus reviewers |

## 7. Review Gates

- Per-step code-reviewer:
  - S201, S202, S203, S204.
  - Required result: fresh `review_status: pass`.
- Docs/spec reviewer:
  - S200 canonical plan amendment;
  - S290 docs update;
  - S299 final spec alignment.
- QA reviewer:
  - S299 final test sufficiency, especially P1 regression coverage and review-timing race coverage.
- Reviewer failure handling:
  - Treat P1/P2 findings as bounded follow-up within the same step where possible.
  - Do not use final reviewer pass to replace missing per-step review.
  - Do not claim reviewer-pass, merge readiness, or implementation readiness from this discussion draft.

## 8. Rollback / Compatibility

- Public shell command compatibility:
  - `fetch_pr_checks_snapshot.sh --repo OWNER/REPO --pr NUMBER --head-sha SHA` must remain valid.
  - `wait_pr_observation.sh` existing flags remain valid; S204 should avoid adding a public option unless canonical design is amended.
- JSON compatibility:
  - Existing `ci.status`, `ci.actions.workflow_runs`, `ci.actions.jobs`, `ci.actions.jobs_summary`, `ci.actions.jobs_detail`, `ci.failures`, `limitations`, and `decision` fields remain.
  - S203 may reduce green-run `ci.actions.jobs[]` detail by design, but must keep summary and limitation semantics explicit.
  - S204 only adds wait timing fields and must not remove existing wait fields.
- Rollback order:
  - Revert the latest failed step commit first.
  - If Python extraction fails in consumers, revert S201 before reverting S202/S203.
  - If timing guard is too conservative, revert or adjust S204 without touching Actions collector fixes.
- Data migration:
  - None. This lane ships scripts/tests/docs only.

## 9. Docs Impact

- Provider `SKILL.md` should describe:
  - Actions workflow runs as primary for GitHub Actions-centered CI;
  - external check/status evidence as valid fallback when Actions has no runs;
  - bounded job expansion and where detailed failure diagnostics remain available;
  - delayed `review_completion_unknown` as non-pass human gate after explicit timing allowance.
- Mirror `.agents/.../SKILL.md` should match provider.
- No ADR is required unless the orchestrator decides the review-latency default should become a durable cross-issue policy.
- Canonical `requirement.md` / `design.md` may need amendment if spec-reviewer decides external-green zero-Actions pass or timing constants are beyond current approved scope.

## 10. Final Quality Gate

S299 should not close until all are true:

- S201-S204 and S290 are committed or explicitly approved-no-op.
- Focused and broad tests pass or failures are explained as unrelated and accepted by reviewers.
- Provider/mirror comparisons pass for all changed files.
- `git diff --check` passes.
- `./spec-dock/scripts/spec-dock validate` passes.
- PR #190 observation is rerun on the latest head and unresolved P1 thread status is recorded.
- qa-reviewer, issue-wide code-reviewer, and final spec-reviewer all pass.
- Final report evidence is updated by the main orchestrator.
- Worktree has no unintended staged/unstaged changes after final commit.

## 11. Plan Blockers

- Potential design blocker:
  - If external green checks with zero Actions runs are judged outside the current requirement/design scope, canonical requirement/design must be amended before S202 implementation.
- Potential timing blocker:
  - The proposed 300s/90s timing constants are planning defaults, not accepted authority. If the orchestrator wants configurable values, design must be amended first.
- Potential extraction blocker:
  - If installer/update asset tests reveal new `.py` files under `.agents` are not copied by current provider asset packaging, S201 must stop and fix scaffold asset inclusion before behavior changes.
- No user clarification is required from this delegated planner; the main orchestrator owns any user dialogue.

## 12. Integration Notes for Main Orchestrator

- Suggested Evidence Adoption Ledger entry:
  - source: `discussions/20260616t030500z-08-disc-additional-implementation-plan-after-s199.md`
  - source_role: `implementation-planner`
  - adoption_status: `adopted`, `partially_adopted`, or `rejected`
  - target: `plan.md` S200+ addendum and `report.md` planning evidence
  - blocking: true until canonical adoption decision and fresh spec-reviewer pass are recorded.
- Suggested canonical plan insertion:
  - append after current S199 addendum;
  - preserve existing S01-S199 closure evidence;
  - add S200-S299 with step-local concrete test cards and reviewer/commit gates.
- Suggested report updates:
  - Delegated Draft Evidence for this file;
  - Evidence Adoption Ledger adoption decision;
  - Closure Delta for new S200+ closure IDs;
  - Spec Authoring Gate / reviewer evidence after canonical plan amendment.
- Leaf evidence used:
  - none beyond local source inspection; no peer authoring roles or implementation agents were invoked.
- Forbidden actions avoided:
  - no canonical requirement/design/plan/report edits;
  - no implementation/test/package/config edits;
  - no `.agents`, `.github`, `.codex`, or secret edits;
  - no GitHub mutation;
  - no reviewer pass, phase promotion, implementation readiness, or issue readiness claimed.

Adoption note:

- This delegated implementation-plan draft has been adopted into the S200+ `plan.md` addendum and `report.md` evidence ledger by the main orchestrator.
- The adoption evidence is recorded in `report.md` D-012 and EAL-029.
- This artifact does not by itself claim reviewer-pass, implementation readiness, or user-dialogue ownership; S200 still requires a fresh spec-reviewer pass before S201 implementation.
