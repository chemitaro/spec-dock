---
種別: research
ID: "20260522t231450z-03-research"
タイトル: "ChatGPT Pro deep analysis for delegated authoring architecture"
状態: "completed"
作成者: "ChatGPT Pro via Codex Chrome delegation"
最終更新: "2026-05-23"
親: ["epic-00112"]
関連: ["GitHub #112"]
authority: "external-analysis"
derived_from:
  - "ChatGPT thread https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a1035c6-bbc4-83a9-b2b7-75f48f9c0886"
  - "20260522t120437z-research-delegated-authoring-source-architecture-report.md"
  - "20260522t120437z-01-research-consultant-analysis-delegated-authoring-rollout.md"
  - "20260522t120437z-02-disc-epic-slicing-recommendation-delegated-authoring.md"
reflected_to: []
---

# epic-00112 Delegated Authoring Architecture — External analysis memo

## Source basis

本メモは、添付された epic-00112 分析依頼の文脈だけを根拠にする。添付4点は内容上同一の分析依頼として扱った。   

現行前提として、`requirement.md` は main orchestrator + human が所有し、`design.md` draft は `system-architect`、`plan.md` draft は `implementation-planner` が一次作成してよい。ただし canonical artifact ownership、user dialogue、canonical integration、phase promotion、report evidence は main orchestrator が持ち続け、delegated draft は spec-reviewer pass の代替ではない。

---

## Executive conclusion

初期 Epic の核心は、**サブエージェントを追加することではなく、「delegated authoring は authority ではなく auditable draft evidence である」と workflow contract に固定すること**である。

現状リサーチの方向性は正しい。ただし、このまま Epic requirement/design/plan に落とすと失敗しやすい箇所がある。特に不足しているのは次の4点。

1. **delegated draft の lifecycle contract**

   * draft がいつ valid / stale / integrated / rejected / superseded / blocked になるのかが未定義。
   * これが曖昧だと、古い draft が canonical design/plan の根拠として残り続ける。

2. **role skill と host adapter の単一責務境界**

   * `spec-dock-system-architect` / `spec-dock-implementation-planner` と `.codex/agents/*.toml` の間で instruction duplication が起きると drift する。
   * 初期 Epic では role skill を正本、`.codex/agents` は thin adapter に限定すべき。

3. **spec-reviewer の delegated draft 用 review criterion**

   * reviewer が draft を「参考資料」と見るのか、「canonical artifact の一部」と見るのかが曖昧。
   * reviewer は delegated draft そのものを pass するのではなく、**canonical artifact が delegated draft を安全に統合したか**を review する必要がある。

4. **report evidence の構造**

   * 現行 report には Spec Authoring Gate として investigated facts / open questions / delegation consent / reviewer / verdict / fixes / promotion を残す前提があるが、delegated authoring 専用の provenance・scope・consent・integration result が未定義。

推奨スコープは、**draft-only delegated authoring の契約・role skill・Codex thin adapter・phase gate・report evidence・dogfooding pilot** まで。
非スコープは、**write-capable delegation、runtime validation、role registry、本格的な multi-host support、`.github/agents` / Copilot agent、GitHub issue 更新、実装コード編集**である。添付文脈でも、初期 Epic では canonical docs の直接編集を delegated author に許可しない想定であり、GitHub issue close/update、destructive command、implementation code editing は範囲外とされている。

---

## Missing information / questions for human

以下は requirement/design/plan 作成を止める不明点ではない。Epic 内では default decision を置き、必要なら後続 issue で修正可能にするべきである。

### Must decide before requirement finalization

| ID     | Missing decision                                       | Recommended default                              | Why it matters                                                         |
| ------ | ------------------------------------------------------ | ------------------------------------------------ | ---------------------------------------------------------------------- |
| MQ-001 | delegated draft を chat-only にするか、`discussions/` に保存するか | `discussions/` に structured draft artifact として保存 | chat-only だと reviewer / future maintainer / dogfooding metrics が追跡できない |
| MQ-002 | delegation consent の粒度                                 | `node + phase + role + artifact` 単位              | workflow-wide blanket consent は write-capable への誤拡張を誘発する               |
| MQ-003 | `.codex/agents` を含めるか                                  | include, but thin adapter only                   | role を実際に呼べないと dogfooding が弱い。ただし正本 instruction は skill 側に置く           |
| MQ-004 | `.github/agents` / Copilot agent を含めるか                 | exclude                                          | multi-host 対応は drift と検証範囲を増やす                                         |
| MQ-005 | report evidence schema の厳密度                            | Markdown structured block with required fields   | JSON schema / runtime validation は初期 Epic では過剰                         |
| MQ-006 | pilot の合格基準                                            | metrics + stop criteria を Epic plan に明記          | 将来 write-capable へ進める判断材料になる                                           |

### Can defer to later Epic / issue

| ID     | Deferred question                                  | Reason                                       |
| ------ | -------------------------------------------------- | -------------------------------------------- |
| DQ-001 | scoped write-capable delegation の allowed paths    | 初期 Epic は draft-only で十分                     |
| DQ-002 | role registry / runtime enforcement                | 初期は docs/skills contract で検証可能               |
| DQ-003 | host-specific model / reasoning effort enforcement | host に依存するため、contract では hint に留める           |
| DQ-004 | automated staleness detection                      | 初期は report evidence と reviewer criterion で十分 |
| DQ-005 | GitHub issue automation                            | delegated authoring roles の非スコープにすべき         |

---

## Recommended Epic scope

## In scope

### S-001: Authoring workflow policy

`workflow_spec_authoring.md` に以下を追加する。

