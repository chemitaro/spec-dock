---
created_by_role: system-architect
scope_id: iss-00187
status: adopted
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/discussions/20260616t025000z-05-disc-current-review-observation-gap.md
  - spec-dock/active/issue/discussions/20260616t025500z-06-disc-current-p1-review-analysis.md
  - spec-dock/active/issue/discussions/20260616t030000z-07-disc-python-extraction-from-shell-scripts.md
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
intended_targets:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
  - tests/unit/infra/test_init_update.py
adoption_status: adopted
reflected_to:
  - design.md
  - plan.md
  - report.md
diff_guard_result: passed
---

# PR Observation Architecture Amendment Proposal

## 1. Requirement Coverage

This proposal covers the three open iss-00187 concerns as one design amendment:

- Extract embedded Python from shell wrappers, starting with `fetch_pr_checks_snapshot.sh`.
- Resolve the current PR #190 P1 findings:
  - bounded Actions job collection inside wait snapshots;
  - zero Actions runs must not mask readable external green checks.
- Harden `review_completion_unknown` timing so it does not finalize before a Codex review can realistically arrive.

The mapped requirement surface is AC-001 through AC-007 and EC-001 through EC-004. The amendment does not change the accepted principle that Actions read is the primary GitHub Actions CI surface, nor that absence of review completion evidence is non-pass.

## 2. Existing Context Findings

The current issue docs already define Actions-primary CI observation, supplemental check/status evidence, `review_completion_unknown`, provider-first editing, and dogfooding mirror verification.

The three latest discussion artifacts add new evidence:

- The current PR #190 snapshot can detect a submitted Codex PR review with two unresolved P1 threads once the review exists.
- The earlier `review_completion_unknown` result was timing-sensitive: CI/head completed before the Codex review object became visible.
- `fetch_pr_checks_snapshot.sh` is a large shell file with embedded Python; both P1 findings are Python data-flow and classification issues, not shell behavior issues.

Current code inspection confirms:

- `fetch_pr_checks_snapshot.sh` calls `gh api repos/{repo}/actions/runs/{run_id}/jobs` inside the loop for every workflow run.
- The status ladder classifies `actions_zero_runs` as `ci_status="none"` before the later external-evidence fallback can pass green check/status evidence.
- `wait_pr_observation.sh` promotes `review_completion_unknown` after quiet and same-fingerprint stability, but there is no explicit minimum age after the trigger or after CI first passed.

## 3. Design Decisions

Decision A: extract the checks collector Python first.

`fetch_pr_checks_snapshot.sh` should become a thin shell wrapper that preserves the public command and calls an adjacent Python entrypoint, proposed as `scripts/lib/pr_observation_checks.py`. This is a prerequisite-quality step for the P1 fixes because the defects live in the Python collector policy and status classifier.

Decision B: split CI collection into summary classification and bounded diagnostics.

The collector should classify high-level CI state from Actions workflow runs plus supplemental check/status evidence without requiring job expansion for every green run. Job expansion should be reserved for failed, non-terminal, unknown, or capped diagnostic cases.

Decision C: zero Actions runs means "no Actions evidence", not "no CI".

If Actions returns zero workflow runs, the classifier must continue to evaluate readable check-runs, commit statuses, and status rollup. External green evidence may yield `ci.status="passed"` when there is no observed failure/pending/unknown evidence. Zero Actions runs alone must remain non-pass.

Decision D: `review_completion_unknown` requires a temporal guard beyond quiet/stable fingerprint.

Quiet and same-fingerprint stability prove the observed JSON stopped changing, not that Codex has had enough time to publish a review. Promotion should require an explicit minimum age relative to the current review trigger and/or first CI-passed observation.

## 4. Alternatives Considered

Alternative 1: patch the heredoc directly.

Rejected as the default path. It is smaller in raw diff but keeps the P1 fixes inside a 1000+ line mixed shell/Python script and makes future regression boundaries worse.

Alternative 2: extract all PR observation scripts first.

Rejected for this issue slice. It increases blast radius before urgent PR #190 fixes. Extract checks first; defer review/wait extraction unless needed for timing tests.

Alternative 3: add an explicit `--mode wait|diagnostic` public flag.

Not recommended initially. It changes the public surface. Prefer internal bounded default behavior that works for both snapshot and wait callers. If needed later, expose mode only through a documented compatible extension.

Alternative 4: delay `review_completion_unknown` only by increasing `--quiet-seconds`.

Rejected. Quiet time tracks payload stability since latest observed change, not Codex review latency. It cannot express trigger age or CI-pass age clearly.

## 5. Boundary / Contract Model

Shell wrapper boundary:

- Preserve command names, flags, stdout final JSON authority, stderr diagnostics, and exit status.
- Validate fixed CLI arguments and pass them to Python explicitly.
- Do not accept arbitrary API endpoints, raw `gh` args, GraphQL queries, headers, or request bodies.

