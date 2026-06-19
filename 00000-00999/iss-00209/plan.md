---
種別: 実装計画書（Issue）
ID: "iss-00209"
タイトル: "Improve dependency PlantUML view rendering"
関連GitHub: ["#209"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
依存: ["requirement.md", "design.md"]
親: ["epic-00059", "init-local-00003"]
---

# iss-00209 Improve dependency PlantUML view rendering — 実装計画

## この計画で満たす要件ID
- AC:
  - AC-001, AC-002, AC-003, AC-004, AC-005, AC-006
- EC:
  - EC-001, EC-002, EC-003, EC-004
- 制約:
  - `.meta.json.depends_on` storage format and `deps add/remove` mutation contract remain unchanged.
  - `deps-issues.json` keeps schema version 2 with additive fields.
  - `deps-issues.puml` and `deps-raw.puml` consume evaluated readiness context, not local presentation-only inference.

## 依存関係から導く実装順序
- S01 Domain Disposition Contract:
  - `domain/models.py` and `domain/deps.py` define evaluated lifecycle / disposition semantics.
- S02 Application Readiness Consumers:
  - `deps check`, `active set`, `issue start`, and `sync` consume the domain result.
- S03 Presentation JSON Contract:
  - `.agent/deps-issues.json` and `deps check --json` expose additive lifecycle / disposition context.
- S04 PlantUML Rendering:
  - `deps-issues.puml` and `deps-raw.puml` render active graph views from evaluated context.
- S90 Docs / Manual Verification:
  - provider docs, dogfooding docs, and realistic manual evidence align with runtime behavior.
- S99 Final Quality Gate:
  - integrated tests, validate/sync, QA/code/spec reviews.

## ステップ一覧
- S01:
  - 観測可能な振る舞い: high-level dependency disposition is classified in domain.
  - 依存: approved requirement/design.
  - unblock: S02, S03, S04.
  - 対象ファイル: domain models / deps and domain tests.
  - レビューゲート: code-reviewer.
- S02:
  - 観測可能な振る舞い: command/application readiness consumers agree on disposition.
  - 依存: S01.
  - unblock: S03, S04.
  - 対象ファイル: application check/active/sync consumers and application/CLI tests.
  - レビューゲート: code-reviewer.
- S03:
  - 観測可能な振る舞い: machine-readable JSON carries lifecycle/disposition context while active graph remains separate.
  - 依存: S01, S02.
  - unblock: S04.
  - 対象ファイル: presentation JSON and sync/deps JSON tests.
  - レビューゲート: code-reviewer.
- S04:
  - 観測可能な振る舞い: PlantUML active graphs remove done/closed/resolved-only noise and keep active blockers.
  - 依存: S03.
  - unblock: S90.
  - 対象ファイル: PUML renderer and presentation/CLI tests.
  - レビューゲート: code-reviewer.
- S90:
  - 観測可能な振る舞い: docs/manual evidence explain and validate the new authority.
  - 依存: S04.
  - unblock: S99.
  - 対象ファイル: provider docs, dogfooding docs, manual-tests/report evidence.
  - レビューゲート: spec-reviewer.
- S99:
  - 観測可能な振る舞い: issue-wide quality gates pass.
  - 依存: S01-S04, S90.
  - unblock: issue execution closeout.
  - 対象ファイル: report evidence only unless reviewer repair routes back to a prior step.
  - レビューゲート: qa-reviewer, code-reviewer, spec-reviewer.

## 要件 ↔ ステップ対応
- AC-001 -> S01, S02, S03, S04
- AC-002 -> S01, S02, S03, S04
- AC-003 -> S01, S03
- AC-004 -> S04
- AC-005 -> S04
- AC-006 -> S01-S04, S90
- EC-001 -> S01, S02
- EC-002 -> S01, S02
- EC-003 -> S01, S02
- EC-004 -> S03, S04, S90

## 仕様固定クロージャ索引（Spec-Locked Closure Index）
| ID | Step | Slice | Type | Spec link | Locked expectation | Observable input/state | Bug class guarded | Required | Evidence level | Closure evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| cl-001 | S01 | domain | acceptance | AC-001 | empty open high-level dependency is blocking | `evaluate_readiness()` with empty open epic/init | lifecycle/disposition conflation | yes | red-required | report step closure |
| cl-002 | S01 | domain | acceptance | AC-002, EC-001 | GitHub-open all-done high-level dependency is satisfied | expanded high-level context with all done descendants | todo projection false-empty | yes | red-required | report step closure |
| cl-003 | S01 | domain | negative | EC-002 | unknown descendant/high-level state fails closed | unknown/missing descendant status | silent satisfied on unknown | yes | red-required | report step closure |
| cl-021 | S01 | domain | acceptance | EC-003 | GitHub-closed high-level dependency is satisfied even when empty | closed empty epic/init dependency context | closed lifecycle misread as empty-open blocker | yes | red-required | report step closure |
| cl-004 | S01 | domain | regression | AC-006 | raw storage/mutation rules unchanged | existing raw validation tests | storage contract drift | yes | covered-existing | report step closure |
| cl-005 | S02 | application | acceptance | AC-002, AC-003 | `deps check --json` reports ready satisfied context | CLI/app check with all-done open parent | command/render mismatch | yes | red-required | report step closure |
| cl-006 | S02 | application | acceptance | AC-001 | `active set` / `issue start` reject empty open blocker | active/issue-start readiness guard | dependency bypass | yes | red-required | report step closure |
| cl-007 | S02 | application | negative | EC-001 | descendant count uses full graph | done descendants absent from todo projection | false empty container | yes | red-required | report step closure |
| cl-022 | S02 | application | acceptance | EC-003 | commands do not block on closed empty high-level dependency | `deps check` / active guard with closed empty parent dependency | command guard ignores lifecycle closure | yes | red-required | report step closure |
| cl-023 | S02 | application | negative | EC-002 | commands fail closed on unknown high-level or descendant state | `deps check` / active guard with unresolved dependency context | application bypasses domain fail-closed rule | yes | red-required | report step closure |
| cl-008 | S02 | application | regression | AC-006 | mutation CLI behavior unchanged | `deps add/remove/check` regression | unintended mutation API change | yes | covered-existing | report step closure |
| cl-009 | S03 | JSON | acceptance | AC-003 | JSON surfaces lifecycle and disposition fields | `deps check --json` payload | machine consumer ambiguity | yes | red-required | report step closure |
| cl-010 | S03 | JSON | acceptance | AC-003, AC-004 | active graph and dependency contexts are separated | `.agent/deps-issues.json` | satisfied context lost or over-rendered | yes | red-required | report step closure |
| cl-011 | S03 | JSON | regression | AC-006 | schema v2 keys remain compatible | sync JSON payload | breaking JSON consumers | yes | covered-existing | report step closure |
| cl-012 | S04 | PUML | acceptance | AC-004 | `deps-issues.puml` omits satisfied-only context | all-done open parent diagram | done/resolved visual noise | yes | red-required | report step closure |
| cl-013 | S04 | PUML | acceptance | AC-001, AC-004 | active blockers render with `blocks` | empty open blocker diagram | hidden blocker / confusing label | yes | red-required | report step closure |
| cl-014 | S04 | PUML | acceptance | AC-005, EC-004 | `deps-raw.puml` is active raw direct view | raw direct high-level/issue dependencies | raw view mistaken for readiness authority | yes | red-required | report step closure |
| cl-015 | S04 | PUML/manual | acceptance | AC-004, AC-005 | mixed-state PlantUML is visually usable | realistic manual fixture | unreadable diagram despite text tests | yes | manual-required | report manual evidence |
| cl-016 | S90 | docs | docs | AC-006, EC-004 | docs explain lifecycle vs disposition and artifact authority | provider/dogfooding docs | operator docs drift | yes | inspect-only | report docs evidence |
| cl-017 | S90 | manual | acceptance | AC-001-AC-005 | realistic manual evidence matches docs/runtime | manual sync/deps check/PUML | fixture-free false confidence | yes | manual-required | report manual evidence |
| cl-018 | S99 | final | regression | all AC/EC | focused regression lane passes | test suite commands | cross-layer regression | yes | covered-existing | report final gate |
| cl-019 | S99 | final | regression | AC-006 | `validate` and `sync` pass | repo-local validation/sync | dogfooding invalid state | yes | covered-existing | report final gate |
| cl-020 | S99 | final | review | all AC/EC | final QA/code/spec reviewers pass | final reviewer triad | premature completion claim | yes | manual-required | report final gate |

## 実装ステップ

### S01 — Domain Disposition Contract
- behavior goal:
  - `evaluate_readiness()` returns explicit lifecycle / disposition / basis context for high-level dependencies.
- planned contract:
  - scope: domain models and dependency readiness evaluator only.
  - allowed paths:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/models.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`
    - `tests/unit/domain/test_deps.py`
  - forbidden changes: storage format, infra topology reader mutation behavior, application command output, presentation rendering.
  - test obligation: `cl-001`, `cl-002`, `cl-003`, `cl-021` red-required; `cl-004` covered-existing.
  - red or alternative evidence requirement: add failing domain tests before implementation for new disposition branches.
  - green verification: `uv run pytest tests/unit/domain/test_deps.py`.
  - refactor guardrail: no broad model rewrite beyond additive lifecycle / disposition fields needed by the evaluator.
- delegation contract:
  - delegated role: dev-coder.
  - input docs: `requirement.md`, `design.md`, this `plan.md`, and current `domain/deps.py` / `domain/models.py` tests.
  - allowed paths: same as planned contract allowed paths.
  - forbidden changes: application, presentation, docs, persisted `.meta.json` shape, `deps add/remove` mutation behavior.
  - acceptance criteria: closure ids `cl-001`, `cl-002`, `cl-003`, `cl-004`, `cl-021` have reportable evidence.
  - required tests or docs-only verification: `uv run pytest tests/unit/domain/test_deps.py`.
  - reviewer focus: domain semantics, fail-closed unknown handling, full descendant graph basis, storage compatibility.
  - stop conditions: implementing the rule requires persistence changes, application command behavior, or schema version changes.
  - output required: changed files, tests run/result, unresolved risks, and `Ledger Note` or `No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧

- `tc-s01-001` acceptance: empty open high-level dependency blocks
  - 前提: domain fixture has an open epic or initiative dependency with no descendant issue nodes.
  - 操作: call the domain readiness evaluator for an issue depending on that high-level node.
  - 期待結果: dependency context has `dependency_disposition=blocking`, an empty/open basis, and a node blocker.
  - 失敗検出: empty open high-level dependency is incorrectly treated as satisfied or omitted.
  - 検証方法: red-first assertion in `tests/unit/domain/test_deps.py`, then `uv run pytest tests/unit/domain/test_deps.py`.
  - 関連 closure id: `cl-001`

- `tc-s01-002` acceptance: open all-descendant-done high-level dependency is satisfied
  - 前提: domain fixture has an open epic or initiative whose full graph descendant issues are all done/closed.
  - 操作: evaluate readiness for an issue depending on that high-level node.
  - 期待結果: dependency context has `dependency_disposition=satisfied`, `disposition_basis=all_descendant_issues_done`, and no node blocker.
  - 失敗検出: done descendants absent from todo projection cause a false empty-container blocker.
  - 検証方法: red-first assertion in `tests/unit/domain/test_deps.py`, then focused domain pytest.
  - 関連 closure id: `cl-002`

- `tc-s01-003` negative: unknown high-level or descendant state fails closed
  - 前提: dependency target or descendant status cannot be resolved from the topology/index fixture.
  - 操作: evaluate readiness for an issue depending on that unresolved context.
  - 期待結果: dependency context has `dependency_disposition=indeterminate` with `disposition_basis=empty_unknown_container` or `descendant_issue_unknown`, and does not mark the dependency ready.
  - 失敗検出: missing lifecycle/status data silently becomes satisfied.
  - 検証方法: red-first negative assertion in `tests/unit/domain/test_deps.py`.
  - 関連 closure id: `cl-003`

- `tc-s01-004` acceptance: closed empty high-level dependency is satisfied
  - 前提: domain fixture has a GitHub-closed epic or initiative dependency with no descendant issue nodes.
  - 操作: evaluate readiness for an issue depending on that high-level node.
  - 期待結果: dependency context has `dependency_disposition=satisfied`, `disposition_basis=lifecycle_closed`, and no node blocker.
  - 失敗検出: closed empty high-level dependency is misclassified as empty open blocker.
  - 検証方法: red-first assertion in `tests/unit/domain/test_deps.py`.
  - 関連 closure id: `cl-021`

- `tc-s01-005` regression: raw dependency storage validation remains unchanged
  - 前提: existing raw dependency fixtures and validation cases are present.
  - 操作: run the focused domain dependency test file.
  - 期待結果: existing raw dependency validation remains green without `.meta.json.depends_on` format changes.
  - 失敗検出: lifecycle/disposition work changes raw mutation/storage semantics.
  - 検証方法: `uv run pytest tests/unit/domain/test_deps.py`.
  - 関連 closure id: `cl-004`

- step closure contract:
  - Close S01 only after all S01 closure ids have observed evidence in `report.md`.
- report evidence destination:
  - `実装記録`, `TDD / Red / Green / Refactor Evidence`, `Step Contract Closure`, `Test Contract Closure`, `Reviewer Gate Status`, `Step Commit Gate`.
- step gate:
  - code-reviewer `review_status: pass`, then commit S01 only.
- amendment trigger:
  - implementation requires persisted storage change, new artifact, or mutation command change.

### S02 — Application Readiness Consumers
- behavior goal:
  - `deps check`, `active set`, `issue start`, and `sync` consume the same evaluated disposition.
- planned contract:
  - scope: application/CLI readiness consumers that decide blocked vs ready.
  - allowed paths:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
    - `tests/unit/application/test_check_deps.py`
    - `tests/unit/application/test_set_active.py`
    - `tests/cli_runtime/test_deps.py`
    - `tests/cli_runtime/test_issue_lifecycle.py`
  - forbidden changes: presentation rendering, docs, GitHub lifecycle close/reopen policy, dependency bypass/force semantics.
  - test obligation: `cl-005`, `cl-006`, `cl-007`, `cl-022`, `cl-023` red-required; `cl-008` covered-existing.
  - red or alternative evidence requirement: add failing application/CLI tests that observe command readiness decisions.
  - green verification:
    - `uv run pytest tests/unit/application/test_check_deps.py tests/unit/application/test_set_active.py`
    - `uv run pytest tests/cli_runtime/test_deps.py tests/cli_runtime/test_issue_lifecycle.py`
  - refactor guardrail: reuse S01 domain result rather than duplicating lifecycle inference in command handlers.
- delegation contract:
  - delegated role: dev-coder.
  - input docs: `requirement.md`, `design.md`, this `plan.md`, S01 implementation, existing command/application tests.
  - allowed paths: same as planned contract allowed paths.
  - forbidden changes: presentation JSON/PUML formatting, docs, storage mutation contract, new CLI flags.
  - acceptance criteria: closure ids `cl-005`, `cl-006`, `cl-007`, `cl-008`, `cl-022`, `cl-023` have reportable evidence.
  - required tests or docs-only verification: the S02 green verification commands.
  - reviewer focus: every readiness consumer uses the same evaluated disposition and closed empty parents do not block.
  - stop conditions: a new user-facing option, changed force behavior, or persistence/schema change is needed.
  - output required: changed files, tests run/result, command behavior summary, unresolved risks, and ledger note/no-material-decision statement.

#### 具体テストケース一覧

- `tc-s02-001` acceptance: `deps check --json` is ready for open all-done high-level dependency
  - 前提: CLI/runtime fixture has an issue depending on an open epic/init whose full graph descendant issues are all done.
  - 操作: run `deps check --json`, active-set guard, and issue-start guard through the application or CLI test harness.
  - 期待結果: `deps check` exits `0`, active-set and issue-start readiness guards allow the target, and JSON includes satisfied high-level dependency context.
  - 失敗検出: any readiness consumer still blocks because the parent container is GitHub-open.
  - 検証方法: red-first tests in `tests/unit/application/test_check_deps.py`, `tests/unit/application/test_set_active.py`, `tests/cli_runtime/test_deps.py`, and/or `tests/cli_runtime/test_issue_lifecycle.py`.
  - 関連 closure id: `cl-005`

- `tc-s02-002` acceptance: `active set` / `issue start` reject empty open high-level blocker
  - 前提: candidate active issue depends on an open empty epic/init.
  - 操作: run `deps check --json`, active-set guard, and issue-start readiness guard tests.
  - 期待結果: `deps check --json` exits `3` and reports not ready with `dependency_disposition=blocking` and `disposition_basis=empty_open_container`; active-set and issue-start reject the target and report the high-level blocker.
  - 失敗検出: the main readiness command or guard commands bypass the empty open high-level blocker after the display filtering change.
  - 検証方法: red-first tests in `tests/unit/application/test_check_deps.py`, `tests/unit/application/test_set_active.py`, `tests/cli_runtime/test_deps.py`, and/or `tests/cli_runtime/test_issue_lifecycle.py`.
  - 関連 closure id: `cl-006`

- `tc-s02-003` negative: full graph descendants are counted even when absent from todo projection
  - 前提: fixture has done descendant issues that would be omitted from todo/active display projection.
  - 操作: run `deps check` and active readiness evaluation for a dependency on that parent.
  - 期待結果: done descendants are counted from the full graph, so the parent is not treated as empty.
  - 失敗検出: application uses todo-only projection and creates a false empty-container blocker.
  - 検証方法: application test in `tests/unit/application/test_check_deps.py`.
  - 関連 closure id: `cl-007`

- `tc-s02-004` acceptance: closed empty high-level dependency does not block commands
  - 前提: candidate issue depends on a GitHub-closed empty epic/init.
  - 操作: run `deps check`, active-set guard, and/or issue-start guard test harness.
  - 期待結果: the closed high-level dependency is satisfied and does not prevent readiness.
  - 失敗検出: command guard treats a closed empty parent as an empty open blocker.
  - 検証方法: red-first test in S02 application/CLI files.
  - 関連 closure id: `cl-022`

- `tc-s02-005` regression: mutation CLI behavior remains green
  - 前提: existing `deps add/remove/check` command tests remain unchanged.
  - 操作: run focused deps CLI tests.
  - 期待結果: mutation syntax and raw storage behavior are unchanged.
  - 失敗検出: readiness work changes dependency mutation API or output unexpectedly.
  - 検証方法: `uv run pytest tests/cli_runtime/test_deps.py`.
  - 関連 closure id: `cl-008`

- `tc-s02-006` negative: unknown high-level or descendant status fails closed in commands
  - 前提: application/CLI fixture has a dependency whose high-level lifecycle or descendant issue status cannot be resolved.
  - 操作: run `deps check` and active-set or issue-start guard through the application/CLI test harness.
  - 期待結果: command does not report the target ready and preserves `dependency_disposition=indeterminate` with `disposition_basis=empty_unknown_container` or `descendant_issue_unknown`.
  - 失敗検出: application layer ignores the domain fail-closed result and lets the target proceed.
  - 検証方法: red-first application/CLI test in `tests/unit/application/test_check_deps.py`, `tests/unit/application/test_set_active.py`, or `tests/cli_runtime/test_issue_lifecycle.py`.
  - 関連 closure id: `cl-023`

- step closure contract:
  - Close S02 only after S01 is committed and every S02 closure id has observed evidence in `report.md`.
- report evidence destination:
  - `実装記録`, `TDD / Red / Green / Refactor Evidence`, `Step Contract Closure`, `Test Contract Closure`, `Reviewer Gate Status`, `Step Commit Gate`.
- step gate:
  - code-reviewer `review_status: pass`, then commit S02 only.
- amendment trigger:
  - new CLI flag, changed force semantics, or storage/mutation behavior change becomes necessary.

### S03 — Presentation JSON Contract
- behavior goal:
  - machine-readable outputs preserve lifecycle fact and dependency disposition separately.
- planned contract:
  - scope: JSON projection for `.agent/deps-issues.json` and `deps check --json` only.
  - allowed paths:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
    - `tests/unit/presentation/test_runtime_sync_s07.py`
    - `tests/cli_runtime/test_sync.py`
    - `tests/cli_runtime/test_deps.py`
  - forbidden changes: PUML renderer changes, schema version bump, existing key removal.
  - test obligation: `cl-009`, `cl-010` red-required; `cl-011` covered-existing.
  - red or alternative evidence requirement: add failing JSON payload assertions before implementation.
  - green verification:
    - `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py -k deps_issues`
    - `uv run pytest tests/cli_runtime/test_sync.py -k deps_issues`
    - `uv run pytest tests/cli_runtime/test_deps.py -k json`
  - refactor guardrail: additive fields only; keep `schema_version: 2`.
- delegation contract:
  - delegated role: dev-coder.
  - input docs: `requirement.md`, `design.md`, this `plan.md`, S01/S02 implementation, existing sync/deps JSON tests.
  - allowed paths: same as planned contract allowed paths.
  - forbidden changes: PUML rendering, schema version bump, removal or rename of existing JSON keys.
  - acceptance criteria: closure ids `cl-009`, `cl-010`, `cl-011` have reportable evidence.
  - required tests or docs-only verification: S03 green verification commands.
  - reviewer focus: active graph `nodes`/`edges` remain separate from top-level `dependency_contexts`.
  - stop conditions: compatibility requires schema version bump or existing key removal.
  - output required: changed files, JSON before/after summary, tests run/result, unresolved risks, and ledger note/no-material-decision statement.

#### 具体テストケース一覧

- `tc-s03-001` acceptance: `deps check --json` includes lifecycle and disposition context
  - 前提: fixture includes issue, high-level, satisfied, blocking, and indeterminate dependency contexts.
  - 操作: run `deps check --json` through CLI/runtime tests.
  - 期待結果: each dependency context exposes lifecycle fact, `dependency_disposition`, and `disposition_basis`.
  - 失敗検出: machine consumers cannot distinguish GitHub lifecycle from readiness interpretation.
  - 検証方法: red-first assertion in `tests/cli_runtime/test_deps.py`.
  - 関連 closure id: `cl-009`

- `tc-s03-002` acceptance: active graph and dependency contexts are separated
  - 前提: sync fixture includes satisfied high-level context and active blockers.
  - 操作: run sync JSON projection test for `.agent/deps-issues.json`.
  - 期待結果: active `nodes`/`edges` omit satisfied-only graph items while top-level `dependency_contexts` preserves evaluated context with at least `source_node_id`, `source_issue_id`, `target_node_id`, `target_node_kind`, `target_issue_ids`, `expansion`, `lifecycle_state`, `lifecycle_source`, `dependency_disposition`, and `disposition_basis`.
  - 失敗検出: satisfied context is either lost from JSON or rendered into active graph noise.
  - 検証方法: red-first assertion in `tests/unit/presentation/test_runtime_sync_s07.py`.
  - 関連 closure id: `cl-010`

- `tc-s03-003` regression: schema v2 compatibility keys remain present
  - 前提: existing sync JSON payload compatibility expectations exist.
  - 操作: run focused sync/deps JSON regression tests.
  - 期待結果: existing keys remain present and `schema_version` stays `2`.
  - 失敗検出: additive context work breaks current JSON consumers.
  - 検証方法: `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py -k deps_issues` and CLI JSON tests.
  - 関連 closure id: `cl-011`

- step closure contract:
  - Close S03 only after S01/S02 are committed and JSON closure evidence is recorded.
- report evidence destination:
  - `実装記録`, `TDD / Red / Green / Refactor Evidence`, `Step Contract Closure`, `Test Contract Closure`, `Reviewer Gate Status`, `Step Commit Gate`.
- step gate:
  - code-reviewer `review_status: pass`, then commit S03 only.
- amendment trigger:
  - schema version bump or removal of existing keys appears necessary.

### S04 — PlantUML Rendering
- behavior goal:
  - `deps-issues.puml` and `deps-raw.puml` render active dependency work surfaces without done / closed / resolved-only noise.
- planned contract:
  - scope: PlantUML rendering and only the minimal JSON filtering needed by PUML payload generation.
  - allowed paths:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/puml.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py` only for PUML payload filtering.
    - `tests/unit/presentation/test_runtime_sync_s07.py`
    - `tests/unit/presentation/test_deps_raw_puml.py`
    - `tests/cli_runtime/test_sync.py`
  - forbidden changes: domain/application readiness rules, new `deps-raw-all.puml`, hiding active empty-open blockers.
  - test obligation: `cl-012`, `cl-013`, `cl-014` red-required; `cl-015` manual-required.
  - red or alternative evidence requirement: add failing text assertions for generated PUML and a manual inspection record for realistic output.
  - green verification:
    - `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/unit/presentation/test_deps_raw_puml.py`
    - `uv run pytest tests/cli_runtime/test_sync.py`
    - manual fixture evidence recorded in `report.md`.
  - refactor guardrail: rendering consumes evaluated context; do not reimplement readiness rules in `puml.py`.
- delegation contract:
  - delegated role: dev-coder.
  - input docs: `requirement.md`, `design.md`, this `plan.md`, S03 JSON contract, existing PUML tests.
  - allowed paths: same as planned contract allowed paths.
  - forbidden changes: domain/application readiness semantics, schema version, complete audit artifact creation, docs.
  - acceptance criteria: closure ids `cl-012`, `cl-013`, `cl-014`, `cl-015` have reportable evidence.
  - required tests or docs-only verification: S04 green verification commands and manual PlantUML evidence.
  - reviewer focus: active blockers stay visible, satisfied-only noise is omitted, `blocks` vs `raw_direct` labels match view semantics.
  - stop conditions: a new UX rule or new artifact is needed outside requirement/design.
  - output required: changed files, generated PUML observations, tests/manual verification result, unresolved risks, and ledger note/no-material-decision statement.

#### 具体テストケース一覧

- `tc-s04-001` acceptance: `deps-issues.puml` omits satisfied-only high-level graph items
  - 前提: sync fixture includes an open all-descendant-done high-level dependency.
  - 操作: generate `deps-issues.puml` through presentation/sync tests.
  - 期待結果: satisfied-only parent node and edge are absent from the active readiness graph.
  - 失敗検出: done/resolved high-level dependencies continue to clutter the diagram.
  - 検証方法: red-first PUML assertion in `tests/unit/presentation/test_runtime_sync_s07.py`.
  - 関連 closure id: `cl-012`

- `tc-s04-002` acceptance: active empty-open blockers render with `blocks`
  - 前提: fixture includes an issue blocked by an open empty epic/init.
  - 操作: generate `deps-issues.puml`.
  - 期待結果: the active blocker remains visible and the edge label uses `blocks`, not user-facing `raw_direct`.
  - 失敗検出: rendering hides an actual blocker or labels readiness view with raw edge semantics.
  - 検証方法: red-first PUML assertion in presentation tests.
  - 関連 closure id: `cl-013`

- `tc-s04-003` acceptance: `deps-raw.puml` is active raw direct view
  - 前提: fixture includes raw direct dependencies across issue, epic, and initiative nodes with some resolved-only contexts.
  - 操作: generate `deps-raw.puml`.
  - 期待結果: active raw direct edges use `raw_direct`, high-level nodes render as packages, and resolved-only noise is omitted.
  - 失敗検出: raw view is mistaken for complete audit or readiness authority.
  - 検証方法: red-first assertions in `tests/unit/presentation/test_deps_raw_puml.py`.
  - 関連 closure id: `cl-014`

- `tc-s04-004` manual: realistic mixed-state PlantUML remains readable
  - 前提: manual fixture models empty open blockers, closed parents, all-done parents, active issue blockers, and raw direct edges.
  - 操作: generate the PlantUML outputs and inspect/render them as the manual test plan defines.
  - 期待結果: active work surface is understandable and does not show done/closed/resolved-only clutter.
  - 失敗検出: textual assertions pass but actual diagram remains misleading or unreadable.
  - 検証方法: manual evidence recorded in `report.md` with file paths and observations.
  - 関連 closure id: `cl-015`

- step closure contract:
  - Close S04 only after S03 is committed, automated PUML tests pass, and manual evidence is recorded.
- report evidence destination:
  - `実装記録`, `TDD / Red / Green / Refactor Evidence`, `Step Contract Closure`, `Test Contract Closure`, `Closure Coverage`, `Reviewer Gate Status`, `Step Commit Gate`.
- step gate:
  - code-reviewer `review_status: pass`, then commit S04 only.
- amendment trigger:
  - manual inspection reveals a new UX rule not present in requirement/design.

### S90 — Docs Impact Resolution / Manual Evidence
- behavior goal:
  - provider docs, dogfooding docs, and manual evidence explain and validate lifecycle vs disposition.
- planned contract:
  - scope: provider/dogfooding reference docs and manual evidence only.
  - allowed paths:
    - `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
    - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
    - `spec-dock/docs/reference_deps.md`
    - `spec-dock/docs/reference_sync.md`
    - `manual-tests/**` if manual fixture refresh is required.
    - `spec-dock/active/issue/report.md` evidence updates.
  - forbidden changes: workflow policy rewrites, skill/template changes, source runtime changes.
  - test obligation: `cl-016` inspect-only; `cl-017` manual-required.
  - red or alternative evidence requirement: docs diff inspection plus manual evidence; no code red test required for docs-only text.
  - green verification: docs inspection and manual test observations recorded in `report.md`.
  - refactor guardrail: only document implemented behavior; do not introduce new lifecycle policy.
- delegation contract:
  - delegated role: doc-writer.
  - input docs: `requirement.md`, `design.md`, this `plan.md`, final S01-S04 report evidence, current reference docs.
  - allowed paths: same as planned contract allowed paths.
  - forbidden changes: runtime source, tests, workflow policy, skills, templates.
  - acceptance criteria: closure ids `cl-016`, `cl-017` have reportable evidence.
  - required tests or docs-only verification: docs diff inspection and manual evidence path in `report.md`.
  - reviewer focus: docs accurately distinguish lifecycle facts from readiness disposition and artifact authority.
  - stop conditions: docs require policy changes outside reference docs or manual evidence contradicts runtime behavior.
  - output required: changed docs/manual files, inspection summary, manual command/results, unresolved risks, and ledger note/no-material-decision statement.

#### 具体テストケース一覧

- `tc-s90-001` docs inspection: reference docs define lifecycle vs disposition
  - 前提: S01-S04 implementation is complete and reference docs are ready to update.
  - 操作: inspect provider and dogfooding reference docs after edits.
  - 期待結果: docs define `lifecycle_state`, `dependency_disposition`, `disposition_basis`, `deps-issues.*`, and `deps-raw.puml` authority.
  - 失敗検出: operators cannot tell GitHub lifecycle from dependency readiness or raw view from readiness authority.
  - 検証方法: doc-writer summary plus spec-reviewer inspection.
  - 関連 closure id: `cl-016`

- `tc-s90-002` manual: realistic sync/deps/PUML evidence matches runtime
  - 前提: manual fixture contains the realistic mixed dependency state from S04.
  - 操作: run manual sync/deps check/PUML generation commands defined by the manual test environment.
  - 期待結果: observed JSON and PUML match the implemented lifecycle/disposition behavior.
  - 失敗検出: docs and automated tests pass but manual realistic fixture shows mismatch.
  - 検証方法: command/result/file-path observations recorded in `report.md`.
  - 関連 closure id: `cl-017`

- step closure contract:
  - Close S90 only after docs/manual evidence is recorded and spec-reviewer passes docs/spec alignment.
- report evidence destination:
  - `Docs Impact Resolution`, `実装記録`, `Step Contract Closure`, `Test Contract Closure`, `Reviewer Gate Status`, `Step Commit Gate`.
- step gate:
  - spec-reviewer `review_status: pass`, then commit S90 only.
- amendment trigger:
  - docs impact expands into workflow lifecycle policy.

### S99 — Final Quality Gate
- behavior goal:
  - issue-wide quality gates pass after all implementation steps.
- planned contract:
  - scope: final verification and report completion only.
  - allowed paths:
    - `spec-dock/active/issue/report.md`
    - bounded repair paths only if a final reviewer routes work back to a specific prior step.
  - forbidden changes: new runtime/docs changes without returning to the relevant step and fresh reviewer gate.
  - test obligation: `cl-018`, `cl-019`, `cl-020`.
  - red or alternative evidence requirement: final gate uses existing step red/green evidence plus integrated regression commands; no new red test is expected unless a final reviewer finds a gap.
  - green verification:
    - `uv run pytest tests/unit/domain/test_deps.py`
    - `uv run pytest tests/unit/application/test_check_deps.py tests/unit/application/test_set_active.py`
    - `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/unit/presentation/test_deps_raw_puml.py`
    - `uv run pytest tests/cli_runtime/test_deps.py tests/cli_runtime/test_sync.py tests/cli_runtime/test_issue_lifecycle.py`
    - `./spec-dock/scripts/spec-dock validate`
    - `./spec-dock/scripts/spec-dock sync`
  - refactor guardrail: only final report completion and reviewer-routed bounded repairs are allowed.
- delegation contract:
  - delegated roles: qa-reviewer, code-reviewer, spec-reviewer.
  - input docs: `requirement.md`, `design.md`, `plan.md`, final `report.md`, all step commits, changed files, and verification output.
  - allowed paths: read-only review by reviewers; parent may update `report.md` with observed reviewer evidence.
  - forbidden changes: reviewer file edits, new implementation outside a returned prior step, claiming waived/provisional review as pass.
  - acceptance criteria: final regression lane passes, `validate`/`sync` pass, QA/code/spec reviewers return `review_status: pass`.
  - required tests or docs-only verification: S99 green verification commands and reviewer results.
  - reviewer focus: QA coverage sufficiency, integrated code correctness, and full AC/EC/spec closure.
  - stop conditions: any command failure caused by this issue, unresolved blocking ledger entry, reviewer fail, stale reviewer result.
  - output required: reviewer findings/status, final commands/results, closure coverage, unresolved risk summary.

#### 具体テストケース一覧

- `tc-s99-001` regression: focused issue test lane passes
  - 前提: S01-S04 and S90 commits are present.
  - 操作: run the focused domain/application/presentation/CLI pytest commands listed in S99 green verification.
  - 期待結果: all focused regression commands pass.
  - 失敗検出: integration regression appears only after multiple steps are combined.
  - 検証方法: command outputs recorded in `report.md`.
  - 関連 closure id: `cl-018`

- `tc-s99-002` regression: repo-local validate and sync pass
  - 前提: runtime and dogfooding docs/artifacts are updated.
  - 操作: run `./spec-dock/scripts/spec-dock validate` and `./spec-dock/scripts/spec-dock sync`.
  - 期待結果: validation and sync complete without dirty invalid state attributable to this issue.
  - 失敗検出: implementation breaks dogfooding repo invariants or generated artifacts.
  - 検証方法: command outputs and post-command status recorded in `report.md`.
  - 関連 closure id: `cl-019`

- `tc-s99-003` review: final QA/code/spec reviewers pass
  - 前提: final diff and report evidence are ready.
  - 操作: request qa-reviewer, issue-wide code-reviewer, and final spec-reviewer.
  - 期待結果: each reviewer returns `review_status: pass`.
  - 失敗検出: implementation is merged to closeout without independent final coverage/correctness/spec checks.
  - 検証方法: reviewer outputs summarized in `report.md`.
  - 関連 closure id: `cl-020`

- step closure contract:
  - Close S99 only after all closure rows are pass/approved-no-op, no blocking ledger entries remain, and final reviewer triad passes.
- report evidence destination:
  - `Final Quality Gate`, `Closure Coverage`, `Closure Delta`, `Reviewer Gate Status`, `Step Commit Gate`.
- closure:
  - final report contains all closure evidence and no unresolved blocking ledger entries.

## レビュー / QA ゲート方針
- Per-step:
  - S01-S04: code-reviewer `review_status: pass`.
  - S90: spec-reviewer `review_status: pass`.
- Final:
  - qa-reviewer pass.
  - issue-wide code-reviewer pass.
  - final spec-reviewer pass.
- Missing, stale, failed, unavailable, denied, waived, or provisional reviewer result is not a pass.

## 実行ルール（全ステップ共通）
- One behavior slice, one reviewer gate, one commit per implementation step.
- Do not use final review as a substitute for per-step review.
- Record observed results, discovered tests, reviewer results, and commit/no-op evidence in `report.md`.
- Each step gate includes report update before closure, reviewer pass, commit gate, and no-op gate.
- If a step becomes an approved no-op, record no-op rationale, checked contracts/files, diff-clean command, read-only confirmation, and reviewer pass in `report.md` before closing that step.
- If implementation changes a locked expectation, allowed path boundary, schema compatibility policy, or command behavior not covered here, stop for plan amendment and fresh spec review.

## ドキュメント影響
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
  - `deps-issues.*` is readiness / blocker authority.
  - `deps-raw.puml` is active raw direct visual/debug output, not complete audit or readiness authority.

## Rollback / Compatibility
- Rollback:
  - Revert the relevant step commit and rerun `./spec-dock/scripts/spec-dock sync`.
- Compatibility:
  - Keep `.meta.json.depends_on` unchanged.
  - Keep `deps add/remove` syntax and storage mutation contract unchanged.
  - Keep `.agent/deps-issues.json` `schema_version: 2`.
  - Keep complete raw audit outside `deps-raw.puml`; point to `.meta.json.depends_on` and `.agent/index-all.json`.

## Plan Blockers
- none

## Final Exit Contract
- All AC / EC rows in the Spec-Locked Closure Index have pass or approved-no-op evidence in `report.md`.
- S01-S04 and S90 each have report evidence, fresh reviewer pass, and step commit/no-op closure.
- S99 focused regression commands, `validate`, and `sync` pass or any failure is documented as unrelated with evidence.
- Final qa-reviewer, issue-wide code-reviewer, and final spec-reviewer all return `review_status: pass`.
- `report.md` has no unresolved blocking ledger entries and records execution handoff / closeout readiness.
