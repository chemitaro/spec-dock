---
種別: 実装計画書（Issue）
ID: "iss-00255"
タイトル: "Add Grade Aware Issue Authoring Smoke Tests"
Issue Grade: "strict"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00255 Add Grade Aware Issue Authoring Smoke Tests — Issue 実装計画書（Strict）

## 1. 実装戦略

G4 は R0〜G3 の本体 logic を実装せず、grade-aware Issue authoring workflow の統合 smoke matrix を追加する。既存 owner file に focused tests を置き、失敗時に R0 / G1 / G2 / G3 のどの surface が崩れたか分かるようにする。

Issue-local M99 は Epic 最終品質ゲートへの local closure checkpoint であり、個別 PR、PR Delivery Gate、Merge Preparation Gate は実行しない。

## 2. この計画で満たす要件ID

- AC-001: Lite remains lightweight.
- AC-002: Standard / Strict / Critical M99 gate exists.
- AC-003: draft source follows `authorized_profile`.
- AC-004: invalid assurance state is no-write.
- AC-005: placeholder artifacts are not ready.
- AC-006: evidence gates are observable.
- AC-007: provider and dogfooding docs stay aligned.
- AC-008: report records commands, results, skipped checks, and risks.

## 3. 依存関係から導く実装順序

1. S00 で既存 test surface と coverage を確認する。
2. S01 で Lite / Standard+ profile plan smoke を固定する。
3. S02 で draft routing と fail-closed no-write smoke を固定する。
4. S03 で readiness false-positive regression smoke を固定する。
5. S04 で report evidence gate smoke を固定する。
6. S90 で provider / dogfooding parity を確認する。
7. S95 で fresh spec review を通す。
8. S99 で issue-local handoff gate を閉じる。

## 4. 仕様固定クロージャ索引（Spec-Locked Closure Index）

| Closure ID | Requirement | 閉じる内容 | 検証レベル | Report evidence |
|---|---|---|---|---|
| C-G4-001 | AC-001 | Lite に途中 commit gate / full static analysis 必須が混入していない | CLI/template smoke | Test Contract Closure |
| C-G4-002 | AC-002 | Standard / Strict / Critical に M99 static analysis / lint / tests / report / commit gate がある | CLI/template smoke | Test Contract Closure |
| C-G4-003 | AC-003 | `draft-design` / `draft-plan` source が `authorized_profile` に従う | CLI smoke | Test Contract Closure |
| C-G4-004 | AC-004 | missing / invalid / stale `.assurance.json` で no-write fail-closed する | CLI negative smoke | Test Contract Closure |
| C-G4-005 | AC-005 | placeholder / heading-only / stale evidence が ready にならない | CLI/domain readiness smoke | Test Contract Closure |
| C-G4-006 | AC-006 | specialist evidence / EAL / fresh spec review relation を観測できる | domain evidence smoke | Test Contract Closure |
| C-G4-007 | AC-007 | provider / dogfooding docs and templates parity を確認できる | infra parity assertion or inspection | Docs Impact Resolution |
| C-G4-008 | AC-008 | command result、skipped reason、residual risk が report に残る | report evidence | Final Quality Gate |

## 5. 振る舞いバックログ

| Behavior | Milestone | 保証 | Closure |
|---|---|---|---|
| B-G4-001 | S01 | Lite remains lightweight | C-G4-001 |
| B-G4-002 | S01 | Standard+ M99 gate remains present | C-G4-002 |
| B-G4-003 | S02 | Draft routing follows authorized profile | C-G4-003 |
| B-G4-004 | S02 | Invalid assurance state is no-write | C-G4-004 |
| B-G4-005 | S03 | Readiness false positives are blocked | C-G4-005 |
| B-G4-006 | S04 | Evidence gate relations are observable | C-G4-006 |
| B-G4-007 | S90 | Provider and dogfooding parity is checked | C-G4-007 |
| B-G4-008 | S99 | Report evidence supports Epic handoff | C-G4-008 |

## 6. 実装ステップ

### S00 Baseline inspection

