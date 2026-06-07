---
created_by_role: spec-dock-implementation-planner
scope_id: iss-00170
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/discussions/20260607t070628z-disc-system-architect-pr-monitor-stable-observation.md
  - spec-dock/active/issue/discussions/20260607t063203z-research-gpt55-pr-monitor-stable-observation-discussion.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/workflow_clarification.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/phase_plan.md
  - spec-dock/docs/reference_deps.md
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
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
adoption_ledger_note: Main orchestrator must decide adoption in canonical report.md before canonical plan integration.
---

# Implementation Plan Draft: PR Monitor Stable Observation

This draft is proposed planning evidence for `iss-00170` only. It does not edit or authorize canonical `requirement.md`, `design.md`, `plan.md`, or `report.md`. The main orchestrator owns adoption, canonical integration, final reviewer gates, implementation readiness, and phase movement.

## 1. Plan Summary

Plan the issue as a dependency-first hardening sequence:

1. Freeze the deterministic wrapper contract, safety boundary, schema, taxonomy, and normalization tests before changing downstream agent instructions.
2. Update provider-side `pr-monitor` instructions to consume the fixed wrapper output and to report head-SHA-bound stable observation.
3. Update skill documentation and dogfooding mirrors, then prove provider source of truth and mirror parity.
4. Run final verification and reviewer gates, then let the main orchestrator decide whether to adopt this draft into canonical `plan.md` and `report.md`.

Primary implementation principle: `src/spec_dock/assets/install_root/` is the provider source of truth; checked-in `.agents/`, `.codex/`, and `.github/` mirrors are verification targets, not the primary source.

Assumptions:

- The fresh design re-review already passed, as recorded in `report.md`; this draft does not claim that pass itself.
- The existing canonical `plan.md` is still a scaffold. This draft provides implementation-planner evidence for orchestrator adoption, not the canonical plan.
- New wrapper implementation may use fixed read-only `gh api graphql` internally for reviewThreads only if the query is hard-coded inside the script and caller input cannot alter endpoint, method, query, body, header, or mutation behavior.

## 2. Requirement / Design Traceability

Requirement trace:

- AC-001 and AC-002 require head SHA binding, stale-head handling, and snapshot reset/separation.
- AC-003 and AC-004 require combined checks/statuses normalization, terminal-state gating, stable fingerprint / quiet-window gating, and zero-check grace.
- AC-005 requires all review signals, Codex-authored subset separation, `reviewDecision`, `reviewRequests`, `reviewThreads`, thread state availability, pagination metadata, and fetched timestamp.
- AC-006 requires review snapshot fingerprint stability before monitor success.
- AC-007 requires `CHANGES_REQUESTED` and unresolved actionable review thread classification as review blockers.
- AC-008 and AC-009 require thread-state unavailable handling, including zero visible comments with unresolved-thread absence unproven.
- AC-010 requires provider/mirror parity and installed asset regression coverage.
- EC-001 through EC-005 require late review comments, mixed check/status sources, resolved/outdated thread distinction, wrapper failure disclosure, and non-required check failure disclosure.

Design trace:

- D1 adds `fetch_pr_stable_observation.sh` as a new fixed read-only stable observation wrapper.
- D2 preserves existing `fetch_codex_pr_review_comments.sh` as compatibility boundary.
- D3 keeps multi-poll stable decision in `pr-monitor`; wrapper emits one normalized snapshot and fingerprint.
- D4 preserves `overall_status` while adding `normalized_status` and `observation_complete`.
- The design dependency analysis explicitly says wrapper schema / taxonomy and tests must be fixed before provider `pr-monitor` instruction updates.

Non-negotiable constraints:

- `pr-monitor` remains read-only.
- Latest / expected head-SHA-bound observation is mandatory for merge-prepared evidence.
- Stable observation is bounded by deadline, fingerprint stability, and quiet window; no infinite wait.
- Thread state unknown, wrapper failure, stale head, and zero-check grace before expiry are not success.
- Provider source of truth stays under `src/spec_dock/assets/install_root/`; dogfooding mirror parity is required.

