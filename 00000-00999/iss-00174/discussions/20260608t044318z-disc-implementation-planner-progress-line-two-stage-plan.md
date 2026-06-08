---
created_by_role: implementation-planner
scope_id: iss-00174
source_paths:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/discussions/20260608t043253z-disc-system-architect-progress-line-two-stage-design.md
  - spec-dock/active/issue/discussions/20260608t031000z-disc-progress-line-two-stage-implementation-plan.md
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
  - .agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
  - tests/unit/infra/test_init_update.py
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/docs/phase_plan.md
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
  - .agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
  - tests/unit/infra/test_init_update.py
adoption_status: unreviewed
reflected_to: []
diff_guard_result: passed
---

# Plan Summary

iss-00174 should be executed as a provider-first, test-first refinement of `wait_pr_observation.sh`: first pin stderr progress behavior and quiet reset obligations in focused regression tests, then add a wait-wrapper progress projection, update semantic fingerprint inputs, render two-stage progress, sync the dogfooding mirror, and close with parity, syntax, focused pytest, reviewer, docs, and final quality gates.

The plan keeps stdout final JSON authoritative, keeps stderr progress non-authoritative and bounded to one line per poll, avoids new progress-only GitHub API calls, and treats provider/mirror parity as a shipped asset contract rather than a cosmetic copy step.

# Requirement / Design Traceability

- AC-001 maps to CI running detailed progress: `ci=running checks=2/4 ok=2 run=2 pend=0 fail=0`.
- AC-002 maps to CI check-run count changes being included in `semantic_fingerprint()` so `latest_change_poll` and `quiet` reset.
- AC-003 maps to terminal passed compact rendering: `ci=passed` with normal `checks=` detail omitted.
- AC-004 maps to trigger-window review progress counts: `comments=0 -> 1 -> 2` from current Codex review comments / review signals, not historical PR-wide comments.
- AC-005 maps to review comment / thread / unresolved count changes being included in quiet reset semantics.
- AC-006 maps to compact human-gate review rendering that preserves `comments=N` and, when thread state is the gate reason, `threads=N unresolved=N`.
- AC-007 maps to preserving `--progress none` as stderr-progress silent while stdout remains parseable final JSON.
- AC-008 maps to stdout/stderr boundary and forbidden-token assertions: no review body, URL, reviewer name, workflow name, job name, failed step detail, or P1/P2 text interpretation in progress lines.
- AC-009 maps to deterministic optional-field dropping and `limit=truncated`, with `limit=none` as the normal value.
- AC-010 maps to provider/mirror parity verification for both `wait_pr_observation.sh` copies.
- EC-001 through EC-008 map to zero-check, skipped/neutral, failed CI, old unresolved thread, unknown trigger timestamp, timeout, raw-body-only, and over-budget progress regression coverage.

# Milestones

- M01 Red contract: add focused failing or characterization tests for CI detail, review detail, compact rendering, quiet reset, stdout/stderr separation, truncation, and parity.
- M02 Provider implementation: add progress projection helpers, two-stage renderer, and fingerprint counter alignment in provider `wait_pr_observation.sh`.
- M03 Mirror sync: copy the provider script to `.agents/.../wait_pr_observation.sh` only after provider behavior is green.
- M04 Verification and refactor: run focused pytest, `bash -n`, provider/mirror `diff -u`, and `git diff --check`; perform bounded refactor only after green.
- M05 Review and evidence closure: record report evidence, run per-step `code-reviewer`, S90 docs impact gate, S99 final `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer`.

# Dependency-Derived Execution Order

1. Confirm implementation entry conditions: requirement and design are approved; report shows requirement/design spec-reviewer pass; no unresolved design gap remains.
2. Inspect current provider wait wrapper and nearby PR observation tests to place tests without creating a new test surface.
3. Add Red tests before behavior changes. Use existing fake `gh` / snapshot harness patterns in `tests/unit/infra/test_init_update.py`.
4. Implement provider projection and rendering. Keep collector schema unchanged unless a test proves existing payload cannot express the required count.
5. Update `semantic_fingerprint()` using the same progress-significant counters as the renderer.
6. Run focused tests against provider behavior; fix only the smallest behavior slice required by the failing test.
7. Sync mirror and verify exact parity.
8. Run syntax, parity, focused pytest, and whitespace diff checks.
9. Close step evidence in `report.md`, then route reviewer gates. A reviewer fail returns to the relevant bounded implementation step, not to final closure.

# Issue / Step Slicing

