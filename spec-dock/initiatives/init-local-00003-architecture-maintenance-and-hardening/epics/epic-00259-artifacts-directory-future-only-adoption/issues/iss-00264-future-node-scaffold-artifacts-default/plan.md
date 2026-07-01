---
種別: 実装計画書（Issue）
ID: "iss-00264"
タイトル: "Future node scaffold artifacts default"
Issue Grade: "standard"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00264 Future node scaffold artifacts default — 実装計画

## この計画で満たす要件ID
- AC-264-001: new initiative / epic / issue scaffold has `artifacts/`.
- AC-264-002: new scaffold does not default-create `discussions/`.
- AC-264-003: `artifacts/rules.md` points to provider-side `docs/rules/<kind>/artifacts.md`.
- AC-264-004: `spec-dock update` preserves existing node-local `discussions/`.
- AC-264-005: old-only layout is not made invalid by this Issue.

## 依存関係から導く実装順序
1. S00 plan readiness and specialist evidence.
2. S01 runtime node scaffold rule-spec switch.
3. S02 scaffold/runtime tests for new node defaults.
4. S03 installer/update compatibility tests.
5. S90 docs impact resolution.
6. S99 final quality gate, issue finish, and commit.

## ステップ一覧
- S00: Plan readiness and specialist evidence.
- S01: Runtime node scaffold rule-spec switch.
- S02: Scaffold/runtime tests for new node defaults.
- S03: Installer/update compatibility tests.
- S90: Docs impact resolution.
- S99: Final quality gate, issue finish, and commit.

## 要件 ↔ ステップ対応
- AC-264-001: S01, S02.
- AC-264-002: S01, S02.
- AC-264-003: S01, S02, S03.
- AC-264-004: S03, S90.
- AC-264-005: S03, S99.

## 仕様固定クロージャ索引
| Closure ID | Requirement | Design | Locked expectation | Evidence destination |
|---|---|---|---|---|
| CLOS-264-001 | AC-264-001, AC-264-003 | DES-264-001 | `new initiative` creates `artifacts/rules.md` -> `docs/rules/initiative/artifacts.md`, and keeps `epics/rules.md` | runtime scaffold test |
| CLOS-264-002 | AC-264-001, AC-264-003 | DES-264-002 | `new epic` creates `artifacts/rules.md` -> `docs/rules/epic/artifacts.md`, and keeps `issues/rules.md` | runtime scaffold test |
| CLOS-264-003 | AC-264-001, AC-264-003 | DES-264-003 | `new issue` creates `artifacts/rules.md` -> `docs/rules/issue/artifacts.md` | runtime scaffold test |
| CLOS-264-004 | AC-264-002 | DES-264-004 | new initiative / epic / issue scaffold does not create `discussions/` by default | absence assertion |
| CLOS-264-005 | AC-264-004 | DES-264-005, DES-264-007 | update and old-node artifact setup preserve existing `discussions/` contents | init/update and regression tests |
| CLOS-264-006 | AC-264-005 | DES-264-006 | old-only / mixed nodes are not invalidated by this Issue | focused validate or unchanged validation evidence |
| CLOS-264-007 | AC-264-003 | DES-264-001..003 | rules sources are preflighted before GitHub issue creation and local write | failure-path or existing preflight test update |
| CLOS-264-008 | AC-264-004 | DES-264-001..005 | `spec-dock update` adds future `docs/rules/{initiative,epic,issue}/artifacts.md` assets to existing workspaces without migrating node-local `discussions/` | init/update asset test |

## 実装ステップ

## S00 Plan Readiness
- Owner: main orchestrator.
- Allowed edits: issue-level `design.md`, `plan.md`, `report.md`.
- Activities:
  - Confirm active issue and current guidance.
  - Inspect `create_node.py`, `create_artifact_doc.py`, provider rules assets, and relevant tests.
  - Record specialist evidence from `system-architect` / `implementation-planner` or manual fallback in `report.md`.
  - Run fresh `spec-reviewer` after plan promotion.
- Exit criteria:
  - `design.md` and `plan.md` are approved and substantive.
  - `guidance issue-planning` is ready or only reports non-blocking warnings.
  - No open decision entry blocks implementation.
