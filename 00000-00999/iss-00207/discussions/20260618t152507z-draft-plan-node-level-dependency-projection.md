---
created_by_role: implementation-planner
scope_id: iss-00207
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/plan.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00207-fix-dependency-projections-for-node-level-blockers/discussions/20260618t145427z-research-node-level-dependency-projection-failure-analysis.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00207-fix-dependency-projections-for-node-level-blockers/discussions/20260618t151109z-draft-design-node-level-dependency-projection.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/contracts.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/models.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/puml.py
  - src/spec_dock/assets/spec_dock/docs/reference_deps.md
  - src/spec_dock/assets/spec_dock/docs/reference_sync.md
  - tests/cli_runtime/test_deps.py
  - tests/cli_runtime/test_sync.py
  - tests/cli_runtime/test_issue_lifecycle.py
  - tests/unit/domain/test_runtime_domain_s03.py
  - tests/unit/presentation/test_runtime_sync_s07.py
  - tests/unit/presentation/test_deps_raw_puml.py
intended_targets:
  - plan.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# Node-level dependency projection implementation-plan draft for iss-00207

This is delegated draft planning evidence only. It does not edit canonical `plan.md`, does not claim implementation readiness, and must be adopted by the main orchestrator with a fresh `spec-reviewer` pass before execution.

Source requirement revision: `iss-00207` requirement last updated `2026-06-18`; user input states a fresh reviewer pass has no findings. Source design revision: `iss-00207` design last updated `2026-06-18`; user input states a fresh reviewer pass has no findings after P1 fixes.

Provider-side source of truth is `src/spec_dock/assets/spec_dock/...`. The dogfooding workspace under `spec-dock/...` is mirror / validation evidence. Legacy monolithic `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py` and dogfooding `spec-dock/scripts/spec_dock_runtime/app.py` must not be used as implementation source of truth.

## 1. Plan Summary

Implement the fix in dependency order:

1. S01 contract/model + topology facts: preserve raw node dependencies and empty expansion context instead of reducing them to warning-only output.
2. S02 domain evaluation: convert topology context into issue blockers, node blockers, satisfied dependencies, and fail-closed unknown handling.
3. S03 command guards: make `deps check`, `active set`, and `issue start` consume the same evaluation and expose typed blocker context.
4. S04 sync/presentation: generate `deps-issues` v2 and `deps-raw` visual state from `SyncStateResult` without deriving readiness in renderers.
5. S90 docs impact + dogfooding mirror: update provider docs and refresh / inspect the dogfooding mirror intentionally.
6. S99 final quality gate: run issue-wide tests, QA review, code review, spec review, and final diff guard.

Execution standard: one implementation step at a time; each step is one review scope and one commit boundary. S90 and S99 are gates, not substitutes for per-step review / commit.

## 2. Requirement / Design Traceability

| Requirement | Closure id | Owner step | Locked implementation meaning |
|---|---|---|---|
| AC-001 | cl-ac-001 | S02, S03 | Empty open high-level dependency produces `node_blockers`, `ready=false`, non-zero `deps check`, and active/start guard rejection. |
| AC-002 | cl-ac-002 | S02, S04 | Empty done / closed high-level dependency is not a blocker and remains visible as satisfied raw/debug context. |
| AC-003 | cl-ac-003 | S01, S02 | Non-empty high-level dependency keeps existing child issue expansion; open children block and done children do not. |
| AC-004 | cl-ac-004 | S04 | `deps-issues` includes readiness and blocker/satisfied context; todo-only filtering cannot hide required context. |
| AC-005 | cl-ac-005 | S04 | `deps-raw.puml` displays high-level participant state from payload, not renderer inference. |
| AC-006 | cl-ac-006 | S90, S99 | Provider docs and regression tests pin the new contract and authority boundary. |
| EC-001 | cl-ec-001 | S02, S03, S04 | Unknown high-level target state is fail-closed with observable unknown reason/context. |
| EC-002 | cl-ec-002 | S02, S04 | Done child-only dependencies are non-blocking and remain visible as satisfied context. |
| EC-003 | cl-ec-003 | S01, S99 | Raw node-level cycle validation stays fail-closed before readiness projection. |
| EC-004 | cl-ec-004 | S90, S99 | Docs and generated labels prevent treating `deps-raw.puml` as readiness authority. |