- S01 Progress test harness and Red obligations
  - Scope: `tests/unit/infra/test_init_update.py`.
  - Closure ids: `cl-ci-detail`, `cl-ci-quiet`, `cl-ci-compact`, `cl-review-detail`, `cl-review-quiet`, `cl-review-human-gate`, `cl-progress-none`, `cl-boundary`, `cl-truncation`.
  - Red / alternative evidence: red-required for new progress fields and quiet reset; covered-existing for old collector trigger-window behavior; inspect-only for exact test placement.
  - Green exit: tests fail for the current coarse `progress_line()` or pass as characterization where the existing collector contract is already correct.
  - Refactor obligation: no refactor before first green implementation; test helper extraction allowed only if it reduces duplicated fake snapshot setup.

- S02 Provider progress projection and two-stage rendering
  - Scope: provider `src/.../wait_pr_observation.sh`.
  - Closure ids: `cl-ci-detail`, `cl-ci-compact`, `cl-review-detail`, `cl-review-human-gate`, `cl-boundary`, `cl-truncation`.
  - Red / Green / Refactor: use one failing test at a time; green with `ci_progress_counts`, `review_progress_counts`, `progress_state`, and `render_progress_line`; refactor only to keep helper responsibilities separate.
  - Stop condition: needing new GitHub API calls, raw `gh` args, or collector schema expansion beyond minimal existing payload derivation.

- S03 Semantic fingerprint alignment
  - Scope: provider `semantic_fingerprint()`.
  - Closure ids: `cl-ci-quiet`, `cl-review-quiet`, `cl-raw-body-stability`.
  - Red / Green / Refactor: prove count changes reset quiet and no-change polls increase quiet; preserve raw-body-only stability expectations by fingerprinting sanitized progress-significant fields, not raw progress text.
  - Stop condition: fingerprint changes make historical body-only or stale-thread tests regress without a design/report decision.

- S04 Mirror sync and shipped asset parity
  - Scope: `.agents/.../wait_pr_observation.sh` plus parity evidence only.
  - Closure ids: `cl-provider-mirror-parity`, `cl-bash-compat`.
  - Red / Green / Refactor: no behavioral redesign in mirror; copy provider result, then prove exact parity and `bash -n` for both scripts.
  - Stop condition: provider/mirror mismatch after sync or Bash 3.2 syntax incompatibility.

- S90 Docs impact resolution
  - Scope: docs/templates/README/workflow/skill/migration notes impact decision.
  - Closure ids: `cl-docs-impact`.
  - Expected result: likely approved-no-op because public CLI names and docs contracts remain unchanged; if docs need updates, delegate to `doc-writer` and run `spec-reviewer`.

- S99 Final quality gate
  - Scope: whole issue diff and report closure.
  - Closure ids: all required closure ids.
  - Required gates: final `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`, final commit/report evidence, PR delivery and merge-preparation gates before issue finish.

# Test Strategy Mapping

- `cl-ci-detail`: focused pytest asserts stderr includes `pr_obs`, `ci=running`, `checks=2/4`, `ok=2`, `run=2`, `pend=0`, `fail=0`.
- `cl-ci-quiet`: focused pytest drives `checks=0/3 -> 1/3 -> 2/3 -> 3/3` and asserts final JSON `wait.latest_change_poll` plus stderr `quiet` reset.
- `cl-ci-compact`: focused pytest asserts terminal passed progress has `ci=passed` and normally omits detailed `checks=`.
- `cl-review-detail`: focused pytest drives trigger-window review signals `0 -> 1 -> 2` and asserts `comments=N`.
- `cl-review-quiet`: focused pytest asserts review comments / threads / unresolved count changes update `latest_change_poll`.
- `cl-review-human-gate`: focused pytest asserts stable unresolved / changes-requested compact output preserves human-gate counts.
- `cl-progress-none`: focused pytest asserts stderr is empty and stdout parses as final JSON under `--progress none`.
- `cl-boundary`: focused pytest asserts stdout is final JSON only and stderr omits body, URL, reviewer name, workflow name, job name, failed step detail, and P1/P2 text interpretation.
- `cl-truncation`: focused pytest asserts optional fields are dropped deterministically, `limit=truncated` appears only when needed, and normal output uses `limit=none`.
- `cl-provider-mirror-parity`: `diff -u src/.../wait_pr_observation.sh .agents/.../wait_pr_observation.sh`.
- `cl-bash-compat`: `bash -n` on provider and mirror scripts; inspect for Bash 3.2-incompatible parameter expansion if touched.
- `cl-docs-impact`: docs-only inspection plus `spec-reviewer` result if canonical/docs updates are made.

# Review Gates

