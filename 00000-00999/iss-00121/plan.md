---
種別: 実装計画書（Issue）
ID: "iss-00121"
タイトル: "Authority Aware Context Pack and Lifecycle Gates"
関連GitHub: ["#121"]
状態: "approved"
作成者: "Codex"
最終更新: "2026-05-23"
依存: ["requirement.md", "design.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00121 Authority Aware Context Pack and Lifecycle Gates — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID
- Issue AC/EC: defined in `requirement.md`.
- Parent Epic mapping: defined in `requirement.md` and `design.md`; no v0 Issue 001〜006 / #113〜#118 rewrite is allowed.

## 依存関係から導く実装順序
- 正本: `design.md` dependency analysis, module dependency diagram, and file change plan.
- 順序: provider contract -> tests/assertions/probes -> dogfooding parity -> S90 docs impact -> S99 final quality.
- Allowed paths are resolved in each implementation step below; executors must not infer broader scope from prose.

## ステップ一覧
- S01:
  - 観測可能な振る舞い: Add authority/grant read model and validation contract
  - delegated role: dev-coder
  - closure id: tc-001, tc-002
  - reviewer gate: code-reviewer
- S02:
  - 観測可能な振る舞い: Apply purpose-aware context-pack and lifecycle blocking
  - delegated role: dev-coder
  - closure id: tc-003, tc-004
  - reviewer gate: code-reviewer
- S90:
  - 観測可能な振る舞い: Document lifecycle semantics and dogfooding parity
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
| tc-001 | S01 | Add authority/grant read model and validation contract | acceptance | AC-003 / EC-001 | Run targeted runtime/domain tests proving missing authority metadata fails closed. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-002 | S01 | Add authority/grant read model and validation contract | acceptance | AC-003 / EC-002 / EC-003 | Run targeted runtime/domain tests proving invalid authority state or stale promotion record fails closed. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-003 | S02 | Apply purpose-aware context-pack and lifecycle blocking | acceptance | AC-001 / AC-002 / EC-001 | Run CLI/runtime tests proving proposed artifacts are excluded or block implementation/ready/finish contexts. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-004 | S02 | Apply purpose-aware context-pack and lifecycle blocking | acceptance | AC-002 / EC-002 | Run CLI/runtime tests proving approved artifacts require the exact grant for the requested lifecycle purpose. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-090 | S90 | Document lifecycle semantics and dogfooding parity | acceptance | AC-004 / EC-003 | Inspect workflow docs and dogfooding runtime copies for matching lifecycle semantics. | exact command or inspection target named in the test case below | vague evidence or scope drift | yes | exact command output or named inspection evidence | report Step/Test Closure |
| tc-099 | S99 | final quality | acceptance | all AC/EC | final QA/code/spec gates pass and report ledger closes every required row | final integrated issue state | false completion | yes | reviewer evidence | final report evidence |

## レビュー / QA ゲート方針
- Step review: docs/templates/skills-only -> `spec-reviewer`; runtime/tests/scaffold behavior -> `code-reviewer`.
- S90 docs impact: `spec-reviewer` pass.
- S99 final quality: `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer` all pass.

## 実装ステップ
### 実装ステップ S01 — Add authority/grant read model and validation contract
- 振る舞いの目標: Add authority/grant read model and validation contract
- design 参照: `design.md` provider source / dogfooding surface / test strategy
- 対象ファイル:
      - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
      - src/spec_dock/assets/spec_dock/docs/workflow_issue.md
      - src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md
      - tests/cli_runtime/
      - tests/domain_runtime/
      - tests/presentation_runtime/
- 閉じる closure id: tc-001, tc-002
- 計画済み契約:
  - scope: listed allowed paths only.
  - Red / 代替証跡: each closure id below names the command, inspection, or manual evidence.
  - Green 検証: targeted evidence for every closure id is recorded in `report.md`.
  - amendment trigger: allowed paths, closes mapping, authority model, required closure id, or fallback condition changes.

#### 委任契約
- delegated role: dev-coder
- source of truth: this `requirement.md`, this `design.md`, parent epic v1 amendment, and `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/discussions/20260523t144246z-disc-v1-issue-authoring-delegated-evidence.md`
- allowed changes:
      - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
      - src/spec_dock/assets/spec_dock/docs/workflow_issue.md
      - src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md
      - tests/cli_runtime/
      - tests/domain_runtime/
      - tests/presentation_runtime/
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00121-authority-aware-context-pack-lifecycle-gates/report.md
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00121-authority-aware-context-pack-lifecycle-gates/discussions/
- forbidden changes:
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00113-* through iss-00118-* report/plan rewrites
      - unrelated provider/runtime files outside the listed allowed paths
      - final authority, reviewer pass, or promotion claims
- required verification: tc-001/tc-002: attempt the planned pytest commands; if pytest is unavailable because this repo has no pytest dependency, run `uv run python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_issue_lifecycle tests.cli_runtime.test_runtime_active_s05` as the approved fallback for the authority gate/runtime assertions added in this issue.
- reviewer focus: code-reviewer
- output required: changed files, verification result for each closure id, unresolved risks, Ledger Note or no-material-decision statement.
- stop conditions: input docs conflict, path outside allowed scope, forbidden v0 rewrite, verification cannot run, or acceptance cannot be met.

#### 具体テストケース一覧
- `tc-001`: Run targeted runtime/domain tests proving missing authority metadata fails closed.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `uv run pytest tests/domain_runtime tests/cli_runtime -k 'authority or grants or metadata'` を実行する。`pytest` executable が unavailable の場合、この repository は `unittest` を標準 test runner としているため、fallback として `uv run python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_issue_lifecycle tests.cli_runtime.test_runtime_active_s05` を実行する。
  - 期待結果: missing authority metadata fails closed in targeted domain/runtime tests.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: pytest attempt result, fallback unittest command/pass summary, and failing-closed test names/resultを `report.md` に記録する。
  - 記録先: Step Contract Closure / Test Contract Closure / Closure Coverage.
- `tc-002`: Run targeted runtime/domain tests proving invalid authority state or stale promotion record fails closed.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `uv run pytest tests/domain_runtime tests/cli_runtime -k 'stale or promotion or authority'` を実行する。`pytest` executable が unavailable の場合、この repository は `unittest` を標準 test runner としているため、fallback として `uv run python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_issue_lifecycle tests.cli_runtime.test_runtime_active_s05` を実行する。
  - 期待結果: invalid authority state and stale promotion record are rejected, not silently accepted.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: pytest attempt result, fallback unittest command/pass summary, selected test names, and rejection evidenceを `report.md` に記録する。
  - 記録先: Step Contract Closure / Test Contract Closure / Closure Coverage.

#### ステップ完了契約
- close 条件: all listed closure ids pass by targeted evidence.
- report evidence: Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta.
- 残リスク: unresolved host/runtime/doc ambiguity requires decision ledger entry and possible plan amendment.

#### ステップゲート
- step reviewer gate: code-reviewer `review_status: pass`
- commit / no-op gate: one behavior slice, committed or justified approved-no-op only after reviewer pass.

### 実装ステップ S02 — Apply purpose-aware context-pack and lifecycle blocking
- 振る舞いの目標: Apply purpose-aware context-pack and lifecycle blocking
- design 参照: `design.md` provider source / dogfooding surface / test strategy
- 対象ファイル:
      - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
      - src/spec_dock/assets/spec_dock/docs/workflow_issue.md
      - src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md
      - tests/cli_runtime/
      - tests/domain_runtime/
      - tests/presentation_runtime/
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
      - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
      - src/spec_dock/assets/spec_dock/docs/workflow_issue.md
      - src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md
      - tests/cli_runtime/
      - tests/domain_runtime/
      - tests/presentation_runtime/
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00121-authority-aware-context-pack-lifecycle-gates/report.md
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00121-authority-aware-context-pack-lifecycle-gates/discussions/
- forbidden changes:
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00113-* through iss-00118-* report/plan rewrites
      - unrelated provider/runtime files outside the listed allowed paths
      - final authority, reviewer pass, or promotion claims
- required verification: tc-003/tc-004: attempt the planned pytest commands; if pytest is unavailable because this repo has no pytest dependency, run `uv run python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_issue_lifecycle tests.cli_runtime.test_runtime_active_s05` as the approved fallback for the context-pack and lifecycle gate assertions added in this issue.
- reviewer focus: code-reviewer
- output required: changed files, verification result for each closure id, unresolved risks, Ledger Note or no-material-decision statement.
- stop conditions: input docs conflict, path outside allowed scope, forbidden v0 rewrite, verification cannot run, or acceptance cannot be met.

#### 具体テストケース一覧
- `tc-003`: Run CLI/runtime tests proving proposed artifacts are excluded or block implementation/ready/finish contexts.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `uv run pytest tests/cli_runtime -k 'context_pack or lifecycle or proposed'` を実行し、必要なら `./spec-dock/scripts/spec-dock active show` と context-pack出力を添付確認する。`pytest` executable が unavailable の場合、この repository は `unittest` を標準 test runner としているため、fallback として `uv run python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_issue_lifecycle tests.cli_runtime.test_runtime_active_s05` を実行する。
  - 期待結果: proposed artifacts are excluded from implementation/ready/finish context or block those lifecycle paths with an explicit diagnostic.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: pytest attempt result, fallback unittest output, and context-pack/lifecycle diagnostic evidenceを `report.md` に記録する。
  - 記録先: Step Contract Closure / Test Contract Closure / Closure Coverage.
- `tc-004`: Run CLI/runtime tests proving approved artifacts require the exact grant for the requested lifecycle purpose.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `uv run pytest tests/cli_runtime tests/domain_runtime -k 'grant or lifecycle or approved'` を実行する。`pytest` executable が unavailable の場合、この repository は `unittest` を標準 test runner としているため、fallback として `uv run python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_issue_lifecycle tests.cli_runtime.test_runtime_active_s05` を実行する。
  - 期待結果: approved artifacts require the exact grant for the requested lifecycle purpose; unrelated or missing grants fail closed.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: pytest attempt result, fallback unittest output, grant-purpose test output, and exact grant mapping evidenceを `report.md` に記録する。
  - 記録先: Step Contract Closure / Test Contract Closure / Closure Coverage.

#### ステップ完了契約
- close 条件: all listed closure ids pass by targeted evidence.
- report evidence: Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta.
- 残リスク: unresolved host/runtime/doc ambiguity requires decision ledger entry and possible plan amendment.

#### ステップゲート
- step reviewer gate: code-reviewer `review_status: pass`
- commit / no-op gate: one behavior slice, committed or justified approved-no-op only after reviewer pass.

### 実装ステップ S90 — Document lifecycle semantics and dogfooding parity
- 振る舞いの目標: Document lifecycle semantics and dogfooding parity
- design 参照: `design.md` provider source / dogfooding surface / test strategy
- 対象ファイル:
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00121-authority-aware-context-pack-lifecycle-gates/report.md
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00121-authority-aware-context-pack-lifecycle-gates/discussions/
      - spec-dock/active/context-pack.md (inspection only)
      - spec-dock/.agent/active.json (inspection only)
      - spec-dock/docs/ (generated dogfooding docs parity output and inspection only; provider docs behavior ownership remains S01/S02)
      - spec-dock/scripts/spec_dock_runtime/ (generated dogfooding parity output only; behavior ownership remains S01/S02)
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
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00121-authority-aware-context-pack-lifecycle-gates/report.md
      - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00121-authority-aware-context-pack-lifecycle-gates/discussions/
      - spec-dock/active/context-pack.md (inspection only)
      - spec-dock/.agent/active.json (inspection only)
      - spec-dock/docs/ (generated dogfooding docs parity output and inspection only; provider docs behavior ownership remains S01/S02)
      - spec-dock/scripts/spec_dock_runtime/ (generated dogfooding parity output only; behavior ownership remains S01/S02)
- forbidden changes:
      - provider source changes during S90; put them in an implementation step with code-reviewer/spec-reviewer mapping
      - runtime/test/scaffold behavior changes under a spec-reviewer-only gate; generated dogfooding parity copies may be inspected/recorded here only when the provider behavior change is already owned by S01/S02 code-reviewer scope
- required verification: tc-090: Inspect workflow docs and dogfooding runtime copies for matching lifecycle semantics.
- reviewer focus: spec-reviewer
- output required: changed files, verification result for each closure id, unresolved risks, Ledger Note or no-material-decision statement.
- stop conditions: input docs conflict, path outside allowed scope, forbidden v0 rewrite, verification cannot run, or acceptance cannot be met.

#### 具体テストケース一覧
- `tc-090`: Inspect workflow docs and dogfooding runtime copies for matching lifecycle semantics.
  - 前提: parent Epic v1 amendment and this Issue requirement/design are approved.
  - 操作: `rg -n 'authority|grant|proposed|approved|context-pack|finish|ready' spec-dock/docs spec-dock/active/context-pack.md spec-dock/.agent/active.json` を inspection only で実行し、`./spec-dock/scripts/spec-dock validate` を実行する。
  - 期待結果: dogfooding docs/context state match lifecycle semantics, and validate passes or documented fallback is present.
  - 失敗検出: required field, command output, inspection result, manual evidence, or reviewer evidence is missing, contradictory, stale, or outside the allowed paths; in that case the closure id remains open and the step cannot claim pass.
  - 検証方法: rg/validate output and no S90 provider/runtime/test edits statementを `report.md` に記録する。
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