## 3. Milestones

- M1 topology contract fixed: S01 reviewed and committed.
- M2 readiness semantics fixed: S02 reviewed and committed.
- M3 command guard parity fixed: S03 reviewed and committed.
- M4 generated artifact contract fixed: S04 reviewed and committed.
- M5 docs and dogfooding mirror aligned: S90 reviewed and committed.
- M6 final verification complete: S99 evidence recorded; no unresolved required closure.

## 4. Dependency-Derived Execution Order

Design dependency path: `infra/deps_reader.py` and `infra/contracts.py` feed `domain/deps.py`; domain evaluation feeds `application/check_deps.py`, `application/set_active.py`, `application/issue_lifecycle.py`, and `application/sync_state.py`; sync state feeds `presentation/json_state.py` and `presentation/puml.py`; docs/tests lock the shipped contract.

Do not begin a downstream step until the upstream step is reviewed and committed:

| Step | Depends on | Unblocks | Main paths |
|---|---|---|---|
| S01 | fresh requirement/design pass | S02 | `infra/contracts.py`, `infra/deps_reader.py`, `domain/models.py`, focused infra/domain tests |
| S02 | S01 commit | S03, S04 | `domain/deps.py`, `domain/models.py`, domain tests |
| S03 | S02 commit | S04 CLI parity assertions | `application/check_deps.py`, `application/set_active.py`, `application/issue_lifecycle.py`, CLI text/JSON tests |
| S04 | S02 and S03 commits | S90 | `application/sync_state.py`, `application/contracts.py`, `presentation/json_state.py`, `presentation/puml.py`, sync/presentation tests |
| S90 | S04 commit | S99 | provider docs under `src/spec_dock/assets/spec_dock/docs/`, dogfooding mirror inspection/update |
| S99 | S01-S90 commits | issue ready/finish decision by main orchestrator | verification only, report evidence, reviews |

## 5. Issue / Step Slicing

### S01 - Contract/model + topology facts

