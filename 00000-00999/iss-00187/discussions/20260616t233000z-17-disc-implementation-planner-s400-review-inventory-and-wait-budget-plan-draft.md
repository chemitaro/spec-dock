---
created_by_role: implementation-planner
scope_id: iss-00187-actions-pr-observation-ci-state
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/phase_plan.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00187-actions-pr-observation-ci-state/discussions/20260616t225521z-14-disc-missed-p2-reserve-next-observation-poll.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00187-actions-pr-observation-ci-state/discussions/20260616t225521z-15-disc-pr-observation-missed-review-root-cause.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00187-actions-pr-observation-ci-state/discussions/20260616t231000z-16-disc-system-architect-review-inventory-and-wait-budget-design-draft.md
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# Implementation Planner Draft: S400+ Review Inventory and Wait Budget Plan Addendum

This is delegated draft planning evidence for appending an S400+ lane to canonical `plan.md`. It assumes S01-S399 are completed and must not be renumbered or rewritten. The main orchestrator owns canonical adoption, report ledger updates, fresh `spec-reviewer` pass, implementation readiness, and final authority.

## 1. Plan Summary

Add an S400+ implementation lane after existing S300+ completion to cover the fresh design evidence for review inventory and wait budget hardening.

Planned lane:

- S400: canonical adoption / evidence gate for S400+ plan and design evidence.
- S410: provider-first actionable review inventory classification.
- S420: snapshot / wait decision precedence and summary alignment.
- S430: wait next-poll budget guard, `review_completion_unknown` CI-passed latency default update, and post-unknown audit metadata.
- S490: docs impact and dogfooding mirror sync.
- S499: final quality gate, live PR #190 re-observation, and final fresh review gates.

Each step is intended as 1 observable behavior, 1 review scope, and 1 commit boundary. Runtime/test/scaffold steps are delegated to `dev-coder`; docs wording goes to `doc-writer`; final gates require `qa-reviewer`, issue-wide `code-reviewer`, and `spec-reviewer`.

## 2. Requirement / Design Traceability

- AC-006: S410/S420/S430 ensure stable no-completion evidence cannot hide actionable review work, and `review_completion_unknown` stays non-pass.
- AC-007: S420 preserves pending review precedence before unknown promotion.
- Existing false-pass constraints: S410/S420 ensure `selected_unresolved_count == 0` is not treated as proof that review work is absent.
- Provider-first / mirror constraint: S410/S420/S430 change provider assets first; S490 syncs `.agents/...` mirror.
- Fake `gh` regression requirement: S410/S420/S430 add or update focused tests in `tests/unit/infra/test_init_update.py`.
- Fresh post-unknown evidence: S430 adds `wait.post_unknown_fresh_audit_required=true` when `review_completion_unknown` is emitted.
- PR #190 evidence: S499 re-observes latest PR #190 head after push and reports actionable review inventory, including review comment `3422572159` if still unresolved and non-outdated.

Design anchors:

- `design.md` S400+ defines `current_selected_unresolved`, `carryover_non_outdated_unresolved`, `all_fetched_unresolved`, and `actionable_unresolved`.
- `design.md` S400+ defines decision precedence: current selected, carryover, blocking collection limitation, pending review, trusted completion, stable no-completion unknown.
- `design.md` S400+ defines wait budget guard and CI-passed latency default increase from `90` to `300` seconds.
- Discussions `14` and `15` establish the P2 next-poll budget defect and the missed-review root cause.
- Discussion `16` establishes the architecture boundary and additive JSON contract.

## 3. Milestones

- M1: S400 authoring adoption gate records S400+ source evidence and receives fresh `spec-reviewer` pass before implementation.
- M2: S410/S420 expose and consume first-class actionable review inventory.
- M3: S430 prevents under-budget final polls from degrading the latest useful payload and strengthens `review_completion_unknown` metadata.
- M4: S490 aligns provider docs, shipped assets, and dogfooding mirror.
- M5: S499 completes focused/broad validation, reviewer gates, and PR #190 live re-observation.

## 4. Dependency-Derived Execution Order

```text
S400
  -> S410
      -> S420
          -> S430
              -> S490
                  -> S499
```

Ordering rationale:

