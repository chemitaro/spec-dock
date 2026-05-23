---
種別: 実装計画書（Issue）
ID: "iss-00120"
タイトル: "Authority Metadata and Promotion Record Schema"
関連GitHub: ["#120"]
状態: "approved"
作成者: "Codex"
最終更新: "2026-05-23"
依存: ["requirement.md", "design.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00120 Authority Metadata and Promotion Record Schema — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID
- Issue AC/EC: defined in `requirement.md`.
- Parent Epic mapping: defined in `requirement.md` and `design.md`; no v0 Issue 001〜006 / #113〜#118 rewrite is allowed.

## 依存関係から導く実装順序
- 正本: `design.md` dependency analysis, module dependency diagram, and file change plan.
- 順序: provider contract -> tests/assertions/probes -> dogfooding parity -> S90 docs impact -> S99 final quality.
- Allowed paths are resolved in each implementation step below; executors must not infer broader scope from prose.

## ステップ一覧
- S01:
  - 観測可能な振る舞い: Define authority metadata, grants, approval, and promotion record schema
  - delegated role: doc-writer
  - closure id: tc-001, tc-002, tc-003
  - reviewer gate: spec-reviewer
- S02:
  - 観測可能な振る舞い: Add managed scaffold/content assertions for the schema
  - delegated role: dev-coder
  - closure id: tc-004
  - reviewer gate: code-reviewer
- S90:
  - 観測可能な振る舞い: Refresh dogfooding parity and docs impact evidence
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
| tc-001 | S01 | Define authority metadata, grants, approval, and promotion record schema | acceptance | AC-001 / EC-001 | Inspect provider docs/templates for status, authority, owner_role, draft_author_role, approval, and source revision fields using rg. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-002 | S01 | Define authority metadata, grants, approval, and promotion record schema | acceptance | AC-003 / EC-002 | Inspect provider docs for the exact normative grant key set and no wildcard grant semantics. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-003 | S01 | Define authority metadata, grants, approval, and promotion record schema | acceptance | AC-002 / AC-004 / EC-003 | Inspect report/template docs for promotion record fields, approved hash/revision, reviewer target hash, and mismatch handling. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-004 | S02 | Add managed scaffold/content assertions for the schema | acceptance | AC-001..AC-004 | Run uv run pytest tests/test_init_update.py for managed scaffold/content assertions added in this issue. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-090 | S90 | Refresh dogfooding parity and docs impact evidence | acceptance | AC-001..AC-004 / EC-001..EC-003 | Run spec-dock sync/validate or inspect generated dogfooding copies for provider/consumer parity. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-099 | S99 | final quality | acceptance | all AC/EC | final QA/code/spec gates pass and report ledger closes every required row | final integrated issue state | false completion | yes | reviewer evidence | final report evidence |

## レビュー / QA ゲート方針
- Step review: docs/templates/skills-only -> `spec-reviewer`; runtime/tests/scaffold behavior -> `code-reviewer`.
- S90 docs impact: `spec-reviewer` pass.
- S99 final quality: `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer` all pass.

## 実装ステップ
### 実装ステップ S01 — Define authority metadata, grants, approval, and promotion record schema
- 振る舞いの目標: Define authority metadata, grants, approval, and promotion record schema
- design 参照: `design.md` provider source / dogfooding surface / test strategy
- 対象ファイル:
      - src/spec_dock/assets/spec_dock/docs/
      - src/spec_dock/assets/spec_dock/templates/
      - src/spec_dock/assets/spec_dock/system/active-none/
- 閉じる closure id: tc-001, tc-002, tc-003
- 計画済み契約:
  - scope: listed allowed paths only.
  - Red / 代替証跡: each closure id below names the command, inspection, or manual evidence.
  - Green 検証: targeted evidence for every closure id is recorded in `report.md`.
  - amendment trigger: allowed paths, closes mapping, authority model, required closure id, or fallback condition changes.

#### 委任契約
- delegated role: doc-writer
- source of truth: this `requirement.md`, this `design.md`, parent epic v1 amendment, and `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/discussions/20260523t144246z-disc-v1-issue-authoring-delegated-evidence.md`
- allowed changes:
      - src/spec_dock/assets/spec_dock/docs/
      - src/spec_dock/assets/spec_dock/templates/
      - src/spec_dock/assets/spec_dock/system/active-none/
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00120-authority-metadata-and-promotion-record-schema/report.md
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00120-authority-metadata-and-promotion-record-schema/discussions/
- forbidden changes:
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00113-* through iss-00118-* report/plan rewrites
      - unrelated provider/runtime files outside the listed allowed paths
      - final authority, reviewer pass, or promotion claims
- required verification: tc-001: Inspect provider docs/templates for status, authority, owner_role, draft_author_role, approval, and source revision fields using rg., tc-002: Inspect provider docs for the exact normative grant key set and no wildcard grant semantics., tc-003: Inspect report/template docs for promotion record fields, approved hash/revision, reviewer target hash, and mismatch handling.
- reviewer focus: spec-reviewer
- output required: changed files, verification result for each closure id, unresolved risks, Ledger Note or no-material-decision statement.
- stop conditions: input docs conflict, path outside allowed scope, forbidden v0 rewrite, verification cannot run, or acceptance cannot be met.

#### 具体テストケース一覧
- `tc-001`: Inspect provider docs/templates for status, authority, owner_role, draft_author_role, approval, and source revision fields using rg.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `rg -n 'status|authority|owner_role|draft_author_role|approval|source_revision|approved_revision|approved_hash' src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates src/spec_dock/assets/spec_dock/system/active-none` を実行し、対象語彙が provider docs/templates/system active-none に現れることを確認する。
  - 期待結果: authority metadata fields for status, authority, owner_role, draft_author_role, approval, source revision, approved revision/hash are present in provider contracts; issue-local report-only mentions alone do not satisfy this tc.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: 上記 `rg` のコマンド、主要ヒット行、欠落なしの判定を `report.md` の Step/Test Closure に記録する。
  - 記録先: Step Contract Closure / Test Contract Closure / Closure Coverage.
- `tc-002`: Inspect provider docs for the exact normative grant key set and no wildcard grant semantics.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `rg -n 'can_write_requirement|can_write_design|can_write_plan|can_write_report|can_write_discussions|wildcard|\*' src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates` を実行する。
  - 期待結果: normative grant keys are explicit, wildcard grant semantics are denied or absent, and no prose implies broad role write authority.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: grant key list and wildcard denial/absence evidenceを `report.md` に記録する。
  - 記録先: Step Contract Closure / Test Contract Closure / Closure Coverage.
- `tc-003`: Inspect report/template docs for promotion record fields, approved hash/revision, reviewer target hash, and mismatch handling.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `rg -n 'Promotion Record|promotion_record|approved_hash|approved_revision|reviewer_target_hash|mismatch|stale|promotion' src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates src/spec_dock/assets/spec_dock/system/active-none` を実行する。
  - 期待結果: promotion record fields, approved hash/revision, reviewer target hash, and mismatch/stale handling are documented in provider contracts/templates.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: promotion record field coverage and mismatch handling evidenceを `report.md` に記録する。
  - 記録先: Step Contract Closure / Test Contract Closure / Closure Coverage.

#### ステップ完了契約
- close 条件: all listed closure ids pass by targeted evidence.
- report evidence: Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta.
- 残リスク: unresolved host/runtime/doc ambiguity requires decision ledger entry and possible plan amendment.

#### ステップゲート
- step reviewer gate: spec-reviewer `review_status: pass`
- commit / no-op gate: one behavior slice, committed or justified approved-no-op only after reviewer pass.
### 実装ステップ S02 — Add managed scaffold/content assertions for the schema
- 振る舞いの目標: Add managed scaffold/content assertions for the schema
- design 参照: `design.md` provider source / dogfooding surface / test strategy
- 対象ファイル:
      - src/spec_dock/assets/spec_dock/docs/
      - src/spec_dock/assets/spec_dock/templates/
      - src/spec_dock/assets/spec_dock/system/active-none/
      - tests/test_init_update.py
- 閉じる closure id: tc-004
- 計画済み契約:
  - scope: listed allowed paths only.
  - Red / 代替証跡: each closure id below names the command, inspection, or manual evidence.
  - Green 検証: targeted evidence for every closure id is recorded in `report.md`.
  - amendment trigger: allowed paths, closes mapping, authority model, required closure id, or fallback condition changes.

#### 委任契約
- delegated role: dev-coder
- source of truth: this `requirement.md`, this `design.md`, parent epic v1 amendment, and `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/discussions/20260523t144246z-disc-v1-issue-authoring-delegated-evidence.md`
- allowed changes:
      - src/spec_dock/assets/spec_dock/docs/
      - src/spec_dock/assets/spec_dock/templates/
      - src/spec_dock/assets/spec_dock/system/active-none/
      - tests/test_init_update.py
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00120-authority-metadata-and-promotion-record-schema/report.md
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00120-authority-metadata-and-promotion-record-schema/discussions/
- forbidden changes:
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00113-* through iss-00118-* report/plan rewrites
      - unrelated provider/runtime files outside the listed allowed paths
      - final authority, reviewer pass, or promotion claims
- required verification: tc-004: Run uv run pytest tests/test_init_update.py for managed scaffold/content assertions added in this issue.
- reviewer focus: code-reviewer
- output required: changed files, verification result for each closure id, unresolved risks, Ledger Note or no-material-decision statement.
- stop conditions: input docs conflict, path outside allowed scope, forbidden v0 rewrite, verification cannot run, or acceptance cannot be met.

#### 具体テストケース一覧
- `tc-004`: Run uv run pytest tests/test_init_update.py for managed scaffold/content assertions added in this issue.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `uv run pytest tests/test_init_update.py` を実行する。
  - 期待結果: managed scaffold/content assertions covering authority metadata and promotion record contract pass.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: pytest command, pass/fail summary, and any added assertion namesを `report.md` に記録する。
  - 記録先: Step Contract Closure / Test Contract Closure / Closure Coverage.

#### ステップ完了契約
- close 条件: all listed closure ids pass by targeted evidence.
- report evidence: Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta.
- 残リスク: unresolved host/runtime/doc ambiguity requires decision ledger entry and possible plan amendment.

#### ステップゲート
- step reviewer gate: code-reviewer `review_status: pass`
- commit / no-op gate: one behavior slice, committed or justified approved-no-op only after reviewer pass.

### 実装ステップ S90 — Refresh dogfooding parity and docs impact evidence
- 振る舞いの目標: Refresh dogfooding parity and docs impact evidence
- design 参照: `design.md` provider source / dogfooding surface / test strategy
- 対象ファイル:
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00120-authority-metadata-and-promotion-record-schema/report.md
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00120-authority-metadata-and-promotion-record-schema/discussions/
      - spec-dock/docs/ (inspection only)
      - spec-dock/templates/ (inspection only)
      - spec-dock/system/active-none/ (inspection only)
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
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00120-authority-metadata-and-promotion-record-schema/report.md
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00120-authority-metadata-and-promotion-record-schema/discussions/
      - spec-dock/docs/ (inspection only)
      - spec-dock/templates/ (inspection only)
      - spec-dock/system/active-none/ (inspection only)
- forbidden changes:
      - provider source changes during S90; put them in an implementation step with code-reviewer/spec-reviewer mapping
      - runtime/test/scaffold behavior changes under a spec-reviewer-only gate
- required verification: tc-090: Run spec-dock sync/validate or inspect generated dogfooding copies for provider/consumer parity.
- reviewer focus: spec-reviewer
- output required: changed files, verification result for each closure id, unresolved risks, Ledger Note or no-material-decision statement.
- stop conditions: input docs conflict, path outside allowed scope, forbidden v0 rewrite, verification cannot run, or acceptance cannot be met.

#### 具体テストケース一覧
- `tc-090`: Run spec-dock sync/validate or inspect generated dogfooding copies for provider/consumer parity.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `./spec-dock/scripts/spec-dock sync` と `./spec-dock/scripts/spec-dock validate` を実行し、必要に応じて `rg -n 'authority|promotion|owner_role|draft_author_role' spec-dock/docs spec-dock/templates spec-dock/system/active-none` で dogfooding copies を inspection only で確認する。
  - 期待結果: sync/validate succeed or a documented no-op/fallback is recorded; dogfooding copies expose the same authority/promotion contract without S90 provider/test edits.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: sync/validate output and dogfooding inspection resultを `report.md` に記録する。
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
