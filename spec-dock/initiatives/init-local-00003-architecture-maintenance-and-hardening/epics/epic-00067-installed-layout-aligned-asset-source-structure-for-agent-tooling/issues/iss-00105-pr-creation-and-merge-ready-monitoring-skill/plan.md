---
種別: 実装計画書（Issue）
ID: "iss-00105"
タイトル: "PR Creation And Merge Ready Monitoring Skill"
関連GitHub: ["#105"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-21"
依存: ["requirement.md", "design.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00105 PR Creation And Merge Ready Monitoring Skill — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007, AC-008, AC-009, AC-010
- EC:
  - EC-001, EC-002, EC-003, EC-004, EC-005, EC-006, EC-007
- 制約:
  - merge / auto-merge / branch delete / GitHub issue close / review comment reply / review thread resolve / admin override を行わない。
  - `pr-monitor` は read-only のまま維持する。
  - `issue_finish()` runtime semantics は変更しない。
  - provider asset を source of truth とし、dogfooding mirror と parity を保つ。

## 依存関係から導く実装順序
- 依存関係の正本:
  - `design.md` の `Module Dependency Diagram`、`インターフェース契約`、`ディレクトリ / ファイル変更計画`。
- 順序ルール:
  - まず shared skill の契約を固定し、その後 issue execution workflow へ接続する。
  - skill / workflow text の後に tests を更新し、最後に docs impact と final quality gate を閉じる。
- step 依存 summary:
  - S01:
    - 依存: reviewer-pass済み `requirement.md` / `design.md`
    - unblock: S02, S03
    - 対象ファイル: `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/**`, `.agents/skills/github-pr-merge-preparer/**`
  - S02:
    - 依存: S01 の shared skill contract
    - unblock: S03
    - 対象ファイル: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`, `.agents/skills/spec-dock-issue-execution/SKILL.md`, `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`, `spec-dock/docs/workflow_issue.md`
  - S03:
    - 依存: S01, S02
    - unblock: S90, S99
    - 対象ファイル: `src/spec_dock/cli.py`, `tests/cli_runtime/harness.py`, `tests/test_init_update.py`

## ステップ一覧
- S01:
  - 観測可能な振る舞い: `github-pr-merge-preparer` skill が PR 作成から merge-prepared 報告までの coordinator contract を定義する。
  - 依存: reviewer-pass済み design
  - unblock: issue execution integration と tests
  - 対象ファイル: new provider / dogfooding skill files
  - 閉じる要件: AC-001..AC-006, EC-001..EC-005, EC-007
  - レビューゲート: spec-reviewer
- S02:
  - 観測可能な振る舞い: `spec-dock-issue-execution` と `workflow_issue.md` が PR Delivery Gate / Merge Preparation Gate を final delivery として扱う。
  - 依存: S01
  - unblock: tests and final quality gate
  - 対象ファイル: issue-execution skill, workflow docs, dogfooding mirrors
  - 閉じる要件: AC-008, AC-009, AC-010, EC-006, EC-007
  - レビューゲート: spec-reviewer
- S03:
  - 観測可能な振る舞い: installer / dogfooding parity / content regression tests が新 skill と final delivery contract を守る。
  - 依存: S01, S02
  - unblock: final quality gate
  - 対象ファイル: `src/spec_dock/cli.py`, `tests/cli_runtime/harness.py`, `tests/test_init_update.py`
  - 閉じる要件: AC-007 and regression coverage for AC/EC
  - レビューゲート: code-reviewer
- S90:
  - 観測可能な振る舞い: docs impact が resolved になり、追加 docs 更新の要否が記録される。
- S99:
  - 観測可能な振る舞い: final QA / code / spec review が issue 全体を pass する。

## 要件 ↔ ステップ対応
- AC-001 -> S01
- AC-002 -> S01, S03
- AC-003 -> S01, S03
- AC-004 -> S01, S03
- AC-005 -> S01, S03
- AC-006 -> S01, S03
- AC-007 -> S03
- AC-008 -> S02, S03
- AC-009 -> S02, S03
- AC-010 -> S02, S03
- EC-001 -> S01, S03
- EC-002 -> S01, S03
- EC-003 -> S01, S03
- EC-004 -> S01, S03
- EC-005 -> S01, S03
- EC-006 -> S02, S03
- EC-007 -> S02, S03

## Spec-Locked Closure Index（仕様固定クロージャ索引）

| id | step | slice | type | spec link | locked expectation | observable input/state | bug class guarded | required | evidence level | closure evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | merge-preparer skill workflow | acceptance | AC-001..AC-006, EC-001..EC-005, EC-007 | New skill defines one-stage PR create/find -> monitor -> classify -> bounded fix delegation -> commit/push confirmation -> re-monitor -> merge-prepared or human gate reporting, including unresolved review-thread limitation disclosure and human gate for unclear feedback. | Provider and dogfooding `github-pr-merge-preparer/SKILL.md` content. | PR creation treated as terminal; unbounded repair loop; accidental merge authority; merge-prepared reported despite unknown unresolved review state. | yes | inspect-only | report step closure + spec-reviewer pass |
| tc-002 | S01 | skill interface metadata | acceptance | AC-007 | New skill has `agents/openai.yaml` metadata consistent with existing GitHub shared skills. | Provider and dogfooding `agents/openai.yaml`. | skill unavailable from installed managed assets. | yes | inspect-only | report step closure + asset inventory test |
| tc-003 | S02 | issue execution final delivery | acceptance | AC-008, AC-009, AC-010, EC-006, EC-007 | Issue execution final completion includes PR Delivery Gate and Merge Preparation Gate before `issue finish`, while `issue_finish()` semantics remain lifecycle-only. | Provider and dogfooding issue-execution skill / workflow docs. | implementation complete reported before PR readiness; runtime lifecycle command drift. | yes | inspect-only | report step closure + spec-reviewer pass |
| tc-004 | S03 | managed asset inventory | regression | AC-007 | New skill files are included in install/update managed asset inventory and dogfooding parity checks. | `tests/test_init_update.py` assertions and generated target install/update behavior. | missing installed skill; provider/mirror drift. | yes | red-required | failing test before asset inventory update; green targeted unittest |
| tc-005 | S03 | content regression | regression | AC-001..AC-010, EC-001..EC-007 | Tests lock stable phrases for merge-preparer workflow, final delivery integration, non-merge boundary, base resolution, non-required check waiver, unresolved review-thread limitation human gate, and fix-loop stop contract. | `tests/test_init_update.py` content assertions. | prose regression that removes critical workflow boundaries. | yes | red-required | failing test before content update; green targeted unittest |
| tc-006 | S90 | docs impact | governance | design.md test strategy | No additional docs beyond planned skill/workflow docs are required, or required docs are updated and reviewed. | docs/templates/README/workflow/skill impact inspection. | untracked documentation drift. | yes | inspect-only | report S90 evidence + spec-reviewer result |
| tc-007 | S99 | final quality | governance | workflow_issue.md final gate | QA, code, and spec reviewers pass for whole issue before final commit. | final integrated diff and report evidence. | incomplete issue closure. | yes | manual-required | final review evidence in report |

## レビュー / QA ゲート方針
- RG1 step review:
  - S01, S02: `spec-reviewer` docs/spec alignment pass.
  - S03: `code-reviewer` pass because tests change; include docs/skill assertions in review scope.
- QG1 final QA:
  - `qa-reviewer` checks obligation coverage and whether additional integration/manual tests are needed.
- CG1 final code review:
  - `code-reviewer` reviews integrated issue diff after all implementation steps.
- SG1 final spec review:
  - `spec-reviewer` verifies requirement / design / plan / report / implementation / tests alignment.

## 実行ルール（全ステップ共通）
- Each implementation step is one review scope and one commit boundary.
- Parent orchestrator records observed evidence in `report.md`; workers return `Ledger Note` or `No material implementation decisions beyond the approved plan.`
- Shipped docs / templates / skills / workflow text are delegated to `doc-writer`.
- Tests are delegated to `dev-coder`.
- Any change to required closure expectation, allowed files, or issue lifecycle semantics requires plan amendment and fresh spec review.

## 実装ステップ

### S01 — Add `github-pr-merge-preparer` shared skill
- behavior goal:
  - A maintainer or orchestrator can invoke `github-pr-merge-preparer` and get a bounded workflow contract for preparing a PR for human merge judgment without performing merge.
- design 参照:
  - `design.md` インターフェース契約、Fix-loop stop contract、要件 / 例外 -> verification mapping。
- 依存:
  - reviewer-pass済み `requirement.md` / `design.md`
- unblock:
  - S02, S03
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml`
  - `.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `.agents/skills/github-pr-merge-preparer/agents/openai.yaml`
- planned contract:
  - scope:
    - `github-pr-merge-preparer` skill and metadata only.
  - test obligation:
    - closure id:
      - tc-001, tc-002
    - coverage rationale:
      - This is a shipped skill contract. Inspection and spec review are sufficient for text semantics; install availability is covered by S03 tests.
  - Red / alternative evidence requirement:
    - docs-only / inspect-only:
      - Code test is not meaningful before the skill text exists.
      - Alternative evidence path is file existence, content inspection, provider/dogfooding byte parity, and spec-reviewer pass.
  - implementation scope:
    - allowed paths:
      - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/**`
      - `.agents/skills/github-pr-merge-preparer/**`
    - forbidden changes:
      - Existing skill behavior, workflow docs, tests, runtime, or GitHub agents in this step.
      - Any wording that grants merge / auto-merge / issue close / review reply / thread resolve authority.
  - Green verification:
    - inspection:
      - Provider and dogfooding skill files exist and match.
      - Skill mentions `github-pr-creator`, `pr-monitor`, repair delegation, base resolution, non-required check waiver, unresolved review-thread limitation human gate, fix-loop limits, merge-prepared evidence, and forbidden writes.
  - Refactor / cleanup guardrail:
    - Keep text concise; do not implement CI parsing or review repair logic in the skill.
  - closure evidence requirements:
    - Step Contract Closure: tc-001, tc-002 pass.
    - Test Contract Closure: inspect-only evidence and spec-reviewer pass.
    - Closure Coverage: AC-001..AC-006 and EC-001..EC-005 / EC-007 mapped.
  - report evidence destination:
    - `report.md` S01 Red/Green/Refactor, Delegated Worker Evidence, Reviewer Gate Status, Step Commit Gate.
  - amendment trigger:
    - Need for new GitHub API wrapper, new monitor output, or changing merge / issue finish authority.

#### delegation contract
- delegated role:
  - doc-writer
- input docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-creator/SKILL.md`
  - `src/spec_dock/assets/install_root/.codex/agents/pr-monitor.toml`
  - `src/spec_dock/assets/install_root/.github/agents/pr-monitor.agent.md`
- allowed paths:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/**`
  - `.agents/skills/github-pr-merge-preparer/**`
- forbidden changes:
  - Runtime code, tests, workflow docs, existing skills, `.codex/agents`, `.github/agents`.
- acceptance criteria:
  - tc-001 and tc-002 close conditions are met.
- required tests or docs-only verification:
  - File existence and byte parity inspection.
  - Skill text inspection against design predicate list.
- reviewer focus:
  - spec-reviewer docs/spec alignment.
- output required:
  - changed files, verification result, unresolved risks, and `Ledger Note` or `No material implementation decisions beyond the approved plan.`
- stop conditions:
  - Existing skills conflict with the designed handoff contract.
  - New agent or API wrapper appears necessary.
  - The worker cannot keep merge / issue close out of scope.

#### 具体テストケース一覧

- `tc-s01-001` inspect-only: merge-preparer skill defines bounded PR preparation
  - 前提: provider and dogfooding skill files are created.
  - 操作: Inspect `SKILL.md`.
  - 期待結果: The skill defines create/find PR, `github-pr-creator` reuse, `pr-monitor` delegation, failure classification, fix-loop limits, latest head SHA re-monitoring, merge-prepared predicate evidence, unresolved review-thread limitation disclosure / human gate, human gate output, and forbidden write operations.
  - 失敗検出: Missing stop conditions, unresolved review limitation handling, merge authority, or PR creation-only completion would be detected by inspection/spec review.
  - 検証方法: Docs inspection plus `spec-reviewer` pass.
  - 関連 closure id: tc-001

- `tc-s01-002` inspect-only: skill metadata exists and mirrors provider
  - 前提: `agents/openai.yaml` exists under provider and dogfooding skill folders.
  - 操作: Inspect metadata and compare provider / dogfooding files.
  - 期待結果: Metadata names `GitHub PR Merge Preparer` and describes bounded PR merge-preparation coordination.
  - 失敗検出: Missing metadata or mirror drift would make the skill unavailable or inconsistent.
  - 検証方法: File inspection; S03 locks this with asset/parity tests.
  - 関連 closure id: tc-002

#### step closure contract
- closure id:
  - tc-001, tc-002
- close 条件:
  - Provider and dogfooding files exist, match, and satisfy the designed contract.
- 検証 evidence:
  - File inspection and `spec-reviewer` pass.
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta.
- 残リスク:
  - Text semantics are inspect-only; S03 adds content regression guards.

#### step gate
- step reviewer gate:
  - reviewer: spec-reviewer
  - review 範囲: S01 changed skill files against requirement/design.
  - pass 条件: review_status: pass
  - re-review rule: 指摘を修正し pass まで再実行。
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S01 files only.
  - no-op: 不可。新 skill files are required.

### S02 — Integrate merge preparation into issue execution workflow
- behavior goal:
  - `spec-dock-issue-execution` and `workflow_issue.md` require final PR delivery and merge-preparation evidence before issue execution completion.
- design 参照:
  - `design.md` Sequence Delta, Domain Model Delta, Directory / file change plan.
- 依存:
  - S01
- unblock:
  - S03, S90, S99
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `spec-dock/docs/workflow_issue.md`
  - optionally `src/spec_dock/assets/install_root/.agents/skills/github-pr-creator/SKILL.md` and `.agents/skills/github-pr-creator/SKILL.md` if handoff wording must be clarified.
- planned contract:
  - scope:
    - Add final delivery handoff from issue execution to `github-pr-merge-preparer`.
    - Add `PR Delivery Gate` and `Merge Preparation Gate` evidence contract to workflow docs.
  - test obligation:
    - closure id:
      - tc-003
    - coverage rationale:
      - This is workflow policy text. Inspection and spec review verify semantics; S03 locks critical phrases.
  - Red / alternative evidence requirement:
    - docs-only / inspect-only:
      - Code behavior does not change.
      - Alternative evidence path is text inspection and spec-reviewer pass.
  - implementation scope:
    - allowed paths:
      - listed target files only.
    - forbidden changes:
      - Runtime `issue_finish()` implementation or tests.
      - Adding direct PR readiness checks to runtime commands.
      - Duplicating full merge-preparer workflow inside `spec-dock-issue-execution/SKILL.md`.
  - Green verification:
    - inspection:
      - `spec-dock-issue-execution` remains concise and points to `workflow_issue.md` / `github-pr-merge-preparer`.
      - `workflow_issue.md` contains PR Delivery Gate, Merge Preparation Gate, blocked/incomplete behavior, and `issue_finish()` lifecycle-only boundary.
  - Refactor / cleanup guardrail:
    - Keep `workflow_issue.md` as source of truth and skill as reminder.
  - closure evidence requirements:
    - Step Contract Closure: tc-003 pass.
    - Test Contract Closure: inspect-only evidence and spec-reviewer pass.
  - report evidence destination:
    - `report.md` S02 Red/Green/Refactor, Delegated Worker Evidence, Reviewer Gate Status, Step Commit Gate.
  - amendment trigger:
    - Need to alter runtime `issue_finish()` behavior, active state, or GitHub issue close behavior.

#### delegation contract
- delegated role:
  - doc-writer
- input docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - current provider and dogfooding `spec-dock-issue-execution/SKILL.md`
  - current provider and dogfooding `workflow_issue.md`
  - S01 `github-pr-merge-preparer/SKILL.md`
- allowed paths:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `spec-dock/docs/workflow_issue.md`
  - optional `github-pr-creator/SKILL.md` provider/dogfooding pair when necessary.
- forbidden changes:
  - Runtime code, tests, `pr-monitor` agent files, unrelated docs.
- acceptance criteria:
  - tc-003 close condition is met.
- required tests or docs-only verification:
  - Text inspection plus `spec-reviewer` pass.
- reviewer focus:
  - spec-reviewer docs/spec alignment.
- output required:
  - changed files, verification result, unresolved risks, and `Ledger Note` or `No material implementation decisions beyond the approved plan.`
- stop conditions:
  - Need to change runtime behavior.
  - The workflow text cannot express PR readiness without duplicating too much skill detail.
  - Existing docs contradict final delivery gate requirements.

#### 具体テストケース一覧

- `tc-s02-001` inspect-only: issue execution includes PR Delivery and Merge Preparation gates
  - 前提: S01 skill exists.
  - 操作: Inspect issue-execution skill and workflow docs.
  - 期待結果: Issue execution final delivery references `github-pr-merge-preparer`, records PR Delivery Gate and Merge Preparation Gate evidence, and treats failed/timeout/blocked PR preparation as incomplete.
  - 失敗検出: Issue execution could still report complete at final commit or PR creation only.
  - 検証方法: Docs inspection plus `spec-reviewer` pass.
  - 関連 closure id: tc-003

- `tc-s02-002` inspect-only: `issue_finish()` remains lifecycle closure only
  - 前提: Workflow docs are updated.
  - 操作: Inspect `workflow_issue.md`.
  - 期待結果: `issue finish` runs only after PR readiness evidence and does not itself guarantee PR, merge, checks, review, or final delivery completion.
  - 失敗検出: Runtime lifecycle command could be misread as PR readiness proof.
  - 検証方法: Docs inspection plus no-runtime-diff evidence for `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**`; final gate runs `uv run pytest tests/cli_runtime/test_issue_lifecycle.py -k "issue_finish"`.
  - 関連 closure id: tc-003

#### step closure contract
- closure id:
  - tc-003
- close 条件:
  - Skill and workflow docs express final delivery gates and issue_finish boundary without runtime semantic drift.
- 検証 evidence:
  - File inspection and `spec-reviewer` pass.
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta.
- 残リスク:
  - Full end-to-end PR preparation is not executed during this docs/skill step.

#### step gate
- step reviewer gate:
  - reviewer: spec-reviewer
  - review 範囲: S02 changed skill/workflow docs against requirement/design.
  - pass 条件: review_status: pass
  - re-review rule: 指摘を修正し pass まで再実行。
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S02 files only.
  - no-op: 不可。Workflow integration is required.

### S03 — Lock install/update, parity, and content regression tests
- behavior goal:
  - Tests fail if the new skill is omitted from managed assets, dogfooding parity drifts, or critical PR merge-preparation contract phrases disappear.
- design 参照:
  - `design.md` テスト戦略、要件 / 例外 -> verification mapping.
- 依存:
  - S01, S02
- unblock:
  - S90, S99
- 対象ファイル:
  - `src/spec_dock/cli.py`
  - `tests/cli_runtime/harness.py`
  - `tests/test_init_update.py`
- planned contract:
  - scope:
    - Update existing asset inventory / parity / content regression tests.
  - test obligation:
    - closure id:
      - tc-004, tc-005
    - coverage rationale:
      - New managed assets and critical prose contracts can regress silently unless tests assert their presence.
  - Red / alternative evidence requirement:
    - red-required:
      - Run targeted tests before or during implementation to observe missing asset/content assertions fail when practical.
      - If adding tests after files already exist, record inspect-only explanation for why pre-change red cannot be captured and run targeted green.
  - implementation scope:
    - allowed paths:
      - `src/spec_dock/cli.py`
      - `tests/cli_runtime/harness.py`
      - `tests/test_init_update.py`
    - forbidden changes:
      - Runtime behavior beyond adding `github-pr-merge-preparer` to the managed skill manifest.
      - Asset text, workflow docs.
  - Green verification:
    - command:
      - `uv run pytest tests/test_init_update.py -k "managed_skills or issue_71_checked_in_dogfooding_agent_tooling_parity or issue_105 or workflow_issue_doc_matches_bundled_asset"`
    - fallback:
      - If `-k` expression is too broad/narrow, run the specific updated test names and document exact command.
  - Refactor / cleanup guardrail:
    - Assert stable phrases, not whole paragraphs.
  - closure evidence requirements:
    - Step Contract Closure: tc-004, tc-005 pass.
    - Test Contract Closure: red/green or justified alternative evidence.
  - report evidence destination:
    - `report.md` S03 Red/Green/Refactor, Delegated Worker Evidence, Reviewer Gate Status, Step Commit Gate.
  - amendment trigger:
    - Tests require changing installer behavior beyond adding the managed skill manifest entry, or adding issue lifecycle runtime behavior.

#### delegation contract
- delegated role:
  - dev-coder
- input docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - S01/S02 changed files
  - `src/spec_dock/cli.py`
  - `tests/cli_runtime/harness.py`
  - `tests/test_init_update.py`
- allowed paths:
  - `src/spec_dock/cli.py`
  - `tests/cli_runtime/harness.py`
  - `tests/test_init_update.py`
- forbidden changes:
  - Runtime behavior beyond adding `github-pr-merge-preparer` to `_MANAGED_SKILL_NAMES`.
  - Assets, docs, broad test rewrites.
- acceptance criteria:
  - tc-004 and tc-005 close conditions are met.
- required tests or docs-only verification:
  - Targeted pytest command for updated tests.
- reviewer focus:
  - code-reviewer, with attention to brittle prose assertions and missing asset inventory coverage.
- output required:
  - changed files, test command/result, unresolved risks, and `Ledger Note` or `No material implementation decisions beyond the approved plan.`
- stop conditions:
  - Existing test structure cannot represent the new skill inventory without broader refactor.
  - Targeted tests require runtime or installer behavior changes beyond the managed skill manifest entry.

#### 具体テストケース一覧

- `tc-s03-001` regression: managed asset inventory includes merge-preparer skill
  - 前提: S01 created provider assets.
  - 操作: Run targeted init/update managed asset tests.
  - 期待結果: New `github-pr-merge-preparer/SKILL.md` and `agents/openai.yaml` are installed and tracked.
  - 失敗検出: New skill missing from install/update inventory.
  - 検証方法: `uv run pytest tests/test_init_update.py -k "managed_skills or issue_105"`
  - 関連 closure id: tc-004

- `tc-s03-002` regression: dogfooding parity includes merge-preparer and updated existing skills
  - 前提: Provider and dogfooding mirrors exist.
  - 操作: Run dogfooding parity test.
  - 期待結果: Provider and checked-in `.agents/skills`, `.codex`, `.github` parity remains byte-identical for managed files.
  - 失敗検出: Provider/dogfooding mirror drift.
  - 検証方法: `uv run pytest tests/test_init_update.py -k "issue_71_checked_in_dogfooding_agent_tooling_parity"`
  - 関連 closure id: tc-004

- `tc-s03-003` regression: final delivery contract phrases are protected
  - 前提: S01 and S02 text exists.
  - 操作: Run content regression tests.
  - 期待結果: Tests assert key phrases for `github-pr-merge-preparer`, `PR Delivery Gate`, `Merge Preparation Gate`, `failure_class`, non-required check waiver, unresolved review-thread limitation human gate, base-resolution precedence, and `issue_finish()` lifecycle-only boundary.
  - 失敗検出: A future edit removes a critical boundary while tests still pass.
  - 検証方法: `uv run pytest tests/test_init_update.py -k "issue_105"`
  - 関連 closure id: tc-005

#### step closure contract
- closure id:
  - tc-004, tc-005
- close 条件:
  - Updated targeted tests pass and cover asset inventory / parity / critical text contracts.
- 検証 evidence:
  - Targeted pytest output.
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta.
- 残リスク:
  - Full unittest suite may still be needed at final gate if targeted tests do not cover indirect installer impact.

#### step gate
- step reviewer gate:
  - reviewer: code-reviewer
  - review 範囲: managed skill manifest diff, harness expectation diff, and whether assertions are stable and sufficient.
  - pass 条件: review_status: pass
  - re-review rule: 指摘を修正し pass まで再実行。
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S03 files only.
  - no-op: 不可。Regression coverage is required.

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs / templates / README / workflow / skill / migration notes.
- 対応:
  - S01 and S02 are the planned docs/skill/workflow updates.
  - Inspect whether additional README / reference docs are needed. Current design expects no additional README change unless implementation discovers a user-facing index must mention `github-pr-merge-preparer`.
- doc update owner:
  - doc-writer when additional updates are required.
- spec/doc review:
  - reviewer: spec-reviewer
  - pass condition: docs impact resolved and no stale references.
- report evidence:
  - `report.md` S90 Docs Impact Resolution.

### S99 — final quality gate
- final QA:
  - reviewer: qa-reviewer
  - scope: closure coverage, targeted tests, `uv run pytest tests/cli_runtime/test_issue_lifecycle.py -k "issue_finish"` evidence or no-runtime-diff evidence, and whether full test suite or manual PR workflow simulation is needed.
- final code review:
  - reviewer: code-reviewer
  - scope: integrated diff, tests, scaffold asset impact, parity.
- final spec review:
  - reviewer: spec-reviewer
  - scope: requirement / design / plan / report / implementation / tests / docs alignment.
- final commit:
  - After all final gates pass, update final report ledger, create final commit, and record post-commit clean evidence externally.

## Final Exit Contract
- Required before reporting complete:
  - `./spec-dock/scripts/spec-dock validate` passes.
  - Required targeted tests pass.
  - `uv run pytest tests/cli_runtime/test_issue_lifecycle.py -k "issue_finish"` passes, or report records no-runtime-diff evidence and reviewer acceptance that issue_finish runtime semantics were not touched.
  - S01, S02, S03 step reviews pass.
  - S90 docs impact is resolved.
  - S99 qa-reviewer, code-reviewer, and spec-reviewer pass.
  - Each implementation step is committed or legitimately approved-no-op.
  - Final report ledger is updated.
  - Final commit is created and worktree is clean, except for intentional external delivery evidence.
- This issue does not require opening a PR for itself until the normal final delivery gate after implementation is complete.