- S400 must run first because delegated discussion evidence is not canonical authority until the orchestrator adopts it and fresh `spec-reviewer` passes the canonical plan.
- S410 must precede S420 because snapshot / wait precedence needs normalized `actionable_unresolved` fields from the review collector or extraction module.
- S420 must precede S430 because wait budget and unknown metadata should preserve the latest meaningful decision shape, not invent parallel review classification.
- S490 follows behavior changes to avoid mirror drift and docs claiming unimplemented output semantics.
- S499 is final only after all behavior, docs, mirror, and report evidence are in place.

## 5. Issue / Step Slicing

### S400 - S400+ canonical adoption and evidence gate

- Observable behavior: S400+ delegated evidence is adopted or rejected in canonical `report.md`, canonical `plan.md` receives the S400+ lane if accepted, and fresh `spec-reviewer` reviews the canonical plan before implementation.
- Depends on: S399 completion and fresh design evidence.
- Unblocks: S410.
- Target files if adopted by main orchestrator: `spec-dock/active/issue/plan.md`, `spec-dock/active/issue/report.md`.
- Review gate: `spec-reviewer`.
- Commit boundary: canonical plan/report adoption only.

Delegation contract:

- delegated role: `spec-reviewer` for canonical plan review; main orchestrator owns canonical edits.
- input docs: active requirement/design/plan/report, discussions `14`, `15`, `16`, and this draft.
- allowed paths for this delegated draft: none; S400 canonical edits are orchestrator-only.
- forbidden changes: no implementation files, tests, configs, `.agents`, GitHub state, phase promotion, or implementation-readiness claim.
- acceptance criteria: Evidence Adoption Ledger records this draft and source discussions; canonical plan has S400+ lane; reviewer returns `review_status: pass`.
- required verification: `git diff --check` after canonical adoption and fresh `spec-reviewer` pass.
- reviewer focus: traceability to fresh design, no S01-S399 renumbering, executable step schema, no delegated-authority claim.
- output required: reviewer verdict, adopted/rejected portions, blockers, and next action.
- stop conditions: design evidence is stale or contradictory; plan adoption would require requirement changes; reviewer fails.

Concrete test cases:

- `tc-s400-001` authoring: S400+ canonical adoption is ledgered
  - 前提: this discussion draft and design S400+ addendum exist.
  - 操作: orchestrator adopts accepted parts into canonical `plan.md` and records Evidence Adoption Ledger.
  - 期待結果: adopted source paths, target sections, reviewer target, and non-adopted portions are visible in `report.md`.
  - 失敗検出: delegated draft is treated as canonical authority without report adoption.
  - 検証方法: `report.md` inspection plus `git diff --check`.

- `tc-s400-002` authoring: fresh plan review gates implementation
  - 前提: canonical S400+ plan has been edited.
  - 操作: run fresh `spec-reviewer` on canonical requirement/design/plan alignment.
  - 期待結果: `review_status: pass` before S410 starts.
  - 失敗検出: implementation begins from unreviewed delegated draft.
  - 検証方法: reviewer evidence in `report.md`.

Step closure contract:

- Close only when canonical adoption evidence and fresh `spec-reviewer` pass are recorded.
- Report destinations: Evidence Adoption Ledger, Spec Authoring Gate, Reviewer Gate Status, Step Commit Gate.

### S410 - Actionable review inventory classification

