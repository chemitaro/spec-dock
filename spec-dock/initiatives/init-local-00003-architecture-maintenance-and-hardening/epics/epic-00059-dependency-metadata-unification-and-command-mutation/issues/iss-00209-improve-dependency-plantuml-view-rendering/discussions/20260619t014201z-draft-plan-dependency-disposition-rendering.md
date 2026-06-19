---
created_by_role: implementation-planner
scope_id: iss-00209
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/active/issue/discussions/20260619t002902z-research-dependency-plantuml-rendering-clarification.md
  - spec-dock/active/issue/discussions/20260619t002903z-interview-dependency-plantuml-closed-node-policy.md
  - spec-dock/active/issue/discussions/20260619t010926z-interview-dependency-disposition-scope-amendment.md
  - spec-dock/active/issue/discussions/20260619t013310z-draft-design-dependency-disposition-plantuml-rendering.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/models.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/puml.py
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# Draft Plan: Dependency Disposition Rendering Implementation

This is delegated draft planning evidence for `iss-00209`. It is not canonical `plan.md`, does not claim adoption, and requires main-orchestrator review plus a fresh `spec-reviewer` pass before reflection.

## 1. Plan Summary

- Goal: implement the accepted Option A scope as one coherent readiness + rendering change.
- Core order: domain contract -> application consumers -> presentation JSON/PUML -> docs/manual verification -> final QA/code/spec gates.
- Commit rule: each implementation step is one review scope and one commit boundary. Do not mix S01/S02/S03/S04/S90 changes in one commit.
- Primary success criteria:
  - `deps check`, `active set`, `issue start`, `sync`, `.agent/deps-issues.json`, `deps-issues.puml`, and `deps-raw.puml` all consume the same dependency readiness interpretation.
  - GitHub-open all-descendant-done high-level dependency is `dependency_disposition=satisfied`.
  - Empty open high-level dependency remains `dependency_disposition=blocking`.
  - Lifecycle facts remain visible separately as `lifecycle_state` / `lifecycle_source`.

Source revisions read for this draft:

- Worktree HEAD: `bdc511fa`.
- `requirement.md` sha256: `a9713d841008dd1d81a4788c5c3dc7be2dd29cda05566589b216fb6b0c37e395`.
- `design.md` sha256: `9013edbe7a99dce2da797f79fbaf95ac672952d5ad1fdee6c13a67133c9561e3`.
- Existing `requirement.md`, `design.md`, and discussion files were already dirty/untracked before this draft; this draft does not edit them.

## 2. Requirement / Design Traceability

- AC-001 -> S01, S02, S03, S04: empty open high-level dependency blocks and renders as active blocker.
- AC-002 -> S01, S02, S03, S04: GitHub-open all-descendant-done high-level dependency is satisfied and not rendered as active blocker/noise.
- AC-003 -> S01, S03: machine consumers see lifecycle fact and dependency disposition separately.
- AC-004 -> S04: `deps-issues.puml` is actionable readiness view with `blocks` labels and no satisfied-only active graph content.
- AC-005 -> S04: `deps-raw.puml` keeps active raw direct edges and package high-level representation while filtering resolved-only noise.
- AC-006 -> S01-S04, S90: `.meta.json.depends_on` and `deps add/remove` mutation contract remain unchanged.
- EC-001 -> S01, S02: full graph descendant traversal, not todo projection.
- EC-002 -> S01, S02: unknown descendant state is fail-closed / indeterminate.
- EC-003 -> S01, S02: closed high-level empty node is satisfied.
- EC-004 -> S03, S04, S90: raw view is not readiness authority.

## 3. Milestones

- M1 Domain readiness contract:
  - Close S01 with explicit disposition fields and domain tests.
- M2 Application readiness consumers:
  - Close S02 so `deps check`, `active set`, `issue start`, and `sync` use the domain result without duplicate blocker rules.
- M3 Machine and visual output:
  - Close S03 and S04 so JSON and PlantUML surfaces match readiness authority.
- M4 Docs/manual/final gates:
  - Close S90 and S99 with docs impact, realistic manual evidence, `sync`, `validate`, final QA, issue-wide code review, and final spec review.