* canonical artifact ownership
* delegated authoring と reviewer / read-only specialist の違い
* draft-only delegation の許可条件
* previous-phase artifact mutation prohibition
* phase promotion は fresh spec-reviewer pass が必須であること
* delegated draft が reviewer pass の代替ではないこと

現行 authoring workflow は `requirement -> fresh spec-reviewer pass -> design -> fresh spec-reviewer pass -> plan -> fresh spec-reviewer pass -> downstream handoff` を正本契約としており、reviewer missing/stale/failed/unavailable/denied/waived/provisional は promotion を block/incomplete にする前提がある。

### S-002: Delegated draft artifact lifecycle

`discussions/` に structured draft artifact を保存する契約を入れる。

推奨 path:

```text
spec-dock/active/{initiative|epic|issue}/discussions/
  delegated-design-system-architect-{seq}.md
  delegated-plan-implementation-planner-{seq}.md
```

`{seq}` は初期実装では `001`, `002` などで十分。timestamp や hash は将来拡張でよい。

### S-003: Role skill assets

Provider-first で shipped role skill を追加する。

```text
src/spec_dock/assets/agents/skills/spec-dock-system-architect/SKILL.md
src/spec_dock/assets/agents/skills/spec-dock-implementation-planner/SKILL.md
```

実際の provider path は未検証であるため、Codex 側で既存 asset layout に合わせて調整すること。

### S-004: Codex host thin adapter

`.codex/agents` は初期 Epic に含めてよい。ただし、**canonical instruction を重複させない**。

```text
.codex/agents/system-architect.toml
.codex/agents/implementation-planner.toml
```

中身は role name、description、skill pointer、draft-only boundary、model/effort hint 程度に限定する。

### S-005: Phase gate and report evidence

`phase_design.md` / `phase_plan.md` / `phase_plan_issue.md` / report guidance に delegated authoring gate を追加する。

現行 design phase は requirement の WHAT/WHY を HOW/guardrails に落とし、方針、境界/契約、SoR/依存、依存関係分析、移行、観測性、テスト戦略を固定する責務を持つ。plan phase は確定済み requirement/design を実行可能な分解・順序・停止点・品質ゲートへ変換し、trace できない step/issue/epic は scope creep とされる。

### S-006: Dogfooding pilot

dogfooding workspace で draft-only delegated authoring を実地検証する。

検証対象は、少なくとも以下を含める。

* Epic-level design draft
* Issue-level design draft
* Issue-level plan draft
* delegated draft evidence in report
* spec-reviewer review
* stale / blocked / rejected の少なくとも1ケース

---

## Out of scope

| ID     | Non-scope                                                                       | Reason                                        |
| ------ | ------------------------------------------------------------------------------- | --------------------------------------------- |
| NS-001 | delegated author による canonical `requirement.md` / `design.md` / `plan.md` の直接編集 | 初期 Epic は draft-only                          |
| NS-002 | implementation code editing                                                     | authoring role の責務外                           |
| NS-003 | GitHub issue close/update                                                       | 外部副作用を増やす                                     |
| NS-004 | destructive command                                                             | authoring role に不要                            |
| NS-005 | `.github/agents` / Copilot agent                                                | host-specific drift が大きい                      |
| NS-006 | scoped write-capable delegation                                                 | pilot metrics 後に判断                            |
| NS-007 | runtime role registry / validation                                              | 初期 Epic では docs/skills contract で足りる          |
| NS-008 | automated diff application                                                      | canonical integration は main orchestrator が所有 |
| NS-009 | model selection enforcement                                                     | host adapter hint に留める                        |
| NS-010 | full structured JSON schema                                                     | Markdown structured block で十分                 |

---

## Proposed E-RQ / E-AC list

### E-RQ-001: Canonical artifact ownership invariant

**Requirement**
The main orchestrator remains the owner of canonical authoring artifacts, user dialogue, canonical integration, phase promotion, and report evidence.

**Acceptance criteria**

* **E-AC-001-A**: `workflow_spec_authoring.md` states that delegated authors cannot own or promote canonical artifacts.
* **E-AC-001-B**: `requirement.md` remains owned by main orchestrator + human.
* **E-AC-001-C**: delegated design/plan drafts are explicitly classified as source material / evidence, not authority.
* **E-AC-001-D**: phase promotion still requires fresh `spec-reviewer` `review_status: pass`.

### E-RQ-002: Draft-only delegated authoring mode

**Requirement**
The initial Epic shall permit only draft-only authoring delegation for `design.md` and `plan.md`.

**Acceptance criteria**

* **E-AC-002-A**: delegated authoring roles are forbidden from directly modifying canonical docs.
* **E-AC-002-B**: delegated authoring roles are forbidden from editing implementation code.
* **E-AC-002-C**: delegated authoring roles are forbidden from GitHub issue close/update and destructive command.
* **E-AC-002-D**: any delegated output must be integrated by main orchestrator before becoming canonical.

### E-RQ-003: Delegation consent and scope contract

**Requirement**
Delegated authoring invocation must record explicit scope, role, phase, artifact, allowed actions, forbidden actions, and output expectation.

**Acceptance criteria**

* **E-AC-003-A**: consent is recorded per `node + phase + role + artifact`.
* **E-AC-003-B**: workflow-wide blanket consent is not sufficient for delegated authoring roles.
* **E-AC-003-C**: invocation contract includes allowed read scope and forbidden write/action scope.
* **E-AC-003-D**: missing consent blocks delegated authoring use, but does not block manual authoring.

### E-RQ-004: Delegated design authoring contract

**Requirement**
`system-architect` may produce a `design.md` draft only after requirement phase gate prerequisites are satisfied.

**Acceptance criteria**

