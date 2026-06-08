---
created_by_role: system-architect
scope_id: iss-00174
source_paths:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/discussions/20260608t024500z-research-progress-line-two-stage-status-analysis.md
  - spec-dock/active/issue/discussions/20260608t025500z-interview-progress-review-comment-count.md
  - spec-dock/active/issue/discussions/20260608t030500z-disc-progress-line-two-stage-design-proposal.md
  - spec-dock/active/issue/discussions/20260608t031000z-disc-progress-line-two-stage-implementation-plan.md
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh
  - tests/unit/infra/test_init_update.py
intended_targets:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
  - .agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
  - tests/unit/infra/test_init_update.py
adoption_status: unreviewed
reflected_to: []
diff_guard_result: passed
---

# Requirement Coverage

iss-00174 is approved and asks for stderr progress only: `wait_pr_observation.sh --progress stderr-summary` must expose useful polling progress while stdout remains the final authoritative JSON. The design below covers the required two-stage progress line, CI check counters, review comment counters, quiet reset semantics, stdout/stderr separation, provider/mirror parity, truncation behavior, and focused regression tests.

No requirement blocker remains. The earlier ambiguity around `comments=N` is answered: it means Codex review comments / review signals newly captured after the `@codex review` trigger within the current observation window, not all historical PR comments or old unresolved threads.

# Existing Context Findings

The current `wait_pr_observation.sh` computes a semantic fingerprint and quiet window, then emits a coarse progress line with only `poll`, `elapsed`, `remain`, `phase`, `ci`, `review`, `quiet`, `limit=ok`, and `final=stdout_json`. That line is sliced to 240 characters and has no projection layer.

The checks collector already exposes `ci.check_runs` counts including `total`, `success`, `skipped`, `neutral`, `failed`, `running`, `pending`, `other`, and `stale`. The review collector already exposes `review.signals`, `review.codex_authored`, `review.summary`, and `review.threads`. Therefore the smallest architecture change is in the wait wrapper: derive progress counters from existing snapshot payloads instead of adding new GitHub API calls.

The current wait fingerprint includes CI status and failures, but not CI check-run count progress. Review fingerprint coverage is broader because it includes sanitized signals, summary, threads, body mode, and the collector fingerprint. This explains why CI can remain `running` while `checks=1/4 -> 2/4` is invisible to quiet reset.

# Design Decisions

Add a small progress projection inside the Python block of `wait_pr_observation.sh`. The projection should be separate from rendering and semantic fingerprinting, but both should consume the same progress-significant counters so stderr visibility and quiet reset semantics do not drift.

CI display is detailed while CI is non-terminal or still waiting: `ci=running checks=2/4 ok=2 run=2 pend=0 fail=0`. CI display is compact when terminal passed: `ci=passed`. Failed CI may keep `fail=N` as a compact human-action hint, but must not expose workflow name, job name, URL, or failed step details in stderr.

Review display is detailed while observation is not complete: `review=observing comments=N threads=N unresolved=N`. After stable completion, compact to the current review status. For human gates such as `unresolved`, `changes_requested`, or `commented`, keep minimal count fields that explain the gate.

Use `limit=none` for the normal path. Use `limit=truncated` only when deterministic optional-field dropping was needed. Do not keep `limit=ok` as the normal value.

# Alternatives Considered

Extending collectors to add progress-only fields was considered but is not the first choice. The collectors already expose enough structured data, and progress rendering is a wait-loop concern.

Expanding stdout final JSON with progress-specific schema was considered unnecessary. The final JSON already contains authoritative CI/review state; progress is an observation aid and should not become a second decision authority.

Emitting event-style deltas for every quiet reset was considered too noisy for the one-line stderr contract. The chosen design makes reset causes inferable through visible counters instead.

String slicing the rendered line was rejected as the normal truncation mechanism because it can cut tokens and hide boundary evidence. It can remain only as a defensive last resort after optional field dropping.

# Boundary / Contract Model

stdout is reserved for exactly one parseable final JSON result. stderr progress is non-authoritative, bounded, one line per poll, and omitted entirely under `--progress none`.

The progress line is a key/value current-state summary. It may expose counts and compact statuses, but not raw review body, URL, reviewer name, workflow name, job name, failed step detail, or P1/P2 text interpretation.

The projection contract should be internal to `wait_pr_observation.sh`. It should not accept arbitrary GitHub query inputs, raw `gh` arguments, custom endpoints, or user-provided jq expressions.

# Dependency Analysis

`wait_pr_observation.sh` depends on `fetch_pr_observation_snapshot.sh`, which composes fixed read-only CI and review collectors. The progress design should preserve that dependency direction.

Provider source of record is `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`. The dogfooding mirror `.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh` must match after implementation.