## 4. Dependency-Derived Execution Order

Design dependency chain:

1. `domain/models.py` defines the data contract.
2. `domain/deps.py` classifies dependency disposition from raw context, lifecycle facts, and full graph descendant status.
3. `application/check_deps.py`, `application/set_active.py`, and `application/sync_state.py` assemble full graph/status inputs and consume `DepsEvaluation`.
4. `presentation/json_state.py` serializes evaluated fields and active graph payload.
5. `presentation/puml.py` renders active readiness/raw views without re-inferring readiness.
6. Provider docs and dogfooding docs explain the contract after the runtime behavior is fixed.

Do not start downstream implementation until the previous step has Step Result Approval: required verification passed, step reviewer passed, report evidence is recorded, step commit is made, and post-commit status is clean except expected next-step changes.

## 5. Issue / Step Slicing

### S01 Domain Disposition Contract

- Behavior goal: `evaluate_readiness()` returns explicit lifecycle/disposition/basis context for high-level dependencies and keeps node blockers limited to actual blocker surfaces.
- Depends on: approved requirement/design.
- Unblocks: S02/S03/S04.
- Allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/models.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`
  - `tests/unit/domain/test_deps.py`
- Forbidden changes:
  - `.meta.json.depends_on` storage format.
  - infra topology reader mutation behavior.
  - application command output or presentation rendering.
- Closure IDs: `cl-001`, `cl-002`, `cl-003`, `cl-004`.
- Review gate: `code-reviewer` before commit.
- Commit boundary: commit only S01 domain/model/test changes.

Delegation contract:

- Delegated role: `dev-coder`.
- Input docs: `requirement.md`, `design.md`, this draft after adoption, `workflow_issue.md`, current target files.
- Required output: changed files, red/green evidence, unresolved risks, and `No material implementation decisions beyond the approved plan.` or a structured Ledger Note.
- Stop conditions: disposition table cannot fit current models without changing storage/reader contracts; application-layer changes become necessary to make domain tests pass; unknown handling conflicts with requirement.

Concrete test cases:

- `tc-s01-001` red-required: empty open high-level dependency exposes blocking disposition.
  - 前提: target issue depends on an empty GitHub-open epic context.
  - 操作: `evaluate_readiness()` with `DepsHighLevelStatus(state="open", source="github")`.
  - 期待結果: not ready; node blocker has `dependency_disposition=blocking`, `disposition_basis=empty_open_container`, `lifecycle_state=open`, `lifecycle_source=github`.
  - 失敗検出: old `reason=empty_open` only contract passes without explicit disposition fields.
  - 検証方法: `uv run pytest tests/unit/domain/test_deps.py -k high_level_dependency`.
  - 関連 closure id: `cl-001`.

- `tc-s01-002` red-required: GitHub-open all-descendant-done high-level dependency is satisfied.
  - 前提: target issue depends on an expanded epic context whose descendant issue IDs are all `done`; high-level lifecycle is GitHub `open`.
  - 操作: `evaluate_readiness()`.
  - 期待結果: ready; no node blocker; evaluated context has `dependency_disposition=satisfied`, `disposition_basis=all_descendant_issues_done`, `lifecycle_state=open`.
  - 失敗検出: GitHub `open` lifecycle is conflated with blocker state.
  - 検証方法: `uv run pytest tests/unit/domain/test_deps.py -k all_done`.
  - 関連 closure id: `cl-002`.

- `tc-s01-003` red-required: unknown descendant status fails closed.
  - 前提: expanded epic context has at least one descendant issue with unknown/missing status.
  - 操作: `evaluate_readiness()`.
  - 期待結果: not ready; `dependency_disposition=indeterminate`, `disposition_basis=descendant_issue_unknown`, `guard_reason=unknown`.
  - 失敗検出: unknown descendant is silently treated as satisfied or plain blocked without basis.
  - 検証方法: `uv run pytest tests/unit/domain/test_deps.py -k unknown`.
  - 関連 closure id: `cl-003`.

- `tc-s01-004` covered-existing: existing storage/mutation behavior is untouched by domain change.
  - 前提: existing raw dependency validation tests cover self/ancestor/descendant/cycle rejection.
  - 操作: run the focused domain dependency suite.
  - 期待結果: existing raw validation tests still pass without `.meta.json.depends_on` schema changes.
  - 失敗検出: disposition implementation leaks into raw storage validation.
  - 検証方法: `uv run pytest tests/unit/domain/test_deps.py`.
  - 関連 closure id: `cl-004`.

Step closure contract:

- S01 closes when `cl-001` through `cl-004` are recorded in report Step Contract Closure, Test Contract Closure, and Closure Coverage.
- Amendment trigger: implementation requires a new persisted field, a new artifact, or a change to `deps add/remove`.

### S02 Application Readiness Consumers

- Behavior goal: `deps check`, `active set`, `issue start`, and `sync` all consume the evaluated disposition and full graph descendant status.
- Depends on: S01.
- Unblocks: S03/S04.
- Allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - `tests/unit/application/test_check_deps.py`
  - `tests/unit/application/test_set_active.py`
  - `tests/cli_runtime/test_deps.py`
  - `tests/cli_runtime/test_issue_lifecycle.py`
- Forbidden changes:
  - presentation rendering changes.
  - docs changes.
  - GitHub lifecycle close/reopen policy.
  - bypassing readiness with `--force`; `issue start -f` must not bypass dependencies.
- Closure IDs: `cl-005`, `cl-006`, `cl-007`, `cl-008`.
- Review gate: `code-reviewer` before commit.
- Commit boundary: commit only S02 application/test changes.

Delegation contract:

- Delegated role: `dev-coder`.
- Required tests: focused application tests first, then CLI runtime tests for `deps check`, `active set`, and `issue start`.
- Stop conditions: command behavior needs new user-facing policy not present in requirement/design; GitHub stub behavior cannot distinguish lifecycle from disposition; changing CLI syntax appears necessary.

Concrete test cases:

- `tc-s02-001` red-required: `deps check --json` reports all-done open high-level dependency as ready.
  - 前提: target issue depends on GitHub-open epic with descendant issues all closed/done in the full graph.
  - 操作: `deps check --json` with stubbed GitHub/cache status.
  - 期待結果: exit 0; `ready=true`; no node blocker; satisfied context includes lifecycle/disposition/basis fields.
  - 失敗検出: command remains blocked because lifecycle `open` masks descendant satisfaction.
  - 検証方法: `uv run pytest tests/unit/application/test_check_deps.py -k all_done` and `uv run pytest tests/cli_runtime/test_deps.py -k high_level`.
  - 関連 closure id: `cl-005`.

- `tc-s02-002` red-required: empty open high-level dependency blocks `active set` and `issue start`.
  - 前提: target issue depends on empty GitHub-open epic or initiative.
  - 操作: `active set <target>` and `issue start <target>` without dependency force.
  - 期待結果: rejection includes node blocker disposition/basis in available JSON/evidence; `issue start -f` does not bypass dependency readiness.
  - 失敗検出: active selection starts despite empty open high-level blocker.
  - 検証方法: `uv run pytest tests/unit/application/test_set_active.py -k empty_open` and `uv run pytest tests/cli_runtime/test_issue_lifecycle.py -k dependency`.
  - 関連 closure id: `cl-006`.

- `tc-s02-003` red-required: full graph descendant count prevents todo projection false-empty.
  - 前提: high-level dependency has only done descendant issues, so done children are absent from todo projection.
  - 操作: `deps check --json` and `sync --no-github`.
  - 期待結果: target is satisfied, not classified as `empty_open_container`.
  - 失敗検出: implementation counts only todo issue projection and misclassifies the container as empty.
  - 検証方法: `uv run pytest tests/unit/application/test_check_deps.py -k descendant_aggregate`.
  - 関連 closure id: `cl-007`.

- `tc-s02-004` covered-existing: mutation contracts still pass.
  - 前提: existing `deps add/remove/check` CLI regression tests.
  - 操作: run focused dependency CLI tests.
  - 期待結果: no storage migration, no syntax change, no regression in raw validation.
  - 失敗検出: readiness work accidentally changes mutation command behavior.
  - 検証方法: `uv run pytest tests/cli_runtime/test_deps.py`.
  - 関連 closure id: `cl-008`.

Step closure contract:

- S02 closes when application/CLI tests show parity across `deps check`, `active set`, `issue start`, and `sync` inputs.
- Amendment trigger: readiness requires a new command flag, changes force semantics, or cannot preserve no-storage-migration.

### S03 Presentation JSON Contract

- Behavior goal: machine-readable outputs preserve lifecycle fact and dependency disposition separately while keeping schema v2 compatible.
- Depends on: S01 and S02.
- Unblocks: S04.
- Allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - `tests/unit/presentation/test_runtime_sync_s07.py`
  - `tests/cli_runtime/test_sync.py`
  - `tests/cli_runtime/test_deps.py`
- Forbidden changes:
  - PUML renderer changes.
  - schema version bump unless canonical plan explicitly allows it.
  - removing existing top-level JSON keys in the first pass.
- Closure IDs: `cl-009`, `cl-010`, `cl-011`.
- Review gate: `code-reviewer` before commit.
- Commit boundary: commit only S03 JSON/test changes.

Delegation contract:

- Delegated role: `dev-coder`.
- Required output: JSON before/after summary for `deps check --json` and `.agent/deps-issues.json`.
- Stop conditions: additive schema cannot represent `dependency_contexts`; existing consumer contract would require key removal; field names diverge from requirement/design.

Concrete test cases:

- `tc-s03-001` red-required: `deps check --json` includes lifecycle/disposition fields.
  - 前提: empty open and all-done-open high-level dependency scenarios.
  - 操作: render JSON through `render_deps_check_json()`.
  - 期待結果: `node_blockers` and `satisfied_dependencies` include `lifecycle_state`, `lifecycle_source`, `dependency_disposition`, and `disposition_basis`.
  - 失敗検出: machine consumers still only see `state`, `state_source`, or raw context fields.
  - 検証方法: `uv run pytest tests/cli_runtime/test_deps.py -k json`.
  - 関連 closure id: `cl-009`.

- `tc-s03-002` red-required: `.agent/deps-issues.json` separates active graph nodes/edges from `dependency_contexts`.
  - 前提: graph contains done issues, closed high-level nodes, empty open blockers, and all-descendant-done open high-level dependencies.
  - 操作: `sync` and read `.agent/deps-issues.json`.
  - 期待結果: active `nodes`/`edges` contain blockers/actionable graph participants; `dependency_contexts` retains satisfied-but-not-rendered high-level context.
  - 失敗検出: satisfied-only context is lost entirely or remains as active graph edge.
  - 検証方法: `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py -k deps_issues`.
  - 関連 closure id: `cl-010`.

- `tc-s03-003` covered-existing: schema v2 compatibility.
  - 前提: existing sync and deps JSON tests expect `projection`, `source`, `deps`, `nodes`, `edges`, and `edge_direction`.
  - 操作: run sync presentation tests.
  - 期待結果: existing keys remain present; new fields are additive.
  - 失敗検出: schema v2 consumers break because existing keys disappear.
  - 検証方法: `uv run pytest tests/cli_runtime/test_sync.py -k deps_issues`.
  - 関連 closure id: `cl-011`.

Step closure contract:

- S03 closes when JSON tests prove additive lifecycle/disposition exposure and active graph/context separation.
- Amendment trigger: a schema version bump or key removal appears necessary.

### S04 PlantUML Rendering

- Behavior goal: `deps-issues.puml` and `deps-raw.puml` render active dependency work surfaces without done/closed/resolved-only noise.
- Depends on: S03.
- Unblocks: S90.
- Allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/puml.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py` only for payload-level filtering that must feed PUML
  - `tests/unit/presentation/test_runtime_sync_s07.py`
  - `tests/unit/presentation/test_deps_raw_puml.py`
  - `tests/cli_runtime/test_sync.py`