## 3. Milestones

M1: Wrapper contract and safety fixed.

- Close target: stable wrapper CLI accepts only `--repo`, `--pr`, optional `--head-sha`, optional `--out`; unsafe passthrough attempts fail before `gh`.
- Trace: AC-001 through AC-009, EC-001 through EC-005, read-only constraints, D1-D4.

M2: Provider `pr-monitor` instruction consumes the contract.

- Close target: provider Codex and GitHub agent instructions require stable wrapper polling, head-change reset/separation, fingerprint quiet window, normalized output, and no unsafe fallback.
- Trace: AC-001 through AC-009, EC-001, EC-004, non-negotiable constraints.

M3: Skill docs and mirror parity complete.

- Close target: provider skill docs describe old/new wrapper split, dogfooding mirror files byte-match provider assets, and init/update tests detect drift.
- Trace: AC-005, AC-010, epic E-RQ-001 through E-RQ-005.

M4: Final verification and handoff gate complete.

- Close target: focused tests, parity tests, validation/diff checks, and reviewer gates have report evidence for orchestrator adoption and downstream implementation.
- Trace: all AC/EC plus workflow issue final quality gate requirements.

## 4. Dependency-Derived Execution Order

Dependency rule: downstream instructions cannot safely reference a wrapper schema until that wrapper schema and tests are fixed.

Order:

1. S01 wrapper contract / safety / normalization.
   - Upstream evidence: design D1-D4, existing wrapper safety tests, issue AC/EC.
   - Unblocks: provider agent instruction can reference stable fields and taxonomy.
2. S02 provider `pr-monitor` instruction.
   - Depends on: S01 schema names and wrapper CLI.
   - Unblocks: host-specific monitor behavior is explicit in provider source.
3. S03 skill docs and dogfooding mirror parity.
   - Depends on: S01 wrapper and S02 provider text.
   - Unblocks: install-shaped assets and checked-in dogfooding mirrors are aligned.
4. S04 final verification / docs impact / report gate.
   - Depends on: S01-S03 green checks.
   - Unblocks: orchestrator can run final QA, code-review, spec-review, PR delivery, and merge-preparation gates.

Do not start S02 before S01 has a stable CLI/schema/taxonomy because otherwise tests and instructions can diverge on `review_requests`, `thread_state_available`, zero-check grace, stale head, and neutral/skipped semantics.

## 5. Issue / Step Slicing

### S01: Wrapper contract, safety, and normalization

Behavior goal:

- Add and test a deterministic single-snapshot PR observation wrapper contract that is safe, read-only, head-SHA-aware, and able to normalize checks/statuses/reviews/thread visibility into machine-readable output.

Allowed paths:

- `src/spec_dock/assets/install_root/.agents/skills/github-codex-pr-review-comments/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/github-codex-pr-review-comments/scripts/fetch_pr_stable_observation.sh`
- `src/spec_dock/assets/install_root/.agents/skills/github-codex-pr-review-comments/scripts/fetch_codex_pr_review_comments.sh` only for minimal compatibility comments if needed, not responsibility expansion.
- `tests/unit/infra/test_init_update.py`

Forbidden changes:

- No canonical spec docs.
- No dogfooding mirror edits in S01 except if a test fixture requires read-only inspection; actual mirror/parity update belongs to S03.
- No arbitrary endpoint/method/query/header/body/jq passthrough.
- No write operations, `gh pr comment`, review reply, thread resolve, review dismiss, merge, close, label/status mutation, push, or commit behavior.
- No broad GitHub plugin or skill rewrite.

Red or inspect evidence:

- Add red-first or characterization tests that fail before the new wrapper exists.
- Unsafe input tests must prove invalid repo, invalid PR, invalid head SHA, unknown flag, endpoint/method/query/body/header/jq/graphql passthrough attempts fail before fake `gh` logs any call.
- Fixed invocation tests must prove only fixed read-only calls are used. If GraphQL is used for reviewThreads, the query must be script-owned and not caller-provided.
- Fixture tests must include `review_requests`, thread state unavailable with zero visible comments, neutral/skipped checks, stale head mismatch, zero checks before/after grace, wrapper failure/auth/rate/schema limitation, and non-required check failure disclosure.

