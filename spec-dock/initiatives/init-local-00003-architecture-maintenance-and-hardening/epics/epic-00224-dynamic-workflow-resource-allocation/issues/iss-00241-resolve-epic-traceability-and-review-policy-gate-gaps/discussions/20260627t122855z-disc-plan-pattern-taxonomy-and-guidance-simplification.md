---
種別: discussion
ID: "20260627t122855z-disc"
タイトル: "plan pattern taxonomy and guidance simplification"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-27"
親: ["iss-00241"]
関連:
  - "20260627t114637z-disc"
  - "20260627t121356z-disc"
authority: "synthesized"
derived_from:
  - "oracle: gpt-5.5-pro extended via chatgpt-use"
  - "user decision: support plan-centric issue execution model"
reflected_to: []
---

# plan pattern taxonomy and guidance simplification

## 位置づけ
- この artifact は、plan-centric issue execution model を具体化するための追加設計ディスカッションである。
- 主な関心は以下の 2 点である。
  - Issue planning 時に、レビュー / QA / 品質ゲート / resource allocation をどのように再現よく `plan.md` へ作り込むか。
  - plan-centric 化に伴い、`guidance issue-execution` から何を削り、何を残すべきか。
- `chatgpt-use` skill により Oracle CLI browser mode で GPT-5.5 Pro Extended に分析を依頼し、その回答をローカル文脈へ統合した。

## 結論
- `Lite` / `Standard` / `Strict` / `Critical` は単独 taxonomy ではなく、Issue 全体の「既定品質プロファイル」として使う。
- 実際の step ごとの review / QA / resource allocation は、artifact type、change risk、evidence level、reviewer gate を組み合わせた Step-level Obligation Pattern として `plan.md` に明示する。
- `plan.md` は executable workflow contract、`report.md` は audit/evidence ledger、`guidance issue-execution` は readiness / consistency preflight に限定する。
- `selected_step`、`report.md` completion parsing、runtime worker/reviewer inference、context packet auto generation は follow-up で削除または deprecated にする。

## 二層 taxonomy

### Issue-level Quality Profile

| Profile | 意味 | default stance |
| --- | --- | --- |
| Lite | 低リスク・局所・可逆・観測容易 | no review ではない。step pattern 側で review 要否を決める。 |
| Standard | 通常の product / runtime / docs issue | 迷ったら Standard。artifact type mapping に従う。 |
| Strict | integration / migration / workflow policy / broad asset 変更 | rollback、compatibility、QA を明記する。 |
| Critical | security / privacy / permission / destructive / high blast radius | explicit risk acceptance なしに downgrade しない。 |

### Step-level Obligation Pattern

| Pattern | 典型対象 | worker allocation | required evidence | required review / QA | 使ってよい条件 |
| --- | --- | --- | --- | --- | --- |
| NoReview-ReadOnly | 状態確認、no-op 判定、差分なし確認 | parent inspect のみ | exact checked files、diff clean、no-op reason、report evidence | なし。ただし no review justification 必須。 | canonical artifact / code / docs / template / workflow の変更がなく、durable decision を残さない。 |
| SpecOnly | docs-only、template text、skill text、workflow text、plan amendment | doc-writer | docs inspection、source alignment、必要なら validate | spec-reviewer pass | runtime / code / tests / scaffold behavior を変更しない。 |
| CodeReview | runtime、CLI、tests、scaffold behavior | dev-coder | unit / behavior command、pre-implementation evidence | code-reviewer pass | public behavior または implementation 変更が step-local に閉じる。 |
| CodePlusSpec | code と docs/spec の両方、provider assets と dogfood workspace の両方 | 原則 split。不可なら dev-coder + doc-writer。 | unit / integration / docs inspection / traceability | code-reviewer + spec-reviewer pass | split 不能な bounded change。review focus を plan に明記する。 |
| QA | bug fix、integration risk、regression risk、acceptance coverage risk | dev-coder + QA review | characterization / regression / integration evidence | qa-reviewer + 必要な code/spec reviewer | test sufficiency が issue success の主要リスク。 |
| StrictGate | migration、rollback、filesystem/GitHub/active state、cross-module workflow、compatibility | delegated worker 必須 | rollback / migration / compatibility / integration evidence | code-reviewer + qa-reviewer。docs 影響があれば spec-reviewer。 | failure blast radius が中〜高、戻し手順や互換性が必要。 |
| CriticalGate | auth/authz、permissions、secret/privacy/security、destructive/external publishing、本番相当影響 | specialist があれば追加。worker delegation 必須。 | security/privacy review evidence、negative/adversarial cases、rollback/containment | code-reviewer + qa-reviewer + spec-reviewer。必要なら specialist。 | under-review を許容できない変更。 |