- Forbidden changes:
  - domain/application readiness rules.
  - new `deps-raw-all.puml` artifact.
  - hiding active empty-open blockers.
  - using presentation-only inference that contradicts `dependency_disposition`.
- Closure IDs: `cl-012`, `cl-013`, `cl-014`, `cl-015`.
- Review gate: `code-reviewer` before commit.
- Commit boundary: commit only S04 rendering/test changes.

Delegation contract:

- Delegated role: `dev-coder`.
- Required output: PUML snippets proving omitted satisfied-only content and retained active blockers/raw_direct edges.
- Stop conditions: renderer cannot consume evaluated fields from JSON; requirement would require complete raw audit view; PlantUML package representation conflicts with existing tests beyond accepted scope.

Concrete test cases:

- `tc-s04-001` red-required: `deps-issues.puml` omits satisfied-only high-level dependency.
  - 前提: GitHub-open all-descendant-done epic dependency is recorded in `dependency_contexts`.
  - 操作: render `deps-issues.puml`.
  - 期待結果: no `satisfied (...)` edge, no active high-level node solely for that satisfied dependency, and no `blocks` edge.
  - 失敗検出: old dashed satisfied edge still renders.
  - 検証方法: `uv run pytest tests/cli_runtime/test_sync.py -k all_done_expanded_high_level`.
  - 関連 closure id: `cl-012`.