- Per-step worker gate: S01-S04 should be delegated to `dev-coder` because the work touches runtime script behavior, tests, and shipped asset parity.
- Per-step reviewer gate: S01-S04 require fresh `code-reviewer` pass focused on projection correctness, quiet reset semantics, stdout/stderr separation, forbidden leakage, timeout/zero-check/stale review regression risk, and provider/mirror parity.
- S90 docs gate: if docs are unchanged, record approved-no-op rationale and request `spec-reviewer` docs/spec alignment check; if changed, delegate docs to `doc-writer` and then run `spec-reviewer`.
- S99 final QA gate: run `qa-reviewer` for obligation coverage and integration-test sufficiency.
- S99 final code gate: run issue-wide `code-reviewer` over the integrated diff after all fixes.
- S99 final spec gate: run final `spec-reviewer` against requirement, design, plan, report, implementation, tests, and docs impact evidence.
- PR / merge-preparation gate: after final commit gates, use the PR delivery and merge-preparation workflow; PR observation evidence must use stdout final JSON as authority, not stderr progress.

# Rollback / Compatibility

Rollback is a low-risk file revert: revert provider wait script, mirror wait script, and focused tests added for this issue. No data migration is needed because the issue must not add persisted schema, new CLI options, new GitHub API surface, or stdout final JSON authority changes.

Compatibility obligations:

- Keep `--progress stderr-summary` and `--progress none` names.
- Keep stdout as exactly one parseable final JSON result.
- Keep stderr progress non-authoritative and one line per poll.
- Keep check-run denominator as check runs only for the first implementation.
- Keep commit statuses / required-check rollup as CI status and limitation inputs, not `checks=done/total` denominator.
- Keep old unresolved threads out of `comments=N` while still allowing final review status / human gate to reflect thread state.
- Keep provider source as source of truth and mirror as exact dogfooding parity.

# Docs Impact

Expected docs impact is none or minimal. The public command surface does not change, and requirement/design already define the progress contract. S90 must still inspect docs, templates, README, workflow docs, skill text, and migration notes for stale `limit=ok`, coarse progress examples, or statements that contradict `limit=none|truncated`.

If stale docs are found, treat docs update as a separate `doc-writer` step with allowed docs paths and a `spec-reviewer` docs/spec alignment gate. Do not mix docs rewrite into the runtime implementation step.

# Final Quality Gate

Final exit requires:

- All closure ids pass or have approved-no-op evidence in `report.md`.
- Focused pytest for PR observation wait / review paths passes.
- `bash -n` passes for provider and mirror wait scripts.
- Provider/mirror `diff -u` is empty.
- `git diff --check` passes.
- S90 docs impact is resolved.
- Final `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer` pass.
- Final report records Red / Green / Refactor evidence, closure coverage, closure delta if any, delegation evidence, reviewer gate status, commit/no-op gates, PR delivery gate, and merge-preparation gate.
- Issue completion is not claimed until the workflow_issue completion requirements are met, including PR/merge-prepared evidence and lifecycle closure via the normal issue finish path.

# Plan Blockers

none

Potential amendment triggers:

- Existing snapshot payload cannot derive trigger-window `comments=N` without collector changes.
- Optional-field dropping cannot keep progress near the line budget without omitting required human-gate fields.
- Quiet reset changes regress existing timeout, zero-check, stale head, raw-body, or review collector semantics.
- Provider/mirror parity cannot be preserved because one side has environment-specific requirements.
- Any implementation requires a new GitHub API call, stdout schema authority change, or progress line containing forbidden detail.

# Integration Notes for Main Orchestrator

Adopt only the parts of this draft that match the latest canonical requirement/design and record adoption in `report.md` Evidence Adoption Ledger and Delegated Draft Evidence. A post-run diff guard should confirm that this delegated draft created exactly one discussion artifact and did not edit canonical docs, source, tests, config, or other files.

Recommended canonical plan shape: S01 tests, S02 provider projection/rendering, S03 fingerprint alignment, S04 mirror parity, S90 docs impact, S99 final quality gate. Keep the closure index in canonical `plan.md` stable; if implementation discovers a new obligation, amend the plan and re-run spec review before closing that obligation.

Leaf evidence used: approved requirement/design, report authoring gates, system-architect design draft, earlier implementation plan draft, provider/mirror wait wrapper function boundaries, nearby PR observation test surface, issue-plan closure semantics, workflow_issue execution/reviewer/completion policy, and phase_plan delegated plan authoring contract.

Forbidden actions avoided: no canonical edit, no source edit, no test edit, no config edit, no phase promotion, no reviewer-pass claim, no implementation-readiness claim, no user-dialogue ownership, no GitHub mutation.

Unresolved design gaps: none.

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
