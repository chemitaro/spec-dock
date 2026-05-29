---
種別: 実装計画書（Issue）
ID: "iss-00137"
タイトル: "Worktree list show remove commands"
関連GitHub: ["#137"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-29"
依存: ["requirement.md", "design.md"]
親: ["epic-00107", "init-local-00002"]
---

# iss-00137 Worktree list show remove commands — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001 list text
  - AC-002 list json
  - AC-003 show target
  - AC-004 ambiguous target
  - AC-005 unsupported branch target
  - AC-006 remove clean managed worktree
  - AC-007 remove json
  - AC-008 remove dirty or locked
  - AC-009 force remove dirty or locked
  - AC-010 non-removable guards
  - AC-011 env fail-fast
  - AC-012 stale diagnostics
  - AC-013 no delete alias
- EC:
  - EC-001 stale planning hint / revalidation
  - EC-002 unmanaged worktree
  - EC-003 main/current worktree
  - EC-004 ambiguous target
  - EC-005 stale record / orphan directory diagnostic only
- 制約:
  - provider-side source of truth under `src/spec_dock/assets/spec_dock/...`
  - layered runtime architecture
  - Git-first remove semantics
  - destructive operations only in temp Git repo / temp central root tests
  - no branch deletion, no prune/repair, no `delete` alias, no active/GitHub/SpecDock tree mutation

## 依存関係から導く実装順序
- 依存関係の正本:
  - `design.md` の module dependency、interface contract、sequence delta、file/module change plan。
- 順序ルール:
  - shared contracts / ports / helper model を先に固定する。
  - inventory/show は remove の target resolver と classification の prerequisite として先に閉じる。
  - destructive remove は JSON/text contract と target resolver が固定されてから閉じる。
  - shipped docs は runtime behavior と JSON schema が実装済みになってから更新する。
- step 依存サマリー:
  - S01:
    - 依存: reviewer-passed requirement/design
    - unblock: S02, S03
    - 対象ファイル: application contracts/ports/worktree helpers, infra filesystem adapter skeleton if needed
  - S02:
    - 依存: S01
    - unblock: S03
    - 対象ファイル: parser, commands, presentation, worktree list/show use cases, runtime tests
  - S03:
    - 依存: S01, S02
    - unblock: S90, S99
    - 対象ファイル: remove use case, Git/filesystem adapters, commands/presentation, destructive safety tests
  - S90:
    - 依存: S02, S03
    - unblock: S99
    - 対象ファイル: provider docs and dogfooding docs
  - S99:
    - 依存: S01, S02, S03, S90
    - unblock: implementation handoff / PR readiness
    - 対象ファイル: report only if recording final evidence during execution

## ステップ一覧
- S01 contract and shared model:
  - 観測可能な振る舞い:
    - list/show/remove use cases can validate central root before Git, derive namespace from Git main record after listing, classify records, and expose stable result/error models without CLI wiring.
  - 依存:
    - reviewer-passed `requirement.md` / `design.md`
  - unblock:
    - S02, S03
  - 対象ファイル:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_cli.py` if needed
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py` only for port wiring skeleton if needed
  - 閉じる要件:
    - AC-002, AC-003, AC-010, AC-011, AC-012, EC-001, EC-002, EC-003, EC-005
  - レビューゲート:
    - code-reviewer for application contracts and safety invariants
- S02 list/show command and JSON/text output:
  - 観測可能な振る舞い:
    - `worktree list` / `show` support text and JSON output, stable ids, target resolution, ambiguity failure, unsupported branch target failure, and env fail-fast.
  - 依存:
    - S01
  - unblock:
    - S03
  - 対象ファイル:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
    - `tests/cli_runtime/test_worktree.py`
  - 閉じる要件:
    - AC-001, AC-002, AC-003, AC-004, AC-005, AC-011, AC-012
  - レビューゲート:
    - code-reviewer for CLI/runtime/tests
- S03 remove command, Git integration, and destructive safety:
  - 観測可能な振る舞い:
    - `worktree remove` removes only managed non-main non-current targets, honors Git default/force semantics, cleans remaining individual directory after Git success, refuses unsafe targets, and returns JSON/text success/failure.
  - 依存:
    - S01, S02
  - unblock:
    - S90, S99
  - 対象ファイル:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_cli.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
    - `tests/cli_runtime/test_worktree.py`
  - 閉じる要件:
    - AC-006, AC-007, AC-008, AC-009, AC-010, AC-011, AC-013, EC-001, EC-002, EC-003, EC-004, EC-005
  - レビューゲート:
    - code-reviewer for destructive safety and tests
- S90 docs impact resolution:
  - 観測可能な振る舞い:
    - shipped and dogfooding worktree references describe create/list/show/remove current scope and status/prune/repair future scope.
  - 依存:
    - S02, S03
  - unblock:
    - S99
  - 対象ファイル:
    - `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`
    - `src/spec_dock/assets/spec_dock/docs/guide.md` if command list needs updating
    - `spec-dock/docs/reference_worktree.md`
    - `spec-dock/docs/guide.md` if dogfooding parity requires it
  - 閉じる要件:
    - docs impact for AC-001..AC-013 and parent E-AC-011
  - レビューゲート:
    - spec-reviewer for docs/spec alignment
- S99 final quality gate:
  - 観測可能な振る舞い:
    - all closure ids have evidence in `report.md`, targeted tests pass, `validate` and diff checks pass, and final reviewers pass.
  - 依存:
    - S01, S02, S03, S90
  - unblock:
    - implementation-ready completion / PR workflow
  - 対象ファイル:
    - `spec-dock/active/issue/report.md`
  - 閉じる要件:
    - all AC/EC/constraints
  - レビューゲート:
    - qa-reviewer and final spec-reviewer

## 要件 ↔ ステップ対応
- AC-001 -> S02
- AC-002 -> S01, S02
- AC-003 -> S01, S02
- AC-004 -> S01, S02, S03
- AC-005 -> S01, S02
- AC-006 -> S03
- AC-007 -> S03
- AC-008 -> S03
- AC-009 -> S03
- AC-010 -> S01, S03
- AC-011 -> S01, S02, S03
- AC-012 -> S01, S02
- AC-013 -> S03
- EC-001 -> S03
- EC-002 -> S01, S02, S03
- EC-003 -> S01, S03
- EC-004 -> S01, S02, S03
- EC-005 -> S01, S02, S03

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ（step） | スライス（slice） | 種別（type） | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル（evidence level） | クロージャ証跡（closure evidence） |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | contract-model | invariant | AC-002, AC-003, AC-010, AC-011, AC-012 | central root validation precedes Git/filesystem; namespace derives from Git main record; stable ids and blockers are deterministic | application use case tests or runtime characterization | wrong namespace, unsafe target model, unstable ids | yes | red-required | report Test Contract Closure |
| tc-002 | S02 | list-show | acceptance | AC-001, AC-002, AC-003 | list/show text and JSON expose required fields and resolve id/path/basename | temp repo with main, managed, unmanaged worktrees | agent cannot discover/select worktrees | yes | red-required | report Test Contract Closure |
| tc-003 | S02 | target-errors | negative | AC-004, AC-005, AC-011, AC-012 | ambiguous/branch/env/stale diagnostics are observable and no removal occurs | ambiguous basename/id, branch-only target, invalid root, stale record | silent wrong target selection | yes | red-required | report Test Contract Closure |
| tc-004 | S03 | remove-clean | acceptance | AC-006, AC-007 | clean managed remove deletes Git record and individual directory, leaves branch, returns JSON fields | temp managed worktree with removable state and leftover directory/cache after Git success | incomplete cleanup or branch deletion | yes | red-required | report Test Contract Closure |
| tc-005 | S03 | remove-guards | negative | AC-008, AC-010, EC-001, EC-002, EC-003, EC-004 | dirty/default refusal, main/current/unmanaged/ambiguous guards, and revalidation prevent deletion | temp dirty/untracked worktree, main/current/unmanaged targets, state change before remove | destructive unsafe deletion | yes | red-required | report Test Contract Closure |
| tc-006 | S03 | remove-force-containment | negative/acceptance | AC-009, AC-010, AC-013 | `--force` maps to Git force only; no `delete` alias; pre-Git and post-Git containment prevent namespace/repo/symlink escape deletion | dirty managed target, unsafe containment fixtures, parser call to delete | force bypasses SpecDock guard | yes | red-required | report Test Contract Closure |
| tc-007 | S90 | docs-parity | docs | AC-001..AC-013, parent E-AC-011 | provider and dogfooding docs describe command scope, JSON, remove safety, and future status/prune/repair boundary | docs inspection and targeted grep | stale docs mislead agents | yes | inspect-only | report Step Contract Closure |
| tc-008 | S99 | final-quality | final gate | all AC/EC/constraints | targeted tests, validate, diff check, reviewer gates, and report closure evidence are complete | final command outputs and reviewer verdicts | incomplete handoff | yes | manual-required | report Final Quality Gate |

## レビュー / QA ゲート方針
- RG-S01:
  - reviewer: code-reviewer
  - focus: contracts, root ordering, stable ids, blocker invariants
- RG-S02:
  - reviewer: code-reviewer
  - focus: CLI parser, JSON/text rendering, target resolution failures
- RG-S03:
  - reviewer: code-reviewer
  - focus: destructive safety, Git-first semantics, containment, force behavior
- RG-S90:
  - reviewer: spec-reviewer
  - focus: docs/spec alignment and stale future-scope wording
- QG1:
  - reviewer: qa-reviewer
  - focus: obligation coverage and missing high-value destructive tests
- SG1:
  - reviewer: spec-reviewer
  - focus: requirement/design/plan/report/docs alignment before final handoff

## 実行ルール（全ステップ共通）
- 実装は provider-side `src/spec_dock/assets/spec_dock/...` を先に変更する。
- dogfooding `spec-dock/...` は docs parity / validation surface として扱う。
- destructive tests must use temp Git repo and temp `SPEC_DOCK_WORKTREE_ROOT`; never target this live checkout.
- Expected JSON failures must not fall through to global dispatch text fallback.
- New material decisions require report Decision Ledger entry and may require plan amendment / re-review.

## 実装ステップ

### 実装ステップ S01 — Contract and Shared Worktree Model
- 振る舞いの目標（behavior goal）:
  - list/show/remove の shared request/result/error model、central root validation order、main-record namespace derivation、stable id algorithm、remove blocker model を fixed contract にする。
- design 参照:
  - `インターフェース契約`
  - `クラス / インターフェース詳細設計`
- 依存:
  - reviewer-passed requirement/design
- unblock:
  - S02, S03
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_cli.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py`
- 計画済み契約（planned contract）:
  - scope:
    - Add worktree list/show/remove dataclasses and expected error model.
    - Add or refactor shared root validation and namespace derivation helpers.
    - Add stable id and remove blocker calculation.
    - Add filesystem port skeleton if needed.
  - テスト義務（test obligation）:
    - closure id:
      - tc-001
    - coverage rationale:
      - Root ordering, namespace derivation, id stability, and blockers are prerequisites for every user-facing command and destructive guard.
  - Red / 代替証跡の要件:
    - red-required:
      - Add focused unit/runtime characterization that fails before the new use case helpers exist or before they enforce the design order.
  - Green 検証:
    - `uv run pytest tests/cli_runtime/test_worktree.py`
    - If unit tests are split out, run the new focused test file.
  - Refactor / cleanup ガードレール:
    - Keep refactor limited to worktree helpers needed by create/list/show/remove.
    - Do not introduce a persisted worktree registry.
  - amendment trigger（plan amendment が必要になる契機）:
    - If stable id cannot be deterministic without persistence.
    - If root validation cannot be shared with create without changing create behavior.

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - dev-coder
- 正本（source of truth）:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - provider runtime files under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/...`
  - When generated/dogfooding files differ from provider runtime files, provider-side source is authoritative.
- 入力 docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/authoring/issue-plan.md`
- 許可 paths:
  - S01 対象ファイルのみ。
- 禁止 changes:
  - CLI command exposure beyond helper wiring.
  - docs updates.
  - branch deletion, prune/repair, GitHub/active/spec tree mutation.
- 受け入れ条件:
  - tc-001 closes with tests or explicit characterization evidence.
- 必須 tests または docs-only verification:
  - focused runtime/unit tests and `git diff --check`.
- reviewer focus:
  - code-reviewer: model correctness, ordering, safety invariants.
- 必須出力（output required）:
  - changed files, verification result, unresolved risks.
  - Ledger Note or `No material implementation decisions beyond the approved plan.`
- 停止条件（stop conditions）:
  - Need to add persistence.
  - Need to change existing `worktree create` output/behavior.
  - Cannot write a test for ordering/safety.

#### 具体テストケース一覧

- `tc-s01-001` invariant: root validation precedes Git listing
  - 前提: env root is missing/invalid and Git gateway would fail if called.
  - 操作: call list/show/remove use case or focused runtime path with invalid `SPEC_DOCK_WORKTREE_ROOT`.
  - 期待結果: root error is returned before Git listing/removal or filesystem cleanup.
  - 失敗検出: implementation calls Git before env/root validation.
  - 検証方法: focused test using fake ports or runtime env failure assertion.
  - 関連 closure id: tc-001

- `tc-s01-002` invariant: namespace derives from Git main record
  - 前提: command runs from a linked worktree whose path basename differs from the main worktree basename.
  - 操作: classify worktree records after root validation and Git list.
  - 期待結果: managed namespace uses main worktree basename, not current linked worktree basename.
  - 失敗検出: chained namespace such as `<linked-basename>/` is used.
  - 検証方法: focused helper test or existing linked-worktree fixture extended for list/show.
  - 関連 closure id: tc-001

- `tc-s01-003` invariant: stable id disambiguation
  - 前提: managed, main, and unmanaged records include duplicate basename-derived ids.
  - 操作: build `WorktreeRecordView` list.
  - 期待結果: JSON ids are deterministic and unique; duplicate later records get `~2`, `~3`.
  - 失敗検出: duplicate ids make `show <id>` ambiguous or unstable without candidates.
  - 検証方法: focused application helper test.
  - 関連 closure id: tc-001

#### ステップ完了契約（step closure contract）
- closure id:
  - tc-001
- close 条件:
  - Shared model and helper tests pass.
- 検証 evidence:
  - focused test command output.
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage.
- 残リスク:
  - none, or explicit discovered test recorded in report.

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: code-reviewer
  - review 範囲: S01 changed files and tests
  - pass 条件: `review_status: pass`
  - re-review rule: 指摘を修正し pass まで再実行
- commit / no-op gate:
  - closure 状態: committed or approved-no-op
  - commit 範囲: S01 files only. If later changes need the same files, close S01 first or amend/split the plan rather than batching multiple steps into one commit.

### 実装ステップ S02 — List/Show CLI, Target Resolution, and JSON/Text Output
- 振る舞いの目標（behavior goal）:
  - `worktree list` / `show` を CLI から使えるようにし、agent-first JSON と expected JSON failures を固定する。
- design 参照:
  - `インターフェース契約`
  - `要件 → 設計マッピング`
- 依存:
  - S01
- unblock:
  - S03
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
  - `tests/cli_runtime/test_worktree.py`
- 計画済み契約（planned contract）:
  - scope:
    - Add parser bindings and typed args for list/show.
    - Add `--json` for both.
    - Implement list/show text and JSON renderers.
    - Ensure expected failures under `--json` return `status=error`.
  - テスト義務（test obligation）:
    - closure id:
      - tc-002
      - tc-003
    - coverage rationale:
      - Agent selection relies on stable JSON and unambiguous target errors.
  - Red / 代替証跡の要件:
    - red-required:
      - Add runtime tests that fail before parser/use case/rendering exists.
  - Green 検証:
    - `uv run pytest tests/cli_runtime/test_worktree.py`
  - Refactor / cleanup ガードレール:
    - Do not implement remove in this step except shared resolver code needed by show.
  - amendment trigger:
    - If argparse/global dispatch cannot support JSON expected failures without broader command outcome changes.

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - dev-coder
- 正本（source of truth）:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - provider runtime parser/command/presentation files under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/...`
  - Existing runtime tests are authoritative for current behavior characterization until this step updates them.
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, runtime parser/command/presentation files.
- 許可 paths:
  - S02 対象ファイルのみ.
- 禁止 changes:
  - Git remove or filesystem cleanup behavior beyond resolver scaffolding.
  - docs updates.
- 受け入れ条件:
  - tc-002 and tc-003 close with runtime tests.
- 必須 tests または docs-only verification:
  - `uv run pytest tests/cli_runtime/test_worktree.py`.
- reviewer focus:
  - code-reviewer: parser shape, JSON schema, expected failure handling.
- 必須出力（output required）:
  - changed files, test output, unresolved risks, Ledger Note if material.
- 停止条件:
  - Need to change top-level dispatch globally without design amendment.
  - Cannot produce JSON error payload for expected failures.

#### 具体テストケース一覧

- `tc-s02-001` acceptance: list text and JSON inventory
  - 前提: temp repo has main checkout, one managed linked worktree, and one unmanaged linked worktree.
  - 操作: run `spec-dock worktree list` and `spec-dock worktree list --json`.
  - 期待結果: text shows id/path/branch/managed/removable summary; JSON has `worktrees[]` with required fields and managed/unmanaged/main/current distinction.
  - 失敗検出: agent cannot distinguish or select worktrees from output.
  - 検証方法: runtime assertions in `tests/cli_runtime/test_worktree.py`.
  - 関連 closure id: tc-002

- `tc-s02-002` acceptance: show resolves id/path/basename
  - 前提: `list --json` returns a managed worktree id.
  - 操作: run `show <id> --json`, `show <absolute-path> --json`, and `show <basename> --json`.
  - 期待結果: all forms resolve to the same worktree detail payload.
  - 失敗検出: accepted target forms diverge or branch names are required.
  - 検証方法: runtime assertions.
  - 関連 closure id: tc-002

- `tc-s02-003` negative: ambiguous and branch-only targets
  - 前提: fixture has ambiguous basename/id candidates and a branch name that matches no accepted target form.
  - 操作: run `show <ambiguous> --json` and `show <branch-name> --json`.
  - 期待結果: ambiguous returns `status=error` with candidates; branch-only target fails without resolving by branch.
  - 失敗検出: command silently picks a target or accepts branch name.
  - 検証方法: runtime assertions.
  - 関連 closure id: tc-003

- `tc-s02-004` negative: env fail-fast for list/show
  - 前提: `SPEC_DOCK_WORKTREE_ROOT` is missing, blank, relative, file, or broken symlink.
  - 操作: run `list --json` and `show wt1 --json`.
  - 期待結果: command fails with JSON error and performs no Git worktree listing/removal or filesystem cleanup.
  - 失敗検出: invalid env still yields partial inventory or text-only fallback.
  - 検証方法: runtime or fake-port assertions.
  - 関連 closure id: tc-003

#### ステップ完了契約（step closure contract）
- closure id:
  - tc-002
  - tc-003
- close 条件:
  - list/show runtime tests pass and JSON schema assertions cover expected success/failure.
- 検証 evidence:
  - `uv run pytest tests/cli_runtime/test_worktree.py`
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage.
- 残リスク:
  - any JSON schema compromise must be reported and may require design/plan amendment.

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: code-reviewer
  - review 範囲: S02 changed files and tests
  - pass 条件: `review_status: pass`
  - re-review rule: 指摘を修正し pass まで再実行
- commit / no-op gate:
  - closure 状態: committed or approved-no-op

### 実装ステップ S03 — Remove Command, Git-First Semantics, and Containment
- 振る舞いの目標（behavior goal）:
  - `worktree remove` を Git-first semantics と containment guard 付きで実装し、clean/default/force/unsafe target cases を閉じる。
- design 参照:
  - `シーケンス差分`
  - `pre-Git remove containment guard`
  - `post-Git cleanup containment guard`
- 依存:
  - S01, S02
- unblock:
  - S90, S99
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_cli.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
  - `tests/cli_runtime/test_worktree.py`
- 計画済み契約（planned contract）:
  - scope:
    - Add parser/args for remove target, `--force`, `--json`.
    - Add Git remove adapter and post-success filesystem cleanup.
    - Implement pre-Git and post-Git containment guard.
    - Implement JSON success and expected failure payloads.
  - テスト義務（test obligation）:
    - closure id:
      - tc-004
      - tc-005
      - tc-006
    - coverage rationale:
      - This step is destructive and must prove both allowed cleanup and all non-bypassable guards.
  - Red / 代替証跡の要件:
    - red-required:
      - Add destructive safety runtime tests before implementation.
  - Green 検証:
    - `uv run pytest tests/cli_runtime/test_worktree.py`
  - Refactor / cleanup ガードレール:
    - Do not add branch deletion, prune, repair, or orphan cleanup.
    - Do not remove namespace parent directory.
  - amendment trigger:
    - If Git default remove behavior for untracked files differs across supported Git versions enough to change AC-008/AC-009 expectations.
    - If safe containment cannot be guaranteed through canonical path checks.

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - dev-coder
- 正本（source of truth）:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - provider runtime files under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/...`
  - Git's `worktree remove` behavior is authoritative for clean/default/`--force` dirty or locked refusal semantics; SpecDock design is authoritative for managed-only, current/main/unmanaged, containment, and no-branch-delete guards.
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, Git adapter, test harness.
- 許可 paths:
  - S03 対象ファイルのみ.
- 禁止 changes:
  - `worktree delete` alias.
  - branch deletion.
  - prune/repair/orphan cleanup.
  - live checkout operations outside temp tests.
- 受け入れ条件:
  - tc-004, tc-005, tc-006 close with runtime tests.
- 必須 tests または docs-only verification:
  - `uv run pytest tests/cli_runtime/test_worktree.py`.
- reviewer focus:
  - code-reviewer: destructive guard, containment, Git-first semantics, JSON failure path.
- 必須出力（output required）:
  - changed files, test output, unresolved risks, Ledger Note if material.
- 停止条件:
  - Any need to delete current/main/unmanaged worktree.
  - Any test would touch non-temp repo/root.
  - Git force semantics cannot be tested hermetically.

#### 具体テストケース一覧

- `tc-s03-001` acceptance: clean managed remove
  - 前提: temp repo has a managed linked worktree, Git allows normal `git worktree remove`, and post-Git directory leftovers can be simulated or observed.
  - 操作: run `spec-dock worktree remove <target>` and `remove <target> --json` in separate fixtures.
  - 期待結果: exit code 0, Git record removed, individual directory removed, branch still exists, JSON includes `resolved_target.id/path/branch/managed`, `removed_record`, `removed_directory`, `branch_deleted=false`.
  - 失敗検出: branch deletion, stale record, leftover directory, missing JSON fields.
  - 検証方法: runtime assertions, `git worktree list --porcelain`, branch existence, filesystem assertion.
  - 関連 closure id: tc-004

- `tc-s03-002` negative: dirty/untracked default remove
  - 前提: target is managed but Git default remove rejects dirty/locked/untracked state.
  - 操作: run `spec-dock worktree remove <target>` and `--json`.
  - 期待結果: command fails, Git refusal is visible, directory remains, JSON error code is `git_worktree_remove_failed` or `remove_blocked` if prediagnosed.
  - 失敗検出: default remove deletes dirty/untracked files without `--force`.
  - 検証方法: runtime assertions.
  - 関連 closure id: tc-005

- `tc-s03-003` acceptance: force remove dirty/untracked managed target
  - 前提: target is managed, not main/current/unmanaged, and Git allows `git worktree remove --force`.
  - 操作: run `spec-dock worktree remove <target> --force --json`.
  - 期待結果: Git record and individual directory are removed, branch remains, JSON success matches schema.
  - 失敗検出: `--force` not passed to Git or branch is deleted.
  - 検証方法: runtime assertions.
  - 関連 closure id: tc-006

- `tc-s03-004` acceptance/negative: locked worktree remove follows Git force semantics
  - 前提: target is a managed linked worktree locked with `git worktree lock <path>` in a temp fixture.
  - 操作: run `spec-dock worktree remove <target> --json` and `spec-dock worktree remove <target> --force --json` in separate fixtures.
  - 期待結果: default remove fails, surfaces Git refusal, and leaves the directory. Force remove succeeds when the installed Git supports forced removal of locked worktrees, removes the Git record and individual directory, and keeps the branch. If the installed Git lacks the needed lock operation, record an explicit skip reason and keep dirty/untracked force coverage as the fallback evidence.
  - 失敗検出: locked worktree is deleted without `--force`, or `--force` bypasses SpecDock managed/current/main/unmanaged guards.
  - 検証方法: runtime assertions using `git worktree lock`, `git worktree list --porcelain`, branch existence, and filesystem assertions.
  - 関連 closure id: tc-005, tc-006

- `tc-s03-005` negative: non-bypassable guards
  - 前提: targets include main checkout, current checkout, unmanaged worktree, ambiguous target.
  - 操作: run `remove <target>` and `remove <target> --force`, with `--json` variants for at least one case.
  - 期待結果: all are refused before Git remove and before filesystem cleanup; JSON/text show blockers/candidates.
  - 失敗検出: `--force` bypasses SpecDock guard or ambiguous target removes something.
  - 検証方法: runtime assertions and, where useful, fake Git gateway call counters.
  - 関連 closure id: tc-005

- `tc-s03-006` negative: containment guard
  - 前提: crafted resolver/fake ports or temp symlink fixture could point target to namespace parent, repo root/main/current path, or symlink-resolved namespace escape.
  - 操作: attempt remove with and without `--force`.
  - 期待結果: command returns `remove_blocked` or `post_remove_cleanup_failed` without deleting unsafe path; Git remove is not called for pre-Git containment failures.
  - 失敗検出: namespace parent, repo root, or escaped path is deleted or passed to Git remove.
  - 検証方法: focused fake-port tests plus filesystem assertions.
  - 関連 closure id: tc-006

- `tc-s03-007` negative: no delete alias
  - 前提: runtime parser is available.
  - 操作: run `spec-dock worktree delete <target>`.
  - 期待結果: parser rejects the command; `remove` remains the only deletion command.
  - 失敗検出: alias is accidentally registered.
  - 検証方法: runtime parser/help assertion.
  - 関連 closure id: tc-006

- `tc-s03-008` negative: remove rejects branch-only target
  - 前提: a branch name exists only as branch metadata and not as id/path/basename.
  - 操作: run `spec-dock worktree remove <branch-name> --json`.
  - 期待結果: command returns non-zero `status=error` and does not call Git remove or filesystem cleanup.
  - 失敗検出: destructive remove accepts branch name or deletes an unintended target.
  - 検証方法: runtime JSON assertion plus Git/filesystem side-effect assertion.
  - 関連 closure id: tc-005

- `tc-s03-009` negative: remove env fail-fast
  - 前提: `SPEC_DOCK_WORKTREE_ROOT` is missing, blank, relative, file, or broken symlink.
  - 操作: run `spec-dock worktree remove <target> --json`.
  - 期待結果: command returns structured root error before Git worktree listing/removal or filesystem cleanup.
  - 失敗検出: invalid root still reaches Git remove, cleanup, or text-only dispatch fallback.
  - 検証方法: runtime/fake-port assertions for JSON payload and no side effects.
  - 関連 closure id: tc-005

#### ステップ完了契約（step closure contract）
- closure id:
  - tc-004
  - tc-005
  - tc-006
- close 条件:
  - destructive remove tests pass in temp fixtures and no unsafe behavior is left untested.
- 検証 evidence:
  - `uv run pytest tests/cli_runtime/test_worktree.py`
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage.
- 残リスク:
  - Git version differences must be recorded as discovered risk if encountered.

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: code-reviewer
  - review 範囲: S03 changed files and tests
  - pass 条件: `review_status: pass`
  - re-review rule: 指摘を修正し pass まで再実行
- commit / no-op gate:
  - closure 状態: committed or approved-no-op

### ドキュメント影響の解消ステップ S90（docs impact resolution / docs refresh）
- 対象:
  - `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`
  - `src/spec_dock/assets/spec_dock/docs/guide.md` if needed
  - `spec-dock/docs/reference_worktree.md`
  - `spec-dock/docs/guide.md` if needed
- 対応:
  - Document `worktree create/list/show/remove`, required `SPEC_DOCK_WORKTREE_ROOT`, JSON-first agent usage, target forms, remove safety, force semantics, no branch deletion, no delete alias, and future `status` / `prune` / `repair`.
- doc update owner:
  - doc-writer
- spec/doc review:
  - reviewer: spec-reviewer

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - doc-writer
- 正本（source of truth）:
  - provider docs under `src/spec_dock/assets/spec_dock/docs/...` are authoritative shipped docs.
  - dogfooding docs under `spec-dock/docs/...` are parity/validation targets and must not contradict provider docs.
  - Runtime help/output after S02/S03 is authoritative for command examples and field names.
- 入力 docs:
  - `requirement.md`, `design.md`, runtime command help/output after S02/S03.
- 許可 paths:
  - S90 対象 docs only.
- 禁止 changes:
  - runtime implementation and tests.
  - claims about status/prune/repair implementation.
- 受け入れ条件:
  - tc-007 closes with docs inspection.
- 必須 tests または docs-only verification:
  - docs grep/inspection and `./spec-dock/scripts/spec-dock validate`.
- reviewer focus:
  - spec-reviewer: docs/spec alignment.
- 必須出力（output required）:
  - changed docs, inspection result, unresolved risks.
- 停止条件:
  - Runtime behavior differs from approved design.

#### 具体テストケース一覧

- `tc-s90-001` inspect-only: provider and dogfooding docs parity
  - 前提: S02/S03 behavior is implemented.
  - 操作: inspect provider and dogfooding worktree docs.
  - 期待結果: docs describe create/list/show/remove current scope and status/prune/repair future scope; no stale wording says list/remove are future-only.
  - 失敗検出: agents read stale docs and avoid using implemented commands.
  - 検証方法: docs inspection, targeted `rg`, `./spec-dock/scripts/spec-dock validate`.
  - 関連 closure id: tc-007

#### ステップ完了契約（step closure contract）
- closure id:
  - tc-007
- close 条件:
  - docs updated and inspected.
- 検証 evidence:
  - docs grep/inspection output and validate output.
- report evidence:
  - Step Contract Closure, Docs Impact Resolution.

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: spec-reviewer
  - review 範囲: docs/spec alignment
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed or approved-no-op

### 実装ステップ S99 — Final Quality Gate
- 振る舞いの目標（behavior goal）:
  - implementation-ready closure evidence を report に集約し、PR/finish に進める状態にする。
- design 参照:
  - all design sections
- 依存:
  - S01, S02, S03, S90
- unblock:
  - final PR workflow / issue finish
- 対象ファイル:
  - `spec-dock/active/issue/report.md`
- 計画済み契約（planned contract）:
  - scope:
    - Run targeted tests, validation, diff checks, QA review, issue-wide code review, final spec review, PR delivery gate, and merge-preparation evidence.
  - テスト義務（test obligation）:
    - closure id:
      - tc-008
    - coverage rationale:
      - Final handoff requires evidence that all AC/EC/constraints and docs are closed.
  - Red / 代替証跡の要件:
    - manual-required:
      - Final gate is evidence aggregation, not new behavior implementation.
  - Green 検証:
    - `uv run pytest tests/cli_runtime/test_worktree.py`
    - `./spec-dock/scripts/spec-dock validate`
    - `./spec-dock/scripts/spec-dock sync`
    - `git diff --check`
    - broader `python -m unittest discover -v` if blast radius warrants or targeted tests expose shared failures.
    - `github-pr-merge-preparer` after final commit / PR creation according to `workflow_issue.md`.
  - Refactor / cleanup ガードレール:
    - no unrelated refactor.
  - amendment trigger:
    - Any failed required check caused by the issue changes.
    - Any reviewer `fail`.

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - qa-reviewer, code-reviewer, and spec-reviewer are reviewer gates; github-pr-merge-preparer handles final PR delivery / merge-preparation evidence.
- 正本（source of truth）:
  - `spec-dock/active/issue/plan.md` owns planned closure conditions.
  - `spec-dock/active/issue/report.md` owns observed evidence, reviewer verdicts, and closure deltas.
  - `spec-dock/docs/workflow_issue.md` owns lifecycle, per-step review/commit, PR Delivery Gate, and Merge Preparation Gate requirements.
- 入力 docs:
  - final requirement/design/plan/report and diff.
- 許可 paths:
  - `spec-dock/active/issue/report.md` for evidence recording.
- 禁止 changes:
  - behavior changes without returning to relevant step.
- 受け入れ条件:
  - tc-008 closure and reviewer pass.
- 必須 tests または docs-only verification:
  - final verification commands listed above.
- reviewer focus:
  - qa-reviewer: obligation coverage and missing high-value tests.
  - code-reviewer: issue-wide integrated diff, runtime safety, tests, docs impact, and regression risk.
  - spec-reviewer: final spec alignment.
- 必須出力（output required）:
  - final verification summary, reviewer verdicts, unresolved risks.
- 停止条件:
  - required test/check failure.
  - reviewer fail.
  - PR delivery or merge-preparation evidence cannot be produced.
  - open Decision Ledger entry.

#### 具体テストケース一覧

- `tc-s99-001` manual-required: final verification and reviewer gates
  - 前提: S01/S02/S03/S90 are closed.
  - 操作: run targeted tests, validate, sync, diff check, QA review, issue-wide code review, final spec review, PR delivery gate, and merge-preparation gate.
  - 期待結果: all required checks pass; report has closure evidence; no unresolved blocking ledger entries; PR/merge-preparation evidence is recorded before lifecycle completion.
  - 失敗検出: implementation is merged forward with incomplete coverage or stale docs/spec.
  - 検証方法: command outputs and reviewer verdicts recorded in `report.md`.
  - 関連 closure id: tc-008

#### ステップ完了契約（step closure contract）
- closure id:
  - tc-008
- close 条件:
  - all final checks and reviewers pass, or documented blocker stops execution.
- 検証 evidence:
  - commands and reviewer outputs.
- report evidence:
  - Final Quality Gate, Reviewer Gate Status, Final QA Gate, Final Code Review Gate, Final Spec Review Gate, PR Delivery Gate, Merge Preparation Gate, Closure Coverage.
- 残リスク:
  - any residual risk must be explicitly non-blocking and recorded.

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer:
    - qa-reviewer
    - code-reviewer
    - spec-reviewer
  - review 範囲:
    - whole issue diff and evidence
  - pass 条件:
    - `review_status: pass`
- commit / no-op gate:
  - closure 状態:
    - committed after all required evidence is recorded.

## Final Exit Contract
- All closure ids `tc-001`..`tc-008` have observed evidence in `report.md`.
- Required commands pass or blockers are resolved:
  - `uv run pytest tests/cli_runtime/test_worktree.py`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
  - `git diff --check`
  - broader unittest if implementation blast radius warrants
- Required reviewer gates pass:
  - step code/spec reviewers
  - final qa-reviewer
  - issue-wide code-reviewer
  - final spec-reviewer
- PR Delivery Gate and Merge Preparation Gate evidence are recorded before issue lifecycle completion.
- No open Decision Ledger entries remain.
- No `worktree delete` alias, branch deletion, prune/repair, active pointer mutation, GitHub mutation, or live checkout destructive operation is introduced.
