---
種別: 実装計画書（Issue）
ID: "iss-00153"
タイトル: "Default Full Delete For Worktree Remove"
関連GitHub: ["#153"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-02"
依存: ["requirement.md", "design.md"]
親: ["epic-00107", "init-local-00002"]
---

# iss-00153 Default Full Delete For Worktree Remove — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001: untracked residue を含む eligible linked worktree を default remove で削除する。
  - AC-002: tracked modification を含む eligible linked worktree を default remove で削除する。
  - AC-003: `--force` を互換入力として受け付け、default と同じ削除契約を満たす。
  - AC-004: main / current / bare / missing / record missing / containment guard を bypass しない。
  - AC-005: provider docs、dogfooding docs、CLI help、tests が新しい contract を示す。
- EC:
  - EC-001: Git が force-equivalent remove を拒否した場合は Git error を返し、filesystem cleanup を行わない。
  - EC-002: post-remove cleanup failure は `removed_record=true` / `removed_directory=false` として区別する。
  - EC-003: unmanaged linked worktree は diagnostic のまま削除可能にする。
- 制約:
  - branch deletion を行わない。
  - filesystem cleanup は Git-first / target-only のままにする。
  - runtime tests は temp Git repo / temp worktree root を使う。
  - Provider-side source of truth は `src/spec_dock/assets/spec_dock/...` とする。

## 依存関係から導く実装順序
- 依存関係の正本:
  - `design.md` の `依存関係分析`、`モジュール依存図`、`ディレクトリ / ファイル変更計画`。
- 順序ルール:
  - Public CLI behavior の Red を先に置く。
  - Application layer の default full delete を最小変更で通す。
  - Compatibility と destructive guardrail を広げて検証する。
  - Runtime behavior が固まった後に docs/help を更新する。
- step 依存サマリー:
  - S01:
    - 依存: approved `requirement.md` / `design.md`
    - unblock: S02, S03
    - 対象ファイル: `application/worktree.py`, `tests/cli_runtime/test_worktree.py`
  - S02:
    - 依存: S01
    - unblock: S03, S90
    - 対象ファイル: `tests/cli_runtime/test_worktree.py`, 必要時のみ `application/worktree.py`
  - S03:
    - 依存: S01, S02
    - unblock: S90, S99
    - 対象ファイル: `tests/cli_runtime/test_worktree.py`, 必要時のみ `application/worktree.py`
  - S90:
    - 依存: S01, S02, S03
    - unblock: S99
    - 対象ファイル: `commands/worktree.py`, provider/dogfooding `reference_worktree.md`, 必要時 `tests/cli_runtime/test_worktree.py`
  - S99:
    - 依存: S01, S02, S03, S90
    - unblock: final handoff / PR workflow
    - 対象ファイル: 原則 product edit なし。`report.md` は orchestrator-owned evidence update。

## ステップ一覧
- S01:
  - 観測可能な振る舞い: untracked residue を含む linked worktree が option なしで削除される。
  - 依存: approved requirement/design
  - unblock: S02, S03
  - 対象ファイル: `application/worktree.py`, `tests/cli_runtime/test_worktree.py`
  - 閉じる要件: AC-001, success output/branch retention の一部
  - レビューゲート: step `code-reviewer`
- S02:
  - 観測可能な振る舞い: tracked modification と `--force` 互換入力が default と同じ削除契約を満たす。
  - 依存: S01
  - unblock: S03, S90
  - 対象ファイル: `tests/cli_runtime/test_worktree.py`, 必要時 `application/worktree.py`
  - 閉じる要件: AC-002, AC-003
  - レビューゲート: step `code-reviewer`
- S03:
  - 観測可能な振る舞い: hard blockers、Git refusal、post-remove cleanup failure、unmanaged diagnostics が維持される。
  - 依存: S01, S02
  - unblock: S90, S99
  - 対象ファイル: `tests/cli_runtime/test_worktree.py`, 必要時 `application/worktree.py`
  - 閉じる要件: AC-004, EC-001, EC-002, EC-003
  - レビューゲート: step `code-reviewer`
- S90:
  - 観測可能な振る舞い: CLI help と provider/dogfooding docs が default full delete / `--force` compatibility を説明する。
  - 依存: S01, S02, S03
  - unblock: S99
  - 対象ファイル: `commands/worktree.py`, `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`, `spec-dock/docs/reference_worktree.md`, 必要時 `tests/cli_runtime/test_worktree.py`
  - 閉じる要件: AC-005
  - レビューゲート: docs/spec `spec-reviewer`; `commands/worktree.py` または `tests/cli_runtime/test_worktree.py` を変更した場合は `code-reviewer` 必須
- S99:
  - 観測可能な振る舞い: issue-wide closure、final QA/code/spec reviews、validate/sync、report evidence が揃う。
  - 依存: S01, S02, S03, S90
  - unblock: PR handoff / issue completion
  - 対象ファイル: 原則 product edit なし
  - 閉じる要件: ci-001..ci-009 全体
  - レビューゲート: `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`

## 要件 ↔ ステップ対応
- AC-001 -> S01
- AC-002 -> S02
- AC-003 -> S02
- AC-004 -> S03
- AC-005 -> S90
- EC-001 -> S03
- EC-002 -> S03
- EC-003 -> S03
- Final closure / report / review gates -> S99

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ（step） | スライス（slice） | 種別（type） | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル（evidence level） | クロージャ証跡（closure evidence） |
|---|---|---|---|---|---|---|---|---|---|---|
| ci-001 | S01 | default full delete for untracked residue | acceptance | AC-001 | exit 0; Git record removed; target path removed; `branch_deleted=false`; branch remains | linked worktree with untracked `cache.tmp`; `worktree remove untracked --json` | default remove still fails on untracked residue | yes | red-required | Step/Test closure in `report.md` |
| ci-002 | S02 | default full delete for tracked modification | acceptance | AC-002 | exit 0; Git record removed; target path removed; `branch_deleted=false`; branch remains | linked worktree with modified tracked file; `worktree remove modified --json` | tracked dirty state not covered | yes | red-required | Step/Test closure in `report.md` |
| ci-003 | S02 | `--force` compatibility input | compatibility | AC-003 | `--force` is accepted and same success/failure contract as default | dirty linked worktree; `worktree remove <target> --force --json` | existing scripts break or force path diverges | yes | red-required | Step/Test closure in `report.md` |
| ci-004 | S03 | hard blockers remain non-bypassable | negative | AC-004 | hard blocker fails before Git remove; `--force` does not bypass | main/current/bare/missing/record-missing/containment target | destructive guard bypass | yes | covered-existing plus targeted update | Step/Test closure in `report.md` |
| ci-005 | S90 | docs/help contract | docs | AC-005 | docs/help state default full delete and `--force` compatibility, not `--force` required | CLI help and reference docs | operator misreads destructive default | yes | inspect-only plus help assertion | Step/Test closure in `report.md` |
| ci-006 | S03 | Git refusal does not cleanup | negative | EC-001 | `git_worktree_remove_failed`; filesystem cleanup not called | GitGateway refuses force-equivalent remove / locked worktree unsupported by Git | cleanup after failed Git remove | yes | covered-existing plus assertion update | Step/Test closure in `report.md` |
| ci-007 | S03 | post-remove cleanup failure remains distinguishable | negative | EC-002 | `post_remove_cleanup_failed`; `removed_record=true`; `removed_directory=false`; cleanup target-only | Git remove success then target cleanup failure | cleanup failure hidden or broadened | yes | covered-existing plus assertion update | Step/Test closure in `report.md` |
| ci-008 | S03 | unmanaged diagnostic-only removal | acceptance | EC-003 | unmanaged target is removable by default; diagnostic fields remain; branch remains | external linked worktree with no hard blocker | unmanaged misclassified as blocker | yes | characterization-update | Step/Test closure in `report.md` |
| ci-009 | S01/S02/S03 | output schema and branch retention | invariant | AC-001, AC-002, AC-003 | success JSON/text schema unchanged; `branch_deleted=false` | default and `--force` successful removals | schema drift while changing behavior | yes | covered-existing plus focused assertions | Step/Test closure in `report.md` |

## レビュー / QA ゲート方針
- RG1 step review:
  - 実施タイミング: S01, S02, S03, S90 の step closure 前。
  - reviewer: runtime / tests は `code-reviewer`; docs-only alignment は `spec-reviewer`。
  - pass 条件: `review_status: pass`。
- QG1 final QA:
  - reviewer: `qa-reviewer`
  - 範囲: closure index coverage、missing high-value tests、manual/integration test 要否。
- CR1 final code review:
  - reviewer: issue-wide `code-reviewer`
  - 範囲: integrated diff、layering、destructive safety、maintainability。
- SG1 final spec review:
  - reviewer: final `spec-reviewer`
  - 範囲: requirement / design / plan / report / docs / implementation / tests の整合。

## 実行ルール（全ステップ共通）
- `plan.md` は planned contract、`report.md` は observed evidence ledger とする。
- 各 step は原則 1 behavior slice / 1 review scope / 1 commit boundary とする。
- Implementation worker は `report.md` へ転記できる changed files、verification result、unresolved risk、Ledger Note を返す。
- Material な仕様解釈、未計画の bug class、closure index 変更、required row の意味変更は plan amendment と re-review を必要とする。

## 実装ステップ

### 実装ステップ S01 — Untracked Residue Default Full Delete
- 振る舞いの目標（behavior goal）:
  - `worktree remove <target>` が untracked residue を含む eligible linked worktree を option なしで削除する。
- design 参照:
  - `design.md` の `採用方針 / トレードオフ`、`インターフェース契約`、`要件 → 設計マッピング`。
- 依存:
  - approved requirement/design。
- unblock:
  - S02, S03。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
  - `tests/cli_runtime/test_worktree.py`
- 計画済み契約（planned contract）:
  - scope:
    - 既存 dirty/untracked test を default success contract に更新する。
    - `application.worktree` の GitGateway remove call を eligible target では force-equivalent default にする。
  - テスト義務（test obligation）:
    - closure id: `ci-001`, `ci-009`
    - coverage rationale: public CLI behavior、branch retention、output schema、Git record/path deletion を同時に固定する。
  - Red / 代替証跡の要件:
    - red-required: 更新した dirty/untracked default success test は現行実装で `git_worktree_remove_failed` になる。
  - Green 検証:
    - focused updated dirty/untracked test。
  - Refactor / cleanup ガードレール:
    - request / port / output schema rename をしない。
    - `git_cli.py` は既存 `force=True` mapping が不足すると証明された場合だけ触る。
  - report 証跡の記録先:
    - TDD / Red / Green / Refactor Evidence、Step Contract Closure、Test Contract Closure、Closure Coverage、Implementation Delegation Gate、Delegated Worker Evidence、Reviewer Gate Status、Step Commit Gate。
  - amendment trigger:
    - preserve mode 追加、branch deletion、cleanup 範囲拡大、GitGateway signature 変更が必要になった場合。

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - `dev-coder`
- 正本（source of truth）:
  - Approved `requirement.md` / `design.md` / `plan.md` and provider-side runtime source under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`.
  - Dogfooding workspace files are not the implementation authority for this step.
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, `workflow_issue.md`, target files。
- 許可 paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
  - `tests/cli_runtime/test_worktree.py`
- 禁止 changes:
  - docs/help、`git_cli.py` signature、branch deletion、cleanup outside resolved target、canonical issue docs。
- 受け入れ条件:
  - `ci-001`, S01-owned `ci-009` pass。
- 必須 tests または docs-only verification:
  - focused dirty/untracked default remove test。
- reviewer focus:
  - `code-reviewer`: force-equivalent call、output schema stability、guard bypass なし。
- 必須出力（output required）:
  - changed files、red/green command results、closure ids、unresolved risks、Ledger Note。
- 停止条件（stop conditions）:
  - `force=True` で untracked residue を削除できない、cleanup 範囲拡大が必要、schema change が必要。

#### 具体テストケース一覧

- `tc-s01-001` acceptance: untracked residue default remove succeeds
  - 前提: temp Git repo に `worktree create untracked` で linked worktree があり、`cache.tmp` が Git 管理外で存在する。
  - 操作: `spec-dock worktree remove untracked --json` を実行する。
  - 期待結果: exit code 0、`removed_record=true`、`removed_directory=true`、`branch_deleted=false`、target path deleted、Git worktree record removed、branch remains。
  - 失敗検出: default remove が旧 contract のまま `git_worktree_remove_failed` になる回帰を検出する。
  - 検証方法: `tests/cli_runtime/test_worktree.py` の dirty remove test を red-first 更新する。
  - 関連 closure id: `ci-001`, `ci-009`

- `tc-s01-002` application: default request calls GitGateway with force-equivalent strength
  - 前提: fake gateway を使う application-level remove test で `WorktreeRemoveRequest(target="leftover")` を渡す。
  - 操作: `app_worktree.worktree_remove(...)` を実行する。
  - 期待結果: `git_gateway.remove_calls` は `(worktree_path, True)` になる。
  - 失敗検出: application layer が `req.force=False` をそのまま GitGateway に渡す回帰を検出する。
  - 検証方法: existing cleanup / gateway assertion を更新または追加する。
  - 関連 closure id: `ci-001`

#### ステップ完了契約（step closure contract）
- closure id:
  - `ci-001`, S01-owned `ci-009`
- close 条件:
  - Red / Green evidence、focused test pass、step `code-reviewer` pass、step commit / approved-no-op evidence。
- 検証 evidence:
  - focused dirty/untracked CLI test。
- report evidence:
  - Step Contract Closure、Test Contract Closure、Closure Coverage、Closure Delta。
- 残リスク:
  - none expected; Git version issue は S03 / EC-001 で扱う。

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: `code-reviewer`
  - review 範囲: S01 changed files and evidence。
  - pass 条件: `review_status: pass`
  - re-review rule: 指摘を修正し pass まで再実行。
- commit / no-op gate:
  - closure 状態: committed / approved-no-op
  - commit 範囲: S01 changed files only。

### 実装ステップ S02 — Tracked Modification And `--force` Compatibility
- 振る舞いの目標（behavior goal）:
  - tracked modification も default full delete し、`--force` 指定も互換入力として default と同じ contract を満たす。
- design 参照:
  - `design.md` の `インターフェース契約` と `テスト戦略`。
- 依存:
  - S01。
- unblock:
  - S03, S90。
- 対象ファイル:
  - `tests/cli_runtime/test_worktree.py`
  - 必要時のみ `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
- 計画済み契約（planned contract）:
  - scope:
    - tracked modification default success test を追加する。
    - `--force` compatibility success test を維持または追加する。
  - テスト義務（test obligation）:
    - closure id: `ci-002`, `ci-003`, S02-owned `ci-009`
    - coverage rationale: dirty の untracked / tracked 両義性と backward compatibility を分離して固定する。
  - Red / 代替証跡の要件:
    - red-required: tracked modification default success は現行実装で失敗する。
    - characterization-update: `--force` compatibility は既存 force success path を default equivalent として再固定する。
  - Green 検証:
    - tracked modification default test と `--force` compatibility test。
  - Refactor / cleanup ガードレール:
    - `--force` parser support を消さない。
    - strength enum や preserve option を追加しない。
  - report 証跡の記録先:
    - TDD / Red / Green / Refactor Evidence、Discovered Tests、Step Contract Closure、Test Contract Closure、Implementation Delegation Gate、Delegated Worker Evidence、Reviewer Gate Status、Step Commit Gate。
  - amendment trigger:
    - `--force` を別強度として扱う必要、または tracked dirty fixture が仕様外になる発見。

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - `dev-coder`
- 正本（source of truth）:
  - Approved `requirement.md` / `design.md` / `plan.md` and provider-side runtime source under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`.
  - Dogfooding workspace files are not the implementation authority for this step.
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, S01 evidence, target tests/source。
- 許可 paths:
  - `tests/cli_runtime/test_worktree.py`
  - 必要時のみ `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
- 禁止 changes:
  - `--force` 削除、GitGateway signature 変更、branch deletion、docs/help edits。
- 受け入れ条件:
  - `ci-002`, `ci-003`, S02-owned `ci-009` pass。
- 必須 tests または docs-only verification:
  - tracked modification default success、`--force` compatibility success。
- reviewer focus:
  - `code-reviewer`: test sensitivity、compatibility coverage、過剰 API 変更なし。
- 必須出力（output required）:
  - changed files、commands、closure ids、compatibility notes、Ledger Note。
- 停止条件（stop conditions）:
  - `--force` compatibility cannot be retained、tracked fixture cannot be represented in temp repo。

#### 具体テストケース一覧

- `tc-s02-001` acceptance: tracked modification default remove succeeds
  - 前提: temp Git repo の linked worktree に committed tracked file があり、その file を未コミット変更する。
  - 操作: `spec-dock worktree remove modified --json` を実行する。
  - 期待結果: exit code 0、Git worktree record removed、target path deleted、`branch_deleted=false`、branch remains。
  - 失敗検出: untracked residue だけ通り、tracked dirty state が Git refusal になる回帰を検出する。
  - 検証方法: `tests/cli_runtime/test_worktree.py` に tracked modification default remove test を追加する。
  - 関連 closure id: `ci-002`, `ci-009`

- `tc-s02-002` compatibility: `--force` remains accepted
  - 前提: dirty linked worktree があり、default remove と同じ eligible target 条件を満たす。
  - 操作: `spec-dock worktree remove <target> --force --json` を実行する。
  - 期待結果: default と同じ success contract を満たし、`--force` 指定による schema 差分はない。
  - 失敗検出: `--force` parser 削除、または `--force` path だけ別挙動になる互換回帰を検出する。
  - 検証方法: existing force portion を独立 test または updated dirty test の second case として残す。
  - 関連 closure id: `ci-003`, `ci-009`

#### ステップ完了契約（step closure contract）
- closure id:
  - `ci-002`, `ci-003`, S02-owned `ci-009`
- close 条件:
  - Red / Green evidence、focused tests pass、step `code-reviewer` pass、step commit / approved-no-op evidence。
- 検証 evidence:
  - tracked modification default test、`--force` compatibility test。
- report evidence:
  - Step Contract Closure、Test Contract Closure、Closure Coverage、Closure Delta。
- 残リスク:
  - none expected。

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: `code-reviewer`
  - review 範囲: S02 changed files and compatibility coverage。
  - pass 条件: `review_status: pass`
  - re-review rule: 指摘を修正し pass まで再実行。
- commit / no-op gate:
  - closure 状態: committed / approved-no-op
  - commit 範囲: S02 changed files only。

### 実装ステップ S03 — Guardrail, Error Path, And Diagnostic Preservation
- 振る舞いの目標（behavior goal）:
  - default full delete が hard blockers、Git-first failure、target-only cleanup、unmanaged diagnostic、branch retention を壊さない。
- design 参照:
  - `design.md` の `要件 / 例外 -> 検証マッピング` と `リスク / 移行 / ロールバック`。
- 依存:
  - S01, S02。
- unblock:
  - S90, S99。
- 対象ファイル:
  - `tests/cli_runtime/test_worktree.py`
  - 必要時のみ `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
- 計画済み契約（planned contract）:
  - scope:
    - hard blocker no-call assertions、Git failure no cleanup、post-remove cleanup failure、unmanaged default remove を確認する。
  - テスト義務（test obligation）:
    - closure id: `ci-004`, `ci-006`, `ci-007`, `ci-008`, remaining `ci-009`
    - coverage rationale: destructive default 化で最も危険な safety boundary を固定する。
  - Red / 代替証跡の要件:
    - covered-existing plus targeted update: 既存 fake gateway / runtime tests の expected force flag や command shape を更新する。
  - Green 検証:
    - `python -m unittest tests.cli_runtime.test_worktree.TestCliWorktree -v`
  - Refactor / cleanup ガードレール:
    - blocker resolution を infra へ移さない。
    - refreshed record check / containment guard を削らない。
  - report 証跡の記録先:
    - TDD / Red / Green / Refactor Evidence、Step Contract Closure、Test Contract Closure、Closure Coverage、Implementation Delegation Gate、Delegated Worker Evidence、Reviewer Gate Status、Step Commit Gate。
  - amendment trigger:
    - cleanup outside target、branch deletion、hard-blocker bypass、GitGateway signature/API change が必要になった場合。

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - `dev-coder`
- 正本（source of truth）:
  - Approved `requirement.md` / `design.md` / `plan.md` and provider-side runtime source under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`.
  - Dogfooding workspace files are not the implementation authority for this step.
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, S01/S02 evidence, target tests/source。
- 許可 paths:
  - `tests/cli_runtime/test_worktree.py`
  - 必要時のみ `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
- 禁止 changes:
  - docs/help、branch deletion、parent/namespace/root cleanup、canonical spec docs。
- 受け入れ条件:
  - `ci-004`, `ci-006`, `ci-007`, `ci-008`, remaining `ci-009` pass。
- 必須 tests または docs-only verification:
  - hard blocker, Git failure no cleanup, cleanup failure, unmanaged default remove tests。
- reviewer focus:
  - `code-reviewer`: destructive safety、containment、error code stability、output schema stability。
- 必須出力（output required）:
  - changed files、verification command result、closure ids、Git-version risks、Ledger Note。
- 停止条件（stop conditions）:
  - tests cannot distinguish pre-Git blockers、locked behavior is unstable beyond guarded skip、fix requires infra signature/API changes。

#### 具体テストケース一覧

- `tc-s03-001` negative: hard blockers stop before Git remove
  - 前提: fake gateway subcases for main、current、bare、missing path、record missing、containment-protected targets。
  - 操作: `app_worktree.worktree_remove(WorktreeRemoveRequest(...))` with default request and, where existing coverage uses it, `force=True`。
  - 期待結果: `remove_blocked` with expected blocker and `git_gateway.remove_calls == []`。
  - 失敗検出: default full delete accidentally bypasses application guard and calls Git remove。
  - 検証方法: existing hard-blocker tests are updated or supplemented for default request semantics。
  - 関連 closure id: `ci-004`

- `tc-s03-002` negative: Git refusal does not cleanup target
  - 前提: fake GitGateway raises `RuntimeError("git refused")` from `remove_worktree`; filesystem gateway raises if cleanup is touched。
  - 操作: `app_worktree.worktree_remove(WorktreeRemoveRequest(target="leftover"))` を実行する。
  - 期待結果: `git_worktree_remove_failed`; filesystem `path_exists` and `remove_target` are not called。
  - 失敗検出: Git failure after default force change triggers filesystem cleanup。
  - 検証方法: existing Git failure test, with expected force flag adjusted only if asserted。
  - 関連 closure id: `ci-006`

- `tc-s03-003` negative: post-remove cleanup failure remains distinguishable and target-only
  - 前提: GitGateway succeeds; filesystem gateway reports target exists and then raises `cleanup denied`。
  - 操作: `app_worktree.worktree_remove(WorktreeRemoveRequest(target="leftover"))` を実行する。
  - 期待結果: `post_remove_cleanup_failed`, `removed_record=true`, `removed_directory=false`, cleanup called only for resolved target path。
  - 失敗検出: cleanup error is hidden, schema changes, or parent/namespace cleanup is attempted。
  - 検証方法: existing cleanup failure and target-only cleanup tests with gateway force assertion updated to `True`。
  - 関連 closure id: `ci-007`

- `tc-s03-004` diagnostic: unmanaged linked worktree default remove succeeds
  - 前提: temp Git repo has external linked worktree created by raw `git worktree add`, no hard blocker。
  - 操作: `spec-dock worktree remove <external-basename> --json` without `--force`。
  - 期待結果: success, `removed_record=true`, `removed_directory=true`, `branch_deleted=false`, diagnostic fields remain present。
  - 失敗検出: unmanaged is incorrectly treated as a blocker or only `--force` path removes it。
  - 検証方法: update existing unmanaged remove assertion that currently uses `--force`。
  - 関連 closure id: `ci-008`, `ci-009`

#### ステップ完了契約（step closure contract）
- closure id:
  - `ci-004`, `ci-006`, `ci-007`, `ci-008`, remaining `ci-009`
- close 条件:
  - Guardrail/error/diagnostic tests pass、step `code-reviewer` pass、step commit / approved-no-op evidence。
- 検証 evidence:
  - focused affected tests, then `TestCliWorktree` suite where appropriate。
- report evidence:
  - Step Contract Closure、Test Contract Closure、Closure Coverage、Closure Delta。
- 残リスク:
  - Git version differences for locked worktree are acceptable if guarded and recorded under EC-001。

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: `code-reviewer`
  - review 範囲: S03 changed files and destructive safety。
  - pass 条件: `review_status: pass`
  - re-review rule: 指摘を修正し pass まで再実行。
- commit / no-op gate:
  - closure 状態: committed / approved-no-op
  - commit 範囲: S03 changed files only。

### ドキュメント影響の解消ステップ S90（docs impact resolution / docs refresh）
- 対象:
  - CLI help
  - provider docs: `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`
  - dogfooding docs: `spec-dock/docs/reference_worktree.md`
  - help assertion in `tests/cli_runtime/test_worktree.py` if useful
- 対応:
  - `--force` help を compatibility wording に更新する。
  - docs の remove section を default full delete / hard blocker / Git-first / target-only / branch retention / Git refusal / `--force` compatibility に合わせる。
- doc update owner:
  - `doc-writer`
- spec/doc review:
  - reviewer: `spec-reviewer`
  - pass 条件: docs/help が requirement / design / plan と整合し、old `--force` required wording が残らない。
- code/runtime review:
  - reviewer: `code-reviewer`
  - pass 条件: `commands/worktree.py` または `tests/cli_runtime/test_worktree.py` を変更した場合は必須。CLI help source / test assertion が runtime command surface として安全であることを確認する。

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - `doc-writer`
- 正本（source of truth）:
  - Approved `requirement.md` / `design.md` / `plan.md` define the issue contract.
  - Provider-side shipped docs and CLI source under `src/spec_dock/assets/spec_dock/...` are the source of truth for shipped behavior.
  - `spec-dock/docs/reference_worktree.md` is a dogfooding parity refresh / inspection target, not the source of truth.
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, provider/dogfooding docs, CLI help source。
- 許可 paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py`
  - `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`
  - `spec-dock/docs/reference_worktree.md`
  - 必要時のみ `tests/cli_runtime/test_worktree.py`
- 禁止 changes:
  - application/infra logic、new options、canonical issue docs、branch/delete/prune/status docs expansion outside scope。
- 受け入れ条件:
  - `ci-005` pass。
- 必須 tests または docs-only verification:
  - CLI help assertion or inspection、provider/dogfooding docs parity inspection。
- reviewer focus:
  - `spec-reviewer`: docs/spec alignment。
  - `code-reviewer`: mandatory if `commands/worktree.py` or `tests/cli_runtime/test_worktree.py` changes; verifies CLI help source/test changes do not alter runtime behavior unexpectedly。
- 必須出力（output required）:
  - changed docs/help paths、inspection summary、verification result、unresolved wording risks、Ledger Note。
- 停止条件（stop conditions）:
  - wording requires new option or contradicts EC-001、dogfooding docs cannot match provider docs。

#### 具体テストケース一覧

- `tc-s90-001` help: `--force` compatibility wording
  - 前提: runtime CLI help is available.
  - 操作: `spec-dock worktree remove --help` を確認する。
  - 期待結果: help says default remove fully deletes eligible worktrees and `--force` is accepted for compatibility, not required to enable dirty/untracked deletion。
  - 失敗検出: old wording `Pass --force to git worktree remove` remains and implies required option。
  - 検証方法: focused help assertion or documented inspection。
  - 関連 closure id: `ci-005`

- `tc-s90-002` docs: provider and dogfooding reference parity
  - 前提: provider `src/.../reference_worktree.md` and dogfooding `spec-dock/docs/reference_worktree.md` are readable。
  - 操作: remove section in both files を inspect する。
  - 期待結果: both docs describe default full delete, hard blockers, target-only cleanup, branch retention, `--force` compatibility, and Git refusal behavior without contradiction。
  - 失敗検出: provider/dogfooding docs drift or old dirty/untracked failure wording remains。
  - 検証方法: docs diff inspection。
  - 関連 closure id: `ci-005`

#### ステップ完了契約（step closure contract）
- closure id:
  - `ci-005`
- close 条件:
  - docs/help evidence、docs/spec review pass、step commit / approved-no-op evidence。
- 検証 evidence:
  - help assertion / inspection、provider/dogfooding docs inspection。
- report evidence:
  - Step Contract Closure、Test Contract Closure、Closure Coverage、Docs impact session log、Reviewer Gate Status。
- 残リスク:
  - none expected。

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer:
    - `spec-reviewer` for docs/spec alignment.
    - `code-reviewer` if `commands/worktree.py` or `tests/cli_runtime/test_worktree.py` changes.
  - review 範囲:
    - `spec-reviewer`: provider/dogfooding docs and CLI help wording against requirement/design/plan.
    - `code-reviewer`: CLI help source/test changes and runtime command surface safety.
  - pass 条件: required reviewers return `review_status: pass`
  - re-review rule: 指摘を修正し pass まで再実行。
- commit / no-op gate:
  - closure 状態: committed / approved-no-op
  - commit 範囲: S90 docs/help files。

### 最終品質ゲートステップ S99（final quality gate）
- branch diff 範囲:
  - S01..S90 の runtime/tests/docs/help/report changes。
- 必須 validation:
  - `python -m unittest tests.cli_runtime.test_worktree.TestCliWorktree -v`
  - `python -m unittest discover -v` は final QA / code reviewer が必要と判断した場合、または affected surface が broader runtime に広がった場合に実行する。
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
- final QA gate:
  - reviewer: `qa-reviewer`
  - 範囲: closure coverage、missing high-value tests、integration / manual test 要否。
  - pass 条件: reviewer pass。
- final code review ゲート:
  - reviewer: issue-wide `code-reviewer`
  - 範囲: integrated diff、layering、destructive safety、regression risk、maintainability。
  - pass 条件: `review_status: pass`。
- final spec review ゲート:
  - reviewer: final `spec-reviewer`
  - 範囲: requirement / design / plan / report / implementation / tests / docs alignment。
  - pass 条件: reviewer pass。
- final commit gate:
  - commit 範囲: final issue work。
  - final report ledger: all required closure and review evidence recorded before final commit.
  - post-commit external evidence destination: final response / PR body / issue comment as applicable。

#### 具体テストケース一覧

- `tc-s99-001` final verification: worktree focused suite
  - 前提: S01..S90 are closed.
  - 操作: `python -m unittest tests.cli_runtime.test_worktree.TestCliWorktree -v` を実行する。
  - 期待結果: pass。failure は issue-caused / pre-existing に分類してから進める。
  - 失敗検出: remove contract changes causing cross-test fixture regressions。
  - 検証方法: command output recorded in `report.md`。
  - 関連 closure id: `ci-001`..`ci-009`

- `tc-s99-002` final workflow validation: spec-dock validate/sync
  - 前提: report evidence and docs are updated.
  - 操作: `./spec-dock/scripts/spec-dock validate` and `./spec-dock/scripts/spec-dock sync` を実行する。
  - 期待結果: pass/success, or failures recorded with cause and next action。
  - 失敗検出: scaffold/docs/spec metadata drift after issue work。
  - 検証方法: command output recorded in final report ledger。
  - 関連 closure id: `ci-005`

## 未確定事項
- なし。

## 最終完了条件
- AC/EC 達成:
  - `ci-001`..`ci-009` が Step Contract Closure / Test Contract Closure / Closure Coverage で pass または valid approved-no-op。
- docs 影響解決:
  - CLI help、provider docs、dogfooding docs が default full delete / `--force` compatibility と整合。
- 全 implementation step 完了:
  - S01, S02, S03, S90, S99 が committed / valid approved-no-op。
- final quality gate pass:
  - `qa-reviewer`: pass
  - issue-wide `code-reviewer`: pass
  - final `spec-reviewer`: pass
- final commit 完了:
  - final report ledger 更新後に commit scope と post-commit clean evidence を外部 delivery evidence として残す。
- final clean state:
  - unintended staged / unstaged changes がない。
