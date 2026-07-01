---
種別: 実装計画書（Issue）
ID: "iss-00266"
タイトル: "Delegated authoring artifacts boundary"
Issue Grade: "standard"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00266 Delegated authoring artifacts boundary — 実装計画

## この計画で満たす要件ID
- AC-266-001: diff guard は exactly one new direct-child Markdown under target `artifacts/` を許可する。
- AC-266-002: forbidden paths / side effects / existing updates / canonical docs writes は fail-closed になる。
- AC-266-003: created_by_role, scope_id, source_paths, intended_targets, adoption_status, reflected_to, diff_guard_result が validation される。
- AC-266-004: future delegated output to `discussions/` は compliant output として採用されない。
- AC-266-005: report ledger は artifacts draft adoption / rejection / diff guard result を記録できる。

## 依存関係から導く実装順序
1. S00 plan readiness and specialist evidence。
2. S01 artifact target boundary。
3. S02 forbidden side effects and baseline guard。
4. S03 provenance validation and CLI compatibility。
5. S04 report evidence guidance。
6. S90 docs impact resolution。
7. S99 final quality gate, issue finish, and commit。

## ステップ一覧
- S00: Plan readiness and specialist evidence。
- S01: Artifact target boundary。
- S02: Forbidden side effects and baseline guard。
- S03: Provenance validation and CLI compatibility。
- S04: Report evidence guidance。
- S90: Docs impact resolution。
- S99: Final quality gate, issue finish, and commit。

## 要件 ↔ ステップ対応
- AC-266-001: S01, S99。
- AC-266-002: S01, S02, S03, S99。
- AC-266-003: S03, S99。
- AC-266-004: S01, S02, S03, S99。
- AC-266-005: S04, S90, S99。

## 仕様固定クロージャ索引
| Closure ID | Requirement | Design | Locked expectation | Evidence |
|---|---|---|---|---|
| CLOS-266-001 | AC-266-001 | DES-266-001 | exactly one new direct-child Markdown artifact under target `artifacts/` passes diff guard | domain / CLI positive test |
| CLOS-266-002 | AC-266-001 | DES-266-002 | zero artifact output fails with artifact count diagnostic | negative test |
| CLOS-266-003 | AC-266-001 | DES-266-002 | multiple artifact outputs fail with artifact count diagnostic | negative test |
| CLOS-266-004 | AC-266-001, AC-266-002 | DES-266-003 | malformed artifact filename / `rules.md` / non-md output fails | filename negative tests |
| CLOS-266-005 | AC-266-002 | DES-266-004 | nested artifact path and artifact symlink fail | boundary negative tests |
| CLOS-266-006 | AC-266-002 | DES-266-004, DES-266-010 | existing artifact update, delete, rename/copy, mixed staged/unstaged, unmerged fail | status classifier tests |
| CLOS-266-007 | AC-266-002 | DES-266-005 | canonical docs, source/tests, agent tooling, `.env*`, and forbidden roots fail-closed | forbidden side-effect tests |
| CLOS-266-008 | AC-266-003 | DES-266-006 | missing required provenance fields fail | metadata negative tests |
| CLOS-266-009 | AC-266-003 | DES-266-006 | role/scope mismatch fails | metadata negative tests |
| CLOS-266-010 | AC-266-003 | DES-266-006 | self-claimed adoption/authority/reflection fails | metadata negative tests |
| CLOS-266-011 | AC-266-004 | DES-266-007, DES-266-008 | future output to `discussions/` fails and legacy discussions are not migrated | discussion-output negative test / inspection |
| CLOS-266-012 | AC-266-002, AC-266-004 | DES-266-009, DES-266-011 | baseline status and deprecated `--allow-existing-discussion` do not widen artifact boundary | CLI/application tests |
| CLOS-266-013 | AC-266-005 | DES-266-012 | report guidance records artifact draft path, adoption/rejection, and diff guard result | docs/template inspection |

## 実装ステップ

## S00 Plan Readiness
- Owner: main orchestrator。
- Allowed edits: issue-level `design.md`, `plan.md`, `report.md`。
- Activities:
  - Confirm active issue and guidance state。
  - Inspect existing delegated authoring runtime, artifact parser, current report scaffold, and focused tests。
  - Integrate `system-architect` and `implementation-planner` evidence into `design.md`, `plan.md`, and `report.md`。
  - Run fresh `spec-reviewer` after design/plan promotion。