- Behavior goal: `load_issue_depends_on_map()` returns issue-level expansion plus lossless raw node dependency context for domain evaluation.
- Dependencies/unblock: no implementation dependency; unblocks S02.
- Allowed paths: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/contracts.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/models.py`, focused tests under `tests/unit/infra/` or `tests/unit/domain/test_runtime_domain_s03.py`.
- Forbidden changes: no `.meta.json.depends_on` storage change; no validation error for empty high-level dependency; no edits to legacy `app.py`; no command/presentation behavior changes in this step.
- Delegated role: `dev-coder`.
- Required Red / characterization evidence: add or update a focused test showing an issue depending on an empty epic currently only yields `deps_ref_expanded_to_empty` and lacks topology context; add a non-empty epic characterization to protect existing child expansion.
- Green verification command: `uv run pytest tests/unit/domain/test_runtime_domain_s03.py tests/cli_runtime/test_sync.py -k "empty or expands or effective_deps or cycle"`
- Reviewer focus: model compatibility, deterministic ordering, raw-vs-compiled separation, no readiness decisions in infra.
- Closure ids: `cl-ac-003`, partial `cl-ec-003`.
- Stop/amendment triggers: if preserving `DepsTopologyLoadResult.issue_depends_on_map` is impossible; if a new storage format is required; if empty high-level dependencies must become validation errors.

Concrete test case seeds:

- `tc-s01-001` characterization: empty epic dependency retains topology context
  - Premise: temp graph has `iss-00301` depending on `epic-00202`; `epic-00202` has zero child issues.
  - Operation: call `load_issue_depends_on_map()` or the smallest public reader-facing path.
  - Expected: `issue_depends_on_map["iss-00301"] == []`, warning includes `deps_ref_expanded_to_empty`, and new context records `iss-00301 -> epic-00202` with empty expansion.
  - Failure detection: context is absent, so S02 cannot distinguish empty open from empty done.
  - Verification method: focused unit test; red before S01 implementation.
  - Related closure id: `cl-ac-001`, `cl-ec-001`.

- `tc-s01-002` regression: non-empty epic keeps compiled child issue expansion
  - Premise: `iss-00301` depends on `epic-00202`; `epic-00202` contains `iss-00401` and `iss-00402`.
  - Operation: load topology.
  - Expected: compiled map contains `iss-00301 -> iss-00401` and `iss-00301 -> iss-00402`; raw context still records the direct epic edge.
  - Failure detection: child expansion disappears or duplicate / unordered edges appear.
  - Verification method: unit or CLI characterization based on existing `test_sync_compiles_shorthand_to_issue_edges`.
  - Related closure id: `cl-ac-003`.

- `tc-s01-003` regression: raw node cycle preflight remains fail-closed
  - Premise: raw direct dependencies create a cycle across initiative / epic / issue nodes.
  - Operation: run `validate_raw_node_dependency_graph()` through existing preflight path.
  - Expected: command fails before readiness projection and before artifact rendering.
  - Failure detection: cycle is downgraded to a warning or appears as a ready graph.
  - Verification method: existing cycle test plus targeted assertion if topology context changes the map shape.
  - Related closure id: `cl-ec-003`.

### S02 - Domain readiness evaluation

- Behavior goal: `domain/deps.py` evaluates issue blockers, node blockers, satisfied dependencies, and unknown high-level blockers from S01 context.
- Dependencies/unblock: requires S01 context model; unblocks command guards and sync/presentation.
- Allowed paths: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/models.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`, `tests/unit/domain/test_runtime_domain_s03.py`, `tests/unit/domain/test_deps.py`.
- Forbidden changes: no GitHub I/O in domain; no presentation fields computed in renderer; no removal of `blockers`, `blockers_top`, or `closure`; no issue-only assumption for new typed fields.
- Delegated role: `dev-coder`.
- Required Red / characterization evidence: red test for empty open epic blocking and empty closed/done epic non-blocking; characterization for existing done issue dependency not reappearing as blocker.
- Green verification command: `uv run pytest tests/unit/domain/test_runtime_domain_s03.py tests/unit/domain/test_deps.py`
- Reviewer focus: fail-closed unknown behavior, compatibility of `DepsEvaluation.blockers`, deterministic `issue_blockers` / `node_blockers`, status source rules.
- Closure ids: `cl-ac-001`, `cl-ac-002`, `cl-ac-003`, `cl-ec-001`, `cl-ec-002`.
- Stop/amendment triggers: if design's high-level status priority cannot be implemented without application-layer status enrichment; if `blockers` cannot safely include node IDs; if new durable semantics not in design are needed.

Concrete test case seeds:

- `tc-s02-001` acceptance: empty open epic blocks target issue
  - Premise: `iss-00301` is open and directly depends on empty open `epic-00202`.
  - Operation: call `evaluate_readiness()` or `inspect_target_deps()` with topology context.
  - Expected: `ready=false`, `guard_reason="blocked"`, `blockers` includes `epic-00202`, `node_blockers[0].reason=="empty_open"`, `issue_blockers==[]`.
  - Failure detection: target remains ready or node blocker only appears in warnings.
  - Verification method: red-first domain test.
  - Related closure id: `cl-ac-001`.

- `tc-s02-002` acceptance: empty closed epic is satisfied
  - Premise: `iss-00301` depends on empty `epic-00202` with closed/done authoritative state.
  - Operation: evaluate readiness.
  - Expected: `ready=true`, no blocker for `epic-00202`, and `satisfied_dependencies` records the raw direct high-level dependency.
  - Failure detection: closed high-level target blocks readiness or disappears from debug context.
  - Verification method: red-first domain test.
  - Related closure id: `cl-ac-002`.

- `tc-s02-003` edge: empty unknown epic fails closed
  - Premise: `iss-00301` depends on empty high-level target with no GitHub/cache/descendant state.
  - Operation: evaluate readiness.
  - Expected: `ready=false`, `guard_reason="unknown"`, `node_blockers` reason is `empty_unknown`.
  - Failure detection: unknown target is treated as ready.
  - Verification method: domain test.
  - Related closure id: `cl-ec-001`.

