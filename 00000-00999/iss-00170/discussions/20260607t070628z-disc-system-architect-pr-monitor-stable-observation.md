---
created_by_role: spec-dock-system-architect
scope_id: iss-00170
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/discussions/20260607t063203z-research-gpt55-pr-monitor-stable-observation-discussion.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/workflow_clarification.md
  - spec-dock/docs/phase_requirement.md
  - spec-dock/docs/phase_design.md
  - spec-dock/docs/reference_sync.md
  - src/spec_dock/assets/install_root/.codex/agents/pr-monitor.toml
  - src/spec_dock/assets/install_root/.github/agents/pr-monitor.agent.md
  - .codex/agents/pr-monitor.toml
  - .github/agents/pr-monitor.agent.md
  - src/spec_dock/assets/install_root/.agents/skills/github-codex-pr-review-comments/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/github-codex-pr-review-comments/scripts/fetch_codex_pr_review_comments.sh
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md
  - tests/unit/infra/test_init_update.py
intended_targets:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
adoption_ledger_note: Main orchestrator must decide adoption in canonical report.md.
---

# System Architect Draft: PR Monitor Stable Observation

This is a delegated architecture draft for `iss-00170`. It is proposed evidence only. Canonical `requirement.md`, `design.md`, `plan.md`, and `report.md` remain owned by the main orchestrator.

## 1. Requirement Coverage

- AC-001 / AC-002: Bind every final observation to the current or expected PR head SHA. If `head_sha` is provided and differs from the current PR head SHA, return a non-success `normalized_status=stale_head` and do not reuse old snapshots.
- AC-003 / AC-004: Treat checks and commit statuses as a combined observation surface. A zero-check result is not immediate success; it remains `pending` or `unknown` until the initial grace/deadline rule is satisfied.
- AC-005 / AC-006: Separate all review signals from Codex-authored subsets, and require stable review snapshot fingerprints across repeated polls plus a minimum quiet window.
- AC-007 / AC-008 / AC-009: `CHANGES_REQUESTED`, unresolved actionable threads, and missing thread visibility when comments exist are non-success states. Thread state absence must be machine-readable and cannot be collapsed into "no review feedback".
- AC-010: Provider-side source of truth remains `src/spec_dock/assets/install_root/`; checked-in dogfooding mirrors under `.agents`, `.codex`, and `.github` must be parity-verified.
- EC-001 through EC-005 are covered by the same contract: late review comments, mixed check/status sources, head SHA changes, resolved/outdated threads, and optional check failures remain distinguishable in output.

Requirement gaps blocking design: none observed. Non-blocking design defaults remain for exact quiet-window seconds, requested reviewer waiting policy, expected check names, and exact GraphQL pagination shape.

## 2. Existing Context Findings

- Active context is `initiative=init-local-00003`, `epic=epic-00067`, `issue=iss-00170`; the context pack states active authority exists but also warns that proposed or missing authority cannot authorize implementation or phase completion.
- The active issue `design.md` and `plan.md` are scaffold-level drafts. They do not yet encode the stable observation contract.
- Existing provider and dogfooding `pr-monitor` instructions already enforce a read-only monitor role, repo-relative wrapper use, no direct `gh api` fallback, no GraphQL fallback, and no write operations.
- Existing `pr-monitor` instructions define completion as "checks/statuses and review are both available", but do not define fingerprint stability, quiet window, snapshot reset, or final SHA binding.
- Existing `fetch_codex_pr_review_comments.sh` is a fixed REST GET wrapper for issue comments, review comments, and reviews. It validates `--repo` and `--pr`, does not accept endpoint/method/query passthrough, and outputs raw arrays plus a Codex subset.
- Existing wrapper output lacks `all` namespace, review thread state, reviewDecision, reviewRequests, head SHA binding, check/status normalization, pagination completeness metadata, and observation completeness flags.
- `github-pr-merge-preparer` already treats monitor output as stale when not for the latest head SHA and requires known unresolved-thread state or an explicitly waived limitation before reporting `merge-prepared: yes`.
- `tests/unit/infra/test_init_update.py` already has useful regression anchors: dogfooding parity, pr-monitor helper path guidance, fixed REST GET wrapper safety, and unsafe input rejection.