Python collector boundary:

- Own `gh` reads, JSON normalization, status taxonomy, limitation construction, secret redaction, and final payload rendering.
- Provide small helper seams only where they reduce concrete complexity:
  - `collect_actions_runs`
  - `should_expand_actions_jobs`
  - `collect_actions_jobs_for_relevant_runs`
  - `classify_ci_status`
  - `build_actions_summary`

Wait wrapper boundary:

- Keep trigger/resume and polling orchestration in `wait_pr_observation.sh` for now.
- Add explicit timing fields and predicates around `review_completion_unknown` promotion without changing it into pass/merge-ready.

## 6. Dependency Analysis

Implementation dependency order should be:

1. Extract `fetch_pr_checks_snapshot.sh` Python to `pr_observation_checks.py` with behavior-preserving tests.
2. Fix bounded job collection and zero-Actions/external-green classification in the extracted module.
3. Adjust wrapper tests only if collector output shape requires it.
4. Add review timing hardening in `wait_pr_observation.sh`; do not broaden review collector semantics unless tests prove missing evidence fields.
5. Refresh provider docs and dogfooding mirror after provider behavior is stable.

`fetch_pr_observation_snapshot.sh` and `wait_pr_observation.sh` depend on the collector JSON contract, so the collector should continue to emit existing fields and only add compatible metadata.

## 7. Source of Record

Provider source is the record for implementation:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`
- proposed new `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`

Dogfooding mirror under `.agents/skills/github-pr-observation/` is validation/sync surface, not primary source.

Canonical issue docs are main-orchestrator-owned. This artifact was adopted into the S200+ design/plan addendum and report evidence.

## 8. Data Flow / Domain Model / Interface Contract

Proposed checks data flow:

1. Shell wrapper receives `--repo`, `--pr`, `--head-sha`.
2. Wrapper invokes `python3 "$script_dir/pr_observation_checks.py" --repo ...`.
3. Python collects Actions workflow runs by expected head SHA.
4. Python classifies run-level state.
5. Python expands jobs only for relevant runs:
   - failed;
   - running/pending;
   - unknown;
   - optionally a documented small cap for green diagnostic sampling.
6. Python collects supplemental check-runs/statuses/rollup.
7. Python classifies CI with this precedence:
   - primary Actions unavailable or head resolution failure -> `unknown`;
   - any observed failure -> `failed`;
   - any observed running -> `running`;
   - any observed pending or required missing -> `pending`;
   - unknown decisive evidence -> `unknown`;
   - zero Actions runs plus green external evidence -> `passed`;
   - zero Actions runs plus no external evidence -> `none` with zero-check limitation;
   - Actions green plus no blocking supplemental evidence -> `passed` with coverage limitation where applicable.

Proposed review timing data flow:

1. Wait loop records trigger metadata and first observed CI-passed timestamp.
2. A no-completion candidate remains pending while below the minimum review latency.
3. Only after CI passed, head matched, no blockers/pending review evidence, quiet stability, same-fingerprint stability, and latency threshold are all satisfied can the wait wrapper emit `review_completion_unknown`.

Suggested output metadata:

- `wait.review_trigger_age_seconds`
- `wait.ci_passed_age_seconds`
- `wait.review_completion_unknown_min_age_seconds`
- `decision.status_reason="missing_current_completion_signal"` before the threshold
- `decision.status_reason="review_completion_unknown"` only after the threshold

## 9. File / Module Change Plan

Provider changes:

- Convert `scripts/lib/fetch_pr_checks_snapshot.sh` into a thin compatibility wrapper.
- Add `scripts/lib/pr_observation_checks.py`.
- Update `scripts/wait_pr_observation.sh` timing predicate and wait metadata.
- Update `SKILL.md` only if user/operator semantics change.

Tests:

- Add extraction-preservation tests for the wrapper invoking the Python entrypoint.
- Add fake `gh` tests for bounded job collection, external green checks with zero Actions runs, failed Actions diagnostics, and zero evidence non-pass.
- Add fake wait tests for below-threshold no-review state, above-threshold `review_completion_unknown`, and late-arriving submitted review taking precedence.

Mirror:

- Sync `.agents/skills/github-pr-observation/` changed files after provider behavior is stable.

## 10. Migration / Compatibility / Rollback

Compatibility constraints:

- Existing commands and flags must remain valid.
- Existing JSON fields must remain available.
- stdout remains final JSON only.
- stderr remains diagnostics/progress only.
- No new third-party dependency.
- No new authentication surface.
- No raw token/auth stderr output.

Migration impact:

- Consumers that execute the shell script continue to do so.
- Installed asset layout gains an adjacent Python file; scaffold/update tests must cover that file.

Rollback:

- Revert the wrapper, new Python file, tests, docs, and mirror changes as one issue diff. Public CLI compatibility means rollback does not require consumer migration.

## 11. Observability

Add machine-readable observability without leaking secrets:

- Job collection summary:
  - `ci.actions.jobs_summary.collection.mode`
  - `ci.actions.jobs_summary.collection.expanded_runs`
  - `ci.actions.jobs_summary.collection.skipped_green_runs`
  - `ci.actions.jobs_summary.collection.cap`
- External evidence summary remains in existing check/status fields.
- Wait timing:
  - `wait.review_trigger_age_seconds`
  - `wait.ci_passed_age_seconds`
  - `wait.review_completion_unknown_min_age_seconds`
  - `wait.review_completion_unknown_latency_satisfied`

These fields should support debugging PR #190-style timing without changing pass/fail semantics.

## 12. Test Strategy

Required tests:

- Behavior-preserving extraction: wrapper returns identical JSON shape for existing fake `gh` happy path.
- Bounded collection: multiple green Actions runs do not trigger unbounded per-run job calls during default snapshots.
- Failed diagnostics: failed run/job still emits sanitized useful `ci.failures` evidence.
- Zero Actions plus external green: returns `ci.status="passed"`.
- Zero Actions plus no external evidence: remains `none` or `unknown`, never `passed`.
- Review below latency threshold: remains pending/wait_or_resume.
- Review above latency threshold: emits `review_completion_unknown` as human gate.
- Late submitted review with unresolved threads: overrides prior no-completion state and recommends `address_review_feedback`.

Run focus:

- `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187 or pr_observation or actions or review_completion_unknown"`
- Then the broader file run if the focused set passes.
- `./spec-dock/scripts/spec-dock validate` before closure.