* **E-AC-004-A**: design delegation requires fresh reviewer-pass `requirement.md`.
* **E-AC-004-B**: `system-architect` must not change or reinterpret requirement scope.
* **E-AC-004-C**: unresolved requirement gaps must be returned as `Requirement Clarification Request`.
* **E-AC-004-D**: design draft must map design decisions to requirement IDs or requirement sections.
* **E-AC-004-E**: design draft must include boundaries/contracts, dependencies, SoR/dependency analysis, migration/compatibility if relevant, observability if relevant, test strategy, and ADR candidates.

### E-RQ-005: Delegated plan authoring contract

**Requirement**
`implementation-planner` may produce a `plan.md` draft only after requirement and design phase gate prerequisites are satisfied.

**Acceptance criteria**

* **E-AC-005-A**: plan delegation requires fresh reviewer-pass `requirement.md` and `design.md`.
* **E-AC-005-B**: `implementation-planner` must not introduce new design decisions.
* **E-AC-005-C**: unresolved design gaps must be returned as `Plan Blocked`.
* **E-AC-005-D**: every plan item must trace to a requirement item or design decision.
* **E-AC-005-E**: plan draft must include implementation order, dependency reasoning, test/review gates, rollback/compatibility notes where relevant, docs impact, and final quality gate.

### E-RQ-006: Draft artifact lifecycle

**Requirement**
Delegated drafts must have an auditable lifecycle independent from canonical artifacts.

**Acceptance criteria**

* **E-AC-006-A**: delegated draft artifacts support statuses: `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`.
* **E-AC-006-B**: draft artifact metadata records role, phase, scope, input artifacts, source snapshot, output status, and integration result.
* **E-AC-006-C**: if source requirement/design changes after draft production, the draft becomes `stale` until reviewed or regenerated.
* **E-AC-006-D**: stale drafts cannot be used as promotion evidence without explicit reconciliation.

### E-RQ-007: Report evidence integration

**Requirement**
`report.md` must record delegated authoring evidence when delegated draft is used.

**Acceptance criteria**

* **E-AC-007-A**: report records role, phase, scope, consent, source artifacts, draft artifact path, integration result, rejected portions, blockers, reviewer result, and promotion decision.
* **E-AC-007-B**: report distinguishes delegated draft production from canonical integration.
* **E-AC-007-C**: report can show that delegated draft was not used, was partially used, or was rejected.
* **E-AC-007-D**: missing delegated evidence blocks promotion only when the canonical artifact claims delegated authoring was used.

### E-RQ-008: Independent spec-reviewer treatment

**Requirement**
`spec-reviewer` shall review canonical artifacts and delegated evidence without treating delegated drafts as pass substitutes.

**Acceptance criteria**

* **E-AC-008-A**: reviewer checks that canonical design/plan still satisfies normal phase criteria.
* **E-AC-008-B**: reviewer checks that delegated draft did not bypass requirement/design gates.
* **E-AC-008-C**: reviewer checks that all integrated delegated content is traceable to approved previous-phase artifacts.
* **E-AC-008-D**: reviewer fails or blocks promotion if delegated draft creates scope creep, unapproved design decisions, or hidden requirement assumptions.
* **E-AC-008-E**: reviewer records delegated authoring findings separately from ordinary artifact findings.

### E-RQ-009: Provider-first and dogfooding parity

**Requirement**
Shipped docs/skills must be provider-first, with dogfooding workspace kept in parity.

**Acceptance criteria**

* **E-AC-009-A**: canonical role skill assets are stored under provider assets.
* **E-AC-009-B**: dogfooding workspace copies are generated or synchronized from provider assets.
* **E-AC-009-C**: implementation includes a validation step that detects provider/consumer drift, or explicitly records manual parity verification.
* **E-AC-009-D**: dogfooding pilot uses the shipped assets, not ad hoc local prompts.

### E-RQ-010: Host adapter boundary

**Requirement**
Host-specific agent definitions may provide callable entry points but must not duplicate canonical role instructions.

**Acceptance criteria**

* **E-AC-010-A**: `.codex/agents/system-architect.toml` and `.codex/agents/implementation-planner.toml`, if added, are thin adapters.
* **E-AC-010-B**: host adapter points to role skill or names it as canonical behavior source.
* **E-AC-010-C**: host adapter contains no expanded copy of the full role contract.
* **E-AC-010-D**: `.github/agents` / Copilot agent support is explicitly non-scope for this Epic.

### E-RQ-011: Failure mode handling

**Requirement**
Delegated authoring must define explicit behavior for common failures.

**Acceptance criteria**

* **E-AC-011-A**: missing consent → do not invoke delegated author; continue manual path.
* **E-AC-011-B**: missing/stale reviewer pass → block delegated design/plan invocation.
* **E-AC-011-C**: requirement gap during design → `Requirement Clarification Request`.
* **E-AC-011-D**: design gap during plan → `Plan Blocked`.
* **E-AC-011-E**: role unavailable → manual authoring remains valid if existing gates pass.
* **E-AC-011-F**: forbidden action attempt → reject draft, record failure, do not promote.
* **E-AC-011-G**: stale draft → reconcile or regenerate before use.

### E-RQ-012: Dogfooding pilot and future write-capable readiness

**Requirement**
The Epic must collect enough evidence to decide whether write-capable delegation should remain deferred.

**Acceptance criteria**

* **E-AC-012-A**: pilot records at least one design draft and one plan draft.
* **E-AC-012-B**: pilot records integration delta, reviewer findings, traceability defects, scope creep defects, blocker quality, and forbidden-action attempts.
* **E-AC-012-C**: pilot defines go/no-go criteria for future scoped write-capable delegation.
* **E-AC-012-D**: write-capable delegation remains non-scope unless pilot criteria are satisfied and a new Epic/Issue approves it.

---

## Proposed design contracts

## 1. Ownership contract