## NoReview-ReadOnly の安全条件
- `NoReview-ReadOnly` は「軽い変更」ではなく、変更がない、または canonical/product artifact に durable effect がない場合に限定する。
- 必須 justification:
  - Change class: read-only / approved-no-op / report-only orchestration evidence。
  - Mutated files: none / report.md only。
  - Canonical artifact impact: none。
  - Product behavior impact: none。
  - Spec / plan / closure index impact: none。
  - Commands checked: `git diff -- ...`、`git status --short` など。
  - Why reviewer adds no signal: no product/spec/docs contract changed。
  - Escalation condition: canonical artifact、shipped docs/template/skill/workflow、runtime、test、scaffold、closure id、locked expectation、durable decision の変更があれば review 必須。

## Issue planning checklist
- Planning agent は step を書く前に以下を明示する。

| Question | Decision output |
| --- | --- |
| この issue は observable behavior を何個の behavior slice に分けられるか | step count / dependency order |
| 変更 artifact は何か | code, tests, docs, template, skill, workflow, runtime, provider asset, dogfood workspace |
| `design.md` の dependency diagram / directory tree と step 順は一致するか | upstream-first order |
| 受け入れ条件 / edge conditions / closure id はどの step で閉じるか | Spec-Locked Closure Index |
| Red / characterization / inspection のどれで pre-implementation evidence を取るか | evidence mode |
| Green verification は 1 step 1 command で観測可能か | command / evidence path |
| docs impact はあるか。ない場合の確認対象は何か | S90 docs impact decision |
| final issue-wide QA/code/spec review は必要か | S99 final gate |
| worker は誰か | dev-coder, doc-writer, parent exception, read-only |
| reviewer は誰か | none, code-reviewer, spec-reviewer, qa-reviewer, specialist |
| delegation boundary は明確か | allowed / forbidden paths, stop conditions |
| rollback / migration / compatibility は必要か | Strict escalation |
| security/privacy/permission/secret/authz は関係するか | Critical escalation |
| external systems / GitHub / filesystem / active state に影響するか | Strict escalation |
| provider source and local dogfood workspace の同期が必要か | source-of-truth + validation scope |
| no review を主張する場合、差分なしまたは report-only と証明できるか | no review justification |

## Default rules
- Default は `Standard`。
- runtime / code / tests 変更は、低リスクそうに見えても `CodeReview` を要求する。
- docs / template / skill / workflow text は `SpecOnly`。ただし workflow policy に影響する場合は `StrictGate` に上げる。
- code + docs は原則 step split。split できない場合だけ `CodePlusSpec`。
- bug / unknown failure は最初の step に diagnosis / characterization loop を固定する。
- S90 docs impact と S99 final quality gate は原則 plan に置く。
- reviewer / worker availability は pass の代替にしない。

## Escalation triggers

