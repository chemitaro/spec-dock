---
種別: 実装計画書（Issue）
ID: "iss-00123"
タイトル: "Role Scoped Permission Profiles and Task Manifest Probes"
関連GitHub: ["#123"]
状態: "approved"
作成者: "Codex"
最終更新: "2026-05-23"
依存: ["requirement.md", "design.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00123 Role Scoped Permission Profiles and Task Manifest Probes — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID
- Issue AC/EC: defined in `requirement.md`.
- Parent Epic mapping: defined in `requirement.md` and `design.md`; no v0 Issue 001〜006 / #113〜#118 rewrite is allowed.

## 依存関係から導く実装順序
- 正本: `design.md` dependency analysis, module dependency diagram, and file change plan.
- 順序: provider contract -> tests/assertions/probes -> dogfooding parity -> S90 docs impact -> S99 final quality.
- Allowed paths are resolved in each implementation step below; executors must not infer broader scope from prose.

## ステップ一覧
- S01:
  - 観測可能な振る舞い: Define task manifest and role-scoped Permission Profile contract
  - delegated role: doc-writer
  - closure id: tc-001
  - reviewer gate: spec-reviewer
- S02:
  - 観測可能な振る舞い: Add agent assets/assertions and probe evidence plan
  - delegated role: dev-coder
  - closure id: tc-002, tc-003, tc-004
  - reviewer gate: code-reviewer
- S90:
  - 観測可能な振る舞い: Document host fallback and dogfooding probe evidence placement
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
| tc-001 | S01 | Define task manifest and role-scoped Permission Profile contract | acceptance | AC-001 / EC-001 | Inspect task manifest docs for resolved canonical target, input revision/hash, allowed paths, forbidden paths, probe commands, and fallback policy. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-002 | S02 | Add agent assets/assertions and probe evidence plan | acceptance | AC-002 | Run or document positive write probe evidence for allowed artifact/evidence paths only. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-003 | S02 | Add agent assets/assertions and probe evidence plan | acceptance | AC-003 / EC-002 | Run or document negative write probe evidence proving forbidden implementation/config paths are blocked. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-004 | S02 | Add agent assets/assertions and probe evidence plan | acceptance | AC-004 / EC-003 | Inspect report/fallback policy proving fail-open, unavailable, or divergent probes disable write-scoped delegation. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-090 | S90 | Document host fallback and dogfooding probe evidence placement | acceptance | AC-004 | Inspect .codex agent assets and docs for fallback evidence placement and provider-first parity. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-099 | S99 | final quality | acceptance | all AC/EC | final QA/code/spec gates pass and report ledger closes every required row | final integrated issue state | false completion | yes | reviewer evidence | final report evidence |

## レビュー / QA ゲート方針
- Step review: docs/templates/skills-only -> `spec-reviewer`; runtime/tests/scaffold behavior -> `code-reviewer`.
- S90 docs impact: `spec-reviewer` pass.
- S99 final quality: `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer` all pass.

## 実装ステップ
### 実装ステップ S01 — Define task manifest and role-scoped Permission Profile contract
- 振る舞いの目標: Define task manifest and role-scoped Permission Profile contract
- design 参照: `design.md` provider source / dogfooding surface / test strategy
- 対象ファイル:
      - src/spec_dock/assets/install_root/.codex/AGENTS.md
      - src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md
- 閉じる closure id: tc-001
- 計画済み契約:
  - scope: listed allowed paths only.
  - Red / 代替証跡: each closure id below names the command, inspection, or manual evidence.
  - Green 検証: targeted evidence for every closure id is recorded in `report.md`.
  - amendment trigger: allowed paths, closes mapping, authority model, required closure id, or fallback condition changes.

#### 委任契約
- delegated role: doc-writer
- source of truth: this `requirement.md`, this `design.md`, parent epic v1 amendment, and `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/discussions/20260523t144246z-disc-v1-issue-authoring-delegated-evidence.md`
- allowed changes:
      - src/spec_dock/assets/install_root/.codex/AGENTS.md
      - src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00123-role-scoped-permission-profiles-task-manifest/report.md
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00123-role-scoped-permission-profiles-task-manifest/discussions/
- forbidden changes:
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00113-* through iss-00118-* report/plan rewrites
      - unrelated provider/runtime files outside the listed allowed paths
      - final authority, reviewer pass, or promotion claims
- required verification: tc-001: Inspect task manifest docs for resolved canonical target, input revision/hash, allowed paths, forbidden paths, probe commands, and fallback policy.
- reviewer focus: spec-reviewer
- output required: changed files, verification result for each closure id, unresolved risks, Ledger Note or no-material-decision statement.
- stop conditions: input docs conflict, path outside allowed scope, forbidden v0 rewrite, verification cannot run, or acceptance cannot be met.

#### 具体テストケース一覧
- `tc-001`: Inspect task manifest docs for resolved canonical target, input revision/hash, allowed paths, forbidden paths, probe commands, and fallback policy.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `rg -n 'task manifest|resolved target|input revision|allowed paths|forbidden paths|probe|fallback|default_permissions|permissions' src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md src/spec_dock/assets/install_root/.codex/AGENTS.md` を実行する。
  - 期待結果: task manifest contract names resolved canonical target, input revision/hash, allowed/forbidden paths, probe commands, and fallback policy.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: contract hit lines and missing-field checklistを `report.md` に記録する。
  - 記録先: Step Contract Closure / Test Contract Closure / Closure Coverage.

#### ステップ完了契約
- close 条件: all listed closure ids pass by targeted evidence.
- report evidence: Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta.
- 残リスク: unresolved host/runtime/doc ambiguity requires decision ledger entry and possible plan amendment.

#### ステップゲート
- step reviewer gate: spec-reviewer `review_status: pass`
- commit / no-op gate: one behavior slice, committed or justified approved-no-op only after reviewer pass.
### 実装ステップ S02 — Add agent assets/assertions and probe evidence plan
- 振る舞いの目標: Add agent assets/assertions and probe evidence plan
- design 参照: `design.md` provider source / dogfooding surface / test strategy
- 対象ファイル:
      - src/spec_dock/assets/install_root/.codex/agents/
      - src/spec_dock/assets/install_root/.codex/AGENTS.md
      - src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md
      - tests/test_init_update.py
      - manual CLI/Desktop write probe evidence
- 閉じる closure id: tc-002, tc-003, tc-004
- 計画済み契約:
  - scope: listed allowed paths only.
  - Red / 代替証跡: each closure id below names the command, inspection, or manual evidence.
  - Green 検証: targeted evidence for every closure id is recorded in `report.md`.
  - amendment trigger: allowed paths, closes mapping, authority model, required closure id, or fallback condition changes.

#### 委任契約
- delegated role: dev-coder
- source of truth: this `requirement.md`, this `design.md`, parent epic v1 amendment, and `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/discussions/20260523t144246z-disc-v1-issue-authoring-delegated-evidence.md`
- allowed changes:
      - src/spec_dock/assets/install_root/.codex/agents/
      - src/spec_dock/assets/install_root/.codex/AGENTS.md
      - src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md
      - tests/test_init_update.py
      - manual CLI/Desktop write probe evidence
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00123-role-scoped-permission-profiles-task-manifest/report.md
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00123-role-scoped-permission-profiles-task-manifest/discussions/
- forbidden changes:
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00113-* through iss-00118-* report/plan rewrites
      - unrelated provider/runtime files outside the listed allowed paths
      - final authority, reviewer pass, or promotion claims
- required verification: tc-002: Run or document positive write probe evidence for allowed artifact/evidence paths only., tc-003: Run or document negative write probe evidence proving forbidden implementation/config paths are blocked., tc-004: Inspect report/fallback policy proving fail-open, unavailable, or divergent probes disable write-scoped delegation.
- reviewer focus: code-reviewer
- output required: changed files, verification result for each closure id, unresolved risks, Ledger Note or no-material-decision statement.
- stop conditions: input docs conflict, path outside allowed scope, forbidden v0 rewrite, verification cannot run, or acceptance cannot be met.

#### 具体テストケース一覧
- `tc-002`: Run or document positive write probe evidence for allowed artifact/evidence paths only.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `rg -n 'default_permissions|permissions\.|write|read|deny|positive probe|allowed artifact|discussions' src/spec_dock/assets/install_root/.codex src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md` と `uv run pytest tests/test_init_update.py` を実行したうえで、hermetic probe または CLI probe を `report.md` に固定された safe target（例: issue-local `report.md` への marker 追記または `discussions/__permission_probe_allowed__.md` 作成）へ実行し、probe 後に cleanup する。
  - 期待結果: positive write probe contract exists, managed asset assertions pass, and the recorded probe writes only the allowed artifact/evidence path named in the Task Manifest; no implementation/config/test path diff is created.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: profile/probe rg evidence, pytest result, exact allowed probe command, target path, cleanup result, and `git diff -- <allowed-target>` / no unexpected diff evidenceを `report.md` に記録する。
  - 記録先: Step Contract Closure / Test Contract Closure / Closure Coverage.
- `tc-003`: Run or document negative write probe evidence proving forbidden implementation/config paths are blocked.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `rg -n 'negative probe|forbidden path|implementation code|tests/|package.json|pyproject|deny|blocked' src/spec_dock/assets/install_root/.codex src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md` と `uv run pytest tests/test_init_update.py` を実行したうえで、hermetic probe または CLI probe を forbidden target（例: `src/spec_dock/__codex_permission_probe_forbidden__.txt`, `tests/__codex_permission_probe_forbidden__.txt`, or `.codex/__codex_permission_probe_forbidden__.txt`）へ実行し、成功した場合は即 fail として cleanup する。
  - 期待結果: negative write probe contract exists, managed asset assertions pass, and the recorded probe fails closed for forbidden implementation/config/test paths; if the host cannot enforce or cannot run the probe, write-scoped delegation is disabled and fallback/proposal-only mode is recorded instead of pass.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: negative-probe command, forbidden target path, blocked/error output, cleanup status, pytest result, and fallback-disable evidenceを `report.md` に記録する。
  - 記録先: Step Contract Closure / Test Contract Closure / Closure Coverage.
- `tc-004`: Inspect report/fallback policy proving fail-open, unavailable, or divergent probes disable write-scoped delegation.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `rg -n 'fail closed|fail-open|unavailable|divergent|fallback|disable write-scoped delegation|Desktop|CLI' src/spec_dock/assets/install_root/.codex src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md` を実行する。
  - 期待結果: unavailable/divergent profile probes fail closed by disabling write-scoped delegation or falling back to proposal-only mode.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: fallback policy evidence and decision summaryを `report.md` に記録する。
  - 記録先: Step Contract Closure / Test Contract Closure / Closure Coverage.

#### ステップ完了契約
- close 条件: all listed closure ids pass by targeted evidence.
- report evidence: Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta.
- 残リスク: unresolved host/runtime/doc ambiguity requires decision ledger entry and possible plan amendment.

#### ステップゲート
- step reviewer gate: code-reviewer `review_status: pass`
- commit / no-op gate: one behavior slice, committed or justified approved-no-op only after reviewer pass.

### 実装ステップ S90 — Document host fallback and dogfooding probe evidence placement
- 振る舞いの目標: Document host fallback and dogfooding probe evidence placement
- design 参照: `design.md` provider source / dogfooding surface / test strategy
- 対象ファイル:
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00123-role-scoped-permission-profiles-task-manifest/report.md
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00123-role-scoped-permission-profiles-task-manifest/discussions/
      - .codex/agents/ (inspection only)
      - .codex/AGENTS.md (inspection only)
      - permission probe output recorded in report/discussions
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
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00123-role-scoped-permission-profiles-task-manifest/report.md
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00123-role-scoped-permission-profiles-task-manifest/discussions/
      - .codex/agents/ (inspection only)
      - .codex/AGENTS.md (inspection only)
      - permission probe output recorded in report/discussions
- forbidden changes:
      - provider source changes during S90; put them in an implementation step with code-reviewer/spec-reviewer mapping
      - runtime/test/scaffold behavior changes under a spec-reviewer-only gate
- required verification: tc-090: Inspect .codex agent assets and docs for fallback evidence placement and provider-first parity.
- reviewer focus: spec-reviewer
- output required: changed files, verification result for each closure id, unresolved risks, Ledger Note or no-material-decision statement.
- stop conditions: input docs conflict, path outside allowed scope, forbidden v0 rewrite, verification cannot run, or acceptance cannot be met.

#### 具体テストケース一覧
- `tc-090`: Inspect .codex agent assets and docs for fallback evidence placement and provider-first parity.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `./spec-dock/scripts/spec-dock validate` を実行し、`rg -n 'default_permissions|task manifest|probe|fallback' .codex/agents .codex/AGENTS.md spec-dock/docs` を dogfooding inspection only で実行する。
  - 期待結果: dogfooding-visible .codex agent assets/docs contain fallback evidence placement; S90 makes no provider/runtime/test edits.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: validate output, dogfooding inspection evidence, and no-edit statementを `report.md` に記録する。
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