- Report evidence destination:
  - Spec Authoring Gate.
  - Evidence Adoption Ledger.
  - Grade Specialist Evidence Gate.
- Step gate:
  - `assurance verify` passes.
  - Fresh `spec-reviewer` passes before implementation starts.

## S01 Runtime Node Scaffold Rule-Spec Switch
- Delegation: `dev-coder`.
- Source of truth:
  - `requirement.md`
  - `design.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
- Expected implementation:
  - Update `_rules_source_paths()` to include `docs/rules/<kind>/artifacts.md` instead of `discussions.md` for node-local artifact rules.
  - Update `_rules_scaffold_specs()` to create `dest_dir / "artifacts" / "rules.md"` instead of `dest_dir / "discussions" / "rules.md"`.
  - Preserve `epics/rules.md` for initiatives and `issues/rules.md` for epics.
  - Keep existing symlink preflight and relative symlink creation helpers.
  - Do not modify `create_artifact_doc.py` unless a test proves an integration defect; if touched, justify in `report.md`.
- Forbidden changes:
  - Do not migrate existing node trees.
  - Do not create or restore `new doc`.
  - Do not change validation/sync/ADR mirror semantics.
- Red evidence:
  - Update or add a test that fails while scaffold still creates `discussions/rules.md` and omits `artifacts/rules.md`.
- Green evidence:
  - New node scaffold tests pass for initiative / epic / issue.
- Closure IDs: CLOS-264-001, CLOS-264-002, CLOS-264-003, CLOS-264-004, CLOS-264-007.

### S01 delegation contract
- delegated role: `dev-coder`.
- input docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - tests listed in S02 if the same worker performs Red/Green implementation.
- forbidden changes:
  - validation/sync/ADR mirror behavior.
  - `create_artifact_doc.py` unless a failing test proves an integration defect.
  - existing node migration or deletion of `discussions/`.
  - `new doc` restoration.
- acceptance criteria:
  - CLOS-264-001, CLOS-264-002, CLOS-264-003, CLOS-264-004, CLOS-264-007.
- required tests or docs-only verification:
  - Red evidence from S02 test update.
  - Green evidence from S02 focused commands.
- reviewer focus:
  - `code-reviewer` checks runtime behavior, failure preflight, and scope containment.
- stop conditions:
  - Any need to migrate/delete existing `discussions/`.
  - Any need to implement validation parity.
  - Any test indicates `new artifact` behavior must be changed beyond old-node preservation.
- output required:
  - changed files.
  - Red/Green commands and results.
  - `Ledger Note` or `No material implementation decisions beyond the approved plan.`
  - unresolved risks.

### S01 具体テストケース一覧
- `tc-s01-001` acceptance: initiative scaffold uses artifact rules.
  - 前提: temp repo initialized with current provider assets and GitHub stubs where needed.
  - 操作: create a new initiative through the runtime command path.
  - 期待結果: created initiative has `artifacts/rules.md` symlink to `spec-dock/docs/rules/initiative/artifacts.md` and still has `epics/rules.md`.
  - 失敗検出: legacy `discussions/rules.md` remains the default or artifact rules are missing.
  - 検証方法: `tests/unit/commands/test_runtime_new_s08.py` planned/executed path assertions and CLI runtime scaffold assertions.
  - 関連 closure id: CLOS-264-001, CLOS-264-004.

- `tc-s01-002` acceptance: epic scaffold uses artifact rules.
  - 前提: temp repo contains an initiative parent.
  - 操作: create a new epic through the runtime command path.
  - 期待結果: created epic has `artifacts/rules.md` symlink to `spec-dock/docs/rules/epic/artifacts.md` and still has `issues/rules.md`.
  - 失敗検出: legacy `discussions/rules.md` remains the default or `issues/rules.md` is lost.
  - 検証方法: `tests/unit/commands/test_runtime_new_s08.py` and CLI runtime scaffold assertions.
  - 関連 closure id: CLOS-264-002, CLOS-264-004.

- `tc-s01-003` acceptance: issue scaffold uses artifact rules.
  - 前提: temp repo contains initiative and epic parents.
  - 操作: create a new issue through the runtime command path.
  - 期待結果: created issue has `artifacts/rules.md` symlink to `spec-dock/docs/rules/issue/artifacts.md`.
  - 失敗検出: legacy `discussions/rules.md` remains the default or artifact rules are missing.
  - 検証方法: `tests/unit/commands/test_runtime_new_s08.py` and CLI runtime scaffold assertions.
  - 関連 closure id: CLOS-264-003, CLOS-264-004.

- `tc-s01-004` negative: missing artifact rules source fails before local write / GitHub creation.
  - 前提: temp repo lacks one of `docs/rules/{initiative,epic,issue}/artifacts.md`.
  - 操作: run the relevant `new` command with a path that would otherwise create a node.
  - 期待結果: command fails with missing rules source before partial local scaffold write and before GitHub creation in create mode.
  - 失敗検出: partial node tree is created or GitHub creation occurs before preflight.
  - 検証方法: existing missing-rules-source test updated to artifact source, or a focused unit command test.
  - 関連 closure id: CLOS-264-007.

### S01 step closure contract
- Close S01 only when CLOS-264-001..004 and CLOS-264-007 have Red/Green or characterization evidence.
- Record actual evidence in `report.md` Step Contract Closure, Test Contract Closure, Closure Coverage, and Closure Delta.
- Amendment trigger: if `create_node.py` cannot satisfy the contract without changing validation/sync or `new artifact`, stop for plan amendment and re-review.

### S01 behavior slice execution
- Red or alternative evidence requirement: red-required for at least one scaffold default test; characterization acceptable for existing planned-path tests updated before implementation.
- Green verification: focused S02 commands pass.
- Refactor guardrail: no helper extraction unless it reduces duplication between source path/spec construction without broadening behavior.

### S01 step gate
- dev-coder worker output is accepted by orchestrator.
- `code-reviewer` pass is required before S03 or S99 closure.

## S02 Scaffold/Runtime Tests
- Delegation: `dev-coder`.
- Likely files:
  - `tests/cli_runtime/test_new.py`
  - `tests/cli_runtime/test_wrappers.py`
  - relevant unit command tests if present for create-plan symlink materialization.
- Required test assertions:
  - `artifacts/rules.md` exists and is a relative symlink to the correct provider rule source for all three node kinds.
  - `discussions/` does not exist immediately after new node creation.
  - child collection rules remain:
    - initiative `epics/rules.md`
    - epic `issues/rules.md`
  - failure-path prechecks use artifact rules source before GitHub creation where the existing test surface covers rules source checks.
- Suggested commands:
  - `uv run pytest tests/cli_runtime/test_new.py -k "rules_symlinks or missing_rules_source or new_artifact_old_node_setup_preserves_discussions"`
  - `uv run pytest tests/cli_runtime/test_wrappers.py -k "rules_symlinks or new_artifact_numbering"`
- Closure IDs: CLOS-264-001..CLOS-264-008 as applicable.

### S02 delegation contract
- delegated role: `dev-coder`.
- input docs:
  - `requirement.md`, `design.md`, `plan.md`.
  - `tests/unit/commands/test_runtime_new_s08.py`
  - `tests/cli_runtime/test_new.py`
  - `tests/cli_runtime/test_wrappers.py`
- allowed paths:
  - `tests/unit/commands/test_runtime_new_s08.py`
  - `tests/cli_runtime/test_new.py`
  - `tests/cli_runtime/test_wrappers.py`
- forbidden changes:
  - Test weakening that merely removes `discussions/` assertions without adding `artifacts/` assertions.
  - Broad fixture rewrites unrelated to node scaffold defaults.
- acceptance criteria:
  - All CLOS-264-* test obligations have explicit test or inspection evidence.
- required tests or docs-only verification:
  - Commands listed in S02.
- reviewer focus:
  - `code-reviewer` and `qa-reviewer` inspect test sensitivity and compatibility coverage.
- stop conditions:
  - Existing test suite shows old-only validation behavior changed outside scope.
  - Tests require non-hermetic GitHub/network access.
- output required:
  - changed tests.
  - failing-before / passing-after evidence.
  - any skipped or replaced test rationale.

### S02 具体テストケース一覧
- `tc-s02-001` acceptance: planned paths include artifact rules and exclude discussion rules.
  - 前提: unit create-plan fixtures for initiative / epic / issue.
  - 操作: compute create plan and inspect planned paths / rules specs.
  - 期待結果: `artifacts/rules.md` is planned; `discussions/rules.md` is not planned.
  - 失敗検出: implementation creates hidden discussion defaults or omits artifact rules from planned collision/preflight coverage.
  - 検証方法: `uv run pytest tests/unit/commands/test_runtime_new_s08.py -k "create_plan or rules or symlink"`.
  - 関連 closure id: CLOS-264-001, CLOS-264-002, CLOS-264-003, CLOS-264-004.

- `tc-s02-002` acceptance: CLI runtime materializes relative artifact rules symlinks.
  - 前提: temp repo initialized by provider installer.
  - 操作: create same-repo linked hierarchy by runtime commands.
  - 期待結果: each node kind has a relative `artifacts/rules.md` symlink to the matching artifacts rules source.
  - 失敗検出: symlink is absolute, points to discussions rules, or is missing.
  - 検証方法: `uv run pytest tests/cli_runtime/test_wrappers.py -k "rules_symlinks"`.
  - 関連 closure id: CLOS-264-001, CLOS-264-002, CLOS-264-003.

- `tc-s02-003` negative: new scaffold does not create `discussions/`.
  - 前提: temp repo with newly created initiative / epic / issue.
  - 操作: inspect each created node directory.
  - 期待結果: `discussions/` does not exist immediately after creation.
  - 失敗検出: any new node contains `discussions/` or `discussions/rules.md` by default.
  - 検証方法: `tests/cli_runtime/test_new.py` or `tests/cli_runtime/test_wrappers.py` absence assertions.
  - 関連 closure id: CLOS-264-004.

### S02 step closure contract
- Close S02 when unit and CLI runtime tests demonstrate planned-path and materialized-path behavior.
- Record evidence in `report.md` Test Contract Closure and Closure Coverage.
- Amendment trigger: if existing wrappers are deprecated/skipped and cannot provide live coverage, add a focused non-skipped test before implementation proceeds.

### S02 behavior slice execution
- Red or alternative evidence requirement: red-required for modified scaffold expectation tests.
- Green verification: S02 focused commands pass.
- Refactor guardrail: keep fixture changes minimal and local to scaffold expectations.

### S02 step gate
- Test changes must be reviewed as behavior-preserving sensitivity improvements, not snapshot churn.

## S03 Installer / Update Compatibility
- Delegation: `dev-coder`.
- Likely files:
  - `tests/unit/infra/test_init_update.py`
  - `src/spec_dock/cli.py` only if tests reveal prune/update behavior conflicts with future artifact assets.
- Required behavior:
  - `spec-dock init` ships provider rules/docs/templates needed for `artifacts/rules.md`.
  - `spec-dock update` adds provider-side `docs/rules/{initiative,epic,issue}/artifacts.md` assets to existing workspaces that predate this future scaffold default.
  - `spec-dock update` preserves existing node-local legacy `discussions/` contents.
  - Managed legacy template artifacts may still be pruned according to existing installer policy; node-local legacy user artifacts must not be pruned.
- Suggested commands:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "legacy_artifacts_inside_existing_node_trees or artifact"`
  - `uv run pytest tests/unit/infra`