Green verification:

- `uv run pytest tests/unit/infra/test_init_update.py -k "pr_monitor or pr_review_wrapper or stable_observation or issue_75 or issue_71"`
- If test naming makes the `-k` expression too broad or empty, run the focused tests added/updated in `tests/unit/infra/test_init_update.py`.
- Inspect generated `pr_observation.json` fixture assertions for `head`, `checks`, `reviews`, `snapshot`, `limitations`, `overall_status`, `normalized_status`, and `observation_complete`.

Close conditions:

- `fetch_pr_stable_observation.sh` exists under provider install_root scripts.
- Wrapper output includes `review_requests`, `thread_state_available`, collection metadata, all/Codex/humans/bots review groupings, head expected/current/matches fields, normalized check/status counts, limitations, `snapshot.fingerprint`, `fingerprint_fields`, `overall_status`, `normalized_status`, and `observation_complete`.
- Existing `fetch_codex_pr_review_comments.sh` remains compatible.
- All unsafe input tests fail closed before `gh`.

Reviewer focus:

- `code-reviewer`: script safety, shell quoting, fail-closed input validation, fixture normalization, status taxonomy, no hidden write path, test sensitivity.

Delegation contract for dev-coder:

- Inputs: active requirement/design/report, system-architect draft, existing wrapper skill/script, `github-pr-merge-preparer` merge-prepared predicate, `tests/unit/infra/test_init_update.py`.
- Required output: changed files, tests added/updated, command results, unresolved risks, and `Ledger Note` or `No material implementation decisions beyond the approved plan.`
- Stop conditions: needing arbitrary GitHub API passthrough, needing write operations, unclear GraphQL schema that changes output contract, inability to test unsafe inputs, or requirement/design contradiction.

### S02: Provider `pr-monitor` instruction hardening

Behavior goal:

- Update provider Codex and GitHub `pr-monitor` instructions to consume the stable wrapper contract, poll snapshots, reset/separate stale observations on head change, and return normalized final output without claiming repair or merge responsibility.

Allowed paths:

- `src/spec_dock/assets/install_root/.codex/agents/pr-monitor.toml`
- `src/spec_dock/assets/install_root/.github/agents/pr-monitor.agent.md`
- `tests/unit/infra/test_init_update.py`

Forbidden changes:

- No dogfooding mirror edits yet except through S03 parity.
- No wrapper implementation changes unless S01 is reopened with plan/report amendment.
- No `github-pr-merge-preparer` responsibility transfer.
- No direct `gh api` or arbitrary GraphQL fallback in agent instructions.
- No write-capable monitor actions.

Red or inspect evidence:

- Instruction content assertions should fail before update and pass after update.
- Assertions must require repo-relative `fetch_pr_stable_observation.sh`, expected/current head SHA binding, head-change snapshot reset/separation, same fingerprint count, quiet window, zero-check grace, normalized statuses, thread-state unavailable human gate, and `review_requests` handling.
- Assertions must preserve forbidden fallback text and read-only role.

Green verification:

- Focused instruction content tests in `tests/unit/infra/test_init_update.py`.
- Manual inspection of provider Codex/GitHub instruction diff for output contract compatibility.

Close conditions:

- Provider `pr-monitor` instructions mention stable wrapper usage and no longer rely only on one or two short review grace waits as a success condition.
- Final output contract includes latest/expected head SHA, `head_matches_expected`, timing, iteration count, `same_fingerprint_count`, `minimum_quiet_seconds`, `snapshot_stable`, `normalized_status`, `observation_complete`, limitations, `checks`, and `reviews`.
- `overall_status` compatibility remains.

Reviewer focus:

- `spec-reviewer` for instruction/spec alignment if docs-only; `code-reviewer` if tests are changed in the same step. Prefer keeping tests in the step because behavior is testable.

Delegation contract for dev-coder or doc-writer:

- Primary worker: `dev-coder` if updating content tests; otherwise `doc-writer` for instruction text with explicit test handoff.
- Required output: changed provider files, exact content assertions, verification command, and residual ambiguity.
- Stop conditions: S01 schema changed, tests cannot assert instruction contract, or instruction update requires changing monitor responsibility beyond read-only observation.

### S03: Skill docs, dogfooding mirror, and parity

Behavior goal:

- Document the wrapper split and mirror provider assets into checked-in dogfooding files, then prove parity and install/update coverage.

Allowed paths:

- `src/spec_dock/assets/install_root/.agents/skills/github-codex-pr-review-comments/SKILL.md`
- `.agents/skills/github-codex-pr-review-comments/SKILL.md`
- `.agents/skills/github-codex-pr-review-comments/scripts/fetch_pr_stable_observation.sh`
- `.agents/skills/github-codex-pr-review-comments/scripts/fetch_codex_pr_review_comments.sh` only if provider compatibility note changed.
- `.codex/agents/pr-monitor.toml`
- `.github/agents/pr-monitor.agent.md`
- `tests/unit/infra/test_init_update.py`

Forbidden changes:

- No canonical docs.
- No changing provider files except to resolve S01/S02 reviewer findings.
- No hand-edited dogfooding content that intentionally diverges from provider source.
- No installer architecture rewrite unless parity tests prove current install_root sync cannot carry the new file.

Red or inspect evidence:

- Existing dogfooding parity test should fail if mirror files are absent or diverge.
- Add or update install/update regression to require the new wrapper appears in init/update targets.
- Add skill-doc assertions that mention both `fetch_codex_pr_review_comments.sh` and `fetch_pr_stable_observation.sh`, their responsibilities, and the no-passthrough boundary.

Green verification:

- `uv run pytest tests/unit/infra/test_init_update.py -k "issue_71 or stable_observation or pr_monitor or pr_review_wrapper"`
- Byte parity inspection by existing `test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets`.

Close conditions:

- Provider and checked-in dogfooding mirror bytes match for touched `.agents`, `.codex`, and `.github/agents` assets.
- New wrapper is included in install_root inventory and checked-in mirror inventory.
- Skill docs clearly distinguish the existing Codex-only review wrapper from the new stable PR observation wrapper.

Reviewer focus:

- `code-reviewer`: parity tests, install/update coverage, no source-of-truth inversion.
- `spec-reviewer`: skill docs and agent instruction consistency with requirement/design.

Delegation contract for dev-coder/doc-writer:

- Primary worker: `dev-coder` because parity tests and asset inventory are involved; `doc-writer` may be used only for skill wording as a bounded sub-slice.
- Required output: provider/mirror changed files, parity command, install/update regression evidence, unresolved drift risks.
- Stop conditions: provider/mirror byte parity cannot be achieved, install_root does not install hidden paths, or mirrored file would need intentional divergence.

### S04: Final verification, docs impact, and report gate

Behavior goal:

- Confirm all closure obligations and handoff gates are ready for the main orchestrator to integrate canonical plan/report evidence and start implementation or final review sequence.

Allowed paths during implementation execution:

- `spec-dock/active/issue/report.md` for orchestrator-owned evidence recording only, not by this delegated draft role.
- No implementation path changes in this draft role.

Forbidden changes for this delegated draft:

- This implementation-planner draft must not edit `report.md`, `plan.md`, implementation files, tests, provider files, mirrors, GitHub state, commits, or phase state.

Required verification after implementation:

- `uv run pytest tests/unit/infra/test_init_update.py`
- If runtime/scaffold asset impact expands, run broader relevant suite: `uv run pytest tests/unit` and any focused integration smoke the final plan requires.
- `./spec-dock/scripts/spec-dock validate`
- `./spec-dock/scripts/spec-dock sync --no-github` or normal `sync` as orchestrator chooses for live state.
- `git diff --check`
- Final `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer` gates.

Close conditions:

- Closure Index rows below are closed in `report.md` Step Contract Closure, Test Contract Closure, and Closure Coverage.
- Docs impact is resolved: skill/instruction docs updated, no unrelated docs required, or docs update is explicitly performed and reviewed.
- Delegated worker evidence and reviewer results are recorded by the main orchestrator.

