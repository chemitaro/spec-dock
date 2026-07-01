---
種別: 実装計画書（Issue）
ID: "iss-00265"
タイトル: "Validation sync ADR mirror and agent projection"
Issue Grade: "standard"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00265 Validation sync ADR mirror and agent projection — 実装計画

## この計画で満たす要件ID
- AC-265-001: old-only / new-only / mixed layout validation pass。
- AC-265-002: malformed artifact-intent filename and duplicate artifact id fail as artifact diagnostics。
- AC-265-003: malformed / duplicate legacy discussion validation remains strict。
- AC-265-004: ADR mirror collects both legacy `discussions/` ADR and future `artifacts/` ADR without moving originals。
- AC-265-005: sync / `.agent` output distinguishes canonical docs / artifacts / discussions。

## 依存関係から導く実装順序
1. S00 plan readiness and specialist evidence。
2. S01 artifact validation connection。
3. S02 validation diagnostics and layout fixtures。
4. S03 ADR mirror mixed-source discovery。
5. S04 sync / `.agent` projection labels。
6. S90 docs impact resolution。
7. S99 final quality gate, issue finish, and commit。

## ステップ一覧
- S00: Plan readiness and specialist evidence。
- S01: Artifact validation connection。
- S02: Validation diagnostics and layout fixtures。
- S03: ADR mirror mixed-source discovery。
- S04: Sync / `.agent` projection labels。
- S90: Docs impact resolution。
- S99: Final quality gate, issue finish, and commit。

## 要件 ↔ ステップ対応
- AC-265-001: S01, S02, S99。
- AC-265-002: S01, S02。
- AC-265-003: S02。
- AC-265-004: S03。
- AC-265-005: S04。

## 仕様固定クロージャ索引
| Closure ID | Requirement | Design | Locked expectation | Evidence |
|---|---|---|---|---|
| CLOS-265-001 | AC-265-001 | DES-265-001 | old-only layout with `discussions/` and no `artifacts/` validates | validation test |
| CLOS-265-002 | AC-265-001 | DES-265-001, DES-265-003 | new-only layout with `artifacts/` and no `discussions/` validates | validation test |
| CLOS-265-003 | AC-265-001 | DES-265-001..003 | mixed layout with both surfaces validates | validation test |
| CLOS-265-004 | AC-265-002 | DES-265-003, DES-265-004 | malformed artifact-intent filename fails with artifact diagnostic | validation negative test |
| CLOS-265-005 | AC-265-002 | DES-265-003, DES-265-004 | duplicate artifact id / timestamp slot fails with artifact diagnostic | validation negative test |
| CLOS-265-006 | AC-265-003 | DES-265-002, DES-265-004 | malformed / duplicate legacy discussion still fails with discussion diagnostic | validation negative test |
| CLOS-265-007 | AC-265-004 | DES-265-005, DES-265-006 | legacy discussion ADR source is mirrored and original remains | ADR mirror test |
| CLOS-265-008 | AC-265-004 | DES-265-005, DES-265-006 | future artifact ADR source is mirrored and original remains | ADR mirror test |
| CLOS-265-009 | AC-265-004 | DES-265-007 | mixed-source basename collision fails before mirror write | ADR mirror negative test |
| CLOS-265-010 | AC-265-005 | DES-265-008, DES-265-010 | projection labels canonical docs / future artifacts / legacy discussions separately | sync projection test |
| CLOS-265-011 | AC-265-005 | DES-265-009 | projection addition does not widen raw dependency exposure or remove existing keys | sync schema regression |

## 実装ステップ

## S00 Plan Readiness
- Owner: main orchestrator。
- Allowed edits: issue-level `design.md`, `plan.md`, `report.md`。
- Activities:
  - Confirm active issue and guidance state。
  - Inspect validation, artifact parser, sync ADR mirror, JSON projection, and focused tests。
  - Record `system-architect` and `implementation-planner` evidence in `report.md`。
  - Run fresh `spec-reviewer` after design/plan promotion。
