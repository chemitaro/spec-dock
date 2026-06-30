---
種別: 実装計画書（Issue）
ID: "iss-00254"
タイトル: "Add Grade Aware Spec Review And Evidence Gates"
Issue Grade: "strict"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00254 Add Grade Aware Spec Review And Evidence Gates — Issue 実装計画書（Strict）

## 1. 実装戦略

G3 は、既存の EAL gate / delegated draft authority gate / artifact readiness preflight を尊重しながら、report evidence gate を issue execution readiness へ接続する。実装は docs/template contract を先に固定し、その contract を読む最小 runtime helper と focused tests を追加する。Issue 単位の PR は作成せず、G3 checkpoint commit を G4 / `iss-00255` に渡す。

## 2. Spec-Locked Closure Index

| ID | 対象 | Close 条件 | 主な検証 |
|---|---|---|---|
| G3-C-001 | AC-001 | fresh `spec-reviewer` pass が phase promotion / issue execution readiness の必須 evidence として docs/template/runtime に現れる | docs/template inspection、workflow negative/positive tests |
| G3-C-002 | AC-002 | delegated draft adoption が EAL と Delegated Draft Evidence なしに成立しない | report template tests、workflow negative tests |
| G3-C-003 | AC-003 | stale draft / stale reviewer / unresolved `stale` or `blocked` EAL が readiness を block する | domain/CLI tests |
| G3-C-004 | AC-004 | Standard skip reason と Strict/Critical specialist/fallback evidence の記録先と block 条件がある | report template tests、workflow negative/positive tests |
| G3-C-005 | AC-005 | missing reviewer/adoption/grade evidence が R0 と矛盾しない reason code で `may_execute_approved_plan: false` になる | `workflow status` / `guidance issue-execution` tests |
| G3-C-006 | AC-006 | discussion draft self-claim prohibition が弱まらず、delegated draft は canonical authority を持たない | docs inspection、existing delegated draft tests |
| G3-C-007 | AC-007 | G2 draft routing、PR observation policy、issue finish GitHub lifecycle が G3 で変更されていない | focused regression / diff inspection |
| G3-C-008 | AC-008 | provider-side source of truth と dogfooding mirror の docs/template が整合する | parity inspection |
| G3-C-090 | M90 | docs impact が provider/dogfooding で解消される | docs impact table |
| G3-C-095 | M95 | final QA / code / spec review が fresh pass する | reviewer gates |
| G3-C-099 | M99 | no per-issue PR の local checkpoint commit が clean で、G4 に渡せる | final commands + commit evidence |

## 3. 振る舞いバックログ

| ID | 振る舞い | Closure |
|---|---|---|
| B-G3-001 | Report evidence が missing のとき、substantive docs / executable plan があっても issue execution readiness は blocked になる | G3-C-001, G3-C-005 |
| B-G3-002 | EAL に unresolved `stale` / `blocked` があると readiness は blocked になる | G3-C-002, G3-C-003 |
| B-G3-003 | Strict issue で specialist evidence または manual fallback evidence がないと readiness は blocked になる | G3-C-004, G3-C-005 |
| B-G3-004 | 必須 evidence が揃うと既存 artifact readiness / assurance authority と合わせて `ready` になる | G3-C-001〜G3-C-005 |
| B-G3-005 | Issue report template は grade evidence / reviewer evidence / adoption evidence の記録先を提供する | G3-C-001〜G3-C-004 |
| B-G3-006 | G3 は no per-issue PR の branch baton を維持する | G3-C-099 |

## 4. 具体テストケース

- `tc-g3-001` template:
  - 前提: provider `templates/issue/report.md` を読む。
  - 操作: required section と accepted token を確認する。
  - 期待結果: Grade Specialist Evidence Gate、Spec Authoring Gate、Reviewer Gate Status、Final Spec Review Gate、EAL、Delegated Draft Evidence が存在する。
  - 関連 closure id: G3-C-001, G3-C-002, G3-C-004
- `tc-g3-002` cli-negative:
  - 前提: substantive requirement/design、executable plan、valid assurance contract がある。
  - 操作: report evidence を missing / scaffold のまま `guidance issue-execution` を実行する。
  - 期待結果: `state=blocked`, `may_execute_approved_plan=false`, reason は report evidence missing 系になる。
  - 関連 closure id: G3-C-001, G3-C-005
