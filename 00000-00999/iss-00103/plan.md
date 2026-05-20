---
種別: 実装計画書（Issue）
ID: "iss-00103"
タイトル: "Agentic TDD report decision ledger"
関連GitHub: ["#103"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-21"
依存: ["requirement.md", "design.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00103 Agentic TDD report decision ledger — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001: worker `Ledger Note` から report decision ledger へ統合できる。
  - AC-002: material decision がない小規模 issue を軽量に閉じられる。
  - AC-003: ledger entry の status / disposition / evidence / follow-up を completion 前に閉じられる。
  - AC-004: worker / orchestrator の著者責任境界を保てる。
  - AC-005: reviewer が decision traceability / promotion / open decision を監査できる。
- EC:
  - EC-001: no-decision lightweight mode。
  - EC-002: provisional worker note。
  - EC-003: reviewer finding disposition。
  - EC-004: legacy report compatibility。
- 制約:
  - provider-side source first。
  - `plan.md` は実装前 contract、`report.md` は observed evidence + decision ledger。
  - runtime strict validator と historical report migration は対象外。

## 依存関係から導く実装順序
- 依存関係の正本:
  - `design.md` の Document Ownership Matrix、Module Dependency Diagram、ディレクトリ / ファイル変更計画。
- 順序ルール:
  - 先に shipped docs/templates/skills/agent text の契約を実装し、次に structural tests で固定する。
  - provider-side source を更新してから dogfooding mirror を sync / inspect する。
- step 依存 summary:
  - S01:
    - 依存: requirement / design pass。
    - unblock: report ledger contract を provider-side assets に実装する。
    - 対象ファイル: provider docs/templates/install_root assets。
  - S02:
    - 依存: S01 provider asset changes。
    - unblock: structural regression tests。
    - 対象ファイル: `tests/test_init_update.py`。
  - S90:
    - 依存: S01 / S02。
    - unblock: dogfooding mirror refresh / docs impact resolution。
  - S99:
    - 依存: S01 / S02 / S90 commit。
    - unblock: final QA / code / spec review and final report.

## ステップ一覧
- S01:
  - 観測可能な振る舞い: shipped docs/templates/skills/agent configs が report decision ledger contract を表現する。
  - 依存: requirement/design pass。
  - unblock: S02 structural assertions。
  - 対象ファイル: `src/spec_dock/assets/spec_dock/...`, `src/spec_dock/assets/install_root/...`
  - 閉じる要件: AC-001, AC-002, AC-003, AC-004, AC-005, EC-001, EC-002, EC-003, EC-004
  - レビューゲート: spec-reviewer
- S02:
  - 観測可能な振る舞い: shipped asset contract が structural tests で固定される。
  - 依存: S01。
  - unblock: S90 sync / final gates。
  - 対象ファイル: `tests/test_init_update.py`
  - 閉じる要件: AC-001, AC-002, AC-003, AC-004, AC-005
  - レビューゲート: code-reviewer
- S90:
  - 観測可能な振る舞い: dogfooding mirror が provider source と整合し、docs impact が解決している。
  - 依存: S01, S02。
  - unblock: S99。
  - 対象ファイル: `spec-dock/`, `.agents/`, `.codex/` mirror
  - 閉じる要件: provider-side source / dogfooding mirror constraint
  - レビューゲート: spec-reviewer
- S99:
  - 観測可能な振る舞い: issue 全体の closure / review / validation / final report が complete に到達する。
  - 依存: S01, S02, S90。
  - レビューゲート: qa-reviewer, issue-wide code-reviewer, final spec-reviewer

## 要件 ↔ ステップ対応
- AC-001 -> S01, S02
- AC-002 -> S01, S02
- AC-003 -> S01, S02, S99
- AC-004 -> S01, S02
- AC-005 -> S01, S02, S99
- EC-001 -> S01
- EC-002 -> S01
- EC-003 -> S01
- EC-004 -> S01

## Spec-Locked Closure Index（仕様固定クロージャ索引）

| id | step | slice | type | spec link | locked expectation | observable input/state | bug class guarded | required | evidence level | closure evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | report template | acceptance | AC-001, AC-002, AC-003 | `templates/issue/report.md` contains `Spec Interpretation / Decision Ledger`, no-decision lightweight phrase, Status/Disposition/Type values, Options Considered, and disposition evidence guidance. | provider report template text | missing decision audit trail | yes | inspect-only | S01 report closure + S02 structural test |
| tc-002 | S01 | worker handoff | acceptance | AC-001, AC-004, EC-002 | skill / prompt / worker agent text requires `Ledger Note` or explicit no-material-decision output and states proposed decision is not accepted decision. | provider skill/prompt/agent text | worker decisions become untracked accepted decisions | yes | inspect-only | S01 report closure + S02 structural test |
| tc-003 | S01 | reviewer audit | acceptance | AC-003, AC-005, EC-003 | reviewer agent text checks ledger absence, `Status=open`, missing disposition evidence, report-only durable decision, follow-up/promotion evidence, and no-decision phrase validity. | provider reviewer agent configs | review passes without traceability | yes | inspect-only | S01 report closure + S02 structural test |
| tc-004 | S01 | workflow lifecycle | acceptance | AC-003, EC-004 | workflow docs define report decision ledger lifecycle, promotion/completion semantics, legacy non-retroactive handling, and plan/report boundary. | provider workflow docs | report ledger becomes design graveyard or legacy blocker | yes | inspect-only | S01 report closure + S02 structural test |
| tc-005 | S02 | structural regression | regression | AC-001..AC-005 | `tests/test_init_update.py` fails before contract markers are present and passes after S01 implementation. | targeted unittest | shipped asset drift | yes | red-required | S02 red/green evidence |
| tc-006 | S90 | dogfooding mirror | acceptance | constraints | provider asset changes are reflected or intentionally inspected in dogfooding mirror. | `./spec-dock/scripts/spec-dock sync`, diff inspection | provider / consumer drift | yes | inspect-only | S90 closure |
| tc-007 | S99 | final quality | acceptance | all AC/EC | final QA, issue-wide code review, and final spec review pass; validate/sync evidence recorded. | final report / reviewer verdicts | incomplete delivery | yes | inspect-only | S99 closure |

## レビュー / QA ゲート方針
- RG1 S01 step review:
  - reviewer: spec-reviewer
  - pass 条件: provider docs/templates/skills/agent text が requirement/design/plan と整合し、report ledger contract を過不足なく表現している。
- RG2 S02 step review:
  - reviewer: code-reviewer
  - pass 条件: structural tests が適切な shipped asset markers を固定し、過剰な semantic validation をしていない。
- RG3 S90 docs impact review:
  - reviewer: spec-reviewer
  - pass 条件: dogfooding mirror と provider source の整合 / docs impact が説明されている。
- QG1 S99 final QA:
  - reviewer: qa-reviewer
  - pass 条件: obligation coverage と test sufficiency が十分。
- CG1 S99 issue-wide code review:
  - reviewer: code-reviewer
  - pass 条件: integrated diff に構造 / regression risk の blocker がない。
- SG1 S99 final spec review:
  - reviewer: spec-reviewer
  - pass 条件: requirement / design / plan / report / implementation / tests / docs が一致する。

## 実行ルール（全ステップ共通）
- `plan.md` には planned contract を置き、実行結果は `report.md` に記録する。
- S01 の shipped docs/templates/skills/workflow text は `doc-writer` に委任する。
- S02 の tests は `dev-coder` に委任する。
- worker は material decision がある場合 `Ledger Note` を返し、ない場合も `No material implementation decisions beyond the approved plan.` を返す。
- reviewer fail 時は bounded follow-up を同じ worker または適切な worker に再委任し、re-review pass まで回す。

## 実装ステップ

### S01 — Provider assets expose report decision ledger contract
- behavior goal:
  - shipped report template / workflow docs / skill / prompt / agent configs が、report decision ledger contract を表現する。
- design 参照:
  - Document Ownership Matrix
  - Ledger Entry Contract
  - Ledger Note Contract
  - Reviewer Gate Contract
- 依存:
  - requirement review pass
  - design review pass
- unblock:
  - S02 structural tests
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/templates/issue/report.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `src/spec_dock/assets/install_root/.codex/prompts/execute-issue.md`
  - `src/spec_dock/assets/install_root/.codex/agents/dev-coder.toml`
  - `src/spec_dock/assets/install_root/.codex/agents/doc-writer.toml`
  - `src/spec_dock/assets/install_root/.codex/agents/utility-worker.toml`
  - `src/spec_dock/assets/install_root/.codex/agents/code-reviewer.toml`
  - `src/spec_dock/assets/install_root/.codex/agents/qa-reviewer.toml`
  - `src/spec_dock/assets/install_root/.codex/agents/spec-reviewer.toml`
- planned contract:
  - scope:
    - report decision ledger section、worker note obligation、reviewer audit checks、promotion/completion semantics を provider assets に追加する。
  - test obligation:
    - closure id: tc-001, tc-002, tc-003, tc-004
    - coverage rationale: report template、worker handoff、reviewer audit、workflow lifecycle の4面がそろわないと contract が再現されない。
  - Red / alternative evidence requirement:
    - inspect-only:
      - code behavior ではなく shipped docs/template/agent text contract のため、実装前の欠落確認と S02 structural red test で担保する。
      - 代替 evidence path: S01 開始時に target files が required markers を欠くことを report に記録する。
  - implementation scope:
    - allowed paths: 対象ファイルのみ。
    - forbidden changes: runtime CLI behavior、historical issue migration、新規 `implementation-notes.md` artifact、unrelated docs。
  - Green verification:
    - target file marker inspection。
    - `git diff --check -- <S01 targets>`。
  - Refactor / cleanup guardrail:
    - duplicate policy を増やさず、full workflow copy を skill / prompt に置かない。
  - closure evidence requirements:
    - Step Contract Closure: tc-001..tc-004
    - Test Contract Closure: inspect-only evidence
    - Closure Coverage: S01 inspect-only evidence で tc-001..tc-004 を close する。S02 tests は post-S01 regression lock として別 step で close する。
  - report evidence destination:
    - `report.md` の S01 session、Delegated Worker Evidence、Reviewer Gate Status、Step Commit Gate。
  - amendment trigger:
    - `Status` / `Disposition` allowed values の変更。
    - `implementation-notes.md` 標準化が必要になった場合。
    - runtime strict validator 実装が必要になった場合。

#### delegation contract
- delegated role:
  - doc-writer
- input docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - current target files
- allowed paths:
  - S01 対象ファイル
- forbidden changes:
  - runtime code
  - tests
  - dogfooding mirror direct edits
  - accepted requirement/design/plan semantics changes
- acceptance criteria:
  - tc-001..tc-004
- required tests or docs-only verification:
  - targeted marker inspection
  - `git diff --check -- <S01 targets>`
- reviewer focus:
  - spec-reviewer docs/spec alignment
- output required:
  - changed files
  - verification result
  - Ledger Note or no-material-decision statement
  - unresolved risks
- stop conditions:
  - need to add standard `implementation-notes.md`
  - need to change runtime validator
  - requirement/design conflict

#### 具体テストケース一覧
- `tc-s01-001` inspect-only: report template contains decision ledger scaffold.
  - 前提: provider report template exists.
  - 操作: template text を確認する。
  - 期待結果: `Spec Interpretation / Decision Ledger`、`No material interpretation changes.`、`No decision entries.`、`Options Considered`、`Status`、`Disposition`、`promoted_to_design` が存在する。
  - 失敗検出: marker が欠ける場合、targeted inspection または S02 structural test が失敗する。
  - 検証方法: targeted `rg` / S02 structural test。
  - 関連 closure id: tc-001
- `tc-s01-002` inspect-only: worker handoff contains Ledger Note schema.
  - 前提: skill / prompt / worker agent configs exist.
  - 操作: `spec-dock-issue-execution` skill、execute issue prompt、`dev-coder.toml`、`doc-writer.toml`、`utility-worker.toml` を確認する。
  - 期待結果: skill / prompt / worker config に `Ledger Note`、`source-agent`、`options considered`、`needs orchestrator decision`、no-material-decision phrase が存在する。
  - 失敗検出: worker が proposed decision を accepted decision として扱う余地が残る場合、inspection と S02 structural test が失敗する。
  - 検証方法: targeted `rg` / S02 structural test。
  - 関連 closure id: tc-002
- `tc-s01-003` inspect-only: reviewer configs contain ledger audit checks.
  - 前提: reviewer agent configs exist.
  - 操作: `code-reviewer.toml`、`qa-reviewer.toml`、`spec-reviewer.toml` を確認する。
  - 期待結果: reviewer configs に `Status=open`、`report-only`、`durable decision`、`promoted_to_design` / follow-up evidence などが存在する。
  - 失敗検出: open decision や report-only durable decision を reviewer が検出できない文面の場合、inspection と S02 structural test が失敗する。
  - 検証方法: targeted `rg` / S02 structural test。
  - 関連 closure id: tc-003
- `tc-s01-004` inspect-only: workflow docs define lifecycle and legacy compatibility.
  - 前提: provider workflow / authoring docs exist.
  - 操作: `workflow_issue.md` と `authoring/issue-plan.md` を確認する。
  - 期待結果: workflow docs に decision ledger lifecycle、promotion/completion semantics、legacy non-retroactive handling が存在する。
  - 失敗検出: legacy report を遡及 blocker にする、または plan/report boundary が曖昧な場合、inspection と S02 structural test が失敗する。
  - 検証方法: targeted `rg` / S02 structural test。
  - 関連 closure id: tc-004

#### step closure contract
- closure id:
  - tc-001, tc-002, tc-003, tc-004
- close 条件:
  - S01 target files contain the required contract markers.
  - spec-reviewer pass.
- 検証 evidence:
  - target marker inspection
  - `git diff --check`
- report evidence:
  - Step Contract Closure
  - Test Contract Closure
  - Closure Coverage
  - Closure Delta
- 残リスク:
  - semantic correctness は S01 spec-reviewer と S99 final spec-reviewer が確認する。

#### step gate
- step reviewer gate:
  - reviewer: spec-reviewer
  - pass 条件: review_status: pass
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S01 provider asset changes + S01 report evidence

### S02 — Structural tests lock shipped report decision ledger contract
- behavior goal:
  - S01 の shipped asset contract が structural tests で固定される。
- design 参照:
  - テスト戦略
- 依存:
  - S01 committed
- unblock:
  - S90 dogfooding mirror
- 対象ファイル:
  - `tests/test_init_update.py`
- planned contract:
  - scope:
    - shipped asset marker assertions を追加する。
  - test obligation:
    - closure id: tc-005
    - coverage rationale: future scaffold drift を防ぐ。
  - Red / alternative evidence requirement:
    - red-required:
      - S01 実装後でも、S02 test を先に追加して未実装 marker が残っていれば fail することを確認する。S01 が先に完了している場合は test sensitivity evidence として、一時的に未存在 marker または old expectation を使った fail を記録してから正しい marker へ戻す。
  - implementation scope:
    - allowed paths: `tests/test_init_update.py`
    - forbidden changes: provider assets、runtime code、dogfooding mirror。
    - exception: structural test creation reveals an S01 target asset drift from the approved design (for example, missing Type vocabulary or disposition evidence guidance). In that case, the orchestrator may correct only the affected S01 provider asset, record the discovered drift / scope delta in `report.md`, and require code-reviewer re-review before closing S02.
  - Green verification:
    - `uv run python -m unittest tests.test_init_update.TestInitUpdate.<new_test_method>`
    - `uv run python -m unittest tests.test_init_update.TestInitUpdate.test_issue_102_agentic_tdd_contract_assets`
  - Refactor / cleanup guardrail:
    - tests should assert structure / markers only; no semantic parser or runtime strict validator.
  - report evidence destination:
    - `report.md` S02 session.
  - amendment trigger:
    - test requires runtime validator or semantic parser.
    - S02 discovers that an S01 provider asset does not actually satisfy tc-001..tc-004 and must be corrected before the structural test can honestly close.

#### delegation contract
- delegated role:
  - dev-coder
- input docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - S01 target files
  - `tests/test_init_update.py`
- allowed paths:
  - `tests/test_init_update.py`
- forbidden changes:
  - provider assets
  - runtime code
  - dogfooding mirror
- orchestrator exception:
  - If S02 exposes an S01 provider asset drift, the main orchestrator may correct the minimum affected S01 target file, but must record it as discovered drift / closure delta and obtain code-reviewer re-review.
- acceptance criteria:
  - tc-005
- required tests or docs-only verification:
  - targeted red / green unittest evidence
- reviewer focus:
  - code-reviewer
- output required:
  - changed files
  - red/green commands and results
  - Ledger Note or no-material-decision statement
  - unresolved risks
- stop conditions:
  - test command cannot run due environment
  - required markers cannot be asserted without semantic parser

#### 具体テストケース一覧
- `tc-s02-001` structural regression: shipped assets contain decision ledger markers.
  - 前提: S01 provider assets updated.
  - 操作: new test reads assets via `cli._assets_dir()`.
  - 期待結果: report template / workflow / skill / prompt / agent configs contain required markers.
  - 失敗検出: marker removal causes targeted unittest failure.
  - 検証方法: `uv run python -m unittest tests.test_init_update.TestInitUpdate.<new_test_method>`
  - 関連 closure id: tc-005

#### step closure contract
- closure id:
  - tc-005
- close 条件:
  - red evidence or sensitivity evidence recorded.
  - targeted unittest passes.
  - code-reviewer pass.
- 検証 evidence:
  - targeted unittest
- report evidence:
  - Red/Green/Refactor Evidence
  - Test Contract Closure
  - Closure Coverage
- 残リスク:
  - full suite may have existing environment issues; targeted result is required, full suite attempted when practical.

#### step gate
- step reviewer gate:
  - reviewer: code-reviewer
  - pass 条件: review_status: pass
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S02 tests + S02 report evidence + plan amendment evidence + minimum S01 provider template correction discovered by tc-005

### S90 — docs impact resolution / dogfooding mirror refresh
- behavior goal:
  - provider-side report ledger contract changes are reflected in the dogfooding mirror or explicitly inspected as intentionally unchanged.
- design 参照:
  - provider-side source first
  - dogfooding mirror verification
- 依存:
  - S01 committed
  - S02 committed
- unblock:
  - S99 final quality gate
- 対象ファイル:
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/authoring/issue-plan.md`
  - `spec-dock/templates/issue/report.md`
  - `.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `.codex/prompts/execute-issue.md`
  - `.codex/agents/*.toml`
- planned contract:
  - scope:
    - `./spec-dock/scripts/spec-dock sync` を実行し、provider asset changes を dogfooding mirror へ反映する。
    - mirror diff を inspect し、追加 docs impact が必要なら doc-writer に委任する。
  - test obligation:
    - closure id: tc-006
    - coverage rationale: shipped asset API change は consumer repo に反映されて初めて完了とみなせる。
  - Red / alternative evidence requirement:
    - inspect-only:
      - code test ではなく sync / validate / diff inspection で閉じる。
  - implementation scope:
    - allowed paths: dogfooding mirror paths generated by sync and S90 report evidence。
    - forbidden changes: provider source direct edits, runtime code, unrelated historical issue docs。
  - Green verification:
    - `./spec-dock/scripts/spec-dock sync`
    - `./spec-dock/scripts/spec-dock validate`
    - mirror marker inspection
  - Refactor / cleanup guardrail:
    - sync output 以外の mirror 手編集を避ける。
  - report evidence destination:
    - `report.md` S90 session, S90 Docs Impact Resolution, Reviewer Gate Status, Step Commit Gate。
  - amendment trigger:
    - sync cannot update required mirror assets。
    - additional docs impact outside S01 design appears。

#### delegation contract
- delegated role:
  - doc-writer / N/A
- input docs:
  - S01/S02 committed changes
  - provider/mirror diff
- allowed paths:
  - mirror files generated by sync
  - additional docs only if spec-reviewer requires them
- forbidden changes:
  - provider source
  - runtime code
  - unrelated issue docs
- acceptance criteria:
  - tc-006
- required tests or docs-only verification:
  - sync / validate / marker inspection
- reviewer focus:
  - spec-reviewer
- output required:
  - sync result
  - validate result
  - mirror changed files
  - docs impact decision
- stop conditions:
  - sync fails
  - mirror differs from provider source unexpectedly

#### 具体テストケース一覧
- `tc-s90-001` inspect-only: dogfooding mirror reflects provider report ledger contract.
  - 前提: S01/S02 are committed and worktree is clean enough to inspect generated changes.
  - 操作: `./spec-dock/scripts/spec-dock sync` を実行し、mirror files を確認する。
  - 期待結果: mirror report template / workflow docs / skill / prompt / agent configs contain the same report decision ledger markers as provider source, or any intentional difference is documented.
  - 失敗検出: required marker が mirror にない、または sync で unrelated destructive change が出る。
  - 検証方法: `./spec-dock/scripts/spec-dock sync`, `./spec-dock/scripts/spec-dock validate`, targeted marker inspection。
  - 関連 closure id: tc-006

#### step closure contract
- closure id:
  - tc-006
- close 条件:
  - sync / validate pass。
  - mirror marker inspection pass。
  - spec-reviewer pass。
- 検証 evidence:
  - sync output
  - validate output
  - mirror diff / marker inspection
- report evidence:
  - S90 Docs Impact Resolution
  - Step Contract Closure
  - Test Contract Closure
  - Closure Coverage
- 残リスク:
  - generated mirror diff が大きい場合は S90 report に scope を記録する。

#### step gate
- step reviewer gate:
  - reviewer: spec-reviewer
  - pass 条件: review_status: pass
- commit / no-op gate:
  - closure 状態: committed / approved-no-op
  - commit 範囲: dogfooding mirror changes + S90 report evidence
  - no-op の場合: sync 後に provider/mirror が既に一致している evidence を report に残す。

### S99 — final quality gate
- behavior goal:
  - issue-wide integrated diff satisfies all AC/EC and is ready for PR.
- design 参照:
  - final quality gate / completion policy
- 依存:
  - S01 committed
  - S02 committed
  - S90 committed or approved-no-op
- 対象ファイル:
  - all changed files in issue diff
  - `report.md`
- planned contract:
  - scope:
    - final QA, issue-wide code review, final spec review, final validation, final report ledger。
  - test obligation:
    - closure id: tc-007
    - coverage rationale: issue completion requires integrated validation and final reviewer gates beyond per-step reviews。
  - Red / alternative evidence requirement:
    - inspect-only:
      - final gate reviews inspect already implemented artifacts and test evidence。
  - implementation scope:
    - allowed paths: final report updates and bounded fixes required by final reviewers。
    - forbidden changes: new scope beyond requirement/design/plan without amendment。
  - Green verification:
    - `./spec-dock/scripts/spec-dock validate`
    - S02 targeted unittest
    - full or broader unittest command when practical; if environment prevents it, record blocker / residual risk and targeted evidence。
  - Refactor / cleanup guardrail:
    - final fixes must be reviewer-driven and bounded。
  - report evidence destination:
    - Final QA Gate
    - Final Code Review Gate
    - Final Spec Review Gate
    - Final Commit
    - Step Contract Closure / Closure Coverage for tc-007
  - amendment trigger:
    - final reviewer requests scope, schema, status/disposition, or runtime validator changes outside approved plan。

#### 具体テストケース一覧
- `tc-s99-001` inspect-only: final quality gates pass.
  - 前提: S01/S02/S90 are closed and report contains their evidence.
  - 操作: qa-reviewer、issue-wide code-reviewer、final spec-reviewer を実行し、validate と targeted unittest を再実行する。
  - 期待結果: all final reviewers return `review_status: pass`; validate and targeted unittest pass; report records final evidence and external delivery evidence destination.
  - 失敗検出: any final reviewer fail, required command fail, missing closure evidence, or unresolved blocker in report.
  - 検証方法: reviewer outputs, `./spec-dock/scripts/spec-dock validate`, targeted unittest, report inspection。
  - 関連 closure id: tc-007

#### step closure contract
- closure id:
  - tc-007
- close 条件:
  - all final gates pass。
  - validate pass。
  - targeted unittest pass。
  - final report ledger records closure and final commit scope。
- 検証 evidence:
  - reviewer outputs
  - command output
  - final report entries
- report evidence:
  - Final QA Gate
  - Final Code Review Gate
  - Final Spec Review Gate
  - Final Commit
  - Closure Coverage
- 残リスク:
  - full suite residuals, if any, must be classified as existing environment issue or fixed before completion。

#### step gate
- final QA gate:
  - reviewer: qa-reviewer
  - pass 条件: review_status: pass
- issue-wide code review gate:
  - reviewer: code-reviewer
  - pass 条件: review_status: pass
- final spec review gate:
  - reviewer: spec-reviewer
  - pass 条件: review_status: pass
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: final report ledger and any final reviewer fixes

## Final Exit Contract
- issue finish 前に必須:
  - active issue が `iss-00103` であること。
  - `./spec-dock/scripts/spec-dock validate` pass。
  - required targeted unittest pass。
  - S01, S02, S90, S99 の closure id が `report.md` で pass / committed / approved-no-op として閉じていること。
  - per-step reviewer gates and final QA / code / spec gates are `passed`。
  - final commit exists and worktree has no unintended staged / unstaged changes。
  - `./spec-dock/scripts/spec-dock issue finish` を実行し、GitHub issue `#103` が closed になること。
- PR delivery:
  - issue finish 後、branch を push し、PR を作成する。
  - PR monitor checks CI / review status.
  - critical review findings and failing CI are fixed, re-reviewed, and re-pushed until PR is mergeable or blocked with documented external reason.