- Observable behavior: review collection exposes actionable unresolved inventory as the union of current-selected unresolved threads and carryover non-outdated unresolved threads, while outdated-only data remains audit-only.
- Depends on: S400.
- Unblocks: S420.
- Target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh` or its extraction successor if current implementation has moved this responsibility.
  - `tests/unit/infra/test_init_update.py`.
- Review gate: `code-reviewer`.
- Commit boundary: provider review inventory fields and focused fake-`gh` tests only.

Delegation contract:

- delegated role: `dev-coder`.
- input docs: requirement AC-006/AC-007, design S400+ review inventory domain model, canonical S400+ plan, existing review collector/snapshot tests.
- allowed paths: provider review collector/extraction module and focused fake-`gh` tests.
- forbidden changes: no wait budget changes, no snapshot/wait precedence changes, no docs/mirror sync, no generic issue comment promotion, no selected-count-only completion inference.
- acceptance criteria: `decision.actionable_unresolved_count`, `decision.current_selected_unresolved_count`, `decision.carryover_unresolved_count`, `decision.actionable_unresolved_thread_ids`, and carryover IDs are emitted or mapped in the owned collector output; existing selected fields remain compatible.
- required tests: focused fake-`gh` tests for current-selected, carryover non-outdated, outdated-only audit, dedupe, and unclassified/outdated-null safety.
- reviewer focus: false-positive carryover blocking, outdated handling, GraphQL `isResolved=false` and `isOutdated=false` requirements, compatibility aliases, secret-safe limitations.
- output required: changed files, red/green evidence, closure IDs, unresolved risks, and `No material implementation decisions beyond the approved plan.` or a Ledger Note.
- stop conditions: GitHub payload cannot distinguish non-outdated carryover from stale audit data; required fields need a design amendment; implementation would require raw REST comments to become blockers without outdated evidence.

Concrete test cases:

- `tc-s410-001` acceptance: current-selected unresolved is actionable
  - 前提: fake `gh` returns a current-boundary unresolved review thread.
  - 操作: run provider review snapshot collector.
  - 期待結果: actionable count is greater than zero, current-selected count is greater than zero, current-selected reason is available, and IDs are listed.
  - 失敗検出: current review blockers remain hidden in selected-only or audit-only fields.
  - 検証方法: pytest fake-`gh` collector test.

- `tc-s410-002` acceptance: carryover non-outdated unresolved is actionable
  - 前提: selected IDs are empty, but GraphQL review thread payload has `isResolved=false` and `isOutdated=false`.
  - 操作: run provider review snapshot collector.
  - 期待結果: carryover count is greater than zero, actionable count is greater than zero, and carryover thread IDs are listed.
  - 失敗検出: non-outdated unresolved review work remains audit-only and can be missed by repair inventory.
  - 検証方法: pytest fake-`gh` collector test.

- `tc-s410-003` negative: outdated-only unresolved remains audit-only
  - 前提: all fetched unresolved threads are `isOutdated=true`.
  - 操作: run provider review snapshot collector.
  - 期待結果: audit data remains visible, but actionable and carryover counts are zero.
  - 失敗検出: stale/outdated review threads over-block current PR repair.
  - 検証方法: pytest fake-`gh` collector test.

- `tc-s410-004` negative: unknown outdated state is not promoted
  - 前提: REST comment data exists but GraphQL `isOutdated` is unavailable or null.
  - 操作: run provider review snapshot collector.
  - 期待結果: data is recorded as audit or limitation, not carryover actionable blocker.
  - 失敗検出: uncertain review artifacts become false blockers.
  - 検証方法: pytest fake-`gh` collector test with limitation assertion.

- `tc-s410-005` regression: selected and carryover sets dedupe
  - 前提: the same thread appears in current-selected and all-fetched non-outdated data.
  - 操作: run provider review snapshot collector.
  - 期待結果: current-selected is authoritative, carryover excludes duplicates, actionable IDs are unique.
  - 失敗検出: duplicated review work produces noisy or conflicting repair inventory.
  - 検証方法: pytest fake-`gh` collector test.

Step closure contract:

- Close when all S410 required tests pass and code-reviewer passes.
- Verification command: `uv run pytest tests/unit/infra/test_init_update.py -k "review_inventory or actionable_unresolved or carryover_unresolved or issue_187"`.
- Report destinations: TDD Evidence, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate, Delegated Worker Evidence.

### S420 - Snapshot / wait decision precedence and summary alignment

- Observable behavior: combined snapshot and wait decisions evaluate actionable review inventory before blocking limitations, pending review, trusted completion, and stable no-completion unknown; `summary.review` and `recommended_next_action` align with actionable inventory.
- Depends on: S410.
- Unblocks: S430.
- Target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py`.
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py` only if wait classification owns final precedence after S320.
  - `tests/unit/infra/test_init_update.py`.
- Review gate: `code-reviewer`.
- Commit boundary: decision precedence / summary behavior only.

Delegation contract:

- delegated role: `dev-coder`.
- input docs: design S400+ decision precedence, S410 output contract, existing snapshot/wait tests.
- allowed paths: provider snapshot/wait decision modules and focused tests.
- forbidden changes: no collector inventory classification beyond integration plumbing, no wait sleep/budget change, no docs/mirror sync, no merge-preparer implementation change.
- acceptance criteria: actionable unresolved inventory forces `summary.review="unresolved"`, `recommended_next_action="address_review_feedback"`, and a precise `decision.status_reason`; `review_completion_unknown` is impossible while actionable inventory is non-empty.
- required tests: focused fake-`gh` snapshot/wait tests for precedence, pending preservation, trusted completion with no blockers, and stable unknown only when actionable inventory is empty.
- reviewer focus: precedence ordering, compatibility of existing `selected_unresolved_count`, non-pass safety, and consistency between snapshot and wait final payloads.
- output required: changed files, tests run, closure evidence, unresolved risks, and Ledger Note if precedence needed interpretation.
- stop conditions: S410 output is insufficient; summary alignment would break existing public contract without design amendment; merge-preparer changes become necessary for this step.

Concrete test cases:

- `tc-s420-001` integration: carryover unresolved blocks unknown
  - 前提: CI passed, head matched, selected unresolved count is zero, and carryover non-outdated unresolved count is greater than zero.
  - 操作: run provider snapshot and wait path with fake `gh`.
  - 期待結果: no `review_completion_unknown`; `summary.review="unresolved"`; `recommended_next_action="address_review_feedback"`; reason `carryover_non_outdated_unresolved_thread`.
  - 失敗検出: stable unknown hides carryover review work.
  - 検証方法: pytest fake-`gh` snapshot/wait test.

- `tc-s420-002` integration: current-selected reason wins over carryover
  - 前提: current-selected unresolved and carryover non-outdated unresolved both exist.
  - 操作: run provider snapshot.
  - 期待結果: decision reason is current-selected; carryover IDs remain listed in inventory.
  - 失敗検出: lower-priority carryover reason obscures current review feedback.
  - 検証方法: pytest fake-`gh` snapshot test.

- `tc-s420-003` negative: pending review beats unknown
  - 前提: no actionable unresolved inventory, no trusted completion, and pending review request or current pending review signal exists.
  - 操作: run provider wait path.
  - 期待結果: pending/wait-or-resume state remains; no `review_completion_unknown`.
  - 失敗検出: in-progress review becomes terminal-like human gate.
  - 検証方法: pytest fake-`gh` wait test.

- `tc-s420-004` acceptance: trusted completion passes only when inventory is empty
  - 前提: CI passed, head matched, trusted `submitted_pull_request_review` exists, and actionable inventory is zero.
  - 操作: run provider snapshot.
  - 期待結果: existing merge-prepared/pass-compatible behavior remains intact.
  - 失敗検出: inventory additions break existing trusted review completion path.
  - 検証方法: existing trusted completion test plus focused assertion.

- `tc-s420-005` acceptance: stable no-completion remains possible with empty inventory
  - 前提: CI passed, head matched, no pending/blocking state, no trusted completion, and actionable inventory is zero.
  - 操作: run provider wait path beyond stability and latency gates.
  - 期待結果: `review_completion_unknown` remains possible and non-pass human gate.
  - 失敗検出: S400+ inventory work removes the useful no-completion escape hatch.
  - 検証方法: pytest fake-`gh` wait test.

Step closure contract:

- Close when precedence tests pass and code-reviewer passes.
- Verification command: `uv run pytest tests/unit/infra/test_init_update.py -k "review_inventory or review_completion_unknown or pr_observation_snapshot or pr_observation_wait or issue_187"`.
- Report destinations: TDD Evidence, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate, Delegated Worker Evidence.

### S430 - Wait next-poll budget guard and post-unknown latency/audit metadata

- Observable behavior: wait loop reserves enough budget for a meaningful next snapshot, preserves the latest useful payload when a final poll would be under-budget, raises CI-passed unknown latency default to `300` seconds, and marks post-unknown fresh audit as required.
- Depends on: S420.
- Unblocks: S490.
- Target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`.
  - `tests/unit/infra/test_init_update.py`.