- `tc-g3-003` cli-negative:
  - 前提: EAL に unresolved `stale` または `blocked` entry がある。
  - 操作: `workflow status --format json` と `guidance issue-execution` を実行する。
  - 期待結果: EAL block reason が details に出て readiness は blocked。
  - 関連 closure id: G3-C-002, G3-C-003, G3-C-005
- `tc-g3-004` cli-negative:
  - 前提: Strict authorized_profile issue で fresh spec-reviewer evidence はあるが specialist/fallback evidence が missing。
  - 操作: `guidance issue-execution` を実行する。
  - 期待結果: grade specialist evidence missing として blocked。
  - 関連 closure id: G3-C-004, G3-C-005
- `tc-g3-005` cli-positive:
  - 前提: fresh spec-reviewer evidence、resolved EAL、Strict specialist/fallback evidence、substantive requirement/design、executable plan、valid assurance contract が揃っている。
  - 操作: `workflow status --format json` と `guidance issue-execution` を実行する。
  - 期待結果: `state=ready`, `may_execute_approved_plan=true`。
  - 関連 closure id: G3-C-001〜G3-C-005
- `tc-g3-006` regression:
  - 前提: G2 の profile-aware draft routing tests が存在する。
  - 操作: `tests/cli_runtime/test_new.py` の relevant tests を実行する。
  - 期待結果: G2 routing が維持される。
  - 関連 closure id: G3-C-006, G3-C-007
- `tc-g3-007` parity:
  - 前提: provider docs/templates と dogfooding mirror を読む。
  - 操作: G3 wording の一致を diff / `rg` で確認する。
  - 期待結果: 意図しない drift がない。
  - 関連 closure id: G3-C-008, G3-C-090

## 5. 実装ステップ

各 step は次の共通契約を持つ。

- report evidence destination:
  - Red / alternative、Green、Refactor、discovered tests、closure delta は `report.md` の実装記録に記録する。
  - delegated worker を使う場合は Workflow Delegation Consent、Implementation Delegation Gate、Delegated Worker Evidence へ記録する。
  - material decision は Spec Interpretation / Decision Ledger へ記録し、必要に応じて design / plan amendment と re-review を行う。
- amendment trigger:
  - allowed paths 外の変更が必要になる。
  - AC / closure ID の追加・削除・意味変更が必要になる。
  - runtime hook が report template の stable headings / tokens では安全に判定できない。
  - PR / GitHub review policy、G2 routing、issue finish lifecycle へ scope が広がる。
  - reviewer が P0/P1 を出す、または required verification が実行不能になる。

### S00 Baseline / 採用証跡

- 目的:
  - delegated design / implementation-plan draft を読み、採用部分を canonical docs に反映したことを `report.md` に記録する。
- 変更対象:
  - active issue `requirement.md`
  - active issue `design.md`
  - active issue `plan.md`
  - active issue `report.md`
- close 条件:
  - EAL に delegated draft 2 件の採用判断がある。
  - Spec Authoring Gate に requirement/design/plan の promotion candidate が記録されている。
- planned contract:
  - scope: issue-local planning docs and discussion drafts.
  - test obligation: inspect-only。実装挙動は変えない。
  - red or alternative evidence requirement: initial `guidance issue-planning` が `design-not-substantive` を返すことを baseline evidence とする。
  - green verification:
    - `./spec-dock/scripts/spec-dock guidance issue-planning`
    - `./spec-dock/scripts/spec-dock guidance issue-execution`
  - refactor guardrail: implementation/runtime/provider docs は変更しない。
- delegation contract:
  - delegated role: `system-architect`, `implementation-planner`.
  - input docs: active issue requirement/design/plan/report, parent Epic docs, workflow/docs/runtime/tests.
  - allowed paths: active issue `discussions/` only for delegated workers; canonical issue docs only for main orchestrator.
  - forbidden changes: source code, provider docs/templates/tests, GitHub state.
  - acceptance criteria: delegated drafts are recorded as source input; not promotion evidence without fresh spec review.
  - required verification: source inspection and guidance commands.
  - reviewer focus: planning `spec-reviewer`.
  - stop conditions: draft self-claims authority/adoption/pass, missing source paths, canonical edit by delegated worker.
  - output required: draft path, summary, EAL/Delegated Draft Evidence rows.