- `tc-s04-002` red-required: `deps-issues.puml` keeps empty open blockers with `blocks` labels.
  - 前提: target issue depends on empty open epic/initiative.
  - 操作: render `deps-issues.puml`.
  - 期待結果: active blocker nodes are visible and edges are labeled `blocks`, not user-facing `raw_direct`.
  - 失敗検出: blocker edge is hidden or label exposes `raw_direct`.
  - 検証方法: `uv run pytest tests/cli_runtime/test_sync.py -k empty_open`.
  - 関連 closure id: `cl-013`.

- `tc-s04-003` red-required: `deps-raw.puml` is active raw direct view with package high-level nodes.
  - 前提: raw `.meta.json.depends_on` contains issue, epic, and initiative direct edges, including resolved-only high-level context.
  - 操作: render `deps-raw.puml`.
  - 期待結果: active raw direct edges are labeled `raw_direct`; epic/initiative use `package`; done issues, closed high-level nodes, and resolved-only high-level noise are omitted.
  - 失敗検出: raw view becomes complete historical audit or renders high-level nodes as rectangles.
  - 検証方法: `uv run pytest tests/unit/presentation/test_deps_raw_puml.py` and `uv run pytest tests/cli_runtime/test_sync.py -k deps_raw`.
  - 関連 closure id: `cl-014`.