Tests live in `tests/unit/infra/test_init_update.py`, where fake `gh` harnesses already cover PR observation collectors, wait behavior, stdout/stderr capture, and checked-in runtime mirror parity.

# Source of Record

Canonical requirement source is `spec-dock/active/issue/requirement.md` at working-tree HEAD `da315d32`, with issue status `approved` and last update `2026-06-08`.

This discussion is unreviewed architecture evidence only. It does not update canonical `requirement.md`, `design.md`, `plan.md`, or `report.md`.

# Data Flow / Domain Model / Interface Contract

Data flow: fixed GitHub collectors produce snapshot JSON; the wait loop classifies the snapshot, computes semantic fingerprint and quiet state, projects progress state, renders stderr if enabled, and finally writes stdout JSON once.

Progress projection fields should include CI status, done/total check counts, success-like count, running, pending, failed, optional other/stale, review status, trigger-window Codex comment/signal count, thread count, unresolved count, limitation count, same fingerprint count, same fingerprint requirement, and final line limit state.

`checks=done/total` uses GitHub check runs as the denominator for the first implementation. Commit statuses and required-check rollup remain inputs to CI status and limitations, not the denominator.

`comments=N` should count trigger-window Codex review comments / review signals. It should exclude the trigger command itself, old PR-wide comments, and unrelated historical unresolved threads.

# File / Module Change Plan

Implementation should first add focused red tests in `tests/unit/infra/test_init_update.py` around the existing PR observation test area.

Then change provider `wait_pr_observation.sh` by adding pure helper functions for CI counts, review counts, progress state, and line rendering. Update `semantic_fingerprint()` to include progress-significant CI counts and the review projection counts that explain quiet reset.

After provider changes pass focused tests, mirror the same script into `.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh` and verify parity. No collector change is expected unless implementation proves a missing review count cannot be derived from existing payload shape.

# Migration / Compatibility / Rollback

The external CLI options remain compatible: `--progress stderr-summary` and `--progress none` keep their current names and stdout final JSON remains parseable.

The observable stderr content changes from coarse to richer key/value output. Consumers must not parse stderr as authority, but tests should pin the fields required by iss-00174.

Rollback is low-risk: revert the wait wrapper and mirror changes plus focused tests. Because no new persisted schema or GitHub query surface is introduced, rollback should not require data migration.

# Observability

The progress line should begin with `pr_obs` so human and agent logs can distinguish it from subprocess stderr. It should keep `final=stdout_json` to reinforce the authority boundary.

Quiet reset observability comes from visible counters moving in the same categories included in the fingerprint: CI counts, review comments, threads/unresolved counts, limitation count/codes, and status transitions.

Optional event output under `--out events.ndjson` may later include compact progress state, but iss-00174 should not depend on that schema.

# Test Strategy

Add focused tests for CI running detail, CI count progress resetting quiet, CI passed compact output, review observing comment count growth, review human-gate compact counts, `--progress none`, stdout/stderr separation, forbidden token absence, truncation with `limit=truncated`, and provider/mirror parity.

Use fake snapshot or fake `gh` fixtures already established in `tests/unit/infra/test_init_update.py`. Assertions should verify stdout parses as JSON and stderr contains only progress lines when enabled.

Verification commands after implementation should include focused pytest for PR observation wait/review paths, `bash -n` for provider and mirror wait scripts, `diff -u` for provider/mirror parity, and `git diff --check`.

# ADR Candidates

An ADR is probably unnecessary if the final design only changes internal wait wrapper projection and stderr rendering.

Create an ADR only if the team decides to make progress projection a stable public contract, add progress schema to final JSON/events, or change the collector contract to emit dedicated progress fields.

# Risks

Review count drift is the highest semantic risk. The implementation must preserve the answered definition of `comments=N` and not count stale historical feedback as current review progress.

Fingerprint/projection drift can reintroduce confusing quiet resets. Tests should cover that CI count changes and review count changes both update `wait.latest_change_poll`, while no-change polls allow quiet to grow.

Line length pressure can hide important fields. The renderer should drop optional fields in a deterministic order and mark `limit=truncated`, instead of slicing the normal line.

Provider/mirror skew is a release risk because agent-tooling assets are installed from provider source but dogfooding validates the checked-in mirror.

# Requirement Clarification Requests

none

# Integration Notes for Main Orchestrator

Adopt this draft into canonical design only after main-orchestrator review. The final design should state that progress projection is internal, stdout remains authoritative, and no new GitHub API call is introduced.

The implementation handoff should ask dev-coder to work provider first, update the mirror second, and keep tests focused in `tests/unit/infra/test_init_update.py`. A fresh code-reviewer pass should specifically inspect progress projection correctness, quiet reset semantics, stdout/stderr boundary, forbidden stderr leakage, and parity evidence.

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