| Trigger | Minimum escalation |
| --- | --- |
| auth/authz, permissions, credentials, secrets, privacy | CriticalGate |
| migration, rollback, schema, checked-in state rewrite | StrictGate |
| GitHub, filesystem, active state, lifecycle command behavior | StrictGate |
| provider assets under `src/spec_dock/assets/...` と dogfood `spec-dock/` の両方に影響 | CodePlusSpec or StrictGate |
| shared workflow policy / template / skill semantics | StrictGate + spec-reviewer |
| cross-module / cross-package / broad refactor | StrictGate |
| acceptance criteria の test sufficiency が不明 | QA |
| unresolved requirement/design/plan gap | execution 禁止、planning/clarification に戻す |
| no review に canonical artifact 変更が含まれる | reject no review; reviewer 必須 |
| report ledger に durable decision が残る | design/ADR/plan amendment/follow-up へ昇格、または issue-local disposition |

## `plan.md` structure proposal

```markdown
---
種別: 実装計画書（Issue）
ID: "iss-xxxxx"
タイトル: "..."
状態: "approved"
依存: ["requirement.md", "design.md"]
quality_profile: "Standard"
plan_contract_version: "issue-plan-contract-v1"
---

# iss-xxxxx ... — 実装計画

## 0. Plan Authority

- Source of truth: this `plan.md`
- Evidence ledger: `report.md`
- Execution order: steps are executed top-to-bottom unless plan amendment is approved.
- Runtime guidance is preflight only; it must not select a step or reduce obligations.
- Any change to required closure id, locked expectation, required evidence level, or reviewer gate requires plan amendment + fresh spec review.

## 1. Quality Profile Decision

| Field | Decision |
|---|---|
| Profile | Standard |
| Reason | ... |
| Downgrade rejected | ... |
| Escalation triggers present | ... |
| Required final gates | S90 docs impact, S99 final QA/code/spec |

## 2. Risk / Resource Allocation Matrix

| Surface / Risk | Present? | Consequence | Pattern |
|---|---:|---|---|
| runtime/code/tests | yes | code-reviewer required | CodeReview |
| docs/template/skill/workflow | yes/no | spec-reviewer required if yes | SpecOnly / CodePlusSpec |
| migration/rollback | no | escalate if yes | StrictGate |
| auth/privacy/security | no | escalate if yes | CriticalGate |
| external / GitHub / filesystem / active state | no | escalate if yes | StrictGate |

## 3. Spec-Locked Closure Index

| ID | Spec link | Observable input/state | Locked expectation | Defect prevented | Required? | Evidence level | Owner step |
|---|---|---|---|---|---:|---|---|
| C01 | AC-1 | ... | ... | ... | yes | unit / docs / integration | S01 |

## 4. Implementation Steps

### S01 — <observable behavior slice>

<Use the step template below.>

### S90 — Docs Impact Resolution

- Pattern: SpecOnly / NoReview-ReadOnly
- Docs checked:
  - ...
- Docs changes planned:
  - ...
- Verification:
  - ...
- Reviewer gate:
  - spec-reviewer pass, or no-review justification if truly no docs impact

### S99 — Final Quality Gate

- Pattern: StrictGate
- QA gate:
  - qa-reviewer verifies test sufficiency and integration need.
- Issue-wide code review:
  - code-reviewer verifies integrated diff.
- Final spec review:
  - spec-reviewer verifies requirement / design / plan / report / docs alignment.
- Final report evidence:
  - report sections to update.
- Final commit boundary:
  - final report / delivery evidence only; no catch-up implementation diff.

## 5. Amendment Triggers

- Unplanned file/path change.
- Closure index change.
- Reviewer gate change.
- Test evidence cannot be produced as planned.
- New security/privacy/migration/external-system risk.
- Requirement/design contradiction.
```

## `plan.md` step template