- `tc-s02-004` regression: done child-only dependency stays non-blocking
  - Premise: high-level target has one or more child issues and all are done.
  - Operation: evaluate dependent issue readiness.
  - Expected: no issue blocker, ready remains true, satisfied context remains available.
  - Failure detection: done child issue returns to `blockers`.
  - Verification method: domain test extending existing done-dependency coverage.
  - Related closure id: `cl-ec-002`.

### S03 - Command guards and CLI output

- Behavior goal: `deps check`, `active set`, and `issue start` enforce the same node-level blocker semantics and expose enough text/JSON context for operators.
- Dependencies/unblock: requires S02 `DepsEvaluation` contract; unblocks S04 CLI parity assumptions.
- Allowed paths: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py` only for `deps check --json`, CLI text renderer if required, `tests/cli_runtime/test_deps.py`, `tests/cli_runtime/test_issue_lifecycle.py`, `tests/unit/application/test_check_deps.py`, `tests/unit/application/test_set_active.py`.
- Forbidden changes: no bypass of dependency guard through `--force`; no GitHub mutation; no unrelated branch lifecycle behavior change; no change to storage or presentation artifacts.
- Delegated role: `dev-coder`.
- Required Red / characterization evidence: CLI red tests for `deps check --json` non-zero on empty open epic, `active set` rejection, and `issue start --force` still respecting dependency guard.
- Green verification command: `uv run pytest tests/cli_runtime/test_deps.py tests/cli_runtime/test_issue_lifecycle.py tests/unit/application/test_check_deps.py tests/unit/application/test_set_active.py -k "deps_check or active or issue_start or node"`
- Reviewer focus: exit code contract, JSON schema v2 shape, typed blocker fields, guard message readability, consistency across commands.
- Closure ids: `cl-ac-001`, `cl-ec-001`.
- Stop/amendment triggers: if `issue start` currently reaches dependency checking only via `active set` and cannot be changed without lifecycle redesign; if JSON compatibility requires a schema strategy beyond design.

Concrete test case seeds:

- `tc-s03-001` acceptance: `deps check --json` fails on empty open epic
  - Premise: temp repo has open `iss-00301` depending on empty open `epic-00202`.
  - Operation: `spec-dock deps check --id iss-00301 --github --json` with `gh` stub marking the epic open.
  - Expected: exit code non-zero, payload `schema_version==2`, `ready==false`, `blockers` includes `epic-00202`, `node_blockers` includes reason/state/source.
  - Failure detection: exit code 0 or only `warnings=["deps_ref_expanded_to_empty"]`.
  - Verification method: CLI runtime test.
  - Related closure id: `cl-ac-001`.

- `tc-s03-002` acceptance: `active set` rejects node-blocked issue
  - Premise: same fixture as `tc-s03-001`.
  - Operation: `spec-dock active set iss-00301`.
  - Expected: command fails, active pointer is not updated, stderr names `epic-00202` and reason.
  - Failure detection: active issue becomes `iss-00301`.
  - Verification method: CLI/runtime or application test with active store assertion.
  - Related closure id: `cl-ac-001`.

- `tc-s03-003` acceptance: `issue start --force` does not bypass dependency guard
  - Premise: node-blocked target issue and no unrelated lifecycle blocker.
  - Operation: `spec-dock issue start iss-00301 --force`.
  - Expected: command fails because dependency guard remains blocking; no checkout/active mutation occurs.
  - Failure detection: force starts the blocked issue.
  - Verification method: extend `tests/cli_runtime/test_issue_lifecycle.py`.
  - Related closure id: `cl-ac-001`.

- `tc-s03-004` edge: warning-only satisfied context exits zero
  - Premise: target depends on empty closed epic or done child-only epic.
  - Operation: `spec-dock deps check --id iss-00301 --github --json`.
  - Expected: exit code 0, `ready=true`, no `node_blockers`, satisfied dependency context present.
  - Failure detection: satisfied-only context causes non-zero exit.
  - Verification method: CLI runtime test.
  - Related closure id: `cl-ac-002`, `cl-ec-002`.

### S04 - Sync state and presentation artifacts

- Behavior goal: `sync` emits lossless readiness context into `.agent/deps-issues.json`, `deps-issues.puml`, and `deps-raw.puml`.
- Dependencies/unblock: requires S02 evaluation and S03 command shape decisions; unblocks docs/dogfooding.
- Allowed paths: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/puml.py`, `tests/cli_runtime/test_sync.py`, `tests/unit/presentation/test_runtime_sync_s07.py`, `tests/unit/presentation/test_deps_raw_puml.py`.
- Forbidden changes: no renderer-side readiness inference; no `index.json` reparse as source for `deps-issues`; no all-history graph dump when only readiness context is needed; no claim that `deps-raw` is readiness authority.
- Delegated role: `dev-coder`.
- Required Red / characterization evidence: red tests for `deps-issues` v2 including high-level blocker and satisfied edge; presentation unit test that high-level packages receive payload-derived state; characterization that disabled deps preflight output remains.
- Green verification command: `uv run pytest tests/cli_runtime/test_sync.py tests/unit/presentation/test_runtime_sync_s07.py tests/unit/presentation/test_deps_raw_puml.py`
- Reviewer focus: schema v2 shape, node inclusion boundaries, edge labels (`blocking` vs `satisfied`), deterministic sorting, payload/renderer responsibility separation.
- Closure ids: `cl-ac-004`, `cl-ac-005`, `cl-ac-002`, `cl-ec-001`, `cl-ec-002`.
- Stop/amendment triggers: if `SyncStateResult` cannot carry required typed contexts without duplicating readiness rules; if docs require a new artifact instead of changing `deps-issues`; if snapshot size becomes unbounded.

