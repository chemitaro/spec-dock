---
種別: 実装計画書（Issue）
ID: "iss-00159"
タイトル: "Make Issue Planning Skill Expose Mandatory Authoring Gates"
関連GitHub: ["#159"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
依存: ["requirement.md", "design.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00159 Make Issue Planning Skill Expose Mandatory Authoring Gates — 実装計画

## この計画で満たす要件ID

- AC:
  - AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007, AC-008, AC-009
- EC:
  - EC-001, EC-002, EC-003
- 制約:
  - Runtime gate / CLI / validation logic は変更しない。
  - Skill は detailed schema を複製せず、docs へ誘導する。
  - Provider-side source と dogfooding mirror は byte-equivalent にする。

## 依存関係から導く実装順序

- 依存関係の正本:
  - `design.md` の provider -> mirror -> agent -> docs routing dependency。
- 順序ルール:
  - まず provider skill と mirror skill を同一内容で更新する。
  - その後に docs 影響を解消し、最後に issue-wide gate を通す。
- step 依存サマリー:
  - S01:
    - 依存: reviewer-pass 済み `requirement.md` / `design.md`
    - unblock: S90, S99
    - 対象ファイル:
      - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
      - `.agents/skills/spec-dock-issue-planning/SKILL.md`
  - S90:
    - 依存: S01
    - unblock: S99
    - 対象ファイル: docs / templates / README / workflow / skill impact inspection
  - S99:
    - 依存: S01, S90
    - unblock: issue finish / PR delivery
    - 対象ファイル: issue-wide diff and reports

## ステップ一覧

- S01:
  - 観測可能な振る舞い: `spec-dock-issue-planning` skill を読んだ agent が mandatory issue authoring gates を first-read surface だけで識別できる。
  - 依存: passed requirement/design
  - unblock: S90, S99
  - 対象ファイル: provider skill, dogfooding mirror skill
  - 閉じる要件: AC-001..AC-009, EC-001..EC-003
  - レビューゲート: docs/spec alignment `spec-reviewer`
- S90:
  - 観測可能な振る舞い: 追加 docs 影響が unresolved で残っていない。
  - 依存: S01
  - unblock: S99
  - 対象ファイル: docs/templates/README/workflow/skill impact surface
  - 閉じる要件: EC-003, docs impact
  - レビューゲート: `spec-reviewer`
- S99:
  - 観測可能な振る舞い: issue-wide diff が requirement/design/plan/report と整合し、required verification が pass している。
  - 依存: S01, S90
  - unblock: final commit, issue finish, PR delivery
  - 対象ファイル: issue-wide diff
  - 閉じる要件: all
  - レビューゲート: qa-reviewer, code-reviewer, spec-reviewer

## 要件 ↔ ステップ対応

- AC-001 -> S01
- AC-002 -> S01
- AC-003 -> S01
- AC-004 -> S01
- AC-005 -> S01, S90
- AC-006 -> S01
- AC-007 -> S01
- AC-008 -> S01
- AC-009 -> S01
- EC-001 -> S01
- EC-002 -> S01
- EC-003 -> S90, S99

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子 | ステップ | スライス | 種別 | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル | クロージャ証跡 |
|---|---|---|---|---|---|---|---|---|---|---|
| cl-001 | S01 | mandatory authoring sequence | acceptance | AC-001 | skill 本文だけで requirement -> reviewer pass -> design -> reviewer pass -> plan -> reviewer pass -> execution handoff を識別できる | provider/mirror skill text | phase promotion skip | yes | inspect-only | report Step/Test Closure |
| cl-002 | S01 | reviewer state semantics | acceptance/negative | AC-002 | fresh pass 以外の reviewer state は pass ではない | provider/mirror skill text | stale/non-pass success | yes | inspect-only | report Step/Test Closure |
| cl-003 | S01 | gap return rule | acceptance | AC-003 | unresolved gap は clarification または prior authoring phase に戻す | provider/mirror skill text | execution assumption leak | yes | inspect-only | report Step/Test Closure |
| cl-004 | S01 | delegated draft authority | acceptance | AC-004 | delegated drafts は採用と report evidence まで canonical authority ではない | provider/mirror skill text | draft-as-authority drift | yes | inspect-only | report Step/Test Closure |
| cl-005 | S01 | detailed docs routing | acceptance | AC-005, AC-009 | skill は schema を複製せず docs owner に誘導する | provider/mirror skill text | duplicated policy drift | yes | inspect-only | report Step/Test Closure |
| cl-006 | S01 | executable plan handoff | acceptance | AC-006 | non-executable `plan.md` は execution handoff blocker である | provider/mirror skill text | premature execution | yes | inspect-only | report Step/Test Closure |
| cl-007 | S01 | report evidence obligation | acceptance | AC-007 | each Spec Authoring Gate を issue `report.md` に記録する | provider/mirror skill text | missing gate evidence | yes | inspect-only | report Step/Test Closure |
| cl-008 | S01 | provider/mirror parity | regression | AC-008, EC-001 | provider skill と dogfooding mirror が byte-equivalent | `cmp` and existing parity unittest | stale dogfooding mirror | yes | covered-existing | report Step/Test Closure |
| cl-009 | S90 | docs impact resolved | risk | EC-003 | runtime/docs/template/harness 変更が不要または解決済み | issue-wide diff inspection | hidden docs impact | yes | inspect-only | report Docs Impact Resolution |
| cl-010 | S99 | final issue gate | final | all | validation, whitespace, reviewer gates が pass | final commands and reviewers | incomplete issue closure | yes | manual-required | report Final Quality Gate |

## 実装ステップ S01 — Issue planning skill first-read workflow spine

- 振る舞いの目標:
  - Agent が `spec-dock-issue-planning` skill を読んだ時点で、Issue authoring の mandatory phase gates、fresh reviewer semantics、non-pass stop condition、delegated draft authority、executable handoff、report evidence obligation、doc routing を理解できる。
- design 参照:
  - `design.md` の `Skill section contract`、`ディレクトリ / ファイル変更計画`、`要件 → 設計マッピング`。
- 依存:
  - passed requirement/design
- unblock:
  - S90, S99
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `.agents/skills/spec-dock-issue-planning/SKILL.md`

### 計画済み契約

- scope:
  - `Mandatory Issue Authoring Workflow` section と doc routing wording を追加/整理する。
- テスト義務:
  - closure id: cl-001..cl-008
  - coverage rationale: この issue は skill-text-only なので、inspection / parity / existing unittest で contract を閉じる。
- Red / 代替証跡の要件:
  - docs-only / inspect-only:
    - code test を置かない理由: runtime behavior ではなく shipped skill instruction text の更新であり、requirement は wording contract を観測点としているため。
    - 代替 evidence path: `rg` inspection、`cmp`、existing parity unittest。
- Green 検証:
  - `rg 'Mandatory Issue Authoring Workflow|fresh.*review_status: pass|missing|stale|waived|provisional|executable.*plan|report.md' src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md .agents/skills/spec-dock-issue-planning/SKILL.md`
  - `cmp -s src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md .agents/skills/spec-dock-issue-planning/SKILL.md`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets`
- Refactor / cleanup ガードレール:
  - 他 skill、workflow docs、runtime、tests を変更しない。
  - Skill へ schema を長くコピーしない。
- closure 証跡要件:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta
- report 証跡の記録先:
  - `report.md` の S01 session log、Implementation Delegation Gate、Reviewer Gate Status、Step Commit Gate。
- amendment trigger:
  - 他 skill / docs / runtime 変更が必要になる。
  - reviewer が requirement/design gap を指摘する。
  - provider/mirror parity を保てない理由が見つかる。

### 委任契約

- 委任ロール:
  - `doc-writer`
- 入力 docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `workflow_spec_authoring.md`
  - `workflow_issue.md`
  - `phase_plan_issue.md`
  - `docs/authoring/issue-plan.md`
  - current provider/mirror skill files
- 許可 paths:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `.agents/skills/spec-dock-issue-planning/SKILL.md`
- 禁止 changes:
  - Runtime, tests, templates, other skills, workflow docs, GitHub metadata, unrelated formatting。
- 受け入れ条件:
  - cl-001..cl-008 pass。
- 必須 tests または docs-only verification:
  - S01 Green 検証 commands。
- reviewer focus:
  - `spec-reviewer` docs/spec alignment。
- 必須出力:
  - changed files
  - verification result
  - unresolved risks
  - `No material implementation decisions beyond the approved plan.` または Ledger Note
- 停止条件:
  - input docs conflict
  - allowed paths 外変更が必要
  - acceptance wording を docs だけで満たせない
  - parity command が通せない

### 具体テストケース一覧

- `tc-s01-001` inspect-only: mandatory phase sequence が first-read surface にある
  - 前提: provider/mirror skill を読む。
  - 操作: `Mandatory Issue Authoring Workflow` section と phase order wording を確認する。
  - 期待結果: requirement -> fresh reviewer pass -> design -> fresh reviewer pass -> plan -> fresh reviewer pass -> execution handoff が識別できる。
  - 失敗検出: agent が docs を開くまで phase order を知らない regression を検出する。
  - 検証方法: `rg` inspection。
  - 関連 closure id: cl-001

- `tc-s01-002` inspect-only: non-pass reviewer state が pass 扱いされない
  - 前提: provider/mirror skill を読む。
  - 操作: fresh pass definition と non-pass state wording を確認する。
  - 期待結果: missing / stale / failed / unavailable / denied / waived / provisional が pass ではないと読める。
  - 失敗検出: stale/provisional review を promotion に使う regression を検出する。
  - 検証方法: `rg` inspection。
  - 関連 closure id: cl-002

- `tc-s01-003` inspect-only: gap / draft / handoff / report evidence boundary がある
  - 前提: provider/mirror skill を読む。
  - 操作: unresolved gap、delegated draft、non-executable plan、report evidence obligation の wording を確認する。
  - 期待結果: gap は authoring/clarification に戻り、draft は canonical authority ではなく、non-executable plan は blocker で、report evidence が必要と読める。
  - 失敗検出: unresolved gap や draft authority を execution に持ち越す regression を検出する。
  - 検証方法: `rg` inspection。
  - 関連 closure id: cl-003, cl-004, cl-006, cl-007

- `tc-s01-004` covered-existing: provider と mirror が一致する
  - 前提: provider/mirror skill を更新済み。
  - 操作: `cmp` と existing parity unittest を実行する。
  - 期待結果: provider と dogfooding mirror が byte-equivalent で、checked-in dogfooding parity test が pass する。
  - 失敗検出: dogfooding mirror が stale のままになる regression を検出する。
  - 検証方法: `cmp -s ...` と `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets`。
  - 関連 closure id: cl-008

### ステップ完了契約

- closure id:
  - cl-001..cl-008
- close 条件:
  - S01 Green 検証が pass。
  - `spec-reviewer` step review が pass。
  - S01 scope の commit が作成される、または正当な approved-no-op が記録される。
- 検証 evidence:
  - `rg` inspection, `cmp`, targeted unittest
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta
- 残リスク:
  - Agent 実行時の実効性は後続 PDCA / empirical tuning で継続確認する。

### ステップゲート

- step reviewer gate:
  - reviewer: `spec-reviewer`
  - review 範囲: S01 diff と requirement/design/plan/report 整合
  - pass 条件: `review_status: pass`
  - re-review rule: 指摘修正後に fresh reviewer を再実行する。
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S01 skill text and report evidence
  - no-op: 不可。S01 は text update を必要とする。

## ドキュメント影響の解消ステップ S90

- 対象:
  - docs / templates / README / workflow / skill / migration notes
- 対応:
  - 今回の planned product change は skill text のみ。
  - `workflow_spec_authoring.md` / `workflow_issue.md` / `phase_plan_issue.md` / `authoring/issue-plan.md` は policy source として参照し、本文変更はしない。
  - docs 影響が不要であることを `git diff --name-only` と spec-reviewer docs/spec alignment で確認する。
- doc update owner:
  - 追加 docs 更新が必要になった場合のみ `doc-writer`。
- spec/doc review:
  - reviewer: `spec-reviewer`
  - pass 条件: docs 影響が解決済みで、requirement/design/plan と矛盾しない。

## 最終品質ゲートステップ S99

- branch diff 範囲:
  - `iss-00159` issue docs/report
  - provider/mirror `spec-dock-issue-planning/SKILL.md`
- 必須 validation:
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
  - `cmp -s src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md .agents/skills/spec-dock-issue-planning/SKILL.md`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets`
- final QA gate:
  - reviewer: `qa-reviewer`
  - 範囲: Issue 全体の obligation coverage と integration test 要否
  - pass 条件: reviewer pass
- final code review ゲート:
  - reviewer: `code-reviewer`
  - 範囲: issue-wide integrated diff、構造、責務境界、回帰リスク、保守性
  - pass 条件: `review_status: pass`
- final spec review ゲート:
  - reviewer: `spec-reviewer`
  - 範囲: requirement / design / plan / report / implementation / tests / docs alignment
  - pass 条件: reviewer pass
- final commit gate:
  - commit 範囲: this issue's implementation and report evidence
  - final report ledger: S99 gate results
  - post-commit external evidence destination: final response / PR body / issue comment

## 最終完了条件

- AC/EC 達成:
  - cl-001..cl-010 が report で pass。
- docs 影響解決:
  - S90 が pass。
- 全 implementation step 完了:
  - S01 committed。
- final quality gate pass:
  - qa-reviewer: pass
  - issue-wide code-reviewer: pass
  - final spec-reviewer: pass
- issue lifecycle:
  - final commit 後に `issue finish` を実行できる状態。
