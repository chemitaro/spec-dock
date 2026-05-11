---
種別: 実装計画書（Issue）
ID: "iss-00091"
タイトル: "Default Github State Commands"
関連GitHub: ["#91"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-11"
依存: ["requirement.md", "design.md"]
親: ["epic-00090", "init-local-00003"]
---

# iss-00091 Default Github State Commands — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007
- EC:
  - EC-001, EC-002, EC-003
- 制約:
  - `--offline` を導入しない
  - local-only node creation を復活させない
  - GitHub issue list の全件 cache file を新設しない
  - application layer の bool request contract を維持する
  - provider / dogfooding docs and skill parity を保つ

## マイルストーン一覧
- M1:
  - 対象: CLI default inversion
  - exit: `sync` / `deps check` / `active set` が flag なしで GitHub enabled になり、`--no-github` が cache path を選ぶ
- M2:
  - 対象: regression tests
  - exit: default GitHub, `--no-github`, compatibility `--github`, mutual exclusion, `new --no-github` rejection がテストで固定される
- M3:
  - 対象: docs / skill parity
  - exit: provider assets と checked-in mirrors の command examples が新 contract に揃う
- M9:
  - 対象: final quality gate
  - exit: targeted tests / validate / sync / review evidence が report に記録される

## 依存関係から導く実装順序
- 依存関係の正本:
  - `design.md` の `依存関係分析`
  - `design.md` の `Module Dependency Diagram`
  - `design.md` の `ディレクトリ / ファイル変更計画`
- sequencing rule:
  - CLI request bool の default を先に固定し、その後に tests と docs を合わせる。
  - docs / skill は最終 command vocabulary が決まってから更新する。
- step dependency summary:
  - S01:
    - depends on: approved requirement/design/plan
    - unblocks: S02, S03
    - target files: command parser files
  - S02:
    - depends on: S01
    - unblocks: S99
    - target files: CLI runtime tests and scaffold assertion tests
  - S03:
    - depends on: S01
    - unblocks: S99
    - target files: docs and skills mirrors
  - S99:
    - depends on: S01, S02, S03
    - unblocks: implementation completion review
    - target files: report and final evidence only

## ステップ一覧
- S01:
  - 観測可能な振る舞い: state commands default to GitHub live state
  - depends on: spec approval
  - unblocks: tests and docs
  - target files: `commands/sync.py`, `commands/deps.py`, `commands/active.py`
  - closes: tc-001, tc-002, tc-003, tc-004, tc-005
  - review gate: targeted parser/runtime diff review
- S02:
  - 観測可能な振る舞い: regression suite fixes and locks new CLI contract
  - depends on: S01
  - unblocks: final quality gate
  - target files: `tests/cli_runtime/test_sync.py`, `test_deps.py`, `test_active.py`, `test_new.py`, `tests/test_init_update.py`
  - closes: tc-006, tc-007, tc-008, tc-009
  - review gate: tests pass
- S03:
  - 観測可能な振る舞い: user-facing docs and skill reminders describe GitHub default and `--no-github` opt-out
  - depends on: S01
  - unblocks: final quality gate
  - target files: provider docs, dogfooding docs, provider install-root skill, checked-in skill mirror
  - closes: tc-010
  - review gate: docs parity diff review
- S99:
  - 観測可能な振る舞い: final evidence proves implementation, tests, docs, and review readiness
  - depends on: S01, S02, S03
  - unblocks: issue completion decision
  - target files: `report.md`
  - closes: tc-009, tc-011
  - review gate: final diff review

## 要件 ↔ ステップ対応
- AC-001 -> S01, S02
- AC-002 -> S01, S02
- AC-003 -> S01, S02
- AC-004 -> S01, S02
- AC-005 -> S01, S02
- AC-006 -> S01, S02
- AC-007 -> S02
- EC-001 -> S02
- EC-002 -> S02
- EC-003 -> S02
- no-new-full-cache constraint -> S02, S99
- docs parity constraint -> S03

## Spec-Locked Closure Index（仕様固定クロージャ索引）

| id | phase / step | slice | type | spec link | locked expectation | observable input/state | bug class guarded | required | evidence level | closure evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | sync default | acceptance | AC-001 | `sync` without `--github` sets `github_enabled=True` | `./spec-dock/scripts/spec-dock sync` | stale cache remains default | yes | red-required | report step closure |
| tc-002 | S01 | sync opt-out | acceptance | AC-002, EC-002, EC-003 | `sync --no-github` sets `github_enabled=False` and never calls gh | `./spec-dock/scripts/spec-dock sync --no-github` | unwanted network call in explicit no-github mode | yes | red-required | report step closure |
| tc-003 | S01 | deps default | acceptance | AC-003 | `deps check <target>` sets `use_github=True` | `./spec-dock/scripts/spec-dock deps check iss-00091` | readiness uses stale cache by default | yes | red-required | report step closure |
| tc-004 | S01 | active default | acceptance | AC-004 | `active set <target>` sets `use_github=True` for deps guard | `./spec-dock/scripts/spec-dock active set iss-00091` | active guard uses stale cache by default | yes | red-required | report step closure |
| tc-005 | S01 | compatibility and conflict flags | negative | AC-005, AC-006 | `--github` remains accepted; `--github --no-github` fails | parser-level invocations | ambiguous mode selection | yes | red-required | report step closure |
| tc-006 | S02 | new rejected contract | regression | AC-007 | `new ... --no-github` remains rejected and does not invoke gh | existing new command tests | accidental local-only creation revival | yes | covered-existing | report test closure |
| tc-007 | S02 | fetch failure behavior | regression | EC-001 | `gh_fetch_failed` warning / unknown behavior remains unchanged | failing gh stub | accidental fatal behavior change | yes | covered-existing | report test closure |
| tc-008 | S02 | cache-only guard | negative | AC-002, EC-002, EC-003 | explicit `--no-github` never falls back to live GitHub fetch | gh guard log absent | hidden network fallback | yes | red-required | report test closure |
| tc-009 | S02/S99 | no new full issue-list cache | negative | requirement MUST NOT | implementation does not add a new file-level cache for the full GitHub issue list | diff inspection and runtime artifact inspection | accidental persistent full GitHub list cache | yes | inspect-required | report test/final closure |
| tc-010 | S03 | docs and skill parity | documentation | docs constraint | examples describe default GitHub commands and `--no-github` opt-out | provider and mirror docs / skills | stale workflow docs | yes | inspect-only | report docs closure |
| tc-011 | S99 | final quality gate | review | final exit contract | targeted tests, validate, sync, uppercase path check, no-new-cache inspection, and diff review are recorded | command evidence | incomplete completion report | yes | manual-required | report final closure |

## レビュー / QA ゲート方針
- SG1 spec review:
  - timing: implementation starts only after requirement/design/plan are reviewed and approved.
  - scope: command contract, docs impact, test coverage, non-goals.
- RG1 implementation review:
  - timing: after S01-S03 implementation and tests.
  - scope: default inversion is contained to CLI boundary; application fetch/cache logic unchanged.
- QG1 QA review:
  - timing: after targeted tests and docs parity checks.
  - scope: CLI behavior, no-github behavior, compatibility behavior, generated docs / skill parity.

## 実行ルール（全ステップ共通）
- 実行 policy、approval cadence、completion contract は `workflow_issue.md` を正本にする。
- step / block / behavior slice の書き方は `phase_plan_issue.md` を正本にする。
- `Spec-Locked Closure Index` の required rows は、実装中に勝手に削除・意味変更しない。
- docs impact があるため S03 を省略しない。
- final diff review quality gate は S99 で独立して実施する。

## 実装ステップ

### S01 — CLI default GitHub mode and `--no-github`
- observable behavior:
  - `sync` / `deps check` / `active set` は flag なしで GitHub enabled request を作る。
  - `--no-github` は GitHub disabled request を作る。
  - `--github --no-github` は parser error になる。
- design refs:
  - `design.md` の `インターフェース契約`
  - `design.md` の `Module Dependency Diagram`
- depends on:
  - SG1 spec approval
- unblocks:
  - S02, S03
- target files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/sync.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/active.py`
- test bundle:
  - closure ids:
    - tc-001, tc-002, tc-003, tc-004, tc-005
  - evidence level:
    - red-required
  - acceptance:
    - default GitHub enabled request values
  - regression:
    - compatibility `--github`
  - negative:
    - `--github --no-github` parser error
- pre-implementation evidence:
  - expected red: default no-flag command tests should currently fail because they do not invoke GitHub.
- report update:
  - record parser defaults and command behavior evidence.

#### step closure contract
- closure ids:
  - tc-001, tc-002, tc-003, tc-004, tc-005
- close when:
  - command parser tests prove default true / no-github false / mutual exclusion.
- verification evidence:
  - targeted command:
    - `python -m unittest tests.cli_runtime.test_sync tests.cli_runtime.test_deps tests.cli_runtime.test_active -v`
- report evidence:
  - Step Contract Closure: S01 rows
  - Test Contract Closure: tc-001 through tc-005
  - Closure Coverage: AC-001 through AC-006
- residual risk:
  - none beyond GitHub auth/network warning behavior, which remains existing behavior.

#### behavior slice execution
- implementation batch:
  - allowed scope:
    - command parser and args factory changes only.
  - forbidden scope:
    - application fetch/cache logic rewrite.
    - `new` local-only creation behavior change.
- verification:
  - targeted command:
    - command runtime tests listed above
  - related / full command:
    - `python -m unittest discover -v` if targeted tests expose shared parser risk.
- refactor / tidy:
  - purpose:
    - keep parser code explicit unless duplication becomes error-prone.
  - guardrail:
    - do not add a new "github mode" module unless review shows duplication risk.

### S02 — Regression tests for GitHub default and no-github cache path
- observable behavior:
  - Tests fail on old behavior and pass on new behavior.
  - Existing `new --no-github` rejection remains green.
- design refs:
  - `design.md` の `テスト戦略`
- depends on:
  - S01
- unblocks:
  - S99
- target files:
  - `tests/cli_runtime/test_sync.py`
  - `tests/cli_runtime/test_deps.py`
  - `tests/cli_runtime/test_active.py`
  - `tests/cli_runtime/test_new.py`
  - `tests/test_init_update.py`
- test bundle:
  - closure ids:
    - tc-006, tc-007, tc-008, tc-009
  - evidence level:
    - red-required / covered-existing
  - acceptance:
    - default GitHub tests
  - regression:
    - `new ... --no-github` rejection
    - `gh_fetch_failed` warning behavior
  - negative:
    - no hidden gh invocation under `--no-github`
- pre-implementation evidence:
  - expected red: old "without --github must not fetch GitHub" expectations conflict with new contract and must be rewritten.
- report update:
  - record which tests were updated and why.

#### step closure contract
- closure ids:
  - tc-006, tc-007, tc-008, tc-009
- close when:
  - default GitHub, no-github cache, compatibility, mutual exclusion, new rejection tests pass.
  - diff inspection confirms no new persistent full GitHub issue-list cache file is introduced.
- verification evidence:
  - targeted command:
    - `python -m unittest tests.cli_runtime.test_sync tests.cli_runtime.test_deps tests.cli_runtime.test_active tests.cli_runtime.test_new -v`
- report evidence:
  - Step Contract Closure: S02 rows
  - Test Contract Closure: tc-006 through tc-009
  - Closure Coverage: AC-001 through AC-007, EC-001 through EC-003
- residual risk:
  - broad test runtime cost may require targeted first, then selected full suite.

#### behavior slice execution
- implementation batch:
  - allowed scope:
    - tests that directly encode the changed command contract.
  - forbidden scope:
    - unrelated test cleanup.
- verification:
  - targeted command:
    - targeted CLI runtime tests
  - related / full command:
    - `python -m unittest discover -v` if time permits.
  - inspection:
    - `git diff --name-status main...HEAD`
    - confirm no new artifact such as a persistent full GitHub issue-list cache file was added.
- refactor / tidy:
  - purpose:
    - reuse existing gh stubs and guard logs where available.
  - guardrail:
    - avoid introducing live network tests.

### S03 — Docs impact resolution / docs refresh
- observable behavior:
  - User-facing docs and skill reminders no longer teach `--github` as required for normal state commands.
  - Docs describe `--no-github` as explicit cache/local opt-out.
- design refs:
  - `design.md` の `ディレクトリ / ファイル変更計画`
- depends on:
  - S01
- unblocks:
  - S99
- target files:
  - `src/spec_dock/assets/spec_dock/docs/reference_github.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `spec-dock/docs/reference_github.md`
  - `spec-dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `tests/test_init_update.py`
- test bundle:
  - closure ids:
    - tc-010
  - evidence level:
    - inspect-only
  - acceptance:
    - docs and skills present default examples plus `--no-github` opt-out.
  - regression:
    - scaffold mirror assertions updated.
- pre-implementation evidence:
  - inspect current `rg -- "--github|--no-github"` output to identify stale examples.
- report update:
  - record docs paths changed.

#### step closure contract
- closure ids:
  - tc-010
- close when:
  - provider and dogfooding docs/skills agree on default GitHub command vocabulary.
- verification evidence:
  - targeted command:
    - `python -m unittest tests.test_init_update -v`
  - inspection:
    - `rg -n -- "sync --github|deps check <target> --github|active set <target> --github" src/spec_dock/assets spec-dock .agents`
- report evidence:
  - Step Contract Closure: S03 rows
  - Test Contract Closure: tc-010
  - Closure Coverage: docs parity constraint
- residual risk:
  - Some historical references may remain intentionally in compatibility notes; report them explicitly if retained.

#### behavior slice execution
- implementation batch:
  - allowed scope:
    - docs and skill command examples affected by this issue.
  - forbidden scope:
    - broad rewrite of GitHub reference unrelated to state command defaults.
- verification:
  - targeted command:
    - `python -m unittest tests.test_init_update -v`
  - related / full command:
    - docs grep inspection.
- refactor / tidy:
  - purpose:
    - keep provider and mirror text aligned.
  - guardrail:
    - update provider source first, then checked-in mirror.

### S99 — final diff review quality gate
- branch diff scope:
  - `git diff main...HEAD`
- required validation:
  - targeted CLI runtime tests from S01/S02
  - `python -m unittest tests.test_init_update -v`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
  - `rg --files | rg '[A-Z]'`
  - `git diff --name-status main...HEAD` inspection proving no new full GitHub issue-list cache file was added
- reviewer approvals:
  - code review pass required before reporting complete.
  - QA/spec review pass required if workflow requires it.
- report update:
  - Record final command outputs, review verdicts, and any residual risks in `report.md`.

#### step closure contract
- closure ids:
  - tc-009, tc-011
- close when:
  - all required validation evidence and review outcomes are recorded.
- verification evidence:
  - targeted commands listed above.
- report evidence:
  - Step Contract Closure: S99 rows
  - Test Contract Closure: tc-009 and tc-011
  - Closure Coverage: every required closure id closed
- residual risk:
  - If GitHub/network is unavailable, record blocker and do not claim complete.

## final exit contract
- AC/EC 達成:
  - AC-001 through AC-007 and EC-001 through EC-003 closed in report.
- docs impact resolved:
  - provider and mirror docs/skills updated or explicitly justified as no-op.
- final diff approved:
  - final diff review and required reviewer pass recorded.
- required closure ids closed:
  - Step Contract Closure: tc-001 through tc-011
  - Test Contract Closure: tc-001 through tc-011
  - Closure Coverage: all required rows mapped to evidence

## 未確定事項
- なし。
