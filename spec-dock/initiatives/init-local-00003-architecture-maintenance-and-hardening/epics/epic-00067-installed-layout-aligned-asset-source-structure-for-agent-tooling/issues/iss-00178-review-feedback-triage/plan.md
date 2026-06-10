---
種別: 実装計画書（Issue）
ID: "iss-00178"
タイトル: "Review Feedback Triage"
関連GitHub: ["#178"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-10"
依存: ["requirement.md", "design.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00178 Review Feedback Triage — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID

- AC:
  - AC-001: PR Repair Triage Gate
  - AC-002: batch dedicated template
  - AC-003: inventory classification
  - AC-004: repair unit handoff
  - AC-005: non-fix disposition
  - AC-006: merge-prepared gate
  - AC-007: observation boundary preservation
  - AC-008: scope containment
- EC:
  - EC-001: timeout / observation limit
  - EC-002: same root cause
  - EC-003: false positive / stale review
  - EC-004: scope expansion
  - EC-005: repeated failure class
- 制約:
  - provider-side `src/spec_dock/assets/install_root/` と `src/spec_dock/assets/spec_dock/` を source of truth とする。
  - skill-local PR repair batch template は追加する。
  - runtime `new doc --template`、new doc type、runtime template catalog、自動分類 runtime、CI log parser、GitHub mutation は追加しない。

## 依存関係から導く実装順序

- 依存関係の参照元:
  - `design.md` の `依存関係分析`、`インターフェース契約`、`ディレクトリ / ファイル変更計画`。
- 順序ルール:
  - まず workflow owner の `github-pr-merge-preparer` skill contract を固定する。
  - 次に evidence collector の `github-pr-observation` boundary を補強する。
  - その後、discussion catalog に短い contract を追加する。
  - 最後に dogfooding copy parity と runtime untouched を確認する。
- step 依存サマリー:
  - S01:
    - 依存: fresh-pass `requirement.md` / `design.md`
    - unblock: S02, S03, S04
    - 対象ファイル: `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`, `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
  - S02:
    - 依存: S01 の judgment boundary
    - unblock: S04, S90
    - 対象ファイル: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - S03:
    - 依存: S01 の skill-local template / checklist
    - unblock: S04, S90
    - 対象ファイル: `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md`
  - S04:
    - 依存: S01-S03
    - unblock: S90, S99
    - 対象ファイル: `.agents/skills/...`, `spec-dock/docs/rules/issue/discussions.md`
  - S90:
    - 依存: S01-S04
    - unblock: S99
  - S99:
    - 依存: S01-S90

## ステップ一覧

- S01:
  - 観測可能な振る舞い: merge-preparer skill が observation 後、fix delegation 前に PR Repair Triage Gate を要求する。
  - 依存: requirement/design pass
  - unblock: S02-S04
  - 対象ファイル: `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`, `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
  - 閉じる要件: AC-001..AC-006, AC-008, EC-001..EC-005
  - レビューゲート: spec-reviewer
- S02:
  - 観測可能な振る舞い: observation skill が collection-only boundary を明確に保つ。
  - 依存: S01
  - unblock: S04/S90
  - 対象ファイル: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - 閉じる要件: AC-007, AC-008
  - レビューゲート: spec-reviewer
- S03:
  - 観測可能な振る舞い: issue discussion rules が PR repair batch/unit を existing `disc` usage として短く案内する。
  - 依存: S01
  - unblock: S04/S90
  - 対象ファイル: `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md`
  - 閉じる要件: AC-002, AC-004, AC-008
  - レビューゲート: spec-reviewer
- S04:
  - 観測可能な振る舞い: dogfooding copy が provider source と一致する。
  - 依存: S01-S03
  - unblock: S90/S99
  - 対象ファイル: `.agents/skills/github-pr-merge-preparer/SKILL.md`, `.agents/skills/github-pr-observation/SKILL.md`, `spec-dock/docs/rules/issue/discussions.md`
  - 閉じる要件: AC-008
  - レビューゲート: spec-reviewer または code-reviewer 条件付き
- S90:
  - 観測可能な振る舞い: docs impact が解決済みまたは no-op rationale 付きで閉じている。
  - 依存: S01-S04
  - unblock: S99
  - 対象ファイル: docs/skills diff 全体
  - レビューゲート: spec-reviewer
- S99:
  - 観測可能な振る舞い: issue-wide diff が要件・設計・計画を満たし、最終 review gate を通せる。
  - 依存: S01-S90
  - レビューゲート: qa-reviewer, code-reviewer, spec-reviewer

## 要件 ↔ ステップ対応

- AC-001 -> S01
- AC-002 -> S01, S03
- AC-003 -> S01
- AC-004 -> S01, S03
- AC-005 -> S01
- AC-006 -> S01
- AC-007 -> S02
- AC-008 -> S01, S02, S03, S04, S99
- EC-001 -> S01
- EC-002 -> S01
- EC-003 -> S01
- EC-004 -> S01
- EC-005 -> S01

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ（step） | スライス（slice） | 種別（type） | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル（evidence level） | クロージャ証跡（closure evidence） |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | triage-gate | acceptance | AC-001 | PR Repair Triage Gate が observation 後、fix delegation 前にある | merge-preparer skill text | raw finding delegated without triage | yes | inspect-only | `rg` output + reviewer pass |
| tc-002 | S01 | batch-template | acceptance | AC-002 | skill-local PR repair batch template が required sections を持ち、merge-preparer skill が参照する | template file + merge-preparer skill text | incomplete control sheet / skeleton embedded only in prose | yes | inspect-only | `rg` output + reviewer pass |
| tc-003 | S01 | classification | acceptance | AC-003 | required fields and values が明記される | merge-preparer skill text | severity-only classification | yes | inspect-only | `rg` output + reviewer pass |
| tc-004 | S01 | repair-unit | acceptance | AC-004 | repair unit checklist と worker handoff がある | merge-preparer skill text | raw finding used as worker source | yes | inspect-only | `rg` output + reviewer pass |
| tc-005 | S01 | non-fix | acceptance | AC-005 | non-fix disposition に rationale / residual risk が必要 | merge-preparer skill text | silent dismissal of findings | yes | inspect-only | `rg` output + reviewer pass |
| tc-006 | S01 | merge-prepared | acceptance | AC-006 | merge-prepared predicate は batch-aware で review-clean と区別される | merge-preparer skill text | endless review-clean loop / premature merge-prepared | yes | inspect-only | `rg` output + reviewer pass |
| tc-007 | S02 | observation-boundary | acceptance | AC-007 | observation skill は collection-only で judgment を持たない | observation skill text | collector starts making judgment | yes | inspect-only | `rg` output + reviewer pass |
| tc-008 | S99 | scope-containment | negative | AC-008 | skill-local template 以外の runtime templates / doc type は変更されない | forbidden path diff | scope creep into runtime template registry | yes | inspect-only | empty diff |
| tc-009 | S01 | stop-conditions | edge | EC-001/004/005 | timeout / observation limit は observation limitation と resume metadata として batch に残し、resume は同じ trigger boundary を使い、latest head SHA 再観測前に merge-prepared と言わず、無承認の新規 trigger を投稿しない | merge-preparer skill text | unsafe repeated repair loop / duplicate trigger / stale-head merge-prepared | yes | inspect-only | exact-term `rg` output + reviewer pass |
| tc-010 | S01 | grouping | edge | EC-002 | same root cause を concern/unit で group できる | merge-preparer skill text | duplicate repair units | yes | inspect-only | `rg` output + reviewer pass |
| tc-011 | S01 | false-positive | edge | EC-003 | false positive / stale review に rationale path がある | merge-preparer skill text | invalid finding treated as required fix | yes | inspect-only | `rg` output + reviewer pass |
| tc-012 | S03 | discussion-contract | acceptance | design discussion contract | discussion rules は短く skill-local template と skill guidance を参照する | provider discussion rules | duplicated drift-prone template | yes | inspect-only | `rg` output + reviewer pass |
| tc-013 | S04 | dogfooding-parity | integration | parent epic provider-first | dogfooding copy が provider source と一致する | provider and dogfooding files | provider/dogfooding drift | yes | inspect-only / command | `diff -u` outputs |
| tc-014 | S90 | docs-impact | docs | workflow_issue docs impact | docs impact が解決済みまたは no-op rationale 付き | relevant docs/skills | undocumented contract drift | yes | inspect-only | docs impact ledger |
| tc-015 | S99 | final-gate | final | workflow_issue final gate | final validation and reviewers pass | full issue diff | incomplete closure | yes | command + reviewer | final report gates |

## レビュー / QA ゲート方針

- RG1 step review:
  - 実施タイミング: 各 implementation step の report 証跡更新後、commit 前。
  - reviewer: docs-only / skill-text-only は `spec-reviewer`。installer/scaffold/runtime behavior が変わった場合のみ `code-reviewer` を追加する。
  - pass 条件: `review_status: pass`
- QG1 final QA:
  - reviewer: `qa-reviewer`
  - 範囲: Issue 全体の obligation coverage、inspect-only evidence の十分性、追加テスト要否。
- SG1 final spec review:
  - reviewer: `spec-reviewer`
  - 範囲: requirement / design / plan / report / skill/docs diff 整合。

## 実行ルール（全ステップ共通）

- 実行結果、検証結果、逸脱、reviewer verdict、commit/no-op evidence は `report.md` に記録する。
- `plan.md` は planned contract のまま保ち、実行中に見つかった新しい仕様判断は `report.md` に記録する。
- runtime `new doc --template`、new doc type、`spec_dock_runtime`、runtime template registry が必要になったら実装を止め、plan amendment と fresh reviewer pass に戻る。
- GitHub mutation、review reply、thread resolve、auto-merge、branch deletion、issue close、`spec-dock issue finish` は禁止。

## 実装ステップ

### 実装ステップ S01 — Provider merge-preparer skill に PR Repair Triage Gate を追加する

- 振る舞いの目標（behavior goal）:
  - `github-pr-merge-preparer` が observation 後、repair delegation 前に batch triage を必須化し、batch-aware merge-prepared predicate を持つ。
- design 参照:
  - `design.md` の `採用方針 / トレードオフ`、`インターフェース契約`、`シーケンス差分`。
- 依存:
  - fresh-pass `requirement.md` / `design.md`
- unblock:
  - S02, S03, S04
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
- 計画済み契約（planned contract）:
  - scope:
    - PR Repair Triage Gate、batch template reference、classification values、repair unit checklist、stop conditions、batch-aware merge-prepared predicate、response checklist を skill text に追加する。
    - PR repair batch 専用 template file を追加し、batch control sheet の required sections / inventory / classification vocabulary / merge-prepared gate を template に固定する。
  - テスト義務（test obligation）:
    - closure id: `tc-001`..`tc-006`, `tc-009`..`tc-011`
    - coverage rationale: user-facing runtime ではなく agent workflow contract なので inspect-only と reviewer pass で閉じる。
  - Red / 代替証跡の要件:
    - docs-only / inspect-only:
      - code test を置かない理由: skill guidance text の変更であり runtime behavior を変更しないため。
      - 代替 evidence path: `rg` による required section / vocabulary / predicate / stop condition の検出。
  - 実装範囲（implementation scope）:
    - allowed paths:
      - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
      - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
    - forbidden changes:
      - runtime scripts、runtime templates、dogfooding copy、tests、canonical docs、GitHub state。
  - Green 検証:
    - `rg -n "PR Repair Triage Gate|fix delegation|PR repair batch|Concern Catalog|Inventory|Unit Discussion Plan|Merge-Prepared Gate" src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
    - `rg -n "templates/pr-repair-batch.md|pr-repair-batch.md" src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
    - `test -f src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
    - `rg -n "PR / Observation Metadata|Batch Purpose|Concern Catalog|Inventory|Classification Values|Per-Concern Analysis|Repair Queue|Unit Discussion Plan|Stop Conditions|Merge-Prepared Gate" src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
    - `rg -n "validity.*valid.*partially-valid.*false-positive.*duplicate.*unknown|risk_class.*blocking.*material-follow-up.*minor.*false-positive.*duplicate|need_to_fix.*yes.*no.*follow-up.*human-decision|disposition.*fix-now.*follow-up.*no-action.*covered-by.*needs-human|status.*untriaged.*triaged.*unit-needed.*unit-created.*implemented.*reobserved-pass.*blocked" src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
    - `rg -n "validity.*valid.*partially-valid.*false-positive.*duplicate.*unknown|risk_class.*blocking.*material-follow-up.*minor.*false-positive.*duplicate|need_to_fix.*yes.*no.*follow-up.*human-decision|disposition.*fix-now.*follow-up.*no-action.*covered-by.*needs-human|status.*untriaged.*triaged.*unit-needed.*unit-created.*implemented.*reobserved-pass.*blocked" src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
    - `rg -n "source_batch|covered_ids|Implementation Plan|Re-observation Result|Residual Risk" src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
    - `rg -n "review-clean|merge-prepared|untriaged|needs-human|human gate|latest head|resume metadata|trigger boundary|new trigger|observation limitation" src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
  - Refactor / cleanup ガードレール:
    - 目的: skill text と skill-local template の追加・再構成に留める。
    - 禁止する広がり: script / runtime / runtime template / unrelated skill の変更。
  - closure 証跡要件:
    - Step Contract Closure: `tc-001`..`tc-006`, `tc-009`..`tc-011`
    - Test Contract Closure: inspect-only evidence
    - Closure Coverage: AC/EC mapping
  - report 証跡の記録先:
    - `Implementation Delegation Gate`, `Step Contract Closure`, `Test Contract Closure`, `Closure Coverage`, `Reviewer Gate Status`, `Step Commit Gate`
  - amendment trigger:
    - runtime behavior、JSON schema、GitHub API、new doc template support が必要になる発見。

#### 委任契約（delegation contract）

- 委任ロール（delegated role）:
  - doc-writer
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, target skill file
- 許可 paths:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
- 禁止 changes:
  - allowed path 以外すべて。
- 受け入れ条件:
  - `tc-001`..`tc-006`, `tc-009`..`tc-011`
- 必須 tests または docs-only verification:
  - 上記 `rg` commands。
- reviewer focus:
  - spec-reviewer: skill text と requirement/design alignment。
- 必須出力（output required）:
  - changed files、verification result、unresolved risks、report evidence。
- 停止条件（stop conditions）:
  - runtime/code/runtime-template 変更が必要、acceptance を skill text + skill-local template で満たせない、または requirement/design と矛盾する。

#### 具体テストケース一覧

- `tc-s01-001` inspect-only: PR Repair Triage Gate と batch template が確認できる
  - 前提: provider-side merge-preparer skill を編集済み。
  - 操作: `test -f` と `rg` で skill-local template file、skill 内の exact template path reference、gate 名、batch template sections、classification vocabulary の exact values を検索する。
  - 期待結果: PR repair batch 専用 template が存在し、provider skill が `templates/pr-repair-batch.md` を参照し、required terms と `valid` / `partially-valid` / `human-decision` / `reobserved-pass` などの標準値が provider skill / template に存在する。
  - 失敗検出: batch artifact を省略できる、template file がない、skill が template を参照しない、または severity-only classification に戻る回帰を検出する。
  - 検証方法: S01 の Green 検証 command。
  - 関連 closure id: `tc-001`, `tc-002`, `tc-003`

- `tc-s01-002` inspect-only: repair unit と non-fix disposition が確認できる
  - 前提: provider-side merge-preparer skill を編集済み。
  - 操作: `rg` で repair unit checklist、non-fix disposition、residual risk を検索する。
  - 期待結果: repair worker が raw finding ではなく unit plan から動くこと、non-fix は rationale 付きで閉じることが読める。
  - 失敗検出: 場当たり修正や silent no-action を許す回帰を検出する。
  - 検証方法: S01 の Green 検証 command。
  - 関連 closure id: `tc-004`, `tc-005`, `tc-010`, `tc-011`

- `tc-s01-003` inspect-only: merge-prepared と stop conditions が確認できる
  - 前提: provider-side merge-preparer skill を編集済み。
  - 操作: `rg` で `review-clean`、`merge-prepared`、`untriaged`、`needs-human`、`latest head`、`resume metadata`、`trigger boundary`、`new trigger`、`observation limitation` を検索する。
  - 期待結果: review-clean と merge-prepared が区別され、timeout / observation limit は observation limitation と resume metadata で記録され、resume は同じ trigger boundary を使い、latest head SHA の re-observation 前に merge-prepared と言わず、無承認の新規 trigger を投稿しない。
  - 失敗検出: duplicate trigger、stale-head merge-prepared、resume metadata 欠落、no major issues までの無限ループ、または untriaged item があるのに merge-prepared と言う回帰を検出する。
  - 検証方法: S01 の Green 検証 command。
  - 関連 closure id: `tc-006`, `tc-009`

#### ステップ完了契約（step closure contract）

- closure id:
  - `tc-001`..`tc-006`, `tc-009`..`tc-011`
- close 条件:
  - Required terms and contract sections are present; spec-reviewer pass.
- 検証 evidence:
  - `rg` command outputs recorded in `report.md`。
- report evidence:
  - Step Contract Closure / Test Contract Closure / Closure Coverage
- 残リスク:
  - agent interpretation risk; mitigated by explicit skill-local template and reviewer pass。

#### ステップゲート（step gate）

- step reviewer gate:
  - reviewer: spec-reviewer
  - review 範囲: S01 diff and AC/EC alignment
  - pass 条件: `review_status: pass`
  - re-review rule: 指摘修正後に fresh review
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S01 file only unless batched with approved docs-only steps

### 実装ステップ S02 — Provider observation skill の collection-only boundary を補強する

- 振る舞いの目標:
  - `github-pr-observation` が evidence collection のみを担い、risk / disposition / grouping を持たないことを明確にする。
- design 参照:
  - `design.md` の `D-005` 相当境界。
- 依存:
  - S01
- unblock:
  - S04, S90
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
- 計画済み契約:
  - allowed paths:
    - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - forbidden changes:
    - scripts、JSON schema、runtime、tests、dogfooding copy。
  - Green 検証:
    - `rg -n "collection-only|evidence collection|risk_class|need_to_fix|disposition|repair unit grouping|github-pr-merge-preparer" src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - report 証跡:
    - `tc-007`
  - amendment trigger:
    - observation script or JSON schema changes become necessary.

#### 委任契約（delegation contract）

- 委任ロール: doc-writer
- 入力 docs: `requirement.md`, `design.md`, target skill
- 許可 paths: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
- 禁止 changes: allowed path 以外すべて
- 受け入れ条件: `tc-007`
- 必須 tests または docs-only verification: S02 Green 検証 command
- reviewer focus: spec-reviewer
- 必須出力: changed files, verification result, unresolved risks
- 停止条件: scripts / runtime / schema 変更が必要

#### 具体テストケース一覧

- `tc-s02-001` inspect-only: observation skill が judgment を持たない
  - 前提: provider-side observation skill を編集済み。
  - 操作: `rg` で collection-only boundary と forbidden judgment terms を検索する。
  - 期待結果: classification / disposition / repair unit grouping は downstream `github-pr-merge-preparer` の責務だと読める。
  - 失敗検出: observation skill が risk_class や disposition を決めるように読める回帰を検出する。
  - 検証方法: S02 Green 検証 command。
  - 関連 closure id: `tc-007`

#### ステップ完了契約（step closure contract）

- closure id: `tc-007`
- close 条件: boundary note が存在し、forbidden runtime diff がない。
- 検証 evidence: `rg` output and forbidden path diff.
- report evidence: Step Contract Closure / Test Contract Closure / Closure Coverage.
- 残リスク: low; text-only boundary clarification.

#### ステップゲート（step gate）

- reviewer: spec-reviewer
- pass 条件: `review_status: pass`
- commit / no-op gate: committed or batched with approved docs-only changes

### 実装ステップ S03 — Issue discussion rules に短い PR repair contract を追加する

- 振る舞いの目標:
  - `docs/rules/issue/discussions.md` が PR repair batch / unit を existing `disc` usage として短く案内する。
- design 参照:
  - `design.md` の discussion rules 方針。
- 依存:
  - S01
- unblock:
  - S04, S90
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md`
- 計画済み契約:
  - allowed paths:
    - `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md`
  - forbidden changes:
    - full template duplication、runtime templates、runtime、dogfooding copy。
  - Green 検証:
    - `rg -n "PR repair batch|repair unit|github-pr-merge-preparer|existing .disc.|canonical" src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md`
  - report 証跡:
    - `tc-012`
  - amendment trigger:
    - full template duplication、runtime template support、または new doc type appears necessary.

#### 委任契約（delegation contract）

- 委任ロール: doc-writer
- 入力 docs: `requirement.md`, `design.md`, target docs
- 許可 paths: `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md`
- 禁止 changes: allowed path 以外すべて
- 受け入れ条件: `tc-012`
- 必須 tests または docs-only verification: S03 Green 検証 command
- reviewer focus: spec-reviewer
- 必須出力: changed files, verification result, unresolved risks
- 停止条件: full template duplication or runtime template support required

#### 具体テストケース一覧

- `tc-s03-001` inspect-only: discussion rules は短い contract に留まる
  - 前提: provider-side issue discussion rules を編集済み。
  - 操作: `rg` で PR repair batch / repair unit / github-pr-merge-preparer 参照を検索する。
  - 期待結果: batch/unit が existing `disc` usage であり、batch full template は skill-local template 側にあると読める。
  - 失敗検出: discussion rules に長大 template を重複し、skill-local template と drift する回帰を検出する。
  - 検証方法: S03 Green 検証 command と manual diff inspection。
  - 関連 closure id: `tc-012`

#### ステップ完了契約（step closure contract）

- closure id: `tc-012`
- close 条件: short catalog contract が存在し、full template duplication がない。
- 検証 evidence: `rg` output and diff inspection.
- report evidence: Step Contract Closure / Test Contract Closure / Closure Coverage.
- 残リスク: low; mitigated by keeping full template in skill-local template.

#### ステップゲート（step gate）

- reviewer: spec-reviewer
- pass 条件: `review_status: pass`
- commit / no-op gate: committed or batched with approved docs-only changes

### 実装ステップ S04 — Dogfooding copy parity を確認または同期する

- 振る舞いの目標:
  - dogfooding checked-in copies match provider-side source-of-truth for changed skill/docs assets.
- design 参照:
  - `design.md` の Source of Record / File Change Plan。
- 依存:
  - S01-S03
- unblock:
  - S90, S99
- 対象ファイル:
  - `.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
  - `.agents/skills/github-pr-observation/SKILL.md`
  - `spec-dock/docs/rules/issue/discussions.md`
- 計画済み契約:
  - safe approach:
    - Prefer supported local update path if it only updates intended managed files.
    - Fallback: copy the changed provider skill/docs/template assets to dogfooding locations if update would cause unrelated rewrites, and record rationale.
  - allowed paths:
    - dogfooding target files above
  - forbidden changes:
    - issue data rewrites, runtime templates, unrelated generated state.
  - Green 検証:
    - `diff -u src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md .agents/skills/github-pr-merge-preparer/SKILL.md`
    - `diff -u src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md .agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
    - `diff -u src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md .agents/skills/github-pr-observation/SKILL.md`
    - `diff -u src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md spec-dock/docs/rules/issue/discussions.md`
    - `git diff -- .agents/skills/github-pr-merge-preparer/SKILL.md .agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md .agents/skills/github-pr-observation/SKILL.md spec-dock/docs/rules/issue/discussions.md`
  - report 証跡:
    - `tc-013`
  - amendment trigger:
    - parity requires broad unrelated rewrite or supported update path changes runtime behavior.

#### 委任契約（delegation contract）

- 委任ロール: doc-writer for parity copy; code-reviewer required only if installer/update behavior changes.
- 入力 docs: `design.md`, provider files, dogfooding files
- 許可 paths: S04 target files
- 禁止 changes: allowed path 以外すべて
- 受け入れ条件: provider and dogfooding files identical, including skill-local template
- 必須 tests または docs-only verification: S04 Green 検証 commands
- reviewer focus: spec-reviewer, code-reviewer if behavior changes
- 必須出力: sync/copy method, changed files, diff outputs, risks
- 停止条件: broad unrelated rewrite or unsafe update needed

#### 具体テストケース一覧

- `tc-s04-001` inspect-only / command: provider and dogfooding files match
  - 前提: S01-S03 provider files are finalized.
  - 操作: supported update/copy path is used, then `diff -u` for all provider/dogfooding pairs.
  - 期待結果: all diffs are empty, including PR repair batch template.
  - 失敗検出: installed dogfooding copy drifts from provider source and agents read stale workflow.
  - 検証方法: S04 Green 検証 commands。
  - 関連 closure id: `tc-013`

#### ステップ完了契約（step closure contract）

- closure id: `tc-013`
- close 条件: all provider/dogfooding pairs match or approved no-op with evidence.
- 検証 evidence: `diff -u` outputs.
- report evidence: Step Contract Closure / Test Contract Closure / Closure Coverage.
- 残リスク: update path may touch unrelated generated files; stop if observed.

#### ステップゲート（step gate）

- reviewer: spec-reviewer unless code/runtime behavior changes
- pass 条件: `review_status: pass`
- commit / no-op gate: committed or approved-no-op

### ドキュメント影響の解消ステップ S90（docs impact resolution / docs refresh）

- 対象:
  - changed skills and issue discussion rules.
  - README/runtime docs/migration notes only if S01-S04 reveal a broader user-facing contract.
- 対応:
  - Confirm no extra docs are required for runtime `new doc --template` because it remains out of scope.
  - Confirm runtime templates are unchanged while the skill-local PR repair batch template is intentionally added.
- doc update owner:
  - doc-writer when updates are required.
- spec/doc review:
  - reviewer: spec-reviewer
  - pass 条件: docs impact resolved.
- 検証:
  - `rg -n "PR Repair Triage Gate|PR repair batch|repair unit|review-clean|merge-prepared" src/spec_dock/assets/install_root/.agents/skills src/spec_dock/assets/spec_dock/docs/rules/issue .agents/skills spec-dock/docs/rules/issue`
  - `test -f src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
  - `git diff -- src/spec_dock/assets/spec_dock/templates src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime`
- closure:
  - `tc-014`

### 最終品質ゲートステップ S99（final quality gate）

- branch diff 範囲:
  - provider skills/docs/skill-local template, dogfooding copies, active issue canonical docs/discussions/report.
- 必須 validation:
  - `git diff --check`
  - `git diff --name-only`
  - `git diff -- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime src/spec_dock/assets/spec_dock/templates`
  - `uv run pytest tests/unit/infra`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync --no-github`
- validation notes:
  - If `uv run pytest tests/unit/infra` is too broad for the environment, record why and run the narrowest available provider/dogfooding parity inspection.
  - If `sync --no-github` is unavailable or touches unrelated state, record alternative validation and rationale.
- final QA gate:
  - reviewer: qa-reviewer
  - 範囲: Issue 全体の obligation coverage と integration test 要否
  - pass 条件: reviewer pass
- final code review ゲート:
  - reviewer: code-reviewer
  - 範囲: issue-wide integrated diff, no runtime template drift, provider/dogfooding parity
  - pass 条件: `review_status: pass`
- final spec review ゲート:
  - reviewer: spec-reviewer
  - 範囲: requirement / design / plan / report / implementation / tests / docs 整合
  - pass 条件: reviewer pass
- final commit gate:
  - commit 範囲: all completed implementation/report evidence
  - final report ledger: all closure IDs `tc-001`..`tc-015`
  - post-commit external evidence destination: PR delivery workflow, outside this plan's authoring authority
- closure:
  - `tc-015`
  - `tc-008`

## 未確定事項

- なし。

## 最終完了条件

- AC/EC 達成:
  - `tc-001`..`tc-015` が `report.md` に pass または justified approved-no-op として記録されている。
- docs 影響解決:
  - S90 pass。
- 全 implementation step 完了:
  - S01-S04 committed / approved-no-op。
- final quality gate pass:
  - qa-reviewer: pass
  - issue-wide code-reviewer: pass
  - final spec-reviewer: pass
- runtime scope:
  - forbidden runtime/template diff empty except intentional skill-local template paths。
- delivery:
  - PR 作成・PR merge-preparation は実装後の delivery workflow で扱う。merge は人間 action のまま残す。
