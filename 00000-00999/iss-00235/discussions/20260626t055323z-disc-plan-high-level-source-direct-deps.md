---
種別: disc
ID: "20260626t055323z-disc"
タイトル: "Plan: High Level Source Direct Deps"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-26"
親: ["iss-00235"]
関連: []
authority: "proposed"
created_by_role: implementation-planner
scope_id: iss-00235
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/discussions/20260626t054055z-disc-design-high-level-source-direct-deps.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/workflow_issue.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/models.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py
  - tests/unit/application/test_check_deps.py
  - tests/unit/presentation/test_runtime_sync_s07.py
  - tests/cli_runtime/test_runtime_deps_s04.py
  - tests/unit/domain/test_deps.py
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pass
---

# 20260626t055323z-disc Plan: High Level Source Direct Deps

This is delegated implementation-plan draft evidence only. It is suitable for main-orchestrator integration into canonical `plan.md`, but it does not edit or replace canonical artifacts.

## 1. Plan Summary

Plan `iss-00235` as a five-step implementation sequence plus S90/S99 gates:

- S01: Add a public domain/application inspection contract for direct node-source dependencies.
- S02: Render `deps check --json` additive `direct_node_dependencies` and non-ready status for high-level source direct deps.
- S03: Render complete raw direct edge audit in `.agent/index-all.json` as `deps.raw_direct_edges`.
- S04: Add CLI/runtime reduced reproduction coverage using `--no-github`.
- S05: Regression hardening for existing issue-source high-level target semantics and non-expanded artifacts.
- S90: Resolve docs impact.
- S99: Run final QA/code/spec gate.

Execution invariant: one implementation step = one observable behavior = one review scope = one commit. Each implementation step should be delegated to `dev-coder`; docs-only S90 work, if needed, should be delegated to `doc-writer`.

## 2. Requirement / Design Traceability

Spec-Locked Closure Index:

| Closure id | Spec link | Locked expectation | Observable input/state | Bug class guarded | Required | Evidence level | Owner step |
|---|---|---|---|---|---|---|---|
| `cl-ac001-direct-check` | AC-001, design `deps check --json` | `deps check --id <initiative|epic> --json` exposes source node direct dependencies in `direct_node_dependencies` with source/target ids and kinds. | Empty high-level source `init-00001` has `.meta.json.depends_on=["epic-00002"]`. | Raw edge is silently dropped by issue projection. | yes | application + presentation + CLI JSON | S01, S02, S04 |
| `cl-ac002-non-ready` | AC-002, design readiness contract | Unresolved direct node dependency yields machine-readable non-ready status; top-level `ready` is false and `blockers` includes unresolved target node id. | Same graph as AC-001, target epic unresolved open/unknown. | False-ready for unresolved high-level source dependency. | yes | domain/application + CLI JSON | S01, S02, S04 |
| `cl-ac003-index-all-raw` | AC-003, design `.agent/index-all.json` | `.agent/index-all.json` includes complete `deps.raw_direct_edges` with source/target kinds and `relation: raw_direct`. | Sync state has raw `init -> epic`, `epic -> epic`, or `issue -> epic` edges. | Raw audit unavailable from full-history machine artifact. | yes | sync/presentation artifact | S03 |
| `cl-ac004-issue-regression` | AC-004, EC-004 | Existing issue-source to high-level target blockers, satisfied deps, and `effective_depends_on` semantics remain unchanged. | Existing issue-source high-level target tests. | Fixing source projection by breaking `iss-00207` behavior. | yes | existing domain/application/CLI regressions | S05 |
| `cl-ec001-empty-source` | EC-001 | Empty high-level source direct dependency is inspectable and cannot return dependency-free ready output. | Initiative/epic source has no descendant issues. | Empty source compiles to no issue contexts. | yes | CLI/runtime no-github reproduction | S04 |
| `cl-ec002-non-empty-source` | EC-002 | Non-empty high-level source keeps direct node status separate from descendant issue readiness projection. | Source has descendant issues plus parent raw direct dependency. | Double-counting or mixing direct source status into issue projection. | yes | application/domain characterization | S01, S05 |
| `cl-ec003-satisfied-raw-audit` | EC-003 | Satisfied/done/closed dependency remains in complete raw audit even when not a blocker. | Raw edge target is closed/done/satisfied. | Complete audit filtered like readiness. | yes | sync/index artifact test | S03 |
| `cl-design-boundary` | design adopted/non-adopted choices | No synthetic issue, no `.meta.json.depends_on` format change, no `deps-issues.json` complete raw graph dump, no `deps-raw.puml` contract expansion. | Diff and existing artifact tests. | Scope creep and contract ambiguity. | yes | regression + code review | S05, S99 |

