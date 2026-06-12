---
種別: draft-design
ID: "20260612t015200z-draft-design"
タイトル: "PR observation boundary design draft"
状態: "draft"
created_by_role: "system-architect"
scope_id: "iss-00182"
source_paths:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/discussions/20260612t012333z-research-pr-observation-final-output-boundary-analysis.md
  - spec-dock/active/issue/discussions/20260612t014627z-interview-fallback-issue-comment-decision-boundary.md
intended_targets:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
authority: "proposed"
adoption_status: "unreviewed"
reflected_to: []
diff_guard_result: "pass_orchestrator_review"
---

# PR observation boundary design draft

## 1. Requirement Coverage

This draft proposes an additive output contract for `iss-00182`: final PR observation decisions are based only on current trigger / resume boundary artifacts, while historical and all-fetched review context remains available as explicitly scoped audit evidence.

Traceability:

- AC-001: move final decision inputs to `review.decision` / top-level `decision` surfaces and keep historical unresolved threads under an all-fetched audit surface.
- AC-002: represent current selected unresolved review thread ids in the decision surface and keep top-level `human_gate` / `address_review_feedback` when those ids are present.
- AC-003: preserve `fallback_issue_comment` as top-level `human_gate` / `wait_or_resume`, not `passed` / `merge_prepared`.
- AC-004: add an explicit `fallback_pass_candidate` signal when the current boundary fallback issue comment indicates no major issues.
- AC-005: split decision and audit fingerprints; wait stability uses the decision fingerprint.
- AC-006: update shipped skill semantics in `SKILL.md` so final decision, current boundary evidence, historical context, fallback semantics, and fingerprints are documented.

Edge coverage:

- EC-001: inferred trigger boundaries stay explicit through `trigger.source`, limitations, and decision source metadata.
- EC-002: no current review completion signal and no fallback comment remains safe-side `pending` / `wait` or `human_gate`, with a reason.
- EC-003: current selected unresolved thread drives final decision; historical thread remains audit-only.
- EC-004: legacy `review.threads` / `review.codex_authored` remain present with scope metadata to reduce breaking risk.

## 2. Existing Context Findings

The existing collector already has part of the correct boundary model:

- `fetch_pr_review_snapshot.sh` marks `current_status_signal` and computes selected review ids, selected review comment ids, selected review thread ids, and current unresolved thread ids.
- `codex_review.collection_summary.review_threads` already summarizes selected / current boundary thread state.
- `fetch_pr_observation_snapshot.sh` and `wait_pr_observation.sh` both intentionally classify `completion_signal == "fallback_issue_comment"` as `human_gate` / `wait_or_resume`.

The design gap is output and stability scope:

- `review.threads` contains all GraphQL threads and exposes all-fetched unresolved counts next to decision-facing fields.
- `review.codex_authored` contains all Codex-authored signals, not only current decision artifacts.
- `fetch_pr_review_snapshot.sh` exposes one `fingerprint` that includes all signals / all threads.
- `fetch_pr_observation_snapshot.sh` uses that review fingerprint in the top-level fingerprint.
- `wait_pr_observation.sh` computes `semantic_fingerprint()` from `review.threads`, `review.signals`, and `codex_review.collection_summary`, so historical-only changes can affect wait stability.
- `wait_pr_observation.sh` progress counts read `review.threads.total` and `review.threads.unresolved`, which are all-fetched counts.

## 3. Design Decisions

### Decision 1: Add authoritative decision surfaces

Add a decision-facing object that is the primary source for final classification:

```json
{
  "decision": {
    "scope": "current_trigger_boundary",
    "status": "human_gate",
    "status_reason": "fallback_issue_comment_low_confidence",
    "recommended_next_action": "wait_or_resume",
    "selected_review_ids": [],
    "selected_review_comment_ids": [],
    "selected_review_thread_ids": [],
    "selected_unresolved_thread_ids": [],
    "selected_unresolved_count": 0,
    "completion_signal": "fallback_issue_comment",
    "confidence": "low",
    "fallback_pass_candidate": {
      "present": true,
      "source": "issue_comment",
      "source_ids": [4683116317],
      "reason": "current_boundary_no_major_issues_comment",
      "promotes_top_level_status": false
    },
    "fingerprint": "<decision_fingerprint>"
  }
}
```