- Exit criteria:
  - `design.md` and `plan.md` are approved and substantive。
  - `guidance issue-planning` no longer blocks on `design-not-substantive`。
  - No open decision entry blocks implementation。
- Report evidence destination:
  - Spec Interpretation / Decision Ledger。
  - Evidence Adoption Ledger。
  - Spec Authoring Gate。
  - Grade Specialist Evidence Gate。
- Step gate:
  - Fresh `spec-reviewer` passes before implementation starts。

## S01 Artifact Target Boundary
- Delegation: `dev-coder`。
- Source of truth:
  - `requirement.md`
  - `design.md` DES-266-001, DES-266-002, DES-266-003, DES-266-007, DES-266-008
  - `domain/delegated_authoring.py`
  - `domain/artifacts.py`
- Expected implementation:
  - Change target output directory from `scope_dir / "discussions"` to `scope_dir / "artifacts"`。
  - Classify only one new direct-child `.md` artifact as allowed output。
  - Validate filenames through `parse_artifact_filename()`。
  - Reject `rules.md`, malformed artifact-intent names, nested outputs, non-md outputs, and symlinks。
  - Treat future `discussions/` writes as noncompliant, not as adoptable drafts。
- Forbidden changes:
  - Do not edit artifact filename grammar。
  - Do not move or rename legacy `discussions/` files。
  - Do not implement general `new artifact` creation。
- Red / characterization evidence:
  - Existing discussion-positive tests should fail or be replaced because discussion output is no longer compliant。
- Green evidence:
  - CLOS-266-001, CLOS-266-002, CLOS-266-003, CLOS-266-004, CLOS-266-005, and CLOS-266-011 pass。
- Reviewer focus:
  - `code-reviewer` checks boundary strictness and parser reuse。
- Stop conditions:
  - Artifact boundary cannot be implemented without changing artifact grammar or migrating discussions。

## S02 Forbidden Side Effects and Baseline Guard
- Delegation: `dev-coder`。
- Source of truth:
  - `design.md` DES-266-004, DES-266-005, DES-266-009, DES-266-010
  - `application/delegated_authoring.py`
  - existing forbidden root / ignored side-effect tests。
- Expected implementation:
  - Preserve repo-outside baseline status requirement。
  - Preserve HEAD mismatch `committed_side_effect` behavior。
  - Move target dirty baseline semantics from discussion subtree to artifact subtree。
  - Ensure canonical docs, provider source, tests, `.agents`, `.codex`, `.github`, `.env*`, and forbidden roots fail when changed after baseline。
  - Keep unbounded cache ignores such as `.venv/` as existing policy allows。
- Green evidence:
  - CLOS-266-006, CLOS-266-007, CLOS-266-012 relevant baseline tests pass。
- Reviewer focus:
  - `code-reviewer` checks no side-effect permission widened。
  - `qa-reviewer` checks negative-path coverage。
- Stop conditions:
  - Baseline guard requires permitting existing artifact updates。
  - Legacy discussions presence alone becomes blocking。

## S03 Provenance Validation and CLI Compatibility
- Delegation: `dev-coder`。
- Source of truth:
  - `design.md` DES-266-006, DES-266-011
  - `commands/delegated_authoring.py`
  - domain metadata validator。
- Expected implementation:
  - Preserve required provenance fields and supported roles。
  - Validate role/scope consistency and non-empty list fields。
  - Reject self-claims: accepted authority, adopted/integrated/rejected/superseded/blocked/stale adoption status, non-empty `reflected_to`, reviewer pass, readiness/completion claims。
  - Keep `diff_guard_result` required for delegated draft evidence。
  - Keep `--allow-existing-discussion` parser compatibility if needed, but do not let it permit discussions output or existing updates。
  - Do not add `--allow-existing-artifact` in this Issue unless a focused failing test proves the CLI cannot otherwise preserve existing behavior; if added, it still must not allow existing updates.