### Authority matrix

| Capability                |            Main orchestrator |                Human | system-architect | implementation-planner | spec-reviewer |
| ------------------------- | ---------------------------: | -------------------: | ---------------: | ---------------------: | ------------: |
| Own user dialogue         |                          Yes |         Participates |               No |                     No |            No |
| Own `requirement.md`      |                          Yes |                  Yes |               No |                     No |   Review only |
| Draft `design.md`         |                          Yes |                   No |  Yes, draft-only |                     No |            No |
| Draft `plan.md`           |                          Yes |                   No |               No |        Yes, draft-only |            No |
| Edit canonical artifacts  |                          Yes |                   No |               No |                     No |            No |
| Integrate delegated draft |                          Yes |                   No |               No |                     No |            No |
| Promote phase             | Yes, only with reviewer pass |                   No |               No |                     No |            No |
| Review phase artifact     |                           No |                   No |               No |                     No |           Yes |
| Change GitHub issue state |         Out of this contract | Out of this contract |        Forbidden |              Forbidden |     Forbidden |
| Edit implementation code  |         Out of this contract | Out of this contract |        Forbidden |              Forbidden |     Forbidden |

### Required wording for design

```md
Delegated authoring roles produce draft evidence only. They do not own canonical artifacts, do not modify previous-phase artifacts, do not promote phases, and do not replace spec-reviewer.
```

---

## 2. Draft artifact lifecycle contract

### Lifecycle states

| State                  | Meaning                                        |                         Promotion usable? |
| ---------------------- | ---------------------------------------------- | ----------------------------------------: |
| `requested`            | main orchestrator prepared delegation contract |                                        No |
| `produced`             | delegated author returned draft                |                         No, not by itself |
| `integrated`           | main integrated draft into canonical artifact  |                  Yes, after reviewer pass |
| `partially_integrated` | main integrated selected portions              | Yes, after rejected portions are recorded |
| `rejected`             | draft not used                                 |                                        No |
| `superseded`           | newer draft or canonical update replaced it    |                                        No |
| `blocked`              | delegated author returned RCR / Plan Blocked   |                                        No |
| `stale`                | source artifact changed after draft            |                       No until reconciled |

### Draft artifact front matter / header

Recommended Markdown block:

```md
# Delegated {Design|Plan} Draft

## Metadata

- epic_id:
- node_type: initiative | epic | issue
- node_id:
- phase: design | plan
- role: system-architect | implementation-planner
- authoring_mode: draft-only
- status: requested | produced | integrated | partially_integrated | rejected | superseded | blocked | stale
- created_at:
- source_artifacts:
  - requirement.md:
  - design.md:
  - parent_docs:
  - adr_docs:
  - existing_code_or_docs:
- source_snapshot:
  - commit_or_revision: unknown | <value>
  - reviewer_pass_reference:
- consent_reference:
- allowed_actions:
- forbidden_actions:

## Invocation Contract

## Draft Output

## Traceability Map

## Blockers / Clarification Requests

## Integration Notes
```

`created_at` and `commit_or_revision` are usefulだが、現在のプロンプトだけでは実際にどう取得できるか未確認。取得不能なら `unknown` を許容し、report 側に「未取得」と明示する。

---

## 3. Delegated design gate contract

### Preconditions

```md
Delegated Design Authoring Gate

Required:
- active node is selected
- requirement.md exists
- requirement.md has fresh spec-reviewer pass
- parent docs relevant to this node are identified
- investigation scope is declared
- role is system-architect
- authoring mode is draft-only
- consent is recorded for this node + phase + role
- output location is declared
```

### Output obligations

`system-architect` must produce:

```md
## Requirement Coverage
- requirement item:
- design decision:
- trace status:

## Architecture Decisions

## Boundaries and Contracts

## Source of Record / Dependency Analysis

## Data Flow / Domain Model / Interface Contract

## File or Module Change Plan

## Migration / Compatibility / Rollback

## Observability

## Test Strategy

## ADR Candidates

## Risks

## Requirement Clarification Requests
```

### Blocker behavior

If requirement is insufficient:

```md
## Requirement Clarification Request

- requirement_gap_id:
- blocked_design_area:
- why requirement is insufficient:
- options:
  - option_a:
  - option_b:
- recommended default:
- risk if assumed:
```

The role must not silently choose an option when the choice changes product behavior, scope, acceptance criteria, security posture, data model, or external contract.

---

## 4. Delegated plan gate contract

### Preconditions

```md
Delegated Plan Authoring Gate

Required:
- active node is selected
- requirement.md exists and has fresh spec-reviewer pass
- design.md exists and has fresh spec-reviewer pass
- design dependency analysis exists
- design file/module change plan exists, or design explicitly says no file/module plan is needed
- role is implementation-planner
- authoring mode is draft-only
- consent is recorded for this node + phase + role
- output location is declared
```

### Output obligations

`implementation-planner` must produce:

```md
## Plan Summary

## Requirement / Design Traceability

## Milestones

## Dependency-Derived Execution Order

## Implementation Steps
- step_id:
- observable behavior:
- depends_on:
- requirement_trace:
- design_trace:
- target_files_or_modules:
- tests:
- review_gate:
- rollback_or_recovery:
- docs_impact:
- completion_evidence:

## Integration Checkpoints

## Quality Gates

## Final Diff Gate

## Plan Blockers
```

### Blocker behavior

If design is insufficient:

```md
## Plan Blocked

- blocking_gap_id:
- affected_design_decision:
- affected_requirement:
- why implementation order cannot be safely derived:
- required design amendment:
- suggested amendment:
- risk if assumed:
```

The planner must not convert design ambiguity into implementation steps.

---

## 5. Report evidence contract

Recommended report block:

```md
## Delegated Authoring Evidence

### Delegation Summary

- phase:
- role:
- authoring_mode: draft-only
- node:
- consent_reference:
- invocation_contract_reference:
- draft_artifact:
- draft_status:
- source_artifacts:
- source_snapshot:
- forbidden_actions_confirmed: yes | no
- canonical_integration_by:
- integration_result: integrated | partially_integrated | rejected | blocked | stale
- integrated_sections:
- rejected_sections:
- blockers:
- reviewer_reference:
- reviewer_verdict:
- promotion_decision:
```

Rules:

* If no delegated authoring was used, report may state `delegated_authoring_used: no`.
* If delegated draft was used but evidence is missing, promotion should be blocked.
* If delegated draft was produced but rejected, report should record rejection reason.
* If draft status is `blocked`, canonical phase should return to previous artifact rather than proceed through assumptions.
* If source artifacts changed after draft production, report must mark draft `stale`.

---

## 6. Skills / host adapter boundary contract

### Canonical role skill

The role skill is the single source of behavior.

```text
Role skill owns:
- mission
- inputs
- output format
- allowed actions
- forbidden actions
- blocker format
- traceability obligations
- safety boundaries
- handoff expectations
```

### Host adapter

Host adapter is a thin callable entry point.

```text
Host adapter owns:
- role name
- short description
- skill reference
- optional model / reasoning effort hint
- draft-only reminder
```

Host adapter must not duplicate full instructions.

Bad pattern:

```text
.codex/agents/system-architect.toml contains a full copy of the system-architect SKILL.md behavior.
```

Good pattern:

```text
.codex/agents/system-architect.toml names the skill and states that SKILL.md is authoritative.
```

---

## 7. Provider / consumer parity contract

Because the prompt states provider-first and identifies `src/spec_dock/assets/...` as source of truth while `spec-dock/` is dogfooding consumer workspace, the Epic should require parity evidence.

Recommended contract:

```md
Provider-first rule:
- Shipped docs/skills are authored under provider assets.
- Dogfooding workspace copies are generated or manually synchronized.
- Any dogfooding change to generated workspace must either be backported to provider assets or recorded as temporary pilot evidence.
```

Acceptance evidence:

```md
## Provider / Consumer Parity Evidence

- provider asset path:
- consumer workspace path:
- sync method:
- verification command or manual check:
- drift found:
- drift resolved:
```

---

## 8. Failure mode contract

| Failure                                                    | Expected behavior                           | Promotion impact                                     |
| ---------------------------------------------------------- | ------------------------------------------- | ---------------------------------------------------- |
| Missing delegation consent                                 | Do not invoke delegated author              | Manual path may continue                             |
| Missing requirement reviewer pass before design delegation | Block design delegation                     | Cannot promote design                                |
| Requirement gap found during design                        | Return RCR                                  | Return to requirement                                |
| Missing design reviewer pass before plan delegation        | Block plan delegation                       | Cannot promote plan                                  |
| Design gap found during plan                               | Return Plan Blocked                         | Return to design                                     |
| Delegated author modifies previous-phase artifact          | Reject draft; record violation              | Block promotion until repaired                       |
| Delegated author edits canonical artifact                  | Reject; record violation                    | Block promotion                                      |
| Delegated author proposes untraceable scope                | Reject or require main integration decision | Block if integrated                                  |
| Delegated draft lacks traceability                         | Treat as incomplete                         | Cannot be promotion evidence                         |
| Role unavailable                                           | Use manual authoring path                   | No automatic block                                   |
| Host adapter/skill drift                                   | Prefer skill; update adapter                | Block host integration issue, not necessarily policy |
| Draft source changed                                       | Mark stale                                  | Reconcile before promotion                           |
| Reviewer unavailable/denied/waived/provisional             | Existing rule applies                       | Block/incomplete                                     |

---

## Proposed issue plan with dependencies and acceptance criteria

The current 5-issue plan is directionally correct, but issue 4 is overloaded and issue 3 risks being implemented before the source-of-truth skill boundary is defined. The better plan is **6 issues**. If issue count must remain 5, merge Issue 002 into Issue 004, but that is less clean.

## Issue 001: Delegated authoring policy foundation

### Purpose

Define ownership, consent, draft-only delegation, and non-scope in `workflow_spec_authoring.md`.

### Dependencies

None.

### Deliverables

* `workflow_spec_authoring.md` update
* ownership vs authoring delegation section
* draft-only delegated authoring section
* consent granularity section
* forbidden actions section
* previous-phase mutation prohibition

### Acceptance criteria

* AC-001-A: main orchestrator remains canonical artifact owner.
* AC-001-B: requirement ownership remains main + human.
* AC-001-C: delegated design/plan authors are allowed only as draft-only producers.
* AC-001-D: delegated draft is not reviewer pass and not phase authority.
* AC-001-E: write-capable delegation is explicitly non-scope.
* AC-001-F: missing/stale/failed reviewer pass remains blocking.

---

## Issue 002: Delegated draft artifact and report evidence schema

### Purpose

Define structured draft artifacts and report evidence before role skills start producing outputs.

### Dependencies

Issue 001.

### Deliverables

* draft artifact lifecycle section
* recommended `discussions/` artifact path
* draft metadata block
* report evidence block
* stale / superseded / rejected / blocked semantics

### Acceptance criteria

* AC-002-A: delegated drafts have required metadata.
* AC-002-B: status lifecycle is defined.
* AC-002-C: report evidence can link draft to canonical integration result.
* AC-002-D: stale draft handling is defined.
* AC-002-E: chat-only output is not sufficient when draft is used as evidence.
* AC-002-F: rejected and partially integrated drafts are representable.

---