- behavior goal: 既存 tests がすでに覆う G2 / G3 / readiness surface を把握し、重複追加を避ける。
- planned contract:
  - scope: read-only inspection.
  - test obligation: covered-existing 判定の根拠を固定する。
  - red or alternative evidence requirement: inspect-only.
  - green verification: `rg` inspection と existing test list。
  - refactor guardrail: implementation file を編集しない。
  - amendment trigger: required AC を支える public seam が存在しない。
- delegation contract:
  - delegated role: repo-analyst or parent read-only inspection.
  - input docs: requirement.md, design.md, plan.md, Epic plan, related tests.
  - allowed paths: `tests/cli_runtime/test_new.py`, `tests/cli_runtime/test_workflow.py`, `tests/unit/domain/test_workflow_state.py`, `tests/unit/infra/test_init_update.py`.
  - forbidden changes: code, docs, templates, runtime behavior.
  - acceptance criteria: C-G4-001〜C-G4-008 の owner file が決まる。
  - required tests or docs-only verification: `rg -n "draft-design|draft-plan|report_evidence_gate|placeholder|workflow_issue_doc_matches" tests`.
  - reviewer focus: spec-reviewer が scope boundary を確認する。
  - stop conditions: owner file が決まらない、または upstream body logic が必要になる。
  - output required: report.md の session log と Closure Coverage。

#### 具体テストケース一覧

- `tc-s00-001` inspect: owner file mapping
  - 前提: active Issue と Epic plan が読める。
  - 操作: 関連 tests を `rg` で検索する。
  - 期待結果: draft routing、readiness、evidence gate、parity の owner file が特定できる。
  - 失敗検出: smoke を置く public seam がない状態を検出する。
  - 検証方法: `rg` output inspection。
  - 関連 closure id: C-G4-001, C-G4-002, C-G4-003, C-G4-004, C-G4-005, C-G4-006, C-G4-007

- `tc-s00-002` inspect: no upstream body ownership
  - 前提: R0〜G3 の scope boundary が Epic design にある。
  - 操作: G4 で runtime implementation を変更しない前提が成立するか確認する。
  - 期待結果: G4 は tests / parity / report evidence に閉じる。
  - 失敗検出: production behavior fix が必要な場合は plan amendment を要求する。
  - 検証方法: design boundary inspection。
  - 関連 closure id: C-G4-008

### S01 Profile plan smoke

- behavior goal: Lite と Standard+ の profile plan gate 差分を smoke で固定する。
- planned contract:
  - scope: profile template materialization smoke.
  - test obligation: Lite negative と Standard+ positive の両方。
  - red or alternative evidence requirement: red-required or covered-existing.
  - green verification: focused pytest.
  - refactor guardrail: profile template semantics を G4 で変更しない。
  - amendment trigger: Lite policy の再解釈が必要になる。
- delegation contract:
  - delegated role: dev-coder.
  - input docs: requirement.md, design.md, profile templates, existing `test_new.py`.
  - allowed paths: `tests/cli_runtime/test_new.py`.
  - forbidden changes: runtime resolver, profile template body, workflow docs.
  - acceptance criteria: C-G4-001 and C-G4-002 pass.
  - required tests or docs-only verification: `uv run pytest tests/cli_runtime/test_new.py -k "profile or m99 or lite"`.
  - reviewer focus: code-reviewer checks test sensitivity; spec-reviewer checks Lite / Standard+ semantics.
  - stop conditions: test requires production behavior changes.
  - output required: changed tests, command result, report ledger note.

#### 具体テストケース一覧

- `tc-s01-001` negative: Lite stays lightweight
  - 前提: Lite profile template or materialized draft-plan is available.
  - 操作: Lite plan text を検査する。
  - 期待結果: Lite に途中 commit gate と full static analysis mandatory がない。
  - 失敗検出: Lite が Standard+ gate を要求する regression を検出する。
  - 検証方法: focused pytest or structural assertion。
  - 関連 closure id: C-G4-001