- `tc-s04-004` manual-required: PlantUML visual inspection.
  - 前提: realistic fixture with ready/blocked/done/satisfied contexts.
  - 操作: generate or refresh manual fixture PUML and inspect `deps-issues.puml` / `deps-raw.puml`.
  - 期待結果: diagrams show actionable blockers/work only; no overlap-causing node flood from done/closed/resolved-only context.
  - 失敗検出: text assertions pass but diagram is unreadable or misleading.
  - 検証方法: manual evidence recorded in `report.md`; include command, fixture path, and observed summary.
  - 関連 closure id: `cl-015`.

Step closure contract:

- S04 closes when PUML tests and manual evidence prove active readiness/raw views match the design.
- Amendment trigger: manual inspection reveals a needed UX rule not present in requirement/design.

### S90 Docs Impact Resolution / Docs Refresh

- Behavior goal: provider-side docs and dogfooding docs explain lifecycle vs disposition, generated artifact roles, and raw vs readiness authority.
- Depends on: S04.
- Allowed paths:
  - `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
  - `spec-dock/docs/reference_deps.md`
  - `spec-dock/docs/reference_sync.md`
  - report evidence only after canonical adoption
- Forbidden changes:
  - workflow policy rewrites outside the issue scope.
  - template/skill/agent changes unless a docs impact review explicitly requires plan amendment.
  - canonical issue docs without main-orchestrator adoption.
- Closure IDs: `cl-016`, `cl-017`.
- Review gate: `spec-reviewer` docs/spec alignment before commit.
- Commit boundary: commit only S90 docs/manual evidence changes.

Delegation contract:

- Delegated role: `doc-writer`.
- Required output: docs changed, docs diff summary, manual verification evidence path/commands, and any unresolved docs risk.
- Stop conditions: docs change requires workflow lifecycle policy beyond `reference_deps.md` / `reference_sync.md`; dogfooding docs cannot be refreshed without scaffold/update decision.

Concrete test cases:

- `tc-s90-001` inspect-only: docs define lifecycle/disposition separation.
  - テスト不要理由: docs-only assertion; behavior already covered in S01-S04.
  - 代替検証方法: inspect provider and dogfooding docs for `lifecycle_state`, `dependency_disposition`, `disposition_basis`, `deps-issues` authority, and `deps-raw` non-authority wording.
  - 期待結果: docs do not imply GitHub open means dependency blocking.
  - 記録先: `report.md` Docs Impact Resolution and Final Spec Review Gate.
  - 関連 closure id: `cl-016`.

- `tc-s90-002` manual-required: realistic manual sync/PlantUML check.
  - 前提: manual fixture can exercise empty open, all-done open, closed high-level, done issue, and raw direct edge scenarios.
  - 操作: run focused `sync`/`deps check` commands on the fixture and inspect generated PlantUML text/visual output.
  - 期待結果: JSON readiness and PUML visibility agree with accepted requirement.
  - 失敗検出: automated tests miss a realistic mixed-state mismatch.
  - 検証方法: record commands, fixture path, and observed results in `report.md`.
  - 関連 closure id: `cl-017`.

Step closure contract:

- S90 closes when docs impact is either updated and reviewed or explicitly proven unnecessary with evidence. For this issue, docs update is expected by requirement/design.
- Amendment trigger: docs impact expands into workflow/spec authoring policy changes.

### S99 Final Quality Gate

- Behavior goal: confirm issue-wide quality after all step commits.
- Depends on: S01-S04 and S90.
- Allowed paths:
  - `spec-dock/active/issue/report.md` after main-orchestrator adoption
  - final delivery evidence surfaces selected by orchestrator
- Forbidden changes:
  - new product implementation changes unless routed back to the relevant step and re-reviewed.
  - using final review as substitute for per-step review.
- Closure IDs: `cl-018`, `cl-019`, `cl-020`.
- Review gates:
  - `qa-reviewer` for obligation coverage and integration/manual test sufficiency.
  - issue-wide `code-reviewer` for integrated runtime/test/docs diff.
  - `spec-reviewer` for requirement/design/plan/report/implementation/test/docs alignment.

Concrete test cases:

- `tc-s99-001` covered-existing: focused regression lane.
  - 前提: S01-S04/S90 commits are complete.
  - 操作: run focused suites named by prior steps plus `uv run pytest tests/unit tests/cli_runtime/test_sync.py tests/cli_runtime/test_deps.py tests/cli_runtime/test_issue_lifecycle.py`.
  - 期待結果: all pass or failures are unrelated and explicitly waived by reviewer policy.
  - 失敗検出: integration drift between domain/application/presentation/docs.
  - 検証方法: command output recorded in report.
  - 関連 closure id: `cl-018`.

- `tc-s99-002` covered-existing: final repo validation.
  - 前提: focused tests pass.
  - 操作: `./spec-dock/scripts/spec-dock validate` and `./spec-dock/scripts/spec-dock sync`.
  - 期待結果: validation/sync complete successfully; no unexpected canonical or generated drift remains unaccounted.
  - 失敗検出: scaffold/dogfooding integration is stale or invalid.
  - 検証方法: report Final QA Gate / Final Spec Review Gate.
  - 関連 closure id: `cl-019`.

- `tc-s99-003` manual-required: final reviewer triad.
  - 前提: all implementation steps are committed or approved-no-op with evidence.
  - 操作: run final `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer`.
  - 期待結果: all pass; any fail routes back to bounded step repair and re-review.
  - 失敗検出: final authority is claimed without reviewer pass.
  - 検証方法: report Reviewer Gate Status and final response.
  - 関連 closure id: `cl-020`.

Step closure contract:

- S99 closes only after final QA/code/spec gates pass and final report/delivery evidence is complete.
- Amendment trigger: final reviewer identifies missing closure row, new bug class, or spec mismatch.

## 6. Test Strategy Mapping

Spec-Locked Closure Index:

| ID | Step | Spec link | Locked expectation | Observable input/state | Bug class guarded | Required | Evidence level |
|---|---|---|---|---|---|---|---|
| cl-001 | S01 | AC-001 | empty open high-level dependency is blocking | `evaluate_readiness()` with empty open epic/init | lifecycle/disposition conflation | yes | red-required |
| cl-002 | S01 | AC-002, EC-001 | GitHub-open all-done high-level dependency is satisfied | expanded high-level context with all done descendants | todo projection false-empty / open parent false-block | yes | red-required |
| cl-003 | S01 | EC-002 | unknown descendant/high-level state fails closed | unknown/missing descendant status | silent satisfied on unknown | yes | red-required |
| cl-004 | S01 | AC-006 | raw storage/mutation rules unchanged | existing raw validation tests | storage contract drift | yes | covered-existing |
| cl-005 | S02 | AC-002, AC-003 | `deps check --json` reports ready satisfied context | CLI/app check with all-done open parent | command/render mismatch | yes | red-required |
| cl-006 | S02 | AC-001 | `active set` / `issue start` reject empty open blocker | active/issue-start readiness guard | dependency bypass | yes | red-required |
| cl-007 | S02 | EC-001 | descendant count uses full graph | done descendants absent from todo projection | false empty container | yes | red-required |
| cl-008 | S02 | AC-006 | mutation CLI behavior unchanged | `deps add/remove/check` regression | unintended mutation API change | yes | covered-existing |
| cl-009 | S03 | AC-003 | JSON surfaces lifecycle and disposition fields | `deps check --json` payload | machine consumer ambiguity | yes | red-required |
| cl-010 | S03 | AC-003, AC-004 | active graph and dependency contexts are separated | `.agent/deps-issues.json` | satisfied context lost or over-rendered | yes | red-required |
| cl-011 | S03 | AC-006 | schema v2 keys remain compatible | sync JSON payload | breaking JSON consumers | yes | covered-existing |
| cl-012 | S04 | AC-004 | `deps-issues.puml` omits satisfied-only context | all-done open parent diagram | done/resolved visual noise | yes | red-required |
| cl-013 | S04 | AC-001, AC-004 | active blockers render with `blocks` | empty open blocker diagram | hidden blocker / confusing label | yes | red-required |
| cl-014 | S04 | AC-005, EC-004 | `deps-raw.puml` is active raw direct view | raw direct high-level/issue dependencies | raw view mistaken for readiness authority | yes | red-required |
| cl-015 | S04 | AC-004, AC-005 | mixed-state PlantUML is visually usable | realistic manual fixture | unreadable diagram despite text tests | yes | manual-required |
| cl-016 | S90 | AC-006, EC-004 | docs explain lifecycle vs disposition and artifact authority | provider/dogfooding docs | operator docs drift | yes | inspect-only |
| cl-017 | S90 | AC-001-AC-005 | realistic manual evidence matches docs/runtime | manual sync/deps check/PUML | fixture-free false confidence | yes | manual-required |
| cl-018 | S99 | all AC/EC | focused regression lane passes | test suite commands | cross-layer regression | yes | covered-existing |
| cl-019 | S99 | AC-006 | `validate` and `sync` pass | repo-local validation/sync | dogfooding invalid state | yes | covered-existing |
| cl-020 | S99 | all AC/EC | final QA/code/spec reviewers pass | final reviewer triad | premature completion claim | yes | manual-required |

## 7. Review Gates

- Per-step gate:
  - S01-S04: `code-reviewer` pass before each step commit.
  - S90: `spec-reviewer` docs/spec alignment pass before commit.
- Step Result Approval:
  - red/green or alternative evidence recorded.
  - step reviewer pass recorded.
  - step commit made.
  - post-commit clean check run.
- Final gate:
  - `qa-reviewer` confirms obligation coverage and integration/manual sufficiency.
  - issue-wide `code-reviewer` reviews integrated diff.
  - final `spec-reviewer` confirms requirement/design/plan/report/implementation/test/docs alignment.
- Reviewer fail handling:
  - Repair inside the same step scope when possible, rerun focused tests, rerun reviewer.
  - If repair crosses allowed paths or changes a locked expectation, stop for plan amendment and fresh spec review.

## 8. Rollback / Compatibility

- Rollback:
  - Revert the issue diff by step commit if a downstream step fails.
  - Rerun `./spec-dock/scripts/spec-dock sync` after rollback to avoid stale generated artifacts.
- Compatibility:
  - Keep `.meta.json.depends_on` unchanged.
  - Keep `deps add/remove` syntax and storage mutation contract unchanged.
  - Keep `.agent/deps-issues.json` `schema_version: 2`; add fields rather than removing existing keys unless main orchestrator approves an amendment.
  - Keep complete raw audit outside `deps-raw.puml`; point to `.meta.json.depends_on` and `.agent/index-all.json`.

## 9. Docs Impact

- Expected provider docs:
  - `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