Reviewer focus:

- `qa-reviewer`: obligation coverage, missing high-value tests, integration test need.
- `code-reviewer`: issue-wide diff, shell safety, tests, install-root/mirror parity.
- `spec-reviewer`: requirement/design/plan/report/implementation alignment.

Delegation contract:

- Worker role: main orchestrator should use reviewers and dev-coder/doc-writer as required by `workflow_issue.md`; this draft role does not execute S04.
- Stop conditions: any reviewer non-pass, uncovered AC/EC, failed parity, failed validation, missing report evidence, stale head/thread-state unknown behavior not tested, or unresolved design gap discovered.

## 6. Test Strategy Mapping

Closure Index for canonical adoption:

| Closure ID | Requirement / constraint | Step | Evidence level | Test / inspection obligation |
|---|---|---:|---|---|
| CL-AC-001 | AC-001 expected/current head SHA binding and stale mismatch | S01, S02 | red-required | wrapper fixture and instruction assertion for `stale_head`, `observation_complete=false`, expected/current fields |
| CL-AC-002 | AC-002 head SHA changes during monitoring reset/separate snapshots | S02 | inspect-only + content test | instruction assertion for `last_observed_head_sha`, reset/separate stale snapshot, final SHA field |
| CL-AC-003 | AC-003 combined checks/statuses terminal and stable fingerprint | S01, S02 | red-required | fixture for success/pending/failure/action_required/stale and fingerprint fields |
| CL-AC-004 | AC-004 zero checks grace | S01, S02 | red-required | fixture for zero checks before grace as pending/unknown and deadline limitation as non-success |
| CL-AC-005 | AC-005 all review signals, Codex subset, `reviewDecision`, `reviewRequests`, `reviewThreads`, metadata | S01, S03 | red-required | wrapper output schema fixture and skill docs assertion |
| CL-AC-006 | AC-006 review snapshot quiet window and late comment stability | S02 | inspect-only + content test | instruction assertion for same fingerprint count and minimum quiet seconds before review complete |
| CL-AC-007 | AC-007 `CHANGES_REQUESTED` / unresolved actionable thread blocker | S01, S02 | red-required | fixture maps blocker to `review_changes_requested`; instruction reports source signal |
| CL-AC-008 | AC-008 thread unavailable with visible comments | S01, S02 | red-required | fixture maps to `review_state_unknown` / human gate, with limitation and next action |
| CL-AC-009 | AC-009 thread unavailable with zero visible comments | S01, S02 | red-required | fixture proves zero visible comments plus unavailable thread state is not unconditional success |
| CL-AC-010 | AC-010 provider/mirror parity and install/update regression | S03 | covered-existing + red-required | existing issue-71 parity plus new wrapper install/update assertion |
| CL-EC-001 | EC-001 late review comment after checks green | S02 | inspect-only + content test | instruction requires review snapshot stability after checks green |
| CL-EC-002 | EC-002 Actions success but commit status pending | S01 | red-required | fixture leaves combined check/status `pending` |
| CL-EC-003 | EC-003 resolved/outdated thread not blocker | S01 | red-required | fixture separates resolved/outdated from unresolved actionable |
| CL-EC-004 | EC-004 wrapper missing/auth/rate/schema failure | S01, S02 | red-required | fixture emits limitation and non-success `review_state_unknown` or `observation_unknown` |
| CL-EC-005 | EC-005 non-required check failure disclosed, waiver outside monitor | S01, S02 | red-required | fixture reports failure/non-success; instruction delegates waiver to caller/human gate |
| CL-C-001 | read-only monitor, no writes | S01, S02, S03 | red-required + inspect-only | unsafe input and instruction forbidden fallback assertions |
| CL-C-002 | latest head SHA only for merge-prepared evidence | S01, S02 | red-required | stale head fixture and preparer compatibility inspection |
| CL-C-003 | bounded stable observation, no infinite wait | S02 | inspect-only + content test | instruction requires deadline, quiet window, iteration count |
| CL-C-004 | thread unknown, wrapper failure, stale head, zero-check grace not success | S01, S02 | red-required | normalized status fixtures and instruction assertions |
| CL-C-005 | provider source of truth and dogfooding mirror parity | S03 | covered-existing | provider-first edits plus byte parity test |