```markdown
### Sxx — <one observable behavior>

- Behavior goal:
  - <観測可能な振る舞いを 1 つに絞る>

- Source contract:
  - Requirement links:
    - AC-...
    - EC-...
  - Design links:
    - Section ...
  - Closure IDs:
    - C...

- Quality / allocation:
  - Issue profile: Standard
  - Step pattern: CodeReview / SpecOnly / CodePlusSpec / QA / StrictGate / CriticalGate / NoReview-ReadOnly
  - Pattern reason:
    - <risk と artifact type に基づく理由>
  - Escalation triggers:
    - present: ...
    - absent but checked: ...

- Scope:
  - Allowed paths:
    - ...
  - Forbidden paths:
    - ...
  - Provider / dogfood sync:
    - provider source:
    - local consumer validation:

- Delegation:
  - Worker: dev-coder / doc-writer / parent-read-only / approved-local-execution
  - Worker scope:
    - ...
  - Worker required output:
    - summary
    - changed files
    - verification result
    - Ledger Note or `No material implementation decisions beyond the approved plan.`

- Pre-implementation evidence:
  - Mode: expected-red / characterization-pass / docs-inspection / no-op-inspection
  - Command or evidence path:
    - ...
  - Test sensitivity / inspection rationale:
    - ...

- Implementation batch:
  - Minimal changes:
    - ...
  - Refactor guardrail:
    - no broad refactor unless ...

- Green verification:
  - Primary command:
    - `...`
  - Required evidence in report.md:
    - Step Contract Closure
    - Test Contract Closure
    - Closure Coverage

- Review / QA gates:
  - code-reviewer: required / not required — reason
  - spec-reviewer: required / not required — reason
  - qa-reviewer: required / not required — reason
  - no review justification:
    - only if Pattern = NoReview-ReadOnly

- Step close:
  - Close state: committed / approved-no-op
  - Step Commit Gate:
    - 1 step = 1 review scope = 1 commit
  - Post-commit clean check:
    - `git status --short`

- Stop / amendment triggers:
  - ...
```

## `guidance issue-execution` に残す責務

| Responsibility | Keep? | 理由 |
| --- | ---: | --- |
| active issue があるか確認 | yes | entrypoint preflight |
| requirement / design / plan / report の存在確認 | yes | execution readiness |
| artifact が template-only / scaffold / unresolved でないか確認 | yes | execution 禁止条件 |
| freshness / reviewer-pass / assurance authority の確認 | yes | start gate |
| executable `plan.md` の粗い contract lint | yes | non-executable plan を planning gap として block |
| command reminders を出す | yes | UX |
| stop conditions を出す | yes | safety |
| projected runbook を human/debug output として保存 | optional | 現行互換。ただし authority ではない |
| plan.md を読むよう促す | yes | plan-centric 方針 |
| selected step を決める | no | second source of truth になる |
| report.md から completed step を推論 | no | report は証跡であって control plane ではない |
| worker / reviewer / verification を runtime inference | no | planning-time contract と衝突 |
| context packet 自動生成 | no by default | step selection と reviewer inference に依存するため |
| `reasoning_effort` / `context_mode` を自動決定 | no | runtime policy engine 化を避ける |

## 削除 / deprecate 対象

| Current element | Recommendation |
| --- | --- |
| `selected_step` | deprecated -> remove from markdown stdout -> remove from JSON in next major contract |
| `_select_step` | remove |
| `_completed_step_ids` / report completion parsing | remove |
| `_classify_task_kind` from plan free text | remove |
| runtime worker inference | remove |
| runtime reviewer inference | remove |
| runtime verification inference | remove |
| context packet generation coupled to selected step | remove or move to explicit `--step Sxx` utility later |
| tests asserting S01/S02 dynamic selection | rewrite to assert no selection / plan-centric guidance |
| context routing policy for issue-execution | retire or move to explicit delegation tooling |

## simplified stdout contract