- Expected dogfooding docs:
  - `spec-dock/docs/reference_deps.md`
  - `spec-dock/docs/reference_sync.md`
- Required content:
  - `lifecycle_state` is a lifecycle fact.
  - `dependency_disposition` is readiness interpretation.
  - `disposition_basis` explains the decision.
  - `deps-issues.*` is readiness/blocker authority.
  - `deps-raw.puml` is active raw direct visual/debug output, not complete audit or readiness authority.
- Docs review:
  - S90 requires `spec-reviewer` pass and report evidence.

## 10. Final Quality Gate

- Required commands before completion:
  - `uv run pytest tests/unit/domain/test_deps.py`
  - `uv run pytest tests/unit/application/test_check_deps.py tests/unit/application/test_set_active.py`
  - `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/unit/presentation/test_deps_raw_puml.py`
  - `uv run pytest tests/cli_runtime/test_deps.py tests/cli_runtime/test_sync.py tests/cli_runtime/test_issue_lifecycle.py`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
- Required human/agent checks:
  - realistic manual PUML inspection.
  - final `qa-reviewer` pass.
  - issue-wide `code-reviewer` pass.
  - final `spec-reviewer` pass.
- Completion is not claimable if any required reviewer is `failed`, `unavailable`, `denied`, `waived`, or `provisional`.

