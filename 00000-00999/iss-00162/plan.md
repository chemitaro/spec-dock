---
種別: 実装計画書（Issue）
ID: "iss-00162"
タイトル: "Align Skill Docs Template Context Surfaces"
関連GitHub: ["#162"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
依存: ["requirement.md", "design.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00162 Align Skill Docs Template Context Surfaces — 実装計画

## この計画で満たす要件ID

- AC:
  - AC-001, AC-002, AC-003, AC-004, AC-005
- EC:
  - EC-001, EC-002, EC-003
- 制約:
  - Runtime gate / CLI enforcement / automated harness は作らない。
  - Downstream owner issue の rewrite scope を吸収しない。
  - Provider source を正本、dogfooding mirror を verification target とする。

## 依存関係から導く実装順序

- 依存関係の正本:
  - `design.md` の inventory flow と file change plan。
- step 依存サマリー:
  - S01 inventory matrix:
    - 依存: passed requirement/design
    - unblock: S02
    - 対象ファイル: `spec-dock/active/issue/discussions/<ts>-disc-context-surface-inventory.md`
  - S02 bounded hub wording cleanup:
    - 依存: S01 inventory matrix
    - unblock: S90, S99
    - 対象ファイル:
      - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
      - `.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - S90 docs impact:
    - 依存: S01, S02
    - unblock: S99
  - S99 final quality gate:
    - 依存: S01, S02, S90

## ステップ一覧

- S01:
  - 観測可能な振る舞い: 後続 issue が surface ownership と handoff owner を判断できる inventory / trace matrix が存在する。
  - 閉じる要件: AC-001, AC-002, AC-005, EC-001, EC-002, EC-003
  - レビューゲート: `spec-reviewer`
- S02:
  - 観測可能な振る舞い: hub first-read wording から、skills/docs/templates boundary が Epic ADR と矛盾なく読める。
  - 閉じる要件: AC-002, AC-003, AC-004
  - レビューゲート: `spec-reviewer`
- S90:
  - 観測可能な振る舞い: docs/templates/runtime 影響が unresolved で残っていない。
  - 閉じる要件: docs impact
  - レビューゲート: `spec-reviewer`
- S99:
  - 観測可能な振る舞い: issue-wide diff, reports, validation, reviewer gates が完了している。
  - 閉じる要件: all
  - レビューゲート: `qa-reviewer`, `code-reviewer`, `spec-reviewer`

## 要件 ↔ ステップ対応

- AC-001 -> S01
- AC-002 -> S01, S02
- AC-003 -> S02
- AC-004 -> S02, S90, S99
- AC-005 -> S01
- EC-001 -> S01
- EC-002 -> S01
- EC-003 -> S01

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子 | ステップ | スライス | 種別 | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル | クロージャ証跡 |
|---|---|---|---|---|---|---|---|---|---|---|
| cl-001 | S01 | inventory coverage | acceptance | AC-001 | provider skills/docs/templates が matrix に分類される | discussion matrix | hidden contradiction | yes | inspect-only | Step Contract Closure / Test Contract Closure / Closure Coverage |
| cl-002 | S01 | downstream handoff | acceptance | AC-002, AC-005 | contradiction rows have owner issue and action/defer reason | discussion matrix | owner ambiguity | yes | inspect-only | Step Contract Closure / Test Contract Closure / Closure Coverage / Evidence Adoption Ledger |
| cl-003 | S01 | scope split | edge | EC-001 | broad rewrite scope is split or handed off | discussion matrix/report | scope absorption | yes | inspect-only | Step Contract Closure / Test Contract Closure / Closure Coverage / Closure Delta |
| cl-004 | S01 | docs/template classification | edge | EC-002, EC-003 | docs hidden workflow and template authority risks are classified | discussion matrix | docs/templates authority drift | yes | inspect-only | Step Contract Closure / Test Contract Closure / Closure Coverage |
| cl-005 | S02 | hub wording cleanup | acceptance | AC-003 | hub wording says skills carry first-read spine and docs/templates carry details/scaffold | hub skill text | stale boundary wording | yes | inspect-only | Step Contract Closure / Test Contract Closure / Closure Coverage |
| cl-006 | S02 | no iss-00164 absorption | negative | AC-002 | route table / clarification routing / leaf ownership restructuring are unchanged | diff inspection | downstream scope theft | yes | inspect-only | Step Contract Closure / Test Contract Closure / Closure Coverage / Closure Delta |
| cl-007 | S02 | provider/mirror parity | regression | AC-004 | provider and mirror hub skill are byte-equivalent | `cmp` and parity unittest | stale mirror | yes | covered-existing | Step Contract Closure / Test Contract Closure / Closure Coverage / Step Commit Gate |
| cl-008 | S90 | docs impact resolved | final | AC-004 | `sync`, validate, and docs impact review pass | commands/report | stale derived views | yes | manual-required | Docs Impact Resolution / Reviewer Gate Status |
| cl-009 | S99 | final gates | final | all | QA/code/spec reviewers pass | reviewer outputs | incomplete issue | yes | manual-required | Final QA Gate / Final Code Review Gate / Final Spec Review Gate / Final Commit |

## 実装ステップ S01 — Context surface inventory / trace matrix

- 振る舞いの目標:
  - 後続 issue が、どの surface にどの ownership claim / contradiction があり、誰が修正するかを判断できる。
- 対象ファイル:
  - `spec-dock/active/issue/discussions/<ts>-disc-context-surface-inventory.md`
- 計画済み契約:
  - scope:
    - provider skills/docs/templates の inventory と trace matrix。
  - Red / 代替証跡:
    - code test 不要。discussion evidence と inspection で閉じる。
  - Green 検証:
    - `find src/spec_dock/assets/install_root/.agents/skills -maxdepth 2 -name SKILL.md | sort`
    - `find src/spec_dock/assets/spec_dock/docs -maxdepth 2 -type f | sort`
    - `find src/spec_dock/assets/spec_dock/templates -maxdepth 3 -type f | sort`
    - matrix に required columns があることを manual inspection。
  - Refactor / cleanup guardrail:
    - S01 では provider files を変更しない。
  - amendment trigger:
    - matrix が issue scope に収まらず、追加 issue split が必要。
- 委任契約:
  - delegated role: `doc-writer`
  - input docs / source of truth:
    - `requirement.md`
    - `design.md`
    - `plan.md`
    - `workflow_spec_authoring.md`
    - `workflow_issue.md`
    - `docs/authoring/issue-plan.md`
    - Epic ADRs listed in `requirement.md`
    - provider skills/docs/templates file lists
  - allowed paths:
    - exactly one new flat Markdown file under `spec-dock/active/issue/discussions/`
    - filename rule: `<ts>-disc-context-surface-inventory.md` or same-second collision `<ts>-01-disc-context-surface-inventory.md`
  - forbidden changes:
    - canonical docs, provider source, tests, runtime, GitHub metadata.
    - nested discussion directories, non-Markdown files, symlinks, deletes, renames, staged changes.
  - acceptance criteria:
    - cl-001..cl-004 pass.
  - required tests or docs-only verification:
    - file list commands in S01 Green verification.
    - manual inspection of matrix columns and downstream owner rows.
  - stop conditions:
    - input docs conflict.
    - required inventory cannot be scoped to one discussion file.
    - provider source changes appear necessary.
    - discussion filename/provenance/diff guard requirements cannot be met.
  - scope-local discussion direct-write contract:
    - required provenance fields: `created_by_role`, `scope_id`, `source_paths`, `intended_targets`, `adoption_status: unreviewed`, `reflected_to: []`, `diff_guard_result`.
    - intended target: `report.md` Evidence Adoption Ledger / Delegated Draft Evidence / Step Contract Closure.
    - fallback decision: if no valid discussion draft can be produced, stop and return to parent manual authoring; do not write canonical docs as fallback.
    - post-run diff guard: parent verifies exactly one new direct-child discussion Markdown file and no forbidden side effects with `git status --short` / `git diff --name-only`.
    - report destinations: Evidence Adoption Ledger, Delegated Draft Evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta, Reviewer Gate Status.
  - reviewer focus:
    - `spec-reviewer`
  - output required:
    - created discussion path, matrix coverage summary, unresolved risks, Ledger Note or no material decision.
- 具体テストケース一覧:
  - `tc-s01-001` inspect-only: inventory matrix has required columns
    - 前提: S01 discussion matrix exists.
    - 操作: matrix header and rows are inspected.
    - 期待結果: surface path / family / current claim / target ownership / contradiction / owner issue / action / evidence がある。
    - 失敗検出: downstream issue owner が推測に戻る regression を検出する。
    - 検証方法: manual inspection and `rg` for headers.
    - 関連 closure id: cl-001, cl-002
  - `tc-s01-002` inspect-only: downstream boundaries are explicit
    - 前提: Matrix includes clarification, hub, workflow docs, and templates rows.
    - 操作: owner issue columnを確認する。
    - 期待結果: `iss-00163`, `iss-00164`, `iss-00165`, `iss-00166` へ渡す rows がある。
    - 失敗検出: この issue が downstream rewrite を吸収する regression を検出する。
    - 検証方法: `rg 'iss-00163|iss-00164|iss-00165|iss-00166' <matrix>`.
    - 関連 closure id: cl-002, cl-003, cl-004
- ステップ完了契約:
  - close 条件: cl-001..cl-004 pass and step `spec-reviewer` pass.
  - commit / no-op gate: committed.

## 実装ステップ S02 — Bounded hub wording cleanup

- 振る舞いの目標:
  - Hub skill の first-read wording が、Epic ADR の skill/docs/templates boundary と矛盾しない。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `.agents/skills/spec-driven-tdd-workflow/SKILL.md`
- 計画済み契約:
  - scope:
    - stale wording `skills stay concise`, `docs are source of truth for workflow explanations` を、skills carry first-read workflow spine and docs carry detail/semantics に整える。
  - Red / 代替証跡:
    - docs-only text change; inspect-only evidence.
  - Green 検証:
    - `rg 'first-read workflow spine|details|templates as minimum authoring scaffolds|source of truth' src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md .agents/skills/spec-driven-tdd-workflow/SKILL.md`
    - negative inspection: stale wording must not say skills merely stay concise while docs own workflow explanations.
    - `cmp -s src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md .agents/skills/spec-driven-tdd-workflow/SKILL.md`
    - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets`
  - Forbidden:
    - route table changes
    - clarification routing changes
    - leaf ownership restructuring
    - broader hub rewrite owned by `iss-00164`
  - amendment trigger:
    - cleanup requires route table or leaf ownership changes.
- 委任契約:
  - delegated role: `doc-writer`
  - input docs / source of truth:
    - `requirement.md`
    - `design.md`
    - `plan.md`
    - S01 inventory matrix
    - `workflow_spec_authoring.md`
    - `workflow_issue.md`
    - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
    - `.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - allowed paths:
    - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
    - `.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - forbidden changes:
    - runtime, tests, templates, docs, other skills, route table rewrite.
    - clarification routing changes, leaf ownership restructuring, broader hub/leaf rewrite owned by `iss-00164`.
  - acceptance criteria:
    - cl-005..cl-007 pass.
  - required tests or docs-only verification:
    - S02 `rg` inspection.
    - provider/mirror `cmp`.
    - targeted dogfooding parity unittest.
    - diff inspection proving route table / clarification routing / leaf ownership blocks are unchanged.
  - stop conditions:
    - changing route table or clarification routing is required.
    - S01 matrix does not support the cleanup.
    - provider/mirror parity cannot be preserved.
    - verification cannot run.
  - reviewer focus:
    - `spec-reviewer`
  - output required:
    - changed files, verification, unresolved risks, Ledger Note or no material decision.
- 具体テストケース一覧:
  - `tc-s02-001` inspect-only: hub wording reflects boundary
    - 前提: provider/mirror hub skill are updated.
    - 操作: hub intro wording is inspected.
    - 期待結果: skill first-read spine / docs detail / templates scaffold が読める。
    - 失敗検出: docs-only source-of-truth wording が残る regression を検出する。
    - 検証方法: `rg` inspection.
    - 関連 closure id: cl-005
  - `tc-s02-002` negative inspect-only: iss-00164 scope is not consumed
    - 前提: S02 diff exists.
    - 操作: route table and clarification routing diffを確認する。
    - 期待結果: route table / clarification routing / leaf ownership restructuring は変更されていない。
    - 失敗検出: downstream hub issue の scope を先取りする regression を検出する。
    - 検証方法: `git diff -- ...spec-driven-tdd-workflow/SKILL.md`.
    - 関連 closure id: cl-006
  - `tc-s02-003` covered-existing: provider/mirror parity
    - 前提: provider/mirror hub skill updated.
    - 操作: `cmp` and parity unittest.
    - 期待結果: provider/mirror byte-equivalent and parity test passes.
    - 失敗検出: stale dogfooding mirror regression.
    - 検証方法: `cmp` and targeted unittest.
    - 関連 closure id: cl-007
- ステップ完了契約:
  - close 条件: cl-005..cl-007 pass and step `spec-reviewer` pass.
  - commit / no-op gate: committed.

## ドキュメント影響の解消ステップ S90

- 対象:
  - skill / discussions / generated projections
  - docs / templates / README / workflow docs as no-change surfaces unless S01/S02 discovers a blocker
- 対応:
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
  - report S90 evidence and no-change rationale.
- spec/doc review:
  - reviewer: `spec-reviewer`
  - pass 条件: docs impact resolved and no downstream owner scope consumed.

## 最終品質ゲートステップ S99

- branch diff 範囲:
  - inventory discussion
  - bounded hub skill cleanup
  - issue docs/report
- 必須 validation:
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
  - provider/mirror `cmp`
  - targeted parity unittest
- final QA gate:
  - reviewer: `qa-reviewer`
  - 範囲: closure coverage and integration test need.
  - pass 条件: reviewer pass.
- final code review gate:
  - reviewer: `code-reviewer`
  - 範囲: issue-wide diff, scope creep, provider/mirror parity, maintainability.
  - pass 条件: `review_status: pass`.
- final spec review gate:
  - reviewer: `spec-reviewer`
  - 範囲: requirement / design / plan / report / implementation / docs alignment.
  - pass 条件: reviewer pass.
- final commit gate:
  - commit 範囲: final report evidence only after S99.
  - post-commit external evidence destination: final response / PR body / issue finish evidence.

## 最終完了条件

- cl-001..cl-009 are pass in report.
- S01 and S02 are committed.
- S90 and S99 reviewer gates pass.
- Final report evidence is committed.
- `issue finish` can close GitHub issue #162 and clear active issue.