```markdown
# Guidance: issue-execution

- state: ready
- next_action: execute-approved-plan
- reason_code: execution-preflight-pass
- active_issue: iss-xxxxx
- contract_source: spec-dock/active/issue/plan.md
- evidence_ledger: spec-dock/active/issue/report.md
- authority:
  - authorized_profile: strict
  - obligation_source: authorized_profile
  - lite_candidate: false

## Readiness

- active issue: pass
- requirement.md: present, non-template, reviewer-pass/fresh
- design.md: present, non-template, reviewer-pass/fresh
- plan.md: present, executable contract, reviewer-pass/fresh
- report.md: present, evidence ledger
- plan contract lint: pass
- unresolved gap check: pass

## Commands

- `./spec-dock/scripts/spec-dock active show`
- `./spec-dock/scripts/spec-dock validate`
- `./spec-dock/scripts/spec-dock sync`

## Execution Contract

- Read `spec-dock/active/issue/plan.md` top-to-bottom.
- Execute exactly one current step from `plan.md`.
- Worker, reviewer, QA, verification, closure IDs, no-op rules, and amendment triggers come from `plan.md`.
- Record observed evidence in `report.md`.
- Do not use this guidance output as a step selector.
- Do not reduce review / QA obligations based on runtime inference.

## Stop Conditions

- Any artifact is missing, stale, template-only, unresolved, or not reviewer-passed.
- `plan.md` lacks executable steps or required step fields.
- `plan.md` and `design.md` dependency order conflict.
- Required closure IDs are not traceable to step close conditions.
- Reviewer / QA / delegation requirements cannot be verified.
- Implementation reveals a requirement/design/plan gap.
```

## simplified JSON contract

```json
{
  "schema_version": "workflow-runbook-v2",
  "workflow_target": "issue-execution",
  "state": "ready",
  "next_action": "execute-approved-plan",
  "reason_code": "execution-preflight-pass",
  "active_issue_id": "iss-xxxxx",
  "contract_source": "spec-dock/active/issue/plan.md",
  "evidence_ledger": "spec-dock/active/issue/report.md",
  "authority": {
    "authorized_profile": "strict",
    "lite_candidate": false,
    "obligation_source": "authorized_profile"
  },
  "readiness": {
    "requirement": "pass",
    "design": "pass",
    "plan": "pass",
    "report": "present",
    "plan_contract_lint": "pass"
  },
  "commands": [
    "./spec-dock/scripts/spec-dock active show",
    "./spec-dock/scripts/spec-dock validate",
    "./spec-dock/scripts/spec-dock sync"
  ],
  "notes": [
    "plan.md is the execution contract",
    "report.md is the evidence ledger",
    "guidance issue-execution does not select steps or infer reviewers"
  ],
  "stop_conditions": []
}
```

## `iss-00241` で今やるべきこと
- 既存 PR を destabilize しないため、runtime 全面再設計は入れない。
- 現在の PR では以下に絞る。
  - `plan.md = executable workflow contract`、`report.md = evidence ledger`、`guidance issue-execution = preflight only` という方針を docs / report / skill に反映する。
  - `selected_step` がある場合でも authority として依存しないよう、execution skill の文面を弱める。
  - planning-time pattern selection は follow-up design gap として明記する。
  - legacy output を残す場合でも deprecated / non-authoritative として扱う。

## follow-up Issue に送るべきこと
- planning-time taxonomy / checklist / `plan.md` step template を docs に追加する。
- issue plan template / compose guidance に Quality Profile + Step Pattern を追加する。
- `guidance issue-execution` stdout / JSON v2 contract を導入する。
- default markdown output から `Step Assurance` / `Context Packets` を削除する。
- `_select_step`、`_completed_step_ids`、`_classify_task_kind`、dynamic task-kind routing を削除する。
- context packet generation は削除、または明示 `--step Sxx` 入力を要求する別 command に分離する。
- current tests を plan-centric contract tests に置換する。
- legacy JSON compatibility が必要なら、明示 opt-in に限定する。

## compatibility policy