- Closure IDs: CLOS-264-005, CLOS-264-006, CLOS-264-008.

### S03 delegation contract
- delegated role: `dev-coder`.
- input docs:
  - `requirement.md`, `design.md`, `plan.md`.
  - `tests/unit/infra/test_init_update.py`
  - `src/spec_dock/cli.py` only for inspection or minimal fix if test proves a conflict.
- allowed paths:
  - `tests/unit/infra/test_init_update.py`
  - `src/spec_dock/cli.py` only with explicit report decision entry.
- forbidden changes:
  - Installer code changes that prune `spec-dock/initiatives/**` node-local user content.
  - Migration of existing node-local `discussions/`.
  - Broad installer asset policy rewrites.
- acceptance criteria:
  - CLOS-264-005, CLOS-264-006, and CLOS-264-008.
- required tests or docs-only verification:
  - S03 focused command.
  - `validate` smoke if old-only fixture is materialized.
- reviewer focus:
  - `code-reviewer` reviews installer/update safety.
  - `qa-reviewer` reviews compatibility coverage.
- stop conditions:
  - Any update path wants to delete existing node-local `discussions/`.
  - Old-only valid cannot be demonstrated without implementing `iss-00265` scope.
- output required:
  - compatibility test evidence.
  - no-migration confirmation.
  - `Ledger Note` if installer behavior needs interpretation.