## Issue 003: Role skill assets for system-architect and implementation-planner

### Purpose

Add shipped role skills that implement the delegated authoring contracts.

### Dependencies

Issue 001, Issue 002.

### Deliverables

* `spec-dock-system-architect/SKILL.md`
* `spec-dock-implementation-planner/SKILL.md`
* provider-first asset placement
* dogfooding copy or sync evidence

### Acceptance criteria

* AC-003-A: `system-architect` skill produces design draft only.
* AC-003-B: `implementation-planner` skill produces plan draft only.
* AC-003-C: both roles forbid canonical artifact edits, implementation edits, GitHub issue updates, and destructive commands.
* AC-003-D: `system-architect` returns RCR for requirement gaps.
* AC-003-E: `implementation-planner` returns Plan Blocked for design gaps.
* AC-003-F: both skills require traceability maps.
* AC-003-G: role instructions do not claim phase promotion authority.

---

## Issue 004: Phase gate and spec-reviewer integration

### Purpose

Integrate delegated authoring gates into `phase_design.md`, `phase_plan.md`, `phase_plan_issue.md`, and reviewer criteria.

### Dependencies

Issue 001, Issue 002, Issue 003.

### Deliverables

* delegated design authoring gate
* delegated plan authoring gate
* reviewer criterion for delegated draft usage
* report gate updates if not completed in Issue 002
* examples of valid and invalid delegated integration

### Acceptance criteria

* AC-004-A: design delegation requires fresh requirement reviewer pass.
* AC-004-B: plan delegation requires fresh requirement and design reviewer pass.
* AC-004-C: phase docs state that delegation cannot fill missing previous-phase decisions.
* AC-004-D: reviewer checks delegated draft provenance, staleness, traceability, and scope discipline.
* AC-004-E: reviewer fails promotion if delegated draft bypasses phase gates.
* AC-004-F: ordinary manual authoring remains valid.

---

## Issue 005: Codex host callable role adapter

### Purpose

Provide named host entry points for Codex without duplicating canonical role instructions.

### Dependencies

Issue 003, Issue 004.

### Deliverables

* `.codex/agents/system-architect.toml`, if host path is confirmed
* `.codex/agents/implementation-planner.toml`, if host path is confirmed
* adapter/skill boundary doc
* drift prevention note

### Acceptance criteria

* AC-005-A: host adapter is thin and points to role skill as authority.
* AC-005-B: adapter contains no duplicated long-form role contract.
* AC-005-C: adapter declares draft-only mode.
* AC-005-D: adapter declares role is forbidden from canonical edit / code edit / GitHub mutation.
* AC-005-E: `.github/agents` and Copilot agent are explicitly not implemented.
* AC-005-F: if `.codex/agents` path or syntax is not confirmed, issue records the uncertainty and ships role skills without pretending host integration is verified.

---

## Issue 006: Dogfooding parity and validation pilot

### Purpose

Use the new delegated authoring workflow in dogfooding workspace and record pilot metrics.

### Dependencies

Issue 001-005.

### Deliverables

* dogfooding delegated design draft
* dogfooding delegated plan draft
* report evidence
* reviewer result
* provider/consumer parity evidence
* pilot metrics summary
* write-capable readiness decision

### Acceptance criteria

* AC-006-A: at least one design draft is produced by `system-architect`.
* AC-006-B: at least one plan draft is produced by `implementation-planner`.
* AC-006-C: report evidence records consent, scope, draft artifact, integration result, and reviewer verdict.
* AC-006-D: reviewer evaluates canonical artifact and delegated evidence.
* AC-006-E: provider/consumer parity is verified.
* AC-006-F: pilot records defects and lessons learned.
* AC-006-G: final report states whether write-capable delegation remains deferred, with reasons.

---

## Role skill contract details

## `spec-dock-system-architect` skill

### Mission

Produce a draft `design.md` candidate from an approved `requirement.md` and relevant context. The role is a design specialist, not a requirement owner, canonical artifact owner, implementation agent, or reviewer.

### Required input contract

```md
## Input Contract

- active_node_type:
- active_node_id:
- target_artifact: design.md
- requirement_path:
- requirement_reviewer_pass_reference:
- parent_docs:
- related_docs:
- related_adrs:
- existing_implementation_scope:
- authoring_mode: draft-only
- allowed_actions:
- forbidden_actions:
- output_expectation:
```

### Mandatory instructions

The skill must state:

```md
You must:
- Treat requirement.md as authoritative.
- Treat parent Initiative/Epic docs as constraints.
- Produce draft design content only.
- Preserve requirement scope and non-scope.
- Map every material design decision to requirement evidence.
- Identify requirement gaps instead of filling them silently.
- Return Requirement Clarification Request when design cannot proceed safely.
- Identify alternatives and tradeoffs.
- Identify boundaries, contracts, dependencies, source of record, migration, observability, and test strategy where relevant.
- Identify ADR candidates when a decision has cross-issue or durable architectural impact.
- Output structured Markdown suitable for saving under discussions/.
```

### Forbidden instructions

```md
You must not:
- Modify requirement.md.
- Modify design.md directly.
- Modify plan.md.
- Modify implementation code.
- Close or update GitHub issues.
- Run destructive commands.
- Promote phases.
- Claim spec-reviewer pass.
- Ask the user directly for clarification.
- Expand scope beyond approved requirement.
- Convert unresolved requirement ambiguity into a design decision.
```

### Required output

```md
# Delegated Design Draft

## Metadata

## Requirement Coverage

## Existing Context Findings

## Design Decisions

## Alternatives Considered

## Boundary / Contract Model

## Dependency Analysis

## Source of Record

## Data Flow / Domain Model / Interface Contract

## File / Module Change Plan

## Migration / Compatibility / Rollback

## Observability

## Test Strategy

## ADR Candidates

## Risks

## Requirement Clarification Requests

## Integration Notes for Main Orchestrator
```