## 13. ADR Candidates

No full ADR is required unless the team wants a durable shipped-asset architecture rule.

Potential ADR if elevated:

- "PR observation shell scripts are stable host adapters; non-trivial collector logic lives in adjacent Python modules."

Issue-local documentation is sufficient if this remains limited to github-pr-observation assets.

## 14. Risks

- Extraction may create scaffold/update drift if the new Python file is not included in provider asset copying and mirror validation.
- Bounded job collection can reduce green-run detail. This is acceptable if high-level green classification remains correct and failed/non-terminal diagnostics are preserved.
- External green pass could false-pass if partial supplemental evidence hides required checks. Mitigate by preserving required rollup blockers when available and limitation when coverage is incomplete.
- Review latency threshold can be too short or too long. Too short repeats the PR #190 race; too long delays completion. Make the default explicit and testable.
- Adding timing state to wait loop may make tests sensitive to wall-clock time. Use fake/stubbed timestamps where possible or very small deterministic thresholds in tests.

## 15. Requirement Clarification Requests

Clarification candidates for the main orchestrator:

- What default minimum review latency should gate `review_completion_unknown` after `@codex review`? A conservative default such as 300 seconds is safer than relying only on quiet/same-fingerprint stability, but this needs owner confirmation.
- Should the minimum latency be configurable through a wait flag, environment variable, or fixed internal constant? Prefer a flag only if operators need control; otherwise a documented constant keeps the public surface smaller.
- Should default job expansion cap be fixed, or should failed/non-terminal-only expansion be the first implementation? Prefer failed/non-terminal-only first, with a small cap only if green diagnostics are still required.

No blocker prevents drafting the amendment; these choices affect exact implementation constants and tests.

## 16. Integration Notes for Main Orchestrator

Recommended canonical amendments:

- In `design.md`, add a "Collector Extraction and Bounded Diagnostics" subsection before the current file change plan.
- In `design.md`, revise zero Actions semantics: zero Actions runs are no Actions evidence, not global no-CI evidence.
- In `design.md`, add review timing invariants for `review_completion_unknown`.
- In `plan.md`, insert an extraction step before current P1 fixes, or amend S01/S02 so extraction is explicitly the first substep.
- In `plan.md`, add closure IDs for:
  - extraction compatibility;
  - bounded green job collection;
  - zero Actions plus external green pass;
  - review latency below/above threshold;
  - late review override.

Adoption should keep the current safety rules:

- No observed failure/pending/unknown risk can become `passed`.
- `selected_unresolved_count == 0` and `completion_signal="none"` are not completion.
- Current unresolved review feedback always overrides no-completion/unknown.
- Actions-only green can pass only with visible coverage limitation when full coverage is unproven.
- Supplemental evidence is still allowed to downgrade Actions green.

Adoption note:

- This delegated architecture draft has been adopted into the S200+ `design.md` / `plan.md` addendum and `report.md` evidence ledger by the main orchestrator.
- The adoption evidence is recorded in `report.md` D-012 and EAL-028.
- This artifact does not by itself claim reviewer-pass, implementation readiness, or user-dialogue ownership; S200 still requires a fresh spec-reviewer pass before S201 implementation.