## 3. Design Decisions

1. Make `StablePrObservation` a deterministic wrapper output contract, not only a prompt instruction.
   - Rationale: stable fingerprinting, taxonomy, and completeness flags are shallow if left only in agent prose. The wrapper should produce the structured evidence; `pr-monitor` should poll, compare snapshots, summarize, and apply deadline policy.

2. Keep `fetch_codex_pr_review_comments.sh` as the existing Codex-focused read-only wrapper.
   - Rationale: it is a known safe boundary with tests and existing consumers. Changing it into a broad PR-observation wrapper risks mixing Codex-only report behavior with all-review/check/status observation behavior.

3. Add a new fixed read-only stable observation wrapper rather than extending the old wrapper in place.
   - Proposed name: `fetch_pr_stable_observation.sh`.
   - Proposed location: `src/spec_dock/assets/install_root/.agents/skills/github-codex-pr-review-comments/scripts/fetch_pr_stable_observation.sh`, mirrored to `.agents/...` by update/parity.
   - Boundary: fixed read-only calls only; no caller-provided method, endpoint, GraphQL query, headers, body, `jq`, or mutation flags.

4. Use the latest PR head SHA as the observation key.
   - `expected_head_sha` is an input field, but the wrapper must always report `current_head_sha`.
   - If expected/current differ, the wrapper may still collect current facts, but `observation_complete=false` and `normalized_status=stale_head` should dominate final monitor interpretation.

5. Preserve `overall_status` for compatibility and add `normalized_status` plus `observation_complete`.
   - Existing coarse values remain: `success`, `failed`, `review_changes_requested`, `timeout`.
   - New normalized values carry the precise reason: `success`, `pending`, `check_failed`, `review_changes_requested`, `review_state_unknown`, `stale_head`, `timeout`, `observation_unknown`.

6. Treat missing observation surfaces as `unknown`, not success.
   - Missing checks/statuses, review collection, review thread visibility, wrapper failure, auth failure, rate limit, schema mismatch, and null status/conclusion must set `observation_complete=false`.

## 4. Alternatives Considered

- Prompt-only hardening:
  - Rejected as insufficient for this issue. It improves agent behavior but does not make stable observation deterministic or testable.

- Extend `fetch_codex_pr_review_comments.sh` in place:
  - Partially viable, but not preferred. The old wrapper name and report are Codex-focused. Adding checks/statuses/head-SHA/thread taxonomy there would make deletion and responsibility boundaries unclear.

- Three separate wrappers for PR metadata, checks/statuses, and reviews/threads:
  - Viable for implementation if the scripts stay fixed and read-only. The design preference is one public stable-observation wrapper that may internally call small fixed helpers, so `pr-monitor` has one stable contract to poll.

- Use arbitrary `gh api graphql` from the agent:
  - Rejected. It violates the existing safety boundary and requirement prohibition. If GraphQL is needed for `reviewThreads`, the query must be fixed inside the wrapper.

- Let `github-pr-merge-preparer` own stable observation:
  - Rejected. It would duplicate policy across callers and blur the existing coordinator/monitor split. The preparer should consume monitor evidence and decide repair/human gate flow.

## 5. Boundary / Contract Model

- `pr-monitor`:
  - Owns read-only polling, bounded timeout, head-change handling, snapshot comparison, summary, and final human-readable handoff.
  - Must not merge, push, comment, reply, resolve threads, dismiss reviews, close issues, change labels/statuses, or delegate repairs.

- stable observation wrapper:
  - Owns fixed GitHub data collection and normalized machine-readable snapshot production.
  - Does not decide whether to repair, push, merge, waive optional checks, or finish an issue.

- existing Codex review wrapper:
  - Continues to own Codex-authored issue comments, inline comments, and review bodies via fixed REST GET.
  - May remain as a component or compatibility output source, but should not become the only source for all review/thread state.

