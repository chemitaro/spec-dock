---
種別: 実装計画書（Issue）
ID: "iss-00219"
タイトル: "Carryover Unresolved Threads Stop Observation"
関連GitHub: ["#219"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
依存: ["requirement.md", "design.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00219 Carryover Unresolved Threads Stop Observation — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001 guard 未満の carryover-only missing-completion は wait/resume 継続
  - AC-002 current selected unresolved / changes requested は即 feedback handling
  - AC-003 guard 満了後の carryover-only missing-completion は `review_completion_unknown`
  - AC-004 trusted completion 後の carryover unresolved は feedback handling
  - AC-005 snapshot と wait の status contract consistency
  - AC-006 skill docs の two-axis contract
- EC:
  - EC-001 fallback issue comment policy は変更しない
  - EC-002 outdated / unknown-outdated threads は actionable inventory に昇格しない
  - EC-003 CI/head blockers を優先する
  - EC-004 empty-inventory unknown path は維持する
- 制約:
  - Provider-side installed skill assets を source of truth とする。
  - 1 implementation step = 1 review scope = 1 commit boundary。
  - Delegated worker output は reviewer pass の代替にしない。

## 依存関係から導く実装順序
- 依存関係の参照元:
  - `design.md` の dependency analysis、module dependency diagram、file change plan。
- 順序ルール:
  - 先に public JSON behavior を red/characterization tests で固定する。
  - 次に provider-side runtime classification を変更する。
  - Runtime が固まった後に skill docs / dogfooding mirror の解釈面を解決する。
  - 最後に docs impact と final quality gate を閉じる。
- step 依存サマリー:
  - S01:
    - 依存: approved requirement/design
    - unblock: S02
    - 対象ファイル: `tests/unit/infra/test_init_update.py`
  - S02:
    - 依存: S01 red/characterization evidence
    - unblock: S03, S90
    - 対象ファイル: provider-side observation runtime
  - S03:
    - 依存: S02 behavior
    - unblock: S90
    - 対象ファイル: provider-side `SKILL.md`, dogfooding mirror if synchronized
  - S90:
    - 依存: S01-S03
    - unblock: S99
    - 対象ファイル: `report.md` and required docs impact records
  - S99:
    - 依存: S01-S90
    - unblock: PR / issue execution closeout

## ステップ一覧
- S01 Regression Tests:
  - 観測可能な振る舞い: Issue219 classification matrix が pre-fix runtime で失敗または既存期待値 supersession として固定される。
  - 依存: requirement/design pass
  - unblock: S02
  - 対象ファイル: `tests/unit/infra/test_init_update.py`
  - 閉じる要件: AC-001..AC-005, EC-001..EC-004
  - レビューゲート: code-reviewer
- S02 Provider Runtime Classification Fix:
  - 観測可能な振る舞い: provider runtime が current lifecycle と carryover inventory を分離して final JSON を返す。
  - 依存: S01
  - unblock: S03, S90
  - 対象ファイル: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/*.py`
  - 閉じる要件: AC-001..AC-005, EC-001..EC-004
  - レビューゲート: code-reviewer
- S03 Skill Docs / Mirror Resolution:
  - 観測可能な振る舞い: future agent が skill docs から two-axis contract を読め、provider/mirror 状態が report に残る。
  - 依存: S02
  - unblock: S90
  - 対象ファイル: provider-side `SKILL.md`; `.agents/...` mirror if intentionally synchronized
  - 閉じる要件: AC-006 and docs side of AC-001/AC-003/AC-004
  - レビューゲート: spec-reviewer; mirror runtime files touchedなら code-reviewer も必要
- S90 Docs Impact:
  - 観測可能な振る舞い: report に Issue187 expectation supersession、provider/mirror decision、closure evidence が残る。
  - 依存: S01-S03
  - unblock: S99
  - 対象ファイル: `report.md` and explicitly required docs
  - 閉じる要件: AC-006, cross-step evidence
  - レビューゲート: spec-reviewer
- S99 Final Quality Gate:
  - 観測可能な振る舞い: AC/EC closure、focused tests、unit tests、validate、QA/code/spec reviews が揃う。
  - 依存: S01-S90
  - unblock: delivery / PR preparation
  - 対象ファイル: report evidence only unless reviewer finding requires plan amendment
  - 閉じる要件: all
  - レビューゲート: qa-reviewer, issue-wide code-reviewer, spec-reviewer

## 要件 ↔ ステップ対応
- AC-001 -> S01, S02, S99
- AC-002 -> S01, S02, S99
- AC-003 -> S01, S02, S99
- AC-004 -> S01, S02, S99
- AC-005 -> S01, S02, S99
- AC-006 -> S03, S90, S99
- EC-001 -> S01, S02
- EC-002 -> S01, S02
- EC-003 -> S01, S02
- EC-004 -> S01, S02

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ（step） | スライス（slice） | 種別（type） | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル（evidence level） | クロージャ証跡（closure evidence） |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01/S02 | guard-under carryover-only | acceptance | AC-001 | `pending` / `wait_or_resume` / `observation_complete=false` / `missing_current_completion_signal` | CI passed, head matched, current selected 0, completion none, carryover > 0, latency false | carryover-only premature terminal feedback | yes | red-required | S01/S02 report closure |
| tc-002 | S01/S02 | current selected blocker | acceptance | AC-002 | current selected unresolved / changes requested が `address_review_feedback` になる | current selected unresolved thread or selected changes requested | current feedback の遅延 | yes | red-required | S01/S02 report closure |
| tc-003 | S01/S02 | guard-satisfied carryover-only | acceptance | AC-003 | `review_completion_unknown` human gate and fresh audit metadata | tc-001 state plus latency true | infinite wait / wrong carryover terminal | yes | red-required | S01/S02 report closure |
| tc-004 | S01/S02 | trusted completion + carryover | acceptance | AC-004 | `carryover_non_outdated_unresolved_thread` feedback handling | submitted PR review completion, no current blocker, carryover > 0 | false pass / false unknown | yes | red-required | S01/S02 report closure |
| tc-005 | S01/S02/S99 | snapshot/wait consistency | acceptance | AC-005 | snapshot と wait が同じ next-action family と reason 意味を返す | AC-001..AC-004 fixtures | one-shot / wait contract divergence | yes | red-required | S01/S02/S99 report closure |
| tc-006 | S03/S90/S99 | skill docs | docs | AC-006 | skill docs が lifecycle/inventory split と unknown semantics を説明する | updated `SKILL.md` and mirror decision | future-agent JSON 誤読 | yes | inspect-only | S03/S90/S99 report closure |
| tc-007 | S01/S02 | fallback preservation | edge | EC-001 | fallback issue comment は low-confidence path のまま | completion signal fallback | Issue218 policy の accidental change | yes | covered-existing + targeted regression | S01/S02 report closure |
| tc-008 | S01/S02 | outdated exclusion | edge | EC-002 | outdated/unknown-outdated は actionable inventory に昇格しない | thread outdated true/null/unavailable | stale feedback promotion | yes | covered-existing | S01/S02 report closure |
| tc-009 | S01/S02 | CI/head priority | edge | EC-003 | CI/head blockers が review/carryover policy より優先される | stale head, CI pending/running/failed/none, limitations | review policy overriding CI/head | yes | covered-existing + targeted regression | S01/S02 report closure |
| tc-010 | S01/S02 | empty-inventory unknown | edge | EC-004 | empty inventory の existing `review_completion_unknown` path を維持 | no carryover, no current selected, completion none, latency true | unknown path regression | yes | covered-existing | S01/S02 report closure |

## レビュー / QA ゲート方針
- RG1 step review:
  - 実施タイミング: 各 implementation step の commit 前。
  - reviewer: code/runtime/tests は code-reviewer、docs-only は spec-reviewer。
  - pass 条件: `review_status: pass`。
- QG1 final QA:
  - reviewer: qa-reviewer。
  - 範囲: closure index coverage、missing high-value tests、integration test 要否。
- CR1 final code review:
  - reviewer: issue-wide code-reviewer。
  - 範囲: runtime/test/docs integrated diff、責務境界、回帰リスク。
- SG1 final spec review:
  - reviewer: spec-reviewer。
  - 範囲: requirement / design / plan / report / implementation / tests / docs 整合。

## 実行ルール（全ステップ共通）
- 各 step は report update、step reviewer gate、commit/no-op gate を閉じてから次 step へ進む。
- Step が code/runtime/tests を含む場合は code-reviewer pass が必要。
- Docs-only step は spec-reviewer docs/spec alignment pass が必要。
- `plan.md` には planned contract だけを書き、observed result は `report.md` に残す。
- 新 top-level status、新 primary `status_reason`、fallback issue comment policy 変更、GitHub collection scope 変更が必要になった場合は plan amendment と re-review を先に行う。

## 実装ステップ

### 実装ステップ S01 — Regression Tests
- 振る舞いの目標（behavior goal）:
  - Issue219 の classification matrix を public script JSON behavior として固定し、既存 Issue187 の carryover-only snapshot expectation を更新 / supersede する。
- design 参照:
  - 状態分類テーブル、テスト戦略、要件 / 例外 -> 検証マッピング。
- 依存:
  - requirement/design pass。
- unblock:
  - S02。
- 対象ファイル:
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約（planned contract）:
  - scope:
    - Guard-under carryover-only、guard-satisfied carryover-only、current selected priority、trusted completion + carryover、fallback/CI/head/outdated/empty unknown を test seeds として固定する。
  - テスト義務:
    - closure id: tc-001, tc-002, tc-003, tc-004, tc-005, tc-007, tc-008, tc-009, tc-010
    - coverage rationale: changed public JSON contract and regression risk are high.
  - Red / 代替証跡の要件:
    - red-required:
      - New Issue219 tests should fail against pre-fix runtime where carryover-only becomes terminal feedback.
      - Existing Issue187 S420 expectation should be revised or superseded with explicit report note.
  - 実装範囲:
    - allowed paths:
      - `tests/unit/infra/test_init_update.py`
    - forbidden changes:
      - Runtime code, skill docs, canonical docs, GitHub state, unrelated tests.
  - Green 検証:
    - `uv run pytest tests/unit/infra/test_init_update.py -k "issue_219 or issue_187_s420 or issue_187_s430"`
  - Refactor / cleanup ガードレール:
    - 既存 fake snapshot / fake gh helper pattern を使い、private helper だけの test にしない。
  - closure 証跡要件:
    - Step Contract Closure: S01 rows for tc-001..tc-005 and edge rows.
    - Test Contract Closure: pre-fix red or explicit characterization result.
    - Closure Coverage: all S01 closure ids mapped.
  - report 証跡の記録先:
    - `report.md` 実装記録、TDD evidence、Closure Delta、Reviewer Gate Status、Step Commit Gate。
  - amendment trigger:
    - Public wrapper-level fixtures cannot express required states without runtime edits.

#### 委任契約（delegation contract）
- 委任ロール:
  - dev-coder
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, `tests/unit/infra/test_init_update.py`, `phase_plan_issue.md`, `authoring/issue-plan.md`
- 許可 paths:
  - `tests/unit/infra/test_init_update.py`
- 禁止 changes:
  - Runtime/provider files, `.agents`, skill docs, canonical docs, GitHub state.
- 受け入れ条件:
  - Closure ids listed in S01 have failing or characterization evidence.
- 必須 tests:
  - Focused pytest command above.
- reviewer focus:
  - code-reviewer: test sensitivity and public JSON behavior.
- 必須出力:
  - Worker summary.
  - Changed files.
  - Expected pre-fix failures or characterization evidence.
  - Verification result.
  - Issue187 supersession note for `report.md` Closure Delta.
  - Unresolved risks.
  - Report evidence destination covering Implementation Delegation Gate, Delegated Worker Evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta, Reviewer Gate Status, and Step Commit Gate.
  - `Ledger Note` for material decisions or `No material implementation decisions beyond the approved plan.`
- 停止条件:
  - Need runtime changes to create test fixtures, or test scope spills beyond observation scripts.

#### 具体テストケース一覧
- `tc-s01-001` acceptance: guard-under carryover-only remains wait/resume
  - 前提: CI passed, head matched, current selected unresolved 0, completion none, carryover unresolved count 1, latency guard not satisfied.
  - 操作: wait fake snapshot helper runs classification.
  - 期待結果: `recommended_next_action="wait_or_resume"`, `observation_complete=false`, `decision.status_reason="missing_current_completion_signal"`, carryover ids remain.
  - 失敗検出: carryover-only inventory causes `address_review_feedback`.
  - 検証方法: Issue219 wait regression.
  - 関連 closure id: tc-001, tc-005
- `tc-s01-002` regression: Issue187 carryover-only snapshot expectation is superseded
  - 前提: Existing S420 snapshot test expects terminal carryover feedback for missing completion.
  - 操作: Revise or supersede with Issue219 expectation.
  - 期待結果: missing-completion snapshot remains wait family while trusted completion + carryover remains feedback handling.
  - 失敗検出: old expectation continues to mask Issue219.
  - 検証方法: focused pytest on Issue187 S420 and Issue219 tests.
  - 関連 closure id: tc-001, tc-004, tc-005
- `tc-s01-003` acceptance: current selected unresolved still wins
  - 前提: current selected unresolved exists, carryover may also exist.
  - 操作: snapshot/wait fixtures classify.
  - 期待結果: `human_gate` / `address_review_feedback`, reason `current_selected_unresolved_thread`.
  - 失敗検出: current feedback is delayed into wait/unknown path.
  - 検証方法: focused pytest.
  - 関連 closure id: tc-002
- `tc-s01-004` acceptance: latency-satisfied carryover-only becomes unknown
  - 前提: tc-s01-001 state but latency guard true.
  - 操作: wait fake snapshots with age metadata.
  - 期待結果: `human_gate`, `decision.status="unknown"`, `decision.status_reason="review_completion_unknown"`, `wait.post_unknown_fresh_audit_required=true`, carryover ids remain.
  - 失敗検出: carryover prevents unknown or disappears.
  - 検証方法: focused pytest.
  - 関連 closure id: tc-003, tc-005
- `tc-s01-005` acceptance: trusted completion plus carryover remains feedback
  - 前提: `completion_signal="submitted_pull_request_review"`, no current selected blocker, carryover count 1.
  - 操作: snapshot/wait fixtures classify.
  - 期待結果: `human_gate` / `address_review_feedback`, reason `carryover_non_outdated_unresolved_thread`.
  - 失敗検出: trusted completion + carryover becomes pass or unknown.
  - 検証方法: focused pytest.
  - 関連 closure id: tc-004, tc-005
- `tc-s01-006` edge: fallback / outdated / CI-head / empty unknown are unchanged
  - 前提: existing fallback, outdated/null, CI/head blocker, empty-inventory unknown fixtures.
  - 操作: targeted pytest subset.
  - 期待結果: existing EC contracts remain.
  - 失敗検出: Issue219 changes unrelated policy.
  - 検証方法: focused pytest around fallback/outdated/stale_head/review_completion_unknown.
  - 関連 closure id: tc-007, tc-008, tc-009, tc-010

#### ステップ完了契約
- close 条件:
  - Required tests are present and show expected red/characterization evidence.
- 検証 evidence:
  - Focused pytest output.
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta.
- 残リスク:
  - Broader unit suite may expose unrelated failures; classify in report.

#### ステップゲート
- step reviewer gate:
  - reviewer: code-reviewer
  - review 範囲: test diff only
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed or approved-no-op
  - commit 範囲: S01 tests only

### 実装ステップ S02 — Provider Runtime Classification Fix
- 振る舞いの目標:
  - Provider-side runtime が carryover-only missing-completion を terminal feedback にせず、latency guard / trusted completion / current selected priority を正しく扱う。
- design 参照:
  - Helper design, interface contract, state classification table.
- 依存:
  - S01.
- unblock:
  - S03, S90.
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py` only if centralizing optional inventory field is necessary.
- 計画済み契約:
  - scope:
    - Split current selected blocker from carryover-only inventory in provider runtime.
  - テスト義務:
    - closure id: tc-001..tc-005, tc-007..tc-010
  - Red / 代替証跡:
    - S01 tests are the red evidence.
  - 実装範囲:
    - allowed paths: provider runtime files listed above.
    - forbidden changes: `.agents` mirror direct edits, skill docs, tests beyond S01, GitHub collection redesign, fallback promotion.
  - Green 検証:
    - `uv run pytest tests/unit/infra/test_init_update.py -k "issue_219 or issue_187_s420 or issue_187_s430 or fallback_issue_comment"`
    - `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation"`
  - Refactor / cleanup:
    - Small helper split only; no broad runtime restructure.
  - amendment trigger:
    - Need new top-level status/reason, collection scope change, or fallback policy change.

#### 委任契約
- 委任ロール:
  - dev-coder
- 入力 docs:
  - Requirement/design/plan, S01 evidence, provider runtime files.
- 許可 paths:
  - S02 target provider runtime files.
- 禁止 changes:
  - Tests, docs, mirror files, GitHub state, unrelated runtime.
- 受け入れ条件:
  - S01 tests pass and EC behavior remains.
- 必須 tests:
  - Focused pytest commands above.
- reviewer focus:
  - code-reviewer: public JSON compatibility, latency guard, minimal diff.
- 必須出力:
  - Worker summary.
  - Changed files.
  - Helper split summary.
  - Verification result.
  - Unresolved risks.
  - Report evidence destination covering Implementation Delegation Gate, Delegated Worker Evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta, Reviewer Gate Status, and Step Commit Gate.
  - `Ledger Note` for material decisions or `No material implementation decisions beyond the approved plan.`
- 停止条件:
  - Requirement/design conflict, path outside allowed scope, or unable to pass S01 without scope expansion.

#### 具体テストケース一覧
- `tc-s02-001` implementation: snapshot guard-under carryover-only stays missing completion
  - 前提: S01 snapshot regression exists.
  - 操作: update snapshot classification helper usage.
  - 期待結果: carryover-only does not force `address_review_feedback` without trusted completion.
  - 失敗検出: `actionable_unresolved_reason(...)` remains terminal for carryover-only.
  - 検証方法: S01 focused pytest.
  - 関連 closure id: tc-001, tc-005
- `tc-s02-002` implementation: wait unknown candidate allows carryover-only
  - 前提: S01 latency-satisfied regression exists.
  - 操作: update unknown candidate and finalization.
  - 期待結果: latency guard controls `review_completion_unknown`, carryover ids remain.
  - 失敗検出: carryover inventory prevents unknown forever.
  - 検証方法: S01 focused pytest.
  - 関連 closure id: tc-003, tc-005
- `tc-s02-003` implementation: current selected priority remains terminal
  - 前提: current selected blocker exists.
  - 操作: focused tests.
  - 期待結果: current selected reason wins.
  - 失敗検出: current feedback delayed.
  - 検証方法: focused pytest.
  - 関連 closure id: tc-002
- `tc-s02-004` implementation: trusted completion plus carryover remains feedback
  - 前提: trusted completion + carryover.
  - 操作: focused tests.
  - 期待結果: `carryover_non_outdated_unresolved_thread` feedback handling.
  - 失敗検出: false pass / false unknown.
  - 検証方法: focused pytest.
  - 関連 closure id: tc-004
- `tc-s02-005` edge: fallback/CI/head/outdated/empty unknown unchanged
  - 前提: EC fixtures.
  - 操作: targeted test subset.
  - 期待結果: existing priorities remain.
  - 失敗検出: unrelated policy drift.
  - 検証方法: focused pytest.
  - 関連 closure id: tc-007, tc-008, tc-009, tc-010

#### ステップ完了契約
- close 条件:
  - S01 focused tests pass with provider runtime changes.
- 検証 evidence:
  - Focused pytest output.
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage.
- 残リスク:
  - Optional `actionable_inventory_reason` may need docs/tests if added.

#### ステップゲート
- step reviewer gate:
  - reviewer: code-reviewer
  - review 範囲: provider runtime only
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed or approved-no-op
  - commit 範囲: S02 runtime only

### 実装ステップ S03 — Skill Docs / Mirror Resolution
- 振る舞いの目標:
  - `SKILL.md` が two-axis lifecycle/inventory contract を説明し、provider/mirror state が明確になる。
- design 参照:
  - Interface contract, risk/migration, docs impact.
- 依存:
  - S02.
- unblock:
  - S90.
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - `.agents/skills/github-pr-observation/...` only if synchronized intentionally.
- 計画済み契約:
  - scope:
    - `review_completion_unknown` wording、carryover-only wait guidance、trusted completion + carryover guidance、selected count warningを更新する。
  - テスト義務:
    - closure id: tc-006 plus docs side of tc-001/tc-003/tc-004.
  - Red / 代替証跡:
    - inspect-only: docs diff and spec-review.
  - 実装範囲:
    - allowed paths: skill docs and explicitly chosen mirror paths.
    - forbidden changes: provider runtime, tests, unrelated skills, GitHub state.
  - Green 検証:
    - docs diff inspection.
    - `git diff -- src/spec_dock/assets/install_root/.agents/skills/github-pr-observation .agents/skills/github-pr-observation`
  - amendment trigger:
    - Broad scaffold regeneration or unrelated mirror churn required.

#### 委任契約
- 委任ロール:
  - doc-writer; dev-coder only if mirror runtime synchronization changes code assets.
- 入力 docs:
  - Requirement/design/plan, S02 diff, current `SKILL.md`.
- 許可 paths:
  - S03 target files.
- 禁止 changes:
  - Runtime provider classification, tests, canonical docs except report evidence, unrelated assets.
- 受け入れ条件:
  - AC-006 is readable from skill docs.
- 必須 tests / verification:
  - docs diff inspection and spec-review.
- reviewer focus:
  - spec-reviewer docs/spec alignment; code-reviewer if mirror runtime files are touched.
- 必須出力:
  - Worker summary.
  - Changed files or approved-no-op checked files.
  - Docs diff summary.
  - Provider/mirror decision.
  - Verification result.
  - Unresolved risks.
  - Report evidence destination covering Implementation Delegation Gate, Delegated Worker Evidence, Docs Impact Resolution, Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta, Reviewer Gate Status, and Step Commit Gate.
  - `Ledger Note` for material decisions or `No material implementation decisions beyond the approved plan.`
- 停止条件:
  - Need broader update/sync or disagreement with S02 behavior.

#### 具体テストケース一覧
- `tc-s03-001` docs: unknown no longer implies empty actionable inventory
  - 前提: Existing docs say actionable inventory empty.
  - 操作: update wording.
  - 期待結果: docs say no current-boundary selected actionable feedback, while carryover may exist.
  - 失敗検出: future agents read unknown as no-review-work proof.
  - 検証方法: docs diff and spec review.
  - 関連 closure id: tc-006, tc-003
- `tc-s03-002` docs: guard-under carryover-only remains wait/resume
  - 前提: carryover exists and completion missing below guard.
  - 操作: inspect updated docs.
  - 期待結果: docs do not instruct early `address_review_feedback`.
  - 失敗検出: docs preserve premature stop guidance.
  - 検証方法: docs diff.
  - 関連 closure id: tc-001, tc-006
- `tc-s03-003` docs: trusted completion + carryover remains feedback
  - 前提: trusted completion and carryover unresolved.
  - 操作: inspect docs.
  - 期待結果: docs preserve carryover feedback handling after completion.
  - 失敗検出: docs demote carryover to audit-only/pass.
  - 検証方法: docs diff.
  - 関連 closure id: tc-004, tc-006
- `tc-s03-004` mirror: provider and dogfooding state are explicit
  - 前提: provider source-of-truth and `.agents` mirror both exist.
  - 操作: diff provider/mirror or run accepted sync path.
  - 期待結果: report explains aligned, intentionally synced, or intentionally pending state.
  - 失敗検出: silent provider/mirror drift.
  - 検証方法: diff inspection.
  - 関連 closure id: tc-006

#### ステップ完了契約
- close 条件:
  - Skill docs explain lifecycle/inventory split and provider/mirror decision is recorded.
- 検証 evidence:
  - docs diff, provider/mirror diff or sync evidence.
- report evidence:
  - Docs Impact, Step Contract Closure, Reviewer Gate Status.
- 残リスク:
  - Mirror synchronization may require separate command or follow-up if broad.

#### ステップゲート
- step reviewer gate:
  - reviewer: spec-reviewer; plus code-reviewer if runtime mirror touched.
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed or approved-no-op
  - commit 範囲: S03 docs/mirror only

### ドキュメント影響の解消ステップ S90（docs impact resolution / docs refresh）
- 対象:
  - `report.md`, issue-local closure ledger, possible shipped skill docs evidence.
- 対応:
  - Issue187 expectation supersession、provider/mirror resolution、Evidence Adoption Ledger、Closure Delta、Step Commit Gate を記録する。
- doc update owner:
  - main orchestrator for canonical issue docs; doc-writer for any extra shipped docs.
- spec/doc review:
  - reviewer: spec-reviewer
  - pass 条件: docs が requirement / design / plan と整合し、未解決の必須 docs 影響が残らない。
- 具体テストケース:
  - `tc-s90-001` report records Issue187 supersession.
  - `tc-s90-002` report records provider/mirror resolution.
- no-op:
  - 追加 docs が不要な場合でも、不要理由と inspection evidence を report に残す。
- step gate:
  - step reviewer gate:
    - reviewer: spec-reviewer
    - review 範囲: report ledger、docs impact decision、Issue187 supersession evidence、provider/mirror resolution、closure coverage
    - pass 条件: `review_status: pass`
    - re-review rule: 指摘を修正し pass まで再実行
  - commit / no-op gate:
    - closure 状態: committed または approved-no-op
    - commit 範囲: S90 report/docs impact updates only
    - post-step clean check: `git status --short` で意図しない staged / unstaged 変更がないこと
    - no-op の場合: 追加変更不要の理由、確認した report/docs sections、差分なし確認コマンド、spec-reviewer pass を `report.md` に残す

### 最終品質ゲートステップ S99（final quality gate）
- branch diff 範囲:
  - Issue219 docs, tests, provider runtime, skill docs, mirror changes if any.
- 必須 validation:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "issue_219 or issue_187_s420 or issue_187_s430 or github-pr-observation or pr_observation"`
  - `uv run pytest tests/unit`
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
- final QA gate:
  - reviewer: qa-reviewer
  - 範囲: closure index coverage and integration test need.
  - pass 条件: reviewer pass.
- final code review ゲート:
  - reviewer: code-reviewer
  - 範囲: issue-wide integrated runtime/test/docs diff.
  - pass 条件: `review_status: pass`.
- final spec review ゲート:
  - reviewer: spec-reviewer
  - 範囲: requirement / design / plan / report / implementation / tests / docs alignment.
  - pass 条件: reviewer pass.
- final commit gate:
  - commit 範囲: final report ledger only if changed; no catch-up implementation.
  - final report ledger: all closure ids and reviewer gates.
  - post-commit external evidence destination: final response / PR / issue comment.

## 未確定事項
- Blocking question:
  - なし。
- Non-blocking implementation choices:
  - `decision.actionable_inventory_reason` を追加するかは S02 の最小差分で判断し、追加する場合は fingerprint/tests/docs を更新する。
  - Dogfooding mirror runtime files を S03 で同期するか、pending sync として report に残すかは実行時の accepted provider-to-mirror workflow に従う。

## 最終完了条件
- AC/EC 達成:
  - tc-001..tc-010 が report closure evidence で閉じている。
- docs 影響解決:
  - S03/S90 で skill docs と provider/mirror decision が記録されている。
- 全 implementation step 完了:
  - S01, S02, S03, S90 が committed または正当な approved-no-op。
- final quality gate pass:
  - qa-reviewer: pass
  - issue-wide code-reviewer: pass
  - spec-reviewer: pass
- final commit 完了:
  - Final report ledger commit or approved no-op evidence.
- 必須 closure id 完了:
  - Step Contract Closure, Test Contract Closure, Closure Coverage in `report.md`.
- final clean state:
  - no unintended staged / unstaged changes after final commit.
