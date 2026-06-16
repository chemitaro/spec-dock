---
created_by_role: system-architect
scope_id: iss-00187
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/.agent/active.json
  - spec-dock/active/initiative/requirement.md
  - spec-dock/active/initiative/design.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00187-actions-pr-observation-ci-state/discussions/20260615t154753z-01-research-actions-ci-observation-scope.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00187-actions-pr-observation-ci-state/discussions/20260615t154753z-02-interview-actions-only-pass-contract.md
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
  - .agents/skills/github-pr-observation/SKILL.md
  - .agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh
  - .agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh
  - .agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
  - tests/unit/infra/test_init_update.py
intended_targets:
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00187-actions-pr-observation-ci-state/design.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00187-actions-pr-observation-ci-state/plan.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00187-actions-pr-observation-ci-state/report.md
adoption_status: partially_adopted
reflected_to:
  - design.md
  - plan.md
  - report.md
diff_guard_result: passed
---

# PR Review Completion Signal Contract

## 1. Requirement Coverage

This draft covers a requirement gap discovered after the Actions-primary CI work in `iss-00187`: PR #190 at head `fc3041f86a7f9defba2d3fd8b48ff1c48126151a` had matching head and passed CI, but `wait_pr_observation.sh` timed out because Codex review lifecycle `completion_signal` stayed `none`. Earlier head `66c6a3be` produced `submitted_pull_request_review` plus unresolved threads, so the collector can detect formal PR review objects but not all terminal Codex no-findings forms.

Existing issue requirements intentionally excluded Codex review lifecycle changes while focusing on CI state. The observed failure shows that merge-preparation readiness is a joint contract: CI can be green and head-fresh, but the wait loop must still know whether the current Codex review attempt has terminally completed, needs repair, is still running, or is unobservable.

## 2. Existing Context Findings

- `spec-dock/active/context-pack.md` and `spec-dock/.agent/active.json` both identify active issue `iss-00187` under `epic-00158`.
- The parent epic requires agent-facing workflow hardening, explicit reviewer gates, evidence boundaries, provider-source authority, and dogfooding mirror verification.
- The issue requirement/design/plan establish Actions-primary CI observation, false-pass-safe JSON output, fixed script surfaces, provider source first, and fake `gh` regression tests.
- Existing discussions resolved that Actions-only green may return `ci.status="passed"` with explicit coverage limitation.
- `SKILL.md` currently documents Codex review completion as primarily detected from Codex-authored submitted PR review objects; issue comments remain fallback/supporting evidence and must not promote to passed.
- `fetch_pr_review_snapshot.sh` sets high-confidence completion only when `selected_review_signals` contains a Codex-authored submitted PR review. A current Codex issue comment becomes `completion_signal="fallback_issue_comment"` with low confidence. Missing formal or fallback evidence becomes `completion_signal="none"`.
- `fetch_pr_observation_snapshot.sh` and `wait_pr_observation.sh` preserve that distinction: `fallback_issue_comment` remains `human_gate` / `wait_or_resume`, and `missing_current_completion_signal` remains pending or non-complete.
- `tests/unit/infra/test_init_update.py` already protects the conservative behavior: fallback issue comments do not promote, missing current completion is not pass, and decision fingerprints override legacy audit noise.

## 3. Design Decisions

Recommended decision: split the overloaded review concept into three explicit axes.

1. `review.lifecycle.completion_signal`: whether the current Codex review attempt reached a terminal observable output.
2. `review.verdict`: what that output means for merge preparation: `no_findings`, `feedback_required`, `changes_requested`, `unresolved_threads`, `unknown`.
3. `review.evidence_transport`: where the signal was observed: `pull_request_review`, `pull_request_review_comment`, `issue_comment`, `review_thread`, `review_request`, `collection_failure`.

The current contract treats "submitted PR review object exists" as both completion and confidence. That is too narrow for no-findings Codex forms where the service may emit only a current-boundary no-findings issue comment. The fix should not make all issue comments high confidence. It should add one narrow, named terminal signal for the known no-findings form.

Recommended new completion signal:

- `codex_no_findings_issue_comment`

It should be terminal only when all of these are true:

- The comment is Codex-authored.
- It is in the explicit or inferred current trigger boundary.
- It is after the trigger instant and associated with the expected head boundary.
- The body matches a strict allow-list such as `No major issues found.` already recognized by `fallback_pass_candidate`.
- There are no current selected unresolved threads.
- There is no current selected changes-requested evidence.
- There is no blocking review collection failure.

Generic Codex issue comments such as progress text, partial summaries, ambiguous praise, or non-allow-listed text should remain `fallback_issue_comment` and should not promote to passed.

## 4. Alternatives Considered

- Keep current behavior and require a submitted PR review object.
  - Rejected for this issue context because PR #190 shows a green CI/head-matched/no-findings case can time out indefinitely when no submitted review object is posted.
