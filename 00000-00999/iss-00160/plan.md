---
種別: 実装計画書（Issue）
ID: "iss-00160"
タイトル: "Reduce Test Runtime Followup"
関連GitHub: ["#160"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-05"
依存: ["requirement.md", "design.md"]
親: ["epic-00080", "init-00079"]
---

# iss-00160 Reduce Test Runtime Followup — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001: Unit / integration directory taxonomy and discovery command.
  - AC-002: `tests/unit/` local runtime <= 120 seconds.
  - AC-003: fake `gh` fixture minimization and large-limit / large-number coverage.
  - AC-004: Heavy CLI coverage split into CLI smoke and lower-layer direct tests.
  - AC-005: Full regression fallback remains available.
- EC:
  - EC-001: Real GitHub / remote git / auth / network tests are integration-only.
  - EC-002: Large index behavior is represented without routine 10000-record generation.
  - EC-003: Deterministic local git adapter smoke can remain Unit.
  - EC-004: Existing dogfooding snapshot divergence is reported separately if full fallback still fails.
- 制約:
  - No production behavior change solely for speed.
  - No external credential / network in `tests/unit/`.
  - No third category beyond `tests/unit/` and `tests/integration/`.

## 依存関係から導く実装順序
- 依存関係の正本:
  - `design.md` の Test Suite Boundary and Layer Mapping。
  - `design.md` の Command 別 coverage split 契約。
- 順序ルール:
  - First create discoverable suite boundaries.
  - Then fix shared heavy fixture defaults.
  - Then migrate low-risk existing layer tests.
  - Then split slow command groups from highest measured cost.
  - Then measure and close remaining hotspots until `tests/unit/` <= 120 seconds.
- step 依存サマリー:
  - S01:
    - 依存: requirement / design reviewed pass.
    - unblock: S02-S06.
    - 対象ファイル: `tests/`.
  - S02:
    - 依存: S01 directories / discover command.
    - unblock: S03-S06.
    - 対象ファイル: test harness / fake `gh` tests.
  - S03:
    - 依存: S01.
    - unblock: S06 measurement completeness.
    - 対象ファイル: low-risk domain / presentation / installer placement.
  - S04:
    - 依存: S02.
    - unblock: S06 runtime target.
    - 対象ファイル: deps / validate tests.
  - S05:
    - 依存: S02.
    - unblock: S06 runtime target.
    - 対象ファイル: delegated authoring / active tests.
  - S06:
    - 依存: S02-S05.
    - unblock: S90/S99.
    - 対象ファイル: sync / new tests and remaining hotspots.

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - `python -m unittest discover -s tests/unit` and `python -m unittest discover -s tests/integration` are valid commands.
  - 依存:
    - design pass.
  - unblock:
    - all test moves and measurements.
  - 対象ファイル:
    - `tests/unit/**`, `tests/integration/**`, package init files.
  - 閉じる要件:
    - AC-001, AC-005 partial.
  - レビューゲート:
    - code-reviewer.
- S02:
  - 観測可能な振る舞い:
    - fake `gh` default no longer generates 10000 issues; large limit / large number / state coverage remains explicit.
  - 依存:
    - S01.
  - unblock:
    - heavy command migration.
  - 対象ファイル:
    - `tests/**/harness.py`, fake `gh` harness tests.
  - 閉じる要件:
    - AC-003, EC-002.
  - レビューゲート:
    - code-reviewer.
- S03:
  - 観測可能な振る舞い:
    - Existing low-risk tests are placed under runtime-layer-mapped Unit paths without behavior loss.
  - 依存:
    - S01.
  - unblock:
    - AC-001 full layout closure.
  - 対象ファイル:
    - `tests/domain_runtime/**`, `tests/presentation_runtime/**`, `tests/test_cli.py`, `tests/test_init_update.py`.
  - 閉じる要件:
    - AC-001, AC-005 partial.
  - レビューゲート:
    - code-reviewer.
- S04:
  - 観測可能な振る舞い:
    - `deps` and `validate` heavy behavior are covered by lower-layer tests while CLI smoke remains.
  - 依存:
    - S02.
  - unblock:
    - runtime reduction.
  - 対象ファイル:
    - `tests/cli_runtime/test_deps.py`, `tests/cli_runtime/test_validate.py`, new/moved tests under `tests/unit/{cli,commands,application,domain,infra,presentation}`.
  - 閉じる要件:
    - AC-004, EC-002.
  - レビューゲート:
    - code-reviewer.
- S05:
  - 観測可能な振る舞い:
    - `delegated authoring` and `active` heavy behavior are covered by lower-layer tests while CLI smoke remains.
  - 依存:
    - S02.
  - unblock:
    - runtime reduction.
  - 対象ファイル:
    - `tests/cli_runtime/test_delegated_authoring.py`, `tests/cli_runtime/test_active.py`, new/moved tests under `tests/unit/{cli,commands,application,domain,infra}`.
  - 閉じる要件:
    - AC-004, EC-003.
  - レビューゲート:
    - code-reviewer.
- S06:
  - 観測可能な振る舞い:
    - `sync` and `new` coverage is split; `tests/unit/` completes within 120 seconds.
  - 依存:
    - S02-S05.
  - unblock:
    - final gates.
  - 対象ファイル:
    - `tests/cli_runtime/test_sync.py`, `tests/cli_runtime/test_new.py`, remaining hotspot tests, `report.md`.
  - 閉じる要件:
    - AC-002, AC-004, EC-001, EC-003, EC-004.
  - レビューゲート:
    - code-reviewer.
- S90:
  - 観測可能な振る舞い:
    - External docs / templates that mention test commands are consistent with the new unit/integration commands.
  - 閉じる要件:
    - AC-001, AC-005.
  - レビューゲート:
    - spec-reviewer when docs changed.
- S99:
  - 観測可能な振る舞い:
    - Issue-wide QA, code review, spec review pass; final measurements are recorded.
  - 閉じる要件:
    - all AC/EC.
  - レビューゲート:
    - qa-reviewer, code-reviewer, spec-reviewer.

## 要件 ↔ ステップ対応
- AC-001 -> S01, S03, S90.
- AC-002 -> S06, S99.
- AC-003 -> S02.
- AC-004 -> S04, S05, S06.
- AC-005 -> S01, S03, S90, S99.
- EC-001 -> S06, S99.
- EC-002 -> S02.
- EC-003 -> S05.
- EC-004 -> S99.

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ（step） | スライス（slice） | 種別（type） | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル（evidence level） | クロージャ証跡（closure evidence） |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-s01-001 | S01 | suite-boundary | acceptance | AC-001 | `tests/unit` and `tests/integration` are discoverable directories with required subdirs | `python -m unittest discover -s tests/unit`; `python -m unittest discover -s tests/integration` | suite boundary drift | yes | red-required | report step closure |
| tc-s01-002 | S01 | full-fallback | acceptance | AC-005 | `python -m unittest discover` remains available | full discovery command or command inspection | fallback removal | yes | covered-existing | report step closure |
| tc-s02-001 | S02 | fake-gh-default | acceptance | AC-003 / EC-002 | default fake `gh issue list` returns small fixture, not 10000 records | targeted harness test | routine large fixture regression | yes | red-required | report step closure |
| tc-s02-002 | S02 | gh-limit-contract | acceptance | AC-003 / EC-002 | `--gh-limit=10000` is verified by captured argv | targeted test invoking command with `--gh-limit=10000` | limit coverage loss | yes | red-required | report step closure |
| tc-s02-003 | S02 | large-number-minimal | edge | AC-003 / EC-002 | issue `number: 10000` behavior uses minimal fixture | targeted test fixture with one or few issues | large number regression | yes | red-required | report step closure |
| tc-s02-004 | S02 | state-variation-minimal | edge | AC-003 / EC-002 | missing / unknown / open / closed behavior is represented with 2-3 issue fixtures, not 10000 generated issues | targeted fake `gh` / status interpretation tests | state coverage loss after fixture shrink | yes | red-required | report step closure |
| tc-s03-001 | S03 | low-risk-placement | acceptance | AC-001 | domain/presentation/installer tests live under mapped Unit paths | file layout inspection and discover run | misplaced tests | yes | inspect-only | report step closure |
| tc-s04-001 | S04 | deps-split | acceptance | AC-004 | deps CLI smoke remains and graph/status logic has direct tests | targeted deps tests | CLI-only branch-heavy coverage | yes | red-required | report step closure |
| tc-s04-002 | S04 | validate-split | acceptance | AC-004 | validate CLI smoke remains and validation rules have direct tests | targeted validate tests | coverage loss in validation rules | yes | red-required | report step closure |
| tc-s05-001 | S05 | delegated-authoring-split | acceptance | AC-004 | delegated authoring CLI smoke remains and diff guard policy has lower-layer tests | targeted delegated authoring tests | subprocess-heavy policy regression | yes | red-required | report step closure |
| tc-s05-002 | S05 | active-split | acceptance | AC-004 / EC-003 | active CLI smoke remains and active resolution / local store behavior has lower-layer tests | targeted active tests | active state coverage loss | yes | red-required | report step closure |
| tc-s06-001 | S06 | sync-split | acceptance | AC-004 | sync CLI smoke remains and projections/status/rendering have lower-layer tests | targeted sync tests | sync branch coverage loss | yes | red-required | report step closure |
| tc-s06-002 | S06 | new-split | acceptance | AC-004 | new CLI smoke remains and create/scope/post-sync behavior has lower-layer tests | targeted new tests | new command branch coverage loss | yes | red-required | report step closure |
| tc-s06-003 | S06 | unit-runtime | acceptance | AC-002 | `tests/unit/` completes within 120 seconds | timed unit command | slow feedback loop persists | yes | manual-required | report measurement |
| tc-s06-004 | S06 | external-boundary | edge | EC-001 | no real GitHub / remote git / auth / network required by unit suite | `rg` inspection and unit command | external dependency leakage | yes | inspect-only | report step closure |
| tc-s90-001 | S90 | docs-command-consistency | acceptance | AC-001 / AC-005 | docs/templates mentioning test commands are consistent or no update needed | `rg` inspection | stale docs | yes | inspect-only | report docs gate |
| tc-s99-001 | S99 | final-gates | acceptance | all | QA/code/spec reviews pass and final evidence is recorded | reviewer outputs and final commands | incomplete closure | yes | manual-required | final quality gate |

## レビュー / QA ゲート方針
- RG1 step review:
  - 実施タイミング: 各 implementation step の commit 前。
  - reviewer: code-reviewer for code/tests/scaffold behavior; spec-reviewer for docs-only changes.
  - pass 条件: review_status: pass。
- QG1 final QA:
  - reviewer: qa-reviewer。
  - 範囲: closure ID coverage、test sufficiency、unit/integration separation、120 秒 measurement。
- SG1 final spec review:
  - reviewer: spec-reviewer。
  - 範囲: requirement / design / plan / report / implementation / tests / docs 整合。

## 実行ルール（全ステップ共通）
- 実装は dev-coder に委任する。
- Main orchestrator は source code / tests を直接編集しない。
- Each step must update `report.md` with:
  - Red / alternative evidence。
  - Green verification。
  - Closure coverage。
  - Reviewer verdict。
  - Any known failure not caused by the step。
- If a step cannot preserve coverage while meeting speed target, stop and amend plan before continuing.
- If full regression fallback fails only due to known dogfooding `.meta.json` snapshot divergence, record EC-004 evidence and do not treat it as AC-002 failure.

## 実装ステップ

### 実装ステップ S01 — Unit / Integration Discovery Boundary
- 振る舞いの目標（behavior goal）:
  - `tests/unit/` and `tests/integration/` exist with required layer / boundary subdirs and are discoverable by unittest.
- design 参照:
  - Directory / file change plan; Test discovery interface.
- 依存:
  - requirement and design reviewer pass.
- unblock:
  - S02-S06.
- 対象ファイル:
  - `tests/unit/**`
  - `tests/integration/**`
  - existing package init files only as needed.
- 計画済み契約（planned contract）:
  - scope:
    - Create required directories and package files.
    - Keep `python -m unittest discover` available as fallback.
  - テスト義務:
    - closure id:
      - tc-s01-001
      - tc-s01-002
  - Red / 代替証跡の要件:
    - red-required:
      - Before creating directories, `python -m unittest discover -s tests/unit` is expected to fail or discover nothing; record actual result if used.
    - covered-existing:
      - `python -m unittest discover` is existing fallback; record command availability.
  - 実装範囲:
    - allowed paths:
      - `tests/unit/**`, `tests/integration/**`, `tests/__init__.py` if needed.
    - forbidden changes:
      - Production code.
      - Test behavior migration beyond discover boundary.
  - Green 検証:
    - `python -m unittest discover -s tests/unit`
    - `python -m unittest discover -s tests/integration`
    - `python -m unittest discover` command availability or focused smoke if full run is deferred.
  - report 証跡の記録先:
    - `report.md` S01 session log and closure tables.
  - amendment trigger:
    - unittest discovery requires a non-standard runner or third category.

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - dev-coder
- 入力 docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
- 許可 paths:
  - `tests/unit/**`
  - `tests/integration/**`
  - `tests/__init__.py`
- 禁止 changes:
  - Production code.
  - Existing test behavior rewrites.
- 受け入れ条件:
  - tc-s01-001 and tc-s01-002 closed.
- 必須 tests または docs-only verification:
  - `python -m unittest discover -s tests/unit`
  - `python -m unittest discover -s tests/integration`
- 必須出力:
  - changed files, commands run, closure evidence, unresolved risks.
- 停止条件:
  - Discovery cannot be made valid without changing production behavior.

### 実装ステップ S02 — fake `gh` Fixture Contract
- 振る舞いの目標:
  - Default fake `gh` is small; large limit, large number, and status variations are explicit tests.
- design 参照:
  - fake `gh` harness interface; Command split for deps / sync.
- 依存:
  - S01.
- unblock:
  - S04-S06.
- 対象ファイル:
  - `tests/**/harness.py`
  - `tests/unit/infra/**`
  - existing tests that assume 10000 default.
- 計画済み契約:
  - scope:
    - Change default fake `gh issue list` fixture to minimal relevant data.
    - Add or adjust tests for argv `--limit 10000`, `number: 10000`, and missing / unknown / open / closed state variations.
  - テスト義務:
    - tc-s02-001, tc-s02-002, tc-s02-003, tc-s02-004.
  - Red / 代替証跡の要件:
    - red-required:
      - A targeted test must fail or characterize the old 10000 default / missing argv capture before green, unless existing test already proves the old behavior.
  - 実装範囲:
    - allowed paths:
      - `tests/cli_runtime/harness.py`
      - `tests/unit/infra/**`
      - `tests/unit/application/**`
      - `tests/unit/domain/**`
      - `tests/unit/cli/**`
      - Existing deps/sync/new/active test files only when needed to replace assumptions about the old 10000-record fake `gh` default.
    - forbidden changes:
      - Production `github_cli.py` behavior unless a real bug unrelated to speed is discovered and plan is amended.
      - Unrelated test rewrites outside fake `gh` fixture contract.
  - Green 検証:
    - Targeted fake `gh` harness tests.
    - Targeted deps/sync tests that exercise `--gh-limit`.
  - report 証跡の記録先:
    - `report.md` S02 session log.
  - amendment trigger:
    - A production contract actually depends on 10000 generated records.

### 実装ステップ S03 — Low-Risk Layer Placement
- 振る舞いの目標:
  - Low-risk existing tests are moved into the accepted layer layout.
- design 参照:
  - Directory / file change plan.
- 依存:
  - S01.
- unblock:
  - AC-001 layout closure.
- 対象ファイル:
  - `tests/domain_runtime/**` -> `tests/unit/domain/**`
  - `tests/presentation_runtime/**` -> `tests/unit/presentation/**`
  - `tests/test_cli.py` -> `tests/unit/cli/test_cli.py`
  - `tests/test_init_update.py` -> `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - scope:
    - Move/classify files and update imports.
    - Preserve existing assertions.
  - テスト義務:
    - tc-s03-001.
  - Red / 代替証跡の要件:
    - inspect-only:
      - File placement inspection is sufficient for placement; behavior is checked by discover commands.
  - 実装範囲:
    - allowed paths:
      - listed test files and package init files.
    - forbidden changes:
      - Assertion weakening.
      - Production code changes.
  - Green 検証:
    - `python -m unittest discover -s tests/unit/domain`
    - `python -m unittest discover -s tests/unit/presentation`
    - `python -m unittest discover -s tests/unit/cli`
    - `python -m unittest discover -s tests/unit/infra`
  - report 証跡の記録先:
    - `report.md` S03 session log.
  - amendment trigger:
    - Large installer file move creates import/discovery cost or package conflict requiring a different placement.

### 実装ステップ S04 — `deps` / `validate` Heavy Coverage Split
- 振る舞いの目標:
  - `deps` and `validate` branch-heavy behavior is covered below CLI while representative CLI contract remains.
- design 参照:
  - Command 別 coverage split 契約: `deps`, `validate`.
- 依存:
  - S02.
- unblock:
  - Unit runtime target.
- 対象ファイル:
  - `tests/cli_runtime/test_deps.py`
  - `tests/cli_runtime/test_validate.py`
  - `tests/unit/cli/**`
  - `tests/unit/commands/**`
  - `tests/unit/application/**`
  - `tests/unit/domain/**`
  - `tests/unit/infra/**`
  - `tests/unit/presentation/**`
- 計画済み契約:
  - scope:
    - Keep representative CLI smoke for deps and validate.
    - Move dependency graph/status and validation rules to direct application/domain/infra/presentation tests.
  - テスト義務:
    - tc-s04-001, tc-s04-002.
  - Red / 代替証跡の要件:
    - red-required:
      - New direct tests should fail before the corresponding direct invocation or fixture correction when practical.
    - covered-existing:
      - Existing CLI tests may be used as characterization before split.
  - 実装範囲:
    - allowed paths:
      - listed tests only.
    - forbidden changes:
      - Production behavior changes.
      - Removing CLI smoke without replacement.
  - Green 検証:
    - Targeted deps tests.
    - Targeted validate tests.
    - `python -m unittest discover -s tests/unit`.
  - report 証跡の記録先:
    - `report.md` S04 session log.
  - amendment trigger:
    - Direct application/domain API is unavailable without production refactor.

### 実装ステップ S05 — `delegated authoring` / `active` Heavy Coverage Split
- 振る舞いの目標:
  - Delegated authoring and active state policy coverage is direct and lightweight; CLI smoke remains.
- design 参照:
  - Command 別 coverage split 契約: `delegated authoring`, `active`.
- 依存:
  - S02.
- unblock:
  - Unit runtime target.
- 対象ファイル:
  - `tests/cli_runtime/test_delegated_authoring.py`
  - `tests/cli_runtime/test_active.py`
  - `tests/unit/cli/**`
  - `tests/unit/commands/**`
  - `tests/unit/application/**`
  - `tests/unit/domain/**`
  - `tests/unit/infra/**`
- 計画済み契約:
  - scope:
    - Keep CLI surface rejection / representative active command smoke.
    - Move diff guard, provenance, ignored path, active resolution, active store behavior to lower layers.
  - テスト義務:
    - tc-s05-001, tc-s05-002.
  - Red / 代替証跡の要件:
    - red-required:
      - New direct tests for diff guard / active resolution should fail or characterize old subprocess-heavy path before green when practical.
  - 実装範囲:
    - allowed paths:
      - listed tests only.
    - forbidden changes:
      - Production behavior changes.
      - Local git tests that contact remote.
  - Green 検証:
    - Targeted delegated authoring tests.
    - Targeted active tests.
    - `python -m unittest discover -s tests/unit`.
  - report 証跡の記録先:
    - `report.md` S05 session log.
  - amendment trigger:
    - Direct policy tests require exposing new production API.

### 実装ステップ S06 — `sync` / `new` Split and 120 Second Measurement
- 振る舞いの目標:
  - Sync/new coverage is split and final unit suite meets 120 second target.
- design 参照:
  - Command 別 coverage split 契約: `sync`, `new`.
- 依存:
  - S02-S05.
- unblock:
  - S90/S99.
- 対象ファイル:
  - `tests/cli_runtime/test_sync.py`
  - `tests/cli_runtime/test_new.py`
  - remaining hotspot tests under `tests/**`
  - `report.md`
- 計画済み契約:
  - scope:
    - Keep representative CLI smoke for sync/new.
    - Move projection/rendering/status/ID/scope/post-sync behavior to lower-layer tests.
    - Measure `tests/unit/` runtime.
  - テスト義務:
    - tc-s06-001, tc-s06-002, tc-s06-003, tc-s06-004.
  - Red / 代替証跡の要件:
    - manual-required:
      - Record timed unit command after migration.
    - inspect-only:
      - Search `tests/unit/` for real external operations.
  - 実装範囲:
    - allowed paths:
      - listed tests and `report.md`.
    - forbidden changes:
      - Production behavior changes.
      - Moving real external tests into unit.
  - Green 検証:
    - Targeted sync tests.
    - Targeted new tests.
    - `python -m unittest discover -s tests/unit` with shell time <= 120 seconds.
    - `rg` inspection for real external operations in `tests/unit`.
  - report 証跡の記録先:
    - `report.md` S06 session log and measurement table.
  - amendment trigger:
    - Unit runtime remains > 120 seconds after planned hotspot splits.

### ドキュメント影響の解消ステップ S90（docs impact resolution / docs refresh）
- 対象:
  - README / docs / templates / workflow / skill files that mention test commands.
- 対応:
  - Run `rg -n "unittest discover|tests/unit|tests/integration|python -m unittest" README.md docs src spec-dock tests` and update persistent docs only if stale command guidance is found.
- doc update owner:
  - doc-writer when persistent non-issue docs require changes.
- spec/doc review:
  - reviewer: spec-reviewer if docs changed.
  - pass 条件: docs align with requirement / design / plan.

### 最終品質ゲートステップ S99（final quality gate）
- branch diff 範囲:
  - issue docs, tests, and any necessary test helper files.
- 必須 validation:
  - `git diff --check`
  - `./spec-dock/scripts/spec-dock validate`
  - `python -m unittest discover -s tests/unit` with shell time <= 120 seconds.
  - `python -m unittest discover` or documented full fallback execution result. If failure persists only due to known snapshot divergence, record EC-004.
- final QA gate:
  - reviewer: qa-reviewer.
  - 範囲: Issue 全体の obligation coverage と integration test 要否.
  - pass 条件: reviewer pass.
- final code review ゲート:
  - reviewer: code-reviewer.
  - 範囲: issue-wide integrated diff、構造、責務境界、回帰リスク、保守性.
  - pass 条件: review_status: pass.
- final spec review ゲート:
  - reviewer: spec-reviewer.
  - 範囲: requirement / design / plan / report / implementation / tests / docs 整合.
  - pass 条件: reviewer pass.
- final commit gate:
  - commit 範囲:
    - User request がある場合のみ commit。
  - final report ledger:
    - All closure IDs complete, no open blocking entries.
  - post-commit external evidence destination:
    - final response / GitHub issue comment if requested.

## 未確定事項
- なし。

## 最終完了条件
- AC/EC 達成:
  - AC-001〜AC-005 and EC-001〜EC-004 are closed in `report.md`.
- docs 影響解決:
  - S90 complete with updates or no-op evidence.
- 全 implementation step 完了:
  - S01-S06 committed or explicitly approved no-op.
- final quality gate pass:
  - qa-reviewer: pass.
  - issue-wide code-reviewer: pass.
  - final spec-reviewer: pass.