Concrete test seeds for S01:

- `tc-s01-001` acceptance: head SHA match/mismatch output.
- `tc-s01-002` negative: unsafe args fail before fake `gh`.
- `tc-s01-003` normalization: neutral/skipped and non-required failure remain visible and non-success without waiver.
- `tc-s01-004` review: `review_requests` appears in all/Codex/humans/bots grouping and fingerprint fields.
- `tc-s01-005` unknown: thread state unavailable with zero visible comments returns non-success limitation.

Concrete test seeds for S02:

- `tc-s02-001` content: provider monitor references `fetch_pr_stable_observation.sh` and output fields.
- `tc-s02-002` content: monitor requires reset/separate stale snapshot when head SHA changes.
- `tc-s02-003` content: monitor forbids direct API/GraphQL fallback and write actions.

Concrete test seeds for S03:

- `tc-s03-001` parity: checked-in mirrors byte-match provider install_root assets.
- `tc-s03-002` install/update: new wrapper is installed after init/update.
- `tc-s03-003` skill docs: old/new wrapper split and safety boundary are documented.

## 7. Review Gates

Per-step gates:

- S01: `code-reviewer` pass is required because shell runtime, safety, and tests change.
- S02: `code-reviewer` pass is required if tests change; `spec-reviewer` should also inspect docs/spec alignment if instruction-only text is material.
- S03: `code-reviewer` pass for parity/install tests and `spec-reviewer` pass for skill/instruction text consistency.
- S04: final `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer` pass are required by `workflow_issue.md`.

Main orchestrator gates before adoption:

- Run post-run diff guard for this delegated discussion draft.
- Record Evidence Adoption Ledger entry in canonical `report.md` if adopting this draft.
- Integrate adopted portions into canonical `plan.md`.
- Run fresh `spec-reviewer` on the canonical plan; this draft is not a reviewer pass.

Reviewer focus checklist:

- Wrapper safety: fail closed before `gh`, no passthrough, fixed read-only calls only.
- Schema completeness: `review_requests`, thread-state availability, zero-visible-comments limitation, stale head, neutral/skipped, zero-check grace.
- Dependency order: no downstream instruction references unstable schema.
- Responsibility boundary: `pr-monitor` observes and summarizes; `github-pr-merge-preparer` coordinates repair/human gate; human merges.
- Provider/mirror parity: source-of-truth is not inverted.

## 8. Rollback / Compatibility

Compatibility:

- Keep `fetch_codex_pr_review_comments.sh` and its output contract.
- Keep `overall_status` and existing coarse values as compatibility surface.
- Add `fetch_pr_stable_observation.sh`, `normalized_status`, `observation_complete`, limitations, and structured head/check/review fields as additive contract.
- Do not change `github-pr-merge-preparer` responsibility unless a later finding proves wording must consume new fields more explicitly.

Rollback:

- Revert the new wrapper, provider instruction references, skill doc references, and mirror copies as one issue diff if necessary.
- If reviewThreads GraphQL collection proves unreliable, keep the wrapper but return `thread_state_available=false` plus limitation and non-success/human gate rather than falling back to arbitrary API calls.
- If neutral/skipped strictness creates false blockers, handle optionality via caller policy or human waiver; do not make monitor silently treat them as success.

Risk controls:

- Use fixtures/fake `gh` for deterministic tests.
- Avoid live GitHub dependencies in unit tests.
- Preserve raw snapshots under wrapper output for audit while normalizing machine-readable fields.

## 9. Docs Impact

Required docs / instruction impact:

- Provider `pr-monitor` Codex instruction.
- Provider GitHub `pr-monitor` agent instruction.
- Provider `github-codex-pr-review-comments` skill docs for wrapper split.
- Dogfooding mirror copies of the same assets.
- Canonical `plan.md` and `report.md` only by main orchestrator if adopting this draft.