---

## `spec-dock-implementation-planner` skill

### Mission

Produce a draft `plan.md` candidate from approved `requirement.md` and `design.md`. The role is an implementation sequencing specialist, not a designer, canonical artifact owner, implementation agent, or reviewer.

### Required input contract

```md
## Input Contract

- active_node_type:
- active_node_id:
- target_artifact: plan.md
- requirement_path:
- requirement_reviewer_pass_reference:
- design_path:
- design_reviewer_pass_reference:
- parent_docs:
- related_adrs:
- authoring_mode: draft-only
- allowed_actions:
- forbidden_actions:
- output_expectation:
```

### Mandatory instructions

The skill must state:

```md
You must:
- Treat requirement.md and design.md as authoritative.
- Produce draft plan content only.
- Preserve design decisions.
- Decompose work into dependency-ordered implementation steps.
- Ensure every step traces to requirement item or design decision.
- Ensure each step has observable behavior or verifiable completion evidence.
- Include test/review gates.
- Include rollback, compatibility, and docs impact where relevant.
- Include final quality gate.
- Return Plan Blocked if design is insufficient.
- Output structured Markdown suitable for saving under discussions/.
```

### Forbidden instructions

```md
You must not:
- Modify requirement.md.
- Modify design.md.
- Modify plan.md directly.
- Invent new design decisions.
- Modify implementation code.
- Close or update GitHub issues.
- Run destructive commands.
- Promote phases.
- Claim spec-reviewer pass.
- Ask the user directly for clarification.
- Convert unresolved design ambiguity into implementation steps.
```

### Required output

```md
# Delegated Implementation Plan Draft

## Metadata

## Plan Summary

## Requirement / Design Traceability

## Milestones

## Dependency-Derived Execution Order

## Implementation Steps

## Test Strategy Mapping

## Review Gates

## Rollback / Compatibility

## Docs Impact

## Final Quality Gate

## Plan Blockers

## Integration Notes for Main Orchestrator
```

---

## Reviewer and evidence policy

## spec-reviewer treatment of delegated drafts

`spec-reviewer` should not review delegated draft as if it were canonical. It should review:

1. canonical artifact quality,
2. delegated draft provenance,
3. integration safety,
4. traceability,
5. scope discipline,
6. phase gate preservation.

### Required reviewer checks for design phase

```md
## Delegated Design Review Criteria

- Was delegated design authoring used?
- Is delegated evidence recorded in report.md?
- Does the draft artifact exist or is it otherwise captured?
- Was requirement.md reviewer-pass before design delegation?
- Did system-architect stay within requirement scope?
- Did system-architect avoid changing requirement.md?
- Were requirement gaps returned as RCR rather than silently assumed?
- Are integrated design decisions traceable to requirement items?
- Are non-integrated or rejected draft portions recorded?
- Is the delegated draft stale relative to requirement/design source artifacts?
- Does canonical design still satisfy ordinary design phase criteria?
```

### Required reviewer checks for plan phase

```md
## Delegated Plan Review Criteria

- Was delegated plan authoring used?
- Is delegated evidence recorded in report.md?
- Was requirement.md reviewer-pass before plan delegation?
- Was design.md reviewer-pass before plan delegation?
- Did implementation-planner avoid adding new design decisions?
- Were design gaps returned as Plan Blocked rather than silently assumed?
- Does every plan item trace to requirement item or design decision?
- Is implementation order derived from design dependency analysis?
- Are test/review gates present?
- Are rollback/compatibility/docs impact handled where relevant?
- Is the delegated draft stale relative to requirement/design source artifacts?
- Does canonical plan still satisfy ordinary plan phase criteria?
```

### Review verdict policy

| Condition                                                                                | Verdict                             |
| ---------------------------------------------------------------------------------------- | ----------------------------------- |
| Delegation not used; canonical artifact satisfies phase                                  | pass                                |
| Delegation used; evidence complete; canonical artifact satisfies phase                   | pass                                |
| Delegation used; evidence missing                                                        | fail or incomplete                  |
| Delegation draft stale and unreconciled                                                  | fail or incomplete                  |
| Delegated author bypassed requirement/design gap                                         | fail                                |
| Delegated author introduced scope creep and it was integrated                            | fail                                |
| Delegated author produced bad draft but main rejected it and canonical artifact is valid | pass with note                      |
| Role unavailable and manual authoring used                                               | pass if ordinary criteria satisfied |

---

## Dogfooding pilot metrics

## Metrics to capture

| Metric                          | Definition                                                   | Why                            |
| ------------------------------- | ------------------------------------------------------------ | ------------------------------ |
| M-001 draft count               | number of delegated design/plan drafts                       | confirms workflow is exercised |
| M-002 integration ratio         | accepted sections / proposed sections                        | measures usefulness            |
| M-003 rejected reason count     | grouped reasons for rejected content                         | finds role contract gaps       |
| M-004 traceability defect count | untraceable draft decisions/steps                            | detects scope creep            |
| M-005 gate violation count      | attempts to bypass reviewer/pass/precondition                | safety signal                  |
| M-006 forbidden action attempts | any attempt to edit canonical/code/GitHub/destructive action | hard stop signal               |
| M-007 RCR quality               | requirement gaps found by architect that were valid          | design role usefulness         |
| M-008 Plan Blocked quality      | design gaps found by planner that were valid                 | plan role usefulness           |
| M-009 reviewer delta            | reviewer findings before/after delegated authoring           | quality signal                 |
| M-010 stale draft events        | source changed after draft                                   | lifecycle pressure             |
| M-011 orchestrator edit load    | amount of rewrite needed before canonical integration        | cost/quality signal            |
| M-012 provider/consumer drift   | drift detected during dogfooding                             | asset management signal        |
| M-013 implementation deviation  | later implementation had to diverge from plan                | plan quality signal            |