Concrete test case seeds:

- `tc-s04-001` acceptance: `deps-issues` v2 includes high-level blocker context
  - Premise: open issue depends on empty open epic, and another open issue depends on open issue prerequisite.
  - Operation: run `spec-dock sync --github --no-update-active` with stubbed GitHub states.
  - Expected: `.agent/deps-issues.json` has `schema_version==2`, projection `issue-readiness-with-dependency-context`, node for blocked issue, node for `epic-00202`, and blocking edge/reason from target to epic.
  - Failure detection: `deps-issues` nodes match todo issues only and omit the epic blocker.
  - Verification method: CLI runtime test.
  - Related closure id: `cl-ac-004`.

- `tc-s04-002` acceptance: satisfied dependencies remain visible without blocking
  - Premise: open target depends on empty closed epic and done issue prerequisite.
  - Operation: run sync.
  - Expected: target remains ready, satisfied dependency nodes/edges are visible with non-blocking state, and Puml labels do not say `blocks` for satisfied edges.
  - Failure detection: satisfied context disappears or is rendered as blocking.
  - Verification method: CLI runtime and presentation assertion.
  - Related closure id: `cl-ac-002`, `cl-ec-002`.

- `tc-s04-003` acceptance: `deps-raw.puml` colors high-level participants from payload
  - Premise: raw direct edges include `epic-00202 -> iss-00301` and `init-00102 -> iss-00302`; payload includes high-level state/source.
  - Operation: render `deps-raw.puml`.
  - Expected: initiative/epic package label or styling reflects `open`, `done`, `blocked`, or `unknown`, and legend distinguishes high-level state from issue state.
  - Failure detection: packages stay unqualified white while only issue rectangles have state.
  - Verification method: unit presentation test.
  - Related closure id: `cl-ac-005`.

- `tc-s04-004` regression: deps disabled path is preserved
  - Premise: raw cycle preflight fails and sync runs with `--force`.
  - Operation: render deps artifacts.
  - Expected: disabled Puml/JSON note remains, no misleading partial graph is rendered.
  - Failure detection: stale or partial dependency graph appears.
  - Verification method: existing disabled raw dependency view test plus deps-issues counterpart if needed.
  - Related closure id: `cl-ec-003`.

### S90 - Docs impact resolution and dogfooding mirror

