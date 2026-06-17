---
種別: 実装計画書（Issue）
ID: "iss-00188"
タイトル: "Prevent duplicate discussion timestamp slots when creating multiple artifacts"
関連GitHub: ["#188"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
依存: ["requirement.md", "design.md"]
親: ["epic-00033", "init-local-00003"]
---

# iss-00188 Prevent duplicate discussion timestamp slots when creating multiple artifacts — 実装計画

## この計画で満たす要件ID
- AC:
  - AC-001 runtime-owned PR repair batch creation
  - AC-002 existing `new doc` interface shape preserved
  - AC-003 manual filename guidance removed from shipped generation workflows
  - AC-004 wait before suffix fallback
  - AC-005 hyphenated doc type validation
- EC:
  - EC-001 frozen / non-advancing clock
  - EC-002 suffix exhaustion
  - EC-003 generated path body update
  - EC-004 repair unit creation
- 制約:
  - Existing timestamp grammar `yyyymmddthhmmssz` is preserved.
  - Suffix fallback `01..99` is preserved.
  - `note` remains retired for new creation.
  - No body/template input option, explicit basename, explicit doc_id override, existing artifact rename/repair, or `pr-repair-unit` type is introduced.

## 依存関係から導く実装順序
- Design source:
  - `design.md` module dependency diagram and directory/file change plan.
- 順序:
  - S01 shared catalog/parser foundation.
  - S02 runtime-owned `pr-repair-batch` creation.
  - S03 wait-before-suffix allocator.
  - S04 shipped guidance and dogfooding parity.
  - S90 docs impact resolution.
  - S99 final quality gate.
- 根拠:
  - S02 and S03 both depend on shared parsing/catalog semantics from S01.
  - S04 depends on S02 because shipped guidance must point to a real `new doc pr-repair-batch` command.
  - S90 closes docs impact after behavior and guidance surfaces are known.

## ステップ一覧
- S01 Shared catalog/parser foundation:
  - 依存: requirement/design reviewer pass.
  - unblock: S02, S03, S04.
  - 対象ファイル:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/discussion_docs.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py`
    - focused tests.
- S02 Runtime-owned `pr-repair-batch` creation:
  - 依存: S01 committed.
  - unblock: S04.
  - 対象ファイル:
    - `commands/new.py`
    - `application/create_node.py`
    - `templates/discussions/pr-repair-batch.md`
    - focused CLI/runtime/validation tests.
- S03 Wait-before-suffix allocator:
  - 依存: S01 committed.
  - unblock: S99.
  - 対象ファイル:
    - `application/create_node.py`
    - deterministic runtime tests.
- S04 Shipped guidance and dogfooding parity:
  - 依存: S02 committed.
  - unblock: S90/S99.
  - 対象ファイル:
    - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md`
    - `src/spec_dock/assets/install_root/.codex/AGENTS.md`
    - `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`
    - `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`
    - dogfooding copies under `.agents/` and `.codex/` by sync/update or parity inspection.
- S90 Docs impact resolution:
  - 依存: S01-S04 committed.
  - 対象ファイル:
    - `src/spec_dock/assets/spec_dock/docs/**` impacted catalog/guidance references.
- S99 Final quality gate:
  - 依存: S90 closed.
  - 対象:
    - integrated diff, report closure, final reviews.

## 要件 ↔ ステップ対応
- AC-001 -> S02, S03, S99
- AC-002 -> S02, S99
- AC-003 -> S04, S90, S99
- AC-004 -> S03, S99
- AC-005 -> S01, S02, S99
- EC-001 -> S03
- EC-002 -> S03
- EC-003 -> S04
- EC-004 -> S04

## 仕様固定クロージャ索引（Spec-Locked Closure Index）
| ID | ステップ | 種別 | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル | クロージャ証跡 |
|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | invariant | AC-005 | shared parser/catalog handles hyphenated and existing doc types consistently | timestamp filenames for current doc types and `pr-repair-batch` | catalog/regex drift | yes | red-required | report Step/Test Contract Closure |
| tc-002 | S01 | regression | AC-005 | malformed timestamp/discussion intent stays fail-closed | malformed basename candidates | silent acceptance | yes | red-required | report Step/Test Contract Closure |
| tc-003 | S02 | acceptance | AC-001 | `new doc pr-repair-batch` returns generated path/id/template/stdout | CLI command | missing first-class doc type | yes | red-required | report Step/Test Contract Closure |
| tc-004 | S02 | negative | AC-002 | body/template and explicit id/basename options are absent | CLI help/parser | interface creep | yes | inspect-only | report Test Contract Closure |
| tc-005 | S02 | validation | AC-005 | valid `pr-repair-batch` passes and malformed intent fails | validate command | hyphenated type regression | yes | red-required | report Step/Test Contract Closure |
| tc-006 | S03 | acceptance | AC-004 | occupied timestamp with advancing clock creates later suffix-less timestamp | fake clock sequence | suffix-first regression | yes | red-required | report Step/Test Contract Closure |
| tc-007 | S03 | edge | EC-001 | frozen clock uses suffix fallback after bounded wait | fake frozen clock | hang / nondeterministic wait | yes | red-required | report Step/Test Contract Closure |
| tc-008 | S03 | edge | EC-002 | suffix exhaustion remains fail-closed | occupied suffixes 01..99 | silent overwrite | yes | covered-existing | report Test Contract Closure |
| tc-009 | S04 | acceptance | AC-003 | in-scope shipped surfaces are command-first / returned-path-first | provider and dogfooding guidance text | manual filename recurrence | yes | inspect-only | report Test Contract Closure |
| tc-010 | S04 | edge | EC-003/EC-004 | batch body update uses generated path; repair unit remains `disc`/future follow-up | guidance text | scope creep / identity corruption | yes | inspect-only | report Test Contract Closure |
| tc-011 | S90 | docs | AC-003 | grammar reference and generation procedure are separated | docs text | reference-as-instruction ambiguity | yes | inspect-only | report Docs Impact Closure |
| tc-012 | S99 | final | all | focused tests, validate/sync, reviewer gates, report closure are complete | full issue diff | incomplete handoff | yes | manual-required | final quality gate evidence |

## レビュー / QA ゲート方針
- Step reviewer:
  - S01, S02, S03: `code-reviewer` after dev-coder work.
  - S04, S90: `spec-reviewer` after doc-writer work.
- Commit gate:
  - Each implementation step is one review scope and one commit.
  - No later step starts until previous step has review pass, commit/no-op evidence, and clean status evidence.
- Final gate:
  - S99 requires `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`, focused tests, `validate`, sync evidence, and report closure.

## 実装ステップ

### 実装ステップ S01 — Shared catalog/parser foundation
- 振る舞いの目標:
  - Discussion doc type catalog, timestamp filename regex, legacy filename regex, doc_id derivation, and malformed candidate detection share one source of truth that supports hyphenated doc types.
- design 参照:
  - `design.md` "ドメインモデル差分" and "ディレクトリ / ファイル変更計画".
- 依存:
  - Requirement/design reviewer pass.
- unblock:
  - S02, S03, S04.
- 計画済み契約:
  - scope:
    - Add shared helper module and migrate create/validate parsing to it without enabling `pr-repair-batch` CLI behavior yet unless needed for helper tests.
  - テスト義務:
    - closure ids: tc-001, tc-002.
    - coverage rationale: hyphenated doc type support is unsafe without central parser coverage.
  - Red / 代替証跡:
    - Add or update tests that fail before shared helper handles current types and malformed candidates consistently.
  - Green 検証:
    - `uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py tests/cli_runtime/test_validate.py tests/unit/application/test_validate.py`
  - refactor guardrail:
    - Allowed cleanup is limited to removing duplication made obsolete by the new shared parser/catalog inside the allowed paths.
    - Renaming public concepts, moving command boundaries, or changing filename grammar requires plan amendment and re-review.
  - amendment trigger:
    - Any need to change public filename grammar, legacy grandfathering, or retired `note` semantics.

#### 委任契約
- delegated role:
  - `dev-coder`
- input docs:
  - `requirement.md`, `design.md`, `plan.md`, `workflow_issue.md`, `authoring/issue-plan.md`
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/discussion_docs.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py`
  - focused tests under `tests/cli_runtime/` and `tests/unit/application/`
- forbidden changes:
  - CLI interface additions, docs/skill edits, allocator wait behavior, existing artifact migration.
- acceptance criteria:
  - tc-001 and tc-002 close.
- required verification:
  - pytest command listed above.
- reviewer focus:
  - `code-reviewer`: shared parser boundaries, compatibility, regression coverage.
- output required:
  - changed files, verification result, no material decision or Ledger Note, unresolved risks.
- stop conditions:
  - shared helper requires grammar change or larger validation policy change.

#### 具体テストケース一覧
- `tc-s01-001` acceptance: shared helper parses supported timestamp filenames.
  - 前提: Existing fixtures include `adr`, `disc`, `research`, `interview`, `scratch`, draft types, and grandfathered `note`.
  - 操作: Run focused parser/validation tests.
  - 期待結果: Supported timestamp filenames produce expected doc_type/doc_id and validation still passes.
  - 失敗検出: create/validate catalog drift or hyphenated-type-incompatible parsing.
  - 検証方法: `tests/cli_runtime/test_validate.py` / unit helper tests.
  - 関連 closure id: tc-001
- `tc-s01-002` negative: malformed discussion candidates remain fail-closed.
  - 前提: Existing malformed candidate cases plus doc-type-prefixed stems.
  - 操作: Run validation tests.
  - 期待結果: Malformed candidates fail with explicit malformed filename error.
  - 失敗検出: refactor accidentally ignores malformed discussion intent.
  - 検証方法: `tests/cli_runtime/test_validate.py`
  - 関連 closure id: tc-002

#### ステップ完了契約
- close 条件:
  - tc-001 and tc-002 pass, code-reviewer pass, step commit/no-op evidence recorded.
- report evidence:
  - Implementation Delegation Gate, TDD evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate.

### 実装ステップ S02 — Runtime-owned `pr-repair-batch` creation
- 振る舞いの目標:
  - `new doc pr-repair-batch` creates a valid runtime-generated discussion artifact and preserves existing `new doc` interface shape.
- 依存:
  - S01 committed.
- unblock:
  - S04.
- 計画済み契約:
  - scope:
    - Add `pr-repair-batch` to creatable catalog, provider template, CLI help output, stdout/doc_id/path behavior, and validation.
  - テスト義務:
    - closure ids: tc-003, tc-004, tc-005.
  - Green 検証:
    - `uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_runtime_new_doc_s09.py tests/cli_runtime/test_validate.py tests/unit/commands/test_runtime_new_s08.py`
  - refactor guardrail:
    - Allowed cleanup is limited to wiring `pr-repair-batch` through the shared catalog/template/create surfaces touched by this step.
    - Broader CLI parser restructuring, command output redesign, or template framework changes require plan amendment and re-review.
  - amendment trigger:
    - Need for body/template option, command output shape change, or `pr-repair-unit`.

#### 委任契約
- delegated role:
  - `dev-coder`
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/discussion_docs.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md`
  - focused CLI/runtime/validation tests.
- forbidden changes:
  - `--template-file`, `--body-file`, explicit basename/doc_id, `pr-repair-unit`, existing artifact migration, docs/skill guidance edits.
- input docs:
  - `requirement.md`, `design.md`, `plan.md`, `workflow_issue.md`, `authoring/issue-plan.md`
- acceptance criteria:
  - tc-003, tc-004, and tc-005 close without changing the existing `new doc` interface shape.
- required tests or docs-only verification:
  - pytest command listed above, plus CLI help/parser inspection for absence of new body/template/id/basename options.
- reviewer focus:
  - `code-reviewer`: public CLI behavior, runtime catalog/create flow, tests, validation, and backward compatibility.
  - `spec-reviewer`: provider discussion template identity, template/front matter alignment, and no interface creep into docs/template semantics.
- stop conditions:
  - template cannot preserve generated identity fields or `pr-repair-batch` requires public grammar change.
- output required:
  - changed files, verification result, CLI/output behavior summary, template impact summary, no material decision or Ledger Note, unresolved risks.

#### 具体テストケース一覧
- `tc-s02-001` acceptance: create PR repair batch artifact.
  - 前提: Temp repo has valid issue scope.
  - 操作: `new doc pr-repair-batch --issue iss-00003 --title "PR Repair Batch"`.
  - 期待結果: File `*-pr-repair-batch-pr-repair-batch.md` exists, stdout includes `type=pr-repair-batch`, slugless id, scope, path.
  - 失敗検出: doc type is not first-class or path/id are wrong.
  - 検証方法: `tests/cli_runtime/test_new.py`.
  - 関連 closure id: tc-003
- `tc-s02-002` negative: interface shape remains unchanged.
  - 前提: CLI help available after implementation.
  - 操作: inspect `new doc --help` and invalid options.
  - 期待結果: no body/template/basename/doc_id options are exposed or accepted.
  - 失敗検出: interface creep.
  - 検証方法: `tests/cli_runtime/test_new.py`.
  - 関連 closure id: tc-004
- `tc-s02-003` validation: hyphenated doc type validates.
  - 前提: Valid and malformed `pr-repair-batch` filenames exist in discussions.
  - 操作: run `validate`.
  - 期待結果: valid files pass; missing slug / malformed candidates fail.
  - 失敗検出: hyphenated type breaks validation or malformed detection.
  - 検証方法: `tests/cli_runtime/test_validate.py`.
  - 関連 closure id: tc-005

#### ステップ完了契約
- close 条件:
  - tc-003/tc-004/tc-005 pass, code-reviewer pass, spec-reviewer pass for template/spec alignment, step commit recorded.
- report evidence:
  - Implementation Delegation Gate, TDD evidence, Step/Test Contract Closure, Closure Coverage, Reviewer Gate Status for both reviewers, Step Commit Gate.

### 実装ステップ S03 — Wait-before-suffix allocator
- 振る舞いの目標:
  - Occupied timestamp slots wait/retry before suffix fallback with deterministic tests and bounded latency.
- 依存:
  - S01 committed.
- unblock:
  - S99.
- 計画済み契約:
  - scope:
    - Add allocation helper with wait budget default 1.1s, poll default 0.05s, env validation, injected fake clock/sleep test seam, suffix fallback.
  - テスト義務:
    - closure ids: tc-006, tc-007, tc-008.
  - Green 検証:
    - `uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py`
  - refactor guardrail:
    - Allowed cleanup is limited to allocation helper extraction and test injection seams inside the allowed runtime/test files.
    - Real sleeps in tests, public `Ports` expansion beyond design, timestamp grammar changes, or suffix policy changes require plan amendment and re-review.
  - amendment trigger:
    - Need to change timestamp grammar, suffix fallback, or public `Ports` contract beyond design.

#### 委任契約
- delegated role:
  - `dev-coder`
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - deterministic tests under `tests/cli_runtime/test_runtime_new_doc_s09.py`
- forbidden changes:
  - sub-second timestamp, removing suffix fallback, real one-second sleeps in tests, docs/skill edits.
- input docs:
  - `requirement.md`, `design.md`, `plan.md`, `workflow_issue.md`, `authoring/issue-plan.md`
- acceptance criteria:
  - tc-006, tc-007, and tc-008 close while preserving timestamp grammar and suffix fallback.
- required tests or docs-only verification:
  - pytest command listed above, including fake advancing clock, fake frozen clock, suffix exhaustion, and invalid env value coverage.
- reviewer focus:
  - `code-reviewer`: lock interaction, deterministic tests, no hangs, compatibility.
- stop conditions:
  - deterministic testing requires changing design wait contract.
- output required:
  - changed files, verification result, allocator timing/fallback behavior summary, no material decision or Ledger Note, unresolved risks.

#### 具体テストケース一覧
- `tc-s03-001` acceptance: advancing fake clock avoids suffix.
  - 前提: Existing standard timestamp slot is occupied and fake clock advances within budget.
  - 操作: create another doc through runtime allocator.
  - 期待結果: new file uses later suffix-less timestamp.
  - 失敗検出: suffix-first regression.
  - 検証方法: `tests/cli_runtime/test_runtime_new_doc_s09.py`.
  - 関連 closure id: tc-006
- `tc-s03-002` edge: frozen clock falls back to suffix.
  - 前提: Clock does not advance and wait budget is exhausted through fake sleep.
  - 操作: create another doc.
  - 期待結果: first available suffix is used; command does not hang.
  - 失敗検出: infinite loop or failure instead of fallback.
  - 検証方法: `tests/cli_runtime/test_runtime_new_doc_s09.py`.
  - 関連 closure id: tc-007
- `tc-s03-003` edge: suffix exhaustion remains fail-closed.
  - 前提: Standard slot and suffixes 01..99 are occupied.
  - 操作: create another doc after fallback path.
  - 期待結果: suffix exhaustion error; no file written.
  - 失敗検出: overwrite or silent success.
  - 検証方法: existing suffix exhaustion test updated if needed.
  - 関連 closure id: tc-008
- `tc-s03-004` negative: invalid env values fail fast.
  - 前提: wait/poll env values are zero, negative, or non-numeric.
  - 操作: create doc in occupied timestamp condition or resolve config.
  - 期待結果: invalid configuration error before ambiguous allocation.
  - 失敗検出: undefined zero wait semantics.
  - 検証方法: focused runtime test.
  - 関連 closure id: tc-007

#### ステップ完了契約
- close 条件:
  - tc-006/tc-007/tc-008 pass or covered-existing evidence recorded, code-reviewer pass, step commit recorded.
- report evidence:
  - TDD evidence, Step/Test Contract Closure, Closure Coverage, Closure Delta, Reviewer Gate Status, Step Commit Gate.

### 実装ステップ S04 — Shipped guidance and dogfooding parity
- 振る舞いの目標:
  - Shipped agent guidance uses command-first / returned-path-first artifact generation and dogfooding copies are not stale.
- 依存:
  - S02 committed.
- unblock:
  - S90/S99.
- 計画済み契約:
  - scope:
    - Update provider install-root skill / role / AGENTS guidance and dogfooding parity evidence.
  - テスト義務:
    - closure ids: tc-009, tc-010.
  - Green 検証:
    - targeted `rg` inspection.
    - focused `uv run pytest tests/unit/infra/test_init_update.py` tests for shipped assets.
  - refactor guardrail:
    - Allowed cleanup is limited to replacing manual filename instructions with command-first / returned-path-first wording in the in-scope surfaces.
    - Rewriting broader agent policy, delegated authoring workflow, or unrelated skill prose requires plan amendment or follow-up.
  - amendment trigger:
    - Guidance needs command support not implemented in S02 or broader delegated authoring policy change.

#### 委任契約
- delegated role:
  - `doc-writer`
- allowed paths:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md`
  - `src/spec_dock/assets/install_root/.codex/AGENTS.md`
  - `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`
  - `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`
  - `.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `.agents/skills/spec-dock-hub/SKILL.md`
  - `.codex/AGENTS.md`
  - `.codex/agents/system-architect.toml`
  - `.codex/agents/implementation-planner.toml`
  - update/sync side effects outside these enumerated dogfooding copies must be reported, reviewed, and either justified as generated parity output or reverted before step closure.
  - focused asset tests.
- forbidden changes:
  - runtime implementation, canonical active issue docs, existing artifact rename/repair.
- input docs:
  - `requirement.md`, `design.md`, `plan.md`, accepted ADRs, and the in-scope provider/dogfooding guidance files listed in AC-003.
- acceptance criteria:
  - tc-009 and tc-010 close with provider and dogfooding guidance aligned to command-first / returned-path-first artifact generation.
- required tests or docs-only verification:
  - targeted `rg` inspection for manual filename guidance recurrence, parity inspection or sync/update evidence for root copies, and focused asset tests when assertions are added or changed.
- reviewer focus:
  - `spec-reviewer`: docs/spec alignment, no manual filename guidance recurrence, dogfooding parity evidence.
  - `code-reviewer`: focused asset tests, scaffold propagation behavior, and any provider-to-dogfooding update/sync mechanics touched by the step.
- output required:
  - changed files, inspection commands, parity evidence, focused asset test results when touched, no material decision or Ledger Note.
- stop conditions:
  - Need to change runtime behavior or define new doc type beyond `pr-repair-batch`.

#### 具体テストケース一覧
- `tc-s04-001` inspect-only: PR merge preparer uses generated path.
  - 前提: Provider skill guidance is updated.
  - 操作: inspect skill text.
  - 期待結果: Skill calls `new doc pr-repair-batch`, captures returned path, updates only that path.
  - 失敗検出: remaining `<ts>-disc-pr-repair-batch.md` target filename instruction.
  - 検証方法: `rg` and focused asset tests.
  - 関連 closure id: tc-009
- `tc-s04-002` inspect-only: role configs do not handcraft filenames.
  - 前提: Provider `.codex` role configs and AGENTS are updated.
  - 操作: inspect provider and dogfooding copies.
  - 期待結果: no "Use filenames <timestamp>" generation instruction remains; grammar references are reference-only.
  - 失敗検出: known AC-003 surface remains stale.
  - 検証方法: `rg` plus parity evidence.
  - 関連 closure id: tc-009
- `tc-s04-003` inspect-only: repair unit remains out of scope.
  - 前提: PR repair guidance describes unit creation.
  - 操作: inspect unit guidance.
  - 期待結果: units remain `disc` or future follow-up; no `pr-repair-unit` type is required.
  - 失敗検出: scope creep into unapproved doc type.
  - 検証方法: guidance inspection.
  - 関連 closure id: tc-010

#### ステップ完了契約
- close 条件:
  - tc-009/tc-010 pass by inspection/tests, spec-reviewer pass, code-reviewer pass when tests/scaffold propagation are touched, dogfooding parity evidence recorded, step commit recorded.
- report evidence:
  - Delegated Worker Evidence, Test Contract Closure, Closure Coverage, Reviewer Gate Status for required reviewers, Step Commit Gate.

### ドキュメント影響の解消ステップ S90
- 対象:
  - `src/spec_dock/assets/spec_dock/docs/reference_naming.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/rules/{initiative,epic,issue}/discussions.md`
  - other docs surfaced by `rg` that list current catalog or describe generation procedure.
- 対応:
  - Update current catalog where listed.
  - Preserve ADR mirror as `adr`-only.
  - Separate grammar reference from generation procedure.
- doc update owner:
  - `doc-writer` when edits are required; approved-no-op only if inspection proves no docs need updates.
- verification:
  - `rg -n "current catalog|pr-repair-batch|new doc <type>|<ts>-<kind>|Use filenames" src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/install_root`
  - focused docs/asset tests.
- spec/doc review:
  - `spec-reviewer` pass required.
- closure:
  - tc-011 closed and report docs impact ledger updated.
- delegation contract:
  - delegated role:
    - `doc-writer`
  - input docs:
    - `requirement.md`, `design.md`, `plan.md`, accepted ADRs, and docs discovered by the S90 `rg` command.
  - allowed paths:
    - `src/spec_dock/assets/spec_dock/docs/reference_naming.md`
    - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
    - `src/spec_dock/assets/spec_dock/docs/rules/initiative/discussions.md`
    - `src/spec_dock/assets/spec_dock/docs/rules/epic/discussions.md`
    - `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md`
    - additional provider docs under `src/spec_dock/assets/spec_dock/docs/` only when discovered by the S90 inspection command and directly tied to tc-011.
  - forbidden changes:
    - runtime code, tests, templates, install-root skill/role assets, canonical issue docs except report evidence updates, and any ADR mirror broadening beyond `adr`-only.
  - acceptance criteria:
    - tc-011 closes by updating or explicitly no-oping catalog/generation-procedure docs with evidence.
  - required tests or docs-only verification:
    - S90 `rg` command, focused docs/asset tests when docs are covered by tests, and direct inspection of any approved-no-op target.
  - reviewer focus:
    - `spec-reviewer`: docs impact completeness, grammar-reference vs generation-procedure separation, no conflict with AC-003.
  - stop conditions:
    - docs need behavior not implemented by S01-S04, or docs reveal a new required public contract outside AC/EC.
  - output required:
    - changed files or approved-no-op rationale per target, inspection output summary, report Docs Impact Resolution row, no material decision or Ledger Note, unresolved risks.
- step gate:
  - `doc-writer` output is accepted only after spec-reviewer pass.
  - Commit or approved-no-op evidence is recorded before S99 starts.

### 最終品質ゲートステップ S99
- branch diff 範囲:
  - Runtime, templates, provider docs/assets, dogfooding parity copies, and tests touched by S01-S90.
- 必須 validation:
  - `uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py tests/cli_runtime/test_new.py tests/cli_runtime/test_validate.py tests/unit/infra/test_init_update.py`
  - `uv run pytest tests/unit/application/test_validate.py tests/unit/commands/test_runtime_new_s08.py`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync --no-github` or normal `sync` according to available command support.
- final QA gate:
  - `qa-reviewer` verifies closure coverage and integration test sufficiency.
- final code review gate:
  - issue-wide `code-reviewer` reviews integrated runtime/scaffold diff.
- final spec review gate:
  - `spec-reviewer` verifies requirement/design/plan/report/docs/test alignment.
- final commit gate:
  - Every implementation step is committed or valid approved-no-op before final commit.
  - Final response / PR / issue comment records post-commit clean evidence.

## Rollback / Compatibility
- Rollback:
  - Remove `pr-repair-batch` from creatable catalog/template/docs/guidance.
  - Revert allocator to suffix-first.
  - Do not rename or repair existing generated artifacts.
- Compatibility:
  - Existing timestamp grammar, suffix family, legacy sequential docs, and retired `note` grandfathering remain valid.

## 未確定事項
- なし。

## 最終完了条件
- All AC/EC closure ids tc-001 through tc-012 are closed in `report.md`.
- S01-S04 and S90 are committed or valid approved-no-op.
- S99 final QA/code/spec gates pass.
- `validate`, focused tests, and sync evidence are recorded.
- No unresolved Evidence Adoption Ledger, Delegated Draft Evidence, or Spec Interpretation entries remain.
