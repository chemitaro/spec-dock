---
種別: 実装計画書（Issue）
ID: "iss-00262"
タイトル: "Artifact templates and rules"
Issue Grade: "standard"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00262 Artifact templates and rules — 実装計画

## 1. この計画で満たす要件ID
- AC-262-001 catalog templates.
- AC-262-002 blank.
- AC-262-003 ADR.
- AC-262-004 draft.
- AC-262-005 rules.
- AC-262-006 no scratch.
- Depends on accepted Epic ADR `artifacts/20260701t072851z-adr-artifact-domain-filename-template-contract.md`.

## 2. 依存関係から導く実装順序
1. Provider-side artifact templates and routing documentationを追加する。
2. Provider-side rules / README guidanceを追加する。
3. Structural testsでcatalog/rules/template reuseを固定する。
4. 必要な範囲だけdogfooding mirrorを確認または同期する。
5. Final QA/code/spec gateを通し、commit候補を作る。

## 3. ステップ一覧
- S01: Provider artifact template catalog.
- S02: Artifact rules and README guidance.
- S03: Structural template/routing tests.
- S90: Docs impact / dogfooding mirror check.
- S99: Final quality gate and commit candidate.

## 4. 要件 -> ステップ対応
- AC-262-001: S01, S03.
- AC-262-002: S01, S03.
- AC-262-003: S01, S03.
- AC-262-004: S01, S03.
- AC-262-005: S02, S03, S90.
- AC-262-006: S01, S03.

## 5. 仕様固定クロージャ索引
| Closure ID | Spec link | Observable input/state | Locked expectation | Required | Evidence level | Owner step |
|---|---|---|---|---|---|---|
| CLOS-262-001 | AC-262-001 / DES-262-001 | provider `templates/artifacts/` and `templates/README.md` | supported catalog has direct template or explicit routing documentation | yes | structural test | S01/S03 |
| CLOS-262-002 | AC-262-002 / DES-262-002 | `templates/artifacts/blank.md` | blank records `template: "blank"` and filename guidance does not require `blank` token | yes | structural test | S01/S03 |
| CLOS-262-003 | AC-262-003 / DES-262-003 | `templates/artifacts/adr.md` | ADR template supports future original under `artifacts/` and accepted authority fields | yes | structural test | S01/S03 |
| CLOS-262-004 | AC-262-004 / DES-262-004 | README/rules draft routing documentation | draft-* reuses existing requirement/design/plan templates and Issue profile-aware selection without dedicated draft-only artifact template files | yes | structural test | S01/S03 |
| CLOS-262-005 | AC-262-005 / DES-262-005 | provider rules docs and template README | rules explain future `artifacts/` surface and legacy `discussions/` preservation | yes | structural test / inspection | S02/S03 |
| CLOS-262-006 | AC-262-006 / DES-262-006 | provider `templates/artifacts/` | `scratch` is absent from future artifact catalog | yes | negative structural test | S01/S03 |

## 6. 実装ステップ

### S01 Provider artifact template catalog
#### Planned contract
- Scope:
  - Add provider artifact templates under `src/spec_dock/assets/spec_dock/templates/artifacts/`.
  - Include direct templates for `blank`, `research`, `interview`, `disc`, `decision-candidate`, `pr-repair-batch`, `adr`.
  - Do not add physical artifact template files for `draft-requirement`, `draft-design`, or `draft-plan`; document their routing in README/rules and tests.
- Test obligation:
  - `inspect-only` before implementation, `red-required` when adding structural test in S03.
- Red or alternative evidence requirement:
  - Before adding files, structural inspection should show `templates/artifacts/` is absent or incomplete.
- Green verification:
  - S03 structural test passes.
- Refactor guardrail:
  - Do not refactor renderer or command code.
- Amendment trigger:
  - If runtime renderer must change to make templates meaningful, stop and move that work to `iss-00263`.

#### Delegation contract
- delegated role:
  - `doc-writer` for template files; `dev-coder` only if test fixture support requires code.
- input docs:
  - `requirement.md`, `design.md`, Epic ADR, `src/spec_dock/assets/spec_dock/templates/README.md`.
- allowed paths:
  - `src/spec_dock/assets/spec_dock/templates/artifacts/**`
  - `src/spec_dock/assets/spec_dock/templates/README.md`
  - S03 test paths when needed.
- forbidden changes:
  - Runtime command/parser/use-case code.
  - `templates/discussions/scratch.md` removal or migration.
  - Dedicated full content duplication of Issue profile design/plan templates into draft-*.
  - `src/spec_dock/assets/spec_dock/templates/artifacts/draft-requirement.md`, `draft-design.md`, or `draft-plan.md`.