- `github-pr-merge-preparer`:
  - Owns PR creation/discovery coordination, monitor invocation with latest head SHA, bounded repair delegation, re-push confirmation, re-monitoring, and final `merge-prepared` or human gate reporting.
  - It consumes `normalized_status`, `observation_complete`, `head_sha`, and limitation fields; it does not collect lower-level review/check data itself.

## 6. Dependency Analysis

- Upstream requirement source: `iss-00170` requirement defines head-SHA binding, stable snapshots, all/Codex review separation, read-only wrappers, and compatibility.
- Parent architecture source: `epic-00067` fixes `src/spec_dock/assets/install_root/` as provider-side source of truth and structure-preserving sync to consumer mirrors.
- Existing test dependency: `test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets` can catch provider/mirror drift if new wrapper and agent files are mirrored.
- Existing safety dependency: `test_issue_75_pr_review_wrapper_uses_fixed_read_only_gh_api_endpoints` and unsafe input tests model the kind of wrapper validation expected for the new script.
- Runtime dependency: `gh` and `jq` remain external command dependencies for wrapper execution. GraphQL thread state, if used, depends on `gh api graphql` but must be script-fixed and read-only.
- Downstream dependency: `github-pr-merge-preparer` needs stable `head_sha`, `normalized_status`, thread limitation fields, and waiver/human gate signals to avoid false merge-prepared evidence.

Implementation order implied by dependencies:

1. Define wrapper output schema and fixtures first.
2. Add provider wrapper and wrapper tests.
3. Update provider `pr-monitor` instructions to consume the wrapper and stable taxonomy.
4. Mirror provider assets into dogfooding tree and verify parity.
5. Adjust `github-pr-merge-preparer` wording only if needed to consume new fields; do not move monitor responsibility into it.

## 7. Source of Record

- Provider source of truth:
  - `src/spec_dock/assets/install_root/.codex/agents/pr-monitor.toml`
  - `src/spec_dock/assets/install_root/.github/agents/pr-monitor.agent.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-codex-pr-review-comments/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-codex-pr-review-comments/scripts/fetch_codex_pr_review_comments.sh`
  - proposed new provider wrapper under the same `scripts/` directory.

- Dogfooding mirrors to verify, not treat as primary authority:
  - `.codex/agents/pr-monitor.toml`
  - `.github/agents/pr-monitor.agent.md`
  - `.agents/skills/github-codex-pr-review-comments/SKILL.md`
  - `.agents/skills/github-codex-pr-review-comments/scripts/fetch_codex_pr_review_comments.sh`
  - proposed mirrored stable observation wrapper.

- Tests as contract evidence:
  - `tests/unit/infra/test_init_update.py` for asset inventory, byte parity, content regression, fixed wrapper validation, representative normalization fixtures, and unsafe input rejection.

## 8. Data Flow / Domain Model / Interface Contract

Recommended wrapper CLI:

```text
fetch_pr_stable_observation.sh --repo OWNER/REPO --pr <number> [--head-sha <sha>] [--out <dir>]
```

Allowed parameters are fixed and narrow. No endpoint, method, query, body, header, or mutation passthrough is allowed.

Recommended output files:

```text
pr_observation.json
pr_observation_report.md
raw/pr_view.json
raw/checks.json
raw/statuses.json
raw/reviews.json
raw/review_comments.json
raw/issue_comments.json
raw/review_threads.json
```

Recommended `pr_observation.json` shape:

```json
{
  "meta": {
    "repo": "OWNER/REPO",
    "pr": 123,
    "transport": "fixed read-only gh calls",
    "fetched_at": "2026-06-07T00:00:00Z",
    "pagination_complete": true
  },
  "head": {
    "expected_head_sha": "abc123",
    "current_head_sha": "abc123",
    "matches_expected": true
  },
  "checks": {
    "collection_status": "success",
    "normalized_status": "success",
    "observation_complete": true,
    "items": [],
    "counts": {
      "success": 1,
      "pending": 0,
      "failure": 0,
      "unknown": 0
    }
  },
  "reviews": {
    "collection_status": "success",
    "thread_state_available": true,
    "observation_complete": true,
    "review_decision": "APPROVED",
    "all": {
      "issue_comments": [],
      "review_comments": [],
      "reviews": [],
      "review_threads": []
    },
    "codex": {
      "issue_comments": [],
      "review_comments": [],
      "reviews": [],
      "review_threads": []
    },
    "humans": {
      "issue_comments": [],
      "review_comments": [],
      "reviews": [],
      "review_threads": []
    },
    "bots": {
      "issue_comments": [],
      "review_comments": [],
      "reviews": [],
      "review_threads": []
    }
  },
  "snapshot": {
    "fingerprint": "sha256:...",
    "fingerprint_fields": [
      "head.current_head_sha",
      "checks.items.normalized_state",
      "reviews.review_decision",
      "reviews.all.*.id",
      "reviews.all.*.updated_at",
      "reviews.all.review_threads.*.is_resolved",
      "reviews.all.review_threads.*.is_outdated",
      "body_hash"
    ]
  },
  "overall_status": "success",
  "normalized_status": "success",
  "observation_complete": true,
  "limitations": [],
  "recommended_next_action": "human may evaluate merge readiness"
}
```

Status/check taxonomy:

- `success`:
  - check/status conclusion/state indicates success and is terminal.
- `pending`:
  - queued, pending, in_progress, waiting, requested, expected, null conclusion/status where completion is not knowable yet.
- `failure`:
  - failure, error, cancelled, timed_out, action_required, startup_failure, stale, or an equivalent non-success terminal state.
- `unknown`:
  - missing collection, schema mismatch, unrecognized state, auth failure, rate limit, null values outside expected pending semantics, or wrapper inability to prove completeness.
- `neutral` and `skipped`:
  - do not become `success` automatically. Record as terminal non-success-neutral items. Design preference: classify them as `unknown` unless an explicit caller/human waiver or repository policy states they are acceptable.

Review taxonomy:

- `review_changes_requested`:
  - `reviewDecision=CHANGES_REQUESTED`, unresolved actionable thread, or actionable review body/comment.
- `review_state_unknown`:
  - review comments/reviews exist but thread state is unavailable, or thread visibility is missing and absence of unresolved threads cannot be proven.
- `pending_review`:
  - requested reviewer wait policy is active and reviewer response remains outstanding.
- `success`:
  - review collection succeeded, thread state is available or explicitly non-required, no blocking review feedback remains, and the review snapshot is stable.

Stable observation completion is not produced by a single wrapper call alone. `pr-monitor` must observe identical `snapshot.fingerprint` at least twice and confirm the minimum quiet window before returning `observation_complete=true` in its final report.

## 9. File / Module Change Plan

Provider-side changes:

```text
src/spec_dock/assets/install_root/
|-- .agents/
|   `-- skills/
|       `-- github-codex-pr-review-comments/
|           |-- SKILL.md
|           `-- scripts/
|               |-- fetch_codex_pr_review_comments.sh       # keep existing compatibility wrapper
|               `-- fetch_pr_stable_observation.sh          # add fixed read-only stable observation wrapper
|-- .codex/
|   `-- agents/
|       `-- pr-monitor.toml                                # update contract and output taxonomy
`-- .github/
    `-- agents/
        `-- pr-monitor.agent.md                            # update equivalent contract