- Behavior goal: provider docs explain storage, readiness authority, node blockers, satisfied dependencies, `deps-issues` v2, and `deps-raw` debug-only status; dogfooding mirror is refreshed or intentionally inspected.
- Dependencies/unblock: requires S04 final artifact contract; unblocks S99.
- Allowed paths: `src/spec_dock/assets/spec_dock/docs/reference_deps.md`, `src/spec_dock/assets/spec_dock/docs/reference_sync.md`, and generated mirror paths under `spec-dock/docs/` only if refresh is intentionally run and reviewed.
- Forbidden changes: no canonical issue `requirement.md`, `design.md`, `plan.md`, `report.md` edits as part of implementation docs step unless main orchestrator separately performs adoption; no workflow policy expansion; no source/test changes in S90.
- Delegated role: `doc-writer`.
- Required inspect-only evidence: compare provider docs against generated mirror after `uvx --from . spec-dock update .` or repo-local approved equivalent; if mirror is not updated, record why in `report.md`.
- Green verification command: `uv run pytest tests/cli_runtime/test_sync.py -k "deps"` plus docs inspection; if scaffold update is run, `git diff -- src/spec_dock/assets/spec_dock/docs/reference_deps.md src/spec_dock/assets/spec_dock/docs/reference_sync.md spec-dock/docs/reference_deps.md spec-dock/docs/reference_sync.md`.
- Reviewer focus: authority language, raw/debug wording, no implication that `deps-raw` blocks execution, provider-vs-dogfooding source-of-truth clarity.
- Closure ids: `cl-ac-006`, `cl-ec-004`.
- Stop/amendment triggers: if docs require changing workflow semantics beyond dependency reference; if generated mirror update touches broad unrelated scaffold output; if docs reveal design ambiguity.

Concrete test case seeds:

- `tc-s90-001` inspect-only: provider docs define readiness authority
  - Premise: implementation has `node_blockers`, `satisfied_dependencies`, and `deps-issues` v2.
  - Operation: inspect `reference_deps.md` and `reference_sync.md`.
  - Expected: docs state `.meta.json.depends_on` is raw storage, `deps-issues` is readiness/blocker authority, `deps-raw` is raw visual/debug only.
  - Failure detection: docs still describe empty expansion as warning-only ready behavior.
  - Verification method: docs diff inspection and `spec-reviewer`.
  - Related closure id: `cl-ac-006`, `cl-ec-004`.

- `tc-s90-002` inspect-only: dogfooding mirror is intentionally aligned or deferred
  - Premise: provider docs changed.
  - Operation: run or intentionally skip scaffold refresh with recorded rationale.
  - Expected: `spec-dock/docs/reference_deps.md` and `spec-dock/docs/reference_sync.md` mirror provider docs, or report records non-blocking deferral with reason and revisit condition.
  - Failure detection: provider docs and dogfooding docs silently diverge.
  - Verification method: diff inspection and report evidence.
  - Related closure id: `cl-ac-006`.

### S99 - Final quality gate

- Behavior goal: close issue-wide risk after all steps are reviewed and committed.
- Dependencies/unblock: S01-S90 complete.
- Allowed paths: no implementation file edits except approved reviewer fixes that go through the relevant step gate; `report.md` evidence updates by main orchestrator.
- Forbidden changes: no new feature work; no broad refactor; no GitHub close/finish/promotion claim from worker; no canonical plan adoption by this draft.
- Delegated roles: `qa-reviewer`, issue-wide `code-reviewer`, `spec-reviewer`.
- Required evidence: full closure coverage table, final test output, code review pass, QA sufficiency pass, spec review pass, post-run diff guard.
- Green verification command: `uv run pytest tests/unit tests/cli_runtime`; broaden to `uv run pytest` if S01-S04 changed shared runtime contracts enough to justify full baseline.
- Reviewer focus: missing high-value tests, compatibility of schema/fields, source-of-truth boundaries, report ledger completeness, unresolved plan blockers.
- Closure ids: all `cl-*`.
- Stop/amendment triggers: any required closure lacks evidence; any reviewer finding is P1/P2 and unresolved; final diff includes out-of-scope files; dogfooding mirror status is unexplained.

Concrete test case seeds:

- `tc-s99-001` final regression lane
  - Premise: S01-S90 changes are committed one step at a time.
  - Operation: run the final verification command.
  - Expected: targeted unit/CLI lanes pass; if full baseline is run, all tests pass or unrelated failures are classified with evidence.
  - Failure detection: dependency contract regressions outside targeted slices.
  - Verification method: command output recorded in `report.md`.
  - Related closure id: all required closure ids.

- `tc-s99-002` diff guard
  - Premise: all implementation steps are complete.
  - Operation: inspect `git diff --name-only` and `git status --short`.
  - Expected: only planned provider runtime/docs/tests and intentional dogfooding mirror files changed; no canonical spec docs changed except orchestrator adoption work.
  - Failure detection: legacy `app.py`, secrets, unrelated workflow, or unplanned canonical docs appear.
  - Verification method: final diff guard evidence in `report.md`.
  - Related closure id: `cl-ac-006`, `cl-ec-004`.

## 6. Test Strategy Mapping

Spec-Locked Closure Index:

| ID | Step | Spec link | Locked expectation | Observable input/state | Bug class guarded | Required | Evidence level | Closure evidence |
|---|---|---|---|---|---|---|---|---|
| cl-ac-001 | S02/S03 | AC-001 | Empty open initiative/epic blocks readiness and start guards. | `deps check`, `active set`, `issue start` on issue depending on empty open epic/init. | false-ready active/start | yes | red-required | domain + CLI tests |
| cl-ac-002 | S02/S04 | AC-002 | Empty done/closed high-level dependency is satisfied, not blocking. | CLI/domain/sync fixture with closed empty epic/init. | over-blocking satisfied high-level target | yes | red-required | domain + CLI/sync tests |
| cl-ac-003 | S01/S02 | AC-003 | Non-empty high-level dependency still expands to child issue blockers. | issue depends on epic with open/done child issues. | regression of existing shorthand expansion | yes | covered-existing + red-required if contract field changes | topology/domain tests |
| cl-ac-004 | S04 | AC-004 | `deps-issues` preserves blocker and satisfied context beyond todo issue set. | sync-generated `.agent/deps-issues.json` and `deps-issues.puml`. | lossy projection | yes | red-required | sync/presentation tests |
| cl-ac-005 | S04 | AC-005 | `deps-raw.puml` shows high-level participant state from payload. | raw direct edge involving initiative/epic. | uncolored/ambiguous raw participants | yes | red-required | presentation tests |
| cl-ac-006 | S90/S99 | AC-006 | Docs and tests fix new contract. | provider docs, mirror docs, regression suite. | undocumented contract drift | yes | inspect-only + command | docs diff + final review |
| cl-ec-001 | S02/S03/S04 | EC-001 | Unknown high-level empty target blocks with unknown reason. | empty high-level target with no authoritative state. | fail-open unknown | yes | red-required | domain/CLI/sync tests |
| cl-ec-002 | S02/S04 | EC-002 | Done child-only dependency does not block but remains visible. | high-level target with all child issues done. | done blocker resurrection or invisible context | yes | red-required | domain/sync tests |
| cl-ec-003 | S01/S04/S99 | EC-003 | Raw node-level cycles fail before readiness projection and do not render stale authority. | raw graph cycle fixture. | cycle hidden by projection | yes | covered-existing + red-required if touched | existing cycle tests + disabled artifact test |
| cl-ec-004 | S90/S99 | EC-004 | Docs/labels keep `deps-raw` as visual/debug, not readiness authority. | provider docs and generated artifact wording. | authority confusion | yes | inspect-only | docs/spec review |

Test strategy by command:

- Fast domain loop: `uv run pytest tests/unit/domain/test_runtime_domain_s03.py tests/unit/domain/test_deps.py`
- Command guard loop: `uv run pytest tests/cli_runtime/test_deps.py tests/cli_runtime/test_issue_lifecycle.py tests/unit/application/test_check_deps.py tests/unit/application/test_set_active.py`
- Sync/presentation loop: `uv run pytest tests/cli_runtime/test_sync.py tests/unit/presentation/test_runtime_sync_s07.py tests/unit/presentation/test_deps_raw_puml.py`
- Final lane: `uv run pytest tests/unit tests/cli_runtime`; escalate to `uv run pytest` if implementation touches shared scaffold/update behavior beyond the planned files.