Requirement/design mapping:

- AC-001 and AC-002 close through S01/S02/S04.
- AC-003 closes through S03.
- AC-004 and EC-004 close through S05.
- EC-001 closes through S04, with S01/S02 as prerequisites.
- EC-002 closes through S01 and S05.
- EC-003 closes through S03.

## 3. Milestones

- M1 Direct readiness contract: S01 and S02 establish the public `deps check` behavior.
- M2 Raw audit artifact: S03 exposes complete raw edge data in full-history sync output.
- M3 Runtime reproduction and regression lock: S04 and S05 prove the fix from CLI/runtime and protect adjacent contracts.
- M4 Completion gates: S90 and S99 close docs, QA, code review, and spec alignment.

## 4. Dependency-Derived Execution Order

Design dependency graph: `infra.deps_reader -> domain.deps -> application.check_deps/sync_state -> presentation.json_state`.

Execution order rationale:

1. S01 starts at domain/application because `deps check` and sync output need a shared status/audit vocabulary before rendering.
2. S02 depends on S01 because JSON rendering should expose stable result data rather than recompute status in presentation.
3. S03 can follow S01 because raw edge kind information and sync state payload shape must be stable before presentation renders `index-all`.
4. S04 follows S02/S03 because CLI/runtime tests should observe the externally visible command/artifact behavior.
5. S05 follows all implementation steps because it is a regression and boundary hardening pass over the integrated diff.

Do not begin a later implementation step until the previous step has Step Result Approval: delegated implementation completed, targeted verification passed, step reviewer passed, step commit made, and post-commit clean check recorded.

## 5. Issue / Step Slicing

### S01 Direct Node Dependency Status Contract

Behavior goal: `check_deps` can evaluate direct dependencies where the checked target itself is an initiative/epic source, without relying on issue-source contexts.