- Exit criteria:
  - `design.md` and `plan.md` are approved and substantive。
  - `guidance issue-planning` permits execution or only reports non-blocking warnings。
  - No open decision entry blocks implementation。
- Report evidence destination:
  - Spec Authoring Gate。
  - Evidence Adoption Ledger。
  - Grade Specialist Evidence Gate。
- Step gate:
  - `assurance verify` passes。
  - Fresh `spec-reviewer` passes before implementation starts。

## S01 Artifact Validation Connection
- Delegation: `dev-coder`。
- Source of truth:
  - `requirement.md`
  - `design.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifacts.py`
- Expected implementation:
  - Add `_validate_artifact_filenames(graph, repo_root=repo_root)` or equivalent narrow helper in `domain/validation.py`。
  - Iterate every graph scope that has an `artifacts/` directory。
  - Use `scan_artifact_duplicate_state(artifacts_dir)` for malformed / duplicate detection。
  - Call artifact validation after existing discussion validation in graph validation。
  - Treat absent `artifacts/` as valid。
- Forbidden changes:
  - Do not weaken `_validate_discussion_filenames()`。
  - Do not alter artifact filename grammar。
  - Do not change node creation or `new artifact` command behavior。
- Red / characterization evidence:
  - A malformed artifact file under an existing node's `artifacts/` must fail after implementation; before S01 it is expected to be missed by `validate` unless already covered by another path。
- Green evidence:
  - CLOS-265-001..005 validation tests pass。
- Reviewer focus:
  - `code-reviewer` checks layering, diagnostics separation, and scope containment。
- Stop conditions:
  - Artifact validation requires changing artifact filename grammar。
  - Validation cannot be added without migrating existing nodes。

## S02 Validation Diagnostics and Layout Fixtures
- Delegation: `dev-coder` may combine with S01。
- Source of truth:
  - `requirement.md`
  - `design.md`
  - focused validation tests under `tests/cli_runtime/` or existing unit lanes。
- Test cases:
  - `tc-s02-001` old-only layout validates。
    - Fixture: node with canonical docs and `discussions/`, no `artifacts/`。
    - Closure: CLOS-265-001。
  - `tc-s02-002` new-only layout validates。
    - Fixture: node with canonical docs and `artifacts/`, no `discussions/`。
    - Closure: CLOS-265-002。
  - `tc-s02-003` mixed layout validates。
    - Fixture: node with both surfaces。
    - Closure: CLOS-265-003。
  - `tc-s02-004` malformed artifact-intent filename fails as artifact diagnostic。
    - Expected diagnostic contains `Malformed artifact filename` or an equivalent artifact-specific message from `artifacts.py`。
    - Closure: CLOS-265-004。
  - `tc-s02-005` duplicate artifact id / timestamp slot fails as artifact diagnostic。
    - Expected diagnostic contains `Duplicate artifact`。
    - Closure: CLOS-265-005。
  - `tc-s02-006` malformed / duplicate discussion still fails as discussion diagnostic。
    - Expected diagnostic remains discussion-specific and is not reclassified as artifact。
    - Closure: CLOS-265-006。
- Suggested focused command:
  - `uv run pytest tests/cli_runtime/test_validate.py -q`
- Stop conditions:
  - Test setup requires changing production scaffold defaults beyond `iss-00264` contract。
  - Discussion strictness becomes weaker than the pre-existing behavior。

## S03 ADR Mirror Mixed-Source Discovery
- Delegation: `dev-coder`。
- Source of truth:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - existing ADR mirror tests in `tests/unit/presentation/test_runtime_sync_s07.py`
- Expected implementation:
  - Extend ADR source discovery to scan both `scope.path / "discussions"` and `scope.path / "artifacts"`。
  - Reuse discussion filename parser for legacy discussion ADRs。
  - Use artifact filename parser for future artifact ADRs and accept only `adr` artifact type。
  - Preserve existing front matter / parent scope matching semantics。
  - Keep `_preflight_adr_mirror_sources()` and `_rebuild_adr_mirror()` writer behavior intact unless tests reveal a direct integration bug。