- Promote all Codex-authored issue comments after the trigger.
  - Rejected as unsafe. Progress comments and ambiguous issue comments are not review completion evidence.
- Promote the existing `fallback_issue_comment` when it contains "No major issues found".
  - Not preferred because the field name already documents low confidence and existing tests assert it does not promote. Reusing it would blur the safety contract.
- Add a new terminal completion signal for strict no-findings issue comments.
  - Recommended. It keeps legacy fallback conservative while giving the no-findings form a clear, testable contract.

## 5. Boundary / Contract Model

The decision boundary should stay in `decision`, not in legacy `review.signals` or audit fields. Audit context may include historical unresolved threads, stale comments, or old Codex-authored items. Only current-boundary selected evidence may drive readiness.

Proposed top-level meanings:

| Signal | Confidence | Decision effect |
|---|---:|---|
| `submitted_pull_request_review` | high | May pass if CI passed and no selected blockers exist |
| `codex_no_findings_issue_comment` | medium-high | May pass if CI passed and no selected blockers exist |
| `fallback_issue_comment` | low | Stays `human_gate` / `wait_or_resume` |
| `none` | medium/low | Stays pending or timeout/resume |
| collection failure | low | `unknown` / `human_gate` unless classified as retryable |

Recommended status semantics:

- `decision.status="passed"` means review lifecycle is terminal for the current boundary and no current selected review blockers exist.
- `decision.status_reason="codex_no_findings_issue_comment"` means no formal PR review object was posted, but strict no-findings issue-comment evidence closed the current Codex review attempt.
- `decision.observation_complete=true` is allowed for this new signal only after CI is passed and review blockers are absent.
- `review.status` can remain explanatory and should not be the merge-readiness authority.

## 6. Dependency Analysis

Direct dependency chain:

1. `fetch_pr_review_snapshot.sh` produces `codex_review.lifecycle`, `decision`, selected blockers, and fallback candidate.
2. `fetch_pr_observation_snapshot.sh` merges CI, metadata, head freshness, and review decision.
3. `wait_pr_observation.sh` polls snapshots and terminates only when the merged decision is complete.
4. `tests/unit/infra/test_init_update.py` executes provider scripts with fake `gh` and is the correct regression lane.
5. `.agents/skills/github-pr-observation/...` mirrors provider assets and should be verified after provider changes.

The narrowest architecture change is in the review collector decision layer. Wrapper scripts should only need to accept `decision.status="passed"` / `recommended_next_action="merge_prepared"` when the new status reason is present. They should not parse raw comment body text themselves.

## 7. Source of Record

Provider source remains the authority:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`

Dogfooding copies under `.agents/skills/github-pr-observation/` are verification surfaces, not the implementation source of truth.

This draft is evidence only. It is not reflected to canonical docs and does not change the approved issue contract by itself.

## 8. Data Flow / Domain Model / Interface Contract

Proposed data flow:

```text
GitHub PR comments/reviews/threads
  -> fetch_pr_review_snapshot.sh
  -> codex_review.lifecycle + decision
  -> fetch_pr_observation_snapshot.sh
  -> normalized_status / recommended_next_action / observation_complete
  -> wait_pr_observation.sh
  -> final JSON / resume metadata