- `tc-s01-002` positive: Standard+ M99 gate exists
  - 前提: Standard / Strict / Critical profile plan text が available。
  - 操作: M99 section を検査する。
  - 期待結果: static analysis、lint、tests、report、commit candidate gate がある。
  - 失敗検出: Standard+ final local quality gate が欠落する regression を検出する。
  - 検証方法: focused pytest or structural assertion。
  - 関連 closure id: C-G4-002

### S02 Draft routing and fail-closed smoke

- behavior goal: G2 routing と no-write fail-closed を integrated smoke として固定する。
- planned contract:
  - scope: `new doc draft-design` / `draft-plan` CLI tests.
  - test obligation: success path and no-write failure path.
  - red or alternative evidence requirement: covered-existing plus smoke.
  - green verification: focused pytest.
  - refactor guardrail: `draft-requirement` and Initiative / Epic draft behavior を変更しない。
  - amendment trigger: no-write を観測できない CLI contract gap。
- delegation contract:
  - delegated role: dev-coder.
  - input docs: G2 design, existing `test_new.py`, `.assurance.json` fixture helpers.
  - allowed paths: `tests/cli_runtime/test_new.py`.
  - forbidden changes: runtime `new doc` implementation and profile templates.
  - acceptance criteria: C-G4-003 and C-G4-004 pass.
  - required tests or docs-only verification: `uv run pytest tests/cli_runtime/test_new.py -k "authorized_profile_templates or no_write or stale"`.
  - reviewer focus: fail-closed path and preservation path.
  - stop conditions: production routing gap appears.
  - output required: Red/Green evidence and no-write discussion file count.

#### 具体テストケース一覧

- `tc-s02-001` success: authorized profile draft source
  - 前提: Issue has approved `.assurance.json` with authorized profile.
  - 操作: `draft-design` and `draft-plan` を生成する。
  - 期待結果: selected profile template source が draft に反映される。
  - 失敗検出: wrong profile or common placeholder template を使う regression を検出する。
  - 検証方法: `tests/cli_runtime/test_new.py` focused test。
  - 関連 closure id: C-G4-003

- `tc-s02-002` negative: invalid assurance no-write
  - 前提: `.assurance.json` is missing, invalid, or stale.
  - 操作: `draft-design` and `draft-plan` を実行する。
  - 期待結果: command fails and `discussions/` file set remains unchanged.
  - 失敗検出: invalid contract でも draft を書く regression を検出する。
  - 検証方法: `tests/cli_runtime/test_new.py` no-write assertion。
  - 関連 closure id: C-G4-004

### S03 Readiness regression smoke

- behavior goal: R0 readiness false-positive prevention を public guidance で smoke する。
- planned contract:
  - scope: workflow status / guidance tests and domain readiness tests.
  - test obligation: placeholder, heading-only, stale evidence, substantive ordinary-word case.
  - red or alternative evidence requirement: red-required or covered-existing.
  - green verification: focused pytest.
  - refactor guardrail: readiness classifier implementation は G4 で変更しない。
  - amendment trigger: R0 behavior gap が production code にある。
- delegation contract:
  - delegated role: dev-coder.
  - input docs: R0 plan/report, existing `test_workflow.py`, `test_workflow_state.py`.
  - allowed paths: `tests/cli_runtime/test_workflow.py`, `tests/unit/domain/test_workflow_state.py`.
  - forbidden changes: workflow implementation, guidance compiler, report evidence parser.
  - acceptance criteria: C-G4-005 pass.
  - required tests or docs-only verification: `uv run pytest tests/cli_runtime/test_workflow.py tests/unit/domain/test_workflow_state.py -k "placeholder or heading or stale"`.
  - reviewer focus: false positive and false block balance.
  - stop conditions: production readiness logic must change.
  - output required: command result and coverage mapping.

#### 具体テストケース一覧

- `tc-s03-001` negative: placeholder plan not ready
  - 前提: plan contains executable-looking headings but generated placeholder entries.
  - 操作: `guidance issue-execution` を実行する。
  - 期待結果: state is blocked and reason is plan-not-executable.
  - 失敗検出: placeholder plan が ready になる regression を検出する。
  - 検証方法: CLI workflow test。
  - 関連 closure id: C-G4-005

