---
種別: 実装計画書（Issue）
ID: "iss-00130"
タイトル: "Central Worktree Root Placement"
関連GitHub: ["#130"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-27"
依存: ["requirement.md", "design.md"]
親: ["epic-00107", "init-local-00002"]
---

# iss-00130 Central Worktree Root Placement — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001: env var missing / blank の fatal failure
  - AC-002: central root placement
  - AC-003: env root / namespace directory auto creation
  - AC-004: path validation
  - AC-005: existing naming and collision behavior is preserved
  - AC-006: linked worktree invocation normalization
  - AC-007: bootstrap behavior preservation
  - AC-008: docs and dogfooding parity
  - AC-009: local setup evidence
- EC:
  - EC-001: invalid label
  - EC-002: valid env var but root path creation fails
  - EC-003: namespace directory already exists
  - EC-004: same basename repository collision
  - EC-005: existing sibling worktrees
- 制約:
  - Missing / blank `SPEC_DOCK_WORKTREE_ROOT` で sibling placement fallback しない。
  - Existing sibling worktrees を migrate / remove しない。
  - Namespace override、list/remove/prune、`$CODEX_HOME/worktrees` mixing は scope 外。
  - Parent Epic の sibling placement は future behavior として残さない。

## 依存関係から導く実装順序
- 依存関係の正本:
  - `design.md` の `依存関係分析`、`Module Dependency Diagram`、`ディレクトリ / ファイル変更計画`。
- 順序ルール:
  - Env/config port を先に固定する。
  - Missing / invalid env の fatal behavior を placement change より先に閉じる。
  - Central placement を実装してから、既存 naming / collision / bootstrap / linked-worktree regression を中央 root に合わせて閉じる。
  - Docs / parent Epic update は runtime behavior と tests のあとに実施する。
- step 依存サマリー:
  - S01:
    - 依存: requirement/design pass
    - unblock: S02, S03
    - 対象ファイル: `ports.py`, `bootstrap.py`, `worktree.py`, `test_worktree.py`
  - S02:
    - 依存: S01 env boundary
    - unblock: S03
    - 対象ファイル: `worktree.py`, `test_worktree.py`
  - S03:
    - 依存: S01, S02
    - unblock: S04, S05
    - 対象ファイル: `worktree.py`, `test_worktree.py`
  - S04:
    - 依存: S03
    - unblock: S99
    - 対象ファイル: `worktree.py`, `test_worktree.py`
  - S05:
    - 依存: S03
    - unblock: S99
    - 対象ファイル: `worktree.py`, `test_worktree.py`
  - S06:
    - 依存: none on runtime implementation
    - unblock: S99 local evidence
    - 対象: report evidence only
  - S90:
    - 依存: S03-S05 runtime contract
    - unblock: S99
    - 対象ファイル: shipped docs, dogfooding docs, parent Epic docs
  - S99:
    - 依存: S01-S06, S90
    - 対象: final validation / reviewers / report ledger
  - S100:
    - 依存: S99 final quality reviews and implementation/report ledger readiness
    - 対象: PR Delivery Gate / Merge Preparation Gate / delivery evidence commit / issue finish readiness

## ステップ一覧
- S01:
  - 観測可能な振る舞い: missing / blank `SPEC_DOCK_WORKTREE_ROOT` が副作用なしで fatal になる。
  - レビューゲート: code-reviewer
- S02:
  - 観測可能な振る舞い: invalid root path は副作用なしで fatal、valid `~` absolute / directory symlink は許可される。
  - レビューゲート: code-reviewer
- S03:
  - 観測可能な振る舞い: valid env root で central root namespace に worktree が作られ、旧 sibling container は使われない。
  - レビューゲート: code-reviewer
- S04:
  - 観測可能な振る舞い: id / label / branch / collision / bootstrap behavior が placement 変更後も維持される。
  - レビューゲート: code-reviewer
- S05:
  - 観測可能な振る舞い: linked worktree からの実行でも main worktree basename を namespace に使う。
  - レビューゲート: code-reviewer
- S06:
  - 観測可能な振る舞い: local setup は report evidence として確認され、repo artifact に混ざらない。
  - レビューゲート: read-only evidence; repo diff がなければ reviewer 不要
- S90:
  - 観測可能な振る舞い: shipped docs / dogfooding docs / parent Epic docs が central root contract と整合する。
  - レビューゲート: spec-reviewer docs/spec alignment
- S99:
  - 観測可能な振る舞い: issue-wide diff が requirement / design / plan / report / tests / docs と整合する。
  - レビューゲート: qa-reviewer, issue-wide code-reviewer, final spec-reviewer
- S100:
  - 観測可能な振る舞い: PR delivery と merge-preparation evidence が report / external delivery に揃い、delivery evidence commit と latest-head monitor により `issue finish` 前提が満たされる。
  - レビューゲート: github-pr-merge-preparer / PR monitor evidence

## 要件 ↔ ステップ対応
- AC-001 -> S01
- AC-002 -> S03, S90
- AC-003 -> S03
- AC-004 -> S02
- AC-005 -> S04
- AC-006 -> S05
- AC-007 -> S04
- AC-008 -> S90, S99
- AC-009 -> S06
- EC-001 -> S04
- EC-002 -> S02
- EC-003 -> S03, S04
- EC-004 -> S04, S90
- EC-005 -> S03, S90

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ（step） | スライス（slice） | 種別（type） | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル（evidence level） | クロージャ証跡（closure evidence） |
|---|---|---|---|---|---|---|---|---|---|---|
| slci-001 | S01 | missing-env-fatal | negative | AC-001 / non-negotiable no fallback | missing / blank env is fatal before Git, branch, directory, bootstrap side effects | valid repo + unset/blank `SPEC_DOCK_WORKTREE_ROOT` | silent fallback to sibling placement | yes | red-required | Step/Test Contract Closure |
| slci-002 | S02 | invalid-root-fatal | negative | AC-004 / EC-002 | invalid root is fatal with var name, raw/resolved path, cause, absolute setup example | relative/file/broken symlink/non-directory root | unclear remediation / unsafe path use | yes | red-required | Step/Test Contract Closure |
| slci-003 | S02 | valid-root-forms | acceptance | AC-004 | `~` absolute expansion and directory symlink are accepted | env var with `~` or directory symlink | over-strict root rejection | yes | red-required | Step/Test Contract Closure |
| slci-004 | S03 | central-placement | acceptance | AC-002 / AC-003 | path is `$SPEC_DOCK_WORKTREE_ROOT/<main-basename>/<main-basename>-<id>` and root/namespace may be created | valid env root, missing namespace | wrong placement / root not created | yes | red-required | Step/Test Contract Closure |
| slci-005 | S03 / S90 | no-sibling-future | negative | AC-002 / EC-005 | new creates do not use or migrate old sibling placement | old sibling path absent or existing | legacy fallback / unintended migration | yes | red-required / inspect-only | Step/Test Contract Closure |
| slci-006 | S04 | existing-naming-collision | regression | AC-005 / EC-001 / EC-003 / EC-004 | label/id/branch/collision rules stay unchanged; no namespace override/config is added | labels, branch prefixes, path/branch/record collisions | behavior regression / scope creep | yes | covered-existing / red-required | Step/Test Contract Closure |
| slci-007 | S04 | bootstrap-preservation | regression | AC-007 | `make init` success/skipped/failed/detection_failed remains non-fatal | Makefile success/failure/missing/detection failure | bootstrap fatality regression | yes | covered-existing | Step/Test Contract Closure |
| slci-008 | S05 | linked-worktree-normalization | regression | AC-006 | linked worktree run uses Git main worktree basename for namespace and current checkout branch for branch prefix | command run from linked worktree | nested namespace / wrong branch prefix | yes | red-required | Step/Test Contract Closure |
| slci-009 | S06 | local-setup-evidence | manual | AC-009 | `.zshenv` / user-local root are evidence only, not repo-managed artifacts | shell env and filesystem inspection | hidden workspace-external mutation | yes | manual-required | Report evidence |
| slci-010 | S90 | docs-parent-supersession | docs | AC-008 / parent Epic supersession | shipped docs, dogfooding docs, parent Epic docs no longer present sibling placement as future behavior | docs diff | stale user-facing contract | yes | inspect-only | Docs review evidence |
| slci-011 | S90 / S99 | scope-boundary-docs | docs | out-of-scope / Codex boundary | docs and diff contain no list/remove/prune feature, no Codex app worktree mixing | docs and code diff | scope creep | yes | inspect-only | Docs/final review evidence |
| slci-012 | S90 / S99 | provider-dogfooding-parity | integration | provider-side source of truth | provider asset changes and dogfooding workspace parity are verified | update/sync/parity evidence | scaffold drift | yes | command evidence | Final quality evidence |
| slci-013 | S100 | pr-delivery-merge-prep | delivery | workflow_issue.md PR Delivery Gate / Merge Preparation Gate | PR delivery and merge-preparation evidence are recorded before `issue finish` | final committed branch and PR state | premature issue finish / missing delivery evidence | yes | command / monitor evidence | PR Delivery Gate / Merge Preparation Gate |

## レビュー / QA ゲート方針
- RG1 step review:
  - Runtime / tests / scaffold behavior steps use `code-reviewer`.
  - Docs-only / parent spec docs alignment uses `spec-reviewer`.
- QG1 final QA:
  - `qa-reviewer` checks test sufficiency, missing high-value tests, and integration/manual evidence.
- CG1 issue-wide code review:
  - `code-reviewer` checks integrated runtime/test structure and regression risk.
- SG1 final spec review:
  - `spec-reviewer` checks requirement / design / plan / report / docs / implementation / tests consistency.

## 実行ルール（全ステップ共通）
- 各 implementation step は 1 behavior slice / 1 review scope / 1 commit boundary を標準にする。
- Observed result は `report.md` に記録し、`plan.md` に戻さない。
- Worker は material decision があれば Ledger Note を返し、なければ `No material implementation decisions beyond the approved plan.` と明示する。
- Reviewer fail の修正は bounded delegated follow-up とし、fresh reviewer pass まで回す。
- 実装前にこの plan をユーザーへ提出し、approval を得る。

## 実装ステップ

### 実装ステップ S01 — Missing / Blank Env Fatal
- 振る舞いの目標:
  - `SPEC_DOCK_WORKTREE_ROOT` が unset / empty / whitespace-only の場合、`worktree create` は副作用なしで fatal になる。
- design 参照:
  - `インターフェース契約`, `シーケンス差分`, `要件 → 設計マッピング`
- 依存:
  - requirement/design reviewer pass
- unblock:
  - S02, S03
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
  - `tests/cli_runtime/test_worktree.py`
- 計画済み契約:
  - scope:
    - `EnvironmentGateway.getenv(name)` protocol を追加する。
    - `cli/bootstrap.py` に `os.environ.get` backed adapter を追加する。
    - `worktree_create` は port 経由で env var を読み、missing / blank を fatal にする。
  - テスト義務:
    - closure id: slci-001
    - coverage rationale:
      - Silent fallback to sibling placement が本 issue の中心 bug class なので red-required。
  - Red / 代替証跡の要件:
    - red-required:
      - 実装前に missing env test が現行実装の sibling success または別 failure として失敗することを確認する。
  - 実装範囲:
    - allowed paths: 対象ファイルのみ。
    - forbidden changes: CLI root flag、request root field、direct `os.environ` read in command/use case、docs update、sibling fallback。
  - Green 検証:
    - `python -m unittest tests.cli_runtime.test_worktree.TestCliWorktree.<missing-env-test> -v`
  - Refactor / cleanup ガードレール:
    - Env boundary 以外の runtime architecture refactor をしない。
  - report 証跡の記録先:
    - TDD evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Implementation Delegation Gate。
  - amendment trigger:
    - Required env var を `WorktreeCreateRequest` field や CLI flag に変更する必要が出た場合。

#### 委任契約（delegation contract）
- 委任ロール:
  - dev-coder
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, `workflow_issue.md`
- 許可 paths:
  - S01 対象ファイルのみ。
- 禁止 changes:
  - docs / parent specs / shell profile / namespace override / sibling fallback。
- 受け入れ条件:
  - slci-001 が pass。
- 必須 tests:
  - missing / blank env targeted tests。
- reviewer focus:
  - code-reviewer: env port boundary, no side effects, no scope creep。
- 必須出力:
  - changed files, verification result, unresolved risks, Ledger Note or no-decision statement。
- 停止条件:
  - Env lookup boundary cannot be added without changing command surface。

#### 具体テストケース一覧

- `tc-s01-001` negative: unset env fails before side effects
  - 前提: temp Git repo is on a named branch and `SPEC_DOCK_WORKTREE_ROOT` is absent.
  - 操作: `spec-dock worktree create` を実行する。
  - 期待結果: non-zero exit; stderr names `SPEC_DOCK_WORKTREE_ROOT` and includes absolute-path setup example.
  - 失敗検出: missing env silently creates sibling or central worktree.
  - 検証方法: `tests/cli_runtime/test_worktree.py` targeted CLI runtime test。
  - 関連 closure id: slci-001

- `tc-s01-002` negative: blank env fails before side effects
  - 前提: temp Git repo is valid and `SPEC_DOCK_WORKTREE_ROOT` is empty or whitespace-only.
  - 操作: `spec-dock worktree create` を実行する。
  - 期待結果: non-zero exit; no sibling container, central namespace, branch, or bootstrap artifact is created.
  - 失敗検出: blank value is treated as current directory or fallback placement.
  - 検証方法: CLI runtime test。
  - 関連 closure id: slci-001

#### ステップ完了契約
- closure id:
  - slci-001
- close 条件:
  - Red / Green evidence が report に残り、targeted tests と code-reviewer が pass。
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Step Commit Gate。
- 残リスク:
  - None if no direct env read and no fallback remain.

#### ステップゲート
- step reviewer gate:
  - reviewer: code-reviewer
  - pass 条件: review_status: pass
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S01 target files only

### 実装ステップ S02 — Root Path Validation
- 振る舞いの目標:
  - Invalid root values fail before mutation; valid `~` absolute and directory symlink are accepted.
- design 参照:
  - `Error contract`, `AC-004`, `EC-002`
- 依存:
  - S01
- unblock:
  - S03
- 対象ファイル:
  - `application/worktree.py`
  - `tests/cli_runtime/test_worktree.py`
- 計画済み契約:
  - scope:
    - `_resolve_worktree_root` / `_validate_worktree_root` 相当の helper を追加する。
    - Error message includes env var name, raw value, resolved path, cause, and absolute setup example。
  - テスト義務:
    - closure id: slci-002, slci-003
    - coverage rationale:
      - Root validation は filesystem mutation 前の safety boundary であり negative path が中心。
  - Red / 代替証跡:
    - red-required for invalid root forms and accepted valid forms。
  - 実装範囲:
    - allowed paths: target files。
    - forbidden changes: shell profile edit, namespace override, config file。
  - Green 検証:
    - Targeted path validation tests。
  - Refactor / cleanup ガードレール:
    - Path helper は worktree create 専用に留める。
  - report 証跡の記録先:
    - TDD evidence and closure ledgers。
  - amendment trigger:
    - Path validation requires persistent config or platform-specific branch not in design。

#### 委任契約（delegation contract）
- 委任ロール:
  - dev-coder
- 入力 docs:
  - `requirement.md`, `design.md`, S01 result。
- 許可 paths:
  - `application/worktree.py`, `tests/cli_runtime/test_worktree.py`
- 禁止 changes:
  - env var name change, shell profile edits, docs updates。
- 受け入れ条件:
  - slci-002 and slci-003 pass。
- 必須 tests:
  - relative, file, broken symlink, directory symlink, `~` expansion, namespace mkdir failure。
- reviewer focus:
  - code-reviewer: mutation ordering and error guidance completeness。
- 必須出力:
  - changed files, verification result, risks, Ledger Note/no-decision。
- 停止条件:
  - Test environment cannot create symlink fixture。

#### 具体テストケース一覧

- `tc-s02-001` negative: relative root is fatal
  - 前提: `SPEC_DOCK_WORKTREE_ROOT=relative/worktrees`.
  - 操作: `worktree create` を実行する。
  - 期待結果: non-zero exit; stderr includes env var name, raw/resolved path, cause, setup example; no mutation.
  - 失敗検出: cwd-dependent worktree root is accepted.
  - 検証方法: CLI runtime test。
  - 関連 closure id: slci-002

- `tc-s02-002` negative: file root is fatal
  - 前提: env var points to an existing file.
  - 操作: `worktree create` を実行する。
  - 期待結果: fatal error with path/cause/setup example; no Git or bootstrap mutation.
  - 失敗検出: file path is overwritten or treated as directory.
  - 検証方法: CLI runtime test。
  - 関連 closure id: slci-002

- `tc-s02-003` negative: broken symlink is fatal
  - 前提: env var points to a broken symlink.
  - 操作: `worktree create` を実行する。
  - 期待結果: fatal error before mutation.
  - 失敗検出: broken symlink is auto-repaired or hidden.
  - 検証方法: CLI runtime test。
  - 関連 closure id: slci-002

- `tc-s02-004` acceptance: directory symlink is accepted
  - 前提: env var points to a symlink whose target is a directory.
  - 操作: `worktree create` を実行する。
  - 期待結果: command can use that directory as central root.
  - 失敗検出: valid symlink root is over-rejected.
  - 検証方法: CLI runtime test。
  - 関連 closure id: slci-003

- `tc-s02-005` acceptance: `~` expands to absolute path
  - 前提: env var contains `~/...` and expanded path is absolute and usable.
  - 操作: `worktree create` を実行する。
  - 期待結果: command uses expanded absolute path.
  - 失敗検出: `~` path is rejected or treated literally.
  - 検証方法: CLI runtime or app-level test。
  - 関連 closure id: slci-003

- `tc-s02-006` negative: namespace mkdir failure reports guidance
  - 前提: env root is valid but namespace path cannot be created because of file conflict or permission-like fixture.
  - 操作: `worktree create` を実行する。
  - 期待結果: fatal error includes env var, resolved root, namespace/container path, cause, setup example.
  - 失敗検出: mkdir failure emits vague path error.
  - 検証方法: CLI runtime test。
  - 関連 closure id: slci-002

#### ステップ完了契約
- closure id:
  - slci-002, slci-003
- close 条件:
  - All path validation tests pass and code-reviewer passes。
- report evidence:
  - Step/Test Contract Closure, Closure Coverage, Step Commit Gate。
- 残リスク:
  - Platform-specific symlink behavior; record if a test is skipped with reason.

#### ステップゲート
- step reviewer gate:
  - reviewer: code-reviewer
  - pass 条件: review_status: pass
- commit / no-op gate:
  - closure 状態: committed

### 実装ステップ S03 — Central Root Placement
- 振る舞いの目標:
  - Valid env root creates worktree under central namespace and does not create old sibling container.
- design 参照:
  - `container = env_root / repo_basename`
- 依存:
  - S01, S02
- unblock:
  - S04, S05
- 対象ファイル:
  - `application/worktree.py`
  - `tests/cli_runtime/test_worktree.py`
- 計画済み契約:
  - scope:
    - Replace sibling container derivation with env-root namespace derivation。
    - `WorktreeCreateResult.container_path` means namespace directory。
  - テスト義務:
    - closure id: slci-004, slci-005
  - Red / 代替証跡:
    - red-required central path assertion。
  - 実装範囲:
    - allowed paths: target files。
    - forbidden changes: migration, result expansion unless needed。
  - Green 検証:
    - central-root targeted tests。
  - amendment trigger:
    - Result contract must change beyond `container_path` meaning。

#### 委任契約（delegation contract）
- 委任ロール:
  - dev-coder
- 入力 docs:
  - `requirement.md` AC-002 / AC-003 / EC-005
  - `design.md` central placement and directory / file change plan
  - S01 / S02 implementation results
- 許可 paths:
  - `application/worktree.py`, `tests/cli_runtime/test_worktree.py`
- 禁止 changes:
  - existing sibling worktree migration, namespace override。
- 受け入れ条件:
  - slci-004 and S03 part of slci-005 pass。
- 必須 tests または docs-only verification:
  - `tc-s03-001`, `tc-s03-002`, `tc-s03-003`
  - targeted central-root CLI runtime test command
- reviewer focus:
  - code-reviewer: path derivation, no fallback, no migration。
- 必須出力:
  - changed files
  - central-root targeted verification result
  - confirmation that `WorktreeCreateResult.container_path` still fits namespace directory semantics
  - Ledger Note or no-decision statement
- 停止条件:
  - implementation needs a request/root CLI flag
  - result contract must change beyond the approved design
  - old sibling worktree migration appears necessary

#### 具体テストケース一覧

- `tc-s03-001` acceptance: create under central root
  - 前提: valid env root points to missing temp root; repo basename is `sample-repo`.
  - 操作: labelなしで `worktree create` を実行する。
  - 期待結果: path is `<root>/sample-repo/sample-repo-wt1`; branch is `<current>-wt1`; stdout shows absolute path.
  - 失敗検出: sibling `sample-repo-worktrees` remains target.
  - 検証方法: CLI runtime test。
  - 関連 closure id: slci-004

- `tc-s03-002` negative: old sibling container is not created
  - 前提: valid env root and no existing sibling container.
  - 操作: `worktree create` を実行する。
  - 期待結果: old sibling container does not exist after command.
  - 失敗検出: compatibility fallback creates sibling container.
  - 検証方法: filesystem assertion in central-root test。
  - 関連 closure id: slci-005

- `tc-s03-003` acceptance: existing namespace directory is accepted
  - 前提: `<root>/sample-repo` already exists and is a directory.
  - 操作: `worktree create` を実行する。
  - 期待結果: command creates candidate under existing namespace.
  - 失敗検出: existing namespace is treated as collision by itself.
  - 検証方法: CLI runtime test。
  - 関連 closure id: slci-004

#### ステップ完了契約
- closure id:
  - slci-004, slci-005
- close 条件:
  - central placement tests pass and code-reviewer passes。
- report evidence:
  - Step/Test Contract Closure, Closure Coverage, Step Commit Gate。

#### ステップゲート
- step reviewer gate:
  - reviewer: code-reviewer
- commit / no-op gate:
  - closure 状態: committed

### 実装ステップ S04 — Naming / Collision / Bootstrap Preservation
- 振る舞いの目標:
  - Placement 以外の existing behavior を維持する。
- design 参照:
  - `AC-005`, `AC-007`, `EC-001`, `EC-003`, `EC-004`
- 依存:
  - S03
- unblock:
  - S99
- 対象ファイル:
  - `application/worktree.py` if needed
  - `tests/cli_runtime/test_worktree.py`
- 計画済み契約:
  - scope:
    - Existing tests を central root expected path に更新し、必要な regression seed を追加する。
  - テスト義務:
    - closure id: slci-006, slci-007
  - Red / 代替証跡:
    - covered-existing plus red-required for any missing regression。
  - forbidden changes:
    - label grammar, branch naming, retry ceiling, bootstrap fatality。
  - Green 検証:
    - `python -m unittest tests.cli_runtime.test_worktree.TestCliWorktree -v` or focused equivalent。

#### 委任契約（delegation contract）
- 委任ロール:
  - dev-coder
- 入力 docs:
  - `requirement.md` AC-005 / AC-007 / EC-001 / EC-003 / EC-004
  - `design.md` preservation and regression mapping
  - S03 implementation result
- 許可 paths:
  - `application/worktree.py`, `tests/cli_runtime/test_worktree.py`
- 禁止 changes:
  - Bootstrap behavior changes, namespace config, list/remove/prune。
- 受け入れ条件:
  - slci-006 and slci-007 pass.
- 必須 tests または docs-only verification:
  - `tc-s04-001`..`tc-s04-006`
  - full or focused `tests.cli_runtime.test_worktree.TestCliWorktree` command
- reviewer focus:
  - code-reviewer: regression preservation and scope discipline。
- 必須出力:
  - changed files
  - verification result for naming/collision/bootstrap regression tests
  - unresolved regression risks
  - Ledger Note or no-decision statement
- 停止条件:
  - preserving existing behavior requires changing label grammar, branch naming, retry ceiling, or bootstrap fatality
  - new namespace override / config seems necessary
  - regression tests cannot isolate central root placement from existing behavior

#### 具体テストケース一覧

- `tc-s04-001` regression: label collision retry remains
  - 前提: valid env root and label `feature` used twice.
  - 操作: `worktree create feature` を2回実行する。
  - 期待結果: ids are `feature` and `feature2`; branches keep current prefix.
  - 失敗検出: placement change breaks retry naming.
  - 検証方法: updated existing CLI test。
  - 関連 closure id: slci-006

- `tc-s04-002` regression: auto id retry remains
  - 前提: valid env root and label omitted.
  - 操作: `worktree create` を2回実行する。
  - 期待結果: ids are `wt1` and `wt2`.
  - 失敗検出: central namespace collision changes id sequence.
  - 検証方法: updated existing CLI test。
  - 関連 closure id: slci-006

- `tc-s04-003` negative: invalid labels remain side-effect-free
  - 前提: invalid labels are provided.
  - 操作: `worktree create <invalid>` を実行する。
  - 期待結果: invalid label error; no env root namespace or sibling path side effects.
  - 失敗検出: invalid label reaches placement creation.
  - 検証方法: updated existing CLI test。
  - 関連 closure id: slci-006

- `tc-s04-004` regression: branch prefix with slash remains
  - 前提: current branch is `feature/base`.
  - 操作: `worktree create slice` を実行する。
  - 期待結果: branch is `feature/base-slice`.
  - 失敗検出: branch name sanitization drift.
  - 検証方法: updated existing CLI test。
  - 関連 closure id: slci-006

- `tc-s04-005` regression: bootstrap statuses remain non-fatal
  - 前提: Makefile success, failure, detection failure, missing target cases exist.
  - 操作: `worktree create` を実行する。
  - 期待結果: `succeeded` / `failed` / `detection_failed` / `skipped` are observable; failure remains exit 0 after worktree creation.
  - 失敗検出: bootstrap failure becomes fatal or warnings disappear.
  - 検証方法: updated existing bootstrap tests。
  - 関連 closure id: slci-007

- `tc-s04-006` regression: non-retryable git add failure reports central path artifact state
  - 前提: fake Git gateway raises non-retryable add failure.
  - 操作: app-level `worktree_create` を実行する。
  - 期待結果: error is non-retryable and artifact state refers to central candidate path.
  - 失敗検出: git failure is swallowed as retryable or reports stale sibling path.
  - 検証方法: updated fake gateway test。
  - 関連 closure id: slci-006

#### ステップ完了契約
- closure id:
  - slci-006, slci-007
- close 条件:
  - Existing behavior regression suite passes and code-reviewer passes。
- report evidence:
  - Step/Test Contract Closure, Closure Coverage, Step Commit Gate。

#### ステップゲート
- step reviewer gate:
  - reviewer: code-reviewer
- commit / no-op gate:
  - closure 状態: committed

### 実装ステップ S05 — Linked Worktree Normalization
- 振る舞いの目標:
  - Linked worktree から実行しても namespace / repo basename は Git main worktree basename を使う。
- design 参照:
  - `AC-006`
- 依存:
  - S03
- unblock:
  - S99
- 対象ファイル:
  - `application/worktree.py` if needed
  - `tests/cli_runtime/test_worktree.py`
- 計画済み契約:
  - scope:
    - `records[0].path` as main worktree source を維持する。
    - Old sibling container を discovery / migration しない。
  - テスト義務:
    - closure id: slci-008
  - Red / 代替証跡:
    - red-required linked-worktree test。
  - Green 検証:
    - linked-worktree targeted test。

#### 委任契約（delegation contract）
- 委任ロール:
  - dev-coder
- 入力 docs:
  - `requirement.md` AC-006
  - `design.md` linked worktree normalization decision
  - S03 implementation result
- 許可 paths:
  - `application/worktree.py`, `tests/cli_runtime/test_worktree.py`
- 禁止 changes:
  - linked worktree basename based namespace, migration behavior。
- 受け入れ条件:
  - slci-008 passes.
- 必須 tests または docs-only verification:
  - `tc-s05-001`
  - linked-worktree targeted CLI runtime test
- reviewer focus:
  - code-reviewer: main worktree normalization and current branch prefix。
- 必須出力:
  - changed files
  - linked-worktree verification result
  - confirmation that old sibling container is not inspected or migrated
  - Ledger Note or no-decision statement
- 停止条件:
  - Git worktree list ordering cannot reliably identify main worktree in current implementation
  - linked worktree test requires migration/discovery behavior outside approved design

#### 具体テストケース一覧

- `tc-s05-001` regression: linked worktree creates inner under main namespace
  - 前提: outer linked worktree exists under central root; command runs from outer.
  - 操作: outer の `spec-dock/scripts/spec-dock worktree create inner` を実行する。
  - 期待結果: inner path is `<root>/sample-repo/sample-repo-inner`; branch is `<current-linked-branch>-inner`.
  - 失敗検出: namespace becomes linked worktree basename or nested path.
  - 検証方法: updated linked-worktree CLI runtime test。
  - 関連 closure id: slci-008

#### ステップ完了契約
- closure id:
  - slci-008
- close 条件:
  - linked-worktree test passes and code-reviewer passes。
- report evidence:
  - Step/Test Contract Closure, Closure Coverage, Step Commit Gate。

#### ステップゲート
- step reviewer gate:
  - reviewer: code-reviewer
- commit / no-op gate:
  - closure 状態: committed

### 実装ステップ S06 — Local Setup Evidence Only
- 振る舞いの目標:
  - Local setup is verified as evidence only and not committed as product artifact.
- design 参照:
  - `AC-009`
- 依存:
  - none
- unblock:
  - S99
- 対象:
  - report evidence only
- 計画済み契約:
  - scope:
    - Verify shell env and root existence / creatability.
  - テスト義務:
    - closure id: slci-009
  - Red / 代替証跡:
    - manual-required。
  - forbidden changes:
    - Workspace-external shell profile edits unless new explicit approval and plan amendment exist.
  - Green 検証:
    - `printenv SPEC_DOCK_WORKTREE_ROOT`
    - read-only `.zshenv` inspection for override-respecting export
    - `test -d "$SPEC_DOCK_WORKTREE_ROOT"` or command-created root evidence。
  - report 証跡の記録先:
    - Session log, Step Contract Closure, Test Contract Closure, Closure Coverage。

#### 委任契約（delegation contract）
- 委任ロール:
  - N/A; parent orchestrator read-only verification
- 入力 docs:
  - `requirement.md` AC-009
  - `design.md` local setup evidence boundary
  - `plan.md` S06
- 許可 paths:
  - none
- 禁止 changes:
  - `/Users/iwasawayuuta/.zshenv` edits, local directory deletion, repo artifact mutation。
- 受け入れ条件:
  - `SPEC_DOCK_WORKTREE_ROOT` is visible in current shell or documented as unavailable.
  - `/Users/iwasawayuuta/.zshenv` contains an override-respecting export or report records blocker/next action.
  - Root directory exists or is proven creatable by runtime behavior.
- 必須 tests または docs-only verification:
  - `printenv SPEC_DOCK_WORKTREE_ROOT`
  - read-only inspection of `/Users/iwasawayuuta/.zshenv`
  - `test -d "$SPEC_DOCK_WORKTREE_ROOT"` or runtime-created root evidence
- reviewer focus:
  - N/A unless repo diff exists。
- 必須出力:
  - command outputs summarized in `report.md`
  - no repo diff for shell profile
  - unresolved local setup risks, if any
- 停止条件:
  - shell env is unavailable and no approved equivalent evidence exists
  - `.zshenv` inspection is denied or shows missing export
  - root path is unusable and runtime behavior cannot create it

#### 具体テストケース一覧

- `tc-s06-001` manual-required: shell env is visible
  - 前提: current shell session is available.
  - 操作: `printenv SPEC_DOCK_WORKTREE_ROOT`
  - 期待結果: value is `/Users/iwasawayuuta/workspace/worktrees` or user-approved equivalent.
  - 失敗検出: local smoke cannot use required env.
  - 検証方法: command evidence in report。
  - 関連 closure id: slci-009

- `tc-s06-002` manual-required: root exists or is creatable
  - 前提: env var value is valid.
  - 操作: `test -d "$SPEC_DOCK_WORKTREE_ROOT"` or observe command-created root during runtime smoke.
  - 期待結果: root exists or is created by valid `worktree create` behavior.
  - 失敗検出: env points to unusable local root.
  - 検証方法: command evidence in report。
  - 関連 closure id: slci-009

- `tc-s06-003` manual-required: `.zshenv` contains override-respecting export
  - 前提: local shell startup file is readable.
  - 操作: inspect `/Users/iwasawayuuta/.zshenv` for `SPEC_DOCK_WORKTREE_ROOT`.
  - 期待結果: file contains an override-respecting export such as `export SPEC_DOCK_WORKTREE_ROOT="${SPEC_DOCK_WORKTREE_ROOT:-$HOME/workspace/worktrees}"`.
  - 失敗検出: env is only transient in current shell and not represented in shell startup config.
  - 検証方法: read-only command evidence in report; no file edit.
  - 関連 closure id: slci-009

#### ステップ完了契約
- closure id:
  - slci-009
- close 条件:
  - Report records local evidence and no repo diff is introduced for shell profile.
- report evidence:
  - Step/Test Contract Closure, Closure Coverage。

#### ステップゲート
- step reviewer gate:
  - reviewer: N/A unless repo diff exists
- commit / no-op gate:
  - closure 状態: approved-no-op if no repo diff

### ドキュメント影響の解消ステップ S90（docs impact resolution / docs refresh）
- 対象:
  - `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`
  - `spec-dock/docs/reference_worktree.md`
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/plan.md`
- 対応:
  - Provider docs を central root contract に更新する。
  - Dogfooding docs を normal update / parity path で同期または差分理由付きで確認する。
  - Parent Epic docs から sibling placement を future behavior として残さない。
  - Existing sibling worktrees は legacy / historical context として扱う。
- doc update owner:
  - doc-writer for shipped docs。
  - parent orchestrator for canonical parent spec docs。
- 委任契約:
  - delegated role: doc-writer for shipped docs。
  - input docs: `requirement.md`, `design.md`, `plan.md`, `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`, parent Epic docs。
  - allowed paths: listed docs only。
  - forbidden changes: runtime/tests, new commands, `$CODEX_HOME/worktrees` mixing。
  - acceptance criteria: slci-010, slci-011, slci-012 docs-related expectations。
  - required tests or docs-only verification: docs diff inspection, provider/dogfooding parity evidence, spec-reviewer docs/spec alignment。
  - stop conditions: docs require runtime behavior outside approved design, parent Epic cannot be reconciled without requirement change, parity update fails without documented blocker。
  - output required: changed docs, verification result, rejected/unchanged docs rationale, Ledger Note or no-decision statement。
- 具体テストケース一覧:
  - `tc-s90-001` inspect-only: docs mention required env root
    - 前提: docs updated.
    - 操作: inspect docs.
    - 期待結果: docs mention `SPEC_DOCK_WORKTREE_ROOT`, fatal missing env, layout `$SPEC_DOCK_WORKTREE_ROOT/spec-dock/spec-dock-wt1`.
    - 失敗検出: stale sibling placement remains current behavior.
    - 検証方法: docs diff inspection。
    - 関連 closure id: slci-010
  - `tc-s90-002` inspect-only: legacy sibling boundary is explicit
    - 前提: docs updated.
    - 操作: inspect docs.
    - 期待結果: existing sibling worktrees are not migrated; future creates use central root.
    - 失敗検出: docs imply migration or fallback.
    - 検証方法: docs diff inspection。
    - 関連 closure id: slci-005, slci-010
  - `tc-s90-003` inspect-only: parent Epic no longer conflicts
    - 前提: parent Epic docs updated.
    - 操作: inspect parent Epic requirement/design/plan.
    - 期待結果: sibling placement is not future contract; central root supersession is clear.
    - 失敗検出: upstream and issue specs remain contradictory.
    - 検証方法: spec diff inspection。
    - 関連 closure id: slci-010
  - `tc-s90-004` command/inspect: provider-dogfooding parity
    - 前提: provider docs updated.
    - 操作: run update/sync/parity test or record explicit parity rationale.
    - 期待結果: provider and dogfooding docs align.
    - 失敗検出: shipped asset and dogfooding workspace drift.
    - 検証方法: parity test / update evidence / diff inspection。
    - 関連 closure id: slci-012
- spec/doc review:
  - reviewer: spec-reviewer
  - pass 条件: docs align with requirement / design / plan and no docs scope creep.
- report 証跡の記録先:
  - `report.md` Session log for docs changes and verification commands。
  - Step Contract Closure for slci-010, slci-011, slci-012。
  - Test Contract Closure for `tc-s90-001`..`tc-s90-004`。
  - Closure Coverage and Closure Delta。
  - Reviewer Gate Status for S90 docs/spec alignment review。
- amendment trigger:
  - Parent Epic docs cannot be reconciled without changing approved requirement/design meaning beyond iss-00130 supersession。
  - Provider/dogfooding parity cannot be achieved or intentionally left divergent without new rationale。
  - Docs update requires adding worktree list/remove/prune, namespace override, or Codex app worktree management scope。
  - Runtime behavior discovered during docs update contradicts requirement/design。
- ステップ完了契約:
  - closure id:
    - slci-010
    - slci-011
    - slci-012
  - close 条件:
    - Shipped docs, dogfooding docs, and parent Epic docs have no unresolved sibling-placement conflict.
    - Docs/spec alignment reviewer returns pass.
    - Report records docs diff, parity/update evidence or accepted no-op rationale, and closure coverage.
  - 検証 evidence:
    - docs diff inspection
    - parity/update command evidence or explicit no-op rationale
    - spec-reviewer pass
  - 残リスク:
    - Generated dogfooding docs may require normal scaffold refresh; if refresh is blocked, report must classify the issue as blocked / 未完了 rather than complete.
- step gate:
  - closure 状態: committed or approved-no-op with evidence.

### 最終品質ゲートステップ S99（final quality gate）
- branch diff 範囲:
  - Runtime, tests, shipped docs, dogfooding docs, parent Epic docs, active issue report。
- 必須 validation:
  - `python -m unittest tests.cli_runtime.test_worktree.TestCliWorktree -v`
  - `python -m unittest discover -v` if feasible
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
- final QA gate:
  - reviewer: qa-reviewer
  - 範囲: Issue 全体の obligation coverage と integration/manual evidence。
  - pass 条件: reviewer pass
- final code review ゲート:
  - reviewer: code-reviewer
  - 範囲: issue-wide integrated diff、構造、責務境界、回帰リスク、保守性。
  - pass 条件: review_status: pass
- final spec review ゲート:
  - reviewer: spec-reviewer
  - 範囲: requirement / design / plan / report / implementation / tests / docs 整合。
  - pass 条件: reviewer pass
- 具体テストケース一覧:
  - `tc-s99-001` command: targeted worktree suite
    - 前提: all implementation/docs steps complete.
    - 操作: `python -m unittest tests.cli_runtime.test_worktree.TestCliWorktree -v`
    - 期待結果: pass.
    - 失敗検出: worktree behavior regression remains.
    - 検証方法: command evidence。
    - 関連 closure id: slci-001..slci-008
  - `tc-s99-002` command: broader test baseline
    - 前提: targeted suite passes.
    - 操作: `python -m unittest discover -v`
    - 期待結果: pass or documented blocker if infeasible.
    - 失敗検出: cross-runtime regression.
    - 検証方法: command evidence。
    - 関連 closure id: slci-012
  - `tc-s99-003` command: spec-dock validation and sync
    - 前提: docs/spec changes complete.
    - 操作: `./spec-dock/scripts/spec-dock validate` and `./spec-dock/scripts/spec-dock sync`
    - 期待結果: pass.
    - 失敗検出: spec tree or generated state drift.
    - 検証方法: command evidence。
    - 関連 closure id: slci-012
  - `tc-s99-004` inspect: final clean state after final commit
    - 前提: final report ledger and commit complete.
    - 操作: `git status --short`
    - 期待結果: no unintended staged / unstaged changes.
    - 失敗検出: untracked or unstaged implementation residue.
    - 検証方法: command evidence。
    - 関連 closure id: slci-012
- final commit gate:
  - commit 範囲:
    - final report ledger and remaining issue-wide changes after all required reviews pass.
  - final report ledger:
    - all required closure ids pass / approved-no-op.
  - post-commit external evidence destination:
    - final response / PR description / issue comment.

### 送達準備ステップ S100（PR delivery / merge preparation gate）
- 振る舞いの目標:
  - `issue finish` 前に PR delivery と merge-preparation evidence を揃え、report evidence が dirty state や stale head SHA を残さないようにする。
- workflow 参照:
  - `workflow_issue.md` の PR Delivery Gate / Merge Preparation Gate。
- 依存:
  - S99 final quality reviews pass。
  - Implementation / docs step commits are complete。
  - Final report ledger is ready for delivery evidence.
- 対象:
  - report evidence, PR state, external delivery evidence。
- 計画済み契約:
  - scope:
    - `github-pr-merge-preparer` を使い、PR 作成または既存 PR 再利用、base branch、head SHA、issue linkage、draft/ready 判断を記録する。
    - PR open state、latest monitored head SHA、checks、blocking reviews、merge conflicts、unresolved blockers、final merge-prepared decision を記録する。
    - S100 で `report.md` に PR / merge-preparation evidence を追記した場合、その report update は delivery evidence commit として commit / push する。
    - Delivery evidence commit が head SHA を変えた場合、merge-preparation monitor は更新後の latest pushed head SHA に対して再実行する。
    - 最終的に report / external delivery evidence は latest monitored head SHA と current pushed head SHA の一致を示し、local worktree に意図しない staged / unstaged change を残さない。
  - テスト義務:
    - closure id: slci-013
  - Red / 代替証跡:
    - command / monitor evidence。PR が作成不能または monitor 不能な場合は `blocked` / `未完了` として report に reason と next action を残す。
  - 実装範囲:
    - allowed paths: `report.md` delivery gate sections and external delivery evidence。
    - forbidden changes: unreviewed code/docs changes, merge execution, issue finish without delivery evidence。
  - Green 検証:
    - PR Delivery Gate evidence present。
    - Merge Preparation Gate evidence present。
    - Any S100 report update is committed and pushed before final monitor decision。
    - Latest monitored head SHA equals latest pushed head SHA。
  - report 証跡の記録先:
    - `report.md` PR Delivery Gate / Merge Preparation Gate sections。
  - amendment trigger:
    - Required PR/merge evidence cannot be produced and workflow policy needs waiver or scope change。

#### 委任契約（delegation contract）
- 委任ロール:
  - github-pr-merge-preparer
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, `report.md`, final commit evidence。
- 許可 paths:
  - `report.md` PR Delivery Gate / Merge Preparation Gate sections。
  - external delivery evidence such as PR description/comment/final response。
  - PR creation/push after S99 quality gates。
- 禁止 changes:
  - merge the PR, bypass failed checks, close issue without gates, implement new product changes。
- 受け入れ条件:
  - slci-013 pass。
- 必須 verification:
  - PR URL / base / head branch / head SHA / issue linkage / PR open state / check status / blocker status / final merge-prepared decision。
  - If S100 commits report evidence, re-push and re-monitor latest head SHA。
- reviewer focus:
  - PR delivery and merge-preparation evidence completeness。
- 必須出力:
  - PR URL, branch, head SHA, monitor result, unresolved blockers, final merge-prepared decision。
- 停止条件:
  - push/PR creation denied, checks unavailable, merge conflict, unresolved blocking review, stale head SHA。

#### 具体テストケース一覧

- `tc-s100-001` delivery: PR Delivery Gate evidence exists
  - 前提: final commit is complete and branch is ready to publish.
  - 操作: run `github-pr-merge-preparer` / PR creation workflow.
  - 期待結果: report records PR URL, selected base, base-resolution source, draft/ready decision, head branch, head SHA, issue linkage, reuse/new decision.
  - 失敗検出: issue finish proceeds without PR delivery context.
  - 検証方法: PR Delivery Gate evidence in report / external delivery.
  - 関連 closure id: slci-013

- `tc-s100-002` monitor: Merge Preparation Gate evidence exists
  - 前提: PR exists and latest head SHA is known.
  - 操作: monitor PR checks/reviews/mergeability.
  - 期待結果: report records open state, latest monitored head SHA, required/non-required checks, blocking review status, merge conflict status, unresolved blockers, final merge-prepared decision.
  - 失敗検出: stale or incomplete monitor result is treated as merge-prepared.
  - 検証方法: Merge Preparation Gate evidence in report / external delivery.
  - 関連 closure id: slci-013

- `tc-s100-003` delivery: report evidence commit does not stale the monitor result
  - 前提: S100 writes PR / merge-preparation evidence to `report.md`.
  - 操作: commit and push the S100 report update, then re-monitor the PR head.
  - 期待結果: latest monitored head SHA equals latest pushed head SHA; `git status --short` has no unintended changes.
  - 失敗検出: PR is marked merge-prepared for a stale pre-report head.
  - 検証方法: push/monitor evidence and clean-state command.
  - 関連 closure id: slci-013

#### ステップ完了契約
- closure id:
  - slci-013
- close 条件:
  - PR Delivery Gate and Merge Preparation Gate are recorded as pass for the latest pushed head, or report records blocked / 未完了 with reason and next action.
- report evidence:
  - PR Delivery Gate, Merge Preparation Gate, delivery evidence commit, latest-head monitor evidence。
- 残リスク:
  - GitHub checks may change after monitor; report must record monitored head SHA.

#### ステップゲート
- delivery gate:
  - role: github-pr-merge-preparer
  - pass 条件: PR delivery and merge-preparation evidence complete.
- issue finish gate:
  - `issue finish` may run only after S100 pass and workflow completion conditions are met.

## ロールバック / 互換
- Rollback:
  - Runtime path derivation、docs、tests を previous sibling placement に revert する。
  - Existing sibling worktrees は移動していないため migration rollback は不要。
- Compatibility:
  - Future `worktree create` requires env root。
  - Existing sibling worktrees remain valid Git worktrees but are not migrated or managed by this issue。

## 未確定事項
- なし。

## 最終完了条件
- AC/EC 達成:
  - slci-001..slci-013 が Step Contract Closure / Test Contract Closure / Closure Coverage で pass または approved-no-op として閉じている。
- docs 影響解決:
  - S90 が spec-reviewer pass。
- 全 implementation step 完了:
  - S01-S05, S90 are committed。
  - S06 is committed if repo diff exists, otherwise approved-no-op with evidence。
- final quality gate pass:
  - qa-reviewer: pass
  - issue-wide code-reviewer: pass
  - final spec-reviewer: pass
- final commit 完了:
  - final implementation/report ledger commit is complete before S100.
  - if S100 adds PR / merge-preparation report evidence, that update is committed and pushed as delivery evidence.
- PR / merge-preparation:
  - S100 PR Delivery Gate and Merge Preparation Gate pass for the latest pushed head before `issue finish`.
- final clean state:
  - no unintended staged / unstaged changes after final implementation commit and after any S100 delivery evidence commit.
- handoff:
  - 実装開始前に、requirement / design / plan をユーザーに提出し、approval を得る。
