---
種別: 実装計画書（Issue）
ID: "iss-00187"
タイトル: "Use Actions Endpoint For PR Observation CI State"
関連GitHub: ["#187"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-16"
依存: ["requirement.md", "design.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00187 Use Actions Endpoint For PR Observation CI State — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007
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
  - AC-001..AC-007 and EC-001..EC-004 mapped closure IDs pass.
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