- `tc-s03-002` negative: stale evidence not ready
  - 前提: report or assurance source binding is stale.
  - 操作: `workflow status --format json` を実行する。
  - 期待結果: blocked or classification-required reason が返る。
  - 失敗検出: stale evidence が ready になる regression を検出する。
  - 検証方法: CLI/domain workflow test。
  - 関連 closure id: C-G4-005

### S04 Evidence gate smoke

- behavior goal: G3 report evidence gate の relation を grade-aware fixture で固定する。
- planned contract:
  - scope: `evaluate_report_evidence_gate` and CLI report readiness fixtures.
  - test obligation: positive row and negative missing / stale row.
  - red or alternative evidence requirement: red-required or covered-existing.
  - green verification: focused pytest.
  - refactor guardrail: report template / parser semantics を G4 で再設計しない。
  - amendment trigger: Standard / Strict / Critical fallback semantics が曖昧になる。
- delegation contract:
  - delegated role: dev-coder.
  - input docs: G3 report evidence gate docs, existing `test_workflow_state.py`.
  - allowed paths: `tests/unit/domain/test_workflow_state.py`, optionally `tests/cli_runtime/test_workflow.py`.
  - forbidden changes: production report gate implementation and templates.
  - acceptance criteria: C-G4-006 pass.
  - required tests or docs-only verification: `uv run pytest tests/unit/domain/test_workflow_state.py -k "report_evidence_gate or specialist or spec_review"`.
  - reviewer focus: evidence relation and missing-evidence reason code.
  - stop conditions: G3 semantics need amendment.
  - output required: positive/negative fixture evidence.

#### 具体テストケース一覧

- `tc-s04-001` positive: Strict evidence complete
  - 前提: report contains EAL, delegated draft evidence, Grade Specialist Evidence Gate, and fresh spec-reviewer pass.
  - 操作: `evaluate_report_evidence_gate(report, "strict")` を評価する。
  - 期待結果: status is pass and reason is report-evidence-valid.
  - 失敗検出: complete evidence が blocked になる regression を検出する。
  - 検証方法: domain unit test。
  - 関連 closure id: C-G4-006

- `tc-s04-002` negative: stale reviewer evidence blocks
  - 前提: report has stale or non-pass spec-reviewer row.
  - 操作: report evidence gate を評価する。
  - 期待結果: blocked reason が返る。
  - 失敗検出: stale reviewer evidence が pass になる regression を検出する。
  - 検証方法: domain unit test。
  - 関連 closure id: C-G4-006

### S90 Docs / parity impact

- behavior goal: provider / dogfooding docs and profile templates parity を確認する。
- planned contract:
  - scope: parity assertions or deterministic inspection.
  - test obligation: profile templates and grade-aware docs.
  - red or alternative evidence requirement: inspect-only or red-required if existing parity helper supports it.
  - green verification: focused infra pytest or documented inspection.
  - refactor guardrail: G4 は provider docs repair を無断で吸収しない。
  - amendment trigger: parity drift requires source edit.
- delegation contract:
  - delegated role: dev-coder for test assertion, repo-analyst for read-only inspection.
  - input docs: provider assets, dogfooding mirror, existing `test_init_update.py`.
  - allowed paths: `tests/unit/infra/test_init_update.py` for parity assertions; read-only provider/dogfooding docs.
  - forbidden changes: shipped docs/templates body unless plan amendment and reviewer gate are added.
  - acceptance criteria: C-G4-007 pass.
  - required tests or docs-only verification: `uv run pytest tests/unit/infra/test_init_update.py -k "workflow_spec_authoring or issue_profiles or dogfooding"`.
  - reviewer focus: source-of-truth and documented exceptions.
  - stop conditions: drift cannot be classified as intentional.
  - output required: parity result and exception list.

#### 具体テストケース一覧

- `tc-s90-001` parity: profile templates exist on both surfaces
  - 前提: provider and dogfooding template roots are available.
  - 操作: `issue-profiles/{lite,standard,strict,critical}/{design,plan}.md` を比較する。
  - 期待結果: all expected files exist and match expected parity contract.
  - 失敗検出: provider / dogfooding drift を検出する。
  - 検証方法: infra pytest or deterministic inspection。
  - 関連 closure id: C-G4-007