- Green evidence:
  - CLOS-266-008, CLOS-266-009, CLOS-266-010, and CLOS-266-012 pass。
- Reviewer focus:
  - `code-reviewer` checks diagnostics and backwards-compatible CLI shape。
  - `qa-reviewer` checks metadata negative tests。
- Stop conditions:
  - A compatibility shortcut would make existing updates, discussion output, or self-claimed adoption pass。

## S04 Report Evidence Guidance
- Delegation: `doc-writer` for provider-side docs/templates; `dev-coder` may update tests that assert scaffold text。
- Source of truth:
  - `design.md` DES-266-012
  - `report.md` Delegated Draft Evidence / Evidence Adoption Ledger
  - provider report templates。
- Expected implementation:
  - Update report template guidance so delegated draft evidence standard path is `artifacts/` direct child。
  - Use `artifact draft path` as the future label。
  - Keep legacy `discussions/` only as historical evidence wording。
  - Defer broad workflow docs / skills overhaul to `iss-00267`; record any intentionally stale old guidance in report S90。
- Green evidence:
  - CLOS-266-013 docs/template inspection passes。
  - If scaffold tests cover report templates, focused assertions pass。
- Reviewer focus:
  - `spec-reviewer` checks docs/defer boundary。
- Stop conditions:
  - Report guidance update requires broad skills rewrite or migration of legacy discussions。

## S90 Docs Impact Resolution
- Owner: main orchestrator with `doc-writer` evidence if docs/templates were changed。
- Activities:
  - Confirm whether provider report templates / active-none report scaffolds were updated in S04。
  - Record old `workflow_*` / skills references deferred to `iss-00267` if not changed。
  - Ensure no required Issue 266 report evidence guidance remains contradictory。
- Exit criteria:
  - S04 evidence is recorded。
  - `spec-reviewer` accepts the scope/defer boundary。

## S99 Final Quality Gate
- Owner: main orchestrator。
- Required checks:
  - `uv run pytest tests/unit/domain/test_delegated_authoring.py -q`
  - `uv run pytest tests/cli_runtime/test_delegated_authoring.py -q`
  - `uv run pytest tests/unit/infra/test_init_update.py -k "delegated_authoring or Delegated Draft Evidence or phase_gate_contract_assets" -q` if report/scaffold assertions are touched。
  - `uv run pytest tests/unit tests/cli_runtime -q` if runtime/test blast radius is broader than delegated authoring。
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
- Required reviews:
  - `code-reviewer` pass after runtime/test changes。
  - `qa-reviewer` pass after tests are complete。
  - `spec-reviewer` pass after implementation, report, docs/defer evidence are integrated。
- Completion:
  - Run `./spec-dock/scripts/spec-dock issue finish` only after all blocking gates pass。
  - Commit this Issue's completed diff on the Issue branch。
  - Do not create per-Issue PR; Epic PR is created after the Epic-level quality gate。

## Allowed Files
- Runtime:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/delegated_authoring.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delegated_authoring.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/delegated_authoring.py`
- Tests:
  - `tests/unit/domain/test_delegated_authoring.py`
  - `tests/cli_runtime/test_delegated_authoring.py`
  - focused report/scaffold assertions in `tests/unit/infra/test_init_update.py`
- Provider-side report guidance:
  - `src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/report.md`
  - `src/spec_dock/assets/spec_dock/system/active-none/{initiative,epic,issue}/report.md`
  - narrow delegated draft evidence sections in workflow docs only if required for consistency.
- Issue-level canonical evidence:
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/issues/iss-00266-delegated-authoring-artifacts-boundary/design.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/issues/iss-00266-delegated-authoring-artifacts-boundary/plan.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/issues/iss-00266-delegated-authoring-artifacts-boundary/report.md`

## Forbidden Files / Actions
- Do not move, rename, delete, or auto-migrate existing `discussions/`。
- Do not implement general `new artifact` creation。
- Do not broaden supported roles。
- Do not edit unrelated installer, sync/projection, ADR mirror, validation, package config, or GitHub integration behavior unless a focused failing test proves it is required。
- Do not update `.codex/agents` / `.agents/skills` broadly in this Issue; default defer to `iss-00267`。
- Do not create per-Issue PR。