- 具体テストケース一覧:
  - `tc-s00-001` inspect-only: 初期 planning block を解消する
    - 前提: active issue `design.md` は draft である。
    - 操作: `guidance issue-planning` を実行し、その後 canonical docs を具体化する。
    - 期待結果: `design-not-substantive` block が消え、planning docs が execution-ready candidate になる。
    - 失敗検出: template-only docs のまま execution へ進む回帰を検出する。
    - 検証方法: `guidance issue-planning` / `guidance issue-execution`。
    - 関連 closure id: G3-C-001, G3-C-099
- step closure contract:
  - G3-C-001〜G3-C-099 の planning candidate が report に記録される。
- step gate:
  - fresh planning `spec-reviewer` pass まで execution に進まない。
- 検証:
  - `./spec-dock/scripts/spec-dock guidance issue-planning`
  - fresh `spec-reviewer`

### S01 Docs / Template Evidence Contract

- 目的:
  - report evidence gate の記録先と accepted states を provider docs/templates と dogfooding mirror に明示する。
- 変更対象:
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_requirement.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_design.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/report.md`
  - 対応する `spec-dock/docs/...` / `spec-dock/templates/issue/report.md`
- close 条件:
  - G3-C-001〜G3-C-004, G3-C-006, G3-C-008 の docs/template contract が確認できる。
- planned contract:
  - scope: provider/dogfooding docs and Issue report template only.
  - test obligation: docs/template structural coverage and parity.
  - red or alternative evidence requirement: existing template/docs lack explicit Grade Specialist Evidence Gate or freshness/report evidence wording in one place.
  - green verification:
    - focused `tests/unit/infra/test_init_update.py` assertions where practical.
    - provider/dogfooding parity inspection.
  - refactor guardrail: runtime behavior and tests are not changed in S01.
- delegation contract:
  - delegated role: `doc-writer` if delegated; parent may integrate tightly scoped docs with Parent Implementation Exception if keeping docs/runtime wording synchronized.
  - input docs: requirement.md, design.md, plan.md, existing workflow/phase docs, issue report template.
  - allowed paths: paths listed in S01 変更対象 only.
  - forbidden changes: runtime code, CLI behavior, G2 draft routing, PR/GitHub policy.
  - acceptance criteria: accepted states and evidence destinations are visible and non-contradictory.
  - required verification: docs/template tests or inspection; `git diff --check`.
  - reviewer focus: spec-reviewer docs/spec alignment.
  - stop conditions: new wording implies waiver/provisional reviewer pass, or fallback replaces fresh `spec-reviewer`.
  - output required: changed docs/templates, verification result, report Docs Impact Resolution.
- 具体テストケース一覧:
  - `tc-s01-001` template: Issue report に G3 evidence slots がある
    - 前提: provider `templates/issue/report.md` を読む。
    - 操作: required headings / tokens を検索する。
    - 期待結果: Grade Specialist Evidence Gate、Spec Authoring Gate、Reviewer Gate Status、Final Spec Review Gate、EAL、Delegated Draft Evidence が存在する。
    - 失敗検出: agent が evidence を report のどこへ書くか判断できない regression を検出する。
    - 検証方法: focused template test または `rg` inspection。
    - 関連 closure id: G3-C-001, G3-C-002, G3-C-004
  - `tc-s01-002` parity: provider と dogfooding mirror の G3 wording が整合する
    - 前提: provider docs/templates と dogfooding mirror がある。
    - 操作: relevant files を diff / search する。
    - 期待結果: source-of-truth と mirror が意図せず drift していない。
    - 失敗検出: shipped scaffold と dogfooding docs の説明差異を検出する。
    - 検証方法: file diff inspection。
    - 関連 closure id: G3-C-008, G3-C-090
- step closure contract:
  - G3-C-001〜G3-C-004 / G3-C-006 / G3-C-008 が docs/template evidence で閉じる。
- step gate:
  - docs/template change 後に spec-reviewer の docs/spec alignment を通す。
- 検証:
  - template/docs inspection
  - `uv run pytest tests/unit/infra/test_init_update.py -k "Evidence Adoption Ledger or spec-reviewer or report template"` から実行可能な focused test を選ぶ。

### S02 Runtime Report Evidence Gate

- 目的:
  - `workflow status` / `guidance issue-execution` が report evidence missing / stale / blocked を readiness block として返す。
- 変更対象:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/workflow_state.py` または新規 domain helper
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py`
  - 必要なら presentation tests
- close 条件:
  - G3-C-001〜G3-C-005 が CLI / domain tests で確認できる。
  - Existing strict-legacy behavior と EAL lifecycle gate を不要に壊していない。
- planned contract:
  - scope: workflow readiness application/domain helper and tests.
  - test obligation: negative/positive CLI behavior, reason code, details, and regression around existing EAL gate.
  - red or alternative evidence requirement: write failing tests where `guidance issue-execution` incorrectly returns ready despite missing report evidence.
  - green verification:
    - `uv run pytest tests/unit/domain/test_workflow_state.py`
    - `uv run pytest tests/cli_runtime/test_workflow.py`
  - refactor guardrail: keep parser narrow; no agent invocation, no PR policy, no issue finish lifecycle redesign.
- delegation contract:
  - delegated role: `dev-coder`.
  - input docs: requirement.md, design.md, plan.md, S01 docs/template contract, target runtime files.
  - allowed paths: runtime paths and tests listed in S02 / S03.
  - forbidden changes: docs/template wording beyond S01, G2 routing, GitHub/PR observation, close lifecycle redesign.
  - acceptance criteria: missing/stale/non-pass evidence blocks readiness; complete evidence allows ready.
  - required verification: focused unit/CLI tests.
  - reviewer focus: code-reviewer for runtime behavior; QA reviewer for matrix sufficiency.
  - stop conditions: broad Markdown semantic inference required, existing strict-legacy behavior breaks unexpectedly, report template cannot support stable parsing.
  - output required: changed files, tests run, reason code matrix, Ledger Note if parser contract changes.
- 具体テストケース一覧:
  - `tc-s02-001` negative: fresh spec-reviewer evidence missing
    - 前提: substantive requirement/design、executable plan、valid assurance contract がある。
    - 操作: report evidence を missing/scaffold にして `guidance issue-execution` を実行する。
    - 期待結果: `state=blocked`, `may_execute_approved_plan=false`, reason は reviewer evidence missing。
    - 失敗検出: report evidence がなくても `ready` になる回帰を検出する。
    - 検証方法: `tests/cli_runtime/test_workflow.py`。
    - 関連 closure id: G3-C-001, G3-C-005
  - `tc-s02-002` negative: unresolved EAL blocks readiness
    - 前提: EAL に `stale` または `blocked` entry がある。
    - 操作: `workflow status --format json` と `guidance issue-execution` を実行する。
    - 期待結果: EAL block reason が出て readiness は blocked。
    - 失敗検出: unresolved delegated evidence があっても execution へ進む回帰を検出する。
    - 検証方法: `tests/cli_runtime/test_workflow.py` / existing authority tests。
    - 関連 closure id: G3-C-002, G3-C-003, G3-C-005
  - `tc-s02-003` negative: Strict specialist evidence missing
    - 前提: Strict authorized_profile issue で reviewer evidence はあるが specialist/fallback evidence がない。
    - 操作: `guidance issue-execution` を実行する。
    - 期待結果: grade specialist evidence missing で blocked。
    - 失敗検出: Strict/Critical が Standard 相当の証跡で通る回帰を検出する。
    - 検証方法: `tests/cli_runtime/test_workflow.py`。
    - 関連 closure id: G3-C-004, G3-C-005
  - `tc-s02-004` positive: 必須 report evidence が揃う
    - 前提: fresh spec-reviewer evidence、resolved EAL、Strict specialist/fallback evidence が揃っている。
    - 操作: `workflow status --format json` と `guidance issue-execution` を実行する。
    - 期待結果: `state=ready`, `may_execute_approved_plan=true`。
    - 失敗検出: 必要証跡が揃っても過剰に blocked になる regression を検出する。
    - 検証方法: `tests/cli_runtime/test_workflow.py`。
    - 関連 closure id: G3-C-001〜G3-C-005
- step closure contract:
  - G3-C-001〜G3-C-005 が runtime/CLI tests で閉じる。
- step gate:
  - code-reviewer と QA reviewer の指摘が P0/P1 なしになるまで次へ進まない。
- 検証:
  - `uv run pytest tests/unit/domain/test_workflow_state.py`
  - `uv run pytest tests/cli_runtime/test_workflow.py`

### S03 Regression / Coverage

- 目的:
  - G2 routing、existing EAL lifecycle、validate behavior、issue lifecycle behavior が維持されることを確認する。
- 変更対象:
  - tests only if coverage gap exists
- close 条件:
  - G3-C-006 / G3-C-007 が確認できる。
- planned contract:
  - scope: tests only unless regression failure reveals required fix.
  - test obligation: G2 routing and existing authority/EAL lifecycle regression.
  - red or alternative evidence requirement: covered-existing; identify existing tests that would fail if G2/EAL behavior regressed.
  - green verification: listed focused tests pass.
  - refactor guardrail: do not modify production behavior unless a regression is found and plan is amended.
- delegation contract:
  - delegated role: `dev-coder` or QA-focused reviewer if needed.
  - input docs: G2 issue report, current design, existing tests.
  - allowed paths: tests only, unless discovered regression requires amendment.
  - forbidden changes: production runtime fixes without plan amendment, PR policy.
  - acceptance criteria: G2 and EAL lifecycle tests pass.
  - required verification: listed commands.
  - reviewer focus: QA reviewer coverage adequacy.
  - stop conditions: test failures caused by current change require bounded fix and re-review.
  - output required: test commands/results and discovered risk entry.
- 具体テストケース一覧:
  - `tc-s03-001` regression: G2 profile draft routing remains intact
    - 前提: G2 tests exist in `tests/cli_runtime/test_new.py`.
    - 操作: relevant tests を実行する。
    - 期待結果: authorized_profile draft routing と no-write fail-closed tests が pass。
    - 失敗検出: G3 readiness work が draft generation を壊す回帰を検出する。
    - 検証方法: `uv run pytest tests/cli_runtime/test_new.py -k "profile_drafts or authorized_profile"`。
    - 関連 closure id: G3-C-006, G3-C-007
  - `tc-s03-002` regression: existing EAL lifecycle remains intact
    - 前提: authority tests が EAL stale/blocked behavior を持つ。
    - 操作: `tests/unit/domain/test_authority.py` を実行する。
    - 期待結果: existing EAL gate behavior が pass。
    - 失敗検出: G3 helper が existing lifecycle gate と矛盾する regression を検出する。
    - 検証方法: `uv run pytest tests/unit/domain/test_authority.py`。
    - 関連 closure id: G3-C-002, G3-C-003, G3-C-007
- step closure contract:
  - G3-C-006 / G3-C-007 が regression tests で閉じる。
- step gate:
  - regression failures は report に記録し、必要なら plan amendment。
- 検証:
  - `uv run pytest tests/cli_runtime/test_new.py -k "profile_drafts or authorized_profile"`
  - `uv run pytest tests/unit/domain/test_authority.py`
  - `uv run pytest tests/cli_runtime/test_workflow.py`

### S90 Docs Impact / Parity

- 目的:
  - provider source of truth と dogfooding mirror の docs/template drift を解消する。
- close 条件:
  - G3-C-008 / G3-C-090 が report に記録される。
- planned contract:
  - scope: provider/dogfooding docs/templates touched by G3.
  - test obligation: docs impact resolution and parity.
  - red or alternative evidence requirement: inspect-only; before/after diff confirms no unintended drift.
  - green verification: diff inspection, validate, diff check.
  - refactor guardrail: no unrelated formatting churn.
- delegation contract:
  - delegated role: `doc-writer` if delegated; parent may perform final parity edits.
  - input docs: changed provider/dogfooding docs/templates.
  - allowed paths: S01 docs/templates and active report only.
  - forbidden changes: runtime/tests unless discovered drift requires amendment.
  - acceptance criteria: provider source of truth and dogfooding mirror are synchronized or explicitly explained.
  - required verification: `git diff --check`, `validate`, parity inspection.
  - reviewer focus: spec-reviewer.
  - stop conditions: generated mirror would require unsafe overwrite; source-of-truth unclear.
  - output required: Docs Impact Resolution row and changed file list.
- 具体テストケース一覧:
  - `tc-s90-001` parity: provider/dogfooding G3 docs align
    - 前提: G3 touched docs/templates have provider and dogfooding copies.
    - 操作: relevant pairs を比較する。
    - 期待結果: 意図しない差分がない。
    - 失敗検出: shipped scaffold と local dogfooding docs の drift を検出する。
    - 検証方法: diff / `rg` inspection。
    - 関連 closure id: G3-C-008, G3-C-090
- step closure contract:
  - Docs Impact Resolution に結果が記録される。
- step gate:
  - spec-reviewer が docs/spec alignment を確認する。
- 検証:
  - `git diff --check`
  - provider/dogfooding relevant file diff inspection
  - `./spec-dock/scripts/spec-dock validate`

### S95 Final Review Gate

- 目的:
  - final QA / code / spec review を fresh に通す。
- close 条件:
  - qa-reviewer: test sufficiency pass
  - code-reviewer: issue-wide integrated diff pass
  - spec-reviewer: requirement/design/plan/report/docs/tests alignment pass
- planned contract:
  - scope: complete issue diff.
  - test obligation: reviewer gates are independent and fresh.
  - red or alternative evidence requirement: reviewer findings are authoritative gate evidence.
  - green verification: all reviewers pass after latest substantive change.
  - refactor guardrail: reviewer-fail fixes must be bounded and re-reviewed.
- delegation contract:
  - delegated role: qa-reviewer / code-reviewer / spec-reviewer.
  - input docs: final diff, active issue docs/report, Epic docs, test output.
  - allowed paths: read-only for reviewers.
  - forbidden changes: reviewer direct edits.
  - acceptance criteria: `review_status: pass` for all required reviewers.
  - required verification: reviewer final messages recorded in report.
  - reviewer focus: as named.
  - stop conditions: any P0/P1, stale review, unavailable/denied reviewer.
  - output required: findings, review_status, residual risk.
- 具体テストケース一覧:
  - `tc-s95-001` review: final QA/code/spec gates pass
    - 前提: implementation and tests are complete.
    - 操作: qa-reviewer、code-reviewer、spec-reviewer を実行する。
    - 期待結果: all pass; P0/P1なし。
    - 失敗検出: coverage gap、behavior regression、spec mismatch を検出する。
    - 検証方法: reviewer outputs in report。
    - 関連 closure id: G3-C-095
- step closure contract:
  - Reviewer Gate Status / Final QA / Final Code / Final Spec gates に pass が記録される。
- step gate:
  - P0/P1 が残る場合は S99 へ進まない。
- 検証:
  - reviewer pass evidence in `report.md`

### S99 Local Handoff / Commit Gate

- 目的:
  - G3 checkpoint commit を作成し、個別 PR なしで G4 / `iss-00255` へ渡す。
- close 条件:
  - focused tests、`make lint`、`validate`、`git diff --check` が pass。
  - commit 後 `git status --short` が clean。
  - `./spec-dock/scripts/spec-dock issue finish` が成功。
- planned contract:
  - scope: final local checkpoint only.
  - test obligation: final focused suite, lint, validate, diff check, clean worktree.
  - red or alternative evidence requirement: covered by S01〜S95; S99 is final integration verification.
  - green verification: final command list passes.
  - refactor guardrail: no new behavior changes after final reviewer pass except report evidence updates; if changed, rerun relevant reviewer.
- delegation contract:
  - delegated role: N/A for commit/finish; parent orchestrator owns lifecycle.
  - input docs: final report, test output, reviewer pass, git status.
  - allowed paths: report final ledger only after reviewers, then git index.
  - forbidden changes: new implementation after review without re-review, PR creation, G4 work.
  - acceptance criteria: clean checkpoint commit and `issue finish` success.
  - required verification: final commands and post-commit status.
  - reviewer focus: already completed in S95.
  - stop conditions: dirty worktree after commit, failed finish, failed validation, PR requested prematurely.
  - output required: commit hash, issue finish output, baton readiness.
- 具体テストケース一覧:
  - `tc-s99-001` final: local checkpoint is clean
    - 前提: S01〜S95 complete.
    - 操作: final commands、commit、`issue finish` を実行する。
    - 期待結果: commands pass、commit 後 clean、issue closed、no per-issue PR。
    - 失敗検出: unfinished diff や invalid spec-dock state を検出する。
    - 検証方法: `git status --short`; `./spec-dock/scripts/spec-dock issue finish`。
    - 関連 closure id: G3-C-099
- commit:
  - commit候補: G3 の docs/template/runtime/tests/report を review 可能な単位としてコミットする。
  - commit前確認:
    - [ ] このマイルストーンの差分だけで意味が通る
    - [ ] 必要な検証が完了している
    - [ ] `report.md` に証跡がある
    - [ ] G4 の未完了差分が混ざっていない

## 6. 変更対象一覧

予定:

- provider docs/templates:
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_requirement.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_design.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/report.md`
- dogfooding mirror:
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/phase_requirement.md`
  - `spec-dock/docs/phase_design.md`
  - `spec-dock/docs/phase_plan_issue.md`
  - `spec-dock/templates/issue/report.md`
- runtime:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/workflow_state.py` または新規 helper
- tests:
  - `tests/cli_runtime/test_workflow.py`
  - `tests/unit/domain/test_workflow_state.py`
  - 必要なら `tests/unit/infra/test_init_update.py`
