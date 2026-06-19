---
種別: 実装計画書（Issue）
ID: "iss-00214"
タイトル: "PR Observation Review Target State"
関連GitHub: ["#214"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
依存: ["requirement.md", "design.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00214 PR Observation Review Target State — 実装計画

## この計画で満たす要件ID

- AC:
  - AC-001: no-signal wait state shows `review=pending_signal`.
  - AC-002: unresolved current review feedback shows `review=unresolved` with counts.
  - AC-003: final JSON `decision` / `decision_fingerprint` contract remains unchanged.
  - AC-004: provider-side source and dogfooding mirror stay aligned.
- EC:
  - EC-001: latency-guarded no-completion path remains wait / resume before promotion.
  - EC-002: `review_completion_unknown` human gate remains distinct from `pending_signal`.
  - EC-003: fallback issue comment semantics remain low-confidence human gate / wait_or_resume.
  - EC-004: progress line budget remains bounded.
- 制約:
  - `review=` must show target review state, not observer state.
  - `observer=` / `wait=` field is not added in this issue.
  - Trigger / resume / snapshot / token permission semantics are out of scope.

## 依存関係から導く実装順序

- 依存関係の参照元:
  - `design.md` の `依存関係分析`、`Module Dependency Diagram`、`ディレクトリ / ファイル変更計画`。
- 順序ルール:
  - Existing `review=observing` expectation を red target として先に固定する。
  - Provider-side display derivation を変更し、dogfooding mirror へ同等内容を反映する。
  - Focused regression tests で wait display、unresolved counts、final JSON no-completion path、line budget を確認する。
- step 依存サマリー:
  - S01:
    - 依存: approved `requirement.md`, approved `design.md`
    - unblock: S90 docs impact inspection, S99 final quality gate
    - 対象ファイル: PR observation wait provider/mirror script and focused tests
  - S90:
    - 依存: S01 implementation diff
    - unblock: S99 final spec review
    - 対象ファイル: PR observation skill docs if inspection shows required update
  - S99:
    - 依存: S01 and S90 complete
    - unblock: issue execution completion / PR delivery workflow
    - 対象ファイル: issue-wide diff and report evidence

## ステップ一覧

- S01:
  - 観測可能な振る舞い: wait progress line displays `review=pending_signal` for trigger-boundary no-signal wait state and preserves actionable review target states.
  - 依存: requirement/design approved.
  - unblock: docs impact inspection and final quality gate.
  - 対象ファイル:
    - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
    - `.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
    - `tests/unit/infra/test_init_update.py`
    - `spec-dock/active/issue/report.md`
  - 閉じる要件: AC-001, AC-002, AC-003, AC-004, EC-001, EC-002, EC-003, EC-004.
  - レビューゲート: code-reviewer pass before step commit.
- S90:
  - 観測可能な振る舞い: docs impact is explicitly resolved as update-needed or no-update with evidence.
  - 依存: S01 diff known.
  - unblock: S99 final spec review.
  - 対象ファイル:
    - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
    - `.agents/skills/github-pr-observation/SKILL.md`
    - `spec-dock/active/issue/report.md`
  - 閉じる要件: AC-003, AC-004.
  - レビューゲート: spec-reviewer docs/spec alignment pass.
- S99:
  - 観測可能な振る舞い: issue-wide quality gates pass and execution handoff readiness is recorded.
  - 依存: S01 committed, S90 resolved.
  - unblock: PR delivery / merge-prep / issue finish workflow.
  - 対象ファイル: issue-wide diff.
  - 閉じる要件: all AC / EC.
  - レビューゲート: qa-reviewer pass, issue-wide code-reviewer pass, final spec-reviewer pass.

## 要件 ↔ ステップ対応

- AC-001 -> S01
- AC-002 -> S01
- AC-003 -> S01, S90, S99
- AC-004 -> S01, S90
- EC-001 -> S01
- EC-002 -> S01
- EC-003 -> S01
- EC-004 -> S01

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ（step） | スライス（slice） | 種別（type） | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル（evidence level） | クロージャ証跡（closure evidence） |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | pending_signal progress display | acceptance | AC-001 | `phase=wait` no-signal state renders `review=pending_signal`, not `review=observing` | wait progress stderr for trigger/resume boundary with no review completion/comment signal | observer state leaks into target review state | yes | red-required | Step Contract Closure / Test Contract Closure |
| tc-002 | S01 | actionable review progress display | acceptance/regression | AC-002 | current unresolved feedback renders `review=unresolved` plus comments/threads/unresolved counts | wait or terminal progress stderr with unresolved Codex feedback | actionable review target state hidden by pending display | yes | covered-existing | Step Contract Closure / Test Contract Closure |
| tc-003 | S01 | final JSON authority preservation | regression | AC-003, EC-001, EC-002, EC-003 | `decision`, `decision_fingerprint`, `recommended_next_action`, no-completion and fallback semantics remain unchanged | stdout JSON for timeout, wait_or_resume, review_completion_unknown, fallback issue comment cases | display-only change mutates authoritative decision semantics | yes | covered-existing | Test Contract Closure |
| tc-004 | S01 | provider/mirror parity | structural | AC-004 | provider-side wait script and dogfooding mirror have equivalent progress display derivation | file inspection / diff of provider and mirror scripts | shipped asset and dogfooding behavior drift | yes | inspect-only | Closure Coverage |
| tc-005 | S90 | docs impact resolution | docs/spec | AC-003, AC-004 | PR observation skill docs either need no update with rationale or are updated consistently | inspection of provider and mirror `github-pr-observation/SKILL.md` | docs contract stale after progress display change | yes | inspect-only | Docs Impact Resolution |
| tc-006 | S99 | final handoff readiness | final gate | all AC/EC | QA/code/spec reviewers pass and report records handoff readiness | final reviewer results and report ledgers | execution proceeds with missing quality evidence | yes | inspect-only | Final Quality Gate |

## レビュー / QA ゲート方針

- S01 step review:
  - reviewer: `code-reviewer`
  - pass 条件: `review_status: pass`
  - focus: provider/mirror parity, progress display derivation, final JSON contract preservation, tests.
- S90 docs/spec review:
  - reviewer: `spec-reviewer`
  - pass 条件: `review_status: pass`
  - focus: docs impact resolution and spec consistency.
- S99 final QA:
  - reviewer: `qa-reviewer`
  - pass 条件: `review_status: pass`
  - focus: obligation coverage and whether integration/manual tests are needed.
- S99 final code review:
  - reviewer: `code-reviewer`
  - pass 条件: `review_status: pass`
  - focus: issue-wide integrated diff.
- S99 final spec review:
  - reviewer: `spec-reviewer`
  - pass 条件: `review_status: pass`
  - focus: requirement/design/plan/report and implementation alignment.

## 実行ルール（全ステップ共通）

- Observed evidence は `report.md` に記録し、`plan.md` へ実行結果を追記しない。
- `review=pending_signal` の exact derivation を変える必要が出た場合は、実装前に plan amendment と fresh spec review を行う。
- Final JSON decision semantics に触る必要が出た場合は、今回の scope を超えるため実装を停止し、requirement/design へ戻す。
- Provider-side source と dogfooding mirror は同じ behavior を保つ。

## 実装ステップ

### 実装ステップ S01 — Target review progress display

- 振る舞いの目標:
  - Wait progress line の `review=` が target Codex review state を表示し、no-signal wait state では `pending_signal` を表示する。
- design 参照:
  - `pending_signal 導出方針`
  - `インターフェース契約`
  - `ディレクトリ / ファイル変更計画`
- 依存:
  - approved `requirement.md`
  - approved `design.md`
- unblock:
  - S90, S99
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `tests/unit/infra/test_init_update.py`
  - `spec-dock/active/issue/report.md`
- 計画済み契約:
  - scope:
    - `progress_line(...)` の review display derivation。
    - Focused tests for pending signal, unresolved counts, decision preservation, line budget.
  - テスト義務:
    - closure id: tc-001, tc-002, tc-003, tc-004
    - coverage rationale:
      - AC-001 は existing `review=observing` expectation を red target にできる。
      - AC-002 / EC-004 は existing progress/count/line-budget tests で regression sensitivity を持つ。
      - AC-003 / EC-001 / EC-002 / EC-003 は existing no-completion / fallback JSON tests で regression sensitivity を持つ。
      - AC-004 は provider/mirror inspection で閉じる。
  - Red / 代替証跡の要件:
    - red-required:
      - Existing `review=observing` assertion を `review=pending_signal` に変更し、実装前に失敗することを確認する。
    - covered-existing:
      - `test_issue_174_pr_observation_wait_compacts_terminal_ci_and_human_gate_review`
      - `test_issue_187_s204_wait_does_not_promote_unknown_before_trigger_age`
      - `test_issue_187_s204_wait_does_not_promote_unknown_before_ci_passed_age`
      - `test_issue_187_s204_wait_resume_preserves_prior_ci_passed_age`
      - `test_issue_187_s204_wait_promotes_unknown_after_trigger_and_ci_ages`
      - `test_issue_187_s204_wait_late_unresolved_review_overrides_unknown_candidate`
      - `test_issue_176_s04_wait_fallback_issue_comment_does_not_request_review_feedback`
      - `test_issue_187_s100_fallback_issue_comment_is_not_no_completion_evidence`
      - `test_issue_174_pr_observation_wait_preserves_output_boundary_and_line_budget`
    - inspect-only:
      - Provider and mirror wait script display derivation match.
  - 実装範囲:
    - allowed paths:
      - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
      - `.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
      - `tests/unit/infra/test_init_update.py`
      - `spec-dock/active/issue/report.md`
    - forbidden changes:
      - `trigger_codex_review.sh`, `fetch_pr_observation_snapshot.sh`, `pr_observation_snapshot.py`, `pr_review_snapshot.py`
      - GitHub auth / token permission behavior
      - final JSON decision schema / fingerprint semantics
      - unrelated tests or broad refactors
  - Green 検証:
    - Focused red/green command:
      - `uv run pytest tests/unit/infra/test_init_update.py -k "issue_176_s04_wait_ci_passed_codex_review_pending_times_out_with_resume_hint or issue_174_pr_observation_wait_compacts_terminal_ci_and_human_gate_review or issue_174_pr_observation_wait_preserves_output_boundary_and_line_budget or issue_187_s204_wait or issue_176_s04_wait_fallback_issue_comment_does_not_request_review_feedback or issue_187_s100_fallback_issue_comment_is_not_no_completion_evidence"`
    - Structural:
      - `rg -n "review=observing|pending_signal|render_review" src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py .agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py tests/unit/infra/test_init_update.py`
  - Refactor / cleanup ガードレール:
    - 目的:
      - Display derivation stays readable and local.
    - 禁止する広がり:
      - Classification / decision rewrite, trigger flow changes, broad fixture rewrites.
  - closure 証跡要件:
    - Step Contract Closure: S01 closes tc-001 through tc-004.
    - Test Contract Closure: red evidence, green focused pytest, structural inspection.
    - Closure Coverage: AC/EC mapping remains complete.
  - report 証跡の記録先:
    - `report.md` TDD evidence
    - Step Contract Closure
    - Test Contract Closure
    - Closure Coverage
    - Reviewer Gate Status
    - Step Commit Gate
  - amendment trigger:
    - Need to change final JSON decision semantics.
    - Need to add observer/wait field.
    - Need to change trigger / resume / snapshot behavior.
    - `pending_signal` cannot be derived without weakening AC-001 or AC-003.
    - QA/final review discovers a no-completion wait payload shape that requires adding a new `review_status` candidate outside `none` / `pending` / `unknown`; in that case amend design/plan and rerun fresh spec review before final handoff.

#### 委任契約（delegation contract）

- delegated role:
  - `dev-coder`
- input docs:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/phase_plan_issue.md`
  - `spec-dock/docs/authoring/issue-plan.md`
  - target files listed above
- allowed paths:
  - Same as S01 implementation scope.
- forbidden changes:
  - Same as S01 forbidden changes.
- acceptance criteria:
  - `tc-001` through `tc-004` pass or are closed with planned inspection evidence.
- required tests or docs-only verification:
  - Focused pytest command listed in Green 検証.
  - Provider/mirror structural `rg` inspection.
- reviewer focus:
  - `code-reviewer` for runtime/tests/scaffold behavior.
- output required:
  - changed files
  - red evidence result
  - green verification result
  - provider/mirror parity note
  - unresolved risks
  - `Ledger Note` or `No material implementation decisions beyond the approved plan.`
- stop conditions:
  - Requirement/design conflict.
  - Need to change forbidden paths.
  - Focused tests cannot run.
  - `pending_signal` derivation would alter final JSON decision semantics.

#### 具体テストケース一覧

- `tc-s01-001` acceptance: no-signal wait progress uses pending_signal
  - 前提: Existing fixture produces wait-phase payload where CI passed, review status is `none` or `pending`, lifecycle is pending/none, and no Codex completion/comment signal exists.
  - 追加前提: Existing latency-guard no-completion fixture may report legacy `approved` / `passed` review status without a trusted Codex completion signal; this is still a no-signal wait display state and must render `review=pending_signal` while final JSON remains wait/resume / non-terminal.
  - 操作: Update the existing `test_issue_176_s04_wait_ci_passed_codex_review_pending_times_out_with_resume_hint` expectation before implementation.
  - 期待結果: Pre-implementation run fails because stderr still contains `review=observing`; post-implementation run passes with `review=pending_signal`.
  - 失敗検出: Observer state remains displayed in `review=`.
  - 検証方法: Focused `uv run pytest ... -k "issue_176_s04_wait_ci_passed_codex_review_pending_times_out_with_resume_hint or issue_187_s204_wait_does_not_promote_unknown_before_trigger_age"`.
  - 関連 closure id: tc-001
- `tc-s01-002` regression: unresolved feedback keeps unresolved target state and counts
  - 前提: Existing issue 174 fixture contains current unresolved Codex review feedback with review comments and threads.
  - 操作: Run `test_issue_174_pr_observation_wait_compacts_terminal_ci_and_human_gate_review`.
  - 期待結果: stderr contains `review=unresolved`, `comments=2`, `threads=2`, and `unresolved=2`.
  - 失敗検出: `pending_signal` masks actionable unresolved state or drops counts.
  - 検証方法: Focused pytest including issue 174 human-gate review test.
  - 関連 closure id: tc-002
- `tc-s01-003` regression: final JSON no-completion and fallback semantics stay unchanged
  - 前提: Existing issue 187 no-completion tests cover latency guards and `review_completion_unknown`; existing issue 176 / issue 187 fallback tests cover fallback issue comment `human_gate` and `wait_or_resume`.
  - 操作: Run focused issue 187 S204 tests plus `test_issue_176_s04_wait_fallback_issue_comment_does_not_request_review_feedback` and `test_issue_187_s100_fallback_issue_comment_is_not_no_completion_evidence`.
  - 期待結果: Existing stdout JSON assertions continue to pass.
  - 失敗検出: Display-only change mutates `decision`, `decision_fingerprint`, `recommended_next_action`, or `observation_complete`.
  - 検証方法: Focused pytest including `issue_187_s204_wait`, `issue_176_s04_wait_fallback_issue_comment_does_not_request_review_feedback`, and `issue_187_s100_fallback_issue_comment_is_not_no_completion_evidence`.
  - 関連 closure id: tc-003
- `tc-s01-004` structural: provider and mirror use equivalent display derivation
  - 前提: Provider-side source and dogfooding mirror both contain `pr_observation_wait.py`.
  - 操作: Inspect both files for `pending_signal` and absence of `render_review = "observing"`.
  - 期待結果: Both files contain the same display derivation behavior.
  - 失敗検出: Shipped asset and local dogfooding behavior diverge.
  - 検証方法: `rg -n "review=observing|pending_signal|render_review" ...`.
  - 関連 closure id: tc-004

#### ステップ完了契約（step closure contract）

- closure id:
  - tc-001
  - tc-002
  - tc-003
  - tc-004
- close 条件:
  - Red evidence confirms existing `review=observing` expectation fails after test update and before implementation, unless implementation and test are intentionally batched with documented characterization evidence.
  - Focused pytest passes after implementation.
  - Structural inspection confirms provider/mirror parity.
  - `code-reviewer` returns `review_status: pass`.
  - Step commit is created and post-commit worktree is clean except intentional next-step artifacts.
- report evidence:
  - TDD evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate.
- 残リスク:
  - Live GitHub/Codex timing behavior still depends on external service signals; this issue fixes local display contract and regression coverage.

#### ステップゲート（step gate）

- step reviewer gate:
  - reviewer: `code-reviewer`
  - review 範囲: S01 changed runtime/test/mirror files and report evidence.
  - pass 条件: `review_status: pass`
  - re-review rule: findings are fixed and fresh `code-reviewer` pass is obtained before commit.
- commit / no-op gate:
  - closure 状態: `committed`
  - commit 範囲: S01 implementation, tests, mirror parity, and S01 report evidence only.
  - no-op: not allowed for S01 because behavior change is required.

### ドキュメント影響の解消ステップ S90 — Docs impact resolution

- 対象:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - `.agents/skills/github-pr-observation/SKILL.md`
  - `spec-dock/active/issue/report.md`
- 対応:
  - Inspect whether the skill docs already state enough: progress is non-authoritative, bounded key/value summary, final JSON authoritative, no manual `@codex review`.
  - If docs do not mention a conflicting `review=observing` contract, record no-update rationale.
  - If S01 changes public progress vocabulary enough to require docs, update provider-side skill doc and mirror consistently.
- doc update owner:
  - `doc-writer` if docs update is required.
  - `N/A` approved-no-op if inspection proves no docs update is required.
- verification:
  - `rg -n "observing|pending_signal|progress lines|review" src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md .agents/skills/github-pr-observation/SKILL.md`
- spec/doc review:
  - reviewer: `spec-reviewer`
  - pass 条件: docs impact evidence aligns with requirement/design/plan and no stale public docs contract remains.

### 最終品質ゲートステップ S99 — Final quality gate

- branch diff 範囲:
  - All issue branch changes since base, including specs, discussion evidence, implementation, tests, mirror updates, and report evidence.
- 必須 validation:
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync --github`
  - Focused pytest from S01.
- final QA gate:
  - reviewer: `qa-reviewer`
  - 範囲: Issue obligation coverage, missing high-value tests, manual/integration need.
  - pass 条件: `review_status: pass`
- final code review gate:
  - reviewer: `code-reviewer`
  - 範囲: issue-wide integrated runtime/test/mirror diff.
  - pass 条件: `review_status: pass`
- final spec review gate:
  - reviewer: `spec-reviewer`
  - 範囲: requirement / design / plan / report / implementation / tests / docs alignment.
  - pass 条件: `review_status: pass`
- final commit gate:
  - commit 範囲:
    - Final report ledger and any final evidence-only adjustments.
  - final report ledger:
    - All closure ids tc-001 through tc-006 closed.
    - S01 committed, S90 resolved, S99 reviews passed.
  - post-commit external evidence destination:
    - Final response / PR body / issue comment as applicable.

## 最終完了条件

- AC/EC 達成:
  - AC-001 through AC-004 and EC-001 through EC-004 have closure evidence.
- docs 影響解決:
  - S90 records docs update or no-update rationale with spec-reviewer pass.
- 全 implementation step 完了:
  - S01 committed.
- final quality gate pass:
  - qa-reviewer pass.
  - issue-wide code-reviewer pass.
  - spec-reviewer pass.
- final commit 完了:
  - Final report ledger committed or external final evidence records final commit boundary.
- 必須 closure id 完了:
  - tc-001 through tc-006 closed in report Step Contract Closure / Test Contract Closure / Closure Coverage.
- final clean state:
  - no unintended staged / unstaged changes.
