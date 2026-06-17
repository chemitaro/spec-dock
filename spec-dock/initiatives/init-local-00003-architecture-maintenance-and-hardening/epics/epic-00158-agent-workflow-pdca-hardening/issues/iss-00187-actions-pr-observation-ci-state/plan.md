---
種別: 実装計画書（Issue）
ID: "iss-00187"
タイトル: "Use Actions Endpoint For PR Observation CI State"
関連GitHub: ["#187"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
依存: ["requirement.md", "design.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00187 Use Actions Endpoint For PR Observation CI State — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007, AC-008
- EC:
  - EC-001, EC-002, EC-003, EC-004
- 制約:
  - stdout final JSON authority
  - no raw secrets / raw auth stderr
  - fixed script surface, no arbitrary GitHub API proxy
  - provider source first, dogfooding mirror verified
  - unsupported / ambiguous / unobserved failure-risk state never silently passes
  - review completion unknown is non-pass and requires wait stability before terminal-like handling

## 依存関係から導く実装順序
- 依存関係の参照元:
  - `design.md` module dependency diagram and file change plan.
- 順序ルール:
  - CI collector output contract を先に固定する。
  - Wrapper behavior は collector contract の後で必要最小限だけ調整する。
  - Docs / mirror は behavior contract が固まってから更新する。
  - Final gates は issue-wide diff と closure coverage を見て実施する。
- step 依存サマリー:
  - S01:
    - 依存: requirement / design
    - unblock: Actions-primary green and supplemental permission semantics
    - 対象ファイル: provider collector and focused tests
  - S02:
    - 依存: S01
    - unblock: failure/running/pending/zero/API-unavailable taxonomy
    - 対象ファイル: provider collector and focused tests
  - S03:
    - 依存: S01, S02
    - unblock: snapshot/wait top-level classification and non-blocking supplemental limitation handling
    - 対象ファイル: snapshot/wait scripts and wrapper tests
  - S90:
    - 依存: S01-S03 behavior settled
    - unblock: permission docs and dogfooding mirror
    - 対象ファイル: `SKILL.md`, `.agents/...`
  - S99:
    - 依存: S01-S03, S90
    - unblock: original Actions-primary CI completion readiness
  - S100:
    - 依存: S99 and post-observation PR #190 evidence
    - unblock: review no-completion evidence contract
    - 対象ファイル: provider review collector and focused tests
  - S101:
    - 依存: S100
    - unblock: stable review completion unknown wait behavior
    - 対象ファイル: snapshot/wait wrappers and focused tests
  - S102:
    - 依存: S100
    - unblock: optional explicit no-findings secondary signal
    - 対象ファイル: provider review collector and focused tests
  - S190:
    - 依存: S100-S101 and S102 if implemented
    - unblock: docs/mirror addendum consistency
  - S199:
    - 依存: S100-S101, S102 if implemented, S190
    - unblock: final addendum completion readiness

## ステップ一覧
- S01:
  - 観測可能な振る舞い: Actions-only green can produce `ci.status="passed"` with explicit coverage limitation while check-runs / status rollup permission denial does not become the normal blocker.
  - 依存: none after approved design
  - unblock: S02, S03
  - 対象ファイル: `fetch_pr_checks_snapshot.sh`, `tests/unit/infra/test_init_update.py`
  - 閉じる要件: AC-001, AC-002, AC-005, EC-002
  - レビューゲート: code-reviewer pass
- S02:
  - 観測可能な振る舞い: Actions run/job taxonomy handles failure, running, pending, zero runs, and Actions API unavailable without false pass.
  - 依存: S01
  - unblock: S03
  - 対象ファイル: `fetch_pr_checks_snapshot.sh`, `tests/unit/infra/test_init_update.py`
  - 閉じる要件: AC-003, AC-004, AC-005, EC-001, EC-004
  - レビューゲート: code-reviewer pass
- S03:
  - 観測可能な振る舞い: snapshot/wait wrappers preserve top-level `normalized_status`, `recommended_next_action`, stale head, wait semantics, and ignore informational supplemental permission limitations under Actions-primary CI output.
  - 依存: S01, S02
  - unblock: S90, S99
  - 対象ファイル: `fetch_pr_observation_snapshot.sh`, `wait_pr_observation.sh`, tests
  - 閉じる要件: AC-001..AC-004, EC-003
  - レビューゲート: code-reviewer pass
- S90:
  - 観測可能な振る舞い: skill docs and dogfooding mirror describe and ship the Actions-primary contract.
  - 依存: S01-S03
  - 対象ファイル: provider `SKILL.md`, `.agents/...` mirror
  - 閉じる要件: provider/mirror constraint, operator remediation clarity
  - レビューゲート: spec-reviewer or code-reviewer depending on diff shape
- S99:
  - 観測可能な振る舞い: issue-wide tests, QA, code review, spec review, and report ledger are complete.
  - 依存: S01-S03, S90
  - 対象ファイル: issue-wide diff
  - 閉じる要件: all AC/EC and closure IDs
  - レビューゲート: qa-reviewer, code-reviewer, spec-reviewer pass

## 要件 ↔ ステップ対応
- AC-001 -> S01, S03
- AC-002 -> S01, S03
- AC-003 -> S02
- AC-004 -> S02, S03
- AC-005 -> S01, S02
- AC-006 -> S100, S101
- AC-007 -> S100, S101
- AC-008 -> S410, S420
- EC-001 -> S02
- EC-002 -> S01
- EC-003 -> S03
- EC-004 -> S02
- Fixed script / stdout / secret constraints -> S01, S02, S03, S99
- Provider/mirror constraint -> S90, S99
- Review completion unknown addendum -> S100, S101, S190, S199
- Optional no-findings secondary signal -> S102 if implemented

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ | スライス | 種別 | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル | クロージャ証跡 |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-s01-001 | S01 | actions-only-green | acceptance | AC-001, AC-002, EC-002 | Actions runs/jobs all terminal green -> `ci.status="passed"` and coverage limitation exists | Actions read succeeds; check-runs / status rollup permission denied or unavailable | unfixable Checks permission blocker; hidden coverage gap | yes | red-required | report: TDD Evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate |
| tc-s01-002 | S01 | supplemental-permission | negative | AC-001, AC-005 | Supplemental check/rollup permission denial is not the normal blocking remediation when Actions is decisive | `github_token_permission_denied` for `check_runs_read` or `status_check_rollup_read` | false blocker / wrong remediation | yes | red-required | report: TDD Evidence, Test Contract Closure, Closure Coverage |
| tc-s02-001 | S02 | actions-failure | acceptance | AC-003 | Failed workflow/job/step -> `ci.status="failed"` and `ci.failures` includes sanitized Actions job evidence with `kind`, workflow/job fields, `failed_steps[]`, and `dedupe_key` | Actions jobs include failed step | false pass on failed CI; unusable repair evidence | yes | red-required | report: TDD Evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate |
| tc-s02-002 | S02 | stale-conclusion | negative | AC-003, EC-003 | Workflow/job `stale` conclusion is CI failure, not stale head freshness | completed Actions run/job with `conclusion="stale"` | stale taxonomy collapse | yes | red-required | report: TDD Evidence, Test Contract Closure, Closure Coverage |
| tc-s02-003 | S02 | running-pending | acceptance | AC-004 | queued/requested/waiting/pending/in_progress -> `pending` or `running`, not `passed` | Actions run/job non-terminal status | premature merge readiness | yes | red-required | report: TDD Evidence, Test Contract Closure, Closure Coverage |
| tc-s02-004 | S02 | actions-api-unavailable | negative | AC-005, EC-004 | Actions primary permission/auth/rate/schema/transient failure -> `unknown` with `capability="actions_read"` and secret redaction | Actions workflow runs API fails | silent pass / leaked token | yes | red-required | report: TDD Evidence, Test Contract Closure, Closure Coverage |
| tc-s02-005 | S02 | zero-actions-runs | edge | EC-001 | zero workflow runs -> `none` or `unknown`, never `passed` | Actions API returns zero runs | pass before CI starts | yes | red-required | report: TDD Evidence, Test Contract Closure, Closure Coverage |
| tc-s03-001 | S03 | snapshot-actions-pass | integration | AC-001, AC-002 | Snapshot wrapper propagates Actions-only `passed` and coverage limitation without `fix_github_token_permissions` | fake `gh` end-to-end snapshot scenario | wrapper re-blocking supplemental limitation | yes | red-required | report: TDD Evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate |
| tc-s03-002 | S03 | wait-actions-pending | integration | AC-004 | Wait wrapper keeps Actions pending/running as wait/resume | fake `gh` wait scenario | loop completion too early | yes | red-required | report: TDD Evidence, Test Contract Closure, Closure Coverage |
| tc-s03-003 | S03 | stale-head-freshness | regression | EC-003 | Existing head mismatch / head change remains `stale_head` with `rerun_for_current_head` | expected head differs from current/final head | CI failure vs freshness confusion | yes | covered-existing | report: Test Contract Closure, Closure Coverage |
| tc-s90-001 | S90 | skill-docs | docs | AC-001, AC-005 | `SKILL.md` names Actions read as normal CI permission and avoids Checks as normal remedy | provider and mirror docs inspection | operator follows impossible permission advice | yes | inspect-only | report: Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate |
| tc-s90-002 | S90 | mirror-sync | scaffold | provider/mirror constraint | dogfooding mirror matches provider assets for changed files | file comparison / sync command | provider/dogfood drift | yes | inspect-only | report: Test Contract Closure, Closure Coverage |
| tc-s99-001 | S99 | final-validation | quality | all AC/EC | focused tests and SpecDock validation pass or failures are explained | test commands, `spec-dock validate`, reviews | incomplete closure | yes | manual-required | report: Final QA Gate, Final Code Review Gate, Final Spec Review Gate, Final Commit |
| tc-s100-001 | S100 | review-no-completion-evidence | acceptance | AC-006 | Current-boundary no-completion evidence remains machine-readable and distinguishable from blockers/pending signals | no selected current reviews/comments/threads, no pending request, no blocking collection failure | wrapper cannot later classify stable unknown safely | yes | red-required or inspection-if-existing | report: TDD Evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate |
| tc-s100-002 | S100 | no-false-pass | negative | AC-006 | no-completion evidence is not `passed` and not `merge_prepared` at collector/snapshot level | same as tc-s100-001 | no-signal false pass | yes | red-required or covered-existing | report: TDD Evidence, Test Contract Closure, Closure Coverage |
| tc-s100-003 | S100 | pending-review-preserved | negative | AC-007 | pending review request / pending current review signal remains pending and is not eligible for unknown promotion | current review request or pending PR review exists | premature unknown terminal state | yes | red-required or covered-existing | report: TDD Evidence, Test Contract Closure, Closure Coverage |
| tc-s101-001 | S101 | snapshot-review-unknown | integration | AC-006 | Combined snapshot preserves no-completion evidence as pending/non-pass before wait stability | CI passed, head matched, no completion signal | single-poll snapshot prematurely stops review wait | yes | red-required | report: TDD Evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate |
| tc-s101-002 | S101 | wait-review-unknown | integration | AC-006 | Wait exits with `review_completion_unknown` instead of generic `wait_timeout` only after quiet/same-fingerprint stability | stable no-completion evidence, CI passed, head matched | wasted wait/resume loop or premature unknown | yes | red-required | report: TDD Evidence, Test Contract Closure, Closure Coverage |
| tc-s101-003 | S101 | existing-missing-signal | regression | AC-007 | truly missing/unstable completion signal still waits and may timeout | review still pending or missing before stability condition | review running treated as done | yes | covered-existing plus focused regression | report: Test Contract Closure, Closure Coverage |
| tc-s102-001 | S102 | no-findings-comment | optional acceptance | AC-006 | strict current-boundary Codex no-findings issue comment can produce distinct secondary signal if adopted | allowlisted body, Codex-authored, after trigger, no blockers | no-review no-findings remains unobservable when explicit evidence exists | optional | red-required if implemented | report: Discovered Tests, Test Contract Closure, Closure Coverage |
| tc-s102-002 | S102 | fallback-preserved | negative | AC-006 | generic `fallback_issue_comment` remains low-confidence human gate | current Codex comment with non-allowlisted body | generic comment false pass | yes if S102 implemented | red-required if implemented | report: Test Contract Closure, Closure Coverage |
| tc-s102-003 | S102 | blockers-win | negative | AC-006 | current unresolved threads / changes-requested evidence override no-findings signal | no-findings comment plus selected blocker | blocker masked by positive comment | yes if S102 implemented | red-required if implemented | report: Test Contract Closure, Closure Coverage |
| tc-s102-004 | S102 | boundary-safety | negative | AC-006 | old trigger / non-Codex / ambiguous no-findings artifacts do not complete | stale or ambiguous comment/reaction | stale-boundary false pass | yes if S102 implemented | red-required if implemented | report: Test Contract Closure, Closure Coverage |
| tc-s190-001 | S190 | docs-mirror-addendum | docs/scaffold | AC-006, AC-007 | Provider docs/mirror describe review completion unknown and optional secondary signal semantics | changed provider/mirror files | operator or dogfooding drift | yes | inspect-only | report: Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate |
| tc-s199-001 | S199 | final-addendum-validation | quality | AC-006, AC-007 | focused tests, mirror checks, validation, and reviewer gates pass or are explicitly explained | final addendum diff | incomplete closure | yes | manual-required | report: Final QA Gate, Final Code Review Gate, Final Spec Review Gate, Final Commit |

## レビュー / QA ゲート方針
- RG1 step review:
  - 実施タイミング: S01, S02, S03, S90 の各 implementation step 完了時。
  - reviewer: code-reviewer for code/test/runtime/scaffold behavior; spec-reviewer for docs-only scope.
  - pass 条件: `review_status: pass`。
- QG1 final QA:
  - reviewer: qa-reviewer。
  - 範囲: Issue 全体の closure ID、missing high-value tests、integration/manual test 要否。
  - pass 条件: `review_status: pass`。
- SG1 final spec review:
  - reviewer: spec-reviewer。
  - 範囲: requirement / design / plan / report / implementation evidence alignment。
  - pass 条件: `review_status: pass`。

## 実行ルール（全ステップ共通）
- 各 implementation step は原則 1 behavior slice / 1 review scope / 1 commit boundary とする。
- 実装者は provider source を先に変更し、mirror は S90 で同期・検証する。
- 実装中に新しい blocking requirement gap が見つかった場合は requirement/design/plan へ戻し、spec-reviewer を再実行する。
- stdout JSON contract、secret redaction、fixed API surface を壊す変更は step 内で完了扱いしない。
- `report.md` に Red/Green/Refactor evidence、reviewer verdict、closure delta を残す。

## 実装ステップ

### 実装ステップ S01 — Actions-only green and supplemental permission contract
- 振る舞いの目標:
  - Actions workflow runs/jobs が terminal green のとき、check-runs / status rollup が読めなくても `ci.status="passed"` と coverage limitation を返す。
- design 参照:
  - `design.md` Interface Contract, Status Taxonomy, Permission Semantics.
- 依存:
  - approved requirement/design.
- unblock:
  - S02 taxonomy and S03 wrappers.
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - scope:
    - Add fixed Actions workflow runs API collection by head SHA.
    - Add `ci.actions` summary sufficient for Actions-only green.
    - Convert supplemental check-runs / status rollup permission denial to non-blocking coverage semantics when Actions primary is decisive green.
  - テスト義務:
    - closure id: `tc-s01-001`, `tc-s01-002`
  - Red / 代替証跡:
    - red-required: fake `gh` test must fail before implementation because Actions workflow runs are not yet primary.
  - 実装範囲:
    - allowed paths: listed target files only.
    - forbidden changes: wrapper scripts, skill docs, mirror files in this step unless required by failing focused tests.
  - Green 検証:
    - `uv run pytest tests/unit/infra/test_init_update.py -k "actions_only or issue_187 or checks_collector"`.
  - amendment trigger:
    - Actions green cannot be represented without changing public JSON fields incompatibly.

#### 委任契約（S01）
- delegated role:
  - dev-coder
- input docs:
  - `requirement.md`, `design.md`, `plan.md`, current collector and tests.
- allowed paths:
  - provider collector and `tests/unit/infra/test_init_update.py`.
- forbidden changes:
  - no arbitrary endpoint inputs; no raw stderr/token output; no Codex review collector changes.
- acceptance:
  - `tc-s01-001` and `tc-s01-002` close with red/green evidence.
- required tests or docs-only verification:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187 or actions_only or checks_collector"` or a narrower equivalent justified in `report.md`.
- reviewer focus:
  - code-reviewer: Actions API path safety, JSON compatibility, supplemental limitation blocking semantics, secret redaction, and focused fake `gh` tests.
- required output:
  - changed files, tests run, closure evidence, unresolved risks.
- report evidence destination:
  - `report.md` TDD Evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate, Delegated Worker Evidence.
- stop conditions:
  - public CLI must change; Actions API path cannot be fixed; secret redaction cannot be preserved.

#### 具体テストケース一覧（S01）
- `tc-s01-001` acceptance: Actions-only green passes with limitation
  - 前提: fake `gh` returns successful Actions runs/jobs; check-runs or status rollup returns permission denied.
  - 操作: run provider `fetch_pr_checks_snapshot.sh`.
  - 期待結果: `ci.status="passed"`, `ci.actions.available=true`, limitation `ci_coverage_limited_to_github_actions`, no top-level `fix_github_token_permissions`.
  - 失敗検出: Actions green を check-runs permission denial で `unknown` / `fix_github_token_permissions` に戻す回帰を検出する。
  - 検証方法: pytest fake `gh`.
- `tc-s01-002` negative: supplemental permission is not normal blocker
  - 前提: Actions primary is decisive; supplemental API emits token-shaped stderr.
  - 操作: run collector.
  - 期待結果: token string absent from stdout/stderr evidence; supplemental limitation is informational/non-blocking or folded into coverage limitation.
  - 失敗検出: supplemental permission stderr が raw leak する、または blocking limitation として wrapper へ渡る回帰を検出する。
  - 検証方法: pytest fake `gh` secret absence assertions.

#### ステップ完了契約（S01）
- close 条件:
  - both closure IDs pass and report records red/green evidence.
- report 証跡の記録先:
  - TDD Evidence for red/green, Test Contract Closure for `tc-s01-001` and `tc-s01-002`, Step Contract Closure for S01, Closure Coverage for closed IDs, Reviewer Gate Status for code-reviewer result, Step Commit Gate for commit/no-op decision.
- reviewer gate:
  - code-reviewer pass before commit.

### 実装ステップ S02 — Actions taxonomy, failures, zero runs, and primary API failure
- 振る舞いの目標:
  - Actions run/job statuses and conclusions map to failed/running/pending/none/unknown without false pass.
- design 参照:
  - `design.md` Status Taxonomy and Requirement Mapping.
- 依存:
  - S01.
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - scope:
    - Add failure/running/pending/zero/unknown classification for Actions runs/jobs.
    - Populate `ci.failures` from failed Actions jobs/steps where available.
    - Make Actions primary API failures blocking with `capability="actions_read"`.
  - テスト義務:
    - closure id: `tc-s02-001`..`tc-s02-005`
  - Red / 代替証跡:
    - red-required for each closure ID.
  - 実装範囲:
    - allowed paths: provider collector and tests.
    - forbidden changes: branch protection model, CI log parsing, wrapper behavior except if S02 tests prove collector-only impossible.
  - Green 検証:
    - focused pytest for issue_187 / actions taxonomy tests.
  - amendment trigger:
    - A new GitHub state cannot be classified by the taxonomy without changing requirement semantics.

#### 委任契約（S02）
- delegated role:
  - dev-coder
- input docs:
  - `requirement.md`, `design.md`, `plan.md`, S01 diff/report evidence.
- allowed paths:
  - provider collector and `tests/unit/infra/test_init_update.py`.
- forbidden changes:
  - no snapshot/wait docs changes unless explicitly escalated to S03/S90.
- acceptance:
  - `tc-s02-001`..`tc-s02-005` close.
- required tests or docs-only verification:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187 or actions or stale or zero"` or a narrower equivalent justified in `report.md`.
- reviewer focus:
  - code-reviewer: status/conclusion taxonomy, `ci.failures[]` shape, fallback and dedupe behavior, primary Actions blocking limitation, no false pass.
- required output:
  - changed files, tests run, closure evidence, unresolved risks.
- report evidence destination:
  - `report.md` TDD Evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate, Delegated Worker Evidence, Discovered Tests if taxonomy gaps appear.
- stop conditions:
  - observed failure/running/pending cannot be distinguished from green.

#### 具体テストケース一覧（S02）
- `tc-s02-001` acceptance: failed job/step surfaces failure detail
  - 前提: fake `gh` returns an Actions workflow run with a failed job and failed step for expected head SHA.
  - 操作: run provider `fetch_pr_checks_snapshot.sh`.
  - 期待結果: `ci.status="failed"`, `ci.failures[].kind="github_actions_job"`, workflow/job identifiers are present, `failed_steps[]` is sanitized, and `dedupe_key` is stable.
  - 失敗検出: failed Actions job が `passed` / `unknown` になる、または repair workflow が使える failure detail を得られない回帰を検出する。
  - 検証方法: pytest fake `gh` collector test with failed job/step payload.
- `tc-s02-002` negative: stale conclusion is CI failure
  - 前提: fake `gh` returns completed Actions run/job with `conclusion="stale"` and matching head SHA.
  - 操作: run provider `fetch_pr_checks_snapshot.sh`.
  - 期待結果: workflow/job `conclusion="stale"` yields `ci.status="failed"` and not `stale_head`.
  - 失敗検出: CI-level stale conclusion を PR head freshness failure と混同し、`rerun_for_current_head` へ誘導する回帰を検出する。
  - 検証方法: pytest fake `gh` collector test asserting `ci.status` and absence of `stale_head`.
- `tc-s02-003` acceptance: running/pending states wait
  - 前提: fake `gh` returns Actions run/job states such as `in_progress`, `queued`, `requested`, `waiting`, or `pending`.
  - 操作: run provider `fetch_pr_checks_snapshot.sh` for each representative state.
  - 期待結果: `in_progress` -> `running`; queued/requested/waiting/pending -> `pending`; never `passed`.
  - 失敗検出: non-terminal Actions state が terminal green として扱われる premature merge readiness regression を検出する。
  - 検証方法: parametrized pytest fake `gh` collector tests.
- `tc-s02-004` negative: Actions API unavailable
  - 前提: fake `gh` returns permission denied/auth/rate/schema/transient failure for `repos/{repo}/actions/runs?head_sha=...`.
  - 操作: run provider `fetch_pr_checks_snapshot.sh`.
  - 期待結果: `ci.status="unknown"`; limitation has `capability="actions_read"` and redacted stderr hash.
  - 失敗検出: Actions primary API failure を成功扱いする、supplemental source だけで pass に昇格する、または token/raw stderr を漏らす回帰を検出する。
  - 検証方法: pytest fake `gh` collector tests with secret marker assertions.
- `tc-s02-005` edge: zero Actions runs
  - 前提: fake `gh` returns an empty workflow runs payload for expected head SHA.
  - 操作: run provider `fetch_pr_checks_snapshot.sh`.
  - 期待結果: `none` or `unknown`, zero-runs limitation, never `passed`.
  - 失敗検出: CI がまだ存在しない / 作成遅延の状態を green と扱う回帰を検出する。
  - 検証方法: pytest fake `gh` collector test asserting zero-run status and limitation.

#### ステップ完了契約（S02）
- close 条件:
  - all S02 closure IDs pass and report records any taxonomy delta.
- report 証跡の記録先:
  - TDD Evidence for each red/green obligation, Test Contract Closure for `tc-s02-001`..`tc-s02-005`, Step Contract Closure for S02, Closure Coverage, Closure Delta if aliases are introduced, Reviewer Gate Status, Step Commit Gate.
- reviewer gate:
  - code-reviewer pass before commit.

### 実装ステップ S03 — Snapshot and wait wrapper classification
- 振る舞いの目標:
  - Wrapper scripts consume Actions-primary collector output without reintroducing `Checks` permission blocker or stale-head confusion.
- design 参照:
  - `design.md` Sequence Delta and Interface Contract.
- 依存:
  - S01, S02.
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - scope:
    - Adjust wrapper blocking limitation checks so only blocking limitations trigger permission remediation.
    - Ensure informational supplemental permission limitations do not trigger `fix_github_token_permissions` when Actions primary status is decisive.
    - Preserve existing stale head detection from expected/current/final head mismatch.
    - Add or update wrapper tests for Actions-only pass and pending/running wait.
  - テスト義務:
    - closure id: `tc-s03-001`, `tc-s03-002`, `tc-s03-003`
  - Red / 代替証跡:
    - red-required for new wrapper behavior; covered-existing for stale head.
  - 実装範囲:
    - allowed paths: wrapper scripts and tests.
    - forbidden changes: review collector, trigger script, merge automation.
  - Green 検証:
    - focused pytest for snapshot/wait issue_187 tests plus stale head regression.
  - amendment trigger:
    - wrapper public output must change incompatibly.

#### 委任契約（S03）
- delegated role:
  - dev-coder
- input docs:
  - `requirement.md`, `design.md`, `plan.md`, S01/S02 report evidence.
- allowed paths:
  - wrapper scripts and tests only.
- forbidden changes:
  - no review lifecycle changes; no merge automation.
- acceptance:
  - `tc-s03-001`..`tc-s03-003` close.
- required tests or docs-only verification:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187 or pr_observation_snapshot or pr_observation_wait or stale_head"` or a narrower equivalent justified in `report.md`.
- reviewer focus:
  - code-reviewer: wrapper permission blocker logic, `normalized_status` / `recommended_next_action`, stale head separation, and preservation of wait/resume behavior.
- required output:
  - changed files, tests run, closure evidence, unresolved risks.
- report evidence destination:
  - `report.md` TDD Evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate, Delegated Worker Evidence.
- stop conditions:
  - stale head and CI failure cannot remain distinct.

#### 具体テストケース一覧（S03）
- `tc-s03-001` integration: snapshot propagates Actions-only pass
  - 前提: fake `gh` end-to-end scenario where PR head matches, Actions CI is terminal green, review state is merge-ready or neutral, and supplemental permission is informational/non-blocking.
  - 操作: run provider `fetch_pr_observation_snapshot.sh`.
  - 期待結果: top-level `normalized_status` / `recommended_next_action` align with CI passed and review state; no `fix_github_token_permissions` from supplemental denial.
  - 失敗検出: collector が non-blocking にした supplemental limitation を wrapper が再び permission blocker に戻す回帰を検出する。
  - 検証方法: pytest fake `gh` snapshot wrapper test.
- `tc-s03-002` integration: wait preserves pending/running
  - 前提: fake `gh` wait scenario where Actions state is pending/running before timeout or before later terminal state.
  - 操作: run provider `wait_pr_observation.sh` with short timeout/poll interval.
  - 期待結果: wait keeps polling or returns wait/resume action when Actions state is not terminal green/failed.
  - 失敗検出: pending/running CI を early complete と扱う、または wrong remediation を返す wait regression を検出する。
  - 検証方法: pytest fake `gh` wait wrapper test.
- `tc-s03-003` regression: stale head remains freshness failure
  - 前提: fake `gh` returns current/final PR head that differs from provided expected head, independent of Actions CI state.
  - 操作: run provider `fetch_pr_observation_snapshot.sh` and/or `wait_pr_observation.sh`.
  - 期待結果: existing stale head tests still pass with `rerun_for_current_head`.
  - 失敗検出: PR head mismatch を CI failure と扱う、または stale workflow conclusion と混同する回帰を検出する。
  - 検証方法: existing stale-head pytest cases plus any issue_187 wrapper regression added in S03.

#### ステップ完了契約（S03）
- close 条件:
  - wrapper tests and stale head regression pass.
- report 証跡の記録先:
  - TDD Evidence for wrapper red/green, Test Contract Closure for `tc-s03-001`..`tc-s03-003`, Step Contract Closure for S03, Closure Coverage, Reviewer Gate Status, Step Commit Gate.
- reviewer gate:
  - code-reviewer pass before commit.

### ドキュメント影響の解消ステップ S90（docs impact resolution / docs refresh）
- 対象:
  - Provider `SKILL.md` permission/remediation text.
  - Dogfooding mirror `.agents/skills/github-pr-observation/` changed files.
- 対応:
  - Update docs so Actions read is normal CI observation permission.
  - State that Checks read / status rollup may be supplemental and that unavailable supplemental coverage is expressed as limitation.
  - Sync or copy provider changes to dogfooding mirror and verify changed files match where intended.
- doc update owner:
  - doc-writer owns skill-text wording for provider `SKILL.md` and mirror `SKILL.md`.
  - dev-coder or utility-worker may perform mechanical mirror sync for changed scripts after S01-S03.
- closure IDs:
  - `tc-s90-001`, `tc-s90-002`
- verification:
  - `diff` / checksum / inspection of provider vs mirror changed files.
  - focused pytest that asserts installed asset content if existing tests cover it.
- spec/doc review:
  - spec-reviewer pass if docs-only; code-reviewer pass if mixed with scripts.

#### 委任契約（S90）
- delegated role:
  - doc-writer for shipped skill-text wording.
  - dev-coder or utility-worker for mechanical mirror sync of changed scripts if script files changed in S01-S03.
- input docs:
  - `requirement.md`, `design.md`, `plan.md`, S01-S03 report evidence, provider `SKILL.md`, changed provider scripts, dogfooding mirror files.
- allowed paths:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - `.agents/skills/github-pr-observation/SKILL.md`
  - `.agents/skills/github-pr-observation/scripts/**` only for mirror copies of changed provider scripts.
  - Provider/mirror files changed by S01-S03 and required sync tests.
- forbidden changes:
  - no workflow docs outside the issue unless a new docs impact is recorded and assigned to doc-writer.
  - no source code behavior changes beyond mechanical provider/mirror synchronization.
  - no generated local-only or scratch files.
- acceptance:
  - `tc-s90-001` and `tc-s90-002` close.
- required tests or docs-only verification:
  - docs inspection proving permission/remediation wording matches Actions-primary contract.
  - file comparison or sync verification proving intended provider/mirror changed files match.
  - focused pytest for installed asset content if existing tests cover the touched asset.
- reviewer focus:
  - spec-reviewer for skill-text docs/spec alignment.
  - code-reviewer for mechanical script mirror sync or scaffold behavior changes. Focus on provider/mirror consistency and no unintended behavior edits.
- required output:
  - changed files, sync or comparison result, docs inspection result, unresolved risks, report evidence notes.
- report evidence destination:
  - `report.md` Step Contract Closure, Test Contract Closure, Closure Coverage, Docs Impact Resolution, Reviewer Gate Status, Step Commit Gate, Delegated Worker Evidence.
- stop conditions:
  - provider and mirror cannot be aligned; a broader workflow/doc update becomes required; docs wording would contradict requirement/design.

#### 具体テストケース一覧（S90）
- `tc-s90-001` docs: skill docs name Actions read as normal permission
  - 前提: S01-S03 behavior is implemented or approved-no-op, and provider/mirror `SKILL.md` are in scope for wording update.
  - 操作: inspect provider and mirror `SKILL.md` permission/remediation sections.
  - 期待結果: docs identify Actions read as the normal CI observation permission, describe Checks/status rollup as supplemental where applicable, and avoid presenting Checks read as the ordinary fix for Actions-decisive green.
  - 失敗検出: user/operator docs still instruct an ungrantable Checks permission as the normal remedy, contradicting AC-001/AC-005.
  - 検証方法: docs inspection recorded in `report.md` Docs Impact Resolution and, if useful, focused text assertions in existing asset tests.
- `tc-s90-002` scaffold: provider and dogfooding mirror align
  - 前提: provider files changed by S01-S03/S90 and matching mirror paths exist under `.agents/skills/github-pr-observation/`.
  - 操作: compare changed provider files with intended mirror files, or run the approved sync/copy mechanism and inspect diff.
  - 期待結果: changed provider skill assets and dogfooding mirror are identical where intended; any intentional difference is documented in `report.md`.
  - 失敗検出: local dogfooding workflow uses stale script/doc behavior that differs from shipped provider assets.
  - 検証方法: `diff`/checksum/file comparison plus focused pytest if asset-content coverage exists.

#### ステップ完了契約（S90）
- close 条件:
  - skill docs reflect Actions-primary permission contract and provider/mirror changed files are aligned or intentional differences are recorded.
- report 証跡の記録先:
  - Docs Impact Resolution for doc status, Test Contract Closure for `tc-s90-001` and `tc-s90-002`, Step Contract Closure for S90, Closure Coverage, Reviewer Gate Status, Step Commit Gate.

### 最終品質ゲートステップ S99（final quality gate）
- branch diff 範囲:
  - Provider PR observation skill assets, dogfooding mirror, focused tests, issue docs/report.
- 必須 validation:
  - Focused pytest for all issue_187 / PR observation CI tests.
  - `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation or issue_187"` or narrower/faster equivalent justified in report.
  - `./spec-dock/scripts/spec-dock validate`.
- final QA gate:
  - reviewer: qa-reviewer
  - 範囲: closure index coverage and missing high-value tests.
  - pass 条件: `review_status: pass`.
- final code review gate:
  - reviewer: code-reviewer
  - 範囲: integrated runtime/scripts/tests/docs asset diff.
  - pass 条件: `review_status: pass`.
- final spec review gate:
  - reviewer: spec-reviewer
  - 範囲: requirement / design / plan / report / implementation evidence alignment.
  - pass 条件: `review_status: pass`.
- final commit gate:
  - commit 範囲: one step commit per S01/S02/S03/S90 where feasible, or documented combined commit if steps were inseparable.
  - final report ledger: all closure IDs complete or explicitly amended/reviewed.

## 未確定事項
- Blocking:
  - なし。
- Non-blocking:
  - Exact `ci.actions` internal field layout may be refined during S01/S02 if public expectation and tests remain aligned with `design.md`.
  - S03 may be no-op if wrappers already honor non-blocking limitation severity after collector changes. If no-op, record approved no-op evidence in report.

## 最終完了条件
- AC/EC 達成:
  - AC-001..AC-008 and EC-001..EC-004 mapped closure IDs pass.
- docs 影響解決:
  - S90 and S190 complete; provider and mirror are aligned or intentional differences are recorded.
- 全 implementation step 完了:
  - S01, S02, S03, S90, S100, S101, S102 if implemented, S190 committed or approved-no-op/deferred with report evidence.
- final quality gate pass:
  - qa-reviewer: pass
  - issue-wide code-reviewer: pass
  - spec-reviewer: pass
- final commit 完了:
  - Conventional Japanese commit message via commit skill when user requests commit/PR flow.
- 必須 closure id 完了:
  - `tc-s01-001`..`tc-s99-001` and addendum closure IDs `tc-s100-001`..`tc-s101-003`, `tc-s190-001`, `tc-s199-001` pass or approved-no-op/deferred where the plan explicitly allows it.
  - S102 closure IDs are required only if S102 is implemented; if deferred, `report.md` must record the evidence and revisit condition.
- final clean state:
  - no unintended staged / unstaged changes; intended docs/code/test changes visible in final diff.

## 追加修正計画（Post-Observation Review Completion Contract Addendum）

### 追加の背景
- PR #190 head `fc3041f86a7f9defba2d3fd8b48ff1c48126151a` の観測で、CI は `passed`、head は `matched` だったが、Codex review lifecycle の `completion_signal` が `none` のまま `wait_pr_observation.sh` が `wait_timeout` になった。
- Earlier head `66c6a3be` では `submitted_pull_request_review` を検出できていたため、問題は PR review endpoint 未取得ではなく、Codex が PR review object を投稿しない完了形態を表現できない completion signal contract gap と扱う。
- この追加計画は、既存 S01-S99 の Actions-primary CI 実装を裏書き・やり直しするものではない。PR observation の追加発見に対する後続修正として、既存実装計画の末尾に追加する。

### 追加ステップ一覧
- S100:
  - 観測可能な振る舞い: CI passed / head matched / no selected current blockers / no trusted completion signal の安定状態を `review_completion_unknown` として表現し、generic timeout に潰さない。
  - 依存: S99 までの Actions-primary CI behavior and PR #190 observation evidence.
  - unblock: S101, S190, S199
  - 対象ファイル: `fetch_pr_review_snapshot.sh`, `tests/unit/infra/test_init_update.py`
  - レビューゲート: code-reviewer pass
- S101:
  - 観測可能な振る舞い: snapshot / wait wrappers が `review_completion_unknown` を terminal-like non-pass state として扱い、blind wait/resume を続けない。
  - 依存: S100
  - unblock: S190, S199
  - 対象ファイル: `fetch_pr_observation_snapshot.sh`, `wait_pr_observation.sh`, `tests/unit/infra/test_init_update.py`
  - レビューゲート: code-reviewer pass
- S102:
  - 観測可能な振る舞い: current-boundary allowlisted no-findings issue comment が実際に観測可能な場合だけ、distinct secondary signal として扱う。
  - 依存: S100
  - unblock: S190, S199
  - 対象ファイル: `fetch_pr_review_snapshot.sh`, `tests/unit/infra/test_init_update.py`
  - レビューゲート: code-reviewer pass
  - note: 実際の GitHub artifact shape が不明または不十分なら approved-no-op / deferred とし、`fallback_issue_comment` の意味は変更しない。
- S190:
  - 観測可能な振る舞い: provider docs and dogfooding mirror reflect the review completion contract.
  - 依存: S100-S102
  - 対象ファイル: provider `SKILL.md` if needed, `.agents/skills/github-pr-observation/` mirror files
  - レビューゲート: spec-reviewer for docs, code-reviewer for mirror script sync
- S199:
  - 観測可能な振る舞い:追加修正全体の tests, reviewer gates, report evidence, and PR observation re-run readiness are complete.
  - 依存: S100-S101, S102 if implemented, S190
  - レビューゲート: qa-reviewer, code-reviewer, spec-reviewer pass

### 追加クロージャ索引

| 識別子（ID） | ステップ | スライス | 種別 | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 |
|---|---|---|---|---|---|---|---|
| tc-s100-001 | S100 | review-no-completion-evidence | acceptance | Current-boundary no-completion evidence remains machine-readable and distinguishable from blockers/pending signals | review collector has no selected reviews/comments/threads, no pending request, no blocking collection failure | wrapper cannot later classify stable unknown safely | yes |
| tc-s100-002 | S100 | no-false-pass | negative | no-completion evidence is not `passed` and not `merge_prepared` at collector/snapshot level | same as tc-s100-001 | no-signal false pass | yes |
| tc-s100-003 | S100 | pending-review-preserved | negative | pending review request / pending current review signal remains pending and is not eligible for unknown promotion | current review request or pending PR review exists | premature unknown terminal state | yes |
| tc-s101-001 | S101 | snapshot-review-unknown | integration | Combined snapshot preserves no-completion evidence as pending/non-pass before wait stability | CI passed, head matched, review collector has no completion signal | single-poll snapshot prematurely stops review wait | yes |
| tc-s101-002 | S101 | wait-review-unknown | integration | Wait exits with `review_completion_unknown` instead of generic `wait_timeout` only after quiet/same-fingerprint stability | stable fingerprint with no-completion evidence, CI passed, head matched | wasted wait/resume loop or premature unknown | yes |
| tc-s101-003 | S101 | existing-missing-signal | regression | Truly missing/unstable completion signal still waits and may timeout | review collector says pending or missing before stability condition | review running treated as done | yes |
| tc-s102-001 | S102 | no-findings-comment | optional acceptance | Strict current-boundary Codex no-findings issue comment can produce distinct secondary signal if adopted | allowlisted body, Codex-authored, after trigger, no blockers | no-review no-findings remains unobservable when explicit evidence exists | optional |
| tc-s102-002 | S102 | fallback-preserved | negative | Generic `fallback_issue_comment` remains low-confidence human gate | current Codex comment with non-allowlisted body | generic comment false pass | yes if S102 implemented |
| tc-s102-003 | S102 | blockers-win | negative | current unresolved threads / changes-requested evidence override no-findings signal | no-findings comment plus selected blocker | blocker masked by positive comment | yes if S102 implemented |
| tc-s102-004 | S102 | boundary-safety | negative | old trigger / non-Codex / ambiguous no-findings artifacts do not complete | stale or ambiguous comment/reaction | stale-boundary false pass | yes if S102 implemented |
| tc-s190-001 | S190 | docs-mirror | docs/scaffold | Provider docs/mirror describe review completion unknown and optional secondary signal semantics | changed provider/mirror files | operator or dogfooding drift | yes |
| tc-s199-001 | S199 | final-validation | quality | focused tests, mirror checks, validation, and reviewer gates pass or are explicitly explained | final addendum diff | incomplete closure | yes |

### 実装ステップ S100 — Review no-completion evidence contract
- 振る舞いの目標:
  - `fetch_pr_review_snapshot.sh` が current-boundary の no-completion evidence を blockers / pending / explicit completion と区別できる形で出力する。
- design 参照:
  - `design.md` Review completion output JSON / Review completion semantics.
- 依存:
  - Existing Actions-primary CI implementation and PR #190 observation evidence.
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - scope:
    - Preserve or add collector evidence after selected blockers, changes-requested evidence, explicit completion signals, pending review request/current pending review signal, and blocking collection failure.
    - Keep no-completion evidence non-pass at this layer: `completion_signal="none"` and `decision.status_reason` remains `missing_current_completion_signal` or a clearly non-terminal candidate reason.
    - Do not emit terminal-like `review_completion_unknown` from the collector alone because the collector lacks CI/head and elapsed stability context.
    - Preserve existing `submitted_pull_request_review`, `fallback_issue_comment`, selected unresolved thread, selected changes-requested, and blocking collection failure semantics.
  - テスト義務:
    - `tc-s100-001`, `tc-s100-002`, `tc-s100-003`
  - Green 検証:
    - `uv run pytest tests/unit/infra/test_init_update.py -k "review_completion_unknown or missing_current_completion_signal or fallback_issue_comment"`
  - amendment trigger:
    - If current collector already exposes all needed no-completion evidence without code changes, close S100 as approved-no-op with tests/inspection evidence and keep S101 responsible for stable promotion.

#### 委任契約（S100）
- delegated role:
  - dev-coder
- allowed paths:
  - provider review collector and focused tests, or tests/inspection only for approved-no-op.
- forbidden changes:
  - no CI collector behavior changes.
  - no generic issue comment promotion.
  - no merge automation.
- reviewer focus:
  - code-reviewer: false-pass safety, ordering of blocker/pending branches, preservation of existing completion signals, and machine-readable no-completion evidence.
- report evidence destination:
  - `report.md` Evidence Adoption Ledger, TDD Evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate.

### 実装ステップ S101 — Snapshot / wait handling for review completion unknown
- 振る舞いの目標:
  - Wait output promotes stable no-completion evidence to `review_completion_unknown` as non-pass terminal-like state and does not overwrite it with generic `wait_timeout`.
- design 参照:
  - `design.md` Sequence Delta / Review completion semantics.
- 依存:
  - S100
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - scope:
    - Snapshot keeps no-completion evidence pending/non-pass before wait stability.
    - Wait promotes no-completion evidence to `review_completion_unknown` only when all stability gates are met: CI `passed`, head matched, no current selected blockers, no pending review request/current pending review signal, semantic fingerprint observed for configured same-fingerprint count, and quiet window elapsed.
    - Promoted `review_completion_unknown` uses `recommended_next_action="human_gate"` and must not be `passed` / `merge_prepared`.
    - Existing pending/missing signal behavior remains for actually in-progress review states.
  - テスト義務:
    - `tc-s101-001`, `tc-s101-002`, `tc-s101-003`
  - Green 検証:
    - `uv run pytest tests/unit/infra/test_init_update.py -k "review_completion_unknown or pr_observation_wait or issue_182"`
  - open decision:
    - Top-level `normalized_status` should be `human_gate` unless a reviewer requires `unknown`; `human_gate` is the recommended inspect-before-merge state.

#### 委任契約（S101）
- delegated role:
  - dev-coder
- allowed paths:
  - snapshot/wait scripts and focused tests.
- forbidden changes:
  - no raw comment body parsing in wrappers.
  - no change to `submitted_pull_request_review` pass behavior.
  - no PR merge automation.
- reviewer focus:
  - code-reviewer: no blind wait loop, no pass without completion signal, stable output fields, timeout overwrite prevention.
- report evidence destination:
  - `report.md` TDD Evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate.

### 実装ステップ S102 — Optional explicit no-findings secondary signal
- 振る舞いの目標:
  - If observable, strict current-boundary no-findings issue comment can become a distinct secondary completion signal without weakening `fallback_issue_comment`.
- design 参照:
  - `design.md` Optional future secondary signal.
- 依存:
  - S100
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - scope:
    - Determine whether current GitHub data provides a Codex-authored allowlisted no-findings issue comment or another explicit artifact.
    - If implemented, introduce a distinct signal such as `codex_no_findings_issue_comment`.
    - Keep generic `fallback_issue_comment` low-confidence and non-promoting.
  - テスト義務:
    - `tc-s102-001`..`tc-s102-004` if implemented.
  - Green 検証:
    - `uv run pytest tests/unit/infra/test_init_update.py -k "no_findings or fallback_issue_comment or completion_signal"`
  - approved no-op / defer condition:
    - If no reliable actor/time/trigger-boundary evidence exists, record S102 as deferred and do not implement a secondary signal.

#### 委任契約（S102）
- delegated role:
  - dev-coder
- allowed paths:
  - review collector and focused tests.
- forbidden changes:
  - do not promote all Codex issue comments.
  - do not rely on review request disappearance alone.
  - do not use selected-comments-zero as completion.
- reviewer focus:
  - code-reviewer: strict body allowlist, actor identity, trigger boundary, selected blocker precedence, and preserved fallback semantics.
- report evidence destination:
  - `report.md` Decision Ledger, Discovered Tests, Step Contract Closure, Test Contract Closure, Reviewer Gate Status.

### ドキュメント / ミラー追加ステップ S190
- 振る舞いの目標:
  - Provider docs and dogfooding mirror make the review completion contract visible to operators and future agents.
- 依存:
  - S100-S101 and S102 if implemented.
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md` if operator behavior changes.
  - `.agents/skills/github-pr-observation/` mirror files corresponding to changed provider files.
- 対応:
  - Document `review_completion_unknown` as a non-pass terminal-like state.
  - Document that `fallback_issue_comment` remains low-confidence unless a distinct no-findings signal is adopted.
  - Sync changed provider scripts/docs to dogfooding mirror and verify intended equality.
- verification:
  - provider/mirror `cmp` or diff for changed files.
  - `git diff --check`.
- reviewer:
  - spec-reviewer for docs wording.
  - code-reviewer for script mirror sync.

### 追加最終品質ゲート S199
- branch diff 範囲:
  - Review collector, snapshot/wait wrappers, focused tests, provider/mirror docs/scripts, report evidence.
- 必須 validation:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "review_completion_unknown or completion_signal or fallback_issue_comment or missing_current_completion_signal or issue_182 or issue_176"`
  - `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation or issue_187"`
  - `git diff --check`
  - `./spec-dock/scripts/spec-dock validate`
- reviewer gates:
  - code-reviewer: integrated runtime/test diff pass.
  - qa-reviewer: no false-pass / no wasted-wait coverage pass.
  - spec-reviewer: canonical docs, discussion evidence, plan addendum, and report evidence alignment pass.
- PR observation gate:
  - Re-run PR observation against the latest PR head SHA after push. Do not reuse older head observations as current completion evidence.
- commit gate:
  - Commit S100, S101, S102 if implemented, S190, and S199 evidence as separate step commits when feasible.

### 追加計画の未確定事項
- Blocking before execution:
  - None if S100/S101 are limited to non-pass `review_completion_unknown`.
- Non-blocking:
  - Whether top-level `review_completion_unknown` normalizes to `human_gate` or `unknown`; recommended default is `human_gate`.
  - Whether an allowlisted no-findings issue comment is actually observable for the no-PR-review completion form; if not, S102 should be deferred.
  - Whether the post-observation review completion work remains in `iss-00187` or should later be split to a follow-up issue. This plan records it as an appended addendum because the user requested追加修正 in the existing plan.

## 追加実装計画（S200+ / PR #190 P1 Review and Script Boundary Addendum）

### 追加の背景
- PR #190 latest head `1bb19acdf512d71f45a39ce7a3790862b36b0295` に対して、current Codex review が P1 unresolved thread 2件を返した。
- 1件目は `fetch_pr_checks_snapshot.sh` が workflow run ごとに jobs API を呼び、bounded wait snapshot の時間予算を消費し得る問題である。
- 2件目は Actions runs が 0 件の repo で external checks / commit statuses が green でも `ci.status="none"` に落ちる問題である。
- S101 で追加した `review_completion_unknown` は non-pass ではあるが、Codex review が通常遅延で後から投稿される前に早く確定する可能性がある。
- これらの修正は、既存 S01-S199 の実施済み計画をやり直すものではない。追加発見に対する S200+ の後続レーンとして末尾に追加する。

### 追加ステップ一覧
- S200:
  - 観測可能な振る舞い: S200+ lane の canonical plan adoption と report evidence が記録され、fresh spec-reviewer gate の対象になる。
  - 依存: S199, discussions `05`..`09`
  - 対象ファイル: `design.md`, `plan.md`, `report.md`
  - レビューゲート: spec-reviewer pass
- S201:
  - 観測可能な振る舞い: `fetch_pr_checks_snapshot.sh` の公開 CLI / stdout JSON contract を維持したまま、Python 本体を `pr_observation_checks.py` へ切り出す。
  - 依存: S200
  - unblock: S202, S203
  - 対象ファイル: provider `fetch_pr_checks_snapshot.sh`, new provider `pr_observation_checks.py`, `tests/unit/infra/test_init_update.py`
  - レビューゲート: code-reviewer pass
- S202:
  - 観測可能な振る舞い: zero Actions runs でも readable green external checks/statuses があれば `ci.status="passed"` になり、外部CI-only repo を false-negative にしない。
  - 依存: S201
  - unblock: S203
  - 対象ファイル: `pr_observation_checks.py`, `tests/unit/infra/test_init_update.py`
  - レビューゲート: code-reviewer pass
- S203:
  - 観測可能な振る舞い: default / wait snapshot は successful Actions run 全件の jobs API expansion に依存せず、failed / non-terminal / unknown diagnostics は保持する。
  - 依存: S201, S202
  - unblock: S204
  - 対象ファイル: `pr_observation_checks.py`, `tests/unit/infra/test_init_update.py`
  - レビューゲート: code-reviewer pass
- S204:
  - 観測可能な振る舞い: `review_completion_unknown` は quiet / same-fingerprint だけでは昇格せず、trigger age と CI-passed age の最小猶予を満たしてから non-pass human gate になる。
  - 依存: S100, S101, S203
  - unblock: S290
  - 対象ファイル: `wait_pr_observation.sh`, `tests/unit/infra/test_init_update.py`
  - レビューゲート: code-reviewer pass
- S290:
  - 観測可能な振る舞い: provider docs and dogfooding mirror reflect extracted Python asset, bounded Actions collection, external green fallback, and delayed `review_completion_unknown`.
  - 依存: S201-S204
  - 対象ファイル: provider/mirror `SKILL.md`, mirror `fetch_pr_checks_snapshot.sh`, mirror `pr_observation_checks.py`, mirror `wait_pr_observation.sh`
  - レビューゲート: spec-reviewer for docs, code-reviewer for mirror/scaffold sync
- S299:
  - 観測可能な振る舞い: S200+ lane の focused / broad tests、provider/mirror checks、SpecDock validation、reviewer gates、PR #190 re-observation が完了する。
  - 依存: S201-S204, S290
  - 対象ファイル: issue-wide diff and `report.md`
  - レビューゲート: qa-reviewer, code-reviewer, spec-reviewer pass

### 追加クロージャ索引 S200+

| 識別子（ID） | ステップ | スライス | 種別 | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 |
|---|---|---|---|---|---|---|---|
| tc-s201-001 | S201 | extraction-preservation | characterization | Existing checks collector JSON shape and exit behavior remain compatible after Python extraction | fake `gh` checks collector scenarios | wrapper/extraction behavior drift | yes |
| tc-s201-002 | S201 | wrapper-validation | negative | invalid repo / PR / SHA are rejected before `gh` is called | invalid CLI args with fake `gh` call log | unsafe caller input reaches GitHub API | yes |
| tc-s201-003 | S201/S290 | scaffold-asset | scaffold | `pr_observation_checks.py` is shipped by init/update asset surface | temp target init/update or asset inspection | installed wrapper cannot find Python entrypoint | yes |
| tc-s202-001 | S202 | zero-actions-check-runs-green | acceptance | zero Actions runs plus green check-runs can produce `ci.status="passed"` | Actions total 0; check-runs success | external-CI-only false-negative | yes |
| tc-s202-002 | S202 | zero-actions-statuses-green | acceptance | zero Actions runs plus green commit statuses can produce `ci.status="passed"` | Actions total 0; statuses success | status-only CI false-negative | yes |
| tc-s202-003 | S202 | zero-actions-zero-external | negative | zero Actions runs plus zero external evidence remains non-pass | Actions/check/status total 0 | no-CI false pass | yes |
| tc-s202-004 | S202 | zero-actions-external-non-green | negative | external pending/failure still wins over zero-Actions fallback | Actions total 0; check/status pending or failed | blocker masked by fallback | yes |
| tc-s203-001 | S203 | bounded-green-job-expansion | performance/regression | multiple green workflow runs do not force jobs API call for every run | fake `gh` call log with multiple green runs | wait budget exhaustion / rate pressure | yes |
| tc-s203-002 | S203 | failed-diagnostics-preserved | acceptance | failed Actions still emits sanitized job/step failure evidence | failed run/job/step payload | loss of repair evidence | yes |
| tc-s203-003 | S203 | expansion-cap-limitation | negative | cap/skip is explicit and non-secret when diagnostics are bounded | more diagnostic-relevant runs than cap | silent evidence omission / unbounded calls | yes if cap path exists |
| tc-s203-004 | S203 | failure-dedupe | regression | Actions/check-run duplicated failure evidence remains deduplicated | overlapping failed run/job evidence | duplicate/noisy failures | yes |
| tc-s204-001 | S204 | no-premature-unknown-trigger-age | negative | below trigger-age threshold, stable no-completion does not become `review_completion_unknown` | CI passed/head matched/recent trigger/no completion | review unknown races ahead of Codex review | yes |
| tc-s204-002 | S204 | no-premature-unknown-ci-age | negative | below CI-passed-age threshold, stable no-completion still waits/resumes | trigger old enough; CI just became passed | CI pass instant terminalizes review unknown | yes |
| tc-s204-003 | S204 | delayed-review-unknown | acceptance | beyond both thresholds, stable no-completion becomes human-gate `review_completion_unknown` | old trigger, CI passed long enough, stable fingerprint | loss of S101 no-completion escape hatch | yes |
| tc-s204-004 | S204 | late-review-wins | regression | late submitted Codex review with unresolved threads overrides no-completion state | sequence no-completion then submitted review | actionable review lost behind unknown | yes |
| tc-s290-001 | S290 | docs | docs | SKILL docs describe bounded Actions collection, external fallback, delayed review unknown | provider/mirror docs inspection | operator misinformation | yes |
| tc-s290-002 | S290 | mirror | scaffold | provider and dogfooding mirror changed files match where intended | `cmp -s` for changed files | dogfooding stale behavior | yes |
| tc-s290-003 | S290 | installed-asset | scaffold | new Python asset is installed/updated with wrapper | init/update asset test | broken shipped wrapper | yes |
| tc-s299-001 | S299 | final-validation | quality | focused/broad tests, validation, reviews, and PR observation evidence close S200+ lane | final issue-wide diff | incomplete closure | yes |

### 実装ステップ S200 — S200+ canonical adoption gate
- 振る舞いの目標:
  - discussions `20260616t025000z-05` through `20260616t031000z-09` の採用判断を canonical `design.md` / `plan.md` / `report.md` に反映し、実装前に fresh spec-reviewer gate を通す。
- 対象ファイル:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
- 計画済み契約:
  - 既存 S01-S199 の実施済み計画は書き換えず、S200+ を末尾に追加する。
  - `design.md` は Python extraction / P1 fixes / timing guard を統合設計として反映する。
  - `report.md` に decision / Evidence Adoption Ledger / Delegated Draft Evidence を記録する。
- review:
  - spec-reviewer pass required before S201.
- report evidence destination:
  - Spec Authoring Gate, Evidence Adoption Ledger, Delegated Draft Evidence, Reviewer Gate Status.

### S200+ 共通実行契約
- 適用範囲:
  - S201, S202, S203, S204, S290, S299.
- orchestration:
  - Parent orchestrator executes exactly one step at a time.
  - Do not start the next step until the current step has: required Red or approved alternative evidence, Green verification, fresh step reviewer pass, report evidence, step commit, and post-commit clean check.
  - Runtime/test/scaffold behavior changes must be delegated to `dev-coder`.
  - Shipped docs / skill text changes must be delegated to `doc-writer`.
  - Mechanical mirror sync may be delegated to `utility-worker` or `dev-coder`, but reviewer gate remains parent-owned.
- required worker output:
  - changed files list.
  - Red evidence or explicit approved-no-op / characterization-only rationale.
  - Green command output summary.
  - scope boundaries observed.
  - Ledger Note, or `No material implementation decisions beyond the approved plan.`
- common forbidden changes:
  - no arbitrary GitHub API proxy.
  - no raw token / raw auth stderr output.
  - no merge-ready / passed promotion from review no-completion evidence.
  - no selected-count-only completion inference.
  - no unrelated refactor outside the step target files.
  - no edits to completed S01-S199 evidence except report rows required to integrate S200+.
- stop conditions:
  - If S201 reveals the new Python asset is not shipped by init/update, stop S201 and fix asset inclusion before any S202 behavior change.
  - If S202 reveals requirement/design conflict around external-CI pass semantics, return to design/plan authoring before code changes.
  - If S203 cannot preserve failed diagnostics while bounding green expansion, stop for design amendment; do not silently drop failure evidence.
  - If S204 requires broad review/wait extraction beyond timing guard, stop for design/plan amendment unless a reviewer explicitly accepts a narrow heredoc change.
  - Any reviewer `fail` blocks commit for that step until bounded follow-up and fresh pass.
- common report evidence destination:
  - `report.md` TDD Evidence, Discovered Tests / Risk, Test Contract Closure, Closure Coverage, Closure Delta if IDs change, Reviewer Gate Status, Step Commit Gate.

### 実装ステップ S201 — Extract checks collector Python
- 振る舞いの目標:
  - Shell wrapper は fixed public CLI の互換レイヤーに戻し、Python collector 本体を `pr_observation_checks.py` へ移す。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - No CI classification behavior change in S201.
  - Wrapper validation and stdout JSON contract are preserved.
  - Python entrypoint uses only standard library and existing `gh` invocation semantics.
  - Installer/update must ship the new `.py` asset.
- 委任契約:
  - delegated role: `dev-coder`
  - allowed paths:
    - provider `fetch_pr_checks_snapshot.sh`
    - provider `pr_observation_checks.py`
    - focused tests in `tests/unit/infra/test_init_update.py`
    - minimal report rows for S201 evidence if the worker is explicitly asked to update report; otherwise parent records report evidence.
  - forbidden changes:
    - no CI status taxonomy change.
    - no wait/review script changes.
    - no dogfooding mirror sync in S201 unless the parent explicitly scopes it into the step; mirror sync normally waits for S290.
    - no new third-party dependency.
- テスト義務:
  - `tc-s201-001`, `tc-s201-002`, `tc-s201-003`
- Red / alternative evidence:
  - `tc-s201-003` should fail or be absent before the new Python asset is added; if existing asset tests already cover copied files generically, record characterization evidence instead.
  - Existing focused collector tests serve as before/after behavior-preservation evidence.
- Green 検証:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187 and actions"`
  - focused wrapper validation / asset presence tests
  - `git diff --check`
- reviewer:
  - code-reviewer pass focused on shell/Python boundary, fixed API surface, secret redaction, stdout/stderr behavior.
- commit gate:
  - S201 commit after reviewer pass and clean check.
- report evidence destination:
  - TDD Evidence for extraction/asset test behavior, Test Contract Closure for `tc-s201-001`..`tc-s201-003`, Closure Coverage, Reviewer Gate Status, Step Commit Gate.

### 実装ステップ S202 — Zero Actions runs with external green evidence
- 振る舞いの目標:
  - Actions runs が 0 件でも external check-runs / commit statuses が green なら CI passed として扱える。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - Zero Actions runs alone is still non-pass.
  - External failure/pending/required missing evidence still wins.
  - No wait/review behavior changes in this step.
- 委任契約:
  - delegated role: `dev-coder`
  - allowed paths:
    - provider `pr_observation_checks.py`
    - focused tests in `tests/unit/infra/test_init_update.py`
    - parent-owned report evidence unless explicitly delegated.
  - forbidden changes:
    - no shell wrapper restructuring beyond S201 output.
    - no wait/review script changes.
    - no pass when Actions/check-runs/statuses/rollup provide no evidence.
- テスト義務:
  - `tc-s202-001`..`tc-s202-004`
- Red / alternative evidence:
  - `tc-s202-001` and `tc-s202-002` must fail or be shown absent before implementation.
  - `tc-s202-003` preserves existing zero-evidence non-pass behavior.
- Green 検証:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "zero_actions or external or issue_187"`
  - `git diff --check`
- reviewer:
  - code-reviewer pass focused on false-pass safety and external-CI compatibility.
- commit gate:
  - S202 commit after reviewer pass.
- report evidence destination:
  - TDD Evidence, Test Contract Closure for `tc-s202-001`..`tc-s202-004`, Closure Coverage, Reviewer Gate Status, Step Commit Gate.

### 実装ステップ S203 — Bound Actions jobs collection
- 振る舞いの目標:
  - Successful Actions runs 全件に対する jobs API expansion を避け、wait snapshot の bounded behavior を守る。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - Failed / running / pending / unknown run diagnostics are preserved or explicitly limited with sanitized limitation.
  - Terminal green run jobs are skipped or capped by documented internal policy.
  - Existing `ci.actions.jobs[]`, `jobs_detail[]`, and `jobs_summary` compatibility is preserved additively.
- 委任契約:
  - delegated role: `dev-coder`
  - allowed paths:
    - provider `pr_observation_checks.py`
    - focused tests in `tests/unit/infra/test_init_update.py`
    - parent-owned report evidence unless explicitly delegated.
  - forbidden changes:
    - no external-green status ladder regression from S202.
    - no loss of failed job/step evidence when jobs are readable.
    - no public `--mode` flag unless design is amended.
    - no raw API stderr/token exposure in new limitations.
- テスト義務:
  - `tc-s203-001`..`tc-s203-004`
- Red / alternative evidence:
  - `tc-s203-001` must fail on unbounded current behavior or be represented by a call-log characterization proving current unbounded calls.
  - `tc-s203-002` and `tc-s203-004` may be covered by existing tests if the worker maps them explicitly.
  - `tc-s203-003` is required only if a cap path is implemented; if green runs are skipped without cap, record no-op rationale for the cap-specific path.
- Green 検証:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "jobs_summary or jobs_detail or actions_job or issue_187"`
  - `git diff --check`
- reviewer:
  - code-reviewer pass focused on wait-budget impact, failure diagnostics, and API call bounding.
- commit gate:
  - S203 commit after reviewer pass.
- report evidence destination:
  - TDD Evidence, Discovered Tests / Risk for any cap-vs-skip decision, Test Contract Closure for `tc-s203-001`..`tc-s203-004`, Closure Coverage, Reviewer Gate Status, Step Commit Gate.

### 実装ステップ S204 — Review completion unknown timing hardening
- 振る舞いの目標:
  - `review_completion_unknown` promotion に trigger age / CI-passed age の latency guard を追加し、Codex review 到着前の premature unknown を防ぐ。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - 推奨初期定数:
    - `review_completion_unknown_min_trigger_age_seconds = 300`
    - `review_completion_unknown_min_ci_passed_age_seconds = 90`
  - Promotion requires CI passed, head matched, no selected blocker, no pending review signal, no blocking collection failure, same-fingerprint stability, quiet window, and both age thresholds.
  - Threshold 未満では `review_completion_unknown` にしない。
  - Submitted review / unresolved thread が後から来た場合は `address_review_feedback` が勝つ。
- 委任契約:
  - delegated role: `dev-coder`
  - allowed paths:
    - provider `wait_pr_observation.sh`
    - focused tests in `tests/unit/infra/test_init_update.py`
    - parent-owned report evidence unless explicitly delegated.
  - forbidden changes:
    - no review collector semantic broadening.
    - no no-findings secondary signal.
    - no `passed` / `merge_prepared` from missing completion.
    - no full wait/review Python extraction unless returned as a plan gap.
- テスト義務:
  - `tc-s204-001`..`tc-s204-004`
- Red / alternative evidence:
  - `tc-s204-001` or `tc-s204-002` must fail on current S101 timing behavior, or worker must provide a source-grounded explanation if current behavior already contains equivalent timing gates.
  - `tc-s204-003` updates the existing S101 stable unknown test to use aged trigger/CI evidence.
  - `tc-s204-004` requires sequence coverage for late review override.
- Green 検証:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "review_completion_unknown or issue_187_s101 or wait_review"`
  - `git diff --check`
- reviewer:
  - code-reviewer pass focused on timing semantics, non-pass safety, and timeout overwrite behavior.
- commit gate:
  - S204 commit after reviewer pass.
- report evidence destination:
  - TDD Evidence, Test Contract Closure for `tc-s204-001`..`tc-s204-004`, Closure Coverage, Reviewer Gate Status, Step Commit Gate.

### ドキュメント / ミラー追加ステップ S290
- 振る舞いの目標:
  - Provider docs, mirror scripts, mirror docs, and installed asset behavior align with S201-S204.
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - `.agents/skills/github-pr-observation/SKILL.md`
  - `.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
  - `.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - any provider/mirror script files changed by S201-S204.
- 計画済み契約:
  - Docs describe external green fallback, bounded Actions job expansion, and delayed `review_completion_unknown`.
  - Provider/mirror changed files are byte-identical where intended.
  - New Python asset is present in scaffold/update output.
- 委任契約:
  - delegated roles:
    - `doc-writer` for provider/mirror `SKILL.md`.
    - `utility-worker` or `dev-coder` for mechanical mirror sync and scaffold asset verification.
  - allowed paths:
    - provider/mirror `SKILL.md`
    - mirror script files corresponding to S201-S204 provider changes
    - focused asset tests if not already added in S201
    - parent-owned report evidence unless explicitly delegated.
  - forbidden changes:
    - no new behavior changes in provider scripts except mechanical mirror sync.
    - no modification of S201-S204 logic while doing docs/mirror sync.
    - no claim that PR #190 is merge-ready.
- verification:
  - provider/mirror `cmp -s`
  - focused init/update asset test
  - `git diff --check`
- reviewer:
  - spec-reviewer for docs wording.
  - code-reviewer for mirror/scaffold sync.
- commit gate:
  - S290 commit after reviewer pass.
- report evidence destination:
  - Docs Impact Resolution, Test Contract Closure for `tc-s290-001`..`tc-s290-003`, Closure Coverage, Reviewer Gate Status, Step Commit Gate.

### 追加最終品質ゲート S299
- branch diff 範囲:
  - S201-S204 behavior changes, S290 docs/mirror/scaffold changes, and final `report.md` evidence.
- 必須 validation:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187 or pr_observation or actions or review_completion_unknown"`
  - `uv run pytest tests/unit/infra/test_init_update.py -q`
  - `git diff --check`
  - `./spec-dock/scripts/spec-dock validate`
  - provider/mirror `cmp -s` for changed assets
- PR observation gate:
  - Re-run PR observation on latest PR #190 head after push.
  - Record whether previous selected unresolved P1 threads are resolved, superseded, or still blocking.
  - Do not claim merge readiness while P1 threads remain unresolved.
- 委任契約:
  - delegated roles:
    - qa-reviewer for final test sufficiency.
    - code-reviewer for integrated runtime/test/docs diff.
    - spec-reviewer for final spec alignment.
  - parent-owned work:
    - final report evidence integration.
    - PR observation orchestration.
    - commit gate and PR delivery handoff.
  - forbidden changes:
    - no behavior changes unless a final reviewer finding requires a bounded follow-up assigned to the relevant previous step or an explicit S299 follow-up.
    - no final commit before all required reviewers pass.
- reviewer gates:
  - qa-reviewer: test sufficiency and race coverage pass.
  - code-reviewer: integrated scripts/tests/docs diff pass.
  - spec-reviewer: requirement/design/plan/report alignment pass.
- commit gate:
  - S299 final evidence commit only after reviewers pass.
  - Do not bundle uncommitted S201-S204 behavior changes into S299.
- report evidence destination:
  - Final QA Gate, Final Code Review Gate, Final Spec Review Gate, Closure Coverage, Step Commit Gate, Final Commit, PR Observation Gate.

### 追加計画の未確定事項
- Blocking before S201:
  - S200 canonical adoption and fresh spec-reviewer pass.
- Non-blocking:
  - Exact timing constants may be adjusted by reviewer feedback.
  - Whether green-run job expansion is skipped entirely or capped with a small diagnostic sample is implementation-local, as long as bounded behavior and failure diagnostics are preserved.
  - Full extraction of review/wait scripts was left as a future follow-up at S200+ closure time. S300+ below adopts the snapshot/wait portion of that follow-up while leaving review collector / trigger extraction outside the direct scope.

## 追加実装計画 S300+ — Snapshot / Wait Python Entrypoint Extraction

### 追加計画の位置づけ
- この追加計画は、既存 S01-S299 の実施済み計画を裏書き・修正・再判定するものではない。
- `discussions/20260616t072719z-10-disc-snapshot-wait-python-extraction-architecture-draft.md` と `discussions/20260616t072719z-11-disc-snapshot-wait-python-extraction-implementation-plan-draft.md` を canonical docs へ採用した follow-up lane として扱う。
- 目的は、`fetch_pr_observation_snapshot.sh` と `wait_pr_observation.sh` に残る Python heredoc を standalone Python entrypoint へ抽出し、shell wrapper を public CLI / validation / Python invocation に薄くすること。
- Direct target は snapshot / wait に限定する。`fetch_pr_review_snapshot.sh` と `trigger_codex_review.sh` の heredoc は別 follow-up 対象とし、S300+ の直接 scope には含めない。

### S300+ 依存順序
```text
S300
  -> S310
      -> S320
          -> S390
              -> S399
```

### 追加クロージャ索引 S300+

| 識別子（ID） | ステップ | スライス | 種別 | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 |
|---|---|---|---|---|---|---|---|
| `tc-s300-001` | S300 | heredoc-inventory | characterization | Remaining snapshot/wait heredoc responsibilities and tests are mapped before extraction | provider snapshot/wait scripts and focused test inventory | extraction proceeds without behavior baseline | yes |
| `tc-s300-002` | S300 | focused-test-map | characterization | Existing snapshot/wait focused tests are identified for before/after evidence | `tests/unit/infra/test_init_update.py` PR observation tests | false confidence from broad tests only | yes |
| `tc-s310-001` | S310 | snapshot-cli | regression | `fetch_pr_observation_snapshot.sh` public CLI and fixed command surface remain compatible | fake `gh` snapshot scenarios | shell/Python extraction breaks callers | yes |
| `tc-s310-002` | S310 | snapshot-validation | negative | invalid snapshot args are rejected before `gh` / collectors are called | invalid CLI args with fake call log | unsafe input reaches GitHub/API scripts | yes |
| `tc-s310-003` | S310 | snapshot-artifacts | regression | snapshot stdout JSON and `--out` artifacts remain compatible | snapshot command with `--out` | artifact consumers break after extraction | yes |
| `tc-s310-004` | S310 | snapshot-head-freshness | regression | initial/final head revalidation and `stale_head` behavior are preserved | head changes during snapshot collection | stale PR head is misreported as current | yes |
| `tc-s310-005` | S310 | snapshot-failure-json | negative | metadata/collector failures still produce secret-redacted limitation JSON | failing fixed `gh` / collector output | raw stderr leaks or failure becomes pass | yes |
| `tc-s310-006` | S310/S390 | snapshot-python-asset | scaffold | `pr_observation_snapshot.py` is installed/updated with shipped assets | init/update target tree | installed wrapper cannot find Python entrypoint | yes |
| `tc-s320-001` | S320 | wait-cli | regression | `wait_pr_observation.sh` public CLI validation remains compatible | invalid and valid wait args | wait callers break after extraction | yes |
| `tc-s320-002` | S320 | wait-stdout-stderr-out | regression | wait stdout final JSON, stderr progress, and `--out` contract are preserved | fake snapshot/trigger wait run | progress/artifact consumers break | yes |
| `tc-s320-003` | S320 | wait-stability | regression | quiet / same-fingerprint gate behavior is preserved | stable and changing snapshot sequence | terminal state occurs too early or never | yes |
| `tc-s320-004` | S320 | wait-timeout | regression | timeout preserves latest payload and wait metadata | snapshot sequence through timeout | resume evidence is lost | yes |
| `tc-s320-005` | S320 | review-unknown-latency | regression | S204 `review_completion_unknown` trigger-age and CI-age timing remains preserved | aged and non-aged no-completion evidence | premature human gate or lost unknown escape hatch | yes |
| `tc-s320-006` | S320 | late-review-overrides | regression | late submitted/unresolved review overrides unknown candidate | no-completion then current review finding | actionable feedback hidden by unknown | yes |
| `tc-s320-007` | S320/S390 | wait-python-asset | scaffold | `pr_observation_wait.py` is installed/updated with shipped assets | init/update target tree | installed wrapper cannot find wait Python entrypoint | yes |
| `tc-s390-001` | S390 | mirror-sync | scaffold | provider/mirror changed snapshot/wait files match where intended | provider/mirror `cmp -s` | dogfooding mirror executes stale logic | yes |
| `tc-s390-002` | S390 | operator-docs | docs | provider/mirror docs describe standalone snapshot/wait Python entrypoints | `SKILL.md` inspection | operator documentation contradicts shipped behavior | yes |
| `tc-s399-001` | S399 | final-validation | quality | S300+ focused/broad validation, reviewers, and latest PR evidence are complete | final branch diff and PR #190 observation | incomplete extraction closure | yes |

### S300+ 共通実行契約
- Parent orchestrator executes exactly one step at a time.
- Runtime/test/scaffold changes must be delegated to `dev-coder`.
- Shipped docs / skill text changes must be delegated to `doc-writer`.
- Mirror-only mechanical sync may be delegated to `utility-worker` or `dev-coder`.
- Each implementation step must close with required evidence, fresh reviewer pass, step commit, and post-commit clean check before the next step starts.
- Forbidden across S300+:
  - no public shell flag change without design amendment.
  - no arbitrary GitHub API proxy.
  - no raw token / raw auth stderr output.
  - no `review_completion_unknown` promotion to `passed` / `merge_prepared`.
  - no selected-count-only review completion inference.
  - no bundling `fetch_pr_review_snapshot.sh` or `trigger_codex_review.sh` extraction unless the plan is explicitly amended.
  - no behavior changes inside docs/mirror-only steps.

### 実装ステップ S300 — Characterization / Current Heredoc Inventory
- 振る舞いの目標:
  - 現在残っている snapshot/wait heredoc と既存テスト契約を棚卸しし、S310/S320 が behavior-preserving extraction であることを検証できる状態にする。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
  - `tests/unit/infra/test_init_update.py`
  - `spec-dock/active/issue/report.md`
- 委任契約:
  - delegated role: `dev-coder` for characterization evidence only.
  - behavior mutation is forbidden in this step.
- Red / alternative evidence:
  - Dedicated extraction asset tests may be absent before extraction.
  - Existing snapshot/wait focused tests can serve as characterization evidence if mapped explicitly.
- Green 検証:
  - `rg -n "python3 - <<|'PY'|PY$" src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - focused existing snapshot/wait test mapping recorded in `report.md`.
- reviewer:
  - code-reviewer inspect-only pass.
- commit gate:
  - If S300 changes only `report.md`, commit after reviewer pass. If no file change is needed, record no-op evidence.
- report evidence destination:
  - TDD Evidence, Test Contract Closure for `tc-s300-001` / `tc-s300-002`, Reviewer Gate Status, Step Commit Gate.

### 実装ステップ S310 — Extract `fetch_pr_observation_snapshot.sh`
- 振る舞いの目標:
  - `fetch_pr_observation_snapshot.sh` の payload-building heredoc と metadata JSON parsing heredoc を `scripts/lib/pr_observation_snapshot.py` へ移し、shell wrapper は argument validation と adjacent Python entrypoint 呼び出しに限定する。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py`
  - `tests/unit/infra/test_init_update.py`
  - `spec-dock/active/issue/report.md`
- 計画済み契約:
  - No snapshot classification behavior change.
  - checks/review collector semantics are unchanged.
  - Public flags, stdout final JSON, stderr diagnostics, and `--out` artifact names are preserved.
  - Python entrypoint uses only standard library and fixed local script / `gh` invocations.
- 委任契約:
  - delegated role: `dev-coder`.
  - forbidden changes:
    - no checks collector behavior change.
    - no review collector semantic change.
    - no wait wrapper extraction in S310.
    - no new third-party dependency.
- Red / alternative evidence:
  - `pr_observation_snapshot.py` asset presence test should fail or be absent before extraction.
  - Existing snapshot behavior tests serve as before/after characterization evidence.
- Green 検証:
  - focused snapshot tests for `tc-s310-001`..`tc-s310-005`.
  - focused asset/scaffold test for `tc-s310-006` if added in this step.
  - `git diff --check`.
- reviewer:
  - code-reviewer pass focused on shell/Python boundary, temp/out artifact compatibility, fixed API surface, and secret redaction.
- commit gate:
  - S310 commit after reviewer pass and post-commit clean check.
- report evidence destination:
  - TDD Evidence, Test Contract Closure for `tc-s310-001`..`tc-s310-006`, Closure Coverage, Reviewer Gate Status, Step Commit Gate.

### 実装ステップ S320 — Extract `wait_pr_observation.sh`
- 振る舞いの目標:
  - `wait_pr_observation.sh` の poll loop、snapshot invocation orchestration、quiet/same-fingerprint stability、zero-check grace、review-completion timing、progress rendering、out artifact handling を `scripts/lib/pr_observation_wait.py` へ移す。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `tests/unit/infra/test_init_update.py`
  - `spec-dock/active/issue/report.md`
- 計画済み契約:
  - S204 timing constants and semantics are unchanged.
  - `review_completion_unknown` remains non-pass `human_gate`.
  - trigger script semantics are unchanged.
  - snapshot script public contract is consumed through the shell script boundary, not direct Python imports.
- 委任契約:
  - delegated role: `dev-coder`.
  - forbidden changes:
    - no trigger script behavior change.
    - no review collector semantic broadening.
    - no `passed` / `merge_prepared` from missing completion.
    - no extraction of `fetch_pr_review_snapshot.sh` or `trigger_codex_review.sh`.
- Red / alternative evidence:
  - `pr_observation_wait.py` asset presence test should fail or be absent before extraction.
  - Existing wait tests serve as before/after characterization evidence.
- Green 検証:
  - wait stdout/stderr/out contract tests.
  - quiet / same-fingerprint tests.
  - timeout preserves latest payload tests.
  - S204 review-completion timing tests.
  - late review feedback override tests.
  - focused asset/scaffold test for `tc-s320-007` if added in this step.
  - `git diff --check`.
- reviewer:
  - code-reviewer pass focused on polling semantics, timeout handling, progress line budget, resume metadata, and non-pass safety.
- commit gate:
  - S320 commit after reviewer pass and post-commit clean check.
- report evidence destination:
  - TDD Evidence, Test Contract Closure for `tc-s320-001`..`tc-s320-007`, Closure Coverage, Reviewer Gate Status, Step Commit Gate.

### ドキュメント / ミラー追加ステップ S390
- 振る舞いの目標:
  - Provider extraction files, dogfooding mirror, operator docs, and init/update scaffold output align with S310/S320.
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - `.agents/skills/github-pr-observation/SKILL.md`
  - `.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
  - `.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - focused asset tests if not already added in S310/S320.
- 計画済み契約:
  - Docs describe that operators still invoke `.sh` scripts directly.
  - Docs describe that snapshot/wait wrappers delegate Python logic to adjacent `scripts/lib/*.py` entrypoints.
  - Required permissions and recommended actions are unchanged.
  - Provider/mirror changed files are byte-identical where intended.
- 委任契約:
  - delegated roles:
    - `doc-writer` for provider/mirror `SKILL.md`.
    - `utility-worker` or `dev-coder` for mechanical mirror sync and scaffold verification.
  - forbidden changes:
    - no behavior changes in provider scripts.
    - no modification of S310/S320 implementation logic while doing docs/mirror sync.
    - no claim that PR #190 is auto merge-ready.
- verification:
  - provider/mirror `cmp -s` for changed files.
  - focused init/update asset tests for new Python files.
  - `git diff --check`.
- reviewer:
  - spec-reviewer for docs wording.
  - code-reviewer for mirror/scaffold sync.
- commit gate:
  - S390 commit after reviewer pass and post-commit clean check.
- report evidence destination:
  - Docs Impact Resolution, Test Contract Closure for `tc-s390-001` / `tc-s390-002`, Closure Coverage, Reviewer Gate Status, Step Commit Gate.

### 追加最終品質ゲート S399
- branch diff 範囲:
  - S300 characterization, S310 snapshot extraction, S320 wait extraction, S390 docs/mirror/scaffold changes, and final `report.md` evidence.
- 必須 validation:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation_snapshot or pr_observation_wait or review_completion_unknown or issue_187"`
  - `uv run pytest tests/unit/infra/test_init_update.py -q`
  - `git diff --check`
  - `./spec-dock/scripts/spec-dock validate`
  - provider/mirror `cmp -s` for changed assets
- PR observation gate:
  - Re-run PR observation on latest PR #190 head after push.
  - Do not use stale pre-final PR observation as final evidence.
  - If `review_completion_unknown` appears, report it as non-pass human gate and distinguish it from GitHub mergeability/check status.
- 委任契約:
  - delegated roles:
    - qa-reviewer for final test sufficiency.
    - code-reviewer for integrated runtime/test/docs diff.
    - spec-reviewer for final spec alignment.
  - parent-owned work:
    - final report evidence integration.
    - PR observation orchestration.
    - commit gate and PR delivery handoff.
  - forbidden changes:
    - no behavior changes unless a final reviewer finding requires a bounded follow-up assigned to the relevant previous step or an explicit S399 follow-up.
    - no final commit before all required reviewers pass.
- reviewer gates:
  - qa-reviewer: test sufficiency and race coverage pass.
  - code-reviewer: integrated scripts/tests/docs diff pass.
  - spec-reviewer: requirement/design/plan/report alignment pass.
- commit gate:
  - S399 final evidence commit only after reviewers pass.
  - Do not bundle uncommitted S310/S320 behavior changes into S399.
- report evidence destination:
  - Final QA Gate, Final Code Review Gate, Final Spec Review Gate, Closure Coverage, Step Commit Gate, Final Commit, PR Observation Gate.

### S300+ 未確定事項
- Blocking:
  - なし。
- Non-blocking:
  - Whether `pr_observation_common.py` is needed should be decided after S310/S320 expose concrete duplication.
  - Metadata `gh pr view` execution should move into `pr_observation_snapshot.py` if focused tests lock current JSON and exit behavior tightly; otherwise split into a narrower follow-up inside S310.
  - `fetch_pr_review_snapshot.sh` / `trigger_codex_review.sh` heredoc extraction should remain a separate follow-up unless S310/S320 reveals a hard dependency.

## 追加実装計画 S400+ — Review Inventory and Wait Budget Guard

### 追加計画の位置づけ
- この追加計画は、既存 S01-S399 の実施済み計画を修正・再番号付けしない。
- `discussions/20260616t225521z-14-disc-missed-p2-reserve-next-observation-poll.md`、`discussions/20260616t225521z-15-disc-pr-observation-missed-review-root-cause.md`、`discussions/20260616t231000z-16-disc-system-architect-review-inventory-and-wait-budget-design-draft.md`、`discussions/20260616t233000z-17-disc-implementation-planner-s400-review-inventory-and-wait-budget-plan-draft.md` を S400+ evidence として扱う。
- 目的は、PR #190 の P2 review と review 見逃し分析を受けて、actionable review inventory、decision precedence、wait next-poll budget guard、post-unknown fresh audit metadata を実装できる状態にすること。
- `review_completion_unknown` は引き続き non-pass human gate であり、merge-ready / no-review-work の証明ではない。

### S400+ 依存順序
```text
S400
  -> S410
      -> S420
          -> S430
              -> S490
                  -> S499
```

### 追加クロージャ索引 S400+

| 識別子（ID） | ステップ | スライス | 種別 | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 |
|---|---|---|---|---|---|---|---|
| `tc-s400-001` | S400 | authoring-adoption | authoring | S400+ delegated evidence is adopted or rejected in report before canonical use | discussions `14`..`17`, canonical plan/report diff | delegated draft treated as authority | yes |
| `tc-s400-002` | S400 | plan-review | authoring | fresh `spec-reviewer` pass gates S410 implementation | canonical S400+ plan candidate | implementation starts from unreviewed plan | yes |
| `tc-s410-001` | S410 | current-selected-actionable | acceptance | current-selected unresolved review is actionable | current-boundary unresolved thread | current review blocker hidden | yes |
| `tc-s410-002` | S410 | carryover-actionable | acceptance | carryover `isResolved=false` and `isOutdated=false` thread is actionable | selected IDs empty; GraphQL thread non-outdated unresolved | non-outdated review work remains audit-only | yes |
| `tc-s410-003` | S410 | outdated-audit-only | negative | outdated-only unresolved threads remain audit-only | all unresolved threads `isOutdated=true` | stale review over-blocks PR | yes |
| `tc-s410-004` | S410 | unknown-outdated-audit-only | negative | unavailable/null outdated evidence is not promoted | REST comment exists but GraphQL outdated state unavailable/null | uncertain review artifact becomes false blocker | yes |
| `tc-s410-005` | S410 | inventory-dedupe | regression | current-selected and carryover inventory dedupe by thread/comment identity | same thread appears in both data sets | duplicate repair inventory | yes |
| `tc-s420-001` | S420 | carryover-blocks-unknown | integration | carryover unresolved blocks `review_completion_unknown` | CI passed, head matched, selected unresolved zero, carryover count > 0 | stable unknown hides review work | yes |
| `tc-s420-002` | S420 | precedence-current-selected | integration | current-selected reason wins while carryover IDs remain listed | current-selected and carryover both exist | lower-priority reason obscures current feedback | yes |
| `tc-s420-003` | S420 | pending-beats-unknown | negative | pending review signal remains pending and not unknown | pending review request/signal exists | in-progress review becomes terminal-like human gate | yes |
| `tc-s420-004` | S420 | trusted-completion-empty-inventory | regression | trusted completion path remains intact when actionable inventory is empty | submitted PR review, CI passed, head matched | inventory addition breaks existing pass path | yes |
| `tc-s420-005` | S420 | unknown-empty-inventory | regression | stable no-completion remains possible when actionable inventory is empty | no completion, no pending/blocker, stability satisfied | useful unknown escape hatch removed | yes |
| `tc-s430-001` | S430 | reserve-next-poll-budget | regression | wait sleep leaves budget for next meaningful snapshot | non-terminal payload requires another stability poll | sleep consumes deadline | yes |
| `tc-s430-002` | S430 | preserve-latest-under-budget | regression | under-budget final poll is skipped and latest useful payload is kept | remaining time below next-poll budget | useful payload overwritten by timeout | yes |
| `tc-s430-003` | S430 | terminal-failures-visible | negative | budget guard does not hide failed/stale/actionable terminal states | terminal blocker near deadline | budget guard masks real blocker | yes |
| `tc-s430-004` | S430 | ci-age-300 | negative | CI-passed age below 300 seconds does not promote unknown | PR #190-like 124 second CI-passed age | late review race remains reproducible | yes |
| `tc-s430-005` | S430 | post-unknown-fresh-audit | acceptance | `review_completion_unknown` emits fresh-audit-required metadata | all stability and latency gates satisfied | unknown misread as review absence | yes |
| `tc-s490-001` | S490 | operator-docs | docs | docs describe actionable inventory and unknown/fresh-audit semantics | provider/mirror `SKILL.md` inspection | operator treats unknown as merge-ready | yes |
| `tc-s490-002` | S490 | mirror-sync | scaffold | provider/mirror changed files match where intended | provider and `.agents` file comparison | dogfooding mirror stale | yes |
| `tc-s490-003` | S490 | asset-completeness | scaffold | installed asset set remains complete | init/update asset coverage or inspection | consumer wrapper cannot find required files | yes |
| `tc-s499-001` | S499 | focused-validation | quality | focused S400+ fake-`gh` tests pass | final diff | untested observation behavior | yes |
| `tc-s499-002` | S499 | reviewer-triad | quality | qa-reviewer, code-reviewer, spec-reviewer all pass | final issue-wide diff | worker output replaces final gates | yes |
| `tc-s499-003` | S499 | live-pr-observation | live | latest PR #190 observation reports actionable inventory and P2 status | latest PR #190 head after push | stale observation hides review | yes |
| `tc-s499-004` | S499 | diff-and-specdock-validation | validation | diff hygiene and SpecDock validation pass | final diff | invalid handoff artifact | yes |

### S400+ 共通実行契約
- Parent orchestrator executes exactly one step at a time.
- Runtime/test/scaffold changes are delegated to `dev-coder`.
- Shipped docs / skill text changes are delegated to `doc-writer`.
- Each behavior step closes with focused evidence, fresh reviewer pass, step commit, and post-commit clean check before the next step starts.
- Forbidden across S400+:
  - no public shell flag change without design amendment.
  - no arbitrary GitHub API proxy.
  - no raw token / raw auth stderr output.
  - no `review_completion_unknown` promotion to `passed` / `merge_prepared`.
  - no selected-count-only review completion inference.
  - no carryover promotion when `isOutdated` is unavailable/null.
  - no merge-ready/no-review-work claim from stale PR observation.

### 実装ステップ S400 — Canonical adoption / S400+ authoring gate
- 振る舞いの目標:
  - S400+ delegated evidence is ledgered, canonical `plan.md` receives this S400+ lane, and fresh `spec-reviewer` pass is obtained before implementation.
- 対象ファイル:
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
- 計画済み契約:
  - Existing S01-S399 content remains intact.
  - Discussions `14`..`17` are recorded in Evidence Adoption Ledger with adopted/rejected scope.
  - No implementation source/test/config/GitHub mutation happens in S400.
- 委任契約:
  - delegated role: `spec-reviewer` for canonical plan review; main orchestrator owns canonical edits.
  - input docs: active requirement/design/plan/report, discussions `14`..`17`.
  - allowed paths: `spec-dock/active/issue/plan.md` and `spec-dock/active/issue/report.md` only, edited by the main orchestrator.
  - forbidden changes: implementation files, tests, configs, `.agents`, GitHub state, phase promotion without reviewer pass.
  - acceptance criteria: Evidence Adoption Ledger records S400+ adoption; fresh `spec-reviewer` returns `review_status: pass`.
  - required verification: `git diff --check` and reviewer evidence.
  - reviewer focus: append-only S400+ placement, executable step schema, no S01-S399 rewrite, design/plan traceability.
  - stop conditions: requirement amendment becomes necessary; design evidence becomes stale/contradictory; reviewer fails.
  - output required: spec-review findings, final `review_status`, adoption decision, unresolved blockers, and implementation handoff readiness or block reason recorded in `report.md`.
- 具体テストケース一覧:
  - `tc-s400-001` authoring: S400+ evidence adoption is ledgered
    - 前提: discussions `14`..`17` and S400+ design exist.
    - 操作: orchestrator records adopted/rejected evidence in `report.md`.
    - 期待結果: source paths, target artifacts, adoption decision, and next action are visible.
    - 失敗検出: delegated draft is used as authority without adoption ledger.
    - 検証方法: `report.md` inspection and `git diff --check`.
  - `tc-s400-002` authoring: fresh plan review gates implementation
    - 前提: canonical S400+ plan has been edited.
    - 操作: run fresh `spec-reviewer` on canonical plan.
    - 期待結果: `review_status: pass` before S410 starts.
    - 失敗検出: implementation begins from unreviewed delegated draft.
    - 検証方法: reviewer evidence in `report.md`.
- report evidence destination:
  - Evidence Adoption Ledger, Spec Authoring Gate, Reviewer Gate Status, Step Commit Gate.

### 実装ステップ S410 — Actionable review inventory classification
- 振る舞いの目標:
  - Review collection exposes actionable unresolved inventory as current-selected unresolved plus carryover non-outdated unresolved, while outdated-only or unknown-outdated artifacts remain audit-only.
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh` or its extraction successor if current implementation has moved ownership.
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - Carryover actionable requires GraphQL thread `isResolved=false` and `isOutdated=false`.
  - REST-only or null/unknown outdated state is audit/limitation, not actionable.
  - current-selected is authoritative and dedupes carryover.
  - Existing selected fields remain additive-compatible.
- 委任契約:
  - delegated role: `dev-coder`.
  - input docs: AC-006/AC-007/AC-008, design S400+ review inventory model, this plan.
  - allowed paths: provider review collector/extraction module and focused fake-`gh` tests.
  - forbidden changes: wait budget, snapshot/wait precedence beyond plumbing, docs/mirror sync, generic issue comment promotion.
  - acceptance criteria: `decision.actionable_unresolved_count`, current/carryover counts, actionable/carryover IDs, and compatible selected fields are emitted.
  - required tests: `tc-s410-001`..`tc-s410-005`.
  - reviewer focus: false-positive carryover blocking, outdated handling, dedupe, compatibility, secret-safe limitations.
  - stop conditions: GitHub payload cannot distinguish non-outdated carryover; implementation would promote REST-only comments; design amendment needed.
  - output required: changed files, worker summary, Red/Green verification results, unresolved risks, closure IDs covered, reviewer handoff notes, and `No material implementation decisions beyond the approved plan.` or a Ledger Note.
- 具体テストケース一覧:
  - `tc-s410-001` acceptance: current-selected unresolved is actionable
    - 前提: fake `gh` returns a current-boundary unresolved thread.
    - 操作: run provider review collector.
    - 期待結果: actionable count and current-selected count are greater than zero, with IDs listed.
    - 失敗検出: current review blockers remain selected-only or audit-only.
    - 検証方法: pytest fake-`gh` collector test.
  - `tc-s410-002` acceptance: carryover non-outdated unresolved is actionable
    - 前提: selected IDs are empty, GraphQL thread has `isResolved=false` and `isOutdated=false`.
    - 操作: run provider review collector.
    - 期待結果: carryover and actionable counts are greater than zero, with carryover IDs listed.
    - 失敗検出: non-outdated review work remains hidden in audit data.
    - 検証方法: pytest fake-`gh` collector test.
  - `tc-s410-003` negative: outdated-only unresolved remains audit-only
    - 前提: all fetched unresolved threads have `isOutdated=true`.
    - 操作: run provider review collector.
    - 期待結果: audit data remains visible; actionable and carryover counts are zero.
    - 失敗検出: stale/outdated review thread over-blocks current PR.
    - 検証方法: pytest fake-`gh` collector test.
  - `tc-s410-004` negative: unknown outdated state is not promoted
    - 前提: REST comment exists but GraphQL `isOutdated` is unavailable/null.
    - 操作: run provider review collector.
    - 期待結果: artifact is audit/limitation only, not carryover actionable.
    - 失敗検出: uncertain review artifact becomes false blocker.
    - 検証方法: pytest fake-`gh` collector test.
  - `tc-s410-005` regression: selected and carryover sets dedupe
    - 前提: same thread appears in current-selected and all-fetched non-outdated data.
    - 操作: run provider review collector.
    - 期待結果: current-selected is authoritative and actionable IDs are unique.
    - 失敗検出: duplicate repair inventory.
    - 検証方法: pytest fake-`gh` collector test.
- Green 検証:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "review_inventory or actionable_unresolved or carryover_unresolved or issue_187"`
- reviewer:
  - code-reviewer pass.
- report evidence destination:
  - TDD Evidence, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate, Delegated Worker Evidence.

### 実装ステップ S420 — Snapshot / wait decision precedence and summary alignment
- 振る舞いの目標:
  - Snapshot/wait decisions evaluate actionable review inventory before blocking limitations, pending review, trusted completion, and stable no-completion unknown; `summary.review` and `recommended_next_action` align with actionable inventory.
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py` if final wait classification owns precedence after S320.
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - Actionable unresolved inventory forces `summary.review="unresolved"` and `recommended_next_action="address_review_feedback"`.
  - `review_completion_unknown` is impossible while actionable inventory is non-empty.
  - trusted completion and stable unknown paths remain available when inventory is empty and other gates allow them.
- 委任契約:
  - delegated role: `dev-coder`.
  - input docs: design S400+ decision precedence, S410 output contract.
  - allowed paths: provider snapshot/wait decision modules and focused tests.
  - forbidden changes: collector inventory classification beyond integration plumbing, wait sleep/budget logic, docs/mirror sync, merge-preparer implementation.
  - acceptance criteria: actionable inventory precedes unknown/completion decisions; `summary.review` and `recommended_next_action` align with actionable inventory; existing trusted completion and stable unknown paths still work when inventory is empty.
  - required tests: `tc-s420-001`..`tc-s420-005`.
  - reviewer focus: precedence ordering, compatibility of selected fields, non-pass safety, snapshot/wait consistency.
  - stop conditions: S410 output is insufficient; summary alignment would break public contract without design amendment.
  - output required: changed files, worker summary, Red/Green verification results, unresolved risks, closure IDs covered, reviewer handoff notes, and `No material implementation decisions beyond the approved plan.` or a Ledger Note.
- 具体テストケース一覧:
  - `tc-s420-001` integration: carryover unresolved blocks unknown
    - 前提: CI passed, head matched, selected unresolved zero, carryover count > 0.
    - 操作: run snapshot/wait fake-`gh` path.
    - 期待結果: no `review_completion_unknown`; `summary.review="unresolved"`; action `address_review_feedback`; reason `carryover_non_outdated_unresolved_thread`.
    - 失敗検出: stable unknown hides carryover review work.
    - 検証方法: pytest fake-`gh` snapshot/wait test.
  - `tc-s420-002` integration: current-selected reason wins over carryover
    - 前提: current-selected and carryover unresolved both exist.
    - 操作: run provider snapshot.
    - 期待結果: current-selected reason wins; carryover IDs remain listed.
    - 失敗検出: lower-priority carryover obscures current feedback.
    - 検証方法: pytest fake-`gh` snapshot test.
  - `tc-s420-003` negative: pending review beats unknown
    - 前提: no actionable inventory, no trusted completion, pending review signal exists.
    - 操作: run wait path.
    - 期待結果: pending/wait state remains; no `review_completion_unknown`.
    - 失敗検出: in-progress review becomes terminal-like human gate.
    - 検証方法: pytest fake-`gh` wait test.
  - `tc-s420-004` regression: trusted completion still passes when inventory is empty
    - 前提: CI passed, head matched, trusted submitted PR review exists, actionable inventory zero.
    - 操作: run provider snapshot.
    - 期待結果: existing trusted completion pass-compatible path remains intact.
    - 失敗検出: inventory additions break existing completion behavior.
    - 検証方法: existing trusted completion test plus focused assertion.
  - `tc-s420-005` regression: stable no-completion remains possible with empty inventory
    - 前提: no completion/pending/blocker and actionable inventory zero after stability gates.
    - 操作: run wait path.
    - 期待結果: `review_completion_unknown` remains possible and non-pass.
    - 失敗検出: S400+ removes useful no-completion escape hatch.
    - 検証方法: pytest fake-`gh` wait test.
- Green 検証:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "review_inventory or review_completion_unknown or pr_observation_snapshot or pr_observation_wait or issue_187"`
- reviewer:
  - code-reviewer pass.
- report evidence destination:
  - TDD Evidence, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate, Delegated Worker Evidence.

### 実装ステップ S430 — Wait next-poll budget guard and post-unknown metadata
- 振る舞いの目標:
  - Wait loop reserves enough budget for a meaningful next snapshot, preserves latest useful payload when final poll would be under-budget, raises CI-passed unknown latency default to `300` seconds, and marks post-unknown fresh audit as required.
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - No public shell CLI changes.
  - `review_completion_unknown_min_ci_passed_age_seconds=300`.
  - `wait.post_unknown_fresh_audit_required=true` when unknown is emitted.
  - `wait.final_poll_skipped_reason="insufficient_next_snapshot_budget"` when applicable.
  - Terminal failed/stale/actionable states are not softened by budget guard.
- 委任契約:
  - delegated role: `dev-coder`.
  - input docs: discussions `14`/`15`, design S400+ wait budget guard, S420 decision output.
  - allowed paths: provider wait module and focused tests.
  - forbidden changes: review inventory classifier, snapshot precedence, public flags, global timeout increase as primary fix, docs/mirror sync.
  - acceptance criteria: next-poll budget is reserved; under-budget final poll preserves latest useful payload; CI-passed unknown latency default is `300`; post-unknown fresh audit metadata is emitted; terminal blockers remain visible.
  - required tests: `tc-s430-001`..`tc-s430-005`.
  - reviewer focus: deadline math, timeout preservation, terminal failure precedence, stdout/stderr/out artifact compatibility, no pass weakening.
  - stop conditions: latest payload preservation would hide real blocker; implementation requires new public flags; test can pass only by raising total timeout.
  - output required: changed files, worker summary, timing constant evidence, Red/Green verification results, unresolved risks, closure IDs covered, reviewer handoff notes, and `No material implementation decisions beyond the approved plan.` or a Ledger Note.
- 具体テストケース一覧:
  - `tc-s430-001` regression: sleep reserves next-poll budget
    - 前提: meaningful non-terminal payload needs one more stability poll before deadline.
    - 操作: run wait test with fake snapshot timing.
    - 期待結果: sleep leaves `wait.next_poll_min_budget_seconds` available.
    - 失敗検出: loop sleeps until deadline and leaves fractional snapshot time.
    - 検証方法: pytest fake wait-loop timing test.
  - `tc-s430-002` regression: under-budget final poll preserves latest useful payload
    - 前提: latest payload has useful CI/head/review evidence and remaining time is below next-poll minimum.
    - 操作: run wait path to deadline.
    - 期待結果: no under-budget snapshot starts when the next snapshot cannot satisfy stability/grace; result keeps latest payload and records insufficient budget.
    - 例外: a final confirmation poll or zero-check grace poll may start under the budget floor when it can satisfy the requested stability / human-gate classification before the actual deadline.
    - 失敗検出: final result becomes all-unknown timeout.
    - 検証方法: pytest fake snapshot call-log and final JSON assertions.
  - `tc-s430-003` negative: budget guard does not hide terminal failures
    - 前提: failed CI, stale head, or actionable unresolved review appears near deadline.
    - 操作: run wait path.
    - 期待結果: terminal/actionable state remains visible.
    - 失敗検出: budget guard masks a real blocker.
    - 検証方法: pytest parametrized wait test.
  - `tc-s430-004` negative: CI-passed age below 300 seconds does not promote unknown
    - 前提: CI passed 124 seconds ago, trigger age sufficient, no actionable inventory, no completion.
    - 操作: run wait path beyond quiet/same-fingerprint stability.
    - 期待結果: `review_completion_unknown` is not emitted before 300 seconds.
    - 失敗検出: PR #190 late-review window remains reproducible.
    - 検証方法: pytest fake wait test.
  - `tc-s430-005` acceptance: post-unknown fresh audit metadata is emitted
    - 前提: CI/head passed, actionable inventory empty, no pending/blocking state, all gates satisfied.
    - 操作: run wait path to `review_completion_unknown`.
    - 期待結果: final JSON has `wait.post_unknown_fresh_audit_required=true` and latest inventory fields.
    - 失敗検出: downstream can misread unknown as review absence proof.
    - 検証方法: pytest fake wait test.
- Green 検証:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "next_poll_budget or insufficient_next_snapshot_budget or post_unknown_fresh_audit or review_completion_unknown or pr_observation_wait"`
- reviewer:
  - code-reviewer pass.
- report evidence destination:
  - TDD Evidence, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate, Delegated Worker Evidence.

### ドキュメント / ミラー追加ステップ S490
- 振る舞いの目標:
  - Provider docs and dogfooding mirror reflect S410-S430 behavior, and changed provider assets match mirror files where intended.
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md` if operator-facing semantics changed.
  - `.agents/skills/github-pr-observation/SKILL.md` if provider docs changed.
  - `.agents/skills/github-pr-observation/scripts/**` corresponding to changed provider files.
  - focused asset tests if new/moved files are involved.
- 計画済み契約:
  - Docs state `review_completion_unknown` is non-pass and not review absence proof.
  - Docs identify actionable review inventory as merge-prepared / repair-batch input.
  - Docs mention post-unknown fresh audit if operator-facing.
  - Provider/mirror changed files are byte-identical where intended.
- 委任契約:
  - delegated roles: `doc-writer` for skill text; `dev-coder` or `utility-worker` for mechanical mirror sync.
  - input docs: requirement/design/plan S400+ sections, S410-S430 report evidence, changed provider files.
  - allowed paths: provider/mirror `SKILL.md`, mirror files corresponding to changed provider scripts/modules, and focused asset tests only if needed.
  - forbidden changes: provider behavior changes, unrelated tests, PR #190 merge-ready claim.
  - acceptance criteria: docs explain actionable inventory and unknown/fresh-audit semantics if operator-visible; provider/mirror changed files match where intended; installed asset surface remains complete.
  - required verification: `tc-s490-001`..`tc-s490-003`, provider/mirror `cmp -s`, `git diff --check`.
  - reviewer focus: docs/spec alignment, mirror equality, no behavior drift during sync.
  - stop conditions: docs contradict requirement/design; provider and mirror cannot align; behavior change becomes necessary.
  - output required: changed files, docs inspection summary, mirror comparison results, asset coverage result if applicable, unresolved risks, reviewer handoff notes, and `No material implementation decisions beyond the approved plan.` or a Ledger Note.
- 具体テストケース一覧:
  - `tc-s490-001` docs: operator-facing semantics are documented
    - 前提: S410-S430 behavior is implemented.
    - 操作: inspect provider and mirror `SKILL.md`.
    - 期待結果: docs state actionable inventory and post-unknown fresh audit semantics without claiming unknown means no review work.
    - 失敗検出: operators treat `review_completion_unknown` as merge-ready/no-review evidence.
    - 検証方法: docs inspection recorded in `report.md`.
  - `tc-s490-002` scaffold: provider and mirror changed files match
    - 前提: provider files changed and corresponding mirror paths exist.
    - 操作: compare provider and mirror files.
    - 期待結果: changed mirror files are identical where intended.
    - 失敗検出: dogfooding observation runs stale logic.
    - 検証方法: `cmp -s` or checksum comparison.
  - `tc-s490-003` scaffold: installed asset set remains complete
    - 前提: S410-S430 touch shipped assets.
    - 操作: run existing init/update asset coverage or focused inspection.
    - 期待結果: required files are present in installed asset surface.
    - 失敗検出: consumer repo cannot run updated observation scripts.
    - 検証方法: focused pytest or asset tree inspection.
- reviewer:
  - spec-reviewer for docs wording; code-reviewer for mirror/scaffold sync.
- report evidence destination:
  - Docs Impact Resolution, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate.

### 追加最終品質ゲート S499
- branch diff 範囲:
  - S400 authoring adoption, S410 review inventory, S420 decision precedence, S430 wait budget/metadata, S490 docs/mirror, final `report.md` evidence.
- 必須 validation:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187 or pr_observation or review_inventory or actionable_unresolved or next_poll_budget or review_completion_unknown"`
  - `uv run pytest tests/unit/infra/test_init_update.py -q`
  - `git diff --check`
  - `./spec-dock/scripts/spec-dock validate`
  - provider/mirror `cmp -s` for touched files
- PR observation gate:
  - Re-run PR observation on latest PR #190 head after push.
  - Report latest head SHA, CI/head status, `decision.actionable_unresolved_count`, current-selected IDs, carryover IDs, and comment `3422572159` status if still unresolved and non-outdated.
  - Do not report merge-prepared while actionable unresolved review inventory is non-empty or observation is stale.
- 委任契約:
  - delegated roles: `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`.
  - input docs: final requirement/design/plan/report, S410-S490 diffs/evidence, latest PR #190 observation output.
  - allowed paths: final report evidence only, unless a reviewer finding creates a bounded follow-up assigned back to S410/S420/S430/S490.
  - parent-owned work: final report evidence integration, PR observation orchestration, commit gate, PR delivery handoff.
  - acceptance criteria: focused and broad validation pass or blockers are recorded; provider/mirror comparisons pass; live PR #190 observation is fresh; final reviewer triad passes.
  - required verification: `tc-s499-001`..`tc-s499-004`, final pytest selectors, `git diff --check`, `spec-dock validate`, provider/mirror comparisons, fresh PR observation.
  - forbidden changes: behavior changes in S499 unless bounded follow-up returns to S410/S420/S430/S490; final commit before reviewers pass; stale PR observation reuse.
  - reviewer focus:
    - qa-reviewer: fake-`gh` coverage, late-review and budget race coverage.
    - code-reviewer: integrated provider/mirror/runtime/test diff and false-pass safety.
    - spec-reviewer: requirement/design/plan/report alignment.
  - stop conditions: any reviewer fails; PR observation is stale/head-mismatched; actionable unresolved review remains and workflow attempts merge-prepared reporting.
  - output required: final validation summary, reviewer verdicts, latest PR #190 head SHA, actionable inventory fields, unresolved blockers or `none`, final next action, and commit/PR handoff evidence.
- 具体テストケース一覧:
  - `tc-s499-001` quality: focused S400+ fake-`gh` regression suite passes
    - 前提: S410-S490 are complete.
    - 操作: run focused pytest selector.
    - 期待結果: focused tests pass or unrelated failures are explained.
    - 失敗検出: S400+ closure relies on untested script behavior.
    - 検証方法: pytest command output in report.
  - `tc-s499-002` quality: final reviewer triad passes
    - 前提: final issue-wide diff and report evidence are ready.
    - 操作: run `qa-reviewer`, issue-wide `code-reviewer`, and `spec-reviewer`.
    - 期待結果: all return `review_status: pass`.
    - 失敗検出: final gate is replaced by worker output.
    - 検証方法: reviewer evidence in `report.md`.
  - `tc-s499-003` live gate: PR #190 final re-observation uses latest head
    - 前提: S400+ changes are pushed or available for dogfooding observation.
    - 操作: run PR observation against latest PR #190 head.
    - 期待結果: report records latest head, CI/head status, actionable inventory, current-selected IDs, carryover IDs, and P2 `3422572159` status if applicable.
    - 失敗検出: stale pre-fix observation is reused or P2 remains hidden.
    - 検証方法: live observation JSON summary in `report.md`.
  - `tc-s499-004` validation: SpecDock and diff hygiene pass
    - 前提: final diff is ready.
    - 操作: run `git diff --check` and `./spec-dock/scripts/spec-dock validate`.
    - 期待結果: both pass or blockers are reported.
    - 失敗検出: final handoff includes whitespace/schema/spec-dock validation defects.
    - 検証方法: command evidence in `report.md`.
- report evidence destination:
  - Final QA Gate, Final Code Review Gate, Final Spec Review Gate, PR Observation Gate, Closure Coverage, Step Commit Gate, Final Commit.

### Post-observation bounded repair lane S500
- 背景:
  - S499 PR observation is both a live PR gate and a manual test of the observation scripts.
  - When S499 observation exposes fresh review findings, runtime/test fixes must not be hidden inside S499 final evidence.
  - This lane records bounded reassignment created by PR #190 observation on head `40fe4dc7d98bd3cc0587aebdbeadadc1deba22b8`.
- 対象 review findings:
  - `3425177951`: under-budget pre-poll gate must not skip a required confirmation poll or zero-check grace poll when that poll can still classify the latest payload before the actual deadline.
  - `3425177952`: no-Actions + readable green check-runs may pass when commit statuses are unreadable due only to `commit_statuses_read` permission denial; non-green / merge-blocking / required-missing states remain non-pass.
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
  - `tests/unit/infra/test_init_update.py`
  - this issue `report.md`
- 委任契約:
  - delegated role: `dev-coder` for runtime/tests; parent orchestrator integrates report evidence and reviewer gates.
  - allowed paths: only the listed runtime provider/mirror files, focused tests, and report evidence.
  - forbidden changes: unrelated PR observation semantics, public CLI flag changes, global timeout increases as primary fix, unbounded job expansion, merge-ready claim while actionable inventory remains.
  - required reviewers: code-reviewer, qa-reviewer, spec-reviewer before commit.
  - stop conditions: fix requires broader design changes; tests pass only by weakening non-green guards; latest observation cannot be tied to the current head.
- 具体テストケース一覧:
  - `tc-s510-001` wait: short timeout still attempts required confirmation poll
    - 前提: latest payload can become `review_completion_unknown` after one more stable confirmation poll and remaining time is below the budget floor.
    - 期待結果: wait attempts the confirmation poll instead of returning `insufficient_next_snapshot_budget` after one poll.
    - 検証方法: focused fake wait-loop pytest.
  - `tc-s510-002` wait: under-budget zero-check grace can still be evaluated
    - 前提: latest payload has zero-check limitation, `poll < zero_check_grace_polls`, and remaining time is below the budget floor.
    - 期待結果: wait attempts the grace poll instead of returning `insufficient_next_snapshot_budget` early.
    - 検証方法: focused fake wait-loop pytest.
  - `tc-s520-001` checks: readable green check-runs tolerate unreadable commit statuses
    - 前提: Actions has zero runs, check-runs are all green, commit statuses endpoint returns `commit_statuses_read` permission denial, merge state is clean.
    - 期待結果: `ci.status="passed"` and the commit-status permission limitation is informational.
    - 検証方法: focused fake `gh` pytest.
  - `tc-s520-002` checks: non-green external evidence remains non-pass
    - 前提: no-Actions external evidence includes failed/pending/non-green checks or statuses, missing required checks, or blocking merge state.
    - 期待結果: status remains non-pass and blocking limitation is not downgraded.
    - 検証方法: existing external green/non-green selector.
  - `tc-s590-001` parity: provider and dogfooding mirror stay byte-identical for changed runtime files.
  - `tc-s599-001` quality: focused selectors, broad PR observation selector, full infra unit file, diff hygiene, SpecDock validation, and generated-artifact cleanup pass.
- PR observation / manual-test evidence:
  - latest observation must record head SHA, CI/head/review summary, current-selected IDs, carryover IDs, actionable count, and outdated status for comment `3422572159`.
  - post-fix PR observation must be rerun on the latest pushed head before final merge-ready claim.
- report evidence destination:
  - S499 post-observation P2 follow-up, S500/S510/S520/S590/S599 evidence, reviewer gates, step commit gate, post-push PR observation gate.

### Post-push CI/manual-test repair lane S530
- 背景:
  - S500 commit `bc11c60a8960d990b939f4582159fb44546bc3f4` was pushed and observed as both a PR gate and a manual test of the observation scripts.
  - The observation/follow-up cross-check correctly detected CI failure instead of timing out or falsely passing.
  - GitHub Provider CI failed on `test_issue_187_s430_under_budget_grace_poll_is_single_attempt`: the wait loop returned `polls == 3` where the bounded-under-budget contract expected `polls == 2`.
- 対象:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - this issue `plan.md` and `report.md`
- 設計/実装方針:
  - Treat the CI failure as a valid manual-test finding from the live PR observation loop.
  - Preserve the S510 behavior that allows one under-budget confirmation/grace poll when it can classify before the actual deadline.
  - Prevent a no-sleep loop from consuming the under-budget exception repeatedly after a fast snapshot shrinks `next_poll_min_budget_seconds`.
  - Do not broaden public CLI flags or weaken non-green CI/review guards.
- 委任契約:
  - delegated role: `dev-coder` for the runtime fix.
  - required review: `code-reviewer` before commit; QA evidence is supplied by focused/broad wait-loop selectors and full infra file validation.
  - parent orchestrator owns report/plan integration, commit, push, and re-observation.
- 具体テストケース一覧:
  - `tc-s530-001` wait: under-budget exception is not re-used in a no-sleep loop after a fast snapshot.
    - 前提: first snapshot consumes the under-budget exception, later snapshots are faster, and the process still has enough wall-clock time to spin.
    - 期待結果: wait stops with `insufficient_next_snapshot_budget` after the single allowed exception instead of continuing to consume zero-check grace polls.
    - 検証方法: `test_issue_187_s430_under_budget_grace_poll_is_single_attempt`.
  - `tc-s530-002` wait: post-exception stop emits explicit skip reason and preserves latest useful payload.
    - 前提: latest non-terminal payload consumed the single under-budget exception and the loop would otherwise spin without sleep.
    - 期待結果: wait stops with `final_poll_skipped_reason="insufficient_next_snapshot_budget"` and keeps the latest limitations/summary visible.
    - 検証方法: `test_issue_187_s430_under_budget_grace_poll_is_single_attempt` plus broad wait/review selector.
  - `tc-s530-003` validation: full `tests/unit/infra/test_init_update.py`, provider/mirror parity, `git diff --check`, generated-artifact cleanup, and fresh post-push PR observation pass.
- report evidence destination:
  - S530 post-push CI/manual-test repair, reviewer gate, commit gate, and post-push PR observation gate.

### S400+ 未確定事項
- Blocking:
  - なし。
- Non-blocking:
  - S400+ carryover actionable inventory is now reflected as AC-008; future refinements should keep AC-006 review-unknown and AC-008 actionable-inventory semantics separate.
  - Whether `review_completion_unknown_min_ci_passed_age_seconds=300` should remain hard-coded internal constant or named module constant only.
  - Whether merge-preparer workflow changes should become a separate follow-up after observation payload exposes actionable inventory.
