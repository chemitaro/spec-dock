---
種別: 実装計画書（Issue）
ID: "iss-00297"
タイトル: "Authoring Command Skeleton"
関連GitHub: ["#297"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md"]
親: ["epic-00295", "init-local-00003"]
---

# iss-00297 Authoring Command Skeleton — 実装計画

## この計画で満たす要件ID

- `AC-001`: installed runtime が `authoring` command group を認識する。
- `AC-002`: `authoring --help` が skeleton command surface と deferred 境界を表示する。
- `AC-003`: 初期 command surface は fail-closed な deferred outcome を返す。
- `AC-004`: deferred outcome は `status=deferred`、`authority=evidence_only`、`command=<command>`、`next_issue=<issue-id>` を安定して含む。
- `AC-005`: deferred command は canonical docs、`.assurance.json`、authorized profile / `set-authorized-profile`、reviewer pass、execution-ready、PR-ready、merge-ready を主張しない。
- `AC-006`: provider-side shipped asset が source of truth で、dogfooding runtime mirror は validation artifact として追従する。
- `EC-001`: GitHub sync、prompt pack、backend invocation、ZIP review/stage、validation、approval check の実質ロジックは後続 Issue へ defer する。
- `EC-002`: 中間 Issue では個別 PR を作成せず、final quality gate Issue `iss-00307` に PR delivery を集約する。

## 依存関係から導く実装順序

1. 既存 parser / registry / command outcome pattern を確認し、command key naming と `CommandSpec` integration point を固定する。
2. provider-side command module で全 deferred command mapping を一元定義する。
3. provider-side parser / registry に `authoring` group を登録し、CLI observable behavior を通す。
4. dogfooding runtime mirror を provider-side 変更へ追従させる。
5. 全 deferred command の diagnostics と `next_issue` mapping を focused tests と direct CLI evidence で確認する。
6. `report.md` に planning repair、実装、検証、reviewer gate、PR defer evidence を記録する。

## ステップ一覧

- `S01`: 既存 runtime command pattern の確認。
- `S02`: provider-side `authoring` command specs と deferred outcome helper の追加。
- `S03`: provider-side parser / registry への `authoring` group 登録。
- `S04`: dogfooding runtime mirror の追従。
- `S05`: focused tests と direct command verification。
- `S90`: docs / report 影響解決。
- `S99`: Issue 最終品質ゲート。

## 要件 ↔ ステップ対応

| 要件ID | owner step | closure id | planned verification |
|---|---|---|---|
| AC-001 | S03 | `cl-001` | focused CLI runtime test and `./spec-dock/scripts/spec-dock authoring --help` |
| AC-002 | S03 | `cl-002` | help output contains `authoring` subcommands and deferred wording |
| AC-003 | S02, S05 | `cl-003` | all deferred commands exit non-zero |
| AC-004 | S02, S05 | `cl-004` | all deferred commands include stable diagnostics and expected `next_issue` |
| AC-005 | S02, S05 | `cl-005` | tests assert forbidden authority claims are absent |
| AC-006 | S04, S05 | `cl-006` | provider/mirror focused assertion and install reachability coverage |
| EC-001 | S02, S05 | `cl-007` | implementation only returns deferred outcome; no backend/GitHub/ZIP logic |
| EC-002 | S90, S99 | `cl-008` | report PR delivery defer evidence and no PR created for this Issue |

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| id | spec link | observable input/state | locked expectation | bug class guarded | required | evidence level | closure owner step |
|---|---|---|---|---|---|---|---|
| `cl-001` | AC-001 | `authoring` top-level command | parser accepts `authoring` and reaches registered command group | command missing from installed runtime | yes | command + focused test | S03 |
| `cl-002` | AC-002 | `authoring --help` | help exposes skeleton command group and does not imply implemented backend behavior | misleading command availability | yes | command + focused test | S03 |
| `cl-003` | AC-003 | each deferred leaf command | command exits non-zero with fail-closed deferred status | deferred command accidentally succeeds | yes | focused test | S05 |
| `cl-004` | AC-004 | each deferred leaf command | output contains `status=deferred`, `authority=evidence_only`, `command=<command>`, expected `next_issue` | wrong follow-up routing or unstable diagnostics | yes | focused test | S05 |
| `cl-005` | AC-005 | each deferred leaf command output | output does not contain canonical docs, `.assurance.json`, authorized profile / `set-authorized-profile`, reviewer pass, execution-ready, PR-ready, or merge-ready success claims | unsafe authority self-claim | yes | focused test | S05 |
| `cl-006` | AC-006 | provider and dogfooding runtime files | provider source exists and dogfooding mirror has same command surface | repo-local implementation not shipped to consumers | yes | structural assertion + init/update coverage | S04/S05 |
| `cl-007` | EC-001 | source diff and command behavior | no substantive GitHub sync, backend invocation, ZIP review/stage, validation, or approval logic is implemented in this Issue | scope creep into later Issues | yes | diff inspection + focused test | S02/S99 |
| `cl-008` | EC-002 | `report.md` and git/PR state | no per-Issue PR delivery claim; final PR delivery remains assigned to `iss-00307` | fragmented PR workflow | yes | report evidence + final gate inspection | S90/S99 |

## 実装ステップ

### S01 既存 runtime command pattern の確認

#### behavior slice execution

既存の parser / registry / command outcome pattern を読み、`authoring` skeleton が既存 runtime architecture に沿って入る最小の integration points を確定する。

#### planned contract

- scope: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/{cli,commands}` と mirror の既存 command patterns の read-only inspection。
- test obligation: inspect-only。既存 `CommandSpec` / `CommandOutcome` / parser binding の shape を確認する。
- red or alternative evidence requirement: `inspect-only`。既存 pattern の誤読を防ぐため、対象 symbol / file を `report.md` に記録する。
- green verification: `rg -n "CommandSpec|CommandOutcome|add_subparsers|build_registry" src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime`.
- refactor guardrail: 既存 runtime command architecture を再構成しない。
- amendment trigger: `authoring` command を追加するために parser / registry 以外の runtime layer restructuring が必要だと判明した場合、plan amendment と re-review を行う。

#### delegation contract

- delegated role: parent orchestrator direct inspection（implementation ではない）。
- input docs: `requirement.md`, `design.md`, `plan.md`, `spec-dock/docs/authoring/issue-plan.md`.
- allowed paths: read-only inspection only.
- forbidden changes: source file mutation、runtime architecture change。
- acceptance criteria: integration points と command outcome pattern が `report.md` に記録される。
- required tests or docs-only verification: `rg` inspection command。
- reviewer focus: spec-reviewer は planning contract、code-reviewer は後続 diff alignment。
- stop conditions: 既存 pattern が設計と矛盾、または scope 外 architecture change が必要。
- output required: inspected files、chosen integration points、No material implementation decisions beyond the approved plan.

#### 具体テストケース一覧

- `tc-s01-001` inspect: command pattern を確認できる
  - 前提: runtime command modules, parser, registry が provider-side shipped assets に存在する。
  - 操作: `rg -n "CommandSpec|CommandOutcome|add_subparsers|build_registry" src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime` を実行する。
  - 期待結果: authoring skeleton の追加先として `commands/`, `cli/parser.py`, `cli/registry.py` が確認できる。
  - 失敗検出: monolithic command 追加や provider source of truth 逸脱のリスクを検出する。
  - 検証方法: command output を `report.md` の実装記録へ要約する。
  - 関連 closure id: `cl-001`, `cl-006`

#### step closure contract

- existing pattern inspection completed.
- implementation target files remain the files listed in `design.md`.
- no source mutation occurs in this step.

#### report evidence destination

- `report.md` の `実装記録（セッションログ）` と `Test Contract Closure`。

#### step gate

- S01 evidence recorded before S02 mutation starts.

### S02 provider-side `authoring` command specs と deferred outcome helper の追加

#### behavior slice execution

provider-side `commands/authoring.py` を追加し、全 deferred command key、human-readable command path、expected `next_issue`、shared fail-closed outcome を一元定義する。

#### planned contract

- scope: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py`.
- test obligation: all deferred leaf commands have a single mapping source.
- red or alternative evidence requirement: `covered-existing` by focused tests added in S05; S02 itself must keep code minimal and deterministic.
- green verification: source inspection and later S05 tests over all mappings.
- refactor guardrail: backend invocation, GitHub sync, ZIP handling, validation, approval logicを実装しない。
- amendment trigger: deferred command が実際の mutation / backend call / canonical adoption を必要とする場合、scope creep として stop し plan amendment。

#### delegation contract

- delegated role: dev-coder.
- input docs: `requirement.md`, `design.md`, this `plan.md`, existing command modules under provider runtime.
- allowed paths: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py`.
- forbidden changes: parser / registry / mirror / tests in this step; any real GitHub / backend / ZIP / approval logic.
- acceptance criteria: `command_specs()` が全 command key を返し、shared deferred runner が `CommandOutcome(exit_code=1, text=CliText(...))` を返す。
- required tests or docs-only verification: S05 all-mapping tests; S02 local inspection.
- reviewer focus: code-reviewer should check no scope creep and stable mapping.
- stop conditions: `CommandOutcome` contract incompatible with fail-closed diagnostic output.
- output required: changed file summary、mapping list、unresolved risk、No material implementation decisions beyond the approved plan.

#### 具体テストケース一覧

- `tc-s02-001` contract: all mapping を一元定義する
  - 前提: provider runtime command module can expose `command_specs()`.
  - 操作: `commands/authoring.py` に deferred command mapping と specs を追加する。
  - 期待結果: mapping は command path と `next_issue` を持ち、後続 tests から列挙できる。
  - 失敗検出: parser 登録と tests が別々の mapping を持ち drift する回帰を検出する。
  - 検証方法: S05 focused test で all mapping を検査する。
  - 関連 closure id: `cl-003`, `cl-004`

- `tc-s02-002` negative: deferred outcome は authority claim をしない
  - 前提: all command leaves still deferred.
  - 操作: shared deferred runner を実装する。
  - 期待結果: output は `status=deferred` と `authority=evidence_only` を含み、canonical docs、`.assurance.json`、authorized profile / `set-authorized-profile`、success / pass / ready claim を含まない。
  - 失敗検出: skeleton command が reviewer pass や PR-ready を自称する危険を検出する。
  - 検証方法: S05 focused test で forbidden phrases absence を検査する。
  - 関連 closure id: `cl-005`, `cl-007`

#### step closure contract

- provider command module exists.
- no parser / registry / mirror mutation yet unless S03 starts.
- no real backend / GitHub / ZIP logic exists in new module.

#### report evidence destination

- `report.md` の `実装記録（セッションログ）` と `Test Contract Closure`。

#### step gate

- S02 closes only when mapping source exists and S03 can bind to it without duplicating mapping.

### S03 provider-side parser / registry への `authoring` group 登録

#### behavior slice execution

provider-side parser に `authoring` group と deferred leaf subcommands を追加し、registry に `authoring.command_specs()` を登録する。

#### planned contract

- scope: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py`.
- test obligation: top-level help and representative dispatch reach registered command specs.
- red or alternative evidence requirement: `covered-existing` by S05 runtime tests.
- green verification: `./spec-dock/scripts/spec-dock authoring --help` after mirror sync; provider-side tests in S05.
- refactor guardrail: existing command parser layout and registry construction remain intact.
- amendment trigger: parser requires new global dispatch semantics or registry contract change.

#### delegation contract

- delegated role: dev-coder.
- input docs: `design.md`, existing `cli/parser.py`, `cli/registry.py`, `commands/authoring.py`.
- allowed paths: provider parser and registry only.
- forbidden changes: command behavior beyond binding, unrelated parser groups, lifecycle command behavior.
- acceptance criteria: provider runtime can register all authoring specs and parse intended leaf commands.
- required tests or docs-only verification: S05 focused CLI runtime tests.
- reviewer focus: code-reviewer should check parser/registry scope and command-key consistency.
- stop conditions: parser ambiguity, command key mismatch, or need to alter dispatch contract.
- output required: changed files、registered command keys、verification result、No material implementation decisions beyond the approved plan.

#### 具体テストケース一覧

- `tc-s03-001` acceptance: authoring help が表示される
  - 前提: provider parser and registry include authoring group.
  - 操作: mirror sync 後に `./spec-dock/scripts/spec-dock authoring --help` を実行する。
  - 期待結果: command exits 0 and help includes `preflight`, `pack`, `backend`, `validate`, `approval`.
  - 失敗検出: installed runtime に top-level command が出ない回帰を検出する。
  - 検証方法: direct command and focused CLI runtime test.
  - 関連 closure id: `cl-001`, `cl-002`

- `tc-s03-002` routing: representative leaf command が runner に到達する
  - 前提: parser leaf command is bound to registry command key.
  - 操作: `authoring preflight github-sync` and `authoring pack prepare` を実行する。
  - 期待結果: parser error ではなく deferred outcome が返る。
  - 失敗検出: parser binding / registry key mismatch を検出する。
  - 検証方法: S05 all deferred command test.
  - 関連 closure id: `cl-003`, `cl-004`

#### step closure contract

- parser and registry changes compile.
- no unrelated command group behavior changes.
- all parser leaf keys correspond to `commands/authoring.py` specs.

#### report evidence destination

- `report.md` の `実装記録（セッションログ）` と `Test Contract Closure`。

#### step gate

- S03 closes after S04 mirror sync makes direct dogfooding CLI runnable.

### S04 dogfooding runtime mirror の追従

#### behavior slice execution

provider-side runtime changesを `spec-dock/scripts/spec_dock_runtime/` mirrorへ反映し、dogfooding CLI で同じ command surface を観測できるようにする。

#### planned contract

- scope: `spec-dock/scripts/spec_dock_runtime/commands/authoring.py`, `spec-dock/scripts/spec_dock_runtime/cli/parser.py`, `spec-dock/scripts/spec_dock_runtime/cli/registry.py`.
- test obligation: dogfooding CLI surface equals provider-side intended command surface.
- red or alternative evidence requirement: `covered-existing` by mirror parity / init/update focused tests where available.
- green verification: `./spec-dock/scripts/spec-dock authoring --help` and focused mirror parity test.
- refactor guardrail: mirror is validation artifact only; provider source remains source of truth.
- amendment trigger: mirror differs intentionally from provider; require explicit report decision and likely follow-up.

#### delegation contract

- delegated role: dev-coder.
- input docs: provider changed files, `AGENTS.md` dogfooding rules.
- allowed paths: dogfooding runtime mirror files listed in scope.
- forbidden changes: canonical implementation under `src/` beyond already completed S02/S03; dogfooding data unrelated to active Issue.
- acceptance criteria: mirror contains authoring command module and parser/registry registration matching provider.
- required tests or docs-only verification: direct dogfooding command and focused parity/install tests.
- reviewer focus: code-reviewer should check provider-first and mirror parity.
- stop conditions: mirror cannot be updated without generated overwrite or provider/mirror divergence.
- output required: changed files、parity evidence、No material implementation decisions beyond the approved plan.

#### 具体テストケース一覧

- `tc-s04-001` acceptance: dogfooding CLI で authoring help が通る
  - 前提: mirror files reflect provider-side command skeleton.
  - 操作: `./spec-dock/scripts/spec-dock authoring --help` を実行する。
  - 期待結果: command exits 0 and displays the authoring group.
  - 失敗検出: provider には実装したが consumer/dogfooding runtime に届かない回帰を検出する。
  - 検証方法: direct command output and focused test.
  - 関連 closure id: `cl-001`, `cl-006`

- `tc-s04-002` install reachability: initialized consumer receives command skeleton
  - 前提: provider assets are copied by `spec-dock init`.
  - 操作: focused init/update test or smoke targetで installed runtime file inventory を確認する。
  - 期待結果: consumer repo includes `spec-dock/scripts/spec_dock_runtime/commands/authoring.py`.
  - 失敗検出: repo-local mirror onlyで shipped asset に含まれない回帰を検出する。
  - 検証方法: `tests/unit/infra/test_init_update.py` focused coverage or equivalent.
  - 関連 closure id: `cl-006`

#### step closure contract

- dogfooding mirror files match provider command surface.
- direct dogfooding CLI help no longer fails with unknown command.

#### report evidence destination

- `report.md` の `実装記録（セッションログ）` と `Test Contract Closure`。

#### step gate

- S04 closes before all-command direct verification in S05.

### S05 focused tests と direct command verification

#### behavior slice execution

全 deferred leaf command の exit code、diagnostics、expected `next_issue`、forbidden authority claim absence を focused tests と direct commands で検証する。

#### planned contract

- scope: `tests/cli_runtime/` または `tests/unit/infra/test_init_update.py`; direct CLI commands.
- test obligation: every deferred command in design is tested, not just representative examples.
- red or alternative evidence requirement: `red-required` where adding focused tests; direct command evidence is supplemental.
- green verification: focused pytest, direct `authoring --help`, representative direct deferred commands, `./spec-dock/scripts/spec-dock validate`.
- refactor guardrail: tests assert public CLI behavior and do not reach private helper internals unless needed for mapping completeness.
- amendment trigger: any command cannot be tested through public CLI because parser surface is incomplete.

#### delegation contract

- delegated role: dev-coder.
- input docs: `requirement.md`, `design.md`, this `plan.md`, target test harness files.
- allowed paths: focused test files under `tests/cli_runtime/` or `tests/unit/infra/test_init_update.py`.
- forbidden changes: broad test harness refactor, unrelated snapshot churn, weakening existing assertions.
- acceptance criteria: all deferred command mappings are covered for diagnostics and forbidden claims.
- required tests or docs-only verification: focused pytest and direct command verification.
- reviewer focus: qa-reviewer should check obligation coverage across all leaf commands.
- stop conditions: focused tests require a broad harness rewrite or cannot observe CLI output.
- output required: test file changes、commands run、results、unresolved risks、No material implementation decisions beyond the approved plan.

#### 全 deferred command mapping

| command | expected next_issue |
|---|---|
| `authoring preflight github-sync` | `iss-00298` |
| `authoring pack prepare` | `iss-00299` |
| `authoring backend invoke` | `iss-00300` |
| `authoring pack review` | `iss-00301` |
| `authoring pack stage` | `iss-00301` |
| `authoring validate initiative-epic-candidates` | `iss-00302` |
| `authoring validate epic-issue-candidates` | `iss-00302` |
| `authoring validate issue-draft-adoption` | `iss-00303` |
| `authoring validate selected-skeleton-fill` | `iss-00303` |
| `authoring approval check` | `iss-00305` |

#### 具体テストケース一覧

- `tc-s05-001` acceptance: all deferred commands fail closed
  - 前提: all command leaves are registered.
  - 操作: focused pytest parametrizes every command listed in the mapping table.
  - 期待結果: each command exits non-zero and includes `status=deferred`, `authority=evidence_only`, `command=<command>`, and expected `next_issue`.
  - 失敗検出: unregistered command、wrong next Issue、accidental success を検出する。
  - 検証方法: focused CLI runtime test.
  - 関連 closure id: `cl-003`, `cl-004`

- `tc-s05-002` negative: authority self-claims are absent
  - 前提: deferred output is captured for every command.
  - 操作: output textを forbidden phrase list against canonical docs / `.assurance.json` / authorized profile / `set-authorized-profile` / reviewer pass / execution-ready / PR-ready / merge-ready claims で検査する。
  - 期待結果: forbidden authority claims are absent.
  - 失敗検出: skeleton command が downstream authority を偽装する回帰を検出する。
  - 検証方法: focused CLI runtime test.
  - 関連 closure id: `cl-005`, `cl-007`

- `tc-s05-003` acceptance: authoring help exposes command groups
  - 前提: dogfooding mirror has parser registration.
  - 操作: `./spec-dock/scripts/spec-dock authoring --help` and focused CLI test.
  - 期待結果: help includes all command groups without claiming concrete implementation.
  - 失敗検出: command group hidden or misleading help text.
  - 検証方法: direct command and focused CLI test.
  - 関連 closure id: `cl-001`, `cl-002`

- `tc-s05-004` regression: SpecDock structure remains valid
  - 前提: active Issue docs and runtime files are changed.
  - 操作: `./spec-dock/scripts/spec-dock validate`.
  - 期待結果: validation passes.
  - 失敗検出: dogfooding docs / active links / dependency graph breakage.
  - 検証方法: direct command.
  - 関連 closure id: `cl-008`

#### step closure contract

- focused tests cover every command in the mapping table.
- direct help and representative deferred commands are recorded.
- validate passes.

#### report evidence destination

- `report.md` の `Test Contract Closure`、`Final QA Gate`、`実装記録（セッションログ）`。

#### step gate

- S05 closes only after all required test commands are run or a documented blocker is recorded.

## S90 docs 影響解決 / docs 更新（S90 docs impact resolution / docs refresh）

### planned contract

- scope: active Issue `report.md` only unless implementation shows help/docs mismatch that requires planned docs amendment.
- test obligation: docs impact is inspected and either resolved or explicitly deferred.
- red or alternative evidence requirement: `inspect-only`.
- green verification: `report.md` records command surface and PR delivery defer evidence.
- refactor guardrail: do not update broader workflow docs in this Issue.
- amendment trigger: user-facing workflow docs become inaccurate because of this skeleton command.

### delegation contract

- delegated role: parent orchestrator; doc-writer only if broader shipped docs need edits.
- input docs: implementation diff, command help output, Epic PR delivery policy.
- allowed paths: active Issue `report.md`; broader docs only after plan amendment.
- forbidden changes: shipped workflow docs without explicit need.
- acceptance criteria: report records verification and no-per-Issue PR rationale.
- required tests or docs-only verification: inspect report ledger.
- reviewer focus: spec-reviewer docs/spec alignment.
- stop conditions: documentation impact exceeds active Issue report.
- output required: docs impact decision and evidence.

### 具体テストケース一覧

- `tc-s90-001` inspect: report ledger resolves docs and PR delivery impact
  - 前提: implementation and verification have completed.
  - 操作: `report.md` を更新し、docs impact and PR defer evidenceを記録する。
  - 期待結果: no unresolved docs impact remains for this Issue; PR delivery remains assigned to `iss-00307`.
  - 失敗検出: intermediate Issue が PR-ready / merge-ready を主張する回帰を検出する。
  - 検証方法: report inspection and final spec-reviewer.
  - 関連 closure id: `cl-008`

### step closure contract

- `report.md` reflects all planned evidence and reviewer states.

### report evidence destination

- `report.md` の `PR delivery defer evidence` と `Final Quality Gate`。

### step gate

- S90 closes before final reviewer gates.

## S99 最終品質ゲート（S99 final quality gate）

### planned contract

- scope: whole Issue diff and active Issue artifacts.
- test obligation: code-reviewer, qa-reviewer, final spec-reviewer pass or documented blocker.
- red or alternative evidence requirement: reviewer gates are manual-required.
- green verification: focused tests, validate, `git diff --check`, reviewer pass results.
- refactor guardrail: reviewer-fail fixes must stay inside Issue scope; scope-expanding fixes require plan amendment and re-review.
- amendment trigger: reviewer identifies missing requirement/design/plan obligation or scope creep.

### delegation contract

- delegated role: reviewers (`code-reviewer`, `qa-reviewer`, `spec-reviewer`); parent orchestrator integrates fixes.
- input docs: requirement/design/plan/report and implementation diff.
- allowed paths: active Issue docs/report and Issue-scoped implementation/test files.
- forbidden changes: unrelated refactor, PR creation, next Issue implementation.
- acceptance criteria: all final local gates pass and commit candidate is ready.
- required tests or docs-only verification: focused pytest, validate, diff check, reviewer gates.
- reviewer focus: code correctness/scope, QA coverage, spec alignment.
- stop conditions: unresolved P0/P1 reviewer finding, failing required command, dirty unexpected files.
- output required: reviewer verdicts, fixes, final commit scope, PR defer evidence.

### 具体テストケース一覧

- `tc-s99-001` final gate: issue-wide local gates pass
  - 前提: implementation, S05 verification, and report update are complete.
  - 操作: run `git diff --check`, required focused tests, `validate`, code-reviewer, qa-reviewer, final spec-reviewer.
  - 期待結果: all gates pass or blocker is recorded; no per-Issue PR is created.
  - 失敗検出: incomplete local quality gate or PR delivery policy violation.
  - 検証方法: command outputs and reviewer verdicts recorded in `report.md`.
  - 関連 closure id: `cl-001`..`cl-008`

### step closure contract

- all required closure ids are closed in `report.md`.
- final local reviewers pass.
- commit candidate is ready.
- issue finish may run after commit and clean post-commit check.

### report evidence destination

- `report.md` の `最終品質ゲート（Final Quality Gate）`、`Final Commit`、`Test Contract Closure`。

### step gate

- S99 is the last local gate before commit and `issue finish`.

## Final Exit Contract

- `requirement.md`, `design.md`, `plan.md`, `report.md` are current and reviewer-gated.
- all `required=yes` closure rows in `Spec-Locked Closure Index` have observed closure evidence in `report.md`.
- all focused tests and direct commands required by S05 have observed results in `report.md`.
- code-reviewer, qa-reviewer, and final spec-reviewer pass are recorded.
- the final commit includes only Issue-scoped docs, implementation, tests, and dogfooding mirror changes.
- this intermediate Issue does not create a PR; after `issue finish`, execution relays to `iss-00298`.

## Relay / PR delivery

この Issue は中間 Issue であるため、個別 PR は作成しない。実装完了後は `issue finish` し、次の `iss-00298` へ進む。Epic 単位の PR delivery は final quality gate Issue `iss-00307` に集約する。