The same object may also be exposed as `review.decision` for locality with existing review output. Top-level `status`, `overall_status`, `normalized_status`, `observation_complete`, and `recommended_next_action` should be derived from this decision surface plus CI/head/limitations state.

### Decision 2: Preserve legacy debug fields additively

Do not remove `review.threads`, `review.signals`, or `review.codex_authored` in this issue. Mark them with explicit scope metadata:

```json
{
  "review": {
    "threads": {
      "scope": "all_fetched",
      "decision_authoritative": false,
      "total": 3,
      "unresolved": 1,
      "items": []
    },
    "codex_authored": {
      "scope": "all_fetched",
      "decision_authoritative": false,
      "items": []
    }
  }
}
```

If changing `review.codex_authored` from list to object is too disruptive, keep the list and add sibling metadata such as `review.codex_authored_scope: "all_fetched"` and `review.codex_authored_decision_authoritative: false`.

### Decision 3: Add current and audit surfaces

Use three surfaces with stable meanings:

- `decision`: final classification input, current boundary only.
- `review.current`: current boundary review artifacts used to explain the decision.
- `review.audit` or `review.history`: all-fetched / historical context for debug and traceability.

The authoritative fields should prefer additive aliases first:

```json
{
  "review": {
    "decision": {},
    "current": {
      "scope": "current_trigger_boundary",
      "signals": [],
      "codex_authored": [],
      "selected_reviews": [],
      "selected_review_comments": [],
      "selected_thread_ids": [],
      "selected_unresolved_thread_ids": []
    },
    "audit": {
      "scope": "all_fetched",
      "signals": [],
      "codex_authored": [],
      "threads": {},
      "fingerprint": "<audit_fingerprint>"
    }
  }
}
```

### Decision 4: Split fingerprints by purpose

Define:

- `decision_fingerprint`: current-boundary decision artifacts only. Used by top-level `fingerprint` and wait stability.
- `audit_fingerprint`: all-fetched debug / historical context. May change when historical threads update.
- `collector_fingerprint`: optional compatibility alias if retaining existing collector-wide behavior is useful.

Top-level `fingerprint` should become the decision fingerprint or an alias of it. If that is too risky for existing consumers, add `decision_fingerprint` first and make `wait_pr_observation.sh` use it while documenting the transition.

### Decision 5: Option C for fallback issue comments

Keep top-level behavior unchanged:

- `status`: `human_gate`
- `overall_status`: `human_gate`
- `normalized_status`: `human_gate`
- `recommended_next_action`: `wait_or_resume`
- `observation_complete`: `false`

Add a non-promoting signal under `decision` and/or `codex_review.lifecycle`:

```json
{
  "codex_review": {
    "lifecycle": {
      "completion_signal": "fallback_issue_comment",
      "fallback_pass_candidate": {
        "present": true,
        "reason": "current_boundary_no_major_issues_comment",
        "promotes_top_level_status": false
      }
    }
  }
}
```

This allows users and downstream agents to distinguish "human gate because only low-confidence fallback exists" from "human gate because current selected unresolved feedback exists."

## 4. Alternatives Considered

- Move all historical fields out of `review` immediately.
  - Rejected for this issue because existing debug consumers may read `review.threads` and `review.codex_authored`.
- Keep current mixed output and only change documentation.
  - Rejected because AC-001 and AC-005 require machine-readable decision / fingerprint separation.
- Promote no-major-issues fallback issue comments to pass.
  - Rejected by adopted Option C; submitted PR review remains the primary completion source.
- Keep one fingerprint and filter only progress text.
  - Rejected because wait stability would still be affected by audit-only changes.

## 5. Boundary / Contract Model

Final decision surface:

- Inputs: head match, CI status, blocking limitations, current boundary lifecycle, selected current review ids, selected current review comment ids, selected current thread ids, selected current unresolved count, fallback issue comment classification.
- Outputs: top-level status, normalized status, overall status, recommended action, observation complete, status reason, decision fingerprint.

Current surface:

- Inputs: artifacts after the current trigger / resume boundary or inferred boundary.
- Outputs: selected current signals, selected reviews, selected review comments, selected thread ids, current fallback issue comments, current collection summary.

History / audit surface:

- Inputs: all fetched signals, all fetched review threads, all Codex-authored artifacts, review requests, raw collection summaries.
- Outputs: debug context, audit fingerprint, all-fetched counts, historical ids, non-authoritative provenance.