No docs impact expected:

- General workflow docs, README, templates, and runtime docs do not need changes unless implementation discovers a broader install_root or delegated workflow contract gap.

Docs review:

- `spec-reviewer` should verify that instructions and skill docs match `requirement.md` and `design.md`.
- S90 docs impact resolution in canonical plan should explicitly record whether broader docs are `none` or updated.

## 10. Final Quality Gate

Required final evidence bundle after implementation:

- Focused tests for wrapper safety/schema/normalization and instruction content.
- Existing and updated parity/install tests.
- `uv run pytest tests/unit/infra/test_init_update.py`.
- Broader suite if code paths or installer behavior expand beyond test_init_update.
- `./spec-dock/scripts/spec-dock validate`.
- `./spec-dock/scripts/spec-dock sync --no-github` or normal `sync`, chosen by orchestrator based on live-state need.
- `git diff --check`.
- Final `qa-reviewer` pass.
- Issue-wide `code-reviewer` pass.
- Final `spec-reviewer` pass on canonical docs/report/evidence.

Final exit conditions:

- Every Closure Index row is closed or explicitly amended with fresh review.
- No unresolved blocker remains in Evidence Adoption Ledger, Spec Interpretation / Decision Ledger, or reviewer gates.
- PR delivery and merge-preparation gates are recorded before issue finish if the issue proceeds to PR delivery.
- No final authority is claimed by this draft.

## 11. Plan Blockers

Plan Blockers: none.

Non-blocking cautions for the main orchestrator:

- Existing worktree baseline already contained modified `design.md`, modified `report.md`, and an untracked system-architect discussion before this draft was created. The post-run diff guard must decide whether that baseline is adoption-eligible.
- Q-001 quiet window default, Q-002 requested reviewer wait policy, and Q-003 neutral/skipped policy are non-blocking design defaults with recommended answers in `design.md`; implementation should not ask the user unless a material contradiction appears.
- Exact GraphQL query/pagination details are implementation details inside the fixed wrapper. If they require changing requirement/design scope, stop and return to design rather than improvising in code.

## 12. Integration Notes for Main Orchestrator

Suggested adoption target:

- Adopt the dependency-derived order, S01-S04 step slicing, Closure Index, delegation contracts, and final gate language into canonical `plan.md` if post-run diff guard passes.
- Record this draft in canonical `report.md` Delegated Draft Evidence and Evidence Adoption Ledger before using it for phase promotion.
- Run fresh `spec-reviewer` on the canonical plan after integration.

Delegated draft evidence:

- role: `spec-dock-implementation-planner`
- phase: plan
- scope: `iss-00170`
- source artifacts read:
  - `spec-dock/active/context-pack.md`
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
  - issue discussions listed in frontmatter
  - parent epic requirement/design
  - workflow / authoring / phase / deps / sync references listed in frontmatter
  - provider and mirror pr-monitor assets
  - wrapper skill/script and merge-preparer skill
  - `tests/unit/infra/test_init_update.py`
- draft artifact path: `spec-dock/active/issue/discussions/20260607t072057z-disc-implementation-plan-pr-monitor-stable-observation.md`
- draft status: `produced`
- authority: `proposed`
- adoption_status: `unreviewed`
- reflected_to: `[]`
- intended_targets:
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
- diff_guard_result: `pending`
- integration notes: use as plan material only after diff guard and canonical report adoption ledger.
- rejected portions: none in draft.
- blockers: none.
- canonical artifacts edited: `none`
- final authority claimed: `no`

Dev-coder handoff contract:

- Start with S01 and do not modify S02/S03 files until S01 wrapper schema and tests are green.
- Use provider paths under `src/spec_dock/assets/install_root/` as source of truth.
- Keep changes within the allowed paths for each step.
- Record Red/Green evidence, changed files, reviewer findings, and closure IDs in `report.md` through the main orchestrator.
- Stop immediately on any need for unsafe GitHub passthrough, write operations, canonical spec edits, scope expansion, or untestable schema changes.

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
