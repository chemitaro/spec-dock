---
種別: 実装計画書（Issue）
ID: "iss-00186"
タイトル: "Harden Issue Execution Step Gates"
関連GitHub: ["#186"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-16"
依存: ["requirement.md", "design.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00186 Harden Issue Execution Step Gates — 実装計画

## この計画で満たす要件ID

- AC:
  - AC-001 First-read single-step gate
  - AC-002 Delegated mutation gate
  - AC-003 Reviewer fail and follow-up gate
  - AC-004 Completion terminology boundary
  - AC-005 Context-surface ownership compliance
  - AC-006 Provider and dogfooding validation
  - AC-007 Evidence adoption and planning readiness
- EC:
  - EC-001 Multiple-step bundling attempt
  - EC-002 Sub-agent unavailable / denied / host conflict
  - EC-003 Skill-text-only / docs-only implementation step
  - EC-004 Final commit catch-up misconception
  - EC-005 Alignment check finds broad template / prompt drift
- 制約:
  - `1 implementation step = 1 review scope = 1 commit`
  - Provider source first, dogfooding mirror validation second
  - Skill = compact workflow spine, docs = detail semantics, templates = scaffold / evidence slots
  - Empirical harness、runtime enforcement、broad template/prompt rewrite は対象外

## 依存関係から導く実装順序

- 依存関係の参照元:
  - `design.md` の dependency order、surface responsibility、file change plan。
- 順序ルール:
  - first-read skill surface を先に固定する。
  - skill が参照する exact semantics を workflow docs に固定する。
  - 最終 wording が固まった後に test assertions を更新する。
  - core contract が固定された後に alignment check を行う。
  - provider changes が確定してから mirror / sync / validate を行う。
- step 依存サマリー:
  - S01: provider skill spine。依存: approved requirement/design/plan。unblock: S02/S03。
  - S02: workflow exact semantics。依存: S01 intent。unblock: S03/S04。
  - S03: provider tests/assertions。依存: S01/S02 final wording。unblock: S90/S99。
  - S04: alignment check and small severe fixes/follow-up decisions。依存: S01/S02。unblock: S90/S99。
  - S90: docs impact, mirror, sync, validate。依存: S01-S04。
  - S99: final quality gate。依存: S01-S90。

## ステップ一覧

| Step | 観測可能な振る舞い | 依存 | 対象ファイル | 閉じる要件 | レビューゲート |
|---|---|---|---|---|---|
| S01 | Skill first-read gate spine が single-step loop を明示する | approved requirement/design/plan | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md` | AC-001, AC-002, AC-003, EC-001, EC-003 | `spec-reviewer` |
| S02 | `workflow_issue.md` が Step Result Approval / exception / final commit semantics を明示する | S01 wording intent | `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` | AC-004, EC-002, EC-004 | `spec-reviewer` |
| S03 | Tests/assertions が new contract と existing fragments を守る | S01, S02 | `tests/unit/infra/test_init_update.py` | AC-001-AC-004 | `code-reviewer` |
| S04 | Adjacent surfaces の severe contradiction がない、または小修正/follow-up が記録される | S01, S02 | alignment targets only if needed | AC-005, EC-005 | `spec-reviewer` |
| S90 | Provider/mirror validation と docs impact が閉じる | S01-S04 | mirror files if required; report evidence | AC-006 | `spec-reviewer` |
| S99 | issue-wide final gates が閉じる | S01-S90 | integrated diff / report ledger | AC-007 | `qa-reviewer`, `code-reviewer`, `spec-reviewer` |

## 要件 ↔ ステップ対応

- AC-001 -> S01, S03
- AC-002 -> S01, S02
- AC-003 -> S01, S02, S03
- AC-004 -> S02, S03
- AC-005 -> S04, S99
- AC-006 -> S90
- AC-007 -> S99
- EC-001 -> S01, S03
- EC-002 -> S02, S03
- EC-003 -> S01, S04
- EC-004 -> S02, S99
- EC-005 -> S04, S99

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| ID | Step | Slice | Type | Spec link | Locked expectation | Observable input/state | Bug class guarded | Required | Evidence level | Closure evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | skill first-read gate | acceptance | AC-001, EC-001 | Skill says one current implementation step closes before next step begins. | Provider skill text and installed mirror text. | Multi-step batching from first-read ambiguity. | yes | inspect-only + structural assertion | report Step/Test Contract Closure |
| tc-002 | S01 | delegated mutation gate | acceptance | AC-002, AC-003, EC-002 | Skill routes normal file mutation to delegated worker and requires Parent Implementation Exception for direct parent fixes. | Provider skill text. | Parent direct implementation or direct reviewer-fail fixes. | yes | inspect-only + structural assertion | report Step/Test Contract Closure |
| tc-003 | S02 | workflow exact semantics | acceptance | AC-004, EC-002, EC-004 | Workflow defines Step Result Approval and non-pass/final-commit boundaries. | Provider workflow docs. | Treating degraded/waived/final commit as gate pass. | yes | inspect-only + structural assertion | report Step/Test Contract Closure |
| tc-004 | S03 | provider assertions | regression | AC-001-AC-004 | Tests assert new critical fragments and preserve existing required fragments. | `tests/unit/infra/test_init_update.py` and targeted pytest. | Silent loss of shipped wording during future updates. | yes | red-required or covered-existing | report Test Contract Closure |
| tc-005 | S04 | alignment triage | acceptance | AC-005, EC-005 | Alignment targets contain no severe contradiction or record small fix/follow-up decision. | `authoring/issue-plan.md`, templates, prompt inspection. | Template/prompt normalizes N/A delegation or bundled steps as success. | yes | inspect-only | report Decision Ledger / Closure Coverage |
| tc-006 | S90 | provider/mirror validation | acceptance | AC-006 | Provider source and dogfooding mirror are intentionally aligned, and SpecDock validate passes. | Provider files, mirror files, validation command. | Mirror-only edit or shipped source drift. | yes | manual-required + command evidence | report Docs Impact / Closure Coverage |
| tc-007 | S99 | final quality gate | acceptance | AC-007 | Final QA, code review, spec review, report ledger, final commit/no-op evidence all close. | Whole issue diff and report ledger. | Final review replacing step gates; incomplete completion claim. | yes | manual-required | report Final Quality Gate |

## レビュー / QA ゲート方針

- RG1 step review:
  - 実施タイミング: 各 implementation step の commit 前。
  - reviewer:
    - docs-only / skill-text-only / template-only: `spec-reviewer`
    - tests / assertion changes: `code-reviewer`
  - pass 条件: fresh `review_status: pass`
  - non-pass: failed / unavailable / denied / waived / provisional は pass ではない。
- QG1 final QA:
  - reviewer: `qa-reviewer`
  - 範囲: Issue 全体の obligation coverage、missing high-value tests、integration test 要否。
- CG1 final code review:
  - reviewer: `code-reviewer`
  - 範囲: issue-wide integrated diff、test assertions、regression risk。
- SG1 final spec review:
  - reviewer: `spec-reviewer`
  - 範囲: requirement / design / plan / report / implementation / docs alignment。

## 実行ルール（全ステップ共通）

- 各 implementation step は順番に実行する。複数 step の同時実装、同時 review、同時 commit はしない。
- 各 implementation step は 1 review scope / 1 commit boundary とする。
- File mutation は step の `delegation contract` に従い `dev-coder` / `doc-writer` へ委任する。
- 親 agent direct implementation は事前に `Parent Implementation Exception` を report に記録した場合だけ許可する。
- Worker output には `Ledger Note` または `No material implementation decisions beyond the approved plan.` を含める。
- Observed result は `report.md` に記録し、`plan.md` へ実行結果を戻さない。
- Plan amendment trigger に該当した場合は、該当 phase へ戻り fresh `spec-reviewer` pass まで execution を止める。

## 実装ステップ

### 実装ステップ S01 — Skill Spine Update

- 振る舞いの目標:
  - Provider skill を読んだ時点で、single current step と next-step unlock 条件が見える。
- design 参照:
  - `design.md` Surface Responsibility / File Change Plan / Sequence Delta。
- 依存:
  - approved requirement/design/plan。
- unblock:
  - S02, S03。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
- 計画済み契約:
  - scope:
    - Compact first-read gate spine を skill の上部に追加する。
    - Full workflow policy / field schema / completion matrix は追加しない。
  - テスト義務:
    - closure id: `tc-001`, `tc-002`
    - coverage rationale: first-read ambiguity と parent direct implementation drift を防ぐ。
  - Red / 代替証跡の要件:
    - docs-only / inspect-only:
      - code test は S03 で追加するため、この step では targeted inspection を pre-implementation / alternative evidence とする。
  - 実装範囲:
    - allowed paths: provider skill only。
    - forbidden changes: workflow docs, tests, templates, prompts, runtime code, canonical docs。
  - Green 検証:
    - targeted inspection for single current step, required verification, fresh reviewer pass, Step Commit Gate, post-commit clean, next-step unlock, delegation routing, Parent Implementation Exception, non-pass availability wording。
  - report 証跡の記録先:
    - TDD / alternative evidence、Step Contract Closure、Test Contract Closure、Closure Coverage、Implementation Delegation Gate、Delegated Worker Evidence、Reviewer Gate Status、Step Commit Gate。
  - amendment trigger:
    - skill に full lifecycle policy、field schema、completion matrix を入れる必要が出た場合。

#### 委任契約

- delegated role: `doc-writer`
- input docs:
  - `requirement.md`, `design.md`, `plan.md`, `report.md`
  - provider skill
  - `workflow_issue.md`, `phase_plan_issue.md`, `authoring/issue-plan.md`
- allowed paths:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
- forbidden changes:
  - allowed paths 以外すべて。
- acceptance criteria:
  - `tc-001`, `tc-002`
- required verification:
  - targeted inspection; S03 assertion follow-up。
- reviewer focus:
  - `spec-reviewer` docs/spec alignment。
- output required:
  - changed files, wording summary, inspection result, Ledger Note / no-material-decision, unresolved risks。
- stop conditions:
  - allowed path 外変更、full policy copy、workflow semantics 変更が必要な場合。

#### 具体テストケース一覧

- `tc-s01-001` acceptance: skill states the step loop before detailed routing.
  - 前提: provider skill lacks a top-loaded loop.
  - 操作: inspect provider skill after `doc-writer` change.
  - 期待結果: skill says current step closure requires required verification, fresh step reviewer pass, Step Commit Gate, and post-commit clean check before next-step unlock.
  - 失敗検出: skill still permits multi-step bundling by omission.
  - 検証方法: targeted inspection and later S03 assertion.
  - 関連 closure id: `tc-001`
- `tc-s01-002` acceptance: skill preserves delegated mutation boundary.
  - 前提: issue steps may mutate shipped docs/skills/tests.
  - 操作: inspect routing and reviewer-fail wording.
  - 期待結果: runtime/tests/scaffold route to `dev-coder`, shipped docs/templates/skills/workflow text route to `doc-writer`, and parent direct fixes require Parent Implementation Exception.
  - 失敗検出: parent direct implementation or direct reviewer-fail fixes are normalized.
  - 検証方法: targeted inspection and later S03 preservation assertion.
  - 関連 closure id: `tc-002`

#### ステップ完了契約

- closure id: `tc-001`, `tc-002`
- close 条件:
  - provider skill has compact gate spine and preserves existing required routing fragments.
- 検証 evidence:
  - targeted inspection output and `spec-reviewer` pass.
- report evidence:
  - Step Contract Closure / Test Contract Closure / Closure Coverage / Step Commit Gate。
- 残リスク:
  - S03 assertion までは future drift protection は未完了。

#### ステップゲート

- step reviewer gate:
  - reviewer: `spec-reviewer`
  - review 範囲: S01 provider skill diff only
  - pass 条件: `review_status: pass`
  - re-review rule: fail 指摘は `doc-writer` follow-up 後に fresh re-review。
- commit / no-op gate:
  - closure 状態: committed / approved-no-op
  - commit 範囲: S01 provider skill change only
  - no-op: 差分不要理由、確認対象、diff-clean command、read-only evidence を report に記録。

### 実装ステップ S02 — Workflow Exact Semantics

- 振る舞いの目標:
  - `workflow_issue.md` が Step Result Approval、non-pass states、final commit boundary を detail semantics として所有する。
- 依存:
  - S01 wording intent。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- 計画済み契約:
  - scope:
    - Minimal definitions / clarifications for Step Result Approval, `approved-local-execution`, `degraded mode`, `waived`, unavailable / denied / host conflict, reviewer fail, final commit boundary。
  - テスト義務:
    - closure id: `tc-003`
  - Red / 代替証跡:
    - docs-only / inspect-only; S03 structural assertion follows。
  - allowed paths:
    - provider workflow doc only。
  - forbidden changes:
    - skill, tests, templates, prompts, runtime code, canonical docs。
  - Green 検証:
    - targeted inspection for Step Result Approval and final commit / non-pass semantics。
  - report 証跡:
    - Decision Ledger if terminology tradeoff is material; Step/Test Contract Closure; Closure Coverage; Reviewer Gate Status; Step Commit Gate。
  - amendment trigger:
    - durable ownership model、runtime enforcement、template authority、agent permissions の変更が必要になった場合。

#### 委任契約

- delegated role: `doc-writer`
- input docs:
  - `requirement.md`, `design.md`, `plan.md`, current provider skill wording from S01, provider workflow docs。
- allowed paths:
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- forbidden changes:
  - allowed paths 以外すべて。
- acceptance criteria:
  - `tc-003`
- required verification:
  - targeted inspection; S03 assertion follow-up。
- reviewer focus:
  - `spec-reviewer` docs/spec alignment。
- output required:
  - changed files, wording summary, inspection result, Ledger Note / no-material-decision, unresolved risks。
- stop conditions:
  - broad terminology rename、workflow policy rewrite、templates/prompts edits が必要な場合。

#### 具体テストケース一覧

- `tc-s02-001` acceptance: Step Result Approval unlocks the next step only after required gates.
  - 前提: workflow docs define per-step review/commit but exact unlock semantics can be missed.
  - 操作: inspect provider workflow docs after update.
  - 期待結果: Step Result Approval requires current step closure, required verification, fresh reviewer pass, Step Commit Gate, and post-commit clean check.
  - 失敗検出: proceeding to next step after verification without reviewer/commit/clean evidence.
  - 検証方法: targeted inspection and later S03 assertion.
  - 関連 closure id: `tc-003`
- `tc-s02-002` negative: final commit is not a catch-up implementation commit.
  - 前提: earlier step diff remains uncommitted before S99.
  - 操作: inspect completion/final commit wording.
  - 期待結果: workflow says final commit cannot bundle earlier uncommitted implementation step changes.
  - 失敗検出: missing per-step commit being rescued at final gate.
  - 検証方法: targeted inspection and later S03 assertion.
  - 関連 closure id: `tc-003`
- `tc-s02-003` negative: unavailable/denied/host conflict/waiver are not reviewer passes.
  - 前提: reviewer/delegation availability is mixed with completion evidence.
  - 操作: inspect reviewer/delegation state semantics.
  - 期待結果: fresh `passed` is the required reviewer gate pass; waiver is explicit risk acceptance, and degraded mode is not success/readiness.
  - 失敗検出: degraded success or automatic parent direct implementation.
  - 検証方法: targeted inspection and later S03 assertion.
  - 関連 closure id: `tc-003`

#### ステップ完了契約

- closure id: `tc-003`
- close 条件:
  - provider workflow docs define exact semantics without moving full policy into skill。
- 検証 evidence:
  - targeted inspection and `spec-reviewer` pass。
- report evidence:
  - Step/Test Contract Closure、Closure Coverage、Step Commit Gate。

#### ステップゲート

- step reviewer gate:
  - reviewer: `spec-reviewer`
  - review 範囲: S02 provider workflow doc diff only
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed / approved-no-op
  - commit 範囲: S02 provider workflow doc change only

### 実装ステップ S03 — Tests / Assertion Update

- 振る舞いの目標:
  - Provider tests protect the new skill/workflow contract while preserving existing fragments.
- 依存:
  - S01, S02 final wording。
- 対象ファイル:
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - scope:
    - Add focused assertions for new gate phrases and retain existing fragment assertions。
  - テスト義務:
    - closure id: `tc-004`
  - Red / 代替証跡:
    - red-required when feasible: assertion should fail before S01/S02 wording and pass after.
    - covered-existing acceptable only when existing assertion already detects the contract.
  - allowed paths:
    - `tests/unit/infra/test_init_update.py`
  - forbidden changes:
    - provider docs/skill, templates, prompts, runtime code, canonical docs。
  - Green 検証:
    - narrowest pytest covering changed assertions; fallback `uv run pytest tests/unit/infra/test_init_update.py`。
  - report 証跡:
    - Red/Green/Refactor evidence, Discovered Tests, Step/Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate。
  - amendment trigger:
    - runtime behavior change、broad fixture rewrite、empirical harness が必要になった場合。

#### 委任契約

- delegated role: `dev-coder`
- input docs:
  - `requirement.md`, `design.md`, `plan.md`, S01/S02 final wording, existing tests。
- allowed paths:
  - `tests/unit/infra/test_init_update.py`
- forbidden changes:
  - allowed paths 以外すべて。
- acceptance criteria:
  - `tc-004`
- required verification:
  - focused pytest。
- reviewer focus:
  - `code-reviewer`
- output required:
  - changed files, test command/result, existing failures not caused by S03, Ledger Note / no-material-decision。
- stop conditions:
  - long paragraph assertions、unrelated refactor、新依存が必要な場合。

#### 具体テストケース一覧

- `tc-s03-001` regression: provider issue-execution skill contains the new gate spine fragments.
  - 前提: S01 final wording exists.
  - 操作: run focused provider asset assertion test.
  - 期待結果: test fails without S01 wording and passes with S01 wording.
  - 失敗検出: future removal of single-step gate, fresh reviewer pass, Step Commit Gate, or post-commit clean wording.
  - 検証方法: `uv run pytest tests/unit/infra/test_init_update.py` or narrower selected test.
  - 関連 closure id: `tc-004`
- `tc-s03-002` regression: provider workflow docs contain exact semantics fragments.
  - 前提: S02 final wording exists.
  - 操作: run focused workflow doc assertion.
  - 期待結果: test covers Step Result Approval, unavailable/denied/host conflict/waiver non-pass semantics, and final commit not catch-up.
  - 失敗検出: future drift from Option B semantics.
  - 検証方法: focused pytest.
  - 関連 closure id: `tc-004`
- `tc-s03-003` preservation: existing asserted fragments remain valid.
  - 前提: existing tests assert source-of-truth, concise reminder, `dev-coder`, `doc-writer`, bounded delegated follow-up, and Parent Implementation Exception.
  - 操作: run the same focused assertions.
  - 期待結果: existing fragments still pass.
  - 失敗検出: accidental wording regression while adding new assertions.
  - 検証方法: focused pytest.
  - 関連 closure id: `tc-004`

#### ステップ完了契約

- closure id: `tc-004`
- close 条件:
  - tests assert new critical fragments and preserve existing fragments.
- 検証 evidence:
  - focused pytest result.
- report evidence:
  - Red/Green evidence, Test Contract Closure, Closure Coverage, Step Commit Gate。

#### ステップゲート

- step reviewer gate:
  - reviewer: `code-reviewer`
  - review 範囲: S03 tests diff only
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed / approved-no-op
  - commit 範囲: S03 tests assertion change only

### 実装ステップ S04 — Alignment Check and Small Severe Fixes / Follow-Up Decisions

- 振る舞いの目標:
  - Adjacent surfaces do not severely contradict the hardened gate, without broad scope expansion.
- 依存:
  - S01, S02。
- 対象ファイル:
  - Inspect:
    - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
    - `src/spec_dock/assets/spec_dock/templates/issue/plan.md`
    - `src/spec_dock/assets/spec_dock/templates/issue/report.md`
    - `src/spec_dock/assets/install_root/.codex/prompts/execute-issue.md`
  - Allowed only if severe fix is required:
    - same list above。
- 計画済み契約:
  - scope:
    - Identify severe contradictions against Option B.
    - Apply only small, directly gate-related wording fixes, or record follow-up / deferred decision.
  - テスト義務:
    - closure id: `tc-005`
  - Red / 代替証跡:
    - inspect-only。
  - forbidden changes:
    - broad template rewrite、empirical harness、runtime enforcement、agent definitions、canonical docs。
  - Green 検証:
    - inspection notes; targeted pytest only if changed shipped asset has relevant assertion.
  - report 証跡:
    - Decision Ledger, Step/Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate。
  - amendment trigger:
    - Broad drift that cannot be fixed as one small, directly gate-related wording change.

#### 委任契約

- delegated role:
  - `doc-writer` for any file mutation.
  - Read-only no-op inspection may be coordinated by main orchestrator and recorded as approved-no-op if no mutation is required.
- input docs:
  - `requirement.md`, `design.md`, `plan.md`, S01/S02 wording, alignment target files。
- allowed paths:
  - listed alignment targets only if severe fix is required.
- forbidden changes:
  - allowed paths 以外すべて。
- acceptance criteria:
  - `tc-005`
- required verification:
  - targeted inspection and, if changed, relevant pytest/validation.
- reviewer focus:
  - `spec-reviewer`; if tests change, split step or add `code-reviewer` review.
- output required:
  - changed files or approved-no-op rationale, severe contradiction inventory, follow-up recommendation, Ledger Note / no-material-decision。
- stop conditions:
  - Template authority redesign、prompt redesign、empirical harness、multi-file broad cleanup が必要な場合。

#### 具体テストケース一覧

- `tc-s04-001` inspect-only: plan authoring docs do not undermine step-local delegation/test gates.
  - 前提: `authoring/issue-plan.md` owns field semantics.
  - 操作: inspect for contradictory delegation contract, concrete test cases, reviewer fail, and commit/no-op gate semantics.
  - 期待結果: no severe contradiction, or small fix/follow-up decision recorded.
  - 失敗検出: global-only test plans or missing step-local gate semantics.
  - 検証方法: targeted inspection, and pytest if an asserted provider asset is changed.
  - 関連 closure id: `tc-005`
- `tc-s04-002` inspect-only: issue templates remain scaffold/evidence slots, not compliance authorities.
  - 前提: templates are alignment targets only.
  - 操作: inspect issue `plan.md` and `report.md` templates for N/A delegation or multi-step bundled logs being normalized as success.
  - 期待結果: no severe contradiction, or small fix/follow-up decision recorded.
  - 失敗検出: templates invite bypassing per-step delegation/review/commit gates.
  - 検証方法: targeted inspection, and pytest if template assertions change.
  - 関連 closure id: `tc-005`
- `tc-s04-003` inspect-only: `/execute-issue` prompt aligns with the skill/workflow gate.
  - 前提: prompt is an entry alignment surface, not a separate source of truth.
  - 操作: inspect prompt for readiness, step-local cases, per-step review/commit, report evidence, and final gate wording.
  - 期待結果: no severe contradiction, or small fix/follow-up decision recorded.
  - 失敗検出: prompt guidance allows implementation before executable plan or final review replacing step review.
  - 検証方法: targeted inspection.
  - 関連 closure id: `tc-005`

#### ステップ完了契約

- closure id: `tc-005`
- close 条件:
  - severe contradictions are absent, fixed in small scope, or recorded as follow-up/deferred with non-blocking rationale.
- 検証 evidence:
  - inspection notes, changed-file diff if any, reviewer pass.
- report evidence:
  - Decision Ledger, Step/Test Contract Closure, Closure Coverage, Step Commit Gate。

#### ステップゲート

- step reviewer gate:
  - reviewer: `spec-reviewer`
  - review 範囲: alignment check / small docs-only fixes only
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed / approved-no-op
  - commit 範囲: small severe alignment fixes only, or no-op evidence.

## ドキュメント影響の解消ステップ S90

- 振る舞いの目標:
  - Provider source と dogfooding mirror の関係、sync / validate / docs impact が閉じている。
- 依存:
  - S01-S04。
- 対象:
  - `.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `spec-dock/docs/workflow_issue.md`
  - Any mirror/projection touched by sync/update.
- 対応:
  - Provider/mirror parity or intentional difference を確認する。
  - `./spec-dock/scripts/spec-dock validate` を実行する。
  - `./spec-dock/scripts/spec-dock sync` は provider/mirror update or projection refresh が必要な場合に実行し、不要なら no-op rationale を report に残す。
  - Targeted inspection of mirror skill and workflow docs。
- doc update owner:
  - `doc-writer` when mirror/docs updates are required。
- spec/doc review:
  - reviewer: `spec-reviewer`
  - pass 条件: docs / mirror evidence が requirement / design / plan と整合し、未解決の docs impact が残っていない。
- commit / no-op gate:
  - closure 状態: committed / approved-no-op
  - commit 範囲:
    - mirror / projection refresh files generated or intentionally updated during S90.
    - S90 report evidence updates.
  - no-op 条件:
    - sync / update / mirror edit が不要であることを targeted inspection and command evidence で確認し、report に no-op rationale を記録する。
  - post-commit clean:
    - S90 が file mutation を行った場合、S90 commit 後に `git status --short` が clean であることを Step Commit Gate に記録する。
    - S90 が approved-no-op の場合、no-op checked contracts / files と diff-clean command を Step Commit Gate に記録する。
- closure id:
  - `tc-006`
- concrete evidence:
  - `tc-s90-001` manual-required: mirror validation and SpecDock validate.
    - 前提: provider changes from S01-S04 are complete.
    - 操作: inspect/update mirror, run validate, run sync if required, then close S90 commit/no-op gate.
    - 期待結果: provider/mirror relation is intentional and validate passes.
    - 失敗検出: mirror-only edit, stale installed surface, invalid SpecDock state.
    - 検証方法: command output and targeted inspection recorded in report.
    - 関連 closure id: `tc-006`

## 最終品質ゲートステップ S99

- branch diff 範囲:
  - All changes from S01-S90 plus canonical planning/report evidence.
- 必須 validation:
  - `./spec-dock/scripts/spec-dock validate`
  - relevant pytest from S03
  - clean status after final commit gate
- final QA gate:
  - reviewer: `qa-reviewer`
  - 範囲: Issue 全体の obligation coverage と integration test 要否
  - pass 条件: reviewer pass
- final code review gate:
  - reviewer: `code-reviewer`
  - 範囲: issue-wide integrated diff、test assertions、regression risk
  - pass 条件: `review_status: pass`
- final spec review gate:
  - reviewer: `spec-reviewer`
  - 範囲: requirement / design / plan / report / implementation / tests / docs alignment
  - pass 条件: reviewer pass
- final commit gate:
  - commit 範囲: final report ledger / planning evidence updates only if previous implementation steps are already committed.
  - final report ledger:
    - all closure ids `tc-001` to `tc-007` closed.
    - no `Status=open` Decision Ledger entries.
    - EAL includes research/interview/design draft/plan draft adoption.
    - all S01-S90 step commits or approved-no-op evidence recorded.
  - post-commit external evidence destination:
    - final response / PR / issue comment records final commit hash and clean worktree check.
- closure id:
  - `tc-007`
- concrete evidence:
  - `tc-s99-001` manual-required: final gates close without replacing step gates.
    - 前提: S01-S90 are committed or approved-no-op.
    - 操作: run final QA, issue-wide code review, final spec review, final validation, final report ledger.
    - 期待結果: final gates pass and no final review substitutes for per-step review/commit.
    - 失敗検出: incomplete closure, missing reviewer pass, open decision entry, catch-up final commit.
    - 検証方法: reviewer outputs, command evidence, final clean check.
    - 関連 closure id: `tc-007`

## 未確定事項

- Blocking question:
  - なし。
- Non-blocking execution risks:
  - S04 で broad template / prompt drift が見つかった場合は、small severe fix とするか follow-up にするかを report Decision Ledger に記録する。
  - Sub-agent / reviewer unavailable は affected gate を block / incomplete にする。success path として扱わない。

## 最終完了条件

- AC/EC 達成:
  - `tc-001` through `tc-007` closed in Step/Test Contract Closure and Closure Coverage.
- docs 影響解決:
  - S90 `spec-reviewer` pass。
- 全 implementation step 完了:
  - S01-S90 committed / approved-no-op.
- final quality gate pass:
  - final `qa-reviewer`: pass
  - issue-wide `code-reviewer`: pass
  - final `spec-reviewer`: pass
- final delivery:
  - final report ledger complete.
  - final commit hash and clean status recorded as external delivery evidence.
