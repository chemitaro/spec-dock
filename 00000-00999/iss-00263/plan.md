---
種別: 実装計画書（Issue）
ID: "iss-00263"
タイトル: "New artifact command and new doc removal"
Issue Grade: "standard"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00263 New artifact command and new doc removal — 実装計画

## 1. この計画で満たす要件ID
- AC-263-001 blank command.
- AC-263-002 typed command.
- AC-263-003 full catalog.
- AC-263-004 new doc removal.
- AC-263-005 draft safety.
- AC-263-006 unsupported draft scope.
- AC-263-007 old node setup.
- Epic E-AC-001, E-AC-002, E-AC-003, E-AC-004, E-AC-006, E-AC-009.

## 2. 依存関係から導く実装順序
1. Artifact filename/catalog domain and application contractを先に固定する。
2. `new artifact` CLI/parser/outputを追加し、最低限の vertical happy pathを通す。
3. Direct catalog/old-node setup/collision/malformed/no-write behaviorを広げる。
4. Draft-* issue-only assurance/profile preflightを接続する。
5. `new doc` command-facing surfaceを削除し、tests/helpを更新する。
6. Docs impactを点検し、final QA/code/spec gatesを通す。

## 3. ステップ一覧
- S01: Artifact domain and application use case.
- S02: CLI parser/registry/output and `new doc` removal.
- S03: Creation behavior, catalog coverage, old-node setup, and no-write guards.
- S04: Draft-* issue-only assurance/profile safety.
- S90: Docs impact / downstream boundary check.
- S99: Final quality gate and commit candidate.

## 4. 要件 -> ステップ対応
- AC-263-001: S01, S02, S03.
- AC-263-002: S01, S02, S03.
- AC-263-003: S01, S03.
- AC-263-004: S02, S03.
- AC-263-005: S01, S04.
- AC-263-006: S01, S04.
- AC-263-007: S03, S90.

## 5. 仕様固定クロージャ索引
| Closure ID | Spec link | Observable input/state | Locked expectation | Required | Evidence level | Owner step |
|---|---|---|---|---|---|---|
| CLOS-263-001 | AC-263-001 / DES-263-001 | `new artifact blank --issue <id> --title ...` | creates `<scope>/artifacts/<ts>-<slug>.md`; id omits `blank`; output says `new artifact` | yes | CLI test | S01/S02/S03 |
| CLOS-263-002 | AC-263-002 / DES-263-002 | `new artifact research --epic <id> --title ...` and other direct types | creates typed artifact filename under `artifacts/` | yes | CLI test | S01/S02/S03 |
| CLOS-263-003 | AC-263-003 / DES-263-003 | supported/unsupported artifact type inputs | closed catalog succeeds; unknown, `scratch`, and `note` fail no-write | yes | CLI/unit test | S01/S03 |
| CLOS-263-004 | AC-263-004 / DES-263-004 | `new --help`; `new doc ...` | help lists `artifact`, omits `doc`; `new doc` fails as ordinary argparse error with no custom migration hint | yes | CLI test | S02/S03 |
| CLOS-263-005 | AC-263-005 / DES-263-005 | issue `draft-requirement/design/plan` artifact creation | requirement template reused for `draft-requirement`; profile templates reused for `draft-design` / `draft-plan`; invalid assurance/profile fails no-write for `draft-design` / `draft-plan` | yes | CLI test | S04 |
| CLOS-263-006 | AC-263-006 / DES-263-006 | initiative/epic `draft-*` input | fails no-write before `artifacts/` setup or artifact write | yes | CLI test | S04 |
| CLOS-263-007 | AC-263-007 / DES-263-007 | legacy node lacking `artifacts/` | creates `artifacts/` and relative `rules.md` symlink on successful creation; leaves `discussions/` untouched | yes | CLI/filesystem test | S03 |

## 6. 実装ステップ

### S01 Artifact domain and application use case
#### Planned contract
- Scope:
  - Add `CreateArtifactDocRequest/Result` and command-facing `UseCases.create_artifact_doc`.
  - Add `domain/artifacts.py` for catalog, filename/id parsing, blank id rule, suffix allocation, and malformed candidate detection.
  - Add `application/create_artifact_doc.py` for scope resolution, preflight order, template routing, setup/write orchestration, and post-write guard.
- Test obligation:
  - red-required where practical through focused unit tests or CLI tests that fail before implementation.
- Green verification:
  - New artifact domain/unit tests pass.
  - A minimal CLI or application test demonstrates blank artifact planning/writing path.
- Refactor guardrail:
  - Do not move legacy `discussion_docs.py` validation.
  - Do not overload `infra/artifact_store.py` as the scope-local artifact writer.

