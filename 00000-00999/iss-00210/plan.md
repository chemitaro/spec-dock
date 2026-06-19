---
種別: 実装計画書（Issue）
ID: "iss-00210"
タイトル: "Epic Planning System Architect Draft Cycles"
関連GitHub: ["#210"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
依存: ["requirement.md", "design.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00210 Epic Planning System Architect Draft Cycles — 実装計画（実行契約 / Execution Contract）

> `plan.md` は planned contract であり、実行結果、逸脱、検証結果、reviewer verdict、commit/no-op evidence は `report.md` に記録する。

## この計画で満たす要件ID
- AC:
  - AC-001: `spec-dock-epic-planning` first-read に conditional `system-architect` draft cycle を追加する。
  - AC-002: delegated draft adoption に EAL、formal baseline/diff-guard、fresh reviewer gate を要求する。
  - AC-003: `workflow_epic.md` に Epic planning completion / handoff contract を定義する。
  - AC-004: cross-issue draft package semantics を定義する。
  - AC-005: issue-local draft requirement/design artifact の作成境界を定義する。
  - AC-006: Issue 211 は独立 Issue として Issue 210 outputs を参照できるだけにする。
  - AC-007: dependency mutation は command-first であることを workflow text に残す。
  - AC-008: provider-side source と dogfooding mirror の検証証跡を残す。
- EC:
  - EC-001: trivial Epic / delegation skipped の skip reason を記録できる。
  - EC-002: delegated role unavailable / denied / unsupported の fallback を記録できる。
  - EC-003: requirement/design gap を前段 authoring phase へ戻せる。
  - EC-004: Issue 211 scope creep を防ぐ。
- 制約:
  - Provider-side assets are source of truth.
  - Dogfooding mirror is validation target.
  - Canonical docs stay main-orchestrator-owned during authoring; implementation file edits are delegated.

## 依存関係から導く実装順序
- 依存関係の参照元:
  - `design.md` の responsibility boundary、interface contract、directory / file change plan。
- 順序ルール:
  - First-read skill surface を先に固定し、その参照先として `workflow_epic.md` を更新する。
  - `workflow_spec_authoring.md` は既存 policy で足りない discoverability gap が確認された場合だけ触る。
  - Provider-side update 後に dogfooding mirror を検証する。
- step 依存サマリー:
  - S01:
    - 依存: reviewed requirement/design。
    - unblock: S02。
    - 対象ファイル: provider-side `spec-dock-epic-planning/SKILL.md`。
  - S02:
    - 依存: S01 の routing wording。
    - unblock: S03。
    - 対象ファイル: provider-side `workflow_epic.md`、必要時のみ `workflow_spec_authoring.md`。
  - S03:
    - 依存: S01/S02。
    - unblock: S90/S99。
    - 対象ファイル: dogfooding mirror skill/docs、`report.md` evidence。

## ステップ一覧
- S01:
  - 観測可能な振る舞い: Agent が Epic planning skill を first-read した時点で、非自明 Epic では `system-architect` draft cycle、skip reason、formal diff guard、fresh reviewer gate が必要だと判断できる。
  - 依存: reviewed `requirement.md` / `design.md`。
  - unblock: S02。
  - 対象ファイル: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`。
  - 閉じる要件: AC-001, AC-002, EC-001, EC-002, EC-003。
  - レビューゲート: step `spec-reviewer` pass。
- S02:
  - 観測可能な振る舞い: Epic workflow docs が planning completion / handoff package / cross-issue draft package / issue-local draft creation command / command-first dependency contract を説明する。
  - 依存: S01。
  - unblock: S03。
  - 対象ファイル: `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`; optional `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`。
  - 閉じる要件: AC-003, AC-004, AC-005, AC-006, AC-007, EC-004。
  - レビューゲート: step `spec-reviewer` pass。
- S03:
  - 観測可能な振る舞い: Provider-side changes are reflected or intentionally compared against dogfooding mirror, and `report.md` records the validation route and evidence.
  - 依存: S01, S02。
  - unblock: S90, S99。
  - 対象ファイル: `.agents/skills/spec-dock-epic-planning/SKILL.md`; `spec-dock/docs/workflow_epic.md`; optional `spec-dock/docs/workflow_spec_authoring.md`; `report.md`。
  - 閉じる要件: AC-008。
  - レビューゲート: step `spec-reviewer` pass。

## 要件 ↔ ステップ対応
- AC-001 -> S01
- AC-002 -> S01
- AC-003 -> S02
- AC-004 -> S02
- AC-005 -> S02
- AC-006 -> S02
- AC-007 -> S02
- AC-008 -> S03
- EC-001 -> S01
- EC-002 -> S01
- EC-003 -> S01
- EC-004 -> S02

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ（step） | スライス（slice） | 種別（type） | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル（evidence level） | クロージャ証跡（closure evidence） |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | skill first-read spine | acceptance | AC-001, AC-002, EC-001, EC-002, EC-003 | Skill names conditional `system-architect` draft cycle, skip/fallback/gap return, formal baseline/diff-guard, EAL, and fresh `spec-reviewer` gate | Provider-side skill text after S01 | Delegated draft used without required guardrails | yes | inspect-only | `report.md` Step/Test/Closure evidence + targeted `rg` |
| tc-002 | S02 | Epic handoff contract | acceptance | AC-003, AC-004, AC-005, AC-006, AC-007, EC-004 | `workflow_epic.md` defines planning completion/handoff, cross-issue package, issue-local draft commands, command-first dependency mutation, and Issue 211 independence | Provider-side workflow doc text after S02 | Issue 211 scope creep or ad hoc issue doc writes | yes | inspect-only | `report.md` Step/Test/Closure evidence + targeted `rg` |
| tc-003 | S03 | dogfooding mirror validation | acceptance | AC-008 | Changed provider-side surfaces are mirrored or explicitly validated against dogfooding copies, with no silent optional mirror validation | Provider and mirror skill/docs after S03 | Provider-only wording drift | yes | manual-required | `report.md` validation command / inspection evidence |

## レビュー / QA ゲート方針
- RG1 step review:
  - 実施タイミング: S01, S02, S03 の各 step closure 前。
  - reviewer: `spec-reviewer`。
  - pass 条件: `review_status: pass`。
- QG1 final QA:
  - reviewer: `qa-reviewer`。
  - 範囲: closure coverage、docs-only verification sufficiency、mirror validation sufficiency。
- CRG1 final code review:
  - reviewer: `code-reviewer`。
  - 範囲: issue-wide diff. Docs/skill-only change でも shipped asset boundary、source-of-truth、unintended code/test churn を確認する。
- SG1 final spec review:
  - reviewer: `spec-reviewer`。
  - 範囲: requirement/design/plan/report/implementation evidence alignment。

## 実行ルール（全ステップ共通）
- Each implementation step is one review scope and one commit boundary unless a plan amendment and fresh review approve otherwise.
- Observed results go to `report.md`, not back into `plan.md`.
- Implementation edits are delegated. Shipped docs/skills/workflow text changes use `doc-writer` with bounded allowed paths.
- If an implementation step discovers a requirement/design gap, stop and return to the prior authoring phase.
- If formal delegated authoring diff guard cannot pass, record fallback in `report.md` and do not adopt the delegated draft as authority.

## 実装ステップ

### 実装ステップ S01 — Epic planning skill first-read spine
- 振る舞いの目標（behavior goal）:
  - Agent が skill だけを読んでも non-trivial Epic planning の draft cycle と adoption guardrails を理解できる。
- design 参照:
  - Skill first-read contract; Delegated draft evidence contract。
- 依存:
  - reviewed `requirement.md`; reviewed `design.md`。
- unblock:
  - S02。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
- 計画済み契約（planned contract）:
  - scope:
    - Add concise first-read wording for conditional `system-architect` use, skip reason, unavailable fallback, requirement/design gap return, formal baseline/diff-guard, EAL, and fresh review gate.
  - テスト義務（test obligation）:
    - closure id: `tc-001`
    - coverage rationale: Skill wording is the first operational surface; inspection must catch missing guardrails that would allow unreviewed delegated evidence.
  - Red / 代替証跡の要件:
    - docs-only / inspect-only:
      - Code test is not required because this step changes agent-facing shipped text only.
      - Alternative evidence path: targeted `rg` for `system-architect`, `baseline-status`, `diff-guard`, `Evidence Adoption Ledger`, `spec-reviewer`, `skip reason`, `fallback`.
  - 実装範囲（implementation scope）:
    - allowed paths:
      - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
    - forbidden changes:
      - Runtime code, tests, GitHub state, issue canonical docs other than report evidence, dogfooding mirror before S03.
  - Green 検証:
    - Targeted `rg` and manual first-read inspection.
  - Refactor / cleanup ガードレール:
    - Keep skill concise; do not copy full workflow docs into the skill.
  - closure 証跡要件:
    - Step Contract Closure: S01 row.
    - Test Contract Closure: `tc-001` row.
    - Closure Coverage: `tc-001` row.
  - report 証跡の記録先:
    - `report.md` session log, TDD alternative evidence, closure tables, Delegated Worker Evidence, Reviewer Gate Status.
  - amendment trigger（plan amendment が必要になる契機）:
    - Need to change runtime command semantics, require all Epics to delegate, or grant canonical write authority.

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - `doc-writer`
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`
  - `.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
- 許可 paths:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
- 禁止 changes:
  - Any canonical issue doc, runtime code, tests, dogfooding mirror, Git operations, GitHub operations.
- 受け入れ条件:
  - `tc-001` close condition is met.
- 必須 tests または docs-only verification:
  - Targeted `rg` and manual inspection.
- reviewer focus:
  - `spec-reviewer`: docs/spec alignment and no scope creep.
- 必須出力（output required）:
  - changed files, summary, verification results, unresolved risks, report evidence notes.
- 停止条件（stop conditions）:
  - Skill wording requires workflow semantics not present in reviewed design, or allowed path is insufficient.

#### 具体テストケース一覧
- `tc-s01-001` inspect-only: Skill names the delegated draft guardrails.
  - 前提: S01 provider-side skill text is updated.
  - 操作: Run targeted `rg` for `system-architect`, `baseline-status`, `diff-guard`, `Evidence Adoption Ledger`, `spec-reviewer`, `skip reason`, `fallback`.
  - 期待結果: All key terms appear in the skill with concise routing/obligation wording.
  - 失敗検出: Agent-facing first-read text omits formal diff guard, skip/fallback, or reviewer pass.
  - 検証方法: command output plus manual inspection.
  - 関連 closure id: `tc-001`

#### ステップ完了契約（step closure contract）
- closure id:
  - `tc-001`
- close 条件:
  - Provider-side skill satisfies S01 acceptance and step `spec-reviewer` passes.
- 検証 evidence:
  - Targeted `rg`; manual first-read inspection; reviewer pass.
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status.
- 残リスク:
  - None if reviewer passes; otherwise amend/fix and re-review.

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: `spec-reviewer`
  - review 範囲: S01 changed file plus requirement/design mapping.
  - pass 条件: `review_status: pass`
  - re-review rule: fix findings and rerun until pass.
- commit / no-op gate:
  - closure 状態: committed after reviewer pass.
  - commit 範囲: S01 file and report evidence only.

### 実装ステップ S02 — Epic planning completion and handoff workflow contract
- 振る舞いの目標（behavior goal）:
  - Epic workflow docs define what “planning complete” means and what handoff evidence Issue 211 may reference.
- design 参照:
  - Epic workflow handoff contract; Issue-local draft creation contract; Issue 211 reference contract。
- 依存:
  - S01。
- unblock:
  - S03。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
  - optional: `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
- 計画済み契約（planned contract）:
  - scope:
    - Add planning completion/handoff, cross-issue draft package, issue-local draft artifact commands, command-first dependency mutation, and Issue 211 independence wording.
  - テスト義務（test obligation）:
    - closure id: `tc-002`
    - coverage rationale: The handoff contract prevents downstream Issue 211 from re-defining planning completion or absorbing Issue 210 execution scope.
  - Red / 代替証跡の要件:
    - docs-only / inspect-only:
      - Code test is not required for text-only workflow contract.
      - Alternative evidence path: targeted `rg` for `planning completion`, `handoff`, `cross-issue draft`, `draft-requirement`, `draft-design`, `--issue`, `Issue 211`, dependency command wording.
  - 実装範囲（implementation scope）:
    - allowed paths:
      - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
      - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md` only if discoverability gap is confirmed.
    - forbidden changes:
      - New runtime schema, issue execution coordinator wording, canonical issue doc edits, dogfooding mirror before S03.
  - Green 検証:
    - Targeted `rg` and manual workflow inspection.
  - Refactor / cleanup ガードレール:
    - Avoid broad template or workflow redesign.
  - closure 証跡要件:
    - Step Contract Closure: S02 row.
    - Test Contract Closure: `tc-002` row.
    - Closure Coverage: `tc-002` row.
  - report 証跡の記録先:
    - `report.md` session log, TDD alternative evidence, closure tables, Delegated Worker Evidence, Reviewer Gate Status.
  - amendment trigger（plan amendment が必要になる契機）:
    - Need to modify runtime `new doc` command behavior or make Issue 211 a subtask/completion condition.

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - `doc-writer`
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
- 許可 paths:
  - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md` only if needed.
- 禁止 changes:
  - Runtime code, tests, dogfooding mirror, GitHub state, canonical issue docs other than report evidence.
- 受け入れ条件:
  - `tc-002` close condition is met.
- 必須 tests または docs-only verification:
  - Targeted `rg` and manual inspection.
- reviewer focus:
  - `spec-reviewer`: workflow/spec alignment, no Issue 211 scope creep.
- 必須出力（output required）:
  - changed files, summary, verification results, unresolved risks, report evidence notes.
- 停止条件（stop conditions）:
  - Required wording conflicts with reviewed design, or runtime command contract is absent.

#### 具体テストケース一覧
- `tc-s02-001` inspect-only: Epic workflow defines handoff package and issue-local draft commands.
  - 前提: S02 provider-side workflow docs are updated.
  - 操作: Run targeted `rg` for `handoff`, `cross-issue draft`, `draft-requirement`, `draft-design`, `--issue`, `Issue 211`, dependency command wording.
  - 期待結果: `workflow_epic.md` names planning completion evidence, issue-local draft commands, command-first dependency handling, and Issue 211 independence.
  - 失敗検出: Handoff remains implicit, issue-local drafts can be ad hoc writes, or Issue 211 becomes an execution dependency.
  - 検証方法: command output plus manual inspection.
  - 関連 closure id: `tc-002`

#### ステップ完了契約（step closure contract）
- closure id:
  - `tc-002`
- close 条件:
  - Provider-side workflow docs satisfy S02 acceptance and step `spec-reviewer` passes.
- 検証 evidence:
  - Targeted `rg`; manual workflow inspection; reviewer pass.
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status.
- 残リスク:
  - None if reviewer passes; otherwise amend/fix and re-review.

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: `spec-reviewer`
  - review 範囲: S02 changed files plus requirement/design mapping.
  - pass 条件: `review_status: pass`
  - re-review rule: fix findings and rerun until pass.
- commit / no-op gate:
  - closure 状態: committed after reviewer pass.
  - commit 範囲: S02 files and report evidence only.

### 実装ステップ S03 — Dogfooding mirror validation and evidence recording
- 振る舞いの目標（behavior goal）:
  - Provider-side updates are validated against the local dogfooding surface and AC-008 is closed with observed evidence.
- design 参照:
  - Directory / file change plan; test strategy; AC-008 mapping。
- 依存:
  - S01, S02。
- unblock:
  - S90, S99。
- 対象ファイル:
  - `.agents/skills/spec-dock-epic-planning/SKILL.md`
  - `spec-dock/docs/workflow_epic.md`
  - optional: `spec-dock/docs/workflow_spec_authoring.md`
  - `report.md`
- 計画済み契約（planned contract）:
  - scope:
    - Refresh or targeted-compare dogfooding mirror for changed provider-side skill/docs, and record exact evidence.
  - テスト義務（test obligation）:
    - closure id: `tc-003`
    - coverage rationale: Parent Epic requires provider/mirror validation and requirement AC-008 forbids treating mirror validation as optional.
  - Red / 代替証跡の要件:
    - manual-required:
      - Full automation may be inappropriate if `spec-dock update .` would produce unrelated scaffold churn.
      - Alternative evidence path: targeted provider-vs-mirror diff/inspection, `./spec-dock/scripts/spec-dock validate`, `./spec-dock/scripts/spec-dock sync`, or explicit no-run rationale for any skipped command.
  - 実装範囲（implementation scope）:
    - allowed paths:
      - `.agents/skills/spec-dock-epic-planning/SKILL.md`
      - `spec-dock/docs/workflow_epic.md`
      - `spec-dock/docs/workflow_spec_authoring.md` only if provider optional file changed.
      - Issue `report.md` evidence tables.
    - forbidden changes:
      - Runtime code, provider source beyond S01/S02, unrelated dogfooding data.
  - Green 検証:
    - Provider/mirror targeted comparison and validation commands or documented no-run rationale.
  - Refactor / cleanup ガードレール:
    - Do not normalize unrelated mirror drift.
  - closure 証跡要件:
    - Step Contract Closure: S03 row.
    - Test Contract Closure: `tc-003` row.
    - Closure Coverage: `tc-003` row.
  - report 証跡の記録先:
    - `report.md` session log, validation commands, closure tables, Docs Impact Resolution.
  - amendment trigger（plan amendment が必要になる契機）:
    - Mirror update reveals broad scaffold drift outside changed surfaces.

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - `doc-writer`
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`
  - S01/S02 provider changed files
  - dogfooding mirror target files
- 許可 paths:
  - `.agents/skills/spec-dock-epic-planning/SKILL.md`
  - `spec-dock/docs/workflow_epic.md`
  - `spec-dock/docs/workflow_spec_authoring.md` only if needed
  - Issue `report.md` evidence rows
- 禁止 changes:
  - Runtime code, tests, unrelated `spec-dock/` issue data, GitHub state.
- 受け入れ条件:
  - `tc-003` close condition is met.
- 必須 tests または docs-only verification:
  - Targeted provider-vs-mirror inspection plus `validate` / `sync` where practical, or no-run rationale.
- reviewer focus:
  - `spec-reviewer`: mirror evidence satisfies AC-008 and does not hide drift.
- 必須出力（output required）:
  - changed mirror files, validation commands/results, no-run rationale if any, unresolved risks, report evidence notes.
- 停止条件（stop conditions）:
  - Mirror update requires unrelated changes, validation command fails for reasons that may affect this issue, or provider/mirror mismatch cannot be explained.

#### 具体テストケース一覧
- `tc-s03-001` manual-required: Dogfooding mirror validation is evidenced.
  - 前提: S01/S02 provider-side changes are complete.
  - 操作: Compare or refresh changed mirror files and run `./spec-dock/scripts/spec-dock validate` / `./spec-dock/scripts/spec-dock sync` where practical.
  - 期待結果: Mirror reflects or is explicitly validated against provider changes, and report records command/inspection evidence.
  - 失敗検出: Provider-only changes are accepted without mirror evidence or skipped commands lack rationale.
  - 検証方法: command output, targeted diff/inspection, and `report.md` evidence.
  - 関連 closure id: `tc-003`

#### ステップ完了契約（step closure contract）
- closure id:
  - `tc-003`
- close 条件:
  - Mirror validation evidence satisfies AC-008 and step `spec-reviewer` passes.
- 検証 evidence:
  - Targeted comparison / update evidence; validation command results or no-run rationale; reviewer pass.
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Docs Impact Resolution.
- 残リスク:
  - Any unrelated mirror drift must be recorded as out of scope or routed to follow-up.

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: `spec-reviewer`
  - review 範囲: S03 mirror evidence and changed mirror files.
  - pass 条件: `review_status: pass`
  - re-review rule: fix findings and rerun until pass.
- commit / no-op gate:
  - closure 状態: committed after reviewer pass.
  - commit 範囲: S03 files and report evidence only.

### ドキュメント影響の解消ステップ S90（docs impact resolution / docs refresh）
- 対象:
  - Shipped skill/docs and dogfooding mirror docs are the primary issue impact.
- 対応:
  - Confirm S01/S02/S03 closed all docs impact. No README or migration note is planned unless implementation discovers user-facing install/update behavior changed.
- doc update owner:
  - `doc-writer` for shipped docs/skills.
- spec/doc review:
  - reviewer: `spec-reviewer`
  - pass 条件: docs are aligned with requirement/design/plan/report and no mandatory docs impact remains unresolved.

### 最終品質ゲートステップ S99（final quality gate）
- branch diff 範囲:
  - Issue 210 requirement/design/plan/report/discussions plus implementation changes from S01/S02/S03.
- 必須 validation:
  - Step closure coverage for `tc-001` through `tc-003`.
  - `./spec-dock/scripts/spec-dock validate` and `./spec-dock/scripts/spec-dock sync` if practical after mirror updates; otherwise explicit no-run rationale.
  - `git diff --check`.
- final QA gate:
  - reviewer: `qa-reviewer`
  - 範囲: Issue obligation coverage, test/inspection sufficiency, mirror validation sufficiency.
  - pass 条件: reviewer pass.
- final code review ゲート:
  - reviewer: `code-reviewer`
  - 範囲: issue-wide integrated diff, source-of-truth boundaries, unintended code/test churn.
  - pass 条件: `review_status: pass`.
- final spec review ゲート:
  - reviewer: `spec-reviewer`
  - 範囲: requirement / design / plan / report / implementation / tests / docs alignment.
  - pass 条件: reviewer pass.
- final commit gate:
  - commit 範囲: reviewed Issue 210 implementation and evidence.
  - final report ledger: all open decision/adoption entries resolved or non-blocking.
  - post-commit external evidence destination: `report.md` commit gate row.

## 計画 authoring fallback evidence
- `implementation-planner` direct-write delegated plan draft was not used.
- Reason:
  - `./spec-dock/scripts/spec-dock delegated-authoring diff-guard --role implementation-planner --scope iss-00210 --baseline-status /private/tmp/iss-00210-plan-baseline-status.txt` returned `dirty_baseline_discussion` because current-session clarification/design discussion files already existed in the target scope `discussions/`.
- Manual authoring path:
  - Main orchestrator authored this canonical `plan.md` from reviewed `requirement.md`, reviewed `design.md`, `phase_plan_issue.md`, `authoring/issue-plan.md`, and the observed diff-guard blocker.
  - This fallback does not weaken the required fresh `spec-reviewer` plan gate.

## 未確定事項
- Blocking question:
  - none.
- Non-blocking implementation discovery:
  - Whether `workflow_spec_authoring.md` needs an additional cross-reference remains optional and must be justified by implementation inspection before edit.

## 最終完了条件
- AC/EC 達成:
  - AC-001 through AC-008 and EC-001 through EC-004 are closed by S01/S02/S03 evidence.
- docs 影響解決:
  - S90 completed with `spec-reviewer` pass.
- 全 implementation step 完了:
  - S01/S02/S03 committed after reviewer pass, or approved-no-op where explicitly justified.
- final quality gate pass:
  - `qa-reviewer`: pass
  - `code-reviewer`: pass
  - `spec-reviewer`: pass
  - validation commands / no-run rationale recorded in `report.md`.