- acceptance criteria:
  - CLOS-262-001, CLOS-262-002, CLOS-262-003, CLOS-262-004, CLOS-262-006.
- required tests or docs-only verification:
  - Structural test introduced in S03 or equivalent inspection evidence before commit.
- reviewer focus:
  - spec-reviewer for template/spec alignment; code-reviewer if tests are changed.
- stop conditions:
  - Need for runtime command wiring, filename allocation, assurance preflight, or scaffold default behavior.
- output required:
  - changed files, inspection/test result, risks, and either `Ledger Note` or `No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧
- `tc-s01-001` acceptance: supported artifact catalog files exist
  - 前提: provider assets do not yet have the complete `templates/artifacts/` catalog.
  - 操作: structural test inspects expected direct artifact template file names and README routing entries.
  - 期待結果: all future catalog entries except legacy-only `scratch` are represented.
  - 失敗検出: missing direct template, missing routing documentation, or unexpected `draft-*` physical template causes the test to fail before command work starts.
  - 検証方法: add focused test in `tests/unit/infra/` or nearby template/scaffold lane.
  - 関連 closure id: CLOS-262-001, CLOS-262-006
- `tc-s01-002` acceptance: blank template records template identity
  - 前提: `blank.md` exists under provider artifact templates.
  - 操作: structural test reads `blank.md`.
  - 期待結果: frontmatter or template body records `template: "blank"` and does not require `blank` in filename.
  - 失敗検出: blank behaves like typed filename template or lacks template identity.
  - 検証方法: focused structural assertion.
  - 関連 closure id: CLOS-262-002
- `tc-s01-003` acceptance: ADR and draft routing contracts are represented
  - 前提: `adr.md` exists and README/rules contain draft-* routing documentation.
  - 操作: structural test reads `adr.md`, README/rules, and confirms `templates/artifacts/draft-*.md` files are absent.
  - 期待結果: ADR supports accepted authority; draft-* routing points to existing requirement/design/plan templates and Issue profile-aware design/plan selection.
  - 失敗検出: draft-* physical files are added, draft-* duplicates content instead of routing, or ADR lacks authority/original guidance.
  - 検証方法: focused structural assertion.
  - 関連 closure id: CLOS-262-003, CLOS-262-004

#### Step closure contract
- Close when direct template files and routing documentation exist, structural expectations are covered, and no runtime command changes were required.
- Report evidence destination:
  - `report.md` Session Log, Step Contract Closure, Test Contract Closure.
- Step gate:
  - S01 may proceed to S02 after files are present; S03 must verify before final gate.

### S02 Artifact rules and README guidance
#### Planned contract
- Scope:
  - Add provider rules docs for artifact directories.
  - Update provider template README to describe `templates/artifacts/`, `new artifact`, draft template reuse, no `scratch` future catalog, and legacy discussion preservation.
- Test obligation:
  - Structural test / inspection.
- Red or alternative evidence requirement:
  - Existing README/rules mention `discussions/` and `new doc` as current surface; absence of artifact rules is sufficient characterization evidence.
- Green verification:
  - S03 structural test or `rg` inspection confirms expected wording.
- Refactor guardrail:
  - Do not perform full docs/workflow/skill migration; that belongs to `iss-00267`.
- Amendment trigger:
  - If README wording requires changing runtime behavior or command help, move to `iss-00263` or `iss-00267`.

#### Delegation contract
- delegated role:
  - `doc-writer`.
- input docs:
  - `requirement.md`, `design.md`, Epic ADR, existing provider `templates/README.md`, existing `docs/rules/*/discussions.md`.
- allowed paths:
  - `src/spec_dock/assets/spec_dock/templates/README.md`
  - `src/spec_dock/assets/spec_dock/docs/rules/initiative/artifacts.md`
  - `src/spec_dock/assets/spec_dock/docs/rules/epic/artifacts.md`
  - `src/spec_dock/assets/spec_dock/docs/rules/issue/artifacts.md`
  - S03 test paths when needed.
- forbidden changes:
  - Broad workflow docs / skills / README command migration outside template/rules scope.
  - Removing existing discussion rules.
- acceptance criteria:
  - CLOS-262-005 plus support for CLOS-262-004.
- required tests or docs-only verification:
  - Structural test or focused `rg` inspection for `artifacts/`, `new artifact`, legacy `discussions/`, and draft template reuse.
- reviewer focus:
  - spec-reviewer docs/spec alignment.
- stop conditions:
  - Need to change command implementation, scaffold creation, sync, validation, or delegated authoring guard.
- output required:
  - changed files, inspection/test result, risks, and either `Ledger Note` or `No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧
- `tc-s02-001` acceptance: artifact rules describe future surface
  - 前提: provider `docs/rules/*/artifacts.md` files exist.
  - 操作: structural test or inspection reads initiative/epic/issue artifact rules.
  - 期待結果: each file says future working artifacts live under `artifacts/` and canonical docs remain separate.
  - 失敗検出: rules still route future artifacts to `discussions/` or blur canonical docs with artifacts.
  - 検証方法: focused structural assertion or `rg` evidence.
  - 関連 closure id: CLOS-262-005
- `tc-s02-002` acceptance: README documents draft reuse and no scratch
  - 前提: provider `templates/README.md` is updated.
  - 操作: structural test or inspection reads README.
  - 期待結果: README documents draft-* reuse of existing templates and excludes `scratch` from future catalog.
  - 失敗検出: README implies dedicated draft-only templates or future scratch support.
  - 検証方法: focused structural assertion or `rg` evidence.
  - 関連 closure id: CLOS-262-004, CLOS-262-006

#### Step closure contract
- Close when artifact rules and README guidance are present and tested/inspected.
- Report evidence destination:
  - `report.md` Session Log, Step Contract Closure, Test Contract Closure.
- Step gate:
  - S02 may proceed to S03 after docs are present.

### S03 Structural template/routing tests
#### Planned contract
- Scope:
  - Add focused tests for provider template/rules structure and wording.
- Test obligation:
  - `red-required` for structural assertions where practical.
- Red or alternative evidence requirement:
  - Run the new focused test before implementation or record equivalent pre-change failure/absence evidence.
- Green verification:
  - `uv run pytest <focused test path>` passes.
- Refactor guardrail:
  - Keep tests structural and low-level; do not rewrite large fixture harnesses.
- Amendment trigger:
  - If existing test architecture cannot inspect shipped assets without broad harness work, record inspection alternative and request plan amendment if automated coverage would be too broad.

#### Delegation contract
- delegated role:
  - `dev-coder`.
- input docs:
  - `requirement.md`, `design.md`, this `plan.md`, existing tests in `tests/unit/infra/` and `tests/cli_runtime/`.
- allowed paths:
  - `tests/unit/infra/**`
  - minimal nearby test helper changes if required.
- forbidden changes:
  - Runtime implementation behavior changes.
  - Broad rewrites of `tests/cli_runtime/test_new.py`.
- acceptance criteria:
  - CLOS-262-001 through CLOS-262-006.
- required tests or docs-only verification:
  - Focused pytest command for new structural tests.
- reviewer focus:
  - code-reviewer for test correctness and scope.
- stop conditions:
  - Need for provider runtime code changes outside structural tests.
- output required:
  - changed files, red/green evidence, command output summary, and either `Ledger Note` or `No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧
- `tc-s03-001` red/green: provider artifact catalog structural test
  - 前提: test targets provider asset directory.
  - 操作: run focused pytest after adding test, before implementation if possible.
  - 期待結果: pre-change fails for missing catalog; post-change passes.
  - 失敗検出: missing catalog files, unexpected `scratch.md`, or missing blank identity.
  - 検証方法: `uv run pytest tests/unit/infra/<new_or_existing_test_file>.py -k artifact`
  - 関連 closure id: CLOS-262-001, CLOS-262-002, CLOS-262-006
- `tc-s03-002` red/green: draft routing and rules structural test
  - 前提: test can read provider templates README, rules docs, and artifact templates.
  - 操作: run focused pytest after adding test, before implementation if possible.
  - 期待結果: pre-change fails for absent artifact rules/routing; post-change passes.
  - 失敗検出: draft-only duplication, missing Issue profile-aware mention, or absent legacy discussion preservation.
  - 検証方法: `uv run pytest tests/unit/infra/<new_or_existing_test_file>.py -k artifact`
  - 関連 closure id: CLOS-262-003, CLOS-262-004, CLOS-262-005

#### Step closure contract
- Close when focused test passes and coverage maps to all required closure rows.
- Report evidence destination:
  - `report.md` TDD / Red / Green / Refactor Evidence, Test Contract Closure.
- Step gate:
  - S03 must pass before S90/S99.

### S90 Docs impact / dogfooding mirror check
#### Planned contract
- Scope:
  - Confirm whether dogfooding mirror needs provider asset refresh in this Issue.
  - Confirm broad docs/skills migration remains assigned to `iss-00267`.
- Test obligation:
  - inspect-only.
- Red or alternative evidence requirement:
  - N/A; docs impact gate.
- Green verification:
  - `rg` inspection over touched provider/mirror paths and `./spec-dock/scripts/spec-dock validate`.
- Refactor guardrail:
  - Do not start `iss-00267` docs/skills alignment early.
- Amendment trigger:
  - If provider template addition cannot be validated without mirror refresh, document and perform minimal mirror update.

#### Delegation contract
- delegated role:
  - `doc-writer` if mirror/docs edits are required; otherwise parent may record inspection evidence.
- input docs:
  - `requirement.md`, `design.md`, `plan.md`, Epic plan.
- allowed paths:
  - `spec-dock/templates/**`
  - `spec-dock/docs/rules/**`
  - `report.md`
- forbidden changes:
  - Runtime implementation, workflow docs, skills beyond this Issue scope.
- acceptance criteria:
  - No remaining `iss-00262` docs impact unresolved before final gate.
- required tests or docs-only verification:
  - `./spec-dock/scripts/spec-dock validate`
  - Focused `rg` inspection.
- reviewer focus:
  - spec-reviewer docs/spec alignment.
- stop conditions:
  - Need for command/scaffold/docs-wide migration belonging to later Issues.
- output required:
  - inspection result and residual risks.

#### 具体テストケース一覧
- `tc-s90-001` inspect-only: docs impact remains bounded
  - 前提: S01-S03 changes are complete.
  - 操作: inspect touched paths and search for Issue-owned terms.
  - 期待結果: provider template/rules changes are coherent; broad workflow/skill work is deferred to `iss-00267`.
  - 失敗検出: hidden dependency on command/scaffold/docs-wide behavior.
  - 検証方法: `rg` inspection and report evidence.

#### Step closure contract
- Close when docs/mirror status is recorded and no blocking docs impact remains in this Issue.
- Report evidence destination:
  - `report.md` Session Log and Closure Coverage.

### S99 Final quality gate and commit candidate
#### Planned contract
- Scope:
  - Run final focused tests, validation, reviewer gates, report update, and commit candidate.
- Test obligation:
  - focused pytest, `spec-dock validate`, diff inspection.
- Red or alternative evidence requirement:
  - Use S03 red/green evidence and final pass evidence.
- Green verification:
  - `uv run pytest <focused test path>`
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
- Refactor guardrail:
  - Only tidy changes introduced by this Issue.
- Amendment trigger:
  - Any unmet AC, new runtime behavior requirement, or reviewer fail that changes scope.

#### Delegation contract
- delegated role:
  - `qa-reviewer`, `code-reviewer`, and `spec-reviewer` as final gates.
- input docs:
  - final diff, requirement/design/plan/report, test output.
- allowed paths:
  - review-only.
- forbidden changes:
  - reviewer self-fixes.
- acceptance criteria:
  - All CLOS-262 rows pass.
- required tests or docs-only verification:
  - focused pytest, validate, diff check.
- reviewer focus:
  - qa-reviewer: test sufficiency.
  - code-reviewer: changed tests/assets and regressions.
  - spec-reviewer: AC/design/plan satisfaction and handoff to `iss-00263`.
- stop conditions:
  - reviewer fail, unresolved report ledger entry, failing check, dirty unrelated changes.
- output required:
  - reviewer verdicts, commit/no-op evidence, residual risks.

#### 具体テストケース一覧
- `tc-s99-001` final gate: focused checks pass
  - 前提: S01-S90 complete.
  - 操作: run focused pytest, validate, and diff check.
  - 期待結果: all commands pass.
  - 失敗検出: missed structural coverage, invalid SpecDock tree, whitespace errors.
  - 検証方法: command evidence in `report.md`.
- `tc-s99-002` final review: reviewers pass
  - 前提: final diff and report evidence are ready.
  - 操作: run qa/code/spec reviewer gates.
  - 期待結果: no blocking findings; residual risks are documented.
  - 失敗検出: unmet AC, missing test sufficiency, or scope creep.
  - 検証方法: reviewer outputs summarized in `report.md`.

#### Step closure contract
- Close when final checks and reviewer gates pass, report is updated, and commit candidate exists.
- Report evidence destination:
  - `report.md` Reviewer Gate Status, Final Quality Gate, Commit Evidence.

## 7. Final Exit Contract
- `requirement.md`, `design.md`, and `plan.md` are approved and fresh-reviewed.
- S01-S99 closure rows are evidenced in `report.md`.
- Focused structural tests pass.
- `./spec-dock/scripts/spec-dock validate` passes.
- `git diff --check` passes.
- qa-reviewer, code-reviewer, and spec-reviewer final gates pass or explicit workflow-compliant handling is recorded.
- Commit candidate is created for `iss-00262`.
- No per-Issue PR is created; delivery remains Epic-level PR after `iss-00268`.
