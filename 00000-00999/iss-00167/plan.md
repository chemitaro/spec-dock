---
種別: 実装計画書（Issue）
ID: "iss-00167"
タイトル: "Migrate Tests To Pytest"
関連GitHub: ["#167"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
依存: ["requirement.md", "design.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00167 Migrate Tests To Pytest — 実装計画（実行契約 / Execution Contract）

> `plan.md` は planned contract です。実行結果、逸脱、発見した追加 test、reviewer verdict、commit/no-op evidence は `report.md` に記録する。

## この計画で満たす要件ID
- AC:
  - AC-001: pytest dependency / config / collection contract
  - AC-002: GitHub Actions / provider CI runs the full pytest suite
  - AC-003: integration lane uses pytest
  - AC-004: `tests/cli_runtime` lane uses pytest
  - AC-005: full suite fallback is `uv run pytest`
  - AC-006: `unittest` runner / assertion / fixture API dependency is removed
  - AC-007: README / AGENTS / CI / command-string tests are pytest-aligned
  - AC-008: test intent, assertion strength, hermeticity, and runtime coverage are preserved
  - AC-009: parent Epic deferred testing / regression lane boundary is preserved
- EC:
  - EC-001: collect-only / pytest config edge
  - EC-002: former `subTest` cases keep visibility through parametrization or labeled assertions
  - EC-003: exception expectations use `pytest.raises(..., match=...)`
  - EC-004: patching / temp paths use pytest-native fixtures or local fakes
  - EC-005: runtime lane duration is recorded when material; optimization remains out of scope
  - EC-006: collection cleanup touches stale directories/cache only when evidence requires it
  - EC-007: docs / CI command-string assertions are updated with docs/CI cutover
- 制約:
  - Product runtime / CLI public behavior is unchanged.
  - Test lanes remain `tests/unit`, `tests/integration`, and `tests/cli_runtime`.
  - GitHub Actions / provider CI runs `uv run pytest`, not only `tests/unit`.
  - No pytest plugins beyond pytest.
  - No permanent `unittest` import exception, including `unittest.mock`.

## 依存関係から導く実装順序
- 依存関係の正本:
  - `design.md` の D-001..D-004、依存関係分析、Module Dependency Diagram、Directory / File Change Plan。
- 順序ルール:
  - pytest executable availability and collection config must exist before migrated tests can produce Green evidence.
  - `tests/cli_runtime/harness.py` must be converted before dependent runtime tests.
  - Low-risk / lower-dependency unit packages are converted before the large `tests/unit/infra/test_init_update.py`.
  - Docs / CI cutover is last among implementation steps so GitHub Actions switches to the full pytest command after the runner contract is real.
  - Final gates prove complete cutover; they do not replace step-local review.

## ステップ一覧
- S00 preflight characterization:
  - 観測可能な振る舞い: current pytest absence / unittest dependency baseline is recorded.
  - 依存: requirement and design fresh pass.
  - unblock: S01.
  - 対象ファイル: read-only.
  - 閉じる要件: AC-008 evidence baseline.
  - レビューゲート: no code review; report evidence required.
- S01 pytest dependency and collection contract:
  - 観測可能な振る舞い: `uv run pytest --version` and `uv run pytest --collect-only` work.
  - 依存: S00.
  - unblock: S02..S99.
  - 対象ファイル: `pyproject.toml`, `uv.lock`.
  - 閉じる要件: AC-001, EC-001.
  - レビューゲート: code-reviewer.
- S02 runtime harness pytest-native conversion:
  - 観測可能な振る舞い: runtime helper no longer requires `unittest.TestCase`.
  - 依存: S01.
  - unblock: S03.
  - 対象ファイル: `tests/cli_runtime/harness.py`, optional `tests/cli_runtime/conftest.py`.
  - 閉じる要件: AC-004, AC-006, EC-004.
  - レビューゲート: code-reviewer.
- S03 runtime / CLI regression lane migration:
  - 観測可能な振る舞い: `uv run pytest tests/cli_runtime` passes without unittest dependency.
  - 依存: S02.
  - unblock: S08, S99.
  - 対象ファイル: `tests/cli_runtime/test_*.py`, optional runtime `conftest.py`.
  - 閉じる要件: AC-004, AC-006, AC-008, EC-002, EC-003, EC-005.
  - レビューゲート: code-reviewer.
- S04 small / medium unit package migration:
  - 観測可能な振る舞い: unit groups outside the large infra file pass under pytest idioms.
  - 依存: S01.
  - unblock: S05, S08.
  - 対象ファイル: `tests/unit/application`, `tests/unit/cli`, `tests/unit/commands`, `tests/unit/domain`, `tests/unit/presentation`, `tests/unit/test_discovery.py`, optional `tests/unit/conftest.py`.
  - 閉じる要件: AC-002, AC-006, AC-008, EC-002..EC-004.
  - レビューゲート: code-reviewer.
- S05 large installer/update unit migration:
  - 観測可能な振る舞い: `uv run pytest tests/unit/infra` and `uv run pytest tests/unit` pass.
  - 依存: S04.
  - unblock: S08, S90.
  - 対象ファイル: `tests/unit/infra/**`, optional infra `conftest.py`.
  - 閉じる要件: AC-002, AC-006, AC-008, EC-003, EC-004, EC-007.
  - レビューゲート: code-reviewer.
- S06 integration lane migration:
  - 観測可能な振る舞い: `uv run pytest tests/integration` passes without unittest dependency.
  - 依存: S01.
  - unblock: S08, S99.
  - 対象ファイル: `tests/integration/test_discovery.py`, package markers only if collection evidence requires.
  - 閉じる要件: AC-003, AC-006.
  - レビューゲート: code-reviewer.
- S08 unittest absence cleanup and lane consolidation:
  - 観測可能な振る舞い: all test lanes pass and test files have no unittest framework dependency.
  - 依存: S03, S05, S06.
  - unblock: S90, S99.
  - 対象ファイル: tests only, cleanup caused by S02..S06.
  - 閉じる要件: AC-006, AC-008, EC-006.
  - レビューゲート: code-reviewer.
- S90 docs impact resolution and CI cutover:
  - 観測可能な振る舞い: contributor docs and GitHub Actions / provider CI expose pytest full-suite commands only.
  - 依存: S08.
  - unblock: S99.
  - 対象ファイル: `README.md`, `AGENTS.md`, `.github/workflows/provider-ci.yml`, tests asserting command strings.
  - 閉じる要件: AC-002, AC-007, EC-007.
  - レビューゲート: code-reviewer for workflow/tests and spec-reviewer for docs/spec alignment.
- S99 final quality gate:
  - 観測可能な振る舞い: full pytest migration is proven by full commands, grep absence, and three final reviewers.
  - 依存: S90.
  - unblock: issue execution closeout.
  - 対象ファイル: no planned implementation edits.
  - 閉じる要件: AC-001..AC-009, EC-001..EC-007.
  - レビューゲート: qa-reviewer, issue-wide code-reviewer, final spec-reviewer.

## 要件 ↔ ステップ対応
- AC-001 -> S01, S99
- AC-002 -> S04, S05, S90, S99
- AC-003 -> S06, S99
- AC-004 -> S02, S03, S99
- AC-005 -> S99
- AC-006 -> S02, S03, S04, S05, S06, S08, S99
- AC-007 -> S90, S99
- AC-008 -> S00, S03, S04, S05, S08, S99
- AC-009 -> S99
- EC-001 -> S01
- EC-002 -> S03, S04, S05
- EC-003 -> S03, S04, S05
- EC-004 -> S02, S04, S05
- EC-005 -> S03, S99
- EC-006 -> S08
- EC-007 -> S90

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ | スライス | 種別 | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル | クロージャ証跡 |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-000 | S00 | baseline | characterization | AC-008 | current pytest/unittest state is recorded before edits | read-only commands against current tree | unverifiable migration baseline | yes | inspect-only | Step/Test Contract Closure |
| tc-001 | S01 | runner contract | acceptance | AC-001, EC-001 | pytest is available through `uv run` and collects current lanes | `uv run pytest --version`; `uv run pytest --collect-only` | missing dependency/config | yes | red-required or covered-existing | Step/Test Contract Closure |
| tc-002 | S02 | runtime harness | acceptance | AC-004, AC-006, EC-004 | runtime helpers work without `unittest.TestCase` inheritance | focused runtime helper pytest command | hidden TestCase dependency | yes | red-required | Step/Test Contract Closure |
| tc-003 | S03 | runtime lane | acceptance | AC-004, AC-006, AC-008 | `tests/cli_runtime` passes under pytest and has no unittest dependency | `uv run pytest tests/cli_runtime`; scoped `rg` | runtime regression lost during conversion | yes | red-required | Step/Test Contract Closure |
| tc-004 | S03 | multi-case visibility | regression | EC-002 | former `subTest` cases remain distinguishable | parametrized tests or explicit case labels | loss of failure localization | yes | covered-existing | Test Contract Closure |
| tc-005 | S03 | exception expectations | regression | EC-003 | expected failures assert exception type/message | pytest exception tests | broad exception assertions | yes | covered-existing | Test Contract Closure |
| tc-006 | S04 | unit groups | acceptance | AC-002, AC-006, AC-008 | small/medium unit packages, including commands tests, pass under pytest idioms | package-group pytest commands | partial unit migration | yes | red-required | Step/Test Contract Closure |
| tc-007 | S05 | infra unit lane | acceptance | AC-002, AC-006, AC-008 | large infra tests and all unit tests pass under pytest | `uv run pytest tests/unit/infra`; `uv run pytest tests/unit` | weakened installer/update assertions | yes | red-required | Step/Test Contract Closure |
| tc-008 | S06 | integration lane | acceptance | AC-003, AC-006 | integration lane is pytest-native and hermetic | `uv run pytest tests/integration`; scoped `rg` | integration lane dropped from contract | yes | red-required | Step/Test Contract Closure |
| tc-009 | S08 | unittest absence | acceptance | AC-006, EC-006 | no migration-blocking unittest dependency remains in tests | grep absence; lane commands | compatibility-only pytest migration | yes | inspect-only | Step/Test Contract Closure |
| tc-010 | S90 | docs / CI cutover | acceptance | AC-002, AC-007, EC-007 | README / AGENTS / provider CI name `uv run pytest` as the GitHub Actions full-suite command | docs/CI grep; full-suite command-string tests | stale or partial official command contract | yes | inspect-only | Step/Test Contract Closure |
| tc-011 | S99 | full suite | acceptance | AC-005 | `uv run pytest` passes as full fallback | full pytest run | lane-only hidden failure | yes | red-required | Final Test Contract Closure |
| tc-012 | S99 | final quality | review | AC-008, AC-009 | QA, code, and spec reviewers pass with parent trace intact | reviewer outputs | assertion weakening or parent-scope drift | yes | manual-required | Final QA/Code/Spec Gate |

## レビュー / QA ゲート方針
- Step review:
  - code / runtime / tests / config / workflow behavior changes require fresh `code-reviewer` pass before commit.
  - docs-only changes require `spec-reviewer` docs/spec alignment; mixed docs + tests/workflow changes either split or list both reviewer focus.
- Final quality gate:
  - `qa-reviewer` checks test sufficiency and assertion-strength preservation.
  - issue-wide `code-reviewer` checks integrated diff structure, responsibility boundaries, and regression risk.
  - final `spec-reviewer` checks requirement / design / plan / report / docs / tests alignment and parent Epic trace.
- Reviewer output is not optional and worker output never substitutes for reviewer pass.

## 実行ルール（全ステップ共通）
- Main orchestrator does not directly edit source/tests/docs outside issue-scoped canonical docs; implementation is delegated.
- Each implementation step is a commit boundary unless it is a justified read-only `approved-no-op`.
- Each worker must return changed files, verification results, unresolved risks, and report evidence notes.
- If a step needs paths outside its allowed list, permanent `unittest` exception, pytest plugin, provider CI reduction below full suite, product runtime source change, test deletion, skip/xfail addition, or assertion weakening, stop for plan amendment and fresh review.
- Report updates must record Step Contract Closure, Test Contract Closure, Closure Coverage, reviewer gate, and commit/no-op evidence.

## 実装ステップ

### 実装ステップ S00 — Preflight characterization
- 振る舞いの目標:
  - Current pytest availability and unittest dependency baseline are recorded without changing product files.
- design 参照:
  - Baseline / Red strategy; AC-008 preservation.
- 依存:
  - Requirement and design fresh reviewer pass.
- unblock:
  - S01.
- 対象ファイル:
  - read-only; `report.md` evidence update after observation.
- 計画済み契約:
  - scope: read-only command evidence for current config/docs/tests.
  - テスト義務: `tc-000`.
  - Red / 代替証跡: inspect-only, because this is characterization.
  - 実装範囲:
    - allowed paths: none for implementation; issue `report.md` evidence update by orchestrator.
    - forbidden changes: source, tests, docs, config.
  - Green 検証:
    - `uv run pytest --version` or unavailable evidence.
    - `uv run pytest --collect-only` or unavailable evidence.
    - grep baseline for unittest dependencies.
  - amendment trigger:
    - pytest already fully configured and all grep checks already clean.

#### 委任契約
- 委任ロール: `dev-coder` read-only evidence worker.
- 入力 docs: `requirement.md`, `design.md`, `plan.md`.
- 許可 paths: none.
- 禁止 changes: any file edit.
- 受け入れ条件: baseline commands reported and report evidence prepared.
- 必須 verification: read-only commands listed above.
- reviewer focus: none; no diff.
- 必須出力: command summaries, current blockers, no changed files.
- 停止条件: command requires network/permissions outside approved environment and cannot be safely retried.

#### 具体テストケース一覧
- `tc-s00-001` inspect-only: current baseline is observable.
  - 前提: No implementation changes for this issue step.
  - 操作: Run pytest availability/collection probes and grep commands.
  - 期待結果: Current absence or failure mode is captured, not hidden.
  - 失敗検出: A migration proceeds without a baseline for what changed.
  - 検証方法: Command summaries in `report.md`.
  - 関連 closure id: tc-000

#### ステップ完了契約
- close 条件: `tc-000` baseline evidence is recorded.
- report evidence: Step Contract Closure, Test Contract Closure.
- 残リスク: None; read-only.

#### ステップゲート
- step reviewer gate: N/A read-only.
- commit / no-op gate: approved-no-op if no files are changed other than orchestrator report evidence.

### 実装ステップ S01 — Pytest dependency and collection contract
- 振る舞いの目標:
  - `uv run pytest` is a valid runner entrypoint and can collect the current test tree.
- design 参照:
  - D-001; interface contract.
- 依存: S00.
- unblock: S02, S03, S04, S05, S06, S08, S90, S99.
- 対象ファイル:
  - `pyproject.toml`
  - `uv.lock`
- 計画済み契約:
  - scope: add pytest in `dependency-groups.dev`; add minimal pytest config only as needed.
  - テスト義務: `tc-001`.
  - Red / 代替証跡: red-required if pytest is initially unavailable or collection fails; otherwise covered-existing characterization.
  - 実装範囲:
    - allowed paths: `pyproject.toml`, `uv.lock`.
    - forbidden changes: tests, docs, CI, product source, pytest plugins.
  - Green 検証:
    - `uv run pytest --version`
    - `uv run pytest --collect-only`
  - amendment trigger:
    - pytest plugin need, dependency group unsupported, or collection requires changing test/source behavior in this step.

#### 委任契約
- 委任ロール: `dev-coder`.
- 入力 docs: `requirement.md`, `design.md`, `plan.md`, `pyproject.toml`, `uv.lock`.
- 許可 paths: `pyproject.toml`, `uv.lock`.
- 禁止 changes: tests/docs/CI/runtime source.
- 受け入れ条件: `tc-001` closes.
- 必須 verification: `uv run pytest --version`; `uv run pytest --collect-only`.
- reviewer focus: `code-reviewer` for dependency/config correctness and minimality.
- 必須出力: changed files, verification results, lock update rationale.
- 停止条件: dependency resolution failure, network/cache issue that cannot be retried with approved path, or need for extra plugin.

#### 具体テストケース一覧
- `tc-s01-001` acceptance: pytest dependency resolves.
  - 前提: Project uses `uv` and has no pytest dependency before this migration.
  - 操作: Run `uv run pytest --version`.
  - 期待結果: Command succeeds and reports pytest.
  - 失敗検出: Local and CI commands cannot execute pytest.
  - 検証方法: Command result in `report.md`.
  - 関連 closure id: tc-001
- `tc-s01-002` acceptance: pytest can collect the existing lanes.
  - 前提: Pytest dependency and config are present.
  - 操作: Run `uv run pytest --collect-only`.
  - 期待結果: Collection includes `tests/unit`, `tests/integration`, and `tests/cli_runtime` without collecting wheelhouse/cache artifacts.
  - 失敗検出: pytest config is missing, too narrow, or too broad.
  - 検証方法: Command result in `report.md`.
  - 関連 closure id: tc-001

#### ステップ完了契約
- close 条件: `tc-001` passes and code-reviewer passes.
- report evidence: Step Contract Closure, Test Contract Closure, reviewer gate, commit gate.
- 残リスク: Existing tests may still be unittest-style until later steps.

#### ステップゲート
- step reviewer gate: code-reviewer pass.
- commit / no-op gate: commit only `pyproject.toml` / `uv.lock` changes.

### 実装ステップ S02 — Runtime harness pytest-native conversion
- 振る舞いの目標:
  - Runtime test helpers are usable without inheritance from `unittest.TestCase`.
- design 参照:
  - D-004 harness-first; Class / Interface detail.
- 依存: S01.
- unblock: S03.
- 対象ファイル:
  - `tests/cli_runtime/harness.py`
  - optional `tests/cli_runtime/conftest.py`
- 計画済み契約:
  - scope: convert helper boundary, skip behavior, and assertion helpers to pytest-native equivalents.
  - テスト義務: `tc-002`.
  - Red / 代替証跡: red-required via focused migrated helper smoke or existing runtime test after minimal adaptation.
  - 実装範囲:
    - allowed paths: listed target files only.
    - forbidden changes: broad runtime test migration, unit/integration tests, docs, CI, product source.
  - Green 検証: focused runtime pytest command selected by worker.
  - amendment trigger:
    - helper API cannot support downstream tests without broad product or test lane redesign.

#### 委任契約
- 委任ロール: `dev-coder`.
- 入力 docs: `requirement.md`, `design.md`, `plan.md`, `tests/cli_runtime/harness.py`.
- 許可 paths: `tests/cli_runtime/harness.py`, optional `tests/cli_runtime/conftest.py`.
- 禁止 changes: product runtime behavior, docs/CI, broad test migration.
- 受け入れ条件: no `unittest` import/TestCase/`self.assert*`/`skipTest` remains in harness.
- 必須 verification: focused pytest helper/runtime smoke; scoped grep on harness.
- reviewer focus: `code-reviewer` for helper contract and assertion preservation.
- 必須出力: changed files, helper API notes, verification result, unresolved downstream risks.
- 停止条件: allowed paths insufficient or verification cannot be run.

#### 具体テストケース一覧
- `tc-s02-001` acceptance: runtime helper smoke runs without TestCase.
  - 前提: Pytest dependency exists and harness no longer subclasses `unittest.TestCase`.
  - 操作: Run a focused pytest command for a minimal runtime/helper smoke.
  - 期待結果: Temp target setup, runtime command invocation, and gh stub behavior work.
  - 失敗検出: Hidden TestCase methods are still required.
  - 検証方法: Focused pytest command and scoped grep.
  - 関連 closure id: tc-002
- `tc-s02-002` negative: skip path is pytest-native.
  - 前提: A helper path previously used `self.skipTest`.
  - 操作: Inspect or run a focused test covering unavailable git/symlink condition where practical.
  - 期待結果: `pytest.skip` or pytest mark is used; no `skipTest` remains.
  - 失敗検出: unittest fixture API remains in helper.
  - 検証方法: Scoped grep and focused command.
  - 関連 closure id: tc-002

#### ステップ完了契約
- close 条件: `tc-002` passes, scoped grep is clean, code-reviewer passes.
- report evidence: Step/Test Contract Closure, reviewer gate, commit gate.
- 残リスク: Dependent runtime tests still migrate in S03.

#### ステップゲート
- step reviewer gate: code-reviewer pass.
- commit / no-op gate: commit harness-only changes.

### 実装ステップ S03 — Runtime / CLI regression lane migration
- 振る舞いの目標:
  - `tests/cli_runtime` is pytest-native and passes as a lane.
- design 参照:
  - D-004 downstream runtime lane; AC-004.
- 依存: S02.
- unblock: S08, S99.
- 対象ファイル:
  - `tests/cli_runtime/test_*.py`
  - optional existing `tests/cli_runtime/conftest.py`
- 計画済み契約:
  - scope: migrate runtime tests from TestCase/assert/subTest/skip/mock patterns to pytest idioms.
  - テスト義務: `tc-003`, `tc-004`, `tc-005`.
  - Red / 代替証跡: red-required by lane command and scoped grep; covered-existing for multi-case/exception conversions.
  - 実装範囲:
    - allowed paths: runtime lane test files and runtime conftest.
    - forbidden changes: unit/integration/docs/CI/product source.
  - Green 検証:
    - `uv run pytest tests/cli_runtime`
    - scoped `rg` absence for `tests/cli_runtime`
  - amendment trigger:
    - need to delete tests, add broad skip/xfail, or change product runtime to pass migrated tests.

#### 委任契約
- 委任ロール: `dev-coder`.
- 入力 docs: `requirement.md`, `design.md`, `plan.md`, runtime test files.
- 許可 paths: `tests/cli_runtime/test_*.py`, optional `tests/cli_runtime/conftest.py`.
- 禁止 changes: unit/integration/docs/CI/product source.
- 受け入れ条件: `tc-003`..`tc-005` close.
- 必須 verification: runtime lane command and scoped grep.
- reviewer focus: `code-reviewer` for assertion strength, parametrization, hermetic runtime isolation.
- 必須出力: changed files, migrated patterns, verification result, skipped/xfail rationale if any.
- 停止条件: assertion weakening, test deletion, unplanned product source change, or runtime lane cannot be verified.

#### 具体テストケース一覧
- `tc-s03-001` acceptance: runtime lane passes.
  - 前提: Harness is pytest-native.
  - 操作: Run `uv run pytest tests/cli_runtime`.
  - 期待結果: Runtime / CLI regression lane passes.
  - 失敗検出: A migrated runtime test lost helper compatibility or hermetic setup.
  - 検証方法: Command result in `report.md`.
  - 関連 closure id: tc-003
- `tc-s03-002` regression: former subTest visibility is preserved.
  - 前提: Runtime tests include repeated case loops.
  - 操作: Inspect migrated tests and run runtime lane.
  - 期待結果: `pytest.mark.parametrize` or explicit assertion messages preserve case identity.
  - 失敗検出: A single loop failure lacks case context.
  - 検証方法: Code review plus runtime lane.
  - 関連 closure id: tc-004
- `tc-s03-003` regression: exception checks remain specific.
  - 前提: Runtime tests assert failure paths.
  - 操作: Inspect migrated exception tests.
  - 期待結果: `pytest.raises(..., match=...)` or equivalent explicit result checks are used.
  - 失敗検出: Broad exception swallowing.
  - 検証方法: Code review plus runtime lane.
  - 関連 closure id: tc-005

#### ステップ完了契約
- close 条件: runtime lane passes, scoped grep clean, code-reviewer passes.
- report evidence: Step/Test Contract Closure, Closure Coverage for `tc-003`..`tc-005`.
- 残リスク: Unit and docs/CI lanes remain to migrate.

#### ステップゲート
- step reviewer gate: code-reviewer pass.
- commit / no-op gate: commit runtime lane migration only.

### 実装ステップ S04 — Small / medium unit package migration
- 振る舞いの目標:
  - Unit packages outside large infra migrate to pytest idioms and pass by package group.
- design 参照:
  - D-004; unit group migration before large infra file.
- 依存: S01.
- unblock: S05, S08.
- 対象ファイル:
  - `tests/unit/application/**`
  - `tests/unit/cli/**`
  - `tests/unit/commands/**`
  - `tests/unit/domain/**`
  - `tests/unit/presentation/**`
  - `tests/unit/test_discovery.py`
  - optional `tests/unit/conftest.py`
- 計画済み契約:
  - scope: migrate lower-risk unit tests; keep large infra for S05.
  - テスト義務: `tc-006`, plus `tc-004` / `tc-005` where applicable.
  - Red / 代替証跡: red-required by focused package commands and scoped grep.
  - 実装範囲:
    - allowed paths: listed unit package paths.
    - forbidden changes: `tests/unit/infra/test_init_update.py`, docs, CI, runtime/product source.
  - Green 検証:
    - `uv run pytest tests/unit/application tests/unit/domain`
    - `uv run pytest tests/unit/cli tests/unit/commands tests/unit/presentation tests/unit/test_discovery.py`
  - amendment trigger:
    - shared fixture need that crosses into infra/runtime or requires product source change.

#### 委任契約
- 委任ロール: `dev-coder`.
- 入力 docs: `requirement.md`, `design.md`, `plan.md`, target unit files.
- 許可 paths: listed target paths only.
- 禁止 changes: infra large file, docs/CI, runtime/product source.
- 受け入れ条件: `tc-006` closes and scoped grep is clean for target paths.
- 必須 verification: package-group pytest commands.
- reviewer focus: `code-reviewer` for assertion strength and mock/monkeypatch scope.
- 必須出力: changed files, verification result, deferred infra grep note.
- 停止条件: changes need large infra file or docs/CI command-string cutover.

#### 具体テストケース一覧
- `tc-s04-001` acceptance: lower-risk unit groups pass.
  - 前提: Pytest dependency exists.
  - 操作: Run focused package-group pytest commands.
  - 期待結果: Target unit groups, including `tests/unit/commands`, pass under pytest.
  - 失敗検出: Unit migration breaks application/domain/cli/commands/presentation behavior.
  - 検証方法: Commands in `report.md`.
  - 関連 closure id: tc-006
- `tc-s04-002` regression: mock migration avoids `unittest.mock`.
  - 前提: Some target tests previously patched collaborators.
  - 操作: Inspect target paths and run scoped grep.
  - 期待結果: Patching uses `monkeypatch`, local fakes, or pytest fixtures; no `from unittest` import remains.
  - 失敗検出: Permanent `unittest.mock` dependency remains.
  - 検証方法: Scoped grep and code review.
  - 関連 closure id: tc-006

#### ステップ完了契約
- close 条件: target package commands pass, scoped grep clean, code-reviewer passes.
- report evidence: Step/Test Contract Closure, Closure Coverage.
- 残リスク: Large infra file handled in S05.

#### ステップゲート
- step reviewer gate: code-reviewer pass.
- commit / no-op gate: commit target unit package migration only.

### 実装ステップ S05 — Large installer/update unit migration
- 振る舞いの目標:
  - The large infra unit tests migrate without weakening generated-file and command-contract assertions.
- design 参照:
  - D-004 dedicated step for `tests/unit/infra/test_init_update.py`.
- 依存: S04.
- unblock: S08, S90.
- 対象ファイル:
  - `tests/unit/infra/test_init_update.py`
  - `tests/unit/infra/test_fake_gh_harness.py`
  - `tests/unit/infra/test_active_store.py`
  - optional `tests/unit/infra/conftest.py`
- 計画済み契約:
  - scope: migrate infra tests and helpers; command-string expectation updates wait for S90 unless inseparable and reviewed as part of docs/CI cutover.
  - テスト義務: `tc-007`, `tc-005`.
  - Red / 代替証跡: red-required by infra lane and full unit lane.
  - 実装範囲:
    - allowed paths: listed infra paths.
    - forbidden changes: docs/CI except explicitly deferred command-string tests, product source, runtime optimization.
  - Green 検証:
    - `uv run pytest tests/unit/infra`
    - `uv run pytest tests/unit`
  - amendment trigger:
    - assertion weakening, test deletion, skip/xfail addition, or command-string update that cannot wait for S90.

#### 委任契約
- 委任ロール: `dev-coder`.
- 入力 docs: `requirement.md`, `design.md`, `plan.md`, infra target files.
- 許可 paths: listed infra paths.
- 禁止 changes: docs/CI/product source except approved command-string handling per plan.
- 受け入れ条件: `tc-007` closes.
- 必須 verification: infra lane then unit lane.
- reviewer focus: `code-reviewer` for large mechanical conversion, assertion strength, and generated asset checks.
- 必須出力: changed files, conversion strategy summary, verification result, any deferred S90 notes.
- 停止条件: migration requires deleting tests, weakening assertions, or broad docs/CI changes.

#### 具体テストケース一覧
- `tc-s05-001` acceptance: infra and unit lanes pass.
  - 前提: Small/medium unit groups are already pytest-native.
  - 操作: Run `uv run pytest tests/unit/infra` and `uv run pytest tests/unit`.
  - 期待結果: Both commands pass.
  - 失敗検出: Large infra migration breaks installer/update behavior assertions.
  - 検証方法: Command results in `report.md`.
  - 関連 closure id: tc-007
- `tc-s05-002` regression: generated-file assertions keep strength.
  - 前提: Infra tests check generated scaffolds and command strings.
  - 操作: Inspect representative converted assertions during review.
  - 期待結果: Equality/containment/path checks remain explicit, not broad truthiness checks.
  - 失敗検出: Mechanical conversion weakens assertions.
  - 検証方法: code-reviewer review notes.
  - 関連 closure id: tc-007

#### ステップ完了契約
- close 条件: infra and unit lanes pass, code-reviewer passes.
- report evidence: Step/Test Contract Closure, Closure Coverage, reviewer gate.
- 残リスク: Docs/CI command strings still close in S90.

#### ステップゲート
- step reviewer gate: code-reviewer pass.
- commit / no-op gate: commit infra unit migration only.

### 実装ステップ S06 — Integration lane migration
- 振る舞いの目標:
  - Integration smoke remains a pytest-native lane.
- design 参照:
  - AC-003; integration lane contract.
- 依存: S01.
- unblock: S08, S99.
- 対象ファイル:
  - `tests/integration/test_discovery.py`
  - package markers only if collection evidence requires.
- 計画済み契約:
  - scope: migrate integration discovery smoke to pytest functions/classes without live external dependency.
  - テスト義務: `tc-008`.
  - Red / 代替証跡: red-required by integration lane and scoped grep.
  - 実装範囲:
    - allowed paths: listed integration paths.
    - forbidden changes: live network, credentials, provider CI scope reduction below full suite.
  - Green 検証: `uv run pytest tests/integration`.
  - amendment trigger:
    - integration lane needs live external services or broader behavior changes.

#### 委任契約
- 委任ロール: `dev-coder`.
- 入力 docs: `requirement.md`, `design.md`, `plan.md`, integration target file.
- 許可 paths: listed integration paths.
- 禁止 changes: live external integration behavior and credentialed dependencies.
- 受け入れ条件: `tc-008` closes.
- 必須 verification: `uv run pytest tests/integration`; scoped grep.
- reviewer focus: `code-reviewer` for hermeticity and pytest-native style.
- 必須出力: changed files, verification result, unresolved risks.
- 停止条件: live external dependency required.

#### 具体テストケース一覧
- `tc-s06-001` acceptance: integration lane passes.
  - 前提: Pytest dependency exists.
  - 操作: Run `uv run pytest tests/integration`.
  - 期待結果: Integration lane passes without unittest imports.
  - 失敗検出: Integration lane is accidentally dropped or kept as unittest-only.
  - 検証方法: Command result and scoped grep.
  - 関連 closure id: tc-008

#### ステップ完了契約
- close 条件: integration lane passes, scoped grep clean, code-reviewer passes.
- report evidence: Step/Test Contract Closure, reviewer gate, commit gate.
- 残リスク: None specific.

#### ステップゲート
- step reviewer gate: code-reviewer pass.
- commit / no-op gate: commit integration migration only.

### 実装ステップ S08 — Unittest absence cleanup and lane consolidation
- 振る舞いの目標:
  - Test implementation is no longer unittest-dependent and all lanes pass.
- design 参照:
  - AC-006; EC-006; final contract checks.
- 依存: S03, S05, S06.
- unblock: S90, S99.
- 対象ファイル:
  - `tests/**` only for cleanup caused by previous migration steps.
- 計画済み契約:
  - scope: remove leftover unittest artifacts and collection cleanup only.
  - テスト義務: `tc-009`.
  - Red / 代替証跡: inspect-only grep absence plus lane command confirmation.
  - 実装範囲:
    - allowed paths: tests cleanup only.
    - forbidden changes: new feature tests, docs/CI cutover, runtime optimization, product source.
  - Green 検証:
    - `uv run pytest tests/unit`
    - `uv run pytest tests/integration`
    - `uv run pytest tests/cli_runtime`
    - grep absence for tests.
  - amendment trigger:
    - remaining unittest import must be preserved, or cleanup needs docs/CI/product changes.

#### 委任契約
- 委任ロール: `dev-coder`.
- 入力 docs: `requirement.md`, `design.md`, `plan.md`, migrated tests.
- 許可 paths: tests cleanup only.
- 禁止 changes: docs/CI/product source/new feature tests.
- 受け入れ条件: `tc-009` closes.
- 必須 verification: all lane commands and grep absence.
- reviewer focus: `code-reviewer` for cleanup minimality and no coverage shrink.
- 必須出力: changed files, grep result, lane verification, skipped/xfail audit.
- 停止条件: any permanent unittest exception or assertion weakening needed.

#### 具体テストケース一覧
- `tc-s08-001` acceptance: no unittest dependency remains in tests.
  - 前提: S02..S06 migrations are complete.
  - 操作: Run `rg -n "unittest|self\\.assert|assertRaises|subTest|unittest\\.main|from unittest|import unittest" tests`.
  - 期待結果: No migration-blocking matches remain.
  - 失敗検出: Pytest only collects leftover unittest-style tests.
  - 検証方法: Grep result in `report.md`.
  - 関連 closure id: tc-009
- `tc-s08-002` acceptance: all lanes still pass after cleanup.
  - 前提: Cleanup has not changed product behavior.
  - 操作: Run all three lane commands.
  - 期待結果: Unit, integration, and runtime lanes pass.
  - 失敗検出: Cleanup removed required helpers or tests.
  - 検証方法: Command results in `report.md`.
  - 関連 closure id: tc-009

#### ステップ完了契約
- close 条件: all lane commands pass, grep absence passes, code-reviewer passes.
- report evidence: Step/Test Contract Closure, Closure Coverage, reviewer gate.
- 残リスク: Docs/CI official command contract still closes in S90.

#### ステップゲート
- step reviewer gate: code-reviewer pass.
- commit / no-op gate: commit cleanup only, or approved-no-op with clean grep evidence.

### ドキュメント影響の解消ステップ S90 — Docs / CI cutover
- 振る舞いの目標:
  - README, AGENTS, provider CI, and command-string tests use pytest commands and current lane layout, with GitHub Actions running the full suite.
- design 参照:
  - AC-002 / AC-007; D-002 provider CI full-suite pytest contract; docs / CI file plan.
- 依存: S08.
- unblock: S99.
- 対象:
  - `README.md`
  - `AGENTS.md`
  - `.github/workflows/provider-ci.yml`
  - tests asserting docs / CI command strings.
- 対応:
  - `doc-writer` updates README / AGENTS test commands and stale layout references.
  - `dev-coder` updates provider CI and command-string assertions when they are code/test artifacts.
  - Provider CI / GitHub Actions runs `uv run pytest` so unit, integration, and runtime / CLI regression lanes are all included.
- doc update owner:
  - `doc-writer` for docs text.
  - `dev-coder` for workflow/test assertions.
- spec/doc review:
  - reviewer: `spec-reviewer`
  - pass 条件: docs / CI contract matches requirement, design, and plan.
- code review:
  - reviewer: `code-reviewer`
  - pass 条件: workflow/test assertion changes are minimal and executable.

#### 計画済み契約
- テスト義務: `tc-010`.
- Red / 代替証跡: inspect-only grep and command-string tests.
- Green 検証:
  - docs/CI grep for stale unittest commands.
  - `uv run pytest` as the local equivalent of provider CI full-suite execution.
- amendment trigger:
  - Need to reduce provider CI below full suite, edit shipped consumer CI, or rewrite unrelated docs.

#### 委任契約
- 委任ロール: `doc-writer` and `dev-coder` as separate bounded workers if both docs and tests/workflow change.
- 入力 docs: `requirement.md`, `design.md`, `plan.md`, README / AGENTS / provider CI.
- 許可 paths: listed target paths.
- 禁止 changes: shipped consumer CI, unrelated docs cleanup, CI scope reduction below full suite.
- 受け入れ条件: `tc-010` closes.
- 必須 verification: grep and relevant unit tests.
- reviewer focus: spec-reviewer docs/spec alignment; code-reviewer workflow/test behavior.
- 必須出力: changed files, verification result, docs/spec notes, unresolved risks.
- 停止条件: docs/CI contract conflicts with implementation evidence.

#### 具体テストケース一覧
- `tc-s90-001` inspect-only: stale unittest commands are gone from official docs/CI.
  - 前提: Test implementation is pytest-native.
  - 操作: Run grep for `unittest discover`, `Framework: unittest`, and stale root test paths in README / AGENTS / workflows / tests.
  - 期待結果: No stale official contract remains except historical discussion/spec evidence if explicitly out of grep scope.
  - 失敗検出: Contributors or CI are still pointed to unittest.
  - 検証方法: Grep result in `report.md`.
  - 関連 closure id: tc-010
- `tc-s90-002` acceptance: provider CI full-suite command is executable locally.
  - 前提: `.github/workflows/provider-ci.yml` uses pytest for the full suite.
  - 操作: Run `uv run pytest`.
  - 期待結果: Command passes and covers pytest collection for unit, integration, and runtime / CLI tests.
  - 失敗検出: CI command diverges from local dependency setup or only runs a subset.
  - 検証方法: Full-suite command result.
  - 関連 closure id: tc-010

#### ステップ完了契約
- close 条件: `tc-010` passes, required reviewers pass.
- report evidence: Step/Test Contract Closure, docs/spec review, code review, commit gate.
- 残リスク: Full-suite proof remains in S99.

#### ステップゲート
- step reviewer gate: code-reviewer and spec-reviewer pass as applicable.
- commit / no-op gate: commit docs/CI cutover as one coherent runner-contract step, or split if reviewer requires.

### 最終品質ゲートステップ S99 — Final quality gate
- branch diff 範囲:
  - pytest dependency/config, tests migration, docs/CI full-suite cutover, issue report evidence.
- 必須 validation:
  - `uv run pytest --version`
  - `uv run pytest --collect-only`
  - `uv run pytest tests/unit`
  - `uv run pytest tests/integration`
  - `uv run pytest tests/cli_runtime`
  - `uv run pytest`
  - `rg -n "unittest|self\\.assert|assertRaises|subTest|unittest\\.main|from unittest|import unittest" tests`
  - `rg -n "unittest discover|Framework: \`unittest\`|tests/test_cli.py|tests/test_init_update.py" README.md AGENTS.md .github/workflows tests`
  - `git diff --check`
- final QA gate:
  - reviewer: `qa-reviewer`
  - 範囲: obligation coverage, assertion strength, integration/manual test need, skip/xfail audit.
  - pass 条件: reviewer pass.
- final code review ゲート:
  - reviewer: issue-wide `code-reviewer`
  - 範囲: integrated diff, helper/fixture boundaries, dependency/config/CI coherence, product runtime non-change.
  - pass 条件: `review_status: pass`.
- final spec review ゲート:
  - reviewer: final `spec-reviewer`
  - 範囲: requirement / design / plan / report / implementation / tests / docs alignment, AC-001..AC-009, parent Epic deferred lane trace.
  - pass 条件: reviewer pass.
- final commit gate:
  - commit 範囲: final report ledger and any final bounded fixes after reviewers pass.
  - final report ledger: Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta, Final QA Gate, Final Code Review Gate, Final Spec Review Gate, final commit scope.
  - post-commit external evidence destination: final response / PR body / issue comment with commit hash and clean status.

#### 具体テストケース一覧
- `tc-s99-001` acceptance: full pytest fallback passes.
  - 前提: All implementation steps and docs/CI cutover are complete.
  - 操作: Run `uv run pytest`.
  - 期待結果: Full suite passes.
  - 失敗検出: A lane-local pass hides cross-lane failure.
  - 検証方法: Command result and duration if material.
  - 関連 closure id: tc-011
- `tc-s99-002` inspect-only: no stale runner contract remains.
  - 前提: S90 completed.
  - 操作: Run final grep absence commands.
  - 期待結果: No migration-blocking matches remain in scoped targets.
  - 失敗検出: Official fallback to unittest remains.
  - 検証方法: Grep results.
  - 関連 closure id: tc-009, tc-010
- `tc-s99-003` manual-required: final reviewers pass.
  - 前提: Commands and report evidence are ready.
  - 操作: Run `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer`.
  - 期待結果: All reviewers pass; any fail triggers bounded fix and fresh re-review.
  - 失敗検出: Test sufficiency, code integration, or spec alignment gap.
  - 検証方法: Reviewer output recorded in `report.md`.
  - 関連 closure id: tc-012

## 未確定事項
- Blocking questions:
  - なし。
- Plan-level assumptions fixed by design:
  - pytest dependency source is `dependency-groups.dev`.
  - `unittest.mock` is not a permanent exception.
- GitHub Actions / provider CI runs `uv run pytest` full suite.

## 最終完了条件
- AC/EC 達成:
  - AC-001..AC-009 and EC-001..EC-007 are closed in Closure Coverage.
- docs 影響解決:
  - S90 completed with docs/spec alignment pass.
- 全 implementation step 完了:
  - S00..S90 are `committed` or justified `approved-no-op`.
- final quality gate pass:
  - S99 commands pass.
  - `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer` pass.
- report / lifecycle:
  - `report.md` records all required evidence before `issue finish`.
  - Final commit external evidence records commit hash and clean worktree status after commit.
