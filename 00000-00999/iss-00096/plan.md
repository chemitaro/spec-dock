---
種別: 実装計画書（Issue）
ID: "iss-00096"
タイトル: "Add self update command"
関連GitHub: ["#96"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-15"
依存: ["requirement.md", "design.md"]
親: ["epic-00054", "init-local-00002"]
---

# iss-00096 Add self update command — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001, AC-002, AC-003, AC-004, AC-005
- EC:
  - EC-001, EC-002, EC-003, EC-004, EC-005
- 制約:
  - upstream source fixed to `git+https://github.com/chemitaro/spec-dock`
  - `uvx --no-cache` required
  - installer update semantics unchanged
  - failure fail-closed and subprocess exit code propagated
  - no arbitrary package source / executable option
  - no `init --force` semantics on runtime update

## マイルストーン一覧
- M1 runtime command:
  - 対象: parser / registry / command wrapper / runtime CLI tests
  - 完了条件: `update --help`、default target、explicit target、failure propagation、missing `uvx`、unsupported `--force` が targeted tests で閉じる。
- M2 docs parity:
  - 対象: README and shipped docs/templates guidance
  - 完了条件: repo-local update command、no-cache、upstream source、target default が docs と runtime help で一致する。
- M3 dogfooding mirror:
  - 対象: local consumer workspace `spec-dock/scripts/...` and generated docs mirror
  - 完了条件: provider-side asset changes are refreshed/inspected in the dogfooding mirror and `./spec-dock/scripts/spec-dock update --help` confirms the runtime command surface.
- M4 final quality:
  - 対象: checked-in dogfooding metadata snapshot parity / sync / validate / full tests / final QA, code, spec reviews
  - 完了条件: required gates が pass し、report ledger と final commit scope が記録される。

## 依存関係から導く実装順序
- 依存関係の正本:
  - `design.md` の `依存関係分析`
  - `design.md` の `Module Dependency Diagram`
  - `design.md` の `ディレクトリ / ファイル変更計画`
- 順序ルール:
  - command wrapper と parser / registry integration を先に実装し、observable CLI behavior を固定する。
  - docs は runtime behavior と help の語彙が固まってから更新する。
  - docs impact / final quality gate は implementation commits の後に実施する。
- step 依存 summary:
  - S01:
    - 依存: reviewer-pass 済み requirement / design / plan
    - unblock: S02 docs parity, S90, S99
    - 対象ファイル: runtime command files and `tests/cli_runtime/test_update.py`
  - S02:
    - 依存: S01 runtime help / command contract
    - unblock: S03 dogfooding mirror refresh, S90 docs impact resolution
    - 対象ファイル: README and shipped docs/templates
  - S03:
    - 依存: S01 runtime command, S02 docs parity
    - unblock: S04 snapshot parity, S90 docs impact resolution, S99 final quality gate
    - 対象ファイル: local dogfooding mirror under `spec-dock/scripts/...` and generated docs/templates mirror when refreshed
  - S04:
    - 依存: S03 dogfooding mirror confirmation
    - unblock: S90 docs impact resolution, S99 final quality gate
    - 対象ファイル: `tests/test_init_update.py`
  - S05:
    - 依存: final QA P2 hardening finding
    - unblock: final issue-wide code/spec review
    - 対象ファイル: `tests/cli_runtime/test_update.py`

## ステップ一覧
- S01:
  - 観測可能な振る舞い: `./spec-dock/scripts/spec-dock update [path]` が fixed `uvx --no-cache --from ... spec-dock update <target>` を実行し、exit/stdout/stderr を伝播する。
  - 依存: requirement/design/plan gate pass
  - unblock: docs wording can reference implemented help and command behavior
  - 対象ファイル: `commands/update.py`, `cli/parser.py`, `cli/registry.py`, `tests/cli_runtime/test_update.py`
  - 閉じる要件: AC-001, AC-002, AC-003, AC-004, EC-001, EC-002, EC-003, EC-004, EC-005, constraints except docs parity
  - レビューゲート: per-step `code-reviewer` pass before commit
- S02:
  - 観測可能な振る舞い: user-facing docs explain repo-local self-update, fixed upstream source, no-cache, default / explicit target consistently.
  - 依存: S01 command/help contract
  - unblock: S03 dogfooding mirror refresh, S90 docs impact resolution
  - 対象ファイル: `README.md`, `src/spec_dock/assets/spec_dock/templates/README.md`, docs discovered during docs impact inspection
  - 閉じる要件: AC-005
  - レビューゲート: per-step `code-reviewer` pass before commit; use `doc-writer` for docs update because this is a persistent non-issue-doc documentation change
- S03:
  - 観測可能な振る舞い: local dogfooding mirror reflects provider-side runtime/docs changes and `./spec-dock/scripts/spec-dock update --help` is confirmable.
  - 依存: S01, S02
  - unblock: S90 docs impact resolution and S99 final quality
  - 対象ファイル: `spec-dock/scripts/spec_dock_runtime/...`, generated `spec-dock/docs` / `spec-dock/templates` mirror files if refreshed, `spec-dock/active/issue/report.md`
  - 閉じる要件: AC-005 provider/dogfooding mirror confirmation
  - レビューゲート: per-step `code-reviewer` pass before commit; if local installer refresh produces no diff, close as valid approved-no-op with inspection evidence
- S04:
  - 観測可能な振る舞い: checked-in dogfooding `.meta.json` snapshot tests include the active issue metadata path and dependency snapshot.
  - 依存: S03 dogfooding mirror confirmation and full-suite failure evidence
  - unblock: S90 docs impact resolution and S99 final quality
  - 対象ファイル: `tests/test_init_update.py`
  - 閉じる要件: AC-005 dogfooding validation parity
  - レビューゲート: per-step `code-reviewer` pass before commit
- S05:
  - 観測可能な振る舞い: source/cache override forms for runtime `update` fail closed and do not invoke `uvx`.
  - 依存: final QA P2 hardening finding
  - unblock: final issue-wide code/spec review
  - 対象ファイル: `tests/cli_runtime/test_update.py`
  - 閉じる要件: EC-001, EC-004, fixed upstream / no arbitrary source / no cache-control option constraints
  - レビューゲート: per-step `code-reviewer` pass before commit
- S90:
  - 観測可能な振る舞い: docs / templates / README / workflow / skill / migration notes impact is resolved or explicitly justified as no update.
  - 閉じる要件: docs impact portion of AC-005
  - レビューゲート: `spec-reviewer` docs/spec alignment pass
- S99:
  - 観測可能な振る舞い: issue-wide QA, integrated code review, final spec review pass with report ledger.
  - 閉じる要件: all AC / EC / constraints and workflow completion gates
  - レビューゲート: `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`

## 要件 ↔ ステップ対応
- AC-001 -> S01
- AC-002 -> S01
- AC-003 -> S01
- AC-004 -> S01
- AC-005 -> S02, S03, S90
- AC-005 dogfooding snapshot parity -> S04
- EC-001 -> S01
- EC-002 -> S01
- EC-003 -> S01
- EC-004 -> S01
- EC-005 -> S01
- no-cache / fixed upstream / fail-closed / no arbitrary source / no force semantics -> S01, S02
- no arbitrary source / no cache-control option hardening -> S05

## Spec-Locked Closure Index（仕様固定クロージャ索引）

| id | phase / step | slice | type | spec link | locked expectation | observable input/state | bug class guarded | required | evidence level | closure evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | runtime update help | acceptance | AC-001 | `update --help` exits 0 and describes repo-local update, upstream GitHub source, no-cache, and optional target default | generated runtime script in temp managed repo; args `update --help` | command unavailable or help hides critical update source/cache contract | yes | red-required | `tests/cli_runtime/test_update.py`; report Step/Test/Closure Coverage |
| tc-002 | S01 | default target subprocess | acceptance | AC-002, EC-003 | `update` invokes `uvx --no-cache --from git+https://github.com/chemitaro/spec-dock spec-dock update <resolved cwd>` | temp managed repo with `uvx` stub on PATH; args `update` | stale uvx cache path or wrong target path used silently | yes | red-required | `tests/cli_runtime/test_update.py`; captured args evidence |
| tc-003 | S01 | explicit target subprocess | acceptance | AC-003 | explicit path is resolved and passed as installer update target | temp managed repo with `uvx` stub; args `update ../target-project` | explicit target ignored or current repo updated accidentally | yes | red-required | `tests/cli_runtime/test_update.py`; captured args evidence |
| tc-004 | S01 | subprocess failure propagation | negative | AC-004, EC-002, EC-005 | non-zero subprocess result stays non-zero and both stdout/stderr remain observable | `uvx` stub prints stdout/stderr and exits non-zero | failed upstream update reported as success or diagnostic output lost | yes | red-required | `tests/cli_runtime/test_update.py`; runtime stdout/stderr assertions |
| tc-005 | S01 | missing uvx / unsupported force | negative | EC-001, EC-004, constraints | missing `uvx` and unsupported `--force` both fail closed and do not run an alternate update path | PATH without `uvx`; parser args `update --force` | missing dependency or destructive option accepted as success | yes | red-required | `tests/cli_runtime/test_update.py`; non-zero assertions |
| tc-006 | S02 | docs parity | acceptance | AC-005 | README and shipped docs/templates explain repo-local update command, no-cache, fixed upstream source, and target default consistently | docs diff and generated scaffold docs inspection | docs teach stale-cache or installer-only path while runtime supports self-update | yes | inspect-only | docs diff; S90 spec-reviewer docs alignment |
| tc-007 | S03 | dogfooding mirror confirmation | acceptance | AC-005, dogfooding rules | local dogfooding mirror is refreshed or inspected, and `./spec-dock/scripts/spec-dock update --help` exposes the new command without live upstream update | provider asset changes after S01/S02; local dogfooding workspace in this repo | provider source passes tests but local consumer mirror remains stale | yes | inspect-only | local installer update / mirror diff / help evidence in report |
| tc-008 | S04 | dogfooding metadata snapshot parity | regression | AC-005, dogfooding rules | checked-in dogfooding metadata snapshot includes `iss-00096-self-update-command/.meta.json` with empty `depends_on` snapshot | full-suite failure in `test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json`; active issue `.meta.json` has no `depends_on` | dogfooding validation fails even though current issue metadata is intentionally checked in | yes | regression-required | `tests/test_init_update.py`; targeted snapshot test; full unittest discover |
| tc-009 | S05 | source/cache override rejection | negative | EC-001, EC-004, constraints | runtime `update --from <source>` and `update --cache-dir <path>` fail closed before subprocess execution | hermetic managed repo with `uvx` stub and args log | future parser exposes arbitrary source or cache override while core subprocess tests still pass | yes | regression-required | `tests/cli_runtime/test_update.py`; targeted update test |

## レビュー / QA ゲート方針
- RG1 S01 implementation review:
  - reviewer: fresh `code-reviewer`
  - scope: S01 diff only, including tests and report updates
  - pass condition: `review_status: pass`
- RG2 S02 docs review:
  - reviewer: fresh `code-reviewer`
  - scope: S02 docs diff and report updates
  - pass condition: `review_status: pass`
- RG3 S04 snapshot review:
  - reviewer: fresh `code-reviewer`
  - scope: S04 dogfooding metadata snapshot diff and validation evidence
  - pass condition: `review_status: pass`
- QG1 final QA review:
  - reviewer: fresh `qa-reviewer`
  - scope: issue-wide test adequacy and integration-test need
  - pass condition: final QA pass
- CRG1 final integrated code review:
  - reviewer: fresh issue-wide `code-reviewer`
  - scope: integrated diff since issue baseline / commits
  - pass condition: `review_status: pass`
- SG1 final spec review:
  - reviewer: fresh `spec-reviewer`
  - scope: requirement / design / plan / report / implementation / tests / docs alignment
  - pass condition: final spec pass

## Pre-Implementation Delegation Consent Gate
- Current recorded workflow consent in `report.md` covers `spec-reviewer` and read-only specialist roles only.
- Before S01, S02, or S03 invokes write-capable delegation, `report.md` must record an explicit consent source that covers:
  - repo/worktree: `/Users/iwasawayuuta/workspace/tools/spec-dock`
  - active issue: `iss-00096`
  - current execution session
  - write-capable roles: `dev-coder` for S01/S03 and `doc-writer` for S02/S90 docs updates
  - boundaries: active issue scope only; no destructive operations, external publishing, credentialed access, browser/private external systems, or scope expansion
  - invalidation: active issue change, issue finish, session end, user revoke, or scope expansion
- If that consent is not present, implementation must not start. The orchestrator must either obtain consent and record it, amend the plan to use a valid `approved-local-execution` path where allowed, or classify the issue as blocked/incomplete.

## 実行ルール（全ステップ共通）
- `workflow_issue.md` is the execution source of truth.
- Each implementation step updates `report.md` before code review so review covers evidence.
- Each implementation step must close its referenced closure ids through `Step Contract Closure`, `Test Contract Closure`, and `Closure Coverage`.
- Each implementation step must record `Implementation Delegation Gate`.
- Each implementation step must reach fresh `code-reviewer` pass before commit.
- Each implementation step is one commit. Do not mix S01, S02, S03, S04, and S05 in the same commit unless this plan is amended and re-reviewed first.

## 実装ステップ

### S01 — Runtime update command executes fixed no-cache upstream installer update
- 観測可能な振る舞い:
  - `./spec-dock/scripts/spec-dock update [path]` exists as a top-level runtime command and invokes the fixed upstream no-cache installer update subprocess.
- design 参照:
  - `design.md` sections: `インターフェース契約`, `Sequence Delta`, `ディレクトリ / ファイル変更計画`
- 依存:
  - Requirement/design/plan spec-reviewer pass
- unblock:
  - S02 docs parity can reference final help wording and subprocess contract
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/update.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py`
  - `tests/cli_runtime/test_update.py`
  - `spec-dock/active/issue/report.md`
- test bundle:
  - closure id:
    - tc-001, tc-002, tc-003, tc-004, tc-005
  - test id:
    - same as closure ids
  - evidence level:
    - red-required
  - 受け入れ:
    - help/default target/explicit target
  - characterization:
    - current missing command behavior may be observed before implementation if needed
  - property / invariant:
    - upstream source fixed; no-cache present; runtime exit code equals subprocess return code
  - regression:
    - `--force` is not accepted on runtime update
  - negative:
    - subprocess failure, missing `uvx`
- pre-implementation evidence:
  - expected red: targeted tests for `update --help` and subprocess invocation fail before parser / registry / command wrapper exists.

#### 具体テストケース一覧

- `tc-s01-001` acceptance: update help exposes the self-update contract
  - 前提: temp managed repo is initialized by installer test harness and generated runtime script exists.
  - 操作: run runtime command `update --help`.
  - 期待結果: command exits 0 and help mentions update, `uvx --no-cache`, upstream GitHub source, and optional target default.
  - 失敗検出: runtime parser lacks `update`, or help omits cache/source/target contract.
  - 検証方法: add `tests/cli_runtime/test_update.py::test_update_help_describes_upstream_no_cache_and_default_target`.
  - 関連 closure id: tc-001

- `tc-s01-002` acceptance: default target invokes no-cache upstream update
  - 前提: temp managed repo has a PATH `uvx` stub that records argv and exits 0.
  - 操作: run runtime command `update` from the temp repo root.
  - 期待結果: captured argv equals `--no-cache --from git+https://github.com/chemitaro/spec-dock spec-dock update <resolved temp repo>`, and runtime exits 0.
  - 失敗検出: `--no-cache` is absent, source differs, installer command differs, or target is not the invocation repo.
  - 検証方法: add `tests/cli_runtime/test_update.py::test_update_runs_uvx_no_cache_with_default_target`.
  - 関連 closure id: tc-002

- `tc-s01-003` acceptance: explicit target is forwarded to installer update
  - 前提: temp managed repo has a sibling target directory and a PATH `uvx` stub that records argv.
  - 操作: run runtime command `update ../target-project`.
  - 期待結果: captured installer target is the resolved sibling target path, not the runtime repo root.
  - 失敗検出: explicit path is ignored, passed in the wrong position, or current repo is always used.
  - 検証方法: add `tests/cli_runtime/test_update.py::test_update_passes_explicit_target_to_installer_update`.
  - 関連 closure id: tc-003

- `tc-s01-004` negative: subprocess failure preserves diagnostics and exit code
  - 前提: PATH `uvx` stub writes one line to stdout, one line to stderr, and exits with code 7.
  - 操作: run runtime command `update`.
  - 期待結果: runtime exit code is 7, stdout contains the stub stdout, and stderr contains the stub stderr.
  - 失敗検出: failed update is reported as success, exit code is collapsed incorrectly, or either stream is hidden.
  - 検証方法: add `tests/cli_runtime/test_update.py::test_update_propagates_subprocess_failure_output_and_exit_code`.
  - 関連 closure id: tc-004

- `tc-s01-005` negative: missing uvx and unsupported force fail closed
  - 前提: one temp run has PATH without `uvx`; another uses normal PATH but passes `--force`.
  - 操作: run runtime command `update` for missing `uvx`, and `update --force` for unsupported option.
  - 期待結果: both commands exit non-zero; missing `uvx` explains that `uvx` could not be executed, and `--force` is rejected by argparse.
  - 失敗検出: runtime falls back to another updater, accepts force semantics, or reports missing dependency as success.
  - 検証方法: add `tests/cli_runtime/test_update.py::test_update_missing_uvx_fails_with_actionable_error` and `test_update_rejects_force_option`.
  - 関連 closure id: tc-005

#### step closure contract
- closure id:
  - tc-001, tc-002, tc-003, tc-004, tc-005
- close 条件:
  - Targeted update CLI tests pass.
  - Runtime command wrapper contains fixed upstream source and mandatory `--no-cache`.
  - Parser does not expose `--force`, arbitrary source, or cache options.
- 検証 evidence:
  - `python -m unittest tests.cli_runtime.test_update -v`
  - Optional focused help/manual command from generated temp repo if needed for diagnosis.
- report evidence:
  - Step Contract Closure: S01 rows for tc-001 through tc-005.
  - Test Contract Closure: red evidence, command result, and pass evidence.
  - Closure Coverage: all S01 closure ids pass.
- 残リスク:
  - Live network/upstream package availability is not exercised by tests; this is acceptable because runtime command is a wrapper and live update is outside automated scope.

#### behavior slice execution
- 実装 batch:
  - 許可範囲:
    - Add isolated update command wrapper.
    - Register parser / registry entry.
    - Add hermetic CLI runtime tests with `uvx` stub.
    - Update issue report with S01 execution evidence.
  - 禁止範囲:
    - Do not change installer update semantics.
    - Do not add arbitrary source/cache/force options.
    - Do not call live GitHub or live `uvx` in tests.
- 検証:
  - targeted command: `python -m unittest tests.cli_runtime.test_update -v`
  - related command: `python -m unittest tests.cli_runtime.test_wrappers -v`
- refactor / tidy:
  - 目的: keep command wrapper small and local.
  - ガードレール: do not collapse runtime layering or introduce non-stdlib dependency.

#### step gate
- delegation 判断:
  - delegated
  - 必須理由 / no delegation rationale: runtime CLI / shipped scaffold / tests cross several files and should use `dev-coder` for bounded implementation.
- report draft update:
  - record pre-implementation evidence, implementation delegation, verification, closure rows before code-reviewer.
- code-reviewer gate:
  - reviewer: code-reviewer
  - review 範囲: S01 diff only
  - pass 条件: review_status: pass
  - re-review rule: fix findings and rerun fresh code-reviewer until pass
- 期待する検証:
  - targeted update tests pass
  - no live network dependency in tests
- commit gate:
  - closure 状態: committed
  - commit 範囲: S01 runtime command, tests, report evidence
  - commit message 意図: `feat(runtime): self update command を追加`
  - post-commit clean check: `git status --short`
- no-op gate:
  - 許可条件: not expected
  - diff 確認コマンド: `git diff --stat`
  - 確認した contract / file: S01 target files
  - read-only 確認 evidence: N/A
  - 根拠: S01 is expected to change runtime command surface
- post-commit report evidence:
  - commit hash / final ledger 参照:
    - record after commit
  - clean check result:
    - record after commit

### S02 — Docs explain repo-local no-cache self-update path
- 観測可能な振る舞い:
  - README and shipped docs/templates consistently teach `./spec-dock/scripts/spec-dock update [path]` and why runtime update uses upstream `uvx --no-cache`.
- design 参照:
  - `design.md` sections: `ディレクトリ / ファイル変更計画`, `要件 → 設計マッピング`, `テスト戦略`
- 依存:
  - S01 command/help contract
- unblock:
  - S90 docs impact resolution and final spec review
- 対象ファイル:
  - `README.md`
  - `src/spec_dock/assets/spec_dock/templates/README.md`
  - Additional shipped docs/templates discovered by docs impact inspection, only when they currently explain update/install command surface.
  - `spec-dock/active/issue/report.md`
- test bundle:
  - closure id:
    - tc-006
  - test id:
    - same as closure id
  - evidence level:
    - inspect-only plus targeted docs assertions if existing tests naturally cover the updated scaffold text
  - 受け入れ:
    - docs mention repo-local update command, fixed upstream source, no-cache, default target.
  - characterization:
    - existing README currently documents installer `uvx ... update` and uvx cache workaround but not the repo-local self-update command.
  - property / invariant:
    - docs do not advertise arbitrary source/cache/force options for runtime update.
  - regression:
    - stale cache workaround remains visible where relevant.
  - negative:
    - docs do not describe runtime update as `init --force`.
- pre-implementation evidence:
  - characterization pass: inspect current docs and record missing repo-local self-update guidance before edits.

#### 具体テストケース一覧

- `tc-s02-001` acceptance: docs expose repo-local self-update guidance
  - 前提: S01 help/command contract is implemented and README / shipped templates are available.
  - 操作: inspect docs diff and, where practical, generated scaffold text from installer tests.
  - 期待結果: docs show `./spec-dock/scripts/spec-dock update [path]`, mention fixed upstream GitHub package source and mandatory no-cache behavior, and state default target is current directory.
  - 失敗検出: docs continue to require long `uvx --from ... spec-dock update` as the only update path or omit no-cache source-of-truth.
  - 検証方法: docs diff inspection, relevant `python -m unittest tests.cli_runtime.test_wrappers -v` scaffold docs assertions if updated, and S90 `spec-reviewer` docs alignment.
  - 関連 closure id: tc-006

#### step closure contract
- closure id:
  - tc-006
- close 条件:
  - README and shipped docs/templates no longer leave repo-local self-update undocumented.
  - Docs do not advertise unsupported runtime options.
  - Docs wording is consistent with S01 help.
- 検証 evidence:
  - `git diff -- README.md src/spec_dock/assets/spec_dock/templates/README.md ...`
  - Relevant targeted docs/scaffold test if updated.
- report evidence:
  - Step Contract Closure: S02 row for tc-006.
  - Test Contract Closure: inspection evidence and command evidence.
  - Closure Coverage: tc-006 pass.
- 残リスク:
  - External package availability remains outside docs verification; docs must describe the source and no-cache contract, not guarantee GitHub uptime.

#### behavior slice execution
- 実装 batch:
  - 許可範囲:
    - Update README and shipped docs/templates for self-update.
    - Add or update docs assertions if current tests already assert command guidance.
    - Update issue report with S02 evidence.
  - 禁止範囲:
    - Do not substantially rewrite workflow skills.
    - Do not add unrelated lifecycle command docs.
- 検証:
  - targeted command: docs-specific unittest if assertions change, otherwise `python -m unittest tests.cli_runtime.test_wrappers -v`
  - related command: `rg -n "spec-dock update|scripts/spec-dock update|--no-cache" README.md src/spec_dock/assets/spec_dock`
- refactor / tidy:
  - 目的: keep docs concise and aligned with runtime help.
  - ガードレール: preserve existing uvx installer usage guidance for first install.

#### step gate
- delegation 判断:
  - delegated
  - 必須理由 / no delegation rationale: persistent README / shipped docs changes are outside main-agent direct edit boundary and should use `doc-writer`.
- report draft update:
  - record docs impact inspection and verification before review.
- code-reviewer gate:
  - reviewer: code-reviewer
  - review 範囲: S02 docs diff, related tests if any, report evidence
  - pass 条件: review_status: pass
  - re-review rule: fix findings and rerun fresh code-reviewer until pass
- 期待する検証:
  - docs search confirms updated command guidance.
- commit gate:
  - closure 状態: committed
  - commit 範囲: S02 docs updates and report evidence
  - commit message 意図: `docs(update): self update command の案内を追加`
  - post-commit clean check: `git status --short`
- no-op gate:
  - 許可条件: only if docs inspection proves all AC-005 wording already exists before S02
  - diff 確認コマンド: `git diff -- README.md src/spec_dock/assets/spec_dock`
  - 確認した contract / file: README, shipped templates/docs, runtime help
  - read-only 確認 evidence: S90 spec-reviewer docs alignment
  - 根拠: docs-only approved-no-op requires no missing AC-005 wording
- post-commit report evidence:
  - commit hash / final ledger 参照:
    - record after commit
  - clean check result:
    - record after commit

### S03 — Dogfooding mirror reflects provider self-update command
- 観測可能な振る舞い:
  - Provider-side runtime/docs changes are reflected in the local dogfooding consumer workspace or explicitly inspected as already current, and the local runtime mirror exposes `update --help`.
- design 参照:
  - `design.md` sections: `Parent Diagram References`, `ディレクトリ / ファイル変更計画`, `テスト戦略`
- 依存:
  - S01 runtime command implementation
  - S02 docs parity
- unblock:
  - S90 docs impact resolution and S99 final quality gate
- 対象ファイル:
  - `spec-dock/scripts/spec-dock`
  - `spec-dock/scripts/spec_dock_runtime/cli/parser.py`
  - `spec-dock/scripts/spec_dock_runtime/cli/registry.py`
  - `spec-dock/scripts/spec_dock_runtime/commands/update.py`
  - generated `spec-dock/docs` / `spec-dock/templates` mirror files when refreshed by local installer update
  - `spec-dock/active/issue/report.md`
- test bundle:
  - closure id:
    - tc-007
  - test id:
    - same as closure id
  - evidence level:
    - inspect-only
  - 受け入れ:
    - local dogfooding runtime mirror exposes `update --help`.
  - characterization:
    - before local refresh, mirror may lack the provider-side `update` command.
  - property / invariant:
    - dogfooding mirror is not treated as implementation source of truth.
  - regression:
    - provider asset changes are not left unobservable in the local consumer workspace.
  - negative:
    - do not execute live `./spec-dock/scripts/spec-dock update` without `--help`, because live upstream update is outside automated scope.
- pre-implementation evidence:
  - characterization pass: inspect local mirror before refresh and record whether `update` is absent or stale.

#### 具体テストケース一覧

- `tc-s03-001` acceptance: dogfooding runtime help exposes update
  - 前提: S01/S02 provider-side changes have passed targeted tests and docs updates; local dogfooding mirror is available in this repo.
  - 操作: run local installer refresh `python -m spec_dock.cli update .` or document why refresh is unnecessary, then run `./spec-dock/scripts/spec-dock update --help`.
  - 期待結果: dogfooding mirror contains the runtime `update` command and help shows the same no-cache upstream/source/default-target contract as provider tests.
  - 失敗検出: provider tests pass but the local `spec-dock/scripts/...` runtime remains stale or cannot show `update --help`.
  - 検証方法: record local installer update / mirror diff / `./spec-dock/scripts/spec-dock update --help` evidence in report.
  - 関連 closure id: tc-007

#### step closure contract
- closure id:
  - tc-007
- close 条件:
  - `python -m spec_dock.cli update .` succeeds or a no-refresh decision is documented with exact inspected files.
  - `./spec-dock/scripts/spec-dock update --help` succeeds and shows the command contract.
  - Any generated mirror diff is reviewed and committed or a valid approved-no-op is recorded.
- 検証 evidence:
  - `python -m spec_dock.cli update .`
  - `./spec-dock/scripts/spec-dock update --help`
  - `git diff -- spec-dock/scripts spec-dock/docs spec-dock/templates`
- report evidence:
  - Step Contract Closure: S03 row for tc-007.
  - Test Contract Closure: mirror refresh/inspection and help evidence.
  - Closure Coverage: tc-007 pass or valid approved-no-op.
- 残リスク:
  - Live upstream self-update path is not executed. This is acceptable because S03 verifies the local mirror command surface, while S01 verifies subprocess invocation hermetically.

#### behavior slice execution
- 実装 batch:
  - 許可範囲:
    - Run local installer update from this checkout into the dogfooding workspace.
    - Inspect and commit resulting generated mirror diffs when relevant.
    - Update report evidence.
  - 禁止範囲:
    - Do not run live upstream `./spec-dock/scripts/spec-dock update` without `--help`.
    - Do not manually edit dogfooding mirror as source of truth except report evidence.
- 検証:
  - targeted command: `./spec-dock/scripts/spec-dock update --help`
  - related command: `git diff -- spec-dock/scripts spec-dock/docs spec-dock/templates`
- refactor / tidy:
  - 目的: keep dogfooding mirror aligned with provider assets.
  - ガードレール: provider-side source remains under `src/spec_dock/assets/spec_dock/...`.

#### step gate
- delegation 判断:
  - delegated when mirror refresh/integration requires file changes; approved-local-execution may be used only for command execution and inspection if no source/test/docs files are edited by the main agent beyond report evidence.
  - 必須理由 / no delegation rationale: dogfooding refresh touches shipped scaffold mirror and must be reviewed as a separate step.
- report draft update:
  - record mirror refresh/no-refresh decision and help evidence before review.
- code-reviewer gate:
  - reviewer: code-reviewer
  - review 範囲: S03 generated mirror diff and report evidence
  - pass 条件: review_status: pass
  - re-review rule: fix findings and rerun fresh code-reviewer until pass
- 期待する検証:
  - local dogfooding help confirms `update`.
- commit gate:
  - closure 状態: committed or valid approved-no-op
  - commit 範囲: dogfooding mirror refresh and report evidence
  - commit message 意図: `chore(dogfooding): self update command mirror を更新`
  - post-commit clean check: `git status --short`
- no-op gate:
  - 許可条件: local dogfooding mirror is already current after S01/S02 and `update --help` passes.
  - diff 確認コマンド: `git diff -- spec-dock/scripts spec-dock/docs spec-dock/templates`
  - 確認した contract / file: runtime parser, registry, update command, help output
  - read-only 確認 evidence: `./spec-dock/scripts/spec-dock update --help`
  - 根拠: valid only when dogfooding mirror is demonstrably current.
- post-commit report evidence:
  - commit hash / final ledger 参照:
    - record after commit
  - clean check result:
    - record after commit

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs / templates / README / workflow / skill / migration notes
- 対応:
  - Inspect README, shipped templates/docs, workflow docs, and skills for update/install command guidance.
  - If S02 did not update a touched surface, record why it is unaffected.
  - Confirm S03 dogfooding mirror refresh/inspection evidence covers the local consumer workspace.
  - Use `doc-writer` for additional persistent docs updates if impact is found after S02.
- doc update owner:
  - doc-writer when updates are required
- spec/doc review:
  - reviewer: spec-reviewer
  - pass 条件: docs are aligned with requirement/design/plan and no required docs impact remains.

### S99 — final quality gate
- branch diff 範囲:
  - all commits and remaining diff for `iss-00096-self-update-command`
- 必須 validation:
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock validate`
  - `python -m unittest tests.cli_runtime.test_update -v`
  - `./spec-dock/scripts/spec-dock update --help`
  - `python -m unittest discover -v`
  - `rg --files | rg '[A-Z]'` with documented existing uppercase necessity / no casual new uppercase paths
- final QA gate:
  - reviewer: qa-reviewer
  - 範囲: Issue 全体の test 十分性と integration test 要否
  - pass 条件: reviewer pass. If reviewer requires integration test, add it before pass.
  - re-review rule: 指摘を修正し qa-reviewer を pass まで再実行
- final code review ゲート:
  - reviewer: code-reviewer
  - 範囲: issue-wide integrated diff, structure, responsibility boundaries, regression risk, maintainability
  - pass 条件: review_status: pass
  - re-review rule: 指摘を修正し code-reviewer を pass まで再実行
- final spec review ゲート:
  - reviewer: spec-reviewer
  - 範囲: requirement / design / plan / report / implementation / tests / docs alignment
  - pass 条件: reviewer pass
  - re-review rule: 指摘を修正し spec-reviewer を pass まで再実行
- final commit gate:
  - commit 範囲:
    - final report ledger updates and any final gate fixes
  - commit 前の final report ledger:
    - S01/S02/S03 closure, sync/validate/test evidence, final QA/code/spec review verdicts, final commit scope, external evidence destination
  - post-commit external evidence の記録先:
    - final response and, if PR/issue publishing is requested later, PR/issue comment

## 未確定事項
- Requirement / design / plan gate を block する未確定事項:
  - なし。

## Final Exit Contract
- AC/EC 達成:
  - AC-001 through AC-005 and EC-001 through EC-005 closed in report `Closure Coverage`.
- docs 影響解決:
  - S02 and S90 complete; final spec-reviewer confirms docs alignment.
- 全 implementation step 完了:
  - S01 committed.
  - S02 committed or valid approved-no-op.
  - S03 committed or valid approved-no-op.
  - S04 committed.
  - S05 committed.
- final quality gate pass:
  - qa-reviewer: pass
  - issue-wide code-reviewer: pass
  - spec-reviewer: pass
- final commit 完了:
  - final report ledger committed after all final gates pass.
- 必須 closure id 完了:
  - Step Contract Closure: tc-001 through tc-009 pass or valid approved-no-op where allowed.
  - Test Contract Closure: tc-001 through tc-009 pass or valid approved-no-op where allowed.
  - Closure Coverage: tc-001 through tc-009 pass or valid approved-no-op where allowed.
- final clean state:
  - no unintended staged / unstaged changes.
  - final commit hash and clean check recorded as external delivery evidence.
