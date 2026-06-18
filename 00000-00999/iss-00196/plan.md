---
種別: 実装計画書（Issue）
ID: "iss-00196"
タイトル: "Document Decision Implementation Layer Responsibilities"
関連GitHub: ["#196"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-18"
依存: ["requirement.md", "design.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00196 Document Decision Implementation Layer Responsibilities — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001: Initiative / Epic / Issue の decision responsibility が読める。
  - AC-002: Issue planning / clarification skill が decision-only Issue を早期検出する。
  - AC-003: 具体例と good / bad pattern が docs にある。
  - AC-004: Templates から作成済み artifact に例や authoring-only instruction が残らない。
  - AC-005: Evidence Adoption Ledger が採用証跡を追跡できる。
  - AC-006: Reviewer が thin skills / thin templates / docs detailed guidance を確認できる。
- EC:
  - EC-001: Issue-local lightweight decision は Issue-local に閉じられる。
  - EC-002: Cross-issue decision は Epic へ戻す。
  - EC-003: Cross-epic decision は Initiative / ADR 候補へ戻す。
  - EC-004: Authoring agent は docs の具体例を参照し、template body へ例を追加しない。
- 制約:
  - Provider source first; dogfooding mirror is validation target.
  - No runtime enforcement / bot / strict schema work in this Issue.
  - One implementation step = one review scope = one commit boundary.

## 依存関係から導く実装順序
- 依存関係の参照元:
  - `design.md` の依存関係分析、Module Dependency Diagram、ディレクトリ / ファイル変更計画。
- 順序ルール:
  - Docs policy を先に固定し、skills は docs へ薄く route し、templates は最後に docs/skills と矛盾しない薄い scaffold へ整える。
  - Dogfooding mirror / validation は provider edits 後にまとめて確認する。
- step 依存サマリー:
  - S01 docs decision-routing surface:
    - 依存: reviewed requirement/design.
    - unblock: S02 skill routing, S03 template checks.
    - 対象ファイル: provider docs, new `docs/authoring/decision-routing.md`.
  - S02 thin skill gates:
    - 依存: S01 docs route target.
    - unblock: S03 template authoring flow consistency.
    - 対象ファイル: provider skills under `src/spec_dock/assets/install_root/.agents/skills/`.
  - S03 thin templates:
    - 依存: S01 docs policy and S02 skill routing.
    - unblock: S90 mirror inspection.
    - 対象ファイル: provider templates.
  - S90 docs impact / mirror / validation:
    - 依存: S01-S03.
    - unblock: S99 final quality gate.
  - S99 final quality gate:
    - 依存: S90.

## ステップ一覧
- S01:
  - 観測可能な振る舞い: Provider docs explain decision placement and route concrete examples to `docs/authoring/decision-routing.md`.
  - 依存: fresh design pass.
  - unblock: S02, S03.
  - 対象ファイル: provider docs.
  - 閉じる要件: AC-001, AC-003, EC-001, EC-002, EC-003, EC-004.
  - レビューゲート: spec-reviewer docs/spec alignment.
- S02:
  - 観測可能な振る舞い: Planning / clarification skills expose a thin decision-only stop/routing gate and link to docs.
  - 依存: S01.
  - unblock: S03.
  - 対象ファイル: provider skills.
  - 閉じる要件: AC-002, AC-006.
  - レビューゲート: spec-reviewer docs/spec alignment.
- S03:
  - 観測可能な振る舞い: Provider templates are thin final-artifact scaffolds without examples or long authoring prose.
  - 依存: S01, S02.
  - unblock: S90.
  - 対象ファイル: provider templates.
  - 閉じる要件: AC-004, EC-004.
  - レビューゲート: spec-reviewer docs/spec alignment.
- S90:
  - 観測可能な振る舞い: Dogfooding mirror / validation / report evidence reflects provider changes.
  - 依存: S01-S03.
  - unblock: S99.
  - 対象ファイル: `spec-dock/` mirror as generated/validated surface, `report.md`.
  - 閉じる要件: AC-005, AC-006.
  - レビューゲート: spec-reviewer docs impact review.
- S99:
  - 観測可能な振る舞い: Final QA/code/spec gates confirm issue readiness for execution completion.
  - 依存: S90.
  - 対象ファイル: integrated diff.
  - 閉じる要件: all requirements and non-scope constraints.
  - レビューゲート: qa-reviewer, code-reviewer if code/test/scaffold behavior changed, spec-reviewer.

## 要件 ↔ ステップ対応
- AC-001 -> S01, S02
- AC-002 -> S02
- AC-003 -> S01
- AC-004 -> S03
- AC-005 -> S90
- AC-006 -> S01, S02, S03, S90, S99
- EC-001 -> S01
- EC-002 -> S01, S02
- EC-003 -> S01, S02
- EC-004 -> S01, S03

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ | スライス | 種別 | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル | クロージャ証跡 |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | docs decision routing | acceptance | AC-001, EC-001, EC-002, EC-003 | Docs state Issue/Epic/Initiative decision ownership and routing destinations | `rg` / inspection over provider docs | decision-only Issue proceeds to execution | yes | inspect-only | report Step/Test/Closure rows |
| tc-002 | S01 | docs examples | acceptance | AC-003, EC-004 | `docs/authoring/decision-routing.md` contains generic concrete examples and good/bad patterns | new provider doc inspection | examples duplicated into templates/skills | yes | inspect-only | report Step/Test/Closure rows |
| tc-003 | S02 | skill routing | acceptance | AC-002 | Issue planning / clarification skills expose thin decision-only stop/routing gate and docs link | `rg` / inspection over provider skills | skill misses decision-only issue | yes | inspect-only | report Step/Test/Closure rows |
| tc-004 | S02 | skill thinness | invariant | AC-006 | Skills do not embed long examples or duplicate docs detail | targeted `rg` and reviewer inspection | skill becomes tutorial/manual | yes | inspect-only | report Step/Test/Closure rows |
| tc-005 | S03 | template thinness | acceptance | AC-004, EC-004 | Templates contain final-artifact scaffold/evidence slots only and no example prose | targeted `rg` over provider templates | completed specs inherit instructional noise | yes | inspect-only | report Step/Test/Closure rows |
| tc-006 | S03 | product-specific leakage | negative | AC-004 | Templates contain no dogfooding-specific product / architecture terms | targeted `rg` over provider templates | reusable scaffold leaks local context | yes | inspect-only | report Step/Test/Closure rows |
| tc-007 | S90 | validation/mirror | acceptance | AC-005, AC-006 | Provider edits validate and dogfooding mirror is inspected or explicitly marked not refreshed with reason | `./spec-dock/scripts/spec-dock validate`; sync/inspection evidence | provider/mirror drift hidden | yes | manual-required | report validation evidence |
| tc-008 | S99 | final quality | acceptance | AC-001..AC-006 | Final reviewers pass or blocked reason is recorded | reviewer outputs | incomplete handoff presented as ready | yes | manual-required | final gate rows |
| tc-009 | S99 | non-scope constraints | constraint | constraints / non-scope | No runtime enforcement, bot/schema work, GitHub mutation, or multi-step batching is introduced | integrated diff, report step gates, git history | implementation expands beyond approved docs/skills/templates workflow scope | yes | manual-required | final gate rows and Step Commit Gate evidence |

## レビュー / QA ゲート方針
- RG1 step review:
  - S01/S02/S03/S90 are docs/template/skill-text oriented, so use `spec-reviewer` docs/spec alignment before each step commit.
  - If implementation adds or changes tests / installer behavior, add `code-reviewer` for that step.
- QG1 final QA:
  - `qa-reviewer` checks obligation coverage and whether integration tests are sufficient.
- CG1 final code review:
  - Required for the issue-wide integrated diff. If the final diff is docs/templates/skills only, code-reviewer still reviews structure, responsibility boundary, and regression risk from a no-runtime-change perspective.
- SG1 final spec review:
  - `spec-reviewer` checks requirement / design / plan / report / implementation / docs alignment.

## 実行ルール（全ステップ共通）
- Do not mutate canonical docs outside the current step's allowed paths.
- Do not change runtime enforcement, CLI behavior, GitHub state, or schema validation in this Issue.
- Each step must update `report.md` with Implementation Delegation Gate, Delegated Worker Evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, and Step Commit Gate evidence.
- If a step discovers a new durable decision, record it in the decision ledger and decide whether it needs design amendment / re-review before continuing.

## 実装ステップ

### 実装ステップ S01 — Provider docs decision-routing guidance
- 振る舞いの目標:
  - Authoring agents can read provider docs to decide whether a finding belongs in Issue, Epic, Initiative, ADR, or clarification before execution handoff.
- design 参照:
  - `design.md` インターフェース契約 / ディレクトリ変更計画。
- 依存:
  - Fresh design reviewer pass.
- unblock:
  - S02, S03.
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/decision-routing.md`
- 計画済み契約:
  - scope:
    - Add durable decision routing semantics and generic examples in docs.
    - Workflow docs provide entry/routing rule; `decision-routing.md` owns concrete examples and good/bad patterns.
  - テスト義務:
    - closure id: tc-001, tc-002.
    - coverage rationale: AC-001/AC-003 require docs-level understanding before skills/templates can stay thin.
  - Red / 代替証跡の要件:
    - inspect-only:
      - Existing docs do not yet contain a single `decision-routing.md` target or explicit decision-only routing matrix.
      - Record before/after targeted `rg` evidence in `report.md`.
  - 実装範囲:
    - allowed paths: listed target docs only.
    - forbidden changes: templates, skills, runtime code, tests, GitHub state.
  - Green 検証:
    - `rg -n "decision-routing|Decision-only|Issue-local|Epic|Initiative" src/spec_dock/assets/spec_dock/docs`
    - Manual inspection of `decision-routing.md`.
  - Refactor / cleanup ガードレール:
    - Keep workflow docs concise; move examples to `decision-routing.md`.
  - amendment trigger:
    - If docs require runtime enforcement or new lifecycle states, return to design.

#### 委任契約（delegation contract）
- 委任ロール: doc-writer
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, provider docs listed above.
- 許可 paths:
  - S01 target docs only.
- 禁止 changes:
  - Skills/templates/runtime/tests/GitHub state.
- 受け入れ条件:
  - tc-001 and tc-002 close.
- 必須 tests または docs-only verification:
  - Targeted `rg` and manual docs inspection.
- reviewer focus:
  - spec-reviewer docs/spec alignment.
- 必須出力:
  - changed files, docs inspection result, unresolved risks, `Ledger Note` or no material decisions.
- 停止条件:
  - Need to define runtime enforcement; unclear Issue/Epic/Initiative responsibility; examples cannot be generic.

#### 具体テストケース一覧
- `tc-s01-001` acceptance: docs route decision-only work to the right scope
  - 前提: Provider docs are at the pre-step state.
  - 操作: Inspect workflow docs and `decision-routing.md` after S01.
  - 期待結果: Issue-local, Epic-owned, Initiative-owned, ADR/clarification routing are distinguishable.
  - 失敗検出: A decision-only Issue can still be read as execution-ready.
  - 検証方法: targeted `rg` plus manual inspection.
  - 関連 closure id: tc-001
- `tc-s01-002` acceptance: concrete examples live in docs authoring guidance
  - 前提: Templates and skills are not the example surface.
  - 操作: Inspect `src/spec_dock/assets/spec_dock/docs/authoring/decision-routing.md`.
  - 期待結果: Generic concrete examples and good/bad patterns exist in that doc.
  - 失敗検出: Examples are absent from docs or are only present in templates/skills.
  - 検証方法: manual docs inspection and `rg -n "good|bad|example|例" src/spec_dock/assets/spec_dock/docs/authoring/decision-routing.md`.
  - 関連 closure id: tc-002

#### ステップ完了契約
- closure id: tc-001, tc-002
- close 条件:
  - docs contain routing rule and `decision-routing.md` owns examples.
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate.
- 残リスク:
  - Docs may still be too verbose; reviewer handles docs/spec alignment.

#### ステップゲート
- step reviewer gate:
  - reviewer: spec-reviewer
  - pass 条件: review_status: pass
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S01 docs changes and report evidence only.

### 実装ステップ S02 — Thin skill decision-only gates
- 振る舞いの目標:
  - Planning / clarification skills expose decision-only stop conditions without becoming tutorials.
- design 参照:
  - `design.md` Skill contract.
- 依存:
  - S01 committed.
- unblock:
  - S03.
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md`
- 計画済み契約:
  - scope:
    - Add thin first-read gates and links to decision-routing docs.
  - テスト義務:
    - closure id: tc-003, tc-004.
    - coverage rationale: AC-002/AC-006 require the first-read surface to stop wrong execution without duplicating docs.
  - Red / 代替証跡の要件:
    - inspect-only:
      - Before/after `rg` for routing terms in skill files.
  - 実装範囲:
    - allowed paths: listed skill files only.
    - forbidden changes: docs/templates/runtime/tests/GitHub state.
  - Green 検証:
    - `rg -n "decision-only|decision routing|decision-routing|Epic|Initiative|stop" src/spec_dock/assets/install_root/.agents/skills/spec-dock-*`
  - Refactor / cleanup ガードレール:
    - Do not paste examples into skills; link docs.
  - amendment trigger:
    - If skill needs long policy explanation to be understandable, return to design.

#### 委任契約
- 委任ロール: doc-writer
- 入力 docs:
  - S01 docs, `requirement.md`, `design.md`, `plan.md`.
- 許可 paths:
  - S02 target skill files only.
- 禁止 changes:
  - Provider docs/templates/runtime/tests/GitHub state.
- 受け入れ条件:
  - tc-003 and tc-004 close.
- 必須 tests または docs-only verification:
  - Targeted `rg`; manual skill inspection; spec-reviewer pass.
- reviewer focus:
  - spec-reviewer docs/spec alignment.
- 必須出力:
  - changed files, verification result, unresolved risks, Ledger Note.
- 停止条件:
  - Skill needs broad rewrite outside decision-only gate; docs route target missing.

#### 具体テストケース一覧
- `tc-s02-001` acceptance: issue planning sees decision-only stop condition
  - 前提: S01 docs are available.
  - 操作: Inspect issue planning and clarification skills.
  - 期待結果: A decision-only Issue is routed back to Epic/Initiative/clarification before execution assumptions.
  - 失敗検出: Skill can proceed to plan/execution without checking decision ownership.
  - 検証方法: targeted `rg` and manual inspection.
  - 関連 closure id: tc-003
- `tc-s02-002` invariant: skills remain thin
  - 前提: Examples are owned by docs.
  - 操作: Inspect changed skill text for example blocks or long field semantics.
  - 期待結果: Skills contain stop/routing/linking only, not tutorial examples.
  - 失敗検出: Skill duplicates `decision-routing.md` examples.
  - 検証方法: manual inspection and spec-reviewer docs/spec alignment.
  - 関連 closure id: tc-004

#### ステップ完了契約
- closure id: tc-003, tc-004
- close 条件:
  - Skill files contain thin decision routing and no long examples.
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate.
- 残リスク:
  - Over-thinning can hide mandatory first actions; reviewer focus includes first-read sufficiency.

#### ステップゲート
- step reviewer gate:
  - reviewer: spec-reviewer
  - pass 条件: review_status: pass
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S02 skill changes and report evidence only.

### 実装ステップ S03 — Thin provider templates
- 振る舞いの目標:
  - Provider templates generate clean final-artifact scaffolds without example prose or dogfooding leakage.
- design 参照:
  - `design.md` Template contract.
- 依存:
  - S01, S02 committed.
- unblock:
  - S90.
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/templates/issue/*.md`
  - `src/spec_dock/assets/spec_dock/templates/epic/*.md`
  - `src/spec_dock/assets/spec_dock/templates/initiative/*.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/*.md`
  - `src/spec_dock/assets/spec_dock/templates/README.md`
- 計画済み契約:
  - scope:
    - Remove examples / authoring-only prose that would remain in completed artifacts.
    - Keep final-artifact headings, minimal prompts, evidence slots, and readiness checklist fields.
  - テスト義務:
    - closure id: tc-005, tc-006.
    - coverage rationale: AC-004/EC-004 are template cleanliness requirements.
  - Red / 代替証跡の要件:
    - inspect-only:
      - Before/after `rg` for forbidden example/noise markers.
  - 実装範囲:
    - allowed paths: provider templates only.
    - forbidden changes: docs/skills/runtime/tests unless plan amendment.
  - Green 検証:
    - `rg -n "例:|サンプル|good example|bad example|management_core|shared kernel" src/spec_dock/assets/spec_dock/templates`
    - Manual inspection for remaining placeholders that are final-artifact fields vs authoring examples.
  - Refactor / cleanup ガードレール:
    - Do not remove necessary final report evidence slots or plan executable schema.
  - amendment trigger:
    - If template schema shrink changes runtime generation expectations or tests, amend plan and add code-reviewer/test step.

#### 委任契約
- 委任ロール: doc-writer
- 入力 docs:
  - S01 docs, S02 skills, `requirement.md`, `design.md`, `plan.md`.
- 許可 paths:
  - S03 target templates only.
- 禁止 changes:
  - Provider docs/skills/runtime/tests/GitHub state.
- 受け入れ条件:
  - tc-005 and tc-006 close.
- 必須 tests または docs-only verification:
  - Targeted `rg`, manual template inspection, spec-reviewer pass.
- reviewer focus:
  - spec-reviewer docs/spec alignment and template cleanliness.
- 必須出力:
  - changed files, verification result, unresolved risks, Ledger Note.
- 停止条件:
  - Need to alter runtime generation or remove required evidence slots.

#### 具体テストケース一覧
- `tc-s03-001` acceptance: templates stay thin
  - 前提: S01/S02 have established docs/skills responsibilities.
  - 操作: Inspect provider templates after S03.
  - 期待結果: Templates contain final-artifact scaffold/evidence slots, not examples or long authoring instructions.
  - 失敗検出: Completed spec artifacts would inherit sample prose.
  - 検証方法: targeted `rg` plus manual template inspection.
  - 関連 closure id: tc-005
- `tc-s03-002` negative: product-specific leakage is absent
  - 前提: Dogfooding examples are evidence, not shipped template content.
  - 操作: Search provider templates for dogfooding-specific terms.
  - 期待結果: No local product/architecture names appear in reusable templates.
  - 失敗検出: Reusable scaffold leaks local context into new repos.
  - 検証方法: targeted `rg` for known dogfooding terms and generic example markers.
  - 関連 closure id: tc-006

#### ステップ完了契約
- closure id: tc-005, tc-006
- close 条件:
  - Template forbidden-marker checks pass or every match is justified as final-artifact field syntax.
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate.
- 残リスク:
  - Template minimalism can reduce authoring convenience; docs own examples.

#### ステップゲート
- step reviewer gate:
  - reviewer: spec-reviewer
  - pass 条件: review_status: pass
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S03 template changes and report evidence only.

### ドキュメント影響の解消ステップ S90（docs impact resolution / docs refresh）
- 対象:
  - Provider docs / skills / templates, dogfooding mirror, report evidence.
- 対応:
  - Run `./spec-dock/scripts/spec-dock validate`.
  - Run `./spec-dock/scripts/spec-dock sync` if provider asset changes must be projected into dogfooding artifacts for inspection.
  - Inspect mirror paths corresponding to changed provider docs/skills/templates.
  - Update `report.md` final quality gate / closure ledgers with command results and reviewer status.
- doc update owner:
  - doc-writer when mirror/docs updates are required.
- spec/doc review:
  - reviewer: spec-reviewer
  - pass 条件: docs/skills/templates/mirror evidence aligns with requirement/design/plan.
- closure:
  - tc-007.

### 最終品質ゲートステップ S99（final quality gate）
- branch diff 範囲:
  - All changes for `iss-00196`.
- 必須 validation:
  - `./spec-dock/scripts/spec-dock validate`
  - Relevant targeted `rg` checks from S01-S03.
  - Focused pytest if S03 triggered runtime/scaffold behavior changes.
- final QA gate:
  - reviewer: qa-reviewer
  - 範囲: closure coverage, missing high-value tests, integration test need.
  - pass 条件: review_status: pass.
- final code review ゲート:
  - reviewer: code-reviewer.
  - 範囲: integrated diff, responsibility boundaries, regression risk.
  - pass 条件: review_status: pass.
- final spec review ゲート:
  - reviewer: spec-reviewer
  - 範囲: requirement / design / plan / report / implementation / tests / docs alignment.
  - pass 条件: review_status: pass.
- final commit gate:
  - commit 範囲: final report ledger updates only after step commits are complete.
  - final report ledger: S99 command evidence and reviewer verdicts.
  - post-commit external evidence destination: final response / PR.
- closure:
  - tc-008, tc-009.

## 未確定事項
- Blocking な未確定事項はない。
- Execution 中に runtime behavior / generated scaffold tests が必要になった場合は、S03 または S90 の plan amendment と fresh re-review を行う。

## 最終完了条件
- AC/EC 達成:
  - tc-001 through tc-009 closed in `report.md`.
- docs 影響解決:
  - S90 pass.
- 全 implementation step 完了:
  - S01, S02, S03 committed or valid approved-no-op with evidence.
- final quality gate pass:
  - qa-reviewer pass.
  - code-reviewer pass.
  - spec-reviewer pass.
- lifecycle:
  - After commits/PR/merge readiness are handled by the appropriate downstream workflow, `issue finish` may be used only when `workflow_issue.md` completion requirements are satisfied.
