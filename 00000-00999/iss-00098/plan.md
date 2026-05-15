---
種別: 実装計画書（Issue）
ID: "iss-00098"
タイトル: "Delegated Implementation Orchestration Contract"
関連GitHub: ["#98"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-05-15"
依存: ["requirement.md", "design.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00098 Delegated Implementation Orchestration Contract — 計画

## この計画で満たす要件ID

- AC-001: Parent Agent Invariant / 親 Codex の通常責務と direct implementation guardrail
- AC-002: plan step の delegation contract 必須項目
- AC-003: delegated worker handoff 必須項目
- AC-004: reviewer gate fail condition と role mapping
- AC-005: Parent Implementation Exception record
- AC-006: report delegation evidence / reviewer verdict / parent integration decision
- EC-001: worker unavailable / denied / host policy conflict の blocked / incomplete / waiver semantics
- EC-002: orchestration metadata と shipped docs/templates/skills/workflow text の direct update 境界
- EC-003: 複数 layer / package / shipped asset step の delegated worker handoff
- EC-004: reviewer fail 後の bounded follow-up delegation

## 依存関係から導く実装順序

1. `workflow_issue.md` を upstream execution policy として先に固定する。
2. plan authoring docs と plan template は、固定済み policy を consumption surface として取り込む。
3. report template は evidence / exception policy の記録面だけを取り込む。
4. issue-execution skill は concise reminder として canonical docs 参照を更新する。
5. provider source の確定後、dogfooding mirror を同期する。
6. `tests/test_init_update.py` で generated / mirrored structural content を固定する。
7. S90 docs impact と S99 final quality gate で、docs drift と issue-wide quality を閉じる。

## ステップ一覧

| Step | Scope | Delegated role | Reviewer gate | Primary closure |
| --- | --- | --- | --- | --- |
| S10 | workflow execution policy provider doc | `doc-writer` | `spec-reviewer` | C01, C02, C03, C07, C08 |
| S20 | plan authoring docs and plan template provider sources | `doc-writer` | `spec-reviewer` | C04, C05, C06 |
| S30 | report template provider source | `doc-writer` | `spec-reviewer` | C09, C10, C11 |
| S40 | issue-execution skill provider source | `doc-writer` | `spec-reviewer` | C12, C13 |
| S50 | dogfooding mirror synchronization | `doc-writer` | `spec-reviewer` | C14 |
| S60 | init/update structural assertions | `dev-coder` | `code-reviewer` | C15 |
| S90 | docs impact resolution / docs refresh | `doc-writer` | `spec-reviewer` | C16 |
| S99 | final quality gate | parent orchestrator | `qa-reviewer`, issue-wide `code-reviewer`, `spec-reviewer` | C17 |

## 要件 ↔ ステップ対応

| Requirement | Steps |
| --- | --- |
| AC-001 | S10, S40, S50, S60, S99 |
| AC-002 | S20, S50, S60, S99 |
| AC-003 | S10, S40, S50, S60, S99 |
| AC-004 | S10, S30, S50, S60, S99 |
| AC-005 | S10, S30, S50, S60, S99 |
| AC-006 | S30, S50, S60, S99 |
| EC-001 | S10, S30, S40, S50, S99 |
| EC-002 | S10, S40, S99 |
| EC-003 | S10, S20, S99 |
| EC-004 | S10, S40, S99 |

## Spec-Locked Closure Index

| id | phase / step | slice | type | spec link | locked expectation | observable input/state | bug class guarded | required | evidence level | closure evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C01 | S10 | workflow policy source | docs | AC-001, design `Parent Agent Invariant` | `workflow_issue.md` owns Parent Agent Invariant and limits parent Codex to inspect / plan / delegate / verify / integrate / report in normal execution. | Provider doc contains the invariant and normal responsibility list. | Parent Codex silently becomes direct implementer. | yes | inspect-only | S10 docs diff and spec-reviewer pass |
| C02 | S10 | delegated worker handoff | docs | AC-003, EC-003 | `workflow_issue.md` defines handoff fields: delegated role, scope, source of truth, allowed changes, forbidden changes, required verification, stop conditions, output required. | Provider doc contains all handoff field names. | Worker handoff omits scope or verification boundary. | yes | inspect-only | S10 docs diff and S60 assertion |
| C03 | S10 | parent exception | docs | AC-005, EC-001 | `workflow_issue.md` defines Parent Implementation Exception fields and states that unavailable / denied / host conflict does not automatically permit direct implementation. | Provider doc contains exception fields and waiver semantics. | Degraded mode is treated as reviewer pass or direct-write approval. | yes | inspect-only | S10 docs diff and S60 assertion |
| C04 | S20 | phase plan consumer | docs | AC-002, design plan responsibility | `phase_plan_issue.md` consumes `workflow_issue.md` policy and tells authors how to write delegation contracts without redefining execution policy. | Provider phase doc references `workflow_issue.md` and required step fields. | Downstream plan doc drifts into alternate policy source. | yes | inspect-only | S20 docs diff |
| C05 | S20 | authoring entrypoint consumer | docs | AC-002 | `docs/authoring/issue-plan.md` names required plan sections and all step delegation fields. | Provider authoring doc contains required sections and field list. | Plan authors miss required delegation evidence. | yes | inspect-only | S20 docs diff |
| C06 | S20 | plan template scaffold | template | AC-002 | Plan template contains Spec-Locked Closure Index, step-local `具体テストケース一覧`, step closure contract, behavior slice execution, step gate, and delegation contract fields. | Provider template has reusable scaffold sections and field names. | New issue plans remain implementation-ambiguous. | yes | covered-existing | S20 template diff and S60 assertion |
| C07 | S10 | reviewer gate mapping | docs | AC-004, EC-004 | `workflow_issue.md` maps code / runtime / tests / scaffold behavior to per-step `code-reviewer`, docs-only / template-only / skill-text-only to `spec-reviewer`, and reviewer fail to delegated follow-up. | Provider workflow doc contains gate mapping and fail semantics. | Wrong reviewer gate passes an unsuitable diff. | yes | inspect-only | S10 docs diff |
| C08 | S10 | orchestration metadata boundary | docs | EC-002 | `workflow_issue.md` distinguishes run-local orchestration metadata from shipped docs/templates/skills/workflow text. | Provider workflow doc names allowed parent metadata and delegated shipped assets. | Parent direct-edits shipped assets as metadata. | yes | inspect-only | S10 docs diff |
| C09 | S30 | report delegation evidence | template | AC-006 | Report template requires step id, delegated role, delegated worker summary, changed files, verification, reviewer verdict, unresolved risks, parent integration decision. | Provider report template contains evidence table or fields. | Completed issue cannot prove delegated implementation. | yes | covered-existing | S30 template diff and S60 assertion |
| C10 | S30 | report exception record | template | AC-005, EC-001 | Report template includes Parent Implementation Exception fields and risk acceptance / reviewer gate state. | Provider report template contains all exception fields. | Direct implementation exception is unreviewed or underdocumented. | yes | covered-existing | S30 template diff and S60 assertion |
| C11 | S30 | report consumes policy | template | design report responsibility | Report template records evidence and exceptions while referring to `workflow_issue.md` as policy source. | Provider report template avoids becoming alternate execution policy. | Report template conflicts with workflow policy. | yes | inspect-only | S30 spec-reviewer pass |
| C12 | S40 | skill concise reminder | skill | AC-001, AC-003 | Issue-execution skill reminds parent invariant, role routing, docs source of truth, stop conditions, and does not duplicate full policy. | Provider skill is concise and links/refers to canonical docs. | Skill becomes stale policy fork. | yes | covered-existing | S40 skill diff and S60 assertion |
| C13 | S40 | skill stop conditions | skill | EC-001, EC-004 | Skill reminds that unavailable/denied delegation and reviewer fail are stop / re-delegation conditions, not success. | Provider skill contains stop-condition reminders. | Agent proceeds after failed reviewer or unavailable worker. | yes | inspect-only | S40 skill diff |
| C14 | S50 | provider/mirror parity | mirror | non-negotiable design constraint | Dogfooding mirror files under `spec-dock/` and `.agents/` carry the provider source changes. | Mirror files contain the same structural headings/fields as provider sources. | Dogfooding uses stale behavior while provider source changed. | yes | inspect-only | S50 parity check |
| C15 | S60 | regression assertions | tests | design test strategy | `tests/test_init_update.py` asserts key structural content for workflow docs, plan template, report template, skill, and mirror generation. | Targeted pytest passes after adding structural assertions; pre-implementation evidence is characterization of existing test coverage, not failing-first. | Future init/update drops contract fields silently. | yes | covered-existing | `uv run pytest tests/test_init_update.py` |
| C16 | S90 | docs impact closure | docs | workflow_issue S90 | Changed docs/templates/skill have consistent references and no unresolved docs impact remains. | Docs impact list is recorded; needed docs edits are complete or no-op is justified. | Contract references break or drift after local edits. | yes | inspect-only | S90 docs/spec alignment pass |
| C17 | S99 | final quality gate | final | workflow_issue S99 | Final qa-reviewer, issue-wide code-reviewer, and spec-reviewer gates pass; closure evidence is complete. | Final report can cite tests, reviews, changed files, and clean scope. | Step-local pass hides issue-wide regression. | yes | manual-required | S99 final gate evidence |

## 実装ステップ

### S10 - Workflow execution policy provider doc

- depends on: approved `requirement.md`, approved `design.md`
- unblocks: S20, S30, S40, S50, S60
- design refs: `Parent Agent Invariant`, `Delegated Worker Handoff`, `Reviewer Gate Mapping`, `Parent Implementation Exception`, `Report Evidence`
- target files:
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`

#### delegation contract

- delegated role: `doc-writer`
- input docs: `spec-dock/active/issue/requirement.md`, `spec-dock/active/issue/design.md`, `spec-dock/docs/workflow_issue.md`, `spec-dock/docs/workflow_spec_authoring.md`
- allowed paths: `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- forbidden changes: dogfooding mirror files, templates, skill files, tests, Python runtime source, active issue `requirement.md` / `design.md` / `report.md`
- acceptance criteria: provider `workflow_issue.md` is the upstream execution policy source and contains Parent Agent Invariant, delegated worker handoff, reviewer gate mapping, Parent Implementation Exception, unavailable/denied/waiver semantics, orchestration metadata boundary, and reviewer-fail re-delegation rule.
- required tests or docs-only verification: docs-only verification against AC-001, AC-003, AC-004, AC-005, EC-001, EC-002, EC-003, EC-004; no automated test in this step.
- reviewer focus: `workflow_issue.md` owns policy; no downstream docs/templates/skills are edited in this step.
- stop conditions: required policy cannot be added without contradicting `workflow_spec_authoring.md`; approved design appears insufficient; provider source path is not readable.
- output required: changed section summary, closure evidence for C01/C02/C03/C07/C08, docs-only verification notes.

#### 具体テストケース一覧

- `tc-s10-001` docs-only: Parent Agent Invariant is canonical
  - 前提: provider `workflow_issue.md` is the execution policy source.
  - 操作: Inspect the changed provider doc.
  - 期待結果: Parent Codex normal responsibilities are limited to inspect / plan / delegate / verify / integrate / report, and direct implementation of shipped assets is not normal execution.
  - 失敗検出: Parent direct implementation remains allowed as an unrecorded normal path.
  - 検証方法: docs-only inspection recorded in report.
  - 関連 closure id: C01
- `tc-s10-002` docs-only: delegated worker handoff and exception fields are complete
  - 前提: AC-003 and AC-005 field names are fixed by requirement/design.
  - 操作: Inspect delegated worker handoff and Parent Implementation Exception sections.
  - 期待結果: All required handoff and exception fields are present, and unavailable/denied/waiver semantics do not imply reviewer pass.
  - 失敗検出: Missing field, degraded success wording, or direct implementation auto-approval.
  - 検証方法: docs-only inspection recorded in report.
  - 関連 closure id: C02, C03
- `tc-s10-003` docs-only: reviewer mapping is explicit
  - 前提: Step types include docs/template/skill and code/runtime/tests/scaffold behavior.
  - 操作: Inspect reviewer gate mapping and reviewer fail handling.
  - 期待結果: docs-only/template-only/skill-text-only maps to `spec-reviewer`; code/runtime/tests/scaffold behavior maps to `code-reviewer`; reviewer fail returns to bounded delegated follow-up.
  - 失敗検出: Wrong reviewer is sufficient for a step type or parent fixes failed review directly without exception.
  - 検証方法: docs-only inspection recorded in report.
  - 関連 closure id: C07, C08

#### step closure contract

- closure ids: C01, C02, C03, C07, C08
- close when: all target policy sections are present in provider `workflow_issue.md`, docs-only verification passes, and `spec-reviewer` passes.
- test bundle: docs-only inspection cases `tc-s10-001` through `tc-s10-003`.
- pre-implementation evidence: characterization pass by reading current `workflow_issue.md` and confirming existing `Implementation Delegation Gate` does not yet satisfy all iss-00098 fields.
- verification evidence: diff excerpt and spec-reviewer verdict in `report.md`.
- report evidence: Step Contract Closure rows for C01/C02/C03/C07/C08.
- residual risk: exact prose may evolve during review, but source-of-truth ownership must not change.

#### behavior slice execution

1. Read current provider `workflow_issue.md` and active requirement/design.
2. Add only the missing delegated-by-default policy sections.
3. Verify field names and gate semantics against requirement AC/EC.
4. Request `spec-reviewer` docs/spec alignment review.
5. Close S10 only after reviewer pass or stop with blocker.

#### step gate

- `spec-reviewer gate`: required pass for docs/spec alignment.
- commit gate: one S10 commit after pass.
- no-op gate: allowed only if provider doc already contains all C01/C02/C03/C07/C08 content and report records inspected sections.
- report update: record docs-only verification, reviewer verdict, and closure IDs.

### S20 - Plan authoring docs and plan template provider sources

- depends on: S10
- unblocks: S50, S60
- design refs: `Plan Step Delegation Contract`, directory / file change plan
- target files:
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/plan.md`

#### delegation contract

- delegated role: `doc-writer`
- input docs: active requirement/design, S10 changed `workflow_issue.md`, current target files, dogfooding `spec-dock/docs/phase_plan_issue.md`, `spec-dock/docs/authoring/issue-plan.md`
- allowed paths: the three S20 target files only
- forbidden changes: `workflow_issue.md`, report template, skill files, tests, dogfooding mirrors, Python runtime source, active issue `requirement.md` / `design.md` / `report.md`
- acceptance criteria: phase and authoring docs consume `workflow_issue.md`; plan template contains Spec-Locked Closure Index, step-local `具体テストケース一覧`, step closure contract, behavior slice execution, step gate, and every delegation contract field.
- required tests or docs-only verification: docs-only verification now; structural assertions are added in S60.
- reviewer focus: no alternate execution policy is introduced; template remains reusable and not iss-00098-specific.
- stop conditions: template source is generated from a different source; required sections cannot fit without breaking existing template contract.
- output required: changed section summary, closure evidence for C04/C05/C06, docs-only verification notes.

#### 具体テストケース一覧

- `tc-s20-001` docs-only: plan docs consume workflow policy
  - 前提: S10 made `workflow_issue.md` the policy source.
  - 操作: Inspect provider `phase_plan_issue.md` and `docs/authoring/issue-plan.md`.
  - 期待結果: They reference/consume `workflow_issue.md` and describe how to author delegation contracts without redefining execution policy.
  - 失敗検出: The docs introduce conflicting cadence, reviewer semantics, or exception policy.
  - 検証方法: docs-only inspection recorded in report.
  - 関連 closure id: C04, C05
- `tc-s20-002` docs-only: plan template has all required step fields
  - 前提: AC-002 field list is fixed.
  - 操作: Inspect provider `templates/issue/plan.md`.
  - 期待結果: Each implementation step scaffold includes delegated role, input docs, allowed paths, forbidden changes, acceptance criteria, required tests or docs-only verification, reviewer focus, stop conditions, and output required.
  - 失敗検出: Future plan authors can omit delegation boundaries or verification.
  - 検証方法: docs-only inspection now; S60 adds automated structural assertion.
  - 関連 closure id: C06
- `tc-s20-003` docs-only: plan template includes required execution sections
  - 前提: `phase_plan_issue.md` requires step-local concrete test cases and closure contracts.
  - 操作: Inspect provider plan template headings.
  - 期待結果: Spec-Locked Closure Index, `具体テストケース一覧`, step closure contract, behavior slice execution, and step gate are present.
  - 失敗検出: Template permits global tests only or omits step-local gate.
  - 検証方法: docs-only inspection now; S60 adds automated structural assertion.
  - 関連 closure id: C06

#### step closure contract

- closure ids: C04, C05, C06
- close when: S20 target files contain the required consumer guidance and plan scaffold, docs-only verification passes, and `spec-reviewer` passes.
- test bundle: docs-only cases `tc-s20-001` through `tc-s20-003`.
- pre-implementation evidence: characterization pass by inspecting current plan docs/template and recording missing AC-002 field coverage.
- verification evidence: diff excerpt and spec-reviewer verdict.
- report evidence: Step Contract Closure rows for C04/C05/C06.
- residual risk: S60 may tighten exact strings for testability; any wording-only adjustment stays within S20 contract.

#### behavior slice execution

1. Read S10 policy and current provider plan docs/template.
2. Update provider plan docs as policy consumers.
3. Update provider plan template with required scaffold sections and fields.
4. Verify the template is reusable and not iss-00098-specific.
5. Request `spec-reviewer` and close only on pass.

#### step gate

- `spec-reviewer gate`: required pass for docs/template alignment.
- commit gate: one S20 commit after pass.
- no-op gate: allowed only if all C04/C05/C06 expectations already exist.
- report update: record docs-only verification and reviewer verdict.

### S30 - Report template provider source

- depends on: S10
- unblocks: S50, S60
- design refs: `Report Evidence`, `Parent Implementation Exception`
- target files:
  - `src/spec_dock/assets/spec_dock/templates/issue/report.md`

#### delegation contract

- delegated role: `doc-writer`
- input docs: active requirement/design, S10 changed `workflow_issue.md`, current report template
- allowed paths: `src/spec_dock/assets/spec_dock/templates/issue/report.md`
- forbidden changes: workflow docs, plan docs, plan template, skill files, tests, dogfooding mirrors, Python runtime source, active issue `requirement.md` / `design.md` / `plan.md`
- acceptance criteria: report template captures delegation evidence, reviewer verdict, parent integration decision, unresolved risks, Parent Implementation Exception, and waiver/unavailable/denied semantics while referring to `workflow_issue.md` as policy source.
- required tests or docs-only verification: docs-only verification now; structural assertions are added in S60.
- reviewer focus: evidence scaffold does not become an alternate execution policy.
- stop conditions: report template structure cannot accept required evidence without broad report workflow redesign.
- output required: changed section summary and closure evidence for C09/C10/C11.

#### 具体テストケース一覧

- `tc-s30-001` docs-only: delegation evidence fields are complete
  - 前提: AC-006 field list is fixed.
  - 操作: Inspect provider report template delegation evidence section.
  - 期待結果: step id, delegated role, worker summary, changed files, verification, reviewer verdict, unresolved risks, and parent integration decision can be recorded.
  - 失敗検出: Completed reports cannot reconstruct delegated work or parent integration judgment.
  - 検証方法: docs-only inspection now; S60 adds automated structural assertion.
  - 関連 closure id: C09
- `tc-s30-002` docs-only: Parent Implementation Exception is recordable
  - 前提: AC-005 and EC-001 define exception and waiver fields.
  - 操作: Inspect provider report template exception section.
  - 期待結果: delegation unavailable reason, user approval / risk acceptance, allowed files, allowed operation, rollback plan, post-change verification, and reviewer gate are recordable.
  - 失敗検出: Parent direct implementation can occur without full exception evidence.
  - 検証方法: docs-only inspection now; S60 adds automated structural assertion.
  - 関連 closure id: C10
- `tc-s30-003` docs-only: report remains evidence surface
  - 前提: `workflow_issue.md` owns execution policy.
  - 操作: Inspect report template wording.
  - 期待結果: The template points to policy and records evidence; it does not redefine reviewer pass, waiver, or delegation semantics.
  - 失敗検出: Report template conflicts with S10 policy wording.
  - 検証方法: docs-only inspection and spec-reviewer review.
  - 関連 closure id: C11

#### step closure contract

- closure ids: C09, C10, C11
- close when: provider report template contains required evidence and exception fields, docs-only verification passes, and `spec-reviewer` passes.
- test bundle: docs-only cases `tc-s30-001` through `tc-s30-003`.
- pre-implementation evidence: characterization pass by inspecting current report template evidence gaps.
- verification evidence: diff excerpt and spec-reviewer verdict.
- report evidence: Step Contract Closure rows for C09/C10/C11.
- residual risk: S60 may require stable labels for assertions; wording can be adjusted without changing policy.

#### behavior slice execution

1. Read S10 policy and current provider report template.
2. Add evidence and exception recording surfaces only.
3. Verify template references policy rather than owning it.
4. Request `spec-reviewer`.
5. Close on pass.

#### step gate

- `spec-reviewer gate`: required pass.
- commit gate: one S30 commit after pass.
- no-op gate: allowed only if C09/C10/C11 already exist.
- report update: record docs-only verification and reviewer verdict.

### S40 - Issue-execution skill provider source

- depends on: S10
- unblocks: S50, S60
- design refs: skill responsibility and concise reminder policy
- target files:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`

#### delegation contract

- delegated role: `doc-writer`
- input docs: active requirement/design, S10 changed `workflow_issue.md`, current provider skill, dogfooding mirror skill
- allowed paths: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
- forbidden changes: workflow docs, templates, tests, dogfooding mirrors, Python runtime source, active issue `requirement.md` / `design.md` / `report.md`
- acceptance criteria: skill concisely reminds parent invariant, role routing, canonical docs, stop conditions, unavailable/denied/waiver semantics, and reviewer-fail re-delegation without duplicating full workflow policy.
- required tests or docs-only verification: docs-only verification now; structural assertion added in S60 if current tests cover installed skill content.
- reviewer focus: concise reminder only; no policy fork.
- stop conditions: skill source is generated externally or missing from provider assets.
- output required: changed reminder summary and closure evidence for C12/C13.

#### 具体テストケース一覧

- `tc-s40-001` docs-only: skill stays concise and canonical-doc driven
  - 前提: `workflow_issue.md` owns policy.
  - 操作: Inspect provider issue-execution skill.
  - 期待結果: Skill points executors to canonical docs and summarizes role routing without embedding full policy.
  - 失敗検出: Skill duplicates long policy text or contradicts workflow docs.
  - 検証方法: docs-only inspection now; S60 assertion if supported.
  - 関連 closure id: C12
- `tc-s40-002` docs-only: skill stop conditions are explicit
  - 前提: EC-001 and EC-004 require stop/re-delegation semantics.
  - 操作: Inspect skill reminders for unavailable/denied delegation and reviewer fail.
  - 期待結果: Skill tells parent Codex to stop or re-delegate, not treat these states as success.
  - 失敗検出: Agent proceeds after unavailable worker or failed reviewer.
  - 検証方法: docs-only inspection.
  - 関連 closure id: C13

#### step closure contract

- closure ids: C12, C13
- close when: provider skill contains concise reminders and stop conditions, docs-only verification passes, and `spec-reviewer` passes.
- test bundle: docs-only cases `tc-s40-001` and `tc-s40-002`.
- pre-implementation evidence: characterization pass by inspecting current skill for missing delegated-by-default reminder fields.
- verification evidence: diff excerpt and spec-reviewer verdict.
- report evidence: Step Contract Closure rows for C12/C13.
- residual risk: brevity is subjective; reviewer focus is source-of-truth consistency and absence of full policy duplication.

#### behavior slice execution

1. Read S10 policy and provider skill.
2. Update only concise reminder bullets/sections.
3. Verify canonical docs remain the source of truth.
4. Request `spec-reviewer`.
5. Close on pass.

#### step gate

- `spec-reviewer gate`: required pass.
- commit gate: one S40 commit after pass.
- no-op gate: allowed only if C12/C13 already exist.
- report update: record docs-only verification and reviewer verdict.

### S50 - Dogfooding mirror synchronization

- depends on: S10, S20, S30, S40
- unblocks: S60, S90, S99
- design refs: provider/mirror non-negotiable constraint
- target files:
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/phase_plan_issue.md`
  - `spec-dock/docs/authoring/issue-plan.md`
  - `spec-dock/templates/issue/plan.md`
  - `spec-dock/templates/issue/report.md`
  - `.agents/skills/spec-dock-issue-execution/SKILL.md`

#### delegation contract

- delegated role: `doc-writer`
- input docs: changed provider sources from S10-S40, current dogfooding mirror files, active requirement/design
- allowed paths: the six S50 target files only
- forbidden changes: provider sources, tests, Python runtime source, active issue `requirement.md` / `design.md` / `report.md`
- acceptance criteria: dogfooding mirror files contain the same structural sections/fields as provider sources; any intentional mirror difference is recorded with reason.
- required tests or docs-only verification: provider/mirror structural parity inspection; automated generation assertions added in S60.
- reviewer focus: synchronization without broad unrelated formatting churn.
- stop conditions: mirror path cannot be matched to provider source; synchronization requires a generator that changes paths outside S50 allowed paths.
- output required: parity summary and closure evidence for C14.

#### 具体テストケース一覧

- `tc-s50-001` docs-only: workflow and plan docs mirror provider structure
  - 前提: S10 and S20 provider docs are complete.
  - 操作: Compare provider docs to dogfooding `spec-dock/docs/...` mirrors for required headings/fields.
  - 期待結果: Mirror docs include the same source-of-truth role split, delegation contract fields, and plan authoring requirements.
  - 失敗検出: Dogfooding docs are stale or conflict with provider docs.
  - 検証方法: docs-only parity inspection.
  - 関連 closure id: C14
- `tc-s50-002` docs-only: templates and skill mirror provider structure
  - 前提: S30 and S40 provider template/skill changes are complete.
  - 操作: Compare provider plan/report templates and skill to dogfooding mirrors for required structural content.
  - 期待結果: Mirror plan/report/skill contain required sections and fields.
  - 失敗検出: New scaffold behavior differs from dogfooding behavior.
  - 検証方法: docs-only parity inspection.
  - 関連 closure id: C14

#### step closure contract

- closure ids: C14
- close when: all six mirror files are synchronized structurally, parity verification passes, and `spec-reviewer` passes.
- test bundle: docs-only cases `tc-s50-001` and `tc-s50-002`.
- pre-implementation evidence: characterization pass by listing provider/mirror target pairs.
- verification evidence: parity notes and spec-reviewer verdict.
- report evidence: Step Contract Closure row for C14.
- residual risk: exact provider/mirror byte-for-byte equality may not be required if existing mirror conventions differ; structural parity is required.

#### behavior slice execution

1. List provider-to-mirror pairs.
2. Apply provider structural changes to dogfooding mirrors.
3. Inspect each pair for required headings/fields.
4. Request `spec-reviewer`.
5. Close on pass.

#### step gate

- `spec-reviewer gate`: required pass.
- commit gate: one S50 commit after pass.
- no-op gate: allowed only if all mirror files already match required structure.
- report update: record mirror paths and parity evidence.

### S60 - Init/update structural assertions

- depends on: S10, S20, S30, S40, S50
- unblocks: S90, S99
- design refs: test strategy
- target files:
  - `tests/test_init_update.py`

#### delegation contract

- delegated role: `dev-coder`
- input docs: active requirement/design, changed provider and mirror files from S10-S50, `tests/test_init_update.py`
- allowed paths: `tests/test_init_update.py`
- forbidden changes: docs, templates, skills, Python runtime source, generated artifacts, active issue `requirement.md` / `design.md` / `report.md`
- acceptance criteria: targeted assertions cover workflow policy fields, plan template required sections/fields, report evidence/exception fields, concise skill reminder, and provider/mirror generated structural content.
- required tests or docs-only verification: `uv run pytest tests/test_init_update.py`
- reviewer focus: assertions should check stable structural contract, not incidental long prose.
- stop conditions: tests require runtime changes outside approved scope; fixtures reveal generated output path drift not covered by design.
- output required: test names added/changed, pytest result, closure evidence for C15.

#### 具体テストケース一覧

- `tc-s60-001` regression: plan template structural contract is asserted
  - 前提: S20 provider plan template and S50 mirror are updated.
  - 操作: Run targeted init/update tests.
  - 期待結果: Tests assert `Spec-Locked Closure Index`, `具体テストケース一覧`, step closure contract, behavior slice execution, step gate, and all delegation contract fields.
  - 失敗検出: Future scaffold drops a required plan section or field.
  - 検証方法: `uv run pytest tests/test_init_update.py`
  - 関連 closure id: C06, C15
- `tc-s60-002` regression: report evidence and exception contract is asserted
  - 前提: S30 provider report template and S50 mirror are updated.
  - 操作: Run targeted init/update tests.
  - 期待結果: Tests assert delegation evidence fields and Parent Implementation Exception fields.
  - 失敗検出: Future report scaffold cannot record AC-005 or AC-006 evidence.
  - 検証方法: `uv run pytest tests/test_init_update.py`
  - 関連 closure id: C09, C10, C15
- `tc-s60-003` regression: workflow/skill source-of-truth roles are asserted
  - 前提: S10 provider workflow doc and S40 provider skill are updated.
  - 操作: Run targeted init/update tests.
  - 期待結果: Tests assert workflow source-of-truth role markers and concise skill reminder markers.
  - 失敗検出: Skill becomes policy fork or workflow policy fields disappear.
  - 検証方法: `uv run pytest tests/test_init_update.py`
  - 関連 closure id: C01, C12, C15

#### step closure contract

- closure ids: C15
- close when: `tests/test_init_update.py` contains structural assertions and targeted pytest passes.
- test bundle: regression cases `tc-s60-001` through `tc-s60-003`.
- pre-implementation evidence: characterization pass by running or inspecting existing tests before changes, or documenting why red-first is not applicable for docs/template asset tests.
- verification evidence: `uv run pytest tests/test_init_update.py` output.
- report evidence: Test Contract Closure and Closure Coverage rows for C15 and linked closure ids.
- residual risk: assertions cannot prove every prose nuance; they lock required structural content.

#### behavior slice execution

1. Inspect existing test helper style in `tests/test_init_update.py`.
2. Add minimal structural assertions for changed assets.
3. Run targeted pytest.
4. Fix assertion overfitting if tests are brittle.
5. Request `code-reviewer` for test diff.

#### step gate

- `code-reviewer gate`: required pass because this step changes tests.
- commit gate: one S60 commit after pass.
- no-op gate: allowed only if existing tests already assert all C15 content.
- report update: record pytest output and reviewer verdict.

### S90 - Docs impact resolution / docs refresh

- depends on: S10-S60
- unblocks: S99
- design refs: S90 standard docs impact gate
- target files:
  - No edits by default.
  - If changed docs introduce a broken or missing reference, only the directly impacted docs index/cross-reference file may be edited after recording the reason.

#### delegation contract

- delegated role: `doc-writer`
- input docs: all changed files from S10-S60, `spec-dock/docs/workflow_spec_authoring.md`, `spec-dock/docs/phase_plan_issue.md`, active requirement/design/plan
- allowed paths: no edits by default; directly impacted docs index/cross-reference files only if required
- forbidden changes: Python runtime source, tests, templates, skills, unrelated docs, active issue `requirement.md` / `design.md` / `report.md`
- acceptance criteria: docs impact is resolved; no stale links, role-split conflicts, or policy/source-of-truth drift remain.
- required tests or docs-only verification: docs-only link/path/reference inspection; `spec-reviewer` docs/spec alignment pass.
- reviewer focus: changed surfaces remain consistent with approved requirement/design/plan and `workflow_spec_authoring.md`.
- stop conditions: resolving docs impact requires broad docs restructuring or edits outside allowed paths.
- output required: impacted-docs list, no-op or changed-path summary, closure evidence for C16.

#### 具体テストケース一覧

- `tc-s90-001` docs-only: changed references are consistent
  - 前提: S10-S60 changes are complete.
  - 操作: Inspect changed docs/templates/skill for references to canonical docs, provider/mirror roles, reviewer gates, and report evidence.
  - 期待結果: References are valid and no changed surface contradicts another.
  - 失敗検出: Broken link, stale role description, or duplicated policy source.
  - 検証方法: docs-only inspection plus `spec-reviewer` pass.
  - 関連 closure id: C16
- `tc-s90-002` docs-only: docs impact no-op is justified when no edit is needed
  - 前提: No broken references or drift are found.
  - 操作: Record inspected paths and no-op reason.
  - 期待結果: Report explains why no additional docs edit is needed.
  - 失敗検出: Docs impact is skipped without inspected-path evidence.
  - 検証方法: report evidence and `spec-reviewer` pass.
  - 関連 closure id: C16

#### step closure contract

- closure ids: C16
- close when: docs impact list is complete, required docs fixes are done or no-op is justified, and `spec-reviewer` passes.
- test bundle: docs-only cases `tc-s90-001` and `tc-s90-002`.
- pre-implementation evidence: inspect changed paths from S10-S60.
- verification evidence: docs impact notes and spec-reviewer verdict.
- report evidence: S90 docs impact section in report.
- residual risk: none expected; broad docs restructuring is out of scope and must stop.

#### behavior slice execution

1. Review changed files and references.
2. Decide whether docs impact is no-op or requires a narrow cross-reference edit.
3. If edit is required, edit only allowed docs reference path.
4. Request `spec-reviewer`.
5. Close on pass.

#### step gate

- `spec-reviewer gate`: required pass.
- commit gate: one S90 commit if edits are made; otherwise approved-no-op evidence.
- no-op gate: allowed with inspected-path evidence.
- report update: record impacted docs and reviewer verdict.

### S99 - Final quality gate

- depends on: S90
- unblocks: issue completion report and final handoff
- design refs: S99 standard final quality gate
- target files:
  - No edits by default.
  - `spec-dock/active/issue/report.md` may be updated by the parent orchestrator as run-local orchestration metadata during execution.

#### delegation contract

- delegated role: parent orchestrator for integration; reviewer roles are `qa-reviewer`, issue-wide `code-reviewer`, and `spec-reviewer`
- input docs: active requirement/design/plan/report, all changed files, S60 test output, S90 docs impact evidence
- allowed paths: no product/doc/template/skill/test edits in this step; report metadata only during actual execution
- forbidden changes: provider sources, mirrors, tests, runtime source, active issue `requirement.md` / `design.md` / `plan.md`
- acceptance criteria: all closure IDs C01-C17 have evidence, `uv run pytest tests/test_init_update.py` passes, `git diff --check` passes, final `qa-reviewer`, issue-wide `code-reviewer`, and `spec-reviewer` pass.
- required tests or docs-only verification: `git diff --check`; `uv run pytest tests/test_init_update.py`; final reviewer gates.
- reviewer focus: issue-wide integration, test sufficiency, source-of-truth role split, provider/mirror parity, complete report evidence.
- stop conditions: any closure ID lacks evidence; any required reviewer is unavailable/denied/failed without explicit blocked/incomplete handling; tests fail.
- output required: final changed-file list, commands/results, reviewer verdicts, closure index status, remaining risks.

#### 具体テストケース一覧

- `tc-s99-001` quality: targeted tests and diff hygiene pass
  - 前提: S10-S90 are closed.
  - 操作: Run `git diff --check` and `uv run pytest tests/test_init_update.py`.
  - 期待結果: Both commands pass.
  - 失敗検出: Whitespace errors or structural asset regression remain.
  - 検証方法: command output recorded in report/final response.
  - 関連 closure id: C15, C17
- `tc-s99-002` quality: final reviewer gates pass
  - 前提: All implementation step reviews have passed or valid no-op evidence exists.
  - 操作: Run final `qa-reviewer`, issue-wide `code-reviewer`, and `spec-reviewer`.
  - 期待結果: All three final reviewers pass fresh.
  - 失敗検出: Step-local review missed test insufficiency, integration risk, or spec mismatch.
  - 検証方法: reviewer verdicts recorded in report.
  - 関連 closure id: C17
- `tc-s99-003` quality: closure ledger is complete
  - 前提: S10-S90 report evidence exists.
  - 操作: Inspect closure index C01-C17 against report evidence.
  - 期待結果: Every required closure has evidence and no unresolved question remains.
  - 失敗検出: Issue is reported complete with missing closure evidence.
  - 検証方法: final report closure review.
  - 関連 closure id: C17

#### step closure contract

- closure ids: C17 plus final confirmation of C01-C16
- close when: tests pass, diff hygiene passes, all final reviewers pass, closure ledger is complete, and unexpected modified files are absent.
- test bundle: quality cases `tc-s99-001` through `tc-s99-003`.
- pre-implementation evidence: all previous step closure evidence exists.
- verification evidence: command outputs and reviewer verdicts.
- report evidence: final quality gate and final exit contract.
- residual risk: none accepted without explicit blocked/incomplete report.

#### behavior slice execution

1. Confirm S10-S90 closure evidence.
2. Run final commands.
3. Run final reviewer gates.
4. Resolve any reviewer failure by returning to the appropriate delegated step, not by direct unrecorded fix.
5. Close only after all final gates pass.

#### step gate

- `qa-reviewer gate`: required pass for test sufficiency and integration test need.
- issue-wide `code-reviewer gate`: required pass for integrated diff.
- `spec-reviewer gate`: required pass for requirement/design/plan/report/docs alignment.
- commit gate: final report/final commit handled by execution workflow after pass.
- no-op gate: not applicable for final quality gate.
- report update: record final commands, reviewer verdicts, closure ledger, and remaining risks.

## Review / QA Gate 方針

- Docs-only, template-only, and skill-text-only steps use `spec-reviewer` as the step reviewer.
- Test changes use `code-reviewer` as the step reviewer.
- S99 always runs `qa-reviewer`, issue-wide `code-reviewer`, and `spec-reviewer`; final reviews do not replace step reviews.
- Required reviewer gate success means fresh `passed` only. `waived`, `provisional`, `unavailable`, `denied`, and `failed` are not pass states.
- Reviewer failure is handled by bounded follow-up delegation to the appropriate worker unless a recorded Parent Implementation Exception is approved.

## Final Exit Contract

The issue can proceed from plan to implementation when:

- This plan has fresh `spec-reviewer` pass.
- Every implementation step has concrete target files, delegation contract, concrete test cases, closure contract, behavior slice execution, and step gate.
- Provider source and dogfooding mirror updates are both planned.
- S90 and S99 are present and decision-complete.
- No unresolved questions or placeholders remain.

The implementation can be reported complete only when:

- Closure IDs C01-C17 have evidence.
- S10-S60 step reviews pass and each step is committed or valid approved-no-op.
- S90 docs impact is resolved.
- S99 final quality gate passes.
- `report.md` records command evidence, reviewer evidence, delegation evidence, parent integration decisions, and any residual risks.
