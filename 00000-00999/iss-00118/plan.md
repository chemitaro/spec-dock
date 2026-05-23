---
種別: 実装計画書（Issue）
ID: "iss-00118"
タイトル: "Delegated Authoring Dogfooding Pilot"
関連GitHub: ["#118"]
状態: "draft"
作成者: "Codex"
最終更新: "2026-05-23"
依存: ["requirement.md", "design.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00118 Delegated Authoring Dogfooding Pilot — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001 pilot prerequisites / provider contract no-op check
  - AC-002 validation / parity evidence
  - AC-003 final spec review
  - E-AC-004 operational design draft evidence
  - E-AC-005 operational plan draft evidence
  - E-AC-007 provider/consumer parity evidence
  - E-AC-008 pilot metrics and defer decision
- EC:
  - EC-001 documented uncertainty path
  - EC-002 provider/consumer drift handling
- 制約:
  - 親 Epic non-scope を超えない。

## 依存関係から導く実装順序
- 依存関係の正本:
  - `design.md` の provider-first dependency and file change plan。
- 順序ルール:
  - Pilot prerequisites / provider contract check -> dogfooding parity -> delegated design pilot -> delegated plan pilot -> metrics/defer decision -> report/review。
- step 依存 summary:
  - S01: Pilot prerequisites and provider contract no-op check; depends on iss-00113, iss-00114, iss-00115, iss-00116, iss-00117; unblocks S02.
  - S02: Dogfooding parity and tests; depends on S01; unblocks S03.
  - S03: Delegated design draft pilot; depends on S02; unblocks S04.
  - S04: Delegated plan draft pilot; depends on S03; unblocks S05.
  - S05: Pilot metrics and defer decision; depends on S03/S04; unblocks S90/S99.
  - S90: Docs impact/report update; depends on S05.
  - S99: Final quality gate; depends on S90.

## ステップ一覧
- S01:
  - 観測可能な振る舞い: Pilot prerequisites are confirmed, and provider-side pilot contract is either already covered by prior Issues or explicitly closed as approved no-op.
  - 依存: iss-00113, iss-00114, iss-00115, iss-00116, iss-00117
  - unblock: S02
  - 対象ファイル: `report.md`; prior provider docs/skills/adapters from iss-00113..iss-00117; `spec-dock/active/epic/discussions/` pilot artifacts
  - 閉じる要件: AC-001
  - レビューゲート: spec-reviewer for docs/skill/template alignment, code-reviewer if tests/runtime are touched.
- S02:
  - 観測可能な振る舞い: dogfooding mirror and verification evidence reflect provider change.
  - 依存: S01
  - unblock: S03
  - 対象ファイル: dogfooding mirrors / tests as applicable
  - 閉じる要件: AC-002, E-AC-007, EC-002
  - レビューゲート: reviewer matching changed surface.
- S03:
  - 観測可能な振る舞い: at least one delegated design draft is saved under `discussions/` and integrated or rejected with report evidence.
  - 閉じる要件: E-AC-004 operational evidence.
- S04:
  - 観測可能な振る舞い: at least one delegated plan draft is saved under `discussions/` and integrated or rejected with report evidence.
  - 閉じる要件: E-AC-005 operational evidence.
- S05:
  - 観測可能な振る舞い: pilot metrics and `write-capable delegation remains deferred` decision are recorded.
  - 閉じる要件: E-AC-008.
  - unblock: S90, S99
- S06:
  - 観測可能な振る舞い: at least one negative / blocked case is exercised or recorded as simulated evidence.
  - 閉じる要件: E-AC-009 operational evidence.
  - unblock: S90, S99
- S90:
  - 観測可能な振る舞い: docs impact and report evidence are complete.
  - 閉じる要件: EC-001, docs impact.
- S99:
  - 観測可能な振る舞い: final validation/review pass and clean closure evidence.
  - 閉じる要件: AC-003.

## 要件 ↔ ステップ対応
- AC-001 -> S01
- AC-002 -> S02 / tc-002
- AC-003 -> S99 / tc-003
- E-AC-007 provider/consumer parity -> S02 / tc-009
- E-AC-004 operational evidence -> S03 / tc-006
- E-AC-005 operational evidence -> S04 / tc-007
- E-AC-008 pilot metrics/defer decision -> S05 / tc-008
- E-AC-009 negative/failure evidence -> S06 / tc-010
- EC-001 -> S90 / tc-004
- EC-002 -> S02 / tc-005

## Spec-Locked Closure Index（仕様固定クロージャ索引）
| id | step | slice | type | spec link | locked expectation | observable input/state | bug class guarded | required | evidence level | closure evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | pilot prerequisites | acceptance | AC-001 | Prior provider contracts from Issues 001-005 are available, or this Issue records provider update as approved no-op without claiming new provider changes. | report prerequisite ledger | false provider update claim | yes | inspect-only | report S01 closure |
| tc-002 | S02 | parity | acceptance | AC-002 | Dogfooding mirror/tests/validation reflect provider change or document intended no-op. | diff + command output | provider/consumer drift | yes | inspect-only | report step closure |
| tc-009 | S02 | parent parity | acceptance | E-AC-007 | Provider/consumer parity for shipped workflow/skills/adapters is verified before pilot evidence is trusted. | validate/sync + diff evidence | pilot on stale assets | yes | inspect-only | report S02 closure |
| tc-003 | S99 | final review | acceptance | AC-003 | Final reviewer confirms issue docs/report/diff alignment. | reviewer output | spec drift | yes | manual-required | report final gate |
| tc-004 | S90 | documented uncertainty | exception | EC-001 | If host/path/target uncertainty blocks verified implementation, the issue records uncertainty and does not claim false success. | report exception evidence | false verified claim | yes | inspect-only | report S90 closure |
| tc-005 | S02 | parity drift | exception | EC-002 | Provider/consumer drift is either corrected or explicitly documented as intended. | provider/consumer diff | silent drift | yes | inspect-only | report S02 closure |
| tc-006 | S03 | design draft pilot | acceptance | E-AC-004 / E-RQ-007 | A delegated design draft exists under discussions and `report.md` records role, phase, scope, consent, source artifacts, draft path, status, integration result, rejected portions, blockers, reviewer result, and promotion decision. | design draft artifact + full Design Authoring Delegation report section | fake pilot completion or missing consent/provenance | yes | manual-required | report S03 closure |
| tc-007 | S04 | plan draft pilot | acceptance | E-AC-005 / E-RQ-007 | A delegated plan draft exists under discussions and `report.md` records role, phase, scope, consent, source artifacts, draft path, status, integration result, rejected portions, blockers, reviewer result, and promotion decision. | plan draft artifact + full Plan Authoring Delegation report section | fake pilot completion or missing consent/provenance | yes | manual-required | report S04 closure |
| tc-008 | S05 | pilot metrics | acceptance | E-AC-008 | Required pilot metrics and write-capable defer decision are recorded. | metrics summary + defer decision | missing readiness evidence | yes | manual-required | report S05 closure |
| tc-010 | S06 | negative / blocked case | acceptance | E-AC-009 | Pilot includes at least one RCR, Plan Blocked, stale reconciliation, rejected/partially integrated draft, or host adapter unavailable fallback; simulated evidence is explicitly marked if used. | negative-path artifact + report evidence | untested failure-mode contract | yes | manual-required | report S06 closure |

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

### S01 — Pilot prerequisites and provider contract no-op check
- behavior goal:
  - Confirm Issues 001-005 provide the shipped provider contracts needed for the pilot, or record an approved no-op if no additional provider source update is required in this Issue.
- design 参照:
  - `design.md` file change plan and parent Epic design.
- 対象ファイル:
  - `report.md`
  - prior provider outputs from Issues 001-005
  - `spec-dock/active/epic/discussions/` pilot artifacts
- planned contract:
  - test obligation:
    - closure id: tc-001
    - coverage rationale: docs/skill/template contract can be closed by inspection plus content assertions if available.
  - implementation scope:
    - allowed paths: `report.md`, pilot discussion artifacts, and validation evidence.
    - forbidden changes: runtime validation, write-capable delegation, `.github/agents` support.
  - Green verification:
    - inspect diff and run targeted tests if tests are changed.
  - report evidence destination:
    - `report.md` Step Contract Closure S01.
  - amendment trigger:
    - required target surface is missing or scope expands beyond parent Epic.

#### delegation contract
- delegated role: doc-writer by default; dev-coder only if tests/runtime are changed.
- allowed paths: `report.md`, pilot discussion artifacts, parity / validation evidence, and issue docs if amendment is required.
- forbidden changes: parent Epic non-scope, new provider contract claims, write-capable delegation.
- required verification: prerequisite ledger inspection, diff inspection, validate/sync, and targeted tests only if tests are changed.
- output required: prerequisite result, no-op / uncertainty status, pilot evidence locations, verification result, unresolved risks.

#### 具体テストケース一覧
- `tc-s01-001` inspect-only: pilot prerequisites confirmed
  - 前提: `iss-00113`..`iss-00117` are complete or explicitly closed as approved no-op.
  - 操作: inspect prior provider outputs and record prerequisite / no-op status.
  - 期待結果: this Issue does not claim a new provider source update; pilot uses shipped/documented workflow assets from prior Issues.
  - 検証方法: diff/reviewer inspection.
  - 関連 closure id: tc-001

#### step closure contract
- close 条件: prior provider contracts are confirmed or approved-no-op is recorded without claiming a new provider update.
- report evidence: Step Contract Closure S01.

### S02 — Dogfooding parity and verification
- behavior goal:
  - Consumer/dogfooding workspace and validation evidence reflect the prior provider contracts or document intended no-op.
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
  - 前提: prior provider contracts / approved no-op ledger is complete.
  - 操作: inspect dogfooding mirror / run sync or validate.
  - 期待結果: no unintended drift.
  - 検証方法: diff + command evidence.
  - 関連 closure id: tc-002

#### step closure contract
- close 条件: parity/verification evidence is recorded.
- report evidence: Step Contract Closure S02.


### S03 — Delegated design draft pilot
- behavior goal:
  - Produce or invoke at least one delegated design draft using the shipped/documented `system-architect` workflow.
- target evidence:
  - `discussions/*delegated-design*.md` or equivalent documented draft artifact.
  - `report.md` full `Design Authoring Delegation` section containing role, phase, scope, consent, source artifacts, draft artifact path, status, integration result, rejected portions, blockers, reviewer result, and promotion decision.
  - fresh reviewer result for the pilot artifact and canonical integration.
- closure ids:
  - tc-006
- report evidence destination:
  - `report.md` Step Contract Closure S03.

### S04 — Delegated plan draft pilot
- behavior goal:
  - Produce or invoke at least one delegated plan draft using the shipped/documented `implementation-planner` workflow.
- target evidence:
  - `discussions/*delegated-plan*.md` or equivalent documented draft artifact.
  - `report.md` full `Plan Authoring Delegation` section containing role, phase, scope, consent, source artifacts, draft artifact path, status, integration result, rejected portions, blockers, reviewer result, and promotion decision.
  - fresh reviewer result for the pilot artifact and canonical integration.
- closure ids:
  - tc-007
- report evidence destination:
  - `report.md` Step Contract Closure S04.

### S05 — Pilot metrics and defer decision
- behavior goal:
  - Record required pilot metrics and the write-capable delegation defer decision.
- required metrics:
  - draft count
  - integration ratio / integration cost
  - rejected reasons
  - traceability defects
  - scope creep or gate violations
  - forbidden action attempts
  - reviewer findings
  - stale draft events
  - provider/consumer drift
  - implementation deviation if implementation follows
- required decision:
  - `write-capable delegation remains deferred` unless a later Epic / Issue explicitly approves it.
- closure ids:
  - tc-008
- report evidence destination:
  - `report.md` Step Contract Closure S05.

### S06 — Negative / blocked case exercise
- behavior goal:
  - Exercise at least one failure-mode path so the pilot is not success-path-only.
- acceptable cases:
  - Requirement Clarification Request
  - Plan Blocked
  - stale draft reconciliation
  - rejected or partially integrated draft
  - host adapter unavailable fallback
- simulation rule:
  - If no case occurs naturally, record a tabletop / controlled exercise and mark it as simulated evidence.
- host adapter closure rule:
  - If Issue 005 closes as documented uncertainty rather than verified adapter implementation, the pilot may proceed using shipped role skills and documented invocation contracts, but must not claim verified Codex host callability.
- closure ids:
  - tc-010
- report evidence destination:
  - `report.md` Step Contract Closure S06.

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
  - S01/S02/S03/S04/S05/S06/S90/S99 committed or approved-no-op.
- final quality gate pass:
  - final spec-reviewer pass.


## Required Dogfooding Pilot Evidence
- Required artifacts:
  - at least one delegated design draft saved under `discussions/`
  - at least one delegated plan draft saved under `discussions/`
  - canonical integration evidence in `report.md`
  - fresh `spec-reviewer` result for the pilot artifacts and canonical integration
- Required pilot metrics:
  - draft count
  - integration ratio / integration cost
  - rejected reasons
  - traceability defects
  - scope creep or gate violations
  - forbidden action attempts
  - reviewer findings
  - stale draft events
  - provider/consumer drift
  - implementation deviation if implementation follows
- Required decision:
  - `write-capable delegation remains deferred` unless a later Epic / Issue explicitly approves it.
- Pilot must use shipped/documented workflow assets rather than ad hoc prompt-only delegation.