- issue-local evidence:
  - active issue `report.md`

## 7. 禁止変更

- G2 の `new doc draft-design` / `draft-plan` routing を変更しない。
- PR observation / GitHub review / code-reviewer policy を再設計しない。
- issue finish の GitHub close / active clear lifecycle を再設計しない。
- Report evidence を完全 JSON schema 化しない。
- Historical delegated-authoring artifacts を削除・rename・validation failure 化しない。
- Issue 単位 PR を作成しない。

## 8. Reviewer / QA 計画

| Gate | Reviewer | Scope | Pass 条件 |
|---|---|---|---|
| Planning review | spec-reviewer | requirement/design/plan/report planning evidence | `review_status: pass` |
| Runtime/code review | code-reviewer | workflow readiness hook、parser/helper、tests | P0/P1 なし、behavior regression なし |
| QA review | qa-reviewer | AC / closure / test sufficiency | missing/stale/evidence matrix が十分 |
| Final spec review | spec-reviewer | canonical docs/report/implementation/tests/docs parity | `review_status: pass` |

## 9. 最終品質ゲート

- static analysis / lint:
  - 実行対象: `make lint`
  - pass条件: ruff / format / mypy が成功する。
- tests:
  - 実行対象:
    - `uv run pytest tests/unit/domain/test_workflow_state.py`
    - `uv run pytest tests/unit/domain/test_authority.py`
    - `uv run pytest tests/cli_runtime/test_workflow.py`
    - relevant `tests/cli_runtime/test_new.py` regression
    - relevant `tests/unit/infra/test_init_update.py` docs/template assertions
  - pass条件: すべて成功する。実行できない場合は理由と代替確認を `report.md` に記録する。
- spec-dock validation:
  - `./spec-dock/scripts/spec-dock validate`
- report:
  - [ ] 実行したコマンド、結果、未実施理由を `report.md` に記録する。
- commit:
  - commit候補: 最終品質ゲート通過後の成果をレビュー可能な単位としてコミットする。
  - commit前確認:
    - [ ] 静的解析 / lint が完了している
    - [ ] 必要なテストが完了している
    - [ ] `report.md` に証跡がある
    - [ ] 未完了差分が混ざっていない

## 10. Epic Branch Baton / PR Policy

- この Issue では個別 PR を作成しない。
- G3 完了後、`issue finish` し、同じ累積 branch HEAD から G4 / `iss-00255` を開始する。
- Epic PR は G4 完了後、Epic 最終品質ゲートを通過してから 1 本だけ作成する。