## Write-capable readiness criteria

The following thresholds are proposed, not verified by external data. They should be treated as initial operating criteria.

### Proceed to investigate write-capable delegation only if all are true

* No forbidden action attempts in pilot.
* No phase gate bypass.
* No reviewer pass mistakenly replaced by delegated draft.
* 100% of integrated design decisions trace to requirement.
* 100% of integrated plan steps trace to requirement/design.
* Stale draft handling worked at least once or was explicitly not needed.
* Main orchestrator edits were mostly integration/formatting, not wholesale redesign.
* `spec-reviewer` found no severe delegated-authoring-specific defect after integration.
* Provider/consumer parity was maintained.
* Dogfooding report shows at least one successful design delegation and one successful plan delegation.

### Do not proceed if any are true

* delegated author attempted canonical edit, code edit, GitHub mutation, or destructive action.
* delegated draft introduced hidden requirement assumptions that passed into canonical artifact.
* implementation-planner invented design decisions.
* report evidence was too burdensome to maintain consistently.
* host adapter drifted from role skill.
* reviewer criteria could not reliably distinguish canonical artifact review from draft review.
* dogfooding failed to produce measurable quality improvement or implementation clarity.

---

## Risks and mitigations

| Risk                                    | Failure mode                                        | Mitigation                                                |
| --------------------------------------- | --------------------------------------------------- | --------------------------------------------------------- |
| R-001 Draft becomes authority           | Team treats delegated draft as approved design/plan | Always require main integration + fresh reviewer pass     |
| R-002 Hidden requirement assumptions    | architect fills requirement gaps silently           | Mandatory RCR format and reviewer check                   |
| R-003 Planner invents design            | planner resolves design ambiguity in plan           | Mandatory Plan Blocked format and reviewer check          |
| R-004 Host adapter drift                | `.codex/agents` duplicates skill instructions       | Thin adapter only; skill is canonical                     |
| R-005 Chat-only loss                    | draft cannot be audited later                       | Save structured artifact in `discussions/`                |
| R-006 Evidence bloat                    | report becomes too heavy                            | Use required compact fields, not full JSON schema         |
| R-007 Global consent too broad          | delegation used outside intended node/phase         | consent per node + phase + role + artifact                |
| R-008 Provider/consumer mismatch        | dogfooding uses different skill than shipped asset  | parity evidence required                                  |
| R-009 Reviewer ambiguity                | reviewer passes draft instead of canonical artifact | delegated-specific reviewer criteria                      |
| R-010 Premature write-capable expansion | safety assumptions not validated                    | write-capable explicitly non-scope; require pilot metrics |
| R-011 Scope creep                       | architect improves beyond requirement               | traceability + non-scope preservation                     |
| R-012 Stale draft                       | source changes after draft                          | lifecycle status and stale handling                       |
| R-013 Role unavailable                  | host cannot invoke subagent                         | manual authoring remains valid                            |
| R-014 Overfitting to Codex              | `.codex` design prevents other hosts                | keep host adapter separate from canonical skill           |

---

## Concrete next actions for Codex

1. Create `spec-dock/active/epic/discussions/delegated-authoring-external-analysis.md` from this memo.

2. Draft `requirement.md` with E-RQ-001 through E-RQ-012 as the Epic requirement backbone.

3. In `requirement.md`, make these explicit non-goals:

   * write-capable delegation,
   * `.github/agents` / Copilot agent,
   * runtime role registry,
   * runtime validation,
   * GitHub issue mutation,
   * implementation code editing by delegated authoring roles.

4. Draft `design.md` around these architecture contracts:

   * ownership matrix,
   * draft artifact lifecycle,
   * delegated design gate,
   * delegated plan gate,
   * report evidence block,
   * skill/host adapter boundary,
   * provider/consumer parity,
   * failure mode table.

5. Draft `plan.md` as 6 issues:

   * Issue 001: policy foundation,
   * Issue 002: draft artifact and report evidence schema,
   * Issue 003: role skill assets,
   * Issue 004: phase gate and reviewer integration,
   * Issue 005: Codex host callable role adapter,
   * Issue 006: dogfooding parity and validation pilot.

6. Before implementing Issue 005, verify actual `.codex/agents` path and syntax. If unverified, keep Issue 005 as adapter contract + documented uncertainty rather than pretending host integration is complete.

7. During dogfooding, require the report to include:

   * draft artifact path,
   * role,
   * phase,
   * consent,
   * source artifacts,
   * integration result,
   * reviewer result,
   * pilot metrics.

---

## Assumptions

* `discussions/` is an acceptable location for structured draft artifacts because the prompt states this response will be imported into `spec-dock/active/epic/discussions/`.
* `.codex/agents` is usable or intended as a host callable mechanism because it is explicitly listed as an uncertainty and example path in the prompt.
* Provider asset paths must be adapted to the actual repository layout; only the provider-first principle is grounded in the prompt.
* Markdown structured blocks are sufficient for initial schema because runtime validation is considered likely out of initial scope.

## Uncertainty / unverified claims

* Actual `.codex/agents/*.toml` schema is not verified from the provided context.
* Actual provider asset directory names are not verified beyond the stated `src/spec_dock/assets/...` source-of-truth principle.
* Actual existing `spec-reviewer` skill implementation is not available in this prompt.
* Actual generator/sync mechanism between provider assets and dogfooding workspace is not available in this prompt.
* Quantitative pilot thresholds are proposed operating criteria, not empirically validated.
