---
種別: 実装計画書（Issue）
ID: "iss-00211"
タイトル: "Epic Execution Coordinator Skill"
関連GitHub: ["#211"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
依存: ["requirement.md", "design.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00211 Epic Execution Coordinator Skill — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001 New skill availability
  - AC-002 Coordinator responsibility boundary
  - AC-003 Epic workflow reference
  - AC-004 Discoverability and routing
  - AC-005 Installer / update regression coverage
- EC:
  - EC-001 Active Issue already exists
  - EC-002 No ready Issue
  - EC-003 Multiple ready Issues
  - EC-004 Small Epic / no-op Epic
  - EC-005 PR preparation blocked
- 制約:
  - Provider-side installed assets are source of truth.
  - Dogfooding mirrors must match provider changes.
  - No runtime CLI command, dependency algorithm, GitHub mutation path, PR merge automation, or merge-ready self-claim.

## 依存関係から導く実装順序
- 依存関係の参照元:
  - `design.md` の責務境界、依存関係分析、Module Dependency Diagram、ディレクトリ / ファイル変更計画。
- 順序ルール:
  - New managed skill を tests / inventories と同じ slice で閉じる。
  - New skill が存在してから workflow / hub / prompt の routing surface を接続する。
  - Provider source と dogfooding mirror の parity を各 step で保つ。
- step 依存サマリー:
  - S01:
    - 依存: reviewer-pass 済み `requirement.md` / `design.md`。
    - unblock: S02 route references。
    - 対象: new provider skill, dogfooding mirror, managed skill inventories/tests。
  - S02:
    - 依存: S01 closure。
    - unblock: S03 integration verification。
    - 対象: `workflow_epic.md`, `spec-dock-hub`, `execute-epic.md`, route/content tests。
  - S03:
    - 依存: S02 closure。
    - unblock: S90 / S99。
    - 対象: verification only; repair only within S01/S02 file set。
  - S90:
    - 依存: S03 closure。
    - 対象: docs impact inspection and conditional docs update only。
  - S99:
    - 依存: S90 closure。
    - 対象: final QA / code / spec gates。

## ステップ一覧
- S01 Managed skill availability and coordinator contract
  - 観測可能な振る舞い: `spec-dock-epic-execution` が managed skill として install/update 対象になり、coordinator boundary を持つ。
  - 依存: requirement/design pass。
  - unblock: S02。
  - 対象ファイル: `tests/cli_runtime/harness.py`, `tests/unit/infra/test_init_update.py`, provider/mirror `spec-dock-epic-execution/SKILL.md`。
  - 閉じる要件: AC-001, AC-002, AC-005, EC-001..EC-005。
  - レビューゲート: code-reviewer for tests/inventory; spec-reviewer for skill prose。
- S02 Epic workflow and discovery route connection
  - 観測可能な振る舞い: workflow/hub/prompt から new skill に迷わず到達でき、旧 prompt contradiction が消える。
  - 依存: S01。
  - unblock: S03。
  - 対象ファイル: provider/mirror `workflow_epic.md`, `spec-dock-hub/SKILL.md`, `execute-epic.md`, route/content tests。
  - 閉じる要件: AC-003, AC-004, EC-004, EC-005。
  - レビューゲート: spec-reviewer; code-reviewer if tests change。
- S03 Targeted integration verification and bounded repair
  - 観測可能な振る舞い: managed asset / parity / route/content regression lane が通る。
  - 依存: S02。
  - unblock: S90。
  - 対象ファイル: no planned mutation; repair only in S01/S02 file set。
  - 閉じる要件: AC-001..AC-005。
  - レビューゲート: code-reviewer only if repair diff exists。
- S90 Docs impact resolution / docs refresh
  - 観測可能な振る舞い: conditional docs に直接矛盾が残っていないことを確認する。
  - 依存: S03。
  - unblock: S99。
  - 対象ファイル: conditional docs only if direct contradiction is found。
  - 閉じる要件: docs impact constraint。
  - レビューゲート: spec-reviewer for docs/spec alignment, including docs-impact-none / approved-no-op evidence。
- S99 Final quality gate
  - 観測可能な振る舞い: QA / code / spec final gates と closure coverage がそろう。
  - 依存: S90。
  - 対象ファイル: no planned mutation except bounded reviewer fixes。
  - 閉じる要件: all AC/EC。
  - レビューゲート: qa-reviewer, issue-wide code-reviewer, final spec-reviewer。

## 要件 ↔ ステップ対応
- AC-001 -> S01, S03, S99
- AC-002 -> S01, S03, S99
- AC-003 -> S02, S90, S99
- AC-004 -> S02, S03, S99
- AC-005 -> S01, S03, S99
- EC-001 -> S01
- EC-002 -> S01
- EC-003 -> S01
- EC-004 -> S01, S02
- EC-005 -> S01, S02
- Non-negotiable constraints -> S01, S02, S90, S99

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ | スライス | 種別 | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル | クロージャ証跡 |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | Managed skill availability | acceptance | AC-001, AC-005 | `spec-dock-epic-execution` is installed as a managed skill and included in expected inventories. | provider install_root, initialized/updated target, expected skill lists | missing managed asset | yes | red-required | report Test Contract Closure |
| tc-002 | S01 | Provider/dogfooding skill parity | acceptance | AC-001, constraints | provider skill and `.agents/` mirror exist and match. | two `SKILL.md` files, parity tests | provider/mirror drift | yes | red-required | report Test Contract Closure |
| tc-003 | S01 | Coordinator boundary | acceptance/negative | AC-002, EC-001..EC-005 | skill covers active Epic / active Issue / git / GitHub freshness bootstrap, no-ready blocked escalation, multiple-ready one-at-a-time selection by dependency / priority / risk, no-op Epic completion evidence, PR-preparer blocked-result evidence, existing workflow handoffs, and no PR merge / finish self-claim. | skill prose / content assertions | role absorption, stale context execution, active Issue bypass, no-ready silent failure, unsafe parallelism, no-op overwork, PR merge self-claim | yes | inspect-only or red-required | report Step Closure |
| tc-004 | S02 | Epic workflow reference | acceptance | AC-003 | `workflow_epic.md` connects planning handoff to Epic execution lifecycle and PR handoff. | provider/mirror `workflow_epic.md` | orphaned planning handoff | yes | inspect-only | report Test Contract Closure |
| tc-005 | S02 | Discovery routing | acceptance/negative | AC-004 | hub and `/execute-epic` route Epic execution to new skill; old no-skill contradiction is absent. | hub/prompt provider and mirror text | future agent ignores coordinator | yes | red-required or inspect-only | report Test Contract Closure |
| tc-006 | S03 | Targeted regression lane | regression | AC-001..AC-005 | targeted CLI runtime and installer/update tests pass. | pytest commands, `git diff --check`, stale prompt phrase check | inventory/package/parity regression | yes | covered-existing | report Closure Coverage |
| tc-007 | S90 | Docs impact boundary | invariant | constraints, AC-003, AC-004 | docs updates stay limited unless direct contradiction is found. | diff, `rg`, docs inspection | broad docs cleanup, workflow drift | yes | inspect-only | report Docs Impact evidence |
| tc-008 | S99 | Final quality gate | final gate | all AC/EC | QA/code/spec final reviewers pass and closure IDs are closed. | final diff, tests, report ledgers, reviewer outputs | incomplete closure | yes | manual-required | final gate ledger evidence |

## レビュー / QA ゲート方針
- RG1 step review:
  - Tests/scaffold/installer behavior -> `code-reviewer`
  - Shipped docs/skills/prompts/workflow text -> `spec-reviewer`
  - Mixed step -> both reviewer focuses unless implementation splits the step before work starts。
- QG1 final QA:
  - `qa-reviewer` checks AC/EC obligation coverage and missing high-value tests。
- CG1 final code review:
  - issue-wide `code-reviewer` checks integrated provider/mirror/tests/scaffold diff and forbidden runtime/GitHub mutation paths。
- SG1 final spec review:
  - final `spec-reviewer` checks requirement/design/plan/report/docs/skill alignment。

## 実行ルール（全ステップ共通）
- One step at a time. Do not begin the next implementation step until the current step has closure evidence, required verification, fresh reviewer pass, commit/no-op gate, and post-commit clean check。
- Main orchestrator owns canonical docs and report integration. Worker outputs are evidence until adopted。
- Shipped docs/skills/prompts should be delegated to `doc-writer`; tests/inventory/scaffold behavior should be delegated to `dev-coder`。
- If implementation needs files outside the step allowed paths or changes runtime command behavior, stop for plan amendment and fresh review。
- Observed evidence goes to `report.md`, not back into `plan.md`。

## 実装ステップ

### 実装ステップ S01 — Managed skill availability and coordinator contract
- 振る舞いの目標:
  - Future install/update targets expose `spec-dock-epic-execution` as a managed first-read skill, and the skill text defines the coordinator boundary required by AC-002 / EC-001..EC-005。
- design 参照:
  - `design.md` 責務境界、依存関係分析、ディレクトリ / ファイル変更計画。
- 依存:
  - reviewer-pass 済み requirement/design evidence。
- unblock:
  - S02 route references。
- 対象ファイル:
  - `tests/cli_runtime/harness.py`
  - `tests/unit/infra/test_init_update.py`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md`
  - `.agents/skills/spec-dock-epic-execution/SKILL.md`
- 計画済み契約:
  - scope:
    - Expected managed skill name and authoritative installed asset inventory entries。
    - Provider skill and dogfooding mirror。
    - Content/parity assertions for missing coordinator boundaries where practical。
  - テスト義務:
    - closure id: `tc-001`, `tc-002`, `tc-003`
    - coverage rationale: new shipped managed asset omission, mirror drift, responsibility absorption, active Issue bypass, PR merge self-claim are high-risk regressions。
  - Red / 代替証跡の要件:
    - red-required where practical for managed skill inventory and parity。
    - inspect-only acceptable for prose-only boundary clauses; prefer content assertions for active Epic / active Issue / git / GitHub freshness bootstrap, `deps check`, no-ready blocked escalation, multiple-ready one-at-a-time selection by dependency / priority / risk, no-op Epic completion evidence, `spec-dock-issue-planning`, `spec-dock-issue-execution`, `github-pr-merge-preparer`, PR-preparer blocked-result evidence, `issue start`, `issue finish`, and no PR merge self-claim。
  - Green 検証:
    - `uv run pytest tests/cli_runtime`
    - `uv run pytest tests/unit/infra/test_init_update.py -k "managed or issue_68 or issue_71 or dogfooding_agent_tooling_parity"`
    - Adjust the focused `-k` expression if live test names require it and record the reason in `report.md`。
  - Refactor / cleanup ガードレール:
    - Do not rewrite existing skills。
    - Do not introduce runtime command or dependency algorithm changes。
    - Do not update unrelated managed assets。
  - closure 証跡要件:
    - Step Contract Closure for S01。
    - Test Contract Closure for `tc-001`..`tc-003`。
    - Reviewer Gate Status。
    - Step Commit Gate。
  - report 証跡の記録先:
    - Implementation Delegation Gate, Delegated Worker Evidence, Test Contract Closure, Step Contract Closure, Reviewer Gate Status, Step Commit Gate。
  - amendment trigger:
    - Need for new runtime behavior, new GitHub mutation path, or responsibility change in existing issue planning/execution/PR skills。

#### 委任契約（delegation contract）
- 委任ロール:
  - `dev-coder` for tests/inventories。
  - `doc-writer` for skill prose。
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, `workflow_issue.md`, `workflow_epic.md`, existing related skills, target test files。
- 許可 paths:
  - S01 target files only。
- 禁止 changes:
  - Canonical docs except report evidence by main orchestrator。
  - Runtime CLI command implementation, dependency algorithm implementation, GitHub issue/PR mutation code。
  - Existing skill rewrites beyond planned references。
- 受け入れ条件:
  - `tc-001`, `tc-002`, `tc-003` close。
- 必須 tests または docs-only verification:
  - Focused pytest commands and direct inspection/parity for provider/mirror skill equality。
- reviewer focus:
  - `code-reviewer` for tests/inventory/scaffold behavior。
  - `spec-reviewer` for skill prose and responsibility boundary。
- 必須出力:
  - changed files, verification result, worker summary, unresolved risks, Ledger Note or `No material implementation decisions beyond the approved plan.`
- 停止条件:
  - Tests require files outside S01/S02 plan。
  - Skill cannot state coordinator semantics without changing `workflow_issue.md`。
  - Provider/mirror cannot be kept in parity。
  - Reviewer result is not fresh `pass`。

#### 具体テストケース一覧

- `tc-s01-001` acceptance: managed skill is installed and listed
  - 前提: expected managed skill lists do not contain `spec-dock-epic-execution`。
  - 操作: add the expected managed skill entry and run the focused CLI runtime managed-skill test path。
  - 期待結果: the test fails before the provider asset exists and passes after the provider asset and mirror are added。
  - 失敗検出: detects a new skill that exists in source but is not installed or not treated as managed。
  - 検証方法: `uv run pytest tests/cli_runtime` or the narrowest test containing `_assert_managed_skills_installed`。
  - 関連 closure id: `tc-001`

- `tc-s01-002` acceptance: provider and dogfooding skill paths stay in parity
  - 前提: provider install_root is source of truth and `.agents/` is checked-in mirror。
  - 操作: update asset map / inventory / parity assertions and compare provider and mirror skill files through existing dogfooding parity tests。
  - 期待結果: provider and mirror `SKILL.md` exist and match the same coordinator contract。
  - 失敗検出: detects missing mirror, stale mirror, or unregistered provider path。
  - 検証方法: `uv run pytest tests/unit/infra/test_init_update.py -k "dogfooding_agent_tooling_parity or issue_68 or issue_71"` or adjusted focused command recorded in `report.md`。
  - 関連 closure id: `tc-002`

- `tc-s01-003` boundary: coordinator locks the full Epic execution stop-condition surface
  - 前提: the new skill text is available in provider and mirror。
  - 操作: inspect or assert content for active Epic / active Issue / git / GitHub freshness bootstrap, `deps check`, no-ready blocked escalation, multiple-ready one-at-a-time selection by dependency / priority / risk, `issue start`, handoff to `spec-dock-issue-planning`, handoff to `spec-dock-issue-execution`, no-op Epic completion evidence, handoff to `github-pr-merge-preparer`, PR-preparer blocked-result evidence, return to `workflow_issue.md` for `issue finish`, and no PR merge self-claim。
  - 期待結果: the skill reads as a coordinator and covers all required stop conditions without replacing implementation, finish, or PR workflows。
  - 失敗検出: catches prose that skips freshness bootstrap, active Issue guard, no-ready blocked state, multiple-ready selection rule, no-op Epic path, PR-preparer blocked evidence, claims merge readiness, claims reviewer pass, or hides `issue finish` authority。
  - 検証方法: content assertions where practical, plus `spec-reviewer` docs/spec alignment。
  - 関連 closure id: `tc-003`

#### ステップ完了契約（step closure contract）
- closure id:
  - `tc-001`, `tc-002`, `tc-003`
- close 条件:
  - Both provider and dogfooding skill files exist。
  - Coordinator prose covers active Epic / active Issue / git / GitHub freshness bootstrap, no-ready blocked escalation, multiple-ready one-at-a-time selection by dependency / priority / risk, no-op Epic completion evidence, PR-preparer blocked-result evidence, issue planning/execution/PR/finish handoffs, and no self-claim of PR merge / finish authority。
  - Relevant tests pass or blocked reason is recorded。
  - Required reviewer gates are fresh pass。
- 検証 evidence:
  - Focused pytest / inspection / reviewer evidence。
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta if needed。
- 残リスク:
  - Low after parity/content assertions and `spec-reviewer` pass。

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: `code-reviewer` for tests/inventory; `spec-reviewer` for skill text。
  - pass 条件: `review_status: pass`。
  - re-review rule: fix findings and rerun fresh reviewer until pass。
- commit / no-op gate:
  - closure 状態: committed expected。
  - commit 範囲: S01 target files and report evidence only。
  - no-op: allowed only if exact existing evidence proves S01 already satisfied。

### 実装ステップ S02 — Epic workflow and discovery route connection
- 振る舞いの目標:
  - Future agents starting from Epic workflow docs, hub, or `/execute-epic` can discover and use `spec-dock-epic-execution` without confusing it with planning or issue execution。
- design 参照:
  - `design.md` Option B and D-002 `/execute-epic.md` conflict。
- 依存:
  - S01 Step Result Approval。
- unblock:
  - S03 integration verification。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
  - `spec-dock/docs/workflow_epic.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md`
  - `.agents/skills/spec-dock-hub/SKILL.md`
  - `src/spec_dock/assets/install_root/.codex/prompts/execute-epic.md`
  - `.codex/prompts/execute-epic.md`
  - `tests/unit/infra/test_init_update.py` only for route/content regression assertions。
- 計画済み契約:
  - scope:
    - Add short Epic execution lifecycle reference to `workflow_epic.md`。
    - Add hub route for Epic execution。
    - Update `/execute-epic` to use the new coordinator and remove the contradictory no-new-skill wording。
    - Preserve provider/mirror parity。
  - テスト義務:
    - closure id: `tc-004`, `tc-005`
    - coverage rationale: stale prompt/hub guidance can make future agents ignore the new coordinator。
  - Red / 代替証跡の要件:
    - red-required content assertion preferred for old `/execute-epic` phrase。
    - inspect-only acceptable for concise workflow prose when parity tests and `spec-reviewer` cover it。
  - Green 検証:
    - `uv run pytest tests/unit/infra/test_init_update.py -k "execute_epic or workflow_epic or dogfooding_agent_tooling_parity"`
    - `rg -n "Do not create a new skill for this workflow" src/spec_dock/assets/install_root/.codex/prompts/execute-epic.md .codex/prompts/execute-epic.md` returns no matches after update。
    - `rg -n "spec-dock-epic-execution|Epic execution" src/spec_dock/assets/spec_dock/docs/workflow_epic.md spec-dock/docs/workflow_epic.md src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md .agents/skills/spec-dock-hub/SKILL.md src/spec_dock/assets/install_root/.codex/prompts/execute-epic.md .codex/prompts/execute-epic.md`
  - Refactor / cleanup ガードレール:
    - Keep skill prose first-read and docs concise。
    - Do not rewrite `workflow_issue.md` or `github-pr-merge-preparer`。
    - Do not broaden to unrelated docs cleanup。
  - report 証跡の記録先:
    - Implementation Delegation Gate, Delegated Worker Evidence, Test Contract Closure, Step Contract Closure, Reviewer Gate Status, Step Commit Gate。
  - amendment trigger:
    - Route update requires runtime command behavior。
    - Docs require changing Issue finish / PR merge-preparer semantics。
    - Direct contradiction in other workflow docs changes accepted scope。

#### 委任契約（delegation contract）
- 委任ロール:
  - `doc-writer` for workflow docs, hub skill, and prompt。
  - `dev-coder` for test/content assertion updates。
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, `workflow_epic.md`, `workflow_issue.md`, `workflow_spec_authoring.md`, current hub and prompt files。
- 許可 paths:
  - S02 target files only。
- 禁止 changes:
  - Unrelated docs cleanup, PR merge automation wording, `issue finish` authority changes, runtime command or GitHub mutation code。
- 受け入れ条件:
  - `tc-004` and `tc-005` close。
- 必須 tests または docs-only verification:
  - Targeted pytest/content assertions and `rg` checks above。
- reviewer focus:
  - `spec-reviewer` for workflow/prompt/skill wording。
  - `code-reviewer` only if tests change。
- 必須出力:
  - changed files, verification result, docs impact note, unresolved risks, Ledger Note。
- 停止条件:
  - Route cannot be represented without broad docs rewrite。
  - Accepted Option B no longer matches implementation need。
  - Prompt/hub update requires changing slash command semantics。

#### 具体テストケース一覧

- `tc-s02-001` acceptance: `workflow_epic.md` references Epic execution lifecycle
  - 前提: existing `workflow_epic.md` says execution coordinator behavior is outside the planning handoff section。
  - 操作: add a short reference section that points to `spec-dock-epic-execution`, Epic completion gate, and PR merge-preparer handoff。
  - 期待結果: future agents can see how Issue 210 planning handoff connects to Issue 211 execution coordinator without duplicating Issue execution policy。
  - 失敗検出: catches a workflow doc that leaves the new skill orphaned or duplicates downstream issue execution semantics。
  - 検証方法: docs inspection, parity test, and `spec-reviewer`。
  - 関連 closure id: `tc-004`

- `tc-s02-002` negative: `/execute-epic` no longer contradicts the new skill
  - 前提: current prompt contains "Do not create a new skill for this workflow"。
  - 操作: update provider and mirror prompts to route Epic execution through `spec-dock-epic-execution`。
  - 期待結果: the old contradictory phrase is absent and the new skill route is present。
  - 失敗検出: catches stale prompt guidance that would make agents ignore the new coordinator。
  - 検証方法: `rg` no-match for the old phrase and targeted content assertion if added。
  - 関連 closure id: `tc-005`

- `tc-s02-003` acceptance: hub route distinguishes planning, execution, and issue execution
  - 前提: hub lists `spec-dock-epic-planning` and `spec-dock-issue-execution` but not the new Epic execution coordinator。
  - 操作: add a route entry for `spec-dock-epic-execution` while preserving existing planning and issue execution routes。
  - 期待結果: Epic execution requests route to the new skill; Epic requirement/design/plan authoring still routes to `spec-dock-epic-planning`。
  - 失敗検出: catches route ambiguity or replacement of existing leaf skill ownership。
  - 検証方法: content assertion or inspection plus `spec-reviewer`。
  - 関連 closure id: `tc-005`

#### ステップ完了契約（step closure contract）
- closure id:
  - `tc-004`, `tc-005`
- close 条件:
  - Old `/execute-epic` contradiction is absent。
  - Provider/mirror docs/prompt/skill files are aligned。
  - Required reviewer gates are fresh pass。
- 検証 evidence:
  - Targeted pytest / `rg` / inspection / reviewer evidence。
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta if needed。
- 残リスク:
  - Conditional docs ambiguity is addressed in S90。

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: `spec-reviewer`; `code-reviewer` if tests changed。
  - pass 条件: `review_status: pass`。
- commit / no-op gate:
  - closure 状態: committed expected。
  - commit 範囲: S02 target files and report evidence only。

### 実装ステップ S03 — Targeted integration verification and bounded repair
- 振る舞いの目標:
  - Integrated S01/S02 changes pass the targeted regression lane for managed assets, dogfooding parity, and route/content assertions。
- 依存:
  - S02 Step Result Approval。
- unblock:
  - S90。
- 対象ファイル:
  - no planned mutation。
  - repair only in S01/S02 target files if verification failure is caused by planned changes。
- 計画済み契約:
  - scope:
    - Run targeted verification and record evidence。
    - Delegate bounded repair only for failures directly caused by S01/S02 changes。
  - テスト義務:
    - closure id: `tc-006`
    - coverage rationale: cross-surface packaging/parity failures may be missed by per-step checks。
  - Red / 代替証跡の要件:
    - covered-existing; S03 is integration check, not new behavior implementation。
  - Green 検証:
    - `uv run pytest tests/cli_runtime`
    - `uv run pytest tests/unit/infra/test_init_update.py`
    - `git diff --check`
    - `rg -n "Do not create a new skill for this workflow" src/spec_dock/assets/install_root/.codex/prompts/execute-epic.md .codex/prompts/execute-epic.md` returns no matches。
  - Refactor / cleanup ガードレール:
    - No opportunistic cleanup。
    - Repair only planned files and only failures caused by this issue。
  - report 証跡の記録先:
    - Test Contract Closure for `tc-006`, Closure Coverage, Reviewer Gate Status if repair diff exists, Step Commit Gate or approved-no-op。
  - amendment trigger:
    - Verification failure requires files outside design file plan。
    - Integration failure exposes missing requirement/design decision。

#### 委任契約（delegation contract）
- 委任ロール:
  - N/A for read-only verification。
  - `dev-coder` for bounded repair if failures are caused by planned implementation。
- 入力 docs:
  - `plan.md`, S01/S02 report evidence, failing command output。
- 許可 paths:
  - none for read-only verification。
  - S01/S02 target files only if repair is needed。
- 禁止 changes:
  - Broad test rewrites, unrelated runtime/docs cleanup, skipping failed checks without blocker evidence。
- 受け入れ条件:
  - `tc-006` closes with pass or blocked reason and next action。
- 必須 tests または docs-only verification:
  - Commands listed in Green verification。
- reviewer focus:
  - No reviewer needed for no-op read-only pass beyond final gates。
  - `code-reviewer` if repair diff exists。
- 必須出力:
  - command results, repair summary if any, unresolved risks, Ledger Note。
- 停止条件:
  - Tests cannot run due environment/tooling。
  - Failures are unrelated or require design amendment。
  - Repair would exceed S01/S02 allowed paths。

#### 具体テストケース一覧

- `tc-s03-001` regression: targeted CLI runtime lane passes
  - 前提: S01/S02 changes are present。
  - 操作: run `uv run pytest tests/cli_runtime`。
  - 期待結果: CLI runtime tests pass with the new managed skill list。
  - 失敗検出: catches install/update behavior that omits or mishandles managed skills。
  - 検証方法: command result in `report.md`。
  - 関連 closure id: `tc-006`

- `tc-s03-002` regression: install/update parity lane passes
  - 前提: S01/S02 changes are present。
  - 操作: run `uv run pytest tests/unit/infra/test_init_update.py`。
  - 期待結果: authoritative inventory, dogfooding parity, content, and package-data tests pass。
  - 失敗検出: catches provider/mirror drift, unregistered files, or stale prompt guidance。
  - 検証方法: command result in `report.md`。
  - 関連 closure id: `tc-006`

- `tc-s03-003` formatting/content guard: diff and stale prompt phrase checks pass
  - 前提: S01/S02 changes are present。
  - 操作: run `git diff --check` and `rg` no-match for the old `/execute-epic` contradiction。
  - 期待結果: no whitespace errors and no old contradiction remains。
  - 失敗検出: catches formatting churn and stale route guidance。
  - 検証方法: command results in `report.md`。
  - 関連 closure id: `tc-006`

#### ステップ完了契約（step closure contract）
- closure id:
  - `tc-006`
- close 条件:
  - Targeted commands pass or blocked/incomplete evidence is recorded。
  - Repair diff, if any, receives required reviewer pass and commit gate。
- 検証 evidence:
  - command results and reviewer evidence if repair occurs。
- report evidence:
  - Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate。
- 残リスク:
  - Full `uv run pytest` may be deferred only with explicit reason and final/CI evidence plan。

#### ステップゲート（step gate）
- step reviewer gate:
  - none for approved-no-op verification pass。
  - `code-reviewer` if repair diff exists。
- commit / no-op gate:
  - closure 状態: approved-no-op if no repair diff; committed if repair diff exists。

### ドキュメント影響の解消ステップ S90（docs impact resolution / docs refresh）
- 振る舞いの目標:
  - Confirm all docs/skill/prompt impact from Issue 211 is complete and no direct contradiction remains outside the planned surfaces。
- design 参照:
  - `design.md` Docs / prompt discovery boundary and conditional docs list。
- 依存:
  - S03 closure。
- unblock:
  - S99 final quality gate。
- 対象ファイル:
  - no planned mutation beyond S01/S02 surfaces。
  - conditional only if direct contradiction is found:
    - `spec-dock/docs/workflow_issue.md`
    - `spec-dock/docs/workflow_spec_authoring.md`
    - `spec-dock/docs/authoring/decision-routing.md`
    - `spec-dock/docs/reference_github.md`
    - provider-side counterparts under `src/spec_dock/assets/spec_dock/docs/`
- 計画済み契約:
  - scope:
    - Inspect docs impact and update only direct contradictions。
    - Record docs-impact-none as explicit evidence when no conditional update is needed。
  - テスト義務:
    - closure id: `tc-007`
    - coverage rationale: conditional workflow docs could contain stale direct contradictions that undermine new skill routing。
  - Red / 代替証跡の要件:
    - inspect-only。
  - Green 検証:
    - `git diff --name-status`
    - `rg -n "spec-dock-epic-execution|Epic execution|execute-epic|issue finish|github-pr-merge-preparer" spec-dock/docs src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/install_root/.agents/skills src/spec_dock/assets/install_root/.codex/prompts .agents/skills .codex/prompts`
    - Targeted docs inspection recorded in `report.md`。
  - Refactor / cleanup ガードレール:
    - Do not perform broad docs cleanup。
    - Do not add examples or policy rewrites not needed for Issue 211。
  - report 証跡の記録先:
    - Docs Impact Resolution section, Test Contract Closure for `tc-007`, Reviewer Gate Status, Step Commit Gate / approved-no-op evidence。
  - amendment trigger:
    - Conditional docs require a new durable policy decision beyond Option B。
    - Docs inspection finds requirement/design gap or requires files outside conditional list。

#### 委任契約（delegation contract）
- 委任ロール:
  - N/A for read-only docs impact inspection。
  - `doc-writer` only if conditional docs updates are required。
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, S01/S02/S03 report evidence, docs/prompt/skill diff。
- 許可 paths:
  - none for read-only inspection。
  - Conditional docs list only when a direct contradiction is found。
- 禁止 changes:
  - Broad docs cleanup。
  - Examples or policy rewrites outside Issue 211。
  - Implementation/test/provider asset changes outside conditional docs update。
- 受け入れ条件:
  - `tc-007` closes。
  - Docs-impact-none is recorded with inspection evidence, or conditional docs update receives review and commit gate。
- 必須 tests または docs-only verification:
  - `rg` / diff inspection commands above。
  - Fresh `spec-reviewer` docs/spec alignment result even for docs-impact-none; if docs changed, review the diff and updated docs。
- reviewer focus:
  - `spec-reviewer` for docs/spec alignment。
- 必須出力:
  - docs impact decision, changed files or approved-no-op evidence, verification result, unresolved risks。
- 停止条件:
  - Docs gap changes accepted requirement/design scope。
  - Update would exceed conditional docs list。
  - Reviewer result is not fresh `pass`。

#### 具体テストケース一覧

- `tc-s90-001` inspect-only: conditional docs have no direct contradiction
  - 前提: S01/S02 route changes are present。
  - 操作: inspect docs/prompts for Epic execution, issue finish, PR-preparer, and old no-skill wording。
  - 期待結果: no unplanned direct contradiction remains; if one is found, it is updated within the conditional docs boundary and reviewed。
  - 失敗検出: catches stale workflow policy that conflicts with the new skill。
  - 検証方法: `rg` output, docs inspection, and fresh `spec-reviewer` docs/spec alignment result in `report.md`。
  - 関連 closure id: `tc-007`

#### ステップ完了契約（step closure contract）
- closure id:
  - `tc-007`
- close 条件:
  - Docs impact is resolved by conditional updates or approved-no-op with inspection evidence。
  - Fresh `spec-reviewer` docs/spec alignment result is recorded for docs-impact-none or docs changes。
- 検証 evidence:
  - `rg` / diff inspection output and reviewer verdict。
- report evidence:
  - Docs Impact Resolution, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate。
- 残リスク:
  - none expected after reviewer pass。

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: `spec-reviewer`。
  - pass 条件: `review_status: pass`。
- commit / no-op gate:
  - closure 状態: committed if docs changed; approved-no-op if inspection finds no updates required。
  - no-op の場合: record exact inspected docs, commands, and reviewer verdict。

### 最終品質ゲート S99（final quality gate）
- 振る舞いの目標:
  - Confirm the entire issue satisfies requirement/design/plan/report alignment and all closure IDs are closed before downstream handoff。
- design 参照:
  - `design.md` test strategy, risks, and final handoff boundaries。
- 依存:
  - S90 closure。
- unblock:
  - issue execution completion / PR delivery handoff after implementation。
- 対象ファイル:
  - no planned mutation except bounded reviewer-requested fixes。
- 計画済み契約:
  - scope:
    - Final QA, issue-wide code review, final spec review。
    - Final report ledger closure。
    - Confirm PR delivery / merge-preparation handoff remains governed by `workflow_issue.md` and `github-pr-merge-preparer`。
  - テスト義務:
    - closure id: `tc-008`
    - coverage rationale: final gate catches cross-step omissions, missing closure evidence, and unauthorized authority claims。
  - Red / 代替証跡の要件:
    - manual-required final reviewer evidence。
  - Green 検証:
    - all required closure IDs closed in `report.md`。
    - targeted S03 tests recorded。
    - any extra tests required by `qa-reviewer`。
    - `git diff --check`。
  - Refactor / cleanup ガードレール:
    - Do not use final review as substitute for missing step review。
    - Do not merge PR, close GitHub issue, or claim `issue finish` before `workflow_issue.md` completion gates。
  - report 証跡の記録先:
    - Final QA Gate, Final Code Review Gate, Final Spec Review Gate, Closure Coverage, Final Commit / external delivery evidence destination。
  - amendment trigger:
    - Final reviewer finds missing requirement/design coverage。
    - Final reviewer requires a new closure ID not covered by current plan。

#### 委任契約（delegation contract）
- 委任ロール:
  - `qa-reviewer`
  - issue-wide `code-reviewer`
  - final `spec-reviewer`
  - `dev-coder` or `doc-writer` only for bounded reviewer-requested fixes matching changed file type。
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, `report.md`, final diff, test evidence, reviewer history。
- 許可 paths:
  - no planned mutation。
  - Bounded fixes only in files already in S01/S02/S90 scope unless reviewer finding requires plan amendment。
- 禁止 changes:
  - Using final review as substitute for missing step review。
  - PR merge, GitHub issue close, or premature `issue finish`。
  - Broad cleanup outside reviewed scope。
- 受け入れ条件:
  - `tc-008` closes。
  - Final `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer` are fresh pass。
- 必須 tests または docs-only verification:
  - Final reviewer outputs, closure coverage inspection, targeted tests recorded, `git diff --check`。
- reviewer focus:
  - `qa-reviewer`: test sufficiency and integration test need。
  - `code-reviewer`: integrated diff, structure, regression risk, no forbidden runtime/GitHub mutation。
  - `spec-reviewer`: requirement/design/plan/report/docs consistency and no unauthorized self-claim。
- 必須出力:
  - final reviewer verdicts, final risk status, final report ledger state, final commit/external evidence destination。
- 停止条件:
  - Any final reviewer is not fresh pass。
  - Any required closure ID unresolved。
  - Missing report evidence。
  - Uncommitted implementation step diff remains without commit/no-op gate。

#### 具体テストケース一覧

- `tc-s99-001` final QA: test sufficiency reviewed
  - 前提: S01/S02/S03/S90 are closed。
  - 操作: run `qa-reviewer` against requirement/design/plan/report and test evidence。
  - 期待結果: QA reviewer passes or identifies missing tests that are fixed and re-reviewed。
  - 失敗検出: catches under-tested managed asset or route behavior。
  - 検証方法: final QA gate evidence in `report.md`。
  - 関連 closure id: `tc-008`

- `tc-s99-002` final code review: integrated diff reviewed
  - 前提: final diff includes provider/mirror/tests/docs changes。
  - 操作: run issue-wide `code-reviewer`。
  - 期待結果: code reviewer passes integrated scaffold/test changes and confirms no forbidden runtime/GitHub mutation path。
  - 失敗検出: catches structural/test regressions or accidental implementation drift。
  - 検証方法: final code review gate evidence in `report.md`。
  - 関連 closure id: `tc-008`

- `tc-s99-003` final spec review: requirements and docs align
  - 前提: final plan/report/docs/skills/prompts are ready。
  - 操作: run final `spec-reviewer`。
  - 期待結果: spec reviewer passes AC/EC traceability and docs/spec alignment。
  - 失敗検出: catches missing AC/EC coverage, stale delegated evidence, or unauthorized self-claim。
  - 検証方法: final spec review gate evidence in `report.md`。
  - 関連 closure id: `tc-008`

#### ステップ完了契約（step closure contract）
- closure id:
  - `tc-008`
- close 条件:
  - Final QA/code/spec reviewers pass。
  - Final report ledger records closure coverage and reviewer gate evidence。
  - Final commit/external evidence destination is recorded by main orchestrator。
- 検証 evidence:
  - final reviewer verdicts, targeted test evidence, `git diff --check`, closure coverage inspection。
- report evidence:
  - Final QA Gate, Final Code Review Gate, Final Spec Review Gate, Closure Coverage, Final Commit / external delivery evidence。
- 残リスク:
  - none acceptable for issue completion; unresolved final reviewer findings block completion。

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`。
  - pass 条件: all final reviewers fresh `review_status: pass`。
- commit / no-op gate:
  - closure 状態: final commit after all implementation steps and report ledger are closed。
  - final commit must not catch up uncommitted implementation step work。

## Final Exit Contract
- All AC/EC rows in the Requirement -> Step Mapping are closed。
- Every required closure ID in the Spec-Locked Closure Index is pass or valid approved-no-op in `report.md`。
- Every implementation step is committed or valid approved-no-op。
- S90 docs impact is resolved。
- S99 final QA/code/spec reviewers are fresh pass。
- Targeted tests and `git diff --check` are recorded。
- Final report ledger is updated before final commit。
- PR delivery and merge-preparation evidence are handled through `github-pr-merge-preparer` before `issue finish`, per `workflow_issue.md`。
- `issue finish` is not claimed by this plan or any delegated worker。
