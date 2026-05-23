---
種別: 実装計画書（Issue）
ID: "iss-00125"
タイトル: "Authority Aware Delegated Authoring Dogfooding Pilot"
関連GitHub: ["#125"]
状態: "approved"
作成者: "Codex"
最終更新: "2026-05-23"
依存: ["requirement.md", "design.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00125 Authority Aware Delegated Authoring Dogfooding Pilot — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID
- Issue AC/EC: defined in `requirement.md`.
- Parent Epic mapping: defined in `requirement.md` and `design.md`; no v0 Issue 001〜006 / #113〜#118 rewrite is allowed.

## 依存関係から導く実装順序
- 正本: `design.md` dependency analysis, module dependency diagram, and file change plan.
- 順序: provider contract -> tests/assertions/probes -> dogfooding parity -> S90 docs impact -> S99 final quality.
- Allowed paths are resolved in each implementation step below; executors must not infer broader scope from prose.

## ステップ一覧
- S01:
  - 観測可能な振る舞い: Pilot preflight for iss-00120 through iss-00124 complete-or-fallback evidence, active scope, validate/sync baseline, permission state
  - delegated role: qa-reviewer/repo-analyst
  - closure id: tc-001, tc-002
  - reviewer gate: spec-reviewer
- S02:
  - 観測可能な振る舞い: Run actual delegated draft design/plan authoring and record proposed status
  - delegated role: system-architect for design draft; implementation-planner for plan draft
  - closure id: tc-003, tc-004
  - reviewer gate: spec-reviewer
- S03:
  - 観測可能な振る舞い: Verify lifecycle block/fallback and provider defect disposition
  - delegated role: qa-reviewer
  - closure id: tc-005, tc-006
  - reviewer gate: code-reviewer if runtime diff appears
- S90:
  - 観測可能な振る舞い: Resolve docs/follow-up impact
  - delegated role: doc-writer
  - closure id: tc-090
  - reviewer gate: spec-reviewer
- S99:
  - 観測可能な振る舞い: final QA/code/spec gates pass and report closure is complete.
  - delegated role: qa-reviewer / code-reviewer / spec-reviewer
  - closure id: tc-099
  - reviewer gate: final three gates

## 仕様固定クロージャ索引（Spec-Locked Closure Index）
| 識別子（ID） | ステップ | スライス | 種別 | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル | クロージャ証跡 |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | Pilot preflight for iss-00120 through iss-00124 complete-or-fallback evidence, active scope, validate/sync baseline, permission state | acceptance | AC-001 / EC-002 | Inspect reports for iss-00120 through iss-00124 complete-or-explicit-fallback evidence and record a Task Manifest Lock for S02 with resolved non-active real paths before pilot S02 starts. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-002 | S01 | Pilot preflight for iss-00120 through iss-00124 complete-or-fallback evidence, active scope, validate/sync baseline, permission state | acceptance | AC-001 / EC-001 / EC-003 | Record active scope, resolved pilot target real paths, permission/profile state, validate output, and sync output as baseline evidence. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-003 | S02 | Run actual delegated draft design/plan authoring and record proposed status | acceptance | AC-002 | Record actual system-architect proposed design draft evidence with no promotion claim. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-004 | S02 | Run actual delegated draft design/plan authoring and record proposed status | acceptance | AC-002 | Record actual implementation-planner proposed plan draft evidence with no promotion claim. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-005 | S03 | Verify lifecycle block/fallback and provider defect disposition | acceptance | AC-003 / EC-001 | Observe proposed artifact lifecycle/context-pack block or explicit fallback evidence. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-006 | S03 | Verify lifecycle block/fallback and provider defect disposition | acceptance | AC-004 / EC-002 | Record provider defect disposition as follow-up/amendment instead of silently implementing inside pilot. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-090 | S90 | Resolve docs/follow-up impact | acceptance | AC-004 / EC-002 / EC-003 | Record docs impact as follow-up/no-op with spec-reviewer pass. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-099 | S99 | final quality | acceptance | all AC/EC | final QA/code/spec gates pass and report ledger closes every required row | final integrated issue state | false completion | yes | reviewer evidence | final report evidence |

## レビュー / QA ゲート方針
- Step review: docs/templates/skills-only -> `spec-reviewer`; runtime/tests/scaffold behavior -> `code-reviewer`.
- S90 docs impact: `spec-reviewer` pass.
- S99 final quality: `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer` all pass.

## 実装ステップ
### 実装ステップ S01 — Pilot preflight for iss-00120 through iss-00124 complete-or-fallback evidence, active scope, validate/sync baseline, permission state
- 振る舞いの目標: Pilot preflight for iss-00120 through iss-00124 complete-or-fallback evidence, active scope, validate/sync baseline, permission state
- design 参照: `design.md` provider source / dogfooding surface / test strategy
- 対象ファイル:
      - no provider source by default; discovered provider defects open follow-up or amend the owning provider issue
      - dogfooding execution evidence
      - reviewer verdicts
      - validation/sync output
      - permission probe records
- 閉じる closure id: tc-001, tc-002
- 計画済み契約:
  - scope: listed allowed paths only.
  - Red / 代替証跡: each closure id below names the command, inspection, or manual evidence.
  - Green 検証: targeted evidence for every closure id is recorded in `report.md`.
  - amendment trigger: allowed paths, closes mapping, authority model, required closure id, or fallback condition changes.

#### 委任契約
- delegated role: qa-reviewer/repo-analyst
- source of truth: this `requirement.md`, this `design.md`, parent epic v1 amendment, and `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/discussions/20260523t144246z-disc-v1-issue-authoring-delegated-evidence.md`
- allowed changes:
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00125-authority-aware-delegated-authoring-dogfooding-pilot/report.md
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00125-authority-aware-delegated-authoring-dogfooding-pilot/discussions/
      - no provider source by default; discovered provider defects open follow-up or amend the owning provider issue
- forbidden changes:
      - canonical writes to v0 Issue #113〜#118
      - canonical writes to prerequisite v1 Issue #120〜#124 without plan amendment and reviewer pass
      - promotion, approval, final reviewer pass claim, or issue finish claim by delegated authoring roles
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00113-* through iss-00118-* report/plan rewrites
      - unrelated provider/runtime files outside the listed allowed paths
      - final authority, reviewer pass, or promotion claims
- required verification: tc-001: Inspect reports for iss-00120 through iss-00124 complete-or-explicit-fallback evidence and record a Task Manifest Lock for S02 with resolved non-active real paths before pilot S02 starts., tc-002: Record active scope, resolved pilot target real paths, permission/profile state, validate output, and sync output as baseline evidence.
- reviewer focus: spec-reviewer
- output required: changed files, verification result for each closure id, unresolved risks, Ledger Note or no-material-decision statement.
- stop conditions: input docs conflict, path outside allowed scope, forbidden v0 rewrite, verification cannot run, or acceptance cannot be met.

#### 具体テストケース一覧
- `tc-001`: Inspect reports for iss-00120 through iss-00124 complete-or-explicit-fallback evidence and record a Task Manifest Lock for S02 with resolved non-active real paths before pilot S02 starts.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `rg -n 'Spec Authoring Gate|review_status: pass|fallback|complete' spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-0012{0,1,2,3,4}-*/report.md` を実行し、`iss-00125/report.md` に Task Manifest Lock for S02 を記録する。
  - 期待結果: iss-00120 through iss-00124 are complete or explicitly fallbacked, and S02 has resolved non-active real paths before pilot drafting begins.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: preflight rg output and Task Manifest Lock contentsを `report.md` に記録する。
  - 記録先: Step Contract Closure / Test Contract Closure / Closure Coverage.
- `tc-002`: Record active scope, resolved pilot target real paths, permission/profile state, validate output, and sync output as baseline evidence.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `./spec-dock/scripts/spec-dock active show`、`./spec-dock/scripts/spec-dock validate`、`./spec-dock/scripts/spec-dock sync` を実行し、resolved pilot target path/profile/probe stateを `report.md` に記録する。
  - 期待結果: active scope, real pilot target paths, permission/profile state, validate output, and sync output are captured as baseline evidence.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: active/validate/sync output and resolved-path evidenceを `report.md` に記録する。
  - 記録先: Step Contract Closure / Test Contract Closure / Closure Coverage.

#### ステップ完了契約
- close 条件: all listed closure ids pass by targeted evidence.
- report evidence: Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta.
- 残リスク: unresolved host/runtime/doc ambiguity requires decision ledger entry and possible plan amendment.

#### ステップゲート
- step reviewer gate: spec-reviewer `review_status: pass`
- commit / no-op gate: one behavior slice, committed or justified approved-no-op only after reviewer pass.

### 実装ステップ S02 — Run actual delegated draft design/plan authoring and record proposed status
- 振る舞いの目標: Run actual delegated draft design/plan authoring and record proposed status
- design 参照: `design.md` provider source / dogfooding surface / test strategy
- 対象ファイル:
      - resolved `design_draft_path` recorded in `report.md` Task Manifest Lock for S02 (system-architect only; absolute real path, never `spec-dock/active/...`)
      - resolved `plan_draft_path` recorded in `report.md` Task Manifest Lock for S02 (implementation-planner only; absolute real path, never `spec-dock/active/...`)
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00125-authority-aware-delegated-authoring-dogfooding-pilot/report.md
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00125-authority-aware-delegated-authoring-dogfooding-pilot/discussions/
      - no provider source by default; discovered provider defects open follow-up or amend the owning provider issue
- pilot write target contract:
  - S01 must create a `Task Manifest Lock for S02` in `report.md` before S02 starts.
  - The lock must name `pilot_target_issue_id`, `design_draft_path`, `plan_draft_path`, source revision/hash, allowed evidence paths, forbidden paths, fallback, and stale-if conditions.
  - `design_draft_path` and `plan_draft_path` must be absolute or repo-root real paths under `spec-dock/initiatives/.../issues/<pilot_target_issue>/`; they must never be `spec-dock/active/...` symlink paths.
  - `pilot_target_issue_id` must not be `iss-00125` itself, any v0 Issue `iss-00113`〜`iss-00118`, or prerequisite v1 Issue `iss-00120`〜`iss-00124` unless a separate plan amendment and fresh spec-reviewer pass explicitly authorize it.
  - stale-if conditions must include active pointer changes, resolved path changes, source revision/hash mismatch, missing prerequisite complete-or-fallback evidence, and Permission Profile probe failure.
  - system-architect may write only the locked `design_draft_path` and design evidence.
  - implementation-planner may write only the locked `plan_draft_path` and plan evidence.
  - qa-reviewer, repo-analyst, doc-writer, and reviewers may write only report/discussion evidence or docs impact records, not canonical design/plan drafts.
  - If no dedicated pilot target can be resolved and locked, S02 writes only proposed draft copies under this issue `discussions/` and records fallback; it must not claim verified canonical draft write.
- 閉じる closure id: tc-003, tc-004
- 計画済み契約:
  - scope: listed allowed paths only.
  - Red / 代替証跡: each closure id below names the command, inspection, or manual evidence.
  - Green 検証: targeted evidence for every closure id is recorded in `report.md`.
  - amendment trigger: allowed paths, closes mapping, authority model, required closure id, or fallback condition changes.

#### 委任契約
- delegated role: system-architect for design draft; implementation-planner for plan draft
- source of truth: this `requirement.md`, this `design.md`, parent epic v1 amendment, and `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/discussions/20260523t144246z-disc-v1-issue-authoring-delegated-evidence.md`
- allowed changes:
      - resolved `design_draft_path` recorded in `report.md` Task Manifest Lock for S02 (system-architect only; absolute real path, never `spec-dock/active/...`)
      - resolved `plan_draft_path` recorded in `report.md` Task Manifest Lock for S02 (implementation-planner only; absolute real path, never `spec-dock/active/...`)
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00125-authority-aware-delegated-authoring-dogfooding-pilot/report.md
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00125-authority-aware-delegated-authoring-dogfooding-pilot/discussions/
      - no provider source by default; discovered provider defects open follow-up or amend the owning provider issue
- forbidden changes:
      - canonical writes to v0 Issue #113〜#118
      - canonical writes to prerequisite v1 Issue #120〜#124 without plan amendment and reviewer pass
      - promotion, approval, final reviewer pass claim, or issue finish claim by delegated authoring roles
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00113-* through iss-00118-* report/plan rewrites
      - unrelated provider/runtime files outside the listed allowed paths
      - final authority, reviewer pass, or promotion claims
- required verification: tc-003: Record actual system-architect proposed design draft evidence with no promotion claim., tc-004: Record actual implementation-planner proposed plan draft evidence with no promotion claim.
- reviewer focus: spec-reviewer
- output required: changed files, verification result for each closure id, unresolved risks, Ledger Note or no-material-decision statement.
- stop conditions: input docs conflict, path outside allowed scope, forbidden v0 rewrite, verification cannot run, or acceptance cannot be met.

#### 具体テストケース一覧
- `tc-003`: Record actual system-architect proposed design draft evidence with no promotion claim.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: Task Manifest Lock の `design_draft_path` に対して system-architect を実行し、生成差分または fallback draft copy を `report.md` に記録する。
  - 期待結果: system-architect produces proposed design draft evidence and makes no promotion/final authority claim.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: draft path, diff summary/fallback artifact path, and no-promotion statementを `report.md` に記録する。
  - 記録先: Step Contract Closure / Test Contract Closure / Closure Coverage.
- `tc-004`: Record actual implementation-planner proposed plan draft evidence with no promotion claim.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: Task Manifest Lock の `plan_draft_path` に対して implementation-planner を実行し、生成差分または fallback draft copy を `report.md` に記録する。
  - 期待結果: implementation-planner produces proposed plan draft evidence and makes no promotion/final authority claim.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: draft path, diff summary/fallback artifact path, and no-promotion statementを `report.md` に記録する。
  - 記録先: Step Contract Closure / Test Contract Closure / Closure Coverage.

#### ステップ完了契約
- close 条件: all listed closure ids pass by targeted evidence.
- report evidence: Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta.
- 残リスク: unresolved host/runtime/doc ambiguity requires decision ledger entry and possible plan amendment.

#### ステップゲート
- step reviewer gate: spec-reviewer `review_status: pass`
- commit / no-op gate: one behavior slice, committed or justified approved-no-op only after reviewer pass.

### 実装ステップ S03 — Verify lifecycle block/fallback and provider defect disposition
- 振る舞いの目標: Verify lifecycle block/fallback and provider defect disposition
- design 参照: `design.md` provider source / dogfooding surface / test strategy
- 対象ファイル:
      - no provider source by default; discovered provider defects open follow-up or amend the owning provider issue
      - dogfooding execution evidence
      - reviewer verdicts
      - validation/sync output
      - permission probe records
- 閉じる closure id: tc-005, tc-006
- 計画済み契約:
  - scope: listed allowed paths only.
  - Red / 代替証跡: each closure id below names the command, inspection, or manual evidence.
  - Green 検証: targeted evidence for every closure id is recorded in `report.md`.
  - amendment trigger: allowed paths, closes mapping, authority model, required closure id, or fallback condition changes.

#### 委任契約
- delegated role: qa-reviewer
- source of truth: this `requirement.md`, this `design.md`, parent epic v1 amendment, and `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/discussions/20260523t144246z-disc-v1-issue-authoring-delegated-evidence.md`
- allowed changes:
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00125-authority-aware-delegated-authoring-dogfooding-pilot/report.md
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00125-authority-aware-delegated-authoring-dogfooding-pilot/discussions/
      - no provider source by default; discovered provider defects open follow-up or amend the owning provider issue
- forbidden changes:
      - canonical writes to v0 Issue #113〜#118
      - canonical writes to prerequisite v1 Issue #120〜#124 without plan amendment and reviewer pass
      - promotion, approval, final reviewer pass claim, or issue finish claim by delegated authoring roles
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00113-* through iss-00118-* report/plan rewrites
      - unrelated provider/runtime files outside the listed allowed paths
      - final authority, reviewer pass, or promotion claims
- required verification: tc-005: Observe proposed artifact lifecycle/context-pack block or explicit fallback evidence., tc-006: Record provider defect disposition as follow-up/amendment instead of silently implementing inside pilot.
- reviewer focus: code-reviewer if runtime diff appears
- output required: changed files, verification result for each closure id, unresolved risks, Ledger Note or no-material-decision statement.
- stop conditions: input docs conflict, path outside allowed scope, forbidden v0 rewrite, verification cannot run, or acceptance cannot be met.

#### 具体テストケース一覧
- `tc-005`: Observe proposed artifact lifecycle/context-pack block or explicit fallback evidence.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `./spec-dock/scripts/spec-dock active show` と `./spec-dock/scripts/spec-dock validate` を実行し、proposed artifact が lifecycle/context-pack に採用されない、または fallback block される evidence を記録する。
  - 期待結果: proposed artifact lifecycle/context-pack block or fallback behavior is observed and documented.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: lifecycle/context-pack output and block/fallback判定を `report.md` に記録する。
  - 記録先: Step Contract Closure / Test Contract Closure / Closure Coverage.
- `tc-006`: Record provider defect disposition as follow-up/amendment instead of silently implementing inside pilot.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: pilot中に provider defect が見つかった場合は `report.md` の follow-up/amendment ledger に defect id, owning issue, blocked tc を記録し、provider source は編集しない。
  - 期待結果: provider defect disposition is explicit as follow-up/amendment and no silent provider implementation occurs inside the pilot.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: defect ledger entry or no-defect statementと git diff scopeを `report.md` に記録する。
  - 記録先: Step Contract Closure / Test Contract Closure / Closure Coverage.

#### ステップ完了契約
- close 条件: all listed closure ids pass by targeted evidence.
- report evidence: Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta.
- 残リスク: unresolved host/runtime/doc ambiguity requires decision ledger entry and possible plan amendment.

#### ステップゲート
- step reviewer gate: code-reviewer if runtime diff appears `review_status: pass`
- commit / no-op gate: one behavior slice, committed or justified approved-no-op only after reviewer pass.

### 実装ステップ S90 — Resolve docs/follow-up impact
- 振る舞いの目標: Resolve docs/follow-up impact
- design 参照: `design.md` provider source / dogfooding surface / test strategy
- 対象ファイル:
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00125-authority-aware-delegated-authoring-dogfooding-pilot/report.md
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00125-authority-aware-delegated-authoring-dogfooding-pilot/discussions/
      - current dogfooding workspace (inspection only)
      - spec-dock validate output recorded in report
      - spec-dock sync output recorded in report
- 閉じる closure id: tc-090
- 計画済み契約:
  - scope: listed allowed paths only.
  - Red / 代替証跡: each closure id below names the command, inspection, or manual evidence.
  - Green 検証: targeted evidence for every closure id is recorded in `report.md`.
  - amendment trigger: allowed paths, closes mapping, authority model, required closure id, or fallback condition changes.

#### 委任契約
- delegated role: doc-writer
- source of truth: this `requirement.md`, this `design.md`, parent epic v1 amendment, and `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/discussions/20260523t144246z-disc-v1-issue-authoring-delegated-evidence.md`
- allowed changes:
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00125-authority-aware-delegated-authoring-dogfooding-pilot/report.md
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00125-authority-aware-delegated-authoring-dogfooding-pilot/discussions/
      - current dogfooding workspace (inspection only)
      - spec-dock validate output recorded in report
      - spec-dock sync output recorded in report
- forbidden changes:
      - provider source changes during S90; put them in an implementation step with code-reviewer/spec-reviewer mapping
      - runtime/test/scaffold behavior changes under a spec-reviewer-only gate
- required verification: tc-090: Record docs impact as follow-up/no-op with spec-reviewer pass.
- reviewer focus: spec-reviewer
- output required: changed files, verification result for each closure id, unresolved risks, Ledger Note or no-material-decision statement.
- stop conditions: input docs conflict, path outside allowed scope, forbidden v0 rewrite, verification cannot run, or acceptance cannot be met.

#### 具体テストケース一覧
- `tc-090`: Record docs impact as follow-up/no-op with spec-reviewer pass.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `./spec-dock/scripts/spec-dock validate` を実行し、`rg -n 'Task Manifest Lock|pilot_target_issue_id|design_draft_path|plan_draft_path|stale-if' spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00125-authority-aware-delegated-authoring-dogfooding-pilot/report.md` を実行する。
  - 期待結果: docs impact is recorded as follow-up/no-op with spec-reviewer pass; pilot evidence remains issue-local or locked real-path only.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: validate output, report evidence rg output, and spec-reviewer verdictを `report.md` に記録する。
  - 記録先: Step Contract Closure / Test Contract Closure / Closure Coverage.

#### ステップ完了契約
- close 条件: all listed closure ids pass by targeted evidence.
- report evidence: Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta.
- 残リスク: unresolved host/runtime/doc ambiguity requires decision ledger entry and possible plan amendment.

#### ステップゲート
- step reviewer gate: spec-reviewer `review_status: pass`
- commit / no-op gate: one behavior slice, committed or justified approved-no-op only after reviewer pass.

### ドキュメント影響の解消ステップ S90
- 対象: docs impact, dogfooding parity inspection, report/discussion evidence only. Provider/runtime/test changes discovered here require a prior implementation step or plan amendment with the correct reviewer gate.
- owner: doc-writer when updates are required.
- pass 条件: docs/spec alignment `spec-reviewer` pass and no unresolved docs impact.

### 最終品質ゲートステップ S99
- 必須 validation: targeted tests from each step, plus `./spec-dock/scripts/spec-dock validate` and `./spec-dock/scripts/spec-dock sync` when relevant.
- final QA gate: `qa-reviewer` pass.
- final code review gate: issue-wide `code-reviewer` pass.
- final spec review gate: `spec-reviewer` pass.
- final commit gate: report ledger complete, clean post-commit evidence, PR Delivery / Merge Preparation evidence reserved for execution completion.

## 未確定事項
- なし。New durable decisions require report ledger disposition and promotion to design/plan/follow-up.

## 最終完了条件
- All AC/EC have Step/Test Closure evidence.
- S90 docs impact is resolved.
- All implementation steps are committed or approved-no-op.
- S99 final QA/code/spec gates pass.
- v0 Issue 001〜006 / #113〜#118 remain unmodified except as historical references.