- Review gate: `code-reviewer`.
- Commit boundary: wait-loop timing and metadata only.

Delegation contract:

- delegated role: `dev-coder`.
- input docs: discussions `14`/`15`, design S400+ wait budget guard and post-unknown fresh audit, S420 decision output contract.
- allowed paths: provider wait module and focused tests.
- forbidden changes: no review inventory classifier changes, no snapshot precedence changes, no public shell CLI flags, no global timeout increase as the primary fix, no docs/mirror sync.
- acceptance criteria: sleep reserves next-poll budget; under-budget final poll is skipped when latest useful payload exists; useful payload is not overwritten by all-unknown timeout; `wait.final_poll_skipped_reason="insufficient_next_snapshot_budget"` appears when applicable; `review_completion_unknown_min_ci_passed_age_seconds=300`; `wait.post_unknown_fresh_audit_required=true` when unknown is emitted.
- required tests: fake snapshot/wait tests for budget reservation, payload preservation, no hiding terminal failures, latency default, and post-unknown audit metadata.
- reviewer focus: deadline math, timeout preservation, terminal failure precedence, compatibility with stdout/stderr/out artifacts, no pass/human-gate weakening.
- output required: changed files, red/green evidence, test command summaries, any timing constants, and unresolved risk.
- stop conditions: preserving latest payload would hide a real failed/stale/unresolved terminal state; implementation requires new public flags; test can pass only by increasing total timeout.