#### Delegation contract
- delegated role: `dev-coder`.
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_artifact_doc.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifacts.py`
  - Minimal wiring in runtime bootstrap if required.
  - Focused tests under `tests/unit/**` or `tests/cli_runtime/**`.
- forbidden changes:
  - `new doc` compatibility shim.
  - Broad validate/sync/ADR mirror changes.
  - Moving/renaming legacy `discussions/`.
  - Canonical docs/templates beyond issue docs.
- stop conditions:
  - Need to change scaffold defaults or validate/sync semantics.
- output required:
  - changed files, red/green evidence, no-write risk notes, and closure coverage.

#### 具体テストケース一覧
- `tc-s01-001` domain: direct and routing-only artifact catalogs are closed.
  - 期待: direct types and routing-only types are explicit; `scratch` / `note` unsupported.
  - 関連 closure id: CLOS-263-003.
- `tc-s01-002` domain: artifact filename/id parse and allocation.
  - 期待: blank id omits `blank`; typed id includes type; suffix 01..99 works.
  - 関連 closure id: CLOS-263-001, CLOS-263-002.
- `tc-s01-003` application: malformed artifact candidates fail before write.
  - 期待: artifact-intent malformed names under `artifacts/` block; `rules.md` is ignored.
  - 関連 closure id: CLOS-263-003.

### S02 CLI parser/registry/output and `new doc` removal
#### Planned contract
- Scope:
  - Add `new artifact` parser binding and command args.
  - Add `render_new_artifact_text`.
  - Remove `new doc` parser subcommand, command spec, command args, run function, and command-facing use case wiring.
  - Ensure `new --help` and `new doc` behavior match AC-263-004.
- Test obligation:
  - red-required CLI tests for help/removal.
- Green verification:
  - `new --help` lists artifact and omits doc.
  - `new doc ...` fails as ordinary argparse invalid choice / unknown subcommand with no custom migration hint.

#### Delegation contract
- delegated role: `dev-coder`.
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
  - bootstrap/registry/use-case wiring files if necessary.
  - CLI runtime tests.
- forbidden changes:
  - Alias/shim/custom migration hint.
  - Removing legacy discussion validation helpers unless unreachable and tests confirm no regressions.
- stop conditions:
  - Help/removal tests require broad unrelated CLI refactor.

#### 具体テストケース一覧
- `tc-s02-001` CLI: `new artifact --help` / `new --help`.
  - 期待: supported command shape is visible; `doc` absent from `new --help`.
  - 関連 closure id: CLOS-263-004.
- `tc-s02-002` CLI: `new doc ...` removal.
  - 期待: non-zero argparse error; no custom migration hint; no file write.
  - 関連 closure id: CLOS-263-004.

### S03 Creation behavior, catalog coverage, old-node setup, and no-write guards
#### Planned contract
- Scope:
  - Implement direct artifact writing under `<scope>/artifacts/`.
  - Implement old-node `artifacts/` setup and relative `rules.md` symlink.
  - Preserve `discussions/`.
  - Cover blank/typed/full direct catalog, unknown types, invalid slug, malformed candidate, duplicate, suffix exhaustion.
- Test obligation:
  - red-required CLI tests for happy paths and no-write negatives.
- Green verification:
  - Focused `tests/cli_runtime/test_new.py` artifact tests pass.
- Refactor guardrail:
  - Keep command-time creation separate from validate/sync/ADR mirror awareness.

#### Delegation contract
- delegated role: `dev-coder`.
- allowed paths:
  - S01/S02 implementation files.
  - `tests/cli_runtime/test_new.py`
  - `tests/cli_runtime/test_runtime_new_doc_s09.py` if shell/wrapper behavior references `new doc`.
  - Focused unit command tests if needed.
- forbidden changes:
  - Broad test harness rewrite.
  - Deleting legacy `discussions/` validation tests that do not depend on command surface.
- stop conditions:
  - New requirement to migrate existing discussions or default scaffold.

#### 具体テストケース一覧
- `tc-s03-001` CLI: blank issue artifact success.
  - 期待: `<ts>-<slug>.md`, `template: "blank"`, output id omits slug and `blank`.
  - 関連 closure id: CLOS-263-001.
- `tc-s03-002` CLI: typed epic artifact success.
  - 期待: `<ts>-research-<slug>.md`, output type/id/path.
  - 関連 closure id: CLOS-263-002.
- `tc-s03-003` CLI: full direct catalog success.
  - 期待: `research/interview/disc/decision-candidate/pr-repair-batch/adr/blank` route.
  - 関連 closure id: CLOS-263-003.
- `tc-s03-004` CLI: unsupported type no-write.
  - 期待: unknown, `scratch`, `note` fail; no `artifacts/` setup or file.
  - 関連 closure id: CLOS-263-003.
- `tc-s03-005` filesystem: old-node setup.
  - 期待: missing `artifacts/` is created with relative `rules.md`; existing `discussions/` unchanged.
  - 関連 closure id: CLOS-263-007.
- `tc-s03-006` negative: malformed artifact candidate and collision/suffix guards.
  - 期待: fail no-write for malformed candidates and exhausted suffixes.
  - 関連 closure id: CLOS-263-003.
- `tc-s03-007` regression: malformed `discussions/` candidate does not block `new artifact`.
  - 期待: artifact creation succeeds if only legacy discussions are malformed.
  - 関連 closure id: CLOS-263-007.

### S04 Draft-* issue-only assurance/profile safety
#### Planned contract
- Scope:
  - `draft-requirement`: issue-only, source `templates/issue/requirement.md`.
  - `draft-design` / `draft-plan`: issue-only, verify `.assurance.json`, then use authorized profile templates.
  - Initiative/Epic `draft-*`: fail no-write before `artifacts/` setup.
  - Missing/stale/invalid assurance/profile states fail no-write.
- Test obligation:
  - red-required CLI tests based on existing `new_doc_issue_profile_*` coverage.
- Green verification:
  - Focused draft safety tests pass.

#### Delegation contract
- delegated role: `dev-coder`.
- allowed paths:
  - S01 application/domain files.
  - `tests/cli_runtime/test_new.py`.
  - Assurance/profile helper tests if needed.
- forbidden changes:
  - Dedicated `templates/artifacts/draft-*.md`.
  - Relaxing `.assurance.json` verification.
  - Supporting initiative/epic draft-*.
- stop conditions:
  - Need for non-Issue assurance model or new ADR.

#### 具体テストケース一覧
- `tc-s04-001` CLI: issue draft requirement success.
  - 期待: issue requirement template body/source used; output path under `artifacts/`.
  - 関連 closure id: CLOS-263-005.
- `tc-s04-002` CLI: issue draft design/plan profile success.
  - 期待: authorized profile design/plan body used; non-authoritative frontmatter remains.
  - 関連 closure id: CLOS-263-005.
- `tc-s04-003` no-write: missing/invalid/stale assurance.
  - 期待: no artifact file and no old-node setup.
  - 関連 closure id: CLOS-263-005.
- `tc-s04-004` no-write: invalid profile template states.
  - 期待: missing/non-file/empty/symlink/outside templates fail before write.
  - 関連 closure id: CLOS-263-005.
- `tc-s04-005` no-write: initiative/epic draft-*.
  - 期待: unsupported issue-only failure before setup/write.
  - 関連 closure id: CLOS-263-006.

### S90 Docs impact / downstream boundary check
#### Planned contract
- Scope:
  - Inspect docs/help/rules surfaces that mention `new doc`.
  - Update only command-facing shipped guidance if it would be directly wrong after `new doc` removal.
  - Defer broad workflow/skills migration to later Issues.
- Test obligation:
  - inspect-only plus any updated docs structural check.
- Green verification:
  - Focused `rg` inspection and `./spec-dock/scripts/spec-dock validate`.

#### Delegation contract
- delegated role:
  - `doc-writer` only if shipped command guidance must be edited.
- allowed paths:
  - narrowly scoped shipped docs/rules/help examples if required.
  - `report.md` evidence by orchestrator.
- forbidden changes:
  - broad workflow docs / skills migration.
  - validate/sync/ADR mirror docs for later Issues.
- stop conditions:
  - docs update would redefine Epic scope.

#### 具体テストケース一覧
- `tc-s90-001` inspect-only: command-facing docs impact.
  - 期待: no remaining Issue-owned `new doc` guidance conflicts with removed command, or conflicts are explicitly deferred to later Issues with non-blocking rationale.
  - 関連 closure id: CLOS-263-004.

### S99 Final quality gate and commit candidate
#### Planned contract
- Scope:
  - Final focused tests, `spec-dock validate`, diff check, reviewer gates, report update, commit candidate.
- Required verification:
  - `uv run pytest tests/cli_runtime/test_new.py -k 'new_artifact or new_doc or draft or assurance'`
  - `uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py` if touched.
  - `uv run pytest tests/cli_runtime`
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
- Review gates:
  - QA reviewer for test sufficiency.
  - Code reviewer for runtime/test diff.
  - Spec reviewer for AC/design/plan/report alignment.

#### Delegation contract
- delegated role:
  - `qa-reviewer`, `code-reviewer`, `spec-reviewer`.
- forbidden changes:
  - reviewer self-fixes.
- stop conditions:
  - failing focused checks, reviewer fail, unresolved report entries.

#### 具体テストケース一覧
- `tc-s99-001` final focused lane.
  - 期待: all focused and cli_runtime checks pass.
  - 関連 closure id: CLOS-263-001 through CLOS-263-007.
- `tc-s99-002` final review.
  - 期待: QA/code/spec reviewer pass.
  - 関連 closure id: CLOS-263-001 through CLOS-263-007.

## 7. Docs / report evidence requirements
- `report.md` must record:
  - system-architect evidence adoption.
  - implementation-planner evidence adoption.
  - Spec Authoring Gate pass for requirement/design/plan before execution.
  - Step closure and test closure rows for each CLOS-263-*.
  - Reviewer gate status and final quality gates.

## 8. Rollback / non-goals
- Rollback is ordinary git revert before Epic PR merge.
- No compatibility shim for `new doc`.
- Existing `discussions/` data remains grandfathered and untouched.
- No default scaffold switch in this Issue.
