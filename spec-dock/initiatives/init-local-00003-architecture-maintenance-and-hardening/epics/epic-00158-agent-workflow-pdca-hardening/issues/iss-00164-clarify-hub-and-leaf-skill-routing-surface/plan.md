---
種別: 実装計画書（Issue）
ID: "iss-00164"
タイトル: "Clarify Hub And Leaf Skill Routing Surface"
関連GitHub: ["#164"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
依存: ["requirement.md", "design.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00164 Clarify Hub And Leaf Skill Routing Surface — 実装計画

## この計画で満たす要件ID

- AC:
  - AC-001, AC-002, AC-003, AC-004, AC-005, AC-006
- EC:
  - EC-001, EC-002
- 制約:
  - Leaf skill rewrite は行わない。
  - Workflow docs / templates / runtime / validation logic は変更しない。
  - Provider source を正本、dogfooding mirror を verification target とする。

## ステップ一覧

- S01:
  - 観測可能な振る舞い: Hub skill が route matrix、surface ownership、global invariants を first-read surface として示す。
  - 対象ファイル:
    - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
    - `.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - 閉じる要件: AC-001, AC-002, AC-003, AC-004, AC-006, EC-001, EC-002
  - レビューゲート: `spec-reviewer`
- S90:
  - 観測可能な振る舞い: sync / validate / docs impact が unresolved で残っていない。
  - 閉じる要件: AC-005 / docs impact
  - レビューゲート: `spec-reviewer`
- S99:
  - 観測可能な振る舞い: issue-wide QA/code/spec final gates が pass し、issue finish 可能な report になっている。
  - 閉じる要件: all
  - レビューゲート: `qa-reviewer`, `code-reviewer`, `spec-reviewer`

## 要件 ↔ ステップ対応

- AC-001 -> S01
- AC-002 -> S01
- AC-003 -> S01
- AC-004 -> S01
- AC-005 -> S90, S99
- AC-006 -> S01
- EC-001 -> S01
- EC-002 -> S01

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子 | ステップ | スライス | 種別 | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル | クロージャ証跡 |
|---|---|---|---|---|---|---|---|---|---|---|
| cl-001 | S01 | route matrix | acceptance | AC-001 | hub lists all required task-type -> leaf routes | hub skill text | ambiguous routing | yes | inspect-only | Step Contract Closure / Test Contract Closure / Closure Coverage |
| cl-002 | S01 | clarification route | acceptance | AC-003 | clarification routes to skill-owned source-grounded workflow | hub skill text | docs-owned clarification regression | yes | inspect-only | Step Contract Closure / Test Contract Closure / Closure Coverage |
| cl-003 | S01 | hub/leaf boundary | acceptance | AC-002, AC-004, EC-001 | hub is router + global invariant; leaf skills own workflow spine; no leaf rewrite | hub skill text / diff scope | scope creep into leaf details | yes | inspect-only | Step Contract Closure / Test Contract Closure / Closure Coverage |
| cl-004 | S01 | global invariants | acceptance | AC-006 | fresh reviewer pass, non-pass states, canonical ownership, evidence adoption remain cross-cutting invariants | hub skill text | unsafe phase promotion | yes | inspect-only | Step Contract Closure / Test Contract Closure / Closure Coverage |
| cl-005 | S01 | provider/mirror parity | regression | AC-005 | provider and mirror hub skill are byte-equivalent | `cmp` and parity unittest | stale mirror | yes | covered-existing | Step Contract Closure / Test Contract Closure / Closure Coverage |
| cl-006 | S90 | docs impact resolved | final | AC-005 | `sync`, `validate`, `git diff --check` pass | commands/report | stale projections | yes | manual-required | Docs Impact Resolution / Reviewer Gate Status |
| cl-007 | S99 | final gates | final | all | QA/code/spec reviewers pass and final report is committed | reviewer outputs | incomplete issue | yes | manual-required | Final QA Gate / Final Code Review Gate / Final Spec Review Gate / Final Commit |

## 実装ステップ S01 — Hub route and invariant surface

- 振る舞いの目標:
  - Agent が `spec-driven-tdd-workflow/SKILL.md` を読むだけで、route matrix、hub/leaf responsibility boundary、global invariants を把握できる。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `.agents/skills/spec-driven-tdd-workflow/SKILL.md`
- 計画済み契約:
  - allowed changes:
    - hub opening bullets / route table / quick reminders の整理。
    - route matrix wording。
    - skill-owned clarification route wording。
    - global invariant wording。
  - forbidden changes:
    - leaf skills。
    - workflow docs / templates。
    - runtime / tests except existing parity smoke execution。
  - Red / 代替証跡:
    - pre-change hub text is inspected for route / boundary / invariant wording; implementation is docs-only and inspect-only.
  - Green 検証:
    - route target existence:
      - `test -f src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`
      - `test -f src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
      - `test -f src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
      - `test -f src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
      - `test -f src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md`
      - `test -f src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md`
      - `test -f src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md`
      - `test -f src/spec_dock/assets/install_root/.agents/skills/spec-dock-adr-facilitation/SKILL.md`
      - `test -f .agents/skills/spec-dock-initiative-planning/SKILL.md`
      - `test -f .agents/skills/spec-dock-epic-planning/SKILL.md`
      - `test -f .agents/skills/spec-dock-issue-planning/SKILL.md`
      - `test -f .agents/skills/spec-dock-issue-execution/SKILL.md`
      - `test -f .agents/skills/spec-dock-clarification/SKILL.md`
      - `test -f .agents/skills/spec-dock-system-architect/SKILL.md`
      - `test -f .agents/skills/spec-dock-implementation-planner/SKILL.md`
      - `test -f .agents/skills/spec-dock-adr-facilitation/SKILL.md`
    - `gh issue view 163 --json state --jq '.state'`
    - `git log --oneline --grep 'final gate証跡を記録'`
    - `rg -n 'entry/routing skill|route selector|global invariant' src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md .agents/skills/spec-driven-tdd-workflow/SKILL.md`
    - `rg -n 'leaf skills own the first-read spine|docs own detailed semantics|templates.*not compliance authorities' src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md .agents/skills/spec-driven-tdd-workflow/SKILL.md`
    - `rg -n 'spec-dock-initiative-planning|spec-dock-epic-planning|spec-dock-issue-planning|spec-dock-issue-execution|spec-dock-clarification|spec-dock-system-architect|spec-dock-implementation-planner|spec-dock-adr-facilitation' src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md .agents/skills/spec-driven-tdd-workflow/SKILL.md`
    - `rg -n 'skill-owned|source-grounded clarification|source-grounded ambiguity' src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md .agents/skills/spec-driven-tdd-workflow/SKILL.md`
    - `rg -n 'fresh .*spec-reviewer|Missing, stale, failed, unavailable, denied, waived, or provisional|canonical docs.*main orchestrator|evidence.*canonical' src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md .agents/skills/spec-driven-tdd-workflow/SKILL.md`
    - negative inspection:
      - `rg -n 'docs.*source of truth.*workflow|compliance authority|must pass validation|leaf workflow details live here' src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md .agents/skills/spec-driven-tdd-workflow/SKILL.md` must return no stale authority/scope-creep matches.
    - `cmp -s src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md .agents/skills/spec-driven-tdd-workflow/SKILL.md`
    - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets`
  - Refactor / cleanup guardrail:
    - Keep the diff limited to the two hub skill files and report evidence.
    - Do not modify leaf skills, docs, templates, runtime, or tests in S01.
  - report evidence destination:
    - TDD / Red-Green-Refactor Evidence
    - Step Contract Closure
    - Test Contract Closure
    - Closure Coverage / Closure Delta
    - Reviewer Gate Status
    - Step Commit Gate
  - close 条件:
    - cl-001..cl-005 pass, route target / `iss-00163` dependency evidence recorded for EC-002, Parent Implementation Exception evidence recorded if parent-local edit is used, and fresh `spec-reviewer` pass.
  - commit gate:
    - committed.
  - delegation contract:
    - delegated role: N/A / parent-local skill edit is permitted only with explicit Parent Implementation Exception evidence because the write set is exactly two mirror skill files and the step is blocked on fresh `spec-reviewer`.
    - input docs: `requirement.md`, `design.md`, `plan.md`, provider/mirror hub skill.
    - allowed paths: the two S01 target files only.
    - forbidden changes: leaf skills, docs, templates, runtime, tests.
    - acceptance criteria: cl-001, cl-002, cl-003, cl-004, cl-005.
    - required tests or docs-only verification: all S01 Green verification commands, S01 negative inspection, `cmp`, targeted parity unittest, and diff inspection proving no outside-path changes.
    - Parent Implementation Exception evidence when parent-local edit is used:
      - delegation unavailable / impossible reason: bounded two-file text edit is faster and less risky than creating a delegated worker branch for a hub wording-only change.
      - user approval / risk acceptance: execution-time report must record the concrete approval source for parent-local direct editing; if no concrete approval source can be cited, do not use the parent-local exception and delegate the text edit to `doc-writer`.
      - allowed files: the two S01 target files only.
      - allowed operation: bounded text edit to hub wording.
      - rollback plan: revert the two hub skill files to pre-S01 state if reviewer fails.
      - post-change verification: S01 Green commands, negative inspection, `cmp`, parity unittest, diff inspection.
      - reviewer gate: fresh `spec-reviewer`.
      - unavailable / denied / host conflict / waiver handling: no waiver; if parent-local exception approval is absent, denied, or ambiguous, delegate the text edit to `doc-writer` before implementation.
    - reviewer focus: route matrix completeness, hub/leaf boundary, global invariant minimality, provider/mirror parity, no leaf rewrite.
    - stop conditions: route target does not exist; wording requires leaf skill rewrite; provider/mirror parity cannot be preserved; user-intent clarification becomes blocking.
    - required output: changed files, command results, stale wording negative inspection, unresolved risks.
  - concrete test cases:
    - `tc-s01-001` inspect-only: route matrix is present.
      - 前提: S01 target hub skill files are updated.
      - 操作: run route target existence commands and route target `rg` command.
      - 期待結果: all route target skill files exist in provider/mirror and all route target skill names are present in provider and mirror hub files.
      - 失敗検出: missing route target means route correctness cannot be externally verified.
      - 検証方法: route target `test -f` commands and route target `rg -n` command listed in S01 Green verification.
      - related closure id: cl-001.
    - `tc-s01-002` inspect-only: clarification route remains skill-owned.
      - 前提: S01 target hub skill files are updated.
      - 操作: run clarification `skill-owned|source-grounded...` `rg` command and stale authority negative command.
      - 期待結果: positive route wording is present; stale docs-owned workflow authority wording is absent.
      - 失敗検出: hub routes clarification back to docs-owned runbook authority.
      - 検証方法: clarification positive `rg` and negative inspection command.
      - related closure id: cl-002.
    - `tc-s01-003` inspect-only: hub/leaf boundary and global invariants are present.
      - 前提: S01 target hub skill files are updated.
      - 操作: run ownership and global invariant `rg` commands.
      - 期待結果: hub states leaf spine / docs semantics / template scaffold boundary and reviewer/canonical/evidence invariants.
      - 失敗検出: hub either omits cross-cutting safety rules or absorbs leaf details.
      - 検証方法: ownership and global invariant `rg -n` commands.
      - related closure id: cl-003, cl-004.
    - `tc-s01-004` covered-existing: hub provider/mirror parity.
      - 前提: S01 target hub skill files are updated.
      - 操作: run `cmp` and targeted parity unittest.
      - 期待結果: `cmp` exits 0 and unittest passes.
      - 失敗検出: stale dogfooding mirror or install-root mismatch.
      - 検証方法: `cmp -s ...`; `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets`.
      - related closure id: cl-005.
    - `tc-s01-005` inspect-only: `iss-00163` prerequisite is completed.
      - 前提: `iss-00163` has been finished before this issue implementation.
      - 操作: run `gh issue view 163 --json state --jq '.state'` and `git log --oneline --grep 'final gate証跡を記録'`.
      - 期待結果: GitHub issue state is `CLOSED` and local git history has the `iss-00163` final gate evidence commit.
      - 失敗検出: clarification route depends on incomplete or stale prerequisite.
      - 検証方法: `gh issue view` and `git log --oneline --grep 'final gate証跡を記録'`.
      - related closure id: cl-002, cl-003, EC-002.

## ドキュメント影響の解消ステップ S90

- 対象:
  - hub skill / generated projections。
- 対応:
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
  - report S90 evidence and no-change rationale for leaf skills / docs / templates / runtime.
- spec/doc review:
  - reviewer: `spec-reviewer`
  - pass 条件: cl-006 pass.
- execution contract:
  - delegated role: N/A / parent-local verification step.
  - allowed paths: `spec-dock/.agent/*`, `spec-dock/*.puml`, `spec-dock/dashboard.md`, and `report.md` evidence updates only if `sync` rewrites projections.
  - forbidden changes: provider/runtime/docs/templates/leaf skills changes beyond S01 without returning to S01.
  - acceptance criteria: cl-006.
  - required tests or docs-only verification: `sync`, `validate`, `git diff --check`, and `git status --short` inspection.
  - reviewer focus: generated projections, docs impact completeness, no unresolved leaf/docs/templates/runtime impact.
  - report evidence destination: Docs Impact Resolution, Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate.
  - stop conditions: `sync` rewrites unexpected provider assets; `validate` fails; diff-check fails; user-intent clarification becomes blocking.
  - concrete test case:
    - `tc-s90-001` manual-required: docs impact resolved.
      - 前提: S01 is committed.
      - 操作: run `./spec-dock/scripts/spec-dock sync`, `./spec-dock/scripts/spec-dock validate`, `git diff --check`, and inspect `git status --short`.
      - 期待結果: commands pass; any generated projection diff is expected and recorded; no unresolved docs/templates/runtime impact remains.
      - 失敗検出: stale projections or hidden docs/runtime impact.
      - 検証方法: the three commands and status inspection.
      - related closure id: cl-006.

## 最終品質ゲートステップ S99

- branch diff 範囲:
  - issue start / planning commit から HEAD。
- 必須 validation:
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
  - provider/mirror parity command evidence already recorded.
- final QA gate:
  - reviewer: `qa-reviewer`
  - 範囲: Issue 全体の obligation coverage と docs/skill-only verification adequacy。
- final code review:
  - reviewer: `code-reviewer`
  - 範囲: issue-wide integrated diff、provider/mirror consistency、scope absorption、stale wording。
- final spec review:
  - reviewer: `spec-reviewer`
  - 範囲: requirement / design / plan / report / implementation / tests / docs alignment。
- final commit gate:
  - final report ledger committed.
- execution contract:
  - delegated role: N/A for local final report updates; reviewers are `qa-reviewer`, `code-reviewer`, and `spec-reviewer`.
  - allowed paths: `report.md` final gate evidence only after S01/S90 commits.
  - forbidden changes: implementation/docs/template/leaf content changes after final reviewers unless returning to the relevant step and re-running gates.
  - acceptance criteria: cl-007.
  - required tests or docs-only verification: final `validate`, `git diff --check`, issue-wide diff inspection, QA/code/spec reviewer pass evidence.
  - reviewer focus: obligation coverage, provider/mirror parity, no scope absorption, report consistency, issue finish readiness.
  - report evidence destination: Final QA Gate, Final Code Review Gate, Final Spec Review Gate, Final Commit.
  - stop conditions: any final reviewer fails; report ledger contradiction; user-intent clarification becomes blocking.
  - concrete test case:
    - `tc-s99-001` manual-required: final gates and report commit.
      - 前提: S01 and S90 are committed.
      - 操作: run final validation commands, obtain QA/code/spec reviewer passes, update and commit final report ledger.
      - 期待結果: all reviewer gates pass and final report commit leaves worktree clean.
      - 失敗検出: incomplete closure evidence or final issue finish blocker.
      - 検証方法: reviewer outputs, `./spec-dock/scripts/spec-dock validate`, `git diff --check`, `git status --short`.
      - related closure id: cl-007.

## 未確定事項

- Blocking question:
  - なし。
- Amendment trigger:
  - Hub route matrix requires leaf skill rewrite。
  - Hub skill cannot remain provider/mirror byte-equivalent。
  - Runtime/docs/templates changes become necessary to satisfy the issue.

## 最終完了条件

- AC-001..AC-006 / EC-001..EC-002 達成。
- cl-001..cl-007 が pass。
- S01/S90/S99 reviewer gates pass。
- All changes committed and `issue finish` succeeds。