Target files:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/models.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py`
- `tests/unit/domain/test_deps.py`
- `tests/unit/application/test_check_deps.py`

Forbidden changes:

- Do not modify `.meta.json.depends_on` storage format.
- Do not create synthetic/fake issues.
- Do not change `effective_depends_on` to include direct high-level source deps.
- Do not update presentation JSON or sync artifacts in this step except as needed for dataclass compatibility.

Delegation contract:

- delegated role: `dev-coder`.
- input docs: requirement/design/plan, design discussion, listed source/test files.
- allowed paths: target files above only.
- acceptance criteria: closes `cl-ac001-direct-check`, `cl-ac002-non-ready`, and part of `cl-ec002-non-empty-source` at domain/application level.
- required verification: `uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py`.
- reviewer focus: `code-reviewer` checks whether status rules are centralized enough, public result contracts are additive, and existing issue readiness paths remain stable.
- stop conditions: needing storage migration, needing private-only tests, needing source/test files outside allowed paths, or discovering design contradiction.
- output required: changed files, red/green evidence, result shape summary, unresolved risks, and `No material implementation decisions beyond the approved plan.` or a Ledger Note.

Concrete test cases:

- `tc-s01-001` red-required: empty initiative source direct dependency blocks
  - 前提: graph has `init-00001 -> epic-00002` in raw node dependency map and no descendant issue under the source.
  - 操作: call application `check_deps` for `init-00001` with `use_github=False` and cached/local open target state.
  - 期待結果: result is not ready; blockers include `epic-00002`; direct dependency status contains source/target ids and kinds.
  - 失敗検出: raw dependency remains only in `raw_node_depends_on_map` and readiness returns dependency-free ready.
  - 検証方法: add focused application/domain tests in `tests/unit/application/test_check_deps.py` and/or `tests/unit/domain/test_deps.py`.
  - 関連 closure id: `cl-ac001-direct-check`, `cl-ac002-non-ready`, `cl-ec001-empty-source`

- `tc-s01-002` characterization: non-empty source keeps projections separate
  - 前提: high-level source has descendant issues and also has a direct raw dependency on another high-level node.
  - 操作: inspect the high-level source and compare direct dependency status with existing descendant issue readiness fields.
  - 期待結果: direct status is present; `effective_depends_on` remains issue-readiness-only.
  - 失敗検出: direct source dependency is merged into `effective_depends_on` or descendant issue blockers are double-counted.
  - 検証方法: application/domain characterization test.
  - 関連 closure id: `cl-ec002-non-empty-source`, `cl-design-boundary`

Step closure contract:

- Direct node dependency status is available from the application result and can be rendered later without recomputation.
- Direct dependency disposition uses existing lifecycle/disposition vocabulary.
- Existing domain tests for issue-source high-level target dependencies still pass.

Amendment trigger:

- If direct node status cannot be represented additively in existing result models, or if `effective_depends_on` must change meaning, stop for plan/design amendment.

### S02 `deps check --json` Additive JSON Contract

Behavior goal: `render_deps_check_json()` emits `direct_node_dependencies`, and unresolved/indeterminate direct node dependencies are visible through top-level `ready` and `blockers`.

Target files:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
- `tests/unit/presentation/test_runtime_sync_s07.py`
- `tests/cli_runtime/test_runtime_deps_s04.py` if a public renderer/CLI fixture is cheaper here than in S04.

Forbidden changes:

- Do not remove or rename existing JSON fields.
- Do not change `schema_version` unless a compatibility reason is recorded and reviewed.
- Do not overload `dependency_contexts` with source-node-only dependencies.

Delegation contract:

- delegated role: `dev-coder`.
- input docs: S01 result, design JSON contract, existing renderer tests.
- allowed paths: target files above only.
- acceptance criteria: closes presentation side of `cl-ac001-direct-check` and `cl-ac002-non-ready`.
- required verification: `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py`.
- reviewer focus: `code-reviewer` checks additive JSON compatibility, field naming, null/empty stability, and no presentation-layer readiness recomputation.
- stop conditions: renderer needs to infer statuses unavailable in result, or JSON contract conflicts with design examples.
- output required: JSON field sample, test command/result, changed files, risks, ledger note/no-decision statement.

Concrete test cases:

- `tc-s02-001` red-required: renderer emits direct node dependency payload
  - 前提: construct `DepsCheckResult` whose inspection has one blocking direct node dependency.
  - 操作: call `render_deps_check_json(result)`.
  - 期待結果: payload contains `direct_node_dependencies[0]` with source/target ids, source/target kinds, expansion, lifecycle, disposition, and basis.
  - 失敗検出: output has `ready=false` but no structural direct dependency payload.
  - 検証方法: focused presentation test near existing `render_deps_check_json` coverage.
  - 関連 closure id: `cl-ac001-direct-check`

- `tc-s02-002` compatibility: existing keys remain present
  - 前提: existing deps check result with node blockers/dependency contexts.
  - 操作: render JSON and inspect top-level keys.
  - 期待結果: existing keys remain present and `direct_node_dependencies` is additive.
  - 失敗検出: existing `node_blockers`, `satisfied_dependencies`, or `dependency_contexts` contracts regress.
  - 検証方法: update existing renderer contract test.
  - 関連 closure id: `cl-ac004-issue-regression`, `cl-design-boundary`

Step closure contract:

- JSON output can be consumed by simple clients through `ready`/`blockers` and by structured clients through `direct_node_dependencies`.
- Empty direct dependency list is rendered consistently.

Amendment trigger:

- If blockers cannot safely contain high-level node ids without breaking an existing documented contract, stop for design/plan amendment.

### S03 `.agent/index-all.json` Raw Direct Edge Audit

Behavior goal: full-history sync artifact exposes complete raw direct node edges under `deps.raw_direct_edges`.

Target files:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py` only if the existing `raw_node_depends_on_map` is insufficient.
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` only if a typed edge list is needed.
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
- `tests/unit/presentation/test_runtime_sync_s07.py`
- `tests/cli_runtime/test_runtime_deps_s04.py`

Forbidden changes:

- Do not make `deps-issues.json` a complete raw graph dump.
- Do not promote `deps-raw.puml` to complete audit artifact.
- Do not filter `raw_direct_edges` by readiness/satisfied state.
- Do not add raw audit to `.agent/index.json` unless main orchestrator amends design.

Delegation contract:

- delegated role: `dev-coder`.
- input docs: AC-003, design `.agent/index-all.json` contract, existing sync artifact tests.
- allowed paths: target files above only.
- acceptance criteria: closes `cl-ac003-index-all-raw` and `cl-ec003-satisfied-raw-audit`.
- required verification: `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py`.
- reviewer focus: `code-reviewer` checks complete raw audit semantics, deterministic sorting, source/target kind correctness, and no expansion of `deps-issues.json` / `deps-raw.puml`.
- stop conditions: raw source/target kind cannot be resolved from graph, or existing sync payload cannot carry complete raw data without schema conflict.
- output required: artifact JSON sample, command/result, changed files, risks, ledger note/no-decision statement.

Concrete test cases:

- `tc-s03-001` red-required: `index-all` includes high-level raw direct edge
  - 前提: sync state has `raw_node_depends_on_map={"init-00001": ["epic-00002"]}`.
  - 操作: render or write sync artifacts and load `.agent/index-all.json`.
  - 期待結果: `deps.raw_direct_edges` contains `{from, from_kind, to, to_kind, relation}` for `init-00001 -> epic-00002`.
  - 失敗検出: edge appears only in visual artifact or is absent from `index-all`.
  - 検証方法: focused sync/presentation artifact test.
  - 関連 closure id: `cl-ac003-index-all-raw`

- `tc-s03-002` red-required: satisfied raw dependency remains in audit
  - 前提: raw source edge target is closed/done/satisfied.
  - 操作: render `.agent/index-all.json`.
  - 期待結果: `deps.raw_direct_edges` still includes the raw edge while readiness blockers may be empty.
  - 失敗検出: raw audit is filtered using active blocker rules.
  - 検証方法: sync artifact test using cached/local status.
  - 関連 closure id: `cl-ec003-satisfied-raw-audit`

Step closure contract:

- `deps.raw_direct_edges` is deterministic, complete for resolved raw edges, and includes node kinds.
- `deps.issue_edges` remains issue readiness projection.

Amendment trigger:

- If `.agent/index-all.json` consumers require schema versioning or cannot tolerate the additive field, stop for compatibility amendment.

### S04 CLI Runtime Reduced Reproduction

Behavior goal: a `--no-github` runtime scenario reproduces #235 and proves the public CLI/artifact behavior end to end.

Target files:

- `tests/cli_runtime/test_runtime_deps_s04.py`
- `tests/cli_runtime/test_deps.py` only if the existing CLI harness there is the better public-command surface.

Forbidden changes:

- Do not require live GitHub state.
- Do not mutate external product repos.
- Do not assert private helper behavior as the primary evidence.

Delegation contract:

- delegated role: `dev-coder`.
- input docs: AC-001 through AC-003, S01-S03 implementation, CLI test harnesses.
- allowed paths: target test files only unless a small runtime bug is discovered and amended back to the owning step.
- acceptance criteria: closes CLI side of `cl-ac001-direct-check`, `cl-ac002-non-ready`, and `cl-ec001-empty-source`.
- required verification: `uv run pytest tests/cli_runtime/test_runtime_deps_s04.py`; if `test_deps.py` is touched, also run `uv run pytest tests/cli_runtime/test_deps.py`.
- reviewer focus: `code-reviewer` checks that the test observes command JSON/artifact output and is hermetic.
- stop conditions: needing network/GitHub, needing broad fixture rewrites, or discovering behavior outside approved design.
- output required: failing-first evidence or characterization rationale, command/result, changed files, risks, ledger note/no-decision statement.

Concrete test cases:

- `tc-s04-001` red-required: `deps check --id init --no-github --json` is non-ready for raw high-level source dep
  - 前提: temp repo contains source initiative with direct dependency on target epic and no descendant source issues.
  - 操作: run runtime `deps check --id init-local-... --no-github --json`.
  - 期待結果: JSON has `ready=false`, `blockers` containing target epic id, and `direct_node_dependencies` containing source/target ids and kinds.
  - 失敗検出: command returns dependency-free `ready=true`.
  - 検証方法: CLI runtime test.
  - 関連 closure id: `cl-ac001-direct-check`, `cl-ac002-non-ready`, `cl-ec001-empty-source`

- `tc-s04-002` red-required: `sync --no-github` writes raw audit to index-all
  - 前提: same temp repo graph as `tc-s04-001`.
  - 操作: run runtime sync or collect/write artifacts, then load `.agent/index-all.json`.
  - 期待結果: `deps.raw_direct_edges` includes the source/target raw edge with kinds.
  - 失敗検出: sync succeeds but full-history machine artifact has no raw direct edge.
  - 検証方法: CLI runtime artifact test.
  - 関連 closure id: `cl-ac003-index-all-raw`

Step closure contract:

- Public command behavior proves the issue without GitHub.
- The test would fail on the current false-ready behavior.

Amendment trigger:

- If the runtime harness cannot represent high-level `.meta.json.depends_on` without adding unrelated scaffold behavior, stop and split fixture support into a plan amendment.

### S05 Regression / Boundary Hardening

Behavior goal: protect existing issue-source high-level target semantics and explicitly guard non-goals.

Target files:

- `tests/unit/domain/test_deps.py`
- `tests/unit/application/test_check_deps.py`
- `tests/unit/presentation/test_runtime_sync_s07.py`
- `tests/unit/presentation/test_deps_raw_puml.py` only if an existing regression needs pinning.
- `tests/cli_runtime/test_runtime_deps_s04.py`

Forbidden changes:

- Do not change implementation except for defects found in S05 review/test failures.
- Do not expand `deps-raw.puml` or `deps-issues.json` contracts.
- Do not add broad snapshot churn.

Delegation contract:

- delegated role: `dev-coder`.
- input docs: requirement EC-004, design non-adopted choices, existing tests named above.
- allowed paths: target tests and minimal implementation files only if fixing S05-detected regression within approved scope.
- acceptance criteria: closes `cl-ac004-issue-regression` and `cl-design-boundary`.
- required verification: `uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py`.
- reviewer focus: `code-reviewer` checks regression coverage, no private-method-only tests, and no non-goal contract expansion.
- stop conditions: failing existing behavior requires changing accepted design, or test update becomes broad snapshot replacement.
- output required: regression matrix, command/result, changed files, risks, ledger note/no-decision statement.

Concrete test cases:

- `tc-s05-001` covered-existing: issue-source high-level target remains blocked/satisfied as before
  - 前提: existing issue source depends on empty/open, closed, done, and descendant aggregate high-level targets.
  - 操作: run existing domain/application tests.
  - 期待結果: node blockers, satisfied dependencies, and `effective_depends_on` remain consistent.
  - 失敗検出: direct source fix changes issue-source target behavior.
  - 検証方法: existing plus narrowly updated tests in `tests/unit/domain/test_deps.py` and `tests/unit/application/test_check_deps.py`.
  - 関連 closure id: `cl-ac004-issue-regression`

- `tc-s05-002` characterization: non-goal artifacts do not become complete raw audit
  - 前提: raw edge is satisfied/done/closed.
  - 操作: inspect `deps-issues.json` / `deps-raw.puml` behavior through existing tests.
  - 期待結果: complete audit is in `index-all`; non-goal artifacts keep existing projection semantics.
  - 失敗検出: implementation broadens unrelated artifacts to satisfy AC-003.
  - 検証方法: existing `deps_raw_puml` and sync presentation tests, with narrow assertions only if needed.
  - 関連 closure id: `cl-design-boundary`

Step closure contract:

- All required closure ids are covered by at least one public/observable test or justified characterization.
- No forbidden artifact/source expansion is present in the diff.

Amendment trigger:

- If regression protection reveals a real conflict between AC-003 complete audit and existing visual projections, stop for design amendment rather than silently changing non-goal artifacts.

## 6. Test Strategy Mapping

- Red-first obligations: S01 direct status at application/domain, S02 JSON field, S03 `index-all` raw audit, S04 runtime reproduction.
- Characterization obligations: S01 non-empty source separation, S05 issue-source high-level target behavior and non-goal artifact boundaries.
- Public/observable priority: CLI JSON, sync artifact JSON, renderer output, and application result objects are acceptable; private helper-only tests are not sufficient.
- Hermetic requirement: all new regression tests use `--no-github`, cached state, temp repos, or stubs.
- Narrow commands:
  - `uv run pytest tests/unit/domain/test_deps.py`
  - `uv run pytest tests/unit/application/test_check_deps.py`
  - `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py`
  - `uv run pytest tests/cli_runtime/test_runtime_deps_s04.py`
- Final broader command candidate after S05: `uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py`.

## 7. Review Gates

- Each implementation step requires delegated worker evidence, targeted verification, per-step `code-reviewer` pass, report evidence, and a step commit before the next step starts.
- S90 docs-only updates, if any, require `doc-writer` and `spec-reviewer` docs/spec alignment.
- S99 requires all three final gates: `qa-reviewer` for test sufficiency, issue-wide `code-reviewer` for integrated diff, and `spec-reviewer` for requirement/design/plan/report alignment.
- Reviewer fail must return to bounded delegated follow-up; final QA/code/spec gates do not replace per-step review.

## 8. Rollback / Compatibility

- Rollback is data-safe because storage remains `.meta.json.depends_on` and no migration is introduced.
- JSON changes are additive: `direct_node_dependencies` in `deps check --json` and `deps.raw_direct_edges` in `.agent/index-all.json`.
- Compatibility risk: consumers that assume `blockers` are issue ids only may need review. Mitigation: keep detailed node data in additive fields and document high-level node ids as non-ready blockers for direct node dependencies.
- Rollback path: remove additive fields and direct source readiness path, leaving existing issue readiness and raw storage intact.
- Do not use rollback to delete raw metadata; this issue fixes projection/inspection only.

## 9. Docs Impact

S90 docs impact resolution:

- Inspect whether `spec-dock/docs/reference_deps.md`, `spec-dock/docs/reference_sync.md`, CLI help docs, or generated context guidance describe `deps check --json`, `index-all`, `deps-issues.json`, or `deps-raw.puml` contract.
- If docs mention these contracts, delegate focused updates to `doc-writer`, limited to shipped docs/templates under provider source of truth.
- If no docs update is needed, record why in `report.md` and obtain `spec-reviewer` docs/spec alignment.
- Verification command if docs change: targeted docs/source tests selected by changed surface, plus `uv run pytest tests/unit/infra/test_init_update.py` only if shipped scaffold snapshots/contracts are affected.

## 10. Final Quality Gate

S99 final quality gate:

- `qa-reviewer`: verify risk-calibrated coverage across AC-001..AC-004 and EC-001..EC-004; decide whether broader `uv run pytest tests/cli_runtime/test_deps.py tests/cli_runtime/test_sync.py` is required.
- issue-wide `code-reviewer`: review integrated diff for layering, additive compatibility, deterministic sorting, and forbidden changes.
- `spec-reviewer`: verify requirement/design/plan/report/test/docs alignment and closure index completion.
- Final command candidate before final report/commit: `uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py`.
- Final exit requires all required closure ids closed in report evidence, all implementation steps committed or approved-no-op, S90 resolved, S99 reviewers passed, final report ledger updated, and final commit created by the main orchestrator workflow.

## 11. Plan Blockers

No blocking requirement/design gaps found.

Non-blocking watch items for main orchestrator:

- Confirm whether `blockers` containing high-level node ids needs a short compatibility note in canonical design/plan.
- Confirm whether S03 should render `raw_direct_edges` only in `.agent/index-all.json` or also tree-all; this draft follows the approved requirement and limits it to `index-all`.
- Existing worktree is already dirty outside this delegated draft scope; main orchestrator should run a post-run diff guard before adoption.

## 12. Integration Notes for Main Orchestrator

- Changed discussion artifact path: `spec-dock/active/issue/discussions/20260626t055323z-disc-plan-high-level-source-direct-deps.md`.
- Source requirement/design revisions used: `iss-00235 requirement.md` and `iss-00235 design.md`, both `最終更新: "2026-06-26"`, plus design discussion `20260626t054055z-disc-design-high-level-source-direct-deps.md`.
- Lightweight provenance summary: active context, approved requirement/design, plan authoring docs, workflow policy, runtime source inspection, and focused existing test inspection.
- Leaf evidence used: none beyond local source/docs/tests and the existing system-architect design discussion.
- Forbidden actions avoided: no canonical `requirement.md` / `design.md` / `plan.md` / `report.md` edits, no source edits, no test edits, no GitHub mutation, no phase promotion, no reviewer-pass claim.
- Unresolved design gaps: none.

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