## 7. Review Gates

- Per-step gate: every S01-S04 and S90 step requires fresh reviewer pass before commit.
- Reviewer mapping:
  - Runtime/code/tests: `code-reviewer`.
  - Docs-only provider/mirror step: `spec-reviewer` docs/spec alignment.
  - Final test sufficiency: `qa-reviewer`.
  - Final integrated diff: issue-wide `code-reviewer`.
  - Final spec closure: `spec-reviewer`.
- Report evidence destination:
  - Step Contract Closure for behavior goal.
  - Test Contract Closure for each `cl-*`.
  - Closure Delta for aliases or changed closure names.
  - Delegated Worker Evidence for worker summaries.
  - Reviewer Gate Status for every review.
  - Step Commit Gate for commit/no-op evidence.

## 8. Rollback / Compatibility

- Storage rollback: no `.meta.json.depends_on` migration is planned, so reverting runtime/docs/tests restores prior behavior.
- Compatibility: keep `DepsEvaluation.blockers`, `blockers_top`, `closure`, `ready`, and `guard_reason`; add typed fields for consumers needing issue-vs-node distinction.
- JSON compatibility: `deps check --json` and `deps-issues.json` should use `schema_version: 2`; docs must state the v2 contract.
- Risk: existing consumers may assume `blockers` contains issue IDs only. Mitigation: typed `issue_blockers` and `node_blockers` fields plus docs.
- Rollback trigger: if node IDs in `blockers` break an approved consumer contract not covered by design, stop for design amendment rather than hiding node blockers in warnings.

## 9. Docs Impact

S90 resolves docs impact. Required docs changes:

- `src/spec_dock/assets/spec_dock/docs/reference_deps.md`: storage vs raw direct deps vs compiled issue deps; empty open/unknown high-level blocker semantics; satisfied dependency semantics; command guard parity.
- `src/spec_dock/assets/spec_dock/docs/reference_sync.md`: `deps-issues` v2 authority, `deps-raw` debug-only boundary, generated artifact fields/labels.
- Dogfooding mirror under `spec-dock/docs/`: refresh from provider or record intentional non-refresh.

Docs must explicitly say `deps-raw.puml` is not readiness authority even when it displays state color.

## 10. Final Quality Gate

Before main orchestrator can mark the implementation ready:

- All required `cl-*` rows have observed closure evidence in `report.md`.
- S01-S04 and S90 are individually reviewed and committed or recorded as approved no-op.
- `uv run pytest tests/unit tests/cli_runtime` passes, or any broader failure is classified with evidence and not caused by this issue.
- `qa-reviewer` passes test sufficiency.
- Issue-wide `code-reviewer` passes integrated diff.
- `spec-reviewer` passes requirement/design/plan/report/docs closure.
- Final diff guard confirms no legacy `app.py`, secrets, GitHub state, unrelated workflow/config, or unplanned canonical docs changes.

## 11. Plan Blockers

- None for drafting the canonical plan.
- Implementation must stop for plan amendment if any S01-S04 stop/amendment trigger occurs.
- Design gap candidate to watch: if high-level GitHub state is not available for initiative/epic through existing snapshots and cannot be inferred without new gateway behavior, S02/S03 must return to design rather than inventing a new authority source.

## 12. Integration Notes for Main Orchestrator

- Suggested adoption target: canonical `spec-dock/active/issue/plan.md`.
- Adoption should record this file in `report.md` Evidence Adoption Ledger and Delegated Draft Evidence with `created_by_role=implementation-planner`.
- A post-run diff guard should verify this draft is the only file changed by the delegated authoring run before adoption.
- Leaf evidence used: active context pack, fresh reviewer-passed requirement/design as stated by user, report gate/adoption context, research discussion, delegated design draft, plan authoring docs, and shallow runtime/test path inspection.
- Forbidden actions avoided in this draft: no canonical doc edit, no implementation/test/config edit, no GitHub mutation, no source-of-truth claim, no reviewer-pass claim, no implementation-readiness claim.
- Unresolved design gaps: none blocking plan adoption; high-level status source availability remains an implementation stop trigger if current runtime data cannot satisfy the approved design.

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
