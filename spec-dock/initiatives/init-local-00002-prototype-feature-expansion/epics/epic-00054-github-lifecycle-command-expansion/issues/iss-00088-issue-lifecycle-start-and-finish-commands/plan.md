---
種別: 実装計画書（Issue）
ID: "iss-00088"
タイトル: "Issue lifecycle start and finish commands"
関連GitHub: ["#88"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-06"
依存: ["requirement.md", "design.md"]
親: ["epic-00054", "init-local-00002"]
---

# iss-00088 Issue lifecycle start and finish commands — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001
  - AC-002
  - AC-003
  - AC-004
  - AC-005
  - AC-006
  - AC-007
- EC:
  - EC-001
  - EC-002
  - EC-003
  - EC-004
  - EC-005
- 制約:
  - `active set` / `active set --checkout` の既存挙動を変更しない
  - `issue finish` は commit / push / merge / PR / stash / report 自動編集を行わない
  - dirty worktree hard block や protected branch hard block は Phase 1 に含めない
  - provider runtime / docs / skills と dogfooding mirror の整合を保つ

## マイルストーン一覧
- M1:
  - 対象:
    - spec readiness and red behavior lock
  - exit:
    - design / plan が issue 固有で、SG1 spec review が pass する
- M2:
  - 対象:
    - `issue start` command and unfinished guard
  - exit:
    - start success / block / force / non-issue target behavior が tests で閉じる
- M3:
  - 対象:
    - `issue finish` command
  - exit:
    - close + active clear / failure active unchanged が tests で閉じる
- M4:
  - 対象:
    - docs / skill / mirror parity and final validation
  - exit:
    - provider + dogfooding docs / skill / runtime tests / final review が pass する

## 依存関係から導く実装順序
- 依存関係の正本:
  - `design.md` の `依存関係分析`
  - `design.md` の `Module Dependency Diagram`
  - `design.md` の `ディレクトリ / ファイル変更計画`
- sequencing rule:
  - use case contracts -> command wrapper -> finish orchestration -> docs / skill -> final validation の順で進める
- step dependency summary:
  - S00:
    - depends on:
      - requirement/design/plan
    - unblocks:
      - implementation
    - target files:
      - issue docs only
  - S01:
    - depends on:
      - current command/use case patterns
    - unblocks:
      - `issue start` parser / CLI wrapper
    - target files:
      - `application/contracts.py`, new lifecycle use case, tests
  - S02:
    - depends on:
      - S01 lifecycle contract
    - unblocks:
      - user-facing `issue start`
    - target files:
      - `commands/issue.py`, `cli/parser.py`, `presentation/cli_text.py`, tests
  - S03:
    - depends on:
      - active issue target handling and close capability
    - unblocks:
      - user-facing `issue finish`
    - target files:
      - lifecycle use case, command wrapper, tests
  - S90:
    - depends on:
      - runtime behavior
    - unblocks:
      - final quality gate
    - target files:
      - provider docs, dogfooding docs, installed skill
  - S99:
    - depends on:
      - S01-S90
    - unblocks:
      - issue completion
    - target files:
      - report and final validation evidence

## ステップ一覧
- S00:
  - 観測可能な振る舞い:
    - issue docs だけで implementation-ready と判断できる
  - closes:
    - SG1 baseline only
  - review gate:
    - SG1 spec review pass
- S01:
  - 観測可能な振る舞い:
    - application layer が `issue start` の success / block / force policy を表現できる
  - closes:
    - AC-001
    - AC-002
    - AC-003
    - AC-004
    - EC-001
    - EC-002
    - EC-003
    - EC-004
    - EC-005
  - review gate:
    - targeted tests pass
- S02:
  - 観測可能な振る舞い:
    - CLI から `issue start` を実行でき、messages が action-oriented である
  - closes:
    - AC-001
    - AC-002
    - AC-003
    - AC-004
  - review gate:
    - CLI tests pass
- S03:
  - 観測可能な振る舞い:
    - CLI から `issue finish` を実行でき、close success 後だけ active clear される
  - closes:
    - AC-005
    - AC-006
  - review gate:
    - CLI/application tests pass
- S90:
  - 観測可能な振る舞い:
    - docs / skills が `issue start` / `issue finish` を primary path として案内する
  - closes:
    - AC-007
  - review gate:
    - docs/spec review pass
- S99:
  - 観測可能な振る舞い:
    - final diff / tests / validation / review evidence が report に揃う
  - closes:
    - final exit contract
  - review gate:
    - implementation review pass
    - QA review pass
    - final spec review pass

## 要件 ↔ ステップ対応
- AC-001 -> S01, S02
- AC-002 -> S01, S02
- AC-003 -> S01, S02
- AC-004 -> S01, S02
- AC-005 -> S03
- AC-006 -> S03
- AC-007 -> S90, S99
- EC-001 -> S01, S02
- EC-002 -> S01, S02
- EC-003 -> S01, S02
- EC-004 -> S01, S02
- EC-005 -> S01, S02, S99

## Spec-Locked Closure Index（仕様固定クロージャ索引）

| id | phase / step | slice | type | spec link | locked expectation | observable input/state | bug class guarded | required | evidence level | closure evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| lc-001 | S01/S02 | issue start success | acceptance | AC-001 | `issue start <issue>` sets active issue and checks out the issue branch; non-issue targets fail-fast | CLI target issue node; active state; branch | missing guided start / wrong node kind accepted | yes | red-required | CLI/runtime test + report closure |
| lc-002 | S01/S02 | unfinished guard | negative | AC-002, EC-002 | different issue start from unfinished active issue branch blocks before active/checkout mutation and prints next commands | active issue open/unknown; current branch maps to active issue; target differs; no force | accidental context switch / partial active mutation | yes | red-required | CLI/runtime test + report closure |
| lc-003 | S01/S02 | force start | acceptance | AC-003 | `-f`/`--force` bypasses only the unfinished issue guard, does not bypass dependency/readiness checks, and shows forced start evidence | same as lc-002 plus force plus dependency-not-ready fixture | force ignored / silent force / dependency bypass leak | yes | red-required | CLI/runtime test + report closure |
| lc-004 | S01/S02 | safe branch start | regression | AC-004, EC-003 | main/non-issue branch and same issue restart do not trigger unfinished guard | current branch main/non-issue or requested==active issue | overblocking normal/emergency workflows | yes | red-required | CLI/runtime test + report closure |
| lc-005 | S03 | issue finish success | acceptance | AC-005 | finish closes/already-closed active linked GitHub issue and clears active only after close success | active issue with GitHub link; issue state open/closed | finish does not clear / finish clears before close | yes | red-required | CLI/runtime test + report closure |
| lc-006 | S03 | issue finish failure | negative | AC-006 | no active, no link, or close/status failure leaves active unchanged and gives recovery guidance | missing active / missing link / gateway error | silent failure / active lost on failure | yes | red-required | CLI/runtime test + report closure |
| lc-007 | S90 | docs and skill guidance | acceptance | AC-007 | provider docs, dogfooding docs, CLI help, and issue execution skill describe `issue start`/`issue finish` as primary path and keep `active set` as manual/recovery | docs/skill files | agent continues old ambiguous workflow | yes | inspect-only | docs diff + spec review closure |
| lc-008 | S99 | existing active contract unchanged | regression | EC-005, constraints | direct `active set` behavior remains unchanged and existing tests stay green | existing active tests and targeted active set use | guard leaks into manual recovery path | yes | covered-existing | regression command + report closure |

## レビュー / QA ゲート方針
- SG1 spec review:
  - timing:
    - S00 後
    - S90 後
    - S99 前
  - scope:
    - requirement / design / plan readiness
    - docs / skill contract consistency
- RG1 implementation review:
  - timing:
    - S02/S03 実装後
    - S99 final diff 前
  - scope:
    - layer boundaries
    - active set / close reuse
    - failure active unchanged guarantees
- QG1 QA review:
  - timing:
    - targeted tests pass 後
    - final validation 後
  - scope:
    - acceptance coverage
    - negative path coverage
    - docs mirror coverage

## 実行ルール（全ステップ共通）
- 実行 policy、approval cadence、completion contract は `workflow_issue.md` を正本にする。
- step / block / behavior slice の書き方は `phase_plan_issue.md` を正本にする。
- required closure row、locked expectation、required、spec link を変更する場合は plan amendment と re-review を先に通す。
- 各 step の pass 後は `report.md` に evidence を残す。

## 実装ステップ

### S00 — spec readiness
- observable behavior:
  - docs are ready for implementation handoff.
- target files:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
- test bundle:
  - closure ids:
    - SG1 baseline
  - evidence level:
    - inspect-only
- bounded implementation batch:
  - issue docs only; no provider runtime/docs/skill files.
- verification command:
  - `./spec-dock/scripts/spec-dock validate`
- report evidence:
  - spec-review verdict, required fixes, and validate result.
- close when:
  - spec-reviewer reports pass or required fixes are applied and re-reviewed.

### S01 — application lifecycle contract and guard
- observable behavior:
  - application layer can decide whether `issue start` should proceed, block, or force.
- design refs:
  - `design.md` dependency analysis
  - `design.md` interface contract
- depends on:
  - S00
- unblocks:
  - S02
- target files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py`
  - wiring file(s) that assemble `UseCases`
  - targeted tests
- test bundle:
  - closure ids:
    - lc-001
    - lc-002
    - lc-003
    - lc-004
    - lc-008
  - evidence level:
    - red-required
  - acceptance:
    - success path delegates to set active with checkout
    - force path delegates despite unfinished guard
    - force path does not bypass dependency/readiness checks
  - negative:
    - unfinished guard blocks before mutation
    - non-issue target fails
  - regression:
    - active set existing behavior unchanged
- pre-implementation evidence:
  - expected red tests for missing lifecycle use case / command path
- bounded implementation batch:
  - application contracts and lifecycle orchestration only.
  - no CLI parser/command registration except wiring needed for callable construction.
  - no docs/skill wording changes.
- refactor/tidy guardrails:
  - reuse existing active, close, GitHub, and branch inference helpers where practical.
  - do not add persisted lifecycle state.
  - keep direct `active set` semantics outside this guard.
- step closure contract:
  - close when:
    - targeted lifecycle tests pass and prove no active/checkout mutation on blocked path.
  - verification evidence:
    - `python -m unittest tests.cli_runtime.test_issue_lifecycle`
  - report evidence:
    - red/green lifecycle test results, mutation-order proof, and force-scope proof.
  - residual risk:
    - GitHub unavailable behavior remains stubbed; final runtime tests cover CLI-level behavior.

### S02 — CLI `issue start`
- observable behavior:
  - `./spec-dock/scripts/spec-dock issue start <target>` is available and action-oriented.
- depends on:
  - S01
- unblocks:
  - S03
- target files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
  - dogfooding mirror runtime files if checked in
  - CLI tests
- test bundle:
  - closure ids:
    - lc-001
    - lc-002
    - lc-003
    - lc-004
  - evidence level:
    - red-required
  - acceptance:
    - parser accepts target forms and `-f` / `--force`
    - success output includes active and checkout evidence
  - negative:
    - blocked output includes next commands
- pre-implementation evidence:
  - expected red parser / CLI test before command registration
- bounded implementation batch:
  - parser, command wrapper, presentation text, registry/bootstrap wiring, and CLI tests for `issue start`.
  - no docs/skill wording changes.
- refactor/tidy guardrails:
  - do not duplicate target parsing rules if existing command helpers can be reused.
  - blocked output must stay actionable without committing to destructive recovery.
- step closure contract:
  - close when:
    - CLI tests for start success/block/force/main branch/same issue/non-issue target pass.
  - verification evidence:
    - targeted `python -m unittest ...test_issue_lifecycle...`
  - report evidence:
    - command parse/output test results and examples of blocked and forced messages.

### S03 — CLI `issue finish`
- observable behavior:
  - `./spec-dock/scripts/spec-dock issue finish` closes active linked GitHub issue and clears active after success.
- depends on:
  - S01
- unblocks:
  - S90
- target files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
  - CLI/application tests
- test bundle:
  - closure ids:
    - lc-005
    - lc-006
  - evidence level:
    - red-required
  - acceptance:
    - open issue closes and clears active
    - already closed clears active
  - negative:
    - no active / no GitHub linkage / close failure leaves active unchanged
- pre-implementation evidence:
  - expected red tests for missing `issue finish`
- bounded implementation batch:
  - finish lifecycle orchestration, command wrapper, presentation text, and finish tests.
  - no close-node behavior rewrite beyond minimal reusable call integration.
- refactor/tidy guardrails:
  - clear active only after close/already-closed success.
  - if close/status fails, preserve active state and surface recovery guidance.
- step closure contract:
  - close when:
    - finish tests pass and demonstrate clear-active ordering.
  - verification evidence:
    - `python -m unittest tests.cli_runtime.test_issue_lifecycle`
  - report evidence:
    - finish success/already-closed/failure test results and active-clear ordering proof.

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs / assets / workflow / skill
- 対応:
  - update provider docs and dogfooding docs:
    - `workflow_issue.md`
    - `reference_github.md`
    - `reference_naming.md` if checkout wording is touched
  - update issue execution skill:
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - update checked-in mirror where applicable:
    - `spec-dock/docs/...`
    - `spec-dock/scripts/...`
    - `.agents/skills/...` mirror if present
- test bundle:
  - closure ids:
    - lc-007
  - evidence level:
    - inspect-only
- bounded implementation batch:
  - provider docs, dogfooding docs, and issue execution skill wording only.
  - no runtime code/test changes.
- verification command:
  - targeted docs grep/inspection plus `./spec-dock/scripts/spec-dock validate`
- report evidence:
  - changed docs/skill list and summary of primary-path / manual-recovery wording.
- step closure contract:
  - close when:
    - docs/skill wording states primary path and exclusions clearly.

### S99 — final diff review quality gate
- branch diff scope:
  - all changes from `main...HEAD`
- required validation:
  - targeted lifecycle tests
  - existing active/close regression tests
  - docs/scaffold tests if assets changed
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync --github`
- reviewer approvals:
  - code-reviewer pass
  - qa-reviewer pass
  - spec-reviewer final pass
- report update:
  - record command evidence, `sync --github` evidence, review verdicts, closure coverage, changed files, residual risks.

## 未確定事項
- なし:
  - Implementation may choose helper names and test fixture internals, but must not change closure expectations.

## final exit contract
- AC/EC 達成:
  - lc-001 through lc-008 closed in report.
- docs impact resolved:
  - provider + dogfooding docs and skill guidance updated or explicit no-op recorded.
- final diff approved:
  - reviewer pass evidence recorded.
- required closure ids closed:
  - Step Contract Closure:
    - all required rows pass or approved no-op.
  - Test Contract Closure:
    - required red/acceptance/negative/regression evidence recorded.
  - Closure Coverage:
    - every required closure id maps to verification evidence.
