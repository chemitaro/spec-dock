---
種別: 実装計画書（Issue）
ID: "iss-00114"
タイトル: "Delegated Draft Evidence Schema"
関連GitHub: ["#114"]
状態: "draft"
作成者: "Codex"
最終更新: "2026-05-23"
依存: ["requirement.md", "design.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00114 Delegated Draft Evidence Schema — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001 provider source update
  - AC-002 validation / parity evidence
  - AC-003 final spec review
- EC:
  - EC-001 documented uncertainty path
  - EC-002 provider/consumer drift handling
- 制約:
  - 親 Epic non-scope を超えない。

## 依存関係から導く実装順序
- 依存関係の正本:
  - `design.md` の provider-first dependency and file change plan。
- 順序ルール:
  - Provider source -> dogfooding mirror/parity -> tests/validate/sync -> report/review。
- step 依存 summary:
  - S01: Provider source update; depends on iss-00113; unblocks S02.
  - S02: Dogfooding parity and tests; depends on S01; unblocks S90/S99.
  - S90: Docs impact/report update; depends on S02.
  - S99: Final quality gate; depends on S90.

## ステップ一覧
- S01:
  - 観測可能な振る舞い: `Draft evidence schema` contract exists in provider-side source of truth.
  - 依存: iss-00113
  - unblock: S02
  - 対象ファイル: src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md; src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/report.md; src/spec_dock/assets/spec_dock/system/active-none/{initiative,epic,issue}/report.md; dogfooding mirrors
  - 閉じる要件: AC-001
  - レビューゲート: spec-reviewer for docs/skill/template alignment, code-reviewer if tests/runtime are touched.
- S02:
  - 観測可能な振る舞い: dogfooding mirror and verification evidence reflect provider change.
  - 依存: S01
  - unblock: S90, S99
  - 対象ファイル: dogfooding mirrors / tests as applicable
  - 閉じる要件: AC-002, EC-002
  - レビューゲート: reviewer matching changed surface.
- S90:
  - 観測可能な振る舞い: docs impact and report evidence are complete.
  - 閉じる要件: EC-001, docs impact.
- S99:
  - 観測可能な振る舞い: final validation/review pass and clean closure evidence.
  - 閉じる要件: AC-003.

## 要件 ↔ ステップ対応
- AC-001 -> S01
- AC-002 -> S02
- AC-003 -> S99
- EC-001 -> S90 / tc-004
- EC-002 -> S02 / tc-005

## Spec-Locked Closure Index（仕様固定クロージャ索引）
| id | step | slice | type | spec link | locked expectation | observable input/state | bug class guarded | required | evidence level | closure evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | provider contract | acceptance | AC-001 | Provider source contains the Draft evidence schema contract. | target provider files | missing shipped contract | yes | inspect-only | report step closure |
| tc-002 | S02 | parity | acceptance | AC-002 | Dogfooding mirror/tests/validation reflect provider change or document intended no-op. | diff + command output | provider/consumer drift | yes | inspect-only | report step closure |
| tc-003 | S99 | final review | acceptance | AC-003 | Final reviewer confirms issue docs/report/diff alignment. | reviewer output | spec drift | yes | manual-required | report final gate |
| tc-004 | S90 | documented uncertainty | exception | EC-001 | If host/path/target uncertainty blocks verified implementation, the issue records uncertainty and does not claim false success. | report exception evidence | false verified claim | yes | inspect-only | report S90 closure |
| tc-005 | S02 | parity drift | exception | EC-002 | Provider/consumer drift is either corrected or explicitly documented as intended. | provider/consumer diff | silent drift | yes | inspect-only | report S02 closure |

## レビュー / QA ゲート方針
- RG1 step review:
  - docs/skill/template-only changes: `spec-reviewer` docs/spec alignment.
  - tests/runtime/scaffold behavior changes: `code-reviewer`.
- QG1 final QA:
  - Use `qa-reviewer` when tests/manual evidence are substantial; otherwise record docs-only rationale and final spec review.
- SG1 final spec review:
  - `spec-reviewer` checks requirement / design / plan / report / diff alignment.

## 実行ルール（全ステップ共通）
- Observed evidence goes to `report.md`.
- If target files differ from design because implementation reveals a better provider surface, record the reason and rerun spec review if scope changes.
- Do not implement parent Epic non-scope items.

## 実装ステップ

### S01 — Provider source update
- behavior goal:
  - Provider-side source of truth contains the `Draft evidence schema` contract.
- design 参照:
  - `design.md` file change plan and parent Epic design.
- 対象ファイル:
  - src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md; src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/report.md; src/spec_dock/assets/spec_dock/system/active-none/{initiative,epic,issue}/report.md; dogfooding mirrors
- planned contract:
  - test obligation:
    - closure id: tc-001
    - coverage rationale: docs/skill/template contract can be closed by inspection plus content assertions if available.
  - implementation scope:
    - allowed paths: target provider files listed above.
    - forbidden changes: runtime validation, write-capable delegation, `.github/agents` support.
  - Green verification:
    - inspect diff and run targeted tests if tests are changed.
  - report evidence destination:
    - `report.md` Step Contract Closure S01.
  - amendment trigger:
    - required target surface is missing or scope expands beyond parent Epic.

#### delegation contract
- delegated role: doc-writer by default; dev-coder only if tests/runtime are changed.
- allowed paths: target provider files and related tests.
- forbidden changes: parent Epic non-scope.
- required verification: diff inspection and targeted tests if applicable.
- output required: changed files, verification result, unresolved risks.

#### 具体テストケース一覧
- `tc-s01-001` inspect-only: provider contract exists
  - 前提: target provider files are edited.
  - 操作: inspect diff.
  - 期待結果: `delegated draft lifecycle、structured draft artifact、report evidence、report template / active-none surfaces を固定する。` is represented without contradicting parent Epic.
  - 検証方法: diff/reviewer inspection.
  - 関連 closure id: tc-001

#### step closure contract
- close 条件: target provider source is updated and inspected.
- report evidence: Step Contract Closure S01.

### S02 — Dogfooding parity and verification
- behavior goal:
  - Consumer/dogfooding workspace and tests reflect the provider change.
- 対象ファイル:
  - dogfooding mirrors and tests as applicable.
- planned contract:
  - test obligation:
    - closure id: tc-002
  - implementation scope:
    - allowed paths: dogfooding mirrors, tests, report evidence.
    - forbidden changes: unrelated implementation refactor.
  - Green verification:
    - `./spec-dock/scripts/spec-dock validate`
    - `./spec-dock/scripts/spec-dock sync`
    - targeted tests if changed.
  - report evidence destination:
    - `report.md` Step Contract Closure S02.

#### delegation contract
- delegated role: doc-writer / dev-coder depending on changed surface.
- required verification: validate/sync and targeted tests if applicable.
- stop conditions: validation failure unrelated to this Issue needs triage before continuing.

#### 具体テストケース一覧
- `tc-s02-001` inspect-only: provider/consumer parity
  - 前提: provider update is complete.
  - 操作: inspect dogfooding mirror / run sync or validate.
  - 期待結果: no unintended drift.
  - 検証方法: diff + command evidence.
  - 関連 closure id: tc-002

#### step closure contract
- close 条件: parity/verification evidence is recorded.
- report evidence: Step Contract Closure S02.

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs / templates / workflow / skill / adapter surfaces listed in this Issue.
- 対応:
  - Update `report.md` with docs impact, validation, and reviewer evidence.
- spec/doc review:
  - reviewer: spec-reviewer
  - pass 条件: docs align with requirement/design/plan.

### S99 — final quality gate
- branch diff 範囲:
  - This Issue's target files and required parity/test updates.
- 必須 validation:
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
  - targeted tests if applicable
- final spec review ゲート:
  - reviewer: spec-reviewer
  - 範囲: requirement / design / plan / report / diff alignment
  - pass 条件: reviewer pass
- final commit gate:
  - commit after reviewer pass and clean intended diff.

## 未確定事項
- なし。

## 最終完了条件
- AC/EC 達成:
  - AC-001..AC-003 and EC-001..EC-002 closed in report.
- docs 影響解決:
  - S90 complete.
- 全 implementation step 完了:
  - S01/S02/S90/S99 committed or approved-no-op.
- final quality gate pass:
  - final spec-reviewer pass.


## Parent Epic Contract Details
- Required draft lifecycle states:
  - `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`.
- Required failure-mode fields:
  - expected verdict
  - allowed next action
  - report evidence path
  - promotion eligibility
- Required failure modes:
  - missing consent
  - missing/stale previous reviewer pass
  - requirement gap during design
  - design gap during plan
  - role unavailable
  - forbidden action attempt
  - stale draft
  - superseded draft
  - missing draft evidence when delegated use is claimed
  - reviewer unavailable/denied/waived/provisional
- Required report surfaces:
  - `src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/report.md`
  - `src/spec_dock/assets/spec_dock/system/active-none/{initiative,epic,issue}/report.md`
  - dogfooding mirrors under `spec-dock/templates/**/report.md` and `spec-dock/system/active-none/**/report.md`