### S95 Strict spec review

- behavior goal: canonical requirement / design / plan / report が execution-ready か fresh spec-reviewer で確認する。
- planned contract:
  - scope: canonical docs and planning evidence.
  - test obligation: spec alignment review.
  - red or alternative evidence requirement: review-required.
  - green verification: `review_status: pass`.
  - refactor guardrail: reviewer pass を自己主張しない。
  - amendment trigger: reviewer finding P0/P1 or plan-not-executable finding.
- delegation contract:
  - delegated role: spec-reviewer.
  - input docs: requirement.md, design.md, plan.md, report.md, delegated drafts.
  - allowed paths: read-only.
  - forbidden changes: canonical edits by reviewer.
  - acceptance criteria: no blocking spec finding.
  - required tests or docs-only verification: reviewer output.
  - reviewer focus: AC traceability, G4 boundary, step-local test cases, Epic single PR policy.
  - stop conditions: review unavailable, denied, failed, stale.
  - output required: reviewer verdict and findings.

#### 具体テストケース一覧

- `tc-s95-001` review: planning handoff
  - 前提: design / plan / report adoption evidence is updated.
  - 操作: fresh spec-reviewer を実行する。
  - 期待結果: review_status is pass.
  - 失敗検出: unresolved spec gap or non-executable plan を検出する。
  - 検証方法: reviewer output。
  - 関連 closure id: C-G4-008

### S99 Issue-local handoff gate

- behavior goal: G4 の成果を commit 候補として閉じ、Epic 最終品質ゲートへ渡す。
- planned contract:
  - scope: focused tests, validate, report evidence, clean checkpoint.
  - test obligation: S01〜S90 の commands and skipped reasons.
  - red or alternative evidence requirement: covered by prior steps.
  - green verification: focused tests, `./spec-dock/scripts/spec-dock validate`, `git diff --check`.
  - refactor guardrail: no PR creation, no merge-preparation, no next-Epic work.
  - amendment trigger: final gate failure or unrecorded residual risk.
- delegation contract:
  - delegated role: main orchestrator for lifecycle; qa-reviewer / code-reviewer / spec-reviewer if final issue gate requires review.
  - input docs: all issue artifacts and test evidence.
  - allowed paths: report.md and files changed by approved implementation steps.
  - forbidden changes: PR creation, GitHub merge-prep, Epic final gate claim.
  - acceptance criteria: C-G4-001〜C-G4-008 closed or explicitly deferred with non-blocking rationale.
  - required tests or docs-only verification: focused pytest lane, validate, diff check.
  - reviewer focus: smoke sufficiency and Epic handoff readiness.
  - stop conditions: failing command, dirty uncommitted diff after commit, missing report evidence.
  - output required: command outputs, closure coverage, commit hash, handoff note.

#### 具体テストケース一覧

- `tc-s99-001` final: handoff evidence complete
  - 前提: all implementation steps are complete.
  - 操作: focused tests, validate, diff check を実行し report を更新する。
  - 期待結果: closure coverage is complete and no per-issue PR is created.
  - 失敗検出: unverified closure or premature PR creation を検出する。
  - 検証方法: command output and report inspection。
  - 関連 closure id: C-G4-008

## 7. 要件とステップ対応

| Requirement | Step |
|---|---|
| AC-001 | S01 |
| AC-002 | S01 |
| AC-003 | S02 |
| AC-004 | S02 |
| AC-005 | S03 |
| AC-006 | S04 |
| AC-007 | S90 |
| AC-008 | S95, S99 |

## 8. Final Exit Contract

- S01〜S90 の closure evidence が `report.md` にある。
- fresh spec-reviewer pass が `report.md` にある。
- focused tests と `./spec-dock/scripts/spec-dock validate` の結果または未実施理由が `report.md` にある。
- G4 checkpoint commit が作成され、worktree が clean である。
- `./spec-dock/scripts/spec-dock issue finish` が成功する。
- 個別 PR は作成しない。Epic PR は G4 完了後の Epic 最終品質ゲートで作成する。