### S03 具体テストケース一覧
- `tc-s03-001` compatibility: update preserves node-local legacy discussions.
  - 前提: temp target repo contains existing node-local `discussions/rules.md` and at least one legacy discussion Markdown file.
  - 操作: run `spec-dock update` from current provider checkout.
  - 期待結果: node-local legacy files remain with identical content and path.
  - 失敗検出: update removes, rewrites, renames, or relinks node-local legacy discussions.
  - 検証方法: `uv run pytest tests/unit/infra/test_init_update.py -k "legacy_artifacts_inside_existing_node_trees or artifact"`.
  - 関連 closure id: CLOS-264-005.

- `tc-s03-002` compatibility: old-only layout is not invalidated by this Issue.
  - 前提: old-only node fixture without `artifacts/` and with legacy `discussions/`.
  - 操作: run focused validate or existing validation regression.
  - 期待結果: absence of `artifacts/` alone does not produce invalid status.
  - 失敗検出: this Issue introduces a required-artifacts validation failure before `iss-00265`.
  - 検証方法: focused validation test or unchanged validation evidence recorded in `report.md`.
  - 関連 closure id: CLOS-264-006.

- `tc-s03-003` compatibility: update adds future artifact rules assets.
  - 前提: existing target workspace was initialized before artifact rules were available, or a temp target has those future rules assets removed to model the old install.
  - 操作: run `spec-dock update` from the current provider checkout.
  - 期待結果: `spec-dock/docs/rules/initiative/artifacts.md`, `spec-dock/docs/rules/epic/artifacts.md`, and `spec-dock/docs/rules/issue/artifacts.md` are present after update while node-local `discussions/` files remain untouched.
  - 失敗検出: existing workspaces remain unable to create `artifacts/rules.md` because update did not install future rules sources.
  - 検証方法: `uv run pytest tests/unit/infra/test_init_update.py -k "artifact or discussion or scaffold"`.
  - 関連 closure id: CLOS-264-008.