Contract invariant:

- No field that can be mistaken for final decision-facing count should expose historical counts without `scope: "all_fetched"` or an equivalent explicit scope marker.

## 6. Dependency Analysis

This issue is under the installed layout epic, so implementation source-of-truth remains `src/spec_dock/assets/install_root/`.

Direct files and responsibilities:

- `fetch_pr_review_snapshot.sh`: collector-side boundary modeling, output shape, selected/current/audit grouping, fallback candidate detection, collector fingerprints.
- `fetch_pr_observation_snapshot.sh`: one-shot snapshot classification and top-level decision derivation.
- `wait_pr_observation.sh`: wait-loop classification, decision fingerprint stability, progress rendering, timeout/resume payload.
- `SKILL.md`: public output semantics and non-authoritative progress/audit documentation.

No installer, package, GitHub workflow, `.agents` metadata, `.codex`, or `.github` structural change is required by this issue.

## 7. Source of Record

Primary requirement source:

- `spec-dock/active/issue/requirement.md`

Evidence sources:

- `spec-dock/active/issue/discussions/20260612t012333z-research-pr-observation-final-output-boundary-analysis.md`
- `spec-dock/active/issue/discussions/20260612t014627z-interview-fallback-issue-comment-decision-boundary.md`

Parent architecture source:

- `spec-dock/active/epic/requirement.md`
- `spec-dock/active/epic/design.md`