Concrete test cases:

- `tc-s430-001` regression: sleep reserves next-poll budget
  - 前提: a meaningful non-terminal payload needs one more quiet/same-fingerprint poll before deadline.
  - 操作: run wait test with fake snapshot timing and poll interval.
  - 期待結果: computed sleep leaves `wait.next_poll_min_budget_seconds` available.
  - 失敗検出: loop sleeps until deadline and leaves only fractional time for next snapshot.
  - 検証方法: pytest fake wait-loop timing test.

- `tc-s430-002` regression: under-budget final poll preserves latest useful payload
  - 前提: latest payload has CI/head/review evidence, and remaining time is below next-poll minimum.
  - 操作: run wait path to deadline.
  - 期待結果: no under-budget snapshot starts; result keeps latest payload and adds `wait.final_poll_skipped_reason="insufficient_next_snapshot_budget"`.
  - 失敗検出: final result becomes all-unknown timeout and loses useful evidence.
  - 検証方法: pytest fake snapshot call-log and final JSON assertions.

- `tc-s430-003` negative: budget guard does not hide terminal failures
  - 前提: latest payload or next available payload contains failed CI, stale head, or actionable unresolved review.
  - 操作: run wait path with tight deadline.
  - 期待結果: terminal failure/actionable state remains visible; budget guard does not soften it into unknown.
  - 失敗検出: budget guard masks a real blocker.
  - 検証方法: pytest parametrized wait test.

- `tc-s430-004` negative: CI-passed age below 300 seconds does not promote unknown
  - 前提: CI passed 124 seconds ago, trigger age is sufficient, no actionable inventory exists, and no completion signal exists.
  - 操作: run wait path beyond quiet/same-fingerprint stability.
  - 期待結果: `review_completion_unknown` is not emitted before the 300 second CI-passed age guard.
  - 失敗検出: PR #190 late-review window remains reproducible.
  - 検証方法: pytest fake wait test using PR #190-like timing.

- `tc-s430-005` acceptance: post-unknown fresh audit metadata is emitted
  - 前提: CI/head passed, actionable inventory empty, no pending/blocking state, and all latency/stability gates are satisfied.
  - 操作: run wait path to `review_completion_unknown`.
  - 期待結果: final JSON has `wait.post_unknown_fresh_audit_required=true` and includes latest actionable inventory fields.
  - 失敗検出: downstream can misread unknown as review absence proof.
  - 検証方法: pytest fake wait test.

Step closure contract:

- Close when S430 tests pass and code-reviewer passes.
- Verification command: `uv run pytest tests/unit/infra/test_init_update.py -k "next_poll_budget or insufficient_next_snapshot_budget or post_unknown_fresh_audit or review_completion_unknown or pr_observation_wait"`.
- Report destinations: TDD Evidence, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate, Delegated Worker Evidence.

### S490 - Docs impact and dogfooding mirror sync