### S03 step closure contract
- Close S03 only when update asset addition, update preservation, and old-only non-invalidation evidence are recorded.
- Record evidence in `report.md` Step Contract Closure, Test Contract Closure, and Closure Coverage.
- Amendment trigger: if old-only validity requires new validation rules, stop and move that work to `iss-00265` or amend scope.

### S03 behavior slice execution
- Red or alternative evidence requirement: covered-existing is acceptable for update preservation if existing test already fails on deletion; otherwise red-required.
- Green verification: S03 focused command passes.
- Refactor guardrail: no installer refactor beyond the minimum needed for artifact asset preservation.

### S03 step gate
- `code-reviewer` and `qa-reviewer` pass required before final close.

## S90 Docs Impact Resolution
- Delegation: `doc-writer` only if persistent non-issue docs require updates.
- Expected classification:
  - Runtime behavior change may require test/document updates for scaffold expectations.
  - Broader workflow/skill guidance remains assigned to `iss-00267`.
- Required decision:
  - If shipped docs directly promise new node `discussions/` defaults, update them in this Issue.
  - If docs are broad `new artifact` / workflow guidance, record handoff to `iss-00267`.
- Closure IDs: CLOS-264-004, CLOS-264-005.

### S90 delegation contract
- delegated role: `doc-writer` if shipped docs need updates; otherwise main orchestrator records approved-no-op.
- input docs:
  - `design.md`
  - `plan.md`
  - shipped docs identified by `rg "discussions/rules.md|new node|new initiative|new epic|new issue" src/spec_dock/assets/spec_dock`.
- allowed paths:
  - shipped docs/templates that directly describe node scaffold defaults.
- forbidden changes:
  - Broad workflow/skill alignment assigned to `iss-00267`.
  - Runtime/code/test edits.