- Test cases:
  - `tc-s03-001` legacy discussion ADR is mirrored and original remains。
    - Closure: CLOS-265-007。
  - `tc-s03-002` future artifact ADR is mirrored and original remains。
    - Closure: CLOS-265-008。
  - `tc-s03-003` mixed-source basename collision fails before mirror write。
    - Closure: CLOS-265-009。
- Suggested focused command:
  - `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py -k "adr_mirror" -q`
- Stop conditions:
  - Any implementation moves, rewrites, or renames ADR originals。
  - Mirror source collection requires accepting invalid artifact filenames。

## S04 Sync / `.agent` Projection Labels
- Delegation: `dev-coder`。
- Source of truth:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - sync projection tests。
- Expected implementation:
  - Add `document_surfaces` to node payloads。
  - Emit `canonical_docs`, `future_artifacts`, and `legacy_discussions` as distinct labels。
  - Include path and presence information only; do not make this field a validation authority。
  - Preserve existing payload keys and current full-history / current-future boundary。
  - Do not add raw `depends_on` to projections that currently omit it。
- Test cases:
  - `tc-s04-001` sync JSON has separate labels for canonical docs, future artifacts, legacy discussions。
    - Closure: CLOS-265-010。
  - `tc-s04-002` canonical docs are not labeled as artifacts。
    - Closure: CLOS-265-010。
  - `tc-s04-003` existing dependency projection boundary is unchanged。
    - Closure: CLOS-265-011。
- Suggested focused command:
  - `uv run pytest tests/cli_runtime/test_sync.py -q`
  - Add a focused unit/presentation assertion if CLI setup is too broad。
- Stop conditions:
  - Projection change requires renaming or removing existing public keys。
  - Projection starts treating `artifacts/` as canonical docs。

## S90 Docs Impact Resolution
- Owner: main orchestrator with `doc-writer` only if necessary。
- Expected handling:
  - Record diagnostics/schema changes in `report.md`。
  - Do not rewrite shipped workflow docs / skills in this Issue unless implementation reveals a hard inconsistency that blocks validation。
  - Planned broader docs/skills alignment remains in `iss-00267`。
- Exit criteria:
  - `report.md` states whether docs/skills updates are deferred to `iss-00267` or no-op。
  - Any changed projection schema name is traceable from design/plan/report。

## S99 Final Quality Gate
- Required focused tests:
  - `uv run pytest tests/cli_runtime/test_validate.py -q`
  - `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py -k "adr_mirror or projection or index" -q`
  - `uv run pytest tests/cli_runtime/test_sync.py -q`
- Broader tests:
  - `uv run pytest tests/cli_runtime -q`
  - `./spec-dock/scripts/spec-dock validate`
- Reviewer gates:
  - `code-reviewer`: S01-S04 implementation diff and compatibility。
  - `qa-reviewer`: AC-265-001..005 coverage and negative cases。
  - `spec-reviewer`: closure coverage, no scope drift, and report ledger readiness。
- Finish:
  - Update `report.md` with final evidence, reviewers, closure coverage, and docs impact。
  - Run `./spec-dock/scripts/spec-dock issue finish`。
  - Commit the issue changes with Japanese Conventional Commit。
  - No per-Issue PR; delivery waits for Epic-level PR after all issues。

## 実装委任契約
- delegated role: `dev-coder`。
- input docs:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - focused tests covering validation, ADR mirror, and sync projection。
- forbidden changes:
  - node migration, deletion, or rewrite of existing `discussions/`。
  - `new artifact` / `new doc` command semantics。
  - artifact filename grammar beyond existing parser contract。
  - `SpecNode` / `.meta.json` schema。
  - broad docs/skills rewrite。
- required output:
  - changed files。
  - Red / Green / Refactor or characterization evidence。
  - commands and results。
  - unresolved risks。
  - explicit note if any stop condition was approached。