Provider-side implementation source-of-truth:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`

## 8. Data Flow / Domain Model / Interface Contract

Proposed flow:

1. `fetch_pr_review_snapshot.sh` collects all review context.
2. It computes current boundary selected artifacts and all-fetched audit artifacts separately.
3. It emits `review.decision`, `review.current`, `review.audit`, `codex_review.lifecycle`, `decision_fingerprint`, and `audit_fingerprint`.
4. `fetch_pr_observation_snapshot.sh` reads the decision surface, merges it with CI/head/limitations, and emits top-level status and action.
5. `wait_pr_observation.sh` reads the decision fingerprint for stable wait and renders progress from decision/current counts.
6. `SKILL.md` defines which surfaces are authoritative and which are audit-only.

Interface contract:

- `decision.scope` is `current_trigger_boundary` or `inferred_current_boundary`.
- `review.audit.scope` is `all_fetched`.
- `fallback_pass_candidate.present == true` never implies top-level pass in this issue.
- `decision.selected_unresolved_count` is authoritative for review-feedback blocking.
- `review.threads.unresolved` is audit-only unless explicitly marked as decision-scoped.
- `decision_fingerprint` excludes historical-only updates.
- `audit_fingerprint` may include historical-only updates.

## 9. File / Module Change Plan

`fetch_pr_review_snapshot.sh`:

- Add helpers to build `decision`, `current`, and `audit` payloads from existing selected/current/all-fetched collections.
- Add `selected_unresolved_thread_ids` and `selected_unresolved_count` to the decision surface.
- Add scope metadata to legacy all-fetched fields.
- Add `fallback_pass_candidate` detection for current boundary Codex issue comments whose body indicates no major issues, using a narrow phrase whitelist.
- Emit `decision_fingerprint` from current decision inputs only.
- Emit `audit_fingerprint` from all-fetched review context.

`fetch_pr_observation_snapshot.sh`:

- Prefer `review.decision` or top-level `decision` over mixed `review.status`.
- Preserve `fallback_issue_comment` as `human_gate` / `wait_or_resume`.
- Set `status_reason` / `decision.status_reason` to distinguish fallback confidence, current selected unresolved thread, changes requested, stale head, CI failure, and blocking limitations.
- Use `decision_fingerprint` in top-level fingerprint source.

`wait_pr_observation.sh`:

- Update `semantic_fingerprint()` to prefer `decision_fingerprint` or reconstruct from decision surface only.
- Update `review_progress_counts()` to use decision/current selected counts by default.
- If audit counts are rendered, label them as audit-only; otherwise omit them from progress.
- Keep timeout/resume metadata unchanged except for fingerprint names.

`SKILL.md`:

- Add output semantics for final decision, current surface, audit surface, fallback issue comment Option C, and fingerprint separation.
- State that `stderr` progress is non-authoritative and decision-scoped.

## 10. Migration / Compatibility / Rollback

Migration:

- Prefer additive fields first: `decision`, `review.decision`, `review.current`, `review.audit`, `decision_fingerprint`, `audit_fingerprint`.
- Keep legacy `review.threads`, `review.signals`, and `review.codex_authored` available.
- Add scope markers to legacy fields instead of deleting or moving them in the first change.
- Keep existing top-level status values and action values.

Compatibility:

- Existing consumers reading top-level status should see the same status class in fallback cases.
- Existing debug tooling can still inspect all-fetched threads.
- Consumers that need authoritative decision counts should move to `decision.selected_unresolved_count`.

Rollback:

- If new surfaces cause consumer breakage, top-level classification can keep using the old fields while leaving the additive fields present.
- If `decision_fingerprint` causes unexpected wait behavior, retain both fingerprints and switch wait stability back only as a temporary rollback, with AC-005 marked unfulfilled.

## 11. Observability

Final JSON should expose:

- `decision.status_reason`
- `decision.source_ids` or selected ids
- `decision.selected_unresolved_count`
- `decision.fallback_pass_candidate`
- `decision_fingerprint`
- `audit_fingerprint`
- `review.current.scope`
- `review.audit.scope`
- legacy field scope metadata

Wait events / final wait JSON should expose:

- fingerprint used for stability
- same fingerprint count based on decision fingerprint
- progress counts from current decision surface
- audit-only counts only when explicitly labeled

No new external telemetry is required.

## 12. Test Strategy

Focused tests should cover output contract and classification:

- Historical unresolved thread before trigger plus current fallback issue comment:
  - top-level `human_gate` / `wait_or_resume`
  - `decision.selected_unresolved_count == 0`
  - `fallback_pass_candidate.present == true` when body matches no-major-issues
  - historical unresolved thread appears only under audit/all-fetched scope
- Current selected unresolved review thread:
  - top-level `human_gate`
  - action `address_review_feedback`
  - selected thread id and unresolved id appear in decision/current surface
- Fallback issue comment without no-major-issues body:
  - top-level remains `human_gate` / `wait_or_resume`
  - `fallback_pass_candidate.present == false`
- Historical-only thread update:
  - `decision_fingerprint` stable
  - `audit_fingerprint` may change
  - wait same-fingerprint count is not reset by audit-only change
- No current review completion signal:
  - no pass
  - reason points to missing completion signal or pending lifecycle
- Scope compatibility:
  - legacy `review.threads` / `review.codex_authored` remain present and marked all-fetched or non-authoritative.

Verification lanes:

- Unit tests around collector payload construction.
- CLI runtime tests for snapshot JSON.
- Wait-loop tests for fingerprint stability and progress rendering.
- Documentation/spec review for `SKILL.md` semantics.

## 13. ADR Candidates

Potential ADR, not mandatory for this issue:

- "Submitted PR review remains the primary completion source; issue comments are fallback evidence and do not independently make PR observation pass."

This becomes ADR-worthy if future work considers promoting `fallback_issue_comment` from candidate signal to pass-equivalent decision input.

## 14. Risks

- Scope metadata can be missed by consumers if legacy fields remain visually prominent.
- A narrow no-major-issues classifier may miss equivalent Codex wording.
- A broad no-major-issues classifier can create false confidence; keep it non-promoting.
- Changing top-level `fingerprint` semantics may surprise consumers that expected audit changes to reset stability.
- If both `decision` and `review.decision` are emitted, drift between aliases must be avoided by constructing one object and reusing it.

## 15. Requirement Clarification Requests

None.

The requirement already adopts Option C for `fallback_issue_comment`, fixes additive migration preference, and states no unresolved items.

## 16. Integration Notes for Main Orchestrator

Recommended canonical design integration:

- Adopt the three-surface model: final decision, current boundary, audit/history.
- Make `decision.selected_unresolved_count` and selected ids authoritative for AC-001 to AC-003.
- Place `fallback_pass_candidate` under `decision` and mirror it under `codex_review.lifecycle` only if compatibility/readability requires it.
- Define `decision_fingerprint` as the wait stability fingerprint.
- Keep legacy all-fetched fields with explicit scope metadata in the first implementation.
- Ensure `SKILL.md` names the authoritative surfaces so downstream agents do not infer status from all-fetched historical counts.

Unresolved blockers: none.

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