- Observable behavior: provider docs and dogfooding mirror reflect S410-S430 behavior and changed provider assets match mirror files where intended.
- Depends on: S410-S430.
- Unblocks: S499.
- Target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md` if operator-facing semantics changed.
  - `.agents/skills/github-pr-observation/SKILL.md` if provider docs changed.
  - `.agents/skills/github-pr-observation/scripts/**` corresponding to changed provider files.
  - focused asset tests if new/moved files are involved.
- Review gate: `spec-reviewer` for docs wording and `code-reviewer` for mirror/scaffold sync if script assets are copied.
- Commit boundary: docs and mirror sync only.

Delegation contract:

- delegated roles: `doc-writer` for skill text; `dev-coder` or `utility-worker` for mechanical mirror sync.
- input docs: canonical S400+ plan, S410-S430 report evidence, changed provider files.
- allowed paths: provider/mirror `SKILL.md`, mirror files corresponding to changed provider scripts/modules, and focused asset tests only if needed.
- forbidden changes: no provider behavior changes, no tests unrelated to scaffold/mirror presence, no claim that PR #190 is merge-ready.
- acceptance criteria: docs explain actionable review inventory, `review_completion_unknown` as non-pass and not review absence proof, post-unknown fresh audit requirement, and next-poll budget preservation where operator-visible; provider/mirror changed files are byte-identical where intended.
- required verification: `cmp -s` or checksums for changed provider/mirror files, `git diff --check`, focused asset tests if scaffold file set changed.
- reviewer focus: docs/spec alignment, mirror equality, no behavior drift during sync.
- output required: changed files, comparison results, docs inspection summary, reviewer evidence, unresolved risks.
- stop conditions: docs would contradict requirement/design; provider and mirror cannot align; behavior change is needed during docs-only step.

Concrete test cases:

- `tc-s490-001` docs: operator-facing semantics are documented
  - 前提: S410-S430 behavior is implemented.
  - 操作: inspect provider and mirror `SKILL.md`.
  - 期待結果: docs state actionable review inventory and post-unknown fresh audit semantics without claiming unknown means no review work.
  - 失敗検出: operators or agents treat `review_completion_unknown` as merge-ready/no-review evidence.
  - 検証方法: docs inspection recorded in `report.md`.

- `tc-s490-002` scaffold: provider and mirror changed files match
  - 前提: provider S410-S430 files changed and corresponding mirror paths exist.
  - 操作: compare provider and mirror files.
  - 期待結果: changed mirror files are identical where intended, or intentional differences are recorded.
  - 失敗検出: dogfooding observation runs stale logic.
  - 検証方法: `cmp -s` or checksum comparison.

- `tc-s490-003` scaffold: installed asset set remains complete
  - 前提: S410-S430 touch shipped provider assets.
  - 操作: run existing init/update asset coverage or focused inspection.
  - 期待結果: shipped files required by wrappers/modules are present in installed asset surface.
  - 失敗検出: consumer repo cannot run the updated observation scripts.
  - 検証方法: focused pytest or asset tree inspection.

Step closure contract:

- Close when docs/mirror verification and applicable reviewer gates pass.
- Verification command: `git diff --check` plus provider/mirror `cmp -s` commands for touched files; focused pytest if asset coverage changes.
- Report destinations: Docs Impact Resolution, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate.

### S499 - Final quality and live PR observation gate

- Observable behavior: S400+ lane has focused/broad validation, final reviewer gates, SpecDock validation, provider/mirror checks, and live PR #190 final re-observation on latest head.
- Depends on: S490.
- Target files: issue-wide diff and `spec-dock/active/issue/report.md`.
- Review gates: `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`.
- Commit boundary: final evidence/report only; no catch-up behavior implementation.

Delegation contract:

- delegated roles: `qa-reviewer`, `code-reviewer`, `spec-reviewer`.
- input docs: canonical requirement/design/plan/report, S410-S490 diffs and evidence, latest PR #190 observation output.
- allowed paths: final report evidence only, unless a reviewer finding creates a bounded follow-up assigned back to S410/S420/S430/S490.
- forbidden changes: no behavior changes in S499, no final commit before reviewer pass, no stale PR observation as final evidence, no merge-ready claim while actionable unresolved review remains.
- acceptance criteria: focused tests pass, broader relevant test lane passes or failures are explained, `git diff --check` passes, `./spec-dock/scripts/spec-dock validate` passes, provider/mirror comparisons pass, live PR #190 final observation records latest head and actionable review inventory.
- required verification:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187 or pr_observation or review_inventory or actionable_unresolved or next_poll_budget or review_completion_unknown"`
  - `uv run pytest tests/unit/infra/test_init_update.py -q`
  - `git diff --check`
  - `./spec-dock/scripts/spec-dock validate`
  - provider/mirror `cmp -s` for touched files
  - fresh PR #190 observation after push.
- reviewer focus:
  - qa-reviewer: risk-calibrated test sufficiency, fake-`gh` coverage, late-review / budget race coverage.
  - code-reviewer: integrated provider/mirror/runtime/test diff, compatibility, false-pass safety.
  - spec-reviewer: requirement/design/plan/report alignment and closure evidence.
- output required: final validation summary, reviewer verdicts, PR #190 latest head SHA, actionable inventory fields, unresolved blockers or `none`, and final next action.
- stop conditions: any reviewer fails; PR #190 observation is stale or head mismatch; actionable unresolved review remains and workflow attempts merge-prepared reporting.

Concrete test cases:

- `tc-s499-001` quality: focused S400+ fake-`gh` regression suite passes
  - 前提: S410-S490 are complete.
  - 操作: run focused pytest selector for S400+ and PR observation.
  - 期待結果: all focused tests pass or failures are attributed to unrelated baseline with evidence.
  - 失敗検出: S400+ closure relies on untested script behavior.
  - 検証方法: pytest command output recorded in report.

- `tc-s499-002` quality: final reviewer triad passes
  - 前提: final issue-wide diff and report evidence are ready.
  - 操作: run `qa-reviewer`, issue-wide `code-reviewer`, and `spec-reviewer`.
  - 期待結果: all return `review_status: pass`.
  - 失敗検出: final QA/code/spec gate is replaced by implementation worker output.
  - 検証方法: reviewer evidence in `report.md`.

- `tc-s499-003` live gate: PR #190 final re-observation uses latest head
  - 前提: S400+ changes are pushed or otherwise available for dogfooding observation.
  - 操作: run PR observation against latest PR #190 head.
  - 期待結果: report records latest head SHA, CI/head status, `decision.actionable_unresolved_count`, current-selected IDs, carryover IDs, and comment `3422572159` status if still unresolved and non-outdated.
  - 失敗検出: stale pre-fix observation is reused as final evidence or P2 review remains hidden.
  - 検証方法: live observation JSON summary recorded in `report.md`.

- `tc-s499-004` validation: SpecDock and diff hygiene pass
  - 前提: final diff is ready.
  - 操作: run `git diff --check` and `./spec-dock/scripts/spec-dock validate`.
  - 期待結果: both pass or blockers are reported.
  - 失敗検出: final handoff includes whitespace/schema/spec-dock validation defects.
  - 検証方法: command evidence in `report.md`.

Step closure contract:

- Close only when all final validations and reviewer gates pass, or blocker is recorded with next action.
- Report destinations: Final QA Gate, Final Code Review Gate, Final Spec Review Gate, PR Observation Gate, Closure Coverage, Step Commit Gate, Final Commit.

## 6. Test Strategy Mapping

Spec-locked closure rows to add if adopted:

| ID | Step | Type | Locked expectation | Evidence level |
|---|---|---|---|---|
| `tc-s400-001` | S400 | authoring | S400+ delegated evidence is ledgered before canonical use | inspect-only |
| `tc-s400-002` | S400 | authoring | fresh `spec-reviewer` pass gates S410 | manual-required |
| `tc-s410-001` | S410 | acceptance | current-selected unresolved is actionable | red-required |
| `tc-s410-002` | S410 | acceptance | carryover non-outdated unresolved is actionable | red-required |
| `tc-s410-003` | S410 | negative | outdated-only unresolved remains audit-only | red-required |
| `tc-s410-004` | S410 | negative | unknown outdated state is not promoted | red-required |
| `tc-s410-005` | S410 | regression | selected/carryover inventory dedupes | red-required |
| `tc-s420-001` | S420 | integration | carryover unresolved blocks unknown | red-required |
| `tc-s420-002` | S420 | integration | current-selected reason wins | red-required |
| `tc-s420-003` | S420 | negative | pending review beats unknown | red-required |
| `tc-s420-004` | S420 | regression | trusted completion still passes when inventory empty | covered-existing plus focused assertion |
| `tc-s420-005` | S420 | regression | stable no-completion remains possible when inventory empty | covered-existing plus focused assertion |
| `tc-s430-001` | S430 | regression | wait sleep reserves next-poll budget | red-required |
| `tc-s430-002` | S430 | regression | under-budget final poll preserves latest useful payload | red-required |
| `tc-s430-003` | S430 | negative | budget guard does not hide terminal failures | red-required |
| `tc-s430-004` | S430 | negative | CI-passed age below 300 does not promote unknown | red-required |
| `tc-s430-005` | S430 | acceptance | post-unknown fresh audit metadata is emitted | red-required |
| `tc-s490-001` | S490 | docs | operator-facing semantics are documented | inspect-only |
| `tc-s490-002` | S490 | scaffold | provider/mirror changed files match | inspect-only |
| `tc-s490-003` | S490 | scaffold | installed asset set remains complete | covered-existing or inspect-only |
| `tc-s499-001` | S499 | quality | focused S400+ fake-`gh` regressions pass | manual-required |
| `tc-s499-002` | S499 | quality | final reviewer triad passes | manual-required |
| `tc-s499-003` | S499 | live | PR #190 final re-observation uses latest head | manual-required |
| `tc-s499-004` | S499 | validation | SpecDock and diff hygiene pass | manual-required |

Primary automated home remains `tests/unit/infra/test_init_update.py` with fake `gh`. No live GitHub API test is required before implementation commits, but S499 requires a live PR #190 observation gate after push because this issue is about PR observation workflow safety.

## 7. Review Gates

- S400: `spec-reviewer` only; confirms canonical plan adoption and traceability.
- S410: `code-reviewer`; confirms review inventory classification safety.
- S420: `code-reviewer`; confirms precedence and summary alignment.
- S430: `code-reviewer`; confirms wait budget, timing, and metadata.
- S490: `doc-writer` worker plus `spec-reviewer` for docs; `code-reviewer` for mirror/script sync if mixed.
- S499: `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`.

Reviewer output is not replaced by delegated worker output. A failed reviewer gate sends the work back to the relevant bounded step before commit.

## 8. Rollback / Compatibility

- JSON changes are additive. Do not remove `decision.selected_unresolved_count`, `decision.selected_review_thread_ids`, `review.threads.*`, or existing `summary.review` fields.
- If carryover classification over-blocks, rollback only the carryover promotion path while preserving current-selected behavior and audit fields.
- If next-poll budget guard prematurely stops, rollback under-budget poll skipping while preserving tests that prove latest payload degradation.
- Public shell CLI options, stdout final JSON authority, stderr diagnostics, and out artifact contract remain unchanged.
- Provider source remains the source of truth; mirror changes can be reverted independently only if provider/mirror drift is explicitly recorded as a blocker.

## 9. Docs Impact

S490 should update docs only if operator-facing behavior changed. Expected docs content:

- `review_completion_unknown` is non-pass human gate and not review absence proof.
- Actionable review inventory is the merge-prepared / repair-batch input, not `selected_unresolved_count` alone.
- Post-unknown fresh audit is required before reporting no review work or merge-prepared.
- Wait loop preserves latest useful payload when a final poll lacks enough budget.

Docs must not claim PR #190 is merge-ready or that unknown means no action is required.

## 10. Final Quality Gate

S499 final gate requires:

- Focused S400+ fake-`gh` test selector.
- Broader `tests/unit/infra/test_init_update.py -q` or justified narrower equivalent only if runtime constraints require.
- `git diff --check`.
- `./spec-dock/scripts/spec-dock validate`.
- Provider/mirror comparisons for all touched assets.
- Final `qa-reviewer`, issue-wide `code-reviewer`, and `spec-reviewer` pass.
- Live PR #190 final observation on latest head after push, including actionable review inventory and fresh audit evidence.

Final report must not classify the issue as merge-prepared while actionable unresolved review inventory is non-empty or PR observation is stale.

## 11. Plan Blockers

Blocking:

- none identified for drafting the S400+ plan addendum.

Execution blockers if discovered later:

- Review thread payload cannot reliably expose `isResolved=false` and `isOutdated=false` for carryover classification.
- Existing implementation location differs from design file plan enough that S410/S420 ownership is ambiguous.
- Fresh `spec-reviewer` rejects treating actionable review inventory as design-level strengthening without requirement amendment.

Clarification candidates for main orchestrator:

- Whether S400+ canonical adoption should add new requirement AC rows, or keep the behavior as AC-006/AC-007 design strengthening.
- Whether `review_completion_unknown_min_ci_passed_age_seconds=300` should remain hard-coded or become an internal named constant only.
- Whether merge-preparer workflow changes should become a separate follow-up issue after observation payload exposes actionable inventory.

## 12. Integration Notes for Main Orchestrator

- This draft is intended to be appended after existing S300+ plan content; do not rewrite S01-S399.
- If adopted, insert the S400+ closure rows into the canonical `Spec-Locked Closure Index` and append the step sections to canonical `plan.md`.
- Record this draft and discussions `14`, `15`, and `16` in `report.md` Evidence Adoption Ledger before using them as canonical evidence.
- Run fresh `spec-reviewer` on canonical `plan.md` after adoption.
- S400+ should not start implementation until S400 authoring gate is closed.
- Final S499 live PR #190 observation must use the latest PR head, not stale observation artifacts from `bb50b7a2`.

Lightweight provenance:

- created_by_role: `implementation-planner`
- leaf evidence used: none beyond required local docs/discussions
- forbidden actions avoided: no canonical edits, no implementation/test/config edits, no GitHub mutation, no phase promotion, no reviewer-pass claim
- unresolved design gaps: none blocking; clarification candidates listed above

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.

review_status: draft-ready