```

Dogfooding mirror parity targets:

```text
.agents/skills/github-codex-pr-review-comments/SKILL.md
.agents/skills/github-codex-pr-review-comments/scripts/fetch_codex_pr_review_comments.sh
.agents/skills/github-codex-pr-review-comments/scripts/fetch_pr_stable_observation.sh
.codex/agents/pr-monitor.toml
.github/agents/pr-monitor.agent.md
```

Test targets:

```text
tests/unit/infra/test_init_update.py
```

Suggested focused test additions:

- `test_issue_170_pr_stable_observation_wrapper_rejects_unsafe_inputs_before_gh`
- `test_issue_170_pr_stable_observation_wrapper_uses_fixed_read_only_calls`
- `test_issue_170_pr_stable_observation_output_normalizes_representative_fixture`
- `test_issue_170_pr_monitor_guidance_requires_latest_head_sha_stability`
- `test_issue_170_pr_monitor_guidance_maps_unknowns_to_non_success`
- Extend dogfooding parity expectations only if the current parity test does not automatically cover the new file inventory.

## 10. Migration / Compatibility / Rollback

Compatibility:

- Keep `fetch_codex_pr_review_comments.sh` and its current output files for existing consumers.
- Keep `overall_status` coarse values in `pr-monitor` final output.
- Add `normalized_status`, `observation_complete`, `head.expected/current/matches_expected`, `limitations`, and stable snapshot fields without removing old keys.
- Existing `codex_review` summary can remain, but should be backed by the new all/Codex-separated observation where available.

Migration:

- Provider assets are updated first under `src/spec_dock/assets/install_root/`.
- Dogfooding mirrors are refreshed or edited to byte parity.
- Tests confirm that init/update installs the new wrapper and restores stale managed files from provider source.
- The main orchestrator should record any adopted draft portions in `report.md` Evidence Adoption Ledger before canonical design integration.

Rollback:

- If the new stable wrapper is defective, revert the new wrapper plus the `pr-monitor` instruction references to it. The existing Codex-only wrapper remains available.
- If GraphQL thread collection is unstable, retain the wrapper but mark `thread_state_available=false`, `normalized_status=review_state_unknown`, and `observation_complete=false` rather than pretending success.
- If output taxonomy causes downstream mismatch, preserve old `overall_status` mapping while fixing or gating only the new `normalized_status` consumers.

## 11. Observability

- Wrapper output must include `fetched_at`, input repo/pr, expected/current head SHA, collection success/failure per surface, pagination completeness, and limitations.
- `pr-monitor` final output should include:
  - `started_at`, `finished_at`, `elapsed_seconds`, `iteration_count`
  - `head_sha` plus `expected_head_sha` and `current_head_sha`
  - `snapshot_stable`, `stable_since`, `same_fingerprint_count`, `minimum_quiet_seconds`
  - `overall_status`, `normalized_status`, `observation_complete`
  - `checks.counts`, failed/pending/unknown item summaries
  - `reviews.thread_state_available`, unresolved/resolved/outdated counts, Codex/all split counts
  - `risks_or_unknowns` and `recommended_next_action`
- Wrapper failures should be visible as structured limitations, not only stderr text.
- No persistent monitor state should be written outside caller-provided output directories. `pr-monitor` itself should keep polling state in context only.

## 12. Test Strategy

Wrapper validation/unit:

- Validate argument rejection before invoking fake `gh`: invalid repo, invalid PR, unknown flags, query/method/endpoint passthrough attempts.
- Fake `gh` should assert only fixed read-only invocations occur.
- Add fixtures for check/status conclusions:
  - success
  - pending/null
  - failure/error/cancelled/timed_out/action_required/stale
  - neutral/skipped
  - unknown schema
- Add review fixtures:
  - no comments and thread state available
  - Codex and human comments separated
  - `CHANGES_REQUESTED`
  - unresolved thread
  - resolved/outdated thread
  - thread state unavailable with comments
  - thread state unavailable with no visible comments

Installed asset content regression:

- Assert `pr-monitor` provider and mirror instructions mention latest head SHA binding, snapshot reset, stable fingerprint, quiet window, `normalized_status`, `observation_complete`, and no arbitrary GraphQL/API fallback.
- Assert the skill `SKILL.md` documents both the compatibility wrapper and the stable observation wrapper without removing existing quick-start behavior.

Dogfooding parity:

- Use the existing issue-71 parity test to verify provider/mirror byte equivalence for `.agents`, `.codex`, and `.github`.
- Add a targeted assertion if the new wrapper file is not naturally covered by current inventory.

Representative output normalization fixture:

- Test one synthetic PR payload where:
  - expected/current head match,
  - one check succeeds,
  - one status is pending,
  - a review comment exists,
  - thread state is unavailable.
- Expected result:
  - `checks.normalized_status=pending`,
  - `reviews.normalized_status=review_state_unknown`,
  - `overall_status` is non-success,
  - `observation_complete=false`,
  - `limitations` includes thread visibility absence.

Integration / manual:

- Avoid live GitHub dependency for unit tests. If a live smoke is later needed, record it as manual-required evidence in `report.md` with repo/pr/head SHA and no mutation.

## 13. ADR Candidates

- ADR candidate: "Stable PR observation uses fixed read-only wrapper output as the monitor interface."
  - Promote only if this becomes a durable cross-issue policy for PR monitoring and future host agents.

- ADR candidate: "Unknown review thread state blocks merge-prepared evidence unless explicitly waived."
  - This may be durable enough for ADR because it affects merge-prepared semantics across workflows.

- Not ADR-worthy unless scope grows:
  - exact quiet-window default seconds,
  - exact script filename,
  - exact fixture names.

## 14. Risks

- GraphQL reviewThreads shape may drift or require permissions not available in all repositories.
  - Mitigation: fixed wrapper marks thread collection unavailable and returns `review_state_unknown`; no direct agent fallback.

- `neutral` / `skipped` treatment may be too strict for some repositories.
  - Mitigation: default to non-success/unknown without policy waiver; let `github-pr-merge-preparer` or human gate decide optionality.

- `gh pr checks` and `statusCheckRollup` may expose overlapping or differently shaped records.
  - Mitigation: normalize by source/name/state/conclusion/url and keep source fields for audit.

- Prompt and wrapper can drift if only one host asset is updated.
  - Mitigation: provider-first edits plus dogfooding parity test.

- New wrapper may duplicate some REST calls from the existing Codex wrapper.
  - Mitigation: accept duplication initially for contract clarity, or have the new wrapper internally reuse fixed helpers later without changing public inputs.

## 15. Requirement Clarification Requests

Requirement Clarification Requests: none.

Non-blocking design defaults for the main orchestrator to decide while integrating design:

- quiet window default: recommend `minimum_quiet_seconds=90` and `same_fingerprint_count>=2` for initial implementation, with timeout still bounded by `timeout_minutes`.
- zero-check grace: recommend at least two polls before classifying no checks as `unknown` at deadline.
- requested reviewers: recommend no default wait for human requested reviewers unless an explicit caller policy requests waiting; always report outstanding requests.
- GraphQL reviewThreads: recommend fixed read-only GraphQL inside the new wrapper if the GitHub CLI supports the required fields; otherwise return machine-readable `thread_state_available=false`.

## 16. Integration Notes for Main Orchestrator

Delegated draft evidence:

- role: `spec-dock-system-architect`
- phase: requirement/design
- scope: `iss-00170`
- source artifacts read:
  - `spec-dock/active/context-pack.md`
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
  - `spec-dock/active/issue/discussions/20260607t063203z-research-gpt55-pr-monitor-stable-observation-discussion.md`
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/workflow_clarification.md`
  - `spec-dock/docs/phase_requirement.md`
  - `spec-dock/docs/phase_design.md`
  - `spec-dock/docs/reference_sync.md`
  - provider/mirror `pr-monitor` assets
  - existing Codex review wrapper skill and script
  - `github-pr-merge-preparer` skill
  - `tests/unit/infra/test_init_update.py`
- draft artifact path: `spec-dock/active/issue/discussions/20260607t070628z-disc-system-architect-pr-monitor-stable-observation.md`
- draft status: `produced`
- authority: `proposed`
- adoption_status: `unreviewed`
- reflected_to: `[]`
- intended_targets:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
- diff_guard_result: `pending`
- integration notes:
  - Adopt the wrapper split, SHA-bound observation model, taxonomy, and parity/test strategy into canonical design only after main-orchestrator review.
  - Record adoption decision in `report.md` Evidence Adoption Ledger.
  - Run the post-run diff guard before treating this draft as adoption-eligible.
  - A fresh `spec-reviewer` pass remains required after canonical design integration.
- rejected portions: none
- blockers: none
- canonical artifacts edited: `none`
- final authority claimed: `no`

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
