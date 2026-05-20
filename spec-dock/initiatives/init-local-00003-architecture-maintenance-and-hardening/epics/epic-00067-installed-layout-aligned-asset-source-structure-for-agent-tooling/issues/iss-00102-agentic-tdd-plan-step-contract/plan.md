---
種別: 実装計画書（Issue）
ID: "iss-00102"
タイトル: "Agentic TDD plan step contract"
関連GitHub: ["#102"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-20"
依存: ["requirement.md", "design.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00102 Agentic TDD plan step contract — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001: risk-calibrated test obligation guidance.
  - AC-002: pre-implementation red / alternative evidence path.
  - AC-003: generated `plan.md` as executable Agentic TDD workflow contract.
  - AC-004: reviewer evaluation based on obligation coverage and evidence.
  - AC-005: source-of-truth separation and routing.
  - AC-006: provider source reflected into consumer scaffold / installed assets.
  - AC-007: closure requires planned requirements plus observed report evidence.
- EC:
  - EC-001: docs-only / inspect-only / manual-required evidence paths.
  - EC-002: discovered tests and plan amendment rules.
  - EC-003: bundled behavior slice exception.
  - EC-004: low-risk few-obligation rationale without raw count guidance.
- 制約:
  - provider-side source first.
  - `plan.md` owns planned contract; `report.md` owns observed evidence ledger.
  - `具体テストケース一覧` heading remains.
  - `phase_plan_issue.md` remains plan philosophy + review checklist.

## 実行契約
- この計画は、この Issue 自身を実行するための planned contract である。
- この Issue で実装される将来の `templates/issue/plan.md` も planned contract にするが、この active `plan.md` 自体を実装対象 template と混同しない。
- 各 implementation step は原則 1 behavior slice / 1 review scope / 1 commit とする。
- docs / templates / skills / workflow text は `doc-writer` に委任する。
- tests / structural assertions は `dev-coder` に委任する。
- step の observed evidence は `report.md` に残す。

## 依存関係から導く実装順序
- 依存関係の正本:
  - `design.md` の Document Ownership Matrix。
  - `design.md` の Plan / Report Boundary。
  - `design.md` の ディレクトリ / ファイル変更計画。
- 順序ルール:
  - 正本境界を先に直し、その後に template、agent routing、tests を更新する。
  - provider-side assets を先に更新し、dogfooding mirror は最後に確認する。
- step 依存 summary:
  - S01:
    - 依存: requirement / design.
    - unblock: S02, S03.
    - 対象ファイル: workflow and authoring docs.
  - S02:
    - 依存: S01 ownership contract.
    - unblock: S03, S04.
    - 対象ファイル: issue plan/report templates.
  - S03:
    - 依存: S01/S02 schema.
    - unblock: S04.
    - 対象ファイル: prompt, skill, agent configs.
  - S04:
    - 依存: S01-S03 provider assets.
    - unblock: S90/S99.
    - 対象ファイル: structural tests.

## ステップ一覧
- S01:
  - 観測可能な振る舞い: plan authoring docs が source-of-truth separation と executable step schema を説明する。
  - 依存: design ownership matrix.
  - unblock: templates and routing updates.
  - 対象ファイル: `workflow_issue.md`, `phase_plan_issue.md`, `authoring/issue-plan.md`, `reference_hard_cutover.md`.
  - 閉じる要件: AC-001, AC-002, AC-003, AC-005, EC-002, EC-003, EC-004.
  - レビューゲート: spec-reviewer docs/spec alignment.
- S02:
  - 観測可能な振る舞い: generated issue `plan.md` / `report.md` templates encode planned contract and observed evidence ledger.
  - 依存: S01.
  - unblock: prompt/skill/agent configs and tests.
  - 対象ファイル: `templates/issue/plan.md`, `templates/issue/report.md`.
  - 閉じる要件: AC-001, AC-002, AC-003, AC-007, EC-001, EC-002, EC-004.
  - レビューゲート: spec-reviewer docs/spec alignment.
- S03:
  - 観測可能な振る舞い: installed agent prompt/skill/configs consume the new plan step contract without duplicating policy.
  - 依存: S01, S02.
  - unblock: structural tests.
  - 対象ファイル: `execute-issue.md`, `spec-dock-issue-execution/SKILL.md`, reviewer/worker agent configs.
  - 閉じる要件: AC-004, AC-005, AC-007.
  - レビューゲート: spec-reviewer docs/spec alignment.
- S04:
  - 観測可能な振る舞い: scaffold and installed asset assertions catch regressions in the new contract.
  - 依存: S01, S02, S03.
  - unblock: final gates.
  - 対象ファイル: `tests/test_init_update.py`.
  - 閉じる要件: AC-006, AC-007.
  - レビューゲート: code-reviewer for tests.
- S90:
  - 観測可能な振る舞い: dogfooding docs/templates/agent assets are refreshed or confirmed aligned.
  - 依存: S01-S04.
  - レビューゲート: spec-reviewer docs/spec alignment.
- S99:
  - 観測可能な振る舞い: issue-wide quality gates pass.
  - 依存: S90.
  - レビューゲート: qa-reviewer, issue-wide code-reviewer, spec-reviewer.

## 要件 ↔ ステップ対応
- AC-001 -> S01, S02.
- AC-002 -> S01, S02.
- AC-003 -> S01, S02, S03.
- AC-004 -> S03, S04, S99.
- AC-005 -> S01, S03.
- AC-006 -> S04, S90.
- AC-007 -> S02, S03, S04, S99.
- EC-001 -> S02.
- EC-002 -> S01, S02.
- EC-003 -> S01.
- EC-004 -> S01, S02.

## Spec-Locked Closure Index（仕様固定クロージャ索引）
| id | step | slice | type | spec link | locked expectation | observable input/state | bug class guarded | required | evidence level | closure evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | source-of-truth docs | acceptance | AC-005 | workflow / authoring / phase docs have non-overlapping ownership | provider docs text | policy drift | yes | inspect-only | report S01 closure |
| tc-002 | S01 | test obligation language | acceptance | AC-001, EC-004 | raw `1〜3件程度` guidance is removed or non-normative | provider docs text | under-testing by count heuristic | yes | inspect-only | report S01 closure |
| tc-003 | S02 | plan template schema | acceptance | AC-001, AC-002, AC-003, EC-004 | plan template encodes behavior goal, obligations, red/alternative path, green verification, refactor, report destination, amendment trigger | generated issue plan scaffold | plan as passive task list | yes | inspect-only | report S02 closure |
| tc-004 | S02 | report ledger | acceptance | AC-007, EC-001, EC-002 | report template owns observed evidence ledger and discovered tests | generated issue report scaffold | evidence authority confusion | yes | inspect-only | report S02 closure |
| tc-005 | S03 | agent routing | acceptance | AC-004, AC-005 | prompt/skill/configs consume plan contract and avoid duplicated detailed policy | installed agent assets | agents bypass plan contract | yes | inspect-only | report S03 closure |
| tc-006 | S04 | regression assertions | regression | AC-006 | tests fail if stale count guidance or missing executable contract language returns | `tests/test_init_update.py` | scaffold regression | yes | red-required | report S04 closure |
| tc-007 | S90 | dogfooding mirror | acceptance | AC-006 | local dogfooding workspace reflects provider-side source or has recorded divergence rationale | mirror paths | provider/consumer drift | yes | manual-required | report S90 closure |

## レビュー / QA ゲート方針
- Per-step docs/template/skill/config review:
  - reviewer: spec-reviewer.
  - pass 条件: docs/spec alignment and no stale external discussion pollution.
- Per-step test review:
  - reviewer: code-reviewer.
  - pass 条件: structural assertions are scoped, stable, and verify the changed contract.
- Final QA:
  - reviewer: qa-reviewer.
  - pass 条件: test strategy is sufficient for docs/templates/installed assets and no high-value structural assertion is missing.
- Final integrated review:
  - reviewers: issue-wide code-reviewer and spec-reviewer.

## 共通 step gate（S01-S04）
- report draft update:
  - step reviewer gate の前に、planned closure、delegation decision、verification intent、expected report evidence destination を `report.md` に下書き更新する。
- step reviewer gate:
  - reviewer mapping:
    - docs / templates / prompts / skills / agent config text: spec-reviewer.
    - tests / test harness changes: code-reviewer.
  - fail 時は bounded follow-up を行い、同じ gate を pass まで再実行する。
- step result approval:
  - reviewer pass と report draft evidence を確認してから commit gate へ進む。
- commit gate:
  - 1 implementation step = 1 review scope = 1 commit を標準にする。
  - commit 後に `git status --short --branch` で意図しない staged / unstaged 変更がないことを確認する。
- no-op gate:
  - 差分なしで閉じる場合は、対象 step、変更不要理由、確認対象、差分なし確認コマンド、read-only evidence を report に残す。

## 実装ステップ

### S01 — Source-of-truth docs encode Agentic TDD plan ownership
- behavior goal:
  - Docs define `plan.md` as planned executable workflow contract and `report.md` as observed evidence ledger without duplicating field-level policy across workflow and phase docs.
- design 参照:
  - Document Ownership Matrix.
  - Plan / Report Boundary.
- 依存:
  - requirement and design approved.
- unblock:
  - S02, S03.
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_hard_cutover.md`
- planned contract:
  - scope:
    - Move or split hard cutover optional pattern out of standard issue workflow.
    - Keep `phase_plan_issue.md` as philosophy + review checklist.
    - Put executable step schema authoring details in `docs/authoring/issue-plan.md`.
  - test obligation:
    - tc-001, tc-002.
  - Red / alternative evidence requirement:
    - inspect-only: show current docs contain stale or overlapping ownership language, including normative count guidance and hard cutover content in standard workflow.
  - Green verification:
    - targeted inspection with `rg` for stale phrases and ownership markers.
  - Refactor / cleanup:
    - remove duplicated policy text rather than adding new parallel descriptions.
  - report evidence destination:
    - `Step Contract Closure`, `Test Contract Closure`, `Closure Coverage`, `Closure Delta` if moving hard cutover text.
  - amendment trigger:
    - If docs require changing accepted terms such as `具体テストケース一覧` or `phase_plan_issue.md` ownership, stop and amend plan.

#### delegation contract
- delegated role:
  - doc-writer.
- input docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
- allowed paths:
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_hard_cutover.md`
- forbidden changes:
  - runtime code.
  - tests.
  - dogfooding mirror direct edits before provider source is updated.
  - changing accepted requirement decisions.
- acceptance criteria:
  - AC-001, AC-002, AC-003, AC-005.
- required tests or docs-only verification:
  - `rg -n "1〜3|hard cutover|planned contract|observed evidence ledger" src/spec_dock/assets/spec_dock/docs`.
- reviewer focus:
  - spec-reviewer docs/spec alignment.
- stop conditions:
  - accepted requirement conflicts.
  - need to rename `具体テストケース一覧`.
  - need to remove `phase_plan_issue.md`.
- output required:
  - changed files.
  - summary of ownership changes.
  - inspection commands and results.
  - unresolved risks.

#### 具体テストケース一覧
- `tc-s01-001` inspect-only: source-of-truth ownership is non-overlapping
  - 前提: workflow / phase / authoring docs currently contain overlapping Issue plan policy.
  - 操作: docs are updated according to the ownership matrix.
  - 期待結果: workflow owns execution policy, authoring owns plan field semantics, phase owns philosophy/checklist.
  - 失敗検出: field-level policy remains duplicated in workflow and phase docs.
  - 検証方法: targeted `rg` inspection and spec-reviewer review.
  - 関連 closure id: tc-001
- `tc-s01-002` inspect-only: raw count guidance no longer drives test adequacy
  - 前提: existing plan guidance includes `1〜3件程度`.
  - 操作: docs are updated to use risk-calibrated obligation coverage.
  - 期待結果: count wording is absent or explicitly non-normative, and coverage rationale is the rule.
  - 失敗検出: agents can still read `1〜3件程度` as cap, floor, or sufficient condition.
  - 検証方法: targeted `rg "1〜3|risk-calibrated|obligation"` inspection.
  - 関連 closure id: tc-002

#### step closure contract
- closure id:
  - tc-001
  - tc-002
- close 条件:
  - Provider docs encode source-of-truth separation and risk-calibrated obligation guidance.
  - hard cutover optional pattern is no longer embedded as standard issue workflow.
- 検証 evidence:
  - targeted `rg` inspection.
  - spec-reviewer pass.
- report evidence:
  - Step Contract Closure.
  - Test Contract Closure.
  - Closure Coverage.
- 残リスク:
  - phase doc may still be longer than ideal; acceptable if it no longer owns field-level details.

#### step gate
- delegation 判断:
  - delegated to doc-writer.
- step reviewer gate:
  - reviewer: spec-reviewer.
  - pass 条件: review_status pass.
- commit gate:
  - closure 状態: committed.
  - commit 範囲: S01 docs only.
- no-op gate:
  - 許可条件: all target docs already satisfy the ownership matrix.

### S02 — Issue templates express planned contract and observed ledger
- behavior goal:
  - Generated issue `plan.md` has executable Agentic TDD planned contract fields; generated `report.md` records observed evidence and discovered tests.
- design 参照:
  - Executable Step Schema.
  - Plan / Report Boundary.
- 依存:
  - S01.
- unblock:
  - S03, S04.
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/templates/issue/plan.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/report.md`
- planned contract:
  - scope:
    - Simplify plan template while preserving required execution fields.
    - Add report observed evidence ledger sections.
  - test obligation:
    - tc-003, tc-004.
  - Red / alternative evidence requirement:
    - inspect-only: current templates lack clean planned/observed boundary and still contain stale count guidance.
  - Green verification:
    - targeted inspection of template headings and stale phrases.
  - Refactor / cleanup:
    - remove redundant summary/table fields where they duplicate implementation step contract.
  - report evidence destination:
    - S02 Step Contract Closure and Closure Delta.
  - amendment trigger:
    - If template simplification removes required workflow gates, stop and amend plan.

#### delegation contract
- delegated role:
  - doc-writer.
- input docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - updated S01 docs.
- allowed paths:
  - `src/spec_dock/assets/spec_dock/templates/issue/plan.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/report.md`
- forbidden changes:
  - tests.
  - installed agent assets.
  - dogfooding mirror direct edits before provider source update.
- acceptance criteria:
  - AC-001, AC-002, AC-003, AC-007, EC-001, EC-002, EC-004.
- required tests or docs-only verification:
  - `rg -n "planned contract|observed evidence ledger|amendment trigger|report evidence destination|1〜3" src/spec_dock/assets/spec_dock/templates/issue`.
- reviewer focus:
  - spec-reviewer docs/spec alignment.
- stop conditions:
  - template cannot stay minimal while preserving required fields.
  - plan/report evidence authority becomes ambiguous.
- output required:
  - changed files.
  - before/after schema summary.
  - inspection evidence.
  - unresolved risks.

#### 具体テストケース一覧
- `tc-s02-001` inspect-only: plan template is executable planned contract
  - 前提: current plan template mixes summary, closure, tests, report update, and gates.
  - 操作: template is rewritten to expose behavior goal, obligations, red/alternative path, green verification, refactor, report destination, amendment trigger.
  - 期待結果: an implementation agent can follow a step without reading unrelated long policy text.
  - 失敗検出: plan remains a passive task list or long policy manual.
  - 検証方法: targeted inspection and spec-reviewer review.
  - 関連 closure id: tc-003
- `tc-s02-002` inspect-only: report template owns observed evidence
  - 前提: report template has closure tables but not explicit observed evidence ownership.
  - 操作: report ledger is clarified for red/green/refactor results, discovered tests, closure delta, reviewer status.
  - 期待結果: actual evidence is recorded in report, while plan stores planned requirements and evidence destinations.
  - 失敗検出: actual execution evidence is expected to be authoritative in both plan and report.
  - 検証方法: targeted inspection and spec-reviewer review.
  - 関連 closure id: tc-004

#### step closure contract
- closure id:
  - tc-003
  - tc-004
- close 条件:
  - Plan template and report template encode the planned/observed split.
- 検証 evidence:
  - targeted inspection.
  - spec-reviewer pass.
- report evidence:
  - Step Contract Closure.
  - Test Contract Closure.
  - Closure Coverage.
- 残リスク:
  - future users may still overfill plan; authoring docs and reviewer config mitigate this.

#### step gate
- delegation 判断:
  - delegated to doc-writer.
- step reviewer gate:
  - reviewer: spec-reviewer.
  - pass 条件: review_status pass.
- commit gate:
  - closure 状態: committed.
  - commit 範囲: S02 templates only.
- no-op gate:
  - 許可条件: target templates already satisfy tc-003 and tc-004.

### S03 — Agent routing consumes the executable plan contract
- behavior goal:
  - execute prompt, issue execution skill, and role configs route agents through the new plan step contract without duplicating full workflow policy.
- design 参照:
  - Document Ownership Matrix.
  - Agent handoff contract.
- 依存:
  - S01, S02.
- unblock:
  - S04.
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.codex/prompts/execute-issue.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `src/spec_dock/assets/install_root/.codex/agents/dev-coder.toml`
  - `src/spec_dock/assets/install_root/.codex/agents/code-reviewer.toml`
  - `src/spec_dock/assets/install_root/.codex/agents/qa-reviewer.toml`
  - `src/spec_dock/assets/install_root/.codex/agents/spec-reviewer.toml`
- planned contract:
  - scope:
    - Update routing and role I/O expectations.
    - Avoid copying full workflow.
  - test obligation:
    - tc-005.
  - Red / alternative evidence requirement:
    - inspect-only: current assets lack full plan-as-command-queue and role output contracts.
  - Green verification:
    - targeted inspection of prompt/skill/configs.
  - Refactor / cleanup:
    - remove stale wording such as `code-reviewer scope` where `review scope` is required.
  - report evidence destination:
    - S03 closure and reviewer status.
  - amendment trigger:
    - If agent config changes require new role semantics beyond this issue, stop and split follow-up.

#### delegation contract
- delegated role:
  - doc-writer.
- input docs:
  - `requirement.md`
  - `design.md`
  - updated S01/S02 docs and templates.
- allowed paths:
  - `src/spec_dock/assets/install_root/.codex/prompts/execute-issue.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `src/spec_dock/assets/install_root/.codex/agents/*.toml`
- forbidden changes:
  - runtime code.
  - tests.
  - non-issue prompts/skills unless a direct stale reference is found and reported.
- acceptance criteria:
  - AC-004, AC-005, AC-007.
- required tests or docs-only verification:
  - `rg -n "executable|planned contract|observed evidence|obligation|code-reviewer scope" src/spec_dock/assets/install_root/.codex src/spec_dock/assets/install_root/.agents`.
- reviewer focus:
  - spec-reviewer docs/spec alignment.
- stop conditions:
  - role config needs model/tool changes.
  - prompt/skill would become a duplicate workflow manual.
- output required:
  - changed files.
  - role contract summary.
  - inspection evidence.
  - unresolved risks.

#### 具体テストケース一覧
- `tc-s03-001` inspect-only: agents follow plan as command queue
  - 前提: execute prompt and skill currently point to workflow but do not fully encode the new planned/observed boundary.
  - 操作: prompt/skill/configs are updated to require reading plan step contract and writing observed evidence to report.
  - 期待結果: agents do not bypass plan step fields or treat implementation delegation as reviewer pass.
  - 失敗検出: role instructions still allow raw count testing or unstated evidence closure.
  - 検証方法: targeted inspection and spec-reviewer review.
  - 関連 closure id: tc-005

#### step closure contract
- closure id:
  - tc-005
- close 条件:
  - installed agent assets route through the planned contract and observed evidence ledger.
- 検証 evidence:
  - targeted inspection.
  - spec-reviewer pass.
- report evidence:
  - Step Contract Closure.
  - Test Contract Closure.
  - Closure Coverage.
- 残リスク:
  - model-specific behavior cannot be guaranteed by text alone; reviewer gates mitigate this.

#### step gate
- delegation 判断:
  - delegated to doc-writer.
- step reviewer gate:
  - reviewer: spec-reviewer.
  - pass 条件: review_status pass.
- commit gate:
  - closure 状態: committed.
  - commit 範囲: S03 installed agent assets only.
- no-op gate:
  - 許可条件: target assets already satisfy tc-005.

### S04 — Structural tests protect the shipped contract
- behavior goal:
  - Tests fail when stale guidance returns or provider assets lose executable contract / observed ledger fields.
- design 参照:
  - テスト戦略.
  - ディレクトリ / ファイル変更計画.
- 依存:
  - S01, S02, S03.
- unblock:
  - S90, S99.
- 対象ファイル:
  - `tests/test_init_update.py`
- planned contract:
  - scope:
    - Add targeted structural assertions.
  - test obligation:
    - tc-006.
  - Red / alternative evidence requirement:
    - red-required for test assertions where feasible: add assertions that fail before provider updates or demonstrate equivalent pre-change failure by targeted inspection.
  - Green verification:
    - targeted unittest subset for updated structural assertions:
      - `uv run python -m unittest tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure tests.test_init_update.TestInitUpdate.test_bundled_skill_routing_contract tests.test_init_update.TestInitUpdate.test_issue_102_agentic_tdd_contract_assets`
    - `./spec-dock/scripts/spec-dock validate`
  - Refactor / cleanup:
    - keep assertions focused on stable contract terms, not prose paragraphs.
  - report evidence destination:
    - S04 test closure.
  - amendment trigger:
    - If tests require runtime support beyond structural assertions, split follow-up issue.

#### delegation contract
- delegated role:
  - dev-coder.
- input docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - changed provider assets from S01-S03.
  - `tests/test_init_update.py`
- allowed paths:
  - `tests/test_init_update.py`
- forbidden changes:
  - runtime behavior changes.
  - broad test rewrites unrelated to asset structure.
  - removing existing coverage.
  - dogfooding mirror content changes; mirror refresh belongs to S90.
- acceptance criteria:
  - AC-006.
- required tests or docs-only verification:
  - targeted unittest subset for updated structural assertions:
    - `uv run python -m unittest tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure tests.test_init_update.TestInitUpdate.test_bundled_skill_routing_contract tests.test_init_update.TestInitUpdate.test_issue_102_agentic_tdd_contract_assets`
  - `./spec-dock/scripts/spec-dock validate`
- reviewer focus:
  - code-reviewer for tests.
- stop conditions:
  - structural assertions need unstable exact prose.
  - validation fails for unrelated existing issue.
- output required:
  - changed files.
  - tests run and results.
  - unresolved risks.

#### 具体テストケース一覧
- `tc-s04-001` red-required: stale count guidance cannot return
  - 前提: tests have assertions for provider plan docs/templates and installed assets.
  - 操作: run targeted test suite.
  - 期待結果: tests fail if normative `1〜3件程度` guidance returns in relevant provider assets.
  - 失敗検出: raw count heuristic is reintroduced as plan/test sufficiency rule.
  - 検証方法: targeted unittest subset for updated structural assertions.
  - 関連 closure id: tc-006
- `tc-s04-002` red-required: executable contract fields are protected
  - 前提: tests assert stable contract markers in plan/report templates and agent assets.
  - 操作: run targeted test suite.
  - 期待結果: tests fail if planned contract, observed evidence ledger, amendment trigger, or report evidence destination markers disappear.
  - 失敗検出: plan becomes passive task list again or report loses observed ledger.
  - 検証方法: targeted unittest subset for updated structural assertions.
  - 関連 closure id: tc-006
#### step closure contract
- closure id:
  - tc-006
- close 条件:
  - Structural tests cover stable contract markers.
- 検証 evidence:
  - targeted unittest subset for updated structural assertions.
  - `./spec-dock/scripts/spec-dock validate`
- report evidence:
  - Step Contract Closure.
  - Test Contract Closure.
  - Closure Coverage.
- 残リスク:
  - structural tests cannot prove model compliance; reviewer gates remain required.

#### step gate
- delegation 判断:
  - delegated to dev-coder.
- step reviewer gate:
  - reviewer: code-reviewer.
  - pass 条件: review_status pass.
- commit gate:
  - closure 状態: committed.
  - commit 範囲: S04 tests only.
- no-op gate:
  - 許可条件: existing tests already cover tc-006.

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs: yes.
  - templates: yes.
  - workflow: yes.
  - skill / prompt / agent configs: yes.
  - migration notes: only if hard cutover reference split requires a note.
- 対応:
  - Confirm all shipped docs/templates and installed assets changed in provider source are reflected or intentionally not reflected in dogfooding mirror.
  - Confirm no unrelated historical issue docs are migrated.
- closure id:
  - tc-007
- 検証 evidence:
  - `./spec-dock/scripts/spec-dock sync`
  - mirror diff / inspection evidence.
  - `./spec-dock/scripts/spec-dock validate`
- doc update owner:
  - doc-writer for any missing shipped docs/template/skill text changes.
- spec/doc review:
  - reviewer: spec-reviewer.
  - pass 条件: requirement / design / plan / provider assets / dogfooding mirror rationale align.

### S99 — final quality gate
- branch diff 範囲:
  - active issue docs.
  - provider docs/templates/installed assets.
  - tests.
  - dogfooding mirror if refreshed.
- 必須 validation:
  - `uv run python -m unittest tests.test_init_update`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
  - `git status --short --branch`
- final QA gate:
  - reviewer: qa-reviewer.
  - 範囲: obligation coverage, structural test adequacy, docs-only / inspect-only evidence validity.
  - pass 条件: reviewer pass.
- final code review ゲート:
  - reviewer: code-reviewer.
  - 範囲: issue-wide integrated diff, tests, mirror update mechanics, maintainability.
  - pass 条件: review_status pass.
- final spec review ゲート:
  - reviewer: spec-reviewer.
  - 範囲: requirement / design / plan / report / implementation / tests / docs alignment.
  - pass 条件: reviewer pass.
- final commit gate:
  - commit 範囲:
    - final report ledger and any fixes from final gates.
  - post-commit external evidence:
    - final response and PR / issue comment if created later.

## 最終完了条件
- AC/EC 達成:
  - AC-001 through AC-007 and EC-001 through EC-004 are closed in report.
- docs 影響解決:
  - S90 pass with sync and mirror evidence.
- 全 implementation step 完了:
  - S01-S04 committed or approved-no-op with rationale.
- final quality gate pass:
  - qa-reviewer pass.
  - issue-wide code-reviewer pass.
  - spec-reviewer pass.
- final commit 完了:
  - final report ledger committed.
- 必須 closure id 完了:
  - tc-001 through tc-007 closed in Step Contract Closure / Test Contract Closure / Closure Coverage.
- final clean state:
  - no unintended staged / unstaged changes.
- required sync / validate evidence:
  - `./spec-dock/scripts/spec-dock sync` and `./spec-dock/scripts/spec-dock validate` results are recorded in report before `issue finish`.

## 未確定事項
- 現時点で、実装着手を止める未確定事項はない。