## 11. Plan Blockers

- None found in the approved requirement/design surface.
- Planning risk: existing code already has partial high-level readiness behavior, so implementation should not duplicate a parallel model. It should extend the existing `DepsDependencyContext` / `DepsNodeBlocker` / `DepsEvaluation` contract or introduce one evaluated context object only where it reduces ambiguity.
- Clarification candidates: none. If implementation finds that `dependency_contexts` cannot be additive under schema v2, stop for plan amendment and spec review.

## 12. Integration Notes for Main Orchestrator

- Created discussion artifact:
  - `spec-dock/active/issue/discussions/20260619t014201z-draft-plan-dependency-disposition-rendering.md`
- Command used:
  - `./spec-dock/scripts/spec-dock new doc draft-plan --issue iss-00209 --title "Dependency disposition rendering implementation plan" --slug dependency-disposition-rendering`
- Note:
  - The command stdout included an extra `spec-dock/spec-dock/...` prefix, but the actual file was created under the active issue `discussions/` directory.
- Leaf evidence used:
  - User-approved interview evidence for Option A.
  - Source-grounded research.
  - Existing system-architect draft design evidence.
  - Current runtime/test file inspection.
- Forbidden actions avoided:
  - No canonical `requirement.md`, `design.md`, `plan.md`, or `report.md` edit.
  - No source code, tests, docs outside this discussion draft, package/config, workflow, secret, or GitHub state edit.
  - No promotion, reviewer-pass claim, phase completion, implementation readiness claim, or final authority claim.
- Unresolved design gaps:
  - none.

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