| Existing issue / plan | Behavior during transition |
| --- | --- |
| 新規 / 更新中 plan | new schema を要求 |
| legacy plan with executable steps | warning: legacy plan contract; execution allowed if fields are sufficiently explicit |
| legacy plan without review/verification fields | planning-required |
| current `step_assurance` consumers | deprecated field retained temporarily, but markdown tells agents not to rely on it |
| existing completed report evidence | audit evidence として尊重。ただし step selection には使わない |
| old issues missing report ledger sections | grandfathered。更新時だけ backfill / migration |

## Tests / manual validation

### planning-time tests
- docs-only step -> `SpecOnly`, `doc-writer`, `spec-reviewer`, docs inspection。
- runtime + tests step -> `CodeReview`, `dev-coder`, `code-reviewer`, unit/behavior command。
- code + docs mixed step -> split required or `CodePlusSpec` with both reviewers。
- security/authz/privacy step -> `CriticalGate`, security/privacy evidence, code + QA + spec review。
- migration / rollback step -> `StrictGate`, rollback plan, integration/compat evidence。
- no-review read-only step -> accepted only with no diff, no canonical impact, explicit justification。
- no-review with canonical docs/code change -> rejected。
- provider source + dogfood workspace change -> plan requires source-of-truth and validation scope。
- closure id missing owner step -> plan review fails。
- S90 missing -> plan review fails unless explicitly waived by policy。
- S99 missing -> plan review fails。

### plan contract tests
- Every implementation step has `Behavior goal`。
- Every step has exactly one primary observable verification command or evidence path。
- Every required closure id appears in the Closure Index and in a step close contract。
- Every step declares `Step pattern`。
- Every step declares worker allocation。
- Every step declares reviewer / QA gates or no-review justification。
- Every step declares allowed / forbidden paths。
- Every step declares report evidence destination。
- Any `NoReview-ReadOnly` step with planned file mutation fails lint。
- Any step changing both runtime and docs without split or `CodePlusSpec` fails lint。
- S90 and S99 exist and are independent。
- No placeholder fields remain。

### simplified guidance tests
- no active issue -> `state=no-active`, `next_action=issue-start-required`。
- scaffold requirement/design/plan -> blocked / planning required。
- missing fresh reviewer evidence -> classification/planning required。
- executable approved plan -> `state=ready`, no `selected_step`, no `step_assurance`, no `context_packets` by default。
- report says S01-S99 complete -> output does not change based on report parsing。
- report has misleading scaffold step rows -> output does not infer completion。
- plan lacks structured steps -> planning required。
- dirty worktree -> readiness warning/block if policy requires, but no context-mode inference。
- invalid context-routing-policy -> irrelevant to default issue-execution guidance after removal。
- JSON schema v2 -> contains readiness, contract_source, evidence_ledger, commands, stop_conditions only。

## failure modes to guard
- Runtime guidance selects wrong step -> remove selection; plan is contract。
- `report.md` becomes control plane -> guidance never parses report for next step。
- under-review due to Lite profile -> Lite is only profile; step pattern still maps artifact/risk to reviewer。
- over-review on read-only/no-op work -> `NoReview-ReadOnly` with strict justification。
- mixed code/docs step hides reviewer need -> split or `CodePlusSpec`。
- security words in forbidden scope trigger false escalation -> planning checklist distinguishes present risk vs forbidden/non-goal risk。
- security/authz present but not escalated -> escalation trigger forces `CriticalGate`。
- reviewer unavailable treated as pass -> blocked / incomplete unless explicit policy and risk acceptance; not pass。
- durable decision trapped in report -> promote to design/ADR/plan/follow-up or issue-local disposition。
- provider and dogfood copies diverge -> step scope requires both source-of-truth and local validation target。
- final QA used as substitute for step review -> S99 cannot replace per-step gate。

## Oracle session
- tool: `npx -y @steipete/oracle --engine browser`
- project: Codex-only ChatGPT Project
- model: `gpt-5.5-pro`
- thinking time: `extended`
- session: `spec-dock-plan-patterns-guidance`
- dry run token estimate: about 42.1k prompt tokens, 11 bundled files
- result: completed successfully