```

Proposed decision payload additions or clarified values:

```json
{
  "status": "passed",
  "status_reason": "codex_no_findings_issue_comment",
  "recommended_next_action": "merge_prepared",
  "observation_complete": true,
  "completion_signal": "codex_no_findings_issue_comment",
  "confidence": "medium-high",
  "selected_unresolved_count": 0,
  "selected_changes_requested_evidence": [],
  "fallback_pass_candidate": {
    "present": true,
    "source": "issue_comment",
    "promotes_top_level_status": true
  }
}
```

If changing `fallback_pass_candidate.promotes_top_level_status` would break its current semantics, introduce `no_findings_completion_candidate` instead and leave `fallback_pass_candidate` unchanged for backward compatibility.

## 9. File / Module Change Plan

Recommended implementation slices:

- S04: Review completion taxonomy.
  - Update provider `fetch_pr_review_snapshot.sh` so strict no-findings issue comments become `codex_no_findings_issue_comment`, not generic `fallback_issue_comment`.
  - Add fake `gh` tests for no PR review object + current Codex "No major issues found." issue comment + no selected blockers.
- S05: Snapshot/wait acceptance.
  - Ensure `fetch_pr_observation_snapshot.sh` and `wait_pr_observation.sh` pass through the new decision signal without reclassifying it as missing completion.
  - Add wrapper tests proving green CI + no-findings issue-comment completion reaches `merge_prepared`.
- S90 addendum: Documentation and mirror.
  - Update `SKILL.md` wording to distinguish submitted PR reviews, strict no-findings issue-comment completion, generic fallback issue comments, and non-promoting fallback candidates.
  - Sync/verify dogfooding mirror bytes for changed assets.

Keep all changes inside provider PR observation assets, dogfooding mirror, and focused tests. Do not broaden into trigger posting, arbitrary GitHub API inputs, branch protection reconstruction, or PR merge automation.

## 10. Migration / Compatibility / Rollback

Compatibility:

- Existing consumers using `decision.status` and `recommended_next_action` should continue to work.
- Existing tests expecting `fallback_issue_comment` to remain non-promoting should remain valid for generic or non-allow-listed issue comments.
- The new completion signal is additive. Consumers that only inspect `decision.status="passed"` should not need to know the transport.

Rollback:

- Revert the new signal classification and tests if it produces false pass.
- Because the change should be additive and isolated to PR observation assets, rollback does not require changing issue identity, CI Actions-primary behavior, or SpecDock canonical docs.

## 11. Observability

Final JSON should make the no-findings path inspectable without reading raw logs:

- `decision.status_reason="codex_no_findings_issue_comment"`
- `decision.completion_signal="codex_no_findings_issue_comment"`
- `codex_review.lifecycle.completion_signal` mirrors the same value.
- `decision.source` or candidate object includes issue-comment source IDs.
- `review.current` shows no selected unresolved threads or changes-requested evidence.
- `review.audit` remains non-authoritative and can still include historical artifacts.

Timeout output should explicitly show whether the blocker is `missing_current_completion_signal`, `fallback_issue_comment_low_confidence`, CI state, stale head, or collection failure.

## 12. Test Strategy

Add focused fake `gh` tests in `tests/unit/infra/test_init_update.py`.

Required cases:

- No PR review object, current Codex issue comment body exactly `No major issues found.`, no selected blockers: review collector emits `codex_no_findings_issue_comment` and decision passed.
- Same setup through `fetch_pr_observation_snapshot.sh` with CI passed: `normalized_status="passed"`, `recommended_next_action="merge_prepared"`, `observation_complete=true`.
- Same setup through `wait_pr_observation.sh`: wait terminates without timeout after stable fingerprint.
- Generic current Codex issue comment remains `fallback_issue_comment`, `human_gate`, `wait_or_resume`.
- Positive no-findings comment plus current selected unresolved thread remains `human_gate` / `address_review_feedback`.
- Positive no-findings comment plus selected changes-requested evidence remains `human_gate` / `address_review_feedback`.
- Missing current completion signal remains non-pass.
- Body-mode variants do not leak raw bodies unexpectedly and still preserve the sanitized source ID.
- Provider and dogfooding mirror changed assets match.

No network commands are needed for this test plan.

## 13. ADR Candidates

No global ADR is required if this remains an issue-local PR observation contract.

Create an ADR only if maintainers want a durable product-level policy for "machine-authored issue comments may represent formal review completion." If so, the ADR should explicitly define allowed transports, confidence levels, and why generic issue comments remain non-promoting.

## 14. Risks

- False pass risk if the no-findings body matcher is too broad.
- Boundary risk if comments from a previous trigger or previous head are treated as current.
- Actor risk if non-Codex users or renamed bots are misclassified as Codex-authored.
- Thread risk if unresolved current threads are present but not selected into decision evidence.
- Timeout risk if the new signal is emitted by the collector but wrappers continue to require `submitted_pull_request_review`.
- Backward compatibility risk if existing `fallback_issue_comment` semantics are changed instead of adding a distinct signal.

## 15. Requirement Clarification Requests

No blocking user clarification is required before drafting implementation design. The product-safe default is:

- strict no-findings Codex issue comments may complete review observation;
- generic fallback issue comments remain non-promoting;
- selected current blockers override no-findings completion.

Non-blocking clarification for the main orchestrator:

- Should the new signal name be `codex_no_findings_issue_comment` or a shorter `no_findings_issue_comment`?
- Should `confidence` be `medium-high` or one of the existing values only, such as `medium`?
- Should `fallback_pass_candidate.promotes_top_level_status` change for this path, or should a new `no_findings_completion_candidate` object avoid altering current semantics?

## 16. Integration Notes for Main Orchestrator

This evidence should be adopted as an addendum to `iss-00187` design/plan only if the main orchestrator agrees that the no-findings Codex review form is in scope for PR #190 completion. The adoption should preserve the existing CI Actions-primary contract and add review lifecycle work as a separate implementation slice after the current CI slices.

Suggested canonical integration:

- Add a design subsection for "Codex review completion signal taxonomy."
- Add plan steps S04/S05 or amend S03 only if implementation has not yet passed its review gate.
- Record this draft in `report.md` Evidence Adoption Ledger before canonical rewrite.
- Require fresh `spec-reviewer` review after any canonical change.

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
