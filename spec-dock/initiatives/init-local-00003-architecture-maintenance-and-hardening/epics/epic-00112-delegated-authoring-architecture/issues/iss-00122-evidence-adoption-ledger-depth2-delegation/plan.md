---
種別: 実装計画書（Issue）
ID: "iss-00122"
タイトル: "Evidence Adoption Ledger and Bounded Depth2 Delegation"
関連GitHub: ["#122"]
状態: "approved"
作成者: "Codex"
最終更新: "2026-05-23"
依存: ["requirement.md", "design.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00122 Evidence Adoption Ledger and Bounded Depth2 Delegation — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID
- Issue AC/EC: defined in `requirement.md`.
- Parent Epic mapping: defined in `requirement.md` and `design.md`; no v0 Issue 001〜006 / #113〜#118 rewrite is allowed.

## 依存関係から導く実装順序
- 正本: `design.md` dependency analysis, module dependency diagram, and file change plan.
- 順序: provider contract -> tests/assertions/probes -> dogfooding parity -> S90 docs impact -> S99 final quality.
- Allowed paths are resolved in each implementation step below; executors must not infer broader scope from prose.

## ステップ一覧
- S01:
  - 観測可能な振る舞い: Define evidence adoption ledger schema in docs/templates/report scaffolds
  - delegated role: doc-writer
  - closure id: tc-001, tc-002
  - reviewer gate: spec-reviewer
- S02:
  - 観測可能な振る舞い: Define bounded depth=2 role graph and managed asset assertions
  - delegated role: dev-coder
  - closure id: tc-003, tc-004
  - reviewer gate: code-reviewer
- S90:
  - 観測可能な振る舞い: Refresh dogfooding-visible skills/docs/template evidence
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
| tc-001 | S01 | Define evidence adoption ledger schema in docs/templates/report scaffolds | acceptance | AC-001 / EC-003 | Inspect provider report templates/docs for adopted, partially adopted, rejected, deferred, stale, and blocked ledger dispositions. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-002 | S01 | Define evidence adoption ledger schema in docs/templates/report scaffolds | acceptance | AC-002 | Inspect workflow docs/templates for unresolved blocking ledger item preventing promotion. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-003 | S02 | Define bounded depth=2 role graph and managed asset assertions | acceptance | AC-003 / EC-002 | Inspect skills/docs and run managed asset assertions for allowed depth=2 graph. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-004 | S02 | Define bounded depth=2 role graph and managed asset assertions | acceptance | AC-003 / EC-001 / EC-002 | Inspect skills/docs and run managed asset assertions forbidding depth=3 and child canonical edit/promotion. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-090 | S90 | Refresh dogfooding-visible skills/docs/template evidence | acceptance | AC-004 | Inspect dogfooding-visible .agents/skills and docs/template evidence after validate; provider install_root parity belongs to S01/S02. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-099 | S99 | final quality | acceptance | all AC/EC | final QA/code/spec gates pass and report ledger closes every required row | final integrated issue state | false completion | yes | reviewer evidence | final report evidence |

## レビュー / QA ゲート方針
- Step review: docs/templates/skills-only -> `spec-reviewer`; runtime/tests/scaffold behavior -> `code-reviewer`.
- S90 docs impact: `spec-reviewer` pass.
- S99 final quality: `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer` all pass.

## 実装ステップ
### 実装ステップ S01 — Define evidence adoption ledger schema in docs/templates/report scaffolds
- 振る舞いの目標: Define evidence adoption ledger schema in docs/templates/report scaffolds
- design 参照: `design.md` provider source / dogfooding surface / test strategy
- 対象ファイル:
      - src/spec_dock/assets/spec_dock/docs/
      - src/spec_dock/assets/spec_dock/templates/
- 閉じる closure id: tc-001, tc-002
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
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00122-evidence-adoption-ledger-depth2-delegation/report.md
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00122-evidence-adoption-ledger-depth2-delegation/discussions/
- forbidden changes:
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00113-* through iss-00118-* report/plan rewrites
      - unrelated provider/runtime files outside the listed allowed paths
      - final authority, reviewer pass, or promotion claims
- required verification: tc-001: Inspect provider report templates/docs for adopted, partially adopted, rejected, deferred, stale, and blocked ledger dispositions., tc-002: Inspect workflow docs/templates for unresolved blocking ledger item preventing promotion.
- reviewer focus: spec-reviewer
- output required: changed files, verification result for each closure id, unresolved risks, Ledger Note or no-material-decision statement.
- stop conditions: input docs conflict, path outside allowed scope, forbidden v0 rewrite, verification cannot run, or acceptance cannot be met.

#### 具体テストケース一覧
- `tc-001`: Inspect provider report templates/docs for adopted, partially adopted, rejected, deferred, stale, and blocked ledger dispositions.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `rg -n 'adopted|partially_adopted|rejected|deferred|blocked|stale' src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates src/spec_dock/assets/spec_dock/system/active-none` を実行する。
  - 期待結果: evidence adoption ledger dispositions are defined in provider docs/templates/report scaffolds.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: ledger disposition hit lines and coverage判定を `report.md` に記録する。
  - 記録先: Step Contract Closure / Test Contract Closure / Closure Coverage.
- `tc-002`: Inspect workflow docs/templates for unresolved blocking ledger item preventing promotion.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `rg -n 'unresolved|blocked|promotion|cannot promote|must not promote|stale' src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates` を実行する。
  - 期待結果: unresolved blocking ledger items prevent promotion and require explicit disposition.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: blocking-ledger rule evidenceを `report.md` に記録する。
  - 記録先: Step Contract Closure / Test Contract Closure / Closure Coverage.

#### ステップ完了契約
- close 条件: all listed closure ids pass by targeted evidence.
- report evidence: Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta.
- 残リスク: unresolved host/runtime/doc ambiguity requires decision ledger entry and possible plan amendment.

#### ステップゲート
- step reviewer gate: spec-reviewer `review_status: pass`
- commit / no-op gate: one behavior slice, committed or justified approved-no-op only after reviewer pass.
### 実装ステップ S02 — Define bounded depth=2 role graph and managed asset assertions
- 振る舞いの目標: Define bounded depth=2 role graph and managed asset assertions
- design 参照: `design.md` provider source / dogfooding surface / test strategy
- 対象ファイル:
      - src/spec_dock/assets/spec_dock/docs/
      - src/spec_dock/assets/spec_dock/templates/
      - src/spec_dock/assets/install_root/.agents/skills/
      - tests/test_init_update.py
- 閉じる closure id: tc-003, tc-004
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
      - src/spec_dock/assets/install_root/.agents/skills/
      - tests/test_init_update.py
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00122-evidence-adoption-ledger-depth2-delegation/report.md
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00122-evidence-adoption-ledger-depth2-delegation/discussions/
- forbidden changes:
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00113-* through iss-00118-* report/plan rewrites
      - unrelated provider/runtime files outside the listed allowed paths
      - final authority, reviewer pass, or promotion claims
- required verification: tc-003: Inspect skills/docs and run managed asset assertions for allowed depth=2 graph., tc-004: Inspect skills/docs and run managed asset assertions forbidding depth=3 and child canonical edit/promotion.
- reviewer focus: code-reviewer
- output required: changed files, verification result for each closure id, unresolved risks, Ledger Note or no-material-decision statement.
- stop conditions: input docs conflict, path outside allowed scope, forbidden v0 rewrite, verification cannot run, or acceptance cannot be met.

#### 具体テストケース一覧
- `tc-003`: Inspect skills/docs and run managed asset assertions for allowed depth=2 graph.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `rg -n 'depth=2|depth 2|leaf-only|child specialist|reviewer independence|final reviewer' src/spec_dock/assets/install_root/.agents/skills src/spec_dock/assets/spec_dock/docs` と `uv run pytest tests/test_init_update.py` を実行する。
  - 期待結果: bounded depth=2 graph is documented in skills/docs and managed asset assertions pass.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: rg evidence, pytest result, and allowed graph summaryを `report.md` に記録する。
  - 記録先: Step Contract Closure / Test Contract Closure / Closure Coverage.
- `tc-004`: Inspect skills/docs and run managed asset assertions forbidding depth=3 and child canonical edit/promotion.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `rg -n 'depth=3|grandchild|canonical edit|promotion claim|final authority|forbidden' src/spec_dock/assets/install_root/.agents/skills src/spec_dock/assets/spec_dock/docs` と `uv run pytest tests/test_init_update.py` を実行する。
  - 期待結果: depth=3, child canonical edit, and child promotion/final-review authority are forbidden by docs/skills/assertions.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: forbidden graph evidence and pytest resultを `report.md` に記録する。
  - 記録先: Step Contract Closure / Test Contract Closure / Closure Coverage.

#### ステップ完了契約
- close 条件: all listed closure ids pass by targeted evidence.
- report evidence: Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta.
- 残リスク: unresolved host/runtime/doc ambiguity requires decision ledger entry and possible plan amendment.

#### ステップゲート
- step reviewer gate: code-reviewer `review_status: pass`
- commit / no-op gate: one behavior slice, committed or justified approved-no-op only after reviewer pass.

### 実装ステップ S90 — Refresh dogfooding-visible skills/docs/template evidence
- 振る舞いの目標: Refresh dogfooding-visible skills/docs/template evidence
- design 参照: `design.md` provider source / dogfooding surface / test strategy
- 対象ファイル:
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00122-evidence-adoption-ledger-depth2-delegation/report.md
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00122-evidence-adoption-ledger-depth2-delegation/discussions/
      - spec-dock/docs/ (inspection only)
      - spec-dock/templates/ (inspection only)
      - .agents/skills/ (inspection only)
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
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00122-evidence-adoption-ledger-depth2-delegation/report.md
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00122-evidence-adoption-ledger-depth2-delegation/discussions/
      - spec-dock/docs/ (inspection only)
      - spec-dock/templates/ (inspection only)
      - .agents/skills/ (inspection only)
- forbidden changes:
      - provider source changes during S90; put them in an implementation step with code-reviewer/spec-reviewer mapping
      - runtime/test/scaffold behavior changes under a spec-reviewer-only gate
- required verification: tc-090: Inspect dogfooding-visible .agents/skills and docs/template evidence after validate; provider install_root parity belongs to S01/S02.
- reviewer focus: spec-reviewer
- output required: changed files, verification result for each closure id, unresolved risks, Ledger Note or no-material-decision statement.
- stop conditions: input docs conflict, path outside allowed scope, forbidden v0 rewrite, verification cannot run, or acceptance cannot be met.

#### 具体テストケース一覧
- `tc-090`: Inspect dogfooding-visible .agents/skills and docs/template evidence after validate; provider install_root parity belongs to S01/S02.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `./spec-dock/scripts/spec-dock validate` を実行し、`rg -n 'adopted|depth=2|reviewer independence|blocked' spec-dock/docs spec-dock/templates spec-dock/system/active-none .agents/skills` を dogfooding inspection only で実行する。
  - 期待結果: dogfooding-visible docs/skills expose ledger/depth semantics; provider install_root is not inspected as an S90 write scope.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: validate output, dogfooding rg evidence, and S90 no provider/runtime/test edits statementを `report.md` に記録する。
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