- acceptance criteria:
  - No shipped doc directly contradicts new node `artifacts/` default.
- required tests or docs-only verification:
  - `rg` inspection and, if docs changed, focused docs/spec review.
- reviewer focus:
  - `spec-reviewer` docs/spec alignment.
- stop conditions:
  - Documentation change would alter delegated authoring policy or validation behavior.
- output required:
  - changed docs or approved-no-op rationale.

### S90 具体テストケース一覧
- `tc-s90-001` inspect-only: shipped docs do not promise new node discussion defaults.
  - 前提: implementation diff is available.
  - 操作: search shipped docs/templates for node scaffold default references.
  - 期待結果: no direct contradiction remains, or required docs are updated in this Issue.
  - 失敗検出: docs still instruct that new nodes default-create `discussions/`.
  - 検証方法: `rg -n "discussions/rules.md|artifacts/rules.md|new initiative|new epic|new issue" src/spec_dock/assets/spec_dock`.
  - 関連 closure id: CLOS-264-004, CLOS-264-005.

### S90 step closure contract
- Close S90 with either docs changes plus review, or approved-no-op evidence that broader docs are owned by `iss-00267`.
- Report destination: Docs Impact Resolution table and Closure Coverage.

### S90 behavior slice execution
- Red or alternative evidence requirement: inspect-only.
- Green verification: docs inspection has no blocking contradiction.
- Refactor guardrail: no opportunistic wording cleanup.

### S90 step gate
- `spec-reviewer` must accept docs impact disposition before issue finish.

## S99 Final Quality Gate
- Delegation:
  - `code-reviewer` after implementation.
  - `qa-reviewer` for scaffold/update coverage and regression sufficiency.
  - `spec-reviewer` for final traceability.
- Required commands:
  - focused test commands from S02/S03.
  - `uv run pytest tests/cli_runtime`
  - `uv run pytest tests/unit/infra`
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
- Completion conditions:
  - All CLOS-264-* entries have pass evidence or documented approved no-op evidence.
  - Final reviewers pass.
  - `issue finish iss-00264` succeeds.
  - Commit is created on the issue branch.
  - No per-Issue PR is opened; Epic PR is created only after the final Epic quality gate.

## レビュー / エスカレーション
- User clarification is required only if implementation discovers that stopping default `discussions/` creation would break an explicitly accepted workflow that cannot be preserved by legacy compatibility.
- A follow-up Issue is preferred over scope expansion for validation/sync/projection/delegated authoring changes.
- Any discovered need to delete or migrate existing `discussions/` is out of scope and must block for user decision.

### S99 具体テストケース一覧
- `tc-s99-001` final verification: focused and broad lanes pass.
  - 前提: S01-S90 changes are complete and reviewed.
  - 操作: run required commands listed in S99.
  - 期待結果: all commands pass or any failure is proven unrelated and recorded.
  - 失敗検出: scaffold/update regression, stale SpecDock projection, or formatting issue.
  - 検証方法: S99 command list and reviewer gates.
  - 関連 closure id: CLOS-264-001..CLOS-264-008.

### S99 step closure contract
- Close S99 only when all closure IDs have evidence, final reviewers pass, `issue finish` succeeds, and commit is created.
- Report destination: Final Quality Gate, Reviewer Gate Status, Milestone / Commit Candidate Gate.

### S99 behavior slice execution
- Red or alternative evidence requirement: covered by S01-S03; final step is verification-only.
- Green verification: all final commands pass.
- Refactor guardrail: no new functional edits after final reviewer pass except reviewer-requested fixes.

### S99 step gate
- Required fresh passes: `code-reviewer`, `qa-reviewer`, `spec-reviewer`.
- No unresolved report decision, stale delegated evidence, or open closure delta remains.

## Final Exit Contract
- `design.md`, `plan.md`, and `report.md` reflect the implemented behavior and evidence.
- `assurance verify` passes.
- `guidance issue-execution` permits execution or finish at the relevant phase.
- `./spec-dock/scripts/spec-dock validate` passes.
- `issue finish iss-00264` closes the Issue and clears active issue if appropriate.
- A focused Japanese Conventional Commit is created.
- No per-Issue PR is opened.
